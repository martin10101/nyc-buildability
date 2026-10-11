"""Page type 2 - Site and context (page-types.md row 2; rework F3-F6; M5-T156).

The page opens with the 'Where is the lot?' sheet (the neighbourhood map and the
block close-up, ruling Y10), then the 'What constrains the design?' sheet: the
lot-area basis stated WITH the result it conditions (the document's own words
after "holds "), the site plan among its surroundings, the document's own reason
that no building is placed yet (ruling Y8), and the constraints table. The
page-type list stays at six - the location sheet lives inside this one page type.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import labels, page_location, readers
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
    # The drawing is in its own block with space above (D7). When the surroundings
    # are shown this is the map-based site plan among them, captioned by the map's
    # own sources and dates (Y7); otherwise it is today's lot-only plan, whose one
    # caption is the kit's own "Lot outline: Approximate - tax map" inside the SVG
    # (D8). Only one of the two outlines is ever drawn (Y5).
    return figure(site_plan, site_plan.caption or "")


def _not_placed(results: Mapping) -> list[object]:
    """One plain sentence whenever the results document gives no floor plate (Y8);
    no building footprint, outline or 3D view is drawn. The document's reason text
    is never spliced in."""
    if not readers.building_not_placed(results):
        return []
    return [short_line(readers.NOT_PLACED_LINE)]


def render(
    results: Mapping, ident: Mapping, *, site_plan: Embedded,
    surroundings: page_location.Surroundings | None = None, env=None,
) -> str:
    item_number = {item["category"]: item["number"] for item in readers.open_items(results)}
    children: list[object] = [el("p", "Site and context", class_="type-name")]
    if surroundings is not None:
        # The location sheet opens page type 2 (ruling Y10).
        children.append(page_location.render(surroundings))
    # The 'What constrains the design?' sheet follows, on its own printed page.
    children.append(el("div",
        el("h2", QUESTION),
        _lot_area_basis(results),
        _site_outline(results, site_plan),
        *_not_placed(results),
        el("h3", "Constraints"),
        table(
            ["Constraint", "State", "Status"],
            _constraint_rows(results, item_number),
            caption="Zoning constraints for this lot",
        ),
        class_="constraints-sheet",
    ))
    return str(el("section", *children, class_="report-page", id="site-and-context"))
