#!/usr/bin/env python3
"""Argv-array-only subprocess abstraction (D-007 S13 baseline, S13.4).

Hard rules this module exists to make structural rather than aspirational:

* **Never `shell=True`, never string interpolation of model-produced text.**
  `run()` accepts a LIST of strings and passes `shell=False` explicitly. There is
  no code path in this module that builds a command string.
* **Bypass flags are HARD-DENY.** `HARD_DENY_ARGUMENTS` is a constants list used
  to REFUSE arguments, and `assert_argv_safe()` raises on any of them. These are
  the only occurrences of those flag names in the supervisor, and they exist
  solely to deny them (D-007 S4.4).
* **Per-process timeouts with process-tree termination.** A timed-out child never
  leaks its descendants: on Windows `taskkill /PID <pid> /T /F` (itself invoked
  as an argv array), on POSIX a process-group kill.
* **Smallest practical child environment**, and environment contents are never
  logged.

Windows process-tree control - what is PROVEN here vs deferred:

    PROVEN in Phase 1  `terminate_process_tree()` via `taskkill /T /F`, exercised
                       against a real spawned child tree in the Phase 1 tests;
                       `run()` timeout handling that invokes it.
    PROVEN in Phase 1  `WindowsJobObject` creation, configuration with
                       JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, assignment of a real
                       child, and kill-on-close, via stdlib `ctypes`.
    DEFERRED to Phase 3 Using a Job Object as the DEFAULT containment for every
                       launched worker (including breakaway handling, nested job
                       compatibility on hosts that already job-object the shell,
                       and resource ceilings via job limits). Phase 1 wires the
                       taskkill fallback as the default and keeps the Job Object
                       as a proven, opt-in mechanism.

Phase 1 scope note: `resolve_executable()` implements the repo-shadowing refusal
and identity recording of S13.4. Comparing that identity against an APPROVED
compatibility matrix, and the plugin/MCP/hook inventory, are Phase 2.
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
import shutil
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence

#: Arguments that are refused unconditionally, whatever any model recommends.
#: THIS IS A DENY LIST. The supervisor never passes any of these to anything.
HARD_DENY_ARGUMENTS: frozenset[str] = frozenset({
    "--dangerously-bypass-approvals-and-sandbox",
    "--dangerously-bypass-hook-trust",
    "--dangerously-skip-permissions",
    "--allow-dangerously-skip-permissions",
    "--yolo",
})

#: Reasoning-effort flags are separately and permanently prohibited (D-004-R159,
#: D-007 S3.1). The installed Claude CLI does expose `--effort`; the supervisor
#: never passes it, and `assert_argv_safe()` refuses it like a bypass flag.
EFFORT_ARGUMENT_PREFIXES: tuple[str, ...] = ("--effort", "--reasoning-effort")

#: Environment variables a child is allowed to inherit by default. Everything
#: else is dropped: the worker receives no ambient credentials (S13.3).
DEFAULT_ENV_ALLOWLIST: tuple[str, ...] = (
    "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "TMPDIR",
    "HOME", "USERPROFILE", "LANG", "LC_ALL", "PATHEXT", "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE", "SYSTEMDRIVE",
)

DEFAULT_TIMEOUT_SECONDS = 900

#: Very large executables (the Claude CLI is a ~265 MB single-file binary) are
#: identified by size + mtime + a bounded head digest instead of a full hash, so
#: preflight does not read a quarter of a gigabyte on every action. Recorded
#: honestly as `digest_kind`.
FULL_HASH_MAX_BYTES = 64 * 1024 * 1024
HEAD_DIGEST_BYTES = 1024 * 1024


class HardDenyError(Exception):
    """A hard-denied argument was proposed. No model opinion can override this."""

    def __init__(self, argument: str, reason: str) -> None:
        super().__init__(f"HARD-DENY {argument!r}: {reason}")
        self.argument = argument
        self.reason = reason


class ProcessError(Exception):
    """Process launch or control failed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Argument validation
# --------------------------------------------------------------------------


