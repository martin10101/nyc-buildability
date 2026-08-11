#!/usr/bin/env python3
"""B-018: stranded-START_CLAUDE crash-window recovery.

Defect (reproduced live 2026-08-08): an external kill of the supervisor between
the `preflight_pass -> START_CLAUDE` journal commit (loop.py ~1607) and the
worker launch (~1632) strands the durable journal at START_CLAUDE with NOTHING
launched. Before this fix, CYCLE_ENTRY_STATES omitted START_CLAUDE, so every
subsequent operator `start` raised `bad_cycle_entry_state` in run_cycle - even
after recover_boot classified the checkout SAFE_CHECKPOINT - and no production
code drove the S7 exits from START_CLAUDE. The launch was permanently
unrecoverable without out-of-band action.

The fix admits START_CLAUDE to CYCLE_ENTRY_STATES: the state means "about to
launch, nothing has launched yet", which is exactly a safe re-entry. These tests
prove three things:

  (a) a journal stranded at START_CLAUDE with NO recorded children RESUMES: the
      unit dispatches EXACTLY ONCE and the machine transitions to CLAUDE_RUNNING
      (regression - this used to raise bad_cycle_entry_state);
  (b) fail-closed - a recovery condition that is NOT SAFE_CHECKPOINT (a surviving
      recorded child, or a competing writer) still makes `start`'s classification
      gate REFUSE to dispatch, so admitting START_CLAUDE never widens who may
      launch;
  (c) idempotence - a stranded START_CLAUDE whose previous process recorded a
      SURVIVING child is refused by recover_boot's child accounting BEFORE the
      loop is ever built, so a resume can never double-launch over a live worker.
"""
from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import recovery as rec  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.claude_runner import RunnerConfig, RunResult  # noqa: E402
from tools.agent_supervisor.codex_reviewer import ReviewOutcome, map_decision_to_tier  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import ClaudeCheckpoint, CodexDecision, digest_of  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402


# --------------------------------------------------------------------------
# Fakes (same shape as tools/test_agent_supervisor_loop.py)
# --------------------------------------------------------------------------

_FAKE_LAUNCH_CONFIG = RunnerConfig(executable="fake-claude")


def checkpoint(**overrides) -> ClaudeCheckpoint:
    data = dict(
        schema_version="1.0.0", run_id="run-reentry", checkpoint_id="cp-1",
        task_id="M0-T052", claude_session_id="sess-1", status="UNIT_COMPLETE",
        summary="unit complete", starting_sha="a" * 40, current_sha="b" * 40,
        branch="task/M0-T052-start-reentry", worktree="/repo/wt",
        proposed_next_action="continue", usage="unknown", context_pressure="unknown")
    data.update(overrides)
    return ClaudeCheckpoint(**data)


def decision(**overrides) -> CodexDecision:
    data = dict(
        schema_version="1.0.0", decision="CONTINUE", reviewed_task_id="M0-T052",
        reviewed_checkpoint_id="cp-1", verified_repo_head="b" * 40,
        verified_origin_main="a" * 40, model_used="fake-review-model",
        next_claude_prompt="Do the next bounded unit.")
    data.update(overrides)
    return CodexDecision(**data)


class FakeRunner:
    """Returns a scripted RunResult and records every prompt (= every dispatch)."""

    def __init__(self, *results: RunResult, model: str = "") -> None:
        self.results = list(results) or [run_result()]
        self.prompts: list[str] = []
        self.models: list[str] = []
        self.config = dataclasses.replace(_FAKE_LAUNCH_CONFIG, model=model,
                                          expected_model=model)

    def with_model(self, model: str) -> "FakeRunner":
        clone = FakeRunner(*self.results, model=model)
        clone.prompts = self.prompts
        clone.models = self.models
        return clone

    def run_unit(self, prompt: str, **_kwargs) -> RunResult:
        self.prompts.append(prompt)
        self.models.append(self.config.model)
        return self.results[min(len(self.prompts) - 1, len(self.results) - 1)]


def run_result(cp: ClaudeCheckpoint | None = None, **overrides) -> RunResult:
    data = dict(argv=("fake",), returncode=0, duration_seconds=0.1,
                session_id="sess-1", checkpoint=cp if cp is not None else checkpoint(),
                containment="job_object")
    data.update(overrides)
    return RunResult(**data)


