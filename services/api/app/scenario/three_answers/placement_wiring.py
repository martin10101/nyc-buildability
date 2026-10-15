"""The illustrative placement and area-allocation wiring (task M5-T172, round 2 / S12).

This module holds the thin wiring that attaches the contract-1.5.0 illustrative placement and the
area allocation to an already-assembled three-way document. It was EXTRACTED verbatim from
``three_way_document.py`` (round 2) so that assembly module stays under the 750-SLOC justification
line; the behaviour and the emitted document are byte-identical. ``three_way_document`` imports
these names and keeps :class:`PlacementInputs` importable at its old path.

It is a thin layer only: the arithmetic lives in the Part-A modules (``build_placement`` and
``build_area_allocation`` in ``placement.py`` / ``area_allocation.py``) and the footprint geometry
in ``geometry.place_building_on_geometry``. The whole feature is OPT-IN - threaded only when the
engine bridge supplies the four lot measures, exactly like the rear-yard and envelope analyses - so
a document emitted without placement inputs is byte-identical to the 1.3.0/1.4.0 emit.

The contract version string a placed/allocated document declares is passed in by the caller
(``contract_version``), keeping the single source of truth in ``three_way_document`` and avoiding a
circular import back into the assembly module that imports this one.
"""

from __future__ import annotations

from dataclasses import dataclass

from .area_allocation import build_area_allocation
from .geometry import footprint_drawable, place_building_on_geometry
from .placement import build_placement

__all__ = [
    "PlacementInputs",
    "_apply_area_allocation",
    "_apply_placement",
    "_placement_applied",
    "_placement_drawn",
]


@dataclass(frozen=True)
class PlacementInputs:
    """The lot measures an illustrative placement rests on, each on its own basis (M5-T172): the
    printed-tax-map frontage/depth drive the footprint; the city-map (GIS) frontage/depth are a
    conflict check only, never mixed in. ``frontage_street_name`` is the street the building sits
    along. The engine bridge reads each on its own basis (the tax pair from PLUTO, the GIS frontage
    from the prepared outline edge, the GIS depth from the lot-reach measure); absent -> no
    placement or allocation and the document is byte-identical, like the rear-yard/envelope ones."""

    tax_frontage_ft: float | None
    tax_depth_ft: float | None
    gis_frontage_ft: float | None
    gis_depth_ft: float | None
    frontage_street_name: str


# ---------------------------------------------------------------------------
# the illustrative placement and area allocation (contract 1.5.0 additive; task M5-T172)
# ---------------------------------------------------------------------------
def _placement_applied(placement_inputs: PlacementInputs | None) -> bool:
    """Whether a placement will be PLACED on the first alternative (so first_option_results drops
    the 'Where the plan sits on the lot' not-checked line and pages agree). True only when the
    caller threaded the placement inputs AND all four lot measures are present - a missing measure
    holds the placement back (withheld), so the line stays. Byte-identical when None."""
    if placement_inputs is None:
        return False
    return all(
        value is not None
        for value in (
            placement_inputs.tax_frontage_ft,
            placement_inputs.tax_depth_ft,
            placement_inputs.gis_frontage_ft,
            placement_inputs.gis_depth_ft,
        )
    )


def _placement_drawn(geometry: dict | None, placement_inputs: PlacementInputs | None) -> bool:
    """The ONE placed-AND-drawn predicate the page-5 'Where the plan sits on the lot'
    not-checked line, the area-allocation ``fitted`` flag and the scenario sheet's not-placed
    sentence all follow (M5-T172 S15) - never the presence of the four lot measures alone. True
    only when the four measures are present (so :func:`build_placement` places the building) AND
    the geometry supports the corner footprint (:func:`footprint_drawable`, the same corner test
    :func:`place_building_on_geometry` applies, so geometry.floor_plates becomes available). A
    single-frontage lot carries the four measures but has no corner, so the footprint cannot be
    drawn: the building is worked out but not placed on the plan, the line stays and ``fitted`` is
    False. Byte-identical on the benchmark corner lot (both this and the drawn outcome are True)."""
    if not _placement_applied(placement_inputs) or not isinstance(geometry, dict):
        return False
    return footprint_drawable(geometry, placement_inputs.frontage_street_name)


