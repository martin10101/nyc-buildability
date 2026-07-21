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

Determinism note: floating-point results are rounded to 10 decimal places at
each step so the same inputs always yield byte-identical traces across
platforms; rules needing a specific legal rounding declare it explicitly with
the ``round`` op.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_QUANT = 10  # internal determinism rounding (not a legal rounding)


class OperationError(ValueError):
    """Raised when an op receives the wrong arity or a non-numeric argument."""


def _nums(op: str, args: list[Any], *, n: int | None = None) -> list[float]:
    if n is not None and len(args) != n:
        raise OperationError(f"op {op!r} expects {n} argument(s), got {len(args)}")
    out = []
    for a in args:
        if isinstance(a, bool) or not isinstance(a, int | float):
            raise OperationError(f"op {op!r} requires numeric arguments, got {a!r}")
        out.append(float(a))
    return out


def _q(value: float) -> float:
    return round(value, _QUANT)


# --- numeric compute ops ---------------------------------------------------

def _identity(args):
    (value,) = _nums("identity", args, n=1)
    return _q(value)


def _add(args):
    return _q(sum(_nums("add", args)))


def _subtract(args):
    a, b = _nums("subtract", args, n=2)
    return _q(a - b)


def _multiply(args):
    vals = _nums("multiply", args)
    out = 1.0
    for v in vals:
        out *= v
    return _q(out)


def _divide(args):
    a, b = _nums("divide", args, n=2)
    if b == 0:
        raise OperationError("division by zero")
    return _q(a / b)


def _min(args):
    return _q(min(_nums("min", args)))


def _max(args):
    return _q(max(_nums("max", args)))


def _round(args):
    # round(value, ndigits) - ndigits is a literal in the step, resolved already.
    value, ndigits = _nums("round", args, n=2)
    return _q(round(value, int(ndigits)))


def _clamp(args):
    value, low, high = _nums("clamp", args, n=3)
    if low > high:
        raise OperationError("clamp low > high")
    return _q(min(max(value, low), high))


COMPUTE_OPS: dict[str, Callable[[list[Any]], float]] = {
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


def _pred_compare(value: Any, spec: dict) -> bool:
    op = spec.get("compare")
    other = spec.get("value")
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    if isinstance(other, bool) or not isinstance(other, int | float):
        return False
    if op == "lt":
        return value < other
    if op == "le":
        return value <= other
    if op == "gt":
        return value > other
    if op == "ge":
        return value >= other
    if op == "eq":
        return value == other
    if op == "ne":
        return value != other
    raise OperationError(f"unknown compare operator {op!r}")


PREDICATE_OPS: dict[str, Callable[[Any, dict], bool]] = {
    "equals": _pred_equals,
    "in_set": _pred_in_set,
    "exists": _pred_exists,
    "compare": _pred_compare,
}
