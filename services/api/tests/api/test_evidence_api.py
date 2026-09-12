"""Internal evidence / provenance endpoint acceptance pack (task M5-T013, AS-1..AS-8).

Offline and deterministic: the route's PLUTO fetcher and its server-side spatial-substrate
provider are both overridden via FastAPI dependency injection with the accepted recorded-official
PLUTO fixtures (services/api/tests/fixtures/pluto) and faithful M2-T013 substrate dicts - the SAME
harness the accepted scenario / rule-evaluation tests use - so NO test touches the network,
Supabase, or Geoclient (AS-8). Coverage: AS-1 whole trail verbatim (byte-equal provenance /
citations / input); AS-2 transport-not-interpret (cap + citations byte-identical, no arithmetic);
AS-3 body-less (body ignored, non-GET 405, malformed BBL 422 pre-fetch); AS-4 flag-gated fail-safe
(generic 404, no OpenAPI, existing flag reused); AS-5 STATUS_STATE_MATRIX == the rule-eval route's
set + thin trail is a normal typed 200; AS-6 fail-closed serialisation (typed 500 per stage, both
json.dumps forms); AS-7 never Verified unless the source says so (server-authored scope); AS-8
additive registration (evidence LAST), egress-seam landmine (zero egress), existing routes intact.

Gate-wave rework (G1/G3/G5). The first pack asserted over PROJECTIONS - hand-picked field lists -
so it passed while the document silently dropped 18 required source-contract fields. Every
transport assertion here is now TOTAL rather than sampled:

* KEY-SET equality against the source contract's own bundled schema, so an omission fails
  (G1 BLOCKING-1);
* WHOLE-SUBTREE byte-equality of every transported sub-document within one build (G3 H-1);
* ``_stable_view`` compares the ENTIRE document with only the one empirically-volatile leaf key
  masked, instead of ~12 hand-picked fields (G3 H-1);
* the never-Verified check WALKS the document instead of enumerating four paths (G3 H-3);
* the route's own FastAPI view is asserted to expose no query parameter and no body (G3 H-4);
* the fetch-stage guard is driven (G3 H-2);
* the two pure classifiers are unit-tested directly, reaching the outcomes no available fixture
  can produce (G3 H-5), including the typed ``rule_conflict`` gap (G1 HIGH-1).
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

from app.api.v1 import evidence as evidence_module
from app.api.v1.evidence import (
    EVIDENCE_CONTRACT_VERSION,
    STATUS_STATE_MATRIX,
    _completeness_marker,
    _gap_markers,
    _verification_status,
    assemble_evidence_document,
)
from app.api.v1.properties import STATUS_STATE_MATRIX as PROPERTY_MATRIX
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.config import (
    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
    INTERNAL_SCENARIO_ENABLED_ENV_VAR,
)
from app.connectors import pluto_soda
from app.connectors.bbl import normalize_bbl
from app.connectors.pluto_soda import (
    SOURCE_ID,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app
from app.profile.builder import build_property_profile
from app.resilience import transport as resilience_transport
from app.rules.integration import evaluate_property
from app.rules.response import (
    RuleEvaluationContractError,
    _load_bundled_schema,
    serialize_rule_evaluation,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"

# The confident-R5 fixture + substrate yield this canonical draft cap VERBATIM from the trace.
TRACE_CAP = 15000.0

EVIDENCE_URL = f"/api/v1/properties/{BBL}/evidence"


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


def install_confident(fixture: str = "F01_single_lot_normal.json") -> None:
    install_fetcher(lambda: [fixture_response(fixture)])
    install_substrate(confident_r5_substrate())


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
    # The evidence view REUSES the rule-evaluation flag (it surfaces that trail verbatim).
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


def _rebuild_with_substrate(substrate, fixture: str = "F01_single_lot_normal.json"):
    """Build the profile + rule_evaluation exactly as the endpoint does - WITH the injected
    substrate - over the offline fixture seams, for use as a deterministic byte-equality baseline.
    Uses a fixed correlation id; only correlation-derived ids (observation_id) differ from a live
    request, so the deterministic provenance/citation fields are directly comparable."""
    result = fetch_by_bbl(
        normalize_bbl(BBL).canonical,
        transport=FakeTransport([fixture_response(fixture)]),
        sleep=lambda s: None,
        clock=FIXED_CLOCK,
        correlation_id="baseline",
    )
    profile = build_property_profile(result, spatial_intersection=substrate)
    rule_eval = serialize_rule_evaluation(
        evaluate_property(profile),
        profile_contract_version=profile["profile_version"]["contract_version"],
    )
    return profile, rule_eval


# ---------------------------------------------------------------------------
# The SOURCE contract this document must carry IN FULL (G1 BLOCKING-1). Loaded from the app's OWN
# bundled schema - the very copy app.rules.response validates the rebuilt document against - so
# the assertion is anchored to the CONTRACT, not to whatever the assembler happens to emit: a
# field added to the source contract and then dropped by the assembler fails here too.
# ---------------------------------------------------------------------------
_RULE_EVAL_SCHEMA = _load_bundled_schema("rule_evaluation.schema.json")
ROOT_REQUIRED = frozenset(_RULE_EVAL_SCHEMA["required"])
TRACE_REQUIRED = frozenset(_RULE_EVAL_SCHEMA["$defs"]["evaluation_trace"]["required"])
EVALUATED_INPUT_REQUIRED = frozenset(_RULE_EVAL_SCHEMA["$defs"]["evaluated_input"]["required"])

# The single server-authored key added to each transported trace. It is deliberately NOT a key of
# the closed evaluation_trace contract, so it cannot shadow a transported field.
SERVER_AUTHORED_CLAIM_KEY = "claim_verification_status"

# Per-request-volatile leaf keys. A rebuilt profile provenance record embeds an observation_id
# derived from that request's random correlation id. Probed empirically: across two identical
# requests this is the ONLY differing leaf anywhere in the document (67 occurrences, all under
# profile_provenance), so EVERYTHING else can be compared byte-for-byte.
_VOLATILE_LEAF_KEYS = frozenset({"observation_id"})


# Deterministic identity projections, used only where two INDEPENDENT builds are compared (their
# observation_ids legitimately differ). Within one build, full byte-equality is asserted instead -
# see test_as8_direct_assembly_is_pure_transport.
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


def _applicable_group(doc: dict) -> dict:
    """The single rule_citations group whose transported trace is the
    APPLICABLE evaluation (each group is the whole trace verbatim plus
    claim_verification_status, so applicability_outcome travels with it;
    M4-T011)."""
    applicable = [
        g for g in doc["rule_citations"] if g["applicability_outcome"] is True
    ]
    assert len(applicable) == 1, sorted(g["rule_id"] for g in applicable)
    return applicable[0]


def _prov_identity(record) -> tuple:
    return (record["source_id"], record["retrieved_at"], record.get("dataset_version"))


def _cit_identity(citation) -> tuple:
    return (citation["snapshot_id"], citation["section"], citation["quote"])


# Keys that ASSERT a verification state, found by WALKING the document (G3 H-3: the previous
# helper enumerated four paths, so a NEW server-authored `verified: True` - at the top level or
# nested per citation group - was invisible to AS-7). Free prose transported inside a citation
# quote / note / description may itself contain the word "Verified"; that is DELIBERATELY out of
# scope and documented on the response in `verification_scope_note` (a blanket token scan is
# falsifiable, and transported prose is never a server-authored status - AS-7 / M5-T012 finding).
_VERIFICATION_CLAIM_KEYS = frozenset(
    {
        "verified",
        "is_verified",
        "verification",
        "verification_status",
        "claim_verification_status",
        "overall_verification_status",
        "coverage_status",
        "verified_eligible",
    }
)


def _verification_claims(node, path="$"):
    """Yield ``(path, key, value)`` for EVERY verification-claim key anywhere in the document, at
    any depth - so a claim added in a new place is caught rather than missed by an enumeration."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}"
            if key in _VERIFICATION_CLAIM_KEYS:
                yield child, key, value
            yield from _verification_claims(value, child)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _verification_claims(item, f"{path}[{index}]")


