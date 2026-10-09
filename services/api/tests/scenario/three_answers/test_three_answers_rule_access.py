"""A-04 review-correction tests: the dwelling-unit factor is read from the rule table (F1),
and the results validator fails closed on an invalid document (N3). Directive D-090.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.scenario.three_answers import (
    ResultsContractError,
    generate_results,
    validate_results_document,
)
from app.scenario.three_answers.dwelling_units import build_unit_estimate

from .test_three_answers_benchmark import _ON, _benchmark_inputs, _generate


class _StubRule:
    """A minimal r6b-dwelling-units rule carrying a NON-680 declared factor."""

    def __init__(self, factor: float) -> None:
        self.rule_id = "r6b-dwelling-units"
        self.rule_version = "9.9.9-stub"
        self.status = "needs_review"
        self.parameters = {
            "dwelling_unit_factor": factor,
            "fraction_counted_as_one_dwelling_unit": 0.75,
        }


class _StubRegistry:
    """Evaluates the dwelling-unit division with its OWN factor, so the estimate, the factor
    field and the formula all move together when the rule's factor changes."""

    def __init__(self, factor: float) -> None:
        self.factor = factor

    def rule_ids(self):
        return ["r6b-dwelling-units"]

    def rule(self, rule_id):
        assert rule_id == "r6b-dwelling-units"
        return _StubRule(self.factor)

    def evaluate(self, rule_id, inputs):
        area = inputs["max_residential_floor_area_sq_ft"]
        before = area / self.factor
        whole = int(before)
        units = whole + (1 if (before - whole) >= 0.75 else 0)
        return SimpleNamespace(
            coverage_status="conditional",
            outputs={
                "dwelling_units_before_rounding": before,
                "max_dwelling_units": float(units),
            },
            trace=SimpleNamespace(
                citations=[{"snapshot_id": "zr-23-52", "section": "23-52"}],
                data_completeness="complete",
            ),
        )


def test_factor_is_read_from_the_rule_table_not_a_literal() -> None:
    # Real registry: the rule's declared factor 680 drives both fields and the formula.
    real = _generate().document["unit_estimate"]
    assert real["factor"]["value"] == 680.0
    assert real["formula"] == "20,150 ÷ 680 = 29.63"
    assert real["value"] == 29

    # Stub registry with a DIFFERENT factor (500): the factor field, the formula text and the
    # computed estimate all change together, proving nothing is hard-coded to 680.
    stub = _StubRegistry(factor=500.0)
    estimate = build_unit_estimate(_benchmark_inputs(), stub, 20150.0)
    assert estimate["factor"]["value"] == 500.0
    assert estimate["formula"] == "20,150 ÷ 500 = 40.30"
    assert estimate["value"] == 40  # 20,150 / 500 = 40.30 -> 40, from the stub's own output


def test_validate_results_document_rejects_an_invalid_document() -> None:
    # N3: additionalProperties:false - an extra top-level key must fail closed.
    doc = generate_results(_benchmark_inputs(), env=_ON).document  # valid
    validate_results_document(doc)  # sanity: the valid document passes
    doc["unexpected_extra_key"] = True
    with pytest.raises(ResultsContractError):
        validate_results_document(doc)
