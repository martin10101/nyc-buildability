"""Live B-03 geometry provider for the study read (lane C, D-090-R124).

Offline and deterministic. Proves the LIVE binding of the study read's injected
geometry seam to Lane B's accepted envelope-intersects street composition
(``street_data_for_lot``, PR #403), behind the existing ``LIVE_SPATIAL_PROVIDER_ENABLED``
flag (default off). Every fetch is driven by the recorded 215-16 Northern pack
(``tests/spatial/_northern_replay`` + the live-streets recorded fetch) through the real
B-03 connectors; no network is touched.

Expected values come from the replay helpers and the B-03 result constants, never
restated literals:

- with the recorded fakes the provider yields the SAME SiteGeometry the recorded pack
  derives (corner lot, 215 Place / Northern Boulevard frontages), and the study read then
  shows ``lot_type`` corner and the two frontage facts;
- with the flag OFF the live default binds no geometry provider (None), and a
  ``geometry_provider=None`` document is byte-identical to the pre-geometry assembly;
  with the flag ON the live geometry provider is bound and geometry is threaded;
- a raising/failing fetch (a typed connector error) yields None -> the facts stay unknown
  and the route returns 200, never a 503/500;
- a non-EPSG:2263 geometry page yields None (the accepted parser refuses it);
- an outline the adapter refuses yields None.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.api.v1.properties as properties
import app.api.v1.study_inputs as study_inputs
import app.api.v1.study_live_geometry as study_live_geometry
from app.api.v1.study_inputs import (
    assemble_study_inputs,
    default_study_inputs_provider,
    pluto_study_inputs_provider,
)
from app.api.v1.study_live_geometry import live_geometry_provider
from app.api.v1.study_read import get_rate_limiter, get_study_inputs_provider
from app.config import INTERNAL_STUDY_READ_ENABLED_ENV_VAR
from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.mappluto_geometry_arcgis import UpstreamError
from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl
from app.connectors.pluto_version_probe import fetch_published_version
from app.main import create_app
from app.spatial.live_provider import LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_for_lot,
)
from app.spatial.site_geometry.results import FRONTAGE_CONFIRMED, LOT_TYPE_CORNER
from tests.spatial._northern_replay import (
    DCM_FILE,
    MANIFEST,
    PACK,
    recorded_dcm_envelope_page,
    replay_lot_geometry,
)
from tests.spatial.test_site_geometry_benchmark_215_16_northern import NORTHERN, PLACE

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
PLUTO_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}
_META_FILE = "dcm_layer_metadata.json"
_CID = "live-geom-test"


# --------------------------------------------------------------------------- offline seams


def _northern_fetcher(bbl: str, correlation_id: str):
    body = (FIXTURE_DIR / "pluto_64uk-42ks_bbl_4073340070.json").read_text(encoding="utf-8")
    return fetch_by_bbl(
        bbl,
        transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


def _f09_probe(correlation_id: str):
    """The recorded F09 published-version probe (26v1) over a fake transport, so the
    live default's version probe (B-4) stays fully offline."""
    fixture = json.loads((PLUTO_FIXTURE_DIR / "F09_version_select.json").read_text("utf-8"))
    response = TransportResponse(fixture["http_status"], fixture["response_body_raw"])
    return fetch_published_version(
        transport=lambda url, headers, timeout: response,
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


def _fake_lot(canonical_bbl: str, correlation_id: str):
    """The recorded MapPLUTO lot geometry, replayed through the real connector."""
    return replay_lot_geometry()


def _pack_transport(name: str) -> DcmTransport:
    entry = MANIFEST[name]
    body = (PACK / name).read_bytes().decode("utf-8")
    return DcmTransport(url=entry["url"], status=200, body=body,
                        retrieved_at=entry["retrieved_at"])


def _recorded_streets(url: str, correlation_id: str) -> DcmTransport:
    """Serve the recorded DCM metadata + envelope-page bytes by URL -- the accepted paged
    fetch calls this exactly as it would ``default_fetch``, fully offline."""
    for name in (_META_FILE, DCM_FILE):
        transport = _pack_transport(name)
        if url == transport.url:
            return transport
    raise AssertionError(f"the code fetched an unexpected URL: {url}")


def _reference_geometry():
    """The B-03 SiteGeometry the recorded pack yields with city_records=None -- the SAME
    object the live geometry provider builds (no PLUTO facts are threaded here)."""
    lot, refusal = lot_outline_from_mappluto(replay_lot_geometry())
    assert lot is not None, refusal
    streets = street_data_for_lot(lot, correlation_id=_CID, fetch=_recorded_streets)
    return derive_site_geometry(lot, streets, None)


def _client(provider) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_study_inputs_provider] = lambda: provider
    return TestClient(app)


