"""One-way Telegram notification sink (D-024 Amendment 8, M0-T111 unit L).

A `NotificationSink` implementation over the S13.10 view-only notification
boundary for EXACTLY the eight Amendment-8 conditions (R241). Everything that
composes or stores text rides the existing machinery: `build_notification`
(fixed field set, redaction, leak-shape refusal, summary bound) and
`NotificationQueue` (a failed delivery leaves the item QUEUED). This module
adds only the closed condition vocabulary, a digest dedup register, bounded
in-call retries, the credential boundary, and the stdlib HTTPS transport.

Authority + secrecy boundary (unusual, so stated here):

* ONE-WAY ONLY (R242): there is no receive path - no getUpdates, no webhook,
  no command parsing, no approval/merge/execution/configuration surface. The
  transport is invoked with the Bot API ``sendMessage`` method and nothing
  else.
* SECRETS (R243): the bot token and chat identifier are read ONLY from the
  owner's local environment (``SUPERVISOR_TELEGRAM_BOT_TOKEN`` /
  ``SUPERVISOR_TELEGRAM_CHAT_ID``) at delivery time. They compose ONLY into
  the HTTPS request itself, never into notification rows, queue/dedup rows,
  audit lines, result details, error messages, or CLI output. Failure details
  carry exception class names and HTTP status buckets - never the URL (the
  Bot API URL embeds the token).
* OWNER-GATED LIVE SEND (R245): the real transport cannot be constructed
  without ``live_send_authorized=True``, which only the owner-typed CLI flag
  ``--live-canary-authorized-by-owner`` supplies. Tests inject fake
  transports; this unit never fires a live send.
* FAILURE ISOLATION (R244): ``deliver`` never raises; after the bounded
  attempts the item remains queued and the loop continues (`run_must_pause`
  is structurally False on every telegram path).

Supervisor-freeze qualifying evidence: D-024-R232/R241.
"""
from __future__ import annotations

import dataclasses
import os
import urllib.parse
import urllib.request
from typing import Any, Callable, Mapping

from .codex_channel import ATTENTION_KEY_PREFIX
from .models import digest_of, to_utc_iso
from .notifications import (
    QUEUE_KEY,
    Notification,
    NotificationError,
    NotificationQueue,
    NotificationSink,
    build_notification,
)
from .redaction import redact_text
from .resume_scheduler import CODEX_HOLD_KEY, LIMIT_RECORD_KEY

#: The closed R241 condition vocabulary. Anything else is a typed refusal -
#: never defaulted (the unit-K disposition rule, applied to conditions).
CONDITIONS: tuple[str, ...] = (
    "stop_for_owner",
    "approval_waiting",
    "breaker_open_stuck",
    "repeated_ci_failure",
    "unrecovered_controller_failure",
    "quota_refusal_hold",
    "golden_run_complete",
    "campaign_complete",
)

#: Fixed condition -> S13.10 risk class. A closed map, not caller-chosen.
CONDITION_RISK: dict[str, str] = {
    "stop_for_owner": "ask",
    "approval_waiting": "ask",
    "breaker_open_stuck": "notify",
    "repeated_ci_failure": "notify",
    "unrecovered_controller_failure": "synchronous_stop",
    "quota_refusal_hold": "notify",
    "golden_run_complete": "info",
    "campaign_complete": "info",
}

#: Bounded in-call delivery attempts (R244). No background scheduler: the
#: sink is one-way informational; past the bound the item stays queued.
MAX_DELIVERY_ATTEMPTS = 3
#: Hard per-attempt transport timeout, seconds.
TRANSPORT_TIMEOUT_SECONDS = 10.0
#: Durable dedup register: FIFO-trimmed digest list (R244 deduplication).
DEDUP_KEY = "telegram_dedup"
DEDUP_MAX_ENTRIES = 64
#: Hard total bound on one outbound message (Telegram caps at 4096; staying
#: well under keeps the truncation marker visible).
MAX_OUTBOUND_CHARS = 3_500

#: The owner's local secret mechanism (R243) - environment only, never a
#: repository file, never discovered from anywhere else.
TOKEN_ENV = "SUPERVISOR_TELEGRAM_BOT_TOKEN"
CHAT_ID_ENV = "SUPERVISOR_TELEGRAM_CHAT_ID"

#: The exact owner command for the R245 live canary (documented, never run
#: by this unit).
LIVE_CANARY_COMMAND = ("python -m tools.agent_supervisor telegram canary "
                      "--live-canary-authorized-by-owner")