# ==========================================================================
# AS-1 - evidence document over server-rebuilt facts.
# ==========================================================================


def test_as1_deterministic_provenance_and_citations_transport_byte_equal(client, monkeypatch):
    # (Renamed: this test compares an independent rebuild, so it asserts the DETERMINISTIC
    # fields. The "whole trail" claim is carried by
    # test_as1_document_carries_every_source_contract_field and by the whole-subtree equality in
    # test_as8_direct_assembly_is_pure_transport - G3 H-1.)
    enable_flag(monkeypatch)
    install_confident()
    response = client.get(EVIDENCE_URL)
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    doc = response.json()

    # (versioned document)
    assert doc["contract_version"] == EVIDENCE_CONTRACT_VERSION
    assert doc["document_kind"] == "evidence_trail"
    assert doc["bbl"] == BBL

    # (a) every profile provenance record, (c) the input provenance, (d) per-claim DRAFT status.
    assert isinstance(doc["profile_provenance"], list) and doc["profile_provenance"]
    assert doc["evaluated_input"]["input_provenance"]
    assert doc["rule_citations"]
    for citation_group in doc["rule_citations"]:
        assert citation_group["claim_verification_status"] == "draft"
        # (b) every rule citation together with its OWN provenance.
        for citation in citation_group["citations"]:
            assert citation["provenance"]  # a material value never leaves without provenance
            assert citation["snapshot_id"] and citation["section"] and citation["quote"]

    # Build the SAME profile + rule_evaluation the endpoint rebuilds - WITH the injected spatial
    # substrate (like the rule-evaluation route) - directly, so the deterministic provenance and
    # citation fields have the right baseline. (GET /properties is PLUTO-ONLY, no substrate, so it
    # carries FEWER provenance records and is NOT the correct baseline for the evidence trail.)
    baseline_profile, baseline_rule_eval = _rebuild_with_substrate(confident_r5_substrate())

    # Each emitted source id + retrieval timestamp is byte-equal to the freshly rebuilt profile's
    # (the deterministic provenance fields AS-1 names; the per-build observation_id is excluded).
    assert sorted(_prov_identity(r) for r in doc["profile_provenance"]) == sorted(
        _prov_identity(r) for r in baseline_profile["provenance"]
    )
    assert len(doc["profile_provenance"]) == len(baseline_profile["provenance"])

    # The input provenance refs and the deterministic input_fingerprint transport verbatim (these
    # carry no correlation-derived content, so they ARE byte-equal across builds).
    assert doc["evaluated_input"]["input_provenance"] == baseline_rule_eval["evaluated_input"][
        "input_provenance"
    ]
    assert doc["evaluated_input"]["input_fingerprint"] == baseline_rule_eval["evaluated_input"][
        "input_fingerprint"
    ]

    # Each emitted citation string (snapshot / section / quote) is byte-equal to the rebuilt
    # trace's. (Full-record byte-equality WITHIN one build is proven in test_as8_direct_assembly.)
    trace_citations = [c for trace in baseline_rule_eval["evaluations"] for c in trace["citations"]]
    evidence_citations = [c for g in doc["rule_citations"] for c in g["citations"]]
    assert sorted(_cit_identity(c) for c in evidence_citations) == sorted(
        _cit_identity(c) for c in trace_citations
    )


