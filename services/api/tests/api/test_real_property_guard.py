"""C-04 / plan task M1-06a (server side): the real-property request guard.

Fully offline. Covers the pure guard (:mod:`app.api.v1.real_property_guard`) and its wiring into
``POST /api/v1/proposal-checks`` and ``POST /api/v1/max-envelope``:

- a real-property request (``lot.bbl`` present) carrying the web's former example site's
  fictional EPSG:2263 geometry (``rectangleSampleDraft``'s outline corners or lot line) is a typed
  422 with the machine-readable ``reason`` ``example_site_values_on_real_property`` unless it says
  ``"example": true``. The example's zoning VALUES (R5 + 8,000 sq ft + wide) are never refused:
  they are an ordinary real lot ([ORCH-CORRECTED per review 1]);
- every caller-attested value on such a request needs a site_fact measurement rank;
- the guard runs after the lot-shape refusals and, on max-envelope, before the derivation's
  outbound call ([ORCH-CORRECTED per review 2]);
- requests without a BBL, and every request while ``LANE_C_ENABLED`` is off, are unchanged.

``tests/api/test_max_envelope_api.py`` runs its whole suite with the flag off AND on; its fixtures
carry ranks for that (the one intended change to an existing test file).
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import max_envelope_api
from app.api.v1 import proposal_checks_api as pc_mod
from app.api.v1 import real_property_guard as guard
from app.api.v1.max_envelope_api import MAX_ENVELOPE_STATUS_STATE_MATRIX
from app.api.v1.max_envelope_api import router as max_envelope_router
from app.api.v1.proposal_checks_api import PROPOSAL_CHECKS_STATUS_STATE_MATRIX
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.main import app
from app.rules.registry import RuleRegistry
from app.rules.snapshots import SnapshotStore

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SITE_FACT_SCHEMA = (
    _REPO_ROOT / "packages" / "contracts" / "schemas" / "v1" / "site_fact.schema.json"
)
_WEB_DRAFT = _REPO_ROOT / "apps" / "web" / "src" / "lib" / "architect" / "proposal-draft.ts"
_B2 = Path(__file__).resolve().parents[1] / "rules" / "fixtures" / "proposal_checks"

_PC_URL = "/api/v1/proposal-checks"
_ME_URL = "/api/v1/max-envelope"
_BBL = "1008350041"
_LANE_C = "LANE_C_ENABLED"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def fixture_registry() -> RuleRegistry:
    return RuleRegistry(_B2 / "rulesets", snapshots=SnapshotStore(_B2 / "snapshots")).load()


@pytest.fixture()
def pc_client(monkeypatch, fixture_registry):
    """proposal-checks on the real app, internal flag ON, synthetic B2 registry, LANE_C unset."""
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    monkeypatch.delenv(_LANE_C, raising=False)
    monkeypatch.setattr(pc_mod, "get_proposal_check_registry", lambda: fixture_registry)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture()
def me_client(monkeypatch, fixture_registry):
    """max-envelope mounted on a fresh app (it ships unmounted), internal flag ON, LANE_C unset."""
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    monkeypatch.delenv(_LANE_C, raising=False)
    monkeypatch.setattr(max_envelope_api, "get_max_envelope_registry", lambda: fixture_registry)
    mounted = FastAPI()
    mounted.include_router(max_envelope_router)
    with TestClient(mounted, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture()
def lane_c_on(monkeypatch):
    monkeypatch.setenv(_LANE_C, "1")


@pytest.fixture()
def example_case() -> dict:
    """The accepted rectangle case = the web example site (R5, 8000 sq ft, wide, fake outline)."""
    return json.loads((_B2 / "rectangle_case.json").read_text(encoding="utf-8"))


def _ranked(rank: str = "city_records", **extra) -> dict:
    return {"rank": rank, **extra}


def _example_pc_body(case: dict, *, bbl: str | None = _BBL, ranked: bool = True) -> dict:
    lot = copy.deepcopy(case["lot"])
    facts = dict(case["lot_rule_facts_attested"])  # R5 + wide
    if bbl is not None:
        lot["bbl"] = bbl
    body = {
        "proposed_massing": copy.deepcopy(case["block"]),
        "lot": lot,
        "lot_rule_facts": facts,
        "scenario_label": case["scenario_label"],
        "proposal_id": case["proposal_id"],
    }
    if ranked:
        lot["area_provenance"] = _ranked(source_id="synthetic-fixture")
        body["lot_rule_facts_provenance"] = {k: _ranked() for k in facts}
    return body


def _real_pc_body(case: dict) -> dict:
    """A real-property request whose values do NOT match the example: shifted outline, no lot
    line at the example position, a 9,000 sq ft lot and no street class."""
    body = _example_pc_body(case)
    dx = 12.5
    body["proposed_massing"]["outline"]["vertices"] = [
        [x + dx, y] for x, y in body["proposed_massing"]["outline"]["vertices"]
    ]
    body["lot"]["lot_line_segments"] = [
        {"id": "LL-W", "start": [999990.0 + dx, 199990.0], "end": [999990.0 + dx, 200060.0]}
    ]
    body["lot"]["area_sq_ft"] = 9000.0
    body["lot_rule_facts"] = {"zoning_district": "R5"}
    body["lot_rule_facts_provenance"] = {"zoning_district": _ranked()}
    return body


def _pair(resp) -> tuple[int, str | None]:
    return resp.status_code, resp.json().get("state")


def _assert_refused(resp, *, reason: str, field: str) -> dict:
    assert resp.status_code == 422, resp.json()
    doc = resp.json()
    assert doc["state"] == "validation_error"
    assert doc["reason"] == reason
    assert doc["field"] == field
    assert doc["correlation_id"] == resp.headers["X-Correlation-ID"]
    assert reason in guard.REAL_PROPERTY_GUARD_REASONS
    return doc


# ---------------------------------------------------------------------------
# The pure guard
# ---------------------------------------------------------------------------
def test_measurement_ranks_match_the_site_fact_contract():
    schema = json.loads(_SITE_FACT_SCHEMA.read_text(encoding="utf-8"))
    ranks = [
        d["properties"]["rank"]["const"]
        for name, d in schema["$defs"].items()
        if name.startswith("measurement_") and "rank" in d.get("properties", {})
    ]
    assert tuple(ranks) == guard.MEASUREMENT_RANKS
    assert guard.KNOWN_VALUE_RANKS == tuple(r for r in ranks if r != "unknown")


def test_example_signature_matches_the_web_example_draft():
    """The signature is the web's rectangleSampleDraft geometry, copied verbatim; if that example
    ever changes, this fails so the server guard is updated with it."""
    source = _WEB_DRAFT.read_text(encoding="utf-8")
    start = source.index("export function rectangleSampleDraft")
    body = source[start : source.index("\n}\n", start)]
    vertices = {
        (float(x), float(y))
        for x, y in re.findall(r"\{ x: (\d+(?:\.\d+)?), y: (\d+(?:\.\d+)?) \}", body)
    }
    assert vertices == guard.EXAMPLE_OUTLINE_CORNERS
    seg = re.search(
        r"start_x: (\d+), start_y: (\d+), end_x: (\d+), end_y: (\d+)", body
    ).groups()
    assert {(float(seg[0]), float(seg[1])), (float(seg[2]), float(seg[3]))} == (
        guard.EXAMPLE_LOT_LINE_ENDPOINTS
    )


@pytest.mark.parametrize(
    ("lot", "expected"),
    [
        ({}, False),
        ({"bbl": None}, False),
        ({"bbl": ""}, False),
        ({"bbl": "   "}, False),
        ({"bbl": False}, False),
        ({"bbl": {"x": 1}}, False),
        ({"bbl": ["1008350041"]}, False),
        ({"bbl": _BBL}, True),
        ({"bbl": 1008350041}, True),
        ({"bbl": 0}, True),
        ({"bbl": "not-a-bbl"}, True),  # a malformed BBL string is still a real-property claim
    ],
)
def test_lot_bbl_present_is_the_one_definition(lot, expected):
    """One definition of "carries a BBL", shared by the guard and max-envelope's derivation
    trigger ([ORCH-CORRECTED per review F4])."""
    assert guard.lot_bbl_present(lot) is expected
    assert max_envelope_api._should_derive_lot_geometry({**lot, "lot_line_segments": []}) is (
        expected
    )


def test_guard_is_off_unless_lane_c_flag_is_an_explicit_true_token():
    assert guard.real_property_guard_enabled(env={}) is False
    assert guard.real_property_guard_enabled(env={_LANE_C: "maybe"}) is False
    assert guard.real_property_guard_enabled(env={_LANE_C: "true"}) is True


def test_guard_ignores_a_request_without_a_bbl(example_case):
    body = _example_pc_body(example_case, bbl=None, ranked=False)
    guard.guard_real_property_request(
        body,
        lot=body["lot"],
        lot_rule_facts=body["lot_rule_facts"],
        proposed_massing=body["proposed_massing"],
    )  # no raise


@pytest.mark.parametrize("rank", ["city_records", "survey_entered", "entered"])
def test_example_zoning_values_alone_never_refuse_a_real_lot(rank):
    """[ORCH-CORRECTED per review 1]: R5 + 8,000 sq ft + wide is an ordinary real lot (80 x 100 ft
    on a wide street); with its own geometry and ranked values it passes."""
    facts = {"zoning_district": "R5", "street_width_class": "wide"}
    lot = {
        "bbl": _BBL,
        "area_sq_ft": 8000.0,
        "area_provenance": _ranked(rank),
        "lot_line_segments": [
            {"id": "L-S", "start": [985000.0, 195000.0], "end": [985080.0, 195000.0]}
        ],
        "street_lines": [],
    }
    guard.guard_real_property_request(
        {"lot_rule_facts_provenance": {k: _ranked(rank) for k in facts}},
        lot=lot,
        lot_rule_facts=facts,
    )  # no raise


# ---------------------------------------------------------------------------
# POST /api/v1/proposal-checks
# ---------------------------------------------------------------------------
def test_pc_flag_off_real_property_example_request_is_unchanged(pc_client, example_case):
    resp = pc_client.post(_PC_URL, json=_example_pc_body(example_case, ranked=False))
    assert resp.status_code == 200, resp.json()
    assert "reason" not in resp.json()


def test_pc_flag_on_request_without_bbl_is_unchanged(pc_client, lane_c_on, example_case):
    resp = pc_client.post(_PC_URL, json=_example_pc_body(example_case, bbl=None, ranked=False))
    assert resp.status_code == 200, resp.json()
    assert resp.json()["summary"] == {"pass": 1, "fail": 1, "could_not_check": 2, "total": 4}


def test_pc_example_draft_on_real_property_is_refused(pc_client, lane_c_on, example_case):
    resp = pc_client.post(_PC_URL, json=_example_pc_body(example_case))
    doc = _assert_refused(
        resp, reason=guard.REASON_EXAMPLE_VALUES, field="proposed_massing.outline.vertices"
    )
    assert _pair(resp) in PROPOSAL_CHECKS_STATUS_STATE_MATRIX
    assert "fictional coordinates" in doc["message"]
    assert "example\": true" not in doc["message"]  # never tells a real lot to mark itself


def test_pc_example_level_outline_is_refused(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["proposed_massing"]["levels"][0]["outline"] = {
        "srid": 2263,
        "vertices": [list(v) for v in example_case["block"]["outline"]["vertices"]],
    }
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp,
        reason=guard.REASON_EXAMPLE_VALUES,
        field="proposed_massing.levels[0].outline.vertices",
    )


def test_level_outline_signature_unit():
    massing = {
        "outline": {"vertices": [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 0.0]]},
        "levels": [
            {"outline": {"vertices": [[1000000, 200000], [1000100, 200000], [1000100, 200050],
                                      [1000000, 200050], [1000000, 200000]]}}
        ],
    }
    with pytest.raises(guard.RealPropertyRefusal) as exc:
        guard.guard_real_property_request(
            {}, lot={"bbl": _BBL}, lot_rule_facts={}, proposed_massing=massing
        )
    assert exc.value.field == "proposed_massing.levels[0].outline.vertices"
    assert exc.value.reason == guard.REASON_EXAMPLE_VALUES


def test_pc_example_zoning_values_with_own_geometry_pass(pc_client, lane_c_on, example_case):
    """[ORCH-CORRECTED per review 1] regression: a real BBL, R5, 8,000 sq ft, wide, every value
    ranked, with the lot's own geometry -> 200."""
    body = _real_pc_body(example_case)
    body["lot"]["area_sq_ft"] = 8000.0
    body["lot_rule_facts"] = {"zoning_district": "R5", "street_width_class": "wide"}
    body["lot_rule_facts_provenance"] = {k: _ranked() for k in body["lot_rule_facts"]}
    resp = pc_client.post(_PC_URL, json=body)
    assert resp.status_code == 200, resp.json()
    assert resp.json()["summary"] == {"pass": 1, "fail": 1, "could_not_check": 2, "total": 4}


