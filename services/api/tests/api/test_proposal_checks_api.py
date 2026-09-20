"""Acceptance pack for POST /api/v1/proposal-checks (task M5-T057, D-076 phase B3 slice 1).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted B2 check
engine; it is feature-flag gated OFF by default (reuses ``INTERNAL_RULE_EVAL_ENABLED``), mirroring
the sibling internal routes. Every G5-recorded precondition BP-1..BP-7 is exercised here.

- AS-1 (end-to-end): the B2 rectangle fixture posted through the route returns the exact accepted
  arithmetic (coverage FAIL 0.125; height PASS 30<=60 attested / COULD_NOT_CHECK unattested; the
  two non-commensurable checks COULD_NOT_CHECK) with the scenario label and summary counts; flag
  off returns the same generic 404 as the sibling route.
- AS-2 (BP-2/BP-3): over-length / bad-charset scenario_label / proposal_id refuse typed at the
  boundary; a payload engineered to raise the B0 validator's uncapped vertex repr returns a
  response whose embedded detail is length-capped (the uncapped-repr class cannot reach a client);
  a propagated ProposalDerivationError is typed + bounded too.
- AS-3 (BP-4): route-level caps documented with shown worst-case arithmetic (<~1e6 segment tests);
  an at-cap payload completes, an above-cap payload refuses typed naming the cap.
- AS-4 (BP-5): a lot_rule_facts value of the wrong type OR outside its enum-constrained DOMAIN
  (derived from the registry's own declared vocabulary, never invented) refuses typed naming the
  field before the engine runs; an unmapped key is surfaced as unmapped and never fed.
- AS-5 (BP-1/BP-6): the route's only engine entry is check_proposal (import + source proof); no
  scenario document / contract version is constructed anywhere in the response.
- AS-8 (proof): the documented (status, state) matrix; oversized body -> 413; malformed / empty /
  non-object body -> typed 422.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import proposal_checks_api as mod
from app.api.v1.proposal_checks_api import (
    MAX_BODY_BYTES,
    MAX_LABEL_LEN,
    PROPOSAL_CHECKS_STATUS_STATE_MATRIX,
    ROUTE_MAX_EXTERIOR_WALLS,
    ROUTE_MAX_LOT_LINE_SEGMENTS,
    ROUTE_MAX_STREET_LINES,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.main import app
from app.rules.registry import RuleRegistry
from app.rules.snapshots import SnapshotStore

_URL = "/api/v1/proposal-checks"
_JSON_HEADERS = {"content-type": "application/json"}

# The B2 fixture bundle (synthetic rulesets + hand-computed rectangle case) lives under the rules
# suite; the route test reuses it read-only via the registry dependency override so AS-1 asserts
# the exact accepted synthetic arithmetic (coverage ceiling 0.5, height allowance 60 ft).
_B2_FIXTURES = Path(__file__).resolve().parents[1] / "rules" / "fixtures" / "proposal_checks"
_CASE_PATH = _B2_FIXTURES / "rectangle_case.json"

_X0 = 1000000.0
_Y0 = 200000.0


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------
def _enable_flag(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture()
def fixture_registry() -> RuleRegistry:
    return RuleRegistry(
        _B2_FIXTURES / "rulesets", snapshots=SnapshotStore(_B2_FIXTURES / "snapshots")
    ).load()


@pytest.fixture()
def client_with_registry(monkeypatch, fixture_registry):
    """A client whose route resolves the SYNTHETIC B2 fixture registry: monkeypatch the module's
    registry provider (auto-reverted at teardown, so no override leaks into the shared app)."""
    monkeypatch.setattr(mod, "get_proposal_check_registry", lambda: fixture_registry)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture()
def case() -> dict:
    return json.loads(_CASE_PATH.read_text(encoding="utf-8"))


def _payload(case: dict, *, attested: bool, **overrides) -> dict:
    facts_key = "lot_rule_facts_attested" if attested else "lot_rule_facts"
    body = {
        "proposed_massing": case["block"],
        "lot": case["lot"],
        "lot_rule_facts": case[facts_key],
        "scenario_label": case["scenario_label"],
        "proposal_id": case["proposal_id"],
    }
    body.update(overrides)
    return body


def _valid_block() -> dict:
    return {
        "outline": {
            "srid": 2263,
            "vertices": [
                [_X0, _Y0],
                [_X0 + 100.0, _Y0],
                [_X0 + 100.0, _Y0 + 80.0],
                [_X0, _Y0 + 80.0],
                [_X0, _Y0],
            ],
        },
        "levels": [{"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0}],
        "exterior_walls": [{"id": "south", "start_vertex_index": 0, "end_vertex_index": 1}],
        "provenance": {"author": "architect@example.com", "kind": "proposed",
                       "editor_version": "proposal-editor/0.1.0"},
    }


def _minimal_lot() -> dict:
    return {
        "area_sq_ft": 8000.0,
        "area_provenance": {"source_id": "synthetic"},
        "lot_line_segments": [],
        "street_lines": [],
    }


def _minimal_body(**overrides) -> dict:
    body = {
        "proposed_massing": _valid_block(),
        "lot": _minimal_lot(),
        "lot_rule_facts": {"zoning_district": "R5"},
        "scenario_label": "scenario-A",
        "proposal_id": "prop-1",
    }
    body.update(overrides)
    return body


def _by_id(results: list[dict]) -> dict[str, dict]:
    return {r["check_id"]: r for r in results}


# ---------------------------------------------------------------------------
# Flag gate / posture
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404_no_leak(client, case):
    resp = client.post(_URL, json=_payload(case, attested=True))
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_route_absent_from_openapi(client):
    assert _URL not in app.openapi().get("paths", {})


# ---------------------------------------------------------------------------
# AS-1: rectangle fixture end-to-end through HTTP (attested + unattested)
# ---------------------------------------------------------------------------
def test_as1_attested_end_to_end(client_with_registry, monkeypatch, case):
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(_URL, json=_payload(case, attested=True))
    assert resp.status_code == 200, resp.json()
    assert resp.headers["X-Correlation-ID"]
    body = resp.json()
    assert body["scenario_label"] == "scenario-A-baseline"
    assert body["proposal_id"] == "prop-0001"
    assert body["summary"] == {"pass": 1, "fail": 1, "could_not_check": 2, "total": 4}

    results = _by_id(body["results"])
    cov = results["lot_coverage_ratio"]
    assert cov["outcome"] == "fail"
    assert cov["provided_value"] == pytest.approx(0.625)
    assert cov["required_value"] == pytest.approx(0.5)
    assert cov["shortfall"] == pytest.approx(0.125)
    assert cov["direction"] == "maximum"

    height = results["building_height"]
    assert height["outcome"] == "pass"
    assert height["provided_value"] == pytest.approx(30.0)
    assert height["required_value"] == pytest.approx(60.0)
    assert height["shortfall"] is None

    for check_id in ("rear_yard_depth", "residential_far_floor_area"):
        res = results[check_id]
        assert res["outcome"] == "could_not_check"
        assert res["could_not_check_reason"] == "provided_fact_not_commensurate"
        assert res["required_value"] is None


def test_as1_unattested_height_is_could_not_check(client_with_registry, monkeypatch, case):
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(_URL, json=_payload(case, attested=False))
    assert resp.status_code == 200, resp.json()
    body = resp.json()
    assert body["summary"] == {"pass": 0, "fail": 1, "could_not_check": 3, "total": 4}
    results = _by_id(body["results"])
    assert results["lot_coverage_ratio"]["outcome"] == "fail"
    height = results["building_height"]
    assert height["outcome"] == "could_not_check"
    assert height["could_not_check_reason"] == "allowance_unresolved"


# ---------------------------------------------------------------------------
# AS-2 (BP-2): scenario_label / proposal_id boundary
# ---------------------------------------------------------------------------
def test_bp2_over_length_scenario_label_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(scenario_label="s" * (MAX_LABEL_LEN + 1)))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "scenario_label"
    assert "MAX_LABEL_LEN" in body["message"]
    # The offending value is never echoed - only its length.
    assert "s" * 50 not in body["message"]


def test_bp2_bad_charset_scenario_label_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(scenario_label="scn<script>"))
    assert resp.status_code == 422
    assert resp.json()["field"] == "scenario_label"


def test_bp2_empty_scenario_label_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(scenario_label="   "))
    assert resp.status_code == 422
    assert resp.json()["field"] == "scenario_label"


def test_bp2_bad_charset_proposal_id_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(proposal_id="p/../../etc"))
    assert resp.status_code == 422
    assert resp.json()["field"] == "proposal_id"


def test_bp2_trailing_newline_scenario_label_refused(client, monkeypatch):
    # Full-string validation: an otherwise-valid label with a TRAILING NEWLINE must refuse. A
    # prefix (re.match) or a trailing ``$`` would accept "scenario-A\n" (``$`` matches just
    # before the newline); fullmatch over the whole value catches it.
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(scenario_label="scenario-A\n"))
    assert resp.status_code == 422
    assert resp.json()["field"] == "scenario_label"


def test_bp2_trailing_newline_proposal_id_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(proposal_id="prop-1\n"))
    assert resp.status_code == 422
    assert resp.json()["field"] == "proposal_id"


def test_bp2_null_proposal_id_is_accepted(client_with_registry, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(_URL, json=_minimal_body(proposal_id=None))
    assert resp.status_code == 200, resp.json()
    assert resp.json()["proposal_id"] is None


# ---------------------------------------------------------------------------
# AS-2 (BP-3): every error path length-caps embedded values
# ---------------------------------------------------------------------------
def test_bp3_uncapped_vertex_repr_is_length_capped(client, monkeypatch):
    # A 2-element vertex whose first element is a long string is NOT a wall id / provenance
    # string, so it passes the DB-034(b) gate ceilings and reaches the accepted B0 validator,
    # which embeds an UNCAPPED repr of the bad vertex (G5-3). The route must length-cap it.
    _enable_flag(monkeypatch)
    attacker = "x" * 600
    block = _valid_block()
    block["outline"]["vertices"][0] = [attacker, _Y0]
    resp = client.post(_URL, json=_minimal_body(proposed_massing=block))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "proposed_massing.outline.vertices[0]"
    message = body["message"]
    assert attacker not in message  # the uncapped repr never reaches the client
    assert "x" * 450 not in message
    assert "truncated" in message
    assert len(message) < 500


def test_bp3_propagated_derivation_error_is_typed_and_bounded(client, monkeypatch):
    # A structurally valid block with a zero lot area passes the gate but raises a
    # ProposalDerivationError inside derive_proposal (before any rule evaluation). The route maps
    # it to a typed, bounded 422 naming the field - no stack trace / internal string.
    _enable_flag(monkeypatch)
    lot = _minimal_lot()
    lot["area_sq_ft"] = 0.0
    resp = client.post(_URL, json=_minimal_body(lot=lot))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot.area_sq_ft"
    blob = json.dumps(body).lower()
    for bad in ("traceback", 'file "', "site-packages", "/services/api", "\\services\\api"):
        assert bad not in blob


# ---------------------------------------------------------------------------
# AS-3 (BP-4): route-level compute caps, tighter than the library ceilings
# ---------------------------------------------------------------------------
def test_bp4_documented_worst_case_product_under_1e6():
    # The exact arithmetic the module comment records: walls x (lot-lines + street-lines).
    worst_case = ROUTE_MAX_EXTERIOR_WALLS * (
        ROUTE_MAX_LOT_LINE_SEGMENTS + ROUTE_MAX_STREET_LINES
    )
    assert worst_case == 600_000
    assert worst_case < 1_000_000
    # Each route cap is strictly below its B2 library counterpart (defense in depth).
    from app.rules.proposal_checks import MAX_LOT_LINE_SEGMENTS, MAX_STREET_LINES
    from app.scenario.proposal import MAX_EXTERIOR_WALLS
    assert ROUTE_MAX_EXTERIOR_WALLS < MAX_EXTERIOR_WALLS
    assert ROUTE_MAX_LOT_LINE_SEGMENTS < MAX_LOT_LINE_SEGMENTS
    assert ROUTE_MAX_STREET_LINES < MAX_STREET_LINES


def test_bp4_over_wall_cap_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    block = _valid_block()
    # Junk walls: the O(1) count refusal fires BEFORE the gate/validator, so shape is irrelevant.
    block["exterior_walls"] = [{"id": f"w{i}"} for i in range(ROUTE_MAX_EXTERIOR_WALLS + 1)]
    resp = client.post(_URL, json=_minimal_body(proposed_massing=block))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "proposed_massing.exterior_walls"
    assert "ROUTE_MAX_EXTERIOR_WALLS" in body["message"]


def test_bp4_over_lot_line_cap_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    lot = _minimal_lot()
    lot["lot_line_segments"] = [
        {"id": f"LL{i}", "start": [_X0, _Y0], "end": [_X0, _Y0 + 1.0]}
        for i in range(ROUTE_MAX_LOT_LINE_SEGMENTS + 1)
    ]
    resp = client.post(_URL, json=_minimal_body(lot=lot))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot.lot_line_segments"
    assert "ROUTE_MAX_LOT_LINE_SEGMENTS" in body["message"]


def test_bp4_over_street_line_cap_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    lot = _minimal_lot()
    lot["street_lines"] = [
        {"wall_id": "south", "start": [_X0, _Y0], "end": [_X0 + 1.0, _Y0], "attestation": {}}
        for _ in range(ROUTE_MAX_STREET_LINES + 1)
    ]
    resp = client.post(_URL, json=_minimal_body(lot=lot))
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot.street_lines"


def test_bp4_at_lot_line_cap_completes(client_with_registry, monkeypatch, case):
    # Exactly at the cap: passes the count check and runs the full engine (a bounded worst-case
    # operation count from the route caps, not a wall-clock/timing claim).
    _enable_flag(monkeypatch)
    lot = dict(case["lot"])
    lot["lot_line_segments"] = [
        {"id": f"LL{i}", "start": [999990.0, 199990.0], "end": [999990.0, 200060.0]}
        for i in range(ROUTE_MAX_LOT_LINE_SEGMENTS)
    ]
    resp = client_with_registry.post(
        _URL, json=_payload(case, attested=True, lot=lot)
    )
    assert resp.status_code == 200, resp.json()


# ---------------------------------------------------------------------------
# AS-4 (BP-5): lot_rule_facts value-type validation + unmapped surfacing
# ---------------------------------------------------------------------------
def test_bp5_bad_bool_fact_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(
        _URL,
        json=_minimal_body(lot_rule_facts={"zoning_district": "R5", "overlay_present": "yes"}),
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot_rule_facts.overlay_present"
    assert "boolean" in body["message"]


def test_bp5_bad_string_fact_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(lot_rule_facts={"zoning_district": 5}))
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.zoning_district"


def test_bp5_bad_number_fact_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(
        _URL,
        json=_minimal_body(lot_rule_facts={"zoning_district": "R5", "lot_depth_ft": "100"}),
    )
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.lot_depth_ft"


def test_bp5_bool_is_not_a_number(client, monkeypatch):
    # bool is a subclass of int; the type guard must still reject it for a numeric fact.
    _enable_flag(monkeypatch)
    resp = client.post(
        _URL,
        json=_minimal_body(lot_rule_facts={"zoning_district": "R5", "lot_depth_ft": True}),
    )
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.lot_depth_ft"


def test_bp5_unmapped_fact_is_surfaced_not_fed(client_with_registry, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(
        _URL,
        json=_minimal_body(
            lot_rule_facts={"zoning_district": "R5", "boobytrap_input": {"x": 1}}
        ),
    )
    assert resp.status_code == 200, resp.json()
    body = resp.json()
    assert "boobytrap_input" in body["unmapped_lot_facts"]
    # The unmapped key was never fed to a rule input (absent from the fed-input bindings).
    assert "boobytrap_input" not in body["rule_input_bindings"]


def test_bp5_out_of_domain_street_width_class_refused(client_with_registry, monkeypatch):
    # BP-5 domain: street_width_class carries a declared enum {wide, narrow} in the registry's OWN
    # input vocabulary; a value outside it is a typed 422 naming the field, BEFORE the engine runs
    # (the accepted set is derived from the registry, never an invented list).
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(
        _URL,
        json=_minimal_body(
            lot_rule_facts={"zoning_district": "R5", "street_width_class": "medium"}
        ),
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot_rule_facts.street_width_class"
    # The accepted vocabulary is surfaced; the offending value is never echoed.
    assert "wide" in body["message"] and "narrow" in body["message"]
    assert "medium" not in body["message"]


def test_bp5_out_of_domain_value_derived_from_the_registry(client_with_registry, monkeypatch):
    # The domain is the registry's OWN declared vocabulary, not an invented list: the synthetic
    # fixture rules declare zoning_district enum {R5}, so R6 is out of domain FOR THIS REGISTRY
    # and refuses typed at the boundary before the engine runs.
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(
        _URL, json=_minimal_body(lot_rule_facts={"zoning_district": "R6"})
    )
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.zoning_district"


def test_bp5_in_domain_street_width_class_is_accepted(client_with_registry, monkeypatch, case):
    # The positive path: an in-domain value ("narrow") is NOT domain-rejected and the engine runs.
    _enable_flag(monkeypatch)
    facts = {"zoning_district": "R5", "street_width_class": "narrow"}
    resp = client_with_registry.post(_URL, json=_payload(case, attested=True, lot_rule_facts=facts))
    assert resp.status_code == 200, resp.json()


# ---------------------------------------------------------------------------
# AS-5 (BP-1/BP-6): only check_proposal; no emission
# ---------------------------------------------------------------------------
def test_bp1_only_check_proposal_entry_is_called():
    source = Path(mod.__file__).read_text(encoding="utf-8")
    assert "check_proposal(" in source  # the single engine entry is invoked
    assert "derive_proposal(" not in source  # never the derivation entry directly
    assert not hasattr(mod, "derive_proposal")


def test_bp6_response_emits_no_scenario_document_or_contract_version(
    client_with_registry, monkeypatch, case
):
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(_URL, json=_payload(case, attested=True))
    body = resp.json()
    for forbidden in ("contract_version", "scenario_id", "constraint_completeness"):
        assert forbidden not in body
    blob = json.dumps(body).lower()
    assert "contract_version" not in blob
    assert "1.1.0" not in blob


# ---------------------------------------------------------------------------
# AS-8: matrix + body discipline
# ---------------------------------------------------------------------------
def test_status_state_matrix_is_the_documented_set():
    assert PROPOSAL_CHECKS_STATUS_STATE_MATRIX == frozenset(
        {
            (200, None),
            (404, None),
            (413, "payload_too_large"),
            (422, "validation_error"),
            (500, "internal_error"),
        }
    )


def test_oversized_body_is_413_before_parse(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, content=b" " * (MAX_BODY_BYTES + 1), headers=_JSON_HEADERS)
    assert resp.status_code == 413
    assert resp.json()["state"] == "payload_too_large"
    assert resp.headers["X-Correlation-ID"]


def test_malformed_json_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, content=b"{ not json", headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_empty_body_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, content=b"", headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_non_object_body_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=[1, 2, 3])
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_nan_body_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    raw = b'{"scenario_label": "s", "lot": {}, "proposed_massing": {}, "x": NaN}'
    resp = client.post(_URL, content=raw, headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_missing_proposed_massing_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    body = _minimal_body()
    del body["proposed_massing"]
    resp = client.post(_URL, json=body)
    assert resp.status_code == 422
    assert resp.json()["field"] == "proposed_massing"
