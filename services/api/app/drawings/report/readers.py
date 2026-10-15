"""Defensive read-only views of one results document.

The page modules ask this module for the pieces they show. Every access is
defensive (``.get``), so a partial document never raises and a missing value
stays missing. This module reads the document and formats figures; it computes
no law and invents no value (ruling X7).
"""

from __future__ import annotations

from collections.abc import Mapping

from . import constraint_text, formatting, labels, unit_limit_text, zoning_lot_item
from .zoning_lot_item import zoning_lot_basis

__all__ = [
    "answer_block",
    "apartment_estimate_range",
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
    "NOT_PLACED_LINE",
    "building_not_placed",
    "named_value",
    "not_worked_buildings",
    "open_items",
    "results_lot_outline",
    "present_values",
    "provenance",
    "recorded_lot_area_text",
    "withheld_values",
    "worked_buildings",
    "zoning_line",
    "zoning_lot_basis",
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


# The open-item order, by effect on the main answers. The short structural effect
# text per category now lives in :mod:`.constraint_text` (the constraints) and
# :mod:`.zoning_lot_item` (the zoning-lot condition); this module only wires them
# into the numbered list (the G-6 report-side isolation, M5-T165).
_ORDER = ["zoning_lot", "lot_area", "coverage", "rear_yard", "placement", "legal_unit_limit",
          "setback", "street_wall", "side_yard", "parking"]
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
            "effect": constraint_text.effect_for(category),
            "reason": reason,
            "resolves": resolves,
            "status_label": label,
        }

    # (DB-232) the property-specific zoning-lot concern, ordered FIRST (owner D-094 R029/R030):
    # the figures carry a condition that recorded documents may name this lot with another. The
    # item is built by its own module (zoning_lot_item) so readers stays a general reader.
    zoning_lot = zoning_lot_item.zoning_lot_open_item(results)
    if zoning_lot is not None:
        by_category["zoning_lot"] = zoning_lot
    basis = lot_area_basis(results)
    if basis:
        # The full lot-area condition sentence is stated once, on the Site and
        # context page; the open item points to it rather than repeating it (V-C2).
        put("lot_area", "Recorded lot area", "See Site and context for the lot-area basis.",
            "A survey or deed that confirms the lot area.", labels.CONDITIONAL)
    for name in ANSWER_NAMES:
        for row in withheld_values(answer_block(results, name)):
            category = _category(row["key"])
            # The legal-apartment-limit item is built from the whole document (shown
            # and withheld limits together) below, not from each withheld row alone.
            if category == "legal_unit_limit":
                continue
            put(category, row["label"], row["reason"], row["resolved_by"], row["status_label"])
    limit_item = unit_limit_text.legal_unit_limit_item(results)
    if limit_item is not None:
        by_category["legal_unit_limit"] = limit_item
    coverage = _coverage_block(results)
    if coverage.get("status") == "withheld":
        put("coverage", coverage.get("label") or "Maximum lot coverage", coverage.get("reason"),
            coverage.get("resolved_by"), labels.label_for_value_state(coverage))
    for building in worked_buildings(results):
        for text in building.get("not_checked", []) or []:
            category = _not_checked_category(text)
            put(category, str(text), str(text), _CHECK_WORD, labels.PENDING_VERIFICATION)

    # M5-T167 (R136/S23): on a 1.5.0 document the rear-yard open item shows the engine's applied
    # ZR 23-344 result, not the "not yet checked" open check. A 1.4.0 document carries no rear_yard
    # block, so this is a no-op and the item stays byte-identical to M5-T165's open-check wording.
    _apply_rear_yard_open_item(by_category, results)
    # M5-T170: on a 1.5.0 document the setback / street-wall / side-yard appendix items show the
    # engine's applied envelope readings (the setback item is rewritten from the withheld value;
    # the street-wall and side-yard items are added from the envelope rows, since the page-6
    # not-checked line and any withheld value have cleared). A 1.4.0 document carries no envelope
    # rows, so this is a no-op and page 8 stays byte-identical.
    _apply_envelope_open_items(by_category, results)

    ordered = [by_category[c] for c in _ORDER if c in by_category]
    ordered += [v for c, v in by_category.items() if c not in _ORDER]
    for number, item in enumerate(ordered, start=1):
        item["number"] = number
    return ordered


