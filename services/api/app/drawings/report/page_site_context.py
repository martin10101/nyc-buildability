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

from . import constraint_text, labels, law_links, page_location, readers
from .components import figure, label_chip, short_line
from .drawings_embed import Embedded
from .html import el, escape, escape_attr, raw, table

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


_QUALIFYING_SUFFIX = "_qualifying_affordable_or_senior"


def _height_pairs(env: Mapping) -> list[tuple[dict, dict | None]]:
    """The shown height values paired as (standard, qualifying-housing) by key, in
    document order. A standard value with no qualifying counterpart pairs with
    ``None`` (the qualifying cell then reads '—')."""
    present = {v["key"]: v for v in readers.present_values(env)}
    pairs: list[tuple[dict, dict | None]] = []
    for key, value in present.items():
        if key.endswith(_QUALIFYING_SUFFIX):
            continue
        pairs.append((value, present.get(key + _QUALIFYING_SUFFIX)))
    return pairs


def _heights_table(results: Mapping) -> object | None:
    """The compact 3x2 standard / qualifying-housing heights table (D-094 R016):
    one row per base height metric, its labels taken from the document, the standard
    and qualifying-housing figures side by side with their status. ``None`` when the
    envelope shows no height values."""
    env = readers.answer_block(results, "permitted_envelope")
    pairs = _height_pairs(env)
    if not pairs:
        return None
    body: list[list[object]] = []
    for standard, qualifying in pairs:
        qual_cell = qualifying["display"] if qualifying else "—"
        body.append([standard["label"], standard["display"], qual_cell,
                     label_chip(standard["status_label"])])
    return table(
        ["Height limit", "Standard", "Qualifying housing", "Status"],
        body,
        caption="Height limits for this lot",
    )


# The page-3 constraint titles for the 1.5.0 envelope rows (the row's kind -> the
# title the constraints table shows; the rear-yard combined row is "Rear yard").
_ENVELOPE_TITLES = {
    "setback": "Setback above the base",
    "street_wall": "Street wall",
    "side_yard": "Side yard",
}
# The envelope-row kind -> the open-item category whose numbered record the row
# links to (`#issue-<n>`); a kind with no open-item category carries no link.
_ENVELOPE_CATEGORY = {"setback": "setback", "street_wall": "street_wall"}


def _issue_link(category: str | None, item_number: dict) -> raw:
    """The 'see item N' reference as a link to the open item's `#issue-<n>` anchor
    on the appendix (D-094 R060), or empty markup when the category has no numbered
    open item. The 1.4.0 fall-back keeps the plain-text reference (byte-identical)."""
    number = item_number.get(category) if category else None
    if not number:
        return raw("")
    return raw(f' (<a href="#issue-{escape_attr(number)}">see item {number}</a>)')


def _zr_section_links(sections: object) -> list[object]:
    """Each ZR section as a link to its captured official text (law_links), or the
    plain section text when no capture exists; never a reconstructed URL."""
    parts: list[object] = []
    for section in sections or []:
        url = law_links.section_url(str(section))
        if url:
            parts.append(raw(f' <a href="{escape_attr(url)}">{escape(section)}</a>'))
        else:
            parts.append(raw(f" {escape(section)}"))
    return parts


def _reading_cell(text: object, sections: object, category: str | None,
                  item_number: dict) -> raw:
    """A 1.5.0 constraint row's State cell: the row's OWN draft text, its ZR
    section links, and the link to its numbered open item. It carries no number
    (the engine's rows never do)."""
    children: list[object] = [el("span", str(text or ""))]
    children += _zr_section_links(sections)
    children.append(_issue_link(category, item_number))
    return el("span", *children)


def _envelope_label(row: Mapping) -> str:
    """The label chip for a 1.5.0 envelope row (a labelled draft reading, never a
    DOB determination, so never Verified): a not_known row is Pending verification;
    a row resting on assumptions is Conditional; a plain applies/not_applicable
    reading is Provisional (prepared, subject to confirmation)."""
    if row.get("state") == "not_known":
        return labels.PENDING_VERIFICATION
    if row.get("conditions"):
        return labels.CONDITIONAL
    return labels.PROVISIONAL


