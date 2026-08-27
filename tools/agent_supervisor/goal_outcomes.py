"""Goal verdict / clearing-class / outcome classification (D-024 Amendment 3
unit E, M0-T106; R152/R174).

Classifies what the native /goal machinery REPORTS — it never decides for the
evaluator, never re-prompts a worker, and fails to UNKNOWN on any shape the
official contract does not document (snapshot + build-time re-fetch, R147):

* **verdicts** — the evaluator returns exactly three: not-yet-met (reason is
  guidance), met (achieved entry), impossible (failed entry + reason);
* **unrecoverable clearing** — the documented warning starts with
  ``Goal cleared after an unrecoverable error`` and names one of FOUR causes:
  authentication failure (with the host-managed-credentials nuance: the goal
  STAYS ACTIVE when a host restores access), exhausted credit balance, a
  context overflow auto-compaction couldn't clear, and an unavailable model.
  Any other failure — including transient rate limits and overloaded
  servers — leaves the goal active;
* **no-progress** — the documented stall (no tool use for several turns)
  stops the loop and returns control WITH THE GOAL STILL SET. The exact
  warning text is not documented, so classification here is STRUCTURAL (loop
  returned control + goal still active + no unrecoverable warning), never a
  guess at unspecified text;
* **resume** — the condition carries over while turn count, timer, and
  token-spend baseline RESET; achieved/cleared goals are never restored;
  every resume route restores the goal at >= 2.1.239 (below, the picker
  route did not);
* **context pressure** — auto-compaction is an EMERGENCY buffer only: a
  context-overflow clearing is a turnover-seam trigger, never a signal to
  silently continue (packet: /autocompact never a seam substitute);
* **status telemetry** — /goal status numbers (turns evaluated, token spend)
  ingest as R042-labelled measurements; spend is goal-scoped and resets at
  resume, so it is never presented as whole-session spend.

Supervisor-freeze qualifying evidence: D-024-R152 + D-024-R174.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping

from .goal_contract import RESUME_ALL_ROUTES_MIN_VERSION, version_at_least
from .models import to_utc_iso
from .telemetry_records import Measurement, TelemetryRecord

#: The three documented evaluator verdicts (anything else is unknown).
VERDICTS = ("not_yet_met", "met", "impossible")

#: The four documented unrecoverable clearing classes.
UNRECOVERABLE_CLASSES = ("auth_failure", "credit_exhausted",
                         "context_overflow", "model_unavailable")

#: Documented warning frame for an unrecoverable clearing.
CLEARED_WARNING_PREFIX = "Goal cleared after an unrecoverable error"
CLEARED_WARNING_SUFFIX = "Run /goal again to continue"

#: Documented user-clear confirmation shapes.
USER_CLEAR_PREFIX = "Goal cleared:"
NO_GOAL_TEXT = "No goal set"

_CAUSE_MARKERS = (
    ("auth_failure", ("authentication", "credential", "logged out", "login")),
    ("credit_exhausted", ("credit", "balance")),
    ("context_overflow", ("context", "overflow", "compact")),
    ("model_unavailable", ("model",)),
)

_TRANSIENT_MARKERS = ("rate limit", "rate_limit", "overloaded", "429", "529",
                      "timeout", "temporarily")


def normalize_verdict(value: Any) -> str:
    """One of the three documented verdicts, else ``unknown`` — never a guess."""
    if not isinstance(value, str):
        return "unknown"
    token = value.strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {"not_yet_met": "not_yet_met", "notyetmet": "not_yet_met",
               "met": "met", "achieved": "met",
               "impossible": "impossible", "failed_impossible": "impossible"}
    return aliases.get(token, "unknown")


@dataclasses.dataclass(frozen=True)
class GoalClearing:
    """Classification of a goal-lifecycle message.

    ``cleared`` is ``True``/``False`` only when the documented contract says
    so; ``None`` means UNKNOWN (unrecognized text — surfaced, never guessed).
    """

    cleared: bool | None
    clazz: str
    reason_excerpt: str = ""

    @property
    def is_unrecoverable(self) -> bool:
        return self.cleared is True and self.clazz in UNRECOVERABLE_CLASSES


def classify_goal_message(text: Any, *,
                          credentials_host_managed: bool = False) -> GoalClearing:
    """Classify one goal-lifecycle message against the documented shapes.

    The unrecoverable-warning PREFIX is the authoritative signal that the
    goal cleared; the cause class is read from the named cause, with the
    documented host-managed-credentials nuance: an auth failure under a
    credential-managing host leaves the goal ACTIVE.
    """
    if not isinstance(text, str) or not text.strip():
        return GoalClearing(cleared=None, clazz="unknown")
    stripped = text.strip()
    lowered = stripped.lower()
    excerpt = stripped[:160]
    if stripped.startswith(CLEARED_WARNING_PREFIX):
        clazz = "unknown_unrecoverable"
        for name, markers in _CAUSE_MARKERS:
            if any(marker in lowered for marker in markers):
                clazz = name
                break
        if clazz == "auth_failure" and credentials_host_managed:
            # documented nuance: the host restores access; goal stays active
            return GoalClearing(cleared=False,
                                clazz="auth_failure_host_managed_active",
                                reason_excerpt=excerpt)
        return GoalClearing(cleared=True, clazz=clazz, reason_excerpt=excerpt)
    if stripped.startswith(USER_CLEAR_PREFIX):
        return GoalClearing(cleared=True, clazz="cleared_by_user",
                            reason_excerpt=excerpt)
    if stripped.startswith(NO_GOAL_TEXT):
        return GoalClearing(cleared=False, clazz="no_goal")
    if any(marker in lowered for marker in _TRANSIENT_MARKERS):
        # documented: any other failure, incl. rate limits and overloaded
        # servers, leaves the goal active
        return GoalClearing(cleared=False, clazz="transient_error_active",
                            reason_excerpt=excerpt)
    return GoalClearing(cleared=None, clazz="unknown", reason_excerpt=excerpt)


def classify_pause(*, control_returned: bool, goal_still_active: bool,
                   clearing: GoalClearing | None = None) -> str:
    """STRUCTURAL no-progress classification (the stall warning text is not
    documented, so nothing here parses it):

    * loop returned control + goal still set + no clearing -> the documented
      no-progress pause (evaluation resumes after the next prompt);
    * goal cleared -> not a pause (the clearing classification governs);
    * anything else -> unknown.
    """
    if clearing is not None and clearing.cleared is True:
        return "not_paused_goal_cleared"
    if control_returned and goal_still_active:
        return "no_progress_paused"
    if control_returned and not goal_still_active:
        return "unknown"  # control back without a goal: nothing documented
    return "running"


def resume_restores_goal(installed_version: str, route: str,
                         prior_state: str) -> bool | None:
    """Does a resume restore the goal? (documented semantics; None = unknown).

    ``prior_state``: active | achieved | cleared. Achieved/cleared are never
    restored. Active goals restore on every route at >= 2.1.239; below that,
    every route EXCEPT the ``picker`` restored.
    """
    if prior_state in ("achieved", "cleared"):
        return False
    if prior_state != "active":
        return None
    at_least = version_at_least(installed_version, RESUME_ALL_ROUTES_MIN_VERSION)
    if at_least is None:
        return None
    if at_least:
        return True
    return route != "picker"


#: The counters a resume RESETS (documented): the condition carries over,
#: these start fresh — so post-resume spend is goal-scoped-since-resume and
#: must never be presented as whole-goal or whole-session spend.
RESUME_RESET_COUNTERS = ("turn_count", "timer", "token_spend_baseline")


def is_turnover_seam_trigger(clearing: GoalClearing) -> bool:
    """Context-pressure policy: auto-compaction is an EMERGENCY buffer only.

    A context-overflow clearing means the emergency buffer was consumed —
    that is a safe-seam turnover trigger for the controller, never a cue to
    silently continue in the same session (packet: /autocompact never a
    seam substitute).
    """
    return clearing.is_unrecoverable and clearing.clazz == "context_overflow"


def _count(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        return None
    return value


def ingest_goal_status(payload: Any, *, task_id: str = "",
                       now_utc_iso: str | None = None) -> TelemetryRecord:
    """One typed record from a /goal status observation (R042 labels).

    Documented status fields: the condition, how long it has been running,
    how many turns were evaluated, the current token spend, and the
    evaluator's most recent reason. Numbers absent before the first
    evaluation ingest as ``unknown`` — never zero.
    """
    now = now_utc_iso or to_utc_iso()
    if not isinstance(payload, Mapping):
        return TelemetryRecord(
            record_type="goal_status", timestamp_utc=now, task_id=task_id,
            measurements={"goal_turns_evaluated": Measurement.unknown(
                "cumulative", "goal status payload missing or not an object")},
            attributes={"payload_error": type(payload).__name__})
    spend_detail = ("goal-scoped token spend from /goal status; baseline "
                    "RESETS on resume - never whole-session, never whole-goal "
                    "across resumes")
    measurements = {
        "goal_turns_evaluated": (
            Measurement(value=_count(payload.get("turns_evaluated")),
                        label="status-live", category="cumulative",
                        detail="turns the evaluator has judged for this goal")
            if _count(payload.get("turns_evaluated")) is not None
            else Measurement.unknown(
                "cumulative", "absent before the first evaluation")),
        "goal_token_spend": (
            Measurement(value=_count(payload.get("token_spend")),
                        label="status-live", category="cumulative",
                        detail=spend_detail)
            if _count(payload.get("token_spend")) is not None
            else Measurement.unknown("cumulative", "token spend not reported")),
    }
    attributes: dict[str, Any] = {}
    for key in ("active", "achieved", "duration", "last_reason", "condition"):
        value = payload.get(key)
        if value is not None:
            attributes[key] = value  # sanitized/bounded by the journal on write
    return TelemetryRecord(record_type="goal_status", timestamp_utc=now,
                           task_id=task_id, measurements=measurements,
                           attributes=attributes)
