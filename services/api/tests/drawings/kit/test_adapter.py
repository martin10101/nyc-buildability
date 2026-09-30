"""The results -> DrawingInput adapter validates and fails closed (task E-01)."""

from __future__ import annotations

import copy

import pytest

from app.contracts.study_contracts import StudyContractError
from app.drawings.kit import adapter
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
    assert isinstance(data.envelope, LayerUnavailable)
    assert data.envelope.reason == doc["geometry"]["envelope"]["reason"]
    assert data.streets[0].name == "Synthetic Street C"


def test_envelope_tiers_load_with_their_heights_and_sources():
    data = load_drawing_input(BASE)
    assert [(t.bottom_ft, t.top_ft) for t in data.envelope] == [(0.0, 45.0), (45.0, 55.0)]
    assert data.envelope[1].source == "/geometry/envelope/tiers/1"
    assert data.envelope[1].outline.source == "/geometry/envelope/tiers/1/outline"
    assert data.envelope[1].outline.exterior[0] == (15.0, 15.0)


def test_too_many_envelope_tiers_fails_closed(monkeypatch):
    monkeypatch.setattr("app.drawings.kit.adapter.MAX_ENVELOPE_TIERS", 1)
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(BASE)
    assert caught.value.code == "too_many_envelope_tiers"


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
TIER1 = "/geometry/envelope/tiers/1"

