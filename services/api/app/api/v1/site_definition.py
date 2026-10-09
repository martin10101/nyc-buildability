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
import os
import uuid
from collections.abc import AsyncIterator, Callable, Mapping
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
    FieldTooLongError,
    InvalidConfirmerError,
    ListResultTooLargeError,
    ParcelSetMismatchError,
    ParcelShapeError,
    RecordIdCollisionError,
    ResolutionProvenanceSnapshot,
    SiteDefinitionError,
    SiteDefinitionStore,
    SupersessionChainTooDeepError,
    TransitionReasonRequiredError,
    build_site_definition_block,
    create_confirmation,
    default_site_definition_store,
    make_confirmer,
)

__all__ = [
    "MAX_BODY_BYTES",
    "SITE_DEFINITION_STATUS_STATE_MATRIX",
    "SITE_DEFINITION_WRITE_ENABLED_ENV_VAR",
    "SiteDefinitionResolver",
    "get_site_definition_resolver",
    "get_site_definition_store",
    "router",
    "site_definition_write_enabled",
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
# DEDICATED, DEFAULT-OFF mount gate for the WRITE route (DB-040(f)). This is the
# ONE new flag the mount packet introduces. It gates REGISTRATION in main.py
# (``main.py`` calls ``include_router`` only when this is an explicit true token),
# so an OFF value means the write routes are ABSENT from the app entirely - a
# request to any site-definition path hits FastAPI's own generic 404, byte-
# identical to an unmounted path. It is DELIBERATELY separate from the
# ``INTERNAL_RULE_EVAL_ENABLED`` flag that gates the read surfaces: enabling the
# general internal flag (e.g. to expose the read-only condo-records document) must
# NOT expose this unauthenticated, ephemeral, self-attested WRITE route. Both must
# stay off in production until B-001 authentication and a durable store land; the
# DB-040(f) read-authorization posture for confirmer identity is deferred behind
# this gate. Mirrors the ``app.config`` fail-safe pattern: absent / empty /
# unknown -> OFF (only an explicit true token turns it on).
SITE_DEFINITION_WRITE_ENABLED_ENV_VAR = "SITE_DEFINITION_WRITE_ENABLED"
_MOUNT_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})


