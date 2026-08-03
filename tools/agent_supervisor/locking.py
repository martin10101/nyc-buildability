#!/usr/bin/env python3
"""Cross-platform single-instance lock keyed to checkout identity (D-007 S7, S11.5).

S7: "Exactly one supervisor instance may control a given checkout; use a
cross-platform lock with stale-lock detection that never silently steals a live
lock."

The three rules that matter, and how they are met:

* **Keyed to the checkout, not the machine.** The lock file lives in the runtime
  directory, which `durable_state.runtime_dir_for` already keys by SHA-256 of the
  canonical full checkout path. Two checkouts never contend; two processes on one
  checkout always do.
* **Never steals a live lock.** A lock is taken over ONLY when the recorded owner
  is provably gone. "Provably" means the pid is not running, or it is running but
  its process-creation timestamp differs from the one recorded at acquisition
  (pid reuse). If liveness cannot be determined at all, acquisition FAILS -
  refusing to run is always safer than two supervisors driving one checkout.
* **Atomic.** Creation uses `O_CREAT | O_EXCL`. Takeover writes a fresh file to a
  temp name and `os.replace`s it, then re-reads it to confirm this process owns
  it (a second contender racing for the same stale lock loses the re-read).

Process liveness on Windows deliberately does NOT use `os.kill(pid, 0)`: CPython
implements `os.kill` on Windows with `TerminateProcess`, so the POSIX idiom
"signal 0 to probe" would KILL the process it was probing. This module uses
`OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `GetExitCodeProcess` +
`GetProcessTimes` through `ctypes` instead.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
from typing import Any

from .models import to_utc_iso

LOCK_FILENAME = "supervisor.lock"

#: Windows constants (winnt.h / processthreadsapi.h).
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_STILL_ACTIVE = 259


class LockError(Exception):
    """The single-instance lock could not be taken. The caller must not proceed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Process liveness
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProcessProbe:
    """What we could determine about a pid.

    `determined` is False when the platform refused to tell us. That is NOT the
    same as "not running", and the lock code treats the two very differently.
    """

    pid: int
    determined: bool
    alive: bool
    start_token: str = ""
    detail: str = ""


def _probe_windows(pid: int) -> ProcessProbe:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE

    handle = kernel32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        # ERROR_INVALID_PARAMETER (87) means "no such process": a determined
        # negative. ERROR_ACCESS_DENIED (5) means the process EXISTS but belongs
        # to another account - determined POSITIVE (and never stealable).
        if error == 87:
            return ProcessProbe(pid, True, False, detail="no such process")
        if error == 5:
            return ProcessProbe(pid, True, True, detail="access denied: process exists")
        return ProcessProbe(pid, False, False, detail=f"OpenProcess failed with {error}")
    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return ProcessProbe(pid, False, False, detail="GetExitCodeProcess failed")
        if exit_code.value != _STILL_ACTIVE:
            return ProcessProbe(pid, True, False, detail=f"exited with {exit_code.value}")
        creation = wintypes.FILETIME()
        exit_time = wintypes.FILETIME()
        kernel_time = wintypes.FILETIME()
        user_time = wintypes.FILETIME()
        ok = kernel32.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time),
                                      ctypes.byref(kernel_time), ctypes.byref(user_time))
        token = ""
        if ok:
            token = f"{creation.dwHighDateTime:08x}{creation.dwLowDateTime:08x}"
        return ProcessProbe(pid, True, True, token, "running")
    finally:
        kernel32.CloseHandle(handle)


def _probe_posix(pid: int) -> ProcessProbe:
    stat_path = pathlib.Path("/proc") / str(pid) / "stat"
    if stat_path.exists():
        try:
            raw = stat_path.read_text(encoding="utf-8", errors="replace")
            # Field 22 (1-based) is starttime. The comm field may contain spaces
            # and parentheses, so split after the LAST ')'.
            tail = raw[raw.rindex(")") + 1:].split()
            token = tail[19] if len(tail) > 19 else ""
            return ProcessProbe(pid, True, True, token, "running (/proc)")
        except (OSError, ValueError):
            return ProcessProbe(pid, False, False, detail="/proc entry unreadable")
    if pathlib.Path("/proc").exists():
        # /proc exists but this pid has no entry: a determined negative.
        return ProcessProbe(pid, True, False, detail="no /proc entry")
    try:
        os.kill(pid, 0)  # POSIX only: signal 0 is a pure existence probe here.
    except ProcessLookupError:
        return ProcessProbe(pid, True, False, detail="no such process")
    except PermissionError:
        return ProcessProbe(pid, True, True, detail="permission denied: process exists")
    except OSError as exc:
        return ProcessProbe(pid, False, False, detail=f"kill(0) failed: {exc}")
    return ProcessProbe(pid, True, True, detail="running")


def probe_process(pid: int) -> ProcessProbe:
    """Determine whether `pid` is running, without ever signalling it."""
    if pid <= 0:
        return ProcessProbe(pid, True, False, detail="invalid pid")
    if os.name == "nt":
        return _probe_windows(pid)
    return _probe_posix(pid)


