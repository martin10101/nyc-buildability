#!/usr/bin/env python3
"""M0-T094 (D-024 Phase F, unit G): the section-16.5 operator-channel matrix.

Scenario pack: project-control/reports/M0-T094-operator-channel.md section 1
(S1-S14). Requirements: R027/R034/R035/R036/R042 (start/status/controls),
R083-R089 (skills, interception, ask, bridge security), R094/R095 (durable
status, concise/verbose), R111 (this matrix, incl. metacharacter/Unicode
safety, timeout single-request, hook fail-closed), R125-R128/R087 (identity),
R045/R184 (no worker pollution), R149/R158/R159/R176 (feature detection,
thin skills, no /loop collision).

The owner-gated C1 live-interception canary (R088 zero-context measurement,
R089 idle/active measurement) is NOT here - S9/S11 assert the committed
detection fixture states those proofs honestly (measured-live OR
pending-owner-C1 with the documented second-terminal fallback), exactly as
R088 permits.

Supervisor-freeze qualifying evidence: D-024-R104 (Phase F).
"""
from __future__ import annotations

import contextlib
import inspect
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import operator_ask as oa  # noqa: E402
from tools.agent_supervisor import operator_channel_cli as occ  # noqa: E402
from tools.agent_supervisor import operator_status as ost  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.claude_runner import SESSION_KEY  # noqa: E402
from tools.agent_supervisor.config import (  # noqa: E402
    load_controller_config,
    load_model_selection,
)
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME,
    DurableJournal,
    runtime_dir_for,
)
from tools.agent_supervisor.process import ProcessResult  # noqa: E402
from tools.agent_supervisor.resume_scheduler import (  # noqa: E402
    LIMIT_RECORD_KEY,
)
from tools.agent_supervisor.stop_intent import (  # noqa: E402
    GRACEFUL_STOP_KEY,
    INTENT_EMERGENCY,
    StopIntents,
    effective_intent,
)
from tools.agent_supervisor.subagent_contracts import (  # noqa: E402
    assert_worker_text_clean,
)

HOOK = REPO / ".claude" / "hooks" / "loop_command_interceptor.py"
SKILLS_DIR = REPO / ".claude" / "skills"
DETECTION_FIXTURE = (REPO / "tools" / "agent_supervisor" / "fixtures" /
                     "loop_interception_detection_2_1_248.json")

SKILL_NAMES = ("loop-start", "loop-status", "loop-tasks", "loop-ask",
               "loop-pause", "loop-resume", "loop-stop",
               "loop-emergency-stop")

CONFIG_TOML = """
[codex]
allowed_models = ["codex-primary"]

[claude]
allowed_models = ["claude-worker"]

[controller]
default_mode = "shadow"
"""

SELECTION_TOML = """
[codex]
review_model = "codex-primary"
fallback_models = []

[claude]
model = "claude-worker"
fallback_models = []
"""

GOOD_ANSWER = {"schema_version": "1.0.0",
               "answer": "The campaign is at sequence 18; unit G is claimed.",
               "confidence_note": "read from the packet's campaign facts",
               "evidence_refs": ["state.campaign"]}


def campaign_record_dict(campaign_id: str = "D-024-fable-codex-loop") -> dict:
    return {
        "schema": "campaign_continuity/v1",
        "campaign_id": campaign_id,
        "directive_id": "D-024",
        "state": "active",
        "control_branch": "control/D-024-fable-codex-loop",
        "ledger_lineage_base": "0" * 12,
        "authority": "project-control/directives/D-024/source-001.md",
        "restrictions": ["never merge PR #241"],
        "next_action": {"task_id": "M0-T094", "description": "unit G"},
        "frozen": {"head_sha": "0" * 40,
                   "recorded_at": "2026-08-27T00:00:00+00:00"},
        "sequence": 18,
        "updated_at": "2026-08-27T00:00:00+00:00",
    }


def answering_runner(answer: dict | None = None, *, returncode: int = 0,
                     timed_out: bool = False, capture: list | None = None,
                     stdout: str = ""):
    """Fake process runner: writes the answer file like a real read-only
    Codex process would, or times out without writing anything."""
    def runner(argv, **kwargs):
        if capture is not None:
            capture.append((list(argv), dict(kwargs)))
        if not timed_out and answer is not None:
            out_path = argv[argv.index("--output-last-message") + 1]
            pathlib.Path(out_path).write_text(
                json.dumps(answer, ensure_ascii=False), encoding="utf-8")
        return ProcessResult(argv=tuple(argv), returncode=returncode,
                             stdout=stdout, stderr="", duration_seconds=0.01,
                             timed_out=timed_out, tree_terminated=timed_out)
    return runner


