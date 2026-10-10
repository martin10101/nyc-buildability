"""Page type 2 - Site and context (page-types.md row 2; rework F3-F6).

The page title is the reader's question. It leads with the lot-area basis stated
WITH the result it conditions (the document's own words after "holds "), the site
plan with one caption, and the constraints table with one row per constraint.
Context maps are not shown here (F3); the coverage inventory reports them.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import labels, readers
from .components import figure, label_chip, short_line
from .drawings_embed import Embedded
from .html import el, table

__all__ = ["render"]

QUESTION = "What constrains the design?"


def _lot_area_basis(results: Mapping) -> object:
    basis = readers.lot_area_basis(results)
    children = [el("h3", "Lot-area basis")]
    if basis:
        body = ("if " + basis[3:]) if basis[:3] == "If " else basis
        children.append(el("p", f"The floor-area allowance holds {body}"))
    else:
        children.append(short_line("The recorded lot area is not available for this property."))
    # The tax-map-outline caption is stated ONCE, below the drawing (D8); no line
    # is repeated above it here.
    return el("div", *children)


def _constraint_rows(results: Mapping, item_number: dict) -> list[list[object]]:
    rows: list[list[object]] = []
    env = readers.answer_block(results, "permitted_envelope")
    for value in readers.present_values(env):
        rows.append([value["label"], value["display"], label_chip(value["status_label"])])

    def see(category: str) -> str:
        number = item_number.get(category)
        return f" (see item {number})" if number else ""

    for withheld in readers.withheld_values(env):
        category = readers.category_for_key(withheld["key"])
        if category == "coverage":
            continue  # merged into the single coverage row below
        state = {"rear_yard": "Not known", "setback": "Not worked out yet"}.get(
            category, "Not shown"
        )
        rows.append(
            [withheld["label"], state + see(category), label_chip(withheld["status_label"])]
        )

    coverage = results.get("coverage_by_portion")
    if isinstance(coverage, Mapping) and coverage.get("status") == "withheld":
        # The full by-portion sentence is stated once, as the open item's detail on
        # the assumptions page; this cell is a short state that points to it (V-C2).
        rows.append([
            coverage.get("label") or "Maximum lot coverage",
            f"Not a single figure; by portion{see('coverage')}",
            label_chip(labels.UNRESOLVED),
        ])
    rows.append(["Street wall", "Not checked" + see("street_wall"),
                 label_chip(labels.PENDING_VERIFICATION)])
    return rows


def _site_outline(results: Mapping, site_plan: Embedded) -> object:
    if not readers.geometry_available(results):
        return short_line("The lot outline is not available for this property.")
    # The drawing is in its own block with space above (D7). ONE caption for the
    # tax-map-outline fact, below the drawing: the report adds none, so the single
    # caption is the kit's own "Lot outline: Approximate - tax map" inside the SVG
    # (D8). No line is repeated above the drawing.
    return figure(site_plan, "")


def _maps(maps: list[Embedded]) -> list[object]:
    """A context-maps section ONLY when a map document rendered (Q3); no empty
    section otherwise."""
    if not maps:
        return []
    out: list[object] = [el("h3", "Context maps")]
    for drawing in maps:
        out.append(figure(drawing, drawing.caption or "Context map"))
    return out


def render(
    results: Mapping, ident: Mapping, *, site_plan: Embedded,
    maps: list[Embedded] | None = None, env=None,
) -> str:
    item_number = {item["category"]: item["number"] for item in readers.open_items(results)}
    children = [
        el("p", "Site and context", class_="type-name"),
        el("h2", QUESTION),
        _lot_area_basis(results),
        _site_outline(results, site_plan),
        el("h3", "Constraints"),
        table(
            ["Constraint", "State", "Status"],
            _constraint_rows(results, item_number),
            caption="Zoning constraints for this lot",
        ),
        *_maps(maps or []),
    ]
    return str(el("section", *children, class_="report-page", id="site-and-context"))