class FakeReviewer:
    def __init__(self, *outcomes: ReviewOutcome) -> None:
        self.outcomes = list(outcomes)
        self.packets: list[dict] = []

    def review(self, packet, **_kwargs) -> ReviewOutcome:
        self.packets.append(dict(packet))
        return self.outcomes[min(len(self.packets) - 1, len(self.outcomes) - 1)]


def outcome(dec: CodexDecision | None = None, **overrides) -> ReviewOutcome:
    actual = dec if dec is not None else decision()
    data = dict(decision=actual, model_used="fake-review-model",
                selection_digest="sel", attempts=1,
                decision_digest=digest_of(actual.to_dict()),
                tier=map_decision_to_tier(actual))
    data.update(overrides)
    return ReviewOutcome(**data)


# --------------------------------------------------------------------------
# Base
# --------------------------------------------------------------------------


class StartReentryBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.journal = DurableJournal(self.tmp / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.run_id = "run-reentry"
        self.machine = StateMachine(self.journal, self.audit, self.run_id)
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T052",
             "allowed_paths": ["tools/agent_supervisor/**",
                               "tools/test_agent_supervisor_*.py"],
             "forbidden_paths": [".github/**", ".claude/**"],
             "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T052-start-reentry", stage="phase4",
            documented_test_commands=(
                "python tools/test_agent_supervisor_start_reentry.py",))

    def strand_at_start_claude(self) -> None:
        """Commit exactly the durable transitions that precede a worker launch.

        IDLE -> PREFLIGHT (operator `start`) -> START_CLAUDE (preflight_pass).
        NOTHING is launched and NO child is recorded: this is the byte-for-byte
        durable state a crash inside the launch window leaves behind.
        """
        self.machine.transition(sm.PREFLIGHT, "start_command",
                                detail={"operator_initiated": True})
        self.machine.transition(sm.START_CLAUDE, "preflight_pass",
                                detail={"cycle": 1, "mode": "supervised"})

    def build(self, *, mode: str = "shadow", runner=None, reviewer=None,
              approval_gate=None, max_cycles: int = 4) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode=mode, task_id="M0-T052", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=max_cycles, owner_touch_budget=2),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=runner or FakeRunner(run_result()),
            reviewer=reviewer or FakeReviewer(outcome()),
            run_id=self.run_id, approval_gate=approval_gate)


# --------------------------------------------------------------------------
# (a) Crash-window regression: START_CLAUDE resumes, dispatching exactly once
# --------------------------------------------------------------------------


class CrashWindowResumeTests(StartReentryBase):
    def test_start_claude_is_a_legal_cycle_entry_state(self) -> None:
        # The whole fix in one assertion: START_CLAUDE joined the entry set.
        self.assertIn(sm.START_CLAUDE, lp.CYCLE_ENTRY_STATES)

    def test_the_strand_is_durable_and_read_from_the_journal(self) -> None:
        self.strand_at_start_claude()
        # A fresh machine (a fresh process) reads START_CLAUDE from the journal,
        # never from memory - this is the exact condition after an external kill.
        fresh = StateMachine(self.journal, self.audit, self.run_id)
        self.assertEqual(fresh.current_state, sm.START_CLAUDE)

    def test_run_cycle_from_start_claude_dispatches_exactly_once(self) -> None:
        self.strand_at_start_claude()
        runner = FakeRunner(run_result())
        loop = self.build(mode="shadow", runner=runner)
        # Pre-fix this raised LoopError('bad_cycle_entry_state').
        result = loop.run_cycle("resume the interrupted launch", cycle=1)
        self.assertEqual(len(runner.prompts), 1,
                         "the resumed cycle must dispatch the worker exactly once")
        self.assertIn(sm.CLAUDE_RUNNING, result.path,
                      "the resumed launch must transition START_CLAUDE -> "
                      "CLAUDE_RUNNING on a real process")

    def test_resume_does_not_re_record_the_preflight_transition(self) -> None:
        self.strand_at_start_claude()
        before = [(t.state_from, t.state_to) for t in self.journal.transitions()]
        self.assertEqual(before[-1], (sm.PREFLIGHT, sm.START_CLAUDE))
        loop = self.build(mode="shadow", runner=FakeRunner(run_result()))
        loop.run_cycle("resume", cycle=1)
        after = [(t.state_from, t.state_to) for t in self.journal.transitions()]
        # The `if entry == PREFLIGHT` guard means resume adds NO duplicate
        # PREFLIGHT -> START_CLAUDE; the next recorded transition launches.
        self.assertEqual(after[len(before):][0], (sm.START_CLAUDE, sm.CLAUDE_RUNNING))
        self.assertEqual(
            [step for step in after if step == (sm.PREFLIGHT, sm.START_CLAUDE)],
            [(sm.PREFLIGHT, sm.START_CLAUDE)],
            "resume must not commit a second preflight_pass transition")

    def test_production_run_entry_from_start_claude_completes_legally(self) -> None:
        # loop.run() is the real production entry (via cmd_start -> _run_loop).
        # From START_CLAUDE it must NOT raise and must complete a legal run.
        self.strand_at_start_claude()
        runner = FakeRunner(run_result())
        run = self.build(mode="shadow", runner=runner).run("resume the launch")
        self.assertEqual(run.stopped, "shadow_observation_complete")
        self.assertEqual(len(runner.prompts), 1)
        self.assertEqual(self.machine.current_state, sm.PREFLIGHT,
                         "a completed shadow observation closes into a resumable state")

    def test_supervised_resume_walks_the_rest_of_the_s7_path_once(self) -> None:
        self.strand_at_start_claude()
        runner = FakeRunner(run_result())
        loop = self.build(mode="supervised", runner=runner,
                          approval_gate=lambda digest, prompt: True)
        result = loop.run_cycle("resume the launch", cycle=1)
        self.assertEqual(len(runner.prompts), 1)
        # Same tail as a normal supervised cycle, entered from START_CLAUDE.
        self.assertEqual(
            result.path,
            (sm.CLAUDE_RUNNING, sm.CHECKPOINT_RECEIVED, sm.COLLECT_EVIDENCE,
             sm.CODEX_REVIEW, sm.VALIDATE_DECISION, sm.POLICY_CHECK,
             sm.WAIT_FOR_OWNER, sm.FORWARD_PROMPT, sm.CLAUDE_RUNNING))
        self.assertTrue(result.forwarded)


