"""Acceptance pack for POST /api/v1/export - the UNMOUNTED CAD/3D export route (M5-T109 + T111).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted, route-free
:func:`app.cad.export_service.build_export`; it ships UNMOUNTED (app/main.py is NOT touched), so
every test mounts the router on a FRESH ``FastAPI()`` via ``TestClient`` (the accepted M5-T059 /
max_envelope_api pattern) and one test asserts the path is ABSENT from the real app's OpenAPI.

AS-4 (route discipline): absent from OpenAPI; flag off -> the same generic 404 as an unmounted
path for EVERY method; bounded request bytes (413); per-format media types on a 200 FILE; a
server-generated X-Correlation-ID; the writer runs off the event loop in a cancellable job with a
per-request deadline (503) behind the ONE shared per-caller rate limiter (429) and a bounded
in-flight job cap (503 capacity); typed refusals are JSON, never a partial file. DB-075 (b): a
pathological-but-bounded caller input returns the reconciled typed refusal through the REAL route.

M5-T111 riders proven here (the shared-limiter properties live in
tests/resilience/test_rate_limit.py): AS-1 the route uses the shared limiter only; AS-4 the
limiter runs before body parse; AS-5 the bounded job cap yields a typed 503; AS-6 every method
404 while disabled + OpenAPI absence on a throwaway app that includes the router.
"""

from __future__ import annotations

import ast
import inspect
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import export_api as mod
from app.api.v1.export_api import EXPORT_MAX_BODY_BYTES, EXPORT_STATUS_STATE_MATRIX, router
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
    """A client over a fresh app with the flag ON and freshly reset shared limiter + slots."""
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")
    mod.get_rate_limiter().reset()
    mod.get_job_slots().reset()
    with TestClient(mounted_app, raise_server_exceptions=False) as test_client:
        yield test_client
    mod.get_rate_limiter().reset()
    mod.get_job_slots().reset()


# --------------------------------------------------------------------------- #
# AS-4 / AS-6: unmounted + flag gating + every-method 404 + OpenAPI absence.
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


def test_every_method_is_a_generic_404_while_disabled(mounted_app, monkeypatch):
    """DB-081 (d): with the flag off, GET/POST/PUT/PATCH/DELETE and also HEAD/OPTIONS all return
    the generic 404 byte-identical to an unmounted path - no 405 that would leak the route's
    existence (every method in _ROUTE_METHODS is covered; G3 A1 / G4 gap 3)."""
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as c:
        for method in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            resp = c.request(method, _URL)
            assert resp.status_code == 404, method
            assert "X-Correlation-ID" not in resp.headers, method
            if method == "HEAD":
                assert resp.content == b"", method  # HEAD carries no body
            else:
                assert resp.json() == {"detail": "Not Found"}, method


def test_enabled_non_post_method_is_a_real_405(client):
    """When ENABLED, a non-POST method is a genuine 405 (only POST does work)."""
    resp = client.get(_URL)
    assert resp.status_code == 405
    assert _pair(resp) == (405, None)
    assert _pair(resp) in EXPORT_STATUS_STATE_MATRIX


def test_no_path_in_the_throwaway_app_openapi(mounted_app):
    """AS-6 / DB-082 (d): the router IS included on this throwaway app, yet
    include_in_schema=False keeps the export path out of its OpenAPI document."""
    schema_paths = mounted_app.openapi().get("paths", {})
    assert _URL not in schema_paths
    assert not any(p.startswith("/api/v1/export") for p in schema_paths)


#: Names of MUTABLE constructors a route-local limiter would use for its state table. Includes
#: ``Counter``/``set``/``list`` (DB-088 (e)) on top of the original dict/deque family; ``frozenset``
#: is deliberately EXCLUDED - it is immutable and is the legitimate shape of the route modules'
#: *_STATUS_STATE_MATRIX and _TRUE_TOKENS constants (never a limiter's mutable state).
_LIMITER_CONTAINER_CALLS = frozenset(
    {"dict", "defaultdict", "OrderedDict", "deque", "Counter", "set", "list"}
)


