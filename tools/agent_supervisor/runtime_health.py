"""Invisible runtime health-band evaluation (D-024 Phase C item 4, M0-T091).

Evaluates a subagent's PRIVATE health band against live telemetry and the
controller's progress assessment (s5.4/s5.5). The measurements never appear
in the worker's instructions and never make the worker ration its reasoning
(D-024-R045); every decision this module produces is a controller record:

- **normal** — coherent progress; no action, no message;
- **observe** — Codex checks progress/remaining scope from EXTERNAL
  evidence; the worker continues uninterrupted and receives NO message;
- **prepare_to_land** — the controller prevents new scope, children, and
  unrelated investigation; still no worker message;
- **land** — ONE short course-correction through the supported messaging
  path (finish the atomic step, save/test what is coherent, return the
  bounded handoff); never a token calculation or telemetry explanation;
- **emergency_stop** — platform task-stop, reserved for an unresponsive or
  unsafe process, an imminent provider/platform hard limit, an owner
  emergency stop, or inability to reach a safe seam.

Token count is only one signal (s5.4): a model that says it is losing the
thread is an immediate quality signal even at low counters; high counters
with a nearly-complete coherent unit reach their safe seam instead of being
killed for crossing a round number; no-progress/scope-drift findings trigger
review regardless of tokens. Bands are calibrated per resolved model from
controller config — conservative warning evidence, never vendor capacity
claims and never automatic kill numbers.

SDK/CLI hard turn/spend caps are NEVER routine sizing: the only permitted
platform ceiling is a catastrophic failsafe far outside the normal
workload/landing range, private to the controller, with partial-state
recovery when it fires (s5.5).

This module records and directs; it never spawns, resumes, stops, or
messages an agent itself (SHADOW-ONLY, R595 untouched).

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any

from .subagent_contracts import (
    BAND_EMERGENCY,
    BAND_LAND,
    BAND_NORMAL,
    BAND_OBSERVE,
    BAND_PREPARE,
    HEALTH_BAND_NAMES,
    HealthBands,
    SupervisionEnvelope,
    TELEMETRY_SOURCES,
    assert_no_envelope_leak,
    assert_worker_text_clean,
)
from .telemetry_records import CONFIDENCE_LABELS


class HealthRuntimeError(ValueError):
    """Typed error for runtime health evaluation (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


#: Closed controller-action vocabulary. Only ``send-landing-direction``
#: produces worker-visible text, and only once per assignment.
ACTION_NONE = "none"
ACTION_EXTERNAL_CHECK = "external-check"
ACTION_HOLD_SCOPE = "hold-scope"
ACTION_SEND_LANDING = "send-landing-direction"
ACTION_ALLOW_SEAM = "allow-reach-seam"
ACTION_EMERGENCY_STOP = "emergency-stop"
BAND_ACTIONS: tuple[str, ...] = (
    ACTION_NONE, ACTION_EXTERNAL_CHECK, ACTION_HOLD_SCOPE,
    ACTION_SEND_LANDING, ACTION_ALLOW_SEAM, ACTION_EMERGENCY_STOP)

#: The s5.5 emergency-stop conditions. Platform TaskStop is reserved for
#: these; ordinary landing NEVER uses it (s16.2).
EMERGENCY_CONDITIONS: tuple[str, ...] = (
    "unresponsive-process",
    "unsafe-process",
    "imminent-hard-limit",
    "owner-emergency-stop",
    "no-safe-seam",
)

#: The ONE concise landing direction (s5.5 "Land" verbatim intent). No
#: numbers, no band names, no telemetry: both contract guards prove it at
#: send time. Course correction is sparse — sent at most once.
LANDING_DIRECTION_TEXT = (
    "Finish the current atomic step, save and test what is coherent, and "
    "return the bounded handoff.")


@dataclasses.dataclass(frozen=True)
class TelemetrySnapshot:
    """A by-value snapshot of live Phase B telemetry for ONE assignment.

    Unknown is ``None``, never zero. ``source``/``confidence`` come from the
    accepted Phase B closed vocabularies; the evaluation turns conservative
    when occupancy is unknown (s5.2).
    """

    assignment_id: str
    occupancy_fraction: float | None = None
    cumulative_tokens: int | None = None
    compaction_count: int | None = None
    elapsed_minutes: float | None = None
    turns: int | None = None
    tool_batches: int | None = None
    source: str = "sdk_events"
    confidence: str = "unknown"

    def __post_init__(self) -> None:
        if not self.assignment_id:
            raise HealthRuntimeError("missing_ids",
                                     "snapshot requires assignment_id")
        if self.source not in TELEMETRY_SOURCES:
            raise HealthRuntimeError(
                "unknown_telemetry_source",
                f"snapshot source {self.source!r} is not in the Phase B "
                f"closed set {list(TELEMETRY_SOURCES)}")
        if self.confidence not in CONFIDENCE_LABELS:
            raise HealthRuntimeError(
                "bad_confidence",
                f"snapshot confidence {self.confidence!r} is not in the "
                f"closed confidence vocabulary")
        if self.occupancy_fraction is not None \
                and not 0.0 <= float(self.occupancy_fraction) <= 1.0:
            raise HealthRuntimeError(
                "bad_occupancy",
                f"occupancy_fraction must be within [0, 1] or None, got "
                f"{self.occupancy_fraction!r}")
        for name in ("cumulative_tokens", "compaction_count", "turns",
                     "tool_batches"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool)
                                      or not isinstance(value, int)
                                      or value < 0):
                raise HealthRuntimeError(
                    "bad_counter",
                    f"{name} must be a non-negative integer or None "
                    f"(unknown is None, never zero), got {value!r}")
        if self.elapsed_minutes is not None and self.elapsed_minutes < 0:
            raise HealthRuntimeError(
                "bad_counter", "elapsed_minutes may not be negative")


