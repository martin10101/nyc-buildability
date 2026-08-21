#!/usr/bin/env python3
"""Fable->Opus turnover ACTUATION policy (M0-T054, second increment).

Qualifying evidence (supervisor-freeze §2, AD-093): a *reproduced provider
incident*. D-010 source-028 / R289: Fable 5 hit its weekly usage limit and hard-
stopped with the exact message

    You've reached your Fable 5 limit. Run /usage-credits to continue or switch
    models with /model.

and the CLI's built-in `fallbackModel` did NOT auto-switch. Increment 1
(`model_turnover.py`) supplies the PURE detection classifier
(`classify_exhaustion` -> `ExhaustionVerdict`). This module is the deterministic
turnover ACTUATION POLICY built on top of it. It is strictly ADDITIVE
(supervisor-freeze §1): it adds NO behavior to any existing frozen module and
does not modify `model_turnover.py`.

Everything here is testable WITHOUT a live provider, a real process launch, a
config change, or any real I/O. All effects flow through INJECTED dependencies -
a successor `Launcher`, a single-instance continuation `Lock`, an `AuditSink`,
and an `Identity` (clock + id) source - so tests substitute in-memory fakes. The
policy NEVER calls `datetime.now`, `os`, `random`, a subprocess, or the network
directly; it only calls the interfaces it was handed.

The one governing rule is FAIL-CLOSED (AD-025, restated by the supervisor-freeze
lane): ONLY a confirmed `FABLE_EXHAUSTED` verdict (`verdict.should_turn_over` is
True) may trigger a turnover. `NOT_EXHAUSTED` and `AMBIGUOUS_FAIL_CLOSED` never
turn over.

WHERE THE SUCCESSOR COMES FROM (M0-T080, D-023-R013). Until M0-T080 this module
carried a module constant naming one literal Opus model id and launched every
successor on it. That is precisely the "unlisted or code-default model
selection" D-023-R013 prohibits: the id lived in the source, not in the owner's
protected configuration, so the owner could neither approve nor change it and no
launch probe ever had to prove it. The constant is GONE. The successor is now
resolved through an INJECTED `SuccessorResolver`, which production wires to the
owner-approved, live-probed chain in `approved_models.py`. A resolver that cannot
name an approved, probed successor produces `NO_APPROVED_SUCCESSOR` - a safe
stop that consumes no dedup - and NEVER a fallback to something the owner did not
approve.

Effort is different in kind and stays a code constant
(`ALLOWED_SUCCESSOR_EFFORT`): D-004-R159 permanently prohibits an effort key in
every configuration file, prompt, and CLI invocation, so the owner-approved
config is structurally unable to carry one and `config.assert_no_effort_key`
refuses any file that tries. It is carried as invocation metadata, never as a
flag.

Exactly-once turnover is guaranteed by three cooperating mechanisms, checked in
this order under the continuation lock: (1) the single-instance Lock serializes
all turnover attempts for a checkout and blocks a second concurrent launch;
(2) a dedup check against the AuditSink (`already_actioned(event_id)`) suppresses
a repeat turnover for an exhaustion event that was already actioned; and (3) the
successor launch marks the event actioned ONLY after a confirmed launch, so a
re-invocation with the same event id observes the dedup and never launches twice.
A surviving Fable worker / competing orchestrator (an injected predicate) blocks
the launch and preserves evidence without consuming the dedup, so a genuine later
attempt is still possible once the survivor is gone.
"""
from __future__ import annotations

import dataclasses
import enum
from typing import Any, Callable, Mapping, Protocol, runtime_checkable

from .model_turnover import ExhaustionVerdict

#: The successor effort. This stays a code constant deliberately and is the ONE
#: thing about the successor that does not come from owner config: D-004-R159
#: permanently prohibits an effort key in every configuration file, so protected
#: config structurally cannot carry one. It rides as invocation metadata; every
#: `--effort` argv form is hard-denied by `process.assert_argv_safe`.
ALLOWED_SUCCESSOR_EFFORT = "xhigh"


