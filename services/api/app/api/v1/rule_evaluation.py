"""GET /api/v1/properties/{bbl}/rule-evaluation - internal rule-evaluation trace
(task M4-T005 phase 2).

SECURITY / DEPLOYMENT STATUS: INTERNAL/DEV ONLY, and additionally FEATURE-FLAG
GATED OFF BY DEFAULT. Two independent guards keep this off in production:

1. Like every route in this service it has NO authentication yet (M0-T007/T008
   blocked on the Supabase token); the service must not be publicly exposed.
2. It is reachable ONLY when ``INTERNAL_RULE_EVAL_ENABLED`` is an explicit true
   token (:func:`app.config.internal_rule_eval_enabled`). Absent / empty /
   unknown -> DISABLED (fail safe): the handler returns a generic ``404 Not
   Found`` that is byte-indistinguishable from an unmounted path and leaks NO
   hint that the feature exists. The route is registered with
   ``include_in_schema=False`` so it never appears in the OpenAPI document
   regardless of the flag.

What it does (deterministic route; legal logic lives in the rule engine, never
here): rebuild the canonical property profile SERVER-SIDE from the same trusted
path the accepted ``GET /properties/{bbl}`` route uses (injected PLUTO fetcher ->
``build_property_profile`` -> ``validate_profile``), run the M4 rules evaluator
over it, and return a versioned ``rule_evaluation`` @ 1.0.0 document. The endpoint
NEVER accepts a request body or a browser-supplied profile - only the ``bbl`` path
parameter - so an untrusted caller can never inject the facts a legal
determination would rest on.

A legitimate needs-review / unsupported / fail-safe outcome is a NORMAL 200
rule_evaluation document (coverage_status ``unsupported`` /
``professional_review_required`` / ``not_applicable``), never an error - so a
consumer keeps the property profile usable independently. Only genuine faults
(malformed BBL, upstream fetch failure, internal defect) become typed API errors,
mapped to the SAME HTTP semantics as the property route and carrying no
traceback, path, secret, or internal string.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.v1.properties import (
    _DEFAULT_ERROR_STATUS,
    _ERROR_STATUS,
    PlutoFetcher,
    get_pluto_fetcher,
)
from app.config import internal_rule_eval_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.pluto_soda import DATASET_ID, SOURCE_ID, PlutoConnectorError
from app.profile.builder import build_property_profile
from app.profile.contract import (
    ContractValidationError,
    UnsupportedContractVersionError,
    validate_profile,
)
from app.rules.integration import evaluate_property
from app.rules.response import (
    RuleEvaluationContractError,
    serialize_rule_evaluation,
    validate_rule_evaluation_document,
)

__all__ = ["get_spatial_substrate_provider", "router"]

logger = logging.getLogger("app.api.v1.rule_evaluation")

router = APIRouter(prefix="/api/v1", tags=["rule-evaluation"])


# ---------------------------------------------------------------------------
# Server-side spatial-substrate provider (injection seam; NEVER browser-supplied).
#
# The evaluator needs the M2-T013 lot/zoning spatial-intersection substrate to
# derive a confident base-zoning district. That substrate is server-side data,
# not something a caller may supply. Today no accepted spatial connector is wired
# into this internal endpoint, so the trusted DEFAULT supplies None: the
# evaluator then fails safe (professional_review_required, spatial absent) - an
# honest "no confident district" rather than a guessed one. A future accepted
# spatial connector plugs in HERE without touching the route, and tests override
# this dependency with recorded substrate fixtures (mirroring get_pluto_fetcher).
# ---------------------------------------------------------------------------

# (canonical_bbl, correlation_id) -> the M2-T013 substrate (LotIntersectionRecord
# or its dict form) for that BBL, or None when no substrate is available.
SpatialSubstrateProvider = Callable[[str, str], object | None]


def _default_spatial_substrate(canonical_bbl: str, correlation_id: str) -> object | None:
    return None


def get_spatial_substrate_provider() -> SpatialSubstrateProvider:
    """Dependency returning the server-side spatial-substrate provider (override
    point for tests). The default yields no substrate -> honest fail-safe."""
    return _default_spatial_substrate


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
    upstream strings - M1-T002 G5 F5 payload-only logging policy)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


@router.get("/properties/{bbl}/rule-evaluation", include_in_schema=False)
def get_rule_evaluation(
    bbl: str,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
) -> JSONResponse:
    """Rebuild the profile server-side, evaluate the draft rule family, and return
    a rule_evaluation @ 1.0.0 document. Feature-flag gated OFF by default."""
    # Guard 1 (fail-safe production disable): absent/unknown flag -> 404 with no
    # hint the feature exists. Checked FIRST, before a correlation id is minted or
    # any input is touched.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any connector call (typed 422; zero network I/O).
    #    Mirrors the accepted property route exactly.
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "rule_evaluation_v1 validation_error code=%s correlation_id=%s",
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

    # 2. Fetch through the injected connector; map typed failures to the SAME
    #    documented HTTP semantics as the property route (single-sourced maps).
    try:
        result = fetcher(normalized.canonical, correlation_id)
    except PlutoConnectorError as exc:
        payload = exc.to_payload()
        logger.warning(
            "rule_evaluation_v1 connector_error state=%s correlation_id=%s",
            payload["error_type"], correlation_id,
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
    except Exception:
        logger.error(
            "rule_evaluation_v1 unexpected_error stage=fetch correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    # 3. Everything after the fetch runs inside one generic-500 guard so ANY
    #    unexpected exception honors the documented contract, never Starlette's
    #    plain-text 500 with full-traceback logging.
    try:
        # no_match is a RESULT, not an error: the property does not exist in the
        # official dataset, so there is nothing to evaluate. Same 404 + machine
        # state shape as the property route (distinguishable from a routing 404).
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

        # Rebuild the profile from the TRUSTED server-side path. The spatial
        # substrate comes from the injected server-side provider, never the
        # request. A None substrate is exactly the PLUTO-only build.
        substrate = substrate_provider(normalized.canonical, correlation_id)
        profile = build_property_profile(result, spatial_intersection=substrate)

        # Validate the rebuilt profile against its canonical schema before it is
        # used, same as the property route (an invalid input is an internal
        # defect, mapped to a typed 500 with no internals).
        try:
            validate_profile(profile)
        except (UnsupportedContractVersionError, ContractValidationError):
            logger.error(
                "rule_evaluation_v1 profile_contract_error correlation_id=%s",
                correlation_id,
            )
            return _json(
                500,
                {
                    "state": "internal_contract_error",
                    "message": (
                        "the rebuilt property profile failed canonical-contract "
                        "validation and was not evaluated; see server logs by "
                        "correlation id"
                    ),
                    "correlation_id": correlation_id,
                },
                correlation_id,
            )

        # Evaluate (deterministic; no temporal gating - the endpoint takes only
        # the bbl path param) and serialize by reference into the versioned
        # contract. A needs-review / unsupported / fail-safe result is a NORMAL
        # 200 document here, never an error.
        evaluation = evaluate_property(profile)
        document = serialize_rule_evaluation(
            evaluation,
            profile_contract_version=profile["profile_version"]["contract_version"],
        )

        # Strict response validation before send: an invalid 200 is impossible.
        try:
            validate_rule_evaluation_document(document)
        except RuleEvaluationContractError as exc:
            logger.error(
                "rule_evaluation_v1 response_contract_error location=%s correlation_id=%s",
                exc.location, correlation_id,
            )
            return _json(
                500,
                {
                    "state": "internal_contract_error",
                    "message": (
                        "the rule_evaluation document failed canonical-contract "
                        "validation and was not sent; see server logs by "
                        "correlation id"
                    ),
                    "correlation_id": correlation_id,
                },
                correlation_id,
            )

        return _json(200, document, correlation_id)
    except Exception:
        logger.exception(
            "rule_evaluation_v1 unexpected_error stage=evaluate correlation_id=%s [TEMP-DEBUG M4-T005; revert before freeze]",
            correlation_id,
        )
        return _internal_error_500(correlation_id)
