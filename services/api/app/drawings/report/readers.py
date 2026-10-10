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
    "geometry_available",
    "identity",
    "identity_header_line",
    "lot_area_basis",
    "named_value",
    "not_worked_buildings",
    "open_items",
    "present_values",
    "provenance",
    "withheld_values",
    "worked_buildings",
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
        "overlay_statement": _assumption_statement(results, "overlay_present"),
        "lot_selection": results.get("lot_selection_statement"),
        "revision": results.get("revision"),
        "computed_at": results.get("computed_at"),
    }


def identity_header_line(ident: Mapping) -> str:
    """One compact line for the running header: address (when known) and the
    borough/block/lot display."""
    display = ident.get("display")
    address = ident.get("address")
    parts = [str(part) for part in (address, display) if part]
    return " - ".join(parts) if parts else "Selected tax lot"


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
                "status_label": labels.label_for_answer_status(
                    "not_available", building.get("gap_kind")
                ),
            }
        )
    return rows


def assumptions(results: Mapping) -> list[str]:
    """The shared assumptions as their document statements, in document order."""
    out: list[str] = []
    for item in _scope(results).get("assumptions", []) or []:
        if isinstance(item, Mapping) and item.get("statement"):
            out.append(str(item["statement"]))
    return out


def _coverage_block(results: Mapping) -> Mapping:
    block = results.get("coverage_by_portion")
    return block if isinstance(block, Mapping) else {}


def open_items(results: Mapping) -> list[dict]:
    """Every open item in the document: a withheld value of any answer, a withheld
    coverage figure, and an unavailable answer. In document order; the decision
    summary takes the first three. This order is presentation, not a legal
    ranking."""
    items: list[dict] = []
    seen: set[tuple] = set()

    def add(title, effect, resolves, status_label, zr_sections):
        marker = (str(title), str(effect))
        if title and effect and marker not in seen:
            seen.add(marker)
            items.append(
                {
                    "title": title,
                    "effect": effect,
                    "resolves": resolves,
                    "status_label": status_label,
                    "zr_sections": list(zr_sections or []),
                }
            )

    for name in ANSWER_NAMES:
        for row in withheld_values(answer_block(results, name)):
            add(row["label"], row["reason"], row["resolved_by"], row["status_label"],
                row["zr_sections"])
    coverage = _coverage_block(results)
    if coverage.get("status") == "withheld":
        add(coverage.get("label"), coverage.get("reason"), coverage.get("resolved_by"),
            labels.label_for_value_state(coverage), coverage.get("zr_sections"))
    return items


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
