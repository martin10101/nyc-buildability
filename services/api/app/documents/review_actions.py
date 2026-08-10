"""Survey review-action handlers — the disclosed backend slice (M2-T016, Packet C).

The typed, server-authorized action surface the review UI builds against
(docs/SURVEY_REVIEW_WORKFLOW.md section 12). Each handler:

1. AUTHORIZES the channel-authenticated principal for the action
   (:mod:`app.documents.review_authz`, workflow section 5.2) — fail-closed, server-side,
   independent of what the UI offered;
2. VALIDATES against the shipped deterministic validators (correction-history integrity,
   professional-confirmation evidence, promotion) — never re-implementing them;
3. TRANSITIONS the document only through
   :func:`app.documents.state.promotion_gated_transition` — the H5 gate wrapper — so the
   three evidence-promoting edges keep their deterministic precondition; raw
   :func:`app.documents.state.transition` is authority-only and is NEVER called here;
4. APPENDS corrections (never overwrites the immutable original or an accepted entry);
5. EMITS the append-only audit event(s) and the dependent-recalculation trigger
   (:mod:`app.documents.review_events`).

Immutability is contract-level (SC-S2): a correction changes ``normalized_value`` /
``units`` only and is one APPEND to ``correction_history``; the immutable original bytes
and each fact's ``original_value`` are never written. The read view returns the original
baseline side by side with the correction chain.

No automatic path to ``professionally_confirmed`` (SC-S3/SC-S4): the per-fact promotion
verdicts the H5 gate consumes are COMPUTED SERVER-SIDE by the store from stored
deterministic results (:meth:`ReviewStore.promotion_verdict`) — a client can never submit
a forged ``PromotionAllowed``, and no confidence/AI value can substitute (proven by
``promotion.py``). Confirmation is reachable only through the professional role past the
gate.

Storage/auth are B-001-honest: handlers depend only on the :class:`ReviewStore`
abstraction (a single in-process test/CI implementation lives in the tests). No bucket,
no credential, no production identity is assumed; the ``sha256:`` document digest is the
content identity and ``actor_id`` stays optional at the wire.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Protocol, runtime_checkable

from app.documents.correction_history import (
    NormalizationBaseline,
    OriginalValueReference,
    ProfessionalConfirmationState,
    UnresolvedCorrectionHistory,
    ValidatedProfessionalConfirmation,
    validate_correcting_actor,
    validate_correction_history,
    validate_history_extension,
    validate_professional_confirmation,
)
from app.documents.errors import DocumentIngestionError
from app.documents.models import DocumentIngestionRecord
from app.documents.promotion import PromotionAllowed, PromotionRefused, PromotionVerdict
from app.documents.review_authz import ReviewAction, authorize_review_action
from app.documents.review_events import (
    COVERAGE_DATA_CONFLICT,
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
    DependentRecalculationRequested,
    DownstreamImpact,
    DownstreamImpactKind,
    ReviewAuditEvent,
    ReviewEventType,
)
from app.documents.state import (
    ActorKind,
    DocumentState,
    TransitionActor,
    TransitionRecord,
    promotion_gated_transition,
)

__all__ = [
    "CORRECTION_TRIGGER_ACTOR_ID",
    "AcceptFactRequest",
    "ConcurrentReviewModification",
    "ConfirmDocumentRequest",
    "ConfirmationRejected",
    "CorrectFactRequest",
    "CorrectionRejected",
    "DocumentRecordNotFound",
    "DocumentReviewView",
    "FactNotFound",
    "FactView",
    "PostConfirmationEditRefused",
    "RejectDocumentRequest",
    "RejectFactRequest",
    "ReopenDocumentRequest",
    "ReviewActionError",
    "ReviewActionResult",
    "ReviewPrincipal",
    "ReviewStore",
    "accept_fact",
    "confirm_document",
    "correct_fact",
    "history_fingerprint",
    "read_document_review",
    "reject_document",
    "reject_fact",
    "reopen_document",
]

#: Document-level actor for the fail-closed demotion of a CLEAN ``auto_extracted``
#: document when a human corrects or rejects one of its facts (edge 6). The demotion is a
#: DETERMINISTIC consequence of the recorded fact-level human action — the document is no
#: longer "every check passed" — so the document-level actor is the pipeline, never a
#: human labelled ``qualified_human``. The human attribution is preserved at the fact
#: level (correction entry / professional_confirmation) and in the ReviewAuditEvent.
CORRECTION_TRIGGER_ACTOR_ID = "review-action-correction-trigger"
_CORRECTION_TRIGGER_ACTOR = TransitionActor(
    ActorKind.DETERMINISTIC_PIPELINE, actor_id=CORRECTION_TRIGGER_ACTOR_ID
)

_UNCONFIRMED_WIRE = {"state": "unconfirmed", "confirmed_by": None, "confirmed_at": None}
_ABSENT = object()


# --------------------------------------------------------------------- typed errors


class ReviewActionError(DocumentIngestionError):
    """Base class for review-action refusals not already typed by the shipped machinery.

    Illegal transitions, unauthorized transition actors, and missing transition reasons
    keep their shipped classes (``IllegalTransition`` / ``UnauthorizedTransitionActor`` /
    ``TransitionReasonRequired``) and are NOT re-wrapped; authorization refusals keep
    ``UnauthorizedReviewAction``. This family covers the record-level defects the review
    slice adds.
    """

    reject_code = "review_action_error"


class DocumentRecordNotFound(ReviewActionError):
    """No document ingestion record exists under the requested digest."""

    reject_code = "document_record_not_found"


class FactNotFound(ReviewActionError):
    """No material-fact evidence record exists under the requested id for this document."""

    reject_code = "fact_not_found"


class ConcurrentReviewModification(ReviewActionError):
    """The submission's accepted-history fingerprint no longer matches stored state.

    Optimistic-concurrency refusal (workflow section 6.3): another correction landed
    since the reviewer opened the fact. Nothing is written; the reviewer re-opens the
    current state and re-submits. Safe to retry (SC-S7).
    """

    reject_code = "concurrent_review_modification"


class PostConfirmationEditRefused(ReviewActionError):
    """A fact edit was attempted on a ``professionally_confirmed`` document (fail-closed).

    Editing (correct/reject) a fact of a confirmed document would silently invalidate a
    completed professional review. The reviewer must first REOPEN the document (edge 12,
    :func:`reopen_document`) — a visible, audited transition — before any fact edit
    (workflow section 4 edge 12; "reopening is visible and audited, never silent"). One
    clear next action: reopen, then edit.
    """

    reject_code = "post_confirmation_edit_refused"


class CorrectionRejected(ReviewActionError):
    """A correction failed a shipped correction-history validator; nothing was written.

    Carries the shipped :class:`UnresolvedCorrectionHistory` refusal payload verbatim in
    ``payload['detail']`` (tamper / chain-break / append-only / actor / no-op / chronology)
    so the UI maps the exact deterministic reason to plain language.
    """

    reject_code = "correction_rejected"


class ConfirmationRejected(ReviewActionError):
    """A professional confirmation/rejection failed the shipped confirmation validator.

    Carries the shipped :class:`UnresolvedCorrectionHistory` refusal payload in
    ``payload['detail']``.
    """

    reject_code = "confirmation_rejected"


# ---------------------------------------------------------------------- store seam


@runtime_checkable
class ReviewStore(Protocol):
    """Storage abstraction the review handlers depend on (B-001-honest).

    A single in-process implementation lives in the tests; production binds a cloud
    implementation when B-001 clears WITHOUT changing this surface. Mutations are keyed
    on the ``sha256:`` document digest and the fact ``evidence_id``; the fact record is
    the ``survey_evidence`` wire object (a dict), exactly the shape the shipped validators
    consume. ``save_fact`` is an optimistic compare-and-swap on the fact's accepted
    ``correction_history`` — a stale write is refused, never silently applied.
    """

    def load_document(self, document_digest: str) -> DocumentIngestionRecord:
        """Return the record, or raise :class:`DocumentRecordNotFound`."""
        ...

    def save_document(self, record: DocumentIngestionRecord) -> None:
        """Persist an advanced document record (its history already validated)."""
        ...

    def material_fact_ids(self, document_digest: str) -> tuple[str, ...]:
        """The evidence ids of every MATERIAL fact of the document (deterministic order)."""
        ...

    def load_fact(self, document_digest: str, evidence_id: str) -> dict:
        """Return the fact's survey_evidence wire dict, or raise :class:`FactNotFound`."""
        ...

    def save_fact(
        self,
        document_digest: str,
        evidence_id: str,
        fact: dict,
        *,
        expected_correction_history: list,
    ) -> None:
        """Compare-and-swap the fact; raise :class:`ConcurrentReviewModification` on drift."""
        ...

    def promotion_verdict(self, document_digest: str, evidence_id: str) -> PromotionVerdict:
        """The SERVER-COMPUTED deterministic promotion verdict for the fact's current state.

        Computed by the ingestion layer from the fact's stored deterministic validator
        results — never accepted from a client — so no confidence/AI value can promote.
        """
        ...

    def original_exists(self, document_digest: str) -> bool:
        """True when the immutable original bytes are retrievable (SC-S2)."""
        ...

    def original_fact_value(self, document_digest: str, evidence_id: str) -> object:
        """The INDEPENDENTLY-held immutable ``original_value`` of the fact (SC-S2).

        Sourced from the original extraction record (not the mutable current fact), so a
        correction's ``expected_original`` cross-check can actually detect a mutated
        stored original — the tamper guard fires only when the two disagree. Raises
        :class:`FactNotFound` when no original detection exists for the id.
        """
        ...

    def append_audit(self, event: ReviewAuditEvent) -> None:
        """Append one audit event (append-only; never edited or reordered)."""
        ...

    def enqueue_recalc(self, event: DependentRecalculationRequested) -> None:
        """Enqueue the dependent-recalculation trigger (the recompute consumer is a seam)."""
        ...


