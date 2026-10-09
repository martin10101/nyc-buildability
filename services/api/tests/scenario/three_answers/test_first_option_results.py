"""PART B of task M5-T146: the first-building-option assembly (first_option_results.py).

One test per acceptance scenario (S7, S9, S10, S11, S13, S14). Every EXPECTED figure is parsed from
the independent hand-worked example ``docs/reference-cases/R6B/cases/step-p6-worked.json`` (rows
real-building-b, real-estimate-b, made-up-building-a), never retyped and never taken from a run of
the module under test. The module keeps its figures unrounded; the reference records them to two
decimals, so a figure is compared within ``_TOL`` = 0.01 (the reference's own precision).

The assembly is a pure function. The benchmark path (the conflicting-area case the server wires
end to end) is exercised with ``corner_areas=None`` - exactly what the emit transform passes, since
the measured corner-reach areas are not needed where the footprint is withheld. The agree case
(S13) and the no-coverage states (S14) are exercised with a constructed corner-reach measurement.
"""

from __future__ import annotations

import json
import math
import pathlib

from app.scenario.three_answers.first_option_results import (
    FirstOptionInputs,
    assemble_first_option,
    max_lot_coverage_value_state,
)
from app.spatial.corner_reach_area import (
    STATE_NO_CONFIRMED_STREET,
    STATE_ONE_CONFIRMED_STREET,
    STATE_OUTLINE_REFUSED,
    CornerPortionAreas,
)
from app.spatial.site_geometry.labels import unknown_value

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]
_CASE = _REPO_ROOT / "docs" / "reference-cases" / "R6B" / "cases" / "step-p6-worked.json"
_TOL = 0.01  # the reference records figures to two decimals; the module keeps them unrounded

# The settled R6B envelope the scenarios pass as INPUTS (not expected values).
_MIN_BASE = 30.0
_MAX_BASE = 45.0
_F2F = 10.0

# The value-state conditions the emit transform reuses from the floor-area answer. On the benchmark
# (the two lot areas disagree) they are the contradicted-record and the unchecked-conditions; where
# the areas agree, only the unchecked-conditions.
_CONTRADICTED = {
    "kind": "contradicted_record",
    "assumption": "If the recorded lot area of 10,075 sq ft is confirmed",
    "settled_by": "A survey or deed dimensions",
}
_UNCHECKED = {
    "kind": "unchecked_condition",
    "assumption": "If none of the unchecked conditions applies to this lot",
    "settled_by": "Capturing and reading the governing law text, then confirming it is absent",
}


def _case() -> dict:
    return json.loads(_CASE.read_text(encoding="utf-8"))


def _numbers_block(row_id: str) -> dict:
    for row in _case()["rows"]:
        if row["row_id"] == row_id:
            return row["numbers_block"]
    raise AssertionError(f"row {row_id} not found in {_CASE}")


def _num(value, reading: str | None = None) -> float:
    if isinstance(value, dict):
        assert reading is not None, f"a reading must be named for {value}"
        return float(value[reading])
    return float(value)


def _benchmark_inputs() -> FirstOptionInputs:
    """The benchmark lot, as the emit transform passes it: recorded 10,075 and outline disagree, a
    corner lot, no corner-reach measurement needed (the footprint is withheld)."""
    return FirstOptionInputs(
        allowance_sqft=20150.0,
        recorded_lot_area_sqft=10075.0,
        min_base_ft=_MIN_BASE,
        max_base_ft=_MAX_BASE,
        floor_to_floor_ft=_F2F,
        lot_type="corner",
        areas_agree=False,
        corner_areas=None,
        outline_area_sqft=None,
        way_conditions=(_CONTRADICTED, _UNCHECKED),
    )


def _no_feasibility_language(blob: dict) -> None:
    # No text CALLS the result feasible, compliant, validated or legally correct. ("Confirmed" is
    # not banned: a condition may legitimately say "if the recorded lot area is confirmed".)
    text = json.dumps(blob).lower()
    for banned in ("feasible", "complies", "compliant", "validated", "legally correct"):
        assert banned not in text, banned