@dataclasses.dataclass(frozen=True)
class ApprovedSuccessor:
    """The successor an owner-approved, live-probed selection produced.

    `model_id` came out of the owner's approved list and carries the evidence
    that authorized it, so a launch record can show WHY this id was permitted
    rather than asserting that it was.
    """

    model_id: str
    effort: str = ALLOWED_SUCCESSOR_EFFORT
    probed_at_utc: str = ""
    config_identity: str = ""
    cli_version: str = ""

    def __post_init__(self) -> None:
        if not self.model_id or self.model_id != self.model_id.strip():
            raise ValueError(
                f"an approved successor needs an exact model id, got {self.model_id!r}; the "
                f"id reaches --model verbatim and is never trimmed or aliased")

    def evidence(self) -> dict[str, Any]:
        return {"successor_model_id": self.model_id,
                "successor_effort": self.effort,
                "successor_probed_at_utc": self.probed_at_utc,
                "successor_config_identity": self.config_identity,
                "successor_cli_version": self.cli_version}


#: The INJECTED successor seam: given the grounded turnover context, name the
#: owner-approved, live-probed model the successor must launch on. It RAISES
#: (typically `approved_models.ModelRoutingError`) when the approved list is
#: empty, when nothing in it probed successfully, or when the chain is spent -
#: and the controller turns that into a typed safe stop.
SuccessorResolver = Callable[["TurnoverContext"], ApprovedSuccessor]


class TurnoverLayer(enum.Enum):
    """Which layer is being turned over. The policy is identical for both; the
    layer is a PARAMETER (not duplicated logic) that the launcher acts on.

    * ``ORCHESTRATOR`` - start/resume the Opus orchestrator from the durable
      handoff at the last safe checkpoint.
    * ``WORKER`` - redispatch the SAME bounded unit of work exactly once on Opus
      from its safe checkpoint.
    """

    ORCHESTRATOR = "orchestrator"
    WORKER = "worker"


class TurnoverStatus(enum.Enum):
    """The typed outcome of an actuation attempt.

    * ``LAUNCHED_SUCCESSOR`` - exactly one Opus successor was launched and the
      Fable->Opus link was audited.
    * ``NO_TURNOVER`` - the verdict did not authorize a turnover
      (NOT_EXHAUSTED or AMBIGUOUS_FAIL_CLOSED); fail closed.
    * ``ALREADY_IN_PROGRESS`` - the continuation lock is already held (a turnover
      in progress or a surviving peer); no second launch.
    * ``SUPPRESSED_DUPLICATE`` - this exhaustion event id was already actioned;
      no repeat turnover.
    * ``BLOCKED_SURVIVOR`` - a surviving Fable worker / competing orchestrator was
      detected; no launch, evidence preserved, dedup NOT consumed.
    * ``INVALID_MODEL_REFUSED`` - the caller named a model/effort other than the
      owner-approved successor the resolver produced; refused with no launch.
    * ``NO_APPROVED_SUCCESSOR`` - the owner-approved list is empty, nothing in it
      has a successful live launch probe, or the chain is spent. A SAFE STOP:
      no launch, no substitute, lock released, dedup NOT consumed.
    * ``OPUS_UNAVAILABLE_SAFE_STOP`` - the launcher could not start the approved
      successor; no fallback to another model, lock released, dedup NOT consumed.
      (The name is the frozen machine contract from M0-T054 and is unchanged; it
      means "the approved successor did not come up", whichever id that is.)
    * ``LAUNCH_FAILED_SAFE_STOP`` - the launcher returned an inconsistent result
      (available but no successor id, or a mismatched model); fail closed, no
      claimed launch, lock released, dedup NOT consumed.
    """

    LAUNCHED_SUCCESSOR = "launched_successor"
    NO_TURNOVER = "no_turnover"
    ALREADY_IN_PROGRESS = "already_in_progress"
    SUPPRESSED_DUPLICATE = "suppressed_duplicate"
    BLOCKED_SURVIVOR = "blocked_survivor"
    INVALID_MODEL_REFUSED = "invalid_model_refused"
    NO_APPROVED_SUCCESSOR = "no_approved_successor"
    OPUS_UNAVAILABLE_SAFE_STOP = "opus_unavailable_safe_stop"
    LAUNCH_FAILED_SAFE_STOP = "launch_failed_safe_stop"


