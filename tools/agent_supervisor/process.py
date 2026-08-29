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

Windows process-tree control - what is PROVEN here:

    PROVEN in Phase 1  `terminate_process_tree()` via `taskkill /T /F`, exercised
                       against a real spawned child tree in the Phase 1 tests;
                       `run()` timeout handling that invokes it.
    PROVEN in Phase 1  `WindowsJobObject` creation, configuration with
                       JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, assignment of a real
                       child, and kill-on-close, via stdlib `ctypes`.
    PHASE 4 (here)     `ProcessContainer` makes the Job Object the DEFAULT
                       container for every launched child on Windows. Every
                       `run()` and every `ClaudeRunner` unit now launches inside
                       a kill-on-close job unless the host refuses one, in which
                       case the container falls back to `taskkill /T /F` and
                       RECORDS the fallback reason instead of silently degrading.

Breakaway and nested jobs (Phase 4, the carried deferral):

* The container deliberately does NOT set `JOB_OBJECT_LIMIT_BREAKAWAY_OK` or
  `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK`. Those flags exist to let a child ESCAPE
  the job; a containment mechanism must never opt into its own bypass. They are
  listed in `FORBIDDEN_JOB_LIMIT_FLAGS` and `assert_no_breakaway()` refuses them
  wherever a caller could supply limit flags or creation flags.
* `CREATE_BREAKAWAY_FROM_JOB` is likewise refused as a creation flag.
* Nested jobs: since Windows 8 / Server 2012 a process may belong to a job
  hierarchy, so assigning a child that is already inside the terminal's or CI
  runner's job normally succeeds. When it does not (an old host, or a parent job
  without nesting), `AssignProcessToJobObject` fails with ERROR_ACCESS_DENIED and
  the container records `nested_job_assignment_denied` and falls back to
  `taskkill /T /F`. The fallback is reported, never assumed.
* `taskkill` fallback is weaker on purpose-honesty grounds: a grandchild spawned
  between enumeration and kill can escape `taskkill`; it cannot escape a job it
  was created inside. `ContainmentReport.kind` always says which one was actually
  achieved so no caller can claim job-strength containment it did not get.

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

#: Owner-gated ACTIVATION flags, denied in any argv this package SYNTHESIZES.
#:
#: M0-T079 C3 (G5 I1): `--owner-enable-bounded-auto` is a per-launch owner act,
#: typed by a human at a terminal. Nothing here changes that - what it closes is
#: REPLAY. Paths that build an argv from a stored prefix (a watchdog's launcher
#: argv, an autostart task definition) would otherwise re-fire an enable the
#: owner typed once, on every scheduler trigger, forever - and "per-launch" would
#: quietly mean "per-launch until it is written into a scheduled task".
#: `resume_scheduler` already guards its own argv with `assert_fixed_action`
#: exact-list-equality; this is the same discipline for every other synthesized
#: argv, enforced in the one shared checker rather than at each call site.
#:
#: Scope, stated plainly: this denies the flag in argv the SUPERVISOR builds. It
#: does not and cannot police what an operator types directly, which is the
#: intended way to enable the mode.
OWNER_ACTIVATION_ARGUMENTS: frozenset[str] = frozenset({
    "--owner-enable-bounded-auto",
})

#: Environment variables a child is allowed to inherit by default. Everything
#: else is dropped: the worker receives no ambient credentials (S13.3).
DEFAULT_ENV_ALLOWLIST: tuple[str, ...] = (
    "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "TMPDIR",
    "HOME", "USERPROFILE", "LANG", "LC_ALL", "PATHEXT", "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE", "SYSTEMDRIVE",
)

DEFAULT_TIMEOUT_SECONDS = 900

#: Cap on the child stdout/stderr characters RETAINED and propagated by `run()`.
#: The reviewer's `--json` stdout is untrusted output that `parse_usage_telemetry`
#: then `splitlines()` over; without a cap a runaway or adversarial child could
#: balloon what is buffered, split, and written into the durable record. The cap
#: bounds what is retained - never silently: an overflow appends a structured
#: truncation marker and sets the truncation flag, and truncation never raises
#: (G5 M0-T042 I-3).
MAX_CAPTURE_BYTES = 8 * 1024 * 1024

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
        # V1.1 hardening L-1 (G3 review): the `=`-form of a bypass flag
        # (`--flag=value`) is hard-denied exactly like the bare token, matching
        # the effort-prefix rule below - previously only the exact token matched.
        if lowered in HARD_DENY_ARGUMENTS or any(
                lowered.startswith(flag + "=") for flag in HARD_DENY_ARGUMENTS):
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
        if lowered in OWNER_ACTIVATION_ARGUMENTS or any(
                lowered.startswith(flag + "=") for flag in OWNER_ACTIVATION_ARGUMENTS):
            raise HardDenyError(
                item,
                "owner activation flags are a per-launch human act and are denied in any "
                "argv this package synthesizes; a stored launcher prefix must never be "
                "able to replay an enable the owner typed once (M0-T079 C3)")
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


