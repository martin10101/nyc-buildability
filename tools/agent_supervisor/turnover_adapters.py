#!/usr/bin/env python3
"""Real-dependency ADAPTERS for the Fable->Opus turnover controller (M0-T054, third increment).

Qualifying evidence (supervisor-freeze §2, AD-093): a *reproduced provider
incident*. D-010 source-028 / R289: Fable 5 hit its weekly usage limit and hard-
stopped with the exact message

    You've reached your Fable 5 limit. Run /usage-credits to continue or switch
    models with /model.

and the CLI's built-in `fallbackModel` did NOT auto-switch. Increment 1
(`model_turnover.py`) is the PURE detection classifier; increment 2
(`turnover_controller.py`) is the deterministic ACTUATION POLICY that runs on
INJECTED Protocol dependencies (`Launcher`, `ContinuationLock`, `AuditSink`,
`Identity`, `SurvivorPredicate`). This third increment supplies CONCRETE adapters
that bind those Protocols to the supervisor's ACTUAL infrastructure - the
single-instance checkout lock (`locking.SingleInstanceLock`), the hash-chained
audit log (`audit_log.AuditLog`), and the confirmed worker launch surface
(`claude_runner.build_argv` / `process`).

This module is strictly ADDITIVE (supervisor-freeze §1): it is a NEW file, it
adds NO behavior to any existing frozen module, and it only IMPORTS and COMPOSES
them (`model_turnover.py`, `turnover_controller.py`, `locking.py`,
`audit_log.py`, `claude_runner.py`, `process.py`, `models.py` are all read, never
edited). Everything here is exercised WITHOUT a live provider call, a real
Claude/Codex process, a config change, or the network: the launcher takes an
INJECTED command-runner so tests substitute a fake that records the argv and
returns a synthetic result, and the lock/audit adapters run against temp dirs.

The governing rule is FAIL-CLOSED (AD-025, restated by the supervisor-freeze
lane): every adapter, on any ambiguity or unreadable durable state, refuses the
action that could double-launch. The successor model is HARD-CODED to
`claude-opus-4-8` at `xhigh` effort (the R289 fallback target - D-010
source-028); a caller-supplied model is NEVER trusted or forwarded.
"""
from __future__ import annotations

import dataclasses
import uuid
from typing import Any, Callable, Mapping

from .audit_log import AuditChainError, AuditLog
from .claude_runner import RunnerConfig, build_argv
from .locking import LockError, SingleInstanceLock
from .models import sha256_hex, to_utc_iso
from .process import assert_argv_safe, minimal_env
from .turnover_controller import (
    ALLOWED_SUCCESSOR_EFFORT,
    ALLOWED_SUCCESSOR_MODEL_ID,
    LaunchRequest,
    LaunchResult,
    TurnoverLayer,
)

#: The event_type of the DEDICATED durable marker appended to the hash-chained
#: audit log when an exhaustion event has been actioned. `already_actioned`
#: scans for this marker; it is the single durable point that consumes a dedup
#: key. Kept distinct from every turnover record kind so a launched/blocked/
#: safe-stop record can never be mistaken for a dedup marker.
ACTIONED_MARKER_EVENT_TYPE = "fable_turnover_event_actioned"


def _event_dedup_digest(event_id: str) -> str:
    """A redaction-proof, deterministic dedup key for an exhaustion event id.

    The event id is stored ONLY as this SHA-256 hex digest, never in the clear:
    a 64-char lowercase hex string matches none of the redaction patterns
    (`redaction._PATTERNS`), so the durable marker survives the audit log's
    mandatory redaction pass byte-for-byte and the lookup is stable across a
    fresh adapter over the same store. A domain prefix keeps the key from
    colliding with any other digest the supervisor computes.
    """
    return sha256_hex(f"fable-turnover-event:{event_id}".encode("utf-8"))


# --------------------------------------------------------------------------
# ContinuationLock adapter -> locking.SingleInstanceLock
# --------------------------------------------------------------------------


