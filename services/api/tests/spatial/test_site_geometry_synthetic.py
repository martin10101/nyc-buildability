"""Single-lot site geometry on small synthetic lots (queue item B-03; plan M1-13, §4).

Offline and deterministic. Lots are EPSG:2263-stamped rings in feet; each street center
line is placed half its mapped width outside the lot line it should front (the stated
premise of app.spatial.site_geometry.adjacency), unless a test moves it on purpose.
"""

from __future__ import annotations

import math

import pytest

from app.spatial.site_geometry import (
    LABEL_CITY_RECORDS,
    LABEL_TAX_MAP,
    LABEL_UNKNOWN,
    CityRecordLot,
    LotOutline,
    StreetCenterline,
    StreetData,
    derive_site_geometry,
)
from app.spatial.site_geometry.parameters import parameters_snapshot
from app.spatial.site_geometry.results import (
    EDGE_FRONTS,
    EDGE_NO_STREET,
    EDGE_UNCERTAIN,
    FRONTAGE_CONFIRMED,
    FRONTAGE_UNCERTAIN,
    RELATION_CORNER,
    RELATION_THROUGH,
    STATUS_COMPLETE,
    STATUS_PARTIAL,
    STATUS_REFUSED,
)

CRS = {"wkid": 102718, "latest_wkid": 2263}
ENVELOPE = (-1000.0, -1000.0, 1000.0, 1000.0)
RECT = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]


def lot(points, crs=CRS) -> LotOutline:
    return LotOutline(tuple(points), crs, "synthetic tax-lot")


def street_for_edge(name, a, b, width="60", *, extra_offset=0.0, extend=300.0, ok=True,
                    note=None, oid=None) -> StreetCenterline:
    """Center line parallel to the counterclockwise lot edge a->b, half the width outside it."""
    length = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = uy, -ux
    offset = float(width) / 2.0 + extra_offset if _number(width) else 30.0 + extra_offset
    start = (a[0] - ux * extend + nx * offset, a[1] - uy * extend + ny * offset)
    end = (b[0] + ux * extend + nx * offset, b[1] + uy * extend + ny * offset)
    return StreetCenterline(name, name, oid, ((start, end),), width, ok, note)


def _number(text) -> bool:
    try:
        float(text)
    except (TypeError, ValueError):
        return False
    return True


def streets(*centerlines, envelope=ENVELOPE, crs=CRS, incomplete=()) -> StreetData:
    return StreetData(tuple(centerlines), envelope, crs, "synthetic streets", tuple(incomplete))


MAIN = street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0))


# --------------------------------------------------------------------------- happy paths


def test_rectangle_interior_lot():
    result = derive_site_geometry(lot(RECT), streets(MAIN))
    assert result.status == STATUS_COMPLETE
    assert result.lot_type.kind == "interior"
    assert result.lot_type.label == LABEL_TAX_MAP
    assert result.lot_type.streets == ("Main Street",)
    assert result.lot_area.value == 2500.0
    assert result.lot_area.label == LABEL_TAX_MAP
    (main,) = result.frontages
    assert main.status == FRONTAGE_CONFIRMED
    assert main.length.value == 25.0 and main.length.label == LABEL_TAX_MAP
    assert main.mapped_width_raw == ()  # no object ids on synthetic streets
    assert main.depth.minimum.value == main.depth.maximum.value == 100.0
    assert result.lot_depth.value == 100.0 and result.lot_depth.label == LABEL_TAX_MAP
    assert [e.verdict for e in result.edges] == [EDGE_FRONTS, EDGE_NO_STREET, EDGE_NO_STREET,
                                                 EDGE_NO_STREET]


def test_clockwise_ring_and_closing_vertex_give_the_same_answer():
    ring = list(reversed(RECT)) + [RECT[-1]]
    result = derive_site_geometry(lot(ring), streets(MAIN))
    assert result.lot_type.kind == "interior"
    assert result.frontages[0].length.value == 25.0


