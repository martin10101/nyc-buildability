"""GET /api/v1/properties/{bbl}/parity - internal read of a property's PARITY
DATA (lane C packet W4; plan section 11b, queue item B-11).

Transports the parity DATA one confirmed BBL carries, shaped to
``packages/contracts/schemas/v1/parity_data.schema.json``:

- ``comparable_sales`` - the disclosed selection of recorded DOF sales "of
  similar type and size" (``app.profile.parity.comparable_sales``), serialized by
  a LOCAL serializer because :class:`ComparableSalesResult` has no ``to_dict``. It
  is DATA, never a valuation: NO average, NO price-per-square-foot and NO estimate
  is computed, and a disclosure line (``not_a_valuation``) states so.
- ``unused_floor_area`` - the unused-floor-area line for the subject lot
  (``app.profile.parity.unused_floor_area``). It ALWAYS reads "Not confirmed" with
  the owner-settled wording (D-090-R038): NO remaining-capacity number, allowance
  or FAR appears. The existing-floor-area INPUT is read UNKNOWN for now (value
  null); the sourced B-05 input is wired in a later slice. The allowance and the
  subtraction are the rule engine's (Lane A), which is off.

NOT a valuation and NOT a tax-incentive analysis. 485-x (and any other tax
exemption/incentive) is OUT of scope here: this layer presents only recorded
sales and the "Not confirmed" unused-floor-area line; it computes no 485-x
eligibility, benefit or valuation.

Route posture mirrors the sibling internal read ``app.api.v1.study_read``
(itself mirroring ``condo_records`` / ``rule_evaluation``):

- A default-off flag ``INTERNAL_PARITY_READ_ENABLED`` (``app.config``) gates
  REACHABILITY. The route is ALWAYS registered but, when the flag is
  absent/empty/unknown, returns a generic ``404 Not Found`` byte-indistinguishable
  from an unmounted path. ``include_in_schema=False`` so it never appears in
  OpenAPI. The comparable-sales data is Lane B behaviour, produced only when
  ``LANE_B_ENABLED`` is ALSO on, so production (neither flag set) keeps the route
  a 404.
- No authentication yet (service is internal/dev only). Because a served request
  drives TWO live DOF SODA calls (the subject's own sales, then the comparable
  candidates), a per-caller rate limit (NB1) runs right after the flag check,
  BEFORE any validation or upstream work, returning a typed ``429`` so one
  unauthenticated GET cannot drive unbounded live SODA calls. The real per-caller
  isolation is the authenticated principal (B-001), which keeps this route family
  effectively dev-only (and UNMOUNTED) until auth lands.
- The BBL flows through ``normalize_bbl`` BEFORE any provider call, so a malformed
  BBL is a typed ``422`` with zero I/O.
- With ``LANE_B_ENABLED`` off the parity data is WITHHELD as a bounded ``503``
  (fail safe, nothing fabricated) and NO live DOF call is made - only Lane B may
  reach live city APIs. The live DOF transport is INJECTED
  (``get_dof_transport``) so the tests run fully offline on recorded fixtures (the
  215-16 Northern / Bayside pack). Every upstream connector failure (and a subject
  with no usable recorded sale) maps to the typed ``503``; nothing is fabricated.

ZONING MATH STAYS OFF (plan / lane rule). This route carries NO allowance,
capacity, FAR or rule output.

CONTRACT-GUARDED BEFORE SEND. The built document is validated against
``parity_data.schema.json`` before the 200 is returned; a built document that
fails is a ``500 internal_contract_error`` (an invalid 200 is impossible).
``PARITY_READ_STATUS_STATE_MATRIX`` is the single source of truth for every
emitted (HTTP status, state) pair.
"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import internal_parity_read_enabled, lane_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.dof_sales_soda import (
    DofSalesConnectorError,
    SaleRecord,
    fetch_comparable_candidates,
    fetch_sales_by_bbl,
)
from app.contracts.study_contracts import StudyContractError, validate_parity_data_document
from app.profile.existing_floor_area import resolve_existing_zoning_floor_area
from app.profile.parity.comparable_sales import (
    ComparableSalesResult,
    select_comparables,
    subject_spec_from_record,
)
from app.profile.parity.unused_floor_area import unused_floor_area_data
from app.resilience.rate_limit import SlidingWindowRateLimiter, caller_key
from app.resilience.transport import Transport, urllib_transport

__all__ = [
    "CANDIDATE_ROW_LIMIT",
    "LANE_B",
    "PARITY_READ_STATUS_STATE_MATRIX",
    "RATE_LIMIT_MAX_KEYS",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "SUBJECT_SALES_ROW_LIMIT",
    "get_dof_transport",
    "get_rate_limiter",
    "router",
]

logger = logging.getLogger("app.api.v1.parity_read")

router = APIRouter(prefix="/api/v1", tags=["parity_read"])

# The Lane B flag this route also requires (its data is Lane B behaviour).
LANE_B = "B"

# Row caps for the two live SODA calls (the connector's own documented defaults,
# surfaced here so the injected test transport can build the exact request urls).
SUBJECT_SALES_ROW_LIMIT = 50
CANDIDATE_ROW_LIMIT = 200

# Server-side length cap on every 422 ``message`` (sibling security review NB3).
MAX_MESSAGE_CHARS = 256
MAX_RAW_VALUE_REPR_CHARS = 256
_RAW_VALUE_TRUNCATION_MARKER = "...[truncated]"

# Per-caller sliding-window rate limit for THIS route (NB1): one unauthenticated
# GET drives TWO live SODA calls, so the route needs a bound BEFORE any upstream
# work. The SAME reviewed primitive the sibling routes use, keyed by caller_key
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


def get_dof_transport() -> Transport:
    """Dependency returning the DOF SODA HTTP transport (test override point).

    The default is the live ``urllib_transport`` the accepted connector ships;
    tests inject a routed fixture transport so the whole suite runs offline. The
    route reaches live city data ONLY through the connector's existing bounded
    retry engine behind this seam, and only when LANE_B_ENABLED is on."""
    return urllib_transport


CONTRACT_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. A success is a 200 with NO ``state``
# field (the document speaks for itself); the disabled sentinel is a 404 with NO
# state (byte-identical to an unmounted path). A malformed BBL is a typed 422; a
# per-caller rate-limit refusal is a typed 429; parity data that cannot be
# produced (Lane B gate off, an upstream failure, or a subject with no usable
# recorded sale) is a bounded 503; an unexpected defect is a generic 500; a built
# document that fails its contract before send is a typed 500 (invalid 200 is
# impossible).
# ---------------------------------------------------------------------------
PARITY_READ_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # parity-data document
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL
        (429, "rate_limited"),  # per-caller rate limit exceeded (NB1)
        (503, "inputs_unavailable"),  # parity data could not be produced (fail safe)
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # built document failed its contract
    }
)


class _ParityUnavailable(Exception):
    """The parity data could not be produced (the Lane B gate is off, an upstream
    DOF failure, or the subject carries no usable recorded sale). The route maps
    this to a bounded ``503 inputs_unavailable`` - never a fabricated document.
    ``reason`` is a bounded platform token, never upstream text."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


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
    """A built parity document failed its contract before send. An invalid 200 is
    impossible; the defect is internal, so the body is generic."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the parity data failed its contract checks before send and was not "
                "delivered; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _inputs_unavailable_503(correlation_id: str) -> JSONResponse:
    """The parity data could not be produced (Lane B gate off, upstream DOF
    unavailable, or no usable subject sale). Fail safe: nothing is fabricated."""
    return _json(
        503,
        {
            "state": "inputs_unavailable",
            "message": (
                "the parity data is not available for this property right now; nothing "
                "was fabricated and this is safe to retry"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _serialize_comparable_sale(record: SaleRecord) -> dict:
    """One :class:`SaleRecord` -> the contract ``comparable_sale`` object. Every
    value is the publisher's own field, carried verbatim; the DOF ``source`` (the
    7-key SaleRecord.source the contract's ``dof_source`` models) is carried AS IS,
    never re-shaped into the connector's wider 9-key DofSalesResult.provenance."""
    return {
        "bbl": record.bbl,
        "borough": record.borough,
        "neighborhood": record.neighborhood,
        "block": record.block,
        "lot": record.lot,
        "address": record.address,
        "zip_code": record.zip_code,
        "building_class_category": record.building_class_category,
        "building_class_at_time_of_sale": record.building_class_at_time_of_sale,
        "residential_units": record.residential_units,
        "commercial_units": record.commercial_units,
        "total_units": record.total_units,
        "year_built": record.year_built,
        "land_square_feet": record.land_square_feet,
        "gross_square_feet": record.gross_square_feet,
        "sale_price": record.sale_price,
        "sale_date": record.sale_date,
        "source": record.source,
    }


