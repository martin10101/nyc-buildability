"""Measurement source labels (plan §4) and the sourced-value record.

Plan: docs/PRODUCT_PLAN_CURRENT_2026-09-28.md §4 "Measurements" - source order, highest wins:

    1 Survey numbers the architect enters     -> "Survey (entered)"
    2 City-recorded dimensions (PLUTO, DOF)   -> "City records"
    3 Computed from the city tax-map outline  -> "Approximate — tax map"
    - No data                                 -> "Unknown — enter"

This package never produces a survey value (it has no survey input). It never picks a
winner between ranks either: it reports each rank's value side by side, and ranking is
the caller's job (queue item B-02). An unknown value is ``None`` with a plain reason -
never 0.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "LABEL_CITY_RECORDS",
    "LABEL_SURVEY",
    "LABEL_TAX_MAP",
    "LABEL_UNKNOWN",
    "RANK_CITY_RECORDS",
    "RANK_SURVEY",
    "RANK_TAX_MAP",
    "RANK_UNKNOWN",
    "SourcedValue",
    "city_records_value",
    "tax_map_value",
    "unknown_value",
]

LABEL_SURVEY = "Survey (entered)"
LABEL_CITY_RECORDS = "City records"
LABEL_TAX_MAP = "Approximate — tax map"
LABEL_UNKNOWN = "Unknown — enter"

# Rank ids of the same labels in the site_fact v1 contract
# (packages/contracts/schemas/v1/site_fact.schema.json, measurement_* definitions).
RANK_SURVEY = "survey_entered"
RANK_CITY_RECORDS = "city_records"
RANK_TAX_MAP = "approximate_tax_map"
RANK_UNKNOWN = "unknown"
_RANK_BY_LABEL = {
    LABEL_SURVEY: RANK_SURVEY,
    LABEL_CITY_RECORDS: RANK_CITY_RECORDS,
    LABEL_TAX_MAP: RANK_TAX_MAP,
    LABEL_UNKNOWN: RANK_UNKNOWN,
}

# Output precision: 0.01 ft / 0.01 sq ft - the MapPLUTO connector's canonical coordinate
# precision (COORD_DECIMALS), far below the source's stated accuracy.
VALUE_DECIMALS = 2


@dataclass(frozen=True)
class SourcedValue:
    """One measurement with its §4 label.

    ``value`` is ``None`` exactly when the measurement is unknown; ``reason`` then says
    why in plain words. ``basis`` names the dataset and the method.
    """

    value: float | None
    unit: str | None
    label: str
    basis: str
    reason: str | None = None

    @property
    def known(self) -> bool:
        return self.value is not None

    @property
    def rank(self) -> str:
        """The label's site_fact v1 rank id."""
        return _RANK_BY_LABEL[self.label]


def tax_map_value(value: float, unit: str, basis: str) -> SourcedValue:
    """A value computed from the tax-map outline (rank 3)."""
    return SourcedValue(round(float(value), VALUE_DECIMALS), unit, LABEL_TAX_MAP, basis)


def city_records_value(value: float, unit: str, basis: str) -> SourcedValue:
    """A value recorded by the city (rank 2), passed through unchanged."""
    return SourcedValue(float(value), unit, LABEL_CITY_RECORDS, basis)


def unknown_value(unit: str | None, reason: str, basis: str = "") -> SourcedValue:
    """No usable data: stays unknown, never 0."""
    return SourcedValue(None, unit, LABEL_UNKNOWN, basis, reason)
