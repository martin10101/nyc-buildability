#!/usr/bin/env python3
"""The deterministic supervisor state machine (D-007 S7).

Every state named in S7 exists here, and every transition is an explicit table
entry with a documented trigger. The rules S7 demands, and where each is met:

* **documented trigger** - `TRANSITIONS` carries a `doc` string per edge.
* **validates required inputs** - `transition()` refuses an unknown state,
  an unknown trigger, and an edge that is not in the table.
* **writes one audit event** - exactly one `AuditLog.append` per applied
  transition (skipped for an idempotent no-op, which is not a new event).
* **idempotent** - re-issuing the transition that was just applied is a no-op
  that reports `applied=False` rather than duplicating work.
* **refuses illegal transitions** - `IllegalTransitionError`.
* **commits transactionally and flushes durably before the next side effect** -
  `transition()` commits the journal FIRST, appends the audit event SECOND, and
  only then invokes the caller's `side_effect`. If the process dies at any point,
  the journal is the recovery truth and no side effect ran un-journaled.
* **survives process restart without duplicating a Claude action** -
  `current_state` is read from the journal, never from memory, so a fresh
  process resumes exactly where the last COMMIT left it.

Phase 1 scope note: this module owns transition LEGALITY and DURABILITY. What
each state actually *does* (launching Claude, building evidence packets, running
Codex) is Phases 2-3. Nothing here forwards a prompt or performs an external
effect.
"""
from __future__ import annotations

import dataclasses
from typing import Callable

from .audit_log import AuditLog
from .durable_state import DurableJournal

# --------------------------------------------------------------------------
# States (S7)
# --------------------------------------------------------------------------

IDLE = "IDLE"
RECOVER_BOOT = "RECOVER_BOOT"
PREFLIGHT = "PREFLIGHT"
START_CLAUDE = "START_CLAUDE"
CLAUDE_RUNNING = "CLAUDE_RUNNING"
ROTATION_PENDING = "ROTATION_PENDING"
CHECKPOINT_RECEIVED = "CHECKPOINT_RECEIVED"
COLLECT_EVIDENCE = "COLLECT_EVIDENCE"
CODEX_REVIEW = "CODEX_REVIEW"
VALIDATE_DECISION = "VALIDATE_DECISION"
POLICY_CHECK = "POLICY_CHECK"
FORWARD_PROMPT = "FORWARD_PROMPT"
WAIT_FOR_OWNER = "WAIT_FOR_OWNER"
PAUSED_RECOVERY = "PAUSED_RECOVERY"
RECONCILE_EXTERNAL_EFFECT = "RECONCILE_EXTERNAL_EFFECT"
USAGE_LIMIT_WAIT = "USAGE_LIMIT_WAIT"
SCHEDULED_RESUME = "SCHEDULED_RESUME"
PREPARE_ROTATION = "PREPARE_ROTATION"
VERIFY_HANDOFF = "VERIFY_HANDOFF"
START_FRESH_SESSION = "START_FRESH_SESSION"
COMPLETE = "COMPLETE"
EMERGENCY_STOPPED = "EMERGENCY_STOPPED"
HALTED = "HALTED"

STATES: tuple[str, ...] = (
    IDLE, RECOVER_BOOT, PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING,
    ROTATION_PENDING, CHECKPOINT_RECEIVED, COLLECT_EVIDENCE, CODEX_REVIEW,
    VALIDATE_DECISION, POLICY_CHECK, FORWARD_PROMPT, WAIT_FOR_OWNER,
    PAUSED_RECOVERY, RECONCILE_EXTERNAL_EFFECT, USAGE_LIMIT_WAIT,
    SCHEDULED_RESUME, PREPARE_ROTATION, VERIFY_HANDOFF, START_FRESH_SESSION,
    COMPLETE, EMERGENCY_STOPPED, HALTED,
)

#: States in which the supervisor performs NO provider work and NO side effects
#: until an explicit owner action moves it (S4.5 synchronous stops + S12 flags).
BLOCKING_STATES: frozenset[str] = frozenset({
    WAIT_FOR_OWNER, PAUSED_RECOVERY, EMERGENCY_STOPPED, HALTED,
})

