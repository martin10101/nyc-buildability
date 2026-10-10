"""Figure formatting for the report (ruling X7).

The report never TYPES a figure. Every number it shows is a value read from the
results document (or the map document) and only FORMATTED here: grouped with
thousands separators, trimmed, given its unit. No arithmetic, no law, no
geometry is computed in this module - it turns one document value into one
display string.
"""

from __future__ import annotations

__all__ = [
    "format_feet",
    "format_int_commas",
    "format_measure",
    "format_ratio",
    "format_sqft",
]


def _as_float(value: object) -> float | None:
    """A float view of a numeric document value, or ``None`` when it is not a
    plain number (so a missing value stays missing - never shown as 0)."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
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
