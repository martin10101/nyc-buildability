"""The illustrative placement of a worked building on its lot - the pure computation of the
footprint, the footprint outline and the lot-line offsets (contract 1.5.0 $defs.building_placement).

This is the SCENARIO layer and a self-contained module (it mirrors rear_yard_checks.py): it holds
no I/O, no clock and no AI, and it imports NOTHING from three_way_document.py, geometry.py,
first_option_results.py or envelope_constraints.py, so the engine's concurrent geometry work cannot
reach it. It turns a few stated facts - the building's zoning floor area and storeys, the lot
frontage and depth on the printed-tax-map basis, and the city-map (GIS) frontage and depth used only
as a conflict check - into a building_placement dict for one worked alternative.

THREE RULES (result-deciding). (1) No default stands for a fact: a missing zoning floor area,
storey count, frontage or depth holds the placement back (it is returned WITHHELD, with no outline),
and no optional fact is read with a truthiness test (every check is ``is None`` or an explicit value
comparison, so a real 0 is never read as missing). (2) Every vertex of the outline and every offset
is DERIVED by arithmetic from those facts, never a typed-in coordinate (R044); the plate and the
footprint are separate quantities, each on its own recompute, reconciled within the readers' half a
square foot and never forced into one figure. (3) Every text is plain user words: no record id, no
task id, no "reference case", never a statement about which law text is "captured" or "built", and
nothing is called complies, buildable, optimal or feasible. The plate is zoning floor area per
storey; the physical floor plate (gross-up, exclusions, wall thickness) is listed as not checked.

Every number here comes only from the stated facts and the arithmetic below, never from a program
run; the agreement of two independent AI readings is not proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

__all__ = [
    "AREA_MEASURE",
    "GIS_BASIS",
    "ILLUSTRATIVE_LABEL",
    "PLATE_CONVERSION_STATEMENT",
    "PRINTED_TAX_MAP_BASIS",
    "RECONCILE_TOLERANCE_SQFT",
    "PlacementGeometry",
    "build_placement",
    "compute_placement_geometry",
    "plate_area_sqft",
]

# The contract-1.5.0 consts an illustrative placement carries, byte-exact with results.schema.json
# ($defs.illustrative_label, $defs.area_measure, $defs.plate_conversion_statement). A test pins each
# against the schema so a reworded const is caught, never silently drifted.
ILLUSTRATIVE_LABEL = "Illustrative"
AREA_MEASURE = "residential_floor_area"
PLATE_CONVERSION_STATEMENT = (
    "plate = zoning floor area per storey; no gross-up, exclusions or "
    "wall-thickness conversion worked"
)

# The quantity bases (the schema's $defs.quantity_basis enum). The stated placement basis (A1) is
# the printed tax map; the city-map outline (GIS) is a conflict check only, never mixed in.
PRINTED_TAX_MAP_BASIS = "printed_tax_map"
GIS_BASIS = "gis"

# The readers reconcile the footprint figure with the plate within half a square foot and never
# force them into one figure; a wider gap is a defect in the derived geometry, so the builder fails
# closed.
RECONCILE_TOLERANCE_SQFT = 0.5

_NOT_A_DETERMINATION = (
    "This is an illustrative placement, not a design, a dwelling layout or a finding that the "
    "building complies, is buildable or is feasible."
)
_PHYSICAL_PLATE_NOT_CHECKED = "the physical floor plate (gross-up, exclusions, wall thickness)"


def _round2(value: float) -> float:
    """Round half up to two decimals (the reading's round_half_up_2dp), as a float."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _fmt(value: float) -> str:
    """Plain two-decimal feet/percent, trailing zeros trimmed (33.34, 3.12, 100, 0)."""
    return f"{value:.2f}".rstrip("0").rstrip(".") or "0"


def plate_area_sqft(zoning_floor_area_sqft: float | None, storeys: int | None) -> float | None:
    """The plate = the building's zoning floor area divided by its storeys, rounded half up to two
    decimals. A missing zoning floor area or storey count holds the plate back (returns None); a
    non-positive storey count is a bad input and fails closed. The plate is zoning floor area per
    storey, NOT a physical floor plate (no gross-up, exclusions or wall-thickness conversion)."""
    if zoning_floor_area_sqft is None or storeys is None:
        return None
    if storeys <= 0:
        raise ValueError(f"storeys must be positive, got {storeys!r}")
    return _round2(zoning_floor_area_sqft / storeys)


@dataclass(frozen=True)
class PlacementGeometry:
    """The derived geometry behind a placed placement, every figure recomputed from the stated
    facts (never a program run). The printed-tax-map figures drive the footprint and the outline;
    the GIS figures are a conflict check only and are None when no city-map outline was given."""

    plate_sqft: float
    plan_depth_ft: float
    footprint_sqft: float
    tax_back_clearance_ft: float
    tax_rectangle_sqft: float
    footprint_share_pct: float
    outline: list[list[list[float]]]
    outline_area_sqft: float
    gis_plan_depth_ft: float | None = None
    gis_back_clearance_ft: float | None = None
    frontage_conflict_ft: float | None = None


def _shoelace_area(ring: list[list[float]]) -> float:
    """The absolute area of a closed ring by the shoelace formula (the ring's first and last points
    are equal). Used to reconcile the built outline with the plate - the outline area is MEASURED
    from the vertices, not copied from the footprint figure, so a wrong vertex is caught."""
    total = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:], strict=False):
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def compute_placement_geometry(
    *,
    zoning_floor_area_sqft: float | None,
    storeys: int | None,
    frontage_ft: float | None,
    lot_depth_ft: float | None,
    gis_frontage_ft: float | None = None,
    gis_depth_ft: float | None = None,
) -> PlacementGeometry | None:
    """Compute the placed footprint, its outline and its offsets from the stated facts, or return
    None when a fact needed to place it is missing (the placement is then held back / withheld).

    The footprint is a rectangle as wide as the full street frontage and as deep as the floor area
    per storey needs: the plan depth is the plate divided by the frontage; the footprint is that
    rounded depth times the frontage; the clearance to the lot line opposite the frontage is the lot
    depth less the plan depth. Every vertex of the outline is built from the frontage, the depth and
    the lot-line touches (all 0 on this basis), so none is typed in (R044). The GIS frontage and
    depth, when given, yield the conflicting plan depth and back clearance beside the tax-map
    figures - a conflict check only; the two bases are never mixed into one figure and neither is
    chosen."""
    plate = plate_area_sqft(zoning_floor_area_sqft, storeys)
    if plate is None or frontage_ft is None or lot_depth_ft is None:
        return None
    if frontage_ft <= 0:
        raise ValueError(f"frontage must be positive, got {frontage_ft!r}")

    # The plate carried at full precision for the depth division (the rounded 6,716.67 and the full
    # 20,150/3 both give the same two-decimal depth); the footprint then uses the rounded depth.
    plate_full = zoning_floor_area_sqft / storeys  # type: ignore[operator]
    plan_depth = _round2(plate_full / frontage_ft)
    footprint = _round2(plan_depth * frontage_ft)
    tax_back_clearance = _round2(lot_depth_ft - plan_depth)
    tax_rectangle = _round2(frontage_ft * lot_depth_ft)
    footprint_share = _round2(footprint / tax_rectangle * 100.0) if tax_rectangle else 0.0

    # Every vertex is an expression of the derived touches (all 0 on the printed-tax-map basis) and
    # the computed frontage and depth - a rectangle in a local illustration frame whose origin is
    # the corner where the two street lines meet, x along the frontage, y back from the frontage.
    touch = 0.0  # the lot-line touches are 0 ft on this basis (derived)
    ring = [
        [touch, touch],
        [touch + frontage_ft, touch],
        [touch + frontage_ft, touch + plan_depth],
        [touch, touch + plan_depth],
        [touch, touch],
    ]
    outline = [ring]
    outline_area = _round2(_shoelace_area(ring))

    # The outline area is MEASURED from the vertices and must reconcile with the plate within the
    # readers' half a square foot; a wider gap means the geometry is wrong, so fail closed.
    if abs(outline_area - plate) > RECONCILE_TOLERANCE_SQFT:
        raise ValueError(
            f"the footprint outline area {outline_area} does not reconcile with the plate {plate} "
            f"within {RECONCILE_TOLERANCE_SQFT} sq ft"
        )

    gis_plan_depth = gis_back_clearance = frontage_conflict = None
    if gis_frontage_ft is not None and gis_depth_ft is not None:
        if gis_frontage_ft <= 0:
            raise ValueError(f"gis frontage must be positive, got {gis_frontage_ft!r}")
        gis_plan_depth = _round2(plate_full / gis_frontage_ft)
        gis_back_clearance = _round2(gis_depth_ft - gis_plan_depth)
        frontage_conflict = _round2(gis_frontage_ft - frontage_ft)

    return PlacementGeometry(
        plate_sqft=plate,
        plan_depth_ft=plan_depth,
        footprint_sqft=footprint,
        tax_back_clearance_ft=tax_back_clearance,
        tax_rectangle_sqft=tax_rectangle,
        footprint_share_pct=footprint_share,
        outline=outline,
        outline_area_sqft=outline_area,
        gis_plan_depth_ft=gis_plan_depth,
        gis_back_clearance_ft=gis_back_clearance,
        frontage_conflict_ft=frontage_conflict,
    )


