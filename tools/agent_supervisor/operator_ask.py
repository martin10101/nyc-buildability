"""The owner `ask` operation: a bounded question to the read-only Codex
supervisor (D-024 Phase F, M0-T094; R085/R087/R104).

R088 required inspecting the live CLI rather than assuming `ask` exists: the
S12.1 command surface (cli.py module docstring) has NO ask operation - this
module adds the one genuine gap. Everything security-shaped is REUSED, not
re-implemented (R018):

* the read-only Codex invocation contract - ``codex_reviewer.build_argv``
  (S2.2 flag set, ``FORBIDDEN_REVIEWER_FLAGS``, ``--sandbox read-only``,
  ``assert_argv_safe``) - so an ask can never grant mutation tools (R085);
* ``process.run`` - argv arrays only, never a shell, kill-on-close Job Object
  containment, and on timeout the WHOLE contained tree is terminated - which
  is exactly R087's "no background duplicate requests after a timeout";
* ``redaction.redact_text`` / ``redact_structure`` for secrets, and the
  durable ``queued_asks`` table (S4.3, ``models.QueuedAsk``) for the R085
  asynchronous fallback: a question the window could not answer becomes a
  durable request ID retrievable (and re-posable) later.

One attempt per window, deliberately: the ask path optimizes for a concise
answer NOW; a malformed provider output is reported as an error the owner can
re-pose (``--resubmit``), never silently retried in the background.

The audit trail records digests and sizes, not raw question/answer text
(R087: auditable but privacy-bounded).

Supervisor-freeze qualifying evidence: D-024-R104 (Phase F).
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import re
import tempfile
import uuid
from typing import Any, Callable, Mapping

from .campaign_continuity import CampaignRecordError, load as load_campaign
from .codex_reviewer import build_argv, provider_failure_reason
from .models import QueuedAsk, digest_of, to_utc_iso
from .operator_status import compose_status
from .policy import resolve_model
from .process import ProcessResult, minimal_env
from .process import run as run_process
from .redaction import redact_structure, redact_text

ASK_SCHEMA_VERSION = "1.0.0"

#: Bounded input/output (R087). A question is a question, not a document; an
#: oversized one is refused with a typed error, never truncated silently.
MAX_QUESTION_CHARS = 4_000
#: Display bound for the answer; over it the text is truncated WITH a marker.
MAX_ANSWER_DISPLAY_CHARS = 4_000
#: Hard byte bound on the state packet sent to the reviewer process.
MAX_PACKET_BYTES = 48_000
#: The short configured synchronous window (R085). Owner-overridable per call.
DEFAULT_ASK_WINDOW_SECONDS = 90.0

#: Terminal control sequences are untrusted in BOTH directions (R087): stripped
#: from the owner's question before anything persists or transmits, and from
#: the provider's answer before anything is displayed. ESC/CSI/OSC sequences
#: plus every C0 control except tab and newline.
_CONTROL_SEQ = re.compile(
    r"\x1b\[[0-9;?]*[ -/]*[@-~]"     # CSI ... final byte
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)"  # OSC ... BEL or ST
    r"|\x1b[@-_]"                    # other ESC-led C1 controls
    r"|[\x00-\x08\x0b-\x1f\x7f]")    # bare C0 controls minus \t \n

_ASK_SCHEMA_PATH = pathlib.Path(__file__).with_name("schemas") / \
    "operator_ask_answer.schema.json"

#: Marker every operator-originated durable ask id carries, so `--show` and
#: `--resubmit` can refuse loop-origin (`ask_...`) rows by name.
OPERATOR_ASK_PREFIX = "oper_"


class AskError(Exception):
    """An ask rule was violated. Always fails closed, never a partial send."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def sanitize_question(text: Any) -> tuple[str, int]:
    """Bound, strip control sequences, and redact the owner's question.

    Returns the cleaned text plus how many redactions/strips happened, so the
    caller can tell the owner their input was altered rather than doing it
    silently. UTF-8 safety: the CLI hands us ``str`` (argv is decoded by the
    interpreter); any non-string is a typed refusal, never coerced.
    """
    if not isinstance(text, str):
        raise AskError("question_not_text",
                       f"the question must be text, got {type(text).__name__}")
    stripped, control_count = _CONTROL_SEQ.subn("", text)
    stripped = stripped.strip()
    if not stripped:
        raise AskError("empty_question",
                       "an empty question cannot be answered; say what you "
                       "want to know")
    if len(stripped) > MAX_QUESTION_CHARS:
        raise AskError(
            "question_too_large",
            f"the question is {len(stripped)} characters; the bound is "
            f"{MAX_QUESTION_CHARS} (R087 bounded input). Ask the biggest "
            f"single question, not a document")
    result = redact_text(stripped)
    return str(result.value), control_count + result.count


