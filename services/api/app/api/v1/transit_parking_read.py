"""GET /api/v1/properties/{bbl}/transit-parking - internal read of ONE lot's
transit/parking-ZONE status (lane C packet W3; plan check C-8, queue item B-10).

Transports the single transit/parking-zone status for one BBL, shaped to
``packages/contracts/schemas/v1/transit_parking.schema.json`` (version 1.0.0):
the serialized :func:`app.profile.transit_parking.resolve_transit_parking_status`
output (``TransitParkingStatus.to_dict()``) wrapped in the contract-version
envelope. ``resolve_transit_parking_status`` runs ONCE per BBL and the one status
is what every option reads (check C-8: the same source applied identically, so the
transit/parking status cannot differ between options).

CARRIES THE ZONE ONLY. The document carries PLUTO's ``transitzone``
classification VERBATIM (DCP's Transit Zones per the PLUTO Data Dictionary 26v1)
or says the source is "Check needed". It states NO parking OUTCOME: the number of
off-street spaces, a waiver, or an exemption is a Zoning-Resolution / legal
determination made by the rule engine (Lane A) and a qualified reviewer at G6,
never here (platform principle 1: deterministic code calculates, qualified humans
approve legal interpretations). There is deliberately no parking-outcome field,
and the contract has no slot for one.

Route posture mirrors the accepted sibling internal read
(``app.api.v1.study_read``):

- A NEW default-off flag ``INTERNAL_TRANSIT_PARKING_READ_ENABLED`` (``app.config``).
  The route is ALWAYS registered but, when the flag is absent/empty/unknown,
  returns a generic ``404 Not Found`` byte-indistinguishable from an unmounted
  path. ``include_in_schema=False`` so it never appears in OpenAPI. The flag gates
  REACHABILITY; the transit-zone data is Lane B behaviour and is produced only
  when ``LANE_B_ENABLED`` is also on (below), so production (neither flag set)
  keeps the route a generic 404.
- No authentication yet (service is internal/dev only). Because the default
  provider reaches LIVE PLUTO, a per-caller rate limit runs right after the flag
  check, BEFORE any validation or upstream work, returning a typed ``429`` so one
  unauthenticated GET cannot drive unbounded live SODA calls (security review NB1).
  The real per-caller isolation is the authenticated principal (B-001), which is
  why this route family stays effectively dev-only until auth lands (NB2).
- The BBL flows through ``normalize_bbl`` BEFORE any provider call, so a malformed
  BBL is a typed ``422`` with zero I/O.
- The status comes through an INJECTED provider (``get_transit_parking_provider``)
  so the tests run fully offline on recorded fixtures (the 215-16 Northern pack).
  The DEFAULT provider binds the resilient PLUTO fetcher the properties route uses
  (``app.api.v1.properties.get_pluto_fetcher``); live city data is reached ONLY
  through that existing connector behind the seam. Every upstream failure, a
  no-match (including a condo unit-lot), and the Lane B gate being off all map to
  the typed ``503`` (fail safe, nothing fabricated).

CONTRACT-GUARDED BEFORE SEND. The built document is validated against
``transit_parking.schema.json`` before the 200 is returned; a built document that
fails is a ``500 internal_contract_error`` (an invalid 200 is impossible, the
sibling-route posture). ``TRANSIT_PARKING_STATUS_STATE_MATRIX`` is the single
source of truth for every emitted (HTTP status, state) pair.

THE ROUTER IS DEFINED BUT NOT MOUNTED. Wiring it into the app
(``services/api/app/main.py``) is packet W5; this packet ships the router and its
tests only, so mounting stays one serial step with the sibling reads.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable, Mapping
from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import internal_transit_parking_read_enabled, lane_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.pluto_soda import (
    CONDO_UNIT_LOT_RANGE,
    PlutoConnectorError,
    PlutoFetchResult,
)
from app.contracts.study_contracts import (
    StudyContractError,
    validate_transit_parking_document,
)
from app.profile.builder import build_property_profile
from app.profile.transit_parking import (
    TransitParkingStatus,
    resolve_transit_parking_status,
)
from app.resilience.rate_limit import SlidingWindowRateLimiter, caller_key

__all__ = [
    "CONTRACT_VERSION",
    "RATE_LIMIT_MAX_KEYS",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "TRANSIT_PARKING_STATUS_STATE_MATRIX",
    "TransitParkingProvider",
    "TransitParkingUnavailableError",
    "assemble_transit_parking_status",
    "default_transit_parking_provider",
    "get_rate_limiter",
    "get_transit_parking_provider",
    "pluto_transit_parking_provider",
    "router",
]

logger = logging.getLogger("app.api.v1.transit_parking_read")

router = APIRouter(prefix="/api/v1", tags=["transit_parking_read"])

# The published transit_parking contract version this route emits. The envelope
# is resolve_transit_parking_status(...).to_dict() PLUS this field; the schema's
# contract_version enum admits exactly this value for v1.
CONTRACT_VERSION = "1.0.0"

# Defense-in-depth length cap for the reflected raw_value repr in a 422 detail
# (the sibling bounded-repr class). The repr is already repr()-sanitized in
# app.connectors.bbl; this only bounds its LENGTH.
MAX_RAW_VALUE_REPR_CHARS = 256
_RAW_VALUE_TRUNCATION_MARKER = "...[truncated]"

# Server-side length cap on every 422 ``message`` (security review NB3), matching
# the sibling route so no 422 body can grow unbounded with reflected text.
MAX_MESSAGE_CHARS = 256

# Per-caller sliding-window rate limit for THIS route (NB1): one unauthenticated
# GET on the LIVE default provider drives a live SODA call, so the route needs a
# bound BEFORE any upstream work. The SAME reviewed primitive the sibling reads
# use (app.resilience.rate_limit.SlidingWindowRateLimiter), keyed by caller_key
# (authenticated principal when present, else client host). State is per-route and
# process-wide; tests reset/tighten it through get_rate_limiter(). Values mirror
# the sibling (30 / 60 s).
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
# EXACT (HTTP status, state) pair matrix. Every success is a 200 with NO
# ``state`` field (the document speaks for itself); the disabled sentinel is a
# 404 with NO state (byte-identical to an unmounted path). A malformed BBL is a
# typed 422; a per-caller rate-limit refusal is a typed 429; a status that cannot
# be produced (upstream unavailable/no-match, the Lane B gate off) is a bounded
# 503; an unexpected defect is a generic 500; a built document that fails its
# contract before send is a typed 500 (an invalid 200 is impossible).
# ---------------------------------------------------------------------------
TRANSIT_PARKING_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # transit_parking document
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL
        (429, "rate_limited"),  # per-caller rate limit exceeded (NB1)
        (503, "inputs_unavailable"),  # status could not be produced (fail safe)
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # built document failed its contract
    }
)


# ---------------------------------------------------------------------------
# Provider seam: (canonical_bbl, correlation_id) -> TransitParkingStatus. Injected
# through FastAPI dependency_overrides so the route's tests run offline on recorded
# fixtures; the DEFAULT binds the live resilient fetcher.
# ---------------------------------------------------------------------------
TransitParkingProvider = Callable[[str, str], TransitParkingStatus]

# (canonical_bbl, correlation_id) -> PlutoFetchResult. The SAME fetcher seam the
# properties route injects.
PlutoFetcher = Callable[[str, str], PlutoFetchResult]


class TransitParkingUnavailableError(Exception):
    """The transit/parking status could not be produced (upstream unavailable, a
    no-match, or the Lane B gate off). The route maps this to a bounded
    ``503 inputs_unavailable`` - never a fabricated status. ``reason`` is a bounded
    platform token for observability, never upstream text."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


