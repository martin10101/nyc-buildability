"""POST /api/v1/properties/{bbl}/scenario/{sensitivity,ranking,comparison,threshold}
- internal, flag-gated scenario OPTIMIZATION-TOOLKIT endpoints (task M5-T012).

These four endpoints make the accepted, offline scenario optimization toolkit
(:func:`app.scenario.analyze_scenario_sensitivity` M5-T008,
:func:`app.scenario.rank_scenario_assumption_sets` M5-T007,
:func:`app.scenario.compare_scenario_assumption_sets` M5-T010,
:func:`app.scenario.find_scenario_threshold` M5-T011) REACHABLE by a client, under the
SAME security posture as the accepted M5-T003 ``GET /properties/{bbl}/scenario`` route.

SECURITY HEART - assumptions yes, FACTS never.
The accepted GET scenario route accepts NO body precisely so an untrusted caller can never
inject the facts a scenario rests on. These endpoints DO need caller input, but ONLY
illustrative ANALYSIS PARAMETERS: named assumption-sets, a variable name, an explicit ordered
candidate domain, a response-metric name, a numeric target, an objective. The scenario document
itself - and therefore the canonical ``draft_zoning_floor_area_cap_sq_ft`` cap, the
coverage/verification status and every other FACT - is ALWAYS rebuilt SERVER-SIDE from the
``bbl`` path parameter over the SAME trusted injected seams the accepted routes use
(``get_pluto_fetcher`` -> ``build_property_profile`` -> ``evaluate_property`` ->
``serialize_rule_evaluation`` -> ``build_scenario``, with ``get_spatial_substrate_provider``).
The request body is NEVER a source of facts: it is merged into the ENGINE arguments only, never
into the server-rebuilt document, and a body key that would supply or override a profile, a
rule_evaluation, a scenario document, a cap value, or a coverage/verification status is REJECTED
with a typed 422 AT ANY DEPTH (see :data:`FORBIDDEN_FACT_KEYS`) - not merely at the top level,
because the engines echo a caller's assumption dict VERBATIM into their result, so a fact-shaped
object nested inside an assumption-set would be reflected in a 200 body. The cap echoed in the
response is therefore the server-rebuilt canonical one, transported VERBATIM.

BOUNDED INPUT (fail-closed at the untrusted edge).
Every body dimension has an explicit documented cap - :data:`MAX_BODY_BYTES`,
:data:`MAX_NESTING_DEPTH`, :data:`MAX_STRING_LENGTH`, :data:`MAX_ASSUMPTION_SETS`,
:data:`MAX_CANDIDATE_DOMAIN_LENGTH`, :data:`MAX_ASSUMPTIONS_PER_SET`. Exceeding any cap is a
typed 422 with a reason. Oversized, deeply-nested (>= a few hundred levels), or otherwise
malformed bodies are a typed 422 - never an unhandled raise, a ``RecursionError``, a hang, or an
unbounded scan (the structural walk is ITERATIVE and every collection is length-checked before it
reaches an engine). This dogfoods the M5-T009/M5-T011 fail-closed lessons at the untrusted edge.
Body strings must also be ENCODABLE TEXT: a JSON escape can carry an unpaired surrogate
(``"\\ud800"`` - pure-ASCII request bytes, under every documented cap) which Starlette's
renderer cannot encode, so such a string is a typed 422 here rather than an unhandled
``UnicodeEncodeError`` at render time.

ROUTE POSTURE (mirrors M5-T003 exactly).
Registered ALWAYS but reachable ONLY when ``INTERNAL_SCENARIO_ENABLED`` is an explicit true
token (:func:`app.config.internal_scenario_enabled`, REUSED - no new flag); absent/empty/unknown
yields a generic 404 byte-indistinguishable from an unmounted path, leaking no hint the feature
exists. All four routes are ``include_in_schema=False`` so nothing appears in the OpenAPI document
regardless of the flag. Every non-disabled response carries ``X-Correlation-ID``; no error body
carries a traceback, filesystem path, secret, or internal implementation string. BOTH stages that
can raise - the trusted server-side rebuild AND the untrusted-input-driven engine call plus
envelope build - sit inside the same generic-500 guard, so no path can escape as Starlette's
plain-text 500 (which would carry no state, no correlation id, and a pair outside
:data:`STATUS_STATE_MATRIX`).

NO NEW LOGIC IN THE ROUTE.
It performs no independent legal calculation and no engine maths: it rebuilds the scenario,
validates and adapts the request into the engine function's documented arguments, calls the
engine READ-ONLY through the public :mod:`app.scenario` facade, and returns its typed result
verbatim inside a thin envelope. A legitimate no-scenario / unsupported / professional-review /
empty / invalid analysis outcome stays a NORMAL 200 typed result, never an error. Nothing is ever
marked Verified; the canonical :data:`app.scenario.NOT_VERIFIED_DISCLAIMER` is present on every
analysis response; every 200 body is proven serializable with the SAME encoder settings the
renderer uses (``json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")``) before
it is sent, so the pre-send check and the renderer can never disagree about what is encodable.

The exact set of emitted (HTTP status, state) pairs is the single source of truth
:data:`STATUS_STATE_MATRIX` below; it EQUALS the accepted scenario route's documented matrix and
introduces no pair beyond it (body-validation failures reuse the existing
``(422, "validation_error")`` pair).
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, Request
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
    NOT_VERIFIED_DISCLAIMER,
    ThresholdResponseMetric,
    analyze_scenario_sensitivity,
    build_scenario,
    compare_scenario_assumption_sets,
    find_scenario_threshold,
    rank_scenario_assumption_sets,
)
from app.scenario.contract import ScenarioContractError, validate_scenario_document

__all__ = [
    "FORBIDDEN_FACT_KEYS",
    "MAX_ASSUMPTIONS_PER_SET",
    "MAX_ASSUMPTION_SETS",
    "MAX_BODY_BYTES",
    "MAX_CANDIDATE_DOMAIN_LENGTH",
    "MAX_NESTING_DEPTH",
    "MAX_STRING_LENGTH",
    "STATUS_STATE_MATRIX",
    "router",
]

logger = logging.getLogger("app.api.v1.scenario_analysis")

router = APIRouter(prefix="/api/v1", tags=["scenario"])

# ---------------------------------------------------------------------------
# Documented untrusted-input caps. Exceeding any is a typed (422,
# "validation_error"); none is ever an unbounded scan or an unhandled raise.
# MAX_NESTING_DEPTH is deliberately far below the engine sanitizer's own 500
# ceiling (app.scenario._json_safety._MAX_JSON_SAFE_DEPTH) so a hostile body
# fails closed HERE, before any engine sees it.
# ---------------------------------------------------------------------------
MAX_BODY_BYTES = 65536  # 64 KiB raw request body
MAX_NESTING_DEPTH = 32  # container nesting levels in the parsed body
MAX_STRING_LENGTH = 4096  # any single JSON string value or key
MAX_ASSUMPTION_SETS = 50  # named assumption-sets (ranking / comparison)
MAX_CANDIDATE_DOMAIN_LENGTH = 256  # sensitivity `values` / threshold `domain`
MAX_ASSUMPTIONS_PER_SET = 64  # assumption dicts within a single assumption-set

# Body keys that would supply or OVERRIDE a server-rebuilt FACT. Their presence
# AT ANY DEPTH is a typed 422: a caller supplies assumptions, never facts. Facts can
# only enter a scenario through the trusted server rebuild - the engines merge the
# body into `assumptions` only, never into the scenario document, so the authoritative
# cap is not forgeable either way - but the engines DO echo a caller's assumption dict
# verbatim into their result, so a nested fact-shaped key would be reflected in a 200
# body and read as a fact. Rejecting at every depth keeps AS-2 (no fact override) and
# AS-6 (nothing marked Verified) honest, not merely unforgeable.
FORBIDDEN_FACT_KEYS: frozenset[str] = frozenset(
    {
        "profile",
        "property_profile",
        "rule_evaluation",
        "evaluation",
        "scenario",
        "scenario_document",
        "document",
        "draft_zoning_floor_area_cap_sq_ft",
        "max_residential_floor_area_sq_ft",
        "canonical_cap_sq_ft",
        "cap",
        "cap_value",
        "cap_label",
        "constraints",
        "coverage_matrix",
        "coverage",
        "coverage_status",
        "data_completeness",
        "verification",
        "verification_status",
        "verified",
        "needs_review",
        "professional_review_required",
    }
)

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every emission path below is a member;
# it EQUALS the accepted scenario route's documented matrix (app.api.v1.scenario)
# and introduces no new pair - body-validation failures reuse the existing
# (422, "validation_error") pair, and every rebuilt-document contract defect maps
# to the shared (500, "internal_contract_error") pair.
# ---------------------------------------------------------------------------
STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # analysis envelope (engine result; EMPTY/INVALID are 200 too)
        (422, "validation_error"),  # malformed BBL OR malformed/oversized/fact-injecting body
        (404, "no_match"),  # valid BBL, no PLUTO record (a result)
        (502, "schema_drift"),  # dataset contract breakage
        (503, "rate_limited"),  # SODA throttling after retry budget
        (503, "source_unavailable"),  # SODA outage after retry budget
        (504, "timeout"),  # SODA timeout after retry budget
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # a rebuilt payload failed its contract
    }
)


# ---------------------------------------------------------------------------
# Response helpers (identical shapes to the accepted scenario route).
# ---------------------------------------------------------------------------


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. Carries NO
    correlation id and NO body hint, so a disabled feature is indistinguishable from a
    route that does not exist (fail-safe production disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _validation_error(
    message: str, correlation_id: str, detail: dict | None = None
) -> JSONResponse:
    """Typed (422, "validation_error"): a malformed BBL or a body that violates the
    untrusted-input boundary (fact injection, a cap, or malformed JSON). Carries a reason,
    never a traceback / path / secret / internal string."""
    body: dict[str, Any] = {
        "state": "validation_error",
        "message": message,
        "correlation_id": correlation_id,
    }
    if detail is not None:
        body["detail"] = detail
    return _json(422, body, correlation_id)


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the correlation id only
    (no str(exc)/traceback: the chain may embed untrusted upstream strings)."""
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
    """Documented typed 500 for a rebuilt payload (profile, rule_evaluation, or scenario) that
    FAILED canonical-schema validation, or an envelope that is not strict-JSON-safe, before
    send. An invalid 200 is impossible - never a raw 500 stack."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "an internal document failed canonical-contract validation and was not sent; "
                "see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


# ---------------------------------------------------------------------------
# Untrusted-body validation (iterative, fail-closed).
# ---------------------------------------------------------------------------


def _fact_injection_error(injected: list[str], correlation_id: str) -> JSONResponse:
    """Typed (422, "validation_error") for a body that supplies or OVERRIDES a server-rebuilt
    FACT. Reuses the documented pair and names the offending keys in ``detail.rejected_keys``."""
    return _validation_error(
        "request body may carry only illustrative analysis parameters; it may not supply "
        "or override facts (a profile, rule_evaluation, scenario, cap value, or "
        "coverage/verification status)",
        correlation_id,
        detail={"rejected_keys": injected},
    )


def _string_boundary_error(value: str, label: str, correlation_id: str) -> JSONResponse | None:
    """Typed 422 when a body string (a value or a dict KEY) breaks a documented string
    boundary: longer than :data:`MAX_STRING_LENGTH`, or not ENCODABLE TEXT.

    Encodability is a real boundary, not a theoretical one. ``json.loads`` accepts the escape
    ``"\\ud800"`` - an UNPAIRED SURROGATE - from 21 pure-ASCII request bytes, under every
    documented cap. ``json.dumps`` with ``ensure_ascii=True`` happily re-escapes it, but
    Starlette's renderer uses ``ensure_ascii=False`` + ``.encode("utf-8")``, which RAISES
    ``UnicodeEncodeError``. Letting one through therefore produced a framework text/plain 500
    with no ``state``, no ``X-Correlation-ID`` and a (500, None) pair outside
    :data:`STATUS_STATE_MATRIX`. It is the caller's malformed input, so it is rejected here -
    before any engine, any echo, and any renderer."""
    if len(value) > MAX_STRING_LENGTH:
        return _validation_error(
            f"{label} exceeds the maximum length of {MAX_STRING_LENGTH}", correlation_id
        )
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return _validation_error(
            "request body contains a string that is not encodable text "
            "(an unpaired surrogate)",
            correlation_id,
        )
    return None


def _structural_error(body: dict, correlation_id: str) -> JSONResponse | None:
    """ITERATIVELY enforce :data:`MAX_NESTING_DEPTH`, :data:`MAX_STRING_LENGTH`, string
    ENCODABILITY and the :data:`FORBIDDEN_FACT_KEYS` boundary across the WHOLE parsed body -
    every value and every dict KEY, at EVERY depth. The body is already bounded by
    :data:`MAX_BODY_BYTES`, so this explicit-stack walk visits a bounded number of nodes and
    NEVER recurses (no ``RecursionError``) and never scans unboundedly. Returns a typed 422 on
    the first violation, else ``None``. JSON is a tree (``json.loads`` cannot produce a cycle),
    so no cycle guard is needed; the walk is finite regardless.

    The body object itself is the first node popped, so a top-level fact key is still reported
    before any nested or structural violation - the documented precedence is unchanged."""
    stack: list[tuple[Any, int]] = [(body, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > MAX_NESTING_DEPTH:
            return _validation_error(
                f"request body nesting exceeds the maximum of {MAX_NESTING_DEPTH} levels",
                correlation_id,
            )
        if isinstance(node, str):
            string_error = _string_boundary_error(node, "a string value", correlation_id)
            if string_error is not None:
                return string_error
        elif isinstance(node, dict):
            injected = sorted(FORBIDDEN_FACT_KEYS & {k for k in node if isinstance(k, str)})
            if injected:
                return _fact_injection_error(injected, correlation_id)
            for key, value in node.items():
                if isinstance(key, str):
                    string_error = _string_boundary_error(key, "a key", correlation_id)
                    if string_error is not None:
                        return string_error
                stack.append((value, depth + 1))
        elif isinstance(node, list):
            for item in node:
                stack.append((item, depth + 1))
    return None


async def _prepare_request(
    bbl: str, request: Request, correlation_id: str
) -> tuple[str, dict] | JSONResponse:
    """Validate the BBL and the untrusted request body BEFORE any I/O. Returns
    ``(canonical_bbl, body)`` on success, or a typed 422 ``JSONResponse`` on any boundary
    violation. Performs no network / connector call."""
    # 1. BBL (typed 422; zero I/O). raw_value is repr()-sanitized inside to_payload().
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()
        logger.info(
            "scenario_analysis_v1 validation_error code=%s correlation_id=%s",
            payload["code"],
            correlation_id,
        )
        return _validation_error(
            payload["message"],
            correlation_id,
            detail={"code": payload["code"], "raw_value": payload["raw_value"]},
        )

    # 2. Raw body size cap (before parsing anything).
    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        return _validation_error(
            f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes", correlation_id
        )

    # 3. Parse. An empty/whitespace body is the all-defaults request ({}). ANY parse failure
    #    (invalid JSON, or a body too deeply nested for the parser -> RecursionError) is the
    #    caller's fault -> a typed 422, never an unhandled raise.
    if not raw or not raw.strip():
        body: Any = {}
    else:
        try:
            body = json.loads(raw)
        except Exception:
            return _validation_error(
                "request body is not valid JSON (or is too deeply nested to parse)",
                correlation_id,
            )

    # 4. The body must be a JSON object of analysis parameters.
    if not isinstance(body, dict):
        return _validation_error(
            "request body must be a JSON object of illustrative analysis parameters",
            correlation_id,
        )

    # 5. One iterative walk enforces the WHOLE untrusted-body boundary at EVERY depth:
    #    fact-key injection, nesting depth, string length, and string encodability. A single
    #    walk (rather than a top-level key check plus a separate structural pass) is why a
    #    fact-shaped object nested inside an assumption-set cannot slip through.
    structural = _structural_error(body, correlation_id)
    if structural is not None:
        return structural

    return normalized.canonical, body


def _candidate_domain_cap_error(
    sequence: Any, label: str, correlation_id: str
) -> JSONResponse | None:
    """Typed 422 when an explicit candidate sequence (sensitivity ``values`` / threshold
    ``domain``) is a list longer than :data:`MAX_CANDIDATE_DOMAIN_LENGTH`. A non-list is left
    for the engine's own fail-closed handling (a NORMAL 200 invalid/empty outcome)."""
    if isinstance(sequence, list) and len(sequence) > MAX_CANDIDATE_DOMAIN_LENGTH:
        return _validation_error(
            f"'{label}' exceeds the maximum of {MAX_CANDIDATE_DOMAIN_LENGTH} candidate values",
            correlation_id,
        )
    return None


