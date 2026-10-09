"""B-05 existing-floor-area evidence threaded into the study read (journey wave 1
item 3, lane C).

Offline and deterministic. The route is driven through its INJECTED study-inputs
provider, now carrying an INJECTED existing-floor-area provider that serves the
recorded 215-16 Northern benchmark evidence (the SAME offline pack the B-05 benchmark
test uses, ``tests/profile/test_existing_floor_area_benchmark``). No network is touched.

Expected values come from the B-05 result object
(``app.profile.existing_floor_area.resolve_existing_zoning_floor_area``), never a
restated floor-area literal:

- with evidence, the study read's ``existing_zoning_floor_area`` fact equals what B-05
  resolves for the SAME profile + evidence -- for the recorded Northern lot that is an
  honest UNKNOWN, because the one completed DOB figure (39,934 sq ft) may cover the whole
  zoning lot (job 421803891 maps tax lots 1 & 70 to one zoning lot), so it is set aside
  with its source and the zoning-lot citation attached, never fabricated into a value;
- with NO evidence provider, threading is a no-op (the facts are byte-identical to the
  pre-wiring study read) -- so every existing study-read test still passes;
- malformed evidence (a recorded row B-05's readers refuse, or a provider value that is
  not an ``ExistingFloorAreaEvidence``) is the route's fail-safe unavailability (a typed
  ``503``), never a generic ``500`` and never a fabricated figure;
- the full study document with the threaded fact still passes the study contract.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.v1.study_inputs import (
    ExistingFloorAreaProvider,
    assemble_study_inputs,
    pluto_study_inputs_provider,
)
from app.api.v1.study_read import get_rate_limiter, get_study_inputs_provider
from app.config import INTERNAL_STUDY_READ_ENABLED_ENV_VAR
from app.contracts.study_contracts import validate_study_document
from app.main import create_app
from app.profile.existing_floor_area import (
    ExistingFloorAreaEvidence,
    resolve_existing_zoning_floor_area,
)
from tests.api.test_study_read_api import (
    _TEST_ONLY_OPTION,
    FIXED_CLOCK,
    LANE_B_ON,
    NORTHERN_BBL,
    _northern_fetcher,
    _northern_provider,
)
from tests.profile.test_existing_floor_area_benchmark import (
    DOB_ZONING_FLOOR_AREA,
    EVIDENCE,
    PLUTO_FILE,
    record_set,
)

# The benchmark PLUTO row records numbldgs = 1 (one building on the lot); this is the
# building count ``build_site_facts`` passes through to B-05 for this pack. The
# assembled-fact == resolved-fact assertion in test (1) locks this in: if the recorded
# count were anything else, that assertion would fail loudly rather than silently pass.
NORTHERN_RECORDED_BUILDING_COUNT = 1


def _evidence_provider(evidence: ExistingFloorAreaEvidence | None) -> ExistingFloorAreaProvider:
    def provide(canonical_bbl: str, correlation_id: str) -> ExistingFloorAreaEvidence | None:
        return evidence

    return provide


def _malformed_evidence_provider(canonical_bbl: str, correlation_id: str):
    # B-05's own reader refuses PLUTO as a DOB dataset, so building the evidence from the
    # recorded PLUTO response raises a ValueError before the provider can return. The
    # seam must surface that as the fail-safe 503, never a 500.
    return ExistingFloorAreaEvidence(dob_job_filings=(record_set(PLUTO_FILE),))


def _bad_type_evidence_provider(canonical_bbl: str, correlation_id: str):
    # A provider that returns a value that is not an ExistingFloorAreaEvidence: the seam
    # fails closed to the 503, never passes a malformed object into assembly.
    return {"not": "evidence"}


def _provider(existing_floor_area_provider: ExistingFloorAreaProvider | None = None):
    return pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON,
        existing_floor_area_provider=existing_floor_area_provider,
    )


def _client(provider) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_study_inputs_provider] = lambda: provider
    return TestClient(app)


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, "1")


def _facts_by_key(body) -> dict:
    return {fact["key"]: fact for fact in body["site"]["facts"]}


def _one(facts, key: str) -> dict:
    (fact,) = [fact for fact in facts if fact["key"] == key]
    return fact


_URL = f"/api/v1/properties/{NORTHERN_BBL}/study"


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


# ---------------------------------------------------------------------------
# (1) Evidence present -> the fact equals B-05's resolution for the same evidence.
# ---------------------------------------------------------------------------
def test_existing_floor_area_fact_equals_b05_resolution(monkeypatch) -> None:
    _enable(monkeypatch)

    # The route's inputs come from assemble_study_inputs; its existing fact IS B-05's
    # ExistingFloorAreaResult for the same recorded profile + evidence.
    inputs = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON,
        existing_floor_area=EVIDENCE,
    )
    assembled_fact = _one(inputs.site_facts, "existing_zoning_floor_area")

    # ... and that fact is exactly what resolve_existing_zoning_floor_area returns for the
    # pack (compared against the B-05 result object, never a restated floor-area literal).
    resolved = resolve_existing_zoning_floor_area(
        NORTHERN_BBL, EVIDENCE, recorded_building_count=NORTHERN_RECORDED_BUILDING_COUNT
    )
    assert assembled_fact == resolved.fact

    # The route serves exactly that fact.
    body = _client(_provider(_evidence_provider(EVIDENCE))).get(_URL).json()
    route_fact = _facts_by_key(body)["existing_zoning_floor_area"]
    assert route_fact == assembled_fact == resolved.fact

    # The honest Northern outcome: UNKNOWN, with the 39,934 sq ft DOB figure SET ASIDE
    # (it may cover the whole zoning lot), its source and the zoning-lot citation kept
    # for the architect -- nothing fabricated.
    assert resolved.basis == "unknown"
    assert route_fact["value"] is None
    assert route_fact["measurement"]["rank"] == "unknown"
    assert route_fact["blocks"] == ["remaining_floor_area", "existing_building_paths"]
    assert "may cover the whole zoning lot rather than this tax lot" in route_fact["note"]
    assert "confirm it as a stated assumption" in route_fact["note"]
    assert DOB_ZONING_FLOOR_AREA in [entry["value"] for entry in resolved.considered]
    # The displaced DOB figure is NEVER emitted as the fact's value.
    assert route_fact["value"] != DOB_ZONING_FLOOR_AREA


# ---------------------------------------------------------------------------
# (2) No evidence provider -> threading is a no-op (facts byte-identical to before).
# ---------------------------------------------------------------------------
def test_no_evidence_provider_is_byte_identical(monkeypatch) -> None:
    _enable(monkeypatch)

    # Assembly with no evidence == assembly with explicit None == the pre-wiring facts.
    baseline = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    threaded_none = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON,
        existing_floor_area=None,
    )
    assert threaded_none.site_facts == baseline.site_facts

    # The route with NO evidence provider serves a body byte-identical to the existing
    # suite's provider (which also binds no evidence provider) -- so every existing
    # study-read test still passes unchanged.
    body_no_evidence = _client(_provider()).get(_URL).json()
    body_existing_suite = _client(_northern_provider()).get(_URL).json()
    assert body_no_evidence == body_existing_suite

    ezfa = _facts_by_key(body_no_evidence)["existing_zoning_floor_area"]
    assert ezfa["value"] is None
    assert ezfa["measurement"]["rank"] == "unknown"
    # No DOB figure anywhere: with no evidence, nothing was considered or set aside.
    assert str(DOB_ZONING_FLOOR_AREA) not in ezfa["note"]


# ---------------------------------------------------------------------------
# (3) Malformed evidence -> the route's fail-safe 503, never a 500.
# ---------------------------------------------------------------------------
def test_malformed_evidence_is_fail_safe_503(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_provider(_malformed_evidence_provider)).get(_URL)
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "inputs_unavailable"
    assert body["correlation_id"]


def test_bad_type_evidence_value_is_fail_safe_503(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_provider(_bad_type_evidence_provider)).get(_URL)
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


def test_valid_evidence_provider_does_not_5xx(monkeypatch) -> None:
    # Red/green companion to the 503 tests: VALID evidence keeps the 200, so the 503
    # above is caused by the malformed evidence, not by threading evidence at all.
    _enable(monkeypatch)
    response = _client(_provider(_evidence_provider(EVIDENCE))).get(_URL)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# (4) The whole study document (with the threaded fact) still passes the contract.
# ---------------------------------------------------------------------------
def test_full_study_with_evidence_passes_contract(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_provider(_evidence_provider(EVIDENCE))).get(_URL).json()
    # Composing the setup with a TEST-ONLY option yields a full study; validating it
    # exercises study.schema.json over the evidence-resolved existing fact too.
    study = {
        "contract_version": "1.0.0",
        "study_id": "test-fixture-synthetic-study-northern-existing-fa",
        "property": body["property"],
        "lots": body["lots"],
        "lot_selection": body["lot_selection"],
        "site": body["site"],
        "options": [_TEST_ONLY_OPTION],
        "selected_option_id": "opt-test",
        "revision": {"number": 1, "created_at": "2026-09-30T12:00:00Z", "parent": None},
        "origin": {"kind": "new", "export_id": None},
    }
    validate_study_document(study)  # raises on any defect
    # The existing_zoning_floor_area fact is present in the validated study.
    assert "existing_zoning_floor_area" in {
        fact["key"] for fact in body["site"]["facts"]
    }
