"""Durable campaign continuity for the D-024 implementation loop (M0-T087).

One-prompt continuity (D-024 sections 1, 15-A item 7, 16.9): after the owner's
single captured directive, successor primary sessions must continue the
implementation campaign from durable repository state alone - no owner
re-prompting, no reliance on a dead conversation.

This module owns the CAMPAIGN RECORD: one small JSON file per campaign under
``project-control/campaigns/`` naming the campaign's authority (the captured
directive and its source digest), its state, the ledger lineage, the frozen git
identity last verified, the standing restrictions a successor must honor, and -
the load-bearing field - the exact next bounded action.

Design rules:

* **Fail closed.** A missing, malformed, schema-mismatched, or vocabulary-
  violating record raises :class:`CampaignRecordError`; callers must treat that
  as "orientation unavailable - reconcile manually", never as an empty campaign.
* **Exact-once advance.** Every mutation carries a monotonic ``sequence``; a
  writer must present the sequence it read. Two successors racing from the same
  snapshot cannot both win (the loser gets a :class:`SequenceConflict`).
* **Atomic writes.** tmp-file + ``os.replace`` in the record's directory, LF
  bytes, so a crash mid-write never leaves a torn record.
* **The record is orientation, not authority.** The project-control ledger,
  git, and the captured directive remain the source of truth (D-024 section 1);
  the record points at them and is re-verifiable against them.

The record instance is orchestrator-authored control-plane state (like
``project-control/state.json``); this module supplies the schema, validation,
exact-once mutation, and a read-only status entry point::

    python -m tools.agent_supervisor.campaign_continuity --status

Supervisor-freeze qualifying evidence: D-024-R099 (Phase A item 7, explicitly
listed in owner directive D-024).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "campaign_continuity/v1"
STATES = ("active", "paused", "blocked", "complete")
DEFAULT_DIR = Path("project-control") / "campaigns"

REQUIRED_FIELDS = (
    "schema", "campaign_id", "directive_id", "state", "control_branch",
    "ledger_lineage_base", "authority", "restrictions", "next_action",
    "frozen", "sequence", "updated_at",
)
NEXT_ACTION_FIELDS = ("task_id", "description")
FROZEN_FIELDS = ("head_sha", "recorded_at")


class CampaignRecordError(ValueError):
    """The campaign record is missing, malformed, or fails validation."""


class SequenceConflict(CampaignRecordError):
    """A writer presented a stale sequence; exactly one racer may advance."""


@dataclass
class CampaignRecord:
    campaign_id: str
    directive_id: str
    state: str
    control_branch: str
    ledger_lineage_base: str
    authority: str
    next_action: dict
    frozen: dict
    restrictions: list = field(default_factory=list)
    sequence: int = 0
    updated_at: str = ""
    schema: str = SCHEMA

    def to_dict(self) -> dict:
        return {
            "schema": self.schema,
            "campaign_id": self.campaign_id,
            "directive_id": self.directive_id,
            "state": self.state,
            "control_branch": self.control_branch,
            "ledger_lineage_base": self.ledger_lineage_base,
            "authority": self.authority,
            "restrictions": list(self.restrictions),
            "next_action": dict(self.next_action),
            "frozen": dict(self.frozen),
            "sequence": self.sequence,
            "updated_at": self.updated_at,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate(data: object) -> CampaignRecord:
    """Validate raw JSON data into a CampaignRecord; fail closed on any defect."""
    if not isinstance(data, dict):
        raise CampaignRecordError("campaign record is not a JSON object")
    missing = [k for k in REQUIRED_FIELDS if k not in data]
    if missing:
        raise CampaignRecordError(f"campaign record missing fields: {missing}")
    if data["schema"] != SCHEMA:
        raise CampaignRecordError(
            f"unsupported schema {data['schema']!r} (expected {SCHEMA})")
    if data["state"] not in STATES:
        raise CampaignRecordError(
            f"state {data['state']!r} not in {STATES} (fail closed)")
    na = data["next_action"]
    if not isinstance(na, dict) or any(not na.get(k) for k in NEXT_ACTION_FIELDS):
        raise CampaignRecordError(
            f"next_action must carry non-empty {NEXT_ACTION_FIELDS}")
    fz = data["frozen"]
    if not isinstance(fz, dict) or any(not fz.get(k) for k in FROZEN_FIELDS):
        raise CampaignRecordError(f"frozen must carry non-empty {FROZEN_FIELDS}")
    sha = fz["head_sha"]
    if not (isinstance(sha, str) and len(sha) == 40
            and all(c in "0123456789abcdef" for c in sha)):
        raise CampaignRecordError("frozen.head_sha must be a 40-hex sha")
    if not isinstance(data["sequence"], int) or data["sequence"] < 0:
        raise CampaignRecordError("sequence must be a non-negative integer")
    if not isinstance(data["restrictions"], list):
        raise CampaignRecordError("restrictions must be a list")
    return CampaignRecord(
        campaign_id=data["campaign_id"], directive_id=data["directive_id"],
        state=data["state"], control_branch=data["control_branch"],
        ledger_lineage_base=data["ledger_lineage_base"],
        authority=data["authority"], restrictions=list(data["restrictions"]),
        next_action=dict(na), frozen=dict(fz),
        sequence=data["sequence"], updated_at=data["updated_at"],
    )


def load(path: Path) -> CampaignRecord:
    """Load and validate the record at ``path``; fail closed, never guess."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CampaignRecordError(f"cannot read campaign record {path}: {exc}")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CampaignRecordError(f"campaign record {path} is malformed: {exc}")
    return validate(data)


