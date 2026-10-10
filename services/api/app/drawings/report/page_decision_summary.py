"""Page type 1 - Decision summary (page-types.md row 1).

The reader's question: What can I potentially build? The page leads with the
property and the three answers (floor-area allowance, permitted envelope,
scheduled building), then a small site plan, the preliminary apartment estimate
apart, and the three most important open items with their effect.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import drawings_embed, labels, readers
from .components import answer_block, figure, label_chip
from .html import el, raw

__all__ = ["render"]

QUESTION = "What can I potentially build?"


def _property_heading(ident: Mapping) -> raw:
    display = ident.get("display")
    address = ident.get("address")
    title = address or display or "Selected tax lot"
    lines = [el("h1", title)]
    sub = []
    if address and display:
        sub.append(display)
    district = ident.get("district")
    if district:
        sub.append(f"District {district}")
    if ident.get("overlay_statement"):
        sub.append(ident["overlay_statement"])
    if sub:
        lines.append(el("p", "; ".join(str(s) for s in sub), class_="identity-line"))
    if ident.get("lot_selection"):
        lines.append(el("p", ident["lot_selection"], class_="identity-line"))
    return el("div", *lines)


def _allowance_answer(results: Mapping) -> raw:
    block = readers.answer_block(results, "floor_area_allowance")
    far = readers.named_value(block, "max_residential_far")
    area = readers.named_value(block, "max_residential_floor_area")
    if area is None:
        return answer_block("Floor-area allowance", None, labels.PENDING_VERIFICATION)
    value = area["display"]
    if far and far.get("display"):
        value = f"{value} (FAR {far['display']})"
    return answer_block("Floor-area allowance", value, area["status_label"])


def _envelope_answer(results: Mapping) -> raw:
    block = readers.answer_block(results, "permitted_envelope")
    min_base = readers.named_value(block, "min_base_height")
    max_base = readers.named_value(block, "max_base_height")
    max_building = readers.named_value(block, "max_building_height")
    if max_building is None:
        return answer_block("Permitted envelope", None, labels.PENDING_VERIFICATION)
    parts = []
    if min_base and max_base:
        parts.append(f"Base {min_base['display']} to {max_base['display']}")
    parts.append(f"building up to {max_building['display']}")
    return answer_block("Permitted envelope", "; ".join(parts), max_building["status_label"])


def _scheduled_answer(worked: list[dict]) -> raw:
    if not worked:
        return answer_block(
            "Scheduled building", "No building option worked yet", labels.PENDING_VERIFICATION
        )
    first = worked[0]
    area = first.get("scheduled_display")
    value = labels.scheduled_floor_area_line(area) if area else "Scheduled building not available"
    exception = None
    if first.get("storey_count") and first.get("height_display"):
        exception = f"{first['storey_count']} storeys; {first['height_display']}."
    return answer_block("Scheduled building", value, first["status_label"], exception)


def _apartment_estimate(worked: list[dict]) -> raw | None:
    if not worked:
        return None
    text = readers.apartment_estimate_text(worked[0].get("capacity_estimate"))
    if text is None:
        return None
    return el(
        "p",
        raw(f'<strong>Preliminary apartment estimate:</strong> {text} '),
        label_chip(labels.PROVISIONAL),
        class_="estimate-line",
    )


def _open_items(results: Mapping) -> raw:
    rows = readers.open_items(results)[:3]
    if not rows:
        return el("p", "No open items recorded.", class_="short-line")
    items = []
    for row in rows:
        items.append(
            el(
                "li",
                raw(f'<strong>{el("span", row["title"])}</strong> '),
                label_chip(row["status_label"]),
                el("div", row["effect"]),
            )
        )
    return el("div", el("h3", "Most important open items"), el("ul", *items), class_="open-items")


def render(results: Mapping, ident: Mapping, *, map_context=None, env=None) -> str:
    worked = readers.worked_buildings(results)
    site_plan = drawings_embed.embed_kit_drawing("render_site_plan", results, env=env)
    children = [
        _property_heading(ident),
        el("p", labels.STANDING_LABEL, class_="standing-label"),
        el("p", QUESTION, class_="reader-question"),
        _allowance_answer(results),
        _envelope_answer(results),
        _scheduled_answer(worked),
        figure(site_plan, "Site plan shown when the drawing is available."),
    ]
    estimate = _apartment_estimate(worked)
    if estimate is not None:
        children.append(estimate)
    children.append(_open_items(results))
    return str(el("section", *children, class_="report-page", id="decision-summary"))
