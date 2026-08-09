"""Deterministic tests for the SB-S3 metadata consistency checks (M2-T015, part 3).

Covers, per check: one PASS with exact expected computed values, one FAIL with exact
expected computed values (verbatim conflicting values), and every UNEVALUABLE refusal
condition — plus the unified package surface: all eight SB-S3 deterministic checks
importable from ``app.documents.checks``.
"""

from __future__ import annotations

import app.documents.checks as checks_package
from app.documents.checks import (
    CheckFailed,
    CheckPassed,
    CheckUnevaluable,
    address_bbl_match,
    elevation_consistency,
    north_orientation_consistency,
    scale_consistency,
)
from app.documents.taxonomy import SurveyFactType
from app.documents.units import (
    AngleUnit,
    ElevationUnit,
    ValidatedBearing,
    ValidatedElevation,
    ValidatedScale,
    ValidatedUnitlessText,
)

# ------------------------------------------------------------- typed-input builders


def _scale(ratio: str) -> ValidatedScale:
    return ValidatedScale(
        fact_type=SurveyFactType.SCALE_STATEMENT,
        ratio=ratio,
        ratio_denominator=int(ratio.partition(":")[2]),
    )


def _orientation(value: int | float) -> ValidatedBearing:
    return ValidatedBearing(
        fact_type=SurveyFactType.NORTH_ARROW_ORIENTATION,
        value=value,
        unit=AngleUnit.DEGREES,
    )


def _elevation(value: int | float) -> ValidatedElevation:
    return ValidatedElevation(
        fact_type=SurveyFactType.ELEVATION_VALUE,
        value=value,
        unit=ElevationUnit.FEET,
    )


def _address(text: str) -> ValidatedUnitlessText:
    return ValidatedUnitlessText(fact_type=SurveyFactType.ADDRESS_TEXT, text=text)


def _bbl(text: str) -> ValidatedUnitlessText:
    return ValidatedUnitlessText(fact_type=SurveyFactType.BBL_TEXT, text=text)


# ------------------------------------------------------------------ scale_consistency


def test_scale_consistency_passes_on_a_single_unique_ratio():
    result = scale_consistency([_scale("1:240"), _scale("1:240")])
    assert isinstance(result, CheckPassed)
    assert result.check_name == "scale_consistency"
    assert result.unit is None
    assert result.tolerance == 0
    assert result.computed == {
        "statement_count": 2,
        "distinct_ratio_count": 1,
        "ratio[1:240]": 2,
    }


def test_scale_consistency_fails_naming_every_conflicting_ratio_verbatim():
    result = scale_consistency([_scale("1:240"), _scale("1:600"), _scale("1:240")])
    assert isinstance(result, CheckFailed)
    assert result.check_name == "scale_consistency"
    assert result.unit is None
    assert result.tolerance == 0
    assert result.computed == {
        "statement_count": 3,
        "distinct_ratio_count": 2,
        "ratio[1:240]": 2,
        "ratio[1:600]": 1,
    }


def test_scale_consistency_unevaluable_on_empty_input():
    result = scale_consistency([])
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "scale_consistency"
    assert "empty" in result.reason


def test_scale_consistency_unevaluable_on_a_non_resolved_value():
    result = scale_consistency([_scale("1:240"), "1:240"])
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "scale_consistency"
    assert "scales[1] must be a resolved ValidatedScale" in result.reason
    assert "str" in result.reason


# ------------------------------------------------- north_orientation_consistency


def test_north_orientation_consistency_passes_across_the_zero_wrap():
    # 359.75 vs 0.25 differ by 0.5 on the circle (never 359.5).
    result = north_orientation_consistency(
        [_orientation(359.75), _orientation(0.25)], tolerance=0.5
    )
    assert isinstance(result, CheckPassed)
    assert result.check_name == "north_orientation_consistency"
    assert result.unit == "degrees"
    assert result.tolerance == 0.5
    assert result.computed == {
        "statement_count": 2,
        "stated_first": 359.75,
        "max_angular_difference": 0.5,
    }