def _build_checks(geom: PlacementGeometry, lot_depth_ft: float) -> list[str]:
    return [
        (
            f"On the printed tax map the footprint clears the lot line opposite the frontage by "
            f"{_fmt(geom.tax_back_clearance_ft)} feet (the {_fmt(lot_depth_ft)}-foot tax-map depth "
            f"less the {_fmt(geom.plan_depth_ft)}-foot plan depth), leaving a back strip wider "
            "than the five feet any open area along a side lot line must keep (ZR 23-335(b))."
        ),
        (
            "The footprint stands on the street lines for the full frontage, which the front-yard "
            "rule for these districts permits (ZR 23-322, no front yard required); it touches the "
            "two street lines and the shared side lot line at 0 feet."
        ),
        (
            f"The footprint is about {_fmt(geom.footprint_share_pct)} percent of the "
            f"{_fmt(geom.tax_rectangle_sqft)}-square-foot tax rectangle; the maximum residential "
            "lot coverage is read by portion - 100 percent for the corner portion and 80 percent "
            "for any interior or through portion (ZR 23-362 with the ZR 12-10 corner definition)."
        ),
    ]


def _build_conditions(geom: PlacementGeometry) -> list[dict]:
    """The assumptions the placement rests on, each in plain words with what would settle it. The
    city-map (GIS) conflict is carried here as a contradicted record, naming both bases' figures and
    choosing neither; the zoning lot and the rear yard are unchecked conditions."""
    conditions: list[dict] = []
    if geom.gis_back_clearance_ft is not None and geom.frontage_conflict_ft is not None:
        conditions.append(
            {
                "kind": "contradicted_record",
                "assumption": (
                    "If the printed tax map governs over the city-map outline: the two disagree - "
                    f"the clearance to the back lot line reads {_fmt(geom.tax_back_clearance_ft)} "
                    f"feet on the tax map and {_fmt(geom.gis_back_clearance_ft)} feet on the "
                    f"city-map outline, and the street frontage differs by about "
                    f"{_fmt(geom.frontage_conflict_ft)} feet."
                ),
                "settled_by": "A survey or deed to resolve the conflicting lot outlines.",
            }
        )
    conditions.append(
        {
            "kind": "unchecked_condition",
            "assumption": (
                "If this lot alone is the zoning lot (whether it and the adjoining lot are one "
                "zoning lot is not known)."
            ),
            "settled_by": "Reading the recorded zoning-lot description.",
        }
    )
    conditions.append(
        {
            "kind": "unchecked_condition",
            "assumption": (
                f"If no rear yard constrains the {_fmt(geom.plan_depth_ft)}-foot depth (the "
                "rear-yard rule ZR 23-344 is not resolved for this lot)."
            ),
            "settled_by": (
                "An express measurement basis in the Zoning Resolution and the adjoining lots' "
                "recorded lot-line kinds."
            ),
        }
    )
    return conditions


