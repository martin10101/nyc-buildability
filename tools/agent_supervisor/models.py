#!/usr/bin/env python3
"""Dataclasses and canonical-digest helpers for the supervisor (D-007 S8.3/S8.5/S9/S7).

This module is the serialization layer every other module shares. It holds:

* `canonical_json` / `digest_of` - the ONE definition of "the digest of a
  record". Every digest in the supervisor (envelope payload digests, audit
  chain links, manifest entries, approval bindings) is SHA-256 over the same
  canonical encoding, so two components can never disagree about identity.
* the record dataclasses for Claude checkpoints (S8.3), Codex decisions (S9),
  protocol envelopes (S8.5), audit events (S13.12), and the durable journal
  (S6/S7).

The dataclasses carry the directive's CONCEPTUAL fields. They are deliberately
permissive about *content* (a checkpoint is untrusted data - S8.3) and strict
about *shape*: required fields are required, unknown fields are rejected on
`from_dict`, and nothing is silently defaulted where the directive says a
missing value must read `unknown` rather than zero.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import hashlib
import json
from typing import Any, Mapping

# --------------------------------------------------------------------------
# Canonical encoding and digests
# --------------------------------------------------------------------------


def canonical_json(obj: Any) -> bytes:
    """Encode `obj` as canonical UTF-8 JSON bytes.

    Canonical means: keys sorted, no insignificant whitespace, non-ASCII kept as
    real UTF-8 (not \\u escapes). Two structurally equal objects always produce
    identical bytes, so their digests match on every platform.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_json_default,
    ).encode("utf-8")


