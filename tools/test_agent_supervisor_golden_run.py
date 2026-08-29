#!/usr/bin/env python3
"""Golden-run pack: the D-024 Phase H integrated canaries (M0-T096, unit I).

Supervisor-freeze qualifying evidence: **D-024-R106**. The matrices are
D-024-R115 (16.9) and the R186 golden-run sequence; the Amendment-7 rows
R220-R227 govern evidence labeling. Every proof here is LANE-1
INJECTED/deterministic (R222/R223): fake provider executables, disposable git
checkouts, scratch runtimes, accelerated counters. No test contacts a
provider, waits for a natural Fable 5 event, or lifts the R187/R595 gates.

Prove-first (R018/R115): the `Section169RegisterTests` and
`GoldenSequenceRegisterTests` registers map EVERY 16.9 item and R186 step to
the file + named test that proves it. Items already proven by the existing
packs are CITED there, not re-implemented; only the genuine gaps get new
tests in this file (the staged pack's section 0 table).
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import campaign_continuity as cc  # noqa: E402
from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import golden_run as gr  # noqa: E402
from tools.agent_supervisor import live_observation as lo  # noqa: E402
from tools.agent_supervisor import refusal_bridge as rb  # noqa: E402
from tools.agent_supervisor import rotation as rot  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.circuit_breakers import (  # noqa: E402
    COUNTER_LIMITS, CircuitBreakers)
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME, DurableJournal, runtime_dir_for)
from tools.agent_supervisor.epoch_lease import (  # noqa: E402
    acquire_first, reconcile_on_boot, release, succeed)
from tools.agent_supervisor.recovery import set_manual_pause  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

TASK = "GOLD-001"
BRANCH = "task/GOLD-001-canary"


def _test_names_in(filename: str) -> set[str]:
    source = (HERE / filename).read_text(encoding="utf-8")
    return set(re.findall(r"def (test_\w+)", source))


def _git(checkout: pathlib.Path, *argv: str) -> str:
    out = subprocess.run(["git", *argv], cwd=str(checkout), check=True,
                         capture_output=True, text=True)
    return out.stdout.strip()


# --------------------------------------------------------------------------
# The golden run through the exact owner command (16.9(m), R121, R186, R222)
# --------------------------------------------------------------------------


class GoldenRunBase(unittest.TestCase):
    """Disposable checkout + scratch runtime + fake providers, driven ONLY
    through `cli.main` - the operator's command surface, nothing internal."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.checkout = self.tmp / "checkout"
        self.identity = gr.build_disposable_checkout(
            self.checkout, task_id=TASK, branch=BRANCH)
        self.files = gr.write_controller_files(self.tmp, cli.PACKAGE_ROOT)
        self.fakes = gr.materialize_fakes(self.tmp / "fakes")
        self.packet = gr.task_packet(self.tmp / f"{TASK}.json", task_id=TASK)
        self.runtime = self.tmp / "runtime"
        self.launch_log = self.tmp / "launch_log.jsonl"

    def plan(self, responses, **kwargs) -> None:
        gr.write_plan(pathlib.Path(self.fakes["plan"]), run_id="run-golden",
                      task_id=TASK, worktree=str(self.checkout),
                      branch=BRANCH, responses=responses,
                      launch_log=str(self.launch_log), **kwargs)

    def review_plan(self, prompts) -> None:
        gr.write_review_plan(pathlib.Path(self.fakes["review_plan"]), prompts)

    def argv(self, *, mode: str = "limited-auto", max_cycles: int = 2,
             enable: bool = True, extra=()) -> list[str]:
        return gr.start_argv(
            mode=mode, claude_executable=self.fakes["claude"],
            codex_executable=self.fakes["codex"],
            task_packet=str(self.packet), config=self.files["config"],
            model_selection=self.files["model_selection"],
            manifest=self.files["manifest"], checkout=str(self.checkout),
            runtime_base=str(self.runtime), branch=BRANCH,
            max_cycles=max_cycles, owner_enable_bounded_auto=enable,
            extra=extra)

    def run_cli(self, argv) -> tuple[int, dict]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(list(argv))
        return code, json.loads(stdout.getvalue())

    def journal(self) -> DurableJournal:
        runtime_dir = runtime_dir_for(self.checkout, base=str(self.runtime))
        journal = DurableJournal(runtime_dir / DB_FILENAME).open()
        self.addCleanup(journal.close)
        return journal

    def launches(self) -> list[dict]:
        return gr.read_launch_log(self.launch_log)

    def work_step(self, checkpoint_id: str, filename: str, *,
                  usage_total: int = 0) -> dict:
        return {"kind": "work", "checkpoint_id": checkpoint_id,
                "status": "UNIT_COMPLETE", "usage_total": usage_total,
                "git_commit": {"path": f"docs/{filename}",
                               "content": f"{gr.INJECTED_MARKER} {filename}",
                               "message": f"{gr.INJECTED_MARKER} {filename}"}}


