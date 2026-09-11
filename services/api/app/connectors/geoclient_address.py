"""Geoclient v2 ``/address`` connector (task M2-T021).

Resolves a NYC street address (house number + street + borough-or-zip) to the
city-canonical address, BBL, BIN and coordinates through the official
Geoclient v2 API behind the NYC API Developers Portal gateway.

Source facts (docs/research/M0-T002-geoclient-address-resolution.md, all
retrieved 2026-07-14 unless noted):

- **Base URL** (section 2.2): ``https://api.nyc.gov/geoclient/v2``; the
  ``/address`` endpoint proxies Geosupport Function 1B. Params:
  ``houseNumber`` (required), ``street`` (required), ``borough`` (required if
  ``zip`` not given), ``zip`` (required if ``borough`` not given).
- **Auth** (section 2.3): subscription key in the
  ``Ocp-Apim-Subscription-Key`` HTTP header (the documented method; the
  undocumented query-string alternative is deliberately NOT used so the key
  never appears in any URL). The key is read at call time from the
  ``GEOCLIENT_SUBSCRIPTION_KEY`` environment variable, sent ONLY as that
  header, and never stored, logged, echoed in errors, or embedded in
  provenance.
- **Status model** (section 2.7): HTTP status covers the service; the
  geocoding outcome lives in Geosupport return codes (GRC) INSIDE a 200
  response. ``/address`` is TWO sub-calls and BOTH must be checked:
  ``geosupportReturnCode``/``reasonCode``/``message`` (alias
  ``returnCode1e``/``reasonCode1e``) and ``geosupportReturnCode2``/
  ``reasonCode2``/``message2`` (alias ``returnCode1a``/``reasonCode1a``).
  "There are a significant number of locations where data is valid and/or
  available for only one of these two sub-function calls." GRC semantics
  (User Guide Table 4 + UPG Appendix 4): ``00`` success; ``01`` success with
  warnings; ``EE`` street not recognized WITH similar-name suggestions
  (returned as ``streetName1..N``/``streetCode1..N`` with
  ``numberOfStreetCodesAndNamesInList`` — shape recorded live in fixture
  G02); ``11`` not recognized, no similar names; every other code is the
  documented reject/error class (e.g. ``42`` ADDRESS NUMBER OUT OF RANGE,
  recorded live in fixture G03).
- **Null omission** (section 2.5 / fixture G01): Geoclient omits null fields
  per response. Absence of a key is NOT evidence of absence of data, and this
  connector never fabricates a value for an absent field.
- **Rate limits** (section 2.4): officially UNKNOWN. The retry budget here is
  bounded and small; live fixture captures are single KB-scale requests.

Transport: the shared hardened stack (:mod:`app.resilience.transport`) —
bounded body read, NO redirect following (the redirect refusal is what keeps
the subscription key from ever being re-sent to a redirect target), bounded
retry on 429/5xx/timeout/network only.

TRANSPORT, NEVER INTERPRET: canonical fields are surfaced verbatim as the
source emitted them (identifiers stay strings; coordinates stay the source's
JSON numbers); the full response ``address`` object rides along verbatim in
``raw_fields``; suggestion selection is ALWAYS the caller's decision.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import NoReturn
from urllib.parse import urlencode

from app.connectors.pluto_soda import canonical_json_digest
from app.resilience.transport import (
    DEFAULT_OPENER,
    Transport,
    TransportResponse,
    fixed_exponential_delay,
    request_with_retry,
    standard_retry_hooks,
)
from app.resilience.transport import (
    urllib_transport as _shared_urllib_transport,
)

__all__ = [
    "ENDPOINT_URL",
    "KEY_ENV_VAR",
    "KEY_HEADER",
    "SOURCE_ID",
    "AddressResolution",
    "AuthFailedError",
    "GeoclientConnectorError",
    "InvalidInputError",
    "KeyMissingError",
    "MalformedResponseError",
    "RateLimitedError",
    "SourceTimeoutError",
    "SourceUnavailableError",
    "resolve_address",
    "urllib_transport",
]

logger = logging.getLogger("app.connectors.geoclient_address")

SOURCE_ID = "nyc-oti-geoclient-v2"  # source registry record: geoclient.json
ENDPOINT_URL = "https://api.nyc.gov/geoclient/v2/address"
KEY_ENV_VAR = "GEOCLIENT_SUBSCRIPTION_KEY"
KEY_HEADER = "Ocp-Apim-Subscription-Key"

DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BACKOFF_BASE_SECONDS = 0.5

# GRC classes per User Guide Table 4 / UPG Appendix 4 (research section 2.7).
_GRC_SUCCESS = frozenset({"00"})
_GRC_WARNING = frozenset({"01"})
_GRC_AMBIGUOUS = frozenset({"EE"})
_GRC_NOT_FOUND = frozenset({"11"})
# A GRC is two characters, digits or uppercase letters, per every observed and
# documented value. Anything outside this SHAPE is unrecognized and fails
# closed (packet S8); anything of valid shape outside the sets above is the
# documented reject/error class ("GRC > 01 = reject/error").
_GRC_SHAPE_RE = re.compile(r"^[0-9A-Z]{2}$")

# Bound on how many streetName<i>/streetCode<i> suggestion slots are walked,
# whatever numberOfStreetCodesAndNamesInList claims (hostile-count guard).
_MAX_SUGGESTIONS = 32

# Sanitizer for untrusted response text embedded in ERROR detail payloads
# (M2-wave _safe_text pattern). Outcome fields carry source text verbatim —
# they are data for the caller; error details reach logs.
_SAFE_TEXT_RE = re.compile(r"^[A-Za-z0-9 .,:;'\"()\[\]/?_%=-]{1,300}$")


def _safe_text(value: object) -> str:
    if isinstance(value, str) and _SAFE_TEXT_RE.match(value):
        return value
    return repr(value)


# ---------------------------------------------------------------------------
# Error taxonomy. Payloads never contain stack traces, headers, bodies, or
# the subscription key.
# ---------------------------------------------------------------------------

class GeoclientConnectorError(Exception):
    """Base typed connector error."""

    error_type = "source_unavailable"

    def __init__(self, message: str, *, correlation_id: str, detail: dict | None = None):
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id
        self.detail = detail or {}

    def to_payload(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "source_id": SOURCE_ID,
            "endpoint": ENDPOINT_URL,
            "detail": self.detail,
        }


class InvalidInputError(GeoclientConnectorError):
    """Caller input rejected before any network attempt."""

    error_type = "invalid_input"


class KeyMissingError(GeoclientConnectorError):
    """No subscription key available. Raised BEFORE any network attempt; the
    detail names the environment variable, never any value."""

    error_type = "key_missing"


class AuthFailedError(GeoclientConnectorError):
    """HTTP 401/403 from the API gateway. The message and detail carry the
    status only — never the key and never the response body."""

    error_type = "auth_failed"


class RateLimitedError(GeoclientConnectorError):
    """HTTP 429 persisted through the bounded retry budget."""

    error_type = "rate_limited"


class SourceTimeoutError(GeoclientConnectorError):
    """Connect/read timeout persisted through the retry budget."""

    error_type = "timeout"


class SourceUnavailableError(GeoclientConnectorError):
    """Network failure, 5xx persisted through retries, or an unexpected
    non-auth HTTP status (refused 3xx redirects included)."""

    error_type = "source_unavailable"


class MalformedResponseError(GeoclientConnectorError):
    """HTTP 200 whose body is not the documented ``{"address": {...}}``
    JSON shape. Fail closed; never partially parsed into a result."""

    error_type = "malformed_response"


# ---------------------------------------------------------------------------
# Transport seam (same accepted monkeypatch shape as the sibling connectors).
# ---------------------------------------------------------------------------

_OPENER = DEFAULT_OPENER


def urllib_transport(url: str, headers: dict[str, str], timeout: float) -> TransportResponse:
    """Default stdlib transport via the shared hardened implementation
    (bounded read, no redirect following — the subscription key header is
    never re-sent to a redirect target)."""
    return _shared_urllib_transport(url, headers, timeout, opener=_OPENER)


# ---------------------------------------------------------------------------
# Result contract
# ---------------------------------------------------------------------------

#: Outcome statuses, exhaustive:
#: - ``resolved``: both sub-call GRCs are 00.
#: - ``resolved_with_warnings``: both GRCs in {00, 01}, at least one 01; the
#:   warning messages are surfaced.
#: - ``ambiguous``: a GRC is EE — the source returned similar-name
#:   suggestions, surfaced verbatim; the connector NEVER picks one.
#: - ``not_found``: a GRC is 11 (not recognized, no similar names).
#: - ``rejected``: any other valid-shape GRC (the documented reject/error
#:   class, e.g. 42 ADDRESS NUMBER OUT OF RANGE).
#: - ``unrecognized_status``: a GRC of invalid shape or absent — fail closed,
#:   never success.
RESOLUTION_STATUSES = (
    "resolved",
    "resolved_with_warnings",
    "ambiguous",
    "not_found",
    "rejected",
    "unrecognized_status",
)


@dataclass
class AddressResolution:
    """Typed resolution outcome. Canonical fields are ``None`` when the
    source omitted them (null omission — never fabricated). Identifier
    fields (``bbl``, ``bin``, street codes) are strings verbatim;
    ``latitude``/``longitude`` are the source's JSON numbers verbatim."""

    status: str
    correlation_id: str
    # Echo of the request (what the CALLER asked; the source's own echo of
    # its inputs lives in raw_fields under houseNumberIn/streetName1In/...).
    house_number_in: str
    street_in: str
    borough_in: str | None
    zip_in: str | None
    # Canonical resolution (None when absent from the response).
    bbl: str | None = None
    bin: str | None = None
    street_name_normalized: str | None = None
    borough_name: str | None = None
    zip_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    # Geosupport status, BOTH sub-calls, verbatim.
    grc: str | None = None
    grc_reason: str | None = None
    grc_message: str | None = None
    grc2: str | None = None
    grc2_reason: str | None = None
    grc2_message: str | None = None
    # EE similar-name suggestions, verbatim, in source order. Selection is
    # the caller's (ultimately the user's) decision — never made here.
    suggestions: list[dict] = field(default_factory=list)
    # The ENTIRE response "address" object, verbatim (transport honesty:
    # 171 fields on the G01 fixture; callers take what they need).
    raw_fields: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _classify(grc: object, grc2: object) -> str:
    """Map the GRC pair to an outcome status. BOTH sub-calls always count
    (packet S2): a clean success requires BOTH codes to be 00."""
    codes = (grc, grc2)
    shaped = [
        c for c in codes if isinstance(c, str) and _GRC_SHAPE_RE.match(c)
    ]
    if len(shaped) != 2:
        return "unrecognized_status"
    if any(c in _GRC_AMBIGUOUS for c in shaped):
        return "ambiguous"
    if any(c in _GRC_NOT_FOUND for c in shaped):
        return "not_found"
    if all(c in _GRC_SUCCESS for c in shaped):
        return "resolved"
    if all(c in _GRC_SUCCESS | _GRC_WARNING for c in shaped):
        return "resolved_with_warnings"
    return "rejected"


