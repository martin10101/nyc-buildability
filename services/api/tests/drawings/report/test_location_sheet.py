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

import pytest

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
    # the two location thumbnails are titled so the reader knows which is which.
    assert "Neighbourhood" in location and "Block close-up" in location


def test_page1_carries_the_summary_frame_site_plan() -> None:
    # Page 1's small site figure is the COMPACT summary-frame site context plan,
    # beside the answers (rework 1 fix 1): a summary-figure, not the full-size plan.
    html = _report_with_maps()
    decision = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    assert "<svg" in decision
    assert 'class="summary-figure"' in decision  # beside the answers, as in wave 21
    # Page 1's thumbnail carries a SHORT caption that fits its column (rework 2 fix
    # 1); the long sources-and-dates caption is NOT on page 1.
    assert "The lot among its neighbours (city map; not surveyed)." in decision
    assert "Sources:" not in decision
    # the full-size plan is printed ONCE, on the constraints sheet - not on page 1.
    site = _site_section(html)
    constraints = site[site.index("What constrains the design?"):]
    assert "<svg" in constraints


def test_fix1_captions_wrap_and_figure_column_is_bounded() -> None:
    # rework 2 fix 1: page 1's figure column has a bounded width so its caption
    # wraps inside it, and no caption element is set to nowrap.
    from app.drawings.report import layout

    css = layout.report_css("H", "F")
    assert re.search(r"\.summary-figure\s*\{[^}]*flex:\s*0 0 88mm", css), "figure column bounded"
    for rule in css.split("}"):
        if "white-space: nowrap" in rule:
            assert "figcaption" not in rule and "figure-note" not in rule, (
                f"a caption is set to nowrap: {rule.strip()!r}"
            )


def _caption_texts(markup: str) -> list[str]:
    """Every caption on the page: the figcaptions (full-size plan) and the location
    sheet's caption paragraphs (shown in the right column, class figure-note)."""
    caps = re.findall(r"<figcaption>(.*?)</figcaption>", markup, re.S)
    caps += re.findall(r'<p class="figure-note">(.*?)</p>', markup, re.S)
    return [_html.unescape(c) for c in caps]


def test_location_page_layout_two_co_equal_wide_maps() -> None:
    # The location page carries the neighbourhood map and the block close-up as two
    # CO-EQUAL full-width wide strips stacked (corrections T156-C2), two drawings in
    # all; the full-size site plan is NOT here (it stays on the constraints sheet).
    site = _site_section(_report_with_maps())
    location = site[site.index("Where is the lot?"):site.index("What constrains the design?")]
    assert location.count('class="location-wide-figure"') == 2  # two co-equal figures
    assert location.count("<figure") == 2 and location.count("<svg") == 2
    assert "Neighbourhood" in location and "Block close-up" in location
    # each wide figure carries its own sources-and-dates caption.
    assert location.count('class="figure-note"') == 2


def test_s1_captions_name_sources_and_their_dates() -> None:
    # Each location drawing is captioned with its sources and dates in plain words
    # (Y7): one short "Sources: ..." line with a readable title and an edit date for
    # each layer the drawing shows.
    captions = _caption_texts(_site_section(_report_with_maps()))
    assert len(captions) >= 3
    assert all(cap.strip() for cap in captions)  # every drawing is captioned
    sourced = [cap for cap in captions if cap.startswith("Sources:")]
    assert sourced, "a location caption opens with a plain 'Sources:' line"
    joined = " ".join(captions)
    # readable source titles from the report package's wording (never code words).
    assert "NYC City Planning, MapPLUTO" in joined
    assert "NYC Digital City Map street centre lines" in joined
    # the recorded source edit dates reach the caption in plain words, each once.
    for date in ("9 Sep 2026", "27 Sep 2026", "1 Dec 2025"):
        assert date in joined, f"source edit date {date} missing from the captions"


def test_s1_captions_are_plain_no_dataset_id_no_doubled_date() -> None:
    # Caption rules (rework 1 fix 3): no dataset id, no "via NYC Open Data", no
    # terms-of-use text, no "last edited" doubling, and each date exactly once.
    captions = _caption_texts(_report_with_maps())
    joined = " ".join(captions)
    low = joined.lower()
    assert "5zhs" not in low and "via nyc open data" not in low
    assert "terms of use" not in low
    assert "last edited" not in low  # no "Source edit date … (last edited …)" doubling
    assert "http" not in low
    assert re.search(r"\b[a-z]+_[a-z]+\b", joined) is None
    # each date appears once per caption (no doubling within a caption).
    for cap in captions:
        for date in ("9 Sep 2026", "27 Sep 2026", "1 Dec 2025"):
            assert cap.count(date) <= 1, f"date {date} doubled in a caption"


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
    assert readers.building_not_placed(doc) is True  # the document gives no floor plate
    line = readers.NOT_PLACED_LINE
    # the fixed sentence, not spliced from the document's reason text (fix 4).
    assert line == ("No building is placed on this plan yet: the program does not yet "
                    "work out where a building sits on the lot.")
    html = build_report_html(doc, map_context=map_context(), env=_LANE_E)
    site = _site_section(html)
    scenario = html[html.index('id="scenario-B"'):]
    assert line in visible_text(site)
    assert line in visible_text(scenario)
    # the document's own reason text is never spliced into the report.
    assert "No floor plate is drawn" not in visible_text(html)


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


# ================================================ QA C3/C4: partially-unavailable map
def _map_with_layer_unavailable(layer: str) -> dict:
    """The benchmark map document with one layer marked not_available (streets
    stay available, so the one-outline check still passes and the location sheet
    still draws the neighbourhood)."""
    doc = copy.deepcopy(map_context())
    doc["map_context"][layer] = {
        "status": "not_available",
        "reason": "This layer is not available for this area.",
        "reason_kind": "source_unavailable",
    }
    return doc


@pytest.mark.parametrize("layer", ["tax_lots", "building_footprints"])
def test_c4_constraints_falls_back_to_lot_only_when_a_layer_is_unavailable(layer: str) -> None:
    # QA C3/C4: the one-outline check passes but a layer the site plan needs is not
    # available, so report_plan is a non-drawing Embedded. The constraints sheet must
    # fall back to today's lot-only plan WITH its tax-map limitation line (S6/R843),
    # never print the drawing's reason line.
    doc = _map_with_layer_unavailable(layer)
    html = build_report_html(benchmark(), map_context=doc, env=_LANE_E)
    site = _site_section(html)
    constraints = site[site.index("What constrains the design?"):]
    assert "<svg" in constraints  # today's lot-only plan is drawn
    # the lot-only plan's own tax-map limitation caption, not the map-based plan.
    assert "Approximate" in visible_text(constraints)
    assert "Sources:" not in constraints  # not the site-context plan among surroundings
    # the layer's reason line never reaches the report.
    assert "This layer is not available for this area." not in visible_text(html)


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
