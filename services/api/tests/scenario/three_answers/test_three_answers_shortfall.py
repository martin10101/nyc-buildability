"""A-04 shortfall red/green tests (competitor-review checks C-2, C-11; directive D-090).

A shortfall reason is COMPUTED from real constraints and emitted only when the building
option cannot reach the allowance. These tests pin the flip: the same engine returns 'none'
when the envelope holds the whole allowance (green) and a true, numbers-bearing reason when
it cannot (red). The core is pure, exact feet arithmetic.
"""

from __future__ import annotations

from app.scenario.three_answers import compute_building_option, validate_results_document
from app.scenario.three_answers.answers import AllowanceResult, EnvelopeResult
from app.scenario.three_answers.building_option import build_building_option, shortfall_reason
from app.scenario.three_answers.inputs import MEASUREMENT_ASSUMED

from .test_three_answers_benchmark import _benchmark_inputs, _generate


def _allowance(sf: float) -> AllowanceResult:
    return AllowanceResult(
        answer={
            "status": "available",
            "values": [
                {
                    "key": "max_residential_floor_area",
                    "label": "Maximum residential floor area (standard)",
                    "value": sf,
                    "unit": "square_feet",
                    "zr_sections": ["ZR 23-22"],
                    "sources": [
                        {"kind": "rule_table", "ref": "r6-r12-residential-far@0.1.0-draft"}
                    ],
                    "exception_label": None,
                }
            ],
            "measurement": {"rank": "city_records", "label": "City records"},
        },
        standard_floor_area_sq_ft=sf,
        standard_far=2.0,
        qualifying_floor_area_sq_ft=None,
        rule_versions=(),
    )


def _envelope(coverage_ratio: float) -> EnvelopeResult:
    return EnvelopeResult(
        answer={
            "status": "available",
            "values": [],
            "measurement": {"rank": "city_records", "label": "City records"},
        },
        max_building_height_ft=55.0,
        max_base_height_ft=45.0,
        min_base_height_ft=30.0,
        max_lot_coverage_ratio=coverage_ratio,
        rear_yard_required=False,
        height_zr_sections=("ZR 23-432",),
        coverage_zr_sections=("ZR 23-362",),
        rear_yard_zr_sections=("ZR 23-344(a)",),
        rule_versions=(),
    )


def test_green_no_shortfall_when_envelope_holds_allowance() -> None:
    comp = compute_building_option(
        allowance_sf=20150.0, plate_sf=10075.0, max_building_height_ft=55.0, floor_to_floor_ft=10.0
    )
    assert comp is not None
    assert comp.envelope_capacity_sf == 50375.0  # 5 floors x 10,075 >= allowance
    assert comp.achieved_sf == 20150.0
    assert comp.floors_built == 2
    assert comp.shortfall_sf == 0.0


def test_red_shortfall_present_with_true_reason_when_envelope_too_small() -> None:
    comp = compute_building_option(
        allowance_sf=20150.0, plate_sf=2000.0, max_building_height_ft=55.0, floor_to_floor_ft=10.0
    )
    assert comp is not None
    assert comp.floors_fit_under_height == 5
    assert comp.envelope_capacity_sf == 10000.0  # 5 x 2,000, all full plates
    assert comp.achieved_sf == 10000.0
    assert comp.shortfall_sf == 10150.0  # 20,150 - 10,000, exact

    reason = shortfall_reason(comp, coverage_ratio=0.2)
    # Reason computed from the named constraints, with the real numbers compared (C-11).
    assert set(reason["computed_from"]) == {
        "max_building_height",
        "max_lot_coverage",
        "max_residential_floor_area",
    }
    values = {v["name"]: v["value"] for v in reason["values"]}
    assert values["envelope_capacity"] == 10000.0
    assert values["allowance"] == 20150.0
    assert values["shortfall"] == 10150.0
    assert "10,000" in reason["text"] and "20,150" in reason["text"] and "55 ft" in reason["text"]


def test_shortfall_flips_between_wide_and_tight_envelope_via_the_wiring() -> None:
    inputs = _benchmark_inputs()
    # Green: the full-coverage corner lot reaches the allowance -> no shortfall, no reason.
    green = build_building_option(inputs, _allowance(20150.0), _envelope(1.0), MEASUREMENT_ASSUMED)
    assert green.shortfall == {"status": "none"}
    # Red: shrink coverage to 20% (plate 2,015 sq ft) -> the envelope cannot hold the allowance.
    red = build_building_option(inputs, _allowance(20150.0), _envelope(0.2), MEASUREMENT_ASSUMED)
    assert red.shortfall["status"] == "shortfall"
    assert red.shortfall["sq_ft"] > 0
    assert len(red.shortfall["reasons"]) >= 1
    assert red.shortfall["sq_ft"] == 20150.0 - red.computation.envelope_capacity_sf


def test_shortfall_present_block_is_schema_valid_in_a_full_document() -> None:
    # Prove the shortfall_present shape validates inside a complete results-v1 document by
    # injecting a computed red shortfall into an otherwise-green benchmark document.
    doc = _generate().document
    inputs = _benchmark_inputs()
    red = build_building_option(inputs, _allowance(20150.0), _envelope(0.2), MEASUREMENT_ASSUMED)
    doc["shortfall"] = red.shortfall
    doc["answers"]["building_option"] = red.answer
    doc["floor_by_floor"] = red.floor_by_floor
    doc["floor_stack"] = red.floor_stack
    validate_results_document(doc)  # raises on any defect
