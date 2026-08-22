#!/usr/bin/env python3
"""Session rotation: pre-dispatch decision, finish-the-unit, safe handoff (D-007 S11.1-S11.3).

Three separable pieces, deliberately kept apart because they have different
safety properties:

* **S11.1 pre-dispatch decision** (`decide_pre_dispatch`) - evaluated ONLY at a
  safe checkpoint, BEFORE the next bounded unit is dispatched. It classifies the
  next unit `SMALL / MEDIUM / LARGE / UNKNOWN` from objective features and
  combines the signals conservatively. It never predicts token counts; the
  thresholds are owner policy, not capacity claims.
* **S11.2 finish-the-current-unit invariant** (`observe_mid_unit`) - once a unit
  is dispatched, context or cumulative-usage pressure alone may NEVER interrupt
  it. This function's return type has no "terminate" outcome at all for pressure
  signals: the only thing it can do is persist `rotation_pending` and report
  `ROTATION_PENDING`. The narrow list of things that may interrupt a dispatched
  unit lives in `INTERRUPT_PERMITTED_REASONS` and is checked by
  `may_interrupt_in_flight`.
* **S11.3 safe rotation protocol** (`assert_safe_to_rotate`, `Handoff`,
  `verify_handoff`, `RotationLedger`) - the unsafe-moment refusal list, the
  structured handoff schema, review_model-only verification, durable storage
  with a digest, and a mandatory `READY` checkpoint.

Two things this module refuses by construction:

* it never emits or automates an interactive `/clear` (S11.3: a new explicitly
  identified session is the required behaviour), and
* it never accepts `advisory_model` for handoff verification (S3.3).

TWO IDENTITIES, NEVER CONFLATED (M0-T080). A completed rotation carries two
different things and they are named differently everywhere:

* the **provider session identity** - the id the Claude CLI itself reports on
  its stream and the only id `--resume` accepts. The supervisor cannot mint one.
* the **rotation record key** - a supervisor-internal bookkeeping id
  (`new_rotation_record_key`, `sup-rot-<uuid4>`) that names one row in this
  ledger. It is NOT a session identity of any kind and must never be written to
  a field, argv, prompt, or record where a provider session id belongs.

The pre-M0-T080 tree minted `sup-<uuid4>` from a function called
`new_session_id` and the loop stored it as "the new session id", which is
exactly the confusion this split removes.
"""
from __future__ import annotations

import dataclasses
import uuid
from typing import Any, Mapping, Sequence

from .models import digest_of, to_utc_iso
from .policy import ASK, NOTIFY
# The S11.3 handoff SCHEMA lives in `handoff.py` (M0-T080 split) and is
# re-exported here so every existing `rotation.<name>` import keeps working
# unchanged (`docs/CODE_MODULARITY_POLICY.md` §6, facade-preserving split).
from .handoff import (  # noqa: F401 - re-exported facade
    HANDOFF_FIELDS,
    HANDOFF_MAY_BE_EMPTY,
    HANDOFF_VERIFICATION_PURPOSE,
    Handoff,
    HandoffVerification,
    RotationError,
    assert_no_clear_automation,
    assert_review_model_used,
    export_handoff_payload,
    validate_handoff,
    verify_handoff,
)


# --------------------------------------------------------------------------
# Job size classification (S11.1)
# --------------------------------------------------------------------------

SMALL = "SMALL"
MEDIUM = "MEDIUM"
LARGE = "LARGE"
UNKNOWN = "UNKNOWN"

JOB_SIZES: tuple[str, ...] = (SMALL, MEDIUM, LARGE, UNKNOWN)

#: Strictness ordering for job size. Combining evidence takes the MAX, so an
#: unknown feature can only ever make the estimate more conservative.
JOB_SIZE_ORDER: dict[str, int] = {SMALL: 0, MEDIUM: 1, LARGE: 2, UNKNOWN: 3}