#: Forced into the environment of EVERY controller-launched CLAUDE child process,
#: unconditionally (D-024 Amendment 13, R278/R286). Background auto-updates are
#: disabled so the certified Claude CLI identity cannot drift mid-run the way it
#: did at seq-30 (installed 2.1.251 vs certified 2.1.248). `DISABLE_AUTOUPDATER`
#: only blocks the background update attempt; `DISABLE_UPDATES` (which also blocks
#: a manual `claude update`) is deliberately NOT used here (R280). This is
#: CLAUDE-scoped on purpose - codex children (`codex_channel`) keep `minimal_env`
#: untouched, so this pair is applied by `claude_child_env`, never by `minimal_env`.
FORCED_CLAUDE_CHILD_ENV: dict[str, str] = {"DISABLE_AUTOUPDATER": "1"}


def claude_child_env(extra: Mapping[str, str] | None = None,
                     allowlist: Sequence[str] = DEFAULT_ENV_ALLOWLIST) -> dict[str, str]:
    """Child environment for a controller-launched CLAUDE process (R278/R286).

    Identical to ``minimal_env(extra, allowlist)`` except that
    ``FORCED_CLAUDE_CHILD_ENV`` is applied LAST - after both the allowlist filter
    and the ``extra`` (config ``extra_env``) merge. Applying it last is the whole
    point: neither omitting ``DISABLE_AUTOUPDATER`` from the env allowlist nor a
    config ``extra_env`` supplying a conflicting value can drop or override the
    forced disable.

    Fail-closed choice for AS-6 - THE FORCED PAIR WINS. A conflicting
    ``extra_env["DISABLE_AUTOUPDATER"]`` (e.g. ``"0"``) is overridden back to
    ``"1"`` rather than raising a typed refusal. Rationale: the guarantee this
    control exists to make is that NO input - parent env, allowlist, or config -
    ever yields a controller-launched claude child without ``DISABLE_AUTOUPDATER=1``.
    An unconditional forced value delivers that guarantee for every input; a
    launch-time refusal is strictly weaker (it fails the launch on a config typo
    instead of neutralizing it, and adds an error path that could itself regress
    to fail-open). The forced pair is therefore made unconditional and total.
    """
    env = minimal_env(extra, allowlist)
    env.update(FORCED_CLAUDE_CHILD_ENV)
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
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

#: Job limit flags that would let a contained child ESCAPE the job. A containment
#: mechanism never opts into its own bypass, so these are refused rather than
#: offered as options (S13.3 "process ceilings", S13.12 invariant 2).
_JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x00000800
_JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x00001000
FORBIDDEN_JOB_LIMIT_FLAGS: dict[str, int] = {
    "JOB_OBJECT_LIMIT_BREAKAWAY_OK": _JOB_OBJECT_LIMIT_BREAKAWAY_OK,
    "JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK": _JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK,
}

#: The creation flag that lets a NEW process start outside its parent's job.
_CREATE_BREAKAWAY_FROM_JOB = 0x01000000
FORBIDDEN_CREATION_FLAGS: dict[str, int] = {
    "CREATE_BREAKAWAY_FROM_JOB": _CREATE_BREAKAWAY_FROM_JOB,
}

_ERROR_ACCESS_DENIED = 5

#: Containment kinds, strongest first.
CONTAINMENT_JOB_OBJECT = "job_object"
CONTAINMENT_PROCESS_GROUP = "process_group"
CONTAINMENT_TASKKILL = "taskkill"


