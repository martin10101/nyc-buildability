"""One-backend runtime selection for the D-024 unit-C adapter (M0-T104).

Selects EXACTLY ONE process-management backend per supervisor session —
the native background-session host (``claude --bg`` + ``claude agents``)
or the existing controller dispatch — and refuses ever to activate two
(D-024-R153). Selection fails closed: any required native capability that
is not positively ``supported`` (including ``unknown`` after a probe
failure) selects the controller, with a machine-readable reason.

The controller fallback is the EXISTING dispatch path, injected as a
callable: this module never re-implements it, and the custom host is
neither removed nor deprecated here — that is a separate reviewed change
after parity + failure tests (replace-not-layer, R180).

Restart semantics (R032): after a supervisor restart the durable dispatch
records are reconciled against the live ``agents --json`` listing —
already-running sessions map by deterministic identity and are NOT
re-dispatched; sessions absent from both the active and completed listings
surface as ``unexpected-exit`` findings for the controller (never a silent
re-run). ``activation_limitations()`` reports the honest persistence
posture: no automatic host-start registration is configured, so reboot
recovery requires the one-command start, and that limitation is an
activation blocker — never a claim of fully unattended persistence.

Supervisor-freeze qualifying evidence: D-024-R153, D-024-R172.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping, Sequence

from .native_runtime import (
    AGENTS_STATUS_ALL_ARGV,
    AGENTS_STATUS_ARGV,
    CLASS_BLOCKED_INPUT,
    CLASS_COMPLETED,
    CLASS_FAILED,
    CLASS_RUNNING,
    CLASS_STOPPED,
    CommandResult,
    DispatchSpec,
    NativeCapabilities,
    NativeRuntimeError,
    NativeSessionIdentity,
    NativeSessionStatus,
    RunCommand,
    STATUS_SUPPORTED,
    run_command,
    build_background_argv,
    build_verb_argv,
    child_environment,
    find_by_identity,
    parse_agents_json,
)

BACKEND_NATIVE = "native-background"
BACKEND_CONTROLLER = "controller"

#: Closed selection-reason codes (capability gaps append their detail).
REASON_NATIVE_READY = "native-ready"
REASON_CONFIG_CONTROLLER = "config-controller"
REASON_CAPABILITY_GAP = "capability-gap"


@dataclasses.dataclass(frozen=True)
class BackendSelection:
    """One recorded backend decision (deterministic; no timestamps)."""

    backend: str
    reason: str
    claude_version: str | None


def select_runtime_backend(caps: NativeCapabilities, *,
                           prefer_native: bool) -> BackendSelection:
    """Select the single runtime backend for this session.

    Native requires BOTH an explicit opt-in (``prefer_native``) and a fully
    ``supported`` background surface; everything else — including probe
    failures that degrade to ``unknown`` — selects the existing controller
    dispatch (fail closed, R153).
    """
    if not prefer_native:
        return BackendSelection(BACKEND_CONTROLLER, REASON_CONFIG_CONTROLLER,
                                caps.claude_version)
    gaps = caps.background_gaps()
    if gaps:
        return BackendSelection(
            BACKEND_CONTROLLER, f"{REASON_CAPABILITY_GAP}:{';'.join(gaps)}",
            caps.claude_version)
    return BackendSelection(BACKEND_NATIVE, REASON_NATIVE_READY,
                            caps.claude_version)


class RuntimeSession:
    """Holds the ONE active backend of a supervisor session.

    A second activation attempt is a typed refusal: never two active
    process-management systems (R153), not even transiently for a
    "migration" — switching backends means a new supervisor session.
    """

    def __init__(self) -> None:
        self._selection: BackendSelection | None = None

    @property
    def active(self) -> BackendSelection | None:
        return self._selection

    def activate(self, selection: BackendSelection) -> BackendSelection:
        if self._selection is not None:
            raise NativeRuntimeError(
                "backend_already_active",
                f"backend {self._selection.backend!r} is already active for "
                f"this session; never two process-management systems (R153)")
        if selection.backend not in (BACKEND_NATIVE, BACKEND_CONTROLLER):
            raise NativeRuntimeError("unknown_backend",
                                     f"unknown backend {selection.backend!r}")
        self._selection = selection
        return selection


@dataclasses.dataclass(frozen=True)
class DaemonStatus:
    """Observability of the native background daemon, derived from one
    live listing attempt — never guessed."""

    available: bool
    detail: str


class NativeBackgroundBackend:
    """Thin wrappers over the native background-session host.

    All process state lives in the native daemon; this class only builds
    argv, controls the child environment, and parses the structured feed.
    """

    def __init__(self, run: RunCommand | None = None,
                 base_env: Mapping[str, str] | None = None) -> None:
        self._run = run or run_command
        self._base_env = base_env

    def dispatch(self, spec: DispatchSpec) -> CommandResult:
        """Dispatch one background session with an EXPLICIT child
        environment (inherited session markers stripped — transcript
        suppression hazard, R162-discharge section 4.3)."""
        env = child_environment(self._base_env) if self._base_env is not None \
            else None
        return self._run(build_background_argv(spec), env=env, cwd=spec.cwd)

    def observe(self, *, include_completed: bool = False
                ) -> tuple[NativeSessionStatus, ...]:
        """One passive ``claude agents --json`` poll (R154: consumed outside
        Fable context). Malformed/unavailable feeds raise typed errors."""
        argv = AGENTS_STATUS_ALL_ARGV if include_completed else AGENTS_STATUS_ARGV
        result = self._run(argv)
        if result.status != STATUS_SUPPORTED:
            raise NativeRuntimeError(
                "agents_feed_unavailable",
                f"agents --json did not succeed: {result.status} "
                f"exit={result.exit_code} {result.stderr!r:.120}")
        return parse_agents_json(result.stdout)

    def daemon_status(self) -> DaemonStatus:
        try:
            self.observe()
        except NativeRuntimeError as exc:
            return DaemonStatus(False, f"{exc.code}: {exc.message}")
        return DaemonStatus(True, "agents --json listing succeeded")

    def logs(self, session_ref: str) -> CommandResult:
        return self._run(build_verb_argv("logs", session_ref))

    def stop(self, session_ref: str) -> CommandResult:
        return self._run(build_verb_argv("stop", session_ref))

    def respawn(self, session_ref: str | None = None, *,
                all_sessions: bool = False) -> CommandResult:
        return self._run(build_verb_argv("respawn", session_ref,
                                         all_sessions=all_sessions))

    def attach_argv(self, session_ref: str) -> tuple[str, ...]:
        """Attach is interactive (returns a live terminal); the adapter only
        constructs the command for an operator, never executes it."""
        return build_verb_argv("attach", session_ref)


class ControllerBackend:
    """The feature-detected fallback: the EXISTING controller dispatch,
    injected as a callable. Nothing is re-implemented here, and nothing is
    deprecated here (R180: removal is a separate reviewed change after
    parity + failure evidence)."""

    def __init__(self, dispatch: Callable[[DispatchSpec], object]) -> None:
        self._dispatch = dispatch

    def dispatch(self, spec: DispatchSpec) -> object:
        return self._dispatch(spec)


# ---------------------------------------------------------------------------
# Supervisor-restart reconciliation (R032; no duplicates, no silent re-runs)
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class RestartReconciliation:
    """Classification of every durably recorded dispatch after a restart."""

    running: tuple[NativeSessionIdentity, ...]
    blocked_input: tuple[NativeSessionIdentity, ...]
    completed: tuple[NativeSessionIdentity, ...]
    stopped: tuple[NativeSessionIdentity, ...]
    failed: tuple[NativeSessionIdentity, ...]
    unexpected_exit: tuple[NativeSessionIdentity, ...]

    @property
    def safe_to_dispatch(self) -> tuple[NativeSessionIdentity, ...]:
        """Identities a restarted supervisor may act on WITHOUT duplicating
        work: none of the observed ones — only ``unexpected_exit`` items,
        and those only after a controller decision (never silently)."""
        return self.unexpected_exit


def reconcile_after_restart(
        expected: Sequence[NativeSessionIdentity],
        observed_active: Sequence[NativeSessionStatus],
        observed_completed: Sequence[NativeSessionStatus] = (),
) -> RestartReconciliation:
    """Map durable dispatch records onto the live listing.

    An expected identity observed active maps by session UUID (then exact
    name) and is NEVER re-dispatched; one found only among completed
    sessions is done; one absent everywhere is an ``unexpected-exit``
    finding for the controller.
    """
    buckets: dict[str, list[NativeSessionIdentity]] = {
        CLASS_RUNNING: [], CLASS_BLOCKED_INPUT: [], CLASS_COMPLETED: [],
        CLASS_STOPPED: [], CLASS_FAILED: [], "missing": []}
    for identity in expected:
        record = find_by_identity(observed_active, identity) \
            or find_by_identity(observed_completed, identity)
        if record is None:
            buckets["missing"].append(identity)
            continue
        classification = record.classification
        if classification not in buckets:
            # unknown display states park with blocked-input: the controller
            # must look before anything is re-run (never a silent guess)
            classification = CLASS_BLOCKED_INPUT
        buckets[classification].append(identity)
    return RestartReconciliation(
        running=tuple(buckets[CLASS_RUNNING]),
        blocked_input=tuple(buckets[CLASS_BLOCKED_INPUT]),
        completed=tuple(buckets[CLASS_COMPLETED]),
        stopped=tuple(buckets[CLASS_STOPPED]),
        failed=tuple(buckets[CLASS_FAILED]),
        unexpected_exit=tuple(buckets["missing"]))


def activation_limitations() -> tuple[str, ...]:
    """The honest persistence posture (R032): reported as activation
    blockers, never papered over as unattended persistence."""
    return (
        "no automatic host-start registration is configured for the native "
        "background daemon; after a reboot the campaign resumes only via "
        "the one-command start",
        "this limitation is an activation blocker for continuous mode "
        "(R187 hold: activation stays owner-gated regardless)",
    )