@dataclasses.dataclass(frozen=True)
class TurnoverContext:
    """The grounded context a turnover decision needs.

    `requested_model` / `requested_effort` capture what a caller asked for so the
    policy can REFUSE anything other than the owner-approved successor the
    resolver produced. They default to EMPTY, meaning "no caller preference" -
    they no longer default to a model id, because a default model id in a context
    object is the same unlisted-selection hazard as a constant in the policy
    (D-023-R013). The successor is always launched with the RESOLVED approved
    id, never with a caller-supplied model string.
    """

    task_id: str
    event_id: str
    failed_fable_execution_id: str
    safe_checkpoint_id: str
    handoff_reference: str
    layer: TurnoverLayer
    requested_model: str = ""
    requested_effort: str = ""
    #: The model the failed execution was running on, so the resolver can walk
    #: the owner-approved list from the entry AFTER it.
    current_model: str = ""


@dataclasses.dataclass(frozen=True)
class LaunchRequest:
    """What the injected launcher is asked to start. Model/effort are the
    hard-coded constants, never caller-supplied."""

    layer: TurnoverLayer
    task_id: str
    event_id: str
    model_id: str
    effort: str
    handoff_reference: str
    safe_checkpoint_id: str
    failed_fable_execution_id: str


@dataclasses.dataclass(frozen=True)
class LaunchResult:
    """What the launcher reports back.

    * ``available`` False means Opus 4.8 could not be started (usage/limit/outage)
      - the policy safe-stops and NEVER retries with another model.
    * ``successor_id`` identifies the launched successor when available.
    * ``model_id`` optionally echoes the model the launcher actually started; when
      present it must equal the requested opus id or the policy fails closed.
    """

    available: bool
    successor_id: str = ""
    model_id: str = ""
    detail: str = ""


@dataclasses.dataclass(frozen=True)
class TurnoverOutcome:
    """The typed, fully-explained result of an actuation attempt."""

    status: TurnoverStatus
    reason: str
    event_id: str
    layer: TurnoverLayer
    failed_fable_execution_id: str
    safe_checkpoint_id: str
    successor_id: str = ""
    model_id: str = ""
    effort: str = ""
    audit_record_id: str = ""

    @property
    def turned_over(self) -> bool:
        """True ONLY when exactly one successor was launched."""
        return self.status is TurnoverStatus.LAUNCHED_SUCCESSOR


# --------------------------------------------------------------------------
# Injected dependency interfaces (tests supply in-memory fakes)
# --------------------------------------------------------------------------


@runtime_checkable
class Launcher(Protocol):
    """Starts exactly one successor. The policy calls this AT MOST once per
    invocation, only after every guard has passed."""

    def launch(self, request: LaunchRequest) -> LaunchResult:
        ...


@runtime_checkable
class ContinuationLock(Protocol):
    """The single-instance / continuation lock.

    `acquire` returns True when this attempt now holds the lock, or False when it
    is already held elsewhere (a turnover in progress or a surviving peer). The
    policy releases the lock on every path once it has acquired it.
    """

    def acquire(self) -> bool:
        ...

    def release(self) -> None:
        ...


@runtime_checkable
class AuditSink(Protocol):
    """Durable dedup + audit store.

    `already_actioned` answers the dedup question for an exhaustion event id.
    `append` records an audit entry and returns its id (a pure append; it does NOT
    consume the dedup). `mark_actioned` is called ONLY after a confirmed launch,
    so it is the single point that consumes an event id.
    """

    def already_actioned(self, event_id: str) -> bool:
        ...

    def append(self, record: Mapping[str, Any]) -> str:
        ...

    def mark_actioned(self, event_id: str) -> None:
        ...


@runtime_checkable
class Identity(Protocol):
    """Injected clock + id source (never `datetime.now` / `random` directly)."""

    def now_iso(self) -> str:
        ...

    def new_audit_id(self) -> str:
        ...


#: An injected predicate: True when a surviving Fable worker or competing
#: orchestrator is detected for this context (so the policy must NOT launch).
SurvivorPredicate = Callable[[TurnoverContext], bool]


