"""POST /api/v1/dxf-import/{candidates,draft} - UNMOUNTED DXF import route (M5-T108, D-087 PKT-F).

The internal, flag-gated HTTP seam onto the accepted strict-subset DXF reader
(:func:`app.drawings.dxf_reader.read_dxf`) and the PKT-F import service
(:mod:`app.drawings.dxf_import`). ``/candidates`` lists the closed rings in an
uploaded ASCII DXF; ``/draft`` builds a proposed_massing DRAFT from the roles the
USER assigns and the units the USER confirms, validated through the SAME
``validate_proposed_massing`` contract. It stores NOTHING (plan section 4 (e)).

THIS ROUTE SHIPS UNMOUNTED. ``app/main.py`` is untouched; the ``include_router``
line rides the later PKT-H mount seam. Tests mount the router on a fresh
``FastAPI()`` via ``TestClient`` (the accepted M5-T059 / max_envelope pattern) and
assert it is ABSENT from the real app's OpenAPI.

Posture (mirrors the accepted sibling internal routes; plan sections 2 + 4):

* Flag-gated OFF by default. The base internal gate REUSES
  ``INTERNAL_RULE_EVAL_ENABLED``; because this is a caller-supplied-geometry
  IMPORT path, a dedicated default-off write flag (``DXF_IMPORT_ENABLED``) gates it
  ADDITIONALLY (plan section 2: registration flag AND handler flag). Either flag
  absent/empty/unknown -> a generic ``404`` byte-indistinguishable from an
  unmounted path (the accepted sentinel, ``lot_geometry.py:100``). ``include_in_schema=False``.
* Parse-time controls (plan section 4 (b)-(e)):
  (b) a raw upload byte ceiling enforced by the accepted T053 bounded-streaming
      primitives BEFORE the body is materialised;
  (c) ``read_dxf`` runs OFF the event loop in a cancellable job under a per-request
      wall-clock deadline, with a per-caller RATE LIMIT at the route (DB-061 (i));
  (d) a content-type + magic-byte check (ASCII DXF only, binary sentinel refused);
      only the exact bytes reach ``read_dxf`` and :data:`_IMPORT_DXF_LIMITS` is a
      fixed reviewed clamp, never built from untrusted input (DB-057 (k), DB-070 (d));
  (e) nothing is persisted - an in-memory result only.
* Every drawing-derived string is escaped in the service before it reaches a
  response; a refusal detail is bounded; only a server-generated correlation id is
  logged (never caller/upstream text) (DB-070 (a),(b)).

DB-070 (c) (a small digit cap on group codes) belongs to ``dxf_reader.py`` (read-only
here) and is NOT applied at this seam: the reader already bounds a group-code line by
``max_line_chars`` (clamped <= 65_536) so the CPython int-digit limit governs, and no
reader change is possible from this packet - recorded for the next reader touch.
"""

from __future__ import annotations

import asyncio
import functools
import json
import logging
import threading
import time
import uuid

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
from app.drawings.dxf_import import (
    CandidatesResult,
    DraftResult,
    ImportRefusal,
    RoleAssignment,
    build_draft,
    list_candidates,
    sniff_dxf_media,
)
from app.drawings.dxf_reader import DxfLimits, read_dxf

__all__ = [
    "DXF_IMPORT_ENABLED_ENV_VAR",
    "DXF_IMPORT_STATUS_STATE_MATRIX",
    "MAX_BODY_BYTES",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "READ_DEADLINE_SECONDS",
    "dxf_import_enabled",
    "get_rate_limiter",
    "router",
]

logger = logging.getLogger("app.api.v1.dxf_import_api")

router = APIRouter(prefix="/api/v1", tags=["dxf_import"])

#: Dedicated default-off write flag for this caller-supplied-geometry IMPORT path
#: (plan section 2). Its canonical name registration lives with the PKT-H mount seam
#: (config.py is outside this packet's scope); declared here so the handler can gate.
DXF_IMPORT_ENABLED_ENV_VAR = "DXF_IMPORT_ENABLED"
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})