# --------------------------------------------------------------------------- S7
def test_s7_benchmark_coverage_withheld_missing_fact_law_by_portion() -> None:
    """S7: on the benchmark the footprint is WITHHELD because the two lot areas disagree; the kind
    is a missing fact; the reason gives the law by portion (corner 100 percent, interior 80 percent,
    within 100 feet) with no square-foot figure; the outline's area is not used in its place."""
    blocks = assemble_first_option(_benchmark_inputs())
    cov = blocks.coverage_by_portion
    assert cov["status"] == "withheld"
    assert cov["gap_kind"] == "missing_information"  # a missing fact about the property
    assert "100 percent" in cov["reason"] and "80 percent" in cov["reason"]
    assert "100 feet" in cov["reason"]
    assert "drawing measure" in cov["reason"]  # the outline's area is never used in its place
    assert "footprint_sqft" not in cov and "corner_portion_area_sqft" not in cov  # no number
    assert cov["zr_sections"] == ["ZR 23-362", "ZR 12-10"]
    _no_feasibility_language(cov)


# --------------------------------------------------------------------------- S9 / S10 / S11
def test_s9_benchmark_building_b_conditional() -> None:
    """S9: building_alternatives is building B alone, CONDITIONAL on the recorded area + the
    unchecked conditions; 3 storeys of 6,716.67 reaching 30 ft; the text says the plan fits even at
    the lowest ratio (0.80 x 10,075 = 8,060 >= the plan); nothing is called feasible."""
    alts = assemble_first_option(_benchmark_inputs()).building_alternatives
    assert alts is not None and len(alts) == 1
    b = alts[0]
    assert b["building"] == "B" and b["fill_rule"] == "to_min_base"
    block = _numbers_block("real-building-b")
    assert b["storey_count"] == int(block["storey_count"]) == 3
    assert math.isclose(b["height_ft"], _num(block["height_ft"]), abs_tol=_TOL)  # 30
    assert math.isclose(
        b["total_floor_area_sqft"], _num(block["total_floor_area_sqft"]), abs_tol=_TOL
    )
    assert math.isclose(b["footprint_area_sqft"], _num(block["footprint_area_sqft"]), abs_tol=_TOL)
    assert b["below_min_base"] is False
    for got, exp in zip(b["floor_schedule"], block["storeys"], strict=True):
        assert math.isclose(got["plan_area_sqft"], _num(exp["plan_area_sqft"]), abs_tol=_TOL)
        assert math.isclose(
            got["running_total_sqft"], _num(exp["running_total_sqft"]), abs_tol=_TOL
        )
    assert b["way"]["way"] == "conditional"
    kinds = {c["kind"] for c in b["way"]["conditions"]}
    assert kinds == {"contradicted_record", "unchecked_condition"}  # ruling W2 (R267)
    # W11 (c): the label is a short name; the lowest-ratio bound (8,060) appears ONLY in fit_note,
    # a text saying what it is, never as a footprint figure.
    assert b["label"] == "Building B: the fewest storeys reaching the minimum base height"
    assert "8,060 sq ft" in b["fit_note"]
    assert "8,060" not in b["label"]
    assert math.isclose(b["footprint_area_sqft"], 8060.0, abs_tol=0.5) is False
    assert b["not_checked"][0] == "The rear yard beyond the corner"
    _no_feasibility_language(b)


def test_s10_benchmark_building_a_is_absent() -> None:
    """S10: building A is NOT in the list on the benchmark - it needs the footprint figure, which is
    withheld (S7); no footprint is invented."""
    alts = assemble_first_option(_benchmark_inputs()).building_alternatives
    assert alts is not None
    assert all(entry["building"] != "A" for entry in alts)