class TurnoverController:
    """Deterministic, injected-dependency turnover actuation policy.

    Reused for BOTH layers via `TurnoverContext.layer`; there is one code path,
    not two. Every external effect is routed through an injected dependency, so
    the policy is fully exercised by in-memory fakes with no live provider,
    process, config change, or network.
    """

    def __init__(
        self,
        *,
        launcher: Launcher,
        lock: ContinuationLock,
        audit: AuditSink,
        identity: Identity,
        survivor_detected: SurvivorPredicate,
        successor: SuccessorResolver,
    ) -> None:
        self._launcher = launcher
        self._lock = lock
        self._audit = audit
        self._identity = identity
        self._survivor_detected = survivor_detected
        # REQUIRED, with no default: a controller that could fall back to a
        # built-in successor would reintroduce exactly the constant M0-T080
        # removed. Every construction site must say where its successor comes
        # from (D-023-R013).
        self._successor = successor

    def execute(
        self, verdict: ExhaustionVerdict, context: TurnoverContext,
    ) -> TurnoverOutcome:
        """Perform an exactly-once turnover for a classified verdict + context."""
        # 1. FAIL-CLOSED gate: only a confirmed exhaustion authorizes a turnover.
        if not getattr(verdict, "should_turn_over", False):
            reason = getattr(verdict, "reason", "") or "verdict did not authorize turnover"
            return self._no_launch(
                context, TurnoverStatus.NO_TURNOVER,
                f"verdict does not authorize turnover ({reason}); fail closed and do "
                f"not turn over")

        # 6 (pre-checked, no side effects): resolve the OWNER-APPROVED successor
        # before touching the lock, and refuse any caller preference that is not
        # it. Resolution is where the approved list and the live launch probe are
        # applied, so nothing past this point can name an unapproved id.
        try:
            successor = self._successor(context)
        except Exception as exc:
            # An empty approved list, no successful probe, or a spent chain. A
            # SAFE STOP: no launch, no substitute, and the dedup is untouched so
            # a later attempt is still possible once the owner has acted.
            return self._no_launch(
                context, TurnoverStatus.NO_APPROVED_SUCCESSOR,
                f"no owner-approved, live-probed successor is available ({exc}); stopping "
                f"safely with no launch. The supervisor never substitutes a model the owner "
                f"did not approve (D-023-R013)")
        if context.requested_model and context.requested_model != successor.model_id:
            return self._no_launch(
                context, TurnoverStatus.INVALID_MODEL_REFUSED,
                f"requested model {context.requested_model!r} is not the owner-approved "
                f"successor {successor.model_id!r} for this turnover; refused with no launch "
                f"(a different model needs an owner change to the protected config)")
        if context.requested_effort and context.requested_effort != successor.effort:
            return self._no_launch(
                context, TurnoverStatus.INVALID_MODEL_REFUSED,
                f"requested effort {context.requested_effort!r} is not the authorized "
                f"successor effort {successor.effort!r}; refused with no launch")

        # 2. Single-instance lock: a second concurrent attempt never launches.
        if not self._lock.acquire():
            return self._no_launch(
                context, TurnoverStatus.ALREADY_IN_PROGRESS,
                "the continuation lock is already held (a turnover in progress or a "
                "surviving peer); refusing a second launch")

        try:
            # 3. Duplicate-event suppression, under the lock.
            if self._audit.already_actioned(context.event_id):
                return self._no_launch(
                    context, TurnoverStatus.SUPPRESSED_DUPLICATE,
                    f"exhaustion event {context.event_id!r} was already actioned; "
                    f"suppressing a repeat turnover")

            # 4. Surviving-child / competing-peer check: preserve evidence, do NOT
            #    consume the dedup, do NOT launch.
            if self._survivor_detected(context):
                audit_id = self._audit.append(self._blocked_record(context))
                return self._no_launch(
                    context, TurnoverStatus.BLOCKED_SURVIVOR,
                    "a surviving Fable worker or competing orchestrator was detected; "
                    "not launching a successor and preserving evidence",
                    audit_record_id=audit_id)

            # 5 + 6 + 7. Launch EXACTLY ONE approved successor.
            request = LaunchRequest(
                layer=context.layer,
                task_id=context.task_id,
                event_id=context.event_id,
                model_id=successor.model_id,
                effort=successor.effort,
                handoff_reference=context.handoff_reference,
                safe_checkpoint_id=context.safe_checkpoint_id,
                failed_fable_execution_id=context.failed_fable_execution_id,
            )
            result = self._launcher.launch(request)

            # 9. Successor unavailable -> safe stop, NO fallback model, dedup NOT
            #    consumed so a later attempt can retry when it returns.
            if not getattr(result, "available", False):
                detail = (getattr(result, "detail", "")
                          or f"launcher reported {successor.model_id} unavailable")
                self._audit.append(self._safe_stop_record(context, detail))
                return self._no_launch(
                    context, TurnoverStatus.OPUS_UNAVAILABLE_SAFE_STOP,
                    f"launcher reported the approved successor {successor.model_id!r} "
                    f"unavailable ({detail}); safe-stopping WITHOUT falling back to any "
                    f"other model")

            # Fail closed on an inconsistent launcher result (no id, or a model the
            # launcher swapped out from under us).
            successor_id = getattr(result, "successor_id", "") or ""
            reported_model = getattr(result, "model_id", "") or ""
            if not successor_id or (reported_model and reported_model != successor.model_id):
                detail = (f"launcher returned available with successor_id={successor_id!r} "
                          f"model_id={reported_model!r}, expected "
                          f"{successor.model_id!r}")
                self._audit.append(self._safe_stop_record(context, detail))
                return self._no_launch(
                    context, TurnoverStatus.LAUNCH_FAILED_SAFE_STOP,
                    f"launcher result is inconsistent ({detail}); fail closed with no "
                    f"claimed launch")

            # 8. Audit the stopped-model -> successor link, then consume the dedup
            #    so a re-invoke with the same event id is suppressed (exactly-once).
            audit_id = self._audit.append(
                self._launched_record(context, successor_id, successor))
            self._audit.mark_actioned(context.event_id)
            return TurnoverOutcome(
                status=TurnoverStatus.LAUNCHED_SUCCESSOR,
                reason=(f"launched exactly one {successor.model_id}/"
                        f"{successor.effort} successor {successor_id!r} for the "
                        f"{context.layer.value} layer from safe checkpoint "
                        f"{context.safe_checkpoint_id!r}; audited stopped execution "
                        f"{context.failed_fable_execution_id!r} -> successor "
                        f"{successor_id!r}"),
                event_id=context.event_id,
                layer=context.layer,
                failed_fable_execution_id=context.failed_fable_execution_id,
                safe_checkpoint_id=context.safe_checkpoint_id,
                successor_id=successor_id,
                model_id=successor.model_id,
                effort=successor.effort,
                audit_record_id=audit_id,
            )
        finally:
            # The acquiring path always releases; a non-acquiring path returned
            # before entering this block.
            self._lock.release()

    # -- helpers -------------------------------------------------------------

    def _no_launch(
        self, context: TurnoverContext, status: TurnoverStatus, reason: str,
        *, audit_record_id: str = "",
    ) -> TurnoverOutcome:
        return TurnoverOutcome(
            status=status,
            reason=reason,
            event_id=context.event_id,
            layer=context.layer,
            failed_fable_execution_id=context.failed_fable_execution_id,
            safe_checkpoint_id=context.safe_checkpoint_id,
            audit_record_id=audit_record_id,
        )

    def _base_record(self, context: TurnoverContext, kind: str) -> dict[str, Any]:
        return {
            "audit_id": self._identity.new_audit_id(),
            "recorded_at_utc": self._identity.now_iso(),
            "kind": kind,
            "event_id": context.event_id,
            "task_id": context.task_id,
            "layer": context.layer.value,
            "failed_fable_execution_id": context.failed_fable_execution_id,
            "safe_checkpoint_id": context.safe_checkpoint_id,
            "handoff_reference": context.handoff_reference,
        }

    def _launched_record(self, context: TurnoverContext, successor_id: str,
                         successor: ApprovedSuccessor) -> dict[str, Any]:
        record = self._base_record(context, "fable_to_opus_turnover")
        record.update({
            "successor_id": successor_id,
            # The approved id AND the probe evidence that authorized it, so the
            # audit row shows why this model was permitted, not just which.
            **successor.evidence(),
            # The explicit stopped-execution -> successor link (both layers).
            "link": {
                "stopped_fable_execution_id": context.failed_fable_execution_id,
                "opus_successor_id": successor_id,
            },
        })
        return record

    def _blocked_record(self, context: TurnoverContext) -> dict[str, Any]:
        record = self._base_record(context, "turnover_blocked_survivor")
        record["detail"] = (
            "surviving Fable worker / competing orchestrator detected; no successor "
            "launched, evidence preserved")
        return record

    def _safe_stop_record(self, context: TurnoverContext, detail: str) -> dict[str, Any]:
        record = self._base_record(context, "turnover_safe_stop")
        record["detail"] = detail
        return record
