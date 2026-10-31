# Working with submodules

Clone with `git clone --recurse-submodules` or run
`git submodule update --init --recursive` after a normal clone.

Pinned commits make the workspace reproducible. `branch = main` in `.gitmodules`
only supplies a development tracking preference; a normal clone still checks out
the exact gitlink commit, usually in detached HEAD state.

To develop a modality, enter its directory and create a branch before editing:

```sh
cd modalities/openast
git switch -c feature/your-change
# edit, verify, commit and publish the child repository first
```

Then return to the umbrella, stage the updated submodule pointer, review it, and
publish the umbrella commit. Never publish an umbrella pointer to a child commit
that is available only on one machine. To adopt a published main revision:

```sh
git submodule update --remote modalities/openast
git diff --submodule=log
git add modalities/openast
git commit -m 'Update sight adapter revision'
```

Use `python3 scripts/check_workspace.py --require-checkouts` to verify a clone.
Avoid `--remote` in reproduction commands: it intentionally moves beyond pins.
The umbrella does not require moving, rewriting or combining modality histories.
