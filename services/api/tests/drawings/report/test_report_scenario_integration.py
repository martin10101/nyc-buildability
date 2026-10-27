"""M5-T173 part B WIRING: the whole report renders every drawing first, builds ONE
drawn-content manifest from the rendered Embedded values, and every shown/drawn/placed/
fitted claim on pages 4, 5, 6 and the appendix reads that manifest - never a data field
(owner audit 2026-10-15c; D-094 R196/R198/R200/R201/R202/R203/R204/R205/R206/R277/R278).

One case per print state (the three the brief names - maps, kit fallback, drawings off -
plus the degenerate-footprint copy and the long-metadata copy). For each new-behaviour
claim the test asserts it honest and then flips the rendered INPUT (the footprint ring, the
Lane E flag, the map pack) and shows the claim text move, so the claim is proven to depend
on rendered content. Every expected figure is read from the document or the reference case
placement-building-b.json (33.34 ft tax map, 35.31 ft city map, 12,090 / 8,060 / 20,150 sq
ft); nothing is retyped and no value comes from a program run.
"""

from __future__ import annotations

import copy
import html as _html
import json
import re
from pathlib import Path

from app.drawings.kit.styles import style_for
from app.drawings.maps.placed_footprint import FOOTPRINT_KIND
from app.drawings.report import build_report_html, manifest

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
_WINDOW_PACK = Path(__file__).resolve().parents[2] / "fixtures" / "benchmark_215_16_northern_window"
_LANE_E = {"LANE_E_ENABLED": "1"}
# A degenerate (zero-area) ring: the engine "placed" the building but this shape draws nothing.
_ZERO_RING = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]


