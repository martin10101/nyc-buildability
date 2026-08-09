#!/usr/bin/env python3
"""WORKER-layer Fable->Opus turnover INTEGRATION seam (M0-T054, fourth increment).

Qualifying evidence (supervisor-freeze §2, AD-093): a *reproduced provider
incident*. D-010 source-028 / R289: Fable 5 hit its weekly usage limit and hard-
stopped with the exact message

    You've reached your Fable 5 limit. Run /usage-credits to continue or switch
    models with /model.

and the CLI's built-in `fallbackModel` did NOT auto-switch. Increments 1-3
supplied the PURE detection classifier (`model_turnover.classify_exhaustion`),
the deterministic ACTUATION POLICY (`turnover_controller.TurnoverController`), and
the real infrastructure ADAPTERS (`turnover_adapters`). This fourth increment is
the MINIMAL, GATED glue that lets the WORKER-layer turnover actually fire from the
assembled loop: at the ONE seam where the loop is about to treat a missing/failed
worker result as a terminal `no_valid_checkpoint` stop, it first CLASSIFIES the
result for a grounded Fable exhaustion and, when confirmed AND the mode authorizes
an automatic redispatch, redispatches the SAME bounded unit on claude-opus-4-8
EXACTLY ONCE through the controller.

This module is strictly ADDITIVE (supervisor-freeze §1): it is a NEW file that
only COMPOSES the already-committed turnover stack; it edits no frozen module and
adds NO behavior to any non-exhaustion path. All effects flow through the injected
`TurnoverController` (built with fakes in tests, real adapters in production), so
it is fully exercised WITHOUT a live provider, a real process launch, a config
change, or the network.

The two governing rules restate the supervisor-freeze / AD-025 lane:

* FAIL-CLOSED: ONLY a confirmed `FABLE_EXHAUSTED` verdict
  (`verdict.should_turn_over` True) is ever `triggered`. `NOT_EXHAUSTED` and
  `AMBIGUOUS_FAIL_CLOSED` return `triggered=False`, so the caller leaves its
  existing terminal path byte-for-byte unchanged.
* MODE / AUTHORITY GATING: a confirmed exhaustion is turned over AUTOMATICALLY
  only when `authorize(config)` says the mode permits it. No mode in this build
  does (shadow forwards nothing; supervised holds every forward at
  WAIT_FOR_OWNER for owner approval; limited-auto is disabled BY NAME), so the
  default is RECORD-INTENT-ONLY: the intended turnover decision is returned and
  surfaced, and NO successor is launched. Automatic actuation is exercised only
  when an explicit owner-authorized channel is injected (the R595 activation
  path). This is what keeps the integration from bypassing supervised-mode
  approval or a LIMITED-AUTO-off state.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Mapping

from .model_turnover import TurnoverEvidence, classify_exhaustion
from .turnover_controller import (
    ExhaustionVerdict,
    TurnoverContext,
    TurnoverController,
    TurnoverLayer,
    TurnoverOutcome,
)

#: Reason code recorded on the owner-touch / journal transition when a confirmed
#: exhaustion was turned over automatically (an opus-4.8 successor was launched).
REASON_TURNOVER_LAUNCHED = "fable_exhaustion_worker_turnover"

#: Reason code recorded when a confirmed exhaustion could NOT be actuated - either
#: the mode did not authorize an automatic redispatch (record-intent-only), or the
#: authorized controller declined to launch (survivor / opus-unavailable / dup /
#: refused). In every one of these the loop keeps its existing safe PAUSE.
REASON_TURNOVER_RECORDED = "fable_exhaustion_turnover_recorded"


def default_actuation_authorization(config: Any) -> bool:
    """Fail-closed authorization: NO mode in this build auto-redispatches a worker.

    Automatic worker redispatch is a forward-equivalent action, and every runnable
    mode withholds that authority: shadow forwards nothing, supervised holds each
    forward at WAIT_FOR_OWNER for an owner approval bound to its digest, and
    limited-auto is refused by name before a `LoopConfig` can even be built. So
    this returns False unconditionally: a confirmed exhaustion is RECORDED and
    SURFACED, never silently auto-run. An owner-authorized actuation channel (the
    R595 activation path) injects a different predicate to exercise the launch.
    """
    return False


@dataclasses.dataclass(frozen=True)
class WorkerTurnoverDecision:
    """What the seam learned. `triggered` is the ONLY divergence signal.

    * ``triggered`` False -> not a confirmed Fable exhaustion; the caller MUST
      leave its existing path unchanged.
    * ``triggered`` True, ``actuated`` True -> an opus-4.8 successor was launched
      exactly once via the controller; `outcome` carries the audited link.
    * ``triggered`` True, ``actuated`` False -> a confirmed exhaustion that was
      recorded and surfaced but NOT auto-run (mode withheld authority, or the
      authorized controller declined). The caller keeps its safe PAUSE.
    """

    triggered: bool
    actuated: bool
    reason_code: str
    reason: str
    verdict: ExhaustionVerdict
    outcome: TurnoverOutcome | None = None
    #: A short, audit-safe summary for the loop's transition detail.
    audit_summary: dict[str, Any] = dataclasses.field(default_factory=dict)


class WorkerTurnoverIntegration:
    """The injectable seam object the loop consults before a terminal stop.

    Constructed with an already-assembled `TurnoverController` (fake dependencies
    in tests, the real `turnover_adapters` in production) and an `authorize`
    predicate deciding whether the run's mode permits an automatic redispatch.
    Everything substantive lives here so the loop's own diff is a single call.
    """

    def __init__(
        self,
        *,
        controller: TurnoverController | None = None,
        layer: TurnoverLayer = TurnoverLayer.WORKER,
        authorize: Callable[[Any], bool] = default_actuation_authorization,
        handoff_reference: str = "",
        event_prefix: str = "fable-exhaustion",
    ) -> None:
        self._controller = controller
        self._layer = layer
        self._authorize = authorize
        self._handoff_reference = handoff_reference
        self._event_prefix = event_prefix

    @staticmethod
    def evidence_from_run_result(run_result: Any, *, current_model: str) -> TurnoverEvidence:
        """Build the classifier's evidence from the ACTUAL bounded-unit result.

        M0-T054 increment 5 (live proof project-control/reports/M0-T054-live-proof/,
        reproducing D-010 source-028 / R289) closed a REAL gap: on a genuine Fable
        weekly-limit hard-stop the exact phrase does NOT reach `stderr_tail` (empty)
        or `checkpoint_error` (a generic no-checkpoint / malformed string) - it lives
        in the STREAM events, which the runner now distills into `result_text` (the
        api-error result/assistant text carrying the exact message) and
        `rate_limit_rejection` (a raw rejected `rate_limit_event`). Feeding only
        stderr+checkpoint_error, as before, left the classifier blind and it returned
        NOT_EXHAUSTED, so the turnover never fired on real exhaustion.

        So the evidence now folds `result_text` into the stdout text ALONGSIDE the
        parser-side `checkpoint_error`, still carries `stderr_tail`, and passes the
        raw `rate_limit_rejection` through as `structured_result`. `exit_code` is the
        observed process return code (the runner reports -1 when none was seen, an
        UNKNOWN-but-not-success exit), and `model_id` is the model the just-failed
        unit actually ran on, so a structured attribution can tie the signal to
        Fable. The classifier remains the SOLE decider (it fails a bare/transient 429
        closed); this only gathers.
        """
        stderr = str(getattr(run_result, "stderr_tail", "") or "")
        checkpoint_error = str(getattr(run_result, "checkpoint_error", "") or "")
        result_text = str(getattr(run_result, "result_text", "") or "")
        stdout = "\n".join(part for part in (checkpoint_error, result_text) if part)
        structured = getattr(run_result, "rate_limit_rejection", None)
        if not isinstance(structured, Mapping):
            structured = None
        return TurnoverEvidence(
            stdout=stdout,
            stderr=stderr,
            exit_code=getattr(run_result, "returncode", None),
            structured_result=structured,
            model_id=str(current_model or ""),
        )

    def evaluate(
        self,
        run_result: Any,
        *,
        current_model: str,
        config: Any,
        run_id: str,
        cycle: int,
        safe_checkpoint_id: str = "",
    ) -> WorkerTurnoverDecision:
        """Classify the failed unit; turn over EXACTLY ONCE only if authorized.

        Called only from the loop's missing/failed-checkpoint seam, and only after
        the pending-external-effect guard has cleared (a same-unit redispatch while
        an effect is unproven would be unsafe - the loop keeps that guard ahead of
        this call).
        """
        evidence = self.evidence_from_run_result(run_result, current_model=current_model)
        verdict = classify_exhaustion(evidence)

        # FAIL-CLOSED: only a confirmed exhaustion diverges. NOT_EXHAUSTED and
        # AMBIGUOUS_FAIL_CLOSED leave the caller's existing path untouched.
        if not getattr(verdict, "should_turn_over", False):
            return WorkerTurnoverDecision(
                triggered=False, actuated=False,
                reason_code="", reason=getattr(verdict, "reason", ""),
                verdict=verdict)

        # MODE / AUTHORITY GATE: record-intent-only unless the mode authorizes an
        # automatic redispatch. This is the point that must never bypass
        # supervised-mode approval or a LIMITED-AUTO-off state.
        if not self._authorize(config):
            reason = (
                "a confirmed Fable weekly-limit exhaustion was detected on the "
                "worker unit, but the current mode does not authorize an automatic "
                f"redispatch ({verdict.reason}); the intended opus-4.8 turnover is "
                "recorded and surfaced for the owner, and the run keeps its safe "
                "PAUSE (no successor launched)")
            return WorkerTurnoverDecision(
                triggered=True, actuated=False,
                reason_code=REASON_TURNOVER_RECORDED, reason=reason,
                verdict=verdict,
                audit_summary={
                    "turnover": "recorded_intent_not_authorized",
                    "successor_model_id": "claude-opus-4-8",
                })

        # AUTHORIZED but no actuation channel wired: fail closed to record-intent.
        # Production is SHADOW-ONLY (supervisor-freeze §4, R595 pre-activation
        # blocking), so no live opus launcher is wired into the start path; the
        # authorized-launch channel (real adapters + survivor detector) is supplied
        # only at R595 activation. Without it a would-be launch is recorded, never
        # run.
        if self._controller is None:
            reason = (
                "a confirmed Fable weekly-limit exhaustion was authorized for "
                "turnover, but no actuation channel is wired (R595 activation "
                f"pending; supervisor is SHADOW-ONLY): {verdict.reason}. The "
                "intended opus-4.8 turnover is recorded and the run keeps its safe "
                "PAUSE (no successor launched)")
            return WorkerTurnoverDecision(
                triggered=True, actuated=False,
                reason_code=REASON_TURNOVER_RECORDED, reason=reason,
                verdict=verdict,
                audit_summary={
                    "turnover": "recorded_intent_no_channel",
                    "successor_model_id": "claude-opus-4-8",
                })

        # AUTHORIZED: build the grounded context and turn over EXACTLY ONCE. The
        # controller owns the lock/dedup/survivor/opus-availability guards, so a
        # second call with the same event id is suppressed there, not here.
        context = TurnoverContext(
            task_id=str(getattr(config, "task_id", "") or ""),
            event_id=self._event_id(run_id, cycle),
            failed_fable_execution_id=self._failed_execution_id(run_result, run_id, cycle),
            safe_checkpoint_id=str(safe_checkpoint_id or ""),
            handoff_reference=self._handoff_reference or run_id,
            layer=self._layer,
        )
        outcome = self._controller.execute(verdict, context)
        actuated = bool(getattr(outcome, "turned_over", False))
        if actuated:
            reason = (
                "a confirmed Fable weekly-limit exhaustion was turned over: "
                f"{outcome.reason}")
            reason_code = REASON_TURNOVER_LAUNCHED
        else:
            reason = (
                "a confirmed Fable weekly-limit exhaustion was authorized for "
                f"turnover, but the controller declined to launch: {outcome.reason}")
            reason_code = REASON_TURNOVER_RECORDED
        return WorkerTurnoverDecision(
            triggered=True, actuated=actuated,
            reason_code=reason_code, reason=reason, verdict=verdict,
            outcome=outcome,
            audit_summary={
                "turnover": outcome.status.value,
                "successor_id": outcome.successor_id,
                "successor_model_id": outcome.model_id,
                "audit_record_id": outcome.audit_record_id,
                "event_id": outcome.event_id,
            })

    def _event_id(self, run_id: str, cycle: int) -> str:
        """A stable exhaustion-event id for the SAME failed unit.

        Deterministic in (run_id, cycle) so a re-invocation for the same failed
        unit presents the SAME event id and the controller's dedup suppresses a
        second redispatch (exactly-once)."""
        return f"{self._event_prefix}:{run_id}:{cycle}"

    @staticmethod
    def _failed_execution_id(run_result: Any, run_id: str, cycle: int) -> str:
        session_id = str(getattr(run_result, "session_id", "") or "")
        return session_id or f"{run_id}:{cycle}"
