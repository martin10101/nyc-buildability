"""The illustrative building footprint on the site close frame (M5-T173 part B1).

The engine's floor-1 plate, translated onto the map lot by ``overlay_offset`` and drawn
as an illustrative footprint with two figure-only dimensions on the lot-interior side.
The ring and the expected figures are read from the sources, never a program run: the
benchmark floor-1 plate (``recorded_215_16_northern_journey``) and the GIS figures of
``placement-building-b.json`` row ``gis-conflict-check`` (frontage 103.88 ft, GIS plan
depth 64.66 ft). placed_footprint defaults to None, so every frame is byte-identical
without it (S1/S6); an invalid ring or an unplaceable label draws NOTHING (S4/S5).
"""

from __future__ import annotations

import copy
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from app.drawings.kit.sheet import Sheet
from app.drawings.maps import Drawing, render_site_context_plan
from app.drawings.maps.adapter import load_map_context
from app.drawings.maps.constraint_overlay import overlay_offset
from app.drawings.maps.context_scene import (
    CLOSE_PLAN,
    CLOSE_PLAN_MARGIN,
    TITLE_BAND_PT,
    fit_view,
    viewport,
)
from app.drawings.maps.model import Polygon
from app.drawings.maps.placed_footprint import FOOTPRINT_KIND, DrawnFootprint, draw_placed_footprint
from app.drawings.maps.site_context_plan import close_frame_view, frontage_rotation

from . import maps_support
from .context_support import label_problems, recorded_document, texts_by_role

ENV = {"LANE_E_ENABLED": "1"}
SVG_NS = "{http://www.w3.org/2000/svg}"
REPO = Path(__file__).resolve().parents[5]
DOC = recorded_document()
_RESULTS = (REPO / "packages" / "contracts" / "fixtures" / "valid" / "results"
            / "recorded_215_16_northern_journey.json")
_REF_CASE = REPO / "docs" / "reference-cases" / "R6B" / "cases" / "placement-building-b.json"
# The benchmark floor-1 plate ring (results-local feet), the input part W threads.
_BENCH_PLATES = json.loads(_RESULTS.read_text())["geometry"]["floor_plates"]
BENCH_RING = _BENCH_PLATES["entries"][0]["outline"][0]
# The two dimensions expected INDEPENDENTLY from the reference case (never a program run).
_REF_ROW = next(r for r in json.loads(_REF_CASE.read_text())["rows"]
                if r["row_id"] == "gis-conflict-check")
_REF_Q = {q["name"]: q["value"] for q in _REF_ROW["quantities"]}
EXPECT_WIDTH = f'{_REF_Q["GIS Northern Boulevard frontage"]} ft'   # "103.88 ft"
EXPECT_DEPTH = f'{_REF_Q["GIS plan depth the plate needs"]} ft'    # "64.66 ft"
# Tax-map / clearance figures that must NEVER be drawn on the gis close frame (NB-04).
FORBIDDEN = ("33.34", "35.31", "35.32", "100.76", "66.66")


def _close_fr():
    ctx = load_map_context(DOC)
    alpha, _n, _s = frontage_rotation(ctx.subject_lot, ctx.streets)
    fr = fit_view(close_frame_view(ctx.subject_lot, ctx.streets), CLOSE_PLAN, CLOSE_PLAN_MARGIN,
                  alpha=alpha, top_band=TITLE_BAND_PT)
    return ctx, fr, viewport(CLOSE_PLAN)


def _footprint_dims(svg: str) -> dict[str, str]:
    """{data-source: text} of the drawn footprint dimensions (edge source under the
    floor_plates ring), so they are told apart from the subject-lot edge dimensions."""
    out = {}
    for el in ET.fromstring(svg).iter(f"{SVG_NS}text"):
        src = el.get("data-source") or ""
        if el.get("data-role") == "dimension" and src.startswith("edge:/geometry/floor_plates"):
            out[src] = "".join(el.itertext())
    return out


def _fp_doc(ring) -> dict:
    """The map-context document plus the floor-1 plate ring, so the footprint dimensions'
    edge sources resolve for the C-4 label check."""
    doc = copy.deepcopy(DOC)
    doc["geometry"] = {"floor_plates": {"status": "available",
                       "entries": [{"floor": 1, "outline": [ring], "gross_sf": 0.0,
                                    "use": "residential"}]}}
    return doc


