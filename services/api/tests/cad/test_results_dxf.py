"""DXF from the results geometry (task E-03; plan section 3 step 7, section 5c
item 3; M1-22): layers from the style table, entity counts per layer, feet at
1:1, the measurement-status note exactly when not surveyed, the option label
read from the results, lot-only export, and fail-closed refusals.

AutoCAD itself is not available here: these tests prove the file's structure
with an independent group-code reader, not that AutoCAD opens it.
"""

from __future__ import annotations

from collections import Counter

import pytest

from app.cad import dxf_writer
from app.cad.results_dxf import (
    DrawingInputError,
    DrawingKitDisabled,
    Unavailable,
    level_layer,
    render_results_dxf,
)
from app.cad.results_dxf_notes import MEASUREMENT_NOTE_TEXT, ascii_text
from app.drawings.kit.scope import ASSUMPTION_KEY_NAMES, FLAG_WORDS
from app.drawings.kit.styles import STYLE_TABLE, style_for

from .results_dxf_support import (
    BASE,
    ENV_ON,
    KIT_FIXTURES,
    LOT_ONLY,
    NARROW,
    expected_counts,
    fixture_paths,
    load,
    mutated,
    open_ring,
    parse_dxf,
    render,
    set_at,
)

PATHS = fixture_paths()
IDS = [p.stem for p in PATHS]
SURVEY = {"rank": "survey_entered", "label": "Survey (entered)"}
NOT_A_SURVEY = "not a survey"


# --------------------------------------------------------------------------- #
# Layers and entity counts.
# --------------------------------------------------------------------------- #

def test_the_main_fixture_has_the_expected_layers_and_counts():
    result = render(BASE)
    parsed = parse_dxf(result.text)
    assert result.layers == ("C-PROP-LINE", "A-ZONE-STBK-LINE-F05", "A-ZONE-ENVL",
                             "A-MASS-RESI", "A-ANNO-NOTE")
    assert parsed.counts() == {
        "C-PROP-LINE": Counter(POLYLINE=1),  # one lot ring
        "A-ZONE-STBK-LINE-F05": Counter(LINE=2),  # floor 5: two two-point lines
        "A-ZONE-ENVL": Counter(POLYLINE=4, LINE=8),  # 2 tiers x (bottom + top, 4 verticals)
        "A-MASS-RESI": Counter(POLYLINE=4),  # floors 1-4, residential
        "A-ANNO-NOTE": Counter(TEXT=6),
    }


@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_entity_counts_per_layer_follow_the_results(path):
    doc = load(path)
    result = render(doc)
    parsed = parse_dxf(result.text)
    assert parsed.counts() == expected_counts(doc, len(result.notes))
    # The LAYER table lists exactly the layers drawn on, in drawing order.
    assert [name for name, _ in parsed.layers] == list(result.layers)
    assert set(result.layers) == set(parsed.counts())


@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_layer_names_and_colors_come_from_the_style_table(path):
    parsed = parse_dxf(render(load(path)).text)
    by_layer = {s.cad_layer: s for s in STYLE_TABLE}
    for name, color in parsed.layers:
        base = name if name in by_layer else name.rsplit("-", 1)[0]
        style = by_layer[base]
        assert color == style.cad_color
        if base != name:  # only setback lines have one layer per level
            assert style.kind == "setback_line"


def test_lot_and_envelope_are_on_separate_layers():
    parsed = parse_dxf(render(BASE).text)
    lot = parsed.on(style_for("lot_line").cad_layer)
    envelope = parsed.on(style_for("envelope").cad_layer)
    assert lot and envelope
    assert style_for("lot_line").cad_layer != style_for("envelope").cad_layer


def test_setback_lines_get_one_layer_per_level():
    doc = mutated(BASE, lambda d: d["geometry"]["setback_lines_per_level"]["entries"].append(
        {"floor": 3, "lines": [[[20, 20], [20, 20], [40, 20]]], "zr_sections": ["ZR 23-433"]}))
    parsed = parse_dxf(render(doc).text)
    assert len(parsed.on("A-ZONE-STBK-LINE-F05", "LINE")) == 2
    # the repeated point draws nothing; the one real segment is on floor 3's layer
    assert [e.points for e in parsed.on("A-ZONE-STBK-LINE-F03")] == [
        [(20.0, 20.0, 0.0), (40.0, 20.0, 0.0)]]


def test_level_layer_names():
    assert level_layer(5) == "A-ZONE-STBK-LINE-F05"
    assert level_layer(12) == "A-ZONE-STBK-LINE-F12"
    assert level_layer(120) == "A-ZONE-STBK-LINE-F120"
    assert level_layer(0) == "A-ZONE-STBK-LINE-C01"  # the results' first cellar level
    assert level_layer(-1) == "A-ZONE-STBK-LINE-C02"


