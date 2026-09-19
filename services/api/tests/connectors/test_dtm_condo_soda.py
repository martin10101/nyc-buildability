"""Offline contract suite for the DTM condo -> base-lot-set resolver (M5-T042).

Covers the DB-002 research contract-test rows that apply to this module:
C1-C2, C3 (unit-count split - implemented as a units-side cross-consistency
check on the resolved base-lot set, research 4.3), C4-C5, C7, C9 (appbbl
independence), C10 (schema-shape guard), and C6 covered two ways: the condo_key
fallback MECHANISM with the real condo_key 301313 response, plus a clearly
labeled SYNTHETIC null-billing scenario that exercises the null-billing code
path. The research embeds NO byte-faithful raw response for a specific
NULL-billing condo (only the aggregate count 28, research 3.4), so the
null-billing-specific OFFICIAL fixture is documented in the producer report as a
source limitation for orchestrator resolution - never fabricated here. The
classification / fail-closed rules and determinism are covered too. C8 and
C11-C14 are wiring/live-era rows recorded as deferred in the producer report -
never faked here.

All research-derived fixtures are the record's byte-faithful raw responses,
embedded inline (the packet scope is three files; no separate fixtures
directory); the two synthetic fixtures (drift-decimal, null-billing scenario)
are labeled as such and assert code-path behavior only, never masquerading as
official captures. No network I/O ever happens: every test injects a URL-routed
fake transport, and the classification / fail-closed paths assert the transport
is never called.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from app.connectors.bbl import BBLValidationError
from app.connectors.dtm_condo_soda import (
    APP_TOKEN_ENV_VAR,
    CONDO_COLUMNS,
    CONDO_DATASET_ID,
    DIVERGENT_ZONING_NOTICE,
    INPUT_KIND_BBL,
    INPUT_KIND_CONDO_KEY,
    LOT_CLASS_BILLING,
    LOT_CLASS_NOT_A_CONDO,
    LOT_CLASS_UNIT,
    PATH_BILLING,
    PATH_CONDO_KEY,
    PATH_UNIT,
    RESEARCH_OBSERVED_ROWS_UPDATED_AT,
    STATUS_NOT_A_CONDO,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
    UNIT_COLUMNS,
    UNIT_DATASET_ID,
    RateLimitedError,
    SchemaDriftError,
    SourceTimeoutError,
    SourceUnavailableError,
    classify_lot,
    resolve,
    resolve_by_condo_key,
)
from app.resilience.transport import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
)

# The documented BBLValidationError vocabulary (bbl.py:44-47). The condo
# resolver's shape guard must raise ONE of these documented codes, never an
# ad-hoc string like the retired "wrong_shape" (M5-T044 item e / G3 #2).
DOCUMENTED_BBL_CODES = frozenset(
    {
        "empty",
        "non_numeric",
        "negative",
        "non_integer_decimal",
        "wrong_length",
        "invalid_borough",
        "invalid_block",
        "invalid_lot",
        "invalid_component",
    }
)


def _unicode_digits(ascii_digits: str) -> str:
    """Map an ASCII digit string to Arabic-Indic digits (U+0660..U+0669) - a
    ``\\d`` (non-ASCII) match that ``re.ASCII`` + fullmatch must reject."""
    return "".join(chr(0x0660 + int(c)) for c in ascii_digits)


def _advancing_clock(moments: list[datetime]):
    """A clock that returns each supplied moment once, in order. StopIteration
    (too few moments) surfaces as a test error, never a silent reuse."""
    iterator = iter(moments)
    return lambda: next(iterator)


class _AlwaysTransport:
    """Transport stub that returns one fixed response (or raises one fixed
    exception) for every call, regardless of URL - drives the error branches
    that RoutedTransport (which asserts on unexpected URLs) cannot."""

    def __init__(
        self,
        response: TransportResponse | None = None,
        *,
        exc: Exception | None = None,
    ) -> None:
        self.response = response
        self.exc = exc
        self.calls = 0

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        assert self.response is not None
        return self.response

# ---------------------------------------------------------------------------
# Byte-faithful raw official responses embedded from the DB-002 research
# record docs/research/condo-base-lot-resolution-sources.md.
# ---------------------------------------------------------------------------

# research section 3.3 - primary billing resolve of 3022647515 (two base lots).
BILLING_3022647515_BODY = (
    '[{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"32",'
    '"condo_base_bbl":"3022640032","condo_base_bbl_key":"3022640032301313",'
    '"condo_key":"301313","condo_number":"1313","condo_billing_bbl":"3022647515"},'
    '{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"33",'
    '"condo_base_bbl":"3022640033","condo_base_bbl_key":"3022640033301313",'
    '"condo_key":"301313","condo_number":"1313","condo_billing_bbl":"3022647515"}]'
)

# research section 4.2 - unit reverse resolve of unit BBL 3022642601.
UNIT_3022642601_BODY = (
    '[{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"32",'
    '"condo_base_bbl":"3022640032","condo_number":"1313","condo_key":"301313",'
    '"condo_base_bbl_key":"3022640032301313","unit_boro":"3","unit_block":"2264",'
    '"unit_lot":"2601","unit_bbl":"3022642601","unit_designation":"1A",'
    '"model":"T","geometry_type":"Table"}]'
)

# condo_key=301313 expansion. Faithful derivation: research 3.3 shows BOTH base
# rows of condo 1313 carry condo_key 301313, and research 4.3 confirms
# condo_key 301313 has exactly base lots {32, 33} - so a ?condo_key=301313
# query returns the same two rows as the billing query.
CONDO_KEY_301313_BODY = BILLING_3022647515_BODY  # gitleaks:allow - fixture alias, no credential

# research section 3.4 - deterministic no-match: nonexistent billing / land lot.
EMPTY_BODY = "[]"

# Synthetic negative fixture (clearly labeled): a base BBL in the PLUTO
# number-type decimal serialization. The DTM columns are TEXT (research 3.2),
# so this shape must be REJECTED fail-closed (research C7 / AS-5).
DRIFT_DECIMAL_BODY = (
    '[{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"32",'
    '"condo_base_bbl":"3022640032.00000000",'
    '"condo_base_bbl_key":"3022640032301313","condo_key":"301313",'
    '"condo_number":"1313","condo_billing_bbl":"3022647515"}]'
)

# research section 4.3 - the 20 units of condo 1313 split across its two base
# lots (14 on lot 32, 6 on lot 33). Byte-faithful grouped response; used for the
# C3 units-side cross-consistency check that the resolved base-lot set is exactly
# the set the units span.
C3_UNIT_SPLIT_BODY = (
    '[{"condo_base_bbl":"3022640032","count_unit_bbl":"14"},'
    '{"condo_base_bbl":"3022640033","count_unit_bbl":"6"}]'
)

# SYNTHETIC null-billing scenario fixture (clearly labeled, NOT an official
# capture). The research embeds no byte-faithful raw response for a specific
# NULL-billing condo (only the aggregate count 28, research 3.4). This shape is
# structurally faithful to the 9-column Condominiums schema with
# condo_billing_bbl = null, and exercises the condo_key fallback code path for a
# null-billing condo. The OFFICIAL null-billing fixture stays a documented
# source limitation for orchestrator resolution (never fabricated as official).
SYNTHETIC_NULL_BILLING_CONDO_KEY_BODY = (
    '[{"condo_base_boro":"3","condo_base_block":"9999","condo_base_lot":"40",'
    '"condo_base_bbl":"3099990040","condo_base_bbl_key":"3099990040309999",'
    '"condo_key":"309999","condo_number":"9999","condo_name":null,'
    '"condo_billing_bbl":null},'
    '{"condo_base_boro":"3","condo_base_block":"9999","condo_base_lot":"41",'
    '"condo_base_bbl":"3099990041","condo_base_bbl_key":"3099990041309999",'
    '"condo_key":"309999","condo_number":"9999","condo_name":null,'
    '"condo_billing_bbl":null}]'
)

CONDO_URL = f"https://data.cityofnewyork.us/resource/{CONDO_DATASET_ID}.json"
UNIT_URL = f"https://data.cityofnewyork.us/resource/{UNIT_DATASET_ID}.json"

FIXED_CLOCK = lambda: datetime(2026, 9, 18, 12, 0, 0, tzinfo=UTC)  # noqa: E731
FIXED_CORR = "test-correlation-id"


@pytest.fixture(autouse=True)
def _hermetic_app_token(monkeypatch):
    """Clear any ambient SOCRATA_APP_TOKEN so token behavior is determined only
    by each test, never by the developer's or CI runner's environment."""
    monkeypatch.delenv(APP_TOKEN_ENV_VAR, raising=False)


class RoutedTransport:
    """URL-routed fake transport. Any URL not in the routing table raises -
    this also proves appbbl independence: no PLUTO (64uk-42ks) URL is ever
    requested, because the table only knows the two DTM datasets."""

    def __init__(self, routes: dict[str, TransportResponse]):
        self.routes = routes
        self.requested_urls: list[str] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.requested_urls.append(url)
        if url not in self.routes:
            raise AssertionError(f"unexpected URL requested: {url}")
        return self.routes[url]


def _never_called(url: str, headers: dict, timeout: float) -> TransportResponse:
    raise AssertionError(f"transport must not be called; got {url}")


def _call(bbl: str, transport, **kwargs):
    return resolve(
        bbl,
        transport=transport,
        clock=FIXED_CLOCK,
        correlation_id=FIXED_CORR,
        **kwargs,
    )


def _billing_transport(body: str = BILLING_3022647515_BODY) -> RoutedTransport:
    return RoutedTransport(
        {f"{CONDO_URL}?condo_billing_bbl=3022647515": TransportResponse(200, body)}
    )


# --- classification --------------------------------------------------------
def test_classify_lot_ranges() -> None:
    assert classify_lot("3022647515") == LOT_CLASS_BILLING  # lot 7515
    assert classify_lot("3022642601") == LOT_CLASS_UNIT  # lot 2601
    assert classify_lot("3022640032") == LOT_CLASS_NOT_A_CONDO  # lot 0032


# --- C1: multi-lot billing resolve (AS-1) ---------------------------------
def test_c1_multi_lot_billing_resolve() -> None:
    transport = _billing_transport()
    result = _call("3022647515", transport)
    assert result.status == STATUS_RESOLVED
    assert result.lot_class == LOT_CLASS_BILLING
    assert result.resolution_path == PATH_BILLING
    assert result.base_bbls == ["3022640032", "3022640033"]
    assert result.condo_key == "301313"
    assert result.condo_number == "1313"
    # provenance populated for the one query performed.
    assert len(result.provenance) == 1
    entry = result.provenance[0]
    assert entry["dataset_id"] == CONDO_DATASET_ID
    assert entry["query_kind"] == "condo_billing_bbl"
    assert entry["record_count"] == 2
    assert entry["retrieved_at"] == "2026-09-18T12:00:00Z"


def test_c1_rows_updated_at_injected_into_provenance() -> None:
    transport = _billing_transport()
    result = _call(
        "3022647515", transport,
        dataset_rows_updated_at=RESEARCH_OBSERVED_ROWS_UPDATED_AT,
    )
    assert result.provenance[0]["rows_updated_at"] == "2026-09-01T14:05:56Z"


# --- C2: unit reverse resolve + condo_key expansion (AS-2) ----------------
def test_c2_unit_reverse_resolve_expands_to_full_set() -> None:
    transport = RoutedTransport(
        {
            f"{UNIT_URL}?unit_bbl=3022642601": TransportResponse(200, UNIT_3022642601_BODY),
            f"{CONDO_URL}?condo_key=301313": TransportResponse(200, CONDO_KEY_301313_BODY),
        }
    )
    result = _call("3022642601", transport)
    assert result.status == STATUS_RESOLVED
    assert result.lot_class == LOT_CLASS_UNIT
    assert result.resolution_path == PATH_UNIT
    # unit sits on base 3022640032; condo_key expansion yields the FULL set.
    assert "3022640032" in result.base_bbls
    assert result.base_bbls == ["3022640032", "3022640033"]
    assert result.condo_key == "301313"
    # two queries: unit lookup then condo_key expansion.
    kinds = [p["query_kind"] for p in result.provenance]
    assert kinds == ["unit_bbl", "condo_key_expansion"]


# --- C3: unit-count split cross-consistency (research 4.3) -----------------
def test_c3_unit_split_matches_resolved_base_lot_set() -> None:
    # research 4.3 grouped response: 14 units on lot 32, 6 on lot 33, total 20
    # (== PLUTO unitstotal). This is a units-side aggregate, not a resolver
    # query; it is used here to cross-check that the resolver's base-lot SET is
    # exactly the set of base lots the units split across (C3 corroborates C1).
    import json

    counts = {
        row["condo_base_bbl"]: int(row["count_unit_bbl"])
        for row in json.loads(C3_UNIT_SPLIT_BODY)
    }
    assert counts == {"3022640032": 14, "3022640033": 6}
    assert sum(counts.values()) == 20
    result = _call("3022647515", _billing_transport())
    assert set(result.base_bbls) == set(counts)


# --- C4/C5 + NOT_A_CONDO: no-match handling (AS-3, AS-4) -------------------
def test_c4_nonexistent_billing_lot_is_unresolved() -> None:
    transport = RoutedTransport(
        {f"{CONDO_URL}?condo_billing_bbl=3022647599": TransportResponse(200, EMPTY_BODY)}
    )
    result = _call("3022647599", transport)
    assert result.status == STATUS_UNRESOLVED
    assert result.resolution_path is None
    assert result.base_bbls == []
    assert result.provenance[0]["record_count"] == 0


def test_c5_land_lot_is_not_a_condo_zero_lookups() -> None:
    # A plain land lot (lot 0032) is classified NOT_A_CONDO before any lookup
    # (research 7 step 1) - the documented rule for a non-condo BBL.
    result = _call("3022640032", _never_called)
    assert result.status == STATUS_NOT_A_CONDO
    assert result.lot_class == LOT_CLASS_NOT_A_CONDO
    assert result.base_bbls == []
    assert result.provenance == []


def test_not_a_condo_low_lot_zero_lookups() -> None:
    result = _call("1000010001", _never_called)  # lot 0001
    assert result.status == STATUS_NOT_A_CONDO
    assert result.provenance == []


# --- C7: BBL string shape (AS-5) ------------------------------------------
def test_c7_returned_base_bbls_match_ten_digit_shape() -> None:
    transport = _billing_transport()
    result = _call("3022647515", transport)
    import re

    assert result.base_bbls
    for base in result.base_bbls:
        assert re.fullmatch(r"\d{10}", base), base


def test_c7_decimal_serialization_rejected_fail_closed() -> None:
    transport = _billing_transport(DRIFT_DECIMAL_BODY)
    with pytest.raises(SchemaDriftError):
        _call("3022647515", transport)


# --- C9: PLUTO appbbl independence (AS-5) ----------------------------------
def test_c9_appbbl_independence() -> None:
    transport = _billing_transport()
    result = _call("3022647515", transport)
    # appbbl returns ONLY lot 32 for this condo (research 6.1); the resolver
    # returns BOTH lots, so it cannot be relying on appbbl.
    assert result.base_bbls == ["3022640032", "3022640033"]
    # And the PLUTO dataset / appbbl field is never requested.
    for url in transport.requested_urls:
        assert "64uk-42ks" not in url
        assert "appbbl" not in url


# --- C10: schema-shape guard ----------------------------------------------
def test_c10_column_inventories_match_research_counts() -> None:
    assert len(CONDO_COLUMNS) == 9  # research 3.2
    assert len(UNIT_COLUMNS) == 16  # research 4.1


def test_c10_fixture_keys_within_declared_columns() -> None:
    import json

    for record in json.loads(BILLING_3022647515_BODY):
        assert set(record) <= CONDO_COLUMNS
    for record in json.loads(UNIT_3022642601_BODY):
        assert set(record) <= UNIT_COLUMNS


# --- C6-class: condo_key fallback mechanism -------------------------------
def test_c6_condo_key_fallback_resolves_full_set() -> None:
    # The condo_key fallback (research 7 step 4a) is the path for the 28 condos
    # with a NULL billing BBL. A byte-faithful raw response for a specific
    # null-billing condo is NOT embedded in the research (only the aggregate
    # count 28), so the fallback MECHANISM is proven here with the real
    # condo_key 301313 response; a null-billing-specific live fixture is
    # deferred in the producer report.
    transport = RoutedTransport(
        {f"{CONDO_URL}?condo_key=301313": TransportResponse(200, CONDO_KEY_301313_BODY)}
    )
    result = resolve_by_condo_key(
        "301313", transport=transport, clock=FIXED_CLOCK, correlation_id=FIXED_CORR
    )
    assert result.status == STATUS_RESOLVED
    assert result.resolution_path == PATH_CONDO_KEY
    assert result.base_bbls == ["3022640032", "3022640033"]
    assert result.condo_key == "301313"


def test_c6_null_billing_condo_resolves_via_condo_key_synthetic() -> None:
    # Null-billing scenario (the 28 condos with a NULL condo_billing_bbl,
    # research 3.4): they cannot be reached by the billing-BBL path and are
    # resolved via condo_key. The fixture is SYNTHETIC and labeled - the
    # research embeds no byte-faithful raw response for a specific null-billing
    # condo, so the OFFICIAL null-billing fixture is a documented source
    # limitation for orchestrator resolution, not fabricated here.
    transport = RoutedTransport(
        {
            f"{CONDO_URL}?condo_key=309999": TransportResponse(
                200, SYNTHETIC_NULL_BILLING_CONDO_KEY_BODY
            )
        }
    )
    result = resolve_by_condo_key(
        "309999", transport=transport, clock=FIXED_CLOCK, correlation_id=FIXED_CORR
    )
    assert result.status == STATUS_RESOLVED
    assert result.resolution_path == PATH_CONDO_KEY
    assert result.base_bbls == ["3099990040", "3099990041"]
    assert result.condo_key == "309999"


def test_condo_key_no_match_is_unresolved() -> None:
    transport = RoutedTransport(
        {f"{CONDO_URL}?condo_key=999999": TransportResponse(200, EMPTY_BODY)}
    )
    result = resolve_by_condo_key(
        "999999", transport=transport, clock=FIXED_CLOCK, correlation_id=FIXED_CORR
    )
    assert result.status == STATUS_UNRESOLVED
    assert result.base_bbls == []


def test_condo_key_invalid_shape_fails_closed() -> None:
    with pytest.raises(BBLValidationError):
        resolve_by_condo_key("abc", transport=_never_called)
    with pytest.raises(BBLValidationError):
        resolve_by_condo_key("30131", transport=_never_called)  # only 5 digits


# --- fail-closed input shapes (AS-4) --------------------------------------
@pytest.mark.parametrize(
    "bad",
    [
        "30226",  # too short
        "3022647515.00000000",  # PLUTO decimal serialization
        "302264751X",  # non-digit
        " 3022647515",  # whitespace
        "0022647515",  # borough 0
    ],
)
def test_malformed_bbl_fails_closed(bad: str) -> None:
    with pytest.raises(BBLValidationError):
        resolve(bad, transport=_never_called)


def test_non_string_bbl_fails_closed() -> None:
    with pytest.raises(BBLValidationError):
        resolve(3022647515, transport=_never_called)  # type: ignore[arg-type]


# --- determinism (same input twice = same output) --------------------------
def test_determinism_same_input_same_output() -> None:
    first = _call("3022647515", _billing_transport())
    second = _call("3022647515", _billing_transport())
    assert first == second


# --- no zoning determination; divergent-zoning boundary carried ------------
def test_resolved_result_carries_divergent_zoning_notice_and_no_zoning() -> None:
    transport = _billing_transport()
    result = _call("3022647515", transport)
    assert result.divergent_zoning_notice == DIVERGENT_ZONING_NOTICE
    # The module makes NO zoning determination: the result exposes no zoning
    # district / overlay / map fields.
    assert not hasattr(result, "zoning_district_1")
    assert not hasattr(result, "zoning_assignment")


def test_module_docstring_states_billing_path_and_boundary() -> None:
    from app.connectors import dtm_condo_soda

    doc = dtm_condo_soda.__doc__ or ""
    assert "billing-BBL" in doc
    assert "qualified-human" in doc


# ===========================================================================
# M5-T044 hardening coverage (DB-029 a, d-i)
# ===========================================================================

# --- (a) G5 F1/F3: hardened ASCII-fullmatch input guard, zero transport calls
@pytest.mark.parametrize(
    "bad",
    [
        "3022647515\n",  # trailing newline (the $ anchor used to accept this)
        "3022647515 ",  # trailing space
        _unicode_digits("3022647515"),  # Unicode (Arabic-Indic) digits
    ],
)
def test_a_bbl_guard_rejects_anchor_leak_no_transport(bad: str) -> None:
    # A guard-failing input raises BBLValidationError BEFORE any I/O; if the
    # transport were reached, _never_called would raise AssertionError instead,
    # so catching BBLValidationError also proves zero transport calls.
    with pytest.raises(BBLValidationError):
        resolve(bad, transport=_never_called)


@pytest.mark.parametrize(
    "bad",
    ["301313\n", "301313 ", _unicode_digits("301313")],
)
def test_a_condo_key_guard_rejects_anchor_leak_no_transport(bad: str) -> None:
    with pytest.raises(BBLValidationError):
        resolve_by_condo_key(bad, transport=_never_called)


def test_a_url_carries_canonical_value() -> None:
    # classify_lot accepts only an exact 10 ASCII-digit string, so the canonical
    # value equals the accepted input; asserting the requested URL carries that
    # value proves normalize_bbl(bbl).canonical (never a raw/other value) is
    # interpolated at the f-string site.
    transport = _billing_transport()
    _call("3022647515", transport)
    assert transport.requested_urls == [
        f"{CONDO_URL}?condo_billing_bbl=3022647515"
    ]


def test_a_unit_and_expansion_urls_carry_canonical_value() -> None:
    transport = RoutedTransport(
        {
            f"{UNIT_URL}?unit_bbl=3022642601": TransportResponse(200, UNIT_3022642601_BODY),
            f"{CONDO_URL}?condo_key=301313": TransportResponse(200, CONDO_KEY_301313_BODY),
        }
    )
    _call("3022642601", transport)
    assert transport.requested_urls == [
        f"{UNIT_URL}?unit_bbl=3022642601",
        f"{CONDO_URL}?condo_key=301313",
    ]


# --- (a) G5 F2 (AS-2): response-side base-BBL guard rejects the leaky shapes
def _billing_body_with_base(base_value: str) -> str:
    return json.dumps(
        [
            {
                "condo_base_bbl": base_value,
                "condo_key": "301313",
                "condo_number": "1313",
                "condo_billing_bbl": "3022647515",
            }
        ]
    )


@pytest.mark.parametrize(
    "base_value",
    [_unicode_digits("3022640032"), "3022640032\n", "3022640032 "],
)
def test_a_response_base_bbl_leaky_shape_rejected(base_value: str) -> None:
    transport = _billing_transport(_billing_body_with_base(base_value))
    with pytest.raises(SchemaDriftError):
        _call("3022647515", transport)


# --- (d) G3 #1: per-query POST-response retrieved_at (AS-3) ------------------
def test_d_two_query_resolve_has_distinct_post_response_timestamps() -> None:
    transport = RoutedTransport(
        {
            f"{UNIT_URL}?unit_bbl=3022642601": TransportResponse(200, UNIT_3022642601_BODY),
            f"{CONDO_URL}?condo_key=301313": TransportResponse(200, CONDO_KEY_301313_BODY),
        }
    )
    clock = _advancing_clock(
        [
            datetime(2026, 9, 18, 12, 0, 0, tzinfo=UTC),  # after the unit query
            datetime(2026, 9, 18, 12, 0, 5, tzinfo=UTC),  # after the expansion
        ]
    )
    result = resolve(
        "3022642601", transport=transport, clock=clock, correlation_id=FIXED_CORR
    )
    stamps = [p["retrieved_at"] for p in result.provenance]
    assert stamps == ["2026-09-18T12:00:00Z", "2026-09-18T12:00:05Z"]
    assert stamps[0] != stamps[1]  # each query stamped after its own response
    # the result-level timestamp reflects the final (most recent) retrieval
    assert result.retrieved_at == "2026-09-18T12:00:05Z"


# --- (e) documented validation code (AS-4) ----------------------------------
def test_e_classify_lot_uses_documented_validation_code() -> None:
    with pytest.raises(BBLValidationError) as excinfo:
        classify_lot("302264751X")
    assert excinfo.value.code == "non_numeric"
    assert excinfo.value.code in DOCUMENTED_BBL_CODES
    assert excinfo.value.code != "wrong_shape"  # the retired ad-hoc code is gone


# --- (f) honest input identity on condo_key results (AS-4) ------------------
def test_f_condo_key_result_carries_honest_input_identity() -> None:
    transport = RoutedTransport(
        {f"{CONDO_URL}?condo_key=301313": TransportResponse(200, CONDO_KEY_301313_BODY)}
    )
    result = resolve_by_condo_key(
        "301313", transport=transport, clock=FIXED_CLOCK, correlation_id=FIXED_CORR
    )
    assert result.input_kind == INPUT_KIND_CONDO_KEY
    assert result.input_value == "301313"
    assert result.lot_class is None  # a condo_key has no lot number


def test_f_condo_key_unresolved_result_also_has_honest_identity() -> None:
    transport = RoutedTransport(
        {f"{CONDO_URL}?condo_key=999999": TransportResponse(200, EMPTY_BODY)}
    )
    result = resolve_by_condo_key(
        "999999", transport=transport, clock=FIXED_CLOCK, correlation_id=FIXED_CORR
    )
    assert result.status == STATUS_UNRESOLVED
    assert result.input_kind == INPUT_KIND_CONDO_KEY
    assert result.input_value == "999999"
    assert result.lot_class is None


def test_f_bbl_result_carries_bbl_input_identity() -> None:
    result = _call("3022647515", _billing_transport())
    assert result.input_kind == INPUT_KIND_BBL
    assert result.input_value == "3022647515"
    assert result.lot_class == LOT_CLASS_BILLING


# --- (g) dtm-local error branches (AS-5) ------------------------------------
_ERR_KW = {"sleep": lambda _delay: None, "clock": FIXED_CLOCK, "correlation_id": FIXED_CORR}


def test_g_400_schema_drift_is_typed() -> None:
    transport = _AlwaysTransport(
        TransportResponse(400, '{"errorCode":"query.soql.no-such-column"}')
    )
    with pytest.raises(SchemaDriftError):
        resolve("3022647515", transport=transport, **_ERR_KW)


def test_g_400_other_is_source_unavailable() -> None:
    transport = _AlwaysTransport(
        TransportResponse(400, '{"errorCode":"query.soql.malformed"}')
    )
    with pytest.raises(SourceUnavailableError):
        resolve("3022647515", transport=transport, **_ERR_KW)


def test_g_non_json_body_is_schema_drift() -> None:
    transport = _AlwaysTransport(TransportResponse(200, "this is not json"))
    with pytest.raises(SchemaDriftError):
        resolve("3022647515", transport=transport, **_ERR_KW)


def test_g_non_array_body_is_schema_drift() -> None:
    transport = _AlwaysTransport(TransportResponse(200, "{}"))
    with pytest.raises(SchemaDriftError):
        resolve("3022647515", transport=transport, **_ERR_KW)


def test_g_non_object_record_is_schema_drift() -> None:
    transport = _AlwaysTransport(TransportResponse(200, "[1, 2, 3]"))
    with pytest.raises(SchemaDriftError):
        resolve("3022647515", transport=transport, **_ERR_KW)


def test_g_rate_limited_terminal() -> None:
    transport = _AlwaysTransport(TransportResponse(429, "{}"))
    with pytest.raises(RateLimitedError):
        resolve(
            "3022647515", transport=transport, max_attempts=2, backoff_base=0.0, **_ERR_KW
        )
    assert transport.calls >= 2  # the bounded retry budget was actually spent


def test_g_timeout_terminal() -> None:
    transport = _AlwaysTransport(exc=TransportTimeout("read timed out"))
    with pytest.raises(SourceTimeoutError):
        resolve(
            "3022647515", transport=transport, max_attempts=2, backoff_base=0.0, **_ERR_KW
        )


def test_g_network_failure_is_source_unavailable() -> None:
    transport = _AlwaysTransport(exc=TransportFailure("dns failure"))
    with pytest.raises(SourceUnavailableError):
        resolve(
            "3022647515", transport=transport, max_attempts=2, backoff_base=0.0, **_ERR_KW
        )


# --- (h) unit-path branches (AS-6) ------------------------------------------
def test_h_unit_empty_is_unresolved_single_query() -> None:
    transport = RoutedTransport(
        {f"{UNIT_URL}?unit_bbl=3022642601": TransportResponse(200, EMPTY_BODY)}
    )
    result = _call("3022642601", transport)
    assert result.status == STATUS_UNRESOLVED
    assert result.base_bbls == []
    assert [p["query_kind"] for p in result.provenance] == ["unit_bbl"]


def test_h_unit_without_condo_key_returns_direct_lot_no_expansion() -> None:
    # A unit row with a base lot but NO condo_key: the resolver returns the
    # direct base lot, issues NO expansion query (RoutedTransport would raise on
    # the unrouted condo_key URL), and surfaces the incompleteness note.
    body = json.dumps(
        [
            {
                "condo_base_bbl": "3022640032",
                "unit_bbl": "3022642601",
                "unit_designation": "1A",
            }
        ]
    )
    transport = RoutedTransport(
        {f"{UNIT_URL}?unit_bbl=3022642601": TransportResponse(200, body)}
    )
    result = _call("3022642601", transport)
    assert result.status == STATUS_RESOLVED
    assert result.base_bbls == ["3022640032"]
    assert result.condo_key is None
    assert [p["query_kind"] for p in result.provenance] == ["unit_bbl"]
    assert any("without condo_key expansion" in note for note in result.notes)


# --- (i) runtime drift-note paths (AS-6) ------------------------------------
def test_i_unknown_columns_note_is_recorded() -> None:
    body = json.dumps(
        [
            {
                "condo_base_bbl": "3022640032",
                "condo_key": "301313",
                "condo_number": "1313",
                "surprise_column": "x",
            }
        ]
    )
    result = _call("3022647515", _billing_transport(body))
    assert result.status == STATUS_RESOLVED
    assert any(note.startswith("unknown_columns:surprise_column") for note in result.notes)


def test_i_multiple_condo_keys_and_numbers_notes() -> None:
    body = json.dumps(
        [
            {"condo_base_bbl": "3022640032", "condo_key": "301313", "condo_number": "1313"},
            {"condo_base_bbl": "3022640033", "condo_key": "301314", "condo_number": "1314"},
        ]
    )
    result = _call("3022647515", _billing_transport(body))
    assert result.status == STATUS_RESOLVED
    assert set(result.base_bbls) == {"3022640032", "3022640033"}
    assert any(note.startswith("multiple_condo_keys:") for note in result.notes)
    assert any(note.startswith("multiple_condo_numbers:") for note in result.notes)
    # ambiguous identifiers are surfaced, never guessed into a single value
    assert result.condo_key is None
    assert result.condo_number is None


# --- [ORCH-CORRECTED per M5-T044-G3 F1] resolve_by_condo_key post-response stamp
def test_f1_correction_condo_key_stamp_is_post_response() -> None:
    """The direct condo_key path stamps retrieved_at AFTER its successful fetch
    (mirroring resolve(); the pluto post-response precedent). The clock supplies
    exactly one post-fetch moment; a pre-fetch stamp would consume the moment
    before the transport ran and a second clock call would StopIteration."""
    calls: list[str] = []

    def transport(url, headers, timeout):
        calls.append(url)
        return TransportResponse(200, CONDO_KEY_301313_BODY)

    moments = iter([datetime(2026, 9, 18, 12, 0, 7, tzinfo=UTC)])

    def clock():
        # the transport MUST have been called before the stamp is taken
        assert calls, "retrieved_at was stamped before the fetch ran"
        return next(moments)

    result = resolve_by_condo_key(
        "301313", transport=transport, clock=clock, correlation_id=FIXED_CORR
    )
    assert result.status == STATUS_RESOLVED
    assert result.retrieved_at == "2026-09-18T12:00:07Z"
    assert [p["retrieved_at"] for p in result.provenance] == ["2026-09-18T12:00:07Z"]