# ------------------------------------------------------------------- request DTOs


@dataclass(frozen=True)
class ReviewPrincipal:
    """The channel-authenticated principal classification passed to a handler.

    ``principal_kind`` is the closed CorrectingPrincipal wire value the SUBMISSION CHANNEL
    resolved (never a payload claim); ``actor_id`` is the authenticated identity or
    ``None`` (B-001).
    """

    principal_kind: str
    actor_id: str | None = None


@dataclass(frozen=True)
class AcceptFactRequest:
    document_digest: str
    evidence_id: str
    principal: ReviewPrincipal
    occurred_at: datetime
    correlation_id: str | None = None


@dataclass(frozen=True)
class CorrectFactRequest:
    document_digest: str
    evidence_id: str
    corrected_normalized_value: object
    corrected_units: str | None
    reason: str
    principal: ReviewPrincipal
    occurred_at: datetime
    #: Optimistic-concurrency token over the fact's accepted correction_history
    #: (:func:`history_fingerprint`). A stale token is refused (SC-S7).
    accepted_history_fingerprint: str
    correlation_id: str | None = None


@dataclass(frozen=True)
class RejectFactRequest:
    document_digest: str
    evidence_id: str
    reason: str
    principal: ReviewPrincipal
    occurred_at: datetime
    correlation_id: str | None = None


