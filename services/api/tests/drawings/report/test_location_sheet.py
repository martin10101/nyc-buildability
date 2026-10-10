"""Acceptance scenarios for M5-T156 - the report shows where the lot is.

Page type 2 opens with the 'Where is the lot?' sheet (the neighbourhood map and
the block close-up), then 'What constrains the design?' with the site plan among
its surroundings, behind the one-outline check (ruling Y5). Captions name their
sources and dates (Y7); the 'not yet placed' line comes from the document's own
reason (Y8); there is no photo (Y9); the page-type list stays at six (Y10).

Every expected figure is READ FROM THE DOCUMENTS, never retyped. The drawings
themselves (M5-T155) are reworked in parallel, so these tests assert that each
drawing is PRESENT, CAPTIONED and on the RIGHT SHEET - never its bytes, label
positions or size (per the M5-T156 brief).
"""

from __future__ import annotations

import copy
import html as _html
import json
import re
from pathlib import Path

from app.drawings.report import build_report_html, coverage, page_location, readers

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
_WINDOW_PACK = Path(__file__).resolve().parents[2] / "fixtures" / "benchmark_215_16_northern_window"
_LANE_E = {"LANE_E_ENABLED": "1"}


def benchmark() -> dict:
    return json.loads((_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8"))


def map_context() -> dict:
    """The recorded 215-16 Northern window map document, built through the real
    connectors from recorded bytes (its subject outline matches the benchmark)."""
    from app.api.v1.report_context import recorded_pack_provider

    doc = recorded_pack_provider(_WINDOW_PACK)("4073340070", "test")
    assert doc is not None
    return doc


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<script.*?</script>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def _site_section(html: str) -> str:
    return html[html.index('id="site-and-context"'):html.index('id="option-comparison"')]


def _report_with_maps() -> str:
    return build_report_html(benchmark(), map_context=map_context(), env=_LANE_E)


# =========================================================================== S1
def test_s1_location_sheet_opens_page_type_two() -> None:
    html = _report_with_maps()
    site = _site_section(html)
    # 'Where is the lot?' opens page type 2, then 'What constrains the design?'.
    assert site.index("Where is the lot?") < site.index("What constrains the design?")
    # The location sheet lives INSIDE page type 2 - the page-type list stays at six.
    assert html.count('class="report-page"') == 6
    # it holds the neighbourhood map and the block close-up (two figures), and the
    # 'What constrains the design?' sheet holds the site plan among the surroundings.
    location = site[site.index("Where is the lot?"):site.index("What constrains the design?")]
    assert location.count("<figure") == 2 and location.count("<svg") == 2
    assert site.count("<svg") >= 3


def test_s1_captions_name_sources_and_their_dates() -> None:
    # Each location-sheet figure is captioned with its sources and dates in plain
    # words (Y7): the caption names a source and carries its last-edited date.
    site = _site_section(_report_with_maps())
    raw_caps = re.findall(r"<figcaption>(.*?)</figcaption>", site, re.S)
    captions = [_html.unescape(c) for c in raw_caps]
    assert len(captions) >= 3
    assert all(cap.strip() for cap in captions)  # every figure is captioned
    dated = [cap for cap in captions if "last edited" in cap]
    assert dated, "at least one caption names its source's last-edited date"
    # the recorded source edit dates reach the caption (from the map provenance).
    joined = " ".join(captions)
    for date in ("2026-09-09", "2025-12-01", "2026-09-27"):
        assert date in joined, f"source edit date {date} missing from the captions"
    # no URL, field name or code word in a caption (ruling X6/Y7).
    assert "http" not in joined.lower()
    assert re.search(r"\b[a-z]+_[a-z]+\b", joined) is None


def test_s1_six_page_types_unchanged() -> None:
    for sid in ("decision-summary", "site-and-context", "option-comparison",
                "scenario-B", "assumptions-open-items", "calculations-evidence"):
        assert f'id="{sid}"' in _report_with_maps()


# =========================================================================== S2
def test_s2_one_outline_check_passes_for_the_benchmark() -> None:
    doc = map_context()
    outline = doc["map_context"]["subject_lot"]["outline"]
    assert page_location.outlines_match(outline, readers.results_lot_outline(benchmark())) is True


def test_s2_moved_outline_drops_the_surroundings() -> None:
    # A map document whose outline is moved by 0.5 ft at an interior vertex fails
    # the 0.01-ft one-outline check: the surroundings are dropped and one
    # limitation line is printed; the site plan falls back to the lot-only plan.
    moved = copy.deepcopy(map_context())
    moved["map_context"]["subject_lot"]["outline"][0][2][0] += 0.5
    assert page_location.outlines_match(
        moved["map_context"]["subject_lot"]["outline"], readers.results_lot_outline(benchmark())
    ) is False
    html = build_report_html(benchmark(), map_context=moved, env=_LANE_E)
    site = _site_section(html)
    assert "The surroundings are not shown for this property" in visible_text(site)
    # with the surroundings dropped, the location sheet draws no map.
    location = site[site.index("Where is the lot?"):site.index("What constrains the design?")]
    assert "<svg" not in location


def test_s2_tolerance_is_one_hundredth_of_a_foot() -> None:
    # The check is exactly 0.01 ft: a 0.5-ft interior move must NOT match (this is
    # the test that catches a widened tolerance, e.g. 1 ft).
    moved = copy.deepcopy(map_context())
    moved["map_context"]["subject_lot"]["outline"][0][2][0] += 0.5
    results_outline = readers.results_lot_outline(benchmark())
    assert page_location.outlines_match(
        moved["map_context"]["subject_lot"]["outline"], results_outline
    ) is False


# =========================================================================== S3
def test_s3_not_yet_placed_on_site_plan_and_scenario_sheet() -> None:
    doc = benchmark()
    reason = readers.not_placed_reason(doc)
    assert reason  # read from /geometry/floor_plates/reason
    line = f"No building is placed on this plan yet: {reason}"
    html = build_report_html(doc, map_context=map_context(), env=_LANE_E)
    site = _site_section(html)
    scenario = html[html.index('id="scenario-B"'):]
    assert line in visible_text(site)
    assert line in visible_text(scenario)
    # the reason is the document's own, with any internal-field clause dropped.
    assert reason in doc["geometry"]["floor_plates"]["reason"]


# =========================================================================== S4
def test_s4_no_photo_no_empty_frame_no_photo_wording() -> None:
    html = _report_with_maps()
    site = _site_section(html)
    location = site[site.index("Where is the lot?"):site.index("What constrains the design?")]
    low = visible_text(location).lower()
    for word in ("photo", "street view", "aerial"):
        assert word not in low, f"photo wording leaked into the location sheet: {word!r}"
    # no raster image and no empty figure frame - every figure carries a drawing.
    assert "<img" not in location
    assert location.count("<figure") == location.count("<svg")
    # 'Aerial and street photographs' appears only under the scope list's 'Not yet'.
    groups = dict(coverage.coverage_groups(benchmark(), maps_present=True))
    assert any("Aerial and street photographs" in n for n in groups["Not yet"])
    assert all("Aerial and street photographs" not in n for n in groups.get("In this report", []))


# =========================================================================== S5
def test_s5_context_maps_moves_only_when_printed() -> None:
    doc = benchmark()
    not_printed = dict(coverage.coverage_groups(doc, maps_present=False))
    printed = dict(coverage.coverage_groups(doc, maps_present=True))
    assert "Context maps" in not_printed["Not yet"]
    assert "Context maps" not in printed.get("Not yet", [])
    assert "Context maps" in printed["In this report"]


# =========================================================================== S6
def test_s6_without_map_data_one_line_never_blank() -> None:
    # provider returns None (no map document): the location sheet prints one short
    # line, and the site plan is the lot-only plan (today's) with its own caption.
    html = build_report_html(benchmark(), env=_LANE_E)
    site = _site_section(html)
    assert "Where is the lot?" in site  # the sheet is present (never missing)
    location = site[site.index("Where is the lot?"):site.index("What constrains the design?")]
    assert "<svg" not in location  # no map figure
    assert "The surroundings are not shown for this property" in visible_text(location)
    # the 'What constrains the design?' sheet still shows today's lot-only site plan.
    constraints = site[site.index("What constrains the design?"):]
    assert "<svg" in constraints


def test_s6_resolve_returns_unavailable_without_a_document() -> None:
    s = page_location.resolve(None, benchmark(), env=_LANE_E)
    assert s.available is False and s.reason


# =========================================================================== S8
_FORBIDDEN_SUBSTRINGS = ("http", "endpoint", "fixture", "wiring", "backlog", "owed", "lane a")


def test_s8_no_developer_words_with_maps_present() -> None:
    text = visible_text(_report_with_maps())
    low = text.lower()
    for token in _FORBIDDEN_SUBSTRINGS:
        assert token not in low, f"developer wording leaked: {token}"
    assert re.search(r"\b[a-z]+_[a-z]+\b", text) is None, "a snake_case word leaked"
    for word in ("null", "true", "false"):
        assert re.search(rf"\b{word}\b", text) is None
    assert re.search(r"\bDB-\d|\bR\d{3}\b|\bM\d+-T\d+\b", text) is None
    assert text.count("Verified") <= 1


# =========================================================================== S9
def test_s9_presentation_contract_has_the_dated_entry() -> None:
    contract = (
        Path(__file__).resolve().parents[5] / "docs" / "design"
        / "ARCHITECT_PRESENTATION_CONTRACT.md"
    ).read_text("utf-8")
    assert "2026-10-10" in contract
    for row in ("R936", "R940"):
        assert row in contract
    assert "Where is the lot?" in contract