INVALID_CASES = [
    ("schema_invalid", lambda d: d.pop("geometry"), ""),
    ("schema_invalid", _set("/geometry/units", "meters"), "/geometry"),
    ("ring_not_closed", _set(LOT, [[0, 0], [50, 0], [50, 100], [0, 100], [0, 1]]), LOT),
    ("ring_degenerate", _set(LOT, [[0, 0], [50, 0], [0, 0], [50, 0], [0, 0]]), LOT),
    ("ring_not_simple", _set(LOT, [[0, 0], [50, 100], [50, 0], [0, 100], [0, 0]]), LOT),
    ("ring_not_simple", _set(LOT, [[0, 0], [50, 0], [25, 0], [0, 100], [0, 0]]), LOT),
    ("ring_not_simple", _set(LOT, [[0, 0], [10, 0], [20, 0], [0, 0]]), LOT),  # zero area
    ("schema_invalid", _set(LOT, [[0, 0], [float("nan"), 0], [50, 100], [0, 0]]), ""),  # NaN
    ("coordinate_out_of_range", _set(LOT, [[0, 0], [2e8, 0], [0, 100], [0, 0]]), f"{LOT}/1"),
    ("plate_outside_lot",
     _set(f"{PLATE0}/outline", [[[0, 0], [60, 0], [60, 50], [0, 50], [0, 0]]]),
     f"{PLATE0}/outline"),
    ("frontage_off_lot",
     _set("/geometry/streets/0/frontage_line", [[0, -5], [50, -5]]),
     "/geometry/streets/0/frontage_line/0"),
    ("plate_area_mismatch", _set(f"{PLATE0}/gross_sf", 2400), PLATE0),
    ("plates_rows_mismatch", _set("/floor_by_floor/0/gross_sf", 2400), "/geometry/floor_plates"),
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
    ("envelope_tier_inverted", _set(f"{TIER1}/top_ft", 45), TIER1),
    ("envelope_outside_lot",
     _set(f"{TIER1}/outline", [[[15, 15], [70, 15], [70, 100], [15, 100], [15, 15]]]),
     f"{TIER1}/outline"),
    ("coordinate_out_of_range", _set(f"{TIER1}/top_ft", 1e300), f"{TIER1}/top_ft"),
    ("ring_not_closed",
     _set(f"{TIER1}/outline/0", [[15, 15], [50, 15], [50, 100], [15, 100], [15, 16]]),
     f"{TIER1}/outline/0"),
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


def test_validation_is_the_shared_results_validator(monkeypatch):
    def refuse(document):
        raise StudyContractError("probe", contract="results", location="geometry/units")

    monkeypatch.setattr(adapter, "validate_results_document", refuse)
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(BASE)
    assert (caught.value.code, caught.value.location) == ("schema_invalid", "/geometry/units")


def test_fixture_only_key_is_refused():
    doc = _mutated(BASE, lambda d: d.__setitem__("_expected_failure", "probe"))
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(doc)
    assert caught.value.code == "schema_invalid"


CONTROL_CASES = [
    ("/geometry/streets/0/street", "Main\x0bStreet"),
    ("/geometry/yards", {"status": "not_available", "reason": "Yards \x00 not built.",
                         "reason_kind": "rule_not_implemented"}),
    ("/floor_by_floor/0/floor_label", "Floor\x1f1"),
    ("/geometry/yards/entries/0/reason", "Lone surrogate \ud800 here"),
    ("/street_width_case", {"marker": "Needs street width", "assumptions": [
        {"street": "Bad\x08Street", "assumed": "narrow", "street_width_fact_id": "f"}],
        "side_by_side_with": ["other"]}),
]


@pytest.mark.parametrize(("path", "value"), CONTROL_CASES, ids=[c[0] for c in CONTROL_CASES])
def test_text_xml_cannot_carry_fails_closed(path, value):
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(_mutated(BASE, _set(path, value)))
    assert caught.value.code == "invalid_text"
    assert caught.value.location.startswith(path)


def test_tab_and_newline_are_allowed_text():
    doc = _mutated(BASE, _set("/geometry/streets/0/street", "Main\tStreet"))
    assert load_drawing_input(doc).streets[0].name == "Main\tStreet"


def test_plate_drawn_smaller_than_its_area_fails_closed():
    """Review probe: floor 2 drawn 30 x 35 ft (1,050 sf) while gross_sf says 4,200."""
    doc = _mutated(MIXED, _set("/geometry/floor_plates/entries/3/outline",
                               [[[0, 0], [30, 0], [30, 35], [0, 35], [0, 0]]]))
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(doc)
    assert (caught.value.code, caught.value.location) == (
        "plate_area_mismatch", "/geometry/floor_plates/entries/3")


def test_plate_area_tolerates_whole_square_foot_rounding():
    doc = _mutated(MIXED, _set("/geometry/floor_plates/entries/3/gross_sf", 4200.9))
    doc["floor_by_floor"][3]["gross_sf"] = 4200.9
    doc["floor_by_floor"][3]["zoning_floor_area_sf"] = 4200.9
    assert isinstance(load_drawing_input(doc), DrawingInput)


def test_yard_drawn_shallower_than_its_depth_fails_closed():
    """Review probe: a yard outline 10 ft deep labeled 30 ft."""
    doc = _mutated(MIXED, _set("/geometry/yards/entries/0/outline",
                               [[[0, 90], [60, 90], [60, 100], [0, 100], [0, 90]]]))
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(doc)
    assert (caught.value.code, caught.value.location) == (
        "yard_depth_mismatch", "/geometry/yards/entries/0")


def test_yard_not_on_any_lot_line_fails_closed():
    doc = _mutated(MIXED, _set("/geometry/yards/entries/0/outline",
                               [[[10, 75], [50, 75], [50, 95], [10, 95], [10, 75]]]))
    doc["geometry"]["yards"]["entries"][0]["depth_ft"] = 20
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(doc)
    assert caught.value.code == "yard_depth_mismatch"


def test_yard_depth_is_measured_from_the_lot_line_it_runs_along():
    """A 50-ft rear yard on a 40-ft wide lot: its depth matches the rear line,
    not the (40-ft) reach from the side lines."""
    doc = load(CONTRACT_FIXTURES / "synthetic_envelope_not_available_existing_building.json")
    doc["geometry"]["yards"] = {"status": "available", "entries": [
        {"kind": "rear", "status": "required", "depth_ft": 50,
         "outline": [[[0, 50], [40, 50], [40, 100], [0, 100], [0, 50]]],
         "zr_sections": BASE["geometry"]["yards"]["entries"][0]["zr_sections"]}]}
    assert load_drawing_input(doc).yards[0].depth_ft == 50


def test_plate_through_a_lot_notch_fails_closed():
    """Review probe: a notch whose sides meet the plate only at vertices."""
    def mutate(doc):
        geometry = doc["geometry"]
        geometry["lot_outline"] = [[[0, 0], [10, 0], [10, 10], [6, 10], [6, 5], [5, 2], [4, 5],
                                    [4, 10], [0, 10], [0, 0]]]
        geometry["streets"] = [dict(geometry["streets"][0], frontage_line=[[0, 0], [10, 0]])]
        geometry["setback_lines_per_level"] = {"status": "not_available", "reason": "n/a",
                                               "reason_kind": "rule_not_implemented"}
        geometry["floor_plates"]["entries"] = [
            {"floor": 1, "outline": [[[0, 0], [10, 0], [10, 5], [8, 5], [0, 5], [0, 0]]],
             "gross_sf": 50, "use": "residential"}]
        doc["floor_by_floor"] = [dict(doc["floor_by_floor"][0], gross_sf=50,
                                      zoning_floor_area_sf=50)]
    with pytest.raises(DrawingInputError) as caught:
        load_drawing_input(_mutated(BASE, mutate))
    assert (caught.value.code, caught.value.location) == (
        "plate_outside_lot", "/geometry/floor_plates/entries/0/outline")


def test_floor_numbering_only_matters_when_floor_plates_are_drawn():
    doc = load(CONTRACT_FIXTURES / "synthetic_envelope_not_available_existing_building.json")
    doc["floor_by_floor"] = [dict(BASE["floor_by_floor"][0], floor=3)]  # a gap, no plates
    assert isinstance(load_drawing_input(doc), DrawingInput)