def bound_answer(text: str) -> str:
    """Strip control sequences, redact, and bound provider text for display."""
    cleaned = _CONTROL_SEQ.sub("", text if isinstance(text, str) else "")
    cleaned = str(redact_text(cleaned).value)
    if len(cleaned) > MAX_ANSWER_DISPLAY_CHARS:
        cleaned = cleaned[:MAX_ANSWER_DISPLAY_CHARS - 15].rstrip() + \
            " ...[truncated]"
    return cleaned


def validate_identity(checkout: pathlib.Path) -> list[dict[str, Any]]:
    """Repository-root + campaign identity validation (R087, reusing the
    handoff-profile marker convention and the machine-validated campaign
    records). Returns the active campaign summaries for the packet."""
    root = pathlib.Path(checkout).resolve()
    for marker in ("CLAUDE.md", pathlib.Path("tools") / "project_control.py"):
        if not (root / marker).exists():
            raise AskError(
                "identity_mismatch",
                f"{root} does not look like the campaign repository root "
                f"(missing {marker}); ask runs only from the repo root it "
                f"reports on")
    campaigns: list[dict[str, Any]] = []
    campaigns_dir = root / "project-control" / "campaigns"
    if campaigns_dir.is_dir():
        for path in sorted(campaigns_dir.glob("*.json")):
            try:
                record = load_campaign(path)
            except CampaignRecordError as exc:
                raise AskError(
                    "campaign_record_invalid",
                    f"campaign record {path.name} failed validation "
                    f"({exc}); a tampered or malformed campaign identity is "
                    f"never sent onward") from exc
            if record.state == "active":
                campaigns.append({
                    "campaign_id": record.campaign_id,
                    "sequence": record.sequence,
                    "next_task_id": record.next_action.get("task_id", ""),
                })
    return campaigns


def build_ask_packet(journal: Any, *, checkout: pathlib.Path, question: str,
                     campaigns: list[dict[str, Any]]) -> dict[str, Any]:
    """The bounded current-state packet (R085): question + labeled durable
    facts, redacted, with a hard byte ceiling that fails closed."""
    facts = redact_structure(compose_status(journal, checkout=checkout)).value
    packet = {
        "schema_version": ASK_SCHEMA_VERSION,
        "kind": "operator_ask",
        "question": question,
        "campaigns": campaigns,
        "state": facts,
        "instruction": (
            "You are the read-only Codex supervisor. Answer the owner's "
            "question concisely using ONLY this packet and read-only "
            "repository evidence. Return exactly one object matching the "
            "operator_ask_answer schema. Say 'unknown from the provided "
            "state' rather than inventing a fact."),
    }
    size = len(json.dumps(packet, ensure_ascii=False).encode("utf-8"))
    if size > MAX_PACKET_BYTES:
        # Drop the bulkiest sections first, visibly, then re-check.
        state = dict(packet["state"])
        dropped = [k for k in ("recent_transitions", "subagents", "current_task")
                   if k in state]
        for key in dropped:
            state[key] = {"value": "omitted", "source": "packet size bound",
                          "confidence": "unknown"}
        packet["state"] = state
        packet["omitted_for_size"] = dropped
        size = len(json.dumps(packet, ensure_ascii=False).encode("utf-8"))
        if size > MAX_PACKET_BYTES:
            raise AskError(
                "packet_too_large",
                f"the state packet is {size} bytes after trimming; the bound "
                f"is {MAX_PACKET_BYTES}. Refusing to send an unbounded "
                f"payload (R087)")
    return packet


