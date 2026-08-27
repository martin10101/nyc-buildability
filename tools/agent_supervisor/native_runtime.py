"""Native background-runtime primitives (D-024 Amendment 3 unit C, M0-T104).

Measured-at-use feature detection, deterministic session identity, explicit
child-environment control, dispatch/verb argv construction, and
``claude agents --json`` ingestion for the native background-session host
(D-024-R153/R172, accepted M0-T102 matrix rows background-session-host /
structured-passive-observation / worktree-isolation). Codex-side observation
consumes the parsed records OUTSIDE Fable's context and never asks the worker
for routine token/status reports (R154).

Security posture (G5 unit-C preconditions):
* every detection probe is help/version-only (no login, no config mutation,
  no network beyond what the CLI does locally); the allowlist is closed;
* builders never emit permission-bypass or remote-control/cloud flags and no
  adapter path opens an inbound port;
* derived names are a closed lowercase charset built ONLY from validated
  campaign/task identifiers — by construction they carry no hostname,
  username, or secret material;
* live captures pass the Phase B redaction subsystem before any fixture
  write (public repository).

Non-obvious invariants this module encodes from live measurement (2.1.247):
* an UNKNOWN subcommand invoked with ``--help`` exits 0 and prints the
  GENERAL help, so verb support is classified by the verb-specific usage
  line, never by exit code alone;
* background children inherit ``CLAUDE_CODE_CHILD_SESSION``/``CLAUDECODE``
  from the dispatching session and then suppress transcript saving
  (M0-T103 R162-discharge section 4.3) — the child environment is therefore
  always explicit, never inherited as-is;
* the unflagged permission mode resolves to the classifier-guarded ``auto``
  (there is no literal ``default`` mode on 2.1.24x, and unflagged is NOT
  bypassPermissions);
* native CLI worktrees (``-w``) branch from the DEFAULT branch with no
  baseRef parameter, so integration-branch dispatch requires an explicit
  pinned-SHA reset guard (matrix worktree-isolation row; R156).

Backend selection, restart reconciliation, and the controller fallback live
in ``runtime_backend`` (one bounded seam, R145/R180).

Supervisor-freeze qualifying evidence: D-024-R153, D-024-R172.
"""
from __future__ import annotations

import dataclasses
import json
import re
import shutil
import subprocess
import uuid
from collections.abc import Callable, Mapping, Sequence

from .capability_probe import PROBE_TIMEOUT_S, classify_flags
from .telemetry_redaction import redact_user_paths


