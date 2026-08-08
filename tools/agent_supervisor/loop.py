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
from . import rotation
from .audit_log import AuditChainError
from .circuit_breakers import GAUGE_LIMITS
from .claude_runner import QUOTA_EXHAUSTED_REASON, broker_permission_handler
from .codex_reviewer import build_forwarded_prompt, stamp_forwarded_at
from .config import DEFAULT_ORCHESTRATOR_MODEL_CHAIN, ModelChain
from .durable_state import JournalError
from .evidence import STOP_FOR_OWNER, build_packet
from .models import ClaudeCheckpoint, CodexDecision, QueuedAsk, digest_of, to_utc_iso
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
from .resume_scheduler import EMERGENCY_STOP_KEY
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
#:
#: B-018 (crash-window recovery): START_CLAUDE is ALSO a legal re-entry, but only
#: to RESUME an interrupted launch, never to invent one. The window is narrow and
#: durable: the `preflight_pass -> START_CLAUDE` transition commits (run_cycle
#: ~1607) BEFORE the worker is launched (~1632), and the
#: `START_CLAUDE -> CLAUDE_RUNNING` transition commits only AFTER a real process
#: started (~1637). An external kill inside that gap strands the durable journal
#: at START_CLAUDE with NOTHING launched. The state's own meaning - "about to
#: launch, nothing has launched yet" - is precisely a safe re-entry: run_cycle
#: skips the duplicate preflight transition (the `if entry == PREFLIGHT` guard),
#: dispatches exactly once, and transitions to CLAUDE_RUNNING only on a real
#: process. This never widens who may dispatch: `start` still gates every launch
#: on recover_boot's SAFE_CHECKPOINT classification (cmd_start), which fails
#: closed if any recorded child SURVIVED the crash or a competing writer exists,
#: so a resume can never double-launch or run over an unaccounted worker. Before
#: this, START_CLAUDE's omission left an externally-killed launch permanently
#: unrecoverable: run_cycle raised bad_cycle_entry_state on every operator start
#: even after recover_boot classified SAFE_CHECKPOINT, and no production code drove
#: the S7 exits from START_CLAUDE.
CYCLE_ENTRY_STATES: frozenset[str] = frozenset({PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING})

# --------------------------------------------------------------------------
# Orchestrator-role model substitution (D-004 am.26 / D-007 am.11; R746-R748)
# --------------------------------------------------------------------------
#
# The pinned model is the strict default at a rotation seam: an unavailable pin
# PAUSES for the owner (never a silent substitute). This is the ONE authorized
# exception, and it is deliberately narrow. When the orchestrator-role session's
# pinned model (Fable 5) is unavailable SPECIFICALLY because its quota is
# exhausted, the seam walks the FIXED owner-configured preference chain and
# relaunches EXPLICITLY on the first entry that ACTUALLY launches, records the
# switch as a first-class event, and returns to the pinned model at the next seam
# it is available. It is never silent, it applies to the orchestrator role only,
# and it never touches the reviewer pins (reviews wait for Fable 5 rather than
# fall back - see codex_reviewer.py, untouched here).
#
# D-004-R751/R754/R758 (owner correction, D-007 am.12): the orchestrator does NOT
# choose a model by judgement. It walks the chain in the config, in order,
# first-available-wins, availability decided by an ACTUAL LAUNCH PROBE of the
# exact id (D-004-R752/R753) - never by reading a model picker, which can hide a
# model that is still usable by string. An id outside the chain is never
# selectable, and chain exhaustion STOPS and notifies the owner (D-004-R755); it
# never silently continues on an unlisted or substitute model.
#
# D-007-R606: this trigger is DISTINCT from the 400k context rotation and from a
# mid-task security downgrade. They share this one seam actuator - the safe place
# where no unit is in flight - and nothing else: separate triggers, separate
# reason codes, separate records.

#: The fail-closed default chain, defined once in config.py and re-exported here
#: for callers that build a loop without a controller config.
DEFAULT_MODEL_CHAIN: tuple[str, ...] = DEFAULT_ORCHESTRATOR_MODEL_CHAIN

# `QUOTA_EXHAUSTED_REASON` is imported from claude_runner and re-exported here: it
# is the ONE availability reason_code that authorizes a chain step, and the probe
# that produces it and the seam that consumes it must not be able to drift apart.
# Any other reason (unknown, error, a bare False with no reason) is NOT quota
# exhaustion and keeps the fail-closed pause.

#: The stop code when NO chain entry actually launches (D-004-R755).
CHAIN_EXHAUSTED_STOP = "model_chain_exhausted"


def effective_model(journal: Any, run_id: str, pinned_model: str) -> str:
    """The model this run is ACTUALLY on right now (D-007-R605).

    The pinned model unless a durable orchestrator-role switch is active, in
    which case it is the chain entry that switch selected. Read from the journal
    so a process restart rebuilds the runner on the model the run is really on
    rather than silently reverting to an exhausted pin - the crash-resume half of
    "the switch must reach the actuation".
    """
    record = journal.get_state(f"model_substitution/{run_id}", None)
    if isinstance(record, Mapping) and record.get("active"):
        selected = str(record.get("substitute_model", "") or "")
        if selected:
            return selected
    return pinned_model

#: The one explicit session role the substitution branch requires. Absent (the
#: default) is the worker role, for which an unavailable pin always pauses.
SESSION_ROLE_ORCHESTRATOR = "orchestrator"

#: Recognized explicit session roles. Absent ("") is the worker default.
SESSION_ROLES: tuple[str, ...] = (SESSION_ROLE_ORCHESTRATOR,)


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
    #: D-004 am.26 / D-007 am.11: an EXPLICIT opt-in, default absent. Only an
    #: "orchestrator"-role session may substitute the pinned model at a seam (and
    #: only for quota exhaustion). The worker default ("") always pauses instead.
    session_role: str = ""

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
        if self.session_role and self.session_role not in SESSION_ROLES:
            raise LoopError(
                "unknown_session_role",
                f"{self.session_role!r} is not a recognized session role; the only explicit "
                f"role is {SESSION_ROLE_ORCHESTRATOR!r} (D-004 orchestrator continuity). "
                f"Absent means the worker default, which never substitutes a pinned model.")

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
    #: V1.1 correction B-1: the EXACT prompt bytes of the outbox row this attempt
    #: marked sent - the durable handoff's consumer is `run()`, which passes these
    #: bytes to the next cycle's unit. On a resumed-unsent row this is the
    #: PREVIOUSLY journaled prompt (the row is resumed, never re-rendered).
    #: Empty when nothing was sent.
    sent_prompt: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        # The full prompt is journaled in the outbox envelope; the run report
        # carries its digest rather than duplicating the bytes.
        prompt = data.pop("sent_prompt")
        data["sent_prompt_digest"] = digest_of(prompt) if prompt else ""
        return data


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
    #: V1.2 (D-004): what the just-finished unit reported. Surfaced so the SEAM
    #: in run() can decide a pre-dispatch rotation without re-reading the runner.
    model_mismatch: bool = False
    context_tokens: int = 0
    rotation_pending: bool = False

    @property
    def continues(self) -> bool:
        """True only when the loop may legitimately run another cycle.

        V1.1 correction B-2: POLICY_CHECK is no longer a continuing state. Every
        POLICY_CHECK outcome now either stops the cycle or closes it explicitly
        (`cycle_closed` -> PREFLIGHT), so the only state a further cycle may
        proceed from mid-run is CLAUDE_RUNNING - after a prompt was forwarded.
        """
        return self.reached_state == CLAUDE_RUNNING and not self.stopped

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
    #: V1.2 (D-004): one record per seam rotation performed (model downgrade or
    #: context-threshold crossing). Empty on a run that never rotated.
    rotations: tuple[dict[str, Any], ...] = ()

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
            "rotations": [dict(r) for r in self.rotations],
            "limited_auto_enabled": False,
        }


@dataclasses.dataclass
class SeamRotation:
    """The outcome of one seam rotation attempt (D-004). Never terminates a unit."""

    relaunched: bool
    reason_code: str
    reason: str = ""
    paused: bool = False
    stopped: str = ""
    touch: OwnerTouch | None = None
    record: dict[str, Any] | None = None
    #: D-004 am.26 / D-007 am.11: True when this seam relaunched on the substitute
    #: model (quota exhaustion), and True on the return event when it rotated back.
    substituted: bool = False


@dataclasses.dataclass(frozen=True)
class ModelAvailability:
    """A pinned-model availability probe result (D-004 am.26 / D-007 am.11).

    The probe seam still accepts a bare bool for backward compatibility; a bool
    carries NO reason and is therefore never quota exhaustion (fail closed). To
    authorize a substitution the probe must return this object (or a
    ``(available, reason_code)`` tuple) with ``reason_code == 'quota_exhausted'``.
    An unknown or unparseable reason is not quota exhaustion.
    """

    available: bool
    reason_code: str = ""