def test_corner_lot():
    first_ave = street_for_edge("First Avenue", (0.0, 100.0), (0.0, 0.0), "80")
    result = derive_site_geometry(lot(RECT), streets(MAIN, first_ave))
    assert result.status == STATUS_COMPLETE
    assert result.lot_type.kind == "corner"
    assert result.lot_type.streets == ("First Avenue", "Main Street")
    (relation,) = result.lot_type.relations
    assert relation.relation == RELATION_CORNER and relation.angle_deg == 90.0
    assert result.frontage("Main Street").length.value == 25.0
    assert result.frontage("First Avenue").length.value == 100.0
    assert result.frontage("Main Street").depth.mean.value == 100.0
    assert result.frontage("First Avenue").depth.mean.value == 25.0
    assert result.lot_depth.value is None
    assert result.lot_depth.label == LABEL_UNKNOWN
    assert "corner lot" in result.lot_depth.reason


def test_through_lot():
    back = street_for_edge("Back Street", (25.0, 100.0), (0.0, 100.0), "50")
    result = derive_site_geometry(lot(RECT), streets(MAIN, back))
    assert result.status == STATUS_COMPLETE
    assert result.lot_type.kind == "through"
    assert result.lot_type.relations[0].relation == RELATION_THROUGH
    assert result.frontage("Back Street").length.value == 25.0
    assert result.lot_depth.value == 100.0


def test_irregular_trapezoid_interior_lot_depth_range():
    ring = [(0.0, 0.0), (40.0, 0.0), (40.0, 90.0), (0.0, 110.0)]
    main = street_for_edge("Main Street", (0.0, 0.0), (40.0, 0.0))
    result = derive_site_geometry(lot(ring), streets(main))
    assert result.lot_type.kind == "interior"
    assert result.lot_area.value == 4000.0
    depth = result.frontages[0].depth
    assert depth.minimum.value == pytest.approx(90.25, abs=0.01)
    assert depth.maximum.value == pytest.approx(109.75, abs=0.01)
    assert depth.mean.value == pytest.approx(100.0, abs=0.01)
    assert result.lot_depth.value == pytest.approx(100.0, abs=0.01)


def test_irregular_l_shaped_lot():
    ring = [(0.0, 0.0), (40.0, 0.0), (40.0, 60.0), (20.0, 60.0), (20.0, 100.0), (0.0, 100.0)]
    main = street_for_edge("Main Street", (0.0, 0.0), (40.0, 0.0))
    result = derive_site_geometry(lot(ring), streets(main))
    assert result.lot_type.kind == "interior"
    assert result.lot_area.value == 3200.0
    depth = result.frontages[0].depth
    assert (depth.minimum.value, depth.maximum.value) == (60.0, 100.0)
    assert depth.mean.value == pytest.approx(80.0, abs=0.01)


def test_depth_skips_points_whose_ray_leaves_through_a_side_line():
    ring = [(0.0, 0.0), (25.0, 0.0), (35.0, 100.0), (10.0, 100.0)]  # sides lean 5.7 degrees
    result = derive_site_geometry(lot(ring), streets(MAIN))
    depth = result.frontages[0].depth
    assert (depth.minimum.value, depth.mean.value, depth.maximum.value) == (100.0, 100.0, 100.0)


def test_depth_unknown_when_no_clear_rear_lot_line():
    ring = [(0.0, 0.0), (25.0, 0.0), (55.0, 100.0), (30.0, 100.0)]  # every ray hits a side
    result = derive_site_geometry(lot(ring), streets(MAIN))
    assert result.lot_type.kind == "interior"
    depth = result.frontages[0].depth
    assert depth.mean.value is None and "no clear rear lot line" in depth.mean.reason
    assert result.lot_depth.value is None
    assert result.status == STATUS_PARTIAL


def test_street_across_a_side_line_is_not_frontage():
    # A street ending 20 ft west of the lot, running at 60 degrees to its west lot line: the
    # side line looks across that street, not along it.
    slope = math.tan(math.radians(30.0))
    diagonal = StreetCenterline("Diagonal Street", "Diagonal Street", None,
                                (((-200.0, 50.0 - 180.0 * slope), (-20.0, 50.0)),), "60", True)
    result = derive_site_geometry(lot(RECT), streets(MAIN, diagonal))
    assert result.edges[3].verdict == EDGE_NO_STREET
    assert result.lot_type.kind == "interior"