class TwoUnitGoldenRunTests(GoldenRunBase):
    """16.9(m)/R121/R186/R222: two consecutive bounded units from ONE start."""

    def test_the_two_unit_golden_run_crosses_a_rotation_with_no_human_step(self) -> None:
        # Unit A crosses the context threshold; the seam rotates; the
        # successor answers READY; unit B completes. THREE launches, ONE
        # operator action (the exact start command), zero approvals typed.
        self.plan([
            self.work_step("cp-A", "unit-a.txt", usage_total=500_000),
            {"kind": "ready", "checkpoint_id": "cp-ready"},
            self.work_step("cp-B", "unit-b.txt"),
        ])
        self.review_plan([
            "INJECTED next bounded unit: confirm identity after rotation.",
            "INJECTED next bounded unit: implement unit B.",
            "INJECTED: campaign seam reached.",
        ])
        argv = self.argv(max_cycles=3,
                         extra=("--context-rotation-threshold", "100000"))
        code, payload = self.run_cli(argv)
        self.assertTrue(payload["dispatched"], payload)
        self.assertEqual(payload["stopped_because"], "max_cycles_reached")
        kinds = [entry["kind"] for entry in self.launches()]
        self.assertEqual(kinds, ["work", "ready", "work"])
        # The real low-risk repository effect (R118): both unit commits exist
        # on the non-protected task branch, each exactly once.
        log = _git(self.checkout, "log", "--oneline", BRANCH)
        self.assertEqual(log.count("unit-a.txt"), 1, log)
        self.assertEqual(log.count("unit-b.txt"), 1, log)
        self.assertEqual(_git(self.checkout, "branch", "--show-current"),
                         BRANCH)
        # One safe-seam rotation happened, via the standard path.
        journal = self.journal()
        self.assertIsNotNone(journal.get_state("last_rotation"))
        self.assertFalse(rot.rotation_pending(journal))
        # Exactly-once forwarding: no unsent rows, no pending effects.
        self.assertEqual(journal.unsent_outbound(), [])
        self.assertEqual(journal.pending_effects(), [])

    def test_the_golden_run_records_the_exact_owner_command_shape(self) -> None:
        # R121: the harness drives the SAME verb + flags handed to the owner.
        argv = self.argv(max_cycles=3)
        self.assertEqual(argv[0], "start")
        for required in ("--mode", "--claude-executable", "--codex-executable",
                         "--task-packet", "--config", "--model-selection",
                         "--manifest", "--checkout"):
            self.assertIn(required, argv)
        # No duration flag exists in the owner command (R027/R035).
        self.assertNotIn("--run-wall-clock-seconds", argv)

    def test_an_injected_controller_restart_continues_without_duplicate_work(self) -> None:
        # Invocation 1 completes unit A and dies (the controller "crash" is
        # the process ending with durable state behind it). Invocation 2 runs
        # the SAME command; recovery reconciles and unit B runs exactly once.
        self.plan([
            self.work_step("cp-A", "unit-a.txt"),
            self.work_step("cp-B", "unit-b.txt"),
        ])
        self.review_plan(["INJECTED next bounded unit: implement unit B."])
        code1, payload1 = self.run_cli(self.argv(max_cycles=1))
        self.assertTrue(payload1["dispatched"], payload1)
        code2, payload2 = self.run_cli(self.argv(max_cycles=2))
        self.assertTrue(payload2["dispatched"], payload2)
        kinds = [entry["kind"] for entry in self.launches()]
        self.assertEqual(kinds, ["work", "work"],
                         "unit A must never re-run after the restart")
        log = _git(self.checkout, "log", "--oneline", BRANCH)
        self.assertEqual(log.count("unit-a.txt"), 1, log)
        self.assertEqual(log.count("unit-b.txt"), 1, log)
        journal = self.journal()
        # No lost pending action and no duplicate: outbox fully drained.
        self.assertEqual(journal.unsent_outbound(), [])
        self.assertEqual(journal.pending_effects(), [])

    def test_a_second_start_while_the_lock_is_held_is_a_typed_refusal(self) -> None:
        # 16.9(i): behavioural idempotency of the one-command start. A SECOND
        # controller (a real live foreign process holding the lock) refuses;
        # same-process re-acquisition stays idempotent by design.
        from tools.agent_supervisor.durable_state import checkout_key
        from tools.agent_supervisor.locking import (
            LOCK_FILENAME, LockRecord, process_start_token)
        self.plan([self.work_step("cp-A", "unit-a.txt")])
        runtime_dir = runtime_dir_for(self.checkout, base=str(self.runtime))
        runtime_dir.mkdir(parents=True, exist_ok=True)
        holder = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(holder.kill)
        record = LockRecord(
            pid=holder.pid, start_token=process_start_token(holder.pid),
            checkout_key=checkout_key(self.checkout),
            controller_version=cli.CONTROLLER_VERSION,
            acquired_at_utc="2026-08-28T00:00:00.000Z", lock_id="lock-foreign")
        (runtime_dir / LOCK_FILENAME).write_text(
            json.dumps(record.to_dict()), encoding="utf-8")
        code, payload = self.run_cli(self.argv(max_cycles=1))
        self.assertNotEqual(code, 0)
        self.assertFalse(payload["dispatched"])
        recovery = payload["recovery"]
        self.assertEqual(recovery["classification"], "UNSAFE_OR_DRIFTED")
        self.assertIn("single-instance lock", recovery["reason"])
        self.assertIn(str(holder.pid), recovery["reason"],
                      "the report NAMES the live owner instead of duplicating")
        self.assertEqual(self.launches(), [],
                         "a refused second start must dispatch nothing")

    def test_an_ambiguous_effect_blocks_the_restart_from_dispatching(self) -> None:
        # GR-8: a crash window left a begun-but-unconfirmed external effect;
        # the SAME start command must reconcile/refuse, never re-dispatch on
        # a guess and never re-fire the effect.
        self.plan([self.work_step("cp-A", "unit-a.txt"),
                   self.work_step("cp-B", "unit-b.txt")])
        self.review_plan(["INJECTED next bounded unit: implement unit B."])
        code1, payload1 = self.run_cli(self.argv(max_cycles=1))
        self.assertTrue(payload1["dispatched"])
        journal = self.journal()
        journal.record_before_effect(
            action_id="eff_golden_ambiguous", effect_type="push",
            target=f"origin/{BRANCH}", expected_prior_state="clean",
            request_digest="d" * 64)
        code2, payload2 = self.run_cli(self.argv(max_cycles=2))
        self.assertFalse(payload2["dispatched"],
                         "an ambiguous pending effect must block dispatch")
        self.assertEqual(
            [entry["kind"] for entry in self.launches()], ["work"],
            "no producer may launch over an unreconciled effect")
        pending = journal.pending_effects()
        self.assertEqual(len(pending), 1, "the effect was never re-fired")


