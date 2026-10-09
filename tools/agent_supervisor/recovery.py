#!/usr/bin/env python3
"""Crash, sleep, reboot, and watchdog recovery (D-007 S11.5).

`RECOVER_BOOT` is the first state after any discontinuity, and it runs with no
prompts and no approvals. The algorithm here is S11.5's, in its order:

1. verify the controller manifest and the journal's integrity;
2. acquire the single-instance lock;
3. detect, terminate, or ACCOUNT FOR every surviving child;
4. detect competing writers;
5. revalidate task authority, stop flags, owner gates, branch, worktree,
   Git/remote state, auth, the CLI capability manifest, pending requests,
   scheduled deadlines, and the last external effect.

Then it classifies into exactly one of:

* ``SAFE_CHECKPOINT`` - resume automatically ONLY if limited-auto was ALREADY
  owner-enabled and nothing forbids it. This build never enables limited-auto, so
  in practice this always reports "resume permitted: no" with the reason;
* ``AMBIGUOUS_EFFECT`` - go to ``RECONCILE_EXTERNAL_EFFECT`` and prove via
  read-only evidence and the stable action id whether the effect occurred.
  Unprovable means ``PAUSED_RECOVERY``, never a blind rerun;
* ``UNSAFE_OR_DRIFTED`` - ``PAUSED_RECOVERY``, preserve evidence.

Two hard rules implemented as code, not prose:

* durable emergency-stop and manual-pause flags BEAT autostart
  (`autostart_permitted`), and
* interrupted-turn resumption is available only behind a recorded capability
  probe (`interrupted_turn_resumption`), otherwise the supervisor sends a
  digest-bound continuation from the last safe checkpoint.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping, Sequence

from .external_effects import (
    RECONCILED_NOT_OCCURRED,
    RECONCILED_OCCURRED,
    RECONCILIATION_IMPOSSIBLE,
)
from .locking import LockError, SingleInstanceLock, probe_process
from .models import digest_of, to_utc_iso
from .resume_scheduler import (
    EMERGENCY_STOP_KEY,
    MANUAL_PAUSE_KEY,
    RESUME_NOT_BEFORE_KEY,
)
from .state_machine import (
    PAUSED_RECOVERY,
    PREFLIGHT,
    RECONCILE_EXTERNAL_EFFECT,
    USAGE_LIMIT_WAIT,
)

SAFE_CHECKPOINT = "SAFE_CHECKPOINT"
AMBIGUOUS_EFFECT = "AMBIGUOUS_EFFECT"
UNSAFE_OR_DRIFTED = "UNSAFE_OR_DRIFTED"

CLASSIFICATIONS: tuple[str, ...] = (SAFE_CHECKPOINT, AMBIGUOUS_EFFECT, UNSAFE_OR_DRIFTED)

#: The transition trigger each classification uses out of RECOVER_BOOT.
CLASSIFICATION_TRIGGER: dict[str, tuple[str, str]] = {
    SAFE_CHECKPOINT: (PREFLIGHT, "recovery_safe_checkpoint"),
    AMBIGUOUS_EFFECT: (RECONCILE_EXTERNAL_EFFECT, "recovery_ambiguous_effect"),
    UNSAFE_OR_DRIFTED: (PAUSED_RECOVERY, "recovery_unsafe_or_drifted"),
}

OWNER_GATE_KEY = "owner_gate_open"
LIMITED_AUTO_KEY = "limited_auto_enabled"
CHILD_PROCESSES_KEY = "launched_child_processes"
RESUME_CAPABILITY_KEY = "interrupted_turn_capability_probe"
LAST_RECOVERY_KEY = "last_recovery_outcome"
#: M0-T126 (M0-T125 D6): a durable record set the moment a bounded unit is
#: dispatched and cleared when its outcome is journaled. An UNRECONCILED intent
#: at recovery time means the supervisor crashed mid-unit (its provider calls and
#: any brokered AUTO-tier effects may have run ONCE), so recovery classifies
#: AMBIGUOUS_EFFECT and reconciles rather than blindly re-dispatching the unit.
UNIT_DISPATCH_INTENT_KEY = "unit_dispatch_intent"
#: M0-T126 (M0-T125 D16): determined-dead child records from a crashed supervisor
#: are archived here with provenance instead of being re-probed forever.
ARCHIVED_DEAD_CHILDREN_KEY = "archived_dead_child_records"


class RecoveryError(Exception):
    """Recovery could not proceed. Always fails to a pause, never to a guess."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Durable flags
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class DurableFlags:
    """The flags that beat autostart, read from the journal (never from argv)."""

    emergency_stop: bool = False
    manual_pause: bool = False
    owner_gate_open: bool = False
    limited_auto_enabled: bool = False
    resume_not_before_utc: str = ""

    @classmethod
    def read(cls, journal: Any) -> "DurableFlags":
        return cls(
            emergency_stop=bool(journal.get_state(EMERGENCY_STOP_KEY, False)),
            manual_pause=bool(journal.get_state(MANUAL_PAUSE_KEY, False)),
            owner_gate_open=bool(journal.get_state(OWNER_GATE_KEY, False)),
            limited_auto_enabled=bool(journal.get_state(LIMITED_AUTO_KEY, False)),
            resume_not_before_utc=str(journal.get_state(RESUME_NOT_BEFORE_KEY, "") or ""),
        )

    def blocking_reasons(self) -> tuple[str, ...]:
        reasons: list[str] = []
        if self.emergency_stop:
            reasons.append("a durable emergency stop is set")
        if self.manual_pause:
            reasons.append("a durable manual pause is set")
        if self.owner_gate_open:
            reasons.append("a blocking owner gate is open")
        if self.resume_not_before_utc:
            reasons.append(f"a usage-limit deadline holds until "
                           f"{self.resume_not_before_utc}")
        return tuple(reasons)


