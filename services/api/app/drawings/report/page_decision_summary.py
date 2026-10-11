"""Page type 1 - Decision summary (D-094 change of 2026-10-11; page-types.md row 1).

Four kinds of content and nothing else, plus the contract's named furniture:

1. the results in large type, each with its assumption line, and the allowance
   phrase beside the headline (R029, R055);
2. one site graphic (the existing compact summary frame, wrapper unchanged);
3. the legal ceiling beside the apartment estimate, side by side and distinct, with
   the distinction line read from the presentation tokens; the estimate links to its
   full calculation on the scenario sheet (R071, R078);
4. at most three uncertainties - zoning lot, lot-area basis, rear yard - each one
   line linked to its issue record (R050), the rear yard worded as the open check.

The coverage inventory has left the report (owner update only, R012); a compact
scope line points to the material-exclusions block at the head of the appendix. The
property-specific zoning-lot sentence names the register's index entry (R030); the
generic sentence shows only when no such condition exists.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.drawings.kit.presentation_tokens import WORDING

from . import (
    constraint_text,
    drawings_embed,
    labels,
    law_links,
    readers,
    unit_limit_text,
    zoning_lot_item,
)
from .components import figure, label_chip
from .html import el, escape, escape_attr, raw

__all__ = ["render"]

QUESTION = "What can I potentially build?"

# R029: the allowance phrase beside the headline whenever the zoning lot is not
# confirmed, with the figure from the result. Quoted once here; it is NOT in the
# token wording group (that group holds the distinction line, the zone labels and
# the area-illustration caption, G-15).
_ALLOWANCE_PHRASE = (
    "{allowance} is a conditional tax-lot-only arithmetic allowance, not established "
    "remaining development rights."
)


def _property_heading(results: Mapping, ident: Mapping) -> raw:
    display = ident.get("display")
    address = ident.get("address")
    title = address or display or "Selected tax lot"
    lines = [el("p", "Decision summary", class_="type-name"), el("h1", title)]
    if address and display:
        lines.append(el("p", display, class_="identity-line"))
    zoning = ident.get("zoning_line")
    if zoning:
        lines.append(el("p", zoning, class_="identity-line"))
    # The property-specific zoning-lot sentence names the register's INDEX ENTRY
    # (R030); the generic "the app does not verify the zoning lot" line shows ONLY
    # when no such condition exists (S2), and then once.
    zl_sentence = zoning_lot_item.page_one_zoning_lot_sentence(results)
    if zl_sentence:
        lines.append(el("p", zl_sentence, class_="identity-line"))
    elif ident.get("lot_selection"):
        lines.append(el("p", ident["lot_selection"], class_="identity-line"))
    return el("div", *lines)


def _answer_cell(figure_text: str | None, basis: str | None, extra: str | None = None) -> raw:
    value = figure_text if figure_text is not None else "Not available"
    children: list[object] = [el("div", value, class_="answer-figure")]
    if basis:
        children.append(el("div", basis, class_="identity-line"))
    if extra:
        children.append(el("p", extra, class_="allowance-phrase"))
    return el("div", *children)


def _floor_area_basis(results: Mapping, ident: Mapping, far_disp: str | None) -> str:
    """The floor-area allowance assumption line (R055): the recorded lot area, the
    FAR and the tax-lot scope, every value read from the document. 'alone' is added
    only while the zoning lot is not confirmed."""
    recorded = readers.recorded_lot_area_text(results)
    lot = ident.get("lot")
    if not (recorded and far_disp and lot):
        return "Residential FAR on the recorded lot area"
    unconfirmed = readers.zoning_lot_basis(results) is not None
    tax_clause = f"tax lot {lot} alone" if unconfirmed else f"tax lot {lot}"
    return f"{recorded} recorded lot area × FAR {far_disp}, {tax_clause}"


def _answers_table(results: Mapping, ident: Mapping) -> raw:
    fa = readers.answer_block(results, "floor_area_allowance")
    far = readers.named_value(fa, "max_residential_far")
    area = readers.named_value(fa, "max_residential_floor_area")
    allowance_text = None
    allowance_label = labels.PENDING_VERIFICATION
    allowance_phrase = None
    if area is not None:
        allowance_text = area["display"]
        if far and far.get("display"):
            allowance_text = f"{allowance_text} (FAR {far['display']})"
        allowance_label = area["status_label"]
        if readers.zoning_lot_basis(results) is not None:
            allowance_phrase = _ALLOWANCE_PHRASE.format(allowance=area["display"])
    fa_basis = _floor_area_basis(results, ident, far.get("display") if far else None)

    envelope_block = readers.answer_block(results, "permitted_envelope")
    min_base = readers.named_value(envelope_block, "min_base_height")
    max_base = readers.named_value(envelope_block, "max_base_height")
    max_building = readers.named_value(envelope_block, "max_building_height")
    envelope_text = None
    envelope_label = labels.PENDING_VERIFICATION
    if max_building is not None:
        parts = []
        if min_base and max_base:
            parts.append(f"Base {min_base['display']} to {max_base['display']}")
        parts.append(f"building up to {max_building['display']}")
        envelope_text = "; ".join(parts)
        envelope_label = max_building["status_label"]
    district = ident.get("district")
    envelope_basis = f"{district} height limits" if district else "Height limits"

    worked = readers.worked_buildings(results)
    if worked:
        area_disp = worked[0].get("scheduled_display")
        scheduled_text = (
            labels.scheduled_floor_area_line(area_disp) if area_disp
            else "Scheduled building not available"
        )
        scheduled_basis = None
        if worked[0].get("storey_count") and worked[0].get("height_display"):
            scheduled_basis = f"{worked[0]['storey_count']} storeys; {worked[0]['height_display']}"
        scheduled_label = worked[0]["status_label"]
    else:
        scheduled_text, scheduled_basis, scheduled_label = (
            "No building option worked yet", None, labels.PENDING_VERIFICATION
        )

    rows = [
        ("Floor-area allowance", _answer_cell(allowance_text, fa_basis, allowance_phrase),
         allowance_label),
        ("Permitted envelope", _answer_cell(envelope_text, envelope_basis), envelope_label),
        ("Scheduled building", _answer_cell(scheduled_text, scheduled_basis), scheduled_label),
    ]
    body = [
        el("tr", el("th", name), el("td", cell), el("td", label_chip(label)))
        for name, cell, label in rows
    ]
    return el(
        "table",
        el("thead", el("tr", el("th", "Answer"), el("th", "Result"), el("th", "Status"))),
        el("tbody", *body),
        class_="answers-table",
    )


def _summary_block(results: Mapping, ident: Mapping, env, site_context_plan) -> raw:
    answers = el("div", _answers_table(results, ident), class_="summary-answers")
    # When the surroundings are available, page type 1's small site figure is the
    # COMPACT summary frame of the site context plan (ruling Y10), beside the answers
    # as in wave 21 so the decision summary fits its first printed page.
    if site_context_plan is not None and site_context_plan.is_drawing:
        # Page 1's thumbnail carries a SHORT caption that fits its column; the full
        # sources-and-dates caption is on the site plan of the 'What constrains the
        # design?' sheet and on the evidence page (rework 2 fix 1).
        plan = el("figure",
                  raw(site_context_plan.svg or ""),
                  el("figcaption", "The lot among its neighbours (city map; not surveyed)."),
                  class_="summary-figure")
        return el("div", answers, plan, class_="summary")
    site_plan = drawings_embed.embed_summary_site_plan(results, env=env)
    if site_plan.is_drawing:
        plan = figure(
            site_plan,
            "Site plan: the lot's approximate tax-map outline (city records).",
            figure_class="summary-figure",
        )
        return el("div", answers, plan, class_="summary")
    return el("div", answers, figure(site_plan, "", line_when_absent=site_plan.short_line))


def _ceiling_cell(results: Mapping) -> raw:
    """The legal-ceiling half of the paired block: the shown ceiling value with its
    own (never Provisional, never settled) label, or - when the standard limit is
    withheld - unit_limit_text's reason (S4)."""
    ceiling = unit_limit_text.legal_ceiling(results)
    if ceiling["value"] is not None:
        return el(
            "div",
            raw(f'<span class="answer-value">Legal ceiling {escape(ceiling["value"])}</span>'),
            label_chip(ceiling["label"]) if ceiling["label"] else raw(""),
            class_="ceiling",
        )
    if ceiling["reason"]:
        return el(
            "div",
            el("span", "Legal ceiling: ", class_="answer-value"),
            el("span", ceiling["reason"]),
            label_chip(ceiling["label"]) if ceiling["label"] else raw(""),
            class_="ceiling",
        )
    return el("div", el("span", "Legal ceiling not available", class_="answer-value"),
              class_="ceiling")