def run_hook(prompt_payload: dict | str, *, env_extra: dict | None = None,
             timeout: float = 30.0) -> tuple[int, str]:
    """Run the interception hook as the real subprocess Claude Code would."""
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = ""  # payload cwd decides identity in tests
    env.update(env_extra or {})
    raw = (prompt_payload if isinstance(prompt_payload, str)
           else json.dumps(prompt_payload))
    result = subprocess.run(  # noqa: S603 - argv array, our own script
        [sys.executable, str(HOOK)], input=raw, capture_output=True,
        text=True, encoding="utf-8", env=env, timeout=timeout)
    return result.returncode, result.stdout.strip()


class OperatorChannelBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.checkout = self.tmp / "checkout"
        (self.checkout / "tools").mkdir(parents=True)
        (self.checkout / "CLAUDE.md").write_text("# markers\n", encoding="utf-8")
        (self.checkout / "tools" / "project_control.py").write_text(
            "# marker\n", encoding="utf-8")
        campaigns = self.checkout / "project-control" / "campaigns"
        campaigns.mkdir(parents=True)
        (campaigns / "D-024-fable-codex-loop.json").write_text(
            json.dumps(campaign_record_dict(), indent=1), encoding="utf-8")
        self.runtime_base = self.tmp / "runtime"
        self.runtime = runtime_dir_for(self.checkout, base=self.runtime_base)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        config_path = self.tmp / "config.toml"
        config_path.write_text(CONFIG_TOML, encoding="utf-8")
        selection_path = self.tmp / "model_selection.toml"
        selection_path.write_text(SELECTION_TOML, encoding="utf-8")
        self.config = load_controller_config(config_path)
        self.selection = load_model_selection(selection_path)

    def journal(self) -> DurableJournal:
        return DurableJournal(self.runtime / DB_FILENAME).open()

    def ask_kwargs(self, journal, **overrides):
        kwargs = dict(journal=journal, audit=self.audit,
                      executable=sys.executable, checkout=self.checkout,
                      config=self.config, selection=self.selection,
                      window_seconds=30.0)
        kwargs.update(overrides)
        return kwargs

    def cli_run(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main([*argv, "--checkout", str(self.checkout),
                             "--runtime-base", str(self.runtime_base)])
        return code, out.getvalue(), err.getvalue()


# --------------------------------------------------------------------------
# S1 - canonical idempotent start; R035 alias
# --------------------------------------------------------------------------


class S1StartSurface(OperatorChannelBase):
    def test_start_takes_no_duration_and_is_unlimited_by_default(self) -> None:
        args = cli.build_parser().parse_args(["start"])
        self.assertIsNone(args.run_wall_clock_seconds)

    def test_the_owner_intent_alias_is_documented_verbatim(self) -> None:
        # R035: 'Start the agent loop' -> the canonical start command, in the
        # CLI's own documentation and the /loop-start skill.
        self.assertIn("Start the agent loop", cli.__doc__)
        self.assertIn("python -m tools.agent_supervisor start", cli.__doc__)
        skill = (SKILLS_DIR / "loop-start" / "SKILL.md").read_text(
            encoding="utf-8")
        self.assertIn("Start the agent loop", skill)

    def test_idempotency_rides_the_existing_lock_not_new_machinery(self) -> None:
        # R018 prove-first citation: cmd_start's single-instance behavior is
        # the accepted SingleInstanceLock; unit G added no parallel start.
        source = inspect.getsource(cli.cmd_start)
        self.assertIn("SingleInstanceLock", source)


# --------------------------------------------------------------------------
# S2 - the section-14 status set (R034/R042/R094/R095)
# --------------------------------------------------------------------------


class S2StatusSection14(OperatorChannelBase):
    REQUIRED_FACTS = (
        "campaign", "effective_stop_intent", "manual_pause", "graceful_stop",
        "emergency_stop", "controller_lease", "outage_retry", "outage_blocked",
        "bounded_idle", "claude_session", "model_override",
        "model_selection_digest", "current_task", "recent_transitions",
        "subagents", "usage_limit_record")

    def test_every_fact_is_present_and_labeled_on_a_fresh_journal(self) -> None:
        journal = self.journal()
        try:
            facts = ost.compose_status(journal, checkout=self.checkout)
        finally:
            journal.close()
        for key in self.REQUIRED_FACTS:
            self.assertIn(key, facts, key)
            entry = facts[key]
            self.assertIn("value", entry)
            self.assertIn("source", entry)
            self.assertIn("confidence", entry)

    def test_absent_facts_are_unknown_never_zero(self) -> None:
        journal = self.journal()
        try:
            facts = ost.compose_status(journal, checkout=self.checkout)
        finally:
            journal.close()
        usage = facts["usage_limit_record"]
        self.assertEqual(usage["value"], "unknown")
        self.assertEqual(usage["confidence"], "unknown")
        self.assertNotEqual(usage["value"], 0)
        self.assertEqual(facts["claude_session"]["value"], "unknown")

    def test_persisted_measurements_keep_their_own_confidence_label(self) -> None:
        journal = self.journal()
        try:
            journal.set_state(LIMIT_RECORD_KEY,
                              {"limit_hit": False, "confidence": "provider-exact"})
            journal.set_state(SESSION_KEY, {"run_id": "r1",
                                            "claude_session_id": "s1"})
            facts = ost.compose_status(journal, checkout=self.checkout)
        finally:
            journal.close()
        self.assertEqual(facts["usage_limit_record"]["confidence"],
                         "provider-exact")
        self.assertEqual(facts["claude_session"]["confidence"], "status-live")

    def test_the_campaign_record_is_read_and_summarized(self) -> None:
        journal = self.journal()
        try:
            facts = ost.compose_status(journal, checkout=self.checkout)
        finally:
            journal.close()
        campaign = facts["campaign"]
        self.assertEqual(campaign["confidence"], ost.CONFIDENCE_CAMPAIGN_RECORD)
        self.assertEqual(campaign["value"][0]["campaign_id"],
                         "D-024-fable-codex-loop")
        self.assertEqual(campaign["value"][0]["next_task_id"], "M0-T094")

    def test_cli_status_carries_section14_in_json_and_concise_text(self) -> None:
        code, out, _ = self.cli_run("status", "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertIn("section14", payload)
        self.assertIn("campaign", payload["section14"])
        code, out, _ = self.cli_run("status")
        self.assertEqual(code, 0)
        self.assertIn("stop intent:", out)
        self.assertIn("token health:", out)
        self.assertIn("unknown", out)          # honest absence, rendered
        self.assertNotIn("token health:      0", out)  # never coerced to zero

    def test_status_json_is_redacted_like_every_transmission(self) -> None:
        # Correction C1 (G3 MINOR-1 / G5 MINOR-1): a token-shaped string in
        # the durable graceful-stop reason must be masked on the --json path
        # exactly as on the concise path (built at runtime; never a literal).
        fake_pat = "ghp_" + "z9Y8" * 5
        code, _, _ = self.cli_run("graceful-stop", "--reason",
                                  f"rotate {fake_pat} then stop")
        self.assertEqual(code, 0)
        code, out, _ = self.cli_run("status", "--json")
        self.assertEqual(code, 0)
        self.assertNotIn(fake_pat, out)
        self.assertIn("REDACTED", out)


# --------------------------------------------------------------------------
# S3 - durable-before-ack controls; graceful-stop verb (R027/R036/R086)
# --------------------------------------------------------------------------


class S3DurableControls(OperatorChannelBase):
    def test_graceful_stop_is_durable_then_acknowledged_then_cleared(self) -> None:
        code, out, _ = self.cli_run("graceful-stop", "--reason", "owner asked")
        self.assertEqual(code, 0)
        self.assertIn("recorded durably BEFORE", out)
        journal = self.journal()
        try:
            intents = StopIntents.read(journal)
            record = journal.get_state(GRACEFUL_STOP_KEY)
        finally:
            journal.close()
        self.assertTrue(intents.graceful)
        self.assertEqual(intents.graceful_reason, "owner asked")
        self.assertEqual(record["clears_by"], "an explicit owner command only")
        code, out, _ = self.cli_run("graceful-stop", "--clear")
        self.assertEqual(code, 0)
        journal = self.journal()
        try:
            self.assertFalse(StopIntents.read(journal).graceful)
        finally:
            journal.close()

    def test_the_journal_write_precedes_the_acknowledgment_in_source(self) -> None:
        # R036/R086 ordering, pinned at source level for the NEW verb and the
        # existing ones it joins: the FIRST durable write precedes the FIRST
        # acknowledgment in every handler.
        for handler, write_call, ack_call in (
                (occ.cmd_graceful_stop, "set_graceful_stop", "emit_payload"),
                (cli.cmd_pause, "set_manual_pause", "_emit"),
                (cli.cmd_stop, "clear_emergency_stop", "_emit")):
            source = inspect.getsource(handler)
            self.assertLess(source.index(write_call),
                            source.index(ack_call), handler.__name__)

    def test_the_audit_filename_constants_cannot_drift(self) -> None:
        # cli.py keeps its own AUDIT_FILENAME (used by doctor/status paths);
        # the split module mirrors it. This pin turns silent drift into a
        # test failure.
        self.assertEqual(cli.AUDIT_FILENAME, occ.AUDIT_FILENAME)

    def test_emergency_outranks_graceful_and_both_stay_durable(self) -> None:
        intents = StopIntents(emergency=True, graceful=True, pause=True,
                              graceful_reason="landing")
        self.assertEqual(effective_intent(intents), INTENT_EMERGENCY)

    def test_the_stop_verbs_map_to_the_existing_surface(self) -> None:
        # R018 prove-first: pause/resume/stop/emergency-stop existed before
        # unit G; the parser exposes all of them plus the ONE new verb.
        parser = cli.build_parser()
        for verb in ("pause", "resume", "stop", "emergency-stop",
                     "graceful-stop", "ask"):
            args = parser.parse_args([verb] if verb != "ask" else ["ask", "q"])
            self.assertTrue(callable(args.func), verb)


# --------------------------------------------------------------------------
# S4 - ask: bounded synchronous window (R085/R104)
# --------------------------------------------------------------------------


class S4AskSynchronous(OperatorChannelBase):
    def test_a_question_gets_a_concise_bounded_answer(self) -> None:
        capture: list = []
        journal = self.journal()
        try:
            outcome = oa.run_ask(
                "What is the campaign state?",
                **self.ask_kwargs(journal,
                                  runner=answering_runner(GOOD_ANSWER,
                                                          capture=capture)))
        finally:
            journal.close()
        self.assertTrue(outcome.answered)
        self.assertIn("sequence 18", outcome.answer)
        self.assertEqual(outcome.model_used, "codex-primary")

    def test_the_invocation_is_the_read_only_reviewer_contract(self) -> None:
        capture: list = []
        journal = self.journal()
        try:
            oa.run_ask("Where are we?",
                       **self.ask_kwargs(journal,
                                         runner=answering_runner(
                                             GOOD_ANSWER, capture=capture)))
        finally:
            journal.close()
        argv, kwargs = capture[0]
        self.assertIn("--sandbox", argv)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        for flag in ("--ephemeral", "--ignore-user-config", "--strict-config"):
            self.assertIn(flag, argv)
        # The question travels on stdin inside the packet - never argv.
        self.assertNotIn("Where are we?", " ".join(argv))
        packet = json.loads(kwargs["input_text"])
        self.assertEqual(packet["question"], "Where are we?")
        self.assertEqual(packet["campaigns"][0]["campaign_id"],
                         "D-024-fable-codex-loop")
        self.assertIn("state", packet)

    def test_the_audit_trail_is_privacy_bounded(self) -> None:
        journal = self.journal()
        try:
            oa.run_ask("What secret plans exist for lot 42?",
                       **self.ask_kwargs(journal,
                                         runner=answering_runner(GOOD_ANSWER)))
        finally:
            journal.close()
        audit_text = (self.tmp / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn("operator_ask_answered", audit_text)
        self.assertIn("question_digest", audit_text)
        self.assertNotIn("lot 42", audit_text)   # digests, never raw text


# --------------------------------------------------------------------------
# S5 - ask: durable async fallback; timeout is single-request (R085/R087)
# --------------------------------------------------------------------------


class S5AskDurableFallback(OperatorChannelBase):
    def test_a_timeout_returns_one_durable_request_id(self) -> None:
        journal = self.journal()
        try:
            outcome = oa.run_ask(
                "Long question?",
                **self.ask_kwargs(journal,
                                  runner=answering_runner(timed_out=True),
                                  ask_id_factory=lambda: "oper_fixed01"))
            open_rows = journal.open_asks()
        finally:
            journal.close()
        self.assertFalse(outcome.answered)
        self.assertTrue(outcome.timed_out)
        self.assertTrue(outcome.tree_terminated)  # the tree was killed
        self.assertEqual(outcome.request_id, "oper_fixed01")
        self.assertEqual(len(open_rows), 1)
        self.assertEqual(open_rows[0].ask_id, "oper_fixed01")

    def test_resubmit_answers_the_same_row_never_a_duplicate(self) -> None:
        journal = self.journal()
        try:
            oa.run_ask("Q?", **self.ask_kwargs(
                journal, runner=answering_runner(timed_out=True),
                ask_id_factory=lambda: "oper_fixed01"))
            outcome = oa.resubmit_ask(
                "oper_fixed01",
                **self.ask_kwargs(journal,
                                  runner=answering_runner(GOOD_ANSWER)))
            self.assertTrue(outcome.answered)
            self.assertEqual(outcome.request_id, "oper_fixed01")
            self.assertEqual(journal.open_asks(), [])
            row = journal.ask_by_id("oper_fixed01")
            assert row is not None
            self.assertTrue(row.answered_at_utc)
            self.assertIn("sequence 18", row.answer)
            with self.assertRaises(oa.AskError) as ctx:
                oa.resubmit_ask("oper_fixed01",
                                **self.ask_kwargs(
                                    journal,
                                    runner=answering_runner(GOOD_ANSWER)))
            self.assertEqual(ctx.exception.code, "already_answered")
        finally:
            journal.close()

    def test_a_second_timeout_keeps_the_single_row(self) -> None:
        journal = self.journal()
        try:
            oa.run_ask("Q?", **self.ask_kwargs(
                journal, runner=answering_runner(timed_out=True),
                ask_id_factory=lambda: "oper_fixed01"))
            outcome = oa.resubmit_ask(
                "oper_fixed01",
                **self.ask_kwargs(journal,
                                  runner=answering_runner(timed_out=True)))
            self.assertTrue(outcome.timed_out)
            self.assertEqual(outcome.request_id, "oper_fixed01")
            self.assertEqual(len(journal.open_asks()), 1)  # still exactly one
        finally:
            journal.close()

    def test_cli_show_reads_the_durable_record(self) -> None:
        journal = self.journal()
        try:
            oa.run_ask("Q?", **self.ask_kwargs(
                journal, runner=answering_runner(timed_out=True),
                ask_id_factory=lambda: "oper_fixed01"))
        finally:
            journal.close()
        code, out, _ = self.cli_run("ask", "--show", "oper_fixed01")
        self.assertEqual(code, 0)
        self.assertIn("oper_fixed01", out)
        self.assertIn("open", out)
        code, _, err = self.cli_run("ask", "--show", "oper_missing")
        self.assertEqual(code, 13)  # stale_state: the fact is missing
        self.assertIn("unknown_request_id", err)


# --------------------------------------------------------------------------
# S6 - bridge security matrix (R087/R111)
# --------------------------------------------------------------------------


class S6BridgeSecurity(OperatorChannelBase):
    def test_empty_and_oversized_questions_are_typed_refusals(self) -> None:
        with self.assertRaises(oa.AskError) as ctx:
            oa.sanitize_question("   ")
        self.assertEqual(ctx.exception.code, "empty_question")
        with self.assertRaises(oa.AskError) as ctx:
            oa.sanitize_question("q" * (oa.MAX_QUESTION_CHARS + 1))
        self.assertEqual(ctx.exception.code, "question_too_large")
        with self.assertRaises(oa.AskError):
            oa.sanitize_question(12345)

    def test_metacharacters_quotes_multiline_unicode_are_data(self) -> None:
        hostile = "why does `rm -rf` & $(echo) | \"quoted\" '×' 東京\nline2?"
        cleaned, _ = oa.sanitize_question(hostile)
        for fragment in ("`rm -rf`", "$(echo)", '"quoted"', "東京", "line2?"):
            self.assertIn(fragment, cleaned)

    def test_terminal_escapes_are_stripped_both_directions(self) -> None:
        cleaned, count = oa.sanitize_question(
            "plain \x1b[31mred\x1b[0m \x1b]0;title\x07 \x07bell")
        self.assertNotIn("\x1b", cleaned)
        self.assertNotIn("\x07", cleaned)
        self.assertIn("red", cleaned)
        self.assertGreater(count, 0)
        shown = oa.bound_answer("answer \x1b[2Jwiped")
        self.assertNotIn("\x1b", shown)

    def test_secret_looking_strings_are_redacted(self) -> None:
        # Built at runtime so no secret-shaped literal is committed.
        fake_pat = "ghp_" + "a1B2" * 5
        cleaned, count = oa.sanitize_question(f"is {fake_pat} still valid?")
        self.assertNotIn(fake_pat, cleaned)
        self.assertIn("REDACTED", cleaned)
        self.assertGreater(count, 0)
        self.assertNotIn(fake_pat, oa.bound_answer(f"token {fake_pat} works"))

    def test_oversized_answers_are_truncated_with_a_visible_marker(self) -> None:
        shown = oa.bound_answer("a" * (oa.MAX_ANSWER_DISPLAY_CHARS * 2))
        self.assertLessEqual(len(shown), oa.MAX_ANSWER_DISPLAY_CHARS)
        self.assertTrue(shown.endswith("...[truncated]"))

    def test_identity_validation_refuses_foreign_roots(self) -> None:
        bare = self.tmp / "not_repo"
        bare.mkdir()
        with self.assertRaises(oa.AskError) as ctx:
            oa.validate_identity(bare)
        self.assertEqual(ctx.exception.code, "identity_mismatch")

    def test_a_tampered_campaign_record_refuses(self) -> None:
        record_path = (self.checkout / "project-control" / "campaigns" /
                       "D-024-fable-codex-loop.json")
        record_path.write_text('{"campaign_id": "x"}', encoding="utf-8")
        with self.assertRaises(oa.AskError) as ctx:
            oa.validate_identity(self.checkout)
        self.assertEqual(ctx.exception.code, "campaign_record_invalid")

    def test_the_packet_is_byte_bounded_and_fails_closed(self) -> None:
        journal = self.journal()
        try:
            big = {"recent_transitions": ost.fact(["x" * 60_000], "t")}
            with mock.patch.object(oa, "compose_status", return_value=big):
                packet = oa.build_ask_packet(journal, checkout=self.checkout,
                                             question="q", campaigns=[])
            self.assertEqual(packet["omitted_for_size"],
                             ["recent_transitions"])
            undroppable = {"blob": ost.fact("x" * 60_000, "t")}
            with mock.patch.object(oa, "compose_status",
                                   return_value=undroppable):
                with self.assertRaises(oa.AskError) as ctx:
                    oa.build_ask_packet(journal, checkout=self.checkout,
                                        question="q", campaigns=[])
            self.assertEqual(ctx.exception.code, "packet_too_large")
        finally:
            journal.close()

    def test_the_window_is_bounded(self) -> None:
        journal = self.journal()
        try:
            for bad in (0, -5, 3601):
                with self.assertRaises(oa.AskError) as ctx:
                    oa.run_ask("q?", **self.ask_kwargs(
                        journal, runner=answering_runner(GOOD_ANSWER),
                        window_seconds=bad))
                self.assertEqual(ctx.exception.code, "bad_window")
        finally:
            journal.close()

    def test_malformed_answers_are_typed_never_echoed(self) -> None:
        journal = self.journal()
        try:
            outcome = oa.run_ask(
                "q?", **self.ask_kwargs(
                    journal,
                    runner=answering_runner({"schema_version": "1.0.0",
                                             "answer": "",
                                             "confidence_note": "",
                                             "evidence_refs": []})))
        finally:
            journal.close()
        self.assertFalse(outcome.answered)
        self.assertEqual(outcome.error_code, "answer_empty")

    def test_ask_reuses_the_hardened_argv_builder(self) -> None:
        # R018: the read-only invocation contract is codex_reviewer.build_argv
        # (forbidden-flag refusal + assert_argv_safe), not a re-implementation.
        source = inspect.getsource(oa.run_ask)
        self.assertIn("build_argv", source)

    def test_cli_ask_refuses_missing_provider_inputs_by_name(self) -> None:
        code, _, err = self.cli_run("ask", "why?")
        self.assertEqual(code, 13)
        self.assertIn("ask_input_missing", err)
        self.assertIn("--codex-executable", err)


# --------------------------------------------------------------------------
# S7 - the 8 skills are thin and user-only (R083/R158/R159)
# --------------------------------------------------------------------------


class S7Skills(unittest.TestCase):
    def frontmatter(self, name: str) -> tuple[dict, str]:
        text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
        _, fm, body = text.split("---", 2)
        fields = {}
        for line in fm.strip().splitlines():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
        return fields, body

    def test_every_skill_exists_user_only_and_thin(self) -> None:
        for name in SKILL_NAMES:
            fields, body = self.frontmatter(name)
            self.assertEqual(fields["name"], name)
            self.assertEqual(fields["disable-model-invocation"], "true", name)
            self.assertTrue(fields.get("description"), name)
            # Thin: the body names the exact external CLI call, and is not an
            # ordinary conversational procedure.
            self.assertIn("tools.agent_supervisor", body, name)
            self.assertLess(len(body), 3_000, name)

    def test_no_collision_with_the_builtin_loop_and_no_btw(self) -> None:
        self.assertFalse((SKILLS_DIR / "loop").exists())
        for name in SKILL_NAMES:
            _, body = self.frontmatter(name)
            self.assertNotIn("/btw", body.replace("Never substitute `/btw`",
                                                  ""), name)

    def test_skills_document_the_interception_and_the_context_cost(self) -> None:
        for name in SKILL_NAMES:
            _, body = self.frontmatter(name)
            self.assertIn("loop_command_interceptor", body, name)
            self.assertIn("second", body.lower(), name)  # second-terminal path


# --------------------------------------------------------------------------
# S8 - feature-detected interception (R084/R088/R149)
# --------------------------------------------------------------------------


class S8FeatureDetection(unittest.TestCase):
    def record(self) -> dict:
        return json.loads(DETECTION_FIXTURE.read_text(encoding="utf-8"))

    def test_the_installed_version_fixture_selects_the_measured_path(self) -> None:
        record = self.record()
        self.assertEqual(record["selected_event"], "UserPromptSubmit")
        basis = record["selection_basis"]
        self.assertIn("measured-live", basis["UserPromptSubmit"]["payload"])
        self.assertIn("UNPROVEN",
                      basis["UserPromptExpansion"]["response_contract"])
        self.assertIn("2.1.248", record["claude_version"])

    def test_the_hook_consults_the_fixture_not_a_hardcoded_choice(self) -> None:
        source = HOOK.read_text(encoding="utf-8")
        self.assertIn("loop_interception_detection_", source)
        self.assertIn("_selected_event", source)

    def test_the_unproven_expansion_event_passes_through_unfaked(self) -> None:
        code, out = run_hook({"hook_event_name": "UserPromptExpansion",
                              "cwd": str(REPO), "prompt": "/loop-status"})
        self.assertEqual(code, 0)
        self.assertEqual(out, "")  # nothing faked, nothing injected (R088)

    def test_the_hook_is_registered_for_the_selected_event(self) -> None:
        settings = json.loads((REPO / ".claude" / "settings.json").read_text(
            encoding="utf-8"))
        commands = [hook["command"]
                    for entry in settings["hooks"]["UserPromptSubmit"]
                    for hook in entry["hooks"]]
        self.assertTrue(any("loop_command_interceptor" in c for c in commands))


# --------------------------------------------------------------------------
# S9 + S11 - zero-context proof and idle/active behavior: honest state (R088/R089)
# --------------------------------------------------------------------------


class S9S11HonestMeasurementState(unittest.TestCase):
    def test_zero_context_proof_is_measured_or_honestly_pending(self) -> None:
        record = json.loads(DETECTION_FIXTURE.read_text(encoding="utf-8"))
        proof = record["zero_context_proof"]
        self.assertIn(proof["status"], ("measured-live", "pending-owner-C1"))
        if proof["status"] == "pending-owner-C1":
            # R088's truthful fallback: the second-terminal CLI is advertised
            # and the measurement method is recorded for the C1 canary.
            self.assertIn("second-terminal", proof["note"])
            self.assertTrue(proof.get("measurement_method"))

    def test_queued_input_is_not_advertised_as_real_time(self) -> None:
        record = json.loads(DETECTION_FIXTURE.read_text(encoding="utf-8"))
        queued = record["queued_input_behavior"]
        self.assertIn(queued["status"], ("measured-live", "pending-owner-C1"))
        self.assertIn("NOT advertised as real-time", queued["note"])
        self.assertIn("second-terminal", queued["note"])


# --------------------------------------------------------------------------
# S10 - similar ordinary text is never intercepted (R084/R111)
# --------------------------------------------------------------------------


class S10ExactMatchOnly(unittest.TestCase):
    PASS_THROUGH = (
        "tell me about /loop-status",
        "loop-status",
        "/loop-statuses",
        "/Loop-Status",
        "what does /loop-pause do?",
        "run /loop-stop for me please",
        "/loopstatus",
        "/loop",
    )

    def test_similar_text_passes_through_untouched(self) -> None:
        for prompt in self.PASS_THROUGH:
            code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                                  "cwd": str(REPO), "prompt": prompt})
            self.assertEqual(code, 0, prompt)
            self.assertEqual(out, "", prompt)  # no output = no interception

    def test_the_exact_command_is_intercepted(self) -> None:
        code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                              "cwd": str(REPO), "prompt": "/loop-tasks"})
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("campaign", payload["reason"])


