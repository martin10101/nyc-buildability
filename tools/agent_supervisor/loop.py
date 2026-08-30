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
* **limited-auto** - the bounded unattended mode (D-023 item 1). It is OFF, and
  `LoopConfig` still raises `LimitedAutoRefused` for every launch that does not
  carry an EXPLICIT owner enable (`owner_enabled_bounded_auto`, set only by the
  `--owner-enable-bounded-auto` operator flag). No default, parse error,
  migration, downgrade, config file, or model can set that field, and
  `RUNNABLE_MODES` deliberately does not contain the mode, so nothing reaches it
  by widening a list. M0-T079 implemented the mode's machinery - durable
  owner-controlled run budgets (`run_budget.py`), every circuit breaker wired to
  its real event site, live pre-dispatch probes (`recovery_probes.py`), and
  typed structured refusals (`refusals.py`) - which is what the directive asked
  for; ACTIVATING it on a live host remains separately owner-gated (R595 /
  D-023-R033) and nothing here lifts that.

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
from . import launch_seam
from . import rotation
from . import session_continuity as sc
from . import loop_turnover as lt
from . import turnover_seam as ts
from .audit_log import AuditChainError
from . import loop_breakers as lb
from .circuit_breakers import GAUGE_LIMITS
from .claude_runner import QUOTA_EXHAUSTED_REASON, broker_permission_handler
from .codex_reviewer import build_forwarded_prompt, stamp_forwarded_at
from .config import ModelChain
from .durable_state import JournalError
from .errors import LoopError
from .evidence import STOP_FOR_OWNER, build_packet
from .models import ClaudeCheckpoint, CodexDecision, QueuedAsk, digest_of, to_utc_iso
# M0-T079: owner-touch accounting moved to its own module under the
# modularity rule. Re-exported here so every existing caller, test, and
# `from .loop import ...` import site is unchanged.
from .owner_touch import (
    COUNTED_TOUCH_KINDS,
    OWNER_TOUCH_KEY,
    TOUCH_BLOCKING_ASK,
    TOUCH_NOTIFY,
    TOUCH_SUPERVISED_APPROVAL,
    TOUCH_SYNCHRONOUS_STOP,
    BudgetReport,
    OwnerTouch,
    OwnerTouchLedger,
)
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
from .process import CONTAINMENT_JOB_OBJECT
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

#: The modes THIS module runs WITHOUT an owner enable. `replay` lives in
#: `replay.py`. `limited-auto` is deliberately ABSENT: it is owner-gated, and
#: keeping it out of this tuple is what makes "no default, parse error,
#: migration, or downgrade reaches it" true structurally rather than by comment.
RUNNABLE_MODES: tuple[str, ...] = (MODE_SHADOW, MODE_SUPERVISED)

#: Modes that exist, are implemented, and run ONLY behind an explicit per-launch
#: owner enable. Membership here authorizes nothing on its own: `LoopConfig`
#: refuses every one of these unless `owner_enabled_bounded_auto` is True, which
#: only the operator flag sets (R595 / D-023-R033).
OWNER_GATED_MODES: tuple[str, ...] = (MODE_LIMITED_AUTO,)

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
#: on recover_boot's SAFE_CHECKPOINT classification (cmd_start) plus the
#: single-instance lock. HONEST LIMIT (M0-T052 G5 C3): the operative guarantee
#: against resuming OVER AN ORPHANED WORKER is the platform kill-on-close
#: containment (the Windows Job Object). recover_boot's surviving-child check
#: fails closed only for RECORDED children, and the production launch path does
#: not yet record children (wiring them is the M0-T053 follow-up), so on a host
#: without live kill-on-close (POSIX, or the Windows taskkill fallback) a
#: START_CLAUDE resume is NOT double-launch-safe and is barred by the
#: supervised-auto activation record (M0-T052 G5 C1 pin). Before
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

#: M0-T080 / D-023-R013: EMPTY, and deliberately so. This name used to re-export
#: `config.DEFAULT_ORCHESTRATOR_MODEL_CHAIN`, three model ids the owner had never
#: approved, which any loop built without a controller config silently inherited.
#: A loop with no configured chain now has NOTHING to select from, and every
#: selection act against it stops safely
#: (`approved_models.ApprovedModels.assert_populated`).
DEFAULT_MODEL_CHAIN: tuple[str, ...] = ()

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


class LimitedAutoRefused(LoopError):
    """`limited-auto` was named without the owner enable. Refused before anything is built."""

    def __init__(self) -> None:
        super().__init__(
            "limited_auto_refused",
            "limited-auto is DISABLED for this launch. The bounded unattended mode is "
            "implemented (M0-T079: durable owner-controlled run budgets, wired circuit "
            "breakers, live pre-dispatch probes, typed refusals) but it is OFF by default "
            "and is never reachable from a configuration default, a missing value, a parse "
            "error, a migration, or a downgrade. Enabling it is a separate explicit owner "
            "activation recorded through directive compliance (D-007 S12; R595 / "
            "D-023-R033), supplied per launch as --owner-enable-bounded-auto.")


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
    #: M0-T056 (R595): the owner's per-run turnover-actuation authorization. Set to
    #: True ONLY by the `--authorize-turnover-actuation` operator flag (cli.py). It
    #: is the single signal `worker_turnover.default_actuation_authorization` reads;
    #: default False keeps the record-intent-only path byte-identical to today and
    #: preserves every existing caller (a run the owner did not explicitly authorize
    #: never auto-redispatches a worker).
    turnover_actuation_authorized: bool = False
    #: M0-T079 (D-023 item 1; R595 / D-023-R033): the owner's EXPLICIT per-launch
    #: enable for the bounded unattended mode. Set to True ONLY by the
    #: `--owner-enable-bounded-auto` operator flag (cli.py). Default False means
    #: `mode="limited-auto"` raises `LimitedAutoRefused` exactly as it always has,
    #: so no configuration default, parse error, migration, or downgrade reaches
    #: the mode - and every existing caller is byte-for-byte unchanged.
    owner_enabled_bounded_auto: bool = False

    def __post_init__(self) -> None:
        if self.mode == MODE_LIMITED_AUTO and not self.owner_enabled_bounded_auto:
            raise LimitedAutoRefused()
        if (self.mode not in RUNNABLE_MODES
                and not (self.mode in OWNER_GATED_MODES
                         and self.owner_enabled_bounded_auto)):
            raise LoopError(
                "unknown_mode",
                f"{self.mode!r} is not a runnable loop mode; expected one of "
                f"{list(RUNNABLE_MODES)} (replay runs in replay.py, which makes no model "
                f"calls; {list(OWNER_GATED_MODES)} additionally require an explicit owner "
                f"enable)")
        if self.owner_enabled_bounded_auto and self.mode not in OWNER_GATED_MODES:
            raise LoopError(
                "owner_enable_without_gated_mode",
                f"the bounded-mode owner enable was supplied for mode {self.mode!r}, which "
                f"is not owner-gated; an enable that does not name the mode it enables is "
                f"refused rather than ignored")
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
        """True for supervised and for the owner-enabled bounded mode.

        Shadow forwards nothing, ever. The two forwarding modes differ in WHO
        authorizes each forward, not in whether one happens: supervised holds
        every prompt for an operator approval bound to its digest; bounded
        forwards an AUTO-tier prompt itself, under the durable run budget and the
        wired circuit breakers, and stops synchronously for anything else.
        """
        return self.mode in (MODE_SUPERVISED, MODE_LIMITED_AUTO)

    @property
    def unattended(self) -> bool:
        """True only for the owner-enabled bounded mode: nobody is watching.

        The one behavioural consequence inside the loop: an AUTO-tier forward is
        not parked at WAIT_FOR_OWNER. Every other stop - ASK, HARD-DENY,
        HALT_UNSAFE, STOP_FOR_OWNER, a tripped breaker, an exhausted budget - is
        identical to supervised, because an unattended run may only ever do LESS
        than a supervised one, never more.
        """
        return self.mode == MODE_LIMITED_AUTO


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
    #: M0-T079 (D-023 item 1): the durable owner-controlled run budget's report -
    #: what the owner set, how much was spent, and whether it stopped the run.
    #: None on a run with no budget ledger, which is also an unlimited run.
    run_budget: dict[str, Any] | None = None

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
            "run_budget": dict(self.run_budget) if self.run_budget else None,
            # The bounded unattended mode is off unless the owner enabled it for
            # THIS launch; a run object reports what it actually was.
            "limited_auto_enabled": self.mode == MODE_LIMITED_AUTO,
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
    #: M0-T080: the FULL persisted handoff, formatted as the successor's first
    #: prompt. Non-empty exactly when the turnover was an explicit REORIENTATION;
    #: empty on a real `--resume`, where the successor already has the context.
    reorientation_prompt: str = ""


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

