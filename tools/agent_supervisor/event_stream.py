"""Stream-JSON subagent-event ingestion (D-024 Amendment 3 unit D, M0-T105;
R154/R042/R043).

Parses ``--output-format stream-json`` / ``--forward-subagent-text`` events
into the SAME typed `TelemetryRecord` currency the rest of the telemetry
subsystem speaks, consumed OUTSIDE Fable's context (R154: the controller
observes structured feeds; it never asks the model for status). This module
is passive parsing only: no sidecar write, no model message, no prompt
composition -- the statusLine/subagentStatusLine sidecar remains the PRIMARY
feed and is untouched here (R154; scenario S3).

Honesty rules carried from the accepted telemetry modules:

* every usage number is a labelled `Measurement` (R042); a missing number is
  ``unknown``, never zero;
* a ``result`` event's usage is recorded under ``final_request_*`` names with
  an explicit R043 caveat -- it may describe ONLY the final API request and
  is never asserted to be the whole subagent run;
* forwarded subagent text is stored as a digest reference (length + sha256),
  never verbatim (D-024 s5.3: summaries and references, not transcripts);
* a malformed line raises the typed `StreamEventError` -- a parse failure is
  never mistaken for an empty stream, and unknown event ``type`` values are
  recorded honestly (``known_type: false``), never dropped or guessed.

Supervisor-freeze qualifying evidence: D-024-R154 + D-024-R173.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .models import to_utc_iso
from .telemetry_records import Measurement, TelemetryRecord

#: Stream event ``type`` values with measured/observed handling in this repo
#: (`claude_runner` stdio probes + shadow pilots). Anything else is recorded
#: with ``known_type: false`` -- a newer CLI adding event types must not
#: crash or be guessed at (mirrors `telemetry_hooks.KNOWN_HOOK_EVENTS`).
KNOWN_STREAM_TYPES = (
    "system", "assistant", "user", "result", "rate_limit_event",
    "stream_event", "agent_text",
)

#: Identity/context fields preserved as attributes when present (no free-form
#: content; text is reduced to a digest reference below).
_EVENT_ATTRIBUTES = ("type", "subtype", "session_id", "uuid",
                     "parent_tool_use_id", "agent_id", "agent_type", "model",
                     "is_error", "num_turns")

#: A single stream line larger than this is malformed, not data (same bound
#: as `claude_runner.ClaudeStreamParser`).
MAX_LINE_BYTES = 4_194_304


class StreamEventError(ValueError):
    """A stream-JSON line/event violated the ingestion contract (typed --
    callers keep the statusLine sidecar primary and surface the failure)."""


def parse_stream_json_line(line: str) -> dict[str, Any] | None:
    """One stream-JSON line -> event dict; blank lines are ``None``.

    Tolerates a BOM and CRLF (the measured CLI output shapes). Anything that
    is not one JSON object raises `StreamEventError` -- typed, never a silent
    skip (scenario S3): the durable event path must not quietly drop what it
    cannot read.
    """
    if not isinstance(line, str):
        raise StreamEventError(
            f"stream line must be str, got {type(line).__name__}")
    text = line.lstrip(chr(0xFEFF)).strip("\r").strip()
    if not text:
        return None
    if len(text.encode("utf-8", "replace")) > MAX_LINE_BYTES:
        raise StreamEventError(
            f"stream line exceeds {MAX_LINE_BYTES} bytes; refusing to parse")
    try:
        event = json.loads(text)
    except json.JSONDecodeError as exc:
        raise StreamEventError(f"stream line is not valid JSON: {exc}") from exc
    if not isinstance(event, dict):
        raise StreamEventError(
            f"stream line must hold a JSON object, got {type(event).__name__}")
    return event


def stream_idempotency_key(event: Mapping[str, Any]) -> str:
    """Dedup key: the event's own id (``uuid``/``message.id``) when present,
    else a canonical-content digest (identical re-delivery collapses)."""
    identity: dict[str, Any] = {"kind": "stream_json"}
    uuid = event.get("uuid")
    if isinstance(uuid, str) and uuid:
        identity["uuid"] = uuid
    message = event.get("message")
    if isinstance(message, Mapping):
        message_id = message.get("id")
        if isinstance(message_id, str) and message_id:
            identity["message_id"] = message_id
    if len(identity) == 1:
        canonical = json.dumps(dict(event), sort_keys=True, ensure_ascii=False,
                               default=repr)
        identity["content_sha256"] = hashlib.sha256(
            canonical.encode("utf-8", "replace")).hexdigest()
    blob = json.dumps(identity, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _event_text(event: Mapping[str, Any]) -> str:
    """The human-readable text an event carries (result text, message blocks,
    forwarded subagent text) -- extracted only to be digested, never stored."""
    parts: list[str] = []
    for key in ("result", "text"):
        value = event.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    message = event.get("message")
    if isinstance(message, Mapping):
        content = message.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, Mapping) and isinstance(block.get("text"), str):
                    parts.append(block["text"])
    return "\n".join(parts)


def _event_usage(event: Mapping[str, Any]) -> Mapping[str, Any] | None:
    usage = event.get("usage")
    if isinstance(usage, Mapping):
        return usage
    message = event.get("message")
    if isinstance(message, Mapping):
        nested = message.get("usage")
        if isinstance(nested, Mapping):
            return nested
    return None


def _count(usage: Mapping[str, Any], field: str) -> int | float | None:
    value = usage.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        return None
    return value


def _step_measurements(usage: Mapping[str, Any] | None) -> dict[str, Measurement]:
    """Per-step assistant usage -> ``step_*`` (provider-exact; R042)."""
    fields = (("input_tokens", "step_input_tokens"),
              ("output_tokens", "step_output_tokens"),
              ("cache_creation_input_tokens", "step_cache_creation_tokens"),
              ("cache_read_input_tokens", "step_cache_read_tokens"))
    out: dict[str, Measurement] = {}
    for field, name in fields:
        clean = _count(usage, field) if usage is not None else None
        if clean is None:
            out[name] = Measurement.unknown(
                "cumulative", f"{field} absent or malformed in stream usage")
        else:
            out[name] = Measurement(
                value=clean, label="provider-exact", category="cumulative",
                detail="single stream-json assistant step, not a running total")
    return out


def _result_measurements(usage: Mapping[str, Any] | None) -> dict[str, Measurement]:
    """Result-event usage -> ``final_request_*`` with the R043 caveat."""
    caveat = ("result-event usage; may describe only the final API request, "
              "never asserted as the whole subagent run (D-024 R043)")
    fields = (("input_tokens", "final_request_input_tokens"),
              ("output_tokens", "final_request_output_tokens"),
              ("total_tokens", "final_request_total_tokens"))
    out: dict[str, Measurement] = {}
    for field, name in fields:
        clean = _count(usage, field) if usage is not None else None
        if clean is None:
            out[name] = Measurement.unknown(
                "cumulative", f"{field} absent in result usage; unknown, never zero")
        else:
            out[name] = Measurement(
                value=clean, label="sdk-cumulative", category="cumulative",
                detail=caveat)
    return out


def ingest_stream_event(event: Mapping[str, Any], *,
                        now_utc_iso: str | None = None) -> TelemetryRecord:
    """One typed record per stream-JSON event (identity + labelled usage).

    ``task_id`` carries the subagent attribution (``parent_tool_use_id``,
    else ``agent_id``) so bus replay can correlate subagent activity without
    any transcript polling (R154).
    """
    if not isinstance(event, Mapping):
        raise StreamEventError(
            f"stream event must be a mapping, got {type(event).__name__}")
    now = now_utc_iso or to_utc_iso()
    event_type = event.get("type")
    event_type = event_type if isinstance(event_type, str) else ""
    attributes: dict[str, Any] = {
        "known_type": event_type in KNOWN_STREAM_TYPES,
    }
    for key in _EVENT_ATTRIBUTES:
        value = event.get(key)
        if value is not None:
            attributes[key] = value
    message = event.get("message")
    if isinstance(message, Mapping):
        for key in ("id", "model"):
            value = message.get(key)
            if isinstance(value, str) and value:
                attributes[f"message_{key}"] = value
    text = _event_text(event)
    if text:
        # reference, never content (s5.3): enough to correlate forwarded
        # subagent text without persisting a transcript
        attributes["text_chars"] = len(text)
        attributes["text_sha256"] = hashlib.sha256(
            text.encode("utf-8", "replace")).hexdigest()
    measurements: dict[str, Measurement] = {}
    if event_type == "assistant":
        measurements = _step_measurements(_event_usage(event))
    elif event_type == "result":
        measurements = _result_measurements(_event_usage(event))
    session = event.get("session_id")
    parent = event.get("parent_tool_use_id")
    agent_id = event.get("agent_id")
    task = parent if isinstance(parent, str) and parent else (
        agent_id if isinstance(agent_id, str) and agent_id else "")
    return TelemetryRecord(
        record_type="subagent_stream_event", timestamp_utc=now,
        session_id=session if isinstance(session, str) else "",
        task_id=task, measurements=measurements, attributes=attributes)
