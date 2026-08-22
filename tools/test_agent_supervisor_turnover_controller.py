#!/usr/bin/env python3
"""M0-T054: deterministic tests for the Fable->Opus turnover ACTUATION policy.

Qualifying evidence (supervisor-freeze §2, AD-093): the reproduced provider
incident D-010 source-028 / R289 - Fable 5 hard-stopped at its weekly usage limit
with the exact message "You've reached your Fable 5 limit. Run /usage-credits to
continue or switch models with /model." and the built-in fallbackModel did NOT
auto-switch. This second increment adds the turnover ACTUATION policy on top of
the increment-1 detection classifier.

These tests pin the actuation CONTRACT with in-memory FAKE injected dependencies
(launcher / lock / audit / identity) - no live provider, no real process launch,
no config change, no network, no real I/O:

* only a confirmed FABLE_EXHAUSTED verdict launches, and it launches EXACTLY ONE
  successor on claude-opus-4-8 at xhigh effort (both orchestrator and worker
  layers, one code path);
* NOT_EXHAUSTED and AMBIGUOUS_FAIL_CLOSED never launch;
* the single-instance lock, dedup store, and post-launch mark_actioned together
  guarantee at most one successor per exhaustion event, idempotent under
  re-invocation with the same event id;
* a surviving Fable worker / competing orchestrator blocks the launch;
* an Opus-unavailable launcher result safe-stops with NO fallback model and
  releases the lock;
* any non-opus-4.8/xhigh request is refused;
* the audit record explicitly links the stopped Fable execution id -> the Opus
  successor id.
"""
from __future__ import annotations

import unittest
from typing import Any, Mapping

from tools.agent_supervisor.model_turnover import (
    ExhaustionClassification,
    ExhaustionVerdict,
)
from tools.agent_supervisor.turnover_controller import (
    ALLOWED_SUCCESSOR_EFFORT,
    ApprovedSuccessor,
    LaunchRequest,
    LaunchResult,
    TurnoverContext,
    TurnoverController,
    TurnoverLayer,
    TurnoverStatus,
)


# --------------------------------------------------------------------------
# M0-T080 (D-023-R013): the successor is no longer a module constant in the
# production code. `ALLOWED_SUCCESSOR_MODEL_ID = "claude-opus-4-8"` is GONE,
# because a model id living in the source is a selection the owner never
# approved and no launch probe ever proved. `TurnoverController` now takes an
# injected resolver that names the next OWNER-APPROVED, live-probed model, so
# these tests state the approved chain THEMSELVES and assert the launch used
# that id - a strictly stronger claim than "it equals the constant the code
# also reads", which could not fail even if the id were wrong.
# --------------------------------------------------------------------------

#: The owner-approved chain these tests pretend the protected config declares.
APPROVED_CHAIN: tuple[str, ...] = ("claude-fable-5", "claude-opus-4-8")
#: The entry after the exhausted Fable model - what the resolver must pick.
APPROVED_SUCCESSOR = "claude-opus-4-8"


def _approved_successor(_context: object) -> ApprovedSuccessor:
    """A `SuccessorResolver` standing in for the approved + live-probed selection."""
    return ApprovedSuccessor(
        model_id=APPROVED_SUCCESSOR, effort=ALLOWED_SUCCESSOR_EFFORT,
        probed_at_utc="2026-08-21T00:00:00+00:00",
        config_identity="test-config-identity", cli_version="test-cli-version")


# --------------------------------------------------------------------------
# In-memory fakes for every injected dependency
# --------------------------------------------------------------------------


class FakeLauncher:
    """Records every launch call and hands back a scripted result.

    `available` False models Opus 4.8 being unavailable. A monotonically numbered
    successor id makes a second (forbidden) launch trivially detectable.
    """

    def __init__(self, *, available: bool = True, model_id: str = APPROVED_SUCCESSOR,
                 successor_id: str | None = None, detail: str = "") -> None:
        self.available = available
        self.model_id = model_id
        self._forced_successor_id = successor_id
        self.detail = detail
        self.calls: list[LaunchRequest] = []

    def launch(self, request: LaunchRequest) -> LaunchResult:
        self.calls.append(request)
        if not self.available:
            return LaunchResult(available=False, detail=self.detail or "opus unavailable")
        successor_id = self._forced_successor_id or f"opus-successor-{len(self.calls)}"
        return LaunchResult(available=True, successor_id=successor_id,
                            model_id=self.model_id, detail="launched")