def autostart_permitted(flags: DurableFlags) -> tuple[bool, str]:
    """S11.5: durable emergency-stop and manual-pause flags ALWAYS beat autostart."""
    reasons = flags.blocking_reasons()
    if reasons:
        return False, ("autostart refused: " + "; ".join(reasons)
                       + ". A durable stop or pause never clears itself and never yields "
                         "to a startup task (S11.5)")
    return True, "no durable flag forbids starting"


# --------------------------------------------------------------------------
# Child-process accounting (S11.5 step 3)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ChildAccount:
    """One recorded child process and what became of it."""

    pid: int
    role: str
    recorded_start_token: str
    surviving: bool
    determined: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def account_for_children(journal: Any) -> tuple[ChildAccount, ...]:
    """Detect and account for every child the supervisor recorded launching.

    A pid whose liveness cannot be determined is `determined=False` and counts as
    UNACCOUNTED - the classifier treats that as drift, not as "probably gone".
    """
    recorded = journal.get_state(CHILD_PROCESSES_KEY, []) or []
    accounts: list[ChildAccount] = []
    for entry in recorded:
        if not isinstance(entry, Mapping):
            continue
        pid = int(entry.get("pid", 0) or 0)
        token = str(entry.get("start_token", ""))
        probe = probe_process(pid)
        surviving = probe.determined and probe.alive
        if surviving and token and probe.start_token and token != probe.start_token:
            # The pid was reused; the original child is gone.
            surviving = False
            detail = "pid reused by an unrelated process; the recorded child is gone"
        else:
            detail = probe.detail
        accounts.append(ChildAccount(pid, str(entry.get("role", "unknown")), token,
                                     surviving, probe.determined, detail))
    return tuple(accounts)


def record_launched_child(journal: Any, *, pid: int, role: str,
                          start_token: str = "") -> None:
    """Record a launched child so a later recovery can account for it."""
    recorded = list(journal.get_state(CHILD_PROCESSES_KEY, []) or [])
    recorded.append({"pid": pid, "role": role, "start_token": start_token,
                     "launched_at_utc": to_utc_iso()})
    journal.set_state(CHILD_PROCESSES_KEY, recorded)


