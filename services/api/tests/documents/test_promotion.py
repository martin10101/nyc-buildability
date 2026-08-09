"""Tests for the deterministic promotion gate (app.documents.promotion; M2-T015).

Prove each refusal condition cannot cross the gate — absent, empty (visible
mid-state), failed (typed refusal value), unresolved, incomplete for the fact type,
tampered/inconsistent (wrong fact type, contradictory flags, ambiguous or
unrecognized evidence), and AI/OCR-only evidence at any confidence — and that one
fully validated fact can. Confidence and extraction method are swept to prove they
carry ZERO deterministic weight: identical evidence yields an identical verdict at
every confidence value and under every extraction method.

Normalized-value evidence uses REAL typed results from
:func:`app.documents.units.validate_normalized_value`. Location and
correction-history evidence uses frozen stand-in results conforming to the gate's
structural evidence contract (``resolved is True``, no ``reject_code``, fact-type
identity) — the real validators' typed results are bound in the state-machine wiring
unit, not here.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass

import pytest

from app.documents.promotion import (
    REQUIRED_VALIDATIONS,
    ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS,
    PromotionAllowed,
    PromotionRefused,
    ValidationKind,
    evaluate_promotion,
)
from app.documents.taxonomy import SurveyFactType
from app.documents.units import (
    UnresolvedNormalizedValue,
    ValidatedArea,
    validate_normalized_value,
)

# Swept over every verdict-invariance test: no value here may change any verdict.
CONFIDENCE_SWEEP = [None, 0.0, 0.31, 0.999999, 1.0, -1.0, float("nan"), "certain", 10**9]


@dataclass(frozen=True)
class _ResolvedResult:
    """Stand-in RESOLVED validator result per the gate's structural contract."""

    fact_type: object

    resolved = True


@dataclass(frozen=True)
class _RefusalResult:
    """Stand-in typed refusal value (the convention's reject_code marker)."""

    fact_type: object
    reason: str = "correction history integrity violated"

    resolved = False
    reject_code = "correction_history_integrity"


@dataclass(frozen=True)
class _NoFlagResult:
    """Stand-in result that never declares itself resolved."""

    fact_type: object


@dataclass(frozen=True)
class _StringFlagResult:
    """Stand-in claiming resolved with a truthy NON-``True`` value — not affirmative."""

    fact_type: object

    resolved = "yes"


@dataclass(frozen=True)
class _ContradictoryResult:
    """Stand-in claiming resolved yet carrying a reject_code — tampered evidence."""

    fact_type: object

    resolved = True
    reject_code = "tampered"


def _validated_area() -> ValidatedArea:
    result = validate_normalized_value("stated_lot_area", 5000.0, "square_feet")
    assert isinstance(result, ValidatedArea)
    return result


def _refused_area() -> UnresolvedNormalizedValue:
    result = validate_normalized_value("stated_lot_area", "5000", "square_feet")
    assert isinstance(result, UnresolvedNormalizedValue)
    return result


def _full_evidence() -> dict:
    return {
        "normalized_value": [_validated_area()],
        "correction_history": [_ResolvedResult(fact_type=SurveyFactType.STATED_LOT_AREA)],
    }


def _promote(
    fact_type: object = "stated_lot_area",
    validation_results: object = None,
    extraction_method: object = "pdf_vector_text",
    confidence: object = 0.9,
):
    return evaluate_promotion(fact_type, validation_results, extraction_method, confidence)


class TestPromotionAllowed:
    def test_fully_validated_fact_promotes(self):
        verdict = _promote(validation_results=_full_evidence(), confidence=0.42)
        assert isinstance(verdict, PromotionAllowed)
        assert verdict.allowed is True
        assert verdict.promotable is True
        assert verdict.fact_type is SurveyFactType.STATED_LOT_AREA
        assert [kind for kind, _ in verdict.grounds] == [
            "normalized_value",
            "correction_history",
        ]
        assert verdict.submitted_extraction_method == "pdf_vector_text"
        assert verdict.submitted_confidence == repr(0.42)

    def test_confidence_has_no_influence_on_allowance(self):
        verdicts = [
            _promote(validation_results=_full_evidence(), confidence=confidence)
            for confidence in CONFIDENCE_SWEEP
        ]
        for verdict in verdicts:
            assert isinstance(verdict, PromotionAllowed)
            assert verdict.fact_type is SurveyFactType.STATED_LOT_AREA
            assert verdict.grounds == verdicts[0].grounds

    def test_extraction_method_carries_zero_weight_but_never_blocks(self):
        # Zero weight is not negative weight: an AI/OCR-extracted fact whose
        # deterministic validations are complete and resolved promotes.
        for method in sorted(ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS) + [
            "deterministic_geometry_reconstruction",
            12345,
        ]:
            verdict = _promote(
                validation_results=_full_evidence(), extraction_method=method
            )
            assert isinstance(verdict, PromotionAllowed)
            assert verdict.grounds[0][0] == "normalized_value"

    def test_polygon_promotes_on_location_and_history_not_unit_typing(self):
        member = SurveyFactType.RECONSTRUCTED_BOUNDARY_POLYGON
        verdict = _promote(
            fact_type="reconstructed_boundary_polygon",
            validation_results={
                ValidationKind.LOCATION: [_ResolvedResult(fact_type=member)],
                ValidationKind.CORRECTION_HISTORY: [_ResolvedResult(fact_type=member)],
            },
        )
        assert isinstance(verdict, PromotionAllowed)
        assert verdict.fact_type is member


