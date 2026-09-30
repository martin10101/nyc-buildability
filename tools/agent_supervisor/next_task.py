"""Audited close-run + next-packet selection + exactly-once task advancement.

D-024 Amendment 22 defect D9 correction (M0-T125 register) and the R373 journey
tail. The reviewed identity STRANDS at COMPLETE:

- ``decision_complete`` enters COMPLETE (loop.py:2041-2042); the ``run_closed``
  edge COMPLETE->IDLE (state_machine.py:395) has ZERO callers, and COMPLETE is
  not in ``CYCLE_ENTRY_STATES`` — so every later start refuses
  ``bad_cycle_entry_state`` (G4 (e) upheld this);
- there is NO next-task/packet selection surface anywhere: ``start`` binds
  exactly one ``--task-packet`` and nothing walks the ledger for the next
  bounded task; the ``NO_ELIGIBLE_WORK`` family is caller-less.

Consequently R388 ("several consecutive simulated bounded task advancements with
no human intervention, no duplicate or lost work, no false acceptance") was
IMPOSSIBLE to satisfy. This module supplies the three missing pieces:

1. an audited close-run surface (``plan_close_run`` / ``close_after_complete``)
   that fires the EXISTING ``run_closed`` edge, mirroring owner-restart's
   discipline;
2. an explicit next-packet selection step over an owner-supplied ordered packet
   list and/or a ledger query (``select_next_packet``);
3. EXACTLY-ONCE advancement recording per task (``record_advancement``) built on
   the durable journal's ``compare_and_swap_state`` single-winner primitive, so
   a crash at the advancement boundary can never double-advance or lose the
   advancement.

This module holds ONLY the decision logic and the durable exactly-once record.
It never takes a state-machine transition itself and never dispatches — the loop
owns transitions and dispatch. That keeps it a testable leaf (the discipline
``recovery.classify`` and ``rotation`` follow) and keeps R374/R375 intact: it
writes only NEW advancement keys, never the preserved live journal's own rows.

Supervisor-freeze qualifying evidence: D-024-R372, M0-T125 D9, G4 (e) ruling.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from typing import Any, Protocol

from tools.agent_supervisor.state_machine import COMPLETE, IDLE

#: Durable key prefix for the per-task exactly-once advancement record. One key
#: per advanced task id; its PRESENCE (won CAS) is the exactly-once witness.
ADVANCEMENT_KEY_PREFIX = "task_advancement/"

#: The trigger name of the existing COMPLETE->IDLE edge (state_machine.py:395).
RUN_CLOSED_TRIGGER = "run_closed"


class NextTaskError(ValueError):
    """Typed error for close-run / selection / advancement (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class DurableStore(Protocol):
    """The minimal durable interface this module needs (a ``DurableJournal``).

    ``compare_and_swap_state(key, expected, value)`` is the single-winner
    primitive: ``expected is None`` means "the key must not exist yet", and it
    returns True only for the caller whose write won. That is what makes
    advancement exactly-once across crashes, restarts and duplicate output.
    """

    def get_state(self, key: str, default: Any = ...) -> Any: ...

    def compare_and_swap_state(self, key: str, expected: Any, value: Any) -> bool: ...


def advancement_key(task_id: str) -> str:
    """The durable key for a task's exactly-once advancement record."""
    if not isinstance(task_id, str) or not task_id.strip():
        raise NextTaskError("bad_task_id", "task_id must be a non-empty string")
    return f"{ADVANCEMENT_KEY_PREFIX}{task_id}"


# --------------------------------------------------------------------------
# 1. Audited close-run surface (COMPLETE -> IDLE via the existing edge)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CloseRunPlan:
    """Whether (and how) a run resting at COMPLETE should be closed to IDLE.

    ``should_close`` True means the caller fires the EXISTING ``run_closed``
    edge (COMPLETE->IDLE) before selecting the next packet — the audited close
    that the reviewed identity never performed. False means the state is not
    COMPLETE and nothing is closed.
    """

    should_close: bool
    from_state: str
    to_state: str
    trigger: str
    reason: str


def plan_close_run(current_state: str) -> CloseRunPlan:
    """Plan an audited close of a COMPLETE run to IDLE via ``run_closed``.

    Idempotent and fail-safe: a state that is already IDLE (or anything other
    than COMPLETE) returns ``should_close=False`` rather than forcing a
    transition, so a duplicate close after a crash is a no-op, never a second
    edge fire.
    """
    if not isinstance(current_state, str) or not current_state:
        raise NextTaskError("bad_state", "current_state must be a non-empty string")
    if current_state == COMPLETE:
        return CloseRunPlan(
            should_close=True, from_state=COMPLETE, to_state=IDLE,
            trigger=RUN_CLOSED_TRIGGER,
            reason=("the run reported the authorized stage COMPLETE; close it to "
                    "IDLE via the run_closed edge before selecting the next "
                    "bounded task (D9). Closing NEVER merges, accepts, deploys, "
                    "or crosses an owner gate — it only returns the checkout to "
                    "IDLE so the next packet can start"))
    return CloseRunPlan(
        should_close=False, from_state=current_state, to_state=current_state,
        trigger="",
        reason=(f"state is {current_state!r}, not COMPLETE; nothing to close "
                f"(a non-COMPLETE run is closed by its own terminal handling)"))


def close_after_complete(current_state: str) -> CloseRunPlan:
    """Alias for the 'automatic close on the next start after COMPLETE' path.

    Same decision as ``plan_close_run`` — kept as a named entry point so the
    start-time caller (mirroring owner-restart discipline) reads intentionally.
    """
    return plan_close_run(current_state)


# --------------------------------------------------------------------------
# 2. Exactly-once task advancement (crash-safe, duplicate-safe)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AdvancementRecord:
    """The durable exactly-once record of one task's advancement.

    ``newly_recorded`` is True only for the caller whose ``compare_and_swap``
    won. A second call for the same task (a retry, a crash-resume, or duplicate
    provider output) reads ``newly_recorded=False`` and returns the SAME stored
    record — never a second advancement.
    """

    task_id: str
    run_id: str
    checkpoint_id: str
    from_state: str
    evidence_refs: tuple[str, ...]
    newly_recorded: bool

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _stored_record(store: DurableStore, task_id: str) -> dict[str, Any] | None:
    value = store.get_state(advancement_key(task_id), None)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise NextTaskError(
            "corrupt_advancement",
            f"advancement record for {task_id!r} is not an object; refusing to "
            f"treat a corrupt record as either advanced or unadvanced")
    return value


def is_advanced(store: DurableStore, task_id: str) -> bool:
    """True iff ``task_id`` already has a durable advancement record."""
    return _stored_record(store, task_id) is not None


def record_advancement(
    store: DurableStore,
    *,
    task_id: str,
    run_id: str,
    checkpoint_id: str,
    from_state: str,
    evidence_refs: Sequence[str] = (),
) -> AdvancementRecord:
    """Record a task's advancement EXACTLY ONCE (crash- and duplicate-safe).

    Uses ``compare_and_swap_state(key, expected=None, ...)`` — the write lands
    only if no advancement record exists yet. A crash after the CAS commit but
    before the next task dispatches leaves the record in place, so a restart
    re-calling this returns ``newly_recorded=False`` and the ORIGINAL record,
    never a duplicate advancement. Contradictory later output (a different
    checkpoint claiming the same task advanced) also loses the CAS and is
    surfaced as the stored fact, never as a new advancement.
    """
    if not isinstance(checkpoint_id, str) or not checkpoint_id.strip():
        raise NextTaskError(
            "bad_checkpoint",
            "advancement requires the checkpoint id that Codex reviewed; a "
            "task never advances without the reviewed checkpoint that justified "
            "it")
    if not isinstance(run_id, str) or not run_id.strip():
        raise NextTaskError("bad_run_id", "advancement requires a non-empty run_id")
    key = advancement_key(task_id)
    record = {
        "task_id": task_id,
        "run_id": run_id,
        "checkpoint_id": checkpoint_id,
        "from_state": from_state,
        "evidence_refs": [str(r) for r in evidence_refs],
    }
    won = store.compare_and_swap_state(key, None, record)
    if won:
        return AdvancementRecord(
            task_id=task_id, run_id=run_id, checkpoint_id=checkpoint_id,
            from_state=from_state,
            evidence_refs=tuple(str(r) for r in evidence_refs),
            newly_recorded=True)
    stored = _stored_record(store, task_id)
    if stored is None:  # pragma: no cover - CAS lost but key absent is impossible
        raise NextTaskError(
            "advancement_race_lost_but_absent",
            f"compare_and_swap for {task_id!r} lost but no record is stored; the "
            f"durable store violated its single-winner contract")
    return AdvancementRecord(
        task_id=str(stored.get("task_id", task_id)),
        run_id=str(stored.get("run_id", "")),
        checkpoint_id=str(stored.get("checkpoint_id", "")),
        from_state=str(stored.get("from_state", "")),
        evidence_refs=tuple(str(r) for r in stored.get("evidence_refs", ())),
        newly_recorded=False)


# --------------------------------------------------------------------------
# 3. Next-packet selection (owner-supplied ordered list and/or ledger query)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class TaskPacketRef:
    """An entry in the owner-supplied ordered next-packet list.

    ``task_id`` identifies the bounded task; ``packet_path`` is the on-disk
    packet the next ``start`` would bind. Both are required — a selection that
    cannot name the packet to dispatch is not a selection.
    """

    task_id: str
    packet_path: str

    def __post_init__(self) -> None:
        for name in ("task_id", "packet_path"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise NextTaskError(
                    "bad_packet_ref", f"TaskPacketRef requires a non-empty {name}")


@dataclasses.dataclass(frozen=True)
class NextTaskSelection:
    """The result of selecting the next bounded task to dispatch.

    ``selected`` None means no eligible work remains (every ordered packet is
    already advanced) — the honest ``NO_ELIGIBLE_WORK`` landing, never an
    optimistic re-dispatch of an already-advanced task.
    """

    selected: TaskPacketRef | None
    skipped_advanced: tuple[str, ...]
    reason: str


def select_next_packet(
    store: DurableStore,
    ordered_packets: Sequence[TaskPacketRef],
) -> NextTaskSelection:
    """Select the first ordered packet whose task has NOT already advanced.

    Skips (never re-dispatches) any task with a durable advancement record — the
    exactly-once guarantee applied at selection time, so a crash-resume that
    re-enters selection after an advancement picks the NEXT task, not the one
    just advanced. Returns ``selected=None`` when the list is exhausted.
    """
    packets = list(ordered_packets)
    if not packets:
        return NextTaskSelection(
            selected=None, skipped_advanced=(),
            reason="the ordered next-packet list is empty; there is no next "
                   "bounded task to select")
    # Validate the WHOLE ordered list first (before returning any selection), so
    # a duplicate task id is caught even when the first occurrence is the one
    # that would be selected — a duplicate anywhere risks a second advancement.
    seen: set[str] = set()
    for packet in packets:
        if not isinstance(packet, TaskPacketRef):
            raise NextTaskError(
                "bad_ordered_list",
                "ordered_packets must be TaskPacketRef entries")
        if packet.task_id in seen:
            raise NextTaskError(
                "duplicate_packet",
                f"task {packet.task_id!r} appears twice in the ordered list; a "
                f"duplicate would risk a second advancement")
        seen.add(packet.task_id)
    skipped: list[str] = []
    for packet in packets:
        if is_advanced(store, packet.task_id):
            skipped.append(packet.task_id)
            continue
        return NextTaskSelection(
            selected=packet, skipped_advanced=tuple(skipped),
            reason=(f"selected {packet.task_id!r}: first ordered packet with no "
                    f"durable advancement record"))
    return NextTaskSelection(
        selected=None, skipped_advanced=tuple(skipped),
        reason=("every packet in the ordered list has already advanced; no "
                "eligible bounded work remains (NO_ELIGIBLE_WORK)"))


# --------------------------------------------------------------------------
# Orchestration: advance the finished task, then select the next
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AdvanceAndSelectResult:
    """One consecutive-advancement step: advance the finished task, pick next."""

    advancement: AdvancementRecord
    next_selection: NextTaskSelection


def advance_and_select(
    store: DurableStore,
    *,
    completed_task_id: str,
    run_id: str,
    checkpoint_id: str,
    from_state: str,
    ordered_packets: Sequence[TaskPacketRef],
    evidence_refs: Sequence[str] = (),
) -> AdvanceAndSelectResult:
    """Advance the finished task exactly once, then select the next packet.

    The single step R388 repeats: task A reported COMPLETE and Codex approved
    it, so advance A exactly once (crash-safe), then select the next un-advanced
    packet. Because ``record_advancement`` is exactly-once and
    ``select_next_packet`` skips advanced tasks, a crash ANYWHERE in this step —
    before the advancement, after it but before selection, or after selection
    but before dispatch — resumes without duplicate or lost advancement.
    """
    advancement = record_advancement(
        store, task_id=completed_task_id, run_id=run_id,
        checkpoint_id=checkpoint_id, from_state=from_state,
        evidence_refs=evidence_refs)
    selection = select_next_packet(store, ordered_packets)
    return AdvanceAndSelectResult(advancement=advancement, next_selection=selection)
