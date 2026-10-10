"""Page type 1 - Decision summary (page-types.md row 1; rework F3).

The reader's question is the page title. It leads with the property and the
three answers in a compact table (figure, one line of basis, label), a compact
site plan beside them, the preliminary apartment estimate on one line, and the
three most important open items on one line each.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import coverage, drawings_embed, labels, readers
from .components import figure, label_chip
from .html import el, escape, raw

__all__ = ["render"]

QUESTION = "What can I potentially build?"


def _property_heading(ident: Mapping) -> raw:
    display = ident.get("display")
    address = ident.get("address")
    title = address or display or "Selected tax lot"
    lines = [el("p", "Decision summary", class_="type-name"), el("h1", title)]
    if address and display:
        lines.append(el("p", display, class_="identity-line"))
    zoning = ident.get("zoning_line")
    if zoning:
        lines.append(el("p", zoning, class_="identity-line"))
    if ident.get("lot_selection"):
        lines.append(el("p", ident["lot_selection"], class_="identity-line"))
    return el("div", *lines)


def _answer_cell(figure_text: str | None, basis: str | None) -> raw:
    value = figure_text if figure_text is not None else "Not available"
    children = [el("div", value, class_="answer-figure")]
    if basis:
        children.append(el("div", basis, class_="identity-line"))
    return el("div", *children)


def _answers_table(results: Mapping) -> raw:
    fa = readers.answer_block(results, "floor_area_allowance")
    far = readers.named_value(fa, "max_residential_far")
    area = readers.named_value(fa, "max_residential_floor_area")
    allowance_text = None
    allowance_label = labels.PENDING_VERIFICATION
    if area is not None:
        allowance_text = area["display"]
        if far and far.get("display"):
            allowance_text = f"{allowance_text} (FAR {far['display']})"
        allowance_label = area["status_label"]

    env = readers.answer_block(results, "permitted_envelope")
    min_base = readers.named_value(env, "min_base_height")
    max_base = readers.named_value(env, "max_base_height")
    max_building = readers.named_value(env, "max_building_height")
    envelope_text = None
    envelope_label = labels.PENDING_VERIFICATION
    if max_building is not None:
        parts = []
        if min_base and max_base:
            parts.append(f"Base {min_base['display']} to {max_base['display']}")
        parts.append(f"building up to {max_building['display']}")
        envelope_text = "; ".join(parts)
        envelope_label = max_building["status_label"]

    worked = readers.worked_buildings(results)
    if worked:
        area_disp = worked[0].get("scheduled_display")
        scheduled_text = (
            labels.scheduled_floor_area_line(area_disp) if area_disp
            else "Scheduled building not available"
        )
        basis = None
        if worked[0].get("storey_count") and worked[0].get("height_display"):
            basis = f"{worked[0]['storey_count']} storeys; {worked[0]['height_display']}"
        scheduled_label = worked[0]["status_label"]
    else:
        scheduled_text, basis, scheduled_label = (
            "No building option worked yet", None, labels.PENDING_VERIFICATION
        )

    rows = [
        ("Floor-area allowance", _answer_cell(allowance_text, "Residential FAR on the recorded "
                                              "lot area"), allowance_label),
        ("Permitted envelope", _answer_cell(envelope_text, "R6B height limits"), envelope_label),
        ("Scheduled building", _answer_cell(scheduled_text, basis), scheduled_label),
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


def _summary_block(results: Mapping, env, site_context_plan) -> raw:
    answers = el("div", _answers_table(results), class_="summary-answers")
    # When the surroundings are available, page type 1's small site figure becomes
    # the report frame of the site context plan (ruling Y10). It is the full report
    # width, so it stacks below the answers rather than sitting beside them.
    if site_context_plan is not None and site_context_plan.is_drawing:
        plan = figure(site_context_plan, site_context_plan.caption or "")
        return el("div", answers, plan)
    site_plan = drawings_embed.embed_summary_site_plan(results, env=env)
    if site_plan.is_drawing:
        plan = figure(
            site_plan,
            "Site plan: the lot's approximate tax-map outline (city records).",
            figure_class="summary-figure",
        )
        return el("div", answers, plan, class_="summary")
    return el("div", answers, figure(site_plan, "", line_when_absent=site_plan.short_line))


def _apartment_estimate(worked: list[dict]) -> raw | None:
    if not worked:
        return None
    text = readers.apartment_estimate_text(worked[0].get("capacity_estimate"))
    if text is None:
        return None
    return el(
        "p",
        raw(f"<strong>Preliminary apartment estimate:</strong> {escape(text)} "),
        label_chip(labels.PROVISIONAL),
        class_="estimate-line",
    )


def _open_items(results: Mapping) -> raw:
    rows = readers.decision_open_items(results)
    if not rows:
        return el("p", "No open items recorded.", class_="short-line")
    items = []
    for row in rows:
        items.append(
            el(
                "li",
                raw(f"<strong>{escape(row['title'])}:</strong> {escape(row['effect'])} "),
                label_chip(row["status_label"]),
                raw(f' <span class="identity-line">(see item {row["number"]})</span>'),
            )
        )
    return el("div", el("h3", "Most important open items"), el("ul", *items), class_="open-items")


def _coverage_block(results: Mapping, maps_present: bool) -> raw:
    """A compact 'What this report covers' block grouped by state (D9), at most a
    few lines; it replaces the coverage table that was on the assumptions page."""
    lines = []
    for label, names in coverage.coverage_groups(results, maps_present=maps_present):
        lines.append(
            el("p", raw(f"<strong>{escape(label)}:</strong> {escape('; '.join(names))}"),
               class_="coverage-line")
        )
    return el("div", el("h3", "What this report covers"), *lines, class_="coverage")


def render(results: Mapping, ident: Mapping, *, maps_present: bool = False,
           site_context_plan=None, env=None) -> str:
    worked = readers.worked_buildings(results)
    children = [
        _property_heading(ident),
        el("p", labels.STANDING_LABEL, class_="standing-label"),
        el("h2", QUESTION),
        _summary_block(results, env, site_context_plan),
    ]
    estimate = _apartment_estimate(worked)
    if estimate is not None:
        children.append(estimate)
    children.append(_open_items(results))
    children.append(_coverage_block(results, maps_present))
    return str(el("section", *children, class_="report-page", id="decision-summary"))
