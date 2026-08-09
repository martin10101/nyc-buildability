"""Deterministic normalized-value and stated-unit typing for survey facts (app-level; M2-T015).

Connects each canonical ``fact_type`` (:mod:`app.documents.taxonomy`) to the exact
``normalized_value`` shape and stated-unit vocabulary the deterministic checks can
consume: boundary segment distances and computed closures are numbers with a supported
distance unit; stated and calculated lot areas are numbers with a supported area unit;
bearings and north-arrow orientations are canonical decimal degrees in [0.0, 360.0);
elevations are finite numbers with a supported elevation unit; a scale statement is the
canonical dimensionless ``1:N`` ratio; address and BBL text are unitless strings.

NOTHING here changes the wire contract
(``packages/contracts/schemas/v1/survey_evidence.schema.json`` 1.0.0): no wire field,
type, or pattern moves. This module is the application-level authority on which
normalized-value shapes and stated units the deterministic implementation actually
accepts — exactly the role :mod:`app.documents.taxonomy` plays for ``fact_type``, whose
typed-result pattern (frozen value results, refusal-as-value, exact match only) it
reuses.

Fail-closed rule: a unit is NEVER silently coerced, inferred, defaulted, converted, or
guessed. A missing, ambiguous, mixed, misspelled, abbreviated, or unsupported unit —
and any normalized value whose shape does not match its fact type's rule — yields the
typed, visible :class:`UnresolvedNormalizedValue` RESULT — a value, deliberately not an
exception — carrying only the verbatim submission and a stated reason, and NO canonical
value or unit at all, so downstream code has nothing it could ever promote. Exact match
only: unit strings get no trimming, case-folding, or alias/abbreviation/symbol
interpretation, and a stated value is never converted between units (0.25 ``acres``
stays 0.25 ``acres``; wrapping a 380-degree bearing to 20 would be a silent coercion
and is refused instead). Normalizing an equivalent source form (e.g. ``1 inch = 20
feet`` into ``1:240``) is the extraction path's job, recorded with provenance — never
done here.
"""

from __future__ import annotations

import enum
import math
import re
from dataclasses import dataclass

from app.documents.models import BBL_PATTERN
from app.documents.taxonomy import (
    SurveyFactType,
    UnsupportedFactType,
    validate_fact_type,
)

__all__ = [
    "AngleUnit",
    "AreaUnit",
    "DistanceUnit",
    "ElevationUnit",
    "FACT_TYPES_WITHOUT_UNIT_RULE",
    "FACT_TYPES_WITH_UNIT_RULE",
    "NormalizedValueValidation",
    "SCALE_RATIO_PATTERN",
    "UnresolvedNormalizedValue",
    "ValidatedArea",
    "ValidatedBearing",
    "ValidatedDistance",
    "ValidatedElevation",
    "ValidatedScale",
    "ValidatedUnitlessText",
    "validate_normalized_value",
]

#: Canonical dimensionless scale form ``1:N`` (N a positive integer, no leading zero):
#: the only scale representation the ``scale_consistency`` check consumes.
SCALE_RATIO_PATTERN = re.compile(r"^1:[1-9][0-9]*$")


@enum.unique
class DistanceUnit(enum.Enum):
    """Closed set of stated distance units the deterministic checks consume.

    Deliberately minimal: NYC survey boundary dimensions are stated in decimal feet.
    Supporting a unit means the deterministic code consumes the value AS STATED — a
    stated unit outside this set is never converted or assumed; it fails closed to
    :class:`UnresolvedNormalizedValue` and routes to review. The set extends ADDITIVELY
    only, together with the deterministic code that grounds the new member (mirroring
    the taxonomy's extension rule).
    """

    FEET = "feet"


@enum.unique
class AreaUnit(enum.Enum):
    """Closed set of stated area units (NYC lot areas: square feet; acreage on larger
    parcels). Same as-stated, fail-closed, additive-extension rules as
    :class:`DistanceUnit` — never a conversion between members.
    """

    SQUARE_FEET = "square_feet"
    ACRES = "acres"


@enum.unique
class AngleUnit(enum.Enum):
    """Closed set of stated angle units for bearings and north-arrow orientations.

    The canonical representation is decimal degrees in [0.0, 360.0) with north at 0.0;
    quadrant prose (``N 45 E``) is an extraction-path source form, never accepted here.
    Same fail-closed and additive-extension rules as :class:`DistanceUnit`.
    """

    DEGREES = "degrees"


