"""Page type 4 - Scenario sheet (page-types.md row 4), one sheet per worked
building.

The reader's question: What is this option? Each sheet leads with the scheduled
floor-area line, storeys and height; shows the floor-stack section (from the
schedule, Illustrative) with the permitted-envelope height lines when drawn; the
two-zone area illustration with ONE caption carrying the document's apartment /
other / total floor-area figures and the footprint basis; the floor schedule with
the plate read as zoning floor area per storey, reconciled to the running total;
why it has this shape; its preliminary apartment estimate; and the unresolved
items for this building, linked to the appendix. A building that was not worked
gets no sheet (it is a row on the option-comparison page).

Every figure comes from the results document (this module formats, never
computes); every drawn or placed claim takes an explicit flag (``footprint_drawn``
and the embedded drawings), so the sheet never says a thing is drawn unless it is.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.drawings.kit.presentation_tokens import WORDING

from . import formatting, labels, readers, scenario_figures
from .components import figure, label_chip, short_line
from .html import el, escape, escape_attr, raw, table

__all__ = ["render"]

QUESTION = "What is this option?"
_SCHEDULE_HEADERS = (
    "Storey",
    "Floor-to-floor",
    "Top of floor",
    "Zoning floor area per storey",
    "Floor area",
    "Running total",
)

# The placement basis token (the nine quantity bases) turned into plain words for
# the illustration caption. The two geometry bases are named exactly so a tax-map
# footprint is never called a city-map outline or vice versa (G-10); any other
# basis falls back to its readable token.
_BASIS_WORDS = {"printed_tax_map": "printed tax map", "gis": "city map outline"}

# Shown only when the rounded storey figures do not add to the shown total.
_ROUNDING_NOTE = (
    "Storey areas are shown rounded; the running total adds the unrounded areas."
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


def _basis_in_words(basis: object) -> str | None:
    if not basis:
        return None
    return _BASIS_WORDS.get(str(basis), str(basis).replace("_", " "))


def _area_caption(building: Mapping) -> str:
    """The ONE figcaption beneath the area illustration: the caption token, then the
    document's apartment / other / total floor-area figures, then the footprint
    basis when a footprint is drawn (fitted). No percentage, no second sentence -
    the kernel prints the one percentage inside the drawing."""
    block = building.get("area_allocation") if isinstance(building, Mapping) else None
    block = block if isinstance(block, Mapping) else {}
    token = WORDING["area_illustration_caption"]
    apartment = formatting.format_int_commas(block.get("apartment_area_sqft"))
    other = formatting.format_int_commas(block.get("other_area_sqft"))
    total = formatting.format_int_commas(block.get("total_sqft"))
    if apartment is None or other is None or total is None:
        return f"{token}."
    text = (
        f"{token}. apartment area {apartment} sq ft; other building area {other} sq ft; "
        f"of {total} sq ft residential floor area"
    )
    if block.get("fitted") is True:
        placement = building.get("placement") if isinstance(building, Mapping) else None
        basis = placement.get("basis") if isinstance(placement, Mapping) else None
        words = _basis_in_words(basis)
        if words:
            text += f"; footprint on the {words}"
    return text


def _conversion_statement(building: Mapping) -> str | None:
    """The document's plate conversion statement (from the area_allocation or the
    placement block), or ``None`` when the document carries neither."""
    if not isinstance(building, Mapping):
        return None
    for key in ("area_allocation", "placement"):
        block = building.get(key)
        if isinstance(block, Mapping):
            statement = block.get("conversion_statement")
            if statement:
                return str(statement)
    return None


def _shown_number(value: object) -> float | None:
    """The numeric value as the schedule displays it (``format_int_commas`` rounding:
    a whole number, else two decimals), so the reconciliation compares the SHOWN
    figures, not the raw ones."""
    text = formatting.format_int_commas(value)
    if text is None:
        return None
    return float(text.replace(",", ""))


def _needs_rounding_note(building: Mapping) -> bool:
    """True when the shown per-storey floor areas do not add to the shown running
    total (e.g. 3 x 6,716.67 against 20,150), so the reconciliation note is shown."""
    floors = [f for f in (building.get("floor_schedule") or []) if isinstance(f, Mapping)]
    if not floors:
        return False
    shown: list[float] = []
    for floor in floors:
        value = _shown_number(floor.get("floor_area_sqft"))
        if value is None:
            return False
        shown.append(value)
    total = _shown_number(floors[-1].get("running_total_sqft"))
    if total is None:
        return False
    return abs(round(sum(shown), 2) - round(total, 2)) > 0.005


def _section_caption(has_height_lines: bool, footprint_drawn: object) -> str:
    """The floor-stack section caption. With the permitted-envelope height lines it
    names them; otherwise today's wording, dropping the 'no placement on the lot'
    clause only when the footprint is drawn on page 4 (``footprint_drawn`` True)."""
    if has_height_lines:
        return (
            "Section (Illustrative): storeys from the floor schedule; height limits "
            "from the permitted envelope (Conditional)."
        )
    base = "Floor-stack section (Illustrative): drawn from the schedule only"
    if footprint_drawn is True:
        return f"{base}."
    return f"{base}, with no placement on the lot."


def _floor_plates_available(results: Mapping) -> bool:
    geometry = results.get("geometry") if isinstance(results, Mapping) else None
    plates = geometry.get("floor_plates") if isinstance(geometry, Mapping) else None
    return isinstance(plates, Mapping) and plates.get("status") == "available"


def _placement_line(results: Mapping, building: Mapping, footprint_drawn: object) -> object:
    """The one placement sentence, or ``None``. No floor plate placed keeps the
    standing not-placed line; a placed building whose footprint is worked out but
    not drawn (``footprint_drawn`` False) says so; a drawn footprint (True) or an
    unknown drawn-state (None) says nothing - the sheet never claims a drawing it
    does not carry."""
    if readers.building_not_placed(results):
        return short_line(readers.NOT_PLACED_LINE)
    placement = building.get("placement") if isinstance(building, Mapping) else None
    placed = isinstance(placement, Mapping) and placement.get("status") == "placed"
    if placed and _floor_plates_available(results) and footprint_drawn is False:
        return short_line("The footprint is worked out but is not drawn in this report.")
    return None


def _unresolved_items(building: Mapping) -> list[str]:
    """This building's unresolved items: ``not_checked`` plus the placement's
    ``not_checked``, de-duplicated case-insensitively in document order."""
    items: list[str] = []
    seen: set[str] = set()

    def add(values: object) -> None:
        for value in values or []:
            text = str(value).strip()
            key = text.lower()
            if text and key not in seen:
                seen.add(key)
                items.append(text)

    add(building.get("not_checked") if isinstance(building, Mapping) else None)
    placement = building.get("placement") if isinstance(building, Mapping) else None
    add(placement.get("not_checked") if isinstance(placement, Mapping) else None)
    return items


def _appendix_link_line(results: Mapping) -> object:
    """One line linking the appendix open items by their reader number (so each
    ``#issue-<n>`` anchor resolves), or ``None`` when there are none. The comma and
    the full stop sit INSIDE each anchor text so they do not read as separate words
    against the page's word budget."""
    numbers = [item.get("number") for item in readers.open_items(results)
               if item.get("number") is not None]
    if not numbers:
        return None
    parts: list[object] = [raw(escape("Open items in the appendix: "))]
    last = len(numbers) - 1
    for index, number in enumerate(numbers):
        suffix = "." if index == last else ","
        parts.append(raw(f'<a href="#issue-{escape_attr(number)}">{escape(number)}{suffix}</a>'))
        if index != last:
            parts.append(raw(" "))
    return el("p", *parts, class_="short-line")


def _unresolved_block(results: Mapping, building: Mapping) -> object:
    items = _unresolved_items(building)
    if not items:
        return None
    children: list[object] = [
        el("h3", raw("Unresolved for this building ")),
        label_chip(labels.PENDING_VERIFICATION),
        el("ul", *[el("li", item) for item in items]),
    ]
    link = _appendix_link_line(results)
    if link is not None:
        children.append(link)
    return el("div", *children, class_="scenario-unresolved")


def _sheet(results: Mapping, raw_building: Mapping, view: Mapping, env,
           draw: scenario_figures.ScenarioDrawings, footprint_drawn: object) -> str:
    name = f"Building {view['building']}" if view.get("building") else "Worked building"
    area = view.get("scheduled_display")
    scheduled = (
        labels.scheduled_floor_area_line(area) if area else "Scheduled building not available"
    )
    children = [
        el("p", f"Scenario sheet - {name}", class_="type-name"),
        el("h2", QUESTION),
        el(
            "p",
            raw(f'<span class="answer-value">{scheduled}</span>'),
            label_chip(view["status_label"]),
        ),
    ]
    if view.get("storey_count") and view.get("height_display"):
        children.append(el("p", f"{view['storey_count']} storeys; {view['height_display']}."))
    if view.get("below_min_base") is True:
        children.append(
            el("p", "This building is below the minimum base height.", class_="limitation")
        )
    placement_line = _placement_line(results, raw_building, footprint_drawn)
    if placement_line is not None:
        children.append(placement_line)
    # The (tall, narrow) floor-stack section sits BESIDE the "Why it has this shape"
    # text, so the sheet fits one page where it can (correction 3). The area
    # illustration sits under that row; the floor schedule needs the full width.
    section_fig = figure(
        draw.section,
        _section_caption(draw.section_has_height_lines, footprint_drawn),
        line_when_absent="The floor-stack section is not shown here.",
    )
    side: list[object] = []
    if view.get("label"):
        side.append(el("div", el("h3", "Why it has this shape"), el("p", view["label"])))
    children.append(el("div",
        el("div", section_fig, class_="scenario-figure"),
        el("div", *side, class_="scenario-side"),
        class_="scenario-row"))
    if draw.area_illustration is not None:
        children.append(el("div",
            figure(draw.area_illustration, _area_caption(raw_building),
                   figure_class="area-illustration"),
            class_="area-illustration-row"))
    # The floor schedule and the preliminary apartment estimate stay together, so the
    # estimate never lands as a lone line (rework 1 fix 5). The plate column is the
    # zoning floor area per storey; the conversion statement is printed once on the
    # page (inside the illustration when drawn, else as a footnote here), and the
    # rounding note shows only when the shown figures do not reconcile.
    tail: list[object] = [
        el("h3", "Floor schedule"),
        table(_SCHEDULE_HEADERS, _schedule_rows(raw_building),
              caption="Floor schedule for this building"),
    ]
    if _needs_rounding_note(raw_building):
        tail.append(short_line(_ROUNDING_NOTE))
    illustration_drawn = draw.area_illustration is not None and draw.area_illustration.is_drawing
    if not illustration_drawn:
        conversion = _conversion_statement(raw_building)
        if conversion:
            tail.append(short_line(conversion))
    estimate = readers.apartment_estimate_text(view.get("capacity_estimate"))
    if estimate is not None:
        # This is the apartment estimate's FULL calculation; page 1 shows the range and
        # links here (D-094 R013, R2-F14). The id lets that link resolve. The long
        # sentence prints once in the report - on this sheet, not on page 1.
        estimate_id = f"estimate-{view['building']}" if view.get("building") else None
        tail.append(
            el("p", raw(f'<strong>Preliminary apartment estimate:</strong> {estimate} '),
               label_chip(labels.PROVISIONAL), id=estimate_id)
        )
    children.append(el("div", *tail, class_="sheet-tail"))
    unresolved = _unresolved_block(results, raw_building)
    if unresolved is not None:
        children.append(unresolved)
    return str(
        el("section", *children, class_="report-page", id=f"scenario-{view.get('building')}")
    )


def render(results: Mapping, ident: Mapping, *, env=None, drawings=None,
           footprint_drawn=None) -> str:
    """One scenario sheet per worked building. ``drawings`` are the per-building
    :class:`scenario_figures.ScenarioDrawings` (part W embeds them once); ``None``
    embeds them here. ``footprint_drawn`` is the manifest's drawn-state for page 4
    (True / False / None), carried into the section caption and the placement line."""
    raw_list = [b for b in (results.get("building_alternatives") or []) if isinstance(b, Mapping)]
    views = readers.worked_buildings(results)
    if not views:
        empty = [
            el("p", "Scenario sheet", class_="type-name"),
            el("h2", QUESTION),
            short_line("No building option has been worked for this property yet."),
        ]
        return str(el("section", *empty, class_="report-page", id="scenario-none"))
    sheets: list[str] = []
    for index, (raw_building, view) in enumerate(zip(raw_list, views, strict=False)):
        draw = drawings[index] if drawings is not None and index < len(drawings) else None
        if draw is None:
            draw = scenario_figures.scenario_drawings_for(raw_building, results, env=env)
        sheets.append(_sheet(results, raw_building, view, env, draw, footprint_drawn))
    return "".join(sheets)
