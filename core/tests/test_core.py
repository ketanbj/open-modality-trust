import concurrent.futures
import json
import sqlite3
import threading

import pytest
from openast import respond

from modality_trust import Action, Contract, Denied, Gateway, Signer, canonical, digest, grant, unpack, verify


@pytest.fixture
def fixture(tmp_path):
    display, owner = Signer.generate("display"), Signer.generate("owner")
    now = [1000000]
    action = Action("agent", "record", "order/42", "pickup", {"statement_digest": digest({"ready": True})})
    gateway = Gateway(
        str(tmp_path / "state.sqlite3"),
        audience="backend",
        attesters={"sight": {"display": display.public_key}},
        delegators={"owner": owner.public_key},
        clock=lambda: now[0],
    )
    challenge = gateway.challenge(action, "sight")
    token = grant(owner, action, "backend", now=now[0])
    gateway.register_grant(token)
    evidence = respond(display, challenge, action, {"ready": True}, now=now[0])
    return gateway, display, owner, action, challenge, token, evidence, now


@pytest.mark.parametrize(
    "encoded",
    [
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
        b'{"a":1.0}',
        b'{"a":true,"a":false}',
        b'{"a":9007199254740992}',
        b"[" * 100 + b"]" * 100,
        b'"' + b"a" * 33000 + b'"',
    ],
)
def test_wire_parser_fails_closed(encoded):
    with pytest.raises(ValueError):
        unpack(encoded)


def test_immutable_action_snapshot():
    arguments = {"amount": 1}
    action = Action("agent", "pay", "order/1", "purchase", arguments)
    before = action.digest
    arguments["amount"] = 1000
    action.document["arguments"]["amount"] = 999
    assert action.digest == before


def test_role_confusion_and_tampering(fixture):
    gateway, display, _, _, _, token, evidence, _ = fixture
    with pytest.raises(ValueError):
        verify(token, {"display": display.public_key}, "sight-evidence")
    altered = unpack(evidence)
    altered["protected"]["body"]["observation"]["resource"] = "order/99"
    with pytest.raises(ValueError):
        verify(canonical(altered), gateway.attesters["sight"], "sight-evidence")


@pytest.mark.parametrize(
    "field,value",
    [
        ("principal", "other"),
        ("action", "delete"),
        ("resource", "order/99"),
        ("purpose", "resale"),
        ("arguments", {"statement_digest": "x"}),
    ],
)
def test_exact_action_binding(fixture, field, value):
    gateway, _, _, action, _, token, evidence, _ = fixture
    altered = Action(**{**action.document, field: value})
    with pytest.raises(Denied, match="request-binding"):
        gateway.commit(evidence, token, altered, Contract("sight"))
    assert not gateway.effects()


@pytest.mark.parametrize("requirement", ["human-consent", "physical-proximity", "resource-association"])
def test_no_guarantee_promotion(fixture, requirement):
    gateway, _, _, action, _, token, evidence, _ = fixture
    with pytest.raises(Denied, match="unsupported-guarantee"):
        gateway.commit(evidence, token, action, Contract("sight", frozenset({requirement})))
    assert not gateway.effects()