def test_pc_example_outline_alone_is_refused(pc_client, lane_c_on, example_case):
    body = _example_pc_body(example_case)
    body["lot"]["area_sq_ft"] = 9000.0  # break the fact triple; keep the fake outline
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp, reason=guard.REASON_EXAMPLE_VALUES, field="proposed_massing.outline.vertices"
    )


def test_pc_example_lot_line_alone_is_refused(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot"]["lot_line_segments"] = [
        {"id": "LL-X", "start": [999990.0, 200060.0], "end": [999990.0, 199990.0]}  # reversed
    ]
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp, reason=guard.REASON_EXAMPLE_VALUES, field="lot.lot_line_segments[0]"
    )


def test_pc_explicit_example_marker_allows_the_example(pc_client, lane_c_on, example_case):
    body = _example_pc_body(example_case)
    body["example"] = True
    resp = pc_client.post(_PC_URL, json=body)
    assert resp.status_code == 200, resp.json()


def test_pc_non_boolean_example_marker_is_refused(pc_client, lane_c_on, example_case):
    body = _example_pc_body(example_case)
    body["example"] = "yes"
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(resp, reason=guard.REASON_EXAMPLE_MARKER_NOT_BOOLEAN, field="example")


def test_pc_real_values_with_ranks_pass(pc_client, lane_c_on, example_case):
    resp = pc_client.post(_PC_URL, json=_real_pc_body(example_case))
    assert resp.status_code == 200, resp.json()
    doc = resp.json()
    assert doc["summary"]["total"] == 4
    coverage = next(r for r in doc["results"] if r["check_id"] == "lot_coverage_ratio")
    assert coverage["outcome"] == "fail"  # 5000 / 9000 > 0.5: the real values were checked


