"""Operator-channel CLI verbs: `graceful-stop` and `ask` (D-024 Phase F,
M0-T094; R027/R034/R036/R085/R086/R087/R104).

Split out of ``cli.py`` under the modularity policy: the command surface file
is grandfathered-oversized, so unit G's two new verbs live here as a focused
module and ``cli.py`` only registers them. The shared runtime-opening and
redacted-emit helpers moved here WITH them (single authority, no duplicate of
the "stdout is a transmission" rule); ``cli.py`` re-imports both under their
established names, so every existing call site is unchanged.

Supervisor-freeze qualifying evidence: D-024-R104 (Phase F).
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Callable, Sequence

from . import refusals
from .audit_log import AuditLog
from .config import ConfigError, load_controller_config, load_model_selection
from .durable_state import DB_FILENAME, DurableJournal, runtime_dir_for
from .operator_ask import (
    DEFAULT_ASK_WINDOW_SECONDS,
    AskError,
    resubmit_ask,
    run_ask,
    show_ask,
)
from .redaction import redact_structure
from .start_gate import emit_refusal
from .stop_intent import clear_graceful_stop, set_graceful_stop

AUDIT_FILENAME = "audit.jsonl"


def open_runtime(args: argparse.Namespace) -> tuple[pathlib.Path,
                                                    DurableJournal, AuditLog]:
    """Open the runtime directory, journal, and audit log for one command."""
    checkout = pathlib.Path(args.checkout).resolve()
    runtime = runtime_dir_for(checkout, base=args.runtime_base)
    journal = DurableJournal(runtime / DB_FILENAME).open()
    audit = AuditLog(runtime / AUDIT_FILENAME)
    return runtime, journal, audit


def emit_payload(args: argparse.Namespace, payload: dict[str, Any],
                 lines: Sequence[str]) -> None:
    """Print a command's result, REDACTED, on stdout.

    C2 (G5 M2): stdout is a TRANSMISSION, so it obeys redaction.py's rule like
    every other. It did not, and M0-T079 routed the raw `git remote get-url`
    result into the payload - so a PAT-bearing remote reached the log.
    """
    if args.json:
        print(json.dumps(redact_structure(payload).value, indent=2, default=str))
    else:
        for line in redact_structure(list(lines)).value:
            print(line)


def cmd_graceful_stop(args: argparse.Namespace) -> int:
    """Durable graceful-stop verb over the accepted unit-F `stop_intent`
    module (M0-T094; R027/R034/R036/R086).

    The intent is journaled BEFORE this command acknowledges anything
    (R036/R086: durable before ack); the loop observes it through the
    controller, never a conversational prompt. Precedence is unit F's:
    emergency > graceful > pause. Only an explicit owner command clears it.
    """
    _, journal, audit = open_runtime(args)
    try:
        if getattr(args, "clear", False):
            record = clear_graceful_stop(journal, owner_command=True, audit=audit)
            cleared = True
        else:
            record = set_graceful_stop(
                journal, reason=args.reason or "operator `graceful-stop`",
                audit=audit)
            cleared = False
    finally:
        journal.close()
    if cleared:
        emit_payload(args, {"command": "graceful-stop", "cleared": True,
                            **record},
                     ["graceful-stop intent cleared by an explicit owner "
                      "command."])
    else:
        emit_payload(args, {"command": "graceful-stop", **record},
                     ["graceful stop recorded durably BEFORE this "
                      "acknowledgment.",
                      "the loop finishes only the smallest safe atomic unit "
                      "already underway, lands it, then stops (unit-F "
                      "stop_intent).",
                      "emergency-stop outranks it; only `graceful-stop "
                      "--clear` clears it."])
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    """Owner question to the read-only Codex supervisor (M0-T094; R085/R087).

    One bounded synchronous window; on timeout a durable request ID (the
    contained process tree is already terminated - no background duplicate).
    `--show` reads a durable record; `--resubmit` re-poses the exact recorded
    question in one new window.
    """
    checkout = pathlib.Path(args.checkout).resolve()
    _, journal, audit = open_runtime(args)
    try:
        if args.show:
            try:
                record = show_ask(journal, args.show)
            except AskError as exc:
                return emit_refusal(args, refusals.refusal(
                    refusals.STALE_STATE, reason_code=exc.code,
                    message=exc.message))
            answered = bool(record.get("answered_at_utc"))
            emit_payload(
                args, {"command": "ask", "shown": record},
                [f"request : {record['ask_id']}  "
                 f"({'answered' if answered else 'open'})",
                 f"asked at: {record['created_at_utc']}",
                 f"question: {record['question']}",
                 *([f"answered: {record['answered_at_utc']}",
                    f"answer  : {record['answer']}"] if answered else
                   ["no answer yet: re-pose it with "
                    f"`ask --resubmit {record['ask_id']}`"])])
            return 0

        missing = [name for name, value in
                   (("--codex-executable", args.codex_executable),
                    ("--config", args.config),
                    ("--model-selection", args.model_selection))
                   if not value]
        if missing:
            return emit_refusal(args, refusals.refusal(
                refusals.STALE_STATE, reason_code="ask_input_missing",
                message=f"ask needs {', '.join(missing)} named explicitly; "
                        f"nothing is discovered from PATH or defaulted into a "
                        f"provider call"))
        try:
            config = load_controller_config(args.config)
            selection = load_model_selection(args.model_selection)
        except ConfigError as exc:
            return emit_refusal(args, refusals.refusal(
                refusals.STALE_STATE, reason_code="ask_config_unreadable",
                message=str(exc)))
        kwargs: dict[str, Any] = dict(
            journal=journal, audit=audit, executable=args.codex_executable,
            checkout=checkout, config=config, selection=selection,
            window_seconds=args.window)
        try:
            if args.resubmit:
                outcome = resubmit_ask(args.resubmit, **kwargs)
            elif args.question:
                outcome = run_ask(args.question, **kwargs)
            else:
                return emit_refusal(args, refusals.refusal(
                    refusals.STALE_STATE, reason_code="no_question",
                    message="ask needs a question (or --show/--resubmit with "
                            "a request id)"))
        except AskError as exc:
            return emit_refusal(args, refusals.refusal(
                refusals.UNSAFE if exc.code in ("identity_mismatch",
                                                "campaign_record_invalid")
                else refusals.STALE_STATE,
                reason_code=exc.code, message=exc.message))
    finally:
        journal.close()

    payload = {"command": "ask", **outcome.to_dict()}
    if outcome.answered:
        lines = [f"answer  : {outcome.answer}"]
        if outcome.confidence_note:
            lines.append(f"grounded: {outcome.confidence_note}")
        if outcome.evidence_refs:
            lines.append(f"evidence: {outcome.evidence_refs}")
        if outcome.redactions:
            lines.append(f"note    : {outcome.redactions} redaction(s)/"
                         f"control-sequence strip(s) were applied")
        emit_payload(args, payload, lines)
        return 0
    if outcome.timed_out:
        emit_payload(
            args, payload,
            [f"no answer within the {args.window:.0f}s window.",
             f"durable request id: {outcome.request_id}",
             "the ask process tree was terminated - nothing keeps running "
             "in the background.",
             f"read it later with `ask --show {outcome.request_id}` or "
             f"re-pose it with `ask --resubmit {outcome.request_id}`."])
        return 0
    return emit_refusal(args, refusals.refusal(
        refusals.STALE_STATE,
        reason_code=outcome.error_code or "ask_failed",
        message=outcome.error_message or "the ask produced no usable answer"))


def register_operator_verbs(
        sub: Any, add_common: Callable[[argparse.ArgumentParser], None]) -> None:
    """Register `graceful-stop` and `ask` on the existing command surface
    (R034: no parallel CLI)."""
    graceful = sub.add_parser(
        "graceful-stop",
        help="record the durable graceful-stop intent: finish only the "
             "smallest safe atomic unit already underway, land it, then stop "
             "(live)")
    add_common(graceful)
    graceful.add_argument("--reason", default="",
                          help="why the owner asked to stop; recorded durably")
    graceful.add_argument("--clear", action="store_true",
                          help="explicit owner command clearing the "
                               "graceful-stop intent")
    graceful.set_defaults(func=cmd_graceful_stop)

    ask = sub.add_parser(
        "ask",
        help="ask the read-only Codex supervisor a bounded question about "
             "the campaign state; a timeout returns a durable request id "
             "(live)")
    add_common(ask)
    ask.add_argument("question", nargs="?", default="",
                     help="the bounded owner question (quote it)")
    ask.add_argument("--codex-executable", default=None,
                     help="explicit path to the Codex executable; never a "
                          "PATH search")
    ask.add_argument("--config", default=None,
                     help="path to the immutable config.toml")
    ask.add_argument("--model-selection", default=None,
                     help="path to the runtime model_selection.toml")
    ask.add_argument("--window", type=float,
                     default=DEFAULT_ASK_WINDOW_SECONDS,
                     help="the short synchronous answer window, in seconds; "
                          "past it the question becomes a durable request id")
    ask.add_argument("--show", default="",
                     help="print the durable record for an operator ask "
                          "request id (no provider call)")
    ask.add_argument("--resubmit", default="",
                     help="re-pose the exact recorded question for this "
                          "request id in one new bounded window; never a "
                          "background duplicate")
    ask.set_defaults(func=cmd_ask)