def validate_answer(raw: Any) -> dict[str, str]:
    """Validate + bound the provider's answer object. Typed failure, no echo."""
    if not isinstance(raw, Mapping):
        raise AskError("answer_not_object",
                       "the provider returned no schema-valid answer object")
    answer = raw.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise AskError("answer_empty",
                       "the provider's answer field is empty or not text")
    note = raw.get("confidence_note", "")
    refs = raw.get("evidence_refs", [])
    if not isinstance(refs, list) or any(not isinstance(r, str) for r in refs):
        refs = []
    return {
        "answer": bound_answer(answer),
        "confidence_note": bound_answer(note if isinstance(note, str) else ""),
        "evidence_refs": ", ".join(bound_answer(r) for r in refs[:8]),
    }


@dataclasses.dataclass(frozen=True)
class AskOutcome:
    """One ask attempt: a concise answer, a durable request id, or an error."""

    answered: bool
    question_digest: str
    model_used: str = ""
    answer: str = ""
    confidence_note: str = ""
    evidence_refs: str = ""
    request_id: str = ""
    timed_out: bool = False
    tree_terminated: bool = False
    error_code: str = ""
    error_message: str = ""
    redactions: int = 0

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _read_answer_file(output_path: str, result: ProcessResult) -> Any:
    """The decision file, else stdout ONLY when no provider failure event -
    the same rule as ``CodexReviewer._invoke`` (a `turn.failed` payload must
    never be mistaken for an answer)."""
    path = pathlib.Path(output_path)
    text = path.read_text(encoding="utf-8-sig").strip() if path.exists() else ""
    if not text:
        stdout_text = result.stdout.strip()
        if stdout_text and not provider_failure_reason(stdout_text):
            text = stdout_text
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, Mapping) else None


def _audit(audit: Any, event: str, **detail: Any) -> None:
    if audit is not None:
        audit.append(event, detail=dict(detail))


