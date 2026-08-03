#!/usr/bin/env python3
"""The authenticated model-change path (D-007 S3.2 rule 6, S12.1).

Rule 6 has five separable requirements, and each is a separate, testable gate
here:

1. **Controller-owned IPC channel protected by OS access control.**
   `EndpointPlan` describes a Windows named pipe whose DACL (an SDDL string)
   admits only the owner's account and SYSTEM. `probe_named_pipe_support()`
   actually CREATES such a pipe through `ctypes` and closes it, so the claim
   "this is creatable on this host" is measured, not asserted. What is PROVEN vs
   DEFERRED is stated in `NAMED_PIPE_STATUS` and repeated in the README: pipe
   creation with a restrictive DACL is proven; the long-lived unattended pipe
   SERVER loop is deferred. The transport this build actually uses is
   `FileEndpoint`: a controller-owned request directory inside the runtime
   directory, which `assert_endpoint_isolated` proves is outside every
   worker-writable root.
2. **Worker/reviewer-origin denial.** `assert_caller_allowed` walks the caller's
   real process ancestry (Toolhelp32 on Windows, `/proc` on POSIX) and denies any
   caller that IS, or descends from, a recorded worker or reviewer process. It
   also denies a request that arrived through a worker-writable path at all.
3. **Explicit interactive owner confirmation bound to the exact change.** The
   controller displays provider, old model, new model, and the resulting
   selection digest, and requires the operator to type back a challenge derived
   from that exact change. A generic "y" cannot satisfy it, and a confirmation
   captured for one change cannot be replayed against another.
4. **Checkpoint-boundary application.** `apply_change` refuses unless the caller
   proves it is at a checkpoint boundary, and it never touches task state.
5. **Complete audit record.** Caller identity, channel, confirmation evidence,
   before/after `model_selection.toml` digests, and the affected run/task ids.

A `model_selection.toml` change arriving by ANY other path is refused and pauses
per S4.5 (`detect_out_of_band_change`). Editing the runtime selection never trips
the controller manifest (the manifest excludes that file by construction), which
`manifest_unaffected` re-checks rather than assumes.
"""
from __future__ import annotations

import dataclasses
import hashlib
import hmac
import os
import pathlib
from typing import Any, Callable, Mapping, Sequence

from .config import ConfigError, load_model_selection
from .manifest import MODEL_SELECTION_FILENAME
from .models import digest_of, to_utc_iso

#: Honest status of the named-pipe transport. `doctor` prints this verbatim.
NAMED_PIPE_STATUS = (
    "PROVEN: a named pipe restricted by an SDDL DACL to the owner's account and SYSTEM can "
    "be created and closed on this host through stdlib ctypes (probe_named_pipe_support). "
    "DEFERRED: the long-lived unattended pipe SERVER loop (overlapped I/O, per-connection "
    "impersonation, reconnect) is not built in this phase. The transport in use is the "
    "controller-owned FileEndpoint under the runtime directory, whose isolation from every "
    "worker-writable root is checked on every request."
)

#: Owner + SYSTEM full control, no inherited ACEs. `%s` is filled with the owner SID.
PIPE_SDDL_TEMPLATE = "D:P(A;;GA;;;SY)(A;;GA;;;{owner_sid})"
PIPE_NAME_TEMPLATE = r"\\.\pipe\NYCBuildabilitySupervisor-{checkout_key}"

CHANNEL_NAMED_PIPE = "windows_named_pipe"
CHANNEL_FILE_ENDPOINT = "controller_file_endpoint"

WORKER_PIDS_KEY = "worker_process_ids"
REVIEWER_PIDS_KEY = "reviewer_process_ids"
SELECTION_DIGEST_KEY = "model_selection_digest"
RUN_OVERRIDE_KEY = "run_model_override"
CHANGE_LOG_KEY = "model_change_audit"

ENDPOINT_DIRNAME = "ipc"


