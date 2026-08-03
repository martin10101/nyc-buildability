#!/usr/bin/env python3
"""View-only notifications (D-007 S13.10).

S13.10: "Default notifications are view-only: run/task/checkpoint, reason, risk
class, short redacted summary, where to review - never secrets, sensitive raw
commands, auth links, or private source excerpts."

This module builds notifications that CANNOT carry those things:

* the payload is a fixed field set (`NOTIFICATION_FIELDS`); there is no free-form
  attachment slot, so a caller cannot smuggle a transcript through it;
* every text field passes through `redaction.redact_text` before it is stored,
  and the redaction count travels with the notification;
* raw commands, URLs that look like auth links, and source-excerpt shapes are
  REFUSED (not silently stripped) so the failure is visible;
* the summary is hard-bounded, so "short" is enforced rather than requested.

Delivery is an injected sink. Nothing here opens a socket: the only sink this
build ships is a durable local queue. A failed delivery leaves the item QUEUED
(S13.10) and, when owner input is required and the unit cannot proceed, reports
that the run must pause.
"""
from __future__ import annotations

import dataclasses
import re
import uuid
from typing import Any, Mapping, Sequence

from .models import digest_of, to_utc_iso
from .redaction import redact_text

#: The complete notification field set. There is no attachment or payload slot.
NOTIFICATION_FIELDS: tuple[str, ...] = (
    "notification_id", "run_id", "task_id", "checkpoint_id", "reason",
    "risk_class", "summary", "where_to_review", "requires_owner_input",
    "created_at_utc", "redaction_count",
)

RISK_CLASSES: tuple[str, ...] = ("info", "notify", "ask", "synchronous_stop")

#: "Short" is a bound, not an aspiration.
MAX_SUMMARY_CHARS = 400

#: Shapes that must never appear in a view-only notification. Each is refused
#: with its own reason so the operator sees WHY, rather than getting a silently
#: emptied field.
_FORBIDDEN_SHAPES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("auth_link", re.compile(
        r"https?://\S*(?:token|auth|login|magic|session|key|secret|signin)\S*", re.I),
     "an authentication or session link"),
    ("raw_command", re.compile(
        r"(?m)^\s*(?:\$|>|PS[ >])|(?:\b(?:git|gh|curl|wget|python|npm|schtasks|icacls)\b"
        r"[^\n]*(?:--\w|\s-\w\b))"),
     "a raw command line"),
    ("source_excerpt", re.compile(r"```|^\s{4,}\S+\s*=\s*\S+", re.M),
     "a source-code excerpt"),
    ("private_path", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\|/home/[^/\s]+/|/Users/[^/\s]+/"),
     "an absolute private user path"),
)


