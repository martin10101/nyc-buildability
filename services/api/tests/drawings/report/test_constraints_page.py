"""The 'What constrains the design?' sheet (M5-T166, S5-S8, S10, S12).

Page 2 keeps one neighbourhood locator; the constraints sheet carries the large
dimensioned close frame, a compact 3x2 standard / qualifying-housing heights table
(labels from the document), the constraint rows each with its state, the 'No
building placed' legend entry (the not-placed sentence stays on the scenario
sheet), and the "Map geometry only ..." honesty line is printed once in the whole
report. Every expected figure is read from the document, never retyped.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from app.drawings.report import build_report_html, readers

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
_WINDOW_PACK = Path(__file__).resolve().parents[2] / "fixtures" / "benchmark_215_16_northern_window"
_LANE_E = {"LANE_E_ENABLED": "1"}
_MAP_DRAWINGS = {"site_context_plan", "neighbourhood_map", "block_map",
                 "location_map", "zoning_map"}


def benchmark() -> dict:
    return json.loads((_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8"))


def map_context() -> dict:
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


def _svg_drawings(html: str) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    for tag in re.findall(r"<svg\b[^>]*>", html):
        dr = re.search(r'data-drawing="([^"]+)"', tag)
        w = re.search(r'width="([-\d.]+)pt"', tag) or re.search(r'width="([-\d.]+)"', tag)
        if dr and w:
            out.append((dr.group(1), float(w.group(1))))
    return out


# =========================================================================== S5
def test_s5_at_most_three_map_figures_each_a_distinct_job() -> None:
    maps = [(d, w) for d, w in _svg_drawings(_report_with_maps()) if d in _MAP_DRAWINGS]
    assert len(maps) <= 3
    assert len(set(maps)) == len(maps)  # each a distinct job (drawing + printed size)
    names = [d for d, _w in maps]
    assert names.count("block_map") == 0           # the block close-up is not printed
    assert names.count("neighbourhood_map") == 1   # the locator
    assert names.count("site_context_plan") == 2   # the compact (page 1) + large (page 3)


# =========================================================================== S6
def test_s6_map_geometry_only_appears_once() -> None:
    assert _report_with_maps().count("Map geometry only") == 1


# =========================================================================== S7
def test_s7_heights_table_is_three_by_two_from_the_document() -> None:
    site = _site_section(_report_with_maps())
    constraints = visible_text(site[site.index("What constrains the design?"):])
    for label in ("Minimum base height", "Maximum base height", "Maximum building height"):
        assert label in constraints
    assert "Standard" in constraints and "Qualifying housing" in constraints
    # the standard and qualifying figures sit side by side (max building: 55 / 65 ft).
    assert "55 ft" in constraints and "65 ft" in constraints
    # the long per-row document label is no longer printed in the heights table.
    assert "with qualifying affordable or senior housing" not in constraints


def test_s7_coverage_once_and_no_bare_not_shown() -> None:
    site = visible_text(_site_section(build_report_html(benchmark())))
    assert site.count("Maximum lot coverage") == 1
    assert "Not shown" not in site


def test_s7_context_maps_svg_only_with_a_map_document() -> None:
    without = _site_section(build_report_html(benchmark()))
    assert "<svg" not in without
    assert "Context maps" not in visible_text(without)
    assert "<svg" in _site_section(_report_with_maps())


def test_s7_heights_table_absent_without_envelope_values() -> None:
    doc = benchmark()
    doc["answers"]["permitted_envelope"] = {
        "status": "not_available", "reason": "x", "reason_kind": "missing_input"}
    html = build_report_html(doc)  # no crash, no heights table
    assert "Height limits for this lot" not in visible_text(html)


# =========================================================================== S8
def test_s8_no_building_placed_legend_on_site_sentence_on_scenario() -> None:
    html = _report_with_maps()
    site = visible_text(_site_section(html))
    scenario = visible_text(html[html.index('id="scenario-B"'):])
    # M5-T172: the benchmark now places building B, so the not-placed sentence is GONE from the
    # scenario sheet; the site close-frame context map keeps the 'No building placed' legend
    # (that map draws no building massing).
    assert "No building placed" in site                 # the close frame legend entry
    assert readers.NOT_PLACED_LINE not in site          # not the full sentence
    assert readers.NOT_PLACED_LINE not in scenario      # the sentence is gone once placed
    # A not-placed document (floor plates withheld) still carries the sentence on the scenario
    # sheet only; kept as explicit not-placed coverage now the benchmark is placed (S13).
    import copy

    doc = copy.deepcopy(benchmark())
    doc["geometry"]["floor_plates"] = {
        "status": "not_available", "reason": "x", "reason_kind": "rule_not_implemented"}
    unplaced = build_report_html(doc, map_context=map_context(), env=_LANE_E)
    assert readers.NOT_PLACED_LINE in visible_text(unplaced[unplaced.index('id="scenario-B"'):])
    assert readers.NOT_PLACED_LINE not in visible_text(_site_section(unplaced))


# =========================================================================== M5-T170 S18 (DB-266)
def test_m5t170_s18_page3_lists_setback_and_street_wall_with_no_envelope_row() -> None:
    # A 1.5.0 document that carries a rear_yard block but NO envelope row for setback or street
    # wall (DB-266: main 2bcdb05a's benchmark dropped both page-3 rows while page 8 kept them). The
    # page-3 table must still LIST both, falling back to the 1.4.0 wording, never silently omitted.
    import copy

    doc = copy.deepcopy(benchmark())
    doc.pop("envelope_rows", None)  # rear-yard-only 1.5.0 document
    text = visible_text(_site_section(build_report_html(doc)))
    assert "Setback above the base" in text
    assert "Not worked out yet" in text  # the 1.4.0 fall-back state, not an omission
    assert "Street wall" in text
    assert "Not checked" in text
    # the side yard has no 1.4.0 row, so with no envelope row it is not listed (no invented row).
    assert "Side yard" not in text


# =========================================================================== S10
def test_s10_site_section_words_within_the_baseline() -> None:
    off = build_report_html(benchmark())
    site = off[off.index('id="site-and-context"'):off.index('id="option-comparison"')]
    # M5-T170: page 3 now shows the three NB-06 envelope readings (setback, street wall, side
    # yard) as short conditional readings, replacing the 1.4.0 "Not worked out yet" / "Not checked"
    # fall-backs and adding the side-yard row (D-094 R037/R043). The G0 baseline was 199; the three
    # applied readings add ~16 words. M5-T170 round 2 (G4 advisory 4): the side-yard row now carries
    # the same "(see item N)" cross-reference the setback and street-wall rows have, adding 4 words
    # (216 -> 220); each reading is still one short sentence.
    assert len(visible_text(site).split()) <= 220


# =========================================================================== S12
def test_s12_six_sections_and_page_one_wrapper_untouched() -> None:
    html = _report_with_maps()
    # M5-T169: pages 5 and 6 merged into one evidence appendix (five sections).
    for sid in ("decision-summary", "site-and-context", "option-comparison",
                "scenario-B", "appendix"):
        assert f'id="{sid}"' in html
    decision = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    # the page-1 wrapper (class summary-figure, its short caption) is unchanged.
    assert 'class="summary-figure"' in decision
    assert "The lot among its neighbours (city map; not surveyed)." in decision


def test_the_frame_is_the_last_block_so_no_table_is_orphaned() -> None:
    # rework 3 addition: the close frame cannot be shrunk below ~416 pt (a dimension
    # label would fall under 8.5 pt), and the constraints section is more than one A4
    # page, so the large frame is placed AFTER the two constraint tables. The tables sit
    # together with the lot-area basis; the frame - the dominant visual - takes its own
    # page. This prevents the 4-row constraint table being orphaned alone on a blank
    # page after the frame. (A true page-break check needs a browser and runs in the
    # print / visual H2 check, not this HTML unit test; here the block ORDER is pinned.)
    site = _site_section(_report_with_maps())
    body = site[site.index("What constrains the design?"):]
    assert 'data-drawing="site_context_plan"' in body  # the close frame is on this page
    frame_at = body.index('data-drawing="site_context_plan"')
    assert body.index("Height limits for this lot") < frame_at
    assert body.index("Zoning constraints for this lot") < frame_at
