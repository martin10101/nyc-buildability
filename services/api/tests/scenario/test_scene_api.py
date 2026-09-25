"""Acceptance pack for POST /api/v1/scene (task M5-T107 + M5-T111 route-hardening riders).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted scene
assembler; it ships UNMOUNTED (app/main.py is NOT touched), so every test mounts the router on
a FRESH ``FastAPI()`` via ``TestClient`` (the accepted M5-T059 / max_envelope_api pattern) and
one test asserts the route is ABSENT from the real app. It is feature-flag gated OFF by default
(reuses ``INTERNAL_RULE_EVAL_ENABLED``). The context connector is injected as an OFFLINE fake so
nothing touches the network.

AS-4 (route, unmounted): absent from OpenAPI; flag-off generic 404 for EVERY method; bounded
request bytes; the assembly runs off the event loop in a cancellable job with a per-request
deadline, a bounded in-flight job cap and the ONE shared per-caller rate limiter (each with a
reddening mutation); typed refusals; a server correlation id.
AS-6 (scope): zero new dependencies; app/main.py untouched.

M5-T111 riders proven here (the shared-limiter properties themselves live in
tests/resilience/test_rate_limit.py): AS-1 the route uses the shared limiter only; AS-4 the
limiter runs before body parse; AS-5 the bounded job cap yields a typed 503; AS-6 every method
404 while disabled + OpenAPI absence on a throwaway app that includes the router.
"""

from __future__ import annotations

import ast
import inspect
import logging
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import scene_api as mod
from app.api.v1.scene_api import SCENE_MAX_BODY_BYTES, SCENE_STATUS_STATE_MATRIX, router
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.building_footprints_arcgis import (
    ContextBuilding,
    ContextBuildingsResult,
    FootprintRefusal,
)
from app.connectors.building_footprints_geometry import FootprintPart

_URL = "/api/v1/scene"
_JSON_HEADERS = {"content-type": "application/json"}

_LOT_RING = [[1000000.0, 200000.0], [1000100.0, 200000.0],
             [1000100.0, 200120.0], [1000000.0, 200120.0]]
_RECT = [[1000010.0, 200010.0], [1000050.0, 200010.0],
         [1000050.0, 200070.0], [1000010.0, 200070.0]]
_PM = {
    "outline": {"srid": 2263, "vertices": _RECT + [_RECT[0]]},
    "levels": [{"level_index": 0, "floor_count": 2, "floor_to_floor_ft": 12.0}],
    "exterior_walls": [{"id": f"W{i}", "start_vertex_index": i, "end_vertex_index": (i + 1) % 4}
                       for i in range(4)],
    "provenance": {"author": "a", "editor_version": "v", "kind": "proposed"},
}
_CONTEXT = {"envelope": [1020160, 267240, 1020230, 267325], "site_ground_elevation_ft": 200.0}


def _ok_result(buildings=None, **_kwargs) -> ContextBuildingsResult:
    return ContextBuildingsResult(
        status="ok", buildings=buildings or [], refusal=None, correlation_id="cid",
        query={"kind": "envelope"}, site_ground_elevation_ft=200.0, subject_bbl=None,
        metadata_request_url="u/meta", metadata_raw_digest="sha256:m", request_urls=["u/p1"],
        raw_digests=["sha256:p1"], retrieved_at="2026-09-24T12:00:00Z",
        source_data_last_edited_ms=1, source_data_last_edited="2026-09-20T02:16:01Z",
        pages_fetched=1, drift_signals=[])


def _one_building() -> ContextBuilding:
    part = FootprintPart(exterior=[[1020160.0, 267240.0], [1020230.0, 267240.0],
                                   [1020230.0, 267325.0], [1020160.0, 267325.0],
                                   [1020160.0, 267240.0]], holes=[], area_sq_ft=5950.0)
    return ContextBuilding(
        object_id=1, doitt_id=1, bin=2000001, base_bbl="1", mappluto_bbl="1",
        joins_subject_lot=None, feature_code=2100, feature_code_label="Building",
        height_roof_ft=40.0, ground_elevation_ft=190.0, relative_base_z_ft=-10.0,
        relative_roof_z_ft=30.0, construction_year=1930, geom_source="Photogrammetric",
        last_edited="2020-01-01T00:00:00Z", last_status_type="Constructed",
        geometry_status="valid", geometry_findings=[], parts=[part], footprint_area_sq_ft=5950.0,
        query_relation="within", query_overlap_area_sq_ft=5950.0, flags=[], gaps=[],
        attributes={"OBJECTID": 1}, original_geometry={"rings": []},
        original_geometry_digest="sha256:x")