#: The FIXED, reviewed DxfLimits passed to read_dxf. Never built from untrusted input
#: (DB-057 (k), DB-070 (d)); the reader additionally hard-clamps every field. max_bytes
#: matches the route body ceiling so the two size bounds agree.
_IMPORT_DXF_LIMITS = DxfLimits(max_bytes=MAX_BODY_BYTES)

#: Per-request wall-clock deadline for the off-event-loop read job (DB-070 (e)). The
#: read is linear and input-bounded; this bounds the caller's wait. A Python thread is
#: not force-killed, but the clamped limits bound the work it can do before returning.
READ_DEADLINE_SECONDS = 10.0

#: Per-caller rate limit (DB-061 (i)): at most N requests per window per client key.
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60.0

#: The documented (HTTP status, state) pairs - the single source of truth. A 200 body
#: carries NO ``state`` (pair ``(200, None)``), mirroring the accepted sibling routes.
DXF_IMPORT_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # candidate listing or validated draft
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (415, "unsupported_media_type"),  # content-type / magic-byte / binary sentinel
        (422, "validation_error"),  # unreadable DXF, bad assignment, invalid draft
        (429, "rate_limited"),  # per-caller rate limit exceeded
        (503, "deadline_exceeded"),  # off-loop read job passed the deadline
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


def dxf_import_enabled(env=None) -> bool:
    """Whether the dedicated import write flag holds an explicit true token. Absent/
    empty/unknown -> False (fail safe). Read each call so a test can flip it."""
    import os

    source = os.environ if env is None else env
    raw = source.get(DXF_IMPORT_ENABLED_ENV_VAR)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_TOKENS


class _RateLimiter:
    """Minimal thread-safe fixed-window per-caller rate limiter (stdlib only; no new
    dependency). ``check`` returns True when the caller is within budget. Keyed by a
    caller identity the route derives from the connection; a monotonic clock so a
    wall-clock change cannot widen the window."""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._lock = threading.Lock()
        self._hits: dict[str, list[float]] = {}

    def check(self, key: str, *, now: float | None = None) -> bool:
        stamp = time.monotonic() if now is None else now
        with self._lock:
            recent = [t for t in self._hits.get(key, ()) if stamp - t < self._window]
            if len(recent) >= self._max:
                self._hits[key] = recent
                return False
            recent.append(stamp)
            self._hits[key] = recent
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_RATE_LIMITER = _RateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)


def get_rate_limiter() -> _RateLimiter:
    """The per-caller rate limiter. Tests monkeypatch this module attribute to inject a
    tight or disabled limiter; NOT a client-controlled input."""
    return _RATE_LIMITER


def _client_key(request: Request) -> str:
    client = request.client
    return client.host if client is not None else "unknown"


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=body, headers={"X-Correlation-ID": correlation_id}
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path (fail-safe
    disable): no correlation id, no body hint that the feature exists."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _guard_finite_response(body: dict, correlation_id: str) -> JSONResponse | None:
    """Defense-in-depth pre-render guard (G5 MEDIUM 1).

    Starlette renders a JSONResponse with ``allow_nan=False``; a non-finite float anywhere in
    a 200 body would make that render raise ValueError AFTER the handler returns - an untyped,
    correlation-id-less 500. The service already refuses out-of-range coordinates, so this is a
    second line: pre-serialize the body with the SAME encoder settings the renderer uses
    (mirroring ``proposal_validation.py``); on failure return the typed (500, internal_error)
    with a correlation id, never a bare 500. Returns ``None`` when the body is safe to render.
    """
    try:
        json.dumps(body, ensure_ascii=False, allow_nan=False)
    except ValueError:
        logger.error("dxf_import non_finite_response correlation_id=%s", correlation_id)
        return _error(500, "internal_error", "unexpected internal error", correlation_id)
    return None


def _error(
    status_code: int, state: str, message: str, correlation_id: str, *, field=None
) -> JSONResponse:
    body: dict[str, object] = {
        "state": state,
        "message": _bounded_message(message),
        "correlation_id": correlation_id,
    }
    if field is not None:
        body["field"] = _bounded_message(field)
    return _json(status_code, body, correlation_id)


