"""Exhaustive offline tests for the pure DCM Streetwidth free-text classifier
(task M4-T015). No network, no fixtures needed - this module is a pure
function over strings."""

from __future__ import annotations

import pytest

from app.connectors.dcm_street_width_classifier import (
    AMBIGUITY_CLASS_DISPOSITIONS,
    DISPOSITION_NARROW_FAIL_CLOSED,
    DISPOSITION_WIDE,
    WIDE_THRESHOLD_FT,
    classify_street_width,
)


def test_wide_threshold_is_75() -> None:
    assert WIDE_THRESHOLD_FT == 75.0


# ---------------------------------------------------------------------------
# Wide-qualifying classes (mathematical entailment >= 75 ft)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    ["75", "80", "100", "75.0", "150", "166", "192"],
)
def test_clean_numeric_ge_75_is_wide(raw: str) -> None:
    result = classify_street_width(raw)
    assert result.disposition == DISPOSITION_WIDE
    assert result.ambiguity_class == "clean_numeric_ge_75"
    assert result.review_required is False
    assert result.raw_text == raw


@pytest.mark.parametrize("raw", ["75-90", "75-100", "166-192", "80-90"])
def test_range_both_endpoints_ge_75_is_wide(raw: str) -> None:
    result = classify_street_width(raw)
    assert result.disposition == DISPOSITION_WIDE
    assert result.ambiguity_class == "range_both_endpoints_ge_75"
    assert result.review_required is False


@pytest.mark.parametrize("raw", [">75", ">80", ">100", ">=75", ">=80"])
def test_gt_inequality_ge_75_is_wide(raw: str) -> None:
    result = classify_street_width(raw)
    assert result.disposition == DISPOSITION_WIDE
    assert result.ambiguity_class == "gt_inequality_ge_75"
    assert result.review_required is False


# ---------------------------------------------------------------------------
# Confidently-narrow classes (no ambiguity to review)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", ["60", "30", "49.5", "66.05", "0", "74.99"])
def test_clean_numeric_lt_75_is_confident_narrow(raw: str) -> None:
    result = classify_street_width(raw)
    assert result.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert result.ambiguity_class == "clean_numeric_lt_75"
    assert result.review_required is False


@pytest.mark.parametrize("raw", ["50-60", "30-40", "10-74.9"])
def test_range_both_endpoints_lt_75_is_confident_narrow(raw: str) -> None:
    result = classify_street_width(raw)
    assert result.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert result.ambiguity_class == "range_both_endpoints_lt_75"
    assert result.review_required is False


@pytest.mark.parametrize("raw", ["<60", "<50", "<75", "<=74", "<=0"])
def test_lt_or_le_inequality_confident_narrow(raw: str) -> None:
    result = classify_street_width(raw)
    assert result.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert result.review_required is False
    assert result.ambiguity_class in (
        "lt_inequality_at_or_below_75_confident_narrow",
        "le_inequality_below_75_confident_narrow",
    )


# ---------------------------------------------------------------------------
# Ambiguous classes: fail closed to narrow WITH a review flag
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_class",
    [
        ("60-75", "range_straddles_cutoff"),
        ("74-75.3", "range_straddles_cutoff"),
        (">60", "gt_inequality_below_75_ambiguous"),
        (">50", "gt_inequality_below_75_ambiguous"),
        ("<80", "lt_inequality_above_75_ambiguous"),
        ("<=75", "le_inequality_at_or_above_75_ambiguous"),
        ("<=80", "le_inequality_at_or_above_75_ambiguous"),
        ("~60", "approximate_or_hedged_value_ambiguous"),
        ("~80", "approximate_or_hedged_value_ambiguous"),
        ("Around 100", "approximate_or_hedged_value_ambiguous"),
        ("More or less 40", "approximate_or_hedged_value_ambiguous"),
        ("Probably between 80 - 90", "approximate_or_hedged_value_ambiguous"),
        ("approx 80", "approximate_or_hedged_value_ambiguous"),
        ("Width Irregular", "width_irregular"),
        ("width irregular", "width_irregular"),
        ("varies", "varies"),
        ("Varies", "varies"),
        ("n/a", "not_applicable_n_a"),
        ("N/A", "not_applicable_n_a"),
        ("Unknown", "unknown_no_qualifier"),
        ("unknown", "unknown_no_qualifier"),
        ("Unknown but <75", "unknown_hedged_below_75"),
        ("Unknown but >75", "unknown_hedged_above_75"),
        ("Regular but unknown.", "regular_but_unknown"),
        ("Regular but unknown", "regular_but_unknown"),
        ("gibberish free text", "unrecognized_free_text_ambiguous"),
        ("100-90", "range_order_unexpected"),
        ("-10", "negative_value_unexpected"),
        ("-10-20", "negative_value_unexpected"),
        (">-5", "negative_value_unexpected"),
    ],
)
def test_ambiguous_classes_fail_closed_with_review(raw: str, expected_class: str) -> None:
    result = classify_street_width(raw)
    assert result.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert result.ambiguity_class == expected_class
    assert result.review_required is True


