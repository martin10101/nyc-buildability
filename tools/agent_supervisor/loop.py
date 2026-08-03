#!/usr/bin/env python3
"""The assembled supervisor loop - shadow and supervised (D-007 S7, S12, S16.7).

Phases 1-3 built the pieces. This module is the wiring that turns them into one
cycle, and it is deliberately the only place in the package where a prompt can
reach the worker:

    START_CLAUDE -> CLAUDE_RUNNING -> CHECKPOINT_RECEIVED -> COLLECT_EVIDENCE
      -> CODEX_REVIEW -> VALIDATE_DECISION -> POLICY_CHECK -> FORWARD_PROMPT

Every arrow is a real `StateMachine.transition()` against the S7 table, so the
journal is the truth about where a run got to and a crash resumes exactly.

MODES (S12) - there are three runnable shapes and one that is not:

* **shadow** - observes a real workflow, gathers evidence and Codex decisions,
  and **forwards NOTHING**. It records what *would* have happened (the exact
  prompt, its digest, the state it would have moved to) as a `ShadowPlan`, and it
  counts would-be **synchronous stops** against the owner-touch budget. Shadow
  never touches the outbox at all: an outbox row is a commitment to send, and
  shadow makes no such commitment. `assert_forwarding_allowed()` raises if any
  caller tries.
* **supervised** - the full loop, but **the owner approves each forwarded
  prompt**. POLICY_CHECK moves to WAIT_FOR_OWNER, the exact prompt is held with
  its digest, and only an explicit operator approval bound to that digest moves
  it to FORWARD_PROMPT. A debugging and fallback mode, not the destination.
* **replay** - implemented in `replay.py`, not here: it makes no model calls.
* **limited-auto** - refused BY NAME. `LoopConfig` raises `LimitedAutoRefused`
  before anything is constructed. There is no code path in this module that can
  enable it, and no default, parse error, migration, or downgrade reaches it.

EXACTLY-ONCE FORWARDING (S15 state-machine family). A forwarded prompt is
journaled in the transactional outbox BEFORE it is sent, under a message id
derived deterministically from the run, cycle, and prompt digest. A second
attempt at the same logical prompt finds the row already there:

* already marked sent -> `duplicate_suppressed`, nothing is sent again;
* enqueued but unsent (a crash between enqueue and send) -> the SAME message is
  resumed; a new one is never minted.

OWNER-TOUCH BUDGET (S16.7). `OwnerTouchLedger` counts would-be synchronous stops
and nothing else, persists them in the journal so a restart does not lose or
double-count them, and reports `authorizes_nothing=True` on every summary. The
budget is a MEASUREMENT. It cannot widen policy, create a grant, alter authority,
or change a tier - this module imports no grant constructor and mutates no
`TaskAuthority` (asserted by a source-level test).
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Callable, Mapping, Sequence

from . import CONTROLLER_VERSION
from .codex_reviewer import build_forwarded_prompt
from .durable_state import JournalError
from .evidence import STOP_FOR_OWNER, build_packet
from .models import ClaudeCheckpoint, CodexDecision, digest_of, to_utc_iso
from .policy import (
    ASK,
    DENY_AND_HALT,
    HARD_DENY,
    NOTIFY,
    NotifyOnceLedger,
    ProposedAction,
    TaskAuthority,
    apply_model_recommendation,
    evaluate as evaluate_policy,
    DEFAULT_POLICY_CONFIG,
)
from .protocol import build_envelope
from .state_machine import (
    CHECKPOINT_RECEIVED,
    CLAUDE_RUNNING,
    CODEX_REVIEW,
    COLLECT_EVIDENCE,
    COMPLETE,
    FORWARD_PROMPT,
    HALTED,
    PAUSED_RECOVERY,
    POLICY_CHECK,
    PREFLIGHT,
    PREPARE_ROTATION,
    START_CLAUDE,
    VALIDATE_DECISION,
    WAIT_FOR_OWNER,
)

# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------

MODE_REPLAY = "replay"
MODE_SHADOW = "shadow"
MODE_SUPERVISED = "supervised"
MODE_LIMITED_AUTO = "limited-auto"

#: The modes THIS module can run. `replay` lives in `replay.py`; `limited-auto`
#: is refused by name and is not implemented anywhere.
RUNNABLE_MODES: tuple[str, ...] = (MODE_SHADOW, MODE_SUPERVISED)

ALL_MODE_NAMES: tuple[str, ...] = (MODE_REPLAY, MODE_SHADOW, MODE_SUPERVISED,
                                   MODE_LIMITED_AUTO)

#: S16.7 default. Configurable UP or DOWN by the owner; never by a model.
DEFAULT_OWNER_TOUCH_BUDGET = 2

#: The only states a cycle may BEGIN from. PREFLIGHT is the first cycle of a run;
#: CLAUDE_RUNNING is every subsequent cycle, after a prompt was forwarded. Any
#: other entry state means the caller's idea of where the run is disagrees with
#: the journal's, which is refused rather than transitioned around.
CYCLE_ENTRY_STATES: frozenset[str] = frozenset({PREFLIGHT, CLAUDE_RUNNING})


class LoopError(Exception):
    """The loop refused to do something. Always carries a code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class LimitedAutoRefused(LoopError):
    """`limited-auto` was named. Refused by name, before anything is built."""

    def __init__(self) -> None:
        super().__init__(
            "limited_auto_refused",
            "limited-auto is DISABLED and is not implemented by this build. It is never "
            "reachable from a configuration default, a missing value, a parse error, a "
            "migration, or a downgrade. Enabling it is a separate explicit owner "
            "activation recorded through directive compliance (D-007 S12).")


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class LoopConfig:
    """One loop run's bounds. Immutable for the life of the run."""

    mode: str
    task_id: str
    stage: str
    allowed_paths: tuple[str, ...] = ()
    stop_conditions: tuple[str, ...] = ()
    packet_reference: str = ""
    max_cycles: int = 8
    owner_touch_budget: int = DEFAULT_OWNER_TOUCH_BUDGET

    def __post_init__(self) -> None:
        if self.mode == MODE_LIMITED_AUTO:
            raise LimitedAutoRefused()
        if self.mode not in RUNNABLE_MODES:
            raise LoopError(
                "unknown_mode",
                f"{self.mode!r} is not a runnable loop mode; expected one of "
                f"{list(RUNNABLE_MODES)} (replay runs in replay.py, which makes no model "
                f"calls)")
        if not isinstance(self.max_cycles, int) or self.max_cycles < 1:
            raise LoopError("bad_max_cycles", "max_cycles must be a positive integer bound")
        if not isinstance(self.owner_touch_budget, int) or self.owner_touch_budget < 0:
            raise LoopError("bad_budget", "owner_touch_budget must be a non-negative integer")

    @property
    def forwards(self) -> bool:
        """True only for supervised. Shadow forwards nothing, ever."""
        return self.mode == MODE_SUPERVISED


