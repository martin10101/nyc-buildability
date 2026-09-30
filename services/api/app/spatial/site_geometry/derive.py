"""Single-lot site geometry: the pure entry point (queue item B-03, plan M1-13 and §4).

From one tax-lot outline in EPSG:2263 feet, the City Map street center lines around it and
(optionally) the city-recorded lot dimensions, derive: lot area from the outline and its
difference from the recorded area; frontage per street along the outline's outside edges;
geometric lot type (corner / interior / through / unknown); lot depth where definable.
Outline-derived values are labeled "Approximate — tax map", recorded values "City records",
and anything that cannot be stated is "Unknown — enter" with the reason.

Pure and deterministic: no I/O, no flags, no callers yet (a later Lane C task wires it).
"""

from __future__ import annotations

from .adjacency import classify_edges
from .area import area_check, city_record_values, outline_area
from .frontage import build_frontages
from .inputs import CityRecordLot, LotOutline, StreetData
from .labels import LABEL_UNKNOWN, SourcedValue, tax_map_value, unknown_value
from .lot_type import BASIS as LOT_TYPE_BASIS
from .lot_type import classify_lot_type
from .outline import prepare_outline
from .parameters import DEPTH_AGREEMENT_FT, METHOD_VERSION, parameters_snapshot
from .results import (
    FRONTAGE_CONFIRMED,
    LOT_TYPE_CORNER,
    LOT_TYPE_INTERIOR,
    LOT_TYPE_THROUGH,
    LOT_TYPE_UNKNOWN,
    STATUS_COMPLETE,
    STATUS_PARTIAL,
    STATUS_REFUSED,
    LotType,
    SiteGeometry,
    StreetFrontage,
)
from .street_data import check_street_data

__all__ = ["derive_site_geometry", "refused_site_geometry"]

_APPROXIMATE_NOTE = (
    "Values measured from the tax-map outline are approximate; a survey, once entered, "
    "replaces them."
)


def _provenance(lot, streets, records) -> dict[str, object]:
    return {
        "method_version": METHOD_VERSION,
        "lot_outline": {"source": lot.source, **dict(lot.provenance)} if lot else None,
        "streets": {"source": streets.source, **dict(streets.provenance)} if streets else None,
        "city_records": (
            {"source": records.source, **dict(records.provenance)} if records else None
        ),
    }


def refused_site_geometry(
    reason: str,
    city_records: CityRecordLot | None = None,
    *,
    lot: LotOutline | None = None,
    streets: StreetData | None = None,
) -> SiteGeometry:
    """Nothing measurable: every outline value is unknown with ``reason``."""
    missing = unknown_value("ft", reason)
    return SiteGeometry(
        status=STATUS_REFUSED,
        refusal_reason=reason,
        lot_area=unknown_value("sq ft", reason),
        city_records=city_record_values(city_records),
        area_check=None,
        frontages=(),
        lot_type=LotType(LOT_TYPE_UNKNOWN, LABEL_UNKNOWN, LOT_TYPE_BASIS, reason, ()),
        lot_depth=missing,
        edges=(),
        street_crossings=(),
        notes=(),
        parameters=parameters_snapshot(),
        provenance=_provenance(lot, streets, city_records),
    )


def _lot_depth(lot_type: LotType, frontages: tuple[StreetFrontage, ...]) -> SourcedValue:
    means = {f.street_key: f.depth.mean for f in frontages if f.depth is not None}
    if lot_type.kind == LOT_TYPE_UNKNOWN:
        return unknown_value("ft", "The lot type is unknown, so no single depth is given.")
    if lot_type.kind == LOT_TYPE_CORNER:
        return unknown_value(
            "ft",
            "On a corner lot the depth depends on which street is taken as the front; the "
            "depth from each street is given with its frontage.",
        )
    depths = [means.get(key) for key in lot_type.streets]
    if any(depth is None or depth.value is None for depth in depths):
        return unknown_value("ft", "The depth could not be measured from the frontage.")
    if lot_type.kind == LOT_TYPE_INTERIOR:
        return depths[0]
    first, second = (depth.value for depth in depths)
    if abs(first - second) > DEPTH_AGREEMENT_FT:
        return unknown_value(
            "ft",
            f"Measured from each street the depth differs ({first:.2f} ft vs "
            f"{second:.2f} ft), so no single depth is given.",
        )
    basis = "Average of the depths measured back from both street frontages"
    return tax_map_value((first + second) / 2.0, "ft", basis)


def _records_note(lot_type: LotType, records) -> str | None:
    known = [(name, value.value) for name, value in
             (("frontage", records.lot_front), ("depth", records.lot_depth)) if value.known]
    if lot_type.kind not in (LOT_TYPE_CORNER, LOT_TYPE_THROUGH) or not known:
        return None
    listed = " and ".join(f"one {name} ({value:.2f} ft)" for name, value in known)
    return (
        f"The city records give {listed} without naming a street; they are shown as "
        "recorded and are not matched to a street here."
    )


def _status(lot_type, frontages, lot_depth) -> str:
    if lot_type.kind == LOT_TYPE_UNKNOWN:
        return STATUS_PARTIAL
    if any(f.status != FRONTAGE_CONFIRMED for f in frontages):
        return STATUS_PARTIAL
    if lot_type.kind == LOT_TYPE_CORNER:
        depths_known = all(f.depth is not None and f.depth.mean.known for f in frontages)
        return STATUS_COMPLETE if depths_known else STATUS_PARTIAL
    return STATUS_COMPLETE if lot_depth.known else STATUS_PARTIAL


def derive_site_geometry(
    lot: LotOutline,
    streets: StreetData | None,
    city_records: CityRecordLot | None = None,
) -> SiteGeometry:
    """Derive the single-lot site facts. Never raises on bad data: it refuses instead."""
    prepared, refusal = prepare_outline(lot)
    if prepared is None:
        return refused_site_geometry(refusal or "The lot outline cannot be used.",
                                     city_records, lot=lot, streets=streets)
    records = city_record_values(city_records)
    area = outline_area(prepared.polygon.area, lot.source)
    street_check = check_street_data(streets, prepared)
    findings = classify_edges(prepared, street_check.centerlines) if street_check.usable else ()
    frontages = build_frontages(findings, prepared, street_check.centerlines,
                                street_check.incomplete, street_check.crossing_keys, lot.source)
    lot_type = classify_lot_type(findings, prepared, list(street_check.blockers))
    lot_depth = _lot_depth(lot_type, frontages)
    checked_area = area_check(area, records.lot_area)
    notes = [_APPROXIMATE_NOTE]
    if checked_area is not None:
        notes.append(checked_area.statement)
    records_note = _records_note(lot_type, records)
    if records_note:
        notes.append(records_note)
    return SiteGeometry(
        status=_status(lot_type, frontages, lot_depth),
        refusal_reason=None,
        lot_area=area,
        city_records=records,
        area_check=checked_area,
        frontages=frontages,
        lot_type=lot_type,
        lot_depth=lot_depth,
        edges=findings,
        street_crossings=street_check.crossing_keys,
        notes=tuple(notes),
        parameters=parameters_snapshot(),
        provenance=_provenance(lot, streets, city_records),
    )
