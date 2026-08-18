#!/usr/bin/env python3
"""M0-T056 (R595): deterministic tests for the production turnover ACTUATION channels.

Qualifying evidence (supervisor-freeze §2, AD-093): the reproduced provider incident
D-010 source-028 / R289 (Fable 5 hard-stopped at its weekly usage limit and the
built-in fallbackModel did NOT auto-switch), plus the owner's R595 activation
authorization (D-010 source-030) and build directive (source-031). M0-T056 takes the
accepted M0-T054 turnover MECHANISM live: (a) an orchestrator-layer watchdog that runs
OUTSIDE the Claude session and auto-launches exactly one opus-4-8 successor on a
grounded orchestrator quota hard stop, and (b) a worker-layer actuation predicate that,
when the owner authorizes it, redispatches the same bounded unit on opus-4-8 exactly
once through the frozen controller.

Every test is deterministic and runs WITHOUT a live provider, a real Claude/Codex
process, a config change, or the network: the launcher is driven through an INJECTED
FAKE command-runner that records the invocation and returns a synthetic result; the
lock/audit adapters run against temp dirs. These tests cover AS-1..AS-4 and AS-6 (the
real AS-5 is the owner-run isolated live proof, per the M0-T056 runbook). The M0-T054
controller/adapters/detection are REUSED UNCHANGED.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from typing import Any

from tools.agent_supervisor import cli
from tools.agent_supervisor import state_machine as sm
from tools.agent_supervisor.audit_log import AuditLog
from tools.agent_supervisor.claude_runner import RunResult
from tools.agent_supervisor.loop import LoopConfig
from tools.agent_supervisor.locking import probe_process
from tools.agent_supervisor.model_turnover import ExhaustionClassification
from tools.agent_supervisor.recovery import CHILD_PROCESSES_KEY
from tools.agent_supervisor.turnover_adapters import (
    CommandRunResult,
    SuccessorInvocation,
)
from tools.agent_supervisor.turnover_controller import (
    ALLOWED_SUCCESSOR_EFFORT,
    ALLOWED_SUCCESSOR_MODEL_ID,
    TurnoverLayer,
    TurnoverStatus,
)
from tools.agent_supervisor.worker_turnover import (
    ACTUATION_AUTHORIZATION_ATTR,
    default_actuation_authorization,
)
# Reuse the proven assembled-loop harness so the M0-T060 containment-gate test
# drives one REAL run_cycle through the state machine (non-vacuous).
from tools.test_agent_supervisor_turnover_integration import (  # noqa: E402
    LoopSeamTestBase,
    FakeRunner as LoopFakeRunner,
    checkpoint as loop_checkpoint,
)

# The exact Fable weekly-limit hard-stop message (D-010 source-028 / R289).
FABLE_LIMIT_MESSAGE = (
    "You've reached your Fable 5 limit. Run /usage-credits to continue or switch "
    "models with /model.")

# A FIXED orchestrator relaunch argv head (argv-safety-checked by the launcher).
ORCH_PREFIX = ("python", "-m", "tools.agent_supervisor", "start")


def _tmpdir(case: unittest.TestCase) -> Path:
    holder = tempfile.TemporaryDirectory()
    case.addCleanup(holder.cleanup)
    return Path(holder.name)


class RecordingRunner:
    """Injected fake command-runner: records each invocation, spawns NOTHING."""

    def __init__(self, *, started: bool = True, available: bool = True,
                 model_id: str = ALLOWED_SUCCESSOR_MODEL_ID) -> None:
        self.started = started
        self.available = available
        self.model_id = model_id
        self.invocations: list[SuccessorInvocation] = []

    def __call__(self, invocation: SuccessorInvocation) -> CommandRunResult:
        self.invocations.append(invocation)
        return CommandRunResult(
            started=self.started, available=self.available,
            successor_id=f"successor-{len(self.invocations)}",
            model_id=self.model_id, detail="fake")


class FakeJournal:
    """A dict-backed journal exposing only get_state/set_state (no survivor by default)."""

    def __init__(self, state: dict[str, Any] | None = None) -> None:
        self._state = dict(state or {})

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value


def _job_object_ok() -> tuple[bool, str, str]:
    return True, "job_object", "test stub: host default containment is job_object"


def _not_job_object() -> tuple[bool, str, str]:
    return False, "process_group", "test stub: host default containment is process_group"


def _audit(case: unittest.TestCase) -> AuditLog:
    return AuditLog(_tmpdir(case) / "audit.log")


# --------------------------------------------------------------------------
# AS-1: orchestrator-layer watchdog (exactly-once, loads handoff + checkpoint,
# audit-linked). Runs OUTSIDE the Claude session.
# --------------------------------------------------------------------------


class OrchestratorWatchdogTests(unittest.TestCase):
    def setUp(self) -> None:
        # A FIXED checkout so a repeated detection yields the SAME event id (the
        # dedup key is derived from (signal, checkout)); a fresh dir per call would
        # defeat the exactly-once test for the wrong reason.
        self._checkout = str(_tmpdir(self))

    def _run(self, runner: RecordingRunner, journal: FakeJournal, audit: AuditLog,
             *, signal: str = FABLE_LIMIT_MESSAGE,
             containment=_job_object_ok, handoff: str = "handoff-digest-abc",
             checkpoint: str = "cp-safe-1") -> dict[str, Any]:
        return cli.run_orchestrator_watchdog(
            signal_text=signal, journal=journal, audit=audit,
            checkout=self._checkout, orchestrator_argv_prefix=ORCH_PREFIX,
            command_runner=runner, handoff_reference=handoff,
            safe_checkpoint_id=checkpoint, current_model="claude-fable-5",
            containment_check=containment)

    def test_grounded_exhaustion_launches_exactly_one_opus_successor(self) -> None:
        runner, journal, audit = RecordingRunner(), FakeJournal(), _audit(self)
        result = self._run(runner, journal, audit)

        self.assertEqual(result["classification"],
                         ExhaustionClassification.FABLE_EXHAUSTED.value)
        self.assertTrue(result["launched"])
        self.assertEqual(result["successor_model_id"], ALLOWED_SUCCESSOR_MODEL_ID)
        self.assertEqual(len(runner.invocations), 1)
        # ORCHESTRATOR layer, opus-4-8/xhigh pin, loads handoff + safe checkpoint.
        inv = runner.invocations[0]
        self.assertEqual(inv.layer, TurnoverLayer.ORCHESTRATOR.value)
        self.assertEqual(inv.model_id, ALLOWED_SUCCESSOR_MODEL_ID)
        self.assertEqual(inv.effort, ALLOWED_SUCCESSOR_EFFORT)
        self.assertEqual(inv.handoff_reference, "handoff-digest-abc")
        self.assertEqual(inv.safe_checkpoint_id, "cp-safe-1")
        # Audit-linked: a launched record is written and its id surfaced.
        self.assertTrue(result["audit_record_id"])

    def test_second_detection_of_same_exhaustion_launches_nothing(self) -> None:
        runner, journal, audit = RecordingRunner(), FakeJournal(), _audit(self)
        first = self._run(runner, journal, audit)
        second = self._run(runner, journal, audit)  # SAME signal + checkout state

        self.assertTrue(first["launched"])
        self.assertFalse(second["launched"])
        self.assertEqual(second["status"], TurnoverStatus.SUPPRESSED_DUPLICATE.value)
        # Exactly once across the two detections.
        self.assertEqual(len(runner.invocations), 1)

    def test_opus_argv_carries_orchestrator_role_and_pin(self) -> None:
        runner, journal, audit = RecordingRunner(), FakeJournal(), _audit(self)
        self._run(runner, journal, audit)
        argv = list(runner.invocations[0].argv)
        self.assertIn("--session-role", argv)
        self.assertIn("orchestrator", argv)
        self.assertIn("--expected-worker-model", argv)
        self.assertIn(ALLOWED_SUCCESSOR_MODEL_ID, argv)


# --------------------------------------------------------------------------
# AS-3: fail-closed. NOT_EXHAUSTED / AMBIGUOUS / unreadable never actuate.
# --------------------------------------------------------------------------


class FailClosedTests(unittest.TestCase):
    def _run(self, signal: str, containment=_job_object_ok) -> tuple[dict, RecordingRunner]:
        runner = RecordingRunner()
        result = cli.run_orchestrator_watchdog(
            signal_text=signal, journal=FakeJournal(), audit=_audit(self),
            checkout=str(_tmpdir(self)), orchestrator_argv_prefix=ORCH_PREFIX,
            command_runner=runner, containment_check=containment)
        return result, runner

    def test_not_exhausted_signal_never_launches(self) -> None:
        result, runner = self._run("permission denied: EACCES on /repo/file")
        self.assertEqual(result["classification"],
                         ExhaustionClassification.NOT_EXHAUSTED.value)
        self.assertFalse(result["launched"])
        self.assertTrue(result["refused"])
        self.assertEqual(len(runner.invocations), 0)

    def test_ambiguous_limit_wording_never_launches(self) -> None:
        # A bare "limit" mention without the exact phrase fails closed to AMBIGUOUS.
        result, runner = self._run("some job hit a rate limit (429), retrying later")
        self.assertEqual(result["classification"],
                         ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED.value)
        self.assertFalse(result["launched"])
        self.assertEqual(len(runner.invocations), 0)

    def test_empty_signal_never_launches(self) -> None:
        # An empty capture carries no grounded exhaustion signal, so it is never a
        # turnover (here NOT_EXHAUSTED on the failure exit); the invariant that
        # matters is fail-closed: nothing is launched and the refusal is recorded.
        result, runner = self._run("")
        self.assertIn(result["classification"],
                      {ExhaustionClassification.NOT_EXHAUSTED.value,
                       ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED.value})
        self.assertFalse(result["launched"])
        self.assertTrue(result["refused"])
        self.assertEqual(len(runner.invocations), 0)


# --------------------------------------------------------------------------
# AS-4: no duplicate workers (surviving recorded child) + C1 containment gate.
# --------------------------------------------------------------------------


class NoDuplicateWorkerTests(unittest.TestCase):
    def test_surviving_recorded_child_refuses_launch(self) -> None:
        # Record THIS live process as a child with its real start token: the
        # M0-T053 child-accounting probe reports it surviving -> BLOCKED_SURVIVOR.
        pid = os.getpid()
        token = probe_process(pid).start_token
        journal = FakeJournal({CHILD_PROCESSES_KEY: [
            {"pid": pid, "role": "worker", "start_token": token}]})
        runner = RecordingRunner()
        result = cli.run_orchestrator_watchdog(
            signal_text=FABLE_LIMIT_MESSAGE, journal=journal, audit=_audit(self),
            checkout=str(_tmpdir(self)), orchestrator_argv_prefix=ORCH_PREFIX,
            command_runner=runner, containment_check=_job_object_ok)
        self.assertFalse(result["launched"])
        self.assertEqual(result["status"], TurnoverStatus.BLOCKED_SURVIVOR.value)
        self.assertEqual(len(runner.invocations), 0)

    def test_c1_containment_gate_refuses_on_non_job_object_host(self) -> None:
        runner = RecordingRunner()
        result = cli.run_orchestrator_watchdog(
            signal_text=FABLE_LIMIT_MESSAGE, journal=FakeJournal(), audit=_audit(self),
            checkout=str(_tmpdir(self)), orchestrator_argv_prefix=ORCH_PREFIX,
            command_runner=runner, containment_check=_not_job_object)
        self.assertFalse(result["launched"])
        self.assertTrue(result["refused"])
        self.assertEqual(result["containment_kind"], "process_group")
        self.assertEqual(len(runner.invocations), 0)


# --------------------------------------------------------------------------
# AS-2: worker-layer actuation predicate + record-intent-only when unauthorized.
# --------------------------------------------------------------------------


class WorkerActuationPredicateTests(unittest.TestCase):
    def test_predicate_true_only_with_explicit_authorization(self) -> None:
        authorized = LoopConfig(mode="supervised", task_id="M0-T056", stage="build",
                                turnover_actuation_authorized=True)
        self.assertTrue(default_actuation_authorization(authorized))

    def test_default_config_is_unauthorized_byte_identical(self) -> None:
        # Every runnable mode defaults to unauthorized: no mode auto-actuates.
        for mode in ("shadow", "supervised"):
            cfg = LoopConfig(mode=mode, task_id="M0-T056", stage="build")
            self.assertFalse(default_actuation_authorization(cfg),
                             f"{mode} must not auto-authorize actuation")

    def test_non_true_values_fail_closed(self) -> None:
        class Cfg:
            pass
        cfg = Cfg()
        # Absent attribute -> False.
        self.assertFalse(default_actuation_authorization(cfg))
        # Truthy-but-not-True (e.g. 1, "yes") is NOT authorization.
        setattr(cfg, ACTUATION_AUTHORIZATION_ATTR, 1)
        self.assertFalse(default_actuation_authorization(cfg))
        setattr(cfg, ACTUATION_AUTHORIZATION_ATTR, "true")
        self.assertFalse(default_actuation_authorization(cfg))
        setattr(cfg, ACTUATION_AUTHORIZATION_ATTR, True)
        self.assertTrue(default_actuation_authorization(cfg))


class WorkerActuationChannelBuildTests(unittest.TestCase):
    def _args(self, *, authorize: bool) -> Any:
        class Args:
            authorize_turnover_actuation = authorize
            runtime_base = None
        return Args()

    def test_unauthorized_returns_no_channel_record_intent(self) -> None:
        controller, report = cli._build_worker_actuation_channel(
            args=self._args(authorize=False), journal=FakeJournal(),
            audit=_audit(self), checkout=_tmpdir(self),
            claude_executable="/opt/claude", max_turns=12, unit_timeout=900.0)
        self.assertIsNone(controller)
        self.assertFalse(report["authorized"])
        self.assertFalse(report["wired"])

    def test_authorized_but_non_job_object_host_refuses_channel(self) -> None:
        # On this POSIX sandbox the real C1 gate reports process_group, not
        # job_object, so even an authorized run gets NO live channel (fail-closed).
        controller, report = cli._build_worker_actuation_channel(
            args=self._args(authorize=True), journal=FakeJournal(),
            audit=_audit(self), checkout=_tmpdir(self),
            claude_executable="/opt/claude", max_turns=12, unit_timeout=900.0)
        contained, _kind, _detail = cli.containment_precondition()
        if contained:  # a job_object host: the channel IS wired
            self.assertIsNotNone(controller)
            self.assertTrue(report["wired"])
        else:  # POSIX / non-job_object: refused, record-intent-only
            self.assertIsNone(controller)
            self.assertTrue(report["authorized"])
            self.assertFalse(report["wired"])
            self.assertFalse(report["containment_ok"])


# --------------------------------------------------------------------------
# AS-6: no other hold moved / the loop cannot self-approve. The full diff-level
# demonstration is in the producer report; these lock the code-level invariants.
# --------------------------------------------------------------------------


class NoOtherHoldMovedTests(unittest.TestCase):
    def test_successor_model_is_hard_pinned_opus_4_8(self) -> None:
        # The successor is never caller-selectable; the pin is the frozen constant.
        self.assertEqual(ALLOWED_SUCCESSOR_MODEL_ID, "claude-opus-4-8")
        self.assertEqual(ALLOWED_SUCCESSOR_EFFORT, "xhigh")

    def test_actuation_requires_explicit_owner_flag_not_a_mode(self) -> None:
        # No runnable mode, by itself, authorizes actuation: only the explicit
        # per-run flag does. (Producer != approver: the loop cannot self-authorize.)
        for mode in ("shadow", "supervised"):
            cfg = LoopConfig(mode=mode, task_id="M0-T056", stage="s")
            self.assertFalse(default_actuation_authorization(cfg))

    def test_limited_auto_still_refused_by_name(self) -> None:
        # The LIMITED-AUTO hold is untouched: constructing a limited-auto LoopConfig
        # still raises before any actuation could be considered.
        with self.assertRaises(Exception):
            LoopConfig(mode="limited-auto", task_id="M0-T056", stage="s")


# --------------------------------------------------------------------------
# M0-T060 fold-in: the achieved-job_object cycle must be VERIFIED in-job. Direct,
# non-vacuous regression over the loop.py `containment_unverified` branch: one
# REAL run_cycle whose RunResult reports job_object containment but an UNVERIFIED
# in-job membership must PAUSE; a verified (or default) cycle must NOT trip it.
# --------------------------------------------------------------------------


class ContainmentVerifiedGateTests(LoopSeamTestBase):
    def _result(self, **overrides) -> RunResult:
        # A valid checkpoint so the cycle passes the no-checkpoint/turnover seam and
        # REACHES the achieved-containment gate; job_object so it is the OTHERWISE-OK
        # path that would proceed but for verified_in_job.
        data = dict(argv=("fake",), returncode=0, duration_seconds=0.1,
                    session_id="sess-1", checkpoint=loop_checkpoint(),
                    containment="job_object")
        data.update(overrides)
        return RunResult(**data)

    def test_unverified_job_object_cycle_stops_containment_unverified(self) -> None:
        runner = LoopFakeRunner(self._result(containment_verified_in_job=False),
                                model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=None)
        self.at_preflight()
        result = loop.run_cycle("do the unit", cycle=1)
        # The cycle fails closed on the unverified in-job membership and lands in
        # the safe PAUSED_RECOVERY state (NOT the ordinary CHECKPOINT_RECEIVED path).
        self.assertEqual(result.stopped, "containment_unverified")
        self.assertEqual(result.reached_state, sm.PAUSED_RECOVERY)

    def test_default_verified_job_object_cycle_does_not_trip(self) -> None:
        # verified_in_job defaults True on a hand-built RunResult -> the branch is
        # NOT tripped; the cycle proceeds past it (freeze-safe backward-compat).
        runner = LoopFakeRunner(self._result(), model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=None)
        self.at_preflight()
        result = loop.run_cycle("do the unit", cycle=1)
        self.assertNotEqual(result.stopped, "containment_unverified")

    def test_explicit_verified_true_job_object_cycle_does_not_trip(self) -> None:
        runner = LoopFakeRunner(self._result(containment_verified_in_job=True),
                                model="claude-fable-5")
        loop = self.build(runner=runner, worker_turnover=None)
        self.at_preflight()
        result = loop.run_cycle("do the unit", cycle=1)
        self.assertNotEqual(result.stopped, "containment_unverified")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
