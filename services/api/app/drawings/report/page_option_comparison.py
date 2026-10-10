"""Page type 3 - Option comparison (page-types.md row 3; rework F7).

The page title is the reader's question. All eleven options in the owner-approved
order, on one basis: option, floor-area allowance, scheduled building, label and
a numbered shared limitation. The shared limitations are stated once above the
table. One compact bar chart shows the allowance against each worked building's
scheduled area, on one scale.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import drawings_embed, formatting, options, readers
from .components import label_chip, short_line
from .html import el, escape, raw, table

__all__ = ["render"]

QUESTION = "How do the options compare?"


def _shared_limitations(results: Mapping) -> object:
    rows = options.shared_limitations(results)
    items = [
        el("p", raw(f"<strong>Limitation {row['number']}.</strong> "), row["sentence"])
        for row in rows
    ]
    return el("div", el("h3", "Shared limitations"), *items, class_="shared-limitations")


def _chart(results: Mapping, worked: list[dict]) -> object:
    allowance = readers.named_value(
        readers.answer_block(results, "floor_area_allowance"), "max_residential_floor_area"
    )
    svg = None
    if allowance is not None:
        svg = drawings_embed.allowance_bar_chart_svg(
            formatting.format_int_commas(allowance.get("value")), allowance.get("value"), worked
        )
    if svg is None:
        return short_line("No scheduled building is available to chart yet.")
    return el(
        "figure",
        raw(svg),
        el("figcaption", "Floor-area allowance against each worked building's scheduled area."),
    )


def _option_rows(results: Mapping) -> list[list[object]]:
    return [
        [
            f"{row['ordinal']}. {row['name']}",
            row["allowance"],
            row["scheduled"],
            label_chip(row["status_label"]),
            f"Limitation {row['limitation']}",
        ]
        for row in options.option_rows(results)
    ]


def _buildings(results: Mapping) -> object:
    worked = readers.worked_buildings(results)
    not_worked = readers.not_worked_buildings(results)
    items = []
    for building in worked:
        name = f"Building {building['building']}" if building.get("building") else "Worked building"
        area = building.get("scheduled_display")
        detail = f"scheduled {area} sq ft" if area else "scheduled area not available"
        items.append(
            el("li", raw(f"<strong>{escape(name)}:</strong> {escape(detail)} "),
               label_chip(building["status_label"]))
        )
    for building in not_worked:
        name = f"Building {building['building']}" if building.get("building") else "Building"
        items.append(
            el("li",
               raw(f"<strong>{escape(name)} - not worked:</strong> the square-foot footprint "
                   "is withheld (see Limitation 1) "),
               label_chip(building["status_label"]))
        )
    if not items:
        return short_line("No building has been worked for this property yet.")
    return el("div", el("h3", "Worked and not-worked buildings"), el("ul", *items))


def render(results: Mapping, ident: Mapping, *, env=None) -> str:
    worked = readers.worked_buildings(results)
    children = [
        el("p", "Option comparison", class_="type-name"),
        el("h2", QUESTION),
        _shared_limitations(results),
        _chart(results, worked),
        table(
            ["Option", "Floor-area allowance", "Scheduled building", "Status", "Limitation"],
            _option_rows(results),
            caption="The eleven development options, in the owner-approved order",
        ),
        _buildings(results),
    ]
    return str(el("section", *children, class_="report-page", id="option-comparison"))
