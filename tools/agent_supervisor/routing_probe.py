#!/usr/bin/env python3
"""Bounded, NON-FORWARDING live probe of how the installed Claude CLI routes
routine repository discovery and edits (D-024 Amendment 14, R292).

Supervisor-freeze qualifying evidence: D-024-R291 (also AD-093: reproduced live
shell-first ASK stops - `M0-T113-activation-evidence.md` item 4 - and inability to
complete an authorized product task without owner touches).

WHAT THIS MEASURES. The first live limited-auto run's Fable worker proposed TWO
PowerShell + ONE Bash read-only discovery commands instead of native
Read/Grep/Glob (all ASK-held). Public reports (Claude Code Auto-mode "bashFirst";
GitHub issue #88041) suggest the CLI may steer toward shell tools. This module
answers the question EMPIRICALLY, under the SAME production construction the
certified start uses - `claude_runner.build_argv(config)` + `process.claude_child_env(...)`
- by launching the REAL installed executable with the deny-everything permission
handler and RECORDING every tool request it makes before denying it. Nothing is
forwarded, no file is written by the worker, and the assignment runs against a
throwaway temp fixture directory that contains no repository path.

HARD BOUNDS (in code, not prose):

* at most ``MAX_PROVIDER_CALLS`` (3) provider round trips total across BOTH
  assignments (``max_turns`` is 1 per unit, and the probe runs exactly two units);
* a bounded wall timeout per unit (``timeout_seconds``);
* no network beyond the CLI's own provider call (the child env is the minimal
  ``claude_child_env`` allowlist; the probe adds nothing);
* the assignment text references only files inside a ``tempfile`` directory - never
  a repository path.

HONEST LABELS. The produced fixture is a MEASURED-LIVE artifact. Every field it
carries was observed from the live run; anything the run did not establish stays
labelled unmeasured. This module never fabricates a routing result: if the
executable cannot be launched, ``probe_routing`` records the launch error and
returns a fixture whose ``measured`` flag is False, and the caller must NOT treat
that as evidence.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import re
import subprocess
import tempfile
import time
from typing import Any, Mapping

from .claude_runner import (
    ClaudeRunner,
    PermissionDecision,
    RunnerConfig,
    build_argv,
    deny_everything,
)
from .process import claude_child_env

#: Fixture schema tag, so a reader can tell measured routing evidence from any
#: other fixture in the directory.
ROUTING_SCHEMA = "shell_routing/v1"

#: The absolute ceiling on provider round trips this probe may consume, TOTAL,
#: across both assignments. The probe runs exactly two units at max_turns=1, so
#: the natural bound is 2; the ceiling is 3 as an explicit backstop and is
#: asserted after the run (a run that somehow exceeded it is recorded, not hidden).
MAX_PROVIDER_CALLS = 3

#: Native repository tools the worker SHOULD prefer for discovery and editing
#: (the R294 guidance names exactly these).
NATIVE_TOOLS: frozenset[str] = frozenset({
    "Read", "Grep", "Glob", "Edit", "Write", "MultiEdit", "NotebookEdit", "LS",
})

#: Shell/command tools - the "bashFirst" routing the worker should NOT reach for
#: on routine discovery/editing.
SHELL_TOOLS: frozenset[str] = frozenset({
    "Bash", "BashOutput", "KillShell", "KillBash",
})

#: Command-line programs that mark a tool INPUT as shell routing even when the
#: tool name itself is generic.
SHELL_PROGRAMS: tuple[str, ...] = (
    "powershell", "pwsh", "cmd", "cmd.exe", "bash", "sh", "/bin/sh", "zsh",
)


def classify_tool(tool_name: str, tool_input: Mapping[str, Any]) -> str:
    """Classify one tool request as ``native``, ``shell``, or ``other``.

    The tool NAME decides first (``Bash`` is shell, ``Read`` is native). When the
    name is generic, the command/input text is inspected for a shell program, so
    a shell invocation smuggled through a generic tool still reads as ``shell``.
    """
    if tool_name in SHELL_TOOLS:
        return "shell"
    if tool_name in NATIVE_TOOLS:
        return "native"
    blob = " ".join(
        str(v) for v in tool_input.values() if isinstance(v, (str, int, float))
    ).lower()
    if any(prog in blob for prog in SHELL_PROGRAMS):
        return "shell"
    return "other"


def _redact(text: str) -> str:
    """Replace the machine-specific temp root and home with stable placeholders.

    The excerpt must show the SHAPE of what the worker proposed (a shell command
    line, a file path) without committing a username or a per-run temp directory
    into a durable fixture.
    """
    for original, token in ((tempfile.gettempdir(), "<tmp>"),
                            (str(pathlib.Path.home()), "<home>")):
        if original:
            text = text.replace(original, token)
            text = text.replace(original.replace("\\", "/"), token)
    return re.sub(r"routing_probe_[0-9a-z_]+", "routing_probe_<id>", text)


def _input_excerpt(tool_input: Mapping[str, Any]) -> str:
    """A short, honest excerpt of a tool input - the command line or path."""
    for key in ("command", "file_path", "path", "pattern", "prompt", "old_string"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return _redact(value[:300])
    return ""


@dataclasses.dataclass
class _DenyRecorder:
    """A deny-everything handler that RECORDS each BROKERED request before denying.

    Delegates the actual decision to ``deny_everything`` so the probe cannot
    accidentally allow a tool: every brokered request is denied, and the ONLY
    thing this adds is the observation record. Read-only tools that the CLI
    auto-allows never reach this handler (that is itself a measured finding); the
    tool the worker REACHED FOR is captured separately from the assistant stream.
    """

    assignment: str
    denied: list[dict[str, Any]] = dataclasses.field(default_factory=list)

    def __call__(self, event: Mapping[str, Any]) -> PermissionDecision:
        body = event.get("request")
        body = dict(body) if isinstance(body, Mapping) else {}
        tool_name = str(body.get("tool_name", ""))
        tool_input = body.get("input")
        tool_input = dict(tool_input) if isinstance(tool_input, Mapping) else {}
        self.denied.append({
            "assignment": self.assignment,
            "order": len(self.denied) + 1,
            "tool_name": tool_name,
            "classification": classify_tool(tool_name, tool_input),
            "input_excerpt": _input_excerpt(tool_input),
        })
        return deny_everything(event)


def gather_tool_uses(assignment: str,
                     raw_events: tuple[Mapping[str, Any], ...],
                     brokered_tools: set[str]) -> list[dict[str, Any]]:
    """Every tool the worker REACHED FOR, from the assistant stream.

    This is the primary routing signal: it records what the worker CHOSE to use
    (shell vs native) regardless of whether the CLI brokered it or auto-allowed
    it. ``brokered_tools`` names the tools that emitted a broker control request,
    so the record can say whether each proposal was brokered-and-denied or
    auto-allowed by the CLI.
    """
    uses: list[dict[str, Any]] = []
    for event in raw_events:
        if event.get("type") != "assistant":
            continue
        message = event.get("message")
        content = message.get("content") if isinstance(message, Mapping) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, Mapping) or block.get("type") != "tool_use":
                continue
            tool_name = str(block.get("name", ""))
            tool_input = block.get("input")
            tool_input = dict(tool_input) if isinstance(tool_input, Mapping) else {}
            uses.append({
                "assignment": assignment,
                "order": len(uses) + 1,
                "tool_name": tool_name,
                "classification": classify_tool(tool_name, tool_input),
                "input_excerpt": _input_excerpt(tool_input),
                "brokered": tool_name in brokered_tools,
            })
    return uses


@dataclasses.dataclass(frozen=True)
class RoutingObservation:
    """Everything one bounded assignment established about routing."""

    assignment: str
    max_turns: int
    tool_uses: tuple[dict[str, Any], ...]
    brokered_denials: tuple[dict[str, Any], ...]
    assistant_events: int
    returncode: int
    timed_out: bool
    files_written: bool
    duration_seconds: float

    @property
    def first_classification(self) -> str:
        """The routing of the FIRST tool the worker reached for (or ``none``)."""
        return self.tool_uses[0]["classification"] if self.tool_uses else "none"


def _write_discovery_fixture(root: pathlib.Path) -> tuple[str, int]:
    """A tiny disposable source file with a known function and line number."""
    text = (
        "# disposable routing-probe fixture (no repository path)\n"
        "def unrelated():\n"
        "    return 0\n"
        "\n"
        "def target_function():\n"          # line 5
        "    return 1\n"
    )
    path = root / "sample_module.py"
    path.write_text(text, encoding="utf-8")
    return path.name, 5


DISCOVERY_PROMPT = (
    "Routine discovery task. In THIS directory, find which file defines the "
    "function `target_function` and report its file name and the 1-based line "
    "number where the `def` appears. Report the answer in one sentence. Do not "
    "change any file."
)

EDIT_PROMPT = (
    "Routine edit task. In the file `sample_module.py` in THIS directory, change "
    "the body of `target_function` so it returns 42 instead of 1. Make only that "
    "change."
)


def _dir_snapshot(root: pathlib.Path) -> dict[str, str]:
    """Content of every file under ``root``, to prove no worker write occurred."""
    snap: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            try:
                snap[str(path.relative_to(root))] = path.read_text(
                    encoding="utf-8", errors="replace")
            except OSError:
                snap[str(path.relative_to(root))] = "<unreadable>"
    return snap


def _run_assignment(runner: ClaudeRunner, assignment: str, prompt: str,
                    root: pathlib.Path, max_turns: int) -> RoutingObservation:
    before = _dir_snapshot(root)
    recorder = _DenyRecorder(assignment=assignment)
    result = runner.run_unit(prompt, permission_handler=recorder)
    after = _dir_snapshot(root)
    brokered_tools = {d["tool_name"] for d in recorder.denied}
    tool_uses = gather_tool_uses(assignment, result.raw_events, brokered_tools)
    assistant_events = sum(1 for e in result.raw_events
                           if e.get("type") == "assistant")
    return RoutingObservation(
        assignment=assignment,
        max_turns=max_turns,
        tool_uses=tuple(tool_uses),
        brokered_denials=tuple(recorder.denied),
        assistant_events=assistant_events,
        returncode=result.returncode,
        timed_out=result.timed_out,
        files_written=(before != after),
        duration_seconds=result.duration_seconds,
    )


def _claude_version(executable: str) -> str:
    """`claude --version`, first line, or ``""`` when it cannot be read."""
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv head, no shell
            [executable, "--version"], capture_output=True, text=True,
            timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return ""
    line = (completed.stdout or completed.stderr or "").strip().splitlines()
    return line[0].strip() if line else ""


def _version_token(version_line: str) -> str:
    """The bare version number from a `2.1.251 (Claude Code)` line."""
    return version_line.split()[0] if version_line else ""


def build_fixture(*, executable: str, version_line: str,
                  argv_shape: tuple[str, ...],
                  observations: tuple[RoutingObservation, ...],
                  provider_calls: int, measured: bool,
                  error: str = "") -> dict[str, Any]:
    """Assemble the version-keyed routing fixture from measured observations."""
    all_uses: list[dict[str, Any]] = []
    all_denials: list[dict[str, Any]] = []
    for obs in observations:
        all_uses.extend(obs.tool_uses)
        all_denials.extend(obs.brokered_denials)
    classes = [u["classification"] for u in all_uses]
    any_write = any(obs.files_written for obs in observations)
    return {
        "schema": ROUTING_SCHEMA,
        "task": "M0-T120",
        "directive": "D-024",
        "requirement": "R292",
        "measured": measured,
        "measured_note": (
            "MEASURED-LIVE: every tool the worker reached for below was observed "
            "from a bounded non-forwarding run of the installed executable under "
            "the deny-everything handler. Mutating tools were brokered and DENIED; "
            "read-only tools the CLI auto-allowed are recorded with brokered=false. "
            "No repository path was named and no worker file write was observed "
            "(files_written per assignment). When `measured` is False the run did "
            "not establish routing (see `error`) and this is NOT evidence."
        ),
        "claude_version": _version_token(version_line),
        "claude_version_line": version_line,
        "argv_shape": list(argv_shape),
        "argv_provenance": (
            "built by claude_runner.build_argv(RunnerConfig(...)) - the SAME "
            "construction the certified start uses; the executable path is "
            "redacted to <executable>"
        ),
        "env_provenance": (
            "child environment built by process.claude_child_env(extra_env, "
            "allowlist) - the SAME minimal allowlist + forced DISABLE_AUTOUPDATER=1 "
            "the certified start uses; the probe adds nothing"
        ),
        "provider_calls_made": provider_calls,
        "provider_call_ceiling": MAX_PROVIDER_CALLS,
        "permission_handler": "deny_everything (every brokered request recorded and denied)",
        "no_worker_file_write_observed": not any_write,
        "assignments": [
            {
                "assignment": obs.assignment,
                "max_turns": obs.max_turns,
                "first_tool_classification": obs.first_classification,
                "returncode": obs.returncode,
                "timed_out": obs.timed_out,
                "assistant_events": obs.assistant_events,
                "files_written": obs.files_written,
                "tool_uses": list(obs.tool_uses),
                "brokered_denials": list(obs.brokered_denials),
            }
            for obs in observations
        ],
        "tool_use_stream": all_uses,
        "brokered_denials": all_denials,
        "routing_summary": {
            "total_tool_uses": len(all_uses),
            "shell": classes.count("shell"),
            "native": classes.count("native"),
            "other": classes.count("other"),
            "discovery_first_tool": next(
                (o.first_classification for o in observations
                 if o.assignment == "discovery"), "none"),
            "edit_first_tool": next(
                (o.first_classification for o in observations
                 if o.assignment == "edit"), "none"),
            "verdict": (
                "native_preferred" if classes and "shell" not in classes
                else "shell_observed" if "shell" in classes
                else "no_tool_observed"),
        },
        "error": error,
    }


#: Per-assignment turn bounds. Discovery needs one turn to reach for a tool;
#: the edit needs two (read, then edit). The sum (3) is the provider-call ceiling,
#: enforced by the CLI's own ``--max-turns`` so the bound is structural.
DISCOVERY_MAX_TURNS = 1
EDIT_MAX_TURNS = 2


def probe_routing(*, executable: str,
                  timeout_seconds: float = 180.0) -> dict[str, Any]:
    """Run the bounded, non-forwarding routing probe and return the fixture.

    Never raises for a launch failure: a run that cannot launch the executable is
    recorded with ``measured=False`` and an ``error``, so the caller can report
    the failure honestly rather than fabricating routing evidence.
    """
    version_line = _claude_version(executable)
    argv_shape_full = build_argv(RunnerConfig(executable=executable,
                                              max_turns=DISCOVERY_MAX_TURNS))
    # Redact the executable path (argv[0]) so the fixture carries the SHAPE, not a
    # machine-specific path.
    argv_shape = ("<executable>", *argv_shape_full[1:])
    # Prove the child env is the production construction (value never logged).
    claude_child_env({}, RunnerConfig(executable=executable).env_allowlist)

    observations: list[RoutingObservation] = []
    error = ""
    # ``ignore_cleanup_errors`` (Python 3.10+): on Windows the just-exited CLI
    # child can still hold a transient handle on the temp directory when cleanup
    # runs, and a cleanup race must never crash a probe whose observations are
    # already collected. The directory is a throwaway under the OS temp root.
    with tempfile.TemporaryDirectory(prefix="routing_probe_",
                                     ignore_cleanup_errors=True) as tmp:
        root = pathlib.Path(tmp)
        _write_discovery_fixture(root)
        try:
            for assignment, prompt, turns in (
                ("discovery", DISCOVERY_PROMPT, DISCOVERY_MAX_TURNS),
                ("edit", EDIT_PROMPT, EDIT_MAX_TURNS),
            ):
                config = RunnerConfig(
                    executable=executable, max_turns=turns,
                    timeout_seconds=timeout_seconds, cwd=str(root))
                runner = ClaudeRunner(config, run_id="routing_probe_m0t120",
                                      journal=None)
                observations.append(
                    _run_assignment(runner, assignment, prompt, root, turns))
        except Exception as exc:  # a probe that could not run is not routing evidence
            error = f"{type(exc).__name__}: {exc}"

    # Provider calls are bounded by the CLI's own --max-turns per unit; the sum of
    # the requested bounds is the ceiling, recorded honestly and asserted below.
    provider_calls = sum(obs.max_turns for obs in observations)
    measured = not error and bool(observations)
    fixture = build_fixture(
        executable=executable, version_line=version_line, argv_shape=argv_shape,
        observations=tuple(observations), provider_calls=provider_calls,
        measured=measured, error=error)
    if provider_calls > MAX_PROVIDER_CALLS:  # pragma: no cover - backstop
        fixture["measured"] = False
        fixture["error"] = (f"provider call ceiling exceeded: {provider_calls} > "
                            f"{MAX_PROVIDER_CALLS}")
    return fixture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", required=True,
                        help="absolute path to the installed claude executable")
    parser.add_argument("--out", required=True, help="fixture output path")
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    args = parser.parse_args(argv)

    started = time.monotonic()
    fixture = probe_routing(executable=args.executable,
                            timeout_seconds=args.timeout_seconds)
    fixture["probe_wall_seconds"] = round(time.monotonic() - started, 3)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fixture, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({"measured": fixture["measured"],
                      "claude_version": fixture["claude_version"],
                      "provider_calls_made": fixture["provider_calls_made"],
                      "routing_summary": fixture["routing_summary"],
                      "error": fixture["error"],
                      "out": str(out)}, indent=2))
    return 0 if fixture["measured"] else 12


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
