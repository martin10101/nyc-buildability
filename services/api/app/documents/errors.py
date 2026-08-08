"""Typed errors for the survey / official-document ingestion module.

Every refusal in this module is a typed error with a machine-readable ``reject_code`` and
a structured payload safe to serialize into an API response or audit record. Payloads
carry metadata only — document bytes never appear in errors, logs, or audit records
(docs/UPLOAD_THREAT_MODEL.md T11).
"""

from __future__ import annotations

__all__ = [
    "DigestMismatchError",
    "DocumentIngestionError",
    "ExtensionMismatchError",
    "FormatDeferredError",
    "IllegalTransitionError",
    "ImmutableOriginalViolationError",
    "InvalidDigestKeyError",
    "InvalidTargetBblError",
    "InvalidUploadMetadataError",
    "OriginalNotFoundError",
    "StorageIntegrityError",
    "TransitionReasonRequiredError",
    "UnauthorizedTransitionActorError",
    "UnsafeTempPathError",
    "UnsupportedExtensionError",
    "UploadRejectedError",
    "UploadTooLargeError",
]


class DocumentIngestionError(Exception):
    """Base class for every typed failure of the ingestion module.

    ``reject_code`` is the stable machine identifier of the defect class; ``payload``
    carries the structured detail (metadata only, never document bytes).
    """

    reject_code = "document_ingestion_error"

    def __init__(self, message: str, **payload: object) -> None:
        super().__init__(message)
        self.message = message
        self.payload = dict(payload)

    def to_payload(self) -> dict:
        """Structured error payload. Never includes a stack trace or document bytes."""
        return {
            "reject_code": self.reject_code,
            "message": self.message,
            **self.payload,
        }


# --------------------------------------------------------------------------- S1 gate


class UploadRejectedError(DocumentIngestionError):
    """Base class for S1 synchronous upload-gate refusals (architecture section 2, S1)."""

    reject_code = "upload_rejected"


class InvalidTargetBblError(UploadRejectedError):
    """Target BBL (upload *intent* — contract section 4.1) failed canonical validation."""

    reject_code = "invalid_target_bbl"


class InvalidUploadMetadataError(UploadRejectedError):
    """A required upload metadata field (filename, declared class) is missing/malformed."""

    reject_code = "invalid_upload_metadata"


class UnsupportedExtensionError(UploadRejectedError):
    """Declared extension names no supported upload format (format policy matrix)."""

    reject_code = "unsupported_extension"


class FormatDeferredError(UploadRejectedError):
    """DXF/DWG upload refused per format policy rows 6-7, with the stated alternative.

    Not a generic rejection: the payload carries the policy's steering guidance
    (export a vector PDF; DXF conversion requires a future validated stage).
    """

    reject_code = "format_deferred"


class UploadTooLargeError(UploadRejectedError):
    """Stream size cap tripped before durable storage (threat T03); no record is created."""

    reject_code = "upload_too_large"


class ExtensionMismatchError(UploadRejectedError):
    """Sniffed content does not match the declared extension (threats T01/T02).

    The declared extension never selects handling — the sniffed type does; a file whose
    bytes do not carry the declared format's signature is rejected typed, including the
    executable-renamed-to-.pdf and HTML-renamed-to-.tiff vectors.
    """

    reject_code = "extension_mismatch"


# ----------------------------------------------------------------- state machine


class IllegalTransitionError(DocumentIngestionError):
    """Requested document state transition is not in the section-4 transition table."""

    reject_code = "illegal_transition"


class UnauthorizedTransitionActorError(DocumentIngestionError):
    """Transition actor is malformed or its kind lacks authority for this transition.

    The actor-kind enum is closed and contains no AI member: there is no path for AI to
    trigger, veto, or propose a transition (architecture section 4).
    """

    reject_code = "unauthorized_transition_actor"


class TransitionReasonRequiredError(DocumentIngestionError):
    """This transition requires a stated reason (typed rejection / audited reopening)."""

    reject_code = "transition_reason_required"


# ------------------------------------------------------------------------ storage


class StorageIntegrityError(DocumentIngestionError):
    """Content-addressing integrity violation in the original-document store."""

    reject_code = "storage_integrity_error"


class DigestMismatchError(StorageIntegrityError):
    """Stored bytes no longer hash to their recorded digest (architecture section 6).

    A typed integrity failure that halts processing and surfaces a blocker —
    never auto-repair.
    """

    reject_code = "digest_mismatch"


class ImmutableOriginalViolationError(StorageIntegrityError):
    """Attempt to overwrite a stored original with different bytes (threat T10)."""

    reject_code = "immutable_original_violation"


class InvalidDigestKeyError(StorageIntegrityError):
    """Digest key is not ``sha256:<64 hex>``; refused before any filesystem interaction."""

    reject_code = "invalid_digest_key"


class OriginalNotFoundError(DocumentIngestionError):
    """No stored original exists under the requested digest."""

    reject_code = "original_not_found"


# --------------------------------------------------------------------- temp paths


class UnsafeTempPathError(DocumentIngestionError):
    """Temp-path safety validation failed (threats T07/T11).

    ``payload['violation']`` names the exact failed condition; a candidate failing any
    condition is never deleted or used — it is a typed anomaly.
    """

    reject_code = "unsafe_temp_path"