# --------------------------------------------------------------------------
# (b)/(c) Fail-closed: a non-SAFE_CHECKPOINT recovery still refuses to dispatch
# --------------------------------------------------------------------------


class FailClosedResumeTests(StartReentryBase):
    ALL_PASS = {name: True for name in rec.REVALIDATION_STEPS}

    def test_a_surviving_recorded_child_forbids_the_resume(self) -> None:
        """(b)+(c): the previous process recorded a SURVIVING child.

        recover_boot's child accounting (S11.5 step 3) marks it UNACCOUNTED and
        classifies UNSAFE_OR_DRIFTED. `start` gates dispatch on
        classification == SAFE_CHECKPOINT, so the loop is never built and no
        second worker is launched over the live one - the idempotence guarantee.
        """
        self.strand_at_start_claude()
        # os.getpid() is provably alive and determined: a real surviving child.
        rec.record_launched_child(self.journal, pid=os.getpid(), role="worker")
        outcome_ = rec.recover_boot(
            journal=self.journal, lock=None, revalidation=self.ALL_PASS)
        self.assertEqual(outcome_.classification, rec.UNSAFE_OR_DRIFTED)
        self.assertIn(os.getpid(), outcome_.unaccounted_children)
        # This is the exact boolean `cmd_start` uses to refuse dispatch.
        self.assertNotEqual(outcome_.classification, rec.SAFE_CHECKPOINT)

    def test_a_competing_writer_forbids_the_resume(self) -> None:
        self.strand_at_start_claude()
        outcome_ = rec.recover_boot(
            journal=self.journal, lock=None, revalidation=self.ALL_PASS,
            competing_writer=(True, "another supervisor is writing the journal"))
        self.assertEqual(outcome_.classification, rec.UNSAFE_OR_DRIFTED)
        self.assertNotEqual(outcome_.classification, rec.SAFE_CHECKPOINT)

    def test_a_pending_external_effect_makes_the_resume_ambiguous(self) -> None:
        self.strand_at_start_claude()
        self.journal.record_before_effect(
            action_id="act-1", effect_type="branch_push", target="task/x",
            expected_prior_state="unknown", request_digest="d")
        outcome_ = rec.recover_boot(
            journal=self.journal, lock=None, revalidation=self.ALL_PASS)
        self.assertEqual(outcome_.classification, rec.AMBIGUOUS_EFFECT)
        self.assertNotEqual(outcome_.classification, rec.SAFE_CHECKPOINT)

    def test_a_clean_strand_classifies_safe_checkpoint(self) -> None:
        # The positive control: with no surviving child, no competing writer, and
        # no pending effect, the SAME stranded START_CLAUDE journal classifies
        # SAFE_CHECKPOINT - which is exactly why (a)'s resume is allowed to run.
        self.strand_at_start_claude()
        outcome_ = rec.recover_boot(
            journal=self.journal, lock=None, revalidation=self.ALL_PASS)
        self.assertEqual(outcome_.classification, rec.SAFE_CHECKPOINT)


