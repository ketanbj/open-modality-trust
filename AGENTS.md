# open-modality-trust agent guide

This is the umbrella and shared local verifier. OpenAST/OpenATT use `core/`;
OpenAVT is independent. The implemented gate checks one modality per local receipt.
General composition, selective acquisition and cloud integration remain research.

## Read first

`README.md` -> `docs/README.md` -> `docs/architecture.md` -> `core/AGENTS.md`.

## Commands

Run from the umbrella root with initialized submodules and Python 3.11+:

```sh
make install
make help
make demo
make test
make lint
make check-docs
make verify-evidence
make check-workspace
```

`PYTHON=/path/to/python` selects the interpreter. `make check-docs` checks this repository and its pinned children using only
stdlib; runtime/test targets require `make install`. Treat submodules as separate
repositories: publish child commits before staging/pushing their gitlinks.
See `docs/development.md` for standalone versus recursive checkout layouts.

## Change map

| Change | Start with | Closest verification |
|---|---|---|
| Shared signing/parsing | `core/src/modality_trust/crypto.py` | `core/tests/test_core.py` |
| Action/grant/receipt semantics | `core/src/modality_trust/gateway.py` | `core/tests/test_core.py` |
| Shared experimental controls | `core/src/modality_trust/benchmark.py` | modality evidence checks |
| Draft contracts vs implemented profile | `spec/README.md`, `spec/local-profile.md` | schema inspection plus protocol tests |
| A modality implementation | its independent repository, not a second copy here | child CI, then `make test` |
| Pinned workspace metadata | `scripts/check_workspace.py`, `.gitmodules` | `make check-workspace` |

## Important boundaries

The model cannot grant itself authority. Keep attester keys scoped by modality
and separate from owner keys. Read `core/AGENTS.md` for transaction invariants.
Draft schema validation is not proof verification. A successful transport or
receipt is not a location, consent or physical-effect guarantee.

## Working rules

- Read the task guide and closest code/tests before editing; use `rg` to navigate.
- Keep changes within the requested behavior. Explain changed guarantees in the
  architecture/threat model and cover them with relevant protocol tests.
- Preserve the separation between observations, verified claims and permission.
  Never promote a fresh signature to location, or a contact report to consent.
- Recorded benchmarks and publication artifacts are evidence. Do not hand-edit
  numeric results or overwrite historical reports to hide a mismatch. Exploratory
  benchmarks go in ignored `output/`; docs-only changes need no benchmark rerun.
- New or changed relative Markdown links should pass `make check-docs`.
- Keep keys, grants, credentials, recordings and databases out of commits. Public fixtures
  must be explicitly synthetic or have documented rights; public verification
  keys are distinct from private signing credentials.
- Publishing a package, running paid/provider integrations and submitting papers
  are separate tasks; the local demo and normal checks require none of them.