@dataclass(frozen=True)
class ConfirmDocumentRequest:
    document_digest: str
    principal: ReviewPrincipal
    occurred_at: datetime
    correlation_id: str | None = None


@dataclass(frozen=True)
class RejectDocumentRequest:
    document_digest: str
    reason: str
    principal: ReviewPrincipal
    occurred_at: datetime
    correlation_id: str | None = None


@dataclass(frozen=True)
class ReopenDocumentRequest:
    document_digest: str
    reason: str
    principal: ReviewPrincipal
    occurred_at: datetime
    correlation_id: str | None = None


# ------------------------------------------------------------------ response DTOs


@dataclass(frozen=True)
class FactView:
    """One fact as the review screen renders it (both state layers, always visible)."""

    evidence_id: str
    fact_type: str
    original_value: object
    baseline_normalized_value: object
    baseline_units: str | None
    normalized_value: object
    units: str | None
    confirmation_state: str
    confirmation_note: str | None
    correction_history: tuple[dict, ...]
    correction_count: int
    check_pass: int
    check_fail: int
    check_unresolved: int
    location: dict | None
    page_number: int | None
    extraction_method: str | None
    is_unconfirmed_evidence: bool
    promotable: bool
    downstream_impact: DownstreamImpact | None


@dataclass(frozen=True)
class DocumentReviewView:
    """The read model the review screen builds against (workflow section 12, row 1)."""

    document_digest: str
    target_bbl: str
    state: str
    state_history: tuple[dict, ...]
    facts: tuple[FactView, ...]
    confirm_precondition_met: bool
    blocking_fact_ids: tuple[str, ...]
    original_available: bool
    correlation_id: str | None = None


@dataclass(frozen=True)
class ReviewActionResult:
    """The outcome of a mutating review action, for the UI and the audit trail."""

    event_type: ReviewEventType
    document_digest: str
    document_state: str
    audit_events: tuple[ReviewAuditEvent, ...]
    evidence_id: str | None = None
    recalculation: DependentRecalculationRequested | None = None
    transitioned: bool = False
    correction_count: int | None = None
    downstream_impact: DownstreamImpact | None = None
    per_fact_confirmations: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------- helpers


