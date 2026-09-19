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

This module ALSO hosts an additive sibling endpoint,
``GET /api/v1/properties/{bbl}/record-address`` (task M5-T047, DB-032), which
transports the lot's PLUTO address-of-record as a display-only city RECORD (the
M5-T046 HJ A1 / OQ-5 gap). It is fully independent of the lot-geometry endpoint
above: it reuses the same feature-flag gate, normalize-first / injected-fetch-seam
discipline, typed-error taxonomy, and ``_assert_json_safe`` render guard, and owns
its own ``RECORD_ADDRESS_STATUS_STATE_MATRIX``. Its full posture is documented in
the section header at ``get_record_address`` below.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable

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
from app.connectors.pluto_soda import (
    DATASET_ID as PLUTO_DATASET_ID,
)
from app.connectors.pluto_soda import (
    SOURCE_ID as PLUTO_SOURCE_ID,
)
from app.connectors.pluto_soda import (
    PlutoConnectorError,
    PlutoFetchResult,
    fetch_by_bbl,
)

__all__ = [
    "RECORD_ADDRESS_STATUS_STATE_MATRIX",
    "STATUS_STATE_MATRIX",
    "get_lot_outline_fetcher",
    "get_pluto_record_fetch",
    "router",
]

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


# ---------------------------------------------------------------------------
# Record-address display channel (task M5-T047, DB-032). A SIBLING endpoint in
# this same route module surfaces the lot's PLUTO address-of-record (the "low
# number of range" address PLUTO stores per lot, e.g. "3622 13 AVENUE" for the
# corner lot whose matched frontage is "1279 37 STREET") so the confirm card can
# show it as a labeled CITY RECORD when it differs from the matched frontage
# (the M5-T046 HJ A1 / OQ-5 gap). It is ADDITIVE: the lot-geometry endpoint
# above is UNTOUCHED, the closed lot_geometry contract schema is UNTOUCHED, and
# the PLUTO row is consumed READ-ONLY through the accepted connector
# (app.connectors.pluto_soda) whose validation, typed-error taxonomy, and
# provenance are unchanged.
#
# RECORD, NOT MEASUREMENT: the address is transported VERBATIM for display as an
# official record; no value is derived from it. SODA omits null columns, so a
# PLUTO record carrying no ``address`` column is an HONEST TYPED ABSENCE
# (no_address_of_record) - never a fabricated or empty-string line. A connector
# fault surfaces as a TYPED error (never a fake absence). The three honest
# outcomes are all (200, None) with an ``outcome`` discriminator, mirroring the
# lot-geometry endpoint's own posture.
# ---------------------------------------------------------------------------

# Record fetch seam: (canonical_bbl, correlation_id) -> PlutoFetchResult. The
# override point for tests (offline recorded results), exactly like the
# lot-outline seam above.
PlutoRecordFetch = Callable[[str, str], PlutoFetchResult]

# EXACT (HTTP status, state) pairs the record-address endpoint emits. The three
# honest outcomes (address_of_record / no_address_of_record / no_record) are all
# (200, None); the disabled/unmounted sentinel is (404, None).
RECORD_ADDRESS_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # record-address document (the document's own outcome discriminates)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL, no connector call
        (429, "rate_limited"),  # SODA throttled through the retry budget
        (502, "source_unavailable"),  # official source unreachable / bad status
        (502, "schema_drift"),  # dataset contract changed
        (504, "timeout"),  # SODA request timed out through the retry budget
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)

# Connector error_type -> HTTP status. The honest outcomes are 200 and never
# appear here; any error_type not listed falls back to 502 (upstream fault).
_PLUTO_ERROR_STATUS: dict[str, int] = {
    "rate_limited": 429,
    "timeout": 504,
    "source_unavailable": 502,
    "schema_drift": 502,
}
_DEFAULT_PLUTO_ERROR_STATUS = 502

# The PLUTO column carrying the address-of-record (dataset 64uk-42ks).
RECORD_ADDRESS_COLUMN = "address"


