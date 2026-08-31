"""Command-document validation tooth: owner-presented commands vs the live contract.

D-024 Amendment 22 defects D1/D14/D15/D17 (M0-T125 register). The live 12-turn
journey's PRECEDING failure was a presented ``start`` command (M0-T124 §4 item 2)
that the parser ACCEPTED but the launch seam REFUSED (``cwd_primary_checkout``,
exit 11) because it carried no ``--worktree`` while the packet declared one. It
escaped 2,889 passing tests and five certifications because certification is
non-live and NO test parses the presented documents (register D17, VERIFIED by
G4). D14 adds that ``start`` requires nothing at the argparse layer and its
silent defaults (no ``--repo`` => primary-checkout leak D2, no ``--branch`` =>
unpinned probe, no ``--max-cycles`` => single cycle => D10) degrade quietly.

This module is the mechanical tooth the register prescribes: extract every
presented supervisor command from the certification docs and the runbook, and
dry-run each against the LIVE contract —

The register phrased extraction as "every ``!``-prefixed command", assuming the
certification-report convention; the LIVING operator runbook
(``docs/CONTROLLER_UPDATE_RUNBOOK.md``) instead presents commands inside fenced
```` ```powershell ```` blocks with PowerShell backtick continuation, and mixes
in non-supervisor shell lines (``Set-Location``, ``Copy-Item`` ...). So the
extractor handles BOTH conventions (``!``-prefixed lines AND fenced code blocks)
and scopes to lines that INVOKE the supervisor (``agent_supervisor``), joining
backtick/backslash continuations into one logical command. This deviation from
the register's literal ``!`` wording preserves its INTENT — mechanically
validate every presented supervisor command against the live contract — and is
recorded in the M0-T126 design record.

- ``cli.build_parser()`` must accept it (catches drift between a presented flag
  and the parser);
- for ``start``, the five load-bearing flags ``--checkout --repo --branch
  --worktree --max-cycles`` must be present EXPLICITLY (no silent default), and
  ``start_gate.dispatch_inputs_missing`` must return empty (the six named
  dispatch inputs);
- when the command names a resolvable ``--task-packet`` that declares an
  isolated worktree, ``launch_seam.evaluate_packet_worktree_binding`` must NOT
  refuse the bound worktree (catches the exact live defect).

Any drift, in either direction, is a validation FAILURE. The removal-sensitive
property (register): deleting ``--worktree`` (or any pinned flag) from a
presented start command, or removing this tooth, must fail. ``tools/
supervisor_command_doc_check.py`` wires this into CI.

Pure and offline: it imports the parser and gates by value and never launches,
never contacts a provider, never opens the live journal (R374/R375 intact).

Supervisor-freeze qualifying evidence: D-024-R372, M0-T125 D1/D14/D15/D17.
"""
from __future__ import annotations

import argparse
import contextlib
import dataclasses
import io
import shlex
from collections.abc import Sequence

#: The load-bearing flags an owner-presented ``start`` command must pin
#: EXPLICITLY (register D1/D14; the reproduced defect). Each silent default is a
#: named hazard: --checkout (journal addressed = cwd), --repo (primary-checkout
#: evidence/review leak D2), --branch (unpinned probe), --worktree (the live
#: exit-11 refusal), --max-cycles (single-cycle feeds D10).
REQUIRED_START_FLAGS: tuple[str, ...] = (
    "--checkout", "--repo", "--branch", "--worktree", "--max-cycles")

#: The verb whose presented shape carries the pinned-flag requirement.
START_VERB = "start"

#: A presented command is a SUPERVISOR command (and thus validated) only when it
#: actually INVOKES the package CLI — the module form ``-m tools.agent_supervisor``
#: or a direct ``cli.py`` / ``__main__.py`` script path. A mere PATH mention of
#: ``agent_supervisor`` (robocopy of the package tree, ``git diff`` over it, a
#: ``$src = "...\agent_supervisor"`` assignment) is NOT an invocation and is
#: ignored, so ordinary shell lines in a runbook code block are not mis-flagged.
SUPERVISOR_INVOCATION_MARKERS: tuple[str, ...] = (
    "-m tools.agent_supervisor",
    "tools.agent_supervisor.cli",
    "agent_supervisor/cli.py",
    "agent_supervisor\\cli.py",
    "agent_supervisor/__main__.py",
    "agent_supervisor\\__main__.py",
)

#: Fenced code-block languages whose bodies may carry presented commands.
_FENCE_MARKERS: tuple[str, ...] = ("```", "~~~")


