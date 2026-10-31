# Architecture

The common path is observation -> evidence -> appraised claims -> action contract.

1. A modality adapter captures a bounded observation and, where participating
   counterparties support it, decodes a structured response.
2. Evidence records state the issuer, claim, interaction, freshness conditions,
   provenance and assumptions. A signature on bytes does not authenticate the
   whole image or speech transcript surrounding them.
3. The local shared verifier checks signatures, per-modality trust configuration,
   scope, freshness and supported action requirements. General dependency-aware
   composition remains proposed work.
4. A participating backend enforces current permission at a specified durable
   commit boundary. The language model proposes actions but cannot mint authority.

OpenAVT is an independent implementation. OpenAST and OpenATT use the implemented
local profile in `core/`, not the draft common schemas. The core checks one
modality per receipt. There is no current general cross-modal security guarantee,
voice integration, evidence acquisition scheduler or physical deployment.

The only implemented shared effect is a local SQLite receipt: grant and issuer
revocation, expiry, one-use state and receipt insertion share a write transaction.
Remote HTTP operations and physical actuators need their own participating commit
boundary. A display key is not a controller key unless explicitly configured for
that modality; an observation signer is not the owner permission signer.

The umbrella owns shared contracts, research documentation, conformance and
benchmarks. Modality repositories own capture, framing, challenge exchange,
modality-specific binding and local examples. Independent repositories are pinned
as submodules, keeping their histories and release cycles separate.

Guarantees are not interchangeable: message identity, freshness, physical
association, delegated permission and human consent require distinct evidence.
Any unsupported guarantee must remain unsupported after a handoff.