@dataclasses.dataclass(frozen=True)
class RotationThresholds:
    """Owner-policy thresholds. Configurable; NOT capacity claims (S11.1).

    The three defaults are the values D-007 S11.1 suggests. They are policy
    numbers the owner may change in the immutable controller config; nothing in
    this module treats them as facts about any model's real context window.
    """

    preflight_large_job_rotation: int = 400_000
    preflight_mandatory_rotation: int = 500_000
    max_checkpoints_per_session: int = 8
    #: Fraction of a Claude-reported context window above which pressure counts
    #: as HIGH. Reported context pressure is a provider signal, not a guess.
    context_pressure_high: float = 0.75
    context_pressure_elevated: float = 0.55
    #: Consecutive instruction-adherence failures that force a rotation.
    max_adherence_failures: int = 2
    #: A checkpoint or evidence packet larger than this is itself a signal.
    oversized_checkpoint_bytes: int = 262_144
    #: D-004-R743..R745: cumulative context-token usage (read off the stream) at
    #: or above which the assembled loop rotates the session before dispatching
    #: the next unit - the same code path as a detected model downgrade. Like the
    #: bounds above this is an owner-policy number, not a capacity claim. It is a
    #: SEAM decision (finish-current-unit invariant, S11.2): the flag is set while
    #: a unit is in flight but only ACTED ON before the next dispatch.
    context_rotation_threshold: int = 400_000

    @classmethod
    def from_controller_config(cls, config: Any) -> "RotationThresholds":
        """Read `[rotation]` out of the immutable controller config, failing closed."""
        raw = getattr(config, "raw", {}) or {}
        section = raw.get("rotation", {}) or {}
        if not isinstance(section, Mapping):
            raise RotationError("bad_section", "[rotation] must be a table")
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(section) - known)
        if unknown:
            raise RotationError("unknown_rotation_key",
                               f"unrecognized [rotation] keys: {unknown}")
        values: dict[str, Any] = {}
        for name, value in section.items():
            if name.startswith("context_pressure_"):
                if not isinstance(value, (int, float)) or not 0 < float(value) < 1:
                    raise RotationError(
                        "bad_threshold",
                        f"{name} must be a fraction strictly between 0 and 1")
                values[name] = float(value)
                continue
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise RotationError("bad_threshold",
                                    f"{name} must be a positive integer, got {value!r}")
            values[name] = value
        thresholds = cls(**values)
        if thresholds.preflight_mandatory_rotation < thresholds.preflight_large_job_rotation:
            raise RotationError(
                "threshold_order",
                "preflight_mandatory_rotation must be >= preflight_large_job_rotation; "
                "otherwise the mandatory bound could never be reached first")
        return thresholds


@dataclasses.dataclass(frozen=True)
class NextUnitFeatures:
    """OBJECTIVE features of the next bounded unit (S11.1).

    Every field is something the supervisor can count from the task packet and
    the evidence it already holds. None of it is a model's opinion, and none of
    it pretends to predict tokens.

    `usage_known=False` is the honest representation of "we could not read
    cumulative usage" - it is never encoded as zero (S8.3).
    """

    file_count: int = 0
    total_target_bytes: int = 0
    documented_test_commands: int = 0
    requires_full_repo_scan: bool = False
    requires_external_research: bool = False
    subunits: int = 1
    packet_bytes: int = 0
    declared_size: str = ""

    def __post_init__(self) -> None:
        if self.declared_size and self.declared_size not in JOB_SIZES:
            raise RotationError("bad_declared_size",
                                f"{self.declared_size!r} is not one of {list(JOB_SIZES)}")
        for name in ("file_count", "total_target_bytes", "documented_test_commands",
                     "subunits", "packet_bytes"):
            if getattr(self, name) < 0:
                raise RotationError("negative_feature", f"{name} may not be negative")


@dataclasses.dataclass(frozen=True)
class SizeClassification:
    job_size: str
    reason_code: str
    reason: str
    features_used: tuple[str, ...] = ()


