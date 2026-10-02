"""Disclosed selection of comparable sales "of similar type and size" (queue item B-11,
plan section 11b; Lane B).

Input is the typed, sourced :class:`~app.connectors.dof_sales_soda.SaleRecord` rows the
connector retrieved from the official DOF sales dataset. This module applies ONE simple,
fully disclosed filter and returns the matching rows with the criteria stated in plain
words. It is NOT a valuation and never an appraisal: it computes no average, no
price-per-square-foot and no estimate - only the publisher's recorded sale price and date
per row (plan: "Do not present the comps as a valuation").

How "similar type and size" is defined is a PRODUCT choice, not a fact. The default filter
below is deliberately simple and is surfaced verbatim so the architect sees exactly what
was applied; confirming or changing it is an open owner question (docs/lanes/status/B.md),
never decided here.

Default filter:

- **Similar type**: the same DOF ``building_class_category`` as the subject. (The connector
  already queries candidates by this field; the filter re-asserts it so a mixed candidate
  list cannot leak a different type.)
- **Similar size**: recorded gross floor area within a tolerance fraction (default +/-50%)
  of the subject's recorded gross floor area. A candidate with no recorded gross floor area
  (DOF leaves it 0 or blank for many lots) is NOT size-matched; it is listed separately so
  the gap is visible, never silently dropped and never guessed.
- **Market sales only**: a $0 sale price is excluded. Per the official ``sale_date`` field
  description, "A $0 sale price indicates that there was a transfer of ownership without a
  cash consideration" - a non-arms-length transfer, not a market sale.
- **Not the subject**: the subject's own lot is excluded from its comparables.

Every excluded candidate is kept with its reason, so nothing is hidden. Pure, deterministic
code: no I/O, no legal logic, no valuation.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from app.connectors.dof_sales_soda import SaleRecord

__all__ = [
    "DEFAULT_SIZE_TOLERANCE_FRACTION",
    "NOT_A_VALUATION_NOTICE",
    "ComparableSalesResult",
    "SelectionCriteria",
    "SubjectSpec",
    "select_comparables",
    "subject_spec_from_record",
]

DEFAULT_SIZE_TOLERANCE_FRACTION = 0.5

# Shown wherever the comparables appear (plan section 5a: one disclosure, not beside every
# row). Verbatim, owner-facing.
NOT_A_VALUATION_NOTICE = (
    "These are recorded sales selected by a simple, disclosed filter, not a valuation or an "
    "appraisal. How \"similar type and size\" should be defined is a product choice to "
    "confirm with the owner."
)

# Excluded-reason tokens (stable, machine-readable).
REASON_SELF = "subject_lot"
REASON_ZERO_PRICE = "zero_price_transfer"
REASON_TYPE_MISMATCH = "different_building_class_category"
REASON_NO_SIZE = "no_recorded_gross_floor_area"
REASON_SIZE_OUT_OF_RANGE = "gross_floor_area_out_of_range"


@dataclass(frozen=True)
class SubjectSpec:
    """The subject lot's recorded type and size, the two inputs the filter matches on.

    These are the subject's OWN recorded DOF values (or an owner-chosen pair); this module
    does not derive them. ``gross_square_feet`` may be None (no recorded size), in which
    case size cannot be matched and the result says so.
    """

    bbl: str | None
    building_class_category: str | None
    gross_square_feet: int | None


@dataclass(frozen=True)
class SelectionCriteria:
    """The disclosed filter. Defaults are a simple product choice, surfaced verbatim."""

    size_tolerance_fraction: float = DEFAULT_SIZE_TOLERANCE_FRACTION
    exclude_zero_price: bool = True
    require_recorded_size: bool = True

    def size_bounds(self, subject_gross_sq_ft: int) -> tuple[float, float]:
        low = subject_gross_sq_ft * (1.0 - self.size_tolerance_fraction)
        high = subject_gross_sq_ft * (1.0 + self.size_tolerance_fraction)
        return low, high


@dataclass(frozen=True)
class ComparableSalesResult:
    """The selected comparable sales and every disclosure around them.

    ``selected`` is the matching rows (sorted most-recent first, as the connector returned
    them). ``excluded`` is every candidate not selected, each ``{bbl, address, sale_date,
    reason}`` with a stable reason token. ``criteria_text`` and ``not_a_valuation`` are the
    verbatim owner-facing lines. ``source`` is the sale rows' shared provenance.
    """

    subject: SubjectSpec
    criteria: SelectionCriteria
    criteria_text: str
    not_a_valuation: str
    selected: tuple[SaleRecord, ...]
    excluded: tuple[dict, ...]
    source: dict | None


def subject_spec_from_record(record: SaleRecord) -> SubjectSpec:
    """Build a :class:`SubjectSpec` from the subject's OWN recorded DOF sale row."""
    return SubjectSpec(
        bbl=record.bbl,
        building_class_category=record.building_class_category,
        gross_square_feet=record.gross_square_feet,
    )


