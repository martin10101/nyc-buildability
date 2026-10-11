"""Street areas: the gaps between the tax lots, named by the centre line that
runs through them (M5-T155, S1). The engine is pure geometry; these tests work
it directly with constructed polygons so the behaviour is unambiguous."""

from __future__ import annotations

from shapely.geometry import Polygon as ShapelyPolygon

from app.drawings.maps.model import Polygon, StreetLine
from app.drawings.maps.street_areas import (
    MIN_STREET_AREA_SQFT,
    clip_street,
    street_areas,
)


def _poly(pts: list[tuple[float, float]]) -> Polygon:
    ring = tuple((float(x), float(y)) for x, y in pts)
    return Polygon(rings=(ring + (ring[0],),), source="/map_context/tax_lots/entries/0/outline")


def _street(name: str, width: float | None, paths) -> StreetLine:
    return StreetLine(
        name=name, name_source=f"/s/{name}/name",
        width_text=str(int(width)) if width is not None else None,
        width_source=f"/s/{name}/width_text",
        mapped_width_ft=width, mapped_width_source=f"/s/{name}/mapped_width_ft",
        paths=tuple(tuple(tuple(map(float, p)) for p in path) for path in paths),
        source=f"/s/{name}")


# Four lots around a cross street: a horizontal Cross Street (y=100) and a
# vertical Main Avenue (x=100); the gap is the plus-shaped street space.
LOTS = [
    _poly([(10, 110), (90, 110), (90, 190), (10, 190)]),
    _poly([(110, 110), (190, 110), (190, 190), (110, 190)]),
    _poly([(10, 10), (90, 10), (90, 90), (10, 90)]),
    _poly([(110, 10), (190, 10), (190, 90), (110, 90)]),
]
STREETS = [
    _street("Cross Street", 60.0, [[(0, 100), (200, 100)]]),
    _street("Main Avenue", 50.0, [[(100, 0), (100, 200)]]),
]
WINDOW = (0.0, 0.0, 200.0, 200.0)


def test_street_area_is_the_window_minus_the_lots_named_by_its_centre_lines():
    areas = street_areas(WINDOW, LOTS, STREETS)
    assert len(areas) == 1  # the plus is one connected gap
    names = {run.name for area in areas for run in area.runs}
    assert names == {"Cross Street", "Main Avenue"}
    widths = {run.name: run.mapped_width_ft for area in areas for run in area.runs}
    assert widths == {"Cross Street": 60.0, "Main Avenue": 50.0}


def _ring(pts: list[tuple[float, float]]):
    ring = tuple((float(x), float(y)) for x, y in pts)
    return ring + (ring[0],)


def test_a_gap_no_centre_line_runs_through_is_drawn_unnamed():
    # Lot A (left) and Lot B (right, with a courtyard hole) leave two SEPARATE
    # gaps: a vertical corridor between them (crossed by Centre Street) and the
    # enclosed courtyard inside B (no centre line) - drawn unnamed.
    lot_a = _poly([(0, 0), (90, 0), (90, 100), (0, 100)])
    lot_b = Polygon(
        rings=(_ring([(110, 0), (300, 0), (300, 100), (110, 100)]),
               _ring([(180, 30), (220, 30), (220, 70), (180, 70)])),
        source="/map_context/tax_lots/entries/1/outline")
    streets = [_street("Centre Street", 60.0, [[(100, 0), (100, 100)]])]
    areas = street_areas((0, 0, 300, 100), [lot_a, lot_b], streets)
    named = [a for a in areas if a.runs]
    unnamed = [a for a in areas if not a.runs]
    assert named and unnamed  # the corridor is named; the courtyard is unnamed
    assert all(run.name == "Centre Street" for a in named for run in a.runs)


def test_slivers_under_the_minimum_are_dropped():
    # two lots with a hair-thin gap between them (< MIN_STREET_AREA_SQFT).
    gap_w = 0.2
    lots = [
        _poly([(0, 0), (50, 0), (50, 100), (0, 100)]),
        _poly([(50 + gap_w, 0), (100, 0), (100, 100), (50 + gap_w, 100)]),
    ]
    # the sliver between them is 0.2 x 100 = 20 sq ft < 40; only the frame remains.
    areas = street_areas((0, 0, 100, 100), lots, [])
    for area in areas:
        sp = ShapelyPolygon(area.outline.exterior)
        assert sp.area >= MIN_STREET_AREA_SQFT
    # the thin interior sliver is not among the pieces
    assert not any(
        ShapelyPolygon(a.outline.exterior).bounds[2]
        - ShapelyPolygon(a.outline.exterior).bounds[0] < 1.0
        for a in areas
    )


def test_street_area_never_overlaps_a_tax_lot():
    # MUTATION GUARD: if the engine failed to subtract a neighbouring lot, a gap
    # would cover it. Every street area's interior is clear of every tax lot.
    areas = street_areas(WINDOW, LOTS, STREETS)
    assert areas
    for area in areas:
        gap = ShapelyPolygon(area.outline.exterior,
                             [ring for ring in area.outline.rings[1:]])
        for lot in LOTS:
            overlap = gap.intersection(ShapelyPolygon(lot.exterior)).area
            assert overlap < 1.0, f"street area overlaps a tax lot by {overlap:.2f} sq ft"


def test_street_areas_are_deterministic():
    first = street_areas(WINDOW, LOTS, STREETS)
    again = street_areas(WINDOW, LOTS, STREETS)
    assert [a.outline.rings for a in first] == [a.outline.rings for a in again]
    assert [[r.name for r in a.runs] for a in first] == [[r.name for r in a.runs] for a in again]


def test_clip_street_keeps_only_the_in_window_pieces():
    street = _street("Long Road", 60.0, [[(-500, 100), (700, 100)]])
    pieces = clip_street(street, WINDOW)
    assert pieces
    for piece in pieces:
        for x, _y in piece:
            assert -1e-6 <= x <= 200.0 + 1e-6
