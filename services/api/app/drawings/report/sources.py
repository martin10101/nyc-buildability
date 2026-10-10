"""Readable source titles (rulings X6, R925).

The results document names its sources by raw reference - a rule id with a draft
version, or a BBL-prefixed fact key. The report never shows those: it shows a
readable title. This module turns one raw reference into one plain title and
carries no figures.
"""

from __future__ import annotations

__all__ = [
    "LAW_SITE_TITLE",
    "readable_fact_title",
    "readable_rule_status",
    "readable_rule_title",
    "readable_source_title",
    "readable_zr_reference",
    "zr_section_number",
]

LAW_SITE_TITLE = "New York City Zoning Resolution (official text)"

# Known draft rule ids -> readable titles. An unknown id falls back to a generic
# title so no raw id (which can carry build words) reaches the reader.
_RULE_TITLES = {
    "r6-r12-residential-far": "Residential floor-area rule (R6-R12 districts)",
    "r6b-qualifying-housing-far": "Qualifying-housing floor-area rule (R6B)",
    "r6b-height": "Height and setback rule (R6B)",
    "r6b-lot-coverage": "Lot-coverage rule (R6B)",
    "r6b-rear-yard": "Rear-yard rule (R6B)",
    "r6b-dwelling-units": "Dwelling-unit rule (R6B)",
}

# Known fact keys -> readable titles.
_FACT_TITLES = {
    "lot_area": "Recorded lot area (city tax-lot record)",
    "lot_frontage": "Lot frontage (city tax-lot record)",
    "lot_depth": "Lot depth (city tax-lot record)",
    "lot_type": "Lot type (city tax-lot record)",
    "zoning_district": "Zoning district (city records)",
}


def _rule_id_of(ref: object) -> str:
    """The rule id before any ``@version`` marker."""
    return str(ref).split("@", 1)[0] if ref is not None else ""


def readable_rule_title(ref: object) -> str:
    rule_id = _rule_id_of(ref)
    if rule_id in _RULE_TITLES:
        return _RULE_TITLES[rule_id]
    return "Draft zoning rule (pending review)"


def readable_rule_status(status: object) -> str:
    if status == "needs_review":
        return "draft, pending review"
    if status in (None, ""):
        return "draft"
    return str(status).replace("_", " ")


def readable_fact_title(ref: object) -> str:
    key = str(ref).split(":", 1)[-1] if ref is not None else ""
    base = key.split(":", 1)[0]
    if base in _FACT_TITLES:
        return _FACT_TITLES[base]
    cleaned = base.replace("_", " ").strip()
    return f"Recorded {cleaned}" if cleaned else "Recorded city data"


def readable_source_title(kind: object, ref: object) -> str:
    if kind == "rule_table":
        return readable_rule_title(ref)
    if kind == "site_fact":
        return readable_fact_title(ref)
    return "Recorded source"


def zr_section_number(section: object) -> str:
    """``"ZR 23-22"`` -> ``"23-22"`` (the bare section number)."""
    text = str(section or "").strip()
    return text[2:].strip() if text.upper().startswith("ZR") else text


def readable_zr_reference(section: object) -> str:
    """``"ZR 23-22"`` -> ``"New York City Zoning Resolution, Section 23-22"``."""
    number = zr_section_number(section)
    return f"New York City Zoning Resolution, Section {number}" if number else LAW_SITE_TITLE
