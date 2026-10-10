"""Page type 5 - Assumptions and open items (page-types.md row 5).

The reader's question: What remains unresolved, and what would resolve it? The
page leads with the shared assumptions, each once and numbered; then the open
items (item, effect on the answer, what would resolve it, label); then the
report's coverage of the promised sections (the nine contents A to I), each "In
this report" or "Not yet in the program".
"""

from __future__ import annotations

from collections.abc import Mapping

from . import readers
from .components import label_chip, short_line
from .html import el, table

__all__ = ["render"]

QUESTION = "What remains unresolved, and what would resolve it?"

IN_REPORT = "In this report"
NOT_YET = "Not yet in the program"

NINE_CONTENTS = (
    ("A", "Property facts"),
    ("B", "Applicable zoning"),
    ("C", "Development options"),
    ("D", "Estimated floors"),
    ("E", "Simple building shapes"),
    ("F", "Legal unit limits"),
    ("G", "Realistic apartment-count estimates"),
    ("H", "Option comparisons"),
    ("I", "The downloadable report"),
)


def _has_floor_schedule(worked: list[dict]) -> bool:
    return any(b.get("floor_schedule") for b in worked)


def _has_capacity(worked: list[dict]) -> bool:
    return any(b.get("capacity_estimate") for b in worked)


def _has_legal_unit_limit(results: Mapping) -> bool:
    block = readers.answer_block(results, "floor_area_allowance")
    for value in readers.present_values(block):
        if "unit_limit" in str(value.get("key") or ""):
            return True
    return False


def _coverage_rows(results: Mapping, maps_present: bool) -> list[list[object]]:
    worked = readers.worked_buildings(results)
    states = {
        "A": IN_REPORT,
        "B": IN_REPORT if readers.present_values(
            readers.answer_block(results, "floor_area_allowance")
        ) else NOT_YET,
        "C": IN_REPORT,
        "D": IN_REPORT if _has_floor_schedule(worked) else NOT_YET,
        "E": IN_REPORT if (readers.geometry_available(results) or maps_present) else NOT_YET,
        "F": IN_REPORT if _has_legal_unit_limit(results) else NOT_YET,
        "G": IN_REPORT if _has_capacity(worked) else NOT_YET,
        "H": IN_REPORT,
        "I": IN_REPORT,
    }
    rows: list[list[object]] = []
    for letter, name in NINE_CONTENTS:
        state = states[letter]
        rows.append([f"{letter}. {name}", state])
    return rows


def _assumptions(results: Mapping) -> object:
    statements = readers.assumptions(results)
    if not statements:
        return short_line("No shared assumptions are recorded for this property.")
    return el("ol", *[el("li", statement) for statement in statements])


def _open_items(results: Mapping) -> object:
    rows = readers.open_items(results)
    if not rows:
        return short_line("No open items are recorded for this property.")
    table_rows = [
        [row["title"], row["effect"], row.get("resolves") or "Not stated",
         label_chip(row["status_label"])]
        for row in rows
    ]
    return table(
        ["Open item", "Effect on the answer", "What would resolve it", "Status"],
        table_rows,
        caption="Open items for this property",
    )


def render(results: Mapping, ident: Mapping, *, maps_present: bool = False, env=None) -> str:
    children = [
        el("h2", "Assumptions and open items"),
        el("p", QUESTION, class_="reader-question"),
        el("h3", "Shared assumptions"),
        _assumptions(results),
        el("h3", "Open items"),
        _open_items(results),
        el("h3", "Coverage of the promised sections"),
        table(
            ["Section", "State"],
            _coverage_rows(results, maps_present),
            caption="What this report covers",
        ),
    ]
    return str(el("section", *children, class_="report-page", id="assumptions-open-items"))