def atomic_write(path: Path, record: CampaignRecord) -> None:
    """Write the record atomically (tmp + os.replace), LF bytes."""
    validate(record.to_dict())  # never persist an invalid record
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record.to_dict(), indent=1, ensure_ascii=False)
               + "\n").encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(payload)
    os.replace(tmp, path)


def advance(path: Path, expected_sequence: int, *, next_action: dict,
            head_sha: str, state: str = "active",
            restrictions: list | None = None) -> CampaignRecord:
    """Exact-once mutation: refuses unless ``expected_sequence`` matches disk.

    Returns the NEW persisted record. A racer that read the same snapshot and
    lost gets :class:`SequenceConflict` and must re-read and re-decide.
    """
    current = load(path)
    if current.sequence != expected_sequence:
        raise SequenceConflict(
            f"stale sequence {expected_sequence} (record is at "
            f"{current.sequence}); re-read the record and re-decide")
    updated = CampaignRecord(
        campaign_id=current.campaign_id, directive_id=current.directive_id,
        state=state, control_branch=current.control_branch,
        ledger_lineage_base=current.ledger_lineage_base,
        authority=current.authority,
        restrictions=(list(restrictions) if restrictions is not None
                      else list(current.restrictions)),
        next_action=dict(next_action),
        frozen={"head_sha": head_sha, "recorded_at": _now()},
        sequence=current.sequence + 1, updated_at=_now(),
    )
    atomic_write(path, updated)
    return updated


def staleness(record: CampaignRecord, live_head_sha: str) -> str | None:
    """None when the frozen identity matches the live HEAD; else a warning.

    A stale frozen identity is NOT an error - the ledger and git win - but a
    successor must reconcile before acting (D-024 section 1).
    """
    if record.frozen.get("head_sha") == live_head_sha:
        return None
    return (f"campaign frozen identity {record.frozen.get('head_sha', '?')[:12]} "
            f"!= live HEAD {live_head_sha[:12]}; reconcile against the ledger "
            f"and git before acting (they win)")


def orientation_summary(record: CampaignRecord) -> str:
    """Compact successor-facing orientation text (read-only surfaces)."""
    lines = [
        f"campaign {record.campaign_id} [{record.state}] "
        f"(directive {record.directive_id}; seq {record.sequence})",
        f"branch {record.control_branch} from {record.ledger_lineage_base[:12]}; "
        f"frozen {record.frozen.get('head_sha', '?')[:12]} "
        f"@ {record.frozen.get('recorded_at', '?')}",
        f"authority: {record.authority}",
        f"NEXT: [{record.next_action.get('task_id')}] "
        f"{record.next_action.get('description')}",
    ]
    for r in record.restrictions:
        lines.append(f"restriction: {r}")
    return "\n".join(lines)


def default_path(campaign_id: str, root: Path | None = None) -> Path:
    return (root or Path(".")) / DEFAULT_DIR / f"{campaign_id}.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only campaign-continuity status (M0-T087)")
    parser.add_argument("--status", action="store_true",
                        help="print the orientation summary")
    parser.add_argument("--path", default=None,
                        help="explicit record path (default: sole record under "
                             "project-control/campaigns/)")
    args = parser.parse_args(argv)
    if not args.status:
        parser.print_help()
        return 2
    if args.path:
        candidates = [Path(args.path)]
    else:
        base = Path(".") / DEFAULT_DIR
        candidates = sorted(base.glob("*.json")) if base.is_dir() else []
    if not candidates:
        sys.stderr.write("no campaign record found (fail closed: orientation "
                         "unavailable; reconcile via ledger + git)\n")
        return 1
    rc = 0
    for path in candidates:
        try:
            record = load(path)
        except CampaignRecordError as exc:
            sys.stderr.write(f"{path}: INVALID: {exc}\n")
            rc = 1
            continue
        sys.stdout.write(orientation_summary(record) + "\n")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