# --------------------------------------------------------------------------- #
# Units: feet at 1:1, the same header as the existing writer.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_feet_at_one_to_one(path):
    doc = load(path)
    parsed = parse_dxf(render(doc).text)
    assert parsed.header["$ACADVER"] == [(1, dxf_writer.DXF_VERSION_R12)]
    assert parsed.header["$INSUNITS"] == [(70, str(dxf_writer.INSUNITS_US_SURVEY_FEET))]
    assert dxf_writer.INSUNITS_US_SURVEY_FEET == 21  # US survey feet, as the old writer
    lot = parsed.on("C-PROP-LINE", "POLYLINE")
    rings = doc["geometry"]["lot_outline"]
    # every vertex is the results' coordinate, unscaled and untranslated, at grade
    assert [[(x, y) for x, y, _ in e.points] for e in lot] == [open_ring(r) for r in rings]
    assert all(e.closed and {z for *_, z in e.points} == {0.0} for e in lot)


def test_envelope_tiers_stand_at_their_heights():
    parsed = parse_dxf(render(BASE).text)
    tiers = BASE["geometry"]["envelope"]["tiers"]
    rings = parsed.on("A-ZONE-ENVL", "POLYLINE")
    expected = []
    for tier in tiers:
        for z in (tier["bottom_ft"], tier["top_ft"]):
            expected += [[(x, y, float(z)) for x, y in open_ring(r)] for r in tier["outline"]]
    assert [e.points for e in rings] == expected
    verticals = parsed.on("A-ZONE-ENVL", "LINE")
    assert [(e.points[0][2], e.points[1][2]) for e in verticals] == [(0.0, 45.0)] * 4 + [
        (45.0, 55.0)] * 4


def test_floor_plates_stack_by_the_floor_to_floor_heights():
    parsed = parse_dxf(render(BASE).text)
    elevations = [e.points[0][2] for e in parsed.on("A-MASS-RESI")]
    heights = [row["height_ft"] for row in BASE["floor_by_floor"]]  # floors 1-4: 12, 10, 10, 10
    assert elevations == [0.0, float(heights[0]), float(sum(heights[:2])),
                          float(sum(heights[:3]))]


def test_cellar_plates_stack_below_grade():
    doc = load(KIT_FIXTURES / "synthetic_interior_lot_mixed_use.json")  # cellar, split floor 1
    parsed = parse_dxf(render(doc).text)
    cellar = parsed.on("A-MASS-CELR")
    rows = {r["floor"]: r["height_ft"] for r in doc["floor_by_floor"]}
    assert [e.points[0][2] for e in cellar] == [-float(rows[0])]
    assert [e.points[0][2] for e in parsed.on("A-MASS-COMM")] == [0.0]


def test_epsg_2263_coordinates_are_kept_as_given():
    doc = load(KIT_FIXTURES / "synthetic_irregular_corner_lot_2263.json")
    assert doc["geometry"]["crs"] == "EPSG:2263"
    result = render(doc)
    lot = parse_dxf(result.text).on("C-PROP-LINE")[0]
    assert [(x, y) for x, y, _ in lot.points] == open_ring(doc["geometry"]["lot_outline"][0])
    assert any("EPSG:2263" in n.text and "US survey feet" in n.text for n in result.notes)


# --------------------------------------------------------------------------- #
# The measurement-status note: present exactly when not surveyed.
# --------------------------------------------------------------------------- #

def _surveyed(doc: dict) -> dict:
    def mutate(d):
        d["geometry"]["measurement"] = dict(SURVEY)
        for answer in d["answers"].values():
            if answer["status"] == "available":
                answer["measurement"] = dict(SURVEY)
    return mutated(doc, mutate)


def _texts(result) -> list[str]:
    return [e.text for e in parse_dxf(result.text).entities if e.kind == "TEXT"]


@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_the_note_is_on_the_drawing_when_not_surveyed(path):
    result = render(load(path))  # every fixture is measured from the city tax map
    texts = _texts(result)
    assert any(t.startswith("Approximate - city tax map, not a survey (lot outline")
               for t in texts)
    notes = [n for n in result.notes if n.role == "measurement_note"]
    assert notes and all(n.text in texts for n in notes)
    assert all(n.layer == "A-ANNO-NOTE" for n in parse_dxf(result.text).entities
               if n.kind == "TEXT")


@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_no_note_when_everything_drawn_is_surveyed(path):
    result = render(_surveyed(load(path)))
    assert not any(NOT_A_SURVEY in t for t in _texts(result))
    assert not [n for n in result.notes if n.role == "measurement_note"]


