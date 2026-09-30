"""Axonometric massing SVG (plan section 5c items 2 and 5; check C-4; task E-01)."""

from __future__ import annotations

import copy
import math
import re
from collections import defaultdict

import pytest

from app.drawings.kit import Drawing, Unavailable, render_massing
from app.drawings.kit.color import mix, relative_luminance
from app.drawings.kit.projection import TOP_LIGHTENING
from app.drawings.kit.styles import style_for

from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    KIT_FIXTURES,
    SVG_NS,
    fixture_paths,
    label_problems,
    load,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    point_in_or_on,
    resolve,
    texts,
)

WITH_PLATES = [p for p in fixture_paths()
               if load(p)["geometry"]["floor_plates"]["status"] == "available"]
IDS = [p.stem for p in WITH_PLATES]


def _massing(path) -> tuple[dict, Drawing]:
    doc = load(path)
    drawing = render_massing(doc, env=ENV_ON)
    assert isinstance(drawing, Drawing)
    return doc, drawing


def _faces(drawing: Drawing):
    """Base face paths (hatch overlays excluded), in document order."""
    return [p for p in parse(drawing.svg).iter(f"{SVG_NS}path")
            if p.get("data-face") and not p.get("fill", "").startswith("url(")]


@pytest.mark.parametrize("path", WITH_PLATES, ids=IDS)
def test_every_label_is_read_from_the_results(path):
    doc, drawing = _massing(path)
    assert label_problems(drawing.svg, doc) == []
    assert numbers_not_in_input(drawing.svg, doc) == []
    assert overlapping_labels(drawing.svg) == []


@pytest.mark.parametrize("path", WITH_PLATES, ids=IDS)
def test_floors_drawn_equal_floors_in_the_results(path):
    doc, drawing = _massing(path)
    root = parse(drawing.svg)
    drawn = [int(g.get("data-floor")) for g in root.iter(f"{SVG_NS}g") if g.get("data-floor")]
    assert drawn == sorted({row["floor"] for row in doc["floor_by_floor"]})
    assert drawn == sorted({p["floor"] for p in doc["geometry"]["floor_plates"]["entries"]})
    tops = [f.get("data-plate") for f in _faces(drawing) if f.get("data-face") == "top"]
    entries = doc["geometry"]["floor_plates"]["entries"]
    expected = [f"/geometry/floor_plates/entries/{i}" for i in range(len(entries))]
    assert sorted(tops) == sorted(expected)
    rows = [el.get("data-source") for el, _ in texts(root) if el.get("data-role") == "floor_name"]
    assert sorted(rows) == sorted(f"/floor_by_floor/{i}/floor_label"
                                  for i in range(len(doc["floor_by_floor"])))


@pytest.mark.parametrize("path", WITH_PLATES, ids=IDS)
def test_footprints_lie_within_the_lot(path):
    doc, drawing = _massing(path)
    lot = doc["geometry"]["lot_outline"][0]
    for plate_ref in {f.get("data-plate") for f in _faces(drawing)}:
        plate = resolve(doc, plate_ref)
        assert all(point_in_or_on(tuple(pt), lot) for ring in plate["outline"] for pt in ring)


@pytest.mark.parametrize("path", WITH_PLATES, ids=IDS)
def test_painters_order_floors_bottom_up_sides_before_tops(path):
    _, drawing = _massing(path)
    root = parse(drawing.svg)
    groups = [g for g in root.iter(f"{SVG_NS}g") if g.get("data-floor")]
    for group in groups:
        kinds = [p.get("data-face") for p in group.iter(f"{SVG_NS}path")
                 if not p.get("fill", "").startswith("url(")]
        assert kinds == sorted(kinds, key=lambda k: k == "top")  # all sides, then all tops
        assert "top" in kinds


@pytest.mark.parametrize("path", WITH_PLATES, ids=IDS)
def test_faces_colored_by_use_and_shaded_top_lightest(path):
    doc, drawing = _massing(path)
    by_plate = defaultdict(lambda: {"side": [], "top": []})
    for face in _faces(drawing):
        by_plate[face.get("data-plate")][face.get("data-face")].append(face.get("fill"))
    for ref, faces in by_plate.items():
        base = style_for(resolve(doc, ref)["use"]).fill
        assert faces["top"] == [mix(base, "#FFFFFF", TOP_LIGHTENING)]
        top_lum = relative_luminance(faces["top"][0])
        assert all(relative_luminance(side) < top_lum for side in faces["side"])


@pytest.mark.parametrize("path", WITH_PLATES, ids=IDS)
def test_each_floor_is_extruded_by_its_floor_to_floor_height(path):
    doc, drawing = _massing(path)
    heights = {row["floor"]: row["height_ft"] for row in doc["floor_by_floor"]}
    ratios = []
    for face in _faces(drawing):
        if face.get("data-face") != "side":
            continue
        floor = resolve(doc, face.get("data-plate"))["floor"]
        d = face.get("d")
        pts = [(float(x), float(y)) for x, y in re.findall(r"[ML](-?[\d.]+) (-?[\d.]+)", d)]
        # quad order: bottom a, bottom b, top b, top a -> vertical edge = b bottom to b top
        ratios.append(math.dist(pts[1], pts[2]) / heights[floor])
    assert ratios and max(ratios) - min(ratios) < 0.02 * max(ratios)


def test_split_use_floor_draws_each_use_and_lists_each_row():
    doc, drawing = _massing(KIT_FIXTURES / "synthetic_interior_lot_mixed_use.json")
    floor1 = [f for f in _faces(drawing)
              if resolve(doc, f.get("data-plate"))["floor"] == 1 and f.get("data-face") == "top"]
    assert sorted(resolve(doc, f.get("data-plate"))["use"] for f in floor1) == [
        "commercial", "community_facility"]
    swatches = [r.get("data-use") for r in parse(drawing.svg).iter(f"{SVG_NS}rect")
                if r.get("data-use")]
    assert swatches == [row["use"] for row in sorted(
        doc["floor_by_floor"], key=lambda r: -r["floor"])]


def test_massing_not_available_carries_the_results_reason():
    doc = load(CONTRACT_FIXTURES / "synthetic_envelope_not_available_existing_building.json")
    result = render_massing(doc, env=ENV_ON)
    assert result == Unavailable(
        "massing", doc["geometry"]["floor_plates"]["reason"], "rule_not_implemented",
        "/geometry/floor_plates/reason")


def test_no_floor_plates_is_not_drawn():
    doc = copy.deepcopy(load(CONTRACT_FIXTURES / "synthetic_all_answers_available.json"))
    doc["geometry"]["floor_plates"]["entries"] = []
    doc["floor_by_floor"] = []
    result = render_massing(doc, env=ENV_ON)
    assert isinstance(result, Unavailable) and result.reason_kind == "missing_input"


def test_geometry_not_available_is_not_drawn():
    doc = copy.deepcopy(load(CONTRACT_FIXTURES / "synthetic_all_answers_available.json"))
    doc["geometry"] = {"status": "not_available", "reason": "No lot outline.",
                       "reason_kind": "missing_input"}
    result = render_massing(doc, env=ENV_ON)
    assert result == Unavailable("massing", "No lot outline.", "missing_input", "/geometry/reason")
