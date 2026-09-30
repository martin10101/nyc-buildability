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
import hashlib
import json
import os
import pathlib
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from tools.agent_supervisor import launch_seam, rotation, stop_intent
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


# ==========================================================================
# D-024 Amendment 25 (D-024-R400..R405): LIVE cross-task wiring.
#
# The three primitives above (close-run, exactly-once advancement, ordered
# selection) were simulation-proven at M0-T126 but had ZERO production callers
# (M0-T127 s7.4 / Amendment 24). Everything below wires them into the live
# limited-auto path so ONE owner-typed bounded-auto start can advance a finished
# task exactly once, SELECT the next ELIGIBLE task from an owner-supplied ordered
# queue (never silently choosing owner-gated, blocked, claimed-elsewhere, stale
# or otherwise ineligible work - R405), re-enforce the isolated-worktree launch
# seam, and continue across MULTIPLE BOUNDED tasks (R400) - all behind the
# EXISTING `--mode limited-auto --owner-enable-bounded-auto` gate (no new
# activation surface). It stays a testable leaf: it decides and records; the loop
# (via the injected ``run_one`` callback) owns every state transition, provider
# contact and dispatch.
# ==========================================================================

#: The ONLY packet status the controller will run as a supervised successor: a
#: task explicitly CLAIMED for supervised execution. Narrow and fail-closed
#: (R405): `accepted`, `awaiting_gate`, `backlog`, `blocked`, `in_progress`, or
#: any unknown status is NOT eligible and is skipped with an audited reason. The
#: owner-typed first task (`--task-packet`) is NOT status-gated here - it runs as
#: today; only SELECTED successors pass this gate.
ELIGIBLE_STATUSES: frozenset[str] = frozenset({"claimed"})

#: A dependency counts as satisfied only when its own packet records this status.
ACCEPTED_STATUS = "accepted"

#: Packet fields that, when truthy/non-empty, mark a task as requiring an owner
#: act before it may run. Enumerated and fail-closed: a successor carrying any of
#: these is refused rather than silently selected (R405). `blockers` is checked
#: separately (it is a list). This list is deliberately broad; real packets
#: express holds through `blockers`/`status`, but an owner-gate field on a future
#: packet must never be run past.
OWNER_GATE_FIELDS: tuple[str, ...] = (
    "owner_gated", "owner_hold", "holds", "awaiting_owner", "requires_owner",
    "on_hold", "hold")

#: Durable key prefix for the per-task packet-content snapshot taken when the
#: queue is first read ("queued"). Selection re-reads the packet and compares, so
#: a packet edited (or whose worktree moved) AFTER queueing is refused as STALE.
QUEUED_DIGEST_PREFIX = "task_queue/queued_digest/"

#: The honest "no work remains" landing (mirrors select_next_packet's family).
NO_ELIGIBLE_WORK = "NO_ELIGIBLE_WORK"


def queued_digest_key(task_id: str) -> str:
    """Durable key for a queued task's packet-content snapshot."""
    if not isinstance(task_id, str) or not task_id.strip():
        raise NextTaskError("bad_task_id", "task_id must be a non-empty string")
    return f"{QUEUED_DIGEST_PREFIX}{task_id}"