def test_lot_in_the_way_is_never_frontage():
    # A thin slot cut into the lot: the slot's upper side faces the street at 34 ft from its
    # center line (within the match tolerance) but the lot itself lies in between.
    ring = [(0.0, 0.0), (60.0, 0.0), (60.0, 2.0), (20.0, 2.0), (20.0, 4.0), (60.0, 4.0),
            (60.0, 100.0), (0.0, 100.0)]
    main = street_for_edge("Main Street", (0.0, 0.0), (60.0, 0.0))
    result = derive_site_geometry(lot(ring), streets(main))
    assert result.lot_type.kind == "interior"
    assert result.frontage("Main Street").length.value == 60.0


def test_bending_frontage_leaves_lot_type_and_depth_unknown():
    bend = math.radians(30.0)
    corner = (50.0 + 40.0 * math.cos(bend), 40.0 * math.sin(bend))
    back = (corner[0] - 80.0 * math.sin(bend), corner[1] + 80.0 * math.cos(bend))
    ring = [(0.0, 0.0), (50.0, 0.0), corner, back, (0.0, 80.0)]
    first = street_for_edge("Bend Street", (0.0, 0.0), (50.0, 0.0), extend=0.0)
    second = street_for_edge("Bend Street", (50.0, 0.0), corner, extend=0.0)
    joined = StreetCenterline("Bend Street", "Bend Street", None,
                              (_joined(first, second),), "60", True)
    result = derive_site_geometry(lot(ring), streets(joined))
    assert result.lot_type.kind == "unknown"
    assert "not straight (its lot lines turn by 30 degrees)" in result.lot_type.reason
    frontage = result.frontage("Bend Street")
    assert frontage.status == FRONTAGE_CONFIRMED
    assert frontage.length.value == 90.0
    assert frontage.depth.mean.value is None
    assert result.lot_depth.value is None


def test_same_street_name_on_opposite_sides_is_unknown():
    north = street_for_edge("Loop Road", (25.0, 100.0), (0.0, 100.0))
    result = derive_site_geometry(lot(RECT), streets(main_named("Loop Road"), north))
    assert result.lot_type.kind == "unknown"
    assert "turn by 180 degrees" in result.lot_type.reason
    assert result.frontage("Loop Road").length.value == 50.0


def main_named(name: str) -> StreetCenterline:
    return StreetCenterline(name, name, None, MAIN.paths, MAIN.mapped_width_raw, True)


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


def test_corner_angle_outside_the_clear_corner_range_is_unknown():
    # Main Street and Slant Street meet at a 150-degree lot corner.
    tip = (-60.0 * math.cos(math.radians(30.0)), 60.0 * math.sin(math.radians(30.0)))
    ring = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (tip[0], 100.0), tip]
    main = street_for_edge("Main Street", (0.0, 0.0), (100.0, 0.0))
    slant = street_for_edge("Slant Street", tip, (0.0, 0.0))
    result = derive_site_geometry(lot(ring), streets(main, slant))
    assert [e.verdict for e in result.edges].count(EDGE_FRONTS) == 2
    assert result.lot_type.kind == "unknown"
    assert "outside the clear-corner range" in result.lot_type.reason
    assert result.lot_type.relations[0].angle_deg == pytest.approx(150.0, abs=0.1)


# --------------------------------------------------------------------------- area + records


def test_area_is_checked_against_city_records_and_never_replaced():
    records = CityRecordLot(2400.0, 25.0, 100.0, "PLUTO test")
    result = derive_site_geometry(lot(RECT), streets(MAIN), records)
    assert result.lot_area.value == 2500.0 and result.lot_area.label == LABEL_TAX_MAP
    assert result.city_records.lot_area.value == 2400.0
    assert result.city_records.lot_area.label == LABEL_CITY_RECORDS
    check = result.area_check
    assert (check.difference_sq_ft, check.difference_pct) == (100.0, 4.17)
    assert check.statement in result.notes


def test_missing_city_records_stay_unknown_never_zero():
    records = CityRecordLot(None, None, None, "PLUTO test")
    result = derive_site_geometry(lot(RECT), streets(MAIN), records)
    for value in (result.city_records.lot_area, result.city_records.lot_front,
                  result.city_records.lot_depth):
        assert value.value is None and value.label == LABEL_UNKNOWN and value.reason
    assert result.area_check is None
    assert derive_site_geometry(lot(RECT), streets(MAIN)).city_records.lot_area.value is None


def test_every_result_records_parameters_and_method():
    result = derive_site_geometry(lot(RECT), streets(MAIN))
    assert result.parameters == parameters_snapshot()
    assert result.provenance["method_version"] == "site-geometry-1"