# --------------------------------------------------------------------------
# Owner-touch accounting (S12, S16.7)
# --------------------------------------------------------------------------

TOUCH_SYNCHRONOUS_STOP = "synchronous_stop"
TOUCH_BLOCKING_ASK = "blocking_ask"
TOUCH_SUPERVISED_APPROVAL = "supervised_mode_approval"
TOUCH_NOTIFY = "notify"

#: Kinds that count against the S16.7 budget. Supervised-mode approvals are a
#: property of the DEBUGGING mode, not of the target operating mode, so they are
#: recorded and reported but never counted - counting them would make the budget
#: measure the wrong thing. NOTIFY never blocks and never counts.
COUNTED_TOUCH_KINDS: frozenset[str] = frozenset({
    TOUCH_SYNCHRONOUS_STOP, TOUCH_BLOCKING_ASK,
})

OWNER_TOUCH_KEY = "owner_touch_ledger"


@dataclasses.dataclass(frozen=True)
class OwnerTouch:
    """One moment the owner would have had to act."""

    kind: str
    reason_code: str
    reason: str
    cycle: int
    counted: bool
    basis: str = ""
    at_utc: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class BudgetReport:
    """What the counter measured. It authorizes nothing (S16.7)."""

    budget: int
    counted: int
    within_budget: bool
    excess: int
    touches: tuple[OwnerTouch, ...]
    authorizes_nothing: bool = True
    note: str = (
        "The budget is a MEASUREMENT. Every excess stop must be dispositioned either as an "
        "accepted permanent gate or as a PROPOSED deterministic policy change that has "
        "passed security and control-plane review, replay testing, and explicit owner "
        "approval. The budget itself authorizes nothing (D-007 S16.7).")

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["touches"] = [t.to_dict() for t in self.touches]
        return data


