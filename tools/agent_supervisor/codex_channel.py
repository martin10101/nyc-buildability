"""Persistent same-terminal Codex-only discussion channel (D-024 Amendment 8).

M0-T110 unit K (qualifying evidence D-024-R232/R234; rows R233-R240).

Threads live as namespaced ``state_kv`` register rows in the existing durable
journal (the CAS conventions unit I re-proved); every provider turn is ONE
bounded read-only Codex invocation built by ``codex_reviewer.build_argv`` and
contained by ``process.run`` - a timeout terminates the whole tree, never a
background duplicate. Per-turn context is exactly the R236 set: a bounded
durable summary, bounded recent exchanges, fresh labeled supervisor/campaign
state, stable evidence references, and the reviewer sandbox's own read-only
repository access for deeper inspection. Never the transcript, the repository
dump, or unrelated history (R237).

Authority boundary (unusual, so stated here): NOTHING in this module can alter
Fable's instructions, tasks, or controls (R239). Every reply carries one
disposition from the closed vocabulary; the channel records durable rows and
displays guidance - actuation stays with the owner and the existing
supervisor machinery. Promotion (R240) only RECORDS the owner's explicit
approval of one Codex message; scope changes still require durable
directive/task capture through the existing route. This module deliberately
imports no stop-intent, repair-gate, task, or ledger write surface.
"""
from __future__ import annotations

import dataclasses
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping

from .codex_reviewer import build_argv
from .models import digest_of, to_utc_iso
from .operator_ask import (
    AskError,
    bound_answer,
    read_answer_file,
    sanitize_question,
    validate_identity,
)
from .operator_status import compose_status
from .policy import resolve_model
from .process import ProcessResult, minimal_env
from .process import run as run_process
from .redaction import redact_structure

CHANNEL_SCHEMA_VERSION = "1.0.0"

#: Register namespaces (``state_kv``). One row per thread; one index row per
#: Codex message (so ``promote`` never scans); one row per promotion and per
#: attention item; one bounded queue row.
THREAD_KEY_PREFIX = "codex_channel/thread/"
MESSAGE_INDEX_KEY_PREFIX = "codex_channel/message/"
PROMOTION_KEY_PREFIX = "codex_channel/promotion/"
ATTENTION_KEY_PREFIX = "codex_channel/attention/"
BOUNDARY_QUEUE_KEY = "codex_channel/boundary_queue"

THREAD_ID_PREFIX = "cxt_"
MESSAGE_ID_PREFIX = "cxm_"

#: Bounds (R236/R237: bounded everywhere, visibly). The message bound itself
#: is ``operator_ask.MAX_QUESTION_CHARS`` via the reused sanitizer.
MAX_SUMMARY_CHARS = 2_000
MAX_RECENT_EXCHANGES = 6
MAX_THREAD_MESSAGES = 40
MAX_PACKET_BYTES = 56_000
MAX_BOUNDARY_QUEUE = 32
DEFAULT_TURN_WINDOW_SECONDS = 90.0

#: The R239 closed disposition vocabulary. There is deliberately no default:
#: a reply without one of these values is a typed failure, never coerced.
DISPOSITIONS = (
    "ADVICE_ONLY",
    "QUEUE_NEXT_BOUNDARY",
    "REVISE_CURRENT_TASK",
    "PROPOSE_NEW_TASK",
    "URGENT_PAUSE",
    "STOP_FOR_OWNER",
)
#: Only a concrete change proposal is promotable (R240); advice, queue rows,
#: and attention items each have their own lane.
PROMOTABLE_DISPOSITIONS = ("REVISE_CURRENT_TASK", "PROPOSE_NEW_TASK")
ATTENTION_DISPOSITIONS = ("URGENT_PAUSE", "STOP_FOR_OWNER")

#: Owner guidance displayed per disposition. Naming the EXACT existing command
#: is the actuation path - the channel itself actuates nothing (R239).
DISPOSITION_GUIDANCE: dict[str, str] = {
    "ADVICE_ONLY": "advice only; nothing was queued or changed.",
    "QUEUE_NEXT_BOUNDARY": "queued durably for the next safe boundary; "
                           "no model context was touched.",
    "REVISE_CURRENT_TASK": "a finding enters the current task ONLY through "
                           "the existing authorized repair route; promote it "
                           "with /loop-codex promote <message-id> to record "
                           "your approval durably.",
    "PROPOSE_NEW_TASK": "parked on the thread; promote it with /loop-codex "
                        "promote <message-id> - new scope still requires "
                        "durable directive/task capture.",
    "URGENT_PAUSE": "ATTENTION recorded durably. Nothing was paused "
                    "automatically; to pause now run: "
                    "python -m tools.agent_supervisor pause",
    "STOP_FOR_OWNER": "ATTENTION recorded durably for an owner decision. "
                      "Nothing was stopped automatically; controls: "
                      "python -m tools.agent_supervisor graceful-stop | stop "
                      "| emergency-stop",
}

