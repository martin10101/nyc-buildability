"""Internal scenario endpoint acceptance pack (task M5-T002, AS-1..AS-6, AS-10).

Offline and deterministic. The route's PLUTO fetcher and its server-side spatial
substrate provider are both overridden via FastAPI dependency injection with the
accepted recorded-official PLUTO fixtures (services/api/tests/fixtures/pluto) and
the faithful M2-T013 substrate dicts the accepted M4-T005 rule-evaluation pack
uses (the exact shape the accepted profile builder consumes), so no test touches
the network.

The endpoint rebuilds the profile SERVER-SIDE, runs the REAL deterministic rule
evaluator, and consumes the REAL app.scenario.build_scenario. No scenario body is
hand-written for the reachable paths; route, builder, evaluator, serializer, and
strict validation are the production code paths.

Coverage of the acceptance scenarios:

* AS-1 flag OFF / absent / unknown token -> generic 404, byte-indistinguishable
  from an unmounted path, no correlation id, absent from OpenAPI.
* AS-2 flag ON + recorded R5 fixture -> 200 preliminary scenario whose surfaced
  cap == the canonical rule_evaluation trace value VERBATIM (asserted against the
  independently-rebuilt trace, never recomputed), never Verified, needs_review +
  not_verified_disclaimer, X-Correlation-ID.
* AS-3 honest no-scenario families -> a NORMAL 200 typed no_scenario / unsupported
  document, never a 500 and never an invented value. The naturally-reachable
  professional-review family runs end to end through the real endpoint; the other
  families (unsupported district, conflict) are proven pass-through as 200 via a
  committed canonical scenario fixture, and the builder-only families (missing
  constraint, malformed / non-finite input) are proven honest at the real
  build_scenario boundary (the fixed R5 endpoint path can never itself emit them,
  exactly as the M4-T005 pack proves its unsupported/conflict families at the
  serializer boundary).
* AS-4 validate-before-emit + depth bound (FH-M5T001-S1/S2): an invalid assembled
  document -> typed 500 internal_contract_error; an adversarially deep document
  hits the bounded-depth guard and returns a typed 500, never RecursionError.
* AS-5 error-mapping parity: malformed BBL -> 422; upstream failures -> the same
  single-sourced status map; no_match -> 404 machine-state body; no leakage.
* AS-6 no injection surface: only the bbl path parameter; POST -> 405.
* AS-10 determinism: identical input -> byte-identical 200 body.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import scenario as scenario_module
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.config import INTERNAL_SCENARIO_ENABLED_ENV_VAR
from app.connectors.pluto_soda import (
    SOURCE_ID,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.profile.builder import build_property_profile
from app.rules.integration import evaluate_property
from app.rules.response import serialize_rule_evaluation
from app.scenario import build_scenario, validate_scenario_document

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
SCENARIO_FIXTURES = (
    REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "scenario"
)

FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"
CAP_OUTPUT_NAME = "max_residential_floor_area_sq_ft"


# --------------------------------------------------------------------------
# Fetcher + substrate override plumbing (fixture-transport, offline). Mirrors
# tests/api/test_rule_evaluation_api.py exactly so the two internal routes share
# one proven injection pattern.
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


def enable_flag(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")


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
# Faithful M2-T013 substrate dicts (identical to the M4-T005 pack).
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


def _coverage_values(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                yield value
            yield from _coverage_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _coverage_values(item)


def canonical_trace_cap() -> float:
    """Independently rebuild the rule_evaluation document via the SAME production
    path the endpoint uses and return the canonical trace cap output. Used to
    assert the surfaced value VERBATIM without ever recomputing FAR * area."""
    result = _fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])(
        BBL, "canonical-cap"
    )
    profile = build_property_profile(result, spatial_intersection=confident_r5_substrate())
    evaluation = evaluate_property(profile)
    document = serialize_rule_evaluation(
        evaluation,
        profile_contract_version=profile["profile_version"]["contract_version"],
    )
    for trace in document.get("evaluations", []):
        if trace.get("family") == "residential_far" and trace.get("applicability_outcome") is True:
            return trace["outputs"][CAP_OUTPUT_NAME]
    raise AssertionError("no residential_far trace with a cap output in the fixture path")


def load_scenario_fixture(name: str) -> dict:
    return json.loads((SCENARIO_FIXTURES / name).read_text(encoding="utf-8"))


# ==========================================================================
# AS-1 - flag OFF / absent / unknown -> generic 404, no hint; not in OpenAPI.
# ==========================================================================


@pytest.mark.parametrize("flag_value", [None, "", "0", "false", "off", "maybe", "2", "  "])
def test_as1_flag_off_or_unknown_is_generic_404(client, monkeypatch, flag_value):
    if flag_value is None:
        monkeypatch.delenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, flag_value)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 404
    # Byte-indistinguishable from an unmounted path: only {"detail": "Not Found"}.
    assert response.json() == {"detail": "Not Found"}
    text = response.text.lower()
    assert "scenario" not in text and "cap" not in text and "flag" not in text
    assert "x-correlation-id" not in {k.lower() for k in response.headers}


def test_as1_openapi_never_lists_the_internal_route(client, monkeypatch):
    # Even with the flag ON the route is include_in_schema=False -> never a hint.
    enable_flag(monkeypatch)
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/api/v1/properties/{bbl}/scenario" not in paths
    assert "/api/v1/properties/{bbl}" in paths  # the existing route is unaffected


# ==========================================================================
# AS-2 - flag ON, R5 pilot -> 200 preliminary; cap == canonical trace verbatim.
# ==========================================================================


def test_as2_happy_path_surfaces_the_canonical_cap_verbatim(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    doc = response.json()

    # Contract shape + never Verified.
    assert doc["contract_version"] == "1.0.0"
    assert doc["scenario_kind"] == "preliminary"
    assert doc["coverage_status"] == "conditional"
    assert "verified" not in set(_coverage_values(doc))

    # The surfaced cap EQUALS the canonical rule_evaluation trace value verbatim
    # (asserted against the independently-rebuilt trace, never recomputed here).
    expected_cap = canonical_trace_cap()
    assert doc["draft_zoning_floor_area_cap_sq_ft"] == expected_cap
    cap_constraint = next(c for c in doc["constraints"] if c["key"] == "residential_far_cap")
    assert cap_constraint["value"] == expected_cap
    assert cap_constraint["state"] == "draft"

    # Honest labelling: draft cap label, citations/provenance, needs_review +
    # not-verified disclaimer.
    assert doc["cap_label"] and "DRAFT" in doc["cap_label"]
    assert doc["cap_provenance"]["output_name"] == CAP_OUTPUT_NAME
    assert doc["cap_provenance"]["citations"], "cap provenance must carry citations"
    assert doc["needs_review"] is True
    assert doc["not_verified_disclaimer"]


def test_as10_response_is_deterministic(client, monkeypatch):
    enable_flag(monkeypatch)

    def once():
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(confident_r5_substrate())
        return client.get(f"/api/v1/properties/{BBL}/scenario").json()

    first, second = once(), once()
    # The body carries no volatile field (the correlation id is a header only);
    # identical inputs -> byte-identical document.
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


# ==========================================================================
# AS-3 - honest no-scenario families are NORMAL 200 documents, never errors.
# ==========================================================================


def test_as3_absent_substrate_is_200_professional_review(client, monkeypatch):
    """Real end-to-end: no substrate wired -> the evaluator fails safe and
    build_scenario emits a professional-review no_scenario document (a 200)."""
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(None)

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200
    doc = response.json()
    assert doc["scenario_kind"] == "no_scenario"
    assert doc["coverage_status"] == "professional_review_required"
    assert doc["professional_review_required"] is True
    assert doc["draft_zoning_floor_area_cap_sq_ft"] is None  # never fabricated
    assert doc["cap_label"] is None
    assert "verified" not in set(_coverage_values(doc))


def test_as3_split_lot_is_200_professional_review(client, monkeypatch):
    """Real end-to-end: a split lot -> spatial uncertainty -> professional-review
    no_scenario document (a 200), never a collapsed district or a value."""
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(split_lot_substrate())

    doc = client.get(f"/api/v1/properties/{BBL}/scenario").json()
    assert doc["scenario_kind"] == "no_scenario"
    assert doc["coverage_status"] == "professional_review_required"
    assert doc["draft_zoning_floor_area_cap_sq_ft"] is None


@pytest.mark.parametrize(
    ("fixture_name", "expected_kind", "expected_coverage"),
    [
        ("unsupported_family.json", "unsupported", "unsupported"),
        ("no_scenario_conflict.json", "no_scenario", "data_conflict"),
        ("no_scenario_professional_review.json", "no_scenario", "professional_review_required"),
    ],
)
def test_as3_no_scenario_families_pass_through_as_200(
    client, monkeypatch, fixture_name, expected_kind, expected_coverage
):
    """Pass-through proof: whatever no-scenario family the builder returns (each a
    committed canonical scenario document), the endpoint emits it as a NORMAL 200
    verbatim - never a 500 - after the depth + contract guards. The builder's own
    per-family logic is owned by the M5-T001 tests/scenario pack."""
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    fixture = load_scenario_fixture(fixture_name)
    monkeypatch.setattr(scenario_module, "build_scenario", lambda *a, **k: fixture)

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200
    doc = response.json()
    assert doc["scenario_kind"] == expected_kind
    assert doc["coverage_status"] == expected_coverage
    assert doc["draft_zoning_floor_area_cap_sq_ft"] is None
    assert "verified" not in set(_coverage_values(doc))


def test_as3_builder_missing_constraint_is_honest_no_scenario():
    """Builder-only family (the fixed R5 endpoint path can never itself emit it):
    a conditional evaluation missing its controlling trace/cap yields an honest
    no_scenario document (a valid 200-shape), never a crash or a guessed value."""
    rule_evaluation = {
        "contract_version": "1.0.0",
        "coverage_status": "conditional",
        "professional_review_required": False,
        "family_coverage": {"coverage_status": "conditional"},
        "evaluations": [],
        "lot_area_sq_ft": 10000.0,
        "zoning_district": "R5",
        "evaluated_input": {"bbl": BBL},
    }
    doc = build_scenario({"identity": {"bbl": BBL}}, rule_evaluation, assumptions=None)
    validate_scenario_document(doc)  # the endpoint's strict pre-send check
    assert doc["scenario_kind"] == "no_scenario"
    assert doc["draft_zoning_floor_area_cap_sq_ft"] is None
    assert "verified" not in set(_coverage_values(doc))


def test_as3_builder_malformed_input_is_honest_no_scenario():
    """Builder-only family: a malformed / non-finite controlling input yields an
    honest professional-review no_scenario document, never a fabricated value."""
    rule_evaluation = {
        "contract_version": "1.0.0",
        "coverage_status": "conditional",
        "professional_review_required": False,
        "family_coverage": {"coverage_status": "conditional"},
        "evaluations": [
            {
                "family": "residential_far",
                "applicability_outcome": True,
                "rule_id": "r5-residential-far",
                "rule_version": "0.1.0-draft",
                "rule_status": "needs_review",
                "outputs": {CAP_OUTPUT_NAME: "not-a-number"},
                "data_completeness": "complete",
                "citations": [],
            }
        ],
        "lot_area_sq_ft": "not-a-number",
        "zoning_district": "R5",
        "evaluated_input": {"bbl": BBL},
    }
    doc = build_scenario({"identity": {"bbl": BBL}}, rule_evaluation, assumptions=None)
    validate_scenario_document(doc)
    assert doc["scenario_kind"] == "no_scenario"
    assert doc["professional_review_required"] is True
    assert doc["draft_zoning_floor_area_cap_sq_ft"] is None


# ==========================================================================
# AS-4 - validate-before-emit + bounded-depth guard (FH-M5T001-S1/S2).
# ==========================================================================


def test_as4_invalid_document_is_typed_500_no_internals(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    # build_scenario returns a document that fails canonical validation.
    monkeypatch.setattr(
        scenario_module, "build_scenario", lambda *a, **k: {"contract_version": "1.0.0"}
    )

    response = raw_client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_contract_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


def test_as4_adversarially_deep_document_hits_bounded_depth_no_recursionerror(
    raw_client, monkeypatch
):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    # Build a document nested far past the bound (and past what json.dumps /
    # jsonschema recursion would tolerate) to prove the guard trips first.
    deep: dict = {}
    node = deep
    for _ in range(5000):
        child: dict = {}
        node["n"] = child
        node = child
    monkeypatch.setattr(scenario_module, "build_scenario", lambda *a, **k: deep)

    response = raw_client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_contract_error"
    # A typed failure, never a RecursionError / stack exhaustion surfacing.
    assert "RecursionError" not in response.text
    assert "Traceback" not in response.text


# ==========================================================================
# AS-5 - error-mapping parity; strict JSON; no internal trace/secret/path.
# ==========================================================================


@pytest.mark.parametrize(
    ("bbl", "expected_code"),
    [("abc", "non_numeric"), ("100001010", "wrong_length"), ("0000010100", "invalid_borough")],
)
def test_as5_malformed_bbl_is_typed_422_no_connector_call(client, monkeypatch, bbl, expected_code):
    enable_flag(monkeypatch)

    def must_not_call(b, c):
        raise AssertionError("connector must not be called for a malformed BBL")

    app.dependency_overrides[get_pluto_fetcher] = lambda: must_not_call
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{bbl}/scenario")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["detail"]["code"] == expected_code
    assert body["correlation_id"]


def test_as5_upstream_timeout_maps_to_504_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportTimeout("timeout after 10.0s")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 504
    assert response.json()["state"] == "timeout"


def test_as5_upstream_unavailable_maps_to_503_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportFailure("network failure: OSError")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 503
    assert response.json()["state"] == "source_unavailable"


def test_as5_schema_drift_maps_to_502_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")])
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 502
    assert response.json()["state"] == "schema_drift"


def test_as5_valid_nonexistent_bbl_is_404_no_match(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    response = client.get("/api/v1/properties/5999999999/scenario")
    assert response.status_code == 404
    body = response.json()
    assert body["state"] == "no_match"  # distinguishable from the disabled-flag 404
    assert body["source_id"] == SOURCE_ID


def test_as5_internal_error_is_generic_500_no_internals(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    def exploding_builder(result, **kwargs):
        raise RuntimeError("secret-internal-path C:\\hostile\r\n::injected")

    monkeypatch.setattr(scenario_module, "build_property_profile", exploding_builder)
    response = raw_client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 500
    assert response.headers.get("X-Correlation-ID")
    body = response.json()  # strict JSON (never Starlette's plain-text 500)
    assert body["state"] == "internal_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


def test_as5_error_bodies_never_leak_token_or_stack(client, monkeypatch):
    canary = "canary-app-token-9x7"  # secretscan:allow fake token, leak-absence test
    monkeypatch.setenv("SOCRATA_APP_TOKEN", canary)
    enable_flag(monkeypatch)
    install_substrate(confident_r5_substrate())
    for script in (
        lambda: [TransportTimeout("timeout after 10.0s")] * 3,
        lambda: [TransportFailure("network failure: OSError")] * 3,
        lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")],
    ):
        install_fetcher(script)
        response = client.get(f"/api/v1/properties/{BBL}/scenario")
        assert response.status_code in {502, 503, 504}
        assert canary not in response.text
        assert "Traceback" not in response.text
        assert 'File "' not in response.text


# ==========================================================================
# AS-6 - no injection surface: only the bbl path param; POST -> 405.
# ==========================================================================


def test_as6_post_is_405_method_not_allowed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    response = client.post(
        f"/api/v1/properties/{BBL}/scenario", json={"assumptions": [{"key": "x"}]}
    )
    assert response.status_code == 405


def test_as6_query_supplied_assumptions_are_ignored(client, monkeypatch):
    """A browser-supplied ?assumptions=... query is inert: the route never reads
    it, so the surfaced document is byte-identical to the clean request."""
    enable_flag(monkeypatch)

    def get_doc(url_suffix: str) -> dict:
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(confident_r5_substrate())
        return client.get(f"/api/v1/properties/{BBL}/scenario{url_suffix}").json()

    clean = get_doc("")
    injected = get_doc("?assumptions=%5B%7B%22key%22%3A%22far%22%2C%22value%22%3A99%7D%5D")
    assert json.dumps(clean, sort_keys=True) == json.dumps(injected, sort_keys=True)


# ==========================================================================
# AS-10 (regression) - the existing property route is unaffected.
# ==========================================================================


def test_as10_existing_property_route_still_works(client, monkeypatch):
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    response = client.get(f"/api/v1/properties/{BBL}")
    assert response.status_code == 200
    assert response.json()["identity"]["bbl"] == BBL


def test_as10_health_endpoint_unaffected(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
