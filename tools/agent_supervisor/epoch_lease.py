"""Renewable controller epoch lease and exact-once succession
(D-024 Phase D, M0-T092; R028/R030/R031/R102).

R028: continuity is a renewable sequence of bounded epochs, never one immortal
process — one durable campaign identity, ONE active controller lease at a time,
exact-once succession, crash recovery from durable state. This module is the
durable lease itself; nothing here spawns, resumes, stops, or messages a
session (SHADOW-ONLY, R595 untouched).

What already existed, and why this module is still owed (R018 prove-first):

* ``locking.SingleInstanceLock`` — a PROCESS-liveness lock for one checkout.
  It answers "is another supervisor process alive right now"; it does not
  survive as an epoch record, cannot say WHICH bounded epoch owns the
  campaign, and releases on process death — exactly when succession needs a
  durable answer.
* ``lease_runtime.LeaseLedger`` — in-memory WRITE-SCOPE leases for subagent
  assignments inside one controller. It serializes producer file scopes, not
  controller succession, and does not survive a restart.
* ``campaign_continuity.CampaignRecord`` — the durable campaign IDENTITY and
  next-action pointer, with stale-read detection only ("NOT a cross-process
  lock ... true cross-process exact-once belongs to the external controller
  lease (Phase D)" — its own docstring names this module as the missing half).

The lease record lives in the ``DurableJournal`` (same SQLite file as every
other durable controller fact), and every mutation goes through
``DurableJournal.compare_and_swap_state`` — the read, the comparison, and the
write in ONE ``BEGIN IMMEDIATE`` transaction — so two contenders, even in two
OS processes on the same journal, can never both win (R030: a restart must not
create two controllers or two successors).

Clock discipline: every liveness decision takes an injected ``now`` in POSIX
epoch seconds (``run_budget.system_clock`` is the production wiring); wall-time
strings are display metadata only. A lease RENEWS or EXPIRES; it never forks.

Supervisor-freeze qualifying evidence: D-024-R102.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping, Sequence

from .models import to_utc_iso
from .telemetry_records import Measurement

#: The single durable lease record. One key — one active lease at a time is a
#: structural fact, not a convention (R028).
LEASE_KEY = "controller_epoch_lease"

#: Bounded, durable succession history (newest last). Bounded so the journal
#: never grows without limit; the transitions table remains the full audit.
SUCCESSION_LOG_KEY = "controller_epoch_successions"
SUCCESSION_LOG_BOUND = 50


class LeaseError(Exception):
    """A lease rule was violated or a race was lost. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class EpochLease:
    """One bounded controller epoch: who owns the campaign, until when."""

    campaign_id: str
    epoch: int
    owner_run_id: str
    ttl_seconds: float
    renew_by_epoch_seconds: float
    acquired_at_utc: str
    released: bool = False

    def __post_init__(self) -> None:
        if not self.campaign_id or not self.owner_run_id:
            raise LeaseError("missing_identity",
                             "a lease names its campaign_id and owner_run_id")
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) \
                or self.epoch < 1:
            raise LeaseError("bad_epoch",
                             f"epoch must be a positive integer, got {self.epoch!r}")
        if not (isinstance(self.ttl_seconds, (int, float))
                and self.ttl_seconds > 0):
            raise LeaseError("bad_ttl",
                             f"ttl_seconds must be positive, got {self.ttl_seconds!r}; "
                             f"an unbounded epoch is an immortal process (R028)")

    def expired(self, now: float) -> bool:
        return float(now) > self.renew_by_epoch_seconds

    def live(self, now: float) -> bool:
        return not self.released and not self.expired(now)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EpochLease":
        if not isinstance(data, Mapping):
            raise LeaseError("unreadable_lease",
                             "the stored lease record is not a mapping; recovery "
                             "must stop rather than guess (R030)")
        try:
            return cls(
                campaign_id=str(data["campaign_id"]),
                epoch=int(data["epoch"]),
                owner_run_id=str(data["owner_run_id"]),
                ttl_seconds=float(data["ttl_seconds"]),
                renew_by_epoch_seconds=float(data["renew_by_epoch_seconds"]),
                acquired_at_utc=str(data.get("acquired_at_utc", "")),
                released=bool(data.get("released", False)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise LeaseError("unreadable_lease",
                             f"the stored lease record is malformed ({exc}); "
                             f"fail closed, never guess") from exc


def current_lease(journal: Any) -> EpochLease | None:
    """The stored lease, or None when none was ever taken. Malformed raises."""
    data = journal.get_state(LEASE_KEY, None)
    if data is None:
        return None
    return EpochLease.from_dict(data)


def acquire_first(
    journal: Any, *, campaign_id: str, owner_run_id: str, now: float,
    ttl_seconds: float, audit: Any = None,
) -> EpochLease:
    """Take epoch 1 of a campaign that has never had a lease.

    Single-winner: the insert is a compare-and-swap against ABSENCE, so two
    first-boot contenders resolve to exactly one epoch-1 owner. A journal that
    already carries any lease record — live, released, or expired — refuses;
    every later epoch is taken through :func:`succeed` so the sequence stays
    renewable and gapless (R028).
    """
    lease = EpochLease(
        campaign_id=campaign_id, epoch=1, owner_run_id=owner_run_id,
        ttl_seconds=float(ttl_seconds),
        renew_by_epoch_seconds=float(now) + float(ttl_seconds),
        acquired_at_utc=to_utc_iso())
    if not journal.compare_and_swap_state(LEASE_KEY, None, lease.to_dict()):
        raise LeaseError(
            "lease_exists",
            "a lease record already exists for this journal; epoch 1 is taken "
            "at most once and every later epoch goes through succeed() "
            "(exact-once, R028/R030)")
    _audit(audit, "epoch_lease_acquired", lease, "")
    return lease


def renew(journal: Any, *, owner_run_id: str, now: float,
          audit: Any = None) -> EpochLease:
    """Extend the CURRENT owner's live lease by its own ttl. Renew or expire —
    never fork: a non-owner, a released lease, and an expired lease all refuse
    (an expired lease is succeeded, not revived)."""
    stored = current_lease(journal)
    if stored is None:
        raise LeaseError("no_lease", "no lease exists to renew")
    if stored.owner_run_id != owner_run_id:
        raise LeaseError(
            "not_owner",
            f"run {owner_run_id!r} does not own the lease (owner is "
            f"{stored.owner_run_id!r}); a renewal by anyone else would fork "
            f"the controller (R028)")
    if stored.released:
        raise LeaseError("lease_released",
                         "a released lease is never renewed; take the next "
                         "epoch through succeed()")
    if stored.expired(now):
        raise LeaseError(
            "lease_expired",
            f"the epoch-{stored.epoch} lease expired at "
            f"{stored.renew_by_epoch_seconds}; an expired lease is succeeded, "
            f"never revived (R028)")
    renewed = dataclasses.replace(
        stored, renew_by_epoch_seconds=float(now) + stored.ttl_seconds)
    if not journal.compare_and_swap_state(LEASE_KEY, stored.to_dict(),
                                          renewed.to_dict()):
        raise LeaseError("lost_race",
                         "the lease changed under this renewal; re-read and "
                         "re-decide (single-winner CAS, R030)")
    _audit(audit, "epoch_lease_renewed", renewed, "")
    return renewed


def release(journal: Any, *, owner_run_id: str,
            audit: Any = None) -> EpochLease:
    """The owner's explicit hand-back at a safe seam. Marks the record
    released (history preserved); it never deletes the lease row."""
    stored = current_lease(journal)
    if stored is None:
        raise LeaseError("no_lease", "no lease exists to release")
    if stored.owner_run_id != owner_run_id:
        raise LeaseError(
            "not_owner",
            f"run {owner_run_id!r} does not own the lease (owner is "
            f"{stored.owner_run_id!r}); only the owner releases it")
    if stored.released:
        return stored  # idempotent: releasing twice is a no-op, not an error
    released = dataclasses.replace(stored, released=True)
    if not journal.compare_and_swap_state(LEASE_KEY, stored.to_dict(),
                                          released.to_dict()):
        raise LeaseError("lost_race",
                         "the lease changed under this release; re-read and "
                         "re-decide (single-winner CAS, R030)")
    _audit(audit, "epoch_lease_released", released, "")
    return released


def succeed(
    journal: Any, *, expected_epoch: int, new_owner_run_id: str, now: float,
    ttl_seconds: float, audit: Any = None,
    usage: Measurement | None = None,
) -> EpochLease:
    """Exact-once succession: epoch N -> N+1 with EXACTLY ONE winner.

    The predecessor must be RELEASED or EXPIRED — a live controller is never
    taken over (R028: one active controller lease at a time; the watchdog path
    for a live-but-crashed owner is :func:`reconcile_on_boot`, which resumes
    the SAME epoch rather than minting a new one). Two successors racing the
    same ``expected_epoch`` resolve through the CAS: the loser gets a typed
    ``succession_race_lost`` and must dispatch nothing (R030/R031).

    ``usage``: any usage number recorded WITH this succession decision must be
    a labelled :class:`telemetry_records.Measurement` — source/confidence
    named, missing is unknown and never zero (R042).
    """
    stored = current_lease(journal)
    if stored is None:
        raise LeaseError("no_lease",
                         "no lease exists to succeed; a first boot takes "
                         "epoch 1 through acquire_first()")
    if stored.epoch != int(expected_epoch):
        raise LeaseError(
            "succession_race_lost",
            f"succession expected epoch {expected_epoch} but the journal is at "
            f"epoch {stored.epoch}; another successor already won — this "
            f"contender dispatches NOTHING (exactly one winner, R030)")
    if stored.live(now):
        raise LeaseError(
            "predecessor_live",
            f"the epoch-{stored.epoch} lease is still live (owner "
            f"{stored.owner_run_id!r}, renew-by "
            f"{stored.renew_by_epoch_seconds}); a live controller is never "
            f"taken over (R028)")
    successor = EpochLease(
        campaign_id=stored.campaign_id, epoch=stored.epoch + 1,
        owner_run_id=new_owner_run_id, ttl_seconds=float(ttl_seconds),
        renew_by_epoch_seconds=float(now) + float(ttl_seconds),
        acquired_at_utc=to_utc_iso())
    if not journal.compare_and_swap_state(LEASE_KEY, stored.to_dict(),
                                          successor.to_dict()):
        raise LeaseError(
            "succession_race_lost",
            "another successor committed first; this contender dispatches "
            "NOTHING (exactly one winner, R030)")
    entry: dict[str, Any] = {
        "from_epoch": stored.epoch,
        "to_epoch": successor.epoch,
        "previous_owner_run_id": stored.owner_run_id,
        "new_owner_run_id": new_owner_run_id,
        "predecessor_state": "released" if stored.released else "expired",
        "at_utc": successor.acquired_at_utc,
    }
    if usage is not None:
        entry["usage"] = usage.to_dict() if hasattr(usage, "to_dict") \
            else dataclasses.asdict(usage)
    log = list(journal.get_state(SUCCESSION_LOG_KEY, []) or [])
    log.append(entry)
    journal.set_state(SUCCESSION_LOG_KEY, log[-SUCCESSION_LOG_BOUND:])
    _audit(audit, "epoch_lease_succeeded", successor,
           f"from epoch {stored.epoch} ({entry['predecessor_state']})")
    return successor


# --------------------------------------------------------------------------
# Boot reconciliation (R031 class 2: controller-process crash)
# --------------------------------------------------------------------------

NO_LEASE = "no_lease"
OWN_LEASE_LIVE = "own_lease_live"
OTHER_LEASE_LIVE = "other_lease_live"
TAKEOVER_ELIGIBLE = "takeover_eligible"

BOOT_STATUSES: tuple[str, ...] = (
    NO_LEASE, OWN_LEASE_LIVE, OTHER_LEASE_LIVE, TAKEOVER_ELIGIBLE)


@dataclasses.dataclass(frozen=True)
class BootLeaseOutcome:
    """What a (re)starting controller may do about the lease, and why."""

    status: str
    reason: str
    lease: EpochLease | None = None

    @property
    def resumes_same_epoch(self) -> bool:
        """True when this boot RESUMES its own live epoch — a watchdog restart
        continues the epoch it owns and never mints a successor (R031)."""
        return self.status == OWN_LEASE_LIVE


def reconcile_on_boot(journal: Any, *, run_id: str,
                      now: float) -> BootLeaseOutcome:
    """Classify the lease at boot. Read-only: this never mutates the record.

    * our own live lease -> resume the SAME epoch (no duplicate controller);
    * someone else's live lease -> bounded READ-ONLY orientation only;
    * a released or expired lease -> takeover-eligible via :func:`succeed`;
    * no lease -> first boot via :func:`acquire_first`.
    """
    stored = current_lease(journal)
    if stored is None:
        return BootLeaseOutcome(
            NO_LEASE, "no lease record exists; a first boot takes epoch 1 "
                      "through acquire_first()")
    if stored.live(now):
        if stored.owner_run_id == run_id:
            return BootLeaseOutcome(
                OWN_LEASE_LIVE,
                f"this run already owns the live epoch-{stored.epoch} lease; "
                f"a restart RESUMES the same epoch and never creates a second "
                f"controller or successor (R030/R031)", stored)
        return BootLeaseOutcome(
            OTHER_LEASE_LIVE,
            f"run {stored.owner_run_id!r} holds the live epoch-{stored.epoch} "
            f"lease; this session may orient READ-ONLY while it drains, and "
            f"must not take a conflicting write lease or dispatch writes "
            f"(R031/R065)", stored)
    state = "released" if stored.released else "expired"
    return BootLeaseOutcome(
        TAKEOVER_ELIGIBLE,
        f"the epoch-{stored.epoch} lease is {state}; succession through "
        f"succeed(expected_epoch={stored.epoch}) is eligible and will have "
        f"exactly one winner", stored)


def may_orient_read_only(outcome: BootLeaseOutcome) -> bool:
    """Bounded read-only orientation is ALWAYS permitted (R031/R065)."""
    return True


def may_dispatch_writes(
    outcome: BootLeaseOutcome, *,
    unreconciled_children: Sequence[str] = (),
    external_effects_reconciled: bool = True,
) -> bool:
    """Write authority needs an OWNED LIVE epoch AND full reconciliation:
    no undrained children, no unreconciled external effects (s6.3, R031).
    Mirrors ``child_handoff.TurnoverCoordinator.successor_may_dispatch_writes``
    at the controller-lease level."""
    if outcome.status != OWN_LEASE_LIVE:
        return False
    if tuple(unreconciled_children):
        return False
    return bool(external_effects_reconciled)


def _audit(audit: Any, event: str, lease: EpochLease, note: str) -> None:
    if audit is None:
        return
    audit.append(event, policy_result=f"epoch={lease.epoch}",
                 detail={"campaign_id": lease.campaign_id,
                         "epoch": lease.epoch,
                         "owner_run_id": lease.owner_run_id,
                         "released": lease.released,
                         "renew_by_epoch_seconds": lease.renew_by_epoch_seconds,
                         "note": note})
