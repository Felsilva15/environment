"""Codex-owned adapter. Uses native CLI installation, never edits full user configs."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from contextlib import contextmanager
from pathlib import Path

from scripts.common import (
    EnvironmentError, copy_source, digest, install_tree, managed_status,
    read_json, run, write_json,
)

MARKETPLACE = "felipe-environment"
JEV = "jev-decisions@" + MARKETPLACE
LEGACY_JEV = "jev-decisions@personal"
DRIVE = "google-drive@openai-curated-remote"
SUPPORTED = {"no-ai-slop", "jev", "google-drive"}


@contextmanager
def exclusive_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise EnvironmentError(f"Another apply may be running. Inspect before removing stale lock: {path}")
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)


class Adapter:
    def __init__(self, root, manifest, home=None, runner=run, codex=None):
        self.root = Path(root)
        self.home = Path(home) if home is not None else Path.home()
        self.runner = runner
        self.capabilities = {c["id"]: c for c in manifest["capabilities"]}
        self.local = self.root / ".local/codex"
        self.receipt_path = self.local / "receipt.json"
        self.template = self.root / "harnesses/codex/marketplace"
        self.runtime = self.root / self.capabilities["jev"]["source"]
        self.skill_source = self.root / self.capabilities["no-ai-slop"]["source"]
        self.skill_target = self.home / ".agents/skills/no-ai-slop"
        bundled = self.home / ".codex/plugins/.plugin-appserver/codex"
        self.codex = codex or os.environ.get("ENVIRONMENT_CODEX_BIN")
        if not self.codex:
            # Desktop's CLI includes its remote plugin catalogue. A separate CLI on PATH
            # may only expose local marketplaces even when both use the same config.
            self.codex = str(bundled) if bundled.is_file() else shutil.which("codex")

    def receipt(self):
        return read_json(self.receipt_path) if self.receipt_path.exists() else {}

    def desired_version(self):
        content = hashlib.sha256((digest(self.template) + digest(self.runtime)).encode()).hexdigest()[:20]
        base = read_json(self.template / "plugins/jev-decisions/.codex-plugin/plugin.json")["version"].split("+")[0]
        return f"{base}+codex.{content}"

    def installed(self):
        if not self.codex:
            raise EnvironmentError("Codex CLI not found. Install Codex or set ENVIRONMENT_CODEX_BIN.")
        payload = json.loads(self.runner([self.codex, "plugin", "list", "--json"]))
        return {p["pluginId"]: p for p in payload["installed"]}

    def plan(self):
        state = self.receipt()
        status, desired = managed_status(self.skill_source, self.skill_target, state.get("skill_digest"))
        items = [{"id": "no-ai-slop", "status": status, "detail": str(self.skill_target)}]
        installed = self.installed()
        desired_version = self.desired_version()
        jev = installed.get(JEV)
        jev_status = "install" if not jev else "ok" if jev.get("enabled") and jev.get("version") == desired_version else "update"
        items.append({"id": "jev", "status": jev_status, "detail": f"{JEV} version {desired_version}"})
        drive = installed.get(DRIVE)
        items.append({"id": "google-drive", "status": "ok" if drive and drive.get("enabled") else "install", "detail": "Native plugin; OAuth authorization must be completed on each computer."})
        if LEGACY_JEV in installed:
            items.append({"id": "legacy-jev", "status": "migration", "detail": "Use --migrate-legacy-jev to replace jev-decisions@personal after the repository plugin is installed."})
        for cap in sorted(set(self.capabilities) - SUPPORTED):
            items.append({"id": cap, "status": "unsupported", "detail": "Codex adapter has no binding; implement it explicitly."})
        # Discovery is read-only. Vendor defaults and integrations are never removal targets.
        unmanaged = sorted(
            p for p, row in installed.items()
            if p not in {JEV, LEGACY_JEV, DRIVE}
            and row.get("installPolicy") != "INSTALLED_BY_DEFAULT"
            and row.get("marketplaceName") not in {"openai-bundled", "openai-primary-runtime"}
        )
        return {"harness": "codex", "executable": self.codex, "items": items, "converged": all(i["status"] == "ok" for i in items), "unmanaged_plugins": unmanaged}

    def build_marketplace(self):
        """Render native packaging with the shared runtime; generated content stays out of Git."""
        target = self.local / "marketplace"
        stage = self.local / "marketplace.stage"
        if stage.exists():
            shutil.rmtree(stage)
        copy_source(self.template, stage)
        plugin = stage / "plugins/jev-decisions"
        copy_source(self.runtime, plugin)
        manifest_path = plugin / ".codex-plugin/plugin.json"
        metadata = read_json(manifest_path)
        metadata["version"] = self.desired_version()
        write_json(manifest_path, metadata)
        npm = shutil.which("npm")
        node = shutil.which("node")
        if not npm or not node:
            raise EnvironmentError("Node.js 20+ and npm are required for Jev.")
        major = int(self.runner([node, "--version"]).strip().lstrip("v").split(".")[0])
        if major < 20:
            raise EnvironmentError("Jev requires Node.js 20 or newer.")
        self.runner([npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=plugin)
        # Keep the previously generated source if dependency installation fails.
        if target.exists():
            shutil.rmtree(target)
        stage.rename(target)
        return target

    def apply(self, adopt=False, migrate=False):
        with exclusive_lock(self.local / "apply.lock"):
            plan = self.plan()
            statuses = {i["id"]: i["status"] for i in plan["items"]}
            if "unsupported" in statuses.values():
                raise EnvironmentError("Unsupported capabilities in manifest; no changes applied.")
            if statuses["no-ai-slop"] == "conflict" and not adopt:
                raise EnvironmentError("Local no-ai-slop differs. Review it, then use --adopt-existing to back it up and adopt the repository copy.")
            if "legacy-jev" in statuses and not migrate:
                raise EnvironmentError("Legacy Jev is installed. Use --migrate-legacy-jev for the one-time migration; no changes applied.")
            if statuses["jev"] != "ok":
                marketplace = self.build_marketplace()
                self.runner([self.codex, "plugin", "marketplace", "add", str(marketplace)])
                self.runner([self.codex, "plugin", "add", JEV, "--json"])
                current = self.installed().get(JEV)
                if not current or not current.get("enabled") or current.get("version") != self.desired_version():
                    raise EnvironmentError("Jev installation could not be verified; legacy registration preserved.")
            if "legacy-jev" in statuses:
                self.runner([self.codex, "plugin", "remove", LEGACY_JEV, "--json"])
            if statuses["google-drive"] != "ok":
                self.runner([self.codex, "plugin", "add", DRIVE, "--json"])
            if statuses["no-ai-slop"] != "ok":
                backup = self.local / "backups" / str(time.time_ns())
                install_tree(self.skill_source, self.skill_target, backup)
            # Receipt is written only after verifying resources; it contains no credentials.
            after = self.plan()
            if not after["converged"]:
                raise EnvironmentError("Apply is incomplete. Run plan to inspect remaining drift; retry is safe.")
            write_json(self.receipt_path, {
                "schema_version": 1,
                "skill_digest": digest(self.skill_source),
                "jev_version": self.desired_version(),
                "auth_verification": "Installation checked; OAuth/API authorization is not asserted.",
            })
            return after


def execute(args, root, manifest):
    adapter = Adapter(root, manifest, codex=args.codex)
    if args.command == "apply":
        return adapter.apply(adopt=args.adopt_existing, migrate=args.migrate_legacy_jev)
    return adapter.plan()
