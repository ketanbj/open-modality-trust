# Shared core instructions

This subdirectory is the `open-modality-trust-core` Python package. Read the
umbrella `AGENTS.md` and `spec/local-profile.md`. Run the umbrella Makefile from
one level up; core tests also need the installed OpenAST and OpenATT packages.

## Implementation map

- `src/modality_trust/crypto.py`: restricted canonical JSON, parsing and signatures.
- `src/modality_trust/gateway.py`: immutable action snapshots, scoped grants,
  per-modality trust, durable revocation/replay state and local receipts.
- `src/modality_trust/benchmark.py`: shared experimental fixtures/controls;
  this is evaluation support, not the public action API.
- `tests/test_core.py`: malformed input, exact scope, role separation, one-use
  state, concurrency, rollback, late registration and unsupported guarantees.

## Preserve these invariants

1. Verify signatures against the appropriate configured modality/permission role.
2. Match the whole stored challenge and immutable action, including purpose and
   every argument. Derive supported guarantees in the verifier.
3. Inside the SQLite write transaction, recheck time, current issuer/grant
   revocation, complete challenge state and one-use state.
4. Receipt insertion and challenge/grant consumption commit or roll back together.
5. Revocation remains effective across restart and grant registration that occurs
   after revocation. Revocation after a committed receipt cannot undo history.
6. No arbitrary handler/HTTP/actuator callback is part of the local atomicity claim.

The gateway clock, configured keys, process and SQLite administrator are trusted.
Do not silently convert the restricted local profile to JOSE/COSE/RFC 8785 or the
umbrella draft schema. A wire-format change needs an explicit version and matching
adapter/documentation changes. No general composition or production enrollment is
implemented. Document changed assumptions alongside code changes.
