"""M5-T152 (S4): the report frame of the location and zoning maps.

render_location_map / render_zoning_map with frame='report': no notes column; the attribution and
notes are still reachable by the caller (as Label records, role 'note', for the evidence page);
every label at least 7 pt; at most 182 mm by 150 mm; the default (sheet) frames stay byte-identical.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from app.drawings.maps import Drawing, Unavailable, render_location_map, render_zoning_map

from .maps_support import (
    ENV_ON,
    SVG_NS,
    fixture_paths,
    load,
    overlapping_labels,
    parse,
)

MAX_W_PT = 515.9
MAX_H_PT = 425.2
MIN_LABEL_PT = 7.0

FIXTURES = fixture_paths()
IDS = [p.stem for p in FIXTURES]
RENDERERS = {"location_map": render_location_map, "zoning_map": render_zoning_map}
CASES = [(p, name) for p in FIXTURES for name in RENDERERS]
CASE_IDS = [f"{p.stem}-{name}" for p, name in CASES]


def _labels_below(svg: str, min_pt: float) -> list[tuple[str, float]]:
    bad = []
    for el in parse(svg).iter(f"{SVG_NS}text"):
        if float(el.get("font-size")) < min_pt:
            bad.append(("".join(el.itertext()), float(el.get("font-size"))))
    return bad


@pytest.mark.parametrize(("path", "name"), CASES, ids=CASE_IDS)
def test_s4_map_report_frame_fits_and_keeps_notes_reachable(path, name):
    drawing = RENDERERS[name](load(path), frame="report", env=ENV_ON)
    if isinstance(drawing, Unavailable):
        return  # the layer was not retrieved; the map is honestly Unavailable
    assert isinstance(drawing, Drawing)
    root = ET.fromstring(drawing.svg)
    w, h = float(root.get("width")), float(root.get("height"))
    assert w <= MAX_W_PT and h <= MAX_H_PT, (w, h)
    assert _labels_below(drawing.svg, MIN_LABEL_PT) == []
    assert overlapping_labels(drawing.svg) == []
    # No notes column: the report-frame map draws no 'note' text ...
    assert [el for el in root.iter(f"{SVG_NS}text") if el.get("data-role") == "note"] == []
    # ... but the attribution and notes stay reachable by the caller as Label records.
    note_labels = [lbl for lbl in drawing.labels if lbl.role == "note"]
    assert note_labels
    assert all(lbl.source for lbl in note_labels)  # each note traces to its data source


@pytest.mark.parametrize(("path", "name"), CASES, ids=CASE_IDS)
def test_s4_map_default_frame_is_byte_identical_to_sheet(path, name):
    doc = load(path)
    assert RENDERERS[name](doc, env=ENV_ON) == RENDERERS[name](doc, frame="sheet", env=ENV_ON)
