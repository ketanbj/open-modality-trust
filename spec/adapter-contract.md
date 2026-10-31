# Draft adapter contract

An adapter reports observations and evidence. It must not return a universal
`trusted: true` field or infer human approval merely from contact.

Evidence identifies the exact structured claim and resource, issuer, interaction
context, modality, provenance, freshness conditions, proof reference, guarantees
claimed, and assumptions. Sensitive raw media and credentials remain outside the
record by default. A proof reference locates evidence; it is not itself a proof.

The verifier, rather than the model or adapter, appraises which guarantees are
established. A successful decoder must not endorse neighboring content. A handoff
retains exact claim references and invalidates incompatible scope or freshness.

Voice, sight and touch have different observation and failure models. Each
adapter must document replay, live relay, missing observations and its limits on
physical association. Unsupported conditions require an explicit outcome.