def _no_record_reason(bbl: str) -> str:
    """A bounded platform token distinguishing a CONDO unit-lot no-match (resolve
    the condominium BILLING BBL and retry) from a GENERIC no-match, using the
    connector's OWN published condo lot-number range. A lot-NUMBER classification
    (PLUTO carries one record per complex under the billing lot), NOT geometry.
    Used only to label the fail-safe 503 for observability; the HTTP status is
    unchanged."""
    try:
        lot = normalize_bbl(bbl).lot
    except BBLValidationError:
        return "no_match"
    low, high = CONDO_UNIT_LOT_RANGE
    return "condo" if low <= lot <= high else "no_match"


def assemble_transit_parking_status(
    pluto_result: PlutoFetchResult,
    *,
    clock: Callable[[], datetime] | None = None,
    env: Mapping[str, str] | None = None,
) -> TransitParkingStatus:
    """Resolve the ONE transit/parking status from a successful PLUTO fetch result.

    Pure: no I/O. ``env`` supplies the ``LANE_B_ENABLED`` gate (defaults to the
    process environment). A no-match withholds the status; the Lane B gate being
    off withholds it (fail safe) - never a fabricated value.

    Raises:
        TransitParkingUnavailableError: the fetch is not a usable single-lot
            record, or the Lane B gate is off.
    """
    if pluto_result.status != "ok":
        # A no-match is a legitimate result (the BBL is valid but PLUTO holds no
        # record). A condo UNIT-lot and a plain no-match map to DISTINCT reasons so
        # the fail-safe 503 is observable; both withhold the status.
        raise TransitParkingUnavailableError(
            f"PLUTO returned {pluto_result.status!r} for {pluto_result.bbl}; no "
            "transit/parking status is produced (a record is required).",
            reason=_no_record_reason(pluto_result.bbl),
        )
    # The transit-zone status is Lane B behaviour (app.config enablement note), so
    # it is produced only when LANE_B_ENABLED is on; off -> withheld, not computed.
    if not lane_enabled("B", env):
        raise TransitParkingUnavailableError(
            "the transit/parking data gate (LANE_B_ENABLED) is off, so the status is "
            "withheld rather than fabricated.",
            reason="lane_b_disabled",
        )
    builder_kwargs = {} if clock is None else {"clock": clock}
    profile = build_property_profile(pluto_result, **builder_kwargs)
    # ONE resolution per BBL (check C-8): every option reads this one status.
    return resolve_transit_parking_status(profile)


