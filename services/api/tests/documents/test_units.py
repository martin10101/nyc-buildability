"""Unit tests for normalized-value + stated-unit typing (M2-T015 unit 3d-2).

Proves:

1. every unit rule resolves a canonical submission to its typed RESOLVED result — the
   stated value and stated unit preserved exactly, never converted (distance, area,
   bearing/orientation, elevation, scale, address text, BBL text);
2. every unit rule fails closed: ambiguous, mixed, missing, misspelled, abbreviated,
   or unsupported units — and wrong-shape values — each yield the typed
   ``UnresolvedNormalizedValue`` RESULT, visible, with the submission preserved and a
   stated reason, never an exception and never a default, best-guess conversion, or
   silent coercion;
3. the unresolved result can never be promoted: it carries no canonical value, unit,
   or text attribute at all, and its ``promotable`` flag is permanently ``False``;
4. the refusal payload is metadata-only and JSON-serializable with the stable
   ``reject_code``, mirroring the ``errors.py`` payload convention;
5. every canonical ``SurveyFactType`` member is governed — it has a unit rule or an
   explicit no-rule entry (the reconstructed polygon, whose validity belongs to the
   ``geometry_validity`` check and which therefore never resolves here);
6. v1 wire compat: this module is application-level only — validating changed nothing
   on the wire, and a taxonomy-refused ``fact_type`` surfaces as the same typed
   unresolved result instead of a competing schema.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from app.documents.taxonomy import SurveyFactType
from app.documents.units import (
    AngleUnit,
    AreaUnit,
    DistanceUnit,
    ElevationUnit,
    FACT_TYPES_WITH_UNIT_RULE,
    FACT_TYPES_WITHOUT_UNIT_RULE,
    UnresolvedNormalizedValue,
    ValidatedArea,
    ValidatedBearing,
    ValidatedDistance,
    ValidatedElevation,
    ValidatedScale,
    ValidatedUnitlessText,
    validate_normalized_value,
)

# -------------------------------------------------------------- resolved path

#: (fact_type, normalized_value, unit, expected result type, expected unit member).
#: One canonical passing case per rule; the value/unit assertions prove the stated
#: submission is preserved exactly — never converted.
VALID_CASES = [
    ("boundary_segment_distance", 125.5, "feet", ValidatedDistance, DistanceUnit.FEET),
    ("computed_closure", 0.04, "feet", ValidatedDistance, DistanceUnit.FEET),
    ("stated_lot_area", 2500, "square_feet", ValidatedArea, AreaUnit.SQUARE_FEET),
    ("calculated_lot_area", 2498.6, "square_feet", ValidatedArea, AreaUnit.SQUARE_FEET),
    ("boundary_bearing", 44.5083, "degrees", ValidatedBearing, AngleUnit.DEGREES),
    ("north_arrow_orientation", 12.25, "degrees", ValidatedBearing, AngleUnit.DEGREES),
    ("elevation_value", -3.2, "feet", ValidatedElevation, ElevationUnit.FEET),
    ("scale_statement", "1:240", None, ValidatedScale, None),
    ("address_text", "123 Example Street, Brooklyn, NY 11201", None, ValidatedUnitlessText, None),
    ("bbl_text", "3012340056", None, ValidatedUnitlessText, None),
]


@pytest.mark.parametrize(
    ("fact_type", "value", "unit", "expected_type", "expected_unit"),
    VALID_CASES,
    ids=[f"{case[0]}={case[1]!r}+{case[2]!r}" for case in VALID_CASES],
)
def test_every_rule_resolves_a_canonical_submission(
    fact_type: str,
    value: object,
    unit: str | None,
    expected_type: type,
    expected_unit: object,
) -> None:
    result = validate_normalized_value(fact_type, value, unit)
    assert isinstance(result, expected_type)
    assert not isinstance(result, UnresolvedNormalizedValue)
    assert result.resolved is True
    assert result.fact_type is SurveyFactType(fact_type)
    assert not isinstance(result, Exception)
    if expected_unit is not None:
        assert isinstance(
            result, (ValidatedDistance, ValidatedArea, ValidatedBearing, ValidatedElevation)
        )
        assert result.unit is expected_unit
        assert result.value == value  # preserved exactly — never converted


def test_area_stated_in_acres_stays_acres() -> None:
    result = validate_normalized_value("stated_lot_area", 0.25, "acres")
    assert isinstance(result, ValidatedArea)
    assert result.unit is AreaUnit.ACRES
    assert result.value == 0.25  # never best-guess converted to square feet


def test_scale_canonical_ratio_parsed_deterministically() -> None:
    result = validate_normalized_value("scale_statement", "1:240", None)
    assert isinstance(result, ValidatedScale)
    assert result.ratio == "1:240"
    assert result.ratio_denominator == 240


def test_unitless_text_preserved_verbatim() -> None:
    result = validate_normalized_value("bbl_text", "3012340056", None)
    assert isinstance(result, ValidatedUnitlessText)
    assert result.text == "3012340056"


def test_bearing_canonical_range_edges() -> None:
    assert isinstance(
        validate_normalized_value("north_arrow_orientation", 0.0, "degrees"), ValidatedBearing
    )
    assert isinstance(
        validate_normalized_value("boundary_bearing", 359.9999, "degrees"), ValidatedBearing
    )
    # 360.0 is never wrapped to canonical north — wrapping is a silent coercion.
    assert isinstance(
        validate_normalized_value("boundary_bearing", 360.0, "degrees"),
        UnresolvedNormalizedValue,
    )


# ------------------------------------------------------------ unresolved path

#: (fact_type, normalized_value, unit) — at least one failing case per rule, plus the
#: cross-cutting refusals (missing/ambiguous/mixed/unsupported units, wrong shapes,
#: the no-rule polygon, taxonomy-refused fact types).
UNRESOLVED_CASES = [
    # boundary distance / computed closure
    ("boundary_segment_distance", 125.5, None),  # missing unit — never defaulted
    ("boundary_segment_distance", 125.5, "ft"),  # abbreviation — no alias interpretation
    ("boundary_segment_distance", 125.5, "Feet"),  # exact match only: no case folding
    ("boundary_segment_distance", 125.5, "square_feet"),  # wrong quantity's unit
    ("boundary_segment_distance", 0, "feet"),  # a distance must be strictly positive
    ("boundary_segment_distance", "125.5", "feet"),  # string number — never coerced
    ("boundary_segment_distance", {"feet": 125, "inches": 6}, "feet"),  # mixed-unit shape
    ("boundary_segment_distance", 125.5, 12),  # non-string unit object
    ("computed_closure", float("nan"), "feet"),  # non-finite number
    # lot area
    ("stated_lot_area", 2500, "sq_ft"),  # abbreviation — no alias interpretation
    ("stated_lot_area", 2500, "feet"),  # a distance unit is not an area unit
    ("stated_lot_area", -10, "square_feet"),  # an area must be strictly positive
    ("calculated_lot_area", 2500, None),  # missing unit — never defaulted
    # bearing / orientation
    ("boundary_bearing", -15.0, "degrees"),  # outside [0, 360) — never wrapped
    ("boundary_bearing", 45.0, "radians"),  # unsupported angle unit — never converted
    ("north_arrow_orientation", "N 45 E", "degrees"),  # quadrant prose is not canonical
    # elevation
    ("elevation_value", 12.0, None),  # missing unit — never defaulted
    ("elevation_value", float("inf"), "feet"),  # non-finite number
    ("elevation_value", True, "feet"),  # bool is not a number
    # scale statement
    ("scale_statement", "1 inch = 20 feet", None),  # source prose — never inferred
    ("scale_statement", 240, None),  # bare denominator is not the canonical form
    ("scale_statement", "2:480", None),  # not the canonical 1:N form
    ("scale_statement", "1:0", None),  # N must be a positive integer
    ("scale_statement", "1:240", "feet"),  # dimensionless — a unit here is ambiguous
    # address text
    ("address_text", "", None),  # empty string is not an address
    ("address_text", "   ", None),  # whitespace-only is not an address
    ("address_text", "123 Example Street", "feet"),  # unitless — a unit is ambiguous
    # BBL text
    ("bbl_text", "301234005", None),  # 9 digits — not a BBL
    ("bbl_text", "6012340056", None),  # borough 6 does not exist
    ("bbl_text", " 3012340056", None),  # no trimming — silent cleanup is acceptance
    ("bbl_text", "Block 1234 Lot 56", None),  # prose is never reformatted
    ("bbl_text", 3012340056, None),  # a number, not the wire string
    # no-rule fact type — always fails closed here
    ("reconstructed_boundary_polygon", {"type": "Polygon", "coordinates": []}, None),
    # taxonomy-refused fact types wrap into the same typed unresolved result
    ("lot_frontage", 100.0, "feet"),
    ("BOUNDARY_SEGMENT_DISTANCE", 100.0, "feet"),
]


@pytest.mark.parametrize(
    ("fact_type", "value", "unit"),
    UNRESOLVED_CASES,
    ids=[f"{case[0]}={case[1]!r}+{case[2]!r}" for case in UNRESOLVED_CASES],
)
def test_ambiguous_missing_mixed_or_unsupported_submissions_fail_closed(
    fact_type: str, value: object, unit: object
) -> None:
    result = validate_normalized_value(fact_type, value, unit)
    assert isinstance(result, UnresolvedNormalizedValue)
    assert result.resolved is False
    assert result.promotable is False
    assert result.reject_code == "unresolved_normalized_value"
    assert result.reason.strip()
    assert result.submitted_value == repr(value)  # submission preserved, visible
    assert not isinstance(result, Exception)
    # Nothing to promote: the refusal carries no canonical value, unit, or text.
    assert not hasattr(result, "value")
    assert not hasattr(result, "unit")
    assert not hasattr(result, "text")


def test_taxonomy_refused_fact_type_wraps_the_taxonomy_reason() -> None:
    result = validate_normalized_value("lot_frontage", 100.0, "feet")
    assert isinstance(result, UnresolvedNormalizedValue)
    assert result.submitted_fact_type == "lot_frontage"
    assert "taxonomy" in result.reason


def test_polygon_never_resolves_through_unit_typing() -> None:
    assert SurveyFactType.RECONSTRUCTED_BOUNDARY_POLYGON in FACT_TYPES_WITHOUT_UNIT_RULE
    result = validate_normalized_value(
        "reconstructed_boundary_polygon", {"type": "Polygon", "coordinates": []}, None
    )
    assert isinstance(result, UnresolvedNormalizedValue)
    assert "geometry_validity" in result.reason


def test_unresolved_payload_is_json_serializable_metadata_only() -> None:
    result = validate_normalized_value("boundary_segment_distance", 125.5, "ft")
    assert isinstance(result, UnresolvedNormalizedValue)
    payload = result.to_payload()
    assert payload["reject_code"] == "unresolved_normalized_value"
    assert payload["submitted_fact_type"] == "boundary_segment_distance"
    assert payload["submitted_value"] == "125.5"
    assert payload["submitted_unit"] == "ft"
    assert payload["reason"]
    assert set(payload) == {
        "reject_code",
        "submitted_fact_type",
        "submitted_value",
        "submitted_unit",
        "reason",
    }
    json.dumps(payload)  # serializable into an API response / audit record


def test_non_string_unit_preserved_as_repr() -> None:
    result = validate_normalized_value("boundary_segment_distance", 125.5, 12)
    assert isinstance(result, UnresolvedNormalizedValue)
    assert result.submitted_unit == "12"
    json.dumps(result.to_payload())


def test_results_are_immutable_values() -> None:
    resolved = validate_normalized_value("boundary_segment_distance", 125.5, "feet")
    assert isinstance(resolved, ValidatedDistance)
    unresolved = validate_normalized_value("boundary_segment_distance", 125.5, None)
    assert isinstance(unresolved, UnresolvedNormalizedValue)
    with pytest.raises(dataclasses.FrozenInstanceError):
        resolved.value = 999.0  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        unresolved.reason = "rewritten"  # type: ignore[misc]


# ---------------------------------------------------------------- governance


def test_every_canonical_fact_type_is_governed() -> None:
    assert FACT_TYPES_WITH_UNIT_RULE | FACT_TYPES_WITHOUT_UNIT_RULE == frozenset(SurveyFactType)
    assert not FACT_TYPES_WITH_UNIT_RULE & FACT_TYPES_WITHOUT_UNIT_RULE
