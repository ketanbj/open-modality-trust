# Implemented local profile v1

This is the experimental profile implemented in `core/` and used by OpenAST and
OpenATT. It is separate from `evidence.schema.json` and `action-contract.schema.json`;
those remain draft research contracts, not interoperable accepted credentials.

A signed envelope has exactly `protected` and `signature`. Protected fields are
`v=1`, `kind`, `issuer`, `body`. Kind is `sight-evidence`, `tactile-evidence` or
`grant`. The signature is Base64 Ed25519 over the domain separator
`OpenModalityTrust/local-profile/1` followed by a zero byte and the canonical
protected bytes. Canonical bytes use sorted keys, ASCII JSON escaping and compact
separators. This is a local restricted profile, not RFC 8785, JOSE or COSE.

Evidence body is exactly `challenge` and `observation`. The stored challenge binds
version, business audience, modality, nonce, session, exact action digest, issue
time and expiry. An action snapshots principal, action, resource, purpose and all
arguments. Attester keys are scoped by modality; owner permission keys are separate.

The signed grant binds one random ID, principal, audience, exact action digest,
allowed modalities and validity times. Registration stores its full token digest;
revocation tombstones survive late registration. Every successful receipt consumes
both grant and challenge inside the same transaction as the ledger insertion.

The verifier derives guarantees from configured validators. Evidence cannot assert
its own unrestricted guarantee set. The common derived guarantees are issuer-key
control, message integrity, fresh signed response and exact request binding; owner
permission is verified separately. OpenAST adds a signed-statement claim; OpenATT
adds reported-contact and reported-pattern-match under its trusted sensor-path
assumption. Proximity, physical resource association and human consent remain
unsupported. A fresh signature is not proof of fresh physical capture.

Input limits and protocol details are executable in `crypto.py`, `gateway.py` and
the modality validators. Deployment needs authenticated enrollment, protected keys,
a trustworthy clock, retention/cleanup and external effect enforcement. The current
one-modality gate does not implement general conjunction or evidence scheduling.
