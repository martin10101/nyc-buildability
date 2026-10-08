"""The adapter emits the three-way document that equals the committed journey fixture (S12).

Task M5-T136 makes the adapter run the engine and then the pure three-way transform over the
engine's document and the decision ways, emitting the contract-1.3.0 three-way document. This file
(whose name is now a misnomer: the adapter DOES emit, as of M5-T136) proves the emit path on the
benchmark lot: the benchmark inputs are built EXACTLY as the recorded 215-16 Northern journey test
builds them, the three carriers are populated, the adapter runs, and the emitted document equals
the committed journey fixture byte-for-byte (the SAME fixture the journey pins, read not written).

This is an UNCHANGED/WIRING proof only (work order rule 3): equality with the saved fixture proves
the parts are connected and the bytes carried, NOT that any value is correct - the correctness of
each way comes from the reference cases, checked in test_three_answers_three_way_emit.py. The engine
itself is unchanged: engine.py never names the decision module and its own inner document still
declares the pre-three-way version.
"""

from __future__ import annotations

import http.client
import json
import socket
from pathlib import Path

import pytest

from app.contracts.evaluator_inputs import build_evaluator_inputs, build_three_answer_inputs
from app.contracts.study_contracts import validate_results_document
from app.contracts.study_setup_bridge import study_from_study_setup
from app.profile.builder import build_property_profile
from app.scenario.three_answers.result_way_engine_bridge import run_engine_and_result_ways
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.outline import prepare_outline
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.contracts.test_evaluator_inputs import _benchmark_identity_address
from tests.contracts.test_study_setup_bridge import _LANE_ON, _OPTION_ID, _REVISION, _northern_setup
from tests.spatial._northern_replay import (
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

# The journey's own identifiers, so the serialized document matches the committed fixture.
_STUDY_ID = "study-215-16-northern-journey"
_RESULTS_ID = "res-215-16-northern-journey"
_COMPUTED_AT = "2026-10-03T00:00:00Z"

_REPO_ROOT = Path(__file__).resolve().parents[5]
_FIXTURE_PATH = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
    / "recorded_215_16_northern_journey.json"
)


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    def _blocked(*_args, **_kwargs):
        raise AssertionError("network I/O attempted in a recorded-data test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def _carriers():
    """The recorded benchmark lot's profile, prepared outline and site geometry (offline)."""
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    profile = build_property_profile(replay_pluto())
    return profile, prepared, geometry


def _benchmark_inputs_with_carriers(monkeypatch):
    profile, prepared, geometry = _carriers()
    setup = _northern_setup(monkeypatch, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id=_STUDY_ID, revision=_REVISION
    )
    doc = build_evaluator_inputs(study, _OPTION_ID)
    inputs = build_three_answer_inputs(
        doc, results_id=_RESULTS_ID, computed_at=_COMPUTED_AT,
        housing_program="standard_residence", overlay_present=True,
        special_district_present=False, within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0, special_density_area=False, study=study,
        property_profile=profile, prepared_outline=prepared, site_geometry=geometry,
    )
    return inputs, doc


def test_s12_adapter_emits_the_committed_three_way_fixture(monkeypatch):
    """S12: with the carriers populated, the adapter emits the EXACT committed journey fixture,
    byte-for-byte, at contract 1.3.0. This is a wiring/unchanged proof, never evidence a value is
    correct (work order rule 3)."""
    inputs, doc = _benchmark_inputs_with_carriers(monkeypatch)
    assert inputs.property_profile is not None
    assert inputs.prepared_outline is not None
    assert inputs.site_geometry is not None

    emitted = run_engine_and_result_ways(
        inputs, evaluator_inputs=doc, special_density_statement=False, env=_LANE_ON
    )
    document = emitted.document
    validate_results_document(document)
    assert document["contract_version"] == "1.3.0"  # the three-way document (M5-T136)

    serialized = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    assert _FIXTURE_PATH.exists(), f"no committed fixture {_FIXTURE_PATH.name}"
    # LF-normalize the checkout copy (a Windows autocrlf checkout smudges CRLF).
    assert serialized == _FIXTURE_PATH.read_bytes().replace(b"\r\n", b"\n")


def test_engine_inner_document_is_unchanged(monkeypatch):
    """engine.py is read-only: the engine's own ThreeAnswersResult still assembles its unchanged
    document (declaring the pre-three-way 1.2.0 version on this lot - scope + the height note); only
    the adapter's transform emits 1.3.0."""
    inputs, doc = _benchmark_inputs_with_carriers(monkeypatch)
    emitted = run_engine_and_result_ways(
        inputs, evaluator_inputs=doc, special_density_statement=False, env=_LANE_ON
    )
    assert emitted.engine_result.document["contract_version"] == "1.2.0"
    # The engine's inner block still carries the legal unit figure; only the EMITTED document
    # reserves it (reading O28). Nothing but the adapter reads the engine's inner document.
    assert emitted.engine_result.document["unit_estimate"]["status"] == "available"
    assert emitted.document["unit_estimate"]["status"] == "not_available"


def test_emitted_document_leaks_no_carrier_key(monkeypatch):
    """The carriers are INERT in the engine and never leak into the emitted document (no top-level
    key named after the profile, the outline or the geometry)."""
    inputs, doc = _benchmark_inputs_with_carriers(monkeypatch)
    document = run_engine_and_result_ways(
        inputs, evaluator_inputs=doc, special_density_statement=False, env=_LANE_ON
    ).document
    for leaked in ("property_profile", "prepared_outline", "site_geometry", "lot_outline"):
        assert leaked not in document, leaked
