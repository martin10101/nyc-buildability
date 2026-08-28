#!/usr/bin/env python3
"""Pre-model /loop-* interception (D-024 Phase F, M0-T094; R084/R087/R088).

Intercepts the EXACT owner commands /loop-start /loop-status /loop-tasks
/loop-ask /loop-pause /loop-resume /loop-stop /loop-emergency-stop BEFORE the
model sees them, runs the external supervisor CLI directly, and returns the
bounded result through the hook's user-visible channel - so the command and
its output never enter the Fable transcript or context.

Feature detection (R084/R149, decided by the committed installed-version
fixture ``tools/agent_supervisor/fixtures/loop_interception_detection_*.json``):

* ``UserPromptSubmit`` is the SELECTED path on the installed version - its
  payload is measured-live and its documented block contract (`decision:
  "block"` + `reason`) erases the prompt from model context and displays the
  reason to the user.
* ``UserPromptExpansion`` is present in the installed event catalog but its
  RESPONSE contract is unproven here, so a matching prompt passes through
  unchanged on that event (the Submit registration still intercepts it);
  never a faked expansion (R088).

Security (R087): exact command-token matching (never substring), argv arrays
only (no shell), repository-root + campaign-marker identity validation before
any execution, bounded stdin/stdout, redaction + terminal-escape stripping of
everything displayed (reusing tools/agent_supervisor redaction), a hard
subprocess timeout with kill (no zombie duplicate), and fail-closed behavior:
a matched control that cannot run safely is BLOCKED with a visible reason
naming the exact second-terminal command - never half-executed, never
silently swallowed.

This file is NEW in unit G; the pre-existing guard hooks are untouched.
Supervisor-freeze qualifying evidence: D-024-R104 (Phase F).
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess  # noqa: S404 - argv arrays only, shell=False, bounded
import sys

MAX_STDIN_BYTES = 262_144
MAX_REASON_CHARS = 4_000
#: Env-overridable so the deterministic timeout test does not wait 45 s;
#: production leaves it unset.
SUBPROCESS_TIMEOUT_SECONDS = float(
    os.environ.get("LOOP_HOOK_TIMEOUT_S", "") or 45.0)

#: Exact command-token match (R087: never substring). Anchored: the prompt IS
#: the command - "tell me about /loop-status", "loop-status", and
#: "/loop-statuses" all pass through untouched.
_COMMAND = re.compile(
    r"^/(loop-(?:start|status|tasks|ask|pause|resume|stop|emergency-stop))"
    r"(?:\s+([\s\S]*))?$")

#: verb -> supervisor argv tail. /loop-stop maps to the graceful landing-rule
#: stop (R034 "graceful stop after next safe checkpoint"); the immediate hard
#: `stop` and `emergency-stop` stay available and are named in the output.
_VERB_ARGV: dict[str, list[str]] = {
    "loop-start": ["start"],
    "loop-status": ["status"],
    "loop-pause": ["pause"],
    "loop-resume": ["resume"],
    "loop-stop": ["graceful-stop"],
    "loop-emergency-stop": ["emergency-stop"],
}

_DETECTION_FIXTURE_GLOB = "loop_interception_detection_*.json"


def _repo_root(payload: dict) -> pathlib.Path | None:
    """The campaign repository root, identity-validated (R087) - or None."""
    candidate = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ""
    if not candidate:
        return None
    root = pathlib.Path(candidate)
    markers = ("CLAUDE.md",
               pathlib.Path("tools") / "project_control.py",
               pathlib.Path("tools") / "agent_supervisor" / "cli.py")
    if all((root / m).exists() for m in markers):
        return root
    return None


def _selected_event(root: pathlib.Path) -> str:
    """Which hook event performs interception, per the committed detection
    fixture. Unreadable/ambiguous -> the measured UserPromptSubmit path."""
    fixtures = sorted((root / "tools" / "agent_supervisor" / "fixtures")
                      .glob(_DETECTION_FIXTURE_GLOB))
    for path in reversed(fixtures):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            selected = record.get("selected_event", "")
            if selected in ("UserPromptSubmit", "UserPromptExpansion"):
                return selected
        except (OSError, json.JSONDecodeError, AttributeError):
            continue
    return "UserPromptSubmit"


def _bound_for_display(root: pathlib.Path, text: str) -> str:
    """Redact + strip terminal escapes + bound, reusing the supervisor's own
    tested redaction. If the import fails the text is NOT shown raw."""
    try:
        sys.path.insert(0, str(root))
        from tools.agent_supervisor.operator_ask import bound_answer
        return bound_answer(text)[:MAX_REASON_CHARS]
    except Exception:  # noqa: BLE001 - fail closed: never display unredacted
        return ("[output withheld: the redaction module could not be loaded; "
                "run the command in a second terminal to read it]")


def _block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason[:MAX_REASON_CHARS]},
                     ensure_ascii=False))


def _second_terminal(verb: str, argv_tail: list[str]) -> str:
    shown = " ".join(argv_tail) or verb
    return (f"second-terminal path: python -m tools.agent_supervisor {shown} "
            f"(from the repository root)")


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
        if len(raw) > MAX_STDIN_BYTES:
            return 0  # oversized payload: never guess, never block prompts
        payload = json.loads(raw.decode("utf-8", errors="replace"))
        if not isinstance(payload, dict):
            return 0
    except Exception:  # noqa: BLE001 - malformed payload: pass through
        return 0

    prompt = payload.get("prompt")
    if not isinstance(prompt, str):
        return 0
    match = _COMMAND.match(prompt.strip())
    if match is None:
        return 0  # not one of the exact commands: untouched (R084)

    verb = match.group(1)
    argument = (match.group(2) or "").strip()
    event = str(payload.get("hook_event_name", ""))

    root = _repo_root(payload)
    if root is None:
        # A matched CONTROL outside the campaign repository fails closed with
        # a visible reason (R087) - never executed, never sent to the model.
        _block(f"/{verb} refused: this session's project directory is not the "
               f"campaign repository root (identity markers missing). Run the "
               f"supervisor CLI from the repository root in a second terminal.")
        return 0

    if event != "UserPromptSubmit" or _selected_event(root) != "UserPromptSubmit":
        # UserPromptExpansion (or any other event): response contract unproven
        # on the installed version - pass through unchanged; the selected
        # event's registration performs the interception. Never fake it (R088).
        return 0

    ignored_argument = ""
    if verb == "loop-tasks":
        argv = [sys.executable, "-m",
                "tools.agent_supervisor.campaign_continuity", "--status"]
        ignored_argument = argument
    elif verb == "loop-ask":
        if not argument:
            _block("/loop-ask needs a question: /loop-ask <question>")
            return 0
        exe = os.environ.get("SUPERVISOR_CODEX_EXECUTABLE", "")
        cfg = os.environ.get("SUPERVISOR_CONFIG", "")
        sel = os.environ.get("SUPERVISOR_MODEL_SELECTION", "")
        if not (exe and cfg and sel):
            # No configured provider inputs -> fail closed, name the exact
            # command (nothing is discovered from PATH; R087).
            _block("/loop-ask refused: SUPERVISOR_CODEX_EXECUTABLE, "
                   "SUPERVISOR_CONFIG, and SUPERVISOR_MODEL_SELECTION are not "
                   "all set for this session. Second-terminal path: python -m "
                   "tools.agent_supervisor ask \"<question>\" "
                   "--codex-executable <path> --config <path> "
                   "--model-selection <path>")
            return 0
        # The question is ONE argv element after an explicit "--"
        # end-of-options separator (G5 ADVISORY-2 hardening): a question
        # beginning with "-" is still the question, never an option -
        # metacharacters, quotes, Unicode, and newlines are data, never
        # shell (R087). The CLI's own sanitize_question applies its bounds
        # and redaction.
        argv = [sys.executable, "-m", "tools.agent_supervisor", "ask",
                "--codex-executable", exe, "--config", cfg,
                "--model-selection", sel, "--", argument]
    elif verb == "loop-stop" and argument:
        # The optional [reason] rides into the durable graceful-stop record.
        argv = [sys.executable, "-m", "tools.agent_supervisor",
                "graceful-stop", "--reason", argument]
    else:
        argv = [sys.executable, "-m", "tools.agent_supervisor",
                *_VERB_ARGV[verb]]
        # A CONTROL with an unexpected argument still executes (failing open
        # to the model would forfeit the control, R087) - but the dropped
        # argument is named, never silently swallowed.
        ignored_argument = argument

    try:
        result = subprocess.run(  # noqa: S603 - argv array, shell=False
            argv, cwd=str(root), shell=False, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=SUBPROCESS_TIMEOUT_SECONDS)
        output = (result.stdout or "") + \
            (("\n" + result.stderr) if result.stderr else "")
        body = _bound_for_display(root, output.strip() or
                                  f"(exit {result.returncode}, no output)")
        header = f"/{verb} -> supervisor (exit {result.returncode})"
        if verb == "loop-stop":
            header += " [graceful landing-rule stop; immediate: `stop`, " \
                      "hardest: /loop-emergency-stop]"
        if ignored_argument:
            header += (f"\n[note: this command takes no argument; "
                       f"{len(ignored_argument)} character(s) were ignored]")
        _block(f"{header}\n{body}")
    except subprocess.TimeoutExpired:
        # subprocess.run KILLS the child on timeout; nothing keeps running.
        _block(f"/{verb} timed out after {SUBPROCESS_TIMEOUT_SECONDS:.0f}s; "
               f"the process was killed (no background duplicate). "
               f"{_second_terminal(verb, _VERB_ARGV.get(verb, []))}")
    except Exception as exc:  # noqa: BLE001 - fail closed with a visible reason
        _block(f"/{verb} failed before execution completed: "
               f"{type(exc).__name__}. No control was half-executed. "
               f"{_second_terminal(verb, _VERB_ARGV.get(verb, []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