# --------------------------------------------------------------------------- degenerate inputs

DEGENERATE = {
    "empty": [],
    "two_points": [(0.0, 0.0), (10.0, 0.0)],
    "collinear": [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)],
    "repeated_point": [(5.0, 5.0)] * 5,
    "bow_tie": [(0.0, 0.0), (10.0, 10.0), (10.0, 0.0), (0.0, 10.0)],
    "nan": [(0.0, 0.0), (10.0, 0.0), (float("nan"), 10.0)],
    "infinite": [(0.0, 0.0), (10.0, 0.0), (10.0, float("inf"))],
    "bool": [(0.0, 0.0), (True, 0.0), (10.0, 10.0)],
    "text": [(0.0, 0.0), ("10", 0.0), (10.0, 10.0)],
    "not_a_pair": [(0.0, 0.0), (10.0,), (10.0, 10.0)],
    "tiny": [(0.0, 0.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.5)],
}


@pytest.mark.parametrize("name", sorted(DEGENERATE))
def test_degenerate_outline_fails_closed(name):
    records = CityRecordLot(2500.0, 25.0, 100.0, "PLUTO test")
    result = derive_site_geometry(lot(DEGENERATE[name]), streets(MAIN), records)
    assert result.status == STATUS_REFUSED
    assert result.refusal_reason
    assert result.lot_area.value is None and result.lot_area.label == LABEL_UNKNOWN
    assert result.lot_type.kind == "unknown" and result.lot_type.reason
    assert result.lot_depth.value is None
    assert result.frontages == () and result.edges == ()
    assert result.city_records.lot_area.value == 2500.0  # still shown, never replaced


def test_degree_outline_is_never_measured():
    wgs84 = {"wkid": 4326, "latest_wkid": 4326}
    result = derive_site_geometry(lot([(-73.77, 40.76), (-73.76, 40.76), (-73.76, 40.77)],
                                      crs=wgs84), streets(MAIN))
    assert result.status == STATUS_REFUSED
    assert "EPSG:2263" in result.refusal_reason
    assert result.lot_area.value is None


def test_invalid_shape_reason_names_no_coordinates():
    result = derive_site_geometry(lot(DEGENERATE["bow_tie"]), streets(MAIN))
    assert "Self-intersection" in result.refusal_reason
    assert "[" not in result.refusal_reason


# --------------------------------------------------------------------------- street data gaps


def _assert_unknown_type(result, fragment):
    assert result.status == STATUS_PARTIAL
    assert result.lot_type.kind == "unknown" and result.lot_type.label == LABEL_UNKNOWN
    assert fragment in result.lot_type.reason
    assert result.lot_area.value == 2500.0  # the outline area stays known


def test_no_street_data():
    result = derive_site_geometry(lot(RECT), None)
    _assert_unknown_type(result, "No city street data")
    assert result.edges == () and result.frontages == ()


def test_street_data_in_degrees_is_not_read():
    result = derive_site_geometry(lot(RECT), streets(MAIN, crs={"wkid": 4326}))
    _assert_unknown_type(result, "not in EPSG:2263")
    assert result.edges == ()


def test_street_data_that_does_not_cover_the_search_radius():
    small = (-10.0, -40.0, 35.0, 110.0)
    result = derive_site_geometry(lot(RECT), streets(MAIN, envelope=small))
    _assert_unknown_type(result, "does not cover 150 ft")
    main = result.frontage("Main Street")
    assert main.status == FRONTAGE_UNCERTAIN and main.length.value is None
    assert main.length.reason.startswith("25.00 ft is confirmed, but")


@pytest.mark.parametrize("envelope", [None, (0.0, 0.0, 1.0), ("a", "b", "c", "d"),
                                      (float("nan"), -1000.0, 1000.0, 1000.0)])
def test_unusable_street_envelope(envelope):
    result = derive_site_geometry(lot(RECT), streets(MAIN, envelope=envelope))
    _assert_unknown_type(result, "does not cover 150 ft")


def test_street_wider_than_the_search_reaches():
    avenue = street_for_edge("Grand Avenue", (0.0, 0.0), (25.0, 0.0), "400")
    result = derive_site_geometry(lot(RECT), streets(avenue))
    _assert_unknown_type(result, "Grand Avenue is wider than the search reaches")