def clear_child_record(journal: Any, *, pid: int, start_token: str = "") -> None:
    """Remove ONLY the recorded child matching ``(pid, start_token)``.

    A settle clears exactly the one child it launched and reaped; every other
    recorded child stays intact. Wiping the whole key here (the pre-M0-T059
    behavior) is latent today with a single recorder, but fails OPEN on the
    no-duplicate-workers invariant the moment a second child is recorded - one
    worker's clean exit would erase a live successor's record (M0-T053 G5
    finding 5; D-010-R347). ``start_token`` disambiguates a reused pid: an entry
    whose recorded token differs is an unrelated process and is left untouched.
    """
    recorded = journal.get_state(CHILD_PROCESSES_KEY, []) or []
    remaining = [
        entry for entry in recorded
        if not (isinstance(entry, Mapping)
                and int(entry.get("pid", 0) or 0) == pid
                and str(entry.get("start_token", "")) == start_token)
    ]
    journal.set_state(CHILD_PROCESSES_KEY, remaining)


def recorded_start_token_for(journal: Any, pid: int) -> str:
    """The ``start_token`` recorded for ``pid`` ('' when the pid is not recorded).

    A settle recovers the exact token it journaled at launch so it can clear
    precisely its own entry: the launch-time token (the process creation stamp)
    cannot be re-derived once the child has exited, so the durable record is the
    only faithful source.
    """
    recorded = journal.get_state(CHILD_PROCESSES_KEY, []) or []
    for entry in recorded:
        if isinstance(entry, Mapping) and int(entry.get("pid", 0) or 0) == pid:
            return str(entry.get("start_token", ""))
    return ""


# --------------------------------------------------------------------------
# Unit dispatch intent (M0-T126; defect D6)
# --------------------------------------------------------------------------


def record_dispatch_intent(journal: Any, *, run_id: str, cycle: int) -> None:
    """Journal that a bounded unit is ABOUT to be dispatched (D6).

    Set BEFORE the provider is contacted. A crash before ``reconcile_dispatch_
    intent`` leaves this pending, and recovery then classifies AMBIGUOUS_EFFECT
    (the unit's provider calls / brokered effects may have run once) instead of
    re-dispatching over them.
    """
    journal.set_state(UNIT_DISPATCH_INTENT_KEY,
                      {"pending": True, "run_id": run_id, "cycle": cycle,
                       "dispatched_at_utc": to_utc_iso()})


def reconcile_dispatch_intent(journal: Any) -> None:
    """Clear the dispatch intent once the unit's outcome is durably journaled."""
    journal.set_state(UNIT_DISPATCH_INTENT_KEY, {"pending": False,
                                                 "reconciled_at_utc": to_utc_iso()})


def pending_dispatch_intent(journal: Any) -> dict | None:
    """The unreconciled dispatch intent, or None."""
    value = journal.get_state(UNIT_DISPATCH_INTENT_KEY, None)
    if isinstance(value, Mapping) and value.get("pending"):
        return dict(value)
    return None


# --------------------------------------------------------------------------
# Dead-child archive sweep (M0-T126; defect D16)
# --------------------------------------------------------------------------


def sweep_dead_child_records(journal: Any, *, audit: Any = None) -> tuple[dict, ...]:
    """Archive DETERMINED-DEAD child records with provenance; keep the rest.

    A child whose liveness was DETERMINED and is NOT alive (and not a
    same-pid/token survivor) is gone; the launching runner's settle normally
    clears it, but a record from a CRASHED supervisor persists and is re-probed
    on every recovery forever. This moves each such record to the archive key
    with an archived-at stamp, leaving surviving/undetermined records untouched
    (they still count as drift). Returns the archived records.
    """
    recorded = journal.get_state(CHILD_PROCESSES_KEY, []) or []
    keep: list[dict] = []
    archived: list[dict] = []
    for entry in recorded:
        if not isinstance(entry, Mapping):
            continue
        probe = probe_process(int(entry.get("pid", 0) or 0))
        token = str(entry.get("start_token", ""))
        reused = (probe.determined and probe.alive and token and probe.start_token
                  and token != probe.start_token)
        dead = probe.determined and (not probe.alive or reused)
        if dead:
            archived.append({**dict(entry), "archived_at_utc": to_utc_iso(),
                             "archive_reason": ("pid reused" if reused
                                                else "determined dead")})
        else:
            keep.append(dict(entry))
    if archived:
        prior = list(journal.get_state(ARCHIVED_DEAD_CHILDREN_KEY, []) or [])
        journal.set_state(ARCHIVED_DEAD_CHILDREN_KEY, prior + archived)
        journal.set_state(CHILD_PROCESSES_KEY, keep)
        if audit is not None:
            audit.append("dead_child_records_archived",
                         detail={"archived": len(archived), "kept": len(keep)})
    return tuple(archived)


