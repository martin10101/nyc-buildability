"""PART C of task M5-T145: the two step-P6 buildings as pure functions (one test per
scenario, S15-S21 and S29-S30, plus the C12 both-missing-input test).

Every EXPECTED value is parsed from the independent hand-worked example
``docs/reference-cases/R6B/cases/step-p6-worked.json`` (rows made-up-building-a /-b and
real-building-a /-b), never retyped and never taken from a run of the module under test. The
settled R6B envelope the scenarios pass as INPUTS (floor-to-floor 10 ft, min base 30 ft, max
base 45 ft) is read from the numbers_block where the block carries it and otherwise named here
as the scenario's stated input. The maximum building height is NOT an input (ruling C13).

The module keeps its figures unrounded; the reference records them to two decimals, so a
figure is compared within ``_TOL`` = 0.01 sq ft (the reference's own precision). Integer and
two-decimal figures (building A, the real lot) match exactly within that tolerance.
"""

from __future__ import annotations

import json
import math
import pathlib

from app.scenario.three_answers.first_building_options import (
    GAP_CODE_NOT_BUILT,
    STATUS_AVAILABLE,
    STATUS_NOT_KNOWN,
    FloorSchedule,
    building_a,
    building_b,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]
_CASE = _REPO_ROOT / "docs" / "reference-cases" / "R6B" / "cases" / "step-p6-worked.json"
_TOL = 0.01  # the reference records figures to two decimals; the module keeps them unrounded

# Scenario input that is NOT in a numbers_block and NOT an expected value (the settled R6B
# maximum base height the scenarios S15-S30 state as an input).
_MAX_BASE = 45.0


def _case() -> dict:
    return json.loads(_CASE.read_text(encoding="utf-8"))


def _numbers_block(row_id: str) -> dict:
    for row in _case()["rows"]:
        if row["row_id"] == row_id:
            return row["numbers_block"]
    raise AssertionError(f"row {row_id} not found in {_CASE}")


def _num(value, reading: str | None = None) -> float:
    """Parse a numbers_block figure, which is either a string or a {reading1, reading2} dict."""
    if isinstance(value, dict):
        assert reading is not None, f"a reading must be named for {value}"
        return float(value[reading])
    return float(value)


def _assert_matches_block(
    schedule: FloorSchedule, block: dict, reading: str | None = None
) -> None:
    """Assert an available floor schedule equals the parsed numbers_block (per reading)."""
    assert schedule.status == STATUS_AVAILABLE, schedule.reason
    assert schedule.storey_count == int(block["storey_count"])
    assert math.isclose(schedule.height_ft, _num(block["height_ft"]), abs_tol=_TOL)
    assert math.isclose(
        schedule.total_floor_area_sqft,
        _num(block["total_floor_area_sqft"], reading),
        abs_tol=_TOL,
    )
    assert math.isclose(
        schedule.unused_floor_area_sqft,
        _num(block["unused_floor_area_sqft"], reading),
        abs_tol=_TOL,
    )
    assert len(schedule.storeys) == len(block["storeys"])
    for got, exp in zip(schedule.storeys, block["storeys"], strict=True):
        assert got.storey == int(exp["storey"])
        assert math.isclose(got.top_ft, _num(exp["top_ft"]), abs_tol=_TOL)
        assert math.isclose(got.plan_area_sqft, _num(exp["plan_area_sqft"], reading), abs_tol=_TOL)
        assert math.isclose(
            got.floor_area_sqft, _num(exp["floor_area_sqft"], reading), abs_tol=_TOL
        )
        assert math.isclose(
            got.running_total_sqft, _num(exp["running_total_sqft"], reading), abs_tol=_TOL
        )
    # below_min_base is a plain fact derived from the parsed height and minimum base height.
    expected_below = _num(block["height_ft"]) < _num(block["min_base_height_ft"])
    assert schedule.below_min_base is expected_below


def test_s15_made_up_building_a() -> None:
    """Building A, made-up lot: the widest footprint (8,000) stacked to the 20,000 maximum."""
    block = _numbers_block("made-up-building-a")
    footprint = _num(block["footprint_area_sqft"])
    allowance = _num(block["maximum_floor_area_sqft"])
    f2f = _num(block["floor_to_floor_ft"])
    min_base = _num(block["min_base_height_ft"])
    result = building_a(footprint, allowance, f2f, min_base, _MAX_BASE)
    _assert_matches_block(result, block)
    assert result.below_min_base is True


def test_s16_made_up_building_b() -> None:
    """Building B, made-up lot: 3 storeys of 20,000/3 that reach the 30 ft minimum base."""
    footprint = _num(_numbers_block("made-up-building-a")["footprint_area_sqft"])  # 8,000
    block = _numbers_block("made-up-building-b")
    allowance = _num(block["maximum_floor_area_sqft"])
    f2f = _num(block["floor_to_floor_ft"])
    min_base = _num(block["min_base_height_ft"])
    result = building_b(footprint, allowance, f2f, min_base, _MAX_BASE)
    _assert_matches_block(result, block)
    assert result.below_min_base is False


def test_s17_real_building_a_reading13() -> None:
    """Building A, real lot, reading 13: one storey of 10,309.91."""
    block = _numbers_block("real-building-a")
    footprint = _num(block["footprint_area_sqft"], "reading1")
    allowance = _num(block["maximum_floor_area_sqft"])
    f2f = _num(block["floor_to_floor_ft"])
    min_base = _num(block["min_base_height_ft"])
    result = building_a(footprint, allowance, f2f, min_base, _MAX_BASE)
    _assert_matches_block(result, block, reading="reading1")
    assert result.below_min_base is True