@dataclasses.dataclass(frozen=True)
class ProgressAssessment:
    """The controller's judgment of progress from DURABLE external evidence
    (s6.2 via ``runtime_detectors``), never from text volume."""

    verified_progress: bool = False
    coherent: bool = True
    near_complete: bool = False
    model_reports_losing_thread: bool = False
    no_progress: bool = False
    scope_drift: bool = False


@dataclasses.dataclass(frozen=True)
class BandEvaluation:
    """One controller-side evaluation: band, action, reasons, and the
    (rare) worker message. Everything except ``worker_message`` is private.
    """

    assignment_id: str
    band: str
    action: str
    reasons: tuple[str, ...]
    worker_message: str | None
    requires_review: bool

    def __post_init__(self) -> None:
        if self.band not in HEALTH_BAND_NAMES:
            raise HealthRuntimeError("bad_band",
                                     f"unknown band {self.band!r}")
        if self.action not in BAND_ACTIONS:
            raise HealthRuntimeError("bad_action",
                                     f"unknown action {self.action!r}")


def _band_from_occupancy(bands: HealthBands,
                         occupancy: float | None) -> tuple[str, str]:
    if occupancy is None:
        return BAND_OBSERVE, ("occupancy unknown - conservative observe, "
                              "never optimistic normal (s5.2)")
    if occupancy >= bands.emergency_occupancy:
        return BAND_EMERGENCY, f"occupancy {occupancy:.2f} at emergency band"
    if occupancy >= bands.land_occupancy:
        return BAND_LAND, f"occupancy {occupancy:.2f} at land band"
    if occupancy >= bands.prepare_occupancy:
        return BAND_PREPARE, f"occupancy {occupancy:.2f} at prepare band"
    if occupancy >= bands.observe_occupancy:
        return BAND_OBSERVE, f"occupancy {occupancy:.2f} at observe band"
    return BAND_NORMAL, f"occupancy {occupancy:.2f} in normal band"


