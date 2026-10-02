"""The engine's as-of-right allowance, as an input to the existing-building flags (B-09).

The §8a "larger than today's rules" flag (plan section 5b) compares the existing zoning
floor area (B-05) with today's as-of-right zoning floor-area allowance. That allowance is
the engine's result (Lane A); this value object only carries it in, with its provenance, so
the flag layer can do the arithmetic without computing or interpreting any rule. A flag that
uses it keeps the provenance, so the number is never shown without its source.

Pure, deterministic code: no I/O, no legal logic.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

__all__ = ["AsOfRightAllowance"]


@dataclass(frozen=True)
class AsOfRightAllowance:
    """Today's as-of-right zoning floor-area allowance, from the engine.

    Attributes:
        value_sq_ft: the as-of-right zoning floor area, in square feet (a positive number).
        source: the provenance of the engine result (for example its rule version and the
            evaluation it came from). Carried through unchanged; this module reads nothing
            from it and derives nothing from it.
    """

    value_sq_ft: int | float
    source: Mapping[str, Any]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.value_sq_ft, int | float)
            or isinstance(self.value_sq_ft, bool)
            or not math.isfinite(self.value_sq_ft)
            or self.value_sq_ft < 0
        ):
            raise ValueError(
                f"value_sq_ft must be a non-negative number of square feet, got "
                f"{self.value_sq_ft!r}"
            )
        if not isinstance(self.source, Mapping) or not self.source:
            raise ValueError(
                "source must be a non-empty provenance mapping naming the engine result"
            )
