#!/usr/bin/env python3
"""The Claude worker adapter (D-007 S8.1-S8.4), CLI subprocess per the Phase 0 decision.

Phase 0 chose the CLI over the Agent SDK and Phase 1's behavioural probes
CONFIRMED the decision on claude 2.1.220. The confirmed invocation is:

    claude -p --input-format stream-json --output-format stream-json --verbose
           --max-turns <bound> --permission-mode manual --permission-prompt-tool stdio

Three probe findings are load-bearing here and are encoded as refusals, not as
comments:

1. `--permission-mode manual` is MANDATORY. Under the default (`auto`) the CLI
   permits writes and emits no control request at all, so the broker would be
   silently bypassed. `build_argv()` refuses any other permission mode.
2. `--permission-prompt-tool stdio` routes each permission decision to the stdio
   control channel as a `can_use_tool` control request carrying the complete tool
   input. With stdin at EOF the CLI fails CLOSED ("Tool permission request
   failed"), which is exactly the S8.4 requirement that a request unable to reach
   the broker is denied.
3. `permission_suggestions` may offer `{"type":"setMode","mode":"acceptEdits"}`.
   That is the "always allow" S8.4 forbids; `broker.py` records it as rejected
   and this module never sends it back.

HONEST UNCERTAINTY (read before a live run). The Phase 1 probe report records the
control REQUEST payload verbatim and records that a deterministic deny
round-tripped, but it does not record the exact bytes of the control RESPONSE
wrapper. `build_control_response()` therefore implements the SDK-documented
shape - `{"type":"control_response","response":{"subtype":"success",
"request_id":X,"response":{"behavior":...}}}` - and `doctor` reports the wrapper
as UNVERIFIED against the live CLI. A preflight round-trip probe must confirm it
before any live worker run; the fake-executable tests here prove the loop, not
the CLI contract.

Everything Claude emits - narrative, summaries, command output, checkpoint text -
is untrusted data. This module never derives an action from it.
"""
from __future__ import annotations

import dataclasses
import json
import re
import subprocess
import threading
import time
import uuid
from typing import Any, Callable, Iterator, Mapping, Sequence

from .models import ClaudeCheckpoint, RecordError, digest_of, to_utc_iso
from .policy import neutralize_untrusted
from .process import (
    DEFAULT_ENV_ALLOWLIST,
    ProcessContainer,
    assert_argv_safe,
    executable_identity,
    minimal_env,
    terminate_process_tree,
)

#: The exact confirmed base invocation, in order. Kept as data so a test can
#: assert the shape rather than trusting prose.
CONFIRMED_BASE_ARGS: tuple[str, ...] = (
    "-p",
    "--input-format", "stream-json",
    "--output-format", "stream-json",
    "--verbose",
)

REQUIRED_PERMISSION_MODE = "manual"
REQUIRED_PERMISSION_PROMPT_TOOL = "stdio"

#: Flags that would resume "the most recent session" instead of an exact one.
#: S8.2 forbids them for unattended work.
FORBIDDEN_SESSION_FLAGS: frozenset[str] = frozenset({"--continue", "-c", "--last"})

#: Recorded so `doctor` can state the uncertainty plainly.
CONTROL_RESPONSE_WRAPPER_VERIFIED = False


class RunnerError(Exception):
    """The worker adapter refused to run, or the run could not be trusted."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class CheckpointError(RunnerError):
    """Output was missing, invalid, truncated, or conflicting.

    S8.3: invalid, truncated, or nonconforming output is NEVER forwarded as
    success.
    """


# --------------------------------------------------------------------------
# Configuration and argv
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class RunnerConfig:
    """One bounded Claude unit's invocation parameters."""

    executable: str
    max_turns: int = 12
    timeout_seconds: float = 900.0
    cwd: str = ""
    model: str = ""
    permission_mode: str = REQUIRED_PERMISSION_MODE
    permission_prompt_tool: str = REQUIRED_PERMISSION_PROMPT_TOOL
    resume_session_id: str = ""
    resume_capability_verified: bool = False
    env_allowlist: tuple[str, ...] = DEFAULT_ENV_ALLOWLIST
    extra_env: Mapping[str, str] = dataclasses.field(default_factory=dict)
    #: Phase 4: the Job Object is the DEFAULT container on Windows. Setting this
    #: False is an explicit, recorded downgrade to the taskkill fallback; it is
    #: never selected implicitly by a default, a config parse error, or a model.
    use_job_object: bool = True


