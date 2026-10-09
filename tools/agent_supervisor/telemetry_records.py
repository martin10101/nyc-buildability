"""Typed telemetry records with source/confidence labels (D-024 Phase B, M0-T088).

Every usage number the supervisor stores or displays is a :class:`Measurement`
carrying BOTH:

* a **source/confidence label** (D-024 s5.2 / R042) naming the evidence source
  the number came from; and
* a **category** (D-024 s5 / R038) separating the three kinds of fact that must
  never be labelled as one another:

  - ``occupancy``   -- how full the live model context is NOW (describes the
                       most recent API response, never lifetime spend);
  - ``cumulative``  -- tokens/cost that flowed through over time, including
                       work compacted away;
  - ``estimate``    -- a planning estimate of future cost, not a fact.

Missing usage is ``unknown``, never zero (R042): a Measurement with no value
MUST carry the ``unknown`` label, and a numeric value may not claim ``unknown``.

This module is pure data/validation - no I/O, no model-context injection, and
nothing here ever composes a prompt (D-024 s5.3 / R044).

Supervisor-freeze qualifying evidence: D-024-R100 (Phase B, explicitly listed
in owner directive D-024).
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping

SCHEMA = "supervisor_telemetry/v1"

#: D-024 s5.2 source/confidence vocabulary, verbatim.
CONFIDENCE_LABELS = (
    "provider-exact",
    "sdk-task-cumulative",
    "subagent-status-live",
    "sdk-cumulative",
    "status-live",
    "transcript-derived",
    "estimated",
    "unknown",
)

#: D-024 s5 measurement categories (R038). Never label one as another.
CATEGORIES = ("occupancy", "cumulative", "estimate")

#: Canonical measurement names -> their REQUIRED category. A name listed here
#: may never be recorded under a different category; unlisted names are allowed
#: (later phases add subagent/SDK names) but must still declare a category.
MEASUREMENT_CATEGORY: dict[str, str] = {
    # live context occupancy (status-line context_window.*; most recent API
    # response - D-024 s5.1 item 3: never presented as lifetime spend)
    "context_used_tokens": "occupancy",
    "context_window_tokens": "occupancy",
    "context_used_pct": "occupancy",
    "context_remaining_pct": "occupancy",
    "context_total_input_tokens": "occupancy",
    "context_total_output_tokens": "occupancy",
    "live_input_tokens": "occupancy",
    "live_output_tokens": "occupancy",
    "live_cache_creation_tokens": "occupancy",
    "live_cache_read_tokens": "occupancy",
    # cumulative spend over the session/task run
    "cumulative_cost_usd": "cumulative",
    "cumulative_duration_ms": "cumulative",
    "cumulative_api_duration_ms": "cumulative",
    "cumulative_input_tokens": "cumulative",
    "cumulative_output_tokens": "cumulative",
    "cumulative_cache_creation_tokens": "cumulative",
    "cumulative_cache_read_tokens": "cumulative",
    "reported_cumulative_input_tokens": "cumulative",
    "reported_cumulative_output_tokens": "cumulative",
    "reported_cumulative_total_tokens": "cumulative",
    # single-step provider usage on provider_usage_step records (M0-T088 G3
    # carried fix: a per-step delta never borrows the cumulative_* names)
    "step_input_tokens": "cumulative",
    "step_output_tokens": "cumulative",
    "step_cache_creation_tokens": "cumulative",
    "step_cache_read_tokens": "cumulative",
    # subagent status feed (docs pair tokenCount with contextWindowSize -> the
    # task's live context, not lifetime spend; M0-T089)
    "subagent_token_count": "occupancy",
    "subagent_context_window_tokens": "occupancy",
    # Agent SDK task feed (task-progress totals are per-task cumulative;
    # final_request_* describe ONLY the final API request - R043)
    "sdk_task_total_tokens": "cumulative",
    "sdk_task_tool_uses": "cumulative",
    "sdk_task_duration_ms": "cumulative",
    "final_request_input_tokens": "cumulative",
    "final_request_output_tokens": "cumulative",
    # transcript-derived fallback sums and compaction facts
    "transcript_input_tokens": "cumulative",
    "transcript_output_tokens": "cumulative",
    "transcript_cache_creation_tokens": "cumulative",
    "transcript_cache_read_tokens": "cumulative",
    "compaction_count": "cumulative",
    "compaction_pre_tokens_total": "cumulative",
    # planning estimates (facts about the future do not exist)
    "estimated_remaining_tokens": "estimate",
    "estimated_total_tokens": "estimate",
}


class TelemetryRecordError(ValueError):
    """A record or measurement violated the telemetry typing rules."""


@dataclasses.dataclass(frozen=True)
class Measurement:
    """One labelled usage number (or an explicit unknown).

    ``value`` is ``None`` exactly when ``label`` is ``unknown``: a missing
    number is never coerced to zero, and a real number never hides behind
    ``unknown``.
    """

    value: int | float | None
    label: str
    category: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.label not in CONFIDENCE_LABELS:
            raise TelemetryRecordError(
                f"unknown confidence label {self.label!r}; allowed: {CONFIDENCE_LABELS}")
        if self.category not in CATEGORIES:
            raise TelemetryRecordError(
                f"unknown measurement category {self.category!r}; allowed: {CATEGORIES}")
        if self.value is None:
            if self.label != "unknown":
                raise TelemetryRecordError(
                    f"missing value must carry label 'unknown', got {self.label!r} "
                    f"(missing usage is unknown, never zero - D-024 R042)")
        else:
            if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
                raise TelemetryRecordError(
                    f"measurement value must be int/float, got {type(self.value).__name__}")
            if self.label == "unknown":
                raise TelemetryRecordError(
                    "a numeric value may not be labelled 'unknown'; pick the real "
                    "evidence source or drop the number")
            if self.value < 0:
                raise TelemetryRecordError(
                    f"measurement value must be >= 0, got {self.value!r}")

    @classmethod
    def unknown(cls, category: str, detail: str = "") -> "Measurement":
        """The one honest representation of a missing number."""
        return cls(value=None, label="unknown", category=category, detail=detail)

    @property
    def is_unknown(self) -> bool:
        return self.value is None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "value": self.value, "label": self.label, "category": self.category}
        if self.detail:
            out["detail"] = self.detail
        return out

    @classmethod
    def from_dict(cls, data: Any) -> "Measurement":
        if not isinstance(data, Mapping):
            raise TelemetryRecordError(
                f"measurement must be a mapping, got {type(data).__name__}")
        return cls(value=data.get("value"), label=str(data.get("label", "")),
                   category=str(data.get("category", "")),
                   detail=str(data.get("detail", "")))


def _check_measurement_name(name: str, measurement: Measurement) -> None:
    required = MEASUREMENT_CATEGORY.get(name)
    if required is not None and measurement.category != required:
        raise TelemetryRecordError(
            f"measurement {name!r} is a {required} fact but was recorded as "
            f"{measurement.category!r}; occupancy, cumulative spend, and estimates "
            f"are never labelled as one another (D-024 s5 / R038)")


@dataclasses.dataclass(frozen=True)
class TelemetryRecord:
    """One typed telemetry event: identity + labelled measurements + context.

    ``attributes`` holds non-numeric context (transcript path, model id,
    rate-limit payloads...). Free text placed here is bounded/redacted by the
    journal on write; nothing in a record is ever injected into model context.
    """

    record_type: str
    timestamp_utc: str
    measurements: Mapping[str, Measurement] = dataclasses.field(default_factory=dict)
    session_id: str = ""
    task_id: str = ""
    attributes: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    redaction_count: int = 0

    def __post_init__(self) -> None:
        if not self.record_type or not isinstance(self.record_type, str):
            raise TelemetryRecordError("record_type must be a non-empty string")
        if not self.timestamp_utc or not isinstance(self.timestamp_utc, str):
            raise TelemetryRecordError("timestamp_utc must be a non-empty string")
        for name, m in self.measurements.items():
            if not isinstance(m, Measurement):
                raise TelemetryRecordError(
                    f"measurement {name!r} must be a Measurement, "
                    f"got {type(m).__name__}")
            _check_measurement_name(name, m)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "record_type": self.record_type,
            "timestamp_utc": self.timestamp_utc,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "measurements": {k: v.to_dict() for k, v in self.measurements.items()},
            "attributes": dict(self.attributes),
            "redaction_count": self.redaction_count,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "TelemetryRecord":
        if not isinstance(data, Mapping):
            raise TelemetryRecordError(
                f"record must be a mapping, got {type(data).__name__}")
        if data.get("schema") != SCHEMA:
            raise TelemetryRecordError(
                f"unsupported telemetry schema {data.get('schema')!r}; "
                f"expected {SCHEMA!r}")
        raw = data.get("measurements") or {}
        if not isinstance(raw, Mapping):
            raise TelemetryRecordError("measurements must be a mapping")
        return cls(
            record_type=str(data.get("record_type", "")),
            timestamp_utc=str(data.get("timestamp_utc", "")),
            session_id=str(data.get("session_id", "")),
            task_id=str(data.get("task_id", "")),
            measurements={str(k): Measurement.from_dict(v) for k, v in raw.items()},
            attributes=dict(data.get("attributes") or {}),
            redaction_count=int(data.get("redaction_count", 0)),
        )
