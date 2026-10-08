"""POST /api/v1/properties/{bbl}/results - the internal results route (task M5-T138, Part A of
docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md).

For one confirmed BBL it reads the lot's facts FROM THE SERVER (never the caller), runs the
already-accepted engine chain, and returns the emitted contract-1.3.0 three-way results document
verbatim. It returns NOTHING of the engine's inner 1.2.0 document.

THE CHAIN (R1 of the orchestrator's rulings). The route calls ONLY the entry that takes evidence,
``run_engine_and_result_ways_from_evidence``: it hands that entry the evaluator-inputs document,
the study document, the option's housing program, the server-held property profile, the prepared
tax-map outline and the site geometry, the user's optional statement about the special density
area, and the result's id and time; the entry derives the five lot conditions (overlay, special
purpose district, within 100 feet of the corner, the corner angle, the special density area) from
that SAME evidence. The route supplies NO condition of the lot itself and never derives one.

THE BODY (R3). The caller body carries only the user's OPTION: the housing program, an optional
floor-to-floor height, and an optional statement about the special density area. Any other field
is refused (``app.api.v1.results_request``). The route sources every lot fact and every lot
condition from the server evidence, never the body.

POSTURE (mirrors the accepted study-read route ``app.api.v1.study_read``):

- A NEW default-off flag ``INTERNAL_RESULTS_ENABLED`` (``app.config``). The route is ALWAYS
  registered but, when the flag is absent/empty/unknown, returns a generic ``404 Not Found``
  byte-indistinguishable from an unmounted path. ``include_in_schema=False`` so it never appears
  in OpenAPI. The flag gates REACHABILITY; the engine's own Lane A gate (``LANE_A_ENABLED``) stays
  separate and is also off in production, so production (neither flag set) keeps the route a 404
  and turns no zoning computation on.
- A per-caller rate limit (NB1) runs right after the flag check, BEFORE any other work, returning
  a typed ``429``. The BBL flows through ``normalize_bbl`` BEFORE any body read or provider call,
  so a malformed BBL is a typed ``422`` with zero I/O and the data source is never touched.
- The study inputs come through an INJECTED provider (``get_results_study_inputs_provider``) so the
  tests run fully offline on recorded fixtures; the default provider is the same live study-inputs
  provider the study-read route uses (flag-gated off in production).
- CONTRACT-GUARDED BEFORE SEND. The emitted document is validated with the existing results
  validator; a built document that fails is a ``500 internal_contract_error`` (an invalid 200 is
  impossible). ``RESULTS_READ_STATUS_STATE_MATRIX`` is the single source of truth for every emitted
  (HTTP status, state) pair.

ERRORS ARE TYPED AND PLAIN. No error reveals an internal path, a stack trace, an environment value
or another lot's data; the switch-off answer is byte-identical to an unknown path.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import internal_results_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.contracts.engine_disclosures import EngineDisclosureError
from app.contracts.evaluator_inputs import EvaluatorInputsError, build_evaluator_inputs
from app.contracts.study_contracts import StudyContractError, validate_results_document
from app.contracts.study_setup_bridge import StudySetupBridgeError, study_from_study_setup
from app.resilience.rate_limit import SlidingWindowRateLimiter, caller_key
from app.scenario.three_answers import BuildingDefaults
from app.scenario.three_answers.result_way_engine_bridge import (
    FLOOR_TO_FLOOR_KEY,
    HOUSING_PROGRAM_KEY,
    run_engine_and_result_ways_from_evidence,
)

from .results_request import ResultsRequestError, build_option, read_results_request
from .study_inputs import (
    StudyInputsProvider,
    StudyInputsUnavailableError,
    default_study_inputs_provider,
)
from .study_setup_document import build_study_setup_document

__all__ = [
    "MAX_BODY_BYTES",
    "RATE_LIMIT_MAX_KEYS",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "RESULTS_READ_STATUS_STATE_MATRIX",
    "get_rate_limiter",
    "get_results_study_inputs_provider",
    "router",
]

logger = logging.getLogger("app.api.v1.results_read")

router = APIRouter(prefix="/api/v1", tags=["results_read"])

#: Raw-body ceiling (defense in depth). The body is three small fields; anything larger is a typed
#: 422 before parsing, so an unbounded body cannot be buffered.
MAX_BODY_BYTES = 64 * 1024

# Per-caller sliding-window rate limit for THIS route (NB1): one unauthenticated POST on the LIVE
# default provider drives a live SODA call, so the route needs a bound BEFORE any other work. The
# SAME reviewed primitive the study-read route uses, keyed by caller_key. State is per-route and
# process-wide; tests reset/tighten it through get_rate_limiter(). Values mirror the study-read
# sibling (30 / 60 s).
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60.0
RATE_LIMIT_MAX_KEYS = 8192
_RATE_LIMITER = SlidingWindowRateLimiter(
    max_requests=RATE_LIMIT_MAX_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
    max_keys=RATE_LIMIT_MAX_KEYS,
)


def get_rate_limiter() -> SlidingWindowRateLimiter:
    """The shared, bounded per-caller limiter for this route. Tests reset/tighten it via this
    getter; it is NOT a client-controlled input."""
    return _RATE_LIMITER


# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every success is a 200 with NO ``state`` field (the
# document speaks for itself); the disabled sentinel is a 404 with NO state (byte-identical to an
# unmounted path). A malformed BBL or a refused body is a typed 422; a per-caller rate-limit
# refusal is a typed 429; inputs that cannot be produced are a bounded 503; a lot whose recorded
# conditions the evidence cannot confirm (the entry fails closed) is a bounded 503 with a plain
# reason, never a fabricated document; an unexpected defect is a generic 500; a built document that
# fails its contract before send is a typed 500 (an invalid 200 is impossible).
# ---------------------------------------------------------------------------
RESULTS_READ_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # the emitted contract-1.3.0 results document
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL OR a refused body field
        (429, "rate_limited"),  # per-caller rate limit exceeded (NB1)
        (503, "inputs_unavailable"),  # the provider could not produce the lot's inputs (fail safe)
        (503, "lot_conditions_unconfirmed"),  # the evidence cannot confirm a recorded condition
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # built document failed its contract
    }
)


def get_results_study_inputs_provider() -> StudyInputsProvider:
    """Dependency returning the study-inputs provider (test override point). The default is the
    SAME live study-inputs provider the study-read route uses (flag-gated off in production); tests
    inject a fixture-backed provider so the whole suite runs offline."""
    return default_study_inputs_provider


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. No correlation id and no
    body hint, so a disabled feature is indistinguishable from a route that does not exist."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _validation_error_422(
    correlation_id: str, *, code: str, message: str, field: str | None = None
) -> JSONResponse:
    detail: dict[str, object] = {"code": code}
    if field is not None:
        detail["field"] = field
    return _json(
        422,
        {
            "state": "validation_error",
            "message": message,
            "correlation_id": correlation_id,
            "detail": detail,
        },
        correlation_id,
    )


def _rate_limited_429(correlation_id: str) -> JSONResponse:
    return _json(
        429,
        {
            "state": "rate_limited",
            "message": "per-caller rate limit exceeded; retry later",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _inputs_unavailable_503(correlation_id: str) -> JSONResponse:
    return _json(
        503,
        {
            "state": "inputs_unavailable",
            "message": (
                "the results are not available for this property right now; nothing was "
                "fabricated and this is safe to retry"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _lot_conditions_unconfirmed_503(correlation_id: str) -> JSONResponse:
    """A recorded fact the engine chain needs to work out this lot's results could not be read:
    either the lot's city record (so a recorded condition such as a commercial overlay cannot be
    confirmed) or the lot outline (so the lot type cannot be worked out). The chain fails closed
    rather than guess. One plain reason true for BOTH causes; never a fabricated document and never
    a 500. The provider DID produce inputs here, so the same request would not succeed on a retry -
    the reason says what is missing, not "safe to retry"."""
    return _json(
        503,
        {
            "state": "lot_conditions_unconfirmed",
            "message": (
                "the results are not available for this property right now: a recorded "
                "fact needed to work out this lot's results - its city record or its lot "
                "outline - could not be read. Nothing was fabricated."
            ),
            "correlation_id": correlation_id,
        },
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


def _internal_contract_error_500(correlation_id: str) -> JSONResponse:
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the results failed their contract checks before send and were not delivered; "
                "see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _now_iso() -> str:
    """The result's time, minted at request time (UTC, RFC3339 'Z' form)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send: allow_nan=False rejects
    NaN/Infinity and the utf-8 form raises on an unpaired surrogate."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


