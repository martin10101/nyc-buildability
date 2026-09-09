"""Internal scenario OPTIMIZATION-TOOLKIT endpoint acceptance pack (task M5-T012, AS-1..AS-8).

Offline and deterministic. The four analysis routes' PLUTO fetcher and server-side spatial
substrate provider are both overridden via FastAPI dependency injection with the accepted
recorded-official PLUTO fixtures (services/api/tests/fixtures/pluto) and faithful M2-T013
substrate dicts - the SAME harness the accepted scenario / rule-evaluation endpoint tests use -
so NO test touches the network, Supabase, or Geoclient (AS-7). Each endpoint rebuilds the
profile, its rule_evaluation, and the scenario document SERVER-SIDE over those seams and calls
the corresponding accepted engine function READ-ONLY through the public app.scenario facade.

Coverage of the acceptance scenarios:

* AS-1 four analysis endpoints over server-rebuilt facts -> 200 envelope carrying the verbatim
  canonical cap and the engine's typed result.
* AS-2 untrusted-input boundary: a body that supplies/overrides a FACT is a typed 422; the cap
  echoed in a legitimate response is the server-rebuilt canonical one, verbatim.
* AS-3 flag-gated fail-safe: flag off/unknown -> generic 404 indistinguishable from an unmounted
  path; never in the OpenAPI document; the existing config flag is reused.
* AS-4 documented STATUS_STATE_MATRIX == the accepted scenario route's matrix; honest non-errors
  are NORMAL 200 typed results; X-Correlation-ID present; no internals leak.
* AS-5 bounded input: every cap is a typed 422; deeply-nested / oversized / malformed bodies are
  a typed 422, never a RecursionError / hang / unhandled raise; no NaN/Inf reaches a response.
* AS-6 strict-JSON-safe + never Verified: every 200 body survives json.dumps(allow_nan=False);
  NOT_VERIFIED_DISCLAIMER present; nothing Verified; no object-address leak.
* AS-7 additive registration + offline + facade-only engine calls.
* AS-8 exercised by the full api + scenario suites staying green (run separately).
"""

from __future__ import annotations

import json
import socket
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import scenario_analysis as analysis_module
from app.api.v1.properties import STATUS_STATE_MATRIX as PROPERTY_MATRIX
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.api.v1.scenario import STATUS_STATE_MATRIX as SCENARIO_MATRIX
from app.api.v1.scenario_analysis import (
    MAX_ASSUMPTION_SETS,
    MAX_ASSUMPTIONS_PER_SET,
    MAX_BODY_BYTES,
    MAX_CANDIDATE_DOMAIN_LENGTH,
    STATUS_STATE_MATRIX,
)
from app.config import (
    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
    INTERNAL_SCENARIO_ENABLED_ENV_VAR,
)
from app.connectors.pluto_soda import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.scenario import NOT_VERIFIED_DISCLAIMER
from app.scenario.contract import ScenarioContractError

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"

# The confident-R5 fixture + substrate yield this canonical draft cap VERBATIM from the trace
# (the value the accepted scenario route surfaces in test_scenario_api.py AS-1).
TRACE_CAP = 15000.0


# --------------------------------------------------------------------------
# Fetcher + substrate override plumbing (fixture-transport, offline) - mirrors
# tests/api/test_scenario_api.py so all internal routes share one offline harness.
# --------------------------------------------------------------------------


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


class FakeTransport:
    def __init__(self, script: list):
        self.script = list(script)

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        if not self.script:
            raise AssertionError("FakeTransport script exhausted")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def _fetcher(script_factory):
    def fetch(bbl: str, correlation_id: str):
        return fetch_by_bbl(
            bbl,
            transport=FakeTransport(script_factory()),
            sleep=lambda s: None,
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
        )

    return fetch


def install_fetcher(script_factory) -> None:
    app.dependency_overrides[get_pluto_fetcher] = lambda: _fetcher(script_factory)


def install_substrate(substrate) -> None:
    app.dependency_overrides[get_spatial_substrate_provider] = (
        lambda: (lambda canonical_bbl, correlation_id: substrate)
    )


