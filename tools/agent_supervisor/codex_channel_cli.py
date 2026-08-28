"""CLI verbs for the Codex discussion channel (D-024 Amendment 8, M0-T110).

``codex new|continue|show|promote|close`` registered on the EXISTING command
surface (no parallel CLI - the R034 precedent ``operator_channel_cli``
established). This module is wiring + display only; every rule lives in
``codex_channel``. Output rides ``operator_channel_cli.emit_payload`` so
stdout stays a redacted transmission (C2).

Supervisor-freeze qualifying evidence: D-024-R232/R234.
"""
from __future__ import annotations

import argparse
import pathlib
from typing import Any, Callable

from . import refusals
from .codex_channel import (
    DEFAULT_TURN_WINDOW_SECONDS,
    ChannelError,
    TurnOutcome,
    close_thread,
    continue_thread,
    new_thread,
    promote_message,
    show_thread,
)
from .config import ConfigError, load_controller_config, load_model_selection
from .operator_channel_cli import emit_payload, open_runtime
from .start_gate import emit_refusal

#: ChannelError codes that mean "identity/tamper", mapped to the UNSAFE exit
#: exactly like the ask verb maps them.
_UNSAFE_CODES = ("identity_mismatch", "campaign_record_invalid")


def _refuse(args: argparse.Namespace, exc: ChannelError) -> int:
    return emit_refusal(args, refusals.refusal(
        refusals.UNSAFE if exc.code in _UNSAFE_CODES else refusals.STALE_STATE,
        reason_code=exc.code, message=exc.message))


def _provider_kwargs(args: argparse.Namespace,
                     journal: Any, audit: Any) -> dict[str, Any] | int:
    """The provider-call inputs, named explicitly - or a refusal exit code."""
    missing = [name for name, value in
               (("--codex-executable", args.codex_executable),
                ("--config", args.config),
                ("--model-selection", args.model_selection))
               if not value]
    if missing:
        return emit_refusal(args, refusals.refusal(
            refusals.STALE_STATE, reason_code="codex_input_missing",
            message=f"codex {args.codex_verb} needs {', '.join(missing)} "
                    f"named explicitly; nothing is discovered from PATH or "
                    f"defaulted into a provider call"))
    try:
        config = load_controller_config(args.config)
        selection = load_model_selection(args.model_selection)
    except ConfigError as exc:
        return emit_refusal(args, refusals.refusal(
            refusals.STALE_STATE, reason_code="codex_config_unreadable",
            message=str(exc)))
    return dict(journal=journal, audit=audit,
                executable=args.codex_executable,
                checkout=pathlib.Path(args.checkout).resolve(),
                config=config, selection=selection,
                window_seconds=args.window)


def _emit_turn(args: argparse.Namespace, outcome: TurnOutcome) -> int:
    payload = {"command": f"codex {args.codex_verb}", **outcome.to_dict()}
    if outcome.answered:
        lines = [f"thread  : {outcome.thread_id}",
                 f"message : {outcome.message_id}",
                 f"reply   : {outcome.reply}",
                 f"disposition: {outcome.disposition} - {outcome.guidance}"]
        if outcome.confidence_note:
            lines.append(f"grounded: {outcome.confidence_note}")
        if outcome.evidence_refs:
            lines.append(f"evidence: {outcome.evidence_refs}")
        if outcome.queue_result and outcome.queue_result != "queued":
            lines.append(f"queue   : {outcome.queue_result} - the reply is "
                         f"recorded on the thread; the boundary queue did "
                         f"not accept a new row")
        if outcome.redactions:
            lines.append(f"note    : {outcome.redactions} redaction(s)/"
                         f"control-sequence strip(s) were applied")
        lines.append(f"continue: /loop-codex continue {outcome.thread_id} "
                     f"<message>")
        emit_payload(args, payload, lines)
        return 0
    if outcome.timed_out:
        emit_payload(
            args, payload,
            [f"no reply within the {args.window:.0f}s window.",
             "the turn's process tree was terminated - nothing keeps running "
             "in the background.",
             f"your message is recorded on thread {outcome.thread_id}; "
             f"re-send it with `codex continue {outcome.thread_id} "
             f"<message>` (or the second terminal) when ready."])
        return 0
    return emit_refusal(args, refusals.refusal(
        refusals.STALE_STATE,
        reason_code=outcome.error_code or "codex_turn_failed",
        message=outcome.error_message or "the turn produced no usable reply"))