def build_argv(config: RunnerConfig) -> list[str]:
    """Build the exact confirmed argv. Refuses every unsafe shape.

    `--resume <session-id>` is emitted only when the caller has recorded that the
    capability was verified against the installed binary. Phase 0/1 verified
    `--max-turns` and the stdio control protocol behaviourally; exact-session
    resume was NOT among the verified probes, so it fails closed here rather than
    being assumed.
    """
    if config.permission_mode != REQUIRED_PERMISSION_MODE:
        raise RunnerError(
            "permission_mode_required",
            f"--permission-mode must be {REQUIRED_PERMISSION_MODE!r}: under the default "
            f"'auto' the CLI permits writes and emits no control request, silently "
            f"bypassing the approval broker (Phase 1 probe B2)")
    if config.permission_prompt_tool != REQUIRED_PERMISSION_PROMPT_TOOL:
        raise RunnerError(
            "permission_prompt_tool_required",
            f"--permission-prompt-tool must be {REQUIRED_PERMISSION_PROMPT_TOOL!r} so the "
            f"broker receives each can_use_tool control request")
    if not isinstance(config.max_turns, int) or config.max_turns < 1:
        raise RunnerError("bad_max_turns", "--max-turns must be a positive integer bound")

    argv: list[str] = [config.executable, *CONFIRMED_BASE_ARGS,
                       "--max-turns", str(config.max_turns),
                       "--permission-mode", config.permission_mode,
                       "--permission-prompt-tool", config.permission_prompt_tool]
    if config.model:
        argv += ["--model", config.model]
    if config.resume_session_id:
        if not config.resume_capability_verified:
            raise RunnerError(
                "resume_capability_unverified",
                "exact-session resume was not behaviourally verified on this binary; a "
                "preflight capability probe must confirm `--resume <session-id>` before "
                "unattended use. Never fall back to a 'most recent session' lookup (S8.2)")
        argv += ["--resume", config.resume_session_id]

    for flag in FORBIDDEN_SESSION_FLAGS:
        if flag in argv:
            raise RunnerError("most_recent_session_forbidden",
                              f"{flag} resumes 'the most recent session'; unattended work "
                              f"resumes only the exact recorded session (S8.2)")
    return assert_argv_safe(argv)


# --------------------------------------------------------------------------
# Session identity (S8.2)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class SessionIdentity:
    """Everything S8.2 requires the supervisor to record about a worker session."""

    run_id: str
    claude_session_id: str
    task_id: str
    canonical_repo_path: str
    starting_sha: str
    branch: str
    worktree: str
    checkpoint_sequence: int = 0
    last_accepted_decision_digest: str = ""
    recorded_at_utc: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def digest(self) -> str:
        return digest_of(self.to_dict())


SESSION_KEY = "claude_session_identity"


def record_session(journal: Any, identity: SessionIdentity) -> SessionIdentity:
    """Persist the session identity. New sessions get new ids; resume is exact."""
    stamped = dataclasses.replace(identity, recorded_at_utc=to_utc_iso())
    journal.set_state(SESSION_KEY, stamped.to_dict())
    return stamped


def recorded_session(journal: Any) -> SessionIdentity | None:
    data = journal.get_state(SESSION_KEY)
    if not isinstance(data, dict):
        return None
    known = {f.name for f in dataclasses.fields(SessionIdentity)}
    return SessionIdentity(**{k: v for k, v in data.items() if k in known})


# --------------------------------------------------------------------------
# Stream parsing (S8.3 / S15 "parsing and processes")
# --------------------------------------------------------------------------


@dataclasses.dataclass
class StreamStats:
    lines: int = 0
    events: int = 0
    blank_lines: int = 0
    noise_lines: int = 0
    malformed_lines: int = 0
    duplicate_events: int = 0


