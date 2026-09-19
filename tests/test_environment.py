import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import env
from scripts.common import EnvironmentError, copy_source, digest, inside, write_json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("codex_adapter", ROOT / "harnesses/codex/adapter.py")
codex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codex)


class FakeCLI:
    def __init__(self, root):
        self.root = root
        self.plugins = {}
        self.calls = []
        self.fail_install = False

    def __call__(self, command, cwd=None, capture=True):
        command = [str(x) for x in command]
        self.calls.append(command)
        if command[1:] == ["--version"]:
            return "v22.0.0\n"
        if "ci" in command:
            return "installed fixture dependencies"
        if command[1:] == ["plugin", "list", "--json"]:
            return json.dumps({"installed": list(self.plugins.values())})
        if command[1:4] == ["plugin", "marketplace", "add"]:
            return "registered"
        if command[1:3] == ["plugin", "add"]:
            if self.fail_install:
                raise EnvironmentError("simulated install failure")
            plugin = command[3]
            version = "remote-version"
            if plugin == codex.JEV:
                version = json.loads((self.root / ".local/codex/marketplace/plugins/jev-decisions/.codex-plugin/plugin.json").read_text())["version"]
            self.plugins[plugin] = {"pluginId": plugin, "enabled": True, "version": version}
            return "{}"
        if command[1:3] == ["plugin", "remove"]:
            del self.plugins[command[3]]
            return "{}"
        raise AssertionError(command)


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        for name in ["environment.json"]:
            shutil.copy2(ROOT / name, self.root / name)
        for name in ["shared", "harnesses"]:
            copy_source(ROOT / name, self.root / name)
        self.home = self.base / "home"
        self.cli = FakeCLI(self.root)
        self.manifest = json.loads((self.root / "environment.json").read_text())
        self.adapter = codex.Adapter(self.root, self.manifest, self.home, self.cli, "fake-codex")
        self.binaries = patch.object(codex.shutil, "which", side_effect=lambda x: "fake-" + x)
        self.binaries.start()
        self.addCleanup(self.binaries.stop)

    def test_plan_is_read_only_and_reports_fresh_install(self):
        result = self.adapter.plan()
        self.assertFalse(result["converged"])
        self.assertFalse((self.root / ".local").exists())
        self.assertFalse(self.home.exists())
        self.assertTrue(all("list" in c for c in self.cli.calls))

    def test_desktop_cli_is_preferred_but_explicit_override_wins(self):
        bundled = self.home / ".codex/plugins/.plugin-appserver/codex"
        bundled.parent.mkdir(parents=True)
        bundled.write_text("fixture")
        with patch.dict(codex.os.environ, {}, clear=True):
            adapter = codex.Adapter(self.root, self.manifest, self.home, self.cli)
            self.assertEqual(adapter.codex, str(bundled))
            adapter = codex.Adapter(self.root, self.manifest, self.home, self.cli, "chosen-codex")
            self.assertEqual(adapter.codex, "chosen-codex")

    def test_fresh_apply_is_idempotent_and_keeps_unknown_plugins(self):
        self.cli.plugins["unrelated@other"] = {"pluginId": "unrelated@other", "enabled": True}
        self.assertTrue(self.adapter.apply()["converged"])
        self.assertEqual(digest(self.adapter.skill_source), digest(self.adapter.skill_target))
        self.cli.calls.clear()
        self.assertTrue(self.adapter.apply()["converged"])
        self.assertTrue(all("list" in c for c in self.cli.calls))
        self.assertIn("unrelated@other", self.cli.plugins)

    def test_repository_skill_update_is_backed_up(self):
        self.adapter.apply()
        original = (self.adapter.skill_target / "SKILL.md").read_text()
        with (self.adapter.skill_source / "SKILL.md").open("a") as f:
            f.write("\nNew source preference.\n")
        self.assertEqual(self.adapter.plan()["items"][0]["status"], "update")
        self.adapter.apply()
        backups = list((self.root / ".local/codex/backups").glob("*/no-ai-slop/SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)

    def test_local_edit_blocks_all_mutations_until_explicit_adoption(self):
        self.adapter.apply()
        local = self.adapter.skill_target / "SKILL.md"
        local.write_text("local edit")
        self.cli.calls.clear()
        with self.assertRaisesRegex(EnvironmentError, "Local no-ai-slop differs"):
            self.adapter.apply()
        self.assertTrue(all("list" in c for c in self.cli.calls))
        self.assertEqual(local.read_text(), "local edit")
        self.adapter.apply(adopt=True)
        self.assertTrue(any(p.read_text() == "local edit" for p in (self.root / ".local/codex/backups").glob("*/no-ai-slop/SKILL.md")))

    def test_legacy_migration_requires_flag_and_keeps_old_until_new_verified(self):
        self.cli.plugins[codex.LEGACY_JEV] = {"pluginId": codex.LEGACY_JEV, "enabled": True}
        with self.assertRaisesRegex(EnvironmentError, "Legacy Jev"):
            self.adapter.apply()
        self.cli.fail_install = True
        with self.assertRaisesRegex(EnvironmentError, "simulated"):
            self.adapter.apply(migrate=True)
        self.assertIn(codex.LEGACY_JEV, self.cli.plugins)
        self.cli.fail_install = False
        self.assertTrue(self.adapter.apply(migrate=True)["converged"])
        self.assertNotIn(codex.LEGACY_JEV, self.cli.plugins)
        self.assertIn(codex.JEV, self.cli.plugins)

    def test_runtime_change_changes_plugin_cache_identity(self):
        before = self.adapter.desired_version()
        with (self.adapter.runtime / "scripts/server.mjs").open("a") as f:
            f.write("\n// changed source\n")
        self.assertNotEqual(before, self.adapter.desired_version())

    def test_disabled_drive_is_reenabled_not_treated_as_healthy(self):
        self.cli.plugins[codex.DRIVE] = {"pluginId": codex.DRIVE, "enabled": False}
        self.adapter.apply()
        self.assertTrue(self.cli.plugins[codex.DRIVE]["enabled"])

    def test_unsupported_capability_refuses_apply(self):
        self.adapter.capabilities["future"] = {"id": "future"}
        with self.assertRaisesRegex(EnvironmentError, "Unsupported"):
            self.adapter.apply()
        self.assertFalse(self.home.exists())

    def test_manifest_rejects_path_traversal_and_duplicate_ids(self):
        with self.assertRaises(EnvironmentError):
            inside(self.root, "../../elsewhere")
        self.manifest["capabilities"].append(self.manifest["capabilities"][0])
        write_json(self.root / "environment.json", self.manifest)
        with self.assertRaisesRegex(EnvironmentError, "Duplicate"):
            env.validate(self.root)

    def test_apply_lock_refuses_concurrent_mutation(self):
        with codex.exclusive_lock(self.adapter.local / "apply.lock"):
            with self.assertRaisesRegex(EnvironmentError, "Another apply"):
                self.adapter.apply()

    def test_source_symlink_is_rejected(self):
        source = self.adapter.skill_source / "escape"
        try:
            source.symlink_to(self.root / "environment.json")
        except OSError:
            self.skipTest("Symlink creation unavailable")
        with self.assertRaisesRegex(EnvironmentError, "symlink"):
            self.adapter.plan()

    def test_local_secret_file_is_not_packaged(self):
        (self.adapter.runtime / ".env").write_text("TYPESAFE_API_KEY=fixture-only")
        with self.assertRaisesRegex(EnvironmentError, "Credential-like"):
            self.adapter.plan()


if __name__ == "__main__":
    unittest.main()
