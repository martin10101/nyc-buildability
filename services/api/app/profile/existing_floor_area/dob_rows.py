"""Reading fields of recorded DOB rows as served (queue item B-05; plan M2-07).

SODA serves every column as text. These readers never coerce: a value that is not what the
column should hold is reported, not repaired. Shared by ``dob_filings`` (the figure) and
``scope`` (whether a figure is shown to describe one building).

Pure, deterministic code: no I/O.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

__all__ = ["BBL_PATTERN", "area", "format_area", "identity", "text"]

BBL_PATTERN = re.compile(r"^[1-5][0-9]{9}$")
_DIGITS = re.compile(r"^[0-9]+$")
_NUMBER = re.compile(r"^[0-9]+(\.[0-9]+)?$")
# NYC borough codes (the first digit of a BBL; PLUTO BoroCode).
_BOROUGH_CODES = {"MANHATTAN": "1", "BRONX": "2", "BROOKLYN": "3", "QUEENS": "4",
                  "STATEN ISLAND": "5"}


def text(value: Any) -> str | None:
    """Non-empty stripped text, or None."""
    return value.strip() if isinstance(value, str) and value.strip() else None


def format_area(value: int | float) -> str:
    return f"{value:,} sq ft"


def area(row: Mapping[str, Any], column: str) -> tuple[int | float | None, str | None]:
    """A positive square-foot figure, or (None, None) when the column states none (absent,
    empty or 0), or (None, problem) when it is not a number."""
    raw = row.get(column)
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, None
    if isinstance(raw, bool):
        return None, f"{column} {raw!r} is not a number"
    if isinstance(raw, int | float):
        number = float(raw)
    elif isinstance(raw, str) and _NUMBER.match(raw.strip()):
        number = float(raw.strip())
    else:
        return None, f"{column} {raw!r} is not a number"
    if not math.isfinite(number) or number < 0:
        return None, f"{column} {raw!r} is not a positive number"
    if number == 0:
        return None, None
    return (int(number) if number.is_integer() else number), None


def identity(row: Mapping[str, Any]) -> set[str]:
    """The BBLs a row names: its ``bbl`` column when that is a valid 10-digit BBL (the
    ic3t-wcy2 column can hold a BIN; ``docs/research/dob-legacy-sources.md`` section 3.1),
    and its borough/block/lot."""
    readings = set()
    bbl = text(row.get("bbl"))
    if bbl is not None and BBL_PATTERN.match(bbl):
        readings.add(bbl)
    borough = _BOROUGH_CODES.get((text(row.get("borough")) or "").upper())
    block, lot = text(row.get("block")), text(row.get("lot"))
    if (
        borough is not None and block is not None and lot is not None
        and _DIGITS.match(block) and _DIGITS.match(lot)
        and int(block) <= 99999 and int(lot) <= 9999
    ):
        readings.add(f"{borough}{int(block):05d}{int(lot):04d}")
    return readings
