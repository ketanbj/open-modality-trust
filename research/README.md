# Research and measured evidence

The research questions concern sound composition of non-equivalent evidence and
efficient acquisition without unnecessary reauthentication. Cryptography, IFC,
attestation, visual/haptic authentication and transactions are foundations. A
scientific contribution must be demonstrated against equally expressive controls.

| Artifact | Recorded evidence | Limits |
|---|---|---|
| [OpenAVT authority experiment](https://github.com/ketanbj/openavt/blob/38beb670688e77910b29ada475a8deddb0169575/docs/experiments/authority-2026-10-31.md) | 12 local trials, 60 fresh audio calls, 264 case observations | Synthetic effects; deliberate post-check revocation exposes a check-to-effect gap |
| [OpenAST benchmark](../modalities/openast/docs/benchmarks/README.md) | 280 generated-raster attempts; 600 serial policy observations; duplicate/revocation schedules | No camera, LLM or physical relay study |
| [OpenATT benchmark](../modalities/openatt/docs/benchmarks/README.md) | 240 generated-force trials; 640 serial policy observations; short-pattern collision test | No sensor hardware, human identity/consent or actuation study |
| [Shared core](../core/README.md) | Exact action/grant binding, per-modality keys, durable replay/revocation and local receipt tests | One modality per receipt; no general composition calculus or remote effect atomicity |

Both new gateways match an equally expressive sequential typed-policy control in
the recorded serial cases. The signature-only comparison is an intentionally weak
ablation. Zero unauthorized new local receipts in these finite cases is not a
real-world attack probability, independent audit or formal proof.

Raw reports include environment versions, source SHA-256s, every case outcome and
timings. Report generators derive paper measurements from those files. Public
fixtures are explicitly synthetic and separate from the measurement trials.
Research manuscripts live in each modality's `paper/` directory. Funding proposals
are maintained outside these repositories and are not part of this published code.
