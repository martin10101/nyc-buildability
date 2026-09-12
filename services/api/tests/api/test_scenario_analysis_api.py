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
* AS-7 additive registration (registered LAST, in the documented order) + offline at the
  EGRESS SEAM for ALL FOUR endpoints + facade-only engine calls.
* AS-8 exercised by the full api + scenario suites staying green (run separately).

Gate-wave rework (G1/G3/G5). Every assertion below is mutation-resistant by construction:

* request -> result CARDINALITY is asserted per endpoint, so dropping an engine argument
  changes a count and FAILS (G3 C1);
* every documented cap is asserted at its LITERAL value, and exercised at exactly N (accepted)
  and N + 1 (rejected), so loosening a cap or an off-by-one ``>`` -> ``>=`` FAILS (G3 C5/C6);
* the byte cap is driven by MANY SHORT strings so no other cap can fire in its place (G3 C4);
* every typed rejection asserts ``state``, not only the status code (G3 C2);
* the never-Verified scan walks EVERY envelope key and string value at every depth (G3 C3);
* route registration order is pinned (G3 C7) and threshold's default response metric is
  pinned (G3 C9);
* FACT-key rejection is asserted at NESTED depth on all four endpoints (G1 BLOCKING-2);
* unpaired surrogates are asserted typed-422 in all eight positions x four endpoints, and
  legitimate non-ASCII text is asserted STILL accepted (G5 BLOCKING-1);
* a forced engine raise and a forced ``_finish`` defect are asserted typed
  ``(500, "internal_error")`` with a correlation id (G1/G5 BLOCKING-3).
"""

from __future__ import annotations

import http.client
import json
import os
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
    FORBIDDEN_FACT_KEYS,
    MAX_ASSUMPTION_SETS,
    MAX_ASSUMPTIONS_PER_SET,
    MAX_BODY_BYTES,
    MAX_CANDIDATE_DOMAIN_LENGTH,
    MAX_NESTING_DEPTH,
    MAX_STRING_LENGTH,
    STATUS_STATE_MATRIX,
)
from app.config import (
    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
    INTERNAL_SCENARIO_ENABLED_ENV_VAR,
)
from app.connectors import pluto_soda
from app.connectors.pluto_soda import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.resilience import transport as resilience_transport
from app.scenario import NOT_VERIFIED_DISCLAIMER, ThresholdResponseMetric
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
ANALYSES = [analysis for analysis, _, _, _ in ENDPOINTS]
RESULT_KINDS = {analysis: (field, kind) for analysis, _, field, kind in ENDPOINTS}

# G3 C1: the result field whose value MUST equal the length of the named request field. This
# is what makes dropping an engine argument visible - `values -> None` silently turned
# point_count 3 into 1 while every other assertion stayed green.
CARDINALITY = {
    "sensitivity": ("point_count", "values"),
    "ranking": ("candidate_count", "assumption_sets"),
    "comparison": ("set_count", "assumption_sets"),
    "threshold": ("candidate_count", "domain"),
}


def _named_sets(count: int) -> list[dict]:
    """`count` DISTINCT named assumption-sets (the form both ranking and comparison accept)."""
    return [
        {"name": f"set{index}", "assumptions": [_assumption("utilization_factor", 0.9)]}
        for index in range(count)
    ]


def body_with_cardinality(analysis: str, count: int) -> dict:
    """A valid body for `analysis` whose cardinality-bearing field holds exactly `count`
    entries, so the engine's echoed count can be checked against the request."""
    if analysis == "sensitivity":
        return {
            "variable": "utilization_factor",
            "values": [0.5 + 0.01 * index for index in range(count)],
        }
    if analysis == "ranking":
        return {
            "objective": "maximize_illustrative_usable_area",
            "assumption_sets": _named_sets(count),
        }
    if analysis == "comparison":
        return {"assumption_sets": _named_sets(count)}
    return {
        "variable": "utilization_factor",
        "target": 10000,
        "domain": [0.5 + 0.01 * index for index in range(count)],
    }


def nested_levels_body(levels: int) -> bytes:
    """Raw body whose TOTAL container nesting is exactly `levels` - the body object itself is
    level 1 - so `levels == MAX_NESTING_DEPTH` must be ACCEPTED and `+ 1` rejected."""
    inner = levels - 1
    return (
        '{"variable": "utilization_factor", "note": ' + "[" * inner + "]" * inner + "}"
    ).encode()


