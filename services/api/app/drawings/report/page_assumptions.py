"""Appendix fragments: the scope note, the shared assumptions and the five-field
issue records (page-types.md row 5; merged into the one evidence appendix, M5-T169).

Page types 5 and 6 now print under one appendix heading (D-094 R077); this module
no longer renders a whole page. It provides the appendix's "what remains unresolved"
fragments, which :mod:`.page_evidence` assembles with the derivation evidence into one
section. The open items are five-field issue records - issue, consequence, next action,
responsible role, evidence reference (R025) - and each row keeps ``id="issue-<n>"`` so
the page-1 and page-3 "see item N" links resolve (R050/R060).
"""

from __future__ import annotations

from collections.abc import Mapping

from . import coverage, open_items, readers
from .components import short_line
from .html import el, escape, raw

__all__ = ["material_exclusions", "open_items_table", "shared_assumptions"]


def material_exclusions(results: Mapping, *, maps_present: bool = False) -> object:
    """The compact scope note at the head of the appendix (D-094 R012): every
    material exclusion, i.e. the sections the report does not yet cover. 'Context
    maps' is excluded only when the report does not print its maps."""
    groups = dict(coverage.coverage_groups(results, maps_present=maps_present))
    not_yet = groups.get("Not yet", [])
    if not not_yet:
        return el("p", "This report covers every promised section.", class_="scope-note")
    return el(
        "p",
        raw(f"<strong>Not yet in this report:</strong> {escape('; '.join(not_yet))}"),
        class_="scope-note",
    )


def shared_assumptions(results: Mapping) -> object:
    statements = readers.assumptions(results)
    if not statements:
        return short_line("No shared assumptions are recorded for this property.")
    return el("ol", *[el("li", statement) for statement in statements])


def open_items_table(results: Mapping) -> object:
    """The open items as five-field issue records (R025): issue, consequence, next
    action, responsible role, evidence reference. Each row carries ``id="issue-<n>"``
    so the page-1 uncertainties and the page-3 "see item N" links resolve (R050/R060).
    Missing site documents carry the owner/surveyor role, program work the program's;
    the honest "A check not yet made ..." next action prints at most once (R054)."""
    records = open_items.appendix_issue_records(results)
    if not records:
        return short_line("No open items are recorded for this property.")
    header = el(
        "thead",
        el("tr", el("th", "#"), el("th", "Issue"), el("th", "Consequence"),
           el("th", "Next action"), el("th", "Responsible role"),
           el("th", "Evidence reference")),
    )
    rows: list[object] = []
    for record in records:
        rows.append(
            el("tr",
               el("td", record["number"], class_="open-number"),
               el("td", record["issue"]),
               el("td", record["consequence"]),
               el("td", record["next_action"]),
               el("td", record["responsible_role"]),
               el("td", record["evidence_reference"]),
               id=f"issue-{record['number']}")
        )
        # The material document reason sits beneath the row when it adds information
        # beyond the consequence or the title (R025); it is never a repeat (A3).
        if record.get("detail"):
            rows.append(el("tr", el("td", record["detail"], colspan="6"), class_="reason-row"))
    return el(
        "table",
        el("caption", "Open items for this property"),
        header,
        el("tbody", *rows),
    )