class IpcError(Exception):
    """A model-change request was refused. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Process ancestry
# --------------------------------------------------------------------------


def _parent_pid_windows(pid: int) -> int:
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
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
    if snapshot in (0, -1, ctypes.c_void_p(-1).value):
        return 0
    try:
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        if not kernel32.Process32First(snapshot, ctypes.byref(entry)):
            return 0
        while True:
            if entry.th32ProcessID == pid:
                return int(entry.th32ParentProcessID)
            if not kernel32.Process32Next(snapshot, ctypes.byref(entry)):
                return 0
    finally:
        kernel32.CloseHandle(snapshot)


def _parent_pid_posix(pid: int) -> int:
    stat_path = pathlib.Path("/proc") / str(pid) / "stat"
    try:
        raw = stat_path.read_text(encoding="utf-8", errors="replace")
        tail = raw[raw.rindex(")") + 1:].split()
        return int(tail[1]) if len(tail) > 1 else 0
    except (OSError, ValueError):
        return 0


def parent_pid(pid: int) -> int:
    """The parent pid, or 0 when it cannot be determined."""
    if pid <= 0:
        return 0
    return _parent_pid_windows(pid) if os.name == "nt" else _parent_pid_posix(pid)


def ancestry(pid: int, *, max_depth: int = 24) -> tuple[int, ...]:
    """The pid's ancestor chain, nearest first. Bounded and cycle-safe."""
    chain: list[int] = []
    seen: set[int] = set()
    current = pid
    for _ in range(max_depth):
        current = parent_pid(current)
        if current <= 0 or current in seen:
            break
        seen.add(current)
        chain.append(current)
    return tuple(chain)


# --------------------------------------------------------------------------
# The endpoint
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class EndpointPlan:
    """The controller-owned endpoint: what it is and what protects it."""

    channel: str
    address: str
    sddl: str
    owner_sid: str
    icacls_argv: tuple[str, ...]
    note: str

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["icacls_argv"] = list(self.icacls_argv)
        return data

    def redacted(self) -> dict[str, Any]:
        """Display form. The account SID identifies the machine user (S13.9)."""
        data = self.to_dict()
        sid = self.owner_sid
        masked = (sid[:9] + "...") if sid.startswith("S-1-5-21") else ("<sid>" if sid else "")
        data["owner_sid"] = masked
        data["sddl"] = self.sddl.replace(sid, masked) if sid else self.sddl
        data["icacls_argv"] = [
            (arg.replace(sid, masked) if sid and sid in arg else arg)
            for arg in self.icacls_argv]
        return data


def current_owner_sid() -> str:
    """The current user's SID on Windows ('' elsewhere or when unavailable)."""
    if os.name != "nt":
        return ""
    try:
        import ctypes
        from ctypes import wintypes

        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        advapi32.OpenProcessToken.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
        advapi32.GetTokenInformation.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD)]
        advapi32.ConvertSidToStringSidW.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_wchar_p)]

        token = wintypes.HANDLE()
        # TOKEN_QUERY = 0x0008
        if not advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), 0x0008,
                                         ctypes.byref(token)):
            return ""
        try:
            size = wintypes.DWORD(0)
            # TokenUser = 1. The first call only sizes the buffer and is EXPECTED
            # to fail with ERROR_INSUFFICIENT_BUFFER, so its return is ignored.
            advapi32.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
            buffer = ctypes.create_string_buffer(size.value)
            if not advapi32.GetTokenInformation(token, 1, buffer, size,
                                                ctypes.byref(size)):
                return ""
            # TOKEN_USER { SID_AND_ATTRIBUTES { PSID Sid; DWORD Attributes; } }
            sid_ptr = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
            string_sid = ctypes.c_wchar_p()
            if not advapi32.ConvertSidToStringSidW(ctypes.c_void_p(sid_ptr),
                                                   ctypes.byref(string_sid)):
                return ""
            try:
                return str(string_sid.value or "")
            finally:
                kernel32.LocalFree(string_sid)
        finally:
            kernel32.CloseHandle(token)
    except Exception:  # pragma: no cover - platform dependent
        return ""


