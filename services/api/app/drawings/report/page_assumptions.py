"""Page type 5 - Assumptions and open items (page-types.md row 5).

The page title is the reader's question. It leads with the shared assumptions
(each once), then the open items with a short structural effect and the full
reason beneath in smaller type. The coverage of the promised sections moved to
the decision summary as a compact block (rework D9), so it is not repeated here.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import coverage, readers
from .components import label_chip, short_line
from .html import el, escape, raw

__all__ = ["render"]

QUESTION = "What remains unresolved, and what would resolve it?"


def _material_exclusions(results: Mapping, *, maps_present: bool = False) -> object:
    """The compact scope note at the head of the appendix (D-094 R012): every
    material exclusion, i.e. the sections the report does not yet cover. The coverage
    inventory itself has left the report; this names only what is excluded. 'Context
    maps' is excluded only when the report does not print its maps: the builder passes
    its ``maps_present`` here, so when the surroundings' maps render the note drops it."""
    groups = dict(coverage.coverage_groups(results, maps_present=maps_present))
    not_yet = groups.get("Not yet", [])
    if not not_yet:
        return el("p", "This report covers every promised section.", class_="scope-note")
    return el(
        "p",
        raw(f"<strong>Not yet in this report:</strong> {escape('; '.join(not_yet))}"),
        class_="scope-note",
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
        # Each row carries id="issue-<n>" so the page-1 uncertainties link to it (R050, R060).
        rows.append(
            el("tr",
               el("td", item["number"], class_="open-number"),
               el("td", item["title"]),
               el("td", item["effect"]),
               el("td", item.get("resolves") or "Not stated"),
               el("td", label_chip(item["status_label"])),
               id=f"issue-{item['number']}")
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


def render(results: Mapping, ident: Mapping, *, maps_present: bool = False, env=None) -> str:
    # The shared assumptions (two columns) and the open-items table share one page,
    # so neither the table is split into a near-empty fragment nor a page is left
    # near-empty (correction 2). ``maps_present`` (from the builder) drops 'Context
    # maps' from the scope note when the report printed its maps; its default keeps
    # every other caller unchanged.
    children = [
        el("p", "Assumptions and open items", class_="type-name"),
        el("h2", QUESTION),
        _material_exclusions(results, maps_present=maps_present),
        el("h3", "Shared assumptions"),
        _assumptions(results),
        el("div", el("h3", "Open items"), _open_items(results), class_="open-items-block"),
    ]
    return str(el("section", *children, class_="report-page", id="assumptions-open-items"))