def test_s11_benchmark_building_b_capacity_estimate() -> None:
    """S11: building B's capacity estimate is 17.27-21.59, labelled 'Preliminary capacity estimate',
    worked from its own floor area (20,150). Basis: step-p6-worked#real-estimate-b."""
    b = assemble_first_option(_benchmark_inputs()).building_alternatives[0]
    est = b["capacity_estimate"]
    exp = _numbers_block("real-estimate-b")
    assert est["label"] == "Preliminary capacity estimate"
    assert math.isclose(est["floor_area_sqft"], _num(exp["floor_area_sqft"]), abs_tol=_TOL)  # 20150
    assert math.isclose(est["quotient_low"], _num(exp["quotient_low"]), abs_tol=_TOL)  # 17.27
    assert math.isclose(est["quotient_high"], _num(exp["quotient_high"]), abs_tol=_TOL)  # 21.59
    assert est["whole_below_low"] == int(exp["whole_below_low"]) == 17
    assert est["whole_above_low"] == int(exp["whole_above_low"]) == 18
    assert est["whole_below_high"] == int(exp["whole_below_high"]) == 21
    assert est["whole_above_high"] == int(exp["whole_above_high"]) == 22
    assert math.isclose(est["share_low"], 0.60, abs_tol=_TOL)
    assert math.isclose(est["share_high"], 0.75, abs_tol=_TOL)


# ----------------------------------------------------------------- W11(a) value-state agreement
def test_w11a_max_lot_coverage_value_state_agrees_with_the_block() -> None:
    """W11 (a): the max_lot_coverage value state mirrors the WITHHELD block exactly (same reason,
    kind, resolver); for an AVAILABLE block it says coverage is given by portion with no single
    whole-lot figure (kind work_owed - claiming no missing property fact)."""
    withheld = assemble_first_option(_benchmark_inputs()).coverage_by_portion
    vs = max_lot_coverage_value_state(withheld)
    assert vs["way"] == "withheld"
    assert vs["reason"] == withheld["reason"]
    assert vs["gap_kind"] == withheld["gap_kind"] == "missing_information"
    assert vs["resolved_by"] == withheld["resolved_by"]
    one_street = CornerPortionAreas(
        unknown_value("sq ft", "one"), unknown_value("sq ft", "one"),
        STATE_ONE_CONFIRMED_STREET, (),
    )
    available = assemble_first_option(FirstOptionInputs(
        allowance_sqft=20000.0, recorded_lot_area_sqft=10000.0, min_base_ft=_MIN_BASE,
        max_base_ft=_MAX_BASE, floor_to_floor_ft=_F2F, lot_type="interior", areas_agree=True,
        corner_areas=one_street, outline_area_sqft=10000.0, way_conditions=(_UNCHECKED,),
    )).coverage_by_portion
    assert available["status"] == "available"
    vs2 = max_lot_coverage_value_state(available)
    assert vs2["way"] == "withheld" and "coverage_by_portion" in vs2["reason"]
    assert vs2["gap_kind"] == "work_owed"


