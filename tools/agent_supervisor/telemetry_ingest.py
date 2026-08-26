"""Primary-session usage ingestion (D-024 Phase B items 2 and 6, M0-T088).

Two ingestion paths, both passive - they read structured payloads the runtime
already produces and emit typed records; nothing here prompts the model, adds
``additionalContext``, or messages a worker (s5.3/R037/R044):

* :func:`ingest_status_line` -- the Claude Code status-line JSON for the
  PRIMARY interactive session (D-024 s5.1 item 3). Field semantics follow the
  official statusline schema captured in
  ``fixtures/capability_matrix_v1.json`` (``claude.statusline.primary_payload``
  / ``claude.statusline.nullable_fields``): ``context_window.*`` describes the
  LIVE context from the most recent API response (occupancy - never presented
  as lifetime spend), ``cost.*`` is session-cumulative, ``current_usage`` is
  null before the first API call and again after compaction, and the
  percentage fields may be null early. Every field is treated as nullable and
  feature-detected; a missing number ingests as ``unknown``, never zero.

* :class:`UsageAccumulator` -- structured provider usage for the main loop
  (D-024 s5.1 item 4). Per-step assistant usage and platform-reported
  cumulative usage are kept DISTINCT (per-step sums never masquerade as a
  platform total and vice versa), assistant messages sharing a message ID are
  deduplicated, and a reported counter that goes BACKWARDS (reset/regression)
  is flagged and high-water totals are preserved so the run never looks
  "fresh" (16.1).

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any

from .models import to_utc_iso
from .telemetry_records import Measurement, TelemetryRecord

#: Anthropic-style usage payload fields consumed per step, in canonical order.
_STEP_USAGE_FIELDS = (
    ("input_tokens", "cumulative_input_tokens"),
    ("output_tokens", "cumulative_output_tokens"),
    ("cache_creation_input_tokens", "cumulative_cache_creation_tokens"),
    ("cache_read_input_tokens", "cumulative_cache_read_tokens"),
)

#: Reported-cumulative fields (result/per-query totals from the platform).
_REPORTED_FIELDS = (
    ("input_tokens", "reported_cumulative_input_tokens"),
    ("output_tokens", "reported_cumulative_output_tokens"),
    ("total_tokens", "reported_cumulative_total_tokens"),
)


def _clean_count(value: Any) -> int | float | None:
    """A usable non-negative number, or None (absent/null/malformed alike).

    ``True``/``False`` are rejected: JSON booleans are not token counts.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value < 0:
        return None
    return value


def _measure(value: Any, category: str, label: str,
             absent_detail: str) -> Measurement:
    clean = _clean_count(value)
    if clean is None:
        return Measurement.unknown(category, absent_detail)
    return Measurement(value=clean, label=label, category=category)


