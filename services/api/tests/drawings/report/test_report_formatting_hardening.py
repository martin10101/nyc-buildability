"""Hardening (DB-278): ``formatting._as_float`` returns ``None`` for inf/nan.

A single guard - ``return None`` when the float is not ``math.isfinite`` - makes
every report figure formatter treat a non-finite document value as MISSING
instead of crashing or printing garbage: ``format_int_commas`` no longer raises
``OverflowError``/``ValueError`` on ``int(inf)``/``int(nan)``, ``format_ratio``
no longer prints ``"inf.0"``/``"nan.0"``, ``format_sqft``/``format_feet`` degrade
to ``None``, and ``whole_percent_shares`` no longer crashes on ``int(inf)``.

One test per input state: finite ints and fractional floats stay byte-identical;
inf/-inf/nan each degrade to ``None``; ``whole_percent_shares`` with a non-finite
member returns ``None`` while a finite set is unchanged. The mutation proof
(remove the ``math.isfinite`` guard -> ``format_int_commas(inf)`` raises and
``format_ratio(inf) == "inf.0"``) is recorded in the producer report.
"""

from __future__ import annotations

import math

from app.drawings.report import formatting


def test_finite_values_are_byte_identical() -> None:
    """Finite ints and fractional floats format exactly as before the guard."""
    assert formatting.format_int_commas(20150.0) == "20,150"
    assert formatting.format_int_commas(6716.666) == "6,716.67"
    assert formatting.format_int_commas(0) == "0"
    assert formatting.format_ratio(2.0) == "2.0"
    assert formatting.format_ratio(2.4) == "2.4"
    assert formatting.format_sqft(20150.0) == "20,150 sq ft"
    assert formatting.format_feet(30.0) == "30 ft"
    assert formatting.format_feet(144.6) == "144.60 ft"
    assert formatting.format_measure(20150.0, "square_feet") == "20,150 sq ft"


def test_infinite_value_degrades_to_missing() -> None:
    """Positive and negative infinity become ``None`` (shown as missing), never a
    crash and never ``"inf.0"``."""
    for bad in (float("inf"), float("-inf")):
        assert formatting.format_int_commas(bad) is None
        assert formatting.format_ratio(bad) is None
        assert formatting.format_sqft(bad) is None
        assert formatting.format_feet(bad) is None
        assert formatting.format_measure(bad, "square_feet") is None
        assert formatting.format_measure(bad, "ratio") is None
        assert formatting.format_measure(bad, "feet") is None


def test_nan_value_degrades_to_missing() -> None:
    """NaN becomes ``None`` (shown as missing), never ``int(nan)`` ValueError."""
    nan = float("nan")
    assert formatting.format_int_commas(nan) is None
    assert formatting.format_ratio(nan) is None
    assert formatting.format_sqft(nan) is None
    assert formatting.format_feet(nan) is None
    assert formatting.format_measure(nan, "square_feet") is None


def test_whole_percent_shares_degrades_on_a_non_finite_member() -> None:
    """A non-finite share makes the whole set missing; a finite set is unchanged."""
    assert formatting.whole_percent_shares([float("inf"), 1.0]) is None
    assert formatting.whole_percent_shares([float("nan"), 1.0]) is None
    assert formatting.whole_percent_shares([1.0, float("-inf")]) is None
    # A finite set still re-rounds to whole percents summing to 100.
    assert formatting.whole_percent_shares([1.0, 1.0]) == [50, 50]
    assert sum(formatting.whole_percent_shares([2.0, 1.0, 1.0])) == 100


def test_non_numeric_and_none_still_missing() -> None:
    """The pre-existing non-numeric / None handling is unchanged (still missing),
    and a bool is still rejected as not-a-plain-number."""
    assert formatting.format_int_commas(None) is None
    assert formatting.format_int_commas("20150") is None
    assert formatting.format_int_commas(True) is None
    assert math.isfinite(1.0)  # sanity: the finite branch is exercised above
