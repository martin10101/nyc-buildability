"""Lifecycle-hook ingestion + subagent identity tracking (D-024 Phase B item 5,
M0-T089).

Claude Code 2.1.220 documents 31 lifecycle hook events (captured at
official-docs confidence in ``fixtures/capability_matrix_v1.json``,
``claude.hooks.event_set_2_1_220``) covering every natural supervision point
D-024 s5.1 item 5 names: session start/end, subagent start/stop, task
creation/completion, post-tool batches, pre/post compaction, stop/failure,
file changes, and permission events.

Hooks write EXTERNAL state only (s5.1 item 5): this module turns a hook
invocation's payload into a typed telemetry record and maintains a bounded
subagent-identity registry. It never blocks a hook, never injects context,
and never messages a worker. Unknown event names are recorded honestly
(``known: false``) — a newer Claude Code adding events must not crash or be
guessed at.

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any

from .models import to_utc_iso
from .telemetry_records import TelemetryRecord

#: The documented 2.1.220 hook event set (official docs, fetched 2026-08-25).
KNOWN_HOOK_EVENTS = (
    "SessionStart", "Setup", "UserPromptSubmit", "UserPromptExpansion",
    "PreToolUse", "PermissionRequest", "PermissionDenied", "PostToolUse",
    "PostToolUseFailure", "PostToolBatch", "Notification", "MessageDisplay",
    "SubagentStart", "SubagentStop", "TaskCreated", "TaskCompleted", "Stop",
    "StopFailure", "TeammateIdle", "InstructionsLoaded", "ConfigChange",
    "CwdChanged", "DirectoryAdded", "FileChanged", "WorktreeCreate",
    "WorktreeRemove", "PreCompact", "PostCompact", "Elicitation",
    "ElicitationResult", "SessionEnd",
)

#: Payload fields preserved as attributes when present (identity/context, no
#: free-form content; prompts/transcripts are withheld by the journal anyway).
_EVENT_ATTRIBUTES = ("session_id", "task_id", "agent_type", "agent_id",
                     "prompt_id", "cwd", "model", "trigger", "tool_name",
                     "subagent_type", "status", "reason")


def ingest_hook_event(event_name: Any, payload: Any, *,
                      now_utc_iso: str | None = None) -> TelemetryRecord:
    """One typed record per hook invocation. Identity facts only, no usage
    numbers are invented — hook payloads carry state changes, not counters."""
    now = now_utc_iso or to_utc_iso()
    name = event_name if isinstance(event_name, str) else ""
    attributes: dict[str, Any] = {
        "event": name or f"<{type(event_name).__name__}>",
        "known": name in KNOWN_HOOK_EVENTS,
    }
    session = ""
    task = ""
    if isinstance(payload, dict):
        for key in _EVENT_ATTRIBUTES:
            value = payload.get(key)
            if value is not None:
                attributes[key] = value
        if isinstance(payload.get("session_id"), str):
            session = payload["session_id"]
        if isinstance(payload.get("task_id"), str):
            task = payload["task_id"]
    else:
        attributes["payload_error"] = type(payload).__name__
    return TelemetryRecord(
        record_type="lifecycle_hook", timestamp_utc=now,
        session_id=session, task_id=task, attributes=attributes)


class SubagentRegistry:
    """Bounded subagent-identity tracker fed by lifecycle events.

    Start/create events open an entry; stop/complete events close it. Closed
    entries are evicted oldest-first past ``max_entries`` so an unattended
    controller cannot grow this without bound. The registry is identity
    bookkeeping (which subagent is which), never a usage store.
    """

    _OPEN_EVENTS = ("SubagentStart", "TaskCreated")
    _CLOSE_EVENTS = ("SubagentStop", "TaskCompleted")

    def __init__(self, *, max_entries: int = 512) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max_entries = max_entries
        self._entries: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def observe(self, record: TelemetryRecord) -> None:
        """Feed one lifecycle_hook record; other record types are ignored."""
        if record.record_type != "lifecycle_hook":
            return
        event = str(record.attributes.get("event", ""))
        key = record.task_id or str(record.attributes.get("agent_id", ""))
        if not key:
            return
        if event in self._OPEN_EVENTS:
            entry = self._entries.pop(key, None) or {"task_id": key}
            entry.update({
                "state": "active",
                "started_at": record.timestamp_utc,
                "session_id": record.session_id,
                "agent_type": record.attributes.get("agent_type")
                or record.attributes.get("subagent_type"),
            })
            self._entries[key] = entry
        elif event in self._CLOSE_EVENTS:
            entry = self._entries.pop(key, None) or {"task_id": key}
            entry.update({"state": "closed",
                          "stopped_at": record.timestamp_utc})
            self._entries[key] = entry
        self._evict()

    def _evict(self) -> None:
        while len(self._entries) > self._max_entries:
            # evict the oldest CLOSED entry first; active identities survive
            # until the bound forces the oldest out regardless
            evicted = False
            for key, entry in self._entries.items():
                if entry.get("state") == "closed":
                    del self._entries[key]
                    evicted = True
                    break
            if not evicted:
                self._entries.popitem(last=False)

    def active(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(e) for e in self._entries.values()
                     if e.get("state") == "active")

    def get(self, task_id: str) -> dict[str, Any] | None:
        entry = self._entries.get(task_id)
        return dict(entry) if entry else None

    def __len__(self) -> int:
        return len(self._entries)