def test_north_orientation_consistency_fails_naming_conflicts_verbatim():
    result = north_orientation_consistency(
        [_orientation(10.0), _orientation(350.0)], tolerance=5.0
    )
    assert isinstance(result, CheckFailed)
    assert result.check_name == "north_orientation_consistency"
    assert result.unit == "degrees"
    assert result.tolerance == 5.0
    assert result.computed == {
        "statement_count": 2,
        "stated_first": 10.0,
        "max_angular_difference": 20.0,
        "statement[1]": 350.0,
        "statement[1].angular_difference": 20.0,
    }


def test_north_orientation_consistency_unevaluable_on_empty_input():
    result = north_orientation_consistency([], tolerance=0.5)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "north_orientation_consistency"
    assert "empty" in result.reason


def test_north_orientation_consistency_unevaluable_on_mixed_unresolved_input():
    result = north_orientation_consistency([_orientation(15.0), 15.0], tolerance=0.5)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "north_orientation_consistency"
    assert "orientations[1] must be a resolved ValidatedBearing" in result.reason


def test_north_orientation_consistency_unevaluable_on_unusable_tolerance():
    result = north_orientation_consistency([_orientation(15.0)], tolerance=-1)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "north_orientation_consistency"
    assert result.reason


# ------------------------------------------------------------ elevation_consistency


def test_elevation_consistency_passes_within_each_label():
    result = elevation_consistency(
        {"BM-1": [_elevation(12.5), _elevation(12.5)], "SPOT-2": [_elevation(40.25)]},
        tolerance=0.25,
    )
    assert isinstance(result, CheckPassed)
    assert result.check_name == "elevation_consistency"
    assert result.unit == "feet"
    assert result.tolerance == 0.25
    assert result.computed == {
        "label_count": 2,
        "statement_count": 3,
        "contradicting_label_count": 0,
    }


def test_elevation_consistency_never_compares_across_labels():
    # Two distinct points 240 feet apart are NOT a contradiction.
    result = elevation_consistency(
        {"BM-1": [_elevation(10.0)], "BM-2": [_elevation(250.0)]}, tolerance=0.1
    )
    assert isinstance(result, CheckPassed)
    assert result.computed == {
        "label_count": 2,
        "statement_count": 2,
        "contradicting_label_count": 0,
    }


def test_elevation_consistency_fails_naming_each_conflicting_label_verbatim():
    result = elevation_consistency(
        {"BM-1": [_elevation(12.5), _elevation(13.75)], "SPOT-2": [_elevation(40.25)]},
        tolerance=0.5,
    )
    assert isinstance(result, CheckFailed)
    assert result.check_name == "elevation_consistency"
    assert result.unit == "feet"
    assert result.tolerance == 0.5
    assert result.computed == {
        "label_count": 2,
        "statement_count": 3,
        "contradicting_label_count": 1,
        "BM-1.stated_first": 12.5,
        "BM-1.restatement[1]": 13.75,
    }


def test_elevation_consistency_unevaluable_on_an_empty_mapping():
    result = elevation_consistency({}, tolerance=0.25)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "elevation_consistency"
    assert "empty" in result.reason


def test_elevation_consistency_unevaluable_on_an_empty_label_sequence():
    result = elevation_consistency(
        {"BM-1": [_elevation(12.5)], "BM-2": []}, tolerance=0.25
    )
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "elevation_consistency"
    assert "statements['BM-2'] is empty" in result.reason


def test_elevation_consistency_unevaluable_on_a_non_resolved_input():
    result = elevation_consistency({"BM-1": [_elevation(12.5), 12.5]}, tolerance=0.25)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "elevation_consistency"
    assert "statements['BM-1'][1] must be a resolved ValidatedElevation" in result.reason


def test_elevation_consistency_unevaluable_on_a_non_string_label():
    result = elevation_consistency({7: [_elevation(12.5)]}, tolerance=0.25)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "elevation_consistency"
    assert "labels must be strings" in result.reason


def test_elevation_consistency_unevaluable_on_unusable_tolerance():
    result = elevation_consistency({"BM-1": [_elevation(12.5)]}, tolerance=-0.25)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "elevation_consistency"
    assert result.reason


# --------------------------------------------------------------- address_bbl_match


