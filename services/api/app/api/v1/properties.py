"""GET /api/v1/properties/{bbl} - canonical property profile (task M1-T005).

SECURITY / DEPLOYMENT STATUS: INTERNAL/DEV ONLY. This endpoint has NO
authentication yet (M0-T007/T008 are blocked on the Supabase token); it must
not be exposed publicly until the auth/organization layer lands. Recorded as
a G5 condition in project-control/reports/M1-T005-producer-report.md.

Documented HTTP semantics (also in the OpenAPI ``responses`` metadata below):

==================  ======  ====================================================
Connector outcome   HTTP    Body ``state``
==================  ======  ====================================================
profile built       200     (canonical property-profile document; no ``state``)
malformed BBL       422     ``validation_error`` (typed; NO connector call made)
no_match            404     ``no_match`` (a result, not an error; includes the
                            condo billing-lot explanation where applicable)
rate_limited        503     ``rate_limited``
source_unavailable  503     ``source_unavailable``
timeout             504     ``timeout``
schema_drift        502     ``schema_drift`` (distinct state AND status so
                            dataset-contract breakage is never mistaken for a
                            transient outage)
unexpected error    500     ``internal_error`` (generic body; internals never
                            leave the process)
==================  ======  ====================================================

Every response carries an ``X-Correlation-ID`` header and (except 200) a
machine-readable ``state``. Responses never contain stack traces, exception
chains, header material, or the Socrata app token (M1-T002 G5 F5: only
``to_payload()`` output is logged/exposed, never formatted tracebacks).
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.pluto_soda import (
    DATASET_ID,
    SOURCE_ID,
    PlutoConnectorError,
    PlutoFetchResult,
    fetch_by_bbl,
)
from app.profile.builder import build_property_profile

__all__ = ["get_pluto_fetcher", "router"]

logger = logging.getLogger("app.api.v1.properties")

router = APIRouter(prefix="/api/v1", tags=["properties"])

# Connector error_type -> HTTP status (see module docstring table).
_ERROR_STATUS: dict[str, int] = {
    "rate_limited": 503,
    "source_unavailable": 503,
    "timeout": 504,
    "schema_drift": 502,
}
_DEFAULT_ERROR_STATUS = 503

# Fetcher contract: (canonical_bbl, correlation_id) -> PlutoFetchResult.
# Injected through FastAPI dependency_overrides so tests run offline on the
# fixture transport while production uses the live connector unchanged.
PlutoFetcher = Callable[[str, str], PlutoFetchResult]


def _default_fetcher(canonical_bbl: str, correlation_id: str) -> PlutoFetchResult:
    return fetch_by_bbl(canonical_bbl, correlation_id=correlation_id)


def get_pluto_fetcher() -> PlutoFetcher:
    """Dependency returning the PLUTO fetcher (override point for tests)."""
    return _default_fetcher


def _drift_monitor_hook(drift_signals: list[str], correlation_id: str) -> None:
    """Drift-monitor hook STUB (M1-T002 G3 carry-forward).

    Today: structured WARNING log so additive dataset drift observed on live
    traffic is visible in log-based alerting. The scheduled monitor that
    calls ``app.connectors.pluto_soda.check_columns_for_drift`` against the
    live /api/views metadata belongs to the M2 ingestion/connector-health
    tasks and will replace this hook; documented in the producer report.
    """
    if drift_signals:
        logger.warning(
            "pluto_drift_signals count=%d signals=%s correlation_id=%s",
            len(drift_signals), json.dumps(drift_signals), correlation_id,
        )


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _internal_error_500(exc: Exception, correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception (G3 D1 fix).

    Unexpected = internal defect. Log type + correlation id only (no
    str(exc)/traceback: the exception chain may embed untrusted upstream
    strings - M1-T002 G5 F5 payload-only logging policy).
    """
    logger.error(
        "properties_v1 unexpected_error type=%s correlation_id=%s",
        type(exc).__name__, correlation_id,
    )
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


