"""CLI verbs for the one-way Telegram sink (D-024 Amendment 8, M0-T111).

``telegram status|canary`` on the EXISTING command surface (the unit-G/K
registration pattern). Wiring + display only; every rule lives in
``telegram_sink``. Output rides ``operator_channel_cli.emit_payload`` so
stdout stays a redacted transmission — and `status` reports credential
PRESENCE only, never a value (R243).

Supervisor-freeze qualifying evidence: D-024-R232/R241.
"""
from __future__ import annotations

import argparse
from typing import Any, Callable

from . import refusals
from .notifications import DELIVERED_KEY, QUEUE_KEY, build_notification
from .operator_channel_cli import emit_payload, open_runtime
from .start_gate import emit_refusal
from .telegram_sink import (
    CHAT_ID_ENV,
    DEDUP_KEY,
    LIVE_CANARY_COMMAND,
    TOKEN_ENV,
    NotificationQueue,
    TelegramError,
    TelegramSink,
    build_real_transport,
    credentials_present,
)


def cmd_telegram(args: argparse.Namespace) -> int:
    """Dispatch one ``telegram`` subverb (M0-T111; R241/R245)."""
    _, journal, audit = open_runtime(args)
    try:
        if args.telegram_verb == "status":
            queued = journal.get_state(QUEUE_KEY, []) or []
            delivered = journal.get_state(DELIVERED_KEY, []) or []
            dedup = journal.get_state(DEDUP_KEY, []) or []
            configured = credentials_present()
            emit_payload(
                args,
                {"command": "telegram status", "configured": configured,
                 "queued": len(queued), "delivered": len(delivered),
                 "dedup_entries": len(dedup), "one_way_only": True},
                [f"configured: {'yes' if configured else 'no'} "
                 f"({TOKEN_ENV} + {CHAT_ID_ENV} presence only; values are "
                 f"never read into output, R243)",
                 f"queued  : {len(queued)}",
                 f"delivered: {len(delivered)}",
                 f"dedup   : {len(dedup)} digest(s)",
                 "one-way only: no Telegram approvals, merges, execution, "
                 "or configuration (R242)",
                 f"live canary (owner-typed only): {LIVE_CANARY_COMMAND}"])
            return 0

        # canary (R245): owner-gated exact command; ONE fixed bounded send.
        if not args.live_canary_authorized_by_owner:
            return emit_refusal(args, refusals.refusal(
                refusals.STALE_STATE, reason_code="live_send_owner_gated",
                message=f"a real Telegram send is an owner-gated "
                        f"exact-command canary (D-024-R245); nothing was "
                        f"sent. The exact command: {LIVE_CANARY_COMMAND}"))
        try:
            transport = build_real_transport(live_send_authorized=True)
        except TelegramError as exc:  # pragma: no cover - gate passed above
            return emit_refusal(args, refusals.refusal(
                refusals.STALE_STATE, reason_code=exc.code,
                message=exc.message))
        sink = TelegramSink(transport)
        notification = build_notification(
            run_id="operator", task_id="", checkpoint_id="",
            reason="owner_live_canary", risk_class="info",
            summary="One-way Telegram canary: the sink can deliver "
                    "view-only notifications to the owner.",
            where_to_review="the supervisor runtime notification queue")
        result = NotificationQueue(journal, audit=audit).deliver(
            notification, sink, unit_can_proceed=True)
        emit_payload(
            args, {"command": "telegram canary",
                   "delivered": result.delivered,
                   "still_queued": result.still_queued,
                   "attempts": sink.last_attempts,
                   "detail": result.detail},
            [f"canary {'DELIVERED' if result.delivered else 'NOT delivered'} "
             f"after {sink.last_attempts} attempt(s).",
             f"detail: {result.detail}",
             *([] if result.delivered else
               ["the item remains queued; the loop is unaffected (R244)."])])
        return 0
    finally:
        journal.close()


def register_telegram_verbs(
        sub: Any, add_common: Callable[[argparse.ArgumentParser], None]) -> None:
    """Register the ``telegram`` verb + subverbs on the existing surface."""
    telegram = sub.add_parser(
        "telegram",
        help="one-way Telegram notification sink: status/canary "
             "(live send owner-gated; Amendment 8)")
    verbs = telegram.add_subparsers(dest="telegram_verb", required=True)

    status = verbs.add_parser(
        "status", help="credential PRESENCE (never values), queue depth, "
                       "dedup count")
    add_common(status)
    status.set_defaults(func=cmd_telegram)

    canary = verbs.add_parser(
        "canary",
        help="ONE bounded live canary send; refuses without the explicit "
             "owner flag (D-024-R245)")
    add_common(canary)
    canary.add_argument("--live-canary-authorized-by-owner",
                        action="store_true",
                        help="explicit owner authorization for the ONE real "
                             "send; without it the command refuses")
    canary.set_defaults(func=cmd_telegram)
