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
        "streets": [],
        "yards": yards,
        "setback_lines_per_level": setback_lines,
        "envelope": envelope_layer,
        "floor_plates": floor_plates,
    }
