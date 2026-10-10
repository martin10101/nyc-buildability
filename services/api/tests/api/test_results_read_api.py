"""POST /api/v1/properties/{bbl}/results - the internal results route (task M5-T138, Part A).

WIRING tests (work order Part A, T1-T3 / T9-T11 and the option/import pins). Offline and
deterministic: the route is driven through its INJECTED study-inputs provider
(``get_results_study_inputs_provider`` override), replaying the recorded 215-16 Northern benchmark
pack through the real connectors, so no network is touched. The LAW tests (T4-T8, the made-up lots
of tables B and C, the missing-evidence states and the mutation proof) are in
``test_results_read_law_examples.py``; the shared benchmark/provider helpers here are imported by
that module.

Every emitted (HTTP status, state) pair asserted here is in the route's single source of truth
``RESULTS_READ_STATUS_STATE_MATRIX``.
"""

from __future__ import annotations

import http.client
import json
import socket
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import results_read as mod
from app.api.v1.results_read import (
    RESULTS_READ_STATUS_STATE_MATRIX,
    get_results_study_inputs_provider,
)
from app.api.v1.results_request import ResultsRequestError, build_option, read_results_request
from app.api.v1.study_inputs import assemble_study_inputs
from app.api.v1.study_setup_document import build_study_setup_document
from app.config import INTERNAL_RESULTS_ENABLED_ENV_VAR
from app.contracts.evaluator_inputs import build_evaluator_inputs
from app.contracts.study_contracts import StudyContractError, validate_study_document
from app.contracts.study_setup_bridge import StudySetupBridgeError, study_from_study_setup
from app.main import create_app
from app.scenario.three_answers.result_way_engine_bridge import (
    FLOOR_TO_FLOOR_KEY,
    HOUSING_PROGRAM_KEY,
    run_engine_and_result_ways_from_evidence,
)
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.outline import prepare_outline
from tests.contracts.test_evaluator_inputs import _benchmark_identity_address
from tests.spatial._northern_replay import (
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

NORTHERN_BBL = "4073340070"
LANE_A_ON = "LANE_A_ENABLED"
LANE_B_ON = {"LANE_B_ENABLED": "1"}
_REPO_ROOT = Path(__file__).resolve().parents[4]
_CASES = _REPO_ROOT / "docs" / "reference-cases" / "R6B" / "cases"

# A structurally-similar POST path that is NOT mounted (an extra segment beyond the single {bbl}),
# so it hits FastAPI's generic 404 - the byte template a flag-off read must be identical to.
UNMOUNTED_PROBE = f"/api/v1/properties/{NORTHERN_BBL}/__results_unmounted_probe__"


# --------------------------------------------------------------------------- reference cases
def _ref_rows(case: str) -> dict:
    data = json.loads((_CASES / f"{case}.json").read_text("utf-8"))
    return {row["row_id"]: row for row in data["rows"]}


def _ref_value(case: str, row_id: str):
    return _ref_rows(case)[row_id]["expected"]["value"]


# --------------------------------------------------------------------------- benchmark provider
def _no_network(monkeypatch) -> None:
    def _blocked(*_a, **_k):
        raise AssertionError("network I/O attempted in a recorded-data test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def _benchmark_carriers():
    """The recorded benchmark lot's prepared tax-map outline and site geometry, built offline
    through the real connectors from the recorded pack (no network)."""
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    return prepared, geometry


def benchmark_provider(*, profile_on=True, geometry_on=True, outline_on=True, address=True):
    """A results study-inputs provider over the recorded benchmark pack. ``assemble_study_inputs``
    builds the property profile from the recorded PLUTO body and threads the recorded B-03
    geometry; the flags drop a carrier so the missing-evidence states can be driven. The confirmed
    address is the benchmark pack identity (a corner lot needs it to pick the front lot line)."""
    prepared, geometry = _benchmark_carriers()
    addr = _benchmark_identity_address() if address else None

    def provide(bbl, correlation_id, *, selected=None):
        inputs = assemble_study_inputs(
            replay_pluto(),
            env=LANE_B_ON,
            address=addr,
            site_geometry=geometry if geometry_on else None,
            prepared_outline=prepared if outline_on else None,
        )
        if not profile_on:
            import dataclasses

            inputs = dataclasses.replace(inputs, property_profile=None)
        return inputs

    return provide


def app_with(provider) -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_results_study_inputs_provider] = lambda: provider
    mod.get_rate_limiter().reset()
    return app


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    mod.get_rate_limiter().reset()
    yield
    mod.get_rate_limiter().reset()


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(LANE_A_ON, "1")
    return monkeypatch


def _post(app, body=None):
    body = {"housing_program": "standard_residence"} if body is None else body
    return TestClient(app).post(f"/api/v1/properties/{NORTHERN_BBL}/results", json=body)


# =========================================================================== T1
def test_t1_flag_unset_is_404_byte_identical_to_unmounted(monkeypatch) -> None:
    """T1: the switch unset -> a plain 404, byte-identical to a path that does not exist, and the
    route is absent from the public route list."""
    monkeypatch.delenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, raising=False)
    client = TestClient(create_app())
    unknown = client.post(UNMOUNTED_PROBE, json={"housing_program": "standard_residence"})
    response = client.post(
        f"/api/v1/properties/{NORTHERN_BBL}/results",
        json={"housing_program": "standard_residence"},
    )
    assert response.status_code == unknown.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert response.content == unknown.content
    assert response.headers.get("content-type") == unknown.headers.get("content-type")
    assert "X-Correlation-ID" not in response.headers