class FakeLock:
    """Single-instance lock. `held` True models a peer already holding it."""

    def __init__(self, *, held: bool = False) -> None:
        self._held_by_other = held
        self.acquired = False
        self.acquire_calls = 0
        self.release_calls = 0

    def acquire(self) -> bool:
        self.acquire_calls += 1
        if self._held_by_other:
            return False
        self.acquired = True
        return True

    def release(self) -> None:
        self.release_calls += 1
        self.acquired = False


class FakeAudit:
    """Append-only audit + dedup store. `mark_actioned` is the sole dedup
    consumer, so a launch is the only thing that suppresses a repeat event."""

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

    # -- test conveniences --
    def launched_records(self) -> list[dict[str, Any]]:
        return [r for r in self.records if r.get("kind") == "fable_to_opus_turnover"]


class FakeIdentity:
    """Deterministic clock + id source (never wall-clock or random)."""

    def __init__(self) -> None:
        self._n = 0

    def now_iso(self) -> str:
        return "2026-08-09T00:00:00Z"

    def new_audit_id(self) -> str:
        self._n += 1
        return f"audit-id-{self._n}"


def _no_survivor(_context: TurnoverContext) -> bool:
    return False


def _survivor_present(_context: TurnoverContext) -> bool:
    return True


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------

_EXHAUSTED = ExhaustionVerdict(
    ExhaustionClassification.FABLE_EXHAUSTED,
    "the exact Fable weekly-limit message is an unambiguous exhaustion signal")
_NOT_EXHAUSTED = ExhaustionVerdict(
    ExhaustionClassification.NOT_EXHAUSTED, "a clean success carries no exhaustion signal")
_AMBIGUOUS = ExhaustionVerdict(
    ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED, "insufficient evidence; fail closed")


def _context(layer: TurnoverLayer = TurnoverLayer.ORCHESTRATOR, *,
             event_id: str = "evt-1", **overrides: Any) -> TurnoverContext:
    base = dict(
        task_id="M0-T054",
        event_id=event_id,
        failed_fable_execution_id="fable-exec-abc",
        safe_checkpoint_id="ckpt-42",
        handoff_reference="handoff://durable/ref-1",
        layer=layer,
    )


    base.update(overrides)
    return TurnoverContext(**base)


def _controller(*, launcher: FakeLauncher | None = None, lock: FakeLock | None = None,
                audit: FakeAudit | None = None, survivor=_no_survivor):
    launcher = launcher or FakeLauncher()
    lock = lock or FakeLock()
    audit = audit or FakeAudit()
    controller = TurnoverController(
        launcher=launcher, lock=lock, audit=audit, identity=FakeIdentity(),
        survivor_detected=survivor, successor=_approved_successor)
    return controller, launcher, lock, audit


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


class LaunchOnExhaustionTests(unittest.TestCase):
    """A confirmed exhaustion launches exactly one opus-4.8/xhigh successor."""

    def test_orchestrator_layer_launches_exactly_one_opus_successor(self) -> None:
        controller, launcher, lock, audit = _controller()
        outcome = controller.execute(_EXHAUSTED, _context(TurnoverLayer.ORCHESTRATOR))

        self.assertEqual(outcome.status, TurnoverStatus.LAUNCHED_SUCCESSOR)
        self.assertTrue(outcome.turned_over)
        self.assertEqual(len(launcher.calls), 1)
        self.assertEqual(launcher.calls[0].layer, TurnoverLayer.ORCHESTRATOR)
        self.assertEqual(launcher.calls[0].model_id, APPROVED_SUCCESSOR)
        self.assertEqual(launcher.calls[0].effort, ALLOWED_SUCCESSOR_EFFORT)
        self.assertEqual(outcome.model_id, "claude-opus-4-8")
        self.assertEqual(outcome.effort, "xhigh")
        self.assertTrue(outcome.successor_id)
        self.assertEqual(lock.release_calls, 1)
        self.assertFalse(lock.acquired)

    def test_worker_layer_redispatches_once_from_safe_checkpoint(self) -> None:
        controller, launcher, lock, audit = _controller()
        ctx = _context(TurnoverLayer.WORKER)
        outcome = controller.execute(_EXHAUSTED, ctx)

        self.assertEqual(outcome.status, TurnoverStatus.LAUNCHED_SUCCESSOR)
        self.assertEqual(len(launcher.calls), 1)
        self.assertEqual(launcher.calls[0].layer, TurnoverLayer.WORKER)
        # The SAME bounded unit is redispatched from its safe checkpoint.
        self.assertEqual(launcher.calls[0].safe_checkpoint_id, "ckpt-42")
        self.assertEqual(launcher.calls[0].model_id, APPROVED_SUCCESSOR)
        self.assertEqual(outcome.safe_checkpoint_id, "ckpt-42")

    def test_launch_passes_handoff_reference(self) -> None:
        controller, launcher, _lock, _audit = _controller()
        controller.execute(_EXHAUSTED, _context())
        self.assertEqual(launcher.calls[0].handoff_reference, "handoff://durable/ref-1")


