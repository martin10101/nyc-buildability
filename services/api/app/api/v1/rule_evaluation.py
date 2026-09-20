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
from typing import TYPE_CHECKING

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
from app.spatial.live_provider import (
    CONDO_BASE_LOT_UNRESOLVED_CAUSE,
    LiveSubstrateResult,
    default_live_substrate,
    default_live_substrate_resolved,
)
from app.spatial.wide_street_live_provider import default_live_wide_street_determination

if TYPE_CHECKING:  # pragma: no cover - typing only; importing the wiring at
    # runtime would pull the shapely-heavy buffer engine onto the request path.
    # The provider is typed against the concrete determination; the runtime
    # default and every test override supply either a real WideStreetDetermination
    # or None, never an arbitrary object.
    from app.rules.wide_street_wiring import WideStreetDetermination

__all__ = [
    "get_resolved_spatial_substrate_provider",
    "get_spatial_substrate_provider",
    "get_wide_street_determination_provider",
    "router",
]

logger = logging.getLogger("app.api.v1.rule_evaluation")

router = APIRouter(prefix="/api/v1", tags=["rule-evaluation"])


# ---------------------------------------------------------------------------
# Server-side spatial-substrate provider (injection seam; NEVER browser-supplied).
#
# The evaluator needs the M2-T013 lot/zoning spatial-intersection substrate to
# derive a confident base-zoning district. That substrate is server-side data,
# not something a caller may supply. The trusted DEFAULT delegates to the
# settings-gated live provider (task M2-T020): with LIVE_SPATIAL_PROVIDER_ENABLED
# unset (its code default; nothing sets it in CI) it supplies None exactly as
# before - the evaluator fails safe (professional_review_required, spatial
# absent), an honest "no confident district" rather than a guessed one. With the
# explicit flag on, the live provider issues the accepted connector calls and
# hands their results to the M2-T013 engine; a SUCCESSFUL connector request is
# not by itself valid, sufficient spatial data, and composition can still yield
# None (empty official assignment, transfer-limited page, connector error) - a
# real substrate results only when the connectors succeed AND return sufficient
# data AND the engine composes a confident record. EVERY failure/partial input
# still yields None (app.spatial.live_provider fail-safe contract). Tests
# override this dependency with recorded substrate fixtures (mirroring
# get_pluto_fetcher).
# ---------------------------------------------------------------------------

# (canonical_bbl, correlation_id) -> the M2-T013 substrate (LotIntersectionRecord
# or its dict form) for that BBL, or None when no substrate is available.
SpatialSubstrateProvider = Callable[[str, str], object | None]


def _default_spatial_substrate(canonical_bbl: str, correlation_id: str) -> object | None:
    return default_live_substrate(canonical_bbl, correlation_id)


def get_spatial_substrate_provider() -> SpatialSubstrateProvider:
    """Dependency returning the server-side spatial-substrate provider (override
    point for tests). The default is the settings-gated live provider: flag off
    (the default) yields no substrate -> honest fail-safe.

    Retained UNCHANGED for the three other route consumers (evidence / scenario /
    scenario_analysis), which observe the exact ``object | None`` contract; this
    route uses :func:`get_resolved_spatial_substrate_provider` (M5-T058) instead."""
    return _default_spatial_substrate


# (canonical_bbl, correlation_id) -> a LiveSubstrateResult carrying the M2-T013
# substrate PLUS the condo resolution that produced it (M5-T058). Used ONLY by
# THIS route so the additive substrate_substitution stamp and the honest
# condo-unresolved refusal can be threaded into the evaluation document. The three
# OTHER route consumers keep the unchanged SpatialSubstrateProvider seam above -
# their observed contract is not widened. A single condo-resolver call per
# evaluation (no double SODA): this route calls ONLY the resolved provider.
ResolvedSpatialSubstrateProvider = Callable[[str, str], LiveSubstrateResult]


def _default_resolved_spatial_substrate(
    canonical_bbl: str, correlation_id: str
) -> LiveSubstrateResult:
    return default_live_substrate_resolved(canonical_bbl, correlation_id)


def get_resolved_spatial_substrate_provider() -> ResolvedSpatialSubstrateProvider:
    """Dependency returning the server-side RESOLVED spatial-substrate provider
    (override point for tests). The default is the settings-gated live provider:
    flag off (the default) yields an empty LiveSubstrateResult (absent substrate,
    no stamp, no condo cause) with zero connector calls -> honest fail-safe. The
    substrate is taken from ``.substrate`` exactly as before; the ``.substitution_
    stamp`` and ``.fail_safe_cause`` carry the M5-T058 additions."""
    return _default_resolved_spatial_substrate