def test_as1_document_carries_every_source_contract_field(client, monkeypatch):
    """G1 BLOCKING-1 regression, asserted as KEY-SET EQUALITY against the source contract.

    The first version hand-picked 14 of the rule_evaluation root's 20 required keys and 7 of each
    evaluation_trace's 19, silently dropping 18 contract fields. Key-set equality is the assertion
    a projection CANNOT satisfy, so a future omission fails here instead of shipping. It is driven
    off the app's own bundled schema, so a field ADDED to the source contract and then dropped by
    the assembler also fails."""
    enable_flag(monkeypatch)
    install_confident()
    doc = client.get(EVIDENCE_URL).json()
    _, baseline_rule_eval = _rebuild_with_substrate(confident_r5_substrate())

    # (1) The relocation map is DECLARED in the response, and each target key really exists - so
    #     "relocated, not omitted" is verifiable by a consumer, not just asserted in prose.
    routing = doc["source_field_routing"]
    assert routing == {"evaluations": "rule_citations", "evaluated_input": "evaluated_input"}
    for source_key, document_key in routing.items():
        assert document_key in doc, f"{source_key} routed to a key the document lacks"

    # (2) The root: every required source field is present, either in source_coverage or at the
    #     declared relocation target. Equality both ways - nothing dropped, nothing invented.
    assert set(doc["source_coverage"]) | set(routing) == ROOT_REQUIRED
    assert set(doc["source_coverage"]) | set(routing) == set(baseline_rule_eval)

    # (3) Every citation group is the WHOLE evaluation_trace plus exactly one server-authored key.
    assert doc["rule_citations"]
    for group in doc["rule_citations"]:
        assert set(group) == TRACE_REQUIRED | {SERVER_AUTHORED_CLAIM_KEY}

    # (4) The evaluated_input sub-document, in full.
    assert set(doc["evaluated_input"]) == EVALUATED_INPUT_REQUIRED

    # (5) And the same holds for every trace the engine actually produced.
    for group, trace in zip(doc["rule_citations"], baseline_rule_eval["evaluations"], strict=True):
        assert set(group) - {SERVER_AUTHORED_CLAIM_KEY} == set(trace)


def test_as1_the_qualifications_that_make_the_cap_honest_travel_with_it(client, monkeypatch):
    """BLOCKING-1 in domain terms rather than key-sets. The F01 trail presents a 15000.0 sq ft
    cap; the qualifications that make that figure honest must travel WITH it. Dropping them
    rendered a QUALIFIED figure as UNQUALIFIED in the one surface built to audit it."""
    enable_flag(monkeypatch)
    install_confident()
    doc = client.get(EVIDENCE_URL).json()
    group = _applicable_group(doc)

    assert group["outputs"]["max_residential_floor_area_sq_ft"] == TRACE_CAP

    # The documented exception: a HIGHER residential FAR may apply under ZR 23-21, so the cap is
    # conditional. Dropping this presented a conditional cap as settled.
    assert group["exceptions_applied"]
    assert any("23-21" in json.dumps(entry) for entry in group["exceptions_applied"])

    # The honest note that this is not an evidence-based determination.
    assert group["notes"]
    assert any("not" in str(note).lower() for note in group["notes"])

    # The derivation behind the number (lot area x FAR), carried rather than summarised away.
    assert group["computation_steps"]
    assert any(step.get("result") == TRACE_CAP for step in group["computation_steps"])

    # The G6 approval state travels too - the reader can see this is not Verified-eligible yet.
    assert group["rule_release"]["verified_eligible"] is False

    # Root-level context the figure depends on, and the typed conflict slot.
    assert doc["source_coverage"]["zoning_district"] == "R5"
    assert doc["source_coverage"]["lot_area_sq_ft"] == 10000.0
    assert doc["source_coverage"]["lot_area_source"]
    assert "rule_conflict" in doc["source_coverage"]
    assert "spatial_context" in doc["source_coverage"]
    assert "spatial_uncertainty" in doc["source_coverage"]


# ==========================================================================
# AS-2 - transport, never interpret.
# ==========================================================================


def test_as2_cap_and_citations_are_byte_identical_to_the_trace(client, monkeypatch):
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    install_confident()
    doc = client.get(EVIDENCE_URL).json()

    install_confident()
    rule_eval = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()
    trace_cap = _applicable_trace(rule_eval)["outputs"]["max_residential_floor_area_sq_ft"]

    # The canonical cap is transported VERBATIM (never recomputed).
    evidence_cap = _applicable_group(doc)["outputs"]["max_residential_floor_area_sq_ft"]
    assert evidence_cap == trace_cap == TRACE_CAP

    # Every citation text and its section reference are byte-identical to the trace's.
    for group, trace in zip(doc["rule_citations"], rule_eval["evaluations"], strict=True):
        assert group["citations"] == trace["citations"]
        assert group["coverage_status"] == trace["coverage_status"]


def test_as2_module_does_no_arithmetic_or_reevaluation(client, monkeypatch):
    # Structural proof the route transports rather than interprets: it never re-runs the scenario
    # builder, imports no math, and evaluates the property exactly ONCE (the trusted rebuild).
    source = Path(evidence_module.__file__).read_text(encoding="utf-8")
    assert "build_scenario" not in source
    assert "import math" not in source
    assert source.count("evaluate_property(") == 1

    # And no new legal rule is introduced: the endpoint adds no rule and is not G6-blocked; the
    # transported cap equals the source cap (already proven byte-equal above), so nothing here
    # rewrote a legal value.
    enable_flag(monkeypatch)
    install_confident()
    doc = client.get(EVIDENCE_URL).json()
    assert doc["overall_verification_status"] == "draft"