# The open-item status label for the combined rear-yard row's way (the 1.3.0 vocabulary as a plain
# word). A conditional reading shows as Conditional (owner's six labels); any other way keeps the
# item's existing label.
_REAR_YARD_LABEL_BY_WAY = {"conditional": labels.CONDITIONAL}


def _rear_yard_open_effect(combined: Mapping) -> str:
    """A SHORT applied-result effect for the appendix rear-yard open item, read from the combined
    row's way and sections (the full draft reading is shown on the design page, not repeated here,
    so the appendix stays within the report's word cap). Never 'not yet checked', never an
    unconditional 'no rear yard' (R136/S13); it names ZR 23-344(b) and (c)(3)."""
    way = combined.get("way")
    lead = "A conditional reading" if way == "conditional" else "A draft reading"
    return (
        f"{lead} of the short-block rule ZR 23-344(b) and the adjoining-side-line rule "
        "ZR 23-344(c)(3): the rear yard is not settled on this lot."
    )


def _apply_rear_yard_open_item(by_category: dict, results: Mapping) -> None:
    """Rewrite the rear-yard open item from the document's own 1.5.0 rear_yard block (R136): its
    effect becomes a short applied-result reading and its label follows the combined way. No-op when
    the document carries no rear_yard block (every 1.4.0 document), so the item stays byte-identical
    to the open-check wording."""
    combined = constraint_text.rear_yard_combined(results)
    if combined is None or "rear_yard" not in by_category:
        return
    item = by_category["rear_yard"]
    item["effect"] = _rear_yard_open_effect(combined)
    item["status_label"] = _REAR_YARD_LABEL_BY_WAY.get(
        combined.get("way"), item["status_label"]
    )


# The page-8 envelope appendix items (M5-T170). Title, a SHORT applied-result effect, and a short
# "what would resolve it", per kind; the setback and street-wall effects vary with the row state so
# they match page 3. Plain user texts: no internal name, never "not yet checked" where page 3 shows
# an applied reading, never an unconditional claim.
_ENVELOPE_TITLES = {"setback": "Setback above the base", "street_wall": "Street wall",
                    "side_yard": "Side yard"}
_ENVELOPE_RESOLVES = {
    "setback": "The building's street-wall height against the maximum base height.",
    "street_wall": "A survey of the adjacent street walls and the operative street line.",
    "side_yard": "The building type and whether an open area runs along a side lot line.",
}


def _envelope_open_label(row: Mapping) -> str:
    """The appendix label for a 1.5.0 envelope row: a not_known row is Pending verification; a row
    resting on named assumptions is Conditional; a plain applies / not_applicable reading is
    Provisional. Mirrors the page-3 chip so pages 3 and 8 agree."""
    if row.get("state") == "not_known":
        return labels.PENDING_VERIFICATION
    if row.get("conditions"):
        return labels.CONDITIONAL
    return labels.PROVISIONAL


def _envelope_open_effect(kind: str, row: Mapping) -> str:
    """A short applied-result effect that matches the row's own state (so page 8 agrees with page
    3). The setback and street-wall effects name whether the check applies here; the side yard is
    'none required'."""
    if kind == "setback":
        if row.get("state") == "not_applicable":
            return "No setback above the base is required for this building (ZR 23-433)."
        return "A setback above the base applies for this building (ZR 23-433)."
    if kind == "street_wall":
        return "The street wall sits close to the street line; the exact position is conditional."
    # side yard: the effect follows the row state, like the setback branch, so page 8 never
    # contradicts page 3 (a detached building without the overlay needs two 5-ft yards).
    if row.get("state") == "applies":
        return "Two side yards, each at least 5 feet wide, are required (ZR 23-335(a))."
    return "No side yard is required (ZR 23-335; ZR 34-232 under a commercial overlay)."


