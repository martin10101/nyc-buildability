"""BBL validation/normalization tests (task M1-T002, scenarios S2/S4/S6).

All tests are offline and deterministic. Grounding for every rule:
PLUTO Data Dictionary 26v1 p.38 (via docs/research/pluto-mappluto-2026-07-16.md
section 4.1) and packages/contracts/schemas/v1/common.schema.json#/$defs/bbl.
"""

import pytest

from app.connectors.bbl import (
    BBLValidationError,
    bbl_from_components,
    check_identifier_consistency,
    normalize_bbl,
)

# --------------------------------------------------------------------------
# S2 boundary: valid inputs and canonical assembly
# --------------------------------------------------------------------------


def test_normalize_plain_canonical_string() -> None:
    result = normalize_bbl("1000010100")
    assert result.canonical == "1000010100"
    assert (result.borough, result.block, result.lot) == (1, 1, 100)
    assert result.raw == "1000010100"


def test_normalize_integer_input() -> None:
    assert normalize_bbl(1000010100).canonical == "1000010100"


def test_normalize_socrata_decimal_serialization_f12() -> None:
    # F12 fixture / G1 finding C6: number-typed BBL with all-zero fraction.
    raw = "1000010100.00000000"
    result = normalize_bbl(raw)
    assert result.canonical == "1000010100"
    assert result.raw == raw  # verbatim raw preserved for provenance


def test_normalize_borough_bounds_1_and_5() -> None:
    assert normalize_bbl("1000010001").borough == 1
    assert normalize_bbl("5999999999").borough == 5


@pytest.mark.parametrize(
    ("borough", "block", "lot", "expected"),
    [
        (1, 1, 1, "1000010001"),  # minimum block and lot, zero-padded
        (5, 99999, 9999, "5999999999"),  # maxima
        ("1", "4", "7501", "1000047501"),  # string components (F2a condo billing lot)
        ("2", "215.00", "3", "2002150003"),  # decimal-zero tails tolerated
    ],
)
def test_bbl_from_components_bounds(borough, block, lot, expected) -> None:
    assert bbl_from_components(borough, block, lot) == expected


@pytest.mark.parametrize(
    ("borough", "block", "lot"),
    [
        (0, 1, 1),
        (6, 1, 1),
        (1, 0, 1),
        (1, 100000, 1),
        (1, 1, 0),
        (1, 1, 10000),
    ],
)
def test_bbl_from_components_out_of_range(borough, block, lot) -> None:
    with pytest.raises(BBLValidationError) as excinfo:
        bbl_from_components(borough, block, lot)
    assert excinfo.value.code == "invalid_component"


# --------------------------------------------------------------------------
# S4a ambiguous/malformed: typed rejection naming the defect
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected_code"),
    [
        ("100001010", "wrong_length"),  # 9 digits
        ("10000101001", "wrong_length"),  # 11 digits
        ("6000010100", "invalid_borough"),  # borough 6
        ("0000010100", "invalid_borough"),  # borough 0
        ("9999999999", "invalid_borough"),  # borough 9 (task packet F3 input)
        ("1000000100", "invalid_block"),  # all-zero block
        ("1000010000", "invalid_lot"),  # all-zero lot
        ("ABCDEFGHIJ", "non_numeric"),
        ("10000101OO", "non_numeric"),  # letter O confusion
        ("-1000010100", "negative"),
        (-1000010100, "negative"),
        ("1000010100.5", "non_integer_decimal"),
        (1000010100.5, "non_integer_decimal"),
        ("", "empty"),
        ("   ", "empty"),
        (None, "empty"),
        (True, "non_numeric"),
        (["1000010100"], "non_numeric"),
    ],
)
def test_malformed_inputs_rejected_with_typed_codes(raw, expected_code) -> None:
    with pytest.raises(BBLValidationError) as excinfo:
        normalize_bbl(raw)
    assert excinfo.value.code == expected_code
    payload = excinfo.value.to_payload()
    assert payload["error_type"] == "validation_error"
    assert payload["code"] == expected_code
    assert payload["message"]  # names the defect
    assert "Traceback" not in str(payload)


def test_error_payload_preserves_raw_value_reference() -> None:
    with pytest.raises(BBLValidationError) as excinfo:
        normalize_bbl("6000010100")
    assert "6000010100" in excinfo.value.to_payload()["raw_value"]


# --------------------------------------------------------------------------
# S4b conflicting identifiers
# --------------------------------------------------------------------------


def test_consistency_agreement_yields_no_conflicts() -> None:
    # Values as SODA serves them (F1 record): strings, no padding.
    assert (
        check_identifier_consistency("1000010100", borocode="1", block="1", lot="100")
        == []
    )


def test_consistency_disagreement_is_reported_not_resolved() -> None:
    conflicts = check_identifier_consistency(
        "1000010100", borocode="2", block="1", lot="100"
    )
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict["field"] == "borocode"
    # Both values stay visible; nothing is silently resolved (PRD section 9).
    assert conflict["bbl_derived_value"] == 1
    assert conflict["component_value_raw"] == "2"


def test_consistency_unparseable_component_is_a_conflict() -> None:
    conflicts = check_identifier_consistency("1000010100", block="not-a-number")
    assert len(conflicts) == 1
    assert conflicts[0]["field"] == "block"
    assert "unparseable" in conflicts[0]["reason"]


def test_consistency_missing_components_are_skipped() -> None:
    assert check_identifier_consistency("1000010100") == []


# --------------------------------------------------------------------------
# S6 idempotency
# --------------------------------------------------------------------------


def test_normalization_is_deterministic() -> None:
    first = normalize_bbl("1000010100.00000000")
    second = normalize_bbl("1000010100.00000000")
    assert first == second