def assert_argv_safe(argv: Sequence[Any]) -> list[str]:
    """Validate an argv array and return it as a list of `str`.

    Refuses: non-sequences, empty argv, non-string elements, embedded NULs, and
    every hard-denied or effort argument.
    """
    if isinstance(argv, (str, bytes)):
        raise ProcessError(
            "argv_not_a_list",
            "argv must be a list of strings; a command STRING is never accepted because "
            "that is the shape shell interpolation needs")
    if not isinstance(argv, Sequence) or not argv:
        raise ProcessError("argv_empty", "argv must be a non-empty sequence")

    out: list[str] = []
    for index, item in enumerate(argv):
        if not isinstance(item, str):
            raise ProcessError("argv_not_string",
                               f"argv[{index}] is {type(item).__name__}, expected str")
        if "\x00" in item:
            raise ProcessError("argv_nul", f"argv[{index}] contains a NUL byte")
        lowered = item.lower()
        if lowered in HARD_DENY_ARGUMENTS:
            raise HardDenyError(
                item,
                "permission-bypass, sandbox-bypass, and hook-trust-bypass flags are denied "
                "immediately and unconditionally (S4.4)")
        if any(lowered == prefix or lowered.startswith(prefix + "=")
               for prefix in EFFORT_ARGUMENT_PREFIXES):
            raise HardDenyError(
                item,
                "effort flags are permanently prohibited in every configuration file, "
                "prompt, and CLI invocation")
        out.append(item)
    return out


def minimal_env(extra: Mapping[str, str] | None = None,
                allowlist: Sequence[str] = DEFAULT_ENV_ALLOWLIST) -> dict[str, str]:
    """Build the smallest practical child environment (S13, S13.3).

    Only allowlisted names are inherited. `extra` is applied on top, and its
    VALUES are never logged by this module.
    """
    allowed = {name.upper() for name in allowlist}
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    env.update(extra or {})
    return env


# --------------------------------------------------------------------------
# Executable resolution and identity (S13.4)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ExecutableIdentity:
    name: str
    path: str
    size_bytes: int
    mtime_utc: float
    digest: str
    digest_kind: str  # "sha256" | "sha256_head+size"


def executable_identity(path: str | os.PathLike[str], name: str = "") -> ExecutableIdentity:
    """Record identity information for an executable, honestly labelled."""
    import hashlib

    file_path = pathlib.Path(path).resolve()
    if not file_path.is_file():
        raise ProcessError("missing_executable", f"not a file: {file_path}")
    stat = file_path.stat()

    hasher = hashlib.sha256()
    if stat.st_size <= FULL_HASH_MAX_BYTES:
        with file_path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(block)
        kind = "sha256"
    else:
        with file_path.open("rb") as handle:
            hasher.update(handle.read(HEAD_DIGEST_BYTES))
        hasher.update(str(stat.st_size).encode("ascii"))
        kind = "sha256_head+size"

    return ExecutableIdentity(
        name=name or file_path.name,
        path=str(file_path),
        size_bytes=stat.st_size,
        mtime_utc=stat.st_mtime,
        digest=hasher.hexdigest(),
        digest_kind=kind,
    )


def resolve_executable(
    name: str,
    *,
    repo_root: str | os.PathLike[str] | None = None,
    search_path: str | None = None,
) -> ExecutableIdentity:
    """Resolve an executable to an absolute path, refusing repo-local shadowing.

    S13.4: "reject repo-local shadowing and unexpected PATH changes". A binary
    found inside the repository under test is never trusted as a toolchain
    executable.
    """
    found = shutil.which(name, path=search_path)
    if not found:
        raise ProcessError("executable_not_found", f"{name!r} is not on PATH")
    resolved = pathlib.Path(found).resolve()
    if repo_root is not None:
        root = pathlib.Path(repo_root).resolve()
        if root == resolved or root in resolved.parents:
            raise ProcessError(
                "repo_local_shadowing",
                f"{name!r} resolved to {resolved}, which is inside the repository "
                f"{root}; a repo-local executable is never trusted as a toolchain binary")
    return executable_identity(resolved, name=name)


# --------------------------------------------------------------------------
# Process-tree termination
# --------------------------------------------------------------------------


def terminate_process_tree(pid: int, *, timeout: float = 15.0) -> bool:
    """Terminate a process and all of its descendants. Returns True on success.

    Windows uses `taskkill /PID <pid> /T /F`, invoked as an argv array (never a
    shell string). POSIX kills the process group.
    """
    if os.name == "nt":
        taskkill = shutil.which("taskkill")
        if not taskkill:
            raise ProcessError("no_taskkill", "taskkill.exe is not available on PATH")
        completed = subprocess.run(  # noqa: S603 - argv array, shell=False
            [taskkill, "/PID", str(pid), "/T", "/F"],
            shell=False, capture_output=True, text=True, timeout=timeout, check=False)
        # 128 = "process not found" (already exited): treat as success.
        return completed.returncode in (0, 128)
    try:
        os.killpg(os.getpgid(pid), 9)
        return True
    except (ProcessLookupError, PermissionError):
        return False


