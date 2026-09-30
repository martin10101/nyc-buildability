"""The results -> DrawingInput adapter validates and fails closed (task E-01)."""

from __future__ import annotations

import copy

import pytest

from app.drawings.kit import schema_source
from app.drawings.kit.adapter import load_drawing_input
from app.drawings.kit.errors import DrawingInputError
from app.drawings.kit.model import DrawingInput, LayerUnavailable, Unavailable

from .kit_support import CONTRACT_FIXTURES, KIT_FIXTURES, fixture_paths, load

BASE = load(CONTRACT_FIXTURES / "synthetic_all_answers_available.json")
MIXED = load(KIT_FIXTURES / "synthetic_interior_lot_mixed_use.json")


def _mutated(doc: dict, mutate) -> dict:
    changed = copy.deepcopy(doc)
    mutate(changed)
    return changed


@pytest.mark.parametrize("path", fixture_paths(), ids=lambda p: p.stem)
def test_every_valid_fixture_loads(path):
    data = load_drawing_input(load(path))
    assert isinstance(data, DrawingInput)
    assert data.lot.source == "/geometry/lot_outline"


def test_lot_outline_without_envelope_still_loads():
    doc = load(CONTRACT_FIXTURES / "synthetic_envelope_not_available_existing_building.json")
    data = load_drawing_input(doc)
    assert isinstance(data.floor_plates, LayerUnavailable)
    assert data.floor_plates.reason == doc["geometry"]["floor_plates"]["reason"]
    assert isinstance(data.yards, LayerUnavailable)
    assert data.streets[0].name == "Synthetic Street C"


def test_geometry_not_available_returns_the_results_reason():
    doc = _mutated(BASE, lambda d: d.__setitem__("geometry", {
        "status": "not_available", "reason": "Lot outline not available - no tax lot found.",
        "reason_kind": "missing_input"}))
    result = load_drawing_input(doc)
    assert result == Unavailable("geometry", "Lot outline not available - no tax lot found.",
                                 "missing_input", "/geometry")


def test_sources_point_into_the_results():
    data = load_drawing_input(MIXED)
    assert data.floor_rows[1].source == "/floor_by_floor/1"
    assert data.floor_plates[2].source == "/geometry/floor_plates/entries/2"
    assert data.yards[0].source == "/geometry/yards/entries/0"
    assert data.yards_not_required[0].kind == "side"


def _set(path: str, value):
    def mutate(doc):
        node = doc
        parts = path.strip("/").split("/")
        for part in parts[:-1]:
            node = node[int(part)] if isinstance(node, list) else node[part]
        last = parts[-1]
        node[int(last) if isinstance(node, list) else last] = value
    return mutate


LOT = "/geometry/lot_outline/0"
PLATE0 = "/geometry/floor_plates/entries/0"

