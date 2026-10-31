# OpenModalityTrust

**Trust for agents using human interfaces.**

Agents increasingly operate through voice, screens, signs, buttons and touch.
This project studies how evidence acquired through those interfaces can inform
an action without being mistaken for stronger authority. Identity is not
permission; freshness is not presence; a contact report is not human consent.

## Status

Experimental implementations now exist for scoped visual and tactile evidence,
backed by a shared local verification/authorization package. OpenAVT remains the
independent experimental voice implementation. No general cross-modal composition
proof, acquisition scheduler, cloud deployment or physical sensor/camera study is
claimed.

| Component | Purpose | Evidence boundary |
| --- | --- | --- |
| `core/` | Exact actions, per-modality issuer keys, separate one-use grants, current revocation and atomic local receipts | Implemented local reference; not a remote/physical effect guarantee |
| [openavt](https://github.com/ketanbj/openavt) | Protected structured requests over audio | Experimental local voice implementation |
| [openast](https://github.com/ketanbj/openast) | Signed visual statements through actual QR images | Generated-raster and policy benchmarks; no camera deployment |
| [openatt](https://github.com/ketanbj/openatt) | Signed controller force/time reports | Generated-signal and policy benchmarks; no hardware or consent proof |

## Run the new adapters

After cloning recursively:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e core -e modalities/openast -e modalities/openatt pytest
python -m openast demo --output output/sight
python -m openatt demo --output output/tactile
python -m pytest core/tests modalities/openast/tests modalities/openatt/tests
```

These are local source packages; no PyPI publication is asserted. See
[shared core](core/README.md), [evidence index](research/README.md) and
[local signing profile](spec/local-profile.md). The decoder or a schema validator
alone does not authenticate evidence. A model cannot mint its own permission.

## Clone the workspace

```sh
git clone --recurse-submodules https://github.com/ketanbj/open-modality-trust.git
cd open-modality-trust
python3 scripts/check_workspace.py --require-checkouts
```

For an existing checkout:

```sh
git submodule update --init --recursive
```

Submodules live under `modalities/` and are pinned to exact commits. Developing a
modality means committing and publishing in that repository first, then updating
its gitlink here. [Development workflow](docs/development.md).

## Layout

```text
docs/           architecture, threat model, assumptions and roadmap
spec/           draft claims/evidence/action contracts
core/           implemented bounded verifier and local receipt gate
conformance/    common adapter requirements
benchmarks/     measured evidence index and future evaluation scope
integrations/   Bedrock, AgentCore/Cedar and backend plans
examples/       workflows spanning modalities
research/       evidence index and research direction
modalities/     independent Git submodules: openavt, openast, openatt
```

Start with the [architecture](docs/architecture.md),
[threat model](docs/threat-model.md), [roadmap](docs/roadmap.md), and
[draft adapter contract](spec/adapter-contract.md). Draft JSON Schemas describe
record shape only; passing schema validation authenticates nothing.
