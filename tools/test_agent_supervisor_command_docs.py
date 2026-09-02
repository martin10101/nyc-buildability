#!/usr/bin/env python3
"""Removal-sensitive tests for the command-document validation tooth.

M0-T126 (D-024-R372; M0-T125 defects D1/D14/D15/D17). R387 scenario 15
(command-document validation): every owner-presented supervisor command must
carry the complete required argument set and match the live parser/seam
contract. These tests prove the tooth FAILS when a pinned flag is removed (the
removal-sensitive property) and PASSES the living runbooks.

M0-T136 C-B5 (D-024-R585, R589): the manifest-form ``start`` contract (the ONE
operator launch path, ``docs/MRL_LAUNCH_RUNBOOK.md``), the package-submodule
programs, the obsoleted CONTROLLER_UPDATE_RUNBOOK section 11 (it presents NO
start any more) and the owner-run canary package, each with paired negatives.
"""
from __future__ import annotations

import json
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

_MANIFEST_START = (
    "python -m tools.agent_supervisor start --mode supervised "
    "--checkout C:\\SupervisorController "
    "--launch-manifest C:\\SupervisorController\\mrl\\launch_manifest.json --max-cycles 1")

_DRAFT = ("python -m tools.agent_supervisor.mrl_launch_draft --worktree C:\\wt "
          "--task-packet C:\\p.json --mode supervised --base-ref refs/heads/main")

CANARY_ITEMS = (
    "clean-base manifest launch",
    "live repository mismatch refusal",
    "Claude/Codex child authentication",
    "runtime model/version identity",
    "updater disablement",
    "restricted tool denial",
    "one successful one-shot result",
    "bounded subagent fan-out and over-limit denial",
    "full process-tree cleanup",
    "bad-command raw exit-code preservation",
)


def _doc_verdicts(relative: str) -> list[cd.CommandVerdict]:
    path = _REPO_ROOT / relative
    return cd.validate_document(path.read_text(encoding="utf-8"), build_parser(), source=str(path))


def _failures(verdicts: list[cd.CommandVerdict]) -> str:
    return "; ".join(f"{v.command.line_number} {v.code}: {v.message}" for v in verdicts if not v.ok)


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

    def test_extracts_submodule_programs_in_both_spellings(self) -> None:
        text = ("```powershell\n"
                f"{_DRAFT}\n"
                "python tools\\agent_supervisor\\mrl_launch_draft.py --worktree C:\\wt --task-packet C:\\p.json\n"
                "```\n")
        cmds = cd.extract_presented_commands(text, source="doc")
        self.assertEqual(len(cmds), 2)

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


class ProgramDetectionTests(unittest.TestCase):
    def test_package_cli_spellings(self) -> None:
        for raw in ("python -m tools.agent_supervisor status --checkout C:\\x",
                    "python -m tools.agent_supervisor.cli status --checkout C:\\x",
                    "python tools/agent_supervisor/cli.py status --checkout C:\\x",
                    "python tools\\agent_supervisor\\__main__.py status --checkout C:\\x"):
            with self.subTest(raw=raw):
                program, argv = cd.program_of(raw)
                self.assertEqual(program, cd.CLI_PROGRAM)
                self.assertEqual(argv[0], "status")

    def test_submodule_spellings(self) -> None:
        for raw in (_DRAFT, "python C:\\ctl\\tools\\agent_supervisor\\mrl_launch_draft.py --worktree C:\\wt"):
            with self.subTest(raw=raw):
                program, argv = cd.program_of(raw)
                self.assertEqual(program, "mrl_launch_draft")
                self.assertEqual(argv[0], "--worktree")

    def test_alias_form_has_no_program(self) -> None:
        self.assertEqual(cd.program_of("supervisor status --checkout C:\\x"), ("", []))


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


