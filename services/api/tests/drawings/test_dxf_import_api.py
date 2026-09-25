"""Acceptance pack for the UNMOUNTED DXF import route (task M5-T108 + M5-T111 route-hardening).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted DXF
reader + import service; it ships UNMOUNTED (app/main.py untouched), so every test mounts
the router on a FRESH ``FastAPI()`` via ``TestClient`` (the accepted M5-T059 / max-envelope
pattern) and one test asserts it is ABSENT from the real app's OpenAPI.

- AS-1 (parse-time controls): an over-ceiling upload refuses before the body is
  materialised; a binary / non-DXF upload refuses on the media/magic-byte check; DxfLimits
  is a fixed clamp at the seam; read_dxf runs in a deadline-bounded off-loop job under a
  bounded in-flight job cap with the ONE shared per-caller rate limiter. Each control has a
  test AND a reddening mutation.
- AS-5 (persists nothing + scope): flag off -> the generic 404 for EVERY method; UNMOUNTED
  from the real app; the documented (status, state) matrix; no persistence.

M5-T111 riders proven here (the shared-limiter properties live in
tests/resilience/test_rate_limit.py): AS-1 the route uses the shared limiter only; DB-081 (b)
the rate limit precedes the parameter parse; AS-5 the bounded job cap yields a typed 503;
AS-6 every method 404 while disabled + OpenAPI absence; DB-081 (e) the pre-render guard's
utf-8 encode step catches a non-encodable string.
"""

from __future__ import annotations

import ast
import inspect
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
from app.drawings import dxf_import as svc_mod
from app.drawings.dxf_reader import DxfLimits, read_dxf

_RING = [(985000.0, 195000.0), (985080.0, 195000.0), (985080.0, 195100.0), (985000.0, 195100.0)]
# Two DISTINCT closed in-bounds rings for the user-assigned-ring route test (G4 F1).
_RING_A = [(985000.0, 195000.0), (985200.0, 195000.0), (985200.0, 195200.0), (985000.0, 195200.0)]
_RING_B = [(990000.0, 200000.0), (990080.0, 200000.0), (990080.0, 200100.0), (990000.0, 200100.0)]
# Coordinates individually finite but overflowing the measured dimensions to inf (G5 MEDIUM 1).
_OVERFLOW_RING = [(1e300, 1e300), (1e300, 2e300), (2e300, 2e300), (2e300, 1e300)]
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
    """A client over a fresh app with BOTH gating flags ON and freshly reset limiter + slots."""
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(DXF_IMPORT_ENABLED_ENV_VAR, "1")
    mod.get_rate_limiter().reset()
    mod.get_job_slots().reset()
    with TestClient(mounted_app, raise_server_exceptions=False) as test_client:
        yield test_client
    mod.get_rate_limiter().reset()
    mod.get_job_slots().reset()


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


def test_every_method_is_a_generic_404_while_disabled(mounted_app, monkeypatch):
    """DB-081 (d): with the dedicated flag off, every method on both paths returns the generic
    404 byte-identical to an unmounted path - no 405 that would leak the route's existence."""
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    monkeypatch.delenv(DXF_IMPORT_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as c:
        for url in (_CAND_URL, _DRAFT_URL):
            for method in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
                resp = c.request(method, url)
                assert resp.status_code == 404, (url, method)
                assert "X-Correlation-ID" not in resp.headers, (url, method)
                if method == "HEAD":
                    assert resp.content == b"", (url, method)  # HEAD carries no body
                else:
                    assert resp.json() == {"detail": "Not Found"}, (url, method)


def test_enabled_non_post_method_is_a_real_405(client):
    """When ENABLED, a non-POST method is a genuine 405 on both paths (only POST does work)."""
    for url in (_CAND_URL, _DRAFT_URL):
        resp = client.get(url)
        assert resp.status_code == 405, url
        assert _pair(resp) == (405, None), url


def test_route_is_unmounted_in_the_real_app():
    from app.main import app as real_app

    real_paths = {getattr(route, "path", None) for route in real_app.routes}
    assert _CAND_URL not in real_paths
    assert _DRAFT_URL not in real_paths
    paths = real_app.openapi().get("paths", {})
    assert _CAND_URL not in paths and _DRAFT_URL not in paths


def test_no_path_in_the_throwaway_app_openapi(mounted_app):
    """AS-6 / DB-080 (c): the router IS included on this throwaway app, yet
    include_in_schema=False keeps both import paths out of its OpenAPI document."""
    schema_paths = mounted_app.openapi().get("paths", {})
    assert _CAND_URL not in schema_paths and _DRAFT_URL not in schema_paths
    assert not any(p.startswith("/api/v1/dxf-import") for p in schema_paths)


#: Names of constructors a route-local limiter would use for its state table.
_LIMITER_CONTAINER_CALLS = frozenset({"dict", "defaultdict", "OrderedDict", "deque"})


def _module_level_limiter_containers(src: str) -> list[str]:
    """AST guard (G3 A2 / G4 gap 4): return the target names of any MODULE-LEVEL assignment whose
    value is a dict literal or a ``dict``/``defaultdict``/``OrderedDict``/``deque`` construction -
    the shape a reintroduced route-local limiter would take (a *plain dict* the old substring scan
    missed). The shared limiter keeps ALL such state inside app.resilience.rate_limit, so a
    hardened route module must have NONE."""
    found: list[str] = []
    for node in ast.parse(src).body:  # module scope only
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        is_container = isinstance(value, ast.Dict)
        if isinstance(value, ast.Call):
            fn = value.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None)
            is_container = is_container or name in _LIMITER_CONTAINER_CALLS
        if is_container:
            found += [t.id for t in targets if isinstance(t, ast.Name)]
    return found