class TestAbsentOrEmptyEvidence:
    def test_no_evidence_refuses(self):
        verdict = _promote(validation_results={})
        assert isinstance(verdict, PromotionRefused)
        assert verdict.allowed is False
        assert verdict.promotable is False
        assert any("'normalized_value'" in r and "absent" in r for r in verdict.reasons)
        assert any(
            "'correction_history'" in r and "absent" in r for r in verdict.reasons
        )

    @pytest.mark.parametrize("missing", ["normalized_value", "correction_history"])
    def test_missing_one_required_validation_refuses(self, missing):
        evidence = _full_evidence()
        del evidence[missing]
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any(f"{missing!r}" in r and "absent" in r for r in verdict.reasons)

    @pytest.mark.parametrize("emptied", ["normalized_value", "correction_history"])
    def test_empty_result_list_refuses(self, emptied):
        evidence = _full_evidence()
        evidence[emptied] = []
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any(
            f"{emptied!r}" in r and "empty result list" in r for r in verdict.reasons
        )
        assert any("visible mid-state" in r for r in verdict.reasons)


class TestFailedOrUnresolvedEvidence:
    def test_typed_refusal_value_refuses(self):
        evidence = _full_evidence()
        evidence["normalized_value"] = [_refused_area()]
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any("typed refusal value" in r for r in verdict.reasons)
        assert any("never promotable" in r for r in verdict.reasons)

    def test_refusal_alongside_resolved_results_still_refuses(self):
        evidence = _full_evidence()
        evidence["normalized_value"] = [_validated_area(), _refused_area()]
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)

    @pytest.mark.parametrize(
        "result",
        [
            _NoFlagResult(fact_type=SurveyFactType.STATED_LOT_AREA),
            _StringFlagResult(fact_type=SurveyFactType.STATED_LOT_AREA),
            object(),
        ],
        ids=["no-flag", "truthy-non-True-flag", "foreign-shape"],
    )
    def test_unresolved_result_refuses(self, result):
        evidence = _full_evidence()
        evidence["correction_history"] = [result]
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any("affirmatively declare itself resolved" in r for r in verdict.reasons)

    def test_confidence_of_any_value_never_rescues_a_failure(self):
        evidence = _full_evidence()
        evidence["normalized_value"] = [_refused_area()]
        verdicts = [
            _promote(validation_results=evidence, confidence=confidence)
            for confidence in CONFIDENCE_SWEEP
        ]
        for verdict in verdicts:
            assert isinstance(verdict, PromotionRefused)
            assert verdict.reasons == verdicts[0].reasons


