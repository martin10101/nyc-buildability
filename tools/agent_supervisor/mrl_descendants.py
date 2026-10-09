#!/usr/bin/env python3
"""Descendant-zero proof for the MRL one-shot process (M0-T136 C-B4; D-024-R584).

``ProcessContainer.terminate_all`` reports success after the job object closes; it
does not PROVE that nothing remains. R584 requires that cancellation or timeout
"terminate and prove zero remaining descendants", so this module enumerates the
live process table (stdlib only: Toolhelp32 on Windows, ``/proc`` or ``ps`` on
POSIX - psutil is not admitted) and walks parent links from the worker pid.

Orphan semantics mostly work in the proof's favour: a grandchild that outlived the
worker still records the worker's pid (or a dead intermediate) as its parent and
stays visible to the walk, so a real descendant is never lost. The one hazard is
pid REUSE - the mirror image of that same "parent pid is never rewritten" rule.
When a worker's pid is later reused as ``root_pid`` (Windows reuses pids quickly),
the orphans an EARLIER process of that pid left behind still record it as their
parent, so the naive ``pid -> ppid`` walk counts those unrelated processes forever
- a false "descendants remaining". That is fail-closed (a false turnover, never a
missed descendant), but it is still a defect. ``prove_zero_descendants`` closes it
with the root's own creation ordinal (``root_start``, captured by the launcher
while the root was alive): a process created BEFORE the root cannot be its
descendant and is pruned with its subtree, while anything with an unknown or
at/after-root creation time is kept (fail closed). A snapshot that cannot be taken
is NOT a proof - the result says ``proven=False`` with the source recorded, never
"zero".
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
import subprocess
import sys
import time
from collections.abc import Callable

from .locking import probe_process

#: pid -> parent pid for every live process the snapshot could see.
ProcessTable = dict[int, int]
Snapshot = Callable[[], ProcessTable]

SOURCE_TOOLHELP32 = "windows_toolhelp32"
SOURCE_PROCFS = "posix_procfs"
SOURCE_PS = "posix_ps"
SOURCE_UNAVAILABLE = "unavailable"


@dataclasses.dataclass(frozen=True)
class DescendantProof:
    root_pid: int
    remaining: tuple[int, ...]
    attempts: int
    elapsed_seconds: float
    proven: bool
    source: str

    def to_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


def _snapshot_windows() -> ProcessTable:
    import ctypes
    from ctypes import wintypes

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_char * 260),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.Process32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
    kernel32.Process32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
    if snapshot in (None, 0, ctypes.c_void_p(-1).value):
        raise OSError(ctypes.get_last_error(), "CreateToolhelp32Snapshot failed")
    table: ProcessTable = {}
    try:
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        if not kernel32.Process32First(snapshot, ctypes.byref(entry)):
            raise OSError(ctypes.get_last_error(), "Process32First failed")
        while True:
            table[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
            if not kernel32.Process32Next(snapshot, ctypes.byref(entry)):
                return table
    finally:
        kernel32.CloseHandle(snapshot)


def _snapshot_procfs() -> ProcessTable:
    proc = pathlib.Path("/proc")
    if not proc.is_dir():
        raise OSError("/proc is not mounted")
    table: ProcessTable = {}
    for child in proc.iterdir():
        if not child.name.isdigit():
            continue
        try:
            raw = (child / "stat").read_text(encoding="utf-8", errors="replace")
            tail = raw[raw.rindex(")") + 1:].split()
            table[int(child.name)] = int(tail[1]) if len(tail) > 1 else 0
        except (OSError, ValueError):
            continue  # raced with exit; the next attempt re-reads the table
    if not table:
        raise OSError("/proc yielded no processes")
    return table


def _snapshot_ps() -> ProcessTable:
    completed = subprocess.run(["ps", "-A", "-o", "pid=,ppid="], capture_output=True, text=True,
                               timeout=30, check=False)
    if completed.returncode != 0:
        raise OSError(f"ps exited {completed.returncode}: {completed.stderr.strip()}")
    table: ProcessTable = {}
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            table[int(parts[0])] = int(parts[1])
    if not table:
        raise OSError("ps yielded no processes")
    return table


def snapshot_processes(*, sys_platform: str = sys.platform) -> tuple[ProcessTable, str]:
    """``(pid -> ppid, source)`` for the live process table; raises OSError when unobservable."""
    if sys_platform == "win32":
        return _snapshot_windows(), SOURCE_TOOLHELP32
    try:
        return _snapshot_procfs(), SOURCE_PROCFS
    except OSError:
        return _snapshot_ps(), SOURCE_PS


#: A pid -> creation ordinal reader. Returns a monotonically-increasing creation
#: ordinal (an earlier-created process has a smaller value), or None when the
#: creation time cannot be read for that pid. Injectable for tests.
CreationOrdinal = Callable[[int], "int | None"]


def creation_token_to_ordinal(token: str) -> "int | None":
    """A ``locking.probe_process`` start token as a monotonically-increasing creation ordinal.

    An earlier-created process has a smaller ordinal. The token format is
    platform-specific, so this parses it the same way ``locking`` produced it:

    * Windows (``locking._probe_windows``): the process creation ``FILETIME`` as
      fixed-width hex (high dword then low dword), which ``int(token, 16)`` turns
      into the raw 64-bit 100 ns tick count since 1601 - earlier means smaller.
    * POSIX (``locking._probe_posix``): ``/proc/<pid>/stat`` field 22 (``starttime``
      in clock ticks since boot) as a decimal string - earlier means smaller.

    An empty or unparseable token yields ``None`` (unknown): the caller then treats
    the pid as NOT provably pre-root and keeps it (fail closed - never exclude a
    possible descendant on an unreadable creation time)."""
    if not token:
        return None
    try:
        return int(token, 16) if os.name == "nt" else int(token)
    except ValueError:
        return None


def _probe_creation_ordinal(pid: int) -> "int | None":
    """Default creation-ordinal reader: the live creation time of ``pid`` from
    ``locking.probe_process`` (``OpenProcess``+``GetProcessTimes`` on Windows,
    ``/proc/<pid>/stat`` on POSIX), as a comparable ordinal. ``None`` when the pid
    is gone or its creation time is unreadable."""
    return creation_token_to_ordinal(probe_process(pid).start_token)


def descendants_of(root_pid: int, table: ProcessTable, *,
                   root_start: "int | None" = None,
                   creation_ordinal: "CreationOrdinal | None" = None) -> tuple[int, ...]:
    """Every pid whose parent chain reaches ``root_pid`` (the root itself included if alive).

    ``root_start`` + ``creation_ordinal`` close a pid-reuse false positive that is
    Windows-specific but modelled on both hosts. A ``pid -> ppid`` snapshot cannot
    tell a genuine descendant from an UNRELATED earlier orphan: when a dead
    process's pid is later reused as ``root_pid``, the orphans that process left
    behind still record it as their parent (Toolhelp32 ``th32ParentProcessID`` is
    never rewritten when a parent exits), so the naive walk counts them forever (a
    false "descendants remaining"). The sound exclusion: **a process created BEFORE
    the root's own start cannot be the root's descendant.** When ``root_start`` (the
    root's creation ordinal, captured by the launcher while the root was alive) and
    a ``creation_ordinal`` reader are supplied, any pid whose creation precedes
    ``root_start`` is pruned together with its subtree (its children only reach the
    root through it, so they are not the root's descendants either). A pid whose
    creation ordinal is unknown is KEPT (fail closed: a real descendant is never
    excluded on an unreadable creation time), and a descendant created at/after the
    root is always kept. With no ``root_start`` the behaviour is unchanged (the
    orphan-stays-visible walk) - callers that cannot capture a start time keep the
    old, fail-closed semantics."""
    reader = creation_ordinal if creation_ordinal is not None else (
        _probe_creation_ordinal if root_start is not None else None)

    def _created_before_root(pid: int) -> bool:
        if root_start is None or reader is None:
            return False
        ordinal = reader(pid)
        if ordinal is None:
            return False  # unknown creation time: keep (fail closed), never exclude
        return ordinal < root_start

    children: dict[int, list[int]] = {}
    for pid, ppid in table.items():
        if pid != ppid:  # pid 0 / System list themselves as their own parent
            children.setdefault(ppid, []).append(pid)
    root_present = root_pid in table and not _created_before_root(root_pid)
    found: list[int] = [root_pid] if root_present else []
    frontier = [root_pid]
    seen = {root_pid}
    while frontier:
        pid = frontier.pop()
        for child in children.get(pid, ()):
            if child in seen:
                continue
            seen.add(child)
            if _created_before_root(child):
                continue  # an earlier orphan on a reused pid: not a descendant; prune its subtree
            found.append(child)
            frontier.append(child)
    return tuple(sorted(found))


def prove_zero_descendants(root_pid: int, *, snapshot: Snapshot | None = None,
                           root_start: "int | None" = None,
                           creation_ordinal: "CreationOrdinal | None" = None,
                           settle_seconds: float = 2.0, poll_seconds: float = 0.05,
                           now: Callable[[], float] = time.monotonic,
                           sleep: Callable[[float], None] = time.sleep) -> DescendantProof:
    """Re-enumerate until the worker and everything under it is gone, or the settle window ends.

    ``proven`` is True only when a real snapshot showed the tree empty. An
    unobservable table yields ``proven=False`` with ``source='unavailable'``: an
    absent proof is reported as absent, never as zero (R584).

    ``root_start`` is the root's own creation ordinal (see ``creation_token_to_ordinal``),
    captured by the LAUNCHER while the root was still alive - the only moment its
    creation time is reliably readable. When supplied it is threaded into
    ``descendants_of`` so a pid created BEFORE the root (an unrelated earlier orphan
    that survives on a reused pid) is never counted as a descendant; ``None`` keeps
    the prior, fail-closed walk. ``creation_ordinal`` overrides the default
    live-probe reader (used by tests to inject deterministic creation times); it is
    ignored unless ``root_start`` is given.
    """
    started = now()
    attempts = 0
    remaining: tuple[int, ...] = (root_pid,)
    source = SOURCE_UNAVAILABLE
    while True:
        attempts += 1
        try:
            if snapshot is None:
                table, source = snapshot_processes()
            else:
                table, source = snapshot(), "injected"
        except OSError:
            return DescendantProof(root_pid, remaining, attempts, now() - started, False, SOURCE_UNAVAILABLE)
        remaining = descendants_of(root_pid, table, root_start=root_start,
                                   creation_ordinal=creation_ordinal)
        if not remaining:
            return DescendantProof(root_pid, (), attempts, now() - started, True, source)
        if now() - started >= settle_seconds:
            return DescendantProof(root_pid, remaining, attempts, now() - started, False, source)
        sleep(poll_seconds)
