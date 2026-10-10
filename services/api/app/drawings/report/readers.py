"""Defensive read-only views of one results document.

The page modules ask this module for the pieces they show. Every access is
defensive (``.get``), so a partial document never raises and a missing value
stays missing. This module reads the document and formats figures; it computes
no law and invents no value (ruling X7).
"""

from __future__ import annotations

from collections.abc import Mapping

from . import formatting, labels

__all__ = [
    "answer_block",
    "apartment_estimate_text",
    "assumptions",
    "category_for_key",
    "decision_open_items",
    "geometry_available",
    "identity",
    "identity_header_line",
    "input_rows",
    "label_meta_statement",
    "lot_area_basis",
    "named_value",
    "not_worked_buildings",
    "open_items",
    "present_values",
    "provenance",
    "recorded_lot_area_text",
    "withheld_values",
    "worked_buildings",
    "zoning_line",
]

ANSWER_NAMES = ("floor_area_allowance", "permitted_envelope", "building_option")


def _scope(results: Mapping) -> Mapping:
    scope = results.get("scope")
    return scope if isinstance(scope, Mapping) else {}


def _assumption_value(results: Mapping, key: str) -> object:
    for item in _scope(results).get("assumptions", []) or []:
        if isinstance(item, Mapping) and item.get("key") == key:
            return item.get("value")
    return None


def _assumption_statement(results: Mapping, key: str) -> str | None:
    for item in _scope(results).get("assumptions", []) or []:
        if isinstance(item, Mapping) and item.get("key") == key:
            text = item.get("statement")
            return str(text) if text else None
    return None


def identity(results: Mapping, *, address: str | None = None) -> dict:
    """Identity for the running header and the decision summary. ``address`` is
    supplied by the route when the path has it; the results document itself
    carries none."""
    lot = _scope(results).get("lot")
    lot = lot if isinstance(lot, Mapping) else {}
    district = _assumption_value(results, "zoning_district")
    overlay_present = _assumption_value(results, "overlay_present")
    return {
        "address": address or None,
        "borough": lot.get("borough"),
        "block": lot.get("block"),
        "lot": lot.get("lot"),
        "display": lot.get("display"),
        "bbl": lot.get("bbl"),
        "district": district,
        "overlay_present": bool(overlay_present) if overlay_present is not None else None,
        "zoning_line": zoning_line(results),
        "lot_selection": results.get("lot_selection_statement"),
        "revision": results.get("revision"),
        "computed_at": results.get("computed_at"),
    }


def zoning_line(results: Mapping) -> str | None:
    """The zoning as a compact line from the document's structured values:
    ``"Zoning district R6B · Commercial overlay C2-2"``. Never a joined
    fragment of two document sentences (A5)."""
    import re

    parts = []
    district = _assumption_value(results, "zoning_district")
    if district:
        parts.append(f"Zoning district {district}")
    if _assumption_value(results, "overlay_present"):
        statement = _assumption_statement(results, "overlay_present") or ""
        match = re.search(r"\(([A-Z0-9-]+)\)", statement)
        parts.append(f"Commercial overlay {match.group(1)}" if match else "Commercial overlay")
    special = _assumption_statement(results, "special_district_present")
    if _assumption_value(results, "special_district_present"):
        match = re.search(r"\(([A-Z0-9-]+)\)", special or "")
        parts.append(f"Special district {match.group(1)}" if match else "Special purpose district")
    return " · ".join(parts) if parts else None


def identity_header_line(ident: Mapping) -> str:
    """One compact line for the running header, joined with ' · ' (D5). When
    the address already carries the borough, it is not repeated from the display
    (``"215-16 Northern Boulevard, Queens · block 7334, lot 70"``)."""
    display = ident.get("display")
    address = ident.get("address")
    borough = ident.get("borough")
    if address and display and borough and str(display).startswith(str(borough)):
        display = str(display)[len(str(borough)):].lstrip(" ,")
    parts = [str(part) for part in (address, display) if part]
    return " · ".join(parts) if parts else "Selected tax lot"


def answer_block(results: Mapping, name: str) -> Mapping:
    answers = results.get("answers")
    answers = answers if isinstance(answers, Mapping) else {}
    block = answers.get(name)
    return block if isinstance(block, Mapping) else {}


def _value_states(block: Mapping) -> Mapping:
    states = block.get("value_states")
    return states if isinstance(states, Mapping) else {}


