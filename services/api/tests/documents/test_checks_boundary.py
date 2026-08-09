"""Tests for the SB-S3 boundary deterministic checks (M2-T015 unit 3g-1).

For each check: a passing case, a failing case pinning the exact computed
misclosure/difference, and every typed UNEVALUABLE refusal condition. Expected closure
numbers are recomputed from the packet's stated formula (dx = d * sin(bearing_rad),
dy = d * cos(bearing_rad), bearing measured clockwise from north, magnitude =
hypot(dx, dy), sums via math.fsum) so the checks' arithmetic is pinned bit-for-bit.
"""

from __future__ import annotations

import enum
import json
import math

import pytest

from app.documents.checks import CheckFailed, CheckPassed, CheckUnevaluable
from app.documents.checks.boundary import boundary_closure, segment_sum_consistency
from app.documents.taxonomy import SurveyFactType
from app.documents.units import (
    AngleUnit,
    DistanceUnit,
    UnresolvedNormalizedValue,
    ValidatedBearing,
    ValidatedDistance,
)

# ------------------------------------------------------------------- fixtures


def _feet(value):
    return ValidatedDistance(
        fact_type=SurveyFactType.BOUNDARY_SEGMENT_DISTANCE,
        value=value,
        unit=DistanceUnit.FEET,
    )


def _degrees(value):
    return ValidatedBearing(
        fact_type=SurveyFactType.BOUNDARY_BEARING,
        value=value,
        unit=AngleUnit.DEGREES,
    )


class _SimulatedFutureDistanceUnit(enum.Enum):
    # Stand-in for a future additively-extended distance unit: DistanceUnit currently
    # has a single member, so a genuinely mixed pair cannot be built from it alone.
    METERS = "meters"


class _SimulatedFutureAngleUnit(enum.Enum):
    # Stand-in for a future additively-extended angle unit the closure math is not
    # grounded for.
    GONS = "gons"


def _meters(value):
    return ValidatedDistance(
        fact_type=SurveyFactType.BOUNDARY_SEGMENT_DISTANCE,
        value=value,
        unit=_SimulatedFutureDistanceUnit.METERS,
    )


_UNRESOLVED = UnresolvedNormalizedValue(
    submitted_fact_type="boundary_segment_distance",
    submitted_value="'about 100 feet'",
    submitted_unit=None,
    reason="test fixture: an unresolved result must never be consumed by a check",
)

_BAD_TOLERANCES = pytest.mark.parametrize(
    "bad_tolerance",
    [None, True, "0.01", float("nan"), float("inf"), -0.01],
    ids=["none", "bool", "string", "nan", "inf", "negative"],
)

RECTANGLE_LENGTHS = [100.0, 50.0, 100.0, 50.0]
RECTANGLE_BEARINGS = [0.0, 90.0, 180.0, 270.0]

OPEN_LENGTHS = [30.0, 40.0, 30.0]
OPEN_BEARINGS = [0.0, 90.0, 180.0]


def _rectangle_inputs():
    return (
        [_feet(value) for value in RECTANGLE_LENGTHS],
        [_degrees(value) for value in RECTANGLE_BEARINGS],
    )


def _expected_closure(lengths, bearings_degrees):
    dx = math.fsum(
        length * math.sin(math.radians(bearing))
        for length, bearing in zip(lengths, bearings_degrees, strict=True)
    )
    dy = math.fsum(
        length * math.cos(math.radians(bearing))
        for length, bearing in zip(lengths, bearings_degrees, strict=True)
    )
    return dx, dy, math.hypot(dx, dy)


# ------------------------------------------------------------- boundary_closure