def _refusal_response(refusal: ImportRefusal, correlation_id: str) -> JSONResponse:
    """Map a typed service :class:`ImportRefusal` onto the status/state matrix. Any
    discrepancies detected before the refusal are SHOWN, never dropped."""
    if refusal.reason == "unsupported_media_type":
        status, state = 415, "unsupported_media_type"
    else:
        status, state = 422, "validation_error"
    body: dict[str, object] = {
        "state": state,
        "message": _bounded_message(refusal.detail),
        "correlation_id": correlation_id,
    }
    if refusal.field is not None:
        body["field"] = _bounded_message(refusal.field)
    if refusal.discrepancies:
        body["discrepancies"] = list(refusal.discrepancies)
    return _json(status, body, correlation_id)


async def _read_dxf_with_deadline(raw: bytes):
    """Run read_dxf OFF the event loop in a cancellable job under the deadline (DB-070
    (e) / DB-061 (i)). ``asyncio.wait_for`` cancels the await on timeout; the clamped
    :data:`_IMPORT_DXF_LIMITS` bound the work the thread can do."""
    return await asyncio.wait_for(
        run_in_threadpool(functools.partial(read_dxf, raw, limits=_IMPORT_DXF_LIMITS)),
        timeout=READ_DEADLINE_SECONDS,
    )


async def _guarded_read(request: Request, correlation_id: str):
    """Shared pipeline for both endpoints: flag gate, rate limit, bounded body,
    media/magic-byte gate, then the deadline-bounded off-loop read. Returns either a
    reader result (DxfReadResult) or a JSONResponse to short-circuit on."""
    # Fail-safe disable: EITHER flag absent/unknown -> generic 404, no feature hint.
    if not (internal_rule_eval_enabled() and dxf_import_enabled()):
        return _not_found()

    if not get_rate_limiter().check(_client_key(request)):
        logger.info("dxf_import rate_limited correlation_id=%s", correlation_id)
        return _error(
            429, "rate_limited", "per-caller rate limit exceeded; retry later", correlation_id
        )

    declared = _declared_content_length(request)
    if declared is not None and declared > MAX_BODY_BYTES:
        logger.info("dxf_import payload_too_large declared correlation_id=%s", correlation_id)
        return _error(
            413, "payload_too_large",
            f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes", correlation_id,
        )
    raw, too_large = await _read_body_within_ceiling(request.stream(), MAX_BODY_BYTES)
    if too_large:
        logger.info("dxf_import payload_too_large streamed correlation_id=%s", correlation_id)
        return _error(
            413, "payload_too_large",
            f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes", correlation_id,
        )

    sniff = sniff_dxf_media(request.headers.get("content-type"), raw)
    if sniff is not None:
        logger.info("dxf_import media_refused correlation_id=%s", correlation_id)
        return _refusal_response(sniff, correlation_id)

    try:
        return await _read_dxf_with_deadline(raw)
    except TimeoutError:
        logger.error("dxf_import deadline_exceeded correlation_id=%s", correlation_id)
        return _error(
            503, "deadline_exceeded", "the drawing could not be read within the deadline",
            correlation_id,
        )
    except Exception:
        logger.error("dxf_import unexpected_error stage=read correlation_id=%s", correlation_id)
        return _error(500, "internal_error", "unexpected internal error", correlation_id)


def _q_int(query, name: str) -> int | None:
    raw = query.get(name)
    if raw is None:
        return None
    return int(raw)  # ValueError caught by the caller -> typed 422


def _q_float(query, name: str) -> float | None:
    raw = query.get(name)
    if raw is None:
        return None
    return float(raw)