def _assumption_sets_cap_error(
    assumption_sets: Any, correlation_id: str
) -> JSONResponse | None:
    """Typed 422 when ``assumption_sets`` (ranking / comparison) is a list exceeding
    :data:`MAX_ASSUMPTION_SETS`, or any set holds more than :data:`MAX_ASSUMPTIONS_PER_SET`
    assumptions. A non-list container is left for the engine's own fail-closed handling."""
    if not isinstance(assumption_sets, list):
        return None
    if len(assumption_sets) > MAX_ASSUMPTION_SETS:
        return _validation_error(
            f"'assumption_sets' exceeds the maximum of {MAX_ASSUMPTION_SETS} named "
            "assumption-sets",
            correlation_id,
        )
    for entry in assumption_sets:
        assumptions = entry.get("assumptions") if isinstance(entry, dict) else entry
        if isinstance(assumptions, list) and len(assumptions) > MAX_ASSUMPTIONS_PER_SET:
            return _validation_error(
                f"an assumption-set exceeds the maximum of {MAX_ASSUMPTIONS_PER_SET} "
                "assumptions",
                correlation_id,
            )
    return None


# ---------------------------------------------------------------------------
# Server-side scenario rebuild (identical trusted seams to app.api.v1.scenario).
# ---------------------------------------------------------------------------