def endpoint_plan(*, checkout_key: str, runtime_dir: str | os.PathLike[str],
                  prefer_named_pipe: bool = True) -> EndpointPlan:
    """Describe the endpoint this controller would own. Creates nothing."""
    owner_sid = current_owner_sid()
    if os.name == "nt" and prefer_named_pipe and owner_sid:
        address = PIPE_NAME_TEMPLATE.format(checkout_key=checkout_key[:32])
        return EndpointPlan(
            CHANNEL_NAMED_PIPE, address,
            PIPE_SDDL_TEMPLATE.format(owner_sid=owner_sid), owner_sid,
            (), NAMED_PIPE_STATUS)
    directory = pathlib.Path(runtime_dir) / ENDPOINT_DIRNAME
    argv: tuple[str, ...] = ()
    if os.name == "nt":
        argv = ("icacls", str(directory), "/inheritance:r",
                "/grant:r", f"*{owner_sid}:(OI)(CI)F" if owner_sid else "%USERNAME%:(OI)(CI)F",
                "/grant:r", "*S-1-5-18:(OI)(CI)F")
    return EndpointPlan(
        CHANNEL_FILE_ENDPOINT, str(directory),
        PIPE_SDDL_TEMPLATE.format(owner_sid=owner_sid or "OWNER"), owner_sid, argv,
        "controller-owned request directory inside the runtime directory; isolation from "
        "every worker-writable root is verified on each request")


@dataclasses.dataclass(frozen=True)
class PipeProbe:
    supported: bool
    detail: str
    address: str = ""


def probe_named_pipe_support(*, checkout_key: str = "probe") -> PipeProbe:
    """Create and immediately close an SDDL-restricted named pipe (Windows only).

    This is the measurement behind `NAMED_PIPE_STATUS`. It creates nothing
    persistent: the handle is closed before returning.
    """
    if os.name != "nt":
        return PipeProbe(False, "not Windows; named pipes are not the transport here")
    owner_sid = current_owner_sid()
    if not owner_sid:
        return PipeProbe(False, "the owner SID could not be read; refusing to create a pipe "
                                "without a restrictive DACL")
    try:
        import ctypes
        from ctypes import wintypes

        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        class SECURITY_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("nLength", wintypes.DWORD),
                        ("lpSecurityDescriptor", ctypes.c_void_p),
                        ("bInheritHandle", wintypes.BOOL)]

        sddl = PIPE_SDDL_TEMPLATE.format(owner_sid=owner_sid)
        #: The account SID identifies the machine user, so only a masked form is
        #: ever reported out of this function (S13.9 never-send).
        shown = PIPE_SDDL_TEMPLATE.format(owner_sid=owner_sid[:9] + "...")
        descriptor = ctypes.c_void_p()
        advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(wintypes.ULONG)]
        if not advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
                sddl, 1, ctypes.byref(descriptor), None):
            return PipeProbe(False, f"SDDL {shown!r} could not be converted "
                                    f"(error {ctypes.get_last_error()})")
        try:
            attributes = SECURITY_ATTRIBUTES()
            attributes.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
            attributes.lpSecurityDescriptor = descriptor
            attributes.bInheritHandle = False
            address = PIPE_NAME_TEMPLATE.format(checkout_key=str(checkout_key)[:32])
            kernel32.CreateNamedPipeW.argtypes = [
                wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                ctypes.POINTER(SECURITY_ATTRIBUTES)]
            kernel32.CreateNamedPipeW.restype = wintypes.HANDLE
            handle = kernel32.CreateNamedPipeW(
                address,
                0x00000003,   # PIPE_ACCESS_DUPLEX
                0x00000006,   # PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE
                1, 4096, 4096, 0, ctypes.byref(attributes))
            if handle == ctypes.c_void_p(-1).value or not handle:
                return PipeProbe(False, f"CreateNamedPipeW failed with "
                                        f"{ctypes.get_last_error()}", address)
            kernel32.CloseHandle(handle)
            return PipeProbe(True, f"created and closed an SDDL-restricted pipe "
                                   f"({shown})", address)
        finally:
            kernel32.LocalFree(descriptor)
    except Exception as exc:  # pragma: no cover - platform dependent
        return PipeProbe(False, f"named-pipe probe raised {type(exc).__name__}: {exc}")


def assert_endpoint_isolated(endpoint_path: str | os.PathLike[str],
                             worker_writable_roots: Sequence[str]) -> None:
    """The worker environment must not be able to reach the endpoint AT ALL (rule 6)."""
    endpoint = pathlib.Path(endpoint_path).resolve()
    for root in worker_writable_roots:
        if not root:
            continue
        resolved = pathlib.Path(root).resolve()
        if endpoint == resolved or resolved in endpoint.parents \
                or endpoint in resolved.parents:
            raise IpcError(
                "endpoint_reachable_by_worker",
                f"the IPC endpoint {endpoint} overlaps the worker-writable root {resolved}; "
                f"S3.2 rule 6 requires the worker environment to be unable to reach the "
                f"endpoint at all")


