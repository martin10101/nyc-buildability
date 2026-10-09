"""Durable owner stop-intent and its precedence
(D-024 Phase D, M0-T092; R026/R027/R029).

R026: "a durable owner pause, stop, or emergency-stop instruction always wins
over queued or recovered work". R029 lists "graceful stopping" as a state the
machine must distinguish; R027 orders the precedence pause / resume /
graceful-stop / emergency-stop.

What already existed (R018 prove-first): ``recovery.set_emergency_stop`` /
``set_manual_pause`` persist the EMERGENCY and PAUSE flags durably (keys owned
by ``resume_scheduler``), ``recovery.DurableFlags.blocking_reasons`` makes both
beat autostart, and ``recovery.clear_emergency_stop`` requires an explicit
owner command. What did NOT exist anywhere: a durable GRACEFUL-stop intent
("finish only the smallest safe atomic unit already underway, land it, then
stop" — R054's landing rule as an owner instruction) or a single precedence
answer across the three intents. This module adds exactly those two things and
imports the existing keys rather than duplicating them.

Nothing here stops a process; the module records and answers. The state
machine's ``GRACEFUL_STOPPING`` node (added by this same unit, R029) is where
the loop dwells while the landing happens.

Supervisor-freeze qualifying evidence: D-024-R102.
"""
from __future__ import annotations

import dataclasses
from typing import Any

from .models import to_utc_iso
from .resume_scheduler import EMERGENCY_STOP_KEY, MANUAL_PAUSE_KEY

#: Durable graceful-stop intent. A mapping (reason + timestamp), never a bare
#: bool, so the record says WHY the owner asked to stop.
GRACEFUL_STOP_KEY = "graceful_stop_intent"

#: The closed intent vocabulary, strongest first (R027 precedence).
INTENT_EMERGENCY = "emergency_stop"
INTENT_GRACEFUL = "graceful_stop"
INTENT_PAUSE = "manual_pause"
INTENT_NONE = "none"
PRECEDENCE: tuple[str, ...] = (INTENT_EMERGENCY, INTENT_GRACEFUL, INTENT_PAUSE)


class StopIntentError(Exception):
    """A stop-intent rule was violated. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class StopIntents:
    """The three durable owner intents, read from the journal (never argv)."""

    emergency: bool = False
    graceful: bool = False
    pause: bool = False
    graceful_reason: str = ""

    @classmethod
    def read(cls, journal: Any) -> "StopIntents":
        graceful = journal.get_state(GRACEFUL_STOP_KEY, None)
        graceful_set = isinstance(graceful, dict) and bool(graceful.get("set"))
        return cls(
            emergency=bool(journal.get_state(EMERGENCY_STOP_KEY, False)),
            graceful=graceful_set,
            pause=bool(journal.get_state(MANUAL_PAUSE_KEY, False)),
            graceful_reason=(str(graceful.get("reason", ""))
                             if graceful_set else ""),
        )


def set_graceful_stop(journal: Any, *, reason: str,
                      audit: Any = None) -> dict[str, Any]:
    """Persist the graceful-stop intent. Durable BEFORE it is acknowledged
    (R036: stop must be durable before acknowledging success)."""
    if not reason.strip():
        raise StopIntentError(
            "missing_reason",
            "a graceful stop records why the owner asked to stop; an "
            "unexplained stop intent cannot be audited")
    record = {"set": True, "reason": reason, "at_utc": to_utc_iso(),
              "clears_by": "an explicit owner command only"}
    journal.set_state(GRACEFUL_STOP_KEY, record)
    if audit is not None:
        audit.append("graceful_stop_set", detail=record)
    return record


def clear_graceful_stop(journal: Any, *, owner_command: bool,
                        audit: Any = None) -> dict[str, Any]:
    """Only an explicit owner command clears the intent — nothing in the loop,
    no recovery path, and no schedule (same rule as the emergency flag)."""
    if not owner_command:
        raise StopIntentError(
            "stop_requires_owner",
            "a durable graceful stop is cleared only by an explicit owner "
            "command; nothing in the loop, no recovery path, and no schedule "
            "may clear it (R026)")
    record = {"set": False, "at_utc": to_utc_iso()}
    journal.set_state(GRACEFUL_STOP_KEY, record)
    if audit is not None:
        audit.append("graceful_stop_cleared", detail=record)
    return record


def effective_intent(intents: StopIntents) -> str:
    """The single strongest active intent (R027 precedence), or ``none``.

    Emergency beats graceful beats pause; a stronger intent does not erase a
    weaker one — it outranks it, and the weaker record stays durable."""
    if intents.emergency:
        return INTENT_EMERGENCY
    if intents.graceful:
        return INTENT_GRACEFUL
    if intents.pause:
        return INTENT_PAUSE
    return INTENT_NONE


def wins_over_queued_work(intent: str) -> bool:
    """R026: EVERY active owner intent wins over queued or recovered work.
    Queued work never outranks the owner, whatever the intent's strength."""
    return intent in PRECEDENCE


def may_finish_current_unit(intent: str) -> bool:
    """May the unit ALREADY UNDERWAY reach its safe seam under this intent?

    * graceful: yes — finish only the smallest safe atomic unit already
      underway, land it, then stop (R054's landing rule);
    * pause: no — a pause is a synchronous hold at the current position;
    * emergency: no — child trees are terminated and evidence preserved.
    """
    if intent not in (*PRECEDENCE, INTENT_NONE):
        raise StopIntentError("unknown_intent",
                              f"{intent!r} is not one of {[*PRECEDENCE, INTENT_NONE]}")
    return intent in (INTENT_GRACEFUL, INTENT_NONE)


def may_dispatch_new_work(intent: str) -> bool:
    """New or queued work is dispatched only when NO intent is active."""
    if intent not in (*PRECEDENCE, INTENT_NONE):
        raise StopIntentError("unknown_intent",
                              f"{intent!r} is not one of {[*PRECEDENCE, INTENT_NONE]}")
    return intent == INTENT_NONE