def run_ask(
    question: str,
    *,
    journal: Any,
    audit: Any,
    executable: str,
    checkout: pathlib.Path,
    config: Any,
    selection: Any,
    window_seconds: float = DEFAULT_ASK_WINDOW_SECONDS,
    availability: Callable[[str], bool] | None = None,
    runner: Callable[..., ProcessResult] | None = None,
    ask_id_factory: Callable[[], str] | None = None,
    existing_request_id: str = "",
) -> AskOutcome:
    """One bounded synchronous ask window (R085/R087).

    On timeout the contained process tree is already terminated by
    ``process.run`` and the question becomes (or, on resubmit, remains) ONE
    durable request row - never a background duplicate (R087).
    """
    cleaned, redactions = sanitize_question(question)
    campaigns = validate_identity(checkout)
    if not (0 < float(window_seconds) <= 3600):
        raise AskError("bad_window",
                       f"window_seconds must be in (0, 3600], got "
                       f"{window_seconds!r}")

    resolution = resolve_model("codex", config=config, selection=selection,
                               availability=availability, role="primary",
                               purpose="operator_ask")
    packet = build_ask_packet(journal, checkout=checkout, question=cleaned,
                              campaigns=campaigns)
    question_digest = digest_of({"question": cleaned})
    if not resolution.usable:
        return AskOutcome(answered=False, question_digest=question_digest,
                          error_code=resolution.reason_code,
                          error_message=resolution.reason,
                          redactions=redactions)

    run = runner or run_process
    handle, output_path = tempfile.mkstemp(prefix="operator_ask_", suffix=".json")
    os.close(handle)
    try:
        argv = build_argv(executable, repo=str(checkout),
                          model=resolution.model,
                          schema_path=str(_ASK_SCHEMA_PATH),
                          output_path=output_path)
        result = run(argv, cwd=str(checkout), env=minimal_env(),
                     timeout=float(window_seconds),
                     input_text=json.dumps(packet, ensure_ascii=False))
        if result.timed_out:
            if existing_request_id:
                request_id = existing_request_id
            else:
                make_id = ask_id_factory or \
                    (lambda: OPERATOR_ASK_PREFIX + uuid.uuid4().hex[:16])
                request_id = make_id()
                journal.queue_ask(QueuedAsk(
                    ask_id=request_id, run_id="operator", task_id="",
                    question=cleaned, request_digest=question_digest,
                    created_at_utc=to_utc_iso(),
                    classification="operator_ask"))
            _audit(audit, "operator_ask_timeout",
                   request_id=request_id, question_digest=question_digest,
                   window_seconds=float(window_seconds),
                   tree_terminated=result.tree_terminated,
                   resubmit=bool(existing_request_id))
            return AskOutcome(answered=False, question_digest=question_digest,
                              model_used=resolution.model,
                              request_id=request_id, timed_out=True,
                              tree_terminated=result.tree_terminated,
                              redactions=redactions)
        raw = _read_answer_file(output_path, result)
        try:
            if raw is None:
                raise AskError(
                    "no_answer",
                    f"the reviewer process exited {result.returncode} with no "
                    f"schema-valid answer object")
            fields = validate_answer(raw)
        except AskError as exc:
            _audit(audit, "operator_ask_failed",
                   question_digest=question_digest, error_code=exc.code,
                   returncode=result.returncode)
            return AskOutcome(answered=False, question_digest=question_digest,
                              model_used=resolution.model,
                              error_code=exc.code, error_message=exc.message,
                              redactions=redactions)
        _audit(audit, "operator_ask_answered",
               question_digest=question_digest,
               answer_digest=digest_of(fields), model=resolution.model,
               answer_chars=len(fields["answer"]))
        if existing_request_id:
            journal.resolve_ask(existing_request_id,
                                json.dumps(fields, ensure_ascii=False))
        return AskOutcome(answered=True, question_digest=question_digest,
                          model_used=resolution.model,
                          answer=fields["answer"],
                          confidence_note=fields["confidence_note"],
                          evidence_refs=fields["evidence_refs"],
                          request_id=existing_request_id,
                          redactions=redactions)
    finally:
        try:
            os.unlink(output_path)
        except OSError:  # pragma: no cover - defensive
            pass


def show_ask(journal: Any, request_id: str) -> dict[str, Any]:
    """Read one durable operator ask record verbatim (R085 'retrievable
    later'). Refuses loop-origin ids by name - those belong to the broker."""
    if not request_id.startswith(OPERATOR_ASK_PREFIX):
        raise AskError("not_an_operator_ask",
                       f"{request_id!r} is not an operator ask id "
                       f"(expected the {OPERATOR_ASK_PREFIX!r} prefix)")
    record = journal.ask_by_id(request_id)
    if record is None:
        raise AskError("unknown_request_id",
                       f"no durable ask row has id {request_id!r}")
    return record.to_dict()


def resubmit_ask(request_id: str, **kwargs: Any) -> AskOutcome:
    """Re-pose the EXACT recorded question in one new bounded window.

    The durable row keeps its identity: an answer resolves it in place, a
    second timeout leaves the same single row - no duplicate request either
    way (R087)."""
    journal = kwargs["journal"]
    record_dict = show_ask(journal, request_id)
    if record_dict.get("answered_at_utc"):
        raise AskError("already_answered",
                       f"{request_id} was answered at "
                       f"{record_dict['answered_at_utc']}; use --show to read "
                       f"it")
    return run_ask(record_dict["question"], existing_request_id=request_id,
                   **kwargs)
