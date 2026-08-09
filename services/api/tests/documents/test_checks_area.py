"""Tests for the SB-S3 area/dimension deterministic checks (M2-T015 unit 3g-2).

For each check: a passing case, a failing case pinning the exact computed numbers, and
every typed UNEVALUABLE refusal condition — including the distance→area unit-pairing
rule (feet → square_feet is the only grounded pairing; anything else refuses, never
converts). Expected areas are recomputed from the packet's stated construction
(vertices accumulated from d * sin/cos(radians(bearing)), bearings measured clockwise
from north; shoelace cross-term sum via math.fsum; absolute value halved) so the
check's arithmetic is pinned bit-for-bit.
"""

from __future__ import annotations

import enum
import json
import math

import pytest

from app.documents import checks as checks_package
from app.documents.checks import CheckFailed, CheckPassed, CheckUnevaluable
from app.documents.checks.area import (
    calculated_vs_stated_area,
    contradictory_dimensions,
)
from app.documents.taxonomy import SurveyFactType
from app.documents.units import (
    AngleUnit,
    AreaUnit,
    DistanceUnit,
    UnresolvedNormalizedValue,
    ValidatedArea,
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


def _square_feet(value):
    return ValidatedArea(
        fact_type=SurveyFactType.STATED_LOT_AREA,
        value=value,
        unit=AreaUnit.SQUARE_FEET,
    )


def _acres(value):
    return ValidatedArea(
        fact_type=SurveyFactType.STATED_LOT_AREA,
        value=value,
        unit=AreaUnit.ACRES,
    )


class _SimulatedFutureDistanceUnit(enum.Enum):
    # Stand-in for a future additively-extended distance unit: DistanceUnit currently
    # has a single member, so a genuinely mixed pair (and an ungrounded distance→area
    # pairing) cannot be built from it alone.
    METERS = "meters"


class _SimulatedFutureAngleUnit(enum.Enum):
    # Stand-in for a future additively-extended angle unit the polygon-area math is
    # not grounded for.
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

# A 100 ft (north-south) by 50 ft (east-west) rectangle: enclosed area 5000 sq ft.
RECTANGLE_LENGTHS = [100.0, 50.0, 100.0, 50.0]
RECTANGLE_BEARINGS = [0.0, 90.0, 180.0, 270.0]


def _rectangle_inputs():
    return (
        [_feet(value) for value in RECTANGLE_LENGTHS],
        [_degrees(value) for value in RECTANGLE_BEARINGS],
    )


def _expected_area(lengths, bearings_degrees):
    vertices = [(0.0, 0.0)]
    x = y = 0.0
    for length, bearing in zip(lengths, bearings_degrees, strict=True):
        x += length * math.sin(math.radians(bearing))
        y += length * math.cos(math.radians(bearing))
        vertices.append((x, y))
    cross_sum = math.fsum(
        vertices[index][0] * vertices[(index + 1) % len(vertices)][1]
        - vertices[(index + 1) % len(vertices)][0] * vertices[index][1]
        for index in range(len(vertices))
    )
    return abs(cross_sum) / 2.0


# ------------------------------------------------------ calculated_vs_stated_area


def test_calculated_vs_stated_area_passes_5000_sq_ft_rectangle():
    distances, bearings = _rectangle_inputs()
    result = calculated_vs_stated_area(
        distances, bearings, _square_feet(5000.0), tolerance=0.01
    )
    assert isinstance(result, CheckPassed)
    assert result.check_name == "calculated_vs_stated_area"
    assert result.unit == "square_feet"
    assert result.tolerance == 0.01
    assert result.evaluated is True
    assert result.passed is True
    assert result.promotable is False
    expected = _expected_area(RECTANGLE_LENGTHS, RECTANGLE_BEARINGS)
    assert result.computed == {
        "segment_count": 4,
        "computed_area": expected,
        "stated_area": 5000.0,
        "difference": expected - 5000.0,
    }
    # The shoelace area of the 100x50 rectangle is 5000 sq ft (exactly, up to float
    # rounding of the axis-aligned trig terms).
    assert result.computed["computed_area"] == pytest.approx(5000.0)
    assert abs(result.computed["difference"]) <= 0.01


def test_calculated_vs_stated_area_fails_with_exact_computed_numbers():
    distances, bearings = _rectangle_inputs()
    result = calculated_vs_stated_area(
        distances, bearings, _square_feet(5200.0), tolerance=1.0
    )
    assert isinstance(result, CheckFailed)
    assert result.check_name == "calculated_vs_stated_area"
    assert result.unit == "square_feet"
    assert result.tolerance == 1.0
    assert result.evaluated is True
    assert result.passed is False
    assert result.promotable is False
    expected = _expected_area(RECTANGLE_LENGTHS, RECTANGLE_BEARINGS)
    assert result.computed == {
        "segment_count": 4,
        "computed_area": expected,
        "stated_area": 5200.0,
        "difference": expected - 5200.0,
    }
    # Computed ~5000 sq ft against a stated 5200 sq ft: the discrepancy is the full
    # 200 sq ft (up to float rounding), far outside the 1 sq ft tolerance.
    assert result.computed["difference"] == pytest.approx(-200.0)
    assert abs(result.computed["difference"]) > 1.0


@pytest.mark.parametrize(
    "bad_stated", [5000.0, _UNRESOLVED], ids=["raw_number", "unresolved_result"]
)
def test_calculated_area_unevaluable_on_non_resolved_stated_area(bad_stated):
    distances, bearings = _rectangle_inputs()
    result = calculated_vs_stated_area(distances, bearings, bad_stated, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "calculated_vs_stated_area"
    assert result.evaluated is False
    assert result.passed is False
    assert result.promotable is False
    assert "stated area must be a resolved ValidatedArea" in result.reason


def test_calculated_area_unevaluable_on_count_mismatch():
    distances, bearings = _rectangle_inputs()
    result = calculated_vs_stated_area(
        distances, bearings[:-1], _square_feet(5000.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "4 distances and 3 bearings" in result.reason
    assert "never truncated or padded" in result.reason


def test_calculated_area_unevaluable_on_fewer_than_three_segments():
    result = calculated_vs_stated_area(
        [_feet(100.0), _feet(50.0)],
        [_degrees(0.0), _degrees(90.0)],
        _square_feet(5000.0),
        tolerance=0.01,
    )
    assert isinstance(result, CheckUnevaluable)
    assert "at least 3 segments, got 2" in result.reason


@pytest.mark.parametrize(
    "bad_distance", [100.0, _UNRESOLVED], ids=["raw_number", "unresolved_result"]
)
def test_calculated_area_unevaluable_on_non_resolved_distance(bad_distance):
    distances, bearings = _rectangle_inputs()
    distances[2] = bad_distance
    result = calculated_vs_stated_area(
        distances, bearings, _square_feet(5000.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "distances[2] must be a resolved ValidatedDistance" in result.reason


def test_calculated_area_unevaluable_on_non_resolved_bearing():
    distances, bearings = _rectangle_inputs()
    bearings[1] = 90.0
    result = calculated_vs_stated_area(
        distances, bearings, _square_feet(5000.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "bearings[1] must be a resolved ValidatedBearing" in result.reason


def test_calculated_area_unevaluable_on_mixed_distance_units():
    distances, bearings = _rectangle_inputs()
    distances[3] = _meters(50.0)
    result = calculated_vs_stated_area(
        distances, bearings, _square_feet(5000.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "state mixed units" in result.reason


def test_calculated_area_unevaluable_on_non_degree_bearing():
    distances, bearings = _rectangle_inputs()
    bearings[0] = ValidatedBearing(
        fact_type=SurveyFactType.BOUNDARY_BEARING,
        value=0.0,
        unit=_SimulatedFutureAngleUnit.GONS,
    )
    result = calculated_vs_stated_area(
        distances, bearings, _square_feet(5000.0), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "grounded only for bearings stated in 'degrees'" in result.reason


def test_calculated_area_unevaluable_on_non_square_stated_unit():
    # feet distances pair ONLY with a square_feet stated area; acres is never
    # converted even though the conversion is well known.
    distances, bearings = _rectangle_inputs()
    result = calculated_vs_stated_area(
        distances, bearings, _acres(0.1148), tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "the stated area is in" in result.reason
    assert "never converted between units" in result.reason


def test_calculated_area_unevaluable_on_ungrounded_distance_unit_pairing():
    # A uniform future distance unit passes the mixed-units gate but has no grounded
    # square-area pairing registered, so the check refuses rather than assuming one.
    result = calculated_vs_stated_area(
        [_meters(value) for value in RECTANGLE_LENGTHS],
        [_degrees(value) for value in RECTANGLE_BEARINGS],
        _square_feet(5000.0),
        tolerance=0.01,
    )
    assert isinstance(result, CheckUnevaluable)
    assert "no grounded square-area unit pairing" in result.reason


@_BAD_TOLERANCES
def test_calculated_area_unevaluable_on_unusable_tolerance(bad_tolerance):
    distances, bearings = _rectangle_inputs()
    result = calculated_vs_stated_area(
        distances, bearings, _square_feet(5000.0), tolerance=bad_tolerance
    )
    assert isinstance(result, CheckUnevaluable)
    assert "tolerance must be" in result.reason


# ------------------------------------------------------- contradictory_dimensions


def test_contradictory_dimensions_passes_consistent_restatements():
    result = contradictory_dimensions(
        {
            "north_boundary": [_feet(100.0), _feet(100.0), _feet(100.005)],
            "east_boundary": [_feet(50.0)],
        },
        tolerance=0.01,
    )
    assert isinstance(result, CheckPassed)
    assert result.check_name == "contradictory_dimensions"
    assert result.unit == "feet"
    assert result.tolerance == 0.01
    assert result.evaluated is True
    assert result.passed is True
    assert result.promotable is False
    assert result.computed == {
        "label_count": 2,
        "statement_count": 4,
        "contradicting_label_count": 0,
    }


def test_contradictory_dimensions_fails_naming_each_contradicting_label():
    result = contradictory_dimensions(
        {
            "north_boundary": [_feet(100.0), _feet(100.0), _feet(103.25)],
            "east_boundary": [_feet(50.0), _feet(49.995)],
        },
        tolerance=0.01,
    )
    assert isinstance(result, CheckFailed)
    assert result.check_name == "contradictory_dimensions"
    assert result.unit == "feet"
    assert result.tolerance == 0.01
    assert result.evaluated is True
    assert result.passed is False
    assert result.promotable is False
    # north_boundary's third statement contradicts its first by 3.25 ft; east_boundary
    # restates within tolerance and is NOT named. Conflicting values verbatim.
    assert result.computed == {
        "label_count": 2,
        "statement_count": 5,
        "contradicting_label_count": 1,
        "north_boundary.stated_first": 100.0,
        "north_boundary.restatement[2]": 103.25,
    }


def test_contradictory_dimensions_unevaluable_on_empty_mapping():
    result = contradictory_dimensions({}, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "contradictory_dimensions"
    assert result.evaluated is False
    assert result.passed is False
    assert result.promotable is False
    assert "empty mapping" in result.reason


def test_contradictory_dimensions_unevaluable_on_empty_label_sequence():
    result = contradictory_dimensions({"north_boundary": []}, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert "statements['north_boundary'] is empty" in result.reason


def test_contradictory_dimensions_unevaluable_on_non_string_label():
    result = contradictory_dimensions({7: [_feet(100.0)]}, tolerance=0.01)
    assert isinstance(result, CheckUnevaluable)
    assert "dimension labels must be strings" in result.reason


@pytest.mark.parametrize(
    "bad_statement", [100.0, _UNRESOLVED], ids=["raw_number", "unresolved_result"]
)
def test_contradictory_dimensions_unevaluable_on_non_resolved_statement(bad_statement):
    result = contradictory_dimensions(
        {"north_boundary": [_feet(100.0), bad_statement]}, tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert (
        "statements['north_boundary'][1] must be a resolved ValidatedDistance"
        in result.reason
    )


def test_contradictory_dimensions_unevaluable_on_mixed_units_within_label():
    result = contradictory_dimensions(
        {"north_boundary": [_feet(100.0), _meters(100.0)]}, tolerance=0.01
    )
    assert isinstance(result, CheckUnevaluable)
    assert "statements['north_boundary'] state mixed units" in result.reason


def test_contradictory_dimensions_unevaluable_on_mixed_units_across_labels():
    # Each label is internally uniform, but the single stated tolerance can only be
    # in one stated unit, so cross-label mixing refuses rather than comparing.
    result = contradictory_dimensions(
        {
            "north_boundary": [_feet(100.0), _feet(100.0)],
            "east_boundary": [_meters(50.0), _meters(50.0)],
        },
        tolerance=0.01,
    )
    assert isinstance(result, CheckUnevaluable)
    assert "one shared stated unit across all labels" in result.reason


@_BAD_TOLERANCES
def test_contradictory_dimensions_unevaluable_on_unusable_tolerance(bad_tolerance):
    result = contradictory_dimensions(
        {"north_boundary": [_feet(100.0), _feet(100.0)]}, tolerance=bad_tolerance
    )
    assert isinstance(result, CheckUnevaluable)
    assert "tolerance must be" in result.reason


# ----------------------------------------------------------------- provenance


def test_contradictory_dimensions_fail_payload_serializes_to_json():
    result = contradictory_dimensions(
        {"north_boundary": [_feet(100.0), _feet(103.25)]}, tolerance=0.01
    )
    assert isinstance(result, CheckFailed)
    payload = result.to_payload()
    assert payload["check_name"] == "contradictory_dimensions"
    assert payload["outcome"] == "failed"
    assert payload["computed"]["north_boundary.restatement[1]"] == 103.25
    assert json.loads(json.dumps(payload)) == payload


def test_checks_package_reexports_area_checks():
    assert checks_package.calculated_vs_stated_area is calculated_vs_stated_area
    assert checks_package.contradictory_dimensions is contradictory_dimensions
    assert "calculated_vs_stated_area" in checks_package.__all__
    assert "contradictory_dimensions" in checks_package.__all__