def body_of_exact_size(size: int) -> bytes:
    """A valid body of EXACTLY `size` raw bytes, built from MANY SHORT strings (each far under
    MAX_STRING_LENGTH, in an uncapped field) so the BYTE cap is the only cap that can fire -
    G3 C4: the old oversized-body test used one huge string and therefore still passed with the
    byte cap deleted, because MAX_STRING_LENGTH tripped instead."""
    prefix = b'{"variable": "utilization_factor", "note": ['
    suffix = b"]}"
    unit = b'"' + b"q" * 98 + b'",'  # 101 bytes including the separating comma
    out = bytearray(prefix)
    while len(out) + len(unit) + 3 + len(suffix) <= size:
        out += unit
    out += b'"' + b"q" * (size - len(out) - 2 - len(suffix)) + b'"' + suffix
    assert len(out) == size, f"helper built {len(out)} bytes, wanted {size}"
    return bytes(out)


# G5 BLOCKING-1: an unpaired surrogate arrives as a pure-ASCII JSON ESCAPE - 21 request bytes
# for the shortest body, under every documented cap - yet is not encodable text. One entry per
# position the gate found, exercised against all four endpoints.
SURROGATE = "\\ud800"
SURROGATE_BODIES = [
    ("variable", '{"variable": "' + SURROGATE + '"}'),
    ("objective", '{"objective": "' + SURROGATE + '", "assumption_sets": []}'),
    ("set_name", '{"assumption_sets": [{"name": "' + SURROGATE + '", "assumptions": []}]}'),
    (
        "assumption_key",
        '{"assumption_sets": [{"name": "a", "assumptions": [{"key": "' + SURROGATE + '"}]}]}',
    ),
    (
        "assumption_unit",
        '{"assumption_sets": [{"name": "a", "assumptions": [{"unit": "' + SURROGATE + '"}]}]}',
    ),
    (
        "assumption_rationale",
        '{"assumption_sets": [{"name": "a", "assumptions": [{"rationale": "'
        + SURROGATE
        + '"}]}]}',
    ),
    ("candidate_value", '{"variable": "utilization_factor", "values": ["' + SURROGATE + '"]}'),
    ("dict_key", '{"' + SURROGATE + '": 1}'),
]

# G1 BLOCKING-2: fact-shaped keys buried BELOW the top level. The engines echo a caller's
# assumption dict verbatim into their result, so before the fix these were accepted and
# reflected into a 200 body.
NESTED_FACT_KEYS = [
    "draft_zoning_floor_area_cap_sq_ft",
    "max_residential_floor_area_sq_ft",
    "coverage_status",
    "verified",
    "verification_status",
    "rule_evaluation",
]

# The module attribute each route calls, for forcing an engine defect (G1/G5 BLOCKING-3).
ENGINE_ATTR = {
    "sensitivity": "analyze_scenario_sensitivity",
    "ranking": "rank_scenario_assumption_sets",
    "comparison": "compare_scenario_assumption_sets",
    "threshold": "find_scenario_threshold",
}


def nested_fact_body(analysis: str, fact_key: str) -> dict:
    """The endpoint's VALID body with `fact_key` buried below the top level - inside an
    assumption dict where the engines echo it, or inside a nested container otherwise."""
    body = json.loads(json.dumps(BODIES[analysis]))
    if analysis == "ranking":
        body["assumption_sets"][0][0][fact_key] = 987654321
    elif analysis == "comparison":
        body["assumption_sets"][0]["assumptions"].append(
            {"key": "utilization_factor", "value": 0.9, fact_key: 987654321}
        )
    else:
        body["illustrative_notes"] = [{"detail": {fact_key: 987654321}}]
    return body

# The typed EMPTY kind each engine emits when the scenario surfaces no positive cap.
EMPTY_KINDS = {
    "sensitivity": ("sensitivity_kind", "empty_no_analyzable_cap"),
    "ranking": ("ranking_kind", "empty_no_rankable_cap"),
    "comparison": ("comparison_kind", "empty_no_comparable_cap"),
    "threshold": ("threshold_kind", "empty_no_analyzable_cap"),
}


# G3 C3: keys that can ASSERT a verification status anywhere in the envelope, at any depth.
# Scanning only `coverage_status` (the previous helper) let `"verified": true` inserted anywhere
# survive. These keys are not themselves forbidden: the accepted M5-T011 threshold engine
# deliberately emits `verified: False` on its illustrative bracket midpoint
# (app.scenario.breakeven._bracket_midpoint) as an HONESTY marker. What must never occur is such
# a key CLAIMING verification, so the scan requires every one of them to deny it.
VERIFICATION_CLAIM_KEYS = frozenset(
    {"verified", "is_verified", "verification", "verification_status"}
)


def _walk_envelope(node, path="$", key=None):
    """Yield ``(path, key, value)`` for EVERY node in the envelope exactly once. A dict value
    carries its key; list items and the root carry ``None``. This is what makes the AS-6 scan
    whole-envelope rather than coverage-only."""
    yield path, key, node
    if isinstance(node, dict):
        for child_key, child in node.items():
            yield from _walk_envelope(child, f"{path}.{child_key}", child_key)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _walk_envelope(item, f"{path}[{index}]", None)


