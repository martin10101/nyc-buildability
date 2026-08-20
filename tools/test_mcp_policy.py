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

# G4 MAJOR-1: the audited identifiers (project-control/reports/M0-T077-mcp-audit.md),
# pinned here INDEPENDENTLY of the validator's own constants. A coordinated edit
# that shrinks both the settings lists and the validator's tuples in one pass now
# fails these pins instead of silently shrinking the test with it.
AUDITED_DENIED_IDENTIFIERS = (
    "pencil", "supabase", "mysql", "sequential-thinking", "playwright",
)
AUDITED_MCPJSON_IDENTIFIERS = (
    "supabase", "mysql", "sequential-thinking", "playwright",
)


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

    # ---- p8 deny-first tool rule ----

    def test_permissions_block_removed_fails(self):
        errs = self.errors_for(self.mutate(permissions=vmp))
        self.assertTrue(any(e.startswith("p8") for e in errs))

    def test_mcp_tool_deny_rule_removed_fails(self):
        errs = self.errors_for(self.mutate(permissions={"deny": []}))
        self.assertTrue(any(e.startswith("p8") for e in errs))

    def test_mcp_tool_deny_rule_narrowed_fails(self):
        errs = self.errors_for(self.mutate(permissions={"deny": ["mcp__supabase__*"]}))
        self.assertTrue(any(e.startswith("p8") for e in errs))

    def test_extra_deny_rules_alongside_wildcard_pass(self):
        settings = copy.deepcopy(self.intact)
        settings["permissions"] = {"deny": ["mcp__*", "WebFetch"]}
        self.assertEqual(self.errors_for(settings), [])

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

    def test_hook_decoy_substring_fails(self):
        # G3 F-3: all three guard registrations deleted, filenames surviving only
        # inside one inert echo command (the review's exact decoy) must NOT count
        # as "preserved" — the bare filename lacks the required full script path.
        decoy = self.mutate(hooks={
            "SessionStart": [{"hooks": [{
                "type": "command",
                "command": "echo disabled: agent_dispatch_guard.py "
                           "readonly_agent_guard.py directive_reminder.py"}]}]})
        errs = self.errors_for(decoy)
        for name in ("agent_dispatch_guard", "readonly_agent_guard",
                     "directive_reminder"):
            with self.subTest(hook=name):
                self.assertTrue(any(e.startswith("p7") and name in e for e in errs))

    def test_hook_names_in_noncommand_field_fail(self):
        noncommand = self.mutate(hooks={
            "SessionStart": [{"matcher": ".claude/hooks/agent_dispatch_guard.py "
                                         ".claude/hooks/readonly_agent_guard.py "
                                         ".claude/hooks/directive_reminder.py",
                              "hooks": [{"type": "command", "command": "echo hi"}]}]})
        errs = self.errors_for(noncommand)
        self.assertTrue(all(any(e.startswith("p7") and name in e for e in errs)
                            for name in ("agent_dispatch_guard",
                                         "readonly_agent_guard",
                                         "directive_reminder")))

    # ---- p9 schema-shape guards (G3 F-2: consumer discards the whole file) ----

    def test_model_wrong_type_fails(self):
        errs = self.errors_for(self.mutate(model=["claude-fable-5"]))
        self.assertTrue(any(e.startswith("p9") and "model" in e for e in errs))

    def test_fallback_model_string_fails(self):
        errs = self.errors_for(self.mutate(fallbackModel="claude-opus-4-8"))
        self.assertTrue(any(e.startswith("p9") and "fallbackModel" in e
                            for e in errs))

    def test_invalid_default_mode_fails(self):
        weakened = copy.deepcopy(self.intact)
        weakened["permissions"]["defaultMode"] = "notARealMode"
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p9") and "defaultMode" in e
                            for e in errs))

    def test_valid_default_mode_passes(self):
        settings = copy.deepcopy(self.intact)
        settings["permissions"]["defaultMode"] = "plan"
        self.assertEqual(self.errors_for(settings), [])

    # ---- audited-identifier pinning + CI wiring (G4 MAJOR-1 / MAJOR-2) ----

    def test_audited_identifiers_pinned_independently(self):
        self.assertEqual(tuple(vmp.DENIED_SERVER_NAMES), AUDITED_DENIED_IDENTIFIERS)
        self.assertEqual(tuple(vmp.DISABLED_MCPJSON_NAMES),
                         AUDITED_MCPJSON_IDENTIFIERS)
        committed_denied = {e.get("serverName")
                            for e in self.intact["deniedMcpServers"]}
        self.assertTrue(set(AUDITED_DENIED_IDENTIFIERS) <= committed_denied)
        self.assertTrue(set(AUDITED_MCPJSON_IDENTIFIERS)
                        <= set(self.intact["disabledMcpjsonServers"]))

    def test_ci_wires_validator_and_test_steps(self):
        # G4 MAJOR-2: deleting a control-plane step must fail a machine check.
        # Honest residual: if BOTH steps are deleted, neither this test nor the
        # validator runs in CI — a self-referential guard cannot survive removal
        # of every executor of itself; that final case is caught by the validator's
        # p10 twin check while the validator step survives, and beyond that only
        # by diff review (disclosed in the policy doc).
        ci = (HERE.parent / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8")
        self.assertIn("python3 tools/validate_mcp_policy.py --check", ci)
        self.assertIn("python3 tools/test_mcp_policy.py", ci)

    # ---- p9 whole-file shape assertion (G3 re-review probes 59-63) ----

    def test_probe59_permissions_allow_not_a_list_fails(self):
        weakened = copy.deepcopy(self.intact)
        weakened["permissions"]["allow"] = "not-a-list"
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p9") and "allow" in e for e in errs))

    def test_probe60_env_not_an_object_fails(self):
        errs = self.errors_for(self.mutate(env="not-an-object"))
        self.assertTrue(any(e.startswith("p9") and "'env'" in e for e in errs))

    def test_probe61_fallback_model_non_string_elements_fails(self):
        errs = self.errors_for(self.mutate(fallbackModel=[123]))
        self.assertTrue(any(e.startswith("p9") and "fallbackModel" in e
                            for e in errs))

    def test_probe62_schema_key_number_fails(self):
        weakened = copy.deepcopy(self.intact)
        weakened["$schema"] = 12345
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p9") and "$schema" in e for e in errs))

    def test_probe63_unknown_key_fails_closed(self):
        weakened = copy.deepcopy(self.intact)
        weakened["cleanupPeriodDays"] = "thirty"
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p9") and "cleanupPeriodDays" in e
                            for e in errs))

    def test_unknown_permissions_subkey_fails_closed(self):
        weakened = copy.deepcopy(self.intact)
        weakened["permissions"]["notARealField"] = True
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p9") and "notARealField" in e
                            for e in errs))

    def test_denied_entry_with_extra_key_fails_closed(self):
        weakened = copy.deepcopy(self.intact)
        weakened["deniedMcpServers"] = (weakened["deniedMcpServers"]
                                        + [{"serverName": "x", "toolName": "y"}])
        errs = self.errors_for(weakened)
        self.assertTrue(any(e.startswith("p9") and "deniedMcpServers" in e
                            for e in errs))

    # ---- exit codes ----

    def test_main_exit_one_on_weakened_policy(self):
        path = write_fixture(self.tmp, self.mutate(disableClaudeAiConnectors=False))
        self.assertEqual(vmp.main(["--check", "--settings", str(path)]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
