"""POST /api/v1/scene - the D-087 PKT-E 3D scene route (UNMOUNTED, flag-gated).

The internal HTTP seam onto the accepted scene assembler
(:func:`app.scenario.scene_assembler.build_scene_payload`). Given a caller lot ring plus a
proposed-massing block (or a generated option) and an optional context-building query, it
builds the renderer-agnostic scene payload of the plan's section 2.1 - the massing truth
object plus the official context buildings under one declared vertical datum - and returns
it. It stores nothing and emits no scenario document.

THIS ROUTE SHIPS UNMOUNTED. ``app/main.py`` is NOT touched; the ``include_router`` line
rides the later PKT-H mount seam. Tests mount the router on a fresh ``FastAPI()`` via
``TestClient`` (the accepted M5-T059 / max_envelope_api pattern) and assert it is ABSENT from
the app's OpenAPI.

Route discipline MIRRORS the accepted ``max_envelope_api`` route, reusing its accepted
boundary primitives:

* Posture - feature-flag gated OFF by default (REUSED ``INTERNAL_RULE_EVAL_ENABLED``;
  ``include_in_schema=False``; absent/empty/unknown flag -> a generic 404
  byte-indistinguishable from an unmounted path - the ``lot_geometry.py:100`` sentinel). A
  bounded request body (raw-byte ceiling by BOUNDED STREAMING, reusing the accepted T053
  primitives). No auth change: authn / tenancy / per-user ownership of the supplied geometry
  arrive with the PUBLIC exposure packet (PKT-H), recorded here as a disposition, not
  implemented (the route is unreachable without the internal flag).
* Job safety (DB-061 (i), the M5-T088 G5 fix (b)) - the assembly (the CPU-bound massing build
  + the connector fetch + the assemble) runs OFF the event loop under a per-request wall-clock
  deadline (``asyncio.wait_for`` over ``run_in_threadpool``), and the connector is called
  ``interactive=True`` with a matching wall-clock ``deadline`` so its own paging is bounded too
  (DB-073 (c)). Over the deadline the AWAIT is cancelled and a typed 504 is returned with no
  partial scene reaching the client; the underlying worker thread cannot be force-killed and
  runs to completion in the background, but its total work is independently bounded (the
  connector's own wall-clock deadline + ``interactive`` single-attempt posture + response-byte
  and vertex caps; the massing build is vertex-bounded), so no unbounded work is left running.
  A per-caller RATE LIMIT (in-process, stdlib, memory-bounded) precedes all work.
* Logging - only a SERVER-generated correlation id, the state, and bounded field names reach a
  log line; no caller or upstream text is ever logged (the assembler does not log at all).

The emitted (HTTP status, state) pairs are the single source of truth
:data:`SCENE_STATUS_STATE_MATRIX`; the 200 scene carries NO ``state``.
"""

from __future__ import annotations

import asyncio
import functools
import json
import logging
import time
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.api.v1.proposal_validation import (
    MAX_BODY_BYTES,
    _bounded_message,
    _declared_content_length,
    _read_body_within_ceiling,
)
from app.config import internal_rule_eval_enabled
from app.connectors.building_footprints_arcgis import fetch_context_buildings
from app.scenario.scene_assembler import SceneAssemblyError, build_scene_payload

__all__ = [
    "MAX_BODY_BYTES",
    "MAX_FIELD_LEN",
    "SCENE_MAX_SECONDS",
    "SCENE_RATE_LIMIT_MAX",
    "SCENE_RATE_LIMIT_MAX_KEYS",
    "SCENE_RATE_LIMIT_WINDOW_S",
    "SCENE_STATUS_STATE_MATRIX",
    "get_context_buildings_fetch",
    "router",
]

logger = logging.getLogger("app.api.v1.scene_api")

router = APIRouter(prefix="/api/v1", tags=["scene"])

#: Hard cap on a refusal ``field`` value on EVERY response and log path (mirrors the sibling
#: route's BP-3 bound).
MAX_FIELD_LEN = 200

#: Per-request wall-clock budget for the whole off-event-loop assembly (DB-061 (i)). Over it,
#: the awaited job is cancelled and a typed 504 is returned to the client - never a partial
#: scene; the worker thread itself cannot be force-killed and runs to completion, bounded by the
#: connector's own deadline and byte/vertex caps (see the module docstring).
SCENE_MAX_SECONDS = 15.0

#: Per-caller in-process rate limit (a sliding window). Keyed by caller host; the internal
#: route has no auth yet, so the key is best-effort (authn/tenancy arrive with PKT-H). Never a
#: new dependency - stdlib only.
SCENE_RATE_LIMIT_MAX = 30
SCENE_RATE_LIMIT_WINDOW_S = 60.0

