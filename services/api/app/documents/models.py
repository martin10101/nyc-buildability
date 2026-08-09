"""Typed domain models for the document ingestion record and its per-fact evidence link.

The :class:`DocumentIngestionRecord` carries exactly the DOCUMENT-level provenance the
survey-evidence contract deliberately does not duplicate per fact (contract section 2:
original filename, uploader, upload timestamp, declared document class, server-sniffed
MIME type, size, storage location, conversion lineage), plus the lifecycle state owned
by the ``state.py`` state machine. The :class:`DocumentEvidenceLink` is the per-fact
join between one ``survey_evidence`` record and its document, by the immutable
original-bytes digest (contract section 3).

B-001 honesty: production private-object storage is unprovisioned (no bucket, no
credentials, no migration), so NOTHING here binds to storage. ``document_ref`` and
``storage_ref`` exist as optional, default-``None`` fields precisely because the ids
they would carry do not exist yet; the ``sha256:`` digest of the exact original uploaded
bytes — not any ref — is the content identity, and these models stay complete without
either ref (mirrors the contract's optional ``document_ref``).

Models are immutable value records validated at construction (``ValueError`` /
``TypeError`` on malformed fields); lifecycle refusals stay typed in ``state.py``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime

from app.documents.state import (
    INITIAL_STATE,
    DocumentState,
    TransitionActor,
    TransitionRecord,
    transition,
)

__all__ = [
    "BBL_PATTERN",
    "RAW_BYTES_DIGEST_PATTERN",
    "ConversionRecord",
    "DocumentEvidenceLink",
    "DocumentIngestionRecord",
]

#: ``sha256:`` + 64 LOWERCASE hex over the EXACT RAW BYTES — verbatim the contract's
#: ``$defs/raw_bytes_digest_sha256`` pattern (deliberately not the canonical-JSON digest
#: of common.schema.json: an uploaded document has no canonical JSON form).
RAW_BYTES_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

#: 10-digit NYC BBL, first digit borough 1-5 — verbatim ``common.schema.json#/$defs/bbl``.
BBL_PATTERN = re.compile(r"^[1-5][0-9]{5}[0-9]{4}$")


def _require_non_empty_str(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string, got {value!r}")
    return value


def _require_optional_non_empty_str(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_non_empty_str(value, field_name)


def _require_raw_bytes_digest(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not RAW_BYTES_DIGEST_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} must match 'sha256:' + 64 lowercase hex "
            f"(raw-bytes digest of the exact original upload), got {value!r}"
        )
    return value


def _require_aware(value: object, field_name: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.tzinfo.utcoffset(value) is None
    ):
        raise ValueError(f"{field_name} must be a timezone-aware datetime, got {value!r}")
    return value


@dataclass(frozen=True)
class ConversionRecord:
    """Tool-and-version lineage of ONE validated conversion producing a derivative.

    No validated conversion stage exists yet (format policy rows 6-7 are deferred), so
    every current record has an empty lineage; the type exists because conversion
    lineage is document-level provenance (architecture section 1 item 4) and the format
    policy requires any future conversion to record tool + version. The derivative gets
    its own digest; ``document_digest`` always stays the ORIGINAL upload's digest.
    """

    tool_name: str
    tool_version: str
    derivative_digest: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.tool_name, "tool_name")
        _require_non_empty_str(self.tool_version, "tool_version")
        _require_raw_bytes_digest(self.derivative_digest, "derivative_digest")


@dataclass(frozen=True)
class DocumentIngestionRecord:
    """Document-level provenance + lifecycle state of one uploaded original.

    ``document_digest`` is the immutable content identity of the exact original
    uploaded bytes, shared by every ``survey_evidence`` fact of the document and stable
    across any storage migration. ``target_bbl`` is upload INTENT, never a verified
    association (the per-fact ``address_bbl_match`` check records whether the document
    actually pertains to it). ``declared_mime_type`` is recorded but never trusted;
    ``sniffed_mime_type`` is what the server determined from the bytes.

    ``state_history`` is the append-only audit chain: it must replay from ``uploaded``
    to the current ``state`` with each record's ``from_state`` equal to its
    predecessor's ``to_state`` — a record whose history does not reproduce its state is
    refused at construction. Evolve records only via :meth:`apply_transition`.
    """

    document_digest: str
    target_bbl: str
    original_filename: str
    declared_document_class: str
    sniffed_mime_type: str
    size_bytes: int
    uploaded_at: datetime
    declared_mime_type: str | None = None
    uploaded_by: str | None = None
    state: DocumentState = INITIAL_STATE
    state_history: tuple[TransitionRecord, ...] = ()
    document_ref: str | None = None
    storage_ref: str | None = None
    conversion_lineage: tuple[ConversionRecord, ...] = ()

    def __post_init__(self) -> None:
        _require_raw_bytes_digest(self.document_digest, "document_digest")
        if not isinstance(self.target_bbl, str) or not BBL_PATTERN.fullmatch(self.target_bbl):
            raise ValueError(
                f"target_bbl must be a 10-digit NYC BBL (borough 1-5), got {self.target_bbl!r}"
            )
        _require_non_empty_str(self.original_filename, "original_filename")
        _require_non_empty_str(self.declared_document_class, "declared_document_class")
        _require_non_empty_str(self.sniffed_mime_type, "sniffed_mime_type")
        if not isinstance(self.size_bytes, int) or isinstance(self.size_bytes, bool):
            raise ValueError(f"size_bytes must be an int, got {self.size_bytes!r}")
        if self.size_bytes < 1:
            raise ValueError("size_bytes must be >= 1: a zero-byte upload is not a document")
        _require_aware(self.uploaded_at, "uploaded_at")
        _require_optional_non_empty_str(self.declared_mime_type, "declared_mime_type")
        _require_optional_non_empty_str(self.uploaded_by, "uploaded_by")
        _require_optional_non_empty_str(self.document_ref, "document_ref")
        _require_optional_non_empty_str(self.storage_ref, "storage_ref")
        if not isinstance(self.state, DocumentState):
            raise ValueError(f"state must be a DocumentState member, got {self.state!r}")
        if not isinstance(self.state_history, tuple):
            raise ValueError("state_history must be a tuple of TransitionRecord")
        for entry in self.state_history:
            if not isinstance(entry, TransitionRecord):
                raise ValueError(f"state_history entries must be TransitionRecord, got {entry!r}")
        self._validate_history_chain()
        if not isinstance(self.conversion_lineage, tuple):
            raise ValueError("conversion_lineage must be a tuple of ConversionRecord")
        for entry in self.conversion_lineage:
            if not isinstance(entry, ConversionRecord):
                raise ValueError(
                    f"conversion_lineage entries must be ConversionRecord, got {entry!r}"
                )

    def _validate_history_chain(self) -> None:
        if not self.state_history:
            if self.state is not INITIAL_STATE:
                raise ValueError(
                    f"a record with no transition history must be in "
                    f"{INITIAL_STATE.value!r}, got {self.state.value!r}: states are "
                    "never skipped and history is never dropped"
                )
            return
        expected_from = INITIAL_STATE
        for entry in self.state_history:
            if entry.from_state is not expected_from:
                raise ValueError(
                    f"broken state_history chain: transition "
                    f"{entry.from_state.value!r} -> {entry.to_state.value!r} does not "
                    f"start at {expected_from.value!r}"
                )
            expected_from = entry.to_state
        if expected_from is not self.state:
            raise ValueError(
                f"state_history replays to {expected_from.value!r} but state is "
                f"{self.state.value!r}"
            )

    def apply_transition(
        self,
        to: DocumentState,
        *,
        actor: TransitionActor,
        occurred_at: datetime,
        reason: str | None = None,
    ) -> DocumentIngestionRecord:
        """Return a new record advanced along one table edge, with the audit entry appended.

        Delegates every check to :func:`app.documents.state.transition` — the state
        machine, not this model, is the transition authority; the same typed errors
        propagate unchanged.
        """
        record = transition(self.state, to, actor=actor, occurred_at=occurred_at, reason=reason)
        return replace(
            self,
            state=record.to_state,
            state_history=(*self.state_history, record),
        )


@dataclass(frozen=True)
class DocumentEvidenceLink:
    """Per-fact join between one ``survey_evidence`` record and its source document.

    ``evidence_id`` cites the fact (contract section 4.1); ``document_digest`` is the
    join key to the document record while B-001 blocks platform storage ids (the
    contract's optional ``document_ref`` becomes usable only after B-001 clears);
    ``page_number`` is the 1-based page of the ORIGINAL document so a reviewer can open
    the exact page of the immutable original; ``extraction_run_id`` groups the facts of
    one isolated extraction run and is optional exactly as in the contract.
    """

    evidence_id: str
    document_digest: str
    page_number: int
    extraction_run_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.evidence_id, "evidence_id")
        _require_raw_bytes_digest(self.document_digest, "document_digest")
        if not isinstance(self.page_number, int) or isinstance(self.page_number, bool):
            raise ValueError(f"page_number must be an int, got {self.page_number!r}")
        if self.page_number < 1:
            raise ValueError("page_number is 1-based and must be >= 1")
        _require_optional_non_empty_str(self.extraction_run_id, "extraction_run_id")

    def belongs_to(self, record: DocumentIngestionRecord) -> bool:
        """True when this fact link and ``record`` share one original-bytes digest."""
        return self.document_digest == record.document_digest
