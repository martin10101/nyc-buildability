"""POST /api/v1/proposal-validation - stateless proposed-massing validation (M5-T053).

Phase B3-scaffold slice 1 (D-076): the FIRST route that wires editor-authored geometry to
the accepted proposed-massing validator. It is VALIDATION ONLY - it stores nothing, derives
nothing, computes NO allowance, area, lot coverage, FAR, or height sum (D-076-R002: a
proposed building is a THIRD input class, never a city record and never a rule). The B3
editor UI consumes this route later; B1/B2 derivation is untouched.

REQUEST: the JSON body IS the ``proposed_massing`` block (an object). The route runs the
untrusted-edge hardening the DB-034(a)/(b) gate owns and then the accepted semantic
validator, and returns either a typed field-named REFUSAL (verbatim from the gate /
validator, with bounded strings) or a minimal ACCEPTANCE ECHO carrying only the block's
integrity digest and the literal kind - never a derived value.

Untrusted-edge discipline (fail-closed, in order):

1. Feature-flag gate. Registered ALWAYS but reachable only when
   ``INTERNAL_RULE_EVAL_ENABLED`` is an explicit true token (REUSED - the proposal editor is
   part of the same internal property flow and ``app.config`` is out of this packet's scope,
   so it adds NO new flag), mirroring the accepted sibling internal routes exactly
   (``app.api.v1.condo_records`` / ``lot_geometry``); absent/empty/unknown -> a generic
   ``404`` byte-indistinguishable from an unmounted path. ``include_in_schema=False`` so it
   never appears in the OpenAPI document.
2. Request-size ceiling (BOUNDED STREAMING). A declared ``Content-Length`` over
   :data:`MAX_BODY_BYTES` is an early ``413`` fast path, but it is NOT the only enforcement:
   the body is accumulated chunk-by-chunk and refused with a typed ``413`` the instant the
   aggregate exceeds the ceiling - before the remaining stream is consumed and before any JSON
   parse - so a chunked / absent-``Content-Length`` body (which carries no length) and a
   declared length that under-reports the true size are both caught, and nothing is ever
   buffered beyond the ceiling.
3. Strict JSON. Malformed JSON (or a body too deeply nested for the parser) is a typed
   ``422``; a body that is not a JSON object is a typed ``422``; a body carrying NaN/Infinity
   or a non-encodable string (an unpaired surrogate) is a typed ``422`` - proven with the
   SAME encoder settings the renderer uses (``json.dumps(..., allow_nan=False)`` then
   ``ensure_ascii=False`` + ``.encode("utf-8")``), so the guard and the renderer can never
   disagree and no malformed value can reach the digest or raise mid-response.
4. The DB-034(a)/(b) input gate then the accepted validator
   (:func:`app.scenario.proposal_input_gate.validate_proposed_massing_input`): a refusal is a
   typed ``422`` naming the exact ``field`` with a BOUNDED message; no stack trace, filesystem
   path, secret, or internal string ever appears.

Every non-disabled response carries ``X-Correlation-ID``. The exact emitted (HTTP status,
state) pairs are the single source of truth
:data:`PROPOSAL_VALIDATION_STATUS_STATE_MATRIX` below; the 200 acceptance echo carries a
``result`` discriminator and NO ``state`` (mirroring the sibling routes' 200 documents).
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import internal_rule_eval_enabled
from app.scenario.proposal import ProposedMassingError
from app.scenario.proposal_input_gate import validate_proposed_massing_input

__all__ = [
    "MAX_BODY_BYTES",
    "PROPOSAL_VALIDATION_STATUS_STATE_MATRIX",
    "router",
]

logger = logging.getLogger("app.api.v1.proposal_validation")

router = APIRouter(prefix="/api/v1", tags=["proposal_validation"])

# Documented raw request-body ceiling. Comfortably fits a realistic at-budget proposed
# massing block (thousands of summed outline positions plus short-id walls); a body beyond it
# is a paste / generation error, refused with a typed 413 BEFORE the body is parsed.
MAX_BODY_BYTES = 262144  # 256 KiB

# A reflected refusal message is bounded to this many characters (cap + truncation marker) so
# a user value the accepted validator embeds via ``repr`` for a field the gate does not own
# (e.g. a duplicate wall id at or under the gate's string ceiling, or the ``kind`` literal)
# can never be echoed unbounded. The gate itself already bounded-reprs the fields it owns.
_MAX_REFUSAL_MESSAGE_CHARS = 400

_PROPOSED_KIND = "proposed"

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every emission path below is a member. The 200
# acceptance echo carries a ``result`` discriminator and NO ``state`` (pair (200, None)),
# mirroring the accepted sibling routes; the disabled / not-found sentinel is a generic 404
# with no body hint. A malformed / non-finite / non-encodable body and a typed validator or
# gate refusal share the (422, "validation_error") pair; an oversized body is (413,
# "payload_too_large"); an unexpected internal defect is a generic (500, "internal_error").
# ---------------------------------------------------------------------------
PROPOSAL_VALIDATION_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # acceptance echo (``result`` = "accepted"; NO derived value)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (422, "validation_error"),  # malformed/non-finite/non-encodable body OR typed refusal
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. Carries NO
    correlation id and NO body hint, so a disabled feature is indistinguishable from a route
    that does not exist (fail-safe disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _bounded_message(message: str) -> str:
    """Bound a reflected refusal message to :data:`_MAX_REFUSAL_MESSAGE_CHARS` with an
    explicit truncation marker, so no user value embedded by the accepted validator can be
    echoed unbounded in a response."""
    if len(message) <= _MAX_REFUSAL_MESSAGE_CHARS:
        return message
    return (
        f"{message[:_MAX_REFUSAL_MESSAGE_CHARS]}"
        f"...<truncated; {len(message)} chars total>"
    )


def _validation_error(
    message: str, correlation_id: str, *, field: str | None = None
) -> JSONResponse:
    """Typed (422, "validation_error"): a malformed / non-finite / non-encodable body, or a
    typed gate/validator refusal naming the exact ``field``. Carries a BOUNDED reason, never a
    traceback / path / secret / internal string."""
    body: dict[str, object] = {
        "state": "validation_error",
        "message": _bounded_message(message),
        "correlation_id": correlation_id,
    }
    if field is not None:
        body["field"] = field
    return _json(422, body, correlation_id)


def _payload_too_large(correlation_id: str) -> JSONResponse:
    """Typed (413, "payload_too_large") for a raw body over :data:`MAX_BODY_BYTES`, read
    before the body is parsed."""
    return _json(
        413,
        {
            "state": "payload_too_large",
            "message": f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the correlation id only (no
    ``str(exc)`` / traceback: the block may embed untrusted strings)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _block_digest(block: dict) -> str:
    """A stable integrity digest of the validated block: SHA-256 over its canonical JSON
    (sorted keys, compact separators). An identity fingerprint of the INPUT, not a derived
    zoning value. Safe because the caller proved the block strict-JSON-safe and encodable
    first."""
    canonical = json.dumps(
        block, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _declared_content_length(request: Request) -> int | None:
    """Parse the ``Content-Length`` header into a non-negative int, or ``None`` when it is
    absent or unparseable. Used ONLY for an early 413 fast path - never the sole size
    enforcement, since a chunked / absent-``Content-Length`` body carries no length and a
    declared length can under-report the true size; the bounded stream accumulation below is
    authoritative."""
    raw = request.headers.get("content-length")
    if raw is None:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value >= 0 else None


async def _read_body_within_ceiling(
    stream: AsyncIterator[bytes], max_bytes: int
) -> tuple[bytes, bool]:
    """Accumulate a request-body byte stream, stopping AS SOON AS the running total exceeds
    ``max_bytes``. Returns ``(raw, too_large)``. When ``too_large`` is true the caller MUST
    return a typed 413 and MUST NOT parse ``raw`` (which is then empty): the accumulation stops
    at the first over-ceiling chunk WITHOUT draining the remaining stream and WITHOUT ever
    buffering more than one chunk past the ceiling, so an oversized body can neither exhaust
    memory nor reach the JSON parser. Empty chunks (the stream's terminal ``b""``) are
    skipped."""
    chunks: list[bytes] = []
    total = 0
    async for chunk in stream:
        if not chunk:
            continue
        total += len(chunk)
        if total > max_bytes:
            return b"", True
        chunks.append(chunk)
    return b"".join(chunks), False


@router.post("/proposal-validation", include_in_schema=False)
async def post_proposal_validation(request: Request) -> JSONResponse:
    """Validate an editor-authored ``proposed_massing`` block. Feature-flag gated OFF by
    default (reuses INTERNAL_RULE_EVAL_ENABLED), mirroring the sibling internal routes."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the feature
    # exists. Checked FIRST, before a correlation id is minted or the body is read.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 2. Raw body size ceiling BEFORE parsing anything, via BOUNDED STREAMING accumulation. A
    #    declared Content-Length over the ceiling is refused immediately (a fast path that
    #    never touches the stream), but it is NOT the only enforcement: the body is then
    #    accumulated chunk-by-chunk and refused the instant the aggregate exceeds
    #    MAX_BODY_BYTES - before the remaining stream is consumed and before any JSON parse -
    #    so a chunked / absent-Content-Length body and an under-reporting length are both
    #    caught, and nothing is ever buffered beyond the ceiling.
    declared_length = _declared_content_length(request)
    if declared_length is not None and declared_length > MAX_BODY_BYTES:
        logger.info(
            "proposal_validation_v1 payload_too_large declared_content_length=%d "
            "correlation_id=%s",
            declared_length, correlation_id,
        )
        return _payload_too_large(correlation_id)
    raw, too_large = await _read_body_within_ceiling(request.stream(), MAX_BODY_BYTES)
    if too_large:
        logger.info(
            "proposal_validation_v1 payload_too_large streamed_over_ceiling "
            "max_bytes=%d correlation_id=%s",
            MAX_BODY_BYTES, correlation_id,
        )
        return _payload_too_large(correlation_id)

    # 3. Parse. ANY parse failure (invalid JSON, or a body too deeply nested to parse ->
    #    RecursionError) is the caller's fault -> a typed 422, never an unhandled raise.
    if not raw or not raw.strip():
        return _validation_error(
            "request body must be a proposed_massing JSON object", correlation_id
        )
    try:
        block = json.loads(raw)
    except Exception:
        return _validation_error(
            "request body is not valid JSON (or is too deeply nested to parse)",
            correlation_id,
        )

    # 4. The body must be the proposed_massing block: a JSON object.
    if not isinstance(block, dict):
        return _validation_error(
            "request body must be a proposed_massing JSON object", correlation_id
        )

    # 5. Strict-JSON + renderer-parity guard: NaN/Infinity (json.loads accepts them) or a
    #    non-encodable string (an unpaired surrogate, which the ensure_ascii=False renderer
    #    would raise on mid-response) is the caller's malformed input, refused here before it
    #    can reach the digest or the renderer. One expression exercises the SAME settings the
    #    renderer uses, so the guard and the renderer can never disagree.
    try:
        json.dumps(block, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        return _validation_error(
            "request body is not strict-JSON serializable (NaN/Infinity) or contains "
            "non-encodable text (an unpaired surrogate)",
            correlation_id,
        )

    # 6. The DB-034(a)/(b) input gate, then the accepted validator. A typed refusal names the
    #    exact field with a bounded message; any unexpected defect is a generic 500.
    try:
        validate_proposed_massing_input(block)
    except ProposedMassingError as exc:
        logger.info(
            "proposal_validation_v1 refused field=%s correlation_id=%s",
            exc.field, correlation_id,
        )
        return _validation_error(str(exc), correlation_id, field=exc.field)
    except Exception:
        logger.error(
            "proposal_validation_v1 unexpected_error stage=validate correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 7. Acceptance echo: the block's integrity digest + the literal kind. NO derived value of
    #    any kind (D-076-R002) - no area, lot coverage, FAR, or height sum. The echo strings
    #    are fully controlled ASCII; the guard is defense-in-depth (step 5 already proved the
    #    block, hence its digest, encodable).
    document = {
        "result": "accepted",
        "kind": _PROPOSED_KIND,
        "block_digest": _block_digest(block),
        "correlation_id": correlation_id,
    }
    try:
        json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        logger.error(
            "proposal_validation_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)
    return _json(200, document, correlation_id)