_RESPONSES_DOC = {
    200: {
        "description": (
            "Canonical property profile (property_profile.schema.json v1 plus "
            "additive coverage_status/data_completeness/reproducibility keys). "
            "Facts are unreviewed official source facts: coverage_status is "
            "conditional/unsupported/data_conflict - never 'verified' (PRD "
            "section 12). Conflicts remain visible and unresolved."
        )
    },
    404: {
        "description": (
            "state=no_match: the BBL is syntactically valid but has no record "
            "in the current PLUTO release. A legitimate result, not an error; "
            "condo unit-lot BBLs include the billing-lot explanation."
        )
    },
    422: {
        "description": (
            "state=validation_error: malformed BBL path parameter (typed code: "
            "empty/non_numeric/negative/non_integer_decimal/wrong_length/"
            "invalid_borough/invalid_block/invalid_lot). No connector call is "
            "made. Accepted input forms: canonical 10-digit BBL or the Socrata "
            "decimal-serialized form (e.g. 1000010100.00000000); component "
            "form (borough/block/lot separately) is not accepted on this path."
        )
    },
    502: {
        "description": (
            "state=schema_drift: the official dataset no longer matches its "
            "recorded contract (distinct from transient unavailability; "
            "surfaced for alerting, never silently retried)."
        )
    },
    503: {
        "description": (
            "state=rate_limited or state=source_unavailable: upstream SODA "
            "throttling or outage after the bounded retry budget."
        )
    },
    504: {"description": "state=timeout: upstream SODA timeout after bounded retries."},
    500: {
        "description": (
            "state=internal_error: unexpected failure; generic body, internals "
            "are never exposed."
        )
    },
}


@router.get("/properties/{bbl}", responses=_RESPONSES_DOC)
def get_property(
    bbl: str,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
) -> JSONResponse:
    """Resolve one BBL to the canonical property profile (PRD sections 9, 12,
    21, 32.3). Deterministic route: validation -> connector -> builder; no
    legal logic lives here."""
    correlation_id = uuid.uuid4().hex

    # 1. Validate BEFORE any connector call (typed 422; zero network I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "properties_v1 validation_error code=%s correlation_id=%s",
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

    # 2. Fetch through the injected connector; map typed failures to the
    #    documented HTTP semantics. Never expose stack traces or internals.
    try:
        result = fetcher(normalized.canonical, correlation_id)
    except PlutoConnectorError as exc:
        payload = exc.to_payload()
        # G5 F5 consumer contract: log the structured payload (json.dumps
        # escapes control characters), NEVER a formatted traceback of
        # connector errors - the exception chain may carry untrusted
        # upstream strings.
        logger.warning(
            "properties_v1 connector_error state=%s correlation_id=%s payload=%s",
            payload["error_type"], correlation_id, json.dumps(payload),
        )
        status_code = _ERROR_STATUS.get(payload["error_type"], _DEFAULT_ERROR_STATUS)
        return _json(
            status_code,
            {
                "state": payload["error_type"],
                "message": payload["message"],
                "correlation_id": payload["correlation_id"],
                "source_id": payload["source_id"],
                "dataset_id": payload["dataset_id"],
                "detail": payload["detail"],
            },
            correlation_id,
        )
    except Exception as exc:
        return _internal_error_500(exc, correlation_id)

    # 3. Everything after the fetch (drift hook, no_match mapping, builder,
    #    200 construction) runs inside the same generic-500 guard so ANY
    #    unexpected exception honors the documented contract (G3 D1 fix) -
    #    never Starlette's plain-text 500 with full-traceback logging.
    try:
        _drift_monitor_hook(result.drift_signals, correlation_id)

        # no_match is a RESULT, not an error (M1-T002 G3 carry-forward):
        # documented choice = HTTP 404 with a machine-readable state, because
        # the resource does not exist in the official dataset. Distinguishable
        # from a routing 404 by the ``state`` field.
        if result.status == "no_match":
            return _json(
                404,
                {
                    "state": "no_match",
                    "bbl": result.bbl,
                    "message": result.no_match_explanation,
                    "correlation_id": result.correlation_id,
                    "source_id": SOURCE_ID,
                    "dataset_id": DATASET_ID,
                    "request_url": result.request_url,
                    "retrieved_at": result.retrieved_at,
                },
                correlation_id,
            )

        profile = build_property_profile(result)
        return _json(200, profile, correlation_id)
    except Exception as exc:
        return _internal_error_500(exc, correlation_id)