def classify_next_unit(
    features: NextUnitFeatures,
    thresholds: RotationThresholds | None = None,
) -> SizeClassification:
    """Classify the next unit SMALL/MEDIUM/LARGE/UNKNOWN from objective features.

    The classification is a deterministic MAX over per-feature verdicts, so any
    single "this looks large" feature dominates and an unrecognizable shape lands
    in UNKNOWN rather than being optimistically called SMALL.
    """
    thresholds = thresholds or RotationThresholds()
    verdicts: list[tuple[str, str]] = []

    if features.declared_size:
        verdicts.append((features.declared_size, "declared_size"))

    if features.requires_full_repo_scan:
        verdicts.append((UNKNOWN, "requires_full_repo_scan"))
    if features.requires_external_research:
        verdicts.append((UNKNOWN, "requires_external_research"))

    if features.file_count == 0 and features.total_target_bytes == 0 \
            and not features.declared_size:
        verdicts.append((UNKNOWN, "no_objective_features"))
    else:
        if features.file_count > 12:
            verdicts.append((LARGE, "file_count"))
        elif features.file_count > 4:
            verdicts.append((MEDIUM, "file_count"))
        elif features.file_count > 0:
            verdicts.append((SMALL, "file_count"))

        if features.total_target_bytes > 300_000:
            verdicts.append((LARGE, "total_target_bytes"))
        elif features.total_target_bytes > 60_000:
            verdicts.append((MEDIUM, "total_target_bytes"))
        elif features.total_target_bytes > 0:
            verdicts.append((SMALL, "total_target_bytes"))

    if features.subunits > 4:
        verdicts.append((LARGE, "subunits"))
    elif features.subunits > 1:
        verdicts.append((MEDIUM, "subunits"))

    if features.documented_test_commands > 3:
        verdicts.append((MEDIUM, "documented_test_commands"))

    if features.packet_bytes > thresholds.oversized_checkpoint_bytes:
        verdicts.append((LARGE, "packet_bytes"))

    if not verdicts:
        return SizeClassification(UNKNOWN, "no_signals",
                                  "no objective feature was available; UNKNOWN is the "
                                  "conservative classification, never SMALL")

    job_size = max((v for v, _ in verdicts), key=lambda size: JOB_SIZE_ORDER[size])
    used = tuple(sorted({name for size, name in verdicts if size == job_size}))
    return SizeClassification(
        job_size, "objective_features",
        f"classified {job_size} from {list(used)} (max over per-feature verdicts)", used)


# --------------------------------------------------------------------------
# Pre-dispatch rotation decision (S11.1)
# --------------------------------------------------------------------------

#: Every signal S11.1 enumerates. A signal absent from this tuple cannot cause a
#: rotation: the decision surface is closed.
ROTATION_SIGNALS: tuple[str, ...] = (
    "cumulative_usage",
    "context_pressure",
    "compaction_event",
    "checkpoint_count",
    "instruction_adherence_loss",
    "oversized_checkpoint_or_packet",
    "owner_request",
)


@dataclasses.dataclass(frozen=True)
class SessionSignals:
    """The live rotation signals for the CURRENT session (S11.1).

    `usage_known=False` means the cumulative reading is unavailable. S11.1 then
    requires combining context-pressure and checkpoint evidence and choosing the
    CONSERVATIVE pre-dispatch action - never treating "unknown" as "low".
    """

    cumulative_usage: int = 0
    usage_known: bool = True
    context_pressure_ratio: float = 0.0
    context_pressure_known: bool = True
    compaction_events: int = 0
    completed_checkpoints: int = 0
    consecutive_adherence_failures: int = 0
    largest_checkpoint_bytes: int = 0
    owner_requested_rotation: bool = False

    def __post_init__(self) -> None:
        if self.usage_known and self.cumulative_usage < 0:
            raise RotationError("negative_usage", "cumulative usage may not be negative")
        if self.context_pressure_known and not 0.0 <= self.context_pressure_ratio <= 1.0:
            raise RotationError("bad_pressure",
                                "context_pressure_ratio must be between 0 and 1")


