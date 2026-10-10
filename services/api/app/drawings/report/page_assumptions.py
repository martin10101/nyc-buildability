"""Page type 5 - Assumptions and open items (page-types.md row 5; rework F8-F10).

The page title is the reader's question. It leads with the shared assumptions
(each once), then the open items with a short structural effect and the full
reason beneath in smaller type, then the report's coverage of the promised
sections with three honest states.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import readers
from .components import label_chip, short_line
from .html import el, table

__all__ = ["render"]

QUESTION = "What remains unresolved, and what would resolve it?"

IN_REPORT = "In this report"
PARTLY = "Partly in this report"
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

# The six further sections the owner kept in scope, plus context maps (F10). Read
# from the section map: none is built into the report yet.
FURTHER_SECTIONS = (
    ("Comparable sales nearby", "A workspace tool only; not in this report."),
    ("Block description", "Not built."),
    ("Parking, loading and bicycle parking", "Not computed; listed as not checked."),
    ("Aerial and street photographs", "Needs a licensed imagery source."),
    ("Tax abatement eligibility", "Not computed."),
    ("Financial analysis inputs", "Held by the owner."),
    ("Context maps", "Not included in this report."),
)


def _assumptions(results: Mapping) -> object:
    statements = readers.assumptions(results)
    if not statements:
        return short_line("No shared assumptions are recorded for this property.")
    return el("ol", *[el("li", statement) for statement in statements])


def _open_items(results: Mapping) -> object:
    items = readers.open_items(results)
    if not items:
        return short_line("No open items are recorded for this property.")
    header = el(
        "thead",
        el("tr", el("th", "#"), el("th", "Item"), el("th", "Effect on the answer"),
           el("th", "What would resolve it"), el("th", "Status")),
    )
    rows: list[object] = []
    for item in items:
        rows.append(
            el("tr",
               el("td", item["number"], class_="open-number"),
               el("td", item["title"]),
               el("td", item["effect"]),
               el("td", item.get("resolves") or "Not stated"),
               el("td", label_chip(item["status_label"])))
        )
        if item.get("reason") and item["reason"] != item["effect"]:
            rows.append(el("tr", el("td", item["reason"], colspan="5"), class_="reason-row"))
    return el(
        "table",
        el("caption", "Open items for this property"),
        header,
        el("tbody", *rows),
    )


def _coverage_rows(results: Mapping) -> list[list[object]]:
    worked = readers.worked_buildings(results)
    n_worked = len(worked)
    has_schedule = any(b.get("floor_schedule") for b in worked)
    has_capacity = any(b.get("capacity_estimate") for b in worked)
    c_state = ((PARTLY, f"{n_worked} of 11 options worked") if n_worked
               else (NOT_YET, "No option worked"))
    d_state = ((PARTLY, "the worked building only") if has_schedule
               else (NOT_YET, "No worked building"))
    e_state = (
        (PARTLY, "lot outline and floor stack; the envelope is not drawn")
        if readers.geometry_available(results) else (NOT_YET, "No lot outline")
    )
    states = {
        "A": (IN_REPORT, ""),
        "B": (IN_REPORT, ""),
        "C": c_state,
        "D": d_state,
        "E": e_state,
        "F": (NOT_YET, "The legal unit limit is withheld"),
        "G": (PARTLY, "the worked building only") if has_capacity else (NOT_YET, "No estimate"),
        "H": (IN_REPORT, ""),
        "I": (IN_REPORT, ""),
    }
    rows: list[list[object]] = []
    for letter, name in NINE_CONTENTS:
        state, note = states[letter]
        rows.append([f"{letter}. {name}", state, note])
    for name, note in FURTHER_SECTIONS:
        rows.append([name, NOT_YET, note])
    return rows


def render(results: Mapping, ident: Mapping, *, env=None) -> str:
    children = [
        el("p", "Assumptions and open items", class_="type-name"),
        el("h2", QUESTION),
        el("h3", "Shared assumptions"),
        _assumptions(results),
        el("h3", "Open items"),
        _open_items(results),
        el("h3", "Coverage of the promised sections"),
        table(
            ["Section", "State", "Note"],
            _coverage_rows(results),
            caption="What this report covers",
        ),
    ]
    return str(el("section", *children, class_="report-page", id="assumptions-open-items"))
