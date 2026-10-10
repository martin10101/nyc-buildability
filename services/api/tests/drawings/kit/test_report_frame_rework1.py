"""M5-T152 rework 1 (K1-K4): the floor-stack section on quiet tokens with full labels clear of
their lines; short-edge dimensions recomposed with a collision check against ticks and lines; a
summary frame for the site plan; and a basis caption under the report-frame site plan.
"""

from __future__ import annotations

import re

import pytest

from app.drawings.kit import (
    Drawing,
    render_floor_stack,
    render_site_plan,
)
from app.drawings.kit.labels import Box, text_box
from app.drawings.kit.presentation_tokens import COLOR

from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    SVG_NS,
    fixture_paths,
    label_problems,
    load,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    texts,
)

MIN_LABEL_PT = 7.0
SUMMARY_MAX_PT = 240.9
FIXTURES = fixture_paths()
IDS = [p.stem for p in FIXTURES]
_POINT = re.compile(r"(-?[\d.]+) (-?[\d.]+)")


# --------------------------------------------------------------------------- K2
def _dimension_segments(root) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Every drawn dimension tick/line as a true (p, q) segment (each ``M.. L..`` subpath)."""
    segs = []
    for p in root.iter(f"{SVG_NS}path"):
        if p.get("data-role") != "dimension-geometry":
            continue
        for sub in (p.get("d") or "").split("M")[1:]:
            pts = [(float(x), float(y)) for x, y in _POINT.findall(sub)]
            for a, b in zip(pts, pts[1:], strict=False):
                segs.append((a, b))
    return segs


def _label_boxes(root) -> list[tuple[str, Box]]:
    out = []
    for el in root.iter(f"{SVG_NS}text"):
        if el.findall(f"{SVG_NS}tspan"):
            continue  # wrapped note blocks (none in these frames)
        text = "".join(el.itertext())
        rot = re.match(r"rotate\((-?[\d.]+)", el.get("transform") or "")
        out.append((text, text_box(float(el.get("x")), float(el.get("y")), text,
                                   float(el.get("font-size")), el.get("text-anchor", "start"),
                                   float(rot.group(1)) if rot else 0.0)))
    return out


def _ccw(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(a, b, c, d) -> bool:
    return (_ccw(a, c, d) > 0) != (_ccw(b, c, d) > 0) and \
           (_ccw(a, b, c) > 0) != (_ccw(a, b, d) > 0)


def _seg_hits_box(p, q, box: Box) -> bool:
    """True when segment p-q actually touches the axis-aligned ``box`` (an endpoint inside, or the
    segment crossing a box edge) - a TRUE geometric test, so a diagonal line beside a label is not a
    false positive the way a bounding-box test would be."""
    for pt in (p, q):
        if box.x0 <= pt[0] <= box.x1 and box.y0 <= pt[1] <= box.y1:
            return True
    corners = [(box.x0, box.y0), (box.x1, box.y0), (box.x1, box.y1), (box.x0, box.y1)]
    return any(_segments_cross(p, q, corners[i], corners[(i + 1) % 4]) for i in range(4))


def labels_over_dimension_geometry(svg: str) -> list[str]:
    """Labels whose box is truly touched by a dimension tick or line (the K2 collision check)."""
    root = parse(svg)
    segs = _dimension_segments(root)
    return [text for text, box in _label_boxes(root)
            if any(_seg_hits_box(p, q, box) for p, q in segs)]


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_k2_no_label_touches_a_dimension_tick_or_line(path):
    doc = load(path)
    for drawing in (render_site_plan(doc, env=ENV_ON),
                    render_site_plan(doc, frame="report", env=ENV_ON)):
        assert isinstance(drawing, Drawing)
        assert labels_over_dimension_geometry(drawing.svg) == []
        assert overlapping_labels(drawing.svg) == []


def test_k2_mutation_a_label_on_a_dimension_line_is_caught():
    """MUTATION PROOF (K2): moving a dimension label onto a dimension line is caught by the
    labels-vs-ticks-and-lines check."""
    svg = render_site_plan(load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json"),
                           frame="report", env=ENV_ON).svg
    assert labels_over_dimension_geometry(svg) == []
    root = parse(svg)
    (p, q) = _dimension_segments(root)[-1]  # the first edge's dimension line
    mid = ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)
    # move the first dimension label's anchor onto that line's midpoint
    dim = next(el for el in root.iter(f"{SVG_NS}text") if el.get("data-role") == "dimension")
    moved = svg.replace(
        f'x="{dim.get("x")}" y="{dim.get("y")}"',
        f'x="{mid[0]:.2f}" y="{mid[1]:.2f}"', 1)
    assert moved != svg
    assert labels_over_dimension_geometry(moved)


# --------------------------------------------------------------------------- K1
def test_k1_floor_stack_bands_are_a_quiet_token_not_yellow():
    doc = load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json")
    drawing = render_floor_stack(doc["building_alternatives"][0], env=ENV_ON)
    assert isinstance(drawing, Drawing)
    root = parse(drawing.svg)
    fills = {p.get("fill") for p in root.iter(f"{SVG_NS}path") if p.get("data-storey")}
    assert fills == {COLOR["selected"]}  # a quiet neutral token, not the residential yellow
    assert "#F0E442" not in drawing.svg


def test_k1_minimum_base_label_reads_in_full_and_clear_of_its_line():
    doc = load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json")
    drawing = render_floor_stack(doc["building_alternatives"][0], env=ENV_ON)
    root = parse(drawing.svg)
    labels = {el.get("data-role"): "".join(el.itertext()) for el in root.iter(f"{SVG_NS}text")}
    assert labels["floor_stack_min_base"] == "Minimum base height"  # in full, not cut short
    # the label and the '30 ft' top label are clear of the dashed reference line (K2-style check)
    geom_y = []  # the minimum-base dashed line y
    for p in root.iter(f"{SVG_NS}path"):
        if p.get("stroke-dasharray") and p.get("stroke") == COLOR["action"]:
            geom_y = [float(y) for _, y in _POINT.findall(p.get("d"))]
    assert geom_y
    line_y = geom_y[0]
    for el in root.iter(f"{SVG_NS}text"):
        if el.get("data-role") in ("floor_stack_min_base", "floor_stack_top"):
            box = text_box(float(el.get("x")), float(el.get("y")), "".join(el.itertext()),
                           float(el.get("font-size")), el.get("text-anchor", "start"))
            # the label's vertical box does not straddle the line, OR it is left of the line start
            assert box.y1 < line_y or box.y0 > line_y or float(el.get("x")) < 144.0


# --------------------------------------------------------------------------- K3
def test_k3_summary_frame_small_and_frontage_only():
    doc = load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json")
    drawing = render_site_plan(doc, frame="summary", env=ENV_ON)
    assert isinstance(drawing, Drawing)
    root = parse(drawing.svg)
    w, h = float(root.get("width")), float(root.get("height"))
    assert w <= SUMMARY_MAX_PT and h <= SUMMARY_MAX_PT, (w, h)
    sizes = [float(el.get("font-size")) for el in root.iter(f"{SVG_NS}text")]
    assert min(sizes) >= MIN_LABEL_PT
    roles = [el.get("data-role") for el in root.iter(f"{SVG_NS}text")]
    assert "legend" not in roles and "note" not in roles  # no legend, no notes
    assert "street" in roles  # the street names are shown
    assert any(g.get("data-role") == "north-arrow" for g in root.iter(f"{SVG_NS}g"))
    # frontage lengths ONLY: one dimension per frontage edge (2 here), not every edge (5).
    dim_sources = [el.get("data-source") for el, _ in texts(root)
                   if el.get("data-role") == "dimension"]
    assert len(dim_sources) == len(doc["geometry"]["streets"]) == 2
    assert overlapping_labels(drawing.svg) == []
    assert label_problems(drawing.svg, doc) == []
    assert numbers_not_in_input(drawing.svg, doc) == []


def test_k3_default_and_report_frames_unchanged_by_summary():
    doc = load(FIXTURES[0])
    assert render_site_plan(doc, env=ENV_ON) == render_site_plan(doc, frame="sheet", env=ENV_ON)


# --------------------------------------------------------------------------- K4
def test_k4_report_site_plan_carries_a_basis_caption():
    doc = load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json")
    drawing = render_site_plan(doc, frame="report", env=ENV_ON)
    root = parse(drawing.svg)
    captions = [(el.get("data-source"), "".join(el.itertext()))
                for el in root.iter(f"{SVG_NS}text") if el.get("data-role") == "caption"]
    assert len(captions) == 1
    source, text = captions[0]
    assert source == "/geometry/measurement/label"
    assert text.endswith(doc["geometry"]["measurement"]["label"])
    assert not re.search(r"[A-Za-z]+_[A-Za-z_]+", text)  # no field words