class InjectedFaultTests(GoldenRunBase):
    """GR-5/GR-6: injected refusal + quota exhaustion through the REAL CLI."""

    def test_an_injected_refusal_records_intent_and_holds(self) -> None:
        self.plan([{"kind": "refusal"}])
        code, payload = self.run_cli(self.argv(mode="shadow", enable=False,
                                               max_cycles=1))
        self.assertEqual(payload.get("stopped_because"),
                         rb.REASON_REFUSAL_RECORDED, payload)
        journal = self.journal()
        digest = journal.get_state(rb.LAST_REFUSAL_KEY)
        self.assertTrue(digest, "the R070 refusal record must exist")
        record = journal.get_state(f"{rb.REFUSAL_RECORD_KEY_PREFIX}{digest}")
        self.assertEqual(record["kind"], "guardrail_refusal")
        self.assertFalse(record["shape_verified_live"],
                         "no live shape exists on this build (R224)")
        self.assertIn(gr.INJECTED_MARKER, record["evidence_excerpt"],
                      "harness-born evidence labels itself (R223)")

    def test_the_refusal_seam_is_reachable_from_the_production_start_path(self) -> None:
        # W-7: the discovered integration defect - before this unit `start`
        # never constructed the H1 bridge, so no real run could record a
        # refusal. The wiring is proven by the CLI run above reaching the
        # journal record; here the wiring itself is pinned so a regression
        # (dropping the argument) fails the build.
        source = (REPO / "tools" / "agent_supervisor" / "cli.py").read_text(
            encoding="utf-8")
        self.assertIn("guardrail_bridge=guardrail_bridge", source)
        self.assertIn("GuardrailBridgeIntegration(", source)

    def test_an_injected_refusal_cannot_actuate_the_bridge(self) -> None:
        # GR-5 tail: both halves of the double gate refuse (R228 fail-safe).
        with self.assertRaises(rb.BridgeError) as raised:
            rb.assert_actuation_permitted(shape_verified_live=False,
                                          owner_authorized=True)
        self.assertEqual(raised.exception.code,
                         "actuation_requires_measured_live_shape")
        with self.assertRaises(rb.BridgeError) as raised:
            rb.assert_actuation_permitted(shape_verified_live=True,
                                          owner_authorized=False)
        self.assertEqual(raised.exception.code,
                         "actuation_requires_owner_authorization")

    def test_an_injected_quota_exhaustion_is_detect_and_hold(self) -> None:
        self.plan([{"kind": "exhaustion"}])
        code, payload = self.run_cli(self.argv(mode="shadow", enable=False,
                                               max_cycles=1))
        stopped = payload.get("stopped_because", "")
        self.assertIn("fable_exhaustion", stopped, payload)
        self.assertEqual(
            [entry["kind"] for entry in self.launches()], ["exhaustion"],
            "exactly one unit launched; nothing redispatched after the hold")
        journal = self.journal()
        last = journal.last_transition()
        self.assertEqual(last.state_to, sm.PAUSED_RECOVERY)

    def test_status_answers_read_only_while_the_producer_is_running(self) -> None:
        # 16.9(f): the operator status surface answers from durable state
        # while the machine is mid-unit, mutating nothing.
        from tools.agent_supervisor.operator_status import compose_status
        journal = self.journal()
        audit = AuditLog(
            runtime_dir_for(self.checkout, base=str(self.runtime))
            / "audit.jsonl", fsync=False)
        machine = StateMachine(journal, audit, "run-status")
        machine.transition(sm.PREFLIGHT, "start_command")
        machine.transition(sm.START_CLAUDE, "preflight_pass")
        machine.transition(sm.CLAUDE_RUNNING, "claude_process_started")
        before = dict(journal.all_state())
        facts = compose_status(journal, checkout=self.checkout)
        self.assertIsInstance(facts, dict)
        self.assertEqual(dict(journal.all_state()), before,
                         "status must not mutate the journal")
        self.assertEqual(machine.current_state, sm.CLAUDE_RUNNING,
                         "the running unit was not touched")


# --------------------------------------------------------------------------
# The Amendment-7 passive watcher + pending_live_observation register
# (R223/R224/R225/R226/R227/R228)
# --------------------------------------------------------------------------


class WatcherBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.journal = DurableJournal(self.tmp / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)

    def refusal_record(self, digest: str = "abc123", *,
                       excerpt: str = "typed refusal captured") -> None:
        self.journal.set_state(
            f"{rb.REFUSAL_RECORD_KEY_PREFIX}{digest}",
            {"kind": "guardrail_refusal", "request_digest": digest,
             "condition": "recognized_guardrail_refusal",
             "matched_shape": "structured_stop_reason_refusal",
             "shape_verified_live": False, "reason": "recognized",
             "evidence_excerpt": excerpt, "at_utc": "2026-08-28T00:00:00Z"})


class WatcherPassivityTests(WatcherBase):
    """W-1: the watcher reads existing records and can only write its OWN keys."""

    def test_the_watcher_module_is_structurally_passive(self) -> None:
        source = (REPO / "tools" / "agent_supervisor"
                  / "live_observation.py").read_text(encoding="utf-8")
        for forbidden in ("import subprocess", "Popen(", "os.system",
                          "additionalContext", "hookSpecificOutput",
                          "input("):
            self.assertNotIn(forbidden, source,
                             f"the watcher must never use {forbidden!r}")

    def test_the_watcher_writes_only_its_own_register_keys(self) -> None:
        self.refusal_record()
        before = set(self.journal.all_state())
        lo.record_observations(self.journal, session_provenance="injected")
        added = set(self.journal.all_state()) - before
        own = (lo.OBSERVATION_KEY_PREFIX,)
        for key in added:
            self.assertTrue(
                key.startswith(own)
                or key in (lo.REGISTER_KEY, lo.LAST_OBSERVATION_KEY),
                f"the watcher wrote a foreign key {key!r}")

    def test_a_scan_of_an_empty_journal_reports_unknown_never_zero_verified(self) -> None:
        report = lo.record_observations(self.journal,
                                        session_provenance="injected")
        self.assertEqual(report["rows_written"], 0)
        status = lo.register_status(self.journal)
        self.assertEqual(status["natural_event_observed"]["value"], "unknown")


