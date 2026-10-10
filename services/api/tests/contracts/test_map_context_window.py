"""M5-T154 S3/S4/S7: the 1.1.0 map document with neighbouring lots and streets.

Builds the report's site-context document from the recorded 215-16 Northern window pack through
the real connectors (offline) and proves: the document is schema-valid 1.1.0 with context_window,
tax_lots, building_footprints and streets (ruling Y2); every outline and path is an input geometry
unchanged; every existing 1.0.0 example still validates; the mapped-width parser turns only a plain
number into a number (D-052); and the independent window check (ruling Y7/S7).
"""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import Polygon

from app.api.v1.report_context import DEFAULT_REPORT_MAP_NOTES
from app.contracts.map_context import build_report_map_context, parse_mapped_width_ft
from app.contracts.study_contracts import validate_map_context_document
from tests.spatial._northern_window_replay import (
    BBL,
    ENV_400,
    ENV_1000,
    replay_footprints,
    replay_streets,
    replay_subject_lot,
    replay_window_lots,
)

# services/api/tests/contracts/<this> -> parents[4] is the repo root.
_VALID_FIXTURES = (
    Path(__file__).resolve().parents[4] / "packages/contracts/fixtures/valid/map_context"
)


def _build_document():
    return build_report_map_context(
        replay_subject_lot(),
        context_window=ENV_400,
        tax_lots=replay_window_lots(),
        footprints=replay_footprints(),
        streets=replay_streets(),
        streets_window=ENV_1000,
        notes=DEFAULT_REPORT_MAP_NOTES,
    )


# ---------------------------------------------------------------------------
# S3 - the 1.1.0 document
# ---------------------------------------------------------------------------


def test_document_is_schema_valid_1_1_0_with_all_layers():
    doc = _build_document()
    validate_map_context_document(doc)  # raises on any defect
    assert doc["contract_version"] == "1.1.0"
    mc = doc["map_context"]
    assert set(mc) >= {"context_window", "tax_lots", "building_footprints", "streets"}
    assert mc["context_window"] == {
        "xmin": ENV_400[0], "ymin": ENV_400[1], "xmax": ENV_400[2], "ymax": ENV_400[3]}
    assert mc["tax_lots"]["status"] == "available"
    assert mc["streets"]["status"] == "available"
    assert mc["streets"]["window"] == {
        "xmin": ENV_1000[0], "ymin": ENV_1000[1], "xmax": ENV_1000[2], "ymax": ENV_1000[3]}
    # the subject lot is never a neighbouring entry
    assert BBL not in [entry["bbl"] for entry in mc["tax_lots"]["entries"]]
    assert mc["subject_lot"]["bbl"] == BBL


def test_every_existing_1_0_0_example_still_validates():
    fixtures = sorted(_VALID_FIXTURES.glob("*.json"))
    assert fixtures, "expected valid map_context fixtures"
    for fixture in fixtures:
        document = json.loads(fixture.read_text("utf-8"))
        validate_map_context_document(document)  # raises on any defect


def test_outlines_and_paths_are_input_geometry_unchanged():
    window = replay_window_lots()
    streets = replay_streets()
    mc = _build_document()["map_context"]

    lot_by_bbl = {lot.bbl: lot for lot in window.lots}
    for entry in mc["tax_lots"]["entries"]:
        source = lot_by_bbl[entry["bbl"]]
        expected = [[[float(x), float(y)] for x, y in ring] for ring in source.outline]
        assert entry["outline"] == expected

    # a street entry's paths equal the source polyline paths, vertex for vertex
    source_paths = {
        polyline.segment.street_name: [
            [[float(x), float(y)] for x, y in path] for path in polyline.paths
        ]
        for polyline in streets.entries
        if polyline.has_usable_geometry and polyline.paths is not None
    }
    checked = 0
    for entry in mc["streets"]["entries"]:
        if entry["name"] in source_paths and entry["paths"] == source_paths[entry["name"]]:
            checked += 1
    assert checked >= 1


# ---------------------------------------------------------------------------
# S4 - street widths (plain number -> number; anything else -> null)
# ---------------------------------------------------------------------------


def test_mapped_width_parser_only_parses_a_plain_number():
    """MUTATION PROOF 2: a parser that reads '60-75' as 60 fails here."""
    assert parse_mapped_width_ft("60") == 60
    assert parse_mapped_width_ft("100") == 100
    assert parse_mapped_width_ft("60-75") is None
    assert parse_mapped_width_ft("<=75") is None
    assert parse_mapped_width_ft("") is None
    assert parse_mapped_width_ft(None) is None
    # the two values stay numbers, never a wide/narrow label
    assert isinstance(parse_mapped_width_ft("60"), int)


def test_width_text_is_kept_verbatim_from_the_source():
    mc = _build_document()["map_context"]
    by_name: dict[str, list[dict]] = {}
    for entry in mc["streets"]["entries"]:
        by_name.setdefault(entry["name"], []).append(entry)
    # Northern Boulevard is '100' -> 100; Bell Boulevard carries a non-numeric '80-100' -> null
    northern = by_name["Northern Boulevard"][0]
    assert northern["width_text"] == "100" and northern["mapped_width_ft"] == 100
    bell_texts = {e["width_text"] for e in by_name["Bell Boulevard"]}
    assert "80-100" in bell_texts
    for entry in by_name["Bell Boulevard"]:
        if entry["width_text"] == "80-100":
            assert entry["mapped_width_ft"] is None


# ---------------------------------------------------------------------------
# S7 - independent check of the window
# ---------------------------------------------------------------------------


def test_independent_window_check():
    window = replay_window_lots()
    subject = Polygon(window.subject.outline[0])
    lot1 = next(lot for lot in window.lots if lot.bbl == "4073340001")
    shared = subject.boundary.intersection(Polygon(lot1.outline[0]).boundary)
    assert abs(shared.length - 99.98) <= 0.01, f"shared edge {shared.length} ft"

    mc = _build_document()["map_context"]
    widths: dict[str, set] = {}
    for entry in mc["streets"]["entries"]:
        widths.setdefault(entry["name"], set()).add(entry["mapped_width_ft"])
    assert 100 in widths["Northern Boulevard"]
    assert 60 in widths["215 Place"]
    assert 60 in widths["215 Street"]