# --------------------------------------------------------------------------
# S12 - hook fail-closed (R087/R111)
# --------------------------------------------------------------------------


def _fake_supervisor_root(base: pathlib.Path, main_body: str) -> pathlib.Path:
    """A root that passes identity validation but whose supervisor module is
    controlled by the test (broken or slow)."""
    root = base / "fake_root"
    (root / "tools" / "agent_supervisor").mkdir(parents=True)
    (root / "CLAUDE.md").write_text("# marker\n", encoding="utf-8")
    (root / "tools" / "project_control.py").write_text("# marker\n",
                                                       encoding="utf-8")
    (root / "tools" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tools" / "agent_supervisor" / "__init__.py").write_text(
        "", encoding="utf-8")
    (root / "tools" / "agent_supervisor" / "cli.py").write_text(
        "# marker\n", encoding="utf-8")
    (root / "tools" / "agent_supervisor" / "__main__.py").write_text(
        textwrap.dedent(main_body), encoding="utf-8")
    return root


class S12HookFailClosed(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()

    def test_malformed_payloads_never_execute_or_block(self) -> None:
        for raw in ("not json", "[]", '{"prompt": 42}', ""):
            code, out = run_hook(raw)
            self.assertEqual(code, 0, raw)
            self.assertEqual(out, "", raw)

    def test_a_failing_supervisor_blocks_with_a_visible_reason(self) -> None:
        root = _fake_supervisor_root(self.tmp, """
            import sys
            print("supervisor exploded", file=sys.stderr)
            sys.exit(7)
        """)
        code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                              "cwd": str(root), "prompt": "/loop-pause"})
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("exit 7", payload["reason"])  # visible, not swallowed

    def test_loop_ask_without_provider_inputs_fails_closed_with_the_path(
            self) -> None:
        # No configured provider inputs -> the control is refused with the
        # exact second-terminal command; nothing is discovered from PATH.
        code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                              "cwd": str(REPO),
                              "prompt": "/loop-ask what is happening?"},
                             env_extra={"SUPERVISOR_CODEX_EXECUTABLE": "",
                                        "SUPERVISOR_CONFIG": "",
                                        "SUPERVISOR_MODEL_SELECTION": ""})
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("SUPERVISOR_CODEX_EXECUTABLE", payload["reason"])
        self.assertIn("python -m tools.agent_supervisor ask", payload["reason"])

    def test_loop_ask_question_rides_behind_an_end_of_options_separator(
            self) -> None:
        # Correction C3 (G5 ADVISORY-2): a dash-leading question is still the
        # question, never an option - proven behaviorally by echoing the argv
        # the hook actually built through a fake supervisor.
        root = _fake_supervisor_root(self.tmp, """
            import json, sys
            print(json.dumps(sys.argv[1:]))
        """)
        # The hook's display path imports bound_answer from the TARGET root;
        # give the fake root a pass-through stub so the echo survives (the
        # real bound_answer is behaviorally tested in S6).
        (root / "tools" / "agent_supervisor" / "operator_ask.py").write_text(
            "def bound_answer(text):\n    return text\n", encoding="utf-8")
        code, out = run_hook(
            {"hook_event_name": "UserPromptSubmit", "cwd": str(root),
             "prompt": "/loop-ask --show is this an option?"},
            env_extra={"SUPERVISOR_CODEX_EXECUTABLE": "fake-codex",
                       "SUPERVISOR_CONFIG": "fake-config.toml",
                       "SUPERVISOR_MODEL_SELECTION": "fake-selection.toml"})
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["decision"], "block")
        echoed = json.loads(payload["reason"].splitlines()[-1])
        separator = echoed.index("--")
        self.assertEqual(echoed[separator + 1], "--show is this an option?")
        self.assertEqual(echoed[0], "ask")

    def test_a_hung_supervisor_is_killed_and_reported(self) -> None:
        root = _fake_supervisor_root(self.tmp, """
            import time
            time.sleep(30)
        """)
        code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                              "cwd": str(root), "prompt": "/loop-status"},
                             env_extra={"LOOP_HOOK_TIMEOUT_S": "2"})
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("timed out", payload["reason"])
        self.assertIn("no background duplicate", payload["reason"])
        self.assertIn("second-terminal", payload["reason"])