@pytest.mark.parametrize("token", ["0", "", "false", "off", "maybe"])
def test_t1_non_true_flag_token_stays_404(monkeypatch, token) -> None:
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, token)
    response = _post(create_app())
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in response.headers


def test_t1_path_absent_from_openapi_in_both_flag_states(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, raising=False)
    off = TestClient(create_app()).get("/openapi.json").json()
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    on = TestClient(create_app()).get("/openapi.json").json()
    template = "/api/v1/properties/{bbl}/results"
    assert template not in off["paths"]
    assert template not in on["paths"]


# =========================================================================== T2
def test_t2_malformed_bbl_is_422_and_provider_never_called(enabled) -> None:
    """T2: a malformed BBL -> a typed 422, and the injected study-inputs provider is never called
    (the data source is not touched)."""
    calls = []

    def spy(bbl, correlation_id, *, selected=None):
        calls.append(bbl)
        raise AssertionError("provider must not be called on a malformed BBL")

    app = app_with(spy)
    response = TestClient(app).post(
        "/api/v1/properties/not-a-bbl/results",
        json={"housing_program": "standard_residence"},
    )
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"
    assert (422, "validation_error") in RESULTS_READ_STATUS_STATE_MATRIX
    assert calls == []


# =========================================================================== T3
def _reference_document(provider, body: dict) -> dict:
    """Reproduce the route's chain deterministically with FIXED identity fields, so the entry's
    own document can be compared to the route's (apart from the id/time fields). Uses the SAME
    option builder the route uses."""
    inputs = provider(NORTHERN_BBL, "ref")
    req = read_results_request(body)
    setup = build_study_setup_document(NORTHERN_BBL, inputs)
    option = build_option(req, option_id="opt-ref")
    study = study_from_study_setup(
        setup, option, study_id="study-ref",
        revision={"number": 1, "created_at": "2026-10-08T00:00:00Z", "parent": None},
    )
    doc = build_evaluator_inputs(study, "opt-ref")
    from app.scenario.three_answers import BuildingDefaults

    defaults = (
        BuildingDefaults(floor_to_floor_ft=req.floor_to_floor_ft)
        if req.floor_to_floor_ft is not None
        else BuildingDefaults()
    )
    # Mirror the route's user_choices exactly (M5-T139): the housing program always, the
    # floor-to-floor height only when the body carried one. Without this the reference would differ
    # from the route on the two design-choice scope lines.
    choices = {HOUSING_PROGRAM_KEY}
    if req.floor_to_floor_ft is not None:
        choices.add(FLOOR_TO_FLOOR_KEY)
    emitted = run_engine_and_result_ways_from_evidence(
        evaluator_inputs=doc, study=study, results_id="res-ref",
        computed_at="2026-10-08T00:00:00Z", housing_program=req.housing_program,
        property_profile=inputs.property_profile, prepared_outline=inputs.prepared_outline,
        site_geometry=inputs.site_geometry,
        special_density_statement=req.special_density_statement,
        building_defaults=defaults, user_choices=frozenset(choices), env=None,
    )
    return emitted.document


_IDENTITY_FIELDS = ("results_id", "study_id", "option_id", "computed_at")


def _blank_identity(doc: dict) -> dict:
    out = json.loads(json.dumps(doc))
    for key in _IDENTITY_FIELDS:
        out[key] = "<id>"
    return out


def test_t3_route_document_equals_the_entry_document(enabled, monkeypatch) -> None:
    """T3 (ruling R1): the route's document equals the document of
    run_engine_and_result_ways_from_evidence for the SAME evidence, apart from the id and time
    fields; it is not compared with any saved file. Nothing of the engine's inner 1.2.0 document is
    returned (no engine_result key; contract 1.3.0)."""
    _no_network(monkeypatch)
    provider = benchmark_provider()
    body = {"housing_program": "standard_residence"}
    response = _post(app_with(provider), body)
    assert response.status_code == 200
    route_doc = response.json()
    # M5-T146 (S23): the route serves the first-building-option blocks - contract 1.4.0, the worked
    # building-alternatives list and each alternative's preliminary capacity estimate.
    assert route_doc["contract_version"] == "1.4.0"
    assert [a["building"] for a in route_doc["building_alternatives"]] == ["B"]
    assert (
        route_doc["building_alternatives"][0]["capacity_estimate"]["label"]
        == "Preliminary capacity estimate"
    )
    assert route_doc["coverage_by_portion"]["status"] == "withheld"
    assert "engine_result" not in route_doc  # the inner engine document is never returned
    reference = _reference_document(provider, body)
    assert _blank_identity(route_doc) == _blank_identity(reference)
    # the route carries a server-minted identity, not the reference's fixed ids
    assert route_doc["results_id"] != "res-ref"
    assert route_doc["study_id"] != "study-ref"