def _module_level_limiter_containers(src: str) -> list[str]:
    """AST guard (G3 A2 / G4 gap 4 / DB-088 (e)): return the target names of any MODULE-LEVEL
    assignment whose value is the shape a reintroduced route-local limiter would take - a dict or
    set literal, an EMPTY list literal (``[]``, the empty-state shape; a *non-empty* constant list
    such as ``__all__``/``_ROUTE_METHODS`` is left alone), or a ``dict``/``defaultdict``/
    ``OrderedDict``/``deque``/``Counter``/``set``/``list`` construction (the plain-dict AND the
    list/set/Counter forms the substring scan missed). The shared limiter keeps ALL such state
    inside app.resilience.rate_limit, so a hardened route module must have NONE. ``frozenset``
    constants (the status matrices, _TRUE_TOKENS) are immutable and are NOT flagged."""
    found: list[str] = []
    for node in ast.parse(src).body:  # module scope only
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        # dict/set literals are always mutable state; an EMPTY list literal is empty limiter state
        # (a non-empty list literal is a constant like __all__/_ROUTE_METHODS and is left alone).
        is_container = isinstance(value, (ast.Dict, ast.Set))
        if isinstance(value, ast.List) and not value.elts:
            is_container = True
        if isinstance(value, ast.Call):
            fn = value.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None)
            is_container = is_container or name in _LIMITER_CONTAINER_CALLS
        if is_container:
            found += [t.id for t in targets if isinstance(t, ast.Name)]
    return found


def test_ast_guard_also_catches_list_set_counter_limiters():
    """DB-088 (e): the AST no-local-limiter guard catches a module-level list / set / Counter
    limiter (not only the dict/deque family), while the route modules' legitimate constants
    (non-empty list literals, frozenset matrices) are NOT flagged. Mutation (the OLD guard,
    dict/deque only): the list/set/Counter cases return [] and this reddens - recorded."""
    assert _module_level_limiter_containers("_log = []\n") == ["_log"]
    assert _module_level_limiter_containers("_log = list()\n") == ["_log"]
    assert _module_level_limiter_containers("_seen = set()\n") == ["_seen"]
    assert _module_level_limiter_containers("_seen = {'a'}\n") == ["_seen"]
    assert _module_level_limiter_containers("_c = Counter()\n") == ["_c"]
    assert _module_level_limiter_containers(
        "import collections\n_c = collections.Counter()\n"
    ) == ["_c"]
    assert _module_level_limiter_containers("__all__ = ['a', 'b']\n") == []
    assert _module_level_limiter_containers("_ROUTE_METHODS = ['GET', 'POST']\n") == []
    assert _module_level_limiter_containers("_M = frozenset({(1, 2)})\n") == []


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
    resp = client.post(_URL, content=b"x" * (EXPORT_MAX_BODY_BYTES + 1), headers=_JSON_HEADERS)
    assert _pair(resp) == (413, "payload_too_large")
    assert _pair(resp) in EXPORT_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")


def _maximal_export_body() -> dict:
    """An export request at the writer contract caps: two rings at the DXF ring cap
    (export_service._FORMAT_RING_CAP['dxf'] = 10,000 vertices) plus MAX_FLOORS (2,000) floor
    heights. Maximal in SIZE; the geometry is a self-touching zig so the writer refuses it - the
    ceiling's contract is the SIZE gate; a legitimate 200 is the per-format file test."""
    ring = [[985000.0 + i * 0.5, 195000.0 + i * 0.5] for i in range(10000)]
    return {"format": "dxf", "source": "proposed", "lot_ring": ring, "building_ring": ring,
            "floor_heights": [10.0] * 2000, "address": "A" * 120, "bbl": "1-00123-0045",
            "generated_at": "2026-09-24T00:00:00Z", "generator_version": "site-plan-writer/1.0.0"}


