"""B-03 site geometry threaded into the study read (journey wave 1 item 1, lane C).

Offline and deterministic. The route is driven through its INJECTED study-inputs
provider, now carrying an INJECTED geometry provider that serves the recorded
215-16 Northern benchmark SiteGeometry (the SAME offline replay the B-03 benchmark
test uses, ``tests/spatial/_northern_replay``). No network is touched.

Expected values come from the fixture geometry and the B-03 result constants
(``app.spatial.site_geometry``), never from literals restated here:

- with geometry, the study read's ``lot_type`` equals what the B-03 benchmark pins
  (``LOT_TYPE_CORNER`` == the replayed ``geometry.lot_type.kind``), and the
  per-street ``lot_frontage`` facts carry B-03's measured lengths;
- with NO geometry, threading is a no-op (the facts are byte-identical to the
  pre-geometry assembly) -- so every existing study-read test still passes;
- a refused geometry keeps ``lot_type`` unknown with B-03's refusal reason and
  leaves the PLUTO facts untouched;
- a geometry that gives a single lot depth replaces ``lot_depth`` and keeps the
  displaced PLUTO depth in the note;
- the full study document with the threaded facts still passes the study contract.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1.study_inputs import (
    GeometryProvider,
    assemble_study_inputs,
    pluto_study_inputs_provider,
)
from app.api.v1.study_read import get_rate_limiter, get_study_inputs_provider
from app.config import INTERNAL_STUDY_READ_ENABLED_ENV_VAR
from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl
from app.contracts.study_contracts import validate_study_document
from app.main import create_app
from app.spatial.site_geometry import (
    LABEL_TAX_MAP,
    derive_site_geometry_from_sources,
    refused_site_geometry,
)
from app.spatial.site_geometry.results import (
    LOT_TYPE_CORNER,
    STATUS_COMPLETE,
    STATUS_REFUSED,
)
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.spatial._northern_replay import (
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}


def _northern_fetcher(bbl: str, correlation_id: str):
    body = (FIXTURE_DIR / "pluto_64uk-42ks_bbl_4073340070.json").read_text(encoding="utf-8")
    return fetch_by_bbl(
        bbl,
        transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


def _benchmark_geometry():
    """The recorded 215-16 Northern SiteGeometry, replayed offline through the real
    B-03 connectors -- the SAME object the B-03 benchmark test asserts on."""
    return derive_site_geometry_from_sources(
        replay_lot_geometry(), [replay_dcm_page()], envelope=DCM_ENVELOPE,
        pluto_result=replay_pluto(),
    )


def _geometry_provider(geometry) -> GeometryProvider:
    def provide(canonical_bbl: str, correlation_id: str):
        return geometry

    return provide


def _provider(geometry_provider: GeometryProvider | None = None):
    return pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON,
        geometry_provider=geometry_provider,
    )


def _client(provider) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_study_inputs_provider] = lambda: provider
    return TestClient(app)


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, "1")


def _facts_by_key(body) -> dict:
    return {fact["key"]: fact for fact in body["site"]["facts"]}


def _frontage_facts(body) -> dict:
    return {
        fact["street"]: fact
        for fact in body["site"]["facts"]
        if fact["key"] == "lot_frontage"
    }


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


# ---------------------------------------------------------------------------
# (1) Geometry present -> lot_type equals the B-03 benchmark; frontages carried.
# ---------------------------------------------------------------------------
def test_lot_type_from_geometry_matches_b03_benchmark(monkeypatch) -> None:
    _enable(monkeypatch)
    geometry = _benchmark_geometry()
    # Cross-check the fixture against the B-03 benchmark constants (not restated
    # literals): the recorded Northern lot is a corner lot, tax-map labelled.
    assert geometry.status == STATUS_COMPLETE
    assert geometry.lot_type.kind == LOT_TYPE_CORNER
    assert geometry.lot_type.label == LABEL_TAX_MAP

    body = _client(_provider(_geometry_provider(geometry))).get(
        f"/api/v1/properties/{NORTHERN_BBL}/study"
    ).json()
    lot_type = _facts_by_key(body)["lot_type"]
    # The study read now carries B-03's geometric lot type -- exactly what the
    # benchmark pins, sourced from the tax-map outline.
    assert lot_type["value"] == geometry.lot_type.kind == LOT_TYPE_CORNER
    assert lot_type["measurement"] == {
        "rank": "approximate_tax_map", "label": LABEL_TAX_MAP,
    }
    assert lot_type["source"]["kind"] == "tax_map_computation"
    assert lot_type["blocks"] == []
    assert lot_type["contract_version"] == "1.0.0"

    # One lot_frontage fact per B-03 street, each carrying the measured length.
    fronts = _frontage_facts(body)
    assert {f.street_name for f in geometry.frontages} == set(fronts)
    for f in geometry.frontages:
        fact = fronts[f.street_name]
        assert fact["value"] == f.length.value
        assert fact["unit"] == "feet"
        assert fact["measurement"]["rank"] == "approximate_tax_map"
        assert fact["source"]["kind"] == "tax_map_computation"


# ---------------------------------------------------------------------------
# (2) Geometry None -> threading is a no-op (facts byte-identical to before).
# ---------------------------------------------------------------------------
def test_geometry_none_is_a_no_op(monkeypatch) -> None:
    _enable(monkeypatch)
    # The route default (no geometry provider) must produce the SAME facts the
    # pre-geometry assembly does. Assembled directly for a byte comparison.
    baseline = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    threaded_none = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON,
        site_geometry=None,
    )
    assert threaded_none.site_facts == baseline.site_facts
    # And a provider with no geometry provider still serves lot_type as UNKNOWN
    # (the pre-geometry behaviour), never a fabricated type.
    body = _client(_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    lot_type = _facts_by_key(body)["lot_type"]
    assert lot_type["value"] is None
    assert lot_type["measurement"]["rank"] == "unknown"
    assert all(fact["key"] != "lot_frontage" for fact in body["site"]["facts"])


# ---------------------------------------------------------------------------
# (3) Refused geometry -> lot_type stays unknown with B-03's reason; PLUTO intact.
# ---------------------------------------------------------------------------
def test_refused_geometry_keeps_lot_type_unknown_with_reason(monkeypatch) -> None:
    _enable(monkeypatch)
    reason = "The lot outline is EPSG:4326 display geometry and is never measured (test)."
    refused = refused_site_geometry(reason)
    assert refused.status == STATUS_REFUSED

    baseline = _facts_by_key(
        _client(_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    )
    body = _client(_provider(_geometry_provider(refused))).get(
        f"/api/v1/properties/{NORTHERN_BBL}/study"
    ).json()
    facts = _facts_by_key(body)
    lot_type = facts["lot_type"]
    assert lot_type["value"] is None
    assert lot_type["measurement"]["rank"] == "unknown"
    assert lot_type["blocks"]  # an unknown names what it blocks
    assert reason in lot_type["note"]
    # A refused geometry has no frontages, so none are added.
    assert all(fact["key"] != "lot_frontage" for fact in body["site"]["facts"])
    # The PLUTO-sourced facts are untouched by a refusal.
    assert facts["lot_depth"] == baseline["lot_depth"]
    assert facts["lot_area"] == baseline["lot_area"]


# ---------------------------------------------------------------------------
# lot_depth: given a single B-03 depth, it is carried and PLUTO is kept as a
# reference in the note (never dropped).
# ---------------------------------------------------------------------------
def test_lot_depth_given_is_carried_and_keeps_pluto_reference(monkeypatch) -> None:
    _enable(monkeypatch)
    geometry = _benchmark_geometry()
    # The benchmark corner lot gives NO single depth; inject one from its own
    # per-street mean (a real tax-map SourcedValue) to exercise the "given" branch.
    injected = geometry.frontage("Northern Boulevard").depth.mean
    assert injected.value is not None and injected.label == LABEL_TAX_MAP
    with_depth = replace(geometry, lot_depth=injected)

    baseline = _facts_by_key(
        _client(_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    )
    pluto_depth = baseline["lot_depth"]["value"]

    facts = _facts_by_key(
        _client(_provider(_geometry_provider(with_depth))).get(
            f"/api/v1/properties/{NORTHERN_BBL}/study"
        ).json()
    )
    lot_depth = facts["lot_depth"]
    assert lot_depth["value"] == injected.value
    assert lot_depth["unit"] == "feet"
    assert lot_depth["measurement"]["rank"] == "approximate_tax_map"
    assert lot_depth["source"]["kind"] == "tax_map_computation"
    # The displaced PLUTO depth is preserved in the note (provenance never dropped).
    assert "reference" in lot_depth["note"]
    assert str(pluto_depth) in lot_depth["note"]


# ---------------------------------------------------------------------------
# (4) The whole study document (with threaded facts) still passes the contract.
# ---------------------------------------------------------------------------
def test_full_study_with_geometry_passes_contract(monkeypatch) -> None:
    _enable(monkeypatch)
    geometry = _benchmark_geometry()
    body = _client(_provider(_geometry_provider(geometry))).get(
        f"/api/v1/properties/{NORTHERN_BBL}/study"
    ).json()
    # Composing the setup with a TEST-ONLY option yields a full study; validating
    # it exercises study.schema.json over the geometry-threaded site.facts too.
    study = {
        "contract_version": "1.0.0",
        "study_id": "test-fixture-synthetic-study-northern-geometry",
        "property": body["property"],
        "lots": body["lots"],
        "lot_selection": body["lot_selection"],
        "site": body["site"],
        "options": [_TEST_ONLY_OPTION],
        "selected_option_id": "opt-test",
        "revision": {"number": 1, "created_at": "2026-09-30T12:00:00Z", "parent": None},
        "origin": {"kind": "new", "export_id": None},
    }
    validate_study_document(study)  # raises on any defect
    # The threaded facts are present in the validated study.
    keys = {fact["key"] for fact in body["site"]["facts"]}
    assert "lot_frontage" in keys
    assert any(
        fact["key"] == "lot_type" and fact["value"] == LOT_TYPE_CORNER
        for fact in body["site"]["facts"]
    )