class ClaudeStreamParser:
    """Incremental parser for the CLI's own stream-json events.

    This is NOT the supervisor's cross-CLI envelope protocol (that is
    `protocol.py`, used between the supervisor and its own messages). The CLI
    emits its own event shapes, so the tolerance rules live here: fragmented
    lines, blank lines, a BOM, CRLF, non-JSON stderr bleed on stdout, duplicate
    event ids, and a truncated final object all have to be safe.
    """

    def __init__(self, *, max_line_bytes: int = 4_194_304) -> None:
        self.stats = StreamStats()
        self.noise: list[str] = []
        self._buffer = ""
        self._max_line_bytes = max_line_bytes
        self._seen_ids: set[str] = set()

    def feed(self, chunk: str) -> Iterator[dict[str, Any]]:
        self._buffer += chunk
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            yield from self._handle(line)

    def close(self) -> Iterator[dict[str, Any]]:
        if self._buffer:
            leftover, self._buffer = self._buffer, ""
            yield from self._handle(leftover, final=True)

    def _handle(self, line: str, *, final: bool = False) -> Iterator[dict[str, Any]]:
        self.stats.lines += 1
        # `chr(0xFEFF)` rather than a literal BOM in the source: a literal here is
        # invisible in review and easy to lose in a re-encoding.
        text = line.lstrip(chr(0xFEFF)).strip("\r").strip()
        if not text:
            self.stats.blank_lines += 1
            return
        if len(text.encode("utf-8", "replace")) > self._max_line_bytes:
            self.stats.malformed_lines += 1
            return
        if not text.startswith("{"):
            self.stats.noise_lines += 1
            if len(self.noise) < 100:
                self.noise.append(text[:500])
            return
        try:
            event = json.loads(text)
        except json.JSONDecodeError:
            # A JSON-looking line that does not parse is malformed - never noise.
            # A truncated FINAL object lands here too, which is why the run result
            # carries `malformed_lines` and is never reported as success.
            self.stats.malformed_lines += 1
            return
        if not isinstance(event, dict):
            self.stats.malformed_lines += 1
            return
        identifier = event.get("uuid") or event.get("message_id")
        if isinstance(identifier, str) and identifier:
            if identifier in self._seen_ids:
                self.stats.duplicate_events += 1
                return
            self._seen_ids.add(identifier)
        self.stats.events += 1
        yield event


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _json_candidates(text: str) -> list[dict[str, Any]]:
    """Every JSON object embedded in a block of model text."""
    found: list[dict[str, Any]] = []
    for body in _FENCE.findall(text):
        try:
            value = json.loads(body.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            found.append(value)
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            pass
        else:
            if isinstance(value, dict):
                found.append(value)
    return found


def _event_text(event: Mapping[str, Any]) -> str:
    """Best-effort extraction of the human-readable text an event carries."""
    parts: list[str] = []
    result = event.get("result")
    if isinstance(result, str):
        parts.append(result)
    message = event.get("message")
    if isinstance(message, Mapping):
        content = message.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, Mapping) and isinstance(block.get("text"), str):
                    parts.append(block["text"])
    return "\n".join(parts)


def extract_checkpoint(events: Sequence[Mapping[str, Any]]) -> ClaudeCheckpoint:
    """Find and validate the ONE structured checkpoint (S8.3).

    Accepts the checkpoint as a bare event object, inside a `result` payload, or
    fenced inside assistant text. Duplicate delivery of an identical checkpoint is
    tolerated; the same checkpoint id with different content is a conflict and is
    refused rather than being resolved by preference.
    """
    candidates: list[dict[str, Any]] = []
    for event in events:
        if "checkpoint_id" in event and "schema_version" in event:
            candidates.append(dict(event))
        text = _event_text(event)
        if text:
            candidates.extend(_json_candidates(text))

    shaped = [c for c in candidates if "checkpoint_id" in c and "schema_version" in c]
    if not shaped:
        raise CheckpointError(
            "missing_checkpoint",
            "the run produced no structured checkpoint; a missing result is never "
            "interpreted as success (S14)")

    by_id: dict[str, dict[str, Any]] = {}
    for candidate in shaped:
        key = str(candidate.get("checkpoint_id"))
        previous = by_id.get(key)
        if previous is not None and digest_of(previous) != digest_of(candidate):
            raise CheckpointError(
                "conflicting_duplicate_checkpoint",
                f"checkpoint id {key!r} was delivered twice with different content; the "
                f"supervisor refuses to choose between them")
        by_id[key] = candidate

    chosen = shaped[-1]
    try:
        checkpoint = ClaudeCheckpoint.from_dict(chosen)
        checkpoint.validate()
    except RecordError as exc:
        raise CheckpointError("invalid_checkpoint",
                              f"the checkpoint does not conform: {exc}") from exc
    return checkpoint


# --------------------------------------------------------------------------
# The control protocol (S8.4)
# --------------------------------------------------------------------------