class CommandDocError(ValueError):
    """Typed error for command-document validation (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class PresentedCommand:
    """One ``!``-prefixed command extracted from a document, with provenance."""

    source: str
    line_number: int
    raw: str


@dataclasses.dataclass(frozen=True)
class CommandVerdict:
    """The validation verdict for one presented command."""

    command: PresentedCommand
    verb: str
    ok: bool
    code: str
    message: str


def _is_supervisor_command(body: str) -> bool:
    if not any(marker in body for marker in SUPERVISOR_INVOCATION_MARKERS):
        return False
    # A command carrying an angle-bracket placeholder (`<path>`, `<recorded
    # manifest>`) is a TEMPLATE, not a concrete presented command; validating a
    # template against argparse is meaningless, so it is not a presented command.
    return not _has_placeholder(body)


def _has_placeholder(body: str) -> bool:
    """True when the command carries a ``<...>`` template placeholder."""
    start = body.find("<")
    return start != -1 and body.find(">", start + 1) != -1


def _join_continuations(lines: list[str], index: int) -> tuple[str, int]:
    """Join PowerShell backtick / shell backslash continuations from ``index``.

    Returns ``(logical_command, last_index_consumed)``. A line ending in a bare
    backtick (PowerShell) or a backslash (POSIX) continues onto the next line.
    """
    body = lines[index].strip()
    while body.endswith(("`", "\\")) and index + 1 < len(lines):
        body = body[:-1].rstrip() + " "
        index += 1
        body += lines[index].strip()
    return body.strip(), index


def extract_presented_commands(
    text: str, *, source: str = "", require_supervisor: bool = True,
) -> list[PresentedCommand]:
    """Extract every presented SUPERVISOR command from a document.

    Handles both conventions: ``!``-prefixed lines (certification reports) and
    commands inside fenced ```` ``` ```` / ``~~~`` code blocks (the runbook),
    joining backtick/backslash continuations into one logical command. When
    ``require_supervisor`` is True (the default), only commands that invoke the
    package are returned — non-supervisor shell lines in a code block are
    ignored. Provenance (source + 1-based start line) is kept for CI output.
    """
    commands: list[PresentedCommand] = []
    lines = text.splitlines()
    index = 0
    in_fence = False
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.lstrip()
        if stripped.startswith(_FENCE_MARKERS):
            in_fence = not in_fence
            index += 1
            continue
        start_line = index + 1  # 1-based
        if stripped.startswith("!"):
            body = stripped[1:].strip()
            cursor = index
            while body.endswith(("`", "\\")) and cursor + 1 < len(lines):
                body = body[:-1].rstrip() + " "
                cursor += 1
                body += lines[cursor].strip()
            index = cursor
            if not require_supervisor or _is_supervisor_command(body):
                commands.append(PresentedCommand(
                    source=source, line_number=start_line, raw=body.strip()))
            index += 1
            continue
        if in_fence and _is_supervisor_command(stripped):
            body, index = _join_continuations(lines, index)
            commands.append(PresentedCommand(
                source=source, line_number=start_line, raw=body.strip()))
            index += 1
            continue
        index += 1
    return commands


def extract_bang_commands(text: str, *, source: str = "") -> list[PresentedCommand]:
    """Back-compat thin wrapper: presented supervisor commands (both conventions)."""
    return extract_presented_commands(text, source=source)


def _verb_choices(parser: argparse.ArgumentParser) -> frozenset[str]:
    """The subcommand names ``build_parser`` accepts."""
    choices: set[str] = set()
    for action in parser._actions:  # noqa: SLF001 - argparse has no public API for this
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            choices.update(action.choices)
    return frozenset(choices)


def subcommand_tokens(
    raw: str, parser: argparse.ArgumentParser,
) -> tuple[str, list[str]]:
    """Split a presented command into (verb, argv-after-verb).

    Drops the interpreter/module prefix (``python -m tools.agent_supervisor``,
    ``python tools/agent_supervisor/cli.py``, ``supervisor``, ...) by finding the
    FIRST token that is a known verb. Returns ``("", [])`` when no known verb is
    present (an unrecognized command, itself a drift signal the caller reports).
    Tokenized with ``shlex(posix=False)`` so Windows backslash paths survive; the
    surrounding quotes are then stripped.
    """
    verbs = _verb_choices(parser)
    raw = _strip_trailing_comment(raw)
    try:
        tokens = shlex.split(raw, posix=False)
    except ValueError as exc:
        raise CommandDocError(
            "untokenizable", f"could not tokenize presented command {raw!r}: {exc}"
        ) from exc
    cleaned = [_strip_quotes(tok) for tok in tokens]
    for position, token in enumerate(cleaned):
        if token in verbs:
            return token, cleaned[position + 1:]
    return "", []