@dataclasses.dataclass(frozen=True)
class RotationDecision:
    """The pre-dispatch verdict. `rotate=True` means rotate BEFORE dispatching."""

    rotate: bool
    job_size: str
    reason_code: str
    reason: str
    tier: str = NOTIFY
    triggered_signals: tuple[str, ...] = ()
    conservative_for_unknown: bool = False
    thresholds_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def decide_pre_dispatch(
    signals: SessionSignals,
    features: NextUnitFeatures,
    *,
    thresholds: RotationThresholds | None = None,
    at_safe_checkpoint: bool = False,
) -> RotationDecision:
    """The S11.1 decision. Callable ONLY at a safe checkpoint, before dispatch.

    Refusing to run mid-unit is not a convenience check: S11.2 forbids acting on
    a threshold while a unit is in flight, so the function that produces "rotate
    now" must be unreachable from that context.
    """
    if not at_safe_checkpoint:
        raise RotationError(
            "not_at_safe_checkpoint",
            "the rotation decision is evaluated ONLY at a safe checkpoint before "
            "dispatching the next unit (S11.1); mid-unit pressure sets rotation_pending "
            "through observe_mid_unit() instead and never interrupts the unit (S11.2)")

    thresholds = thresholds or RotationThresholds()
    classification = classify_next_unit(features, thresholds)
    job_size = classification.job_size
    triggered: list[str] = []
    conservative = False

    # 1. Owner request always wins and needs no other evidence.
    if signals.owner_requested_rotation:
        return RotationDecision(
            True, job_size, "owner_request",
            "the owner asked for a rotation before the next unit", NOTIFY,
            ("owner_request",), False, digest_of(dataclasses.asdict(thresholds)))

    # 2. Mandatory bound: rotate before ANY unit.
    if signals.usage_known and \
            signals.cumulative_usage >= thresholds.preflight_mandatory_rotation:
        return RotationDecision(
            True, job_size, "mandatory_threshold",
            f"cumulative usage {signals.cumulative_usage} reached the mandatory bound "
            f"{thresholds.preflight_mandatory_rotation}: rotate before any unit",
            NOTIFY, ("cumulative_usage",), False,
            digest_of(dataclasses.asdict(thresholds)))

    # 3. Large-job bound: rotate before a LARGE or UNKNOWN unit.
    at_large_bound = (signals.usage_known
                      and signals.cumulative_usage >= thresholds.preflight_large_job_rotation)
    if at_large_bound:
        triggered.append("cumulative_usage")

    # 4. Unknown usage: combine context pressure and checkpoint evidence and take
    #    the conservative action (S11.1's explicit instruction).
    if not signals.usage_known:
        conservative = True
        pressure_high = (signals.context_pressure_known
                         and signals.context_pressure_ratio >= thresholds.context_pressure_high)
        pressure_elevated = (
            signals.context_pressure_known
            and signals.context_pressure_ratio >= thresholds.context_pressure_elevated)
        if not signals.context_pressure_known:
            # Neither usage nor pressure is readable. There is no evidence of
            # safety at all, so the conservative action is to treat the next unit
            # as UNKNOWN *and* engage the large-job bound, which makes the
            # LARGE/UNKNOWN rule below rotate. Caught by
            # test_unknown_usage_and_unknown_pressure_treats_the_unit_as_unknown:
            # setting the size alone left the bound unengaged and the decision
            # fell through to "no rotation required" on no evidence whatsoever.
            job_size = UNKNOWN
            triggered.append("context_pressure")
            at_large_bound = True
        if pressure_high or signals.compaction_events > 0:
            triggered.append("context_pressure" if pressure_high else "compaction_event")
            return RotationDecision(
                True, job_size, "unknown_usage_conservative",
                "cumulative usage is unavailable and the context/compaction evidence shows "
                "pressure; S11.1 requires the conservative pre-dispatch action",
                NOTIFY, tuple(sorted(set(triggered))), True,
                digest_of(dataclasses.asdict(thresholds)))
        if pressure_elevated:
            triggered.append("context_pressure")
            at_large_bound = True

    if signals.compaction_events > 0 and "compaction_event" not in triggered:
        triggered.append("compaction_event")
        at_large_bound = True

    # 5. Checkpoint count per session.
    if signals.completed_checkpoints >= thresholds.max_checkpoints_per_session:
        triggered.append("checkpoint_count")
        return RotationDecision(
            True, job_size, "checkpoint_count",
            f"{signals.completed_checkpoints} completed checkpoints reached the configured "
            f"per-session maximum {thresholds.max_checkpoints_per_session}",
            NOTIFY, tuple(sorted(set(triggered))), conservative,
            digest_of(dataclasses.asdict(thresholds)))

    # 6. Repeated loss of instruction adherence.
    if signals.consecutive_adherence_failures >= thresholds.max_adherence_failures:
        triggered.append("instruction_adherence_loss")
        return RotationDecision(
            True, job_size, "instruction_adherence_loss",
            f"{signals.consecutive_adherence_failures} consecutive instruction-adherence "
            f"failures; a fresh session is the remedy, not a louder prompt",
            NOTIFY, tuple(sorted(set(triggered))), conservative,
            digest_of(dataclasses.asdict(thresholds)))

    # 7. Oversized checkpoint or packet.
    if signals.largest_checkpoint_bytes > thresholds.oversized_checkpoint_bytes:
        triggered.append("oversized_checkpoint_or_packet")
        return RotationDecision(
            True, job_size, "oversized_checkpoint",
            f"a checkpoint/packet of {signals.largest_checkpoint_bytes} bytes exceeded the "
            f"{thresholds.oversized_checkpoint_bytes}-byte signal bound",
            NOTIFY, tuple(sorted(set(triggered))), conservative,
            digest_of(dataclasses.asdict(thresholds)))

    # 8. The large-job bound only rotates ahead of a LARGE or UNKNOWN unit.
    if at_large_bound and job_size in (LARGE, UNKNOWN):
        return RotationDecision(
            True, job_size, "large_job_threshold",
            f"at the large-job bound with a {job_size} next unit: rotate before dispatching "
            f"it ({classification.reason})",
            NOTIFY, tuple(sorted(set(triggered))), conservative,
            digest_of(dataclasses.asdict(thresholds)))

    return RotationDecision(
        False, job_size, "no_rotation_required",
        f"no threshold requires rotation before a {job_size} unit "
        f"({classification.reason})",
        NOTIFY, tuple(sorted(set(triggered))), conservative,
        digest_of(dataclasses.asdict(thresholds)))


