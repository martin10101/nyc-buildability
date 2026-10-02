#!/usr/bin/env python3
"""Atomic review-or-combine slot reservation for the cloud loop (D-091 TW1, M0-T171).

`run_budget.admit_review_or_combine` (M0-T170) is a PURE, STATELESS admission
check: the caller hands it the current active counts and it says whether ONE more
review/combine process may start. Its own G3/G4 review (`M0-T170-G3G4.md` note 1)
flagged the gap this module closes:

    "The pure stateless primitive cannot prevent a TOCTOU by itself ... the
    M0-T166 wiring MUST perform count-check-reserve ATOMICALLY (serialize) so two
    lanes cannot both observe an open slot and both admit -> 3 running."

Two lanes each reading `global_active == 1` would both pass `admit_review_or_combine`
and both start, taking three processes against a 2-slot box. This module makes the
count, the decision, and the reservation ONE atomic step, serialized across
processes by an exclusive file lock in the runtime directory:

* **count-check-reserve under one lock.** `try_reserve` takes an exclusive lock,
  reads the live reservations, calls `admit_review_or_combine` on those counts, and
  — only if admitted — records the new reservation BEFORE releasing the lock. A
  second process cannot observe the pre-reservation count, so two processes can
  never both take the last of the 2 global slots, nor exceed 1 per lane.
* **reservations carry their owner, so a dead process is reclaimed safely.** Each
  reservation records the owning pid and its process-start token (via `locking`,
  the package's proven liveness machinery). A reservation whose owner is provably
  gone — or whose pid was reused — is pruned on the next read and never counted,
  so a crashed worker does not strand a slot. Liveness that CANNOT be determined
  keeps the reservation counted (fail closed: never free a possibly-live slot).
* **fail closed.** Any lock error, any unreadable or malformed state file, and any
  write failure REFUSE the reservation (no slot). Like every bound in this package
  an uncountable state admits nothing; it never guesses a slot is free.

The lock itself mirrors `locking.py`: `O_CREAT | O_EXCL` atomic acquisition, and
the same `locking.probe_process` stale-detection discipline (it never silently
steals a live lock, and it reclaims only a provably-dead holder). The OS does not
auto-release an `O_EXCL` lock file, so a crashed lock-holder is reclaimed by the
same stale takeover `locking.SingleInstanceLock` uses; a holder that cannot be
assessed makes acquisition time out and fail closed.

Nothing in the loop calls this yet (TW2 wires it into the dual-review conductor);
it is built, reviewed, and merged on its own first.
"""
from __future__ import annotations

import contextlib
import dataclasses
import json
import os
import pathlib
import time
from typing import Any, Iterator

from .locking import probe_process, process_start_token
from .models import canonical_json, to_utc_iso
from .run_budget import (
    GLOBAL_REVIEW_OR_COMBINE_DEFAULT,
    AdmissionVerdict,
    admit_review_or_combine,
)

#: Design §5 default per-lane ceiling (one review/combine in flight per lane).
LANE_REVIEW_OR_COMBINE_DEFAULT = 1

#: The two files that live in the runtime directory. The lock serializes the
#: critical section; the state file holds the reservations.
SLOTS_STATE_FILENAME = "review_slots.json"
SLOTS_LOCK_FILENAME = "review_slots.lock"

#: Bumped only with a documented migration of the state-file shape.
SLOTS_SCHEMA_VERSION = "1.0.0"

#: Lock defaults: a brief critical section, so a generous wait serializes real
#: contention without over-subscribing, and a stuck holder fails closed.
DEFAULT_LOCK_TIMEOUT_S = 10.0
DEFAULT_LOCK_POLL_S = 0.01