def test_t3_route_files_name_neither_older_entry_nor_the_inputs_builder() -> None:
    """Ruling R1 / scenario S3: the new route files call ONLY the entry that takes evidence; they
    name neither the older entry run_engine_and_result_ways( nor build_three_answer_inputs."""
    here = Path(__file__).resolve().parents[2] / "app" / "api" / "v1"
    for name in ("results_read.py", "results_request.py"):
        src = (here / name).read_text("utf-8")
        assert "build_three_answer_inputs" not in src, name
        assert "run_engine_and_result_ways(" not in src, name


# =========================================================================== M5-T146 live route
_JOURNEY_FIXTURE = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
    / "recorded_215_16_northern_journey.json"
)


def test_m5t146_live_route_benchmark_matches_the_committed_first_option_blocks(
    enabled, monkeypatch,
) -> None:
    """M5-T146 (the defect): the SAME benchmark lot and inputs must give the SAME document by the
    live route and by the journey path. The committed journey document is built with the engine
    lane on and the recorded carriers threaded (property profile, prepared tax-map OUTLINE and site
    geometry), housing program 'standard_residence', no entered floor-to-floor height, no density
    statement. With those same inputs (benchmark_provider threads the outline; the `enabled` fixture
    turns the lane on) the live route returns contract 1.4.0 with coverage_by_portion WITHHELD (no
    figure - the two lot areas disagree) and building_alternatives holding building B, conditional,
    with its preliminary capacity estimate (building A absent). The route's first-building-option
    blocks are byte-equal to the committed document's."""
    _no_network(monkeypatch)
    response = _post(app_with(benchmark_provider()), {"housing_program": "standard_residence"})
    assert response.status_code == 200
    doc = response.json()
    committed = json.loads(_JOURNEY_FIXTURE.read_text("utf-8"))
    assert committed["contract_version"] == doc["contract_version"] == "1.4.0"
    assert doc["building_alternatives"] == committed["building_alternatives"]
    assert doc["coverage_by_portion"] == committed["coverage_by_portion"]
    assert [a["building"] for a in doc["building_alternatives"]] == ["B"]
    building_b = doc["building_alternatives"][0]
    assert building_b["way"]["way"] == "conditional"
    assert building_b["capacity_estimate"]["label"] == "Preliminary capacity estimate"
    assert doc["coverage_by_portion"]["status"] == "withheld"
    assert "footprint_sqft" not in doc["coverage_by_portion"]  # no number on a withheld result
    # the single building option points to the list; the older coverage value agrees with the block
    assert "building_alternatives" in doc["answers"]["building_option"]["reason"]
    assert doc["answers"]["permitted_envelope"]["value_states"]["max_lot_coverage"]["reason"] == (
        doc["coverage_by_portion"]["reason"]
    )


def test_m5t146_live_route_entered_floor_to_floor_works_building_b_at_that_height(
    enabled, monkeypatch,
) -> None:
    """M5-T146 (2): when the user ENTERS a floor-to-floor height (14 ft) the route works building B
    with 14-ft storeys - never silently at 10 ft. Building B reaches the 30 ft minimum base in three
    14-ft storeys (42 ft, at or below the 45 ft maximum base)."""
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider()),
        {"housing_program": "standard_residence", "floor_to_floor_ft": 14},
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["contract_version"] == "1.4.0"
    building_b = next(a for a in doc["building_alternatives"] if a["building"] == "B")
    assert all(row["floor_to_floor_ft"] == 14 for row in building_b["floor_schedule"])  # not 10
    assert building_b["storey_count"] == 3
    assert building_b["height_ft"] == 42  # 3 x 14 ft, reaching the 30 ft minimum base