def test_pc_missing_area_rank_is_refused(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot"]["area_provenance"] = {"source_id": "synthetic-fixture"}
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(resp, reason=guard.REASON_RANK_MISSING, field="lot.area_provenance.rank")


def test_pc_absent_area_provenance_is_a_missing_rank(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    del body["lot"]["area_provenance"]
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(resp, reason=guard.REASON_RANK_MISSING, field="lot.area_provenance.rank")


def test_pc_rank_outside_vocabulary_is_refused_without_echo(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot"]["area_provenance"] = _ranked("measured-by-eye-XYZZY")
    resp = pc_client.post(_PC_URL, json=body)
    doc = _assert_refused(
        resp, reason=guard.REASON_RANK_NOT_IN_VOCABULARY, field="lot.area_provenance.rank"
    )
    assert "XYZZY" not in json.dumps(doc)
    assert "city_records" in doc["message"]  # names the closed vocabulary


def test_pc_unknown_rank_beside_a_value_is_refused(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot"]["area_provenance"] = _ranked("unknown")
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp, reason=guard.REASON_RANK_UNKNOWN_WITH_VALUE, field="lot.area_provenance.rank"
    )


def test_pc_every_lot_rule_fact_needs_a_rank(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot_rule_facts"]["overlay_present"] = False
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp,
        reason=guard.REASON_RANK_MISSING,
        field="lot_rule_facts_provenance.overlay_present.rank",
    )


def test_pc_missing_fact_provenance_object_is_a_missing_rank(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    del body["lot_rule_facts_provenance"]
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp,
        reason=guard.REASON_RANK_MISSING,
        field="lot_rule_facts_provenance.zoning_district.rank",
    )


def test_pc_non_object_fact_provenance_entry_is_refused(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot_rule_facts_provenance"] = {"zoning_district": "city_records"}
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp,
        reason=guard.REASON_PROVENANCE_NOT_AN_OBJECT,
        field="lot_rule_facts_provenance.zoning_district",
    )


def test_pc_non_object_fact_provenance_is_refused(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot_rule_facts_provenance"] = ["city_records"]
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp, reason=guard.REASON_PROVENANCE_NOT_AN_OBJECT, field="lot_rule_facts_provenance"
    )


def test_pc_street_line_attestation_needs_a_rank(pc_client, lane_c_on, example_case):
    body = _real_pc_body(example_case)
    body["lot"]["street_lines"] = [
        {
            "wall_id": "W-S",
            "start": [1000000.0, 199980.0],
            "end": [1000200.0, 199980.0],
            "attestation": {"source_id": "dcm"},
        }
    ]
    resp = pc_client.post(_PC_URL, json=body)
    _assert_refused(
        resp, reason=guard.REASON_RANK_MISSING, field="lot.street_lines[0].attestation.rank"
    )


# ---------------------------------------------------------------------------
# POST /api/v1/max-envelope (unmounted; mounted on a fresh app here)
# ---------------------------------------------------------------------------
def _me_body(*, area: float, facts: dict, ranked: bool = True, **lot_extra) -> dict:
    lot = {
        "area_sq_ft": area,
        "area_provenance": _ranked() if ranked else {"source_id": "synthetic"},
        "lot_line_segments": [
            {"id": "L-S", "start": [985000.0, 195000.0], "end": [985080.0, 195000.0]},
            {"id": "L-E", "start": [985080.0, 195000.0], "end": [985080.0, 195100.0]},
            {"id": "L-N", "start": [985080.0, 195100.0], "end": [985000.0, 195100.0]},
            {"id": "L-W", "start": [985000.0, 195100.0], "end": [985000.0, 195000.0]},
        ],
        "street_lines": [],
        **lot_extra,
    }
    body = {"lot": lot, "lot_rule_facts": facts, "label": "env-A"}
    if ranked:
        body["lot_rule_facts_provenance"] = {k: _ranked() for k in facts}
    return body


_EXAMPLE_FACTS = {"zoning_district": "R5", "street_width_class": "wide"}


def test_me_flag_off_example_on_real_property_is_unchanged(me_client):
    resp = me_client.post(_ME_URL, json=_me_body(area=8000.0, facts=_EXAMPLE_FACTS,
                                                 ranked=False, bbl=_BBL))
    assert resp.status_code == 200, resp.json()


def test_me_example_zoning_values_on_a_real_lot_pass(me_client, lane_c_on):
    """[ORCH-CORRECTED per review 1] regression: the accepted max-envelope fixture lot (real
    EPSG:2263 coordinates, R5, 8,000 sq ft, wide) with a real BBL and ranked values -> 200."""
    resp = me_client.post(_ME_URL, json=_me_body(area=8000.0, facts=_EXAMPLE_FACTS, bbl=_BBL))
    assert resp.status_code == 200, resp.json()
    assert resp.json()["candidate_placement"]["status"] == "fitted"


def test_me_example_lot_line_on_real_property_is_refused(me_client, lane_c_on):
    body = _me_body(area=7200.0, facts={"zoning_district": "R5"}, bbl=_BBL)
    body["lot"]["lot_line_segments"].append(
        {"id": "LL-W", "start": [999990.0, 199990.0], "end": [999990.0, 200060.0]}
    )
    resp = me_client.post(_ME_URL, json=body)
    _assert_refused(resp, reason=guard.REASON_EXAMPLE_VALUES, field="lot.lot_line_segments[4]")
    assert _pair(resp) in MAX_ENVELOPE_STATUS_STATE_MATRIX


def _recording_provider(calls: list):
    def _provider(canonical_bbl):  # pragma: no cover - asserted never invoked
        calls.append(canonical_bbl)
        raise AssertionError("the derivation provider must not be reached")

    return _provider


def test_me_refused_real_property_request_never_reaches_the_derivation(
    me_client, lane_c_on, monkeypatch
):
    """[ORCH-CORRECTED per review 2]: the guard runs BEFORE the DB-050(a) derivation's outbound
    call - an unranked geometry-free real-property request is refused with no provider call."""
    calls: list = []
    monkeypatch.setattr(max_envelope_api, "get_lot_geometry_provider",
                        lambda: _recording_provider(calls))
    body = _me_body(area=8000.0, facts={"zoning_district": "R5"}, ranked=False, bbl=_BBL)
    body["lot"]["lot_line_segments"] = []
    resp = me_client.post(_ME_URL, json=body)
    _assert_refused(resp, reason=guard.REASON_RANK_MISSING, field="lot.area_provenance.rank")
    assert calls == []


@pytest.mark.parametrize("malformed", ["abc", 0, None, {"id": "L-S"}])
def test_me_malformed_lot_refuses_identically_with_and_without_bbl_when_unranked(
    me_client, lane_c_on, monkeypatch, malformed
):
    """[ORCH-CORRECTED per review 2] / DB-051(b): lot-shape refusals come before the guard, so an
    UNRANKED malformed request gets the same shape refusal with or without a BBL, and the
    derivation provider is never reached."""
    calls: list = []
    monkeypatch.setattr(max_envelope_api, "get_lot_geometry_provider",
                        lambda: _recording_provider(calls))
    without = _me_body(area=8000.0, facts=_EXAMPLE_FACTS, ranked=False)
    without["lot"]["lot_line_segments"] = malformed
    with_bbl = copy.deepcopy(without)
    with_bbl["lot"]["bbl"] = _BBL
    a = me_client.post(_ME_URL, json=without).json()
    b = me_client.post(_ME_URL, json=with_bbl).json()
    assert a["field"] == b["field"] == "lot.lot_line_segments"
    assert "reason" not in b
    a.pop("correlation_id")
    b.pop("correlation_id")
    assert a == b
    assert calls == []


def test_me_example_values_without_bbl_are_unchanged(me_client, lane_c_on):
    resp = me_client.post(_ME_URL, json=_me_body(area=8000.0, facts=_EXAMPLE_FACTS, ranked=False))
    assert resp.status_code == 200, resp.json()


def test_me_real_values_with_ranks_pass(me_client, lane_c_on):
    facts = {"zoning_district": "R5", "street_width_class": "narrow"}
    resp = me_client.post(_ME_URL, json=_me_body(area=8000.0, facts=facts, bbl=_BBL))
    assert resp.status_code == 200, resp.json()
    assert "derived_lot_geometry" not in resp.json()  # segments supplied -> no derivation


def test_me_real_property_value_without_rank_is_refused(me_client, lane_c_on):
    body = _me_body(area=7200.0, facts={"zoning_district": "R5"}, bbl=_BBL)
    body["lot_rule_facts_provenance"] = {"zoning_district": {"source_id": "pluto"}}
    resp = me_client.post(_ME_URL, json=body)
    _assert_refused(
        resp,
        reason=guard.REASON_RANK_MISSING,
        field="lot_rule_facts_provenance.zoning_district.rank",
    )
