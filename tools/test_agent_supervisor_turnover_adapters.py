#!/usr/bin/env python3
"""M0-T054: deterministic tests for the Fable->Opus turnover REAL-DEPENDENCY adapters.

Qualifying evidence (supervisor-freeze §2, AD-093): the reproduced provider
incident D-010 source-028 / R289 - Fable 5 hard-stopped at its weekly usage limit
with the exact message "You've reached your Fable 5 limit. Run /usage-credits to
continue or switch models with /model." and the built-in fallbackModel did NOT
auto-switch. This third increment binds the increment-2 actuation policy's
injected Protocols to the supervisor's ACTUAL infrastructure - the
single-instance checkout lock, the hash-chained audit log, and the confirmed
worker launch surface.

Every test is deterministic and runs WITHOUT a live provider, a real
Claude/Codex process, a config change, or the network: the lock/audit adapters
run against temp dirs and the launcher is driven through an INJECTED FAKE
command-runner that records the argv and returns a synthetic result. The
end-to-end test wires a REAL `TurnoverController` to these real adapters (fake
runner) and drives one FABLE_EXHAUSTED verdict to LAUNCHED_SUCCESSOR, asserting
exactly one launch, the opus-4.8/xhigh pin, the Fable->Opus audit link, and
idempotency on a repeated event id.
"""
from __future__ import annotations

import datetime as _dt
import os
import tempfile
import unittest
from pathlib import Path