#: States from which a run does not continue on its own.
TERMINAL_STATES: frozenset[str] = frozenset({COMPLETE, EMERGENCY_STOPPED, HALTED})

#: The state a brand-new journal starts in.
INITIAL_STATE = IDLE


# --------------------------------------------------------------------------
# Transition table
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Transition:
    state_from: str
    state_to: str
    trigger: str
    doc: str


def _t(state_from: str, state_to: str, trigger: str, doc: str) -> Transition:
    return Transition(state_from, state_to, trigger, doc)


TRANSITIONS: tuple[Transition, ...] = (
    # --- entry ---------------------------------------------------------------
    _t(IDLE, PREFLIGHT, "start_command",
       "Operator ran `start --mode ...`; begin preflight."),
    _t(IDLE, RECOVER_BOOT, "discontinuity_detected",
       "Process started after a crash, reboot, or unclean shutdown (S11.5)."),

    # --- recovery ------------------------------------------------------------
    _t(RECOVER_BOOT, PREFLIGHT, "recovery_safe_checkpoint",
       "SAFE_CHECKPOINT: last action has a verified after-effect and invariants match."),
    _t(RECOVER_BOOT, RECONCILE_EXTERNAL_EFFECT, "recovery_ambiguous_effect",
       "AMBIGUOUS_EFFECT: an effect may have happened without a verified after-effect."),
    _t(RECOVER_BOOT, PAUSED_RECOVERY, "recovery_unsafe_or_drifted",
       "UNSAFE_OR_DRIFTED: integrity, authority, identity, or toolchain no longer matches."),
    _t(RECOVER_BOOT, USAGE_LIMIT_WAIT, "recovery_restores_deadline",
       "Recovery found a persisted usage-limit deadline; restore the timer, contact nobody."),
    _t(RECONCILE_EXTERNAL_EFFECT, PREFLIGHT, "effect_proven_reconciled",
       "Read-only evidence proved whether the effect occurred; no blind rerun happened."),
    _t(RECONCILE_EXTERNAL_EFFECT, PAUSED_RECOVERY, "effect_unprovable",
       "The effect could not be proven either way: synchronous stop (S11.5)."),

    # --- preflight and dispatch ---------------------------------------------
    _t(PREFLIGHT, START_CLAUDE, "preflight_pass",
       "Manifest, journal, lock, config, models, and capabilities all verified."),
    _t(PREFLIGHT, PAUSED_RECOVERY, "controller_integrity_failure",
       "Controller manifest or executable/config drift failed closed (S13.1/S13.4)."),
    _t(PREFLIGHT, WAIT_FOR_OWNER, "preflight_requires_owner",
       "Preflight surfaced an owner-gated item (for example an exhausted model chain)."),
    _t(PREFLIGHT, HALTED, "preflight_fatal",
       "Preflight found an unrecoverable configuration or environment fault."),
    _t(START_CLAUDE, CLAUDE_RUNNING, "claude_process_started",
       "The bounded Claude subprocess launched with a recorded session id."),
    _t(START_CLAUDE, HALTED, "claude_start_failed",
       "The worker process could not be started within the restart budget."),

    # --- the working loop ----------------------------------------------------
    _t(CLAUDE_RUNNING, CHECKPOINT_RECEIVED, "valid_checkpoint_received",
       "The worker returned one schema-valid structured checkpoint."),
    _t(CLAUDE_RUNNING, ROTATION_PENDING, "rotation_threshold_crossed",
       "A usage/context threshold was crossed MID-UNIT: flag only, never terminate (S11.2)."),
    _t(CLAUDE_RUNNING, USAGE_LIMIT_WAIT, "usage_limit_notice",
       "A trustworthy provider limit notice with a parseable reset time was observed."),
    _t(CLAUDE_RUNNING, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Explicit owner emergency stop; child trees terminated, evidence preserved."),
    _t(CLAUDE_RUNNING, PAUSED_RECOVERY, "unsafe_condition",
       "A S4.5 synchronous-stop condition fired during the run."),
    _t(CLAUDE_RUNNING, HALTED, "unrecoverable_worker_failure",
       "The worker failed beyond the bounded retry budget with no safe continuation."),
    _t(ROTATION_PENDING, CHECKPOINT_RECEIVED, "unit_reached_terminal_checkpoint",
       "The in-flight unit finished normally; rotation happens BEFORE the next unit."),
    _t(ROTATION_PENDING, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Emergency stop is one of the few things that may interrupt a dispatched unit."),

    _t(CHECKPOINT_RECEIVED, COLLECT_EVIDENCE, "checkpoint_validated",
       "The checkpoint parsed, validated, and correlated to the expected unit."),
    _t(CHECKPOINT_RECEIVED, PREPARE_ROTATION, "rotation_pending_set",
       "rotation_pending was set; rotate before dispatching further work."),
    _t(CHECKPOINT_RECEIVED, PAUSED_RECOVERY, "checkpoint_unsafe",
       "The checkpoint itself indicated a S4.5 condition (for example suspected leakage)."),

    _t(COLLECT_EVIDENCE, CODEX_REVIEW, "evidence_packet_built",
       "A bounded, digest-bound evidence packet was assembled within the size limit."),
    _t(COLLECT_EVIDENCE, WAIT_FOR_OWNER, "evidence_incomplete_ask",
       "Material evidence could not be gathered safely; queue an ASK rather than omit it."),
    _t(COLLECT_EVIDENCE, PAUSED_RECOVERY, "suspected_secret_leak",
       "A suspected secret in a packet or log: synchronous stop (S4.5)."),

    _t(CODEX_REVIEW, VALIDATE_DECISION, "decision_received",
       "The fresh read-only reviewer returned output to validate."),
    _t(CODEX_REVIEW, USAGE_LIMIT_WAIT, "codex_rate_limited",
       "The reviewer is rate-limited: hold at the completed checkpoint, never continue "
       "unreviewed."),
    _t(CODEX_REVIEW, WAIT_FOR_OWNER, "codex_unavailable_ask",
       "The reviewer is unavailable and its provider fallback chain is exhausted."),

    _t(VALIDATE_DECISION, POLICY_CHECK, "decision_schema_valid",
       "Exactly one schema-valid decision, correlated to this checkpoint and evidence."),
    _t(VALIDATE_DECISION, CODEX_REVIEW, "decision_invalid_bounded_retry",
       "A schema-invalid answer gets one bounded retry carrying the validation error."),
    _t(VALIDATE_DECISION, HALTED, "decision_invalid_repeatedly",
       "Repeated schema-invalid decisions halt rather than being interpreted."),

    _t(POLICY_CHECK, FORWARD_PROMPT, "tier_auto",
       "The deterministic policy classified the next action AUTO within packet authority."),
    _t(POLICY_CHECK, WAIT_FOR_OWNER, "tier_ask_blocking",
       "An ASK item the current unit cannot proceed without, with no independent unit."),
    _t(POLICY_CHECK, PREPARE_ROTATION, "decision_rotate_session",
       "A valid ROTATE_SESSION decision with a reason and handoff plan."),
    _t(POLICY_CHECK, COMPLETE, "decision_complete",
       "The authorized stage is evidenced complete. This never merges or accepts anything."),
    _t(POLICY_CHECK, PAUSED_RECOVERY, "deny_and_halt",
       "A DENY_AND_HALT outcome: bypass, credential, controller-mutation, or audit-disabling "
       "attempt (S4.4)."),
    _t(POLICY_CHECK, HALTED, "decision_halt_unsafe",
       "A valid HALT_UNSAFE decision with a concrete safety reason."),

    _t(FORWARD_PROMPT, CLAUDE_RUNNING, "prompt_forwarded",
       "Exactly-once forwarding of the next authorized prompt to the recorded session."),

    # --- rotation ------------------------------------------------------------
    _t(PREPARE_ROTATION, VERIFY_HANDOFF, "handoff_generated",
       "The worker produced a structured handoff at a safe checkpoint."),
    _t(PREPARE_ROTATION, PAUSED_RECOVERY, "unsafe_rotation_point",
       "Rotation was attempted while work was in flight or state was ambiguous (S11.3)."),
    _t(VERIFY_HANDOFF, START_FRESH_SESSION, "handoff_verified",
       "A fresh read-only reviewer using review_model verified the handoff against evidence."),
    _t(VERIFY_HANDOFF, PREPARE_ROTATION, "handoff_rejected_retry",
       "The handoff was rejected; regenerate it within the bounded retry budget."),
    _t(VERIFY_HANDOFF, WAIT_FOR_OWNER, "handoff_rejected_ask",
       "The handoff could not be verified within budget; queue an ASK."),
    _t(START_FRESH_SESSION, CLAUDE_RUNNING, "new_session_ready",
       "A brand-new session id re-oriented and returned a structured READY checkpoint."),

    # --- waiting -------------------------------------------------------------
    _t(USAGE_LIMIT_WAIT, SCHEDULED_RESUME, "durable_trigger_created",
       "A durable OS trigger was created for resume_not_before_utc (never a sleep loop)."),
    _t(USAGE_LIMIT_WAIT, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Emergency stop suppresses any scheduled wake."),
    _t(USAGE_LIMIT_WAIT, PAUSED_RECOVERY, "reset_time_unusable",
       "The reset time was ambiguous, implausible, or expired; never guess a timer."),
    _t(SCHEDULED_RESUME, PREFLIGHT, "deadline_reached_revalidated",
       "The deadline passed and the full revalidation set passed before contacting anyone."),
    _t(SCHEDULED_RESUME, USAGE_LIMIT_WAIT, "still_limited_reschedule",
       "The provider is still limited; persist a new deadline and replace the trigger."),
    _t(SCHEDULED_RESUME, PAUSED_RECOVERY, "wake_revalidation_failed",
       "Revalidation at wake found drift; stop rather than resume."),

    _t(WAIT_FOR_OWNER, PREFLIGHT, "owner_answer_validated",
       "The owner answered through an authenticated path; digest and repo state revalidated."),
    _t(WAIT_FOR_OWNER, FORWARD_PROMPT, "owner_approved_pending_prompt",
       "The owner approved the exact pending prompt; forward it unchanged."),
    _t(WAIT_FOR_OWNER, EMERGENCY_STOPPED, "owner_emergency_stop",
       "The owner stopped the run instead of answering."),
    _t(WAIT_FOR_OWNER, COMPLETE, "owner_closed_stage",
       "The owner declared the authorized stage finished."),
    _t(WAIT_FOR_OWNER, HALTED, "owner_halt",
       "The owner halted the run."),

    _t(PAUSED_RECOVERY, PREFLIGHT, "owner_cleared_pause",
       "The owner resolved the pause condition and explicitly resumed."),
    _t(PAUSED_RECOVERY, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Escalation from a pause to a full stop."),
    _t(PAUSED_RECOVERY, HALTED, "owner_halt",
       "The owner halted rather than resuming."),

    # --- exits ---------------------------------------------------------------
    _t(COMPLETE, IDLE, "run_closed",
       "The run was closed out. Merge and acceptance remain owner gates, never done here."),
    _t(EMERGENCY_STOPPED, IDLE, "owner_explicit_restart",
       "A durable stop flag never resumes by itself; only an explicit owner command clears it."),
    _t(HALTED, IDLE, "owner_explicit_restart",
       "Halt is cleared only by an explicit owner command after the cause is addressed."),
)

#: index: state_from -> state_to -> {trigger: doc}
_INDEX: dict[str, dict[str, dict[str, str]]] = {}
for _transition in TRANSITIONS:
    _INDEX.setdefault(_transition.state_from, {}) \
          .setdefault(_transition.state_to, {})[_transition.trigger] = _transition.doc

TRIGGERS: frozenset[str] = frozenset(t.trigger for t in TRANSITIONS)


class IllegalTransitionError(Exception):
    """A transition that is not in the table was attempted. Always refused."""

    def __init__(self, state_from: str, state_to: str, trigger: str, reason: str) -> None:
        super().__init__(f"illegal transition {state_from} -> {state_to} "
                         f"(trigger {trigger!r}): {reason}")
        self.state_from = state_from
        self.state_to = state_to
        self.trigger = trigger
        self.reason = reason


def legal_targets(state_from: str) -> tuple[str, ...]:
    return tuple(sorted(_INDEX.get(state_from, {})))


def is_legal(state_from: str, state_to: str, trigger: str) -> bool:
    return trigger in _INDEX.get(state_from, {}).get(state_to, {})


def transition_doc(state_from: str, state_to: str, trigger: str) -> str:
    return _INDEX.get(state_from, {}).get(state_to, {}).get(trigger, "")


# --------------------------------------------------------------------------
# Runtime
# --------------------------------------------------------------------------

STATE_KEY = "current_state"
LAST_TRIGGER_KEY = "last_trigger"


@dataclasses.dataclass(frozen=True)
class TransitionResult:
    applied: bool
    state_from: str
    state_to: str
    trigger: str
    sequence: int
    reason: str = ""


class StateMachine:
    """Durable, auditable driver over the S7 transition table."""

    def __init__(self, journal: DurableJournal, audit: AuditLog, run_id: str) -> None:
        self.journal = journal
        self.audit = audit
        self.run_id = run_id

    @property
    def current_state(self) -> str:
        """Read from the JOURNAL, never from memory, so restarts resume exactly."""
        return str(self.journal.get_state(STATE_KEY, INITIAL_STATE))

    @property
    def last_trigger(self) -> str:
        return str(self.journal.get_state(LAST_TRIGGER_KEY, ""))

    def transition(
        self,
        state_to: str,
        trigger: str,
        *,
        detail: dict[str, object] | None = None,
        side_effect: Callable[[], None] | None = None,
    ) -> TransitionResult:
        """Apply one transition: validate, COMMIT, audit, then run the side effect.

        The ordering is the point. The journal commit is durable before the audit
        event, and the audit event is written before any side effect runs, so a
        crash can never leave an un-journaled effect behind.
        """
        state_from = self.current_state

        if state_to not in STATES:
            raise IllegalTransitionError(state_from, state_to, trigger,
                                         f"unknown state {state_to!r}")
        if trigger not in TRIGGERS:
            raise IllegalTransitionError(state_from, state_to, trigger,
                                         f"unknown trigger {trigger!r}")

        # Idempotency: the same transition applied twice is a no-op, not a repeat.
        if state_from == state_to and self.last_trigger == trigger:
            return TransitionResult(
                False, state_from, state_to, trigger,
                sequence=self.journal.next_transition_sequence() - 1,
                reason="idempotent_repeat")

        if not is_legal(state_from, state_to, trigger):
            allowed = legal_targets(state_from)
            raise IllegalTransitionError(
                state_from, state_to, trigger,
                f"not in the transition table; legal targets from {state_from} are "
                f"{list(allowed)}")

        record = self.journal.record_transition(
            state_from=state_from,
            state_to=state_to,
            trigger=trigger,
            run_id=self.run_id,
            detail=detail or {},
            state_updates={STATE_KEY: state_to, LAST_TRIGGER_KEY: trigger},
        )

        self.audit.append(
            "state_transition",
            run_id=self.run_id,
            state_from=state_from,
            state_to=state_to,
            policy_result=trigger,
            detail={"sequence": record.sequence,
                    "doc": transition_doc(state_from, state_to, trigger),
                    **(detail or {})},
        )

        if side_effect is not None:
            side_effect()

        return TransitionResult(True, state_from, state_to, trigger, record.sequence)

    def assert_can_act(self) -> None:
        """S13.12 invariant 5: no action while paused, halted, or awaiting an owner gate."""
        state = self.current_state
        if state in BLOCKING_STATES:
            raise IllegalTransitionError(
                state, state, "act",
                f"no action is permitted while the supervisor is in {state}")