@enum.unique
class ElevationUnit(enum.Enum):
    """Closed set of stated elevation units (NYC survey elevations: feet against the
    survey's stated datum — the datum is provenance the ``elevation_consistency`` check
    reads, never assumed here). Same fail-closed and additive-extension rules as
    :class:`DistanceUnit`.
    """

    FEET = "feet"


# ------------------------------------------------------------------ typed results


@dataclass(frozen=True)
class ValidatedDistance:
    """Typed RESOLVED distance fact: the stated number with its stated distance unit,
    exactly as submitted — never converted."""

    fact_type: SurveyFactType
    value: int | float
    unit: DistanceUnit

    resolved = True


@dataclass(frozen=True)
class ValidatedArea:
    """Typed RESOLVED area fact: the stated number with its stated area unit,
    exactly as submitted — never converted."""

    fact_type: SurveyFactType
    value: int | float
    unit: AreaUnit

    resolved = True


@dataclass(frozen=True)
class ValidatedBearing:
    """Typed RESOLVED bearing/orientation fact: canonical decimal degrees in
    [0.0, 360.0), exactly as submitted — never wrapped or re-normalized."""

    fact_type: SurveyFactType
    value: int | float
    unit: AngleUnit

    resolved = True


@dataclass(frozen=True)
class ValidatedElevation:
    """Typed RESOLVED elevation fact: the stated finite number (any sign — elevations
    run below datum) with its stated elevation unit, exactly as submitted."""

    fact_type: SurveyFactType
    value: int | float
    unit: ElevationUnit

    resolved = True


@dataclass(frozen=True)
class ValidatedScale:
    """Typed RESOLVED scale statement: the canonical dimensionless ``1:N`` ratio.

    ``ratio_denominator`` is the deterministically parsed N of the already-canonical
    string — a lossless read, not a conversion.
    """

    fact_type: SurveyFactType
    ratio: str
    ratio_denominator: int

    resolved = True


@dataclass(frozen=True)
class ValidatedUnitlessText:
    """Typed RESOLVED unitless text fact (address or BBL): the string exactly as
    submitted, with no unit — because none may exist for it."""

    fact_type: SurveyFactType
    text: str

    resolved = True


@dataclass(frozen=True)
class UnresolvedNormalizedValue:
    """Typed refusal of a normalized value whose shape or unit cannot be resolved — a
    visible RESULT that can NEVER be promoted.

    Deliberately a value, not a ``DocumentIngestionError`` subclass and never raised:
    an ambiguous, mixed, missing, or unsupported unit (or a wrong-shape value) is a
    routine fail-closed outcome the caller must handle and surface — typed rejection,
    route to review — not a crash. The result carries ONLY the verbatim submission
    (``repr`` for non-wire shapes) and the stated reason: it has no canonical value, no
    resolved unit, and no conversion of any kind, so there is nothing downstream code
    could promote into a material buildability input. The payload is metadata only —
    mirroring the ``errors.py`` payload convention — and safe to serialize into an API
    response or audit record.
    """

    submitted_fact_type: str
    submitted_value: str
    submitted_unit: str | None
    reason: str

    resolved = False
    promotable = False
    reject_code = "unresolved_normalized_value"

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "reject_code": self.reject_code,
            "submitted_fact_type": self.submitted_fact_type,
            "submitted_value": self.submitted_value,
            "submitted_unit": self.submitted_unit,
            "reason": self.reason,
        }


NormalizedValueValidation = (
    ValidatedDistance
    | ValidatedArea
    | ValidatedBearing
    | ValidatedElevation
    | ValidatedScale
    | ValidatedUnitlessText
    | UnresolvedNormalizedValue
)


# ---------------------------------------------------------------------- helpers


def _unresolved(
    submitted_fact_type: str, value: object, unit: object, reason: str
) -> UnresolvedNormalizedValue:
    return UnresolvedNormalizedValue(
        submitted_fact_type=submitted_fact_type,
        submitted_value=repr(value),
        submitted_unit=unit if unit is None or isinstance(unit, str) else repr(unit),
        reason=reason,
    )


