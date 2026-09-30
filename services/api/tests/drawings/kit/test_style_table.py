"""The drawing style table: one table, complete, colorblind-safe, readable in
black-and-white print (plan section 5c item 5)."""

from __future__ import annotations

import itertools
import json
import math
import re

import pytest

from app.drawings.kit import schema_source
from app.drawings.kit.hatches import hatch_defs, hatch_fill
from app.drawings.kit.styles import AREA, LINE, STYLE_TABLE, style_for, style_table_as_dict

USES = ("residential", "commercial", "community_facility", "cellar", "bulkhead_or_mechanical")
PLAN_KINDS = USES + ("yard", "court", "setback_zone", "lot_line", "envelope")
HEX = re.compile(r"^#[0-9A-F]{6}$")

# Machado, Oliveira & Fernandes (2009) CVD simulation matrices at severity 1.0
# (linear RGB), the same constants the dataviz palette validator uses.
MACHADO = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
}


def _linear(color: str) -> list[float]:
    channels = [int(color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]


def _oklab(rgb) -> tuple[float, float, float]:
    r, g, b = rgb
    lms = [
        (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3),
        (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3),
        (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3),
    ]
    l_, m, s = lms
    return (0.2104542553 * l_ + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l_ - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l_ + 0.7827717662 * m - 0.8086757660 * s)


def _delta_e(c1: str, c2: str, kind: str | None = None) -> float:
    """OKLab Delta E x100, optionally under simulated color-vision deficiency."""
    def sim(color):
        rgb = _linear(color)
        if kind is None:
            return rgb
        return [max(0.0, min(1.0, sum(m * v for m, v in zip(row, rgb, strict=True))))
                for row in MACHADO[kind]]
    return 100 * math.dist(_oklab(sim(c1)), _oklab(sim(c2)))


def test_table_covers_every_plan_kind_once():
    kinds = [s.kind for s in STYLE_TABLE]
    assert len(kinds) == len(set(kinds))
    assert set(PLAN_KINDS) <= set(kinds)


def test_uses_match_the_results_contract_vocabulary():
    results = schema_source.schema_documents()[0]
    assert tuple(results["$defs"]["floor_use"]["enum"]) == USES
    assert all(style_for(use).geometry == AREA for use in USES)


def test_every_entry_is_well_formed():
    layers = [s.cad_layer for s in STYLE_TABLE]
    assert len(layers) == len(set(layers))
    for style in STYLE_TABLE:
        assert HEX.match(style.outline)
        assert style.line_weight_pt > 0
        assert re.fullmatch(r"[A-Z0-9-]{1,31}", style.cad_layer)
        assert style.label and style.geometry in (AREA, LINE)
        if style.geometry == AREA:
            assert HEX.match(style.fill)
        else:
            assert style.fill is None and style.hatch is None
        if style.hatch:
            assert HEX.match(style.hatch.color)
            assert style.hatch.angle_deg in (0, 45, 90, 135) and style.hatch.spacing_pt > 0


def test_black_and_white_every_area_kind_has_a_unique_hatch():
    signatures = [
        (s.hatch.angle_deg, s.hatch.spacing_pt, s.hatch.crossed) if s.hatch else None
        for s in STYLE_TABLE if s.geometry == AREA
    ]
    assert len(signatures) == len(set(signatures))


def test_black_and_white_every_line_kind_differs_by_weight_or_dash():
    looks = [(s.line_weight_pt, s.dash_pt) for s in STYLE_TABLE if s.geometry == LINE]
    assert len(looks) == len(set(looks))


@pytest.mark.parametrize("pair", list(itertools.combinations(USES, 2)), ids="-".join)
def test_use_colors_separate_for_normal_and_colorblind_vision(pair):
    a, b = (style_for(kind).fill for kind in pair)
    assert _delta_e(a, b) >= 15.0  # normal-vision floor
    assert _delta_e(a, b, "protan") >= 8.0  # CVD target
    assert _delta_e(a, b, "deutan") >= 8.0


def test_zone_hatch_colors_separate_under_colorblind_vision():
    colors = [style_for(k).hatch.color for k in ("yard", "court", "setback_zone")]
    for a, b in itertools.combinations(colors, 2):
        assert min(_delta_e(a, b, "protan"), _delta_e(a, b, "deutan")) >= 8.0


def test_serialized_table_is_json_ready_and_ordered():
    data = style_table_as_dict()
    assert [s["kind"] for s in data["styles"]] == [s.kind for s in STYLE_TABLE]
    assert json.loads(json.dumps(data)) == data


def test_unknown_kind_fails_loudly():
    with pytest.raises(ValueError):
        style_for("parking")


def test_hatch_patterns_follow_the_table():
    defs = hatch_defs(["residential", "yard", "cellar", "yard"])
    assert defs.count("<pattern") == 2  # residential is unhatched; yard deduplicated
    assert 'id="hatch-yard"' in defs and 'patternTransform="rotate(-45.00)"' in defs
    cellar = defs[defs.index('id="hatch-cellar"'):]
    assert cellar[: cellar.index("</pattern>")].count("<line") == 2  # crossed
    assert hatch_fill("residential") is None
    assert hatch_fill("yard") == "url(#hatch-yard)"