class NotificationError(Exception):
    """A notification would have leaked something. It is refused, not trimmed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class Notification:
    """One view-only notification. Every field is bounded and redacted."""

    notification_id: str
    run_id: str
    task_id: str
    checkpoint_id: str
    reason: str
    risk_class: str
    summary: str
    where_to_review: str
    requires_owner_input: bool
    created_at_utc: str
    redaction_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def digest(self) -> str:
        return digest_of(self.to_dict())


def assert_view_only(text: str, *, field: str) -> None:
    """Refuse text carrying a secret, a raw command, an auth link, or an excerpt."""
    for code, pattern, description in _FORBIDDEN_SHAPES:
        if pattern.search(text or ""):
            raise NotificationError(
                f"notification_would_leak_{code}",
                f"the {field} field contains {description}; S13.10 notifications are "
                f"view-only and never carry secrets, sensitive raw commands, auth links, or "
                f"private source excerpts. Point the owner at where to review instead")


def build_notification(
    *,
    run_id: str,
    task_id: str,
    checkpoint_id: str,
    reason: str,
    risk_class: str,
    summary: str,
    where_to_review: str,
    requires_owner_input: bool = False,
    never_send: Sequence[str] = (),
) -> Notification:
    """Build a redacted, bounded, view-only notification. Refuses on leak shapes."""
    if risk_class not in RISK_CLASSES:
        raise NotificationError("unknown_risk_class",
                                f"{risk_class!r} is not one of {list(RISK_CLASSES)}")
    if not where_to_review.strip():
        raise NotificationError("missing_review_pointer",
                                "a view-only notification must say WHERE to review the item; "
                                "that pointer is what replaces the content")

    redaction_count = 0
    cleaned: dict[str, str] = {}
    for field, raw in (("reason", reason), ("summary", summary),
                       ("where_to_review", where_to_review)):
        result = redact_text(raw or "", tuple(never_send))
        redaction_count += result.count
        assert_view_only(str(result.value), field=field)
        cleaned[field] = str(result.value)

    if len(cleaned["summary"]) > MAX_SUMMARY_CHARS:
        cleaned["summary"] = cleaned["summary"][:MAX_SUMMARY_CHARS - 3].rstrip() + "..."

    return Notification(
        notification_id=f"ntf_{uuid.uuid4().hex[:16]}",
        run_id=run_id,
        task_id=task_id,
        checkpoint_id=checkpoint_id,
        reason=cleaned["reason"],
        risk_class=risk_class,
        summary=cleaned["summary"],
        where_to_review=cleaned["where_to_review"],
        requires_owner_input=bool(requires_owner_input),
        created_at_utc=to_utc_iso(),
        redaction_count=redaction_count,
    )


# --------------------------------------------------------------------------
# Delivery
# --------------------------------------------------------------------------

QUEUE_KEY = "notification_queue"
DELIVERED_KEY = "notification_delivered"


class NotificationSink:
    """The delivery interface. This build ships only local sinks - no network."""

    name = "abstract"

    def deliver(self, notification: Notification) -> tuple[bool, str]:
        raise NotImplementedError


class LocalFileSink(NotificationSink):
    """Appends the view-only payload to a local file under the runtime directory."""

    name = "local_file"

    def __init__(self, path: Any) -> None:
        import pathlib

        self.path = pathlib.Path(path)

    def deliver(self, notification: Notification) -> tuple[bool, str]:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="") as handle:
                handle.write(str(digest_of(notification.to_dict())) + " "
                             + notification.risk_class + " "
                             + notification.summary.replace("\n", " ") + "\n")
        except OSError as exc:
            return False, f"local sink write failed: {exc}"
        return True, f"written to {self.path.name}"


@dataclasses.dataclass(frozen=True)
class DeliveryResult:
    delivered: bool
    notification_id: str
    sink: str
    detail: str
    still_queued: bool
    run_must_pause: bool = False


class NotificationQueue:
    """Durable queue. A failed delivery leaves the item queued (S13.10)."""

    def __init__(self, journal: Any, *, audit: Any = None) -> None:
        self.journal = journal
        self.audit = audit

    def queued(self) -> tuple[dict[str, Any], ...]:
        return tuple(self.journal.get_state(QUEUE_KEY, []) or [])

    def enqueue(self, notification: Notification) -> Notification:
        items = list(self.queued())
        items.append(notification.to_dict())
        self.journal.set_state(QUEUE_KEY, items)
        return notification

    def deliver(self, notification: Notification, sink: NotificationSink,
                *, unit_can_proceed: bool = True) -> DeliveryResult:
        """Deliver once. On failure the item stays queued and may pause the run."""
        self.enqueue(notification)
        ok, detail = sink.deliver(notification)
        if ok:
            self._dequeue(notification.notification_id)
            delivered = list(self.journal.get_state(DELIVERED_KEY, []) or [])
            delivered.append({"notification_id": notification.notification_id,
                              "digest": notification.digest(),
                              "sink": sink.name, "at_utc": to_utc_iso()})
            self.journal.set_state(DELIVERED_KEY, delivered)
            self._audit("notification_delivered",
                        {"notification_id": notification.notification_id,
                         "sink": sink.name, "risk_class": notification.risk_class})
            return DeliveryResult(True, notification.notification_id, sink.name, detail,
                                  still_queued=False)

        must_pause = notification.requires_owner_input and not unit_can_proceed
        self._audit("notification_delivery_failed",
                    {"notification_id": notification.notification_id, "sink": sink.name,
                     "detail": detail, "still_queued": True, "run_must_pause": must_pause})
        return DeliveryResult(
            False, notification.notification_id, sink.name,
            f"{detail}. The item REMAINS QUEUED"
            + (". Owner input is required and the unit cannot proceed, so the run pauses "
               "(S13.10)" if must_pause else ""),
            still_queued=True, run_must_pause=must_pause)

    def _dequeue(self, notification_id: str) -> None:
        items = [item for item in self.queued()
                 if item.get("notification_id") != notification_id]
        self.journal.set_state(QUEUE_KEY, items)

    def _audit(self, event: str, detail: Mapping[str, Any]) -> None:
        if self.audit is not None:
            self.audit.append(event, detail=dict(detail))
