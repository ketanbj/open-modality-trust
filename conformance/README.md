# Executable local conformance

The shared `core/tests` exercises exact principal/action/resource/purpose/argument
binding, malformed encoding, signer-role/modality separation, replay after restart,
revocation before and after registration, concurrent duplicates, rollback and
unsupported guarantee promotion. Independent modality tests cover actual image
and force-trace parsers, signed public fixtures and local signal assumptions.

```sh
python -m pytest core/tests modalities/openast/tests modalities/openatt/tests
```

Benchmark runners add a common serial attack taxonomy and selected concurrency
schedules. General evidence composition, handoff invalidation and full agent-output
IFC remain proposed research. Workspace structure is checked separately by
`scripts/check_workspace.py`; passing it is not protocol validation.
