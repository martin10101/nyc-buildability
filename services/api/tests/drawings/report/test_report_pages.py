"""Acceptance scenarios S1-S11 and rework findings F1-F12 for the report
generator (tasks M5-T151, rework 1).

Every expected figure is READ FROM THE DOCUMENT, never retyped. Drawing-frame
behaviour is exercised with ``LANE_E_ENABLED`` set; the compact summary frame
(F3) is skipped until M5-T152 makes it distinct from the full sheet frame.
"""

from __future__ import annotations

import html as _html
import inspect
import json
import re
from pathlib import Path

import pytest

from app.drawings import kit
from app.drawings.report import build_report_html, drawings_embed, layout, options, readers
from app.drawings.report.labels import FORBIDDEN_RESULT_WORDS

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
_LANE_E = {"LANE_E_ENABLED": "1"}


def load_results(name: str) -> dict:
    return json.loads((_FIXTURES / f"{name}.json").read_text("utf-8"))


def benchmark() -> dict:
    return load_results("recorded_215_16_northern_journey")


def two_buildings_document() -> dict:
    """Building A and B both worked, copied from the committed 1.4.0 fixtures."""
    base = benchmark()
    building_a = load_results(
        "synthetic_coverage_by_portion_available_contract_1_4_0")["building_alternatives"][0]
    building_b = load_results(
        "synthetic_building_alternatives_contract_1_4_0")["building_alternatives"][0]
    base["results_id"] = "synthetic_two_worked_buildings"
    base["building_alternatives"] = [building_a, building_b]
    base["buildings_not_worked"] = []
    return base


def partial_document() -> dict:
    return {
        "contract_version": "1.4.0", "revision": 1, "computed_at": "2026-10-03T00:00:00Z",
        "lot_selection_statement": "Based on the lots you selected",
        "answers": {
            "floor_area_allowance": {"status": "not_available", "reason": "x",
                                     "reason_kind": "missing_input"},
            "permitted_envelope": {"status": "not_available", "reason": "x",
                                   "reason_kind": "missing_input"},
            "building_option": {"status": "not_available", "reason": "x",
                                "reason_kind": "rule_not_implemented"},
        },
        "geometry": {"status": "not_available", "reason": "x", "reason_kind": "missing_input"},
        "scope": {"lot": {"borough": "Queens", "block": "7334", "lot": "70",
                          "display": "Queens block 7334, lot 70", "bbl": "4073340070"},
                  "assumptions": []},
        "building_alternatives": [], "buildings_not_worked": [], "addon_gains": [],
    }


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<script.*?</script>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


# M5-T169: page types 5 and 6 are merged into ONE evidence appendix (D-094 R077), so
# the section-id list, the reader-question list and the page count drop from six to five.
REASONS_IN_ORDER = (
    "What can I potentially build?",
    "What constrains the design?",
    "How do the options compare?",
    "What is this option?",
    "What remains unresolved, and how was this derived?",
)
SECTION_IDS_IN_ORDER = (
    "decision-summary", "site-and-context", "option-comparison",
    "scenario-", "appendix",
)


# =========================================================================== S1
def test_s1_five_page_types_in_order() -> None:
    html = build_report_html(benchmark())
    positions = [html.index(f'id="{sid}') for sid in SECTION_IDS_IN_ORDER]
    assert positions == sorted(positions)
    text = visible_text(html)
    for question in REASONS_IN_ORDER:
        assert question in text
    assert html.count('id="scenario-B"') == 1
    assert 'id="scenario-A"' not in html


def test_s1_two_worked_buildings_two_sheets() -> None:
    html = build_report_html(two_buildings_document())
    assert html.count('id="scenario-A"') == 1 and html.count('id="scenario-B"') == 1
    assert html.count('class="report-page"') == 6


def test_s1_benchmark_has_five_pages() -> None:
    assert build_report_html(benchmark()).count('class="report-page"') == 5


