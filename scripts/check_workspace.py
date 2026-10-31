"""Verify the workspace metadata and exact pinned submodule checkouts; stdlib only."""

from __future__ import annotations

import argparse
import configparser
import json
import subprocess
from pathlib import Path


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def check(root, require_checkouts=False):
    modules = configparser.ConfigParser(interpolation=None)
    modules.read(root / ".gitmodules")
    expected = {f"modalities/{name}": f"https://github.com/ketanbj/{name}.git"
                for name in ("openavt", "openast", "openatt")}
    actual = {modules[section]["path"]: modules[section]["url"] for section in modules.sections()}
    if actual != expected:
        raise ValueError("Submodule paths/URLs do not match the documented workspace")
    for path, url in sorted(actual.items()):
        entry = git(root, "ls-files", "--stage", "--", path).split()
        if len(entry) < 4 or entry[0] != "160000":
            raise ValueError(f"{path} is not a Git submodule")
        pinned = entry[1]
        module = root / path
        if require_checkouts:
            if not (module / ".git").exists():
                raise ValueError(f"{path} is not initialized; run git submodule update --init --recursive")
            if git(module, "rev-parse", "HEAD") != pinned:
                raise ValueError(f"{path} differs from its pinned commit")
            if not (module / "README.md").is_file():
                raise ValueError(f"{path} has no README")
            if path.endswith(("openast", "openatt")):
                metadata = json.loads((module / "project.json").read_text())
                if metadata["project"] != Path(path).name or metadata["implemented"] is not False:
                    raise ValueError(f"{path} scaffold maturity metadata is inconsistent")
        print(f"{path}: {pinned[:12]} ({url})")
    for name in ("evidence", "action-contract"):
        schema = json.loads((root / "spec" / f"{name}.schema.json").read_text())
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ValueError(f"Unexpected schema dialect for {name}")
    print("Workspace metadata checked; this is not cryptographic or protocol validation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-checkouts", action="store_true")
    args = parser.parse_args()
    check(Path(__file__).resolve().parents[1], args.require_checkouts)