# --------------------------------------------------------------------------
# Revalidation inputs
# --------------------------------------------------------------------------

#: Everything S11.5 requires be revalidated after a discontinuity. A step absent
#: from the supplied results is a FAILURE, not an omission.
REVALIDATION_STEPS: tuple[str, ...] = (
    "controller_manifest",
    "journal_integrity",
    "audit_chain",
    "task_authority",
    "branch",
    "worktree",
    "git_and_remote_state",
    "auth",
    "cli_capability_manifest",
    "pending_requests",
    "scheduled_deadlines",
    "last_external_effect",
)


@dataclasses.dataclass(frozen=True)
class RecoveryContext:
    """Everything the classifier needs. The caller collects it read-only."""

    revalidation: Mapping[str, bool]
    competing_writer_detected: bool = False
    competing_writer_detail: str = ""
    pending_effect_ids: tuple[str, ...] = ()
    lock_acquired: bool = True
    lock_detail: str = ""
    children: tuple[ChildAccount, ...] = ()
    flags: DurableFlags = dataclasses.field(default_factory=DurableFlags)
    notes: tuple[str, ...] = ()
    #: M0-T126 (M0-T125 D6): a bounded unit was dispatched and its outcome was
    #: never reconciled - the supervisor crashed mid-unit. Additive: defaults
    #: False, so a recovery that records no dispatch intent is classified exactly
    #: as before.
    dispatch_intent_pending: bool = False


@dataclasses.dataclass(frozen=True)
class RecoveryOutcome:
    """The classification and exactly what may happen next."""

    classification: str
    next_state: str
    trigger: str
    reason_code: str
    reason: str
    resume_permitted: bool
    failed_steps: tuple[str, ...] = ()
    missing_steps: tuple[str, ...] = ()
    unaccounted_children: tuple[int, ...] = ()
    pending_effect_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, tuple):
                data[key] = list(value)
        return data

    def digest(self) -> str:
        return digest_of(self.to_dict())