def present_values(block: Mapping) -> list[dict]:
    """The answer's shown values (those not withheld), each with a formatted
    figure and a label."""
    states = _value_states(block)
    rows: list[dict] = []
    for value in block.get("values", []) or []:
        if not isinstance(value, Mapping):
            continue
        key = value.get("key")
        state = states.get(key) if isinstance(states.get(key), Mapping) else {}
        if state.get("way") == "withheld":
            continue
        rows.append(
            {
                "key": key,
                "label": value.get("label"),
                "value": value.get("value"),
                "display": formatting.format_measure(value.get("value"), value.get("unit")),
                "unit": value.get("unit"),
                "zr_sections": list(value.get("zr_sections", []) or []),
                "sources": list(value.get("sources", []) or []),
                "status_label": labels.label_for_way(state) if state else labels.PROVISIONAL,
                "conditions": list(state.get("conditions", []) or []),
            }
        )
    return rows


def withheld_values(block: Mapping) -> list[dict]:
    """The answer's withheld values, each with its reason, what resolves it and a
    label. No figure is shown for a withheld value."""
    rows: list[dict] = []
    for key, state in _value_states(block).items():
        if not isinstance(state, Mapping) or state.get("way") != "withheld":
            continue
        rows.append(
            {
                "key": key,
                "label": state.get("label"),
                "reason": state.get("reason"),
                "gap_kind": state.get("gap_kind"),
                "resolved_by": state.get("resolved_by"),
                "zr_sections": list(state.get("zr_sections", []) or []),
                "status_label": labels.label_for_value_state(state),
            }
        )
    return rows


def _scheduled_area(building: Mapping) -> object:
    for key in ("total_floor_area_sqft", "floor_area_allowance_sqft"):
        if building.get(key) is not None:
            return building.get(key)
    return None


def worked_buildings(results: Mapping) -> list[dict]:
    rows: list[dict] = []
    for building in results.get("building_alternatives", []) or []:
        if not isinstance(building, Mapping):
            continue
        area = _scheduled_area(building)
        rows.append(
            {
                "building": building.get("building"),
                "label": building.get("label"),
                "scheduled_display": formatting.format_int_commas(area),
                "scheduled_value": area,
                "storey_count": building.get("storey_count"),
                "height_display": formatting.format_feet(building.get("height_ft")),
                "footprint_display": formatting.format_sqft(building.get("footprint_area_sqft")),
                "floor_schedule": list(building.get("floor_schedule", []) or []),
                "not_checked": list(building.get("not_checked", []) or []),
                "capacity_estimate": building.get("capacity_estimate"),
                "fit_note": building.get("fit_note"),
                "fill_rule": building.get("fill_rule"),
                "below_min_base": building.get("below_min_base"),
                "status_label": labels.label_for_way(building.get("way")),
            }
        )
    return rows


def not_worked_buildings(results: Mapping) -> list[dict]:
    rows: list[dict] = []
    for building in results.get("buildings_not_worked", []) or []:
        if not isinstance(building, Mapping):
            continue
        rows.append(
            {
                "building": building.get("building"),
                "label": building.get("label"),
                "reason": building.get("reason"),
                "resolved_by": building.get("resolved_by"),
                "status_label": labels.label_for_gap_kind(building.get("gap_kind")),
            }
        )
    return rows


# The label-meta assumption is moved to the evidence page's provenance (F9).
_LABEL_META_KEY = "site_measurement_rank"


def assumptions(results: Mapping) -> list[str]:
    """The shared assumptions as their document statements, each once, in document
    order. The label-meta assumption (how the weakest input sets the label) is
    excluded here and shown on the evidence page instead (F9)."""
    out: list[str] = []
    for item in _scope(results).get("assumptions", []) or []:
        if not isinstance(item, Mapping) or item.get("key") == _LABEL_META_KEY:
            continue
        if item.get("statement"):
            out.append(str(item["statement"]))
    return out


def label_meta_statement(results: Mapping) -> str | None:
    """The 'results carry the label of their weakest input' statement, for the
    evidence page's provenance (F9)."""
    return _assumption_statement(results, _LABEL_META_KEY)


def _coverage_block(results: Mapping) -> Mapping:
    block = results.get("coverage_by_portion")
    return block if isinstance(block, Mapping) else {}


