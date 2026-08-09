"""H5 promotion-gate WIRING tests (M2-T015 unit 3f-2; D-010 R265).

Prove the three evidence-promoting edges consume :mod:`app.documents.promotion`
verdicts as a transition PRECONDITION: ``processing -> auto_extracted`` and both
professional-confirmation edges refuse without a ``PromotionAllowed`` verdict for
every material fact and succeed with one; already-refused evidence (including an
AI-only submission) and raw AI values (confidence numbers, classifications, model
output) cannot cross either path; the state machine remains the only transition
authority; and non-gated edges behave exactly as before.

Allowed verdicts are obtained from the REAL ``evaluate_promotion`` — never
hand-built — so these tests exercise the actual gate contract end to end.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from app.documents.promotion import (
    REQUIRED_VALIDATIONS,
    PromotionAllowed,
    PromotionRefused,
    evaluate_promotion,
)
from app.documents.state import (
    PROMOTION_GATED_TRANSITIONS,
    ActorKind,
    DocumentState as S,
    IllegalTransition,
    TransitionActor,
    TransitionRecord,
    UnauthorizedTransitionActor,
    promotion_gated_transition,
    transition,
)

WHEN = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)
PIPELINE = TransitionActor(ActorKind.DETERMINISTIC_PIPELINE, actor_id="worker-7")
HUMAN = TransitionActor(ActorKind.QUALIFIED_HUMAN, actor_id="reviewer-1")

#: Each gated edge with the actor kind the section-4 table authorizes for it.
GATED_EDGES = [
    (S.PROCESSING, S.AUTO_EXTRACTED, PIPELINE),
    (S.AUTO_EXTRACTED, S.PROFESSIONALLY_CONFIRMED, HUMAN),
    (S.NEEDS_REVIEW, S.PROFESSIONALLY_CONFIRMED, HUMAN),
]

#: A deterministically chosen taxonomy member that requires at least one validation.
_FACT_TYPE = sorted(
    (ft for ft in REQUIRED_VALIDATIONS if REQUIRED_VALIDATIONS[ft]),
    key=lambda ft: str(getattr(ft, "value", ft)),
)[0]
_WIRE_FACT_TYPE = str(getattr(_FACT_TYPE, "value", _FACT_TYPE))


@dataclass(frozen=True)
class _ResolvedResult:
    """Minimal typed result per the promotion evidence contract: affirmative
    ``resolved is True``, no ``reject_code`` attribute, identifies the fact type."""

    resolved: bool
    fact_type: object


def _allowed_verdict() -> PromotionAllowed:
    results = {
        kind: (_ResolvedResult(resolved=True, fact_type=_FACT_TYPE),)
        for kind in REQUIRED_VALIDATIONS[_FACT_TYPE]
    }
    verdict = evaluate_promotion(_WIRE_FACT_TYPE, results, "ocr_text", None)
    assert isinstance(verdict, PromotionAllowed), (
        "test harness could not obtain a PromotionAllowed from the real "
        f"evaluate_promotion; got {verdict!r}"
    )
    return verdict


def _ai_only_refused_verdict() -> PromotionRefused:
    """AI-only submission: high confidence, zero deterministic validations."""
    verdict = evaluate_promotion(_WIRE_FACT_TYPE, {}, "ai_assisted_classification", 0.99)
    assert isinstance(verdict, PromotionRefused)
    return verdict


def test_gated_edge_set_is_exactly_the_three_promotion_edges():
    assert PROMOTION_GATED_TRANSITIONS == frozenset(
        (frm, to) for frm, to, _ in GATED_EDGES
    )


@pytest.mark.parametrize(("frm", "to", "actor"), GATED_EDGES)
def test_gated_edges_refuse_without_verdicts(frm, to, actor):
    with pytest.raises(IllegalTransition) as exc:
        promotion_gated_transition(frm, to, actor=actor, occurred_at=WHEN)
    assert exc.value.from_state is frm
    assert exc.value.to_state is to
    assert "promotion gate" in str(exc.value)


@pytest.mark.parametrize(("frm", "to", "actor"), GATED_EDGES)
def test_gated_edges_refuse_an_empty_verdict_mapping(frm, to, actor):
    with pytest.raises(IllegalTransition):
        promotion_gated_transition(
            frm, to, actor=actor, occurred_at=WHEN, material_fact_verdicts={}
        )


def test_processing_to_auto_extracted_refuses_when_any_material_fact_is_unproven():
    verdicts = {"fact-1": _allowed_verdict(), "fact-2": _ai_only_refused_verdict()}
    with pytest.raises(IllegalTransition) as exc:
        promotion_gated_transition(
            S.PROCESSING,
            S.AUTO_EXTRACTED,
            actor=PIPELINE,
            occurred_at=WHEN,
            material_fact_verdicts=verdicts,
        )
    assert "'fact-2'" in str(exc.value)


def test_processing_to_auto_extracted_succeeds_with_allowed_verdict_for_every_fact():
    verdicts = {"fact-1": _allowed_verdict(), "fact-2": _allowed_verdict()}
    record = promotion_gated_transition(
        S.PROCESSING,
        S.AUTO_EXTRACTED,
        actor=PIPELINE,
        occurred_at=WHEN,
        material_fact_verdicts=verdicts,
    )
    assert isinstance(record, TransitionRecord)
    assert record.from_state is S.PROCESSING
    assert record.to_state is S.AUTO_EXTRACTED
    assert record.actor is PIPELINE
    assert record.occurred_at == WHEN


@pytest.mark.parametrize("frm", [S.AUTO_EXTRACTED, S.NEEDS_REVIEW])
def test_professional_confirmation_refuses_unvalidated_or_refused_evidence(frm):
    for unproven in (None, {}, {"fact-1": _ai_only_refused_verdict()}):
        with pytest.raises(IllegalTransition):
            promotion_gated_transition(
                frm,
                S.PROFESSIONALLY_CONFIRMED,
                actor=HUMAN,
                occurred_at=WHEN,
                material_fact_verdicts=unproven,
            )


@pytest.mark.parametrize("frm", [S.AUTO_EXTRACTED, S.NEEDS_REVIEW])
def test_professional_confirmation_succeeds_with_proven_evidence(frm):
    record = promotion_gated_transition(
        frm,
        S.PROFESSIONALLY_CONFIRMED,
        actor=HUMAN,
        occurred_at=WHEN,
        material_fact_verdicts={"fact-1": _allowed_verdict()},
    )
    assert record.to_state is S.PROFESSIONALLY_CONFIRMED


@pytest.mark.parametrize(("frm", "to", "actor"), GATED_EDGES)
@pytest.mark.parametrize(
    "ai_value",
    [
        0.99,
        "professionally_confirmed",
        {"classification": "survey", "confidence": 0.99},
        True,
    ],
    ids=["confidence-number", "classification-string", "model-output", "bare-flag"],
)
def test_ai_values_cannot_stand_in_for_typed_verdicts(frm, to, actor, ai_value):
    with pytest.raises(IllegalTransition):
        promotion_gated_transition(
            frm,
            to,
            actor=actor,
            occurred_at=WHEN,
            material_fact_verdicts={"fact-1": ai_value},
        )


def test_ai_only_evidence_cannot_cross_either_path():
    refused = _ai_only_refused_verdict()
    for frm, to, actor in GATED_EDGES:
        with pytest.raises(IllegalTransition):
            promotion_gated_transition(
                frm,
                to,
                actor=actor,
                occurred_at=WHEN,
                material_fact_verdicts={"fact-1": refused},
            )


def test_gate_adds_precondition_not_authority():
    # Proven evidence does NOT let an unauthorized actor kind cross a gated edge...
    with pytest.raises(UnauthorizedTransitionActor):
        promotion_gated_transition(
            S.AUTO_EXTRACTED,
            S.PROFESSIONALLY_CONFIRMED,
            actor=PIPELINE,
            occurred_at=WHEN,
            material_fact_verdicts={"fact-1": _allowed_verdict()},
        )
    # ...and does NOT legalize an edge outside the section-4 table.
    with pytest.raises(IllegalTransition, match="section-4 transition table"):
        promotion_gated_transition(
            S.UPLOADED,
            S.AUTO_EXTRACTED,
            actor=PIPELINE,
            occurred_at=WHEN,
            material_fact_verdicts={"fact-1": _allowed_verdict()},
        )


def test_non_gated_transition_unchanged():
    direct = transition(S.UPLOADED, S.PROCESSING, actor=PIPELINE, occurred_at=WHEN)
    gated = promotion_gated_transition(
        S.UPLOADED, S.PROCESSING, actor=PIPELINE, occurred_at=WHEN
    )
    assert gated == direct
    # The plain non-table refusal keeps its exact pre-wiring message.
    with pytest.raises(IllegalTransition, match="is not an edge of the section-4 transition table"):
        transition(S.UPLOADED, S.AUTO_EXTRACTED, actor=PIPELINE, occurred_at=WHEN)
