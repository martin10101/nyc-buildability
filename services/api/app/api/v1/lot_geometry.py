"""GET /api/v1/properties/{bbl}/lot-geometry - internal display-only lot outline
(task M5-T020, D-040-R001).

Exposes the official NYC DCP MapPLUTO parcel geometry to the web as an
approximate, DISPLAY-ONLY EPSG:4326 GeoJSON outline for the address confirm
card (MapLibre GL JS consumes 4326 directly). Route posture mirrors the accepted
scenario / evidence routes EXACTLY:

- Feature-flag gated OFF by default: reachable ONLY when the EXISTING
  ``INTERNAL_RULE_EVAL_ENABLED`` flag is an explicit true token (the outline is
  part of the same internal property flow and app.config is out of this packet's
  scope, so it REUSES that flag and adds NO new one). Absent/empty/unknown -> a
  generic ``404 Not Found`` byte-indistinguishable from an unmounted path (no
  correlation header, no hint the feature exists). ``include_in_schema=False`` so
  it never appears in OpenAPI.
- No authentication yet (service is internal/dev only; must not be public).
- BODY-LESS: only the ``bbl`` path parameter, so the untrusted-input surface is
  exactly zero. The BBL flows through ``normalize_bbl`` before any I/O; the query
  URL is built from the canonical BBL only and can never be injected.

DISPLAY-ONLY, NEVER MEASUREMENT. The transported 4326 geometry is for drawing an
outline; NO area or dimension is computed from it anywhere. The authoritative
EPSG:2263 connector (services/api/app/connectors/mappluto_geometry_arcgis.py)
remains the sole owner of measurement, canonical digests, and legal provenance
and is untouched.

HONEST TYPED OUTCOMES. single_lot / no_outline (condo unit or no-feature) /
multiple_features (review, geometry withheld, never a first-pick) / invalid_geometry
are all NORMAL 200 outline documents (each carries its own ``outcome`` field);
only genuine transport/parse faults become typed API errors. The fetch seam is
INJECTED (the M5-T003/M5-T013 dependency-injection pattern) so the whole test
suite runs fully OFFLINE against recorded fixtures.

``STATUS_STATE_MATRIX`` below is the single source of truth for every emitted
(HTTP status, state) pair.
"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.config import internal_rule_eval_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.mappluto_lot_outline import (
    LotOutlineContractError,
    LotOutlineError,
    LotOutlineFetcher,
    build_lot_outline,
    default_fetch,
)

__all__ = ["STATUS_STATE_MATRIX", "get_lot_outline_fetcher", "router"]

logger = logging.getLogger("app.api.v1.lot_geometry")

router = APIRouter(prefix="/api/v1", tags=["lot_geometry"])

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every emission path below is
# enumerated here. A successful outline is a 200 with NO ``state`` field (the
# outcome discriminator is the document's own ``outcome`` key); the disabled /
# not-found sentinel is a 404 with NO ``state`` (byte-identical to an unmounted
# path). The four honest outline outcomes are all (200, None).
# ---------------------------------------------------------------------------
STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # outline document (contract- and renderer-parity-checked)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL, no connector call
        (502, "upstream_error"),  # official service unreachable / bad status / error object
        (502, "malformed_response"),  # body not a well-formed GeoJSON FeatureCollection
        (502, "wrong_crs"),  # response CRS is not the requested EPSG:4326
        (502, "result_mismatch"),  # returned feature does not match the requested lot
        (500, "internal_contract_error"),  # assembled outline failed its contract / serialisation
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)

# Transport-fault error_type -> HTTP status (the honest outline outcomes are 200
# and never appear here). internal_contract_error is handled separately (500).
_ERROR_STATUS: dict[str, int] = {
    "upstream_error": 502,
    "malformed_response": 502,
    "wrong_crs": 502,
    "result_mismatch": 502,
}
_DEFAULT_ERROR_STATUS = 502


def get_lot_outline_fetcher() -> LotOutlineFetcher:
    """Dependency returning the outline transport seam (override point for
    tests). Production uses the live keyless GET; tests inject recorded
    fixtures via ``app.dependency_overrides`` so the suite runs offline."""
    return default_fetch


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. Carries
    NO correlation id and NO body hint, so a disabled feature is indistinguishable
    from a route that does not exist (fail-safe production disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the type +
    correlation id only (no str(exc)/traceback: the chain may embed untrusted
    upstream strings - payload-only logging policy)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_contract_error_500(correlation_id: str) -> JSONResponse:
    """Documented typed 500 for an assembled outline that FAILED canonical-schema
    or serialisation-safety validation before send. An invalid 200 is impossible."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the assembled outline document failed canonical-contract or "
                "serialisation validation and was not sent; see server logs by "
                "correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send.

    ``json.dumps(doc, allow_nan=False)`` rejects NaN/Infinity; the
    ``ensure_ascii=False`` + ``.encode('utf-8')`` form is EXACTLY what Starlette's
    ``JSONResponse.render`` uses and is the one that raises on an unpaired
    surrogate. Running BOTH lets the caller fail closed to a typed 500 instead of
    an untyped ASGI 500 (M5-T012 G5 BLOCKING-1)."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


@router.get("/properties/{bbl}/lot-geometry", include_in_schema=False)
def get_lot_geometry(
    bbl: str,
    fetch: LotOutlineFetcher = Depends(get_lot_outline_fetcher),  # noqa: B008
) -> JSONResponse:
    """Transport the display-only 4326 lot outline for one BBL. Feature-flag
    gated OFF by default (reuses INTERNAL_RULE_EVAL_ENABLED)."""
    # Guard 1 (fail-safe production disable): absent/unknown flag -> 404 with no
    # hint the feature exists. Checked FIRST, before a correlation id is minted or
    # any input is touched.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any connector call (typed 422; zero network I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "lot_geometry_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _json(
            422,
            {
                "state": "validation_error",
                "message": payload["message"],
                "correlation_id": correlation_id,
                "detail": {"code": payload["code"], "raw_value": payload["raw_value"]},
            },
            correlation_id,
        )

    # 2. Fetch + transport through the injected seam. The four honest outline
    #    outcomes are NORMAL 200 documents; only genuine faults become errors.
    try:
        outline = build_lot_outline(
            normalized.canonical, fetch=fetch, correlation_id=correlation_id
        )
    except LotOutlineContractError:
        logger.error(
            "lot_geometry_v1 contract_error correlation_id=%s", correlation_id
        )
        return _internal_contract_error_500(correlation_id)
    except LotOutlineError as exc:
        payload = exc.to_payload()
        logger.warning(
            "lot_geometry_v1 transport_error state=%s correlation_id=%s",
            payload["error_type"], correlation_id,
        )
        status_code = _ERROR_STATUS.get(payload["error_type"], _DEFAULT_ERROR_STATUS)
        return _json(
            status_code,
            {
                "state": payload["error_type"],
                "message": payload["message"],
                "correlation_id": correlation_id,
                "source_id": payload["source_id"],
                "detail": payload["detail"],
            },
            correlation_id,
        )
    except Exception:
        logger.error(
            "lot_geometry_v1 unexpected_error stage=transport correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 3. Renderer-parity serialisation guard before send (belt-and-suspenders on
    #    top of the connector's contract validation): fail closed to a typed 500,
    #    never an untyped ASGI 500, for any non-finite / unpaired-surrogate content.
    try:
        _assert_json_safe(outline)
    except Exception:
        logger.error(
            "lot_geometry_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_contract_error_500(correlation_id)

    return _json(200, outline, correlation_id)
