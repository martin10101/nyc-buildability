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
  with a digest, a brand-new session id, and a mandatory `READY` checkpoint.

Two things this module refuses by construction:

* it never emits or automates an interactive `/clear` (S11.3: a new explicitly
  identified session is the required behaviour), and
* it never accepts `advisory_model` for handoff verification (S3.3).
"""
from __future__ import annotations

import dataclasses
import re
import uuid
from typing import Any, Mapping, Sequence

from .models import digest_of, to_utc_iso
from .policy import ASK, NOTIFY, assert_advisory_allowed

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


class RotationError(Exception):
    """A rotation rule was violated. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


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


#: The S11.3 handoff schema, verbatim in order. Every field is REQUIRED; an
#: empty required field is an invalid handoff, not a tolerable omission.
HANDOFF_FIELDS: tuple[str, ...] = (
    "task_and_stage",
    "authoritative_shas",
    "branch",
    "worktree",
    "completed_work",
    "changed_files",
    "tests_and_ci",
    "pull_request_state",
    "reviews_and_findings",
    "open_blockers",
    "owner_gates",
    "forbidden_scope",
    "exact_next_action",
    "evidence_digests",
)

#: Fields that may legitimately be an empty COLLECTION (there may genuinely be no
#: blockers). They must still be present, and must still be the right type.
HANDOFF_MAY_BE_EMPTY: frozenset[str] = frozenset({
    "changed_files", "open_blockers", "reviews_and_findings", "owner_gates",
    "evidence_digests", "tests_and_ci",
})

#: S11.3: "Do not automate an interactive `/clear`."
_CLEAR_AUTOMATION = re.compile(r"(?<![\w/])/clear\b", re.IGNORECASE)


def assert_no_clear_automation(text: str, *, where: str) -> None:
    """Refuse any handoff or next-action text that automates `/clear` (S11.3)."""
    if _CLEAR_AUTOMATION.search(text or ""):
        raise RotationError(
            "clear_automation_forbidden",
            f"{where} tries to automate an interactive `/clear`; S11.3 requires a brand-new "
            f"explicitly identified session instead")


