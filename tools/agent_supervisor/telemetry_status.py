"""Read-only shadow telemetry status (D-024 Phase B item 8, M0-T089).

Assembles what the passive pipeline has recorded — sidecar snapshots, journal
tail, subagent registry — into one read-only status structure. ACTUATION IS
OFF: nothing here pauses, messages, spawns, stops, or steers anything; it
performs no repository writes and no model-context injection. It exists so an
operator (or a later, owner-activated controller) can SEE the shadow
measurements.

Manual-diagnostic comparison (D-024 Phase B item 9): `compare_with_manual`
is an OPT-IN test/canary diagnostic that diffs a pipeline record against a
manually collected status payload. It is never called on a schedule and never
prompts the model — comparisons happen in tests and bounded canaries only.

Usage (read-only):
    python -m tools.agent_supervisor.telemetry_status --sidecar FILE [...]

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .models import to_utc_iso
from .telemetry_ingest import ingest_status_line
from .telemetry_journal import TelemetryJournal, TelemetrySidecar


def read_only_status(*, sidecar_paths: dict[str, str] | None = None,
                     journal_path: str | None = None,
                     journal_tail: int = 20,
                     now_utc_iso: str | None = None) -> dict[str, Any]:
    """Assemble the current shadow-telemetry picture from stored artifacts.

    Missing/unreadable artifacts report as ``null`` (unknown), never as zero
    and never as an error — absence of telemetry is itself a finding.
    """
    if journal_tail < 0:
        raise ValueError("journal_tail must be >= 0")
    status: dict[str, Any] = {
        "schema": "telemetry_shadow_status/v1",
        "generated_at": now_utc_iso or to_utc_iso(),
        "actuation": "off (shadow mode; D-024 15-B item 8)",
        "sidecars": {},
        "journal": None,
    }
    for name, path in (sidecar_paths or {}).items():
        status["sidecars"][name] = TelemetrySidecar(path).read()
    if journal_path is not None:
        journal = TelemetryJournal(journal_path)
        result = journal.read_all()
        records = list(result.records)
        status["journal"] = {
            "records_total": len(records),
            "skipped_lines": result.skipped_lines,
            "tail": records[-journal_tail:] if journal_tail else [],
        }
    return status


def compare_with_manual(pipeline_record: Any, manual_payload: Any,
                        *, now_utc_iso: str | None = None) -> dict[str, Any]:
    """OPT-IN diagnostic: diff a pipeline status record against a manually
    collected status payload (tests/canaries only — never scheduled, never a
    prompt). Returns per-measurement agreement; disagreement is a report, not
    an exception (calibration data, not a crash)."""
    manual = ingest_status_line(manual_payload, now_utc_iso=now_utc_iso)
    fields: dict[str, Any] = {}
    pipe_measurements = getattr(pipeline_record, "measurements", {}) or {}
    for name, manual_m in manual.measurements.items():
        pipe_m = pipe_measurements.get(name)
        fields[name] = {
            "pipeline": pipe_m.to_dict() if pipe_m is not None else None,
            "manual": manual_m.to_dict(),
            "agree": (pipe_m is not None
                      and pipe_m.value == manual_m.value
                      and pipe_m.is_unknown == manual_m.is_unknown),
        }
    return {
        "schema": "telemetry_manual_comparison/v1",
        "generated_at": now_utc_iso or to_utc_iso(),
        "note": "opt-in test/canary diagnostic (D-024 15-B item 9); never a "
                "scheduled probe, never a model prompt",
        "fields": fields,
        "all_agree": all(f["agree"] for f in fields.values()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only shadow telemetry status (actuation off)")
    parser.add_argument("--sidecar", action="append", default=[],
                        metavar="NAME=PATH",
                        help="named sidecar file to include (repeatable)")
    parser.add_argument("--journal", default=None, help="journal JSONL path")
    parser.add_argument("--tail", type=int, default=20,
                        help="journal tail records to include")
    args = parser.parse_args(argv)
    sidecars: dict[str, str] = {}
    for item in args.sidecar:
        name, sep, path = item.partition("=")
        if not sep or not name or not path:
            parser.error(f"--sidecar expects NAME=PATH, got {item!r}")
        sidecars[name] = path
    status = read_only_status(sidecar_paths=sidecars,
                              journal_path=args.journal,
                              journal_tail=args.tail)
    sys.stdout.write(json.dumps(status, indent=1, ensure_ascii=False,
                                sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