def test_m5t146_live_route_lists_building_b_without_the_tax_map_outline(
    enabled, monkeypatch,
) -> None:
    """M5-T146 (the defect's root cause): building B is worked from the recorded lot area and the
    allowance, NOT from the tax-map outline, so the route lists it even when the outline is not
    threaded - the production/e2e default (geometry present, the prepared outline absent, so the two
    areas could not be compared and the floor-area way carries no contradicted-record condition).
    Before the fix the route returned 1.3.0 with no blocks here; now building B appears on both
    paths. W13 (b): the area comparison now reaches the emitter, so coverage_by_portion is WITHHELD
    naming that the lot's outline is not available (a missing fact), never computed from the
    recorded area; building A, which needs that footprint, is absent."""
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider(outline_on=False)),
        {"housing_program": "standard_residence"},
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["contract_version"] == "1.4.0"
    assert [a["building"] for a in doc["building_alternatives"]] == ["B"]  # B lists, A absent
    assert doc["building_alternatives"][0]["capacity_estimate"]["label"] == (
        "Preliminary capacity estimate"
    )
    # W13 (b): coverage_by_portion is withheld because the outline is not available, a missing fact;
    # no square-foot figure, and the recorded area is never used in its place.
    coverage = doc["coverage_by_portion"]
    assert coverage["status"] == "withheld"
    assert coverage["gap_kind"] == "missing_information"
    assert "outline is not available" in coverage["reason"]
    assert "footprint_sqft" not in coverage  # no number on a withheld result
    # the older max_lot_coverage value state agrees with the block (ruling W11 a)
    assert doc["answers"]["permitted_envelope"]["value_states"]["max_lot_coverage"]["reason"] == (
        coverage["reason"]
    )
    # M5-T150 (S2 / R896): with no tax-map outline the site plan is not drawn - the whole geometry
    # block is not_available with its reason, never a rectangle sized to the recorded lot area.
    assert doc["geometry"]["status"] == "not_available"
    assert "outline is not available" in doc["geometry"]["reason"]
    assert doc["geometry"]["reason_kind"] == "missing_input"
    assert "lot_outline" not in doc["geometry"]


# ======================================================= W14 (walkthrough F1) live route
def test_w14_s25_live_route_sixteen_ft_no_building_both_reasons(enabled, monkeypatch) -> None:
    """S25 through the LIVE ROUTE (the way the 14 ft test drives the entered height): at 16 ft no
    building is listed, and buildings_not_worked names building A (footprint withheld, missing
    information) and building B (two storeys above the lowest-coverage bound, work owed). The single
    building_option points to both lists and never says 'below the minimum base height'."""
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider()),
        {"housing_program": "standard_residence", "floor_to_floor_ft": 16},
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["contract_version"] == "1.4.0"
    assert doc.get("building_alternatives") in (None, [])
    not_worked = {e["building"]: e for e in doc["buildings_not_worked"]}
    assert set(not_worked) == {"A", "B"}
    assert not_worked["A"]["gap_kind"] == "missing_information"
    assert not_worked["B"]["gap_kind"] == "work_owed"
    assert "80 percent of the recorded lot area" in not_worked["B"]["reason"]
    assert "footprint" not in not_worked["B"]["reason"]
    bo = doc["answers"]["building_option"]
    assert "buildings_not_worked" in bo["reason"] and "building_alternatives" in bo["reason"]
    assert "below the minimum base height" not in bo["reason"]


def test_w14_s26_live_route_twenty_five_ft_building_b_base_passes_max(enabled, monkeypatch) -> None:
    """S26 through the LIVE ROUTE: at 25 ft building B is not worked because the fewest storeys
    reaching the minimum base height stand above the maximum base height. (The route imposes no
    upper limit on the entered floor-to-floor height, so 25 ft is accepted directly.)"""
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider()),
        {"housing_program": "standard_residence", "floor_to_floor_ft": 25},
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc.get("building_alternatives") in (None, [])
    b = next(e for e in doc["buildings_not_worked"] if e["building"] == "B")
    assert b["gap_kind"] == "work_owed"
    assert "maximum base height" in b["reason"]
    assert "feasible" not in json.dumps(doc["buildings_not_worked"]).lower()


def test_w14_s27_live_route_fourteen_ft_building_b_listed_building_a_not_worked(
    enabled, monkeypatch,
) -> None:
    """S27 through the LIVE ROUTE: at 14 ft building B is listed and building A is in
    buildings_not_worked only; each building is in exactly one list."""
    _no_network(monkeypatch)
    response = _post(
        app_with(benchmark_provider()),
        {"housing_program": "standard_residence", "floor_to_floor_ft": 14},
    )
    assert response.status_code == 200
    doc = response.json()
    assert [a["building"] for a in doc["building_alternatives"]] == ["B"]
    assert [e["building"] for e in doc["buildings_not_worked"]] == ["A"]
    worked = {a["building"] for a in doc["building_alternatives"]}
    not_worked = {e["building"] for e in doc["buildings_not_worked"]}
    assert not (worked & not_worked)  # a building is in exactly one list
    assert doc["buildings_not_worked"][0]["gap_kind"] == "missing_information"


def _all_strings(node) -> list[str]:
    out: list[str] = []

    def walk(n):
        if isinstance(n, str):
            out.append(n)
        elif isinstance(n, dict):
            for key, value in n.items():
                out.append(key)
                walk(value)
        elif isinstance(n, list):
            for value in n:
                walk(value)

    walk(node)
    return out