# --------------------------------------------------------------------------
# Windows Job Objects (proven mechanism; Phase 3 makes it the default)
# --------------------------------------------------------------------------

_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
_PROCESS_SET_QUOTA = 0x0100
_PROCESS_TERMINATE = 0x0001


def job_objects_available() -> bool:
    """True when Windows Job Objects can be created in this environment."""
    if os.name != "nt":
        return False
    try:
        job = WindowsJobObject()
    except Exception:
        return False
    job.close()
    return True


class WindowsJobObject:
    """A kill-on-close Job Object, built with stdlib `ctypes` only.

    Closing the job handle terminates every process still assigned to it, which
    is the containment guarantee `taskkill` cannot give (a child that spawns and
    exits between enumeration and kill can escape taskkill; it cannot escape a
    job it was created inside).
    """

    def __init__(self) -> None:
        if os.name != "nt":
            raise ProcessError("not_windows", "Job Objects exist only on Windows")
        import ctypes
        from ctypes import wintypes

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_int64),
                ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        self._ctypes = ctypes
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        self._kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self._kernel32.OpenProcess.restype = wintypes.HANDLE
        self._kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self._kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        self._kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self._kernel32.SetInformationJobObject.restype = wintypes.BOOL
        self._kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]

        handle = self._kernel32.CreateJobObjectW(None, None)
        if not handle:
            raise ProcessError("create_job_failed",
                               f"CreateJobObjectW failed: {ctypes.get_last_error()}")
        self._handle = handle

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        ok = self._kernel32.SetInformationJobObject(
            handle, _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(info), ctypes.sizeof(info))
        if not ok:
            error = ctypes.get_last_error()
            self.close()
            raise ProcessError("set_job_info_failed",
                               f"SetInformationJobObject failed: {error}")

    def assign_pid(self, pid: int) -> None:
        """Assign a running process to this job."""
        ctypes = self._ctypes
        process_handle = self._kernel32.OpenProcess(
            _PROCESS_SET_QUOTA | _PROCESS_TERMINATE, False, pid)
        if not process_handle:
            raise ProcessError("open_process_failed",
                               f"OpenProcess({pid}) failed: {ctypes.get_last_error()}")
        try:
            if not self._kernel32.AssignProcessToJobObject(self._handle, process_handle):
                raise ProcessError(
                    "assign_job_failed",
                    f"AssignProcessToJobObject failed: {ctypes.get_last_error()}")
        finally:
            self._kernel32.CloseHandle(process_handle)

    def close(self) -> None:
        """Close the job handle, terminating everything still assigned to it."""
        handle = getattr(self, "_handle", None)
        if handle:
            self._kernel32.CloseHandle(handle)
            self._handle = None

    def __enter__(self) -> "WindowsJobObject":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProcessResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    tree_terminated: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def run(
    argv: Sequence[str],
    *,
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    input_text: str | None = None,
) -> ProcessResult:
    """Run a bounded subprocess from an argv array. Never uses a shell.

    On timeout the whole process TREE is terminated and `timed_out` is True. A
    timeout is never interpreted as success (S14).
    """
    checked = assert_argv_safe(argv)
    child_env = dict(env) if env is not None else minimal_env()

    popen_kwargs: dict[str, Any] = {
        "shell": False,                      # explicit: never a shell
        "cwd": str(cwd) if cwd is not None else None,
        "env": child_env,
        "stdin": subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }
    if os.name != "nt":
        popen_kwargs["start_new_session"] = True   # own process group for killpg

    started = time.monotonic()
    process = subprocess.Popen(checked, **popen_kwargs)  # noqa: S603 - argv array, shell=False
    timed_out = False
    tree_terminated = False
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        tree_terminated = terminate_process_tree(process.pid)
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()

    return ProcessResult(
        argv=tuple(checked),
        returncode=process.returncode if process.returncode is not None else -1,
        stdout=stdout or "",
        stderr=stderr or "",
        duration_seconds=time.monotonic() - started,
        timed_out=timed_out,
        tree_terminated=tree_terminated,
    )


def python_argv(script: str | os.PathLike[str], *args: str) -> list[str]:
    """argv for running a Python script with the CURRENT interpreter.

    Used by the fake-process test harness so tests never depend on a `python` on
    PATH resolving to something unexpected.
    """
    return [sys.executable, str(script), *args]