class NativeRuntimeError(ValueError):
    """Typed error for the native runtime adapter (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# ---------------------------------------------------------------------------
# Command execution (injectable; default resolves through PATH like the probe)
# ---------------------------------------------------------------------------

#: Capability statuses share the probe vocabulary (M0-T086).
STATUS_SUPPORTED = "supported"
STATUS_NOT_IN_HELP = "not-detected-in-help"
STATUS_ABSENT = "absent"
STATUS_UNKNOWN = "unknown"


@dataclasses.dataclass(frozen=True)
class CommandResult:
    """Outcome of one adapter-issued CLI command."""

    status: str          # supported | absent | unknown (execution outcome)
    exit_code: int | None
    stdout: str
    stderr: str


RunCommand = Callable[..., CommandResult]


def run_command(argv: Sequence[str], *, env: Mapping[str, str] | None = None,
                 cwd: str | None = None,
                 timeout: float = PROBE_TIMEOUT_S) -> CommandResult:
    """Run one CLI command; never raises. Resolves the executable first:
    bare names bypass PATHEXT under Windows CreateProcess (M0-T086 lesson)."""
    exe = shutil.which(argv[0])
    if exe is None:
        return CommandResult(STATUS_ABSENT, None, "", f"{argv[0]} not on PATH")
    try:
        # encoding is pinned: the CLI emits UTF-8 (e.g. the arrow in the
        # attach help), which crashes the default cp1252 reader thread on
        # Windows and silently degrades the probe to empty output.
        proc = subprocess.run(
            [exe, *argv[1:]], capture_output=True, text=True, check=False,
            encoding="utf-8", errors="replace",
            timeout=timeout, env=dict(env) if env is not None else None,
            cwd=cwd)
    except subprocess.TimeoutExpired:
        return CommandResult(STATUS_UNKNOWN, None, "", f"timeout after {timeout}s")
    except OSError as exc:
        return CommandResult(STATUS_UNKNOWN, None, "", f"OSError: {exc}")
    return CommandResult(
        STATUS_SUPPORTED if proc.returncode == 0 else STATUS_UNKNOWN,
        proc.returncode, proc.stdout or "", proc.stderr or "")


# ---------------------------------------------------------------------------
# Feature detection (measured at use; NEVER cached — M0-T103 advisory 2)
# ---------------------------------------------------------------------------

#: Dispatch-surface flags classified from ``claude --help``.
DISPATCH_FLAG_TOKENS: tuple[str, ...] = (
    "--bg", "--background", "--name", "--session-id", "--agent",
    "--worktree", "--permission-mode", "--strict-mcp-config", "--tools",
)

#: Background-host verbs probed as ``claude <verb> --help`` (read-only).
BACKGROUND_VERBS: tuple[str, ...] = ("agents", "attach", "logs", "stop", "respawn")

#: Minimum surface for the native backend to be selectable at all.
#: NOTE (G3 ADV-3): ``--session-id`` is required-in-help but deliberately
#: NEVER emitted by build_background_argv — ``--bg`` manages the session id
#: and ignores the flag (measured 2.1.247). Its presence here is a
#: conservative readiness gate: a future CLI dropping it from help signals a
#: surface change and falls the selection back to the proven controller.
REQUIRED_BACKGROUND_FLAGS: tuple[str, ...] = ("--bg", "--name", "--session-id")
REQUIRED_BACKGROUND_VERBS: tuple[str, ...] = BACKGROUND_VERBS


@dataclasses.dataclass(frozen=True)
class NativeCapabilities:
    """One measured-at-use snapshot of the installed native surface."""

    claude_version: str | None
    flags: Mapping[str, str]
    verbs: Mapping[str, str]

    def background_gaps(self) -> tuple[str, ...]:
        """Required features that are not positively ``supported`` (any
        weaker classification — including ``unknown`` — is a gap: selection
        fails closed to the controller, R153)."""
        gaps = [f"flag:{tok}={self.flags.get(tok, STATUS_ABSENT)}"
                for tok in REQUIRED_BACKGROUND_FLAGS
                if self.flags.get(tok) != STATUS_SUPPORTED]
        gaps += [f"verb:{verb}={self.verbs.get(verb, STATUS_ABSENT)}"
                 for verb in REQUIRED_BACKGROUND_VERBS
                 if self.verbs.get(verb) != STATUS_SUPPORTED]
        if self.claude_version is None:
            gaps.insert(0, "claude:absent")
        return tuple(gaps)

    @property
    def background_host_ready(self) -> bool:
        return not self.background_gaps()


def _classify_verb(verb: str, result: CommandResult) -> str:
    """Verb support from ``claude <verb> --help``. Measured 2.1.247 trap: an
    unknown subcommand with ``--help`` ALSO exits 0 but prints the general
    usage, so only a verb-specific usage line proves support."""
    if result.status == STATUS_ABSENT:
        return STATUS_ABSENT
    if result.exit_code != 0:
        return STATUS_UNKNOWN
    text = (result.stdout + "\n" + result.stderr).strip()
    first = text.splitlines()[0].strip() if text else ""
    if first.startswith(f"Usage: claude {verb}"):
        return STATUS_SUPPORTED
    return STATUS_NOT_IN_HELP


def detect_native_capabilities(run: RunCommand | None = None) -> NativeCapabilities:
    """Detect the native background surface by executing fresh read-only
    probes NOW. Installed-version facts are measured at use and never cached:
    the binary auto-updates itself (observed 2.1.246 -> 2.1.247 mid-session,
    M0-T103 R162 discharge)."""
    runner = run or run_command
    version = runner(("claude", "--version"))
    if version.status == STATUS_ABSENT:
        absent_flags = {tok: STATUS_ABSENT for tok in DISPATCH_FLAG_TOKENS}
        absent_verbs = {verb: STATUS_ABSENT for verb in BACKGROUND_VERBS}
        return NativeCapabilities(None, absent_flags, absent_verbs)
    claude_version = (version.stdout.strip().splitlines()[0]
                      if version.status == STATUS_SUPPORTED and version.stdout.strip()
                      else None)
    help_result = runner(("claude", "--help"))
    help_text = help_result.stdout + "\n" + help_result.stderr
    flags = classify_flags(help_text, list(DISPATCH_FLAG_TOKENS))
    verbs = {verb: _classify_verb(verb, runner(("claude", verb, "--help")))
             for verb in BACKGROUND_VERBS}
    return NativeCapabilities(claude_version, flags, verbs)


def build_detection_fixture(caps: NativeCapabilities, *, task: str) -> dict:
    """Deterministic, committable record of one detection run (task-id
    stamped per G3 ADV-1; no timestamps or user paths in the body)."""
    return {
        "schema": "native_runtime_detection/v1",
        "directive": "D-024",
        "task": task,
        "claude_version": caps.claude_version,
        "flags": dict(sorted(caps.flags.items())),
        "verbs": dict(sorted(caps.verbs.items())),
        "background_gaps": list(caps.background_gaps()),
    }


# ---------------------------------------------------------------------------
# Deterministic session identity (R153: named + deterministic)
# ---------------------------------------------------------------------------

#: Fixed namespace => uuid5 identities are stable across machines/sessions.
_IDENTITY_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL,
                                 "nyc-buildability/d-024/native-runtime")

_ID_TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_MAX_NAME_LEN = 64


@dataclasses.dataclass(frozen=True)
class NativeSessionIdentity:
    """Deterministic (name, session UUID) pair for one producer dispatch.

    Measured on 2.1.247: ``--bg`` MANAGES the session id itself and ignores
    ``--session-id`` (stderr warning), so the deterministic NAME is the
    operative dispatch key for background sessions; the daemon-assigned live
    UUID is read back from the listing and durably recorded by the caller.
    The derived uuid5 remains the stable EXPECTED-identity key for durable
    records and non-background flows.
    """

    name: str
    session_id: str


def derive_session_identity(campaign_id: str, task_id: str,
                            attempt: int = 1) -> NativeSessionIdentity:
    """Derive the deterministic identity for (campaign, task, attempt).

    Inputs are validated to a closed lowercase charset, so the derived name
    cannot carry a hostname, username, path, or secret (G5 precondition) —
    the guarantee is by construction, not by scanning.
    """
    parts = {"campaign_id": campaign_id, "task_id": task_id}
    normalized: dict[str, str] = {}
    for label, value in parts.items():
        candidate = str(value).strip().lower()
        if not _ID_TOKEN_RE.fullmatch(candidate):
            raise NativeRuntimeError(
                "invalid_identity_token",
                f"{label} {value!r} must match {_ID_TOKEN_RE.pattern}")
        normalized[label] = candidate
    if not isinstance(attempt, int) or isinstance(attempt, bool) \
            or not 1 <= attempt <= 999:
        raise NativeRuntimeError("invalid_attempt",
                                 f"attempt must be an int in 1..999, got {attempt!r}")
    name = f"{normalized['campaign_id']}-{normalized['task_id']}-a{attempt}"
    if len(name) > _MAX_NAME_LEN:
        raise NativeRuntimeError(
            "identity_too_long",
            f"derived name {name!r} exceeds {_MAX_NAME_LEN} chars")
    return NativeSessionIdentity(
        name=name, session_id=str(uuid.uuid5(_IDENTITY_NAMESPACE, name)))


# ---------------------------------------------------------------------------
# Explicit child-environment control (R162-discharge section 4.3)
# ---------------------------------------------------------------------------

#: Inherited session markers that flag a spawn as a child session and
#: suppress its transcript saving; a background producer must never inherit
#: them from the dispatching orchestrator shell.
CHILD_ENV_STRIP_KEYS: tuple[str, ...] = ("CLAUDECODE",)
CHILD_ENV_STRIP_PREFIXES: tuple[str, ...] = ("CLAUDE_CODE_",)


def child_environment(base_env: Mapping[str, str]) -> dict[str, str]:
    """The explicit environment for a dispatched background session: the
    parent environment minus every Claude session marker."""
    return {
        key: value for key, value in base_env.items()
        if key not in CHILD_ENV_STRIP_KEYS
        and not any(key.startswith(p) for p in CHILD_ENV_STRIP_PREFIXES)
    }


# ---------------------------------------------------------------------------
# Permission-mode vocabulary (measured on 2.1.246/2.1.247)
# ---------------------------------------------------------------------------

INSTALLED_PERMISSION_MODES: tuple[str, ...] = (
    "acceptEdits", "auto", "bypassPermissions", "manual", "dontAsk", "plan")
#: The unflagged default measured live in both R162-discharge canaries.
UNFLAGGED_DEFAULT_PERMISSION_MODE = "auto"
#: Never dispatchable by this adapter (Amendment 3: no permission bypass).
FORBIDDEN_PERMISSION_MODES: tuple[str, ...] = ("bypassPermissions",)


def validate_permission_mode(mode: str | None) -> str:
    """Resolve/validate a dispatch permission mode.

    ``None`` (unflagged) resolves to the measured default ``auto`` — NOT to
    a literal ``default`` mode, which does not exist on 2.1.24x. Bypass is
    refused outright.
    """
    if mode is None:
        return UNFLAGGED_DEFAULT_PERMISSION_MODE
    if mode in FORBIDDEN_PERMISSION_MODES:
        raise NativeRuntimeError(
            "forbidden_permission_mode",
            f"{mode!r} is never dispatchable by this adapter (D-024 "
            f"Amendment 3: no permission-bypass flags)")
    if mode not in INSTALLED_PERMISSION_MODES:
        raise NativeRuntimeError(
            "unknown_permission_mode",
            f"{mode!r} is not in the installed enum "
            f"{list(INSTALLED_PERMISSION_MODES)} (note: there is no literal "
            f"'default' mode; unflagged resolves to 'auto')")
    return mode


# ---------------------------------------------------------------------------
# Worktree base pinning (R156; native -w has NO baseRef parameter)
# ---------------------------------------------------------------------------

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
WORKTREE_BASE_HEAD = "head"


@dataclasses.dataclass(frozen=True)
class WorktreeSpec:
    """A worktree request with a mandatory pinned base (default-branch
    hazard: unpinned native worktrees branch from the DEFAULT branch)."""

    name: str
    base: str  # WORKTREE_BASE_HEAD or a full 40-hex commit SHA

    def __post_init__(self) -> None:
        if not _ID_TOKEN_RE.fullmatch(self.name):
            raise NativeRuntimeError(
                "invalid_worktree_name",
                f"worktree name {self.name!r} must match {_ID_TOKEN_RE.pattern}")
        if self.base != WORKTREE_BASE_HEAD and not _SHA_RE.fullmatch(self.base):
            raise NativeRuntimeError(
                "worktree_base_unpinned",
                f"worktree base must be {WORKTREE_BASE_HEAD!r} or a full "
                f"40-hex SHA, got {self.base!r} (default-branch hazard)")


def _worktree_reset_preamble(sha: str) -> str:
    return (
        "FIRST ACTION (worktree base pin): run `git rev-parse "
        "--show-toplevel` and confirm you are inside your OWN isolated "
        "worktree, NOT the primary checkout. If it is the primary checkout, "
        "STOP and report without running any further git command. Otherwise "
        f"run `git reset --hard {sha}` there before any other work."
    )


# ---------------------------------------------------------------------------
# Dispatch + verb argv construction
# ---------------------------------------------------------------------------

#: Flags this adapter must never emit: permission bypass (Amendment 3) and
#: every remote-control/cloud/port-opening surface (matrix
#: messaging-and-remote-control = REJECTED_OR_DEFERRED; G5 precondition).
FORBIDDEN_DISPATCH_FLAGS: tuple[str, ...] = (
    "--dangerously-skip-permissions", "--allow-dangerously-skip-permissions",
    "--teleport", "--cloud", "--chrome", "--environment", "--tmux",
)

#: Closed value charsets for the free argv fields (G5 F1). An agent is a
#: roster identifier; tools is empty or a comma/space list of built-in tool
#: names. Neither may begin with '-' (no flag-shaped values).
_AGENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_TOOLS_RE = re.compile(r"|[A-Za-z][A-Za-z0-9,\s()*_-]*")


@dataclasses.dataclass(frozen=True)
class DispatchSpec:
    """One validated native background dispatch request."""

    identity: NativeSessionIdentity
    prompt: str
    agent: str | None = None
    permission_mode: str | None = None
    worktree: WorktreeSpec | None = None
    strict_mcp_config: bool = True
    tools: str | None = None
    #: Working directory the session starts under (daemon sessions bind to
    #: their cwd); None inherits the dispatching process cwd.
    cwd: str | None = None

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise NativeRuntimeError("empty_prompt",
                                     "a dispatch needs a non-empty prompt")
        # G5 F1: agent and tools are free-value argv fields; validate them so
        # a caller cannot inject a flag-shaped value (defence in depth beyond
        # the argv-position + `--` fence + post-build denylist). agent is a
        # roster identifier; tools is a comma/space list of built-in tool
        # names (or "" to disable all) — neither may begin with '-'.
        if self.agent is not None and not _AGENT_RE.fullmatch(self.agent):
            raise NativeRuntimeError(
                "invalid_agent", f"agent {self.agent!r} must match "
                f"{_AGENT_RE.pattern}")
        if self.tools is not None and not _TOOLS_RE.fullmatch(self.tools):
            raise NativeRuntimeError(
                "invalid_tools", f"tools {self.tools!r} must be empty or a "
                f"comma/space list of built-in tool names (no leading '-')")


def build_background_argv(spec: DispatchSpec) -> tuple[str, ...]:
    """The exact ``claude --bg`` argv for one dispatch. Deterministic; the
    permission mode is validated; forbidden and permission-bypass flags are
    refused at construction and re-checked before return (a defence-in-depth
    denylist, not a total proof — see the value validation on DispatchSpec).

    Two canary-measured constraints (2.1.247, C1): ``--session-id`` is NOT
    emitted (``--bg`` manages the session id and ignores the flag — the
    deterministic name carries identity); and the prompt is separated by a
    literal ``--`` (variadic flags like ``--tools <tools...>`` otherwise
    swallow the positional prompt, leaving the session idle).
    """
    argv: list[str] = ["claude", "--bg", "--name", spec.identity.name]
    if spec.agent is not None:
        argv += ["--agent", spec.agent]
    mode = validate_permission_mode(spec.permission_mode)
    if spec.permission_mode is not None:
        argv += ["--permission-mode", mode]
    if spec.strict_mcp_config:
        argv.append("--strict-mcp-config")
    if spec.tools is not None:
        argv += ["--tools", spec.tools]
    prompt = spec.prompt
    if spec.worktree is not None:
        if spec.worktree.base == WORKTREE_BASE_HEAD:
            raise NativeRuntimeError(
                "worktree_base_head_unsupported_cli",
                "native CLI worktrees have no baseRef parameter and branch "
                "from the DEFAULT branch; pin an explicit 40-hex SHA so the "
                "dispatch carries a guarded reset (R156)")
        argv += ["--worktree", spec.worktree.name]
        prompt = _worktree_reset_preamble(spec.worktree.base) + "\n\n" + prompt
    argv += ["--", prompt]
    forbidden = [tok for tok in argv if tok in FORBIDDEN_DISPATCH_FLAGS]
    if forbidden:
        raise NativeRuntimeError(
            "forbidden_flag", f"builder produced forbidden flags {forbidden}")
    return tuple(argv)


def build_verb_argv(verb: str, session_ref: str | None = None, *,
                    all_sessions: bool = False) -> tuple[str, ...]:
    """Argv for attach/logs/stop/respawn. ``respawn`` alone accepts
    ``--all`` (supervisor-restart binary pickup); every other verb needs a
    session reference."""
    if verb not in ("attach", "logs", "stop", "respawn"):
        raise NativeRuntimeError("unknown_verb",
                                 f"{verb!r} is not a background-host verb")
    if all_sessions:
        if verb != "respawn":
            raise NativeRuntimeError(
                "all_not_supported", f"only respawn supports --all, not {verb}")
        return ("claude", "respawn", "--all")
    if not session_ref or not session_ref.strip():
        raise NativeRuntimeError("missing_session_ref",
                                 f"{verb} requires a session id")
    return ("claude", verb, session_ref)


# ---------------------------------------------------------------------------
# ``claude agents --json`` ingestion (R154: passive, outside Fable context)
# ---------------------------------------------------------------------------

AGENTS_STATUS_ARGV: tuple[str, ...] = ("claude", "agents", "--json")
AGENTS_STATUS_ALL_ARGV: tuple[str, ...] = ("claude", "agents", "--json", "--all")

#: Closed classification vocabulary. ``unknown`` is a first-class honest
#: outcome (never coerced) — the controller decides what to do with it.
CLASS_RUNNING = "running"
CLASS_BLOCKED_INPUT = "blocked-input"
CLASS_COMPLETED = "completed"
CLASS_STOPPED = "stopped"
CLASS_FAILED = "failed"
CLASS_UNKNOWN = "unknown"

KIND_BACKGROUND = "background"


@dataclasses.dataclass(frozen=True)
class NativeSessionStatus:
    """One session row from ``claude agents --json``, with raw fields
    preserved beside the derived classification (raw wins any dispute)."""

    session_id: str
    name: str
    kind: str
    classification: str
    raw_status: str
    raw_state: str
    waiting_for: str
    pid: int | None
    cwd: str


def _classify_row(status: str, state: str, pid: int | None) -> str:
    """Closed mapping with ``state`` outranking ``status``.

    LITERALS MEASURED on 2.1.247 (C1 canaries + live listings): status in
    {waiting, busy, idle, ''}; state in {failed, blocked, done, stopped, ''}.
    The parked-session conflict row (status=waiting + state=failed)
    classifies FAILED (investigate before input); idle means done or
    needs-input depending on state. A few additional synonyms not observed
    here (status completed/done/finished/running/working; state completed)
    are accepted defensively — each maps to its semantically-obvious class
    and none can flip a live/blocked session into a safe-to-ignore state.
    Every UNMEASURED combination stays ``unknown``; the controller decides
    (reconcile parks unknown with blocked-input, never re-dispatch)."""
    if state == "failed":
        return CLASS_FAILED
    if state == "stopped":
        return CLASS_STOPPED
    if state in ("done", "completed") \
            or status in ("completed", "done", "finished"):
        return CLASS_COMPLETED
    if state == "blocked" or status in ("waiting", "idle"):
        # idle = "send a prompt to start" (C1 round a1): needs input.
        return CLASS_BLOCKED_INPUT
    if status in ("running", "working", "busy"):
        # "busy" measured live (this orchestrator's own row).
        return CLASS_RUNNING
    if status == "" and state == "" and pid is not None:
        # Measured shape: live rows with a pid may omit status entirely.
        return CLASS_RUNNING
    return CLASS_UNKNOWN


def parse_agents_json(text: str) -> tuple[NativeSessionStatus, ...]:
    """Parse one ``claude agents --json`` payload into typed records.

    Malformed input raises a typed error (fail closed — the statusLine
    sidecar remains the primary feed, R154); unknown EXTRA fields are
    tolerated so CLI additions do not break observation.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise NativeRuntimeError("malformed_agents_json",
                                 f"not valid JSON: {exc}") from exc
    if not isinstance(data, list):
        raise NativeRuntimeError("malformed_agents_json",
                                 f"expected a JSON array, got {type(data).__name__}")
    records: list[NativeSessionStatus] = []
    for index, row in enumerate(data):
        if not isinstance(row, dict) or not isinstance(row.get("sessionId"), str) \
                or not row["sessionId"]:
            raise NativeRuntimeError(
                "malformed_agents_json",
                f"row {index} lacks a string sessionId: {row!r:.120}")
        status = row.get("status", "")
        state = row.get("state", "")
        pid = row.get("pid")
        records.append(NativeSessionStatus(
            session_id=row["sessionId"],
            name=str(row.get("name", "")),
            kind=str(row.get("kind", STATUS_UNKNOWN)),
            classification=_classify_row(
                status if isinstance(status, str) else "",
                state if isinstance(state, str) else "",
                pid if isinstance(pid, int) else None),
            raw_status=status if isinstance(status, str) else "",
            raw_state=state if isinstance(state, str) else "",
            waiting_for=str(row.get("waitingFor", "")),
            pid=pid if isinstance(pid, int) else None,
            cwd=str(row.get("cwd", "")),
        ))
    return tuple(records)


