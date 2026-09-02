#!/usr/bin/env python3
"""Descendant-zero proof for the MRL one-shot process (M0-T136 C-B4; D-024-R584).

``ProcessContainer.terminate_all`` reports success after the job object closes; it
does not PROVE that nothing remains. R584 requires that cancellation or timeout
"terminate and prove zero remaining descendants", so this module enumerates the
live process table (stdlib only: Toolhelp32 on Windows, ``/proc`` or ``ps`` on
POSIX - psutil is not admitted) and walks parent links from the worker pid.

Orphan semantics work in the proof's favour: neither Windows nor Linux rewrites a
child's recorded parent when the parent dies, so a grandchild that outlived the
worker still reports the worker's pid (or a dead intermediate) as its parent and
stays visible to the walk. A snapshot that cannot be taken is NOT a proof - the
result says ``proven=False`` with the source recorded, never "zero".
"""
from __future__ import annotations

import dataclasses
import pathlib
import subprocess
import sys
import time
from collections.abc import Callable

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


def descendants_of(root_pid: int, table: ProcessTable) -> tuple[int, ...]:
    """Every pid whose parent chain reaches ``root_pid`` (the root itself included if alive)."""
    children: dict[int, list[int]] = {}
    for pid, ppid in table.items():
        if pid != ppid:  # pid 0 / System list themselves as their own parent
            children.setdefault(ppid, []).append(pid)
    found: list[int] = [root_pid] if root_pid in table else []
    frontier = [root_pid]
    seen = {root_pid}
    while frontier:
        pid = frontier.pop()
        for child in children.get(pid, ()):
            if child not in seen:
                seen.add(child)
                found.append(child)
                frontier.append(child)
    return tuple(sorted(found))


def prove_zero_descendants(root_pid: int, *, snapshot: Snapshot | None = None,
                           settle_seconds: float = 2.0, poll_seconds: float = 0.05,
                           now: Callable[[], float] = time.monotonic,
                           sleep: Callable[[float], None] = time.sleep) -> DescendantProof:
    """Re-enumerate until the worker and everything under it is gone, or the settle window ends.

    ``proven`` is True only when a real snapshot showed the tree empty. An
    unobservable table yields ``proven=False`` with ``source='unavailable'``: an
    absent proof is reported as absent, never as zero (R584).
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
        remaining = descendants_of(root_pid, table)
        if not remaining:
            return DescendantProof(root_pid, (), attempts, now() - started, True, source)
        if now() - started >= settle_seconds:
            return DescendantProof(root_pid, remaining, attempts, now() - started, False, source)
        sleep(poll_seconds)