def test_w14c_live_route_false_building_option_text_appears_nowhere(enabled, monkeypatch) -> None:
    """W14 (c) second round / requirement 3 through the LIVE ROUTE: the phrase 'below the minimum
    base height' appears in NO string of the returned document, at the default 10 ft and at 14, 16
    and 25 ft (the heights the existing helpers allow). geometry.floor_plates states the true
    placement reason."""
    _no_network(monkeypatch)
    for f2f in (None, 14, 16, 25):
        body = {"housing_program": "standard_residence"}
        if f2f is not None:
            body["floor_to_floor_ft"] = f2f
        response = _post(app_with(benchmark_provider()), body)
        assert response.status_code == 200
        doc = response.json()
        for text in _all_strings(doc):
            assert "below the minimum base height" not in text, (f2f, text)
        fp = doc["geometry"]["floor_plates"]
        assert fp["reason"].startswith("No floor plate is drawn: no placement on the lot is worked")


# =========================================================================== T9
def test_t9_rate_limit_before_any_other_work(enabled, monkeypatch) -> None:
    """T9: more calls than the per-caller limit -> a typed 429 BEFORE any other work. The limiter
    is set to refuse every caller (max_requests 0), a MALFORMED body is sent and the provider is a
    spy: a 429 (never the 422 the body would earn, and never the provider) proves the limit runs
    first. A loosened limiter removes the 429 (mutation check)."""
    calls = []

    def spy(bbl, correlation_id, *, selected=None):
        calls.append(bbl)
        raise AssertionError("provider must not be reached when rate limited")

    app = create_app()
    app.dependency_overrides[get_results_study_inputs_provider] = lambda: spy
    limiter = mod.get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)  # refuse every caller
    limiter.reset()
    client = TestClient(app)
    response = client.post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", json={"not": "accepted"}
    )
    assert response.status_code == 429
    body = response.json()
    assert body["state"] == "rate_limited"
    assert response.headers["X-Correlation-ID"] == body["correlation_id"]
    assert (429, "rate_limited") in RESULTS_READ_STATUS_STATE_MATRIX
    assert calls == []
    # Mutation (loosen the limiter): a large limit removes the 429 (the malformed body 422 shows).
    monkeypatch.setattr(limiter, "max_requests", 1000)
    limiter.reset()
    loosened = client.post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", json={"not": "accepted"}
    )
    assert loosened.status_code == 422


def test_t9_rate_limit_precedes_the_bbl_check(enabled, monkeypatch) -> None:
    """The limiter runs BEFORE the BBL check: an over-limit caller with a MALFORMED BBL still gets
    the 429, never the 422 the BBL would earn, and the provider is never reached."""
    app = create_app()
    app.dependency_overrides[get_results_study_inputs_provider] = lambda: _spy()
    limiter = mod.get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)  # refuse every caller
    limiter.reset()
    response = TestClient(app).post(
        "/api/v1/properties/not-a-bbl/results", json={"housing_program": "standard_residence"}
    )
    assert response.status_code == 429
    assert response.json()["state"] == "rate_limited"


# =========================================================================== T10
@pytest.mark.parametrize(
    "field,value",
    [
        ("lot_area_sq_ft", 5000),
        ("lot_type", "corner"),
        ("overlay_present", True),
        ("special_district_present", True),
        ("within_100_ft_of_street_line_intersection", True),
        ("lot_line_segments", [{"start": [0, 0], "end": [1, 1]}]),
        ("area_provenance", {"rank": "survey_entered"}),
        ("bbl", "4073340070"),
    ],
)
def test_t10_example_and_lot_fact_fields_are_refused(enabled, field, value) -> None:
    """T10 / S13 / ruling R3: a body carrying ANY field beyond the housing program, the
    floor-to-floor height and the density statement is refused with a typed 422 - one case each for
    a lot area, a lot type, an overlay flag, a special-district flag, a corner condition, a lot
    geometry and an attested-fact provenance. The example-value guard (real_property_guard) has
    nothing to check in this body: no lot fact can enter it, so the refusal happens at the body
    gate, before any guard. The provider is never reached."""
    calls = []

    def spy(bbl, correlation_id, *, selected=None):
        calls.append(bbl)
        raise AssertionError("provider must not be reached on a refused body")

    app = app_with(spy)
    body = {"housing_program": "standard_residence", field: value}
    response = TestClient(app).post(f"/api/v1/properties/{NORTHERN_BBL}/results", json=body)
    assert response.status_code == 422
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert payload["detail"]["field"] == field
    assert calls == []


