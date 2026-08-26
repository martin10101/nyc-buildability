"""Version-probed, read-only transcript derivation — the feature-detected
FALLBACK evidence source (D-024 Phase B item 7 / s5.1 item 6, M0-T089).

Used ONLY when the supported progress/status feeds do not expose a required
fact. Parses shapes proven on the installed runtime (measured live on Claude
Code 2.1.220 transcripts, 2026-08-25):

* assistant lines: ``{"type": "assistant", "message": {"id": ..., "usage":
  {"input_tokens", "output_tokens", "cache_creation_input_tokens",
  "cache_read_input_tokens", ...}}}`` — per-step usage keyed by message id;
* compact boundaries: ``{"type": "system", "subtype": "compact_boundary",
  "compactMetadata": {"preTokens", "postTokens", "cumulativeDroppedTokens",
  "trigger", ...}, "sessionId": ...}``;
* every line carries ``sessionId`` — a transcript spanning several session ids
  is a resumed session.

Duties (16.1): tolerate fragmentation (torn lines skip+count), duplicates
(message-id dedup), unknown line types (counted, never guessed); fail to
``unknown`` rather than invent; track multiple compactions and resumption;
label everything ``transcript-derived``. Reading is strictly read-only —
this module NEVER writes into a transcript, the conversation, or a worker.

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

import json
from typing import Any, Iterable

from .models import to_utc_iso
from .telemetry_ingest import UsageAccumulator
from .telemetry_records import Measurement, TelemetryRecord

#: Map from the accumulator's cumulative_* sum names to transcript-derived
#: measurement names (same order as the underlying usage fields).
_SUM_TO_TRANSCRIPT = (
    ("cumulative_input_tokens", "transcript_input_tokens"),
    ("cumulative_output_tokens", "transcript_output_tokens"),
    ("cumulative_cache_creation_tokens", "transcript_cache_creation_tokens"),
    ("cumulative_cache_read_tokens", "transcript_cache_read_tokens"),
)

#: Accumulator bounds (M0-T089 G5-M2 carried fix): an adversarially shaped
#: transcript with millions of boundary/unknown-type lines can no longer grow
#: the per-derivation state without bound. Totals stay EXACT (they are counted
#: incrementally); only the retained detail entries are capped, and every cap
#: crossing is counted, never silent.
MAX_COMPACTION_DETAILS = 256
MAX_SESSION_IDS = 64
MAX_UNKNOWN_TYPE_KEYS = 64
_UNKNOWN_TYPE_OVERFLOW_KEY = "<other>"


def _narrow_count(value: Any) -> int | float | None:
    """A usable non-negative number or None (bools are not token counts)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if value >= 0 else None


def derive_from_transcript_lines(lines: Iterable[str], *,
                                 runtime_version: str = "",
                                 now_utc_iso: str | None = None
                                 ) -> TelemetryRecord:
    """Conservative usage derivation over raw transcript JSONL lines.

    ``runtime_version`` records which installed version's fixture-proven
    shapes the caller believes apply; it is provenance, not a behavior switch —
    unknown shapes are skipped and counted regardless.
    """
    now = now_utc_iso or to_utc_iso()
    acc = UsageAccumulator(step_label="transcript-derived")
    torn = 0
    unknown_types: dict[str, int] = {}
    compactions: list[dict[str, Any]] = []
    compaction_total = 0
    compactions_truncated = 0
    pre_tokens_sum: int | float = 0
    pre_tokens_seen = 0
    session_ids: list[str] = []
    session_id_overflow_events = 0

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            torn += 1
            continue
        if not isinstance(obj, dict):
            torn += 1
            continue
        sid = obj.get("sessionId")
        if isinstance(sid, str) and sid and sid not in session_ids:
            if len(session_ids) < MAX_SESSION_IDS:
                session_ids.append(sid)
            else:
                # beyond the cap dropped ids cannot be re-distinguished, so
                # this counts EVENTS (a lower bound of at least one more id)
                session_id_overflow_events += 1
        ltype = obj.get("type")
        if ltype == "assistant":
            message = obj.get("message")
            if isinstance(message, dict):
                acc.ingest_step(message.get("id"), message.get("usage"),
                                now_utc_iso=now)
            else:
                torn += 1
        elif ltype == "system" and obj.get("subtype") == "compact_boundary":
            meta = obj.get("compactMetadata")
            meta = meta if isinstance(meta, dict) else {}
            compaction_total += 1
            pre = _narrow_count(meta.get("preTokens"))
            if pre is not None:
                pre_tokens_sum += pre
                pre_tokens_seen += 1
            trigger = meta.get("trigger")
            if len(compactions) < MAX_COMPACTION_DETAILS:
                compactions.append({
                    "pre_tokens": pre,
                    # M0-T089 G5-N2 carried fix: postTokens narrowed exactly
                    # like preTokens; trigger stored only as a string
                    "post_tokens": _narrow_count(meta.get("postTokens")),
                    "trigger": trigger if isinstance(trigger, str) else None,
                })
            else:
                compactions_truncated += 1
        else:
            key = str(ltype)
            if key in unknown_types or len(unknown_types) < MAX_UNKNOWN_TYPE_KEYS:
                unknown_types[key] = unknown_types.get(key, 0) + 1
            else:
                unknown_types[_UNKNOWN_TYPE_OVERFLOW_KEY] = (
                    unknown_types.get(_UNKNOWN_TYPE_OVERFLOW_KEY, 0) + 1)

    snap = acc.snapshot(now_utc_iso=now)
    measurements: dict[str, Measurement] = {}
    for sum_name, out_name in _SUM_TO_TRANSCRIPT:
        source = snap.measurements[sum_name]
        if source.is_unknown:
            measurements[out_name] = Measurement.unknown(
                "cumulative", source.detail or "no usage derivable")
        else:
            measurements[out_name] = Measurement(
                value=source.value, label="transcript-derived",
                category="cumulative",
                detail="derived from deduplicated assistant-message usage; a "
                       "conservative lower bound, not a provider statement")

    measurements["compaction_count"] = Measurement(
        value=compaction_total, label="transcript-derived",
        category="cumulative", detail="compact_boundary lines observed")
    measurements["compaction_pre_tokens_total"] = (
        Measurement.unknown(
            "cumulative",
            "no compaction observed" if not compaction_total
            else "compact boundaries present but preTokens missing/malformed")
        if not pre_tokens_seen else
        Measurement(value=pre_tokens_sum, label="transcript-derived",
                    category="cumulative",
                    detail="sum of compactMetadata.preTokens at boundaries - "
                           "context spent before each compaction"))

    return TelemetryRecord(
        record_type="transcript_derivation", timestamp_utc=now,
        session_id=session_ids[0] if session_ids else "",
        measurements=measurements,
        attributes={
            "runtime_version": runtime_version,
            "torn_or_malformed_lines": torn,
            "unknown_line_types": unknown_types,
            "session_ids_seen": len(session_ids),
            "session_id_overflow_events": session_id_overflow_events,
            "resumed_session": len(session_ids) > 1,
            "duplicates_ignored": acc.duplicates_ignored,
            "compactions": compactions,
            "compactions_truncated": compactions_truncated,
        })