def build_control_response(
    request_id: str,
    behavior: str,
    *,
    message: str = "",
    updated_input: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one control_response for a `can_use_tool` control_request.

    Shape per the SDK's documented control protocol. See the module docstring for
    the honest verification status of this wrapper.
    """
    if behavior not in ("allow", "deny"):
        raise RunnerError("bad_behavior", f"{behavior!r} is not allow/deny")
    payload: dict[str, Any] = {"behavior": behavior}
    if behavior == "allow" and updated_input is not None:
        payload["updatedInput"] = dict(updated_input)
    if message:
        payload["message"] = message
    return {"type": "control_response",
            "response": {"subtype": "success", "request_id": request_id,
                         "response": payload}}


def build_control_error(request_id: str, error: str) -> dict[str, Any]:
    """Answer an unsupported control request. Nothing is ever left unanswered."""
    return {"type": "control_response",
            "response": {"subtype": "error", "request_id": request_id, "error": error}}


def user_message(text: str) -> dict[str, Any]:
    """One stream-json user turn."""
    return {"type": "user",
            "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


@dataclasses.dataclass(frozen=True)
class PermissionDecision:
    """What the broker decided about one control request, for the run record."""

    request_id: str
    tool_name: str
    behavior: str
    reason_code: str
    reason: str
    tool_use_id: str = ""
    rejected_suggestions: tuple[str, ...] = ()


#: The callback the runner asks for a decision. It receives the parsed
#: `can_use_tool` request payload and returns a `PermissionDecision`.
PermissionHandler = Callable[[Mapping[str, Any]], PermissionDecision]


def deny_everything(request: Mapping[str, Any]) -> PermissionDecision:
    """The default handler: deny. A runner without a broker never allows."""
    return PermissionDecision(
        request_id=str(request.get("request_id", "")),
        tool_name=str((request.get("request") or {}).get("tool_name", "")),
        behavior="deny",
        reason_code="no_broker",
        reason="no approval broker is attached to this run; requests are denied, never "
               "allowed and never left hanging (S8.4)")


# --------------------------------------------------------------------------
# Running a bounded unit
# --------------------------------------------------------------------------


@dataclasses.dataclass
class RunResult:
    """Everything the supervisor learned from one bounded unit."""

    argv: tuple[str, ...]
    returncode: int
    duration_seconds: float
    session_id: str = ""
    events: int = 0
    stats: StreamStats = dataclasses.field(default_factory=StreamStats)
    permission_decisions: tuple[PermissionDecision, ...] = ()
    checkpoint: ClaudeCheckpoint | None = None
    checkpoint_error: str = ""
    timed_out: bool = False
    cancelled: bool = False
    tree_terminated: bool = False
    containment: str = ""
    containment_fallback_reason: str = ""
    stderr_tail: str = ""
    injection_labels: tuple[str, ...] = ()
    raw_events: tuple[dict[str, Any], ...] = ()

    @property
    def ok(self) -> bool:
        """A run is OK only with a valid checkpoint, a clean exit, and no timeout.

        A nonzero exit, a timeout, a cancellation, or a malformed final object is
        never interpreted as success (S14).
        """
        return (self.checkpoint is not None and not self.checkpoint_error
                and self.returncode == 0 and not self.timed_out and not self.cancelled)


class ClaudeRunner:
    """Owns the Claude subprocess. Never attaches to an interactive terminal."""

    def __init__(self, config: RunnerConfig, *, audit: Any = None,
                 run_id: str = "") -> None:
        self.config = config
        self.audit = audit
        self.run_id = run_id or f"run_{uuid.uuid4().hex[:12]}"

    def executable_identity(self) -> dict[str, Any]:
        identity = executable_identity(self.config.executable, name="claude")
        return dataclasses.asdict(identity)

    def run_unit(
        self,
        prompt: str,
        *,
        permission_handler: PermissionHandler | None = None,
        cancel_event: threading.Event | None = None,
        extra_turns: Sequence[str] = (),
    ) -> RunResult:
        """Run one bounded unit, brokering every permission request.

        The prompt is written as a stream-json user turn on stdin; every
        `can_use_tool` control request is answered from the handler; the process
        tree is terminated on timeout or cancellation.
        """
        argv = build_argv(self.config)
        handler = permission_handler or deny_everything
        env = minimal_env(dict(self.config.extra_env), self.config.env_allowlist)
        parser = ClaudeStreamParser()
        decisions: list[PermissionDecision] = []
        events: list[dict[str, Any]] = []
        stderr_chunks: list[str] = []
        session_id = ""
        timed_out = threading.Event()
        cancelled = threading.Event()
        tree_terminated = False

        started = time.monotonic()
        # Phase 4: the worker is launched INSIDE the default container (a
        # kill-on-close Job Object on Windows). Nothing it spawns can outlive the
        # container, and the containment actually achieved is recorded.
        container = ProcessContainer(prefer_job_object=self.config.use_job_object)
        process = subprocess.Popen(  # noqa: S603 - argv array, shell=False
            argv, shell=False,
            cwd=self.config.cwd or None, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", bufsize=1)
        container.adopt(process.pid)

        def drain_stderr() -> None:
            assert process.stderr is not None
            for line in process.stderr:
                stderr_chunks.append(line)
                if len(stderr_chunks) > 500:
                    del stderr_chunks[:100]

        def watchdog() -> None:
            deadline = started + self.config.timeout_seconds
            while process.poll() is None:
                if cancel_event is not None and cancel_event.is_set():
                    cancelled.set()
                    break
                if time.monotonic() >= deadline:
                    timed_out.set()
                    break
                time.sleep(0.05)
            if timed_out.is_set() or cancelled.is_set():
                try:
                    container.terminate_all()
                except Exception:  # pragma: no cover - defensive
                    try:
                        terminate_process_tree(process.pid)
                    except Exception:
                        pass

        stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
        watch_thread = threading.Thread(target=watchdog, daemon=True)
        stderr_thread.start()
        watch_thread.start()

        def write(payload: Mapping[str, Any]) -> None:
            assert process.stdin is not None
            try:
                process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
                process.stdin.flush()
            except (BrokenPipeError, ValueError, OSError):
                # Early pipe closure: the CLI already fails closed on its side.
                pass

        try:
            write(user_message(prompt))
            for turn in extra_turns:
                write(user_message(turn))

            assert process.stdout is not None
            for chunk in process.stdout:
                for event in parser.feed(chunk):
                    events.append(event)
                    kind = event.get("type")
                    if kind == "system" and event.get("subtype") == "init":
                        session_id = str(event.get("session_id", "")) or session_id
                    elif kind == "control_request":
                        decision = self._answer_control_request(event, handler, write)
                        if decision is not None:
                            decisions.append(decision)
            for event in parser.close():
                events.append(event)
        finally:
            try:
                if process.stdin is not None and not process.stdin.closed:
                    process.stdin.close()
            except Exception:  # pragma: no cover - defensive
                pass
            process.wait()
            watch_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            for pipe in (process.stdout, process.stderr):
                try:
                    if pipe is not None and not pipe.closed:
                        pipe.close()
                except Exception:  # pragma: no cover - defensive
                    pass
            if timed_out.is_set() or cancelled.is_set():
                tree_terminated = True
            containment_report = container.report()
            container.close()

        duration = time.monotonic() - started
        checkpoint: ClaudeCheckpoint | None = None
        checkpoint_error = ""
        try:
            checkpoint = extract_checkpoint(events)
        except CheckpointError as exc:
            checkpoint_error = f"{exc.code}: {exc.message}"
        if parser.stats.malformed_lines and checkpoint is None and not checkpoint_error:
            checkpoint_error = "malformed_output: the stream contained malformed JSON"

        narrative = "\n".join(_event_text(event) for event in events)
        untrusted = neutralize_untrusted(narrative)

        result = RunResult(
            argv=tuple(argv),
            returncode=process.returncode if process.returncode is not None else -1,
            duration_seconds=duration,
            session_id=session_id,
            events=len(events),
            stats=parser.stats,
            permission_decisions=tuple(decisions),
            checkpoint=checkpoint,
            checkpoint_error=checkpoint_error,
            timed_out=timed_out.is_set(),
            cancelled=cancelled.is_set(),
            tree_terminated=tree_terminated,
            containment=containment_report.kind,
            containment_fallback_reason=containment_report.fallback_reason,
            stderr_tail="".join(stderr_chunks)[-4000:],
            injection_labels=untrusted.labels,
            raw_events=tuple(events),
        )
        self._audit_run(result)
        return result

    def _answer_control_request(
        self,
        event: Mapping[str, Any],
        handler: PermissionHandler,
        write: Callable[[Mapping[str, Any]], None],
    ) -> PermissionDecision | None:
        """Answer exactly one control request. Nothing is left unanswered."""
        request_id = str(event.get("request_id", ""))
        body = event.get("request")
        if not isinstance(body, Mapping):
            write(build_control_error(request_id, "malformed control request"))
            return None
        subtype = str(body.get("subtype", ""))
        if subtype != "can_use_tool":
            write(build_control_error(
                request_id, f"unsupported control request subtype {subtype!r}"))
            return None
        try:
            decision = handler(event)
        except Exception as exc:  # pragma: no cover - defensive
            decision = PermissionDecision(
                request_id=request_id,
                tool_name=str(body.get("tool_name", "")),
                behavior="deny",
                reason_code="handler_error",
                reason=f"the approval handler failed ({exc}); failing closed")
        write(build_control_response(request_id, decision.behavior,
                                     message=decision.reason))
        return decision

    def _audit_run(self, result: RunResult) -> None:
        if self.audit is None:
            return
        self.audit.append(
            "claude_unit_completed",
            run_id=self.run_id,
            checkpoint_id=result.checkpoint.checkpoint_id if result.checkpoint else "",
            output_digest=digest_of(result.checkpoint.to_dict()) if result.checkpoint else "",
            error_category=result.checkpoint_error.split(":")[0]
            if result.checkpoint_error else "",
            detail={
                "returncode": result.returncode,
                "timed_out": result.timed_out,
                "cancelled": result.cancelled,
                "events": result.events,
                "noise_lines": result.stats.noise_lines,
                "malformed_lines": result.stats.malformed_lines,
                "duplicate_events": result.stats.duplicate_events,
                "permission_decisions": [d.behavior for d in result.permission_decisions],
                "injection_labels": list(result.injection_labels),
                "session_id_recorded": bool(result.session_id),
            })


# --------------------------------------------------------------------------
# Broker wiring
# --------------------------------------------------------------------------


def broker_permission_handler(
    broker: Any,
    *,
    authority: Any,
    head_sha: str = "",
    origin_main_sha: str = "",
    session_id_getter: Callable[[], str] | None = None,
    executable_identity_data: Mapping[str, Any] | None = None,
) -> PermissionHandler:
    """Wire the stdio control channel to the approval broker.

    The returned handler translates a `can_use_tool` request into a
    `ProposedAction` plus a fully bound `ApprovalRequest`, asks the broker, and
    converts the outcome into allow/deny. `DEFER_TO_OWNER` becomes a DENY for
    THIS call - the request stays queued for the owner and resumes as its own
    exact call later; the worker is never left waiting on a human.
    """
    from .broker import APPROVE_ONCE, action_from_tool_request, build_request

    def handle(event: Mapping[str, Any]) -> PermissionDecision:
        request_id = str(event.get("request_id", ""))
        body = dict(event.get("request") or {})
        tool_name = str(body.get("tool_name", ""))
        tool_input = body.get("input")
        tool_input = dict(tool_input) if isinstance(tool_input, Mapping) else {}
        suggestions = body.get("permission_suggestions")
        suggestions = [dict(s) for s in suggestions] if isinstance(suggestions, list) else []
        stated_reason = str(body.get("description", ""))

        action = action_from_tool_request(tool_name, tool_input,
                                          request_id=request_id,
                                          stated_reason=stated_reason)
        request = build_request(
            tool_name=tool_name,
            tool_input=tool_input,
            authority=authority,
            argv=action.argv,
            executable_identity=executable_identity_data or {},
            cwd=authority.worktree,
            target_paths=action.target_paths,
            head_sha=head_sha,
            origin_main_sha=origin_main_sha,
            session_id=session_id_getter() if session_id_getter else "",
            tool_use_id=str(body.get("tool_use_id", "")),
            permission_suggestions=suggestions,
            stated_reason=stated_reason,
            request_id=request_id or "",
        )
        outcome = broker.evaluate_request(request, action)
        behavior = "allow" if outcome.behavior == APPROVE_ONCE else "deny"
        return PermissionDecision(
            request_id=request_id,
            tool_name=tool_name,
            behavior=behavior,
            reason_code=outcome.reason_code,
            reason=outcome.reason,
            tool_use_id=str(body.get("tool_use_id", "")),
            rejected_suggestions=outcome.rejected_suggestions)

    return handle
