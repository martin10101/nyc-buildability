"""The illustrative building footprint on the kit report-frame site plan (M5-T173 B1).

The report-frame fallback draws the engine's floor-1 plate in kind
``illustrative_footprint`` (not its 'Residential' use colour) with two figure-only
dimensions (the width/back edge and one depth edge) on the lot-interior side. The sheet
and summary frames keep the use-coloured plate, byte-identical (covered by the snapshot
suite). The two figures are the plate's own edge lengths, which match the independently
worked reference case ``placement-building-b.json`` row ``gis-conflict-check`` (frontage
103.88 ft, GIS plan depth 64.66 ft) - never a program run.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from app.drawings.kit import Drawing, render_site_plan
from app.drawings.kit.adapter import load_drawing_input
from app.drawings.kit.labels import Box
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.site_plan import (
    REPORT_PLAN,
    REPORT_PLAN_MARGIN,
    REPORT_TOP_BIAS,
    _frame,
    _report_footprint,
)

from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    SVG_NS,
    label_problems,
    load,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    texts,
)

MAX_W_PT = 515.9
MAX_H_PT = 425.2
REPO = Path(__file__).resolve().parents[5]
_REF_CASE = REPO / "docs" / "reference-cases" / "R6B" / "cases" / "placement-building-b.json"
_REF_ROW = next(r for r in json.loads(_REF_CASE.read_text())["rows"]
                if r["row_id"] == "gis-conflict-check")
_REF_Q = {q["name"]: q["value"] for q in _REF_ROW["quantities"]}
EXPECT_WIDTH = f'{_REF_Q["GIS Northern Boulevard frontage"]} ft'   # "103.88 ft"
EXPECT_DEPTH = f'{_REF_Q["GIS plan depth the plate needs"]} ft'    # "64.66 ft"
BENCH = CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json"


def _footprint_dims(svg: str) -> dict[str, str]:
    """{data-source: text} of the drawn footprint dimensions (edge source under the
    floor_plates ring), told apart from the lot-outline edge dimensions."""
    out = {}
    for el in ET.fromstring(svg).iter(f"{SVG_NS}text"):
        src = el.get("data-source") or ""
        if el.get("data-role") == "dimension" and src.startswith("edge:/geometry/floor_plates"):
            out[src] = "".join(el.itertext())
    return out


def _legend(svg: str) -> list[str]:
    return [t for el, t in texts(parse(svg)) if el.get("data-role") == "legend"]


# =========================================================================== S3
def test_s3_report_frame_plate_is_the_illustrative_footprint_with_two_dimensions() -> None:
    doc = load(BENCH)
    d = render_site_plan(doc, frame="report", env=ENV_ON)
    assert isinstance(d, Drawing)
    assert "illustrative_footprint" in d.kinds_drawn
    legend = _legend(d.svg)
    assert "Illustrative building footprint" in legend
    assert "Residential" not in legend                       # not the use kind
    # the same two dimensions as the close frame, equal to the reference-case GIS figures.
    assert set(_footprint_dims(d.svg).values()) == {EXPECT_WIDTH, EXPECT_DEPTH}


def test_s3_report_frame_fits_a4_one_caption_no_overlap_numbers_traceable() -> None:
    doc = load(BENCH)
    d = render_site_plan(doc, frame="report", env=ENV_ON)
    root = parse(d.svg)
    assert float(root.get("width")) <= MAX_W_PT and float(root.get("height")) <= MAX_H_PT
    captions = [t for el, t in texts(root) if el.get("data-role") == "caption"]
    assert len(captions) == 1                                # exactly one caption (K4)
    assert overlapping_labels(d.svg) == []
    assert numbers_not_in_input(d.svg, doc) == []            # every number read from the results
    assert label_problems(d.svg, doc) == []                  # C-4 (footprint dims included)
    for el in root.iter(f"{SVG_NS}text"):
        if (el.get("data-source") or "").startswith("edge:/geometry/floor_plates"):
            assert float(el.get("font-size")) >= 8.5         # footprint labels >= 8.5 pt (R053)


# =========================================================================== S1 (kit)
def test_s1_sheet_frame_keeps_the_use_plate_not_the_illustrative_footprint() -> None:
    # the report frame swaps the plate to the illustrative footprint; the sheet frame
    # keeps the 'Residential' use plate (byte-identity against the snapshot is covered by
    # test_snapshots). This is the toggle: reverting the report behaviour (drawing the use
    # plate) would drop 'illustrative_footprint' from the report and redden S3 above.
    doc = load(BENCH)
    sheet = render_site_plan(doc, env=ENV_ON)
    assert isinstance(sheet, Drawing)
    assert "illustrative_footprint" not in sheet.kinds_drawn
    assert "residential" in sheet.kinds_drawn
    report = render_site_plan(doc, frame="report", env=ENV_ON)
    assert "illustrative_footprint" in report.kinds_drawn
    assert "residential" not in report.kinds_drawn


# =========================================================================== S5 (kit)
def test_s5_report_frame_withholds_the_footprint_when_a_label_cannot_be_placed() -> None:
    doc = load(BENCH)
    data = load_drawing_input(doc)
    fr = _frame(data.lot, REPORT_PLAN, REPORT_PLAN_MARGIN, REPORT_TOP_BIAS)
    # a clear sheet draws the footprint...
    clear = Sheet()
    _report_footprint(clear, data, fr)
    assert "illustrative_footprint" in clear.kinds
    # ...but with every lane blocked no label can be placed, so the WHOLE footprint is
    # withheld (plan-then-commit): nothing is drawn, not a partial footprint (S5).
    blocked = Sheet()
    blocked.boxes = [Box(-1e4, -1e4, 1e4, 1e4)]
    _report_footprint(blocked, data, fr)
    assert "illustrative_footprint" not in blocked.kinds
    assert all("illustrative" not in part and "A-BLDG-ILLUS" not in part
               for part in blocked.parts)
