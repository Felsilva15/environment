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
        self.skill_source, self.skill_target = self.adapter.skills["no-ai-slop"]
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
        for source, target in self.adapter.skills.values():
            self.assertEqual(digest(source), digest(target))
        self.cli.calls.clear()
        self.assertTrue(self.adapter.apply()["converged"])
        self.assertTrue(all("list" in c for c in self.cli.calls))
        self.assertIn("unrelated@other", self.cli.plugins)

    def test_repository_skill_update_is_backed_up(self):
        self.adapter.apply()
        original = (self.skill_target / "SKILL.md").read_text()
        with (self.skill_source / "SKILL.md").open("a") as f:
            f.write("\nNew source preference.\n")
        self.assertEqual(self.adapter.plan()["items"][0]["status"], "update")
        self.adapter.apply()
        backups = list((self.root / ".local/codex/backups").glob("*/no-ai-slop/SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)

    def test_local_edit_blocks_all_mutations_until_explicit_adoption(self):
        self.adapter.apply()
        local = self.skill_target / "SKILL.md"
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

    def test_legacy_skill_receipt_allows_update_and_new_skill_install(self):
        self.adapter.apply()
        original_digest = digest(self.skill_target)
        write_json(self.adapter.receipt_path, {"schema_version": 1, "skill_digest": original_digest})
        second_source, second_target = self.adapter.skills["software-design"]
        shutil.rmtree(second_target)
        with (self.skill_source / "SKILL.md").open("a") as stream:
            stream.write("\nUpdated preference.\n")
        statuses = {i["id"]: i["status"] for i in self.adapter.plan()["items"]}
        self.assertEqual(statuses["no-ai-slop"], "update")
        self.assertEqual(statuses["software-design"], "install")
        self.adapter.apply()
        self.assertEqual(digest(second_source), digest(second_target))
        self.assertEqual(set(self.adapter.receipt()["skill_digests"]), set(self.adapter.skills))

    def test_second_skill_conflict_prevents_first_skill_update(self):
        self.adapter.apply()
        original = digest(self.skill_target)
        with (self.skill_source / "SKILL.md").open("a") as stream:
            stream.write("\nUpdated preference.\n")
        _, second_target = self.adapter.skills["software-design"]
        (second_target / "SKILL.md").write_text("local preference")
        self.cli.plugins[codex.DRIVE]["enabled"] = False
        self.cli.calls.clear()
        with self.assertRaisesRegex(EnvironmentError, "Local software-design differs"):
            self.adapter.apply()
        self.assertEqual(digest(self.skill_target), original)
        self.assertTrue(all("list" in c for c in self.cli.calls))
        self.adapter.apply(adopt=True)
        backups = list((self.adapter.local / "backups").glob("*/software-design/SKILL.md"))
        self.assertEqual([p.read_text() for p in backups], ["local preference"])

    def test_new_skill_requires_registration_then_installs_without_code_binding(self):
        cap = {"id": "another-skill", "kind": "skill", "source": "shared/skills/another-skill"}
        source = self.root / cap["source"]
        source.mkdir()
        (source / "SKILL.md").write_text("---\nname: another-skill\ndescription: fixture\n---\n")
        self.manifest["capabilities"].append(cap)
        adapter = codex.Adapter(self.root, self.manifest, self.home, self.cli, "fake-codex")
        with self.assertRaisesRegex(EnvironmentError, "Unsupported"):
            adapter.apply()
        registration_path = self.root / "harnesses/codex/adapter.json"
        registration = json.loads(registration_path.read_text())
        registration["capabilities"].append(cap["id"])
        write_json(registration_path, registration)
        adapter = codex.Adapter(self.root, self.manifest, self.home, self.cli, "fake-codex")
        self.assertTrue(adapter.apply()["converged"])
        self.assertEqual(digest(source), digest(self.home / ".agents/skills/another-skill"))

    def install_retired_fixture(self):
        retired = self.adapter.retired_skills[0]
        target = self.home / ".agents/skills" / retired["id"]
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("previous combined instructions")
        retired["sha256"] = digest(target)
        return target

    def test_explicit_retirement_backs_up_only_after_replacements_install(self):
        old = self.install_retired_fixture()
        original = digest(old)
        self.assertIn("retire", [i["status"] for i in self.adapter.plan()["items"]])
        self.assertTrue(self.adapter.apply()["converged"])
        self.assertFalse(old.exists())
        backups = list((self.adapter.local / "backups").glob("*/" + old.name))
        self.assertEqual([digest(p) for p in backups], [original])
        for source, target in self.adapter.skills.values():
            self.assertEqual(digest(source), digest(target))
        self.cli.calls.clear()
        self.adapter.apply()
        self.assertEqual(len(list((self.adapter.local / "backups").glob("*/" + old.name))), 1)
        self.assertTrue(all("list" in c for c in self.cli.calls))

    def test_retired_local_edit_blocks_all_mutation_even_with_adopt(self):
        old = self.install_retired_fixture()
        (old / "SKILL.md").write_text("unsynced change")
        with self.assertRaisesRegex(EnvironmentError, "has local changes"):
            self.adapter.apply(adopt=True)
        self.assertEqual((old / "SKILL.md").read_text(), "unsynced change")
        self.assertFalse(self.skill_target.exists())
        self.assertTrue(all("list" in c for c in self.cli.calls))

    def test_failed_replacement_preserves_retired_skill(self):
        old = self.install_retired_fixture()
        self.cli.fail_install = True
        with self.assertRaisesRegex(EnvironmentError, "simulated"):
            self.adapter.apply()
        self.assertTrue(old.is_dir())
        self.assertFalse((self.adapter.local / "backups").exists())

    def test_skill_target_symlink_is_a_conflict(self):
        external = self.base / "external"
        copy_source(self.skill_source, external)
        self.skill_target.parent.mkdir(parents=True)
        self.skill_target.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(EnvironmentError, "Local no-ai-slop differs"):
            self.adapter.apply()
        self.assertTrue(self.skill_target.is_symlink())
        self.assertEqual(digest(external), digest(self.skill_source))

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

    def test_capability_id_cannot_escape_skill_destination(self):
        self.manifest["capabilities"][0]["id"] = "../escape"
        write_json(self.root / "environment.json", self.manifest)
        with self.assertRaisesRegex(EnvironmentError, "Invalid capability ID"):
            env.validate(self.root)

    def test_apply_lock_refuses_concurrent_mutation(self):
        with codex.exclusive_lock(self.adapter.local / "apply.lock"):
            with self.assertRaisesRegex(EnvironmentError, "Another apply"):
                self.adapter.apply()

    def test_source_symlink_is_rejected(self):
        source = self.skill_source / "escape"
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
