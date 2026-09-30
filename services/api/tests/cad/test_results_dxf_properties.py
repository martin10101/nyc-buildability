"""The results DXF over generated lots and buildings (task E-03): the same 30
seeded documents the drawing-kit property tests draw (rectangular or chamfered
lots, local_feet or EPSG:2263, cellars, split and setback floors), so the DXF
and the SVGs are proven on the same geometry."""

from __future__ import annotations

import pytest

from app.cad.results_dxf import render_results_dxf
from app.drawings.kit.styles import style_for

from ..drawings.kit.test_properties import SEEDS, generated_results
from .results_dxf_support import ENV_ON, expected_counts, open_ring, parse_dxf, render


@pytest.mark.parametrize("seed", SEEDS)
def test_generated_results_give_a_faithful_dxf(seed):
    doc = generated_results(seed)
    result = render(doc)
    parsed = parse_dxf(result.text)
    assert parsed.counts() == expected_counts(doc, len(result.notes))
    lot = parsed.on("C-PROP-LINE")
    # the writer prints six decimals (dxf_writer); generated sums are not always exact
    assert [[(x, y) for x, y, _ in e.points] for e in lot] == [
        [pytest.approx(p, abs=5e-7) for p in open_ring(r)]
        for r in doc["geometry"]["lot_outline"]]
    # floor plates stand at the floor-to-floor stack of floor_by_floor
    heights = {row["floor"]: row["height_ft"] for row in doc["floor_by_floor"]}
    above = sorted(f for f in heights if f >= 1)
    below = sorted((f for f in heights if f <= 0), reverse=True)
    bottom = {f: float(sum(heights[g] for g in above[:i])) for i, f in enumerate(above)}
    bottom |= {f: -float(sum(heights[g] for g in below[: i + 1])) for i, f in enumerate(below)}
    plates = [e for e in parsed.entities if e.kind == "POLYLINE" and e.layer.startswith("A-MASS")]
    entries = doc["geometry"]["floor_plates"]["entries"]
    assert [(e.layer, e.points[0][2]) for e in plates] == [
        (style_for(p["use"]).cad_layer, pytest.approx(bottom[p["floor"]])) for p in entries]
    assert any("not a survey" in n.text for n in result.notes)
    assert render_results_dxf(doc, env=ENV_ON) == result
