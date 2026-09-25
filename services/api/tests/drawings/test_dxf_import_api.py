"""Acceptance pack for the UNMOUNTED DXF import route (task M5-T108, D-087 PKT-F).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted DXF
reader + import service; it ships UNMOUNTED (app/main.py untouched), so every test mounts
the router on a FRESH ``FastAPI()`` via ``TestClient`` (the accepted M5-T059 / max-envelope
pattern) and one test asserts it is ABSENT from the real app's OpenAPI.

- AS-1 (parse-time controls): an over-ceiling upload refuses before the body is
  materialised; a binary / non-DXF upload refuses on the media/magic-byte check; DxfLimits
  is a fixed clamp at the seam; read_dxf runs in a deadline-bounded off-loop job with a
  per-caller rate limit. Each control has a test AND a reddening mutation.
- AS-5 (persists nothing + scope): flag off -> the generic 404; UNMOUNTED from the real
  app; the documented (status, state) matrix; no persistence.
"""

from __future__ import annotations

import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import dxf_import_api as mod
from app.api.v1.dxf_import_api import (
    DXF_IMPORT_ENABLED_ENV_VAR,
    DXF_IMPORT_STATUS_STATE_MATRIX,
    MAX_BODY_BYTES,
    router,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.drawings.dxf_reader import DxfLimits, read_dxf

_RING = [(985000.0, 195000.0), (985080.0, 195000.0), (985080.0, 195100.0), (985000.0, 195100.0)]
_CAND_URL = "/api/v1/dxf-import/candidates"
_DRAFT_URL = "/api/v1/dxf-import/draft"
_DXF_HEADERS = {"content-type": "application/dxf"}
_DRAFT_Q = (
    "?building_outline=0&floors=5&floor_to_floor_ft=11&author=Jane"
    "&confirmed_units=us_survey_feet"
)


def _dxf(rings=((_RING, "BUILDING", True),), *, insunits=21) -> bytes:
    lines = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", str(insunits)]
    lines += ["0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for verts, layer, closed in rings:
        lines += ["0", "LWPOLYLINE", "8", layer, "70", "1" if closed else "0"]
        for x, y in verts:
            lines += ["10", str(x), "20", str(y)]
    lines += ["0", "ENDSEC", "0", "EOF"]
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def _pair(response) -> tuple[int, str | None]:
    try:
        state = response.json().get("state")
    except ValueError:  # pragma: no cover
        state = None
    return response.status_code, state


@pytest.fixture
def mounted_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(mounted_app, monkeypatch):
    """A client over a fresh app with BOTH gating flags ON and a clean rate limiter."""
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(DXF_IMPORT_ENABLED_ENV_VAR, "1")
    mod.get_rate_limiter().reset()
    with TestClient(mounted_app, raise_server_exceptions=False) as test_client:
        yield test_client


# --------------------------------------------------------------------------- happy path


def test_candidates_200(client):
    resp = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert resp.status_code == 200
    assert _pair(resp) in DXF_IMPORT_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")
    doc = resp.json()
    assert doc["declared_units"]["name"] == "us_survey_feet"
    assert len(doc["candidates"]) == 1
    assert doc["candidates"][0]["measured"]["area"] == 8000.0
    assert "not survey-confirmed" in doc["notice"]


def test_draft_200(client):
    resp = client.post(_DRAFT_URL + _DRAFT_Q, content=_dxf(), headers=_DXF_HEADERS)
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["proposed_massing"]["outline"]["srid"] == 2263
    assert doc["provenance"]["precision"] == "imported drawing - not survey-confirmed"
    assert doc["provenance"]["label"] == "Proposed - not a city record"


def test_draft_shows_discrepancy_not_reconciled(client):
    resp = client.post(_DRAFT_URL + _DRAFT_Q, content=_dxf(insunits=6), headers=_DXF_HEADERS)
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["discrepancies"][0]["type"] == "units_mismatch"
    assert doc["provenance"]["unit_scale_ft_per_unit"] == 1.0  # feet, not converted


# --------------------------------------------------------------------------- AS-5 posture


def test_flag_off_is_generic_404(mounted_app, monkeypatch):
    # Base flag on, dedicated import flag off -> the generic 404 (fail-safe disable).
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    monkeypatch.delenv(DXF_IMPORT_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as c:
        resp = c.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_draft_flag_off_is_404_even_with_bad_params(mounted_app, monkeypatch):
    # A disabled feature must not leak a 422 for malformed params either.
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    monkeypatch.delenv(DXF_IMPORT_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as c:
        resp = c.post(_DRAFT_URL + "?floors=notanumber", content=_dxf(), headers=_DXF_HEADERS)
    assert resp.status_code == 404


def test_route_is_unmounted_in_the_real_app():
    from app.main import app as real_app

    real_paths = {getattr(route, "path", None) for route in real_app.routes}
    assert _CAND_URL not in real_paths
    assert _DRAFT_URL not in real_paths
    paths = real_app.openapi().get("paths", {})
    assert _CAND_URL not in paths and _DRAFT_URL not in paths


def test_status_state_matrix_is_the_documented_set():
    assert (200, None) in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (404, None) in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (413, "payload_too_large") in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (415, "unsupported_media_type") in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (429, "rate_limited") in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (503, "deadline_exceeded") in DXF_IMPORT_STATUS_STATE_MATRIX


def test_no_persistence_state_between_requests(client):
    # Two identical draft requests return equivalent bodies (bar the correlation id): the
    # route holds no per-request state beyond the rate limiter (AS-5 persists nothing).
    a = client.post(_DRAFT_URL + _DRAFT_Q, content=_dxf(), headers=_DXF_HEADERS).json()
    b = client.post(_DRAFT_URL + _DRAFT_Q, content=_dxf(), headers=_DXF_HEADERS).json()
    a.pop("correlation_id"), b.pop("correlation_id")
    assert a == b


# --------------------------------------------------------------------------- AS-1 (b) ceiling


def test_over_ceiling_upload_refused_413(client):
    big = b"0\r\nSECTION\r\n" + b"9" * (MAX_BODY_BYTES + 1)
    resp = client.post(_CAND_URL, content=big, headers=_DXF_HEADERS)
    assert _pair(resp) == (413, "payload_too_large")


def test_over_ceiling_streamed_refused_413(client, monkeypatch):
    # Force the declared-length fast path off so the STREAMED accumulator is what refuses.
    monkeypatch.setattr(mod, "_declared_content_length", lambda request: None)
    big = b"0\r\nSECTION\r\n" + b"9" * (MAX_BODY_BYTES + 1)
    resp = client.post(_CAND_URL, content=big, headers=_DXF_HEADERS)
    assert _pair(resp) == (413, "payload_too_large")


def test_mutation_ceiling_guard(client, monkeypatch):
    # Raise the ceiling far above the payload -> the over-original body no longer 413s,
    # proving MAX_BODY_BYTES drives the guard (AS-1 b).
    monkeypatch.setattr(mod, "MAX_BODY_BYTES", 10**9)
    big = _dxf() + b"9" * (MAX_BODY_BYTES + 1000)
    resp = client.post(_CAND_URL, content=big, headers=_DXF_HEADERS)
    assert resp.status_code != 413


# --------------------------------------------------------------------------- AS-1 (d) media/magic


def test_binary_dxf_refused_415(client):
    resp = client.post(_CAND_URL, content=b"AutoCAD Binary DXF\r\n\x1a\x00xx", headers=_DXF_HEADERS)
    assert _pair(resp) == (415, "unsupported_media_type")


def test_wrong_content_type_refused_415(client):
    resp = client.post(_CAND_URL, content=_dxf(), headers={"content-type": "application/json"})
    assert _pair(resp) == (415, "unsupported_media_type")


def test_mutation_media_guard(client, monkeypatch):
    # Neuter the media/magic-byte gate -> a binary upload reaches read_dxf, which refuses
    # it as 422 (not 415), proving the seam gate is what returns 415 (AS-1 d).
    monkeypatch.setattr(mod, "sniff_dxf_media", lambda ct, raw: None)
    resp = client.post(_CAND_URL, content=b"AutoCAD Binary DXF\r\n\x1a\x00xx", headers=_DXF_HEADERS)
    assert resp.status_code == 422  # reddens test_binary_dxf_refused_415


# --------------------------------------------------------------------------- AS-1 (d) clamp


def test_seam_passes_fixed_reviewed_limits(client, monkeypatch):
    captured = {}
    real = read_dxf

    def _capturing(raw, *, limits):
        captured["limits"] = limits
        return real(raw, limits=limits)

    monkeypatch.setattr(mod, "read_dxf", _capturing)
    client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert captured["limits"] is mod._IMPORT_DXF_LIMITS
    assert isinstance(captured["limits"], DxfLimits)
    assert captured["limits"].max_bytes == MAX_BODY_BYTES  # fixed, not request-derived


def test_mutation_clamp_uses_module_constant(client, monkeypatch):
    # Swap the module clamp constant -> the captured limits follow it, proving the route
    # reads the module constant (not a request-derived or hardcoded value) (AS-1 d).
    sentinel = DxfLimits(max_entities=7)
    monkeypatch.setattr(mod, "_IMPORT_DXF_LIMITS", sentinel)
    captured = {}
    real = read_dxf

    def _capturing(raw, *, limits):
        captured["limits"] = limits
        return real(raw, limits=limits)

    monkeypatch.setattr(mod, "read_dxf", _capturing)
    client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert captured["limits"] is sentinel


# --------------------------------------------------------------------------- AS-1 (c) deadline


def test_read_job_deadline_503(client, monkeypatch):
    monkeypatch.setattr(mod, "READ_DEADLINE_SECONDS", 0.1)

    def _slow(raw, *, limits):
        time.sleep(0.6)
        return read_dxf(raw, limits=limits)

    monkeypatch.setattr(mod, "read_dxf", _slow)
    resp = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert _pair(resp) == (503, "deadline_exceeded")


def test_mutation_deadline_guard(client, monkeypatch):
    # A generous deadline over the same slow read -> no 503, proving the deadline drives
    # the refusal (AS-1 c).
    monkeypatch.setattr(mod, "READ_DEADLINE_SECONDS", 5.0)

    def _slow(raw, *, limits):
        time.sleep(0.2)
        return read_dxf(raw, limits=limits)

    monkeypatch.setattr(mod, "read_dxf", _slow)
    resp = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert resp.status_code == 200  # reddens test_read_job_deadline_503


# --------------------------------------------------------------------------- AS-1 (c) rate limit


def test_rate_limit_429(client, monkeypatch):
    monkeypatch.setattr(mod, "_RATE_LIMITER", mod._RateLimiter(1, 60.0))
    monkeypatch.setattr(mod, "get_rate_limiter", lambda: mod._RATE_LIMITER)
    first = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    second = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert first.status_code == 200
    assert _pair(second) == (429, "rate_limited")


def test_mutation_rate_limit_guard(client, monkeypatch):
    # Disable the limiter -> the second request no longer 429s, proving the limiter drives
    # the refusal (AS-1 c).
    class _AlwaysAllow:
        def check(self, key, **k):
            return True

    monkeypatch.setattr(mod, "get_rate_limiter", lambda: _AlwaysAllow())
    for _ in range(3):
        resp = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert resp.status_code == 200  # reddens test_rate_limit_429


# --------------------------------------------------------------------------- draft refusals


def test_out_of_bounds_ring_422(client):
    near_origin = [(0.0, 0.0), (80.0, 0.0), (80.0, 100.0), (0.0, 100.0)]
    resp = client.post(
        _DRAFT_URL + _DRAFT_Q, content=_dxf(rings=((near_origin, "B", True),)), headers=_DXF_HEADERS
    )
    assert _pair(resp) == (422, "validation_error")
    assert resp.json()["field"].startswith("proposed_massing.outline")


def test_missing_required_param_422(client):
    resp = client.post(
        _DRAFT_URL + "?floors=5&floor_to_floor_ft=11&author=J&confirmed_units=feet",
        content=_dxf(), headers=_DXF_HEADERS,
    )
    assert _pair(resp) == (422, "validation_error")
    assert resp.json()["field"] == "building_outline"


def test_bad_numeric_param_422(client):
    bad = "?building_outline=0&floors=x&floor_to_floor_ft=11&author=J&confirmed_units=feet"
    resp = client.post(_DRAFT_URL + bad, content=_dxf(), headers=_DXF_HEADERS)
    assert _pair(resp) == (422, "validation_error")