def test_boundary_closure_passes_closed_rectangle_traverse():
    distances, bearings = _rectangle_inputs()
    result = boundary_closure(distances, bearings, tolerance=0.01)
    assert isinstance(result, CheckPassed)
    assert result.check_name == "boundary_closure"
    assert result.unit == "feet"
    assert result.tolerance == 0.01
    assert result.evaluated is True
    assert result.passed is True
    assert result.promotable is False
    dx, dy, magnitude = _expected_closure(RECTANGLE_LENGTHS, RECTANGLE_BEARINGS)
    assert result.computed == {
        "segment_count": 4,
        "closure_dx": dx,
        "closure_dy": dy,
        "closure_magnitude": magnitude,
    }
    assert result.computed["closure_magnitude"] <= 0.01


def test_boundary_closure_fails_open_traverse_with_exact_computed_misclosure():
    result = boundary_closure(
        [_feet(value) for value in OPEN_LENGTHS],
        [_degrees(value) for value in OPEN_BEARINGS],
        tolerance=0.05,
    )
    assert isinstance(result, CheckFailed)
    assert result.check_name == "boundary_closure"
    assert result.unit == "feet"
    assert result.tolerance == 0.05
    assert result.evaluated is True
    assert result.passed is False
    assert result.promotable is False
    dx, dy, magnitude = _expected_closure(OPEN_LENGTHS, OPEN_BEARINGS)
    assert result.computed == {
        "segment_count": 3,
        "closure_dx": dx,
        "closure_dy": dy,
        "closure_magnitude": magnitude,
    }
    # The 40 ft east leg never returns: the misclosure is that full leg
    # (up to float rounding of the trig terms), far outside the 0.05 ft tolerance.
    assert result.computed["closure_magnitude"] == pytest.approx(40.0)
    assert result.computed["closure_magnitude"] > 0.05


