"""Geoclient v2 ``/address`` connector (task M2-T021; reworked after the
G1/G3/G4/G5 gate wave at d4cdbe79).

Resolves a NYC street address (house number + street + borough-or-zip) to the
city-canonical address, BBL, BIN and coordinates through the official
Geoclient v2 API behind the NYC API Developers Portal gateway.

Source facts (docs/research/M0-T002-geoclient-address-resolution.md, all
retrieved 2026-07-14 unless noted):

- **Base URL** (section 2.2): ``https://api.nyc.gov/geoclient/v2``; the
  ``/address`` endpoint proxies Geosupport Function 1B. Params:
  ``houseNumber`` (required), ``street`` (required), ``borough`` (required if
  ``zip`` not given), ``zip`` (required if ``borough`` not given). Query
  values are percent-encoded (``%20`` for spaces) — the encoding the three
  recorded fixtures were captured with, asserted by test against the
  fixtures' own ``request_url``.
- **Auth** (section 2.3): subscription key in the
  ``Ocp-Apim-Subscription-Key`` HTTP header (the documented method; the
  undocumented query-string alternative is deliberately NOT used so the key
  never appears in any URL). The key is read AT CALL TIME from the
  ``GEOCLIENT_SUBSCRIPTION_KEY`` environment variable, sent ONLY as that
  header, and never stored, logged, echoed in errors, or embedded in
  provenance. NOTE: the injected ``transport`` callable receives the headers
  dict INCLUDING the key — that is what makes offline testing possible, and
  it means any future instrumenting/caching transport wrapper is itself a
  key-handling surface and must be reviewed as one.
- **Status model** (section 2.7): HTTP status covers the service; the
  geocoding outcome lives in Geosupport return codes (GRC) INSIDE a 200
  response. ``/address`` is TWO sub-calls and BOTH must be checked:
  ``geosupportReturnCode``/``reasonCode``/``message`` and
  ``geosupportReturnCode2``/``reasonCode2``/``message2``. The documented
  aliases ``returnCode1e``/``returnCode1a`` (and reason/message
  counterparts) are DELIBERATELY not consulted: every recorded response
  carries both forms with identical values, the primary names are the
  documented canonical ones, and a hypothetical alias-only response fails
  CLOSED as ``unrecognized_status`` rather than being half-guessed.
  GRC semantics (User Guide Table 4 + UPG Appendix 4): ``00`` success;
  ``01`` success with warnings; ``EE`` street not recognized WITH
  similar-name suggestions (shape recorded live in fixture G02); ``11`` not
  recognized, no similar names; every other code is classified into the
  documented reject/error class here. KNOWN NARROWING, disclosed: UPG
  Appendix 4 also documents ``50`` and ``75`` as alternative-carrying
  classes; this connector classifies them ``rejected`` and does not extract
  their alternatives, because no recorded fixture pins their response shape.
  A follow-up capture task may widen ``_GRC_AMBIGUOUS`` with evidence.
- **Sub-call asymmetry**: "a significant number of locations" are valid for
  only ONE of the two sub-calls. Whether Geoclient omits the second code in
  such responses is NOT established by any fixture; if it ever does, this
  connector fails CLOSED (``unrecognized_status``) rather than guessing.
  Both codes are always surfaced so the caller can distinguish the cases.
- **Null omission** (section 2.5 / fixture G01): Geoclient omits null fields
  per response. Absence of a key is NOT evidence of absence of data, and
  this connector never fabricates a value for an absent field. An
  empty-string source value is likewise preserved verbatim (it is data, not
  absence). **Type drift** is the third honesty rule: a canonical field the
  source carried with a DRIFTED type (a numeric ``bbl``, a string
  ``latitude``) is surfaced as ``None`` on the canonical field — never
  coerced — while the drifted value stays verbatim in ``raw_fields``. On the
  canonical field alone, ``None`` therefore means "omitted OR drifted";
  consult ``raw_fields`` when the distinction matters.
- **Rate limits** (section 2.4): officially UNKNOWN. Retries are bounded and
  use the shared jittered policy, which honors an upstream ``Retry-After``
  within ``retry_after_cap``.

Transport: the shared hardened stack (:mod:`app.resilience.transport`) —
bounded body read, NO redirect following (the redirect refusal is what keeps
the subscription key from ever being re-sent to a redirect target), bounded
retry on 429/5xx/timeout/network only, one optional
:class:`~app.resilience.budget.AnalysisBudget` unit consumed per attempt.

TRANSPORT, NEVER INTERPRET: canonical fields are surfaced verbatim as the
source emitted them (identifiers stay strings; coordinates stay the source's
JSON numbers, so an integer stays ``int``); the full response ``address``
object rides along in ``raw_fields`` (a deep copy, defense-in-depth: the
caller receives an independent object, never the connector's own parse);
suggestion selection is ALWAYS the
caller's decision. CAUTION for consumers: ``grc_message``/``grc2_message``,
``suggestions`` and ``raw_fields`` are UNSANITIZED source text that reflects
caller input back (fixture G02's message quotes the user's typed street) —
escape on render and never log them verbatim.
"""

