"""The location and zoning maps draw the real city geometry and label it from
the data (task E-07, plan section 5c item 2).

Checks: every printed label is read from the data (check C-4); no label overlaps
another; the subject lot and every district/footprint is drawn once, and its
drawn area (re-measured through the map scale) equals its world area; the
zoning map carries the official use-limitation, accuracy and attribution notes;
the legend is generated from exactly the kinds drawn; and no raster base-map
imagery is embedded.
"""

from __future__ import annotations

import pytest

from app.drawings.kit.styles import AREA, style_for
from app.drawings.maps import Drawing, render_location_map, render_zoning_map

from .maps_support import (
    SVG_NS,
    base_sources,
    drawn_world_area,
    fixture_paths,
    label_problems,
    load,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    pieces,
    world_area,
)

RENDERERS = (render_location_map, render_zoning_map)
CASES = [(path, render) for path in fixture_paths() for render in RENDERERS]
MIDBLOCK = next(p for p in fixture_paths() if p.stem == "synthetic_midblock_split_lot")


def _drawings():
    for path in fixture_paths():
        doc = load(path)
        for render in RENDERERS:
            result = render(doc, env={"LANE_E_ENABLED": "1"})
            if isinstance(result, Drawing):
                yield path, doc, result


def _texts_by_role(svg: str, role: str) -> list[str]:
    root = parse(svg)
    out = []
    for el in root.iter(f"{SVG_NS}text"):
        if el.get("data-role") == role:
            out.append("".join(el.itertext()))
    return out


@pytest.mark.parametrize(("path", "render"), CASES,
                         ids=[f"{p.stem}-{r.__name__}" for p, r in CASES])
def test_every_label_is_read_from_the_data(path, render):
    result = render(load(path), env={"LANE_E_ENABLED": "1"})
    if not isinstance(result, Drawing):
        pytest.skip("layer not available for this map")
    doc = load(path)
    assert label_problems(result.svg, doc) == []
    assert numbers_not_in_input(result.svg, doc) == []
    assert overlapping_labels(result.svg) == []


@pytest.mark.parametrize(("path", "render"), CASES,
                         ids=[f"{p.stem}-{r.__name__}" for p, r in CASES])
def test_no_raster_base_map_imagery(path, render):
    result = render(load(path), env={"LANE_E_ENABLED": "1"})
    if not isinstance(result, Drawing):
        pytest.skip("layer not available for this map")
    svg = result.svg
    assert "<image" not in svg
    assert "href=" not in svg  # no linked tiles / external raster


def test_subject_lot_drawn_once_and_area_matches():
    doc = load(MIDBLOCK)
    for render in RENDERERS:
        result = render(doc, env={"LANE_E_ENABLED": "1"})
        assert isinstance(result, Drawing)
        sources = base_sources(result.svg)
        assert sources.count("/map_context/subject_lot/outline") == 1
        drawn = drawn_world_area(result.svg, "/map_context/subject_lot/outline")
        expected = world_area(doc, "/map_context/subject_lot/outline")
        assert drawn is not None and abs(drawn - expected) <= max(5.0, 0.01 * expected)


def test_zoning_map_draws_each_district_with_its_symbol():
    doc = load(MIDBLOCK)
    result = render_zoning_map(doc, env={"LANE_E_ENABLED": "1"})
    assert isinstance(result, Drawing)
    districts = doc["map_context"]["zoning_districts"]["entries"]
    sources = base_sources(result.svg)
    for i in range(len(districts)):
        pointer = f"/map_context/zoning_districts/entries/{i}"
        assert sources.count(pointer) == 1
        drawn = drawn_world_area(result.svg, pointer)
        expected = world_area(doc, f"{pointer}/outline")
        assert drawn is not None and abs(drawn - expected) <= max(50.0, 0.01 * expected)
    symbols = _texts_by_role(result.svg, "zoning_district")
    assert sorted(symbols) == sorted(e["zonedist"] for e in districts)


def test_location_map_draws_every_footprint():
    doc = load(MIDBLOCK)
    result = render_location_map(doc, env={"LANE_E_ENABLED": "1"})
    assert isinstance(result, Drawing)
    footprints = doc["map_context"]["building_footprints"]["entries"]
    sources = base_sources(result.svg)
    for i in range(len(footprints)):
        assert sources.count(f"/map_context/building_footprints/entries/{i}") == 1


def test_zoning_map_carries_the_official_notes():
    doc = load(MIDBLOCK)
    result = render_zoning_map(doc, env={"LANE_E_ENABLED": "1"})
    assert isinstance(result, Drawing)
    z = doc["map_context"]["zoning_districts"]
    by_source = {src: text for src, text, _role in pieces(parse(result.svg)) if src}
    for key in ("use_limitation", "accuracy", "attribution"):
        source = f"/map_context/zoning_districts/{key}"
        assert source in by_source, f"{key} note missing"
        assert by_source[source] == " ".join(z[key].split())


def test_legend_is_generated_from_the_kinds_drawn():
    doc = load(MIDBLOCK)
    zoning = render_zoning_map(doc, env={"LANE_E_ENABLED": "1"})
    location = render_location_map(doc, env={"LANE_E_ENABLED": "1"})
    assert isinstance(zoning, Drawing) and isinstance(location, Drawing)
    assert set(zoning.kinds_drawn) == {"zoning_district", "subject_lot"}
    assert set(location.kinds_drawn) == {"building_footprint", "subject_lot"}
    # the legend text lists exactly those kinds' labels
    assert set(_texts_by_role(zoning.svg, "legend")) == {"Zoning district", "Subject lot"}
    assert set(_texts_by_role(location.svg, "legend")) == {"Building footprint", "Subject lot"}


@pytest.mark.parametrize("kind", ["subject_lot", "zoning_district", "building_footprint"])
def test_map_kinds_are_in_the_shared_style_table(kind):
    style = style_for(kind)
    assert style.geometry == AREA
    assert style.in_legend
    assert style.hatch is not None  # readable in black-and-white print