# --------------------------------------------------------------------------
# Finish-the-current-unit invariant (S11.2)
# --------------------------------------------------------------------------

ROTATION_PENDING_KEY = "rotation_pending"
JOB_SIZE_KEY = "job_size_class"
#: D-004: why rotation_pending was set (model_downgrade | context_threshold |
#: owner_request | ...). Persisted alongside the flag so the seam knows what to
#: report and audit, and cleared with the flag by complete_rotation.
ROTATION_REASON_KEY = "rotation_pending_reason"

#: The ONLY reasons a dispatched unit may be interrupted (S11.2). Context or
#: cumulative-usage pressure is deliberately absent and can never be added by
#: configuration - this tuple is the whole list.
INTERRUPT_PERMITTED_REASONS: tuple[str, ...] = (
    "owner_emergency_stop",
    "hard_safety_or_policy_violation",
    "os_resource_circuit_breaker",
    "hardware_or_process_failure",
    "provider_enforced_abort",
)

#: Pressure reasons, named so a caller passing one to `may_interrupt_in_flight`
#: gets an explicit refusal rather than a silent False.
PRESSURE_REASONS: tuple[str, ...] = (
    "context_pressure", "cumulative_usage", "rotation_threshold", "checkpoint_count",
    "compaction_event", "token_budget",
)


def may_interrupt_in_flight(reason: str) -> bool:
    """True only for the five S11.2 exceptions. Pressure reasons raise."""
    if reason in PRESSURE_REASONS:
        raise RotationError(
            "pressure_may_not_interrupt",
            f"{reason!r} is a context/usage pressure signal; S11.2 forbids cancelling, "
            f"Ctrl+C-ing, SIGTERMing, or taskkilling a dispatched unit merely because a "
            f"threshold was crossed. Persist rotation_pending and let the unit finish")
    return reason in INTERRUPT_PERMITTED_REASONS


@dataclasses.dataclass(frozen=True)
class MidUnitOutcome:
    """What the supervisor does about a threshold crossed MID-UNIT.

    There is no `terminate` field. That is the point: this type cannot express
    "kill the unit", so no caller can accidentally do it for pressure.
    """

    rotation_pending: bool
    reason_code: str
    reason: str
    unit_continues: bool = True


