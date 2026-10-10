"""Page type 6 - Calculations and evidence (page-types.md row 6).

The reader's question: How was this derived? The page carries the inputs with
readable source titles; the allowance figures as the document gives them, with
the rule sections linked to the official law; the provenance (revision, computed
date, rule versions); the drawing notes and map attributions; and the
status-label key. This is the ONLY place the word "Verified" appears.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import labels, readers, sources
from .components import short_line
from .html import el, escape, escape_attr, raw, table

__all__ = ["render"]

QUESTION = "How was this derived?"
_LAW_URL = "https://zoningresolution.planning.nyc.gov/"


def _law_links(zr_sections) -> object:
    parts = []
    for section in zr_sections or []:
        text = sources.readable_zr_reference(section)
        parts.append(f'<a href="{escape_attr(_LAW_URL)}">{escape(text)}</a>')
    return raw("; ".join(parts)) if parts else "See the official Zoning Resolution"


def _inputs(results: Mapping) -> object:
    seen: list[str] = []
    for name in readers.ANSWER_NAMES:
        for value in readers.present_values(readers.answer_block(results, name)):
            for source in value.get("sources", []) or []:
                if isinstance(source, Mapping):
                    title = sources.readable_source_title(source.get("kind"), source.get("ref"))
                    if title not in seen:
                        seen.append(title)
    if not seen:
        return short_line("No sources are recorded for this property.")
    return el("ul", *[el("li", title) for title in seen])


def _allowance_rows(results: Mapping) -> list[list[object]]:
    block = readers.answer_block(results, "floor_area_allowance")
    rows: list[list[object]] = []
    for value in readers.present_values(block):
        rows.append([value["label"], value["display"], _law_links(value.get("zr_sections"))])
    return rows


def _provenance(results: Mapping) -> object:
    prov = readers.provenance(results)
    items = []
    revision = prov.get("revision")
    if revision is not None:
        items.append(el("li", f"Results revision: {revision}"))
    computed = prov.get("computed_at")
    if computed:
        items.append(el("li", f"Computed: {str(computed).split('T', 1)[0]}"))
    for rule in prov.get("rule_versions", []):
        title = sources.readable_rule_title(rule.get("rule_id"))
        status = sources.readable_rule_status(rule.get("status"))
        items.append(el("li", f"{title} ({status})"))
    if not items:
        return short_line("No provenance is recorded for this property.")
    return el("ul", *items)


def _attributions(map_context) -> object:
    notes: list[str] = []
    if isinstance(map_context, Mapping):
        context = map_context.get("map_context")
        context = context if isinstance(context, Mapping) else {}
        for layer_name in ("zoning_districts", "building_footprints"):
            layer = context.get(layer_name)
            if isinstance(layer, Mapping):
                for field in ("attribution", "accuracy", "use_limitation"):
                    if layer.get(field):
                        notes.append(str(layer[field]))
    if not notes:
        return short_line("No drawing notes or map attributions in this report.")
    return el("ul", *[el("li", note) for note in notes])


def _label_key() -> object:
    rows = [[label, meaning] for label, meaning in labels.SIX_LABEL_DEFINITIONS]
    return table(["Label", "Meaning"], rows, caption="Status-label key", class_="key-table")


def render(results: Mapping, ident: Mapping, *, map_context=None, env=None) -> str:
    children = [
        el("h2", "Calculations and evidence"),
        el("p", QUESTION, class_="reader-question"),
        el("h3", "Inputs and sources"),
        _inputs(results),
        el("h3", "Floor-area allowance"),
        el("p", "The maximum residential floor area is the residential floor-area ratio applied "
                "to the recorded lot area; the figures below are read from the result."),
        table(["Figure", "Value", "Law"], _allowance_rows(results),
              caption="Floor-area allowance figures and their law sections"),
        el("h3", "Provenance"),
        _provenance(results),
        el("h3", "Drawing notes and map attributions"),
        _attributions(map_context),
        el("h3", "Status-label key"),
        _label_key(),
    ]
    return str(el("section", *children, class_="report-page", id="calculations-evidence"))
