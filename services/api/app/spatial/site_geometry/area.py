"""Lot area from the outline, checked against the recorded lot area (B-03, plan §4).

The outline area (rank 3, "Approximate — tax map") and the City records area (rank 2) are
both reported; the difference is stated and nothing is replaced.
"""

from __future__ import annotations

from .inputs import CityRecordLot
from .labels import SourcedValue, city_records_value, tax_map_value, unknown_value
from .results import AreaCheck, CityRecordValues

__all__ = ["area_check", "city_record_values", "outline_area"]


def outline_area(area_sq_ft: float, source: str) -> SourcedValue:
    basis = f"Planar area of the {source} outline in EPSG:2263 (US survey feet)"
    return tax_map_value(area_sq_ft, "sq ft", basis)


def _recorded(value: float | None, unit: str, field: str, source: str) -> SourcedValue:
    if value is None:
        return unknown_value(unit, f"The city records have no {field} for this lot.", source)
    return city_records_value(value, unit, f"{source}, {field}")


def city_record_values(records: CityRecordLot | None) -> CityRecordValues:
    if records is None:
        missing = "No city record was provided."
        return CityRecordValues(
            unknown_value("sq ft", missing), unknown_value("ft", missing),
            unknown_value("ft", missing),
        )
    return CityRecordValues(
        _recorded(records.lot_area_sq_ft, "sq ft", "lot area", records.source),
        _recorded(records.lot_front_ft, "ft", "lot frontage", records.source),
        _recorded(records.lot_depth_ft, "ft", "lot depth", records.source),
    )


def area_check(outline: SourcedValue, recorded: SourcedValue) -> AreaCheck | None:
    """Outline minus recorded area, in square feet and percent of the recorded area."""
    if outline.value is None or recorded.value is None or recorded.value <= 0.0:
        return None
    difference = round(outline.value - recorded.value, 2)
    percent = round(difference / recorded.value * 100.0, 2)
    statement = (
        f"The tax-map outline measures {outline.value:,.2f} sq ft; the city records say "
        f"{recorded.value:,.2f} sq ft ({difference:+,.2f} sq ft, {percent:+.2f} %). "
        "Both are shown; neither replaces the other."
    )
    return AreaCheck(outline.value, recorded.value, difference, percent, statement)