class NoTurnoverTests(unittest.TestCase):
    """Fail-closed: only FABLE_EXHAUSTED may turn over."""

    def test_not_exhausted_does_not_launch(self) -> None:
        controller, launcher, lock, audit = _controller()
        outcome = controller.execute(_NOT_EXHAUSTED, _context())
        self.assertEqual(outcome.status, TurnoverStatus.NO_TURNOVER)
        self.assertFalse(outcome.turned_over)
        self.assertEqual(launcher.calls, [])
        # The lock is never even acquired on the fail-closed path.
        self.assertEqual(lock.acquire_calls, 0)

    def test_ambiguous_fail_closed_does_not_launch(self) -> None:
        controller, launcher, lock, _audit = _controller()
        outcome = controller.execute(_AMBIGUOUS, _context())
        self.assertEqual(outcome.status, TurnoverStatus.NO_TURNOVER)
        self.assertEqual(launcher.calls, [])
        self.assertEqual(lock.acquire_calls, 0)


class LockTests(unittest.TestCase):
    """The single-instance lock prevents a second concurrent launch."""

    def test_lock_already_held_yields_no_second_launch(self) -> None:
        controller, launcher, lock, _audit = _controller(lock=FakeLock(held=True))
        outcome = controller.execute(_EXHAUSTED, _context())
        self.assertEqual(outcome.status, TurnoverStatus.ALREADY_IN_PROGRESS)
        self.assertEqual(launcher.calls, [])
        # A lock we never acquired is never released.
        self.assertEqual(lock.release_calls, 0)


class DuplicateEventTests(unittest.TestCase):
    """Duplicate exhaustion events are suppressed - exactly-once."""

    def test_same_event_id_twice_launches_only_once(self) -> None:
        audit = FakeAudit()
        # Two separate lock objects model two independent invocations that each
        # cleanly acquire+release; the dedup store is what suppresses the second.
        controller1, launcher1, _l1, _a = _controller(audit=audit)
        first = controller1.execute(_EXHAUSTED, _context(event_id="dup-evt"))

        controller2, launcher2, _l2, _a2 = _controller(
            launcher=launcher1, audit=audit)
        second = controller2.execute(_EXHAUSTED, _context(event_id="dup-evt"))

        self.assertEqual(first.status, TurnoverStatus.LAUNCHED_SUCCESSOR)
        self.assertEqual(second.status, TurnoverStatus.SUPPRESSED_DUPLICATE)
        # Exactly one launch across both invocations.
        self.assertEqual(len(launcher1.calls), 1)

    def test_idempotent_reinvocation_same_controller(self) -> None:
        """Invoking twice with the same event id yields exactly one successor."""
        controller, launcher, lock, audit = _controller()
        ctx = _context(event_id="idem-evt")
        first = controller.execute(_EXHAUSTED, ctx)
        second = controller.execute(_EXHAUSTED, ctx)

        self.assertEqual(first.status, TurnoverStatus.LAUNCHED_SUCCESSOR)
        self.assertEqual(second.status, TurnoverStatus.SUPPRESSED_DUPLICATE)
        self.assertEqual(len(launcher.calls), 1)
        self.assertEqual(len(audit.launched_records()), 1)
        # The lock was acquired and released on both invocations.
        self.assertEqual(lock.acquire_calls, 2)
        self.assertEqual(lock.release_calls, 2)


class SurvivorTests(unittest.TestCase):
    """A surviving peer blocks the launch and preserves evidence."""

    def test_surviving_child_blocks_launch(self) -> None:
        controller, launcher, lock, audit = _controller(survivor=_survivor_present)
        outcome = controller.execute(_EXHAUSTED, _context(event_id="surv-evt"))

        self.assertEqual(outcome.status, TurnoverStatus.BLOCKED_SURVIVOR)
        self.assertEqual(launcher.calls, [])
        self.assertTrue(outcome.audit_record_id)
        # Evidence preserved, dedup NOT consumed.
        self.assertFalse(audit.already_actioned("surv-evt"))
        self.assertEqual(lock.release_calls, 1)
        blocked = [r for r in audit.records if r.get("kind") == "turnover_blocked_survivor"]
        self.assertEqual(len(blocked), 1)


