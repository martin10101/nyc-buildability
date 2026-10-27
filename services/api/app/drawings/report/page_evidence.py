"""The evidence appendix - page types 5 and 6 merged into ONE clearly-named section
(page-types.md rows 5/6; D-094 R077, merged M5-T169).

The appendix answers "what remains unresolved, and how was this derived?". At its head
the compact scope note (every material exclusion), then the shared assumptions and the
five-field issue records (:mod:`.page_assumptions`); then the inputs with their basis
in plain words and real source identifiers and dates, the worked arithmetic from the
document's values, the rule sections with links and each result's review-register entry
and review state, the area-illustration method when the document carries an
``area_allocation`` block, the run identity (fingerprint, code commit, revision) and the
status-label key printed once (the ONLY place "Verified" appears). No explanation is
printed twice (R077).
"""

from __future__ import annotations

from collections.abc import Mapping

from . import (
    labels,
    law_links,
    map_caption,
    open_items,
    page_assumptions,
    readers,
    run_identity,
    sources,
)
from .components import short_line
from .html import el, escape, escape_attr, raw, table

__all__ = ["render"]

QUESTION = "What remains unresolved, and how was this derived?"


def _law_links(zr_sections) -> object:
    parts = []
    for section in zr_sections or []:
        number = sources.zr_section_number(section)
        # The section number never breaks across a line (A7).
        if number:
            label = (f'New York City Zoning Resolution, Section '
                     f'<span class="nowrap">{escape(number)}</span>')
        else:
            label = escape(sources.LAW_SITE_TITLE)
        # Link only to the exact captured section URL; a section with no capture
        # prints as plain text (never a guessed URL, never the homepage) - D-094 R027.
        url = law_links.section_url(section)
        if url:
            parts.append(f'<a href="{escape_attr(url)}">{label}</a>')
        else:
            parts.append(label)
    return raw("; ".join(parts)) if parts else "See the official Zoning Resolution"


def _nowrap(text: object) -> raw:
    return raw(f'<span class="nowrap">{escape(text)}</span>')


def _inputs(results: Mapping) -> object:
    """The inputs with their basis and real sources (R026): on a 1.5.0 document the
    measured ``input_facts`` with the nine-bases plain words and each fact's source
    title and date. The categorical reads (district, overlay, lot type, frontage, depth,
    program, floor-to-floor) are NOT re-listed here - they are stated once in the Shared
    assumptions above, so the appendix carries no repeated explanation (R077). A 1.4.0
    document (no input_facts) falls back to the scope-assumption inputs."""
    fact_rows = [[row["name"], _nowrap(row["value"]), row["basis"], row["source"]]
                 for row in open_items.input_fact_rows(results)]
    if fact_rows:
        return table(["Input", "Value", "Basis", "Source"], fact_rows,
                     caption="Inputs and their sources")
    scope_rows = [[row["name"], _nowrap(row["value"]), row["basis"]]
                  for row in readers.input_rows(results)]
    if not scope_rows:
        return short_line("No inputs are recorded for this property.")
    return table(["Input", "Value", "Source"], scope_rows, caption="Inputs and their sources")


def _worked_arithmetic(results: Mapping) -> object | None:
    rows = open_items.worked_arithmetic(results)
    if not rows:
        return None
    items = [el("li", raw(f"<strong>{escape(row['name'])}:</strong> {escape(row['expression'])}"))
             for row in rows]
    return el("div", el("h3", "Worked arithmetic"), el("ul", *items))


def _figure_rows(results: Mapping, name: str) -> list[list[object]]:
    return [
        [row["label"], _nowrap(row["display"]), _law_links(row.get("zr_sections"))]
        for row in readers.present_values(readers.answer_block(results, name))
    ]


def _rules_and_review(results: Mapping) -> object:
    """Each rule version mapped to its existing review-register entry and review state
    (R027), plus the label-basis note. The register is read, never written (G-11)."""
    items = []
    for row in open_items.register_rule_rows(results):
        items.append(el("li", f"{row['title']} - review: {row['review_state']}"))
    meta = readers.label_meta_statement(results)
    if meta:
        items.append(el("li", meta))
    if not items:
        return short_line("No rules are recorded for this property.")
    return el("ul", *items)


def _run_identity(results: Mapping, *, commit: str | None = None) -> object:
    """The run identity (R028/R038) as an appendix COLUMN: the document fingerprint
    (stable for the same document, changing with any value), the deployed code commit,
    the result revision and the computed date. ``commit`` is the value the route carries
    (report_read.py); when absent the deployed commit is read from the environment
    ("unknown" when unset)."""
    ident = run_identity.run_identity(results, commit=commit)
    items = [
        el("li", f"Document fingerprint: {ident['fingerprint']}"),
        el("li", f"Code commit: {ident['commit']}"),
    ]
    if ident.get("revision") is not None:
        items.append(el("li", f"Results revision: {ident['revision']}"))
    if ident.get("computed_at"):
        items.append(el("li", f"Computed: {str(ident['computed_at']).split('T', 1)[0]}"))
    return el("div", el("h3", "Run identity"), el("ul", *items), class_="evidence-column")


_G14_CONVERSION = ("plate = zoning floor area per storey; no gross-up, exclusions or "
                   "wall-thickness conversion worked")


def _area_allocation(results: Mapping) -> Mapping | None:
    for building in results.get("building_alternatives", []) or []:
        block = building.get("area_allocation") if isinstance(building, Mapping) else None
        if isinstance(block, Mapping) and block:
            return block
    return None