class SingleInstanceContinuationLock:
    """`ContinuationLock` backed by the real single-instance checkout lock (S7).

    The controller's `ContinuationLock` Protocol requires `acquire()` to RETURN
    True on acquisition and False on contention, and to NEVER raise on
    contention. The real `SingleInstanceLock.acquire()` instead RAISES
    `LockError` when another live instance holds the checkout (`lock_held`), when
    a stale takeover is lost (`takeover_race`), or when the lock file is
    malformed (`malformed_lock`). This adapter translates that surface:
    a successful acquire -> True; ANY `LockError` -> False (fail closed: an
    unacquirable or ambiguous lock is treated as "already held", so the
    controller reports ALREADY_IN_PROGRESS and never launches a second successor).

    `release()` delegates to the real lock, which only removes the file when this
    process still owns it (it never removes another instance's lock).
    """

    def __init__(self, lock: SingleInstanceLock) -> None:
        self._lock = lock

    def acquire(self) -> bool:
        try:
            self._lock.acquire()
            return True
        except LockError:
            # Contention, a lost stale-takeover race, or a malformed lock file:
            # every one means "do not take the lock", so fail closed to False
            # rather than propagating - the Protocol forbids raising here.
            return False

    def release(self) -> None:
        # Never raises: the real release returns False when this process no
        # longer owns the lock, which the controller does not need to act on.
        self._lock.release()


# --------------------------------------------------------------------------
# AuditSink adapter -> audit_log.AuditLog (hash-chained, durable dedup)
# --------------------------------------------------------------------------


class HashChainedAuditSink:
    """`AuditSink` backed by the real append-only, hash-chained audit log (S13.12).

    Durability / dedup mechanism (the exact choice this increment makes):

    * `append(record)` writes ONE durable, hash-chained audit event. The record's
      ``kind`` becomes the event_type and the whole mapping becomes the event
      ``detail`` (which the log redacts before persisting, as S13.12 requires).
      It returns the record's chain ``digest`` as a stable unique id.
    * `mark_actioned(event_id)` appends a DEDICATED marker event
      (`ACTIONED_MARKER_EVENT_TYPE`) carrying only the event's redaction-proof
      dedup digest. This is the single durable point that consumes a dedup key.
    * `already_actioned(event_id)` scans the durable chain for that marker. It is
      durable across process restarts and across a FRESH adapter over the same
      store, because the marker lives in the same append-only file.

    Fail-closed reads: if the underlying log could not be loaded
    (`AuditLog.load_error` set - e.g. a forked/duplicate-sequence chain from an
    emergency stop) or the chain cannot be read, `already_actioned` returns TRUE.
    "Already actioned" is the SAFE direction: it makes the controller suppress a
    turnover it cannot prove is new, so an unreadable audit store can never cause
    a double launch. (A damaged chain also makes `append`/`mark_actioned` refuse
    via the log's own `append_to_damaged_chain` guard, but the read-side gate
    fires first, so the controller stops before ever attempting a write.)
    """

    def __init__(self, log: AuditLog) -> None:
        self._log = log

    def already_actioned(self, event_id: str) -> bool:
        # Fail closed on an unreadable/forked chain: treat as already actioned so
        # the controller never launches a successor it cannot prove is new.
        if self._log.load_error is not None:
            return True
        digest = _event_dedup_digest(event_id)
        try:
            records = self._log.read_all()
        except AuditChainError:
            return True
        for record in records:
            if record.get("event_type") != ACTIONED_MARKER_EVENT_TYPE:
                continue
            detail = record.get("detail")
            if isinstance(detail, Mapping) and detail.get("turnover_event_digest") == digest:
                return True
        return False

    def append(self, record: Mapping[str, Any]) -> str:
        event_type = str(record.get("kind") or "fable_turnover_event")
        written = self._log.append(event_type, detail=dict(record))
        return written.digest

    def mark_actioned(self, event_id: str) -> None:
        self._log.append(
            ACTIONED_MARKER_EVENT_TYPE,
            detail={"turnover_event_digest": _event_dedup_digest(event_id)},
        )