# Short, structural effect text per open-item category (F8) and the order they
# appear in, by effect on the main answers.
_EFFECTS = {
    "lot_area": "The floor-area figures depend on it; the recorded area and the tax-map outline "
                "disagree.",
    "coverage": "The square-foot coverage figure is withheld.",
    "rear_yard": "The rear yard is not known beyond the corner area.",
    "placement": "Where the building sits on the lot is not worked out.",
    "legal_unit_limit": "No legal apartment limit is shown.",
    "setback": "The setback above the base is not worked out.",
    "street_wall": "The street wall is not checked.",
    "parking": "Parking, loading and bicycle requirements are not checked.",
}
_ORDER = ["lot_area", "coverage", "rear_yard", "placement", "legal_unit_limit",
          "setback", "street_wall", "parking"]
_CHECK_WORD = "A check not yet made against an independently worked example."


def category_for_key(key: str) -> str | None:
    """The open-item category for a withheld value key (public helper used by the
    site page to key its 'see item N' references)."""
    return _category(key)


def _category(key: str) -> str | None:
    key = str(key or "")
    if "legal_unit_limit" in key:
        return "legal_unit_limit"
    if "lot_coverage" in key or key == "coverage_by_portion":
        return "coverage"
    if "rear_yard" in key:
        return "rear_yard"
    if "setback" in key:
        return "setback"
    return None


def _not_checked_category(text: str) -> str | None:
    low = str(text or "").lower()
    if "street wall" in low:
        return "street_wall"
    if "where the plan sits" in low or "placement" in low:
        return "placement"
    if "parking" in low or "loading" in low or "bicycle" in low:
        return "parking"
    return None


def open_items(results: Mapping) -> list[dict]:
    """Every open item, numbered and ordered by effect on the main answers (F8):
    the lot-area condition, the withheld values (unit limits combined, coverage,
    rear yard, setback) and the worked building's not-checked items (placement,
    street wall, parking). Each carries a short structural effect and the full
    document reason. The order is presentation, not a legal ranking."""
    by_category: dict[str, dict] = {}

    def put(category, title, reason, resolves, label):
        if category in by_category or not category:
            return
        by_category[category] = {
            "category": category,
            "title": title,
            "effect": _EFFECTS.get(category, ""),
            "reason": reason,
            "resolves": resolves,
            "status_label": label,
        }

    basis = lot_area_basis(results)
    if basis:
        put("lot_area", "Recorded lot area", basis,
            "A survey or deed that confirms the lot area.", labels.CONDITIONAL)
    for name in ANSWER_NAMES:
        for row in withheld_values(answer_block(results, name)):
            category = _category(row["key"])
            title = "Legal apartment limit" if category == "legal_unit_limit" else row["label"]
            put(category, title, row["reason"], row["resolved_by"], row["status_label"])
    coverage = _coverage_block(results)
    if coverage.get("status") == "withheld":
        put("coverage", coverage.get("label") or "Maximum lot coverage", coverage.get("reason"),
            coverage.get("resolved_by"), labels.label_for_value_state(coverage))
    for building in worked_buildings(results):
        for text in building.get("not_checked", []) or []:
            category = _not_checked_category(text)
            put(category, str(text), str(text), _CHECK_WORD, labels.PENDING_VERIFICATION)

    ordered = [by_category[c] for c in _ORDER if c in by_category]
    ordered += [v for c, v in by_category.items() if c not in _ORDER]
    for number, item in enumerate(ordered, start=1):
        item["number"] = number
    return ordered


def decision_open_items(results: Mapping) -> list[dict]:
    """The three most important open items for the decision summary (F3): a
    condition of the allowance (the recorded lot area), what limits the scheduled
    building (site fit), then the apartment limit. Falls back to the first items
    when a category is absent."""
    items = open_items(results)
    by_cat = {item["category"]: item for item in items}
    picks: list[dict] = []
    for preferred in (["lot_area"], ["rear_yard", "placement"], ["legal_unit_limit"]):
        for category in preferred:
            if category in by_cat and by_cat[category] not in picks:
                picks.append(by_cat[category])
                break
    for item in items:
        if len(picks) >= 3:
            break
        if item not in picks:
            picks.append(item)
    return picks[:3]


def named_value(block: Mapping, key: str) -> dict | None:
    """One shown value of an answer by its key, or ``None`` when it is absent or
    withheld."""
    for row in present_values(block):
        if row.get("key") == key:
            return row
    return None


