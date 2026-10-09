"""Section-14 operator status composition (D-024 Phase F, M0-T094;
R034/R042/R094/R095).

The `status` verb answers the owner WITHOUT waking Fable (R094): everything
here is read from durable records - the journal, the campaign record file, and
nothing else. Every rendered fact carries a source and an R042 confidence
label; a fact no durable record holds is reported ``unknown`` with the label
``unknown`` - NEVER invented, never coerced to zero (R042: "missing usage is
unknown, never zero").

What already existed (R018 prove-first): ``cli.cmd_status`` renders the
journal core (state, mode, integrity, asks, audit chain). The section-14 list
in R034 additionally names: current task and why selected, recent completed
checkpoints, active model/session and fallback state, active subagents and
their bounded contracts, and token/context health with measurement confidence.
No module composed those; this one does, purely by reading records other units
already persist (``claude_runner.SESSION_KEY``, ``epoch_lease.LEASE_KEY``,
``stop_intent``, ``outage_policy``, ``recovery.CHILD_PROCESSES_KEY``,
``resume_scheduler.LIMIT_RECORD_KEY``, ``model_change_ipc`` keys, the campaign
record). Facts the loop has not yet recorded for the current run stay honest
unknowns rather than acquiring a parallel bookkeeping channel.

Read-only on purpose: like ``cmd_status``, this module may never mutate a
journal it reports on.

Supervisor-freeze qualifying evidence: D-024-R104 (Phase F).
"""
from __future__ import annotations

import pathlib
from typing import Any

from .campaign_continuity import CampaignRecordError, load as load_campaign
from .claude_runner import SESSION_KEY
from .epoch_lease import LEASE_KEY, EpochLease, current_lease
from .model_change_ipc import RUN_OVERRIDE_KEY, SELECTION_DIGEST_KEY
from .outage_policy import BLOCKED_KEY, IDLE_KEY, RETRY_KEY
from .recovery import CHILD_PROCESSES_KEY, DurableFlags
from .resume_scheduler import LIMIT_RECORD_KEY
from .stop_intent import StopIntents, effective_intent

#: R042 confidence labels this module can truthfully assign. A journal read is
#: `status-live`; an absent record is `unknown`. The richer provider labels
#: (provider-exact, sdk-task-cumulative, ...) belong to the units that MEASURE;
#: status only relays what they persisted, keeping their label when present.
CONFIDENCE_STATUS_LIVE = "status-live"
CONFIDENCE_CAMPAIGN_RECORD = "control-plane-record"
CONFIDENCE_UNKNOWN = "unknown"

#: How many of the most recent transitions the concise view names. Transitions
#: are the durable seam log - checkpoint landings appear here - so the bound
#: keeps `status` bounded on a long-lived journal (R095: concise by default).
RECENT_TRANSITIONS = 5


def fact(value: Any, source: str,
         confidence: str = CONFIDENCE_STATUS_LIVE) -> dict[str, Any]:
    """One labeled status fact (R042): value + where it was read + confidence."""
    return {"value": value, "source": source, "confidence": confidence}


def unknown(source: str, note: str = "") -> dict[str, Any]:
    """An honestly-absent fact. `unknown` is a value here, never zero (R042)."""
    entry = fact("unknown", source, CONFIDENCE_UNKNOWN)
    if note:
        entry["note"] = note
    return entry


def _relay(record: Any, source: str) -> dict[str, Any]:
    """Relay a persisted record verbatim, keeping any confidence label the
    measuring unit stored inside it (status never re-labels a measurement)."""
    if not isinstance(record, dict) or not record:
        return unknown(source)
    confidence = str(record.get("confidence", "")) or CONFIDENCE_STATUS_LIVE
    return fact(record, source, confidence)