#: Upper bound on the number of distinct caller-host keys the sliding-window state may hold, so
#: a spray of distinct callers cannot grow ``_rate_state`` without bound (G5 F-3 / G3 A2). When
#: a NEW caller arrives at the ceiling, expired-window keys are swept first; if the ceiling is
#: still full of ACTIVE callers the new caller is refused (fail-closed). A durable per-caller
#: key (chosen at the auth seam) and a shared limiter module arrive with PKT-H.
SCENE_RATE_LIMIT_MAX_KEYS = 4096

#: Per-caller request timestamps (monotonic seconds), keyed by caller host. In-process only.
#: Bounded to ``SCENE_RATE_LIMIT_MAX_KEYS`` active keys; expired windows are evicted.
_rate_state: dict[str, list[float]] = {}

#: The documented (HTTP status, state) pairs - the single source of truth. The 200 scene
#: carries NO ``state``; the disabled/unmounted sentinel is (404, None).
SCENE_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # the assembled scene payload (NO state)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (422, "validation_error"),  # malformed body OR a typed scene-assembly refusal
        (429, "rate_limited"),  # per-caller rate limit exceeded
        (504, "deadline_exceeded"),  # the assembly exceeded the per-request wall-clock budget
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


def get_context_buildings_fetch():
    """The connector seam used to fetch context buildings. Production uses the live keyless
    connector (:func:`app.connectors.building_footprints_arcgis.fetch_context_buildings`); tests
    monkeypatch this module attribute to inject an OFFLINE fake so the suite never touches the
    network. NOT a client-controlled input."""
    return fetch_context_buildings


def _rate_limit_clock() -> float:
    return time.monotonic()


def _reset_rate_limit_state() -> None:
    """Test hook: clear the in-process rate-limit window (module state persists across a
    process, and every test mounts a fresh app)."""
    _rate_state.clear()


def _evict_empty_keys(now: float, window: float) -> None:
    """Drop every key whose window is empty after pruning (G5 F-3 / G3 A2), so the state holds
    only currently-active callers. O(keys); called only when a NEW caller hits the key ceiling."""
    for key in list(_rate_state):
        if not any(now - t < window for t in _rate_state[key]):
            _rate_state.pop(key, None)


def _rate_limit_allows(caller_key: str) -> bool:
    """Sliding-window per-caller rate limit (DB-061 (i)), memory-bounded (G5 F-3 / G3 A2). Reads
    the module-level max/window/key-ceiling at call time so a test can tighten them. Prunes the
    caller's stamps outside the window on each call, EVICTS the caller's key when that window is
    empty (so a dead entry is never left behind), and bounds the total distinct-key count: a new
    caller arriving at the ceiling triggers a sweep of expired keys, and if the ceiling is still
    full of active callers the new caller is refused (fail-closed)."""
    now = _rate_limit_clock()
    window = SCENE_RATE_LIMIT_WINDOW_S
    stamps = [t for t in _rate_state.get(caller_key, []) if now - t < window]
    if not stamps:
        # An empty window (a brand-new caller or one whose stamps all expired) leaves no entry
        # behind; the caller is then treated as new for the key-ceiling check below.
        _rate_state.pop(caller_key, None)
    if len(stamps) >= SCENE_RATE_LIMIT_MAX:
        _rate_state[caller_key] = stamps  # at the limit: keep the (nonempty) window, refuse
        return False
    if caller_key not in _rate_state and len(_rate_state) >= SCENE_RATE_LIMIT_MAX_KEYS:
        _evict_empty_keys(now, window)
        if len(_rate_state) >= SCENE_RATE_LIMIT_MAX_KEYS:
            return False  # key ceiling full of active callers: refuse the new caller (fail-closed)
    stamps.append(now)
    _rate_state[caller_key] = stamps
    return True


def _caller_key(request: Request) -> str:
    client = request.client
    return client.host if client is not None else "unknown"


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=body, headers={"X-Correlation-ID": correlation_id}
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path (fail-safe disable):
    no correlation id, no body hint that the feature exists."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _bounded_field(field: str | None) -> str | None:
    if field is None or len(field) <= MAX_FIELD_LEN:
        return field
    return field[:MAX_FIELD_LEN] + f"...<truncated; {len(field)} chars total>"


def _validation_error(
    message: str, correlation_id: str, *, field: str | None = None
) -> JSONResponse:
    body: dict[str, object] = {
        "state": "validation_error",
        "message": _bounded_message(message),
        "correlation_id": correlation_id,
    }
    if field is not None:
        body["field"] = _bounded_field(field)
    return _json(422, body, correlation_id)


