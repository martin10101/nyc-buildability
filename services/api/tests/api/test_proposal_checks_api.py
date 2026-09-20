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
from typing import cast

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import _proposal_fact_domains as fd
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
from app.rules.models import InputSpec
from app.rules.registry import RuleRegistry
from app.rules.snapshots import SnapshotStore


# ---------------------------------------------------------------------------
# M5-T061 / DB-039: a minimal duck-typed registry for the registry-DERIVED domain/bounds unit
# tests. derive_input_domains only reads rule_ids() and rule(id).inputs (each an InputSpec), so a
# tiny stand-in lets us assert the numeric-bound derivation against KNOWN specs without touching
# the (forbidden) fixture rulesets. Instances are weakref-able, so input_domains_for's
# WeakKeyDictionary memo keys them correctly.
class _FakeRule:
    def __init__(self, inputs):
        self.inputs = inputs


class _FakeRegistry:
    def __init__(self, rules: dict):
        self._rules = rules

    def rule_ids(self):
        return list(self._rules)

    def rule(self, rule_id):
        return self._rules[rule_id]

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
    # [ORCH-CORRECTED per G4-F-1]: bind the cap VALUE exactly (the marker starts at exactly the
    # 400-char prefix boundary), not just a <500 window a drifted cap could still satisfy.
    assert message.index("...<truncated;") == 400


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
    # [ORCH-CORRECTED per G5-F2]: the engine call is now offloaded via
    # functools.partial(check_proposal, ...) inside run_in_threadpool, so the entry reference is
    # the partial target rather than a direct call token. The invocation-count property is bound
    # separately by test_bp1_check_proposal_called_exactly_once (the stronger G4-gap-5 binding).
    assert "functools.partial(" in source and "check_proposal," in source
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


# ---------------------------------------------------------------------------
# [ORCH-CORRECTED per G3-F1/F2, G4 gaps 1/2/5, G5-F1/F2] rework bindings (seq 122)
# ---------------------------------------------------------------------------
def test_bounded_field_helper_caps_hard():
    # BP-3 (G3-F1/G5-F1): the refusal `field` is capped on every response/log path.
    long_field = "A" * 10_000
    bounded = mod._bounded_field(long_field)
    assert bounded is not None
    assert bounded.startswith("A" * mod.MAX_FIELD_LEN)
    assert bounded.endswith("chars total>")
    assert len(bounded) < mod.MAX_FIELD_LEN + 50
    assert mod._bounded_field(None) is None
    assert mod._bounded_field("lot.area_sq_ft") == "lot.area_sq_ft"


def test_lot_line_id_over_cap_refused_and_bounded(client, monkeypatch):
    # G5-F1 root fix: an attacker-length lot-line id is refused typed AT THE BOUNDARY; it can
    # reach neither a 422 field, a 200 provenance id, nor a log record. Removing the id bound
    # flips this red: the (geometrically valid) payload would then return 200.
    _enable_flag(monkeypatch)
    evil = "<script>alert(1)</script>" + "A" * 100_000
    lot = _minimal_lot()
    lot["lot_line_segments"] = [{"id": evil, "start": [_X0, _Y0], "end": [_X0, _Y0 + 1.0]}]
    resp = client.post(_URL, json=_minimal_body(lot=lot))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot.lot_line_segments[0].id"
    blob = json.dumps(body)
    assert "<script>" not in blob
    assert "A" * 250 not in blob
    assert len(blob) < 2_000


def test_street_wall_id_bad_charset_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    lot = _minimal_lot()
    lot["street_lines"] = [
        {"wall_id": "<b>south</b>", "start": [_X0, _Y0], "end": [_X0 + 1.0, _Y0],
         "attestation": {}}
    ]
    resp = client.post(_URL, json=_minimal_body(lot=lot))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot.street_lines[0].wall_id"
    assert "<b>" not in json.dumps(body)


