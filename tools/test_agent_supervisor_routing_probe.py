#!/usr/bin/env python3
"""D-024 Amendment 14 (M0-T120): shell-routing compatibility.

Qualifying evidence (supervisor-freeze §2: a reproduced defect + inability to
complete an authorized product task): the first live limited-auto run
(`M0-T113-activation-evidence.md` item 4) stopped fail-closed on THREE ad-hoc
shell discovery proposals (two PowerShell + one Bash) that native Read/Grep/Glob
would have done in scope, and no ledger task addressed that worker routing.

This file proves the unit's three teeth WITHOUT contacting a provider:

* R292 - the measured routing fixture is well-formed and honestly labelled, and
  the probe's pure helpers (classify, gather, build) behave; the LIVE run itself
  is captured separately in the routing-evidence report.
* R294 - the native-tool preference block is appended to every worker prompt
  exactly once, names the validation-command rule, and stays quota-clean.
* R295 - the pre-dispatch drift tooth passes only when current routing evidence
  exists for the pinned CLI identity, and fails closed on absent, stale, or
  unreadable evidence (removal-sensitive).
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import claude_runner as cr  # noqa: E402
from tools.agent_supervisor import recovery_probes as rp  # noqa: E402
from tools.agent_supervisor import routing_probe as rpr  # noqa: E402
from tools.agent_supervisor import subagent_contracts as sc  # noqa: E402

PACKAGE = REPO / "tools" / "agent_supervisor"
FIXTURE_PATH = (PACKAGE / "fixtures"
                / "shell_routing_2026-08-29_m0t120_2_1_251.json")


# --------------------------------------------------------------------------
# R292: the measured fixture and the probe's pure helpers
# --------------------------------------------------------------------------


class RoutingFixtureShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))

    def test_the_committed_fixture_is_measured_and_versioned(self) -> None:
        self.assertEqual(self.fixture["schema"], rpr.ROUTING_SCHEMA)
        self.assertIs(self.fixture["measured"], True)
        self.assertEqual(self.fixture["claude_version"], "2.1.251")
        self.assertEqual(self.fixture["task"], "M0-T120")
        self.assertEqual(self.fixture["requirement"], "R292")

    def test_the_fixture_records_native_routing_and_no_shell(self) -> None:
        summary = self.fixture["routing_summary"]
        self.assertEqual(summary["shell"], 0)
        self.assertGreaterEqual(summary["native"], 1)
        self.assertEqual(summary["verdict"], "native_preferred")
        self.assertEqual(summary["discovery_first_tool"], "native")
        self.assertEqual(summary["edit_first_tool"], "native")

    def test_the_provider_call_ceiling_was_respected(self) -> None:
        self.assertLessEqual(self.fixture["provider_calls_made"],
                             rpr.MAX_PROVIDER_CALLS)
        self.assertIs(self.fixture["no_worker_file_write_observed"], True)

    def test_the_argv_shape_is_the_certified_construction(self) -> None:
        shape = self.fixture["argv_shape"]
        self.assertIn("--permission-mode", shape)
        self.assertIn("manual", shape)
        self.assertIn("--permission-prompt-tool", shape)
        self.assertIn("stdio", shape)
        # The machine-specific executable path is redacted, never committed.
        self.assertEqual(shape[0], "<executable>")

    def test_no_username_or_temp_path_leaks_into_the_fixture(self) -> None:
        raw = FIXTURE_PATH.read_text(encoding="utf-8")
        self.assertNotIn(str(pathlib.Path.home()), raw)
        self.assertNotIn(tempfile.gettempdir(), raw)


class ClassifyToolTests(unittest.TestCase):
    def test_native_tools_classify_native(self) -> None:
        for name in ("Read", "Grep", "Glob", "Edit", "Write"):
            self.assertEqual(rpr.classify_tool(name, {}), "native", name)

    def test_shell_tools_classify_shell(self) -> None:
        self.assertEqual(rpr.classify_tool("Bash", {"command": "ls"}), "shell")

    def test_a_shell_program_in_a_generic_tool_is_shell(self) -> None:
        self.assertEqual(
            rpr.classify_tool("mcp__run", {"command": "powershell -Command dir"}),
            "shell")

    def test_an_unknown_tool_with_no_shell_program_is_other(self) -> None:
        self.assertEqual(rpr.classify_tool("WebFetch", {"url": "x"}), "other")


class GatherAndBuildTests(unittest.TestCase):
    def _assistant(self, name: str, tool_input: dict) -> dict:
        return {"type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": name,
                                         "input": tool_input}]}}

    def test_gather_reads_tool_uses_and_marks_brokered(self) -> None:
        events = (self._assistant("Grep", {"pattern": "def x"}),
                  self._assistant("Edit", {"file_path": "a.py"}))
        uses = rpr.gather_tool_uses("edit", events, brokered_tools={"Edit"})
        self.assertEqual([u["tool_name"] for u in uses], ["Grep", "Edit"])
        self.assertFalse(uses[0]["brokered"])
        self.assertTrue(uses[1]["brokered"])
        self.assertEqual([u["classification"] for u in uses], ["native", "native"])

    def test_build_fixture_summarizes_shell_when_present(self) -> None:
        obs = rpr.RoutingObservation(
            assignment="discovery", max_turns=1,
            tool_uses=({"assignment": "discovery", "order": 1,
                        "tool_name": "Bash", "classification": "shell",
                        "input_excerpt": "dir", "brokered": True},),
            brokered_denials=(), assistant_events=1, returncode=1,
            timed_out=False, files_written=False, duration_seconds=1.0)
        fixture = rpr.build_fixture(
            executable="x", version_line="2.1.251 (Claude Code)",
            argv_shape=("<executable>", "-p"), observations=(obs,),
            provider_calls=1, measured=True)
        self.assertEqual(fixture["routing_summary"]["shell"], 1)
        self.assertEqual(fixture["routing_summary"]["verdict"], "shell_observed")

    def test_input_excerpts_are_redacted(self) -> None:
        excerpt = rpr._input_excerpt({"path": tempfile.gettempdir() + "/x"})
        self.assertIn("<tmp>", excerpt)
        self.assertNotIn(tempfile.gettempdir(), excerpt)


# --------------------------------------------------------------------------
# R295: the pre-dispatch routing drift tooth (three states, removal-sensitive)
# --------------------------------------------------------------------------


class DriftToothTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = pathlib.Path(self._tmp.name)

    def _write(self, version: str, *, measured: bool = True,
               schema: str = "shell_routing/v1", name: str | None = None) -> None:
        payload = {"schema": schema, "measured": measured,
                   "claude_version": version,
                   "routing_summary": {"verdict": "native_preferred"}}
        fname = name or f"shell_routing_{version}.json"
        (self.dir / fname).write_text(json.dumps(payload), encoding="utf-8")

    def test_current_evidence_for_the_pinned_identity_passes(self) -> None:
        self._write("2.1.251")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_version="2.1.251")
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["claude_version"], "2.1.251")
        self.assertEqual(result.evidence["routing_verdict"], "native_preferred")

    def test_no_evidence_at_all_refuses_fail_closed(self) -> None:
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_version="2.1.251")
        self.assertFalse(result.passes)
        self.assertTrue(result.known)  # a determined refusal, not undetermined
        self.assertEqual(result.reason_code, "routing_evidence_absent")

    def test_a_missing_directory_refuses_fail_closed(self) -> None:
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir / "gone"), installed_version="2.1.251")
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "routing_evidence_absent")

    def test_evidence_for_a_different_cli_identity_refuses(self) -> None:
        self._write("2.1.251")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_version="2.1.252")
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "routing_evidence_stale")
        self.assertEqual(result.evidence["evidence_identities"], ["2.1.251"])

    def test_matching_by_the_pinned_digest_identity_passes(self) -> None:
        (self.dir / "shell_routing_digestkeyed.json").write_text(json.dumps({
            "schema": "shell_routing/v1", "measured": True,
            "claude_version": "2.1.251", "cli_identity": "d6f6c29a" * 8,
            "routing_summary": {"verdict": "native_preferred"}}), encoding="utf-8")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_identity="d6f6c29a" * 8)
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["cli_identity"], "d6f6c29a" * 8)

    def test_a_mismatched_digest_identity_refuses(self) -> None:
        (self.dir / "shell_routing_digestkeyed.json").write_text(json.dumps({
            "schema": "shell_routing/v1", "measured": True,
            "claude_version": "2.1.251", "cli_identity": "a" * 64,
            "routing_summary": {"verdict": "native_preferred"}}), encoding="utf-8")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_identity="b" * 64)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "routing_evidence_stale")

    def test_an_undetermined_cli_version_fails_closed(self) -> None:
        self._write("2.1.251")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_version="")
        self.assertFalse(result.passes)
        self.assertFalse(result.known)
        self.assertEqual(result.reason_code, "cli_version_undetermined")

    def test_an_unmeasured_or_wrong_schema_fixture_is_not_evidence(self) -> None:
        self._write("2.1.251", measured=False, name="shell_routing_unmeasured.json")
        self._write("2.1.251", schema="other/v1", name="shell_routing_wrongschema.json")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_version="2.1.251")
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "routing_evidence_absent")

    def test_a_malformed_fixture_is_skipped_not_trusted(self) -> None:
        (self.dir / "shell_routing_broken.json").write_text(
            "{ not json", encoding="utf-8")
        self._write("2.1.251")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_version="2.1.251")
        # The valid fixture still matches; the broken one neither trusted nor fatal.
        self.assertTrue(result.passes)

    def test_the_version_runner_is_used_when_no_version_is_supplied(self) -> None:
        self._write("2.1.251")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), executable_path="claude",
            version_runner=lambda _p: "2.1.251 (Claude Code)".split()[0])
        self.assertTrue(result.passes)

    def test_the_committed_package_fixture_matches_the_installed_version(self) -> None:
        """The bundled fixture is current for 2.1.251 - the tooth is green now."""
        result = rp.probe_shell_routing_evidence(installed_version="2.1.251")
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["fixture"], FIXTURE_PATH.name)

    def test_the_committed_fixture_passes_for_the_real_claude_digest(self) -> None:
        """Instruction 5: the genuine-production path still passes - the committed
        fixture's cli_identity IS the real installed claude digest."""
        data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))
        real_digest = data["cli_identity"]
        result = rp.probe_shell_routing_evidence(installed_identity=real_digest)
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["cli_identity"], real_digest)