def _floor_plates_drawn(doc: dict) -> bool:
    """True when the engine actually DREW the floor plates on this document (geometry.floor_plates
    is available) - the placed-and-drawn fact read straight from the emitted document, the same one
    the scenario sheet's not-placed sentence reads (readers.building_not_placed)."""
    geometry = doc.get("geometry")
    plates = geometry.get("floor_plates") if isinstance(geometry, dict) else None
    return isinstance(plates, dict) and plates.get("status") == "available"


def _apply_placement(
    doc: dict, placement_inputs: PlacementInputs, *, contract_version: str
) -> None:
    """Place the FIRST building alternative on the lot (M5-T172): build_placement (Part A) makes the
    placement; when placed, geometry.py draws the plates and returns the floor-by-floor table they
    pair with, so the not-placed sentence clears and the kit draws plates. 1.5.0 is declared."""
    alternatives = doc.get("building_alternatives")
    if not alternatives:
        return
    first = alternatives[0]
    zfa = first.get("total_floor_area_sqft")
    storeys = first.get("storey_count")
    placement = build_placement(
        placed=True,
        zoning_floor_area_sqft=zfa,
        storeys=storeys,
        frontage_ft=placement_inputs.tax_frontage_ft,
        lot_depth_ft=placement_inputs.tax_depth_ft,
        gis_frontage_ft=placement_inputs.gis_frontage_ft,
        gis_depth_ft=placement_inputs.gis_depth_ft,
    )
    first["placement"] = placement
    floor_to_floor = _placed_floor_to_floor(first)
    geometry = doc.get("geometry")
    if (
        placement.get("status") == "placed" and isinstance(zfa, (int, float)) and storeys
        and floor_to_floor is not None
        and isinstance(geometry, dict) and geometry.get("status") == "available"
    ):
        rows = place_building_on_geometry(
            geometry, frontage_street_name=placement_inputs.frontage_street_name,
            plate_gross_sqft=zfa / storeys, storeys=storeys, floor_to_floor_ft=floor_to_floor,
        )
        if rows is not None:
            doc["floor_by_floor"] = rows  # the plates and the table are set together (check C-4)
    doc["contract_version"] = contract_version


def _placed_floor_to_floor(alternative: dict) -> float | None:
    """The alternative's floor-to-floor height, read from its own floor schedule (never typed)."""
    schedule = alternative.get("floor_schedule")
    if isinstance(schedule, list) and schedule and isinstance(schedule[0], dict):
        value = schedule[0].get("floor_to_floor_ft")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def _apply_area_allocation(doc: dict, *, contract_version: str) -> None:
    """Split every alternative's residential floor area at the one stated share (M5-T172): emitted
    for every alternative with a floor area, placed or not; fitted is True only when the building
    is placed AND its footprint was actually drawn (S15), so a single-frontage lot whose plates
    could not be drawn is emitted but NOT fitted. ``_floor_plates_drawn`` reads the actual outcome
    from the document (the same fact the not-placed sentence reads), so the fitted flag, the page-5
    line and the sentence all follow one predicate. The Part-A module carries the arithmetic; the
    way-layer rule enforces the fitted-only-when-placed cross-key check."""
    drawn = _floor_plates_drawn(doc)
    for alternative in doc.get("building_alternatives") or []:
        if not isinstance(alternative, dict):
            continue
        placement = alternative.get("placement")
        status = placement.get("status") if isinstance(placement, dict) else None
        allocation = build_area_allocation(
            residential_floor_area_sqft=alternative.get("total_floor_area_sqft"),
            placement_status=status if drawn else None,
        )
        if allocation is not None:
            alternative["area_allocation"] = allocation
            doc["contract_version"] = contract_version
