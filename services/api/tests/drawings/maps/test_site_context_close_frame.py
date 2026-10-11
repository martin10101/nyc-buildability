"""The large constraints close frame and its dimension lines (M5-T166, S1-S4, S9).

The close frame is the page-3 drawing: the subject lot and its edge-sharing
neighbours (lots 1, 11, 61) dominate, every edge long enough to label carries a
dimension line anchored to the edge's own vertices and named with its basis in
plain words ("<n> ft, map outline, not surveyed"), the fronting streets are named
with their mapped widths, and a 'No building placed' legend entry shows. The
outline is the MapPLUTO (gis) outline, so the only basis is the city map outline;
no tax-map value is drawn and nothing is merged across bases (NB-04).

Every drawn figure is read from the recorded document, never retyped.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

import pytest

from app.drawings.kit import geometry as geo
from app.drawings.kit.sheet import Sheet
from app.drawings.maps import Drawing, Unavailable, render_site_context_plan
from app.drawings.maps.adapter import load_map_context
from app.drawings.maps.close_frame_dimensions import (
    GIS_BASIS,
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


def test_s1_each_label_names_its_basis_in_plain_words() -> None:
    _ctx, _fr, dims = _dims()
    for d in dims:
        assert "map outline" in d.text  # the gis basis, named on every dimension
        assert d.text.startswith(f"{d.length_ft:.2f}".rstrip("0").rstrip("."))
        assert d.basis == GIS_BASIS


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


# =========================================================================== S9
def test_s9_close_frame_is_deterministic() -> None:
    first = render_site_context_plan(DOC, frame="close", env=ENV)
    assert isinstance(first, Drawing)
    assert first.svg == render_site_context_plan(DOC, frame="close", env=ENV).svg


def test_close_frame_fits_the_a4_content_width() -> None:
    d = render_site_context_plan(DOC, frame="close", env=ENV)
    root = ET.fromstring(d.svg)
    assert float(root.get("width")) <= 515.95   # within the A4 content width (182 mm)