# ==========================================================================
# AS-3 - body-less, zero untrusted-input surface.
# ==========================================================================


def _stable_view(doc):
    """The WHOLE document with only the per-request-volatile leaves masked, so two independent
    builds can be compared for BODY influence rather than inherent randomness.

    G3 H-1: the previous version projected ~12 hand-picked fields, so a mutation anywhere else in
    the document was invisible to every test that compared stable views. Masking exactly one
    empirically-determined volatile leaf key (:data:`_VOLATILE_LEAF_KEYS`) lets the comparison be
    total instead."""
    if isinstance(doc, dict):
        return {
            key: "<volatile>" if key in _VOLATILE_LEAF_KEYS else _stable_view(value)
            for key, value in doc.items()
        }
    if isinstance(doc, list):
        return [_stable_view(item) for item in doc]
    return doc


def test_as3_request_body_cannot_influence_the_response(client, monkeypatch):
    enable_flag(monkeypatch)
    install_confident()
    clean = client.get(EVIDENCE_URL).json()

    # A GET carrying a body must be given NO meaning by the handler: every deterministic part of
    # the document is identical and the injected values appear nowhere.
    install_confident()
    bodied = client.request(
        "GET",
        EVIDENCE_URL,
        content=json.dumps(
            {
                "draft_zoning_floor_area_cap_sq_ft": 10**9,
                "verified": True,
                "coverage_status": "verified",
            }
        ).encode(),
        headers={"content-type": "application/json"},
    )
    assert bodied.status_code == 200
    assert _stable_view(bodied.json()) == _stable_view(clean)
    assert "1000000000" not in bodied.text


def _flattened_route_list(application):
    """``app.routes`` with included routers expanded, registration order preserved.

    fastapi>=0.139 (starlette>=1.0) records each ``include_router`` call as one
    ``_IncludedRouter`` entry (``path`` is ``None``) whose ``original_router.routes``
    holds the prefixed ``APIRoute`` objects; older versions flatten them into
    ``app.routes`` directly. Expanding included routers in place preserves the
    registration order the AS-8 assertions pin, and is a no-op on the old layout.
    """
    flat = []
    for route in application.routes:
        inner = getattr(getattr(route, "original_router", None), "routes", None)
        flat.extend(inner if inner is not None else [route])
    return flat


def test_as3_route_declares_no_query_parameter_and_no_body():
    """G3 H-4: AS-3's "no query parameter" half was untested - adding a `terse: bool = False`
    parameter that strips `profile_provenance` shipped green. Assert the route's OWN FastAPI view:
    the only declared parameter is the `bbl` path param, and there is no body field. The two
    Depends seams are checked too, so a query parameter cannot enter through a dependency."""
    route = next(
        r
        for r in _flattened_route_list(app)
        if getattr(r, "path", None) == "/api/v1/properties/{bbl}/evidence"
    )
    assert sorted(route.methods) == ["GET"]

    dependant = route.dependant
    assert [param.name for param in dependant.path_params] == ["bbl"]
    assert dependant.query_params == []
    assert dependant.body_params == []
    assert dependant.header_params == []
    assert dependant.cookie_params == []
    assert route.body_field is None

    # The injected seams are server-side providers: neither may introduce a caller-facing param.
    assert len(dependant.dependencies) == 2
    for sub_dependency in dependant.dependencies:
        assert sub_dependency.query_params == []
        assert sub_dependency.body_params == []


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_as3_no_non_get_method_is_served(client, monkeypatch, method):
    enable_flag(monkeypatch)
    install_confident()
    response = getattr(client, method)(EVIDENCE_URL)
    assert response.status_code == 405  # Method Not Allowed - only GET is served


@pytest.mark.parametrize(
    ("bbl", "expected_code"),
    [("abc", "non_numeric"), ("100001010", "wrong_length"), ("0000010100", "invalid_borough")],
)
def test_as3_malformed_bbl_is_typed_422_no_connector_call(client, monkeypatch, bbl, expected_code):
    enable_flag(monkeypatch)
    install_landmine_seams()  # a malformed BBL must be rejected BEFORE any fetch
    response = client.get(f"/api/v1/properties/{bbl}/evidence")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["detail"]["code"] == expected_code
    assert body["correlation_id"]


# ==========================================================================
# AS-4 - flag-gated fail-safe, no OpenAPI leak, existing flag reused.
# ==========================================================================


@pytest.mark.parametrize("flag_value", [None, "", "0", "false", "off", "maybe", "2", "  "])
def test_as4_flag_off_or_unknown_is_generic_404(client, monkeypatch, flag_value):
    if flag_value is None:
        monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, flag_value)
    install_landmine_seams()

    response = client.get(EVIDENCE_URL)
    assert response.status_code == 404
    # Byte-indistinguishable from an unmounted path: only {"detail": "Not Found"}.
    assert response.json() == {"detail": "Not Found"}
    text = response.text.lower()
    assert "evidence" not in text and "flag" not in text
    assert "x-correlation-id" not in {k.lower() for k in response.headers}


def test_as4_reuses_the_existing_rule_eval_flag_not_a_new_one(client, monkeypatch):
    # A scenario-only flag does NOT enable this route: it is gated on the EXISTING rule-eval flag.
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    monkeypatch.setenv(INTERNAL_SCENARIO_ENABLED_ENV_VAR, "1")
    install_landmine_seams()
    assert client.get(EVIDENCE_URL).status_code == 404

    # Flip the rule-eval flag on -> the route serves.
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    install_confident()
    assert client.get(EVIDENCE_URL).status_code == 200


