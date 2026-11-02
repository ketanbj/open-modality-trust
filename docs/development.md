# Develop the workspace

Run the commands below from **the umbrella repository root** unless a step
explicitly enters a modality. Python 3.11+ is required. Read the
[documentation map](README.md) or [agent guide](../AGENTS.md) first.

## Clone, install and check

```sh
git clone --recurse-submodules https://github.com/ketanbj/open-modality-trust.git
cd open-modality-trust
python3 -m venv .venv
source .venv/bin/activate
make install
make help
make check
make demo
```

For an existing clone, initialize exact pinned checkouts with:

```sh
git submodule update --init --recursive
```

`make install` installs the local core, pinned OpenAST/OpenATT and developer tools.
It does not install OpenAVT's independent optional dependencies. `make check`
checks shared-core/workspace lint, documentation across all pinned repositories,
all core/visual/tactile tests,
recorded evidence and exact submodule pins. Demos use generated inputs and no
external model/provider account. Set `PYTHON=/path/to/python` when needed.

Without Make, the core setup/check is:

```sh
python -m pip install -e core -e 'modalities/openast[dev]' -e 'modalities/openatt[dev]'
python -m pytest -q core/tests modalities/openast/tests modalities/openatt/tests
python scripts/check_docs.py
python scripts/check_workspace.py --require-checkouts
```

## Two checkout layouts

A sibling `openast/` checkout and `modalities/openast/` are separate Git checkouts.
Choose one for the implementation change. The adapter Makefiles detect both the
sibling shared core (`../open-modality-trust/core`) and recursive layout
(`../../core`); custom layouts can set `CORE=/path/to/core`.

The umbrella's code is `core/src/modality_trust/`. Shared tests import both adapters,
so install them together before testing a core change. OpenAVT has a separate
`uv.lock` and its own Makefile/environment; see its development guide.

## Change and publish a modality

Pinned commits make the workspace reproducible. A normal recursive clone often
leaves submodules detached. Create a task branch before editing inside one:

```sh
cd modalities/openast
git switch -c feature/your-change
# edit, check, commit and publish this child repository first
cd ../..
```

If working in a standalone sibling checkout, publish there instead. Then fetch
that already published branch in the umbrella copy:

```sh
git -C modalities/openast fetch origin feature/your-change
git -C modalities/openast switch --detach FETCH_HEAD
git add modalities/openast
git diff --cached --submodule=log
make check-workspace
make test
```

Review and commit the updated gitlink with related umbrella documentation. Do not
publish a gitlink to a commit available only on one machine. Check for local
submodule changes before switching revisions; do not discard another task's work.

`branch = main` in `.gitmodules` is only a development tracking preference.
`git submodule update --remote` deliberately moves beyond pins; reproduction uses
`git submodule update --init --recursive` without `--remote`.

## Scope the validation

| Change | Check |
|---|---|
| Human/agent documentation | `make check-docs`; inspect commands and claims |
| Shared parsing, trust, permissions or receipts | Closest core tests, then `make check` |
| A modality implementation | Child checks, then the published pin and umbrella tests |
| Core package metadata | `make build` plus a source/wheel smoke install |
| Benchmark/manuscript | The owning modality's evidence/publication guide |

The shared gate's only atomic effect is its local receipt. Read
[core instructions](../core/AGENTS.md) before changing transaction semantics.
Draft schemas describe proposed record shapes; the [local profile](../spec/local-profile.md)
and implementation define accepted credentials today.

## Evidence and local material

The [evidence index](../research/README.md) points to actual reports. Preserve dated
snapshots and measured source hashes. New runs belong in ignored output paths;
docs-only changes do not require remeasurement. Generated tables, plots and PDFs
must stay consistent with their report sources and review records.

Funding proposals are maintained outside these repositories. Keep them, credentials
and local/private artifacts out of implementation commits. Each repository retains
its own history and release cycle.