# --------------------------------------------------------------------------
# Caller origin
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Caller:
    """Who is asking. `pid` is measured, not claimed: ancestry is resolved from it."""

    pid: int
    account: str = ""
    channel: str = CHANNEL_FILE_ENDPOINT
    arrived_via_path: str = ""

    def identity(self) -> dict[str, Any]:
        return {"pid": self.pid, "account": self.account, "channel": self.channel}


def assert_caller_allowed(
    caller: Caller,
    *,
    journal: Any,
    controller_pid: int | None = None,
    worker_writable_roots: Sequence[str] = (),
) -> tuple[int, ...]:
    """Deny worker- and reviewer-originated requests (S3.2 rule 6). Returns the ancestry."""
    worker_pids = {int(p) for p in (journal.get_state(WORKER_PIDS_KEY, []) or [])}
    reviewer_pids = {int(p) for p in (journal.get_state(REVIEWER_PIDS_KEY, []) or [])}
    forbidden = worker_pids | reviewer_pids

    if caller.arrived_via_path:
        assert_endpoint_isolated(caller.arrived_via_path, worker_writable_roots)

    if caller.pid in forbidden:
        raise IpcError(
            "worker_origin_denied",
            f"pid {caller.pid} is a recorded "
            f"{'worker' if caller.pid in worker_pids else 'reviewer'} process; requests from "
            f"the worker or reviewer process trees are identified and DENIED (S3.2 rule 6)")

    chain = ancestry(caller.pid)
    for ancestor in chain:
        if ancestor in forbidden:
            raise IpcError(
                "worker_origin_denied",
                f"pid {caller.pid} descends from recorded "
                f"{'worker' if ancestor in worker_pids else 'reviewer'} process {ancestor}; "
                f"the whole process tree is denied, not just the leaf")

    if controller_pid is not None and caller.pid != controller_pid \
            and controller_pid not in chain:
        raise IpcError(
            "unrelated_caller",
            f"pid {caller.pid} is neither the controller ({controller_pid}) nor one of its "
            f"descendants; a local invocation is NOT automatically owner-authenticated "
            f"(S3.2 rule 2)")
    return chain


def record_worker_pid(journal: Any, pid: int, *, role: str = "worker") -> None:
    """Record a launched worker/reviewer pid so origin denial can see its tree."""
    key = WORKER_PIDS_KEY if role == "worker" else REVIEWER_PIDS_KEY
    pids = list(journal.get_state(key, []) or [])
    if pid not in pids:
        pids.append(pid)
    journal.set_state(key, pids)


# --------------------------------------------------------------------------
# The change itself
# --------------------------------------------------------------------------

SCOPE_PERSISTENT = "persistent"
SCOPE_SINGLE_RUN = "single_run"


@dataclasses.dataclass(frozen=True)
class ModelChangeRequest:
    """One requested model change. Immutable; its digest is what gets confirmed."""

    provider: str
    old_model: str
    new_model: str
    scope: str
    run_id: str
    task_id: str
    before_selection_digest: str
    after_selection_digest: str
    requested_at_utc: str = ""

    def __post_init__(self) -> None:
        if self.provider not in ("codex", "claude"):
            raise IpcError("unknown_provider", f"{self.provider!r} is not a provider")
        if self.scope not in (SCOPE_PERSISTENT, SCOPE_SINGLE_RUN):
            raise IpcError("unknown_scope", f"{self.scope!r} is not a change scope")
        if not self.new_model:
            raise IpcError("no_model", "a model change must name the new model")

    def digest(self) -> str:
        return digest_of(dataclasses.asdict(self))

    def display(self) -> str:
        """Exactly what the controller shows the owner before confirming."""
        return (
            f"MODEL CHANGE ({self.scope})\n"
            f"  provider                : {self.provider}\n"
            f"  current model           : {self.old_model or '(account/CLI default)'}\n"
            f"  requested model         : {self.new_model}\n"
            f"  selection digest before : {self.before_selection_digest}\n"
            f"  selection digest after  : {self.after_selection_digest}\n"
            f"  run / task              : {self.run_id} / {self.task_id}\n"
        )

    def challenge(self) -> str:
        """The token the operator must type back. Derived from THIS change only."""
        return hashlib.sha256(
            f"model-change:{self.digest()}".encode("utf-8")).hexdigest()[:12]


