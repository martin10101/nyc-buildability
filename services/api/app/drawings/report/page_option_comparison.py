"""Page type 3 - Option comparison (page-types.md row 3; rework F7; M5-T169 R075).

The page title is the reader's question. The comparison comes FIRST (R075): the
eleven-option table, then one compact bar chart. Options 1-3 carry figures; options
4-11 read "Not evaluated in this report" (R059/R084) - never an infeasibility or an
achieved-on-site finding. The "Limitation N." paragraphs are gone from this page;
the material limitations live as issue records in the evidence appendix (R025). The
chart distinguishes the floor-area allowance, each worked building's scheduled area,
and whether a building is placed on site ("Not demonstrated", no bar) on one scale
(R018/R020) - never two equal bars, never a zero-height bar for an unknown.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import drawings_embed, formatting, labels, options, readers
from .components import label_chip, short_line
from .html import el, escape, raw, table

__all__ = ["render"]

QUESTION = "How do the options compare?"


def _chart(results: Mapping, worked: list[dict]) -> object:
    allowance = readers.named_value(
        readers.answer_block(results, "floor_area_allowance"), "max_residential_floor_area"
    )
    svg = None
    if allowance is not None:
        svg = drawings_embed.allowance_bar_chart_svg(
            formatting.format_int_commas(allowance.get("value")), allowance.get("value"), worked,
            placed_on_site=not readers.building_not_placed(results),
        )
    if svg is None:
        return short_line("No scheduled building is available to chart yet.")
    return el(
        "figure",
        raw(svg),
        el("figcaption",
           "Floor-area allowance, each worked building's scheduled area, and whether a "
           "building is placed on site."),
    )


def _allowance_cell(row: dict) -> object:
    area = escape(row.get("allowance_area") or "")
    far = row.get("allowance_far")
    markup = f'<span class="nowrap">{area}</span>'
    if far:
        markup += f'<br><span class="nowrap">{escape(far)}</span>'
    return raw(markup)


def _option_rows(results: Mapping) -> list[list[object]]:
    return [
        [
            f"{row['ordinal']}. {row['name']}",
            _allowance_cell(row),
            raw(f'<span class="nowrap">{escape(row["scheduled"])}</span>')
            if row["scheduled"] == "None scheduled" else row["scheduled"],
            label_chip(row["status_label"]),
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
        # Every mention of a scheduled building uses the one phrase (D6).
        detail = labels.scheduled_floor_area_line(area) if area else "scheduled area not available"
        items.append(
            el("li", raw(f"<strong>{escape(name)}:</strong> {escape(detail)} "),
               label_chip(building["status_label"]))
        )
    for building in not_worked:
        name = f"Building {building['building']}" if building.get("building") else "Building"
        items.append(
            el("li",
               raw(f"<strong>{escape(name)} – not worked:</strong> the square-foot footprint "
                   "is withheld (see the evidence appendix) "),
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
        table(
            ["Option", "Floor-area allowance", "Scheduled building", "Status"],
            _option_rows(results),
            caption="The eleven development options, in the owner-approved order",
        ),
        _chart(results, worked),
        _buildings(results),
    ]
    return str(el("section", *children, class_="report-page", id="option-comparison"))
