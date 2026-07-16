"""Property-profile API v1 tests (task M1-T005, scenarios S1-S8).

Offline and deterministic: the route's connector dependency is overridden via
FastAPI dependency injection with a fixture-transport fetcher, so no test
touches the network. Fixtures are the accepted M1-T002 live captures in
services/api/tests/fixtures/pluto/; where a scenario needs a variant the
official API cannot politely provide (borocode conflict, hostile bodies),
the test derives a clearly-labeled SYNTHETIC variant inside the test body.
"""

import io
import json
import urllib.error
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1.properties import get_pluto_fetcher
from app.connectors import pluto_soda
from app.connectors.pluto_soda import (
    MAX_RESPONSE_BYTES,
    SOURCE_ID,
    SourceUnavailableError,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
    urllib_transport,
)
from app.main import app
from app.profile.builder import build_property_profile

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"

FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731

COVERAGE_ENUM = {
    "verified", "conditional", "professional_review_required",
    "data_conflict", "unsupported", "not_applicable",
}
UNREVIEWED_ALLOWED_COVERAGE = COVERAGE_ENUM - {"verified", "professional_review_required"}


# --------------------------------------------------------------------------
# Helpers (local copies of the M1-T002 fixture-transport pattern)
# --------------------------------------------------------------------------


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


class FakeTransport:
    """Replays a scripted sequence of responses/exceptions and records calls."""

    def __init__(self, script: list):
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        if not self.script:
            raise AssertionError("FakeTransport script exhausted - unexpected extra request")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class SleepRecorder:
    def __init__(self):
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


class FetcherHarness:
    """Route fetcher bound to fixture transports; one fresh transport per
    request so repeat calls (S6) replay identical official captures."""

    def __init__(self, script_factory, **fetch_kwargs):
        self.script_factory = script_factory
        self.fetch_kwargs = fetch_kwargs
        self.transports: list[FakeTransport] = []
        self.calls: list[tuple[str, str]] = []

    def __call__(self, bbl: str, correlation_id: str):
        self.calls.append((bbl, correlation_id))
        transport = FakeTransport(self.script_factory())
        self.transports.append(transport)
        return fetch_by_bbl(
            bbl,
            transport=transport,
            sleep=SleepRecorder(),
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
            **self.fetch_kwargs,
        )


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def install_fetcher(fetcher) -> None:
    app.dependency_overrides[get_pluto_fetcher] = lambda: fetcher


def fixture_fetcher(name: str, **fetch_kwargs) -> FetcherHarness:
    harness = FetcherHarness(lambda: [fixture_response(name)], **fetch_kwargs)
    install_fetcher(harness)
    return harness


def synthetic_record_fetcher(mutate, **fetch_kwargs) -> FetcherHarness:
    """SYNTHETIC variant of the real F01 record (exercises route/builder
    logic only; never presented as official data)."""
    record = json.loads(load_fixture("F01_single_lot_normal.json")["response_body_raw"])[0]
    mutate(record)
    body = json.dumps([record])
    harness = FetcherHarness(lambda: [TransportResponse(200, body)], **fetch_kwargs)
    install_fetcher(harness)
    return harness