def classify(context: RecoveryContext) -> RecoveryOutcome:
    """The S11.5 classification. Order matters: UNSAFE dominates AMBIGUOUS."""
    unknown = sorted(set(context.revalidation) - set(REVALIDATION_STEPS))
    if unknown:
        raise RecoveryError("unknown_revalidation_step",
                            f"unrecognized revalidation steps: {unknown}")
    missing = tuple(s for s in REVALIDATION_STEPS if s not in context.revalidation)
    failed = tuple(s for s in REVALIDATION_STEPS
                   if s in context.revalidation and not context.revalidation[s])
    unaccounted = tuple(child.pid for child in context.children
                        if child.surviving or not child.determined)

    # --- UNSAFE_OR_DRIFTED ------------------------------------------------
    unsafe_reasons: list[str] = []
    if not context.lock_acquired:
        unsafe_reasons.append(
            f"the single-instance lock could not be acquired ({context.lock_detail})")
    if failed:
        unsafe_reasons.append(f"revalidation failed for {list(failed)}")
    if missing:
        unsafe_reasons.append(
            f"revalidation results were missing for {list(missing)}; a missing check is a "
            f"failed check")
    if context.competing_writer_detected:
        unsafe_reasons.append(
            f"a competing writer was detected ({context.competing_writer_detail})")
    if unaccounted:
        unsafe_reasons.append(
            f"child processes {list(unaccounted)} survived the discontinuity or could not be "
            f"determined")
    if unsafe_reasons:
        return RecoveryOutcome(
            UNSAFE_OR_DRIFTED, PAUSED_RECOVERY, "recovery_unsafe_or_drifted",
            "unsafe_or_drifted",
            "integrity, authority, identity, repository, toolchain, auth, or policy no "
            "longer matches: " + "; ".join(unsafe_reasons)
            + ". Pausing synchronously and preserving evidence (S11.5)",
            False, failed, missing, unaccounted, context.pending_effect_ids, context.notes)

    # --- AMBIGUOUS_EFFECT --------------------------------------------------
    if context.pending_effect_ids:
        return RecoveryOutcome(
            AMBIGUOUS_EFFECT, RECONCILE_EXTERNAL_EFFECT, "recovery_ambiguous_effect",
            "ambiguous_effect",
            f"{len(context.pending_effect_ids)} external effect(s) were journaled before the "
            f"discontinuity with no verified after-effect: "
            f"{list(context.pending_effect_ids)}. Proving whether each occurred, via "
            f"read-only evidence and the stable action id - never a blind rerun (S11.5)",
            False, (), (), (), context.pending_effect_ids, context.notes)

    # M0-T126 (M0-T125 D6): a bounded unit was dispatched with no reconciled
    # outcome - the supervisor crashed mid-unit. Its provider calls and any
    # brokered AUTO-tier effects may have run ONCE. Classify AMBIGUOUS_EFFECT and
    # reconcile the unit's effect before any re-dispatch, rather than treating a
    # determined-dead child as SAFE and dispatching the unit again.
    if context.dispatch_intent_pending:
        return RecoveryOutcome(
            AMBIGUOUS_EFFECT, RECONCILE_EXTERNAL_EFFECT, "recovery_ambiguous_effect",
            "unit_dispatch_unreconciled",
            "a bounded unit was dispatched before the discontinuity with no "
            "reconciled outcome; the supervisor crashed mid-unit. Reconcile "
            "whether the unit's provider calls and brokered effects took effect "
            "via read-only evidence before any re-dispatch - never a blind rerun "
            "(S11.5; M0-T125 D6)",
            False, (), (), (), (), context.notes)

    # --- SAFE_CHECKPOINT ---------------------------------------------------
    permitted, why = autostart_permitted(context.flags)
    if not permitted:
        return RecoveryOutcome(
            SAFE_CHECKPOINT, PAUSED_RECOVERY, "recovery_unsafe_or_drifted",
            "safe_but_forbidden",
            f"the last action has a verified after-effect and every invariant matches, but "
            f"{why}",
            False, notes=context.notes)
    if not context.flags.limited_auto_enabled:
        return RecoveryOutcome(
            SAFE_CHECKPOINT, PREFLIGHT, "recovery_safe_checkpoint",
            "safe_no_auto_resume",
            "the last action has a verified after-effect and every invariant matches, but "
            "limited-auto was NOT already owner-enabled, so recovery does not resume by "
            "itself: it re-runs preflight and waits for an explicit operator start (S11.5). "
            "Recovery never enables or broadens limited-auto",
            False, notes=context.notes)
    # M0-T126 (M0-T125 D7): this `safe_auto_resume` branch (resume_permitted=True)
    # is R595-GATED and therefore UNREACHABLE on this build: it fires only when
    # `flags.limited_auto_enabled` is True, but that durable key has ONLY
    # False-writers (broker.py; remote_approvals.py:295/307) until the owner's
    # R595 activation path sets it, so `autostart_permitted`/the branch above
    # always land first. It is kept (not deleted) as the exact edge R595 will
    # enable, and is documented here rather than looking like dead code.
    return RecoveryOutcome(
        SAFE_CHECKPOINT, PREFLIGHT, "recovery_safe_checkpoint", "safe_auto_resume",
        "verified safe checkpoint with limited-auto already owner-enabled and nothing "
        "forbidding it: resuming automatically. This is a NOTIFY event (S11.5). "
        "R595-gated: reachable only once the owner's activation path enables "
        "limited-auto (M0-T125 D7)",
        True, notes=context.notes)


# --------------------------------------------------------------------------
# External-effect reconciliation (S11.5 AMBIGUOUS_EFFECT)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ReconciliationVerdict:
    resolved: bool
    action_id: str
    status: str
    next_state: str
    trigger: str
    reason: str
    evidence: tuple[str, ...] = ()