def test_as4_openapi_never_lists_the_route_and_is_byte_identical_off_and_on(client, monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    off = client.get("/openapi.json").text
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    on = client.get("/openapi.json").text

    assert "/api/v1/properties/{bbl}/evidence" not in json.loads(on)["paths"]
    assert "/api/v1/properties/{bbl}" in json.loads(on)["paths"]  # existing route unaffected
    assert off == on  # the OpenAPI document is byte-identical with the flag off and on


# ==========================================================================
# AS-5 - documented status/state matrix + honest non-errors.
# ==========================================================================


def test_as5_matrix_equals_the_rule_evaluation_route_emitted_set():
    # Single source of truth: exactly the pairs the mirrored rule-evaluation route emits, which is
    # the property route's matrix MINUS the (500, unsupported_contract_version) pair the rebuild
    # path collapses into the shared (500, internal_contract_error). NO new pair is introduced.
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
    version_pair = (500, "unsupported_contract_version")
    assert STATUS_STATE_MATRIX == PROPERTY_MATRIX - {version_pair}
    assert version_pair not in STATUS_STATE_MATRIX


def test_as5_thin_professional_review_trail_is_a_normal_200_typed_document(client, monkeypatch):
    # A professional-review evidence trail is a NORMAL 200 typed document carrying a typed reason,
    # never an error and never silently omitted - the user must be able to SEE that it is thin.
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    install_substrate(split_lot_substrate())

    response = client.get(EVIDENCE_URL)
    assert response.status_code == 200
    assert response.headers["x-correlation-id"]
    doc = response.json()

    assert doc["evidence_completeness"] == "professional_review_required"
    assert doc["gaps"]  # gaps are NAMED, never silently dropped
    kinds = {gap["kind"] for gap in doc["gaps"]}
    assert "professional_review_required" in kinds
    for gap in doc["gaps"]:
        assert gap["kind"] in {
            "not_available",
            "not_applicable",
            "professional_review_required",
            "data_conflict",
        }
        assert "reason" in gap  # a typed marker always carries a reason
    # Still honest and never Verified.
    assert doc["overall_verification_status"] == "draft"
    assert doc["not_verified_disclaimer"]


def test_as5_every_emitted_pair_is_in_the_matrix(client, raw_client, monkeypatch):
    enable_flag(monkeypatch)
    emitted: set[tuple[int, str | None]] = set()

    def record(response):
        state = None if response.status_code == 200 else response.json().get("state")
        emitted.add((response.status_code, state))

    # 200 confident + 200 professional-review (both NORMAL 200 / no state).
    for substrate in (confident_r5_substrate(), split_lot_substrate()):
        install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
        install_substrate(substrate)
        resp = client.get(EVIDENCE_URL)
        assert resp.status_code == 200
        record(resp)

    # 422 malformed BBL, with NO connector call.
    install_landmine_seams()
    record(client.get("/api/v1/properties/abc/evidence"))

    # 404 no_match.
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    record(client.get("/api/v1/properties/5999999999/evidence"))

    # 504 timeout, 503 source_unavailable, 502 schema_drift, 503 rate_limited.
    for script, expected in (
        (lambda: [TransportTimeout("t")] * 3, 504),
        (lambda: [TransportFailure("f")] * 3, 503),
        (lambda: [fixture_response("F13_schema_drift_no_such_column_400.json")], 502),
        (lambda: [fixture_response("F07_rate_limit_429_synthetic.json")] * 3, 503),
    ):
        install_fetcher(script)
        install_substrate(confident_r5_substrate())
        resp = client.get(EVIDENCE_URL)
        assert resp.status_code == expected
        record(resp)

    # 500 internal_contract_error: force the rebuilt rule_evaluation document validator to fail.
    install_confident()
    monkeypatch.setattr(
        evidence_module,
        "validate_rule_evaluation_document",
        lambda doc: (_ for _ in ()).throw(
            RuleEvaluationContractError("forced contract defect", location="<root>")
        ),
    )
    record(raw_client.get(EVIDENCE_URL))

    # 500 internal_error: any unexpected exception in the rebuild stage -> the generic pair.
    install_confident()
    monkeypatch.setattr(
        evidence_module,
        "build_property_profile",
        lambda result, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    record(raw_client.get(EVIDENCE_URL))

    # Every documented pair was actually driven AND nothing undocumented was emitted.
    assert emitted == STATUS_STATE_MATRIX


def test_as5_no_match_is_documented_404_no_trail(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fetcher(lambda: [fixture_response("F03b_no_match_valid_bbl.json")])
    install_substrate(None)
    response = client.get("/api/v1/properties/5999999999/evidence")
    assert response.status_code == 404
    assert response.headers["x-correlation-id"]
    body = response.json()
    assert body["state"] == "no_match"  # distinguishable from the disabled-flag 404
    assert body["source_id"] == SOURCE_ID
    assert "profile_provenance" not in body and "rule_citations" not in body


# ==========================================================================
# AS-6 - fail-closed serialisation (M5-T012's gate findings carried forward).
# ==========================================================================


def test_as6_rebuild_stage_raise_is_typed_internal_error_500(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_confident()

    def exploding_builder(result, **kwargs):
        raise RuntimeError("secret-internal-path C:\\hostile\r\n::injected")

    monkeypatch.setattr(evidence_module, "build_property_profile", exploding_builder)
    response = raw_client.get(EVIDENCE_URL)
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["state"] == "internal_error"
    assert (500, "internal_error") in STATUS_STATE_MATRIX
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


def test_as6_fetch_stage_raise_is_typed_internal_error_500(raw_client, monkeypatch):
    """G3 H-2: the FETCH stage has its own generic-500 guard (for anything the injected fetcher
    raises that is NOT a typed PlutoConnectorError), and removing that guard stayed green because
    no test drove it. An unexpected fetcher exception must honor the documented typed pair with a
    correlation id, never escape as an untyped text/plain ASGI 500, and never leak."""
    enable_flag(monkeypatch)

    def exploding_fetcher(bbl, correlation_id):
        raise RuntimeError("secret-internal-path C:\\hostile\r\n::fetch boom")

    app.dependency_overrides[get_pluto_fetcher] = lambda: exploding_fetcher
    app.dependency_overrides[get_spatial_substrate_provider] = lambda: (
        lambda canonical_bbl, correlation_id: confident_r5_substrate()
    )

    response = raw_client.get(EVIDENCE_URL)
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["state"] == "internal_error"
    assert (500, "internal_error") in STATUS_STATE_MATRIX
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "hostile" not in response.text
    assert "secret-internal-path" not in response.text
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


def test_as6_assembly_stage_raise_is_typed_internal_error_500(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_confident()

    def exploding_assembly(*args, **kwargs):
        raise RuntimeError("assembly-stage boom")

    monkeypatch.setattr(evidence_module, "assemble_evidence_document", exploding_assembly)
    response = raw_client.get(EVIDENCE_URL)
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["state"] == "internal_error"
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "boom" not in response.text


@pytest.mark.parametrize(
    ("label", "bad_document"),
    [
        ("unpaired_surrogate", {"contract_version": "1.0.0", "bad": "\ud800"}),
        ("nan", {"contract_version": "1.0.0", "bad": float("nan")}),
        ("infinity", {"contract_version": "1.0.0", "bad": float("inf")}),
    ],
)
def test_as6_unserialisable_assembled_document_is_typed_contract_error_500(
    raw_client, monkeypatch, label, bad_document
):
    """The final serialisation stage: an assembled document the renderer cannot encode (an
    unpaired surrogate - M5-T012 G5 BLOCKING-1) or that carries non-finite content is caught
    BEFORE send by _assert_json_safe and mapped to the documented typed pair, never an untyped
    text/plain 500 from the ASGI layer."""
    enable_flag(monkeypatch)
    install_confident()
    monkeypatch.setattr(
        evidence_module, "assemble_evidence_document", lambda *a, **k: dict(bad_document)
    )

    response = raw_client.get(EVIDENCE_URL)
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["state"] == "internal_contract_error"
    assert (500, "internal_contract_error") in STATUS_STATE_MATRIX
    assert body["correlation_id"] == response.headers["X-Correlation-ID"]
    assert "Traceback" not in response.text


def test_as6_confident_document_survives_both_json_dumps_forms(client, monkeypatch):
    enable_flag(monkeypatch)
    install_confident()
    response = client.get(EVIDENCE_URL)
    assert response.status_code == 200
    doc = response.json()

    # BOTH renderings the stack could use must succeed (they disagree about unpaired surrogates
    # and the renderer uses the second): no NaN/Inf, no unpaired surrogate, no object-address leak.
    json.dumps(doc, allow_nan=False)
    json.dumps(doc, ensure_ascii=False, allow_nan=False).encode("utf-8")
    assert " at 0x" not in response.text
    # The module's own pre-send guard agrees.
    evidence_module._assert_json_safe(doc)


# ==========================================================================
# AS-7 - never Verified unless the source says so (scoped to server-authored content).
# ==========================================================================


def test_as7_no_server_authored_claim_is_verified(client, monkeypatch):
    enable_flag(monkeypatch)
    install_confident()
    doc = client.get(EVIDENCE_URL).json()

    # EVERY verification-claim key anywhere in the document (a WALK, not an enumeration) must
    # deny verification: never boolean True, never the status string 'verified'.
    claims = list(_verification_claims(doc))
    assert claims, "the walk must actually reach the verification-claim fields"
    for path, _key, value in claims:
        assert value is not True, f"a verification state is ASSERTED at {path}"
        assert str(value).strip().lower() != "verified", f"'verified' claimed at {path}"

    # The walk really does reach the top-level, per-group and deeply-nested claim fields - so a
    # new `verified: True` in any of those places would have been caught above.
    reached = {key for _path, key, _value in claims}
    assert {
        "overall_verification_status",
        "claim_verification_status",
        "coverage_status",
        "verified_eligible",
    } <= reached, reached

    assert doc["overall_verification_status"] == "draft"
    assert doc["not_verified_disclaimer"]
    assert "server-authored" in doc["verification_scope_note"].lower()
    assert "verbatim" in doc["verification_scope_note"].lower()


def test_as7_verification_status_only_echoes_the_source_case_insensitively():
    # _verification_status is the ONLY place a claim can be marked verified, and it can only echo
    # what the source coverage_status literally says (case-insensitive), never up-label.
    assert _verification_status("verified") == "verified"
    assert _verification_status("VERIFIED") == "verified"
    assert _verification_status("  Verified  ") == "verified"
    for draft_status in ("conditional", "professional_review_required", "unsupported", None, 123):
        assert _verification_status(draft_status) == "draft"


# ==========================================================================
# AS-8 - additive registration + offline + existing routes unaffected.
# ==========================================================================


def test_as8_evidence_route_is_registered_last_and_after_the_pre_existing_routes():
    paths = [getattr(route, "path", None) for route in _flattened_route_list(app)]
    evidence_path = "/api/v1/properties/{bbl}/evidence"
    assert paths.count(evidence_path) == 1
    evidence_index = paths.index(evidence_path)
    for pre_existing in (
        "/api/v1/properties/{bbl}",
        "/api/v1/properties/{bbl}/rule-evaluation",
        "/api/v1/properties/{bbl}/scenario",
    ):
        assert paths.index(pre_existing) < evidence_index, f"{pre_existing} must precede evidence"


def test_as8_existing_routes_unaffected(client, monkeypatch):
    assert client.get("/api/v1/health").status_code == 200

    install_fetcher(lambda: [fixture_response("F01_single_lot_normal.json")])
    prop = client.get(f"/api/v1/properties/{BBL}")
    assert prop.status_code == 200
    assert prop.json()["identity"]["bbl"] == BBL

    # The accepted GET rule-evaluation route still serves under the shared flag.
    enable_flag(monkeypatch)
    install_confident()
    assert client.get(f"/api/v1/properties/{BBL}/rule-evaluation").status_code == 200


def test_as8_evidence_request_runs_fully_offline(client, monkeypatch):
    """AS-8 offline guarantee asserted at the EGRESS SEAM (mirrors test_scenario_analysis_api's
    landmine harness). Blocking socket CONSTRUCTION deadlocks the anyio portal the TestClient
    drives the app through, so egress is asserted where it actually happens - the connector's
    URL opener, http.client's connect choke point, and socket.create_connection - each RECORDING
    the attempt as well as raising, so egress == [] fails even if a connector swallows the raise."""
    monkeypatch.delenv(pluto_soda.APP_TOKEN_ENV_VAR, raising=False)
    enable_flag(monkeypatch)

    egress: list[str] = []

    def _landmine(label: str):
        def _attempt(*args, **kwargs):
            egress.append(label)
            raise AssertionError(f"network egress attempted during an evidence request: {label}")

        return _attempt

    class _LandmineOpener:
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

    response = client.get(EVIDENCE_URL)

    assert egress == []
    assert response.status_code == 200
    assert response.json()["profile_provenance"]
    assert sorted(set(consulted)) == ["pluto_fetcher", "spatial_substrate"]
    assert outbound_headers, "the fixture transport must have been exercised"
    assert pluto_soda.APP_TOKEN_ENV_VAR not in os.environ
    assert all("x-app-token" not in {key.lower() for key in h} for h in outbound_headers)


def test_as8_direct_assembly_is_pure_transport(client, monkeypatch):
    # Assemble directly from the rebuilt documents (read back through the accepted routes) and
    # confirm the assembler transports rather than interprets: profile provenance, input
    # provenance and citations all appear verbatim in the assembled document.
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    install_confident()
    profile = client.get(f"/api/v1/properties/{BBL}").json()
    install_confident()
    rule_eval = client.get(f"/api/v1/properties/{BBL}/rule-evaluation").json()

    document = assemble_evidence_document(profile, rule_eval, bbl=BBL)

    # WHOLE-SUBTREE byte-equality (G3 H-1), not a hand-picked sample of fields. Within ONE build
    # every id is stable, so each transported sub-document must be byte-equal to its source. This
    # single block is what makes a joined `source_coverage.reasons`, an emptied
    # `data_completeness` / `family_coverage` / `rule_lifecycle_statuses`, a wrong
    # `evaluated_input.bbl` or `profile_contract_version`, or a dropped group `rule_version` /
    # `family` FAIL - each of those mutations previously survived because ~60% of the emitted
    # document was unasserted.
    routing = document["source_field_routing"]
    assert document["source_coverage"] == {
        key: value for key, value in rule_eval.items() if key not in routing
    }
    assert document["evaluated_input"] == rule_eval["evaluated_input"]
    assert document["profile_provenance"] == profile["provenance"]
    assert document["not_verified_disclaimer"] == rule_eval["not_verified_disclaimer"]

    assert len(document["rule_citations"]) == len(rule_eval["evaluations"])
    for group, trace in zip(document["rule_citations"], rule_eval["evaluations"], strict=True):
        assert group == {
            **trace,
            "claim_verification_status": _verification_status(trace["coverage_status"]),
        }

    # Transport is by DEEP COPY, never an alias into the source documents: mutating the assembled
    # document must not reach back into the rebuilt rule_evaluation.
    document["source_coverage"]["reasons"].append("mutated")
    assert "mutated" not in rule_eval["reasons"]

    # Serialisation-safe by construction.
    evidence_module._assert_json_safe(document)


# ==========================================================================
# AS-5 (continued) - the two PURE classifiers, unit-tested directly.
#
# G3 H-5: every substrate reachable from this suite yields
# professional_review_required, so `complete` / `thin` / `conflicting` and the
# not_applicable / data_conflict / rule_conflict gaps are UNREACHABLE through the
# route. Calling the pure functions directly is both the only way to reach them and
# the honest place to test a pure classifier - no fixtures, no runtime, no network.
# ==========================================================================


def _synthetic_rule_eval(**overrides) -> dict:
    """A minimal rule_evaluation-shaped dict for unit-testing the classifiers. Only the fields
    the two classifiers read are present; `overrides` drives each documented outcome."""
    base = {
        "coverage_status": "conditional",
        "coverage_source": "rule_engine",
        "data_completeness": "complete",
        "needs_review": False,
        "professional_review_required": False,
        "fail_safe": False,
        "fail_safe_reason": None,
        "rule_lifecycle_statuses": ["needs_review"],
        "reasons": [],
        "evaluations": [{"rule_id": "ZR-23-21", "coverage_status": "conditional"}],
        "rule_conflict": None,
    }
    base.update(overrides)
    return base


_HAS_PROVENANCE = {"provenance": [{"source_id": "nyc-dcp-mappluto-arcgis"}]}


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({}, "complete"),
        ({"coverage_status": "data_conflict"}, "conflicting"),
        ({"coverage_status": "professional_review_required"}, "professional_review_required"),
        ({"needs_review": True}, "professional_review_required"),
        ({"fail_safe": True}, "thin"),
        ({"coverage_status": "unsupported"}, "thin"),
        ({"coverage_status": "not_applicable"}, "thin"),
        ({"evaluations": []}, "thin"),
    ],
)
def test_as5_completeness_marker_classifies_every_documented_outcome(overrides, expected):
    # Reaches `complete`, `thin` and `conflicting` - none of which any available fixture can
    # produce - so the classifier's full documented vocabulary is covered, not just one value.
    assert _completeness_marker(_synthetic_rule_eval(**overrides)) == expected


@pytest.mark.parametrize(
    ("overrides", "expected_kind", "expected_subject"),
    [
        (
            {"fail_safe": True, "fail_safe_reason": "rule_conflict_detected"},
            "not_available",
            "rule_evaluation",
        ),
        ({"evaluations": []}, "not_available", "evaluation_trace"),
        ({"coverage_status": "data_conflict"}, "data_conflict", "coverage"),
        (
            {"coverage_status": "professional_review_required"},
            "professional_review_required",
            "coverage",
        ),
        ({"needs_review": True}, "professional_review_required", "coverage"),
        ({"coverage_status": "unsupported"}, "not_applicable", "coverage"),
        ({"coverage_status": "not_applicable"}, "not_applicable", "coverage"),
    ],
)
def test_as5_gap_markers_name_every_documented_gap(overrides, expected_kind, expected_subject):
    markers = _gap_markers(_HAS_PROVENANCE, _synthetic_rule_eval(**overrides))
    assert any(
        marker["kind"] == expected_kind and marker["subject"] == expected_subject
        for marker in markers
    ), markers
    for marker in markers:
        assert "reason" in marker  # a typed marker ALWAYS carries a reason


def test_as5_missing_profile_provenance_is_a_named_gap():
    markers = _gap_markers({"provenance": []}, _synthetic_rule_eval())
    assert any(
        marker["subject"] == "profile_provenance" and marker["kind"] == "not_available"
        for marker in markers
    )
    # A complete trail with provenance present names no provenance gap.
    clean = _gap_markers(_HAS_PROVENANCE, _synthetic_rule_eval())
    assert not [m for m in clean if m["subject"] == "profile_provenance"]
    assert clean == []


_CONFLICT = {
    "conflict": True,
    "family": "residential_far",
    "as_of_date": "2026-07-16",
    "competing_output_names": ["max_residential_far"],
    "competing_rules": [
        {
            "rule_id": "ZR-23-21-A",
            "rule_version": "1.0.0",
            "effective_from": "2020-01-01",
            "effective_to": None,
            "output_names": ["max_residential_far"],
        },
        {
            "rule_id": "ZR-23-21-B",
            "rule_version": "2.0.0",
            "effective_from": "2024-01-01",
            "effective_to": None,
            "output_names": ["max_residential_far"],
        },
    ],
    "note": "two same-family rules are simultaneously effective",
}


def _conflict_rule_eval() -> dict:
    """The shape app.rules.integration._conflict_result produces: fail-closed, no evaluations,
    professional review required, and the typed rule_conflict object preserved for reviewers."""
    return _synthetic_rule_eval(
        coverage_status="professional_review_required",
        needs_review=True,
        professional_review_required=True,
        fail_safe=True,
        fail_safe_reason="rule_conflict_detected",
        evaluations=[],
        rule_conflict=_CONFLICT,
    )


def test_as1_rule_conflict_gets_its_own_gap_marker_naming_the_competing_rules():
    """G1 HIGH-1 (BLOCKING-2) regression. `rule_conflict` is the typed object the engine
    DELIBERATELY preserves for reviewers (app.rules.integration._conflict_result): it names WHICH
    rules compete, over which outputs, and each one's effective window. It was dropped from the
    document and `_gap_markers` had no branch for it, so a genuine conflict surfaced only as a
    generic professional_review_required - the reviewer was told a human is needed without being
    told what to look at."""
    markers = _gap_markers(_HAS_PROVENANCE, _conflict_rule_eval())

    conflict_markers = [m for m in markers if m["subject"] == "rule_conflict"]
    assert len(conflict_markers) == 1, markers
    marker = conflict_markers[0]
    assert marker["kind"] == "data_conflict"
    assert marker["reason"] == _CONFLICT["note"]

    # The WHOLE typed object travels, so the reviewer sees exactly what competes.
    assert marker["detail"] == _CONFLICT
    assert [r["rule_id"] for r in marker["detail"]["competing_rules"]] == [
        "ZR-23-21-A",
        "ZR-23-21-B",
    ]
    # Deep copy, never an alias into the source document.
    assert marker["detail"] is not _CONFLICT

    # The generic markers still fire as well - the conflict marker ADDS information, it does not
    # replace the posture markers.
    kinds = {m["kind"] for m in markers}
    assert "professional_review_required" in kinds


def test_as1_assembled_document_carries_rule_conflict_and_its_gap():
    """The same defect at the document level: a conflict document must carry the typed object at
    the root AND name it as a gap."""
    rule_eval = _conflict_rule_eval()
    rule_eval["not_verified_disclaimer"] = "Not a Verified zoning determination."
    rule_eval["evaluated_input"] = {
        "bbl": BBL,
        "profile_contract_version": "1.0.0",
        "input_fingerprint": "fingerprint",
        "input_provenance": {},
    }

    document = assemble_evidence_document(_HAS_PROVENANCE, rule_eval, bbl=BBL)

    assert document["source_coverage"]["rule_conflict"] == _CONFLICT
    assert document["source_coverage"]["rule_conflict"] is not _CONFLICT
    assert any(gap["subject"] == "rule_conflict" for gap in document["gaps"])
    assert document["evidence_completeness"] == "professional_review_required"
    # Honest and never Verified, and serialisation-safe.
    assert document["overall_verification_status"] == "draft"
    evidence_module._assert_json_safe(document)