def _serialize_comparable_sales(result: ComparableSalesResult) -> dict:
    """Serialize a :class:`ComparableSalesResult` to the contract ``comparable_sales``
    object (the module has no ``to_dict``). NO average, price-per-square-foot or
    estimate is added - only the publisher's recorded rows, the disclosed filter in
    plain words, and the verbatim not-a-valuation line. ``excluded`` entries are
    already the contract ``{bbl, address, sale_date, reason}`` shape; ``source`` is
    the shared 7-key DOF row source (or null)."""
    return {
        "subject": {
            "bbl": result.subject.bbl,
            "building_class_category": result.subject.building_class_category,
            "gross_square_feet": result.subject.gross_square_feet,
        },
        "criteria": {
            "size_tolerance_fraction": result.criteria.size_tolerance_fraction,
            "exclude_zero_price": result.criteria.exclude_zero_price,
            "require_recorded_size": result.criteria.require_recorded_size,
        },
        "criteria_text": result.criteria_text,
        "not_a_valuation": result.not_a_valuation,
        "selected": [_serialize_comparable_sale(record) for record in result.selected],
        "excluded": [dict(entry) for entry in result.excluded],
        "source": result.source,
    }


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send:
    ``allow_nan=False`` rejects NaN/Infinity, and the ``ensure_ascii=False`` utf-8
    form is what Starlette renders and raises on an unpaired surrogate."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