# =========================================================================== S2 / F1
def test_s2_page_size_furniture_and_literal_header_footer() -> None:
    css = layout.report_css("HEADER-TEXT", "FOOTER-TEXT")
    assert "size: A4 portrait" in css
    assert css.count("@page") == 1 and css.count("size: A4") == 1
    assert "margin: 14mm" in css
    for other in ("A3", "A5", "Letter", "legal", "Tabloid"):
        assert f"size: {other}" not in css
    assert "counter(page)" in css and "counter(pages)" in css
    assert "@top-left" in css and "@bottom-right" in css
    assert "break-before: page" in css and "table-header-group" in css
    assert "break-inside: avoid" in css
    # F1: the identity and footer are literal in the margin boxes, not string-set.
    assert '"HEADER-TEXT"' in css and '"FOOTER-TEXT"' in css
    assert "string-set" not in css and "string(" not in css


def test_f1_header_and_footer_rendered_into_page() -> None:
    html = build_report_html(benchmark(), identity={"address": "215-16 Northern Boulevard, Queens"})
    assert "215-16 Northern Boulevard, Queens" in html
    assert "Results revision 1" in html and "computed 2026-10-03" in html


# =========================================================================== S3
def test_s3_scheduled_wording_and_no_forbidden_words() -> None:
    doc = benchmark()
    text = visible_text(build_report_html(doc))
    area = readers.worked_buildings(doc)[0]["scheduled_display"]
    assert f"Scheduled floor area: {area} sq ft; site fit unverified" in text
    assert [w for w in FORBIDDEN_RESULT_WORDS if w in text.lower()] == []
    assert text.count("Verified") == 1


# =========================================================================== S4
FORBIDDEN_SUBSTRINGS = ("http", "endpoint", "fixture", "wiring", "backlog",
                        "owed", "lane a", "task a-", "this slice")


def _assert_no_developer_info(text: str) -> None:
    low = text.lower()
    for token in FORBIDDEN_SUBSTRINGS:
        assert token not in low, f"developer wording leaked: {token}"
    assert re.search(r"\b[a-z]+_[a-z]+\b", text) is None, "a snake_case word leaked"
    # 'None scheduled' is owner wording (F7); a bare rendered None/null/true/false is not allowed.
    assert re.search(r"\bNone\b(?!\s+scheduled)", text) is None
    for word in ("null", "true", "false"):
        assert re.search(rf"\b{word}\b", text) is None
    assert re.search(r"\bDB-\d|\bR\d{3}\b|\bM\d+-T\d+\b", text) is None
    for ref in ("question C1", "question D1", "question B6"):
        assert ref not in text


def test_s4_no_developer_information_benchmark() -> None:
    _assert_no_developer_info(visible_text(build_report_html(benchmark(), env=_LANE_E)))


def test_s4_no_developer_information_partial() -> None:
    _assert_no_developer_info(visible_text(build_report_html(partial_document())))


# =========================================================================== S5 / F7
def test_s5_eleven_options_table_first_no_limitation_paragraphs() -> None:
    # M5-T169 (R075/R059/R084): the comparison comes first - the eleven-option table
    # precedes the chart, and no "<p><strong>Limitation N.</strong>" paragraph remains
    # on the page; options 1-3 carry figures and options 4-11 read "Not evaluated in
    # this report" in the owner-approved order and names.
    doc = benchmark()
    rows = options.option_rows(doc)
    assert [r["ordinal"] for r in rows] == list(range(1, 12))
    assert [r["name"] for r in rows] == [name for _ordinal, name in options.ELEVEN_OPTIONS]
    assert len({r["status_label"] for r in rows}) > 1
    assert len({r["allowance_area"] for r in rows}) > 1
    html = build_report_html(doc)
    comparison = html[html.index('id="option-comparison"'):html.index('id="scenario-B"')]
    # the table precedes the chart (the comparison, not the limitation text, comes first).
    assert comparison.index("<table") < comparison.index('class="bar-chart"')
    # no "Limitation N." paragraph remains anywhere in the section.
    assert "<p><strong>Limitation" not in comparison
    text = visible_text(html)
    assert "Building A – not worked" in text  # en dash (A6)
    # options 1-3 carry figures; options 4-11 read "Not evaluated in this report".
    assert text.count("Not evaluated in this report") == 8