def assert_allowlisted(request: ModelChangeRequest, config: Any) -> None:
    """A model outside its OWN provider's allowlist is refused in every role (rule 4)."""
    allowed = tuple(config.allowlist(request.provider))
    if not allowed:
        raise IpcError(
            "no_explicit_selection_permitted",
            f"{request.provider}.allowed_models is empty: only the account/CLI default may "
            f"be used and no explicit selection is permitted")
    if request.new_model not in allowed:
        raise IpcError(
            "model_not_allowlisted",
            f"{request.new_model!r} is not in {request.provider}.allowed_models "
            f"{list(allowed)}; a model outside its own provider's list may never be used in "
            f"any role, even if the provider defaults to or suggests it")


@dataclasses.dataclass(frozen=True)
class Confirmation:
    """Evidence that the owner confirmed THIS change interactively."""

    confirmed: bool
    method: str
    challenge: str
    response: str
    at_utc: str
    request_digest: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def confirm_interactively(
    request: ModelChangeRequest,
    *,
    prompt: Callable[[str], str],
    method: str = "controller_tty",
) -> Confirmation:
    """Display the exact change and require the challenge token back.

    A bare "y" cannot satisfy this, and a response captured for one change cannot
    be replayed against another because the challenge is derived from the
    request digest.
    """
    challenge = request.challenge()
    message = (request.display()
               + f"\nType this exact confirmation token to proceed: {challenge}\n> ")
    response = str(prompt(message)).strip()
    ok = hmac.compare_digest(response, challenge)
    return Confirmation(ok, method, challenge, "<matched>" if ok else "<mismatched>",
                        to_utc_iso(), request.digest())


# --------------------------------------------------------------------------
# Out-of-band detection and manifest independence
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class TamperVerdict:
    detected: bool
    reason_code: str
    reason: str
    synchronous_stop: bool = False


def detect_out_of_band_change(*, recorded_digest: str, current_digest: str) -> TamperVerdict:
    """A `model_selection.toml` change arriving by any other path is refused (rule 6)."""
    if not recorded_digest:
        return TamperVerdict(False, "no_baseline",
                             "no recorded selection digest yet; nothing to compare")
    if recorded_digest == current_digest:
        return TamperVerdict(False, "unchanged", "the runtime selection matches the record")
    return TamperVerdict(
        True, "out_of_band_model_selection_change",
        f"model_selection.toml changed outside the authenticated IPC path (recorded "
        f"{recorded_digest[:16]}..., found {current_digest[:16]}...). The change is REFUSED "
        f"and the run pauses: this is controller-adjacent tampering (S4.5)",
        synchronous_stop=True)


def manifest_unaffected(manifest: Mapping[str, Any]) -> tuple[bool, str]:
    """Re-check that the runtime selection is outside the controller manifest (S13.1)."""
    files = manifest.get("files", {}) or {}
    covered = list(files) if isinstance(files, Mapping) else [
        entry.get("path", "") for entry in files if isinstance(entry, Mapping)]
    offending = [path for path in covered
                 if pathlib.PurePosixPath(str(path)).name == MODEL_SELECTION_FILENAME]
    if offending:
        return False, (f"the controller manifest covers {offending}; editing the runtime "
                       f"model selection would invalidate the controller, which S13.1 "
                       f"explicitly forbids")
    return True, (f"{MODEL_SELECTION_FILENAME} is outside the manifest: a runtime model "
                  f"change never invalidates the controller, while editing the immutable "
                  f"config does")


# --------------------------------------------------------------------------
# The endpoint object that ties it together
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ChangeOutcome:
    applied: bool
    reason_code: str
    reason: str
    request_digest: str = ""
    audit_record: dict[str, Any] = dataclasses.field(default_factory=dict)


