"""Page type 2 - Site and context (page-types.md row 2).

The reader's question: What constrains the design? The page leads with the
lot-area basis in the document's own words (the recorded lot area used in the
calculations and the tax-map outline the drawing shows, and that they disagree),
then the site plan, the constraints table (coverage, yards, heights and
setbacks, street walls, each with its state), and the maps when a map document
is given - otherwise one short line.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import labels, readers
from .components import figure, label_chip, short_line
from .drawings_embed import Embedded
from .html import el, table

__all__ = ["render"]

QUESTION = "What constrains the design?"
SITE_PLAN_CAPTION = "The site plan shows the lot's approximate tax-map outline (city records)."


def _lot_area_basis(results: Mapping) -> object:
    text = readers.lot_area_basis(results)
    children = [el("h3", "Lot-area basis")]
    if text:
        children.append(el("p", text))
    else:
        children.append(short_line("The recorded lot area is not available for this property."))
    children.append(el("p", SITE_PLAN_CAPTION, class_="figure-note"))
    return el("div", *children)


def _constraint_rows(results: Mapping) -> list[list[object]]:
    rows: list[list[object]] = []
    env = readers.answer_block(results, "permitted_envelope")
    for value in readers.present_values(env):
        rows.append([value["label"], value["display"], label_chip(value["status_label"])])
    for withheld in readers.withheld_values(env):
        rows.append([withheld["label"], "Not shown", label_chip(withheld["status_label"])])
    coverage = results.get("coverage_by_portion")
    if isinstance(coverage, Mapping) and coverage.get("status") == "withheld":
        rows.append(
            [
                coverage.get("label") or "Maximum lot coverage",
                "By portion; not a single figure",
                label_chip(labels.label_for_value_state(coverage)),
            ]
        )
    rows.append(["Street wall", "Not checked", label_chip(labels.PENDING_VERIFICATION)])
    return rows


def _site_outline(results: Mapping, site_plan: Embedded) -> object:
    if not readers.geometry_available(results):
        return short_line("The lot outline is not available for this property.")
    return figure(site_plan, SITE_PLAN_CAPTION)


def _maps(location_map: Embedded, zoning_map: Embedded) -> list[object]:
    out: list[object] = [el("h3", "Context maps")]
    any_map = False
    for drawing, name in ((zoning_map, "Zoning map"), (location_map, "Location map")):
        if drawing.is_drawing:
            any_map = True
            out.append(figure(drawing, name))
    if not any_map:
        out.append(short_line("Context maps are not included in this report."))
    return out


def render(
    results: Mapping,
    ident: Mapping,
    *,
    site_plan: Embedded,
    location_map: Embedded,
    zoning_map: Embedded,
    env=None,
) -> str:
    children = [
        el("h2", "Site and context"),
        el("p", QUESTION, class_="reader-question"),
        _lot_area_basis(results),
        _site_outline(results, site_plan),
        el("h3", "Constraints"),
        table(
            ["Constraint", "State", "Status"],
            _constraint_rows(results),
            caption="Zoning constraints for this lot",
        ),
        *_maps(location_map, zoning_map),
    ]
    return str(el("section", *children, class_="report-page", id="site-and-context"))
