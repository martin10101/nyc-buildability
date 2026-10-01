"""Site plan SVG (plan section 5c item 2; check C-4; task E-01)."""

from __future__ import annotations

import math
import re

import pytest

from app.drawings.kit import Drawing, render_site_plan
from app.drawings.kit.site_plan import STANDARD_SCALES_FT_PER_IN
from app.drawings.kit.styles import STYLE_TABLE
from app.drawings.kit.svg import escape

from .drawn_checks import site_plan_problems
from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    KIT_FIXTURES,
    SVG_NS,
    fixture_paths,
    label_problems,
    load,
    numbers_in,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    pieces,
    point_in_or_on,
    resolve,
    texts,
)

FIXTURES = fixture_paths()
IDS = [p.stem for p in FIXTURES]


def _plan(path) -> tuple[dict, Drawing]:
    doc = load(path)
    drawing = render_site_plan(doc, env=ENV_ON)
    assert isinstance(drawing, Drawing)
    return doc, drawing


def _path_points(d: str) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in re.findall(r"[ML](-?[\d.]+) (-?[\d.]+)", d)]


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_every_label_is_read_from_the_results(path):
    doc, drawing = _plan(path)
    assert label_problems(drawing.svg, doc) == []
    assert numbers_not_in_input(drawing.svg, doc) == []


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_drawn_footprints_and_yards_match_the_printed_numbers(path):
    doc, drawing = _plan(path)
    assert site_plan_problems(drawing.svg, doc) == []


def test_the_drawn_geometry_checker_catches_a_mismatch():
    doc, drawing = _plan(KIT_FIXTURES / "synthetic_interior_lot_mixed_use.json")
    assert ">30 ft<" in drawing.svg
    assert site_plan_problems(drawing.svg.replace(">30 ft<", ">10 ft<"), doc)


@pytest.mark.parametrize("text", ["Main\x0bStreet", "a\x00", "b\ud800", "c\uffff"])
def test_svg_text_never_carries_characters_xml_forbids(text):
    with pytest.raises(ValueError):
        escape(text)
    assert escape("Tab\tand\nnewline & <ok>") == "Tab\tand\nnewline &amp; &lt;ok&gt;"


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_labels_do_not_overlap(path):
    _, drawing = _plan(path)
    assert overlapping_labels(drawing.svg) == []


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_label_manifest_matches_the_svg(path):
    _, drawing = _plan(path)
    sourced = [(source, text) for source, text, _ in pieces(parse(drawing.svg)) if source]
    assert sorted(sourced) == sorted((lbl.source, lbl.text) for lbl in drawing.labels)


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_every_lot_edge_is_dimensioned_from_the_geometry(path):
    doc, drawing = _plan(path)
    ring = doc["geometry"]["lot_outline"][0]
    dims = [el.get("data-source") for el, _ in texts(parse(drawing.svg))
            if el.get("data-role") == "dimension"]
    assert dims == [f"edge:/geometry/lot_outline/0#{i}" for i in range(len(ring) - 1)]


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_drawn_lot_matches_the_scale_bar(path):
    doc, drawing = _plan(path)
    root = parse(drawing.svg)
    bar = next(g for g in root.iter(f"{SVG_NS}g") if g.get("data-role") == "scale-bar")
    k, x0 = float(bar.get("data-px-per-ft")), float(bar.get("data-x0"))
    assert any(math.isclose(k, 72.0 / s, rel_tol=1e-6) for s in STANDARD_SCALES_FT_PER_IN)
    for el in bar.iter(f"{SVG_NS}text"):
        value = numbers_in(el.text)[0]
        assert math.isclose(float(el.get("x")) - x0, value * k, abs_tol=0.01)
    lot = next(p for p in root.iter(f"{SVG_NS}path")
               if p.get("data-source") == "/geometry/lot_outline")
    drawn = _path_points(lot.get("d"))
    ring = doc["geometry"]["lot_outline"][0]
    for i in range(len(ring) - 1):
        (ax, ay), (bx, by) = ring[i], ring[i + 1]
        (px, py), (qx, qy) = drawn[i], drawn[(i + 1) % len(drawn)]
        assert math.isclose(math.hypot(qx - px, qy - py), math.hypot(bx - ax, by - ay) * k,
                            abs_tol=0.02)


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_legend_lists_exactly_what_is_drawn(path):
    _, drawing = _plan(path)
    root = parse(drawing.svg)
    legend = next(g for g in root.iter(f"{SVG_NS}g") if g.get("data-role") == "legend")
    shown = [el.text for el in legend.iter(f"{SVG_NS}text") if el.get("data-role") == "legend"]
    expected = [s.label for s in STYLE_TABLE if s.in_legend and s.kind in drawing.kinds_drawn]
    assert shown == expected
    fills = {p.get("fill") for p in root.iter(f"{SVG_NS}path")}
    for kind in drawing.kinds_drawn:
        style = next(s for s in STYLE_TABLE if s.kind == kind)
        if style.geometry == "area":
            assert style.fill in fills, kind


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_footprint_lies_within_the_lot(path):
    doc, drawing = _plan(path)
    lot = doc["geometry"]["lot_outline"][0]
    footprint = [p for p in parse(drawing.svg).iter(f"{SVG_NS}path") if p.get("data-floor")]
    for element in footprint:
        plate = resolve(doc, element.get("data-source"))
        assert plate["floor"] == 1
        assert all(point_in_or_on(tuple(pt), lot) for ring in plate["outline"] for pt in ring)


