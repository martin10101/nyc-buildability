#!/usr/bin/env python3
"""Preflight capability probes, including the control-response round trip.

Phase 2 left one honest residual: the Phase 1 behavioural probe captured the
`can_use_tool` control REQUEST payload verbatim and proved a deny round-tripped,
but it did not record the exact bytes of the control RESPONSE wrapper the CLI
accepts. Everything downstream of `claude_runner.build_control_response` was
therefore tested against our own fake, not against the CLI's contract.

`control_response_round_trip` closes that gap and is deliberately opt-in:

* `live=False` (the default, and what `doctor` uses) runs NOTHING. It reports
  `UNVERIFIED` and says exactly what a live run would do.
* `live=True` runs the real canonical executable ONCE, briefly, in a throwaway
  directory, with `--permission-mode manual --permission-prompt-tool stdio
  --max-turns 1`. It asks for one tool call, answers the control request with the
  EXACT bytes `build_control_response` produces, and then checks the CLI's own
  reaction: the wrapper is confirmed only if the CLI accepts the response and
  reports the tool denied WITH OUR MESSAGE. A CLI-side protocol error, a hang, or
  a silently-allowed tool all read as NOT verified.

The probe never writes inside the repository, never runs a repository command,
and bounds itself with a timeout and `--max-turns 1`.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
from typing import Any, Sequence

from .claude_runner import (
    CONTROL_RESPONSE_WRAPPER_VERIFIED,
    RunnerConfig,
    build_argv,
    build_control_response,
    user_message,
)
from .models import to_utc_iso
from .process import assert_argv_safe, minimal_env

VERIFIED = "VERIFIED"
UNVERIFIED = "UNVERIFIED"
FAILED = "FAILED"

#: The deny message the probe sends back. Finding it in the CLI's own tool result
#: is the proof that our wrapper was parsed and honoured.
PROBE_DENY_MESSAGE = "preflight: deterministic broker denied (control-response probe)"

DEFAULT_PROBE_TIMEOUT_SECONDS = 120


@dataclasses.dataclass(frozen=True)
class ProbeResult:
    """What a preflight probe established. `status` is never optimistic."""

    name: str
    status: str
    detail: str
    ran_live: bool = False
    evidence: dict[str, Any] = dataclasses.field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == VERIFIED

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def describe_unverified() -> ProbeResult:
    """The default, no-call answer. Says what a live run would prove."""
    return ProbeResult(
        "control_response_round_trip",
        VERIFIED if CONTROL_RESPONSE_WRAPPER_VERIFIED else UNVERIFIED,
        "no live call was made. The control-response WRAPPER shape is implemented as the "
        "SDK documents it and is exercised against a fake in the test suite, but the exact "
        "bytes the installed CLI accepts have not been observed by this build. Run "
        "`doctor --live` (one bounded run of the canonical executable, one turn, one denied "
        "tool call, in a throwaway directory) to close it.",
        ran_live=False)


def _probe_argv(executable: str, cwd: str) -> list[str]:
    """The exact bounded argv. Built through the SHIPPED adapter, not by hand."""
    config = RunnerConfig(executable=executable, max_turns=1, timeout_seconds=60.0, cwd=cwd)
    return assert_argv_safe(build_argv(config))


def control_response_round_trip(
    executable: str,
    *,
    live: bool = False,
    timeout_seconds: float = DEFAULT_PROBE_TIMEOUT_SECONDS,
    prompt: str = "",
) -> ProbeResult:
    """Verify the control-response wrapper against the installed CLI.

    Returns UNVERIFIED without running anything unless `live=True`.
    """
    if not live:
        return describe_unverified()
    if not executable:
        return ProbeResult("control_response_round_trip", FAILED,
                           "no canonical executable path was supplied", ran_live=False)

    workdir = pathlib.Path(tempfile.mkdtemp(prefix="supervisor_preflight_"))
    target = workdir / "preflight_probe_target.txt"
    instruction = prompt or (
        f"Use the Write tool exactly once to create the file {target.name} with the "
        f"contents PROBE, then stop. Do nothing else.")

    argv = _probe_argv(executable, str(workdir))
    started = time.monotonic()
    events: list[dict[str, Any]] = []
    sent_response: dict[str, Any] | None = None
    request_seen: dict[str, Any] | None = None
    stderr_tail = ""

    try:
        process = subprocess.Popen(  # noqa: S603 - argv array, shell=False, fixed flags
            argv,
            cwd=str(workdir),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=minimal_env(),
        )
    except OSError as exc:
        return ProbeResult("control_response_round_trip", FAILED,
                           f"the canonical executable could not be started: {exc}",
                           ran_live=False, evidence={"argv": argv})

    try:
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(json.dumps(user_message(instruction)) + "\n")
        process.stdin.flush()

        while True:
            if time.monotonic() - started > timeout_seconds:
                process.kill()
                return ProbeResult(
                    "control_response_round_trip", FAILED,
                    f"the probe exceeded its {timeout_seconds}s bound; a wrapper that cannot "
                    f"be confirmed within a bounded run is not confirmed",
                    ran_live=True, evidence={"events": len(events)})
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append(event)
            if event.get("type") == "control_request":
                request = event.get("request") or {}
                if request.get("subtype") == "can_use_tool":
                    request_seen = event
                    sent_response = build_control_response(
                        str(event.get("request_id", "")), "deny",
                        message=PROBE_DENY_MESSAGE)
                    process.stdin.write(json.dumps(sent_response) + "\n")
                    process.stdin.flush()
            if event.get("type") == "result":
                break
        try:
            process.stdin.close()
        except OSError:
            pass
        process.wait(timeout=15)
    except Exception as exc:  # pragma: no cover - defensive around a live process
        process.kill()
        return ProbeResult("control_response_round_trip", FAILED,
                           f"the probe failed with {type(exc).__name__}: {exc}",
                           ran_live=True, evidence={"events": len(events)})
    finally:
        if process.stderr is not None:
            stderr_tail = (process.stderr.read() or "")[-500:]
        for stream in (process.stdin, process.stdout, process.stderr):
            try:
                if stream is not None:
                    stream.close()
            except OSError:
                pass

    file_created = target.exists()
    result_events = [e for e in events if e.get("type") == "result"]
    denials: list[dict[str, Any]] = []
    for event in result_events:
        denials.extend(event.get("permission_denials") or [])
    message_echoed = any(PROBE_DENY_MESSAGE in json.dumps(e) for e in events)
    protocol_error = any(
        e.get("type") == "control_response"
        and (e.get("response") or {}).get("subtype") == "error"
        for e in events)

    evidence = {
        "argv_flags": [a for a in argv[1:]],
        "events": len(events),
        "control_request_seen": request_seen is not None,
        "response_sent": sent_response,
        "permission_denials": len(denials),
        "deny_message_echoed": message_echoed,
        "cli_protocol_error": protocol_error,
        "target_file_created": file_created,
        "returncode": process.returncode,
        "stderr_tail": stderr_tail,
        "probed_at_utc": to_utc_iso(),
    }

    try:
        if target.exists():
            target.unlink()
        for leftover in workdir.iterdir():
            leftover.unlink(missing_ok=True)
        workdir.rmdir()
    except OSError:
        pass

    if request_seen is None:
        return ProbeResult(
            "control_response_round_trip", FAILED,
            "the CLI never emitted a can_use_tool control request, so the wrapper was never "
            "exercised. The adapter's mandatory --permission-mode manual is what makes the "
            "request appear; investigate before trusting any live run.",
            ran_live=True, evidence=evidence)
    if protocol_error:
        return ProbeResult(
            "control_response_round_trip", FAILED,
            "the CLI answered our control response with a protocol error: the wrapper shape "
            "is NOT what the installed CLI accepts.",
            ran_live=True, evidence=evidence)
    if file_created:
        return ProbeResult(
            "control_response_round_trip", FAILED,
            "the tool ran despite our deny: the wrapper was not honoured. Fail closed.",
            ran_live=True, evidence=evidence)
    if denials and message_echoed:
        return ProbeResult(
            "control_response_round_trip", VERIFIED,
            "the installed CLI accepted the exact control_response bytes this build emits, "
            "denied the tool, and echoed our deny message back in permission_denials. The "
            "wrapper shape is confirmed against the live CLI.",
            ran_live=True, evidence=evidence)
    if denials:
        return ProbeResult(
            "control_response_round_trip", UNVERIFIED,
            "the tool was denied and no file was written, but our deny message was not "
            "echoed back, so the denial cannot be attributed to our response rather than to "
            "the CLI's own fail-closed behaviour at stream end.",
            ran_live=True, evidence=evidence)
    return ProbeResult(
        "control_response_round_trip", UNVERIFIED,
        "no tool ran and no denial was recorded; the run did not exercise the wrapper.",
        ran_live=True, evidence=evidence)


# --------------------------------------------------------------------------
# Capability probe records (consumed by recovery + the runner's resume gate)
# --------------------------------------------------------------------------

CAPABILITY_KEY = "cli_capability_probes"


def record_probe(journal: Any, result: ProbeResult, *, executable_identity: str = "") -> None:
    """Persist a probe outcome so later phases can gate on measured facts."""
    probes = dict(journal.get_state(CAPABILITY_KEY, {}) or {})
    probes[result.name] = {
        **result.to_dict(),
        "executable_identity": executable_identity,
        "recorded_at_utc": to_utc_iso(),
    }
    journal.set_state(CAPABILITY_KEY, probes)


def probe_record(journal: Any, name: str) -> dict[str, Any] | None:
    probes = journal.get_state(CAPABILITY_KEY, {}) or {}
    value = probes.get(name) if isinstance(probes, dict) else None
    return value if isinstance(value, dict) else None


def canonical_claude_candidates() -> tuple[str, ...]:
    """Documented candidate locations for the canonical executable (no discovery run)."""
    home = pathlib.Path.home()
    candidates = [
        str(home / ".local" / "bin" / ("claude.exe" if os.name == "nt" else "claude")),
    ]
    override = os.environ.get("SUPERVISOR_CLAUDE_EXECUTABLE", "")
    if override:
        candidates.insert(0, override)
    return tuple(candidates)


def resolve_canonical_claude(candidates: Sequence[str] = ()) -> str:
    """Return the first candidate that exists, or '' - never a PATH search.

    S13.4 forbids following a path supplied by repository text or by a model, and
    a bare PATH lookup is exactly the shadowing risk it warns about, so the
    canonical executable is chosen from an explicit list only.
    """
    for candidate in (candidates or canonical_claude_candidates()):
        if candidate and pathlib.Path(candidate).is_file():
            return candidate
    return ""


def python_executable() -> str:
    """This interpreter, for fake-process test harnesses."""
    return sys.executable