def _default_pluto_record_fetch(
    canonical_bbl: str, correlation_id: str
) -> PlutoFetchResult:
    """Production record fetch: the accepted single-source-of-truth PLUTO
    connector, consumed read-only. Its own BBL validation is redundant here (the
    route validates first) but harmless; its typed errors and provenance are
    unchanged."""
    return fetch_by_bbl(canonical_bbl, correlation_id=correlation_id)


def get_pluto_record_fetch() -> PlutoRecordFetch:
    """Dependency returning the PLUTO record transport seam (override point for
    tests). Production uses the live SODA GET; tests inject recorded results via
    ``app.dependency_overrides`` so the suite runs offline."""
    return _default_pluto_record_fetch


def _record_address_from_result(result: PlutoFetchResult) -> str | None:
    """The verbatim PLUTO ``address`` original value, or None when the column is
    absent (SODA null-omission = honest key absence) or is not a usable string
    (drift never becomes a fabricated line)."""
    for fact in result.facts:
        if fact.get("original_field_name") == RECORD_ADDRESS_COLUMN:
            value = fact.get("original_value")
            if isinstance(value, str) and value.strip() != "":
                return value
            return None
    return None


def _record_source(result: PlutoFetchResult) -> dict:
    """Provenance of the transported record: the official source id, dataset id,
    per-record PLUTO release version, retrieval timestamp, and request URL."""
    return {
        "source_id": PLUTO_SOURCE_ID,
        "dataset_id": PLUTO_DATASET_ID,
        "dataset_version": result.dataset_version,
        "retrieved_at": result.retrieved_at,
        "request_url": result.request_url,
    }


@router.get("/properties/{bbl}/record-address", include_in_schema=False)
def get_record_address(
    bbl: str,
    fetch: PlutoRecordFetch = Depends(get_pluto_record_fetch),  # noqa: B008
) -> JSONResponse:
    """Transport the lot's PLUTO address-of-record for one BBL as a display-only
    city RECORD. Feature-flag gated OFF by default (reuses
    INTERNAL_RULE_EVAL_ENABLED), mirroring the lot-geometry endpoint's posture."""
    # Guard 1 (fail-safe production disable): absent/unknown flag -> 404 with no
    # hint the feature exists. Checked FIRST, before a correlation id is minted.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any connector call (typed 422; zero network I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "record_address_v1 validation_error code=%s correlation_id=%s",
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

    # 2. Fetch the PLUTO row read-only through the injected seam. A connector
    #    fault becomes a TYPED error (never a fake absence).
    try:
        result = fetch(normalized.canonical, correlation_id)
    except PlutoConnectorError as exc:
        payload = exc.to_payload()
        status_code = _PLUTO_ERROR_STATUS.get(
            payload["error_type"], _DEFAULT_PLUTO_ERROR_STATUS
        )
        logger.warning(
            "record_address_v1 connector_error state=%s correlation_id=%s",
            payload["error_type"], correlation_id,
        )
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
            "record_address_v1 unexpected_error stage=fetch correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 3. Build the typed record-address document. Every outcome is an honest 200;
    #    honest absence is a typed outcome with address=null, never a fabricated
    #    line.
    if result.status == "no_match":
        document = {
            "document_kind": "record_address",
            "bbl": normalized.canonical,
            "outcome": "no_record",
            "address": None,
            "reason": result.no_match_explanation
            or "The official PLUTO dataset returned no record for this lot.",
            "source": _record_source(result),
        }
    else:
        address = _record_address_from_result(result)
        if address is None:
            document = {
                "document_kind": "record_address",
                "bbl": normalized.canonical,
                "outcome": "no_address_of_record",
                "address": None,
                "reason": (
                    "The official PLUTO record for this lot carries no address "
                    "column (the field is absent); no address-of-record is asserted."
                ),
                "source": _record_source(result),
            }
        else:
            document = {
                "document_kind": "record_address",
                "bbl": normalized.canonical,
                "outcome": "address_of_record",
                "address": address,
                "reason": None,
                "source": _record_source(result),
            }

    # 4. Renderer-parity serialisation guard before send (same discipline as the
    #    lot-geometry endpoint): fail closed to a typed 500, never an untyped ASGI
    #    500, for any non-finite / unpaired-surrogate content.
    try:
        _assert_json_safe(document)
    except Exception:
        logger.error(
            "record_address_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