class WatcherCaptureTests(WatcherBase):
    """W-2/W-6: idempotent CAS capture of the five R226 fields, sanitized."""

    def test_the_source_record_key_is_sanitized_not_raw(self) -> None:
        """M0-T114 residual 2 (unit-I G-report one-liner, pinned at accept):
        the register row wrote the RAW source_record_key although its
        sanitized value was already computed - a key-shaped token embedded in
        a source record key must never reach the register."""
        secret = "sk-ant-api03-FAKEFAKEFAKEFAKE1234567890abcdefg"
        self.refusal_record(f"d-{secret}")
        lo.record_observations(self.journal, session_provenance="injected")
        rows = lo.observation_rows(self.journal)
        self.assertEqual(len(rows), 1)
        key_value = rows[0]["source_record_key"]
        self.assertNotIn(secret, key_value,
                         msg="the raw key-shaped token leaked into the register")
        self.assertIn("[REDACTED", key_value)

    R226_FIELDS = ("observed_event_type", "installed_version_shape",
                   "classification_decision", "selected_response",
                   "sanitized_outcome")

    def test_capture_is_idempotent_and_carries_the_five_fields(self) -> None:
        # One source per DISCOVERY BRANCH (G4 MINOR-1): refusal, usage-limit
        # quota, provider-abort availability, outage availability, model-change
        # turnover, and a worker-turnover transition - so a broken or renamed
        # source key can never silently un-capture an event kind.
        from tools.agent_supervisor.outage_policy import RETRY_KEY
        from tools.agent_supervisor.worker_turnover import (
            REASON_TURNOVER_RECORDED)
        self.refusal_record("d1")
        self.journal.set_state("usage_limit_record",
                              {"limit_class": "weekly", "recorded_at_utc": "t",
                               "raw_notice": "limit reached"})
        self.journal.set_state(rot.PROVIDER_ABORT_KEY,
                              {"unit_id": "u1", "recorded_at_utc": "t",
                               "reason_code": "provider_enforced_abort"})
        self.journal.set_state(RETRY_KEY,
                              {"cause": "network", "reason": "timeout",
                               "attempt": 1, "recorded_at_utc": "t"})
        self.journal.set_state("model_change_audit",
                              [{"change": "claude-fable-5->claude-opus-4-8",
                                "at_utc": "t"}])
        self.journal.record_transition(
            state_from="CLAUDE_RUNNING", state_to="PAUSED_RECOVERY",
            trigger="unsafe_condition", run_id="run-w2",
            detail={"reason": REASON_TURNOVER_RECORDED, "cycle": 1,
                    "turnover": {"reason_code": REASON_TURNOVER_RECORDED}})
        first = lo.record_observations(self.journal,
                                       session_provenance="injected")
        self.assertEqual(first["rows_written"], 6)
        again = lo.record_observations(self.journal,
                                       session_provenance="injected")
        self.assertEqual(again["rows_written"], 0,
                         "a re-scan must be a counted no-op (CAS)")
        rows = lo.observation_rows(self.journal)
        for row in rows:
            for field in self.R226_FIELDS:
                self.assertIn(field, row)
            self.assertIn(row["observed_event_type"], lo.EVENT_TYPES)
        self.assertEqual({row["observed_event_type"] for row in rows},
                         set(lo.EVENT_TYPES),
                         "every event kind in the closed vocabulary is "
                         "captured through its own discovery branch")

    def test_register_rows_are_sanitized_at_the_boundary(self) -> None:
        secret = "api_key=sk-" + "a" * 40
        self.refusal_record("d2", excerpt=secret + " " + ("x" * 5000))
        lo.record_observations(self.journal, session_provenance="injected")
        row = lo.observation_rows(self.journal)[0]
        dumped = json.dumps(row)
        self.assertNotIn(secret, dumped, "secrets never reach the register")
        self.assertGreaterEqual(row["redaction_count"], 1)

    def test_bad_provenance_is_refused_never_guessed(self) -> None:
        with self.assertRaises(lo.ObservationError):
            lo.record_observations(self.journal, session_provenance="real")


class WatcherLabelingTests(WatcherBase):
    """W-3/W-4: injected can never read as live; nothing verifies live."""

    def test_the_evidence_vocabulary_has_no_live_value(self) -> None:
        self.assertEqual(set(lo.EVIDENCE_CLASSES),
                         {"injected", "live_candidate"})

    def test_injected_session_provenance_labels_injected(self) -> None:
        self.refusal_record("d3")
        lo.record_observations(self.journal, session_provenance="injected")
        row = lo.observation_rows(self.journal)[0]
        self.assertEqual(row["evidence_class"], lo.EVIDENCE_INJECTED)
        self.assertFalse(row["verified_live"])

    def test_the_harness_marker_wins_over_a_live_session_scan(self) -> None:
        self.refusal_record(
            "d4", excerpt=f"{gr.INJECTED_MARKER} typed refusal")
        lo.record_observations(self.journal, session_provenance="live")
        row = lo.observation_rows(self.journal)[0]
        self.assertEqual(row["evidence_class"], lo.EVIDENCE_INJECTED,
                         "fixture-born evidence NEVER reads as live (R223)")

    def test_a_clean_live_scan_yields_only_a_candidate(self) -> None:
        self.refusal_record("d5", excerpt="a natural refusal excerpt")
        lo.record_observations(self.journal, session_provenance="live")
        row = lo.observation_rows(self.journal)[0]
        self.assertEqual(row["evidence_class"], lo.EVIDENCE_LIVE_CANDIDATE)
        self.assertFalse(row["verified_live"],
                         "observation is never verification (R224)")

    def test_no_code_path_writes_verified_live_true(self) -> None:
        source = (REPO / "tools" / "agent_supervisor"
                  / "live_observation.py").read_text(encoding="utf-8")
        self.assertIn('"verified_live": False', source)
        self.assertNotRegex(source, r'"verified_live":\s*True')
        self.assertNotRegex(source, r"verified_live\s*=\s*True")

    def test_comparison_refuses_wrong_sides_and_mutates_nothing(self) -> None:
        self.refusal_record("d6", excerpt="natural")
        lo.record_observations(self.journal, session_provenance="live")
        live_row = lo.observation_rows(self.journal)[0]
        injected_row = dict(live_row, evidence_class=lo.EVIDENCE_INJECTED)
        before = dict(self.journal.all_state())
        comparison = lo.compare_with_injected_proof(live_row, injected_row)
        self.assertTrue(comparison["all_match"])
        self.assertIn("NOT performed by this module",
                      comparison["graduation"])
        self.assertEqual(dict(self.journal.all_state()), before)
        with self.assertRaises(lo.ObservationError):
            lo.compare_with_injected_proof(injected_row, injected_row)
        with self.assertRaises(lo.ObservationError):
            lo.compare_with_injected_proof(live_row, live_row)

    def test_a_pre_graduation_natural_event_holds_fail_closed(self) -> None:
        # W-5 (R227/R228): a natural event before graduation captures a
        # candidate row, gates nothing open, and the bridge still refuses.
        self.refusal_record("d7", excerpt="a natural refusal")
        lo.record_observations(self.journal, session_provenance="live")
        readiness = lo.graduation_readiness(self.journal)
        self.assertIn("not_ready", readiness["bridge_actuation"]["value"])
        self.assertIn("not_gated", readiness["general_loop"]["value"])
        with self.assertRaises(rb.BridgeError):
            rb.assert_actuation_permitted(shape_verified_live=False,
                                          owner_authorized=False)
        register = self.journal.get_state(lo.REGISTER_KEY)
        self.assertEqual(register["status"], "pending_live_observation")
        self.assertEqual(len(register["awaited"]), 3)