def observe_mid_unit(
    journal: Any,
    *,
    reason_code: str,
    detail: str = "",
) -> MidUnitOutcome:
    """Record that a rotation threshold was crossed while a unit is in flight.

    Persists `rotation_pending = true` durably (so a crash does not lose it) and
    returns an outcome whose `unit_continues` is unconditionally True.
    """
    if reason_code in INTERRUPT_PERMITTED_REASONS:
        raise RotationError(
            "not_a_pressure_signal",
            f"{reason_code!r} is an S11.2 interrupt reason, not a rotation signal; route it "
            f"through the emergency-stop / circuit-breaker path, not rotation")
    journal.set_state(ROTATION_PENDING_KEY, True)
    return MidUnitOutcome(
        True, reason_code,
        f"rotation_pending persisted for {reason_code!r}"
        + (f": {detail}" if detail else "")
        + ". The in-flight unit is NOT terminated; it runs to a valid terminal "
          "checkpoint and rotation happens before the next dispatch (S11.2)")


def rotation_pending(journal: Any) -> bool:
    return bool(journal.get_state(ROTATION_PENDING_KEY, False))


def clear_rotation_pending(journal: Any) -> None:
    journal.set_state(ROTATION_PENDING_KEY, False)


@dataclasses.dataclass(frozen=True)
class UnitBounds:
    """A unit's safety bounds, FIXED before dispatch (S11.2).

    "may not be extended in flight to dodge rotation" is enforced by
    `assert_bounds_unchanged`, which refuses any increase - and refuses a changed
    bound set entirely, because silently adding a bound is also a change.
    """

    max_turns: int
    wall_seconds: float
    max_processes: int
    max_output_bytes: int

    def digest(self) -> str:
        return digest_of(dataclasses.asdict(self))


def assert_bounds_unchanged(original: UnitBounds, candidate: UnitBounds) -> None:
    """Refuse any in-flight change to a dispatched unit's bounds."""
    if original == candidate:
        return
    widened = [
        name for name in ("max_turns", "wall_seconds", "max_processes", "max_output_bytes")
        if getattr(candidate, name) > getattr(original, name)
    ]
    if widened:
        raise RotationError(
            "bounds_extended_in_flight",
            f"a dispatched unit's bounds may not be extended in flight to dodge rotation "
            f"(S11.2); {widened} were increased")
    raise RotationError(
        "bounds_changed_in_flight",
        "a dispatched unit's max turns, wall time, process count, and safety bounds are "
        "fixed before dispatch and may not change while it runs (S11.2)")


PROVIDER_ABORT_KEY = "provider_abort_record"


def record_provider_abort(journal: Any, *, unit_id: str, detail: str) -> dict[str, Any]:
    """A provider-enforced abort is recorded INCOMPLETE, never reported complete (S11.2)."""
    record = {
        "unit_id": unit_id,
        "outcome": "INCOMPLETE",
        "reason_code": "provider_enforced_abort",
        "detail": detail,
        "recorded_at_utc": to_utc_iso(),
        "requires_recovery": True,
    }
    journal.set_state(PROVIDER_ABORT_KEY, record)
    return record


# --------------------------------------------------------------------------
# Safe rotation protocol (S11.3)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class RotationSafetyState:
    """Everything S11.3 says must be quiet and unambiguous before rotating."""

    command_running: bool = False
    tool_call_pending: bool = False
    approval_pending: bool = False
    unaccounted_background_actions: int = 0
    unexplained_uncommitted_changes: bool = False
    merge_or_rebase_in_progress: bool = False
    conflict_present: bool = False
    sha_ambiguous: bool = False
    worktree_ambiguous: bool = False
    task_stage_ambiguous: bool = False


#: The unsafe-moment refusal list, in the order S11.3 states it.
UNSAFE_MOMENT_CHECKS: tuple[tuple[str, str], ...] = (
    ("command_running", "a command is still running"),
    ("tool_call_pending", "a tool call is still outstanding"),
    ("approval_pending", "an approval is still outstanding"),
    ("unaccounted_background_actions", "background actions are unaccounted for"),
    ("unexplained_uncommitted_changes", "uncommitted changes are unexplained"),
    ("merge_or_rebase_in_progress", "a merge or rebase is in progress"),
    ("conflict_present", "an unresolved conflict is present"),
    ("sha_ambiguous", "the authoritative SHA is ambiguous"),
    ("worktree_ambiguous", "the worktree identity is ambiguous"),
    ("task_stage_ambiguous", "the task stage is ambiguous"),
)