class ModelChangeEndpoint:
    """The controller-owned endpoint. Every rule-6 gate runs here, in order."""

    def __init__(
        self,
        *,
        journal: Any,
        config: Any,
        selection_path: str | os.PathLike[str],
        runtime_dir: str | os.PathLike[str],
        checkout_key: str,
        audit: Any = None,
        controller_pid: int | None = None,
        worker_writable_roots: Sequence[str] = (),
    ) -> None:
        self.journal = journal
        self.config = config
        self.selection_path = pathlib.Path(selection_path)
        self.runtime_dir = pathlib.Path(runtime_dir)
        self.checkout_key = checkout_key
        self.audit = audit
        self.controller_pid = os.getpid() if controller_pid is None else controller_pid
        self.worker_writable_roots = tuple(worker_writable_roots)
        self.plan = endpoint_plan(checkout_key=checkout_key, runtime_dir=runtime_dir)

    # -- helpers -------------------------------------------------------------

    def current_selection_digest(self) -> str:
        try:
            return load_model_selection(self.selection_path).digest()
        except ConfigError as exc:
            raise IpcError("selection_unreadable",
                           f"the runtime model selection could not be read: {exc}") from exc

    def recorded_selection_digest(self) -> str:
        return str(self.journal.get_state(SELECTION_DIGEST_KEY, "") or "")

    def record_selection_digest(self, digest: str) -> None:
        self.journal.set_state(SELECTION_DIGEST_KEY, digest)

    def check_tampering(self) -> TamperVerdict:
        return detect_out_of_band_change(
            recorded_digest=self.recorded_selection_digest(),
            current_digest=self.current_selection_digest())

    # -- the gated change ----------------------------------------------------

    def request_change(
        self,
        *,
        caller: Caller,
        provider: str,
        new_model: str,
        old_model: str,
        after_selection_digest: str,
        run_id: str,
        task_id: str,
        scope: str = SCOPE_PERSISTENT,
        prompt: Callable[[str], str],
        at_checkpoint_boundary: bool = False,
    ) -> ChangeOutcome:
        """Run every rule-6 gate in order and apply only if ALL of them pass."""
        # Gate 1: OS access control / endpoint isolation and caller origin.
        chain = assert_caller_allowed(
            caller, journal=self.journal, controller_pid=self.controller_pid,
            worker_writable_roots=self.worker_writable_roots)

        # Gate 2: nothing changed the selection behind our back.
        tamper = self.check_tampering()
        if tamper.detected:
            self._audit_change("model_change_refused_tampering", {
                "reason_code": tamper.reason_code, "caller": caller.identity()})
            return ChangeOutcome(False, tamper.reason_code, tamper.reason)

        before = self.current_selection_digest()
        request = ModelChangeRequest(
            provider=provider, old_model=old_model, new_model=new_model, scope=scope,
            run_id=run_id, task_id=task_id, before_selection_digest=before,
            after_selection_digest=after_selection_digest,
            requested_at_utc=to_utc_iso())

        # Gate 3: allowlist (rule 4) - checked BEFORE bothering the owner.
        assert_allowlisted(request, self.config)

        # Gate 4: explicit interactive confirmation bound to this exact change.
        confirmation = confirm_interactively(request, prompt=prompt)
        if not confirmation.confirmed:
            record = self._audit_change("model_change_unconfirmed", {
                "request_digest": request.digest(), "caller": caller.identity(),
                "channel": self.plan.channel, "ancestry": list(chain),
                "confirmation": confirmation.to_dict()})
            return ChangeOutcome(
                False, "unconfirmed",
                "the owner did not confirm this exact change; an unconfirmed change is NEVER "
                "applied (S3.2 rule 6)", request.digest(), record)

        # Gate 5: checkpoint boundary.
        if not at_checkpoint_boundary:
            record = self._audit_change("model_change_deferred_to_checkpoint", {
                "request_digest": request.digest(), "caller": caller.identity()})
            return ChangeOutcome(
                False, "not_at_checkpoint_boundary",
                "the change is confirmed but takes effect only at a checkpoint boundary; it "
                "is held, and it never resets task state (S3.2 rule 6)",
                request.digest(), record)

        return self.apply_change(request, confirmation=confirmation, caller=caller,
                                 ancestry_chain=chain)

    def apply_change(self, request: ModelChangeRequest, *, confirmation: Confirmation,
                     caller: Caller, ancestry_chain: Sequence[int] = ()) -> ChangeOutcome:
        """Apply a CONFIRMED change at a checkpoint boundary and write the audit record."""
        if not confirmation.confirmed:
            raise IpcError("unconfirmed_change",
                           "apply_change requires a positive confirmation bound to the "
                           "request digest")
        if not hmac.compare_digest(confirmation.request_digest, request.digest()):
            raise IpcError(
                "confirmation_not_bound",
                "the confirmation was captured for a different change; a confirmation is "
                "bound to one exact request and is never reused")

        task_state_before = {
            key: self.journal.get_state(key)
            for key in ("current_state", "claude_session_identity", "rotation_pending")
        }

        if request.scope == SCOPE_SINGLE_RUN:
            self.journal.set_state(RUN_OVERRIDE_KEY, {
                "provider": request.provider, "model": request.new_model,
                "run_id": request.run_id, "request_digest": request.digest(),
                "applied_at_utc": to_utc_iso()})
        else:
            self.record_selection_digest(request.after_selection_digest)

        task_state_after = {
            key: self.journal.get_state(key)
            for key in ("current_state", "claude_session_identity", "rotation_pending")
        }
        if task_state_before != task_state_after:  # pragma: no cover - defensive
            raise IpcError("task_state_reset",
                           "a model change must never reset task state (S3.2 rule 6)")

        record = self._audit_change("model_change_applied", {
            "caller": caller.identity(),
            "caller_ancestry": list(ancestry_chain),
            "channel": self.plan.channel,
            "endpoint": self.plan.address,
            "confirmation": confirmation.to_dict(),
            "provider": request.provider,
            "old_model": request.old_model,
            "new_model": request.new_model,
            "scope": request.scope,
            "before_selection_digest": request.before_selection_digest,
            "after_selection_digest": request.after_selection_digest,
            "run_id": request.run_id,
            "task_id": request.task_id,
            "request_digest": request.digest(),
        })
        return ChangeOutcome(True, "applied",
                             f"{request.provider} model set to {request.new_model!r} "
                             f"({request.scope}) at a checkpoint boundary",
                             request.digest(), record)

    # -- the --codex-model per-run override (S3.2 rule 2) --------------------

    def request_run_override(
        self,
        *,
        caller: Caller,
        provider: str,
        model: str,
        current_model: str,
        run_id: str,
        task_id: str,
        prompt: Callable[[str], str],
        at_checkpoint_boundary: bool = True,
    ) -> ChangeOutcome:
        """`--codex-model <name>`: same authenticated path, single-run scope (rule 2)."""
        return self.request_change(
            caller=caller, provider=provider, new_model=model, old_model=current_model,
            after_selection_digest=self.current_selection_digest(), run_id=run_id,
            task_id=task_id, scope=SCOPE_SINGLE_RUN, prompt=prompt,
            at_checkpoint_boundary=at_checkpoint_boundary)

    def active_run_override(self, provider: str, run_id: str) -> str:
        """The model an accepted single-run override installed, or ''."""
        data = self.journal.get_state(RUN_OVERRIDE_KEY)
        if not isinstance(data, Mapping):
            return ""
        if data.get("provider") != provider or data.get("run_id") != run_id:
            return ""
        return str(data.get("model", ""))

    def clear_run_override(self) -> None:
        self.journal.set_state(RUN_OVERRIDE_KEY, None)

    # -- audit ---------------------------------------------------------------

    def _audit_change(self, event: str, detail: Mapping[str, Any]) -> dict[str, Any]:
        record = {"event": event, "at_utc": to_utc_iso(), **dict(detail)}
        history = list(self.journal.get_state(CHANGE_LOG_KEY, []) or [])
        history.append(record)
        self.journal.set_state(CHANGE_LOG_KEY, history)
        if self.audit is not None:
            self.audit.append(event, detail=dict(record))
        return record


def decision_record_fields(*, model_used: str, override_active: bool,
                           selection_digest: str) -> dict[str, Any]:
    """The model fields every decision record must carry (S3.2 rules 2 and 5)."""
    return {
        "model_used": model_used,
        "single_run_override_active": bool(override_active),
        "model_selection_digest": selection_digest,
    }