def test_f7_columns_chart_and_units() -> None:
    doc = benchmark()
    html = build_report_html(doc, env=_LANE_E)
    text = visible_text(html)
    # the "Limitation" column is gone (R075); the table keeps these four columns.
    for header in ("Floor-area allowance", "Scheduled building", "Status"):
        assert header in text
    comparison = html[html.index('id="option-comparison"'):html.index('id="scenario-B"')]
    header_row = comparison[comparison.index("<thead"):comparison.index("</thead>")]
    assert "Limitation" not in visible_text(header_row)
    assert "No scheduled building is available to chart yet." not in text
    assert 'class="bar-chart"' in html
    assert "sq ft sq ft" not in text and "FAR FAR" not in text
    # A6: allowance area and FAR are kept apart (each on its own line).
    assert "20,150 sq ft" in text and "FAR 2.0" in text
    assert "24,180 sq ft" in text and "FAR 2.4" in text
    assert "None scheduled" in text
    # the chart shows the placed-on-site status, never a bar; the benchmark building is placed but
    # the site plan does not yet draw the footprint (M5-T172 S14; M5-T173 part B draws it), so it
    # reads "Worked out; not drawn", never "Shown on the site plan" or "Not demonstrated".
    assert "Placed on site" in text and "Worked out; not drawn" in text
    assert "Shown on the site plan" not in text


# =========================================================================== S6
def test_s6_no_min_base_contradiction() -> None:
    doc = benchmark()
    assert readers.worked_buildings(doc)[0]["below_min_base"] is False
    assert "below the minimum base height" not in visible_text(build_report_html(doc))


def test_s6_below_min_base_only_when_document_says_so() -> None:
    doc = two_buildings_document()
    doc["building_alternatives"][0] = {**doc["building_alternatives"][0], "below_min_base": True}
    assert "below the minimum base height" in visible_text(build_report_html(doc))


def test_s6_no_empty_maps_section_inventory_reports_maps() -> None:
    text = visible_text(build_report_html(benchmark()))
    # F3: no maps section/sheet; the coverage inventory reports them instead.
    assert "Context maps are not included in this report." not in text
    assert "Context maps" in text  # in the coverage inventory


# =========================================================================== S7 / F5
def test_s7_lot_area_basis_quoted_with_result() -> None:
    doc = benchmark()
    text = visible_text(build_report_html(doc))
    expected = ("The floor-area allowance holds if the recorded lot area of 10,075 sq ft "
                "is confirmed")
    assert expected in text
    assert "10,387.99" in text and "disagree" in text
    # the basis names the tax-map outline in the document's own words.
    assert "tax-map outline" in text
    # D8: the drawing's own caption (one, below) names the tax-map basis; no line above repeats it.
    drawn = visible_text(build_report_html(doc, env=_LANE_E))
    assert "Approximate — tax map" in drawn
    assert "The site plan shows the tax-map outline (approximate; not a survey)." not in drawn


# =========================================================================== F4
def test_f4_no_stale_caption_and_single_floor_stack_caption() -> None:
    html = build_report_html(benchmark(), env=_LANE_E)
    text = visible_text(html)
    assert "shown when the drawing is available" not in text
    # the floor-stack Illustrative caption appears once per worked building (one here).
    assert text.count("Floor-stack section (Illustrative)") == 1


# =========================================================================== F6
def test_f6_one_coverage_row_in_constraints() -> None:
    html = build_report_html(benchmark())
    site = html[html.index('id="site-and-context"'):html.index('id="option-comparison"')]
    assert visible_text(site).count("Maximum lot coverage") == 1
    assert "Not shown" not in visible_text(site)  # states are named, never bare "Not shown"


# =========================================================================== S8 / Q1
ALL_FIXTURES = [p.stem for p in sorted(_FIXTURES.glob("*.json"))]
SIX_LABELS = ("Provisional", "Illustrative", "Conditional", "Pending verification", "Unresolved")
ALL_SIX = ("Verified", *SIX_LABELS)


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_s8_q1_one_label_per_output_on_every_fixture(name: str) -> None:
    doc = load_results(name)
    html = build_report_html(doc)
    text = visible_text(html)
    assert text.count("Verified") <= 1
    assert any(label in text for label in SIX_LABELS)
    # Q1: every answer value, option row, open-item row and constraint (withheld)
    # row carries exactly one of the six labels.
    for option in options.option_rows(doc):
        assert option["status_label"] in ALL_SIX
    for item in readers.open_items(doc):
        assert item["status_label"] in ALL_SIX
    for name_ in readers.ANSWER_NAMES:
        block = readers.answer_block(doc, name_)
        for value in readers.present_values(block):
            assert value["status_label"] in ALL_SIX
        for withheld in readers.withheld_values(block):
            assert withheld["status_label"] in ("Unresolved", "Pending verification")
    for building in (*readers.worked_buildings(doc), *readers.not_worked_buildings(doc)):
        assert building["status_label"] in ALL_SIX
    # every rendered label chip is one of the six (no stray label).
    for chip in re.findall(r'class="label-chip">([^<]*)<', html):
        assert chip in ALL_SIX, f"stray label chip: {chip!r}"