from __future__ import annotations

import copy
import json
import logging
import os
import re
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from random import Random
from typing import NoReturn
from urllib.parse import quote, urlencode

from app.connectors.pluto_soda import CANONICALIZATION_SPEC, canonical_json_digest
from app.resilience.budget import AnalysisBudget
from app.resilience.transport import (
    Transport,
    TransportResponse,
    jittered_retry_after_delay,
    request_with_retry,
    standard_retry_hooks,
    urllib_transport,
)

__all__ = [
    "ENDPOINT_URL",
    "KEY_ENV_VAR",
    "KEY_HEADER",
    "RESOLUTION_STATUSES",
    "SOURCE_ID",
    "AddressResolution",
    "AuthFailedError",
    "GeoclientConnectorError",
    "InvalidInputError",
    "KeyMissingError",
    "MalformedResponseError",
    "RateLimitedError",
    "RequestBudgetExceededError",
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
DEFAULT_BACKOFF_CAP_SECONDS = 30.0
DEFAULT_RETRY_AFTER_CAP_SECONDS = 120.0

# Caller-input length caps (G5 C4): fail closed before any I/O so oversized
# input can never inflate retry logs, error payloads, or upstream quota use.
# Geosupport house numbers and street names are short; these are generous.
MAX_HOUSE_NUMBER_CHARS = 32
MAX_STREET_CHARS = 120
MAX_BOROUGH_CHARS = 32
MAX_ZIP_CHARS = 16

# GRC classes per User Guide Table 4 / UPG Appendix 4 (research section 2.7).
# See the module docstring for the disclosed 50/75 narrowing.
_GRC_SUCCESS = frozenset({"00"})
_GRC_WARNING = frozenset({"01"})
_GRC_AMBIGUOUS = frozenset({"EE"})
_GRC_NOT_FOUND = frozenset({"11"})
# A GRC is exactly two characters, digits or uppercase letters, per every
# observed and documented value. fullmatch, so a trailing newline is invalid
# shape (fail closed), not a match.
_GRC_SHAPE_RE = re.compile(r"[0-9A-Z]{2}")

# Bound on how many streetName<i>/streetCode<i> suggestion slots are walked.
# The response's declared count (numberOfStreetCodesAndNamesInList) is NOT
# trusted in either direction (G1 finding 4): the walk always covers all
# slots up to this bound and surfaces every populated one; the declared
# count remains available verbatim in raw_fields.
_MAX_SUGGESTIONS = 32

# Sanitizer for untrusted response text embedded in ERROR detail payloads and
# log lines (M2-wave _safe_text pattern, hardened per G5 C1/C2): fullmatch so
# a trailing newline cannot split a log record, and the repr() fallback is
# length-capped so a hostile value cannot inflate a record.
_SAFE_TEXT_MAX_CHARS = 300
_SAFE_TEXT_RE = re.compile(r"[A-Za-z0-9 .,:;'\"()\[\]/?_%=-]{1,300}")

# Cap on how many response top-level keys a malformed-shape error reports
# (G5 C3): enough to diagnose drift, never an amplification surface.
_MAX_REPORTED_KEYS = 20


def _safe_text(value: object) -> str:
    if isinstance(value, str) and _SAFE_TEXT_RE.fullmatch(value):
        return value
    return repr(value)[:_SAFE_TEXT_MAX_CHARS]


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
    """Caller input rejected (type, presence, or length) before any network
    attempt."""

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


class RequestBudgetExceededError(GeoclientConnectorError):
    """The caller-supplied per-analysis upstream request budget is exhausted
    (one unit per attempt, consumed before I/O by the shared engine)."""

    error_type = "request_budget_exceeded"


# ---------------------------------------------------------------------------
# Result contract
# ---------------------------------------------------------------------------

#: Outcome statuses, exhaustive. ``_classify`` can return nothing else, and a
#: test pins that.
#: - ``resolved``: both sub-call GRCs are 00.
#: - ``resolved_with_warnings``: both GRCs in {00, 01}, at least one 01; the
#:   warning messages are surfaced on ``grc_message``/``grc2_message``.
#: - ``ambiguous``: a GRC is EE — the source returned similar-name
#:   suggestions, surfaced verbatim; the connector NEVER picks one.
#: - ``not_found``: a GRC is 11 (not recognized, no similar names).
#: - ``rejected``: every other valid-shape GRC (the documented reject/error
#:   class, e.g. 42 ADDRESS NUMBER OUT OF RANGE; also 50/75 — see the
#:   disclosed narrowing in the module docstring).
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
    """Typed resolution outcome.

    Canonical fields are ``None`` in exactly two cases: the source OMITTED
    the field (null omission — never fabricated), or the source carried it
    with a DRIFTED type (a non-string identifier, a non-number coordinate) —
    drift is never coerced onto the canonical field; the drifted value is
    preserved verbatim in ``raw_fields``. ``None`` alone does not
    distinguish the two — consult ``raw_fields`` when that matters. An
    empty-string source value is preserved as ``""``. Identifier fields
    (``bbl``, ``bin``, street codes) are strings verbatim;
    ``latitude``/``longitude`` are the source's JSON numbers verbatim (an
    integer stays ``int``).

    NOTE (deliberate, per the two-sub-call model): canonical fields may be
    POPULATED on non-``resolved`` statuses — e.g. a ``not_found`` outcome
    whose one valid sub-call still carried a ``bbl``, or a ``rejected``
    outcome that still normalized the street name. The status, both GRC
    codes and both messages are always surfaced so the caller can tell these
    cases apart; consumers must branch on ``status``, never on field
    presence.
    """

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
    latitude: float | int | None = None
    longitude: float | int | None = None
    # Geosupport status, BOTH sub-calls, verbatim.
    grc: str | None = None
    grc_reason: str | None = None
    grc_message: str | None = None
    grc2: str | None = None
    grc2_reason: str | None = None
    grc2_message: str | None = None
    # EE similar-name suggestions, verbatim, in source slot order. Selection
    # is the caller's (ultimately the user's) decision — never made here.
    suggestions: list[dict] = field(default_factory=list)
    # The ENTIRE response "address" object. Deep copy as defense-in-depth —
    # the caller gets an independent object, never the connector's own
    # parse. Recorded values are all scalars today, so no external assertion
    # can observe the copy (G1/G3 re-review N1/N2: the prior test claiming
    # to pin it was vacuous and is removed, not replaced with another
    # tautology). Unsanitized source text; see the module docstring's
    # consumer caution.
    raw_fields: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _classify(grc: object, grc2: object) -> str:
    """Map the GRC pair to an outcome status. BOTH sub-calls always count
    (packet S2): a clean success requires BOTH codes to be exactly ``"00"``,
    and a missing or shape-invalid code on EITHER side fails closed."""
    codes = (grc, grc2)
    shaped = [
        c for c in codes if isinstance(c, str) and _GRC_SHAPE_RE.fullmatch(c)
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
    """EE similar-name list: ``streetName1..N``/``streetCode1..N`` (shape
    recorded live, fixture G02). The response's declared count
    (``numberOfStreetCodesAndNamesInList``) is untrusted in BOTH directions
    and is not consulted (G1 finding 4: trusting it downward would silently
    discard suggestions the source actually returned): every slot up to
    ``_MAX_SUGGESTIONS`` is walked, populated slots are surfaced verbatim in
    slot order, empty or missing slots are skipped, and a slot with a name
    but no code carries only the name. The declared count itself remains
    available verbatim in ``raw_fields``."""
    suggestions: list[dict] = []
    for i in range(1, _MAX_SUGGESTIONS + 1):
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
    """Verbatim string transport: absent or non-string -> None; an
    empty-string SOURCE VALUE is preserved as ``""`` (it is data, not
    absence — the mirror image of the fabrication rule)."""
    value = address.get(key)
    return value if isinstance(value, str) else None


def _number_or_none(address: Mapping, key: str) -> float | int | None:
    """Verbatim number transport. bool is an int subclass; a boolean here
    would be malformed, not a coordinate — treated as absent rather than
    coerced. A string number is NOT parsed (transport, never interpret);
    it remains available verbatim in raw_fields."""
    value = address.get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return None


def _validated_input(
    value: object, *, name: str, max_chars: int, required: bool, correlation_id: str
) -> str | None:
    """Type-, presence- and length-check one caller input (G1 finding 2 and
    G5 C4): every rejection is a typed InvalidInputError BEFORE any network
    attempt; no value content is echoed into the error."""
    if value is None:
        stripped = ""
    elif isinstance(value, str):
        stripped = value.strip()
    else:
        raise InvalidInputError(
            f"{name} must be a string, got {type(value).__name__}",
            correlation_id=correlation_id,
            detail={"param": name, "received_type": type(value).__name__},
        )
    if not stripped:
        if required:
            raise InvalidInputError(
                f"{name} is required",
                correlation_id=correlation_id,
                detail={"param": name},
            )
        return None
    if len(stripped) > max_chars:
        raise InvalidInputError(
            f"{name} exceeds the {max_chars}-character bound",
            correlation_id=correlation_id,
            detail={"param": name, "length": len(stripped), "max_chars": max_chars},
        )
    return stripped


def _request(
    url: str,
    *,
    transport: Transport,
    headers: dict[str, str],
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    backoff_cap: float,
    retry_after_cap: float,
    rng: Random,
    sleep: Callable[[float], None],
    wall_clock: Callable[[], datetime],
    correlation_id: str,
    budget: AnalysisBudget | None,
) -> TransportResponse:
    """Bounded retry on 429/5xx/timeout/network failure only, using the
    shared M1-T009 jittered policy (honors upstream ``Retry-After`` within
    ``retry_after_cap``; jitter decorrelates concurrent retries). 401/403
    raise AuthFailedError immediately (never retried, never body-echoed);
    every other unexpected status — refused 3xx redirects included — raises
    SourceUnavailableError."""

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
            budget_error=RequestBudgetExceededError,
        ),
        compute_delay=jittered_retry_after_delay(
            backoff_base=backoff_base,
            backoff_cap=backoff_cap,
            retry_after_cap=retry_after_cap,
            rng=rng,
            wall_clock=wall_clock,
        ),
        sleep=sleep,
        budget=budget,
    )


