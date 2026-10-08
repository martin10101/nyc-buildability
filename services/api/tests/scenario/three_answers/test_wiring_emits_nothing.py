"""Populating the carriers emits NOTHING: the results document is byte-for-byte unchanged (S13).

Task M5-T134 surfaces the property profile, the prepared tax-map outline and the site geometry onto
ThreeAnswerInputs as INERT carriers and hands them, through one new adapter, to the scenario
decision step. The engine reads NONE of them. This test proves that: the benchmark inputs are built
EXACTLY as tests/journey/test_215_16_northern_journey.py builds them, the three carriers are
populated, the real engine runs, and the emitted document equals the committed journey fixture
byte-for-byte (the SAME fixture the journey pins, read never written here). No new results fixture
is added. The red direction (an engine that read a carrier would move these bytes) is a mutation
proof outside the repository, recorded in the producer report.
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
from app.scenario.three_answers import generate_results
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
    return inputs


def test_s13_carriers_populated_emit_the_identical_document(monkeypatch):
    """S13: with the three carriers populated, generate_results emits the EXACT committed journey
    fixture, byte-for-byte. Populating the carriers changes nothing emitted; no new fixture."""
    inputs = _benchmark_inputs_with_carriers(monkeypatch)
    # the carriers are really populated (so the proof is non-vacuous)
    assert inputs.property_profile is not None
    assert inputs.prepared_outline is not None
    assert inputs.site_geometry is not None

    result = generate_results(inputs, env=_LANE_ON)
    document = result.document
    validate_results_document(document)
    assert document["contract_version"] == "1.2.0"  # scope + the R6B height note, as the journey

    serialized = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    assert _FIXTURE_PATH.exists(), f"no committed fixture {_FIXTURE_PATH.name}"
    # LF-normalize the checkout copy (a Windows autocrlf checkout smudges CRLF).
    assert serialized == _FIXTURE_PATH.read_bytes().replace(b"\r\n", b"\n")


def test_carriers_add_no_top_level_key_to_the_document(monkeypatch):
    """The carriers are INERT: the emitted document gains no key named after them (nothing leaks
    the profile, the outline or the geometry into the results document)."""
    inputs = _benchmark_inputs_with_carriers(monkeypatch)
    document = generate_results(inputs, env=_LANE_ON).document
    for leaked in ("property_profile", "prepared_outline", "site_geometry", "lot_outline"):
        assert leaked not in document, leaked