class OpusUnavailableTests(unittest.TestCase):
    """Opus 4.8 unavailable -> safe stop, no fallback model, lock released."""

    def test_opus_unavailable_safe_stops_without_fallback(self) -> None:
        launcher = FakeLauncher(available=False, detail="You've reached your Opus limit")
        controller, launcher, lock, audit = _controller(launcher=launcher)
        outcome = controller.execute(_EXHAUSTED, _context(event_id="unavail-evt"))

        self.assertEqual(outcome.status, TurnoverStatus.OPUS_UNAVAILABLE_SAFE_STOP)
        self.assertFalse(outcome.turned_over)
        self.assertEqual(outcome.successor_id, "")
        # Exactly one launch ATTEMPT, and NO retry with a different model.
        self.assertEqual(len(launcher.calls), 1)
        # dedup not consumed: a later attempt when Opus returns is still possible.
        self.assertFalse(audit.already_actioned("unavail-evt"))
        self.assertEqual(lock.release_calls, 1)
        self.assertFalse(lock.acquired)

    def test_launcher_swapping_a_different_model_fails_closed(self) -> None:
        """If the launcher reports a non-opus model, fail closed - never claim it."""
        launcher = FakeLauncher(model_id="claude-opus-5")
        controller, launcher, _lock, audit = _controller(launcher=launcher)
        outcome = controller.execute(_EXHAUSTED, _context(event_id="swap-evt"))
        self.assertEqual(outcome.status, TurnoverStatus.LAUNCH_FAILED_SAFE_STOP)
        self.assertFalse(audit.already_actioned("swap-evt"))


class ModelValidationTests(unittest.TestCase):
    """Only claude-opus-4-8/xhigh is an acceptable successor target."""

    def test_wrong_model_requested_is_refused(self) -> None:
        controller, launcher, lock, _audit = _controller()
        ctx = _context(event_id="wm-evt", requested_model="claude-opus-5")
        outcome = controller.execute(_EXHAUSTED, ctx)
        self.assertEqual(outcome.status, TurnoverStatus.INVALID_MODEL_REFUSED)
        self.assertEqual(launcher.calls, [])
        # Refused before the lock is touched (no side effects).
        self.assertEqual(lock.acquire_calls, 0)

    def test_wrong_effort_requested_is_refused(self) -> None:
        controller, launcher, _lock, _audit = _controller()
        ctx = _context(event_id="we-evt", requested_effort="high")
        outcome = controller.execute(_EXHAUSTED, ctx)
        self.assertEqual(outcome.status, TurnoverStatus.INVALID_MODEL_REFUSED)
        self.assertEqual(launcher.calls, [])


class AuditLinkTests(unittest.TestCase):
    """The audit record explicitly links stopped Fable id -> Opus successor id."""

    def test_audit_links_fable_execution_to_opus_successor(self) -> None:
        controller, launcher, _lock, audit = _controller()
        outcome = controller.execute(_EXHAUSTED, _context())

        launched = audit.launched_records()
        self.assertEqual(len(launched), 1)
        record = launched[0]
        self.assertEqual(record["link"]["stopped_fable_execution_id"], "fable-exec-abc")
        self.assertEqual(record["link"]["opus_successor_id"], outcome.successor_id)
        self.assertEqual(record["successor_model_id"], "claude-opus-4-8")
        self.assertEqual(record["successor_effort"], "xhigh")
        self.assertEqual(outcome.audit_record_id, record["audit_id"])

    def test_worker_layer_audit_also_links_both_ids(self) -> None:
        controller, launcher, _lock, audit = _controller()
        outcome = controller.execute(_EXHAUSTED, _context(TurnoverLayer.WORKER))
        record = audit.launched_records()[0]
        self.assertEqual(record["layer"], "worker")
        self.assertEqual(record["link"]["opus_successor_id"], outcome.successor_id)


class CheckpointRecordingTests(unittest.TestCase):
    """The exact last safe checkpoint id is carried into outcome and audit."""

    def test_safe_checkpoint_recorded(self) -> None:
        controller, _launcher, _lock, audit = _controller()
        outcome = controller.execute(_EXHAUSTED, _context(safe_checkpoint_id="ckpt-safe-99"))
        self.assertEqual(outcome.safe_checkpoint_id, "ckpt-safe-99")
        self.assertEqual(audit.launched_records()[0]["safe_checkpoint_id"], "ckpt-safe-99")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