def test_assumptions_are_policy_inputs(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    with pytest.raises(Denied, match="unaccepted-assumption"):
        gateway.commit(evidence, token, action, Contract("sight", permitted_assumptions=frozenset()))


def test_replay_and_restart(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    gateway.commit(evidence, token, action, Contract("sight"))
    restarted = Gateway(
        gateway.database,
        audience=gateway.audience,
        attesters=gateway.attesters,
        delegators=gateway.delegators,
        clock=gateway.clock,
    )
    with pytest.raises(Denied):
        restarted.commit(evidence, token, action, Contract("sight"))
    assert len(restarted.effects()) == 1


def test_revoke_cannot_be_undone_by_registration(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    gateway.revoke_grant(unpack(token)["protected"]["body"]["id"])
    gateway.register_grant(token)
    with pytest.raises(Denied, match="grant-inactive"):
        gateway.commit(evidence, token, action, Contract("sight"))
    assert not gateway.effects()


def test_revocation_before_registration_is_durable(fixture):
    gateway, _, owner, action, _, _, evidence, now = fixture
    token = grant(owner, action, "backend", now=now[0])
    gateway.revoke_grant(unpack(token)["protected"]["body"]["id"])
    gateway.register_grant(token)
    with pytest.raises(Denied, match="grant-inactive"):
        gateway.commit(evidence, token, action, Contract("sight"))
    assert not gateway.effects()


@pytest.mark.parametrize("issuer", ["owner", "display"])
def test_current_issuer_revocation(fixture, issuer):
    gateway, _, _, action, _, token, evidence, _ = fixture
    gateway.revoke_issuer(issuer)
    with pytest.raises(Denied, match="issuer-revoked"):
        gateway.commit(evidence, token, action, Contract("sight"))


def test_exact_signed_challenge_must_exist(fixture):
    gateway, display, _, action, challenge, token, _, now = fixture
    challenge["session"] = "new-session"
    evidence = respond(display, challenge, action, {"ready": True}, now=now[0])
    with pytest.raises(Denied, match="unknown-or-consumed"):
        gateway.commit(evidence, token, action, Contract("sight"))


def test_no_permission_no_effect(fixture):
    gateway, _, owner, action, _, _, evidence, now = fixture
    unregistered = grant(owner, action, "backend", now=now[0])
    with pytest.raises(Denied, match="grant-inactive"):
        gateway.commit(evidence, unregistered, action, Contract("sight"))
    assert not gateway.effects()


def test_expiry_rechecked_after_lock(fixture):
    gateway, _, _, action, _, token, evidence, now = fixture
    # A deterministic clock schedule simulates expiry during the pre-transaction work.
    values = iter([1000000, 1000031])
    gateway.clock = lambda: next(values)
    with pytest.raises(Denied, match="expired-at-commit"):
        gateway.commit(evidence, token, action, Contract("sight"))
    assert not gateway.effects()


def test_atomic_one_use_under_concurrency(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    barrier = threading.Barrier(8)

    def attempt(_):
        barrier.wait(timeout=10)
        try:
            gateway.commit(evidence, token, action, Contract("sight"))
            return True
        except Denied:
            return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(attempt, range(8))) == 1
    assert len(gateway.effects()) == 1


def test_effect_failure_rolls_back_consumption(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    with sqlite3.connect(gateway.database) as connection:
        connection.executescript(
            "CREATE TRIGGER no_effect BEFORE INSERT ON effects BEGIN SELECT RAISE(ABORT, 'fail'); END;"
        )
    with pytest.raises(sqlite3.IntegrityError):
        gateway.commit(evidence, token, action, Contract("sight"))
    with sqlite3.connect(gateway.database) as connection:
        connection.execute("DROP TRIGGER no_effect")
    gateway.commit(evidence, token, action, Contract("sight"))
    assert len(gateway.effects()) == 1


def test_invalid_evidence_does_not_consume_permission(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    with pytest.raises(Denied):
        gateway.commit(b"{}", token, action, Contract("sight"))
    gateway.commit(evidence, token, action, Contract("sight"))
    assert len(gateway.effects()) == 1


def test_grant_hash_covers_arguments_and_purpose(fixture):
    gateway, _, owner, action, _, _, evidence, now = fixture
    altered = Action(**{**action.document, "purpose": "another-purpose"})
    token = grant(owner, altered, "backend", now=now[0])
    gateway.register_grant(token)
    with pytest.raises(Denied, match="grant-scope"):
        gateway.commit(evidence, token, action, Contract("sight"))


def test_receipt_contains_no_grant_or_raw_observation(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    result = gateway.commit(evidence, token, action, Contract("sight"))
    encoded = json.dumps(result)
    assert "signature" not in encoded and "observation" not in encoded and "nonce" not in encoded


def test_display_key_cannot_impersonate_controller(fixture):
    from openatt import respond as tactile_response
    from openatt import simulate

    gateway, display, owner, action, _, _, _, now = fixture
    challenge = gateway.challenge(action, "tactile")
    evidence = tactile_response(display, challenge, action, simulate(challenge), now=now[0])
    token = grant(owner, action, "backend", now=now[0], modalities=("tactile",))
    gateway.register_grant(token)
    with pytest.raises(Denied, match="invalid-evidence"):
        gateway.commit(evidence, token, action, Contract("tactile"))
    assert not gateway.effects()


def test_different_modality_needs_fresh_evidence(fixture):
    gateway, _, _, action, _, token, evidence, _ = fixture
    with pytest.raises(Denied, match="invalid-evidence"):
        gateway.commit(evidence, token, action, Contract("tactile"))
    assert not gateway.effects()
