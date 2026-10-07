"""Lot-reach measurements (task M5-T127): acceptance scenarios S1 to S5.

Offline and deterministic. The real benchmark lot (215-16 Northern Blvd, BBL 4073340070) is
replayed through the recorded pack; the three made-up corner rectangles C1, C2 and C3 are
built as outlines, each street center line placed half its mapped width outside the lot line
it fronts (the stated premise of app.spatial.site_geometry.adjacency). Every expected number
is PARSED from the corner-reach reference case (docs/reference-cases/R6B/cases/corner-reach.json)
through its loader -- never retyped and never taken from the module under test.

Tolerance: both the reference row and the module quote feet to two decimals (0.01 ft), so
0.01 ft is the shared rounding unit. A reach taken along the wrong axis or from the wrong
corner is wrong by whole feet, far outside it; the mutation proof (producer report, check e)
runs a wrong-axis copy of the module outside the repository and shows the row fails and is
named.
"""

from __future__ import annotations

import math
import pathlib
import re
import sys

import pytest

from app.spatial import lot_reach
from app.spatial.site_geometry import (
    LotOutline,
    StreetCenterline,
    StreetData,
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.labels import LABEL_TAX_MAP, LABEL_UNKNOWN
from app.spatial.site_geometry.outline import prepare_outline
from app.spatial.site_geometry.results import FRONTAGE_CONFIRMED

from ._northern_replay import DCM_ENVELOPE, replay_dcm_page, replay_lot_geometry

_REF_LIB_DIR = pathlib.Path(__file__).resolve().parents[1] / "rules" / "reference_cases"
if str(_REF_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_REF_LIB_DIR))

import r6b_reference_cases_lib as reference_cases  # noqa: E402

CRS = {"wkid": 102718, "latest_wkid": 2263}
ENVELOPE = (-1000.0, -1000.0, 1000.0, 1000.0)
REACH_TOL_FT = 0.01
ANGLE_TOL_DEG = 0.1


# --------------------------------------------------------------------------- offline builders


def _lot(points) -> LotOutline:
    return LotOutline(tuple(points), CRS, "synthetic tax-lot")


def _street_for_edge(key, a, b, width="60", *, extra_offset=0.0, extend=300.0) -> StreetCenterline:
    """A center line parallel to the counterclockwise lot edge a->b, half the mapped width
    outside it."""
    length = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = uy, -ux
    offset = float(width) / 2.0 + extra_offset
    start = (a[0] - ux * extend + nx * offset, a[1] - uy * extend + ny * offset)
    end = (b[0] + ux * extend + nx * offset, b[1] + uy * extend + ny * offset)
    return StreetCenterline(key, key, None, ((start, end),), width, True)


def _streets(*centerlines) -> StreetData:
    return StreetData(tuple(centerlines), ENVELOPE, CRS, "synthetic streets")


def _joined(first: StreetCenterline, second: StreetCenterline):
    """One bent center line: both pieces extended to where their lines meet."""
    (a0, a1), (b0, b1) = first.paths[0], second.paths[0]
    da = (a1[0] - a0[0], a1[1] - a0[1])
    db = (b1[0] - b0[0], b1[1] - b0[1])
    denom = da[0] * db[1] - da[1] * db[0]
    t = ((b0[0] - a0[0]) * db[1] - (b0[1] - a0[1]) * db[0]) / denom
    meet = (a0[0] + da[0] * t, a0[1] + da[1] * t)
    far_a = (a0[0] - da[0] * 5, a0[1] - da[1] * 5)
    far_b = (b1[0] + db[0] * 5, b1[1] + db[1] * 5)
    return (far_a, meet, far_b)


def _measure(points, *centerlines):
    lot = _lot(points)
    geometry = derive_site_geometry(lot, _streets(*centerlines))
    prepared, _reason = prepare_outline(lot)
    return geometry, lot_reach.measure_lot_reach(prepared, geometry)


def _reach_by_street(result) -> dict:
    return {line.street_key: line.reach for line in result.street_lines}


def _number_after(pattern: str, text: str, row_id: str) -> float:
    match = re.search(pattern, text)
    assert match, f"{row_id}: reference row text has no match for {pattern!r}"
    return float(match.group(1))


def _assert_ft(got, expected, row_id, what):
    message = f"{row_id}: {what} -- measured {got!r}, reference {expected!r}"
    assert got is not None, message
    assert got == pytest.approx(expected, abs=REACH_TOL_FT), message


# --------------------------------------------------------------------------- S1 real lot


