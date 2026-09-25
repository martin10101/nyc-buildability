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
  byte-indistinguishable from an unmounted path - the ``lot_geometry.py:100`` sentinel), for
  EVERY HTTP method (DB-081 (d)): the path is registered for all methods so a disabled route
  never answers a 405 that would leak its existence. A bounded request body (raw-byte ceiling
  by BOUNDED STREAMING, reusing the accepted T053 primitives). No auth change: authn / tenancy
  / per-user ownership of the supplied geometry arrive with the PUBLIC exposure packet (PKT-H),
  recorded here as a disposition, not implemented (the route is unreachable without the
  internal flag).
* Job safety (DB-061 (i), the M5-T088 G5 fix (b)) - the assembly (the CPU-bound massing build
  + the connector fetch + the assemble) runs OFF the event loop under a per-request wall-clock
  deadline (``run_in_job_slot`` over ``run_in_threadpool``), and the connector is called
  ``interactive=True`` with a matching wall-clock ``deadline`` so its own paging is bounded too
  (DB-073 (c)). Over the deadline the AWAIT is cancelled and a typed 504 is returned with no
  partial scene reaching the client; the underlying worker thread cannot be force-killed and
  runs to completion in the background, but its total work is independently bounded (the
  connector's own wall-clock deadline + ``interactive`` single-attempt posture + response-byte
  and vertex caps; the massing build is vertex-bounded), so no unbounded work is left running.
  The whole assembly is additionally admitted through a bounded IN-FLIGHT JOB CAP
  (:func:`app.resilience.rate_limit.run_in_job_slot`), so deadline-abandoned threads cannot pile
  up: a slot is held until the worker THREAD returns (never at the deadline cancel) and over the
  cap is a typed 503. A per-caller RATE LIMIT (the shared, bounded
  :class:`app.resilience.rate_limit.SlidingWindowRateLimiter`) precedes all work.
* Logging - only a SERVER-generated correlation id, the state, and bounded field names reach a
  log line; no caller or upstream text is ever logged (the assembler does not log at all).