def test_area_provenance_over_ceiling_refused(client, monkeypatch):
    # G5-F1 200-path: the caller blob the engine republishes verbatim is size-bounded, typed.
    _enable_flag(monkeypatch)
    lot = _minimal_lot()
    lot["area_provenance"] = {"evil": "v" * (mod.MAX_PROVENANCE_BYTES + 100)}
    resp = client.post(_URL, json=_minimal_body(lot=lot))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot.area_provenance"
    assert "MAX_PROVENANCE_BYTES" in body["message"]
    assert "v" * 100 not in json.dumps(body)


def test_street_attestation_over_ceiling_refused(client, monkeypatch):
    _enable_flag(monkeypatch)
    lot = _minimal_lot()
    lot["street_lines"] = [
        {"wall_id": "south", "start": [_X0, _Y0], "end": [_X0 + 1.0, _Y0],
         "attestation": {"blob": "w" * (mod.MAX_PROVENANCE_BYTES + 100)}}
    ]
    resp = client.post(_URL, json=_minimal_body(lot=lot))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot.street_lines[0].attestation"
    assert "w" * 100 not in json.dumps(body)


def test_lot_rule_facts_key_bound_and_unmapped_stays_bounded(
    client_with_registry, monkeypatch, case
):
    # G3-F3 / G5-F1 200-path: fact KEYS get the BP-2 label discipline (they are surfaced in
    # unmapped_lot_facts and rendered by B3); a conforming unmapped key still surfaces (BP-5).
    _enable_flag(monkeypatch)
    bad_charset = _payload(
        case, attested=True, lot_rule_facts={"<img src=x onerror=alert(1)>": True}
    )
    resp = client_with_registry.post(_URL, json=bad_charset)
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot_rule_facts"
    assert "<img" not in json.dumps(body)

    over_len = _payload(
        case, attested=True, lot_rule_facts={"k" * (MAX_LABEL_LEN + 1): True}
    )
    resp2 = client_with_registry.post(_URL, json=over_len)
    assert resp2.status_code == 422
    assert "k" * 50 not in json.dumps(resp2.json())

    facts = dict(case["lot_rule_facts_attested"])
    facts["mystery_fact"] = True
    resp3 = client_with_registry.post(_URL, json=_payload(case, attested=True,
                                                          lot_rule_facts=facts))
    assert resp3.status_code == 200, resp3.json()
    assert "mystery_fact" in resp3.json()["unmapped_lot_facts"]


def test_forced_500_is_generic_and_bounded(client, monkeypatch):
    # G3-F2(b) / G4 gap 1: a REAL 500 emission from THIS route (registry unavailable). Exact
    # key set = any added leak field fails; no exception text/path reaches the client.
    _enable_flag(monkeypatch)

    def boom():
        raise RuntimeError("boom-internal-secret")

    monkeypatch.setattr(mod, "get_proposal_check_registry", boom)
    resp = client.post(_URL, json=_minimal_body())
    assert resp.status_code == 500
    body = resp.json()
    assert set(body) == {"state", "message", "correlation_id"}
    assert body["state"] == "internal_error"
    blob = json.dumps(body).lower()
    for bad in ("boom", "runtimeerror", "traceback", "/services/api"):
        assert bad not in blob


def test_lone_surrogate_body_refused_typed(client, monkeypatch):
    # G4 gap 2: the checks route's OWN strict-JSON guard, surrogate half (the NaN half is bound
    # elsewhere). The raw \ud800 escape parses, then trips the renderer-parity guard.
    _enable_flag(monkeypatch)
    raw = (
        '{"proposed_massing": {"a": 1}, "lot": {}, "lot_rule_facts": {}, '
        '"scenario_label": "s", "proposal_id": "p", "x": "\\ud800"}'
    )
    resp = client.post(_URL, content=raw.encode("ascii"), headers=_JSON_HEADERS)
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "validation_error"
    assert "surrogate" in body["message"]