def benchmark() -> dict:
    return json.loads((_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8"))


def map_context() -> dict:
    from app.api.v1.report_context import recorded_pack_provider

    doc = recorded_pack_provider(_WINDOW_PACK)("4073340070", "test")
    assert doc is not None
    return doc


def _vis(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return " ".join(_html.unescape(markup).split())


def _site(html: str) -> str:
    return html[html.index('id="site-and-context"'):html.index('id="option-comparison"')]


def _comparison(html: str) -> str:
    return html[html.index('id="option-comparison"'):html.index('id="scenario-B"')]


def _scenario(html: str) -> str:
    return html[html.index('id="scenario-B"'):html.index('id="appendix"')]


def _appendix(html: str) -> str:
    return html[html.index('id="appendix"'):]


def _degenerate_footprint() -> dict:
    """The benchmark with a degenerate floor-1 plate ring: the engine still placed the
    building (floor_plates 'available', placement 'placed'), but neither the site-plan
    footprint nor the two-zone area illustration can be drawn (H4 T2)."""
    doc = copy.deepcopy(benchmark())
    doc["geometry"]["floor_plates"]["entries"][0]["outline"] = [_ZERO_RING]
    doc["building_alternatives"][0]["placement"]["outline"] = [_ZERO_RING]
    return doc


# ============================================================ S1 / drawings off (R277 no-draw)
def test_s1_drawings_off_no_drawing_and_every_claim_reads_not_drawn() -> None:
    # Drawings off (no Lane E, no map pack): no footprint kind anywhere; the placed benchmark's
    # page-5 status reads "Worked out; not drawn" (engine placed, nothing drawn) and the appendix
    # says the illustration "is not yet drawn". No page claims a drawing the report does not carry.
    html = build_report_html(benchmark())
    assert FOOTPRINT_KIND not in html
    assert "Illustrative building footprint on the city map outline" not in _vis(_site(html))
    assert "Worked out; not drawn" in _vis(_comparison(html))
    assert "Shown on the site plan" not in _vis(_comparison(html))
    assert "it is not yet drawn in this report" in _vis(_appendix(html))


def test_s1_1_4_0_document_makes_no_new_drawn_claim() -> None:
    doc = {"contract_version": "1.4.0", "answers": {}, "geometry": {"status": "not_available"}}
    html = build_report_html(doc)  # must not raise; no footprint, no manifest claim
    assert FOOTPRINT_KIND not in html
    assert "Illustrative building footprint on the city map outline" not in html


# =========================================================== S2 the real print (maps + Lane E)
def test_s2_real_print_page4_footprint_drawn_with_both_bases() -> None:
    # R198/R200/R201/R202: page 4 draws the footprint, names it, and states BOTH clearance bases.
    html = build_report_html(benchmark(), map_context=map_context(), env=_LANE_E)
    site = _vis(_site(html))
    assert FOOTPRINT_KIND in html                                   # the footprint kind is drawn
    assert "Illustrative building footprint on the city map outline" in site
    assert "No building placed" not in site                        # replaced by the footprint
    # the document's own clearance-conflict sentence, both bases named, neither chosen (R202).
    assert "33.34 feet on the tax map" in site and "35.31 feet on the city-map outline" in site
    # the measured 35.32 ft figure is NEVER drawn (packet RISK 2): only the document's 35.31 ft.
    assert "35.32" not in site


def test_s2_real_print_page5_shown_page6_sheet_and_appendix() -> None:
    html = build_report_html(benchmark(), map_context=map_context(), env=_LANE_E)
    # page 5 (R198: the "shown on" status names the site plan that shows it).
    assert "Shown on the site plan" in _vis(_comparison(html))
    # page 6 scenario sheet: the area illustration caption carries the document figures.
    scenario = _vis(_scenario(html))
    assert "apartment area 12,090 sq ft" in scenario
    assert "other building area 8,060 sq ft" in scenario
    assert "of 20,150 sq ft residential floor area" in scenario
    # appendix (R200: the zones are named only where they are drawn).
    assert ("it is shown as zones inside the placed building footprint on the scenario sheet"
            in _vis(_appendix(html)))


# ====================================================================== S3 the kit fallback
def test_s3_kit_fallback_draws_the_footprint_and_page5_agrees() -> None:
    # Lane E on but no map pack: the report falls back to the kit site plan, which now DRAWS the
    # illustrative footprint (carry item 6), so page 4 and page 5 agree with the manifest.
    html = build_report_html(benchmark(), env=_LANE_E)
    assert FOOTPRINT_KIND in html
    assert "Illustrative building footprint on the city map outline" in _vis(_site(html))
    assert "Shown on the site plan" in _vis(_comparison(html))


# ============================================ S4 degenerate footprint (R278: placed, not drawn)
def test_s4_degenerate_footprint_every_claim_reads_not_drawn() -> None:
    html = build_report_html(_degenerate_footprint(), map_context=map_context(), env=_LANE_E)
    site = _vis(_site(html))
    # page 4: nothing drawn and NOT "No building placed" (the engine placed it, S4); the caption
    # says the worked-out footprint is not drawn - never "Illustrative building footprint ...".
    assert FOOTPRINT_KIND not in html
    assert "No building placed" not in site
    assert "The worked-out footprint is not drawn on this map." in site
    assert "Illustrative building footprint on the city map outline" not in site
    # page 5 and page 6 agree.
    assert "Worked out; not drawn" in _vis(_comparison(html))
    assert "The footprint is worked out but is not drawn in this report." in _vis(_scenario(html))
    # appendix: the illustration is not drawn either (its ring is degenerate too), so no zones.
    appendix = _vis(_appendix(html))
    assert "it is not yet drawn in this report" in appendix
    assert "it is shown as zones" not in appendix


def test_s4_mutation_a_drawable_footprint_flips_every_claim_to_drawn() -> None:
    # MUTATION / red-green: restoring a drawable ring (the benchmark itself) flips every S4 claim
    # from not-drawn to drawn - proving each claim depends on the RENDERED footprint, not a field.
    not_drawn = build_report_html(_degenerate_footprint(), map_context=map_context(), env=_LANE_E)
    drawn = build_report_html(benchmark(), map_context=map_context(), env=_LANE_E)
    assert "The worked-out footprint is not drawn on this map." in _vis(_site(not_drawn))
    assert "The worked-out footprint is not drawn on this map." not in _vis(_site(drawn))
    assert "Worked out; not drawn" in _vis(_comparison(not_drawn))
    assert "Shown on the site plan" in _vis(_comparison(drawn))


# ===================================================== S6 budgets (the maps-on print adds words)
def test_s6_footprint_caption_adds_a_bounded_number_of_words() -> None:
    # Isolate the drawn-footprint cost: compare the drawn footprint (two short caption lines plus
    # the two SVG edge labels) against the SAME maps-on render with a degenerate footprint (one
    # short line, no edge labels). Both carry the full map, so the delta is only the footprint; it
    # stays small (< 70 words), so the drawn state never balloons the page (DB-270 / S6).
    drawn = len(_vis(_site(build_report_html(
        benchmark(), map_context=map_context(), env=_LANE_E))).split())
    not_drawn = len(_vis(_site(build_report_html(
        _degenerate_footprint(), map_context=map_context(), env=_LANE_E))).split())
    assert 0 < (drawn - not_drawn) < 70


# ============================================= S8 manifest consistency across the three states
def test_s8_the_footprint_kind_literal_equals_the_kit_style_kind() -> None:
    # The manifest's footprint-kind literal is the SAME string the kit style and the map renderer
    # draw (the cross-part contract with B1); a rename on one side without the other would break it.
    assert manifest._FOOTPRINT_KIND == FOOTPRINT_KIND
    assert style_for(FOOTPRINT_KIND).kind == FOOTPRINT_KIND


def test_s8_every_printed_claim_matches_the_rendered_footprint_state() -> None:
    # Across the three print states the page-5 status and the page-4 presence of the footprint kind
    # agree: "Shown on the site plan" iff the footprint kind is actually in the output.
    states = {
        "maps": build_report_html(benchmark(), map_context=map_context(), env=_LANE_E),
        "kit_fallback": build_report_html(benchmark(), env=_LANE_E),
        "drawings_off": build_report_html(benchmark()),
        "degenerate": build_report_html(_degenerate_footprint(), map_context=map_context(),
                                        env=_LANE_E),
    }
    for name, html in states.items():
        drawn = FOOTPRINT_KIND in html
        shown = "Shown on the site plan" in _vis(_comparison(html))
        assert drawn == shown, f"{name}: footprint kind drawn={drawn} but page-5 shown={shown}"


def test_s8_no_figure_mixes_the_two_bases_and_each_is_named() -> None:
    # The two clearance bases are stated in ONE sentence that names each (33.34 ft tax map, 35.31 ft
    # city map) and chooses neither; the two numbers never appear averaged into a single figure.
    site = _vis(_site(build_report_html(benchmark(), map_context=map_context(), env=_LANE_E)))
    assert "33.34 feet on the tax map" in site
    assert "35.31 feet on the city-map outline" in site
    # 34.325 / 34.33 would be the forbidden average of 33.34 and 35.31.
    assert "34.32" not in site and "34.33" not in site


def test_s8_long_commit_and_address_change_no_claim() -> None:
    # A 40-character commit and a long address must not move any drawn/placed claim (H4 T8).
    commit = "a" * 40
    long_addr = "215-16 Northern Boulevard, " + ("Very Long Neighbourhood Name " * 4) + "Queens"
    base = build_report_html(benchmark(), map_context=map_context(), env=_LANE_E)
    themed = build_report_html(benchmark(), map_context=map_context(), env=_LANE_E,
                               identity={"commit": commit, "address": long_addr})
    for section in (_comparison, _site):
        for claim in ("Shown on the site plan", "Illustrative building footprint on the city map "
                      "outline"):
            assert (claim in _vis(section(base))) == (claim in _vis(section(themed)))
    assert commit in themed  # the long commit still prints (in the run identity)