def install_landmine_seams() -> None:
    """Override BOTH injected seams with providers whose returned callables raise if ever
    invoked, so a request that returns before any I/O cannot silently perform a fetch."""

    def _landmine_fetcher_provider():
        def fetch(bbl: str, correlation_id: str):
            raise AssertionError("PLUTO fetcher must not be invoked for this request")

        return fetch

    def _landmine_substrate_provider():
        def provide(canonical_bbl: str, correlation_id: str):
            raise AssertionError("substrate provider must not be invoked for this request")

        return provide

    app.dependency_overrides[get_pluto_fetcher] = _landmine_fetcher_provider
    app.dependency_overrides[get_spatial_substrate_provider] = _landmine_substrate_provider


def enable_flag(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")


def install_confident(fixture: str = "F01_single_lot_normal.json") -> None:
    install_fetcher(lambda: [fixture_response(fixture)])
    install_substrate(confident_r5_substrate())


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


# --------------------------------------------------------------------------
# Faithful M2-T013 substrate dicts (mirrors tests/api/test_scenario_api.py).
# --------------------------------------------------------------------------


def _pair(label: str, pair_class: str, *, lot_area=10000.0, share=(1.0, 1.0, 1.0), minor=False):
    smin, spoint, smax = share
    return {
        "layer": "nyzd",
        "family": "base_zoning",
        "district_label": label,
        "pair_class": pair_class,
        "raw_intersection_sq_ft": lot_area * spoint,
        "firm_intersection_sq_ft": lot_area * spoint,
        "dilated_intersection_sq_ft": lot_area * smax,
        "distance_ft": 0.0,
        "lot_area_sq_ft": lot_area,
        "share_min": smin,
        "share_point": spoint,
        "share_max": smax,
        "minor_portion": minor,
    }


def _substrate(lot_overall_class: str, pairs: list, *, review: bool, review_reasons=None):
    return {
        "bbl": BBL,
        "lot_overall_class": lot_overall_class,
        "pairs": pairs,
        "coverage_audits": [{"family": "base_zoning", "status": "unknown"}],
        "crosscheck": None,
        "professional_review_required": review,
        "review_reasons": review_reasons or [],
        "unassigned_area": [],
        "overlap_area": [],
        "accuracy_records": [{"applies_to": "lot", "value_ft": 20.0, "basis": "documented"}],
        "policy": {"version": "policy-1"},
        "provenance": {
            "source_id": "nyc-dcp-mappluto-arcgis",
            "requested_bbl": BBL,
            "retrieved_at": "2026-07-16T12:00:00Z",
            "normalized_digest": "sha256:" + "e" * 64,
            "source_data_last_edited": "2026-07-15T00:00:00Z",
        },
        "coverage_note": "facts_with_uncertainty; not a Verified zoning determination",
        "notes": [],
    }


def confident_r5_substrate(area: float = 10000.0):
    return _substrate(
        "single_district_confident",
        [_pair("R5", "interior_confident", lot_area=area)],
        review=False,
    )


def split_lot_substrate():
    return _substrate(
        "split_lot_confident",
        [
            _pair("R5", "split_confident", share=(0.55, 0.60, 0.65)),
            _pair("R6", "split_confident", share=(0.35, 0.40, 0.45)),
        ],
        review=True,
        review_reasons=["lot_overall_class=split_lot_confident"],
    )


# --------------------------------------------------------------------------
# Endpoint table + valid illustrative bodies (assumptions only, never facts).
# --------------------------------------------------------------------------


def _assumption(factor: str, value):
    return {
        "key": factor,
        "assumption_type": factor,
        "value": value,
        "unit": "ratio",
        "rationale": "test what-if factor",
    }


def url(analysis: str, bbl: str = BBL) -> str:
    return f"/api/v1/properties/{bbl}/scenario/{analysis}"


SENSITIVITY_BODY = {"variable": "utilization_factor", "values": [0.5, 0.8, 1.0]}
RANKING_BODY = {
    "objective": "maximize_illustrative_usable_area",
    "assumption_sets": [
        [_assumption("utilization_factor", 0.9)],
        [_assumption("utilization_factor", 0.5)],
    ],
}
COMPARISON_BODY = {
    "assumption_sets": [
        {"name": "baseline", "assumptions": []},
        {"name": "reduced", "assumptions": [_assumption("utilization_factor", 0.7)]},
    ],
}
THRESHOLD_BODY = {
    "variable": "utilization_factor",
    "target": 10000,
    "domain": [0.5, 0.7, 0.9, 1.0],
    "response_metric": "usable_range_point",
}

# (analysis, valid body, result kind-field, expected kind for the confident scenario).
ENDPOINTS = [
    ("sensitivity", SENSITIVITY_BODY, "sensitivity_kind", "sensitivity_response"),
    ("ranking", RANKING_BODY, "ranking_kind", "ranked_scenario_assumption_sets"),
    ("comparison", COMPARISON_BODY, "comparison_kind", "scenario_assumption_set_comparison"),
    ("threshold", THRESHOLD_BODY, "threshold_kind", "scenario_threshold_crossing"),
]

BODIES = {analysis: body for analysis, body, _, _ in ENDPOINTS}

# The typed EMPTY kind each engine emits when the scenario surfaces no positive cap.
EMPTY_KINDS = {
    "sensitivity": ("sensitivity_kind", "empty_no_analyzable_cap"),
    "ranking": ("ranking_kind", "empty_no_rankable_cap"),
    "comparison": ("comparison_kind", "empty_no_comparable_cap"),
    "threshold": ("threshold_kind", "empty_no_analyzable_cap"),
}


def _coverage_values(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                yield value
            yield from _coverage_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _coverage_values(item)


# ==========================================================================
# AS-1 - four analysis endpoints over server-rebuilt facts.
# ==========================================================================


@pytest.mark.parametrize(("analysis", "body", "kind_field", "kind"), ENDPOINTS)
def test_as1_endpoint_returns_engine_result_envelope(
    client, monkeypatch, analysis, body, kind_field, kind
):
    enable_flag(monkeypatch)
    install_confident()

    response = client.post(url(analysis), json=body)
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    envelope = response.json()

    # Thin envelope shape; the engine result is carried verbatim.
    assert envelope["analysis"] == analysis
    assert envelope["bbl"] == BBL
    result = envelope["result"]
    assert result[kind_field] == kind

    # The cap is the SERVER-rebuilt canonical value, transported VERBATIM (never recomputed).
    assert envelope["scenario_cap_sq_ft"] == TRACE_CAP
    assert envelope["scenario_kind"] == "preliminary"
    assert envelope["coverage_status"] == "conditional"
    # Never Verified; the canonical disclaimer is present.
    assert envelope["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert "verified" not in set(_coverage_values(envelope))


def test_as1_cap_equals_rule_evaluation_trace_value_verbatim(client, monkeypatch):
    # Prove the envelope cap is the trace value read back through the mirrored
    # rule-evaluation route over the identical inputs (never a local recomputation).
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")

    install_confident()
    envelope = client.post(url("sensitivity"), json=SENSITIVITY_BODY).json()

    install_confident()
    rule_eval = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()
    trace_cap = rule_eval["evaluations"][0]["outputs"]["max_residential_floor_area_sq_ft"]
    assert envelope["scenario_cap_sq_ft"] == trace_cap == TRACE_CAP


# ==========================================================================
# AS-2 - untrusted-input boundary: assumptions yes, FACTS never.
# ==========================================================================


@pytest.mark.parametrize(
    "fact_key",
    [
        "property_profile",
        "rule_evaluation",
        "scenario",
        "scenario_document",
        "draft_zoning_floor_area_cap_sq_ft",
        "max_residential_floor_area_sq_ft",
        "cap",
        "coverage_status",
        "verified",
        "verification_status",
        "constraints",
    ],
)
def test_as2_fact_injecting_body_is_typed_422(client, monkeypatch, fact_key):
    enable_flag(monkeypatch)
    # Landmine seams: a fact-injecting body must be rejected BEFORE any fetch/rebuild.
    install_landmine_seams()

    body = {"variable": "utilization_factor", "values": [0.8], fact_key: 999999}
    response = client.post(url("sensitivity"), json=body)
    assert response.status_code == 422
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert fact_key in payload["detail"]["rejected_keys"]
    assert response.headers["x-correlation-id"]


def test_as2_injected_cap_cannot_change_the_echoed_cap(client, monkeypatch):
    enable_flag(monkeypatch)

    # (a) An attempt to inject the cap is rejected outright.
    install_landmine_seams()
    injected = client.post(
        url("sensitivity"),
        json={"variable": "utilization_factor", "draft_zoning_floor_area_cap_sq_ft": 10**9},
    )
    assert injected.status_code == 422

    # (b) A legitimate request echoes the SERVER-rebuilt canonical cap, verbatim.
    install_confident()
    envelope = client.post(url("sensitivity"), json=SENSITIVITY_BODY).json()
    assert envelope["scenario_cap_sq_ft"] == TRACE_CAP


# ==========================================================================
# AS-3 - flag-gated fail-safe, no OpenAPI leak.
# ==========================================================================


@pytest.mark.parametrize("analysis", ["sensitivity", "ranking", "comparison", "threshold"])
@pytest.mark.parametrize("flag_value", [None, "", "0", "false", "off", "maybe", "2", "  "])
def test_as3_flag_off_or_unknown_is_generic_404(client, monkeypatch, analysis, flag_value):
    if flag_value is None:
        monkeypatch.delenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, flag_value)
    install_landmine_seams()

    response = client.post(url(analysis), json=SENSITIVITY_BODY)
    assert response.status_code == 404
    # Byte-indistinguishable from an unmounted path: only {"detail": "Not Found"}.
    assert response.json() == {"detail": "Not Found"}
    text = response.text.lower()
    assert "scenario" not in text and "flag" not in text
    assert "x-correlation-id" not in {k.lower() for k in response.headers}


def test_as3_openapi_never_lists_any_analysis_route(client, monkeypatch):
    enable_flag(monkeypatch)
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    for analysis in ("sensitivity", "ranking", "comparison", "threshold"):
        assert f"/api/v1/properties/{{bbl}}/scenario/{analysis}" not in paths
    assert "/api/v1/properties/{bbl}" in paths  # the existing route is unaffected


# ==========================================================================
# AS-4 - documented status/state matrix + honest non-errors.
# ==========================================================================


def test_as4_matrix_equals_scenario_route_matrix():
    # Single source of truth EQUALS the accepted scenario route's matrix, and equals the
    # property route's matrix minus the (500, unsupported_contract_version) pair the rebuild
    # path collapses into the shared (500, internal_contract_error). No new pair is introduced.
    assert STATUS_STATE_MATRIX == SCENARIO_MATRIX
    version_pair = (500, "unsupported_contract_version")
    assert STATUS_STATE_MATRIX == PROPERTY_MATRIX - {version_pair}
    assert version_pair not in STATUS_STATE_MATRIX


@pytest.mark.parametrize("analysis", ["sensitivity", "ranking", "comparison", "threshold"])
def test_as4_no_scenario_is_a_normal_200_typed_result(client, monkeypatch, analysis):
    # A professional-review no_scenario outcome is a NORMAL 200 typed EMPTY result, never an
    # error (the property stays usable). The cap is None and nothing is Verified.
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(split_lot_substrate())

    body = dict(ENDPOINTS[["sensitivity", "ranking", "comparison", "threshold"].index(analysis)][1])
    response = client.post(url(analysis), json=body)
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["scenario_cap_sq_ft"] is None
    assert envelope["scenario_kind"] == "no_scenario"
    kind_field, empty_kind = EMPTY_KINDS[analysis]
    assert envelope["result"][kind_field] == empty_kind


def test_as4_every_emitted_pair_is_in_the_matrix(client, raw_client, monkeypatch):
    enable_flag(monkeypatch)
    emitted: set[tuple[int, str | None]] = set()

    def record(response):
        state = None if response.status_code == 200 else response.json().get("state")
        emitted.add((response.status_code, state))

    # 200 valid + 200 no_scenario (both NORMAL 200 / no state).
    install_confident()
    record(client.post(url("sensitivity"), json=SENSITIVITY_BODY))
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(split_lot_substrate())
    record(client.post(url("ranking"), json=RANKING_BODY))

    # 422 malformed BBL (no connector call) + 422 malformed body (same pair).
    install_landmine_seams()
    record(client.post(url("sensitivity", bbl="abc"), json=SENSITIVITY_BODY))
    install_landmine_seams()
    record(client.post(url("sensitivity"), json={"scenario": {}}))

    # 404 no_match.
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    record(client.post(url("sensitivity", bbl="5999999999"), json=SENSITIVITY_BODY))

    # 504 timeout, 503 source_unavailable, 502 schema_drift, 503 rate_limited.
    for script, expected in (
        (lambda: [TransportTimeout("t")] * 3, 504),
        (lambda: [TransportFailure("f")] * 3, 503),
        (lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")], 502),
        (lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3, 503),
    ):
        install_fetcher(script)
        install_substrate(confident_r5_substrate())
        resp = client.post(url("sensitivity"), json=SENSITIVITY_BODY)
        assert resp.status_code == expected
        record(resp)

    # 500 internal_contract_error: the rebuilt scenario fails its canonical-contract validation.
    install_confident()
    monkeypatch.setattr(
        analysis_module,
        "validate_scenario_document",
        lambda doc: (_ for _ in ()).throw(
            ScenarioContractError("forced scenario contract defect", location="<root>")
        ),
    )
    record(raw_client.post(url("sensitivity"), json=SENSITIVITY_BODY))

    # 500 internal_error: any unexpected exception in the build stage -> the generic pair.
    install_confident()
    monkeypatch.setattr(
        analysis_module,
        "build_property_profile",
        lambda result, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    record(raw_client.post(url("sensitivity"), json=SENSITIVITY_BODY))

    # Every emitted pair is documented AND the whole documented matrix was driven.
    assert emitted == STATUS_STATE_MATRIX


def test_as4_internal_defect_leaks_nothing(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_confident()

    def exploding_builder(result, **kwargs):
        raise RuntimeError("secret-internal-path C:\\hostile\r\n::injected")

    monkeypatch.setattr(analysis_module, "build_property_profile", exploding_builder)
    response = raw_client.post(url("threshold"), json=THRESHOLD_BODY)
    assert response.status_code == 500
    assert response.headers.get("X-Correlation-ID")
    body = response.json()
    assert body["state"] == "internal_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


# ==========================================================================
# AS-5 - bounded input, fail-closed at the untrusted edge.
# ==========================================================================


def _post_raw(client, analysis, content):
    return client.post(
        url(analysis), content=content, headers={"content-type": "application/json"}
    )


def test_as5_oversized_body_is_typed_422(client, monkeypatch):
    enable_flag(monkeypatch)
    install_landmine_seams()
    content = '{"variable": "utilization_factor", "note": "' + "x" * (MAX_BODY_BYTES + 10) + '"}'
    response = _post_raw(client, "sensitivity", content)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


@pytest.mark.parametrize("levels", [40, 600])
def test_as5_deeply_nested_body_is_typed_422_never_recursionerror(client, monkeypatch, levels):
    # A body nested far past MAX_NESTING_DEPTH (including >=500 levels) is a typed 422 - never a
    # RecursionError, hang, or 500 - whether json.loads raises or the iterative walk rejects it.
    enable_flag(monkeypatch)
    install_landmine_seams()
    nested = "[" * levels + "]" * levels
    content = '{"variable": "utilization_factor", "values": ' + nested + "}"
    response = _post_raw(client, "sensitivity", content)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_as5_oversized_string_is_typed_422(client, monkeypatch):
    enable_flag(monkeypatch)
    install_landmine_seams()
    body = {"variable": "utilization_factor", "values": ["y" * 5000]}
    response = client.post(url("sensitivity"), json=body)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


@pytest.mark.parametrize("content", ["{not valid json", "[1, 2, 3]", "42", '"a string"'])
def test_as5_malformed_or_non_object_body_is_typed_422(client, monkeypatch, content):
    enable_flag(monkeypatch)
    install_landmine_seams()
    response = _post_raw(client, "sensitivity", content)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_as5_candidate_domain_length_cap(client, monkeypatch):
    enable_flag(monkeypatch)
    install_landmine_seams()
    for analysis, key in (("sensitivity", "values"), ("threshold", "domain")):
        body = {"variable": "utilization_factor", key: [0.5] * (MAX_CANDIDATE_DOMAIN_LENGTH + 1)}
        if analysis == "threshold":
            body["target"] = 10000
        response = client.post(url(analysis), json=body)
        assert response.status_code == 422
        assert response.json()["state"] == "validation_error"


def test_as5_assumption_set_caps(client, monkeypatch):
    enable_flag(monkeypatch)
    install_landmine_seams()

    # Too many named assumption-sets.
    many = {
        "objective": "maximize_illustrative_usable_area",
        "assumption_sets": [[] for _ in range(MAX_ASSUMPTION_SETS + 1)],
    }
    assert client.post(url("ranking"), json=many).status_code == 422

    # Too many assumptions within one set.
    big_set = {
        "objective": "maximize_illustrative_usable_area",
        "assumption_sets": [
            [_assumption("utilization_factor", 0.9)] * (MAX_ASSUMPTIONS_PER_SET + 1)
        ],
    }
    assert client.post(url("ranking"), json=big_set).status_code == 422


def test_as5_nan_inf_values_never_reach_the_response(client, monkeypatch):
    # A caller can send NaN/Infinity tokens (Python's json parses them); the engine sanitizes
    # every echoed value, so the 200 body is strict-JSON-safe with no NaN/Inf and no crash.
    enable_flag(monkeypatch)
    install_confident()
    content = (
        '{"variable": "utilization_factor", '
        '"values": [NaN, Infinity, -Infinity, 1e400, 0.8]}'
    )
    response = _post_raw(client, "sensitivity", content)
    assert response.status_code == 200
    # Re-serialize strictly: must not raise, proving no NaN/Inf survived.
    json.dumps(response.json(), allow_nan=False)
    assert " at 0x" not in response.text


# ==========================================================================
# AS-6 - strict-JSON-safe + never Verified.
# ==========================================================================


@pytest.mark.parametrize(("analysis", "body", "kind_field", "kind"), ENDPOINTS)
def test_as6_response_is_strict_json_safe_and_never_verified(
    client, monkeypatch, analysis, body, kind_field, kind
):
    enable_flag(monkeypatch)
    install_confident()
    response = client.post(url(analysis), json=body)
    assert response.status_code == 200
    envelope = response.json()

    # Strict JSON safety: re-dump with allow_nan=False must not raise; no object address leak.
    json.dumps(envelope, allow_nan=False)
    assert " at 0x" not in response.text

    # Never Verified; the canonical disclaimer is present at the envelope AND in the result.
    assert envelope["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert envelope["result"]["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert envelope["coverage_status"] != "verified"
    assert "verified" not in set(_coverage_values(envelope))


# ==========================================================================
# AS-7 - additive registration + offline + facade-only engine calls.
# ==========================================================================


def test_as7_existing_routes_unaffected(client, monkeypatch):
    assert client.get("/api/v1/health").status_code == 200

    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    prop = client.get(f"/api/v1/properties/{BBL}")
    assert prop.status_code == 200
    assert prop.json()["identity"]["bbl"] == BBL

    # The accepted GET scenario route still serves under the shared flag.
    enable_flag(monkeypatch)
    install_confident()
    assert client.get(f"/api/v1/properties/{BBL}/scenario").status_code == 200


def test_as7_engine_calls_use_the_public_facade():
    import app.scenario as facade

    assert analysis_module.analyze_scenario_sensitivity is facade.analyze_scenario_sensitivity
    assert analysis_module.rank_scenario_assumption_sets is facade.rank_scenario_assumption_sets
    assert (
        analysis_module.compare_scenario_assumption_sets
        is facade.compare_scenario_assumption_sets
    )
    assert analysis_module.find_scenario_threshold is facade.find_scenario_threshold
    assert analysis_module.NOT_VERIFIED_DISCLAIMER is facade.NOT_VERIFIED_DISCLAIMER


def test_as7_full_analysis_runs_fully_offline(client, monkeypatch):
    # No credential is read and no real socket is opened: blocking socket.socket does not break
    # the in-process request, proving the analysis path touches no network / Supabase / Geoclient.
    monkeypatch.delenv("SOCRATA_APP_TOKEN", raising=False)
    enable_flag(monkeypatch)
    install_confident()

    def _no_socket(*args, **kwargs):
        raise AssertionError("network access attempted during an analysis request")

    monkeypatch.setattr(socket, "socket", _no_socket)
    response = client.post(url("comparison"), json=COMPARISON_BODY)
    assert response.status_code == 200
    assert response.json()["result"]["comparison_kind"] == "scenario_assumption_set_comparison"