def test_route_uses_the_shared_limiter_and_slots_only():
    """AS-1: the shared limiter/slot classes back this route; no route-local limiter class,
    module-level dict/deque/OrderedDict or the old ``_rate_state`` dict survives (an AST guard
    over the module source catches the plain-dict form the substring scan missed - G3 A2)."""
    from app.resilience.rate_limit import JobSlots, SlidingWindowRateLimiter

    assert isinstance(mod.get_rate_limiter(), SlidingWindowRateLimiter)
    assert isinstance(mod.get_job_slots(), JobSlots)
    assert not hasattr(mod, "_RateLimiter")
    assert not hasattr(mod, "_rate_state")
    src = inspect.getsource(mod)
    assert "class _RateLimiter" not in src
    assert "deque" not in src and "OrderedDict" not in src and "_rate_state" not in src
    # AST guard: NO module-level dict/defaultdict/OrderedDict/deque limiter container.
    assert _module_level_limiter_containers(src) == []


def test_status_state_matrix_is_the_documented_set():
    assert (200, None) in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (404, None) in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (405, None) in DXF_IMPORT_STATUS_STATE_MATRIX  # DB-081 (d) enabled non-POST
    assert (413, "payload_too_large") in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (415, "unsupported_media_type") in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (429, "rate_limited") in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (503, "capacity_exhausted") in DXF_IMPORT_STATUS_STATE_MATRIX  # DB-082 (b) job cap
    assert (503, "deadline_exceeded") in DXF_IMPORT_STATUS_STATE_MATRIX
    assert (500, "internal_error") in DXF_IMPORT_STATUS_STATE_MATRIX  # G3 A6


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


def test_upload_exactly_at_ceiling_accepted_plus_one_refused(client):
    # G4 A3: the ceiling is a strict '>' - exactly MAX_BODY_BYTES is ACCEPTED (passes the
    # ceiling through to the reader, here a 422), and MAX_BODY_BYTES + 1 is refused 413. Guards
    # against a '>=' off-by-one that would (safely) refuse the boundary too.
    prefix = b"0\r\nSECTION\r\n"
    at_limit = prefix + b"9" * (MAX_BODY_BYTES - len(prefix))
    assert len(at_limit) == MAX_BODY_BYTES
    resp = client.post(_CAND_URL, content=at_limit, headers=_DXF_HEADERS)
    assert resp.status_code != 413  # the ceiling accepts exactly MAX_BODY_BYTES
    assert _pair(resp) == (422, "validation_error")  # reached the reader, refused there
    over = at_limit + b"9"
    resp_over = client.post(_CAND_URL, content=over, headers=_DXF_HEADERS)
    assert _pair(resp_over) == (413, "payload_too_large")


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
    limiter = mod.get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 1)
    limiter.reset()
    first = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    second = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert first.status_code == 200
    assert _pair(second) == (429, "rate_limited")


def test_mutation_rate_limit_guard(client, monkeypatch):
    # Raise the limit far above the request count -> the later requests no longer 429,
    # proving the limiter drives the refusal (AS-1 c).
    limiter = mod.get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 1000)
    limiter.reset()
    for _ in range(3):
        resp = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert resp.status_code == 200  # reddens test_rate_limit_429


def test_draft_rate_limit_precedes_parameter_parse(client, monkeypatch):
    """DB-081 (b): an over-limit caller hitting /draft with a MALFORMED parameter gets the 429,
    never a 422 ahead of the limiter. Load-bearing: admitting the caller lets the SAME malformed
    parameter reach the parser (422), proving the rate limit precedes the parameter parse."""
    limiter = mod.get_rate_limiter()
    bad = "?building_outline=0&floors=notanumber&floor_to_floor_ft=11&author=J"

    monkeypatch.setattr(limiter, "max_requests", 0)  # refuse every caller
    limiter.reset()
    resp = client.post(_DRAFT_URL + bad, content=_dxf(), headers=_DXF_HEADERS)
    assert _pair(resp) == (429, "rate_limited")  # the limiter fired before the param parse

    monkeypatch.setattr(limiter, "max_requests", 1000)  # admit the caller
    limiter.reset()
    resp2 = client.post(_DRAFT_URL + bad, content=_dxf(), headers=_DXF_HEADERS)
    assert _pair(resp2) == (422, "validation_error")  # now the malformed param is parsed