def test_q1_drawing_caption_carries_a_label() -> None:
    # the floor-stack caption (a drawing caption) carries the Illustrative label.
    text = visible_text(build_report_html(benchmark(), env=_LANE_E))
    assert "Floor-stack section (Illustrative)" in text


# =========================================================================== S9
def _rounded(value: float) -> set[float]:
    return {round(float(value), k) for k in (0, 1, 2, 3, 4, 6)}


def _collect(obj, allowed: set[float]) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        allowed |= _rounded(obj)
    elif isinstance(obj, str):
        for match in re.findall(r"\d[\d,]*(?:\.\d+)?", obj):
            try:
                allowed |= _rounded(float(match.replace(",", "")))
            except ValueError:
                pass
    elif isinstance(obj, dict):
        for value in obj.values():
            _collect(value, allowed)
    elif isinstance(obj, list):
        for value in obj:
            _collect(value, allowed)


def test_s9_every_number_comes_from_the_document() -> None:
    doc = benchmark()
    allowed: set[float] = set()
    _collect(doc, allowed)
    ordinal_max = max(11, len(readers.assumptions(doc)), len(readers.open_items(doc)))
    for i in range(1, ordinal_max + 1):
        allowed |= _rounded(i)
    # Checked on the report's OWN text (drawings off): the kit's site plan prints
    # computed edge dimensions whose provenance is the kit's own labels, not the
    # report's. The report itself types no figure (ruling X7). The run-identity block
    # (M5-T169) carries a document FINGERPRINT and the code COMMIT - identity hashes,
    # not document figures - so it is excluded before the figure scan.
    html = build_report_html(doc)
    html = re.sub(r'<h3>Run identity</h3>.*?(?=<h3>Status-label key</h3>)', " ", html, flags=re.S)
    text = visible_text(html)
    for token in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        value = float(token.replace(",", ""))
        assert any(round(value, k) in allowed for k in (0, 1, 2, 3, 4, 6)), (
            f"number {token!r} is not in the results document"
        )


# =========================================================================== S10
def test_s10_partial_data_every_page() -> None:
    html = build_report_html(partial_document())
    for sid in ("decision-summary", "site-and-context", "option-comparison",
                "scenario-none", "appendix"):
        assert f'id="{sid}"' in html
    text = visible_text(html)
    assert "The lot outline is not available for this property." in text
    assert "11. All programs combined" in text
    assert "No building option has been worked for this property yet." in text


# =========================================================================== S11
def test_s11_escaping() -> None:
    doc = partial_document()
    doc["lot_selection_statement"] = 'A & B <script>alert(1)</script> "quoted" <img src=x>'
    doc["scope"]["assumptions"] = [
        {"key": "k", "value": "v", "statement": 'danger & <script>x</script> "q"'}
    ]
    html = build_report_html(doc)
    assert "<script" not in html.lower() and "<img" not in html.lower()
    assert "onerror=" not in html.lower() and "onclick=" not in html.lower()
    assert "&lt;script&gt;" in html


# =========================================================================== F8 / A3
def test_f8_open_items_five_field_records() -> None:
    # M5-T169 (R025): the appendix open items are five-field issue records -
    # issue, consequence, next action, responsible role, evidence reference.
    html = build_report_html(benchmark())
    text = visible_text(html)
    for header in ("Issue", "Consequence", "Next action", "Responsible role",
                   "Evidence reference"):
        assert header in text
    # The legal-apartment-limit consequence (after M5-T157) follows the document.
    assert (
        "The legal apartment limit is shown as a conditional ceiling for standard residences; "
        "it is not known for qualifying affordable housing or qualifying senior housing."
    ) in text
    assert "No legal apartment limit is shown." not in text
    # site documents are kept apart from program work (R025).
    assert "Owner or surveyor" in text
    assert "This program" in text
    # material document reasons are preserved beneath the row (not deleted, R025).
    assert "class=\"reason-row\"" in html


