"""subagentStatusLine ingestion (D-024 Phase B item 3, M0-T089).

The Claude Code ``subagentStatusLine`` command runs once per refresh tick and
receives ALL visible subagent rows as ONE JSON object: base status fields plus
a ``tasks`` array; each task row carries (where the installed version supports
it) ``id``, ``name``, ``type``, ``status``, ``description``, ``label``,
``startTime``, ``model``, ``effort``, ``contextWindowSize``, ``tokenCount``,
``tokenSamples``, ``cwd`` — captured at official-docs confidence in
``fixtures/capability_matrix_v1.json`` (``claude.subagentStatusLine``).

Feature-detection duties (D-024 s5.1 item 2):

* ``model`` and ``contextWindowSize`` require >= 2.1.205 and are OMITTED until
  the task's model resolves — absence is normal, never an error;
* ``tokenCount``/``contextWindowSize`` may be absent on older versions —
  a missing count ingests as ``unknown``, never zero;
* ``tokenCount`` is paired with ``contextWindowSize`` in the documented feed
  (the task's live context view), so it records as OCCUPANCY under the
  ``subagent-status-live`` label;
* ``tokenSamples`` is a TREND-ONLY signal until installed-version fixtures
  establish its exact semantics — it is preserved raw in attributes and NEVER
  interpreted into a measurement (do not invent undocumented meaning).

Everything here is passive parsing: no model-context injection, no worker
messages. The refresh path must stay fast — pair with
``telemetry_journal.TelemetrySidecar`` for the atomic bounded sidecar update.

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

from typing import Any

from .models import to_utc_iso
from .telemetry_records import Measurement, TelemetryRecord

#: Task-row string fields preserved as attributes when present (feature-detected).
_ROW_ATTRIBUTES = ("name", "type", "status", "description", "label",
                   "startTime", "model", "effort", "cwd")


def _count_measurement(value: Any, name_detail: str,
                       detail: str) -> Measurement:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        return Measurement.unknown(
            "occupancy",
            f"{name_detail} absent or malformed (normal before model "
            f"resolution and on versions older than 2.1.205)")
    return Measurement(value=value, label="subagent-status-live",
                       category="occupancy", detail=detail)


def ingest_subagent_status(payload: Any, *,
                           now_utc_iso: str | None = None
                           ) -> list[TelemetryRecord]:
    """Typed records for one refresh tick: one record per visible task row.

    A payload that is not an object, or whose ``tasks`` is missing/malformed,
    produces a single all-unknown record (fail to unknown, never invent).
    Every task-row field is optional; unknown extra fields are ignored.
    """
    now = now_utc_iso or to_utc_iso()
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        return [TelemetryRecord(
            record_type="subagent_status", timestamp_utc=now,
            measurements={"subagent_token_count": Measurement.unknown(
                "occupancy", "subagentStatusLine payload missing or malformed")},
            attributes={"payload_error": f"expected object with tasks[], got "
                                         f"{type(payload).__name__}"})]

    session = payload.get("session_id")
    records: list[TelemetryRecord] = []
    for row in payload["tasks"]:
        if not isinstance(row, dict):
            records.append(TelemetryRecord(
                record_type="subagent_status", timestamp_utc=now,
                session_id=session if isinstance(session, str) else "",
                measurements={"subagent_token_count": Measurement.unknown(
                    "occupancy", "task row is not an object")},
                attributes={"row_error": type(row).__name__}))
            continue
        task_id = row.get("id")
        attributes: dict[str, Any] = {}
        for key in _ROW_ATTRIBUTES:
            value = row.get(key)
            if value is not None:
                attributes[key] = value
        samples = row.get("tokenSamples")
        if isinstance(samples, list):
            # trend-only: preserved raw, never interpreted (D-024 s5.1 item 2)
            attributes["tokenSamples"] = samples
            attributes["tokenSamples_note"] = (
                "trend signal only; exact semantics await installed-version "
                "fixtures - never interpreted into a measurement")
        records.append(TelemetryRecord(
            record_type="subagent_status", timestamp_utc=now,
            session_id=session if isinstance(session, str) else "",
            task_id=task_id if isinstance(task_id, str) else "",
            measurements={
                "subagent_token_count": _count_measurement(
                    row.get("tokenCount"), "tokenCount",
                    "documented pairing with contextWindowSize: the task's "
                    "live context view, not lifetime spend"),
                # M0-T089 G3 nit#4 carried fix: the window is the denominator
                # of the live view, not "paired with itself"
                "subagent_context_window_tokens": _count_measurement(
                    row.get("contextWindowSize"), "contextWindowSize",
                    "the task's context-window size - denominator of the "
                    "live view, not lifetime spend"),
            },
            attributes=attributes))
    if not records:
        records.append(TelemetryRecord(
            record_type="subagent_status", timestamp_utc=now,
            session_id=session if isinstance(session, str) else "",
            measurements={"subagent_token_count": Measurement.unknown(
                "occupancy", "no visible subagent tasks this tick")},
            attributes={"tasks": 0}))
    return records


def sidecar_snapshot(records: list[TelemetryRecord], *,
                     now_utc_iso: str | None = None) -> dict[str, Any]:
    """Compact latest-tick snapshot for the atomic sidecar (fast extraction).

    Holds only the required fields per row — the sidecar is a bounded compact
    external record (s5.3), not an archive; history belongs to the journal.
    """
    now = now_utc_iso or to_utc_iso()
    rows = []
    for rec in records:
        if rec.record_type != "subagent_status":
            continue
        token = rec.measurements.get("subagent_token_count")
        window = rec.measurements.get("subagent_context_window_tokens")
        rows.append({
            "task_id": rec.task_id,
            "status": rec.attributes.get("status"),
            "model": rec.attributes.get("model"),
            "token_count": token.to_dict() if token else None,
            "context_window": window.to_dict() if window else None,
        })
    return {"schema": "subagent_sidecar/v1", "updated_at": now, "tasks": rows}