def _payload_too_large(correlation_id: str) -> JSONResponse:
    return _json(
        413,
        {
            "state": "payload_too_large",
            "message": f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _rate_limited(correlation_id: str) -> JSONResponse:
    return _json(
        429,
        {
            "state": "rate_limited",
            "message": "per-caller rate limit exceeded; retry later",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _deadline_exceeded(correlation_id: str) -> JSONResponse:
    return _json(
        504,
        {
            "state": "deadline_exceeded",
            "message": (
                "the scene assembly exceeded the per-request time budget; the request was "
                "cancelled and no scene is returned"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the correlation id only (never
    ``str(exc)`` / a traceback: the request may carry untrusted strings)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


@router.post("/scene", include_in_schema=False)
async def post_scene(request: Request) -> JSONResponse:
    """Assemble the section 2.1 scene payload for a caller lot + proposal/generated option and
    an optional context query. Feature-flag gated OFF by default (reuses
    INTERNAL_RULE_EVAL_ENABLED), mirroring the sibling internal routes."""
    # Fail-safe disable: absent/unknown flag -> generic 404 with no hint the feature exists.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Per-caller rate limit BEFORE any body read or heavy work (DB-061 (i)).
    if not _rate_limit_allows(_caller_key(request)):
        logger.info("scene_v1 rate_limited correlation_id=%s", correlation_id)
        return _rate_limited(correlation_id)

    # Bounded body - raw size ceiling BEFORE parsing, via the reused bounded-streaming accumulator.
    declared_length = _declared_content_length(request)
    if declared_length is not None and declared_length > MAX_BODY_BYTES:
        logger.info("scene_v1 payload_too_large declared correlation_id=%s", correlation_id)
        return _payload_too_large(correlation_id)
    raw, too_large = await _read_body_within_ceiling(request.stream(), MAX_BODY_BYTES)
    if too_large:
        logger.info("scene_v1 payload_too_large streamed correlation_id=%s", correlation_id)
        return _payload_too_large(correlation_id)

    if not raw or not raw.strip():
        return _validation_error("request body must be a JSON object", correlation_id)
    try:
        body = json.loads(raw)
    except Exception:
        return _validation_error(
            "request body is not valid JSON (or is too deeply nested to parse)", correlation_id
        )
    if not isinstance(body, dict):
        return _validation_error("request body must be a JSON object", correlation_id)

    # Strict-JSON + renderer-parity guard with the SAME encoder settings the response renderer
    # uses, so no malformed value reaches the assembler or the response.
    try:
        json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        return _validation_error(
            "request body is not strict-JSON serializable (NaN/Infinity) or contains "
            "non-encodable text (an unpaired surrogate)",
            correlation_id,
        )

    # Cheap event-loop boundary checks (fail fast with a named field before any threadpool work).
    if "lot_ring" not in body:
        return _validation_error("lot_ring is required", correlation_id, field="lot_ring")
    proposed_massing = body.get("proposed_massing")
    generated_option = body.get("generated_option")
    if (proposed_massing is None) == (generated_option is None):
        return _validation_error(
            "exactly one of proposed_massing or generated_option is required", correlation_id,
            field="proposed_massing")
    # G3 A4: a non-dict `context` is a caller-side request fault, not "no context" - refuse it
    # typed rather than silently ignoring it (an absent or null context is honest no-context).
    context_raw = body.get("context")
    if context_raw is None:
        context: dict = {}
    elif isinstance(context_raw, dict):
        context = context_raw
    else:
        return _validation_error(
            "context must be a JSON object when present", correlation_id, field="context")

    # The whole assembly runs OFF the event loop in a CANCELLABLE job under the per-request
    # wall-clock deadline (DB-061 (i)). The connector is called interactive=True with a matching
    # wall-clock deadline so its own paging is bounded too (DB-073 (c)). Over budget -> 504.
    connector_deadline = datetime.now(UTC) + timedelta(seconds=SCENE_MAX_SECONDS)
    fetch = get_context_buildings_fetch()
    work = functools.partial(
        build_scene_payload,
        lot_ring=body.get("lot_ring"),
        proposed_massing=proposed_massing,
        generated_option=generated_option,
        fetch=fetch,
        envelope=context.get("envelope"),
        polygon=context.get("polygon"),
        site_ground_elevation_ft=context.get("site_ground_elevation_ft"),
        subject_bbl=context.get("subject_bbl"),
        page_size=context.get("page_size"),
        deadline=connector_deadline,
        correlation_id=correlation_id,
        scenario_id=body.get("scenario_id"),
        property_geometry_version_id=body.get("property_geometry_version_id"),
        rule_release_id=body.get("rule_release_id"),
    )
    try:
        scene = await asyncio.wait_for(run_in_threadpool(work), timeout=SCENE_MAX_SECONDS)
    except TimeoutError:
        logger.warning("scene_v1 deadline_exceeded correlation_id=%s", correlation_id)
        return _deadline_exceeded(correlation_id)
    except SceneAssemblyError as exc:
        logger.info("scene_v1 refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(str(exc), correlation_id, field=exc.field)
    except Exception:
        logger.error("scene_v1 unexpected_error stage=assemble correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)

    scene["correlation_id"] = correlation_id
    try:  # defense in depth: the body was already proven strict-JSON above
        json.dumps(scene, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        logger.error("scene_v1 serialization_unsafe correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
    return _json(200, scene, correlation_id)