def evaluate_band(envelope: SupervisionEnvelope,
                  snapshot: TelemetrySnapshot,
                  assessment: ProgressAssessment,
                  *,
                  emergency_conditions: tuple[str, ...] = ()) -> BandEvaluation:
    """Evaluate one assignment's band and controller action (s5.4/s5.5).

    ``emergency_conditions`` are the s5.5-reserved reasons; occupancy at or
    above the emergency threshold implies ``imminent-hard-limit``. Without a
    condition, the evaluation NEVER escalates to the platform stop — landing
    is the ordinary mechanism (s16.2 TaskStop reservation).
    """
    if snapshot.assignment_id != envelope.assignment_id:
        raise HealthRuntimeError(
            "unlinked_records",
            f"snapshot {snapshot.assignment_id!r} does not belong to "
            f"envelope {envelope.assignment_id!r}")
    unknown = sorted(set(emergency_conditions) - set(EMERGENCY_CONDITIONS))
    if unknown:
        raise HealthRuntimeError(
            "bad_emergency_condition",
            f"unknown emergency condition(s) {unknown}; the closed set is "
            f"{list(EMERGENCY_CONDITIONS)}")
    reasons: list[str] = []
    band, why = _band_from_occupancy(envelope.health_bands,
                                     snapshot.occupancy_fraction)
    reasons.append(why)

    order = {name: i for i, name in enumerate(HEALTH_BAND_NAMES)}
    conditions = list(emergency_conditions)
    if band == BAND_EMERGENCY and "imminent-hard-limit" not in conditions:
        conditions.append("imminent-hard-limit")

    if assessment.model_reports_losing_thread:
        # Immediate quality signal even if every counter is low (s5.5).
        if order[band] < order[BAND_LAND]:
            band = BAND_LAND
        reasons.append("model reports losing the thread - immediate "
                       "quality signal regardless of counters")
    requires_review = False
    if assessment.no_progress or assessment.scope_drift:
        # Review triggers regardless of how many tokens were used (s6.2);
        # low usage does not buy unlimited investigation time.
        requires_review = True
        if order[band] < order[BAND_PREPARE]:
            band = BAND_PREPARE
        reasons.append("no-progress/scope-drift finding - landing/extension "
                       "review triggered regardless of token counters")

    if conditions:
        reasons.append(f"emergency condition(s): {sorted(set(conditions))}")
        return BandEvaluation(
            assignment_id=envelope.assignment_id, band=BAND_EMERGENCY,
            action=ACTION_EMERGENCY_STOP, reasons=tuple(reasons),
            worker_message=None, requires_review=True)
    if band == BAND_EMERGENCY:
        # Unreachable without a condition (emergency occupancy implies one);
        # kept as an explicit fail-closed landing fallback.
        band = BAND_LAND
    if band == BAND_LAND:
        if assessment.near_complete and assessment.coherent:
            reasons.append("near-complete coherent unit - let it reach the "
                           "safe seam; never killed solely for crossing a "
                           "round number (s5.5)")
            return BandEvaluation(
                assignment_id=envelope.assignment_id, band=band,
                action=ACTION_ALLOW_SEAM, reasons=tuple(reasons),
                worker_message=None, requires_review=requires_review)
        return BandEvaluation(
            assignment_id=envelope.assignment_id, band=band,
            action=ACTION_SEND_LANDING, reasons=tuple(reasons),
            worker_message=LANDING_DIRECTION_TEXT,
            requires_review=requires_review)
    if band == BAND_PREPARE:
        return BandEvaluation(
            assignment_id=envelope.assignment_id, band=band,
            action=ACTION_HOLD_SCOPE, reasons=tuple(reasons),
            worker_message=None, requires_review=requires_review)
    if band == BAND_OBSERVE:
        return BandEvaluation(
            assignment_id=envelope.assignment_id, band=band,
            action=ACTION_EXTERNAL_CHECK, reasons=tuple(reasons),
            worker_message=None, requires_review=requires_review)
    return BandEvaluation(
        assignment_id=envelope.assignment_id, band=band, action=ACTION_NONE,
        reasons=tuple(reasons), worker_message=None,
        requires_review=requires_review)


@dataclasses.dataclass(frozen=True)
class LandingDirection:
    """The durable record of the ONE landing message (sparse by contract)."""

    assignment_id: str
    at_minutes: float
    text: str


class SupervisionState:
    """Per-assignment mutable runtime state: enforces the one-message
    landing discipline and the prepare-to-land scope hold."""

    def __init__(self, envelope: SupervisionEnvelope) -> None:
        self._envelope = envelope
        self._landing: LandingDirection | None = None
        self._scope_held = False

    @property
    def scope_held(self) -> bool:
        return self._scope_held

    @property
    def landing_directed(self) -> bool:
        return self._landing is not None

    def landing_record(self) -> LandingDirection | None:
        return self._landing

    def apply(self, evaluation: BandEvaluation,
              *, at_minutes: float = 0.0) -> LandingDirection | None:
        """Apply one evaluation. Returns the landing direction EXACTLY once;
        every other action returns None (no worker message ever).

        The message is proven through BOTH contract guards at send time: no
        quota/countdown language and no envelope leak (R045/s6).
        """
        if evaluation.assignment_id != self._envelope.assignment_id:
            raise HealthRuntimeError(
                "unlinked_records",
                f"evaluation {evaluation.assignment_id!r} does not belong "
                f"to state {self._envelope.assignment_id!r}")
        if evaluation.action in (ACTION_HOLD_SCOPE, ACTION_SEND_LANDING,
                                 ACTION_EMERGENCY_STOP):
            self._scope_held = True
        if evaluation.action != ACTION_SEND_LANDING:
            return None
        if self._landing is not None:
            return None
        message = evaluation.worker_message or LANDING_DIRECTION_TEXT
        assert_worker_text_clean("landing_direction", message)
        assert_no_envelope_leak(message, self._envelope)
        self._landing = LandingDirection(
            assignment_id=evaluation.assignment_id,
            at_minutes=at_minutes, text=message)
        return self._landing


