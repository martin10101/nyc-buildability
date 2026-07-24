"""Exact legal arithmetic (canonical-decimal / exact-rational) and dimensional units.

Foundation for M4-T007 / DF-2 / blocker B-014. NYC legal thresholds - FAR, floor
area, lot coverage, yard depths, height, setback - are computed and, above all,
*compared* here in **exact rational arithmetic** (:class:`fractions.Fraction`)
constructed from **canonical decimal strings**, never in binary IEEE-754 float. A
float equality/threshold test at an exact legal boundary is subject to
representation error (``0.1 + 0.2 != 0.3``); an exact-rational one is not.

Why exact rational and not raw ``Decimal``:

* ``Decimal`` is exact for terminating decimals but its division rounds to a
  context precision, so a quotient at a legal boundary can still mis-compare.
  ``Fraction`` is closed under ``+ - * /`` for rational inputs: no rounding, ever,
  until a rule *explicitly* asks for it via :func:`quantize`.
* Construction goes through a canonical decimal string, so a JSON/float input
  ``0.1`` becomes exactly ``Fraction(1, 10)`` - NOT ``Fraction(0.1)`` which would
  capture the binary noise ``Fraction(3602879701896397, 36028797018963968)``.

The GEOMETRY-FLOAT ISOLATION boundary is :func:`to_exact`: shapely / PostGIS
geometry keeps its floats in the spatial layer, and the single, explicit, typed
conversion into a legal value is a call to :func:`to_exact`. Nothing on the legal
value path consumes a raw geometry float without passing through it.

Per-rule ROUNDING is explicit: intermediate results are kept exact, and rounding
happens only where a rule places a ``round`` step, with a documented mode
(:data:`DEFAULT_LEGAL_ROUNDING`, round-half-away-from-zero) and scale (the step's
``ndigits``). There is no hidden intermediate rounding.

UNIT enforcement: :func:`require_known_unit` rejects an unknown unit (fail
closed), and :class:`Quantity` performs exact unit-aware arithmetic that rejects
dimensionally incompatible combinations (``feet + square_feet``) and comparisons
across incompatible units. Unknown *and* incompatible units are rejected, never
silently coerced.

This module is a **frozen interface** (M4-T007): its public names and behaviour
are the contract future M4 rule tasks build on. It has no I/O and no dependency
beyond the standard library.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction

__all__ = [
    "Exact",
    "LegalNumberError",
    "UnitError",
    "to_exact",
    "canonical_decimal_str",
    "is_representable_float",
    "to_json_number",
    "ROUND_HALF_UP",
    "ROUND_HALF_EVEN",
    "ROUND_DOWN",
    "ROUND_UP",
    "ROUND_FLOOR",
    "ROUND_CEILING",
    "ROUNDING_MODES",
    "DEFAULT_LEGAL_ROUNDING",
    "quantize",
    "KNOWN_UNITS",
    "DIMENSIONLESS_UNITS",
    "dimension_of",
    "require_known_unit",
    "units_compatible",
    "assert_compatible",
    "Quantity",
]

# The internal legal number type. Public alias so callers can annotate/typecheck
# against ``units.Exact`` without importing ``fractions`` directly.
Exact = Fraction

_MAX_FINITE_FLOAT = sys.float_info.max


class LegalNumberError(ValueError):
    """A value cannot be turned into (or emitted from) an exact legal number.

    Raised for ``None``, ``bool``, a non-finite float/Decimal (NaN / infinity), a
    malformed decimal string, an unsupported type, or a magnitude that cannot be
    represented as a finite JSON number. Fail-closed: a bad numeric value never
    becomes a fabricated result."""


class UnitError(ValueError):
    """A unit is unknown, or two quantities are dimensionally incompatible for the
    attempted operation (add/subtract/compare across different dimensions, an
    unsupported dimensional product, etc.). Fail-closed: incompatible units are
    rejected, never silently coerced."""


# ---------------------------------------------------------------------------
# Canonical-decimal construction  (the geometry-float isolation boundary)
# ---------------------------------------------------------------------------

def to_exact(value: object) -> Fraction:
    """Convert ``value`` to an EXACT :class:`~fractions.Fraction` via a canonical
    decimal string. This is the single, explicit, typed conversion from a raw
    (possibly geometry-derived) number onto the legal value path.

    * ``int`` -> exact ``Fraction`` (arbitrary precision; not float-limited).
    * ``float`` -> ``Fraction(Decimal(str(x)))``: ``str`` is the shortest decimal
      that round-trips the double, so ``0.1`` becomes exactly ``Fraction(1, 10)``.
      Never ``Fraction(x)`` (that captures binary noise).
    * ``Decimal`` -> exact ``Fraction`` (finite only).
    * ``str`` -> parsed as a canonical decimal literal (finite only).
    * ``Fraction`` -> returned unchanged.

    Fails closed (:class:`LegalNumberError`) for ``bool``, ``None``, a non-finite
    float/Decimal, a malformed string, or any other type. A boolean is rejected
    even though ``bool`` is an ``int`` subclass: ``True`` is not a legal quantity.
    """
    if isinstance(value, bool):
        raise LegalNumberError(f"boolean {value!r} is not a legal numeric value")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise LegalNumberError(
                f"non-finite float {value!r} (NaN or infinity) is not a usable legal value"
            )
        # str(float) is the shortest round-tripping decimal -> canonical + exact.
        return Fraction(Decimal(str(value)))
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise LegalNumberError(
                f"non-finite Decimal {value!r} (NaN or infinity) is not a usable legal value"
            )
        return Fraction(value)
    if isinstance(value, str):
        text = value.strip()
        try:
            dec = Decimal(text)
        except (InvalidOperation, ValueError) as exc:
            raise LegalNumberError(f"malformed decimal string {value!r}") from exc
        if not dec.is_finite():
            raise LegalNumberError(
                f"non-finite decimal string {value!r} (NaN or infinity) is not usable"
            )
        return Fraction(dec)
    raise LegalNumberError(
        f"unsupported type {type(value).__name__} for a legal numeric value ({value!r})"
    )


def canonical_decimal_str(value: object) -> str:
    """A canonical, exact string form of ``value`` for traces / provenance.

    Terminating rationals (denominator factors only 2 and 5) are rendered as an
    exact decimal string (e.g. ``"1.5"``, ``"0.005"``); a non-terminating rational
    (e.g. ``1/3``) is rendered as an exact ``"numerator/denominator"`` fraction so
    the value is never silently truncated. Deterministic and platform-independent.
    """
    frac = to_exact(value)
    den = frac.denominator
    # strip all factors of 2 and 5 from the denominator; if anything remains the
    # decimal expansion does not terminate.
    residual = den
    for factor in (2, 5):
        while residual % factor == 0:
            residual //= factor
    if residual != 1:
        return f"{frac.numerator}/{frac.denominator}"
    # terminating: scale to an integer, then place the decimal point.
    tens = 0
    scaled = frac
    while scaled.denominator != 1:
        scaled *= 10
        tens += 1
    digits = scaled.numerator  # an int; sign carried here
    sign = "-" if digits < 0 else ""
    digits = abs(digits)
    if tens == 0:
        return f"{sign}{digits}"
    text = str(digits).rjust(tens + 1, "0")
    return f"{sign}{text[:-tens]}.{text[-tens:]}"


# ---------------------------------------------------------------------------
# Representability at the JSON-number boundary
# ---------------------------------------------------------------------------

def is_representable_float(value: object) -> bool:
    """True iff ``value`` can be emitted as a FINITE JSON number (a finite
    ``float``). An exact rational whose magnitude overflows the double range
    (e.g. ``1.8e308``) is NOT representable: the caller must fail closed rather
    than emit ``inf``. Never raises."""
    try:
        exact = to_exact(value)
    except LegalNumberError:
        return False
    try:
        emitted = float(exact)
    except (OverflowError, ValueError):
        return False
    return math.isfinite(emitted)


def to_json_number(value: object) -> int | float:
    """Render an exact/legal number to a JSON-safe FINITE number for a trace.

    ``int`` passes through as ``int`` (so a raw integer argument such as a
    ``10000`` lot area stays ``10000``, not ``10000.0``); ``float`` passes through
    (finite only); a :class:`~fractions.Fraction` / ``Decimal`` is rendered to the
    correctly-rounded ``float``. Fails closed (:class:`LegalNumberError`) rather
    than ever emitting NaN / infinity or raising an uncaught ``OverflowError``.
    """
    if isinstance(value, bool):
        # not expected on the numeric value path; return as-is without coercion.
        return value  # type: ignore[return-value]
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise LegalNumberError(f"cannot emit non-finite float {value!r} to a trace")
        return value
    if isinstance(value, Fraction | Decimal):
        try:
            emitted = float(value)
        except (OverflowError, ValueError) as exc:
            raise LegalNumberError(
                f"exact value {value!r} overflows the finite JSON number range"
            ) from exc
        if not math.isfinite(emitted):
            raise LegalNumberError(
                f"exact value {value!r} overflows the finite JSON number range"
            )
        return emitted
    raise LegalNumberError(f"cannot emit type {type(value).__name__} to a trace ({value!r})")


# ---------------------------------------------------------------------------
# Per-rule rounding: explicit mode + scale, on exact rationals
# ---------------------------------------------------------------------------
# Mode names match ``decimal`` so they are recognizable and serializable.
ROUND_HALF_UP = "ROUND_HALF_UP"        # ties away from zero (common legal default)
ROUND_HALF_EVEN = "ROUND_HALF_EVEN"    # ties to even (banker's)
ROUND_DOWN = "ROUND_DOWN"              # toward zero (truncate)
ROUND_UP = "ROUND_UP"                  # away from zero
ROUND_FLOOR = "ROUND_FLOOR"            # toward -infinity
ROUND_CEILING = "ROUND_CEILING"        # toward +infinity

ROUNDING_MODES = frozenset(
    {ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN, ROUND_UP, ROUND_FLOOR, ROUND_CEILING}
)

# The default legal rounding mode. NYC dimensional thresholds conventionally round
# half away from zero; a rule may still round to a specific SCALE (ndigits). This
# is documented and explicit precisely so it is never an accidental float artifact.
DEFAULT_LEGAL_ROUNDING = ROUND_HALF_UP


def _round_fraction_to_int(x: Fraction, rounding: str) -> int:
    """Round an exact rational to the nearest integer under ``rounding``. Exact:
    the tie decision is made on the exact remainder, never on a float."""
    if x == 0:
        return 0
    sign = 1 if x > 0 else -1
    magnitude = x if x > 0 else -x
    whole, remainder = divmod(magnitude.numerator, magnitude.denominator)
    if remainder == 0:
        return sign * whole
    twice = 2 * remainder
    den = magnitude.denominator
    if rounding == ROUND_DOWN:
        step = 0
    elif rounding == ROUND_UP:
        step = 1
    elif rounding == ROUND_FLOOR:
        step = 0 if sign > 0 else 1
    elif rounding == ROUND_CEILING:
        step = 1 if sign > 0 else 0
    elif rounding == ROUND_HALF_UP:
        step = 1 if twice >= den else 0
    elif rounding == ROUND_HALF_EVEN:
        if twice > den:
            step = 1
        elif twice < den:
            step = 0
        else:
            step = whole & 1  # tie -> round to even
    else:
        raise LegalNumberError(f"unknown rounding mode {rounding!r}")
    return sign * (whole + step)


def quantize(value: object, ndigits: int, *, rounding: str = DEFAULT_LEGAL_ROUNDING) -> Fraction:
    """Round the EXACT value of ``value`` to ``ndigits`` decimal places under
    ``rounding``, returning an exact :class:`~fractions.Fraction`. The rounding is
    performed on the exact rational (the tie is decided exactly), so it is free of
    any float representation error. ``ndigits`` may be negative (round to tens,
    hundreds, ...). ``rounding`` must be one of :data:`ROUNDING_MODES`."""
    if isinstance(ndigits, bool) or not isinstance(ndigits, int):
        raise LegalNumberError(f"ndigits must be an int, got {ndigits!r}")
    if rounding not in ROUNDING_MODES:
        raise LegalNumberError(f"unknown rounding mode {rounding!r}")
    exact = to_exact(value)
    scale = Fraction(10) ** ndigits
    rounded_int = _round_fraction_to_int(exact * scale, rounding)
    return Fraction(rounded_int) / scale


# ---------------------------------------------------------------------------
# Dimensional units
# ---------------------------------------------------------------------------
# Base dimensions used by the legal domain. A unit maps to a tuple of integer
# exponents (length, count). "Dimensionless" (FAR, ratio, percent) is all-zero.
_LENGTH = "length"
_COUNT = "count"

# unit label -> (length_exponent, count_exponent)
_UNIT_DIMENSION: dict[str | None, tuple[int, int]] = {
    None: (0, 0),
    "far": (0, 0),
    "ratio": (0, 0),
    "dimensionless": (0, 0),
    "percent": (0, 0),
    "feet": (1, 0),
    "foot": (1, 0),
    "ft": (1, 0),
    "square_feet": (2, 0),
    "sq_ft": (2, 0),
    "stories": (0, 1),
    "story": (0, 1),
    "dwelling_units": (0, 1),
    "dwelling_unit": (0, 1),
    "units": (0, 1),
}

KNOWN_UNITS = frozenset(u for u in _UNIT_DIMENSION if u is not None)
DIMENSIONLESS_UNITS = frozenset(
    u for u, dim in _UNIT_DIMENSION.items() if u is not None and dim == (0, 0)
)


def require_known_unit(unit: str | None) -> str | None:
    """Return ``unit`` if it is a recognized legal unit (or ``None`` =
    dimensionless), else fail closed with :class:`UnitError`. An unknown unit is
    rejected rather than silently treated as dimensionless."""
    if unit is None:
        return None
    if not isinstance(unit, str):
        raise UnitError(f"unit must be a string or None, got {type(unit).__name__}")
    if unit not in _UNIT_DIMENSION:
        raise UnitError(f"unknown unit {unit!r} (known: {sorted(KNOWN_UNITS)})")
    return unit


def dimension_of(unit: str | None) -> tuple[int, int]:
    """The (length, count) dimension exponents of a known unit; ``UnitError`` if
    unknown."""
    require_known_unit(unit)
    return _UNIT_DIMENSION[unit]


def units_compatible(unit_a: str | None, unit_b: str | None) -> bool:
    """True iff both units are known and share the same dimension. Same-dimension
    (not merely same-label) so ``feet`` and ``foot`` are compatible, while ``feet``
    and ``square_feet`` are not."""
    try:
        return dimension_of(unit_a) == dimension_of(unit_b)
    except UnitError:
        return False


def assert_compatible(unit_a: str | None, unit_b: str | None) -> None:
    """Raise :class:`UnitError` unless the two units share a dimension."""
    if dimension_of(unit_a) != dimension_of(unit_b):
        raise UnitError(f"incompatible units {unit_a!r} and {unit_b!r} (different dimensions)")


def _dimension_is_zero(unit: str | None) -> bool:
    return dimension_of(unit) == (0, 0)


@dataclass(frozen=True)
class Quantity:
    """An exact rational magnitude with a legal unit. Unit-aware arithmetic that
    fails closed on dimensionally incompatible operations. This is the frozen
    typed-unit foundation for future rule tasks; the DSL evaluator computes on
    bare exact rationals (the rule DSL does not annotate per-argument units), but
    a rule author with unit context can compose ``Quantity`` values to get exact
    dimensional checking for free.

    Add / subtract / compare require the SAME dimension (else ``UnitError``).
    Multiply / divide are supported only where the result dimension is
    unambiguous: scaling by a dimensionless factor keeps the unit, dividing equal
    units yields a dimensionless ratio; an unsupported dimensional product (e.g.
    ``feet * feet``) is rejected rather than guessing a derived unit."""

    value: Fraction
    unit: str | None

    @classmethod
    def of(cls, raw: object, unit: str | None) -> Quantity:
        """Build a Quantity from a raw value (canonicalized via :func:`to_exact`)
        and a validated known unit."""
        return cls(to_exact(raw), require_known_unit(unit))

    def __post_init__(self) -> None:
        # frozen dataclass: validate without reassigning through normal setattr.
        require_known_unit(self.unit)
        if not isinstance(self.value, Fraction):
            object.__setattr__(self, "value", to_exact(self.value))

    def _require_same_dimension(self, other: Quantity, verb: str) -> None:
        if dimension_of(self.unit) != dimension_of(other.unit):
            raise UnitError(
                f"cannot {verb} incompatible units {self.unit!r} and {other.unit!r}"
            )

    def __add__(self, other: Quantity) -> Quantity:
        self._require_same_dimension(other, "add")
        return Quantity(self.value + other.value, self.unit)

    def __sub__(self, other: Quantity) -> Quantity:
        self._require_same_dimension(other, "subtract")
        return Quantity(self.value - other.value, self.unit)

    def __mul__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        if _dimension_is_zero(other.unit):
            return Quantity(self.value * other.value, self.unit)
        if _dimension_is_zero(self.unit):
            return Quantity(self.value * other.value, other.unit)
        raise UnitError(
            f"unsupported unit product {self.unit!r} * {other.unit!r}: multiplying "
            "two dimensional units has no unambiguous legal unit (fail closed)"
        )

    def __truediv__(self, other: Quantity) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        if other.value == 0:
            raise LegalNumberError("division by zero quantity")
        if _dimension_is_zero(other.unit):
            return Quantity(self.value / other.value, self.unit)
        if dimension_of(self.unit) == dimension_of(other.unit):
            return Quantity(self.value / other.value, None)  # same units -> ratio
        raise UnitError(
            f"unsupported unit quotient {self.unit!r} / {other.unit!r}: no unambiguous "
            "legal unit (fail closed)"
        )

    def _compare(self, other: Quantity) -> tuple[Fraction, Fraction]:
        if not isinstance(other, Quantity):
            raise TypeError("Quantity can only be compared with another Quantity")
        self._require_same_dimension(other, "compare")
        return self.value, other.value

    def __lt__(self, other: Quantity) -> bool:
        a, b = self._compare(other)
        return a < b

    def __le__(self, other: Quantity) -> bool:
        a, b = self._compare(other)
        return a <= b

    def __gt__(self, other: Quantity) -> bool:
        a, b = self._compare(other)
        return a > b

    def __ge__(self, other: Quantity) -> bool:
        a, b = self._compare(other)
        return a >= b

    def equals(self, other: Quantity) -> bool:
        """Exact, unit-checked equality (``UnitError`` on incompatible units).
        Named method rather than ``__eq__`` so ``Quantity`` stays hashable and a
        cross-unit equality is a loud error, not a silent ``False``."""
        a, b = self._compare(other)
        return a == b

    def to_json_number(self) -> int | float:
        return to_json_number(self.value)