def test_real_benchmark_lot_matches_the_reference_case():
    row = reference_cases.load_row("corner-reach", "real-lot-reach")
    assert row["kind"] == "value"
    text = row["value"]
    expect_northern = _number_after(
        r"Northern Boulevard street line the lot reaches at most (\d+\.\d+) ft", text,
        "real-lot-reach")
    expect_place = _number_after(
        r"215 Place street line at most (\d+\.\d+) ft", text, "real-lot-reach")
    expect_corner = _number_after(
        r"from the corner point at most (\d+\.\d+) ft", text, "real-lot-reach")

    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    result = lot_reach.measure_lot_reach(prepared, geometry)

    assert geometry.lot_type.kind == "corner"
    reaches = _reach_by_street(result)
    _assert_ft(reaches["Northern Boulevard"].value, expect_northern, "real-lot-reach",
               "reach from the Northern Boulevard street line")
    _assert_ft(reaches["215 Place"].value, expect_place, "real-lot-reach",
               "reach from the 215 Place street line")
    _assert_ft(result.corner.reach.value, expect_corner, "real-lot-reach",
               "farthest distance from the corner point")
    assert reaches["Northern Boulevard"].label == LABEL_TAX_MAP
    assert result.corner.reach.label == LABEL_TAX_MAP
    assert result.corner.corner_point is not None
    # The module carries the site-geometry corner angle, never an invented one.
    (relation,) = geometry.lot_type.relations
    assert result.corner.angle.value == pytest.approx(relation.angle_deg, abs=ANGLE_TOL_DEG)
    assert result.corner.angle.label == LABEL_TAX_MAP


# --------------------------------------------------------------------------- S2 made-up lots


@pytest.mark.parametrize(("row_id", "frontage_a", "frontage_b"), [
    ("C1-reach", 40.0, 100.0),
    ("C2-reach", 60.0, 80.0),
    ("C3-reach", 150.0, 100.0),
])
def test_made_up_corner_lots_match_the_reference_case(row_id, frontage_a, frontage_b):
    row = reference_cases.load_row("corner-reach", row_id)
    assert row["kind"] == "value"
    text = row["value"]
    expect_a = _number_after(r"reach (\d+\.\d+) ft from street line A", text, row_id)
    expect_b = _number_after(r"and (\d+\.\d+) ft from street line B", text, row_id)
    expect_corner = _number_after(r"diagonal to the far corner is (\d+\.\d+) ft", text, row_id)

    # Street A along the bottom edge (frontage_a long); Street B along the left edge
    # (frontage_b long). The reach from street line A is then the frontage_b dimension.
    points = [(0.0, 0.0), (frontage_a, 0.0), (frontage_a, frontage_b), (0.0, frontage_b)]
    street_a = _street_for_edge("Street A", (0.0, 0.0), (frontage_a, 0.0))
    street_b = _street_for_edge("Street B", (0.0, frontage_b), (0.0, 0.0))
    geometry, result = _measure(points, street_a, street_b)

    assert geometry.lot_type.kind == "corner", f"{row_id}: expected a corner lot"
    reaches = _reach_by_street(result)
    _assert_ft(reaches["Street A"].value, expect_a, row_id, "reach from street line A")
    _assert_ft(reaches["Street B"].value, expect_b, row_id, "reach from street line B")
    _assert_ft(result.corner.reach.value, expect_corner, row_id,
               "farthest distance from the corner point")
    assert reaches["Street A"].label == LABEL_TAX_MAP
    assert result.corner.reach.label == LABEL_TAX_MAP
    # The 90-degree corner is a property of the right-angle rectangle built here -- not a
    # reference reach value, and not read back from the module under test.
    assert result.corner.angle.value == pytest.approx(90.0, abs=ANGLE_TOL_DEG), \
        f"{row_id}: corner angle"
    assert result.corner.corner_point == pytest.approx((0.0, 0.0), abs=REACH_TOL_FT)


# --------------------------------------------------------------------------- S3 unknown stays


def test_refused_outline_leaves_every_reach_unknown_never_zero():
    lot = _lot([(0.0, 0.0), (10.0, 0.0)])  # two points: the outline is refused
    geometry = derive_site_geometry(lot, _streets())
    prepared, reason = prepare_outline(lot)
    assert prepared is None and reason
    result = lot_reach.measure_lot_reach(prepared, geometry)
    assert result.street_lines == ()
    corner = result.corner
    assert corner.reach.value is None and corner.reach.label == LABEL_UNKNOWN
    assert corner.reach.reason
    assert corner.angle.value is None and corner.angle.label == LABEL_UNKNOWN
    assert corner.corner_point is None
    assert corner.first_street is None and corner.second_street is None