def unsafe_rotation_reasons(state: RotationSafetyState) -> tuple[str, ...]:
    """Every reason the current moment is unsafe for rotation (possibly none)."""
    reasons: list[str] = []
    for field_name, description in UNSAFE_MOMENT_CHECKS:
        value = getattr(state, field_name)
        if isinstance(value, bool):
            if value:
                reasons.append(description)
        elif value:
            reasons.append(f"{description} ({value})")
    return tuple(reasons)


def assert_safe_to_rotate(state: RotationSafetyState) -> None:
    """Refuse to close or replace a session at an unsafe moment (S11.3)."""
    reasons = unsafe_rotation_reasons(state)
    if reasons:
        raise RotationError(
            "unsafe_rotation_point",
            "refusing to close or replace the session: " + "; ".join(reasons)
            + ". S11.3 permits rotation only at a quiet, unambiguous checkpoint")


# --------------------------------------------------------------------------
# The rotation ledger (durable storage, new session, READY gate)
# --------------------------------------------------------------------------

HANDOFF_KEY = "verified_handoff"
SESSION_ARCHIVE_KEY = "archived_sessions"


def new_rotation_record_key(previous: str = "") -> str:
    """A fresh SUPERVISOR-INTERNAL key naming one row in the rotation ledger.

    This is bookkeeping, NOT an identity any provider knows. The supervisor
    cannot mint a provider session id - only the Claude CLI can, and it reports
    it on its stream (`claude_runner.RunResult.session_id`). The `sup-rot-`
    prefix and this function's name exist so the value can never be mistaken for
    one: it is never passed to `--resume`, never written to
    `RunnerConfig.resume_session_id`, and never stored in a
    `provider_session_id` field.

    Until M0-T080 this function was called `new_session_id`, returned
    `sup-<uuid4>`, and the loop stored its result where the new session's
    identity belonged - so a "completed rotation" recorded an id no provider had
    ever issued while the successor actually launched unresumed.
    """
    candidate = f"sup-rot-{uuid.uuid4().hex}"
    if previous and candidate == previous:  # pragma: no cover - uuid4 collision
        return new_rotation_record_key(previous)
    return candidate


