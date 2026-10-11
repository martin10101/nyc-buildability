"""Page type 1 (decision summary) acceptance scenarios for M5-T165.

The report's first page, rebuilt to the design-contract change of 2026-10-11
(ARCHITECT_PRESENTATION_CONTRACT.md, "Change 2026-10-11", "Page 1, decision
summary"). Every expected string is quoted from the contract, the packet or the
evidence records (NB-01, NB-03, NB-04) - never copied from a program run.

Scenarios: S1 (four kinds + furniture), S2 (zoning-lot sentence / generic state),
S3 (headline from tokens), S4 (ceiling + estimate block), S5 (three uncertainties),
S6 (links resolve), S11 (allowance phrase), S12 (scope line / exclusions), S18 (no
GIS value called "tax map" in this task's texts), S19 (rear-yard open check).
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from app.drawings.kit.presentation_tokens import TYPE, WORDING
from app.drawings.report import (
    build_report_html,
    constraint_text,
    layout,
    page_decision_summary,
    readers,
    unit_limit_text,
)
from app.drawings.report.labels import CONDITIONAL, FORBIDDEN_RESULT_WORDS, PROVISIONAL

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)


def load_results(name: str) -> dict:
    return json.loads((_FIXTURES / f"{name}.json").read_text("utf-8"))


def benchmark() -> dict:
    return load_results("recorded_215_16_northern_journey")


def not_checked_document() -> dict:
    """A recorded Northern-Boulevard document whose figures carry NO ACRIS
    zoning-lot-index condition, so page 1 shows the generic line (S2)."""
    return load_results("synthetic_scope_tax_lot_only_northern")


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<script.*?</script>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def _page_one_html(doc: dict) -> str:
    html = build_report_html(doc)
    return html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]


# =========================================================================== S1
def test_s1_page_one_holds_the_four_kinds_and_the_named_furniture() -> None:
    page = _page_one_html(benchmark())
    text = visible_text(page)
    # kind 1: results in large type with their assumption line and the allowance phrase.
    assert "Floor-area allowance" in text
    assert "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" in text
    # kind 2: one site graphic slot (the compact frame or its unavailable short line).
    assert 'class="summary' in page
    # kind 3: the legal ceiling beside the apartment estimate with the distinction line.
    assert 'class="ceiling-estimate-pair"' in page
    assert WORDING["ceiling_estimate_distinction"] in text
    # kind 4: the uncertainties block.
    assert "What is still uncertain" in text
    # named furniture: type name, identity, standing label, the question, the scope line.
    assert "Decision summary" in text
    assert "Queens block 7334, lot 70" in text
    assert "Preliminary zoning results: a labelled, unreviewed draft." in text
    assert "What can I potentially build?" in text
    assert "The material exclusions are listed at the head of the appendix." in text
    # nothing the page type never carries: no status definitions, no version history,
    # no coverage inventory.
    assert "What this report covers" not in text
    assert "version history" not in text.lower()


# =========================================================================== S2
def test_s2_zoning_lot_sentence_names_the_register_index_entry() -> None:
    # NB-01 observed facts: ZONE = "ZONING LOT DESCRIPTION", recorded 2022-02-08,
    # indexed against lots 1 and 70. The page-1 sentence names the index ENTRY, not the
    # instrument, with every value from the document's own condition.
    page = _page_one_html(benchmark())
    text = visible_text(page)
    assert (
        "the city's register lists a zoning lot description recorded 2022-02-08 "
        "against lots 1 and 70"
    ) in text
    # it never names an instrument (the CRFN / document id belongs to the appendix, not page 1).
    assert "2022000059134" not in text
    # the generic line does NOT appear when the property-specific condition exists.
    assert "the app does not verify the zoning lot" not in text


def test_s2_generic_line_only_in_the_not_checked_state_and_once() -> None:
    doc = not_checked_document()
    assert readers.zoning_lot_basis(doc) is None
    page = _page_one_html(doc)
    text = visible_text(page)
    assert text.count("the app does not verify the zoning lot") == 1
    # no property-specific register sentence in the not-checked state.
    assert "the city's register lists a zoning lot description" not in text


# =========================================================================== S3
def test_s3_headline_is_28_to_32_pt_and_every_print_size_comes_from_tokens() -> None:
    headline_pt = TYPE["headline-value"]["print_pt"]
    assert 28 <= headline_pt <= 32
    css = layout.report_css("HEADER", "FOOTER")
    # the page-1 result figure uses the headline token size, nothing hard-coded.
    rule = re.search(r"\.answers-table \.answer-figure \{([^}]*)\}", css)
    assert rule is not None
    assert f"font-size: {headline_pt}pt" in rule.group(1)
    # every print size in the stylesheet is one of the TYPE tokens' print sizes (no stray pt).
    allowed = set()
    for role in TYPE.values():
        for key in ("print_pt", "print_pt_preferred"):
            if key in role:
                allowed.add(str(role[key]))
    for match in re.finditer(r"font-size:\s*([0-9.]+)pt", css):
        assert match.group(1) in allowed, f"font-size {match.group(1)}pt is not a TYPE token"


# ============================================================= visual G3 rework 1
def test_rework1_headline_holds_only_a_key_figure_not_a_sentence() -> None:
    # Only the KEY FIGURE of each answer sits at the 30 pt headline size - a short value read
    # from the document, never a whole sentence (a sentence wrapped into a word-by-word tower in
    # the narrow Result column, the visual G3 defect). The rest of the result is the body detail.
    page = _page_one_html(benchmark())
    figures = re.findall(r'<div class="answer-figure">([^<]*)</div>', page)
    assert figures, "page 1 has no answer figures"
    for figure_text in figures:
        words = figure_text.split()
        assert 0 < len(words) <= 4, f"headline is not a short key figure: {figure_text!r}"
        assert ";" not in figure_text, f"headline carries a sentence clause: {figure_text!r}"
    # the longer result text lives in the body-size detail line, not the headline.
    details = re.findall(r'<div class="answer-detail">([^<]*)</div>', page)
    assert any(";" in d for d in details), "the fixed scheduled wording should be a body detail"


def test_rework1_answers_table_and_figure_fit_printable_width() -> None:
    # The answers table and the site figure fit side by side within the printable width
    # (A4 210mm - 2x14mm margins = 182mm), so the Status column is never clipped by the figure
    # (the visual G3 defect printed "Conditi"). The figure is a bounded flex column; it plus the
    # gap must leave room for the answers column, which can shrink (min-width 0) so the table
    # never overflows under the figure.
    css = layout.report_css("H", "F")
    fig = re.search(r"\.summary-figure\s*\{[^}]*flex:\s*0 0 (\d+)mm", css)
    assert fig is not None, "the site figure is not a bounded flex column"
    gap = re.search(r"\.summary\s*\{[^}]*gap:\s*(\d+)mm", css)
    assert gap is not None, "the summary row has no gap"
    printable_mm = 210 - 2 * 14
    assert int(fig.group(1)) + int(gap.group(1)) < printable_mm, (
        "the figure column leaves no room for the answers table within the printable width"
    )
    assert re.search(r"\.summary-answers\s*\{[^}]*min-width:\s*0", css), (
        "the answers column cannot shrink, so the table would overflow under the figure"
    )


# =========================================================================== S4
def test_s4_ceiling_and_estimate_sit_in_one_block_with_the_token_line() -> None:
    # the token distinction line equals the contract's quoted line (byte-for-byte).
    assert WORDING["ceiling_estimate_distinction"] == (
        "The ceiling is a conditional zoning limit; the estimate is an unvalidated "
        "apartment-yield range; neither is a demonstrated layout."
    )
    page = _page_one_html(benchmark())
    text = visible_text(page)
    # one block holds the ceiling beside the estimate and the distinction line below.
    pair = page[page.index('class="ceiling-estimate'):]
    assert 'class="ceiling-estimate-pair"' in pair
    assert "Legal ceiling 29" in text
    assert "Estimate 17-22" in text
    assert WORDING["ceiling_estimate_distinction"] in text
    # the 29 ceiling carries Conditional, never Provisional or a settled claim.
    ceiling_cell = page[page.index('class="ceiling"'):page.index('class="estimate"')]
    assert CONDITIONAL in visible_text(ceiling_cell)
    assert PROVISIONAL not in visible_text(ceiling_cell)
    assert "settled" not in visible_text(ceiling_cell).lower()
    # the estimate carries Provisional and links to its full calculation on the sheet.
    assert 'href="#estimate-B"' in page


def test_s4_no_forbidden_result_word_on_page_one() -> None:
    low = visible_text(_page_one_html(benchmark())).lower()
    for word in (*FORBIDDEN_RESULT_WORDS, "buildable", "achievable", "can be built"):
        assert word.lower() not in low, f"forbidden result word leaked: {word}"


def test_s4_withheld_ceiling_shows_unit_limit_texts_reason() -> None:
    # When the standard-residence limit is WITHHELD, the ceiling half shows the document's
    # own reason (never an invented number). Built as a minimal document in the reader shape.
    reason = "The legal apartment limit needs the zoning lot confirmed."
    doc = {
        "answers": {
            "floor_area_allowance": {
                "value_states": {
                    "legal_unit_limit_standard": {
                        "way": "withheld",
                        "gap_kind": "missing_information",
                        "reason": reason,
                    }
                }
            }
        }
    }
    ceiling = unit_limit_text.legal_ceiling(doc)
    assert ceiling["value"] is None
    assert ceiling["reason"] == reason
    cell_html = str(page_decision_summary._ceiling_cell(doc))
    cell_text = visible_text(cell_html)
    assert reason in cell_text
    assert not re.search(r"Legal ceiling\s+\d", cell_text)


# =========================================================================== S5
def test_s5_three_uncertainties_in_order_with_the_rear_yard_open_check() -> None:
    rows = readers.decision_open_items(benchmark())
    assert len(rows) <= 3
    assert [row["category"] for row in rows] == ["zoning_lot", "lot_area", "rear_yard"]
    # the rear-yard uncertainty text comes from constraint_text (the open check), not a gap.
    assert constraint_text.effect_for("rear_yard") == constraint_text.REAR_YARD_OPEN_CHECK


# =========================================================================== S6
def test_s6_issue_links_and_the_estimate_link_resolve() -> None:
    html = build_report_html(benchmark())
    page = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    anchors = re.findall(r'href="#([^"]+)"', page)
    assert anchors  # the page carries links
    for anchor in anchors:
        assert f'id="{anchor}"' in html, f"dangling link #{anchor}"
    # the estimate link resolves to its full calculation on the scenario sheet.
    assert 'href="#estimate-B"' in page
    assert 'id="estimate-B"' in html


# =========================================================================== S11
def test_s11_allowance_phrase_sits_beside_the_headline() -> None:
    page = _page_one_html(benchmark())
    # the phrase is inside the floor-area answer cell, with the headline figure.
    assert 'class="allowance-phrase"' in page
    assert (
        "20,150 sq ft is a conditional tax-lot-only arithmetic allowance, "
        "not established remaining development rights."
    ) in visible_text(page)


# =========================================================================== S12
def test_s12_scope_line_on_page_one_and_exclusions_head_the_appendix() -> None:
    html = build_report_html(benchmark())
    text = visible_text(html)
    page = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    assert "The material exclusions are listed at the head of the appendix." in visible_text(page)
    # the material-exclusions block heads the appendix (type 5).
    appendix = html[
        html.index('id="assumptions-open-items"'):html.index('id="calculations-evidence"')
    ]
    appendix_text = visible_text(appendix)
    exclusions = appendix_text.index("Not yet in this report:")
    shared = appendix_text.index("Shared assumptions")
    assert exclusions < shared  # the exclusions note precedes the assumptions.
    # no feature inventory remains anywhere in the report.
    assert "What this report covers" not in text
    # all six page types are present.
    for sid in ("decision-summary", "site-and-context", "option-comparison",
                "scenario-B", "assumptions-open-items", "calculations-evidence"):
        assert f'id="{sid}"' in html


# =========================================================================== S10
def test_s10_zoning_lot_marker_stays_in_step_with_the_scenario_engine() -> None:
    # The report-side marker (zoning_lot_item) must equal the scenario engine's marker
    # (result_way_conditions.ZONING_LOT_INDEX_MARKER), so the recorded-document condition is
    # detected the same way on both sides and cannot silently drift (S10).
    from app.drawings.report import zoning_lot_item
    from app.scenario.three_answers import result_way_conditions
    assert (
        zoning_lot_item._ZONING_LOT_CONDITION_MARKER
        == result_way_conditions.ZONING_LOT_INDEX_MARKER
    )


def test_s10_readers_facade_keeps_the_zoning_lot_names() -> None:
    # After the G-6 isolation, readers re-exports zoning_lot_basis (a compatibility facade)
    # and keeps ANSWER_NAMES, so existing importers do not break (S10).
    from app.drawings.report import zoning_lot_item
    assert "zoning_lot_basis" in readers.__all__
    assert readers.zoning_lot_basis is zoning_lot_item.zoning_lot_basis
    assert readers.ANSWER_NAMES == ("floor_area_allowance", "permitted_envelope", "building_option")


# =========================================================================== S18
def test_s18_lot_area_effect_names_the_city_map_outline_not_tax_map() -> None:
    # NB-04: the 10,387.99 sq ft outline area is basis "gis"; the contract's plain-word
    # basis for gis is "city map outline". This task's lot_area effect text (constraint_text)
    # names it so, never "tax-map outline"; and page 1 names no GIS value "tax map" at all.
    effect = constraint_text.effect_for("lot_area")
    assert "city map outline" in effect
    assert "tax-map outline" not in effect
    assert "tax map" not in effect.lower()
    page_text = visible_text(_page_one_html(benchmark())).lower()
    assert "tax map" not in page_text
    assert "tax-map" not in page_text


# =========================================================================== S19
def test_s19_rear_yard_open_check_names_both_provisions_and_no_conclusion() -> None:
    # NB-03 (interpretation_awaiting_review): no rear-yard conclusion. The open check names
    # ZR 23-344(b) (short dimension of a block) and 23-344(c)(3) (adjoining side line) as not
    # yet checked, links 23-344, and draws no conclusion. The old corner-area wording is gone.
    text = visible_text(build_report_html(benchmark()))
    assert "not known beyond the corner area" not in text
    check = constraint_text.REAR_YARD_OPEN_CHECK
    assert "23-344(b)" in check and "23-344(c)(3)" in check
    assert constraint_text.REAR_YARD_LAW_SECTION == "ZR 23-344"
    # it states no conclusion: no "a rear yard is required" / "no rear yard is required".
    low = check.lower()
    assert "not yet checked" in low
    assert "is required" not in low or "not yet checked" in low
    # page 1 links the law section for the rear-yard uncertainty.
    page = build_report_html(benchmark())
    page1 = page[page.index('id="decision-summary"'):page.index('id="site-and-context"')]
    assert "ZR 23-344" in visible_text(page1)
