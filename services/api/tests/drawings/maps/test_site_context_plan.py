"""The site plan among its surroundings (M5-T155, S2, S4-S8), on the REAL
recorded pack (215-16 Northern: 200 neighbouring lots, 263 buildings, 35 street
segments) - the data the report actually draws. It must read like an architect's
drawing: the subject lot coloured with its edge lengths, ONLY its edge-sharing
neighbours labelled, even street areas with names/widths, clipped to a clean
viewport, rotated to the Northern Boulevard frontage, no overlaps."""

from __future__ import annotations

import json

import pytest

from app.drawings.maps import Drawing, Unavailable, render_site_context_plan

from .context_support import (
    as_legacy,
    forbidden_tokens,
    label_problems,
    labels_below,
    note_labels,
    recorded_document,
    report_too_big,
    texts_by_role,
    with_layer_unavailable,
)
from .maps_support import overlapping_labels

ENV = {"LANE_E_ENABLED": "1"}
DOC = recorded_document()

# The law/proposed kinds ruling Y6/Y8 forbids: required yards, courts, setback
# zones and lines, the permitted envelope, and the massing floor-plate uses.
LAW_KINDS = {
    "yard", "court", "setback_zone", "setback_line", "envelope",
    "residential", "commercial", "community_facility", "cellar", "bulkhead_or_mechanical",
}


def _render(frame="report", doc=None):
    return render_site_context_plan(doc or DOC, frame=frame, env=ENV)


# --------------------------------------------------------------------------- #
# S2 - the site plan among its surroundings.
# --------------------------------------------------------------------------- #
def test_s2_subject_is_coloured_with_its_edge_lengths():
    d = _render()
    assert isinstance(d, Drawing)
    assert "subject_lot" in d.kinds_drawn
    assert len(texts_by_role(d.svg, "dimension")) >= 3  # the lot's edges are dimensioned
    assert label_problems(d.svg, DOC) == []  # every value traces to the data


def test_s2_only_the_subject_and_its_edge_sharing_neighbours_are_labelled():
    d = _render()
    assert isinstance(d, Drawing)
    assert "neighbour_lot" in d.kinds_drawn and "building_footprint" in d.kinds_drawn
    # the only lot labels are the subject and the three lots that share an edge
    assert set(texts_by_role(d.svg, "lot_number")) == {"Lot 70", "Lot 1", "Lot 11", "Lot 61"}


def test_s2_streets_are_named_with_their_mapped_widths():
    d = _render()
    assert isinstance(d, Drawing)
    streets = set(texts_by_role(d.svg, "street"))
    assert {"NORTHERN BOULEVARD", "215 PLACE", "215 STREET"} <= streets
    widths = set(texts_by_role(d.svg, "street_width"))
    assert "100 ft mapped width" in widths
    assert "60 ft mapped width" in widths


def test_s2_has_north_arrow_scale_bar_legend_title_and_subtitle():
    d = _render()
    assert isinstance(d, Drawing)
    assert 'data-role="north-arrow"' in d.svg
    assert 'data-role="scale-bar"' in d.svg
    assert set(texts_by_role(d.svg, "legend")) == set(_legend_labels(d.kinds_drawn))
    titles = texts_by_role(d.svg, "title")
    assert "Site plan: the lot among its neighbours" in titles
    assert "Queens, Block 7334, lot 70" in titles  # derived from the BBL, never the raw BBL
    assert not any(t.strip() == "BBL 4073340070" for t in titles)


def test_s2_rotated_to_the_frontage_with_grid_north_noted():
    d = _render()
    assert isinstance(d, Drawing)
    caption = [lbl.text for lbl in note_labels(d)]
    assert any("Rotated to the Northern Boulevard frontage" in t for t in caption)
    assert "Grid north" in d.svg


def _legend_labels(kinds):
    from app.drawings.kit.styles import style_for
    return [style_for(k).label for k in kinds if style_for(k).in_legend]


# --------------------------------------------------------------------------- #
# S4 - printed size, every drawing, on the real pack.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("frame", ["report", "sheet"])
def test_s4_report_frame_fits_and_every_label_is_at_least_7pt(frame):
    d = _render(frame)
    assert isinstance(d, Drawing)
    if frame == "report":
        assert not report_too_big(d.svg)
    assert labels_below(d.svg, 7.0) == []
    assert overlapping_labels(d.svg) == []


# --------------------------------------------------------------------------- #
# S5 - sources and limits, on the real pack.
# --------------------------------------------------------------------------- #
def test_s5_caption_names_each_source_and_its_date():
    d = _render()
    assert isinstance(d, Drawing)
    notes = note_labels(d)
    assert all(lbl.source for lbl in notes)
    joined = " ".join(lbl.text for lbl in notes)
    assert "MapPLUTO" in joined and "Digital City Map" in joined and "Building footprints" in joined
    assert "2026-09-09" in joined and "2025-12-01" in joined and "2026-09-27" in joined


def test_s5_the_street_area_and_survey_notes_are_present():
    joined = " ".join(lbl.text for lbl in note_labels(_render()))
    assert "gaps between the tax lots" in joined
    assert "nothing is surveyed" in joined


def test_s5_no_url_field_name_or_code_word_in_any_drawn_text():
    assert forbidden_tokens(_render().svg) == []


# --------------------------------------------------------------------------- #
# S6 - missing layers.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("layer", ["tax_lots", "streets", "building_footprints"])
def test_s6_a_missing_needed_layer_gives_unavailable(layer):
    result = render_site_context_plan(with_layer_unavailable(DOC, layer), frame="report", env=ENV)
    assert isinstance(result, Unavailable)
    assert result.reason


def test_s6_a_1_0_0_document_gives_unavailable():
    result = render_site_context_plan(as_legacy(DOC), frame="report", env=ENV)
    assert isinstance(result, Unavailable)


# --------------------------------------------------------------------------- #
# S7 - no law drawn.
# --------------------------------------------------------------------------- #
def test_s7_no_law_is_drawn():
    d = _render()
    assert isinstance(d, Drawing)
    assert not (set(d.kinds_drawn) & LAW_KINDS)
    assert set(d.kinds_drawn) <= {
        "street_area", "subject_lot", "neighbour_lot", "building_footprint"}


# --------------------------------------------------------------------------- #
# S8 - deterministic.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("frame", ["report", "sheet"])
def test_s8_same_input_gives_byte_identical_svg(frame):
    first = _render(frame)
    assert isinstance(first, Drawing)
    assert first.svg == _render(frame).svg
    reordered = json.loads(json.dumps(DOC, sort_keys=True))
    assert render_site_context_plan(reordered, frame=frame, env=ENV).svg == first.svg
