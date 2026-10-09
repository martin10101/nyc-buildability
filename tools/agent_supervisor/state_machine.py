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

# D-024 section-3 additions (M0-T092, cited per state; supervisor-freeze
# qualifying evidence D-024-R102). Each is a distinction R029 requires that no
# existing state or durable-flag composite could honestly express — see the
# M0-T092 report §4 for the full 18-distinction mapping proof.
GRACEFUL_STOPPING = "GRACEFUL_STOPPING"      # R029 "graceful stopping"
AWAIT_CHILDREN = "AWAIT_CHILDREN"            # R029 "awaiting/reconciling child work"
CODEX_OUTAGE_BACKOFF = "CODEX_OUTAGE_BACKOFF"  # R033 transient-outage backoff
NO_ELIGIBLE_WORK = "NO_ELIGIBLE_WORK"        # R029/R033 bounded idle

# D-024 section-8 Phase-E additions (M0-T093; supervisor-freeze qualifying
# evidence D-024-R103). Two distinctions no existing state expresses:
# a mechanically RESTRICTED 4.8 continuity bridge is not CLAUDE_RUNNING (the
# bridge may only finish/collect/checkpoint/handoff, R070 step 3), and a fresh
# Fable re-entry carrying a RE-PRESENTED refused request under the durable
# two-attempt cap is not an ordinary START_FRESH_SESSION successor (R071).
# Both are journaled on every entry/exit like every other state. These states
# exist for the R595-activated path and are exercised deterministically in
# tests; on this build the loop's refusal seam records intent and pauses
# (SHADOW-ONLY) without entering them.
GUARDRAIL_BRIDGE = "GUARDRAIL_BRIDGE"        # R070 bounded 4.8 continuity bridge
REPRESENT_FABLE = "REPRESENT_FABLE"          # R071 re-presented Fable re-entry

