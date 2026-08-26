"""Agent SDK task-event ingestion — feature-detected, never installed
(D-024 Phase B item 4, M0-T089).

The Agent SDK is OPTIONAL (D-024 s5.1/R040): it is currently absent-by-policy
on this workstation (``fixtures/capability_matrix_v1.json`` ``agent_sdk.python``)
and this module must never install, import-for-side-effects, or upgrade it.
Availability is probed with ``importlib.util.find_spec`` only. The event
PARSERS below are pure functions over already-decoded event dicts, so the test
suite exercises them with fixtures while the SDK stays absent (16.1: an
unadmitted SDK cleanly skips the SDK path; the suite installs nothing).

Documented SDK task telemetry (D-024 s5.1 item 1): a periodic task-progress
event keyed by task ID with ``total_tokens``, ``tool_uses``, ``duration_ms``,
current description and ``last_tool_name``, followed by a completion/failure/
stopped notification. Duties implemented here:

* progress totals are per-task cumulative -> ``sdk-task-cumulative`` label;
* duplicate progress events dedupe monotonically (a repeat or stale total
  never double-counts, a REGRESSION is counted and high-water retained);
* out-of-order completion tolerated (completion before the last progress
  keeps the high-water totals);
* a final result's usage/totalTokens is NEVER assumed to describe the whole
  run (R043): it records as ``final_request_*`` with an explicit caveat while
  cumulative tracking stays with the progress high-water.

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

import importlib.util
from typing import Any

from .models import to_utc_iso
from .telemetry_records import Measurement, TelemetryRecord

#: Module names probed for SDK presence. Probing NEVER imports the module.
SDK_MODULE_CANDIDATES = ("claude_agent_sdk",)


def sdk_available() -> bool:
    """True only when an approved SDK is already installed (find_spec probe;
    no import, no install, no side effect — R040)."""
    for name in SDK_MODULE_CANDIDATES:
        try:
            if importlib.util.find_spec(name) is not None:
                return True
        except (ImportError, ValueError):
            continue
    return False


def _clean(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        return None
    return value


class SdkTaskTracker:
    """Per-task cumulative tracking over SDK progress/notification events."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}

    def ingest_event(self, event: Any, *,
                     now_utc_iso: str | None = None) -> TelemetryRecord:
        """Parse one SDK task event dict into a typed record and update the
        per-task high-water state. Malformed/unknown events fail to unknown."""
        now = now_utc_iso or to_utc_iso()
        if not isinstance(event, dict) or not isinstance(event.get("task_id"), str):
            return TelemetryRecord(
                record_type="sdk_task_event", timestamp_utc=now,
                measurements={"sdk_task_total_tokens": Measurement.unknown(
                    "cumulative", "event missing task_id or not an object")},
                attributes={"event_error": type(event).__name__})
        task_id = event["task_id"]
        etype = str(event.get("type", ""))
        state = self._tasks.setdefault(task_id, {
            "high_water": {}, "regressions": 0, "duplicates": 0,
            "completed": False})

        measurements: dict[str, Measurement] = {}
        attributes: dict[str, Any] = {"event_type": etype or "<missing>"}

        if etype == "task_progress":
            for field, name in (("total_tokens", "sdk_task_total_tokens"),
                                ("tool_uses", "sdk_task_tool_uses"),
                                ("duration_ms", "sdk_task_duration_ms")):
                clean = _clean(event.get(field))
                if clean is None:
                    measurements[name] = Measurement.unknown(
                        "cumulative", f"{field} absent or malformed")
                    continue
                previous = state["high_water"].get(name)
                if previous is not None and clean == previous:
                    state["duplicates"] += 1
                elif previous is not None and clean < previous:
                    # a lower total is a reset/regression, never "fresh"
                    state["regressions"] += 1
                    clean = previous
                else:
                    state["high_water"][name] = clean
                measurements[name] = Measurement(
                    value=state["high_water"].get(name, clean),
                    label="sdk-task-cumulative", category="cumulative",
                    detail="per-task cumulative from SDK progress feed "
                           "(high-water; regressions never lower it)")
            for key in ("description", "last_tool_name"):
                if event.get(key) is not None:
                    attributes[key] = event[key]
        elif etype in ("task_completed", "task_failed", "task_stopped"):
            state["completed"] = True
            attributes["outcome"] = etype
            usage = event.get("usage")
            if isinstance(usage, dict):
                for field, name in (("input_tokens", "final_request_input_tokens"),
                                    ("output_tokens", "final_request_output_tokens")):
                    clean = _clean(usage.get(field))
                    measurements[name] = (
                        Measurement.unknown("cumulative",
                                            f"{field} absent or malformed")
                        if clean is None else
                        Measurement(value=clean, label="sdk-cumulative",
                                    category="cumulative",
                                    detail="FINAL API request only - never "
                                           "assumed to describe the whole "
                                           "subagent run (D-024 R043)"))
            # cumulative truth stays with the progress high-water, out of
            # order or not:
            high = state["high_water"].get("sdk_task_total_tokens")
            measurements["sdk_task_total_tokens"] = (
                Measurement.unknown("cumulative",
                                    "no progress event observed for this task")
                if high is None else
                Measurement(value=high, label="sdk-task-cumulative",
                            category="cumulative",
                            detail="per-task cumulative high-water at "
                                   "completion (survives out-of-order events)"))
        elif etype == "task_started":
            for key in ("description", "agent_type", "model"):
                if event.get(key) is not None:
                    attributes[key] = event[key]
        else:
            attributes["known"] = False
            measurements["sdk_task_total_tokens"] = Measurement.unknown(
                "cumulative", f"unknown SDK event type {etype!r}")

        attributes["duplicates"] = state["duplicates"]
        attributes["regressions"] = state["regressions"]
        return TelemetryRecord(
            record_type="sdk_task_event", timestamp_utc=now,
            task_id=task_id, measurements=measurements, attributes=attributes)

    def high_water(self, task_id: str) -> dict[str, Any]:
        state = self._tasks.get(task_id)
        return dict(state["high_water"]) if state else {}
