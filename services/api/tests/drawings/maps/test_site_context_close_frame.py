"""The large constraints close frame and its dimension lines (M5-T166, S1-S4, S9).

The close frame is the page-3 drawing: the subject lot and its edge-sharing
neighbours (lots 1, 11, 61) dominate, every edge long enough to label carries a
dimension line anchored to the edge's own vertices with a FIGURE-ONLY label
("<n> ft"), the drawing states the shared basis ONCE in a note under it
("All dimensions: city map outline, not surveyed."; owner K1, 2026-10-12), the
fronting streets are named with their mapped widths, every label sits on a white
background clear of every drawn line, the neighbours' addresses are dropped and
their buildings drawn lighter, and a 'No building placed' legend entry shows. The
outline is the MapPLUTO (gis) outline, so the only basis is the city map outline;
no tax-map value is drawn and nothing is merged across bases (NB-04).

Every drawn figure is read from the recorded document, never retyped.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

import pytest

from app.drawings.kit import geometry as geo
from app.drawings.kit.sheet import Sheet
from app.drawings.maps import Drawing, Unavailable, render_site_context_plan
from app.drawings.maps.adapter import load_map_context
from app.drawings.maps.close_frame_dimensions import (
    GIS_BASIS,
    GIS_BASIS_NOTE,
    GIS_BASIS_TAG,
    MIN_LABELLED_EDGE_FT,
    DimensionPlacementError,
    draw_edge_dimensions,
)
from app.drawings.maps.context_scene import (
    CLOSE_PLAN,
    CLOSE_PLAN_MARGIN,
    TITLE_BAND_PT,
    fit_view,
    viewport,
)
from app.drawings.maps.site_context_plan import close_frame_view, frontage_rotation

from .context_support import (
    label_problems,
    recorded_document,
    texts_by_role,
    with_layer_unavailable,
)
from .maps_support import overlapping_labels

ENV = {"LANE_E_ENABLED": "1"}
DOC = recorded_document()
_SVG_NS = "{http://www.w3.org/2000/svg}"
# The measured data labels the close frame must keep at >= 8.5 pt (the kit's own
# furniture - legend, scale bar, north arrow, title block - keeps its standard
# >= 7 pt sizes, checked by the site-context-plan suite).
_DATA_ROLES = {"dimension", "street", "street_width", "lot_number", "lot_address"}
# tax-map figures (printed_tax_map / filing_attribute basis) must never be drawn
# on the gis close frame.
_TAX_MAP_VALUES = {100.76, 100.0}


def _close_fr():
    ctx = load_map_context(DOC)
    view = close_frame_view(ctx.subject_lot, ctx.streets)
    alpha, _n, _s = frontage_rotation(ctx.subject_lot, ctx.streets)
    fr = fit_view(view, CLOSE_PLAN, CLOSE_PLAN_MARGIN, alpha=alpha, top_band=TITLE_BAND_PT)
    return ctx, fr, viewport(CLOSE_PLAN)


def _dims():
    ctx, fr, rect = _close_fr()
    sheet = Sheet()
    return ctx, fr, draw_edge_dimensions(sheet, ctx.subject_lot.outline, fr, rect)


def _label_sizes(svg: str):
    return [(el.get("data-role"), "".join(el.itertext()), float(el.get("font-size")))
            for el in ET.fromstring(svg).iter(f"{_SVG_NS}text")]


# =========================================================================== S1
def test_s1_dimension_endpoints_lie_on_their_edge_vertices() -> None:
    ctx, fr, dims = _dims()
    ring = ctx.subject_lot.outline.exterior
    assert len(dims) == 4  # the four edges >= 6 ft (the 2.22 ft sliver is undimensioned)
    for d in dims:
        a, b = fr.px(ring[d.edge_index]), fr.px(ring[d.edge_index + 1])
        assert math.dist(d.a_px, a) <= 0.01, f"edge {d.edge_index} start off its vertex"
        assert math.dist(d.b_px, b) <= 0.01, f"edge {d.edge_index} end off its vertex"
        assert geo.edge_length(ring[d.edge_index], ring[d.edge_index + 1]) == pytest.approx(
            d.length_ft)


def test_s1_each_label_shows_only_the_figure() -> None:
    # owner K1, D-094 R116 (2026-10-12): when every dimension shares one basis each
    # label shows ONLY the figure ("103.88 ft"), never the basis words.
    _ctx, _fr, dims = _dims()
    for d in dims:
        figure = f"{d.length_ft:.2f}".rstrip("0").rstrip(".")
        assert d.text == f"{figure} ft"      # figure only, no basis words
        assert "map outline" not in d.text   # the basis is NOT repeated on the label
        assert d.basis == GIS_BASIS          # the basis is still recorded on the dimension


def test_s1_basis_is_stated_once_in_a_note_under_the_drawing() -> None:
    # The shared basis is stated ONCE, in a note under the drawing, at >= 8.5 pt.
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    notes = texts_by_role(d.svg, "dimension-basis")
    assert notes == [GIS_BASIS_NOTE]                          # exactly once, exact words
    for role, _text, size in _label_sizes(d.svg):
        if role == "dimension-basis":
            assert size >= 8.5
    # the basis words never appear on a dimension label.
    assert all("map outline" not in t for t in texts_by_role(d.svg, "dimension"))


def test_s1_a_mixed_basis_frame_tags_each_label_with_a_short_tag() -> None:
    # The kept code path for a drawing that MIXES bases: each label then carries its
    # own short tag so the bases stay distinct (none does today - this is a made-up
    # mixed frame; owner K1 wording "only when one drawing mixes bases").
    ctx, fr, rect = _close_fr()
    edge_bases = {0: (GIS_BASIS, "map outline"), 1: ("survey", "survey"),
                  2: (GIS_BASIS, "map outline"), 3: ("survey", "survey")}
    dims = draw_edge_dimensions(Sheet(), ctx.subject_lot.outline, fr, rect,
                                avoid_lines=[], edge_bases=edge_bases)
    assert len(dims) == 4
    for d in dims:
        _full, tag = edge_bases[d.edge_index]
        figure = f"{d.length_ft:.2f}".rstrip("0").rstrip(".")
        assert d.text == f"{figure} ft, {tag}"   # figure + the edge's own short tag
        assert d.basis == edge_bases[d.edge_index][0]
    assert {d.basis for d in dims} == {GIS_BASIS, "survey"}  # two bases, kept distinct


def test_s1_a_single_basis_given_through_edge_bases_stays_figure_only() -> None:
    # edge_bases naming ONE basis is not "mixed": labels stay figure-only.
    ctx, fr, rect = _close_fr()
    one = {i: (GIS_BASIS, GIS_BASIS_TAG) for i in range(4)}
    dims = draw_edge_dimensions(Sheet(), ctx.subject_lot.outline, fr, rect,
                                avoid_lines=[], edge_bases=one)
    for d in dims:
        assert "," not in d.text and "map outline" not in d.text


def test_s1_nothing_is_merged_across_bases() -> None:
    _ctx, _fr, dims = _dims()
    assert {d.basis for d in dims} == {GIS_BASIS}  # one basis only


def test_s1_no_tax_map_value_is_drawn() -> None:
    _ctx, _fr, dims = _dims()
    for d in dims:
        assert round(d.length_ft, 2) not in _TAX_MAP_VALUES, "a tax-map figure was drawn"


# =========================================================================== S2
def test_s2_every_measured_label_is_at_least_8_5pt_no_collisions() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    for role, text, size in _label_sizes(d.svg):
        if role in _DATA_ROLES:
            assert size >= 8.5, f"{role} {text!r} prints at {size} pt (< 8.5)"
    assert overlapping_labels(d.svg) == []
    assert len(texts_by_role(d.svg, "dimension")) == 4  # no dimension is suppressed


def test_s2_a_sub_minimum_size_fails_rather_than_shrink() -> None:
    ctx, fr, rect = _close_fr()
    with pytest.raises(DimensionPlacementError):
        draw_edge_dimensions(Sheet(), ctx.subject_lot.outline, fr, rect, size=8.0)


def test_s2_a_cramped_frame_fails_rather_than_dropping_a_dimension() -> None:
    ctx, fr, _rect = _close_fr()
    with pytest.raises(DimensionPlacementError):
        draw_edge_dimensions(Sheet(), ctx.subject_lot.outline, fr, (0.0, 0.0, 20.0, 20.0))


def test_an_edge_too_short_to_label_is_left_undimensioned() -> None:
    ctx, fr, dims = _dims()
    assert all(d.length_ft >= MIN_LABELLED_EDGE_FT for d in dims)
    assert 4 not in {d.edge_index for d in dims}  # the 2.22 ft edge carries no dimension


def _drawn_boundary_lines(ctx, fr, rect):
    """Every DRAWN lot boundary on the close frame - the neighbour outlines plus the
    subject outline, clipped to the viewport exactly as the scene draws them. These
    are the lines a dimension label may not cross (its own witness and dimension
    lines are drawn separately and are the only lines it may cross; rework 2 / G3 F5)."""
    from app.drawings.maps.context_scene import project_polygon
    from app.drawings.maps.site_context_plan import dimension_avoid_lines
    from app.drawings.maps.street_areas import clip_polygon_to_rect

    lines = list(dimension_avoid_lines(ctx, fr, rect))  # the drawn neighbour outlines
    for poly in clip_polygon_to_rect(
        [tuple(r) for r in project_polygon(ctx.subject_lot.outline, fr)], rect
    ):
        lines.append(("subject", list(poly)))
    return lines


def test_s2_no_dimension_label_crosses_a_drawn_line() -> None:
    # Visual G3 finding 5 / S2: on the benchmark close frame no dimension label's box
    # is crossed by any drawn lot boundary (neighbour or subject). The label is placed
    # with the SAME avoid set the scene uses (the drawn neighbour outlines); the check
    # is against every drawn boundary, so a label never collides with a line but its own.
    from app.drawings.maps.context_scene import box_crosses_lines
    from app.drawings.maps.site_context_plan import dimension_avoid_lines

    ctx, fr, rect = _close_fr()
    dims = draw_edge_dimensions(
        Sheet(), ctx.subject_lot.outline, fr, rect, avoid_lines=dimension_avoid_lines(ctx, fr, rect)
    )
    assert len(dims) == 4
    drawn = _drawn_boundary_lines(ctx, fr, rect)
    for d in dims:
        assert not box_crosses_lines(d.label_box, drawn, None, pad=0.5, max_len=0.0), (
            f"edge {d.edge_index} label {d.text!r} crosses a drawn boundary line"
        )


def test_s2_a_forced_collision_fails_closed() -> None:
    # A made-up frame built to collide: boundary lines laid across every lane of the
    # viewport so no candidate box is clear. The build FAILS (never a silent crossing
    # or a shrunk label); the real benchmark above has clear spots.
    ctx, fr, rect = _close_fr()
    x0, y0, x1, y1 = rect
    blocking = [("block", [(x0, float(y)), (x1, float(y))])
                for y in range(int(y0), int(y1) + 1, 3)]  # a line every 3 pt, spanning the frame
    with pytest.raises(DimensionPlacementError):
        draw_edge_dimensions(Sheet(), ctx.subject_lot.outline, fr, rect, avoid_lines=blocking)


def _svg_label_boxes(svg: str):
    """Every data label on the rendered close frame as (role, text, Box) - the labels
    that must be crossed by no drawn line but their own (rework 3)."""
    from app.drawings.kit.labels import text_box

    out = []
    for t in ET.fromstring(svg).iter(f"{_SVG_NS}text"):
        role = t.get("data-role")
        if role in _DATA_ROLES:
            text = "".join(t.itertext())
            m = re.search(r"rotate\(([-\d.]+)", t.get("transform", "") or "")
            out.append((role, text, text_box(float(t.get("x")), float(t.get("y")), text,
                        float(t.get("font-size")), t.get("text-anchor", "start"),
                        float(m.group(1)) if m else 0.0)))
    return out


def _svg_dimension_lines(svg: str):
    """Every drawn witness and dimension line segment (data-role='dimension-line')."""
    out = []
    for p in ET.fromstring(svg).iter(f"{_SVG_NS}path"):
        if p.get("data-role") == "dimension-line" and p.get("d"):
            n = re.findall(r"[-\d.]+", p.get("d"))
            pts = [(float(n[i]), float(n[i + 1])) for i in range(0, len(n) - 1, 2)]
            out.append(("dimension", pts))
    return out


def test_s2_no_line_crosses_any_label_own_dimension_line_included() -> None:
    # rework 3 (visual G3 defects 1 & 2): no drawn witness or dimension line passes
    # through ANY label's box - the label's OWN dimension and witness lines included.
    # A dimension label sits BESIDE its dimension line with a gap (never struck
    # through); the lot, street and width labels are clear of the dimension lines too.
    from app.drawings.maps.context_scene import box_crosses_lines

    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    lines = _svg_dimension_lines(d.svg)
    assert len(lines) == 12  # four edges x (two witness + one dimension) lines
    labels = _svg_label_boxes(d.svg)
    assert len(texts_by_role(d.svg, "dimension")) == 4  # all four dimension labels present
    for role, text, box in labels:
        assert not box_crosses_lines(box, lines, None, pad=0.3, max_len=0.0), (
            f"a dimension/witness line passes through {role} label {text!r}"
        )


def test_s2_a_line_through_a_label_box_is_detected() -> None:
    # Forced case for the new rule: a line laid through a label's box IS caught by the
    # same check the test above uses, so the rule cannot pass vacuously.
    from app.drawings.kit.labels import Box
    from app.drawings.maps.context_scene import box_crosses_lines

    box = Box(100.0, 100.0, 160.0, 110.0)
    through = [("dimension", [(130.0, 90.0), (130.0, 120.0)])]  # a vertical line across the box
    beside = [("dimension", [(170.0, 90.0), (170.0, 120.0)])]   # a line clear of the box
    assert box_crosses_lines(box, through, None, pad=0.3, max_len=0.0) is True
    assert box_crosses_lines(box, beside, None, pad=0.3, max_len=0.0) is False


# =========================================================================== S4
def test_s4_close_frame_contents() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    # the subject and its three edge-sharing neighbours dominate (only these labelled).
    assert set(texts_by_role(d.svg, "lot_number")) == {"Lot 70", "Lot 1", "Lot 11", "Lot 61"}
    # the fronting streets are named with their mapped widths.
    assert {"NORTHERN BOULEVARD", "215 PLACE"} <= set(texts_by_role(d.svg, "street"))
    widths = set(texts_by_role(d.svg, "street_width"))
    assert "100 ft mapped width" in widths and "60 ft mapped width" in widths
    # north arrow, scale bar and the 'No building placed' legend entry.
    assert 'data-role="north-arrow"' in d.svg and 'data-role="scale-bar"' in d.svg
    assert "No building placed" in texts_by_role(d.svg, "legend")
    # every drawn value traces to the document (C-4).
    assert label_problems(d.svg, DOC) == []


def test_s4_no_yard_or_setback_area_is_drawn() -> None:
    # R008/R017: no rear-yard or setback area whose basis depends on the unresolved
    # 23-344(b)/(c)(3) analysis is drawn.
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    law = {"yard", "court", "setback_zone", "setback_line", "envelope"}
    assert not (set(d.kinds_drawn) & law)


def test_s4_a_missing_layer_gives_unavailable() -> None:
    # the lot-only fallback is handled at the report level (test_constraints_page); the
    # drawing itself is honestly Unavailable when a needed layer is missing.
    result = render_site_context_plan(
        with_layer_unavailable(DOC, "tax_lots"), frame="close", env=ENV)
    assert isinstance(result, Unavailable) and result.reason


# ========================================================================== S14
_HALOED_ROLES = {"dimension", "street", "street_width", "lot_number", "lot_address"}


def _haloed_labels(svg: str):
    """(text, x, y, size, anchor, transform) of every drawn label that must sit on
    a white background (S14)."""
    out = []
    for t in ET.fromstring(svg).iter(f"{_SVG_NS}text"):
        if t.get("data-role") in _HALOED_ROLES:
            out.append(("".join(t.itertext()), float(t.get("x")), float(t.get("y")),
                        float(t.get("font-size")), t.get("text-anchor", "start"),
                        t.get("transform")))
    return out


def _background_rects(svg: str):
    """(x, y, transform) of every white label-background rect."""
    out = []
    for r in ET.fromstring(svg).iter(f"{_SVG_NS}rect"):
        if r.get("data-role") == "label-background":
            assert r.get("fill") == "#FFFFFF"
            out.append((float(r.get("x")), float(r.get("y")), r.get("transform")))
    return out


def _expect_background(text, x, y, size, anchor, transform, pad=0.6):
    from app.drawings.kit.styles import TYPOGRAPHY

    width = len(text) * size * TYPOGRAPHY.char_width_em
    left = {"start": 0.0, "middle": -width / 2.0, "end": -width}[anchor]
    return (x + left - pad, y - 0.8 * size - pad, transform)


def test_s14_every_label_sits_on_a_white_background() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    labels = _haloed_labels(d.svg)
    assert labels  # there ARE data labels on the close frame
    rects = _background_rects(d.svg)
    assert len(rects) == len(labels)  # one white background per label, no more
    for text, x, y, size, anchor, transform in labels:
        ex, ey, et = _expect_background(text, x, y, size, anchor, transform)
        assert any(abs(rx - ex) <= 0.02 and abs(ry - ey) <= 0.02 and rt == et
                   for rx, ry, rt in rects), f"no white background behind {text!r}"


def test_s14_a_label_with_no_clear_place_fails_rather_than_shrinking() -> None:
    # S14 end-to-end: with every lane blocked no dimension label finds a clear spot,
    # so the build raises rather than placing a label on a line or shrinking it.
    ctx, fr, rect = _close_fr()
    x0, y0, x1, y1 = rect
    blocking = [("block", [(x0, float(y)), (x1, float(y))])
                for y in range(int(y0), int(y1) + 1, 3)]
    with pytest.raises(DimensionPlacementError):
        draw_edge_dimensions(Sheet(), ctx.subject_lot.outline, fr, rect, avoid_lines=blocking)


# ========================================================================== S15
def _lighter_building_groups(svg: str):
    return [g for g in ET.fromstring(svg).iter(f"{_SVG_NS}g")
            if g.get("data-role") == "lighter-neighbour-building"]


def test_s15_no_neighbour_addresses_but_lot_numbers_stay() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    assert texts_by_role(d.svg, "lot_address") == []  # neighbour street addresses dropped
    assert set(texts_by_role(d.svg, "lot_number")) == {"Lot 70", "Lot 1", "Lot 11", "Lot 61"}


def test_s15_neighbour_buildings_are_drawn_lighter_than_the_subject() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(d, Drawing)
    groups = _lighter_building_groups(d.svg)
    assert groups  # the neighbour buildings are wrapped in lighter groups
    for g in groups:
        assert 0.0 < float(g.get("opacity")) < 1.0
        assert any((p.get("fill") or "") not in ("", "none")
                   for p in g.iter(f"{_SVG_NS}path"))  # a drawn building fill inside
    # the subject lot fill is NOT inside any lighter group (it stays full strength).
    root = ET.fromstring(d.svg)
    light_paths = {id(p) for g in groups for p in g.iter(f"{_SVG_NS}path")}
    subj = [p for p in root.iter(f"{_SVG_NS}path")
            if p.get("data-source") == "/map_context/subject_lot/outline"]
    assert subj and all(id(p) not in light_paths for p in subj)
    assert "building_footprint" in d.kinds_drawn  # the legend keeps the entry


def test_s14_s15_apply_to_the_page_one_compact_close_frame() -> None:
    # The page-1 compact close frame (no dimensions, keeps its 88 mm column) gets the
    # same white backgrounds and lighter neighbours; it carries no basis note (S15).
    d = render_site_context_plan(DOC, frame="summary_close", env=ENV)
    assert isinstance(d, Drawing)
    assert _background_rects(d.svg)                 # white backgrounds behind its labels
    assert _lighter_building_groups(d.svg)          # lighter neighbour buildings
    assert texts_by_role(d.svg, "lot_address") == []
    assert texts_by_role(d.svg, "dimension") == []        # no dimensions on the compact frame
    assert texts_by_role(d.svg, "dimension-basis") == []  # so no basis note
    assert "Lot 70" in texts_by_role(d.svg, "lot_number")


# =========================================================================== S9
def test_s9_close_frame_is_deterministic() -> None:
    first = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(first, Drawing)
    assert first.svg == render_site_context_plan(DOC, frame="close", env=ENV).svg


def test_close_frame_fits_the_a4_content_width() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    root = ET.fromstring(d.svg)
    assert float(root.get("width")) <= 515.95   # within the A4 content width (182 mm)
