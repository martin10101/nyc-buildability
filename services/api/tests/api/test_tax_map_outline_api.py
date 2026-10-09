"""Explicit DOF source selection is gated, isolated, and source-honest."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1.lot_geometry import get_lot_outline_fetcher, get_tax_map_outline_fetcher
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors import dtm_lot_outline as dtm
from app.connectors.mappluto_lot_outline import LotOutlineTransport
from app.main import app

FX = Path(__file__).resolve().parents[1] / "fixtures" / "dtm_lot_outline"
MANIFEST = json.loads((FX / "MANIFEST.json").read_text())
BBL = "3022640032"
URL = f"/api/v1/properties/{BBL}/lot-geometry"


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    with TestClient(app) as value:
        yield value
    app.dependency_overrides.clear()


def fixture_fetch(bbl, correlation_id):
    capture = next(row for row in MANIFEST["captures"] if row["bbl"] == bbl)
    return LotOutlineTransport(
        capture["url"], 200, (FX / capture["file"]).read_text(), capture["retrieved_at"]
    )


def forbidden_fetch(*args):
    pytest.fail("unselected source must not be queried")


def test_tax_map_selects_dof_and_never_queries_mappluto(client):
    app.dependency_overrides[get_lot_outline_fetcher] = lambda: forbidden_fetch
    app.dependency_overrides[get_tax_map_outline_fetcher] = lambda: fixture_fetch
    response = client.get(URL + "?source=tax-map")
    assert response.status_code == 200
    doc = response.json()
    assert doc["source"]["source_id"] == dtm.SOURCE_ID
    assert doc["contract_version"] == "1.1.0"
    assert doc["lot_identity"]["lot"] == 32
    assert doc["display_only"] is True
    assert response.headers["X-Correlation-ID"]


def test_default_remains_mappluto_and_never_queries_dof(client):
    from app.connectors.mappluto_lot_outline import build_outline_query_url
    app.dependency_overrides[get_tax_map_outline_fetcher] = lambda: forbidden_fetch
    app.dependency_overrides[get_lot_outline_fetcher] = lambda: (
        lambda b, c: LotOutlineTransport(
            build_outline_query_url(b), 200,
            '{"type":"FeatureCollection","features":[]}', "2026-09-26T20:00:00Z"
        )
    )
    response = client.get(URL)
    assert response.status_code == 200
    assert response.json()["contract_version"] == "1.0.0"
    assert response.json()["source"]["source_id"] == "nyc-dcp-mappluto-arcgis"


@pytest.mark.parametrize("suffix", ["?source=untrusted", "?source=tax-map&unused=1"])
def test_invalid_source_or_bbl_has_no_network_io(client, suffix):
    app.dependency_overrides[get_lot_outline_fetcher] = lambda: forbidden_fetch
    app.dependency_overrides[get_tax_map_outline_fetcher] = lambda: forbidden_fetch
    path = URL if "untrusted" in suffix else URL.replace(BBL, "bad")
    response = client.get(path + suffix)
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_disabled_flag_masks_tax_map_source_and_errors(client, monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR)
    app.dependency_overrides[get_lot_outline_fetcher] = lambda: forbidden_fetch
    app.dependency_overrides[get_tax_map_outline_fetcher] = lambda: forbidden_fetch
    for source in ("tax-map", "untrusted"):
        response = client.get(URL + "?source=" + source)
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}
        assert "X-Correlation-ID" not in response.headers


def test_dof_identity_fault_is_typed_502_with_correct_source(client):
    def mismatched(bbl, correlation_id):
        transport = fixture_fetch(bbl, correlation_id)
        doc = json.loads(transport.body)
        doc["features"][0]["properties"]["LOT"] = 33
        return LotOutlineTransport(
            transport.url, 200, json.dumps(doc), transport.retrieved_at
        )
    app.dependency_overrides[get_lot_outline_fetcher] = lambda: forbidden_fetch
    app.dependency_overrides[get_tax_map_outline_fetcher] = lambda: mismatched
    response = client.get(URL + "?source=tax-map")
    assert response.status_code == 502
    assert response.json()["state"] == "result_mismatch"
    assert response.json()["source_id"] == dtm.SOURCE_ID
