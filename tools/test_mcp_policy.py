#!/usr/bin/env python3
"""Tests for the repository MCP default-deny policy validator (D-020 / M0-T077).

Stdlib-only (unittest); runnable as `python3 tools/test_mcp_policy.py` so the
control-plane CI job can execute it. Proves the validator is fail-closed: the
committed policy passes, and EVERY removal/weakening mutation of a policy
invariant — including the ones a well-meaning future edit is most likely to
make — is caught with a nonzero result. Hermetic: fixtures live in temp dirs;
the real .claude/settings.json is only ever READ.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import validate_mcp_policy as vmp  # noqa: E402


def write_fixture(tmp: Path, settings: dict) -> Path:
    path = tmp / "settings.json"
    path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return path


class McpPolicyValidatorTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # The committed settings are the canonical intact fixture: this both
        # anchors the tests to reality and proves the repo file passes as-is.
        self.intact = json.loads(vmp.DEFAULT_SETTINGS.read_text(encoding="utf-8"))

    def errors_for(self, settings: dict) -> list[str]:
        return vmp.validate(write_fixture(self.tmp, settings))

    def mutate(self, **changes) -> dict:
        settings = copy.deepcopy(self.intact)
        for key, value in changes.items():
            if value is vmp:  # sentinel: delete the key
                settings.pop(key, None)
            else:
                settings[key] = value
        return settings

    # ---- intact policy ----

    def test_committed_settings_pass(self):
        self.assertEqual(vmp.validate(vmp.DEFAULT_SETTINGS), [])

    def test_intact_fixture_passes_in_temp_dir(self):
        self.assertEqual(self.errors_for(self.intact), [])

    def test_main_check_exit_zero(self):
        path = write_fixture(self.tmp, self.intact)
        self.assertEqual(vmp.main(["--check", "--settings", str(path)]), 0)

    # ---- p1 file-level failures ----

    def test_missing_file_fails(self):
        errs = vmp.validate(self.tmp / "nope.json")
        self.assertTrue(errs and errs[0].startswith("p1"))

    def test_unparseable_file_fails(self):
        path = self.tmp / "settings.json"
        path.write_text("{not json", encoding="utf-8")
        errs = vmp.validate(path)
        self.assertTrue(errs and errs[0].startswith("p1"))

    # ---- p2 claude.ai connectors ----

    def test_connectors_flag_removed_fails(self):
        errs = self.errors_for(self.mutate(disableClaudeAiConnectors=vmp))
        self.assertTrue(any(e.startswith("p2") for e in errs))

    def test_connectors_flag_false_fails(self):
        errs = self.errors_for(self.mutate(disableClaudeAiConnectors=False))
        self.assertTrue(any(e.startswith("p2") for e in errs))

    def test_connectors_flag_truthy_string_fails(self):
        errs = self.errors_for(self.mutate(disableClaudeAiConnectors="true"))
        self.assertTrue(any(e.startswith("p2") for e in errs))

    # ---- p3 default-deny allowlist ----

    def test_allowlist_removed_fails(self):
        errs = self.errors_for(self.mutate(allowedMcpServers=vmp))
        self.assertTrue(any(e.startswith("p3") for e in errs))

    def test_allowlist_nonempty_fails(self):
        weakened = self.mutate(allowedMcpServers=[{"serverName": "supabase"}])
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p3") for e in errs))

    # ---- p4 audited deny identifiers ----

    def test_each_denied_identifier_is_required(self):
        for name in vmp.DENIED_SERVER_NAMES:
            with self.subTest(server=name):
                weakened = copy.deepcopy(self.intact)
                weakened["deniedMcpServers"] = [
                    e for e in weakened["deniedMcpServers"]
                    if e.get("serverName") != name
                ]
                errs = self.errors_for(weakened)
                self.assertTrue(any(e.startswith("p4") and f"'{name}'" in e
                                    for e in errs))

    def test_denylist_wrong_shape_fails(self):
        errs = self.errors_for(self.mutate(deniedMcpServers=["pencil"]))
        self.assertTrue(any(e.startswith("p4") for e in errs))

    # ---- p5 audited .mcp.json rejections ----

    def test_each_disabled_mcpjson_identifier_is_required(self):
        for name in vmp.DISABLED_MCPJSON_NAMES:
            with self.subTest(server=name):
                weakened = copy.deepcopy(self.intact)
                weakened["disabledMcpjsonServers"] = [
                    n for n in weakened["disabledMcpjsonServers"] if n != name
                ]
                errs = self.errors_for(weakened)
                self.assertTrue(any(e.startswith("p5") and f"'{name}'" in e
                                    for e in errs))

    # ---- p6 auto-approval ----

    def test_auto_approval_removed_fails(self):
        errs = self.errors_for(self.mutate(enableAllProjectMcpServers=vmp))
        self.assertTrue(any(e.startswith("p6") for e in errs))

    def test_auto_approval_true_fails(self):
        errs = self.errors_for(self.mutate(enableAllProjectMcpServers=True))
        self.assertTrue(any(e.startswith("p6") for e in errs))

    # ---- p7 merge-not-replace preservation ----

    def test_wholesale_replacement_fails(self):
        policy_only = {
            "disableClaudeAiConnectors": True,
            "allowedMcpServers": [],
            "deniedMcpServers": [{"serverName": n} for n in vmp.DENIED_SERVER_NAMES],
            "disabledMcpjsonServers": list(vmp.DISABLED_MCPJSON_NAMES),
            "enableAllProjectMcpServers": False,
        }
        errs = self.errors_for(policy_only)
        self.assertTrue(any(e.startswith("p7") for e in errs))

    def test_dropped_hook_registration_fails(self):
        weakened = copy.deepcopy(self.intact)
        hooks_json = json.dumps(weakened["hooks"]).replace(
            "readonly_agent_guard.py", "somewhere_else.py")
        weakened["hooks"] = json.loads(hooks_json)
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p7") and "readonly_agent_guard" in e
                            for e in errs))

    # ---- exit codes ----

    def test_main_exit_one_on_weakened_policy(self):
        path = write_fixture(self.tmp, self.mutate(disableClaudeAiConnectors=False))
        self.assertEqual(vmp.main(["--check", "--settings", str(path)]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