class SlotError(Exception):
    """A slot could not be reserved safely. Always carries a code; never fails open."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# A reservation
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Reservation:
    """One held review-or-combine slot, owned by a specific live process.

    `pid` + `start_token` together identify the owner so a reservation left behind
    by a dead process (or a reused pid) is reclaimed rather than counted forever.
    `reservation_id` is the release key: a process releases only its OWN slot.
    """

    reservation_id: str
    pid: int
    start_token: str
    lane: str
    acquired_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "Reservation":
        if not isinstance(data, dict):
            raise SlotError("slot_state_unreadable",
                            "a slot reservation entry is not a record; admitting nothing")
        try:
            reservation_id = str(data["reservation_id"])
            pid = data["pid"]
            lane = str(data["lane"])
            start_token = str(data.get("start_token", "") or "")
            acquired_at_utc = str(data.get("acquired_at_utc", "") or "")
        except (KeyError, TypeError) as exc:
            raise SlotError("slot_state_unreadable",
                            f"a slot reservation entry is malformed ({exc}); "
                            f"admitting nothing (fail closed)") from exc
        if not isinstance(pid, int) or isinstance(pid, bool):
            raise SlotError("slot_state_unreadable",
                            f"a slot reservation carries pid {pid!r}, not an integer; "
                            f"admitting nothing (fail closed)")
        if not reservation_id:
            raise SlotError("slot_state_unreadable",
                            "a slot reservation carries no reservation_id; admitting nothing")
        return cls(reservation_id=reservation_id, pid=pid, start_token=start_token,
                   lane=lane, acquired_at_utc=acquired_at_utc)


@dataclasses.dataclass(frozen=True)
class SlotGrant:
    """The outcome of a reservation attempt.

    `admitted` is True only when a slot was atomically reserved; `reservation`
    carries it so the caller can release it. Any refusal — the box is full, this
    lane is full, or a lock/state error — is `admitted=False` with a `verdict`
    naming the blocking dimension and reason, never an exception the caller must
    catch to stay safe.
    """

    admitted: bool
    verdict: AdmissionVerdict
    reservation: Reservation | None = None

    @property
    def reason_code(self) -> str:
        return self.verdict.reason_code

    @property
    def reason(self) -> str:
        return self.verdict.reason


# --------------------------------------------------------------------------
# Liveness of a reservation's owner (mirrors locking.assess)
# --------------------------------------------------------------------------


def reservation_owner_alive(reservation: Reservation) -> bool:
    """True while the reservation's owning process is (provably) still its owner.

    Fail closed: when liveness CANNOT be determined the reservation stays counted
    (never free a slot we are unsure about). A provably-gone owner, a reused pid
    (start-token mismatch), or an invalid pid releases the slot.
    """
    probe = probe_process(reservation.pid)
    if not probe.determined:
        return True
    if not probe.alive:
        return False
    if (reservation.start_token and probe.start_token
            and reservation.start_token != probe.start_token):
        return False
    return True


# --------------------------------------------------------------------------
# The exclusive critical-section lock (mirrors locking.py's O_EXCL + stale scan)
# --------------------------------------------------------------------------


class _SlotLock:
    """A short-lived exclusive file lock, taken only around the count-check-reserve.

    Acquisition is `O_CREAT | O_EXCL` (atomic), retried until a deadline so real
    contenders serialize rather than failing. A holder that is provably dead (or a
    reused pid) is taken over with the same temp-write + `os.replace` + re-read
    confirmation `locking.SingleInstanceLock` uses; a holder whose liveness cannot
    be read makes the wait time out and fail closed.
    """

    def __init__(self, path: pathlib.Path, *, pid: int, start_token: str,
                 timeout_s: float, poll_s: float) -> None:
        self.path = pathlib.Path(path)
        self.pid = pid
        self.start_token = start_token
        self.timeout_s = float(timeout_s)
        self.poll_s = float(poll_s)
        self._lock_id = ""

    def _payload(self) -> bytes:
        return canonical_json({
            "pid": self.pid,
            "start_token": self.start_token,
            "lock_id": self._lock_id,
            "acquired_at_utc": to_utc_iso(),
        })

    def _read_holder(self) -> dict[str, Any] | None:
        try:
            holder = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return holder if isinstance(holder, dict) else None

    def _holder_is_stale(self) -> bool:
        holder = self._read_holder()
        if holder is None:
            return False  # unreadable or mid-write: wait, never steal
        pid = holder.get("pid")
        if not isinstance(pid, int) or isinstance(pid, bool):
            return False
        probe = probe_process(pid)
        if not probe.determined:
            return False  # never steal a possibly-live lock
        recorded = str(holder.get("start_token", "") or "")
        reused = bool(recorded and probe.start_token and recorded != probe.start_token)
        return (not probe.alive) or reused

    def _take_over(self) -> bool:
        temp = self.path.with_suffix(self.path.suffix + f".{self.pid}.tmp")
        try:
            temp.write_bytes(self._payload())
            os.replace(temp, self.path)
        except OSError:
            with contextlib.suppress(OSError):
                temp.unlink()
            return False
        confirmed = self._read_holder()
        return bool(confirmed and confirmed.get("lock_id") == self._lock_id)

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout_s
        while True:
            self._lock_id = os.urandom(16).hex()
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                if self._holder_is_stale() and self._take_over():
                    return
                if time.monotonic() >= deadline:
                    raise SlotError(
                        "slot_lock_timeout",
                        f"the slot lock {self.path} was held past {self.timeout_s:g}s; "
                        f"refusing the reservation (fail closed)")
                time.sleep(self.poll_s)
                continue
            except OSError as exc:
                raise SlotError("slot_lock_error",
                                f"could not acquire slot lock {self.path}: {exc}") from exc
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(self._payload())
                    stream.flush()
                    os.fsync(stream.fileno())
            except OSError as exc:
                raise SlotError("slot_lock_error",
                                f"could not write slot lock {self.path}: {exc}") from exc
            return

    def release(self) -> None:
        holder = self._read_holder()
        if holder is None or holder.get("lock_id") != self._lock_id:
            return  # never remove another process's lock
        with contextlib.suppress(OSError):
            self.path.unlink()

    def __enter__(self) -> "_SlotLock":
        self.acquire()
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.release()


# --------------------------------------------------------------------------
# The reservation registry
# --------------------------------------------------------------------------


class ReviewSlots:
    """Atomic reserve/release of the shared review-or-combine slots.

    Bounds are supplied by the caller (the immutable `config.toml [limits]` in
    production): `global_limit` is the whole-box ceiling, `lane_limit` the per-lane
    ceiling. `admit_review_or_combine` fails closed on a non-positive limit, so a
    missing bound admits nothing rather than everything.
    """

    def __init__(self, runtime_dir: str | os.PathLike[str], *,
                 global_limit: int = GLOBAL_REVIEW_OR_COMBINE_DEFAULT,
                 lane_limit: int = LANE_REVIEW_OR_COMBINE_DEFAULT,
                 pid: int | None = None,
                 lock_timeout_s: float = DEFAULT_LOCK_TIMEOUT_S,
                 lock_poll_s: float = DEFAULT_LOCK_POLL_S) -> None:
        self.runtime_dir = pathlib.Path(runtime_dir)
        self.global_limit = global_limit
        self.lane_limit = lane_limit
        self.pid = os.getpid() if pid is None else int(pid)
        self.lock_timeout_s = float(lock_timeout_s)
        self.lock_poll_s = float(lock_poll_s)
        #: Resolved once: the current process's creation token, stamped onto every
        #: reservation this instance makes (dead-owner reclaim keys on it).
        self._start_token = process_start_token(self.pid)

    # -- paths ---------------------------------------------------------------

    @property
    def state_path(self) -> pathlib.Path:
        return self.runtime_dir / SLOTS_STATE_FILENAME

    @property
    def lock_path(self) -> pathlib.Path:
        return self.runtime_dir / SLOTS_LOCK_FILENAME

    def _lock(self) -> _SlotLock:
        return _SlotLock(self.lock_path, pid=self.pid, start_token=self._start_token,
                         timeout_s=self.lock_timeout_s, poll_s=self.lock_poll_s)

    # -- state file ----------------------------------------------------------

    def _read_raw(self) -> list[Any]:
        """The persisted reservation entries. Missing file is empty; a present but
        unreadable or malformed file REFUSES (fail closed)."""
        if not self.state_path.exists():
            return []
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise SlotError("slot_state_unreadable",
                            f"the slot state file {self.state_path} is unreadable ({exc}); "
                            f"admitting nothing (fail closed)") from exc
        if not isinstance(data, dict) or not isinstance(data.get("reservations"), list):
            raise SlotError("slot_state_unreadable",
                            f"the slot state file {self.state_path} is not a slot record; "
                            f"admitting nothing (fail closed)")
        return data["reservations"]

    def _read_live(self) -> tuple[list[Reservation], bool]:
        """Live reservations and whether any dead ones were pruned (prune persists)."""
        raw = self._read_raw()
        live = [res for res in (Reservation.from_dict(item) for item in raw)
                if reservation_owner_alive(res)]
        return live, len(live) != len(raw)

    def _write(self, reservations: list[Reservation]) -> None:
        payload = canonical_json({
            "schema_version": SLOTS_SCHEMA_VERSION,
            "reservations": [res.to_dict() for res in reservations],
        })
        temp = self.state_path.with_suffix(self.state_path.suffix + f".{self.pid}.tmp")
        try:
            with open(temp, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.state_path)
        except OSError as exc:
            with contextlib.suppress(OSError):
                temp.unlink()
            raise SlotError("slot_state_write_failed",
                            f"could not write the slot state file {self.state_path} "
                            f"({exc}); admitting nothing (fail closed)") from exc

    # -- reserve / release ---------------------------------------------------

    def _fail_closed(self, exc: SlotError) -> SlotGrant:
        verdict = AdmissionVerdict(
            admitted=False, scope="global", active=-1, limit=self._coerce_limit(),
            reason_code=exc.code, reason=exc.message)
        return SlotGrant(False, verdict, None)

    def _coerce_limit(self) -> int:
        return (self.global_limit if isinstance(self.global_limit, int)
                and not isinstance(self.global_limit, bool) else 0)

    def try_reserve(self, lane: str) -> SlotGrant:
        """Atomically count, decide, and (if admitted) reserve one slot.

        The whole body runs under the exclusive lock, so the count another process
        sees already includes any slot this call takes. Returns an admitted grant
        carrying the `Reservation`, or a refusal grant (box full, lane full, or a
        fail-closed lock/state error).
        """
        lane = str(lane)
        try:
            with self._lock():
                live, pruned = self._read_live()
                global_active = len(live)
                lane_active = sum(1 for res in live if res.lane == lane)
                verdict = admit_review_or_combine(
                    global_active=global_active, lane_active=lane_active,
                    global_limit=self.global_limit, lane_limit=self.lane_limit, lane=lane)
                if not verdict.admitted:
                    if pruned:
                        self._write(live)  # persist the reclaim even on a refusal
                    return SlotGrant(False, verdict, None)
                reservation = Reservation(
                    reservation_id=os.urandom(16).hex(), pid=self.pid,
                    start_token=self._start_token, lane=lane,
                    acquired_at_utc=to_utc_iso())
                self._write([*live, reservation])
                return SlotGrant(True, verdict, reservation)
        except SlotError as exc:
            return self._fail_closed(exc)

    def release(self, reservation: Reservation | None) -> bool:
        """Release one slot this process holds. Idempotent; never raises.

        A lock or state error leaves the reservation in place — its owner (this
        pid + start token) still identifies it, so it is reclaimed when this
        process exits rather than stranding the slot on an error.
        """
        if reservation is None:
            return False
        try:
            with self._lock():
                live, pruned = self._read_live()
                remaining = [res for res in live
                             if res.reservation_id != reservation.reservation_id]
                removed = len(remaining) != len(live)
                if removed or pruned:
                    self._write(remaining)
                return removed
        except SlotError:
            return False

    @contextlib.contextmanager
    def reserve(self, lane: str) -> Iterator[SlotGrant]:
        """Reserve-before-spawn / release-after-exit as a context manager.

        ``with slots.reserve(lane) as grant:`` — when ``grant.admitted`` the slot
        is held for the block and released on exit; when it is not, the caller
        WAITS and retries, and nothing is released.
        """
        grant = self.try_reserve(lane)
        try:
            yield grant
        finally:
            if grant.admitted and grant.reservation is not None:
                self.release(grant.reservation)

    # -- reporting -----------------------------------------------------------

    def active(self) -> list[Reservation]:
        """A snapshot of the live reservations (dead owners pruned). Fail closed."""
        with self._lock():
            live, pruned = self._read_live()
            if pruned:
                self._write(live)
            return live