class TelegramError(Exception):
    """A telegram-sink rule was violated. Typed, fail-closed, secret-free."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class Credentials:
    """The resolved secrets. Never printed: repr/str are redacted."""

    bot_token: str
    chat_id: str

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "Credentials(bot_token=[redacted], chat_id=[redacted])"

    __str__ = __repr__


def resolve_credentials(env: Mapping[str, str] | None = None) -> Credentials:
    """Read the secrets from the approved local mechanism (R243) or refuse."""
    source = env if env is not None else os.environ
    token = (source.get(TOKEN_ENV) or "").strip()
    chat_id = (source.get(CHAT_ID_ENV) or "").strip()
    if not (token and chat_id):
        raise TelegramError(
            "telegram_not_configured",
            f"{TOKEN_ENV} and {CHAT_ID_ENV} are not both set in this "
            f"session's environment; the sink refuses (secrets live only in "
            f"the owner's local environment - never the repository, R243)")
    return Credentials(bot_token=token, chat_id=chat_id)


def credentials_present(env: Mapping[str, str] | None = None) -> bool:
    """Presence check ONLY (for `telegram status`); never returns a value."""
    try:
        resolve_credentials(env)
        return True
    except TelegramError:
        return False


# --------------------------------------------------------------------------
# Transport (R245: the real one is owner-gated; tests inject fakes)
# --------------------------------------------------------------------------

#: A transport takes (credentials, text, timeout) and returns (ok, detail).
Transport = Callable[[Credentials, str, float], tuple[bool, str]]


def build_real_transport(*, live_send_authorized: bool = False,
                         opener: Callable[..., Any] | None = None) -> Transport:
    """The stdlib HTTPS ``sendMessage`` transport.

    Refuses construction without the owner authorization (R245). ``opener``
    is injectable so tests can prove the URL/body shape without a socket.
    """
    if not live_send_authorized:
        raise TelegramError(
            "live_send_owner_gated",
            f"a real Telegram send remains an owner-gated exact-command "
            f"canary (D-024-R245); it is authorized only by the owner typing: "
            f"{LIVE_CANARY_COMMAND}")
    open_url = opener or urllib.request.urlopen

    def transport(credentials: Credentials, text: str,
                  timeout: float) -> tuple[bool, str]:
        # The token composes ONLY into the request URL; the detail strings
        # below carry status buckets / exception classes, never the URL.
        url = (f"https://api.telegram.org/bot{credentials.bot_token}"
               f"/sendMessage")
        body = urllib.parse.urlencode({
            "chat_id": credentials.chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        request = urllib.request.Request(url, data=body, method="POST")
        response = open_url(request, timeout=timeout)  # noqa: S310 - fixed https host
        status = int(getattr(response, "status", 0) or 0)
        if 200 <= status < 300:
            return True, "sent (2xx)"
        return False, f"telegram responded with status bucket {status // 100}xx"

    return transport


class TelegramSink(NotificationSink):
    """One-way Telegram delivery of a view-only notification (R241)."""

    name = "telegram"

    def __init__(self, transport: Transport, *,
                 env: Mapping[str, str] | None = None,
                 timeout: float = TRANSPORT_TIMEOUT_SECONDS,
                 max_attempts: int = MAX_DELIVERY_ATTEMPTS) -> None:
        self.transport = transport
        self.env = env
        self.timeout = float(timeout)
        self.max_attempts = max(1, int(max_attempts))
        self.last_attempts = 0

    def compose_text(self, notification: Notification) -> str:
        """The outbound text: view-only fields only. The S13.10 builder has
        already redacted/bounded reason/summary/where_to_review; the identifier
        fields ride through the builder unredacted (G5 MINOR-2, gate round),
        so they are redacted HERE, and the whole message carries a hard total
        bound with a visible truncation marker."""
        task = str(redact_text(notification.task_id or "-").value)
        run = str(redact_text(notification.run_id or "-").value)
        text = (f"[{notification.risk_class}] {notification.reason}\n"
                f"task: {task}  run: {run}\n"
                f"{notification.summary}\n"
                f"review: {notification.where_to_review}")
        if len(text) > MAX_OUTBOUND_CHARS:
            text = text[:MAX_OUTBOUND_CHARS - 15].rstrip() + " ...[truncated]"
        return text

    def deliver(self, notification: Notification) -> tuple[bool, str]:
        """Bounded attempts; NEVER raises (R244 failure isolation)."""
        self.last_attempts = 0
        try:
            credentials = resolve_credentials(self.env)
        except TelegramError as exc:
            return False, f"{exc.code}: delivery skipped; the item stays queued"
        text = self.compose_text(notification)
        detail = "no attempt made"
        for attempt in range(1, self.max_attempts + 1):
            self.last_attempts = attempt
            try:
                ok, detail = self.transport(credentials, text, self.timeout)
            except Exception as exc:  # noqa: BLE001 - isolation: never raise
                ok, detail = False, f"transport {type(exc).__name__}"
            if ok:
                return True, f"{detail} (attempt {attempt}/{self.max_attempts})"
        return False, (f"failed after {self.max_attempts} attempt(s): {detail}")


# --------------------------------------------------------------------------
# The single entry point (R241) + dedup (R244)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class NotifyOutcome:
    """One notify_condition call. Structurally loop-safe: never a pause."""

    condition: str
    deduplicated: bool = False
    already_queued: bool = False
    delivered: bool = False
    still_queued: bool = False
    attempts: int = 0
    notification_id: str = ""
    detail: str = ""
    error_code: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _dedup_digest(condition: str, task_id: str, summary: str) -> str:
    return digest_of({"condition": condition, "task_id": task_id,
                      "summary": summary})


def _dedup_seen(journal: Any, digest: str) -> bool:
    entries = journal.get_state(DEDUP_KEY, []) or []
    return any(e.get("digest") == digest for e in entries)


def _already_queued(journal: Any, digest: str) -> bool:
    """True when an identical (condition, task, summary) item is already
    sitting in the durable queue awaiting delivery. Bounds queue growth
    under a sustained outage (G5 ADVISORY-1, gate round) without touching
    the frozen S13.10 queue itself — at-least-once is preserved because the
    queued item is still there to deliver."""
    for item in journal.get_state(QUEUE_KEY, []) or []:
        if _dedup_digest(item.get("reason", ""), item.get("task_id", ""),
                         item.get("summary", "")) == digest:
            return True
    return False


def _dedup_record(journal: Any, digest: str) -> None:
    entries = list(journal.get_state(DEDUP_KEY, []) or [])
    entries.append({"digest": digest, "at_utc": to_utc_iso()})
    if len(entries) > DEDUP_MAX_ENTRIES:
        entries = entries[-DEDUP_MAX_ENTRIES:]
    journal.set_state(DEDUP_KEY, entries)


def notify_condition(journal: Any, audit: Any, *, condition: str,
                     summary: str, where_to_review: str, sink: TelegramSink,
                     run_id: str = "", task_id: str = "",
                     checkpoint_id: str = "") -> NotifyOutcome:
    """Deliver ONE condition notification through the queued sink.

    The only entry point (R241): validates the closed vocabulary, dedups,
    composes via the S13.10 builder (which refuses leak shapes), and rides
    ``NotificationQueue.deliver`` with ``unit_can_proceed=True`` - a failed
    delivery leaves the item queued and the loop untouched (R244).
    """
    if condition not in CONDITIONS:
        raise TelegramError(
            "unknown_condition",
            f"{condition!r} is not one of the eight Amendment-8 conditions "
            f"{CONDITIONS}; refusing (closed vocabulary, R241)")
    digest = _dedup_digest(condition, task_id, summary)
    if _dedup_seen(journal, digest):
        if audit is not None:
            audit.append("telegram_deduplicated",
                         detail={"condition": condition, "digest": digest})
        return NotifyOutcome(condition=condition, deduplicated=True,
                             detail="identical notification already sent; "
                                    "deduplicated (R244)")
    if _already_queued(journal, digest):
        if audit is not None:
            audit.append("telegram_already_queued",
                         detail={"condition": condition, "digest": digest})
        return NotifyOutcome(condition=condition, already_queued=True,
                             still_queued=True,
                             detail="an identical item is already queued "
                                    "awaiting delivery; not re-enqueued "
                                    "(bounded queue growth, R244)")
    try:
        notification = build_notification(
            run_id=run_id, task_id=task_id, checkpoint_id=checkpoint_id,
            reason=condition, risk_class=CONDITION_RISK[condition],
            summary=summary, where_to_review=where_to_review,
            requires_owner_input=CONDITION_RISK[condition] in
            ("ask", "synchronous_stop"))
    except NotificationError as exc:
        return NotifyOutcome(condition=condition, error_code=exc.code,
                             detail=exc.message)
    queue = NotificationQueue(journal, audit=audit)
    result = queue.deliver(notification, sink, unit_can_proceed=True)
    if result.delivered:
        _dedup_record(journal, digest)
    return NotifyOutcome(
        condition=condition, delivered=result.delivered,
        still_queued=result.still_queued, attempts=sink.last_attempts,
        notification_id=result.notification_id, detail=result.detail)


# --------------------------------------------------------------------------
# Passive discovery (read-only; the two durably-derivable conditions)
# --------------------------------------------------------------------------


def discover_conditions(journal: Any) -> tuple[dict[str, Any], ...]:
    """Read-only scan for the conditions that already have durable records.

    Exactly two are passively derivable (unit report §1): STOP_FOR_OWNER
    attention rows (unit K) and the quota/refusal hold records. Everything
    else is loop-emitted through :func:`notify_condition` at the seam -
    nothing here invents an event that did not durably occur.
    """
    found: list[dict[str, Any]] = []
    state = journal.all_state()
    for key, row in state.items():
        if key.startswith(ATTENTION_KEY_PREFIX) and isinstance(row, dict) \
                and row.get("disposition") == "STOP_FOR_OWNER" \
                and not row.get("actuated", False):
            found.append({"condition": "stop_for_owner", "source_key": key,
                          "reference": row.get("message_id", "")})
    for key in (LIMIT_RECORD_KEY, CODEX_HOLD_KEY):
        if isinstance(state.get(key), dict):
            found.append({"condition": "quota_refusal_hold",
                          "source_key": key, "reference": ""})
    return tuple(found)