STATES: tuple[str, ...] = (
    IDLE, RECOVER_BOOT, PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING,
    ROTATION_PENDING, CHECKPOINT_RECEIVED, COLLECT_EVIDENCE, CODEX_REVIEW,
    VALIDATE_DECISION, POLICY_CHECK, FORWARD_PROMPT, WAIT_FOR_OWNER,
    PAUSED_RECOVERY, RECONCILE_EXTERNAL_EFFECT, USAGE_LIMIT_WAIT,
    SCHEDULED_RESUME, PREPARE_ROTATION, VERIFY_HANDOFF, START_FRESH_SESSION,
    COMPLETE, EMERGENCY_STOPPED, HALTED,
    GRACEFUL_STOPPING, AWAIT_CHILDREN, CODEX_OUTAGE_BACKOFF, NO_ELIGIBLE_WORK,
    GUARDRAIL_BRIDGE, REPRESENT_FABLE,
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
    # V1.1 correction B-4: the per-checkpoint review breaker (S13.8) trips BEFORE
    # the reviewer is invoked, and a trip is a synchronous pause exactly like the
    # claude_runs breaker - which needs a legal pause edge from CODEX_REVIEW.
    _t(CODEX_REVIEW, PAUSED_RECOVERY, "unsafe_condition",
       "A S4.5 synchronous-stop condition fired before dispatching the review (for "
       "example the per-checkpoint review circuit breaker tripped)."),

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
    # V1.1 correction B-2: POLICY_CHECK previously had no legal exit after a
    # completed shadow observation or a DENY_AND_CONTINUE refusal, so every such
    # cycle stranded the journal (the only remedy was parking it - the exact
    # continuity loss pilot finding F-2 describes, in a second state). The cycle
    # now CLOSES explicitly into PREFLIGHT, which is a legal cycle-entry state,
    # so the same journal is re-startable. PREFLIGHT rather than IDLE because
    # IDLE's only outbound trigger is the operator's `start_command`, which was
    # already given for this run.
    _t(POLICY_CHECK, PREFLIGHT, "cycle_closed",
       "The policy evaluation concluded without forwarding (a completed shadow "
       "observation, or a DENY_AND_CONTINUE refusal of the proposed forward); the "
       "cycle closes into a resumable state instead of stranding the journal."),

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

    # --- D-024 unit F additions (M0-T092; D-024-R102) ------------------------
    # Graceful stop (R026/R027/R029): a durable owner graceful-stop intent
    # (stop_intent.GRACEFUL_STOP_KEY) lets the unit ALREADY UNDERWAY reach its
    # seam, lands it, and then stops — it never dispatches queued work.
    _t(CHECKPOINT_RECEIVED, GRACEFUL_STOPPING, "graceful_stop_intent_set",
       "A durable owner graceful stop is set and the in-flight unit reached its "
       "checkpoint: land it and stop; queued work is never dispatched (R026/R029)."),
    _t(RECOVER_BOOT, GRACEFUL_STOPPING, "recovery_finds_graceful_stop",
       "Recovery found a durable graceful-stop intent: the stop SURVIVES the restart "
       "and WINS over queued and recovered work (R026); land what is durable, then stop."),
    _t(GRACEFUL_STOPPING, IDLE, "graceful_stop_landed",
       "The landing finished: children reconciled, external effects settled, the "
       "durable handoff written. The run closes to stopped/inactive (R029)."),
    _t(GRACEFUL_STOPPING, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Escalation while landing: emergency outranks graceful (R027 precedence)."),
    _t(GRACEFUL_STOPPING, PAUSED_RECOVERY, "unsafe_condition",
       "A synchronous-stop condition fired during the graceful landing."),

    # Child drain (R029 'awaiting/reconciling child work'; s6.3/R065): rotation
    # waits while bounded children finish; no new children, no broadened scope.
    _t(PREPARE_ROTATION, AWAIT_CHILDREN, "children_still_draining",
       "Bounded children are still finishing their already-bounded assignments; the "
       "rotation waits and dispatches nothing new (s6.3, R065)."),
    _t(AWAIT_CHILDREN, PREPARE_ROTATION, "children_reconciled",
       "Every child returned a durable handoff and external effects are reconciled; "
       "the rotation proceeds (s6.3)."),
    _t(AWAIT_CHILDREN, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Emergency stop interrupts the drain; child trees terminated, evidence kept."),
    _t(AWAIT_CHILDREN, PAUSED_RECOVERY, "unsafe_condition",
       "A synchronous-stop condition fired while children drained."),

    # Transient supervisor outage (R033): bounded backoff with jitter and a
    # DURABLE retry state (outage_policy.RETRY_KEY) — never a tight loop, never
    # unlimited, and never new producer work without supervision.
    _t(CODEX_REVIEW, CODEX_OUTAGE_BACKOFF, "codex_transient_failure",
       "A transient transport/model/network failure: enter bounded backoff with "
       "jitter and durable retry state; dispatch nothing new (R033)."),
    _t(CODEX_OUTAGE_BACKOFF, CODEX_REVIEW, "outage_retry_due",
       "The durable retry deadline arrived: one bounded retry attempt (R033)."),
    _t(CODEX_OUTAGE_BACKOFF, WAIT_FOR_OWNER, "outage_blocked_with_handoff",
       "Auth, billing, revoked access, incompatibility, or the bounded attempts are "
       "exhausted: blocked-with-handoff for the owner, never a further retry (R033)."),
    _t(CODEX_OUTAGE_BACKOFF, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Emergency stop suppresses any pending retry."),

    # Bounded idle (R029 'idle because no eligible authorized task exists';
    # R028 'no busy loop when there is no eligible work'; R033 bounded idle).
    _t(POLICY_CHECK, NO_ELIGIBLE_WORK, "no_eligible_authorized_work",
       "No eligible authorized task exists: dwell until a durable bounded deadline "
       "(outage_policy.IDLE_KEY); never a busy loop (R028/R033)."),
    _t(NO_ELIGIBLE_WORK, PREFLIGHT, "idle_recheck_due",
       "The bounded idle deadline arrived: revalidate through PREFLIGHT (the legal "
       "cycle-entry state, V1.1 B-2 precedent) before contacting anyone."),
    _t(NO_ELIGIBLE_WORK, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Emergency stop while idle."),
    _t(NO_ELIGIBLE_WORK, HALTED, "owner_halt",
       "The owner halted the run while it was idle."),

    # --- D-024 unit H1 additions (M0-T093; D-024-R103) -----------------------
    # The guardrail-refusal bridge (R068-R073): entered ONLY on a narrowly
    # recognized refusal with the exact allowlisted continuation option
    # (R069); every edge is journaled. Live actuation of these paths stays
    # owner-gated (R595 + measured-live C1 shape); the deterministic table is
    # complete now so activation changes nothing structural.
    _t(CLAUDE_RUNNING, GUARDRAIL_BRIDGE, "guardrail_refusal_recognized",
       "A narrowly recognized Fable guardrail refusal (R068) with the EXACT "
       "allowlisted continue-with-4.8 option (R069): the bounded continuity "
       "bridge begins - finish/collect/checkpoint/handoff only (R070)."),
    _t(GUARDRAIL_BRIDGE, PREPARE_ROTATION, "bridge_first_seam_reached",
       "The bridge finished the smallest atomic operation, reconciled bounded "
       "children, and validated its checkpoint: retire at the FIRST safe seam "
       "through the standard rotation/handoff machinery toward a fresh Fable 5 "
       "session (R070 step 4); it never continues past the seam."),
    _t(GUARDRAIL_BRIDGE, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Emergency stop interrupts the bridge; evidence preserved."),
    _t(GUARDRAIL_BRIDGE, PAUSED_RECOVERY, "unsafe_condition",
       "A S4.5 synchronous-stop condition fired while the bridge was landing."),
    _t(START_FRESH_SESSION, REPRESENT_FABLE, "represent_refused_request",
       "The fresh Fable 5 session is ready and a durably recorded refused "
       "request is pending: it receives the semantic-preserving re-presented "
       "request (R071/R073) and the digest-bound durable attempt counter "
       "increments (at most two attempts, surviving restart)."),
    _t(REPRESENT_FABLE, CLAUDE_RUNNING, "representation_accepted",
       "Fable accepted the re-presented request: the durable counter records "
       "the success and the normal working loop resumes (R071)."),
    _t(REPRESENT_FABLE, GUARDRAIL_BRIDGE, "refusal_repeated_within_cap",
       "The re-presented request was refused again and the durable counter is "
       "below the two-attempt cap: one more bounded bridge carries continuity "
       "to the next seam for the second and FINAL fresh re-entry (R071)."),
    _t(REPRESENT_FABLE, START_CLAUDE, "refusal_cap_lower_tier",
       "Both fresh Fable attempts received the recognized refusal and the "
       "already-configured lower-tier model passed its stricter workload-fit/"
       "health profile for the SAME bounded task (R072): continue there, "
       "returning to Fable 5 at the next safe seam."),
    _t(REPRESENT_FABLE, WAIT_FOR_OWNER, "refusal_cap_blocked",
       "Both fresh Fable attempts received the recognized refusal and a live "
       "higher-precedence policy forbids (or nothing is configured for) the "
       "narrow lower-tier fallback: blocked, citing the exact conflict for "
       "the owner to reconcile (R072)."),
    _t(REPRESENT_FABLE, EMERGENCY_STOPPED, "owner_emergency_stop",
       "Emergency stop during a re-presentation attempt."),
    _t(REPRESENT_FABLE, PAUSED_RECOVERY, "unsafe_condition",
       "A S4.5 synchronous-stop condition fired during a re-presentation."),

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