# --------------------------------------------------------------------------
# S13 - no worker pollution (R045/R184)
# --------------------------------------------------------------------------


class S13NoWorkerPollution(OperatorChannelBase):
    def test_the_ask_packet_instruction_is_quota_clean(self) -> None:
        journal = self.journal()
        try:
            packet = oa.build_ask_packet(journal, checkout=self.checkout,
                                         question="q", campaigns=[])
        finally:
            journal.close()
        assert_worker_text_clean("ask_packet_instruction",
                                 packet["instruction"])

    def test_the_hook_never_injects_context_into_the_model(self) -> None:
        # A pass-through emits NOTHING (UserPromptSubmit stdout would become
        # model context); an interception emits ONLY decision+reason (the
        # blocked-prompt display channel, erased from context).
        source = HOOK.read_text(encoding="utf-8")
        self.assertNotIn("additionalContext", source)
        self.assertNotIn("hookSpecificOutput", source)
        code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                              "cwd": str(REPO), "prompt": "hello there"})
        self.assertEqual((code, out), (0, ""))
        _, out = run_hook({"hook_event_name": "UserPromptSubmit",
                           "cwd": str(REPO), "prompt": "/loop-tasks"})
        self.assertEqual(set(json.loads(out)), {"decision", "reason"})


# --------------------------------------------------------------------------
# S14 - Gate-0 / identity validation on the operator surface (R087/R125-R128)
# --------------------------------------------------------------------------


