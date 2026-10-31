"""Evidence appraisal and an atomic SQLite *local ledger* effect boundary.

The only implemented effect is a durable receipt. No arbitrary callback or remote
actuator is disguised as a transactional effect. A local database administrator,
configured signers and the verifier process are trusted.
"""

from __future__ import annotations

import secrets
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass

from .crypto import Signer, canonical, digest, exact, identifier, integer, unpack, verify

MODALITIES = {"sight", "tactile"}
BASE = frozenset({"issuer-key-control", "message-integrity", "fresh-response", "request-binding"})
ASSUMPTIONS = {"sight": "configured-display-key", "tactile": "trusted-controller-and-sensor-path"}
CHALLENGE_KEYS = (
    "v",
    "audience",
    "modality",
    "nonce",
    "session",
    "request_digest",
    "issued_at",
    "expires_at",
)


class Denied(PermissionError):
    """A stable reason code for fail-closed outcomes."""


class Action:
    """An immutable snapshot, including all tool arguments and the user's purpose."""

    def __init__(self, principal: str, action: str, resource: str, purpose: str, arguments: dict):
        for value in (principal, action, resource, purpose):
            identifier(value)
        if type(arguments) is not dict:
            raise ValueError("arguments must be an object")
        self._encoded = canonical(
            dict(principal=principal, action=action, resource=resource, purpose=purpose, arguments=arguments)
        )

    @property
    def document(self) -> dict:
        return unpack(self._encoded)

    @property
    def digest(self) -> str:
        return digest(self.document)


@dataclass(frozen=True)
class Contract:
    modality: str
    required_guarantees: frozenset[str] = BASE | {"delegated-permission"}
    permitted_assumptions: frozenset[str] = frozenset(ASSUMPTIONS.values())

    def __post_init__(self):
        if self.modality not in MODALITIES:
            raise ValueError("unsupported modality")
        # Freeze even if a caller supplies mutable sets.
        object.__setattr__(self, "required_guarantees", frozenset(self.required_guarantees))
        object.__setattr__(self, "permitted_assumptions", frozenset(self.permitted_assumptions))


def validate_challenge(challenge: dict, *, now: int, modality: str):
    exact(challenge, CHALLENGE_KEYS)
    if type(challenge["v"]) is not int or challenge["v"] != 1 or challenge["modality"] != modality:
        raise ValueError("wrong challenge profile")
    for key in ("audience", "nonce", "session", "request_digest"):
        identifier(challenge[key])
    if len(challenge["request_digest"]) != 64 or any(
        c not in "0123456789abcdef" for c in challenge["request_digest"]
    ):
        raise ValueError("invalid request digest")
    start, end = integer(challenge["issued_at"]), integer(challenge["expires_at"])
    if not start <= now < end or not 1 <= end - start <= 120:
        raise ValueError("challenge expired or not yet valid")


def grant(
    signer: Signer, action: Action, audience: str, *, now: int, ttl: int = 60, modalities=("sight", "tactile")
) -> bytes:
    integer(now)
    integer(ttl, 1, 3600)
    identifier(audience)
    if not set(modalities) <= MODALITIES or not modalities or len(set(modalities)) != len(modalities):
        raise ValueError("invalid modalities")
    return signer.sign(
        "grant",
        {
            "id": secrets.token_hex(16),
            "principal": action.document["principal"],
            "audience": audience,
            "request_digest": action.digest,
            "modalities": list(modalities),
            "issued_at": now,
            "expires_at": now + ttl,
        },
    )