def test_address_bbl_match_passes_when_every_present_fact_matches_exactly():
    result = address_bbl_match(
        _address("123 Main Street"),
        _bbl("1000010001"),
        subject_address="123 Main Street",
        subject_bbl="1000010001",
    )
    assert isinstance(result, CheckPassed)
    assert result.check_name == "address_bbl_match"
    assert result.unit is None
    assert result.tolerance == 0
    assert result.computed == {
        "compared_fact_count": 2,
        "mismatched_fact_count": 0,
        "address.document_fact[123 Main Street]": 1,
        "address.subject_target[123 Main Street]": 1,
        "bbl.document_fact[1000010001]": 1,
        "bbl.subject_target[1000010001]": 1,
    }


def test_address_bbl_match_passes_on_a_single_present_fact():
    result = address_bbl_match(
        None,
        _bbl("3012340056"),
        subject_address="45 Court Street",
        subject_bbl="3012340056",
    )
    assert isinstance(result, CheckPassed)
    assert result.computed == {
        "compared_fact_count": 1,
        "mismatched_fact_count": 0,
        "bbl.document_fact[3012340056]": 1,
        "bbl.subject_target[3012340056]": 1,
    }


def test_address_bbl_match_fails_verbatim_without_any_address_normalization():
    # "123 MAIN ST" vs "123 Main Street" would fuzzy-match; exact equality must FAIL
    # and route to review — normalization is a deliberate non-goal of this check.
    result = address_bbl_match(
        _address("123 MAIN ST"),
        _bbl("1000010001"),
        subject_address="123 Main Street",
        subject_bbl="1000010001",
    )
    assert isinstance(result, CheckFailed)
    assert result.check_name == "address_bbl_match"
    assert result.unit is None
    assert result.tolerance == 0
    assert result.computed == {
        "compared_fact_count": 2,
        "mismatched_fact_count": 1,
        "address.document_fact[123 MAIN ST]": 0,
        "address.subject_target[123 Main Street]": 0,
        "bbl.document_fact[1000010001]": 1,
        "bbl.subject_target[1000010001]": 1,
    }


def test_address_bbl_match_unevaluable_when_no_fact_is_present_at_all():
    result = address_bbl_match(
        None, None, subject_address="123 Main Street", subject_bbl="1000010001"
    )
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "address_bbl_match"
    assert "got neither" in result.reason


def test_address_bbl_match_unevaluable_on_a_blank_address_target():
    result = address_bbl_match(
        _address("123 Main Street"),
        None,
        subject_address="   ",
        subject_bbl="1000010001",
    )
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "address_bbl_match"
    assert "subject_address target is missing or blank" in result.reason


def test_address_bbl_match_unevaluable_on_a_blank_bbl_target():
    result = address_bbl_match(
        None,
        _bbl("1000010001"),
        subject_address="123 Main Street",
        subject_bbl="",
    )
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "address_bbl_match"
    assert "subject_bbl target is missing or blank" in result.reason


def test_address_bbl_match_unevaluable_on_a_non_resolved_fact():
    result = address_bbl_match(
        "123 Main Street",
        None,
        subject_address="123 Main Street",
        subject_bbl="1000010001",
    )
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "address_bbl_match"
    assert "address fact must be a resolved ValidatedUnitlessText" in result.reason


def test_address_bbl_match_unevaluable_on_a_wrong_role_fact_type():
    # A BBL-typed fact handed in as the address fact is never re-labeled to fit.
    result = address_bbl_match(
        _bbl("1000010001"),
        None,
        subject_address="123 Main Street",
        subject_bbl="1000010001",
    )
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "address_bbl_match"
    assert "never re-labeled" in result.reason


# ----------------------------------------------------------- unified package surface


def test_all_eight_sb_s3_checks_are_importable_from_the_checks_package():
    check_names = [
        "boundary_closure",
        "segment_sum_consistency",
        "calculated_vs_stated_area",
        "contradictory_dimensions",
        "scale_consistency",
        "north_orientation_consistency",
        "elevation_consistency",
        "address_bbl_match",
    ]
    for check_name in check_names:
        assert check_name in checks_package.__all__
        assert callable(getattr(checks_package, check_name))
