"""The site plan among its surroundings (M5-T155, S2, S4-S8).

Renders the benchmark 215-16 Northern 1.1.0 document and checks it draws what the
owner's reference and the competitor draw: the subject lot coloured with its edge
lengths, the neighbouring lots and existing buildings in greys, the streets named
along them with their mapped widths, rotated to the Northern Boulevard frontage;
with the sources/limits caption returned to the caller, no law drawn, and
deterministic output.
"""

from __future__ import annotations

import json

import pytest

from app.drawings.maps import Drawing, Unavailable, render_site_context_plan

from .context_support import (
    benchmark_document,
    forbidden_tokens,
    label_problems,
    labels_below,
    legacy_1_0_0_document,
    note_labels,
    report_too_big,
    texts_by_role,
    with_layer_unavailable,
)
from .maps_support import overlapping_labels

ENV = {"LANE_E_ENABLED": "1"}
DOC = benchmark_document()

# The law/proposed kinds ruling Y6/Y8 forbids: required yards, courts, setback
# zones and lines, the permitted envelope, and the massing floor-plate uses (a
# drawn coverage portion or building position). None may appear.
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
    dims = texts_by_role(d.svg, "dimension")
    assert len(dims) >= 3  # the lot's edges are dimensioned (the 2.22 ft edge aside)
    assert label_problems(d.svg, DOC) == []  # every length traces to the outline


def test_s2_neighbours_and_buildings_are_drawn_in_greys():
    d = _render()
    assert isinstance(d, Drawing)
    assert "neighbour_lot" in d.kinds_drawn
    assert "building_footprint" in d.kinds_drawn
    lots = set(texts_by_role(d.svg, "lot_number"))
    assert {"Lot 70", "Lot 1", "Lot 11", "Lot 61"} <= lots


def test_s2_streets_are_named_with_their_mapped_widths():
    d = _render()
    assert isinstance(d, Drawing)
    streets = set(texts_by_role(d.svg, "street"))
    assert {"NORTHERN BOULEVARD", "215 PLACE", "215 STREET"} <= streets
    widths = set(texts_by_role(d.svg, "street_width"))
    assert "100 ft mapped width" in widths
    assert "60 ft mapped width" in widths


def test_s2_has_north_arrow_scale_bar_legend_and_title():
    d = _render()
    assert isinstance(d, Drawing)
    assert 'data-role="north-arrow"' in d.svg
    assert 'data-role="scale-bar"' in d.svg
    # the legend lists ONLY the kinds drawn
    assert set(texts_by_role(d.svg, "legend")) == {
        "Subject lot", "Building footprint", "Neighbouring lot", "Street"}
    assert "Site plan: the lot among its neighbours" in texts_by_role(d.svg, "title")


def test_s2_rotated_to_the_frontage_with_grid_north_noted():
    d = _render()
    assert isinstance(d, Drawing)
    caption = [lbl.text for lbl in note_labels(d)]
    assert any("Rotated to the Northern Boulevard frontage" in t for t in caption)
    assert "Grid north" in d.svg  # the arrow still names grid north


# --------------------------------------------------------------------------- #
# S4 - printed size.
# --------------------------------------------------------------------------- #
def test_s4_report_frame_fits_and_every_label_is_at_least_7pt():
    d = _render()
    assert isinstance(d, Drawing)
    assert not report_too_big(d.svg)
    assert labels_below(d.svg, 7.0) == []
    assert overlapping_labels(d.svg) == []


# --------------------------------------------------------------------------- #
# S5 - sources and limits.
# --------------------------------------------------------------------------- #
def test_s5_caption_names_each_source_and_its_date():
    d = _render()
    assert isinstance(d, Drawing)
    notes = note_labels(d)
    assert all(lbl.source for lbl in notes)  # every caption note traces to its source
    joined = " ".join(lbl.text for lbl in notes)
    # the three drawn layers' sources, each with its edit date / version
    assert "MapPLUTO 26v2" in joined
    assert "Digital City Map" in joined
    assert "Building footprints" in joined
    assert "2026-09-09" in joined and "2025-12-01" in joined and "2026-09-27" in joined


def test_s5_the_street_area_note_and_survey_note_are_present():
    d = _render()
    assert isinstance(d, Drawing)
    joined = " ".join(lbl.text for lbl in note_labels(d))
    assert "gaps between the tax lots" in joined
    assert "nothing is surveyed" in joined


def test_s5_no_url_field_name_or_code_word_in_any_drawn_text():
    d = _render()
    assert isinstance(d, Drawing)
    assert forbidden_tokens(d.svg) == []


# --------------------------------------------------------------------------- #
# S6 - missing layers.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("layer", ["tax_lots", "streets", "building_footprints"])
def test_s6_a_missing_needed_layer_gives_unavailable(layer):
    doc = with_layer_unavailable(DOC, layer)
    result = render_site_context_plan(doc, frame="report", env=ENV)
    assert isinstance(result, Unavailable)
    assert result.reason


def test_s6_a_1_0_0_document_gives_unavailable():
    result = render_site_context_plan(legacy_1_0_0_document(), frame="report", env=ENV)
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
    again = _render(frame)
    assert isinstance(first, Drawing)
    assert first.svg == again.svg
    reordered = json.loads(json.dumps(DOC, sort_keys=True))
    third = render_site_context_plan(reordered, frame=frame, env=ENV)
    assert isinstance(third, Drawing)
    assert third.svg == first.svg