def process_start_token(pid: int) -> str:
    """The creation-time token used to defend against pid reuse ('' when unknown)."""
    return probe_process(pid).start_token


# --------------------------------------------------------------------------
# The lock
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class LockRecord:
    """The contents of the lock file. No secrets, no environment, no user paths."""

    pid: int
    start_token: str
    checkout_key: str
    controller_version: str
    acquired_at_utc: str
    lock_id: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LockRecord":
        known = {f.name for f in dataclasses.fields(cls)}
        missing = sorted(known - set(data))
        if missing:
            raise LockError("malformed_lock", f"lock file is missing {missing}")
        return cls(**{k: data[k] for k in known})


@dataclasses.dataclass(frozen=True)
class StaleAssessment:
    """Why the lock was, or was not, considered stale."""

    stale: bool
    code: str
    detail: str


def assess(record: LockRecord) -> StaleAssessment:
    """Decide whether an existing lock may be taken over. Fails closed."""
    probe = probe_process(record.pid)
    if not probe.determined:
        return StaleAssessment(False, "liveness_undetermined",
                               f"could not determine whether pid {record.pid} is running "
                               f"({probe.detail}); refusing to assume it is gone")
    if not probe.alive:
        return StaleAssessment(True, "owner_gone",
                               f"pid {record.pid} is not running ({probe.detail})")
    if record.start_token and probe.start_token and record.start_token != probe.start_token:
        return StaleAssessment(True, "pid_reused",
                               f"pid {record.pid} is running but was created at a different "
                               f"time than the lock records; this is a reused pid, not the "
                               f"lock owner")
    return StaleAssessment(False, "live_owner",
                           f"pid {record.pid} is running and owns this checkout")


class SingleInstanceLock:
    """Exactly-one-supervisor-per-checkout lock with honest stale detection."""

    def __init__(self, runtime_dir: str | os.PathLike[str], *, checkout_key: str,
                 controller_version: str, pid: int | None = None) -> None:
        self.path = pathlib.Path(runtime_dir) / LOCK_FILENAME
        self.checkout_key = checkout_key
        self.controller_version = controller_version
        self.pid = os.getpid() if pid is None else pid
        self.record: LockRecord | None = None
        self.took_over_stale: StaleAssessment | None = None

    # -- reading -------------------------------------------------------------

    def read(self) -> LockRecord | None:
        """Read the current lock record, or None when the file does not exist."""
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise LockError("malformed_lock",
                            f"lock file {self.path} is unreadable: {exc}") from exc
        return LockRecord.from_dict(data)

    def held_by_other(self) -> LockRecord | None:
        """The live foreign holder, or None (also None for a stale lock)."""
        existing = self.read()
        if existing is None or existing.pid == self.pid:
            return None
        return existing if not assess(existing).stale else None

    # -- acquiring -----------------------------------------------------------

    def _new_record(self) -> LockRecord:
        return LockRecord(
            pid=self.pid,
            start_token=process_start_token(self.pid),
            checkout_key=self.checkout_key,
            controller_version=self.controller_version,
            acquired_at_utc=to_utc_iso(),
            lock_id=os.urandom(16).hex(),
        )

    def acquire(self) -> LockRecord:
        """Acquire the lock or raise. Never silently steals a live lock."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = self._new_record()
        payload = json.dumps(record.to_dict(), sort_keys=True).encode("utf-8")

        try:
            handle = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            pass
        else:
            with os.fdopen(handle, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            self.record = record
            return record

        existing = self.read()
        if existing is None:  # It vanished between the O_EXCL failure and the read.
            return self.acquire()
        if existing.pid == self.pid and existing.checkout_key == self.checkout_key:
            self.record = existing
            return existing

        verdict = assess(existing)
        if not verdict.stale:
            raise LockError(
                "lock_held",
                f"another supervisor instance holds this checkout: {verdict.detail}. "
                f"Exactly one instance may control a checkout (S7)")

        # Stale takeover: replace atomically, then re-read to confirm we won.
        temp = self.path.with_suffix(self.path.suffix + f".{self.pid}.tmp")
        temp.write_bytes(payload)
        os.replace(temp, self.path)
        confirmed = self.read()
        if confirmed is None or confirmed.lock_id != record.lock_id:
            raise LockError("takeover_race",
                            "another process took the stale lock first; refusing to run")
        self.record = confirmed
        self.took_over_stale = verdict
        return confirmed

    # -- releasing -----------------------------------------------------------

    def release(self) -> bool:
        """Release the lock IF this process still owns it. Never removes another's."""
        current = self.read()
        if current is None or self.record is None:
            return False
        if current.lock_id != self.record.lock_id:
            return False
        try:
            self.path.unlink()
        except OSError:
            return False
        self.record = None
        return True

    def __enter__(self) -> "SingleInstanceLock":
        self.acquire()
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.release()
