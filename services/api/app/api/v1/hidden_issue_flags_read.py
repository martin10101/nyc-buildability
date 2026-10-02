"""GET /api/v1/properties/{bbl}/hidden-issue-flags - internal read of the §8a
hidden-issue flag layer for one confirmed BBL (lane C, packet W2; plan
``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 8a, queue item B-09).

Transports the four §8a flag groups wrapped in the W0
``packages/contracts/schemas/v1/hidden_issue_flags.schema.json`` envelope
(``{contract_version, groups}``). Each group is the serialized
``FlagGroup.to_dict()`` output of ``app.profile.hidden_issue_flags`` (the
accepted B-09 groups), carried VERBATIM:

- ``existing_building`` - five items (larger than today, non-conforming use,
  legal use/occupancy, rent regulation, harassment certification);
- ``zoning_lot_history`` - four reminder-only items (flag or "Check needed",
  never a verified or combined zoning-lot claim, plan P-2);
- ``map_based_rules`` - nine items from the recorded PLUTO map-based columns;
- ``site_shape_and_street`` - six items from the B-07 combined site geometry.

THIS LAYER CARRIES NO LEGAL MEANING AND COMPUTES NOTHING ABOUT THE LAW (platform
principle 1; lane prompt B). A flag only reports what the sourced data already
shows, or says the source is not available ("Check needed", never a guess). What
any rule requires is a determination for the engine (Lane A) and a qualified
reviewer at G6, never here. The zoning-math engine is off in these packets, so
the existing-building "larger than today" item carries no allowance and is never
decided; the zoning-lot-history group never claims a verified or combined zoning
lot.

Route posture mirrors the accepted sibling internal reads
(``app.api.v1.study_read`` / ``app.api.v1.study_inputs``, packet W1a):

- A NEW default-off flag ``INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED``
  (``app.config``). The route is ALWAYS registered but, when the flag is
  absent/empty/unknown, returns a generic ``404 Not Found``
  byte-indistinguishable from an unmounted path. ``include_in_schema=False`` so it
  never appears in OpenAPI. The flag gates REACHABILITY; the flag inputs are Lane
  B behaviour and are produced only when LANE_B_ENABLED is also on
  (``app.api.v1.hidden_issue_flags_inputs``), so production (neither flag set)
  keeps the route a 404. The router is DEFINED but NOT mounted here (packet W5
  mounts the W2-W4 routes self-gated in ``app.main``).
- No authentication yet (service internal/dev only). Because the default provider
  reaches LIVE PLUTO, a per-caller rate limit runs right after the flag check,
  BEFORE any validation or upstream work, returning a typed ``429`` so one
  unauthenticated GET cannot drive unbounded live SODA calls. The real per-caller
  isolation is the authenticated principal (B-001); this route family stays
  effectively dev-only (and unmounted) until auth lands.
- The BBL flows through ``normalize_bbl`` BEFORE any provider call, so a malformed
  BBL is a typed ``422`` with zero I/O.
- The inputs come through an INJECTED provider
  (``get_hidden_issue_flag_inputs_provider``) so the tests run fully offline on
  recorded fixtures (the 215-16 Northern pack). The DEFAULT provider binds the
  resilient PLUTO fetcher the properties route uses; live city data is reached
  ONLY through that existing connector behind the seam. Every upstream failure
  (and a no-match, including a condo unit-lot, or the Lane B gate off) maps to the
  typed ``503``; nothing is ever fabricated.
- CONTRACT-GUARDED BEFORE SEND. The built envelope is validated against
  ``hidden_issue_flags.schema.json`` before the 200 is returned; a built document
  that fails is a ``500 internal_contract_error`` (an invalid 200 is impossible,
  the properties-route posture). ``HIDDEN_ISSUE_FLAGS_STATUS_STATE_MATRIX`` is the
  single source of truth for every emitted (HTTP status, state) pair.
"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import internal_hidden_issue_flags_read_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.contracts.study_contracts import (
    StudyContractError,
    validate_hidden_issue_flags_document,
)
from app.profile.hidden_issue_flags import (
    existing_building_group,
    map_based_rules_group,
    site_shape_and_street_group,
    zoning_lot_history_group,
)
from app.resilience.rate_limit import SlidingWindowRateLimiter, caller_key

from .hidden_issue_flags_inputs import (
    HiddenIssueFlagInputs,
    HiddenIssueFlagInputsProvider,
    HiddenIssueFlagInputsUnavailableError,
    default_hidden_issue_flag_inputs_provider,
)

__all__ = [
    "CONTRACT_VERSION",
    "HIDDEN_ISSUE_FLAGS_STATUS_STATE_MATRIX",
    "RATE_LIMIT_MAX_KEYS",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "get_hidden_issue_flag_inputs_provider",
    "get_rate_limiter",
    "router",
]

logger = logging.getLogger("app.api.v1.hidden_issue_flags_read")

router = APIRouter(prefix="/api/v1", tags=["hidden_issue_flags_read"])

# The only published hidden_issue_flags contract version (W0 schema enum).
CONTRACT_VERSION = "1.0.0"

# Server-side length cap on every 422 ``message`` and the reflected raw_value
# repr (mirrors the study-read sibling). The repr is already repr()-sanitized in
# app.connectors.bbl; these only bound LENGTH so no 422 body grows unbounded.
MAX_RAW_VALUE_REPR_CHARS = 256
MAX_MESSAGE_CHARS = 256
_RAW_VALUE_TRUNCATION_MARKER = "...[truncated]"

# Per-caller sliding-window rate limit for THIS route: one unauthenticated GET on
# the LIVE default provider drives a live SODA call, so the route needs a bound
# BEFORE any upstream work. The SAME reviewed primitive the sibling routes use
# (app.resilience.rate_limit.SlidingWindowRateLimiter), keyed by caller_key
# (authenticated principal when present, else client host). State is per-route and
# process-wide; tests reset/tighten it through get_rate_limiter(). Values mirror
# the study-read sibling (30 / 60 s).
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60.0
RATE_LIMIT_MAX_KEYS = 8192
_RATE_LIMITER = SlidingWindowRateLimiter(
    max_requests=RATE_LIMIT_MAX_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
    max_keys=RATE_LIMIT_MAX_KEYS,
)


def get_rate_limiter() -> SlidingWindowRateLimiter:
    """The shared, bounded per-caller limiter for this route. Tests reset/tighten
    it via this getter; it is NOT a client-controlled input."""
    return _RATE_LIMITER


# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. A success is a 200 with NO ``state``
# field (the document speaks for itself); the disabled sentinel is a 404 with NO
# state (byte-identical to an unmounted path). A malformed BBL is a typed 422; a
# per-caller rate-limit refusal is a typed 429; inputs that cannot be produced
# (upstream unavailable/no-match, the Lane B gate off) are a bounded 503; an
# unexpected defect is a generic 500; a built document that fails its contract
# before send is a typed 500 (an invalid 200 is impossible).
# ---------------------------------------------------------------------------
HIDDEN_ISSUE_FLAGS_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # the §8a flag document
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL
        (429, "rate_limited"),  # per-caller rate limit exceeded
        (503, "inputs_unavailable"),  # inputs could not be produced (fail safe)
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # built document failed its contract
    }
)


def get_hidden_issue_flag_inputs_provider() -> HiddenIssueFlagInputsProvider:
    """Dependency returning the flag-inputs provider (test override point).

    The default is the LIVE PLUTO path through the resilient fetcher the
    properties route uses; tests inject a fixture-backed provider so the whole
    suite runs offline."""
    return default_hidden_issue_flag_inputs_provider


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. No
    correlation id and no body hint, so a disabled feature is indistinguishable
    from a route that does not exist (fail-safe disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _capped_raw_value(raw_value_repr: str) -> str:
    if len(raw_value_repr) <= MAX_RAW_VALUE_REPR_CHARS:
        return raw_value_repr
    return raw_value_repr[:MAX_RAW_VALUE_REPR_CHARS] + _RAW_VALUE_TRUNCATION_MARKER


def _capped_message(message: str) -> str:
    if len(message) <= MAX_MESSAGE_CHARS:
        return message
    return message[:MAX_MESSAGE_CHARS] + _RAW_VALUE_TRUNCATION_MARKER


def _validation_error_422(
    correlation_id: str, *, code: str, message: str, raw_value: str | None = None
) -> JSONResponse:
    """A typed ``(422, validation_error)`` with a bounded message. ``detail``
    always carries the bounded ``code``; ``raw_value`` is included (capped) only
    when the source error reflected one (a malformed BBL)."""
    detail: dict[str, object] = {"code": code}
    if raw_value is not None:
        detail["raw_value"] = _capped_raw_value(raw_value)
    return _json(
        422,
        {
            "state": "validation_error",
            "message": _capped_message(message),
            "correlation_id": correlation_id,
            "detail": detail,
        },
        correlation_id,
    )


def _rate_limited_429(correlation_id: str) -> JSONResponse:
    """A typed ``(429, rate_limited)`` consistent with the sibling routes: a
    server-minted correlation id, a bounded message, no caller text."""
    return _json(
        429,
        {
            "state": "rate_limited",
            "message": "per-caller rate limit exceeded; retry later",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the type +
    correlation id only (no str(exc)/traceback: the chain may embed untrusted
    upstream strings)."""
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
    """A built §8a flag document failed its contract before send. An invalid 200
    is impossible; the defect is internal, so the body is generic."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the hidden-issue flags failed their contract checks before send and "
                "were not delivered; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _inputs_unavailable_503(correlation_id: str) -> JSONResponse:
    """The flag inputs could not be produced (upstream unavailable, the Lane B gate
    off, or no PLUTO record). Fail safe: nothing is fabricated. The body carries a
    bounded platform message, never upstream text."""
    return _json(
        503,
        {
            "state": "inputs_unavailable",
            "message": (
                "the hidden-issue flags are not available for this property right now; "
                "nothing was fabricated and this is safe to retry"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send:
    ``allow_nan=False`` rejects NaN/Infinity, and the ``ensure_ascii=False`` utf-8
    form is what Starlette renders and raises on an unpaired surrogate."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


def _build_document(inputs: HiddenIssueFlagInputs) -> dict:
    """Shape the §8a flag document from the domain inputs. The four B-09 groups are
    carried VERBATIM (``FlagGroup.to_dict()``); nothing is computed here.

    The zoning-math engine is off in these packets, so the existing-building and
    zoning-lot-history groups take the group defaults: existing floor area is not
    wired (B-05), the as-of-right allowance is never supplied (Lane A off), and no
    recorded documents are fed in - so those groups stay "Check needed" and never
    claim a verified or combined zoning lot. Transit/parking is not passed (B-10
    open question (b) is not decided here), so the map-based group emits exactly
    its nine §8a items. The site geometry is the B-07 combined geometry (B-09 open
    question (a): lane C passes it)."""
    bbl = inputs.bbl
    groups = (
        existing_building_group(
            bbl,
            existing_floor_area=None,
            as_of_right_allowance=None,
            data_versions=None,
        ),
        zoning_lot_history_group(
            bbl,
            existing_floor_area=None,
            recorded_documents=(),
        ),
        map_based_rules_group(
            bbl,
            profile=inputs.profile,
            transit_parking=None,
        ),
        site_shape_and_street_group(
            bbl,
            site_geometry=inputs.site_geometry,
            profile=inputs.profile,
        ),
    )
    return {
        "contract_version": CONTRACT_VERSION,
        "groups": [group.to_dict() for group in groups],
    }


@router.get("/properties/{bbl}/hidden-issue-flags", include_in_schema=False)
def get_hidden_issue_flags(
    request: Request,
    bbl: str,
    provide_inputs: HiddenIssueFlagInputsProvider = Depends(  # noqa: B008
        get_hidden_issue_flag_inputs_provider
    ),
) -> JSONResponse:
    """Read the §8a hidden-issue flags for one BBL. Feature-flag gated OFF by
    default (INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED), mirroring the sibling
    internal reads; the flag inputs are additionally Lane B behaviour
    (LANE_B_ENABLED), withheld as a bounded 503 when that gate is off."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the
    # feature exists. Checked FIRST, before a correlation id is minted (the
    # flag-off 404 is byte-identical to an unmounted path).
    if not internal_hidden_issue_flags_read_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Guard 2: per-caller rate limit BEFORE any validation or upstream work, so one
    # unauthenticated GET that would drive a LIVE SODA call is bounded. Keyed by
    # caller_key (principal when present, else host). A typed 429, consistent with
    # the sibling routes.
    if not get_rate_limiter().allow(caller_key(request)):
        logger.info("hidden_issue_flags_v1 rate_limited correlation_id=%s", correlation_id)
        return _rate_limited_429(correlation_id)

    # 1. Validate the BBL BEFORE any provider call (typed 422; zero I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "hidden_issue_flags_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _validation_error_422(
            correlation_id,
            code=payload["code"],
            message=payload["message"],
            raw_value=payload["raw_value"],
        )

    canonical = normalized.canonical

    # 2. Produce the inputs through the injected provider. A typed unavailability
    #    (upstream outage/no-match, the Lane B gate off) is a bounded 503 (fail
    #    safe, nothing fabricated); any other exception is a generic 500.
    try:
        inputs = provide_inputs(canonical, correlation_id)
    except HiddenIssueFlagInputsUnavailableError as exc:
        logger.info(
            "hidden_issue_flags_v1 inputs_unavailable reason=%s correlation_id=%s",
            exc.reason, correlation_id,
        )
        return _inputs_unavailable_503(correlation_id)
    except Exception:
        logger.error(
            "hidden_issue_flags_v1 unexpected_error stage=provide correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 3. Shape the document, contract-guard it, and guard its serialisation before
    #    send. A built document that fails the contract is a typed 500 (never an
    #    invalid 200).
    try:
        document = _build_document(inputs)
        validate_hidden_issue_flags_document(document)
        _assert_json_safe(document)
    except StudyContractError:
        logger.error(
            "hidden_issue_flags_v1 contract_invalid correlation_id=%s", correlation_id
        )
        return _internal_contract_error_500(correlation_id)
    except Exception:
        logger.error(
            "hidden_issue_flags_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
