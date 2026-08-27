"""Background-work check-in schedule + durable ingestion (D-024 Amendment 3
unit E, M0-T106; R174 "background-agent check-ins").

Documented cadence (official /goal contract; snapshot + build-time re-fetch,
R147): background work defers evaluation; once it has kept the goal waiting
for 30 minutes a check-in is due; after the first check-in the wait DOUBLES
before each later one, capped at FOUR TIMES the first interval (default: 1 h
after the first, then every 2 h). ``CLAUDE_CODE_GOAL_CHECKIN_MINUTES``
replaces the 30-minute first interval and scales the rest; ``0`` turns
check-ins off. Version gates: check-ins >= 2.1.234; idle check-ins >=
2.1.236; the three-idle-check-ins-per-goal cap >= 2.1.246 (uncapped before).

This module is controller-side math + passive ingestion: it computes when
the NATIVE runtime will check in (so the controller can corroborate without
transcript polling — R154 carried) and turns observed check-ins into typed
records persisted through the reused unit-D durable bus (dedup-keyed,
sanitize-first). Nothing here messages a worker or schedules its own pings
into Fable context.

Supervisor-freeze qualifying evidence: D-024-R152 + D-024-R174.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping

from .event_bus import DurableEventBus
from .goal_contract import (CHECKINS_MIN_VERSION, IDLE_CHECKIN_CAP_MIN_VERSION,
                            IDLE_CHECKINS_MIN_VERSION, version_at_least)
from .models import to_utc_iso
from .telemetry_records import TelemetryRecord

#: Documented defaults.
DEFAULT_FIRST_INTERVAL_MINUTES = 30
BACKOFF_FACTOR = 2
BACKOFF_CAP_MULTIPLE = 4
IDLE_CHECKIN_CAP = 3

#: Environment variable that replaces the first interval and scales the rest.
CHECKIN_ENV_VAR = "CLAUDE_CODE_GOAL_CHECKIN_MINUTES"


class GoalCheckinError(ValueError):
    """Check-in configuration/observation violated the contract (fail visible)."""


@dataclasses.dataclass(frozen=True)
class CheckinSchedule:
    """Deterministic due-time offsets for background-work check-ins.

    ``due_offsets_minutes[i]`` is minutes from the moment background work
    started keeping the goal waiting until check-in ``i+1`` is due. Empty
    when check-ins are disabled (env ``0``) or unavailable (< 2.1.234).
    """

    enabled: bool
    first_interval_minutes: int
    due_offsets_minutes: tuple[int, ...]
    source: str  # "default" | "env" | "disabled-env" | "unavailable-version"


def resolve_first_interval(env_value: str | None) -> tuple[int, str]:
    """(first interval minutes, source); typed error on a malformed override.

    A malformed env value is a misconfiguration the controller must SEE —
    silently falling back would hide a broken deployment (fail visible).
    """
    if env_value is None or env_value == "":
        return DEFAULT_FIRST_INTERVAL_MINUTES, "default"
    try:
        minutes = int(env_value.strip())
    except (ValueError, AttributeError) as exc:
        raise GoalCheckinError(
            f"{CHECKIN_ENV_VAR} must be a non-negative integer, got "
            f"{env_value!r}") from exc
    if minutes < 0:
        raise GoalCheckinError(
            f"{CHECKIN_ENV_VAR} must be >= 0, got {minutes}")
    if minutes == 0:
        return 0, "disabled-env"
    return minutes, "env"


def checkin_schedule(*, installed_version: str, env_value: str | None = None,
                     count: int = 6) -> CheckinSchedule:
    """The first ``count`` due offsets under the documented cadence.

    Gap sequence: F, 2F, 4F, 4F, ... (doubling capped at four times the
    first interval), so default offsets are 30, 90, 210, 330, ... minutes.
    Below 2.1.234 the schedule is empty with source
    ``unavailable-version`` — an older runtime never checks in, and the
    controller must not expect it to (unknown is never invented).
    """
    if count < 0:
        raise GoalCheckinError("count must be >= 0")
    available = version_at_least(installed_version, CHECKINS_MIN_VERSION)
    if available is not True:
        return CheckinSchedule(enabled=False, first_interval_minutes=0,
                               due_offsets_minutes=(),
                               source="unavailable-version")
    first, source = resolve_first_interval(env_value)
    if first == 0:
        return CheckinSchedule(enabled=False, first_interval_minutes=0,
                               due_offsets_minutes=(), source=source)
    offsets: list[int] = []
    elapsed = 0
    gap = first
    cap = first * BACKOFF_CAP_MULTIPLE
    for _ in range(count):
        elapsed += gap
        offsets.append(elapsed)
        gap = min(gap * BACKOFF_FACTOR, cap)
    return CheckinSchedule(enabled=True, first_interval_minutes=first,
                           due_offsets_minutes=tuple(offsets), source=source)


def idle_checkin_cap(installed_version: str) -> int | None:
    """Idle check-ins per goal between prompts: 3 at >= 2.1.246; uncapped
    (None) at >= 2.1.236; 0 below 2.1.236 (idle delivery unavailable);
    None-with-unknown when the version cannot be parsed."""
    at_cap = version_at_least(installed_version, IDLE_CHECKIN_CAP_MIN_VERSION)
    if at_cap is True:
        return IDLE_CHECKIN_CAP
    has_idle = version_at_least(installed_version, IDLE_CHECKINS_MIN_VERSION)
    if has_idle is True:
        return None  # documented: uncapped before 2.1.246
    if has_idle is False:
        return 0
    return None  # unparseable version: unknown, never invented


#: Documented delivery kinds for a due check-in.
CHECKIN_KINDS = ("turn_end", "idle")


def ingest_checkin(payload: Any, *, task_id: str = "",
                   now_utc_iso: str | None = None) -> TelemetryRecord:
    """One typed record per observed check-in (identity facts, no free text).

    ``kind`` outside the documented pair is preserved with
    ``known_kind: false`` (recorded honestly, never guessed).
    """
    now = now_utc_iso or to_utc_iso()
    attributes: dict[str, Any] = {}
    if isinstance(payload, Mapping):
        kind = payload.get("kind")
        kind = kind if isinstance(kind, str) else ""
        attributes["kind"] = kind or "<missing>"
        attributes["known_kind"] = kind in CHECKIN_KINDS
        for key in ("sequence", "running_tasks", "session_id", "goal_active"):
            value = payload.get(key)
            if value is not None:
                attributes[key] = value
    else:
        attributes["payload_error"] = type(payload).__name__
        attributes["known_kind"] = False
    session = payload.get("session_id") if isinstance(payload, Mapping) else ""
    return TelemetryRecord(
        record_type="goal_checkin", timestamp_utc=now,
        session_id=session if isinstance(session, str) else "",
        task_id=task_id, attributes=attributes)


def record_checkin(bus: DurableEventBus, payload: Any, *, task_id: str = "",
                   now_utc_iso: str | None = None) -> TelemetryRecord | None:
    """Ingest one check-in and persist it via the REUSED unit-D durable bus
    (dedup-keyed on the record content; duplicate delivery is a counted
    no-op). Returns the stored record, or None on a duplicate."""
    record = ingest_checkin(payload, task_id=task_id, now_utc_iso=now_utc_iso)
    return bus.publish_typed(record)