def reconcile_effect(
    effects: Any,
    action_id: str,
    *,
    prober: Any,
) -> ReconciliationVerdict:
    """Prove whether ONE pending effect occurred, using read-only evidence.

    `prober` is the caller's read-only evidence function (a Git query, a provider
    read, a filesystem check) bound to the stable action id. It returns
    `(occurred, observed_state)` where `occurred` may be None for "cannot be
    determined" - which lands in PAUSED_RECOVERY, never in a retry.
    """
    result = effects.reconcile(action_id, prober)
    status = getattr(result, "status", RECONCILIATION_IMPOSSIBLE)
    evidence = tuple(x for x in (getattr(result, "observed_state", ""),
                                 getattr(result, "detail", "")) if x)
    if status == RECONCILED_OCCURRED:
        return ReconciliationVerdict(
            True, action_id, status, PREFLIGHT, "effect_proven_reconciled",
            "read-only evidence proved the effect DID occur; it is recorded complete and is "
            "never rerun", evidence)
    if status == RECONCILED_NOT_OCCURRED:
        return ReconciliationVerdict(
            True, action_id, status, PREFLIGHT, "effect_proven_reconciled",
            "read-only evidence proved the effect did NOT occur; the unit may be retried "
            "under its original approval", evidence)
    return ReconciliationVerdict(
        False, action_id, RECONCILIATION_IMPOSSIBLE, PAUSED_RECOVERY, "effect_unprovable",
        "whether the effect occurred could not be proven either way; S11.5 requires a "
        "synchronous stop rather than a blind rerun", evidence)


# --------------------------------------------------------------------------
# Interrupted-turn resumption gate (S11.5)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ResumptionPlan:
    """How the supervisor re-enters a session after a discontinuity."""

    mode: str
    reason: str
    session_id: str = ""
    continuation_digest: str = ""


def interrupted_turn_resumption(
    journal: Any,
    *,
    session_id: str,
    last_safe_checkpoint_digest: str,
) -> ResumptionPlan:
    """Interrupted-turn resumption ONLY behind a recorded capability probe.

    The probe record must state that duplication of a pending tool or action was
    tested and proven impossible. Absent that, the supervisor sends a
    digest-bound continuation from the last safe checkpoint instead.
    """
    probe = journal.get_state(RESUME_CAPABILITY_KEY)
    proven = (isinstance(probe, Mapping)
              and bool(probe.get("proves_no_duplicate_pending_action", False))
              and bool(probe.get("tested_against_installed_cli", False)))
    if proven:
        return ResumptionPlan(
            "interrupted_turn", session_id=session_id,
            reason=f"a recorded capability probe ({probe.get('probe_id', 'unnamed')}) proved "
                   f"interrupted-turn resumption cannot duplicate a pending tool or action "
                   f"on the installed CLI")
    return ResumptionPlan(
        "digest_bound_continuation", session_id=session_id,
        continuation_digest=last_safe_checkpoint_digest,
        reason="interrupted-turn resumption is NOT enabled: no capability probe has proven "
               "it cannot duplicate a pending tool or action. Sending a digest-bound "
               "continuation from the last safe checkpoint instead (S11.5)")


def codex_recovery_plan() -> dict[str, Any]:
    """Codex recovery discards partial output and reruns fresh (S11.5)."""
    return {
        "discard_partial_output": True,
        "rerun": "fresh process from the persisted packet",
        "resume_partial_review": False,
        "reason": "a partially written review is not evidence; S11.5 reruns it from the "
                  "persisted packet rather than interpreting a fragment",
    }


# --------------------------------------------------------------------------
# The RECOVER_BOOT driver
# --------------------------------------------------------------------------