def _area_illustration_drawing_clause(results: Mapping, illustration_state: str | None,
                                      how: str) -> str:
    """The one drawing clause of the method sentence, decided ONLY from the drawn-content
    manifest's ``area_illustration_state`` (M5-T173 part B4): ``'zones'`` / ``'bar'`` name
    WHERE the illustration is drawn on the scenario sheet; ``None`` (an unwired caller) or
    any other not-drawn state gives the not-yet-drawn clause. There is no hard-coded
    constant and no legacy predicate: a page states a drawn claim only from rendered
    content, never a guess."""
    if illustration_state == "zones":
        return "it is shown as zones inside the placed building footprint on the scenario sheet"
    if illustration_state == "bar":
        return "it is shown as a proportional bar on the scenario sheet"
    return f"it is not yet drawn in this report; when drawn it will be shown {how}"


def _area_illustration_method(results: Mapping,
                              illustration_state: str | None = None) -> object | None:
    """The area-illustration METHOD (R095/R092), once, when the document carries an
    ``area_allocation`` block: the stated share, the measure, the G-14 conversion
    statement, and the bar-or-zones rule. Absent when there is no block (the benchmark
    until M5-T172), so the appendix is byte-identical then.

    The method's facts (the share, the measure, the conversion statement) are honest on
    their own, so the block is KEPT; only the drawing clause is made honest (S14):
    :func:`_area_illustration_drawing_clause` decides it from ``illustration_state`` (the
    drawn-content manifest), never the present-tense 'it is shown' unless the illustration
    is actually drawn, which would send a reader hunting for a figure not in the report."""
    block = _area_allocation(results)
    if block is None:
        return None
    share = block.get("share")
    measure = "residential floor area" if block.get("measure") == "residential_floor_area" \
        else str(block.get("measure") or "the building's floor area")
    how = ("as zones inside the placed building footprint" if block.get("fitted")
           else "as a proportional bar beside the building diagram, not yet fitted")
    drawing = _area_illustration_drawing_clause(results, illustration_state, how)
    sentence = (
        f"The area illustration applies one preliminary share ({share}) of the {measure} "
        f"to split apartment area from other area; {drawing}. "
        f"It is illustrative ({block.get('label') or labels.ILLUSTRATIVE}) and rests on no "
        f"reviewed rule of its own. "
        f"The plate measure is stated as: {_G14_CONVERSION}."
    )
    return el("div", el("h3", "Area-illustration method"), el("p", sentence))


_SURVEY_NOTE = (
    "Map geometry only; tax boundaries do not establish the legal zoning lot; "
    "nothing is surveyed."
)


def _attributions(map_context) -> list[str]:
    """The map sources in plain words - a readable title and its edit date once per
    layer shown (ruling Y7/X6), then the honesty note. No dataset id, no "via NYC
    Open Data" phrase and no terms-of-use text (rework 1 fix 3)."""
    if not isinstance(map_context, Mapping):
        return []
    lines = map_caption.source_lines(map_context, map_caption.SITE_LAYERS)
    if not lines:
        return []
    return [*lines, _SURVEY_NOTE]


def _label_key() -> object:
    # No caption: the 'Status-label key' h3 already names it (R049, no caption
    # duplicating a section title).
    rows = [[label, meaning] for label, meaning in labels.SIX_LABEL_DEFINITIONS]
    return table(["Label", "Meaning"], rows, class_="key-table")


def render(results: Mapping, ident: Mapping, *, maps_present: bool = False,
           map_context=None, env=None, commit: str | None = None,
           illustration_state: str | None = None) -> str:
    children: list[object] = [
        el("p", "Appendix", class_="type-name"),
        el("h2", QUESTION),
        page_assumptions.material_exclusions(results, maps_present=maps_present),
        el("h3", "Shared assumptions"),
        page_assumptions.shared_assumptions(results),
        el("div", el("h3", "Open items"), page_assumptions.open_items_table(results),
           class_="open-items-block"),
        el("h3", "Inputs and sources"),
        _inputs(results),
    ]
    worked = _worked_arithmetic(results)
    if worked is not None:
        children.append(worked)
    # The floor-area allowance and permitted-envelope figures share one table (one
    # heading, one caption - R049, R077), each row naming its own law section.
    figure_rows = (_figure_rows(results, "floor_area_allowance")
                   + _figure_rows(results, "permitted_envelope"))
    children += [
        el("h3", "Figures and their law sections"),
        table(["Figure", "Value", "Law"], figure_rows,
              caption="Allowance and envelope figures and their law sections"),
    ]
    # Rules/review, drawing notes and run identity sit side by side so the appendix
    # stays compact (R077, DB-270: the appendix fits fewer pages).
    columns = [el("div", el("h3", "Rules and their review state"), _rules_and_review(results),
                  class_="evidence-column")]
    attributions = _attributions(map_context)
    if attributions:
        columns.append(el("div",
            el("h3", "Drawing notes and map attributions"),
            el("ul", *[el("li", note) for note in attributions]),
            class_="evidence-column"))
    columns.append(_run_identity(results, commit=commit))
    children.append(el("div", *columns, class_="evidence-columns"))
    method = _area_illustration_method(results, illustration_state)
    if method is not None:
        children.append(method)
    children.append(el("h3", "Status-label key"))
    children.append(_label_key())
    return str(el("section", *children, class_="report-page", id="appendix"))