# --------------------------------------------------------------------------
# The loop
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Prompt digests: what an approval actually binds to
# --------------------------------------------------------------------------
#
# Historically a rendered forwarded prompt was NOT stable across renders: it
# carried a `FORWARDED AT:` timestamp and a reference to the evidence packet,
# whose own digest moved with the clock and with live git state. Binding an
# approval to those bytes makes a digest-bound approval impossible to honour - the
# operator is shown one digest, and by the time they answer with it the prompt has
# re-rendered to a different one. (Found by running `start --mode supervised` end
# to end: the approval never matched, twice, for two different reasons.)
#
# So the approval digest is computed from the INSTRUCTION FIELDS directly - the
# exact five things S9 says every forwarded prompt carries, plus the task and stage
# that confer authority:
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
#
# M0-T048 (D-010 am.14, R136/R137) went one step further so the FORWARDED CONTENT
# itself - not just the approval - is bound to that operator-named digest.
# `build_forwarded_prompt` now emits a DETERMINISTIC, timestamp-free body that is a
# pure function of the same five canonical fields; the `FORWARDED AT:` clock is
# appended only at actual forward time (`stamp_forwarded_at`) and the volatile
# packet reference is gone. So the timestamp-free body is reconstructable from
# approval-covered material, and `verify_covered_instruction` (below) recomputes it
# at approve/resume and refuses fail-closed unless the persisted structured
# instruction reproduces the operator-named approval digest. An attacker who
# rewrites the parked prompt bytes AND their journal-resident `prompt_bytes_digest`,
# leaving the operator digest untouched, can no longer get altered content
# forwarded: the content is derived from the operator-covered instruction, never
# trusted from the mutable journal bytes.

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


def pending_prompt_key(run_id: str) -> str:
    """The durable key the supervised WAIT parks its held prompt under.

    Kept here so the writer (`run_cycle`), the loop consumer, and the CLI
    `resume-pending-prompt` command cannot drift apart on the key shape.

    The record travels through three shapes, and every consumer keys off the
    field that is present (never a positional guess):

    * PARKED (written by `run_cycle` at the supervised WAIT) -
      ``{"cycle", "digest", "prompt", "reviewed_checkpoint_id", "decision",
      "created_at_utc"}``. ``digest`` is the approval binding the operator must
      name; ``prompt`` is the EXACT held prompt bytes, parked so a DIFFERENT
      process can forward them unchanged (M0-T045).
    * APPROVED (written by `approve_pending_prompt` on a successful
      `resume-pending-prompt`) - ``{"approved": True, "cycle", "prompt",
      "approved_digest", "decision", "prior_digest", "approved_at_utc"}``. The
      ``digest`` key is DROPPED so the re-approval guards (`not
      pending.get("digest")`) stay closed, while ``prompt`` + ``approved_digest``
      carry exactly what a fresh `start` needs to forward once.
    * CONSUMED (written by `consume_pending_prompt` after the forward is sent) -
      ``{"consumed": True, "consumed_at_utc", "prior_digest"}``. Nothing
      approvable and nothing forwardable remains.
    """
    return f"pending_prompt/{run_id}"


def consume_pending_prompt(journal: Any, run_id: str, *, prior_digest: str = "") -> None:
    """Clear the pending_prompt record after it is approved and forwarded (AS-4).

    G5 V1.2.3 LOW finding (project-control/reports/
    M0-T036-V1.2.3-G5-security-delta-review.md): "neither it nor the loop
    consumes/clears the record after use", so in an active supervised
    multi-cycle run a later WAIT for a DIFFERENT ask could still carry a prior
    cycle's pending_prompt, and an operator supplying that (genuine, system-
    recorded) digest would re-fire owner_approved_pending_prompt. Consuming the
    record on a SUCCESSFUL resume drops the digest, so the WAIT guards ("no
    pending-prompt record" / digest mismatch) fail closed on any re-approval:
    a stale record can never be approved twice.
    """
    journal.set_state(
        pending_prompt_key(run_id),
        {"consumed": True, "consumed_at_utc": to_utc_iso(),
         "prior_digest": prior_digest})


def verify_covered_instruction(
        instruction: Any, operator_digest: str, prompt: str, anchor: Any) -> str:
    """Reconstruct the forwarded body from OPERATOR-COVERED material, or fail closed.

    M0-T048 (D-010 am.14, R136): the forwarded content must be cryptographically
    bound to information the operator-named ``approval_digest`` covers, never trusted
    from the mutable journal ``prompt``/``prompt_bytes_digest`` fields alone. This
    recomputes the instruction body from the persisted structured instruction and
    returns it ONLY when:

      1. the persisted structured instruction is present and well-formed (an
         old-shape/missing record REFUSES - it is never treated as journal-resident-
         only verification, AS-6);
      2. ``approval_digest(instruction)`` reproduces the operator-named digest - so
         every field that determines the body is exactly what the operator approved;
      3. (defence in depth, preserving the M0-T046 sealed byte anchor) the park-time
         ``prompt_bytes_digest`` and the parked ``prompt`` bytes both still match the
         reconstruction.

    Because ``build_forwarded_prompt`` is a pure function of the same canonical fields
    ``approval_digest`` covers, step 2 alone already fixes every byte of the returned
    body; steps 1/3 give distinct fail-closed reason codes and keep the earlier
    guarantees intact. Raises ``LoopError`` (``pending_prompt_uncovered`` or
    ``pending_prompt_tampered``) with no side effect on any refusal.
    """
    if not isinstance(instruction, Mapping):
        raise LoopError(
            "pending_prompt_uncovered",
            "the parked record carries no structured approved instruction; refusing "
            "to forward bytes that are not bound to the operator-named approval digest "
            "(old-shape/missing binding material). Fail-closed: no fallback to "
            "journal-resident-only verification")
    try:
        fields = {
            "task_id": str(instruction["task_id"]),
            "stage": str(instruction["stage"]),
            "allowed_paths": list(instruction["allowed_paths"]),
            "requested_action": str(instruction["requested_action"]),
            "stop_conditions": list(instruction["stop_conditions"]),
        }
    except (KeyError, TypeError) as exc:
        raise LoopError(
            "pending_prompt_uncovered",
            f"the parked approved instruction is malformed ({exc!r}); refusing "
            f"fail-closed rather than forward uncovered content") from exc
    if approval_digest(**fields) != operator_digest:
        raise LoopError(
            "pending_prompt_uncovered",
            "the parked approved instruction does not reproduce the operator-named "
            "approval digest; the forwarded content would not be covered by the "
            "operator's approval. Fail-closed: no approval is written")
    expected_body = build_forwarded_prompt(**fields)
    if isinstance(anchor, str) and anchor and digest_of(expected_body) != anchor:
        raise LoopError(
            "pending_prompt_tampered",
            "the park-time byte anchor no longer matches the body reconstructed from "
            "the operator-covered instruction; the parked record was altered after "
            "park. Fail-closed: no approval is written")
    if digest_of(prompt) != digest_of(expected_body):
        raise LoopError(
            "pending_prompt_tampered",
            "the parked prompt bytes no longer match the byte anchor / reconstruction "
            "from the operator-covered instruction; the held prompt was altered after "
            "it was parked. Refusing fail-closed: no approval is written")
    return expected_body


#: The sealed, hash-chained audit event the `resume-pending-prompt` CLI writes on a
#: genuine operator approval. Its ``input_digest`` is the operator-named approval
#: digest; the event lives in the append-only local hash chain (audit_log.py, M0-T046),
#: so forging or rewriting it requires breaking the chain, which `verify_chain` detects.
OPERATOR_APPROVAL_EVENT = "operator_resume_pending_prompt"


def verify_approved_digest_against_audit(
        audit: Any, run_id: str, approved_digest: str) -> None:
    """Cross-check the journal ``approved_digest`` against the SEALED operator approval.

    M0-T048 REWORK (D-010 R145..R150; G3 MAJOR-1): the cross-process resume path must
    NOT trust the mutable journal ``approved_digest`` as the sole record of what the
    operator approved. An attacker with journal write who rewrites ``approved_instruction``
    AND ``approved_digest`` (AND ``prompt``/``prompt_bytes_digest``) self-consistently
    AFTER a genuine approval otherwise slips altered content through the reconstruction
    check (the forged instruction reproduces the forged digest). This anchors the resume
    to the ALREADY-SEALED, hash-chained operator-approval audit evidence instead: the
    ``resume-pending-prompt`` CLI seals an ``operator_resume_pending_prompt``
    (``decision="approve"``) event whose ``input_digest`` is the operator-named digest.
    Rewriting that event requires breaking the chain, which ``verify_chain`` detects.

    Fails closed with a DISTINCT reason code (never fails open, never warn-only) on:
      * no audit log to consult                    -> ``approved_digest_audit_unavailable``
      * an unreadable audit log                    -> ``approval_audit_unreadable``
      * a chain that does not verify (tamper/fork/
        truncate)                                  -> ``approval_audit_chain_invalid``
      * no sealed approval event for this run      -> ``approved_digest_audit_missing``
      * a sealed approval whose operator-named
        digest differs from the journal's          -> ``approved_digest_audit_mismatch``
      * conflicting/duplicated sealed approvals of
        the same digest                            -> ``approved_digest_audit_ambiguous``

    No side effects. The caller seals the refusal (owner requirement: the mismatch must
    be durably recorded) and re-raises fail-closed.
    """
    if audit is None:
        raise LoopError(
            "approved_digest_audit_unavailable",
            "no sealed operator-approval audit evidence is available to cross-check the "
            "journal approved_digest against; refusing fail-closed rather than treating "
            "the mutable journal as the sole record of what the operator approved")
    try:
        verification = audit.verify_chain()
    except Exception as exc:  # a damaged/unreadable log must never fail open
        raise LoopError(
            "approval_audit_unreadable",
            f"the operator-approval audit log is unreadable ({exc}); refusing to forward "
            f"without a verifiable sealed record of the approval") from exc
    if not getattr(verification, "ok", False):
        raise LoopError(
            "approval_audit_chain_invalid",
            f"the operator-approval audit chain does not verify "
            f"({getattr(verification, 'code', '')}: {getattr(verification, 'message', '')}); "
            f"a tampered, forked, or truncated chain can no longer anchor what the "
            f"operator approved, so the resume refuses fail-closed")
    try:
        records = audit.read_all()
    except Exception as exc:
        raise LoopError(
            "approval_audit_unreadable",
            f"the operator-approval audit log could not be read ({exc}); refusing to "
            f"forward without a verifiable sealed record of the approval") from exc
    approvals = [
        r for r in records
        if r.get("event_type") == OPERATOR_APPROVAL_EVENT
        and r.get("decision") == "approve"
        and (r.get("run_id") or "") == run_id]
    if not approvals:
        raise LoopError(
            "approved_digest_audit_missing",
            "no sealed operator-approval event records an approval for this run; the "
            "journal claims an approval that the hash-chained audit evidence does not "
            "hold. Refusing fail-closed - a missing durable approval is never trusted")
    matching = [r for r in approvals
                if (r.get("input_digest") or "") == approved_digest]
    if not matching:
        raise LoopError(
            "approved_digest_audit_mismatch",
            "the journal approved_digest does not match the operator-named digest sealed "
            "in the operator-approval audit evidence; the mutable journal was altered "
            "after a genuine approval. Refusing fail-closed - the sealed, hash-chained "
            "record, not the journal, is the authoritative record of the approval")
    if len(matching) > 1:
        raise LoopError(
            "approved_digest_audit_ambiguous",
            "multiple sealed operator-approval events name the same approved_digest for "
            "this run; the approval evidence is ambiguous or replayed. Refusing "
            "fail-closed rather than guessing which approval is authoritative")


