"""Acceptance scenarios S1-S11 for the report generator (task M5-T151).

Every expected figure is READ FROM THE DOCUMENT, never retyped: the tests load
the committed fixtures and compare against values taken from those same
documents. Drawing-frame behaviour (ruling X9) is exercised by the
skipped-until-integration tests at the end; they run once M5-T152's ``frame``
keyword and ``render_floor_stack`` exist.
"""

from __future__ import annotations

import html as _html
import inspect
import json
import re
from pathlib import Path

import pytest

from app.drawings import kit
from app.drawings.report import build_report_html, layout, options, readers
from app.drawings.report.labels import FORBIDDEN_RESULT_WORDS

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)


def load_results(name: str) -> dict:
    return json.loads((_FIXTURES / f"{name}.json").read_text("utf-8"))


def benchmark() -> dict:
    return load_results("recorded_215_16_northern_journey")


def two_buildings_document() -> dict:
    """Building A and B both worked, copied from the committed 1.4.0 fixtures (the
    same shape apps/web/src/test-support/results-two-buildings.ts builds). No
    number is retyped; both buildings come from committed fixtures."""
    base = benchmark()
    building_a = load_results("synthetic_coverage_by_portion_available_contract_1_4_0")[
        "building_alternatives"
    ][0]
    building_b = load_results("synthetic_building_alternatives_contract_1_4_0")[
        "building_alternatives"
    ][0]
    base["results_id"] = "synthetic_two_worked_buildings"
    base["building_alternatives"] = [building_a, building_b]
    base["buildings_not_worked"] = []
    return base


def partial_document() -> dict:
    """S10: geometry not available, no worked building, every answer withheld, no
    map document."""
    return {
        "contract_version": "1.4.0",
        "revision": 1,
        "computed_at": "2026-10-03T00:00:00Z",
        "lot_selection_statement": "Based on the lots you selected",
        "answers": {
            "floor_area_allowance": {
                "status": "not_available", "reason": "x", "reason_kind": "missing_input"
            },
            "permitted_envelope": {
                "status": "not_available", "reason": "x", "reason_kind": "missing_input"
            },
            "building_option": {
                "status": "not_available", "reason": "x", "reason_kind": "rule_not_implemented"
            },
        },
        "geometry": {"status": "not_available", "reason": "x", "reason_kind": "missing_input"},
        "scope": {
            "lot": {
                "borough": "Queens", "block": "7334", "lot": "70",
                "display": "Queens block 7334, lot 70", "bbl": "4073340070",
            },
            "assumptions": [],
        },
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
    "decision-summary",
    "site-and-context",
    "option-comparison",
    "scenario-",
    "assumptions-open-items",
    "calculations-evidence",
)


# =========================================================================== S1
def test_s1_six_page_types_in_order_benchmark() -> None:
    html = build_report_html(benchmark())
    positions = [html.index(f'id="{sid}') for sid in SECTION_IDS_IN_ORDER]
    assert positions == sorted(positions), "page types are not in the required order"
    text = visible_text(html)
    for question in REASONS_IN_ORDER:
        assert question in text, f"missing reader question: {question}"
    # one scenario sheet (building B); a not-worked building is a row, not a sheet.
    assert html.count('id="scenario-B"') == 1
    assert 'id="scenario-A"' not in html


def test_s1_two_worked_buildings_get_two_sheets() -> None:
    html = build_report_html(two_buildings_document())
    assert html.count('id="scenario-A"') == 1
    assert html.count('id="scenario-B"') == 1
    assert html.count('class="report-page"') == 7


def test_s1_benchmark_has_six_pages() -> None:
    assert build_report_html(benchmark()).count('class="report-page"') == 6


# =========================================================================== S2
def test_s2_one_sheet_size_and_page_furniture() -> None:
    css = layout.report_css()
    assert "size: A4 portrait" in css
    assert css.count("@page") == 1, "there must be exactly one @page rule"
    assert css.count("size: A4") == 1, "exactly one page size is declared"
    assert "margin: 14mm" in css
    for other in ("A3", "A5", "Letter", "legal", "Tabloid"):
        assert f"size: {other}" not in css, f"a second page size leaked: {other}"
    assert "counter(page)" in css and "counter(pages)" in css
    assert "string(running-identity)" in css and "string-set:" in css
    assert "@top-left" in css and "@bottom-right" in css
    assert "break-before: page" in css
    assert "table-header-group" in css
    assert "break-inside: avoid" in css


