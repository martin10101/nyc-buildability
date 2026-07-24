"""M4-T007 unit tests for the exact-legal-arithmetic foundation (units.py).

Everything here is offline, deterministic, and stdlib-only. It pins the FROZEN
interface of :mod:`app.rules.units`: canonical-decimal construction (no binary
noise), explicit per-rule rounding modes on exact rationals, the JSON-number
boundary, and dimensional unit enforcement (unknown AND incompatible units
rejected). DF-2 / blocker B-014.
"""

from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction

import pytest

from app.rules import units as u

# --------------------------------------------------------------------------
# Canonical-decimal construction: the geometry-float isolation boundary.
# --------------------------------------------------------------------------

def test_to_exact_is_canonical_not_binary_noise():
    # str(float) is the shortest round-tripping decimal, so 0.1 -> exactly 1/10,
    # never Fraction(0.1) == 3602879701896397/36028797018963968.
    assert u.to_exact(0.1) == Fraction(1, 10)
    assert u.to_exact(0.2) == Fraction(1, 5)
    assert u.to_exact(0.3) == Fraction(3, 10)
    assert u.to_exact(1.5) == Fraction(3, 2)
    # the value is exact, unlike the raw binary double.
    assert u.to_exact(0.1) != Fraction(0.1)


def test_to_exact_accepts_int_str_decimal_fraction_exactly():
    assert u.to_exact(10000) == Fraction(10000)
    assert u.to_exact(10**309) == Fraction(10**309)  # arbitrary precision, not float-limited
    assert u.to_exact("0.1") == Fraction(1, 10)
    assert u.to_exact(" 2.50 ") == Fraction(5, 2)  # surrounding whitespace tolerated
    assert u.to_exact("1e3") == Fraction(1000)
    assert u.to_exact(Decimal("0.005")) == Fraction(1, 200)
    assert u.to_exact(Fraction(7, 3)) == Fraction(7, 3)


def test_the_classic_float_traps_are_exact():
    assert u.to_exact(0.1) + u.to_exact(0.2) == u.to_exact(0.3)     # 0.1+0.2 != 0.3 in float
    assert u.to_exact(0.3) - u.to_exact(0.1) == u.to_exact(0.2)
    assert u.to_exact(1.1) + u.to_exact(2.2) == u.to_exact(3.3)
    assert u.to_exact(0.1) * 3 == u.to_exact(0.3)


@pytest.mark.parametrize("bad", [True, False, None, float("nan"), float("inf"), float("-inf")])
def test_to_exact_fails_closed_on_non_numeric_or_non_finite(bad):
    with pytest.raises(u.LegalNumberError):
        u.to_exact(bad)


@pytest.mark.parametrize("bad", ["", "abc", "1.2.3", "NaN", "Infinity", "  ", "0x1"])
def test_to_exact_rejects_malformed_or_nonfinite_strings(bad):
    with pytest.raises(u.LegalNumberError):
        u.to_exact(bad)


@pytest.mark.parametrize("bad", [[1], {"a": 1}, (1, 2), complex(1, 2), object()])
def test_to_exact_rejects_unsupported_types(bad):
    with pytest.raises(u.LegalNumberError):
        u.to_exact(bad)


def test_canonical_decimal_str_terminating_and_repeating():
    assert u.canonical_decimal_str(1.5) == "1.5"
    assert u.canonical_decimal_str(0.005) == "0.005"
    assert u.canonical_decimal_str(-2.5) == "-2.5"
    assert u.canonical_decimal_str(15000) == "15000"
    assert u.canonical_decimal_str(0) == "0"
    # a non-terminating rational is rendered exactly as a fraction, never truncated.
    assert u.canonical_decimal_str(Fraction(1, 3)) == "1/3"
    assert u.canonical_decimal_str(Fraction(2, 7)) == "2/7"


# --------------------------------------------------------------------------
# Per-rule rounding: explicit mode + scale, on the exact rational.
# --------------------------------------------------------------------------

def test_quantize_half_up_is_away_from_zero_and_exact():
    assert u.quantize("2.5", 0) == Fraction(3)
    assert u.quantize("-2.5", 0) == Fraction(-3)
    assert u.quantize("0.5", 0) == Fraction(1)
    # 2.675 rounded to 2 places is exactly 2.68 - the classic float trap
    # (round(2.675, 2) == 2.67) does NOT occur because the value stays exact.
    assert u.quantize("2.675", 2) == Fraction(268, 100)
    assert float(u.quantize("2.675", 2)) == 2.68


def test_quantize_half_even_banker_rounding():
    assert u.quantize("2.5", 0, rounding=u.ROUND_HALF_EVEN) == Fraction(2)
    assert u.quantize("3.5", 0, rounding=u.ROUND_HALF_EVEN) == Fraction(4)
    assert u.quantize("1.25", 1, rounding=u.ROUND_HALF_EVEN) == Fraction(12, 10)
    assert u.quantize("1.35", 1, rounding=u.ROUND_HALF_EVEN) == Fraction(14, 10)


def test_quantize_directed_modes():
    assert u.quantize("1.9", 0, rounding=u.ROUND_DOWN) == Fraction(1)     # toward zero
    assert u.quantize("-1.9", 0, rounding=u.ROUND_DOWN) == Fraction(-1)
    assert u.quantize("1.1", 0, rounding=u.ROUND_UP) == Fraction(2)       # away from zero
    assert u.quantize("-1.1", 0, rounding=u.ROUND_UP) == Fraction(-2)
    assert u.quantize("-1.1", 0, rounding=u.ROUND_FLOOR) == Fraction(-2)  # toward -inf
    assert u.quantize("1.1", 0, rounding=u.ROUND_CEILING) == Fraction(2)  # toward +inf
    assert u.quantize("-1.9", 0, rounding=u.ROUND_CEILING) == Fraction(-1)