def test_db232_zoning_lot_open_item_is_first() -> None:
    # DB-232 / D-094 R029/R030: on the benchmark (a recorded zoning lot description names lot 1) the
    # property-specific zoning-lot concern is the FIRST open item, and the decision summary prefers
    # it. The reason names lot 1 and the resolver names the City Register file.
    doc = benchmark()
    items = readers.open_items(doc)
    assert items[0]["title"] == "Zoning lot"
    assert items[0]["number"] == 1
    assert "lot 1" in items[0]["reason"]
    assert "2022000059134" in items[0]["resolves"]
    decision = readers.decision_open_items(doc)
    assert decision[0]["title"] == "Zoning lot"


def test_a3_material_reason_preserved_and_honest_sentence_once() -> None:
    # M5-T169 (R025/R054/R077): a material document reason is preserved beneath the
    # issue row ONLY for the unique material reasons (coverage by-portion law; the
    # per-program legal-limit gaps). The zoning-lot, lot-area and rear-yard reasons
    # already appear on page 1 / page 3 / the shared assumptions, so repeating them is
    # the repetition R077 removes. The honest "A check not yet made ..." next action
    # prints at most once though more than one not-checked item exists.
    from app.drawings.report import open_items
    doc = benchmark()
    expected = sum(1 for r in open_items.appendix_issue_records(doc) if r.get("detail"))
    html = build_report_html(doc)
    text = visible_text(html)
    assert html.count('class="reason-row"') == expected
    assert 0 < expected < len(readers.open_items(doc))  # some details, not every item
    # the unique material reasons are preserved; the repeated zoning-lot one is not.
    assert "the law allows up to 100 percent coverage" in text  # coverage by-portion kept
    assert text.count("A check not yet made against an independently worked example.") <= 1
    # Placement now resolves "Where the plan sits on the lot" on the benchmark (M5-T172), so parking
    # is the one not-checked item carrying the honest sentence above. The dedupe (R054) is still
    # exercised on an UNPLACED building, which keeps the placement not-checked line: two items then
    # carry the sentence and only the first prints it (the second points back).
    import copy
    unplaced = copy.deepcopy(doc)
    unplaced["building_alternatives"][0]["not_checked"] = [
        "Where the plan sits on the lot", "Parking, loading and bicycle requirements",
    ]
    not_checked = [i for i in readers.open_items(unplaced)
                   if i["category"] in ("placement", "parking")]
    assert len(not_checked) >= 2  # more than one not-checked item, so the dedupe is exercised
    unplaced_text = visible_text(build_report_html(unplaced))
    assert unplaced_text.count(
        "A check not yet made against an independently worked example."
    ) == 1


# ==================================================================== F10 / R012 / UX-12
def test_f10_r012_coverage_inventory_leaves_the_report() -> None:
    # The coverage inventory (the D9 "what this report covers" block) LEAVES the report
    # (R012/UX-12, change 2026-10-11; M5-T165). It is the owner update's material now, not
    # the architect's reading path. Page 1 carries a compact scope line pointing to the
    # material-exclusions block at the head of the appendix. coverage.coverage_groups stays
    # for the owner update.
    from app.drawings.report import coverage
    html = build_report_html(benchmark())
    text = visible_text(html)
    # the inventory and its state headings appear NOWHERE in the report.
    assert "What this report covers" not in text
    assert "In this report:" not in text
    assert "Coverage of the promised sections" not in text
    assert "1 of 11 options worked" not in text
    # page 1 carries the scope line to the appendix instead.
    decision = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    scope_line = "The material exclusions are listed at the head of the appendix."
    assert scope_line in visible_text(decision)
    # the owner-update data stays computable even though the report no longer prints it.
    assert dict(coverage.coverage_groups(benchmark())).get("Not yet")


