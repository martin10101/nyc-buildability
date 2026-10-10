"""The block close-up and the neighbourhood map (M5-T155, S3, S4, S6, S8) on the
REAL recorded pack. The block shows the whole context window - the lot coloured
among its neighbours (only the subject labelled) and the street grid with one
name per street. The neighbourhood shows the street network north-up with the
lot marked and no label crossing another street."""

from __future__ import annotations

import json

import pytest

from app.drawings.maps import (
    Drawing,
    Unavailable,
    render_block_map,
    render_neighbourhood_map,
    render_site_context_plan,
)

from .context_support import (
    as_legacy,
    forbidden_tokens,
    label_problems,
    labels_below,
    labels_overlapping_marker,
    note_labels,
    recorded_document,
    report_too_big,
    street_area_polys,
    street_labels_crossing_other_streets,
    summary_note_leaks,
    summary_too_big,
    texts_by_role,
    wide_too_big,
    with_layer_unavailable,
)
from .maps_support import overlapping_labels

ENV = {"LANE_E_ENABLED": "1"}
DOC = recorded_document()
RENDERERS = {"block_map": render_block_map, "neighbourhood_map": render_neighbourhood_map}
# the S4 label-cleanliness checks run on every frame of ALL three drawings
ALL_RENDERERS = {**RENDERERS, "site_context_plan": render_site_context_plan}
ALL_FRAMES = ["report", "summary", "wide"]


# --------------------------------------------------------------------------- #
# S3 - the lot marked, the street names readable along their streets.
# --------------------------------------------------------------------------- #
def test_s3_block_marks_only_the_subject_and_names_the_streets():
    d = render_block_map(DOC, frame="report", env=ENV)
    assert isinstance(d, Drawing)
    assert "subject_lot" in d.kinds_drawn and "neighbour_lot" in d.kinds_drawn
    assert "street_area" in d.kinds_drawn
    assert {"NORTHERN BOULEVARD", "215 PLACE", "215 STREET"} <= set(texts_by_role(d.svg, "street"))
    # the close-up marks the subject (coral) and labels NO neighbour; "Lot 70"
    # is only drawn if it fits on the lot without crossing a street (else the
    # coral marker stands alone, like the competitor close-up).
    assert set(texts_by_role(d.svg, "lot_number")) <= {"Lot 70"}
    assert label_problems(d.svg, DOC) == []


def test_s3_neighbourhood_shows_the_street_network_with_the_lot_marked():
    d = render_neighbourhood_map(DOC, frame="report", env=ENV)
    assert isinstance(d, Drawing)
    assert "street_centreline" in d.kinds_drawn and "subject_lot" in d.kinds_drawn
    assert {"NORTHERN BOULEVARD", "215 PLACE", "215 STREET"} <= set(texts_by_role(d.svg, "street"))
    assert "Subject lot" in texts_by_role(d.svg, "subject_mark")
    assert label_problems(d.svg, DOC) == []


def test_s3_neighbourhood_is_north_up_and_block_is_rotated():
    nbhd = render_neighbourhood_map(DOC, frame="report", env=ENV)
    block = render_block_map(DOC, frame="report", env=ENV)
    assert isinstance(nbhd, Drawing) and isinstance(block, Drawing)
    assert '<g data-role="north-arrow">' in nbhd.svg          # north-up: no rotate transform
    assert 'data-role="north-arrow" transform="rotate' in block.svg


def test_s3_each_street_is_named_once():
    for name in RENDERERS:
        d = RENDERERS[name](DOC, frame="report", env=ENV)
        streets = texts_by_role(d.svg, "street")
        assert len(streets) == len(set(streets)), f"{name} repeats a street name"