def site_definition_write_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the site-definition WRITE route may be MOUNTED (registered).

    Returns True ONLY for an explicit true token in
    :data:`SITE_DEFINITION_WRITE_ENABLED_ENV_VAR`; absent / empty / unknown -> False
    (fail safe), so production (which sets nothing) never registers the route. Read
    each call so a test can flip it with ``monkeypatch.setenv`` and rebuild the app.
    Independent of the handler-level ``internal_rule_eval_enabled`` gate: the write
    route requires BOTH to serve, and this one is what keeps it off in a config that
    turns the general internal flag on for the reads."""
    source = os.environ if env is None else env
    raw = source.get(SITE_DEFINITION_WRITE_ENABLED_ENV_VAR)
    if raw is None:
        return False
    return raw.strip().lower() in _MOUNT_TRUE_TOKENS

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
    # [DB-040(e)] an id collision is a state conflict; [DB-040(d)] a chain past
    # the depth cap, and a list past the response cap, are likewise conflicts. All
    # are unreachable from this route (server uuid4 ids; the caps are far above any
    # per-request chain, and the chain cap is <= the list cap) but are mapped
    # explicitly so a library-boundary refusal stays inside the matrix.
    RecordIdCollisionError: (409, "conflict"),
    SupersessionChainTooDeepError: (409, "conflict"),
    ListResultTooLargeError: (409, "conflict"),
    ParcelSetMismatchError: (422, "validation_error"),
    # [DB-040(i)] a parcel-SHAPE defect gets its own class and maps to a
    # validation error - NOT mislabelled invalid_confirmer (its reject_code
    # already distinguishes it in the body).
    ParcelShapeError: (422, "validation_error"),
    InvalidConfirmerError: (422, "validation_error"),
    FieldTooLongError: (422, "validation_error"),
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
    """The SINGLE matrix-checked emission point ([DB-040(k)]). Every non-sentinel
    response this module returns passes through here, and its ``(status, state)``
    pair is asserted against :data:`SITE_DEFINITION_STATUS_STATE_MATRIX` - the
    matrix's documentation as "the single source of truth for every emission path"
    is now ENFORCED, not decorative. ``state`` is ``body["state"]`` for a typed
    response, or ``None`` for a success document (which carries no ``state`` key).

    An off-matrix pair is a SERVER programming error, never a caller error: it
    FAILS CLOSED to the in-matrix ``(500, "internal_error")`` rather than emit an
    undocumented pair (and cannot recurse - the fallback builds its response
    directly). The generic unmounted/flag-off sentinel (:func:`_not_found`) is the
    one deliberate exception: it is ``(404, None)`` - in the matrix - but must be
    byte-identical to FastAPI's default (no correlation header), so it is built
    directly."""
    state = body.get("state")
    if (status_code, state) not in SITE_DEFINITION_STATUS_STATE_MATRIX:
        logger.error(
            "site_definition_v1 off_matrix_emission status=%d state=%r correlation_id=%s",
            status_code,
            state,
            correlation_id,
        )
        return JSONResponse(
            status_code=500,
            content={
                "state": "internal_error",
                "message": "unexpected internal error; see server logs by correlation id",
                "correlation_id": correlation_id,
            },
            headers={"X-Correlation-ID": correlation_id},
        )
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
    """Re-read the resolver seam and require a MULTI-LOT outcome with a condo key
    (a site definition treats two or more base lots as one KEYED site). Anything
    else is a typed 422 - there is no multi-lot site to confirm. Used by CREATE
    and SUPERSEDE only; revoke must not require a healthy multi-lot resolution
    (D-051), so it resolves the condo key best-effort instead."""
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
    # [DB-040(j)] close the condo_key None write/read asymmetry AT THE WRITE SIDE:
    # a multi-lot resolution with no condo key cannot be KEYED, so a confirmation
    # recorded for it could never be surfaced by the read document (which keys on
    # condo_key). Refuse rather than record an un-surfaceable confirmation - the
    # write and read now agree in both directions on a null condo key (write
    # refuses; read shows nothing).
    if resolution.condo_key is None:
        return None, _error(
            422,
            "validation_error",
            "this multi-lot resolution carries no condo key, so a site definition "
            "cannot be recorded for it (a confirmation with no condo key could "
            "never be surfaced on the records document)",
            correlation_id,
        )
    return resolution, None


def _resolve_condo_key_best_effort(
    canonical: str,
    correlation_id: str,
    resolver: SiteDefinitionResolver,
) -> str | None:
    """Best-effort condo grouping for the REVOKE binding ([DB-040(a)/(b)], D-051).

    Revoke is the ONLY human path to withdraw a confirmation, so - UNLIKE create /
    supersede (which require a healthy multi-lot resolution via
    :func:`_resolve_multi_lot`) - it must NOT be blocked by a degraded resolver.
    Refusing a withdrawal because live resolution is unhealthy is the WRONG
    fail-direction (D-051). This resolves the condo key best-effort:

    - a HEALTHY multi-lot resolution carrying a condo key -> that key is
      authoritative (the stored record must belong to it, mirroring supersede's
      binding);
    - ANY degraded outcome (a resolver exception, or a non-multi-lot / unresolved /
      error / null-condo-key resolution) -> ``None``.

    ``None`` is NEVER "skip scoping": the store treats it as "fall back to the
    record's own recorded ``addressed_bbl``" (see
    :meth:`InMemorySiteDefinitionStore._matches_addressed_property`), so a
    foreign-property probe still fails while a legitimate withdrawal at the
    record's own property still succeeds. Never raises - a resolver failure is a
    degraded (``None``) key, not a 500."""
    try:
        resolution = resolver(canonical, correlation_id)
    except Exception:
        logger.info(
            "site_definition_v1 revoke_resolver_degraded stage=resolve correlation_id=%s",
            correlation_id,
        )
        return None
    if resolution.outcome == OUTCOME_MULTI_LOT and resolution.condo_key is not None:
        return resolution.condo_key
    return None


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
    resolve: SiteDefinitionResolver = Depends(get_site_definition_resolver),  # noqa: B008
    store: SiteDefinitionStore = Depends(get_site_definition_store),  # noqa: B008
) -> JSONResponse:
    """Revoke an active confirmation (terminal; reason REQUIRED).

    [DB-040(a)/(b), D-051] The revocation is SCOPED to the property in the request
    path, but the scope is evaluated in the store BEFORE the ACTIVE-status check so
    every cross-property probe reads an indistinguishable 404 (no 409-vs-404 status
    oracle). The binding is a DETERMINISTIC association that survives a degraded
    resolver: the resolver is re-read best-effort for ``{bbl}``
    (:func:`_resolve_condo_key_best_effort`);
    a healthy multi-lot resolution's condo key is authoritative, and ANY degraded
    outcome yields ``None``, which the store resolves against the record's own
    recorded ``addressed_bbl`` rather than skipping the scope check. Revoke is the
    only human path to undo a confirmation, so - unlike create / supersede - it is
    NEVER blocked by an unhealthy resolver (refusing withdrawal on a degraded
    resolver is the wrong fail-direction, D-051)."""
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
    # Best-effort condo key (None when the resolver degrades); NOT _resolve_multi_lot,
    # which would 422/500 a degraded resolver and block the only withdrawal path.
    condo_key = _resolve_condo_key_best_effort(canonical, correlation_id, resolve)
    confirmer = block.get("confirmer")
    confirmer_map = confirmer if isinstance(confirmer, dict) else {}
    try:
        actor = make_confirmer(confirmer_map.get("name"), confirmer_map.get("role"))
        reason = block.get("reason")
        view = store.revoke(
            record_id,
            addressed_bbl=canonical,
            condo_key=condo_key,
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
