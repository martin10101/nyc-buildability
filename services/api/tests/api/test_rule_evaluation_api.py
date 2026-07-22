"""Internal rule-evaluation endpoint + response-serializer acceptance pack
(task M4-T005 phase 2, scenarios AS-3..AS-8, AS-10, AS-14).

Offline and deterministic. The route's PLUTO fetcher and its server-side spatial
substrate provider are both overridden via FastAPI dependency injection with the
accepted recorded-official PLUTO fixtures (services/api/tests/fixtures/pluto) and
faithful M2-T013 substrate dicts (the exact shape the accepted profile builder
consumes - proven by tests/profile/test_wave_integration.py), so no test touches
the network.

Coverage of the acceptance scenarios:

* AS-3 flag ON, confident supported family -> 200 schema-valid draft document.
* AS-4 flag OFF / default -> generic 404, no hint; plus the assert_not_verified
  boundary guard.
* AS-6 missing spatial substrate / lot area -> professional_review_required
  fail-safe, typed reason, no fabricated value (a NORMAL 200 document).
* AS-8 split-lot -> spatial uncertainty share RANGES preserved verbatim.
* AS-10 malformed BBL / upstream failure / internal error -> safe typed API
  error, strict JSON, no internal trace/secret/path.
* AS-14 regression: the existing /properties/{bbl} route is unaffected and the
  internal route never appears in the OpenAPI document.

AS-5 (unsupported family) and AS-7 (conflicting in-effect rules) are exercised at
the SERIALIZER level: the endpoint's evaluate_property is fixed to the real,
implemented residential_far family, which has exactly one R5 rule and can never
be unsupported or conflict. Those scenarios are produced with the synthetic
M4-T004 conflict registry / a labelled synthetic unsupported result and asserted
through the same serialize + strict-validate path the endpoint uses (documented in
the producer report).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient
from referencing import Registry, Resource

from app.api.v1 import rule_evaluation as rule_eval_module
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.pluto_soda import (
    SOURCE_ID,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.rules import RuleRegistry
from app.rules import coverage as cov
from app.rules import integration as ri
from app.rules.response import (
    RULE_EVALUATION_CONTRACT_VERSION,
    compute_input_fingerprint,
    serialize_rule_evaluation,
    validate_rule_evaluation_document,
)
from app.rules.snapshots import SnapshotStore

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
M4T004 = Path(__file__).resolve().parents[1] / "rules" / "fixtures" / "m4t004"

FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"


# --------------------------------------------------------------------------
# Fetcher + substrate override plumbing (fixture-transport, offline)
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
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


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
# Faithful M2-T013 substrate dicts (the shape build_property_profile consumes;
# mirrors tests/profile/test_wave_integration.intersection_record).
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
# rule_evaluation contract validator (mirrors the phase-1 contract test)
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def rule_eval_validator():
    resources = []
    for schema_file in sorted(SCHEMA_DIR.glob("*.schema.json")):
        doc = json.loads(schema_file.read_text(encoding="utf-8"))
        resources.append((doc["$id"], Resource.from_contents(doc)))
    registry = Registry().with_resources(resources)
    schema = json.loads((SCHEMA_DIR / "rule_evaluation.schema.json").read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema, registry=registry)


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
# AS-3 - flag ON, confident supported family -> 200 schema-valid draft.
# ==========================================================================


def test_as3_confident_supported_family_is_200_draft(client, monkeypatch, rule_eval_validator):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    doc = response.json()

    # Schema-valid against the canonical contract.
    errors = list(rule_eval_validator.iter_errors(doc))
    assert errors == [], [e.message for e in errors]

    # Draft (never verified), professional-review discipline, disclaimer.
    assert doc["contract_version"] == RULE_EVALUATION_CONTRACT_VERSION
    assert doc["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert "verified" not in set(_coverage_values(doc))
    assert doc["not_verified_disclaimer"]
    assert doc["family_coverage"]["coverage_status"] == cov.COVERAGE_CONDITIONAL

    # A full draft trace: citations + computation steps + spatial_uncertainty.
    assert doc["zoning_district"] == "R5"
    assert len(doc["evaluations"]) == 1
    trace = doc["evaluations"][0]
    assert trace["citations"] and trace["computation_steps"]
    assert trace["outputs"]["max_residential_far"] == 1.5
    assert doc["spatial_uncertainty"]["base_district_candidates"][0]["district_label"] == "R5"

    # Input identified BY REFERENCE; NO embedded property profile.
    ev = doc["evaluated_input"]
    assert set(ev) == {"bbl", "profile_contract_version", "input_fingerprint", "input_provenance"}
    assert ev["bbl"] == BBL
    assert ev["profile_contract_version"] == "1.4.0"
    assert ev["input_fingerprint"].startswith("sha256:")
    for embedded in ("property_profile", "profile_version", "provenance", "identity", "lot_facts"):
        assert embedded not in doc


def test_as3_response_is_deterministic(client, monkeypatch):
    enable_flag(monkeypatch)

    def once():
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(confident_r5_substrate())
        return client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()

    # The response body carries no volatile field (the correlation id is a header
    # only); identical inputs -> byte-identical document, fingerprint included.
    first, second = once(), once()
    assert (
        first["evaluated_input"]["input_fingerprint"]
        == second["evaluated_input"]["input_fingerprint"]
    )
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


# ==========================================================================
# AS-4 - flag OFF / default -> generic 404, no hint; boundary guard present.
# ==========================================================================


@pytest.mark.parametrize("flag_value", [None, "", "0", "false", "off", "maybe", "2", "  "])
def test_as4_flag_off_or_unknown_is_generic_404(client, monkeypatch, flag_value):
    if flag_value is None:
        monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, flag_value)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 404
    # Byte-indistinguishable from an unmounted path: only {"detail": "Not Found"}.
    assert response.json() == {"detail": "Not Found"}
    # No hint the feature exists and no correlation id disclosed.
    text = response.text.lower()
    assert "rule" not in text and "evaluation" not in text and "flag" not in text
    assert "x-correlation-id" not in {k.lower() for k in response.headers}


def test_as4_openapi_never_lists_the_internal_route(client, monkeypatch):
    # Even with the flag ON the route is include_in_schema=False -> never a hint.
    enable_flag(monkeypatch)
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/api/v1/properties/{bbl}/rule-evaluation" not in paths
    assert "/api/v1/properties/{bbl}" in paths  # the existing route is unaffected


def test_as4_serializer_boundary_refuses_verified():
    # The assert_not_verified boundary the endpoint relies on: a verified result
    # can never be serialized into a rule_evaluation document.
    verified = _synthetic_evaluation(coverage_status=cov.COVERAGE_VERIFIED)
    with pytest.raises(ri.DraftVerifiedError):
        serialize_rule_evaluation(verified, profile_contract_version="1.4.0")


# ==========================================================================
# AS-6 - missing spatial substrate / lot area -> PRR fail-safe, no value.
# ==========================================================================


def test_as6_absent_substrate_is_professional_review_fail_safe(
    client, monkeypatch, rule_eval_validator
):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(None)  # default server-side path: no substrate wired

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200  # a fail-safe result is a normal document
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    assert doc["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert doc["fail_safe"] is True
    assert doc["fail_safe_reason"] == "spatial_intersection_absent"
    assert doc["professional_review_required"] is True
    # No fabricated value / district.
    assert doc["zoning_district"] is None
    assert doc["lot_area_sq_ft"] is None
    assert doc["evaluations"] == []


def test_as6_confident_but_missing_lot_area_is_prr_no_value(
    client, monkeypatch, rule_eval_validator
):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    # Confident R5 district but a non-positive lot area -> no computed value.
    install_substrate(confident_r5_substrate(area=0.0))

    doc = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    assert doc["zoning_district"] == "R5"  # confidently known
    assert doc["lot_area_sq_ft"] is None  # never fabricated
    assert doc["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert doc["evaluations"][0]["outputs"] == {}


# ==========================================================================
# AS-8 - split-lot: spatial uncertainty share ranges preserved verbatim.
# ==========================================================================


def test_as8_split_lot_preserves_share_ranges(client, monkeypatch, rule_eval_validator):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(split_lot_substrate())

    doc = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    assert doc["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert doc["fail_safe_reason"] == "geometry_uncertain"
    assert doc["zoning_district"] is None  # never collapsed to a single district
    assert doc["evaluations"] == []

    candidates = {
        c["district_label"]: c for c in doc["spatial_uncertainty"]["base_district_candidates"]
    }
    assert candidates["R5"]["share_min"] == 0.55 and candidates["R5"]["share_max"] == 0.65
    assert candidates["R6"]["share_min"] == 0.35 and candidates["R6"]["share_max"] == 0.45
    assert doc["spatial_uncertainty"]["professional_review_required"] is True


# ==========================================================================
# AS-5 (serializer) - unsupported family surfaces as a normal 200 document.
# ==========================================================================


def _empty_spatial_uncertainty():
    return {
        "lot_overall_class": None,
        "professional_review_required": False,
        "coverage_note": None,
        "review_reasons": [],
        "notes": [],
        "base_district_candidates": [],
        "crosscheck": None,
    }


def _synthetic_evaluation(*, coverage_status, family_coverage=None):
    """A labelled SYNTHETIC PropertyRuleEvaluation for serializer/contract proofs
    the fixed-target endpoint cannot itself produce (unsupported family / verified
    boundary probe)."""
    return ri.PropertyRuleEvaluation(
        bbl=BBL,
        coverage_status=coverage_status,
        data_completeness=None,
        needs_review=True,
        professional_review_required=False,
        fail_safe=False,
        fail_safe_reason=None,
        rule_lifecycle_statuses=[],
        not_verified_disclaimer=ri.NOT_VERIFIED_DISCLAIMER,
        zoning_district=None,
        lot_area_sq_ft=None,
        lot_area_source=None,
        spatial_context=None,
        spatial_uncertainty=_empty_spatial_uncertainty(),
        input_provenance={"zoning_district": [], "lot_area_sq_ft": []},
        evaluations=[],
        family_coverage=family_coverage
        or {
            "family": "commercial_far",
            "coverage_status": cov.COVERAGE_UNSUPPORTED,
            "note": "no rule implemented for this family in the current registry",
        },
        reasons=["no implemented rule for this family"],
        coverage_source="integration_fail_safe",
        rule_conflict=None,
    )


def test_as5_unsupported_family_serializes_to_valid_200_document(rule_eval_validator):
    evaluation = _synthetic_evaluation(coverage_status=cov.COVERAGE_UNSUPPORTED)
    doc = serialize_rule_evaluation(evaluation, profile_contract_version="1.4.0")
    assert list(rule_eval_validator.iter_errors(doc)) == []
    validate_rule_evaluation_document(doc)  # the endpoint's strict pre-send check
    assert doc["coverage_status"] == cov.COVERAGE_UNSUPPORTED
    assert doc["family_coverage"]["coverage_status"] == cov.COVERAGE_UNSUPPORTED
    assert "verified" not in set(_coverage_values(doc))
    # input still identified by reference; no embedded profile.
    assert doc["evaluated_input"]["bbl"] == BBL
    assert "property_profile" not in doc


# ==========================================================================
# AS-7 (serializer) - conflicting in-effect rules surface a typed rule_conflict.
# ==========================================================================


def _synthetic_conflict_registry():
    snaps = SnapshotStore(M4T004 / "snapshots")
    return RuleRegistry(M4T004 / "rulesets", snapshots=snaps).load()


def _confident_synth_profile():
    return {
        "identity": {"bbl": BBL},
        "spatial_intersection": {
            "lot_overall_class": "single_district_confident",
            "professional_review_required": False,
            "coverage_note": None,
            "pairs": [
                {
                    "family": "base_zoning",
                    "pair_class": "interior_confident",
                    "district_label": "SYNTH",
                    "lot_area_sq_ft": 10000.0,
                    "share_min": 1.0,
                    "share_point": 1.0,
                    "share_max": 1.0,
                    "minor_portion": False,
                }
            ],
            "review_reasons": [],
            "notes": [],
            "provenance_refs": ["prov-spatial"],
            "crosscheck": None,
        },
        "lot_geometry": {
            "outcome": "single_feature",
            "geometry_status": "valid",
            "review_required": False,
            "area_sq_ft": 10000.0,
            "provenance_ref": "prov-lotgeom",
        },
    }


def test_as7_rule_conflict_serializes_to_typed_prr_200_document(rule_eval_validator):
    evaluation = ri.evaluate_property(
        _confident_synth_profile(), registry=_synthetic_conflict_registry()
    )
    doc = serialize_rule_evaluation(evaluation, profile_contract_version="1.4.0")
    assert list(rule_eval_validator.iter_errors(doc)) == []
    validate_rule_evaluation_document(doc)
    # Typed conflict surfaced; NO silent pick, NO value produced.
    assert doc["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert doc["fail_safe_reason"] == "rule_conflict"
    assert doc["rule_conflict"] is not None
    assert [r["rule_id"] for r in doc["rule_conflict"]["competing_rules"]] == [
        "res-far-synth-a",
        "res-far-synth-b",
    ]
    assert doc["evaluations"] == []
    assert "verified" not in set(_coverage_values(doc))


def test_serializer_fingerprint_is_stable_and_sha256_hex():
    evaluation = ri.evaluate_property(
        _confident_synth_profile(), registry=_synthetic_conflict_registry()
    )
    fp1 = compute_input_fingerprint(evaluation)
    fp2 = compute_input_fingerprint(evaluation)
    assert fp1 == fp2
    assert fp1.startswith("sha256:") and len(fp1) == len("sha256:") + 64
    int(fp1.split(":")[1], 16)  # valid lowercase hex


# ==========================================================================
# AS-10 - safe typed errors; strict JSON; no internal trace/secret/path.
# ==========================================================================


@pytest.mark.parametrize(
    ("bbl", "expected_code"),
    [("abc", "non_numeric"), ("100001010", "wrong_length"), ("0000010100", "invalid_borough")],
)
def test_as10_malformed_bbl_is_typed_422_no_connector_call(client, monkeypatch, bbl, expected_code):
    enable_flag(monkeypatch)

    def must_not_call(b, c):
        raise AssertionError("connector must not be called for a malformed BBL")

    app.dependency_overrides[get_pluto_fetcher] = lambda: must_not_call
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{bbl}/rule-evaluation")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["detail"]["code"] == expected_code
    assert body["correlation_id"]


def test_as10_upstream_timeout_maps_to_504_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportTimeout("timeout after 10.0s")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 504
    assert response.json()["state"] == "timeout"


def test_as10_upstream_unavailable_maps_to_503_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportFailure("network failure: OSError")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 503
    assert response.json()["state"] == "source_unavailable"


def test_as10_schema_drift_maps_to_502_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")])
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 502
    assert response.json()["state"] == "schema_drift"


def test_as10_valid_nonexistent_bbl_is_404_no_match(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    response = client.get("/api/v1/properties/5999999999/rule-evaluation")
    assert response.status_code == 404
    body = response.json()
    assert body["state"] == "no_match"  # distinguishable from the disabled-flag 404
    assert body["source_id"] == SOURCE_ID


def test_as10_internal_error_is_generic_500_no_internals(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    def exploding_builder(result, **kwargs):
        raise RuntimeError("secret-internal-path C:\\hostile\r\n::injected")

    monkeypatch.setattr(rule_eval_module, "build_property_profile", exploding_builder)
    response = raw_client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 500
    assert response.headers.get("X-Correlation-ID")
    body = response.json()  # strict JSON (never Starlette's plain-text 500)
    assert body["state"] == "internal_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


def test_as10_error_bodies_never_leak_token_or_stack(client, monkeypatch):
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
        response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
        assert response.status_code in {502, 503, 504}
        assert canary not in response.text
        assert "Traceback" not in response.text
        assert 'File "' not in response.text


# ==========================================================================
# AS-14 - regression: the existing property route is unaffected.
# ==========================================================================


def test_as14_existing_property_route_still_works(client, monkeypatch):
    # Mounting the new router must not disturb GET /properties/{bbl}.
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    response = client.get(f"/api/v1/properties/{BBL}")
    assert response.status_code == 200
    assert response.json()["identity"]["bbl"] == BBL


def test_as14_health_endpoint_unaffected(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