@pytest.fixture(scope="module")
def profile_validator():
    """jsonschema validator for property_profile.schema.json v1 with the
    common + source_fact contracts resolved (mirrors validate_contracts.py)."""
    jsonschema = pytest.importorskip("jsonschema")
    docs = [
        json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        for name in (
            "property_profile.schema.json",
            "source_fact.schema.json",
            "common.schema.json",
        )
    ]
    schema = docs[0]
    try:
        from referencing import Registry, Resource

        registry = Registry().with_resources(
            [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
        )
        return jsonschema.Draft202012Validator(schema, registry=registry)
    except ImportError:
        resolver = jsonschema.RefResolver(
            base_uri=schema["$id"],
            referrer=schema,
            store={doc["$id"]: doc for doc in docs},
        )
        return jsonschema.Draft202012Validator(schema, resolver=resolver)


def all_fact_values(profile: dict) -> list[dict]:
    values = list(profile["lot_facts"].values())
    values.extend(profile["existing_building_facts"].values())
    values.extend(profile["zoning"]["mapped_features"])
    return values


# --------------------------------------------------------------------------
# S1 - normal: 200 canonical profile, schema-valid, provenance-linked
# --------------------------------------------------------------------------


def test_s1_200_profile_validates_against_property_profile_v1(
    client, profile_validator
) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    profile = response.json()
    errors = list(profile_validator.iter_errors(profile))
    assert errors == [], [error.message for error in errors]


def test_s1_every_provenance_ref_resolves_no_dangling(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    profile = client.get("/api/v1/properties/1000010100").json()
    provenance_ids = {record["provenance_id"] for record in profile["provenance"]}
    refs = [value["provenance_ref"] for value in all_fact_values(profile)]
    assert refs, "profile emitted no fact values"
    assert set(refs) <= provenance_ids  # no dangling refs (PRD sections 9/19)


def test_s1_coverage_present_never_verified_never_from_confidence(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    profile = client.get("/api/v1/properties/1000010100").json()
    values = all_fact_values(profile)
    assert values
    for value in values:
        assert value["coverage_status"] in UNREVIEWED_ALLOWED_COVERAGE
    # Confidence is 1.0 on every deterministic connector fact, yet coverage
    # stays 'conditional' - proof the two axes are independent (PRD 12).
    assert all(record["confidence"] == 1.0 for record in profile["provenance"])
    assert profile["lot_facts"]["lotarea"]["coverage_status"] == "conditional"
    assert profile["reproducibility"]["coverage_policy"].startswith("coverage_status")


def test_s1_profile_version_and_reproducibility_metadata(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    profile = client.get("/api/v1/properties/1000010100").json()
    version = profile["profile_version"]
    assert version["contract_version"] == "1.0.0"
    assert version["profile_revision"] == 1
    assert version["generated_at"].endswith("Z")
    repro = profile["reproducibility"]
    assert repro["source_id"] == SOURCE_ID
    assert repro["dataset_id"] == "64uk-42ks"
    assert repro["dataset_version"] == "26v1"
    assert repro["request_url"].endswith("?bbl=1000010100")
    assert repro["retrieved_at"] == "2026-07-16T12:00:00Z"
    assert repro["record_count"] == 1
    assert repro["correlation_id"]


def test_s1_fact_placement_and_values(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    profile = client.get("/api/v1/properties/1000010100").json()
    lotarea = profile["lot_facts"]["lotarea"]
    assert lotarea["value"] == 23121
    assert lotarea["units"] == "square feet"
    backing = {r["provenance_id"]: r for r in profile["provenance"]}
    assert backing[lotarea["provenance_ref"]]["original_value"] == "23121"
    assert profile["identity"]["bbl"] == "1000010100"
    assert profile["zoning"]["districts"] == ["R3-2"]
    assert profile["zoning"]["special_districts"] == ["GI"]
    assert profile["zoning"]["commercial_overlays"] == []
    features = {f["feature"] for f in profile["zoning"]["mapped_features"]}
    assert "splitzone" in features
    # Unitless FAR facts stay informational building facts, no units key.
    # (F01 live capture: builtfar raw "0.43000000000" -> 0.43.)
    assert profile["existing_building_facts"]["builtfar"]["value"] == 0.43
    assert "units" not in profile["existing_building_facts"]["builtfar"]


# --------------------------------------------------------------------------
# S2 - boundary: input forms, borough bounds, documented OpenAPI semantics
# --------------------------------------------------------------------------


def test_s2_decimal_serialized_path_input_normalizes_to_canonical(client) -> None:
    harness = fixture_fetcher("F01_single_lot_normal.json")
    response = client.get("/api/v1/properties/1000010100.00000000")
    assert response.status_code == 200
    profile = response.json()
    assert profile["identity"]["bbl"] == "1000010100"
    # The connector was called with the canonical form only.
    assert harness.calls[0][0] == "1000010100"
    assert harness.transports[0].calls[0]["url"].endswith("?bbl=1000010100")
    # Raw record-level serialization is preserved verbatim in provenance.
    bbl_fact = next(
        r for r in profile["provenance"] if r["original_field_name"] == "bbl"
    )
    assert bbl_fact["original_value"] == "1000010100.00000000"
    assert profile["lot_facts"]["bbl"]["value"] == "1000010100"


@pytest.mark.parametrize(
    ("bbl", "expected_code"),
    [
        ("0000010100", "invalid_borough"),
        ("6000010100", "invalid_borough"),
        ("100001010", "wrong_length"),
        ("1000010100.5", "non_integer_decimal"),
        ("abc", "non_numeric"),
        ("1-00001-0100", "non_numeric"),  # component form not accepted here
    ],
)
def test_s2_malformed_bbl_422_typed_and_no_connector_call(
    client, bbl, expected_code
) -> None:
    def must_not_be_called(bbl_arg, correlation_id):
        raise AssertionError("connector must not be called for malformed BBL")

    install_fetcher(must_not_be_called)
    response = client.get(f"/api/v1/properties/{bbl}")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["detail"]["code"] == expected_code
    assert body["correlation_id"]


def test_s2_borough_bounds_1_and_5_are_consistent(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    assert client.get("/api/v1/properties/1000010100").status_code == 200
    fixture_fetcher("F03b_no_match_valid_bbl.json")
    response = client.get("/api/v1/properties/5999999999")
    # Borough 5 is valid input; nonexistence is a 404 no_match result.
    assert response.status_code == 404
    assert response.json()["state"] == "no_match"


def test_s2_openapi_documents_response_semantics(client) -> None:
    spec = client.get("/openapi.json").json()
    responses = spec["paths"]["/api/v1/properties/{bbl}"]["get"]["responses"]
    assert {"200", "404", "422", "500", "502", "503", "504"} <= set(responses)
    assert "no_match" in responses["404"]["description"]
    assert "validation_error" in responses["422"]["description"]
    assert "schema_drift" in responses["502"]["description"]


# --------------------------------------------------------------------------
# S3 - missing: explicit no_match; absent columns never fabricated
# --------------------------------------------------------------------------


def test_s3_valid_nonexistent_bbl_is_404_with_machine_readable_state(client) -> None:
    fixture_fetcher("F03b_no_match_valid_bbl.json")
    response = client.get("/api/v1/properties/5999999999")
    assert response.status_code == 404
    body = response.json()
    assert body["state"] == "no_match"
    assert body["bbl"] == "5999999999"
    assert "No PLUTO record" in body["message"]
    assert body["source_id"] == SOURCE_ID
    assert body["dataset_id"] == "64uk-42ks"
    assert body["correlation_id"]
    assert body["retrieved_at"] == "2026-07-16T12:00:00Z"


def test_s3_condo_unit_lot_404_includes_billing_lot_explanation(client) -> None:
    fixture_fetcher("F02b_condo_unit_lot_no_match.json")
    response = client.get("/api/v1/properties/1000041001")
    assert response.status_code == 404
    body = response.json()
    assert body["state"] == "no_match"
    assert "BILLING lot" in body["message"]
    assert "7501-7599" in body["message"]


def test_s3_absent_columns_surface_as_missing_inputs_never_fabricated(client) -> None:
    fixture_fetcher("F04_null_field_omission.json")
    response = client.get("/api/v1/properties/1000010101")
    assert response.status_code == 200
    profile = response.json()
    # F04: numfloors omitted while numbldgs=10 -> dictionary p.28 'not
    # available'. The fact must NOT exist; the gap must be explicit.
    assert "numfloors" not in profile["existing_building_facts"]
    missing = {entry["field"]: entry for entry in profile["missing_inputs"]}
    assert "numfloors" in missing
    assert missing["numfloors"]["reason"].startswith("numfloors_not_available")
    assert missing["numfloors"]["criticality"] == "noncritical"
    assert profile["data_completeness"] in {"missing_noncritical", "missing_critical"}
    # Every absent column is stated, never silently dropped.
    absent = set(profile["reproducibility"]["connector_notes"])  # notes persisted
    assert any(note.startswith("numfloors_not_available") for note in absent)


def test_s3_missing_critical_column_flags_completeness(client) -> None:
    # SYNTHETIC variant: drop lotarea (a critical completeness column).
    def drop_lotarea(record):
        record.pop("lotarea", None)

    synthetic_record_fetcher(drop_lotarea)
    profile = client.get("/api/v1/properties/1000010100").json()
    assert "lotarea" not in profile["lot_facts"]
    missing = {entry["field"]: entry for entry in profile["missing_inputs"]}
    assert missing["lotarea"]["criticality"] == "critical"
    assert profile["data_completeness"] == "missing_critical"


# --------------------------------------------------------------------------
# S4 - conflict: visible, data_conflict coverage, never silently resolved
# --------------------------------------------------------------------------


def test_s4_borocode_conflict_visible_and_marked_data_conflict(client) -> None:
    # SYNTHETIC variant of F01: borocode disagrees with the BBL digits.
    def conflicting_borocode(record):
        record["borocode"] = "3"

    synthetic_record_fetcher(conflicting_borocode)
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 200  # conflicts are results, not errors
    profile = response.json()
    conflicts = profile["conflicts"]
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict["field"] == "borocode"
    assert conflict["resolution"] == "unresolved"
    values = {json.dumps(v["value"]) for v in conflict["values"]}
    assert values == {"1", '"3"'}  # both values verbatim, nothing resolved
    # Affected facts carry data_conflict coverage; unaffected facts do not.
    assert profile["lot_facts"]["borocode"]["coverage_status"] == "data_conflict"
    assert profile["lot_facts"]["bbl"]["coverage_status"] == "data_conflict"
    assert profile["lot_facts"]["lotarea"]["coverage_status"] == "conditional"


def test_s4_identity_never_derived_from_conflicting_borocode(client) -> None:
    def conflicting_borocode(record):
        record["borocode"] = "3"

    synthetic_record_fetcher(conflicting_borocode)
    profile = client.get("/api/v1/properties/1000010100").json()
    address = profile["identity"].get("address", {})
    # Brooklyn must NOT be silently asserted for a Manhattan BBL.
    assert "borough" not in address
    assert "borough_code" not in address
    assert profile["identity"]["bbl"] == "1000010100"


# --------------------------------------------------------------------------
# S5 - failure: typed states, documented statuses, no internals leak
# --------------------------------------------------------------------------


def scripted_fetcher(script_factory, **fetch_kwargs) -> FetcherHarness:
    harness = FetcherHarness(script_factory, **fetch_kwargs)
    install_fetcher(harness)
    return harness


def test_s5_rate_limited_maps_to_503_typed(client) -> None:
    scripted_fetcher(lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3)
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "rate_limited"
    assert body["source_id"] == SOURCE_ID
    assert body["correlation_id"]


def test_s5_timeout_maps_to_504_typed(client) -> None:
    scripted_fetcher(lambda: [TransportTimeout("timeout after 10.0s")] * 3)
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 504
    assert response.json()["state"] == "timeout"


def test_s5_source_unavailable_maps_to_503_typed(client) -> None:
    scripted_fetcher(lambda: [TransportFailure("network failure: OSError")] * 3)
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 503
    assert response.json()["state"] == "source_unavailable"


def test_s5_schema_drift_maps_to_distinct_502_state(client) -> None:
    scripted_fetcher(lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")])
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 502  # distinct from 503/504 outage classes
    body = response.json()
    assert body["state"] == "schema_drift"
    assert body["detail"]["error_code"] == "query.soql.no-such-column"


def test_s5_error_responses_never_leak_token_or_stack_trace(
    client, monkeypatch
) -> None:
    canary = "canary-app-token-9x7"  # secretscan:allow fake token, leak-absence test
    monkeypatch.setenv("SOCRATA_APP_TOKEN", canary)
    scripts = [
        lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3,
        lambda: [TransportTimeout("timeout after 10.0s")] * 3,
        lambda: [TransportFailure("network failure: OSError")] * 3,
        lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")],
    ]
    for script in scripts:
        scripted_fetcher(script)
        response = client.get("/api/v1/properties/1000010100")
        assert response.status_code in {502, 503, 504}
        text = response.text
        assert canary not in text
        assert "X-App-Token" not in text
        assert "Traceback" not in text
        assert 'File "' not in text


def test_s5_unexpected_exception_is_500_generic_no_internals(client) -> None:
    class HostileError(RuntimeError):
        pass

    def exploding_fetcher(bbl, correlation_id):
        raise HostileError("internal secret path C:\\hostile\r\n::injected")

    install_fetcher(exploding_fetcher)
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_error"
    assert body["correlation_id"]
    assert "hostile" not in response.text
    assert "Traceback" not in response.text


# --------------------------------------------------------------------------
# S6 - retry/idempotency: identical documents modulo volatile identifiers
# --------------------------------------------------------------------------


def test_s6_same_bbl_twice_yields_identical_profiles_modulo_volatile(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    first = client.get("/api/v1/properties/1000010100").json()
    second = client.get("/api/v1/properties/1000010100").json()

    def strip_volatile(profile: dict) -> dict:
        profile["profile_version"].pop("generated_at")
        profile["reproducibility"].pop("correlation_id")
        return profile

    # json.dumps compares structure AND key ordering (stable output).
    assert json.dumps(strip_volatile(first)) == json.dumps(strip_volatile(second))


def test_s6_provenance_ids_are_deterministic(client) -> None:
    fixture_fetcher("F01_single_lot_normal.json")
    first = client.get("/api/v1/properties/1000010100").json()
    second = client.get("/api/v1/properties/1000010100").json()
    ids_first = [record["provenance_id"] for record in first["provenance"]]
    ids_second = [record["provenance_id"] for record in second["provenance"]]
    assert ids_first == ids_second
    assert len(ids_first) == len(set(ids_first))


# --------------------------------------------------------------------------
# S7 - security hardening (M1-T002 G5 findings F1-F4)
# --------------------------------------------------------------------------


class _FakeUrlopenResponse:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self, amt: int | None = None) -> bytes:
        if amt is None:
            return self._body
        return self._body[:amt]

    def __enter__(self):
        return self

    def __exit__(self, *exc_info) -> bool:
        return False


class _FakeOpener:
    def __init__(self, fn):
        self._fn = fn

    def open(self, request, timeout=None):
        return self._fn(request, timeout=timeout)


def test_s7_f1_oversized_200_body_is_refused_bounded_read(monkeypatch) -> None:
    oversized = b"x" * (MAX_RESPONSE_BYTES + 10)

    def fake_open(request, timeout=None):
        return _FakeUrlopenResponse(200, oversized)

    monkeypatch.setattr(pluto_soda, "_OPENER", _FakeOpener(fake_open))
    with pytest.raises(TransportFailure) as excinfo:
        urllib_transport("https://data.cityofnewyork.us/resource/64uk-42ks.json", {}, 10.0)
    assert "exceeded" in str(excinfo.value)
    assert str(MAX_RESPONSE_BYTES) in str(excinfo.value)


def test_s7_f1_oversized_error_body_is_refused_bounded_read(monkeypatch) -> None:
    oversized = b"x" * (MAX_RESPONSE_BYTES + 10)

    def fake_open(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 400, "Bad Request", None, io.BytesIO(oversized)
        )

    monkeypatch.setattr(pluto_soda, "_OPENER", _FakeOpener(fake_open))
    with pytest.raises(TransportFailure):
        urllib_transport("https://data.cityofnewyork.us/resource/64uk-42ks.json", {}, 10.0)


def test_s7_f2_hostile_deeply_nested_json_is_typed_error(client) -> None:
    hostile_body = "[" * 100_000
    scripted_fetcher(lambda: [TransportResponse(200, hostile_body)])
    response = client.get("/api/v1/properties/1000010100")
    # Typed source_unavailable - never a raw RecursionError/stack escape.
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "source_unavailable"
    assert body["detail"]["parse_error"] == "RecursionError"


def test_s7_f2_hostile_deeply_nested_400_body_classifies_as_unparseable() -> None:
    hostile_body = "[" * 100_000
    transport = FakeTransport([TransportResponse(400, hostile_body)])
    with pytest.raises(SourceUnavailableError) as excinfo:
        fetch_by_bbl(
            "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
        )
    assert excinfo.value.detail["error_code"] is None  # unparseable, not drift


def test_s7_f3_redirect_handler_refuses_all_redirects() -> None:
    handler = pluto_soda._NoRedirectHandler()
    request = urllib.request.Request(
        "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000010100",
        headers={"X-App-Token": "canary-token"},  # secretscan:allow fake, refusal test
    )
    refused = handler.redirect_request(
        request, io.BytesIO(b""), 302, "Found", {}, "https://evil.example/collect"
    )
    assert refused is None  # None => urllib raises HTTPError; no re-request


def test_s7_f3_opener_has_only_the_no_redirect_handler() -> None:
    redirect_handlers = [
        h for h in pluto_soda._OPENER.handlers
        if isinstance(h, urllib.request.HTTPRedirectHandler)
    ]
    assert redirect_handlers, "opener must carry the refusing redirect handler"
    assert all(
        isinstance(h, pluto_soda._NoRedirectHandler) for h in redirect_handlers
    )


def test_s7_f3_refused_redirect_surfaces_as_typed_error_single_call(client) -> None:
    # A refused 3xx reaches the connector as a plain status (via HTTPError
    # pass-through) and must map to a typed error after exactly one request:
    # the token never follows any redirect.
    harness = scripted_fetcher(
        lambda: [TransportResponse(302, "")],
    )
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "source_unavailable"
    assert body["detail"]["http_status"] == 302
    assert len(harness.transports[0].calls) == 1  # never re-issued


def test_s7_f4_hostile_errorcode_is_sanitized_in_detail(client) -> None:
    hostile = json.dumps({"errorCode": "bad\r\ncode ::injected", "message": "x"})
    scripted_fetcher(lambda: [TransportResponse(400, hostile)])
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 503
    error_code = response.json()["detail"]["error_code"]
    assert "\r" not in error_code and "\n" not in error_code
    assert error_code == repr("bad\r\ncode ::injected")


def test_s7_f4_official_errorcode_passes_verbatim(client) -> None:
    scripted_fetcher(lambda: [fixture_response("F13b_non_drift_400_type_mismatch.json")])
    response = client.get("/api/v1/properties/1000010100")
    assert response.status_code == 503
    assert response.json()["detail"]["error_code"] == "query.soql.type-mismatch"


# --------------------------------------------------------------------------
# S8 - regression: health endpoint still mounted; builder guard
# --------------------------------------------------------------------------


def test_s8_health_endpoint_unaffected_by_router_mount(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_builder_rejects_non_ok_results() -> None:
    transport = FakeTransport([fixture_response("F03b_no_match_valid_bbl.json")])
    result = fetch_by_bbl(
        "5999999999", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert result.status == "no_match"
    with pytest.raises(ValueError, match="status='ok'"):
        build_property_profile(result)
