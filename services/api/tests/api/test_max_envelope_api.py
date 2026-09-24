"""Acceptance pack for POST /api/v1/max-envelope (task M5-T064, D-082).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted max-envelope
engine; it ships UNMOUNTED (main.py is held by the live M5-T062 lane), so every test mounts the
router on a FRESH ``FastAPI()`` via ``TestClient`` (the accepted M5-T059 pattern) and one test
asserts the route is ABSENT from the real app. It is feature-flag gated OFF by default (reuses
``INTERNAL_RULE_EVAL_ENABLED``), mirroring the sibling internal routes.

- AS-5 (route discipline): 200 returns the envelope (dimensions + candidate + disclosure) with an
  X-Correlation-ID header; flag off -> the same generic 404 as an unmounted path; UNMOUNTED from
  the real app; typed + bounded refusals; the documented (status, state) matrix; no persistence.
- AS-3 (honest gaps in the response): the non-commensurable FAR / rear-yard gaps appear in the 200
  body; nothing is silently omitted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import max_envelope_api as mod
from app.api.v1.max_envelope_api import (
    MAX_BODY_BYTES,
    MAX_ENVELOPE_STATUS_STATE_MATRIX,
    router,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.rules.registry import RuleRegistry
from app.rules.snapshots import SnapshotStore

_B2 = Path(__file__).resolve().parents[1] / "rules" / "fixtures" / "proposal_checks"
_URL = "/api/v1/max-envelope"
_JSON_HEADERS = {"content-type": "application/json"}

#: A supported axis-aligned rectangular lot (80 x 100 = 8000 sq ft) at a real interior 2263 SW
#: corner, so the engine can fit + contain a candidate to it (not a fixed-anchor schematic).
_LOT_ANCHOR = (985000.0, 195000.0)
_LOT = {
    "area_sq_ft": 8000.0,
    "area_provenance": {"source_id": "synthetic"},
    "lot_line_segments": [
        {"id": "L-S", "start": [985000.0, 195000.0], "end": [985080.0, 195000.0]},
        {"id": "L-E", "start": [985080.0, 195000.0], "end": [985080.0, 195100.0]},
        {"id": "L-N", "start": [985080.0, 195100.0], "end": [985000.0, 195100.0]},
        {"id": "L-W", "start": [985000.0, 195100.0], "end": [985000.0, 195000.0]},
    ],
    "street_lines": [],
}
_FACTS = {"zoning_district": "R5", "street_width_class": "wide"}


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


def _body(**overrides) -> dict:
    body = {"lot": _LOT, "lot_rule_facts": _FACTS, "label": "env-A"}
    body.update(overrides)
    return body


def _pair(response) -> tuple[int, str | None]:
    try:
        state = response.json().get("state")
    except ValueError:  # pragma: no cover - all our responses are JSON
        state = None
    return response.status_code, state


@pytest.fixture
def fixture_registry() -> RuleRegistry:
    return RuleRegistry(_B2 / "rulesets", snapshots=SnapshotStore(_B2 / "snapshots")).load()


@pytest.fixture
def mounted_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(mounted_app, monkeypatch, fixture_registry):
    """A client over a fresh app with the flag ON and the SYNTHETIC fixture registry injected."""
    _enable(monkeypatch)
    monkeypatch.setattr(mod, "get_max_envelope_registry", lambda: fixture_registry)
    with TestClient(mounted_app, raise_server_exceptions=False) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# AS-5 / AS-3: the happy path.
# ---------------------------------------------------------------------------


def test_200_returns_the_envelope(client):
    resp = client.post(_URL, json=_body())
    assert resp.status_code == 200
    assert _pair(resp) in MAX_ENVELOPE_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")
    doc = resp.json()

    assert doc["massing_class"] == "rectangle_prism"
    assert doc["label"] == "env-A"
    assert doc["disclosure"] and "ESTIMATE" in doc["disclosure"]
    assert doc["summary"]["total"] == 4
    assert doc["correlation_id"] == resp.headers["X-Correlation-ID"]

    dims = {d["dimension_id"]: d for d in doc["dimensions"]}
    assert dims["max_lot_coverage_ratio"]["binding_value"] == pytest.approx(0.5)
    assert dims["max_lot_coverage_ratio"]["binding_rule_id"] == "pc-lot-coverage-demo"
    assert dims["max_building_height"]["binding_value"] == pytest.approx(60.0)

    # AS-3: honest gaps present in the response, nothing silently omitted.
    non_commensurable = "non_commensurable_with_massing"
    assert dims["max_residential_floor_area_sq_ft"]["gap_reason"] == non_commensurable
    assert dims["min_rear_yard_depth_ft"]["gap_reason"] == non_commensurable

    # A candidate the engine proved consistent; it is a proposed_massing block, not a scenario doc.
    assert doc["candidate"]["provenance"]["kind"] == "proposed"
    assert doc["candidate_consistency"]["saturating_checks"] == {
        "lot_coverage_ratio": "pass", "building_height": "pass",
    }

    # The candidate is FITTED to the actual lot geometry (anchored at the real lot, contained) -
    # not a fixed-anchor schematic. The placement is explicit in the response.
    placement = doc["candidate_placement"]
    assert placement["status"] == "fitted"
    assert placement["contained"] is True
    assert placement["footprint"]["anchor_x"] == _LOT_ANCHOR[0]
    assert placement["footprint"]["anchor_y"] == _LOT_ANCHOR[1]
    assert doc["candidate"]["outline"]["vertices"][0] == [_LOT_ANCHOR[0], _LOT_ANCHOR[1]]
    # AS-5 (no persistence / no emission): no scenario document keys.
    for scenario_key in ("scenario_id", "contract_version", "constraint_completeness"):
        assert scenario_key not in doc


# ---------------------------------------------------------------------------
# AS-5: flag off + UNMOUNTED.
# ---------------------------------------------------------------------------


def test_flag_off_is_a_generic_404(mounted_app, monkeypatch):
    """No flag -> the same generic 404 as an unmounted path: no body hint, no correlation id."""
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as client:
        resp = client.post(_URL, json=_body())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers
    assert _pair(resp) in MAX_ENVELOPE_STATUS_STATE_MATRIX


def test_route_is_unmounted_in_the_real_app():
    """The route ships UNMOUNTED: main.py is held by the live M5-T062 lane, so the path is absent
    from the real app's routes (and, being include_in_schema=False, from its OpenAPI)."""
    from app.main import app as real_app

    real_paths = {getattr(route, "path", None) for route in real_app.routes}
    assert _URL not in real_paths
    assert _URL not in real_app.openapi().get("paths", {})