def test_boundary_closure_unevaluable_on_count_mismatch():
    distances, bearings = _rectangle_inputs()
    result = boundary_closure(distances, bearings[:-1], tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "boundary_closure"
    assert result.evaluated is False
    assert result.passed is False
    assert result.promotable is False
    assert "4 distances and 3 bearings" in result.reason
    assert "never truncated or padded" in result.reason


def test_boundary_closure_unevaluable_on_fewer_than_three_segments():
    result = boundary_closure(
        [_feet(100.0), _feet(50.0)], [_degrees(0.0), _degrees(90.0)], tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "at least 3 segments, got 2" in result.reason


@pytest.mark.parametrize(
    "bad_distance", [100.0, _UNRESOLVED], ids=["raw_number", "unresolved_result"]
)
def test_boundary_closure_unevaluable_on_non_resolved_distance(bad_distance):
    distances, bearings = _rectangle_inputs()
    distances[2] = bad_distance
    result = boundary_closure(distances, bearings, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert "distances[2] must be a resolved ValidatedDistance" in result.reason


def test_boundary_closure_unevaluable_on_non_resolved_bearing():
    distances, bearings = _rectangle_inputs()
    bearings[1] = 90.0
    result = boundary_closure(distances, bearings, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert "bearings[1] must be a resolved ValidatedBearing" in result.reason


def test_boundary_closure_unevaluable_on_mixed_distance_units():
    distances, bearings = _rectangle_inputs()
    distances[3] = _meters(50.0)
    result = boundary_closure(distances, bearings, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert "state mixed units" in result.reason


def test_boundary_closure_unevaluable_on_non_degree_bearing():
    distances, bearings = _rectangle_inputs()
    bearings[0] = ValidatedBearing(
        fact_type=SurveyFactType.BOUNDARY_BEARING,
        value=0.0,
        unit=_SimulatedFutureAngleUnit.GONS,
    )
    result = boundary_closure(distances, bearings, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert "grounded only for bearings stated in 'degrees'" in result.reason


@_BAD_TOLERANCES
def test_boundary_closure_unevaluable_on_unusable_tolerance(bad_tolerance):
    distances, bearings = _rectangle_inputs()
    result = boundary_closure(distances, bearings, tolerance=bad_tolerance)
    assert isinstance(result, CheckUnevaluable)
    assert "tolerance must be" in result.reason


# ------------------------------------------------------- segment_sum_consistency


def test_segment_sum_consistency_passes_when_parts_match_whole():
    result = segment_sum_consistency(
        [_feet(25.5), _feet(30.25), _feet(44.25)], _feet(100.0), tolerance=0.01
    )
    assert isinstance(result, CheckPassed)
    assert result.check_name == "segment_sum_consistency"
    assert result.unit == "feet"
    assert result.tolerance == 0.01
    assert result.evaluated is True
    assert result.passed is True
    assert result.promotable is False
    assert result.computed == {
        "part_count": 3,
        "parts_sum": 100.0,
        "stated_whole": 100.0,
        "difference": 0.0,
    }


def test_segment_sum_consistency_fails_with_exact_computed_difference():
    result = segment_sum_consistency(
        [_feet(25.0), _feet(30.0)], _feet(60.0), tolerance=0.5
    )
    assert isinstance(result, CheckFailed)
    assert result.check_name == "segment_sum_consistency"
    assert result.unit == "feet"
    assert result.tolerance == 0.5
    assert result.evaluated is True
    assert result.passed is False
    assert result.promotable is False
    assert result.computed == {
        "part_count": 2,
        "parts_sum": 55.0,
        "stated_whole": 60.0,
        "difference": -5.0,
    }


def test_segment_sum_unevaluable_on_empty_parts():
    result = segment_sum_consistency([], _feet(100.0), tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "segment_sum_consistency"
    assert result.evaluated is False
    assert result.passed is False
    assert result.promotable is False
    assert "at least one part distance" in result.reason


@pytest.mark.parametrize(
    "bad_part", [25.0, _UNRESOLVED], ids=["raw_number", "unresolved_result"]
)
def test_segment_sum_unevaluable_on_non_resolved_part(bad_part):
    result = segment_sum_consistency(
        [_feet(25.0), bad_part], _feet(55.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "parts[1] must be a resolved ValidatedDistance" in result.reason


def test_segment_sum_unevaluable_on_non_resolved_whole():
    result = segment_sum_consistency(
        [_feet(25.0), _feet(30.0)], 55.0, tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "stated whole must be a resolved ValidatedDistance" in result.reason


def test_segment_sum_unevaluable_on_mixed_part_units():
    result = segment_sum_consistency(
        [_feet(25.0), _meters(30.0)], _feet(55.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "state mixed units" in result.reason


def test_segment_sum_unevaluable_on_whole_unit_differing_from_parts():
    result = segment_sum_consistency(
        [_feet(25.0), _feet(30.0)], _meters(55.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "but the whole is stated in" in result.reason


@_BAD_TOLERANCES
def test_segment_sum_unevaluable_on_unusable_tolerance(bad_tolerance):
    result = segment_sum_consistency(
        [_feet(25.0), _feet(30.0)], _feet(55.0), tolerance=bad_tolerance
    )
    assert isinstance(result, CheckUnevaluable)
    assert "tolerance must be" in result.reason


# ----------------------------------------------------------------- provenance


def test_check_results_serialize_to_json_payloads():
    passed = segment_sum_consistency(
        [_feet(50.0), _feet(50.0)], _feet(100.0), tolerance=0.01
    )
    failed = segment_sum_consistency([_feet(50.0)], _feet(100.0), tolerance=0.01)
    unevaluable = segment_sum_consistency([], _feet(100.0), tolerance=0.01)
    assert isinstance(passed, CheckPassed)
    assert isinstance(failed, CheckFailed)
    assert isinstance(unevaluable, CheckUnevaluable)
    for result, outcome in (
        (passed, "passed"),
        (failed, "failed"),
        (unevaluable, "unevaluable"),
    ):
        payload = result.to_payload()
        assert payload["check_name"] == "segment_sum_consistency"
        assert payload["outcome"] == outcome
        assert json.loads(json.dumps(payload)) == payload
    assert unevaluable.to_payload()["reject_code"] == "check_unevaluable"
