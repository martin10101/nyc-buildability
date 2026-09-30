"""Results contract -> :class:`DrawingInput` (validated, fail-closed).

1. The whole results document is validated by the shared server-side
   validator :func:`app.contracts.study_contracts.validate_results_document`
   (task C-03: bundled canonical schema, strict JSON, no fixture-only keys).
2. The geometry is then checked for what a schema cannot state: closed,
   finite, simple, non-degenerate rings; holes inside their exterior; yards,
   setback lines and floor plates inside the lot outline; street frontages on
   the lot boundary; every printed string well-formed for XML; and the drawn
   outlines agreeing with the printed numbers (:mod:`.consistency`, check C-4).

Any failure raises :class:`DrawingInputError`; nothing partial is returned.
``geometry: not_available`` is not an error - it returns :class:`Unavailable`
carrying the results' own reason.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from app.contracts.study_contracts import StudyContractError, validate_results_document

from . import geometry as geo
from .consistency import (
    check_floor_numbers,
    check_plate_areas,
    check_plates_match_rows,
    check_yard_depths,
)
from .errors import DrawingInputError
from .model import (
    CaseAssumption,
    DrawingInput,
    FloorPlate,
    FloorRow,
    LayerUnavailable,
    Point,
    Polygon,
    Ring,
    SetbackLine,
    Street,
    StreetWidthCase,
    Unavailable,
    Yard,
    YardNotRequired,
)
from .svg import xml_illegal

__all__ = [
    "FRONTAGE_TOL_FT",
    "MAX_ABS_COORD_FT",
    "MAX_FLOOR_PLATES",
    "MAX_RING_POINTS",
    "load_drawing_input",
]

MAX_RING_POINTS = 1024  # bounds the O(n^2) simplicity check
MAX_FLOOR_PLATES = 1000
MAX_ABS_COORD_FT = 1.0e8  # EPSG:2263 NYC values are ~1e6 ft; anything far beyond is corrupt
FRONTAGE_TOL_FT = 0.01  # a frontage end point this close to the lot boundary lies on it


def load_drawing_input(results: Mapping) -> DrawingInput | Unavailable:
    """Validate ``results`` and return the drawable geometry, or ``Unavailable``
    when the results carry no geometry at all."""
    _validate_schema(results)
    geometry = results["geometry"]
    if geometry["status"] == "not_available":
        return Unavailable("geometry", geometry["reason"], geometry["reason_kind"], "/geometry")

    lot = _polygon(geometry["lot_outline"], "/geometry/lot_outline")
    rows = tuple(
        _row(row, f"/floor_by_floor/{i}") for i, row in enumerate(results["floor_by_floor"])
    )
    plates = _floor_plates(geometry["floor_plates"], lot)
    if not isinstance(plates, LayerUnavailable):  # the massing stacks plates by these rows
        check_plate_areas(plates)
        check_plates_match_rows(plates, rows)
        check_floor_numbers(rows)
    yards, not_required = _yards(geometry["yards"], lot)
    if not isinstance(yards, LayerUnavailable):
        check_yard_depths(yards, lot)
    return DrawingInput(
        crs=geometry["crs"],
        measurement_label=_text(geometry["measurement"]["label"], "/geometry/measurement/label"),
        lot=lot,
        streets=tuple(
            _street(street, f"/geometry/streets/{i}", lot)
            for i, street in enumerate(geometry["streets"])
        ),
        yards=yards,
        yards_not_required=not_required,
        setback_lines=_setback_lines(geometry["setback_lines_per_level"], lot),
        floor_plates=plates,
        floor_rows=rows,
        street_width_case=_street_width_case(results["street_width_case"]),
    )


def _street_width_case(raw: Mapping | None) -> StreetWidthCase | None:
    if raw is None:
        return None
    base = "/street_width_case"
    return StreetWidthCase(
        marker=_text(raw["marker"], f"{base}/marker"),
        assumptions=tuple(
            CaseAssumption(_text(a["street"], f"{base}/assumptions/{i}/street"), a["assumed"],
                           f"{base}/assumptions/{i}")
            for i, a in enumerate(raw["assumptions"])
        ),
        source=base,
    )


def _validate_schema(results: Mapping) -> None:
    try:
        validate_results_document(results)
    except StudyContractError as exc:
        pointer = "" if exc.location == "<root>" else "/" + exc.location
        raise DrawingInputError("schema_invalid", str(exc), location=pointer) from exc


def _text(value: str, location: str) -> str:
    """A string the drawings print: refuse characters XML 1.0 forbids (C0 controls
    other than tab/LF/CR, lone surrogates, U+FFFE/U+FFFF), which would make the
    SVG malformed."""
    if xml_illegal(value):
        raise DrawingInputError("invalid_text", "text carries a character XML forbids",
                                location=location)
    return value


def _finite(value: float, location: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise DrawingInputError("non_finite_number", "value is not finite", location=location)
    return number


def _point(raw: Sequence, location: str) -> Point:
    x, y = _finite(raw[0], location), _finite(raw[1], location)
    if abs(x) > MAX_ABS_COORD_FT or abs(y) > MAX_ABS_COORD_FT:
        raise DrawingInputError(
            "coordinate_out_of_range", "coordinate beyond the supported extent", location=location
        )
    return (x, y)


def _ring(raw: Sequence, location: str) -> Ring:
    if len(raw) > MAX_RING_POINTS:
        raise DrawingInputError(
            "ring_too_large", f"more than {MAX_RING_POINTS} points", location=location
        )
    ring = tuple(_point(p, f"{location}/{i}") for i, p in enumerate(raw))
    if ring[0] != ring[-1]:
        raise DrawingInputError("ring_not_closed", "first and last point differ", location=location)
    if len(set(ring[:-1])) < 3:
        raise DrawingInputError(
            "ring_degenerate", "fewer than 3 distinct points", location=location
        )
    if not geo.is_simple(ring):
        raise DrawingInputError(
            "ring_not_simple", "outline crosses or touches itself", location=location
        )
    if abs(geo.signed_area(ring)) <= geo.BOUNDARY_TOL_FT:
        raise DrawingInputError("ring_zero_area", "outline encloses no area", location=location)
    return ring


def _polygon(raw: Sequence, location: str) -> Polygon:
    rings = tuple(_ring(r, f"{location}/{i}") for i, r in enumerate(raw))
    for i, hole in enumerate(rings[1:], start=1):
        if not geo.ring_within(hole, rings[0]):
            raise DrawingInputError(
                "hole_outside_exterior", "hole is not inside its exterior ring",
                location=f"{location}/{i}",
            )
    return Polygon(rings=rings, source=location)


def _clear_of_hole(polygon: Polygon, hole: Ring) -> bool:
    """Whether the polygon's solid part stays out of one of the lot's holes."""
    if not geo.interiors_overlap(polygon.exterior, hole):
        return True
    # The lot hole overlaps this outline: fine only inside one of its own holes.
    return any(geo.ring_within(hole, own) for own in polygon.holes)


def _check_within_lot(polygon: Polygon, lot: Polygon, code: str) -> None:
    inside = geo.ring_within(polygon.exterior, lot.exterior) and all(
        _clear_of_hole(polygon, hole) for hole in lot.holes
    )
    if not inside:
        raise DrawingInputError(code, "outline is not inside the lot outline",
                                location=polygon.source)


def _unavailable(layer: str, raw: Mapping, base: str) -> LayerUnavailable:
    return LayerUnavailable(layer, _text(raw["reason"], f"{base}/reason"), raw["reason_kind"],
                            base)


def _street(raw: Mapping, location: str, lot: Polygon) -> Street:
    frontage = tuple(
        _point(p, f"{location}/frontage_line/{i}") for i, p in enumerate(raw["frontage_line"])
    )
    for i, p in enumerate(frontage):
        if not geo.point_on_boundary(p, lot.exterior, FRONTAGE_TOL_FT):
            raise DrawingInputError(
                "frontage_off_lot", "frontage point is not on the lot boundary",
                location=f"{location}/frontage_line/{i}",
            )
    if all(geo.edge_length(frontage[0], p) <= FRONTAGE_TOL_FT for p in frontage[1:]):
        raise DrawingInputError("frontage_degenerate", "frontage has no length",
                                location=f"{location}/frontage_line")
    return Street(name=_text(raw["street"], f"{location}/street"), frontage=frontage,
                  source=location)


def _yards(
    raw: Mapping, lot: Polygon
) -> tuple[tuple[Yard, ...] | LayerUnavailable, tuple[YardNotRequired, ...]]:
    base = "/geometry/yards"
    if raw["status"] == "not_available":
        return _unavailable("yards", raw, base), ()
    yards: list[Yard] = []
    not_required: list[YardNotRequired] = []
    for i, entry in enumerate(raw["entries"]):
        location = f"{base}/entries/{i}"
        if entry["status"] == "not_required":
            not_required.append(YardNotRequired(
                entry["kind"], _text(entry["reason"], f"{location}/reason"), location))
            continue
        outline = _polygon(entry["outline"], f"{location}/outline")
        _check_within_lot(outline, lot, "yard_outside_lot")
        depth = _finite(entry["depth_ft"], f"{location}/depth_ft")
        yards.append(Yard(entry["kind"], depth, outline, location))
    return tuple(yards), tuple(not_required)


def _setback_lines(raw: Mapping, lot: Polygon) -> tuple[SetbackLine, ...] | LayerUnavailable:
    base = "/geometry/setback_lines_per_level"
    if raw["status"] == "not_available":
        return _unavailable("setback_lines", raw, base)
    result: list[SetbackLine] = []
    for i, entry in enumerate(raw["entries"]):
        location = f"{base}/entries/{i}"
        lines = []
        for j, line in enumerate(entry["lines"]):
            points = tuple(_point(p, f"{location}/lines/{j}/{k}") for k, p in enumerate(line))
            if all(geo.edge_length(points[0], p) <= geo.BOUNDARY_TOL_FT for p in points[1:]):
                raise DrawingInputError("setback_line_degenerate", "setback line has no length",
                                        location=f"{location}/lines/{j}")
            if any(geo.point_location(p, lot.exterior) == "outside" for p in points):
                raise DrawingInputError("setback_line_outside_lot",
                                        "setback line leaves the lot outline",
                                        location=f"{location}/lines/{j}")
            lines.append(points)
        result.append(SetbackLine(entry["floor"], tuple(lines), location))
    return tuple(result)


def _floor_plates(raw: Mapping, lot: Polygon) -> tuple[FloorPlate, ...] | LayerUnavailable:
    base = "/geometry/floor_plates"
    if raw["status"] == "not_available":
        return _unavailable("floor_plates", raw, base)
    if len(raw["entries"]) > MAX_FLOOR_PLATES:
        raise DrawingInputError("too_many_floor_plates", f"more than {MAX_FLOOR_PLATES}",
                                location=base)
    plates: list[FloorPlate] = []
    for i, entry in enumerate(raw["entries"]):
        location = f"{base}/entries/{i}"
        outline = _polygon(entry["outline"], f"{location}/outline")
        _check_within_lot(outline, lot, "plate_outside_lot")
        gross = _finite(entry["gross_sf"], f"{location}/gross_sf")
        plates.append(FloorPlate(entry["floor"], entry["use"], gross, outline, location))
    return tuple(plates)


def _row(raw: Mapping, location: str) -> FloorRow:
    return FloorRow(
        floor=raw["floor"],
        label=_text(raw["floor_label"], f"{location}/floor_label"),
        gross_sf=_finite(raw["gross_sf"], f"{location}/gross_sf"),
        height_ft=_finite(raw["height_ft"], f"{location}/height_ft"),
        use=raw["use"],
        source=location,
    )
