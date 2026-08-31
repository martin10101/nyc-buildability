#!/usr/bin/env python3
"""Removal-sensitive tests for the command-document validation tooth.

M0-T126 (D-024-R372; M0-T125 defects D1/D14/D15/D17). R387 scenario 15
(command-document validation): every owner-presented supervisor command must
carry the complete required argument set and match the live parser/seam
contract. These tests prove the tooth FAILS when a pinned flag is removed (the
removal-sensitive property) and PASSES the living runbook.
"""
from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.agent_supervisor import command_docs as cd  # noqa: E402
from tools.agent_supervisor.cli import build_parser  # noqa: E402

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

_FULL_START = (
    "python -m tools.agent_supervisor start --mode supervised "
    "--checkout C:\\ctl --repo C:\\repo --branch task/x --worktree C:\\wt "
    "--max-cycles 1 --manifest m.json --config c.toml "
    "--model-selection ms.toml --claude-executable claude.exe "
    "--codex-executable codex.cmd --task-packet p.json")


class ExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()

    def test_extracts_bang_prefixed_supervisor_command(self) -> None:
        text = "Run this:\n!python -m tools.agent_supervisor status --checkout C:\\x\n"
        cmds = cd.extract_presented_commands(text, source="doc")
        self.assertEqual(len(cmds), 1)
        self.assertIn("status", cmds[0].raw)

    def test_extracts_fenced_powershell_with_backtick_continuation(self) -> None:
        text = ("```powershell\n"
                "python -m tools.agent_supervisor doctor `\n"
                "  --config c.toml\n"
                "```\n")
        cmds = cd.extract_presented_commands(text, source="doc")
        self.assertEqual(len(cmds), 1)
        self.assertIn("--config c.toml", cmds[0].raw)
        self.assertIn("doctor", cmds[0].raw)

    def test_ignores_non_supervisor_shell_lines_in_a_code_block(self) -> None:
        text = ("```powershell\n"
                "Set-Location C:\\x\n"
                "robocopy A B\\tools\\agent_supervisor /E\n"
                "$src = \"C:\\tools\\agent_supervisor\"\n"
                "```\n")
        self.assertEqual(cd.extract_presented_commands(text, source="doc"), [])

    def test_ignores_angle_bracket_template_commands(self) -> None:
        text = ("```\n"
                "python -m tools.agent_supervisor verify-controller "
                "--manifest <recorded manifest>\n```\n")
        self.assertEqual(cd.extract_presented_commands(text, source="doc"), [])

    def test_strips_trailing_comment(self) -> None:
        text = "!python -m tools.agent_supervisor status  # a note here\n"
        cmds = cd.extract_presented_commands(text, source="doc")
        verdict = cd.validate_command(cmds[0], self.parser)
        self.assertTrue(verdict.ok, verdict.message)
        self.assertEqual(verdict.verb, "status")

    def test_preserves_hash_inside_quoted_path(self) -> None:
        raw = 'python -m tools.agent_supervisor status --checkout "C:\\a#b"'
        cmd = cd.PresentedCommand(source="", line_number=1, raw=raw)
        verdict = cd.validate_command(cmd, self.parser)
        self.assertTrue(verdict.ok, verdict.message)


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()

    def _verdict(self, raw: str) -> cd.CommandVerdict:
        return cd.validate_command(
            cd.PresentedCommand(source="", line_number=1, raw=raw), self.parser)

    def test_full_start_command_passes(self) -> None:
        self.assertTrue(self._verdict(_FULL_START).ok, self._verdict(_FULL_START).message)

    def test_removing_worktree_fails_removal_sensitive(self) -> None:
        # The EXACT live defect: --worktree omitted while a packet declares one.
        stripped = _FULL_START.replace(" --worktree C:\\wt", "")
        verdict = self._verdict(stripped)
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "missing_pinned_flag")
        self.assertIn("--worktree", verdict.message)

    def test_removing_each_pinned_flag_fails(self) -> None:
        for flag, token in (("--checkout", "--checkout C:\\ctl "),
                            ("--repo", "--repo C:\\repo "),
                            ("--branch", "--branch task/x "),
                            ("--worktree", "--worktree C:\\wt "),
                            ("--max-cycles", "--max-cycles 1 ")):
            with self.subTest(flag=flag):
                stripped = _FULL_START.replace(token, "")
                verdict = self._verdict(stripped)
                self.assertFalse(verdict.ok, f"{flag} removal should fail")
                self.assertEqual(verdict.code, "missing_pinned_flag")
                self.assertIn(flag, verdict.message)

    def test_missing_dispatch_input_fails(self) -> None:
        stripped = _FULL_START.replace(" --manifest m.json", "")
        verdict = self._verdict(stripped)
        self.assertFalse(verdict.ok)
        # Missing --manifest is BOTH a dispatch input and not pinned; either code
        # is a failure. The register wants it caught; assert it is NOT ok.
        self.assertIn(verdict.code, {"missing_pinned_flag", "dispatch_inputs_missing"})

    def test_unknown_verb_fails(self) -> None:
        verdict = self._verdict("python -m tools.agent_supervisor frobnicate --x")
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "unknown_verb")

    def test_parser_rejects_bad_flag(self) -> None:
        verdict = self._verdict("python -m tools.agent_supervisor status --no-such-flag")
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "parser_rejected")

    def test_non_start_verb_passes_on_parse_alone(self) -> None:
        self.assertTrue(self._verdict(
            "python -m tools.agent_supervisor recovery-status --checkout C:\\x").ok)


class WorktreeBindingDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()

    def test_worktree_binding_refuses_primary_checkout(self) -> None:
        raw = _FULL_START.replace("--worktree C:\\wt", "--worktree C:\\ctl24")
        _verb, argv = cd.subcommand_tokens(raw, self.parser)
        namespace, err = cd._parse_quietly(self.parser, ["start", *argv])
        self.assertIsNotNone(namespace, err)
        verdict = cd.check_worktree_binding(
            namespace, packet_worktree="C:\\wt-m0t107",
            primary_checkout="C:\\ctl24")
        self.assertIsNotNone(verdict)
        self.assertEqual(verdict.code, "worktree_binding_refused")

    def test_worktree_binding_ok_when_matching(self) -> None:
        raw = _FULL_START.replace("--worktree C:\\wt", "--worktree C:\\wt-m0t107")
        _verb, argv = cd.subcommand_tokens(raw, self.parser)
        namespace, _ = cd._parse_quietly(self.parser, ["start", *argv])
        verdict = cd.check_worktree_binding(
            namespace, packet_worktree="C:\\wt-m0t107",
            primary_checkout="C:\\ctl24")
        self.assertIsNone(verdict)


class LivingRunbookTests(unittest.TestCase):
    """The living operator runbook must pass the tooth (D15 regeneration)."""

    def test_runbook_presented_commands_all_pass(self) -> None:
        parser = build_parser()
        runbook = _REPO_ROOT / "docs" / "CONTROLLER_UPDATE_RUNBOOK.md"
        verdicts = cd.validate_document(
            runbook.read_text(encoding="utf-8"), parser, source=str(runbook))
        self.assertTrue(verdicts, "the runbook should present supervisor commands")
        failures = [v for v in verdicts if not v.ok]
        self.assertEqual(
            failures, [],
            "runbook drift: " + "; ".join(
                f"{v.command.line_number} {v.code}: {v.message}" for v in failures))

    def test_runbook_has_a_pinned_start_command(self) -> None:
        parser = build_parser()
        runbook = _REPO_ROOT / "docs" / "CONTROLLER_UPDATE_RUNBOOK.md"
        verdicts = cd.validate_document(
            runbook.read_text(encoding="utf-8"), parser, source=str(runbook))
        starts = [v for v in verdicts if v.verb == "start"]
        self.assertTrue(starts, "the runbook must present at least one start command")
        for verdict in starts:
            self.assertTrue(verdict.ok, verdict.message)


if __name__ == "__main__":
    unittest.main()