# ---- a synthetic square lot for the precise validation / placement tests (S4/S5) ----
SUBJECT = Polygon(rings=(((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0), (0.0, 0.0)),),
                  source="/x")
VALID_RING = [[10.0, 10.0], [90.0, 10.0], [90.0, 60.0], [10.0, 60.0], [10.0, 10.0]]


def _synthetic_fr():
    fr = fit_view((0.0, 0.0, 100.0, 100.0), CLOSE_PLAN, CLOSE_PLAN_MARGIN, top_band=TITLE_BAND_PT)
    return fr, viewport(CLOSE_PLAN)


# =========================================================================== S1
def test_s1_no_footprint_is_byte_identical_and_keeps_no_building_placed() -> None:
    base = render_site_context_plan(DOC, frame="close", env=ENV)
    none = render_site_context_plan(DOC, frame="close", env=ENV, placed_footprint=None)
    assert isinstance(base, Drawing)
    assert base.svg == none.svg                                     # None is byte-identical
    assert FOOTPRINT_KIND not in base.kinds_drawn
    assert "No building placed" in texts_by_role(base.svg, "legend")


# =========================================================================== S2
def test_s2_footprint_drawn_with_the_two_reference_dimensions() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV, placed_footprint=BENCH_RING)
    assert isinstance(d, Drawing)
    assert FOOTPRINT_KIND in d.kinds_drawn
    assert "Illustrative building footprint" in texts_by_role(d.svg, "legend")
    assert "No building placed" not in texts_by_role(d.svg, "legend")
    # the two footprint dimensions equal the reference-case GIS figures (not a program run).
    assert set(_footprint_dims(d.svg).values()) == {EXPECT_WIDTH, EXPECT_DEPTH}
    # the single shared-basis note is printed exactly once.
    assert texts_by_role(d.svg, "dimension-basis") == ["All dimensions: city map outline, "
                                                       "not surveyed."]
    # no tax-map or clearance figure is drawn anywhere (NB-04).
    for bad in FORBIDDEN:
        assert bad not in d.svg, bad
    # every drawn figure traces to its source, the footprint dimensions included (C-4).
    assert label_problems(d.svg, _fp_doc(BENCH_RING)) == []


def test_s2_footprint_vertices_are_the_document_vertices_plus_the_overlay_offset() -> None:
    ctx, fr, rect = _close_fr()
    drawn = draw_placed_footprint(Sheet(), BENCH_RING, ctx.subject_lot.outline, fr, rect)
    assert isinstance(drawn, DrawnFootprint)
    ox, oy = overlay_offset(ctx.subject_lot.outline)
    for v, mapped in zip(BENCH_RING, drawn.map_points, strict=True):
        assert math.dist((v[0] + ox, v[1] + oy), mapped) <= 0.01
    assert round(drawn.width_ft, 2) == float(_REF_Q["GIS Northern Boulevard frontage"])
    assert round(drawn.depth_ft, 2) == float(_REF_Q["GIS plan depth the plate needs"])


def test_s2_footprint_adds_no_untraceable_number_to_the_raw_number_check() -> None:
    # The close frame's edge dimensions are edge LENGTHS, not raw numbers, so the raw
    # maps_support.numbers_not_in_input check does not pass on the plain close frame
    # either (the edge-sourced C-4 check above is the authoritative one). The footprint
    # must add NO new untraceable number: its 103.88/64.66 are the input ring's own edges.
    base = render_site_context_plan(DOC, frame="close", env=ENV)
    fp = render_site_context_plan(DOC, frame="close", env=ENV, placed_footprint=BENCH_RING)
    edges = [math.hypot(BENCH_RING[i + 1][0] - BENCH_RING[i][0],
                        BENCH_RING[i + 1][1] - BENCH_RING[i][1])
             for i in range(len(BENCH_RING) - 1)]
    allow = {**DOC, "_footprint_edges_ft": edges}
    base_missing = set(maps_support.numbers_not_in_input(base.svg, DOC))
    fp_missing = set(maps_support.numbers_not_in_input(fp.svg, allow))
    assert fp_missing <= base_missing


def test_s2_every_footprint_label_is_at_least_8_5pt_no_collisions() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV, placed_footprint=BENCH_RING)
    for el in ET.fromstring(d.svg).iter(f"{SVG_NS}text"):
        src = el.get("data-source") or ""
        if src.startswith("edge:/geometry/floor_plates"):
            assert float(el.get("font-size")) >= 8.5
    assert maps_support.overlapping_labels(d.svg) == []


