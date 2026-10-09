"""POST /api/v1/export - UNMOUNTED, flag-gated CAD/3D export route (task M5-T109, D-087 PKT-D).

The internal HTTP seam onto the accepted, route-free
:func:`app.cad.export_service.build_export`. Given a caller massing option (an EPSG:2263 lot
ring, an optional building footprint, per-floor heights and provenance strings) plus a
``format`` in ``{dxf, pdf, glb}``, it returns the corresponding download - an AutoCAD-openable
ASCII DXF, a PDF site-plan sheet, or a glTF 2.0 binary massing - via the accepted writers, or a
single reconciled, redacted refusal. It stores nothing.

THIS ROUTE SHIPS UNMOUNTED. ``app/main.py`` is NOT touched; ``include_in_schema=False`` and the
generic-404 sentinel keep it byte-indistinguishable from an unmounted path until the later PKT-H
mount seam. Tests mount the router on a fresh ``FastAPI()`` via ``TestClient`` (the accepted
M5-T059 / max_envelope_api pattern) and assert it is ABSENT from the real app's OpenAPI.

Route discipline MIRRORS the accepted sibling ``max_envelope_api`` and reuses its boundary
primitives rather than forking them:

* Posture - feature-flag gated OFF by default (REUSED ``INTERNAL_RULE_EVAL_ENABLED``;
  ``include_in_schema=False``; absent/empty/unknown flag -> a generic 404 with no correlation id
  and no body hint, byte-identical to an unmounted path) for EVERY HTTP method (DB-081 (d)): the
  path is registered for all methods so a disabled route never answers a 405 that would leak its
  existence. A bounded request body (raw-byte ceiling by BOUNDED STREAMING, reusing the accepted
  T053 primitives) is read BEFORE any parse. authn / tenancy / per-user ownership arrive with the
  PUBLIC exposure packet (PKT-H), recorded here as a disposition, not implemented (unreachable
  without the internal flag).
* Job safety (DB-061 (i), the M5-T088 G5 fix (b)) - the writer runs OFF the event loop in a
  cancellable job (``run_in_job_slot`` over ``run_in_threadpool``) with a per-request wall-clock
  deadline, behind a per-caller RATE LIMIT and a bounded IN-FLIGHT JOB CAP. Over the deadline ->
  a typed 503, never a partial file; the cap full -> a typed 503; the slot is held until the
  worker THREAD returns (never at the deadline cancel) so deadline-abandoned threads cannot pile
  up (DB-082 (b)). The per-caller limiter and the job-slot cap are now the ONE shared, bounded
  :mod:`app.resilience.rate_limit` primitives shared with the scene / import routes.
* Redaction - only a server-generated ``X-Correlation-ID`` is logged; NO caller or writer text
  reaches a log line (the exception class + a length-bounded sanitized message at most). The
  reconciled refusal body is ``{reject_code, detail}`` from the service, which never echoes
  caller text (DB-059 (e), (h)).

The emitted (HTTP status, state) pairs are the single source of truth
:data:`EXPORT_STATUS_STATE_MATRIX`; a 200 is a FILE (bytes) with a per-format media type and a
server-built ``Content-Disposition`` (the mandatory filename-safety token), NOT a JSON document.
"""

from __future__ import annotations

import functools
import json
import logging
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.api.v1.proposal_validation import (
    _bounded_message,
    _declared_content_length,
    _read_body_within_ceiling,
)
from app.cad import export_service
from app.config import internal_rule_eval_enabled
from app.resilience.rate_limit import (
    JobSlots,
    SlidingWindowRateLimiter,
    SlotsExhausted,
    caller_key,
    run_in_job_slot,
)

__all__ = [
    "EXPORT_DEADLINE_SECONDS",
    "EXPORT_MAX_BODY_BYTES",
    "EXPORT_MAX_IN_FLIGHT",
    "EXPORT_STATUS_STATE_MATRIX",
    "RATE_LIMIT_MAX_KEYS",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "get_job_slots",
    "get_rate_limiter",
    "router",
]

logger = logging.getLogger("app.api.v1.export_api")

router = APIRouter(prefix="/api/v1", tags=["export"])

#: Every HTTP method registered on the path, so a DISABLED route answers ALL of them with the
#: SAME generic 404 as an unmounted path (DB-081 (d)) - no 405 that would leak the route's
#: existence. When ENABLED only POST does work; any other method is a genuine 405.
_ROUTE_METHODS = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

#: Raw request-body ceiling for THIS route (DB-086 (d) / M5-T111 G5 Finding 4). Sized to the
#: export request contract's OWN caps, NOT the shared 256 KiB proposal_validation.MAX_BODY_BYTES
#: (which stays 256 KiB and is untouched). A maximal legitimate export is two rings at the writer
#: cap (``export_service._FORMAT_RING_CAP`` = 10,000 vertices for dxf/glb) plus MAX_FLOORS (2,000)
#: floor heights; that body MEASURES ~452,336 bytes (~442 KiB, [OBSERVED]; see the producer report
#: + the measurement test), which the shared 256 KiB ceiling would WRONGLY refuse (413) BEFORE the
#: writer's own vertex cap. 1 MiB admits it with ~2.3x headroom; enforced BEFORE the body is
#: buffered past it via the reused bounded-streaming path (the 413 shape is unchanged).
EXPORT_MAX_BODY_BYTES = 1 * 1024 * 1024  # 1 MiB

