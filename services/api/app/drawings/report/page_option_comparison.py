"""Page type 3 - Option comparison (page-types.md row 3).

The reader's question: How do the options compare? All eleven options in the
owner-approved order, on one basis. Shared limitations are stated once above the
table and referred to by number. One compact bar chart shows the floor-area
allowance against each worked building's scheduled area, on one scale.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import drawings_embed, options, readers
from .components import label_chip, short_line
from .html import el, raw, table

__all__ = ["render"]

QUESTION = "How do the options compare?"


def _shared_limitations() -> object:
    return el(
        "div",
        el("h3", "Shared limitations"),
        el("p", raw(f'<strong>Limitation 1.</strong> {options.SHARED_LIMITATION_1}')),
        el("p", raw(f'<strong>Limitation 2.</strong> {options.SHARED_LIMITATION_2}')),
        class_="shared-limitations",
    )


def _chart(results: Mapping, worked: list[dict]) -> object:
    block = readers.answer_block(results, "floor_area_allowance")
    allowance = readers.named_value(block, "max_residential_floor_area")
    svg = None
    if allowance is not None:
        from .formatting import format_int_commas

        svg = drawings_embed.allowance_bar_chart_svg(
            format_int_commas(allowance.get("value")), allowance.get("value"), worked
        )
    if svg is None:
        return short_line("No scheduled building is available to chart yet.")
    return el(
        "figure",
        raw(svg),
        el("figcaption", "Floor-area allowance against each worked building's scheduled area."),
    )


def _option_rows(results: Mapping) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in options.option_rows(results):
        rows.append(
            [
                f"{row['ordinal']}. {row['name']}",
                row["result"],
                label_chip(row["status_label"]),
                f"Limitation {row['limitation']}",
            ]
        )
    return rows


def _buildings(results: Mapping) -> object:
    worked = readers.worked_buildings(results)
    not_worked = readers.not_worked_buildings(results)
    items = []
    for building in worked:
        name = f"Building {building['building']}" if building.get("building") else "Worked building"
        area = building.get("scheduled_display")
        detail = f"scheduled {area} sq ft" if area else "scheduled area not available"
        items.append(el("li", raw(f'<strong>{el("span", name)}:</strong> {detail} '),
                        label_chip(building["status_label"])))
    for building in not_worked:
        name = f"Building {building['building']}" if building.get("building") else "Building"
        items.append(
            el(
                "li",
                raw(f'<strong>{el("span", name)} - not worked:</strong> '),
                label_chip(building["status_label"]),
                el("div", building.get("reason") or ""),
            )
        )
    if not items:
        return short_line("No building has been worked for this property yet.")
    return el("div", el("h3", "Worked and not-worked buildings"), el("ul", *items))


def render(results: Mapping, ident: Mapping, *, env=None) -> str:
    worked = readers.worked_buildings(results)
    children = [
        el("h2", "Option comparison"),
        el("p", QUESTION, class_="reader-question"),
        _shared_limitations(),
        _chart(results, worked),
        table(
            ["Option", "Available result", "Status", "Material limitation"],
            _option_rows(results),
            caption="The eleven development options, in the owner-approved order",
        ),
        _buildings(results),
    ]
    return str(el("section", *children, class_="report-page", id="option-comparison"))
