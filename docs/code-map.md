# Code and ownership map

| Concern | Owning source | Closest verification |
|---|---|---|
| Restricted JSON and signature envelopes | [crypto.py](../core/src/modality_trust/crypto.py) | [core tests](../core/tests/test_core.py) |
| Immutable actions, challenges, owner grants and transactional local receipts | [gateway.py](../core/src/modality_trust/gateway.py) | [core tests](../core/tests/test_core.py) |
| Shared experimental fixtures and policy controls | [benchmark.py](../core/src/modality_trust/benchmark.py) | Modality raw reports and source-hash checks |
| Exact checked-out submodule revisions | [check_workspace.py](../scripts/check_workspace.py), [.gitmodules](../.gitmodules) | `make check-workspace` |
| Human/agent documentation links | [check_docs.py](../scripts/check_docs.py) | `make check-docs` |
| Implemented protocol contract | [local profile](../spec/local-profile.md) | Actual core/adapter code and tests |
| Proposed contracts | [draft schema guide](../spec/README.md) | Shape validation does not establish trust |

## Modality ownership

- [OpenAVT](../modalities/openavt/README.md): independent audio transport,
  enrollment, scoped authorization and voice demos.
- [OpenAST](../modalities/openast/README.md): visual claim signing and QR raster
  processing; permission/receipt enforcement lives in the shared core.
- [OpenATT](../modalities/openatt/README.md): bounded force traces and signed
  controller reports; permission/receipt enforcement lives in the shared core.

Edit the owning child repository once, publish its commit, then update its pin
here. A sibling checkout and an umbrella submodule are two checkouts, not two
sources to edit independently. See [development](development.md).

## Sources, measurements and future work

`core/src`, modality `src/` and tests define implemented behavior. Raw measurement
reports and reviewed manuscripts are indexed in [research](../research/README.md).
Generated plots/tables/PDFs have their own source hashes and review records.
[Roadmap](roadmap.md), draft schemas and [integration plans](../integrations/README.md)
are proposed work, not evidence that those capabilities are deployed.