def approve_pending_prompt(journal: Any, run_id: str, *, pending: Mapping[str, Any],
                           approval_binding: str) -> None:
    """Record a PARKED prompt as APPROVED without dropping what the forward needs.

    M0-T045: the approval and the forward can happen in DIFFERENT processes -
    `resume-pending-prompt` fires the owner_approved_pending_prompt transition,
    and a later, separate `start` completes the forward. The old code called
    `consume_pending_prompt` at approval time, which dropped the held prompt
    bytes and the digest, so the resuming process had nothing to forward and the
    loop refused. This keeps the exact held prompt text plus an `approved_digest`
    binding so the resuming loop can verify integrity and forward once - while
    STILL removing the `digest` key so every re-approval guard (`not
    pending.get("digest")`) stays fail-closed. An OLD-shape parked record with no
    held prompt leaves behind an approved record with no `prompt`/`approved_digest`,
    which the loop refuses to forward (it never fabricates a prompt).

    M0-T046 (D-010-R124), G5 LOW-1: a park-time byte anchor (`prompt_bytes_digest`)
    was frozen when the bytes were authentic and re-verified before any state change.

    M0-T048 (D-010 am.14, R136/R137): closes the G5 C2 residual. The parked record
    now carries the STRUCTURED approved instruction, and this function reconstructs
    the forwarded body from it and REFUSES fail-closed unless that instruction
    reproduces the OPERATOR-NAMED approval digest (`approval_binding`). `approved_digest`
    is bound to that operator-named digest - not a journal-resident byte anchor - so an
    attacker who rewrites BOTH the parked `prompt` and `prompt_bytes_digest`
    consistently, leaving the operator digest unchanged, still cannot get altered
    content forwarded: the body is derived from operator-covered material, and any
    edit to a covered field breaks the digest match. Old-shape records (no structured
    instruction) refuse (AS-6). The CLI performs the same check BEFORE it
    transitions/audits, so in the normal path this is defense in depth.
    """
    prompt = pending.get("prompt")
    record: dict[str, Any] = {
        "approved": True,
        "cycle": pending.get("cycle"),
        "decision": pending.get("decision"),
        "reviewed_checkpoint_id": pending.get("reviewed_checkpoint_id"),
        "approved_at_utc": to_utc_iso(),
        "prior_digest": approval_binding,
    }
    if isinstance(prompt, str) and prompt:
        # Reconstruct + verify against the OPERATOR-NAMED digest; raises fail-closed.
        expected_body = verify_covered_instruction(
            pending.get("approved_instruction"), approval_binding, prompt,
            pending.get("prompt_bytes_digest"))
        record["approved_instruction"] = dict(pending["approved_instruction"])
        # Persist the canonical reconstruction (== the verified parked bytes), never a
        # possibly-tampered journal value.
        record["prompt"] = expected_body
        # Bind to the OPERATOR-NAMED approval digest itself (R136), now that the body
        # is a verified pure function of the material that digest covers.
        record["approved_digest"] = approval_binding
    journal.set_state(pending_prompt_key(run_id), record)


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
        pinned_model: str = "",
        context_rotation_threshold: int = 0,
        model_available: Callable[[str], bool] | None = None,
        model_chain: "ModelChain | Sequence[str] | None" = None,
        head_sha: str = "",
        origin_main_sha: str = "",
        executable_identity: Mapping[str, Any] | None = None,
        resource_sampler: Any = None,
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
        # V1.2 (D-004): the model the worker is pinned to, the context-usage
        # rotation threshold (0 disables it), and a strict availability probe used
        # ONLY at a rotation seam. `model_available` defaulting to always-True is
        # the production stance; a live availability check is an operator concern.
        self.pinned_model = pinned_model
        self.context_rotation_threshold = context_rotation_threshold
        self._model_available_probe = model_available or (lambda _model: True)
        # D-004-R751/R758: the FIXED, owner-configured preference chain. Passed in
        # from the immutable controller config; the default is the same order,
        # fail closed. The loop never invents an entry and never reorders one.
        if model_chain is None:
            self.model_chain = ModelChain()
        elif isinstance(model_chain, ModelChain):
            self.model_chain = model_chain
        else:
            self.model_chain = ModelChain(entries=tuple(model_chain))
        self._head_sha = head_sha
        self._origin_main_sha = origin_main_sha
        self._executable_identity = dict(executable_identity or {})
        self._current_session_id = ""
        # D-004 am.26 / D-007 am.11 / am.12: the model the CURRENT session runs
        # on. It is the pinned model unless an orchestrator-role switch is active,
        # in which case it is the chain entry that switch selected. The durable
        # record survives a process restart, so the model is re-derived from it
        # here rather than silently reverting to an exhausted pin on resume - and
        # the RUNNER is rebound to it below, so the resumed run launches on the
        # model it says it is on (D-007-R605).
        self._current_model = effective_model(journal, run_id, pinned_model)
        if self._current_model != pinned_model:
            self._actuate_model(self._current_model)
        self._rotations: list[dict[str, Any]] = []
        self.touches = OwnerTouchLedger(journal, run_id=run_id,
                                        budget=config.owner_touch_budget)
        self.notify_ledger = NotifyOnceLedger(journal)
        self.provider_calls = 0
        self._forwarded: list[str] = []
        # AS-3 (activation-checklist: "live resource sampling wired into the loop
        # for the R207 limit set"). Default None keeps every existing caller and
        # test unchanged: sampling is a no-op unless a sampler is injected (the
        # CLI wires a real one). When present it feeds the gauge breakers with
        # fail-closed defaults; an outage degrades to the conservative pause.
        self._resource_sampler = resource_sampler

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

    def _check_resources(self, cycle: int, notify: list[str]) -> tuple[bool, str]:
        """Sample live resources and evaluate the R207 gauge breakers (AS-3).

        Returns (tripped, message). Fail-closed by construction:

        * a MEASURED reading is fed to `breakers.gauge`; a TRIP is a synchronous
          pause, a WARN is a notify;
        * a sampling OUTAGE of a normally-measurable gauge (known=False,
          structural=False) degrades to the conservative path -> TRIP (a resource
          guard that cannot read the resource never assumes it is fine);
        * a STRUCTURALLY unmeasurable gauge (known=False, structural=True) is
          never fed a fabricated OK value and never causes a per-cycle pause -- it
          is disclosed by `doctor` via the sampler's capability report instead
          (AD-025: unknown is not success, but a permanent capability gap is not a
          spurious trip either).
        """
        if self._resource_sampler is None or self.breakers is None:
            return False, ""
        for sample in self._resource_sampler.sample():
            if sample.gauge not in GAUGE_LIMITS:
                continue
            if sample.known:
                verdict = self.breakers.gauge(sample.gauge, sample.value)
                if verdict.tripped:
                    return True, verdict.message
                if verdict.warning:
                    notify.append("circuit_breaker_warning")
            elif not sample.structural:
                return True, (f"{sample.gauge} could not be sampled "
                              f"({sample.reason}); a resource guard that cannot "
                              f"read the resource pauses rather than assuming it "
                              f"is within limits (fail closed)")
            # structural-unknown: neither trip nor a fabricated OK; disclosed by
            # doctor's resource_sampling capability check.
        return False, ""

    # -- broker wiring (G3 V-1) ---------------------------------------------

    def _permission_handler(self) -> Any:
        """The `can_use_tool` handler for the bounded unit's control channel.

        SUPERVISED: route every in-scope tool request through the four-tier
        policy + approval broker, so an AUTO/approved tool is PERMITTED and
        executes (allow control-response), an ASK holds for the owner, and a
        HARD-DENY is immovable. SHADOW (or a missing broker): return None, so the
        runner falls back to `deny_everything` - shadow permits nothing and never
        forwards, observing only (S8.4 / S12).
        """
        if not self.config.forwards or self.broker is None:
            return None
        return broker_permission_handler(
            self.broker,
            authority=self.authority,
            head_sha=self._head_sha,
            origin_main_sha=self._origin_main_sha,
            session_id_getter=lambda: self._current_session_id,
            executable_identity_data=self._executable_identity)

    # -- seam-only rotation (D-004-R739, R743..R745) ------------------------

    def rotation_pending(self) -> bool:
        """True when a rotation was flagged and not yet consumed (durable)."""
        return rotation.rotation_pending(self.journal)

    def _probe_model(self, model: str) -> "ModelAvailability":
        """Normalize the injected availability probe into a ModelAvailability.

        The probe seam accepts three shapes for backward compatibility with the
        original bool probe (D-004 am.26 / D-007 am.11):

        * a bare ``bool`` -> available with NO reason (a bare False is therefore
          never quota exhaustion: fail closed);
        * a ``(available, reason_code)`` tuple;
        * a :class:`ModelAvailability`.

        A probe that raises fails closed to unavailable with a ``probe_error``
        reason, which is likewise NOT quota exhaustion.
        """
        try:
            raw = self._model_available_probe(model)
        except Exception:
            # A failing probe fails closed, and `probe_error` is NOT quota
            # exhaustion, so it pauses rather than switching models.
            return ModelAvailability(available=False, reason_code="probe_error")
        if isinstance(raw, ModelAvailability):
            return raw
        if (isinstance(raw, tuple) and len(raw) == 2
                and not isinstance(raw, ModelAvailability)):
            return ModelAvailability(available=bool(raw[0]), reason_code=str(raw[1] or ""))
        return ModelAvailability(available=bool(raw), reason_code="")

    def _model_available(self, model: str) -> bool:
        """Strict, no-substitute availability probe for the pinned model (bool view)."""
        return self._probe_model(model).available

    # -- actuation: the switch must reach the LAUNCH (D-007-R605) -----------

    def _actuate_model(self, model: str) -> None:
        """Rebind the RUNNER so the next unit actually launches on `model`.

        This is the fix for the record-only defect: writing a `model_substitution`
        record while the runner kept its original `--model` made the audit trail
        assert a model selection that was never made. Actuation happens BEFORE any
        record is written, and a runner that cannot be rebound is a refusal, not a
        record - the loop never claims a launch it could not perform.
        """
        if model not in self.model_chain and model != self.pinned_model:
            # Belt and braces for D-004-R754: the only ids that can reach the
            # launch config are the pin and the chain entries.
            raise LoopError(
                "model_not_in_chain",
                f"{model!r} is not in the configured model chain "
                f"{list(self.model_chain.entries)} and is not the pinned model; an id "
                f"outside the chain is never selectable no matter what a picker shows")
        rebind = getattr(self.runner, "with_model", None)
        if not callable(rebind):
            raise LoopError(
                "model_actuation_unavailable",
                f"the runner cannot be rebound to {model!r}, so the switch would be a "
                f"record without a launch; refusing rather than recording a model "
                f"selection that never reached the process")
        self.runner = rebind(model)

    def launched_model(self) -> str:
        """The model the runner will ACTUALLY launch with, read off its config.

        Evidence, not bookkeeping: it reads the launch config the argv is built
        from, so a test (or `doctor`) can compare what the records claim with what
        the next process will really be started on.
        """
        config = getattr(self.runner, "config", None)
        return str(getattr(config, "model", "") or "")

    # -- orchestrator-role model substitution (D-004 am.26 / D-007 am.11) ---

    def _substitution_key(self) -> str:
        return f"model_substitution/{self.run_id}"

    def _active_substitution(self) -> dict[str, Any] | None:
        """The durable substitution record when one is active, else None."""
        data = self.journal.get_state(self._substitution_key(), None)
        if isinstance(data, dict) and data.get("active"):
            return data
        return None

    def _flag_rotation_if_needed(self, run_result: Any, *, cycle: int) -> None:
        """Set rotation_pending if THIS unit downgraded or crossed the threshold.

        Flag-only. It never interrupts the unit (which has already returned) and
        never rotates here: `observe_mid_unit` persists the flag and the actual
        rotation happens at the next seam. Restricted to forwarding (supervised)
        mode so a shadow observation stays purely observational.
        """
        if not self.config.forwards:
            return
        reason_code = ""
        detail = ""
        if getattr(run_result, "model_mismatch", False):
            reason_code = "model_downgrade"
            detail = str(getattr(run_result, "mismatch_detail", "") or "")
        elif (self.context_rotation_threshold > 0
              and getattr(run_result, "usage_known", False)
              and int(getattr(run_result, "context_tokens", 0) or 0)
              >= self.context_rotation_threshold):
            reason_code = "context_threshold"
            detail = (f"cumulative context usage "
                      f"{int(getattr(run_result, 'context_tokens', 0) or 0)} crossed the "
                      f"configured threshold {self.context_rotation_threshold}")
        if not reason_code:
            return
        if self.rotation_pending():
            return
        # observe_mid_unit persists rotation_pending durably and, by construction,
        # cannot terminate the unit - neither reason is an S11.2 interrupt reason.
        rotation.observe_mid_unit(self.journal, reason_code=reason_code, detail=detail)
        self.journal.set_state(rotation.ROTATION_REASON_KEY, reason_code)
        if self.audit is not None:
            self.audit.append(
                "rotation_pending_flagged", run_id=self.run_id,
                policy_result=reason_code,
                detail={"cycle": cycle, "reason_code": reason_code, "detail": detail,
                        "note": "the in-flight unit is NOT interrupted (S11.2); rotation "
                                "happens before the next dispatch"})

    def _refresh_session_handoff(self, *, cycle: int, reason_code: str) -> str:
        """Refresh the durable SESSION_HANDOFF snapshot before rotating.

        A bounded continuity record the rotated-to session binds to: the task,
        stage, branch, worktree, the reason, and the outgoing session id, with a
        digest. It is NOT the full S11.3 Codex-verified handoff (that needs a live
        worker + reviewer and is out of fake-harness scope); it is the refresh
        step named by D-004, recorded durably and in the audit chain.
        """
        snapshot = {
            "task_id": self.config.task_id,
            "stage": self.config.stage,
            "branch": self.authority.branch,
            "worktree": self.authority.worktree,
            "reason_code": reason_code,
            "outgoing_session_id": self._current_session_id,
            "pinned_model": self.pinned_model,
            "cycle": cycle,
            "refreshed_at_utc": to_utc_iso(),
        }
        digest = digest_of(snapshot)
        self.journal.set_state(f"session_handoff/{self.run_id}",
                               {**snapshot, "digest": digest})
        if self.audit is not None:
            self.audit.append("session_handoff_refreshed", run_id=self.run_id,
                              output_digest=digest, policy_result=reason_code,
                              detail={"cycle": cycle, "reason_code": reason_code})
        return digest

    def _rotate_at_seam(self, *, cycle: int) -> "SeamRotation":
        """Rotate the session BEFORE dispatching the next unit (B and C share this).

        The single rotation code path for both a detected model downgrade (B) and
        a context-threshold crossing (C). Structurally seam-only: only run() calls
        it, always between cycles, and it asserts nothing is in flight by requiring
        the durable rotation_pending flag. Order: refresh handoff -> strict pinned-
        model check -> rotate via rotation.py (archive old, mint new, complete) or
        PAUSE+notify when the pinned model is unavailable.
        """
        pending = self.rotation_pending()
        substitution = self._active_substitution()
        if not pending and substitution is None:  # pragma: no cover - guarded by caller
            raise LoopError("rotate_without_pending",
                            "a seam rotation was attempted with no rotation_pending flag "
                            "and no active substitution; rotation is only reachable at a "
                            "safe seam")

        # RETURN-TO-PINNED (D-004 am.26 / D-007 am.11): while a substitution is
        # active, probe the pinned model at THIS seam (and only at a seam). The
        # moment it is available again, rotate back onto the pinned model and
        # record a first-class return event - never silently. This runs before any
        # new-rotation handling so the session returns at the earliest safe seam.
        if substitution is not None:
            if self._probe_model(self.pinned_model).available:
                return self._return_to_pinned(cycle=cycle, substitution=substitution)
            if not pending:
                # Pinned still unavailable and nothing new to rotate for: the
                # switched session simply continues on its current chain entry.
                return SeamRotation(
                    relaunched=False, paused=False, stopped="", substituted=True,
                    reason=(f"substitution active: pinned model {self.pinned_model!r} is "
                            f"still unavailable, continuing on {self._current_model!r}"),
                    reason_code="model_substitution_active")

        reason_code = str(self.journal.get_state(rotation.ROTATION_REASON_KEY, "")
                          or "context_threshold")
        handoff_digest = self._refresh_session_handoff(cycle=cycle,
                                                       reason_code=reason_code)

        # Availability gate on the model this seam would relaunch on: the pin
        # normally, or the current chain entry while a switch is active. The pin is
        # strict by default: an unavailable model PAUSES for the owner and never
        # silently substitutes. The ONE exception (D-004 am.26 / D-007 am.11/12) is
        # an ORCHESTRATOR-ROLE session whose model is unavailable SPECIFICALLY
        # because its quota is exhausted - it walks the configured chain and
        # relaunches on the first entry that ACTUALLY launches. Every OTHER
        # unavailability reason (unknown, error, a bare False with no reason), and
        # every non-orchestrator loop, keeps the PAUSE+notify below byte-for-byte:
        # fail closed.
        gated_model = self._current_model if substitution is not None else self.pinned_model
        if gated_model:
            availability = self._probe_model(gated_model)
            if not availability.available:
                if (self.config.session_role == SESSION_ROLE_ORCHESTRATOR
                        and availability.reason_code == QUOTA_EXHAUSTED_REASON):
                    return self._switch_at_seam(
                        cycle=cycle, reason_code=reason_code,
                        handoff_digest=handoff_digest, exhausted_model=gated_model,
                        substitution=substitution)
                return self._pause_model_unavailable(
                    cycle=cycle, reason_code=reason_code, model=gated_model,
                    handoff_digest=handoff_digest)

        # Rotate via rotation.py: archive the outgoing session, clear the pending
        # flag, mint a brand-new session id, record the NOTIFY event. The relaunch
        # continues on the CURRENT model - the pin normally, or the substitute
        # while a substitution is active and the pin is still unavailable.
        old_session = self._current_session_id
        new_session = rotation.new_session_id(old_session)
        ledger = rotation.RotationLedger(self.journal, audit=self.audit)
        record = ledger.complete_rotation(
            old_session_id=old_session, new_session_id_value=new_session,
            handoff_digest=handoff_digest)
        self._current_session_id = new_session
        self.journal.set_state(rotation.ROTATION_REASON_KEY, "")
        relaunch = {
            "cycle": cycle, "reason_code": reason_code,
            "old_session_id": old_session, "new_session_id": new_session,
            "handoff_digest": handoff_digest, "pinned_model": self.pinned_model,
            "model": self._current_model,
            "tier": NOTIFY, "recorded_at_utc": to_utc_iso(),
        }
        self._rotations.append(relaunch)
        if self.audit is not None:
            self.audit.append(
                "supervisor_rotation_relaunch", run_id=self.run_id,
                policy_result=reason_code, output_digest=handoff_digest,
                detail={**relaunch,
                        "note": "relaunch continues on the CURRENT model in a brand-new "
                                "session; a completed rotation is a NOTIFY event (S11.3)"})
        model_label = self._current_model or self.pinned_model or "the configured model"
        return SeamRotation(relaunched=True, paused=False, stopped="",
                            substituted=substitution is not None,
                            reason=(f"rotated {reason_code}: archived {old_session!r}, "
                                    f"relaunching on {model_label} in {new_session!r}"),
                            reason_code=reason_code, record=relaunch)

    def _pause_model_unavailable(self, *, cycle: int, reason_code: str, model: str,
                                 handoff_digest: str) -> "SeamRotation":
        """PAUSE + notify: the model this seam would relaunch on is unavailable.

        The strict default, unchanged: a rotation never silently substitutes
        another model. Reached for every unavailability reason that is NOT a
        quota exhaustion on an orchestrator-role session, and for every
        non-orchestrator loop whatever the reason.
        """
        self.machine.transition(
            PAUSED_RECOVERY, "unsafe_condition",
            detail={"cycle": cycle, "reason": "pinned_model_unavailable",
                    "pinned_model": self.pinned_model,
                    "unavailable_model": model,
                    "rotation_reason": reason_code})
        touch = self._touch(
            TOUCH_SYNCHRONOUS_STOP, reason_code="pinned_model_unavailable",
            reason=(f"the configured model {model!r} is unavailable; a "
                    f"rotation may not silently substitute another model (D-004)"),
            cycle=cycle, basis="D-004 model pinning / S3.2")
        ask_id = f"rotation_pause/{self.run_id}/{cycle}"
        try:
            self.journal.queue_ask(QueuedAsk(
                ask_id=ask_id, run_id=self.run_id, task_id=self.config.task_id,
                question=(f"The configured model {model!r} is "
                          f"unavailable after a {reason_code} rotation. An "
                          f"orchestrator-role session will not continue on a "
                          f"substitute; how should it proceed?"),
                request_digest=handoff_digest, created_at_utc=to_utc_iso(),
                classification="security"))
        except Exception:
            # A duplicate ask id means the same pause is already queued.
            pass
        if self.audit is not None:
            self.audit.append(
                "rotation_paused_model_unavailable", run_id=self.run_id,
                decision="deny", policy_result="pinned_model_unavailable",
                detail={"cycle": cycle, "pinned_model": self.pinned_model,
                        "unavailable_model": model,
                        "reason_code": reason_code, "ask_id": ask_id,
                        "handoff_digest": handoff_digest})
        return SeamRotation(
            relaunched=False, paused=True,
            stopped="rotation_paused_model_unavailable",
            reason=(f"the configured model {model!r} is unavailable; "
                    f"the session is paused for the owner rather than continuing "
                    f"on a substitute"),
            reason_code=reason_code, touch=touch)

    def _switch_at_seam(self, *, cycle: int, reason_code: str, handoff_digest: str,
                        exhausted_model: str,
                        substitution: Mapping[str, Any] | None = None) -> "SeamRotation":
        """Walk the configured chain and relaunch on the first entry that LAUNCHES.

        The single authorized exception to strict pinning (D-004 am.26 / D-007
        am.11, corrected by D-007 am.12): the current model is unavailable
        specifically because its quota is exhausted, and this is an
        orchestrator-role session. There is no judgement here and no owner tap
        (D-004-R760): the seam walks the FIXED config chain in order from the
        entry after the exhausted one, probes each by ACTUAL LAUNCH (D-004-R752),
        and takes the first that brings up a real process on that exact id.

        The selected id is ACTUATED on the runner BEFORE anything is recorded
        (D-007-R605), so the `model_substitution` event and the durable record
        describe a launch configuration that really changed - never a record
        without a relaunch. If NO entry launches, nothing is recorded as a switch:
        the run STOPS and notifies the owner (D-004-R755).
        """
        attempts: list[dict[str, Any]] = []
        selected = ""
        for candidate in self.model_chain.candidates_after(exhausted_model):
            availability = self._probe_model(candidate)
            attempts.append({"model": candidate, "available": availability.available,
                             "reason_code": availability.reason_code})
            if availability.available:
                selected = candidate
                break
        if not selected:
            return self._stop_chain_exhausted(
                cycle=cycle, reason_code=reason_code, exhausted_model=exhausted_model,
                attempts=attempts)

        # ACTUATION FIRST: the next unit must really launch on `selected`.
        self._actuate_model(selected)
        old_session = self._current_session_id
        new_session = rotation.new_session_id(old_session)
        ledger = rotation.RotationLedger(self.journal, audit=self.audit)
        ledger.complete_rotation(
            old_session_id=old_session, new_session_id_value=new_session,
            handoff_digest=handoff_digest)
        self._current_session_id = new_session
        self._current_model = selected
        self.journal.set_state(rotation.ROTATION_REASON_KEY, "")
        record = {
            "active": True,
            "pinned_model": self.pinned_model,
            "exhausted_model": exhausted_model,
            "substitute_model": selected,
            "effective_model": selected,
            "launched_model": self.launched_model(),
            "chain": list(self.model_chain.entries),
            "chain_attempts": attempts,
            "reason_code": QUOTA_EXHAUSTED_REASON,
            "rotation_reason": reason_code,
            "cycle": cycle,
            "old_session_id": old_session,
            "new_session_id": new_session,
            "handoff_digest": handoff_digest,
            "started_at_utc": to_utc_iso(),
        }
        if substitution is not None:
            record["previous_switch_started_at_utc"] = str(
                substitution.get("started_at_utc", "") or "")
        self.journal.set_state(self._substitution_key(), record)
        relaunch = {
            "cycle": cycle, "reason_code": reason_code,
            "old_session_id": old_session, "new_session_id": new_session,
            "handoff_digest": handoff_digest, "pinned_model": self.pinned_model,
            "model": selected, "substitute_model": selected,
            "launched_model": self.launched_model(),
            "chain": list(self.model_chain.entries), "chain_attempts": attempts,
            "exhausted_model": exhausted_model,
            "substitution": True, "availability_reason": QUOTA_EXHAUSTED_REASON,
            "tier": NOTIFY, "recorded_at_utc": to_utc_iso(),
        }
        self._rotations.append(relaunch)
        if self.audit is not None:
            self.audit.append(
                "model_substitution", run_id=self.run_id,
                policy_result=QUOTA_EXHAUSTED_REASON, output_digest=handoff_digest,
                detail={**record,
                        "note": "orchestrator-role continuity: this model's quota is "
                                "exhausted at this seam, so the session relaunches EXPLICITLY "
                                "on the next chain entry that ACTUALLY launched, in a "
                                "brand-new session, with the runner rebound to that exact id "
                                "before this record was written. Never silent; never a "
                                "reviewer substitute; never an id outside the chain; the "
                                "pinned model is probed at every subsequent seam and restored "
                                "the moment it is available (D-004 am.26 / D-007 am.11, "
                                "corrected by am.12)"})
        return SeamRotation(
            relaunched=True, paused=False, stopped="", substituted=True,
            reason=(f"model {exhausted_model!r} quota exhausted; the orchestrator-role "
                    f"session relaunched on chain entry {selected!r} in {new_session!r}"),
            reason_code=reason_code, record=relaunch)

    def _stop_chain_exhausted(self, *, cycle: int, reason_code: str,
                              exhausted_model: str,
                              attempts: Sequence[Mapping[str, Any]]) -> "SeamRotation":
        """No chain entry launched: STOP, refresh the handoff, notify (D-004-R755).

        The end of the chain is a full stop, never a fallback. Nothing outside the
        chain is tried, no substitute is chosen, and the run does not continue: the
        handoff is refreshed under this reason code, the owner is notified through
        the existing pause/ask surface, and the seam reports the stop.
        """
        handoff_digest = self._refresh_session_handoff(cycle=cycle,
                                                       reason_code=CHAIN_EXHAUSTED_STOP)
        self.machine.transition(
            PAUSED_RECOVERY, "unsafe_condition",
            detail={"cycle": cycle, "reason": CHAIN_EXHAUSTED_STOP,
                    "pinned_model": self.pinned_model,
                    "exhausted_model": exhausted_model,
                    "chain": list(self.model_chain.entries),
                    "rotation_reason": reason_code})
        touch = self._touch(
            TOUCH_SYNCHRONOUS_STOP, reason_code=CHAIN_EXHAUSTED_STOP,
            reason=(f"no entry in the configured model chain "
                    f"{list(self.model_chain.entries)} actually launched after "
                    f"{exhausted_model!r} was exhausted; the session stops rather than "
                    f"continuing on an unlisted or substitute model (D-004-R755)"),
            cycle=cycle, basis="D-004 model chain / D-007 am.12")
        ask_id = f"model_chain_exhausted/{self.run_id}/{cycle}"
        try:
            self.journal.queue_ask(QueuedAsk(
                ask_id=ask_id, run_id=self.run_id, task_id=self.config.task_id,
                question=(f"No model in the configured chain "
                          f"{list(self.model_chain.entries)} could be launched after "
                          f"{exhausted_model!r} was exhausted. The session has stopped and "
                          f"will not continue on any other model; how should it proceed?"),
                request_digest=handoff_digest, created_at_utc=to_utc_iso(),
                classification="security"))
        except Exception:
            # A duplicate ask id means the same stop is already queued.
            pass
        if self.audit is not None:
            self.audit.append(
                CHAIN_EXHAUSTED_STOP, run_id=self.run_id,
                decision="deny", policy_result=CHAIN_EXHAUSTED_STOP,
                output_digest=handoff_digest,
                detail={"cycle": cycle, "pinned_model": self.pinned_model,
                        "exhausted_model": exhausted_model,
                        "chain": list(self.model_chain.entries),
                        "chain_attempts": [dict(a) for a in attempts],
                        "launched_model": self.launched_model(),
                        "reason_code": reason_code, "ask_id": ask_id,
                        "handoff_digest": handoff_digest,
                        "note": "every chain entry was tried by an actual launch attempt and "
                                "none came up; the supervisor NEVER continues on an unlisted "
                                "or substitute model (D-004-R754/R755)"})
        return SeamRotation(
            relaunched=False, paused=True, stopped=CHAIN_EXHAUSTED_STOP,
            reason=(f"no entry in the configured model chain launched after "
                    f"{exhausted_model!r} was exhausted; the session stopped and the owner "
                    f"was notified"),
            reason_code=CHAIN_EXHAUSTED_STOP, touch=touch)

    def _return_to_pinned(self, *, cycle: int,
                          substitution: Mapping[str, Any]) -> "SeamRotation":
        """Rotate a substituted session back onto the pinned model (D-004 am.26).

        The pinned model is available again at this seam, so the orchestrator-role
        session returns to it in a brand-new session and records a FIRST-CLASS
        `model_substitution_ended` event. Never silent. Called only from
        `_rotate_at_seam`, i.e. only at a seam. The return is ACTUATED on the
        runner before it is recorded, exactly like the outbound switch: the
        mirrored half of D-007-R605.
        """
        left_behind = self._current_model or str(
            substitution.get("substitute_model", "") or "")
        handoff_digest = self._refresh_session_handoff(
            cycle=cycle, reason_code="model_substitution_ended")
        old_session = self._current_session_id
        new_session = rotation.new_session_id(old_session)
        self._actuate_model(self.pinned_model)
        ledger = rotation.RotationLedger(self.journal, audit=self.audit)
        ledger.complete_rotation(
            old_session_id=old_session, new_session_id_value=new_session,
            handoff_digest=handoff_digest)
        self._current_session_id = new_session
        self._current_model = self.pinned_model
        self.journal.set_state(rotation.ROTATION_REASON_KEY, "")
        ended = {**dict(substitution), "active": False,
                 "ended_cycle": cycle, "ended_at_utc": to_utc_iso(),
                 "return_new_session_id": new_session}
        self.journal.set_state(self._substitution_key(), ended)
        relaunch = {
            "cycle": cycle, "reason_code": "model_substitution_ended",
            "old_session_id": old_session, "new_session_id": new_session,
            "handoff_digest": handoff_digest, "pinned_model": self.pinned_model,
            "model": self.pinned_model, "restored_from_substitute": left_behind,
            "launched_model": self.launched_model(),
            "tier": NOTIFY, "recorded_at_utc": to_utc_iso(),
        }
        self._rotations.append(relaunch)
        if self.audit is not None:
            self.audit.append(
                "model_substitution_ended", run_id=self.run_id,
                policy_result="pinned_model_available", output_digest=handoff_digest,
                detail={**relaunch, "substitute_model": left_behind,
                        "note": "the pinned model is available again at this seam; the "
                                "orchestrator-role session returns to it in a brand-new "
                                "session, with the runner rebound to the pin before this "
                                "record was written. Never silent (D-004 am.26 / D-007 "
                                "am.11)"})
        return SeamRotation(
            relaunched=True, paused=False, stopped="", substituted=False,
            reason=(f"pinned model {self.pinned_model!r} available again; returned from "
                    f"substitute {left_behind!r} in {new_session!r}"),
            reason_code="model_substitution_ended", record=relaunch)

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

        # AS-3: sample live resources BEFORE spending a provider call. A trip (a
        # measured limit crossing, or a sampling outage of a measurable gauge)
        # ends the cycle at its current LEGAL entry state (no transition, no
        # stranding, no provider call), reported honestly.
        tripped, message = self._check_resources(cycle, notify)
        if tripped:
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="resource_gauge_hard_threshold",
                reason=message, cycle=cycle,
                basis="S13.8 gauge breaker fed by R207 live resource sampling"))
            return stop("resource_gauge_hard_threshold", message, entry)

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
        # G3 V-1: the approval broker is now WIRED. In supervised mode each
        # in-scope tool request the worker makes routes through the four-tier
        # policy + broker; an AUTO/approved tool is PERMITTED and executes. In
        # shadow mode the handler permits nothing (deny/observe only) - shadow
        # semantics unchanged.
        self.provider_calls += 1
        run_result = self.runner.run_unit(
            prompt, permission_handler=self._permission_handler())
        session_id = str(getattr(run_result, "session_id", "") or "")
        if session_id:
            self._current_session_id = session_id
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
            # V1.1 correction V-4: say precisely WHY the unit is not OK. A unit
            # that produced a valid checkpoint but had to be tree-terminated (or
            # hit the wall) is a different fact from "exited without a valid
            # checkpoint", and the recorded reason must not conflate them.
            reason = str(getattr(run_result, "checkpoint_error", "") or "")
            if not reason:
                if checkpoint is not None and getattr(run_result, "graceful_close_failed",
                                                      False):
                    reason = ("the unit completed its turns and produced a valid "
                              "checkpoint, but the worker did not exit within the close "
                              "grace and was tree-terminated (graceful_close_failed); a "
                              "killed worker is never success (S14)")
                elif checkpoint is not None and getattr(run_result, "timed_out", False):
                    reason = ("the unit produced a valid checkpoint but hit the wall "
                              "timeout and was tree-terminated; a timed-out unit is "
                              "never success (S14)")
                else:
                    reason = "the worker exited without a valid checkpoint"
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
        if self.breakers is not None:
            # V1.1 correction B-4: the per-checkpoint review counter measures
            # reviews of THIS checkpoint, so it resets when a new checkpoint is
            # received - without this it silently measured reviews-per-run.
            self.breakers.reset("codex_reviews_per_checkpoint")

        # --- V1.2 (D-004-R739 / R743): seam-only rotation triggers ------------
        # A detected model downgrade or a context-threshold crossing during THIS
        # unit sets rotation_pending. Per S11.2 the in-flight unit is NEVER
        # interrupted for pressure: it already returned above, and the actual
        # rotation decision runs at the next seam in run() - unreachable while a
        # unit is in flight. Surfaced on the CycleResult for the seam to read.
        result.model_mismatch = bool(getattr(run_result, "model_mismatch", False))
        result.context_tokens = int(getattr(run_result, "context_tokens", 0) or 0)
        self._flag_rotation_if_needed(run_result, cycle=cycle)
        result.rotation_pending = self.rotation_pending()

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
        # V1.1 correction B-4: the breaker verdict is HONORED, not discarded. A
        # tripped S13.8 review breaker pauses synchronously before the reviewer
        # is contacted, exactly like the claude_runs breaker above.
        tripped, message = self._breaker("codex_reviews_per_checkpoint")
        if tripped:
            self.machine.transition(
                PAUSED_RECOVERY, "unsafe_condition",
                detail={"cycle": cycle, "breaker": "codex_reviews_per_checkpoint"})
            touches.append(self._touch(TOUCH_SYNCHRONOUS_STOP,
                                       reason_code="circuit_breaker_hard_threshold",
                                       reason=message, cycle=cycle,
                                       basis="S13.8 hard threshold"))
            return stop("circuit_breaker_hard_threshold", message, PAUSED_RECOVERY)
        if message:
            notify.append("circuit_breaker_warning")
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
            # DENY_AND_CONTINUE: the proposed forward is refused; the machine is
            # NOT paused or halted. V1.1 correction B-2: the cycle CLOSES into a
            # resumable state and the run reports the refusal honestly - the old
            # behaviour left the journal at POLICY_CHECK with no legal exit, and
            # in supervised multi-cycle mode the next iteration crashed with
            # bad_cycle_entry_state. A refused forward means there is nothing to
            # send to the worker, so the run does not auto-retry the same
            # instruction; the operator decides whether to start again.
            self.machine.transition(PREFLIGHT, "cycle_closed",
                                    detail={"cycle": cycle,
                                            "reason_code": verdict.reason_code,
                                            "closed_after": "deny_and_continue"})
            result.notes += ("deny_and_continue",)
            return stop("deny_and_continue", verdict.reason, PREFLIGHT)

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

        # M0-T048 (D-010 am.14): the structured approved instruction is the single
        # source for BOTH the operator-named approval digest and the reconstructable
        # forwarded body, so they cannot drift. `build_forwarded_prompt` emits a
        # deterministic, timestamp-free body (the `FORWARDED AT:` clock is appended
        # only at forward time); the volatile packet reference is no longer embedded.
        instruction = {
            "task_id": self.config.task_id,
            "stage": self.config.stage,
            "allowed_paths": list(
                self.config.allowed_paths or self.authority.allowed_paths),
            "requested_action": decision.next_claude_prompt,
            "stop_conditions": list(self.config.stop_conditions),
        }
        forwarded_prompt = build_forwarded_prompt(**instruction)
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
            # V1.1 correction B-2: a completed shadow observation CLOSES the
            # cycle rather than stranding the journal at POLICY_CHECK (which had
            # no legal exit, so the next `start` against the same journal
            # crashed and the only remedy was parking it). The journal now rests
            # at PREFLIGHT, a legal cycle-entry state.
            self.machine.transition(PREFLIGHT, "cycle_closed",
                                    detail={"cycle": cycle,
                                            "closed_after": "shadow_observation"})
            land(PREFLIGHT)
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
        # M0-T045: park the EXACT held prompt bytes alongside the approval
        # digest. Prompt text is digest-only everywhere else, but a cross-process
        # resume (approve in one invocation, forward in a fresh `start`) has
        # nothing to forward unless the bytes are durable here. `digest` stays the
        # approval binding; `prompt` is the deterministic timestamp-free body.
        self.journal.set_state(pending_prompt_key(self.run_id),
                               {"cycle": cycle, "digest": prompt_digest,
                                # M0-T048 (D-010 am.14, R136): the STRUCTURED approved
                                # instruction. approve/resume reconstruct the forwarded
                                # body from this and verify it reproduces the
                                # operator-named `digest`, so the forwarded content is
                                # bound to operator-covered material - never trusted
                                # from the mutable `prompt`/`prompt_bytes_digest` fields.
                                "approved_instruction": instruction,
                                "prompt": forwarded_prompt,
                                # M0-T046 (D-010-R124): the park-time byte anchor of the
                                # deterministic body, kept as defense in depth. The body
                                # is now reconstructable from covered material, so a
                                # journal-write tamper of `prompt` (and/or this anchor)
                                # is caught fail-closed by the reconstruction check.
                                "prompt_bytes_digest": digest_of(forwarded_prompt),
                                "reviewed_checkpoint_id":
                                    decision.reviewed_checkpoint_id,
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

        # M0-T048 (R137): append the non-authoritative FORWARDED AT clock at the
        # ACTUAL forward, excluded from the binding. The parked body stays timestamp-
        # free; the message id keys on the approval digest, not these bytes, so the
        # stamp never affects exactly-once identity.
        forward = self.forward_exactly_once(stamp_forwarded_at(forwarded_prompt),
                                            cycle=cycle, decision=decision)
        result.forward = forward
        result.forwarded = forward.sent
        if forward.sent:
            self._forwarded.append(forward.message_id)
            self.machine.transition(CLAUDE_RUNNING, "prompt_forwarded",
                                    detail={"cycle": cycle,
                                            "message_id": forward.message_id})
            land(CLAUDE_RUNNING)
            # AS-4 (G5 V1.2.3 LOW): the held prompt has now been approved AND
            # forwarded, so consume its pending_prompt record. Without this a
            # later WAIT for a different ask would still carry this cycle's
            # digest and could be re-approved against a stale record.
            consume_pending_prompt(self.journal, self.run_id,
                                   prior_digest=prompt_digest)
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
        return self._forward_outbox(
            prompt, cycle=cycle, message_id=message_id, payload=payload,
            correlation_id=decision.reviewed_checkpoint_id or self.run_id)

    def _resume_forward(self, prompt: str, *, cycle: int, approval_binding: str,
                        decision_str: str,
                        reviewed_checkpoint_id: str) -> ForwardResult:
        """Forward a CROSS-PROCESS approved prompt with no live decision in hand.

        M0-T045: on a fresh `start` that resumes a run parked-and-approved in an
        earlier invocation, the CodexDecision object is gone - only the durable
        approved record survives. This mirrors `forward_exactly_once` exactly (same
        outbox mechanics, same exactly-once suppression, same message-id keyed on
        the approval binding) so a crash between approval and forward, or a second
        resume, never double-sends. The approval binding IS the id key, so this
        method and the in-loop `forward_message_id` mint the SAME id for the same
        instruction.
        """
        self.assert_forwarding_allowed()
        self._guard()
        message_id = f"{self.run_id}/fwd/{cycle}/{approval_binding[:16]}"
        payload = {
            "prompt": prompt,
            "prompt_digest": digest_of(prompt),
            "approval_digest": approval_binding,
            "decision": decision_str,
            "reviewed_checkpoint_id": reviewed_checkpoint_id,
            "task_id": self.config.task_id,
            "stage": self.config.stage,
        }
        return self._forward_outbox(
            prompt, cycle=cycle, message_id=message_id, payload=payload,
            correlation_id=reviewed_checkpoint_id or self.run_id)

    def _forward_outbox(self, prompt: str, *, cycle: int, message_id: str,
                        payload: dict[str, Any],
                        correlation_id: str) -> ForwardResult:
        """The durable outbox mechanic shared by both forward callers.

        Journal, then send, then mark sent. Extracted verbatim so the in-loop
        forward and the cross-process resume forward cannot drift on the
        exactly-once guarantee (M0-T045).
        """
        envelope = build_envelope(
            payload=payload, payload_type="forwarded_prompt", run_id=self.run_id,
            task_id=self.config.task_id, sequence=max(1, cycle),
            producer="supervisor", producer_version=CONTROLLER_VERSION,
            correlation_id=correlation_id,
            message_id=message_id)

        resumed = False
        sent_prompt = prompt
        try:
            self.journal.enqueue_outbound(message_id, envelope.to_dict())
        except JournalError as exc:
            if exc.code != "duplicate_outbound":
                raise
            unsent_row = next((e for e in self.journal.unsent_outbound()
                               if e.get("message_id") == message_id), None)
            if unsent_row is None:
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
            # V1.1 correction B-1: the resumed row's OWN journaled prompt is
            # what gets marked sent, so that is what the next unit must receive
            # - never a fresh re-render of it.
            previous_payload = unsent_row.get("payload")
            if isinstance(previous_payload, Mapping):
                previous_prompt = previous_payload.get("prompt")
                if isinstance(previous_prompt, str) and previous_prompt:
                    sent_prompt = previous_prompt

        # The "send" is the durable handoff to the worker's next unit. It is
        # marked sent only AFTER the outbox row exists, so a crash between the
        # two leaves an unsent row that is resumed, never re-minted. The
        # CONSUMER of the handoff is `run()`, which passes `sent_prompt` to the
        # next cycle's unit (V1.1 correction B-1).
        self.journal.mark_sent(message_id)
        if self.audit is not None:
            self.audit.append("prompt_forwarded", run_id=self.run_id,
                              output_digest=digest_of(sent_prompt),
                              detail={"message_id": message_id, "cycle": cycle,
                                      "resumed_unsent": resumed})
        return ForwardResult(message_id, sent=True, resumed_unsent=resumed,
                             sent_prompt=sent_prompt)

    # -- cross-process resume (M0-T045) -------------------------------------

    def _seal_cross_process_resume_refusal(
            self, exc: LoopError, *, approved_digest: str, cycle: Any) -> None:
        """Durably seal a fail-closed cross-process-resume refusal (M0-T048 R149/R150).

        The security guarantee is the caller's fail-closed raise (no forward, zero
        provider calls). This records WHY, in the same sealed, hash-chained audit log the
        approval used, so the mismatch/refusal is durable. It is best-effort ONLY when the
        chain itself is already broken (`append` REFUSES to extend a damaged chain): in
        that case the broken chain is itself the recorded evidence, and the caller still
        refuses. The journal is never mutated here."""
        if self.audit is None:
            return
        try:
            self.audit.append(
                "cross_process_resume_refused", run_id=self.run_id,
                input_digest=approved_digest, decision="refuse",
                state_from=FORWARD_PROMPT, state_to=FORWARD_PROMPT,
                detail={"reason": exc.code, "cross_process_resume": True,
                        "cycle": cycle,
                        "note": "the journal approved_digest failed the sealed operator-"
                                "approval audit cross-check; no forward, no provider call"})
        except AuditChainError:
            # The chain is already damaged (that IS the finding); it cannot be extended.
            # The caller's fail-closed raise remains the security guarantee.
            pass

    def _resume_approved_forward(self) -> tuple[str, int]:
        """Complete a forward that was APPROVED in an earlier, separate process.

        M0-T045: a supervised WAIT parked a prompt; the operator ran
        `resume-pending-prompt`, which fired owner_approved_pending_prompt and
        left the journal at FORWARD_PROMPT with an APPROVED record; and THIS fresh
        `start` must forward it. The S7 table already carries the legal exit
        FORWARD_PROMPT -> CLAUDE_RUNNING on prompt_forwarded; the only thing
        missing was a caller that read the approved record, forwarded it exactly
        once, and continued. That is this method.

        It fails closed - a structured `forwarded_prompt_unavailable` refusal, no
        provider call, journal unchanged - on every degenerate entry: a durable
        emergency stop, a journal whose last trigger is not the owner approval, a
        missing/old-shape/consumed record, no held prompt bytes (a pre-fix record
        that never parked the text), or a held prompt whose digest does not match
        what was approved. Returns ``(forwarded_prompt, parked_cycle)`` on success.
        """
        # A durable emergency stop is absolute: never forward around it.
        if bool(self.journal.get_state(EMERGENCY_STOP_KEY, False)):
            raise LoopError(
                "forwarded_prompt_unavailable",
                "refusing to resume the approved forward: a durable emergency stop "
                "is set. Clear it with an explicit `stop --clear` first; a resume "
                "never overrides it")
        # The journal must ACTUALLY record the owner approval that leads here.
        if self.machine.last_trigger != "owner_approved_pending_prompt":
            raise LoopError(
                "forwarded_prompt_unavailable",
                f"the journal rests at {FORWARD_PROMPT} but its last trigger is "
                f"{self.machine.last_trigger!r}, not owner_approved_pending_prompt; "
                f"only an explicitly approved pending prompt is forwarded from here")
        record = self.journal.get_state(pending_prompt_key(self.run_id), None)
        if not isinstance(record, dict) or not record.get("approved"):
            raise LoopError(
                "forwarded_prompt_unavailable",
                "no approved pending-prompt record to forward; a resume forwards "
                "exactly one explicitly approved prompt and refuses when none is "
                "recorded (a consumed or missing record forwards nothing)")
        prompt = record.get("prompt")
        approved_digest = record.get("approved_digest")
        if not isinstance(prompt, str) or not prompt:
            raise LoopError(
                "forwarded_prompt_unavailable",
                "the approved pending-prompt record carries no held prompt bytes "
                "(an old-shape record parked before the held text was durable); "
                "refusing to fabricate a prompt to forward")
        # M0-T048 REWORK (D-010 R145..R150; G3 MAJOR-1): the mutable journal
        # `approved_digest` is NOT the sole record of what the operator approved. BEFORE
        # any forward, cross-check it against the ALREADY-SEALED, hash-chained operator-
        # approval audit evidence (the `operator_resume_pending_prompt` approve event's
        # operator-named `input_digest`). An attacker who rewrites `approved_instruction`
        # + `approved_digest` (+ `prompt`/`prompt_bytes_digest`) self-consistently after a
        # genuine approval passes the reconstruction check below, but cannot match the
        # operator-named digest sealed in the immutable chain. Fail-closed on any
        # mismatch/missing/ambiguous/chain-invalid evidence, with a DISTINCT reason code,
        # a durable sealed refusal, and zero provider calls (the forward is never reached).
        try:
            verify_approved_digest_against_audit(
                self.audit, self.run_id, str(approved_digest or ""))
        except LoopError as exc:
            self._seal_cross_process_resume_refusal(
                exc, approved_digest=str(approved_digest or ""),
                cycle=record.get("cycle"))
            raise LoopError(
                "forwarded_prompt_unavailable",
                f"refusing to forward: {exc.message}") from exc
        # M0-T048 (D-010 am.14, R136): RECONSTRUCT the forwarded body from the
        # operator-covered structured instruction and verify it reproduces the
        # operator-named `approved_digest`, rather than trusting the parked bytes. A
        # missing/old-shape/uncovered or tampered record refuses fail-closed (AS-6) -
        # never a fallback to journal-resident-only byte comparison.
        try:
            body = verify_covered_instruction(
                record.get("approved_instruction"), str(approved_digest or ""),
                prompt, record.get("prompt_bytes_digest"))
        except LoopError as exc:
            raise LoopError(
                "forwarded_prompt_unavailable",
                f"refusing to forward: {exc.message}") from exc
        approval_binding = str(record.get("prior_digest") or "") or str(approved_digest)
        parked_cycle = record.get("cycle")
        if not isinstance(parked_cycle, int) or parked_cycle < 1:
            parked_cycle = 1
        # Append the non-authoritative clock at the actual forward (R137); the parked
        # `body` stays deterministic and the message id keys on the approval binding.
        forward = self._resume_forward(
            stamp_forwarded_at(body), cycle=parked_cycle, approval_binding=approval_binding,
            decision_str=str(record.get("decision") or ""),
            reviewed_checkpoint_id=str(record.get("reviewed_checkpoint_id") or ""))
        # prompt_forwarded -> CLAUDE_RUNNING (the legal S7 exit). Reached whether
        # the send happened now or was already durable from a crashed prior
        # attempt (duplicate-suppressed): the journal still lands at CLAUDE_RUNNING
        # exactly once.
        self.machine.transition(
            CLAUDE_RUNNING, "prompt_forwarded",
            detail={"cycle": parked_cycle, "message_id": forward.message_id,
                    "cross_process_resume": True,
                    "duplicate_suppressed": forward.duplicate_suppressed})
        if forward.sent:
            self._forwarded.append(forward.message_id)
            if self.breakers is not None:
                self.breakers.record_progress()
        # Delete the record only AFTER the forward + transition succeeded, mirroring
        # the in-loop consume point, so a crash before this leaves the approved
        # record intact for an idempotent retry rather than losing the handoff.
        consume_pending_prompt(self.journal, self.run_id,
                               prior_digest=approval_binding)
        return (forward.sent_prompt or prompt), parked_cycle

    # -- the run ------------------------------------------------------------

    def run(self, first_prompt: str) -> LoopRun:
        """Run bounded cycles until the loop stops or the cycle bound is reached."""
        cycles: list[CycleResult] = []
        prompt = first_prompt
        stopped = ""
        start_index = 1
        # M0-T045: cross-process resume. A run approved at WAIT (via
        # `resume-pending-prompt`, in a separate invocation) rests at
        # FORWARD_PROMPT. Complete that approved forward here BEFORE the cycle loop,
        # so run_cycle only ever sees its legal entry states, then continue from
        # CLAUDE_RUNNING - including actuating an ARMED rotation at the safe seam,
        # which is the whole point of the R595 rehearsal.
        if self.machine.current_state == FORWARD_PROMPT:
            prompt, parked_cycle = self._resume_approved_forward()
            next_index = parked_cycle + 1
            if next_index <= self.config.max_cycles and (
                    self.rotation_pending() or self._active_substitution() is not None):
                seam = self._rotate_at_seam(cycle=next_index)
                if seam.paused:
                    return LoopRun(
                        run_id=self.run_id, mode=self.mode, cycles=(),
                        final_state=self.machine.current_state, stopped=seam.stopped,
                        budget=self.touches.report(),
                        forwarded_message_ids=tuple(self._forwarded),
                        provider_calls=self.provider_calls,
                        rotations=tuple(self._rotations))
            start_index = next_index
        for index in range(start_index, self.config.max_cycles + 1):
            result = self.run_cycle(prompt, cycle=index)
            cycles.append(result)
            if result.stopped:
                stopped = result.stopped
                break
            if not self.config.forwards:
                # Shadow forwards nothing, so one observation is the whole run.
                # (Checked before `continues`: since V1.1 correction B-2 a shadow
                # cycle closes into PREFLIGHT, which is not a continuing state.)
                stopped = "shadow_observation_complete"
                break
            if not result.continues:
                stopped = "cycle_did_not_continue"
                break
            if result.forward is None or not result.forward.sent:
                stopped = "forward_suppressed"
                break
            # V1.1 correction B-1: the durable handoff has a CONSUMER. The next
            # cycle's unit receives EXACTLY the prompt whose outbox row was just
            # marked sent - never the original first prompt again. Fails closed:
            # a sent forward without its prompt bytes refuses rather than
            # silently re-sending the wrong instruction.
            if not result.forward.sent_prompt:
                raise LoopError(
                    "forwarded_prompt_unavailable",
                    f"cycle {index} marked outbox message "
                    f"{result.forward.message_id!r} sent but carried no prompt bytes "
                    f"for the next unit; refusing to fall back to the original prompt")
            prompt = result.forward.sent_prompt
            # V1.2 (D-004): SEAM. Honor any pending rotation BEFORE dispatching
            # the next unit. This is structurally the only place rotation acts:
            # the just-finished unit has returned and no new unit is in flight, so
            # the finish-current-unit invariant (S11.2) holds by construction. A
            # detected downgrade (B) and a context-threshold crossing (C) share
            # this one path. Only fires when there IS a next unit to relaunch.
            # A seam acts when there is a pending rotation OR while an orchestrator-
            # role substitution is active (so the pinned model is re-probed every
            # seam and restored the moment it is available - D-004 am.26 / D-007
            # am.11). Only fires when there IS a next unit to relaunch.
            if index < self.config.max_cycles and (
                    self.rotation_pending() or self._active_substitution() is not None):
                seam = self._rotate_at_seam(cycle=index + 1)
                if seam.paused:
                    # Pinned model unavailable and NOT a quota-exhausted
                    # orchestrator substitution: PAUSE + notify. The worker default
                    # never continues on a substitute model.
                    stopped = seam.stopped
                    break
                # Relaunched: the next cycle dispatches the SAME forwarded prompt on
                # the fresh session id - on the pinned model, or on the substitute
                # model while an orchestrator-role substitution is active.
        else:
            stopped = "max_cycles_reached"
        return LoopRun(
            run_id=self.run_id, mode=self.mode, cycles=tuple(cycles),
            final_state=self.machine.current_state, stopped=stopped,
            budget=self.touches.report(),
            forwarded_message_ids=tuple(self._forwarded),
            provider_calls=self.provider_calls,
            rotations=tuple(self._rotations))