from tools.agent_supervisor.audit_log import AuditLog
from tools.agent_supervisor.locking import SingleInstanceLock
from tools.agent_supervisor.model_turnover import TurnoverEvidence, classify_exhaustion
from tools.agent_supervisor.turnover_adapters import (
    ACTIONED_MARKER_EVENT_TYPE,
    CommandRunResult,
    HashChainedAuditSink,
    SingleInstanceContinuationLock,
    SuccessorInvocation,
    SuccessorLaunchTargets,
    SupervisorIdentity,
    SupervisorLauncher,
    make_subprocess_command_runner,
)
from tools.agent_supervisor.turnover_controller import (
    ALLOWED_SUCCESSOR_EFFORT,
    ApprovedSuccessor,
    LaunchRequest,
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

def _tmpdir(case: unittest.TestCase) -> Path:
    holder = tempfile.TemporaryDirectory()
    case.addCleanup(holder.cleanup)
    return Path(holder.name)


def _adjacent(argv, flag, value) -> bool:
    """True when `flag` is immediately followed by `value` in argv."""
    tokens = list(argv)
    for index, token in enumerate(tokens[:-1]):
        if token == flag and tokens[index + 1] == value:
            return True
    return False


# --------------------------------------------------------------------------
# Fake command-runner (records the invocation, spawns NOTHING)
# --------------------------------------------------------------------------


class RecordingRunner:
    """Injected fake: records each `SuccessorInvocation` and returns a synthetic
    result. No subprocess is ever started."""

    def __init__(self, *, available: bool = True, started: bool = True,
                 model_id: str = APPROVED_SUCCESSOR, detail: str = "",
                 raises: bool = False) -> None:
        self.available = available
        self.started = started
        self.model_id = model_id
        self.detail = detail
        self.raises = raises
        self.invocations: list[SuccessorInvocation] = []

    def __call__(self, invocation: SuccessorInvocation) -> CommandRunResult:
        self.invocations.append(invocation)
        if self.raises:
            raise RuntimeError("synthetic launcher failure")
        n = len(self.invocations)
        if not self.available or not self.started:
            return CommandRunResult(started=self.started, available=self.available,
                                    detail=self.detail or "opus unavailable")
        return CommandRunResult(started=True, available=True,
                                successor_id=f"opus-succ-{n}", model_id=self.model_id,
                                detail="synthetic start")


def _worker_targets() -> SuccessorLaunchTargets:
    return SuccessorLaunchTargets(
        checkout="/checkout/x", claude_executable="/opt/claude/claude")


def _orchestrator_targets() -> SuccessorLaunchTargets:
    return SuccessorLaunchTargets(
        checkout="/checkout/x",
        orchestrator_argv_prefix=("python", "-m", "tools.agent_supervisor.cli", "start"))


def _request(layer: TurnoverLayer, *, model_id: str = APPROVED_SUCCESSOR,
             effort: str = ALLOWED_SUCCESSOR_EFFORT, event_id: str = "evt-1") -> LaunchRequest:
    return LaunchRequest(
        layer=layer, task_id="M0-T054", event_id=event_id, model_id=model_id, effort=effort,
        handoff_reference="handoff://durable/ref-1", safe_checkpoint_id="ckpt-42",
        failed_fable_execution_id="fable-exec-abc")


# --------------------------------------------------------------------------
# ContinuationLock adapter over the real SingleInstanceLock
# --------------------------------------------------------------------------


class ContinuationLockAdapterTests(unittest.TestCase):
    def test_acquire_then_contention_returns_false(self) -> None:
        runtime = _tmpdir(self)
        first = SingleInstanceContinuationLock(
            SingleInstanceLock(runtime, checkout_key="ck", controller_version="v"))
        # A distinct pid so the second lock sees a FOREIGN owner (the first lock's
        # recorded pid is this live test process, so it is never stale).
        second = SingleInstanceContinuationLock(
            SingleInstanceLock(runtime, checkout_key="ck", controller_version="v",
                               pid=os.getpid() + 1))

        self.assertTrue(first.acquire())
        self.assertFalse(second.acquire())  # contention -> False, never raises

    def test_release_frees_the_lock_for_a_new_instance(self) -> None:
        runtime = _tmpdir(self)
        first = SingleInstanceContinuationLock(
            SingleInstanceLock(runtime, checkout_key="ck", controller_version="v"))
        self.assertTrue(first.acquire())
        first.release()
        second = SingleInstanceContinuationLock(
            SingleInstanceLock(runtime, checkout_key="ck", controller_version="v",
                               pid=os.getpid() + 1))
        self.assertTrue(second.acquire())


# --------------------------------------------------------------------------
# AuditSink adapter over the real hash-chained audit log
# --------------------------------------------------------------------------


class AuditSinkAdapterTests(unittest.TestCase):
    def _sink(self, path: Path) -> HashChainedAuditSink:
        return HashChainedAuditSink(AuditLog(path, fsync=False))

    def test_append_returns_id_and_dedup_lifecycle(self) -> None:
        path = _tmpdir(self) / "audit.jsonl"
        sink = self._sink(path)

        self.assertFalse(sink.already_actioned("evt-1"))
        record_id = sink.append(
            {"kind": "fable_to_opus_turnover", "event_id": "evt-1",
             "link": {"stopped_fable_execution_id": "fable-exec-abc",
                      "opus_successor_id": "opus-succ-1"}})
        self.assertTrue(record_id)  # a non-empty durable id (the chain digest)
        # append alone does NOT consume the dedup key.
        self.assertFalse(sink.already_actioned("evt-1"))
        sink.mark_actioned("evt-1")
        self.assertTrue(sink.already_actioned("evt-1"))
        # A different event is unaffected.
        self.assertFalse(sink.already_actioned("evt-2"))

    def test_dedup_is_durable_across_a_fresh_adapter(self) -> None:
        path = _tmpdir(self) / "audit.jsonl"
        self._sink(path).mark_actioned("evt-durable")
        # A brand-new adapter over a brand-new AuditLog on the SAME file still
        # sees the marker: the dedup lives in the durable chain, not in memory.
        fresh = HashChainedAuditSink(AuditLog(path, fsync=False))
        self.assertTrue(fresh.already_actioned("evt-durable"))
        self.assertFalse(fresh.already_actioned("evt-never"))

    def test_marker_uses_the_dedicated_event_type(self) -> None:
        path = _tmpdir(self) / "audit.jsonl"
        sink = self._sink(path)
        sink.mark_actioned("evt-1")
        log = AuditLog(path, fsync=False)
        markers = [r for r in log.read_all()
                   if r.get("event_type") == ACTIONED_MARKER_EVENT_TYPE]
        self.assertEqual(len(markers), 1)
        # The event id is stored ONLY as a digest, never in the clear.
        self.assertNotIn("evt-1", markers[0]["detail"].values())

    def test_fail_closed_when_the_chain_is_unreadable(self) -> None:
        path = _tmpdir(self) / "audit.jsonl"
        path.write_text("this is not valid jsonl\n", encoding="utf-8")
        log = AuditLog(path, fsync=False)
        self.assertIsNotNone(log.load_error)  # damaged: refuses to load
        sink = HashChainedAuditSink(log)
        # Fail closed: an unverifiable store reads as ALREADY actioned, so the
        # controller suppresses a turnover it cannot prove is new (no double-launch).
        self.assertTrue(sink.already_actioned("evt-anything"))


# --------------------------------------------------------------------------
# Identity adapter
# --------------------------------------------------------------------------


class IdentityAdapterTests(unittest.TestCase):
    def test_default_now_iso_is_aware_utc_and_ids_are_unique(self) -> None:
        identity = SupervisorIdentity()
        stamp = identity.now_iso()
        self.assertTrue(stamp.endswith("Z"))
        self.assertNotEqual(identity.new_audit_id(), identity.new_audit_id())

    def test_injected_clock_and_id_source_are_deterministic(self) -> None:
        fixed = _dt.datetime(2026, 8, 9, 12, 0, 0, tzinfo=_dt.timezone.utc)
        ids = iter(["id-a", "id-b"])
        identity = SupervisorIdentity(clock=lambda: fixed, id_source=lambda: next(ids))
        self.assertEqual(identity.now_iso(), "2026-08-09T12:00:00.000Z")
        self.assertEqual(identity.new_audit_id(), "id-a")
        self.assertEqual(identity.new_audit_id(), "id-b")


# --------------------------------------------------------------------------
# Launcher adapter (INJECTED fake command-runner; nothing spawns)
# --------------------------------------------------------------------------


class LauncherAdapterTests(unittest.TestCase):
    def test_worker_launches_the_approved_model_and_never_a_bare_default(self) -> None:
        # M0-T080 (D-023-R013). This test used to assert the launcher IGNORED the
        # request's model and pinned the hard-coded `ALLOWED_SUCCESSOR_MODEL_ID`.
        # That constant is gone: the model discipline MOVED UP a layer, where it
        # is stronger. `TurnoverController` now resolves the successor from the
        # OWNER-APPROVED, live-probed list and refuses any caller preference that
        # differs (see `ApprovedSuccessorControllerTests::test_a_caller_requesting_
        # a_different_model_is_refused_before_the_lock` in
        # test_agent_supervisor_turnover_live_seam.py, and the INVALID_MODEL_REFUSED
        # tests in the controller module), so what
        # reaches the launcher is already the approved id. The launcher's own duty
        # is to launch EXACTLY that id and to refuse a request that names none -
        # it has nothing to fall back to.
        runner = RecordingRunner()
        launcher = SupervisorLauncher(command_runner=runner, targets=_worker_targets())
        result = launcher.launch(_request(TurnoverLayer.WORKER,
                                          model_id=APPROVED_SUCCESSOR))

        self.assertTrue(result.available)
        self.assertEqual(result.model_id, APPROVED_SUCCESSOR)
        self.assertTrue(result.successor_id)

        self.assertEqual(len(runner.invocations), 1)
        invocation = runner.invocations[0]
        self.assertEqual(invocation.model_id, APPROVED_SUCCESSOR)
        self.assertEqual(invocation.effort, ALLOWED_SUCCESSOR_EFFORT)
        # The confirmed worker argv carries --model <approved id> ...
        self.assertTrue(_adjacent(invocation.argv, "--model", APPROVED_SUCCESSOR))
        # ... and never a hard-denied effort flag.
        self.assertFalse(any(t.startswith("--effort") or t.startswith("--reasoning-effort")
                             for t in invocation.argv))
        # Effort rides as invocation metadata / env, not as a CLI flag.
        self.assertEqual(invocation.env.get("SUPERVISOR_SUCCESSOR_EFFORT"),
                         ALLOWED_SUCCESSOR_EFFORT)

    def test_a_caller_supplied_effort_is_ignored_by_the_launcher(self) -> None:
        # M0-T080 correction U9, restoring the adversarial half of the removed
        # "never a caller model OR effort" test. The MODEL legitimately comes from
        # the request now (the controller resolved it from the owner-approved
        # list), but the EFFORT still cannot: D-004-R159 forbids protected config
        # from carrying an effort key at all, so no owner-approved source exists
        # for a caller to have consulted. An intermediate M0-T080 version made the
        # launcher read `request.effort or ALLOWED_SUCCESSOR_EFFORT`, silently
        # turning a launcher-level pin into a caller-supplied value.
        for smuggled in ("low", "medium", "high", "none"):
            with self.subTest(effort=smuggled):
                runner = RecordingRunner()
                launcher = SupervisorLauncher(command_runner=runner,
                                              targets=_worker_targets())
                result = launcher.launch(_request(TurnoverLayer.WORKER,
                                                  model_id=APPROVED_SUCCESSOR,
                                                  effort=smuggled))
                self.assertTrue(result.available)
                invocation = runner.invocations[0]
                self.assertEqual(invocation.effort, ALLOWED_SUCCESSOR_EFFORT)
                self.assertEqual(invocation.env.get("SUPERVISOR_SUCCESSOR_EFFORT"),
                                 ALLOWED_SUCCESSOR_EFFORT)
                # And it never reaches the argv in any form (R159 hard-deny).
                self.assertNotIn(smuggled, invocation.argv)
                self.assertFalse(any(t.startswith("--effort")
                                     or t.startswith("--reasoning-effort")
                                     for t in invocation.argv))

    def test_a_request_naming_no_model_is_refused_with_nothing_launched(self) -> None:
        # The replacement for "never a caller model": there is no default to fall
        # back to, so an unnamed model is a refusal rather than a quiet pin.
        for layer, targets in ((TurnoverLayer.WORKER, _worker_targets()),
                               (TurnoverLayer.ORCHESTRATOR, _orchestrator_targets())):
            with self.subTest(layer=layer.value):
                runner = RecordingRunner()
                launcher = SupervisorLauncher(command_runner=runner, targets=targets)
                result = launcher.launch(_request(layer, model_id=""))
                self.assertFalse(result.available)
                self.assertIn("no usable successor model", result.detail)
                self.assertEqual(len(runner.invocations), 0)

    def test_orchestrator_carries_the_approved_model_and_the_role(self) -> None:
        runner = RecordingRunner()
        launcher = SupervisorLauncher(command_runner=runner, targets=_orchestrator_targets())
        result = launcher.launch(_request(TurnoverLayer.ORCHESTRATOR,
                                          model_id=APPROVED_SUCCESSOR))

        self.assertTrue(result.available)
        invocation = runner.invocations[0]
        self.assertEqual(invocation.model_id, APPROVED_SUCCESSOR)
        self.assertEqual(invocation.effort, ALLOWED_SUCCESSOR_EFFORT)
        self.assertTrue(_adjacent(invocation.argv, "--expected-worker-model",
                                  APPROVED_SUCCESSOR))
        self.assertTrue(_adjacent(invocation.argv, "--session-role", "orchestrator"))
        self.assertNotIn("claude-fable-5", invocation.argv)

    def test_unavailable_runner_returns_available_false(self) -> None:
        runner = RecordingRunner(available=False, started=False)
        launcher = SupervisorLauncher(command_runner=runner, targets=_worker_targets())
        result = launcher.launch(_request(TurnoverLayer.WORKER))
        self.assertFalse(result.available)
        self.assertFalse(result.successor_id)

    def test_runner_exception_fails_closed(self) -> None:
        runner = RecordingRunner(raises=True)
        launcher = SupervisorLauncher(command_runner=runner, targets=_worker_targets())
        result = launcher.launch(_request(TurnoverLayer.WORKER))
        self.assertFalse(result.available)

    def test_runner_reporting_a_different_model_fails_closed(self) -> None:
        runner = RecordingRunner(model_id="claude-opus-5")
        launcher = SupervisorLauncher(command_runner=runner, targets=_worker_targets())
        result = launcher.launch(_request(TurnoverLayer.WORKER))
        self.assertFalse(result.available)

    def test_missing_worker_executable_fails_closed(self) -> None:
        runner = RecordingRunner()
        launcher = SupervisorLauncher(
            command_runner=runner, targets=SuccessorLaunchTargets(checkout="/c"))
        result = launcher.launch(_request(TurnoverLayer.WORKER))
        self.assertFalse(result.available)
        self.assertEqual(len(runner.invocations), 0)  # never reached the runner

    def test_subprocess_runner_factory_is_a_callable_seam(self) -> None:
        # The production seam is DEFINED (it uses process.run); we only assert it
        # is constructed as a callable here - it is never invoked, so nothing is
        # spawned.
        runner = make_subprocess_command_runner(new_successor_id=lambda: "id")
        self.assertTrue(callable(runner))


# --------------------------------------------------------------------------
# End-to-end: real controller + real adapters + fake runner
# --------------------------------------------------------------------------


class EndToEndWiringTests(unittest.TestCase):
    def _build(self, runner: RecordingRunner):
        base = _tmpdir(self)
        lock = SingleInstanceContinuationLock(
            SingleInstanceLock(base / "rt", checkout_key="ck", controller_version="v"))
        self.audit_log = AuditLog(base / "audit.jsonl", fsync=False)
        audit = HashChainedAuditSink(self.audit_log)
        launcher = SupervisorLauncher(command_runner=runner, targets=_worker_targets())
        controller = TurnoverController(
            launcher=launcher, lock=lock, audit=audit,
            identity=SupervisorIdentity(), survivor_detected=lambda _c: False, successor=_approved_successor)
        return controller

    def _context(self, event_id: str = "evt-e2e") -> TurnoverContext:
        return TurnoverContext(
            task_id="M0-T054", event_id=event_id,
            failed_fable_execution_id="fable-exec-abc", safe_checkpoint_id="ckpt-42",
            handoff_reference="handoff://durable/ref-1", layer=TurnoverLayer.WORKER)

    def test_fable_exhausted_drives_one_opus_launch_and_is_idempotent(self) -> None:
        runner = RecordingRunner()
        controller = self._build(runner)

        # REAL detection: the exact reproduced R289 weekly-limit message.
        verdict = classify_exhaustion(TurnoverEvidence(
            stderr="You've reached your Fable 5 limit. Run /usage-credits to continue "
                   "or switch models with /model.",
            exit_code=1, model_id="claude-fable-5"))
        self.assertTrue(verdict.should_turn_over)

        context = self._context()
        outcome = controller.execute(verdict, context)

        self.assertEqual(outcome.status, TurnoverStatus.LAUNCHED_SUCCESSOR)
        self.assertTrue(outcome.turned_over)
        self.assertEqual(outcome.model_id, APPROVED_SUCCESSOR)
        self.assertEqual(outcome.effort, ALLOWED_SUCCESSOR_EFFORT)

        # Exactly one launch, pinned to opus-4.8 in the confirmed worker argv.
        self.assertEqual(len(runner.invocations), 1)
        self.assertTrue(_adjacent(runner.invocations[0].argv, "--model",
                                  APPROVED_SUCCESSOR))

        # The durable audit chain carries the explicit Fable -> Opus link ...
        records = AuditLog(self.audit_log.path, fsync=False).read_all()
        links = [r for r in records if r.get("event_type") == "fable_to_opus_turnover"]
        self.assertEqual(len(links), 1)
        link = links[0]["detail"]["link"]
        self.assertEqual(link["stopped_fable_execution_id"], "fable-exec-abc")
        self.assertEqual(link["opus_successor_id"], outcome.successor_id)
        # ... and the whole chain still verifies.
        self.assertTrue(AuditLog(self.audit_log.path, fsync=False).verify_chain().ok)

        # Idempotency: a repeat of the SAME event id suppresses a second launch.
        repeat = controller.execute(verdict, self._context())
        self.assertEqual(repeat.status, TurnoverStatus.SUPPRESSED_DUPLICATE)
        self.assertEqual(len(runner.invocations), 1)  # still exactly one launch


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
