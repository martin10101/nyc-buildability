"""Serialized write-lease ledger and scope enforcement
(D-024 Phase C item 4, M0-T091).

Graduates the M0-T090 contract-level guards to runtime enforcement:

- ``subagent_contracts.assert_grantable`` validates ONE candidate against a
  SNAPSHOT and is not a lock (G5 M4). This ledger is the serialization the
  runtime owes: every grant — parent or nested child — passes through ONE
  ledger, and each granted envelope is folded into the active set before the
  next candidate is checked, so two overlapping candidates can never both
  pass against a stale snapshot;
- nested children cannot evade the producer cap or the leases because a
  child grant names its parent and still goes through the same fold
  (D-024 s6, s16.2 "Nested children cannot evade the repository's stricter
  producer cap, write leases, or controller health policy");
- a write observed outside the granted lease fails closed
  (``scope_violation``) — scope enforcement is a controller act, never a
  worker-visible counter;
- exact-once ownership: a parent holding active children cannot release its
  lease until the children are drained (s6.3), and a successor cannot take a
  conflicting lease while any old grant is live (``turnover`` rules in
  ``child_handoff``).

The ledger is a single-controller, call-order-serialized structure (the
supervisor is single-threaded by design, like the rest of this package); it
records and refuses — it never spawns, resumes, stops, or messages an agent
(SHADOW-ONLY, R595 untouched).

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses

from .subagent_contracts import (
    SupervisionEnvelope,
    _normalize_lease_path,
    assert_grantable,
    validate_envelope,
)


class LeaseRuntimeError(ValueError):
    """Typed error for runtime lease enforcement (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class LeaseGrant:
    """One serialized grant: the envelope plus its fold position."""

    assignment_id: str
    envelope: SupervisionEnvelope
    parent_assignment_id: str | None
    granted_seq: int


class LeaseLedger:
    """The single serialized grant registry (G5 M4 graduation).

    Grants mutate the active set atomically per call, in call order; a
    candidate is always checked against the CURRENT active set, never a
    caller-held snapshot. Releases refuse to break exact-once ownership.
    """

    def __init__(self) -> None:
        self._active: dict[str, LeaseGrant] = {}
        self._seq = 0

    def grant(self, envelope: SupervisionEnvelope, *,
              parent_assignment_id: str | None = None) -> LeaseGrant:
        """Validate against the LIVE active set, then fold the grant in."""
        validate_envelope(envelope)
        if envelope.assignment_id in self._active:
            raise LeaseRuntimeError(
                "duplicate_grant",
                f"assignment {envelope.assignment_id!r} already holds a "
                f"grant; exact-once ownership admits one grant per "
                f"assignment")
        if parent_assignment_id is not None \
                and parent_assignment_id not in self._active:
            raise LeaseRuntimeError(
                "unknown_parent",
                f"nested grant names parent {parent_assignment_id!r} which "
                f"holds no active grant; children exist only under a live "
                f"parent (D-024 s6.3)")
        assert_grantable(self.active_envelopes(), envelope)
        self._seq += 1
        grant = LeaseGrant(
            assignment_id=envelope.assignment_id,
            envelope=envelope,
            parent_assignment_id=parent_assignment_id,
            granted_seq=self._seq,
        )
        self._active[envelope.assignment_id] = grant
        return grant

    def release(self, assignment_id: str) -> None:
        """Release a grant; refuse while children still hold grants."""
        if assignment_id not in self._active:
            raise LeaseRuntimeError(
                "unknown_grant",
                f"assignment {assignment_id!r} holds no active grant")
        children = self.children_of(assignment_id)
        if children:
            raise LeaseRuntimeError(
                "children_not_drained",
                f"assignment {assignment_id!r} still has active child "
                f"grants {sorted(children)}; drain children before the "
                f"parent releases (D-024 s6.3 exact-once ownership)")
        del self._active[assignment_id]

    def active_envelopes(self) -> tuple[SupervisionEnvelope, ...]:
        return tuple(g.envelope for g in self._active.values())

    def active_ids(self) -> tuple[str, ...]:
        return tuple(self._active)

    def writer_count(self) -> int:
        return sum(1 for g in self._active.values()
                   if g.envelope.write_lease_paths)

    def children_of(self, assignment_id: str) -> tuple[str, ...]:
        return tuple(a for a, g in self._active.items()
                     if g.parent_assignment_id == assignment_id)

    def holds(self, assignment_id: str) -> bool:
        return assignment_id in self._active

    def assert_write_within_scope(self, assignment_id: str,
                                  path: str) -> None:
        """Fail closed on a write outside the granted lease.

        Enforcement is controller-side only: the refusal is a typed error in
        the controller, never a counter or message shown to the worker.
        """
        grant = self._active.get(assignment_id)
        if grant is None:
            raise LeaseRuntimeError(
                "unknown_grant",
                f"assignment {assignment_id!r} holds no active grant; no "
                f"write authority exists without a grant")
        lease = grant.envelope.write_lease_paths
        if not lease:
            raise LeaseRuntimeError(
                "scope_violation",
                f"assignment {assignment_id!r} is read/review-only; a write "
                f"to {path!r} is outside any lease (D-024 s6)")
        normalized = _normalize_lease_path(path)
        for held in lease:
            held_norm = _normalize_lease_path(held)
            if normalized == held_norm \
                    or normalized.startswith(held_norm + "/"):
                return
        raise LeaseRuntimeError(
            "scope_violation",
            f"assignment {assignment_id!r} wrote {path!r} outside its "
            f"granted lease {sorted(lease)}; scope enforcement fails closed "
            f"(D-024 s6)")