def _extract_suggestions(address: Mapping) -> list[dict]:
    """EE similar-name list: ``streetName1..N``/``streetCode1..N`` with
    ``numberOfStreetCodesAndNamesInList`` (shape recorded live, fixture G02).
    The declared count is untrusted: it is bounds-clamped, and slots are also
    walked past a missing index only up to the clamp. Entries are verbatim;
    a slot with no street name is skipped, never fabricated."""
    declared = address.get("numberOfStreetCodesAndNamesInList")
    try:
        count = int(str(declared))
    except (TypeError, ValueError):
        count = _MAX_SUGGESTIONS
    count = max(0, min(count, _MAX_SUGGESTIONS))
    suggestions: list[dict] = []
    for i in range(1, count + 1):
        name = address.get(f"streetName{i}")
        if not isinstance(name, str) or not name:
            continue
        entry: dict = {"street_name": name}
        code = address.get(f"streetCode{i}")
        if isinstance(code, str) and code:
            entry["street_code"] = code
        suggestions.append(entry)
    return suggestions


def _string_or_none(address: Mapping, key: str) -> str | None:
    value = address.get(key)
    return value if isinstance(value, str) and value != "" else None


def _number_or_none(address: Mapping, key: str) -> float | None:
    value = address.get(key)
    # bool is an int subclass; a boolean here would be malformed, not a
    # coordinate — treat it as absent rather than coercing.
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return None