class WatcherStartEpilogueTests(GoldenRunBase):
    """R226 wiring: a real `start` session's epilogue notices the events."""

    def test_the_start_epilogue_scans_and_labels_harness_events_injected(self) -> None:
        self.plan([{"kind": "refusal"}])
        self.run_cli(self.argv(mode="shadow", enable=False, max_cycles=1))
        journal = self.journal()
        rows = lo.observation_rows(journal)
        self.assertTrue(rows, "the start epilogue must have scanned (R226)")
        refusal_rows = [r for r in rows
                        if r["observed_event_type"] == "guardrail_refusal"]
        self.assertEqual(len(refusal_rows), 1)
        self.assertEqual(refusal_rows[0]["evidence_class"],
                         lo.EVIDENCE_INJECTED,
                         "the harness marker labels the row injected even "
                         "though the session scan runs as live (R223)")


# --------------------------------------------------------------------------
# Composition gaps: 16.9 (a), (e), (g), (h) + R186 steps 2/12
# --------------------------------------------------------------------------


class EpochRotationCompositionTests(WatcherBase):
    """16.9(a): multiple renewable epochs, each ended by a FORCED rotation."""

    def test_three_epochs_each_end_through_a_forced_rotation(self) -> None:
        journal = self.journal
        now = 1_770_000_000.0
        lease = acquire_first(journal, campaign_id="D-024",
                              owner_run_id="run-e1", now=now,
                              ttl_seconds=3600)
        self.assertEqual(lease.epoch, 1)
        for epoch, (owner, successor) in enumerate(
                [("run-e1", "run-e2"), ("run-e2", "run-e3")], start=1):
            rot.observe_mid_unit(journal, reason_code="owner_request",
                                 detail=f"forced rotation ending epoch {epoch}")
            self.assertTrue(rot.rotation_pending(journal))
            rot.clear_rotation_pending(journal)
            release(journal, owner_run_id=owner)
            lease = succeed(journal, expected_epoch=epoch,
                            new_owner_run_id=successor, now=now + epoch,
                            ttl_seconds=3600)
            self.assertEqual(lease.epoch, epoch + 1)
        outcome = reconcile_on_boot(journal, run_id="run-e3", now=now + 10)
        self.assertIn("OWN_LEASE_LIVE", str(outcome.status).upper())
        from tools.agent_supervisor.epoch_lease import SUCCESSION_LOG_KEY
        log = journal.get_state(SUCCESSION_LOG_KEY, [])
        self.assertEqual(len(log), 2, "two successions, exactly once each")


class ExtendedPauseTests(WatcherBase):
    """16.9(e): an arbitrarily long durable pause changes NOTHING but the flag."""

    def test_an_extended_pause_survives_restart_and_resumes_cleanly(self) -> None:
        journal = self.journal
        journal.set_state("campaign_fact", {"unit": "A", "sha": "c" * 40})
        set_manual_pause(journal, paused=True, reason="owner extended hold")
        before = dict(journal.all_state())
        # The "restart after days away": close and reopen the same file. A
        # pause has no decay path, so elapsed wall-clock CANNOT change state.
        db = self.tmp / "journal.sqlite3"
        journal.close()
        reopened = DurableJournal(db).open()
        self.addCleanup(reopened.close)
        self.journal = reopened
        self.assertEqual(dict(reopened.all_state()), before,
                         "nothing decays while paused")
        from tools.agent_supervisor.recovery import MANUAL_PAUSE_KEY
        self.assertTrue(reopened.get_state(MANUAL_PAUSE_KEY),
                        "the durable pause flag survived the restart")
        set_manual_pause(reopened, paused=False, reason="owner resume")
        self.assertEqual(reopened.get_state("campaign_fact"),
                         {"unit": "A", "sha": "c" * 40},
                         "work state is intact after the resume")