def bands_for_model(config: Any, resolved_model: str) -> HealthBands:
    """Per-resolved-model band calibration (s5.5).

    Reads ``[subagent_model_bands.<model>]`` from controller config, failing
    closed on unknown keys; a model without an override uses the global
    ``[subagent_health_bands]`` table. These are controller policy from
    observed behavior — conservative warning evidence, never vendor capacity
    claims and never automatic kill numbers.
    """
    if not resolved_model:
        raise HealthRuntimeError("missing_model",
                                 "resolved_model is required")
    raw = getattr(config, "raw", {}) or {}
    section = raw.get("subagent_model_bands", {}) or {}
    if not isinstance(section, Mapping):
        raise HealthRuntimeError("bad_section",
                                 "[subagent_model_bands] must be a table")
    override = section.get(resolved_model)
    if override is None:
        return HealthBands.from_controller_config(config)
    if not isinstance(override, Mapping):
        raise HealthRuntimeError(
            "bad_section",
            f"[subagent_model_bands.{resolved_model}] must be a table")
    known = {f.name for f in dataclasses.fields(HealthBands)}
    unknown = sorted(set(override) - known)
    if unknown:
        raise HealthRuntimeError(
            "unknown_band_key",
            f"unrecognized [subagent_model_bands.{resolved_model}] keys: "
            f"{unknown}")
    return HealthBands(**{k: v for k, v in override.items()})


@dataclasses.dataclass(frozen=True)
class CatastrophicCeiling:
    """The ONLY permitted platform-level hard cap (s5.5): a private
    catastrophic failsafe far outside the normal workload/landing range —
    never a routine sizing or landing mechanism."""

    ceiling_tokens: int
    normal_range_tokens: int
    min_multiple: int = 5

    def __post_init__(self) -> None:
        for name in ("ceiling_tokens", "normal_range_tokens",
                     "min_multiple"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) \
                    or value <= 0:
                raise HealthRuntimeError(
                    "bad_ceiling", f"{name} must be a positive integer")
        if self.ceiling_tokens < self.normal_range_tokens * self.min_multiple:
            raise HealthRuntimeError(
                "bad_ceiling",
                f"ceiling_tokens={self.ceiling_tokens} is inside the normal "
                f"workload/landing range (< {self.min_multiple} x "
                f"{self.normal_range_tokens}); a platform cap that can cut "
                f"through useful work is prohibited as routine sizing "
                f"(s5.5)")


def validate_platform_caps(*, max_turns: int | None = None,
                           max_budget_usd: float | None = None,
                           catastrophic: CatastrophicCeiling | None = None,
                           ) -> CatastrophicCeiling | None:
    """Refuse SDK/CLI hard caps as routine work sizing (s5.5, s16.2).

    Any ``maxTurns``/``maxBudgetUsd``-style value is rejected outright; the
    only representable ceiling is a validated :class:`CatastrophicCeiling`.
    """
    if max_turns is not None or max_budget_usd is not None:
        raise HealthRuntimeError(
            "routine_cap",
            "maxTurns/maxBudgetUsd-style hard caps are never routine "
            "sizing or landing mechanisms; official behavior can end the "
            "loop or stop background subagents mid-work (s5.5). Use the "
            "health bands, and at most a catastrophic ceiling far outside "
            "the normal range.")
    return catastrophic


#: Ordered partial-state recovery steps when the catastrophic ceiling fires:
#: quarantine and reconcile, never pretend completion (s5.5).
RECOVERY_STEPS: tuple[str, ...] = (
    "quarantine-partial-state",
    "reconcile-write-leases",
    "reconcile-external-effects",
    "harvest-durable-evidence",
    "record-durable-partial-handoff",
)


@dataclasses.dataclass(frozen=True)
class PartialStateRecovery:
    """The recovery record produced when the catastrophic ceiling fires."""

    assignment_id: str
    fired_at_tokens: int
    steps: tuple[str, ...]
    quarantined: bool
    completed: bool

    def __post_init__(self) -> None:
        if self.completed:
            raise HealthRuntimeError(
                "false_completion",
                "a ceiling-interrupted assignment is NEVER recorded as "
                "completed; quarantine and reconcile instead (s5.5)")
        if not self.quarantined:
            raise HealthRuntimeError(
                "not_quarantined",
                "partial state must be quarantined before reconciliation")


def ceiling_fired(ceiling: CatastrophicCeiling,
                  snapshot: TelemetrySnapshot) -> PartialStateRecovery | None:
    """Return the partial-state recovery plan if the failsafe fired."""
    if snapshot.cumulative_tokens is None \
            or snapshot.cumulative_tokens < ceiling.ceiling_tokens:
        return None
    return PartialStateRecovery(
        assignment_id=snapshot.assignment_id,
        fired_at_tokens=snapshot.cumulative_tokens,
        steps=RECOVERY_STEPS,
        quarantined=True,
        completed=False,
    )