def _build_parity_document(canonical_bbl: str, transport: Transport, correlation_id: str) -> dict:
    """Produce the parity-data document for ``canonical_bbl``. Makes the TWO live
    DOF SODA calls through the injected ``transport`` (the subject's own sales,
    then the comparable candidates), runs the disclosed selection, and carries the
    UNKNOWN existing-floor-area input (B-05 wiring is a later slice). Nothing is
    computed: no average, no valuation, no capacity. Raises :class:`_ParityUnavailable`
    for any fail-safe 503 case."""
    # 1. The subject's OWN recorded DOF sales -> its recorded type and size.
    try:
        subject_result = fetch_sales_by_bbl(
            canonical_bbl,
            transport=transport,
            row_limit=SUBJECT_SALES_ROW_LIMIT,
            correlation_id=correlation_id,
        )
    except DofSalesConnectorError as exc:
        raise _ParityUnavailable(exc.error_type) from exc
    if not subject_result.records:
        raise _ParityUnavailable("no_subject_sale")
    subject = subject_result.records[0]
    if subject.neighborhood is None or subject.building_class_category is None:
        # Without a recorded neighborhood + building class the disclosed
        # "similar type" query has no honest inputs; withhold rather than guess.
        raise _ParityUnavailable("no_subject_query_inputs")

    # 2. The comparable candidates sharing the subject's DOF neighborhood +
    #    building-class category (the disclosed "similar type" query).
    try:
        candidate_result = fetch_comparable_candidates(
            subject.neighborhood,
            subject.building_class_category,
            transport=transport,
            row_limit=CANDIDATE_ROW_LIMIT,
            correlation_id=correlation_id,
        )
    except DofSalesConnectorError as exc:
        raise _ParityUnavailable(exc.error_type) from exc

    # 3. The disclosed selection. No source kwarg: the result carries the 7-key
    #    row source the contract models, never the wider connector provenance.
    comparables = select_comparables(
        subject_spec_from_record(subject), candidate_result.records
    )

    # 4. The unused-floor-area line. The existing-floor-area INPUT is UNKNOWN for
    #    now (no B-05 evidence supplied), so the result reads value null; the line
    #    is ALWAYS "Not confirmed" and carries NO capacity number.
    existing = resolve_existing_zoning_floor_area(canonical_bbl)
    unused = unused_floor_area_data(existing).to_dict()

    return {
        "contract_version": CONTRACT_VERSION,
        "comparable_sales": _serialize_comparable_sales(comparables),
        "unused_floor_area": unused,
    }