@dataclasses.dataclass(frozen=True)
class TaskQueueEntry:
    """One entry in the owner-supplied ordered next-task queue.

    The owner names the WHOLE universe of selectable work at start time; the
    controller never invents candidates. Each successor entry carries the packet
    to bind AND the isolated worktree/branch/repo the next start must launch in,
    so selection can re-enforce the launch seam before dispatch.
    """

    task_id: str
    packet_path: str
    worktree: str
    branch: str = ""
    repo: str = ""

    def __post_init__(self) -> None:
        for name in ("task_id", "packet_path", "worktree"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise NextTaskError(
                    "bad_queue_entry",
                    f"a task-queue entry requires a non-empty {name}")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "TaskQueueEntry":
        if not isinstance(data, Mapping):
            raise NextTaskError("bad_queue_entry",
                                "each queue entry must be an object")
        return cls(
            task_id=str(data.get("task_id", "") or ""),
            packet_path=str(data.get("packet_path", "") or ""),
            worktree=str(data.get("worktree", "") or ""),
            branch=str(data.get("branch", "") or ""),
            repo=str(data.get("repo", "") or ""))


def load_task_queue(path: str) -> list[TaskQueueEntry]:
    """Parse the owner-supplied ordered successor queue file.

    Format: ``{"tasks": [ {"task_id","packet_path","worktree","branch","repo"},
    ... ]}``. A missing/empty ``--packet-queue`` yields an empty list (the
    single-task default). Fails closed (typed error) on an unreadable or
    malformed file rather than silently running fewer tasks.
    """
    if not path:
        return []
    try:
        raw = pathlib.Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise NextTaskError("queue_unreadable",
                            f"cannot read the packet queue {path!r}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise NextTaskError("queue_unparseable",
                            f"packet queue {path!r} is not valid JSON: {exc}") from exc
    tasks = data.get("tasks") if isinstance(data, Mapping) else None
    if not isinstance(tasks, list):
        raise NextTaskError(
            "queue_malformed",
            f"packet queue {path!r} must be an object with a list `tasks`")
    return [TaskQueueEntry.from_mapping(item) for item in tasks]


def _read_packet_file(path: str) -> tuple[dict[str, Any], str]:
    """Read a task packet, returning (packet, sha256-of-raw-bytes).

    The digest is over the RAW file bytes, so any edit (even whitespace) moves
    it - that is the staleness witness. Raises ``NextTaskError`` (unparseable
    category) on any read/parse failure so the caller can SKIP the candidate
    with an audited reason instead of crashing the journey.
    """
    p = pathlib.Path(path)
    try:
        raw = p.read_bytes()
    except OSError as exc:
        raise NextTaskError("packet_unreadable",
                            f"task packet {path!r} is unreadable: {exc}") from exc
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NextTaskError("packet_unparseable",
                            f"task packet {path!r} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise NextTaskError("packet_not_object",
                            f"task packet {path!r} is not a JSON object")
    return data, hashlib.sha256(raw).hexdigest()


def packet_digest(path: str) -> str:
    """The staleness digest of a packet file (raw-bytes sha256)."""
    return _read_packet_file(path)[1]


def snapshot_queued_digest(store: DurableStore, task_id: str, digest: str) -> str:
    """Record the packet digest captured WHEN THE QUEUE WAS READ, exactly once.

    CAS with ``expected=None`` so the FIRST start's snapshot wins and a
    crash-resume (which re-reads the same queue) keeps the ORIGINAL snapshot -
    otherwise a packet edited during the run would silently re-baseline itself
    and never read as stale. Returns the durable snapshot in force.
    """
    key = queued_digest_key(task_id)
    if store.compare_and_swap_state(key, None, digest):
        return digest
    stored = store.get_state(key, None)
    return str(stored) if isinstance(stored, str) else digest


@dataclasses.dataclass(frozen=True)
class EligibilityVerdict:
    """Whether a candidate successor may be SELECTED, and why not if refused.

    ``eligible`` False always carries a stable ``code`` and human ``reason`` so
    the skip is auditable and never silent (R405).
    """

    eligible: bool
    code: str
    reason: str

    @classmethod
    def ok(cls, task_id: str) -> "EligibilityVerdict":
        return cls(True, "", f"{task_id} is eligible for supervised execution")


def evaluate_eligibility(
    entry: TaskQueueEntry,
    *,
    queued_digest: str,
    primary_checkout: str = "",
    tasks_dir: str = "",
) -> EligibilityVerdict:
    """Fail-closed eligibility for ONE candidate successor (R405).

    Every category below refuses VISIBLY (a code + reason the caller audits),
    never silently. Order is cheapest-first, and the FIRST failing check wins:

    1. packet parses and is a JSON object (``packet_unparseable`` etc.);
    2. the entry's ``task_id`` matches the packet's own id (``task_id_mismatch``);
    3. status is in the narrow eligible set (``ineligible_status``);
    4. no blockers and no owner-gate field is set (``blocked`` / ``owner_gated``);
    5. every declared dependency's own packet is ``accepted`` (``dependency_unaccepted``);
    6. the declared worktree exists, is not the primary checkout, and binds via
       the EXISTING launch-seam guards (``worktree_missing`` / ``*_binding``);
    7. the packet content still matches the queued snapshot (``stale_packet``).
    """
    try:
        packet, current_digest = _read_packet_file(entry.packet_path)
    except NextTaskError as exc:
        return EligibilityVerdict(False, exc.code, exc.message)

    packet_task_id = str(packet.get("task_id", "") or "")
    if packet_task_id != entry.task_id:
        return EligibilityVerdict(
            False, "task_id_mismatch",
            f"queue entry names {entry.task_id!r} but the packet at "
            f"{entry.packet_path!r} declares task_id {packet_task_id!r}; a "
            f"mismatched packet is never run")

    status = str(packet.get("status", "") or "")
    if status not in ELIGIBLE_STATUSES:
        return EligibilityVerdict(
            False, "ineligible_status",
            f"{entry.task_id} status is {status!r}, not in the eligible set "
            f"{sorted(ELIGIBLE_STATUSES)}; only a task claimed for supervised "
            f"execution is selected (accepted/awaiting_gate/backlog/blocked/"
            f"in_progress are refused, never silently run)")

    blockers = packet.get("blockers") or []
    if blockers:
        return EligibilityVerdict(
            False, "blocked",
            f"{entry.task_id} carries {len(blockers)} open blocker(s); a blocked "
            f"task requires resolution before it can run and is never selected")
    for field in OWNER_GATE_FIELDS:
        if packet.get(field):
            return EligibilityVerdict(
                False, "owner_gated",
                f"{entry.task_id} sets the owner-gate field {field!r}; a task that "
                f"requires an owner act is never selected without one (R405)")

    dependencies = packet.get("dependencies") or []
    base = tasks_dir or str(pathlib.Path(entry.packet_path).parent)
    for dep in dependencies:
        dep_id = str(dep or "")
        dep_path = str(pathlib.Path(base) / f"{dep_id}.json")
        try:
            dep_packet, _ = _read_packet_file(dep_path)
        except NextTaskError:
            return EligibilityVerdict(
                False, "dependency_unresolved",
                f"{entry.task_id} depends on {dep_id!r} but its packet at "
                f"{dep_path!r} is missing or unreadable; a dependency whose state "
                f"cannot be read is fail-closed unaccepted")
        if str(dep_packet.get("status", "") or "") != ACCEPTED_STATUS:
            return EligibilityVerdict(
                False, "dependency_unaccepted",
                f"{entry.task_id} depends on {dep_id!r}, whose status is "
                f"{dep_packet.get('status')!r}, not {ACCEPTED_STATUS!r}; a task "
                f"never runs ahead of an unaccepted dependency")

    if not entry.worktree or not os.path.isdir(entry.worktree):
        return EligibilityVerdict(
            False, "worktree_missing",
            f"{entry.task_id} declares worktree {entry.worktree!r}, which does not "
            f"exist as a directory; an unbound/absent worktree fails closed")
    if primary_checkout and launch_seam.same_path(entry.worktree, primary_checkout):
        return EligibilityVerdict(
            False, "worktree_primary_checkout",
            f"{entry.task_id} worktree {entry.worktree!r} is the primary control "
            f"checkout; a worker never runs in the control checkout (D-024-R336)")
    repo = entry.repo or entry.worktree
    binding = launch_seam.enforce_launch_bindings(
        entry.worktree, repo, str(packet.get("worktree", "") or ""), primary_checkout)
    if binding is not None:
        return EligibilityVerdict(
            False, f"binding_{binding.code}",
            f"{entry.task_id} launch-seam binding refused: {binding.message}")

    if queued_digest and current_digest != queued_digest:
        return EligibilityVerdict(
            False, "stale_packet",
            f"{entry.task_id} packet content changed since it was queued "
            f"(queued digest {queued_digest[:12]}..., now {current_digest[:12]}...); "
            f"a packet that moved after queueing is refused as stale")
    return EligibilityVerdict.ok(entry.task_id)


def _audit(audit: Any, event: str, **detail: Any) -> None:
    """Best-effort typed audit append (never breaks the journey on a log error)."""
    if audit is None:
        return
    try:
        audit.append(event, detail=detail)
    except Exception:  # pragma: no cover - audit logging is best-effort here
        pass


def between_task_seam(
    journal: Any, prior_run: Mapping[str, Any] | None, *,
    audit: Any = None,
) -> str:
    """Re-check the stop signals BEFORE dispatching the next task (R402, R400 s4).

    Returns "" to proceed, or a stop reason. Reuses the EXISTING durable
    machinery so the between-task seam can never disagree with the between-cycle
    one:

    * owner stop/pause/graceful/emergency intents (``stop_intent``) - a durable
      intent set from another terminal wins over queued work;
    * the owner-set run budget's own durable exhaustion (the prior run's ledger
      report), which the next task's first-cycle ``_budget_stop`` also backstops;
    * a pending context-rotation (``rotation.rotation_pending``) - the ceiling the
      next launch's pre-first-dispatch seam also backstops.
    """
    intent = stop_intent.effective_intent(stop_intent.StopIntents.read(journal))
    if not stop_intent.may_dispatch_new_work(intent):
        _audit(audit, "cross_task_intent_stop", intent=intent,
               note="owner stop/pause/graceful/emergency intent read at the "
                    "between-task seam; the next task is not dispatched")
        return f"owner_intent_{intent}"
    budget = (prior_run or {}).get("run_budget") or {}
    if isinstance(budget, Mapping) and budget.get("exhausted"):
        _audit(audit, "cross_task_budget_stop",
               dimension=budget.get("exhausted_dimension", "budget"),
               note="the owner-set run budget is spent; the next task is not "
                    "dispatched")
        return "budget_exhausted"
    if rotation.rotation_pending(journal):
        _audit(audit, "cross_task_rotation_pending",
               note="a context-rotation is pending; the next task is not dispatched "
                    "at the between-task seam (the launch ceiling seam backstops it)")
        return "rotation_pending_before_next_task"
    return ""


def run_reached_complete(run: Mapping[str, Any]) -> tuple[bool, str, str]:
    """Did this run reach a Codex COMPLETE verdict with a reviewed checkpoint?

    Advancement (family 5) requires BOTH the durable COMPLETE state AND a last
    cycle whose Codex decision is COMPLETE carrying the reviewed checkpoint id -
    so a run that stopped for budget, an intent, a REVISE, an ASK, or any refusal
    never advances. Returns (complete, checkpoint_id, reason).
    """
    if not isinstance(run, Mapping):
        return False, "", "no run result to evaluate"
    if str(run.get("final_state", "") or "") != COMPLETE:
        return False, "", (f"the run did not reach COMPLETE (final_state="
                            f"{run.get('final_state')!r}, stopped="
                            f"{run.get('stopped')!r})")
    cycles = run.get("cycles") or []
    last = cycles[-1] if cycles else {}
    if not isinstance(last, Mapping) or str(last.get("decision", "") or "") != "COMPLETE":
        return False, "", ("the run rests at COMPLETE but its last cycle is not a "
                           "COMPLETE Codex decision; refusing to advance")
    checkpoint_id = str(last.get("checkpoint_id", "") or "")
    if not checkpoint_id:
        return False, "", ("COMPLETE was reached without a reviewed checkpoint id; "
                           "a task never advances without the checkpoint Codex reviewed")
    return True, checkpoint_id, "Codex COMPLETE with a reviewed checkpoint"


@dataclasses.dataclass
class TaskQueueStep:
    """What happened to ONE task in the cross-task journey (audit-friendly)."""

    task_id: str
    outcome: str  # dispatched | already_advanced | skipped | not_completed | bound
    detail: str = ""
    checkpoint_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class TaskQueueResult:
    """The whole bounded cross-task journey. Attached to the last run's payload."""

    dispatched: int
    max_tasks: int
    stop_reason: str
    steps: list[TaskQueueStep] = dataclasses.field(default_factory=list)
    advanced: list[str] = dataclasses.field(default_factory=list)
    provider_calls: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "dispatched": self.dispatched,
            "max_tasks": self.max_tasks,
            "stop_reason": self.stop_reason,
            "steps": [s.to_dict() for s in self.steps],
            "advanced": list(self.advanced),
            "provider_calls": self.provider_calls,
        }