# M0-T093 modularity split (facade-preserving; the M0-T080 / unit-G
# operator_channel_cli precedent): the pending-prompt approval-binding block
# - approval_digest, parked/approved/consumed record handling, the
# covered-instruction reconstruction (M0-T048), and the sealed-audit
# cross-check - moved VERBATIM to `pending_prompt.py`. These re-exports keep
# every existing `loop.<name>` import site working unchanged.
from .pending_prompt import (  # noqa: E402,F401
    APPROVAL_DIGEST_FIELDS,
    OPERATOR_APPROVAL_EVENT,
    approval_digest,
    approve_pending_prompt,
    consume_pending_prompt,
    is_synchronous_stop,
    pending_prompt_key,
    verify_covered_instruction,
    verify_approved_digest_against_audit,
)


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
        worker_turnover: Any = None,
        guardrail_bridge: Any = None,
        run_budget: Any = None,
        handoff_verifier: Any = None,
        review_model: str = "",
        advisory_model: str = "",
        resume_max_age_seconds: float | None = None,
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
        # M0-T080: TWO identities, deliberately separate attributes.
        #
        # `_provider_session_id` is the id the PROVIDER issued and reported on its
        # stream. It is the only thing `--resume` accepts, it is restored from
        # durable state so a crash-resume does not forget which session did the
        # work, and it is what the broker binds a request to.
        #
        # `_rotation_record_key` is SUPERVISOR-INTERNAL bookkeeping naming the
        # last rotation ledger row. Before this task one attribute held both
        # meanings: the loop read a real provider id off the stream and then
        # OVERWROTE it with an invented `sup-<uuid4>` at every rotation, so the
        # recorded "new session id" named a session no provider had ever issued
        # and the successor launched unresumed.
        recorded_session = sc.recorded_provider_session(journal, run_id=run_id)
        self._provider_session_id = (recorded_session.session_id
                                     if recorded_session is not None else "")
        # M0-T123 (D-024-R332/R333): the recorded session's last-observed ceiling
        # telemetry, restored so the pre-first-dispatch launch seam can decide -
        # BEFORE any provider contact - whether continuing this session would cross
        # the 400k ceiling. `None`/False mean unknown, which the seam treats as
        # fail-closed on a continuation (never assumed below the ceiling).
        self._recorded_session_tokens = (recorded_session.context_tokens
                                         if recorded_session is not None else None)
        self._recorded_session_usage_known = (
            bool(recorded_session.usage_known) if recorded_session is not None else False)
        self._rotation_record_key = ""
        self._resume_max_age_seconds = resume_max_age_seconds
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
        # M0-T054 increment 4 (qualifying evidence: reproduced R289 incident,
        # D-010 source-028): the optional WORKER-layer Fable->Opus turnover seam.
        # Default None keeps every existing caller and test byte-for-byte: when
        # absent the missing-checkpoint path is 100% unchanged. When injected it is
        # consulted at that ONE seam, and only a confirmed FABLE_EXHAUSTED verdict
        # ever diverges (worker_turnover.WorkerTurnoverIntegration).
        self._worker_turnover = worker_turnover
        # M0-T093 (D-024 Phase E, qualifying evidence D-024-R103): the optional,
        # DISTINCT guardrail-refusal seam (refusal_bridge.
        # GuardrailBridgeIntegration), consulted only AFTER the quota turnover
        # seam declined to diverge - D-024-R075 keeps the two policies'
        # triggers, counters, and transitions separate in both directions.
        # Default None keeps the path byte-for-byte unchanged; on this build a
        # recognized refusal is RECORDED only, never actuated (SHADOW-ONLY).
        self._guardrail_bridge = guardrail_bridge
        #: The last valid checkpoint id this run received - the safe checkpoint a
        #: turnover redispatch resumes the SAME bounded unit from.
        self._last_checkpoint_id = ""
        #: M0-T080: the last VALID checkpoint object. The S11.3 handoff is built
        #: from it (completed work, changed files, tests, blockers, owner gates,
        #: and the SHA the worker finished on), so the handoff describes the real
        #: unit instead of the six-field snapshot the seams used to write.
        self._last_checkpoint: Any = None
        # M0-T079 (D-023 item 1): the durable owner-controlled run budget
        # (`run_budget.RunBudgetLedger`). Default None keeps every existing caller
        # and test unchanged - with no ledger there is no timer, which is also
        # exactly what an unlimited budget means (D-023-R037). When one is
        # injected the loop asks it, between cycles only, whether the run may take
        # another step, and persists the breaker tallies through it so a
        # crash-resume cannot hand the run back an allowance it already spent.
        self.run_budget = run_budget
        #: The checkpoint id the PREVIOUS cycle received, for the no-progress
        #: breaker. Distinct from `_last_checkpoint_id`, which is the safe
        #: checkpoint a turnover resumes from and is updated in the same place.
        self._previous_checkpoint_id = ""
        # M0-T080: the FULL S11.3 turnover path all three rotation seams take -
        # safe-seam check, handoff build, verify, durable persist, READY gate,
        # post-launch identity check. `handoff_verifier` is the live review-model
        # seam; with none injected the supervisor verifies DETERMINISTICALLY by
        # re-deriving every field from its own durable facts and records that it
        # did (S3.3 permits review_model OR deterministic verification), so the
        # handoff is never simply asserted.
        self._seam = ts.SeamTurnover(
            journal=journal, audit=audit, run_id=run_id,
            verifier=handoff_verifier, review_model=review_model,
            advisory_model=advisory_model)
        #: What the last completed turnover commanded the successor to be. The
        #: post-launch check compares the successor's own report against it.
        self._successor_expectation: ts.SuccessorExpectation | None = None

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

    # -- M0-T079: the counter breakers, at their real event sites -------------
    #
    # WHICH counter one production event ticks, how the per-day window gets its
    # UTC day, when a forward counts as progress, and how the tallies reach
    # durable storage all live in `loop_breakers.py` - they change for entirely
    # different reasons than the S7 wiring this module owns. These are the thin
    # delegating methods; the event map is documented there.

    def _daily_breaker(self, name: str) -> tuple[bool, str]:
        return lb.tick_daily(self.breakers, self.run_budget, name)

    def _breakers_for_event(self, *names: str) -> tuple[bool, str, str]:
        return lb.tick_event(self.breakers, self.run_budget, *names)

    def _reset_breaker(self, name: str) -> None:
        lb.reset(self.breakers, name)

    def _persist_breaker_tallies(self) -> None:
        lb.persist(self.breakers, self.run_budget)

    def _record_forward_progress(self, decision: "CodexDecision | str | None") -> None:
        lb.record_progress(self.breakers, decision)

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
            session_id_getter=lambda: self._provider_session_id,
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

    def _rotate_over_ceiling_before_first_dispatch(self, *, cycle: int) -> bool:
        """Rotate a recorded over-ceiling session to a fresh one BEFORE the first dispatch.

        The reproduced cycle-2 defect (D-024-R332/R333): the durable
        `rotation_pending=true` / `rotation_pending_reason=context_threshold` set
        when a prior unit crossed the 400k ceiling (604,772 tokens) was left
        UNCONSUMED across the next START, which then dispatched a unit on the
        over-ceiling session that ran to 640,224 tokens and died. The between-cycle
        and FORWARD_PROMPT rotation seams both check `rotation_pending`, but the
        ordinary IDLE->PREFLIGHT->first-cycle start never did - so the ceiling was
        never evaluated before the first provider contact.

        This is that missing pre-first-dispatch seam. It routes the decision through
        the ONE launch seam (`launch_seam.evaluate_ceiling`) and fires when either
        the durable `rotation_pending` flag carries a context-shedding reason, or the
        recorded session's known telemetry is at/above the ceiling. On a fire it
        SHEDS the over-ceiling session at the safe seam: the recorded provider
        session is forgotten (so nothing downstream can `--resume` it and the old
        oversized transcript receives no new events), any resume binding on the
        runner is dropped, and the durable rotation_pending flag is consumed - so the
        first unit launches as a fresh, distinct session in the packet worktree.
        Returns True when it rotated, False when there was nothing to shed.
        """
        if not self.config.forwards:
            # A shadow observation dispatches nothing durable and never resumes; the
            # pressure path is forwarding-mode only (see `_flag_rotation_if_needed`).
            return False
        reason = str(self.journal.get_state(rotation.ROTATION_REASON_KEY, "") or "")
        pending_context = (self.rotation_pending()
                           and reason in sc.CONTEXT_SHEDDING_REASONS)
        ceiling = self.context_rotation_threshold or launch_seam.CONTEXT_ROTATION_CEILING
        # Route the telemetry decision through the single seam. `rotate` names an
        # at/above-ceiling session; a recorded session whose telemetry is known and
        # over the ceiling triggers the shed even without a durable pending flag.
        ceiling_decision = launch_seam.evaluate_ceiling(
            resuming=bool(self._provider_session_id),
            session_context_tokens=self._recorded_session_tokens,
            session_usage_known=self._recorded_session_usage_known,
            ceiling=ceiling)
        known_over = ceiling_decision is not None and ceiling_decision.rotate
        if not (pending_context or known_over):
            return False
        shed_session = self._provider_session_id
        shed_tokens = (self._recorded_session_tokens
                       if self._recorded_session_usage_known else None)
        # Shed the over-ceiling session: nothing downstream may resume it.
        self._provider_session_id = ""
        self._recorded_session_tokens = None
        self._recorded_session_usage_known = False
        sc.clear_provider_session(self.journal)
        drop_resume = getattr(self.runner, "with_resume", None)
        # Drop any resume binding on the runner so the fresh launch carries no
        # `--resume`. `with_resume("")` is refused by the runner (an empty id is not
        # a session), so a bound runner is only cleared by re-deriving a fresh one;
        # in practice the ordinary first-dispatch runner is never resume-bound, so
        # this is a defensive no-op unless a prior act bound it.
        if callable(drop_resume) and getattr(
                getattr(self.runner, "config", None), "resume_session_id", ""):
            # Re-create the runner without the resume binding by replacing the config.
            cfg = getattr(self.runner, "config", None)
            if cfg is not None and hasattr(cfg, "resume_session_id"):
                self.runner.config = dataclasses.replace(
                    cfg, resume_session_id="", resume_context_tokens=None,
                    resume_usage_known=False)
        rotation.clear_rotation_pending(self.journal)
        self.journal.set_state(rotation.ROTATION_REASON_KEY, "")
        record = {
            "cycle": cycle,
            "reason_code": reason or "context_threshold",
            "shed_provider_session_id": shed_session,
            "shed_context_tokens": shed_tokens,
            "ceiling": ceiling,
            "pending_flag_consumed": pending_context,
            "known_over_ceiling": known_over,
        }
        self._rotations.append({**record, "kind": "over_ceiling_shed_pre_dispatch",
                                "recorded_at_utc": to_utc_iso()})
        if self.audit is not None:
            self.audit.append(
                "over_ceiling_session_shed", run_id=self.run_id,
                policy_result="over_ceiling_resume_forbidden",
                detail={**record,
                        "note": "a session at or above the 400k ceiling is NEVER resumed "
                                "(D-024-R333); it was shed at the safe seam BEFORE the "
                                "first dispatch and the next unit launches as a fresh, "
                                "distinct session in the packet worktree"})
        return True

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
            "outgoing_provider_session_id": self._provider_session_id,
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

    # -- M0-T080: the FULL S11.3 turnover every seam takes -------------------
    #
    # WHICH facts this run can state about the work, and WHERE in the cycle the
    # post-rotation gates apply, live in `loop_turnover.py` - they change for
    # entirely different reasons than the S7 wiring this module owns. These are
    # the thin delegating methods; the mechanics are documented there.

    def _seam_facts(self, *, reason_code: str, cycle: int) -> ts.SeamFacts:
        return lt.seam_facts(self, reason_code=reason_code, cycle=cycle)

    def _full_turnover(self, *, cycle: int, reason_code: str,
                       successor_model: str) -> ts.SeamTurnoverResult:
        return lt.full_turnover(self, cycle=cycle, reason_code=reason_code,
                                successor_model=successor_model)

    def _turnover_refused(self, *, cycle: int, reason_code: str,
                          error: "ts.SeamTurnoverError") -> "SeamRotation":
        return lt.turnover_refused(self, cycle=cycle, reason_code=reason_code,
                                   error=error)

    def _post_rotation_gates(self, checkpoint: Any, run_result: Any, *, cycle: int,
                             touches: list[OwnerTouch]) -> tuple[str, str] | None:
        return lt.post_rotation_gates(self, checkpoint, run_result, cycle=cycle,
                                      touches=touches)

    def _resume_capability_verified(self) -> bool:
        return lt.resume_capability_verified(self)

    def _actuate_resume(self, provider_session_id: str) -> None:
        lt.actuate_resume(self, provider_session_id)

    def _rotate_at_seam(self, *, cycle: int) -> "SeamRotation":
        """Rotate the session BEFORE dispatching the next unit (B and C share this).

        The single rotation code path for both a detected model downgrade (B) and
        a context-threshold crossing (C). Structurally seam-only: only run() calls
        it, always between cycles, and it asserts nothing is in flight by requiring
        the durable rotation_pending flag. Order: refresh the D-004 SESSION_HANDOFF
        snapshot -> strict pinned-model check -> the FULL S11.3 turnover
        (`_full_turnover`: safe seam, handoff build + verify, durable persist,
        rotation record with both identities, armed READY gate) -> or PAUSE+notify
        when the pinned model is unavailable.
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
                        exhausted_model=gated_model, substitution=substitution)
                return self._pause_model_unavailable(
                    cycle=cycle, reason_code=reason_code, model=gated_model,
                    handoff_digest=handoff_digest)

        # M0-T080: the FULL S11.3 turnover, replacing the direct
        # `complete_rotation` call this seam used to make. Safe-seam check, S11.3
        # handoff build + verification, durable persistence of the VERIFIED
        # handoff, the rotation record carrying BOTH identities, and the armed
        # READY gate all happen inside `_full_turnover`.
        old_session = self._provider_session_id
        successor_model = self._current_model or self.pinned_model
        try:
            turnover = self._full_turnover(cycle=cycle, reason_code=reason_code,
                                           successor_model=successor_model)
        except ts.SeamTurnoverError as exc:
            return self._turnover_refused(cycle=cycle, reason_code=reason_code, error=exc)
        except LoopError as exc:
            # M0-T080 correction U14 (G3 N1). `_full_turnover` can raise a
            # LoopError AFTER the rotation is durably recorded - the actuation
            # step does, when the runner cannot be rebound to resume
            # (`resume_actuation_unavailable`). Letting it escape left a durable
            # record of a resume that never reached a launch. It is refused
            # through the same fail-closed path as every other seam gate, so the
            # owner is told and the run pauses instead of continuing on a
            # continuity it does not have.
            return self._turnover_refused(
                cycle=cycle, reason_code=reason_code,
                error=ts.SeamTurnoverError(exc.code, exc.message))
        self.journal.set_state(rotation.ROTATION_REASON_KEY, "")
        relaunch = {
            "cycle": cycle, "reason_code": reason_code,
            **turnover.to_dict(),
            "pinned_model": self.pinned_model,
            "model": self._current_model,
            "tier": NOTIFY, "recorded_at_utc": to_utc_iso(),
        }
        self._rotations.append(relaunch)
        if self.audit is not None:
            self.audit.append(
                "supervisor_rotation_relaunch", run_id=self.run_id,
                policy_result=reason_code, output_digest=turnover.handoff_digest,
                detail={**relaunch,
                        "note": "relaunch continues on the CURRENT model; the successor "
                                "either RESUMES the recorded provider session or is "
                                "explicitly re-oriented from the full verified handoff, and "
                                "the record says which. A completed rotation is a NOTIFY "
                                "event (S11.3)"})
        model_label = self._current_model or self.pinned_model or "the configured model"
        return SeamRotation(relaunched=True, paused=False, stopped="",
                            substituted=substitution is not None,
                            reason=(f"rotated {reason_code}: outgoing provider session "
                                    f"{old_session or '(none recorded)'!r}, relaunching on "
                                    f"{model_label} by {turnover.continuity.mode}"),
                            reason_code=reason_code, record=relaunch,
                            reorientation_prompt=turnover.reorientation_prompt)

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

    def _switch_at_seam(self, *, cycle: int, reason_code: str, exhausted_model: str,
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
        old_session = self._provider_session_id
        # M0-T080: the FULL S11.3 turnover, not a direct `complete_rotation`. A
        # chain switch is by definition CROSS-MODEL, so the continuity decision
        # here can only ever be an explicit reorientation - and it is recorded as
        # one, with `cross_model` named as the reason resume was impossible.
        try:
            turnover = self._full_turnover(cycle=cycle, reason_code=reason_code,
                                           successor_model=selected)
        except ts.SeamTurnoverError as exc:
            return self._turnover_refused(cycle=cycle, reason_code=reason_code, error=exc)
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
            **turnover.to_dict(),
            "started_at_utc": to_utc_iso(),
        }
        if substitution is not None:
            record["previous_switch_started_at_utc"] = str(
                substitution.get("started_at_utc", "") or "")
        self.journal.set_state(self._substitution_key(), record)
        relaunch = {
            "cycle": cycle, "reason_code": reason_code,
            **turnover.to_dict(),
            "pinned_model": self.pinned_model,
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
                policy_result=QUOTA_EXHAUSTED_REASON,
                output_digest=turnover.handoff_digest,
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
                    f"session relaunched on chain entry {selected!r} by "
                    f"{turnover.continuity.mode} (outgoing provider session "
                    f"{old_session or '(none recorded)'!r})"),
            reason_code=reason_code, record=relaunch,
            reorientation_prompt=turnover.reorientation_prompt)

    def _stop_chain_exhausted(self, *, cycle: int, reason_code: str,
                              exhausted_model: str,
                              attempts: Sequence[Mapping[str, Any]]) -> "SeamRotation":
        return lt.stop_chain_exhausted(self, cycle=cycle, reason_code=reason_code,
                                       exhausted_model=exhausted_model,
                                       attempts=attempts)

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
        self._refresh_session_handoff(
            cycle=cycle, reason_code="model_substitution_ended")
        old_session = self._provider_session_id
        self._actuate_model(self.pinned_model)
        # M0-T080: the FULL S11.3 turnover, not a direct `complete_rotation`.
        # Returning to the pin is also cross-model, so this too is an explicit,
        # recorded reorientation rather than a rotation that merely claimed one.
        try:
            turnover = self._full_turnover(cycle=cycle,
                                           reason_code="model_substitution_ended",
                                           successor_model=self.pinned_model)
        except ts.SeamTurnoverError as exc:
            return self._turnover_refused(cycle=cycle,
                                          reason_code="model_substitution_ended", error=exc)
        self._current_model = self.pinned_model
        self.journal.set_state(rotation.ROTATION_REASON_KEY, "")
        ended = {**dict(substitution), "active": False,
                 "ended_cycle": cycle, "ended_at_utc": to_utc_iso(),
                 "return_rotation_record_key": turnover.rotation_record_key}
        self.journal.set_state(self._substitution_key(), ended)
        relaunch = {
            "cycle": cycle, "reason_code": "model_substitution_ended",
            **turnover.to_dict(),
            "pinned_model": self.pinned_model,
            "model": self.pinned_model, "restored_from_substitute": left_behind,
            "launched_model": self.launched_model(),
            "tier": NOTIFY, "recorded_at_utc": to_utc_iso(),
        }
        self._rotations.append(relaunch)
        if self.audit is not None:
            self.audit.append(
                "model_substitution_ended", run_id=self.run_id,
                policy_result="pinned_model_available",
                output_digest=turnover.handoff_digest,
                detail={**relaunch, "substitute_model": left_behind,
                        "note": "the pinned model is available again at this seam; the "
                                "orchestrator-role session returns to it, with the runner "
                                "rebound to the pin before this record was written and the "
                                "successor re-oriented from the full verified handoff. "
                                "Never silent (D-004 am.26 / D-007 am.11)"})
        return SeamRotation(
            relaunched=True, paused=False, stopped="", substituted=False,
            reason=(f"pinned model {self.pinned_model!r} available again; returned from "
                    f"substitute {left_behind!r} by {turnover.continuity.mode} (outgoing "
                    f"provider session {old_session or '(none recorded)'!r})"),
            reason_code="model_substitution_ended", record=relaunch,
            reorientation_prompt=turnover.reorientation_prompt)

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

        def breaker_stop(name: str, message: str, *, state: str,
                         trigger: str = "", note: str = "") -> CycleResult:
            """M0-T079: one synchronous pause for a tripped S13.8 counter.

            The shape is the same at every event site: take the S7 edge when
            there is one to take (`trigger` empty ends the cycle at its current
            legal state instead), record the owner touch, persist the tallies so
            the trip survives a restart, and stop.
            """
            if trigger:
                self.machine.transition(state, trigger,
                                        detail={"cycle": cycle, "breaker": name})
            # C6 (G5 I5): seal the trip itself, by name and value. A trip taken
            # WITHOUT an S7 trigger - the cycle counter and the pre-dispatch
            # model-call counter both stop at their legal entry state without
            # transitioning - otherwise reached the hash-chained log only through
            # a transition detail that, in those cases, does not exist. A limit
            # that fired is exactly the kind of event a tamper-evident log is for.
            if self.audit is not None:
                self.audit.append(
                    "circuit_breaker_tripped", run_id=self.run_id,
                    policy_result="circuit_breaker_hard_threshold",
                    detail={"breaker": name, "cycle": cycle,
                            "value": (self.breakers.value(name)
                                      if self.breakers is not None else None),
                            "transitioned": bool(trigger), "trigger": trigger,
                            "state": state, "reason": message})
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="circuit_breaker_hard_threshold",
                reason=message, cycle=cycle,
                basis=f"S13.8 hard threshold ({name}){note}"))
            self._persist_breaker_tallies()
            return stop("circuit_breaker_hard_threshold", message,
                        self.machine.current_state if trigger else state)

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

        # M0-T079: the per-task CYCLE counter, at the one place a cycle begins.
        # Like the resource guard below it stops at the current LEGAL entry state:
        # no transition, no stranding, and no provider call has happened yet.
        tripped, message = self._breaker("supervisor_cycles_per_task")
        if tripped:
            return breaker_stop("supervisor_cycles_per_task", message, state=entry)
        if message:
            notify.append("circuit_breaker_warning")

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
        # M0-T079: the per-task and per-day MODEL-CALL counters, at a real
        # provider dispatch. Ticked BEFORE the call, so a trip stops the run
        # without spending the call it would have been the (N+1)th of.
        tripped, name, message = self._breakers_for_event(
            "model_calls_per_task", "model_calls_per_day")
        if tripped:
            return breaker_stop(
                name, message, state=self.machine.current_state,
                trigger=("unsafe_condition"
                         if self.machine.current_state == CLAUDE_RUNNING else ""),
                note=", before the provider dispatch")
        if message:
            notify.append("circuit_breaker_warning")

        # G3 V-1: the approval broker is now WIRED. In supervised mode each
        # in-scope tool request the worker makes routes through the four-tier
        # policy + broker; an AUTO/approved tool is PERMITTED and executes. In
        # shadow mode the handler permits nothing (deny/observe only) - shadow
        # semantics unchanged.
        self.provider_calls += 1
        run_result = self.runner.run_unit(
            prompt, permission_handler=self._permission_handler())
        # M0-T080: capture the PROVIDER's own session identity at unit
        # completion and persist it, so a later rotation can really resume the
        # session that did the work instead of minting one. A stream that
        # reported two different ids is AMBIGUOUS: the id is dropped rather than
        # recorded, because an ambiguous identity must never authorize a
        # `--resume` (S8.2 - unattended work resumes only the exact recorded
        # session).
        session_id = str(getattr(run_result, "session_id", "") or "")
        session_conflict = str(getattr(run_result, "session_id_conflict", "") or "")
        if session_id and not session_conflict:
            self._provider_session_id = session_id
            # M0-T123 (D-024-R332): persist the session's cumulative context
            # telemetry alongside its identity, so a later START that might continue
            # this session can evaluate the 400k ceiling BEFORE provider contact
            # instead of re-launching to measure it. `usage_known` False records the
            # tokens as unknown (never a below-ceiling zero).
            sc.record_provider_session(
                self.journal, session_id=session_id,
                model_id=self._current_model or self.pinned_model,
                run_id=self.run_id, cycle=cycle,
                context_tokens=int(getattr(run_result, "context_tokens", 0) or 0),
                usage_known=bool(getattr(run_result, "usage_known", False)))
        elif session_conflict:
            self._provider_session_id = ""
            sc.clear_provider_session(self.journal)
            notify.append("provider_session_ambiguous")
            if self.audit is not None:
                self.audit.append(
                    "provider_session_ambiguous", run_id=self.run_id,
                    policy_result="session_identity_ambiguous",
                    detail={"cycle": cycle, "conflict": session_conflict,
                            "note": "the recorded provider session id was DROPPED; an "
                                    "ambiguous identity can never be resumed"})
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
            # M0-T079: a unit that produced no valid checkpoint IS an invalid
            # output, and this is the site where that is known. The tally is
            # durable, so the counter measures consecutive invalid outputs across
            # the crash-resumes an unattended run is made of, not just within one
            # process. The cycle stops for its own specific reason either way; a
            # TRIP is surfaced as a note and a NOTIFY rather than being allowed to
            # mask a paramount ambiguous-effect or turnover stop below.
            invalid_tripped, invalid_message = self._breaker("consecutive_invalid_outputs")
            if invalid_tripped:
                notify.append("circuit_breaker_warning")
                result.notes += ("consecutive_invalid_outputs_tripped",)
                reason = f"{reason}. {invalid_message}"
            elif invalid_message:
                notify.append("circuit_breaker_warning")
            self._persist_breaker_tallies()
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
            # M0-T054 increment 4 (qualifying evidence: reproduced R289 incident,
            # D-010 source-028): before treating this failed unit as an ordinary
            # terminal stop, classify it for a grounded Fable weekly-limit
            # exhaustion. Reached ONLY with no unreconciled external effect (the
            # guard above), so a same-unit redispatch is never attempted while an
            # effect is unproven. FAIL-CLOSED: only a confirmed FABLE_EXHAUSTED
            # verdict (decision.triggered) diverges; every other verdict - and an
            # absent integration - falls through to the existing path unchanged.
            if self._worker_turnover is not None:
                decision = self._worker_turnover.evaluate(
                    run_result, current_model=self._current_model,
                    config=self.config, run_id=self.run_id, cycle=cycle,
                    safe_checkpoint_id=self._last_checkpoint_id)
                if decision.triggered:
                    self.machine.transition(
                        PAUSED_RECOVERY, "unsafe_condition",
                        detail={"cycle": cycle, "reason": decision.reason_code,
                                "turnover": decision.audit_summary})
                    touches.append(self._touch(
                        TOUCH_SYNCHRONOUS_STOP, reason_code=decision.reason_code,
                        reason=decision.reason, cycle=cycle,
                        basis="M0-T054 Fable->Opus worker turnover (R289 / D-010 "
                              "source-028)"))
                    return stop(decision.reason_code, decision.reason, PAUSED_RECOVERY)
            # M0-T093 (D-024 Phase E, D-024-R103): AFTER the quota seam declined,
            # consult the DISTINCT guardrail-refusal seam (R075 ordering: the
            # quota detect-and-hold policy always evaluates first and its
            # verdicts never enter the bridge). FAIL-CLOSED: only a narrowly
            # recognized refusal verdict (R068) diverges - and on this build it
            # only RECORDS intent and keeps the safe PAUSE; the 4.8 bridge is
            # never actuated here (SHADOW-ONLY; R595 + owner-gated C1 shape).
            if self._guardrail_bridge is not None:
                refusal_decision = self._guardrail_bridge.evaluate(
                    run_result, current_model=self._current_model,
                    config=self.config, run_id=self.run_id, cycle=cycle)
                if refusal_decision.triggered:
                    self.machine.transition(
                        PAUSED_RECOVERY, "unsafe_condition",
                        detail={"cycle": cycle,
                                "reason": refusal_decision.reason_code,
                                "guardrail": refusal_decision.audit_summary})
                    touches.append(self._touch(
                        TOUCH_SYNCHRONOUS_STOP,
                        reason_code=refusal_decision.reason_code,
                        reason=refusal_decision.reason, cycle=cycle,
                        basis="M0-T093 guardrail-refusal record-intent seam "
                              "(D-024-R068/R070/R075)"))
                    return stop(refusal_decision.reason_code,
                                refusal_decision.reason, PAUSED_RECOVERY)
            self.machine.transition(PAUSED_RECOVERY, "unsafe_condition",
                                    detail={"cycle": cycle, "reason": reason})
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="no_valid_checkpoint",
                reason=reason, cycle=cycle, basis="S14"))
            return stop("no_valid_checkpoint", reason, PAUSED_RECOVERY)

        # M0-T060 (M0-T053 G5 R4 enforcement half; 2026-08-08 pin criterion 2):
        # criterion (1) pins the host DEFAULT containment at doctor time; the
        # ACHIEVED per-cycle containment is enforced HERE, on the OTHERWISE-OK path
        # - the only path that would PROCEED. `ProcessContainer.adopt` can honestly
        # DEGRADE to taskkill at launch (job-object creation denied), and that
        # degradation was previously only RECORDED on the `claude_process_started`
        # transition detail above. Recording is not enough: unattended, nobody reads
        # the audit line, and a child that spawns its own tree can ESCAPE a non-job
        # container. A cycle that did not actually get job-strength containment is
        # therefore a FAIL-CLOSED stop with an explicit recorded reason - never a
        # silent continue (S13.2 / S13.12 invariants 10 and 11). Placed AFTER the
        # S14 checkpoint/effect reconciliation so a paramount ambiguous-effect or
        # no-checkpoint stop is never masked by this one; a cycle whose checkpoint
        # already failed stops for that reason. A cycle reporting `job_object`
        # proceeds unchanged.
        achieved = str(getattr(run_result, "containment", "") or "")
        if achieved != CONTAINMENT_JOB_OBJECT:
            fallback = str(getattr(run_result, "containment_fallback_reason", "") or "")
            containment_reason = (
                f"the cycle achieved {achieved or 'unknown'!r} containment, not "
                f"job-strength {CONTAINMENT_JOB_OBJECT!r}: a child that spawns its "
                f"own process tree can escape a non-job container, so an unattended "
                f"run must fail closed rather than proceed on it")
            if fallback:
                containment_reason += f" (fallback reason: {fallback})"
            self.machine.transition(
                PAUSED_RECOVERY, "unsafe_condition",
                detail={"cycle": cycle, "reason": "containment_degraded",
                        "containment": achieved,
                        "containment_fallback_reason": fallback})
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="containment_degraded",
                reason=containment_reason, cycle=cycle,
                basis="M0-T053 G5 R4 achieved-containment enforcement (2026-08-08 "
                      "pin criterion 2; S13.2 / S13.12 invariants 10-11)"))
            return stop("containment_degraded", containment_reason, PAUSED_RECOVERY)

        # M0-T056 fold-in of the carried M0-T060 residual (M0-T053 G5 pin P3): a
        # reported `job_object` KIND is not proof that the child is actually inside
        # the job. `ProcessContainer.adopt` records `ContainmentReport.verified_in_job`
        # from a real `is_process_in_job` membership probe; a kind that says
        # job_object while membership could NOT be confirmed gives no more real
        # containment than taskkill, so it must fail closed under an unattended loop
        # rather than proceed on an unverified claim. The strengthening is ADDITIVE
        # and freeze-safe: the runner reports the boolean explicitly, and a
        # run_result that does not carry the field at all (every pre-existing test
        # fake, and any non-Windows cycle that never reaches this job_object branch)
        # reads the True default and proceeds exactly as before. ONLY an explicit
        # `verified_in_job == False` on an otherwise job_object cycle stops here.
        verified_in_job = getattr(run_result, "containment_verified_in_job", True)
        if verified_in_job is False:
            unverified_reason = (
                f"the cycle reported {CONTAINMENT_JOB_OBJECT!r} containment but its "
                f"in-job membership could not be verified (ContainmentReport."
                f"verified_in_job is False): an unverified job assignment is not proof "
                f"of kill-on-close containment, so an unattended run fails closed rather "
                f"than proceed on an unconfirmed claim")
            self.machine.transition(
                PAUSED_RECOVERY, "unsafe_condition",
                detail={"cycle": cycle, "reason": "containment_unverified",
                        "containment": achieved, "verified_in_job": False})
            touches.append(self._touch(
                TOUCH_SYNCHRONOUS_STOP, reason_code="containment_unverified",
                reason=unverified_reason, cycle=cycle,
                basis="M0-T056 / M0-T060 verified_in_job strengthening (M0-T053 G5 "
                      "pin P3; S13.2 / S13.12 invariants 10-11)"))
            return stop("containment_unverified", unverified_reason, PAUSED_RECOVERY)

        self.machine.transition(
            CHECKPOINT_RECEIVED, "valid_checkpoint_received",
            detail={"cycle": cycle, "checkpoint_id": checkpoint.checkpoint_id,
                    "checkpoint_digest": digest_of(checkpoint.to_dict())})
        land(CHECKPOINT_RECEIVED)
        result.checkpoint_id = checkpoint.checkpoint_id
        # M0-T079: a VALID checkpoint clears the invalid-output streak. Only a
        # streak of invalid outputs is a livelock; one bad unit followed by a good
        # one is ordinary.
        self._reset_breaker("consecutive_invalid_outputs")
        # M0-T079: the no-progress counter, at its semantic site. A unit that
        # returns the SAME checkpoint id as the previous cycle advanced nothing -
        # the classic unattended livelock, where the worker keeps answering and
        # the work stands still. A new checkpoint id resets the streak.
        if (self._previous_checkpoint_id
                and checkpoint.checkpoint_id == self._previous_checkpoint_id):
            tripped, message = self._breaker("consecutive_no_progress")
            if tripped:
                # `checkpoint_unsafe` is the S7 edge out of CHECKPOINT_RECEIVED for
                # "the checkpoint itself indicated a S4.5 condition", and a
                # checkpoint that repeats its predecessor without advancing is
                # exactly such a condition. No new edge is needed.
                return breaker_stop(
                    "consecutive_no_progress", message, state=PAUSED_RECOVERY,
                    trigger="checkpoint_unsafe",
                    note=f": the worker returned checkpoint {checkpoint.checkpoint_id!r} again")
            if message:
                notify.append("circuit_breaker_warning")
        else:
            self._reset_breaker("consecutive_no_progress")
        self._previous_checkpoint_id = checkpoint.checkpoint_id
        # M0-T054: remember the safe checkpoint a later turnover would resume from.
        self._last_checkpoint_id = checkpoint.checkpoint_id
        # M0-T080: and the checkpoint itself, which is what the S11.3 handoff is
        # built from at the next seam.
        self._last_checkpoint = checkpoint
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

        # --- M0-T080: the post-rotation gates --------------------------------
        # Placed here, after the checkpoint is valid and BEFORE any evidence is
        # collected, any review is requested, or anything is forwarded - so a
        # successor that did not re-orient, or is not the session that was
        # commanded, cannot act on the work at all.
        #
        # (1) The S11.3 READY gate: a re-oriented session returns a structured
        #     READY checkpoint BEFORE any change. Armed by the turnover, cleared
        #     only by a checkpoint that satisfies it.
        # (2) Post-launch identity: the successor must report the task, branch,
        #     HEAD, and MODEL that were commanded. A model mismatch here is a
        #     fail-closed stop, not a note.
        gate_stop = self._post_rotation_gates(checkpoint, run_result, cycle=cycle,
                                              touches=touches)
        if gate_stop is not None:
            code, reason = gate_stop
            self.machine.transition(PAUSED_RECOVERY, "checkpoint_unsafe",
                                    detail={"cycle": cycle, "reason": code})
            return stop(code, reason, PAUSED_RECOVERY)

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
        # M0-T079: the reviewer is the SECOND provider dispatch in a cycle, so it
        # ticks the same model-call counters. Before the call, for the same reason.
        tripped, name, message = self._breakers_for_event(
            "model_calls_per_task", "model_calls_per_day")
        if tripped:
            return breaker_stop(name, message, state=PAUSED_RECOVERY,
                                trigger="unsafe_condition",
                                note=", before the review dispatch")
        if message:
            notify.append("circuit_breaker_warning")
        self.provider_calls += 1
        outcome = self.reviewer.review(
            packet.to_dict(), expected_task_id=self.config.task_id,
            expected_checkpoint_id=checkpoint.checkpoint_id)
        notify.extend(getattr(outcome, "notify_events", ()) or ())
        if not outcome.ok:
            # M0-T079: a reviewer answer that never validated is an invalid
            # OUTPUT; a reviewer that was unavailable is not. Only the former
            # ticks the livelock counter (`schema_retry_exhausted` is the reviewer's
            # own code for "every bounded retry came back schema-invalid").
            if str(getattr(outcome, "error_code", "")) == "schema_retry_exhausted":
                invalid_tripped, invalid_message = self._breaker(
                    "consecutive_invalid_outputs")
                if invalid_tripped or invalid_message:
                    notify.append("circuit_breaker_warning")
                if invalid_tripped:
                    result.notes += ("consecutive_invalid_outputs_tripped",)
                self._persist_breaker_tallies()
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

        # M0-T079: the REVISION-LOOP counter, at its semantic site. A REVISE says
        # the last unit's work was not accepted; a run of them is the reviewer and
        # the worker circling. Any other decision that reaches here (CONTINUE)
        # ends the streak, so the counter measures CONSECUTIVE revisions as its
        # name claims. The trip stops BEFORE the revision prompt is forwarded -
        # forwarding it is what would extend the loop.
        if decision.decision == "REVISE":
            tripped, message = self._breaker("consecutive_revision_loops")
            if tripped:
                return breaker_stop("consecutive_revision_loops", message,
                                    state=PREFLIGHT, trigger="cycle_closed")
            if message:
                notify.append("circuit_breaker_warning")
        else:
            self._reset_breaker("consecutive_revision_loops")

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

        # M0-T079: the per-task and per-day EXTERNAL-WRITE counters. Forwarding a
        # prompt into the recorded worker session is the loop's own external
        # write - the outbox row is a commitment to send, and the send leaves this
        # process. Ticked BEFORE the write, so a trip means nothing was sent.
        # (Modeled external effects that go through `ExternalEffectJournal` live
        # in github_flow.py, which a later task owns and which this one does not
        # touch.)
        tripped, name, message = self._breakers_for_event(
            "external_writes_per_task", "external_writes_per_day")
        if tripped:
            return breaker_stop(name, message, state=PREFLIGHT,
                                trigger="cycle_closed",
                                note=", before the outbound send")
        if message:
            notify.append("circuit_breaker_warning")

        # --- BOUNDED (limited-auto): forward the AUTO-tier prompt directly ---
        # M0-T079. The owner-enabled unattended mode reaches this line having
        # already run everything above it: the breakers, the budget, the policy
        # tiers, and the HARD-DENY / HALT_UNSAFE / STOP_FOR_OWNER / ASK stops,
        # all identical to supervised. The ONLY difference is that an AUTO-tier
        # forward is not parked for a human who is not there - it takes the S7
        # table's own `tier_auto` edge, which has always meant "the deterministic
        # policy classified the next action AUTO within packet authority". The
        # forward itself below is the SAME code both modes run, so an unattended
        # run can never take a different path to the send than a supervised one.
        if self.config.unattended:
            self.machine.transition(
                FORWARD_PROMPT, "tier_auto",
                detail={"cycle": cycle, "prompt_digest": prompt_digest,
                        "reason_code": verdict.reason_code,
                        "decision": decision.decision,
                        "note": "bounded unattended forward under the owner-enabled mode; "
                                "AUTO tier within packet authority, inside the durable run "
                                "budget and the wired circuit breakers"})
            land(FORWARD_PROMPT)
            return self._send_forward(forwarded_prompt, cycle=cycle, decision=decision,
                                      result=result, land=land, touches=touches,
                                      notify=notify, prompt_digest=prompt_digest)

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

        return self._send_forward(forwarded_prompt, cycle=cycle, decision=decision,
                                  result=result, land=land, touches=touches,
                                  notify=notify, prompt_digest=prompt_digest)

    def _send_forward(self, forwarded_prompt: str, *, cycle: int,
                      decision: CodexDecision, result: CycleResult,
                      land: Callable[[str], None], touches: Sequence[OwnerTouch],
                      notify: Sequence[str], prompt_digest: str) -> CycleResult:
        """Send the approved/AUTO prompt exactly once and close the cycle.

        The single send path both forwarding modes take, entered only from
        FORWARD_PROMPT. Supervised arrives here after an operator approval bound
        to `prompt_digest`; the bounded mode arrives after the `tier_auto` edge.
        Sharing the code is the point: an unattended run cannot reach the outbox
        by a route a supervised run does not also take.

        M0-T048 (R137): the non-authoritative FORWARDED AT clock is appended at
        the ACTUAL forward and excluded from the binding. The parked body stays
        timestamp-free, and the message id keys on the approval digest rather
        than these bytes, so the stamp never affects exactly-once identity.
        """
        forward = self.forward_exactly_once(stamp_forwarded_at(forwarded_prompt),
                                            cycle=cycle, decision=decision)
        result.forward = forward
        result.forwarded = forward.sent
        if forward.sent:
            self._forwarded.append(forward.message_id)
            self.machine.transition(
                CLAUDE_RUNNING, "prompt_forwarded",
                detail={"cycle": cycle, "message_id": forward.message_id,
                        "unattended": self.config.unattended})
            land(CLAUDE_RUNNING)
            if not self.config.unattended:
                # AS-4 (G5 V1.2.3 LOW): the held prompt has now been approved AND
                # forwarded, so consume its pending_prompt record. Without this a
                # later WAIT for a different ask would still carry this cycle's
                # digest and could be re-approved against a stale record. The
                # bounded mode parks nothing, so it has nothing to consume.
                consume_pending_prompt(self.journal, self.run_id,
                                       prior_digest=prompt_digest)
            self._record_forward_progress(decision)
        self._persist_breaker_tallies()
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
        # M0-T079: the cross-process resume performs the SAME external write as an
        # in-loop forward, so it ticks the same counters, before the send. A trip
        # refuses the resume with no send and no state change, like every other
        # fail-closed guard on this path.
        tripped, name, message = self._breakers_for_event(
            "external_writes_per_task", "external_writes_per_day")
        self._persist_breaker_tallies()
        if tripped:
            raise LoopError(
                "circuit_breaker_hard_threshold",
                f"refusing to complete the approved forward: {message} (breaker {name}); "
                f"the outbound send is an external write and the run has reached its "
                f"owner-set bound for them")
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
            self._record_forward_progress(str(record.get("decision") or "CONTINUE"))
        # Delete the record only AFTER the forward + transition succeeded, mirroring
        # the in-loop consume point, so a crash before this leaves the approved
        # record intact for an idempotent retry rather than losing the handoff.
        consume_pending_prompt(self.journal, self.run_id,
                               prior_digest=approval_binding)
        return (forward.sent_prompt or prompt), parked_cycle

    # -- the run ------------------------------------------------------------

    # -- M0-T079: the durable run budget, consulted only at a safe seam -------

    def _budget_stop(self) -> str:
        """`budget_exhausted` when the owner-set budget is spent, else "".

        Called ONLY between cycles (S11.2: an in-flight unit is never interrupted
        for pressure, and a budget is pressure). See `loop_breakers.budget_stop`.
        """
        return lb.budget_stop(self.run_budget, audit=self.audit, run_id=self.run_id)

    def run(self, first_prompt: str) -> LoopRun:
        """Run bounded cycles until the loop stops or the cycle bound is reached."""
        cycles: list[CycleResult] = []
        prompt = first_prompt
        stopped = ""
        start_index = 1
        # M0-T079: reconcile the persisted breaker tallies BEFORE anything runs,
        # so a crash-resume re-enters with the allowance it left behind rather
        # than a fresh one, and refuse immediately when the budget it is resuming
        # into is already spent.
        if self.run_budget is not None:
            self.run_budget.restore_counters(self.breakers)
            exhausted = self._budget_stop()
            if exhausted:
                return LoopRun(
                    run_id=self.run_id, mode=self.mode, cycles=(),
                    final_state=self.machine.current_state, stopped=exhausted,
                    budget=self.touches.report(),
                    forwarded_message_ids=tuple(self._forwarded),
                    provider_calls=self.provider_calls,
                    rotations=tuple(self._rotations),
                    run_budget=self.run_budget.report())
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
                prompt = lt.with_reorientation(seam, prompt)
            start_index = next_index
        # M0-T123 (D-024-R332/R333): the pre-first-dispatch ceiling seam. BEFORE the
        # first bounded unit of this run is dispatched - i.e. before any provider
        # contact - a recorded session at or above the 400k ceiling (or a durable,
        # unconsumed context-shedding rotation) is shed to a fresh session at the
        # safe seam. This closes the exact gap the reproduced cycle-2 start fell
        # through: the ordinary IDLE->PREFLIGHT->first-cycle path never consulted the
        # ceiling, so the over-ceiling session was continued and died. The FORWARD_
        # PROMPT branch above already rotated when it resumed an approved forward, so
        # this is a no-op there.
        self._rotate_over_ceiling_before_first_dispatch(cycle=start_index)
        for index in range(start_index, self.config.max_cycles + 1):
            # M0-T079: the budget gate, at the seam BEFORE a unit is dispatched.
            # Nothing is in flight here, so exhaustion is a clean deterministic
            # stop rather than an interrupted unit (S11.2).
            exhausted = self._budget_stop()
            if exhausted:
                stopped = exhausted
                break
            result = self.run_cycle(prompt, cycle=index)
            cycles.append(result)
            self._persist_breaker_tallies()
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
                # M0-T079: a seam RELAUNCH is a restart - the outgoing session is
                # archived and a brand-new one is started. That is the production
                # event `restart_attempts` counts, and this is the single place
                # every relaunch shape (rotation, chain switch, return-to-pin)
                # passes through, so it is ticked exactly once each.
                if seam.relaunched:
                    tripped, message = self._breaker("restart_attempts")
                    self._persist_breaker_tallies()
                    if tripped:
                        stopped = "circuit_breaker_hard_threshold"
                        self.touches.record(
                            TOUCH_SYNCHRONOUS_STOP,
                            reason_code="circuit_breaker_hard_threshold",
                            reason=message, cycle=index + 1,
                            basis="S13.8 hard threshold (restart_attempts): a run that "
                                  "keeps restarting sessions is not making progress")
                        break
                # M0-T080: a REORIENTATION successor is a session that knows
                # nothing, so the next unit receives the FULL persisted handoff
                # ahead of the forwarded prompt. A real `--resume` successor
                # already has the context and gets the forwarded prompt unchanged.
                prompt = lt.with_reorientation(seam, prompt)
                # Relaunched: the next cycle dispatches the forwarded prompt - on
                # the pinned model, or on the substitute model while an
                # orchestrator-role substitution is active - either resuming the
                # recorded provider session or in an explicitly re-oriented one.
        else:
            stopped = "max_cycles_reached"
        if self.run_budget is not None and stopped != "budget_exhausted":
            # Close the durable record with how the run actually ended, so a later
            # start reads a truthful exit reason rather than an open record.
            self.run_budget.finalize(exit_reason=stopped or "cycles_completed")
        return LoopRun(
            run_id=self.run_id, mode=self.mode, cycles=tuple(cycles),
            final_state=self.machine.current_state, stopped=stopped,
            budget=self.touches.report(),
            forwarded_message_ids=tuple(self._forwarded),
            provider_calls=self.provider_calls,
            rotations=tuple(self._rotations),
            run_budget=(self.run_budget.report() if self.run_budget is not None else None))