@router.get("/properties/{bbl}/parity", include_in_schema=False)
def get_parity(
    request: Request,
    bbl: str,
    transport: Transport = Depends(get_dof_transport),  # noqa: B008
) -> JSONResponse:
    """Read the parity data (comparable sales + the unused-floor-area line) for one
    BBL. Feature-flag gated OFF by default (INTERNAL_PARITY_READ_ENABLED), and the
    data is Lane B behaviour produced only when LANE_B_ENABLED is also on."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the
    # feature exists. Checked FIRST, before a correlation id is minted.
    if not internal_parity_read_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Guard 2 (NB1): per-caller rate limit BEFORE any validation or upstream work,
    # so one unauthenticated GET that would drive TWO live SODA calls is bounded.
    if not get_rate_limiter().allow(caller_key(request)):
        logger.info("parity_read_v1 rate_limited correlation_id=%s", correlation_id)
        return _rate_limited_429(correlation_id)

    # 1. Validate the BBL BEFORE any provider call (typed 422; zero I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "parity_read_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _validation_error_422(
            correlation_id,
            code=payload["code"],
            message=payload["message"],
            raw_value=payload["raw_value"],
        )

    canonical = normalized.canonical

    # 2. Lane B gate: the comparable-sales data (and its LIVE DOF calls) are Lane B
    #    behaviour. With LANE_B_ENABLED off, withhold as a bounded 503 and make NO
    #    live call - only Lane B may reach live city APIs.
    if not lane_enabled(LANE_B):
        logger.info(
            "parity_read_v1 inputs_unavailable reason=lane_b_disabled correlation_id=%s",
            correlation_id,
        )
        return _inputs_unavailable_503(correlation_id)

    # 3. Produce the document (two live DOF calls through the injected transport).
    #    A fail-safe unavailability is a bounded 503; any other exception is a
    #    generic 500.
    try:
        document = _build_parity_document(canonical, transport, correlation_id)
    except _ParityUnavailable as exc:
        logger.info(
            "parity_read_v1 inputs_unavailable reason=%s correlation_id=%s",
            exc.reason, correlation_id,
        )
        return _inputs_unavailable_503(correlation_id)
    except Exception:
        logger.error(
            "parity_read_v1 unexpected_error stage=produce correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 4. Contract-guard the built document and guard its serialisation before send.
    #    A built document that fails the contract is a typed 500.
    try:
        validate_parity_data_document(document)
        _assert_json_safe(document)
    except StudyContractError:
        logger.error("parity_read_v1 contract_invalid correlation_id=%s", correlation_id)
        return _internal_contract_error_500(correlation_id)
    except Exception:
        logger.error("parity_read_v1 serialization_unsafe correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