def _parse_assignment(query, correlation_id: str):
    """Build a :class:`RoleAssignment` from validated query params, or a 422 response.
    Roles/units come as query params because the request BODY is the raw DXF upload."""
    try:
        building_outline = _q_int(query, "building_outline")
        floors = _q_int(query, "floors")
        property_line = _q_int(query, "property_line")
        street_frontage = _q_int(query, "street_frontage")
        floor_to_floor_ft = _q_float(query, "floor_to_floor_ft")
        known_length_ft = _q_float(query, "known_length_ft")
        measured_length = _q_float(query, "measured_length")
    except ValueError:
        return _error(
            422, "validation_error", "a numeric query parameter is not a valid number",
            correlation_id,
        )
    author = query.get("author")
    if building_outline is None:
        return _error(
            422, "validation_error", "building_outline (a candidate index) is required",
            correlation_id, field="building_outline",
        )
    if floors is None or floor_to_floor_ft is None:
        return _error(
            422, "validation_error",
            "floors and floor_to_floor_ft are required (the drawing carries no height)",
            correlation_id, field="floors",
        )
    if not author or not author.strip():
        return _error(
            422, "validation_error", "author is required (non-empty)", correlation_id,
            field="author",
        )
    confirmed_units = query.get("confirmed_units")
    return RoleAssignment(
        building_outline=building_outline,
        floors=floors,
        floor_to_floor_ft=floor_to_floor_ft,
        author=author,
        property_line=property_line,
        street_frontage=street_frontage,
        confirmed_units=confirmed_units,
        known_length_ft=known_length_ft,
        measured_length=measured_length,
    )


@router.post("/dxf-import/candidates", include_in_schema=False)
async def post_dxf_candidates(request: Request) -> JSONResponse:
    """List the closed-ring candidates in an uploaded ASCII DXF (layer, vertex count,
    measured dimensions in the DECLARED units). Persists nothing."""
    correlation_id = uuid.uuid4().hex
    result = await _guarded_read(request, correlation_id)
    if isinstance(result, JSONResponse):
        return result

    outcome = list_candidates(result)
    if isinstance(outcome, ImportRefusal):
        logger.info("dxf_import candidates_refused correlation_id=%s", correlation_id)
        return _refusal_response(outcome, correlation_id)

    assert isinstance(outcome, CandidatesResult)
    body = {
        "declared_units": outcome.declared_units,
        "acad_version": outcome.acad_version,
        "candidates": [
            {
                "index": c.index,
                "entity_type": c.entity_type,
                "layer": c.layer,
                "vertex_count": c.vertex_count,
                "measured": c.measured,
            }
            for c in outcome.candidates
        ],
        "disclosure": outcome.disclosure,
        "notice": (
            "Imported drawing - not survey-confirmed. Nothing here is a city record "
            "or a permitted value."
        ),
        "correlation_id": correlation_id,
    }
    guarded = _guard_finite_response(body, correlation_id)
    if guarded is not None:
        return guarded
    return _json(200, body, correlation_id)


@router.post("/dxf-import/draft", include_in_schema=False)
async def post_dxf_draft(request: Request) -> JSONResponse:
    """Build a proposed_massing DRAFT from the user's assigned roles and confirmed
    units, validated through validate_proposed_massing. Persists nothing."""
    correlation_id = uuid.uuid4().hex
    assignment = _parse_assignment(request.query_params, correlation_id)
    if isinstance(assignment, JSONResponse):
        # Still fail-safe closed: a disabled feature must not answer 422 either.
        if not (internal_rule_eval_enabled() and dxf_import_enabled()):
            return _not_found()
        return assignment

    result = await _guarded_read(request, correlation_id)
    if isinstance(result, JSONResponse):
        return result

    outcome = build_draft(result, assignment)
    if isinstance(outcome, ImportRefusal):
        logger.info("dxf_import draft_refused correlation_id=%s", correlation_id)
        return _refusal_response(outcome, correlation_id)

    assert isinstance(outcome, DraftResult)
    body = {
        "proposed_massing": outcome.proposed_massing,
        "provenance": outcome.provenance,
        "discrepancies": list(outcome.discrepancies),
        "correlation_id": correlation_id,
    }
    guarded = _guard_finite_response(body, correlation_id)
    if guarded is not None:
        return guarded
    return _json(200, body, correlation_id)
