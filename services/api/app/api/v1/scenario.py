"""GET /api/v1/properties/{bbl}/scenario - internal deterministic scenario
(task M5-T003).

SECURITY / DEPLOYMENT STATUS: INTERNAL/DEV ONLY, and additionally FEATURE-FLAG
GATED OFF BY DEFAULT - exactly like the rule-evaluation route this mirrors. Two
independent guards keep it off in production:

1. Like every route in this service it has NO authentication yet (M0-T007/T008
   blocked on the Supabase token); the service must not be publicly exposed.
2. It is reachable ONLY when ``INTERNAL_SCENARIO_ENABLED`` is an explicit true
   token (:func:`app.config.internal_scenario_enabled`). Absent / empty /
   unknown -> DISABLED (fail safe): the handler returns a generic ``404 Not
   Found`` byte-indistinguishable from an unmounted path, leaking NO hint the
   feature exists. The route is registered ``include_in_schema=False`` so it
   never appears in the OpenAPI document regardless of the flag.

What it does (deterministic route; NO independent legal calculation lives here):
rebuild the canonical property profile AND its rule_evaluation SERVER-SIDE over
the SAME trusted, injected seams the accepted rule-evaluation route uses
(``get_pluto_fetcher`` -> ``build_property_profile`` -> ``evaluate_property`` ->
``serialize_rule_evaluation``, with the server-side spatial substrate from
``get_spatial_substrate_provider``), then run the already-built deterministic
``build_scenario`` and return a versioned ``scenario`` @ 1.0.0 document. The
endpoint NEVER accepts a request body or a browser-supplied profile - only the
``bbl`` path parameter - so an untrusted caller can never inject the facts a
scenario would rest on. The only material number a scenario can surface is the
canonical ``max_residential_floor_area_sq_ft`` cap ALREADY present in the
rule_evaluation trace, surfaced VERBATIM by ``build_scenario``; nothing is
recomputed here.

A legitimate no-scenario / unsupported / professional-review outcome is a NORMAL
200 ``scenario`` document (``scenario_kind`` no_scenario / unsupported;
``coverage_status`` professional_review_required / data_conflict / unsupported /
not_applicable), never an error - so a consumer keeps the property usable. Only
genuine faults (malformed BBL, upstream fetch failure, internal contract defect,
unexpected exception) become typed API errors, mapped to the SAME HTTP semantics
as the property and rule-evaluation routes and carrying no traceback, path,
secret, or internal string.

The exact set of emitted (HTTP status, state) pairs is the single source of
truth ``STATUS_STATE_MATRIX`` below; it equals the rule-evaluation route's
documented matrix (the scenario contract defect reuses the shared
``internal_contract_error`` 500 pair, so it adds no new pair).
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.v1.properties import (
    _DEFAULT_ERROR_STATUS,
    _ERROR_STATUS,
    PlutoFetcher,
    get_pluto_fetcher,
)
from app.api.v1.rule_evaluation import (
    SpatialSubstrateProvider,
    get_spatial_substrate_provider,
)
from app.config import internal_scenario_enabled
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
from app.scenario import build_scenario
from app.scenario.contract import ScenarioContractError, validate_scenario_document

__all__ = ["STATUS_STATE_MATRIX", "router"]

logger = logging.getLogger("app.api.v1.scenario")

router = APIRouter(prefix="/api/v1", tags=["scenario"])

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every emission path below is
# enumerated here; it equals the rule-evaluation route's documented matrix
# (a fail-safe no-scenario result is a NORMAL 200 with no ``state`` field - the
# ``None`` sentinel records the exhaustive 200 path). The scenario-document
# contract defect maps to the shared ``internal_contract_error`` 500 pair, so it
# never introduces a status/state pair the mirrored route does not also emit.
# ---------------------------------------------------------------------------
STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # scenario document (validated before send)
        (422, "validation_error"),  # malformed BBL, no connector call
        (404, "no_match"),  # valid BBL, no PLUTO record (a result)
        (502, "schema_drift"),  # dataset contract breakage
        (503, "rate_limited"),  # SODA throttling after retry budget
        (503, "source_unavailable"),  # SODA outage after retry budget
        (504, "timeout"),  # SODA timeout after retry budget
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # a built payload failed its contract
    }
)


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


def _internal_contract_error_500(correlation_id: str) -> JSONResponse:
    """Documented typed 500 for a built payload (rebuilt profile, rebuilt
    rule_evaluation, or assembled scenario) that FAILED canonical-schema
    validation before send. A payload that does not honor its contract is an
    internal defect - an invalid 200 is impossible - never a raw 500 stack."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "an internal document failed canonical-contract validation and "
                "was not sent; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


