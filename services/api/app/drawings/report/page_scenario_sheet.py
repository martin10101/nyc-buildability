"""Page type 4 - Scenario sheet (page-types.md row 4), one sheet per worked
building.

The reader's question: What is this option? Each sheet leads with the scheduled
floor-area line, storeys and height; shows the floor-stack section (from the
schedule only, Illustrative); the floor schedule; why it has this shape; what
was not checked; and its preliminary apartment estimate. A building that was not
worked gets no sheet (it is a row on the option-comparison page).
"""

from __future__ import annotations

from collections.abc import Mapping

from . import drawings_embed, formatting, labels, readers
from .components import figure, label_chip, short_line
from .html import el, raw, table

__all__ = ["render"]

QUESTION = "What is this option?"
_SCHEDULE_HEADERS = (
    "Storey",
    "Floor-to-floor",
    "Top of floor",
    "Plan area",
    "Floor area",
    "Running total",
)


def _schedule_rows(building: Mapping) -> list[list[object]]:
    rows: list[list[object]] = []
    for floor in building.get("floor_schedule", []) or []:
        if not isinstance(floor, Mapping):
            continue
        rows.append(
            [
                formatting.format_int_commas(floor.get("storey")),
                formatting.format_feet(floor.get("floor_to_floor_ft")),
                formatting.format_feet(floor.get("top_ft")),
                formatting.format_sqft(floor.get("plan_area_sqft")),
                formatting.format_sqft(floor.get("floor_area_sqft")),
                formatting.format_sqft(floor.get("running_total_sqft")),
            ]
        )
    return rows


def _not_checked(view: Mapping) -> object:
    entries = view.get("not_checked") or []
    if not entries:
        return short_line("Nothing is recorded as unchecked for this building.")
    items = [el("li", entry) for entry in entries]
    return el(
        "div",
        el("h3", raw('What was not checked ')),
        label_chip(labels.PENDING_VERIFICATION),
        el("ul", *items),
    )


def _sheet(results: Mapping, raw_building: Mapping, view: Mapping, env) -> str:
    name = f"Building {view['building']}" if view.get("building") else "Worked building"
    area = view.get("scheduled_display")
    scheduled = (
        labels.scheduled_floor_area_line(area) if area else "Scheduled building not available"
    )
    head_bits = []
    if view.get("storey_count") and view.get("height_display"):
        head_bits.append(f"{view['storey_count']} storeys; {view['height_display']}.")
    stack = drawings_embed.embed_floor_stack(raw_building, env=env)
    children = [
        el("p", f"Scenario sheet - {name}", class_="type-name"),
        el("h2", QUESTION),
        el(
            "p",
            raw(f'<span class="answer-value">{scheduled}</span>'),
            label_chip(view["status_label"]),
        ),
    ]
    if head_bits:
        children.append(el("p", " ".join(head_bits)))
    if view.get("below_min_base") is True:
        children.append(
            el("p", "This building is below the minimum base height.", class_="limitation")
        )
    if readers.building_not_placed(results):
        # One plain sentence whenever the document gives no floor plate (ruling Y8);
        # no footprint, building outline or 3D view is drawn.
        children.append(short_line(readers.NOT_PLACED_LINE))
    children.append(
        figure(
            stack,
            "Floor-stack section (Illustrative): drawn from the schedule only, "
            "with no placement on the lot.",
            line_when_absent="The floor-stack section is not shown here.",
        )
    )
    if view.get("label"):
        children.append(el("div", el("h3", "Why it has this shape"), el("p", view["label"])))
    # The floor schedule, what was not checked and the preliminary apartment estimate
    # stay TOGETHER on one page, so the estimate never lands as a lone line on a page
    # of its own (rework 1 fix 5).
    tail: list[object] = [
        el("h3", "Floor schedule"),
        table(_SCHEDULE_HEADERS, _schedule_rows(raw_building),
              caption="Floor schedule for this building"),
        _not_checked(view),
    ]
    estimate = readers.apartment_estimate_text(view.get("capacity_estimate"))
    if estimate is not None:
        tail.append(
            el("p", raw(f'<strong>Preliminary apartment estimate:</strong> {estimate} '),
               label_chip(labels.PROVISIONAL))
        )
    children.append(el("div", *tail, class_="sheet-tail"))
    return str(
        el("section", *children, class_="report-page", id=f"scenario-{view.get('building')}")
    )


def render(results: Mapping, ident: Mapping, *, env=None) -> str:
    raw_list = [b for b in (results.get("building_alternatives") or []) if isinstance(b, Mapping)]
    views = readers.worked_buildings(results)
    if not views:
        empty = [
            el("p", "Scenario sheet", class_="type-name"),
            el("h2", QUESTION),
            short_line("No building option has been worked for this property yet."),
        ]
        return str(el("section", *empty, class_="report-page", id="scenario-none"))
    return "".join(
        _sheet(results, raw_building, view, env)
        for raw_building, view in zip(raw_list, views, strict=False)
    )
