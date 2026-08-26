"""Project statusLine handler — ONE feed for the sanitized sidecar and the
compact human status row (D-024 amendment 2, M0-T099; R129–R138).

Official contract (PRIMARY capability evidence, D-024-R129):
https://code.claude.com/docs/en/statusline — Claude Code invokes the
configured ``statusLine`` command with the main-session status JSON on stdin;
the command's stdout becomes the status row. Official note, verbatim: "The
status line runs locally and does not consume API tokens." This handler adds
no model messages, composes no prompts, and opens no network connection
(R135); it parses stdin, persists ONE sanitized record, prints ONE row.

One feed (R132): the SAME ingested record drives both outputs — the atomic
sanitized sidecar (Codex/controller monitoring reads it via
``telemetry_status.read_only_status``) and the human row — so owner
visibility and machine monitoring can never disagree by configuration.

Axis separation in the row (R133/R134): the ``ctx`` segment holds ONLY live
context occupancy (``context_window.*`` — the most recent API response, never
lifetime spend); the ``sess`` segment holds ONLY session-cumulative facts
(``cost.*``); the ``5h``/``7d`` segment holds ONLY rate-limit pressure
(``rate_limits.*.used_percentage`` — account pressure, not context pressure).
Segments never borrow each other's numbers; an unknown renders as ``?``,
never as zero (R136 via ``ingest_status_line``: absent becomes unknown, a
reported zero stays zero).

Live wiring into ``.claude/settings.json`` is an owner-visible step that this
module only documents (see ``project-control/reports/M0-T099-statusline-handler.md``);
nothing here reads or writes any settings file. Reuses the accepted M0-T088
records/sanitization/sidecar/journal — no rebuild (R130).

Supervisor-freeze qualifying evidence: D-024-R100 + D-024-R131/R132.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import IO, Any

from .telemetry_ingest import ingest_status_line
from .telemetry_journal import TelemetryJournal, TelemetrySidecar
from .telemetry_records import Measurement, TelemetryRecord

#: Default sidecar location, relative to the status-line process working
#: directory (the session's project directory). Runtime-local state — never a
#: committed artifact; the wiring doc tells the owner to keep it ignored.
DEFAULT_SIDECAR_PATH = ".claude/telemetry/statusline_sidecar.json"

_UNKNOWN = "?"


def parse_payload(text: str) -> Any:
    """Decode the stdin JSON; unparseable input is ``None`` (fail to unknown,
    never crash — the ingest layer turns a non-dict into an all-unknown
    record, so even a torn payload still refreshes the one feed)."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _fmt_pct(value: int | float | None) -> str:
    """Whole-percent display; a missing number is ``?``, never 0."""
    if value is None:
        return _UNKNOWN
    return f"{round(value)}%"


def _fmt_tokens(value: int | float | None) -> str:
    if value is None:
        return _UNKNOWN
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(int(value))


def _measurement_value(record: TelemetryRecord, name: str) -> int | float | None:
    m = record.measurements.get(name)
    if isinstance(m, Measurement) and not m.is_unknown:
        return m.value
    return None


def _model_segment(payload: Any) -> str:
    model = payload.get("model") if isinstance(payload, dict) else None
    model = model if isinstance(model, dict) else {}
    name = model.get("display_name")
    if not isinstance(name, str) or not name:
        return f"model {_UNKNOWN}"
    effort = payload.get("effort") if isinstance(payload, dict) else None
    effort = effort if isinstance(effort, dict) else {}
    level = effort.get("level")
    if isinstance(level, str) and level:
        # effort is absent when the model lacks the parameter (documented) —
        # shown only when the feed reports it
        return f"{name} {level}"
    return name


def _context_segment(record: TelemetryRecord) -> str:
    """Occupancy axis ONLY (R133): live context, never lifetime spend."""
    used_pct = _measurement_value(record, "context_used_pct")
    window = _measurement_value(record, "context_window_tokens")
    out = f"ctx {_fmt_pct(used_pct)}"
    if window is not None:
        out += f" of {_fmt_tokens(window)}"
    return out