def _as_number(value: object, quantity: str, *, require_positive: bool) -> int | float | str:
    """The acceptable number itself, or the refusal reason string.

    The union discriminates cleanly: an acceptable value is never a ``str`` (a string
    number is refused — never parsed), so a ``str`` result is always the reason.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return (
            f"{quantity} normalized_value must be a number, got "
            f"{type(value).__name__} — a non-numeric shape is never coerced or parsed here"
        )
    if not math.isfinite(value):
        return f"{quantity} normalized_value must be a finite number, got {value!r}"
    if require_positive and value <= 0:
        return f"{quantity} must be strictly positive, got {value!r}"
    return value


def _match_unit[UnitT: enum.Enum](
    unit_enum: type[UnitT], unit: str | None, quantity: str
) -> UnitT | str:
    """The exactly matched unit member of one closed vocabulary, or the refusal reason.

    A missing unit is its own stated reason — it is never defaulted.
    """
    if unit is None:
        return (
            f"a {quantity} value requires an explicit stated unit; a missing unit is "
            "never defaulted or inferred"
        )
    try:
        return unit_enum(unit)
    except ValueError:
        supported = ", ".join(sorted(member.value for member in unit_enum))
        return (
            f"{unit!r} is not a supported {quantity} unit (supported: {supported}); "
            "exact match required — no alias, abbreviation, symbol, case, or "
            "whitespace interpretation, and never a unit conversion"
        )


# ------------------------------------------------------------------- per-rule


def _validate_distance(
    member: SurveyFactType, value: object, unit: str | None
) -> NormalizedValueValidation:
    number = _as_number(value, "a boundary distance", require_positive=True)
    if isinstance(number, str):
        return _unresolved(member.value, value, unit, number)
    resolved_unit = _match_unit(DistanceUnit, unit, "distance")
    if isinstance(resolved_unit, str):
        return _unresolved(member.value, value, unit, resolved_unit)
    return ValidatedDistance(fact_type=member, value=number, unit=resolved_unit)


def _validate_area(
    member: SurveyFactType, value: object, unit: str | None
) -> NormalizedValueValidation:
    number = _as_number(value, "a lot area", require_positive=True)
    if isinstance(number, str):
        return _unresolved(member.value, value, unit, number)
    resolved_unit = _match_unit(AreaUnit, unit, "area")
    if isinstance(resolved_unit, str):
        return _unresolved(member.value, value, unit, resolved_unit)
    return ValidatedArea(fact_type=member, value=number, unit=resolved_unit)


def _validate_bearing(
    member: SurveyFactType, value: object, unit: str | None
) -> NormalizedValueValidation:
    number = _as_number(value, "a bearing/orientation", require_positive=False)
    if isinstance(number, str):
        return _unresolved(member.value, value, unit, number)
    if not 0.0 <= number < 360.0:
        return _unresolved(
            member.value,
            value,
            unit,
            (
                "canonical bearing/orientation is decimal degrees in [0.0, 360.0) with "
                f"north at 0.0; {value!r} is outside that range and is never wrapped, "
                "reflected, or re-normalized here"
            ),
        )
    resolved_unit = _match_unit(AngleUnit, unit, "bearing/orientation")
    if isinstance(resolved_unit, str):
        return _unresolved(member.value, value, unit, resolved_unit)
    return ValidatedBearing(fact_type=member, value=number, unit=resolved_unit)


def _validate_elevation(
    member: SurveyFactType, value: object, unit: str | None
) -> NormalizedValueValidation:
    number = _as_number(value, "an elevation", require_positive=False)
    if isinstance(number, str):
        return _unresolved(member.value, value, unit, number)
    resolved_unit = _match_unit(ElevationUnit, unit, "elevation")
    if isinstance(resolved_unit, str):
        return _unresolved(member.value, value, unit, resolved_unit)
    return ValidatedElevation(fact_type=member, value=number, unit=resolved_unit)


def _validate_scale(
    member: SurveyFactType, value: object, unit: str | None
) -> NormalizedValueValidation:
    if not isinstance(value, str) or not SCALE_RATIO_PATTERN.fullmatch(value):
        return _unresolved(
            member.value,
            value,
            unit,
            (
                "a scale statement normalized_value must be the canonical dimensionless "
                "ratio string '1:N' (N a positive integer, e.g. '1:240'); an equivalent "
                "source form (e.g. '1 inch = 20 feet') is normalized by the extraction "
                "path with provenance, never inferred here"
            ),
        )
    if unit is not None:
        return _unresolved(
            member.value,
            value,
            unit,
            (
                "a scale statement is a dimensionless ratio and never carries a unit; a "
                "stated unit here is ambiguous and fails closed"
            ),
        )
    return ValidatedScale(
        fact_type=member, ratio=value, ratio_denominator=int(value.partition(":")[2])
    )


def _validate_address_text(
    member: SurveyFactType, value: object, unit: str | None
) -> NormalizedValueValidation:
    if not isinstance(value, str) or not value.strip():
        return _unresolved(
            member.value,
            value,
            unit,
            f"address_text normalized_value must be a non-empty string, got {value!r}",
        )
    if unit is not None:
        return _unresolved(
            member.value,
            value,
            unit,
            "address text is unitless; a stated unit here is ambiguous and fails closed",
        )
    return ValidatedUnitlessText(fact_type=member, text=value)


def _validate_bbl_text(
    member: SurveyFactType, value: object, unit: str | None
) -> NormalizedValueValidation:
    if not isinstance(value, str) or not BBL_PATTERN.fullmatch(value):
        return _unresolved(
            member.value,
            value,
            unit,
            (
                "bbl_text normalized_value must be the 10-digit NYC BBL string "
                f"(borough 1-5, common.schema.json#/$defs/bbl), got {value!r}; "
                "section/block/lot prose is never reformatted or inferred here"
            ),
        )
    if unit is not None:
        return _unresolved(
            member.value,
            value,
            unit,
            "BBL text is unitless; a stated unit here is ambiguous and fails closed",
        )
    return ValidatedUnitlessText(fact_type=member, text=value)


# ------------------------------------------------------------------- dispatch


_RULES = {
    SurveyFactType.BOUNDARY_SEGMENT_DISTANCE: _validate_distance,
    SurveyFactType.COMPUTED_CLOSURE: _validate_distance,
    SurveyFactType.STATED_LOT_AREA: _validate_area,
    SurveyFactType.CALCULATED_LOT_AREA: _validate_area,
    SurveyFactType.BOUNDARY_BEARING: _validate_bearing,
    SurveyFactType.NORTH_ARROW_ORIENTATION: _validate_bearing,
    SurveyFactType.ELEVATION_VALUE: _validate_elevation,
    SurveyFactType.SCALE_STATEMENT: _validate_scale,
    SurveyFactType.ADDRESS_TEXT: _validate_address_text,
    SurveyFactType.BBL_TEXT: _validate_bbl_text,
}

#: Fact types WITH a normalized-value/unit rule in this module.
FACT_TYPES_WITH_UNIT_RULE: frozenset[SurveyFactType] = frozenset(_RULES)

#: Fact types deliberately WITHOUT a unit rule here: the reconstructed polygon's
#: validity belongs to the ``geometry_validity`` deterministic check, not to unit
#: typing, so a unit-typing request for it always fails closed to review.
FACT_TYPES_WITHOUT_UNIT_RULE: frozenset[SurveyFactType] = frozenset(
    {SurveyFactType.RECONSTRUCTED_BOUNDARY_POLYGON}
)

# Additive-extension guard: a taxonomy member added without deciding its unit rule
# must fail here at import, never fall through silently at validation time.
_UNGOVERNED = frozenset(SurveyFactType) - FACT_TYPES_WITH_UNIT_RULE - FACT_TYPES_WITHOUT_UNIT_RULE
if _UNGOVERNED:
    raise RuntimeError(
        "every SurveyFactType member needs a normalized-value/unit rule or an explicit "
        "FACT_TYPES_WITHOUT_UNIT_RULE entry; ungoverned: "
        + ", ".join(sorted(member.value for member in _UNGOVERNED))
    )


def validate_normalized_value(
    fact_type: str, normalized_value: object, unit: object
) -> NormalizedValueValidation:
    """Validate one fact's ``normalized_value`` shape and stated unit for its ``fact_type``.

    ``unit`` is the stated wire unit string, or ``None`` when the submission states
    none — the parameter deliberately has NO default, so a caller must state even the
    absence of a unit explicitly. Returns the rule's typed RESOLVED result when the
    shape and unit exactly match the fact type's rule, else the typed
    :class:`UnresolvedNormalizedValue`. Never raises — every malformed, ambiguous,
    mixed, missing, or unsupported submission becomes the typed refusal, so no
    unresolved value or unit can crash ingestion or slip through as a material
    buildability input.
    """
    fact_type_result = validate_fact_type(fact_type)
    if isinstance(fact_type_result, UnsupportedFactType):
        return _unresolved(
            fact_type_result.submitted_fact_type,
            normalized_value,
            unit,
            f"fact_type refused by the canonical taxonomy: {fact_type_result.reason}",
        )
    member = fact_type_result.fact_type
    if unit is not None and not isinstance(unit, str):
        return _unresolved(
            member.value,
            normalized_value,
            unit,
            (
                "unit must be the stated wire unit string or None, got "
                f"{type(unit).__name__} — a non-string unit cannot be matched exactly"
            ),
        )
    rule = _RULES.get(member)
    if rule is None:
        return _unresolved(
            member.value,
            normalized_value,
            unit,
            (
                f"no normalized-value/unit rule is grounded for {member.value!r} in "
                "this module: the reconstructed polygon's validity belongs to the "
                "geometry_validity deterministic check, so unit typing fails closed "
                "here and routes to review"
            ),
        )
    return rule(member, normalized_value, unit)