def recover_boot(
    *,
    journal: Any,
    lock: SingleInstanceLock | None,
    revalidation: Mapping[str, bool],
    competing_writer: tuple[bool, str] = (False, ""),
    audit: Any = None,
    notes: Sequence[str] = (),
) -> RecoveryOutcome:
    """Run the S11.5 RECOVER_BOOT algorithm. No prompts, no approvals, no provider calls.

    The scheduled-deadline branch is checked FIRST: S11.5 says a recovery that
    finds `USAGE_LIMIT_WAIT`/`SCHEDULED_RESUME` restores the timer without
    contacting any provider before `resume_not_before_utc`.
    """
    flags = DurableFlags.read(journal)

    lock_acquired, lock_detail = True, "no lock object supplied"
    if lock is not None:
        try:
            lock.acquire()
            lock_detail = "single-instance lock acquired"
            if lock.took_over_stale is not None:
                lock_detail += f" (took over a stale lock: {lock.took_over_stale.detail})"
        except LockError as exc:
            lock_acquired, lock_detail = False, exc.message

    children = account_for_children(journal)
    pending = tuple(effect.action_id for effect in journal.pending_effects())

    context = RecoveryContext(
        revalidation=dict(revalidation),
        competing_writer_detected=bool(competing_writer[0]),
        competing_writer_detail=str(competing_writer[1]),
        pending_effect_ids=pending,
        lock_acquired=lock_acquired,
        lock_detail=lock_detail,
        children=children,
        flags=flags,
        notes=tuple(notes),
        # M0-T126 (D6): an unreconciled dispatch intent means a crash mid-unit.
        dispatch_intent_pending=pending_dispatch_intent(journal) is not None,
    )
    outcome = classify(context)

    # M0-T126 (D16): archive determined-dead child records with provenance so a
    # crashed supervisor's stale pid records are not re-probed on every recovery
    # forever. Runs AFTER classify (which already accounted for them), and never
    # touches surviving/undetermined records - so it cannot mask drift.
    sweep_dead_child_records(journal, audit=audit)

    # A restored deadline overrides an otherwise-safe resume: no provider work
    # before resume_not_before_utc, even from a clean checkpoint.
    if outcome.classification == SAFE_CHECKPOINT and flags.resume_not_before_utc:
        outcome = dataclasses.replace(
            outcome, next_state=USAGE_LIMIT_WAIT, trigger="recovery_restores_deadline",
            reason_code="deadline_restored", resume_permitted=False,
            reason=f"recovery found a persisted usage-limit deadline "
                   f"({flags.resume_not_before_utc}); restoring the timer and contacting no "
                   f"provider before it (S11.5)")

    journal.set_state(LAST_RECOVERY_KEY, outcome.to_dict())
    if audit is not None:
        audit.append("recover_boot", policy_result=outcome.classification,
                     detail={"reason_code": outcome.reason_code,
                             "next_state": outcome.next_state,
                             "resume_permitted": outcome.resume_permitted,
                             "lock": lock_detail,
                             "outcome_digest": outcome.digest()})
    return outcome


def last_outcome(journal: Any) -> dict[str, Any] | None:
    data = journal.get_state(LAST_RECOVERY_KEY)
    return data if isinstance(data, dict) else None


# --------------------------------------------------------------------------
# Durable pause / stop / resume
# --------------------------------------------------------------------------


def set_manual_pause(journal: Any, *, paused: bool, reason: str,
                     audit: Any = None) -> dict[str, Any]:
    journal.set_state(MANUAL_PAUSE_KEY, bool(paused))
    record = {"manual_pause": bool(paused), "reason": reason, "at_utc": to_utc_iso()}
    if audit is not None:
        audit.append("manual_pause_set" if paused else "manual_pause_cleared", detail=record)
    return record


def set_emergency_stop(journal: Any, *, reason: str, audit: Any = None) -> dict[str, Any]:
    """Set the durable stop flag. It never clears itself and beats every autostart."""
    journal.set_state(EMERGENCY_STOP_KEY, True)
    record = {"emergency_stop": True, "reason": reason, "at_utc": to_utc_iso(),
              "clears_by": "an explicit owner command only"}
    if audit is not None:
        audit.append("emergency_stop_set", detail=record)
    return record


def clear_emergency_stop(journal: Any, *, owner_command: bool,
                         audit: Any = None) -> dict[str, Any]:
    if not owner_command:
        raise RecoveryError(
            "stop_requires_owner",
            "a durable emergency stop is cleared only by an explicit owner command; nothing "
            "in the loop, no recovery path, and no schedule may clear it")
    journal.set_state(EMERGENCY_STOP_KEY, False)
    record = {"emergency_stop": False, "at_utc": to_utc_iso()}
    if audit is not None:
        audit.append("emergency_stop_cleared", detail=record)
    return record