def _request(
    url: str,
    *,
    transport: Transport,
    headers: dict[str, str],
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    sleep: Callable[[float], None],
    correlation_id: str,
) -> TransportResponse:
    """Bounded retry on 429/5xx/timeout/network failure only; 401/403 raise
    AuthFailedError immediately (never retried, never body-echoed)."""

    def _raise_for_unexpected_status(response: TransportResponse) -> NoReturn:
        if response.status in (401, 403):
            raise AuthFailedError(
                f"Geoclient gateway rejected the subscription key (HTTP "
                f"{response.status}); the key value is never included in "
                f"errors or logs",
                correlation_id=correlation_id,
                detail={"http_status": response.status, "url": url},
            )
        raise SourceUnavailableError(
            f"unexpected HTTP status {response.status} from the Geoclient "
            f"endpoint",
            correlation_id=correlation_id,
            detail={"http_status": response.status, "url": url},
        )

    return request_with_retry(
        url,
        transport=transport,
        headers=headers,
        timeout=timeout,
        max_attempts=max_attempts,
        hooks=standard_retry_hooks(
            logger=logger,
            log_label="geoclient_address",
            correlation_id=correlation_id,
            url=url,
            sanitize_network_reason=_safe_text,
            rate_limited_error=RateLimitedError,
            rate_limited_message=(
                "Geoclient gateway throttled the request (HTTP 429) and the "
                "retry budget is exhausted"
            ),
            timeout_error=SourceTimeoutError,
            timeout_message=(
                "Geoclient request timed out and the retry budget is exhausted"
            ),
            unavailable_error=SourceUnavailableError,
            unavailable_message=(
                "Geoclient endpoint unavailable and the retry budget is "
                "exhausted"
            ),
            include_reason_kind=True,
            raise_for_unexpected_status=_raise_for_unexpected_status,
        ),
        compute_delay=fixed_exponential_delay(backoff_base),
        sleep=sleep,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_address(
    house_number: str,
    street: str,
    *,
    borough: str | None = None,
    zip_code: str | None = None,
    key: str | None = None,
    transport: Transport | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    backoff_base: float = DEFAULT_BACKOFF_BASE_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    env: Mapping[str, str] | None = None,
) -> AddressResolution:
    """Resolve one address through Geoclient v2 ``/address``.

    ``borough`` or ``zip_code`` is required (endpoint contract, research
    section 2.2). The subscription key comes from ``key`` or, when ``None``,
    from the ``GEOCLIENT_SUBSCRIPTION_KEY`` environment variable AT CALL
    TIME; a missing key raises :class:`KeyMissingError` before any network
    attempt. The key is sent only as the ``Ocp-Apim-Subscription-Key``
    header and appears nowhere in the returned outcome, its provenance, any
    error, or any log line.

    Geocoding outcomes (success / warnings / ambiguous / not found /
    rejected / unrecognized) RETURN an :class:`AddressResolution`; transport,
    auth and input failures RAISE typed :class:`GeoclientConnectorError`
    subclasses.
    """
    correlation_id = uuid.uuid4().hex

    house_number_in = (house_number or "").strip()
    street_in = (street or "").strip()
    borough_in = borough.strip() if isinstance(borough, str) and borough.strip() else None
    zip_in = zip_code.strip() if isinstance(zip_code, str) and zip_code.strip() else None
    if not house_number_in or not street_in:
        raise InvalidInputError(
            "house_number and street are both required",
            correlation_id=correlation_id,
            detail={"house_number_present": bool(house_number_in),
                    "street_present": bool(street_in)},
        )
    if borough_in is None and zip_in is None:
        raise InvalidInputError(
            "either borough or zip_code is required (Geoclient /address "
            "contract)",
            correlation_id=correlation_id,
            detail={},
        )

    source = os.environ if env is None else env
    resolved_key = key if key is not None else source.get(KEY_ENV_VAR)
    resolved_key = resolved_key.strip() if isinstance(resolved_key, str) else None
    if not resolved_key:
        raise KeyMissingError(
            f"no Geoclient subscription key available: pass key= or set the "
            f"{KEY_ENV_VAR} environment variable; no network request was "
            f"attempted",
            correlation_id=correlation_id,
            detail={"env_var": KEY_ENV_VAR},
        )

    params: dict[str, str] = {"houseNumber": house_number_in, "street": street_in}
    if borough_in is not None:
        params["borough"] = borough_in
    if zip_in is not None:
        params["zip"] = zip_in
    url = f"{ENDPOINT_URL}?{urlencode(params)}"
    headers = {"Accept": "application/json", KEY_HEADER: resolved_key}

    response = _request(
        url,
        transport=transport if transport is not None else urllib_transport,
        headers=headers,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        correlation_id=correlation_id,
    )

    try:
        parsed = json.loads(response.body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        raise MalformedResponseError(
            "Geoclient returned HTTP 200 with a non-JSON body",
            correlation_id=correlation_id,
            detail={"url": url, "body_bytes": len(response.body)},
        ) from None
    if not isinstance(parsed, dict) or not isinstance(parsed.get("address"), dict):
        raise MalformedResponseError(
            "Geoclient returned HTTP 200 without the documented "
            "{'address': {...}} shape",
            correlation_id=correlation_id,
            detail={
                "url": url,
                "top_level_keys": sorted(map(_safe_text, parsed.keys()))
                if isinstance(parsed, dict) else _safe_text(type(parsed).__name__),
            },
        )
    address: dict = parsed["address"]

    retrieved_at = _rfc3339(datetime.now(UTC))
    grc = address.get("geosupportReturnCode")
    grc2 = address.get("geosupportReturnCode2")
    status = _classify(grc, grc2)

    outcome = AddressResolution(
        status=status,
        correlation_id=correlation_id,
        house_number_in=house_number_in,
        street_in=street_in,
        borough_in=borough_in,
        zip_in=zip_in,
        bbl=_string_or_none(address, "bbl"),
        bin=_string_or_none(address, "buildingIdentificationNumber"),
        street_name_normalized=_string_or_none(address, "firstStreetNameNormalized"),
        borough_name=_string_or_none(address, "firstBoroughName"),
        zip_code=_string_or_none(address, "zipCode"),
        latitude=_number_or_none(address, "latitude"),
        longitude=_number_or_none(address, "longitude"),
        grc=grc if isinstance(grc, str) else None,
        grc_reason=_string_or_none(address, "reasonCode"),
        grc_message=_string_or_none(address, "message"),
        grc2=grc2 if isinstance(grc2, str) else None,
        grc2_reason=_string_or_none(address, "reasonCode2"),
        grc2_message=_string_or_none(address, "message2"),
        suggestions=_extract_suggestions(address) if status == "ambiguous" else [],
        raw_fields=address,
        provenance={
            "source_id": SOURCE_ID,
            "endpoint": ENDPOINT_URL,
            "request_params": dict(params),  # key is NEVER a param
            "retrieved_at": retrieved_at,
            "http_status": response.status,
            "geosupport_return_code": grc if isinstance(grc, str) else None,
            "geosupport_return_code2": grc2 if isinstance(grc2, str) else None,
            "reason_code": _string_or_none(address, "reasonCode"),
            "reason_code2": _string_or_none(address, "reasonCode2"),
            "response_digest": canonical_json_digest(parsed),
            "correlation_id": correlation_id,
        },
    )
    logger.info(
        "geoclient_address resolution correlation_id=%s status=%s grc=%s grc2=%s",
        correlation_id,
        status,
        _safe_text(grc) if grc is not None else "absent",
        _safe_text(grc2) if grc2 is not None else "absent",
    )
    return outcome