def history_fingerprint(history: object) -> str:
    """Deterministic content fingerprint of an accepted correction_history array.

    Canonical JSON (sorted keys, tight separators) over the wire array, hashed to
    ``sha256:<hex>``. Used as the optimistic-concurrency token: two byte-identical
    accepted histories fingerprint identically; any edit/append changes it.
    """
    if not isinstance(history, list):
        raise TypeError("history must be the wire array of correction entries")
    canonical = json.dumps(
        history, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _to_rfc3339(occurred_at: datetime) -> str:
    if (
        not isinstance(occurred_at, datetime)
        or occurred_at.tzinfo is None
        or occurred_at.tzinfo.utcoffset(occurred_at) is None
    ):
        raise ValueError("occurred_at must be a timezone-aware datetime")
    return occurred_at.isoformat()


def _transition_payload(record: TransitionRecord) -> dict:
    return {
        "from_state": record.from_state.value,
        "to_state": record.to_state.value,
        "actor_kind": record.actor.kind.value,
        "actor_id": record.actor.actor_id,
        "occurred_at": record.occurred_at.isoformat(),
        "reason": record.reason,
    }


def _require_non_empty_reason(reason: object) -> str:
    if not isinstance(reason, str) or not reason.strip():
        raise CorrectionRejected(
            "a non-empty human-readable reason is required for this action",
            detail={"field": "reason"},
        )
    return reason


def _advance_document(
    record: DocumentIngestionRecord,
    to: DocumentState,
    *,
    actor: TransitionActor,
    occurred_at: datetime,
    reason: str | None = None,
    material_fact_verdicts: Mapping[str, object] | None = None,
) -> tuple[DocumentIngestionRecord, TransitionRecord]:
    """Advance a document strictly through the H5-gated wrapper (never raw transition).

    ``promotion_gated_transition`` raises the shipped typed errors on any illegal edge,
    unauthorized actor, missing reason, or unmet promotion precondition — propagated
    unchanged. The new record is built with ``dataclasses.replace`` so
    ``DocumentIngestionRecord.__post_init__`` re-validates the append-only state chain.
    """
    transition_record = promotion_gated_transition(
        record.state,
        to,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
        material_fact_verdicts=material_fact_verdicts,
    )
    advanced = replace(
        record,
        state=transition_record.to_state,
        state_history=(*record.state_history, transition_record),
    )
    return advanced, transition_record


def _confirmation_state(fact: dict) -> ProfessionalConfirmationState:
    confirmation = fact.get("professional_confirmation") or _UNCONFIRMED_WIRE
    validated = validate_professional_confirmation(confirmation)
    if isinstance(validated, ValidatedProfessionalConfirmation):
        return validated.state
    # A stored confirmation that no longer validates is treated as unconfirmed for
    # display honesty (never as confirmed): confirmation evidence must be provable.
    return ProfessionalConfirmationState.UNCONFIRMED


def _downstream_impact(
    document_digest: str,
    evidence_id: str,
    verdict: PromotionVerdict,
    confirmation_state: ProfessionalConfirmationState,
) -> DownstreamImpact | None:
    """The honest blocked/provisional consequence of one fact's current state (section 7.2).

    Deterministic and derived only from evidence state — the flag clears solely by
    changing evidence state (accept/correct/reject/confirm), never by dismissal (SC-S5).
    ``analysis_readiness`` (criticality) is left ``None`` here: only a profile consumer
    that knows the dependency graph decides whether a critical basis is touched (section
    9.2). A confirmed fact has no negative impact.
    """
    if confirmation_state is ProfessionalConfirmationState.REJECTED:
        return DownstreamImpact(
            impact_kind=DownstreamImpactKind.BLOCKED,
            coverage_status=COVERAGE_DATA_CONFLICT,
            reason=(
                "survey detection was professionally rejected as unusable; a dependent "
                "conclusion cannot rest on it"
            ),
            provenance_digest=document_digest,
            provenance_evidence_ids=(evidence_id,),
        )
    if isinstance(verdict, PromotionRefused):
        return DownstreamImpact(
            impact_kind=DownstreamImpactKind.BLOCKED,
            coverage_status=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            reason=(
                "survey fact is unresolved: its deterministic checks are incomplete, "
                "failed, or in conflict; needs review before a dependent conclusion"
            ),
            provenance_digest=document_digest,
            provenance_evidence_ids=(evidence_id,),
        )
    if confirmation_state is ProfessionalConfirmationState.CONFIRMED:
        return None
    # Deterministically promotable but not yet professionally confirmed: usable only as
    # provisional, labelled "Unconfirmed evidence" everywhere (SC-S4).
    return DownstreamImpact(
        impact_kind=DownstreamImpactKind.PROVISIONAL,
        coverage_status=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
        reason=(
            "survey evidence is complete but not professionally confirmed (Unconfirmed "
            "evidence); a dependent conclusion is provisional until confirmation"
        ),
        provenance_digest=document_digest,
        provenance_evidence_ids=(evidence_id,),
    )


def _baseline(fact: dict) -> NormalizationBaseline | None:
    if "baseline_normalized_value" not in fact:
        return None
    return NormalizationBaseline(
        normalized_value=fact.get("baseline_normalized_value"),
        units=fact.get("baseline_units"),
    )


def _refuse_post_confirmation_edit(record: DocumentIngestionRecord, verb: str) -> None:
    """Refuse a fact edit on a ``professionally_confirmed`` document (fail-closed).

    Editing a fact of a confirmed document must not be silent: the reviewer reopens the
    document first (edge 12), which is visible and audited. Keeps ``auto_extracted`` /
    ``needs_review`` behavior unchanged.
    """
    if record.state is DocumentState.PROFESSIONALLY_CONFIRMED:
        raise PostConfirmationEditRefused(
            f"cannot {verb} a fact on a professionally_confirmed document; reopen the "
            "document first (edge 12) so the change is visible and audited",
            document_digest=record.document_digest,
            document_state=record.state.value,
        )


def _recalc(
    trigger: ReviewEventType,
    document_digest: str,
    occurred_at: datetime,
    evidence_id: str | None,
    correlation_id: str | None,
) -> DependentRecalculationRequested:
    return DependentRecalculationRequested(
        document_digest=document_digest,
        trigger=trigger,
        requested_at=occurred_at,
        evidence_id=evidence_id,
        correlation_id=correlation_id,
        consumer_bound=False,
    )


# ---------------------------------------------------------------------- read


def read_document_review(
    store: ReviewStore,
    document_digest: str,
    principal: ReviewPrincipal,
    *,
    correlation_id: str | None = None,
) -> DocumentReviewView:
    """Assemble the review read model (document + facts + overlay + honesty flags).

    Authorizes READ, then returns both state layers, each fact's original/baseline/current
    values side by side with its correction chain (SC-S2), overlay ``location`` refs, the
    per-fact confirmation state, the check summary, the H5 confirm-precondition status with
    the exact blocking facts (section 4.3), and the blocked/provisional downstream impact
    per fact (section 7.2). Read-only: never mutates or transitions anything.
    """
    authorize_review_action(ReviewAction.READ, principal.principal_kind, principal.actor_id)
    record = store.load_document(document_digest)
    fact_views: list[FactView] = []
    blocking: list[str] = []
    material_ids = store.material_fact_ids(document_digest)
    for evidence_id in material_ids:
        fact = store.load_fact(document_digest, evidence_id)
        verdict = store.promotion_verdict(document_digest, evidence_id)
        confirmation_state = _confirmation_state(fact)
        confirmation = fact.get("professional_confirmation") or _UNCONFIRMED_WIRE
        # A fact blocks document confirmation when it is deterministically unproven OR
        # professionally rejected (a rejected detection is never confirmable — R1).
        if (
            isinstance(verdict, PromotionRefused)
            or confirmation_state is ProfessionalConfirmationState.REJECTED
        ):
            blocking.append(evidence_id)
        summary = fact.get("check_summary") or {}
        correction_history = tuple(fact.get("correction_history") or ())
        fact_views.append(
            FactView(
                evidence_id=evidence_id,
                fact_type=str(fact.get("fact_type")),
                original_value=fact.get("original_value"),
                baseline_normalized_value=fact.get(
                    "baseline_normalized_value", fact.get("normalized_value")
                ),
                baseline_units=fact.get("baseline_units", fact.get("units")),
                normalized_value=fact.get("normalized_value"),
                units=fact.get("units"),
                confirmation_state=confirmation_state.value,
                confirmation_note=confirmation.get("note"),
                correction_history=correction_history,
                correction_count=len(correction_history),
                check_pass=int(summary.get("pass", 0)),
                check_fail=int(summary.get("fail", 0)),
                check_unresolved=int(summary.get("unresolved", 0)),
                location=fact.get("location"),
                page_number=fact.get("page_number"),
                extraction_method=fact.get("extraction_method"),
                is_unconfirmed_evidence=(
                    confirmation_state is not ProfessionalConfirmationState.CONFIRMED
                ),
                promotable=isinstance(verdict, PromotionAllowed),
                downstream_impact=_downstream_impact(
                    document_digest, evidence_id, verdict, confirmation_state
                ),
            )
        )
    precondition_met = bool(material_ids) and not blocking
    return DocumentReviewView(
        document_digest=document_digest,
        target_bbl=record.target_bbl,
        state=record.state.value,
        state_history=tuple(_transition_payload(t) for t in record.state_history),
        facts=tuple(fact_views),
        confirm_precondition_met=precondition_met,
        blocking_fact_ids=tuple(blocking),
        original_available=store.original_exists(document_digest),
        correlation_id=correlation_id,
    )


# ---------------------------------------------------------------- per-fact actions


def accept_fact(store: ReviewStore, request: AcceptFactRequest) -> ReviewActionResult:
    """Affirm a fact's current extracted value (a lightweight review decision).

    Distinct from professional confirmation (section 10.4): accept does NOT set
    ``professional_confirmation`` and does not transition the document. It records the
    audit event and emits the dependent-recalculation trigger so that a previously-blocking
    item, once accepted, clears its downstream flag through rerun (SC-S5), never by
    dismissal.
    """
    principal = authorize_review_action(
        ReviewAction.ACCEPT_FACT, request.principal.principal_kind, request.principal.actor_id
    )
    record = store.load_document(request.document_digest)
    fact = store.load_fact(request.document_digest, request.evidence_id)
    event = ReviewAuditEvent(
        event_type=ReviewEventType.FACT_ACCEPTED,
        document_digest=request.document_digest,
        occurred_at=request.occurred_at,
        actor_role=principal.role.value,
        actor_id=principal.actor_id,
        evidence_id=request.evidence_id,
        correlation_id=request.correlation_id,
        detail={
            "affirmed_normalized_value": _reprable(fact.get("normalized_value")),
            "affirmed_units": fact.get("units"),
        },
    )
    store.append_audit(event)
    recalc = _recalc(
        ReviewEventType.FACT_ACCEPTED,
        request.document_digest,
        request.occurred_at,
        request.evidence_id,
        request.correlation_id,
    )
    store.enqueue_recalc(recalc)
    return ReviewActionResult(
        event_type=ReviewEventType.FACT_ACCEPTED,
        document_digest=request.document_digest,
        document_state=record.state.value,
        audit_events=(event,),
        evidence_id=request.evidence_id,
        recalculation=recalc,
    )


def correct_fact(store: ReviewStore, request: CorrectFactRequest) -> ReviewActionResult:
    """Append one correction (value/units + reason); route a clean doc to needs_review.

    Fully deterministic-validator-gated (SC-S1/SC-S2/SC-S6): the actor authority, the
    append-only extension, and the whole-record chain/immutability/no-op/chronology checks
    all run before anything is written, and any refusal is a typed
    :class:`CorrectionRejected` with the shipped reason and NO write. On success the
    correction is one APPEND to ``correction_history`` (the immutable original and
    ``original_value`` are never touched); an ``auto_extracted`` document demotes to
    ``needs_review`` (edge 6, the correction as its reason); the audit event and the
    recalculation trigger are emitted.
    """
    principal = authorize_review_action(
        ReviewAction.CORRECT_FACT,
        request.principal.principal_kind,
        request.principal.actor_id,
    )
    reason = _require_non_empty_reason(request.reason)
    record = store.load_document(request.document_digest)
    _refuse_post_confirmation_edit(record, "correct")
    fact = store.load_fact(request.document_digest, request.evidence_id)
    accepted_history = list(fact.get("correction_history") or [])

    if history_fingerprint(accepted_history) != request.accepted_history_fingerprint:
        raise ConcurrentReviewModification(
            "the fact's correction history changed since it was opened; re-open the "
            "current state and re-submit",
            document_digest=request.document_digest,
            evidence_id=request.evidence_id,
        )

    actor = validate_correcting_actor(
        principal.role.value, principal.principal.value, principal.actor_id
    )
    if isinstance(actor, UnresolvedCorrectionHistory):
        raise CorrectionRejected(actor.reason, detail=actor.to_payload())

    entry: dict = {
        "corrected_at": _to_rfc3339(request.occurred_at),
        "corrected_by_role": principal.role.value,
        "previous_normalized_value": fact.get("normalized_value"),
        "corrected_normalized_value": request.corrected_normalized_value,
        "previous_units": fact.get("units"),
        "corrected_units": request.corrected_units,
        "reason": reason,
    }
    if principal.actor_id is not None:
        entry["corrected_by"] = principal.actor_id

    submitted_history = [*accepted_history, entry]

    extension = validate_history_extension(accepted_history, submitted_history)
    if isinstance(extension, UnresolvedCorrectionHistory):
        raise CorrectionRejected(extension.reason, detail=extension.to_payload())

    # The immutable original is fetched INDEPENDENTLY (from the original extraction
    # record), never the mutable current fact, so the shipped tamper cross-check can fire
    # if the stored original_value was mutated (SC-S2).
    expected_original = store.original_fact_value(
        request.document_digest, request.evidence_id
    )
    integrity = validate_correction_history(
        original_value=fact.get("original_value"),
        normalized_value=request.corrected_normalized_value,
        units=request.corrected_units,
        correction_history=submitted_history,
        expected_original=OriginalValueReference(expected_original),
        baseline=_baseline(fact),
    )
    if isinstance(integrity, UnresolvedCorrectionHistory):
        raise CorrectionRejected(integrity.reason, detail=integrity.to_payload())

    new_fact = {
        **fact,
        "normalized_value": request.corrected_normalized_value,
        "units": request.corrected_units,
        "correction_history": submitted_history,
    }
    store.save_fact(
        request.document_digest,
        request.evidence_id,
        new_fact,
        expected_correction_history=accepted_history,
    )

    audit_events: list[ReviewAuditEvent] = []
    transitioned = False
    detail: dict = {"correction_entry": entry}
    document_state = record.state
    if record.state is DocumentState.AUTO_EXTRACTED:
        advanced, transition_record = _advance_document(
            record,
            DocumentState.NEEDS_REVIEW,
            actor=_CORRECTION_TRIGGER_ACTOR,
            occurred_at=request.occurred_at,
            reason=reason,
        )
        store.save_document(advanced)
        document_state = advanced.state
        transitioned = True
        detail["transition"] = _transition_payload(transition_record)

    event = ReviewAuditEvent(
        event_type=ReviewEventType.FACT_CORRECTED,
        document_digest=request.document_digest,
        occurred_at=request.occurred_at,
        actor_role=principal.role.value,
        actor_id=principal.actor_id,
        evidence_id=request.evidence_id,
        reason=reason,
        correlation_id=request.correlation_id,
        detail=detail,
    )
    store.append_audit(event)
    audit_events.append(event)

    recalc = _recalc(
        ReviewEventType.FACT_CORRECTED,
        request.document_digest,
        request.occurred_at,
        request.evidence_id,
        request.correlation_id,
    )
    store.enqueue_recalc(recalc)

    return ReviewActionResult(
        event_type=ReviewEventType.FACT_CORRECTED,
        document_digest=request.document_digest,
        document_state=document_state.value,
        audit_events=tuple(audit_events),
        evidence_id=request.evidence_id,
        recalculation=recalc,
        transitioned=transitioned,
        correction_count=integrity.correction_count,
    )


def reject_fact(store: ReviewStore, request: RejectFactRequest) -> ReviewActionResult:
    """Professionally reject a fact detection as unusable (sets confirmation → rejected).

    Professional role only (SC-S3; workflow section 12). Sets the fact's
    ``professional_confirmation.state = rejected`` with attributed identity/time and the
    reason as the note, validated by the shipped
    :func:`validate_professional_confirmation`; demotes a clean ``auto_extracted`` document
    to ``needs_review`` (edge 6); propagates the fact as a BLOCKING downstream item
    (section 7.2) and emits the recalculation trigger.
    """
    principal = authorize_review_action(
        ReviewAction.REJECT_FACT, request.principal.principal_kind, request.principal.actor_id
    )
    reason = _require_non_empty_reason(request.reason)
    record = store.load_document(request.document_digest)
    _refuse_post_confirmation_edit(record, "reject")
    fact = store.load_fact(request.document_digest, request.evidence_id)
    accepted_history = list(fact.get("correction_history") or [])

    confirmation = {
        "state": ProfessionalConfirmationState.REJECTED.value,
        "confirmed_by": principal.actor_id,
        "confirmed_at": _to_rfc3339(request.occurred_at),
        "note": reason,
    }
    validated = validate_professional_confirmation(confirmation)
    if isinstance(validated, UnresolvedCorrectionHistory):
        raise ConfirmationRejected(validated.reason, detail=validated.to_payload())

    new_fact = {**fact, "professional_confirmation": confirmation}
    store.save_fact(
        request.document_digest,
        request.evidence_id,
        new_fact,
        expected_correction_history=accepted_history,
    )

    transitioned = False
    document_state = record.state
    detail: dict = {"professional_confirmation": confirmation}
    if record.state is DocumentState.AUTO_EXTRACTED:
        advanced, transition_record = _advance_document(
            record,
            DocumentState.NEEDS_REVIEW,
            actor=_CORRECTION_TRIGGER_ACTOR,
            occurred_at=request.occurred_at,
            reason=reason,
        )
        store.save_document(advanced)
        document_state = advanced.state
        transitioned = True
        detail["transition"] = _transition_payload(transition_record)

    event = ReviewAuditEvent(
        event_type=ReviewEventType.FACT_REJECTED,
        document_digest=request.document_digest,
        occurred_at=request.occurred_at,
        actor_role=principal.role.value,
        actor_id=principal.actor_id,
        evidence_id=request.evidence_id,
        reason=reason,
        correlation_id=request.correlation_id,
        detail=detail,
    )
    store.append_audit(event)
    recalc = _recalc(
        ReviewEventType.FACT_REJECTED,
        request.document_digest,
        request.occurred_at,
        request.evidence_id,
        request.correlation_id,
    )
    store.enqueue_recalc(recalc)

    impact = _downstream_impact(
        request.document_digest,
        request.evidence_id,
        store.promotion_verdict(request.document_digest, request.evidence_id),
        ProfessionalConfirmationState.REJECTED,
    )
    return ReviewActionResult(
        event_type=ReviewEventType.FACT_REJECTED,
        document_digest=request.document_digest,
        document_state=document_state.value,
        audit_events=(event,),
        evidence_id=request.evidence_id,
        recalculation=recalc,
        transitioned=transitioned,
        downstream_impact=impact,
    )


# --------------------------------------------------------------- document actions


def confirm_document(
    store: ReviewStore, request: ConfirmDocumentRequest
) -> ReviewActionResult:
    """Professionally confirm the document (edges 9/10), H5-gated; confirm each fact.

    Professional role only (SC-S3). The per-fact ``PromotionAllowed`` verdicts the H5 gate
    requires are COMPUTED SERVER-SIDE (:meth:`ReviewStore.promotion_verdict`) for EVERY
    material fact — never accepted from the client — so a confidence/AI value can never
    promote (SC-S4). ``promotion_gated_transition`` refuses (typed ``IllegalTransition``)
    if any material fact is unproven or if there are no material facts. On success the
    document moves to ``professionally_confirmed`` and each material fact's
    ``professional_confirmation.state`` is set to ``confirmed`` with attributed
    identity/time.
    """
    principal = authorize_review_action(
        ReviewAction.CONFIRM_DOCUMENT,
        request.principal.principal_kind,
        request.principal.actor_id,
    )
    record = store.load_document(request.document_digest)
    material_ids = store.material_fact_ids(request.document_digest)

    # A professionally-rejected fact BLOCKS confirmation and is NEVER silently overwritten
    # to "confirmed" (workflow sections 7.2/10.4 over the literal section-12 table). A
    # rejected detection can be deterministically promotable, so the H5 gate alone would
    # not catch it — this explicit refusal does. It is cleared only by re-extraction or a
    # corrected new upload, never by confirm_document.
    rejected_ids = [
        evidence_id
        for evidence_id in material_ids
        if _confirmation_state(store.load_fact(request.document_digest, evidence_id))
        is ProfessionalConfirmationState.REJECTED
    ]
    if rejected_ids:
        raise ConfirmationRejected(
            "cannot confirm a document while material facts are professionally rejected; "
            "a rejected detection is unusable and blocks confirmation until re-extraction "
            "or a corrected upload replaces it — never overwritten to 'confirmed'",
            detail={"rejected_fact_ids": rejected_ids},
        )

    verdicts: dict[str, object] = {
        evidence_id: store.promotion_verdict(request.document_digest, evidence_id)
        for evidence_id in material_ids
    }

    actor = TransitionActor(ActorKind.QUALIFIED_HUMAN, actor_id=principal.actor_id)
    advanced, transition_record = _advance_document(
        record,
        DocumentState.PROFESSIONALLY_CONFIRMED,
        actor=actor,
        occurred_at=request.occurred_at,
        material_fact_verdicts=verdicts,
    )
    store.save_document(advanced)

    confirmed_at = _to_rfc3339(request.occurred_at)
    audit_events: list[ReviewAuditEvent] = []
    confirmed_ids: list[str] = []
    for evidence_id in material_ids:
        fact = store.load_fact(request.document_digest, evidence_id)
        confirmation = {
            "state": ProfessionalConfirmationState.CONFIRMED.value,
            "confirmed_by": principal.actor_id,
            "confirmed_at": confirmed_at,
        }
        validated = validate_professional_confirmation(confirmation)
        if isinstance(validated, UnresolvedCorrectionHistory):  # pragma: no cover
            raise ConfirmationRejected(validated.reason, detail=validated.to_payload())
        store.save_fact(
            request.document_digest,
            evidence_id,
            {**fact, "professional_confirmation": confirmation},
            expected_correction_history=list(fact.get("correction_history") or []),
        )
        confirmed_ids.append(evidence_id)
        fact_event = ReviewAuditEvent(
            event_type=ReviewEventType.FACT_CONFIRMED,
            document_digest=request.document_digest,
            occurred_at=request.occurred_at,
            actor_role=principal.role.value,
            actor_id=principal.actor_id,
            evidence_id=evidence_id,
            correlation_id=request.correlation_id,
            detail={"professional_confirmation": confirmation},
        )
        store.append_audit(fact_event)
        audit_events.append(fact_event)

    doc_event = ReviewAuditEvent(
        event_type=ReviewEventType.DOCUMENT_CONFIRMED,
        document_digest=request.document_digest,
        occurred_at=request.occurred_at,
        actor_role=principal.role.value,
        actor_id=principal.actor_id,
        correlation_id=request.correlation_id,
        detail={
            "transition": _transition_payload(transition_record),
            "confirmed_fact_ids": list(confirmed_ids),
        },
    )
    store.append_audit(doc_event)
    audit_events.append(doc_event)

    recalc = _recalc(
        ReviewEventType.DOCUMENT_CONFIRMED,
        request.document_digest,
        request.occurred_at,
        None,
        request.correlation_id,
    )
    store.enqueue_recalc(recalc)

    return ReviewActionResult(
        event_type=ReviewEventType.DOCUMENT_CONFIRMED,
        document_digest=request.document_digest,
        document_state=advanced.state.value,
        audit_events=tuple(audit_events),
        recalculation=recalc,
        transitioned=True,
        per_fact_confirmations=tuple(confirmed_ids),
    )


def reject_document(
    store: ReviewStore, request: RejectDocumentRequest
) -> ReviewActionResult:
    """Professionally reject the document (edge 11, ``needs_review → rejected``, +reason).

    Professional role only. ``rejected`` is terminal; recovery is a NEW upload (new
    digest). A non-``needs_review`` source state fails closed with the shipped
    ``IllegalTransition``.
    """
    principal = authorize_review_action(
        ReviewAction.REJECT_DOCUMENT,
        request.principal.principal_kind,
        request.principal.actor_id,
    )
    # Reason discipline is the shipped transition's job (edge 11 requires it): an empty
    # reason raises the shipped ``TransitionReasonRequired``, keeping the error domain
    # correct (R4) — not a fact-level CorrectionRejected.
    reason = request.reason
    record = store.load_document(request.document_digest)
    actor = TransitionActor(ActorKind.QUALIFIED_HUMAN, actor_id=principal.actor_id)
    advanced, transition_record = _advance_document(
        record,
        DocumentState.REJECTED,
        actor=actor,
        occurred_at=request.occurred_at,
        reason=reason,
    )
    store.save_document(advanced)
    event = ReviewAuditEvent(
        event_type=ReviewEventType.DOCUMENT_REJECTED,
        document_digest=request.document_digest,
        occurred_at=request.occurred_at,
        actor_role=principal.role.value,
        actor_id=principal.actor_id,
        reason=reason,
        correlation_id=request.correlation_id,
        detail={"transition": _transition_payload(transition_record)},
    )
    store.append_audit(event)
    recalc = _recalc(
        ReviewEventType.DOCUMENT_REJECTED,
        request.document_digest,
        request.occurred_at,
        None,
        request.correlation_id,
    )
    store.enqueue_recalc(recalc)
    return ReviewActionResult(
        event_type=ReviewEventType.DOCUMENT_REJECTED,
        document_digest=request.document_digest,
        document_state=advanced.state.value,
        audit_events=(event,),
        recalculation=recalc,
        transitioned=True,
    )


def reopen_document(
    store: ReviewStore, request: ReopenDocumentRequest
) -> ReviewActionResult:
    """Reopen a confirmed document on a post-confirmation contradiction (edge 12, +reason).

    Professional (human) reopening: ``professionally_confirmed → needs_review``, visible
    and audited, never silent (workflow section 4, edge 12). Emits the recalculation
    trigger so dependent conclusions re-derive honestly.
    """
    principal = authorize_review_action(
        ReviewAction.REOPEN_DOCUMENT,
        request.principal.principal_kind,
        request.principal.actor_id,
    )
    # Edge 12 requires a reason; an empty one raises the shipped
    # ``TransitionReasonRequired`` (R4), not a fact-level CorrectionRejected.
    reason = request.reason
    record = store.load_document(request.document_digest)
    actor = TransitionActor(ActorKind.QUALIFIED_HUMAN, actor_id=principal.actor_id)
    advanced, transition_record = _advance_document(
        record,
        DocumentState.NEEDS_REVIEW,
        actor=actor,
        occurred_at=request.occurred_at,
        reason=reason,
    )
    store.save_document(advanced)
    event = ReviewAuditEvent(
        event_type=ReviewEventType.DOCUMENT_REOPENED,
        document_digest=request.document_digest,
        occurred_at=request.occurred_at,
        actor_role=principal.role.value,
        actor_id=principal.actor_id,
        reason=reason,
        correlation_id=request.correlation_id,
        detail={"transition": _transition_payload(transition_record)},
    )
    store.append_audit(event)
    recalc = _recalc(
        ReviewEventType.DOCUMENT_REOPENED,
        request.document_digest,
        request.occurred_at,
        None,
        request.correlation_id,
    )
    store.enqueue_recalc(recalc)
    return ReviewActionResult(
        event_type=ReviewEventType.DOCUMENT_REOPENED,
        document_digest=request.document_digest,
        document_state=advanced.state.value,
        audit_events=(event,),
        recalculation=recalc,
        transitioned=True,
    )


def _reprable(value: object) -> object:
    """Return ``value`` if JSON-native, else its ``repr`` (audit payloads are JSON-safe)."""
    if value is None or isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return repr(value)