# ---------------------------------------------------------------------------
# AS-5: bounded body, malformed body, typed refusals.
# ---------------------------------------------------------------------------


def test_413_oversized_body(client):
    resp = client.post(_URL, content=b"x" * (MAX_BODY_BYTES + 1), headers=_JSON_HEADERS)
    assert resp.status_code == 413
    assert _pair(resp) == (413, "payload_too_large")
    assert _pair(resp) in MAX_ENVELOPE_STATUS_STATE_MATRIX


@pytest.mark.parametrize("raw", [b"", b"   ", b"not json", b"[]", b'"a string"'])
def test_422_malformed_body(client, raw):
    resp = client.post(_URL, content=raw, headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert _pair(resp) == (422, "validation_error")


def test_422_nan_is_refused(client):
    resp = client.post(_URL, content=b'{"lot": {"area_sq_ft": NaN}}', headers=_JSON_HEADERS)
    assert resp.status_code == 422
    assert _pair(resp) == (422, "validation_error")


def test_422_bad_label_charset(client):
    resp = client.post(_URL, json=_body(label="bad\nlabel"))
    assert resp.status_code == 422
    assert resp.json()["field"] == "label"


def test_422_lot_not_an_object(client):
    resp = client.post(_URL, json=_body(lot="not-an-object"))
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot"


def test_422_bad_lot_rule_fact_type(client):
    resp = client.post(_URL, json=_body(lot_rule_facts={"zoning_district": 123}))
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.zoning_district"


def test_422_lot_rule_fact_outside_registry_domain(client):
    """A mapped fact outside the registry's OWN declared vocabulary refuses typed, before the
    engine runs (street_width_class is enum-constrained to wide/narrow by the fixture rule)."""
    resp = client.post(
        _URL, json=_body(lot_rule_facts={"zoning_district": "R5", "street_width_class": "bogus"})
    )
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_rule_facts.street_width_class"


def test_422_bad_lot_area_is_a_precondition_refusal(client):
    """A non-finite lot area is a typed precondition refusal from the engine (422), naming the
    field - never a 500 and never a fabricated envelope."""
    resp = client.post(_URL, json=_body(lot={**_LOT, "area_sq_ft": "huge"}))
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot.area_sq_ft"


def test_bad_charset_field_is_bounded(client):
    # A deep/odd field never rides unbounded; the refusal message stays short.
    resp = client.post(_URL, json=_body(label="x" * 5000))
    assert resp.status_code == 422
    assert len(resp.json()["message"]) < 1000


# ---------------------------------------------------------------------------
# AS-5: determinism through the route (same body -> same envelope, modulo correlation id).
# ---------------------------------------------------------------------------


def test_route_output_is_deterministic(client):
    a = client.post(_URL, json=_body()).json()
    b = client.post(_URL, json=_body()).json()
    a.pop("correlation_id")
    b.pop("correlation_id")
    assert a == b


def test_no_candidate_when_a_saturating_dimension_is_a_gap(client):
    """With no attested street width the height dimension is an honest gap, so no candidate is
    emitted - the route still returns 200 with every dimension enumerated."""
    resp = client.post(_URL, json=_body(lot_rule_facts={"zoning_district": "R5"}))
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["candidate"] is None
    assert doc["candidate_consistency"] is None
    assert doc["summary"]["total"] == 4
    assert len(doc["dimensions"]) == 4
    height = {d["dimension_id"]: d for d in doc["dimensions"]}["max_building_height"]
    assert height["gap_reason"] == "allowance_unresolved"


def test_no_candidate_when_lot_geometry_is_unsupported(client):
    """A lot with no supplied lot-line geometry cannot be fitted, so the route returns 200 with no
    candidate and an EXPLICIT typed placement gap - never a fixed-anchor schematic. The binding
    values still stand."""
    resp = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": []}))
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["candidate"] is None
    assert doc["candidate_consistency"] is None
    assert doc["candidate_placement"]["status"] == "lot_geometry_unsupported"
    dims = {d["dimension_id"]: d for d in doc["dimensions"]}
    assert dims["max_lot_coverage_ratio"]["binding_value"] == pytest.approx(0.5)
    assert dims["max_building_height"]["binding_value"] == pytest.approx(60.0)


# ---------------------------------------------------------------------------
# DB-046 (M5-T068): the (500, internal_error) matrix row exercised LIVE. A generator-checker
# inconsistency and a genuine internal defect both map to the bounded generic 500 - the fixed
# body, NO exception detail/traceback leaked, X-Correlation-ID present. TEST-ONLY.
# ---------------------------------------------------------------------------


class _StubCheck:
    def __init__(self, check_id, outcome, provided_value=0.6, required_value=0.5) -> None:
        self.check_id = check_id
        self.outcome = outcome
        self.provided_value = provided_value
        self.required_value = required_value


class _StubReport:
    def __init__(self, results) -> None:
        self.results = results

    def as_dict(self) -> dict:
        return {"summary": {}}


def test_500_generator_checker_inconsistency_is_a_bounded_generic_error(client, monkeypatch):
    """DB-046(d) route side: a generator-checker inconsistency (the engine's candidate FAILs its
    own checker -> MaxEnvelopeError field 'candidate.max_lot_coverage_ratio') maps to the
    documented bounded generic 500 - never a 422, and never leaking the internal invariant
    field/detail.

    This does NOT merely observe *some* 500. A spy wraps the route's engine entry
    (``mod.derive_max_envelope``): it runs the REAL engine with its imported ``check_proposal``
    patched to FAIL the saturating lot-coverage check, OBSERVES that the engine raised exactly
    ``MaxEnvelopeError`` with ``field == 'candidate.max_lot_coverage_ratio'``, and RE-RAISES that
    same error unchanged so the route's own MaxEnvelopeError handler (the ``candidate.*`` -> 500
    branch) processes it. An unrelated generic exception (or a stub that only incidentally 500s
    for the wrong reason, or a checker patch that silently missed and let the candidate pass)
    could never satisfy the type+field observation, and a mutant routing ``candidate.*`` to 422
    would leave ``resp.status_code`` != 500 - either way this test goes red."""
    import app.scenario.max_envelope as engine
    from app.rules.proposal_checks import CheckOutcome
    from app.scenario.max_envelope import MaxEnvelopeError

    def _failing(candidate, lot, facts, *, scenario_label, registry):
        return _StubReport(
            [
                _StubCheck("lot_coverage_ratio", CheckOutcome.FAIL),
                _StubCheck("building_height", CheckOutcome.PASS),
            ]
        )

    monkeypatch.setattr(engine, "check_proposal", _failing)

    # Spy over the route's engine entry: run the REAL engine, observe the specific fail-closed
    # invariant error it raises, then re-raise it unchanged for the route to handle.
    real_derive = engine.derive_max_envelope
    observed: dict[str, object] = {}

    def _observing_derive(*args, **kwargs):
        try:
            return real_derive(*args, **kwargs)
        except MaxEnvelopeError as exc:
            observed["type"] = type(exc).__name__
            observed["field"] = exc.field
            raise  # re-raise for route handling (the candidate.* -> 500 branch)

    monkeypatch.setattr(mod, "derive_max_envelope", _observing_derive)

    resp = client.post(_URL, json=_body())

    # The REAL engine raised EXACTLY the fail-closed generator-checker invariant - not an
    # incidental generic exception; this is what pins the intended candidate.* -> 500 branch.
    assert observed == {
        "type": "MaxEnvelopeError",
        "field": "candidate.max_lot_coverage_ratio",
    }

    assert resp.status_code == 500
    assert _pair(resp) == (500, "internal_error")
    assert _pair(resp) in MAX_ENVELOPE_STATUS_STATE_MATRIX
    body = resp.json()
    assert body["message"] == "unexpected internal error; see server logs by correlation id"
    assert "candidate" not in resp.text  # the internal invariant field never leaks to the client
    assert resp.headers.get("X-Correlation-ID")
    assert body["correlation_id"] == resp.headers["X-Correlation-ID"]


def test_500_registry_unavailable_is_a_bounded_generic_error(mounted_app, monkeypatch):
    """DB-046(e): a genuine internal defect (registry resolution raising) produces the documented
    (500, internal_error) LIVE - the fixed generic body, NO exception message/type/traceback
    leaked, and the X-Correlation-ID header present. Previously this matrix row was asserted only
    by frozenset membership, never by a live response."""
    _enable(monkeypatch)
    secret = "boom-secret-detail-should-never-leak"  # secretscan:allow fake leak-absence sentinel

    def _raise():
        raise RuntimeError(secret)

    monkeypatch.setattr(mod, "get_max_envelope_registry", _raise)
    with TestClient(mounted_app, raise_server_exceptions=False) as internal_client:
        resp = internal_client.post(_URL, json=_body())
    assert resp.status_code == 500
    assert _pair(resp) == (500, "internal_error")
    assert _pair(resp) in MAX_ENVELOPE_STATUS_STATE_MATRIX
    body = resp.json()
    assert body["message"] == "unexpected internal error; see server logs by correlation id"
    assert secret not in resp.text  # no exception message leaked
    assert "RuntimeError" not in resp.text  # no exception type / traceback leaked
    assert resp.headers.get("X-Correlation-ID")
    assert body["correlation_id"] == resp.headers["X-Correlation-ID"]


# ---------------------------------------------------------------------------
# M5-T076 / DB-050(a): server-side lot-geometry derivation makes the fitted-candidate path
# reachable for a geometry-free request carrying a BBL. Fully OFFLINE - the canonical EPSG:2263
# exterior ring comes from the REAL connector analyzer over an inline esri rectangle, and a
# fixture-backed provider is injected via mod.get_lot_geometry_provider (no network).
# ---------------------------------------------------------------------------

# The same rectangular lot as _LOT, expressed as an esri-clockwise exterior ring: bounding box
# 80 x 100 = 8000 sq ft anchored at _LOT_ANCHOR, so the engine fits + contains a candidate.
_RECT_ESRI = {
    "rings": [
        [
            [985000, 195000],
            [985000, 195100],
            [985080, 195100],
            [985080, 195000],
            [985000, 195000],
        ]
    ]
}


def _rect_result(*, outcome: str | None = None, esri: object | None = _RECT_ESRI,
                 review_required: bool = False, bbl: str = "1008350041",
                 version: str = "26v1"):
    """A LotGeometryResult for one BBL from an esri geometry (offline) - the inline SYNTHETIC
    rectangle by default, or a RECORDED fixture ring via :func:`_recorded_result`."""
    from app.connectors.mappluto_geometry_arcgis import (
        CRS_STAMP,
        OUTCOME_SINGLE,
        LotGeometryResult,
        analyze_lot_geometry,
    )

    assessment = analyze_lot_geometry(esri, crs=dict(CRS_STAMP)) if esri is not None else None
    return LotGeometryResult(
        status="ok",
        outcome=outcome or OUTCOME_SINGLE,
        review_required=review_required,
        requested_bbl=bbl,
        borough=1, block=835, lot=41,
        condo={"classification": "standard_lot", "condo_no": None, "note": None},
        identifier_conflicts=[],
        attributes={"BBL": int(bbl), "Version": version},
        features=[],
        geometry=assessment,
        area_sq_ft=(assessment.area_sq_ft if assessment is not None else None),
        shape_area_attribute_sq_ft=None,
        exceeded_transfer_limit=False,
        correlation_id="c-fixture",
        request_url="https://example/query",
        metadata_request_url="https://example/meta",
        retrieved_at="2026-07-20T00:00:00Z",
        crs=dict(CRS_STAMP),
        source_data_last_edited_ms=None,
        source_data_last_edited="2026-06-01T00:00:00Z",
        raw_digest="sha256:raw",
        metadata_raw_digest="sha256:meta",
        normalized_digest="sha256:features",
        digest_canonicalization="spec",
        shapely_version="2.0.7",
        geos_version="3.11.4",
    )


#: The accepted M2-T009 RECORDED fixture pack (live captures of the official keyless ArcGIS
#: service). These carry the real City geometry classes the mounted route will meet first.
_MPG_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "mappluto_geometry"


def _recorded_feature(fixture_name: str) -> dict:
    """The single feature of a RECORDED fixture, asserted to still be a raw live capture."""
    fixture = json.loads((_MPG_FIXTURES / fixture_name).read_text(encoding="utf-8"))
    assert fixture["classification"] == "raw"
    assert fixture["capture_method"].startswith("live ")
    features = json.loads(fixture["response_body_raw"])["features"]
    assert len(features) == 1
    return features[0]


def _recorded_result(fixture_name: str):
    """A LotGeometryResult whose geometry, BBL and dataset version come from a RECORDED fixture."""
    feature = _recorded_feature(fixture_name)
    attributes = feature["attributes"]
    return _rect_result(
        esri=feature["geometry"],
        bbl=str(attributes["BBL"]),
        version=attributes["Version"],
    )


def _inject_provider(monkeypatch, provider) -> None:
    monkeypatch.setattr(mod, "get_lot_geometry_provider", lambda: provider)


def _inject_provider_recording_resolution(monkeypatch, provider, resolutions: list[str]) -> None:
    """Inject a provider through a getter that RECORDS each resolution, so a test can prove the
    provider was never even resolved (not merely never called)."""

    def _get():
        resolutions.append("resolved")
        return provider

    monkeypatch.setattr(mod, "get_lot_geometry_provider", _get)


def _recording_provider(calls: list[str]):
    """A provider that records each BBL it is asked for (to prove non-invocation)."""

    def _p(canonical_bbl: str):
        calls.append(canonical_bbl)
        return _rect_result()

    return _p


def test_derived_path_yields_fitted_candidate(client, monkeypatch):
    """AS-2: a geometry-free request with a resolvable BBL now yields a FITTED contained candidate
    from the REAL engine, proven through the route, with the derived provenance quintuple on the
    response.

    FIXTURE-CONDITIONAL, stated plainly: the lot geometry here is the SYNTHETIC axis-aligned
    rectangle ``_RECT_ESRI``, because that is the only class the accepted engine can currently fit
    (``_lot_rectangle`` requires an axis-aligned ring whose bbox area matches the recorded area).
    A RECORDED City lot of the same BBL does NOT fit - see
    ``test_recorded_single_lot_derives_but_is_honestly_unfittable``, which asserts that outcome
    rather than hiding it. So this proves the derivation-to-fitted PATH works, not that real NYC
    lots generally fit."""
    _inject_provider(monkeypatch, lambda canonical_bbl: _rect_result())
    resp = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": [], "bbl": "1008350041"}))
    assert resp.status_code == 200
    doc = resp.json()

    placement = doc["candidate_placement"]
    assert placement["status"] == "fitted"
    assert placement["contained"] is True
    assert placement["footprint"]["anchor_x"] == _LOT_ANCHOR[0]
    assert placement["footprint"]["anchor_y"] == _LOT_ANCHOR[1]
    assert doc["candidate"] is not None
    assert doc["candidate"]["provenance"]["kind"] == "proposed"
    assert doc["candidate_consistency"]["saturating_checks"] == {
        "lot_coverage_ratio": "pass", "building_height": "pass",
    }

    derived = doc["derived_lot_geometry"]
    assert derived["outcome"] == "derived"
    assert derived["provenance"]["source_id"] == "nyc-dcp-mappluto-arcgis"
    assert derived["provenance"]["bbl"] == "1008350041"
    assert derived["provenance"]["dataset_version"] == "26v1"
    assert derived["provenance"]["geometry_digest"].startswith("sha256:")


def test_with_segments_is_byte_identical_and_never_derives(client, monkeypatch):
    """AS-3 (byte-identity): a request that carries client segments is served byte-identically to
    today - the derivation provider is NEVER RESOLVED and never called, and no derived_lot_geometry
    block appears. Both claims are asserted: the getter itself is a spy (so a mutant that resolved
    the provider and then discarded it still reddens this), and the provider records invocations."""
    calls: list[str] = []
    resolutions: list[str] = []
    _inject_provider_recording_resolution(monkeypatch, _recording_provider(calls), resolutions)

    # _body() carries the full _LOT rectangle segments AND a bbl - segments-present must win.
    resp = client.post(_URL, json=_body(lot={**_LOT, "bbl": "1008350041"}))
    assert resp.status_code == 200
    doc = resp.json()
    assert resolutions == []  # the provider is never even resolved
    assert calls == []  # no derivation call
    assert "derived_lot_geometry" not in doc
    # today's behavior: the supplied rectangle fits a candidate.
    assert doc["candidate_placement"]["status"] == "fitted"


# The connector's outcome constants are plain string values ("no_feature" / "multiple_features"),
# so the fixtures use the literals directly rather than importing them mid-file (ruff E402).
@pytest.mark.parametrize(
    "result_kwargs, expected_outcome",
    [
        ({"outcome": "no_feature", "esri": None}, "no_feature"),
        ({"outcome": "multiple_features", "esri": None}, "multiple_features"),
        ({"esri": {"rings": []}}, "invalid_geometry"),
    ],
)
def test_derivation_failure_keeps_honest_gap_with_reason(
    client, monkeypatch, result_kwargs, expected_outcome
):
    """AS-3 (fail-closed): each derivation failure class leaves the engine with empty segments, so
    it returns the honest lot_geometry_unsupported gap, and the derivation reason is carried into
    the placement detail - NEVER a fabricated candidate. A mutant that injected a fabricated
    rectangle on failure would flip the candidate to non-None and redden this test."""
    _inject_provider(monkeypatch, lambda _bbl: _rect_result(**result_kwargs))
    resp = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": [], "bbl": "1008350041"}))
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["candidate"] is None
    placement = doc["candidate_placement"]
    assert placement["status"] == "lot_geometry_unsupported"
    assert "server-side lot-geometry derivation" in placement["detail"]
    assert expected_outcome in placement["detail"]
    assert doc["derived_lot_geometry"]["outcome"] == expected_outcome
    assert doc["derived_lot_geometry"]["provenance"] is None


def test_connector_fault_keeps_honest_gap(client, monkeypatch):
    """AS-3 (fail-closed): a connector fault (an upstream/transport error) keeps the honest gap and
    surfaces the connector_fault reason - never a fabricated rectangle."""
    from app.connectors.mappluto_geometry_arcgis import MalformedResponseError

    def _faulting(canonical_bbl: str):
        raise MalformedResponseError("boom", correlation_id="c")

    _inject_provider(monkeypatch, _faulting)
    resp = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": [], "bbl": "1008350041"}))
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["candidate"] is None
    placement = doc["candidate_placement"]
    assert placement["status"] == "lot_geometry_unsupported"
    assert doc["derived_lot_geometry"]["outcome"] == "connector_fault"
    # DB-051(c): the failure reason reaches placement.detail (not only the derived block).
    assert "server-side lot-geometry derivation" in placement["detail"]
    assert "connector_fault" in placement["detail"]
    assert "could not be reached" in placement["detail"]


def test_unresolvable_bbl_keeps_honest_gap_without_calling_provider(client, monkeypatch):
    """AS-3 (fail-closed): a syntactically-present but unresolvable BBL never reaches the provider
    and keeps the honest gap with the bbl_unresolvable reason."""
    def _p(canonical_bbl: str):  # pragma: no cover - asserted never invoked
        raise AssertionError("provider must not be called for an unresolvable BBL")

    _inject_provider(monkeypatch, _p)
    resp = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": [], "bbl": "not-a-bbl"}))
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["candidate"] is None
    placement = doc["candidate_placement"]
    assert placement["status"] == "lot_geometry_unsupported"
    assert doc["derived_lot_geometry"]["outcome"] == "bbl_unresolvable"
    # DB-051(c): the honest bbl_unresolvable reason reaches placement.detail.
    assert "server-side lot-geometry derivation" in placement["detail"]
    assert "bbl_unresolvable" in placement["detail"]
    assert "not a resolvable canonical BBL" in placement["detail"]


def test_no_bbl_and_no_segments_does_not_derive(client, monkeypatch):
    """AS-3: a geometry-free request WITHOUT a BBL behaves exactly like today - no derivation is
    attempted and no derived_lot_geometry block appears (byte-identical to the pre-T076 gap)."""
    calls: list[str] = []
    _inject_provider(monkeypatch, _recording_provider(calls))
    resp = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": []}))
    assert resp.status_code == 200
    doc = resp.json()
    assert calls == []
    assert "derived_lot_geometry" not in doc
    assert doc["candidate_placement"]["status"] == "lot_geometry_unsupported"


@pytest.mark.parametrize("non_scalar_bbl", [{"x": 1}, ["1008350041"]])
def test_non_scalar_bbl_does_not_derive_and_never_calls_the_provider(
    client, monkeypatch, non_scalar_bbl
):
    """AS-4 / DB-051(e): a non-scalar ``lot.bbl`` (an object or a list) is not a usable BBL, so
    ``_should_derive_lot_geometry`` returns False. The request then gets today's honest
    ``lot_geometry_unsupported`` gap - a 200 with NO ``derived_lot_geometry`` block at all (no typed
    refusal, no derivation attempt) - and the provider is never even RESOLVED, proven by the spy.
    This pins the documented fail-closed behavior; ``_build_lot_context`` never reads the bbl."""
    calls: list[str] = []
    resolutions: list[str] = []
    _inject_provider_recording_resolution(monkeypatch, _recording_provider(calls), resolutions)
    resp = client.post(
        _URL, json=_body(lot={**_LOT, "lot_line_segments": [], "bbl": non_scalar_bbl})
    )
    assert resp.status_code == 200
    doc = resp.json()
    assert resolutions == [] and calls == []  # provider never resolved or called
    assert "derived_lot_geometry" not in doc
    assert doc["candidate_placement"]["status"] == "lot_geometry_unsupported"


# ---------------------------------------------------------------------------
# G3 rework: the derivation hop obeys the documented status/state matrix (F1), a malformed
# lot_line_segments is never silently replaced (F2), and the RECORDED City fixtures are exercised
# end to end (F3/F4).
# ---------------------------------------------------------------------------


def test_500_when_the_lot_geometry_provider_raises_unexpectedly(client, monkeypatch):
    """F1: the derivation hop is the route's only external call, and an UNEXPECTED provider defect
    (anything the derivation does not type - here a ValueError) must land on the documented
    (500, internal_error) pair with an X-Correlation-ID, exactly like the registry and engine
    guards. Without the guard this escapes to Starlette's bare 500 - plain-text body, no state, no
    correlation id - so this test is a direct red/green witness for the fix."""
    leak_probe = "provider-defect-detail-should-never-leak"  # secretscan:allow leak-absence probe

    def _raising(canonical_bbl: str):
        raise ValueError(leak_probe)

    _inject_provider(monkeypatch, _raising)
    resp = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": [], "bbl": "1008350041"}))

    assert resp.status_code == 500
    assert _pair(resp) == (500, "internal_error")
    assert _pair(resp) in MAX_ENVELOPE_STATUS_STATE_MATRIX
    body = resp.json()
    assert body["message"] == "unexpected internal error; see server logs by correlation id"
    assert leak_probe not in resp.text  # no exception message leaked
    assert "ValueError" not in resp.text  # no exception type / traceback leaked
    assert resp.headers.get("X-Correlation-ID")
    assert body["correlation_id"] == resp.headers["X-Correlation-ID"]


@pytest.mark.parametrize(
    "malformed",
    # Truthy set (the pre-T077 net) PLUS the FALSY set (DB-051(a) / G4-F1): the idiomatic weakening
    # `if lot.get("lot_line_segments"): return False` ships GREEN over every truthy value but lets
    # the five falsy malformed values fall through to derivation, silently replacing a documented
    # 422 with a 200. Only the falsy values discriminate that mutant - so both sets are pinned.
    ["abc", 42, {"id": "L-S"}, True, 0, "", {}, False, 0.0],
)
def test_malformed_segments_refuse_identically_with_and_without_a_bbl(
    client, monkeypatch, malformed
):
    """F2 / DB-051(a): a malformed ``lot.lot_line_segments`` is a documented typed 422 today. Adding
    a BBL must NOT turn it into a 200 by substituting derived geometry - the caller's malformed
    field (truthy OR falsy) stays on the typed-refusal path, byte-for-byte the same refusal as
    without the BBL, and the provider is never resolved or called."""
    calls: list[str] = []
    resolutions: list[str] = []
    _inject_provider_recording_resolution(monkeypatch, _recording_provider(calls), resolutions)

    without_bbl = client.post(_URL, json=_body(lot={**_LOT, "lot_line_segments": malformed}))
    with_bbl = client.post(
        _URL, json=_body(lot={**_LOT, "lot_line_segments": malformed, "bbl": "1008350041"})
    )

    assert _pair(without_bbl) == (422, "validation_error")
    assert _pair(with_bbl) == (422, "validation_error")
    without_body = without_bbl.json()
    with_body = with_bbl.json()
    assert with_body["field"] == without_body["field"] == "lot.lot_line_segments"
    # Identical refusals modulo the per-request correlation id.
    without_body.pop("correlation_id")
    with_body.pop("correlation_id")
    assert with_body == without_body
    assert resolutions == [] and calls == []


def test_absent_or_empty_segments_with_a_bbl_still_derive(client, monkeypatch):
    """AS-1 / DB-051(b): the two shapes that mean "no geometry supplied" and INVITE server-side
    derivation - the field ABSENT or an EMPTY LIST - both derive and fit. ``null`` is deliberately
    NOT here: it refuses (see test_null_segments_refuse_in_every_state_with_no_provider_call)."""
    _inject_provider(monkeypatch, lambda _bbl: _rect_result())
    base = {k: v for k, v in _LOT.items() if k != "lot_line_segments"}

    for lot in (
        {**base, "bbl": "1008350041"},                            # absent
        {**base, "lot_line_segments": [], "bbl": "1008350041"},   # empty list
    ):
        resp = client.post(_URL, json=_body(lot=lot))
        assert resp.status_code == 200, lot
        doc = resp.json()
        assert doc["derived_lot_geometry"]["outcome"] == "derived", lot
        assert doc["candidate_placement"]["status"] == "fitted", lot


def test_null_segments_refuse_in_every_state_with_no_provider_call(client, monkeypatch):
    """AS-1 / DB-051(b) ORCHESTRATOR RULING: the JSON ``null`` spelling of ``lot_line_segments`` is
    NOT an invitation to derive. Unlike an absent field or an empty list, ``null`` stays on
    ``_build_lot_context``'s typed 422 (``lot.lot_line_segments must be an array``) in EVERY
    BBL/provider state - no BBL, BBL + a passing provider, BBL + a failing provider - each with NO
    provider call. One rule, one refusal class: the same 422 ``null`` already receives without a
    BBL. MUTATION (DB-051(b)): re-admitting ``None`` to the derivable set reddens this test."""
    base = {k: v for k, v in _LOT.items() if k != "lot_line_segments"}

    def _recording_faulting(calls: list[str]):
        from app.connectors.mappluto_geometry_arcgis import MalformedResponseError

        def _p(canonical_bbl: str):
            calls.append(canonical_bbl)
            raise MalformedResponseError("boom", correlation_id="c")

        return _p

    states = [
        ("no BBL", {**base, "lot_line_segments": None}, _recording_provider),
        ("BBL + passing provider",
         {**base, "lot_line_segments": None, "bbl": "1008350041"}, _recording_provider),
        ("BBL + failing provider",
         {**base, "lot_line_segments": None, "bbl": "1008350041"}, _recording_faulting),
    ]
    for label, lot, make_provider in states:
        calls: list[str] = []
        resolutions: list[str] = []
        _inject_provider_recording_resolution(monkeypatch, make_provider(calls), resolutions)
        resp = client.post(_URL, json=_body(lot=lot))
        assert _pair(resp) == (422, "validation_error"), label
        assert resp.json()["field"] == "lot.lot_line_segments", label
        assert resolutions == [] and calls == [], label  # provider never resolved or called
        assert "derived_lot_geometry" not in resp.json(), label


def test_recorded_single_lot_derives_but_is_honestly_unfittable(client, monkeypatch):
    """F3, on the RECORDED MPG02 capture (Empire State Building, BBL 1008350041) - the packet's own
    named "fitted-candidate-reachable" fixture. Run through the real route, the real connector
    analyzer and the real engine, the truth is: the derivation SUCCEEDS (the City's 6-vertex
    exterior ring becomes 6 authoritative segments with recorded provenance), and the ENGINE then
    honestly refuses to place a candidate, because that real ring is not axis-aligned - the
    accepted engine's only supported class.

    The assertion is NAMED, not "some unsupported status": the placement detail must be the
    engine's OWN verbatim reason, with NO derivation reason appended (there was no derivation
    failure to report). This is the dominant real-world outcome for NYC lots - the street grid is
    rotated in EPSG:2263 - and it is asserted here rather than left uncovered."""
    _inject_provider(
        monkeypatch, lambda _bbl: _recorded_result("MPG02_lot_single_1008350041.json")
    )
    recorded_lot = {
        # The recorded Shape__Area attribute of the same capture (sq ft), not a synthetic number.
        "area_sq_ft": 97113.6875,
        "area_provenance": {"source_id": "nyc-dcp-mappluto-arcgis"},
        "lot_line_segments": [],
        "street_lines": [],
        "bbl": "1008350041",
    }
    resp = client.post(_URL, json=_body(lot=recorded_lot))
    assert resp.status_code == 200
    doc = resp.json()

    derived = doc["derived_lot_geometry"]
    assert derived["outcome"] == "derived"  # the official DATA was fine
    assert derived["provenance"]["source_id"] == "nyc-dcp-mappluto-arcgis"
    assert derived["provenance"]["bbl"] == "1008350041"
    assert derived["provenance"]["dataset_version"] == "26v1"

    placement = doc["candidate_placement"]
    assert placement["status"] == "lot_geometry_unsupported"
    assert placement["detail"] == (
        "the lot-line geometry is not an axis-aligned rectangle (a diagonal or zero-length "
        "segment); unsupported for candidate placement in slice 1"
    )
    assert "server-side lot-geometry derivation" not in placement["detail"]
    assert doc["candidate"] is None
    assert doc["candidate_consistency"] is None
    # The envelope's binding values still stand - only the PLACEMENT is gapped.
    dims = {d["dimension_id"]: d for d in doc["dimensions"]}
    assert dims["max_building_height"]["binding_value"] == pytest.approx(60.0)


def test_recorded_multipolygon_is_reported_over_cap_not_invalid(client, monkeypatch):
    """F3/F4, on the RECORDED MPG07 capture (Queens, shoreline-clipped true multipolygon): its
    3130-vertex exterior rings exceed the route's own ROUTE_MAX_LOT_LINE_SEGMENTS (800). The
    response must classify that as ``geometry_over_cap`` and say our cap is the binding constraint
    - NOT ``invalid_geometry``, which would tell a caller the City's valid data is bad."""
    _inject_provider(
        monkeypatch, lambda _bbl: _recorded_result("MPG07_lot_multipolygon_4142600001.json")
    )
    recorded_lot = {
        "area_sq_ft": 174572369.0070343,  # the recorded Shape__Area attribute (sq ft)
        "area_provenance": {"source_id": "nyc-dcp-mappluto-arcgis"},
        "lot_line_segments": [],
        "street_lines": [],
        "bbl": "4142600001",
    }
    resp = client.post(_URL, json=_body(lot=recorded_lot))
    assert resp.status_code == 200
    doc = resp.json()

    derived = doc["derived_lot_geometry"]
    assert derived["outcome"] == "geometry_over_cap"
    assert derived["outcome"] != "invalid_geometry"
    assert derived["provenance"] is None
    assert "is valid" in derived["detail"] and "not at fault" in derived["detail"]
    assert "800" in derived["detail"]  # the route's own cap, named

    placement = doc["candidate_placement"]
    assert placement["status"] == "lot_geometry_unsupported"
    assert "geometry_over_cap" in placement["detail"]
    assert "our own cap is the binding constraint" in placement["detail"]
    assert doc["candidate"] is None