_SCHEMA_PATH = Path(__file__).with_name("schemas") / \
    "codex_discussion_reply.schema.json"


class ChannelError(Exception):
    """A channel rule was violated. Always fails closed, never a partial row."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _sanitized_inputs(text: str, checkout: Path) -> tuple[str, int,
                                                          list[dict[str, Any]]]:
    """Reuse the ask sanitizer + identity validation, surfacing their typed
    refusals as ChannelError (same codes) so the channel has ONE error type."""
    try:
        cleaned, redactions = sanitize_question(text)
        campaigns = validate_identity(checkout)
    except AskError as exc:
        raise ChannelError(exc.code, exc.message) from exc
    return cleaned, redactions, campaigns


# --------------------------------------------------------------------------
# Thread records
# --------------------------------------------------------------------------


def _thread_key(thread_id: str) -> str:
    return THREAD_KEY_PREFIX + thread_id


def load_thread(journal: Any, thread_id: str) -> dict[str, Any]:
    if not isinstance(thread_id, str) or \
            not thread_id.startswith(THREAD_ID_PREFIX):
        raise ChannelError(
            "not_a_thread_id",
            f"{thread_id!r} is not a discussion thread id (expected the "
            f"{THREAD_ID_PREFIX!r} prefix)")
    record = journal.get_state(_thread_key(thread_id), None)
    if not isinstance(record, dict):
        raise ChannelError("unknown_thread",
                           f"no discussion thread has id {thread_id!r}")
    return record


def _bound_summary(text: Any, prior: str) -> str:
    """The provider-maintained durable summary: bounded on store; an empty
    update keeps the prior summary (a turn never erases context silently)."""
    cleaned = bound_answer(text if isinstance(text, str) else "")
    if len(cleaned) > MAX_SUMMARY_CHARS:
        cleaned = cleaned[:MAX_SUMMARY_CHARS - 15].rstrip() + " ...[truncated]"
    return cleaned if cleaned.strip() else prior


def _message_entry(role: str, text: str, *, message_id: str,
                   disposition: str = "") -> dict[str, Any]:
    return {"message_id": message_id, "role": role, "text": text,
            "disposition": disposition, "at_utc": to_utc_iso()}


# --------------------------------------------------------------------------
# The bounded per-turn packet (R236/R237/R238)
# --------------------------------------------------------------------------


def build_turn_packet(journal: Any, *, checkout: Path, thread: Mapping[str, Any],
                      message: str,
                      campaigns: list[dict[str, Any]]) -> dict[str, Any]:
    """Exactly the R236 context set, redacted, under a hard byte ceiling.

    Trimming order is visible (``omitted_for_size``): bulky fresh-state
    sections first, then the oldest recent exchanges; still over -> a typed
    refusal, never an unbounded send (R237).
    """
    recents = [
        {"message_id": m.get("message_id", ""), "role": m.get("role", ""),
         "text": bound_answer(m.get("text", "")),
         "disposition": m.get("disposition", "")}
        for m in list(thread.get("messages", []))[-MAX_RECENT_EXCHANGES:]
    ]
    facts = redact_structure(compose_status(journal, checkout=checkout)).value
    packet: dict[str, Any] = {
        "schema_version": CHANNEL_SCHEMA_VERSION,
        "kind": "codex_discussion_turn",
        "thread": {
            "thread_id": thread.get("thread_id", ""),
            "summary": thread.get("summary", ""),
            "recent_exchanges": recents,
        },
        "message": message,
        "campaigns": campaigns,
        "state": facts,
        "reference_guidance": (
            "Cite commit SHAs, content digests, changed paths, symbols, and "
            "test names - never bare line numbers (they drift)."),
        "instruction": (
            "You are the read-only Codex discussion partner for the owner. "
            "Discuss using ONLY this packet plus read-only inspection of the "
            "working directory when you need more detail; never ask for the "
            "full conversation transcript, the whole repository, all source "
            "code, or full logs. Return exactly one object matching the "
            "codex_discussion_reply schema: a concise reply, ONE disposition "
            "from the closed set, an updated bounded thread summary, and "
            "stable evidence references. Say 'unknown from the provided "
            "state' rather than inventing a fact. Your reply changes nothing "
            "by itself; the owner decides."),
    }

    def _size() -> int:
        return len(json.dumps(packet, ensure_ascii=False).encode("utf-8"))

    if _size() > MAX_PACKET_BYTES:
        omitted: list[str] = []
        state = dict(packet["state"])
        for key in ("recent_transitions", "subagents", "current_task"):
            if key in state:
                state[key] = {"value": "omitted", "source": "packet size bound",
                              "confidence": "unknown"}
                omitted.append(key)
        packet["state"] = state
        while _size() > MAX_PACKET_BYTES and \
                packet["thread"]["recent_exchanges"]:
            dropped = packet["thread"]["recent_exchanges"].pop(0)
            omitted.append(f"exchange:{dropped.get('message_id', '?')}")
        packet["omitted_for_size"] = omitted
        if _size() > MAX_PACKET_BYTES:
            raise ChannelError(
                "packet_too_large",
                f"the discussion packet is {_size()} bytes after trimming; "
                f"the bound is {MAX_PACKET_BYTES}. Refusing to send an "
                f"unbounded payload (R237)")
    return packet


def validate_reply(raw: Any) -> dict[str, Any]:
    """Validate + bound the provider reply. The disposition is the R239 closed
    vocabulary - unknown or missing is a typed failure, never a default."""
    if not isinstance(raw, Mapping):
        raise ChannelError("reply_not_object",
                           "the provider returned no schema-valid reply object")
    reply = raw.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise ChannelError("reply_empty",
                           "the provider's reply field is empty or not text")
    disposition = raw.get("disposition")
    if disposition not in DISPOSITIONS:
        raise ChannelError(
            "disposition_invalid",
            f"the provider's disposition {disposition!r} is not in the closed "
            f"set {DISPOSITIONS}; refusing the reply (R239 - never defaulted)")
    refs = raw.get("evidence_refs", [])
    if not isinstance(refs, list) or any(not isinstance(r, str) for r in refs):
        refs = []
    note = raw.get("confidence_note", "")
    return {
        "reply": bound_answer(reply),
        "disposition": disposition,
        "updated_summary": raw.get("updated_summary", ""),
        "confidence_note": bound_answer(note if isinstance(note, str) else ""),
        "evidence_refs": ", ".join(bound_answer(r) for r in refs[:8]),
    }


# --------------------------------------------------------------------------
# Turn outcome
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class TurnOutcome:
    """One discussion turn: a reply with its disposition, or a typed failure."""

    answered: bool
    thread_id: str = ""
    message_id: str = ""
    model_used: str = ""
    reply: str = ""
    disposition: str = ""
    guidance: str = ""
    confidence_note: str = ""
    evidence_refs: str = ""
    queue_result: str = ""
    attention_key: str = ""
    timed_out: bool = False
    tree_terminated: bool = False
    error_code: str = ""
    error_message: str = ""
    redactions: int = 0

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _audit(audit: Any, event: str, **detail: Any) -> None:
    if audit is not None:
        audit.append(event, detail=dict(detail))


# --------------------------------------------------------------------------
# Disposition side effects (durable rows only - never actuation; R239)
# --------------------------------------------------------------------------


def _queue_boundary_item(journal: Any, item: dict[str, Any]) -> str:
    """Append one bounded row to the boundary queue. A full queue is a visible
    'queue_full' result, never a silent drop and never a failed turn."""
    for _ in range(3):
        stored = journal.get_state(BOUNDARY_QUEUE_KEY, None)
        items = list(stored) if isinstance(stored, list) else []
        if len(items) >= MAX_BOUNDARY_QUEUE:
            return "queue_full"
        expected = stored if isinstance(stored, list) else None
        if journal.compare_and_swap_state(BOUNDARY_QUEUE_KEY, expected,
                                          items + [item]):
            return "queued"
    return "queue_contended"


def _apply_disposition_effects(journal: Any, audit: Any, *, thread_id: str,
                               message_id: str,
                               fields: Mapping[str, Any]) -> tuple[str, str]:
    """Durable rows per disposition (§3 of the unit report). Returns
    (queue_result, attention_key)."""
    disposition = fields["disposition"]
    queue_result = ""
    attention_key = ""
    if disposition == "QUEUE_NEXT_BOUNDARY":
        queue_result = _queue_boundary_item(journal, {
            "schema_version": CHANNEL_SCHEMA_VERSION,
            "message_id": message_id, "thread_id": thread_id,
            "reply_digest": digest_of({"reply": fields["reply"]}),
            "queued_at_utc": to_utc_iso(),
        })
    elif disposition in ATTENTION_DISPOSITIONS:
        attention_key = ATTENTION_KEY_PREFIX + message_id
        journal.compare_and_swap_state(attention_key, None, {
            "schema_version": CHANNEL_SCHEMA_VERSION,
            "message_id": message_id, "thread_id": thread_id,
            "disposition": disposition,
            "reply_digest": digest_of({"reply": fields["reply"]}),
            "recorded_at_utc": to_utc_iso(),
            "actuated": False,
        })
        _audit(audit, "codex_channel_attention",
               thread_id=thread_id, message_id=message_id,
               disposition=disposition)
    return queue_result, attention_key


# --------------------------------------------------------------------------
# The provider turn
# --------------------------------------------------------------------------


def _run_turn(thread: dict[str, Any], message: str, *, journal: Any,
              audit: Any, executable: str, checkout: Path, config: Any,
              selection: Any, window_seconds: float,
              availability: Callable[[str], bool] | None,
              runner: Callable[..., ProcessResult] | None,
              message_id_factory: Callable[[], str] | None,
              create: bool, redactions: int,
              campaigns: list[dict[str, Any]]) -> TurnOutcome:
    """One bounded synchronous discussion window against the read-only
    reviewer contract. Persistence happens ONLY after a validated reply (or,
    on timeout, the owner message alone so `show` stays honest)."""
    thread_id = thread["thread_id"]
    if not (0 < float(window_seconds) <= 3600):
        raise ChannelError("bad_window",
                           f"window_seconds must be in (0, 3600], got "
                           f"{window_seconds!r}")
    resolution = resolve_model("codex", config=config, selection=selection,
                               availability=availability, role="primary",
                               purpose="codex_discussion")
    packet = build_turn_packet(journal, checkout=checkout, thread=thread,
                               message=message, campaigns=campaigns)
    if not resolution.usable:
        return TurnOutcome(answered=False, thread_id=thread_id,
                           error_code=resolution.reason_code,
                           error_message=resolution.reason,
                           redactions=redactions)

    make_id = message_id_factory or \
        (lambda: MESSAGE_ID_PREFIX + uuid.uuid4().hex[:16])
    run = runner or run_process
    handle, output_path = tempfile.mkstemp(prefix="codex_channel_",
                                           suffix=".json")
    os.close(handle)
    try:
        argv = build_argv(executable, repo=str(checkout),
                          model=resolution.model,
                          schema_path=str(_SCHEMA_PATH),
                          output_path=output_path)
        result = run(argv, cwd=str(checkout), env=minimal_env(),
                     timeout=float(window_seconds),
                     input_text=json.dumps(packet, ensure_ascii=False))
        owner_entry = _message_entry("owner", message, message_id=make_id())
        if result.timed_out:
            # The contained tree is already terminated (no background
            # duplicate); the owner message is persisted so the thread record
            # matches what happened.
            updated = dict(thread)
            updated["messages"] = list(thread.get("messages", [])) + \
                [owner_entry]
            updated["updated_at_utc"] = to_utc_iso()
            _store_thread(journal, thread, updated, create=create)
            _audit(audit, "codex_channel_timeout", thread_id=thread_id,
                   window_seconds=float(window_seconds),
                   tree_terminated=result.tree_terminated)
            return TurnOutcome(answered=False, thread_id=thread_id,
                               model_used=resolution.model, timed_out=True,
                               tree_terminated=result.tree_terminated,
                               redactions=redactions)
        raw = read_answer_file(output_path, result)
        try:
            if raw is None:
                raise ChannelError(
                    "no_reply",
                    f"the reviewer process exited {result.returncode} with no "
                    f"schema-valid reply object")
            fields = validate_reply(raw)
        except ChannelError as exc:
            _audit(audit, "codex_channel_turn_failed", thread_id=thread_id,
                   error_code=exc.code, returncode=result.returncode)
            return TurnOutcome(answered=False, thread_id=thread_id,
                               model_used=resolution.model,
                               error_code=exc.code, error_message=exc.message,
                               redactions=redactions)

        codex_id = make_id()
        codex_entry = _message_entry("codex", fields["reply"],
                                     message_id=codex_id,
                                     disposition=fields["disposition"])
        updated = dict(thread)
        updated["messages"] = list(thread.get("messages", [])) + \
            [owner_entry, codex_entry]
        updated["summary"] = _bound_summary(fields["updated_summary"],
                                            thread.get("summary", ""))
        updated["updated_at_utc"] = to_utc_iso()
        _store_thread(journal, thread, updated, create=create)
        journal.compare_and_swap_state(
            MESSAGE_INDEX_KEY_PREFIX + codex_id, None,
            {"thread_id": thread_id, "message_id": codex_id})
        queue_result, attention_key = _apply_disposition_effects(
            journal, audit, thread_id=thread_id, message_id=codex_id,
            fields=fields)
        _audit(audit, "codex_channel_turn", thread_id=thread_id,
               message_id=codex_id, disposition=fields["disposition"],
               packet_bytes=len(json.dumps(packet, ensure_ascii=False)
                                .encode("utf-8")),
               reply_digest=digest_of({"reply": fields["reply"]}),
               model=resolution.model)
        return TurnOutcome(
            answered=True, thread_id=thread_id, message_id=codex_id,
            model_used=resolution.model, reply=fields["reply"],
            disposition=fields["disposition"],
            guidance=DISPOSITION_GUIDANCE[fields["disposition"]],
            confidence_note=fields["confidence_note"],
            evidence_refs=fields["evidence_refs"],
            queue_result=queue_result, attention_key=attention_key,
            redactions=redactions)
    finally:
        try:
            os.unlink(output_path)
        except OSError:  # pragma: no cover - defensive
            pass


def _store_thread(journal: Any, before: Mapping[str, Any],
                  after: dict[str, Any], *, create: bool) -> None:
    """CAS single-winner persistence: a concurrent contender loses cleanly
    with a typed error, never a silent overwrite."""
    key = _thread_key(after["thread_id"])
    expected = None if create else dict(before)
    if not journal.compare_and_swap_state(key, expected, after):
        raise ChannelError(
            "thread_conflict",
            f"thread {after['thread_id']} changed concurrently; show it and "
            f"re-send your message")


# --------------------------------------------------------------------------
# Public operations (the five subverbs)
# --------------------------------------------------------------------------


def new_thread(question: str, *, journal: Any, audit: Any, executable: str,
               checkout: Path, config: Any, selection: Any,
               window_seconds: float = DEFAULT_TURN_WINDOW_SECONDS,
               availability: Callable[[str], bool] | None = None,
               runner: Callable[..., ProcessResult] | None = None,
               thread_id_factory: Callable[[], str] | None = None,
               message_id_factory: Callable[[], str] | None = None,
               ) -> TurnOutcome:
    """Open a discussion thread with its first bounded turn."""
    cleaned, redactions, campaigns = _sanitized_inputs(question, checkout)
    make_thread_id = thread_id_factory or \
        (lambda: THREAD_ID_PREFIX + uuid.uuid4().hex[:16])
    thread = {
        "schema_version": CHANNEL_SCHEMA_VERSION,
        "thread_id": make_thread_id(),
        "status": "open",
        "created_at_utc": to_utc_iso(),
        "updated_at_utc": to_utc_iso(),
        "summary": "",
        "messages": [],
        "closed_at_utc": "",
    }
    return _run_turn(thread, cleaned, journal=journal, audit=audit,
                     executable=executable, checkout=checkout, config=config,
                     selection=selection, window_seconds=window_seconds,
                     availability=availability, runner=runner,
                     message_id_factory=message_id_factory, create=True,
                     redactions=redactions, campaigns=campaigns)


def continue_thread(thread_id: str, message: str, *, journal: Any, audit: Any,
                    executable: str, checkout: Path, config: Any,
                    selection: Any,
                    window_seconds: float = DEFAULT_TURN_WINDOW_SECONDS,
                    availability: Callable[[str], bool] | None = None,
                    runner: Callable[..., ProcessResult] | None = None,
                    message_id_factory: Callable[[], str] | None = None,
                    ) -> TurnOutcome:
    """One more bounded turn on an existing open thread."""
    cleaned, redactions, campaigns = _sanitized_inputs(message, checkout)
    thread = load_thread(journal, thread_id)
    if thread.get("status") != "open":
        raise ChannelError("thread_closed",
                           f"thread {thread_id} is closed; open a new one "
                           f"with /loop-codex new <question>")
    if len(thread.get("messages", [])) >= MAX_THREAD_MESSAGES:
        raise ChannelError(
            "thread_full",
            f"thread {thread_id} holds {MAX_THREAD_MESSAGES} messages (the "
            f"bound). Start a new thread - its summary carries the context "
            f"forward; nothing is dropped silently")
    return _run_turn(thread, cleaned, journal=journal, audit=audit,
                     executable=executable, checkout=checkout, config=config,
                     selection=selection, window_seconds=window_seconds,
                     availability=availability, runner=runner,
                     message_id_factory=message_id_factory, create=False,
                     redactions=redactions, campaigns=campaigns)


def show_thread(journal: Any, thread_id: str) -> dict[str, Any]:
    """Read one durable thread record. No provider call, no mutation."""
    return load_thread(journal, thread_id)


def close_thread(journal: Any, thread_id: str) -> dict[str, Any]:
    """Close a thread durably (CAS). Closing twice reports, never errors."""
    thread = load_thread(journal, thread_id)
    if thread.get("status") == "closed":
        return {"thread_id": thread_id, "status": "closed",
                "already_closed": True,
                "closed_at_utc": thread.get("closed_at_utc", "")}
    updated = dict(thread)
    updated["status"] = "closed"
    updated["closed_at_utc"] = to_utc_iso()
    updated["updated_at_utc"] = updated["closed_at_utc"]
    _store_thread(journal, thread, updated, create=False)
    return {"thread_id": thread_id, "status": "closed",
            "already_closed": False,
            "closed_at_utc": updated["closed_at_utc"]}


def promote_message(journal: Any, audit: Any,
                    message_id: str) -> dict[str, Any]:
    """Record the owner's explicit promotion of ONE Codex message (R240).

    The row is approval EVIDENCE, not authorization: scope changes still
    require durable directive/task capture through the existing route. The
    command surface reaching this function is owner-typed by construction
    (user-only skill + pre-model interception), so promotion is owner-gated.
    Deliberate: promotion targets a specific MESSAGE, so it works on closed
    threads too — closing a discussion never voids an owner's approval path.
    """
    if not isinstance(message_id, str) or \
            not message_id.startswith(MESSAGE_ID_PREFIX):
        raise ChannelError(
            "not_a_message_id",
            f"{message_id!r} is not a Codex message id (expected the "
            f"{MESSAGE_ID_PREFIX!r} prefix)")
    index = journal.get_state(MESSAGE_INDEX_KEY_PREFIX + message_id, None)
    if not isinstance(index, dict):
        raise ChannelError("unknown_message_id",
                           f"no Codex message has id {message_id!r}")
    thread = load_thread(journal, index["thread_id"])
    entry = next((m for m in thread.get("messages", [])
                  if m.get("message_id") == message_id), None)
    if entry is None or entry.get("role") != "codex":
        raise ChannelError("unknown_message_id",
                           f"no Codex message has id {message_id!r}")
    if entry.get("disposition") not in PROMOTABLE_DISPOSITIONS:
        raise ChannelError(
            "not_promotable",
            f"message {message_id} carries disposition "
            f"{entry.get('disposition')!r}; only "
            f"{'/'.join(PROMOTABLE_DISPOSITIONS)} messages are promotable "
            f"(R240)")
    key = PROMOTION_KEY_PREFIX + message_id
    row = {
        "schema_version": CHANNEL_SCHEMA_VERSION,
        "message_id": message_id,
        "thread_id": thread["thread_id"],
        "disposition": entry.get("disposition", ""),
        "message_digest": digest_of({"text": entry.get("text", "")}),
        "text": bound_answer(entry.get("text", "")),
        "promoted_at_utc": to_utc_iso(),
        "status": "recorded_awaiting_capture",
        "authorizes_nothing": True,
        "required_next": (
            "durable directive/task capture via /directive-compliance before "
            "any scope change (D-024-R240)"),
    }
    if journal.compare_and_swap_state(key, None, row):
        _audit(audit, "codex_channel_promoted", message_id=message_id,
               thread_id=thread["thread_id"],
               disposition=row["disposition"],
               message_digest=row["message_digest"])
        return {**row, "already_promoted": False}
    stored = journal.get_state(key, row)
    return {**stored, "already_promoted": True}