def test_incomplete_street_data():
    result = derive_site_geometry(lot(RECT), streets(MAIN, incomplete=("transfer limit hit",)))
    _assert_unknown_type(result, "transfer limit hit")
    assert result.frontage("Main Street").length.label == LABEL_UNKNOWN


def test_malformed_center_line_is_a_blocker():
    broken = StreetCenterline("Side Street", "Side Street", 7, (((0.0, 0.0),),), "60", True)
    result = derive_site_geometry(lot(RECT), streets(MAIN, broken))
    _assert_unknown_type(result, "Side Street has unusable center-line geometry")


def test_no_street_found():
    far = street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0), extra_offset=30.0)
    result = derive_site_geometry(lot(RECT), streets(far))
    _assert_unknown_type(result, "No street frontage was found")
    assert all(e.verdict == EDGE_NO_STREET for e in result.edges)


@pytest.mark.parametrize(
    ("street", "fragment"),
    [
        (street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0), extra_offset=10.0),
         "too far to be frontage, too close to rule it out"),
        (street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0), extra_offset=-10.0),
         "inside the mapped street"),
        (street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0), "varies"),
         "is not a single number"),
        (street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0), "60-80"),
         "is not a single number"),
        (street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0), ok=False,
                         note="the City Map flags it (paper_street='Y'); needs review"),
         "paper_street"),
    ],
    ids=["between", "inside", "prose_width", "range_width", "paper_street"],
)
def test_uncertain_street_line_leaves_lot_type_unknown(street, fragment):
    result = derive_site_geometry(lot(RECT), streets(street))
    _assert_unknown_type(result, fragment)
    assert result.edges[0].verdict == EDGE_UNCERTAIN
    frontage = result.frontage("Main Street")
    assert frontage.status == FRONTAGE_UNCERTAIN
    assert frontage.length.value is None
    assert frontage.length.reason.startswith("Possible frontage")


def test_street_at_an_angle_is_uncertain():
    angle = math.radians(20.0)
    ux, uy = math.cos(angle), math.sin(angle)
    center = (12.5, -30.0)
    path = ((center[0] - 300 * ux, center[1] - 300 * uy), (center[0] + 300 * ux,
                                                           center[1] + 300 * uy))
    skew = StreetCenterline("Skew Street", "Skew Street", None, (path,), "60", True)
    result = derive_site_geometry(lot(RECT), streets(skew))
    _assert_unknown_type(result, "runs at up to 20 degrees")


def test_street_that_ends_part_way_along_a_lot_line():
    short = StreetCenterline("Main Street", "Main Street", None,
                             (((12.0, -30.0), (300.0, -30.0)),), "60", True)
    result = derive_site_geometry(lot(RECT), streets(short))
    _assert_unknown_type(result, "the street line runs along only 52% of it")


def test_street_running_through_the_lot():
    through = StreetCenterline("Cut Street", "Cut Street", None,
                               (((-300.0, 50.0), (300.0, 50.0)),), "60", True)
    result = derive_site_geometry(lot(RECT), streets(MAIN, through))
    _assert_unknown_type(result, "(Cut Street) runs through the lot")
    assert result.street_crossings == ("Cut Street",)
    assert result.frontage("Cut Street").status == FRONTAGE_UNCERTAIN
    assert result.frontage("Main Street").status == FRONTAGE_CONFIRMED


def test_two_named_segments_along_one_lot_line_are_uncertain():
    left = StreetCenterline("West Name", "West Name", None,
                            (((-300.0, -30.0), (12.0, -30.0)),), "60", True)
    right = StreetCenterline("East Name", "East Name", None,
                             (((12.0, -30.0), (300.0, -30.0)),), "60", True)
    result = derive_site_geometry(lot(RECT), streets(left, right))
    _assert_unknown_type(result, "faces more than one street")


def test_side_line_next_to_a_narrow_corner_lot_is_uncertain():
    # A cross street 10 ft beyond the west lot line: a 10 ft neighbour lot at most.
    cross = street_for_edge("Cross Street", (0.0, 100.0), (0.0, 0.0), extra_offset=10.0)
    result = derive_site_geometry(lot(RECT), streets(MAIN, cross))
    _assert_unknown_type(result, "Cross Street")
    assert result.frontage("Main Street").status == FRONTAGE_CONFIRMED
