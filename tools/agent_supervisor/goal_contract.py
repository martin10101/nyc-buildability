"""Bounded /goal condition contract (D-024 Amendment 3 unit E, M0-T106;
R152/R174).

`/goal` is the native inner continuation mechanism: a completion condition a
small fast model evaluates after every turn (official contract snapshotted at
``project-control/reports/M0-T102-docs-snapshot/goal.md`` and re-fetched at
build time — R147; no drift found 2026-08-27). This module composes and
validates the condition the supervisor sets for ONE bounded Fable assignment:

* **one cohesive task at a time** (R152: never one goal for the entire
  campaign) — a condition binds exactly one ledger task and is refused when
  it references other ledger tasks or campaign-scale language;
* **safe completion condition** (R174) — one measurable end state, a stated
  check the worker's own output can demonstrate, the constraints that
  matter, and an EXPLICIT turn bound ("or stop after N turns" — the
  documented way to bound how long a goal runs);
* **no worker-visible token pressure** (R045) — the FULL composed text
  passes the reused `subagent_contracts.assert_worker_text_clean` fail-closed
  validator; the documented 4,000-character ceiling is enforced.

Version facts for the goal contract (documented; the fixture pins them):
check-ins >= 2.1.234; idle check-ins >= 2.1.236; idle-check-in cap of three
>= 2.1.246; goal restored on every resume route >= 2.1.239. The goal
contract does not exist on the 2.1.220 baseline.

Supervisor-freeze qualifying evidence: D-024-R152 + D-024-R174.
"""
from __future__ import annotations

import dataclasses
import re

from .subagent_contracts import assert_worker_text_clean

#: Documented ceiling for a /goal condition.
GOAL_CONDITION_MAX_CHARS = 4000

#: Documented version gates of the goal contract (official docs; also pinned
#: in fixtures/goal_semantics_2_1_247.json with the drift reconciliation).
CHECKINS_MIN_VERSION = "2.1.234"
IDLE_CHECKINS_MIN_VERSION = "2.1.236"
IDLE_CHECKIN_CAP_MIN_VERSION = "2.1.246"
RESUME_ALL_ROUTES_MIN_VERSION = "2.1.239"

#: Ledger task-id shape (docs/PROJECT_CONTROL_PROTOCOL.md).
_TASK_ID_RE = re.compile(r"^M\d+-T\d+$")
_LEDGER_TASK_RE = re.compile(r"\bM\d+-T\d+\b")

#: Campaign-scale phrasing that must never become a single goal (R152). A
#: heuristic tripwire on top of the structural one-task binding — fail closed
#: on the obvious shapes rather than guess intent.
_CAMPAIGN_SCALE_RE = re.compile(
    r"(?i)\b(entire|whole)\s+(campaign|project|backlog|milestone)\b"
    r"|\bevery\s+(remaining\s+)?task\b"
    r"|\ball\s+(remaining\s+)?(tasks|milestones|units)\b")

_TURN_BOUND_RE = re.compile(r"(?i)\bstop\s+after\s+\d+\s+(turns?|minutes?|hours?)\b")


class GoalContractError(ValueError):
    """A goal condition violated the bounded-goal contract (fail closed)."""


def parse_claude_version(text: str) -> tuple[int, int, int] | None:
    """``2.1.247`` / ``2.1.247 (Claude Code)`` -> (2, 1, 247); None when the
    string carries no leading semantic version (unknown, never guessed)."""
    match = re.match(r"\s*(\d+)\.(\d+)\.(\d+)", text or "")
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def version_at_least(installed: str, required: str) -> bool | None:
    """True/False when both versions parse; None (unknown) otherwise."""
    have = parse_claude_version(installed)
    need = parse_claude_version(required)
    if have is None or need is None:
        return None
    return have >= need


@dataclasses.dataclass(frozen=True)
class GoalCondition:
    """One validated, bounded /goal condition for exactly one task.

    ``text`` is the exact string handed to ``/goal``. Validation is fail
    closed at construction: a condition that cannot prove its own boundedness
    never exists as an object.
    """

    task_id: str
    end_state: str
    stated_check: str
    constraints: tuple[str, ...]
    max_turns: int
    text: str

    def __post_init__(self) -> None:
        if not _TASK_ID_RE.match(self.task_id):
            raise GoalContractError(
                f"goal binds exactly ONE ledger task; got task_id "
                f"{self.task_id!r} (R152: never one goal for the campaign)")
        for name, value in (("end_state", self.end_state),
                            ("stated_check", self.stated_check)):
            if not value or not value.strip():
                raise GoalContractError(
                    f"{name} must be non-empty: a goal needs one measurable "
                    f"end state and a stated check (documented condition shape)")
        if self.max_turns < 1:
            raise GoalContractError("max_turns must be >= 1 (explicit bound)")
        if not _TURN_BOUND_RE.search(self.text):
            raise GoalContractError(
                "composed condition lost its turn-bound clause; a goal "
                "without an explicit bound is not a safe completion condition")
        if len(self.text) > GOAL_CONDITION_MAX_CHARS:
            raise GoalContractError(
                f"condition is {len(self.text)} chars; the documented ceiling "
                f"is {GOAL_CONDITION_MAX_CHARS}")
        foreign = [t for t in _LEDGER_TASK_RE.findall(self.text)
                   if t != self.task_id]
        if foreign:
            raise GoalContractError(
                f"condition references other ledger tasks {sorted(set(foreign))}; "
                f"one goal covers one cohesive task (R152)")
        if _CAMPAIGN_SCALE_RE.search(self.text):
            raise GoalContractError(
                "condition uses campaign-scale language; never one goal for "
                "the entire campaign (R152, fail closed)")
        # R045 last: the full worker-facing text, exactly as /goal would see it.
        assert_worker_text_clean("goal_condition", self.text)


def compose_goal_condition(task_id: str, end_state: str, stated_check: str,
                           *, constraints: tuple[str, ...] = (),
                           max_turns: int = 20) -> GoalCondition:
    """Compose the canonical bounded condition text for one assignment.

    Deterministic layout (documented effective-condition shape): end state,
    the check that proves it, the constraints that matter, then the explicit
    turn bound. Every validation in :class:`GoalCondition` applies.
    """
    parts = [f"For task {task_id}: {end_state.strip()}",
             f"Prove it: {stated_check.strip()}"]
    for constraint in constraints:
        if constraint and constraint.strip():
            parts.append(f"Constraint: {constraint.strip()}")
    parts.append(f"Or stop after {max_turns} turns and report the exact state")
    text = ". ".join(parts) + "."
    return GoalCondition(task_id=task_id, end_state=end_state.strip(),
                         stated_check=stated_check.strip(),
                         constraints=tuple(c.strip() for c in constraints
                                           if c and c.strip()),
                         max_turns=max_turns, text=text)
