"""Acceptance pack for POST /api/v1/export - the UNMOUNTED CAD/3D export route (M5-T109, PKT-D).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted, route-free
:func:`app.cad.export_service.build_export`; it ships UNMOUNTED (app/main.py is NOT touched), so
every test mounts the router on a FRESH ``FastAPI()`` via ``TestClient`` (the accepted M5-T059 /
max_envelope_api pattern) and one test asserts the path is ABSENT from the real app's OpenAPI.

AS-4 (route discipline): absent from OpenAPI; flag off -> the same generic 404 as an unmounted
path; bounded request bytes (413); per-format media types on a 200 FILE; a server-generated
X-Correlation-ID; the writer runs off the event loop in a cancellable job with a per-request
deadline (503) behind a per-caller rate limit (429); typed refusals are JSON, never a partial
file. DB-075 (b): a pathological-but-bounded caller input returns the reconciled typed refusal
through the REAL route.
"""

from __future__ import annotations

import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import export_api as mod
from app.api.v1.export_api import EXPORT_STATUS_STATE_MATRIX, MAX_BODY_BYTES, router
from app.cad import export_service
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR

_URL = "/api/v1/export"
_JSON_HEADERS = {"content-type": "application/json"}

_LOT = [
    [985000.0, 195000.0], [985080.0, 195000.0],
    [985080.0, 195100.0], [985000.0, 195100.0],
]
_BUILDING = [
    [985010.0, 195010.0], [985070.0, 195010.0],
    [985070.0, 195090.0], [985010.0, 195090.0],
]


def _body(**overrides) -> dict:
    body = {
        "format": "dxf",
        "source": "proposed",
        "lot_ring": _LOT,
        "building_ring": _BUILDING,
        "floor_heights": [10.0, 10.0, 10.0],
        "address": "12 MAIN ST",
        "bbl": "1-00123-0045",
        "generated_at": "2026-09-24T00:00:00Z",
        "generator_version": "site-plan-writer/1.0.0",
    }
    body.update(overrides)
    return body


def _pair(response) -> tuple[int, str | None]:
    try:
        state = response.json().get("state")
    except ValueError:  # a 200 FILE download is not JSON
        state = None
    return response.status_code, state


@pytest.fixture
def mounted_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(mounted_app, monkeypatch):
    """A client over a fresh app with the flag ON and a freshly reset rate limiter."""
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    mod.get_rate_limiter().reset()
    with TestClient(mounted_app, raise_server_exceptions=False) as test_client:
        yield test_client
    mod.get_rate_limiter().reset()


# --------------------------------------------------------------------------- #
# AS-4: unmounted + flag gating.
# --------------------------------------------------------------------------- #

def test_route_is_unmounted_in_the_real_app():
    """The route ships UNMOUNTED: app/main.py is not touched, so the path is absent from the real
    app's routes and (include_in_schema=False) from its OpenAPI."""
    from app.main import app as real_app

    real_paths = {getattr(route, "path", None) for route in real_app.routes}
    assert _URL not in real_paths
    assert _URL not in real_app.openapi().get("paths", {})


def test_flag_off_is_a_generic_404(mounted_app, monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as client:
        resp = client.post(_URL, json=_body())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers
    assert _pair(resp) in EXPORT_STATUS_STATE_MATRIX


# --------------------------------------------------------------------------- #
# AS-4: a 200 FILE per format, correct media type + safe headers.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "fmt, media",
    [("dxf", "image/vnd.dxf"), ("pdf", "application/pdf"), ("glb", "model/gltf-binary")],
)
def test_200_returns_a_file_per_format(client, fmt, media):
    resp = client.post(_URL, json=_body(format=fmt))
    assert resp.status_code == 200
    assert _pair(resp) == (200, None)
    assert resp.headers["content-type"] == media
    assert resp.content  # non-empty file bytes
    cid = resp.headers.get("X-Correlation-ID")
    assert cid
    cd = resp.headers["content-disposition"]
    assert cd.startswith('attachment; filename="site-plan-') and cd.endswith(f'.{fmt}')
    assert resp.headers["x-content-type-options"] == "nosniff"
    # No caller text reaches a header value; the filename token is the safe allowlist grammar.
    assert "12 MAIN ST" not in cd


def test_filename_falls_back_to_correlation_id_when_token_empties(client):
    """DB-065 (a): a bbl/generated_at that allowlists to nothing uses the request correlation id
    as the caller-free filename token."""
    resp = client.post(_URL, json=_body(bbl=":::", generated_at="///"))
    assert resp.status_code == 200
    cid = resp.headers["X-Correlation-ID"]
    assert f"site-plan-{cid}.dxf" in resp.headers["content-disposition"]


# --------------------------------------------------------------------------- #
# AS-4: bounded body + malformed body.
# --------------------------------------------------------------------------- #