# =========================================================================== F11
def test_f11_evidence_inputs_label_key_and_nowrap() -> None:
    # M5-T169 (R026/R077): the "Inputs and their sources" table lists the MEASURED
    # 1.5.0 input_facts with their real source titles and dates; the categorical reads
    # (zoning district, lot type, frontage) are stated once in the Shared assumptions
    # above (not repeated as input rows).
    html = build_report_html(benchmark())
    text = visible_text(html)
    assert "Inputs and their sources" in text
    assert "Recorded lot area" in text and "Lot outline area (city map)" in text
    assert "Mapped street width - 215 Place" in text
    # real source identifiers and dates, never just "City records" (R026).
    assert "NYC Department of City Planning MapPLUTO, version 26v2 (as of 2026-09-30)" in text
    assert "DCP Digital City Map street center lines (as of 2026-09-30)" in text
    # the categorical reads are stated once, in the shared assumptions.
    assert "Zoning district" in text
    # envelope law sections present (not only 23-22); the number never breaks (A7).
    assert "23-432" in text
    assert '<span class="nowrap">23-432</span>' in html
    # the owner's exact R783 wording and the "Not used in this report." note.
    assert "Supported by completed checks and evidence. Not used in this report." in text
    assert "Prepared but subject to confirmation or revision." in text
    assert 'class="nowrap"' in html
    assert "the figures below are read from the result" not in text


# ================================================= no page wider than the paper (correction 2)
def test_correction2_decision_row_shrinks_and_cells_wrap() -> None:
    css = layout.report_css("H", "F")
    # The answers column takes the remaining width and can shrink to fit.
    assert re.search(r"\.summary-answers\s*\{[^}]*flex:\s*1 1 auto[^}]*min-width:\s*0", css)
    # The figure stays 88 mm beside it.
    assert re.search(r"\.summary-figure\s*\{[^}]*flex:\s*0 0 88mm", css)
    # The answer figures WRAP (no nowrap), so the table shrinks below their one-line width.
    cell = re.search(r"\.answers-table \.answer-figure\s*\{([^}]*)\}", css)
    assert cell and "white-space: nowrap" not in cell.group(1)
    # The decision row holds the shrinking answers table beside the fixed figure.
    decision = _decision_section(build_report_html(benchmark(), env=_LANE_E))
    assert 'class="summary-answers"' in decision and 'class="summary-figure"' in decision


def _decision_section(html: str) -> str:
    return html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]


# ===================================== no-split by printed HEIGHT, tall tables break (correction 3)
def test_short_table_by_height_is_no_split_and_a_tall_one_is_not() -> None:
    from app.drawings.report.html import (
        SHORT_TABLE_MAX_HEIGHT_MM,
        estimated_table_height_mm,
        table,
    )

    # pick a body-row count that is short by estimated height, and one that is tall.
    short_rows = next(
        n for n in range(1, 40)
        if estimated_table_height_mm(n) <= SHORT_TABLE_MAX_HEIGHT_MM
        and estimated_table_height_mm(n + 1) > SHORT_TABLE_MAX_HEIGHT_MM
    )
    short = str(table(["A", "B"], [["1", "2"]] * short_rows))
    tall = str(table(["A", "B"], [["1", "2"]] * (short_rows + 1)))
    assert 'class="no-split"' in short  # <= 70 mm: never split across a page
    assert "no-split" not in tall  # taller: may break between rows
    css = layout.report_css("H", "F")
    assert re.search(r"\.no-split\s*\{[^}]*break-inside:\s*avoid", css)
    # a tall table's note never separates from its row (the note row never starts a page).
    assert re.search(r"\.reason-row\s*\{[^}]*break-before:\s*avoid", css)


def test_status_label_key_is_a_no_split_table() -> None:
    # the status-label key (a short table) moves whole, never a lone fragment.
    html = build_report_html(benchmark())
    evidence = html[html.index('id="appendix"'):]
    key_table = evidence[evidence.index("<table", evidence.index("Status-label key")):]
    assert key_table.startswith('<table class="key-table no-split"')


# =========================================================================== A2
def test_a2_no_non_drawing_text_below_8pt() -> None:
    css = layout.report_css("H", "F")
    for block in css.split("}"):
        for match in re.finditer(r"font-size:\s*([\d.]+)pt", block):
            size = float(match.group(1))
            if size < 8:
                assert "bar-chart" in block, f"non-drawing rule sets {size}pt: {block.strip()!r}"