def cmd_codex(args: argparse.Namespace) -> int:
    """Dispatch one ``codex`` subverb (M0-T110; R234)."""
    _, journal, audit = open_runtime(args)
    try:
        if args.codex_verb in ("new", "continue"):
            kwargs = _provider_kwargs(args, journal, audit)
            if isinstance(kwargs, int):
                return kwargs
            try:
                if args.codex_verb == "new":
                    outcome = new_thread(args.text, **kwargs)
                else:
                    outcome = continue_thread(args.thread_id, args.text,
                                              **kwargs)
            except ChannelError as exc:
                return _refuse(args, exc)
            return _emit_turn(args, outcome)

        try:
            if args.codex_verb == "show":
                record = show_thread(journal, args.thread_id)
                lines = [f"thread  : {record['thread_id']}  "
                         f"({record.get('status', '?')})",
                         f"updated : {record.get('updated_at_utc', '')}",
                         f"summary : {record.get('summary', '') or '(none yet)'}"]
                for m in record.get("messages", []):
                    tag = m.get("disposition", "")
                    lines.append(
                        f"[{m.get('message_id', '?')}] {m.get('role', '?')}"
                        f"{f' ({tag})' if tag else ''}: {m.get('text', '')}")
                emit_payload(args, {"command": "codex show", "shown": record},
                             lines)
                return 0
            if args.codex_verb == "close":
                record = close_thread(journal, args.thread_id)
                emit_payload(
                    args, {"command": "codex close", **record},
                    [f"thread {record['thread_id']} "
                     f"{'was already closed' if record['already_closed'] else 'closed durably'}"
                     f" at {record['closed_at_utc']}."])
                return 0
            # promote
            record = promote_message(journal, audit, args.message_id)
            emit_payload(
                args, {"command": "codex promote", **record},
                [f"promotion {'already recorded' if record['already_promoted'] else 'recorded durably'}"
                 f" for {record['message_id']} "
                 f"({record.get('disposition', '')}).",
                 "this row authorizes nothing by itself: scope changes still "
                 "require durable directive/task capture via "
                 "/directive-compliance (D-024-R240)."])
            return 0
        except ChannelError as exc:
            return _refuse(args, exc)
    finally:
        journal.close()


def register_codex_channel_verbs(
        sub: Any, add_common: Callable[[argparse.ArgumentParser], None]) -> None:
    """Register the ``codex`` verb + subverbs on the existing surface."""
    codex = sub.add_parser(
        "codex",
        help="persistent same-terminal Codex-only discussion channel: "
             "new/continue/show/promote/close (live; Amendment 8)")
    verbs = codex.add_subparsers(dest="codex_verb", required=True)

    def add_provider(p: argparse.ArgumentParser) -> None:
        p.add_argument("--codex-executable", default=None,
                       help="explicit path to the Codex executable; never a "
                            "PATH search")
        p.add_argument("--config", default=None,
                       help="path to the immutable config.toml")
        p.add_argument("--model-selection", default=None,
                       help="path to the runtime model_selection.toml")
        p.add_argument("--window", type=float,
                       default=DEFAULT_TURN_WINDOW_SECONDS,
                       help="the bounded synchronous reply window, in "
                            "seconds; on timeout the process tree is "
                            "terminated and your message stays on the thread")

    new = verbs.add_parser("new", help="open a thread with its first "
                                       "bounded turn")
    add_common(new)
    add_provider(new)
    new.add_argument("text", help="the discussion question (quote it)")
    new.set_defaults(func=cmd_codex)

    cont = verbs.add_parser("continue", help="one more bounded turn on an "
                                             "open thread")
    add_common(cont)
    add_provider(cont)
    cont.add_argument("thread_id", help="the cxt_... thread id")
    cont.add_argument("text", help="your message (quote it)")
    cont.set_defaults(func=cmd_codex)

    show = verbs.add_parser("show", help="print the durable thread record "
                                         "(no provider call)")
    add_common(show)
    show.add_argument("thread_id", help="the cxt_... thread id")
    show.set_defaults(func=cmd_codex)

    promote = verbs.add_parser(
        "promote",
        help="record your explicit owner promotion of one Codex message "
             "(durable approval evidence; authorizes nothing by itself)")
    add_common(promote)
    promote.add_argument("message_id", help="the cxm_... Codex message id")
    promote.set_defaults(func=cmd_codex)

    close = verbs.add_parser("close", help="close a thread durably")
    add_common(close)
    close.add_argument("thread_id", help="the cxt_... thread id")
    close.set_defaults(func=cmd_codex)
