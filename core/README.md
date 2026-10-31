# Shared verification reference

`open-modality-trust-core` 0.1.0 implements a bounded signed-evidence profile,
exact action binding, separate one-use delegated grants, and a transactional
**local ledger receipt** effect. OpenAST and OpenATT use it; OpenAVT remains an
independent implementation. This is not a general evidence calculus, IFC engine,
remote attestation system, or production authorization service.

## Install

From an umbrella checkout with the updated modality revisions:

```sh
python -m pip install -e core -e modalities/openast -e modalities/openatt
python -m openast demo --output output/sight-demo
python -m openatt demo --output output/tactile-demo
python -m pytest core/tests modalities/openast/tests modalities/openatt/tests
```

These are local research packages. Publication to PyPI is not asserted. Install
all three packages explicitly from source; Python 3.11+ is required.

## Acceptance boundary

The gate independently verifies the configured attester signature, server-issued
nonce/session/audience, exact immutable action digest (principal, operation,
resource, purpose and every argument), modality claim, required guarantees,
accepted assumptions, and a separately signed grant. The verifier derives
accepted guarantees. An adapter cannot supply a universal trust flag.
Unsupported proximity, scene truth and human consent remain unsupported.

Evidence keys are configured per modality; a display key cannot impersonate a
controller. Evidence and grants have different signing roles and trust maps. The gateway's
clock, configured keys, process and SQLite administrator are trusted. The local
profile rejects duplicate JSON keys, floats, excessive input and unknown fields;
it uses domain-separated Ed25519 signatures. It is not JOSE, COSE, RFC 8785 or
wire interoperability with the umbrella's draft schemas. Signatures do not
encrypt public QR evidence or force traces.

`BEGIN IMMEDIATE` serializes grant/issuer revocation checks, expiry,
challenge/grant consumption and receipt insertion in one SQLite transaction.
Revocation committed first prevents a later receipt; subsequent revocation
cannot undo an already committed receipt. Failed insertion rolls back consumption.
Restart retains replay state. Revocation tombstones also survive registration
that happens after revocation. There is no arbitrary handler callback in this
claim: HTTP calls and actuators require their own participating effect boundary.
Deployments need authenticated enrollment, protected keys, retention/expiry
cleanup, a trustworthy clock and operational hardening.

## Validation

Tests cover parser ambiguity, exact action binding, replay after restart,
revocation, concurrent duplicates, rollback, unsupported guarantees and expiry at
the write boundary. Both modality benchmark runners include a weak signature-only
ablation and an equally expressive sequential typed-policy control. The latter
shares crypto/adapter primitives but checks policy separately from the SQL gate;
agreement is not an independent audit or proof of novelty.

Composition, voice integration, acquisition scheduling, cloud enforcement and
formal proofs remain research. A configured issuer can still lie.