# =========================================================================== S3
def test_s3_scheduled_wording_and_no_forbidden_words() -> None:
    doc = benchmark()
    html = build_report_html(doc)
    text = visible_text(html)
    area = readers.worked_buildings(doc)[0]["scheduled_display"]
    assert f"Scheduled floor area: {area} sq ft; site fit unverified" in text
    low = text.lower()
    assert [w for w in FORBIDDEN_RESULT_WORDS if w in low] == []
    # 'Verified' appears only in the label key's definition row.
    assert text.count("Verified") == 1


# =========================================================================== S4
FORBIDDEN_SUBSTRINGS = ("HTTP", "endpoint", "fixture", "flag", "wiring", "backlog", "owed")
STATUS_CODES = ("200", "301", "400", "401", "403", "404", "405", "422", "429", "500", "502", "503")


def _assert_no_developer_info(text: str) -> None:
    for token in FORBIDDEN_SUBSTRINGS:
        assert token.lower() not in text.lower(), f"developer word leaked: {token}"
    assert re.search(r"\b[a-z]+_[a-z]+\b", text) is None, "a snake_case word leaked"
    for word in ("None", "null", "true", "false"):
        assert re.search(rf"\b{word}\b", text) is None, f"{word} leaked"
    assert re.search(r"\bDB-\d|\bR\d{3}\b|\bM\d+-T\d+\b", text) is None, "an internal id leaked"
    for ref in ("question C1", "question D1", "question B6"):
        assert ref not in text
    for code in STATUS_CODES:
        assert f"HTTP {code}" not in text and f"status {code}" not in text


def test_s4_no_developer_information_benchmark() -> None:
    _assert_no_developer_info(visible_text(build_report_html(benchmark())))


def test_s4_no_developer_information_partial() -> None:
    _assert_no_developer_info(visible_text(build_report_html(partial_document())))


# =========================================================================== S5
def test_s5_eleven_options_shared_limitations_once() -> None:
    doc = benchmark()
    rows = options.option_rows(doc)
    assert [r["ordinal"] for r in rows] == list(range(1, 12))
    assert [r["name"] for r in rows] == [name for _ordinal, name in options.ELEVEN_OPTIONS]
    labels_col = {r["status_label"] for r in rows}
    results_col = {r["result"] for r in rows}
    assert len(labels_col) > 1, "the status column repeats one state on every row"
    assert len(results_col) > 1, "the result column repeats one state on every row"
    text = visible_text(build_report_html(doc))
    assert text.count(options.SHARED_LIMITATION_1) == 1
    assert text.count(options.SHARED_LIMITATION_2) == 1
    # building A appears as not worked, with the document's own reason.
    building_a = doc["buildings_not_worked"][0]
    assert building_a["reason"] in text


# =========================================================================== S6
def test_s6_no_min_base_contradiction() -> None:
    doc = benchmark()
    assert readers.worked_buildings(doc)[0]["below_min_base"] is False
    text = visible_text(build_report_html(doc))
    assert "below the minimum base height" not in text


def test_s6_below_min_base_shown_only_when_document_says_so() -> None:
    doc = two_buildings_document()
    doc["building_alternatives"][0] = {**doc["building_alternatives"][0], "below_min_base": True}
    text = visible_text(build_report_html(doc))
    assert "below the minimum base height" in text


class _FakeDrawing:
    def __init__(self, svg: str) -> None:
        self.svg = svg
        self.caption = "Context map"
        self.notes = ()
        self.attribution = "Map attribution"


def _fake_map_render(_doc, *, frame: str = "report", env=None):
    return _FakeDrawing('<svg role="img"></svg>')


def test_s6_coverage_inventory_claims_maps_only_when_present(monkeypatch) -> None:
    doc = benchmark()
    without = visible_text(build_report_html(doc))
    assert "Context maps are not included in this report." in without
    monkeypatch.setattr("app.drawings.maps.render_location_map", _fake_map_render, raising=False)
    monkeypatch.setattr("app.drawings.maps.render_zoning_map", _fake_map_render, raising=False)
    with_maps = build_report_html(doc, map_context={"map_context": {"zoning_districts": {}}})
    assert "Context maps are not included in this report." not in visible_text(with_maps)
    assert "<figure>" in with_maps


# =========================================================================== S7
def test_s7_lot_area_basis_quoted_not_computed() -> None:
    doc = benchmark()
    basis = readers.lot_area_basis(doc)
    assert basis is not None
    text = visible_text(build_report_html(doc))
    assert basis in text, "the lot-area basis is not quoted in the document's own words"
    assert "10,075" in basis and "10,387.99" in basis and "disagree" in basis
    assert "tax-map outline" in text.lower()


