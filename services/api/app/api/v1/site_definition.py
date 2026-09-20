"""Internal, UNMOUNTED site-definition confirmation API (task M5-T059, D-078).

Create / list / supersede / revoke the typed, append-only
:class:`~app.site_definition.records.SiteDefinitionConfirmation` records that back
the owner's one-click "treat these lots as one site" flow. It is a HUMAN
professional's recorded act (D-078-R002): the route never auto-selects a site, and
slice 1 changes NO calculation path - creating a confirmation does not alter any
allowance, and the unconfirmed multi-lot refusal stays byte-identical.

DELIBERATELY UNMOUNTED. This router is NOT included in ``app.main`` - that file is
held by the live M5-T057 lane and the one-line mount lands in a later packet.
Production-unreachable is the SAFE state for a write-shaped endpoint whose store is
ephemeral (in-memory, B-001) and whose identity is self-attested (auth B-001): a
confirmation cannot yet be durably or authentically recorded, so it must not be
reachable in production. The tests build a LOCAL ``FastAPI()`` app, include this
router, and drive it with ``TestClient`` (the first such precedent in this suite;
recorded in the producer report), so the route's discipline is fully proven
offline without touching ``main.py``.

Route posture mirrors the accepted internal siblings EXACTLY
(``app.api.v1.condo_records`` / ``proposal_validation``):

- Feature-flag gated on the EXISTING ``INTERNAL_RULE_EVAL_ENABLED`` flag (NO new
  flag). Absent/unknown -> a generic ``404`` byte-indistinguishable from an
  unmounted path. ``include_in_schema=False`` so it never appears in OpenAPI.
- Body-carrying POSTs enforce the ``proposal_validation`` request-size discipline:
  an early ``413`` on a declared over-ceiling ``Content-Length`` PLUS bounded
  streaming accumulation that refuses the instant the aggregate exceeds the ceiling
  (a chunked / under-reporting body is still caught), then strict-JSON parsing.
- A malformed BBL is a typed ``422`` before any resolver call. Every typed
  site-definition refusal is serialized uniformly with a BOUNDED message; no stack
  trace, path, secret, or internal string is ever echoed.

The resolver and the store are INJECTED (the lot-geometry dependency pattern) so
the whole suite runs offline: the route RE-READS the resolver seam to obtain the
authoritative base lots and never trusts a caller-supplied resolution snapshot for
the strict parcel binding.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import internal_rule_eval_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.condo_base_lot import (
    OUTCOME_MULTI_LOT,
    CondoResolution,
    resolve_condo_billing,
)
from app.site_definition import (
    ConfirmationNotActiveError,
    ConfirmationNotFoundError,
    DuplicateActiveConfirmationError,
    ParcelSetMismatchError,
    ResolutionProvenanceSnapshot,
    SiteDefinitionError,
    SiteDefinitionStore,
    TransitionReasonRequiredError,
    build_site_definition_block,
    create_confirmation,
    default_site_definition_store,
    make_confirmer,
)

__all__ = [
    "MAX_BODY_BYTES",
    "SITE_DEFINITION_STATUS_STATE_MATRIX",
    "SiteDefinitionResolver",
    "get_site_definition_resolver",
    "get_site_definition_store",
    "router",
]

logger = logging.getLogger("app.api.v1.site_definition")

router = APIRouter(prefix="/api/v1", tags=["site_definition"])

# Documented raw request-body ceiling (a confirmation body is a short parcel list
# plus a confirmer + reason; anything beyond this is a paste / generation error).
MAX_BODY_BYTES = 65536  # 64 KiB

# A reflected refusal message is bounded to this many characters so a user value a
# typed refusal embeds can never be echoed unbounded.
_MAX_REFUSAL_MESSAGE_CHARS = 400

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix - the single source of truth for every
# emission path. A successful create is (201, None); list / supersede / revoke
# success documents are (200, None). The flag-off / unmounted sentinel is a
# generic (404, None) with no body hint; an unknown record id is the TYPED
# (404, "not_found") (distinguished from the sentinel by its state). A conflict
# (duplicate active, or superseding/revoking a non-active record) is (409,
# "conflict"); a malformed BBL / body / parcel mismatch / missing reason / bad
# confirmer / non-multi-lot site is (422, "validation_error"); an over-ceiling
# body is (413, "payload_too_large"); an unexpected defect is (500,
# "internal_error").
# ---------------------------------------------------------------------------
SITE_DEFINITION_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),
        (201, None),
        (404, None),
        (404, "not_found"),
        (409, "conflict"),
        (413, "payload_too_large"),
        (422, "validation_error"),
        (500, "internal_error"),
    }
)

# The typed refusal -> (HTTP status, state) mapping. A base SiteDefinitionError
# not listed here is a validation refusal by default (fail-closed to 422, never a
# 500 that would hide a typed cause).
_REFUSAL_STATUS: dict[type[SiteDefinitionError], tuple[int, str]] = {
    DuplicateActiveConfirmationError: (409, "conflict"),
    ConfirmationNotActiveError: (409, "conflict"),
    ConfirmationNotFoundError: (404, "not_found"),
    ParcelSetMismatchError: (422, "validation_error"),
    TransitionReasonRequiredError: (422, "validation_error"),
}


# Resolver seam: (canonical_bbl, correlation_id) -> CondoResolution. Default is
# the accepted billing policy seam; tests inject recorded resolutions.
SiteDefinitionResolver = Callable[[str, str], CondoResolution]


def _default_resolver(canonical_bbl: str, correlation_id: str) -> CondoResolution:
    return resolve_condo_billing(canonical_bbl, correlation_id=correlation_id)


def get_site_definition_resolver() -> SiteDefinitionResolver:
    """Dependency returning the resolution seam (test override point)."""
    return _default_resolver


def get_site_definition_store() -> SiteDefinitionStore:
    """Dependency returning the site-definition store (test override point).

    Binds to the ONE shared package default (``default_site_definition_store``) -
    the SAME object the condo-records read document consumes - so a confirmation
    created here is visible on that document without a durable store. The store is
    B-001-deferred and ephemeral and this write route is UNMOUNTED, so the shared
    default is never reachable in production. Tests override this with a fresh
    store per test."""
    return default_site_definition_store()


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path (no
    correlation id, no body hint) - the fail-safe disable / unmounted sentinel."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _bounded_message(message: str) -> str:
    if len(message) <= _MAX_REFUSAL_MESSAGE_CHARS:
        return message
    return (
        f"{message[:_MAX_REFUSAL_MESSAGE_CHARS]}"
        f"...<truncated; {len(message)} chars total>"
    )


def _error(status_code: int, state: str, message: str, correlation_id: str) -> JSONResponse:
    return _json(
        status_code,
        {
            "state": state,
            "message": _bounded_message(message),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _payload_too_large(correlation_id: str) -> JSONResponse:
    return _error(
        413,
        "payload_too_large",
        f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes",
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _refuse(exc: SiteDefinitionError, correlation_id: str) -> JSONResponse:
    """Serialize a typed site-definition refusal uniformly with a bounded message.
    Fail-closed: an unmapped SiteDefinitionError becomes a 422 validation error,
    never a 500 (a typed cause is never hidden as an internal defect)."""
    status_code, state = _REFUSAL_STATUS.get(type(exc), (422, "validation_error"))
    logger.info(
        "site_definition_v1 refused reject_code=%s status=%d correlation_id=%s",
        getattr(exc, "reject_code", "site_definition_error"),
        status_code,
        correlation_id,
    )
    body = {
        "state": state,
        "message": _bounded_message(str(exc)),
        "reject_code": getattr(exc, "reject_code", "site_definition_error"),
        "correlation_id": correlation_id,
    }
    return _json(status_code, body, correlation_id)


def _declared_content_length(request: Request) -> int | None:
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
    """Accumulate a request body, stopping AS SOON AS the running total exceeds
    ``max_bytes`` (returns ``(raw, too_large)``; on ``too_large`` the caller MUST
    return 413 and MUST NOT parse the empty ``raw``). Mirrors
    ``proposal_validation._read_body_within_ceiling`` exactly."""
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


async def _read_json_object(
    request: Request, correlation_id: str
) -> tuple[dict | None, JSONResponse | None]:
    """Read a body-carrying request through the ceiling discipline and parse it as
    a JSON object. Returns ``(block, None)`` on success or ``(None, response)``
    with the typed 413/422 to return."""
    declared = _declared_content_length(request)
    if declared is not None and declared > MAX_BODY_BYTES:
        return None, _payload_too_large(correlation_id)
    raw, too_large = await _read_body_within_ceiling(request.stream(), MAX_BODY_BYTES)
    if too_large:
        return None, _payload_too_large(correlation_id)
    if not raw or not raw.strip():
        return None, _error(
            422, "validation_error", "request body must be a JSON object", correlation_id
        )
    try:
        block = json.loads(raw)
    except Exception:
        return None, _error(
            422,
            "validation_error",
            "request body is not valid JSON (or is too deeply nested to parse)",
            correlation_id,
        )
    if not isinstance(block, dict):
        return None, _error(
            422, "validation_error", "request body must be a JSON object", correlation_id
        )
    return block, None


def _normalize_bbl_or_422(
    bbl: str, correlation_id: str
) -> tuple[str | None, JSONResponse | None]:
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()
        return None, _error(
            422, "validation_error", payload["message"], correlation_id
        )
    return normalized.canonical, None


def _snapshot(resolution: CondoResolution) -> ResolutionProvenanceSnapshot:
    """Byte-copy the resolution provenance the CondoResolution showed, so the
    confirmation records WHY these parcels were the site."""
    return ResolutionProvenanceSnapshot(
        source_id=resolution.source_id,
        dataset_ids=tuple(resolution.dataset_ids),
        retrieved_at=resolution.retrieved_at,
        resolution_path=resolution.resolution_path,
    )


def _resolve_multi_lot(
    canonical: str,
    correlation_id: str,
    resolver: SiteDefinitionResolver,
) -> tuple[CondoResolution | None, JSONResponse | None]:
    """Re-read the resolver seam and require a MULTI-LOT outcome (a site
    definition treats two or more base lots as one site). Anything else is a typed
    422 - there is no multi-lot site to confirm."""
    try:
        resolution = resolver(canonical, correlation_id)
    except Exception:
        logger.error(
            "site_definition_v1 unexpected_error stage=resolve correlation_id=%s",
            correlation_id,
        )
        return None, _internal_error_500(correlation_id)
    if resolution.outcome != OUTCOME_MULTI_LOT:
        return None, _error(
            422,
            "validation_error",
            "no multi-lot site to confirm: the entered BBL does not resolve to two "
            "or more recorded base lots, so there is nothing to treat as one site",
            correlation_id,
        )
    return resolution, None


@router.post(
    "/properties/{bbl}/site-definition-confirmations", include_in_schema=False
)
async def create_site_definition_confirmation(
    bbl: str,
    request: Request,
    resolve: SiteDefinitionResolver = Depends(get_site_definition_resolver),  # noqa: B008
    store: SiteDefinitionStore = Depends(get_site_definition_store),  # noqa: B008
) -> JSONResponse:
    """Create an active site-definition confirmation for a multi-lot condo."""
    if not internal_rule_eval_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex
    canonical, refusal = _normalize_bbl_or_422(bbl, correlation_id)
    if refusal is not None:
        return refusal
    assert canonical is not None
    block, body_refusal = await _read_json_object(request, correlation_id)
    if body_refusal is not None:
        return body_refusal
    assert block is not None
    resolution, resolve_refusal = _resolve_multi_lot(canonical, correlation_id, resolve)
    if resolve_refusal is not None:
        return resolve_refusal
    assert resolution is not None
    confirmer = block.get("confirmer")
    confirmer_map = confirmer if isinstance(confirmer, dict) else {}
    try:
        confirmation = create_confirmation(
            condo_key=resolution.condo_key or canonical,
            billing_bbl=canonical,
            entered_bbl=canonical,
            proposed_parcels=block.get("parcels"),
            resolver_base_bbls=resolution.base_bbls,
            confirmer_name=confirmer_map.get("name"),
            confirmer_role=confirmer_map.get("role"),
            confirmed_at=datetime.now(UTC),
            provenance=_snapshot(resolution),
            note=block.get("note"),
        )
        view = store.create(confirmation)
    except SiteDefinitionError as exc:
        return _refuse(exc, correlation_id)
    except Exception:
        logger.error(
            "site_definition_v1 unexpected_error stage=create correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)
    return _json(201, view.to_payload(), correlation_id)


@router.get(
    "/properties/{bbl}/site-definition-confirmations", include_in_schema=False
)
def list_site_definition_confirmations(
    bbl: str,
    resolve: SiteDefinitionResolver = Depends(get_site_definition_resolver),  # noqa: B008
    store: SiteDefinitionStore = Depends(get_site_definition_store),  # noqa: B008
) -> JSONResponse:
    """List every confirmation (active, superseded, revoked) for the condo, newest
    first, as the ``site_definition`` block document."""
    if not internal_rule_eval_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex
    canonical, refusal = _normalize_bbl_or_422(bbl, correlation_id)
    if refusal is not None:
        return refusal
    assert canonical is not None
    try:
        resolution = resolve(canonical, correlation_id)
    except Exception:
        logger.error(
            "site_definition_v1 unexpected_error stage=list_resolve correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)
    condo_key = resolution.condo_key
    resolver_base_bbls = (
        resolution.base_bbls if resolution.outcome == OUTCOME_MULTI_LOT else None
    )
    views = store.list_for_condo_key(condo_key) if condo_key is not None else ()
    block = build_site_definition_block(
        condo_key=condo_key,
        views=views,
        resolver_base_bbls=resolver_base_bbls,
    )
    return _json(200, block, correlation_id)


@router.post(
    "/properties/{bbl}/site-definition-confirmations/{record_id}/supersede",
    include_in_schema=False,
)
async def supersede_site_definition_confirmation(
    bbl: str,
    record_id: str,
    request: Request,
    resolve: SiteDefinitionResolver = Depends(get_site_definition_resolver),  # noqa: B008
    store: SiteDefinitionStore = Depends(get_site_definition_store),  # noqa: B008
) -> JSONResponse:
    """Supersede an active confirmation with a new one (reason REQUIRED)."""
    if not internal_rule_eval_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex
    canonical, refusal = _normalize_bbl_or_422(bbl, correlation_id)
    if refusal is not None:
        return refusal
    assert canonical is not None
    block, body_refusal = await _read_json_object(request, correlation_id)
    if body_refusal is not None:
        return body_refusal
    assert block is not None
    resolution, resolve_refusal = _resolve_multi_lot(canonical, correlation_id, resolve)
    if resolve_refusal is not None:
        return resolve_refusal
    assert resolution is not None
    confirmer = block.get("confirmer")
    confirmer_map = confirmer if isinstance(confirmer, dict) else {}
    try:
        new_confirmation = create_confirmation(
            condo_key=resolution.condo_key or canonical,
            billing_bbl=canonical,
            entered_bbl=canonical,
            proposed_parcels=block.get("parcels"),
            resolver_base_bbls=resolution.base_bbls,
            confirmer_name=confirmer_map.get("name"),
            confirmer_role=confirmer_map.get("role"),
            confirmed_at=datetime.now(UTC),
            provenance=_snapshot(resolution),
            note=block.get("note"),
            reason=block.get("reason"),
            supersedes_id=record_id,
        )
        view = store.supersede(record_id, new_confirmation)
    except SiteDefinitionError as exc:
        return _refuse(exc, correlation_id)
    except Exception:
        logger.error(
            "site_definition_v1 unexpected_error stage=supersede correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)
    return _json(200, view.to_payload(), correlation_id)


@router.post(
    "/properties/{bbl}/site-definition-confirmations/{record_id}/revoke",
    include_in_schema=False,
)
async def revoke_site_definition_confirmation(
    bbl: str,
    record_id: str,
    request: Request,
    store: SiteDefinitionStore = Depends(get_site_definition_store),  # noqa: B008
) -> JSONResponse:
    """Revoke an active confirmation (terminal; reason REQUIRED)."""
    if not internal_rule_eval_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex
    canonical, refusal = _normalize_bbl_or_422(bbl, correlation_id)
    if refusal is not None:
        return refusal
    assert canonical is not None
    block, body_refusal = await _read_json_object(request, correlation_id)
    if body_refusal is not None:
        return body_refusal
    assert block is not None
    confirmer = block.get("confirmer")
    confirmer_map = confirmer if isinstance(confirmer, dict) else {}
    try:
        actor = make_confirmer(confirmer_map.get("name"), confirmer_map.get("role"))
        reason = block.get("reason")
        view = store.revoke(
            record_id,
            reason=reason if isinstance(reason, str) else "",
            actor=actor,
            at=datetime.now(UTC).isoformat(),
        )
    except SiteDefinitionError as exc:
        return _refuse(exc, correlation_id)
    except Exception:
        logger.error(
            "site_definition_v1 unexpected_error stage=revoke correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)
    return _json(200, view.to_payload(), correlation_id)