def _facts_by_key(facts) -> dict:
    return {fact["key"]: fact for fact in facts}


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


# ---------------------------------------------------------------------------
# (a) The provider composes the accepted pieces into the recorded SiteGeometry.
# ---------------------------------------------------------------------------
def test_provider_yields_corner_and_two_frontages_from_recorded_pack() -> None:
    provider = live_geometry_provider(fetch_lot=_fake_lot, fetch_streets=_recorded_streets)
    geometry = provider(NORTHERN_BBL, _CID)
    reference = _reference_geometry()
    # Byte-identical to the accepted composition path (lot type, frontages, depth,
    # area, provenance), and a corner lot with both named frontages confirmed.
    assert geometry == reference
    assert geometry.lot_type.kind == reference.lot_type.kind == LOT_TYPE_CORNER
    for street in (PLACE, NORTHERN):
        got, want = geometry.frontage(street), reference.frontage(street)
        assert got is not None
        assert got.status == want.status == FRONTAGE_CONFIRMED
        assert got.length.value == want.length.value


# ---------------------------------------------------------------------------
# (a) The study read shows the live geometry's lot type and frontages.
# ---------------------------------------------------------------------------
def test_study_read_shows_live_geometry_lot_type_and_frontages(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, "1")
    provider = live_geometry_provider(fetch_lot=_fake_lot, fetch_streets=_recorded_streets)
    inputs_provider = pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON, geometry_provider=provider,
    )
    body = _client(inputs_provider).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    geometry = _reference_geometry()
    lot_type = _facts_by_key(body["site"]["facts"])["lot_type"]
    assert lot_type["value"] == geometry.lot_type.kind == LOT_TYPE_CORNER
    assert lot_type["measurement"]["rank"] == "approximate_tax_map"
    assert lot_type["source"]["kind"] == "tax_map_computation"
    fronts = {
        fact["street"]: fact
        for fact in body["site"]["facts"]
        if fact["key"] == "lot_frontage"
    }
    assert {f.street_name for f in geometry.frontages} == set(fronts)
    for f in geometry.frontages:
        assert fronts[f.street_name]["value"] == f.length.value


# ---------------------------------------------------------------------------
# (b) The live default binds the geometry provider ONLY behind the flag.
# ---------------------------------------------------------------------------
def test_live_default_flag_gates_the_geometry_binding(monkeypatch) -> None:
    monkeypatch.setenv("LANE_B_ENABLED", "1")
    monkeypatch.setattr(properties, "get_pluto_fetcher", lambda: _northern_fetcher)
    monkeypatch.setattr(study_inputs, "cached_default_version_probe", lambda: _f09_probe)
    # Spy on the live geometry factory, returning the REAL provider with the recorded
    # fakes injected, so the flag-on path stays offline.
    real_factory = study_live_geometry.live_geometry_provider
    calls: list[dict] = []

    def spy(**kwargs):
        calls.append(kwargs)
        return real_factory(fetch_lot=_fake_lot, fetch_streets=_recorded_streets)

    monkeypatch.setattr(study_live_geometry, "live_geometry_provider", spy)

    # Flag OFF (production default): the binding is None, geometry is never built.
    monkeypatch.delenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, raising=False)
    study_inputs._live_study_inputs_provider.cache_clear()
    try:
        off = default_study_inputs_provider(NORTHERN_BBL, "cid-off")
    finally:
        study_inputs._live_study_inputs_provider.cache_clear()
    assert calls == []
    off_facts = _facts_by_key(off.site_facts)
    assert off_facts["lot_type"]["value"] is None
    assert off_facts["lot_type"]["measurement"]["rank"] == "unknown"
    assert all(fact["key"] != "lot_frontage" for fact in off.site_facts)

    # Flag ON: the live geometry provider is bound and geometry is threaded.
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    study_inputs._live_study_inputs_provider.cache_clear()
    try:
        on = default_study_inputs_provider(NORTHERN_BBL, "cid-on")
    finally:
        study_inputs._live_study_inputs_provider.cache_clear()
    assert calls  # the flag-on path built the live geometry provider
    on_facts = _facts_by_key(on.site_facts)
    assert on_facts["lot_type"]["value"] == LOT_TYPE_CORNER
    assert any(fact["key"] == "lot_frontage" for fact in on.site_facts)