def pluto_transit_parking_provider(
    fetcher: PlutoFetcher,
    *,
    clock: Callable[[], datetime] | None = None,
    env: Mapping[str, str] | None = None,
) -> TransitParkingProvider:
    """A :data:`TransitParkingProvider` over a PLUTO ``fetcher``.

    Fetches the PLUTO record, then resolves the one status. A typed PLUTO
    connector failure or a no-record result becomes
    :class:`TransitParkingUnavailableError` (the route's bounded 503), never a
    partial or fabricated status.
    """

    def provider(canonical_bbl: str, correlation_id: str) -> TransitParkingStatus:
        try:
            result = fetcher(canonical_bbl, correlation_id)
        except PlutoConnectorError as exc:
            raise TransitParkingUnavailableError(
                "the official PLUTO source could not be reached; the transit/parking "
                "status is withheld and is safe to retry.",
                reason=exc.error_type,
            ) from exc
        return assemble_transit_parking_status(result, clock=clock, env=env)

    return provider


@lru_cache(maxsize=1)
def _live_transit_parking_provider() -> TransitParkingProvider:
    """The live provider, bound to the SAME resilient PLUTO fetcher the properties
    route uses (``app.api.v1.properties.get_pluto_fetcher`` ->
    ``app.resilience.fetcher.build_default_resilient_fetcher``): a TTL cache,
    bounded retries with jittered backoff, a per-source circuit breaker and
    last-known-good serving wrap the accepted connector (NB1). Built once, LAZILY,
    so importing this module reads no resilience env and makes no network call; the
    import is local to avoid import-time coupling to the properties route."""
    from app.api.v1.properties import get_pluto_fetcher

    return pluto_transit_parking_provider(get_pluto_fetcher())


def default_transit_parking_provider(
    canonical_bbl: str, correlation_id: str
) -> TransitParkingStatus:
    """Route default: the LIVE PLUTO path through the resilient fetcher the
    properties route uses.

    Every upstream failure maps to the route's typed 503; a no-match (including a
    condo unit-lot) and the Lane B gate being off withhold the status rather than
    fabricating one. Tests override the dependency so the suite runs fully offline;
    this live default is never exercised on the network in tests. The route flag is
    off in production regardless, and production stays blocked on B-001 auth plus
    the route-local rate limit (NB1/NB2) before any unauthenticated live-fetch
    surface is reachable."""
    return _live_transit_parking_provider()(canonical_bbl, correlation_id)


def get_transit_parking_provider() -> TransitParkingProvider:
    """Dependency returning the transit/parking provider (test override point).

    The default is the LIVE PLUTO path through the resilient fetcher the properties
    route uses (NB1); tests inject a fixture-backed provider so the whole suite runs
    offline."""
    return default_transit_parking_provider