def test_ceiling_admits_the_contract_maximal_export_request():
    """AS-1: the ceiling is sized to admit the contract-maximal export and the OLD shared 256 KiB
    ceiling would refuse it. A maximal-at-caps body serializes to well over 256 KiB yet at or under
    the new ceiling. Mutation (the old 256 KiB constant): the ceiling would refuse this legitimate
    maximum (413) before the writer's own vertex cap - recorded."""
    import json

    body = _maximal_export_body()
    size = len(json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8"))
    assert size > 256 * 1024  # the OLD shared 256 KiB ceiling would WRONGLY refuse this
    assert size <= EXPORT_MAX_BODY_BYTES  # the NEW route ceiling admits it


def test_maximal_sized_export_body_is_admitted_past_the_ceiling(client):
    """AS-1: a body at the maximal legitimate SIZE is admitted PAST the 413 size gate through the
    real route (it reaches the writer; the geometry then yields a typed refusal, but NEVER a 413).
    Mutation (set the ceiling back to 256 KiB): this body would 413 - recorded."""
    resp = client.post(_URL, json=_maximal_export_body())
    assert resp.status_code != 413  # admitted past the size ceiling
    assert _pair(resp) in EXPORT_STATUS_STATE_MATRIX


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
# AS-4: per-caller rate limit (429), limit-before-parse, deadline (503), capacity (503).
# --------------------------------------------------------------------------- #

def test_429_per_caller_rate_limit(client, monkeypatch):
    """The shared per-caller limiter refuses over-budget requests. Mutation (mutate the CONSUMING
    namespace - the live limiter): a large max_requests removes the 429."""
    limiter = mod.get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 2)
    limiter.reset()
    assert client.post(_URL, json=_body()).status_code == 200
    assert client.post(_URL, json=_body()).status_code == 200
    limited = client.post(_URL, json=_body())
    assert _pair(limited) == (429, "rate_limited")
    assert _pair(limited) in EXPORT_STATUS_STATE_MATRIX
    assert limited.headers.get("X-Correlation-ID")

    monkeypatch.setattr(limiter, "max_requests", 1000)
    limiter.reset()
    assert [client.post(_URL, json=_body()).status_code for _ in range(4)] == [200] * 4


def test_limiter_runs_before_body_parse(client, monkeypatch):
    """AS-4 / DB-081 (b) analogue: the limiter refuses BEFORE the body is read - an over-limit
    caller with a malformed body gets the 429, never a 422. Load-bearing: admitting the same
    caller lets the SAME malformed body reach the parser (422) and trips the body-read tripwire."""
    limiter = mod.get_rate_limiter()
    real = mod._read_body_within_ceiling
    seen = {"read": False}

    async def _tripwire(stream, max_bytes):
        seen["read"] = True
        return await real(stream, max_bytes)

    monkeypatch.setattr(mod, "_read_body_within_ceiling", _tripwire)

    monkeypatch.setattr(limiter, "max_requests", 0)  # refuse every caller
    limiter.reset()
    resp = client.post(_URL, content=b"not json at all", headers=_JSON_HEADERS)
    assert _pair(resp) == (429, "rate_limited")
    assert seen["read"] is False  # the body was NOT read (the limiter precedes the parse)

    monkeypatch.setattr(limiter, "max_requests", 1000)  # admit the caller
    limiter.reset()
    seen["read"] = False
    resp2 = client.post(_URL, content=b"not json at all", headers=_JSON_HEADERS)
    assert _pair(resp2) == (422, "validation_error")
    assert seen["read"] is True


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


def test_503_capacity_exhausted_and_its_reddening_mutation(client, monkeypatch):
    """AS-5 / DB-082 (b): when the bounded in-flight job cap is full, a new job is refused with a
    typed (503, capacity_exhausted). Mutation: restoring capacity lets the SAME request complete
    (200), proving the cap is load-bearing."""
    slots = mod.get_job_slots()
    monkeypatch.setattr(slots, "max_slots", 0)  # every slot is 'taken' -> refuse
    slots.reset()
    resp = client.post(_URL, json=_body())
    assert _pair(resp) == (503, "capacity_exhausted")
    assert _pair(resp) in EXPORT_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")

    monkeypatch.setattr(slots, "max_slots", 16)
    slots.reset()
    assert client.post(_URL, json=_body()).status_code == 200


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
