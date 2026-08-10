"""Survey review-action handler behavior (M2-T016, SC-S1..S8).

Adversarial, fixture-table coverage over an in-process :class:`ReviewStore` (the B-001
local/CI implementation): each legal action, each illegal transition (fail-closed),
immutability under correction, authorization, correction-history append-only/tamper
refusal, audit completeness, the dependent-recalculation trigger, and recoverable
concurrency. Promotion verdicts are COMPUTED SERVER-SIDE from stored deterministic results
via the real ``evaluate_promotion`` — never hand-built — so no confidence/AI value can
promote (SC-S4).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from app.documents.models import DocumentIngestionRecord
from app.documents.promotion import (
    REQUIRED_VALIDATIONS,
    PromotionAllowed,
    PromotionRefused,
    evaluate_promotion,
)
from app.documents.review_actions import (
    AcceptFactRequest,
    ConcurrentReviewModification,
    ConfirmationRejected,
    ConfirmDocumentRequest,
    CorrectFactRequest,
    CorrectionRejected,
    DocumentRecordNotFound,
    FactNotFound,
    PostConfirmationEditRefused,
    RejectDocumentRequest,
    RejectFactRequest,
    ReopenDocumentRequest,
    ReviewPrincipal,
    ReviewStore,
    accept_fact,
    confirm_document,
    correct_fact,
    history_fingerprint,
    read_document_review,
    reject_document,
    reject_fact,
    reopen_document,
)
from app.documents.review_authz import UnauthorizedReviewAction
from app.documents.review_events import DownstreamImpactKind, ReviewEventType
from app.documents.state import (
    ActorKind,
    DocumentState,
    IllegalTransition,
    TransitionActor,
    TransitionReasonRequired,
)
from app.documents.taxonomy import SurveyFactType

WHEN = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
DIGEST = "sha256:" + "b" * 64
BBL = "1002270001"
PIPELINE = TransitionActor(ActorKind.DETERMINISTIC_PIPELINE, actor_id="worker-1")
HUMAN = TransitionActor(ActorKind.QUALIFIED_HUMAN, actor_id="pls-1")

USER = ReviewPrincipal("human_user", "analyst-1")
PRO = ReviewPrincipal("human_qualified_professional", "pls-1")
AI = ReviewPrincipal("ai_assisted_classification", "bot")


@dataclass(frozen=True)
class _ResolvedResult:
    """Minimal typed result satisfying the promotion evidence contract."""

    resolved: bool
    fact_type: object


def make_fact(
    evidence_id: str,
    fact_type: str = SurveyFactType.STATED_LOT_AREA.value,
    normalized_value: object = 5000.0,
    units: str | None = "square_feet",
    *,
    resolved: bool = True,
    original_value: object = "AREA = 5000 SF",
    professional_confirmation: dict | None = None,
    correction_history: list | None = None,
    check_summary: dict | None = None,
) -> dict:
    required = REQUIRED_VALIDATIONS[SurveyFactType(fact_type)]
    if resolved:
        results = {kind: (_ResolvedResult(True, fact_type),) for kind in required}
        summary = check_summary or {"pass": 3, "fail": 0, "unresolved": 0}
    else:
        results = {}  # missing required validations -> PromotionRefused
        summary = check_summary or {"pass": 1, "fail": 1, "unresolved": 1}
    return {
        "evidence_id": evidence_id,
        "fact_type": fact_type,
        "original_value": original_value,
        "baseline_normalized_value": normalized_value,
        "baseline_units": units,
        "normalized_value": normalized_value,
        "units": units,
        "correction_history": list(correction_history or []),
        "professional_confirmation": professional_confirmation
        or {"state": "unconfirmed", "confirmed_by": None, "confirmed_at": None},
        "location": {
            "bounding_box": {"coordinate_space": "raster_pixels", "x": 1, "y": 2, "w": 3, "h": 4}
        },
        "page_number": 1,
        "extraction_method": "deterministic_geometry_reconstruction",
        "confidence": None,
        "check_summary": summary,
        "promotion_results": results,
    }


def make_document(state: DocumentState, digest: str = DIGEST) -> DocumentIngestionRecord:
    record = DocumentIngestionRecord(
        document_digest=digest,
        target_bbl=BBL,
        original_filename="survey.pdf",
        declared_document_class="survey",
        sniffed_mime_type="application/pdf",
        size_bytes=2048,
        uploaded_at=WHEN,
    )
    if state is DocumentState.UPLOADED:
        return record
    record = record.apply_transition(DocumentState.PROCESSING, actor=PIPELINE, occurred_at=WHEN)
    if state is DocumentState.PROCESSING:
        return record
    if state is DocumentState.AUTO_EXTRACTED:
        return record.apply_transition(
            DocumentState.AUTO_EXTRACTED, actor=PIPELINE, occurred_at=WHEN
        )
    record = record.apply_transition(
        DocumentState.NEEDS_REVIEW, actor=PIPELINE, occurred_at=WHEN
    )
    if state is DocumentState.NEEDS_REVIEW:
        return record
    if state is DocumentState.PROFESSIONALLY_CONFIRMED:
        return record.apply_transition(
            DocumentState.PROFESSIONALLY_CONFIRMED, actor=HUMAN, occurred_at=WHEN
        )
    if state is DocumentState.REJECTED:
        return record.apply_transition(
            DocumentState.REJECTED, actor=HUMAN, occurred_at=WHEN, reason="not a survey"
        )
    raise AssertionError(state)


class InMemoryReviewStore:
    """Single-process B-001 store: dicts, no bucket/credential/network (see storage.py)."""

    def __init__(self) -> None:
        self.documents: dict[str, DocumentIngestionRecord] = {}
        self.facts: dict[tuple[str, str], dict] = {}
        self.material: dict[str, list[str]] = {}
        self.originals: set[str] = set()
        # Independently-held immutable original detection values, snapshotted at ingest and
        # NEVER updated by a correction (mirrors the original extraction record).
        self.original_values: dict[tuple[str, str], object] = {}
        self.audit: list = []
        self.recalcs: list = []

    def add(self, record: DocumentIngestionRecord, facts: list[dict], *, original: bool = True):
        self.documents[record.document_digest] = record
        self.material[record.document_digest] = [f["evidence_id"] for f in facts]
        for fact in facts:
            key = (record.document_digest, fact["evidence_id"])
            self.facts[key] = dict(fact)
            self.original_values[key] = fact["original_value"]
        if original:
            self.originals.add(record.document_digest)

    # --- ReviewStore protocol ---
    def load_document(self, document_digest: str) -> DocumentIngestionRecord:
        try:
            return self.documents[document_digest]
        except KeyError:
            raise DocumentRecordNotFound(
                "no such document", document_digest=document_digest
            ) from None

    def save_document(self, record: DocumentIngestionRecord) -> None:
        self.documents[record.document_digest] = record

    def material_fact_ids(self, document_digest: str) -> tuple[str, ...]:
        return tuple(self.material.get(document_digest, ()))

    def load_fact(self, document_digest: str, evidence_id: str) -> dict:
        try:
            return dict(self.facts[(document_digest, evidence_id)])
        except KeyError:
            raise FactNotFound("no such fact", evidence_id=evidence_id) from None

    def save_fact(self, document_digest, evidence_id, fact, *, expected_correction_history):
        key = (document_digest, evidence_id)
        current = self.facts.get(key)
        if current is None:
            raise FactNotFound("no such fact", evidence_id=evidence_id)
        if list(current.get("correction_history") or []) != list(expected_correction_history):
            raise ConcurrentReviewModification("stale write", evidence_id=evidence_id)
        self.facts[key] = dict(fact)

    def promotion_verdict(self, document_digest, evidence_id):
        fact = self.facts[(document_digest, evidence_id)]
        return evaluate_promotion(
            fact["fact_type"],
            fact.get("promotion_results", {}),
            fact.get("extraction_method"),
            fact.get("confidence"),
        )

    def original_exists(self, document_digest: str) -> bool:
        return document_digest in self.originals

    def original_fact_value(self, document_digest, evidence_id):
        key = (document_digest, evidence_id)
        if key not in self.original_values:
            raise FactNotFound("no original detection", evidence_id=evidence_id)
        return self.original_values[key]

    def append_audit(self, event) -> None:
        self.audit.append(event)

    def enqueue_recalc(self, event) -> None:
        self.recalcs.append(event)


def _store(state=DocumentState.NEEDS_REVIEW, facts=None) -> InMemoryReviewStore:
    store = InMemoryReviewStore()
    store.add(make_document(state), facts if facts is not None else [make_fact("ev-1")])
    return store


def test_store_satisfies_protocol():
    assert isinstance(InMemoryReviewStore(), ReviewStore)


# =========================================================== SC-S1 primary journey


def test_sc_s1_primary_journey_accept_correct_reject_full_audit_and_rerun():
    store = _store(
        facts=[make_fact("ev-1"), make_fact("ev-2"), make_fact("ev-3", resolved=False)]
    )
    # Accept ev-1
    accept_fact(store, AcceptFactRequest(DIGEST, "ev-1", USER, WHEN))
    # Correct ev-2 (with reason)
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-2")["correction_history"])
    corr = correct_fact(
        store,
        CorrectFactRequest(
            DIGEST, "ev-2", 5200.0, "square_feet", "transcribed area was 5200 not 5000",
            USER, WHEN, fp,
        ),
    )
    assert corr.correction_count == 1
    assert store.load_fact(DIGEST, "ev-2")["normalized_value"] == 5200.0
    # Reject ev-3 (professional)
    rej = reject_fact(store, RejectFactRequest(DIGEST, "ev-3", "illegible dimension", PRO, WHEN))
    assert (
        store.load_fact(DIGEST, "ev-3")["professional_confirmation"]["state"] == "rejected"
    )
    assert rej.downstream_impact.impact_kind is DownstreamImpactKind.BLOCKED
    # Audit trail complete: one event per action; recalcs fired for each.
    kinds = [e.event_type for e in store.audit]
    assert kinds == [
        ReviewEventType.FACT_ACCEPTED,
        ReviewEventType.FACT_CORRECTED,
        ReviewEventType.FACT_REJECTED,
    ]
    assert len(store.recalcs) == 3


# =========================================================== SC-S2 immutability


def test_sc_s2_original_and_digest_intact_after_corrections():
    store = _store(state=DocumentState.AUTO_EXTRACTED)
    original_before = store.load_fact(DIGEST, "ev-1")["original_value"]
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    correct_fact(
        store,
        CorrectFactRequest(DIGEST, "ev-1", 4800.0, "square_feet", "unit fix", PRO, WHEN, fp),
    )
    fact = store.load_fact(DIGEST, "ev-1")
    assert fact["original_value"] == original_before  # never mutated
    assert fact["baseline_normalized_value"] == 5000.0  # original baseline preserved
    assert fact["normalized_value"] == 4800.0  # corrected value
    assert len(fact["correction_history"]) == 1
    assert store.original_exists(DIGEST)


def test_sc_s2_read_view_shows_original_baseline_beside_corrections():
    store = _store()
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    correct_fact(
        store,
        CorrectFactRequest(DIGEST, "ev-1", 5100.0, "square_feet", "typo", USER, WHEN, fp),
    )
    view = read_document_review(store, DIGEST, USER)
    fact_view = view.facts[0]
    assert fact_view.original_value == "AREA = 5000 SF"
    assert fact_view.baseline_normalized_value == 5000.0
    assert fact_view.normalized_value == 5100.0
    assert fact_view.correction_count == 1
    assert view.original_available


# =========================================================== SC-S3 authorization


@pytest.mark.parametrize(
    "call",
    [
        lambda s: reject_fact(s, RejectFactRequest(DIGEST, "ev-1", "r", USER, WHEN)),
        lambda s: confirm_document(s, ConfirmDocumentRequest(DIGEST, USER, WHEN)),
        lambda s: reject_document(s, RejectDocumentRequest(DIGEST, "r", USER, WHEN)),
    ],
)
def test_sc_s3_user_cannot_perform_professional_actions(call):
    store = _store()
    with pytest.raises(UnauthorizedReviewAction):
        call(store)
    assert store.audit == [] and store.recalcs == []  # no write on refusal


@pytest.mark.parametrize(
    "call",
    [
        lambda s: accept_fact(s, AcceptFactRequest(DIGEST, "ev-1", AI, WHEN)),
        lambda s: correct_fact(
            s, CorrectFactRequest(DIGEST, "ev-1", 1.0, "u", "r", AI, WHEN, "sha256:x")
        ),
        lambda s: reject_fact(s, RejectFactRequest(DIGEST, "ev-1", "r", AI, WHEN)),
        lambda s: confirm_document(s, ConfirmDocumentRequest(DIGEST, AI, WHEN)),
        lambda s: read_document_review(s, DIGEST, AI),
    ],
)
def test_sc_s3_ai_principal_cannot_do_anything(call):
    store = _store()
    with pytest.raises(UnauthorizedReviewAction):
        call(store)


# ======================================================= SC-S4 no auto-verified


def test_sc_s4_confirm_refused_when_any_material_fact_unresolved():
    store = _store(
        state=DocumentState.NEEDS_REVIEW,
        facts=[make_fact("ev-1"), make_fact("ev-2", resolved=False)],
    )
    with pytest.raises(IllegalTransition) as exc:
        confirm_document(store, ConfirmDocumentRequest(DIGEST, PRO, WHEN))
    assert "'ev-2'" in str(exc.value)
    # Document did NOT transition; no fact was confirmed.
    assert store.load_document(DIGEST).state is DocumentState.NEEDS_REVIEW
    assert store.load_fact(DIGEST, "ev-1")["professional_confirmation"]["state"] == "unconfirmed"


def test_sc_s4_confirm_refused_when_no_material_facts():
    store = _store(facts=[])
    with pytest.raises(IllegalTransition):
        confirm_document(store, ConfirmDocumentRequest(DIGEST, PRO, WHEN))


def test_sc_s4_confirm_succeeds_only_through_professional_and_gate():
    store = _store(facts=[make_fact("ev-1"), make_fact("ev-2")])
    result = confirm_document(store, ConfirmDocumentRequest(DIGEST, PRO, WHEN))
    assert store.load_document(DIGEST).state is DocumentState.PROFESSIONALLY_CONFIRMED
    assert set(result.per_fact_confirmations) == {"ev-1", "ev-2"}
    for eid in ("ev-1", "ev-2"):
        assert store.load_fact(DIGEST, eid)["professional_confirmation"]["state"] == "confirmed"
        assert store.load_fact(DIGEST, eid)["professional_confirmation"]["confirmed_by"] == "pls-1"


def test_sc_s4_auto_extracted_facts_display_as_unconfirmed_evidence():
    store = _store(state=DocumentState.AUTO_EXTRACTED)
    view = read_document_review(store, DIGEST, USER)
    assert view.facts[0].is_unconfirmed_evidence is True
    assert view.facts[0].confirmation_state == "unconfirmed"
    assert view.facts[0].promotable is True  # promotable != confirmed


def test_sc_s4_client_cannot_forge_promotion_high_confidence_ai_fact_cannot_promote():
    # An AI-extracted fact with high confidence but no resolved deterministic validation
    # is PromotionRefused server-side and blocks confirmation.
    ai_fact = make_fact("ev-1", resolved=False)
    ai_fact["extraction_method"] = "ai_assisted_classification"
    ai_fact["confidence"] = 0.99
    store = _store(facts=[ai_fact])
    assert isinstance(store.promotion_verdict(DIGEST, "ev-1"), PromotionRefused)
    with pytest.raises(IllegalTransition):
        confirm_document(store, ConfirmDocumentRequest(DIGEST, PRO, WHEN))


# ==================================================== SC-S5 downstream honesty


def test_sc_s5_unresolved_and_unconfirmed_items_propagate_visibly():
    store = _store(
        facts=[
            make_fact("ev-ok"),  # resolved, unconfirmed -> provisional
            make_fact("ev-bad", resolved=False),  # unresolved -> blocked
        ]
    )
    view = read_document_review(store, DIGEST, USER)
    impacts = {f.evidence_id: f.downstream_impact for f in view.facts}
    assert impacts["ev-ok"].impact_kind is DownstreamImpactKind.PROVISIONAL
    assert impacts["ev-bad"].impact_kind is DownstreamImpactKind.BLOCKED
    assert view.blocking_fact_ids == ("ev-bad",)
    assert view.confirm_precondition_met is False


def test_sc_s5_resolving_clears_the_flag_through_rerun_not_dismissal():
    store = _store(facts=[make_fact("ev-1", resolved=False)])
    # There is no "dismiss" handler; the only handlers that touch the item change evidence.
    result = accept_fact(store, AcceptFactRequest(DIGEST, "ev-1", USER, WHEN))
    assert result.recalculation is not None  # the flag clears through this rerun
    assert result.recalculation.trigger is ReviewEventType.FACT_ACCEPTED
    assert result.recalculation.consumer_bound is False  # documented seam


def test_sc_s5_confirmed_fact_has_no_downstream_impact():
    confirmed = make_fact(
        "ev-1",
        professional_confirmation={
            "state": "confirmed",
            "confirmed_by": "pls-1",
            "confirmed_at": "2026-08-09T12:00:00+00:00",
        },
    )
    store = _store(state=DocumentState.PROFESSIONALLY_CONFIRMED, facts=[confirmed])
    view = read_document_review(store, DIGEST, USER)
    assert view.facts[0].downstream_impact is None
    assert view.facts[0].is_unconfirmed_evidence is False


# ==================================================== SC-S6 conflict display


def test_sc_s6_conflict_is_blocked_and_only_resolvable_by_correct_or_reject():
    store = _store(facts=[make_fact("ev-1", resolved=False)])
    view = read_document_review(store, DIGEST, USER)
    assert view.facts[0].downstream_impact.impact_kind is DownstreamImpactKind.BLOCKED
    assert "unresolved" in view.facts[0].downstream_impact.reason
    # Correct resolves it with an audited reason (no dismissal path exists).
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    out = correct_fact(
        store,
        CorrectFactRequest(DIGEST, "ev-1", 5000.0, "meters", "unit was mislabeled", PRO, WHEN, fp),
    )
    assert out.audit_events[0].reason == "unit was mislabeled"


# ===================================================== SC-S7 recovery + concurrency


def test_sc_s7_stale_fingerprint_is_refused_and_safe_to_retry():
    store = _store()
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    correct_fact(
        store, CorrectFactRequest(DIGEST, "ev-1", 5100.0, "square_feet", "first", USER, WHEN, fp)
    )
    # A second correction with the STALE fingerprint is refused, nothing written.
    with pytest.raises(ConcurrentReviewModification):
        correct_fact(
            store,
            CorrectFactRequest(
                DIGEST, "ev-1", 5200.0, "square_feet", "second", USER,
                WHEN + timedelta(minutes=1), fp,
            ),
        )
    assert len(store.load_fact(DIGEST, "ev-1")["correction_history"]) == 1
    # Re-opening the current state and re-submitting the fresh fingerprint succeeds.
    fresh = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    correct_fact(
        store,
        CorrectFactRequest(
            DIGEST, "ev-1", 5200.0, "square_feet", "retry", USER, WHEN + timedelta(minutes=2), fresh
        ),
    )
    assert len(store.load_fact(DIGEST, "ev-1")["correction_history"]) == 2


# =============================================== correction adversarial fixture table


CORRECTION_REFUSALS = [
    # (name, corrected_value, corrected_units, reason, principal, expect_exc)
    ("no_op_same_value_units", 5000.0, "square_feet", "no change", USER, CorrectionRejected),
    ("empty_reason", 4000.0, "square_feet", "   ", USER, CorrectionRejected),
    ("empty_reason_none", 4000.0, "square_feet", "", USER, CorrectionRejected),
]


@pytest.mark.parametrize(
    ("name", "value", "units", "reason", "principal", "exc"),
    CORRECTION_REFUSALS,
    ids=[c[0] for c in CORRECTION_REFUSALS],
)
def test_correction_refusals_fail_closed_with_no_write(name, value, units, reason, principal, exc):
    store = _store()
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    with pytest.raises(exc):
        correct_fact(
            store, CorrectFactRequest(DIGEST, "ev-1", value, units, reason, principal, WHEN, fp)
        )
    assert store.load_fact(DIGEST, "ev-1")["correction_history"] == []  # nothing written
    assert store.recalcs == []


def test_professional_correction_without_actor_id_is_refused():
    store = _store()
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    # A professional principal with no actor_id fails authorization before any write.
    with pytest.raises(UnauthorizedReviewAction):
        correct_fact(
            store,
            CorrectFactRequest(
                DIGEST, "ev-1", 4000.0, "square_feet", "fix",
                ReviewPrincipal("human_qualified_professional", None), WHEN, fp,
            ),
        )


def test_correction_on_broken_prior_history_fails_closed():
    # A stored fact carrying a pre-existing correction whose corrected state does NOT match
    # the record's current normalized_value is a broken/forged chain: the shipped
    # whole-record validator refuses the next correction (fail-closed), nothing written.
    store = _store()
    store.facts[(DIGEST, "ev-1")]["correction_history"] = [
        {
            "corrected_at": "2026-08-09T11:00:00+00:00",
            "corrected_by_role": "user",
            "previous_normalized_value": 5000.0,
            "corrected_normalized_value": 4000.0,  # but current normalized_value is 5000
            "previous_units": "square_feet",
            "corrected_units": "square_feet",
            "reason": "prior",
        }
    ]
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    with pytest.raises(CorrectionRejected):
        correct_fact(
            store,
            CorrectFactRequest(DIGEST, "ev-1", 3000.0, "square_feet", "next", USER, WHEN, fp),
        )
    assert len(store.load_fact(DIGEST, "ev-1")["correction_history"]) == 1  # no new append


# ===================================================== illegal transitions (fail closed)


ILLEGAL = [
    ("reject_document_from_auto_extracted", DocumentState.AUTO_EXTRACTED,
     lambda s: reject_document(s, RejectDocumentRequest(DIGEST, "no", PRO, WHEN))),
    ("reject_document_from_confirmed", DocumentState.PROFESSIONALLY_CONFIRMED,
     lambda s: reject_document(s, RejectDocumentRequest(DIGEST, "no", PRO, WHEN))),
    ("confirm_from_processing", DocumentState.PROCESSING,
     lambda s: confirm_document(s, ConfirmDocumentRequest(DIGEST, PRO, WHEN))),
    ("reopen_from_needs_review", DocumentState.NEEDS_REVIEW,
     lambda s: reopen_document(s, ReopenDocumentRequest(DIGEST, "why", PRO, WHEN))),
    ("confirm_from_uploaded", DocumentState.UPLOADED,
     lambda s: confirm_document(s, ConfirmDocumentRequest(DIGEST, PRO, WHEN))),
]


@pytest.mark.parametrize(
    ("name", "state", "call"), ILLEGAL, ids=[c[0] for c in ILLEGAL]
)
def test_illegal_transitions_fail_closed(name, state, call):
    store = _store(state=state)
    before = store.load_document(DIGEST).state
    with pytest.raises(IllegalTransition):
        call(store)
    assert store.load_document(DIGEST).state is before  # unchanged


@pytest.mark.parametrize("empty", ["   ", ""])
def test_reject_document_empty_reason_raises_shipped_transition_reason_required(empty):
    # R4: the error domain is the shipped transition machinery, not a fact-level refusal.
    store = _store()
    with pytest.raises(TransitionReasonRequired):
        reject_document(store, RejectDocumentRequest(DIGEST, empty, PRO, WHEN))
    assert store.audit == []  # no write


@pytest.mark.parametrize("empty", ["   ", ""])
def test_reopen_document_empty_reason_raises_shipped_transition_reason_required(empty):
    store = _store(state=DocumentState.PROFESSIONALLY_CONFIRMED)
    with pytest.raises(TransitionReasonRequired):
        reopen_document(store, ReopenDocumentRequest(DIGEST, empty, PRO, WHEN))


def test_reject_document_terminal_and_audited():
    store = _store()
    result = reject_document(store, RejectDocumentRequest(DIGEST, "wrong property", PRO, WHEN))
    assert store.load_document(DIGEST).state is DocumentState.REJECTED
    assert result.audit_events[0].event_type is ReviewEventType.DOCUMENT_REJECTED
    assert result.audit_events[0].reason == "wrong property"


def test_reopen_confirmed_document_is_audited():
    store = _store(state=DocumentState.PROFESSIONALLY_CONFIRMED)
    result = reopen_document(
        store, ReopenDocumentRequest(DIGEST, "post-confirmation conflict", PRO, WHEN)
    )
    assert store.load_document(DIGEST).state is DocumentState.NEEDS_REVIEW
    assert result.audit_events[0].event_type is ReviewEventType.DOCUMENT_REOPENED
    assert result.recalculation is not None


# ===================================================== edge-6 correction demotion


def test_correction_on_auto_extracted_demotes_to_needs_review_edge6():
    store = _store(state=DocumentState.AUTO_EXTRACTED)
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    result = correct_fact(
        store,
        CorrectFactRequest(
            DIGEST, "ev-1", 4900.0, "square_feet", "off by transcription", USER, WHEN, fp
        ),
    )
    assert result.transitioned is True
    doc = store.load_document(DIGEST)
    assert doc.state is DocumentState.NEEDS_REVIEW
    # The demotion is attributed to the deterministic pipeline (never a user-as-qualified_human);
    # the human is attributed at the fact level.
    last = doc.state_history[-1]
    assert last.actor.kind is ActorKind.DETERMINISTIC_PIPELINE
    assert last.reason == "off by transcription"


def test_correction_on_needs_review_does_not_transition():
    store = _store(state=DocumentState.NEEDS_REVIEW)
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    result = correct_fact(
        store, CorrectFactRequest(DIGEST, "ev-1", 4900.0, "square_feet", "fix", USER, WHEN, fp)
    )
    assert result.transitioned is False
    assert store.load_document(DIGEST).state is DocumentState.NEEDS_REVIEW


# ===================================================== not-found (fail closed)


def test_missing_document_is_typed_not_found():
    store = InMemoryReviewStore()
    with pytest.raises(DocumentRecordNotFound):
        read_document_review(store, DIGEST, USER)


def test_missing_fact_is_typed_not_found():
    store = _store()
    with pytest.raises(FactNotFound):
        accept_fact(store, AcceptFactRequest(DIGEST, "nope", USER, WHEN))


# ============================================ R1: rejected fact blocks confirmation


def test_r1_professionally_rejected_fact_blocks_confirmation_and_is_not_overwritten():
    # Invariant: a professionally-rejected (yet deterministically resolved) material fact
    # blocks document confirmation and is NEVER relabeled "confirmed".
    store = _store(facts=[make_fact("ev-1"), make_fact("ev-2")])
    reject_fact(store, RejectFactRequest(DIGEST, "ev-2", "detection unusable", PRO, WHEN))
    # ev-2 is deterministically promotable, so only the explicit reject-state check catches it.
    assert isinstance(store.promotion_verdict(DIGEST, "ev-2"), PromotionAllowed)
    with pytest.raises(ConfirmationRejected) as exc:
        confirm_document(store, ConfirmDocumentRequest(DIGEST, PRO, WHEN))
    assert "ev-2" in exc.value.payload["detail"]["rejected_fact_ids"]
    # The document did not transition and ev-2 stays rejected (never overwritten).
    assert store.load_document(DIGEST).state is DocumentState.NEEDS_REVIEW
    assert store.load_fact(DIGEST, "ev-2")["professional_confirmation"]["state"] == "rejected"


def test_r1_read_model_lists_rejected_fact_as_blocking():
    store = _store(facts=[make_fact("ev-1"), make_fact("ev-2")])
    reject_fact(store, RejectFactRequest(DIGEST, "ev-2", "illegible", PRO, WHEN))
    view = read_document_review(store, DIGEST, PRO)
    assert "ev-2" in view.blocking_fact_ids
    assert view.confirm_precondition_met is False
    impacts = {f.evidence_id: f.downstream_impact for f in view.facts}
    assert impacts["ev-2"].impact_kind is DownstreamImpactKind.BLOCKED


# ==================================== R2: no silent post-confirmation fact edits


@pytest.mark.parametrize(
    "call",
    [
        lambda s: correct_fact(
            s,
            CorrectFactRequest(
                DIGEST, "ev-1", 9999.0, "square_feet", "sneaky", PRO, WHEN,
                history_fingerprint(s.load_fact(DIGEST, "ev-1")["correction_history"]),
            ),
        ),
        lambda s: reject_fact(s, RejectFactRequest(DIGEST, "ev-1", "sneaky", PRO, WHEN)),
    ],
    ids=["correct", "reject"],
)
def test_r2_fact_edit_on_confirmed_document_is_refused(call):
    # Build a genuinely confirmed document end to end.
    store = _store(facts=[make_fact("ev-1")])
    confirm_document(store, ConfirmDocumentRequest(DIGEST, PRO, WHEN))
    assert store.load_document(DIGEST).state is DocumentState.PROFESSIONALLY_CONFIRMED
    before_value = store.load_fact(DIGEST, "ev-1")["normalized_value"]
    with pytest.raises(PostConfirmationEditRefused):
        call(store)
    # Nothing changed — the confirmed review is intact until an explicit reopen.
    assert store.load_fact(DIGEST, "ev-1")["normalized_value"] == before_value
    assert store.load_document(DIGEST).state is DocumentState.PROFESSIONALLY_CONFIRMED


def test_r2_reopen_then_correct_is_allowed_and_audited():
    store = _store(facts=[make_fact("ev-1")])
    confirm_document(store, ConfirmDocumentRequest(DIGEST, PRO, WHEN))
    reopen_document(
        store, ReopenDocumentRequest(DIGEST, "post-confirmation contradiction", PRO, WHEN)
    )
    assert store.load_document(DIGEST).state is DocumentState.NEEDS_REVIEW
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    result = correct_fact(
        store,
        CorrectFactRequest(DIGEST, "ev-1", 4700.0, "square_feet", "true value", PRO, WHEN, fp),
    )
    assert result.correction_count == 1
    assert store.load_fact(DIGEST, "ev-1")["normalized_value"] == 4700.0
    assert result.audit_events[0].event_type is ReviewEventType.FACT_CORRECTED


# ==================================== R3: real immutable-original cross-check


def test_r3_tampered_stored_original_is_detected_by_correction_cross_check():
    # The independently-held original ("AREA = 5000 SF") diverges from a mutated stored
    # original_value; the shipped expected-original cross-check now actually fires.
    store = _store()
    store.facts[(DIGEST, "ev-1")]["original_value"] = "TAMPERED = 9999 SF"
    assert store.original_fact_value(DIGEST, "ev-1") == "AREA = 5000 SF"  # pristine snapshot
    fp = history_fingerprint(store.load_fact(DIGEST, "ev-1")["correction_history"])
    with pytest.raises(CorrectionRejected) as exc:
        correct_fact(
            store,
            CorrectFactRequest(DIGEST, "ev-1", 4800.0, "square_feet", "fix", USER, WHEN, fp),
        )
    assert exc.value.payload["detail"]["reject_code"] == "unresolved_correction_history"
    assert store.load_fact(DIGEST, "ev-1")["correction_history"] == []  # no write