# --------------------------------------------------------------------------
# (d) M0-T053: the C1 host-containment gate in the START launch path
# (qualifying evidence: M0-T052 G5 SEC-MAJOR, required correction C1)
# --------------------------------------------------------------------------

CONFIG_TOML = """
[codex]
allowed_models = ["codex-primary"]

[claude]
allowed_models = ["claude-worker"]

[controller]
default_mode = "shadow"

[limits]
max_review_packet_bytes = 262144
"""

SELECTION_TOML = """
[codex]
review_model = "codex-primary"
advisory_model = "codex-primary"
fallback_models = []

[claude]
model = "claude-worker"
fallback_models = []
"""


class ContainmentGateTests(unittest.TestCase):
    """C1: `start` refuses to spawn a worker on a host without kill-on-close.

    Until M0-T053 the bar lived only in the activation record and in `doctor`'s
    advisory report, so nothing stopped a supervised run on a POSIX or
    Windows-`taskkill` host - where an external kill of the supervisor skips the
    runner's `finally` termination and strands a live worker for the next
    `start` to launch a second worker over (M0-T052 G5 SEC-MAJOR, C1).
    """

    def setUp(self) -> None:
        from tools.agent_supervisor import cli
        from tools.agent_supervisor import process as proc

        self.cli = cli
        self.proc = proc
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.runtime = self.tmp / "runtime"
        self.config = self.tmp / "config.toml"
        self.config.write_text(CONFIG_TOML, encoding="utf-8")
        self.selection = self.tmp / "model_selection.toml"
        self.selection.write_text(SELECTION_TOML, encoding="utf-8")
        self.packet = self.tmp / "M0-T053.json"
        self.packet.write_text(json.dumps({
            "task_id": "M0-T053",
            "allowed_paths": ["tools/agent_supervisor/**"],
            "forbidden_paths": [".github/**"],
            "status": "in_progress",
            "stop_conditions": ["no bypass flags"],
        }), encoding="utf-8")

    def full_inputs(self) -> tuple[str, ...]:
        return ("start", "--mode", "shadow",
                "--claude-executable", sys.executable,
                "--codex-executable", sys.executable,
                "--task-packet", str(self.packet),
                "--config", str(self.config),
                "--model-selection", str(self.selection))

    def run_cli(self, *args: str) -> tuple[int, dict]:
        stdout = io.StringIO()
        argv = [*args, "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime), "--json"]
        with contextlib.redirect_stdout(stdout):
            code = self.cli.main(list(argv))
        return code, json.loads(stdout.getvalue())

    @contextlib.contextmanager
    def host_containment(self, kind: str):
        """Pretend this host's DEFAULT containment is `kind`.

        The gate is patched at its single source of truth - the same
        `default_containment_kind()` `doctor` reads - so both host shapes are
        exercised on any machine the suite runs on, and neither branch depends
        on which OS happens to be running the test.
        """
        original = self.cli.default_containment_kind
        self.cli.default_containment_kind = lambda: kind  # type: ignore[assignment]
        try:
            yield
        finally:
            self.cli.default_containment_kind = original  # type: ignore[assignment]

    def audit_events(self) -> list[str]:
        from tools.agent_supervisor.durable_state import runtime_dir_for

        path = runtime_dir_for(self.repo, base=str(self.runtime)) / "audit.jsonl"
        if not path.exists():
            return []
        return [json.loads(line)["event_type"]
                for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_the_gate_reads_the_same_host_source_doctor_reads(self) -> None:
        # Doctor parity by construction: the gate has no config, flag, or
        # environment input of its own - it reports what the host actually does.
        ok, kind, _ = self.cli.containment_precondition()
        self.assertEqual(kind, self.proc.default_containment_kind())
        self.assertEqual(ok, kind == self.proc.CONTAINMENT_JOB_OBJECT)

    def test_a_posix_process_group_host_refuses_to_dispatch(self) -> None:
        with self.host_containment(self.proc.CONTAINMENT_PROCESS_GROUP):
            code, payload = self.run_cli(*self.full_inputs())
        self.assertEqual(code, 0)
        self.assertFalse(payload["dispatched"],
                         "a host without kill-on-close must never spawn a worker")
        self.assertEqual(payload["provider_calls_made"], 0)
        self.assertFalse(payload["containment"]["ok"])
        self.assertEqual(payload["containment"]["kind"],
                         self.proc.CONTAINMENT_PROCESS_GROUP)
        self.assertIn("containment_refused", payload["stopped_because"])
        self.assertIn("double-launch", payload["stopped_because"])
        self.assertIn("containment_gate_refused", self.audit_events())

    def test_a_windows_taskkill_fallback_host_refuses_to_dispatch(self) -> None:
        with self.host_containment(self.proc.CONTAINMENT_TASKKILL):
            _, payload = self.run_cli(*self.full_inputs())
        self.assertFalse(payload["dispatched"])
        self.assertEqual(payload["containment"]["kind"], self.proc.CONTAINMENT_TASKKILL)
        self.assertIn("containment_refused", payload["stopped_because"])

    def test_an_undeterminable_containment_refuses_to_dispatch(self) -> None:
        def explode() -> str:
            raise OSError("the host would not say")

        original = self.cli.default_containment_kind
        self.cli.default_containment_kind = explode  # type: ignore[assignment]
        try:
            _, payload = self.run_cli(*self.full_inputs())
        finally:
            self.cli.default_containment_kind = original  # type: ignore[assignment]
        self.assertFalse(payload["dispatched"])
        self.assertEqual(payload["containment"]["kind"], "unknown")
        self.assertIn("REFUSAL", payload["stopped_because"])

    def test_a_job_object_host_permits_the_dispatch(self) -> None:
        with self.host_containment(self.proc.CONTAINMENT_JOB_OBJECT):
            code, payload = self.run_cli(*self.full_inputs())
        self.assertEqual(code, 0)
        self.assertTrue(payload["containment"]["ok"])
        self.assertTrue(payload["dispatched"],
                        "the gate must not block the verified live host shape")
        # sys.executable is not a real worker, so the cycle ends in the honest
        # no_valid_checkpoint stop; what C1 requires is that dispatch RAN.
        self.assertEqual(payload["stopped_because"], "no_valid_checkpoint")
        self.assertNotIn("containment_gate_refused", self.audit_events())

    def test_the_dispatched_run_records_and_clears_the_child_in_production(self) -> None:
        """C2 end to end through the real CLI: the launch path really is wired.

        The two accounting calls are observed where the RUNNER makes them (the
        spies delegate to the real functions, so the journal is written exactly
        as in production), because "the key ended up empty" alone would also be
        true of a launch path that recorded nothing and only cleared. Both the
        call with a live pid and the final empty record are asserted.
        """
        from tools.agent_supervisor import claude_runner as cr
        from tools.agent_supervisor.durable_state import DB_FILENAME, runtime_dir_for

        recorded: list[dict] = []
        cleared: list[bool] = []
        real_record, real_clear = cr.record_launched_child, cr.clear_child_record

        def spy_record(journal, *, pid, role, start_token=""):
            recorded.append({"pid": pid, "role": role})
            real_record(journal, pid=pid, role=role, start_token=start_token)

        def spy_clear(journal, **kwargs):
            cleared.append(True)
            real_clear(journal, **kwargs)

        cr.record_launched_child = spy_record  # type: ignore[assignment]
        cr.clear_child_record = spy_clear  # type: ignore[assignment]
        try:
            with self.host_containment(self.proc.CONTAINMENT_JOB_OBJECT):
                _, payload = self.run_cli(*self.full_inputs())
        finally:
            cr.record_launched_child = real_record  # type: ignore[assignment]
            cr.clear_child_record = real_clear  # type: ignore[assignment]

        self.assertTrue(payload["dispatched"])
        self.assertEqual(len(recorded), 1,
                         "the production launch path must record the worker pid")
        self.assertEqual(recorded[0]["role"], cr.WORKER_CHILD_ROLE)
        self.assertGreater(int(recorded[0]["pid"]), 0)
        self.assertEqual(len(cleared), 1, "the verified exit must clear the record")

        journal = DurableJournal(
            runtime_dir_for(self.repo, base=str(self.runtime)) / DB_FILENAME).open()
        self.addCleanup(journal.close)
        self.assertEqual(journal.get_state(rec.CHILD_PROCESSES_KEY, "absent"), [],
                         "the durable record must be empty after the verified exit")


if __name__ == "__main__":
    unittest.main()