# --------------------------------------------------------------------------- S13
def test_s13_interior_lot_areas_agree_shows_footprint_and_building_a() -> None:
    """S13: on an interior lot whose areas agree (a made-up 10,000 sq ft lot) the footprint shows -
    the interior ratio on the whole lot = 8,000 (DB-212 b) - and building A is in the list. Basis:
    step-p6-worked#made-up-building-a."""
    one_street = CornerPortionAreas(
        unknown_value("sq ft", "one street"), unknown_value("sq ft", "one street"),
        STATE_ONE_CONFIRMED_STREET, (),
    )
    blocks = assemble_first_option(FirstOptionInputs(
        allowance_sqft=20000.0, recorded_lot_area_sqft=10000.0,
        min_base_ft=_MIN_BASE, max_base_ft=_MAX_BASE, floor_to_floor_ft=_F2F,
        lot_type="interior", areas_agree=True, corner_areas=one_street,
        outline_area_sqft=10000.0, way_conditions=(_UNCHECKED,),
    ))
    cov = blocks.coverage_by_portion
    block_a = _numbers_block("made-up-building-a")
    assert cov["status"] == "available"
    assert math.isclose(cov["interior_portion_area_sqft"], 10000.0, abs_tol=_TOL)
    assert math.isclose(cov["corner_portion_area_sqft"], 0.0, abs_tol=_TOL)
    assert math.isclose(
        cov["footprint_sqft"], _num(block_a["footprint_area_sqft"]), abs_tol=_TOL
    )  # 8000
    assert math.isclose(cov["interior_ratio"], 0.80, abs_tol=_TOL)
    assert math.isclose(cov["corner_ratio"], 1.0, abs_tol=_TOL)
    buildings = {entry["building"] for entry in blocks.building_alternatives}
    assert "A" in buildings  # S13: building A is in the list
    a = next(e for e in blocks.building_alternatives if e["building"] == "A")
    assert a["storey_count"] == int(block_a["storey_count"]) == 2
    assert math.isclose(
        a["total_floor_area_sqft"], _num(block_a["total_floor_area_sqft"]), abs_tol=_TOL
    )
    assert math.isclose(
        a["unused_floor_area_sqft"], _num(block_a["unused_floor_area_sqft"]), abs_tol=_TOL
    )
    assert a["below_min_base"] is True  # 20 ft < 30 ft
    assert "The rear yard beyond the corner" not in a["not_checked"]  # not a corner lot
    assert "fit_note" not in a  # building A's footprint is the coverage footprint; no bound
    assert a["label"] == "Building A: the widest footprint"
    _no_feasibility_language(blocks.building_alternatives[0])


# --------------------------------------------------------------------------- S14
def test_s14_no_outline_withholds_missing_fact_and_lists_nothing() -> None:
    """S14: a lot whose outline was refused withholds coverage, kind a missing fact, and lists no
    building (its geometry is not understood); nothing is called feasible."""
    refused = CornerPortionAreas(
        unknown_value("sq ft", "no outline"), unknown_value("sq ft", "no outline"),
        STATE_OUTLINE_REFUSED, (),
    )
    blocks = assemble_first_option(FirstOptionInputs(
        allowance_sqft=20000.0, recorded_lot_area_sqft=10000.0,
        min_base_ft=_MIN_BASE, max_base_ft=_MAX_BASE, floor_to_floor_ft=_F2F,
        lot_type="corner", areas_agree=None, corner_areas=refused,
        outline_area_sqft=None, way_conditions=(_UNCHECKED,),
    ))
    assert blocks.coverage_by_portion["status"] == "withheld"
    assert blocks.coverage_by_portion["gap_kind"] == "missing_information"  # a missing fact
    assert blocks.building_alternatives is None
    _no_feasibility_language(blocks.coverage_by_portion)


def test_s14_bent_frontage_withholds_method_limit_and_lists_nothing() -> None:
    """S14: a bent frontage (the outline is drawn but no two straight street lines) withholds
    coverage as a LIMIT OF THE METHOD and lists no building."""
    bent = CornerPortionAreas(
        unknown_value("sq ft", "bent"), unknown_value("sq ft", "bent"),
        STATE_NO_CONFIRMED_STREET, (("Main Street", "frontage_not_straight"),),
    )
    blocks = assemble_first_option(FirstOptionInputs(
        allowance_sqft=20000.0, recorded_lot_area_sqft=10000.0,
        min_base_ft=_MIN_BASE, max_base_ft=_MAX_BASE, floor_to_floor_ft=_F2F,
        lot_type="corner", areas_agree=True, corner_areas=bent,
        outline_area_sqft=10000.0, way_conditions=(_UNCHECKED,),
    ))
    assert blocks.coverage_by_portion["status"] == "withheld"
    assert blocks.coverage_by_portion["gap_kind"] == "work_owed"  # a limit of the method
    assert blocks.building_alternatives is None