def _excluded(record: SaleRecord, reason: str) -> dict:
    return {
        "bbl": record.bbl,
        "address": record.address,
        "sale_date": record.sale_date,
        "reason": reason,
    }


def _criteria_text(subject: SubjectSpec, criteria: SelectionCriteria) -> str:
    type_clause = (
        f"same DOF building class category \"{subject.building_class_category}\""
        if subject.building_class_category is not None
        else "same DOF building class category (the subject has no recorded category)"
    )
    pct = f"{criteria.size_tolerance_fraction * 100:g}%"
    if subject.gross_square_feet is not None and subject.gross_square_feet > 0:
        size_clause = (
            f"recorded gross floor area within +/-{pct} of the subject's recorded "
            f"{subject.gross_square_feet:,} sq ft"
        )
    else:
        size_clause = (
            "recorded gross floor area within the size tolerance (the subject has no "
            "recorded gross floor area, so no size match could be applied)"
        )
    parts = [f"Similar type: {type_clause}.", f"Similar size: {size_clause}."]
    if criteria.exclude_zero_price:
        parts.append(
            "Market sales only: $0 sales (transfers without cash consideration, per DOF) "
            "are excluded."
        )
    parts.append("The subject lot itself is excluded.")
    parts.append(
        "Candidates with no recorded gross floor area are listed separately, not "
        "size-matched."
    )
    return " ".join(parts)


def select_comparables(
    subject: SubjectSpec,
    candidates: Iterable[SaleRecord],
    *,
    criteria: SelectionCriteria | None = None,
    source: dict | None = None,
) -> ComparableSalesResult:
    """Select comparable sales for ``subject`` from ``candidates`` by the disclosed filter.

    ``source`` is the sale rows' shared provenance (``DofSalesResult.provenance``), carried
    through for the record; when omitted it is taken from the first candidate's ``source``.
    Returns a :class:`ComparableSalesResult`; it is never a valuation.
    """
    criteria = criteria or SelectionCriteria()
    rows: Sequence[SaleRecord] = tuple(candidates)
    if source is None and rows:
        source = rows[0].source
    bounds = (
        criteria.size_bounds(subject.gross_square_feet)
        if subject.gross_square_feet is not None and subject.gross_square_feet > 0
        else None
    )

    selected: list[SaleRecord] = []
    excluded: list[dict] = []
    for record in rows:
        if subject.bbl is not None and record.bbl == subject.bbl:
            excluded.append(_excluded(record, REASON_SELF))
            continue
        if subject.building_class_category is not None and (
            record.building_class_category != subject.building_class_category
        ):
            excluded.append(_excluded(record, REASON_TYPE_MISMATCH))
            continue
        if criteria.exclude_zero_price and not record.is_cash_sale:
            excluded.append(_excluded(record, REASON_ZERO_PRICE))
            continue
        if not record.has_recorded_size:
            if criteria.require_recorded_size:
                excluded.append(_excluded(record, REASON_NO_SIZE))
                continue
        elif bounds is not None:
            low, high = bounds
            if not (low <= record.gross_square_feet <= high):
                excluded.append(_excluded(record, REASON_SIZE_OUT_OF_RANGE))
                continue
        selected.append(record)

    return ComparableSalesResult(
        subject=subject,
        criteria=criteria,
        criteria_text=_criteria_text(subject, criteria),
        not_a_valuation=NOT_A_VALUATION_NOTICE,
        selected=tuple(selected),
        excluded=tuple(excluded),
        source=source,
    )