#: Per-request wall-clock deadline (seconds). The writer runs off the event loop and is
#: abandoned by the deadline past this bound -> a typed 503, never a partial file.
EXPORT_DEADLINE_SECONDS = 15.0

#: Per-caller sliding-window rate limit (unchanged: 30 / 60 s), now served by the ONE shared,
#: bounded :class:`app.resilience.SlidingWindowRateLimiter`.
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60.0
#: Hard ceiling on distinct tracked caller keys (bounds limiter memory against key spraying).
RATE_LIMIT_MAX_KEYS = 8192

#: Bounded in-flight writer jobs (DB-082 (b) / DB-088 (a)). A slot is held from job start until
#: the worker THREAD returns (never at the deadline cancel), so deadline-abandoned writer threads
#: cannot pile up. Sized with scene (8) and dxf-import (4) so the SUMMED caps (8 + 12 + 4 = 24)
#: stay UNDER anyio's 40-token default thread pool with 16 tokens of headroom for the app's other
#: run_sync users; export gets the MOST of the three because its per-slot memory is the lightest
#: (a 1 MiB ceiling; the writer is CPU-bound, not memory-bound). See tests/resilience.
EXPORT_MAX_IN_FLIGHT = 12

#: The shared limiter + job-slot instances for this route (per-route state; the CLASS is shared
#: across the three D-087 routes). Exposed via getters that tests reset/tighten.
_RATE_LIMITER = SlidingWindowRateLimiter(
    max_requests=RATE_LIMIT_MAX_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
    max_keys=RATE_LIMIT_MAX_KEYS,
)
_JOB_SLOTS = JobSlots(max_slots=EXPORT_MAX_IN_FLIGHT)

#: The documented (HTTP status, state) pairs - the single source of truth. A 200 is a FILE with
#: NO ``state`` (pair ``(200, None)``); every refusal is JSON carrying a ``state``. The disabled
#: sentinel is (404, None) for EVERY method; a non-POST method on the ENABLED route is (405, None).
EXPORT_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # the export file (bytes; per-format media type; NO state)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found), every method
        (405, None),  # non-POST method on the ENABLED route (real Method Not Allowed)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (422, "validation_error"),  # malformed body OR a reconciled writer/service refusal
        (429, "rate_limited"),  # per-caller rate limit exceeded
        (503, "capacity_exhausted"),  # the bounded in-flight job cap was full (DB-082 (b))
        (503, "deadline_exceeded"),  # per-request wall-clock deadline exceeded
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


def get_rate_limiter() -> SlidingWindowRateLimiter:
    """The shared, bounded per-caller limiter for this route. Tests reset/tighten it via this
    getter; NOT a client-controlled input."""
    return _RATE_LIMITER


def get_job_slots() -> JobSlots:
    """The bounded in-flight job-slot counter for this route. NOT a client-controlled input."""
    return _JOB_SLOTS


# --------------------------------------------------------------------------- #
# Response builders (mirror the accepted sibling route's shapes).
# --------------------------------------------------------------------------- #

def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path (fail-safe disable):
    no correlation id, no body hint the feature exists."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _method_not_allowed() -> JSONResponse:
    """A genuine 405 for a non-POST method on the ENABLED route (the disabled case is a 404,
    handled first). Carries no state; only POST is a real operation."""
    return JSONResponse(
        status_code=405, content={"detail": "Method Not Allowed"}, headers={"Allow": "POST"}
    )


def _error(status_code: int, state: str, message: str, correlation_id: str) -> JSONResponse:
    body: dict[str, object] = {
        "state": state,
        "message": _bounded_message(message),
        "correlation_id": correlation_id,
    }
    return JSONResponse(
        status_code=status_code, content=body, headers={"X-Correlation-ID": correlation_id}
    )


def _refusal_response(
    refusal: export_service.ExportRefusal, correlation_id: str
) -> JSONResponse:
    """A reconciled, redacted (422, "validation_error"). Carries the service's fixed
    ``reject_code`` + a server-built ``detail`` that never echoes caller text."""
    body: dict[str, object] = {
        "state": "validation_error",
        "reject_code": refusal.reject_code,
        "detail": _bounded_message(refusal.detail),
        "correlation_id": correlation_id,
    }
    return JSONResponse(
        status_code=422, content=body, headers={"X-Correlation-ID": correlation_id}
    )


def _file_response(result: export_service.ExportResult, correlation_id: str) -> Response:
    """A 200 FILE download: the writer bytes, the per-format media type, the server-built
    Content-Disposition (the mandatory filename-safety token) and the correlation id. No caller
    text reaches any header value."""
    return Response(
        content=result.body,
        media_type=result.media_type,
        headers={
            "Content-Disposition": result.content_disposition,
            "X-Correlation-ID": correlation_id,
            "X-Content-Type-Options": "nosniff",
        },
    )