def ingest_status_line(payload: Any, *,
                       now_utc_iso: str | None = None) -> TelemetryRecord:
    """One typed record from a primary status-line JSON payload.

    Accepts anything: a non-dict payload produces an all-unknown record (fail
    to unknown, never invent). Null/absent numeric fields - normal at startup
    and immediately after compaction - each become an ``unknown`` measurement.
    """
    now = now_utc_iso or to_utc_iso()
    if not isinstance(payload, dict):
        return TelemetryRecord(
            record_type="primary_status_line", timestamp_utc=now,
            measurements={
                "context_used_pct": Measurement.unknown(
                    "occupancy", "status payload missing or not a JSON object"),
            },
            attributes={"payload_error": f"expected object, got "
                                         f"{type(payload).__name__}"})

    context = payload.get("context_window")
    context = context if isinstance(context, dict) else {}
    current = context.get("current_usage")
    current = current if isinstance(current, dict) else {}
    cost = payload.get("cost")
    cost = cost if isinstance(cost, dict) else {}

    nullable = "absent or null (nullable at startup and after compaction)"
    measurements = {
        # LIVE occupancy - most recent API response, never lifetime spend.
        "context_total_input_tokens": _measure(
            context.get("total_input_tokens"), "occupancy", "status-live", nullable),
        "context_total_output_tokens": _measure(
            context.get("total_output_tokens"), "occupancy", "status-live", nullable),
        "context_window_tokens": _measure(
            context.get("context_window_size"), "occupancy", "status-live", nullable),
        "context_used_pct": _measure(
            context.get("used_percentage"), "occupancy", "status-live", nullable),
        "context_remaining_pct": _measure(
            context.get("remaining_percentage"), "occupancy", "status-live", nullable),
        "live_input_tokens": _measure(
            current.get("input_tokens"), "occupancy", "status-live", nullable),
        "live_output_tokens": _measure(
            current.get("output_tokens"), "occupancy", "status-live", nullable),
        "live_cache_creation_tokens": _measure(
            current.get("cache_creation_input_tokens"), "occupancy",
            "status-live", nullable),
        "live_cache_read_tokens": _measure(
            current.get("cache_read_input_tokens"), "occupancy",
            "status-live", nullable),
        # session-cumulative facts from cost.*
        "cumulative_cost_usd": _measure(
            cost.get("total_cost_usd"), "cumulative", "status-live", nullable),
        "cumulative_duration_ms": _measure(
            cost.get("total_duration_ms"), "cumulative", "status-live", nullable),
        "cumulative_api_duration_ms": _measure(
            cost.get("total_api_duration_ms"), "cumulative", "status-live",
            nullable),
    }

    model = payload.get("model")
    model = model if isinstance(model, dict) else {}
    attributes: dict[str, Any] = {}
    for key, value in (
            ("transcript_path", payload.get("transcript_path")),
            ("cwd", payload.get("cwd")),
            ("version", payload.get("version")),
            ("model_id", model.get("id")),
            ("model_display_name", model.get("display_name")),
            ("exceeds_200k_tokens", payload.get("exceeds_200k_tokens"))):
        if value is not None:
            attributes[key] = value
    rate_limits = payload.get("rate_limits")
    if isinstance(rate_limits, dict):
        # preserved verbatim for the controller; sanitized by the journal on
        # write; absent for non-subscribers and before the first response
        attributes["rate_limits"] = rate_limits

    session = payload.get("session_id")
    return TelemetryRecord(
        record_type="primary_status_line",
        timestamp_utc=now,
        session_id=session if isinstance(session, str) else "",
        measurements=measurements,
        attributes=attributes,
    )