def _constraint_rows_from_results(results: Mapping, item_number: dict) -> list[list[object]]:
    """The page-3 constraint rows read from the results contract 1.5.0 blocks
    (D-094 R037/R038/R079): the rear-yard combined row and the envelope rows show
    the engine's OWN state/way/text, their ZR sections linked and their numbered
    open item linked; the coverage row is unchanged."""
    rows: list[list[object]] = []
    combined = constraint_text.rear_yard_combined(results)
    if combined is not None:
        # The rear yard reads the combined row: its own text, labelled by its way
        # (a conditional reading is Conditional), ZR 23-344 linked; no number (R037).
        rows.append([
            "Rear yard",
            _reading_cell(combined.get("text"), combined.get("zr_sections"), "rear_yard",
                          item_number),
            label_chip(labels.label_for_way(combined.get("way"))),
        ])
    for kind in ("setback", "street_wall", "side_yard"):
        row = constraint_text.envelope_row(results, kind)
        if row is None:
            continue
        rows.append([
            _ENVELOPE_TITLES[kind],
            _reading_cell(row.get("text"), row.get("zr_sections"),
                          _ENVELOPE_CATEGORY.get(kind), item_number),
            label_chip(_envelope_label(row)),
        ])
    coverage = results.get("coverage_by_portion")
    if isinstance(coverage, Mapping) and coverage.get("status") == "withheld":
        rows.append([
            coverage.get("label") or "Maximum lot coverage",
            el("span", "Not a single figure; by portion", _issue_link("coverage", item_number)),
            label_chip(labels.UNRESOLVED),
        ])
    return rows


def _constraint_rows(results: Mapping, item_number: dict) -> list[list[object]]:
    # A document carrying the results contract 1.5.0 rear_yard / envelope blocks
    # reads the engine's own rows (fix the data path, D-094 R038); a 1.4.0 (and
    # earlier) document falls back to today's output UNCHANGED (S1, byte-identical).
    if constraint_text.has_results_rows(results):
        return _constraint_rows_from_results(results, item_number)

    rows: list[list[object]] = []
    env = readers.answer_block(results, "permitted_envelope")

    def see(category: str) -> str:
        number = item_number.get(category)
        return f" (see item {number})" if number else ""

    for withheld in readers.withheld_values(env):
        category = readers.category_for_key(withheld["key"])
        if category == "coverage":
            continue  # merged into the single coverage row below
        state = constraint_text.PAGE3_FALLBACK_STATE.get(
            category, constraint_text.PAGE3_DEFAULT_STATE
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


def render(
    results: Mapping, ident: Mapping, *, site_plan: Embedded,
    surroundings: page_location.Surroundings | None = None, env=None,
) -> str:
    item_number = {item["category"]: item["number"] for item in readers.open_items(results)}
    children: list[object] = [el("p", "Site and context", class_="type-name")]
    if surroundings is not None:
        # The location sheet opens page type 2 (ruling Y10).
        children.append(page_location.render(surroundings))
    # The 'What constrains the design?' sheet follows, on its own printed page. The
    # 'No building placed' state is a legend entry on the close frame now (M5-T166 S8);
    # the plain not-placed sentence stays on the scenario sheet only.
    # Order (rework 3 addition). The close frame cannot be shrunk below ~416 pt without
    # a dimension label falling under 8.5 pt, and the section's content (lot-area basis,
    # two tables, the large frame) totals more than one A4 page, so the frame cannot
    # share a page with every table. Printed frame-first (contract order), the 4-row
    # constraint table lands ALONE on an otherwise blank page after the frame. So the
    # section is reordered (the addition's sanctioned alternative): the two constraint
    # tables sit together with the lot-area basis, and the large frame - the page's
    # dominant visual - takes the next page; no block is left alone on a blank page.
    constraints_block: list[object] = [el("h2", QUESTION), _lot_area_basis(results)]
    heights = _heights_table(results)
    if heights is not None:
        constraints_block += [el("h3", "Height limits"), heights]
    constraints_block += [
        el("h3", "Constraints"),
        table(
            ["Constraint", "State", "Status"],
            _constraint_rows(results, item_number),
            caption="Zoning constraints for this lot",
        ),
        _site_outline(results, site_plan),
    ]
    children.append(el("div", *constraints_block, class_="constraints-sheet"))
    return str(el("section", *children, class_="report-page", id="site-and-context"))