def _strip_trailing_comment(cmd: str) -> str:
    """Drop a trailing ``#`` shell/PowerShell comment that begins a token.

    A ``#`` is a comment start only when it is outside quotes AND at the start of
    the command or preceded by whitespace, so a ``#`` inside a quoted path is
    preserved. Everything from that point to end-of-line is dropped.
    """
    out: list[str] = []
    quote = ""
    for ch in cmd:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in {'"', "'"}:
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (not out or out[-1].isspace()):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _strip_quotes(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {'"', "'"}:
        return token[1:-1]
    return token


def _parse_quietly(
    parser: argparse.ArgumentParser, argv: Sequence[str],
) -> tuple[argparse.Namespace | None, str]:
    """Run ``parser.parse_args`` capturing argparse's SystemExit/stderr.

    Returns ``(namespace, "")`` on acceptance or ``(None, error_text)`` on any
    argparse rejection — never lets argparse's ``SystemExit`` escape.
    """
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            namespace = parser.parse_args(list(argv))
        return namespace, ""
    except SystemExit:
        return None, err.getvalue().strip() or "argparse rejected the command"


def validate_command(
    command: PresentedCommand,
    parser: argparse.ArgumentParser,
) -> CommandVerdict:
    """Validate one presented command against the live parser + start contract.

    - unknown verb -> FAIL (``unknown_verb``);
    - argparse rejects -> FAIL (``parser_rejected``);
    - ``start`` missing any pinned flag -> FAIL (``missing_pinned_flag``);
    - ``start`` with a non-empty ``dispatch_inputs_missing`` -> FAIL
      (``dispatch_inputs_missing``).

    Non-``start`` verbs pass on parser acceptance alone (their contract is the
    parser). ``start`` additionally carries the pinned-flag + dispatch-input
    tooth. The worktree-binding dry-run is a separate call
    (``check_worktree_binding``) the CI entry runs when the packet is resolvable,
    so this function stays offline and packet-free.
    """
    verb, argv = subcommand_tokens(command.raw, parser)
    if not verb:
        return CommandVerdict(
            command=command, verb="", ok=False, code="unknown_verb",
            message=("no known supervisor verb found in the presented command; "
                     "the command drifted from the CLI contract or the doc "
                     "presents a command the parser no longer accepts"))
    namespace, error = _parse_quietly(parser, [verb, *argv])
    if namespace is None:
        return CommandVerdict(
            command=command, verb=verb, ok=False, code="parser_rejected",
            message=f"build_parser() rejected the presented command: {error}")
    if verb == START_VERB:
        present = set(argv)
        missing = [flag for flag in REQUIRED_START_FLAGS if flag not in present]
        if missing:
            return CommandVerdict(
                command=command, verb=verb, ok=False, code="missing_pinned_flag",
                message=(f"presented start command omits load-bearing flag(s) "
                         f"{missing}; each silent default is a named hazard "
                         f"(register D1/D14/D2/D10). Pin every one of "
                         f"{list(REQUIRED_START_FLAGS)} explicitly"))
        # Lazy import: start_gate imports the package; keeping it here means the
        # extractor half of this module stays importable standalone.
        from tools.agent_supervisor import start_gate
        still_missing = start_gate.dispatch_inputs_missing(namespace)
        if still_missing:
            return CommandVerdict(
                command=command, verb=verb, ok=False, code="dispatch_inputs_missing",
                message=(f"presented start command is missing dispatch inputs "
                         f"{still_missing}; the six named inputs must all be "
                         f"present for an unattended start (D14)"))
    return CommandVerdict(
        command=command, verb=verb, ok=True, code="ok",
        message=f"presented {verb!r} command matches the live contract")


def check_worktree_binding(
    namespace: argparse.Namespace, packet_worktree: str, primary_checkout: str = "",
) -> CommandVerdict | None:
    """Dry-run the presented start's worktree binding against the seam gate.

    When the named packet declares an isolated worktree, the presented
    ``--worktree`` (bound cwd) must NOT be refused by
    ``launch_seam.evaluate_packet_worktree_binding`` — the exact live-defect
    check. Returns a FAIL verdict on refusal, or None when there is nothing to
    check (no packet worktree). Kept separate so the core validator stays
    offline; the CI entry calls this only when it resolves the packet.
    """
    if not packet_worktree:
        return None
    from tools.agent_supervisor import launch_seam
    bound = getattr(namespace, "worktree", "") or ""
    decision = launch_seam.evaluate_packet_worktree_binding(
        bound, packet_worktree, primary_checkout)
    if decision is not None and not decision.ok:
        cmd = PresentedCommand(source="", line_number=0, raw="")
        return CommandVerdict(
            command=cmd, verb=START_VERB, ok=False, code="worktree_binding_refused",
            message=(f"the presented --worktree {bound!r} is refused against the "
                     f"packet worktree {packet_worktree!r}: {decision.message}"))
    return None


def validate_document(
    text: str, parser: argparse.ArgumentParser, *, source: str = "",
) -> list[CommandVerdict]:
    """Extract and validate every presented command in one document."""
    return [validate_command(cmd, parser)
            for cmd in extract_bang_commands(text, source=source)]
