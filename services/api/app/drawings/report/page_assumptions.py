"""Page type 5 - Assumptions and open items (page-types.md row 5).

The page title is the reader's question. It leads with the shared assumptions
(each once), then the open items with a short structural effect and the full
reason beneath in smaller type. The coverage of the promised sections moved to
the decision summary as a compact block (rework D9), so it is not repeated here.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import readers
from .components import label_chip, short_line
from .html import el

__all__ = ["render"]

QUESTION = "What remains unresolved, and what would resolve it?"


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
        reason = item.get("reason")
        # Omit the detail line when it only repeats the item's name or effect (A3).
        if reason and reason not in (item["effect"], item["title"]):
            rows.append(el("tr", el("td", reason, colspan="5"), class_="reason-row"))
    return el(
        "table",
        el("caption", "Open items for this property"),
        header,
        el("tbody", *rows),
    )


def render(results: Mapping, ident: Mapping, *, env=None) -> str:
    # The shared assumptions (two columns) and the open-items table share one page,
    # so neither the table is split into a near-empty fragment nor a page is left
    # near-empty (correction 2).
    children = [
        el("p", "Assumptions and open items", class_="type-name"),
        el("h2", QUESTION),
        el("h3", "Shared assumptions"),
        _assumptions(results),
        el("div", el("h3", "Open items"), _open_items(results), class_="open-items-block"),
    ]
    return str(el("section", *children, class_="report-page", id="assumptions-open-items"))