def _fetch_ok(**kwargs):
    return _ok_result([_one_building()])


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


def _body(**overrides) -> dict:
    body = {"lot_ring": _LOT_RING, "proposed_massing": _PM, "context": dict(_CONTEXT)}
    body.update(overrides)
    return body


def _pair(response) -> tuple[int, str | None]:
    try:
        state = response.json().get("state")
    except ValueError:  # pragma: no cover
        state = None
    return response.status_code, state


@pytest.fixture(autouse=True)
def _reset_shared_state():
    mod.get_rate_limiter().reset()
    mod.get_job_slots().reset()
    yield
    mod.get_rate_limiter().reset()
    mod.get_job_slots().reset()


@pytest.fixture
def mounted_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(mounted_app, monkeypatch):
    _enable(monkeypatch)
    monkeypatch.setattr(mod, "get_context_buildings_fetch", lambda: _fetch_ok)
    with TestClient(mounted_app, raise_server_exceptions=False) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# AS-4: the happy path.
# ---------------------------------------------------------------------------


def test_200_returns_the_scene(client):
    resp = client.post(_URL, json=_body())
    assert resp.status_code == 200
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")
    doc = resp.json()
    assert doc["scene_version"] == "scene-1.0.0"
    assert doc["source"] == "proposed"
    assert doc["disclosure"] == "Proposed - not a city record"
    assert doc["vertical_unit"] == "us_survey_foot"
    assert "context_buildings" in doc and doc["context_buildings"]["status"] == "ok"
    assert len(doc["context_buildings"]["buildings"]) == 1
    assert doc["correlation_id"] == resp.headers["X-Correlation-ID"]


def test_200_context_refusal_is_disclosed_never_dropped(client, monkeypatch):
    refusal = FootprintRefusal(
        error_type="upstream_error", message="down", correlation_id="cid", detail={"url": "u"},
        request_url="u/p1", retrieved_at="2026-09-24T12:00:00Z", raw_digest="sha256:z")

    def _fetch_refused(**kwargs):
        return ContextBuildingsResult(
            status="refused", buildings=[], refusal=refusal, correlation_id="cid",
            query=None, site_ground_elevation_ft=None, subject_bbl=None,
            metadata_request_url=None, metadata_raw_digest=None, request_urls=[], raw_digests=[],
            retrieved_at="2026-09-24T12:00:00Z", source_data_last_edited_ms=None,
            source_data_last_edited=None, pages_fetched=0, drift_signals=[])

    monkeypatch.setattr(mod, "get_context_buildings_fetch", lambda: _fetch_refused)
    resp = client.post(_URL, json=_body())
    assert resp.status_code == 200
    layer = resp.json()["context_buildings"]
    assert layer["status"] == "refused" and layer["buildings"] == []
    assert layer["refusal"]["error_type"] == "upstream_error"


def test_200_without_context_is_a_scene_with_no_context_query(client):
    resp = client.post(_URL, json=_body(context={}))
    assert resp.status_code == 200
    assert resp.json()["context_buildings"]["status"] == "not_requested"


# ---------------------------------------------------------------------------
# AS-4 / AS-6: flag off + UNMOUNTED + every-method 404 + OpenAPI absence.
# ---------------------------------------------------------------------------