# --------------------------------------------------------------------------- AS-5 job cap


def test_503_capacity_exhausted_and_its_reddening_mutation(client, monkeypatch):
    """AS-5 / DB-082 (b): when the bounded in-flight job cap is full, a new read job is refused
    with a typed (503, capacity_exhausted). Mutation: restoring capacity lets the SAME request
    complete (200), proving the cap is load-bearing."""
    slots = mod.get_job_slots()
    monkeypatch.setattr(slots, "max_slots", 0)  # every slot is 'taken' -> refuse
    slots.reset()
    resp = client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS)
    assert _pair(resp) == (503, "capacity_exhausted")
    assert _pair(resp) in DXF_IMPORT_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")

    monkeypatch.setattr(slots, "max_slots", 16)
    slots.reset()
    assert client.post(_CAND_URL, content=_dxf(), headers=_DXF_HEADERS).status_code == 200


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


def test_draft_uses_the_user_assigned_ring(client):
    # G4 F1 at the route: two distinct in-bounds rings + building_outline=1 -> the draft is
    # built from ring B (the SECOND ring), proving the route honours the user's assignment.
    q = (
        "?building_outline=1&floors=5&floor_to_floor_ft=11&author=Jane"
        "&confirmed_units=us_survey_feet"
    )
    resp = client.post(
        _DRAFT_URL + q,
        content=_dxf(rings=((_RING_A, "A", True), (_RING_B, "B", True))),
        headers=_DXF_HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["proposed_massing"]["outline"]["vertices"][0] == [990000.0, 200000.0]


# --------------------------------------------------------------------------- G5 MEDIUM 1 overflow


def test_overflow_coordinates_typed_4xx_never_500(client):
    # G5 MEDIUM 1: huge-but-finite coordinates overflow the measured dimensions to inf; the
    # route must return a TYPED 4xx with a correlation id, never a bare untyped 500.
    resp = client.post(
        _CAND_URL, content=_dxf(rings=((_OVERFLOW_RING, "B", True),)), headers=_DXF_HEADERS
    )
    assert resp.status_code != 500
    assert _pair(resp) == (422, "validation_error")
    assert resp.headers.get("X-Correlation-ID")


def test_non_finite_body_becomes_typed_500_with_correlation_id(client, monkeypatch):
    # G5 MEDIUM 1 defense in depth: disable the SERVICE finiteness guard so a real overflow (inf)
    # reaches the response body; the route's pre-render guard must convert it to a TYPED
    # (500, internal_error) WITH a correlation id, never a bare Starlette 500.
    monkeypatch.setattr(svc_mod, "_measured_is_finite", lambda measured: True)
    resp = client.post(
        _CAND_URL, content=_dxf(rings=((_OVERFLOW_RING, "B", True),)), headers=_DXF_HEADERS
    )
    assert _pair(resp) == (500, "internal_error")
    assert resp.headers.get("X-Correlation-ID")


def test_mutation_pre_render_finiteness_guard(client, monkeypatch):
    # Neuter BOTH the service guard and the route's pre-render guard -> the non-finite body
    # reaches Starlette's allow_nan=False render and becomes a BARE untyped 500 with NO
    # correlation id, proving the pre-render guard is what makes it typed (G5 MEDIUM 1).
    monkeypatch.setattr(svc_mod, "_measured_is_finite", lambda measured: True)
    monkeypatch.setattr(mod, "_guard_finite_response", lambda body, correlation_id: None)
    resp = client.post(
        _CAND_URL, content=_dxf(rings=((_OVERFLOW_RING, "B", True),)), headers=_DXF_HEADERS
    )
    assert resp.status_code == 500  # reddens test_non_finite_body_becomes_typed_500...
    assert "X-Correlation-ID" not in resp.headers  # bare Starlette 500, untyped


# --------------------------------------------------------------------------- DB-081 (e) encode step


def test_pre_render_guard_catches_a_non_encodable_string():
    """DB-081 (e): the pre-render guard's utf-8 encode step (now ALIGNED with the sibling routes)
    catches a non-encodable string - an unpaired surrogate - that ``json.dumps`` alone would pass,
    returning a typed (500, internal_error) rather than a bare Starlette 500. It still catches a
    non-finite float. A safe body returns None. Mutation (drop the .encode step): the surrogate
    slips through and the guard returns None - recorded red in the report."""
    cid = "cid-test"
    surrogate_body = {"x": "\ud800"}  # json.dumps succeeds; .encode('utf-8') raises
    resp = mod._guard_finite_response(surrogate_body, cid)
    assert resp is not None and resp.status_code == 500

    nan_body = {"x": float("nan")}  # allow_nan=False still catches NaN
    resp_nan = mod._guard_finite_response(nan_body, cid)
    assert resp_nan is not None and resp_nan.status_code == 500

    assert mod._guard_finite_response({"x": 1.0, "ok": "ascii"}, cid) is None  # safe body