class RotationLedger:
    """Durable rotation bookkeeping: store, archive, gate on READY."""

    def __init__(self, journal: Any, *, audit: Any = None) -> None:
        self.journal = journal
        self.audit = audit

    def store_verified_handoff(self, handoff: Handoff,
                               verification: HandoffVerification) -> dict[str, Any]:
        """Durably store the VERIFIED handoff and its digest (S11.3)."""
        if not verification.verified:
            raise RotationError("unverified_handoff",
                                "only a verified handoff is stored and carried into a new "
                                "session")
        record = {
            "handoff": handoff.to_dict(),
            "handoff_digest": handoff.digest(),
            "verified_by_model": verification.model_used,
            "verified_at_utc": to_utc_iso(),
        }
        self.journal.set_state(HANDOFF_KEY, record)
        self._audit("rotation_handoff_stored", {"handoff_digest": record["handoff_digest"],
                                                "model": verification.model_used})
        return record

    def stored_handoff(self) -> dict[str, Any] | None:
        data = self.journal.get_state(HANDOFF_KEY)
        return data if isinstance(data, dict) else None

    def archive_session(self, session_id: str, *, reason: str) -> tuple[str, ...]:
        """Archive the old session reference (S11.3). Never resumed afterwards."""
        archived = list(self.journal.get_state(SESSION_ARCHIVE_KEY, []) or [])
        if session_id and session_id not in archived:
            archived.append(session_id)
        self.journal.set_state(SESSION_ARCHIVE_KEY, archived)
        self._audit("rotation_session_archived",
                    {"archived_count": len(archived), "reason": reason})
        return tuple(archived)

    def archived_sessions(self) -> tuple[str, ...]:
        return tuple(self.journal.get_state(SESSION_ARCHIVE_KEY, []) or [])

    def assert_not_archived(self, session_id: str) -> None:
        """Refuse to resume an archived session (S15 'no accidental old-session resume')."""
        if session_id in self.archived_sessions():
            raise RotationError(
                "archived_session_resume",
                f"session {session_id!r} was archived by a rotation and may never be resumed; "
                f"a rotation always continues in a brand-new session id (S11.3)")

    # THE S11.3 READY GATE LIVES IN `turnover_seam.SeamTurnover.require_ready`.
    #
    # `RotationLedger.assert_ready_checkpoint` used to sit here and was REMOVED by
    # the M0-T080 correction (U4). It had zero production callers, its docstring
    # falsely named `turnover_seam.SeamTurnover` as one, and it disagreed with the
    # live gate: it demanded `claude_session_id == expected_session_id`, which is
    # unsatisfiable on a reorientation because the successor's provider session id
    # does not exist until the successor reports it. Two gates that disagree are
    # worse than one, so the dead one is gone rather than kept as a decoy.

    def complete_rotation(self, *, previous_provider_session_id: str,
                          rotation_record_key: str,
                          handoff_digest: str,
                          continuity_mode: str,
                          provider_session_id: str = "",
                          provider_session_none_reason: str = "") -> dict[str, Any]:
        """Record the rotation with BOTH identities, and archive when appropriate.

        `continuity_mode` (`session_continuity.RESUME` / `REORIENTATION`) decides
        what actually happened to the session:

        * **reorientation** - the outgoing provider session is ARCHIVED (S11.3:
          never resumed afterwards) and `provider_session_id` is EMPTY, because
          the successor's own id does not exist until it reports one. The record
          must then name why resume was impossible, so a reader can never read
          the blank as "it resumed and we lost the id".
        * **resume** - the successor continues the SAME provider session, so that
          session is deliberately NOT archived (archiving it would make the very
          resume being recorded illegal), and `provider_session_id` names it.

        `rotation_record_key` is supervisor-internal bookkeeping and is required
        to differ from the outgoing provider session id, so the two identities
        can never be silently the same value.
        """
        if continuity_mode not in ("resume", "reorientation"):
            raise RotationError(
                "unknown_continuity_mode",
                f"{continuity_mode!r} is not a continuity mode; a completed rotation states "
                f"whether the successor really resumed the provider session or was "
                f"explicitly re-oriented into a new one")
        if not rotation_record_key:
            raise RotationError("no_rotation_record_key",
                                "a completed rotation needs its supervisor-internal record key")
        if rotation_record_key == previous_provider_session_id:
            raise RotationError(
                "identity_conflated",
                "the supervisor-internal rotation record key equals the outgoing PROVIDER "
                "session id; the two identities are different kinds of thing and may never "
                "hold the same value")
        if continuity_mode == "resume":
            if not provider_session_id:
                raise RotationError(
                    "resume_without_provider_session",
                    "a rotation recorded as a resume must name the exact provider session "
                    "id the successor launch resumes; a resume with no id is a fresh "
                    "unresumed session wearing a resume label")
            self.assert_not_archived(provider_session_id)
        else:
            if not provider_session_none_reason:
                raise RotationError(
                    "reorientation_without_reason",
                    "a rotation recorded as a reorientation must name why resume was "
                    "impossible; an unexplained blank session id is indistinguishable from "
                    "a lost one")
            if provider_session_id:
                raise RotationError(
                    "reorientation_with_provider_session",
                    "a reorientation starts a session the provider has not identified yet, "
                    "so it may not claim a provider session id in advance")
            self.archive_session(previous_provider_session_id,
                                 reason="rotation_complete")
        clear_rotation_pending(self.journal)
        record = {
            "previous_provider_session_id": previous_provider_session_id,
            "rotation_record_key": rotation_record_key,
            "continuity_mode": continuity_mode,
            "provider_session_id": provider_session_id,
            "provider_session_none_reason": provider_session_none_reason,
            "handoff_digest": handoff_digest,
            "completed_at_utc": to_utc_iso(),
            "tier": NOTIFY,
            "note": "a completed rotation is a NOTIFY event (S11.3). rotation_record_key is "
                    "SUPERVISOR-INTERNAL bookkeeping and is never a provider session id",
        }
        self.journal.set_state("last_rotation", record)
        self._audit("rotation_complete", record)
        return record

    def _audit(self, event: str, detail: Mapping[str, Any]) -> None:
        if self.audit is not None:
            self.audit.append(event, detail=dict(detail))


def rotation_tier(decision: RotationDecision) -> str:
    """A completed rotation is NOTIFY; a rotation that cannot proceed is ASK."""
    return NOTIFY if decision.rotate else ASK if decision.reason_code == "blocked" else NOTIFY