def _apply_envelope_open_items(by_category: dict, results: Mapping) -> None:
    """Show the applied envelope readings on page 8 from the document's own 1.5.0 envelope_rows
    (M5-T170). The setback item (still present as a withheld value, reconciled to the envelope row)
    is rewritten; the street-wall and side-yard items are added (their page-6 not-checked line and
    any withheld value have cleared), so page 8 agrees with page 3. The item's detail reason is set
    to its effect, so the appendix prints the short effect once (no duplicate reason row). No-op
    when the document carries no envelope row (every 1.4.0 document), so page 8 stays
    byte-identical."""
    for kind in ("setback", "street_wall", "side_yard"):
        row = constraint_text.envelope_row(results, kind)
        if row is None:
            continue
        effect = _envelope_open_effect(kind, row)
        item = by_category.get(kind) or {"category": kind, "title": _ENVELOPE_TITLES[kind]}
        item["effect"] = effect
        item["reason"] = effect  # detail line omitted (reason == effect) so it prints once
        item["resolves"] = _ENVELOPE_RESOLVES[kind]
        item["status_label"] = _envelope_open_label(row)
        by_category[kind] = item


def decision_open_items(results: Mapping) -> list[dict]:
    """The three uncertainties for the decision summary, in the design-contract order
    (D-094 R050, R037): the zoning lot, the lot-area basis, then the rear yard. Falls
    back to the next open items when one of those categories is absent, so the page
    always shows at most three."""
    items = open_items(results)
    by_cat = {item["category"]: item for item in items}
    picks: list[dict] = []
    # The page-1 uncertainty order (owner D-094): zoning lot, lot-area basis, rear yard.
    for preferred in (["zoning_lot"], ["lot_area"], ["rear_yard"]):
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


def apartment_estimate_range(estimate: object) -> str | None:
    """The preliminary apartment estimate's whole-number range as ``"low-high"``
    (e.g. ``"17-22"``) for the page-1 estimate figure, read from the document; both
    bounds come from the document and none is retyped. ``None`` when the range is
    absent."""
    if not isinstance(estimate, Mapping):
        return None
    low = formatting.format_int_commas(estimate.get("whole_below_low"))
    high = formatting.format_int_commas(estimate.get("whole_above_high"))
    if low is None or high is None:
        return None
    return f"{low}-{high}"


def apartment_estimate_text(estimate: object) -> str | None:
    """The preliminary apartment estimate with the assumptions that make it
    reconcile (V-C1): the document's whole-number range, its usable-share
    sensitivity range (D-090 R540) and its chosen starting apartment size on the
    HPD basis (D-090 R541). Every figure comes from the document; none is retyped
    and no percentage is computed."""
    if not isinstance(estimate, Mapping):
        return None
    low = formatting.format_int_commas(estimate.get("whole_below_low"))
    high = formatting.format_int_commas(estimate.get("whole_above_high"))
    size = formatting.format_int_commas(estimate.get("apartment_size_sqft"))
    share_low = formatting.format_int_commas(estimate.get("share_low"))
    share_high = formatting.format_int_commas(estimate.get("share_high"))
    if low is None or high is None:
        return None
    text = f"about {low} to {high} apartments"
    if share_low is not None and share_high is not None:
        text += (f", using {share_low} to {share_high} of the floor area inside apartments "
                 "as an unvalidated sensitivity range")
    if size is not None:
        text += (f", and a chosen starting apartment size of {size} sq ft "
                 "measured as HPD measures an apartment")
    return text


def geometry_available(results: Mapping) -> bool:
    geometry = results.get("geometry")
    return isinstance(geometry, Mapping) and geometry.get("status") == "available"


def results_lot_outline(results: Mapping) -> list | None:
    """The lot-outline rings from ``/geometry/lot_outline`` (the results document's
    own local-feet outline), or ``None`` when the document carries none. Used by
    the one-outline check (ruling Y5), never retyped or drawn directly."""
    geometry = results.get("geometry")
    if not isinstance(geometry, Mapping):
        return None
    rings = geometry.get("lot_outline")
    return rings if isinstance(rings, list) and rings else None


# The ONE plain sentence shown whenever the results document gives no floor plate
# (ruling Y8, D-090 R939). The document's reason text is never spliced in.
NOT_PLACED_LINE = (
    "No building is placed on this plan yet: the program does not yet work out "
    "where a building sits on the lot."
)


def building_not_placed(results: Mapping) -> bool:
    """True when the results document carries a floor-plates block that is not
    ``available`` - no building is placed on the plan yet (ruling Y8). False when a
    floor plate is placed or the document carries no floor-plates block."""
    geometry = results.get("geometry")
    plates = geometry.get("floor_plates") if isinstance(geometry, Mapping) else None
    return isinstance(plates, Mapping) and plates.get("status") != "available"


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