def _not_checked() -> list[str]:
    return [
        _PHYSICAL_PLATE_NOT_CHECKED,
        "where the walls, rooms, core, stairs and elevators sit",
        "parking, loading and bicycle requirements",
        "the whole-lot coverage as one figure (the recorded, tax-map and city-map areas conflict)",
        "the street wall and any required setback above the base height",
        "a survey or deed to settle the lot dimensions and the zoning lot",
    ]


def build_placement(
    *,
    placed: bool,
    zoning_floor_area_sqft: float | None = None,
    storeys: int | None = None,
    frontage_ft: float | None = None,
    lot_depth_ft: float | None = None,
    gis_frontage_ft: float | None = None,
    gis_depth_ft: float | None = None,
) -> dict:
    """Build a building_placement dict (contract 1.5.0 $defs.building_placement).

    When ``placed`` is True AND every fact needed to place the footprint is present, it returns a
    PLACED placement carrying the derived footprint outline, the method, the printed-tax-map basis,
    the plate's area measure, the fixed conversion statement, the checks, the assumptions it rests
    on and what was not checked. Otherwise - ``placed`` False, or a needed fact missing - it
    returns a WITHHELD placement carrying the same labels and basis but NO outline (the schema's
    withheld branch; additionalProperties false rejects an outline key). Nothing here is a
    determination."""
    geom = None
    if placed:
        geom = compute_placement_geometry(
            zoning_floor_area_sqft=zoning_floor_area_sqft,
            storeys=storeys,
            frontage_ft=frontage_ft,
            lot_depth_ft=lot_depth_ft,
            gis_frontage_ft=gis_frontage_ft,
            gis_depth_ft=gis_depth_ft,
        )

    if geom is None:
        return {
            "status": "withheld",
            "label": ILLUSTRATIVE_LABEL,
            "method": (
                "No illustrative footprint is placed for this building; the placement is not "
                f"shown. {_NOT_A_DETERMINATION}"
            ),
            "basis": PRINTED_TAX_MAP_BASIS,
            "measure": AREA_MEASURE,
            "conversion_statement": PLATE_CONVERSION_STATEMENT,
            "not_checked": [_PHYSICAL_PLATE_NOT_CHECKED],
        }

    return {
        "status": "placed",
        "label": ILLUSTRATIVE_LABEL,
        "outline": geom.outline,
        "method": (
            "The footprint is a rectangle as wide as the full street frontage and as deep as the "
            "floor area per storey needs; it is placed with one wall on the street line for the "
            "full frontage, a corner where the two street lines meet, and one wall along the side "
            f"street. {_NOT_A_DETERMINATION}"
        ),
        "basis": PRINTED_TAX_MAP_BASIS,
        "measure": AREA_MEASURE,
        "conversion_statement": PLATE_CONVERSION_STATEMENT,
        "checks": _build_checks(geom, lot_depth_ft),  # type: ignore[arg-type]
        "conditions": _build_conditions(geom),
        "not_checked": _not_checked(),
    }
