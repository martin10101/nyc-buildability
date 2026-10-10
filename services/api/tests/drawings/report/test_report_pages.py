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


REASONS_IN_ORDER = (
    "What can I potentially build?",
    "What constrains the design?",
    "How do the options compare?",
    "What is this option?",
    "What remains unresolved, and what would resolve it?",
    "How was this derived?",
)
SECTION_IDS_IN_ORDER = (
    "decision-summary", "site-and-context", "option-comparison",
    "scenario-", "assumptions-open-items", "calculations-evidence",
)


# =========================================================================== S1
def test_s1_six_page_types_in_order() -> None:
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
    assert html.count('class="report-page"') == 7


def test_s1_benchmark_has_six_pages() -> None:
    assert build_report_html(benchmark()).count('class="report-page"') == 6


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
def test_s5_eleven_options_shared_limitations_once() -> None:
    doc = benchmark()
    rows = options.option_rows(doc)
    assert [r["ordinal"] for r in rows] == list(range(1, 12))
    assert [r["name"] for r in rows] == [name for _ordinal, name in options.ELEVEN_OPTIONS]
    assert len({r["status_label"] for r in rows}) > 1
    assert len({r["allowance_area"] for r in rows}) > 1
    text = visible_text(build_report_html(doc))
    for limitation in options.shared_limitations(doc):
        assert text.count(limitation["sentence"]) == 1, limitation["sentence"]
    assert "Building A – not worked" in text  # en dash (A6)


def test_f7_columns_chart_and_units() -> None:
    doc = benchmark()
    html = build_report_html(doc, env=_LANE_E)
    text = visible_text(html)
    for header in ("Floor-area allowance", "Scheduled building", "Limitation"):
        assert header in text
    assert "No scheduled building is available to chart yet." not in text
    assert 'class="bar-chart"' in html
    assert "sq ft sq ft" not in text and "FAR FAR" not in text
    # A6: allowance area and FAR are kept apart (each on its own line).
    assert "20,150 sq ft" in text and "FAR 2.0" in text
    assert "24,180 sq ft" in text and "FAR 2.4" in text
    assert "None scheduled" in text
    # A6: the Limitation column cells carry the number only (no "Limitation 2" in a cell).
    comparison = html[html.index('id="option-comparison"'):html.index('id="scenario-B"')]
    assert "Limitation 2" not in visible_text(
        comparison[comparison.index("<tbody"):comparison.index("</table>")]
    )


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
    # report's. The report itself types no figure (ruling X7).
    text = visible_text(build_report_html(doc))
    for token in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        value = float(token.replace(",", ""))
        assert any(round(value, k) in allowed for k in (0, 1, 2, 3, 4, 6)), (
            f"number {token!r} is not in the results document"
        )


# =========================================================================== S10
def test_s10_partial_data_every_page() -> None:
    html = build_report_html(partial_document())
    for sid in ("decision-summary", "site-and-context", "option-comparison",
                "scenario-none", "assumptions-open-items", "calculations-evidence"):
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
def test_f8_open_items_short_effect_and_full_reason() -> None:
    html = build_report_html(benchmark())
    text = visible_text(html)
    assert "Effect on the answer" in text
    assert "No legal apartment limit is shown." in text
    assert "rear yard is not known beyond the corner area" in text
    assert "class=\"reason-row\"" in html


def test_a3_not_checked_items_have_no_redundant_detail() -> None:
    # Only items whose full reason differs from the title/effect get a reason row.
    doc = benchmark()
    expected = sum(
        1 for item in readers.open_items(doc)
        if item.get("reason") and item["reason"] not in (item["effect"], item["title"])
    )
    html = build_report_html(doc)
    assert html.count('class="reason-row"') == expected
    # the not-checked items (street wall, placement, parking) contribute no reason row.
    assert expected < len(readers.open_items(doc))


# =========================================================================== F10 / D9
def test_f10_d9_coverage_compact_block_on_decision_summary() -> None:
    html = build_report_html(benchmark())
    decision = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    text = visible_text(decision)
    # D9: a compact block grouped by state, on the decision summary.
    assert "What this report covers" in text
    assert "In this report:" in text and "Partly:" in text and "Not yet:" in text
    assert "1 of 11 options worked" in text
    for further in ("Comparable sales nearby", "Context maps", "Tax abatement eligibility"):
        assert further in text
    # the owner-held section is marked.
    assert "Financial analysis inputs (held)" in text
    # D9: the coverage table is removed from the assumptions page (stated once).
    assumptions = html[
        html.index('id="assumptions-open-items"'):html.index('id="calculations-evidence"')
    ]
    assert "What this report covers" not in visible_text(assumptions)
    assert "Coverage of the promised sections" not in visible_text(assumptions)


# =========================================================================== F11
def test_f11_evidence_inputs_label_key_and_nowrap() -> None:
    html = build_report_html(benchmark())
    text = visible_text(html)
    assert "Inputs and their sources" in text
    assert "Recorded lot area" in text and "Zoning district" in text
    assert "Lot frontage" in text  # A7: the document's label, not "Front lot line"
    assert "Lot within 100 ft of the street-line intersection" in text  # A7
    # envelope law sections present (not only 23-22); the number never breaks (A7).
    assert "23-432" in text
    assert '<span class="nowrap">23-432</span>' in html
    # the owner's exact R783 wording and the "Not used in this report." note.
    assert "Supported by completed checks and evidence. Not used in this report." in text
    assert "Prepared but subject to confirmation or revision." in text
    assert 'class="nowrap"' in html
    assert "the figures below are read from the result" not in text


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
    # the two sentences the review flagged each appear once; the lot-area item points away.
    assert text.count("by portion the law allows up to 100 percent coverage") == 1
    assert text.count("if the recorded lot area of 10,075 sq ft is confirmed") == 1
    assert "see site and context for the lot-area basis." in text
    # the estimate line (composed; carried on pages 1 and 4) is the allowed repeat.
    estimate = readers.apartment_estimate_text(doc["building_alternatives"][0]["capacity_estimate"])
    assert text.count(estimate.lower()) == 2


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
    assert "Context maps" not in visible_text(without[without.index('id="site-and-context"'):])

    # with a map document whose maps render: context maps are In this report, and shown.
    with_maps = build_report_html(doc, map_context=_benchmark_map_context(), env=_LANE_E)
    groups_with = dict(coverage.coverage_groups(doc, maps_present=True))
    assert "Context maps" in groups_with["In this report"]
    start = with_maps.index('id="site-and-context"')
    site = with_maps[start:with_maps.index('id="option-comparison"')]
    assert "<svg" in site
    text = visible_text(with_maps)
    assert "Context maps" in text  # in the coverage inventory


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
