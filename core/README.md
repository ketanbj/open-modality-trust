# Shared verifier design

Planned responsibilities: evidence appraisal, guarantee composition, scope and
freshness checking, dependency invalidation, and action-contract evaluation.
Cryptographic proof verification and commit authorization are not implemented
here yet. Draft records are untrusted input, not accepted credentials.

The intended acceptance rule requires established evidence and current delegated
permission for the exact action/resource under configured assumptions. Acquisition
scheduling may optimize cost but must not bypass the deterministic acceptance
check. Established cryptography and IFC are foundations, not novelty claims.