def test_flag_off_is_a_generic_404(mounted_app, monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as client:
        resp = client.post(_URL, json=_body())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX


def test_every_method_is_a_generic_404_while_disabled(mounted_app, monkeypatch):
    """DB-081 (d): with the flag off, GET/POST/PUT/PATCH/DELETE and also HEAD/OPTIONS all return
    the generic 404 byte-identical to an unmounted path - no 405 that would leak the route's
    existence (every method in _ROUTE_METHODS is covered; G3 A1 / G4 gap 3)."""
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as client:
        for method in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            resp = client.request(method, _URL)
            assert resp.status_code == 404, method
            assert "X-Correlation-ID" not in resp.headers, method
            if method == "HEAD":
                assert resp.content == b"", method  # HEAD carries no body
            else:
                assert resp.json() == {"detail": "Not Found"}, method


def test_enabled_non_post_method_is_a_real_405(client):
    """When ENABLED, a non-POST method is a genuine 405 (only POST does work) - proving the
    disabled 404 above is the flag, not a missing route registration."""
    resp = client.get(_URL)
    assert resp.status_code == 405
    assert _pair(resp) == (405, None)
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX


def test_route_is_unmounted_in_the_real_app():
    from app.main import app as real_app

    real_paths = {getattr(route, "path", None) for route in real_app.routes}
    assert _URL not in real_paths
    assert _URL not in real_app.openapi().get("paths", {})


def test_no_path_in_the_throwaway_app_openapi(mounted_app):
    """AS-6 / DB-080 (c): the router IS included on this throwaway app, yet
    include_in_schema=False keeps every scene path out of its OpenAPI document."""
    schema_paths = mounted_app.openapi().get("paths", {})
    assert _URL not in schema_paths
    assert not any(p.startswith("/api/v1/scene") for p in schema_paths)


# ---------------------------------------------------------------------------
# AS-1: the route uses the ONE shared limiter only (no route-local limiter remains).
# ---------------------------------------------------------------------------


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
    limiter (not only the dict/deque family). Each reintroduction shape is flagged, while the
    route modules' legitimate constants (non-empty list literals, frozenset matrices) are NOT.
    Mutation (the OLD guard, dict/deque only): the list/set/Counter cases return [] and this
    reddens - recorded in the report."""
    # Reintroduction shapes a list/set/Counter limiter would take -> all flagged.
    assert _module_level_limiter_containers("_log = []\n") == ["_log"]
    assert _module_level_limiter_containers("_log = list()\n") == ["_log"]
    assert _module_level_limiter_containers("_seen = set()\n") == ["_seen"]
    assert _module_level_limiter_containers("_seen = {'a'}\n") == ["_seen"]
    assert _module_level_limiter_containers("_c = Counter()\n") == ["_c"]
    assert _module_level_limiter_containers(
        "import collections\n_c = collections.Counter()\n"
    ) == ["_c"]
    # Legitimate constants the route modules actually use -> NOT flagged (no false positive).
    assert _module_level_limiter_containers("__all__ = ['a', 'b']\n") == []
    assert _module_level_limiter_containers("_ROUTE_METHODS = ['GET', 'POST']\n") == []
    assert _module_level_limiter_containers("_M = frozenset({(1, 2)})\n") == []


def test_route_uses_the_shared_limiter_and_slots_only():
    """AS-1: the shared limiter/slot classes back this route and no route-local limiter class,
    dict or deque survives. An AST guard over the module source is the reddening check: a
    reintroduced local limiter (a class, a module-level ``dict``/``defaultdict``/``OrderedDict``/
    ``deque``, or the old ``_rate_state`` dict) reddens it."""
    from app.resilience.rate_limit import JobSlots, SlidingWindowRateLimiter

    assert isinstance(mod.get_rate_limiter(), SlidingWindowRateLimiter)
    assert isinstance(mod.get_job_slots(), JobSlots)
    assert not hasattr(mod, "_RateLimiter")
    assert not hasattr(mod, "_rate_state")
    src = inspect.getsource(mod)
    assert "class _RateLimiter" not in src
    assert "deque" not in src and "OrderedDict" not in src and "_rate_state" not in src
    # AST guard: NO module-level dict/defaultdict/OrderedDict/deque limiter container (catches a
    # plain dict the substring scan above cannot).
    assert _module_level_limiter_containers(src) == []


# ---------------------------------------------------------------------------
# AS-4: bounded body, malformed body, typed refusals.
# ---------------------------------------------------------------------------


def test_413_oversized_body(client):
    resp = client.post(_URL, content=b"x" * (SCENE_MAX_BODY_BYTES + 1), headers=_JSON_HEADERS)
    assert _pair(resp) == (413, "payload_too_large")
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX


def _maximal_scene_body() -> dict:
    """A scene request at the proposed_massing contract caps (app.scenario.proposal): 20,000 total
    outline positions (footprint 1,000 + 500 levels x 38), 4,000 exterior walls and a lot_ring at
    MAX_OUTLINE_VERTICES (1,000). Structurally maximal in SIZE (the geometry is degenerate, so the
    assembler will refuse it - the ceiling's contract is the SIZE gate, tested here; a legitimate
    non-degenerate request is the happy-path 200 test)."""
    foot = 1000
    n_levels = 500
    per_level = (20000 - foot) // n_levels  # 38
    foot_ring = [[1000000.0 + i, 200000.0 + i] for i in range(foot)]
    levels = [
        {"level_index": li, "floor_count": 1, "floor_to_floor_ft": 12.0,
         "outline": {"srid": 2263, "vertices": [[1000000.0 + j, 200000.0 + j]
                                                 for j in range(per_level)]}}
        for li in range(n_levels)
    ]
    walls = [{"id": f"W{i}", "start_vertex_index": i % foot, "end_vertex_index": (i + 1) % foot}
             for i in range(4000)]
    pm = {"outline": {"srid": 2263, "vertices": foot_ring}, "levels": levels,
          "exterior_walls": walls,
          "provenance": {"author": "a" * 64, "editor_version": "v1.0.0", "kind": "proposed"}}
    lot = [[1000000.0 + i, 200000.0 + i] for i in range(1000)]
    return {"lot_ring": lot, "proposed_massing": pm,
            "context": {"envelope": [1020160, 267240, 1020230, 267325]}}


def test_ceiling_admits_the_contract_maximal_scene_request():
    """AS-1: the ceiling is sized to admit the contract-maximal scene request and the OLD shared
    256 KiB ceiling would refuse it. A maximal-at-caps body serializes to well over 256 KiB yet at
    or under the new ceiling - so it fits the new ceiling but NOT the old one. Mutation (the old
    256 KiB constant): the ceiling would refuse this legitimate maximum (413) - recorded."""
    import json

    body = _maximal_scene_body()
    size = len(json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8"))
    assert size > 256 * 1024  # the OLD shared 256 KiB ceiling would WRONGLY refuse this
    assert size <= SCENE_MAX_BODY_BYTES  # the NEW route ceiling admits it


def test_maximal_sized_scene_body_is_admitted_past_the_ceiling(client):
    """AS-1: a body at the maximal legitimate SIZE is admitted PAST the 413 size gate through the
    real route (it reaches the assembler; the degenerate geometry then yields a typed refusal, but
    NEVER a 413). Mutation (set the ceiling back to 256 KiB): this body would 413 - recorded."""
    resp = client.post(_URL, json=_maximal_scene_body())
    assert resp.status_code != 413  # admitted past the size ceiling
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX


@pytest.mark.parametrize("raw", [b"", b"   ", b"not json", b"[]", b'"a string"'])
def test_422_malformed_body(client, raw):
    resp = client.post(_URL, content=raw, headers=_JSON_HEADERS)
    assert _pair(resp) == (422, "validation_error")


def test_422_nan_is_refused(client):
    resp = client.post(_URL, content=b'{"lot_ring": [[NaN, 0]]}', headers=_JSON_HEADERS)
    assert _pair(resp) == (422, "validation_error")


def test_422_missing_lot_ring(client):
    resp = client.post(_URL, json={"proposed_massing": _PM})
    assert resp.status_code == 422
    assert resp.json()["field"] == "lot_ring"


def test_422_exactly_one_of_proposed_or_generated(client):
    both = client.post(_URL, json=_body(generated_option={"candidate": _PM}))
    assert both.status_code == 422
    assert both.json()["field"] == "proposed_massing"
    neither = client.post(_URL, json={"lot_ring": _LOT_RING})
    assert neither.status_code == 422


def test_422_typed_scene_assembly_refusal_names_the_field(client):
    """A non-numeric lot-ring coordinate is a typed SceneAssemblyError -> bounded 422 naming the
    field (DB-054 (o)); never a 500, never a fabricated scene."""
    resp = client.post(_URL, json=_body(lot_ring=[["abc", "0"], [1, 0], [1, 1], [0, 1]]))
    assert resp.status_code == 422
    assert _pair(resp) == (422, "validation_error")
    assert resp.json()["field"] == "lot_ring[0]"
    assert resp.headers.get("X-Correlation-ID")


def test_bad_field_is_bounded(client):
    resp = client.post(_URL, json=_body(lot_ring=[["x" * 5000, "0"], [1, 0], [1, 1], [0, 1]]))
    assert resp.status_code == 422
    assert len(resp.json()["message"]) < 1000


def test_422_huge_int_coordinate_is_typed_not_a_500(client):
    """G5 F-1: a JSON integer coordinate beyond float range (10**400) is a typed 422
    (unparseable_coordinate) naming the field, never an untyped OverflowError -> 500."""
    resp = client.post(_URL, json=_body(lot_ring=[[10**400, 0], [1, 0], [1, 1], [0, 1]]))
    assert _pair(resp) == (422, "validation_error")
    assert resp.json()["field"] == "lot_ring[0]"
    assert resp.headers.get("X-Correlation-ID")


def test_422_non_dict_context_is_refused_typed(client):
    """G3 A4: a non-dict `context` is a caller-side request fault -> typed 422 naming the field,
    not a silently ignored no-context (which would mask the caller's mistake)."""
    for bad in ("not-an-object", [1, 2], 5):
        resp = client.post(_URL, json=_body(context=bad))
        assert _pair(resp) == (422, "validation_error"), bad
        assert resp.json()["field"] == "context"
    # An ABSENT/null context is still honest no-context (200, not_requested).
    resp = client.post(_URL, json=_body(context=None))
    assert resp.status_code == 200
    assert resp.json()["context_buildings"]["status"] == "not_requested"


# ---------------------------------------------------------------------------
# AS-4: the per-caller rate limit (shared limiter) + reddening mutation.
# ---------------------------------------------------------------------------


def test_429_rate_limit_and_its_reddening_mutation(client, monkeypatch):
    """The shared per-caller limiter refuses over-budget requests with a typed 429. Mutation
    (mutate the CONSUMING namespace - the live limiter): raising max_requests far above the
    request count removes the 429 entirely, proving the limit is load-bearing."""
    limiter = mod.get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 2)
    limiter.reset()
    statuses = [client.post(_URL, json=_body()).status_code for _ in range(3)]
    assert statuses == [200, 200, 429]
    assert _pair(client.post(_URL, json=_body())) == (429, "rate_limited")

    monkeypatch.setattr(limiter, "max_requests", 1000)
    limiter.reset()
    assert [client.post(_URL, json=_body()).status_code for _ in range(4)] == [200] * 4


def test_limiter_runs_before_body_parse(client, monkeypatch):
    """AS-4 / DB-081 (b) analogue: the limiter refuses BEFORE the body is read - an over-limit
    caller with a malformed body gets the 429, never a 422. Load-bearing: admitting the same
    caller lets the SAME malformed body reach the parser (422) and trips the body-read tripwire,
    proving the ordering."""
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


# ---------------------------------------------------------------------------
# AS-5: the bounded in-flight job cap yields a typed 503 + reddening mutation.
# ---------------------------------------------------------------------------


def test_503_capacity_exhausted_and_its_reddening_mutation(client, monkeypatch):
    """AS-5 / DB-082 (b): when the bounded in-flight job cap is full, a new job is refused with a
    typed (503, capacity_exhausted) rather than starting unbounded work. Mutation: restoring
    capacity lets the SAME request complete (200), proving the cap is load-bearing."""
    slots = mod.get_job_slots()
    monkeypatch.setattr(slots, "max_slots", 0)  # every slot is 'taken' -> refuse
    slots.reset()
    resp = client.post(_URL, json=_body())
    assert _pair(resp) == (503, "capacity_exhausted")
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")

    monkeypatch.setattr(slots, "max_slots", 16)
    slots.reset()
    assert client.post(_URL, json=_body()).status_code == 200


# ---------------------------------------------------------------------------
# AS-4: the per-request wall-clock deadline (DB-061 (i)) + a reddening mutation.
# ---------------------------------------------------------------------------


def test_504_deadline_and_its_reddening_mutation(client, monkeypatch):
    """A slow assembly is cancelled at the per-request wall-clock deadline with a typed 504 - no
    partial scene. In-process mutation: with a generous deadline the SAME slow fetch returns 200,
    proving the deadline (run_in_job_slot over run_in_threadpool) is load-bearing."""
    def _slow_fetch(**kwargs):
        time.sleep(0.3)
        return _ok_result([_one_building()])

    monkeypatch.setattr(mod, "get_context_buildings_fetch", lambda: _slow_fetch)

    monkeypatch.setattr(mod, "SCENE_MAX_SECONDS", 0.05)
    resp = client.post(_URL, json=_body())
    assert _pair(resp) == (504, "deadline_exceeded")
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")

    # Mutation: a generous deadline lets the same slow work complete (200).
    monkeypatch.setattr(mod, "SCENE_MAX_SECONDS", 30.0)
    mod.get_rate_limiter().reset()
    assert client.post(_URL, json=_body()).status_code == 200


# ---------------------------------------------------------------------------
# AS-3/AS-4: no caller or upstream text reaches a log line (G4 advisory 2).
# ---------------------------------------------------------------------------


def test_no_caller_or_upstream_text_reaches_a_log_line(client, caplog):
    """G4 advisory 2: the route logs ONLY a server correlation id + bounded server-vocabulary field
    names - never caller or upstream text. A refusal carrying a hostile caller string logs the field
    path only, and the hostile string appears in NO log record."""
    hostile = "<script>hostile-caller-text</script>"
    with caplog.at_level(logging.INFO, logger="app.api.v1.scene_api"):
        resp = client.post(_URL, json=_body(lot_ring=[[hostile, "0"], [1, 0], [1, 1], [0, 1]]))
    assert resp.status_code == 422
    messages = [r.getMessage() for r in caplog.records]
    assert messages, "expected the refusal to emit a log line"
    joined = "\n".join(messages)
    assert hostile not in joined and "hostile-caller-text" not in joined
    # What IS logged: the server field vocabulary + the correlation id, nothing caller-derived.
    cid = resp.headers["X-Correlation-ID"]
    assert any("field=lot_ring[0]" in m and cid in m for m in messages)


# ---------------------------------------------------------------------------
# AS-4/AS-6: the (500, "internal_error") matrix pairs are exercised (G4 advisory 4).
# ---------------------------------------------------------------------------


def test_500_assemble_stage_unexpected_error_is_generic(client, monkeypatch):
    """G4 advisory 4: an unexpected (non-typed) error inside the off-loop assembly maps to the
    documented generic (500, internal_error); no exception text reaches the client."""
    def _boom(**kwargs):
        raise RuntimeError("<secret-internal-detail>")

    monkeypatch.setattr(mod, "build_scene_payload", _boom)
    resp = client.post(_URL, json=_body())
    assert _pair(resp) == (500, "internal_error")
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX
    assert resp.headers.get("X-Correlation-ID")
    assert "secret-internal-detail" not in resp.text


def test_500_serialization_unsafe_scene_is_generic(client, monkeypatch):
    """G4 advisory 4: a scene that survives the pre-parse guard but is not strict-JSON serializable
    (a NaN slipping in) maps to the documented (500, internal_error), never a partial/NaN body."""
    def _nan_scene(**kwargs):
        return {"scene_version": "scene-1.0.0", "bad": float("nan")}

    monkeypatch.setattr(mod, "build_scene_payload", _nan_scene)
    resp = client.post(_URL, json=_body())
    assert _pair(resp) == (500, "internal_error")
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX


# ---------------------------------------------------------------------------
# AS-4: the connector is called interactive with a wall-clock deadline (DB-073 (c)).
# ---------------------------------------------------------------------------


def test_connector_is_called_interactive_with_a_deadline(client, monkeypatch):
    seen: dict[str, object] = {}

    def _spy_fetch(**kwargs):
        seen.update(kwargs)
        return _ok_result([])

    monkeypatch.setattr(mod, "get_context_buildings_fetch", lambda: _spy_fetch)
    resp = client.post(_URL, json=_body())
    assert resp.status_code == 200
    assert seen["interactive"] is True
    assert seen["deadline"] is not None and seen["deadline"].tzinfo is not None
    assert seen["correlation_id"] == resp.headers["X-Correlation-ID"]


# ---------------------------------------------------------------------------
# AS-4: a server-generated correlation id on every non-disabled response.
# ---------------------------------------------------------------------------


def test_correlation_id_is_server_generated_and_echoed(client):
    a = client.post(_URL, json=_body())
    b = client.post(_URL, json=_body())
    assert a.headers["X-Correlation-ID"] != b.headers["X-Correlation-ID"]
    assert a.json()["correlation_id"] == a.headers["X-Correlation-ID"]


# ---------------------------------------------------------------------------
# AS-6: scope - the matrix is the single source of truth for every emitted pair.
# ---------------------------------------------------------------------------


def test_every_emitted_pair_is_in_the_matrix(client, monkeypatch):
    seen = set()
    seen.add(_pair(client.post(_URL, json=_body())))                       # 200
    seen.add(_pair(client.post(_URL, content=b"", headers=_JSON_HEADERS)))  # 422
    seen.add(_pair(client.post(_URL, content=b"x" * (SCENE_MAX_BODY_BYTES + 1),
                               headers=_JSON_HEADERS)))                     # 413
    for pair in seen:
        assert pair in SCENE_STATUS_STATE_MATRIX