# =========================================================================== A5
def test_a5_zoning_line_not_a_joined_fragment() -> None:
    text = visible_text(build_report_html(benchmark()))
    assert "Zoning district R6B · Commercial overlay C2-2" in text
    assert "District R6B; A commercial overlay" not in text


# =========================================================================== A9
def test_a9_unavailable_drawing_line_names_the_drawing() -> None:
    # Drawings off (no LANE_E): the site-plan line names the site plan, not a generic drawing.
    text = visible_text(build_report_html(benchmark()))
    assert "The site plan is not available for this report." in text
    assert "This drawing is not shown here." not in text


# =========================================================================== D1 / D2
def test_d1_d2_drawings_embedded_at_designed_point_size() -> None:
    html = build_report_html(benchmark(), env=_LANE_E)
    svgs = re.findall(r"<svg\b[^>]*>", html)
    assert len(svgs) >= 3
    for tag in svgs:
        vb = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([-\d.]+) ([-\d.]+)"', tag)
        w = re.search(r'width="([-\d.]+)pt"', tag)
        h = re.search(r'height="([-\d.]+)pt"', tag)
        assert vb and w and h, f"svg not sized in pt from viewBox: {tag[:80]}"
        assert abs(float(w.group(1)) - float(vb.group(1))) < 0.01
        assert abs(float(h.group(1)) - float(vb.group(2))) < 0.01
    # every SVG text font size (in viewBox units) is at least 7.
    for size in re.findall(r'<text[^>]*font-size="([0-9.]+)"', html):
        assert float(size) >= 7, f"svg text font size {size} < 7"
    # the report CSS never sizes an svg (in %, or at all).
    css = layout.report_css("H", "F")
    assert not re.search(r"svg[^{}]*\{[^}]*(?:max-)?width", css)


# =========================================================================== D5
def test_d5_running_header_join_no_repeated_borough() -> None:
    ident = readers.identity(benchmark(), address="215-16 Northern Boulevard, Queens")
    line = readers.identity_header_line(ident)
    assert line == "215-16 Northern Boulevard, Queens · block 7334, lot 70"
    assert " - " not in line and line.count("Queens") == 1


# =========================================================================== D6
def test_d6_every_scheduled_building_uses_one_phrase() -> None:
    doc = benchmark()
    text = visible_text(build_report_html(doc, env=_LANE_E))
    area = readers.worked_buildings(doc)[0]["scheduled_display"]
    assert f"Scheduled floor area: {area} sq ft; site fit unverified" in text
    assert f"scheduled {area} sq ft" not in text  # no abbreviated mention


# =========================================================================== V-C1
def test_vc1_apartment_estimate_states_its_usable_share() -> None:
    doc = benchmark()
    text = visible_text(build_report_html(doc, env=_LANE_E))
    estimate = readers.apartment_estimate_text(doc["building_alternatives"][0]["capacity_estimate"])
    # the share range (0.60 to 0.75) and the HPD size are stated so the range reconciles.
    assert "0.60 to 0.75 of the floor area inside apartments" in estimate
    assert "unvalidated sensitivity range" in estimate
    assert "chosen starting apartment size of 700 sq ft measured as HPD" in estimate
    assert estimate in text


# =========================================================================== V-C2
# Prose fields in the results document (not metric labels, which legitimately
# recur as table row names): the long sentences a report must state once.
_PROSE_KEYS = {"reason", "statement", "assumption", "settled_by", "resolved_by"}


def _long_document_sentences(obj, out: set[str], key: str | None = None) -> None:
    if isinstance(obj, str):
        normalized = " ".join(obj.split())
        if key in _PROSE_KEYS and len(normalized) >= 60:
            out.add(normalized)
    elif isinstance(obj, dict):
        for name, value in obj.items():
            _long_document_sentences(value, out, name)
    elif isinstance(obj, list):
        for value in obj:
            _long_document_sentences(value, out, key)


