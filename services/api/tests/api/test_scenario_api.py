"""Internal scenario endpoint acceptance pack (task M5-T003, AS-1..AS-7).

Offline and deterministic. The route's PLUTO fetcher and its server-side spatial
substrate provider are both overridden via FastAPI dependency injection with the
accepted recorded-official PLUTO fixtures (services/api/tests/fixtures/pluto) and
faithful M2-T013 substrate dicts - the SAME harness the accepted rule-evaluation
endpoint test uses - so NO test touches the network, Supabase, or Geoclient
(AS-7). The endpoint rebuilds the profile AND its rule_evaluation server-side
over those seams and runs the already-built deterministic ``build_scenario``.

Coverage of the acceptance scenarios:

* AS-1 confident R5 cap -> 200 preliminary scenario whose cap is surfaced
  VERBATIM from the rule_evaluation trace (asserted equal to the trace value read
  from the mirrored rule-evaluation route, never locally recomputed); cap_label
  present; the 8 envelope families are MISSING; never Verified.
* AS-2 split-lot -> fail-closed no_scenario / professional-review, share RANGES
  preserved (never collapsed), no cap surfaced (a NORMAL 200 document).
* AS-3 no-match BBL -> documented 404 no_match with correlation id; no scenario.
* AS-4 malformed BBL / upstream failure (incl. rate-limit) / internal defect /
  contract-validation failure -> documented typed error; no partial or invented
  scenario is ever emitted and no internals leak.
* AS-5 contract: every 200 body passes validate_scenario_document; EVERY
  documented (HTTP status, state) pair - including (503, rate_limited) and
  (500, internal_contract_error) - is actually driven, the emitted set equals the
  route's documented matrix, and that matrix is cross-checked against the accepted
  GET /properties/{bbl} route's published matrix.
* AS-6 flag-off -> generic 404 indistinguishable from an unmounted path, absent
  from the OpenAPI schema, and reached WITHOUT invoking either injected seam's
  I/O-performing callable (landmine seams prove non-invocation).
* AS-7 offline: AS-1..AS-6 all run under the injected seams over committed
  fixtures via FastAPI TestClient - no network, no Supabase, no Geoclient.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import rule_evaluation as rule_evaluation_module
from app.api.v1 import scenario as scenario_module
from app.api.v1.properties import STATUS_STATE_MATRIX as PROPERTY_MATRIX
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.api.v1.scenario import STATUS_STATE_MATRIX
from app.config import (
    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
    INTERNAL_SCENARIO_ENABLED_ENV_VAR,
)
from app.connectors.pluto_soda import (
    SOURCE_ID,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.rules.response import RuleEvaluationContractError
from app.scenario.contract import ScenarioContractError, validate_scenario_document

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"

# The professional-review reason the split-lot substrate carries. AS-2 asserts
# this exact reason is surfaced VISIBLY in the scenario document (propagated
# verbatim through rule_evaluation.spatial_uncertainty.review_reasons into the
# zoning_district constraint provenance), never silently dropped.
SPLIT_LOT_REVIEW_REASON = "lot_overall_class=split_lot_confident"

# The 8 envelope families the coverage matrix must always list as MISSING
# (constants.MISSING_ENVELOPE_CONSTRAINTS keys; asserted, never imported, so a
# silent change to that tuple surfaces here).
MISSING_ENVELOPE_FAMILIES = frozenset(
    {
        "height_limit",
        "setbacks_yards",
        "lot_coverage_open_space",
        "street_wall_base_height",
        "parking_loading",
        "use_group_overlay",
        "special_districts_overlays",
        "density_bonuses",
    }
)


# --------------------------------------------------------------------------
# Fetcher + substrate override plumbing (fixture-transport, offline) - mirrors
# tests/api/test_rule_evaluation_api.py so the two internal routes share the
# exact same offline harness.
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
    """Override BOTH injected seams with providers whose RETURNED callables raise
    if ever invoked. The providers themselves are cheap (they only return the
    callable), so FastAPI resolves the dependency without side effects - exactly
    like the real ``get_pluto_fetcher`` / ``get_spatial_substrate_provider``,
    which return a function reference and perform their network / spatial I/O only
    when that reference is CALLED. A disabled request that returns 404 before
    calling either seam therefore performs NO fetch or substrate I/O and cannot be
    broken by a failing dependency callable; if the flag check ever regressed to
    run after a seam call, these landmines would fire and fail the test."""
    def _landmine_fetcher_provider():
        def fetch(bbl: str, correlation_id: str):
            raise AssertionError(
                "PLUTO fetcher must not be invoked for a disabled-flag request"
            )

        return fetch

    def _landmine_substrate_provider():
        def provide(canonical_bbl: str, correlation_id: str):
            raise AssertionError(
                "spatial-substrate provider must not be invoked for a disabled request"
            )

        return provide

    app.dependency_overrides[get_pluto_fetcher] = _landmine_fetcher_provider
    app.dependency_overrides[get_spatial_substrate_provider] = _landmine_substrate_provider


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
# Faithful M2-T013 substrate dicts (the shape build_property_profile consumes;
# mirrors tests/api/test_rule_evaluation_api.py so both routes share fixtures).
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
        review_reasons=[SPLIT_LOT_REVIEW_REASON],
    )


def _constraints_by_key(doc: dict) -> dict:
    return {c["key"]: c for c in doc["constraints"]}


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
# AS-1 - confident R5 cap: 200 preliminary scenario, cap surfaced VERBATIM.
# ==========================================================================


def test_as1_confident_r5_cap_surfaces_trace_value_verbatim(client, monkeypatch):
    # Enable BOTH internal routes so the SAME inputs can be read back through the
    # mirrored rule-evaluation route to prove the scenario cap is the trace value
    # verbatim (not a locally recomputed number).
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    doc = response.json()

    # Strict canonical-contract validity (the endpoint's own pre-send check).
    validate_scenario_document(doc)

    # A preliminary, conditional, never-Verified draft scenario.
    assert doc["scenario_kind"] == "preliminary"
    assert doc["coverage_status"] == "conditional"
    assert doc["needs_review"] is True
    assert "verified" not in set(_coverage_values(doc))
    assert doc["not_verified_disclaimer"]

    # The cap is the canonical trace value, VERBATIM. Read the trace value from
    # the mirrored rule-evaluation route over the identical inputs.
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    rule_eval = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()
    trace_cap = _applicable_trace(rule_eval)["outputs"]["max_residential_floor_area_sq_ft"]
    assert doc["draft_zoning_floor_area_cap_sq_ft"] == trace_cap == 15000.0
    assert doc["cap_label"]  # present, non-null

    # The cap constraint carries the draft label and its trace provenance.
    residential = _constraints_by_key(doc)["residential_far_cap"]
    assert residential["value"] == trace_cap
    assert residential["state"] == "draft"

    # The coverage matrix lists all 8 envelope families as MISSING, never inferred.
    missing = {
        row["constraint_family"]
        for row in doc["coverage_matrix"]
        if row["rule_status_today"] == "missing"
    }
    assert MISSING_ENVELOPE_FAMILIES <= missing
    for family in MISSING_ENVELOPE_FAMILIES:
        assert _constraints_by_key(doc)[family]["state"] == "missing"

    # C1 (M5-T017, D-041): the server-rebuilt profile (F01 bldgarea = 10000) plus
    # the draft cap (15000) yields a COMPUTED unused-floor-area section of exactly
    # 5000 sq ft, with the existing-area coverage_status echoed and the ZR 12-10
    # assumption present. Values derived from the same trace cap + fixture bldgarea.
    section = doc["unused_draft_zoning_floor_area"]
    assert section["state"] == "computed"
    assert section["unused_draft_zoning_floor_area_sq_ft"] == trace_cap - 10000.0 == 5000.0
    assert section["unit"] == "square_feet"
    assert section["inputs"]["draft_zoning_floor_area_cap"]["value_sq_ft"] == trace_cap
    assert section["inputs"]["existing_building_floor_area"]["value_sq_ft"] == 10000.0
    assert section["inputs"]["existing_building_floor_area"]["coverage_status"] == "conditional"
    assert section["inputs"]["existing_building_floor_area"]["provenance"] is not None
    assert [a["key"] for a in section["assumptions"]] == ["zoning_lot_extent"]
    # A positive remainder does not itself force professional review.
    assert doc["professional_review_required"] is False


# ==========================================================================
# AS-2 - split-lot: fail-closed no_scenario, share ranges preserved, no cap.
# ==========================================================================


def test_as2_split_lot_is_no_scenario_ranges_preserved(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(split_lot_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200  # a fail-closed outcome is a normal document
    doc = response.json()
    validate_scenario_document(doc)

    assert doc["scenario_kind"] == "no_scenario"
    assert doc["coverage_status"] == "professional_review_required"
    assert doc["professional_review_required"] is True
    # No cap surfaced.
    assert doc["draft_zoning_floor_area_cap_sq_ft"] is None
    assert doc["cap_label"] is None

    # A VISIBLE review reason is surfaced, never silently dropped. Surface (a):
    # the top-level human-readable reasons list explains WHY this is a
    # professional-review no_scenario outcome.
    assert isinstance(doc["reasons"], list) and doc["reasons"]
    assert any(
        "professional" in reason.lower() and "review" in reason.lower()
        for reason in doc["reasons"]
    )

    # Share RANGES preserved verbatim, never collapsed to a single district.
    district = _constraints_by_key(doc)["zoning_district"]
    assert district["value"] is None  # never collapsed
    candidates = {
        c["district_label"]: c
        for c in district["provenance"]["base_district_candidates"]
    }
    assert candidates["R5"]["share_min"] == 0.55 and candidates["R5"]["share_max"] == 0.65
    assert candidates["R6"]["share_min"] == 0.35 and candidates["R6"]["share_max"] == 0.45

    # Surface (b): the district-constraint provenance carries the EXACT spatial
    # review reason from the substrate, propagated verbatim through
    # rule_evaluation.spatial_uncertainty.review_reasons - a machine-readable,
    # visible review reason (not merely a boolean flag).
    assert SPLIT_LOT_REVIEW_REASON in district["provenance"]["review_reasons"]

    # C1 (M5-T017, D-041): the section rides on this no-scenario document too, with
    # no cap it is not_computable/no_draft_far_cap and never invents a number.
    section = doc["unused_draft_zoning_floor_area"]
    assert section["state"] == "not_computable"
    assert section["not_computable_reason"] == "no_draft_far_cap"
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None


# ==========================================================================
# AS-3 - no-match BBL: documented 404 no_match, correlation id, no scenario.
# ==========================================================================


def test_as3_no_match_is_documented_404(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)

    response = client.get("/api/v1/properties/5999999999/scenario")
    assert response.status_code == 404
    assert response.headers["x-correlation-id"]
    body = response.json()
    assert body["state"] == "no_match"  # distinguishable from the disabled-flag 404
    assert body["source_id"] == SOURCE_ID
    assert body["correlation_id"]
    # No invented scenario body.
    assert "scenario_kind" not in body and "constraints" not in body


# ==========================================================================
# AS-4 - malformed BBL / upstream failure / internal defect -> typed errors.
# ==========================================================================


@pytest.mark.parametrize(
    ("bbl", "expected_code"),
    [("abc", "non_numeric"), ("100001010", "wrong_length"), ("0000010100", "invalid_borough")],
)
def test_as4_malformed_bbl_is_typed_422_no_connector_call(
    client, monkeypatch, bbl, expected_code
):
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


def test_as4_upstream_timeout_maps_to_504_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportTimeout("timeout after 10.0s")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 504
    assert response.json()["state"] == "timeout"


def test_as4_upstream_unavailable_maps_to_503_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [TransportFailure("network failure: OSError")] * 3)
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 503
    assert response.json()["state"] == "source_unavailable"


def test_as4_schema_drift_maps_to_502_typed(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")])
    install_substrate(confident_r5_substrate())
    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 502
    assert response.json()["state"] == "schema_drift"


def test_as4_internal_defect_is_generic_500_no_internals(raw_client, monkeypatch):
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
    # No invented/partial scenario and no internals leaked.
    assert "scenario_kind" not in body
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


def test_as4_contract_validation_failure_is_typed_500_no_partial_scenario(
    raw_client, monkeypatch
):
    # A built payload that fails its canonical-contract validation before send is
    # an internal defect (an invalid 200 is impossible), mapped to the documented
    # typed (500, internal_contract_error) pair - NEVER a partial/invalid scenario
    # and never a raw stack. Driven via the scenario-document validator, the last
    # of the three contract checks the route runs (rebuilt profile, rebuilt
    # rule_evaluation, assembled scenario all share this pair).
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    def failing_validator(doc):
        raise ScenarioContractError(
            "secret-internal-path C:\\hostile\r\n::injected", location="constraints/0"
        )

    monkeypatch.setattr(scenario_module, "validate_scenario_document", failing_validator)
    response = raw_client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_contract_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    # No partial/invented scenario body and no internals (message, path, stack).
    assert "scenario_kind" not in body and "constraints" not in body
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


# ==========================================================================
# AS-5 - contract: every 200 validates; the emitted (status, state) matrix.
# ==========================================================================


def test_as5_status_state_matrix_is_the_documented_set():
    # The single source of truth mirrors the rule-evaluation route's matrix: a
    # 200 (no state), the 422 validation pair, the 404 no_match result pair, the
    # connector-failure pairs, and the two generic 500 pairs. The scenario
    # contract defect reuses (500, internal_contract_error) -> no new pair.
    assert STATUS_STATE_MATRIX == frozenset(
        {
            (200, None),
            (422, "validation_error"),
            (404, "no_match"),
            (502, "schema_drift"),
            (503, "rate_limited"),
            (503, "source_unavailable"),
            (504, "timeout"),
            (500, "internal_error"),
            (500, "internal_contract_error"),
        }
    )


def test_as5_matrix_is_the_existing_property_route_matrix_minus_version_pair():
    # Cross-check against an ACTUAL existing route's published matrix (the
    # accepted GET /properties/{bbl} route, app.api.v1.properties), not just this
    # module's own literal. The scenario route emits the SAME pairs except the
    # bounded (500, unsupported_contract_version) case: the property route
    # surfaces an unpublished contract_version distinctly, whereas the scenario
    # and rule-evaluation rebuild paths collapse that defect into the shared
    # (500, internal_contract_error) pair (see app/api/v1/scenario.py, which maps
    # both UnsupportedContractVersionError and ContractValidationError to
    # _internal_contract_error_500). So the scenario matrix introduces NO pair the
    # existing route does not already document.
    version_pair: tuple[int, str | None] = (500, "unsupported_contract_version")
    assert STATUS_STATE_MATRIX == PROPERTY_MATRIX - {version_pair}
    assert version_pair in PROPERTY_MATRIX  # the existing route DOES document it
    assert version_pair not in STATUS_STATE_MATRIX  # scenario collapses it away


def test_as5_matrix_equals_rule_evaluation_route_emitted_set(
    client, raw_client, monkeypatch
):
    # Confirm the scenario matrix against the SIBLING rule-evaluation ROUTE
    # ITSELF (app.api.v1.rule_evaluation), the route this task mirrors - not
    # merely the property route's published constant. rule_evaluation.py exposes
    # NO matrix constant, so we DRIVE its route over the identical offline
    # harness, collect every emitted (HTTP status, state) pair, and assert the
    # scenario route's single-source-of-truth matrix EQUALS the set the
    # rule-evaluation route actually emits. This is the direct evidence for the
    # report's claim that the scenario matrix equals the rule-evaluation route's
    # emitted set (the scenario-document contract defect reuses the shared
    # (500, internal_contract_error) pair, introducing none of its own).
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    emitted: set[tuple[int, str | None]] = set()
    url = f"/api/v1/properties/{BBL}/rule-evaluation"

    def record(response):
        state = None if response.status_code == 200 else response.json().get("state")
        emitted.add((response.status_code, state))

    # 200 (confident) + 200 (split-lot fail-safe: a NORMAL rule_evaluation
    # document, still 200 / no state - the rule-evaluation route never errors on
    # a professional-review outcome, exactly like the scenario route).
    for substrate in (confident_r5_substrate(), split_lot_substrate()):
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(substrate)
        resp = client.get(url)
        assert resp.status_code == 200
        record(resp)

    # 422 malformed BBL, with NO connector call.
    install_substrate(confident_r5_substrate())
    app.dependency_overrides[get_pluto_fetcher] = lambda: (
        lambda b, c: (_ for _ in ()).throw(AssertionError("no call"))
    )
    record(client.get("/api/v1/properties/abc/rule-evaluation"))

    # 404 no_match.
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    record(client.get("/api/v1/properties/5999999999/rule-evaluation"))

    # 504 timeout, 503 source_unavailable, 502 schema_drift, 503 rate_limited.
    for script, expected in (
        (lambda: [TransportTimeout("t")] * 3, 504),
        (lambda: [TransportFailure("f")] * 3, 503),
        (lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")], 502),
        (lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3, 503),
    ):
        install_fetcher(script)
        install_substrate(confident_r5_substrate())
        resp = client.get(url)
        assert resp.status_code == expected
        record(resp)

    # 500 internal_contract_error: force the rule-evaluation route's own document
    # validator to fail (its contract-defect branch, the sibling of the scenario
    # route's).
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        rule_evaluation_module,
        "validate_rule_evaluation_document",
        lambda doc: (_ for _ in ()).throw(
            RuleEvaluationContractError("forced contract defect", location="<root>")
        ),
    )
    record(raw_client.get(url))

    # 500 internal_error: any unexpected exception in the build stage (explodes
    # before the still-patched validator is reached).
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        rule_evaluation_module,
        "build_property_profile",
        lambda result, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    record(raw_client.get(url))

    # The rule-evaluation route emitted EXACTLY the scenario route's matrix.
    assert emitted == STATUS_STATE_MATRIX


def test_as5_every_emitted_pair_is_in_the_matrix(client, raw_client, monkeypatch):
    enable_flag(monkeypatch)
    emitted: set[tuple[int, str | None]] = set()

    def record(response):
        state = None if response.status_code == 200 else response.json().get("state")
        emitted.add((response.status_code, state))

    # 200 preliminary + 200 no_scenario (both must validate).
    for substrate in (confident_r5_substrate(), split_lot_substrate()):
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(substrate)
        resp = client.get(f"/api/v1/properties/{BBL}/scenario")
        assert resp.status_code == 200
        validate_scenario_document(resp.json())
        record(resp)

    # 422 malformed, 404 no_match, 504/503/502 connector failures.
    install_substrate(confident_r5_substrate())
    app.dependency_overrides[get_pluto_fetcher] = lambda: (
        lambda b, c: (_ for _ in ()).throw(AssertionError("no call"))
    )
    record(client.get("/api/v1/properties/abc/scenario"))

    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    record(client.get("/api/v1/properties/5999999999/scenario"))

    # 504 timeout, 503 source_unavailable, 502 schema_drift, AND 503 rate_limited
    # (the fourth connector pair: three 429s exhaust the bounded retry budget).
    for script, expected in (
        (lambda: [TransportTimeout("t")] * 3, 504),
        (lambda: [TransportFailure("f")] * 3, 503),
        (lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")], 502),
        (lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3, 503),
    ):
        install_fetcher(script)
        install_substrate(confident_r5_substrate())
        resp = client.get(f"/api/v1/properties/{BBL}/scenario")
        assert resp.status_code == expected
        record(resp)

    # 500 internal_contract_error: a built payload fails its canonical-contract
    # validation before send. Driven via the scenario-document validator (the last
    # of the three contract checks the route runs); the rebuilt-profile and
    # rebuilt-rule_evaluation contract branches emit the SAME pair.
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        scenario_module,
        "validate_scenario_document",
        lambda doc: (_ for _ in ()).throw(
            ScenarioContractError("forced scenario contract defect", location="<root>")
        ),
    )
    record(raw_client.get(f"/api/v1/properties/{BBL}/scenario"))

    # 500 internal_error: any unexpected exception -> the generic pair. (build
    # explodes before the still-patched validator is reached.)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())
    monkeypatch.setattr(
        scenario_module,
        "build_property_profile",
        lambda result, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    record(raw_client.get(f"/api/v1/properties/{BBL}/scenario"))

    # Every documented pair was actually driven AND the route emitted nothing
    # undocumented: the emitted set EQUALS the single-source-of-truth matrix.
    assert emitted == STATUS_STATE_MATRIX


# ==========================================================================
# AS-6 - flag-off / unknown -> generic 404; never in the OpenAPI schema.
# ==========================================================================


@pytest.mark.parametrize("flag_value", [None, "", "0", "false", "off", "maybe", "2", "  "])
def test_as6_flag_off_or_unknown_is_generic_404(client, monkeypatch, flag_value):
    if flag_value is None:
        monkeypatch.delenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, flag_value)
    # Landmine seams: a disabled request must return 404 WITHOUT invoking the
    # fetcher or substrate callables (the only things that perform network /
    # spatial I/O and could fail). The providers resolve cleanly; the returned
    # callables raise if the handler ever reached them.
    install_landmine_seams()

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 404
    # Byte-indistinguishable from an unmounted path: only {"detail": "Not Found"}.
    assert response.json() == {"detail": "Not Found"}
    # No hint the feature exists and no correlation id disclosed.
    text = response.text.lower()
    assert "scenario" not in text and "flag" not in text
    assert "x-correlation-id" not in {k.lower() for k in response.headers}


def test_as6_disabled_request_performs_no_dependency_io(client, monkeypatch):
    # Explicit fail-safe guard for the disabled path: the flag check runs FIRST,
    # so neither injected seam's I/O-performing callable is invoked. Proven two
    # ways over the SAME disabled request.
    monkeypatch.delenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, raising=False)

    # (a) Landmine seams installed: the handler must not call them -> still 404.
    install_landmine_seams()
    landmined = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert landmined.status_code == 404
    assert landmined.json() == {"detail": "Not Found"}

    # (b) No override at all: the REAL providers resolve (they only return a
    # function reference; no network/Supabase/Geoclient touched at resolution)
    # and the disabled handler returns 404 before any fetch is attempted.
    app.dependency_overrides.clear()
    real = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert real.status_code == 404
    assert real.json() == {"detail": "Not Found"}


def test_as6_openapi_never_lists_the_internal_route(client, monkeypatch):
    # Even with the flag ON the route is include_in_schema=False -> never a hint.
    enable_flag(monkeypatch)
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/api/v1/properties/{bbl}/scenario" not in paths
    assert "/api/v1/properties/{bbl}" in paths  # the existing route is unaffected


# ==========================================================================
# AS-7 - offline / no credentials: the confident path runs purely on the
# injected seams over committed fixtures (all tests above share this harness).
# ==========================================================================


def test_as7_confident_path_is_fully_offline(client, monkeypatch):
    # No SOCRATA/Supabase/Geoclient credential is set or read; the ONLY data
    # sources are the committed PLUTO fixture and the injected substrate.
    monkeypatch.delenv("SOCRATA_APP_TOKEN", raising=False)
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(confident_r5_substrate())

    response = client.get(f"/api/v1/properties/{BBL}/scenario")
    assert response.status_code == 200
    validate_scenario_document(response.json())


def test_as7_existing_property_route_still_works(client):
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    response = client.get(f"/api/v1/properties/{BBL}")
    assert response.status_code == 200
    assert response.json()["identity"]["bbl"] == BBL