@pytest.mark.parametrize(
    "body,code,field",
    [
        ({}, "housing_program_required", "housing_program"),
        ({"housing_program": "luxury"}, "housing_program_invalid", "housing_program"),
        (
            {"housing_program": "standard_residence", "floor_to_floor_ft": 0},
            "floor_to_floor_ft_invalid", "floor_to_floor_ft",
        ),
        (
            {"housing_program": "standard_residence", "floor_to_floor_ft": "ten"},
            "floor_to_floor_ft_invalid", "floor_to_floor_ft",
        ),
        (
            {"housing_program": "standard_residence", "special_density_statement": "yes"},
            "special_density_statement_invalid", "special_density_statement",
        ),
    ],
)
def test_t10_bad_values_carry_their_specific_code_and_field(enabled, body, code, field) -> None:
    """Each bad-value refusal carries its SPECIFIC detail.code (and field): a housing program
    outside the vocabulary, a bad floor-to-floor value, a bad density statement."""
    response = TestClient(app_with(_spy())).post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", json=body
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == code
    assert detail["field"] == field


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_t10_non_finite_floor_to_floor_is_422_not_500(enabled, token) -> None:
    """A floor-to-floor height sent as a raw JSON NaN / Infinity / -Infinity token is a typed 422
    (floor_to_floor_ft_invalid) at the body gate - never a 500 - and the provider is never reached.
    The JSON parser admits these tokens, so the body gate must reject them with math.isfinite."""
    raw = '{"housing_program": "standard_residence", "floor_to_floor_ft": ' + token + "}"
    response = TestClient(app_with(_spy())).post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", content=raw
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "floor_to_floor_ft_invalid"
    assert detail["field"] == "floor_to_floor_ft"
    assert response.json()["state"] == "validation_error"


def test_t10_non_object_body_is_422(enabled) -> None:
    app = app_with(benchmark_provider())
    response = TestClient(app).post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", json=[1, 2, 3]
    )
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


# =========================================================================== T11
def test_t11_switch_defaults_off_and_render_untouched() -> None:
    """T11 / S11: INTERNAL_RESULTS_ENABLED defaults off (build-info reports it false by default),
    and the change does not touch render.yaml."""
    from app.api.v1.build_info import build_info_payload

    flags = build_info_payload("0.0.0", env={})["flags"]
    assert flags["INTERNAL_RESULTS_ENABLED"] is False
    render = _REPO_ROOT / "render.yaml"
    assert "INTERNAL_RESULTS_ENABLED" not in render.read_text("utf-8")


# =========================================================================== S15 (the option)
@pytest.mark.parametrize(
    "program", ["standard_residence", "qualifying_affordable_housing", "qualifying_senior_housing"]
)
@pytest.mark.parametrize("f2f", [None, 11.5])
def test_s15_option_built_from_the_body_validates_and_carries_no_lot_fact(program, f2f) -> None:
    """S15 / ruling R2: the option the route hands to study_from_study_setup validates against the
    option definition of the study schema for each housing program and with/without a floor-to-floor
    height; the housing program and floor-to-floor height are the body's; every other field is the
    neutral value; no field is a fact about the lot. Built as a full study (via the benchmark setup)
    so the option is validated in context."""
    body = {"housing_program": program}
    if f2f is not None:
        body["floor_to_floor_ft"] = f2f
    req = read_results_request(body)
    option = build_option(req, option_id="opt-s15")
    # neutral fields (no lot fact; nothing selected; schema-default goal; no existing building)
    assert option["addon_selection"] == []
    assert option["assumptions"] == []
    assert option["existing_building_plan"] == "no_existing_building"
    assert option["goal"] == {"kind": "most_residential_floor_area", "text": None}
    # the floor-to-floor height is the body's (or the stated 10 ft default), printed in the option
    expected_height = 11.5 if f2f is not None else 10.0
    assert option["floor_to_floor_heights"]["typical_floor"]["height_ft"] == expected_height
    assert option["floor_to_floor_heights"]["ground_floor"]["height_ft"] == expected_height
    # validate the option in a full study (study_from_study_setup re-validates the whole study)
    with pytest.MonkeyPatch.context() as mp:
        _no_network(mp)
        inputs = benchmark_provider()(NORTHERN_BBL, "s15")
    setup = build_study_setup_document(NORTHERN_BBL, inputs)
    study = study_from_study_setup(
        setup, option, study_id="s15",
        revision={"number": 1, "created_at": "2026-10-08T00:00:00Z", "parent": None},
    )
    validate_study_document(study)  # reaching here = the option is contract-valid in a study


# =========================================================================== body-shape errors
def _spy():
    def provide(bbl, correlation_id, *, selected=None):
        raise AssertionError("provider must not be reached")

    return provide


def _assert_no_document_or_leak(body: dict, marker: str, response_text: str) -> None:
    """A failure answer carries NO part of a results document, and never the injected exception's
    own text, a file path or a traceback."""
    assert "answers" not in body
    assert "contract_version" not in body
    assert "scope" not in body
    assert marker not in response_text
    assert "Traceback" not in response_text