class AcceleratedOvernightTests(unittest.TestCase):
    """16.9(g): an accelerated multi-day campaign with a mid-campaign restart."""

    def test_an_accelerated_overnight_campaign_survives_a_mid_campaign_restart(self) -> None:
        import tools.test_agent_supervisor_bounded_mode as bm
        import tools.test_agent_supervisor_loop as lpk
        from tools.agent_supervisor import loop as lp
        from tools.agent_supervisor import policy as pol
        from tools.agent_supervisor import run_budget as budget_mod
        from tools.agent_supervisor.config import Limits

        tmp = pathlib.Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(lambda: None)
        db = tmp / "journal.sqlite3"
        clock = bm.FakeClock()
        journal = DurableJournal(db).open()
        audit = AuditLog(tmp / "audit.jsonl", fsync=False)
        authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T036", "allowed_paths": ["tools/**"],
             "forbidden_paths": [".github/**"], "status": "in_progress"},
            repo_root=str(tmp), worktree=str(tmp),
            branch="task/M0-T036-supervisor-bridge", stage="phase4")

        def build(journal, machine, results, run_budget):
            return lp.SupervisedLoop(
                config=lp.LoopConfig(
                    mode="supervised", task_id="M0-T036", stage="phase4",
                    allowed_paths=authority.allowed_paths,
                    stop_conditions=("no bypass flags",), max_cycles=3,
                    owner_touch_budget=8),
                journal=journal, audit=audit, machine=machine,
                authority=authority,
                runner=lpk.FakeRunner(*results),
                reviewer=lpk.FakeReviewer(lpk.outcome()),
                run_id="run-overnight", run_budget=run_budget,
                approval_gate=lambda d, p: True)

        ledger = budget_mod.RunBudgetLedger(
            journal, run_id="run-overnight",
            budget=budget_mod.RunBudget.from_limits(Limits()),
            clock=clock, audit=audit)
        ledger.start()
        machine = StateMachine(journal, audit, "run-overnight")
        machine.transition(sm.PREFLIGHT, "start_command")
        night_one = build(journal, machine,
                          [lpk.run_result() for _ in range(3)], ledger)
        run_one = night_one.run("night one first unit")
        self.assertEqual(len(run_one.cycles), 3)

        # The overnight roll + the injected controller restart.
        clock.advance(30 * 3600)
        journal.close()
        journal = DurableJournal(db).open()
        self.addCleanup(journal.close)
        resumed_ledger = budget_mod.RunBudgetLedger(
            journal, run_id="run-overnight",
            budget=budget_mod.RunBudget.from_limits(Limits()),
            clock=clock, audit=audit)
        resumed_ledger.start()
        machine_two = StateMachine(journal, audit, "run-overnight")
        night_two = build(journal, machine_two,
                          [lpk.run_result() for _ in range(3)],
                          resumed_ledger)
        run_two = night_two.run("night two resumes")
        self.assertGreaterEqual(len(run_two.cycles), 1)
        # No duplicated forward across the restart: message ids are unique.
        ids = list(run_one.forwarded_message_ids) + \
            list(run_two.forwarded_message_ids)
        self.assertEqual(len(ids), len(set(ids)),
                         "a restart must never re-send a forwarded prompt")
        self.assertTrue(resumed_ledger.resumed,
                        "the restarted ledger RESUMED the original record")
        self.assertGreaterEqual(
            resumed_ledger.elapsed(), 30 * 3600,
            "a restart can never earn back elapsed campaign time")


class SoakTests(WatcherBase):
    """16.9(h)/R118: the bounded soak - every counter boundary crossed via
    accelerated ticks, tallies durable across a mid-soak restart, no
    unbounded growth. The bound IS the breaker registry (`COUNTER_LIMITS`
    against the immutable `Limits`); no token is spent (R119/R182)."""

    def test_the_bounded_soak_crosses_every_breaker_boundary_exactly(self) -> None:
        from tools.agent_supervisor.config import Limits
        limits = Limits()
        breakers = CircuitBreakers(limits)
        crossed = 0
        for name, field in COUNTER_LIMITS.items():
            limit = int(getattr(limits, field))
            breakers.reset(name)
            verdict = None
            for _ in range(limit):
                verdict = breakers.record(name)
            self.assertTrue(verdict.tripped,
                            f"{name} must trip exactly at its limit {limit}")
            breakers.reset(name)
            for _ in range(limit - 1):
                verdict = breakers.record(name)
            self.assertFalse(verdict.tripped,
                             f"{name} must NOT trip below its limit")
            crossed += 1
        self.assertEqual(crossed, len(COUNTER_LIMITS),
                         "every registered counter boundary was soaked")

    def test_soak_tallies_survive_a_mid_soak_restart_without_growth(self) -> None:
        from tools.agent_supervisor import run_budget as budget_mod
        from tools.agent_supervisor.config import Limits
        limits = Limits()
        ledger = budget_mod.RunBudgetLedger(
            self.journal, run_id="run-soak",
            budget=budget_mod.RunBudget.from_limits(Limits()))
        ledger.start()
        breakers = CircuitBreakers(limits)
        for _ in range(3):
            breakers.record("restart_attempts")
        ledger.persist_counters(breakers.snapshot())
        keys_after_first = len(self.journal.all_state())
        for _ in range(50):  # the accelerated soak: repeated persists
            ledger.persist_counters(breakers.snapshot())
        self.assertEqual(len(self.journal.all_state()), keys_after_first,
                         "repeated soak persists must not grow the journal")
        db = self.tmp / "journal.sqlite3"
        self.journal.close()
        reopened = DurableJournal(db).open()
        self.addCleanup(reopened.close)
        self.journal = reopened
        resumed = budget_mod.RunBudgetLedger(
            reopened, run_id="run-soak",
            budget=budget_mod.RunBudget.from_limits(Limits()))
        resumed.start()
        restored = CircuitBreakers(limits)
        resumed.restore_counters(restored)
        self.assertEqual(restored.value("restart_attempts"), 3,
                         "the mid-soak tally survived the restart exactly")


class AutonomousSelectionTests(WatcherBase):
    """R186 steps 2 + 12: bounded autonomous selection; correct-next advance."""

    def good_record(self, **over) -> dict:
        data = {
            "schema": "campaign_continuity/v1", "campaign_id": "D-024-test",
            "directive_id": "D-024", "state": "active",
            "control_branch": "control/D-024-test",
            "ledger_lineage_base": "1" * 40,
            "authority": "source-001.md", "restrictions": [],
            "next_action": {"task_id": "GOLD-001",
                            "description": "one bounded unit"},
            "frozen": {"head_sha": "2" * 40,
                       "recorded_at": "2026-08-28T00:00:00+00:00"},
            "sequence": 3, "updated_at": "2026-08-28T00:00:00+00:00"}
        data.update(over)
        return data

    def test_an_unbounded_next_unit_selection_refuses(self) -> None:
        with self.assertRaises(cc.CampaignRecordError):
            cc.validate(self.good_record(
                next_action={"task_id": "GOLD-001", "description": ""}))

    def test_advance_moves_to_the_dependency_correct_next_task(self) -> None:
        path = self.tmp / "campaign.json"
        cc.atomic_write(path, cc.validate(self.good_record()))
        advanced = cc.advance(path, 3,
                              next_action={"task_id": "GOLD-002",
                                           "description": "the next unit"},
                              head_sha="3" * 40)
        self.assertEqual(advanced.sequence, 4)
        self.assertEqual(advanced.next_action["task_id"], "GOLD-002")
        with self.assertRaises(cc.SequenceConflict):
            cc.advance(path, 3,
                       next_action={"task_id": "GOLD-999",
                                    "description": "a stale racer"},
                       head_sha="4" * 40)


class OnDemandAfterCompactTests(GoldenRunBase):
    """R113: after the compact rotation handoff, deeper evidence is retrieved
    on demand from the authoritative source - never carried in the handoff."""

    def test_the_compact_handoff_omits_content_that_deep_retrieval_returns(self) -> None:
        content_a = f"{gr.INJECTED_MARKER} unit-a.txt"
        self.plan([
            self.work_step("cp-A", "unit-a.txt", usage_total=500_000),
            {"kind": "ready", "checkpoint_id": "cp-ready"},
        ])
        self.review_plan(["INJECTED: confirm identity after rotation."])
        self.run_cli(self.argv(max_cycles=2,
                               extra=("--context-rotation-threshold",
                                      "100000")))
        journal = self.journal()
        stored = rot.RotationLedger(journal).stored_handoff()
        self.assertIsNotNone(stored, "the rotation stored a handoff")
        self.assertNotIn(content_a, json.dumps(stored),
                         "the handoff is compact: it references, never copies")
        retrieved = _git(self.checkout, "show", f"{BRANCH}:docs/unit-a.txt")
        self.assertEqual(retrieved, content_a,
                         "the exact source is retrievable on demand")
        provenance = _git(self.checkout, "log", "-1", "--format=%H", BRANCH,
                          "--", "docs/unit-a.txt")
        self.assertRegex(provenance, r"^[0-9a-f]{40}$")


class CampaignCrossingEvidenceTests(unittest.TestCase):
    """16.9(l): THIS campaign crossed its primary-session turnovers from the
    one captured directive - evidenced by the machine-validated record."""

    def test_the_campaign_record_evidences_the_crossed_turnovers(self) -> None:
        path = REPO / "project-control" / "campaigns" / \
            "D-024-fable-codex-loop.json"
        record = cc.validate(json.loads(path.read_text(encoding="utf-8")))
        self.assertGreaterEqual(
            record.sequence, 22,
            "22+ recorded seams, each crossed without re-prompting the owner")
        self.assertIn("source-001.md", record.authority,
                      "every session re-derives authority from the ONE "
                      "captured directive")
        self.assertTrue(any("PR #241" in r for r in record.restrictions))


# --------------------------------------------------------------------------
# The executable prove-first registers (R018/R115/R186) + the R118 ladder
# --------------------------------------------------------------------------

THIS = "test_agent_supervisor_golden_run.py"
LOOP = "test_agent_supervisor_loop.py"
SUCCESSION = "test_agent_supervisor_controller_succession.py"
CONTRACTS = "test_agent_supervisor_bounded_contracts.py"
SUPERVISION = "test_agent_supervisor_runtime_supervision.py"
OPERATOR = "test_agent_supervisor_operator_channel.py"
CHAIN = "test_agent_supervisor_model_chain.py"
CRASH = "test_agent_supervisor_crash.py"
BOUNDED = "test_agent_supervisor_bounded_mode.py"
SCHEDULER = "test_agent_supervisor_scheduler.py"
RECOVERY = "test_agent_supervisor_recovery.py"
CONTINUITY = "test_agent_supervisor_bootstrap_continuity.py"
NATIVE = "test_agent_supervisor_native_adapter.py"
GOAL = "test_agent_supervisor_goal_integration.py"
TELEMETRY = "test_agent_supervisor_subagent_telemetry.py"
REPLAY = "test_agent_supervisor_replay.py"
FLOW = "test_agent_supervisor_github_flow.py"
INVARIANTS = "test_agent_supervisor_invariants.py"
REENTRY = "test_agent_supervisor_start_reentry.py"
SEAM = "test_agent_supervisor_turnover_live_seam.py"
TURNOVER = "test_agent_supervisor_turnover_integration.py"
REVIEWER = "test_agent_supervisor_reviewer.py"
ENDURANCE = "test_agent_supervisor_endurance.py"


class RegisterMixin:
    def assert_register(self, register) -> None:
        names_by_file: dict[str, set[str]] = {}
        for item, proofs in register.items():
            for filename, fragment in proofs:
                if filename not in names_by_file:
                    names_by_file[filename] = _test_names_in(filename)
                assert any(fragment in name
                           for name in names_by_file[filename]), (
                    f"{item!r} cites {filename}::{fragment}, but no such "
                    f"test exists - the prove-first mapping is stale")


class Section169RegisterTests(unittest.TestCase, RegisterMixin):
    """The R018 prove-first register for the 16.9 matrix (R115)."""

    SECTION_16_9: dict[str, tuple[tuple[str, str], ...]] = {
        "a_renewable_epochs_forced_rotations": (
            (SUCCESSION, "epochs_advance_as_a_renewable_bounded_sequence"),
            (THIS, "three_epochs_each_end_through_a_forced_rotation")),
        "b_mixed_fable_48_sequence": (
            (CHAIN, "a_real_process_comes_up_on_opus_4_8_after_a_fable_5_exhaustion"),
            (CHAIN, "the_return_to_the_pin_launches_a_real_process_on_the_pin"),
            (TURNOVER, "authorized_exhaustion_redispatches_exactly_one_opus_worker")),
        "c_bounded_subagents_no_parent_flooding": (
            (CONTRACTS, "producer_cap_rejects_fourth_writer"),
            (SUPERVISION, "verbose_child_transcript_stays_out_of_primary_context")),
        "d_mixed_session_routes_startup_overhead": (
            (CONTRACTS, "followup_resumes_healthy_subagent"),
            (CONTRACTS, "overloaded_subagent_never_resumed_to_save_startup"),
            (CONTRACTS, "startup_observation_measures_the_calibration_inputs")),
        "e_extended_pause_clean_resume": (
            (RECOVERY, "pause_and_resume_round_trip"),
            (SCHEDULER, "the_deadline_and_trigger_survive_a_restart"),
            (THIS, "an_extended_pause_survives_restart_and_resumes_cleanly")),
        "f_owner_status_ask_while_running": (
            (OPERATOR, "a_question_gets_a_concise_bounded_answer"),
            (THIS, "status_answers_read_only_while_the_producer_is_running")),
        "g_crash_restart_accelerated_overnight": (
            (CRASH, "a_crash_after_every_transition_in_a_full_cycle_resumes_exactly"),
            (BOUNDED, "a_resumed_loop_re_enters_with_the_tallies_it_left"),
            (THIS, "an_accelerated_overnight_campaign_survives_a_mid_campaign_restart")),
        "h_bounded_soak": (
            (THIS, "the_bounded_soak_crosses_every_breaker_boundary_exactly"),
            (THIS, "soak_tallies_survive_a_mid_soak_restart_without_growth"),
            (BOUNDED, "every_counter_in_the_registry_has_a_wired_event_site")),
        "i_idempotent_no_duration_start": (
            (OPERATOR, "start_takes_no_duration_and_is_unlimited_by_default"),
            (THIS, "a_second_start_while_the_lock_is_held_is_a_typed_refusal")),
        "j_status_clarity": (
            (OPERATOR, "every_fact_is_present_and_labeled_on_a_fresh_journal"),
            (SUCCESSION, "missing_usage_is_unknown_never_zero")),
        "k_stop_leaves_resumable_checkpoint": (
            (SUCCESSION, "graceful_stop_survives_a_restart_and_wins_over_queued_work"),
            (OPERATOR, "graceful_stop_is_durable_then_acknowledged_then_cleared")),
        "l_campaign_crossed_turnover_from_directive": (
            (CONTINUITY, "orientation_summary_contents"),
            (THIS, "the_campaign_record_evidences_the_crossed_turnovers")),
        "m_two_unit_golden_run": (
            (THIS, "the_two_unit_golden_run_crosses_a_rotation_with_no_human_step"),
            (THIS, "an_injected_controller_restart_continues_without_duplicate_work"),
            (LOOP, "cycle_two_receives_the_forwarded_prompt_not_the_original"),
            (LOOP, "a_model_downgrade_rotates_at_the_seam_and_relaunches_pinned")),
    }

    def test_every_16_9_item_maps_to_a_real_named_test(self) -> None:
        self.assert_register(self.SECTION_16_9)

    def test_the_16_9_register_lists_all_thirteen_items(self) -> None:
        self.assertEqual(len(self.SECTION_16_9), 13)


class GoldenSequenceRegisterTests(unittest.TestCase, RegisterMixin):
    """The R186 fifteen-step golden-run sequence, each step -> named proof."""

    R186_STEPS: dict[str, tuple[tuple[str, str], ...]] = {
        "s01_codex_reads_durable_campaign": (
            (CONTINUITY, "orientation_summary_contents"),
            (OPERATOR, "the_campaign_record_is_read_and_summarized")),
        "s02_selects_one_bounded_task": (
            (CONTRACTS, "vague_assignment_rejected"),
            (THIS, "an_unbounded_next_unit_selection_refuses")),
        "s03_launches_named_producer_via_backend": (
            (NATIVE, "build_background_argv_exact"),
            (NATIVE, "native_selected_only_with_optin_and_full_support")),
        "s04_bounded_goal": (
            (GOAL, "s1_one_task_only"),),
        "s05_subagents_sized_passively_observed": (
            (SUPERVISION, "observe_band_produces_no_worker_message"),
            (TELEMETRY, "subagent_token_samples_trend_only_never_a_measurement")),
        "s06_health_monitored_without_interrupting": (
            (SUPERVISION, "land_sends_one_concise_direction_exactly_once"),
            (SUCCESSION, "the_landing_instruction_is_clean")),
        "s07_lands_at_safe_seam": (
            (SUCCESSION, "a_quiet_unambiguous_moment_passes"),),
        "s08_tests_and_reviews_run": (
            (REVIEWER, "only_enumerated_read_only_git_commands_are_allowed"),
            (THIS, "the_two_unit_golden_run_crosses_a_rotation_with_no_human_step")),
        "s09_codex_decides_on_evidence": (
            (REPLAY, "clean_continuation_continues_with_no_owner_touch"),
            (REPLAY, "review_required_correction_revises")),
        "s10_effects_exactly_once": (
            (FLOW, "a_confirmed_push_is_not_pushed_again"),
            (LOOP, "a_second_forward_of_the_same_prompt_sends_nothing")),
        "s11_successor_reconstructs_from_durable_state": (
            (SEAM, "the_successor_receives_the_full_handoff_as_its_first_prompt"),
            (CONTINUITY, "orientation_summary_contents")),
        "s12_campaign_advances_to_correct_next": (
            (CONTINUITY, "advance_success_increments_sequence"),
            (THIS, "advance_moves_to_the_dependency_correct_next_task")),
        "s13_operator_controls_behave": (
            (OPERATOR, "the_stop_verbs_map_to_the_existing_surface"),
            (ENDURANCE, "every_s12_1_command_is_registered")),
        "s14_simulated_crash_no_duplicates": (
            (CRASH, "a_crash_after_every_transition_in_a_full_cycle_resumes_exactly"),
            (REENTRY, "run_cycle_from_start_claude_dispatches_exactly_once"),
            (THIS, "an_injected_controller_restart_continues_without_duplicate_work")),
        "s15_no_protected_owner_gate_crossed": (
            (INVARIANTS, "invariant_7_no_owner_gate_is_satisfied_by_a_model"),
            (INVARIANTS, "invariant_9_no_automatic_merge_deploy_credential_payment_or_g6")),
    }

    def test_every_r186_step_maps_to_a_real_named_test(self) -> None:
        self.assert_register(self.R186_STEPS)

    def test_the_r186_register_lists_all_fifteen_steps(self) -> None:
        self.assertEqual(len(self.R186_STEPS), 15)


class LadderRegisterTests(unittest.TestCase, RegisterMixin):
    """The R118 progression ladder: every rung -> named proof or owner gate."""

    #: rung -> ("test", ((file, fragment), ...)) | ("owner_gated", reason)
    LADDER: dict[str, tuple[str, object]] = {
        "r01_deterministic_simulation": ("test", (
            (REPLAY, "the_report_declares_zero_model_calls_and_zero_writes"),)),
        "r02_read_only_shadow_telemetry": ("test", (
            (LOOP, "a_real_child_process_drives_a_shadow_cycle"),
            (CHAIN, "shadow_observes_and_never_switches"))),
        "r03_supervised_local_canary_fake_effects": ("test", (
            (LOOP, "run2_scenario_clear_recovery_then_start_works"),)),
        "r04_disposable_real_session_canary": ("test", (
            (THIS, "the_two_unit_golden_run_crosses_a_rotation_with_no_human_step"),)),
        "r05_crash_restart_forced_fallback_canary": ("test", (
            (THIS, "an_injected_controller_restart_continues_without_duplicate_work"),
            (CHAIN, "a_real_process_comes_up_on_opus_4_8_after_a_fable_5_exhaustion"))),
        "r06_low_risk_real_repo_task_non_protected_branch": ("test", (
            (THIS, "the_two_unit_golden_run_crosses_a_rotation_with_no_human_step"),)),
        "r07_two_unit_golden_readiness_run": ("test", (
            (THIS, "the_two_unit_golden_run_crosses_a_rotation_with_no_human_step"),)),
        "r08_host_restart_canary_or_truthful_limitation": ("test", (
            (SUCCESSION, "forbidden_registration_reports_a_truthful_activation_blocker"),
            (SCHEDULER, "a_confirmed_install_verifies_afterwards"))),
        "r09_bounded_soak_reliability_proof": ("test", (
            (THIS, "the_bounded_soak_crosses_every_breaker_boundary_exactly"),)),
        "r10_independent_final_review": (
            "process",
            "the four independent reviewers (G3/G4/G5 + DCV) at ONE frozen "
            "identity; recorded in project-control/gates/M0-T096-*.json"),
        "r11_owner_activation_checkpoint": (
            "owner_gated",
            "R187/R595: continuous mode stays DISABLED after the golden run "
            "until explicit owner activation; the activation package is "
            "project-control/reports/M0-T096-activation-package.md"),
    }

    def test_every_test_rung_maps_to_a_real_named_test(self) -> None:
        register = {rung: proofs
                    for rung, (kind, proofs) in self.LADDER.items()
                    if kind == "test"}
        self.assert_register(register)

    def test_non_test_rungs_name_their_gate_or_process(self) -> None:
        for rung, (kind, detail) in self.LADDER.items():
            if kind in ("owner_gated", "process"):
                self.assertTrue(isinstance(detail, str) and len(detail) > 20,
                                f"{rung} must name its gate explicitly")
        gated = [r for r, (k, _) in self.LADDER.items() if k == "owner_gated"]
        self.assertEqual(gated, ["r11_owner_activation_checkpoint"],
                         "exactly ONE rung is owner-gated (R187/R595)")

    def test_the_ladder_lists_all_eleven_rungs(self) -> None:
        self.assertEqual(len(self.LADDER), 11)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
