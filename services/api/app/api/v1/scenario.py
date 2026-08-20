"""GET /api/v1/properties/{bbl}/scenario - internal draft coverage-aware
scenario (task M5-T002).

SECURITY / DEPLOYMENT STATUS: INTERNAL/DEV ONLY, and additionally FEATURE-FLAG
GATED OFF BY DEFAULT - identical posture to the M4-T005 rule-evaluation route.
Two independent guards keep this off in production:

1. Like every route in this service it has NO authentication yet (M0-T007/T008
   blocked on the Supabase token); the service must not be publicly exposed.
2. It is reachable ONLY when ``INTERNAL_SCENARIO_ENABLED`` is an explicit true
   token (:func:`app.config.internal_scenario_enabled`). Absent / empty /
   unknown -> DISABLED (fail safe): the handler returns a generic ``404 Not
   Found`` that is byte-indistinguishable from an unmounted path and leaks NO
   hint that the feature exists. The route is registered with
   ``include_in_schema=False`` so it never appears in the OpenAPI document
   regardless of the flag.

What it does (deterministic route; legal logic lives in the rule engine and the
scenario builder, never here): rebuild the canonical property profile
SERVER-SIDE from the same trusted path the accepted ``GET /properties/{bbl}``
route uses (injected PLUTO fetcher -> ``build_property_profile`` ->
``validate_profile``), run the M4 rules evaluator over it, serialize the
versioned ``rule_evaluation`` @ 1.0.0 document, then consume that document
READ-ONLY through :func:`app.scenario.builder.build_scenario` with NO caller
assumptions and surface the resulting ``scenario`` @ 1.0.0 document. The endpoint
NEVER accepts a request body or a browser-supplied profile / rule evaluation /
assumption - only the ``bbl`` path parameter - so an untrusted caller can never
inject the facts a scenario rests on.

A legitimate no_scenario / unsupported / professional-review outcome from
``build_scenario`` is a NORMAL 200 scenario document, never an error - so a
consumer keeps the property profile usable independently. Only genuine faults
(malformed BBL, upstream fetch failure, internal defect) become typed API
errors, mapped to the SAME HTTP semantics as the property / rule-evaluation
routes and carrying no traceback, path, secret, or internal string.

The surfaced draft residential zoning-floor-area cap is the canonical
rule_evaluation trace value, consumed VERBATIM by the builder and never
recomputed or relabeled here.

FH-M5T001-S1 / FH-M5T001-S2 (M5-T001 future-hardening) are closed at this
boundary: the assembled scenario document is passed through a bounded-depth
guard AND ``validate_scenario_document`` before it is ever sent, so an
adversarially deep document fails closed with a typed error (never a
RecursionError) and an invalid document is impossible to emit.
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
from app.scenario import (
    ScenarioContractError,
    build_scenario,
    validate_scenario_document,
)

__all__ = ["router"]

logger = logging.getLogger("app.api.v1.scenario")

router = APIRouter(prefix="/api/v1", tags=["scenario"])

# ---------------------------------------------------------------------------
# Bounded-depth guard (closes FH-M5T001-S2). The scenario builder embeds
# provenance sub-objects (citation.provenance, rule_conflict.competing_rules,
# spatial_uncertainty.*) by reference from a rule_evaluation document. Those
# inputs are upstream schema-validated and bounded today, but the contract
# validation that follows (json.dumps / jsonschema recursion) would raise a
# RecursionError on an adversarially deep document. This iterative guard walks
# the assembled document with an explicit stack (never recursing itself) and
# fails closed BEFORE validation if any path exceeds the bound.
# ---------------------------------------------------------------------------

# Comfortably above the deepest legitimate scenario document (a citation's
# provenance nests only a handful of levels) yet far below Python's recursion
# ceiling, so a genuine document always passes and a hostile one always fails.
_MAX_SCENARIO_DEPTH = 64


def _document_depth_ok(document: object, limit: int = _MAX_SCENARIO_DEPTH) -> bool:
    """Return True iff no nested dict/list in ``document`` is deeper than
    ``limit``. Iterative (explicit stack) so the check itself can never raise a
    RecursionError, regardless of how deep the input is."""
    stack: list[tuple[object, int]] = [(document, 0)]
    while stack:
        node, depth = stack.pop()
        if depth > limit:
            return False
        if isinstance(node, dict):
            for value in node.values():
                stack.append((value, depth + 1))
        elif isinstance(node, list):
            for item in node:
                stack.append((item, depth + 1))
    return True


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


def _internal_contract_error_500(correlation_id: str, message: str) -> JSONResponse:
    """Typed 500 for an internal contract defect (a rebuilt profile, a
    rule_evaluation document, or the assembled scenario that fails canonical
    validation / the depth bound). A document that does not honor the contract is
    an internal defect, never a valid 200. No internals are surfaced."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": message,
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
    """Rebuild the profile server-side, evaluate the draft rule family, build the
    coverage-aware draft scenario, and return a scenario @ 1.0.0 document.
    Feature-flag gated OFF by default."""
    # Guard 1 (fail-safe production disable): absent/unknown flag -> 404 with no
    # hint the feature exists. Checked FIRST, before a correlation id is minted or
    # any input is touched.
    if not internal_scenario_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any connector call (typed 422; zero network I/O).
    #    Mirrors the accepted property / rule-evaluation routes exactly.
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
    #    documented HTTP semantics as the property route (single-sourced maps).
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
        # substrate comes from the injected server-side provider (REUSED from the
        # rule-evaluation route), never the request. A None substrate is exactly
        # the PLUTO-only build.
        substrate = substrate_provider(normalized.canonical, correlation_id)
        profile = build_property_profile(result, spatial_intersection=substrate)

        # Validate the rebuilt profile against its canonical schema before it is
        # used (an invalid input is an internal defect, typed 500, no internals).
        try:
            validate_profile(profile)
        except (UnsupportedContractVersionError, ContractValidationError):
            logger.error(
                "scenario_v1 profile_contract_error correlation_id=%s", correlation_id
            )
            return _internal_contract_error_500(
                correlation_id,
                "the rebuilt property profile failed canonical-contract validation "
                "and no scenario was built; see server logs by correlation id",
            )

        # Evaluate (deterministic; no temporal gating - the endpoint takes only
        # the bbl path param) and serialize by reference into the versioned
        # rule_evaluation contract, then strictly validate it before it feeds the
        # scenario builder.
        evaluation = evaluate_property(profile)
        rule_evaluation_document = serialize_rule_evaluation(
            evaluation,
            profile_contract_version=profile["profile_version"]["contract_version"],
        )
        try:
            validate_rule_evaluation_document(rule_evaluation_document)
        except RuleEvaluationContractError as exc:
            logger.error(
                "scenario_v1 rule_evaluation_contract_error location=%s correlation_id=%s",
                exc.location, correlation_id,
            )
            return _internal_contract_error_500(
                correlation_id,
                "the rule_evaluation document failed canonical-contract validation "
                "and no scenario was built; see server logs by correlation id",
            )

        # Build the deterministic scenario, consuming the rule_evaluation READ-ONLY
        # and with NO caller assumptions. A no_scenario / unsupported /
        # professional-review outcome is a NORMAL 200 document, never an error.
        document = build_scenario(
            profile, rule_evaluation_document, assumptions=None
        )

        # FH-M5T001-S2: bounded-depth guard BEFORE contract validation so an
        # adversarially deep provenance sub-object fails closed with a typed error
        # rather than a RecursionError inside json.dumps / jsonschema.
        if not _document_depth_ok(document):
            logger.error(
                "scenario_v1 depth_bound_exceeded correlation_id=%s", correlation_id
            )
            return _internal_contract_error_500(
                correlation_id,
                "the assembled scenario document exceeded the maximum allowed "
                "nesting depth and was not sent; see server logs by correlation id",
            )

        # FH-M5T001-S1: strict response validation before send: an invalid or
        # ever-Verified 200 is impossible.
        try:
            validate_scenario_document(document)
        except ScenarioContractError as exc:
            logger.error(
                "scenario_v1 scenario_contract_error location=%s correlation_id=%s",
                exc.location, correlation_id,
            )
            return _internal_contract_error_500(
                correlation_id,
                "the scenario document failed canonical-contract validation and was "
                "not sent; see server logs by correlation id",
            )

        return _json(200, document, correlation_id)
    except Exception:
        logger.error(
            "scenario_v1 unexpected_error stage=build correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)