class JournalEvidenceTests(unittest.TestCase):
    """R295 journal-recorded routing evidence (the M0-T072 bound-manifest path
    fake-executable harnesses use)."""

    class FakeJournal:
        def __init__(self) -> None:
            self._state: dict = {}

        def get_state(self, key, default=None):
            return self._state.get(key, default)

        def set_state(self, key, value) -> None:
            self._state[key] = value

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.empty_dir = str(pathlib.Path(self._tmp.name))  # no package fixtures

    def test_recorded_journal_evidence_passes_the_tooth(self) -> None:
        journal = self.FakeJournal()
        rp.record_routing_evidence(journal, cli_identity="fake" * 16,
                                   claude_version="harness-fake")
        result = rp.probe_shell_routing_evidence(
            evidence_dir=self.empty_dir, installed_identity="fake" * 16,
            journal=journal)
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["routing_verdict"], "native_preferred")

    def test_no_journal_and_no_dir_evidence_refuses(self) -> None:
        result = rp.probe_shell_routing_evidence(
            evidence_dir=self.empty_dir, installed_identity="fake" * 16,
            journal=self.FakeJournal())
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "routing_evidence_absent")

    def test_journal_evidence_for_another_identity_is_stale(self) -> None:
        journal = self.FakeJournal()
        rp.record_routing_evidence(journal, cli_identity="a" * 64)
        result = rp.probe_shell_routing_evidence(
            evidence_dir=self.empty_dir, installed_identity="b" * 64,
            journal=journal)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "routing_evidence_stale")

    def test_record_routing_evidence_is_idempotent_per_identity(self) -> None:
        journal = self.FakeJournal()
        rp.record_routing_evidence(journal, cli_identity="a" * 64)
        rp.record_routing_evidence(journal, cli_identity="a" * 64)
        records = journal.get_state(rp.SHELL_ROUTING_EVIDENCE_KEY)
        self.assertEqual(len(records), 1)

    def test_record_routing_evidence_rejects_an_empty_identity(self) -> None:
        with self.assertRaises(Exception):
            rp.record_routing_evidence(self.FakeJournal(), cli_identity="")