def test_block_street_areas_stay_inside_the_data_window():
    """Every drawn street area lies inside the context window (the box the lots
    and buildings were fetched for): no street is drawn where no data exists."""
    from shapely.geometry import Polygon as SP

    from app.drawings.maps.adapter import load_map_context
    from app.drawings.maps.layout import REPORT_PLAN, REPORT_PLAN_MARGIN
    from app.drawings.maps.site_context_plan import (
        TITLE_BAND_PT,
        fit_view,
        frontage_rotation,
    )
    ctx = load_map_context(DOC)
    window = ctx.context_window.box
    alpha, _name, _src = frontage_rotation(ctx.subject_lot, ctx.streets)
    fr = fit_view(window, REPORT_PLAN, REPORT_PLAN_MARGIN, alpha=alpha, top_band=TITLE_BAND_PT)
    corners = [(window[0], window[1]), (window[2], window[1]),
               (window[2], window[3]), (window[0], window[3])]
    cw_screen = SP([fr.px(c) for c in corners]).buffer(0.75)  # small tolerance for 2dp rounding
    d = render_block_map(DOC, frame="report", env=ENV)
    polys = street_area_polys(d.svg)
    assert polys, "the block close-up draws no street areas"
    for ring in polys:
        assert cw_screen.contains(SP(ring)), "a street area lies outside the data window"


# --------------------------------------------------------------------------- #
# S4 - printed size, every drawing, on the real pack.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(RENDERERS))
@pytest.mark.parametrize("frame", ["report", "sheet"])
def test_s4_fits_and_every_label_is_at_least_7pt_with_no_overlaps(name, frame):
    d = RENDERERS[name](DOC, frame=frame, env=ENV)
    assert isinstance(d, Drawing)
    if frame == "report":
        assert not report_too_big(d.svg)
        # the architect-facing report frame draws no source code; the full sheet
        # frame keeps the attribution in its notes column (the evidence sheet).
        assert forbidden_tokens(d.svg) == []
    assert labels_below(d.svg, 7.0) == []
    assert overlapping_labels(d.svg) == []


@pytest.mark.parametrize("name", list(RENDERERS))
def test_s4_caption_is_returned_with_dates(name):
    d = RENDERERS[name](DOC, frame="report", env=ENV)
    assert isinstance(d, Drawing)
    notes = note_labels(d)
    assert notes and all(lbl.source for lbl in notes)
    assert "Digital City Map" in " ".join(lbl.text for lbl in notes)
    assert "2025-12-01" in " ".join(lbl.text for lbl in notes)


# --------------------------------------------------------------------------- #
# S6 - missing layers.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(("name", "layer"), [
    ("block_map", "tax_lots"), ("block_map", "streets"), ("neighbourhood_map", "streets"),
])
def test_s6_a_missing_needed_layer_gives_unavailable(name, layer):
    result = RENDERERS[name](with_layer_unavailable(DOC, layer), frame="report", env=ENV)
    assert isinstance(result, Unavailable)
    assert result.reason


@pytest.mark.parametrize("name", list(RENDERERS))
def test_s6_a_1_0_0_document_gives_unavailable(name):
    assert isinstance(RENDERERS[name](as_legacy(DOC), frame="report", env=ENV), Unavailable)


def test_s6_neighbourhood_still_draws_when_tax_lots_or_buildings_are_missing():
    for layer in ("tax_lots", "building_footprints"):
        d = render_neighbourhood_map(with_layer_unavailable(DOC, layer), frame="report", env=ENV)
        assert isinstance(d, Drawing)


# --------------------------------------------------------------------------- #
# S8 - deterministic.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(RENDERERS))
@pytest.mark.parametrize("frame", ["report", "sheet", "summary", "wide"])
def test_s8_same_input_gives_byte_identical_svg(name, frame):
    first = RENDERERS[name](DOC, frame=frame, env=ENV)
    assert isinstance(first, Drawing)
    assert first.svg == RENDERERS[name](DOC, frame=frame, env=ENV).svg
    reordered = json.loads(json.dumps(DOC, sort_keys=True))
    assert RENDERERS[name](reordered, frame=frame, env=ENV).svg == first.svg


# --------------------------------------------------------------------------- #
# Summary frame (rework 3): compact, for the one-page location sheet.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(RENDERERS))
def test_summary_frame_is_compact_clean_and_captionable(name):
    d = RENDERERS[name](DOC, frame="summary", env=ENV)
    assert isinstance(d, Drawing)
    assert not summary_too_big(d.svg)
    assert labels_below(d.svg, 7.0) == []
    assert overlapping_labels(d.svg) == []
    assert texts_by_role(d.svg, "title") == []
    assert texts_by_role(d.svg, "legend") == []
    assert forbidden_tokens(d.svg) == []
    assert texts_by_role(d.svg, "street")  # the main streets are named (some drop on a thumbnail)
    assert summary_note_leaks(d) == []


