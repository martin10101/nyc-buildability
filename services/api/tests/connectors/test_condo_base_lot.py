"""Offline suite for the condo billing-BBL -> base-lot SEAM POLICY (M5-T045).

The seam (:mod:`app.connectors.condo_base_lot`) classifies an input BBL and, for
a condo BILLING BBL, invokes the accepted resolver and collapses its result into
one typed, fail-closed outcome. These tests inject a resolver DOUBLE (or a
URL-routed fake transport into the real resolver) so no network I/O ever
happens; the classification / pass-through branches assert the resolver is never
called at all.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from app.connectors.condo_base_lot import (
    OUTCOME_ERROR,
    OUTCOME_MULTI_LOT,
    OUTCOME_NOT_CONDO_BILLING,
    OUTCOME_RESOLVED_SINGLE,
    OUTCOME_UNRESOLVED,
    CondoResolution,
    resolve_condo_billing,
)
from app.connectors.dtm_condo_soda import (
    CONDO_DATASET_ID,
    DIVERGENT_ZONING_NOTICE,
    SOURCE_ID,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
    CondoBaseLotResult,
    RateLimitedError,
    SchemaDriftError,
    resolve,
)
from app.resilience.transport import TransportResponse

FIXED_CLOCK = lambda: datetime(2026, 9, 18, 12, 0, 0, tzinfo=UTC)  # noqa: E731
CID = "cid-condo-seam-test"
CONDO_URL = f"https://data.cityofnewyork.us/resource/{CONDO_DATASET_ID}.json"

# Billing resolve of 3022647515 -> TWO base lots (DB-002 §3.3).
BILLING_MULTI_BODY = (
    '[{"condo_base_bbl":"3022640032","condo_key":"301313","condo_number":"1313",'
    '"condo_billing_bbl":"3022647515"},'
    '{"condo_base_bbl":"3022640033","condo_key":"301313","condo_number":"1313",'
    '"condo_billing_bbl":"3022647515"}]'
)
# Real null-billing condo 103343 resolved by its billing lot would be empty, but
# a single-base-lot billing condo shape (one row) drives the resolved-single
# branch. condo_key/number present, single base lot.
BILLING_SINGLE_BODY = (
    '[{"condo_base_bbl":"1003030019","condo_key":"103343","condo_number":"3343",'
    '"condo_name":"THE 128 HESTER STREET CONDO","condo_billing_bbl":"1010037501"}]'
)
EMPTY_BODY = "[]"


class _RoutedTransport:
    def __init__(self, routes: dict[str, TransportResponse]):
        self.routes = routes
        self.requested_urls: list[str] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.requested_urls.append(url)
        if url not in self.routes:
            raise AssertionError(f"unexpected URL requested: {url}")
        return self.routes[url]


def _resolver_double(result: CondoBaseLotResult):
    """A resolver stub that returns a fixed result and records its call."""
    calls: list[tuple] = []

    def _resolver(bbl: str, *, correlation_id: str, **kwargs):
        calls.append((bbl, correlation_id))
        return result

    _resolver.calls = calls  # type: ignore[attr-defined]
    return _resolver


def _never_resolver(bbl: str, *, correlation_id: str, **kwargs):
    raise AssertionError(f"resolver must not be called; got {bbl}")


# --- pass-through (not condo-billing): zero resolver/network I/O -------------
@pytest.mark.parametrize(
    "bbl",
    [
        "3022640032",  # a plain land lot (lot 0032)
        "1000010001",  # lot 0001
        "3022642601",  # a UNIT lot (2601) -> pass-through in this seam
    ],
)
def test_non_billing_bbl_is_pass_through_zero_lookups(bbl: str) -> None:
    res = resolve_condo_billing(bbl, correlation_id=CID, resolver=_never_resolver)
    assert res.outcome == OUTCOME_NOT_CONDO_BILLING
    assert res.is_pass_through is True
    assert res.substitutes_base_lot is False
    assert res.is_fail_safe is False
    assert res.input_bbl == bbl
    assert res.base_bbls == ()
    assert res.provenance == ()


def test_malformed_bbl_is_pass_through_not_error() -> None:
    # A malformed BBL is not our class; the seam passes through (byte-identical
    # prior behavior for the consumer) with zero lookups, never raising.
    res = resolve_condo_billing("30226", correlation_id=CID, resolver=_never_resolver)
    assert res.outcome == OUTCOME_NOT_CONDO_BILLING
    assert res.is_pass_through is True


# --- resolved single base lot ----------------------------------------------
def test_resolved_single_exposes_the_base_lot_and_provenance() -> None:
    transport = _RoutedTransport(
        {
            f"{CONDO_URL}?condo_billing_bbl=1010037501": TransportResponse(
                200, BILLING_SINGLE_BODY
            )
        }
    )
    res = resolve_condo_billing(
        "1010037501",
        correlation_id=CID,
        resolver=resolve,
        transport=transport,
        clock=FIXED_CLOCK,
    )
    assert res.outcome == OUTCOME_RESOLVED_SINGLE
    assert res.substitutes_base_lot is True
    assert res.is_fail_safe is False
    assert res.resolved_base_bbl == "1003030019"
    assert res.base_bbls == ("1003030019",)
    assert res.condo_key == "103343"
    assert res.condo_number == "3343"
    assert res.source_id == SOURCE_ID
    assert res.dataset_ids == (CONDO_DATASET_ID,)
    assert res.retrieved_at == "2026-09-18T12:00:00Z"
    assert res.divergent_zoning_notice == DIVERGENT_ZONING_NOTICE
    assert len(res.provenance) == 1


# --- multi-lot set: never a single substrate --------------------------------
def test_multi_lot_exposes_all_base_lots_and_no_single_substrate() -> None:
    transport = _RoutedTransport(
        {
            f"{CONDO_URL}?condo_billing_bbl=3022647515": TransportResponse(
                200, BILLING_MULTI_BODY
            )
        }
    )
    res = resolve_condo_billing(
        "3022647515",
        correlation_id=CID,
        resolver=resolve,
        transport=transport,
        clock=FIXED_CLOCK,
    )
    assert res.outcome == OUTCOME_MULTI_LOT
    assert res.substitutes_base_lot is False
    assert res.is_fail_safe is True
    # The FULL set is exposed, sorted, never collapsed; no single substitute lot.
    assert res.base_bbls == ("3022640032", "3022640033")
    assert res.resolved_base_bbl is None
    assert res.divergent_zoning_notice == DIVERGENT_ZONING_NOTICE


# --- unresolved: honest no-result -------------------------------------------
def test_unresolved_billing_bbl_fails_safe() -> None:
    transport = _RoutedTransport(
        {
            f"{CONDO_URL}?condo_billing_bbl=3022647599": TransportResponse(
                200, EMPTY_BODY
            )
        }
    )
    res = resolve_condo_billing(
        "3022647599",
        correlation_id=CID,
        resolver=resolve,
        transport=transport,
        clock=FIXED_CLOCK,
    )
    assert res.outcome == OUTCOME_UNRESOLVED
    assert res.is_fail_safe is True
    assert res.resolved_base_bbl is None
    assert res.base_bbls == ()


# --- typed transport error -> fail-safe OUTCOME_ERROR -----------------------
def test_transport_error_maps_to_typed_error_outcome() -> None:
    def _raising_resolver(bbl: str, *, correlation_id: str, **kwargs):
        raise RateLimitedError("throttled", correlation_id=correlation_id)

    res = resolve_condo_billing(
        "3022647515", correlation_id=CID, resolver=_raising_resolver
    )
    assert res.outcome == OUTCOME_ERROR
    assert res.is_fail_safe is True
    assert res.error_type == "rate_limited"
    assert res.resolved_base_bbl is None
    assert res.source_id == SOURCE_ID


def test_schema_drift_error_is_typed_error_outcome() -> None:
    def _raising_resolver(bbl: str, *, correlation_id: str, **kwargs):
        raise SchemaDriftError("drift", correlation_id=correlation_id)

    res = resolve_condo_billing(
        "3022647515", correlation_id=CID, resolver=_raising_resolver
    )
    assert res.outcome == OUTCOME_ERROR
    assert res.error_type == "schema_drift"


# --- mapping is driven purely by the resolver result (double) ---------------
def test_resolved_double_single_maps_to_resolved_single() -> None:
    double = _resolver_double(
        CondoBaseLotResult(
            status=STATUS_RESOLVED,
            input_value="3022647515",
            lot_class="billing",
            correlation_id=CID,
            retrieved_at="2026-09-18T12:00:00Z",
            resolution_path="billing",
            base_bbls=["3099990040"],
            condo_key="309999",
            condo_number="9999",
            provenance=[{"dataset_id": CONDO_DATASET_ID, "query_kind": "condo_billing_bbl"}],
        )
    )
    res = resolve_condo_billing("3022647515", correlation_id=CID, resolver=double)
    assert res.outcome == OUTCOME_RESOLVED_SINGLE
    assert res.resolved_base_bbl == "3099990040"
    assert double.calls == [("3022647515", CID)]  # type: ignore[attr-defined]


def test_resolved_double_unresolved_maps_to_unresolved() -> None:
    double = _resolver_double(
        CondoBaseLotResult(
            status=STATUS_UNRESOLVED,
            input_value="3022647599",
            lot_class="billing",
            correlation_id=CID,
            retrieved_at="2026-09-18T12:00:00Z",
        )
    )
    res = resolve_condo_billing("3022647599", correlation_id=CID, resolver=double)
    assert res.outcome == OUTCOME_UNRESOLVED
    assert res.is_fail_safe is True


def test_outcome_is_frozen() -> None:
    res = CondoResolution(
        outcome=OUTCOME_NOT_CONDO_BILLING, input_bbl="x", correlation_id=CID
    )
    with pytest.raises(FrozenInstanceError):
        res.outcome = OUTCOME_ERROR  # type: ignore[misc]
