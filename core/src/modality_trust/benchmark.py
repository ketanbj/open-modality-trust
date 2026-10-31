"""Local evaluation helpers. No network, models, hardware or private-key output."""

from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.metadata
import platform
import sqlite3
import statistics
import tempfile
import threading
import time
from pathlib import Path

from .crypto import canonical, digest, unpack, verify
from .gateway import ASSUMPTIONS, BASE, Action, Contract, Denied, Gateway, Signer, grant, validate_challenge


def metadata(roots: list[Path]) -> dict:
    files = {}
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" not in path.parts:
                files[str(path.relative_to(root.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
    versions = {}
    for name in ("cryptography", "numpy", "qrcode", "zxing-cpp", "opencv-python-headless"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": versions,
        "source_sha256": files,
        "clock": "synthetic fixed verifier clock; perf_counter_ns for costs",
    }


def timing(values: list[float]) -> dict:
    ordered = sorted(values)
    return {
        "n": len(values),
        "median_ms": statistics.median(ordered),
        "p95_ms": ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)],
        "min_ms": min(ordered),
        "max_ms": max(ordered),
    }


def wilson(successes: int, count: int) -> list[float]:
    """Descriptive 95% Wilson interval for a generated-channel condition, not deployment risk."""
    z, p = 1.959963984540054, successes / count
    denominator = 1 + z * z / count
    center = (p + z * z / (2 * count)) / denominator
    width = z * ((p * (1 - p) / count + z * z / (4 * count * count)) ** 0.5) / denominator
    return [max(0, center - width), min(1, center + width)]


def reference_accepts(evidence, token, action, contract, fixture) -> bool:
    """Sequential typed-policy control. Shares crypto/adapter primitives, not the SQL gate.

    This is an equally expressive *local* policy control, not an IFC implementation
    or an independent audit. It has no atomic remote-effect or concurrency claim.
    """
    try:
        protected = verify(evidence, fixture.gateway.attesters, contract.modality + "-evidence")
        body = protected["body"]
        if set(body) != {"challenge", "observation"}:
            return False
        challenge = body["challenge"]
        validate_challenge(challenge, now=fixture.now, modality=contract.modality)
        if (
            challenge != fixture.challenge
            or fixture.consumed
            or fixture.issuer_revoked
            or challenge["audience"] != fixture.gateway.audience
            or challenge["request_digest"] != action.digest
        ):
            return False
        if contract.modality == "sight":
            from openast.protocol import appraise
        else:
            from openatt.protocol import appraise
        supported = (
            BASE | appraise(body["observation"], challenge, action.document) | {"delegated-permission"}
        )
        if not contract.required_guarantees <= supported:
            return False
        if ASSUMPTIONS[contract.modality] not in contract.permitted_assumptions:
            return False
        permission = verify(token, fixture.gateway.delegators, "grant")["body"]
        return (
            digest(unpack(token)) == fixture.registered_digest
            and not fixture.revoked
            and permission["audience"] == fixture.gateway.audience
            and permission["principal"] == action.document["principal"]
            and permission["request_digest"] == action.digest
            and contract.modality in permission["modalities"]
            and permission["issued_at"] <= fixture.now < permission["expires_at"]
        )
    except (ValueError, TypeError, KeyError):
        return False


class Fixture:
    def __init__(self, directory, modality):
        self.now = 1000000
        self.modality = modality
        self.signer, self.owner = Signer.generate("attester"), Signer.generate("owner")
        self.statement = {"order": "42", "status": "ready"}
        arguments = {"statement_digest": digest(self.statement)} if modality == "sight" else {}
        self.action = Action("agent", "record", "resource/42", "authorized-demo", arguments)
        self.gateway = Gateway(
            str(Path(directory) / "state.sqlite3"),
            audience="backend",
            attesters={"attester": self.signer.public_key},
            delegators={"owner": self.owner.public_key},
            clock=lambda: self.now,
        )
        self.challenge = self.gateway.challenge(self.action, modality)
        if modality == "sight":
            from openast import respond

            self.evidence = respond(self.signer, self.challenge, self.action, self.statement, now=self.now)
        else:
            from openatt import respond, simulate

            self.evidence = respond(
                self.signer, self.challenge, self.action, simulate(self.challenge), now=self.now
            )
        self.token = grant(self.owner, self.action, "backend", now=self.now, modalities=(modality,))
        self.gateway.register_grant(self.token)
        self.registered_digest = digest(unpack(self.token))
        self.consumed = self.revoked = self.issuer_revoked = False

    def signed_body(self, update):
        body = unpack(self.evidence)["protected"]["body"]
        update(body)
        return self.signer.sign(self.modality + "-evidence", body)


SERIAL_CASES = [
    "valid",
    "evidence-tamper",
    "unconfigured-key",
    "action-substitution",
    "resource-substitution",
    "principal-substitution",
    "purpose-substitution",
    "arguments-substitution",
    "session-transplant",
    "nonce-transplant",
    "wrong-audience",
    "expired-challenge",
    "expired-grant",
    "revoked-grant",
    "revoked-attester",
    "revoked-delegator",
    "unregistered-grant",
    "wrong-grant-scope",
    "wrong-grant-modality",
    "consumed-replay",
    "unknown-observation-profile",
    "extra-observation-field",
    "unaccepted-assumption",
    "require-proximity",
    "require-consent",
    "fresh-relay-without-proximity-requirement",
    "compromised-attester-without-sensor-truth-requirement",
]


def serial_benchmark(modality: str, repetitions: int = 10, extra_cases=()) -> dict:
    cases, rows, durations = SERIAL_CASES + list(extra_cases), [], []
    for trial in range(repetitions):
        for case in cases:
            with tempfile.TemporaryDirectory() as directory:
                f = Fixture(directory, modality)
                evidence, token, action, contract = f.evidence, f.token, f.action, Contract(modality)
                expected = case in {
                    "valid",
                    "fresh-relay-without-proximity-requirement",
                    "compromised-attester-without-sensor-truth-requirement",
                }
                if case == "evidence-tamper":
                    obj = unpack(evidence)
                    obj["protected"]["body"]["observation"]["resource"] = "resource/evil"
                    evidence = canonical(obj)
                elif case == "unconfigured-key":
                    evidence = Signer.generate("rogue").sign(
                        modality + "-evidence", unpack(evidence)["protected"]["body"]
                    )
                elif case in {
                    "action-substitution",
                    "resource-substitution",
                    "principal-substitution",
                    "purpose-substitution",
                    "arguments-substitution",
                }:
                    field = case.removesuffix("-substitution")
                    value = {"evil": True} if field == "arguments" else "substituted"
                    action = Action(**{**action.document, field: value})
                elif case in {"session-transplant", "nonce-transplant", "wrong-audience"}:
                    field = {
                        "session-transplant": "session",
                        "nonce-transplant": "nonce",
                        "wrong-audience": "audience",
                    }[case]
                    evidence = f.signed_body(lambda body: body["challenge"].update({field: "transplanted"}))
                elif case == "expired-challenge":
                    f.now += 31
                elif case == "expired-grant":
                    token = grant(f.owner, action, "backend", now=f.now, ttl=1, modalities=(modality,))
                    f.gateway.register_grant(token)
                    f.registered_digest = digest(unpack(token))
                    f.now += 2
                elif case == "revoked-grant":
                    f.revoked = True
                    f.gateway.revoke_grant(unpack(token)["protected"]["body"]["id"])
                elif case in {"revoked-attester", "revoked-delegator"}:
                    f.issuer_revoked = True
                    f.gateway.revoke_issuer("attester" if case == "revoked-attester" else "owner")
                elif case == "unregistered-grant":
                    token = grant(f.owner, action, "backend", now=f.now, modalities=(modality,))
                elif case == "wrong-grant-scope":
                    wrong = Action(**{**action.document, "purpose": "another-purpose"})
                    token = grant(f.owner, wrong, "backend", now=f.now, modalities=(modality,))
                    f.gateway.register_grant(token)
                    f.registered_digest = digest(unpack(token))
                elif case == "wrong-grant-modality":
                    token = grant(
                        f.owner,
                        action,
                        "backend",
                        now=f.now,
                        modalities=("tactile" if modality == "sight" else "sight",),
                    )
                    f.gateway.register_grant(token)
                    f.registered_digest = digest(unpack(token))
                elif case == "consumed-replay":
                    f.gateway.commit(evidence, token, action, contract)
                    f.consumed = True
                elif case == "unknown-observation-profile":
                    evidence = f.signed_body(lambda body: body["observation"].update(profile="unconfigured"))
                elif case == "extra-observation-field":
                    evidence = f.signed_body(lambda body: body["observation"].update(trusted=True))
                elif case == "unaccepted-assumption":
                    contract = Contract(modality, permitted_assumptions=frozenset())
                elif case in {"require-proximity", "require-consent"}:
                    requirement = "physical-proximity" if case == "require-proximity" else "human-consent"
                    contract = Contract(modality, required_guarantees=frozenset({requirement}))
                elif case == "wrong-statement":
                    evidence = f.signed_body(
                        lambda body: body["observation"].update(statement_digest="0" * 64)
                    )
                elif case == "trace-gap":
                    evidence = f.signed_body(
                        lambda body: body["observation"]["samples"].__delitem__(slice(5, 10))
                    )
                elif case == "trace-force-substitution":
                    evidence = f.signed_body(
                        lambda body: body["observation"]["samples"][15].__setitem__(1, 0)
                    )
                elif case == "wrong-pattern":
                    from openatt.trace import pattern, simulate

                    other = {**f.challenge, "nonce": "other"}
                    while pattern(other) == pattern(f.challenge):
                        other["nonce"] += "x"
                    evidence = f.signed_body(lambda body: body["observation"].update(samples=simulate(other)))
                before = len(f.gateway.effects())
                try:
                    verify(evidence, f.gateway.attesters, modality + "-evidence")
                    signature_only = True
                except ValueError:
                    signature_only = False
                reference = reference_accepts(evidence, token, action, contract, f)
                started = time.perf_counter_ns()
                try:
                    f.gateway.commit(evidence, token, action, contract)
                    accepted, reason = True, "committed"
                except Denied as error:
                    accepted, reason = False, str(error)
                elapsed = (time.perf_counter_ns() - started) / 1e6
                after = len(f.gateway.effects())
                row = {
                    "trial": trial,
                    "case": case,
                    "expected": expected,
                    "accepted": accepted,
                    "reason": reason,
                    "new_effects": after - before,
                    "signature_only": signature_only,
                    "typed_reference": reference,
                    "elapsed_ms": elapsed,
                }
                rows.append(row)
                durations.append(elapsed)
                if accepted != expected or reference != expected or after - before != int(expected):
                    raise AssertionError(row)
    return {
        "repetitions": repetitions,
        "cases_per_trial": len(cases),
        "observations": len(rows),
        "unexpected_outcomes": sum(r["accepted"] != r["expected"] for r in rows),
        "unauthorized_new_effects": sum(r["new_effects"] for r in rows if not r["expected"]),
        "typed_reference_disagreements": sum(r["accepted"] != r["typed_reference"] for r in rows),
        "signature_only_false_accepts": sum(r["signature_only"] for r in rows if not r["expected"]),
        "cost": timing(durations),
        "rows": rows,
    }


def concurrency_benchmark(modality: str, repetitions=10, workers=8) -> dict:
    rows = []
    for trial in range(repetitions):
        with tempfile.TemporaryDirectory() as directory:
            f = Fixture(directory, modality)
            barrier = threading.Barrier(workers)

            def attempt(_):
                barrier.wait(timeout=10)
                try:
                    f.gateway.commit(f.evidence, f.token, f.action, Contract(modality))
                    return True
                except Denied:
                    return False

            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                commits = sum(pool.map(attempt, range(workers)))
            effects = len(f.gateway.effects())
            if commits != 1 or effects != 1:
                raise AssertionError("duplicate effect")
            rows.append(
                {
                    "trial": trial,
                    "schedule": "simultaneous-duplicate",
                    "attempts": workers,
                    "commits": commits,
                    "effects": effects,
                }
            )
        with tempfile.TemporaryDirectory() as directory:
            f = Fixture(directory, modality)
            # Hold the SQLite write boundary, revoke inside it, then release the waiting commit.
            connection = sqlite3.connect(f.gateway.database, isolation_level=None)
            connection.execute("BEGIN IMMEDIATE")
            permission_id = unpack(f.token)["protected"]["body"]["id"]
            connection.execute("UPDATE grants SET revoked=1 WHERE id=?", (permission_id,))
            entered = threading.Event()

            def waiting_commit():
                entered.set()
                try:
                    f.gateway.commit(f.evidence, f.token, f.action, Contract(modality))
                    return True
                except Denied:
                    return False

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(waiting_commit)
                entered.wait(timeout=10)
                connection.commit()
                connection.close()
                accepted = future.result(timeout=10)
            if accepted or f.gateway.effects():
                raise AssertionError("revocation failed at serialized boundary")
            rows.append(
                {
                    "trial": trial,
                    "schedule": "revocation-before-commit-lock",
                    "attempts": 1,
                    "commits": 0,
                    "effects": 0,
                }
            )
    return {
        "rows": rows,
        "trials": repetitions,
        "workers": workers,
        "boundary": "same SQLite file and transaction; no external or physical effects",
    }