# ---------------------------------------------------------------------------
# Server-side wide-street-determination provider (M5-T034 injection seam; NEVER
# browser-supplied). The ZR 23-22 R6/R7-1/R7-2/R8 conditional-FAR rows depend on
# whether the lot is within 100 ft of a WIDE street - a determination produced by
# the accepted wide-street stack (app.rules.wide_street_wiring.
# determine_wide_street_far) from server-side DCM street-width + geometry inputs,
# never from the request body. Mirrors get_spatial_substrate_provider exactly: the
# trusted DEFAULT supplies None because no wide-street data source is wired into
# the profile-build path yet (precisely as the spatial substrate defaulted to None
# before the M2-T020 live provider), so evaluate_property behaves byte-identically
# to before - the conservative conditional-FAR row governs and NO wide-street
# bonus is granted. A future provider (or a test override) supplies a real typed
# determination, which then drives server-side conditional-FAR row selection in
# evaluate_property: a professional-review determination escalates coverage to
# professional_review_required; a guessed 'wide' is never produced.
# ---------------------------------------------------------------------------

# (canonical_bbl, correlation_id) -> the typed
# app.rules.wide_street_wiring.WideStreetDetermination for that BBL, or None when
# no wide-street determination is available. The return type is the CONCRETE
# determination (forward-referenced so the shapely-heavy wiring stays off this
# module's own type surface), not a loose ``object`` - a provider can only ever
# supply a real typed determination or None.
WideStreetDeterminationProvider = Callable[[str, str], "WideStreetDetermination | None"]


def _default_wide_street_determination(
    canonical_bbl: str, correlation_id: str
) -> WideStreetDetermination | None:
    # Delegates to the settings-gated live provider (task M5-T035), exactly as
    # _default_spatial_substrate delegates to default_live_substrate. With
    # LIVE_WIDE_STREET_PROVIDER_ENABLED unset (its code default; nothing sets it
    # in CI) it returns None with zero connector calls, so evaluate_property
    # behaves byte-identically to before - the conservative conditional-FAR row
    # governs and NO wide-street bonus is granted. With the explicit flag on, the
    # live provider composes the accepted wide-street stack and returns its typed
    # determination (never a fabricated wide; see the provider's fail-safe
    # contract). EVERY failure/partial input still yields None.
    return default_live_wide_street_determination(canonical_bbl, correlation_id)


def get_wide_street_determination_provider() -> WideStreetDeterminationProvider:
    """Dependency returning the server-side wide-street-determination provider
    (override point for tests). The default is the settings-gated live provider:
    flag off (the default) yields None with zero connector calls -> the
    conditional-FAR rows return the conservative row and grant no wide-street
    bonus (honest fail-safe)."""
    return _default_wide_street_determination


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
    resolved_substrate_provider: ResolvedSpatialSubstrateProvider = Depends(  # noqa: B008
        get_resolved_spatial_substrate_provider
    ),
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
    wide_street_provider: WideStreetDeterminationProvider = Depends(  # noqa: B008
        get_wide_street_determination_provider
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
        # request. A None substrate is exactly the PLUTO-only build. M5-T058: the
        # resolved provider carries the condo resolution across the seam alongside
        # the substrate (a single condo-resolver call), so the substitution stamp
        # and the honest condo-unresolved refusal can be threaded below.
        substrate_result = resolved_substrate_provider(
            normalized.canonical, correlation_id
        )
        if substrate_result.evaluated:
            # The live resolved path ran (flag on): use its substrate AND the
            # condo carry - a single condo-resolver call. An absent substrate here
            # is a genuine live fail-safe, named honestly below.
            substrate = substrate_result.substrate
            substitution_stamp = substrate_result.substitution_stamp
            spatial_absent_condo_unresolved = (
                substrate_result.fail_safe_cause == CONDO_BASE_LOT_UNRESOLVED_CAUSE
            )
        else:
            # Flag-off no-op default: defer to the legacy object|None substrate
            # provider - the UNWIDENED seam the three other route consumers
            # (evidence / scenario / scenario_analysis) and their tests inject
            # through. No condo carry exists on this path.
            substrate = substrate_provider(normalized.canonical, correlation_id)
            substitution_stamp = None
            spatial_absent_condo_unresolved = False
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
        # 200 document here, never an error. The wide-street determination comes
        # from the injected server-side provider (default None - no data source
        # wired yet), never the request; when present it drives conditional-FAR
        # row selection server-side in evaluate_property.
        wide_street_determination = wide_street_provider(normalized.canonical, correlation_id)
        # M5-T058: thread the condo carry into the evaluator. The substitution
        # stamp (present only when a single resolved condo base lot was
        # substituted for the entered billing BBL) rides onto the result as the
        # additive substrate_substitution block; the honest condo-unresolved cause
        # renames an ABSENT-substrate refusal from the generic
        # spatial_intersection_absent to condo_base_lot_unresolved. Both are the
        # evaluator's pre-M5-T058 defaults on every non-condo path.
        evaluation = evaluate_property(
            profile,
            wide_street_determination=wide_street_determination,
            substrate_substitution=substitution_stamp,
            spatial_absent_condo_unresolved=spatial_absent_condo_unresolved,
        )
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
        logger.error(
            "rule_evaluation_v1 unexpected_error stage=evaluate correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)