def _campaign_facts(checkout: pathlib.Path) -> dict[str, Any]:
    """Campaign identity + NEXT from the machine-validated campaign record(s).

    The record file is the canonical next-action pointer (D-024); a missing or
    invalid record is reported as such - orientation falls back to the ledger,
    exactly as `campaign_continuity --status` fails closed.
    """
    campaigns_dir = checkout / "project-control" / "campaigns"
    if not campaigns_dir.is_dir():
        return {"campaign": unknown(str(campaigns_dir), "no campaign directory")}
    records = []
    for path in sorted(campaigns_dir.glob("*.json")):
        try:
            record = load_campaign(path)
        except CampaignRecordError as exc:
            records.append({"file": path.name, "error": str(exc)})
            continue
        if record.state != "active":
            continue
        records.append({
            "campaign_id": record.campaign_id,
            "state": record.state,
            "sequence": record.sequence,
            "next_task_id": record.next_action.get("task_id", ""),
            "next_description": str(record.next_action.get("description",
                                                           ""))[:400],
        })
    if not records:
        return {"campaign": unknown(str(campaigns_dir), "no active campaign record")}
    return {"campaign": fact(records, str(campaigns_dir),
                             CONFIDENCE_CAMPAIGN_RECORD)}


def _lease_facts(journal: Any, now: float | None) -> dict[str, Any]:
    lease: EpochLease | None = current_lease(journal)
    if lease is None:
        return {"controller_lease": unknown(LEASE_KEY, "no lease recorded")}
    payload: dict[str, Any] = {
        "campaign_id": lease.campaign_id,
        "owner_run_id": lease.owner_run_id,
        "epoch": lease.epoch,
        "acquired_at_utc": lease.acquired_at_utc,
        "renew_by_epoch_seconds": lease.renew_by_epoch_seconds,
        "released": lease.released,
    }
    if now is not None:
        payload["live"] = lease.live(now)
        payload["expired"] = lease.expired(now)
    return {"controller_lease": fact(payload, LEASE_KEY)}


def _control_facts(journal: Any) -> dict[str, Any]:
    intents = StopIntents.read(journal)
    flags = DurableFlags.read(journal)
    return {
        "effective_stop_intent": fact(effective_intent(intents), "stop_intent"),
        "manual_pause": fact(intents.pause, "stop_intent"),
        "graceful_stop": fact(
            {"set": intents.graceful, "reason": intents.graceful_reason},
            "stop_intent"),
        "emergency_stop": fact(intents.emergency, "stop_intent"),
        "limited_auto_flag": fact(flags.limited_auto_enabled, "recovery flags"),
    }


def _outage_facts(journal: Any) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    for label, key in (("outage_retry", RETRY_KEY),
                       ("outage_blocked", BLOCKED_KEY),
                       ("bounded_idle", IDLE_KEY)):
        record = journal.get_state(key, None)
        facts[label] = (fact(record, key) if isinstance(record, dict) and record
                        else unknown(key, "not active"))
    return facts


def _session_facts(journal: Any) -> dict[str, Any]:
    """Active model/session and fallback state (R034), from persisted identity."""
    facts: dict[str, Any] = {
        "claude_session": _relay(journal.get_state(SESSION_KEY, None), SESSION_KEY),
    }
    override = journal.get_state(RUN_OVERRIDE_KEY, None)
    facts["model_override"] = (fact(override, RUN_OVERRIDE_KEY)
                               if isinstance(override, dict) and override
                               else unknown(RUN_OVERRIDE_KEY, "no override active"))
    digest = journal.get_state(SELECTION_DIGEST_KEY, None)
    facts["model_selection_digest"] = (fact(digest, SELECTION_DIGEST_KEY)
                                       if digest else unknown(SELECTION_DIGEST_KEY))
    return facts


def _task_facts(journal: Any) -> dict[str, Any]:
    """Current task/unit and why selected, from the durable transition log.

    The loop records its dispatch decisions as transitions; the LAST transition
    detail is therefore the most recent durable statement of what ran and why.
    When the journal predates a run (or the loop has not recorded a dispatch),
    the answer is an honest unknown - status never reconstructs intent.
    """
    last = journal.last_transition()
    if last is None:
        return {"current_task": unknown("transition log", "no transitions recorded")}
    detail = dict(last.detail or {})
    payload = {
        "run_id": last.run_id,
        "state": last.state_to,
        "trigger": last.trigger,
        "at_utc": last.committed_at_utc,
        "detail": detail,
    }
    return {"current_task": fact(payload, "transition log (last transition)")}