def _estimate_cell(worked: list[dict]) -> raw | None:
    """The apartment-estimate half of the paired block: the range from the document,
    labelled Provisional, linking to its full calculation on the scenario sheet."""
    if not worked:
        return None
    estimate_range = readers.apartment_estimate_range(worked[0].get("capacity_estimate"))
    if estimate_range is None:
        return None
    building = worked[0].get("building")
    figure_text = f"Estimate {estimate_range}"
    if building:
        value = raw(
            f'<a href="#estimate-{escape_attr(building)}">'
            f'<span class="answer-value">{escape(figure_text)}</span></a>'
        )
    else:
        value = raw(f'<span class="answer-value">{escape(figure_text)}</span>')
    return el("div", value, label_chip(labels.PROVISIONAL), class_="estimate")


def _ceiling_estimate_block(results: Mapping, worked: list[dict]) -> raw:
    """One block holding the legal ceiling beside the apartment estimate, with the
    distinction line read from the token wording group (S4)."""
    pair_children: list[object] = [_ceiling_cell(results)]
    estimate = _estimate_cell(worked)
    if estimate is not None:
        pair_children.append(estimate)
    return el(
        "div",
        el("div", *pair_children, class_="ceiling-estimate-pair"),
        el("p", WORDING["ceiling_estimate_distinction"], class_="distinction"),
        class_="ceiling-estimate",
    )