class ManifestFormStartTests(unittest.TestCase):
    """The manifest-form start (C-B5): what the manifest cannot supply must be pinned."""

    def setUp(self) -> None:
        self.parser = build_parser()

    def _verdict(self, raw: str) -> cd.CommandVerdict:
        return cd.validate_command(
            cd.PresentedCommand(source="", line_number=1, raw=raw), self.parser)

    def test_manifest_form_passes_structurally_when_the_file_is_absent(self) -> None:
        verdict = self._verdict(_MANIFEST_START)
        self.assertTrue(verdict.ok, verdict.message)
        self.assertEqual(verdict.verb, "start")
        self.assertIn("not present on this host", verdict.message)

    def test_manifest_form_does_not_need_the_legacy_five_flags(self) -> None:
        for legacy in ("--repo", "--branch", "--worktree"):
            self.assertNotIn(legacy, _MANIFEST_START)
        self.assertTrue(self._verdict(_MANIFEST_START).ok)

    def test_removing_each_manifest_form_pin_fails(self) -> None:
        for flag, token in (("--checkout", " --checkout C:\\SupervisorController"),
                            ("--mode", " --mode supervised")):
            with self.subTest(flag=flag):
                verdict = self._verdict(_MANIFEST_START.replace(token, ""))
                self.assertFalse(verdict.ok)
                self.assertEqual(verdict.code, "missing_pinned_flag")
                self.assertIn(flag, verdict.message)

    def test_relative_or_env_manifest_path_fails(self) -> None:
        for path in ("mrl\\launch_manifest.json", "$env:LOCALAPPDATA\\x\\launch_manifest.json",
                     "./launch_manifest.json"):
            with self.subTest(path=path):
                raw = _MANIFEST_START.replace(
                    "C:\\SupervisorController\\mrl\\launch_manifest.json", path)
                verdict = self._verdict(raw)
                self.assertFalse(verdict.ok)
                self.assertEqual(verdict.code, "launch_manifest_not_absolute")

    def test_posix_absolute_manifest_path_is_absolute(self) -> None:
        raw = _MANIFEST_START.replace("C:\\SupervisorController\\mrl\\launch_manifest.json",
                                      "/srv/ctl/launch_manifest.json")
        self.assertTrue(self._verdict(raw).ok)

    def test_single_task_refusal_is_mirrored_offline(self) -> None:
        for extra in (" --max-tasks 2", " --packet-queue C:\\q.json", " --max-cycles 3"):
            with self.subTest(extra=extra):
                raw = _MANIFEST_START.replace(" --max-cycles 1", "") + extra
                verdict = self._verdict(raw)
                self.assertFalse(verdict.ok)
                self.assertEqual(verdict.code, "launch_manifest_single_task")

    def test_parser_drift_in_the_manifest_form_still_fails(self) -> None:
        verdict = self._verdict(_MANIFEST_START + " --no-such-flag")
        self.assertEqual(verdict.code, "parser_rejected")

    def test_absolute_path_predicate(self) -> None:
        self.assertTrue(cd.is_absolute_path("C:\\x\\y.json"))
        self.assertTrue(cd.is_absolute_path("/x/y.json"))
        self.assertFalse(cd.is_absolute_path("x\\y.json"))
        self.assertFalse(cd.is_absolute_path("$env:LOCALAPPDATA\\y.json"))
        self.assertFalse(cd.is_absolute_path(""))


class ManifestFormWithRealFileTests(unittest.TestCase):
    """When the named manifest EXISTS, the tooth applies it exactly as cmd_start does."""

    def setUp(self) -> None:
        import tempfile
        from tools.test_agent_supervisor_mrl_launch_manifest import build_world
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="cmd-docs-"))
        self.world = build_world(self.tmp)
        self.parser = build_parser()

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _raw(self, *, mode: str = "supervised", extra: str = "") -> str:
        return (f"python -m tools.agent_supervisor start --mode {mode} --checkout {self.tmp} "
                f"--launch-manifest {self.world['manifest_path']} --max-cycles 1{extra}")

    def _verdict(self, raw: str) -> cd.CommandVerdict:
        return cd.validate_command(cd.PresentedCommand(source="", line_number=1, raw=raw), self.parser)

    def _rewrite(self) -> None:
        self.world["manifest_path"].write_text(json.dumps(self.world["manifest"]), encoding="utf-8")

    def test_existing_manifest_applies_and_binds_every_dispatch_input(self) -> None:
        verdict = self._verdict(self._raw())
        self.assertTrue(verdict.ok, verdict.message)
        self.assertIn("applied cleanly", verdict.message)

    def test_mode_disagreeing_with_the_manifest_fails_like_preflight(self) -> None:
        verdict = self._verdict(self._raw(mode="shadow"))
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "launch_manifest_mismatch")

    def test_typed_flag_disagreeing_with_the_manifest_is_a_conflict(self) -> None:
        verdict = self._verdict(self._raw(extra=" --branch some/other"))
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "launch_manifest_conflict")

    def test_broken_manifest_is_invalid(self) -> None:
        self.world["manifest_path"].write_text("{not json", encoding="utf-8")
        verdict = self._verdict(self._raw())
        self.assertEqual(verdict.code, "launch_manifest_invalid")

    def test_unfilled_base_ref_is_refused(self) -> None:
        self.world["manifest"]["dispatch"]["base_ref"] = "<fill>"
        self._rewrite()
        verdict = self._verdict(self._raw())
        self.assertEqual(verdict.code, "launch_manifest_base_ref_missing")


class SubmoduleProgramTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()

    def _verdict(self, raw: str) -> cd.CommandVerdict:
        return cd.validate_command(cd.PresentedCommand(source="", line_number=1, raw=raw), self.parser)

    def test_registered_submodule_passes_on_its_own_parser(self) -> None:
        verdict = self._verdict(_DRAFT)
        self.assertTrue(verdict.ok, verdict.message)
        self.assertEqual(verdict.verb, "-m mrl_launch_draft")

    def test_registered_submodule_script_path_passes(self) -> None:
        verdict = self._verdict(
            "python tools\\agent_supervisor\\mrl_launch_draft.py --worktree C:\\wt --task-packet C:\\p.json")
        self.assertTrue(verdict.ok, verdict.message)

    def test_submodule_parser_drift_fails(self) -> None:
        verdict = self._verdict(_DRAFT + " --no-such-flag")
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "parser_rejected")

    def test_submodule_missing_required_argument_fails(self) -> None:
        verdict = self._verdict(_DRAFT.replace(" --task-packet C:\\p.json", ""))
        self.assertEqual(verdict.code, "parser_rejected")

    def test_unregistered_submodule_fails_closed(self) -> None:
        verdict = self._verdict("python -m tools.agent_supervisor.mrl_launch_manifest observe --worktree C:\\wt")
        self.assertFalse(verdict.ok)
        self.assertEqual(verdict.code, "unknown_program")

    def test_cli_module_spelling_still_validates_verbs(self) -> None:
        verdict = self._verdict("python -m tools.agent_supervisor.cli status --checkout C:\\x")
        self.assertTrue(verdict.ok, verdict.message)
        self.assertEqual(verdict.verb, "status")


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
    """The living operator docs must pass the tooth (D15 regeneration; C-B5 single launch path)."""

    MRL_RUNBOOK = "docs/MRL_LAUNCH_RUNBOOK.md"
    CONTROLLER_RUNBOOK = "docs/CONTROLLER_UPDATE_RUNBOOK.md"
    CANARY = "project-control/reports/M0-T136-canary-package.md"

    def test_mrl_runbook_presented_commands_all_pass(self) -> None:
        verdicts = _doc_verdicts(self.MRL_RUNBOOK)
        self.assertTrue(verdicts, "the MRL runbook should present supervisor commands")
        self.assertEqual([v for v in verdicts if not v.ok], [], "runbook drift: " + _failures(verdicts))

    def test_mrl_runbook_presents_exactly_one_manifest_form_start(self) -> None:
        starts = [v for v in _doc_verdicts(self.MRL_RUNBOOK) if v.verb == "start"]
        self.assertEqual(len(starts), 1, "exactly ONE operator launch path (R585): "
                         + "; ".join(v.command.raw for v in starts))
        self.assertTrue(starts[0].ok, starts[0].message)
        self.assertIn(cd.MANIFEST_FLAG, starts[0].command.raw)

    def test_mrl_runbook_presents_the_draft_program(self) -> None:
        drafts = [v for v in _doc_verdicts(self.MRL_RUNBOOK) if v.verb == "-m mrl_launch_draft"]
        self.assertEqual(len(drafts), 1)
        self.assertTrue(drafts[0].ok, drafts[0].message)

    def test_controller_runbook_presented_commands_all_pass(self) -> None:
        verdicts = _doc_verdicts(self.CONTROLLER_RUNBOOK)
        self.assertTrue(verdicts, "the controller runbook should still present supervisor commands")
        self.assertEqual([v for v in verdicts if not v.ok], [], "runbook drift: " + _failures(verdicts))

    def test_controller_runbook_presents_no_start_any_more(self) -> None:
        # Section 11's main-based start is OBSOLETED (C-B5): a second presented
        # launch path would be a second source of truth for one launch.
        starts = [v for v in _doc_verdicts(self.CONTROLLER_RUNBOOK) if v.verb == "start"]
        self.assertEqual(starts, [], "; ".join(v.command.raw for v in starts))
        text = (_REPO_ROOT / self.CONTROLLER_RUNBOOK).read_text(encoding="utf-8")
        self.assertIn("OBSOLETE", text)
        self.assertIn("docs/MRL_LAUNCH_RUNBOOK.md", text)

    def test_canary_package_presented_commands_all_pass_and_list_the_ten_items(self) -> None:
        verdicts = _doc_verdicts(self.CANARY)
        self.assertTrue(verdicts, "the canary package should present supervisor commands")
        self.assertEqual([v for v in verdicts if not v.ok], [], "canary drift: " + _failures(verdicts))
        starts = [v for v in verdicts if v.verb == "start"]
        self.assertTrue(starts)
        for verdict in starts:
            self.assertIn(cd.MANIFEST_FLAG, verdict.command.raw, verdict.command.raw)
        text = (_REPO_ROOT / self.CANARY).read_text(encoding="utf-8")
        for item in CANARY_ITEMS:
            self.assertIn(item, text, f"canary item missing: {item!r}")


if __name__ == "__main__":
    unittest.main()