# --------------------------------------------------------------------------- #
# Wide frame (rework 4): a landscape strip so two maps stack on the location page.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(RENDERERS))
def test_wide_frame_is_a_landscape_strip(name):
    d = RENDERERS[name](DOC, frame="wide", env=ENV)
    assert isinstance(d, Drawing)
    assert not wide_too_big(d.svg)
    assert labels_below(d.svg, 7.0) == []
    assert overlapping_labels(d.svg) == []
    assert texts_by_role(d.svg, "title") == []
    assert forbidden_tokens(d.svg) == []
    assert {"NORTHERN BOULEVARD"} <= set(texts_by_role(d.svg, "street"))
    assert texts_by_role(d.svg, "legend")  # a compact legend is allowed
    assert summary_note_leaks(d) == []


def test_block_wide_labels_the_subject_and_confines_street_areas():
    from shapely.geometry import Polygon as SP

    from app.drawings.maps.adapter import load_map_context
    from app.drawings.maps.site_context_plan import (
        WIDE_PLAN,
        WIDE_PLAN_MARGIN,
        fit_view,
        frontage_rotation,
    )
    d = render_block_map(DOC, frame="wide", env=ENV)
    assert "subject_lot" in d.kinds_drawn  # the subject is marked (coral)
    assert set(texts_by_role(d.svg, "lot_number")) <= {"Lot 70"}  # no neighbour labelled
    ctx = load_map_context(DOC)
    window = ctx.context_window.box
    alpha, _n, _s = frontage_rotation(ctx.subject_lot, ctx.streets)
    fr = fit_view(window, WIDE_PLAN, WIDE_PLAN_MARGIN, alpha=alpha, top_band=0.0)
    corners = [(window[0], window[1]), (window[2], window[1]),
               (window[2], window[3]), (window[0], window[3])]
    cw = SP([fr.px(c) for c in corners]).buffer(0.75)
    polys = street_area_polys(d.svg)
    assert polys
    for ring in polys:
        assert cw.contains(SP(ring)), "a wide street area lies outside the data window"


def test_block_summary_street_areas_stay_inside_the_data_window():
    from shapely.geometry import Polygon as SP

    from app.drawings.maps.adapter import load_map_context
    from app.drawings.maps.site_context_plan import (
        SUMMARY_PLAN,
        SUMMARY_PLAN_MARGIN,
        fit_view,
        frontage_rotation,
    )
    ctx = load_map_context(DOC)
    window = ctx.context_window.box
    alpha, _n, _s = frontage_rotation(ctx.subject_lot, ctx.streets)
    fr = fit_view(window, SUMMARY_PLAN, SUMMARY_PLAN_MARGIN, alpha=alpha, top_band=0.0)
    corners = [(window[0], window[1]), (window[2], window[1]),
               (window[2], window[3]), (window[0], window[3])]
    cw = SP([fr.px(c) for c in corners]).buffer(0.75)
    polys = street_area_polys(render_block_map(DOC, frame="summary", env=ENV).svg)
    assert polys
    for ring in polys:
        assert cw.contains(SP(ring)), "a summary street area lies outside the data window"


# --------------------------------------------------------------------------- #
# S4 extension (M5-T155 corrections, T156-C2): in EVERY frame of EVERY drawing,
# no label crosses the subject marker or runs along another street's line.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(ALL_RENDERERS))
@pytest.mark.parametrize("frame", ALL_FRAMES)
def test_no_label_overlaps_the_subject_marker(name, frame):
    d = ALL_RENDERERS[name](DOC, frame=frame, env=ENV)
    assert isinstance(d, Drawing)
    assert labels_overlapping_marker(d.svg) == []


@pytest.mark.parametrize("name", list(ALL_RENDERERS))
@pytest.mark.parametrize("frame", ALL_FRAMES)
def test_no_label_runs_along_another_streets_centre_line(name, frame):
    # only the neighbourhood draws the centre lines, so the on-paper check runs
    # there (the block/site draw streets as areas - the production code keeps
    # their labels off other streets via place(avoid_lines=...)).
    d = ALL_RENDERERS[name](DOC, frame=frame, env=ENV)
    assert isinstance(d, Drawing)
    if "street_centreline" in d.kinds_drawn:
        assert street_labels_crossing_other_streets(d.svg, DOC) == []
