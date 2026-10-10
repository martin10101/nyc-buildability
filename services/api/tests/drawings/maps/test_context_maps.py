"""The block close-up and the neighbourhood map (M5-T155, S3, S4, S6, S8).

The block close-up shows the whole context window - the lot marked among its
neighbours and the surrounding street network, rotated to the frontage. The
neighbourhood map shows the street network of the streets window with the lot
marked, NORTH-UP. Both name their sources and compute no law.
"""

from __future__ import annotations

import json

import pytest

from app.drawings.maps import (
    Drawing,
    Unavailable,
    render_block_map,
    render_neighbourhood_map,
)

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
RENDERERS = {"block_map": render_block_map, "neighbourhood_map": render_neighbourhood_map}


# --------------------------------------------------------------------------- #
# S3 - the lot marked, the street names readable along their streets.
# --------------------------------------------------------------------------- #
def test_s3_block_marks_the_lot_among_its_neighbours_and_names_the_streets():
    d = render_block_map(DOC, frame="report", env=ENV)
    assert isinstance(d, Drawing)
    assert "subject_lot" in d.kinds_drawn and "neighbour_lot" in d.kinds_drawn
    assert "street_centreline" in d.kinds_drawn
    streets = set(texts_by_role(d.svg, "street"))
    assert {"NORTHERN BOULEVARD", "215 PLACE", "215 STREET"} <= streets
    assert "Lot 70" in texts_by_role(d.svg, "lot_number")
    assert label_problems(d.svg, DOC) == []


def test_s3_neighbourhood_shows_the_street_network_with_the_lot_marked():
    d = render_neighbourhood_map(DOC, frame="report", env=ENV)
    assert isinstance(d, Drawing)
    assert "street_centreline" in d.kinds_drawn and "subject_lot" in d.kinds_drawn
    streets = set(texts_by_role(d.svg, "street"))
    assert {"NORTHERN BOULEVARD", "215 PLACE", "215 STREET"} <= streets
    assert "Subject lot" in texts_by_role(d.svg, "subject_mark")
    assert label_problems(d.svg, DOC) == []


def test_s3_neighbourhood_is_north_up_and_block_is_rotated():
    nbhd = render_neighbourhood_map(DOC, frame="report", env=ENV)
    block = render_block_map(DOC, frame="report", env=ENV)
    assert isinstance(nbhd, Drawing) and isinstance(block, Drawing)
    # north-up: the north-arrow group carries no rotate transform.
    assert '<g data-role="north-arrow">' in nbhd.svg
    assert 'data-role="north-arrow" transform="rotate' in block.svg


# --------------------------------------------------------------------------- #
# S4 - printed size.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(RENDERERS))
def test_s4_report_frame_fits_and_every_label_is_at_least_7pt(name):
    d = RENDERERS[name](DOC, frame="report", env=ENV)
    assert isinstance(d, Drawing)
    assert not report_too_big(d.svg)
    assert labels_below(d.svg, 7.0) == []
    assert overlapping_labels(d.svg) == []
    assert forbidden_tokens(d.svg) == []


@pytest.mark.parametrize("name", list(RENDERERS))
def test_s4_caption_is_returned_to_the_caller(name):
    d = RENDERERS[name](DOC, frame="report", env=ENV)
    assert isinstance(d, Drawing)
    notes = note_labels(d)
    assert notes and all(lbl.source for lbl in notes)
    assert "Digital City Map" in " ".join(lbl.text for lbl in notes)


# --------------------------------------------------------------------------- #
# S6 - missing layers.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(("name", "layer"), [
    ("block_map", "tax_lots"), ("block_map", "streets"),
    ("neighbourhood_map", "streets"),
])
def test_s6_a_missing_needed_layer_gives_unavailable(name, layer):
    doc = with_layer_unavailable(DOC, layer)
    result = RENDERERS[name](doc, frame="report", env=ENV)
    assert isinstance(result, Unavailable)
    assert result.reason


@pytest.mark.parametrize("name", list(RENDERERS))
def test_s6_a_1_0_0_document_gives_unavailable(name):
    result = RENDERERS[name](legacy_1_0_0_document(), frame="report", env=ENV)
    assert isinstance(result, Unavailable)


def test_s6_neighbourhood_still_draws_when_tax_lots_or_buildings_are_missing():
    # the neighbourhood map needs only the streets; tax_lots / buildings absent
    # does not make it Unavailable.
    for layer in ("tax_lots", "building_footprints"):
        d = render_neighbourhood_map(with_layer_unavailable(DOC, layer), frame="report", env=ENV)
        assert isinstance(d, Drawing)


# --------------------------------------------------------------------------- #
# S8 - deterministic.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", list(RENDERERS))
@pytest.mark.parametrize("frame", ["report", "sheet"])
def test_s8_same_input_gives_byte_identical_svg(name, frame):
    first = RENDERERS[name](DOC, frame=frame, env=ENV)
    again = RENDERERS[name](DOC, frame=frame, env=ENV)
    assert isinstance(first, Drawing)
    assert first.svg == again.svg
    reordered = json.loads(json.dumps(DOC, sort_keys=True))
    third = RENDERERS[name](reordered, frame=frame, env=ENV)
    assert isinstance(third, Drawing)
    assert third.svg == first.svg
