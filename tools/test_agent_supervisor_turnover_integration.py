#!/usr/bin/env python3
"""M0-T054 increment 4: the WORKER-layer Fable->Opus turnover INTEGRATION seam.

Qualifying evidence (supervisor-freeze §2, AD-093): the reproduced provider
incident D-010 source-028 / R289 - Fable 5 hard-stopped at its weekly usage limit
with the exact message "You've reached your Fable 5 limit. Run /usage-credits to
continue or switch models with /model." and the built-in fallbackModel did NOT
auto-switch. This increment wires the already-committed turnover stack into the
assembled loop at the ONE seam where a missing/failed worker result would become a
terminal `no_valid_checkpoint` stop.

These tests drive the REAL `SupervisedLoop` and the REAL
`WorkerTurnoverIntegration` with in-memory FAKES - no provider, no subprocess, no
network, no config change. They prove:

* a supervised worker result carrying the exact Fable weekly-limit message, with
  an owner-authorized channel, redispatches EXACTLY ONE claude-opus-4-8 WORKER
  successor (asserted via the fake launcher's recorded invocation) and records the
  Fable->Opus audit link;
* a normal successful worker result never reaches the seam - NO turnover, existing
  behaviour unchanged;
* an ordinary failure / ambiguous failed result classifies to no-turnover and
  keeps the existing `no_valid_checkpoint` PAUSE - NO launch;
* a duplicate exhaustion event (same failed unit) is suppressed - NO second
  redispatch;
* mode/authority gating: with no owner authorization (the default) a confirmed
  exhaustion is RECORDED and surfaced but NOT auto-run - supervised-mode approval /
  LIMITED-AUTO-off is never bypassed.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys
import tempfile
import unittest
from typing import Any, Mapping

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.claude_runner import RunResult  # noqa: E402
from tools.agent_supervisor.codex_reviewer import ReviewOutcome, map_decision_to_tier  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import ClaudeCheckpoint, CodexDecision, digest_of  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402
from tools.agent_supervisor.turnover_controller import (  # noqa: E402
    ALLOWED_SUCCESSOR_EFFORT,
    ALLOWED_SUCCESSOR_MODEL_ID,
    LaunchRequest,
    LaunchResult,
    TurnoverContext,
    TurnoverController,
    TurnoverLayer,
    TurnoverStatus,
)
from tools.agent_supervisor.worker_turnover import (  # noqa: E402
    REASON_TURNOVER_LAUNCHED,
    REASON_TURNOVER_RECORDED,
    WorkerTurnoverIntegration,
)

#: The exact R289 message (D-010 source-028) the exhausted Fable worker emitted.
FABLE_LIMIT_MESSAGE = (
    "You've reached your Fable 5 limit. Run /usage-credits to continue or switch "
    "models with /model.")


# --------------------------------------------------------------------------
# In-memory fakes for the controller's injected dependencies
# --------------------------------------------------------------------------


class FakeLauncher:
    """Records every launch and hands back a scripted result (no subprocess)."""

    def __init__(self, *, available: bool = True) -> None:
        self.available = available
        self.calls: list[LaunchRequest] = []

    def launch(self, request: LaunchRequest) -> LaunchResult:
        self.calls.append(request)
        if not self.available:
            return LaunchResult(available=False, detail="opus unavailable")
        return LaunchResult(available=True, successor_id=f"opus-successor-{len(self.calls)}",
                            model_id=ALLOWED_SUCCESSOR_MODEL_ID, detail="launched")


class FakeLock:
    def __init__(self) -> None:
        self.acquired = False

    def acquire(self) -> bool:
        self.acquired = True
        return True

    def release(self) -> None:
        self.acquired = False


class FakeAudit:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self._actioned: set[str] = set()

    def already_actioned(self, event_id: str) -> bool:
        return event_id in self._actioned

    def append(self, record: Mapping[str, Any]) -> str:
        stored = dict(record)
        self.records.append(stored)
        return stored.get("audit_id", f"audit-{len(self.records)}")

    def mark_actioned(self, event_id: str) -> None:
        self._actioned.add(event_id)

    def launched_records(self) -> list[dict[str, Any]]:
        return [r for r in self.records if r.get("kind") == "fable_to_opus_turnover"]


class FakeIdentity:
    def __init__(self) -> None:
        self._n = 0

    def now_iso(self) -> str:
        return "2026-08-09T00:00:00Z"

    def new_audit_id(self) -> str:
        self._n += 1
        return f"audit-id-{self._n}"


def _no_survivor(_context: TurnoverContext) -> bool:
    return False


def build_controller(*, launcher: FakeLauncher | None = None, survivor=_no_survivor):
    launcher = launcher or FakeLauncher()
    audit = FakeAudit()
    controller = TurnoverController(
        launcher=launcher, lock=FakeLock(), audit=audit, identity=FakeIdentity(),
        survivor_detected=survivor)
    return controller, launcher, audit


def _authorized(_config: Any) -> bool:
    """An owner-authorized actuation channel (the R289/R595 activation stance)."""
    return True


# --------------------------------------------------------------------------
# Loop fakes (mirrors the harness in test_agent_supervisor_loop.py)
# --------------------------------------------------------------------------


def checkpoint(**overrides) -> ClaudeCheckpoint:
    data = dict(
        schema_version="1.0.0", run_id="run-turnover", checkpoint_id="cp-1",
        task_id="M0-T054", claude_session_id="sess-1", status="UNIT_COMPLETE",
        summary="unit complete", starting_sha="a" * 40, current_sha="b" * 40,
        branch="task/M0-T054-turnover-watchdog", worktree="/repo/wt",
        proposed_next_action="continue", usage="unknown", context_pressure="unknown")
    data.update(overrides)
    return ClaudeCheckpoint(**data)


def decision(**overrides) -> CodexDecision:
    data = dict(
        schema_version="1.0.0", decision="CONTINUE", reviewed_task_id="M0-T054",
        reviewed_checkpoint_id="cp-1", verified_repo_head="b" * 40,
        verified_origin_main="a" * 40, model_used="fake-review-model",
        next_claude_prompt="Do the next bounded unit.")
    data.update(overrides)
    return CodexDecision(**data)


def review_outcome(dec: CodexDecision | None = None, **overrides) -> ReviewOutcome:
    actual = dec if dec is not None else decision()
    data = dict(decision=actual, model_used="fake-review-model",
                selection_digest="sel", attempts=1,
                decision_digest=digest_of(actual.to_dict()),
                tier=map_decision_to_tier(actual))
    data.update(overrides)
    return ReviewOutcome(**data)


class FakeRunner:
    """Returns a scripted RunResult and records prompts (no subprocess)."""

    def __init__(self, *results: RunResult, model: str = "") -> None:
        self.results = list(results)
        self.prompts: list[str] = []
        from tools.agent_supervisor.claude_runner import RunnerConfig
        self.config = RunnerConfig(executable="fake-claude", model=model,
                                   expected_model=model)

    def with_model(self, model: str) -> "FakeRunner":
        clone = FakeRunner(*self.results, model=model)
        clone.prompts = self.prompts
        return clone

    def run_unit(self, prompt: str, **_kwargs) -> RunResult:
        self.prompts.append(prompt)
        return self.results[min(len(self.prompts) - 1, len(self.results) - 1)]


class FakeReviewer:
    def __init__(self, *outcomes: ReviewOutcome) -> None:
        self.outcomes = list(outcomes)

    def review(self, packet, **_kwargs) -> ReviewOutcome:
        return self.outcomes[0]


def success_result() -> RunResult:
    return RunResult(argv=("fake",), returncode=0, duration_seconds=0.1,
                     session_id="sess-1", checkpoint=checkpoint(),
                     containment="job_object")


def failed_result(*, stderr: str, returncode: int = 1) -> RunResult:
    return RunResult(argv=("fake",), returncode=returncode, duration_seconds=0.1,
                     session_id="sess-fable", checkpoint=None,
                     checkpoint_error="the worker exited without a valid checkpoint",
                     stderr_tail=stderr, containment="job_object")


# --------------------------------------------------------------------------
# Loop-level tests: the seam fires (or doesn't) inside the REAL run_cycle
# --------------------------------------------------------------------------


class LoopSeamTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.journal = DurableJournal(self.tmp / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.run_id = "run-turnover"
        self.machine = StateMachine(self.journal, self.audit, self.run_id)
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T054",
             "allowed_paths": ["tools/agent_supervisor/**"],
             "forbidden_paths": [".github/**"], "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T054-turnover-watchdog", stage="phase4")

    def build(self, *, runner, worker_turnover, mode: str = "supervised",
              pinned_model: str = "claude-fable-5") -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode=mode, task_id="M0-T054", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 max_cycles=4, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority, runner=runner,
            reviewer=FakeReviewer(review_outcome()), run_id=self.run_id,
            pinned_model=pinned_model, worker_turnover=worker_turnover)

    def at_preflight(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")


class TurnoverFiresTests(LoopSeamTestBase):
    def test_authorized_exhaustion_redispatches_exactly_one_opus_worker(self) -> None:
        controller, launcher, audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        runner = FakeRunner(failed_result(stderr=FABLE_LIMIT_MESSAGE),
                            model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=integration)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        # Exactly one WORKER-layer opus-4.8/xhigh successor was launched.
        self.assertEqual(len(launcher.calls), 1)
        self.assertEqual(launcher.calls[0].layer, TurnoverLayer.WORKER)
        self.assertEqual(launcher.calls[0].model_id, ALLOWED_SUCCESSOR_MODEL_ID)
        self.assertEqual(launcher.calls[0].effort, ALLOWED_SUCCESSOR_EFFORT)
        # The cycle stopped on the turnover reason, not the ordinary no-checkpoint
        # stop, and landed at the safe PAUSED_RECOVERY state.
        self.assertEqual(result.stopped, REASON_TURNOVER_LAUNCHED)
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)
        # The Fable->Opus link was audited: the stopped Fable execution -> the
        # launched opus successor.
        launched = audit.launched_records()
        self.assertEqual(len(launched), 1)
        self.assertEqual(launched[0]["link"]["opus_successor_id"], "opus-successor-1")
        self.assertEqual(launched[0]["link"]["stopped_fable_execution_id"], "sess-fable")
        self.assertEqual(launched[0]["successor_model_id"], ALLOWED_SUCCESSOR_MODEL_ID)

    def test_normal_success_never_reaches_the_seam(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        runner = FakeRunner(success_result(), model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=integration)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        # A valid checkpoint means the missing-checkpoint seam is never entered.
        self.assertEqual(len(launcher.calls), 0)
        self.assertNotIn(result.stopped, (REASON_TURNOVER_LAUNCHED, REASON_TURNOVER_RECORDED))
        self.assertEqual(result.checkpoint_id, "cp-1")

    def test_ordinary_failure_keeps_existing_no_checkpoint_pause(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        runner = FakeRunner(
            failed_result(stderr="Traceback: build failed with a normal error"),
            model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=integration)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        # No exhaustion signal -> no turnover, existing terminal behaviour intact.
        self.assertEqual(len(launcher.calls), 0)
        self.assertEqual(result.stopped, "no_valid_checkpoint")
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)

    def test_ambiguous_limit_wording_keeps_existing_pause(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        # Limit-LOOKING wording without the exact phrase -> AMBIGUOUS -> no launch.
        runner = FakeRunner(
            failed_result(stderr="Error 429: you may be approaching a rate limit"),
            model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=integration)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(len(launcher.calls), 0)
        self.assertEqual(result.stopped, "no_valid_checkpoint")

    def test_absent_integration_leaves_path_unchanged(self) -> None:
        # The production default before wiring: no integration -> byte-for-byte the
        # existing no_valid_checkpoint pause on the exact same exhaustion input.
        runner = FakeRunner(failed_result(stderr=FABLE_LIMIT_MESSAGE),
                            model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=None)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, "no_valid_checkpoint")
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)


class ModeGatingTests(LoopSeamTestBase):
    def test_default_authorization_records_intent_and_does_not_launch(self) -> None:
        # Default authorize = fail-closed (no runnable mode auto-redispatches):
        # a confirmed exhaustion is RECORDED and surfaced, NOT auto-run.
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller)  # default gate
        runner = FakeRunner(failed_result(stderr=FABLE_LIMIT_MESSAGE),
                            model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=integration)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        # Triggered but NOT actuated: no successor launched, supervised-mode /
        # LIMITED-AUTO-off approval semantics are not bypassed.
        self.assertEqual(len(launcher.calls), 0)
        self.assertEqual(result.stopped, REASON_TURNOVER_RECORDED)
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)

    def test_authorized_but_no_channel_records_intent(self) -> None:
        # Authorized, but no actuation channel wired (production SHADOW-ONLY):
        # still record-intent-only, never a launch.
        integration = WorkerTurnoverIntegration(controller=None, authorize=_authorized)
        runner = FakeRunner(failed_result(stderr=FABLE_LIMIT_MESSAGE),
                            model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=integration)
        self.at_preflight()

        result = loop.run_cycle("do the unit", cycle=1)

        self.assertEqual(result.stopped, REASON_TURNOVER_RECORDED)
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)


# --------------------------------------------------------------------------
# Integration-object tests: classification, exactly-once dedup, gating precision
# --------------------------------------------------------------------------


class IntegrationEvaluateTests(unittest.TestCase):
    def _config(self):
        return lp.LoopConfig(mode="supervised", task_id="M0-T054", stage="phase4",
                             max_cycles=4)

    def test_exact_message_triggers_and_actuates_worker_layer(self) -> None:
        controller, launcher, audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        rr = failed_result(stderr=FABLE_LIMIT_MESSAGE)
        decision = integration.evaluate(
            rr, current_model="claude-fable-5", config=self._config(),
            run_id="run-x", cycle=1, safe_checkpoint_id="cp-safe")

        self.assertTrue(decision.triggered)
        self.assertTrue(decision.actuated)
        self.assertEqual(decision.reason_code, REASON_TURNOVER_LAUNCHED)
        self.assertEqual(len(launcher.calls), 1)
        self.assertEqual(launcher.calls[0].layer, TurnoverLayer.WORKER)
        self.assertEqual(launcher.calls[0].safe_checkpoint_id, "cp-safe")
        self.assertEqual(len(audit.launched_records()), 1)

    def test_duplicate_exhaustion_event_is_suppressed(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        rr = failed_result(stderr=FABLE_LIMIT_MESSAGE)
        kwargs = dict(current_model="claude-fable-5", config=self._config(),
                      run_id="run-x", cycle=7, safe_checkpoint_id="cp-safe")

        first = integration.evaluate(rr, **kwargs)
        second = integration.evaluate(rr, **kwargs)  # same run_id+cycle => same event id

        self.assertTrue(first.actuated)
        self.assertFalse(second.actuated)
        self.assertEqual(second.outcome.status, TurnoverStatus.SUPPRESSED_DUPLICATE)
        self.assertEqual(len(launcher.calls), 1)  # exactly once

    def test_not_exhausted_result_does_not_trigger(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        rr = failed_result(stderr="ordinary compiler error: undefined symbol")
        decision = integration.evaluate(
            rr, current_model="claude-fable-5", config=self._config(),
            run_id="run-x", cycle=1)

        self.assertFalse(decision.triggered)
        self.assertEqual(len(launcher.calls), 0)

    def test_success_exit_with_message_is_ambiguous_not_triggered(self) -> None:
        # A success exit (0) co-occurring with the phrase is a contradiction the
        # classifier fails closed on: never a turnover.
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        rr = failed_result(stderr=FABLE_LIMIT_MESSAGE, returncode=0)
        decision = integration.evaluate(
            rr, current_model="claude-fable-5", config=self._config(),
            run_id="run-x", cycle=1)

        self.assertFalse(decision.triggered)
        self.assertEqual(len(launcher.calls), 0)

    def test_unauthorized_records_intent_without_touching_controller(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller)  # default gate
        rr = failed_result(stderr=FABLE_LIMIT_MESSAGE)
        decision = integration.evaluate(
            rr, current_model="claude-fable-5", config=self._config(),
            run_id="run-x", cycle=1)

        self.assertTrue(decision.triggered)
        self.assertFalse(decision.actuated)
        self.assertEqual(decision.reason_code, REASON_TURNOVER_RECORDED)
        self.assertEqual(len(launcher.calls), 0)


if __name__ == "__main__":
    unittest.main()