def assert_no_breakaway(*, limit_flags: int = 0, creation_flags: int = 0) -> None:
    """Refuse any flag that would let a contained child escape its container."""
    for name, bit in FORBIDDEN_JOB_LIMIT_FLAGS.items():
        if limit_flags & bit:
            raise ProcessError(
                "breakaway_flag_refused",
                f"{name} lets an assigned process leave the job; containment never enables "
                f"its own bypass")
    for name, bit in FORBIDDEN_CREATION_FLAGS.items():
        if creation_flags & bit:
            raise ProcessError(
                "breakaway_flag_refused",
                f"{name} starts the child OUTSIDE the supervisor's job object; refused")


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
        self._kernel32.IsProcessInJob.restype = wintypes.BOOL
        self._kernel32.IsProcessInJob.argtypes = [
            wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]

        handle = self._kernel32.CreateJobObjectW(None, None)
        if not handle:
            raise ProcessError("create_job_failed",
                               f"CreateJobObjectW failed: {ctypes.get_last_error()}")
        self._handle = handle

        # Kill-on-close ONLY. `assert_no_breakaway` proves no escape bit is set.
        limit_flags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        assert_no_breakaway(limit_flags=limit_flags)
        self.limit_flags = limit_flags

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = limit_flags
        ok = self._kernel32.SetInformationJobObject(
            handle, _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(info), ctypes.sizeof(info))
        if not ok:
            error = ctypes.get_last_error()
            self.close()
            raise ProcessError("set_job_info_failed",
                               f"SetInformationJobObject failed: {error}")

    def assign_pid(self, pid: int) -> None:
        """Assign a running process to this job.

        A nested-job refusal (ERROR_ACCESS_DENIED on a host whose parent job does
        not permit nesting) raises `nested_job_assignment_denied` specifically, so
        `ProcessContainer` can fall back to taskkill and SAY it fell back rather
        than reporting job-strength containment it did not achieve.
        """
        ctypes = self._ctypes
        process_handle = self._kernel32.OpenProcess(
            _PROCESS_SET_QUOTA | _PROCESS_TERMINATE, False, pid)
        if not process_handle:
            raise ProcessError("open_process_failed",
                               f"OpenProcess({pid}) failed: {ctypes.get_last_error()}")
        try:
            if not self._kernel32.AssignProcessToJobObject(self._handle, process_handle):
                error = ctypes.get_last_error()
                if error == _ERROR_ACCESS_DENIED:
                    raise ProcessError(
                        "nested_job_assignment_denied",
                        f"AssignProcessToJobObject({pid}) denied: this host does not permit "
                        f"the supervisor's job to nest inside the job the process is already "
                        f"in (pre-Windows-8 behaviour, or a parent job created without "
                        f"nesting). The caller must fall back and record the fallback")
                raise ProcessError(
                    "assign_job_failed",
                    f"AssignProcessToJobObject failed: {error}")
        finally:
            self._kernel32.CloseHandle(process_handle)

    def contains_pid(self, pid: int) -> bool:
        """True when `pid` is a member of THIS job (IsProcessInJob).

        This is the containment PROOF: it asks the kernel, not the code that just
        tried to assign.
        """
        ctypes = self._ctypes
        from ctypes import wintypes

        process_handle = self._kernel32.OpenProcess(
            _PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not process_handle:
            raise ProcessError("open_process_failed",
                               f"OpenProcess({pid}) failed: {ctypes.get_last_error()}")
        try:
            result = wintypes.BOOL(0)
            if not self._kernel32.IsProcessInJob(process_handle, self._handle,
                                                 ctypes.byref(result)):
                raise ProcessError("is_process_in_job_failed",
                                   f"IsProcessInJob failed: {ctypes.get_last_error()}")
            return bool(result.value)
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
# The DEFAULT container (Phase 4)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ContainmentReport:
    """What containment was ACTUALLY achieved, never what was hoped for."""

    kind: str
    job_object_used: bool
    adopted_pids: tuple[int, ...] = ()
    fallback_reason: str = ""
    verified_in_job: bool = False

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class ProcessContainer:
    """Default containment for every child the supervisor launches.

    On Windows the container IS a kill-on-close Job Object: a child assigned to
    it, and every descendant that child creates, dies when the job handle closes,
    with no enumeration race. `taskkill /T /F` remains as the fallback for hosts
    where a job cannot be created or assigned, and the fallback is recorded in
    `ContainmentReport.fallback_reason` so nothing claims job-strength
    containment it did not get.

    Off Windows the container is the POSIX process group (`start_new_session` +
    `killpg`), which `run()` already establishes.
    """

    def __init__(self, *, prefer_job_object: bool = True) -> None:
        self.prefer_job_object = prefer_job_object
        self._job: "WindowsJobObject | None" = None
        self._pids: list[int] = []
        self._fallback_reason = ""
        self._verified = False
        if os.name != "nt":
            self.kind = CONTAINMENT_PROCESS_GROUP
            return
        if not prefer_job_object:
            self.kind = CONTAINMENT_TASKKILL
            self._fallback_reason = "caller explicitly disabled the job object"
            return
        try:
            self._job = WindowsJobObject()
            self.kind = CONTAINMENT_JOB_OBJECT
        except Exception as exc:  # host refused a job object
            self._job = None
            self.kind = CONTAINMENT_TASKKILL
            self._fallback_reason = f"job object unavailable: {exc}"

    @property
    def job_object_used(self) -> bool:
        return self._job is not None

    def adopt(self, pid: int) -> str:
        """Put a running child under containment. Returns the kind achieved."""
        self._pids.append(pid)
        if self._job is None:
            return self.kind
        try:
            self._job.assign_pid(pid)
        except ProcessError as exc:
            # Nested-job refusal or a race with an already-exited child: degrade
            # HONESTLY to taskkill rather than pretending the job holds it.
            self._job.close()
            self._job = None
            self.kind = CONTAINMENT_TASKKILL
            self._fallback_reason = f"{exc.code}: {exc.message}"
            return self.kind
        try:
            self._verified = self._job.contains_pid(pid)
        except ProcessError:
            self._verified = False
        return self.kind

    def terminate_all(self) -> bool:
        """Terminate every adopted process tree. Returns True when all succeeded."""
        if self._job is not None:
            self._job.close()          # kill-on-close terminates the whole job
            self._job = None
            return True
        ok = True
        for pid in self._pids:
            try:
                ok = terminate_process_tree(pid) and ok
            except ProcessError:
                ok = False
        return ok

    def close(self) -> None:
        """Release the container. On Windows this KILLS anything still inside."""
        if self._job is not None:
            self._job.close()
            self._job = None

    def report(self) -> ContainmentReport:
        return ContainmentReport(
            kind=self.kind,
            job_object_used=self._job is not None or self.kind == CONTAINMENT_JOB_OBJECT,
            adopted_pids=tuple(self._pids),
            fallback_reason=self._fallback_reason,
            verified_in_job=self._verified,
        )

    def __enter__(self) -> "ProcessContainer":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()


def default_containment_kind() -> str:
    """The containment `run()` uses on this host with no configuration at all."""
    if os.name != "nt":
        return CONTAINMENT_PROCESS_GROUP
    return CONTAINMENT_JOB_OBJECT if job_objects_available() else CONTAINMENT_TASKKILL


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------


def _bounded_capture(text: str, cap: int, stream: str) -> tuple[str, bool]:
    """Cap a captured stream, appending a structured marker on overflow (I-3).

    Returns `(possibly-truncated text, truncated?)`. A truncation is NEVER
    silent - the marker names how much was retained of the total - and this
    function never raises, so a bounded capture cannot itself crash `run()`.
    """
    if cap <= 0 or len(text) <= cap:
        return text, False
    marker = (f"\n[{stream.upper()} TRUNCATED: retained {cap} of {len(text)} "
              f"characters at the supervisor capture cap]")
    return text[:cap] + marker, True


@dataclasses.dataclass(frozen=True)
class ProcessResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    tree_terminated: bool = False
    containment: str = ""
    containment_fallback_reason: str = ""
    stdout_truncated: bool = False
    stderr_truncated: bool = False

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
    container: "ProcessContainer | None" = None,
    use_job_object: bool = True,
    max_capture_bytes: int = MAX_CAPTURE_BYTES,
) -> ProcessResult:
    """Run a bounded subprocess from an argv array. Never uses a shell.

    Phase 4: the child is launched INSIDE a `ProcessContainer`, which on Windows
    is a kill-on-close Job Object by default. On timeout the whole contained tree
    is terminated and `timed_out` is True. A timeout is never interpreted as
    success (S14). `result.containment` records the containment actually achieved.
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

    owns_container = container is None
    box = container or ProcessContainer(prefer_job_object=use_job_object)

    started = time.monotonic()
    process = subprocess.Popen(checked, **popen_kwargs)  # noqa: S603 - argv array, shell=False
    box.adopt(process.pid)
    timed_out = False
    tree_terminated = False
    try:
        try:
            stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            tree_terminated = box.terminate_all()
            try:
                stdout, stderr = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
        report = box.report()
    finally:
        if owns_container:
            box.close()

    # I-3: bound what is RETAINED and propagated. The child ran under a timeout
    # and containment; the cap keeps a runaway/adversarial stream from ballooning
    # the durable record and the `splitlines()` scans over it, with a visible
    # marker so the truncation is never silent.
    stdout_text, stdout_truncated = _bounded_capture(
        stdout or "", max_capture_bytes, "stdout")
    stderr_text, stderr_truncated = _bounded_capture(
        stderr or "", max_capture_bytes, "stderr")
    return ProcessResult(
        argv=tuple(checked),
        returncode=process.returncode if process.returncode is not None else -1,
        stdout=stdout_text,
        stderr=stderr_text,
        duration_seconds=time.monotonic() - started,
        timed_out=timed_out,
        tree_terminated=tree_terminated,
        containment=report.kind,
        containment_fallback_reason=report.fallback_reason,
        stdout_truncated=stdout_truncated,
        stderr_truncated=stderr_truncated,
    )


def python_argv(script: str | os.PathLike[str], *args: str) -> list[str]:
    """argv for running a Python script with the CURRENT interpreter.

    Used by the fake-process test harness so tests never depend on a `python` on
    PATH resolving to something unexpected.
    """
    return [sys.executable, str(script), *args]