def _malformed_shape_detail(url: str, parsed: object) -> dict:
    """Bounded diagnosis of a 200 body without the documented shape (G5 C3):
    at most ``_MAX_REPORTED_KEYS`` sanitized key names, each length-capped,
    with an explicit truncation marker — never an amplification surface."""
    if not isinstance(parsed, dict):
        return {"url": url, "body_shape": _safe_text(type(parsed).__name__)}
    keys = sorted(map(_safe_text, parsed.keys()))
    detail: dict = {"url": url, "top_level_keys": keys[:_MAX_REPORTED_KEYS]}
    if len(keys) > _MAX_REPORTED_KEYS:
        detail["top_level_keys_truncated"] = True
        detail["top_level_key_count"] = len(keys)
    return detail


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
    backoff_cap: float = DEFAULT_BACKOFF_CAP_SECONDS,
    retry_after_cap: float = DEFAULT_RETRY_AFTER_CAP_SECONDS,
    rng: Random | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    env: Mapping[str, str] | None = None,
    budget: AnalysisBudget | None = None,
) -> AddressResolution:
    """Resolve one address through Geoclient v2 ``/address``.

    ``borough`` or ``zip_code`` is required (endpoint contract, research
    section 2.2). The subscription key comes from ``key`` or, when ``None``,
    from the ``GEOCLIENT_SUBSCRIPTION_KEY`` environment variable AT CALL
    TIME (never captured at import); an explicitly passed empty/whitespace
    ``key`` does NOT fall back to the environment. A missing key raises
    :class:`KeyMissingError` before any network attempt. The key is sent
    only as the ``Ocp-Apim-Subscription-Key`` header and appears nowhere in
    the returned outcome, its provenance, any error, or any log line.

    Geocoding outcomes (success / warnings / ambiguous / not found /
    rejected / unrecognized) RETURN an :class:`AddressResolution`; transport,
    auth, budget and input failures RAISE typed
    :class:`GeoclientConnectorError` subclasses.
    """
    correlation_id = uuid.uuid4().hex

    house_number_in = _validated_input(
        house_number, name="house_number", max_chars=MAX_HOUSE_NUMBER_CHARS,
        required=True, correlation_id=correlation_id,
    )
    street_in = _validated_input(
        street, name="street", max_chars=MAX_STREET_CHARS,
        required=True, correlation_id=correlation_id,
    )
    borough_in = _validated_input(
        borough, name="borough", max_chars=MAX_BOROUGH_CHARS,
        required=False, correlation_id=correlation_id,
    )
    zip_in = _validated_input(
        zip_code, name="zip_code", max_chars=MAX_ZIP_CHARS,
        required=False, correlation_id=correlation_id,
    )
    assert house_number_in is not None and street_in is not None  # noqa: S101
    if borough_in is None and zip_in is None:
        raise InvalidInputError(
            "either borough or zip_code is required (Geoclient /address "
            "contract)",
            correlation_id=correlation_id,
            detail={},
        )

    if key is not None:
        resolved_key: str | None = key.strip() if isinstance(key, str) else None
    else:
        source = os.environ if env is None else env
        raw_key = source.get(KEY_ENV_VAR)
        resolved_key = raw_key.strip() if isinstance(raw_key, str) else None
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
    # quote_via=quote: percent-encoding (%20 for spaces), the exact encoding
    # the recorded fixtures' request_url fields were captured with (G4
    # finding 5); default urlencode would emit '+', which no fixture
    # documents as accepted by the gateway.
    url = f"{ENDPOINT_URL}?{urlencode(params, quote_via=quote)}"
    headers = {"Accept": "application/json", KEY_HEADER: resolved_key}

    # Resolved at CALL time (not bound as a parameter default) so the seam
    # stays monkeypatchable and the no-network guard tests stay meaningful.
    if transport is None:
        transport = urllib_transport

    response = _request(
        url,
        transport=transport,
        headers=headers,
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_cap=backoff_cap,
        retry_after_cap=retry_after_cap,
        rng=rng if rng is not None else Random(),
        sleep=sleep,
        wall_clock=clock,
        correlation_id=correlation_id,
        budget=budget,
    )

    try:
        parsed = json.loads(response.body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        raise MalformedResponseError(
            "Geoclient returned HTTP 200 with a non-JSON body",
            correlation_id=correlation_id,
            detail={"url": url, "body_chars": len(response.body)},
        ) from None
    if not isinstance(parsed, dict) or not isinstance(parsed.get("address"), dict):
        raise MalformedResponseError(
            "Geoclient returned HTTP 200 without the documented "
            "{'address': {...}} shape",
            correlation_id=correlation_id,
            detail=_malformed_shape_detail(url, parsed),
        )
    address: dict = parsed["address"]

    # Stamped AFTER the successful parse, deliberately: retrieved_at
    # describes the response the outcome carries, not an attempt.
    retrieved_at = _rfc3339(clock())
    grc = address.get("geosupportReturnCode")
    grc2 = address.get("geosupportReturnCode2")
    status = _classify(grc, grc2)

    # A hostile 200 body can nest deeply enough that json.loads's C scanner
    # accepts it while the pure-Python deepcopy/canonicalization here blow
    # the recursion limit. That is a malformed response and stays inside the
    # typed taxonomy (G5 re-review N1); `from None` drops the body-laden
    # recursion frames so no hostile content rides the traceback.
    try:
        raw_fields = copy.deepcopy(address)
        response_digest = canonical_json_digest(parsed)
    except RecursionError:
        raise MalformedResponseError(
            "Geoclient returned HTTP 200 with a body nested too deeply "
            "to process",
            correlation_id=correlation_id,
            detail={"url": url, "body_chars": len(response.body)},
        ) from None

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
        raw_fields=raw_fields,
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
            "response_digest": response_digest,
            "digest_canonicalization": CANONICALIZATION_SPEC,
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
