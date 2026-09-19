#!/usr/bin/env python3
"""Repository entry point. Python standard library only."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.common import EnvironmentError, inside, read_json

ROOT = Path(__file__).resolve().parent


def validate(root=ROOT):
    manifest = read_json(root / "environment.json")
    if manifest.get("schema_version") != 1:
        raise EnvironmentError("Unsupported environment manifest version")
    ids = []
    for cap in manifest["capabilities"]:
        ids.append(cap["id"])
        if cap.get("source") and not inside(root, cap["source"]).is_dir():
            raise EnvironmentError(f"Missing source for {cap['id']}")
    if len(ids) != len(set(ids)):
        raise EnvironmentError("Duplicate capability IDs")
    for path in sorted((root / "harnesses").glob("*/adapter.json")):
        adapter = read_json(path)
        if adapter.get("schema_version") != 1 or adapter["id"] != path.parent.name:
            raise EnvironmentError(f"Invalid adapter identity: {path}")
        if adapter["status"] not in {"implemented", "pending"}:
            raise EnvironmentError(f"Unknown adapter status: {path}")
        if not set(adapter["capabilities"]).issubset(ids):
            raise EnvironmentError(f"Unknown capability in {path}")
        if adapter["status"] == "implemented":
            if not inside(path.parent, adapter["entrypoint"]).is_file():
                raise EnvironmentError(f"Missing entrypoint in {path}")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "list", "plan", "status", "apply", "sync"])
    parser.add_argument("harness", nargs="?")
    parser.add_argument("--codex", help="Codex executable override (or ENVIRONMENT_CODEX_BIN)")
    parser.add_argument("--adopt-existing", action="store_true", help="Back up and replace differing copies of managed personal skills")
    parser.add_argument("--migrate-legacy-jev", action="store_true", help="Replace the known jev-decisions@personal registration after installing the repository version")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = validate()
        if args.command == "validate":
            print("Manifest and adapter registrations are valid.")
            return 0
        if args.command == "list":
            for p in sorted((ROOT / "harnesses").glob("*/adapter.json")):
                a = read_json(p)
                print(f"{a['id']}: {a['status']} (owner: {a['owner']})")
            return 0
        if not args.harness or not args.harness.replace("-", "").isalnum():
            raise EnvironmentError("Specify a registered harness, e.g. codex")
        directory = inside(ROOT, "harnesses/" + args.harness)
        if not (directory / "adapter.json").exists():
            raise EnvironmentError("Unknown harness. Follow docs/adapter-contract.md to add it.")
        registration = read_json(directory / "adapter.json")
        if registration["status"] != "implemented":
            raise EnvironmentError(f"{args.harness} is pending; its owning harness must implement it. See {directory / 'README.md'}")
        if args.command == "sync":
            dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
            if dirty.strip():
                raise EnvironmentError("Commit or stash repository edits before sync; no automatic stash or merge.")
            subprocess.run(["git", "pull", "--ff-only"], cwd=ROOT, check=True)
            # Re-execute the updated entrypoint rather than running stale in-memory code.
            tail = [x for x in (argv if argv is not None else sys.argv[1:])]
            tail[0] = "apply"
            os.execv(sys.executable, [sys.executable, str(ROOT / "env.py"), *tail])
        spec = importlib.util.spec_from_file_location("environment_adapter", inside(directory, registration["entrypoint"]))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.execute(args, ROOT, manifest)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for item in result["items"]:
                print(f"{item['status']:12} {item['id']}: {item['detail']}")
            if result.get("unmanaged_plugins"):
                print("Unmanaged plugins (unchanged): " + ", ".join(result["unmanaged_plugins"]))
        return 0 if result["converged"] or args.command == "plan" else 1
    except (EnvironmentError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"environment: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