def _build_request(body: dict) -> export_service.ExportRequest:
    """Shape the parsed body into an :class:`ExportRequest`. Deep validation (vocab, caps,
    claim-word screen, geometry) is the service's job; this only reads fields, leaving their
    types for the service to refuse (typed)."""
    return export_service.ExportRequest(
        format=body.get("format"),
        source=body.get("source"),
        lot_ring=body.get("lot_ring"),
        building_ring=body.get("building_ring"),
        floor_heights=body.get("floor_heights"),
        address=body.get("address"),
        bbl=body.get("bbl"),
        generated_at=body.get("generated_at"),
        generator_version=body.get("generator_version"),
        base_elevation=body.get("base_elevation", 0.0),
    )


@router.api_route("/export", methods=_ROUTE_METHODS, include_in_schema=False)
async def export_endpoint(request: Request) -> Response:
    """Export a caller massing option to a DXF, PDF or GLB download. Feature-flag gated OFF by
    default (reuses INTERNAL_RULE_EVAL_ENABLED), mirroring the sibling internal routes."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> a generic 404 for EVERY method
    # (DB-081 (d)) with no hint the feature exists. Checked FIRST, before a correlation id is
    # minted or the method is dispatched.
    if not internal_rule_eval_enabled():
        return _not_found()
    if request.method != "POST":
        return _method_not_allowed()

    correlation_id = uuid.uuid4().hex

    # Guard 2: per-caller rate limit BEFORE any body read or work (the shared bounded limiter,
    # keyed on the authenticated principal when present else the caller host).
    if not get_rate_limiter().allow(caller_key(request)):
        logger.info("export_v1 rate_limited correlation_id=%s", correlation_id)
        return _error(429, "rate_limited", "per-caller rate limit exceeded", correlation_id)

    # Guard 3: raw body size ceiling BEFORE parsing, via BOUNDED STREAMING accumulation.
    declared_length = _declared_content_length(request)
    if declared_length is not None and declared_length > EXPORT_MAX_BODY_BYTES:
        logger.info("export_v1 payload_too_large declared=%d correlation_id=%s",
                    declared_length, correlation_id)
        return _error(413, "payload_too_large",
                      f"request body exceeds the maximum of {EXPORT_MAX_BODY_BYTES} bytes",
                      correlation_id)
    raw, too_large = await _read_body_within_ceiling(request.stream(), EXPORT_MAX_BODY_BYTES)
    if too_large:
        logger.info("export_v1 payload_too_large streamed_over_ceiling correlation_id=%s",
                    correlation_id)
        return _error(413, "payload_too_large",
                      f"request body exceeds the maximum of {EXPORT_MAX_BODY_BYTES} bytes",
                      correlation_id)

    if not raw or not raw.strip():
        return _error(422, "validation_error", "request body must be a JSON object", correlation_id)
    try:
        body = json.loads(raw)
    except Exception:
        return _error(422, "validation_error",
                      "request body is not valid JSON (or is too deeply nested to parse)",
                      correlation_id)
    if not isinstance(body, dict):
        return _error(422, "validation_error", "request body must be a JSON object", correlation_id)

    # Strict-JSON guard with the SAME encoder settings the error renderer uses, so a NaN/Infinity
    # or non-encodable value is refused here rather than reaching a writer.
    try:
        json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        return _error(422, "validation_error",
                      "request body is not strict-JSON serializable (NaN/Infinity) or contains "
                      "non-encodable text (an unpaired surrogate)", correlation_id)

    export_request = _build_request(body)

    # The single service entry, run OFF the event loop in a cancellable job under a per-request
    # wall-clock deadline AND a bounded in-flight job slot (DB-061 (i), DB-082 (b)). The fallback
    # filename token is the correlation id, so a bbl/generated_at that allowlists to nothing still
    # yields a caller-free filename. Over budget -> 503 deadline; the job cap full -> 503 capacity.
    work = functools.partial(
        export_service.build_export, export_request, fallback_token=correlation_id
    )
    try:
        result = await run_in_job_slot(get_job_slots(), work, timeout=EXPORT_DEADLINE_SECONDS)
    except SlotsExhausted:
        logger.warning("export_v1 capacity_exhausted correlation_id=%s", correlation_id)
        return _error(503, "capacity_exhausted",
                      "the server is at its in-flight job capacity; retry later", correlation_id)
    except TimeoutError:  # the deadline raises TimeoutError (asyncio.TimeoutError alias)
        logger.warning("export_v1 deadline_exceeded correlation_id=%s", correlation_id)
        return _error(503, "deadline_exceeded",
                      "export exceeded the per-request time budget", correlation_id)
    except Exception:
        logger.error("export_v1 unexpected_error stage=build_export correlation_id=%s",
                     correlation_id)
        return _error(500, "internal_error",
                      "unexpected internal error; see server logs by correlation id",
                      correlation_id)

    if isinstance(result, export_service.ExportRefusal):
        logger.info("export_v1 refused reject_code=%s correlation_id=%s",
                    result.reject_code, correlation_id)
        return _refusal_response(result, correlation_id)
    return _file_response(result, correlation_id)