@router.post("/properties/{bbl}/results", include_in_schema=False)
async def post_results(
    request: Request,
    bbl: str,
    provide_inputs: StudyInputsProvider = Depends(get_results_study_inputs_provider),  # noqa: B008
) -> JSONResponse:
    """Run the accepted engine chain for one BBL and return the emitted results document.
    Feature-flag gated OFF by default (INTERNAL_RESULTS_ENABLED), mirroring the sibling internal
    routes."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the feature exists.
    # Checked FIRST, before a correlation id is minted (byte-identical to an unmounted path).
    if not internal_results_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Guard 2 (NB1): per-caller rate limit BEFORE any other work.
    if not get_rate_limiter().allow(caller_key(request)):
        logger.info("results_v1 rate_limited correlation_id=%s", correlation_id)
        return _rate_limited_429(correlation_id)

    # Guard 3: validate the BBL BEFORE any body read or provider call (typed 422; zero I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()
        logger.info(
            "results_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _validation_error_422(
            correlation_id, code=payload["code"], message=payload["message"]
        )
    canonical = normalized.canonical

    # Guard 4: read and check the small caller body (typed 422; still zero data-source I/O).
    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        return _validation_error_422(
            correlation_id, code="body_too_large",
            message="the request body is larger than this route accepts",
        )
    try:
        body = json.loads(raw) if raw.strip() else None
    except Exception:
        return _validation_error_422(
            correlation_id, code="invalid_json",
            message="the request body is not valid JSON",
        )
    try:
        req = read_results_request(body)
    except ResultsRequestError as exc:
        logger.info(
            "results_v1 validation_error code=%s correlation_id=%s", exc.code, correlation_id
        )
        return _validation_error_422(
            correlation_id, code=exc.code, message=exc.message, field=exc.field
        )

    # 1. Produce the lot's inputs through the injected provider. A typed unavailability is a
    #    bounded 503 (fail safe, nothing fabricated); any other exception is a generic 500.
    try:
        inputs = provide_inputs(canonical, correlation_id)
    except StudyInputsUnavailableError as exc:
        logger.info(
            "results_v1 inputs_unavailable reason=%s correlation_id=%s",
            exc.reason, correlation_id,
        )
        return _inputs_unavailable_503(correlation_id)
    except Exception:
        logger.error("results_v1 unexpected_error stage=provide correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)

    # 2. Build the study-setup document (shared builder) and, from the checked body, ONE option;
    #    bridge to a study; build the evaluator inputs; run the entry that takes evidence; validate
    #    the emitted document. The route supplies NO lot condition - the entry derives all five from
    #    the evidence the provider produced.
    option_id = uuid.uuid4().hex
    computed_at = _now_iso()
    try:
        study_setup = build_study_setup_document(canonical, inputs)
        option = build_option(req, option_id=option_id)
        study = study_from_study_setup(
            study_setup,
            option,
            study_id=uuid.uuid4().hex,
            revision={"number": 1, "created_at": computed_at, "parent": None},
        )
        evaluator_inputs = build_evaluator_inputs(study, option_id)
    except EvaluatorInputsError as exc:
        # The lot's evidence cannot be turned into a runnable input set (no known value, an
        # ambiguous multi-frontage lot, or a visible conflict). Fail safe: a bounded 503, never a
        # fabricated document.
        logger.info("results_v1 lot_conditions_unconfirmed stage=evaluator_inputs "
                    "reason=%s correlation_id=%s", type(exc).__name__, correlation_id)
        return _lot_conditions_unconfirmed_503(correlation_id)
    except StudySetupBridgeError:
        logger.error("results_v1 unexpected_error stage=bridge correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
    except StudyContractError:
        logger.error("results_v1 contract_invalid stage=study correlation_id=%s", correlation_id)
        return _internal_contract_error_500(correlation_id)
    except Exception:
        logger.error("results_v1 unexpected_error stage=prepare correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)

    building_defaults = (
        BuildingDefaults(floor_to_floor_ft=req.floor_to_floor_ft)
        if req.floor_to_floor_ft is not None
        else BuildingDefaults()
    )
    # Which of the two design-choice scope lines the caller's request carried (M5-T139, DB-204 a):
    # the housing program ALWAYS (the body requires it); the floor-to-floor height only when the
    # body carried one (presence tested with `is not None`, never a truthiness test). The transform
    # says the user's choice on those rows; a choice the body did not carry stays the engine's.
    user_choices = {HOUSING_PROGRAM_KEY}
    if req.floor_to_floor_ft is not None:
        user_choices.add(FLOOR_TO_FLOOR_KEY)
    try:
        emitted = run_engine_and_result_ways_from_evidence(
            evaluator_inputs=evaluator_inputs,
            study=study,
            results_id=uuid.uuid4().hex,
            computed_at=computed_at,
            housing_program=req.housing_program,
            property_profile=inputs.property_profile,
            prepared_outline=inputs.prepared_outline,
            site_geometry=inputs.site_geometry,
            special_density_statement=req.special_density_statement,
            building_defaults=building_defaults,
            user_choices=frozenset(user_choices),
            env=None,
        )
    except EngineDisclosureError:
        # The entry fails closed when a recorded condition cannot be confirmed from the evidence
        # (for example, a recorded overlay with no property profile to confirm it). Fail safe.
        logger.info("results_v1 lot_conditions_unconfirmed stage=engine correlation_id=%s",
                    correlation_id)
        return _lot_conditions_unconfirmed_503(correlation_id)
    except EvaluatorInputsError:
        logger.info("results_v1 lot_conditions_unconfirmed stage=engine_inputs correlation_id=%s",
                    correlation_id)
        return _lot_conditions_unconfirmed_503(correlation_id)
    except Exception:
        logger.error("results_v1 unexpected_error stage=engine correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)

    # 3. Contract-guard the emitted document and guard its serialisation before send. The route
    #    returns ONLY emitted.document (the contract-1.3.0 three-way document), never the engine's
    #    inner 1.2.0 document.
    document = emitted.document
    try:
        validate_results_document(document)
        _assert_json_safe(document)
    except StudyContractError:
        logger.error("results_v1 contract_invalid stage=results correlation_id=%s", correlation_id)
        return _internal_contract_error_500(correlation_id)
    except Exception:
        logger.error("results_v1 serialization_unsafe correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
