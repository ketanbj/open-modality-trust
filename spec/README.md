# Draft common contracts

Version 0.1 is a design draft. Schemas describe record shape, not cryptographic
verification or authority. They are not current OpenAVT wire formats or the accepted OpenAST/OpenATT
local signing profile. See [the implemented profile](local-profile.md).

- `evidence.schema.json`: a claim, provenance and its explicitly stated guarantees.
- `action-contract.schema.json`: the conditions required before a specific action.
- `adapter-contract.md`: adapter responsibilities and limits.

Do not turn a self-declared `guarantees` value into an authorization decision. A
verifier must independently establish every accepted predicate under its configured
trust and policy. The implemented shared core accepts its bounded local profile;
the broader composition contract here remains research. Scope, proof formats and interoperability remain
research work.