def test_invalid_json_body_is_422(enabled) -> None:
    """A body that is not valid JSON -> a typed 422 (validation_error, code invalid_json); the
    provider is never reached."""
    response = TestClient(app_with(_spy())).post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", content="{not valid json"
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert payload["detail"]["code"] == "invalid_json"
    assert "answers" not in payload


def test_body_over_the_size_limit_is_422(enabled) -> None:
    """A raw body larger than MAX_BODY_BYTES (64 KiB) -> a typed 422 (validation_error, code
    body_too_large) BEFORE the body is parsed; the provider is never reached."""
    big = b'{"housing_program":"standard_residence","pad":"' + b"a" * mod.MAX_BODY_BYTES + b'"}'
    assert len(big) > mod.MAX_BODY_BYTES
    response = TestClient(app_with(_spy())).post(
        f"/api/v1/properties/{NORTHERN_BBL}/results", content=big
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert payload["detail"]["code"] == "body_too_large"
    assert "answers" not in payload


def test_bridged_study_contract_failure_is_500_contract_error(enabled, monkeypatch) -> None:
    """The bridged study failing its contract -> 500 internal_contract_error; no document is sent
    and the exception's own text is not leaked. Injected by monkeypatching the route module's own
    study_from_study_setup name (the bridge module itself is read-only)."""
    _no_network(monkeypatch)
    marker = "SECRET-TRACE-/private/study/leak"

    def boom(*a, **k):
        raise StudyContractError(marker, contract="study", location="x")

    monkeypatch.setattr(mod, "study_from_study_setup", boom)
    response = _post(app_with(benchmark_provider()), {"housing_program": "standard_residence"})
    assert response.status_code == 500
    payload = response.json()
    assert payload["state"] == "internal_contract_error"
    assert (500, "internal_contract_error") in RESULTS_READ_STATUS_STATE_MATRIX
    _assert_no_document_or_leak(payload, marker, response.text)


def test_emitted_document_contract_failure_is_500_and_not_delivered(enabled, monkeypatch) -> None:
    """The emitted results document failing its contract before send -> 500 internal_contract_error
    and the document is NOT delivered (an invalid 200 is impossible). Injected by monkeypatching the
    route module's own validate_results_document name (the validator module is read-only)."""
    _no_network(monkeypatch)
    marker = "SECRET-TRACE-/private/results/leak"

    def boom(document):
        raise StudyContractError(marker, contract="results", location="x")

    monkeypatch.setattr(mod, "validate_results_document", boom)
    response = _post(app_with(benchmark_provider()), {"housing_program": "standard_residence"})
    assert response.status_code == 500
    payload = response.json()
    assert payload["state"] == "internal_contract_error"
    _assert_no_document_or_leak(payload, marker, response.text)


def test_bridge_refusal_is_500_internal_error(enabled, monkeypatch) -> None:
    """A StudySetupBridgeError (the server-built study_setup is malformed) -> 500 internal_error; no
    document and no leak. Injected via the route module's own study_from_study_setup name."""
    _no_network(monkeypatch)
    marker = "SECRET-TRACE-/private/bridge/leak"

    def boom(*a, **k):
        raise StudySetupBridgeError(marker)

    monkeypatch.setattr(mod, "study_from_study_setup", boom)
    response = _post(app_with(benchmark_provider()), {"housing_program": "standard_residence"})
    assert response.status_code == 500
    payload = response.json()
    assert payload["state"] == "internal_error"
    assert (500, "internal_error") in RESULTS_READ_STATUS_STATE_MATRIX
    _assert_no_document_or_leak(payload, marker, response.text)


def test_unexpected_exception_is_500_internal_error(enabled, monkeypatch) -> None:
    """Any other unexpected exception in the prepare stage -> a generic 500 internal_error; no
    document and no leak. Injected via the route module's own build_option name."""
    _no_network(monkeypatch)
    marker = "SECRET-TRACE-/private/unexpected/leak"

    def boom(*a, **k):
        raise RuntimeError(marker)

    monkeypatch.setattr(mod, "build_option", boom)
    response = _post(app_with(benchmark_provider()), {"housing_program": "standard_residence"})
    assert response.status_code == 500
    payload = response.json()
    assert payload["state"] == "internal_error"
    _assert_no_document_or_leak(payload, marker, response.text)


# =========================================================================== S7 (wrong-kind values)
# M5-T141 scope correction: a value of the WRONG KIND for a field is refused with that field's typed
# code - through the reader (a typed ResultsRequestError, NEVER another exception: an unhashable
# housing program used to raise TypeError, and the route then answered a generic 500) and through
# the route (a 422 validation_error carrying that code; the provider is never reached; never a 500).
# Only housing_program was fixed; floor_to_floor_ft, special_density_statement and the not-an-object
# body were already refused correctly and deliberately (explicit isinstance / number checks), and
# these tests lock that behaviour. No answer for a valid body changes.

_STD = "standard_residence"
# Wrong KIND for the housing program: unhashable (the reported fault), and the other non-strings.
_WRONG_HOUSING_PROGRAM = [[], {}, [_STD], {"a": 1}, 1, 1.5, True, False, None]
# A parsed body that is not a JSON object.
_NON_OBJECT_BODIES = [[1, 2, 3], "a string", 123, 1.5, True, False, None]
# Wrong KIND for the optional floor-to-floor height (true/false are numbers to Python; an explicit
# null is refused too - S7 names it - never silently treated as "absent").
_WRONG_FLOOR_TO_FLOOR = [[], {}, "ten", True, False, None]
# Wrong KIND for the optional density statement: anything but a real boolean. The WORDS "true" and
# "false" are refused (a reader that read them as booleans would pass every other row); 1/0 are not
# booleans; an explicit null is refused too (S7), never read as "no statement".
_WRONG_DENSITY_STATEMENT = [[], {}, "yes", "true", "false", 1, 0, 1.5, None]


def _reader_refuses(body, *, code, field) -> None:
    """``read_results_request(body)`` raises a typed ResultsRequestError (never another exception,
    e.g. TypeError) carrying ``code`` and ``field``."""
    with pytest.raises(ResultsRequestError) as excinfo:
        read_results_request(body)
    assert excinfo.value.code == code
    assert excinfo.value.field == field


def _route_refuses(*, code, field, json_body=None, content=None) -> None:
    """POST ``json_body`` (or raw ``content``) with a SPY provider: a 422 validation_error carrying
    ``code``/``field``, the provider never reached, and never a 500."""
    calls: list[str] = []

    def spy(bbl, correlation_id, *, selected=None):
        calls.append(bbl)
        raise AssertionError("provider must not be reached on a refused body")

    client = TestClient(app_with(spy))
    url = f"/api/v1/properties/{NORTHERN_BBL}/results"
    response = client.post(url, content=content) if content is not None else client.post(
        url, json=json_body
    )
    assert response.status_code == 422, response.text
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert (422, "validation_error") in RESULTS_READ_STATUS_STATE_MATRIX
    assert payload["detail"]["code"] == code
    if field is None:
        assert "field" not in payload["detail"]
    else:
        assert payload["detail"]["field"] == field
    assert calls == []


# --------------------------------------------------------------------------- housing_program
@pytest.mark.parametrize("value", _WRONG_HOUSING_PROGRAM)
def test_s7_reader_refuses_wrong_kind_housing_program(value) -> None:
    _reader_refuses({"housing_program": value}, code="housing_program_invalid",
                    field="housing_program")


@pytest.mark.parametrize("value", _WRONG_HOUSING_PROGRAM)
def test_s7_route_refuses_wrong_kind_housing_program(enabled, value) -> None:
    _route_refuses(json_body={"housing_program": value}, code="housing_program_invalid",
                   field="housing_program")


# --------------------------------------------------------------------------- not an object
@pytest.mark.parametrize("value", _NON_OBJECT_BODIES)
def test_s7_reader_refuses_non_object_body(value) -> None:
    _reader_refuses(value, code="invalid_body", field=None)


@pytest.mark.parametrize("value", _NON_OBJECT_BODIES)
def test_s7_route_refuses_non_object_body(enabled, value) -> None:
    _route_refuses(content=json.dumps(value), code="invalid_body", field=None)


# --------------------------------------------------------------------------- floor_to_floor_ft
@pytest.mark.parametrize("value", _WRONG_FLOOR_TO_FLOOR)
def test_s7_reader_refuses_wrong_kind_floor_to_floor(value) -> None:
    _reader_refuses({"housing_program": _STD, "floor_to_floor_ft": value},
                    code="floor_to_floor_ft_invalid", field="floor_to_floor_ft")


@pytest.mark.parametrize("value", _WRONG_FLOOR_TO_FLOOR)
def test_s7_route_refuses_wrong_kind_floor_to_floor(enabled, value) -> None:
    _route_refuses(json_body={"housing_program": _STD, "floor_to_floor_ft": value},
                   code="floor_to_floor_ft_invalid", field="floor_to_floor_ft")


# --------------------------------------------------------------------------- density statement
@pytest.mark.parametrize("value", _WRONG_DENSITY_STATEMENT)
def test_s7_reader_refuses_wrong_kind_density_statement(value) -> None:
    _reader_refuses({"housing_program": _STD, "special_density_statement": value},
                    code="special_density_statement_invalid", field="special_density_statement")


@pytest.mark.parametrize("value", _WRONG_DENSITY_STATEMENT)
def test_s7_route_refuses_wrong_kind_density_statement(enabled, value) -> None:
    _route_refuses(json_body={"housing_program": _STD, "special_density_statement": value},
                   code="special_density_statement_invalid", field="special_density_statement")


def test_s7_reported_fault_is_now_a_typed_422_not_a_500(enabled) -> None:
    """The exact reported fault: a list as the housing program no longer raises TypeError / a 500 -
    the reader refuses it typed and the route answers a 422 validation_error (regression guard)."""
    _reader_refuses({"housing_program": []}, code="housing_program_invalid",
                    field="housing_program")
    _route_refuses(json_body={"housing_program": []}, code="housing_program_invalid",
                   field="housing_program")
