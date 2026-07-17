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
contract invalid    500     ``internal_contract_error`` (a built payload failed
                            canonical-schema validation before send - an
                            invalid 200 is impossible; task M2-T003)
version unpublished 500     ``unsupported_contract_version`` (a payload declared
                            a contract_version not in the closed published enum;
                            bounded, never coerced; task M2-T003)
==================  ======  ====================================================

The exact set of emitted (HTTP status, state) pairs is the single source of
truth ``STATUS_STATE_MATRIX`` below; a parametrized test enumerates every
emission path and fails on any undocumented pair (task M2-T003 scenario S3).

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
from functools import lru_cache

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.pluto_soda import (
    DATASET_ID,
    SOURCE_ID,
    PlutoConnectorError,
    PlutoFetchResult,
)
from app.profile.builder import build_property_profile
from app.profile.contract import (
    ContractValidationError,
    UnsupportedContractVersionError,
    validate_profile,
)

__all__ = ["STATUS_STATE_MATRIX", "get_pluto_fetcher", "router"]

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

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix (task M2-T003 item D, scenario S3).
#
# This is the SINGLE SOURCE OF TRUTH for the status/state pairs this endpoint
# may emit. Every emission path below is enumerated here; a parametrized test
# (tests/api/test_property_contract.py::test_s3_*) drives each path and FAILS
# on any (status, state) pair not present in this set, so a mismatched pair is
# impossible to ship undocumented.
#
# The 200 success path carries NO ``state`` field (state is the non-200
# discriminator - M1-T005 G3 review #5 / M1-T006 D5); it is recorded with the
# sentinel ``None`` so the enumeration is exhaustive.
# ---------------------------------------------------------------------------
STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # canonical profile (validated before send)
        (422, "validation_error"),  # malformed BBL, no connector call
        (404, "no_match"),  # valid BBL, no PLUTO record (a result)
        (502, "schema_drift"),  # dataset contract breakage
        (503, "rate_limited"),  # SODA throttling after retry budget
        (503, "source_unavailable"),  # SODA outage after retry budget
        (504, "timeout"),  # SODA timeout after retry budget
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # built payload failed contract
        (500, "unsupported_contract_version"),  # declared version unpublished
    }
)

# Fetcher contract: (canonical_bbl, correlation_id) -> PlutoFetchResult.
# Injected through FastAPI dependency_overrides so tests run offline on the
# fixture transport while production uses the live connector unchanged.
PlutoFetcher = Callable[[str, str], PlutoFetchResult]


@lru_cache(maxsize=1)
def _default_resilient_fetcher():
    """Process-wide resilient fetcher (task M1-T009): TTL cache, exact
    Retry-After honoring, jittered bounded backoff, per-source circuit
    breaker, and last-known-good serving with VISIBLE staleness wrap the
    accepted connector. Lazily built so importing this module never reads
    resilience env vars at import time; the same instance serves every
    request so cache/breaker/LKG state is process-wide. Typed failures keep
    the documented status/state matrix: circuit-open fast rejects surface as
    (503, source_unavailable) with detail.circuit == "open"."""
    from app.resilience.fetcher import build_default_resilient_fetcher

    return build_default_resilient_fetcher()


def _default_fetcher(canonical_bbl: str, correlation_id: str) -> PlutoFetchResult:
    return _default_resilient_fetcher()(canonical_bbl, correlation_id)


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


def _internal_contract_error_500(
    exc: ContractValidationError, correlation_id: str
) -> JSONResponse:
    """Typed 500 for a built payload that FAILED canonical-schema validation
    before send (task M2-T003 item A, scenario S2).

    A profile that does not honor the contract is an internal defect, never a
    valid 200. Distinct ``state`` (``internal_contract_error``) so this is not
    conflated with a generic 500. The validation ``reason`` is a fixed,
    non-secret classifier (schema_validation_failed / missing_profile_version
    / malformed_contract_version / declared_version_below_emitted_keys) - safe
    to surface; the detailed message stays in logs only."""
    logger.error(
        "properties_v1 internal_contract_error reason=%s correlation_id=%s",
        exc.reason, correlation_id,
    )
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the property profile failed canonical-contract validation and "
                "was not sent; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
            "detail": {"reason": exc.reason},
        },
        correlation_id,
    )


def _unsupported_contract_version_500(
    exc: UnsupportedContractVersionError, correlation_id: str
) -> JSONResponse:
    """BOUNDED typed error for a payload declaring an UNPUBLISHED
    ``contract_version`` (task M2-T003 item C, scenario S8).

    Never coerced to a nearby version and never a raw 500 stack: the declared
    version is echoed (it is the builder's own output, not untrusted upstream
    content) alongside the closed set of published versions."""
    from app.profile.contract import SUPPORTED_CONTRACT_VERSIONS

    logger.error(
        "properties_v1 unsupported_contract_version declared=%s correlation_id=%s",
        exc.declared_version, correlation_id,
    )
    return _json(
        500,
        {
            "state": "unsupported_contract_version",
            "message": (
                "the property profile declared an unpublished contract_version; "
                "it was rejected rather than coerced or served"
            ),
            "correlation_id": correlation_id,
            "detail": {
                "declared_version": exc.declared_version,
                "supported_versions": list(SUPPORTED_CONTRACT_VERSIONS),
            },
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
            "are never exposed. OR state=internal_contract_error: a built "
            "payload failed canonical-schema validation before send (task "
            "M2-T003; an invalid 200 is impossible). OR "
            "state=unsupported_contract_version: the payload declared a "
            "contract_version outside the closed published enum, rejected "
            "rather than coerced (bounded, typed)."
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

        # M2-T003 item A/B/C: validate EVERY 200 payload against the selected
        # canonical schema before send. An invalid 200 is impossible; typed
        # contract errors are distinguished from generic internal failures and
        # from the bounded unsupported-version case.
        try:
            validate_profile(profile)
        except UnsupportedContractVersionError as exc:
            return _unsupported_contract_version_500(exc, correlation_id)
        except ContractValidationError as exc:
            return _internal_contract_error_500(exc, correlation_id)

        return _json(200, profile, correlation_id)
    except Exception as exc:
        return _internal_error_500(exc, correlation_id)