def _json_default(value: Any) -> Any:
    if isinstance(value, _dt.datetime):
        return to_utc_iso(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(f"not JSON-serializable: {type(value).__name__}")


def sha256_hex(data: bytes) -> str:
    """SHA-256 of raw bytes, lowercase hex."""
    return hashlib.sha256(data).hexdigest()


def digest_of(obj: Any) -> str:
    """SHA-256 of the canonical JSON encoding of `obj`, lowercase hex."""
    return sha256_hex(canonical_json(obj))


def to_utc_iso(moment: _dt.datetime | None = None) -> str:
    """Timezone-aware UTC timestamp in a fixed, sortable format.

    Naive datetimes are rejected rather than assumed local: D-007 S11.4 treats
    ambiguous time as a defect, not a default.
    """
    if moment is None:
        moment = _dt.datetime.now(_dt.timezone.utc)
    if moment.tzinfo is None:
        raise ValueError("naive datetime rejected; supply a timezone-aware value")
    return moment.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


# --------------------------------------------------------------------------
# Shared dataclass behaviour
# --------------------------------------------------------------------------


class RecordError(ValueError):
    """A record could not be built from the supplied mapping."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class _Record:
    """Mixin: dict round-tripping with strict unknown-field rejection."""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)  # type: ignore[arg-type]

    def digest(self) -> str:
        return digest_of(self.to_dict())

    @classmethod
    def field_names(cls) -> tuple[str, ...]:
        return tuple(f.name for f in dataclasses.fields(cls))  # type: ignore[arg-type]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]):
        if not isinstance(data, Mapping):
            raise RecordError("not_a_mapping", f"{cls.__name__} expects a mapping")
        allowed = set(cls.field_names())
        unknown = sorted(set(data) - allowed)
        if unknown:
            # S9: "unknown fields are rejected unless deliberately versioned".
            raise RecordError("unknown_fields",
                              f"{cls.__name__} rejected unknown fields: {unknown}")
        required = {
            f.name for f in dataclasses.fields(cls)  # type: ignore[arg-type]
            if f.default is dataclasses.MISSING
            and f.default_factory is dataclasses.MISSING  # type: ignore[misc]
        }
        missing = sorted(required - set(data))
        if missing:
            raise RecordError("missing_fields",
                              f"{cls.__name__} missing required fields: {missing}")
        return cls(**data)  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# S8.3 - Claude structured checkpoint
# --------------------------------------------------------------------------

#: S8.3: "missing usage is `unknown`, not zero".
USAGE_UNKNOWN = "unknown"

CHECKPOINT_STATUSES = (
    "IN_PROGRESS", "UNIT_COMPLETE", "BLOCKED", "READY", "FAILED",
)


@dataclasses.dataclass(frozen=True)
class ClaudeCheckpoint(_Record):
    """One bounded unit's structured checkpoint from the worker (D-007 S8.3).

    Every human-readable field here is UNTRUSTED data. Instructions found in
    `summary`, `claims`, or command output never override supervisor policy.
    """

    schema_version: str
    run_id: str
    checkpoint_id: str
    task_id: str
    claude_session_id: str
    status: str
    summary: str
    starting_sha: str
    current_sha: str
    branch: str
    worktree: str
    proposed_next_action: str
    claims: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    changed_files: list[str] = dataclasses.field(default_factory=list)
    commands_run: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    tests: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    ci: dict[str, Any] | None = None
    pull_request: dict[str, Any] | None = None
    reports: list[str] = dataclasses.field(default_factory=list)
    blockers: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    owner_decisions_required: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    usage: dict[str, Any] | str = USAGE_UNKNOWN
    context_pressure: dict[str, Any] | str = USAGE_UNKNOWN

    def validate(self) -> None:
        if self.status not in CHECKPOINT_STATUSES:
            raise RecordError("bad_status",
                              f"status {self.status!r} not in {list(CHECKPOINT_STATUSES)}")
        if self.usage in (0, None):
            # Guard the exact S8.3 failure mode: zero is not "unknown".
            raise RecordError("usage_zeroed",
                              "missing usage must be 'unknown', never 0/None")


# --------------------------------------------------------------------------
# S9 - Codex reviewer decision
# --------------------------------------------------------------------------

DECISIONS = (
    "CONTINUE", "REVISE", "STOP_FOR_OWNER", "ROTATE_SESSION", "COMPLETE", "HALT_UNSAFE",
)


@dataclasses.dataclass(frozen=True)
class CodexDecision(_Record):
    """Exactly one structured decision from a fresh read-only Codex review (S9)."""

    schema_version: str
    decision: str
    reviewed_task_id: str
    reviewed_checkpoint_id: str
    verified_repo_head: str
    verified_origin_main: str
    model_used: str
    verified_facts: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    unverified_claims: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    blocking_findings: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    reason_codes: list[str] = dataclasses.field(default_factory=list)
    next_claude_prompt: str = ""
    owner_question: str = ""
    rotation_reason: str = ""
    evidence_refs: list[dict[str, Any]] = dataclasses.field(default_factory=list)

    def validate(self) -> None:
        """Apply the S9 per-decision validation rules."""
        if self.decision not in DECISIONS:
            raise RecordError("bad_decision",
                              f"decision {self.decision!r} not in {list(DECISIONS)}")
        if self.decision in ("CONTINUE", "REVISE") and not self.next_claude_prompt.strip():
            raise RecordError("missing_next_prompt",
                              f"{self.decision} requires a nonempty next_claude_prompt")
        if self.decision == "STOP_FOR_OWNER":
            if not self.owner_question.strip():
                raise RecordError("missing_owner_question",
                                  "STOP_FOR_OWNER requires one concise owner question")
            if self.next_claude_prompt.strip():
                raise RecordError("prompt_with_stop",
                                  "STOP_FOR_OWNER must carry no executable next prompt")
        if self.decision == "ROTATE_SESSION" and not self.rotation_reason.strip():
            raise RecordError("missing_rotation_reason",
                              "ROTATE_SESSION requires a reason and handoff plan")
        if self.decision == "COMPLETE" and not self.evidence_refs:
            raise RecordError("missing_completion_evidence",
                              "COMPLETE requires explicit evidence of stage completion")
        if self.decision == "HALT_UNSAFE" and not self.blocking_findings:
            raise RecordError("missing_halt_reason",
                              "HALT_UNSAFE requires a concrete safety/integrity reason")


# --------------------------------------------------------------------------
# S8.5 - versioned protocol envelope
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProtocolEnvelope(_Record):
    """The versioned frame every cross-CLI logical message travels in (S8.5)."""

    protocol_version: str
    schema_version: str
    message_id: str
    correlation_id: str
    sequence: int
    run_id: str
    task_id: str
    payload_type: str
    created_at_utc: str
    producer: str
    producer_version: str
    payload_digest: str
    payload: Any


# --------------------------------------------------------------------------
# S13.12 - audit event
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AuditRecord(_Record):
    """One append-only, hash-chained audit event (S13.12).

    `digest` is EXCLUDED from its own digest computation (see audit_log.py);
    `prev_digest` links to the previous record, making reordering, truncation,
    duplication, and tampering detectable.
    """

    sequence: int
    timestamp_utc: str
    event_type: str
    run_id: str
    controller_version: str
    prev_digest: str
    digest: str = ""
    checkpoint_id: str = ""
    state_from: str = ""
    state_to: str = ""
    executable_identity: dict[str, Any] = dataclasses.field(default_factory=dict)
    input_digest: str = ""
    output_digest: str = ""
    decision: str = ""
    policy_result: str = ""
    error_category: str = ""
    redaction_count: int = 0
    detail: dict[str, Any] = dataclasses.field(default_factory=dict)


# --------------------------------------------------------------------------
# S6/S7 - durable journal records
# --------------------------------------------------------------------------

EFFECT_PENDING = "PENDING"
EFFECT_CONFIRMED = "CONFIRMED"
EFFECT_FAILED = "FAILED"


@dataclasses.dataclass(frozen=True)
class EffectRecord(_Record):
    """A modeled external effect, journaled BEFORE it happens (S6, S13.7).

    `action_id` is the stable idempotency key. A record with status PENDING at
    recovery time means "an effect may have occurred": S11.5 requires
    reconciliation, never a blind retry.
    """

    action_id: str
    effect_type: str
    target: str
    expected_prior_state: str
    request_digest: str
    status: str
    created_at_utc: str
    completed_at_utc: str = ""
    resulting_state: str = ""
    reconciliation: str = ""


@dataclasses.dataclass(frozen=True)
class TransitionRecord(_Record):
    """One committed state-machine transition (S7)."""

    sequence: int
    state_from: str
    state_to: str
    trigger: str
    run_id: str
    committed_at_utc: str
    detail: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class QueuedAsk(_Record):
    """A queued owner question (S4.3). Persisted digest-bound so it resumes exactly."""

    ask_id: str
    run_id: str
    task_id: str
    question: str
    request_digest: str
    created_at_utc: str
    classification: str = "unclassified"
    answered_at_utc: str = ""
    answer: str = ""