class OwnerTouchLedger:
    """Durable count of would-be synchronous stops.

    Persisted in the journal's state table keyed by run, so a restart neither
    loses a touch nor counts one twice. It exposes no mutator of policy, of
    authority, or of any grant: reading this ledger can never widen anything.
    """

    def __init__(self, journal: Any, *, run_id: str, budget: int) -> None:
        self.journal = journal
        self.run_id = run_id
        self.budget = int(budget)

    def _key(self) -> str:
        return f"{OWNER_TOUCH_KEY}/{self.run_id}"

    def all_touches(self) -> tuple[OwnerTouch, ...]:
        raw = self.journal.get_state(self._key(), [])
        if not isinstance(raw, list):
            return ()
        known = {f.name for f in dataclasses.fields(OwnerTouch)}
        return tuple(OwnerTouch(**{k: v for k, v in item.items() if k in known})
                     for item in raw if isinstance(item, dict))

    def record(self, kind: str, *, reason_code: str, reason: str, cycle: int,
               basis: str = "") -> OwnerTouch:
        if kind not in (TOUCH_SYNCHRONOUS_STOP, TOUCH_BLOCKING_ASK,
                        TOUCH_SUPERVISED_APPROVAL, TOUCH_NOTIFY):
            raise LoopError("unknown_touch_kind", f"{kind!r} is not an owner-touch kind")
        touch = OwnerTouch(
            kind=kind, reason_code=reason_code, reason=reason, cycle=cycle,
            counted=kind in COUNTED_TOUCH_KINDS, basis=basis, at_utc=to_utc_iso())
        existing = [t.to_dict() for t in self.all_touches()]
        existing.append(touch.to_dict())
        self.journal.set_state(self._key(), existing)
        return touch

    def counted(self) -> int:
        return sum(1 for t in self.all_touches() if t.counted)

    def report(self) -> BudgetReport:
        touches = self.all_touches()
        counted = sum(1 for t in touches if t.counted)
        return BudgetReport(
            budget=self.budget,
            counted=counted,
            within_budget=counted <= self.budget,
            excess=max(0, counted - self.budget),
            touches=touches)


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ShadowPlan:
    """What shadow mode WOULD have done. Nothing here was sent."""

    cycle: int
    would_forward: bool
    would_transition_to: str
    prompt_digest: str
    prompt_preview: str
    decision: str
    tier: str
    recorded_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class ForwardResult:
    """The outcome of one exactly-once forwarding attempt."""

    message_id: str
    sent: bool
    duplicate_suppressed: bool = False
    resumed_unsent: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class CycleResult:
    """Everything one cycle established. Nothing is inferred from a model."""

    cycle: int
    mode: str
    reached_state: str
    path: tuple[str, ...] = ()
    checkpoint_id: str = ""
    decision: str = ""
    tier: str = ""
    reason_code: str = ""
    reason: str = ""
    forwarded: bool = False
    forward: ForwardResult | None = None
    shadow_plan: ShadowPlan | None = None
    pending_prompt_digest: str = ""
    owner_touches: tuple[OwnerTouch, ...] = ()
    notify_events: tuple[str, ...] = ()
    stopped: str = ""
    packet_digest: str = ""
    notes: tuple[str, ...] = ()

    @property
    def continues(self) -> bool:
        """True only when the loop may legitimately run another cycle."""
        return self.reached_state in (CLAUDE_RUNNING, POLICY_CHECK) and not self.stopped

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["owner_touches"] = [t.to_dict() for t in self.owner_touches]
        data["forward"] = self.forward.to_dict() if self.forward else None
        data["shadow_plan"] = self.shadow_plan.to_dict() if self.shadow_plan else None
        return data


@dataclasses.dataclass
class LoopRun:
    """The whole run: every cycle, the budget report, and where it stopped."""

    run_id: str
    mode: str
    cycles: tuple[CycleResult, ...]
    final_state: str
    stopped: str
    budget: BudgetReport
    forwarded_message_ids: tuple[str, ...] = ()
    provider_calls: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "final_state": self.final_state,
            "stopped": self.stopped,
            "cycles": [c.to_dict() for c in self.cycles],
            "budget": self.budget.to_dict(),
            "forwarded_message_ids": list(self.forwarded_message_ids),
            "provider_calls": self.provider_calls,
            "limited_auto_enabled": False,
        }


# --------------------------------------------------------------------------
# The loop
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Prompt digests: what an approval actually binds to
# --------------------------------------------------------------------------
#
# A rendered forwarded prompt is NOT stable across renders: it carries a
# `FORWARDED AT:` timestamp and a reference to the evidence packet, whose own
# digest moves with the clock and with live git state. Binding an approval to
# those bytes makes a digest-bound approval impossible to honour - the operator
# is shown one digest, and by the time they answer with it the prompt has
# re-rendered to a different one. (Found by running `start --mode supervised`
# end to end: the approval never matched, twice, for two different reasons.)
#
# Scrubbing the volatile lines out of the rendered text would work until someone
# adds a third one. So the approval digest is computed from the INSTRUCTION
# FIELDS directly - the exact five things S9 says every forwarded prompt carries,
# plus the task and stage that confer authority:
#
#   approval_digest   "is this the same INSTRUCTION?"   Binds the approval, the
#                     pending-prompt record, and the outbox message id, so a
#                     crash-and-re-render resumes rather than duplicating.
#   digest_of(prompt) "what exact bytes went out?"      Recorded in the envelope
#                     and the audit trail, for provenance.
#
# Change the task, the stage, a permitted path, the requested action, or a stop
# condition, and the approval digest changes - so the approval is invalidated,
# which is exactly S13.5's rule. Change only the clock, and it does not.

APPROVAL_DIGEST_FIELDS: tuple[str, ...] = (
    "task_id", "stage", "allowed_paths", "requested_action", "stop_conditions")


def approval_digest(
    *,
    task_id: str,
    stage: str,
    allowed_paths: Sequence[str],
    requested_action: str,
    stop_conditions: Sequence[str],
) -> str:
    """The digest an approval binds to: the instruction, not the clock."""
    return digest_of({
        "task_id": task_id,
        "stage": stage,
        "allowed_paths": sorted(str(p) for p in allowed_paths),
        "requested_action": requested_action.strip(),
        "stop_conditions": sorted(str(s) for s in stop_conditions),
    })