# =========================================================================== S4
_DEGENERATE = {
    "non_finite": [[10.0, 10.0], [math.inf, 10.0], [90.0, 60.0], [10.0, 60.0], [10.0, 10.0]],
    "over_magnitude": [[10.0, 10.0], [2e9, 10.0], [90.0, 60.0], [10.0, 60.0], [10.0, 10.0]],
    "point_not_a_pair": [[10.0, 10.0], [90.0], [90.0, 60.0], [10.0, 60.0], [10.0, 10.0]],
    "over_1000_vertices": [[0.0, 0.0]] * 1002,
    "under_3_points": [[10.0, 10.0], [90.0, 10.0]],
    "zero_area": [[10.0, 10.0], [50.0, 10.0], [90.0, 10.0], [10.0, 10.0]],
    "vertex_0_06_ft_outside": [[10.0, 10.0], [90.0, 10.0], [90.0, 60.0], [10.0, 100.06],
                               [10.0, 10.0]],
}


@pytest.mark.parametrize("ring", list(_DEGENERATE.values()), ids=list(_DEGENERATE))
def test_s4_a_degenerate_footprint_draws_nothing(ring) -> None:
    fr, rect = _synthetic_fr()
    sheet = Sheet()
    assert draw_placed_footprint(sheet, ring, SUBJECT, fr, rect) is None   # no exception
    assert sheet.parts == [] and sheet.kinds == [] and sheet.boxes == []   # nothing drawn


def test_s4_a_vertex_0_04_ft_outside_is_still_drawn() -> None:
    # the 0.05 ft tolerance boundary: 0.04 ft outside is "on" the outline and drawn.
    fr, rect = _synthetic_fr()
    inside = [[10.0, 10.0], [90.0, 10.0], [90.0, 60.0], [10.0, 100.04], [10.0, 10.0]]
    assert isinstance(draw_placed_footprint(Sheet(), inside, SUBJECT, fr, rect), DrawnFootprint)


def test_s4_a_degenerate_footprint_on_the_close_frame_shows_no_no_building_placed() -> None:
    # the engine placed the building, so even a degenerate ring (drawing nothing) drops
    # the 'No building placed' row (placed_footprint is not None).
    zero_area = [[0.0, 0.0], [50.0, 0.0], [100.0, 0.0], [0.0, 0.0]]
    d = render_site_context_plan(DOC, frame="close", env=ENV, placed_footprint=zero_area)
    assert isinstance(d, Drawing)
    assert FOOTPRINT_KIND not in d.kinds_drawn
    assert "No building placed" not in texts_by_role(d.svg, "legend")


# =========================================================================== S5
def test_s5_an_unplaceable_label_withholds_the_whole_footprint() -> None:
    from app.drawings.kit.labels import Box
    fr, rect = _synthetic_fr()
    blocked = Sheet()
    blocked.boxes = [Box(rect[0], rect[1], rect[2], rect[3])]  # every candidate collides
    assert draw_placed_footprint(blocked, VALID_RING, SUBJECT, fr, rect) is None
    assert FOOTPRINT_KIND not in blocked.kinds                # nothing drawn, not partial
    assert all("illustrative-footprint" not in part for part in blocked.parts)
    # control: with a clear sheet the same footprint IS drawn (the mutation boundary).
    clear = Sheet()
    assert isinstance(draw_placed_footprint(clear, VALID_RING, SUBJECT, fr, rect), DrawnFootprint)
    assert FOOTPRINT_KIND in clear.kinds


# =========================================================================== S6
@pytest.mark.parametrize("frame", ["summary", "summary_close", "wide", "report", "sheet"])
def test_s6_other_frames_ignore_placed_footprint(frame) -> None:
    without = render_site_context_plan(DOC, frame=frame, env=ENV)
    with_fp = render_site_context_plan(DOC, frame=frame, env=ENV, placed_footprint=BENCH_RING)
    assert isinstance(without, Drawing)
    assert without.svg == with_fp.svg                          # byte-identical (pages 1 and 2)


# =========================================================================== S9
def test_s9_the_footprint_close_frame_is_deterministic() -> None:
    first = render_site_context_plan(DOC, frame="close", env=ENV, placed_footprint=BENCH_RING)
    again = render_site_context_plan(DOC, frame="close", env=ENV, placed_footprint=BENCH_RING)
    assert isinstance(first, Drawing) and first.svg == again.svg
