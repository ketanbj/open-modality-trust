# Architecture

The common path is observation -> evidence -> appraised claims -> action contract.

1. A modality adapter captures a bounded observation and, where participating
   counterparties support it, decodes a structured response.
2. Evidence records state the issuer, claim, interaction, freshness conditions,
   provenance and assumptions. A signature on bytes does not authenticate the
   whole image or speech transcript surrounding them.
3. A planned shared verifier checks signatures, trust configuration, scope,
   freshness, dependencies and the exact guarantee required by an action.
4. A participating backend enforces current permission at a specified durable
   commit boundary. The language model proposes actions but cannot mint authority.

The existing OpenAVT code is an independent implementation, not yet a consumer
of these draft common schemas. OpenAST and OpenATT initially provide designs;
there is no current cross-modal security guarantee.

The umbrella owns shared contracts, research documentation, conformance and
benchmarks. Modality repositories own capture, framing, challenge exchange,
modality-specific binding and local examples. Independent repositories are pinned
as submodules, keeping their histories and release cycles separate.

Guarantees are not interchangeable: message identity, freshness, physical
association, delegated permission and human consent require distinct evidence.
Any unsupported guarantee must remain unsupported after a handoff.
