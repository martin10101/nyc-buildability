"""Recorded 215-16 Northern map_context fixture: byte-drift, schema, adapter and
labels (maps step 4, D-090-R124).

The committed fixture ``fixtures/recorded_215_16_northern.json`` is built OFFLINE
from the recorded Northern pack through the real builder (no network). These
tests prove the committed JSON has not drifted from a fresh rebuild, that it is
schema-valid AND adapter-loadable, and that the rendered maps label the recorded
``ZONEDIST`` symbols and the subject BBL - both read from the fixture, never a
re-typed literal - with no raster/external imagery. The SVG snapshots themselves
are covered by the globbing snapshot suite in ``test_snapshots.py`` (its
``fixtures/*.json`` glob picks this fixture up automatically).
"""

from __future__ import annotations

from app.contracts.study_contracts import validate_map_context_document
from app.drawings.maps import Drawing, render_location_map, render_zoning_map
from app.drawings.maps.adapter import load_map_context

from .maps_support import ENV_ON, load, parse, pieces
from .northern_fixture import FIXTURE, build_document, serialize


def _texts_by_role(svg: str, role: str) -> list[str]:
    return [text for _source, text, piece_role in pieces(parse(svg)) if piece_role == role]


def test_committed_fixture_has_not_drifted() -> None:
    """Rebuilding from the replay helpers and serializing the same way equals the
    committed file byte for byte (LF-normalized for a Windows autocrlf checkout)."""
    rebuilt = serialize(build_document()).encode("utf-8")
    committed = FIXTURE.read_bytes().replace(b"\r\n", b"\n")
    assert rebuilt == committed


def test_fixture_is_schema_valid_and_adapter_loadable() -> None:
    document = load(FIXTURE)
    validate_map_context_document(document)  # raises on any defect
    context = load_map_context(document)
    assert context.crs == "EPSG:2263"
    assert context.measurement_label == "Approximate — tax map"


def test_zoning_labels_are_the_recorded_zonedist_symbols() -> None:
    document = load(FIXTURE)
    result = render_zoning_map(document, env=ENV_ON)
    assert isinstance(result, Drawing)
    drawn = sorted(_texts_by_role(result.svg, "zoning_district"))
    expected = sorted(
        entry["zonedist"] for entry in document["map_context"]["zoning_districts"]["entries"]
    )
    assert expected  # at least one district is drawn
    assert drawn == expected


def test_subject_lot_is_labelled_by_its_recorded_bbl() -> None:
    document = load(FIXTURE)
    bbl = document["map_context"]["subject_lot"]["bbl"]
    result = render_location_map(document, env=ENV_ON)
    assert isinstance(result, Drawing)
    labels = _texts_by_role(result.svg, "subject_lot")
    assert len(labels) == 1
    assert labels[0].endswith(bbl)


def test_no_raster_base_map_imagery() -> None:
    document = load(FIXTURE)
    for render in (render_location_map, render_zoning_map):
        result = render(document, env=ENV_ON)
        assert isinstance(result, Drawing)
        assert "<image" not in result.svg
        assert "href=" not in result.svg  # no linked tiles / external raster