def run_task_queue(
    args: Any, checkout: Any, journal: Any, audit: Any, run_one: Any,
) -> dict[str, Any]:
    """Drive ONE owner-typed bounded-auto start across MULTIPLE bounded tasks.

    ``run_one(args, checkout, journal, audit) -> run-dict`` is the injected
    single-task loop (``cli._run_loop``); this driver owns only the DECISION
    logic between tasks. The first task is the owner-typed ``--task-packet``
    (validated exactly as today); successors come from ``--packet-queue``. Bound
    by ``--max-tasks`` (default 1 -> byte-identical single-task behaviour; this
    driver is only entered when the owner opted into multi-task).

    Exactly-once + crash safety (R402): a completed task is advanced via the CAS
    BEFORE the next selection; a task already carrying a durable advancement
    record is SKIPPED (never re-run), so a crash-resume that re-invokes start
    resumes without double-advancing or losing work. Ineligible successors are
    skipped with an audited reason; an exhausted eligible set lands
    NO_ELIGIBLE_WORK visibly (R405).

    Envelope confinement (R400/R402, G3-C1): the multi-task driver runs ONLY
    under ``--mode limited-auto`` (the owner-gated bounded unattended mode). The
    owner-ENABLE half is already enforced pre-dispatch by ``bounded_mode_gate``
    (limited-auto without ``--owner-enable-bounded-auto`` never reaches here); this
    is the complementary MODE half, so a ``--mode supervised/shadow --max-tasks>1``
    (or ``--packet-queue``) start is refused fail-closed with a typed refusal and
    an audit row BEFORE any packet is read, snapshotted, or dispatched. The typed
    ``NextTaskError`` rides the existing ``cmd_start`` refusal path (a report, not
    a traceback).
    """
    mode = str(getattr(args, "mode", "") or "")
    if mode != "limited-auto":
        _audit(audit, "cross_task_mode_refused", mode=mode,
               note="the multi-task queue driver runs only under --mode "
                    "limited-auto; a non-limited-auto multi-task start is refused "
                    "before any packet is read or dispatched")
        raise NextTaskError(
            "cross_task_mode_refused",
            f"the cross-task queue driver runs only under --mode limited-auto (the "
            f"owner-gated bounded unattended mode), not {mode!r}; multi-task "
            f"continuation is refused fail-closed. bounded_mode_gate enforces the "
            f"owner-enable half pre-dispatch; this is the mode half")
    primary = str(checkout)
    max_tasks = max(1, int(getattr(args, "max_tasks", 1) or 1))
    first_packet, _ = _read_packet_file(str(args.task_packet))
    first_entry = TaskQueueEntry(
        task_id=str(first_packet.get("task_id", "") or "task-1"),
        packet_path=str(args.task_packet),
        worktree=str(getattr(args, "worktree", "") or getattr(args, "checkout", "")),
        branch=str(getattr(args, "branch", "") or ""),
        repo=str(getattr(args, "repo", "") or ""))
    successors = load_task_queue(str(getattr(args, "packet_queue", "") or ""))
    # Snapshot every successor's packet digest at queue-read time (CAS-once), so
    # a packet edited DURING the journey reads as stale at selection (R405).
    for entry in successors:
        try:
            snapshot_queued_digest(journal, entry.task_id, packet_digest(entry.packet_path))
        except NextTaskError:
            # An unreadable packet cannot be snapshotted; eligibility will refuse
            # it visibly when it is reached. No snapshot => no false freshness.
            pass

    ordered = [(first_entry, False)] + [(e, True) for e in successors]
    result = TaskQueueResult(dispatched=0, max_tasks=max_tasks, stop_reason="")
    last_run: dict[str, Any] | None = None
    dispatched = 0

    for entry, is_successor in ordered:
        # Crash-resume: a task already advanced is never re-run. It counts toward
        # the bound (it was dispatched in a prior process) and we move on.
        if is_advanced(journal, entry.task_id):
            result.steps.append(TaskQueueStep(entry.task_id, "already_advanced",
                                              "durable advancement record present"))
            dispatched += 1
            continue
        if dispatched >= max_tasks:
            result.stop_reason = "max_tasks_reached"
            result.steps.append(TaskQueueStep(entry.task_id, "bound",
                                              f"max-tasks={max_tasks} reached"))
            break
        if is_successor:
            seam = between_task_seam(journal, last_run, audit=audit)
            if seam:
                result.stop_reason = seam
                result.steps.append(TaskQueueStep(entry.task_id, "bound", seam))
                break
            verdict = evaluate_eligibility(
                entry, queued_digest=str(journal.get_state(
                    queued_digest_key(entry.task_id), "") or ""),
                primary_checkout=primary)
            if not verdict.eligible:
                _audit(audit, "cross_task_candidate_skipped",
                       task_id=entry.task_id, code=verdict.code, reason=verdict.reason)
                result.steps.append(TaskQueueStep(
                    entry.task_id, "skipped", f"{verdict.code}: {verdict.reason}"))
                continue
            # Re-bind the run to THIS successor's isolated worktree/branch/repo.
            args.task_packet = entry.packet_path
            args.worktree = entry.worktree
            if entry.branch:
                args.branch = entry.branch
            if entry.repo:
                args.repo = entry.repo

        _audit(audit, "cross_task_dispatch", task_id=entry.task_id,
               worktree=entry.worktree, successor=is_successor)
        run = run_one(args, checkout, journal, audit)
        last_run = run
        dispatched += 1
        result.provider_calls += int(run.get("provider_calls", 0) or 0)
        complete, checkpoint_id, why = run_reached_complete(run)
        if not complete:
            result.stop_reason = f"task_not_completed:{entry.task_id}"
            result.steps.append(TaskQueueStep(entry.task_id, "not_completed", why))
            break
        advancement = record_advancement(
            journal, task_id=entry.task_id, run_id=str(run.get("run_id", "") or ""),
            checkpoint_id=checkpoint_id, from_state=COMPLETE,
            evidence_refs=(f"run:{run.get('run_id', '')}", f"checkpoint:{checkpoint_id}"))
        if advancement.newly_recorded:
            result.advanced.append(entry.task_id)
        _audit(audit, "cross_task_advancement", task_id=entry.task_id,
               checkpoint_id=checkpoint_id, newly_recorded=advancement.newly_recorded)
        result.steps.append(TaskQueueStep(
            entry.task_id, "dispatched",
            "advanced" if advancement.newly_recorded else "already_advanced",
            checkpoint_id=checkpoint_id))
    else:
        # Fell off the end of the ordered list without breaking: either every
        # successor advanced, or all remaining were skipped ineligible.
        if not result.stop_reason:
            any_skipped = any(s.outcome == "skipped" for s in result.steps)
            result.stop_reason = NO_ELIGIBLE_WORK if any_skipped else "queue_exhausted"

    if last_run is None:
        # No task ever dispatched (e.g. task 1 already advanced on resume and no
        # eligible successor). Surface an honest, non-dispatched shape.
        return {"run_id": str(getattr(args, "run_id", "") or ""), "mode": args.mode,
                "final_state": IDLE, "stopped": result.stop_reason or NO_ELIGIBLE_WORK,
                "cycles": [], "budget": {"counted": 0, "budget": 0, "within_budget": True},
                "forwarded_message_ids": [], "provider_calls": 0, "rotations": [],
                "run_budget": None, "limited_auto_enabled": args.mode == "limited-auto",
                "task_queue": result.to_dict()}
    result.dispatched = dispatched
    last_run = dict(last_run)
    last_run["provider_calls"] = result.provider_calls
    last_run["task_queue"] = result.to_dict()
    return last_run
