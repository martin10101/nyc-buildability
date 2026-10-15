"""The ONE geometry block, in feet (task A-04; plan section 5c). Every drawing, the PDF and
the DXF read from this block; nothing is typed into them.

The lot outline is the MEASURED tax-map parcel polygon (:attr:`ThreeAnswerInputs.lot_outline`,
threaded from the prepared Lane B outline in EPSG:2263 US survey feet), translated to the
local-feet drawing plane: its minimum x and y are subtracted so the origin sits at the lot's
min corner, the orientation is kept and grid north stays up (the local-feet axes are parallel
to the EPSG:2263 grid). The outline is NEVER a rectangle sized to the recorded lot area, and the
outline is never stretched to match a recorded area (owner presentation contract section 6,
rows R841/R846/R896): local drawing feet are labelled ``local_feet`` with the tax-map source,
never ``EPSG:2263``. No placement on the lot is worked in this slice, so no layer that would
scale the lot shape into a footprint or an envelope is drawn (ruling W5 of wave 19): the
permitted envelope and the floor plates are honestly ``not_available``; the three-way transform
restates each withheld layer from its own result. The rear-yard waiver (shown as 'not required'
so no drawing invents a yard) and an honest not_available for the setback lines that ZR 23-433
would drive (not encoded in this slice) are kept.

When no measured outline is threaded (the direct engine path only - never a shown document; a
shown document whose outline is not available is a whole ``not_available`` geometry block, set by
the three-way transform so 'nothing is drawn and the geometry says why', S2/R896), the block
keeps a LOCAL-FEET axis-aligned fallback sized to the recorded lot area, used solely for the
internal option-comparison extent; it is never rendered into a site plan, PDF or DXF.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from .answers import EnvelopeResult, not_available
from .building_option import BuildingOptionComputation
from .inputs import ThreeAnswerInputs

_RESIDENTIAL = "residential"

# Ruling W5 (wave 19): no placement on the lot is worked in this slice, so no layer that scales
# the lot shape into a footprint or an envelope is drawn with the measured outline.
_ENVELOPE_NO_PLACEMENT = (
    "The permitted-envelope solid is not drawn: no placement on the lot is worked for any "
    "building."
)
_FLOOR_PLATES_NO_PLACEMENT = (
    "No floor plate is drawn: no placement on the lot is worked for any building."
)

# A corner of one street line this close to a corner of another (local feet) is the shared corner
# where the two frontages meet; the footprint is anchored there (M5-T172).
_CORNER_TOL_FT = 0.05


def _footprint_outline(
    frontage_line: Sequence[Sequence[float]],
    side_line: Sequence[Sequence[float]] | None,
    plate_gross_sqft: float,
) -> list[list[float]] | None:
    """The illustrative footprint ring (local feet), as wide as the full frontage and as deep as
    the plate needs, anchored at the corner where the frontage and the side street meet and run
    back along the side street (so both drawn edges are parallel to a street line). Every vertex is
    DERIVED from the frontage and side lines the site plan already carries - none is typed in. The
    depth is the plate divided by the frontage length, so the ring's area reconciles with the plate;
    returns None when the two lines share no corner or the frontage has no length."""
    if side_line is None or len(frontage_line) < 2 or len(side_line) < 2:
        return None
    f_ends = (frontage_line[0], frontage_line[-1])
    s_ends = (side_line[0], side_line[-1])
    corner = far = side_far = None
    for fe in f_ends:
        for se in s_ends:
            if math.dist(fe, se) <= _CORNER_TOL_FT:
                corner = fe
                far = f_ends[1] if fe is f_ends[0] else f_ends[0]
                side_far = s_ends[1] if se is s_ends[0] else s_ends[0]
    if corner is None or far is None or side_far is None:
        return None
    frontage_len = math.dist(corner, far)
    side_len = math.dist(corner, side_far)
    if frontage_len <= 0 or side_len <= 0:
        return None
    depth = plate_gross_sqft / frontage_len
    sx = (side_far[0] - corner[0]) / side_len
    sy = (side_far[1] - corner[1]) / side_len
    c = [float(corner[0]), float(corner[1])]
    f = [float(far[0]), float(far[1])]
    f_back = [f[0] + sx * depth, f[1] + sy * depth]
    c_back = [c[0] + sx * depth, c[1] + sy * depth]
    return [c, f, f_back, c_back, c]


def build_placed_floor_plates(
    *,
    frontage_line: Sequence[Sequence[float]],
    side_line: Sequence[Sequence[float]] | None,
    plate_gross_sqft: float,
    storeys: int,
) -> dict | None:
    """The ``floor_plates`` geometry layer once a building is placed (task M5-T172): one plate per
    storey, each the same illustrative footprint (:func:`_footprint_outline`) placed in the corner
    on the full frontage within the drawn lot outline, carrying the plate's gross area and the
    residential use. The drawn ring's area reconciles with the plate within the readers' half a
    square foot (check C-4). Returns None when the footprint cannot be positioned, so the caller
    keeps the honest not-available layer rather than invent a shape."""
    if storeys <= 0:
        return None
    ring = _footprint_outline(frontage_line, side_line, plate_gross_sqft)
    if ring is None:
        return None
    outline = [ring]
    return {
        "status": "available",
        "entries": [
            {
                "floor": storey,
                "outline": outline,
                "gross_sf": plate_gross_sqft,
                "use": _RESIDENTIAL,
            }
            for storey in range(1, storeys + 1)
        ],
    }


def _frontage_lines(geometry: dict, frontage_street_name: str) -> tuple[list | None, list | None]:
    """The placement frontage line (the street the building sits along) and ONE adjacent street
    line (the corner) from the drawn geometry's streets. None when the frontage street is not
    drawn, so the caller keeps the honest not-available layer."""
    streets = geometry.get("streets") or []
    frontage_line = side_line = None
    for street in streets:
        if isinstance(street, dict) and street.get("street") == frontage_street_name:
            frontage_line = street.get("frontage_line")
    for street in streets:
        if (
            isinstance(street, dict)
            and street.get("street") != frontage_street_name
            and street.get("frontage_line")
        ):
            side_line = street.get("frontage_line")
            break
    return frontage_line, side_line


def place_building_on_geometry(
    geometry: dict,
    *,
    frontage_street_name: str,
    plate_gross_sqft: float,
    storeys: int,
    floor_to_floor_ft: float,
) -> list[dict] | None:
    """Draw the placed building into an AVAILABLE geometry block (task M5-T172): set
    ``geometry.floor_plates`` to the footprint on the placement frontage (:func:`build_placed_
    floor_plates`) and return the floor-by-floor rows the drawings pair with those plates (check
    C-4), one per storey. The plate rows and the table are produced together, so they never
    disagree. Returns None when the footprint cannot be positioned (the geometry is left unchanged
    and the caller keeps the honest not-available layer); the storey gross area carries no
    building-code deduction in this phase (zoning_floor_area_sf = gross_sf)."""
    frontage_line, side_line = _frontage_lines(geometry, frontage_street_name)
    if frontage_line is None:
        return None
    plates = build_placed_floor_plates(
        frontage_line=frontage_line, side_line=side_line,
        plate_gross_sqft=plate_gross_sqft, storeys=storeys,
    )
    if plates is None:
        return None
    geometry["floor_plates"] = plates
    return [
        {
            "floor": storey,
            "floor_label": f"Floor {storey}",
            "gross_sf": plate_gross_sqft,
            "deductions_sf": 0.0,
            "zoning_floor_area_sf": plate_gross_sqft,
            "height_ft": floor_to_floor_ft,
            "use": _RESIDENTIAL,
        }
        for storey in range(1, storeys + 1)
    ]


def footprint_drawable(geometry: dict, frontage_street_name: str) -> bool:
    """Whether a placed footprint CAN be drawn into this geometry (task M5-T172 S15): the
    frontage street and an adjacent street share a corner, so :func:`place_building_on_geometry`
    would set an AVAILABLE ``floor_plates`` layer. False for a single-frontage (non-corner) lot,
    where the four lot measures may all be present but no corner exists - the building is worked
    out but not placed on the plan. The result does not depend on the plate size (the footprint
    depth scales to the frontage), so a nominal positive plate reuses the one ring builder and the
    same corner test place_building_on_geometry applies; it is the actual-outcome predicate, never
    a guess."""
    if not isinstance(geometry, dict) or geometry.get("status") != "available":
        return False
    frontage_line, side_line = _frontage_lines(geometry, frontage_street_name)
    if frontage_line is None:
        return False
    return _footprint_outline(frontage_line, side_line, plate_gross_sqft=1.0) is not None


def _rectangle(width: float, depth: float) -> list[list[float]]:
    """A closed axis-aligned ring anchored at the origin (a lot corner), feet."""
    return [[0.0, 0.0], [width, 0.0], [width, depth], [0.0, depth], [0.0, 0.0]]


def _lot_dimensions(inputs: ThreeAnswerInputs) -> tuple[float, float]:
    """Width x depth (feet) of a rectangle whose area equals the recorded lot area, using the
    recorded frontage/depth aspect when available (else square). Internal fallback extent only -
    never the shown lot outline (the shown outline is the measured tax-map polygon)."""
    area = inputs.lot_area_sq_ft
    if inputs.lot_front_ft and inputs.lot_depth_ft and inputs.lot_depth_ft > 0:
        aspect = inputs.lot_front_ft / inputs.lot_depth_ft
    else:
        aspect = 1.0
    depth = math.sqrt(area / aspect)
    width = aspect * depth
    return width, depth


def _build_streets(inputs: ThreeAnswerInputs) -> list[dict]:
    """The street frontages the spatial engine already matched to the lot outline, each carried as
    ``{street, frontage_line, street_width_fact_id}`` for the site plan (results-v1
    ``geometry.streets`` item shape; no schema change). The frontage line is the confirmed
    frontage's own lot-outline edges, translated to the SAME local-feet plane as the lot outline
    (its minimum x and y subtracted), so every point lies exactly on the drawn outline.

    Streets stays EMPTY - and nothing is invented - on every path that does not carry the
    frontages: the direct engine path (no prepared outline and no site geometry threaded), or a
    threaded geometry whose frontages are not confirmed. The names are the recorded source's own
    street names (``StreetFrontage.street_name``); the engine derives no street-width figure here,
    so ``street_width_fact_id`` is null (the study has none for this path)."""
    geometry = inputs.site_geometry
    prepared = inputs.prepared_outline
    measured = inputs.lot_outline
    if geometry is None or prepared is None or measured is None or len(measured) < 3:
        return []
    from app.spatial.site_geometry.results import FRONTAGE_CONFIRMED

    minx = min(float(x) for x, _ in measured)
    miny = min(float(y) for _, y in measured)
    edges = prepared.edges
    streets: list[dict] = []
    for frontage in geometry.frontages:
        name = frontage.street_name
        if frontage.status != FRONTAGE_CONFIRMED or not name:
            continue
        line: list[list[float]] = []
        for index in frontage.edge_indices:
            if not 0 <= index < len(edges):
                line = []
                break
            edge = edges[index]
            if not line:
                line.append([edge.start[0] - minx, edge.start[1] - miny])
            line.append([edge.end[0] - minx, edge.end[1] - miny])
        if len(line) < 2:
            continue
        streets.append(
            {"street": name, "frontage_line": line, "street_width_fact_id": None}
        )
    return streets


def _local_feet_ring(measured: Sequence[Sequence[float]]) -> list[list[float]]:
    """Translate a MEASURED outline ring (EPSG:2263 US survey feet) to the local-feet drawing
    plane: subtract the minimum x and y so the origin sits at the lot's min corner; keep the
    orientation and grid north (the EPSG:2263 axes are kept, not rotated). The ring is returned
    CLOSED (first point repeated) as plain ``[x, y]`` lists. The translation preserves the area,
    so the drawn outline's area equals the measured outline area."""
    pts = [(float(x), float(y)) for x, y in measured]
    minx = min(x for x, _ in pts)
    miny = min(y for _, y in pts)
    ring = [[x - minx, y - miny] for x, y in pts]
    if ring[0] != ring[-1]:
        ring.append(list(ring[0]))
    return ring