# --------------------------------------------------------------------------
# Identity adapter -> models.to_utc_iso + a documented id source
# --------------------------------------------------------------------------


class SupervisorIdentity:
    """`Identity` using the supervisor's own time/id idioms (never bare now/random).

    * `now_iso()` formats through `models.to_utc_iso`, the ONE timezone-aware UTC
      formatter every supervisor record shares. An injected `clock` (a callable
      returning an aware `datetime`) makes tests deterministic; the default asks
      `to_utc_iso()` for the current aware UTC instant (naive datetimes are
      rejected by `to_utc_iso`, never assumed local - S11.4).
    * `new_audit_id()` uses `uuid.uuid4().hex` by default (the same id idiom
      `ClaudeRunner` uses for run ids); an injected `id_source` makes tests
      deterministic.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], Any] | None = None,
        id_source: Callable[[], str] | None = None,
    ) -> None:
        self._clock = clock
        self._id_source = id_source

    def now_iso(self) -> str:
        moment = self._clock() if self._clock is not None else None
        return to_utc_iso(moment)

    def new_audit_id(self) -> str:
        if self._id_source is not None:
            return self._id_source()
        return uuid.uuid4().hex


# --------------------------------------------------------------------------
# Launcher adapter -> the confirmed worker launch surface (INJECTED runner)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class SuccessorLaunchTargets:
    """The FIXED, non-model parts of a successor invocation for one checkout.

    These describe WHERE and WITH WHICH executables a successor is launched. The
    model and effort are NEVER taken from here or from a caller - they are always
    the hard-coded `ALLOWED_SUCCESSOR_MODEL_ID` / `ALLOWED_SUCCESSOR_EFFORT`.
    `orchestrator_argv_prefix` is the argv head for an orchestrator/handoff
    launch (e.g. the supervisor `start` entry); the worker layer instead uses the
    confirmed Claude worker argv from `claude_runner.build_argv`.
    """

    checkout: str
    claude_executable: str = ""
    orchestrator_argv_prefix: tuple[str, ...] = ()
    max_turns: int = 12
    unit_timeout_seconds: float = 900.0


@dataclasses.dataclass(frozen=True)
class SuccessorInvocation:
    """What the injected command-runner is handed. The model/effort are the
    hard-coded constants; no field here is ever a caller-supplied model."""

    layer: str
    argv: tuple[str, ...]
    env: Mapping[str, str]
    model_id: str
    effort: str
    expected_worker_model: str
    task_id: str
    event_id: str
    handoff_reference: str
    safe_checkpoint_id: str
    failed_fable_execution_id: str


@dataclasses.dataclass(frozen=True)
class CommandRunResult:
    """What the injected command-runner reports back.

    * ``available`` False (or ``started`` False) means the successor could NOT be
      started - Opus 4.8 unavailable/usage-exhausted, or the launch failed. The
      adapter maps either to `LaunchResult(available=False)` and the controller
      safe-stops WITHOUT trying another model.
    * ``successor_id`` identifies the started successor.
    * ``model_id`` optionally echoes the model the runner actually started; if it
      is present and is NOT the pinned opus id the adapter fails closed.
    """

    started: bool
    successor_id: str = ""
    model_id: str = ""
    available: bool = True
    detail: str = ""


#: The injected command-runner contract: a callable that ATTEMPTS the launch
#: described by a `SuccessorInvocation` and reports a `CommandRunResult`. Tests
#: pass a fake that records the invocation and returns a synthetic result WITHOUT
#: spawning anything; production passes a real subprocess runner (see
#: `make_subprocess_command_runner`).
CommandRunner = Callable[[SuccessorInvocation], CommandRunResult]


class SupervisorLauncher:
    """`Launcher` that builds a model-PINNED successor invocation and runs it
    through an INJECTED command-runner.

    Model discipline is unconditional: the invocation is ALWAYS pinned to
    `claude-opus-4-8` at `xhigh` effort, taken from the frozen constants, and the
    `LaunchRequest.model_id` a caller supplied is NEVER read into the argv or the
    result. For the WORKER layer the argv is the confirmed Claude worker argv
    from `claude_runner.build_argv` (which emits `--model claude-opus-4-8` and is
    itself argv-safe-checked). For the ORCHESTRATOR layer the argv is the
    injected orchestrator prefix plus real `start` flags (`--checkout`,
    `--session-role orchestrator`, `--expected-worker-model claude-opus-4-8`).

    Effort is carried as invocation METADATA and an env hint, NEVER as a CLI
    flag: `process.assert_argv_safe` hard-denies every `--effort` form
    (D-004-R159), so the effort pin lives in the invocation the runner applies
    out of band (settings / model selection), not in the command line. The
    safe-checkpoint and handoff references likewise ride as metadata so the
    successor resumes the SAME bounded unit from the safe checkpoint.

    Fail-closed everywhere: a missing worker executable, an argv-safety refusal,
    a runner exception, a not-started/unavailable result, or a runner that echoes
    a different model than the pinned opus id -> `LaunchResult(available=False)`.
    """

    def __init__(self, *, command_runner: CommandRunner, targets: SuccessorLaunchTargets) -> None:
        self._command_runner = command_runner
        self._targets = targets

    def launch(self, request: LaunchRequest) -> LaunchResult:
        try:
            invocation = self._build_invocation(request)
        except Exception as exc:  # argv-safety refusal or a missing target
            return LaunchResult(
                available=False,
                model_id=ALLOWED_SUCCESSOR_MODEL_ID,
                detail=f"could not build a safe opus-4.8 successor invocation: {exc}")

        try:
            outcome = self._command_runner(invocation)
        except Exception as exc:  # a real launcher that raised: fail closed
            return LaunchResult(
                available=False,
                model_id=ALLOWED_SUCCESSOR_MODEL_ID,
                detail=f"the successor command-runner raised ({exc}); failing closed with "
                       f"no claimed launch")

        if not getattr(outcome, "available", False) or not getattr(outcome, "started", False):
            detail = getattr(outcome, "detail", "") or "runner reported the successor did not start"
            return LaunchResult(
                available=False,
                model_id=ALLOWED_SUCCESSOR_MODEL_ID,
                detail=f"opus-4.8 successor not started ({detail})")

        reported_model = getattr(outcome, "model_id", "") or ""
        if reported_model and reported_model != ALLOWED_SUCCESSOR_MODEL_ID:
            return LaunchResult(
                available=False,
                model_id=ALLOWED_SUCCESSOR_MODEL_ID,
                detail=f"runner started {reported_model!r}, not the pinned "
                       f"{ALLOWED_SUCCESSOR_MODEL_ID!r}; failing closed")

        successor_id = getattr(outcome, "successor_id", "") or ""
        if not successor_id:
            return LaunchResult(
                available=False,
                model_id=ALLOWED_SUCCESSOR_MODEL_ID,
                detail="runner reported a start with no successor id; failing closed")

        return LaunchResult(
            available=True,
            successor_id=successor_id,
            model_id=ALLOWED_SUCCESSOR_MODEL_ID,
            detail=(f"launched a {ALLOWED_SUCCESSOR_MODEL_ID}/{ALLOWED_SUCCESSOR_EFFORT} "
                    f"{invocation.layer} successor {successor_id!r}"))

    # -- argv / invocation building -----------------------------------------

    def _build_invocation(self, request: LaunchRequest) -> SuccessorInvocation:
        layer = request.layer
        if layer is TurnoverLayer.WORKER:
            argv = tuple(self._worker_argv())
        else:
            argv = tuple(self._orchestrator_argv())
        env = minimal_env({
            # Effort and role ride as env/metadata, never as a hard-denied CLI
            # flag. They are applied out of band by the launch mechanism.
            "SUPERVISOR_SUCCESSOR_EFFORT": ALLOWED_SUCCESSOR_EFFORT,
            "SUPERVISOR_SESSION_ROLE": layer.value,
        })
        return SuccessorInvocation(
            layer=layer.value,
            argv=argv,
            env=env,
            model_id=ALLOWED_SUCCESSOR_MODEL_ID,
            effort=ALLOWED_SUCCESSOR_EFFORT,
            expected_worker_model=ALLOWED_SUCCESSOR_MODEL_ID,
            task_id=request.task_id,
            event_id=request.event_id,
            handoff_reference=request.handoff_reference,
            safe_checkpoint_id=request.safe_checkpoint_id,
            failed_fable_execution_id=request.failed_fable_execution_id,
        )

    def _worker_argv(self) -> list[str]:
        """The confirmed Claude worker argv, pinned to opus-4.8.

        Reuses the frozen `claude_runner.build_argv` (read-only) so the redispatch
        is the SAME bounded-unit invocation the supervisor already trusts, with
        `--model claude-opus-4-8` and `expected_model` moved to the same id so
        stream verification checks exactly what is launched. The safe-checkpoint /
        handoff resume rides as invocation metadata rather than `--resume`, whose
        capability this increment does not re-probe.
        """
        if not self._targets.claude_executable:
            raise ValueError("no claude executable configured for a worker redispatch")
        config = RunnerConfig(
            executable=self._targets.claude_executable,
            max_turns=self._targets.max_turns,
            timeout_seconds=self._targets.unit_timeout_seconds,
            cwd=self._targets.checkout,
            model=ALLOWED_SUCCESSOR_MODEL_ID,
            expected_model=ALLOWED_SUCCESSOR_MODEL_ID,
        )
        return build_argv(config)

    def _orchestrator_argv(self) -> list[str]:
        """The orchestrator/handoff launch argv, using only real `start` flags.

        The orchestrator model is chosen from the immutable model_chain (which
        lists `claude-opus-4-8`); the opus pin is expressed via
        `--expected-worker-model claude-opus-4-8` and the invocation metadata,
        not a synthesized flag. `assert_argv_safe` refuses any bypass/effort
        token that could slip into the prefix.
        """
        if not self._targets.orchestrator_argv_prefix:
            raise ValueError("no orchestrator argv prefix configured for a handoff launch")
        argv = [
            *self._targets.orchestrator_argv_prefix,
            "--checkout", self._targets.checkout,
            "--session-role", "orchestrator",
            "--expected-worker-model", ALLOWED_SUCCESSOR_MODEL_ID,
        ]
        return assert_argv_safe(argv)


def make_subprocess_command_runner(
    *,
    new_successor_id: Callable[[], str],
    timeout_seconds: float = 60.0,
) -> CommandRunner:
    """The PRODUCTION command-runner seam: launch the invocation as a real
    subprocess via `process.run` (argv array, never a shell).

    Defined for completeness; the tests never call it (they inject a fake so no
    real Claude/Codex process is spawned). It runs the argv under the supervisor's
    bounded, contained `process.run`, treats a clean start as started, and takes
    the successor id from the injected `new_successor_id` source (a real launch is
    fire-and-observe, so the id is minted by the caller, not scraped from output).
    """
    from . import process as _process  # local import: real launcher only

    def _runner(invocation: SuccessorInvocation) -> CommandRunResult:
        result = _process.run(
            list(invocation.argv),
            cwd=None,
            env=dict(invocation.env),
            timeout=timeout_seconds,
        )
        if result.timed_out or result.returncode != 0:
            return CommandRunResult(
                started=False,
                available=not result.timed_out,
                detail=f"successor launch returncode={result.returncode} "
                       f"timed_out={result.timed_out}")
        return CommandRunResult(
            started=True,
            successor_id=new_successor_id(),
            model_id=ALLOWED_SUCCESSOR_MODEL_ID,
            available=True,
            detail="successor process started")

    return _runner
