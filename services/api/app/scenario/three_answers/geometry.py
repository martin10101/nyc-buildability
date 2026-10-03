"""The ONE geometry block, in feet (task A-04; plan section 5c). Every drawing, the PDF and
the DXF read from this block; nothing is typed into them.

Slice 1 builds a LOCAL-FEET axis-aligned rectangle for the lot (a stated approximation of
the recorded tax-lot area - the true parcel polygon is Lane B site geometry), the permitted
envelope as one tier extruded to the maximum building height over the coverage-limited
footprint, the building option's floor plates, the rear-yard waiver (shown as 'not required'
so no drawing invents a yard), and an honest not_available for the setback lines that ZR
23-433 would drive (not encoded in this slice).
"""

from __future__ import annotations

import math
from collections.abc import Mapping

from .answers import EnvelopeResult, not_available
from .building_option import BuildingOptionComputation
from .inputs import ThreeAnswerInputs

_RESIDENTIAL = "residential"


def _rectangle(width: float, depth: float) -> list[list[float]]:
    """A closed axis-aligned ring anchored at the origin (a lot corner), feet."""
    return [[0.0, 0.0], [width, 0.0], [width, depth], [0.0, depth], [0.0, 0.0]]


def _lot_dimensions(inputs: ThreeAnswerInputs) -> tuple[float, float]:
    """Width x depth (feet) of a rectangle whose area equals the recorded lot area, using the
    recorded frontage/depth aspect when available (else square)."""
    area = inputs.lot_area_sq_ft
    if inputs.lot_front_ft and inputs.lot_depth_ft and inputs.lot_depth_ft > 0:
        aspect = inputs.lot_front_ft / inputs.lot_depth_ft
    else:
        aspect = 1.0
    depth = math.sqrt(area / aspect)
    width = aspect * depth
    return width, depth


def build_geometry(
    inputs: ThreeAnswerInputs,
    envelope: EnvelopeResult,
    option: BuildingOptionComputation | None,
    measurement: Mapping[str, str],
) -> dict:
    """Assemble the results-v1 geometry block. The lot outline is always present; each
    rule-dependent layer is independently available or not_available with its reason."""
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
        envelope_layer: dict = {
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
        floor_plates: dict = {
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
