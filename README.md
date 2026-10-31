# OpenModalityTrust

**Trust for agents using human interfaces.**

Agents increasingly operate through voice, screens, signs, buttons and touch.
This project studies how evidence acquired through those interfaces can inform
an action without being mistaken for stronger authority. Identity is not
permission; freshness is not presence; a contact report is not human consent.

## Status

This is the initial research workspace and specification scaffold. The shared
verifier, visual protocol and tactile protocol are proposed work, not deployed
security mechanisms. OpenAVT is the existing experimental voice implementation.

| Submodule | Purpose | Maturity |
| --- | --- | --- |
| [openavt](https://github.com/ketanbj/openavt) | Protected structured requests over voice audio | Experimental implementation |
| [openast](https://github.com/ketanbj/openast) | Open Agent Sight Trust | Design scaffold |
| [openatt](https://github.com/ketanbj/openatt) | Open Agent Tactile Trust | Exploratory design scaffold |

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
core/           shared verification design
conformance/    common adapter requirements
benchmarks/     attack taxonomy and evaluation plans
integrations/   Bedrock, AgentCore/Cedar and backend plans
examples/       workflows spanning modalities
research/       evidence index and research direction
modalities/     independent Git submodules: openavt, openast, openatt
```

Start with the [architecture](docs/architecture.md),
[threat model](docs/threat-model.md), [roadmap](docs/roadmap.md), and
[draft adapter contract](spec/adapter-contract.md). Draft JSON Schemas describe
record shape only; passing schema validation authenticates nothing.