def test_the_note_names_each_label_and_what_it_applies_to():
    # Lot surveyed; the envelope and floor plates rest on an assumed street width.
    doc = mutated(NARROW, set_at("/geometry/measurement", dict(SURVEY)))
    notes = [n for n in render(doc).notes if n.role == "measurement_note"]
    assert [n.text for n in notes] == [
        "Assumed, not a survey (setback lines, envelope, floor plates)"]
    assert notes[0].sources == ("/answers/permitted_envelope/measurement/rank",
                                "/answers/building_option/measurement/rank")
    both = [n.text for n in render(NARROW).notes if n.role == "measurement_note"]
    assert both == ["Approximate - city tax map, not a survey (lot outline)",
                    "Assumed, not a survey (setback lines, envelope, floor plates)"]


@pytest.mark.parametrize(("rank", "label"), [
    ("city_records", "City records"), ("entered", "Entered"), ("assumed", "Assumed")])
def test_each_rank_that_is_not_a_survey_has_its_note(rank, label):
    doc = mutated(LOT_ONLY, set_at("/geometry/measurement", {"rank": rank, "label": label}))
    notes = [n.text for n in render(doc).notes if n.role == "measurement_note"]
    assert notes == [f"{label}, not a survey (lot outline)"]
    assert MEASUREMENT_NOTE_TEXT[rank] == f"{label}, not a survey"


def test_a_drawn_part_without_an_answer_label_is_not_taken_as_surveyed():
    doc = _surveyed(BASE)
    doc["answers"]["permitted_envelope"] = {
        "status": "not_available", "reason": "Envelope not available - rules not reviewed.",
        "reason_kind": "rule_not_reviewed"}
    notes = [n for n in render(doc).notes if n.role == "measurement_note"]
    assert [n.text for n in notes] == [
        "Measurement status not stated in the results, not known to be a survey "
        "(setback lines, envelope)"]
    assert notes[0].sources == ("/answers/permitted_envelope/status",)


def test_the_plan_example_wording_for_the_tax_map():
    assert MEASUREMENT_NOTE_TEXT["approximate_tax_map"] == (
        "Approximate \u2014 city tax map, not a survey")  # plan section 3 step 7
    assert ascii_text(MEASUREMENT_NOTE_TEXT["approximate_tax_map"], "") == (
        "Approximate - city tax map, not a survey")


# --------------------------------------------------------------------------- #
# The option label and every other note are read from the results.
# --------------------------------------------------------------------------- #

def test_the_option_label_is_read_from_the_results():
    doc = mutated(BASE, set_at("/option_id", "opt-zz"), set_at("/revision", 9))
    result = render(doc)
    texts = _texts(result)
    assert texts[0] == "Option opt-zz - revision 9"
    assert "Option opt-a - revision 3" in _texts(render(BASE))
    assert not any("GENERATED BUILDING OPTION" in t.upper() for t in texts)


def _resolve(doc, pointer):
    node = doc
    for part in pointer.strip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def _scope_token(source, value):
    """The fixed plain word a scope note prints for an assumption key or boolean
    flag source (the kit's presentation vocabulary), or None for a plain figure
    or string read straight from the results (D-090-R108)."""
    if "/scope/assumptions/" in source and source.endswith("/key"):
        return ASSUMPTION_KEY_NAMES[value]
    if "/scope/assumptions/" in source and source.endswith("/value") and isinstance(value, bool):
        return FLAG_WORDS[value]
    return None


@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_every_note_value_is_read_from_the_results(path):
    doc = load(path)
    result = render(doc)
    for note in result.notes:
        for source in note.sources:
            if source == "units":
                continue
            value = _resolve(doc, source)
            token = _scope_token(source, value)
            if token is not None:  # a key/flag: its word maps to the document value
                assert token in note.text, (source, note.text)
                continue
            if note.role == "measurement_note":
                assert value == "not_available" or value in MEASUREMENT_NOTE_TEXT
                continue
            if source == "/geometry/crs":  # a closed table: one wording per CRS
                wording = {"EPSG:2263": "Coordinates: EPSG:2263 NAD83 New York Long Island",
                           "local_feet": "Coordinates: local plane in feet"}[value]
                assert note.text.startswith(wording)
                continue
            assert ascii_text(str(value), source) in note.text, (source, note.text)
    # Check C-4: no note prints a number that is not a results value; only the
    # fixed coordinates and units statements carry digits of their own.
    for note in result.notes:
        rest = note.text
        tokens = []
        for source in note.sources:
            if source.startswith("/") and note.role not in ("measurement_note", "crs"):
                value = _resolve(doc, source)
                token = _scope_token(source, value)
                tokens.append(token if token is not None else ascii_text(str(value), source))
        for token in sorted(tokens, key=len, reverse=True):  # a longer value first, so a
            rest = rest.replace(token, "")                   # short word inside it is not lost
        if note.role not in ("crs", "units"):
            assert not any(ch.isdigit() for ch in rest), note.text


