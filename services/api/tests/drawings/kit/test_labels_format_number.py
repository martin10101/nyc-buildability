"""Hardening (DB-278): ``kit.labels.format_number`` fails closed on a non-numeric
or non-finite value.

Every number printed on a drawing goes through ``format_number``. Before the
guard a ``str``/``None`` raised the cryptic "Unknown format code 'f' for object
of type 'str'" and a non-finite value rendered as literal "inf"/"nan" label text
("inf sq ft, map outline"). The guard rejects a bool, a non-``(int, float)`` and
a non-finite value with a ``ValueError`` (fails closed). This also covers
``close_frame_dimensions._fact_figure``, which formats through ``format_number``,
with NO edit to the NB-04-pinned close-frame module.

One test per input state: finite reals (incl. ``-0.0`` and a thousands value)
stay byte-identical; inf/-inf/nan/str/None/bool each raise ``ValueError``. The
mutation proof (remove the guard -> ``inf`` renders "inf" and ``"abc"`` raises
the cryptic format-code error) is recorded in the producer report.
"""

from __future__ import annotations

import pytest

from app.drawings.kit.labels import format_number


def test_finite_reals_are_byte_identical() -> None:
    """Finite ints and floats format exactly as before the guard."""
    assert format_number(1234.5) == "1,234.5"
    assert format_number(20150.0) == "20,150"
    assert format_number(144.6) == "144.6"
    assert format_number(0.0) == "0"
    assert format_number(-0.0) == "0"
    assert format_number(2) == "2"
    assert format_number(-3.25) == "-3.25"


def test_non_finite_value_fails_closed() -> None:
    """inf / -inf / nan raise ``ValueError`` instead of rendering "inf"/"nan"."""
    for bad in (float("inf"), float("-inf"), float("nan")):
        with pytest.raises(ValueError):
            format_number(bad)


def test_non_numeric_value_fails_closed() -> None:
    """A str / None / non-number raises ``ValueError`` instead of the cryptic
    "Unknown format code 'f'" error."""
    for bad in ("abc", None, [1.0], {}):
        with pytest.raises(ValueError):
            format_number(bad)  # type: ignore[arg-type]


def test_bool_is_rejected() -> None:
    """A bool is not a plain number here and fails closed (it would otherwise
    format as 1/0)."""
    with pytest.raises(ValueError):
        format_number(True)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        format_number(False)  # type: ignore[arg-type]