def assert_nothing_is_verified(envelope) -> None:
    """AS-6: NOTHING anywhere in the envelope may CLAIM verification - not as a status value,
    not as a bare string in a list, not through a verification-claim key - and the canonical
    disclaimer must be present. Asserted over every node at every depth (G3 C3), so
    ``"verified": true`` or ``"verification_status": "verified"`` inserted ANYWHERE fails:

    * no string value anywhere may be the status ``"verified"``;
    * every :data:`VERIFICATION_CLAIM_KEYS` entry must DENY verification (``False``/``None``) -
      which passes the engine's deliberate ``verified: False`` marker and rejects ``True``,
      a truthy number, or the string ``"verified"``.
    """
    for path, key, value in _walk_envelope(envelope):
        if isinstance(value, str):
            assert value.strip().lower() != "verified", f"a 'verified' status value at {path}"
        if key in VERIFICATION_CLAIM_KEYS:
            assert value in (False, None), (
                f"a verification-claim key may only DENY verification; got {value!r} at {path}"
            )
    assert envelope["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert envelope["coverage_status"] != "verified"


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
    # G3 C1: the engine's result cardinality must track the REQUEST, so dropping an engine
    # argument (e.g. `values -> None`) changes a count here and fails instead of passing.
    count_field, request_key = CARDINALITY[analysis]
    assert result[count_field] == len(body[request_key])

    # Never Verified anywhere in the envelope; the canonical disclaimer is present.
    assert_nothing_is_verified(envelope)


def test_as1_cap_equals_rule_evaluation_trace_value_verbatim(client, monkeypatch):
    # Prove the envelope cap is the trace value read back through the mirrored
    # rule-evaluation route over the identical inputs (never a local recomputation).
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")

    install_confident()
    envelope = client.post(url("sensitivity"), json=SENSITIVITY_BODY).json()

    install_confident()
    rule_eval = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()
    trace_cap = _applicable_trace(rule_eval)["outputs"]["max_residential_floor_area_sq_ft"]
    assert envelope["scenario_cap_sq_ft"] == trace_cap == TRACE_CAP


@pytest.mark.parametrize("count", [2, 3, 7])
@pytest.mark.parametrize("analysis", ANALYSES)
def test_as1_result_cardinality_tracks_the_request(client, monkeypatch, analysis, count):
    """G3 C1 (HIGH): the engine result's cardinality must EQUAL the request's. Mutating the
    route to drop an engine argument (`values -> None`, `assumption_sets -> None`) visibly
    changed the body - point_count 3 -> 1, candidate_count 2 -> 1 - yet all 75 tests stayed
    green because nothing asserted the relationship. Three different counts per endpoint means
    a hardcoded or defaulted count cannot satisfy it either."""
    enable_flag(monkeypatch)
    install_confident()

    body = body_with_cardinality(analysis, count)
    count_field, request_key = CARDINALITY[analysis]

    response = client.post(url(analysis), json=body)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result[count_field] == len(body[request_key]) == count


def test_as1_threshold_default_response_metric_is_the_documented_default(client, monkeypatch):
    """G3 C9: omitting ``response_metric`` must resolve to the documented engine default
    (the usable-range POINT). Untested before, so changing the route's default was invisible.
    The explicit non-default case is asserted too, so the default cannot be hardcoded
    downstream."""
    enable_flag(monkeypatch)
    domain_body = {"variable": "utilization_factor", "target": 10000, "domain": [0.5, 0.7, 1.0]}

    install_confident()
    defaulted = client.post(url("threshold"), json=domain_body)
    assert defaulted.status_code == 200
    result = defaulted.json()["result"]
    assert result["response_metric"] == "usable_range_point"
    assert result["response_metric"] == ThresholdResponseMetric.USABLE_RANGE_POINT.value

    install_confident()
    explicit = client.post(
        url("threshold"), json={**domain_body, "response_metric": "usable_range_max"}
    )
    assert explicit.status_code == 200
    assert explicit.json()["result"]["response_metric"] == "usable_range_max"


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


@pytest.mark.parametrize("fact_key", NESTED_FACT_KEYS)
@pytest.mark.parametrize("analysis", ANALYSES)
def test_as2_nested_fact_key_at_any_depth_is_typed_422(client, monkeypatch, analysis, fact_key):
    """G1 BLOCKING-2: the fact-key boundary checked only ``body.keys()``, so one level down -
    inside an assumption-set - a fact-shaped object was ACCEPTED and echoed verbatim into a 200
    body. Every one of these returned 200 before the fix; each must now be the same typed 422,
    naming the key, on ALL FOUR endpoints, rejected before any fetch/rebuild."""
    enable_flag(monkeypatch)
    install_landmine_seams()

    response = client.post(url(analysis), json=nested_fact_body(analysis, fact_key))
    assert response.status_code == 422
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert fact_key in payload["detail"]["rejected_keys"]
    assert response.headers["x-correlation-id"]
    assert (422, "validation_error") in STATUS_STATE_MATRIX


def test_as2_every_forbidden_fact_key_is_rejected_nested_too(client, monkeypatch):
    """The whole :data:`FORBIDDEN_FACT_KEYS` set - not just a sample - is enforced below the
    top level, so adding a key to the set without extending the walk cannot pass."""
    enable_flag(monkeypatch)
    for fact_key in sorted(FORBIDDEN_FACT_KEYS):
        install_landmine_seams()
        body = {
            "variable": "utilization_factor",
            "values": [0.8],
            "illustrative_notes": [{"detail": {fact_key: 1}}],
        }
        response = client.post(url("sensitivity"), json=body)
        assert response.status_code == 422, f"nested {fact_key!r} was not rejected"
        assert response.json()["detail"]["rejected_keys"] == [fact_key]


def test_as2_nested_verified_claim_never_reaches_a_200_body(client, monkeypatch):
    """G1's exact finding, as an executable regression: a fact-shaped assumption carrying
    ``coverage_status: "verified"``, ``verified: true`` and a forged cap was accepted and
    reflected into ``$.result.candidates[0].assumption_set[0]`` of a 200 response - which
    falsifies AS-2 (no fact override attempt accepted) and AS-6 (nothing marked Verified) even
    though the AUTHORITATIVE cap was never forgeable. It must now be a typed 422, and the
    forged cap value must appear nowhere in the response."""
    enable_flag(monkeypatch)
    install_confident()

    body = json.loads(json.dumps(RANKING_BODY))
    body["assumption_sets"][0][0].update(
        {
            "coverage_status": "verified",
            "verified": True,
            "draft_zoning_floor_area_cap_sq_ft": 987654321,
        }
    )
    response = client.post(url("ranking"), json=body)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"
    assert "987654321" not in response.text

    # And the legitimate request over the same seams is still a clean, never-Verified 200.
    install_confident()
    envelope = client.post(url("ranking"), json=RANKING_BODY).json()
    assert_nothing_is_verified(envelope)
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


@pytest.mark.parametrize("analysis", ANALYSES)
def test_as4_engine_raise_is_typed_internal_error_500(raw_client, monkeypatch, analysis):
    """G1 HIGH-1 / G5 HIGH-1 (BLOCKING-3): the engine call sat OUTSIDE any try/except while the
    trusted rebuild stage was guarded - the asymmetry backwards, since the engine is the stage
    that processes untrusted input. A forced engine raise produced Starlette's plain-text
    ``Internal Server Error``: no ``state``, no ``X-Correlation-ID``, a (500, None) pair absent
    from :data:`STATUS_STATE_MATRIX`, and a full traceback logged. It must now be the
    documented typed pair, on every endpoint, leaking nothing."""
    enable_flag(monkeypatch)
    install_confident()

    def exploding_engine(*args, **kwargs):
        raise RuntimeError("secret-internal-path C:\\hostile\r\n::engine boom")

    monkeypatch.setattr(analysis_module, ENGINE_ATTR[analysis], exploding_engine)
    response = raw_client.post(url(analysis), json=BODIES[analysis])

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["state"] == "internal_error"
    assert (500, "internal_error") in STATUS_STATE_MATRIX
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text


def test_as4_finish_stage_defect_is_typed_internal_error_500(raw_client, monkeypatch):
    """BLOCKING-3, second half: ``_finish`` (envelope build + pre-send serialization check) was
    outside the guard too. A defect there must also honor the documented pair - proving the
    guard wraps the envelope build, not merely the engine call."""
    enable_flag(monkeypatch)
    install_confident()

    def exploding_finish(*args, **kwargs):
        raise RuntimeError("finish-stage boom")

    monkeypatch.setattr(analysis_module, "_finish", exploding_finish)
    response = raw_client.post(url("sensitivity"), json=SENSITIVITY_BODY)

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["state"] == "internal_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "boom" not in response.text


# ==========================================================================
# AS-5 - bounded input, fail-closed at the untrusted edge.
# ==========================================================================


def _post_raw(client, analysis, content):
    return client.post(
        url(analysis), content=content, headers={"content-type": "application/json"}
    )


def test_as5_oversized_body_is_typed_422(client, monkeypatch):
    # G3 C4: built from MANY SHORT strings in an uncapped field, so MAX_STRING_LENGTH and the
    # list caps CANNOT fire in the byte cap's place - deleting MAX_BODY_BYTES makes this body
    # reach the (landmined) rebuild stage and the test fail, which is the point.
    enable_flag(monkeypatch)
    install_landmine_seams()
    content = json.dumps(
        {"variable": "utilization_factor", "note": ["q" * 100] * 1200}
    ).encode()
    assert len(content) > MAX_BODY_BYTES
    response = _post_raw(client, "sensitivity", content)
    assert response.status_code == 422
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert "bytes" in payload["message"]  # the BYTE cap, not a string/list cap


def test_as5_body_byte_cap_is_exact_at_the_boundary(client, monkeypatch):
    # G3 C6: exactly MAX_BODY_BYTES is ACCEPTED and MAX_BODY_BYTES + 1 is REJECTED, so an
    # off-by-one (`>` -> `>=`) cannot survive.
    enable_flag(monkeypatch)
    install_confident()
    at_cap = body_of_exact_size(MAX_BODY_BYTES)
    assert len(at_cap) == MAX_BODY_BYTES
    assert _post_raw(client, "sensitivity", at_cap).status_code == 200

    install_landmine_seams()
    over_cap = body_of_exact_size(MAX_BODY_BYTES + 1)
    assert len(over_cap) == MAX_BODY_BYTES + 1
    response = _post_raw(client, "sensitivity", over_cap)
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


def test_as5_documented_caps_are_the_literal_values():
    # G3 C5: the other cap tests are written RELATIVE to these constants, so loosening a cap
    # (64 KiB -> 256 KiB, domain 256 -> 1024) would keep them all green. Pin the documented
    # literals so a widened boundary is a test failure, not a silent posture change.
    assert MAX_BODY_BYTES == 65536
    assert MAX_NESTING_DEPTH == 32
    assert MAX_STRING_LENGTH == 4096
    assert MAX_ASSUMPTION_SETS == 50
    assert MAX_CANDIDATE_DOMAIN_LENGTH == 256
    assert MAX_ASSUMPTIONS_PER_SET == 64


def test_as5_string_length_cap_is_exact_at_the_boundary(client, monkeypatch):
    # G3 C6: N accepted, N + 1 rejected - for a string VALUE and for a dict KEY.
    enable_flag(monkeypatch)
    install_confident()
    at_cap = {"variable": "utilization_factor", "note": "q" * MAX_STRING_LENGTH}
    assert client.post(url("sensitivity"), json=at_cap).status_code == 200

    install_landmine_seams()
    over = {"variable": "utilization_factor", "note": "q" * (MAX_STRING_LENGTH + 1)}
    response = client.post(url("sensitivity"), json=over)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"

    install_landmine_seams()
    key_over = client.post(url("sensitivity"), json={"q" * (MAX_STRING_LENGTH + 1): 1})
    assert key_over.status_code == 422
    assert key_over.json()["state"] == "validation_error"


def test_as5_nesting_depth_cap_is_exact_at_the_boundary(client, monkeypatch):
    # G3 C6: a body nested to exactly MAX_NESTING_DEPTH container levels (the body object is
    # level 1) is ACCEPTED; one level deeper is a typed 422.
    enable_flag(monkeypatch)
    install_confident()
    at_cap = _post_raw(client, "sensitivity", nested_levels_body(MAX_NESTING_DEPTH))
    assert at_cap.status_code == 200

    install_landmine_seams()
    response = _post_raw(client, "sensitivity", nested_levels_body(MAX_NESTING_DEPTH + 1))
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


@pytest.mark.parametrize("content", ["{not valid json", "[1, 2, 3]", "42", '"a string"'])
def test_as5_malformed_or_non_object_body_is_typed_422(client, monkeypatch, content):
    enable_flag(monkeypatch)
    install_landmine_seams()
    response = _post_raw(client, "sensitivity", content)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


@pytest.mark.parametrize(
    ("analysis", "key"), [("sensitivity", "values"), ("threshold", "domain")]
)
def test_as5_candidate_domain_length_cap(client, monkeypatch, analysis, key):
    # G3 C6: exactly MAX_CANDIDATE_DOMAIN_LENGTH candidates is ACCEPTED, one more is a typed
    # 422 rejected BEFORE any fetch/rebuild (landmined seams prove it).
    enable_flag(monkeypatch)

    def body(count):
        out = {"variable": "utilization_factor", key: [0.8] * count}
        if analysis == "threshold":
            out["target"] = 10000
        return out

    install_confident()
    assert client.post(url(analysis), json=body(MAX_CANDIDATE_DOMAIN_LENGTH)).status_code == 200

    install_landmine_seams()
    response = client.post(url(analysis), json=body(MAX_CANDIDATE_DOMAIN_LENGTH + 1))
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_as5_assumption_set_caps(client, monkeypatch):
    # G3 C2: assert the documented STATE too, not only the status code - otherwise emitting an
    # undocumented (422, "too_many_sets") pair would ship green.
    enable_flag(monkeypatch)
    install_landmine_seams()

    # Too many named assumption-sets.
    many = {
        "objective": "maximize_illustrative_usable_area",
        "assumption_sets": [[] for _ in range(MAX_ASSUMPTION_SETS + 1)],
    }
    response = client.post(url("ranking"), json=many)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"

    # Too many assumptions within one set.
    big_set = {
        "objective": "maximize_illustrative_usable_area",
        "assumption_sets": [
            [_assumption("utilization_factor", 0.9)] * (MAX_ASSUMPTIONS_PER_SET + 1)
        ],
    }
    response = client.post(url("ranking"), json=big_set)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


@pytest.mark.parametrize("analysis", ["ranking", "comparison"])
def test_as5_assumption_set_count_cap_is_exact_at_the_boundary(client, monkeypatch, analysis):
    # G3 C6: exactly MAX_ASSUMPTION_SETS sets is ACCEPTED, one more is a typed 422.
    enable_flag(monkeypatch)
    install_confident()
    at_cap = {
        "objective": "maximize_illustrative_usable_area",
        "assumption_sets": _named_sets(MAX_ASSUMPTION_SETS),
    }
    assert client.post(url(analysis), json=at_cap).status_code == 200

    install_landmine_seams()
    over = {
        "objective": "maximize_illustrative_usable_area",
        "assumption_sets": _named_sets(MAX_ASSUMPTION_SETS + 1),
    }
    response = client.post(url(analysis), json=over)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_as5_assumptions_per_set_cap_is_exact_at_the_boundary(client, monkeypatch):
    # G3 C6: exactly MAX_ASSUMPTIONS_PER_SET assumptions in one set is ACCEPTED, one more is a
    # typed 422.
    enable_flag(monkeypatch)

    def body(count):
        return {
            "objective": "maximize_illustrative_usable_area",
            "assumption_sets": [
                {
                    "name": "one",
                    "assumptions": [_assumption("utilization_factor", 0.9)] * count,
                }
            ],
        }

    install_confident()
    assert client.post(url("ranking"), json=body(MAX_ASSUMPTIONS_PER_SET)).status_code == 200

    install_landmine_seams()
    response = client.post(url("ranking"), json=body(MAX_ASSUMPTIONS_PER_SET + 1))
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


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


@pytest.mark.parametrize(("position", "content"), SURROGATE_BODIES)
@pytest.mark.parametrize("analysis", ANALYSES)
def test_as5_unpaired_surrogate_is_typed_422(client, monkeypatch, analysis, position, content):
    """G5 BLOCKING-1: ``{"variable": "\\ud800"}`` is 21 pure-ASCII bytes, under every documented
    cap, and ``json.loads`` accepts it - but it is NOT encodable text. The route validated with
    ``json.dumps(..., allow_nan=False)`` (``ensure_ascii=True``, which ESCAPES surrogates and so
    never raises) while Starlette renders with ``ensure_ascii=False`` + ``.encode("utf-8")``,
    which DOES raise: the two disagreed about what is encodable. Before the fix these bodies
    either crashed the endpoint with a framework text/plain 500 (no state, no correlation id, a
    pair outside the matrix, traceback logged) or were silently dropped into a 200. Every
    position x every endpoint must now be the same typed 422."""
    enable_flag(monkeypatch)
    install_landmine_seams()

    response = _post_raw(client, analysis, content)
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert payload["state"] == "validation_error"
    assert "surrogate" in payload["message"]
    assert response.headers["x-correlation-id"]
    assert (422, "validation_error") in STATUS_STATE_MATRIX
    assert "Traceback" not in response.text


def test_as5_surrogate_body_is_tiny_and_under_every_cap(client, monkeypatch):
    """The hostile body is not an oversized-input case in disguise: it is smaller than every
    documented cap, so ONLY the encodability boundary can reject it."""
    content = SURROGATE_BODIES[0][1]
    # 22 ASCII bytes as spelled here (the gate quoted 21 for the space-free spelling) - either
    # way orders of magnitude under the byte cap, so no size boundary can be what rejects it.
    assert len(content.encode()) < 32
    assert len(content.encode()) < MAX_BODY_BYTES
    parsed = json.loads(content)
    assert len(parsed) == 1
    assert len(next(iter(parsed.values()))) < MAX_STRING_LENGTH

    enable_flag(monkeypatch)
    install_landmine_seams()
    assert _post_raw(client, "sensitivity", content).status_code == 422


@pytest.mark.parametrize("analysis", ANALYSES)
def test_as5_legitimate_non_ascii_text_is_still_accepted(client, monkeypatch, analysis):
    """The encodability boundary must reject ONLY unencodable text. Real non-ASCII - accents,
    CJK, an astral-plane emoji (a legitimate SURROGATE PAIR), smart quotes - is perfectly
    encodable and must still produce a 200, and must survive the ``ensure_ascii=False``
    renderer intact."""
    enable_flag(monkeypatch)
    install_confident()

    text = "\u00e9\u4e2d\U0001f600 \u201cquoted\u201d \u2014 caf\u00e9"
    body = {**BODIES[analysis], "illustrative_note": text}
    response = client.post(url(analysis), json=body)
    assert response.status_code == 200
    json.dumps(response.json(), allow_nan=False)
    # The renderer emitted real UTF-8, not escapes, and the body round-trips.
    assert response.json()["result"][RESULT_KINDS[analysis][0]] == RESULT_KINDS[analysis][1]


def test_as5_non_ascii_assumption_text_round_trips_into_the_response(client, monkeypatch):
    """Stronger form of the same guard: non-ASCII text the engine ECHOES must appear in the
    response unchanged, proving the pre-send check does not reject what the renderer accepts."""
    enable_flag(monkeypatch)
    install_confident()

    text = "r\u00e9duction \u4e2d\u6587 \U0001f600"
    assumption = {**_assumption("utilization_factor", 0.7), "rationale": text}
    # The comparison engine needs at least TWO sets to compare (one yields a typed
    # invalid_comparison_request that echoes no sets), so the non-ASCII set is compared
    # against a baseline and therefore really is echoed back.
    body = {
        "assumption_sets": [
            {"name": "baseline", "assumptions": []},
            {"name": "caf\u00e9", "assumptions": [assumption]},
        ]
    }
    response = client.post(url("comparison"), json=body)
    assert response.status_code == 200
    assert response.json()["result"]["comparison_kind"] == (
        "scenario_assumption_set_comparison"
    )
    assert text in response.text
    assert "caf\u00e9" in response.text


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

    # Never Verified ANYWHERE in the envelope (every key and string value, every depth);
    # the canonical disclaimer is present at the envelope AND in the result.
    assert_nothing_is_verified(envelope)
    assert envelope["result"]["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER


def test_as6_unencodable_engine_result_is_typed_internal_contract_error_500(
    raw_client, monkeypatch
):
    """BLOCKING-1, the pre-send half: the envelope check now uses the SAME encoder settings as
    the renderer (``ensure_ascii=False`` + ``.encode("utf-8")``), so a string the renderer
    cannot encode is caught BEFORE send and mapped to the documented
    ``(500, "internal_contract_error")`` pair. With the old ``ensure_ascii=True`` check this
    passed validation and then raised inside the renderer - a framework text/plain 500."""
    enable_flag(monkeypatch)
    install_confident()
    monkeypatch.setattr(
        analysis_module, "analyze_scenario_sensitivity", lambda *a, **k: {"bad": "\ud800"}
    )

    response = raw_client.post(url("sensitivity"), json=SENSITIVITY_BODY)
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["state"] == "internal_contract_error"
    assert (500, "internal_contract_error") in STATUS_STATE_MATRIX
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "Traceback" not in response.text


def test_as6_non_json_safe_engine_result_is_typed_500(raw_client, monkeypatch):
    """The same pre-send guard for a plainly unserializable result: a typed 500, never a
    partial 200 and never a framework stack."""
    enable_flag(monkeypatch)
    install_confident()
    monkeypatch.setattr(
        analysis_module, "analyze_scenario_sensitivity", lambda *a, **k: {"bad": object()}
    )

    response = raw_client.post(url("sensitivity"), json=SENSITIVITY_BODY)
    assert response.status_code == 500
    assert response.json()["state"] == "internal_contract_error"
    assert " at 0x" not in response.text


# ==========================================================================
# AS-7 - additive registration + offline + facade-only engine calls.
# ==========================================================================


def _flattened_route_list(application):
    """``app.routes`` with included routers expanded, registration order preserved.

    fastapi>=0.139 (starlette>=1.0) records each ``include_router`` call as one
    ``_IncludedRouter`` entry (``path`` is ``None``) whose ``original_router.routes``
    holds the prefixed ``APIRoute`` objects; older versions flatten them into
    ``app.routes`` directly. Expanding included routers in place preserves the
    registration order the assertions below pin, and is a no-op on the old layout.
    """
    flat = []
    for route in application.routes:
        inner = getattr(getattr(route, "original_router", None), "routes", None)
        flat.extend(inner if inner is not None else [route])
    return flat


def test_as7_analysis_routes_are_registered_last_and_in_order():
    """G3 C7: reordering the ``include_router`` calls in ``app.main`` survived every test. The
    claim being defended is ADDITIVE registration - the four analysis routes are appended
    AFTER every pre-existing router, in the documented order - so pin both."""
    paths = [getattr(route, "path", None) for route in _flattened_route_list(app)]
    expected = [f"/api/v1/properties/{{bbl}}/scenario/{analysis}" for analysis in ANALYSES]

    # Each analysis route is registered exactly once, in the documented order.
    assert [path for path in paths if path in set(expected)] == expected

    # ... and strictly AFTER every pre-existing route (additive, never interleaved).
    first_analysis = min(paths.index(path) for path in expected)
    for pre_existing in (
        "/api/v1/properties/{bbl}",
        "/api/v1/properties/{bbl}/rule-evaluation",
        "/api/v1/properties/{bbl}/scenario",
    ):
        assert paths.index(pre_existing) < first_analysis, f"{pre_existing} must precede"


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


@pytest.mark.parametrize("analysis", ANALYSES)
def test_as7_full_analysis_runs_fully_offline(client, monkeypatch, analysis):
    """AS-7 offline guarantee, asserted at the EGRESS SEAM for ALL FOUR endpoints (G5 LOW-4:
    the first version covered only ``comparison``).

    Rework note: the first version of this test replaced ``socket.socket`` globally, which
    DEADLOCKED the whole api suite - Starlette's ``TestClient`` drives the ASGI app through an
    anyio blocking portal, and that portal's event-loop wakeup needs ``socket.socket`` for its
    own ``socket.socketpair()`` (on Windows a real AF_INET localhost pair), so the portal thread
    could never service the request and the main thread waited on it forever. Blocking socket
    CONSTRUCTION is therefore the wrong seam; egress is asserted where it actually happens, at
    places the portal never touches:

    * ``pluto_soda._OPENER`` - the accepted monkeypatch seam the connector opens URLs through
      (the same seam tests/api/test_properties_v1.py already uses), plus the shared
      ``app.resilience.transport.DEFAULT_OPENER`` any other connector would fall back to;
    * ``http.client.HTTP(S)Connection.connect`` - every stdlib/urllib/httpx-style client's
      single socket-connect choke point;
    * ``socket.create_connection`` - the lower-level outbound connect helper those use.

    Each landmine RECORDS the attempt as well as raising, so ``egress == []`` still fails even
    if a connector translates the raise into a typed transport error instead of propagating it.
    Positively: the injected fixture fetcher and substrate are proven to be the only sources
    consulted, and no Socrata credential exists to read or reaches an outbound header.
    """
    monkeypatch.delenv(pluto_soda.APP_TOKEN_ENV_VAR, raising=False)
    enable_flag(monkeypatch)

    egress: list[str] = []

    def _landmine(label: str):
        def _attempt(*args, **kwargs):
            egress.append(label)
            raise AssertionError(f"network egress attempted during an analysis request: {label}")

        return _attempt

    class _LandmineOpener:
        """Stand-in for the no-redirect urllib opener: opening anything at all is egress."""

        handlers: tuple = ()

        def __init__(self) -> None:
            self.open = _landmine("urllib opener.open")

    monkeypatch.setattr(pluto_soda, "_OPENER", _LandmineOpener())
    monkeypatch.setattr(resilience_transport, "DEFAULT_OPENER", _LandmineOpener())
    monkeypatch.setattr(
        http.client.HTTPConnection, "connect", _landmine("http.client.HTTPConnection.connect")
    )
    monkeypatch.setattr(
        http.client.HTTPSConnection, "connect", _landmine("http.client.HTTPSConnection.connect")
    )
    monkeypatch.setattr(socket, "create_connection", _landmine("socket.create_connection"))

    # The ONLY two sources this request may consult, each recording that it was used.
    consulted: list[str] = []
    outbound_headers: list[dict] = []

    class RecordingTransport(FakeTransport):
        def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
            outbound_headers.append(dict(headers))
            return super().__call__(url, headers, timeout)

    def _recording_fetcher_provider():
        def fetch(bbl: str, correlation_id: str):
            consulted.append("pluto_fetcher")
            return fetch_by_bbl(
                bbl,
                transport=RecordingTransport([fixture_response("F01_single_lot_normal.json")]),
                sleep=lambda s: None,
                clock=FIXED_CLOCK,
                correlation_id=correlation_id,
            )

        return fetch

    substrate = confident_r5_substrate()

    def _recording_substrate_provider():
        def provide(canonical_bbl: str, correlation_id: str):
            consulted.append("spatial_substrate")
            return substrate

        return provide

    app.dependency_overrides[get_pluto_fetcher] = _recording_fetcher_provider
    app.dependency_overrides[get_spatial_substrate_provider] = _recording_substrate_provider

    response = client.post(url(analysis), json=BODIES[analysis])

    # The offline guarantee: not one egress attempt on any real outbound path.
    assert egress == []
    assert response.status_code == 200
    kind_field, kind = RESULT_KINDS[analysis]
    assert response.json()["result"][kind_field] == kind

    # ... and the answer was built from the injected fixture seams, nothing else.
    assert sorted(set(consulted)) == ["pluto_fetcher", "spatial_substrate"]
    assert outbound_headers, "the fixture transport must have been exercised"

    # No credential was available to read, and none was placed on an outbound header.
    assert pluto_soda.APP_TOKEN_ENV_VAR not in os.environ
    assert all("x-app-token" not in {key.lower() for key in h} for h in outbound_headers)