def test_s18_real_building_a_reading14() -> None:
    """Building A, real lot, reading 14: one storey of 10,309.88 (the readings differ)."""
    block = _numbers_block("real-building-a")
    footprint = _num(block["footprint_area_sqft"], "reading2")
    allowance = _num(block["maximum_floor_area_sqft"])
    f2f = _num(block["floor_to_floor_ft"])
    min_base = _num(block["min_base_height_ft"])
    result = building_a(footprint, allowance, f2f, min_base, _MAX_BASE)
    _assert_matches_block(result, block, reading="reading2")
    assert result.below_min_base is True


def test_s19_real_building_b_both_readings() -> None:
    """Building B, real lot: 3 storeys of 20,150/3; the same under both readings' footprints."""
    a_block = _numbers_block("real-building-a")
    footprint_r1 = _num(a_block["footprint_area_sqft"], "reading1")  # 10,309.91
    footprint_r2 = _num(a_block["footprint_area_sqft"], "reading2")  # 10,309.88
    block = _numbers_block("real-building-b")
    allowance = _num(block["maximum_floor_area_sqft"])
    f2f = _num(block["floor_to_floor_ft"])
    min_base = _num(block["min_base_height_ft"])
    r1 = building_b(footprint_r1, allowance, f2f, min_base, _MAX_BASE)
    r2 = building_b(footprint_r2, allowance, f2f, min_base, _MAX_BASE)
    _assert_matches_block(r1, block)
    _assert_matches_block(r2, block)
    assert r1.storeys == r2.storeys  # the plan (6,716.67) fits both footprints
    assert r1.below_min_base is False


def test_s20_missing_footprint_both_not_known() -> None:
    """A missing footprint: BOTH buildings not known, naming the missing input, no kind of
    gap (ruling C12), no zero, no default."""
    a = building_a(None, 20150.0, 10.0, 30.0, _MAX_BASE)
    b = building_b(None, 20150.0, 10.0, 30.0, _MAX_BASE)
    for result in (a, b):
        assert result.status == STATUS_NOT_KNOWN
        assert result.gap_kind is None
        assert result.missing_inputs == ("footprint_area",)
        assert result.storeys == ()
        assert result.storey_count is None
        assert result.height_ft is None
        assert result.total_floor_area_sqft is None
        assert "footprint" in result.reason.lower()
    joined = (a.reason + b.reason).lower()
    assert "complies" not in joined
    assert "feasible" not in joined


def test_s21_missing_floor_area_allowance_both_not_known() -> None:
    """A missing floor-area allowance: BOTH buildings not known, naming the missing input, no
    kind of gap (ruling C12), no default. The text asserts no cause."""
    a = building_a(8000.0, None, 10.0, 30.0, _MAX_BASE)
    b = building_b(8000.0, None, 10.0, 30.0, _MAX_BASE)
    for result in (a, b):
        assert result.status == STATUS_NOT_KNOWN
        assert result.gap_kind is None
        assert result.missing_inputs == ("floor_area_allowance",)
        assert result.storeys == ()
        assert result.total_floor_area_sqft is None
        assert "allowance" in result.reason.lower()
        assert "not available for this lot" not in result.reason


def test_c12_missing_footprint_and_allowance_lists_both() -> None:
    """When more than one input is missing, ALL missing names are listed (ruling C12)."""
    a = building_a(None, None, 10.0, 30.0, _MAX_BASE)
    b = building_b(None, None, 10.0, 30.0, _MAX_BASE)
    for result in (a, b):
        assert result.status == STATUS_NOT_KNOWN
        assert result.gap_kind is None
        assert result.missing_inputs == ("footprint_area", "floor_area_allowance")
        assert "footprint" in result.reason.lower()
        assert "allowance" in result.reason.lower()


def test_s29_building_b_plan_would_not_fit_footprint() -> None:
    """Building B not known when its plan would not fit the footprint (code not built);
    building A is still worked from its own inputs."""
    footprint = 5000.0
    allowance = 20000.0
    f2f = 10.0
    min_base = 30.0
    b = building_b(footprint, allowance, f2f, min_base, _MAX_BASE)
    assert b.status == STATUS_NOT_KNOWN
    assert b.gap_kind == GAP_CODE_NOT_BUILT
    assert b.missing_inputs == ()
    assert b.storeys == ()
    plan = allowance / math.ceil(min_base / f2f)  # 20,000 / 3 = 6,666.67, more than 5,000
    assert plan > footprint
    assert f"{plan:,.2f}" in b.reason
    assert f"{footprint:,.2f}" in b.reason
    a = building_a(footprint, allowance, f2f, min_base, _MAX_BASE)
    assert a.status == STATUS_AVAILABLE


def test_s30_building_a_stack_passes_max_base_height() -> None:
    """Building A not known when its stack would pass the maximum base height (code not
    built); no storey above the base is returned."""
    footprint = 2000.0
    allowance = 20000.0
    f2f = 10.0
    a = building_a(footprint, allowance, f2f, 30.0, _MAX_BASE)
    assert a.status == STATUS_NOT_KNOWN
    assert a.gap_kind == GAP_CODE_NOT_BUILT
    assert a.missing_inputs == ()
    assert a.storeys == ()
    assert a.height_ft is None
    assert "maximum base height" in a.reason
    assert "10 storeys" in a.reason  # 20,000 / 2,000 = 10 storeys, 100 ft high
    assert f"{_MAX_BASE:g}" in a.reason
