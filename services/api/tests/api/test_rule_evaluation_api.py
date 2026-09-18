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
import logging
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import pytest
from fastapi.testclient import TestClient
from referencing import Registry, Resource

from app.api.v1 import rule_evaluation as rule_eval_module
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import (
    get_spatial_substrate_provider,
    get_wide_street_determination_provider,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.mappluto_geometry_arcgis import CRS_STAMP, analyze_lot_geometry
from app.connectors.pluto_soda import (
    SOURCE_ID,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.connectors.ztldb_soda import UpstreamError as ZtldbUpstreamError
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
from app.rules.wide_street_wiring import (
    COVERAGE_CONDITIONAL as WS_COVERAGE_CONDITIONAL,
)
from app.rules.wide_street_wiring import (
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED as WS_COVERAGE_PRR,
)
from app.rules.wide_street_wiring import (
    DETERMINATION_PROFESSIONAL_REVIEW as WS_DET_PRR,
)
from app.rules.wide_street_wiring import (
    DETERMINATION_WITHIN_WIDE as WS_DET_WITHIN,
)
from app.rules.wide_street_wiring import (
    DRAFT_LABEL_NOTICE,
    FALLBACK_DIRECTION_NOTICE,
    ROUTED_TO_NOT_USED_NOTICE,
    WideStreetDetermination,
)
from app.rules.wide_street_wiring import (
    FAR_ROW_NONE as WS_FAR_ROW_NONE,
)
from app.rules.wide_street_wiring import (
    FAR_ROW_WIDE_STREET as WS_FAR_ROW_WIDE,
)
from app.spatial import live_provider as live_provider_module
from app.spatial import wide_street_live_provider as wide_provider_module
from app.spatial.live_provider import (
    LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR,
    LiveSpatialFetchers,
)
from app.spatial.wide_street_live_provider import (
    LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR,
    LiveWideStreetFetchers,
)

# Importing app.rules.wide_street_wiring (above) pulls the shapely-heavy buffer
# engine, exactly as the live provider would at runtime; a directly-constructed
# WideStreetDetermination is the same typed object a real provider returns. The
# M5-T034 disclosed gap is a provider RETURNING a determination through the
# endpoint, exercised via the dependency override below (the wiring's own
# engine-driven construction is proven in
# tests/spatial/test_wide_street_live_provider.py and
# tests/rules/test_wide_street_wiring.py).
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


def _applicable_trace(rule_eval: dict) -> dict:
    """The SINGLE applicable residential_far trace. The family evaluates every
    member (visible not_applicable for the others), so positional selection
    rots as the family grows; exactly-one is asserted so zero or several
    applicable members fails loudly (M4-T011)."""
    applicable = [
        t for t in rule_eval["evaluations"] if t["applicability_outcome"] is True
    ]
    assert len(applicable) == 1, sorted(t["rule_id"] for t in applicable)
    return applicable[0]


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
    # Every family member is evaluated (visible not_applicable for the non-R5
    # rules); the count follows the document's own family list so it never
    # rots as the family grows (M4-T011).
    assert doc["zoning_district"] == "R5"
    assert len(doc["evaluations"]) == len(doc["family_coverage"]["rule_ids"])
    trace = _applicable_trace(doc)
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


# ==========================================================================
# M2-T020 - settings-gated LIVE spatial provider behind the DEFAULT seam.
# S1 parity: live flag off -> the DEFAULT provider (no dependency override) is
# byte-identical to the recorded absent-substrate fail-safe, with ZERO
# connector calls. S2: flag on + connector doubles -> a real engine substrate
# flows through the DEFAULT provider into evaluate_property. S3: a live
# connector failure -> the SAME documented fail-safe document, never a 500.
# ==========================================================================

SPATIAL_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"
_R32_X, _R32_Y = 997482.04, 163293.94  # interior probe of the real ZF03 polygon


def _uninstall_substrate_override() -> None:
    """Route the request through the route's DEFAULT spatial provider."""
    app.dependency_overrides.pop(get_spatial_substrate_provider, None)


def _live_lot_double(bbl: str, correlation_id: str):
    """LotGeometryResult-shaped double: a square deep inside the real R3-2
    polygon, assessed by the accepted MapPLUTO geometry validator."""
    half = 25.0
    ring = [
        [_R32_X - half, _R32_Y - half],
        [_R32_X - half, _R32_Y + half],
        [_R32_X + half, _R32_Y + half],
        [_R32_X + half, _R32_Y - half],
        [_R32_X - half, _R32_Y - half],
    ]
    assessment = analyze_lot_geometry({"rings": [ring]}, crs=dict(CRS_STAMP))
    return SimpleNamespace(
        outcome="single_feature",
        geometry=assessment,
        review_required=False,
        requested_bbl=bbl,
        area_sq_ft=assessment.area_sq_ft,
        retrieved_at="2026-09-06T00:00:00Z",
        normalized_digest="digest-live-lot",
        source_data_last_edited="2026-07-01T00:00:00Z",
        crs=dict(CRS_STAMP),
    )


def _live_layer_double(label: str):
    """LayerQueryResult-shaped double carrying the REAL ZF03 nyzd polygon,
    relabelled to the queried district label (test data in a double)."""
    doc = json.loads(
        (SPATIAL_FIXTURE_DIR / "zoning_features" / "ZF03_query_nyzd_single_R3-2.json")
        .read_text(encoding="utf-8")
    )
    features = json.loads(doc["response_body_raw"])["features"]
    for feature in features:
        feature["attributes"]["ZONEDIST"] = label
    return SimpleNamespace(
        layer="nyzd",
        features=features,
        object_id_field="OBJECTID",
        normalized_digest="digest-live-zf03",
        retrieved_at="2026-09-06T00:00:00Z",
        source_data_last_edited="2026-07-01T00:00:00Z",
        exceeded_transfer_limit=False,
    )


def _live_ztldb_double(label: str):
    return SimpleNamespace(
        status="ok",
        zoning_assignment={
            "zoning_districts": [
                {"position": 1, "column": "zoning_district_1", "value": label}
            ],
            "commercial_overlays": [],
            "special_districts": [],
            "limited_height_district": None,
        },
        dataset_version="rows-2026-09-01",
        source_freshness={"rows_updated_at": "2026-09-01T00:00:00Z"},
    )


class RecordingLiveFetchers:
    """Recording spies around the live-fetcher doubles. Call lists are asserted
    AFTER the request returns: the provider's fail-safe ``except`` swallows any
    AssertionError raised inside a fetcher, so an exploding guard cannot prove
    non-invocation, but a recorded call cannot be hidden. ``ztldb`` optionally
    overrides the ZTLDB fetcher (e.g. with a raiser) while still being recorded.
    """

    def __init__(self, *, label: str = "R5", ztldb=None):
        self.lot_calls: list = []
        self.ztldb_calls: list = []
        self.layer_calls: list = []
        self._label = label
        self._ztldb = ztldb  # optional (bbl, cid) callable override

    def suite(self) -> LiveSpatialFetchers:
        def fetch_lot(bbl, cid):
            self.lot_calls.append((bbl, cid))
            return _live_lot_double(bbl, cid)

        def fetch_ztldb(bbl, cid):
            self.ztldb_calls.append((bbl, cid))
            if self._ztldb is not None:
                return self._ztldb(bbl, cid)
            return _live_ztldb_double(self._label)

        def fetch_district_layer(layer, field, value, cid):
            self.layer_calls.append((layer, field, value, cid))
            return _live_layer_double(value)

        return LiveSpatialFetchers(
            fetch_lot=fetch_lot,
            fetch_ztldb=fetch_ztldb,
            fetch_district_layer=fetch_district_layer,
        )


def test_m2t020_s1_flag_off_default_seam_matches_absent_substrate_byte_for_byte(
    client, monkeypatch
):
    enable_flag(monkeypatch)
    monkeypatch.delenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, raising=False)
    # Recording spies (working doubles): if a defect invoked them while the
    # flag is off, the count assertions below fail AND the composed substrate
    # would break the byte-parity assertion. Counts are checked AFTER the
    # request returns, so the provider's fail-safe except cannot hide a call.
    recording = RecordingLiveFetchers()
    monkeypatch.setattr(live_provider_module, "_ACTIVE_FETCHERS", recording.suite())

    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(None)  # the recorded pre-M2-T020 default behavior
    baseline = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()

    _uninstall_substrate_override()  # now the route uses its DEFAULT provider
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    live_default = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()

    # The body carries no volatile field (AS-3 determinism), so parity is exact.
    assert json.dumps(live_default, sort_keys=True) == json.dumps(baseline, sort_keys=True)
    assert live_default["fail_safe_reason"] == "spatial_intersection_absent"
    # Zero connector calls with the flag off, asserted after both requests.
    assert recording.ztldb_calls == []
    assert recording.lot_calls == []
    assert recording.layer_calls == []


def test_m2t020_s2_flag_on_live_substrate_reaches_evaluation_via_default_seam(
    client, monkeypatch, rule_eval_validator
):
    enable_flag(monkeypatch)
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    recording = RecordingLiveFetchers(label="R5")
    monkeypatch.setattr(live_provider_module, "_ACTIVE_FETCHERS", recording.suite())
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    _uninstall_substrate_override()  # DEFAULT provider; no dependency override

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []

    # Each connector was consulted exactly once, and every call carried the
    # SAME correlation id the response advertises (provenance binding).
    correlation_id = response.headers["X-Correlation-ID"]
    assert recording.ztldb_calls == [(BBL, correlation_id)]
    assert recording.lot_calls == [(BBL, correlation_id)]
    assert recording.layer_calls == [("nyzd", "ZONEDIST", "R5", correlation_id)]

    # The engine-composed substrate reached evaluate_property: a confident R5
    # district and the GEOMETRIC lot area drive a full conditional draft trace.
    assert doc["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert doc["zoning_district"] == "R5"
    assert doc["lot_area_source"] == "spatial_intersection.pairs[].lot_area_sq_ft"
    assert doc["spatial_uncertainty"]["base_district_candidates"][0][
        "district_label"
    ] == "R5"
    assert len(doc["evaluations"]) == len(doc["family_coverage"]["rule_ids"])
    assert _applicable_trace(doc)["outputs"]["max_residential_far"] == 1.5
    assert "verified" not in set(_coverage_values(doc))


def test_m2t020_s3_live_connector_failure_is_absent_substrate_fail_safe(
    client, monkeypatch, rule_eval_validator, caplog
):
    enable_flag(monkeypatch)
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")

    # The message is a CANARY: it must never reach a log line or the response.
    def _raising_ztldb(bbl, cid):
        raise ZtldbUpstreamError("canary-upstream-detail", correlation_id=cid)

    recording = RecordingLiveFetchers(ztldb=_raising_ztldb)
    monkeypatch.setattr(live_provider_module, "_ACTIVE_FETCHERS", recording.suite())
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    _uninstall_substrate_override()

    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200  # documented fail-safe, never a 500
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    assert doc["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert doc["fail_safe"] is True
    assert doc["fail_safe_reason"] == "spatial_intersection_absent"
    assert doc["professional_review_required"] is True
    assert doc["zoning_district"] is None
    assert doc["evaluations"] == []

    # Short-circuit asserted AFTER the request returned: the failing ZTLDB call
    # happened exactly once and the later connectors were never consulted (an
    # in-call exploding guard would have been swallowed by the fail-safe except).
    correlation_id = response.headers["X-Correlation-ID"]
    assert recording.ztldb_calls == [(BBL, correlation_id)]
    assert recording.lot_calls == []
    assert recording.layer_calls == []

    # The typed failure is logged payload-only: error CLASS + the SAME
    # correlation id the response advertises, never the exception text.
    lines = [
        record.getMessage()
        for record in caplog.records
        if record.name == "app.spatial.live_provider"
        and "fail_safe" in record.getMessage()
    ]
    assert len(lines) == 1
    assert "event=connector_error" in lines[0]
    assert "error_type=UpstreamError" in lines[0]
    assert f"correlation_id={correlation_id}" in lines[0]
    assert "canary-upstream-detail" not in lines[0]
    assert "canary-upstream-detail" not in response.text


# ==========================================================================
# M5-T033 - deployed spatial_intersection_absent root-cause reproduction
# (D-059-R004). The live capture (project-control/reports/M5-T033-live-capture.md)
# recorded a UNIFORM spatial_intersection_absent across both D-059 parcels AND a
# known-good control, each in ~0.6-0.7 s. Two candidate branches produce that
# same response-level reason; these reproduce BOTH deterministically through the
# route's DEFAULT spatial seam and pin what each observable signature does and
# does NOT distinguish. No production code changes - the branches already exist;
# this is the regression fence keeping a future deploy regression (flag unset)
# separable from a live connector/data failure. Uniform absence across the control
# and fast latency are SUGGESTIVE, never decisive: a shared connector failure is
# uniform and fast too, so they cannot by themselves prove the flag was off (the
# provider-level counterexample lives in tests/spatial/test_live_provider.py::
# test_m5t033_shared_connector_failure_is_uniform_absent_flag_on). The runtime
# cause stays UNCONFIRMED until the owner reads the deployed
# LIVE_SPATIAL_PROVIDER_ENABLED value and its correlated connector logs
# (docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md §6b); the tests assert code
# behavior only, never that the live cause is confirmed.
# ==========================================================================

# The end-to-end seam behavior below is BBL-agnostic, so it runs on the module
# fixture BBL (whose PLUTO row the connector validates against the requested BBL).
# The D-059-R004 parcels themselves (3052960043, 3022647515) are exercised in the
# reproduction fixtures at the PROVIDER level (tests/spatial/test_live_provider.py)
# and the EVALUATOR level (tests/rules/test_rules_integration.py), where no PLUTO
# row is fetched so the real parcel BBLs flow through unmodified.


def test_m5t033_flag_off_uniform_absent_zero_connector_calls(
    client, monkeypatch, rule_eval_validator
):
    """Branch A (deploy regression): LIVE_SPATIAL_PROVIDER_ENABLED unset -> the
    DEFAULT provider yields no substrate with ZERO connector calls, and the
    endpoint fail-safes to spatial_intersection_absent - the same reason the live
    capture recorded UNIFORMLY across every parcel, reproduced end-to-end through
    the route's own default seam (this branch's BBL-independence is pinned
    per-parcel for the D-059 parcels at the provider/evaluator levels)."""
    enable_flag(monkeypatch)  # INTERNAL_RULE_EVAL_ENABLED on (route reachable)
    monkeypatch.delenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, raising=False)
    recording = RecordingLiveFetchers(label="R5")  # working doubles; stay unused
    monkeypatch.setattr(live_provider_module, "_ACTIVE_FETCHERS", recording.suite())
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    _uninstall_substrate_override()  # route uses its DEFAULT (live) provider

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    assert doc["fail_safe"] is True
    assert doc["fail_safe_reason"] == "spatial_intersection_absent"
    assert doc["professional_review_required"] is True
    assert doc["zoning_district"] is None
    assert doc["evaluations"] == []
    # The signature that separates this from a live connector failure: ZERO
    # connector calls, asserted AFTER the request (the fail-safe except cannot
    # hide a recorded call). Flag-off short-circuits before any network I/O.
    assert recording.ztldb_calls == []
    assert recording.lot_calls == []
    assert recording.layer_calls == []


def test_m5t033_flag_on_connector_failure_same_reason_but_connector_consulted(
    client, monkeypatch, rule_eval_validator, caplog
):
    """Branch B (live data failure): flag ON + an injected connector failure
    returns the SAME response-level spatial_intersection_absent (a documented 200
    fail-safe, never a 500) - so the response body alone does NOT distinguish it
    from branch A. What DOES: the connector was actually consulted (recorded) and
    the provider logged exactly one payload-only connector_error line. This is the
    crux the owner dashboard check resolves."""
    enable_flag(monkeypatch)
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")

    def _raising_ztldb(bbl, cid):
        raise ZtldbUpstreamError("canary-m5t033-detail", correlation_id=cid)

    recording = RecordingLiveFetchers(ztldb=_raising_ztldb)
    monkeypatch.setattr(live_provider_module, "_ACTIVE_FETCHERS", recording.suite())
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    _uninstall_substrate_override()

    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    # Response-level reason IDENTICAL to branch A (body cannot tell them apart).
    assert doc["fail_safe_reason"] == "spatial_intersection_absent"
    assert doc["professional_review_required"] is True
    assert doc["zoning_district"] is None
    # Provider-level signature is observably DIFFERENT: the connector was consulted
    # for this BBL, carrying the same correlation id the response advertises ...
    correlation_id = response.headers["X-Correlation-ID"]
    assert recording.ztldb_calls == [(BBL, correlation_id)]
    # ... and exactly one payload-only fail-safe line was logged (no canary text).
    lines = [
        r.getMessage()
        for r in caplog.records
        if r.name == "app.spatial.live_provider" and "fail_safe" in r.getMessage()
    ]
    assert len(lines) == 1
    assert "event=connector_error" in lines[0]
    assert "error_type=UpstreamError" in lines[0]
    assert "canary-m5t033-detail" not in lines[0]
    assert "canary-m5t033-detail" not in response.text


def test_m5t033_flag_on_healthy_connectors_is_not_absent_per_parcel(
    client, monkeypatch, rule_eval_validator
):
    """Flag ON + HEALTHY connectors end-to-end -> the parcel resolves to a real
    district (NOT absent). This shows the flag-on branch CAN resolve; it does NOT
    prove uniform absence implies flag-off. A SHARED connector failure yields
    uniform absence with the flag ON too (tests/spatial/test_live_provider.py::
    test_m5t033_shared_connector_failure_is_uniform_absent_flag_on), so uniformity
    and latency are suggestive only - the owner dashboard flag reading and the
    correlated typed connector logs are the decisive runtime evidence."""
    enable_flag(monkeypatch)
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    recording = RecordingLiveFetchers(label="R5")
    monkeypatch.setattr(live_provider_module, "_ACTIVE_FETCHERS", recording.suite())
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    _uninstall_substrate_override()

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    assert doc["fail_safe_reason"] != "spatial_intersection_absent"
    assert doc["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert doc["zoning_district"] == "R5"
    # The connectors WERE consulted for this parcel (unlike branch A's zero calls).
    correlation_id = response.headers["X-Correlation-ID"]
    assert recording.ztldb_calls == [(BBL, correlation_id)]


# ==========================================================================
# M5-T035 - a wide-street-determination provider RETURNING a real typed
# determination flows through the DEFAULT get_wide_street_determination_provider
# seam into evaluate_property and drives ZR 23-22 conditional-FAR row selection.
# This closes the M5-T034 disclosed gap (AS-3): M5-T034 covered the provider
# DEFAULT (None), but no test exercised a provider RETURNING a determination
# through the full /rule-evaluation endpoint. The determination is supplied via a
# dependency override (exactly as get_spatial_substrate_provider is overridden),
# which is what "a provider returning a determination" means to this route.
#
# CONTRACT LIMITATION (surfaced here, routed as a discovery in the producer
# report - NOT fixed in-packet): the wide-street row (wide_street_far_row), the
# governing FAR (wide_street_governing_far), and the D-052 provenance summary
# (wide_street_determination) are DELIBERATELY NOT part of the frozen
# rule_evaluation @ 1.0.0 response contract (app.rules.integration.
# PropertyRuleEvaluation.as_dict omits them; a future additive contract bump would
# serialize the block). The determination's effect that DOES reach the response is
# carried by coverage_status / professional_review_required / reasons. The
# assertions below verify exactly those observable effects and pin the absence of
# the structured block, rather than asserting a field the contract does not carry.
# ==========================================================================


def confident_district_substrate(district: str, area: float = 10000.0):
    """A single-district-confident base-zoning substrate for an arbitrary district
    label (mirrors confident_r5_substrate for the wide-street-conditional R6)."""
    return _substrate(
        "single_district_confident",
        [_pair(district, "interior_confident", lot_area=area)],
        review=False,
    )


def _wide_street_determination(
    determination_state: str,
    far_row: str,
    coverage_hint: str,
    *,
    reason: str,
    aggregate_intersects: bool | None = None,
) -> WideStreetDetermination:
    """A real typed WideStreetDetermination (the exact object a live provider
    returns) built directly - no shapely geometry needed at this seam; the
    engine-driven construction from fixtures is proven in
    tests/spatial/test_wide_street_live_provider.py. Mirrors
    tests/rules/test_rules_integration.py::_wide_determination."""
    return WideStreetDetermination(
        determination_state=determination_state,
        far_row=far_row,
        coverage_hint=coverage_hint,
        exceptions_checked=True,
        named_street_override_pending=False,
        reason=reason,
        policy_decision_states=("wide",),
        original_labels=("100",),
        source_versions=("dcm-streetwidth-v1",),
        matched_geometry_refs=("segment-object-id-1",),
        interpreted_bounds_summaries=("exactly 100 ft",),
        classification_reasons=("mapped width 100 ft >= 75 ft threshold",),
        buffer_status="computed",
        aggregate_intersects=aggregate_intersects,
        aggregate_area_sq_ft=None,
        lot_identity=BBL,
        draft_label=DRAFT_LABEL_NOTICE,
        routed_to_note=ROUTED_TO_NOT_USED_NOTICE,
        fallback_direction_note=FALLBACK_DIRECTION_NOTICE,
    )


def install_wide_street_provider(determination) -> None:
    """Override the route's wide-street-determination provider so the endpoint
    behaves as if a live provider returned this determination (mirrors
    install_substrate)."""
    app.dependency_overrides[get_wide_street_determination_provider] = (
        lambda: (lambda canonical_bbl, correlation_id: determination)
    )


class _RecordingWideFetchers:
    """Recording spies for the live wide-street provider's connector seams, to
    prove ZERO connector calls when LIVE_WIDE_STREET_PROVIDER_ENABLED is off.
    Counts are asserted AFTER the request returns (the provider's fail-safe except
    would swallow an in-call AssertionError, but a recorded call cannot hide)."""

    def __init__(self) -> None:
        self.calls = {"lot": 0, "segments": 0, "geometries": 0}

    def suite(self) -> LiveWideStreetFetchers:
        def fetch_lot(bbl, cid):
            self.calls["lot"] += 1
            raise AssertionError("wide-street lot fetch must not run with the flag off")

        def fetch_segments(envelope, cid):
            self.calls["segments"] += 1
            raise AssertionError("wide-street segment fetch must not run with the flag off")

        def fetch_geometries(object_id_in, cid):
            self.calls["geometries"] += 1
            raise AssertionError("wide-street geometry fetch must not run with the flag off")

        return LiveWideStreetFetchers(
            fetch_lot=fetch_lot,
            fetch_segments_by_envelope=fetch_segments,
            fetch_segment_geometries_by_ids=fetch_geometries,
        )


def test_m5t035_within_wide_determination_fires_wide_row_via_endpoint(
    client, monkeypatch, rule_eval_validator
):
    # A within-100ft-of-a-wide-street determination on a confident R6 lot: the
    # WIDE conditional-FAR row governs server-side. R6 is covered by exactly one
    # residential_far rule (r6-r7-r8-wide-street-conditional-far; the flat r6-r12
    # rule applies only to the suffixed districts), so the determination folds.
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_district_substrate("R6"))
    det = _wide_street_determination(
        WS_DET_WITHIN,
        WS_FAR_ROW_WIDE,
        WS_COVERAGE_CONDITIONAL,
        reason="M5-T035 endpoint fixture: within-100ft determination",
        aggregate_intersects=True,
    )
    install_wide_street_provider(det)

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []

    # WITHIN is a confident DRAFT outcome: coverage stays conditional, never
    # escalated and never Verified (D-045-R009).
    assert doc["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert doc["professional_review_required"] is False
    assert doc["zoning_district"] == "R6"
    assert "verified" not in set(_coverage_values(doc))
    assert doc["not_verified_disclaimer"]

    # The rule's OWN DSL trace output stays the CONSERVATIVE R6 value (2.20); the
    # higher wide-street value is NEVER produced by the rule's computation - it is
    # selected only server-side and only surfaces in reasons (below).
    trace = _applicable_trace(doc)
    assert trace["outputs"]["max_residential_far"] == 2.2

    # The wide-row effect that reaches the frozen contract is the fold reason,
    # naming the higher governing FAR (3.00) and the DRAFT marker. Asserted as an
    # exact reconstructed string (not a broad substring match).
    expected_reason = (
        "wide-street determination within_100ft_of_wide_street: the "
        "wide-street (higher) conditional-FAR row governs (max_residential_far "
        "3.0); DRAFT pending G6. M5-T035 endpoint fixture: within-100ft determination"
    )
    assert expected_reason in doc["reasons"]

    # CONTRACT LIMITATION (discovery-routed): the structured wide-street row /
    # governing FAR / provenance summary are NOT part of rule_evaluation @ 1.0.0.
    for absent in ("wide_street_far_row", "wide_street_governing_far", "wide_street_determination"):
        assert absent not in doc


def test_m5t035_professional_review_determination_escalates_coverage_via_endpoint(
    client, monkeypatch, rule_eval_validator
):
    # A professional-review wide-street determination on a confident R6 lot grants
    # NO wide-street FAR bonus and ESCALATES coverage to professional_review_required
    # (D-051 fallback direction: the wide value is the higher FAR, withheld on
    # uncertainty). This is the observable, frozen-contract effect.
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_district_substrate("R6"))
    det = _wide_street_determination(
        WS_DET_PRR,
        WS_FAR_ROW_NONE,
        WS_COVERAGE_PRR,
        reason="M5-T035 endpoint fixture: unresolved street width",
    )
    install_wide_street_provider(det)

    response = client.get(f"/api/v1/properties/{BBL}/rule-evaluation")
    assert response.status_code == 200  # escalation is still a normal 200 document
    doc = response.json()
    assert list(rule_eval_validator.iter_errors(doc)) == []
    assert doc["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert doc["professional_review_required"] is True
    assert doc["zoning_district"] == "R6"  # the district is still confidently known
    assert "verified" not in set(_coverage_values(doc))

    expected_reason = (
        "wide-street determination professional_review_required: no "
        "conditional-FAR row fires and no higher (wide-street) FAR bonus is "
        "granted; coverage escalates to professional review "
        "(D-051 fallback direction for these rows - the wide value is the "
        "higher FAR, so it is withheld on uncertainty). "
        "M5-T035 endpoint fixture: unresolved street width"
    )
    assert expected_reason in doc["reasons"]


def test_m5t035_flag_off_default_wide_provider_zero_calls_byte_identical(client, monkeypatch):
    # AS-1 (endpoint half): with LIVE_WIDE_STREET_PROVIDER_ENABLED off, the route's
    # DEFAULT wide-street provider returns None with ZERO connector calls, and the
    # /rule-evaluation document is byte-identical to the no-determination path.
    enable_flag(monkeypatch)
    monkeypatch.delenv(LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR, raising=False)
    recording = _RecordingWideFetchers()
    monkeypatch.setattr(wide_provider_module, "_ACTIVE_FETCHERS", recording.suite())

    # Baseline: an explicit override that supplies NO determination (None).
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_district_substrate("R6"))
    install_wide_street_provider(None)
    baseline = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()

    # Now the route uses its DEFAULT wide-street provider (flag off -> None).
    app.dependency_overrides.pop(get_wide_street_determination_provider, None)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_district_substrate("R6"))
    live_default = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()

    # The body carries no volatile field (AS-3 determinism), so parity is exact.
    assert json.dumps(live_default, sort_keys=True) == json.dumps(baseline, sort_keys=True)
    assert live_default["zoning_district"] == "R6"
    # Zero wide-street connector calls with the flag off, asserted AFTER the request
    # (the provider's fail-safe except cannot hide a recorded call).
    assert recording.calls == {"lot": 0, "segments": 0, "geometries": 0}
