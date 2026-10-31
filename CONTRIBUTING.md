# Contribute to OpenModalityTrust

Use the [documentation map](docs/README.md), [code map](docs/code-map.md) and
[development workflow](docs/development.md). Coding agents should read
[AGENTS.md](AGENTS.md), plus [core instructions](core/AGENTS.md) for shared code.

1. Identify the owning repository: shared verification belongs here; modality
   capture/framing belongs in the independent modality repository.
2. Keep observation, appraised claims and action permission separate. A changed
   guarantee needs an explicit assumption/threat-model update and relevant tests.
3. Use `make check-docs` for documentation-only work and `make check` for shared
   implementation changes. Follow child package/evidence guides where applicable.
4. Preserve historical measurements and distinguish them from research targets.
   Do not manually rewrite hashes or generated numbers to conceal drift.
5. Publish child commits before updating exact submodule pointers here. Inspect
   `git diff --submodule=log` and verify the complete pinned workspace.

Code is Apache-2.0. Public media/data need documented rights and consent. Keys,
credentials, local grants/databases and unconsented recordings are not committed.
Funding proposals remain outside this repository.
