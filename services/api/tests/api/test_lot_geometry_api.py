"""Internal display-only lot-geometry endpoint acceptance pack (task M5-T020,
D-040-R001; scenarios S1-S6).

Fully OFFLINE and deterministic: the route's outline transport seam is overridden
via FastAPI dependency injection with the RECORDED f=geojson&outSR=4326 fixtures
(services/api/tests/fixtures/mappluto_lot_outline). No test touches the network.

Coverage:
- S1: 200 single-lot outline; contract-valid document; EPSG:4326 lng/lat; bbl
  echoed; condo classification; source provenance (source_id, endpoint, dataset
  Version, retrieved_at); display_only true; +/-20 ft accuracy note; NYC DCP
  attribution; X-Correlation-ID header.
- S2: every typed outcome is an HONEST 200 (single_lot / no_outline condo-unit &
  no-feature / multiple_features review / invalid_geometry); geometry withheld
  where appropriate; every body is renderer-parity JSON safe.
- S3: flag off -> generic 404 {detail: Not Found} with no correlation leak;
  malformed bbl -> typed 422 with X-Correlation-ID; body-less GET-only;
  include_in_schema False.
- S6: STATUS_STATE_MATRIX is the emitted set; every 200 body validates against the
  bundled lot_geometry schema and both json.dumps renderings.
- transport faults map to typed 5xx (wrong_crs, malformed_response, upstream).
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from app.api.v1.lot_geometry import STATUS_STATE_MATRIX, get_lot_outline_fetcher
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.mappluto_lot_outline import (
    LotOutlineError,
    LotOutlineTransport,
    build_outline_query_url,
)
from app.main import app

FX = Path(__file__).resolve().parents[1] / "fixtures" / "mappluto_lot_outline"
BUNDLE = Path(__file__).resolve().parents[2] / "app" / "_contract_schemas" / "v1"

SINGLE_BBL = "1008350041"
URL = f"/api/v1/properties/{SINGLE_BBL}/lot-geometry"
RETRIEVED_AT = "2026-09-12T13:45:07Z"

_WRONG_CRS_BODY = json.dumps(
    {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:2263"}},
        "features": [],
    }
)


# ---------------------------------------------------------------------------
# Offline seam plumbing
# ---------------------------------------------------------------------------


def _fixture_fetch(fixture_file: str):
    body = (FX / fixture_file).read_text(encoding="utf-8")

    def fetch(canonical_bbl: str, correlation_id: str) -> LotOutlineTransport:
        return LotOutlineTransport(
            url=build_outline_query_url(canonical_bbl),
            status=200,
            body=body,
            retrieved_at=RETRIEVED_AT,
        )

    return fetch


def install_fixture(fixture_file: str) -> None:
    app.dependency_overrides[get_lot_outline_fetcher] = lambda: _fixture_fetch(fixture_file)


def install_landmine() -> None:
    """Override the seam with a fetcher that raises if ever invoked, so a request
    that returns before any I/O cannot silently perform a fetch."""

    def _provider():
        def fetch(canonical_bbl: str, correlation_id: str):
            raise AssertionError("outline fetcher must not be invoked for this request")

        return fetch

    app.dependency_overrides[get_lot_outline_fetcher] = _provider


def install_raising(exc: Exception) -> None:
    def _provider():
        def fetch(canonical_bbl: str, correlation_id: str):
            raise exc

        return fetch

    app.dependency_overrides[get_lot_outline_fetcher] = _provider


def install_raw_body(body: str) -> None:
    def _provider():
        def fetch(canonical_bbl: str, correlation_id: str):
            return LotOutlineTransport(
                url=build_outline_query_url(canonical_bbl),
                status=200,
                body=body,
                retrieved_at=RETRIEVED_AT,
            )

        return fetch

    app.dependency_overrides[get_lot_outline_fetcher] = _provider


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


# ---------------------------------------------------------------------------
# Contract validation helper (mirrors how the API loads the bundled schema)
# ---------------------------------------------------------------------------


def _registry() -> Registry:
    resources = []
    for name in ("lot_geometry.schema.json", "common.schema.json"):
        doc = json.loads((BUNDLE / name).read_text(encoding="utf-8"))
        resources.append(
            (doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
        )
    return Registry().with_resources(resources)


def _validate_contract(document: dict) -> None:
    schema = json.loads((BUNDLE / "lot_geometry.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema, registry=_registry()).validate(document)


def _assert_renderer_parity_safe(document: dict) -> None:
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


# ---------------------------------------------------------------------------
# S1 - single-lot 200
# ---------------------------------------------------------------------------


def test_s1_single_lot_200(client, monkeypatch):
    enable_flag(monkeypatch)
    install_fixture("LOT01_single_1008350041.geojson")
    resp = client.get(URL)
    assert resp.status_code == 200
    assert resp.headers["X-Correlation-ID"]
    body = resp.json()
    _validate_contract(body)
    _assert_renderer_parity_safe(body)
    assert body["outcome"] == "single_lot"
    assert body["bbl"] == SINGLE_BBL
    assert body["display_only"] is True
    assert body["crs"] == "EPSG:4326"
    assert body["geometry"]["type"] == "Polygon"
    lng, lat = body["geometry"]["coordinates"][0][0]
    assert -74.3 < lng < -73.6 and 40.4 < lat < 41.0
    assert body["condo_classification"]["classification"] == "standard_lot"
    assert body["source"]["source_id"] == "nyc-dcp-mappluto-arcgis"
    assert body["source"]["dataset_version"] == "26v2"
    assert body["source"]["endpoint"].endswith("&f=geojson&outSR=4326")
    assert body["source"]["retrieved_at"] == RETRIEVED_AT
    assert "20 ft" in body["accuracy_note"]
    assert "DCP" in body["attribution"]


# ---------------------------------------------------------------------------
# S2 - every typed outcome is an honest 200
# ---------------------------------------------------------------------------

OUTCOME_200 = [
    ("1008350041", "LOT01_single_1008350041.geojson", "single_lot", "Polygon"),
    ("4142600001", "LOT06_multipolygon_4142600001.geojson", "single_lot", "MultiPolygon"),
    ("1000157501", "LOT03_condo_billing_1000157501.geojson", "single_lot", "Polygon"),
    ("1000151001", "LOT04_condo_unit_1000151001.geojson", "no_outline", None),
    ("5999999999", "LOT02_nofeature_5999999999.geojson", "no_outline", None),
    ("1008350041", "LOT96_multiple_features_synthetic.geojson", "multiple_features", None),
    ("1008350041", "LOT80_invalid_geometry_null_synthetic.geojson", "invalid_geometry", None),
]


_OUTCOME_200_IDS = [c[1] for c in OUTCOME_200]


@pytest.mark.parametrize("bbl,fixture,outcome,geom_type", OUTCOME_200, ids=_OUTCOME_200_IDS)
def test_s2_typed_outcomes_are_honest_200(client, monkeypatch, bbl, fixture, outcome, geom_type):
    enable_flag(monkeypatch)
    install_fixture(fixture)
    resp = client.get(f"/api/v1/properties/{bbl}/lot-geometry")
    assert resp.status_code == 200
    body = resp.json()
    _validate_contract(body)
    _assert_renderer_parity_safe(body)
    assert body["outcome"] == outcome
    assert (body["geometry"] is None) == (geom_type is None)
    if geom_type:
        assert body["geometry"]["type"] == geom_type
    if outcome == "multiple_features":
        assert body["review_required"] is True
        assert body["geometry"] is None  # never a silent first-pick


# ---------------------------------------------------------------------------
# S3 - route posture
# ---------------------------------------------------------------------------


def test_s3_flag_off_is_generic_404_no_leak(client, monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    install_landmine()  # a fetch here would be a boundary violation
    resp = client.get(URL)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_s3_flag_unknown_token_is_disabled(client, monkeypatch):
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "maybe")
    install_landmine()
    resp = client.get(URL)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}


def test_s3_malformed_bbl_is_422_with_correlation(client, monkeypatch):
    enable_flag(monkeypatch)
    install_landmine()  # 422 is pre-fetch: the seam must not run
    resp = client.get("/api/v1/properties/not-a-bbl/lot-geometry")
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "validation_error"
    assert resp.headers["X-Correlation-ID"]
    assert "raw_value" in body["detail"]


def test_s3_get_only_post_is_405(client, monkeypatch):
    enable_flag(monkeypatch)
    install_landmine()
    resp = client.post(URL)
    assert resp.status_code == 405


def test_s3_not_in_openapi(client):
    schema = client.get("/openapi.json").json()
    assert "/api/v1/properties/{bbl}/lot-geometry" not in schema.get("paths", {})


# ---------------------------------------------------------------------------
# transport faults -> typed 5xx
# ---------------------------------------------------------------------------


def test_wrong_crs_maps_to_502(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_raw_body(_WRONG_CRS_BODY)
    resp = raw_client.get(URL)
    assert resp.status_code == 502
    assert resp.json()["state"] == "wrong_crs"
    assert resp.headers["X-Correlation-ID"]


def test_malformed_body_maps_to_502(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_raw_body("<html>not json</html>")
    resp = raw_client.get(URL)
    assert resp.status_code == 502
    assert resp.json()["state"] == "malformed_response"


def test_upstream_error_maps_to_502(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_raising(LotOutlineError("service down", correlation_id="x", detail={}))
    resp = raw_client.get(URL)
    assert resp.status_code == 502
    assert resp.json()["state"] == "upstream_error"


def test_unexpected_exception_maps_to_generic_500(raw_client, monkeypatch):
    enable_flag(monkeypatch)
    install_raising(RuntimeError("boom"))
    resp = raw_client.get(URL)
    assert resp.status_code == 500
    assert resp.json()["state"] == "internal_error"


# ---------------------------------------------------------------------------
# S6 - status/state matrix is exactly the emitted set
# ---------------------------------------------------------------------------


def test_s6_emitted_pairs_are_in_the_matrix(client, raw_client, monkeypatch):
    seen: set[tuple[int, str | None]] = set()

    enable_flag(monkeypatch)
    install_fixture("LOT01_single_1008350041.geojson")
    r = client.get(URL)
    seen.add((r.status_code, r.json().get("state")))

    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    install_landmine()
    r = client.get(URL)
    seen.add((r.status_code, None))  # generic 404 sentinel

    enable_flag(monkeypatch)
    install_landmine()
    r = client.get("/api/v1/properties/xx/lot-geometry")
    seen.add((r.status_code, r.json().get("state")))

    install_raw_body(_WRONG_CRS_BODY)
    r = raw_client.get(URL)
    seen.add((r.status_code, r.json().get("state")))

    assert seen <= STATUS_STATE_MATRIX, f"emitted {seen - STATUS_STATE_MATRIX} not in matrix"


def test_s6_bundled_schema_is_byte_identical_to_canonical():
    canonical = (
        Path(__file__).resolve().parents[4]
        / "packages" / "contracts" / "schemas" / "v1" / "lot_geometry.schema.json"
    ).read_bytes()
    bundled = (BUNDLE / "lot_geometry.schema.json").read_bytes()
    assert bundled == canonical, "runtime-bundled lot_geometry schema diverged from canonical"


def test_s6_generated_ts_covers_every_schema_key_enum_and_const():
    """G4 correction BLOCKING-2: the contracts-typegen CI job's hardcoded list does
    not yet cover lot_geometry.ts (generator wiring is a bound follow-up), so this
    in-suite structural check is the load-bearing schema->TS drift guard until it
    lands: every property name, enum string value, and const string literal in the
    canonical schema must appear in the committed generated TS. A schema change
    without regenerating the TS fails here."""
    root = Path(__file__).resolve().parents[4]
    schema = json.loads(
        (root / "packages" / "contracts" / "schemas" / "v1" / "lot_geometry.schema.json")
        .read_text(encoding="utf-8")
    )
    ts_text = (
        root / "packages" / "contracts" / "generated" / "lot_geometry.ts"
    ).read_text(encoding="utf-8")

    missing: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            for key in node.get("properties", {}) or {}:
                if key not in ts_text:
                    missing.append(f"property {key!r}")
            for value in node.get("enum", []) or []:
                if isinstance(value, str) and f'"{value}"' not in ts_text:
                    missing.append(f"enum value {value!r}")
            const = node.get("const")
            if isinstance(const, str) and f'"{const}"' not in ts_text:
                missing.append(f"const {const!r}")
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(schema)
    assert not missing, f"generated lot_geometry.ts is missing schema tokens: {missing}"
