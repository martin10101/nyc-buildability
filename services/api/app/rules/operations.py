"""Deterministic, family-agnostic operations for the rules DSL.

Two closed vocabularies, both pure and side-effect-free:

* COMPUTE_OPS - numeric operations used by a rule's ``computation.steps``.
* PREDICATE_OPS - boolean operations used by a rule's ``applicability`` /
  exception conditions.

There is NO string-expression parser and NO ``eval`` anywhere: a computation is
a list of structured steps, each naming one op and its already-resolved
arguments. This makes every calculation fully inspectable and reproducible, and
keeps the op set family-neutral - a FAR rule, a yard rule, and a height rule all
compose the same primitives, so a structurally different family is representable
with zero engine changes (only new rule DATA).

EXACT LEGAL ARITHMETIC (M4-T007 / DF-2 / B-014). Every numeric argument is
converted, at the op boundary, to an EXACT rational (:func:`units.to_exact`,
built from a canonical decimal string) and all arithmetic is performed on those
exact rationals. There is no binary IEEE-754 float on the legal value path and no
hidden intermediate rounding: an intermediate result stays exact until a rule
*explicitly* rounds it with the ``round`` op (documented mode + scale). Threshold
comparisons in :func:`_pred_compare` are likewise exact, so a legal equality at an
exact boundary (``0.1 + 0.2 == 0.3``) resolves deterministically. Callers that
serialize a result render it to a JSON number at the trace boundary via
:func:`units.to_json_number`; that render is the only place a value meets a float,
and it feeds no legal decision. Geometry (shapely) floats stay isolated in the
spatial layer and cross onto the legal path only through :func:`units.to_exact`.
"""

from __future__ import annotations

from collections.abc import Callable
from fractions import Fraction
from typing import Any

from . import units


class OperationError(ValueError):
    """Raised when an op receives the wrong arity or a non-numeric argument."""


def _nums(op: str, args: list[Any], *, n: int | None = None) -> list[Fraction]:
    """Arity-check ``args`` and convert each to an EXACT rational. A non-numeric or
    non-finite argument is surfaced as :class:`OperationError` (the evaluator turns
    it into a fail-closed EvaluationError), never a fabricated value."""
    if n is not None and len(args) != n:
        raise OperationError(f"op {op!r} expects {n} argument(s), got {len(args)}")
    out: list[Fraction] = []
    for a in args:
        try:
            out.append(units.to_exact(a))
        except units.LegalNumberError as exc:
            raise OperationError(
                f"op {op!r} requires numeric arguments, got {a!r} ({exc})"
            ) from exc
    return out


# --- numeric compute ops ---------------------------------------------------
# Each op returns an EXACT ``Fraction``; the evaluator keeps these exact for
# step-to-step chaining and renders them to JSON numbers only at the trace edge.

def _identity(args):
    (value,) = _nums("identity", args, n=1)
    return value


def _add(args):
    return sum(_nums("add", args), Fraction(0))


def _subtract(args):
    a, b = _nums("subtract", args, n=2)
    return a - b


def _multiply(args):
    out = Fraction(1)
    for v in _nums("multiply", args):
        out *= v
    return out


def _divide(args):
    a, b = _nums("divide", args, n=2)
    if b == 0:
        raise OperationError("division by zero")
    return a / b  # exact rational quotient (no context-precision rounding)


def _min(args):
    return min(_nums("min", args))


def _max(args):
    return max(_nums("max", args))


def _round(args):
    # round(value, ndigits) - ndigits is a numeric literal in the step, resolved
    # already. Rounding is EXACT (on the rational) with the documented default
    # legal mode (round half away from zero) at the declared scale.
    value, ndigits = _nums("round", args, n=2)
    if ndigits.denominator != 1:
        raise OperationError(f"round ndigits must be an integer, got {ndigits}")
    return units.quantize(value, int(ndigits), rounding=units.DEFAULT_LEGAL_ROUNDING)


def _clamp(args):
    value, low, high = _nums("clamp", args, n=3)
    if low > high:
        raise OperationError("clamp low > high")
    return min(max(value, low), high)


COMPUTE_OPS: dict[str, Callable[[list[Any]], Fraction]] = {
    "identity": _identity,
    "add": _add,
    "subtract": _subtract,
    "multiply": _multiply,
    "divide": _divide,
    "min": _min,
    "max": _max,
    "round": _round,
    "clamp": _clamp,
}


# --- boolean predicate ops -------------------------------------------------
# Each predicate receives the resolved left value and the predicate spec, and
# returns a bool. Predicates never raise on a missing value - a missing input is
# a completeness concern handled by the evaluator, not a truthiness error here.

def _pred_equals(value: Any, spec: dict) -> bool:
    return value == spec.get("value")


def _pred_in_set(value: Any, spec: dict) -> bool:
    return value in (spec.get("values") or [])


def _pred_exists(value: Any, spec: dict) -> bool:
    return value is not None


def _as_comparable(value: Any) -> Fraction | None:
    """Return the EXACT rational value of a genuinely numeric operand, or ``None``
    if it is not a comparable number. Mirrors the historical admissibility (a
    non-bool ``int``/``float`` only - a ``bool``, ``str``, ``None``, or non-finite
    value is *not* comparable), so the exactness upgrade changes no applicability
    outcome except to make a genuine numeric threshold compare exactly."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    try:
        return units.to_exact(value)
    except units.LegalNumberError:
        return None


def _pred_compare(value: Any, spec: dict) -> bool:
    """Numeric threshold comparison, performed on EXACT rationals so a legal
    boundary compares without float representation error. Fail-closed and total:
    a non-numeric / non-finite operand yields ``False`` (not comparable) and never
    raises - a missing/bad value is a completeness concern, not a truthiness
    error."""
    op = spec.get("compare")
    if op not in ("lt", "le", "gt", "ge", "eq", "ne"):
        raise OperationError(f"unknown compare operator {op!r}")
    left = _as_comparable(value)
    right = _as_comparable(spec.get("value"))
    if left is None or right is None:
        return False
    if op == "lt":
        return left < right
    if op == "le":
        return left <= right
    if op == "gt":
        return left > right
    if op == "ge":
        return left >= right
    if op == "eq":
        return left == right
    return left != right  # "ne"


PREDICATE_OPS: dict[str, Callable[[Any, dict], bool]] = {
    "equals": _pred_equals,
    "in_set": _pred_in_set,
    "exists": _pred_exists,
    "compare": _pred_compare,
}
