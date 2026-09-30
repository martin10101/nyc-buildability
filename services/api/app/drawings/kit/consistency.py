"""Drawn geometry must agree with the printed numbers (check C-4, plan section 5c).

The drawings print ``gross_sf``, ``height_ft`` and ``depth_ft`` read from the
results beside shapes drawn from the results' outlines. These checks refuse
(fail closed) results whose outlines and numbers disagree, so a drawing can
never show a plate a quarter of the size of the area printed beside it:

* floor plates agree with the floor-by-floor table (same floors and uses,
  same gross area per floor and use);
* each floor plate's outline area (exterior minus holes) equals its
  ``gross_sf`` within ``max(PLATE_AREA_TOL_SF, PLATE_AREA_TOL_REL x gross_sf)``;
* each required yard's outline reaches ``depth_ft`` from a lot line it adjoins
  (within ``YARD_DEPTH_TOL_FT``, the printing precision);
* one floor-to-floor height per floor, and floor numbers without gaps.
"""

from __future__ import annotations

from . import geometry as geo
from .errors import DrawingInputError
from .model import FloorPlate, FloorRow, Point, Polygon, Ring, Yard

__all__ = [
    "GROSS_SF_TOL",
    "PLATE_AREA_TOL_REL",
    "PLATE_AREA_TOL_SF",
    "YARD_DEPTH_TOL_FT",
    "check_floor_numbers",
    "check_plate_areas",
    "check_plates_match_rows",
    "check_yard_depths",
    "polygon_area",
    "yard_depths",
]

GROSS_SF_TOL = 0.01
PLATE_AREA_TOL_SF = 1.0  # absorbs a gross area rounded to whole square feet
PLATE_AREA_TOL_REL = 0.001
YARD_DEPTH_TOL_FT = 0.01  # labels print feet to two decimals
_ON_LINE_TOL_FT = 0.01


def polygon_area(polygon: Polygon) -> float:
    return geo.ring_area(polygon.exterior) - sum(geo.ring_area(h) for h in polygon.holes)


def check_plate_areas(plates: tuple[FloorPlate, ...]) -> None:
    for plate in plates:
        drawn = polygon_area(plate.outline)
        tolerance = max(PLATE_AREA_TOL_SF, PLATE_AREA_TOL_REL * plate.gross_sf)
        if abs(drawn - plate.gross_sf) > tolerance:
            raise DrawingInputError(
                "plate_area_mismatch",
                f"outline encloses {drawn:.2f} sf but gross_sf is {plate.gross_sf} sf",
                location=plate.source,
            )


def _sums(items, key) -> dict[tuple[int, str], float]:
    sums: dict[tuple[int, str], float] = {}
    for item in items:
        sums[key(item)] = sums.get(key(item), 0.0) + item.gross_sf
    return sums


def check_plates_match_rows(plates: tuple[FloorPlate, ...], rows: tuple[FloorRow, ...]) -> None:
    plate_sums = _sums(plates, lambda p: (p.floor, p.use))
    row_sums = _sums(rows, lambda r: (r.floor, r.use))
    for key in sorted(set(plate_sums) | set(row_sums)):
        a, b = plate_sums.get(key), row_sums.get(key)
        if a is None or b is None or abs(a - b) > GROSS_SF_TOL:
            raise DrawingInputError(
                "plates_rows_mismatch",
                f"floor {key[0]} {key[1]}: floor plates {a} sf vs floor-by-floor {b} sf",
                location="/geometry/floor_plates",
            )


def check_floor_numbers(rows: tuple[FloorRow, ...]) -> None:
    heights: dict[int, float] = {}
    for row in rows:
        if row.floor in heights and heights[row.floor] != row.height_ft:
            raise DrawingInputError("floor_height_conflict",
                                    f"floor {row.floor} has two floor-to-floor heights",
                                    location=row.source)
        heights[row.floor] = row.height_ft
    above = sorted(f for f in heights if f >= 1)
    below = sorted((f for f in heights if f <= 0), reverse=True)
    if above != list(range(1, len(above) + 1)) or below != list(range(0, -len(below), -1)):
        raise DrawingInputError("floors_not_contiguous",
                                "floor numbers must run 1..N above grade and 0, -1, ... below",
                                location="/floor_by_floor")


def _distance_to_line(p: Point, a: Point, b: Point) -> float:
    length = geo.edge_length(a, b)
    return abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / length


def _adjoins(lot_edge: tuple[Point, Point], ring: Ring) -> bool:
    """Whether some edge of ``ring`` runs along ``lot_edge`` for a positive length."""
    a, b = lot_edge
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy
    for c, d in geo.edges(ring):
        if max(_distance_to_line(c, a, b), _distance_to_line(d, a, b)) > _ON_LINE_TOL_FT:
            continue
        tc = ((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / length_sq
        td = ((d[0] - a[0]) * dx + (d[1] - a[1]) * dy) / length_sq
        overlap = min(max(tc, td), 1.0) - max(min(tc, td), 0.0)
        if overlap * length_sq ** 0.5 > _ON_LINE_TOL_FT:
            return True
    return False


def yard_depths(yard: Yard, lot: Polygon) -> list[float]:
    """How far the yard reaches from each lot line it adjoins."""
    ring = yard.outline.exterior
    return [
        max(_distance_to_line(p, a, b) for p in ring[:-1])
        for a, b in geo.edges(lot.exterior)
        if _adjoins((a, b), ring)
    ]


def check_yard_depths(yards: tuple[Yard, ...], lot: Polygon) -> None:
    for yard in yards:
        reaches = yard_depths(yard, lot)
        if not any(abs(reach - yard.depth_ft) <= YARD_DEPTH_TOL_FT for reach in reaches):
            drawn = ", ".join(f"{reach:.2f}" for reach in reaches) or "none"
            raise DrawingInputError(
                "yard_depth_mismatch",
                f"depth_ft is {yard.depth_ft} ft but the outline reaches {drawn} ft "
                "from the lot lines it adjoins",
                location=yard.source,
            )
