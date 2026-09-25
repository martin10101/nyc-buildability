"""Acceptance pack for POST /api/v1/scene (task M5-T107, AS-4, AS-6).

Fully OFFLINE and deterministic. The route is the trust boundary onto the accepted scene
assembler; it ships UNMOUNTED (app/main.py is NOT touched), so every test mounts the router on
a FRESH ``FastAPI()`` via ``TestClient`` (the accepted M5-T059 / max_envelope_api pattern) and
one test asserts the route is ABSENT from the real app. It is feature-flag gated OFF by default
(reuses ``INTERNAL_RULE_EVAL_ENABLED``). The context connector is injected as an OFFLINE fake so
nothing touches the network.

AS-4 (route, unmounted): absent from OpenAPI; flag-off generic 404; bounded request bytes; the
assembly runs off the event loop in a cancellable job with a per-request deadline and a
per-caller rate limit (each with a reddening mutation); typed refusals; a server correlation id.
AS-6 (scope): zero new dependencies; app/main.py untouched.
"""

from __future__ import annotations

import logging
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import scene_api as mod
from app.api.v1.scene_api import MAX_BODY_BYTES, SCENE_STATUS_STATE_MATRIX, router
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
def _reset_rate_limit():
    mod._reset_rate_limit_state()
    yield
    mod._reset_rate_limit_state()


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
# AS-4: flag off + UNMOUNTED.
# ---------------------------------------------------------------------------


def test_flag_off_is_a_generic_404(mounted_app, monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    with TestClient(mounted_app, raise_server_exceptions=False) as client:
        resp = client.post(_URL, json=_body())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers
    assert _pair(resp) in SCENE_STATUS_STATE_MATRIX


def test_route_is_unmounted_in_the_real_app():
    from app.main import app as real_app

    real_paths = {getattr(route, "path", None) for route in real_app.routes}
    assert _URL not in real_paths
    assert _URL not in real_app.openapi().get("paths", {})


# ---------------------------------------------------------------------------
# AS-4: bounded body, malformed body, typed refusals.
# ---------------------------------------------------------------------------


def test_413_oversized_body(client):
    resp = client.post(_URL, content=b"x" * (MAX_BODY_BYTES + 1), headers=_JSON_HEADERS)
    assert _pair(resp) == (413, "payload_too_large")
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
# AS-4: the per-caller rate limit (DB-061 (i)) + a reddening mutation.
# ---------------------------------------------------------------------------


def test_429_rate_limit_and_its_reddening_mutation(client, monkeypatch):
    """The per-caller rate limit refuses over-budget requests with a typed 429. In-process
    mutation (mutate the CONSUMING namespace): raising SCENE_RATE_LIMIT_MAX far above the request
    count removes the 429 entirely - proving the limit is load-bearing."""
    monkeypatch.setattr(mod, "SCENE_RATE_LIMIT_MAX", 2)
    mod._reset_rate_limit_state()
    statuses = [client.post(_URL, json=_body()).status_code for _ in range(3)]
    assert statuses == [200, 200, 429]
    assert _pair(client.post(_URL, json=_body())) == (429, "rate_limited")

    # Mutation: a large limit lets every request through (no 429).
    monkeypatch.setattr(mod, "SCENE_RATE_LIMIT_MAX", 1000)
    mod._reset_rate_limit_state()
    assert [client.post(_URL, json=_body()).status_code for _ in range(4)] == [200] * 4


# ---------------------------------------------------------------------------
# AS-4: the rate-limit state is MEMORY-BOUNDED (G5 F-3 / G3 A2) + reddening mutations.
# ---------------------------------------------------------------------------


def test_rate_limit_evicts_expired_keys_and_bounds_the_key_count(monkeypatch):
    """G5 F-3 / G3 A2: the sliding-window state evicts a key whose window expired and bounds the
    total tracked-key count, so a spray of distinct callers cannot grow it without bound. In-process
    mutation: raising the key ceiling far above the caller count removes the refusal, proving the
    ceiling is load-bearing. (Unit-level: TestClient gives every request the same host.)"""
    clock = {"t": 1000.0}
    monkeypatch.setattr(mod, "_rate_limit_clock", lambda: clock["t"])
    monkeypatch.setattr(mod, "SCENE_RATE_LIMIT_WINDOW_S", 60.0)
    monkeypatch.setattr(mod, "SCENE_RATE_LIMIT_MAX_KEYS", 3)
    mod._reset_rate_limit_state()

    for host in ("a", "b", "c"):  # three distinct active callers fill the key ceiling
        assert mod._rate_limit_allows(host) is True
    assert len(mod._rate_state) == 3

    # A fourth NEW caller while all windows are active -> the ceiling refuses it (fail-closed);
    # the dict does not grow.
    assert mod._rate_limit_allows("d") is False
    assert len(mod._rate_state) == 3 and "d" not in mod._rate_state

    # Advance past the window: the three windows expire. A new caller triggers the sweep, the
    # expired keys are evicted, and the dict stays bounded.
    clock["t"] += 61.0
    assert mod._rate_limit_allows("d") is True
    assert set(mod._rate_state) == {"d"}

    # Mutation: with a large ceiling the fourth active caller is admitted (no refusal).
    clock["t"] = 5000.0
    monkeypatch.setattr(mod, "SCENE_RATE_LIMIT_MAX_KEYS", 1000)
    mod._reset_rate_limit_state()
    assert [mod._rate_limit_allows(h) for h in ("a", "b", "c", "d")] == [True] * 4
    assert len(mod._rate_state) == 4


def test_rate_limit_evicts_a_single_key_whose_window_emptied(monkeypatch):
    """G5 F-3: a key with no live stamps left is dropped, never kept as a dead entry."""
    clock = {"t": 0.0}
    monkeypatch.setattr(mod, "_rate_limit_clock", lambda: clock["t"])
    monkeypatch.setattr(mod, "SCENE_RATE_LIMIT_WINDOW_S", 10.0)
    mod._reset_rate_limit_state()
    assert mod._rate_limit_allows("solo") is True
    assert mod._rate_state["solo"] == [0.0]
    clock["t"] = 100.0  # the window has expired
    mod._evict_empty_keys(clock["t"], mod.SCENE_RATE_LIMIT_WINDOW_S)
    assert "solo" not in mod._rate_state


# ---------------------------------------------------------------------------
# AS-4: the per-request wall-clock deadline (DB-061 (i)) + a reddening mutation.
# ---------------------------------------------------------------------------


def test_504_deadline_and_its_reddening_mutation(client, monkeypatch):
    """A slow assembly is cancelled at the per-request wall-clock deadline with a typed 504 - no
    partial scene. In-process mutation: with a generous deadline the SAME slow fetch returns 200,
    proving the deadline (asyncio.wait_for over run_in_threadpool) is load-bearing."""
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
    mod._reset_rate_limit_state()
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
    seen.add(_pair(client.post(_URL, content=b"x" * (MAX_BODY_BYTES + 1),
                               headers=_JSON_HEADERS)))                     # 413
    for pair in seen:
        assert pair in SCENE_STATUS_STATE_MATRIX
