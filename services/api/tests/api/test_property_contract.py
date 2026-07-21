"""Property API boundary + contract-version hardening (task M2-T003).

Acceptance scenarios (packet S1-S8, S10):

- S1  valid profile passes backend validation unchanged and declares the
      resolved canonical contract_version (1.4.0 since task M2-T012).
- S2  fault injection: a malformed profile from the builder yields a typed
      500 internal_contract_error with correlation id, never an invalid 200.
- S3  pair matrix: every (HTTP status, state) emission path is enumerated
      against the documented STATUS_STATE_MATRIX; an undocumented pair fails.
- S5  typegen determinism + 100% key coverage (test_property_typegen.py).
- S6  contract_version consistency: schema, README, API, builder agree on
      1.4.0; declared-vs-emitted-key-set consistency (including the M2-T006
      dotted-path key reproducibility.staleness and the M2-T012 wave keys); no
      stale hard-coded ver.
- S7  backward compatibility: valid 1.2.0, 1.1.0 AND 1.0.0 instances still
      pass backend validation (every added key is optional).
- S8  unsupported version: a profile declaring an unpublished contract_version
      is rejected with a bounded typed error, never coerced.
- S10 regression is the whole suite staying green (this file adds to it).

Offline and deterministic: the connector dependency is overridden with the
same fixture-transport seam the accepted M1-T005/M2-T004 tests use; no test
touches the network.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import properties as properties_module
from app.api.v1.properties import STATUS_STATE_MATRIX, get_pluto_fetcher
from app.connectors.pluto_soda import (
    SOURCE_ID,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.profile import contract as contract_module
from app.profile.builder import PROFILE_CONTRACT_VERSION, build_property_profile
from app.profile.contract import (
    SUPPORTED_CONTRACT_VERSIONS,
    ContractValidationError,
    UnsupportedContractVersionError,
    select_schema_version,
    validate_profile,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
CONTRACTS_FIXTURE_DIR = REPO_ROOT / "packages" / "contracts" / "fixtures"

FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731


# --------------------------------------------------------------------------
# Fixture-transport helpers (same seam as the accepted suites)
# --------------------------------------------------------------------------


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


class FakeTransport:
    def __init__(self, script: list):
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        if not self.script:
            raise AssertionError("FakeTransport script exhausted")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class FetcherHarness:
    def __init__(self, script_factory):
        self.script_factory = script_factory

    def __call__(self, bbl: str, correlation_id: str):
        return fetch_by_bbl(
            bbl,
            transport=FakeTransport(self.script_factory()),
            sleep=lambda seconds: None,
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
        )


def install_fetcher(fetcher) -> None:
    app.dependency_overrides[get_pluto_fetcher] = lambda: fetcher


def fixture_fetcher(name: str) -> None:
    install_fetcher(FetcherHarness(lambda: [fixture_response(name)]))


def scripted_fetcher(script_factory) -> None:
    install_fetcher(FetcherHarness(script_factory))


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def raw_client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def build_f01_profile() -> dict:
    """Build a real F01 profile through the accepted connector + builder."""
    transport = FakeTransport([fixture_response("F01_single_lot_normal.json")])
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=lambda s: None,
        clock=FIXED_CLOCK, correlation_id="test-correlation",
    )
    return build_property_profile(result)


# --------------------------------------------------------------------------
# S1 - valid profile passes validation and declares the resolved version
# --------------------------------------------------------------------------


def test_s1_valid_profile_declares_resolved_version_and_validates(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    profile = response.json()
    # The resolved canonical declaration (declare-what-you-emit; 1.4.0 since
    # M2-T012 added the optional wave/spatial-integration keys).
    assert profile["profile_version"]["contract_version"] == "1.4.0"
    # And it passes the same validator the route ran before send.
    validate_profile(profile)  # must not raise


def test_s1_validate_profile_accepts_the_real_builder_output() -> None:
    validate_profile(build_f01_profile())  # must not raise


# --------------------------------------------------------------------------
# S2 - fault injection: a malformed profile -> typed 500, never a 200
# --------------------------------------------------------------------------


def _assert_internal_contract_500(response, expected_reason: str | None = None) -> None:
    assert response.status_code == 500
    assert response.headers.get("X-Correlation-ID")
    body = response.json()
    assert body["state"] == "internal_contract_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    if expected_reason is not None:
        assert body["detail"]["reason"] == expected_reason


def test_s2_missing_required_key_yields_typed_500_never_200(raw_client, monkeypatch) -> None:
    fixture_fetcher("F01_single_lot_normal.json")

    def malformed_builder(result):
        profile = build_property_profile(result)
        del profile["lot_facts"]  # drop a REQUIRED key
        return profile

    monkeypatch.setattr(properties_module, "build_property_profile", malformed_builder)
    response = raw_client.get("/api/v1/properties/1000010100")
    _assert_internal_contract_500(response, "schema_validation_failed")


def test_s2_wrong_type_yields_typed_500_never_200(raw_client, monkeypatch) -> None:
    fixture_fetcher("F01_single_lot_normal.json")

    def malformed_builder(result):
        profile = build_property_profile(result)
        profile["lot_facts"] = "not-an-object"  # wrong type
        return profile

    monkeypatch.setattr(properties_module, "build_property_profile", malformed_builder)
    response = raw_client.get("/api/v1/properties/1000010100")
    _assert_internal_contract_500(response, "schema_validation_failed")


def test_s2_an_invalid_200_is_impossible(raw_client, monkeypatch) -> None:
    """The core guarantee: whatever the builder does, a schema-invalid payload
    can never leave as a 200."""
    fixture_fetcher("F01_single_lot_normal.json")

    def malformed_builder(result):
        profile = build_property_profile(result)
        # Break provenance-ref integrity AND a fact value shape at once.
        profile["lot_facts"]["lotarea"] = {"value": 1}  # missing provenance_ref
        return profile

    monkeypatch.setattr(properties_module, "build_property_profile", malformed_builder)
    response = raw_client.get("/api/v1/properties/1000010100")
    assert response.status_code != 200
    _assert_internal_contract_500(response)


def test_s2_staleness_conditional_violations_are_schema_failures() -> None:
    """M2-T006: the 1.3.0 staleness conditionals are enforced at the boundary.
    A payload claiming stale without naming the upstream failure, or claiming
    a cached serve without stating its age, fails schema validation - it can
    never leave as a 200 (the route maps this to internal_contract_error)."""
    profile = build_f01_profile()
    profile["reproducibility"]["staleness"] = {
        "served_from_cache": True,
        "stale": True,
        "original_retrieved_at": "2026-07-16T12:00:00Z",
        "age_seconds": 120.0,
        # upstream_error_type missing while stale is true
    }
    with pytest.raises(ContractValidationError) as excinfo:
        validate_profile(profile)
    assert excinfo.value.reason == "schema_validation_failed"

    profile = build_f01_profile()
    profile["reproducibility"]["staleness"] = {
        "served_from_cache": True,  # cached serve without age/original ts
        "stale": False,
    }
    with pytest.raises(ContractValidationError) as excinfo:
        validate_profile(profile)
    assert excinfo.value.reason == "schema_validation_failed"


# --------------------------------------------------------------------------
# S3 - exact (HTTP status, state) pair matrix enforcement
# --------------------------------------------------------------------------


# Every emission path the endpoint can take, as (path_id, driver, expected
# pair). The test drives each and asserts the observed pair is BOTH what the
# path documents AND a member of STATUS_STATE_MATRIX. A path producing an
# undocumented pair fails the suite (packet item D).
def _drive_200(client):
    fixture_fetcher("F01_single_lot_normal.json")
    return client.get("/api/v1/properties/1000010100")


def _drive_422(client):
    def must_not_call(bbl, correlation_id):
        raise AssertionError("connector must not be called for malformed BBL")

    install_fetcher(must_not_call)
    return client.get("/api/v1/properties/6000010100")  # invalid borough


def _drive_404(client):
    fixture_fetcher("F03b_no_match_valid_bbl.json")
    return client.get("/api/v1/properties/5999999999")


def _drive_502(client):
    scripted_fetcher(lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")])
    return client.get("/api/v1/properties/1000010100")


def _drive_503_rate(client):
    scripted_fetcher(lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3)
    return client.get("/api/v1/properties/1000010100")


def _drive_503_unavail(client):
    scripted_fetcher(lambda: [TransportFailure("network failure: OSError")] * 3)
    return client.get("/api/v1/properties/1000010100")


def _drive_504(client):
    scripted_fetcher(lambda: [TransportTimeout("timeout after 10.0s")] * 3)
    return client.get("/api/v1/properties/1000010100")


PAIR_PATHS = [
    ("profile_200", _drive_200, (200, None)),
    ("validation_422", _drive_422, (422, "validation_error")),
    ("no_match_404", _drive_404, (404, "no_match")),
    ("schema_drift_502", _drive_502, (502, "schema_drift")),
    ("rate_limited_503", _drive_503_rate, (503, "rate_limited")),
    ("source_unavailable_503", _drive_503_unavail, (503, "source_unavailable")),
    ("timeout_504", _drive_504, (504, "timeout")),
]


@pytest.mark.parametrize(
    ("path_id", "driver", "expected"), PAIR_PATHS, ids=[p[0] for p in PAIR_PATHS]
)
def test_s3_every_pair_is_documented(client, path_id, driver, expected) -> None:
    response = driver(client)
    status = response.status_code
    state = None if status == 200 else response.json().get("state")
    observed = (status, state)
    assert observed == expected, f"{path_id}: emitted {observed}, path documents {expected}"
    assert observed in STATUS_STATE_MATRIX, (
        f"{path_id}: emitted undocumented (status, state) pair {observed}; "
        "add it to STATUS_STATE_MATRIX or fix the emission"
    )


def test_s3_500_internal_contract_error_pair_is_documented(raw_client, monkeypatch) -> None:
    fixture_fetcher("F01_single_lot_normal.json")

    def malformed_builder(result):
        profile = build_property_profile(result)
        del profile["identity"]
        return profile

    monkeypatch.setattr(properties_module, "build_property_profile", malformed_builder)
    response = raw_client.get("/api/v1/properties/1000010100")
    observed = (response.status_code, response.json().get("state"))
    assert observed == (500, "internal_contract_error")
    assert observed in STATUS_STATE_MATRIX


def test_s3_500_unsupported_version_pair_is_documented(raw_client, monkeypatch) -> None:
    fixture_fetcher("F01_single_lot_normal.json")

    def bad_version_builder(result):
        profile = build_property_profile(result)
        profile["profile_version"]["contract_version"] = "1.5.0"  # unpublished
        return profile

    monkeypatch.setattr(properties_module, "build_property_profile", bad_version_builder)
    response = raw_client.get("/api/v1/properties/1000010100")
    observed = (response.status_code, response.json().get("state"))
    assert observed == (500, "unsupported_contract_version")
    assert observed in STATUS_STATE_MATRIX


def test_s3_500_generic_internal_error_pair_is_documented(raw_client) -> None:
    def exploding(bbl, correlation_id):
        raise RuntimeError("boom")

    install_fetcher(exploding)
    response = raw_client.get("/api/v1/properties/1000010100")
    observed = (response.status_code, response.json().get("state"))
    assert observed == (500, "internal_error")
    assert observed in STATUS_STATE_MATRIX


def test_s3_matrix_has_no_untested_pairs() -> None:
    """The matrix must not accumulate documented-but-unreachable pairs: every
    member is exercised by a test above."""
    tested = {expected for _, _, expected in PAIR_PATHS} | {
        (500, "internal_contract_error"),
        (500, "unsupported_contract_version"),
        (500, "internal_error"),
    }
    assert tested == set(STATUS_STATE_MATRIX)


# --------------------------------------------------------------------------
# S6 - contract_version consistency; no stale hard-coded version
# --------------------------------------------------------------------------


def test_s6_builder_and_schema_agree_on_canonical_version() -> None:
    assert PROFILE_CONTRACT_VERSION == "1.4.0"
    assert PROFILE_CONTRACT_VERSION in SUPPORTED_CONTRACT_VERSIONS
    # The supported set is sourced LIVE from the schema enum, not hard-coded.
    assert SUPPORTED_CONTRACT_VERSIONS == ("1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0")


def test_s6_declared_below_emitted_keys_is_rejected() -> None:
    """The exact stale-declaration bug M2-T004 deferred: declaring 1.0.0 while
    emitting a 1.2.0 key must be rejected by the consistency check."""
    profile = build_f01_profile()
    assert "status_dimensions" in profile  # a 1.2.0-only key
    profile["profile_version"]["contract_version"] = "1.0.0"
    with pytest.raises(ContractValidationError) as excinfo:
        validate_profile(profile)
    assert excinfo.value.reason == "declared_version_below_emitted_keys"


def test_s6_declared_11_with_status_dimensions_is_rejected() -> None:
    profile = build_f01_profile()
    profile["profile_version"]["contract_version"] = "1.1.0"
    with pytest.raises(ContractValidationError) as excinfo:
        validate_profile(profile)
    assert excinfo.value.reason == "declared_version_below_emitted_keys"


def test_s6_declared_12_with_staleness_is_rejected_via_dotted_path() -> None:
    """M2-T006: the NESTED 1.3.0 key participates in the consistency check
    through dotted-path resolution. A payload emitting
    reproducibility.staleness while declaring 1.2.0 misstates its version and
    is rejected - the schema/builder/check move atomically or not at all."""
    profile = build_f01_profile()
    profile.pop("status_dimensions")  # remove the 1.2.0 top-level signal
    assert "staleness" in profile["reproducibility"]  # the 1.3.0-only key
    profile["profile_version"]["contract_version"] = "1.2.0"
    with pytest.raises(ContractValidationError) as excinfo:
        validate_profile(profile)
    assert excinfo.value.reason == "declared_version_below_emitted_keys"


def test_s6_dotted_path_absence_is_not_a_false_positive() -> None:
    """A 1.2.0-declaring payload WITHOUT staleness passes the consistency
    check (dotted-path absence detected through the nested walk)."""
    profile = build_f01_profile()
    profile["reproducibility"].pop("staleness")
    profile["profile_version"]["contract_version"] = "1.2.0"
    contract_module._assert_declared_matches_emitted(profile)  # must not raise


def test_s6_no_stale_version_hard_coded_in_builder_source() -> None:
    """Guard against a stray hard-coded '1.0.0' contract_version reappearing in
    the builder (the defect this task fixes)."""
    builder_src = (REPO_ROOT / "services" / "api" / "app" / "profile" / "builder.py").read_text(
        encoding="utf-8"
    )
    assert 'PROFILE_CONTRACT_VERSION = "1.4.0"' in builder_src
    assert 'PROFILE_CONTRACT_VERSION = "1.0.0"' not in builder_src
    assert 'PROFILE_CONTRACT_VERSION = "1.2.0"' not in builder_src
    assert 'PROFILE_CONTRACT_VERSION = "1.3.0"' not in builder_src


# --------------------------------------------------------------------------
# S7 - backward compatibility: valid 1.1.0 AND 1.0.0 still validate
# --------------------------------------------------------------------------


def load_contract_fixture(rel: str) -> dict:
    return json.loads((CONTRACTS_FIXTURE_DIR / rel).read_text(encoding="utf-8"))


def test_s7_valid_1_0_0_instance_still_validates() -> None:
    """A 1.0.0 instance with NO post-1.0.0 keys remains valid and served
    unchanged (every added key is optional)."""
    instance = load_contract_fixture("valid/property_profile/full_example.json")
    assert instance["profile_version"]["contract_version"] == "1.0.0"
    assert "status_dimensions" not in instance
    assert "reproducibility" not in instance
    validate_profile(instance)  # must not raise


def test_s7_valid_1_1_0_instance_still_validates() -> None:
    """A 1.1.0 instance (data_completeness + reproducibility, no
    status_dimensions) remains valid and served unchanged."""
    instance = load_contract_fixture("valid/property_profile/full_example_v1_1.json")
    assert instance["profile_version"]["contract_version"] == "1.1.0"
    assert "status_dimensions" not in instance
    validate_profile(instance)  # must not raise


def test_s7_a_declared_11_instance_may_carry_11_keys() -> None:
    """Declared-vs-emitted allows a declared version to carry keys at OR below
    its own version - 1.1.0 with reproducibility is consistent."""
    instance = load_contract_fixture("valid/property_profile/full_example_v1_1.json")
    assert "reproducibility" in instance
    contract_module._assert_declared_matches_emitted(instance)  # must not raise


def test_s7_valid_1_2_0_instance_still_validates() -> None:
    """M2-T006 (packet S5): a 1.2.0-shaped instance (status_dimensions and
    lineage keys, NO staleness) remains valid against the 1.3.0-published
    schema and passes the full backend boundary - additive-optional proof."""
    instance = load_contract_fixture(
        "valid/property_profile/status_dimensions_lineage_m2_t004.json"
    )
    assert instance["profile_version"]["contract_version"] == "1.2.0"
    assert "staleness" not in instance.get("reproducibility", {})
    validate_profile(instance)  # must not raise


def test_s7_valid_1_3_0_lkg_fixture_validates() -> None:
    """The committed 1.3.0 LKG-serve fixture (typed staleness + retained
    human-readable note) passes the full backend boundary."""
    instance = load_contract_fixture("valid/property_profile/staleness_lkg_m2_t006.json")
    staleness = instance["reproducibility"]["staleness"]
    assert staleness["served_from_cache"] is True
    assert staleness["stale"] is True
    validate_profile(instance)  # must not raise


# --------------------------------------------------------------------------
# S8 - unsupported version -> bounded typed error, never coerced
# --------------------------------------------------------------------------


def test_s8_select_schema_version_rejects_unpublished() -> None:
    # 1.5.0 is the current rejected exemplar (one beyond the published 1.4.0);
    # 1.4.0 became published by task M2-T012.
    with pytest.raises(UnsupportedContractVersionError) as excinfo:
        select_schema_version("1.5.0")
    assert excinfo.value.declared_version == "1.5.0"


def test_s8_validate_profile_bounded_error_for_unpublished_version() -> None:
    profile = build_f01_profile()
    profile["profile_version"]["contract_version"] = "1.5.0"
    with pytest.raises(UnsupportedContractVersionError):
        validate_profile(profile)


def test_s8_route_returns_bounded_500_for_unpublished_version(raw_client, monkeypatch) -> None:
    fixture_fetcher("F01_single_lot_normal.json")

    def bad_version_builder(result):
        profile = build_property_profile(result)
        profile["profile_version"]["contract_version"] = "9.9.9"
        return profile

    monkeypatch.setattr(properties_module, "build_property_profile", bad_version_builder)
    response = raw_client.get("/api/v1/properties/1000010100")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "unsupported_contract_version"
    assert body["detail"]["declared_version"] == "9.9.9"
    assert body["detail"]["supported_versions"] == list(SUPPORTED_CONTRACT_VERSIONS)
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    # Bounded: no stack trace, no builder internals leaked.
    assert "Traceback" not in response.text


def test_s8_unsupported_version_is_never_coerced_to_a_neighbor() -> None:
    """The declared version is rejected, not silently rewritten to 1.4.0."""
    profile = build_f01_profile()
    profile["profile_version"]["contract_version"] = "1.5.0"
    with pytest.raises(UnsupportedContractVersionError):
        validate_profile(profile)
    # The profile object was not mutated to a supported version.
    assert profile["profile_version"]["contract_version"] == "1.5.0"


def test_s8_malformed_contract_version_type_is_typed_contract_error() -> None:
    profile = build_f01_profile()
    profile["profile_version"]["contract_version"] = 120  # not a string
    with pytest.raises(ContractValidationError) as excinfo:
        validate_profile(profile)
    assert excinfo.value.reason == "malformed_contract_version"


# --------------------------------------------------------------------------
# S1/S7 - the S4 client-regression fixture exists and is a coherent artifact
# --------------------------------------------------------------------------


def test_s4_client_regression_fixture_is_recorded_and_incoherent_by_design() -> None:
    """The HTTP 500 + state=no_match fixture (packet item F) exists for M2-T002
    and records the deliberately INCOHERENT pair the client must defend
    against. It is not in STATUS_STATE_MATRIX (the real app never emits it)."""
    fixture = load_contract_fixture("client_regression/http500_state_no_match.json")
    assert fixture["http_status"] == 500
    assert fixture["response_body"]["state"] == "no_match"
    assert fixture["_synthetic"] is True
    # The whole point: this pair is NOT a documented emission of the API.
    assert (500, "no_match") not in STATUS_STATE_MATRIX
    # The body still carries the correlation id the client keys logging off of.
    assert fixture["response_body"]["correlation_id"]
    assert fixture["response_body"]["source_id"] == SOURCE_ID