def test_quantize_scale_including_negative():
    assert u.quantize("3.14159", 2) == Fraction(314, 100)
    assert u.quantize("1234", -2) == Fraction(1200)  # round to hundreds
    assert u.quantize("1250", -2, rounding=u.ROUND_HALF_EVEN) == Fraction(1200)


def test_quantize_rejects_bad_mode_and_ndigits():
    with pytest.raises(u.LegalNumberError):
        u.quantize("1.5", 0, rounding="ROUND_SOMETHING")
    with pytest.raises(u.LegalNumberError):
        u.quantize("1.5", 1.0)  # ndigits must be int
    with pytest.raises(u.LegalNumberError):
        u.quantize("1.5", True)  # bool is not an int scale


def test_default_legal_rounding_is_half_up():
    assert u.DEFAULT_LEGAL_ROUNDING == u.ROUND_HALF_UP


# --------------------------------------------------------------------------
# JSON-number boundary + representability.
# --------------------------------------------------------------------------

def test_to_json_number_preserves_int_and_renders_fraction_to_float():
    assert u.to_json_number(10000) == 10000 and isinstance(u.to_json_number(10000), int)
    assert u.to_json_number(Fraction(3, 2)) == 1.5
    assert u.to_json_number(Fraction(15000)) == 15000.0
    assert isinstance(u.to_json_number(Fraction(15000)), float)
    assert u.to_json_number(3999.99) == 3999.99  # finite float passes through


def test_to_json_number_fails_closed_on_nonfinite_and_overflow():
    with pytest.raises(u.LegalNumberError):
        u.to_json_number(float("inf"))
    with pytest.raises(u.LegalNumberError):
        u.to_json_number(float("nan"))
    overflow = u.to_exact(1.2e308) * u.to_exact(1.5)  # 1.8e308, above max double
    with pytest.raises(u.LegalNumberError):
        u.to_json_number(overflow)


def test_is_representable_float():
    assert u.is_representable_float(1.5e308) is True
    assert u.is_representable_float(u.to_exact(1.2e308) * u.to_exact(1.5)) is False
    assert u.is_representable_float(float("inf")) is False
    assert u.is_representable_float("not a number") is False


# --------------------------------------------------------------------------
# Dimensional units: unknown AND incompatible rejected.
# --------------------------------------------------------------------------

def test_require_known_unit_accepts_known_and_none_rejects_unknown():
    for unit in ("far", "feet", "square_feet"):
        assert u.require_known_unit(unit) == unit
    assert u.require_known_unit(None) is None
    with pytest.raises(u.UnitError):
        u.require_known_unit("furlongs")
    with pytest.raises(u.UnitError):
        u.require_known_unit("SQUARE_FEET")  # case-sensitive; not silently coerced


def test_units_compatible_by_dimension():
    assert u.units_compatible("feet", "foot") is True     # same dimension, different label
    assert u.units_compatible("feet", "square_feet") is False
    assert u.units_compatible("far", None) is True        # both dimensionless
    assert u.units_compatible("feet", "unknownium") is False
    u.assert_compatible("far", "ratio")
    with pytest.raises(u.UnitError):
        u.assert_compatible("feet", "square_feet")


def test_quantity_add_sub_require_same_dimension():
    a = u.Quantity.of(10, "feet")
    b = u.Quantity.of(5, "feet")
    assert (a + b).value == Fraction(15) and (a + b).unit == "feet"
    assert (a - b).value == Fraction(5)
    with pytest.raises(u.UnitError):
        a + u.Quantity.of(1, "square_feet")


def test_quantity_multiply_scales_by_dimensionless_and_rejects_dim_product():
    lot = u.Quantity.of(10000, "square_feet")
    far = u.Quantity.of(1.5, "far")
    floor_area = lot * far
    assert floor_area.unit == "square_feet" and floor_area.value == Fraction(15000)
    # multiplying two dimensional units has no unambiguous legal unit -> fail closed.
    with pytest.raises(u.UnitError):
        u.Quantity.of(10, "feet") * u.Quantity.of(10, "feet")


def test_quantity_divide_ratio_and_rejects_incompatible():
    ratio = u.Quantity.of(30, "feet") / u.Quantity.of(10, "feet")
    assert ratio.unit is None and ratio.value == Fraction(3)
    kept = u.Quantity.of(15000, "square_feet") / u.Quantity.of(2, "far")
    assert kept.unit == "square_feet" and kept.value == Fraction(7500)
    with pytest.raises(u.UnitError):
        u.Quantity.of(10, "square_feet") / u.Quantity.of(2, "feet")
    with pytest.raises(u.LegalNumberError):
        u.Quantity.of(10, "feet") / u.Quantity.of(0, "far")


def test_quantity_comparison_is_exact_and_unit_checked():
    # exact value equality across a float trap, unit-checked.
    summed = u.Quantity.of(0.1, "feet") + u.Quantity.of(0.2, "feet")
    assert summed.equals(u.Quantity.of(0.3, "feet"))
    assert u.Quantity.of(3, "feet") > u.Quantity.of(2, "feet")
    assert u.Quantity.of(2, "feet") <= u.Quantity.of(2, "feet")
    with pytest.raises(u.UnitError):
        _ = u.Quantity.of(3, "feet") < u.Quantity.of(3, "square_feet")
    with pytest.raises(u.UnitError):
        u.Quantity.of(3, "feet").equals(u.Quantity.of(3, "square_feet"))


def test_quantity_to_json_number():
    assert u.Quantity.of(15000, "square_feet").to_json_number() == 15000.0
    assert math.isclose(u.Quantity.of(1.5, "far").to_json_number(), 1.5)