# =========================================================================== S8
ALL_FIXTURES = [p.stem for p in sorted(_FIXTURES.glob("*.json"))]
SIX_LABELS = ("Provisional", "Illustrative", "Conditional", "Pending verification", "Unresolved")


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_s8_labels_on_every_fixture(name: str) -> None:
    doc = load_results(name)
    html = build_report_html(doc)
    text = visible_text(html)
    # 'Verified' appears only in the label key (at most once).
    assert text.count("Verified") <= 1
    # at least one non-Verified label is shown.
    assert any(label in text for label in SIX_LABELS)
    # a withheld value shows "Not shown", never a fabricated figure, in the constraints table.
    for row in readers.withheld_values(readers.answer_block(doc, "permitted_envelope")):
        assert row["status_label"] in ("Unresolved", "Pending verification")


# =========================================================================== S9
def _rounded_forms(value: float) -> set[float]:
    return {round(float(value), k) for k in (0, 1, 2, 3, 4, 6)}


def _collect_numbers(obj, allowed: set[float]) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        allowed |= _rounded_forms(obj)
    elif isinstance(obj, str):
        for match in re.findall(r"\d[\d,]*(?:\.\d+)?", obj):
            try:
                allowed |= _rounded_forms(float(match.replace(",", "")))
            except ValueError:
                pass
    elif isinstance(obj, dict):
        for value in obj.values():
            _collect_numbers(value, allowed)
    elif isinstance(obj, list):
        for value in obj:
            _collect_numbers(value, allowed)


def test_s9_every_number_comes_from_the_document() -> None:
    doc = benchmark()
    allowed: set[float] = set()
    _collect_numbers(doc, allowed)
    # presentation ordinals derived from document counts (option order, limitations, list indices).
    ordinal_max = max(11, len(readers.assumptions(doc)), len(readers.open_items(doc)))
    for i in range(1, ordinal_max + 1):
        allowed |= _rounded_forms(i)
    text = visible_text(build_report_html(doc))
    for token in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        value = float(token.replace(",", ""))
        assert any(round(value, k) in allowed for k in (0, 1, 2, 3, 4, 6)), (
            f"number {token!r} is not in the results document"
        )


# =========================================================================== S10
def test_s10_partial_data_every_page_no_exception() -> None:
    html = build_report_html(partial_document())
    for sid in ("decision-summary", "site-and-context", "option-comparison",
                "scenario-none", "assumptions-open-items", "calculations-evidence"):
        assert f'id="{sid}"' in html
    text = visible_text(html)
    assert "The lot outline is not available for this property." in text
    assert "11. All programs combined" in text  # every option still listed
    assert "No building option has been worked for this property yet." in text


# =========================================================================== S11
def test_s11_escaping() -> None:
    doc = partial_document()
    doc["lot_selection_statement"] = 'A & B <script>alert(1)</script> "quoted" <img src=x>'
    doc["scope"]["assumptions"] = [
        {"key": "k", "value": "v", "statement": 'danger & <script>x</script> "q"'}
    ]
    html = build_report_html(doc)
    assert "<script" not in html.lower(), "an unescaped script element is present"
    assert "<img" not in html.lower(), "an unescaped element is present"
    assert "onerror=" not in html.lower() and "onclick=" not in html.lower()
    assert "&lt;script&gt;" in html, "the injected markup was not escaped"


# =============================================== skipped until M5-T152 integration (ruling X9)
_HAS_FRAME = "frame" in inspect.signature(kit.render_site_plan).parameters


@pytest.mark.skipif(not _HAS_FRAME, reason="render_site_plan has no report frame yet (M5-T152)")
def test_site_plan_report_frame(monkeypatch) -> None:
    monkeypatch.setenv("LANE_E_ENABLED", "1")
    from app.drawings.report import drawings_embed

    embedded = drawings_embed.embed_kit_drawing("render_site_plan", benchmark())
    assert embedded.is_drawing or embedded.short_line is not None


@pytest.mark.skipif(
    not hasattr(kit, "render_floor_stack"),
    reason="render_floor_stack does not exist yet (M5-T152)",
)
def test_floor_stack_report_frame(monkeypatch) -> None:
    monkeypatch.setenv("LANE_E_ENABLED", "1")
    from app.drawings.report import drawings_embed

    alternative = benchmark()["building_alternatives"][0]
    embedded = drawings_embed.embed_floor_stack(alternative)
    assert embedded.is_drawing or embedded.short_line is not None