#: Reason codes that ARE would-be synchronous stops (S4.5), used to count the
#: owner-touch budget. Derived, not restated: policy owns the condition list.
def is_synchronous_stop(decision: Any) -> bool:
    """True when a `PolicyDecision`-shaped object demands a synchronous stop."""
    return bool(getattr(decision, "synchronous_stop", False)) or \
        getattr(decision, "outcome", "") == DENY_AND_HALT


class SupervisedLoop:
    """One controlled task's supervised or shadow loop.

    Collaborators are injected, so every test drives the REAL loop against fake
    executables and fake collectors rather than a reimplementation of it.
    """

    def __init__(
        self,
        *,
        config: LoopConfig,
        journal: Any,
        audit: Any,
        machine: Any,
        authority: TaskAuthority,
        runner: Any,
        reviewer: Any,
        run_id: str,
        collector: Any = None,
        broker: Any = None,
        breakers: Any = None,
        policy_config: Any = DEFAULT_POLICY_CONFIG,
        packet_builder: Callable[..., Any] | None = None,
        approval_gate: Callable[[str, str], bool] | None = None,
        never_send: Sequence[str] = (),
    ) -> None:
        self.config = config
        self.journal = journal
        self.audit = audit
        self.machine = machine
        self.authority = authority
        self.runner = runner
        self.reviewer = reviewer
        self.run_id = run_id
        self.collector = collector
        self.broker = broker
        self.breakers = breakers
        self.policy_config = policy_config
        self._build_packet = packet_builder or build_packet
        self._approval_gate = approval_gate
        self.never_send = tuple(never_send)
        self.touches = OwnerTouchLedger(journal, run_id=run_id,
                                        budget=config.owner_touch_budget)
        self.notify_ledger = NotifyOnceLedger(journal)
        self.provider_calls = 0
        self._forwarded: list[str] = []

    # -- guards -------------------------------------------------------------

    @property
    def mode(self) -> str:
        return self.config.mode

    def assert_forwarding_allowed(self) -> None:
        """S12: shadow forwards NOTHING. This is the structural guarantee."""
        if not self.config.forwards:
            raise LoopError(
                "shadow_forwards_nothing",
                f"mode {self.mode!r} observes and reports; it never forwards a prompt, "
                f"never enqueues one for sending, and never contacts the worker with one")

    def _guard(self) -> None:
        """S13.12 invariant 5 before every step."""
        self.machine.assert_can_act()

    def _touch(self, kind: str, *, reason_code: str, reason: str, cycle: int,
               basis: str = "") -> OwnerTouch:
        touch = self.touches.record(kind, reason_code=reason_code, reason=reason,
                                    cycle=cycle, basis=basis)
        if self.audit is not None:
            self.audit.append("owner_touch_recorded", run_id=self.run_id,
                              policy_result=reason_code,
                              detail={"kind": kind, "counted": touch.counted,
                                      "cycle": cycle, "basis": basis,
                                      "mode": self.mode})
        return touch

    def _breaker(self, name: str) -> tuple[bool, str]:
        """Record one breaker tick. Returns (tripped, message)."""
        if self.breakers is None:
            return False, ""
        verdict = self.breakers.record(name)
        if verdict.tripped:
            return True, verdict.message
        if verdict.warning:
            return False, verdict.message
        return False, ""

    # -- the cycle ----------------------------------------------------------

    def run_cycle(self, prompt: str, *, cycle: int) -> CycleResult:
        """One complete supervised/shadow cycle. Returns what it established."""
        result = CycleResult(cycle=cycle, mode=self.mode,
                             reached_state=self.machine.current_state)
        path: list[str] = []
        touches: list[OwnerTouch] = []
        notify: list[str] = []

        def land(state: str) -> None:
            if not path or path[-1] != state:
                path.append(state)
            result.reached_state = state
            result.path = tuple(path)

        def stop(code: str, reason: str, state: str) -> CycleResult:
            land(state)
            result.stopped = code
            result.reason = reason
            result.owner_touches = tuple(touches)
            result.notify_events = tuple(notify)
            return result

        self._guard()

        # --- START_CLAUDE ---------------------------------------------------
        entry = self.machine.current_state
        if entry not in CYCLE_ENTRY_STATES:
            raise LoopError(
                "bad_cycle_entry_state",
                f"a cycle starts from {sorted(CYCLE_ENTRY_STATES)}, not from {entry!r}. "
                f"Refusing rather than attempting a transition the S7 table does not "
                f"contain: an illegal transition here would mean the caller and the "
                f"journal disagree about where the run is")
        if entry == PREFLIGHT:
            self.machine.transition(START_CLAUDE, "preflight_pass",
                                    detail={"cycle": cycle, "mode": self.mode})
            land(START_CLAUDE)

        tripped, message = self._breaker("claude_runs_per_task")
        if tripped:
            if self.machine.current_state == CLAUDE_RUNNING:
                self.machine.transition(PAUSED_RECOVERY, "unsafe_condition",
                                        detail={"breaker": "claude_runs_per_task"})
            touches.append(self._touch(TOUCH_SYNCHRONOUS_STOP,
                                       reason_code="circuit_breaker_hard_threshold",
                                       reason=message, cycle=cycle,
                                       basis="S13.8 hard threshold"))
            return stop("circuit_breaker_hard_threshold", message,
                        self.machine.current_state)
        if message:
            notify.append("circuit_breaker_warning")

        # --- run the bounded unit -------------------------------------------
        self.provider_calls += 1
        run_result = self.runner.run_unit(prompt)
        if self.machine.current_state == START_CLAUDE:
            self.machine.transition(
                CLAUDE_RUNNING, "claude_process_started",
                detail={"cycle": cycle, "session_id": run_result.session_id,
                        "containment": getattr(run_result, "containment", "")})
            land(CLAUDE_RUNNING)

        checkpoint: ClaudeCheckpoint | None = getattr(run_result, "checkpoint", None)
        if checkpoint is None or not run_result.ok:
            # S14: a timeout, a nonzero exit, or a missing checkpoint is NEVER
            # success. Reconcile the external-effect journal before any retry.
            unreconciled = list(self.journal.pending_effects())
            reason = (getattr(run_result, "checkpoint_error", "")
                      or "the worker exited without a valid checkpoint")
            if unreconciled:
                self.machine.transition(
                    PAUSED_RECOVERY, "unsafe_condition",
                    detail={"cycle": cycle, "reason": "ambiguous_effect_before_retry",
                            "pending_effects": [e.action_id for e in unreconciled]})
                touches.append(self._touch(
                    TOUCH_SYNCHRONOUS_STOP, reason_code="ambiguous_effect",
                    reason="the worker exited without a checkpoint while a modeled "
                           "external effect was still PENDING; the exact unit is never "
                           "retried until the effect is proven",
                    cycle=cycle, basis="S11.5 / S14"))
                return stop("ambiguous_effect", reason, PAUSED_RECOVERY)
            self.machine.transition(PAUSED_RECOVERY, "unsafe_condition",
                                    detail={"cycle": cycle, "reason": reason})
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="no_valid_checkpoint",
                reason=reason, cycle=cycle, basis="S14"))
            return stop("no_valid_checkpoint", reason, PAUSED_RECOVERY)

        self.machine.transition(
            CHECKPOINT_RECEIVED, "valid_checkpoint_received",
            detail={"cycle": cycle, "checkpoint_id": checkpoint.checkpoint_id,
                    "checkpoint_digest": digest_of(checkpoint.to_dict())})
        land(CHECKPOINT_RECEIVED)
        result.checkpoint_id = checkpoint.checkpoint_id

        # --- COLLECT_EVIDENCE ------------------------------------------------
        self.machine.transition(COLLECT_EVIDENCE, "checkpoint_validated",
                                detail={"cycle": cycle})
        land(COLLECT_EVIDENCE)

        packet_result = self._collect(checkpoint)
        if not packet_result.ok:
            self.machine.transition(WAIT_FOR_OWNER, "evidence_incomplete_ask",
                                    detail={"cycle": cycle,
                                            "stop": packet_result.stop,
                                            "reason": packet_result.reason})
            touches.append(self._touch(
                TOUCH_BLOCKING_ASK, reason_code="evidence_incomplete",
                reason=packet_result.reason, cycle=cycle,
                basis="S10 - material evidence is never silently omitted"))
            return stop("evidence_incomplete", packet_result.reason, WAIT_FOR_OWNER)

        packet = packet_result.packet
        result.packet_digest = packet.packet_digest
        self.machine.transition(CODEX_REVIEW, "evidence_packet_built",
                                detail={"cycle": cycle,
                                        "packet_digest": packet.packet_digest,
                                        "packet_bytes": packet.size_bytes})
        land(CODEX_REVIEW)

        # --- CODEX_REVIEW ----------------------------------------------------
        self._breaker("codex_reviews_per_checkpoint")
        self.provider_calls += 1
        outcome = self.reviewer.review(
            packet.to_dict(), expected_task_id=self.config.task_id,
            expected_checkpoint_id=checkpoint.checkpoint_id)
        notify.extend(getattr(outcome, "notify_events", ()) or ())
        if not outcome.ok:
            self.machine.transition(
                WAIT_FOR_OWNER, "codex_unavailable_ask",
                detail={"cycle": cycle, "error": outcome.error_code,
                        "message": outcome.error_message})
            touches.append(self._touch(
                TOUCH_BLOCKING_ASK, reason_code=outcome.error_code or "review_unavailable",
                reason=outcome.error_message, cycle=cycle,
                basis="S9 - never continue an unreviewed unit"))
            return stop("review_unavailable", outcome.error_message, WAIT_FOR_OWNER)

        decision: CodexDecision = outcome.decision
        self.machine.transition(VALIDATE_DECISION, "decision_received",
                                detail={"cycle": cycle,
                                        "decision_digest": outcome.decision_digest})
        land(VALIDATE_DECISION)
        self.machine.transition(
            POLICY_CHECK, "decision_schema_valid",
            detail={"cycle": cycle, "decision": decision.decision,
                    "model_used": outcome.model_used,
                    "reviewed_checkpoint": decision.reviewed_checkpoint_id})
        land(POLICY_CHECK)
        result.decision = decision.decision

        # --- POLICY_CHECK ----------------------------------------------------
        action = ProposedAction(
            kind="forwarded_prompt",
            tool_name="forward_prompt",
            command_text=decision.next_claude_prompt,
            branch=self.authority.branch,
            request_id=f"{self.run_id}/cycle/{cycle}",
            stated_reason=decision.next_claude_prompt[:200],
        )
        verdict = evaluate_policy(action, authority=self.authority, mode=self.mode,
                                  config=self.policy_config)
        if outcome.tier is not None:
            verdict = apply_model_recommendation(verdict, outcome.tier.tier,
                                                 source="codex_decision")
            if outcome.tier.synchronous_stop:
                verdict = dataclasses.replace(verdict, synchronous_stop=True)
        result.tier = verdict.tier
        result.reason_code = verdict.reason_code

        # HARD-DENY first, and DENY_AND_HALT is a synchronous stop.
        if verdict.tier == HARD_DENY:
            if verdict.outcome == DENY_AND_HALT:
                self.machine.transition(PAUSED_RECOVERY, "deny_and_halt",
                                        detail={"cycle": cycle,
                                                "reason_code": verdict.reason_code,
                                                "reason": verdict.reason})
                touches.append(self._touch(
                    TOUCH_SYNCHRONOUS_STOP, reason_code=verdict.reason_code,
                    reason=verdict.reason, cycle=cycle, basis="S4.4 DENY_AND_HALT"))
                return stop("deny_and_halt", verdict.reason, PAUSED_RECOVERY)
            # DENY_AND_CONTINUE: the action is refused, the run is not stopped.
            result.reason = verdict.reason
            result.notes += ("deny_and_continue",)
            result.owner_touches = tuple(touches)
            result.notify_events = tuple(notify)
            return result

        if decision.decision == "HALT_UNSAFE":
            self.machine.transition(HALTED, "decision_halt_unsafe",
                                    detail={"cycle": cycle,
                                            "findings": decision.blocking_findings})
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="halt_unsafe",
                reason="HALT_UNSAFE always pauses synchronously", cycle=cycle,
                basis="S9"))
            return stop("halt_unsafe", "HALT_UNSAFE", HALTED)

        if decision.decision == "STOP_FOR_OWNER":
            self.machine.transition(WAIT_FOR_OWNER, "tier_ask_blocking",
                                    detail={"cycle": cycle,
                                            "owner_question": decision.owner_question,
                                            "reason_code": verdict.reason_code})
            kind = (TOUCH_SYNCHRONOUS_STOP if is_synchronous_stop(verdict)
                    else TOUCH_BLOCKING_ASK)
            touches.append(self._touch(
                kind, reason_code=verdict.reason_code,
                reason=decision.owner_question, cycle=cycle,
                basis="S9 STOP_FOR_OWNER"))
            return stop("stop_for_owner", decision.owner_question, WAIT_FOR_OWNER)

        if decision.decision == "ROTATE_SESSION":
            self.machine.transition(PREPARE_ROTATION, "decision_rotate_session",
                                    detail={"cycle": cycle,
                                            "rotation_reason": decision.rotation_reason})
            return stop("rotate_session", decision.rotation_reason, PREPARE_ROTATION)

        if decision.decision == "COMPLETE":
            self.machine.transition(
                COMPLETE, "decision_complete",
                detail={"cycle": cycle, "evidence_refs": decision.evidence_refs,
                        "note": "COMPLETE reports the AUTHORIZED STAGE is finished. It "
                                "never merges, accepts, deploys, or closes an owner gate."})
            return stop("stage_complete", "the authorized stage is evidenced complete",
                        COMPLETE)

        # CONTINUE / REVISE: there is a prompt to forward.
        if verdict.tier == ASK:
            self.machine.transition(WAIT_FOR_OWNER, "tier_ask_blocking",
                                    detail={"cycle": cycle,
                                            "reason_code": verdict.reason_code})
            touches.append(self._touch(
                TOUCH_BLOCKING_ASK, reason_code=verdict.reason_code,
                reason=verdict.reason, cycle=cycle, basis="S4.3"))
            return stop("ask_blocking", verdict.reason, WAIT_FOR_OWNER)

        if verdict.tier == NOTIFY:
            notify.append(verdict.reason_code)

        forwarded_prompt = build_forwarded_prompt(
            decision,
            task_id=self.config.task_id,
            stage=self.config.stage,
            allowed_paths=self.config.allowed_paths or self.authority.allowed_paths,
            packet_reference=self.config.packet_reference or packet.packet_digest,
            stop_conditions=self.config.stop_conditions)
        prompt_digest = self.approval_digest_for(decision)
        result.pending_prompt_digest = prompt_digest

        # --- SHADOW: forward NOTHING ----------------------------------------
        if not self.config.forwards:
            plan = ShadowPlan(
                cycle=cycle, would_forward=True, would_transition_to=FORWARD_PROMPT,
                prompt_digest=prompt_digest,
                prompt_preview=forwarded_prompt[:400],
                decision=decision.decision, tier=verdict.tier,
                recorded_at_utc=to_utc_iso())
            self.journal.set_state(f"shadow_plan/{self.run_id}/{cycle}", plan.to_dict())
            if self.audit is not None:
                self.audit.append(
                    "shadow_would_have_forwarded", run_id=self.run_id,
                    checkpoint_id=checkpoint.checkpoint_id,
                    output_digest=prompt_digest, policy_result=verdict.reason_code,
                    detail={"cycle": cycle, "decision": decision.decision,
                            "forwarded": False,
                            "note": "shadow mode forwards nothing; this records what "
                                    "WOULD have happened"})
            result.shadow_plan = plan
            result.forwarded = False
            result.reason = "shadow mode: recorded, not forwarded"
            result.owner_touches = tuple(touches)
            result.notify_events = tuple(notify)
            return result

        # --- SUPERVISED: the owner approves each forwarded prompt -----------
        self.machine.transition(
            WAIT_FOR_OWNER, "tier_ask_blocking",
            detail={"cycle": cycle, "reason_code": "supervised_mode_operator_approval",
                    "prompt_digest": prompt_digest,
                    "note": "supervised mode holds every forwarded prompt for an explicit "
                            "operator approval bound to this digest (S12)"})
        land(WAIT_FOR_OWNER)
        self.journal.set_state(f"pending_prompt/{self.run_id}",
                               {"cycle": cycle, "digest": prompt_digest,
                                "decision": decision.decision,
                                "created_at_utc": to_utc_iso()})
        touches.append(self._touch(
            TOUCH_SUPERVISED_APPROVAL, reason_code="supervised_mode_operator_approval",
            reason="supervised mode requires the owner to approve this exact prompt",
            cycle=cycle,
            basis="S12 - a debugging and fallback mode, not the destination; NOT counted "
                  "against the S16.7 budget, which measures the target operating mode"))

        approved = self._await_approval(prompt_digest, forwarded_prompt)
        if not approved:
            return stop("operator_declined",
                        "the operator did not approve the pending prompt", WAIT_FOR_OWNER)

        self.machine.transition(FORWARD_PROMPT, "owner_approved_pending_prompt",
                                detail={"cycle": cycle, "prompt_digest": prompt_digest})
        land(FORWARD_PROMPT)

        forward = self.forward_exactly_once(forwarded_prompt, cycle=cycle,
                                            decision=decision)
        result.forward = forward
        result.forwarded = forward.sent
        if forward.sent:
            self._forwarded.append(forward.message_id)
            self.machine.transition(CLAUDE_RUNNING, "prompt_forwarded",
                                    detail={"cycle": cycle,
                                            "message_id": forward.message_id})
            land(CLAUDE_RUNNING)
            if self.breakers is not None:
                self.breakers.record_progress()
        result.owner_touches = tuple(touches)
        result.notify_events = tuple(notify)
        return result

    # -- evidence -----------------------------------------------------------

    def _collect(self, checkpoint: ClaudeCheckpoint) -> Any:
        git_facts = {}
        project_control = {}
        if self.collector is not None:
            git_facts = self.collector.collect_git_facts()
            project_control = self.collector.collect_project_control()
        return self._build_packet(
            run_id=self.run_id,
            task_id=self.config.task_id,
            checkpoint_id=checkpoint.checkpoint_id,
            checkpoint=checkpoint.to_dict(),
            git_facts=git_facts,
            project_control=project_control,
            never_send=self.never_send)

    # -- approval -----------------------------------------------------------

    def _await_approval(self, prompt_digest: str, prompt: str) -> bool:
        """Supervised mode: an operator approval bound to THIS exact digest.

        With no gate wired the answer is NO. An unanswerable approval never
        becomes an implicit yes (S8.4: "unhandled non-interactive request denies
        rather than hangs").
        """
        if self._approval_gate is None:
            if self.audit is not None:
                self.audit.append(
                    "supervised_approval_unavailable", run_id=self.run_id,
                    input_digest=prompt_digest, decision="deny",
                    detail={"reason": "no operator approval gate is attached; supervised "
                                      "mode denies rather than forwarding unapproved"})
            return False
        answer = bool(self._approval_gate(prompt_digest, prompt))
        if self.audit is not None:
            self.audit.append("supervised_approval_answered", run_id=self.run_id,
                              input_digest=prompt_digest,
                              decision="approve" if answer else "deny",
                              detail={"mode": self.mode})
        return answer

    # -- exactly-once forwarding --------------------------------------------

    def approval_digest_for(self, decision: CodexDecision) -> str:
        """What an operator approves when they approve THIS decision's prompt."""
        return approval_digest(
            task_id=self.config.task_id,
            stage=self.config.stage,
            allowed_paths=self.config.allowed_paths or self.authority.allowed_paths,
            requested_action=decision.next_claude_prompt,
            stop_conditions=self.config.stop_conditions)

    def forward_message_id(self, cycle: int, prompt: str,
                           *, decision: CodexDecision | None = None) -> str:
        """Deterministic id: the same logical prompt always has the same id.

        Keyed on the INSTRUCTION when a decision is available, so a crash that
        forces a re-render (new timestamp, new packet reference) resumes the same
        message instead of minting a second one for the same instruction.
        """
        key = (self.approval_digest_for(decision) if decision is not None
               else digest_of(prompt))
        return f"{self.run_id}/fwd/{cycle}/{key[:16]}"

    def _outbox_state(self, message_id: str) -> str:
        """`unsent` | `sent` for a row the outbox already holds.

        Called only after `enqueue_outbound` reported a duplicate, i.e. the row
        exists for certain. If it is still in the unsent set the previous attempt
        crashed between enqueue and send; otherwise it was sent.
        """
        for envelope in self.journal.unsent_outbound():
            if envelope.get("message_id") == message_id:
                return "unsent"
        return "sent"

    def forward_exactly_once(self, prompt: str, *, cycle: int,
                             decision: CodexDecision) -> ForwardResult:
        """Journal, then send, then mark sent. A repeat never sends twice."""
        self.assert_forwarding_allowed()
        self._guard()
        message_id = self.forward_message_id(cycle, prompt, decision=decision)
        payload = {
            "prompt": prompt,
            "prompt_digest": digest_of(prompt),                    # exact bytes sent
            "approval_digest": self.approval_digest_for(decision),  # what was approved
            "decision": decision.decision,
            "reviewed_checkpoint_id": decision.reviewed_checkpoint_id,
            "task_id": self.config.task_id,
            "stage": self.config.stage,
        }
        envelope = build_envelope(
            payload=payload, payload_type="forwarded_prompt", run_id=self.run_id,
            task_id=self.config.task_id, sequence=max(1, cycle),
            producer="supervisor", producer_version=CONTROLLER_VERSION,
            correlation_id=decision.reviewed_checkpoint_id or self.run_id,
            message_id=message_id)

        resumed = False
        try:
            self.journal.enqueue_outbound(message_id, envelope.to_dict())
        except JournalError as exc:
            if exc.code != "duplicate_outbound":
                raise
            state = self._outbox_state(message_id)
            if state == "sent":
                if self.audit is not None:
                    self.audit.append(
                        "forward_duplicate_suppressed", run_id=self.run_id,
                        output_digest=digest_of(prompt),
                        detail={"message_id": message_id, "cycle": cycle,
                                "note": "this exact prompt was already forwarded; a "
                                        "second send is never performed"})
                return ForwardResult(
                    message_id, sent=False, duplicate_suppressed=True,
                    reason="already forwarded exactly once; not sent again")
            resumed = True

        # The "send" is the durable handoff to the worker's next unit. It is
        # marked sent only AFTER the outbox row exists, so a crash between the
        # two leaves an unsent row that is resumed, never re-minted.
        self.journal.mark_sent(message_id)
        if self.audit is not None:
            self.audit.append("prompt_forwarded", run_id=self.run_id,
                              output_digest=digest_of(prompt),
                              detail={"message_id": message_id, "cycle": cycle,
                                      "resumed_unsent": resumed})
        return ForwardResult(message_id, sent=True, resumed_unsent=resumed)

    # -- the run ------------------------------------------------------------

    def run(self, first_prompt: str) -> LoopRun:
        """Run bounded cycles until the loop stops or the cycle bound is reached."""
        cycles: list[CycleResult] = []
        prompt = first_prompt
        stopped = ""
        for index in range(1, self.config.max_cycles + 1):
            result = self.run_cycle(prompt, cycle=index)
            cycles.append(result)
            if result.stopped:
                stopped = result.stopped
                break
            if not result.continues:
                stopped = "cycle_did_not_continue"
                break
            if not self.config.forwards:
                stopped = "shadow_observation_complete"
                break
            if result.forward is not None and not result.forward.sent:
                stopped = "forward_suppressed"
                break
        else:
            stopped = "max_cycles_reached"
        return LoopRun(
            run_id=self.run_id, mode=self.mode, cycles=tuple(cycles),
            final_state=self.machine.current_state, stopped=stopped,
            budget=self.touches.report(),
            forwarded_message_ids=tuple(self._forwarded),
            provider_calls=self.provider_calls)