class Gateway:
    def __init__(
        self,
        database: str,
        *,
        audience: str,
        attesters: dict[str, bytes],
        delegators: dict[str, bytes],
        clock=None,
    ):
        self.database, self.audience = str(database), identifier(audience)
        if self.database == ":memory:":
            raise ValueError("use a file database for multi-connection transaction semantics")
        self.attesters, self.delegators = dict(attesters), dict(delegators)
        self.clock = clock or (lambda: int(time.time()))
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS challenges (
                    nonce TEXT PRIMARY KEY, document BLOB NOT NULL, consumed INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS grants (
                    id TEXT PRIMARY KEY, token_digest TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0,
                    consumed INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS revoked_issuers (issuer TEXT PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS effects (
                    nonce TEXT PRIMARY KEY, request_digest TEXT NOT NULL, evidence_digest TEXT NOT NULL,
                    grant_id TEXT NOT NULL, committed_at INTEGER NOT NULL, receipt BLOB NOT NULL);
            """)

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database, timeout=10, isolation_level=None)
        try:
            connection.execute("PRAGMA busy_timeout=10000")
            connection.execute("PRAGMA synchronous=FULL")
            yield connection
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def challenge(self, action: Action, modality: str, *, ttl=30) -> dict:
        if modality not in MODALITIES:
            raise ValueError("unsupported modality")
        integer(ttl, 1, 120)
        now = integer(self.clock())
        result = dict(
            v=1,
            audience=self.audience,
            modality=modality,
            nonce=secrets.token_hex(16),
            session=secrets.token_hex(16),
            request_digest=action.digest,
            issued_at=now,
            expires_at=now + ttl,
        )
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO challenges(nonce, document) VALUES (?, ?)", (result["nonce"], canonical(result))
            )
        return result

    def _grant(self, token):
        try:
            protected = verify(token, self.delegators, "grant")
            body = protected["body"]
            exact(
                body,
                ("id", "principal", "audience", "request_digest", "modalities", "issued_at", "expires_at"),
            )
            for key in ("id", "principal", "audience", "request_digest"):
                identifier(body[key])
            if (
                type(body["modalities"]) is not list
                or not body["modalities"]
                or not all(type(m) is str and m in MODALITIES for m in body["modalities"])
                or len(set(body["modalities"])) != len(body["modalities"])
            ):
                raise ValueError("grant modality")
            start, end = integer(body["issued_at"]), integer(body["expires_at"])
            if body["audience"] != self.audience or not 1 <= end - start <= 3600:
                raise ValueError("grant audience or lifetime")
            return protected
        except (ValueError, TypeError) as error:
            raise Denied("invalid-grant") from error

    def register_grant(self, token: bytes):
        protected = self._grant(token)
        body = protected["body"]
        if not body["issued_at"] <= self.clock() < body["expires_at"]:
            raise Denied("grant-not-current")
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO grants(id, token_digest) VALUES (?, ?)",
                (body["id"], digest(unpack(token))),
            )
            row = connection.execute("SELECT token_digest FROM grants WHERE id=?", (body["id"],)).fetchone()
            if row[0] != digest(unpack(token)):
                raise Denied("grant-id-collision")

    def revoke_grant(self, grant_id: str):
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("UPDATE grants SET revoked=1 WHERE id=?", (identifier(grant_id),))
            connection.commit()

    def revoke_issuer(self, issuer: str):
        with self._connect() as connection:
            connection.execute("INSERT OR IGNORE INTO revoked_issuers VALUES (?)", (identifier(issuer),))

    def commit(self, evidence: bytes, token: bytes, action: Action, contract: Contract) -> dict:
        """Verify, consume challenge/grant and append a receipt in one transaction.

        No guarantee is accepted from an adapter-provided list. Guarantees are
        derived from the configured modality validator and this gateway's checks.
        """
        try:
            protected = verify(evidence, self.attesters, contract.modality + "-evidence")
            body = protected["body"]
            exact(body, ("challenge", "observation"))
            challenge = body["challenge"]
            validate_challenge(challenge, now=integer(self.clock()), modality=contract.modality)
            if challenge["audience"] != self.audience or challenge["request_digest"] != action.digest:
                raise Denied("request-binding")
            # Import the independent adapter validator only for the requested modality.
            if contract.modality == "sight":
                from openast.protocol import appraise
            else:
                from openatt.protocol import appraise
            guarantees = (
                BASE
                | frozenset(appraise(body["observation"], challenge, action.document))
                | {"delegated-permission"}
            )
            if not contract.required_guarantees <= guarantees:
                raise Denied("unsupported-guarantee")
            if ASSUMPTIONS[contract.modality] not in contract.permitted_assumptions:
                raise Denied("unaccepted-assumption")
            permission = self._grant(token)
            scope = permission["body"]
            if (
                scope["request_digest"] != action.digest
                or scope["principal"] != action.document["principal"]
                or contract.modality not in scope["modalities"]
            ):
                raise Denied("grant-scope")
        except Denied:
            raise
        except (ValueError, TypeError, KeyError) as error:
            raise Denied("invalid-evidence") from error

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            # Time and revocation are checked again *after* acquiring the write lock.
            now = integer(self.clock())
            if not (
                challenge["issued_at"] <= now < challenge["expires_at"]
                and scope["issued_at"] <= now < scope["expires_at"]
            ):
                raise Denied("expired-at-commit")
            for issuer in (protected["issuer"], permission["issuer"]):
                if connection.execute("SELECT 1 FROM revoked_issuers WHERE issuer=?", (issuer,)).fetchone():
                    raise Denied("issuer-revoked")
            row = connection.execute(
                "SELECT document, consumed FROM challenges WHERE nonce=?", (challenge["nonce"],)
            ).fetchone()
            if row is None or row[0] != canonical(challenge) or row[1]:
                raise Denied("unknown-or-consumed-challenge")
            row = connection.execute(
                "SELECT token_digest, revoked, consumed FROM grants WHERE id=?", (scope["id"],)
            ).fetchone()
            if row is None or row[0] != digest(unpack(token)) or row[1] or row[2]:
                raise Denied("grant-inactive-or-consumed")
            receipt = dict(
                v=1,
                result="committed",
                effect="local-ledger-receipt",
                committed_at=now,
                request_digest=action.digest,
                evidence_digest=digest(unpack(evidence)),
                modality=contract.modality,
                guarantees=sorted(guarantees),
                assumptions=[ASSUMPTIONS[contract.modality]],
            )
            connection.execute(
                "INSERT INTO effects VALUES (?, ?, ?, ?, ?, ?)",
                (
                    challenge["nonce"],
                    action.digest,
                    receipt["evidence_digest"],
                    scope["id"],
                    now,
                    canonical(receipt),
                ),
            )
            connection.execute("UPDATE challenges SET consumed=1 WHERE nonce=?", (challenge["nonce"],))
            connection.execute("UPDATE grants SET consumed=1 WHERE id=?", (scope["id"],))
            connection.commit()
            return receipt

    def effects(self) -> list[dict]:
        with self._connect() as connection:
            return [
                unpack(row[0]) for row in connection.execute("SELECT receipt FROM effects ORDER BY rowid")
            ]