def test_bp1_check_proposal_called_exactly_once(client_with_registry, monkeypatch, case):
    # G4 gap 5: bind "exactly ONCE", not just "which entry" - a second call flips this red.
    calls: list[int] = []
    real = mod.check_proposal

    def spy(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(mod, "check_proposal", spy)
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(_URL, json=_payload(case, attested=True))
    assert resp.status_code == 200, resp.json()
    assert len(calls) == 1


def test_bp4_outline_position_over_cap_refused(client, monkeypatch):
    # G5-F2: the O(n^2) simplicity surface is route-capped BEFORE any validation pass.
    _enable_flag(monkeypatch)
    block = _valid_block()
    n = mod.ROUTE_MAX_TOTAL_OUTLINE_POSITIONS + 1
    block["outline"]["vertices"] = [[_X0 + i, _Y0] for i in range(n)]
    resp = client.post(_URL, json=_minimal_body(proposed_massing=block))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "proposed_massing"
    assert "ROUTE_MAX_TOTAL_OUTLINE_POSITIONS" in body["message"]


def test_bp4_corrected_worst_case_arithmetic():
    # G5-F2: the documented worst case now covers BOTH compute surfaces - the wall-by-segment
    # product AND the double O(n^2) simplicity pass under the route's outline cap - and the
    # outline cap sits strictly below the inherited DB-034(a) budget (also an import-time guard).
    from app.scenario.proposal_input_gate import MAX_TOTAL_VERTICES
    product = ROUTE_MAX_EXTERIOR_WALLS * (
        ROUTE_MAX_LOT_LINE_SEGMENTS + ROUTE_MAX_STREET_LINES
    )
    n = mod.ROUTE_MAX_TOTAL_OUTLINE_POSITIONS
    simplicity_two_passes = 2 * (n * (n - 1) // 2)
    assert product == 600_000
    assert simplicity_two_passes == 1_438_800
    assert product + simplicity_two_passes < 2_100_000
    assert n < MAX_TOTAL_VERTICES


def test_cpu_bound_calls_run_off_the_event_loop(client_with_registry, monkeypatch, case):
    # G5-F2: both CPU-bound calls (gate+B0 validation, engine check) are offloaded through
    # run_in_threadpool - removing either offload flips this red.
    offloaded: list[str] = []
    real = mod.run_in_threadpool

    async def spy(fn, *args, **kwargs):
        offloaded.append(getattr(fn, "func", fn).__name__)
        return await real(fn, *args, **kwargs)

    monkeypatch.setattr(mod, "run_in_threadpool", spy)
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(_URL, json=_payload(case, attested=True))
    assert resp.status_code == 200, resp.json()
    assert "validate_proposed_massing_input" in offloaded
    assert "check_proposal" in offloaded


# ===========================================================================
# M5-T061 / DB-039 route-hardening fold-ins
# ===========================================================================
# AS-1 (numeric bounds): registry-DERIVED numeric acceptance windows, never an invented limit.
# ---------------------------------------------------------------------------
def _num_input(**bounds) -> InputSpec:
    return InputSpec(name="lot_depth_ft", type="number", required=True, **bounds)


def test_derive_input_domains_numeric_bounds_are_registry_derived():
    # DB-039(d): each kept bound is copied from an InputSpec field; the window rejects out-of-range
    # values in EACH direction and accepts an in-range value (mutation-flips-red per direction).
    reg = _FakeRegistry({"r1": _FakeRule([_num_input(minimum=10.0, maximum=500.0)])})
    bounds = fd.derive_input_domains(cast(RuleRegistry, reg)).numeric["lot_depth_ft"]
    assert bounds.minimum == 10.0 and bounds.maximum == 500.0
    assert bounds.refusal_reason(5.0) is not None  # below the declared floor
    assert bounds.refusal_reason(600.0) is not None  # above the declared ceiling
    assert bounds.refusal_reason(100.0) is None  # inside the window


def test_derive_input_domains_exclusive_bounds_reject_the_endpoint():
    reg = _FakeRegistry({"r1": _FakeRule([_num_input(exclusive_minimum=0.0)])})
    bounds = fd.derive_input_domains(cast(RuleRegistry, reg)).numeric["lot_depth_ft"]
    assert bounds.exclusive_minimum == 0.0
    assert bounds.refusal_reason(0.0) is not None  # exclusive: the endpoint itself is refused
    assert bounds.refusal_reason(0.5) is None


def test_numeric_bound_only_when_every_declaring_rule_bounds_the_direction():
    # DB-039(d) conservatism: a direction is bounded only when EVERY declaring rule bounds it, and
    # the kept bound is the MOST PERMISSIVE. r2 leaves the upper open -> no ceiling is enforced.
    reg = _FakeRegistry(
        {
            "r1": _FakeRule([_num_input(minimum=10.0, maximum=500.0)]),
            "r2": _FakeRule([_num_input(minimum=20.0)]),  # no maximum
        }
    )
    bounds = fd.derive_input_domains(cast(RuleRegistry, reg)).numeric["lot_depth_ft"]
    assert bounds.minimum == 10.0  # most-permissive floor across the two rules
    assert bounds.maximum is None and bounds.exclusive_maximum is None
    assert bounds.refusal_reason(10.0) is None  # inclusive floor endpoint accepted
    assert bounds.refusal_reason(9.0) is not None  # below every rule's floor
    assert bounds.refusal_reason(1e9) is None  # a rule leaves the ceiling open -> fed unchanged


def test_numeric_input_left_unbounded_has_no_window():
    # A caller-mappable numeric that no rule bounds is absent from the numeric map (fed unchanged).
    reg = _FakeRegistry({"r1": _FakeRule([_num_input()])})
    assert "lot_depth_ft" not in fd.derive_input_domains(cast(RuleRegistry, reg)).numeric


def test_route_numeric_fact_out_of_bounds_refused_before_engine(client, monkeypatch):
    # AS-1 end-to-end: an out-of-bounds numeric fact is a typed 422 naming the field, BEFORE the
    # engine or gate runs; the offending value is never echoed.
    reg = _FakeRegistry(
        {
            "r1": _FakeRule(
                [
                    InputSpec(name="zoning_district", type="string", required=True,
                              enum=("R5",)),
                    _num_input(minimum=10.0, maximum=1000.0),
                ]
            )
        }
    )
    fd.clear_input_domain_cache()
    monkeypatch.setattr(mod, "get_proposal_check_registry", lambda: reg)
    _enable_flag(monkeypatch)
    resp = client.post(
        _URL,
        json=_minimal_body(lot_rule_facts={"zoning_district": "R5", "lot_depth_ft": 999999.0}),
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "lot_rule_facts.lot_depth_ft"
    assert "999999" not in json.dumps(body)  # the value is never echoed (accepted range only)


# ---------------------------------------------------------------------------
# AS-2 (ordering): the cheap registry-derived domain/bounds check runs BEFORE the O(n^2) gate.
# ---------------------------------------------------------------------------
def test_domain_check_runs_before_the_input_gate(client_with_registry, monkeypatch):
    # An out-of-domain fact refuses WITHOUT paying the O(n^2) input gate: the gate spy must record
    # ZERO calls. Restoring the old ordering (gate first) flips this red.
    calls: list[int] = []
    real = mod.validate_proposed_massing_input

    def spy(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(mod, "validate_proposed_massing_input", spy)
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(
        _URL, json=_minimal_body(lot_rule_facts={"zoning_district": "R6"})
    )
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.zoning_district"
    assert calls == []  # the expensive gate never ran - the domain check fired first


def test_registry_unavailable_500_is_recorded_before_the_gate(client, monkeypatch):
    # AS-2: the registry-unavailable path stays a bounded 500, now at its earlier position (before
    # the gate). The gate must NOT run when the registry cannot be resolved.
    calls: list[int] = []
    real = mod.validate_proposed_massing_input

    def spy(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    def boom():
        raise RuntimeError("registry-load-failed")

    monkeypatch.setattr(mod, "validate_proposed_massing_input", spy)
    monkeypatch.setattr(mod, "get_proposal_check_registry", boom)
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body())
    assert resp.status_code == 500
    assert resp.json()["state"] == "internal_error"
    assert calls == []  # resolved (and failed) before the gate ran


# ---------------------------------------------------------------------------
# AS-3 (memoization): the derivation runs once per registry object across repeated requests.
# ---------------------------------------------------------------------------
def test_domain_derivation_memoized_once_per_registry(client_with_registry, monkeypatch, case):
    fd.clear_input_domain_cache()
    calls: list[int] = []
    real = fd.derive_input_domains

    def spy(registry):
        calls.append(1)
        return real(registry)

    monkeypatch.setattr(fd, "derive_input_domains", spy)
    _enable_flag(monkeypatch)
    for _ in range(3):
        resp = client_with_registry.post(_URL, json=_payload(case, attested=True))
        assert resp.status_code == 200, resp.json()
    assert len(calls) == 1  # derived ONCE for the injected registry, then served from the memo


def test_test_injected_registry_derives_its_own_domains(client_with_registry, monkeypatch):
    # The memo is keyed by registry identity: the test-injected fixture registry derives its OWN
    # (fixture) vocabulary, so R6 (absent from the fixture's zoning_district enum) refuses.
    fd.clear_input_domain_cache()
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(
        _URL, json=_minimal_body(lot_rule_facts={"zoning_district": "R6"})
    )
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.zoning_district"


# ---------------------------------------------------------------------------
# AS-4 (wall-id charset): exterior_walls[].id gets the BP-2 label discipline.
# ---------------------------------------------------------------------------
def test_wall_id_bad_charset_refused(client, monkeypatch):
    # DB-039(h): a block wall id shares one identity space with a street line's wall_id (already
    # charset-bound), so a wall id with markup refuses typed AT THE BOUNDARY. Removing
    # _validate_exterior_wall_ids flips this red (the markup id would ride through to the gate).
    _enable_flag(monkeypatch)
    block = _valid_block()
    block["exterior_walls"] = [
        {"id": "<b>south</b>", "start_vertex_index": 0, "end_vertex_index": 1}
    ]
    resp = client.post(_URL, json=_minimal_body(proposed_massing=block))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "proposed_massing.exterior_walls[0].id"
    assert "<b>" not in json.dumps(body)


def test_wall_id_over_length_refused_length_only(client, monkeypatch):
    _enable_flag(monkeypatch)
    block = _valid_block()
    block["exterior_walls"] = [
        {"id": "w" * (MAX_LABEL_LEN + 1), "start_vertex_index": 0, "end_vertex_index": 1}
    ]
    resp = client.post(_URL, json=_minimal_body(proposed_massing=block))
    assert resp.status_code == 422
    body = resp.json()
    assert body["field"] == "proposed_massing.exterior_walls[0].id"
    assert "MAX_LABEL_LEN" in body["message"]
    assert "w" * 50 not in json.dumps(body)  # the value is never echoed - length only


def test_wall_id_non_string_left_to_the_validator(client, monkeypatch):
    # The route wall-id guard only narrows STRING ids (so a matching string pair cannot diverge);
    # a non-string id is left to the B0 validator's own shape refusal. Because the validator names
    # the SAME field for a bad wall id, the discriminator is the ORDERING: the route guard sits
    # BEFORE the gate, so if it had fired the gate would never run. Proof: the gate DOES run for a
    # non-string id (spy records the call), i.e. the route guard skipped it.
    calls: list[int] = []
    real = mod.validate_proposed_massing_input

    def spy(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(mod, "validate_proposed_massing_input", spy)
    _enable_flag(monkeypatch)
    block = _valid_block()
    block["exterior_walls"] = [{"id": 123, "start_vertex_index": 0, "end_vertex_index": 1}]
    resp = client.post(_URL, json=_minimal_body(proposed_massing=block))
    assert resp.status_code == 422
    assert calls == [1]  # the gate ran - the route guard did not short-circuit the non-string id


def test_wall_id_conforming_round_trips_the_accepted_arithmetic(
    client_with_registry, monkeypatch, case
):
    # AS-4 positive: the fixture's conforming wall ids (W-S/W-E/W-N/W-W - the same charset a street
    # wall_id must satisfy) still round-trip the accepted rectangle arithmetic byte-identically.
    _enable_flag(monkeypatch)
    resp = client_with_registry.post(_URL, json=_payload(case, attested=True))
    assert resp.status_code == 200, resp.json()
    cov = _by_id(resp.json()["results"])["lot_coverage_ratio"]
    assert cov["provided_value"] == pytest.approx(0.625)
    assert cov["shortfall"] == pytest.approx(0.125)


# ---------------------------------------------------------------------------
# AS-5 (coverage closure): at-cap-exact boundaries + every _build_lot_context shape branch.
# ---------------------------------------------------------------------------
def test_at_cap_scenario_label_accepted(client_with_registry, monkeypatch, case):
    # label == MAX_LABEL_LEN is accepted (the refusal fires only ABOVE the cap); 201 is covered by
    # test_bp2_over_length_scenario_label_refused.
    _enable_flag(monkeypatch)
    label = "s" * MAX_LABEL_LEN
    resp = client_with_registry.post(
        _URL, json=_payload(case, attested=True, scenario_label=label)
    )
    assert resp.status_code == 200, resp.json()
    assert resp.json()["scenario_label"] == label


def test_body_at_exact_ceiling_passes_the_size_gate(client, monkeypatch):
    # body == MAX_BODY_BYTES is NOT 413 (413 fires only ABOVE the ceiling): the exactly-at-ceiling
    # whitespace body passes the size gate and is refused later as a 422 empty body. A `>=` size
    # gate would 413 here (mutation-flips-red).
    _enable_flag(monkeypatch)
    resp = client.post(_URL, content=b" " * MAX_BODY_BYTES, headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_body_at_exact_ceiling_valid_payload_returns_200(
    client_with_registry, monkeypatch, case
):
    # AS-5 at-cap-exact (body -> 200): a VALID payload padded with trailing JSON whitespace to
    # EXACTLY MAX_BODY_BYTES passes the size gate (==ceiling is accepted; >ceiling is the 413 of
    # test_oversized_body_is_413_before_parse) and runs end-to-end to a real 200 report. json.loads
    # ignores the trailing spaces, so the padded body is the SAME accepted request sitting at the
    # exact byte ceiling. A `>=` size gate would 413 here (mutation-flips-red).
    _enable_flag(monkeypatch)
    raw = json.dumps(_payload(case, attested=True)).encode("utf-8")
    assert len(raw) <= MAX_BODY_BYTES
    padded = raw + b" " * (MAX_BODY_BYTES - len(raw))
    assert len(padded) == MAX_BODY_BYTES  # the request body is exactly at the ceiling
    resp = client_with_registry.post(_URL, content=padded, headers=_JSON_HEADERS)
    assert resp.status_code == 200, resp.text
    cov = _by_id(resp.json()["results"])["lot_coverage_ratio"]
    assert cov["provided_value"] == pytest.approx(0.625)  # a real derivation ran at the ceiling


def test_at_wall_cap_exact_returns_200_for_a_valid_solid(
    client_with_registry, monkeypatch, case
):
    # AS-5 at-cap-exact (walls -> 200): a VALID solid carrying EXACTLY ROUTE_MAX_EXTERIOR_WALLS
    # walls runs end-to-end and returns 200 with the accepted rectangle arithmetic byte-identical.
    # The 500 walls all name the base outline's south edge (indices 0->1, distinct in-range, unique
    # ids) - each is B0-valid, the count check accepts ==cap (>cap only refuses), and the derivation
    # is driven by the outline so coverage stays 0.625. A cap of 499 would trip the count refusal at
    # 500; 501 is the typed refusal (test_bp4_over_wall_cap_refused) - the two bracket the boundary.
    _enable_flag(monkeypatch)
    block = {
        **case["block"],
        "exterior_walls": [
            {"id": f"W{i}", "start_vertex_index": 0, "end_vertex_index": 1}
            for i in range(ROUTE_MAX_EXTERIOR_WALLS)
        ],
    }
    assert len(block["exterior_walls"]) == ROUTE_MAX_EXTERIOR_WALLS == 500
    resp = client_with_registry.post(
        _URL, json=_payload(case, attested=True, proposed_massing=block)
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "ROUTE_MAX_EXTERIOR_WALLS" not in json.dumps(body)  # the count cap did NOT trip
    cov = _by_id(body["results"])["lot_coverage_ratio"]
    assert cov["provided_value"] == pytest.approx(0.625)  # a real derivation ran, not a refusal
    assert cov["shortfall"] == pytest.approx(0.125)


def test_at_street_line_cap_exact_returns_200(client_with_registry, monkeypatch, case):
    # AS-5 at-cap-exact (street lines -> 200): a VALID lot carrying EXACTLY ROUTE_MAX_STREET_LINES
    # attested street lines runs end-to-end and returns 200 with the accepted arithmetic. Each line
    # is finite EPSG:2263 geometry naming the fixture's W-S frontage wall; the count check accepts
    # ==cap (>cap only refuses) and 400 <= MAX_STREET_LINES (500) clears the engine's wiring
    # ceiling. 401 is the typed refusal (test_bp4_over_street_line_cap_refused) - the two bracket
    # the boundary.
    _enable_flag(monkeypatch)
    lot = {
        **case["lot"],
        "street_lines": [
            {"wall_id": "W-S", "start": [999990.0, 199990.0], "end": [999990.0, 200060.0],
             "attestation": {}}
            for _ in range(ROUTE_MAX_STREET_LINES)
        ],
    }
    assert len(lot["street_lines"]) == ROUTE_MAX_STREET_LINES == 400
    resp = client_with_registry.post(_URL, json=_payload(case, attested=True, lot=lot))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "ROUTE_MAX_STREET_LINES" not in json.dumps(body)  # the count cap did NOT trip
    cov = _by_id(body["results"])["lot_coverage_ratio"]
    assert cov["provided_value"] == pytest.approx(0.625)  # a real derivation ran, not a refusal


def test_lot_rule_facts_not_object_is_422(client, monkeypatch):
    _enable_flag(monkeypatch)
    resp = client.post(_URL, json=_minimal_body(lot_rule_facts=[1, 2, 3]))
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts"


def test_build_lot_context_shape_refusals_each_bound():
    # AS-5: every _build_lot_context shape-refusal branch names its exact field. Each assertion
    # flips red if that branch's guard is removed.
    def field_of(bad) -> str | None:
        with pytest.raises(mod._FieldRefusal) as excinfo:
            mod._build_lot_context(bad)
        return excinfo.value.field

    assert field_of("not-an-object") == "lot"
    assert field_of({"area_provenance": "x"}) == "lot.area_provenance"
    assert field_of({"lot_line_segments": "x"}) == "lot.lot_line_segments"
    assert field_of({"street_lines": "x"}) == "lot.street_lines"
    assert field_of({"lot_line_segments": ["not-an-object"]}) == "lot.lot_line_segments[0]"
    assert field_of({"street_lines": ["not-an-object"]}) == "lot.street_lines[0]"
    assert (
        field_of({"street_lines": [{"wall_id": "s", "attestation": "x"}]})
        == "lot.street_lines[0].attestation"
    )
