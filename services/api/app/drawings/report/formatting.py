"""Figure formatting for the report (ruling X7).

The report never TYPES a figure. Every number it shows is a value read from the
results document (or the map document) and only FORMATTED here: grouped with
thousands separators, trimmed, given its unit. No arithmetic, no law, no
geometry is computed in this module - it turns one document value into one
display string.
"""

from __future__ import annotations

import math

__all__ = [
    "format_feet",
    "format_int_commas",
    "format_measure",
    "format_ratio",
    "format_sqft",
    "whole_percent_shares",
]


def _as_float(value: object) -> float | None:
    """A float view of a numeric document value, or ``None`` when it is not a
    plain number or is non-finite (inf/nan), so a missing or garbage value stays
    missing - never shown as 0 and never crashing or printing "inf.0" (DB-278)."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        return result if math.isfinite(result) else None
    return None


def format_int_commas(value: object) -> str | None:
    """A whole number grouped with commas (``20150.0`` -> ``"20,150"``); a value
    with a fractional part keeps two decimals (``6716.666...`` -> ``"6,716.67"``)."""
    number = _as_float(value)
    if number is None:
        return None
    if number == int(number):
        return f"{int(number):,}"
    return f"{number:,.2f}"


def format_sqft(value: object) -> str | None:
    """A square-foot figure (``20150.0`` -> ``"20,150 sq ft"``)."""
    grouped = format_int_commas(value)
    return None if grouped is None else f"{grouped} sq ft"


def format_ratio(value: object) -> str | None:
    """A floor-area ratio, at least one decimal (``2.0`` -> ``"2.0"``; ``2.4`` ->
    ``"2.4"``)."""
    number = _as_float(value)
    if number is None:
        return None
    text = f"{number:.2f}".rstrip("0").rstrip(".")
    if "." not in text:
        text += ".0"
    return text


def format_feet(value: object) -> str | None:
    """A length in feet (``30.0`` -> ``"30 ft"``; ``144.6`` -> ``"144.60 ft"``)."""
    grouped = format_int_commas(value)
    return None if grouped is None else f"{grouped} ft"


def whole_percent_shares(values: object) -> list[int] | None:
    """Re-round document-provided shares to whole percents that SUM TO 100 (the
    largest-remainder method), for the area-illustration display only.

    BOUNDARY (ruling X7; M5-T169): this helper computes NO zoning quantity. It takes
    shares that the DOCUMENT already carries (for example an apartment-area and
    other-area split), turns each into its percentage of their own total, and rounds
    the set so the printed whole percents add to exactly 100 - a display nicety, never
    a law or geometry calculation. ``None`` when the values are not two-or-more plain
    non-negative numbers whose total is positive, so a missing split stays missing.
    (M5-T173 only READS this helper; it owns no arithmetic of its own.)"""
    if not isinstance(values, (list, tuple)) or len(values) < 2:
        return None
    numbers = [_as_float(v) for v in values]
    if any(n is None or n < 0 for n in numbers):
        return None
    total = sum(numbers)  # type: ignore[arg-type]
    if total <= 0:
        return None
    exact = [100.0 * n / total for n in numbers]  # type: ignore[operator]
    floors = [int(x) for x in exact]
    remainder = 100 - sum(floors)
    # hand the leftover whole points to the largest fractional parts first.
    order = sorted(range(len(exact)), key=lambda i: exact[i] - floors[i], reverse=True)
    for i in order[:remainder]:
        floors[i] += 1
    return floors


def format_measure(value: object, unit: object) -> str | None:
    """Format one answer value by its document unit. Unknown units fall back to a
    grouped number with no unit, so a value is always shown, never dropped."""
    if unit == "square_feet":
        return format_sqft(value)
    if unit == "ratio":
        return format_ratio(value)
    if unit == "feet":
        return format_feet(value)
    if unit == "degrees":
        grouped = format_int_commas(value)
        return None if grouped is None else f"{grouped} degrees"
    return format_int_commas(value)