def build_geometry(
    inputs: ThreeAnswerInputs,
    envelope: EnvelopeResult,
    option: BuildingOptionComputation | None,
    measurement: Mapping[str, str],
) -> dict:
    """Assemble the results-v1 geometry block. The lot outline is always present; each
    rule-dependent layer is independently available or not_available with its reason.

    The lot outline is the measured tax-map polygon (``inputs.lot_outline``) translated to local
    feet when it is threaded; no placement is worked, so the footprint-scaled layers (envelope,
    floor plates) are then not drawn (ruling W5). Without a threaded outline a local-feet fallback
    sized to the recorded area is used for the internal option-comparison extent only."""
    measured = inputs.lot_outline
    has_measured_outline = measured is not None and len(measured) >= 3

    if has_measured_outline:
        lot_outline = [_local_feet_ring(measured)]
        # Ruling W5: no placement is worked, so no footprint-scaled solid or floor plate is drawn
        # from the measured lot shape. The three-way transform restates each from its own result.
        envelope_layer: dict = not_available(_ENVELOPE_NO_PLACEMENT, "rule_not_implemented")
        floor_plates: dict = not_available(_FLOOR_PLATES_NO_PLACEMENT, "rule_not_implemented")
    else:
        # Internal fallback extent for the direct engine path (never a shown document). The shown
        # document always carries the measured outline or a whole not_available geometry block.
        width, depth = _lot_dimensions(inputs)
        lot_outline = [_rectangle(width, depth)]

        # Coverage-limited footprint: the lot rectangle scaled so its area equals the plate.
        coverage = envelope.max_lot_coverage_ratio
        if coverage is not None and 0 < coverage <= 1:
            scale = math.sqrt(coverage)
            footprint = [_rectangle(width * scale, depth * scale)]
        else:
            footprint = lot_outline

        # Envelope tier: one prism from grade to the maximum building height over the footprint.
        if envelope.max_building_height_ft is not None and coverage is not None:
            envelope_layer = {
                "status": "available",
                "tiers": [
                    {
                        "bottom_ft": 0.0,
                        "top_ft": envelope.max_building_height_ft,
                        "outline": footprint,
                    }
                ],
            }
        else:
            envelope_layer = not_available(
                "The permitted-envelope geometry needs the height limit and lot coverage.",
                "rule_not_implemented",
            )

        # Floor plates: one per built floor of the building option.
        if option is not None:
            plate_outline = footprint
            floor_plates = {
                "status": "available",
                "entries": [
                    {
                        "floor": row.floor,
                        "outline": plate_outline,
                        "gross_sf": row.gross_sf,
                        "use": _RESIDENTIAL,
                    }
                    for row in option.floor_rows
                ],
            }
        else:
            floor_plates = not_available(
                "Floor plates need the building option.", "missing_input"
            )

    # Rear-yard waiver: show it as 'not required' so no drawing invents a yard.
    if envelope.rear_yard_required is False:
        yards: dict = {
            "status": "available",
            "entries": [
                {
                    "kind": "rear",
                    "status": "not_required",
                    "reason": (
                        "No rear yard is required within 100 ft of the corner (two street "
                        "lines intersecting at 135 degrees or less)."
                    ),
                    "zr_sections": list(envelope.rear_yard_zr_sections or ("ZR 23-344(a)",)),
                }
            ],
        }
    else:
        yards = not_available(
            "The rear-yard requirement for this lot is not resolved.", "eligibility_unresolved"
        )

    setback_lines = not_available(
        "Setback lines need the ZR 23-433 setback depths, not encoded in this slice.",
        "rule_not_implemented",
    )

    return {
        "status": "available",
        "crs": "local_feet",
        "units": "feet",
        "measurement": dict(measurement),
        "lot_outline": lot_outline,
        "streets": _build_streets(inputs),
        "yards": yards,
        "setback_lines_per_level": setback_lines,
        "envelope": envelope_layer,
        "floor_plates": floor_plates,
    }