def test_vc2_no_long_document_sentence_printed_twice() -> None:
    doc = benchmark()
    text = " ".join(visible_text(build_report_html(doc)).split()).lower()
    sentences: set[str] = set()
    _long_document_sentences(doc, sentences)
    for sentence in sentences:
        # case-normalized so the lot-area condition (quoted after "holds if …") matches.
        assert text.count(sentence.lower()) <= 1, (
            f"document sentence printed twice: {sentence[:70]!r}"
        )
    # the two sentences the review flagged each appear once.
    assert text.count("by portion the law allows up to 100 percent coverage") == 1
    assert text.count("if the recorded lot area of 10,075 sq ft is confirmed") == 1
    # The long apartment-estimate sentence now prints ONCE: on the scenario sheet (page 4),
    # its full calculation. Page 1 shows the range "Estimate 17-22" and links here, so the
    # duplicate on page 1 is gone (D-094 R013, R2-F14; M5-T165).
    estimate = readers.apartment_estimate_text(doc["building_alternatives"][0]["capacity_estimate"])
    assert text.count(estimate.lower()) == 1


# =========================================================================== Q3
def _benchmark_map_context() -> dict:
    """The recorded 215-16 Northern WINDOW map document (M5-T154), built through the
    real connectors from recorded bytes - its subject outline matches the benchmark
    results lot outline, so the one-outline check (Y5) passes."""
    from app.api.v1.report_context import recorded_pack_provider

    pack = (
        Path(__file__).resolve().parents[2] / "fixtures" / "benchmark_215_16_northern_window"
    )
    return recorded_pack_provider(pack)("4073340070", "q3")


def test_q3_coverage_and_maps_with_and_without_a_map_document() -> None:
    doc = benchmark()
    from app.drawings.report import coverage

    # without a map document: context maps are Not yet, and the location sheet prints
    # one short line (never a blank sheet, S6) - no Context-maps section.
    without = build_report_html(doc)
    groups_without = dict(coverage.coverage_groups(doc, maps_present=False))
    assert "Context maps" in groups_without["Not yet"]
    # No Context-maps SECTION on the site-and-context page (slice bounded to that page).
    # The coverage inventory has left the report (M5-T165); "Context maps" now appears only
    # in the appendix's material-exclusions block, which is out of this slice.
    site = without[without.index('id="site-and-context"'):without.index('id="option-comparison"')]
    assert "Context maps" not in visible_text(site)

    # with a map document whose maps render: context maps are In this report, and shown.
    with_maps = build_report_html(doc, map_context=_benchmark_map_context(), env=_LANE_E)
    groups_with = dict(coverage.coverage_groups(doc, maps_present=True))
    assert "Context maps" in groups_with["In this report"]
    start = with_maps.index('id="site-and-context"')
    site = with_maps[start:with_maps.index('id="option-comparison"')]
    assert "<svg" in site
    text = visible_text(with_maps)
    # the appendix scope note now reads maps_present (M5-T179): with maps printed,
    # 'Context maps' is not listed among the report's exclusions.
    assert "Context maps" not in text


# =============================================== drawing frame (ruling X9); run once integrated
_HAS_FRAME = "frame" in inspect.signature(kit.render_site_plan).parameters
_HAS_FLOOR_STACK = hasattr(kit, "render_floor_stack")
_HAS_SUMMARY = _HAS_FRAME and drawings_embed.summary_frame_available(benchmark(), env=_LANE_E)


@pytest.mark.skipif(not _HAS_FRAME, reason="render_site_plan has no report frame yet (M5-T152)")
def test_site_plan_report_frame_renders() -> None:
    html = build_report_html(benchmark(), env=_LANE_E)
    site = html[html.index('id="site-and-context"'):html.index('id="option-comparison"')]
    assert "<svg" in site


@pytest.mark.skipif(not _HAS_FLOOR_STACK, reason="render_floor_stack missing (M5-T152)")
def test_floor_stack_report_frame_renders() -> None:
    html = build_report_html(benchmark(), env=_LANE_E)
    scenario = html[html.index('id="scenario-B"'):]
    assert "<svg" in scenario


@pytest.mark.skipif(not _HAS_SUMMARY, reason="summary frame not distinct yet (M5-T152)")
def test_summary_frame_site_plan_in_decision_summary() -> None:
    html = build_report_html(benchmark(), env=_LANE_E)
    decision = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    assert 'class="summary-figure"' in decision