def test_yards_are_hatched_only_where_the_results_require_them():
    doc, drawing = _plan(KIT_FIXTURES / "synthetic_interior_lot_mixed_use.json")
    root = parse(drawing.svg)
    hatched = [p for p in root.iter(f"{SVG_NS}path") if p.get("fill") == "url(#hatch-yard)"]
    assert [p.get("data-source") for p in hatched] == ["/geometry/yards/entries/0"]
    assert any(pt.get("id") == "hatch-yard" for pt in root.iter(f"{SVG_NS}pattern"))
    names = [t for el, t in texts(root) if el.get("data-role") == "yard_kind"]
    assert names == ["Rear yard"]  # the side yard is not required: stated, never drawn

    _, corner = _plan(CONTRACT_FIXTURES / "synthetic_all_answers_available.json")
    assert "hatch-yard" not in corner.svg
    assert "yard" not in corner.kinds_drawn


def test_street_names_come_from_the_results_and_no_width_is_invented():
    for path in FIXTURES:
        doc, drawing = _plan(path)
        found = texts(parse(drawing.svg))
        streets = [t for el, t in found if el.get("data-role") == "street"]
        assert streets == [s["street"] for s in doc["geometry"]["streets"]]
        # The results carry no street-width value (only a fact id), so none is printed.
        assert not [t for el, t in found if el.get("data-source", "").startswith(
            "/geometry/streets") and el.get("data-role") != "street"]


def test_the_c4_checker_catches_typed_and_unsourced_numbers():
    doc, drawing = _plan(CONTRACT_FIXTURES / "synthetic_all_answers_available.json")
    typed = drawing.svg.replace(">100 ft<", ">116 ft<", 1)  # the benchmark defect
    assert label_problems(typed, doc) and numbers_not_in_input(typed, doc)
    unsourced = drawing.svg.replace(">Grid north<", ">Grid north 20<", 1)
    assert label_problems(unsourced, doc)


def test_north_arrow_is_present():
    _, drawing = _plan(FIXTURES[0])
    root = parse(drawing.svg)
    arrow = next(g for g in root.iter(f"{SVG_NS}g") if g.get("data-role") == "north-arrow")
    assert [el.text for el in arrow.iter(f"{SVG_NS}text")] == ["N", "Grid north"]


def test_missing_layers_are_named_in_one_line_each():
    doc, drawing = _plan(
        CONTRACT_FIXTURES / "synthetic_envelope_not_available_existing_building.json")
    notes = [source for source, _, role in pieces(parse(drawing.svg))
             if role == "note" and source]
    assert notes == ["/geometry/measurement/label", "/geometry/yards/reason",
                     "/geometry/setback_lines_per_level/reason", "/geometry/floor_plates/reason"]
    assert drawing.kinds_drawn == ("lot_line", "dimension")


def test_a_street_width_case_says_so_on_every_drawing():
    from app.drawings.kit import render_massing

    doc = load(CONTRACT_FIXTURES / "synthetic_needs_street_width_narrow_case.json")
    for render in (render_site_plan, render_massing):
        found = [(source, text) for source, text, _ in pieces(parse(render(doc, env=ENV_ON).svg))
                 if source and source.startswith("/street_width_case")]
        assert found == [("/street_width_case/marker", "Needs street width"),
                         ("/street_width_case/assumptions/0/street", "Synthetic Street B"),
                         ("/street_width_case/assumptions/0/assumed", "narrow")]
