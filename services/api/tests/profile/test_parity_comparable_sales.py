"""Disclosed comparable-sales selection (queue item B-11; plan section 11b). Offline: the
candidate rows are replayed from the recorded Bayside fixture through the connector; the
filter is pure. Never a valuation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.connectors.dof_sales_soda import (
    SaleRecord,
    build_by_bbl_url,
    build_candidates_url,
    fetch_comparable_candidates,
    fetch_sales_by_bbl,
)
from app.profile.parity.comparable_sales import (
    NOT_A_VALUATION_NOTICE,
    REASON_NO_SIZE,
    REASON_SELF,
    REASON_SIZE_OUT_OF_RANGE,
    REASON_TYPE_MISMATCH,
    REASON_ZERO_PRICE,
    SelectionCriteria,
    SubjectSpec,
    select_comparables,
    subject_spec_from_record,
)
from app.resilience.transport import TransportResponse

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "dof_sales_bayside"
SUBJECT_URL = build_by_bbl_url("4073340070", row_limit=50)
CANDIDATES_URL = build_candidates_url("BAYSIDE", "22 STORE BUILDINGS", row_limit=12)
FIXED_CLOCK = lambda: datetime(2026, 10, 2, 11, 0, 0, tzinfo=UTC)  # noqa: E731


def _routed(url: str, file: str):
    body = (PACK / file).read_text(encoding="utf-8")
    response = TransportResponse(200, body, {"x-soda2-truth-last-modified": "x"})

    def transport(requested: str, headers: dict, timeout: float) -> TransportResponse:
        assert requested == url
        return response

    return transport


def _subject_record() -> SaleRecord:
    result = fetch_sales_by_bbl(
        "4073340070",
        transport=_routed(SUBJECT_URL, "dof_sales_w2pb-icbu_bbl_4073340070.json"),
        row_limit=50, clock=FIXED_CLOCK, correlation_id="c",
    )
    return result.records[0]


def _candidates():
    result = fetch_comparable_candidates(
        "BAYSIDE", "22 STORE BUILDINGS",
        transport=_routed(CANDIDATES_URL, "dof_sales_w2pb-icbu_bayside_22_store_buildings.json"),
        row_limit=12, clock=FIXED_CLOCK, correlation_id="c",
    )
    return result.records, result.provenance


def _rec(**overrides) -> SaleRecord:
    base = dict(
        bbl="4000000001", borough="4", neighborhood="BAYSIDE", block="1", lot="1",
        address="1 TEST ST", zip_code="11361", building_class_category="22 STORE BUILDINGS",
        building_class_at_time_of_sale="K1", residential_units=0, commercial_units=1,
        total_units=1, year_built=1960, land_square_feet=5000, gross_square_feet=5000,
        sale_price=1_000_000, sale_date="2025-01-01", source={}, raw={},
    )
    base.update(overrides)
    return SaleRecord(**base)


def test_default_filter_selects_cash_same_type_in_size_band():
    subject = subject_spec_from_record(_subject_record())  # 22 STORE BUILDINGS, gsf 5091
    records, source = _candidates()
    result = select_comparables(subject, records, source=source)

    # Subject gsf 5,091 -> +/-50% band [2545.5, 7636.5]. From the 12 recorded rows:
    # 4 cash sales of the same category fall in the band.
    assert len(result.selected) == 4
    low, high = result.criteria.size_bounds(5091)
    for row in result.selected:
        assert row.is_cash_sale
        assert row.building_class_category == "22 STORE BUILDINGS"
        assert low <= row.gross_square_feet <= high

    reasons = [e["reason"] for e in result.excluded]
    assert reasons.count(REASON_ZERO_PRICE) == 6
    assert reasons.count(REASON_SIZE_OUT_OF_RANGE) == 2
    assert reasons.count(REASON_TYPE_MISMATCH) == 0
    assert len(result.selected) + len(result.excluded) == 12


def test_result_is_not_a_valuation_and_discloses_criteria():
    subject = subject_spec_from_record(_subject_record())
    records, source = _candidates()
    result = select_comparables(subject, records, source=source)
    assert result.not_a_valuation == NOT_A_VALUATION_NOTICE
    assert "+/-50%" in result.criteria_text
    assert "5,091 sq ft" in result.criteria_text
    assert "22 STORE BUILDINGS" in result.criteria_text
    # Data only: the result carries no average / price-per-sqft / estimate field.
    assert not hasattr(result, "average_price")
    assert not hasattr(result, "price_per_sq_ft")
    assert result.source["source_id"] == "nyc-dof-annualized-sales-soda"


def test_subject_lot_is_excluded_from_its_own_comparables():
    subject = SubjectSpec(bbl="4000000001", building_class_category="22 STORE BUILDINGS",
                          gross_square_feet=5000)
    result = select_comparables(subject, [_rec(bbl="4000000001"), _rec(bbl="4000000002")])
    assert len(result.selected) == 1
    assert result.selected[0].bbl == "4000000002"
    assert [e["reason"] for e in result.excluded] == [REASON_SELF]


def test_different_category_is_excluded_as_type_mismatch():
    subject = SubjectSpec(bbl="4000000001", building_class_category="22 STORE BUILDINGS",
                          gross_square_feet=5000)
    other = _rec(bbl="4000000003", building_class_category="01 ONE FAMILY DWELLINGS")
    result = select_comparables(subject, [other])
    assert result.selected == ()
    assert [e["reason"] for e in result.excluded] == [REASON_TYPE_MISMATCH]


def test_cash_row_with_no_recorded_size_is_excluded_as_no_size():
    subject = SubjectSpec(bbl="4000000001", building_class_category="22 STORE BUILDINGS",
                          gross_square_feet=5000)
    no_size = _rec(bbl="4000000004", gross_square_feet=0)  # recorded 0 = size not recorded
    result = select_comparables(subject, [no_size])
    assert result.selected == ()
    assert [e["reason"] for e in result.excluded] == [REASON_NO_SIZE]


def test_subject_without_recorded_size_skips_the_size_match():
    subject = SubjectSpec(bbl="4000000001", building_class_category="22 STORE BUILDINGS",
                          gross_square_feet=None)
    big = _rec(bbl="4000000005", gross_square_feet=200_000)  # would be out of any band
    result = select_comparables(subject, [big])
    assert result.selected == (big,)
    assert "no size match could be applied" in result.criteria_text


def test_tolerance_is_configurable():
    subject = SubjectSpec(bbl="4000000001", building_class_category="22 STORE BUILDINGS",
                          gross_square_feet=5000)
    near = _rec(bbl="4000000006", gross_square_feet=5400)  # +8%
    tight = SelectionCriteria(size_tolerance_fraction=0.05)  # +/-5% -> excludes +8%
    result = select_comparables(subject, [near], criteria=tight)
    assert [e["reason"] for e in result.excluded] == [REASON_SIZE_OUT_OF_RANGE]