def _rebuild_scenario(
    canonical_bbl: str,
    fetcher: PlutoFetcher,
    substrate_provider: SpatialSubstrateProvider,
    correlation_id: str,
) -> tuple[dict | None, JSONResponse | None]:
    """Rebuild the canonical scenario document SERVER-SIDE over the SAME trusted injected seams
    the accepted scenario route uses. Returns ``(scenario_document, None)`` on success, or
    ``(None, error_response)`` mapped to the documented (status, state) pairs. The request body
    is NEVER consulted here: the scenario rests only on the ``bbl`` and the server-side seams."""
    try:
        result = fetcher(canonical_bbl, correlation_id)
    except PlutoConnectorError as exc:
        payload = exc.to_payload()
        logger.warning(
            "scenario_analysis_v1 connector_error state=%s correlation_id=%s",
            payload["error_type"],
            correlation_id,
        )
        status_code = _ERROR_STATUS.get(payload["error_type"], _DEFAULT_ERROR_STATUS)
        return None, _json(
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
            "scenario_analysis_v1 unexpected_error stage=fetch correlation_id=%s",
            correlation_id,
        )
        return None, _internal_error_500(correlation_id)

    try:
        # no_match is a RESULT, not an error: nothing exists to build a scenario over.
        if result.status == "no_match":
            return None, _json(
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

        substrate = substrate_provider(canonical_bbl, correlation_id)
        profile = build_property_profile(result, spatial_intersection=substrate)
        try:
            validate_profile(profile)
        except (UnsupportedContractVersionError, ContractValidationError):
            logger.error(
                "scenario_analysis_v1 profile_contract_error correlation_id=%s", correlation_id
            )
            return None, _internal_contract_error_500(correlation_id)

        evaluation = evaluate_property(profile)
        rule_evaluation = serialize_rule_evaluation(
            evaluation,
            profile_contract_version=profile["profile_version"]["contract_version"],
        )
        try:
            validate_rule_evaluation_document(rule_evaluation)
        except RuleEvaluationContractError as exc:
            logger.error(
                "scenario_analysis_v1 rule_evaluation_contract_error location=%s "
                "correlation_id=%s",
                exc.location,
                correlation_id,
            )
            return None, _internal_contract_error_500(correlation_id)

        scenario = build_scenario(profile, rule_evaluation)
        try:
            validate_scenario_document(scenario)
        except ScenarioContractError as exc:
            logger.error(
                "scenario_analysis_v1 scenario_contract_error location=%s correlation_id=%s",
                exc.location,
                correlation_id,
            )
            return None, _internal_contract_error_500(correlation_id)

        return scenario, None
    except Exception:
        logger.error(
            "scenario_analysis_v1 unexpected_error stage=build correlation_id=%s",
            correlation_id,
        )
        return None, _internal_error_500(correlation_id)


def _finish(
    analysis: str,
    canonical_bbl: str,
    scenario_document: dict,
    result: dict,
    correlation_id: str,
) -> JSONResponse:
    """Wrap the engine ``result`` VERBATIM in a thin envelope and return a 200. The canonical
    cap and coverage status are transported VERBATIM from the SERVER-rebuilt scenario document;
    the canonical not-verified disclaimer is always present and nothing is ever Verified.

    The envelope is proven serializable before send WITH THE SAME ENCODER SETTINGS THE RENDERER
    USES - ``json.dumps(..., ensure_ascii=False, allow_nan=False).encode("utf-8")``. Validating
    with ``ensure_ascii=True`` while Starlette renders with ``ensure_ascii=False`` made the two
    disagree: an unpaired surrogate passed validation and then raised ``UnicodeEncodeError``
    inside the renderer. ``UnicodeEncodeError`` subclasses ``ValueError``, so the existing
    handler maps it to the documented (500, "internal_contract_error") pair. A non-serializable
    body is an internal defect, never a partial 200 and never a framework text/plain 500."""
    envelope = {
        "analysis": analysis,
        "bbl": canonical_bbl,
        "scenario_cap_sq_ft": scenario_document.get("draft_zoning_floor_area_cap_sq_ft"),
        "cap_label": scenario_document.get("cap_label"),
        "scenario_kind": scenario_document.get("scenario_kind"),
        "coverage_status": scenario_document.get("coverage_status"),
        "not_verified_disclaimer": NOT_VERIFIED_DISCLAIMER,
        "result": result,
    }
    try:
        json.dumps(envelope, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError):
        logger.error(
            "scenario_analysis_v1 json_safety_error analysis=%s correlation_id=%s",
            analysis,
            correlation_id,
        )
        return _internal_contract_error_500(correlation_id)
    return _json(200, envelope, correlation_id)


def _guarded_analysis(
    analysis: str,
    canonical_bbl: str,
    scenario_document: dict,
    correlation_id: str,
    engine_call: Callable[[], Any],
) -> JSONResponse:
    """Call the engine and build the envelope inside the SAME generic-500 guard the trusted
    rebuild stage uses. Both halves are driven by UNTRUSTED input - the engine receives the
    caller's analysis parameters, and ``_finish`` serializes whatever the engine returned from
    them - so leaving this stage bare while guarding the trusted rebuild was the asymmetry
    backwards. An unexpected defect here now honors the documented (500, "internal_error") pair
    with an ``X-Correlation-ID`` instead of escaping as Starlette's plain-text 500 (no state, no
    correlation id, a pair outside :data:`STATUS_STATE_MATRIX`, full traceback logged). The
    engine is still called READ-ONLY through the public :mod:`app.scenario` facade; the callable
    only defers the call so it lands inside the guard."""
    try:
        result = engine_call()
        return _finish(analysis, canonical_bbl, scenario_document, result, correlation_id)
    except Exception:
        logger.error(
            "scenario_analysis_v1 unexpected_error stage=analysis analysis=%s correlation_id=%s",
            analysis,
            correlation_id,
        )
        return _internal_error_500(correlation_id)


# ---------------------------------------------------------------------------
# The four endpoints. Each: flag-gate -> mint correlation id -> validate BBL +
# untrusted body -> field caps -> rebuild scenario server-side -> call the engine
# READ-ONLY via the app.scenario facade inside the generic-500 guard -> return its
# typed result in a thin envelope. No independent legal calculation and no engine
# maths live here.
# ---------------------------------------------------------------------------


@router.post("/properties/{bbl}/scenario/sensitivity", include_in_schema=False)
async def post_sensitivity(
    bbl: str,
    request: Request,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
) -> JSONResponse:
    """Single-variable sensitivity / what-if over the server-rebuilt scenario (M5-T008)."""
    if not internal_scenario_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex

    prepared = await _prepare_request(bbl, request, correlation_id)
    if isinstance(prepared, JSONResponse):
        return prepared
    canonical_bbl, body = prepared

    cap_error = _candidate_domain_cap_error(body.get("values"), "values", correlation_id)
    if cap_error is not None:
        return cap_error

    scenario, error = _rebuild_scenario(
        canonical_bbl, fetcher, substrate_provider, correlation_id
    )
    if scenario is None:
        return error if error is not None else _internal_error_500(correlation_id)

    return _guarded_analysis(
        "sensitivity",
        canonical_bbl,
        scenario,
        correlation_id,
        lambda: analyze_scenario_sensitivity(
            scenario, body.get("variable"), body.get("values")
        ),
    )


@router.post("/properties/{bbl}/scenario/ranking", include_in_schema=False)
async def post_ranking(
    bbl: str,
    request: Request,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
) -> JSONResponse:
    """Ranking of explicit assumption-sets by a named objective (M5-T007)."""
    if not internal_scenario_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex

    prepared = await _prepare_request(bbl, request, correlation_id)
    if isinstance(prepared, JSONResponse):
        return prepared
    canonical_bbl, body = prepared

    cap_error = _assumption_sets_cap_error(body.get("assumption_sets"), correlation_id)
    if cap_error is not None:
        return cap_error

    scenario, error = _rebuild_scenario(
        canonical_bbl, fetcher, substrate_provider, correlation_id
    )
    if scenario is None:
        return error if error is not None else _internal_error_500(correlation_id)

    return _guarded_analysis(
        "ranking",
        canonical_bbl,
        scenario,
        correlation_id,
        lambda: rank_scenario_assumption_sets(
            scenario, body.get("objective"), body.get("assumption_sets")
        ),
    )


@router.post("/properties/{bbl}/scenario/comparison", include_in_schema=False)
async def post_comparison(
    bbl: str,
    request: Request,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
) -> JSONResponse:
    """Side-by-side comparison of two or more named assumption-sets (M5-T010)."""
    if not internal_scenario_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex

    prepared = await _prepare_request(bbl, request, correlation_id)
    if isinstance(prepared, JSONResponse):
        return prepared
    canonical_bbl, body = prepared

    cap_error = _assumption_sets_cap_error(body.get("assumption_sets"), correlation_id)
    if cap_error is not None:
        return cap_error

    scenario, error = _rebuild_scenario(
        canonical_bbl, fetcher, substrate_provider, correlation_id
    )
    if scenario is None:
        return error if error is not None else _internal_error_500(correlation_id)

    return _guarded_analysis(
        "comparison",
        canonical_bbl,
        scenario,
        correlation_id,
        lambda: compare_scenario_assumption_sets(scenario, body.get("assumption_sets")),
    )


@router.post("/properties/{bbl}/scenario/threshold", include_in_schema=False)
async def post_threshold(
    bbl: str,
    request: Request,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
) -> JSONResponse:
    """Break-even / threshold scan over an explicit candidate domain (M5-T011)."""
    if not internal_scenario_enabled():
        return _not_found()
    correlation_id = uuid.uuid4().hex

    prepared = await _prepare_request(bbl, request, correlation_id)
    if isinstance(prepared, JSONResponse):
        return prepared
    canonical_bbl, body = prepared

    cap_error = _candidate_domain_cap_error(body.get("domain"), "domain", correlation_id)
    if cap_error is not None:
        return cap_error

    scenario, error = _rebuild_scenario(
        canonical_bbl, fetcher, substrate_provider, correlation_id
    )
    if scenario is None:
        return error if error is not None else _internal_error_500(correlation_id)

    # Omitting response_metric defaults to the usable-range POINT (engine default); a present
    # but unknown/malformed metric is the engine's own typed invalid outcome (a NORMAL 200).
    response_metric = body.get("response_metric")
    if response_metric is None:
        response_metric = ThresholdResponseMetric.USABLE_RANGE_POINT

    return _guarded_analysis(
        "threshold",
        canonical_bbl,
        scenario,
        correlation_id,
        lambda: find_scenario_threshold(
            scenario,
            body.get("variable"),
            body.get("target"),
            body.get("domain"),
            response_metric=response_metric,
        ),
    )