def background_sessions(
        records: Sequence[NativeSessionStatus]) -> tuple[NativeSessionStatus, ...]:
    """Only background sessions are adapter-managed; interactive sessions
    (the owner's terminals) are observed but NEVER managed."""
    return tuple(r for r in records if r.kind == KIND_BACKGROUND)


def find_by_identity(records: Sequence[NativeSessionStatus],
                     identity: NativeSessionIdentity) -> NativeSessionStatus | None:
    """Match by session UUID first (authoritative), then by exact name."""
    for record in records:
        if record.session_id == identity.session_id:
            return record
    for record in records:
        if record.name == identity.name:
            return record
    return None


_UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def _mask_uuids(text: str) -> str:
    return _UUID_RE.sub(lambda m: m.group(0)[:8] + "-[MASKED]", text)


def _mask_value(value: object) -> object:
    """Recursively mask any string value: home-path redaction + UUID
    truncation. Non-strings pass through; containers recurse."""
    if isinstance(value, str):
        redacted, _ = redact_user_paths(value)
        return _mask_uuids(redacted)
    if isinstance(value, dict):
        return {k: _mask_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_mask_value(v) for v in value]
    return value


def mask_session_row(row: dict) -> dict:
    """Mask one raw agents-row for a committed fixture (public repo).

    G5 F3: a COMPREHENSIVE pass over EVERY string value (home-path
    redaction + UUID truncation), not a three-field allowlist — a home path
    or session UUID in ``name``/``waitingFor``/any future field is masked
    too. ``sessionId``/``id`` additionally collapse to their first 8 chars so
    a short (non-UUID-shaped) id still loses its tail."""
    masked = {k: _mask_value(v) for k, v in row.items()}
    for key in ("sessionId", "id"):
        value = masked.get(key)
        if isinstance(value, str) and "-[MASKED]" not in value \
                and len(value) > 8:
            masked[key] = value[:8] + "-[MASKED]"
    return masked


def build_agents_fixture(rows: Sequence[dict], *, task: str) -> dict:
    """Deterministic masked fixture body for a captured live listing
    (task-id stamped per G3 ADV-1; volatile pids/timestamps dropped)."""
    sanitized = []
    for row in rows:
        masked = mask_session_row(row)
        masked.pop("pid", None)
        masked.pop("startedAt", None)
        sanitized.append(masked)
    return {
        "schema": "native_runtime_agents_listing/v1",
        "directive": "D-024",
        "task": task,
        "sessions": sanitized,
    }
