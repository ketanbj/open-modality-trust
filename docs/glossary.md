# Vocabulary

| Term | Plain meaning in this project |
|---|---|
| Modality | A way to interact: voice, sight or touch |
| Observation | Input that was heard, seen or reported by a sensor; it begins untrusted |
| Claim | A specific statement about a named subject/resource |
| Evidence | Material a verifier can inspect to assess that claim under configured assumptions |
| Attester / issuer | The configured key that signs a report or statement |
| Verifier / appraisal | Code that checks the evidence and determines its supported guarantees |
| Guarantee | A narrowly stated property established by checks, such as message integrity |
| Assumption | A condition the checks rely on, such as a trustworthy sensor-to-signing path |
| Principal | The agent/account named in an action request |
| Resource | The particular order, fixture or other object that the action concerns |
| Action contract | The requirements an action must satisfy; the model cannot invent accepted permission |
| Owner grant | Separate signed permission for an exact action, principal and audience |
| Challenge / nonce | A verifier-issued interaction value bound to a stored request |
| Fresh response | A signed response to that challenge; this does not prove recent physical capture or proximity |
| Replay | Reusing old evidence/permission or repeating a consumed transaction |
| Revocation | Withdrawing authority; its effect depends on the documented commit boundary |
| Receipt | The shared demo's local database record of an accepted request |
| Commit boundary | The point where checks and the supported effect become durable together |
| Composition | Proposed rules for retaining claim scope and assumptions when combining or handing off evidence |

The [implemented local profile](../spec/local-profile.md) uses precise field names
and bounds. The [draft schemas](../spec/README.md) explore broader research contracts;
they are not accepted runtime credentials.
