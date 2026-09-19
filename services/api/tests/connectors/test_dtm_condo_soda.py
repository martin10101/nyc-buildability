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

from datetime import UTC, datetime

import pytest

from app.connectors.bbl import BBLValidationError
from app.connectors.dtm_condo_soda import (
    APP_TOKEN_ENV_VAR,
    CONDO_COLUMNS,
    CONDO_DATASET_ID,
    DIVERGENT_ZONING_NOTICE,
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
    SchemaDriftError,
    classify_lot,
    resolve,
    resolve_by_condo_key,
)
from app.resilience.transport import TransportResponse

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