class UsageAccumulator:
    """Main-loop provider-usage tracking: dedup, distinct scopes, no resets.

    Step sums (built from deduplicated per-step assistant usage) and
    platform-reported cumulative totals are held in separate structures and
    emitted under separate measurement names with separate labels
    (``provider-exact`` vs ``sdk-cumulative``); they are never merged.
    """

    def __init__(self, *, session_id: str = "",
                 max_seen_ids: int = 4096) -> None:
        if max_seen_ids < 1:
            raise ValueError("max_seen_ids must be >= 1")
        self.session_id = session_id
        self._max_seen_ids = max_seen_ids
        self._seen_ids: OrderedDict[str, None] = OrderedDict()
        self._step_totals: dict[str, int | float] = {}
        self._steps_ingested = 0
        self._duplicates_ignored = 0
        self._unidentified_steps = 0
        self._malformed_steps = 0
        self._reported_high_water: dict[str, int | float] = {}
        self._reported_latest: dict[str, int | float] = {}
        self._counter_regressions = 0

    # -- per-step assistant usage (provider-exact) ---------------------------

    def ingest_step(self, message_id: Any, usage: Any, *,
                    now_utc_iso: str | None = None) -> TelemetryRecord | None:
        """Ingest one assistant message's usage; returns the per-step record.

        Duplicate message IDs (streaming/resume replays deliver the same
        message more than once) are ignored and counted - ``None`` is
        returned so callers know nothing was added.
        """
        now = now_utc_iso or to_utc_iso()
        if isinstance(message_id, str) and message_id:
            if message_id in self._seen_ids:
                self._duplicates_ignored += 1
                return None
            self._seen_ids[message_id] = None
            if len(self._seen_ids) > self._max_seen_ids:
                self._seen_ids.popitem(last=False)
        else:
            # no ID -> cannot dedup; ingest (losing real usage is worse) and
            # count it so the controller can see dedup coverage is partial
            self._unidentified_steps += 1

        if not isinstance(usage, dict):
            self._malformed_steps += 1
            return TelemetryRecord(
                record_type="provider_usage_step", timestamp_utc=now,
                session_id=self.session_id,
                measurements={
                    "cumulative_input_tokens": Measurement.unknown(
                        "cumulative", "step usage missing or not an object"),
                },
                attributes={"message_id": message_id
                            if isinstance(message_id, str) else ""})

        step_measurements: dict[str, Measurement] = {}
        any_known = False
        for field, name in _STEP_USAGE_FIELDS:
            clean = _clean_count(usage.get(field))
            if clean is None:
                step_measurements[name] = Measurement.unknown(
                    "cumulative", f"{field} absent or malformed in step usage")
            else:
                any_known = True
                step_measurements[name] = Measurement(
                    value=clean, label="provider-exact", category="cumulative",
                    detail="single step, not a running total")
                self._step_totals[name] = self._step_totals.get(name, 0) + clean
        if any_known:
            self._steps_ingested += 1
        else:
            self._malformed_steps += 1
        return TelemetryRecord(
            record_type="provider_usage_step", timestamp_utc=now,
            session_id=self.session_id, measurements=step_measurements,
            attributes={"message_id": message_id
                        if isinstance(message_id, str) else ""})

    # -- platform-reported cumulative usage (sdk-cumulative) -----------------

    def ingest_reported_cumulative(self, usage: Any) -> None:
        """Record a platform-reported cumulative total (result/per-query).

        A total lower than one already reported is a counter reset or
        regression: it is counted, and the high-water values are retained so
        the run never appears fresher than it is (16.1).
        """
        if not isinstance(usage, dict):
            self._malformed_steps += 1
            return
        regressed = False
        for field, name in _REPORTED_FIELDS:
            clean = _clean_count(usage.get(field))
            if clean is None:
                continue
            previous = self._reported_high_water.get(name)
            if previous is not None and clean < previous:
                regressed = True
            else:
                self._reported_high_water[name] = clean
            self._reported_latest[name] = clean
        if regressed:
            self._counter_regressions += 1

    # -- snapshot ------------------------------------------------------------

    @property
    def counter_regressions(self) -> int:
        return self._counter_regressions

    @property
    def duplicates_ignored(self) -> int:
        return self._duplicates_ignored

    def snapshot(self, *, now_utc_iso: str | None = None) -> TelemetryRecord:
        """Current cumulative picture; step sums and reported totals distinct."""
        now = now_utc_iso or to_utc_iso()
        measurements: dict[str, Measurement] = {}
        incomplete = (" (lower bound: some steps had unknown usage)"
                      if self._malformed_steps else "")
        for _field, name in _STEP_USAGE_FIELDS:
            if self._steps_ingested == 0:
                measurements[name] = Measurement.unknown(
                    "cumulative", "no provider usage observed yet")
            else:
                measurements[name] = Measurement(
                    value=self._step_totals.get(name, 0),
                    label="provider-exact", category="cumulative",
                    detail="sum of deduplicated per-step usage" + incomplete)
        for _field, name in _REPORTED_FIELDS:
            high = self._reported_high_water.get(name)
            if high is None:
                measurements[name] = Measurement.unknown(
                    "cumulative", "platform has not reported this total")
            else:
                measurements[name] = Measurement(
                    value=high, label="sdk-cumulative", category="cumulative",
                    detail="platform-reported high-water total; never merged "
                           "with per-step sums")
        return TelemetryRecord(
            record_type="provider_usage", timestamp_utc=now,
            session_id=self.session_id, measurements=measurements,
            attributes={
                "steps_ingested": self._steps_ingested,
                "duplicates_ignored": self._duplicates_ignored,
                "unidentified_steps": self._unidentified_steps,
                "malformed_steps": self._malformed_steps,
                "counter_regressions": self._counter_regressions,
                "reported_latest": dict(self._reported_latest),
            })