def test_interior_lot_gives_its_one_reach_and_no_corner():
    points = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]
    main = _street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0))
    geometry, result = _measure(points, main)
    assert geometry.lot_type.kind == "interior"
    reaches = _reach_by_street(result)
    assert reaches["Main Street"].value == pytest.approx(100.0, abs=REACH_TOL_FT)
    assert reaches["Main Street"].label == LABEL_TAX_MAP
    corner = result.corner
    assert corner.reach.value is None and corner.reach.label == LABEL_UNKNOWN
    assert "no corner point" in corner.reach.reason
    assert corner.corner_point is None


def test_through_lot_gives_both_reaches_but_no_corner():
    points = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]
    main = _street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0))
    back = _street_for_edge("Back Street", (25.0, 100.0), (0.0, 100.0), "50")
    geometry, result = _measure(points, main, back)
    assert geometry.lot_type.kind == "through"
    reaches = _reach_by_street(result)
    assert reaches["Main Street"].value == pytest.approx(100.0, abs=REACH_TOL_FT)
    assert reaches["Back Street"].value == pytest.approx(100.0, abs=REACH_TOL_FT)
    corner = result.corner
    assert corner.reach.value is None and corner.reach.label == LABEL_UNKNOWN
    assert "do not meet at a corner" in corner.reach.reason
    assert corner.corner_point is None


def test_uncertain_frontage_reach_is_unknown():
    # A corner lot whose First Avenue center line is 16 ft off: that side is uncertain.
    points = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]
    main = _street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0))
    first = _street_for_edge("First Avenue", (0.0, 100.0), (0.0, 0.0), "80", extra_offset=16.0)
    geometry, result = _measure(points, main, first)
    reaches = _reach_by_street(result)
    assert reaches["Main Street"].value == pytest.approx(100.0, abs=REACH_TOL_FT)
    assert reaches["First Avenue"].value is None
    assert reaches["First Avenue"].label == LABEL_UNKNOWN
    assert "not confirmed" in reaches["First Avenue"].reason
    # Only one street has a confirmed, straight frontage, so there is no corner.
    assert result.corner.reach.value is None and result.corner.corner_point is None


def test_bending_frontage_reach_is_unknown():
    bend = math.radians(30.0)
    corner = (50.0 + 40.0 * math.cos(bend), 40.0 * math.sin(bend))
    back = (corner[0] - 80.0 * math.sin(bend), corner[1] + 80.0 * math.cos(bend))
    points = [(0.0, 0.0), (50.0, 0.0), corner, back, (0.0, 80.0)]
    first = _street_for_edge("Bend Street", (0.0, 0.0), (50.0, 0.0), extend=0.0)
    second = _street_for_edge("Bend Street", (50.0, 0.0), corner, extend=0.0)
    joined = StreetCenterline("Bend Street", "Bend Street", None, (_joined(first, second),),
                              "60", True)
    geometry, result = _measure(points, joined)
    assert geometry.frontage("Bend Street").status == FRONTAGE_CONFIRMED  # confirmed but bends
    reach = _reach_by_street(result)["Bend Street"]
    assert reach.value is None and reach.label == LABEL_UNKNOWN
    assert "not straight" in reach.reason


# --------------------------------------------------------------------------- S4 measurements only


def test_measurements_only_no_law_in_the_module():
    source = pathlib.Path(lot_reach.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for token in ("100", "135"):
        assert token not in source, f"the module names the legal constant {token!r}"
    for token in ("coverage", "yard"):
        assert token not in lowered, f"the module names {token!r}"
    assert "app.rules" not in source and "app.scenario" not in source
    assert "import" in source  # sanity: the source really was read


def test_nothing_imports_the_module_yet():
    app_root = pathlib.Path(lot_reach.__file__).resolve().parents[1]  # services/api/app
    offenders = [
        str(path) for path in app_root.rglob("*.py")
        if path.name != "lot_reach.py" and "lot_reach" in path.read_text(encoding="utf-8")
    ]
    assert offenders == [], f"these modules already reference lot_reach: {offenders}"


# --------------------------------------------------------------------------- S5 independence


def test_expected_values_are_read_from_the_reference_case_not_the_module():
    # The reference rows carry the numbers as prose; the test parses them and never asks the
    # module under test for an expected value. The mutation proof (a reach along the wrong
    # axis, or from the wrong corner, fails a row above and names it) is recorded in the
    # producer report, run against a copy of the module outside the repository.
    for row_id in ("real-lot-reach", "C1-reach", "C2-reach", "C3-reach"):
        row = reference_cases.load_row("corner-reach", row_id)
        assert row["kind"] == "value"
        assert re.search(r"\d+\.\d+ ft", row["value"]), f"{row_id}: no measured feet in the row"
