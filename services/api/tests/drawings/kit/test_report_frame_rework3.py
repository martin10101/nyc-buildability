"""M5-T152 rework 3 (K5-K7): no label clipped at the drawing edge; a compact summary frame; the
floor-stack section leaves its caption to the report.
"""

from __future__ import annotations

import re

import pytest

from app.drawings.kit import Drawing, render_floor_stack, render_site_plan
from app.drawings.kit.labels import text_box
from app.drawings.kit.section import draw_floor_stack

from .kit_support import CONTRACT_FIXTURES, ENV_ON, SVG_NS, fixture_paths, load, parse

EDGE_MARGIN = 1.0  # every label lies wholly inside the viewBox with at least this margin (K5)
FIXTURES = fixture_paths()
IDS = [p.stem for p in FIXTURES]


def _texts(root):
    out = []
    for el in root.iter(f"{SVG_NS}text"):
        if el.findall(f"{SVG_NS}tspan"):
            continue
        text = "".join(el.itertext())
        rot = re.match(r"rotate\((-?[\d.]+)", el.get("transform") or "")
        out.append((el, text, text_box(float(el.get("x")), float(el.get("y")), text,
                                       float(el.get("font-size")), el.get("text-anchor", "start"),
                                       float(rot.group(1)) if rot else 0.0)))
    return out


def labels_outside_viewbox(svg: str, margin: float = EDGE_MARGIN) -> list[str]:
    """Every label whose rotated bounding box leaves the viewBox (or its ``margin`` border) - the
    K5 check that no label, rotated or not, is clipped at the drawing edge."""
    root = parse(svg)
    w, h = float(root.get("width")), float(root.get("height"))
    bad = []
    for _el, text, box in _texts(root):
        if box.x0 < margin or box.y0 < margin or box.x1 > w - margin or box.y1 > h - margin:
            bad.append(text)
    return bad


# --------------------------------------------------------------------------- K5
@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_k5_no_label_is_clipped_in_the_report_or_summary_frame(path):
    doc = load(path)
    for frame in ("report", "summary"):
        drawing = render_site_plan(doc, frame=frame, env=ENV_ON)
        assert isinstance(drawing, Drawing)
        assert labels_outside_viewbox(drawing.svg) == [], (path.stem, frame)


def test_k5_mutation_a_label_pushed_over_the_edge_is_caught():
    """MUTATION PROOF (K5): a label whose box leaves the viewBox (e.g. the top street label moved
    up) is caught by the viewBox check."""
    svg = render_site_plan(load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json"),
                           frame="report", env=ENV_ON).svg
    assert labels_outside_viewbox(svg) == []
    root = parse(svg)
    street = next(el for el in root.iter(f"{SVG_NS}text") if el.get("data-role") == "street")
    moved = svg.replace(f'y="{street.get("y")}"', 'y="-3.00"', 1)
    assert moved != svg
    assert labels_outside_viewbox(moved)


# --------------------------------------------------------------------------- K6
def test_k6_summary_is_composed_tightly():
    """K6: the north arrow and scale bar sit immediately beneath the drawn content - no large empty
    band (the gap between the plan content and the north arrow is small)."""
    doc = load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json")
    root = parse(render_site_plan(doc, frame="summary", env=ENV_ON).svg)
    # the lowest plan content: the lot path's points and the dimension/street label boxes
    plan_bottom = 0.0
    for p in root.iter(f"{SVG_NS}path"):
        if p.get("data-source") == "/geometry/lot_outline":
            plan_bottom = max([plan_bottom, *(float(y) for _x, y in
                               re.findall(r"(-?[\d.]+) (-?[\d.]+)", p.get("d")))])
    for el, _text, box in _texts(root):
        if el.get("data-role") in ("street", "dimension"):
            plan_bottom = max(plan_bottom, box.y1)
    north_n = next(el for el in root.iter(f"{SVG_NS}text") if "".join(el.itertext()) == "N")
    gap = (float(north_n.get("y")) - float(north_n.get("font-size"))) - plan_bottom
    assert 0.0 <= gap < 24.0, gap


# --------------------------------------------------------------------------- K7
@pytest.mark.parametrize(("stem", "idx"), [
    ("recorded_215_16_northern_journey", 0),
    ("synthetic_coverage_by_portion_available_contract_1_4_0", 0),
])
def test_k7_report_floor_stack_has_no_caption(stem, idx):
    doc = load(CONTRACT_FIXTURES / f"{stem}.json")
    root = parse(render_floor_stack(doc["building_alternatives"][idx], env=ENV_ON).svg)
    assert [el for el in root.iter(f"{SVG_NS}text") if el.get("data-role") == "caption"] == []


def test_k7_default_floor_stack_still_draws_its_caption():
    """The default (non-report) floor stack keeps its caption; only the report frame drops it."""
    doc = load(CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json")
    drawing = draw_floor_stack(doc["building_alternatives"][0])  # caption=True by default
    assert isinstance(drawing, Drawing)
    root = parse(drawing.svg)
    captions = [("".join(el.itertext())) for el in root.iter(f"{SVG_NS}text")
                if el.get("data-role") == "caption"]
    assert captions == ["Drawn from the floor schedule; no placement on the lot."]