def _session_segment(record: TelemetryRecord) -> str:
    """Session-cumulative axis ONLY (R133): cost.* facts, never occupancy."""
    cost = _measurement_value(record, "cumulative_cost_usd")
    duration_ms = _measurement_value(record, "cumulative_duration_ms")
    parts = []
    if cost is not None:
        parts.append(f"${cost:.2f}")
    if duration_ms is not None:
        parts.append(f"{round(duration_ms / 60_000)}m")
    return "sess " + (" ".join(parts) if parts else _UNKNOWN)


def _rate_limit_segment(record: TelemetryRecord) -> str:
    """Rate-limit pressure axis ONLY (R134): account windows, never context.

    Each window is independently absent (subscribers only, and only after the
    first API response — documented nullability); absent windows are omitted,
    and a wholly absent block renders ``limits ?`` rather than 0.
    """
    limits = record.attributes.get("rate_limits")
    limits = limits if isinstance(limits, dict) else {}
    parts = []
    for key, tag in (("five_hour", "5h"), ("seven_day", "7d")):
        window = limits.get(key)
        if not isinstance(window, dict):
            continue
        used = window.get("used_percentage")
        if isinstance(used, bool) or not isinstance(used, (int, float)):
            continue
        parts.append(f"{tag} {_fmt_pct(used)}")
    return " ".join(parts) if parts else f"limits {_UNKNOWN}"


def format_status_row(record: TelemetryRecord, payload: Any) -> str:
    """Compact ASCII row from the ONE ingested record (plus identity strings
    read from the same payload). No paths, no session ids, no secrets — the
    row is displayable/screenshottable without leaking the workstation."""
    segments = [
        _model_segment(payload),
        _context_segment(record),
        _session_segment(record),
        _rate_limit_segment(record),
    ]
    version = payload.get("version") if isinstance(payload, dict) else None
    if isinstance(version, str) and version:
        segments.append(f"v{version}")
    return " | ".join(segments)


def handle_status_line(payload: Any, *, sidecar: TelemetrySidecar,
                       journal: TelemetryJournal | None = None,
                       now_utc_iso: str | None = None,
                       ) -> tuple[TelemetryRecord, dict[str, Any], str]:
    """Ingest one payload; persist sanitized; return (record, stored, row).

    The sidecar write happens BEFORE the row is returned so a displayed row
    always has a persisted counterpart (one feed, R132). Both persistence
    surfaces sanitize-first (M0-T088 journal/sidecar — reused, not rebuilt).
    """
    record = ingest_status_line(payload, now_utc_iso=now_utc_iso)
    stored = sidecar.update(record)
    if journal is not None:
        journal.append(record)
    return record, stored, format_status_row(record, payload)


def main(argv: list[str] | None = None, *, stdin: IO[str] | None = None,
         stdout: IO[str] | None = None) -> int:
    """CLI entry point for the statusLine command wiring.

    Always exits 0 with SOME row on stdout: a status line must degrade, never
    crash the display. Errors surface as a ``telemetry ?`` row naming only
    the exception type (no message text — messages can carry paths)."""
    parser = argparse.ArgumentParser(
        description="Claude Code statusLine handler: sanitized sidecar + "
                    "compact human row from one feed (shadow telemetry; "
                    "no model messages, no API tokens)")
    parser.add_argument("--sidecar", default=DEFAULT_SIDECAR_PATH,
                        help="sidecar JSON path (atomic, sanitized)")
    parser.add_argument("--journal", default=None,
                        help="optional JSONL journal path (bounded, rotated)")
    args = parser.parse_args(argv)
    in_stream = stdin if stdin is not None else sys.stdin
    out_stream = stdout if stdout is not None else sys.stdout
    try:
        payload = parse_payload(in_stream.read())
        # journal fsync off: this runs on every refresh tick; the journal's
        # read path tolerates (skips + counts) a torn final line by design
        journal = (TelemetryJournal(args.journal, fsync=False)
                   if args.journal else None)
        _record, _stored, row = handle_status_line(
            payload, sidecar=TelemetrySidecar(args.sidecar), journal=journal)
    except Exception as exc:  # noqa: BLE001 - display must never crash
        row = f"telemetry {_UNKNOWN} (handler error: {type(exc).__name__})"
    out_stream.write(row + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