@router.get("/properties/{bbl}/scenario", include_in_schema=False)
def get_scenario(
    bbl: str,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
) -> JSONResponse:
    """Rebuild the profile + rule_evaluation server-side, run the deterministic
    scenario builder, and return a scenario @ 1.0.0 document. Feature-flag gated
    OFF by default."""
    # Guard 1 (fail-safe production disable): absent/unknown flag -> 404 with no
    # hint the feature exists. Checked FIRST, before a correlation id is minted or
    # any input is touched.
    if not internal_scenario_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any connector call (typed 422; zero network I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "scenario_v1 validation_error code=%s correlation_id=%s",
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
    #    documented HTTP semantics as the property / rule-evaluation routes.
    try:
        result = fetcher(normalized.canonical, correlation_id)
    except PlutoConnectorError as exc:
        payload = exc.to_payload()
        logger.warning(
            "scenario_v1 connector_error state=%s correlation_id=%s",
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
            "scenario_v1 unexpected_error stage=fetch correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    # 3. Everything after the fetch runs inside one generic-500 guard so ANY
    #    unexpected exception honors the documented contract, never Starlette's
    #    plain-text 500 with full-traceback logging.
    try:
        # no_match is a RESULT, not an error: the property does not exist in the
        # official dataset, so there is nothing to build a scenario over. Same
        # 404 + machine state shape as the property / rule-evaluation routes.
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

        # Validate the rebuilt profile against its canonical schema before use.
        try:
            validate_profile(profile)
        except (UnsupportedContractVersionError, ContractValidationError):
            logger.error(
                "scenario_v1 profile_contract_error correlation_id=%s", correlation_id
            )
            return _internal_contract_error_500(correlation_id)

        # Rebuild the rule_evaluation document over the SAME deterministic path
        # the accepted rule-evaluation route uses (evaluate -> serialize ->
        # strict validate). A needs-review / unsupported / fail-safe evaluation
        # is a NORMAL rule_evaluation document here, never an error; the scenario
        # builder consumes it read-only.
        evaluation = evaluate_property(profile)
        rule_evaluation = serialize_rule_evaluation(
            evaluation,
            profile_contract_version=profile["profile_version"]["contract_version"],
        )
        try:
            validate_rule_evaluation_document(rule_evaluation)
        except RuleEvaluationContractError as exc:
            logger.error(
                "scenario_v1 rule_evaluation_contract_error location=%s correlation_id=%s",
                exc.location, correlation_id,
            )
            return _internal_contract_error_500(correlation_id)

        # Run the already-built deterministic scenario builder. It surfaces the
        # canonical cap VERBATIM from the trace (never recomputed) and fails
        # closed to a typed no_scenario outcome on any conflict / uncertainty /
        # malformed or absent controlling input - a NORMAL 200 document.
        scenario = build_scenario(profile, rule_evaluation)

        # Strict response validation before send: an invalid 200 is impossible;
        # the validator also fails closed on any 'verified' coverage_status.
        try:
            validate_scenario_document(scenario)
        except ScenarioContractError as exc:
            logger.error(
                "scenario_v1 scenario_contract_error location=%s correlation_id=%s",
                exc.location, correlation_id,
            )
            return _internal_contract_error_500(correlation_id)

        return _json(200, scenario, correlation_id)
    except Exception:
        logger.error(
            "scenario_v1 unexpected_error stage=build correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)
