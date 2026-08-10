"""Audit events, dependent-recalculation trigger, and downstream-honesty markers for
the survey review-action slice (M2-T016, docs/SURVEY_REVIEW_WORKFLOW.md sections 7-9).

Every review, correction, confirmation, rejection, and reopening is an append-only,
attributed, timestamped record (section 8). This module carries the ENVELOPE that ties a
review action to the shipped audit shapes it already produces — a
:class:`~app.documents.state.TransitionRecord`, a wire ``correction_history`` entry, a
wire ``professional_confirmation`` object, a
:class:`~app.documents.promotion.PromotionRefused` — rather than inventing a parallel
audit model. Every payload is METADATA ONLY (stated reasons, ids, digests, timestamps)
and safe to serialize: document bytes never appear (mirrors ``errors.py`` T11).

Two further typed values encode section-7 downstream honesty:

- :class:`DependentRecalculationRequested` — the trigger a successful accept / correct /
  reject / confirm / reopen emits so the DEPENDENT buildability calculations that consume
  the fact are rerun (section 7.1). This slice does not own the buildability recompute
  consumer; the event is the typed SEAM. ``consumer_bound`` is ``False`` until a
  recompute worker is wired in — the trigger is never silently dropped.
- :class:`DownstreamImpact` — the blocked/provisional propagation marker (section 7.2):
  an unresolved / rejected / depended-on-unconfirmed fact makes every dependent
  conclusion honestly worse-covered, expressed with the EXISTING property_profile 1.4.0
  vocabulary (``coverage_status`` ``professional_review_required`` / ``data_conflict``;
  ``status_dimensions.analysis_readiness`` ``blocked_data_conflict`` /
  ``blocked_missing_critical``). This slice CONSUMES that vocabulary as honesty signals;
  it never writes the profile and never changes the 1.4.0 contract (section 9).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime

__all__ = [
    "ANALYSIS_READINESS_BLOCKED_DATA_CONFLICT",
    "ANALYSIS_READINESS_BLOCKED_MISSING_CRITICAL",
    "COVERAGE_DATA_CONFLICT",
    "COVERAGE_PROFESSIONAL_REVIEW_REQUIRED",
    "DependentRecalculationRequested",
    "DownstreamImpact",
    "DownstreamImpactKind",
    "ReviewAuditEvent",
    "ReviewEventType",
]

# --- property_profile 1.4.0 honesty-signal vocabulary (CONSUMED, never redefined) ---
# Exact wire strings from packages/contracts/schemas/v1/coverage_status.schema.json and
# property_profile.schema.json status_dimensions.analysis_readiness. Referenced here as
# constants so a downstream profile consumer maps a DownstreamImpact onto the existing
# 1.4.0 surface without this slice importing or mutating the profile contract.
COVERAGE_PROFESSIONAL_REVIEW_REQUIRED = "professional_review_required"
COVERAGE_DATA_CONFLICT = "data_conflict"
ANALYSIS_READINESS_BLOCKED_DATA_CONFLICT = "blocked_data_conflict"
ANALYSIS_READINESS_BLOCKED_MISSING_CRITICAL = "blocked_missing_critical"

_COVERAGE_STATUSES = frozenset(
    {COVERAGE_PROFESSIONAL_REVIEW_REQUIRED, COVERAGE_DATA_CONFLICT}
)
_ANALYSIS_READINESS = frozenset(
    {
        ANALYSIS_READINESS_BLOCKED_DATA_CONFLICT,
        ANALYSIS_READINESS_BLOCKED_MISSING_CRITICAL,
    }
)


@enum.unique
class ReviewEventType(enum.Enum):
    """Closed set of auditable review actions (workflow sections 3, 8)."""

    FACT_ACCEPTED = "fact_accepted"
    FACT_CORRECTED = "fact_corrected"
    FACT_REJECTED = "fact_rejected"
    FACT_CONFIRMED = "fact_confirmed"
    DOCUMENT_CONFIRMED = "document_confirmed"
    DOCUMENT_REJECTED = "document_rejected"
    DOCUMENT_REOPENED = "document_reopened"


def _require_aware(value: object, field_name: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.tzinfo.utcoffset(value) is None
    ):
        raise ValueError(f"{field_name} must be a timezone-aware datetime, got {value!r}")
    return value


def _require_non_empty_str(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string, got {value!r}")
    return value


@dataclass(frozen=True)
class ReviewAuditEvent:
    """One append-only, attributed, timestamped review audit event (section 8).

    ``detail`` embeds the shipped audit shape(s) the action produced as JSON-safe
    metadata (a transition payload, a correction entry, a confirmation object, a
    promotion refusal) — never a parallel shape and never document bytes. Human events
    carry the acting principal's ``actor_role`` and (where the identity scheme states
    one) ``actor_id``; a professional event without ``actor_id`` is refused at
    construction — anonymous professional authority is not auditable.
    """

    event_type: ReviewEventType
    document_digest: str
    occurred_at: datetime
    actor_role: str
    actor_id: str | None = None
    evidence_id: str | None = None
    reason: str | None = None
    correlation_id: str | None = None
    detail: dict = field(default_factory=dict)

    #: Roles whose events must carry an attributed actor_id to be auditable.
    _ATTRIBUTED_ROLES = frozenset({"qualified_professional"})

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, ReviewEventType):
            raise ValueError("event_type must be a ReviewEventType member")
        _require_non_empty_str(self.document_digest, "document_digest")
        _require_aware(self.occurred_at, "occurred_at")
        _require_non_empty_str(self.actor_role, "actor_role")
        if self.actor_id is not None:
            _require_non_empty_str(self.actor_id, "actor_id")
        if self.evidence_id is not None:
            _require_non_empty_str(self.evidence_id, "evidence_id")
        if self.reason is not None:
            _require_non_empty_str(self.reason, "reason")
        if self.correlation_id is not None:
            _require_non_empty_str(self.correlation_id, "correlation_id")
        if not isinstance(self.detail, dict):
            raise ValueError("detail must be a JSON-safe metadata dict")
        if self.actor_role in self._ATTRIBUTED_ROLES and self.actor_id is None:
            raise ValueError(
                f"a {self.actor_role!r} audit event requires attributed actor_id "
                "identity evidence; anonymous professional authority is not auditable"
            )

    def to_payload(self) -> dict:
        """Structured audit payload (metadata only, JSON-serializable)."""
        return {
            "event_type": self.event_type.value,
            "document_digest": self.document_digest,
            "occurred_at": self.occurred_at.isoformat(),
            "actor_role": self.actor_role,
            "actor_id": self.actor_id,
            "evidence_id": self.evidence_id,
            "reason": self.reason,
            "correlation_id": self.correlation_id,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class DependentRecalculationRequested:
    """Typed trigger to rerun the buildability calculations that depend on a fact.

    Emitted on every accept / correct / reject / confirm / reopen that can change a
    depended-on fact's resolution state (section 7.1, 7.3): the flag on a dependent
    conclusion clears ONLY through this rerun, never by a UI dismissal. ``consumer_bound``
    stays ``False`` while the buildability recompute worker is out of this slice's scope
    — the SEAM is explicit and the trigger is never a silent no-op. ``invalidated_basis``
    names, in stable deterministic keys, which downstream computations consume the fact
    (empty tuple means "the recompute worker resolves the dependency set"); it never
    carries a fabricated value.
    """

    document_digest: str
    trigger: ReviewEventType
    requested_at: datetime
    evidence_id: str | None = None
    invalidated_basis: tuple[str, ...] = ()
    correlation_id: str | None = None
    consumer_bound: bool = False

    def __post_init__(self) -> None:
        _require_non_empty_str(self.document_digest, "document_digest")
        if not isinstance(self.trigger, ReviewEventType):
            raise ValueError("trigger must be a ReviewEventType member")
        _require_aware(self.requested_at, "requested_at")
        if self.evidence_id is not None:
            _require_non_empty_str(self.evidence_id, "evidence_id")
        if not isinstance(self.invalidated_basis, tuple) or any(
            not isinstance(key, str) or not key.strip() for key in self.invalidated_basis
        ):
            raise ValueError("invalidated_basis must be a tuple of non-empty strings")
        if self.correlation_id is not None:
            _require_non_empty_str(self.correlation_id, "correlation_id")
        if not isinstance(self.consumer_bound, bool):
            raise ValueError("consumer_bound must be a bool")

    def to_payload(self) -> dict:
        """Structured recalculation-trigger payload (metadata only, JSON-serializable)."""
        return {
            "document_digest": self.document_digest,
            "trigger": self.trigger.value,
            "requested_at": self.requested_at.isoformat(),
            "evidence_id": self.evidence_id,
            "invalidated_basis": list(self.invalidated_basis),
            "correlation_id": self.correlation_id,
            "consumer_bound": self.consumer_bound,
        }


@enum.unique
class DownstreamImpactKind(enum.Enum):
    """How an unresolved survey item propagates to a dependent conclusion (section 7.2).

    ``blocked``: the conclusion cannot be computed without the item — shown as
    "Blocked — needs survey resolution", never a fabricated value. ``provisional``: the
    conclusion is computable on a stated provisional basis, clearly labelled and linked to
    the blocking item, never presented as final.
    """

    BLOCKED = "blocked"
    PROVISIONAL = "provisional"


@dataclass(frozen=True)
class DownstreamImpact:
    """The honest downstream consequence of one or more unresolved survey items.

    Expressed with the EXISTING property_profile 1.4.0 vocabulary so a profile consumer
    maps it onto ``coverage_status`` and ``status_dimensions.analysis_readiness`` without
    a contract change. ``provenance_digest`` (+ ``provenance_evidence_ids``) is the
    joinable survey-provenance identity (section 9.2: a survey signal with no provenance
    is a defect). Never carries a computed number — it states blocked/provisional and why.
    """

    impact_kind: DownstreamImpactKind
    coverage_status: str
    reason: str
    provenance_digest: str
    provenance_evidence_ids: tuple[str, ...] = ()
    analysis_readiness: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.impact_kind, DownstreamImpactKind):
            raise ValueError("impact_kind must be a DownstreamImpactKind member")
        if self.coverage_status not in _COVERAGE_STATUSES:
            raise ValueError(
                "coverage_status must be an existing property_profile coverage status "
                f"honesty signal ({sorted(_COVERAGE_STATUSES)}); a survey item never "
                "downgrades a conclusion to 'verified'"
            )
        _require_non_empty_str(self.reason, "reason")
        _require_non_empty_str(self.provenance_digest, "provenance_digest")
        if not isinstance(self.provenance_evidence_ids, tuple) or any(
            not isinstance(e, str) or not e.strip()
            for e in self.provenance_evidence_ids
        ):
            raise ValueError("provenance_evidence_ids must be a tuple of non-empty strings")
        if self.analysis_readiness is not None and (
            self.analysis_readiness not in _ANALYSIS_READINESS
        ):
            raise ValueError(
                "analysis_readiness, when stated, must be an existing blocked "
                f"analysis-readiness signal ({sorted(_ANALYSIS_READINESS)})"
            )

    def to_payload(self) -> dict:
        """Structured downstream-impact payload (metadata only, JSON-serializable)."""
        return {
            "impact_kind": self.impact_kind.value,
            "coverage_status": self.coverage_status,
            "reason": self.reason,
            "provenance_digest": self.provenance_digest,
            "provenance_evidence_ids": list(self.provenance_evidence_ids),
            "analysis_readiness": self.analysis_readiness,
        }
