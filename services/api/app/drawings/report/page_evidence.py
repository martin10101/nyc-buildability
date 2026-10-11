"""Page type 6 - Calculations and evidence (page-types.md row 6; rework F11).

The page title is the reader's question. It carries the inputs as a table, the
allowance and envelope figures with their own law sections, the provenance
(revision, computed date, rule versions and the label-basis note), the drawing
notes and map attributions when there are any, and the status-label key in the
owner's own words (the ONLY place "Verified" appears).
"""

from __future__ import annotations

from collections.abc import Mapping

from . import labels, map_caption, readers, sources
from .components import short_line
from .html import el, escape, escape_attr, raw, table

__all__ = ["render"]

QUESTION = "How was this derived?"
_LAW_URL = "https://zoningresolution.planning.nyc.gov/"


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
        parts.append(f'<a href="{escape_attr(_LAW_URL)}">{label}</a>')
    return raw("; ".join(parts)) if parts else "See the official Zoning Resolution"


def _nowrap(text: object) -> raw:
    return raw(f'<span class="nowrap">{escape(text)}</span>')


def _inputs(results: Mapping) -> object:
    rows = readers.input_rows(results)
    if not rows:
        return short_line("No inputs are recorded for this property.")
    table_rows = [[row["name"], _nowrap(row["value"]), row["basis"]] for row in rows]
    return table(["Input", "Value", "Source"], table_rows, caption="Inputs and their sources")


def _figure_rows(results: Mapping, name: str) -> list[list[object]]:
    return [
        [row["label"], _nowrap(row["display"]), _law_links(row.get("zr_sections"))]
        for row in readers.present_values(readers.answer_block(results, name))
    ]


def _provenance(results: Mapping) -> object:
    prov = readers.provenance(results)
    items = []
    if prov.get("revision") is not None:
        items.append(el("li", f"Results revision: {prov['revision']}"))
    if prov.get("computed_at"):
        items.append(el("li", f"Computed: {str(prov['computed_at']).split('T', 1)[0]}"))
    for rule in prov.get("rule_versions", []):
        title = sources.readable_rule_title(rule.get("rule_id"))
        status = sources.readable_rule_status(rule.get("status"))
        items.append(el("li", f"{title} ({status})"))
    meta = readers.label_meta_statement(results)
    if meta:
        items.append(el("li", meta))
    if not items:
        return short_line("No provenance is recorded for this property.")
    return el("ul", *items)


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
    rows = [[label, meaning] for label, meaning in labels.SIX_LABEL_DEFINITIONS]
    return table(["Label", "Meaning"], rows, caption="Status-label key", class_="key-table")


def render(results: Mapping, ident: Mapping, *, map_context=None, env=None) -> str:
    children = [
        el("p", "Calculations and evidence", class_="type-name"),
        el("h2", QUESTION),
        el("h3", "Inputs and sources"),
        _inputs(results),
        el("h3", "Floor-area allowance"),
        table(["Figure", "Value", "Law"], _figure_rows(results, "floor_area_allowance"),
              caption="Floor-area allowance figures and their law sections"),
        el("h3", "Permitted envelope"),
        table(["Figure", "Value", "Law"], _figure_rows(results, "permitted_envelope"),
              caption="Envelope figures and their law sections"),
    ]
    # Provenance and the drawing notes sit side by side in two columns, so this page
    # is compact enough to hold the status-label key and the key is never orphaned on
    # a near-empty last page (corrections T156-C1).
    columns = [el("div", el("h3", "Provenance"), _provenance(results), class_="evidence-column")]
    attributions = _attributions(map_context)
    if attributions:
        columns.append(el("div",
            el("h3", "Drawing notes and map attributions"),
            el("ul", *[el("li", note) for note in attributions]),
            class_="evidence-column"))
    children.append(el("div", *columns, class_="evidence-columns"))
    children.append(el("h3", "Status-label key"))
    children.append(_label_key())
    return str(el("section", *children, class_="report-page", id="calculations-evidence"))