@dataclasses.dataclass(frozen=True)
class Handoff:
    """The structured handoff (S11.3 schema). Untrusted content, strict shape."""

    task_and_stage: str
    authoritative_shas: dict[str, str]
    branch: str
    worktree: str
    completed_work: str
    changed_files: tuple[str, ...]
    tests_and_ci: dict[str, Any]
    pull_request_state: str
    reviews_and_findings: tuple[str, ...]
    open_blockers: tuple[str, ...]
    owner_gates: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    exact_next_action: str
    evidence_digests: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, tuple):
                data[key] = list(value)
        return data

    def digest(self) -> str:
        return digest_of(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Handoff":
        if not isinstance(data, Mapping):
            raise RotationError("not_a_mapping", "a handoff must be a mapping")
        unknown = sorted(set(data) - set(HANDOFF_FIELDS))
        if unknown:
            raise RotationError("unknown_handoff_fields",
                                f"handoff carries unknown fields: {unknown}")
        missing = sorted(set(HANDOFF_FIELDS) - set(data))
        if missing:
            raise RotationError("incomplete_handoff",
                               f"handoff is missing required fields: {missing}")
        return cls(
            task_and_stage=str(data["task_and_stage"]),
            authoritative_shas=dict(data["authoritative_shas"] or {}),
            branch=str(data["branch"]),
            worktree=str(data["worktree"]),
            completed_work=str(data["completed_work"]),
            changed_files=tuple(data["changed_files"] or ()),
            tests_and_ci=dict(data["tests_and_ci"] or {}),
            pull_request_state=str(data["pull_request_state"]),
            reviews_and_findings=tuple(data["reviews_and_findings"] or ()),
            open_blockers=tuple(data["open_blockers"] or ()),
            owner_gates=tuple(data["owner_gates"] or ()),
            forbidden_scope=tuple(data["forbidden_scope"] or ()),
            exact_next_action=str(data["exact_next_action"]),
            evidence_digests=dict(data["evidence_digests"] or {}),
        )


def validate_handoff(handoff: Handoff) -> None:
    """Reject an incomplete or unusable handoff (S11.3, S15 'invalid handoff')."""
    for name in HANDOFF_FIELDS:
        value = getattr(handoff, name)
        if name in HANDOFF_MAY_BE_EMPTY:
            continue
        if isinstance(value, str) and not value.strip():
            raise RotationError("incomplete_handoff",
                                f"handoff field {name!r} is empty; a rotation may not proceed "
                                f"on a handoff that omits it")
        if isinstance(value, (dict, tuple)) and not value:
            raise RotationError("incomplete_handoff",
                                f"handoff field {name!r} is empty; a rotation may not proceed "
                                f"on a handoff that omits it")
    if "HEAD" not in handoff.authoritative_shas:
        raise RotationError("incomplete_handoff",
                            "authoritative_shas must name at least HEAD")
    assert_no_clear_automation(handoff.exact_next_action, where="handoff.exact_next_action")
    assert_no_clear_automation(handoff.completed_work, where="handoff.completed_work")


@dataclasses.dataclass(frozen=True)
class HandoffVerification:
    """The reviewer's verdict on a handoff, plus the model that produced it."""

    verified: bool
    model_used: str
    role: str
    reason_code: str
    reason: str
    handoff_digest: str = ""
    findings: tuple[str, ...] = ()


HANDOFF_VERIFICATION_PURPOSE = "handoff_verification"


def assert_review_model_used(*, role: str, model_used: str,
                             review_model: str, advisory_model: str = "") -> None:
    """S11.3/S3.3: handoff verification uses review_model, never advisory_model."""
    if role != "primary":
        raise RotationError(
            "advisory_model_forbidden",
            f"handoff verification ran in role {role!r}; S3.3 reserves final handoff "
            f"verification before autonomous continuation to review_model or deterministic "
            f"verification")
    if advisory_model and model_used == advisory_model and model_used != review_model:
        raise RotationError(
            "advisory_model_forbidden",
            f"handoff verification used the advisory model {model_used!r}; S3.3 forbids the "
            f"cheaper model for this purpose")
    if review_model and model_used != review_model:
        raise RotationError(
            "unexpected_verifier_model",
            f"handoff verification reported model {model_used!r} but the configured "
            f"review_model is {review_model!r}; the mismatch is never accepted silently")
    # Belt and braces: the policy engine's own refusal for this purpose.
    try:
        assert_advisory_allowed(HANDOFF_VERIFICATION_PURPOSE)
    except Exception:
        return  # Expected: the purpose is on the forbidden list. Nothing to do.
    raise RotationError(
        "advisory_purpose_not_protected",
        "handoff_verification is no longer on the advisory-forbidden list; refusing to "
        "verify a handoff under a weakened policy")


def verify_handoff(
    handoff: Handoff,
    *,
    reviewer_verdict: Mapping[str, Any],
    review_model: str,
    advisory_model: str = "",
    role: str = "primary",
) -> HandoffVerification:
    """Turn a fresh read-only reviewer's verdict into a durable verification.

    The supervisor - not the reviewer - decides what the verdict means, and the
    model identity is checked against the configured `review_model` before the
    verdict is honoured at all.
    """
    validate_handoff(handoff)
    model_used = str(reviewer_verdict.get("model_used", ""))
    assert_review_model_used(role=role, model_used=model_used,
                             review_model=review_model, advisory_model=advisory_model)

    reviewed_digest = str(reviewer_verdict.get("handoff_digest", ""))
    if reviewed_digest != handoff.digest():
        return HandoffVerification(
            False, model_used, role, "digest_mismatch",
            f"the reviewer verified a handoff whose digest ({reviewed_digest[:16]}...) is not "
            f"the one being rotated ({handoff.digest()[:16]}...)",
            handoff.digest())

    findings = tuple(str(f) for f in reviewer_verdict.get("findings", ()) or ())
    if not bool(reviewer_verdict.get("verified", False)) or findings:
        return HandoffVerification(
            False, model_used, role, "handoff_rejected",
            "the reviewer did not verify the handoff against live evidence",
            handoff.digest(), findings)
    return HandoffVerification(
        True, model_used, role, "handoff_verified",
        f"{model_used} verified the handoff against live evidence", handoff.digest())


# --------------------------------------------------------------------------
# The rotation ledger (durable storage, new session, READY gate)
# --------------------------------------------------------------------------

HANDOFF_KEY = "verified_handoff"
SESSION_ARCHIVE_KEY = "archived_sessions"


def new_session_id(previous: str = "") -> str:
    """A brand-new session id (S11.3). Never reuses or derives from the old one."""
    candidate = f"sup-{uuid.uuid4().hex}"
    if previous and candidate == previous:  # pragma: no cover - uuid4 collision
        return new_session_id(previous)
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

    def assert_ready_checkpoint(self, checkpoint: Any, *, expected_session_id: str,
                                previous_session_id: str = "") -> None:
        """The new session must return a structured READY checkpoint before any change."""
        status = getattr(checkpoint, "status", None)
        session = getattr(checkpoint, "claude_session_id", "")
        if status != "READY":
            raise RotationError(
                "ready_checkpoint_required",
                f"the re-oriented session reported status {status!r}; S11.3 requires a "
                f"structured READY checkpoint after re-orientation BEFORE any change")
        if session != expected_session_id:
            raise RotationError(
                "wrong_session_ready",
                f"the READY checkpoint came from session {session!r}, not the new session "
                f"{expected_session_id!r}")
        if previous_session_id and session == previous_session_id:
            raise RotationError(
                "session_not_rotated",
                "the 'new' session id equals the archived one; rotation requires a brand-new "
                "explicitly identified session")

    def complete_rotation(self, *, old_session_id: str, new_session_id_value: str,
                          handoff_digest: str) -> dict[str, Any]:
        """Archive, clear rotation_pending, and record the NOTIFY event (S11.3)."""
        if new_session_id_value == old_session_id:
            raise RotationError("session_not_rotated",
                                "a completed rotation must carry a brand-new session id")
        self.archive_session(old_session_id, reason="rotation_complete")
        clear_rotation_pending(self.journal)
        record = {
            "old_session_id": old_session_id,
            "new_session_id": new_session_id_value,
            "handoff_digest": handoff_digest,
            "completed_at_utc": to_utc_iso(),
            "tier": NOTIFY,
            "note": "a completed rotation is a NOTIFY event (S11.3)",
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


def export_handoff_payload(handoff: Handoff, verification: HandoffVerification,
                           *, new_session: str,
                           evidence: Sequence[str] = ()) -> dict[str, Any]:
    """The bundle a fresh session receives (S11.3): handoff, packet refs, next action."""
    validate_handoff(handoff)
    assert_no_clear_automation(handoff.exact_next_action, where="exported next action")
    return {
        "new_session_id": new_session,
        "handoff": handoff.to_dict(),
        "handoff_digest": handoff.digest(),
        "verified_by_model": verification.model_used,
        "exact_next_authorized_action": handoff.exact_next_action,
        "evidence_refs": list(evidence),
        "required_first_response": "a structured READY checkpoint; no change before it",
        "exported_at_utc": to_utc_iso(),
    }