class TestInconsistentOrTamperedEvidence:
    def test_incomplete_for_fact_type_refuses(self):
        member = SurveyFactType.RECONSTRUCTED_BOUNDARY_POLYGON
        verdict = _promote(
            fact_type="reconstructed_boundary_polygon",
            validation_results={
                "correction_history": [_ResolvedResult(fact_type=member)]
            },
        )
        assert isinstance(verdict, PromotionRefused)
        assert any("'location'" in r and "absent" in r for r in verdict.reasons)

    def test_result_for_different_fact_type_refuses(self):
        # A resolved stated_lot_area result cannot ground a calculated_lot_area fact.
        verdict = _promote(
            fact_type="calculated_lot_area",
            validation_results={
                "normalized_value": [_validated_area()],
                "correction_history": [
                    _ResolvedResult(fact_type=SurveyFactType.CALCULATED_LOT_AREA)
                ],
            },
        )
        assert isinstance(verdict, PromotionRefused)
        assert any(
            "identifies fact type" in r and "'calculated_lot_area'" in r
            for r in verdict.reasons
        )

    def test_contradictory_result_refuses(self):
        evidence = _full_evidence()
        evidence["correction_history"] = [
            _ContradictoryResult(fact_type=SurveyFactType.STATED_LOT_AREA)
        ]
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any("internally contradictory" in r for r in verdict.reasons)
        assert any("tampered" in r for r in verdict.reasons)

    def test_unknown_validation_kind_refuses(self):
        evidence = _full_evidence()
        evidence["vibes"] = [_ResolvedResult(fact_type=SurveyFactType.STATED_LOT_AREA)]
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any("unrecognized validation kind 'vibes'" in r for r in verdict.reasons)

    def test_duplicate_kind_submission_refuses(self):
        evidence = _full_evidence()
        evidence[ValidationKind.NORMALIZED_VALUE] = [_validated_area()]
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any("more than once" in r for r in verdict.reasons)

    def test_bare_result_outside_sequence_refuses(self):
        evidence = _full_evidence()
        evidence["normalized_value"] = _validated_area()
        verdict = _promote(validation_results=evidence)
        assert isinstance(verdict, PromotionRefused)
        assert any("must be a list/tuple" in r for r in verdict.reasons)

    @pytest.mark.parametrize("bad", [None, 5, [("normalized_value", [])]])
    def test_non_mapping_evidence_refuses(self, bad):
        verdict = _promote(validation_results=bad)
        assert isinstance(verdict, PromotionRefused)
        assert any("must be a mapping" in r for r in verdict.reasons)


class TestAiOnlyEvidence:
    @pytest.mark.parametrize(
        "method", sorted(ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS)
    )
    def test_ai_only_evidence_cannot_cross_the_gate(self, method):
        # An AI/OCR extraction with sky-high confidence and no deterministic
        # validation results is refused for the missing validations — the
        # confidence number never substitutes.
        verdicts = [
            _promote(
                validation_results={},
                extraction_method=method,
                confidence=confidence,
            )
            for confidence in CONFIDENCE_SWEEP
        ]
        for verdict in verdicts:
            assert isinstance(verdict, PromotionRefused)
            assert verdict.reasons == verdicts[0].reasons
            assert any("never substitutes" in r for r in verdict.reasons)

    @pytest.mark.parametrize(
        "method", sorted(ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS)
    )
    def test_ai_extraction_with_failed_validation_refuses(self, method):
        evidence = _full_evidence()
        evidence["normalized_value"] = [_refused_area()]
        verdict = _promote(
            validation_results=evidence, extraction_method=method, confidence=1.0
        )
        assert isinstance(verdict, PromotionRefused)

    def test_zero_weight_set_names_ai_and_ocr(self):
        assert ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS == {
            "ai_assisted_classification",
            "ocr_text",
        }


class TestGateFoundations:
    def test_required_map_covers_every_taxonomy_member(self):
        assert set(REQUIRED_VALIDATIONS) == set(SurveyFactType)
        for member, kinds in REQUIRED_VALIDATIONS.items():
            assert kinds, f"{member.value} must require at least one validation"
            assert all(isinstance(kind, ValidationKind) for kind in kinds)

    def test_required_map_is_immutable(self):
        with pytest.raises(TypeError):
            REQUIRED_VALIDATIONS[SurveyFactType.STATED_LOT_AREA] = frozenset()

    @pytest.mark.parametrize(
        "bad_fact_type",
        ["Stated_Lot_Area", " stated_lot_area", "", "zoning_district", 5, None],
        ids=["case", "whitespace", "empty", "unknown", "int", "none"],
    )
    def test_unsupported_fact_type_refuses(self, bad_fact_type):
        verdict = _promote(
            fact_type=bad_fact_type, validation_results=_full_evidence()
        )
        assert isinstance(verdict, PromotionRefused)
        assert any("canonical taxonomy" in r for r in verdict.reasons)

    def test_refusal_is_a_value_with_verbatim_submission_and_payload(self):
        verdict = _promote(validation_results={}, confidence=0.87)
        assert isinstance(verdict, PromotionRefused)
        assert verdict.reject_code == "promotion_refused"
        assert verdict.submitted_fact_type == "stated_lot_area"
        assert verdict.submitted_confidence == repr(0.87)
        assert verdict.submitted_extraction_method == "pdf_vector_text"
        payload = verdict.to_payload()
        assert json.loads(json.dumps(payload)) == payload
        assert payload["reasons"] == list(verdict.reasons)

    def test_verdicts_are_frozen(self):
        allowed = _promote(validation_results=_full_evidence())
        refused = _promote(validation_results={})
        with pytest.raises(dataclasses.FrozenInstanceError):
            allowed.fact_type = SurveyFactType.BBL_TEXT
        with pytest.raises(dataclasses.FrozenInstanceError):
            refused.reasons = ()