def _checkpoint_facts(journal: Any) -> dict[str, Any]:
    """Recent completed checkpoints, read from the transition seam log."""
    transitions = journal.transitions()
    if not transitions:
        return {"recent_transitions": unknown("transition log", "empty")}
    recent = [
        {"at_utc": t.committed_at_utc, "to_state": t.state_to,
         "trigger": t.trigger, "run_id": t.run_id}
        for t in transitions[-RECENT_TRANSITIONS:]
    ]
    return {"recent_transitions": fact(recent, "transition log")}


def _subagent_facts(journal: Any) -> dict[str, Any]:
    """Active subagents + their recorded child state (R034/R094)."""
    children = journal.get_state(CHILD_PROCESSES_KEY, None)
    if not children:
        return {"subagents": unknown(CHILD_PROCESSES_KEY, "no children recorded")}
    return {"subagents": fact(children, CHILD_PROCESSES_KEY)}


def _usage_facts(journal: Any) -> dict[str, Any]:
    """Token/context health with measurement confidence (R034/R042).

    Status RELAYS persisted measurements; it never measures. An absent record
    is `unknown` - and unknown means a conservative planning policy applies,
    not unlimited continuation (R042).
    """
    return {"usage_limit_record": _relay(journal.get_state(LIMIT_RECORD_KEY, None),
                                         LIMIT_RECORD_KEY)}


def compose_status(journal: Any, *, checkout: pathlib.Path,
                   now: float | None = None) -> dict[str, Any]:
    """The section-14 fact set, every entry labeled (R034/R042/R094)."""
    facts: dict[str, Any] = {}
    facts.update(_campaign_facts(checkout))
    facts.update(_control_facts(journal))
    facts.update(_lease_facts(journal, now))
    facts.update(_outage_facts(journal))
    facts.update(_session_facts(journal))
    facts.update(_task_facts(journal))
    facts.update(_checkpoint_facts(journal))
    facts.update(_subagent_facts(journal))
    facts.update(_usage_facts(journal))
    return facts


def _brief(entry: dict[str, Any]) -> str:
    """One concise line-fragment for a labeled fact (R095)."""
    value = entry.get("value")
    confidence = entry.get("confidence", CONFIDENCE_UNKNOWN)
    if value == "unknown":
        note = entry.get("note", "")
        return f"unknown{f' ({note})' if note else ''}"
    if isinstance(value, dict):
        keys = ("reason", "set", "owner_run_id", "epoch", "state", "trigger",
                "session_id", "model")
        parts = [f"{k}={value[k]}" for k in keys if k in value and value[k] != ""]
        body = ", ".join(str(p) for p in parts[:4]) or "recorded"
        return f"{body} [{confidence}]"
    if isinstance(value, list):
        return f"{len(value)} recorded [{confidence}]"
    return f"{value} [{confidence}]"


def render_concise(facts: dict[str, Any]) -> list[str]:
    """The concise human view (R095): one bounded line per section-14 fact."""
    order = (
        ("campaign", "campaign"),
        ("effective_stop_intent", "stop intent"),
        ("controller_lease", "lease/epoch"),
        ("outage_blocked", "outage hold"),
        ("bounded_idle", "idle hold"),
        ("claude_session", "model/session"),
        ("model_override", "model fallback"),
        ("current_task", "current task"),
        ("recent_transitions", "recent seams"),
        ("subagents", "subagents"),
        ("usage_limit_record", "token health"),
    )
    lines = []
    for key, label in order:
        entry = facts.get(key)
        if entry is None:
            continue
        lines.append(f"{label + ':':<18}{_brief(entry)}")
    return lines
