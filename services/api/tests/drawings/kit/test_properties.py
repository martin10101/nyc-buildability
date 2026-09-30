"""Property tests over generated results documents (seeded, deterministic).

For many generated lots and buildings - rectangular or chamfered lots, local
or EPSG:2263 coordinates, cellars, split and setback floors, yards present or
not available - both drawings must: print only numbers read from the results
(check C-4), keep every footprint inside the lot, draw exactly the floors in
the results, never overlap labels, and render byte-identically twice.
"""

from __future__ import annotations

import copy
import random

import pytest

from app.drawings.kit import Drawing, render_massing, render_site_plan

from .drawn_checks import massing_problems, site_plan_problems
from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    SVG_NS,
    label_problems,
    load,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    point_in_or_on,
    resolve,
)

BASE = load(CONTRACT_FIXTURES / "synthetic_all_answers_available.json")
SEEDS = range(30)


def _rect(x0, y0, x1, y1):
    return [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]


def _r2(value: float) -> float:
    return round(value, 2)


def generated_results(seed: int) -> dict:
    rnd = random.Random(seed)
    doc = copy.deepcopy(BASE)
    geo = doc["geometry"]
    w, d = _r2(rnd.uniform(20, 220)), _r2(rnd.uniform(40, 220))
    if rnd.random() < 0.5:
        ox, oy, geo["crs"] = 0.0, 0.0, "local_feet"
    else:
        ox, oy = 1_000_000.0 + rnd.randint(0, 9999), 200_000.0 + rnd.randint(0, 9999)
        geo["crs"] = "EPSG:2263"
    chamfer = _r2(rnd.uniform(0, min(w, d) / 3)) if rnd.random() < 0.5 else 0.0
    lot = [[ox, oy], [ox + w, oy], [ox + w, oy + d - chamfer]]
    if chamfer:
        lot.append([ox + w - chamfer, oy + d])
    lot += [[ox, oy + d], [ox, oy]]
    geo["lot_outline"] = [lot]
    geo["streets"] = [{"street": f"Generated Street {seed}",
                       "frontage_line": [[ox, oy], [ox + w, oy]], "street_width_fact_id": None}]
    rear = _r2(rnd.uniform(5, d / 4))
    if rnd.random() < 0.7:
        yard = {"kind": "rear", "status": "required", "depth_ft": rear,
                "outline": _rect(ox, oy + d - rear, ox + w - chamfer, oy + d),
                "zr_sections": BASE["geometry"]["yards"]["entries"][0]["zr_sections"]}
        geo["yards"] = {"status": "available", "entries": [yard]}
    else:
        geo["yards"] = {"status": "not_available", "reason": "Yards not available.",
                        "reason_kind": "rule_not_implemented"}
    geo["setback_lines_per_level"] = {"status": "not_available", "reason": "Not built.",
                                      "reason_kind": "rule_not_implemented"}
    depth = _r2(rnd.uniform(10, d - chamfer - rear - 1))
    rows, plates = [], []
    floors = list(range(-rnd.randint(0, 2) + 1, rnd.randint(1, 14) + 1))
    inset = 0.0
    for floor in floors:
        if floor >= 2 and rnd.random() < 0.25:
            inset = _r2(min(inset + rnd.uniform(1, 8), min(w, depth) / 3))
        x0, y0, x1, y1 = ox + inset, oy + inset, ox + w - inset, oy + depth - inset
        use = "cellar" if floor <= 0 else rnd.choice(
            ["residential", "commercial", "community_facility"] if floor == 1 else ["residential"])
        height = rnd.choice([9.5, 10, 10.75, 12, 15])
        label = f"Cellar {1 - floor}" if floor <= 0 else f"Floor {floor}"
        split = floor == 1 and rnd.random() < 0.4
        parts = ([(y0, _r2(y0 + (y1 - y0) / 2), "commercial"),
                  (_r2(y0 + (y1 - y0) / 2), y1, "residential")] if split else [(y0, y1, use)])
        for py0, py1, part_use in parts:
            gross = _r2((x1 - x0) * (py1 - py0))
            plates.append({"floor": floor, "outline": _rect(x0, py0, x1, py1), "gross_sf": gross,
                           "use": part_use})
            rows.append({"floor": floor, "floor_label": label, "gross_sf": gross,
                         "deductions_sf": 0, "zoning_floor_area_sf": gross, "height_ft": height,
                         "use": part_use})
    geo["floor_plates"] = {"status": "available", "entries": plates}
    doc["floor_by_floor"] = rows
    return doc


@pytest.mark.parametrize("seed", SEEDS)
def test_generated_drawings_hold_the_c4_properties(seed):
    doc = generated_results(seed)
    lot = doc["geometry"]["lot_outline"][0]
    for render in (render_site_plan, render_massing):
        drawing = render(doc, env=ENV_ON)
        assert isinstance(drawing, Drawing)
        assert label_problems(drawing.svg, doc) == []
        assert numbers_not_in_input(drawing.svg, doc) == []
        assert overlapping_labels(drawing.svg) == []
        assert render(doc, env=ENV_ON) == drawing
        checks = site_plan_problems if render is render_site_plan else massing_problems
        assert checks(drawing.svg, doc) == []
    root = parse(drawing.svg)  # the massing
    drawn = sorted(int(g.get("data-floor")) for g in root.iter(f"{SVG_NS}g") if g.get("data-floor"))
    assert drawn == sorted({row["floor"] for row in doc["floor_by_floor"]})
    for ref in {p.get("data-plate") for p in root.iter(f"{SVG_NS}path") if p.get("data-plate")}:
        outline = resolve(doc, ref)["outline"]
        assert all(point_in_or_on(tuple(pt), lot) for ring in outline for pt in ring)