class S14Identity(OperatorChannelBase):
    def test_ask_refuses_outside_the_campaign_repository(self) -> None:
        foreign = self.tmp / "foreign"
        foreign.mkdir()
        journal = self.journal()
        try:
            with self.assertRaises(oa.AskError) as ctx:
                oa.run_ask("q?", **self.ask_kwargs(
                    journal, checkout=foreign,
                    runner=answering_runner(GOOD_ANSWER)))
        finally:
            journal.close()
        self.assertEqual(ctx.exception.code, "identity_mismatch")

    def test_the_hook_refuses_a_control_outside_the_repository(self) -> None:
        foreign = self.tmp / "foreign2"
        foreign.mkdir()
        code, out = run_hook({"hook_event_name": "UserPromptSubmit",
                              "cwd": str(foreign), "prompt": "/loop-pause"})
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("not the campaign repository root", payload["reason"])

    def test_cli_ask_maps_identity_refusal_to_the_unsafe_exit(self) -> None:
        foreign = self.tmp / "foreign3"
        foreign.mkdir()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["ask", "q?", "--checkout", str(foreign),
                             "--runtime-base", str(self.runtime_base),
                             "--codex-executable", sys.executable,
                             "--config", str(self.tmp / "config.toml"),
                             "--model-selection",
                             str(self.tmp / "model_selection.toml")])
        self.assertEqual(code, 11)  # refusals.UNSAFE
        self.assertIn("identity_mismatch", err.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