# ---------------------------------------------------------------------------
# Missing / malformed input
# ---------------------------------------------------------------------------


def test_none_is_empty_or_missing() -> None:
    result = classify_street_width(None)
    assert result.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert result.ambiguity_class == "empty_or_missing"
    assert result.review_required is True
    assert result.raw_text is None


@pytest.mark.parametrize("raw", ["", "   "])
def test_empty_string_is_empty_or_missing(raw: str) -> None:
    result = classify_street_width(raw)
    assert result.ambiguity_class == "empty_or_missing"
    assert result.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert result.review_required is True


@pytest.mark.parametrize("raw", [75, 80.0, True, ["75"], {"value": "75"}])
def test_non_string_type_is_unexpected_type(raw: object) -> None:
    result = classify_street_width(raw)
    assert result.ambiguity_class == "unexpected_type"
    assert result.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert result.review_required is True


# ---------------------------------------------------------------------------
# Never raises
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [None, "", "   ", 75, object(), "~~~", "1-2-3", ">", "<", "-", "n / a"],
)
def test_classify_never_raises(raw: object) -> None:
    result = classify_street_width(raw)
    assert result.disposition in (DISPOSITION_WIDE, DISPOSITION_NARROW_FAIL_CLOSED)


# ---------------------------------------------------------------------------
# Exhaustiveness: every class in the documented disposition table is
# actually reachable, and the table is the single source of truth used by
# the producer report's class -> disposition summary.
# ---------------------------------------------------------------------------


def test_disposition_table_is_internally_consistent() -> None:
    classes = [row[0] for row in AMBIGUITY_CLASS_DISPOSITIONS]
    assert len(classes) == len(set(classes)), "duplicate class in the disposition table"
    for _ambiguity_class, disposition, _review in AMBIGUITY_CLASS_DISPOSITIONS:
        assert disposition in (DISPOSITION_WIDE, DISPOSITION_NARROW_FAIL_CLOSED)


_REACHED_BY_ABOVE_TESTS = {
    "clean_numeric_ge_75",
    "clean_numeric_lt_75",
    "range_both_endpoints_ge_75",
    "range_both_endpoints_lt_75",
    "range_straddles_cutoff",
    "range_order_unexpected",
    "gt_inequality_ge_75",
    "gt_inequality_below_75_ambiguous",
    "lt_inequality_at_or_below_75_confident_narrow",
    "lt_inequality_above_75_ambiguous",
    "le_inequality_below_75_confident_narrow",
    "le_inequality_at_or_above_75_ambiguous",
    "approximate_or_hedged_value_ambiguous",
    "width_irregular",
    "varies",
    "not_applicable_n_a",
    "unknown_no_qualifier",
    "unknown_hedged_below_75",
    "unknown_hedged_above_75",
    "regular_but_unknown",
    "empty_or_missing",
    "unexpected_type",
    "negative_value_unexpected",
    "unrecognized_free_text_ambiguous",
}


def test_every_documented_class_is_exercised_by_this_suite() -> None:
    documented = {row[0] for row in AMBIGUITY_CLASS_DISPOSITIONS}
    assert documented == _REACHED_BY_ABOVE_TESTS, (
        "the documented class table and this test suite's exercised classes "
        "have drifted apart - keep them in lockstep"
    )