# ---------------------------------------------------------------------------
# Response helpers (mirror the sibling study_read route exactly).
# ---------------------------------------------------------------------------
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
    """Length-cap a 422 ``message`` server-side (security review NB3)."""
    if len(message) <= MAX_MESSAGE_CHARS:
        return message
    return message[:MAX_MESSAGE_CHARS] + _RAW_VALUE_TRUNCATION_MARKER


def _validation_error_422(
    correlation_id: str, *, code: str, message: str, raw_value: str | None = None
) -> JSONResponse:
    """A typed ``(422, validation_error)`` with a bounded message (NB3)."""
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
    """A typed ``(429, rate_limited)`` consistent with the sibling route: a
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
    """A built transit/parking document failed its contract before send. An invalid
    200 is impossible; the defect is internal, so the body is generic."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the transit/parking status failed its contract checks before send and "
                "was not delivered; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _inputs_unavailable_503(correlation_id: str) -> JSONResponse:
    """The transit/parking status could not be produced (upstream unavailable, a
    no-match, or the Lane B gate off). Fail safe: nothing is fabricated. The
    ``reason`` is a bounded platform token, never upstream text."""
    return _json(
        503,
        {
            "state": "inputs_unavailable",
            "message": (
                "the transit/parking status is not available for this property right "
                "now; nothing was fabricated and this is safe to retry"
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


def _build_document(status: TransitParkingStatus) -> dict:
    """Shape the transit/parking document: the serialized status wrapped in the
    contract-version envelope. ``resolve_transit_parking_status`` already decided
    the zone / check-needed; nothing is computed here, and no parking-outcome field
    is ever added (the contract forbids one)."""
    return {"contract_version": CONTRACT_VERSION, **status.to_dict()}


@router.get("/properties/{bbl}/transit-parking", include_in_schema=False)
def get_transit_parking(
    request: Request,
    bbl: str,
    provide_status: TransitParkingProvider = Depends(get_transit_parking_provider),  # noqa: B008
) -> JSONResponse:
    """Read the ONE transit/parking-zone status for one BBL. Feature-flag gated OFF
    by default (INTERNAL_TRANSIT_PARKING_READ_ENABLED), mirroring the sibling
    internal read. The zone only - never spaces, a waiver or an exemption (Lane A /
    G6)."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the
    # feature exists. Checked FIRST, before a correlation id is minted (the
    # flag-off 404 is byte-identical to an unmounted path).
    if not internal_transit_parking_read_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Guard 2 (NB1): per-caller rate limit BEFORE any validation or upstream work,
    # so one unauthenticated GET that would drive a LIVE SODA call is bounded. A
    # typed 429, consistent with the sibling route.
    if not get_rate_limiter().allow(caller_key(request)):
        logger.info("transit_parking_v1 rate_limited correlation_id=%s", correlation_id)
        return _rate_limited_429(correlation_id)

    # 1. Validate the BBL BEFORE any provider call (typed 422; zero I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "transit_parking_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _validation_error_422(
            correlation_id,
            code=payload["code"],
            message=payload["message"],
            raw_value=payload["raw_value"],
        )

    canonical = normalized.canonical

    # 2. Produce the ONE status through the injected provider. A typed
    #    unavailability (upstream, no-match, Lane B gate off) is a bounded 503
    #    (fail safe, nothing fabricated); any other exception is a generic 500.
    try:
        status = provide_status(canonical, correlation_id)
    except TransitParkingUnavailableError as exc:
        logger.info(
            "transit_parking_v1 inputs_unavailable reason=%s correlation_id=%s",
            exc.reason, correlation_id,
        )
        return _inputs_unavailable_503(correlation_id)
    except Exception:
        logger.error(
            "transit_parking_v1 unexpected_error stage=provide correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 3. Shape the document, contract-guard it, and guard its serialisation before
    #    send. A built document that fails the contract is a typed 500.
    try:
        document = _build_document(status)
        validate_transit_parking_document(document)
        _assert_json_safe(document)
    except StudyContractError:
        logger.error(
            "transit_parking_v1 contract_invalid correlation_id=%s", correlation_id
        )
        return _internal_contract_error_500(correlation_id)
    except Exception:
        logger.error(
            "transit_parking_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