The emitted (HTTP status, state) pairs are the single source of truth
:data:`SCENE_STATUS_STATE_MATRIX`; the 200 scene carries NO ``state``.
"""

from __future__ import annotations

import functools
import json
import logging
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.v1.proposal_validation import (
    MAX_BODY_BYTES,
    _bounded_message,
    _declared_content_length,
    _read_body_within_ceiling,
)
from app.config import internal_rule_eval_enabled
from app.connectors.building_footprints_arcgis import fetch_context_buildings
from app.resilience.rate_limit import (
    JobSlots,
    SlidingWindowRateLimiter,
    SlotsExhausted,
    caller_key,
    run_in_job_slot,
)
from app.scenario.scene_assembler import SceneAssemblyError, build_scene_payload

__all__ = [
    "MAX_BODY_BYTES",
    "MAX_FIELD_LEN",
    "SCENE_MAX_IN_FLIGHT",
    "SCENE_MAX_SECONDS",
    "SCENE_RATE_LIMIT_MAX",
    "SCENE_RATE_LIMIT_MAX_KEYS",
    "SCENE_RATE_LIMIT_WINDOW_S",
    "SCENE_STATUS_STATE_MATRIX",
    "get_context_buildings_fetch",
    "get_job_slots",
    "get_rate_limiter",
    "router",
]

logger = logging.getLogger("app.api.v1.scene_api")

router = APIRouter(prefix="/api/v1", tags=["scene"])

#: Every HTTP method registered on the path, so a DISABLED route answers ALL of them with the
#: SAME generic 404 as an unmounted path (DB-081 (d)) - no 405 that would leak the route's
#: existence. When ENABLED only POST does work; any other method is a genuine 405.
_ROUTE_METHODS = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

#: Hard cap on a refusal ``field`` value on EVERY response and log path (mirrors the sibling
#: route's BP-3 bound).
MAX_FIELD_LEN = 200

#: Per-request wall-clock budget for the whole off-event-loop assembly (DB-061 (i)). Over it,
#: the awaited job is cancelled and a typed 504 is returned to the client - never a partial
#: scene; the worker thread itself cannot be force-killed and runs to completion, bounded by the
#: connector's own deadline and byte/vertex caps (see the module docstring).
SCENE_MAX_SECONDS = 15.0

#: Per-caller rate limit (a sliding window), unchanged from the route-local limiter (30 / 60 s);
#: now served by the ONE shared :class:`app.resilience.rate_limit.SlidingWindowRateLimiter`.
SCENE_RATE_LIMIT_MAX = 30
SCENE_RATE_LIMIT_WINDOW_S = 60.0

#: Upper bound on the number of distinct caller keys the shared limiter may hold, so a spray of
#: distinct callers cannot grow its state without bound (G5 F-3 / G3 A2). A new caller arriving
#: while the ceiling is full of ACTIVE keys is refused (fail-closed); an active key is never
#: evicted. The durable per-caller key (the authenticated principal) arrives with PKT-H.
SCENE_RATE_LIMIT_MAX_KEYS = 4096

#: Bounded in-flight assembly jobs (DB-082 (b)). A slot is held from job start until the worker
#: THREAD returns (never at the deadline cancel), so deadline-abandoned threads cannot pile up.
#: Kept below anyio's 40-thread default pool so one saturated route cannot starve it.
SCENE_MAX_IN_FLIGHT = 16

#: The shared limiter + job-slot instances for this route (per-route state; the CLASS is shared
#: across the three D-087 routes). Exposed via getters that tests reset/tighten.
_RATE_LIMITER = SlidingWindowRateLimiter(
    max_requests=SCENE_RATE_LIMIT_MAX,
    window_seconds=SCENE_RATE_LIMIT_WINDOW_S,
    max_keys=SCENE_RATE_LIMIT_MAX_KEYS,
)
_JOB_SLOTS = JobSlots(max_slots=SCENE_MAX_IN_FLIGHT)

#: The documented (HTTP status, state) pairs - the single source of truth. The 200 scene
#: carries NO ``state``; the disabled/unmounted sentinel is (404, None) for EVERY method; a
#: non-POST method on the ENABLED route is a genuine (405, None).
SCENE_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # the assembled scene payload (NO state)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found), every method
        (405, None),  # non-POST method on the ENABLED route (real Method Not Allowed)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (422, "validation_error"),  # malformed body OR a typed scene-assembly refusal
        (429, "rate_limited"),  # per-caller rate limit exceeded
        (503, "capacity_exhausted"),  # the bounded in-flight job cap was full (DB-082 (b))
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


def get_rate_limiter() -> SlidingWindowRateLimiter:
    """The shared, bounded per-caller limiter for this route. Tests reset/tighten it via this
    getter; NOT a client-controlled input."""
    return _RATE_LIMITER


def get_job_slots() -> JobSlots:
    """The bounded in-flight job-slot counter for this route. NOT a client-controlled input."""
    return _JOB_SLOTS


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=body, headers={"X-Correlation-ID": correlation_id}
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path (fail-safe disable):
    no correlation id, no body hint that the feature exists."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _method_not_allowed() -> JSONResponse:
    """A genuine 405 for a non-POST method on the ENABLED route (the disabled case is a 404,
    handled first). Carries no state; only POST is a real operation."""
    return JSONResponse(
        status_code=405, content={"detail": "Method Not Allowed"}, headers={"Allow": "POST"}
    )


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


def _capacity_exhausted(correlation_id: str) -> JSONResponse:
    """Typed (503, capacity_exhausted): the bounded in-flight job cap is full (DB-082 (b)) -
    every slot is held by a still-running (possibly deadline-abandoned) worker thread. A
    server-capacity signal, distinct from the per-caller 429 and the per-request 504."""
    return _json(
        503,
        {
            "state": "capacity_exhausted",
            "message": "the server is at its in-flight job capacity; retry later",
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


@router.api_route("/scene", methods=_ROUTE_METHODS, include_in_schema=False)
async def scene_endpoint(request: Request) -> JSONResponse:
    """Assemble the section 2.1 scene payload for a caller lot + proposal/generated option and
    an optional context query. Feature-flag gated OFF by default (reuses
    INTERNAL_RULE_EVAL_ENABLED), mirroring the sibling internal routes."""
    # Fail-safe disable: absent/unknown flag -> generic 404 for EVERY method (DB-081 (d)), with
    # no hint the feature exists. Checked FIRST, before the method is dispatched.
    if not internal_rule_eval_enabled():
        return _not_found()
    if request.method != "POST":
        return _method_not_allowed()

    correlation_id = uuid.uuid4().hex

    # Per-caller rate limit BEFORE any body read or heavy work (DB-061 (i)); the shared bounded
    # limiter, keyed on the authenticated principal when present else the caller host.
    if not get_rate_limiter().allow(caller_key(request)):
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
    # wall-clock deadline AND a bounded in-flight job slot (DB-061 (i), DB-082 (b)). The
    # connector is called interactive=True with a matching wall-clock deadline so its own paging
    # is bounded too (DB-073 (c)). Over budget -> 504; the job cap full -> 503.
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
        scene = await run_in_job_slot(get_job_slots(), work, timeout=SCENE_MAX_SECONDS)
    except SlotsExhausted:
        logger.warning("scene_v1 capacity_exhausted correlation_id=%s", correlation_id)
        return _capacity_exhausted(correlation_id)
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