# ---------------------------------------------------------------------------
# (b) The flag-off binding (geometry_provider=None) is byte-identical to today.
# ---------------------------------------------------------------------------
def test_none_binding_is_byte_identical_to_the_pre_geometry_document() -> None:
    baseline = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON,
    )
    none_bound = pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON, geometry_provider=None,
    )(NORTHERN_BBL, "cid")
    assert none_bound.site_facts == baseline.site_facts


# ---------------------------------------------------------------------------
# (c) A raising/failing fetch -> None -> facts unknown; the route stays 200.
# ---------------------------------------------------------------------------
def test_raising_fetch_yields_none_and_route_stays_200_with_unknown(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, "1")

    def _raising_lot(canonical_bbl: str, correlation_id: str):
        raise UpstreamError(
            "official MapPLUTO source unreachable (test)", correlation_id=correlation_id
        )

    provider = live_geometry_provider(fetch_lot=_raising_lot, fetch_streets=_recorded_streets)
    # The provider swallows the typed connector error to None (geometry unavailable).
    assert provider(NORTHERN_BBL, _CID) is None
    # The study read then shows unknown facts and returns 200 (never 503/500).
    inputs_provider = pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON, geometry_provider=provider,
    )
    response = _client(inputs_provider).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 200
    facts = _facts_by_key(response.json()["site"]["facts"])
    assert facts["lot_type"]["value"] is None
    assert facts["lot_type"]["measurement"]["rank"] == "unknown"
    assert all(fact["key"] != "lot_frontage" for fact in response.json()["site"]["facts"])


# ---------------------------------------------------------------------------
# (c) A non-EPSG:2263 geometry page -> None (the accepted parser refuses it).
# ---------------------------------------------------------------------------
def test_non_2263_geometry_page_yields_none() -> None:
    url, body, retrieved = recorded_dcm_envelope_page()
    doc = json.loads(body)
    doc["spatialReference"] = {"wkid": 4326, "latestWkid": 4326}
    tampered = json.dumps(doc)

    def _streets(fetch_url: str, correlation_id: str) -> DcmTransport:
        meta = _pack_transport(_META_FILE)
        if fetch_url == meta.url:
            return meta
        assert fetch_url == url
        return DcmTransport(url=url, status=200, body=tampered, retrieved_at=retrieved)

    provider = live_geometry_provider(fetch_lot=_fake_lot, fetch_streets=_streets)
    assert provider(NORTHERN_BBL, _CID) is None


# ---------------------------------------------------------------------------
# (c) An outline the adapter refuses -> None (geometry unavailable, facts unknown).
# ---------------------------------------------------------------------------
def test_adapter_refused_outline_yields_none(monkeypatch) -> None:
    monkeypatch.setattr(
        study_live_geometry, "lot_outline_from_mappluto",
        lambda result: (None, "the MapPLUTO outline is not measured here (test)"),
    )
    provider = live_geometry_provider(fetch_lot=_fake_lot, fetch_streets=_recorded_streets)
    assert provider(NORTHERN_BBL, _CID) is None