# --------------------------------------------------------------------------
# R294: the native-tool preference block
# --------------------------------------------------------------------------


class NativeToolsGuidanceTests(unittest.TestCase):
    def test_the_prompt_file_exists_and_carries_the_sentinel(self) -> None:
        path = PACKAGE / "prompts" / "claude_native_tools.md"
        self.assertTrue(path.is_file())
        self.assertIn(cr.NATIVE_TOOLS_SENTINEL, path.read_text(encoding="utf-8"))

    def test_the_guidance_is_appended_exactly_once(self) -> None:
        prompt = cr.with_native_tools_guidance("Do one bounded thing.")
        self.assertEqual(prompt.count(cr.NATIVE_TOOLS_SENTINEL), 1)

    def test_the_append_is_idempotent(self) -> None:
        once = cr.with_native_tools_guidance("Do one bounded thing.")
        twice = cr.with_native_tools_guidance(once)
        self.assertEqual(twice.count(cr.NATIVE_TOOLS_SENTINEL), 1)
        self.assertEqual(once, twice)

    def test_the_guidance_names_the_validation_command_rule(self) -> None:
        self.assertIn("documented_test_commands", cr.NATIVE_TOOLS_GUIDANCE)
        for tool in ("Read", "Grep", "Glob", "Edit", "Write"):
            self.assertIn(tool, cr.NATIVE_TOOLS_GUIDANCE)

    def test_the_guidance_is_worker_text_clean(self) -> None:
        # No quota, percentage, countdown, or conserve-tokens pressure (R045).
        sc.assert_worker_text_clean("native_tools_guidance", cr.NATIVE_TOOLS_GUIDANCE)

    def test_a_prompt_already_carrying_the_block_is_not_duplicated(self) -> None:
        prompt = "Task.\n\n" + cr.NATIVE_TOOLS_GUIDANCE
        self.assertEqual(cr.with_native_tools_guidance(prompt), prompt)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