def test_street_width_case_is_named():
    texts = _texts(render(NARROW))
    assert "Needs street width" in texts
    assert "Synthetic Street B width assumed narrow" in texts


# --------------------------------------------------------------------------- #
# Lot-only export.
# --------------------------------------------------------------------------- #

def test_lot_only_export_is_allowed():
    result = render(LOT_ONLY)
    assert result.layers == ("C-PROP-LINE", "A-ANNO-NOTE")
    parsed = parse_dxf(result.text)
    assert parsed.counts()["C-PROP-LINE"] == Counter(POLYLINE=1)
    texts = _texts(result)
    geometry = LOT_ONLY["geometry"]
    for layer in ("yards", "setback_lines_per_level", "envelope", "floor_plates"):
        assert ascii_text(geometry[layer]["reason"], "") in texts
    assert "Out of date: " + LOT_ONLY["out_of_date_reason"] in texts


def test_lot_only_when_just_the_envelope_is_missing():
    doc = mutated(BASE, set_at("/geometry/envelope", {
        "status": "not_available", "reason_kind": "rule_not_implemented",
        "reason": "Envelope not available \u2014 height rules for this district are "
                  "not built yet."}))
    result = render(doc)
    assert "A-ZONE-ENVL" not in result.layers and "C-PROP-LINE" in result.layers
    assert ("Envelope not available - height rules for this district are not built yet."
            in _texts(result))


def test_no_geometry_at_all_is_unavailable_with_the_results_reason():
    reason = "Lot outline not available - no tax lot found."
    doc = mutated(BASE, set_at("/geometry", {
        "status": "not_available", "reason": reason, "reason_kind": "missing_input"}))
    assert render_results_dxf(doc, env=ENV_ON) == Unavailable(
        "dxf", reason, "missing_input", "/geometry/reason")


# --------------------------------------------------------------------------- #
# Fail closed.
# --------------------------------------------------------------------------- #

LOT = "/geometry/lot_outline/0"
TIER1 = "/geometry/envelope/tiers/1"
INVALID = [
    ("schema_invalid", lambda d: d.pop("option_id")),
    ("ring_not_closed", set_at(LOT, [[0, 0], [50, 0], [50, 100], [0, 100], [0, 1]])),
    ("ring_not_simple", set_at(LOT, [[0, 0], [50, 100], [50, 0], [0, 100], [0, 0]])),
    ("plate_outside_lot", set_at("/geometry/floor_plates/entries/0/outline",
                                 [[[0, 0], [60, 0], [60, 50], [0, 50], [0, 0]]])),
    ("envelope_outside_lot", set_at(f"{TIER1}/outline",
                                    [[[15, 15], [70, 15], [70, 100], [15, 100], [15, 15]]])),
    ("envelope_tier_inverted", set_at(f"{TIER1}/top_ft", 40)),
    ("coordinate_out_of_range", set_at(f"{TIER1}/top_ft", 1e300)),
    ("setback_line_outside_lot", set_at(
        "/geometry/setback_lines_per_level/entries/0/lines/0", [[15, 15], [70, 15]])),
    ("text_not_representable", set_at("/option_id", "opt-\u00e9")),
    ("text_control_code", set_at("/option_id", "opt-%%d")),
    ("text_control_code", set_at("/results_id", "res\\U+2014")),
]


@pytest.mark.parametrize(("code", "mutate"), INVALID,
                         ids=[f"{c}-{i}" for i, (c, _) in enumerate(INVALID)])
def test_invalid_results_fail_closed(code, mutate):
    with pytest.raises(DrawingInputError) as caught:
        render_results_dxf(mutated(BASE, mutate), env=ENV_ON)
    assert caught.value.code == code


def test_writer_refusals_surface_as_one_typed_error(monkeypatch):
    monkeypatch.setattr(dxf_writer, "MAX_ENTITIES", 5)
    with pytest.raises(DrawingInputError) as caught:
        render_results_dxf(BASE, env=ENV_ON)
    assert caught.value.code == "entity_cap_exceeded"
    assert isinstance(caught.value.__cause__, dxf_writer.DxfValidationError)


def test_off_unless_the_lane_flag_is_on(monkeypatch):
    monkeypatch.delenv("LANE_E_ENABLED", raising=False)
    for env in (None, {}, {"LANE_E_ENABLED": "0"}, {"LANE_D_ENABLED": "1"}):
        with pytest.raises(DrawingKitDisabled):
            render_results_dxf(BASE, env=env)


def test_the_results_path_leaves_the_old_writer_alone():
    # additive only: the caller-ring writer keeps its fixed layers and labels
    assert [name for name, _ in dxf_writer.LAYER_DEFINITIONS] == [
        "LOT", "BUILDING_OUTLINE", "MASSING_3D", "ANNOTATION"]
    assert dxf_writer.GENERATOR_NOTE.startswith("GENERATED BUILDING OPTION")
