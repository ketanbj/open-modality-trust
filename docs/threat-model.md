# Threat model and assumptions

An adversary may supply neighboring speech or text, replay recordings, relocate
markers, relay live responses, splice modalities and induce handoffs. Individually
valid signatures may accompany an invalid inference about location or authority.

The intended research model trusts a configured verifier, trust roots and
participating enforcement backends. It does not assume an arbitrary camera view,
voice or contact event is authenticated. Compromise of a signer or sensor changes
what can be claimed and must be represented in the assumptions.

OpenAVT authenticates cryptographic endpoints and protected structured messages;
ordinary speech is outside its inner secure channel. Visual challenge-response
alone does not prove proximity. A signed tactile report authenticates a reporting
controller, not necessarily the toucher or their intent. Robot collision safety
and general sensor truth are outside the project's claims.

Strict revocation requires a cooperating effect boundary. A pre-handler check is
not automatically atomic with a later remote or physical effect. Unsupported
commit semantics must be reported explicitly, not hidden behind a successful
transport handshake.