def test_413_oversized_body(client):
    resp = client.post(_URL, content=b"x" * (MAX_BODY_BYTES + 1), headers=_JSON_HEADERS)
    assert _pair(resp) == (413, "payload_too_large")
    assert _pair(resp) in EXPORT_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")


@pytest.mark.parametrize("raw", [b"", b"   ", b"not json", b"[]", b'"a string"'])
def test_422_malformed_body(client, raw):
    resp = client.post(_URL, content=raw, headers=_JSON_HEADERS)
    assert _pair(resp) == (422, "validation_error")


def test_422_nan_is_refused(client):
    resp = client.post(_URL, content=b'{"format": "dxf", "base_elevation": NaN}',
                       headers=_JSON_HEADERS)
    assert _pair(resp) == (422, "validation_error")


# --------------------------------------------------------------------------- #
# AS-4 / AS-2 / DB-075 (b): a typed, reconciled refusal through the REAL route.
# --------------------------------------------------------------------------- #

def test_422_typed_refusal_through_the_real_route(client):
    """DB-075 (b): a pathological-but-bounded input (a claim word in caller text) returns the
    reconciled typed refusal - {reject_code, detail} - through the real route, never a 500 and
    never a partial file."""
    resp = client.post(_URL, json=_body(address="APPROVED luxury tower"))
    assert _pair(resp) == (422, "validation_error")
    body = resp.json()
    assert body["reject_code"] == "claim_class_word"
    assert "luxury" not in body["detail"]  # caller text redacted
    assert resp.headers["content-type"].startswith("application/json")  # not a partial file
    assert resp.headers.get("X-Correlation-ID")


def test_422_bad_geometry_is_reconciled_and_redacted(client):
    """A GLB writer RAISE (an out-of-range coordinate) surfaces as one redacted refusal; the
    offending value is absent from the response."""
    huge = [[0.0, 0.0], [2.0e9, 0.0], [2.0e9, 1.0]]
    resp = client.post(_URL, json=_body(format="glb", building_ring=huge))
    assert _pair(resp) == (422, "validation_error")
    assert resp.json()["reject_code"] == "coordinate_out_of_range"
    assert "2000000000" not in resp.text


def test_422_unsupported_format(client):
    resp = client.post(_URL, json=_body(format="dwg"))
    assert _pair(resp) == (422, "validation_error")
    assert resp.json()["reject_code"] == "unsupported_format"


# --------------------------------------------------------------------------- #
# AS-4: per-caller rate limit (429) + per-request deadline (503).
# --------------------------------------------------------------------------- #

def test_429_per_caller_rate_limit(client, monkeypatch):
    monkeypatch.setattr(mod, "RATE_LIMIT_MAX_REQUESTS", 2)
    mod.get_rate_limiter().reset()
    assert client.post(_URL, json=_body()).status_code == 200
    assert client.post(_URL, json=_body()).status_code == 200
    limited = client.post(_URL, json=_body())
    assert _pair(limited) == (429, "rate_limited")
    assert _pair(limited) in EXPORT_STATUS_STATE_MATRIX
    assert limited.headers.get("X-Correlation-ID")


def test_503_per_request_deadline(client, monkeypatch):
    """The writer runs OFF the event loop in a cancellable job under a wall-clock deadline; a slow
    build is abandoned with a typed 503, never a partial file (DB-061 (i))."""
    def _slow(*args, **kwargs):
        time.sleep(0.5)
        return export_service.ExportRefusal("unused", "unused")

    monkeypatch.setattr(export_service, "build_export", _slow)
    monkeypatch.setattr(mod, "EXPORT_DEADLINE_SECONDS", 0.02)
    resp = client.post(_URL, json=_body())
    assert _pair(resp) == (503, "deadline_exceeded")
    assert _pair(resp) in EXPORT_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")


def test_500_on_an_unexpected_internal_defect(client, monkeypatch):
    """An unexpected exception from the service is a documented generic 500, no str(exc) leak."""
    def _boom(*args, **kwargs):
        raise RuntimeError("SECRET_INTERNAL_STRING")

    monkeypatch.setattr(export_service, "build_export", _boom)
    resp = client.post(_URL, json=_body())
    assert _pair(resp) == (500, "internal_error")
    assert "SECRET_INTERNAL_STRING" not in resp.text


# --------------------------------------------------------------------------- #
# AS-4: every emitted (status, state) is a documented matrix member.
# --------------------------------------------------------------------------- #

def test_correlation_id_on_every_non_disabled_response(client):
    for kwargs in ({"json": _body()}, {"json": _body(format="dwg")},
                   {"content": b"", "headers": _JSON_HEADERS}):
        resp = client.post(_URL, **kwargs)
        assert resp.headers.get("X-Correlation-ID")