def _uncertainty_line(row: Mapping) -> raw:
    # Each uncertainty is ONE short reference: the title linked to its issue record
    # (#issue-<n>), then its label. The full effect wording lives in that issue record
    # on the appendix, so page 1 never repeats an 8+ word sentence found there (R2-F13).
    number = row["number"]
    children: list[object] = [
        raw(f'<a href="#issue-{escape_attr(number)}">{escape(row["title"])}</a> '),
    ]
    if row["category"] == "rear_yard":
        # The rear-yard uncertainty links the law (ZR 23-344) through its existing
        # capture; its open-check wording (names 23-344(b)/(c)(3), no conclusion) is the
        # issue record's effect on the appendix.
        url = law_links.section_url(constraint_text.REAR_YARD_LAW_SECTION)
        if url:
            children.append(raw(
                f'<a href="{escape_attr(url)}">'
                f'{escape(constraint_text.REAR_YARD_LAW_SECTION)}</a> '
            ))
    children.append(label_chip(row["status_label"]))
    return el("li", *children)


def _uncertainties(results: Mapping) -> raw:
    rows = readers.decision_open_items(results)
    if not rows:
        return el("p", "No uncertainties recorded.", class_="short-line")
    items = [_uncertainty_line(row) for row in rows]
    return el("div", el("h3", "What is still uncertain"), el("ul", *items), class_="uncertainties")


def _scope_line() -> raw:
    return el(
        "p",
        "The material exclusions are listed at the head of the appendix.",
        class_="scope-line",
    )


def render(results: Mapping, ident: Mapping, *, maps_present: bool = False,
           site_context_plan=None, env=None) -> str:
    worked = readers.worked_buildings(results)
    children = [
        _property_heading(results, ident),
        el("p", labels.STANDING_LABEL, class_="standing-label"),
        el("h2", QUESTION),
        _summary_block(results, ident, env, site_context_plan),
        _ceiling_estimate_block(results, worked),
        _uncertainties(results),
        _scope_line(),
    ]
    return str(el("section", *children, class_="report-page", id="decision-summary"))