def lot_area_basis(results: Mapping) -> str | None:
    """The document's own words for the recorded-lot-area / tax-map-outline
    disagreement (the first ``contradicted_record`` condition it carries)."""
    for name in ANSWER_NAMES:
        for row in present_values(answer_block(results, name)):
            for condition in row.get("conditions", []) or []:
                if not isinstance(condition, Mapping):
                    continue
                if condition.get("kind") == "contradicted_record" and condition.get("assumption"):
                    return str(condition["assumption"])
    for building in results.get("building_alternatives", []) or []:
        if not isinstance(building, Mapping):
            continue
        way = building.get("way")
        conditions = way.get("conditions", []) if isinstance(way, Mapping) else []
        for condition in conditions or []:
            if isinstance(condition, Mapping) and condition.get("kind") == "contradicted_record":
                text = condition.get("assumption")
                if text:
                    return str(text)
    return None


def apartment_estimate_text(estimate: object) -> str | None:
    """The preliminary apartment estimate as a plain range, from the document's
    own whole-number range and apartment size. No percentage is computed."""
    if not isinstance(estimate, Mapping):
        return None
    low = formatting.format_int_commas(estimate.get("whole_below_low"))
    high = formatting.format_int_commas(estimate.get("whole_above_high"))
    size = formatting.format_int_commas(estimate.get("apartment_size_sqft"))
    if low is None or high is None:
        return None
    text = f"about {low} to {high} apartments"
    if size is not None:
        text += f", assuming about {size} sq ft per apartment"
    return text


def geometry_available(results: Mapping) -> bool:
    geometry = results.get("geometry")
    return isinstance(geometry, Mapping) and geometry.get("status") == "available"


_INPUT_NAMES = {
    "zoning_district": "Zoning district",
    "overlay_present": "Commercial overlay",
    "special_district_present": "Special purpose district",
    "special_density_area": "Special density area",
    "lot_type": "Lot type",
    "lot_front_ft": "Lot frontage",
    "lot_depth_ft": "Lot depth",
    "within_100_ft_of_street_line_intersection":
        "Lot within 100 ft of the street-line intersection",
    "street_line_intersection_angle_degrees": "Street-line intersection angle",
    "housing_program": "Housing program",
    "floor_to_floor_ft": "Floor-to-floor height",
}
_BASIS_NAMES = {
    "city_records": "City records",
    "approximate_tax_map": "Approximate tax map",
    "default": "Default",
    "assumed": "Assumed",
}


def _input_value_text(value: object, unit: object) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        return formatting.format_measure(value, unit) or ""
    text = str(value)
    return text.replace("_", " ").capitalize() if "_" in text else text


def recorded_lot_area_text(results: Mapping) -> str | None:
    """The recorded lot-area figure, read from the document's own condition
    sentence (never retyped)."""
    basis = lot_area_basis(results)
    if not basis:
        return None
    import re

    match = re.search(r"recorded lot area of ([\d,]+) sq ft", basis)
    return f"{match.group(1)} sq ft" if match else None


def input_rows(results: Mapping) -> list[dict]:
    """Inputs for the evidence page: name, value (readable), basis. The recorded
    lot area comes first (from the document's own condition sentence); the rest
    come from the scope assumptions in a readable form (F11)."""
    rows: list[dict] = []
    area = recorded_lot_area_text(results)
    if area:
        rows.append({"name": "Recorded lot area", "value": area, "basis": "City tax-lot record"})
    assumptions_by_key = {}
    for item in _scope(results).get("assumptions", []) or []:
        if isinstance(item, Mapping) and item.get("key"):
            assumptions_by_key[item["key"]] = item
    for key, name in _INPUT_NAMES.items():
        item = assumptions_by_key.get(key)
        if not item:
            continue
        rows.append(
            {
                "name": name,
                "value": _input_value_text(item.get("value"), item.get("unit")),
                "basis": _BASIS_NAMES.get(item.get("basis"), str(item.get("basis") or "").title()),
            }
        )
    return rows


def provenance(results: Mapping) -> dict:
    rules = []
    for item in results.get("rule_versions", []) or []:
        if isinstance(item, Mapping):
            rules.append(
                {
                    "rule_id": item.get("rule_id"),
                    "version": item.get("version"),
                    "status": item.get("status"),
                }
            )
    return {
        "revision": results.get("revision"),
        "computed_at": results.get("computed_at"),
        "rule_versions": rules,
    }
