"""Durable child handoffs and parent/child turnover draining
(D-024 Phase C item 6, s6.3, M0-T091).

When the primary session must rotate, existing subagents finish ONLY their
already-bounded cohesive assignments while external evidence shows their
contexts remain healthy; they may not start new children or broaden scope. A
child reaching its own landing condition receives ONE landing instruction
and returns a durable partial handoff instead of running forever. A new
primary session may orient read-only while old children drain, but must not
take a conflicting write lease or dispatch new writes until child work,
commits, test processes, and external effects are reconciled — exact-once
ownership (s6.3).

A child returns a BOUNDED evidence summary, artifact references, and
unresolved questions — not an entire transcript (s6): the handoff record
refuses transcript-sized payloads outright, so verbose child output stays
out of the primary context by construction. A child whose API call failed
returns an EXPLICIT partial/failure state (s16.2), never a silent absence.

This module records and refuses; nothing here spawns, resumes, stops, or
messages an agent (SHADOW-ONLY, R595 untouched).

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses

from .lease_runtime import LeaseLedger
from .runtime_health import LANDING_DIRECTION_TEXT


class HandoffError(ValueError):
    """Typed error for child handoffs and turnover (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


#: Closed child-outcome vocabulary (s6.3, s16.2).
OUTCOME_COMPLETE = "complete"
OUTCOME_PARTIAL_LANDED = "partial-landed"
OUTCOME_PARTIAL_BLOCKED = "partial-blocked"
OUTCOME_FAILED_API = "failed-api"
CHILD_OUTCOMES: tuple[str, ...] = (
    OUTCOME_COMPLETE, OUTCOME_PARTIAL_LANDED, OUTCOME_PARTIAL_BLOCKED,
    OUTCOME_FAILED_API)

#: A bounded summary, not a transcript (s6). Chosen well above any honest
#: evidence summary and far below a transcript dump.
MAX_SUMMARY_CHARS = 4000


@dataclasses.dataclass(frozen=True)
class ChildHandoff:
    """The durable (partial) handoff a child returns at its seam."""

    assignment_id: str
    parent_task_id: str
    outcome: str
    bounded_summary: str
    completed: str = ""
    repository_state: str = ""
    verified_evidence: tuple[str, ...] = ()
    open_questions: tuple[str, ...] = ()
    exact_next_action: str = ""
    api_error: str = ""

    def __post_init__(self) -> None:
        if not self.assignment_id or not self.parent_task_id:
            raise HandoffError("missing_ids",
                               "assignment_id and parent_task_id required")
        if self.outcome not in CHILD_OUTCOMES:
            raise HandoffError(
                "bad_outcome",
                f"outcome {self.outcome!r} is not in {list(CHILD_OUTCOMES)}")
        if not self.bounded_summary.strip():
            raise HandoffError(
                "missing_summary",
                "a handoff carries a bounded evidence summary (s6)")
        if len(self.bounded_summary) > MAX_SUMMARY_CHARS:
            raise HandoffError(
                "transcript_not_summary",
                f"bounded_summary is {len(self.bounded_summary)} chars "
                f"(max {MAX_SUMMARY_CHARS}); return a bounded evidence "
                f"summary with artifact references, never the transcript "
                f"(D-024 s6)")
        if self.outcome == OUTCOME_FAILED_API:
            if not self.api_error.strip():
                raise HandoffError(
                    "missing_api_error",
                    "a failed-api handoff must state the explicit failure "
                    "(s16.2: child API failure returns explicit "
                    "partial/failure state)")
            return
        for name, value in (("completed", self.completed),
                            ("repository_state", self.repository_state),
                            ("exact_next_action", self.exact_next_action)):
            if not value.strip():
                raise HandoffError(
                    "incomplete_handoff",
                    f"{name!r} is required for a {self.outcome!r} handoff: "
                    f"what was completed, the exact repository state, and "
                    f"the exact next action (s6, s7)")


class TurnoverCoordinator:
    """Parent/child turnover draining rules (s6.3), per parent session.

    Tracks registered children through the drain: during parent landing a
    HEALTHY child finishes its bounded assignment; an unhealthy child gets
    ONE landing instruction; every child ends in a durable handoff. The
    successor gains write authority only after full reconciliation.
    """

    def __init__(self, parent_task_id: str) -> None:
        if not parent_task_id:
            raise HandoffError("missing_ids", "parent_task_id required")
        self._parent_task_id = parent_task_id
        self._landing = False
        self._children: dict[str, str] = {}  # assignment_id -> state
        self._landing_sent: set[str] = set()
        self._handoffs: dict[str, ChildHandoff] = {}

    # -- child registration and drain state --------------------------------

    def register_child(self, assignment_id: str) -> None:
        if self._landing:
            raise HandoffError(
                "landing_in_progress",
                "no new children once landing has begun; finish only the "
                "smallest safe atomic unit already underway (s5.5, s6.3)")
        if assignment_id in self._children:
            raise HandoffError("duplicate_child",
                               f"child {assignment_id!r} already registered")
        self._children[assignment_id] = "active"

    def begin_landing(self) -> None:
        self._landing = True

    @property
    def landing(self) -> bool:
        return self._landing

    def may_spawn_children(self) -> bool:
        """False once landing/drain begins (s6.3)."""
        return not self._landing

    def child_may_continue(self, assignment_id: str, *,
                           healthy: bool) -> bool:
        """During parent landing a healthy child FINISHES its bounded
        assignment; it never picks up new scope (enforced by the extension
        gate and the scope hold). An unhealthy child may not continue."""
        if assignment_id not in self._children:
            raise HandoffError("unknown_child",
                               f"child {assignment_id!r} is not registered")
        if self._children[assignment_id] != "active":
            return False
        return healthy

    def land_child(self, assignment_id: str) -> str | None:
        """Return the ONE landing instruction for a child, once; a repeat
        call returns None (course correction is sparse, s16.2)."""
        if assignment_id not in self._children:
            raise HandoffError("unknown_child",
                               f"child {assignment_id!r} is not registered")
        if assignment_id in self._landing_sent:
            return None
        self._landing_sent.add(assignment_id)
        self._children[assignment_id] = "landing"
        return LANDING_DIRECTION_TEXT

    def record_child_handoff(self, handoff: ChildHandoff) -> None:
        """A durable handoff reconciles the child (any outcome, including
        the explicit failed-api state)."""
        if handoff.assignment_id not in self._children:
            raise HandoffError(
                "unknown_child",
                f"child {handoff.assignment_id!r} is not registered")
        if handoff.parent_task_id != self._parent_task_id:
            raise HandoffError(
                "unlinked_records",
                f"handoff parent {handoff.parent_task_id!r} is not this "
                f"coordinator's parent {self._parent_task_id!r}")
        self._children[handoff.assignment_id] = "reconciled"
        self._handoffs[handoff.assignment_id] = handoff

    def unreconciled_children(self) -> tuple[str, ...]:
        return tuple(a for a, state in self._children.items()
                     if state != "reconciled")

    def handoff_for(self, assignment_id: str) -> ChildHandoff | None:
        return self._handoffs.get(assignment_id)

    # -- successor authority (exact-once ownership) -------------------------

    def successor_may_orient_read_only(self) -> bool:
        """Read-only orientation is always allowed while children drain."""
        return True

    def successor_may_dispatch_writes(
            self, ledger: LeaseLedger, *,
            external_effects_reconciled: bool) -> bool:
        """Write authority transfers only after child work, leases, and
        external effects are reconciled (s6.3); never overlapping writers."""
        if self.unreconciled_children():
            return False
        if not external_effects_reconciled:
            return False
        return ledger.writer_count() == 0
