"""Multi-lot site math: the pure entry point (queue item B-07; plan M2-05, §3 step 2, §4).

From the lot choice and the lots the architect selects (all by default):

1. the same-block and touching check, with the reason when the combination is not offered;
2. the combined outline, with the lot lines the selected lots share removed;
3. the B-03 site geometry of that outline: frontage only along the streets on its outside,
   lot type and depth from the combined outline, and its area against the sum of the
   recorded lot areas ("Combined area is the sum of the lot areas, checked against the
   combined outline", plan §4);
4. optionally the B-04 street width of each outside frontage;
5. each lot's existing building (B-05), carried per lot, never added up or subtracted;
6. the zoning-lot status, always "Check needed": the app does not verify the zoning lot.

Selecting one lot gives exactly B-03's single-lot result for that lot. This step computes
geometry only: no floor area, FAR or capacity. Pure and deterministic, no I/O; reached in
the product only through ``gate.py`` (Lane B flag, off by default).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import replace

from app.spatial.frontage_street_width import MappedStreetSegment
from app.spatial.site_geometry import (
    CityRecordLot,
    CityRecordValues,
    SiteGeometry,
    SourcedValue,
    StreetData,
    derive_site_geometry,
    refused_site_geometry,
)
from app.spatial.site_geometry.area import city_record_values
from app.spatial.site_geometry.labels import city_records_value, unknown_value
from app.spatial.site_geometry.outline import prepare_outline

from .combination import check_combination, lots_text
from .combined_outline import build_combined_outline
from .existing_buildings import PER_LOT_NOTE, attach_existing_buildings
from .inputs import SiteLot
from .parameters import MAX_SELECTED_LOTS, METHOD_VERSION, parameters_snapshot
from .results import (
    COMBINATION_NOT_OFFERED,
    SELECTION_ALL,
    SELECTION_STATEMENT,
    SELECTION_SUBSET,
    CombinedOutline,
    LotChoice,
    MultiLotSite,
)
from .street_widths import combined_street_widths
from .zoning_lot import zoning_lot_status

__all__ = ["LotSelectionError", "derive_multi_lot_site"]

_COMBINED_RECORD = (
    "The city records give one {field} per tax lot, not for lots taken together; the "
    "combined site's {field} is measured from the combined outline."
)


class LotSelectionError(ValueError):
    """The selection is not a non-empty set of lots from the lot choice."""


def _select(choice: LotChoice, selected: Sequence[str] | None):
    if not choice.entries:
        raise LotSelectionError("the lot choice lists no tax lots")
    if selected is None:
        return SELECTION_ALL, list(choice.entries)
    picked = list(selected)
    if not picked:
        raise LotSelectionError("select at least one lot")
    if len(set(picked)) != len(picked):
        raise LotSelectionError(f"a lot is selected twice: {picked}")
    unknown = [bbl for bbl in picked if bbl not in choice.bbls]
    if unknown:
        raise LotSelectionError(f"not in this property's lot choice: {unknown}")
    entries = [entry for entry in choice.entries if entry.bbl in picked]
    mode = SELECTION_ALL if len(entries) == len(choice.entries) else SELECTION_SUBSET
    return mode, entries


def _bounded(mode: str, entries: list) -> tuple[str, list]:
    if len(entries) > MAX_SELECTED_LOTS:
        raise LotSelectionError(f"{len(entries)} lots selected; at most {MAX_SELECTED_LOTS} "
                                "are combined")
    return mode, entries


def _lot_area_sum(lots: Sequence[SiteLot]) -> SourcedValue:
    values = [city_record_values(lot.city_records).lot_area for lot in lots]
    missing = [lot.bbl for lot, value in zip(lots, values, strict=True) if not value.known]
    if missing:
        return unknown_value("sq ft", f"The city records have no lot area for "
                                      f"{lots_text(missing)}, so the recorded areas cannot be "
                                      "added up.")
    if len(lots) == 1:
        return values[0]
    basis = "Sum of the recorded lot areas: " + " + ".join(
        f"{lots_text([lot.bbl])} {value.value:,.2f} sq ft ({value.basis})"
        for lot, value in zip(lots, values, strict=True))
    return city_records_value(sum(value.value for value in values), "sq ft", basis)


def _combined_geometry(outline, streets, lots, area_sum: SourcedValue) -> SiteGeometry:
    records = CityRecordLot(area_sum.value, None, None, "the selected lots' city records",
                            {"lots": {lot.bbl: dict(lot.city_records.provenance)
                                      if lot.city_records else None for lot in lots}})
    geometry = derive_site_geometry(outline, streets, records)
    combined = CityRecordValues(
        area_sum,
        unknown_value("ft", _COMBINED_RECORD.format(field="frontage")),
        unknown_value("ft", _COMBINED_RECORD.format(field="depth")),
    )
    return replace(geometry, city_records=combined)


def _single(lot: SiteLot, streets):
    if lot.outline is None:
        return None, refused_site_geometry(lot.outline_refusal, lot.city_records,
                                           streets=streets)
    prepared, _ = prepare_outline(lot.outline)
    outline = None if prepared is None else CombinedOutline(
        (lot.bbl,), tuple(lot.outline.exterior), lot.outline.source, (),
        round(prepared.polygon.area, 2), "One lot is selected; its own outline is used.")
    return outline, derive_site_geometry(lot.outline, streets, lot.city_records)


def derive_multi_lot_site(
    choice: LotChoice,
    selected: Sequence[str] | None = None,
    streets: StreetData | None = None,
    *,
    street_segments: Iterable[MappedStreetSegment] | None = None,
    recorded_zoning_lot_documents: Sequence[Mapping[str, object]] = (),
) -> MultiLotSite:
    """Site facts for the selected lots (all lots when ``selected`` is None).

    ``streets`` must cover the selected lots (B-03 checks the envelope). ``street_segments``
    (the same DCM pages, as B-04 segments) adds the street width of each frontage.
    Raises :class:`LotSelectionError` for an empty, repeated, unknown or oversized selection.
    """
    mode, entries = _bounded(*_select(choice, selected))
    lots = [entry.lot for entry in entries]
    area_sum = _lot_area_sum(lots)
    check = check_combination(lots)
    notes: list[str] = []
    outline = geometry = None
    if len(lots) == 1:
        outline, geometry = _single(lots[0], streets)
    elif check.combination.status == COMBINATION_NOT_OFFERED:
        notes.append(check.combination.reason)
    else:
        outline, measured, refusal = build_combined_outline(check, lots)
        if measured is None:
            notes.append(refusal)
            geometry = refused_site_geometry(refusal, streets=streets)
        else:
            notes.append(outline.statement)
            geometry = _combined_geometry(measured, streets, lots, area_sum)
        if area_sum.known:
            notes.append(f"Combined area from the city records: {area_sum.basis}.")
    widths = None
    if geometry is not None and street_segments is not None:
        widths = combined_street_widths(geometry, lots, street_segments)
    notes.append(PER_LOT_NOTE)
    return MultiLotSite(
        selection_mode=mode,
        selected_bbls=tuple(lot.bbl for lot in lots),
        statement=SELECTION_STATEMENT,
        lots=tuple(entries),
        combination=check.combination,
        outline=outline,
        geometry=geometry,
        lot_area_sum=area_sum,
        street_widths=widths,
        existing_buildings=attach_existing_buildings(lots),
        zoning_lot=zoning_lot_status(lots, recorded_documents=recorded_zoning_lot_documents),
        notes=tuple(notes),
        parameters=parameters_snapshot(),
        provenance={
            "method_version": METHOD_VERSION,
            "site_geometry_method_version": (geometry.parameters.get("method_version")
                                             if geometry else None),
            "lots": {lot.bbl: dict(lot.provenance) for lot in lots},
            "condo_base_lots": {e.bbl: e.condo.billing_bbl for e in entries if e.condo},
        },
    )