INVALID_CASES = [
    ("schema_invalid", lambda d: d.pop("geometry"), ""),
    ("schema_invalid", _set("/geometry/units", "meters"), "/geometry"),
    ("ring_not_closed", _set(LOT, [[0, 0], [50, 0], [50, 100], [0, 100], [0, 1]]), LOT),
    ("ring_degenerate", _set(LOT, [[0, 0], [50, 0], [0, 0], [50, 0], [0, 0]]), LOT),
    ("ring_not_simple", _set(LOT, [[0, 0], [50, 100], [50, 0], [0, 100], [0, 0]]), LOT),
    ("ring_not_simple", _set(LOT, [[0, 0], [50, 0], [25, 0], [0, 100], [0, 0]]), LOT),
    ("ring_not_simple", _set(LOT, [[0, 0], [10, 0], [20, 0], [0, 0]]), LOT),  # zero area
    ("non_finite_number", _set(LOT, [[0, 0], [float("nan"), 0], [50, 100], [0, 0]]), f"{LOT}/1"),
    ("coordinate_out_of_range", _set(LOT, [[0, 0], [2e8, 0], [0, 100], [0, 0]]), f"{LOT}/1"),
    ("plate_outside_lot",
     _set(f"{PLATE0}/outline", [[[0, 0], [60, 0], [60, 50], [0, 50], [0, 0]]]),
     f"{PLATE0}/outline"),
    ("frontage_off_lot",
     _set("/geometry/streets/0/frontage_line", [[0, -5], [50, -5]]),
     "/geometry/streets/0/frontage_line/0"),
    ("plates_rows_mismatch", _set(f"{PLATE0}/gross_sf", 2400), "/geometry/floor_plates"),
    ("plates_rows_mismatch", _set(f"{PLATE0}/use", "commercial"), "/geometry/floor_plates"),
    ("floor_height_conflict", lambda d: d["floor_by_floor"].append(
        dict(d["floor_by_floor"][0], height_ft=99, gross_sf=0, zoning_floor_area_sf=0)),
     "/floor_by_floor/4"),
    ("floors_not_contiguous", lambda d: [
        r.__setitem__("floor", 5) for r in d["floor_by_floor"] if r["floor"] == 4] and [
        p.__setitem__("floor", 5) for p in d["geometry"]["floor_plates"]["entries"]
        if p["floor"] == 4], "/floor_by_floor"),
    ("setback_line_degenerate",
     _set("/geometry/setback_lines_per_level/entries/0/lines/0", [[15, 15], [15, 15]]),
     "/geometry/setback_lines_per_level/entries/0/lines/0"),
    ("setback_line_outside_lot",
     _set("/geometry/setback_lines_per_level/entries/0/lines/0", [[15, 15], [70, 15]]),
     "/geometry/setback_lines_per_level/entries/0/lines/0"),
]


@pytest.mark.parametrize(("code", "mutate", "location"), INVALID_CASES,
                         ids=[f"{c[0]}-{i}" for i, c in enumerate(INVALID_CASES)])
def test_invalid_input_fails_closed(code, mutate, location):
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(_mutated(BASE, mutate))
    assert caught.value.code == code
    assert caught.value.location.startswith(location)


def test_yard_outside_lot_fails_closed():
    def mutate(doc):
        doc["geometry"]["yards"]["entries"][0]["outline"] = [
            [[0, 70], [60, 70], [60, 101], [0, 101], [0, 70]]]
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(_mutated(MIXED, mutate))
    assert caught.value.code == "yard_outside_lot"


def test_hole_outside_exterior_fails_closed():
    def mutate(doc):
        doc["geometry"]["lot_outline"].append([[70, 10], [80, 10], [80, 20], [70, 20], [70, 10]])
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(_mutated(BASE, mutate))
    assert caught.value.code == "hole_outside_exterior"


def test_plate_over_a_lot_hole_fails_closed():
    def mutate(doc):
        doc["geometry"]["lot_outline"].append([[10, 10], [20, 10], [20, 20], [10, 20], [10, 10]])
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(_mutated(BASE, mutate))
    assert caught.value.code == "plate_outside_lot"


def test_not_a_mapping_fails_closed():
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input([1, 2, 3])
    assert caught.value.code == "schema_invalid"


def test_schema_unavailable_fails_closed(monkeypatch):
    monkeypatch.setattr(schema_source, "_bundled_texts", lambda: None)
    monkeypatch.setattr(schema_source, "_canonical_texts", lambda: None)
    schema_source.schema_documents.cache_clear()
    schema_source.results_validator.cache_clear()
    try:
        with pytest.raises(DrawingInputError) as caught:
            load_drawing_input(BASE)
        assert caught.value.code == "schema_unavailable"
    finally:
        schema_source.schema_documents.cache_clear()
        schema_source.results_validator.cache_clear()


def test_schemas_come_from_one_source_results_first():
    docs = schema_source.schema_documents()
    assert docs[0]["title"] == "Results"
    assert [d["$id"].rsplit("/", 1)[1] for d in docs] == [
        "results.schema.json", "common.schema.json", "site_fact.schema.json", "study.schema.json"]


def test_floor_numbering_only_matters_when_floor_plates_are_drawn():
    doc = load(CONTRACT_FIXTURES / "synthetic_envelope_not_available_existing_building.json")
    doc["floor_by_floor"] = [dict(BASE["floor_by_floor"][0], floor=3)]  # a gap, no plates
    assert isinstance(load_drawing_input(doc), DrawingInput)
