"""Label text formatting and collision boxes (plan section 5c item 5).

Every number printed on a drawing goes through :func:`format_number`, so the
tests can parse it back and compare it with the results (check C-4). Labels
are placed so they do not overlap: callers try candidate positions in a
fixed order and keep the first whose box is free (deterministic).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .styles import TYPOGRAPHY

__all__ = [
    "YARD_KIND_NAMES",
    "Box",
    "first_free",
    "format_area",
    "format_feet",
    "format_number",
    "text_box",
]

# Display names of the results' yard ``kind`` enum.
YARD_KIND_NAMES = {"front": "Front yard", "side": "Side yard", "rear": "Rear yard"}


def format_number(value: float) -> str:
    """At most two decimals, trailing zeros dropped, thousands separated."""
    text = f"{value:,.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def format_feet(value: float) -> str:
    return f"{format_number(value)} ft"


def format_area(value: float) -> str:
    return f"{format_number(value)} sf"


@dataclass(frozen=True)
class Box:
    x0: float
    y0: float
    x1: float
    y1: float

    def overlaps(self, other: Box, pad: float = 1.0) -> bool:
        return not (
            self.x1 + pad <= other.x0
            or other.x1 + pad <= self.x0
            or self.y1 + pad <= other.y0
            or other.y1 + pad <= self.y0
        )


def text_box(
    x: float, y: float, text: str, size: float, anchor: str = "start", rotate: float = 0.0
) -> Box:
    """Conservative axis-aligned box of a (possibly rotated) text line whose
    baseline starts, centers or ends at (x, y)."""
    width = len(text) * size * TYPOGRAPHY.char_width_em
    left = {"start": 0.0, "middle": -width / 2.0, "end": -width}[anchor]
    corners = [(left, -0.8 * size), (left + width, -0.8 * size),
               (left, 0.25 * size), (left + width, 0.25 * size)]
    angle = math.radians(rotate)
    cos, sin = math.cos(angle), math.sin(angle)
    xs = [x + cx * cos - cy * sin for cx, cy in corners]
    ys = [y + cx * sin + cy * cos for cx, cy in corners]
    return Box(min(xs), min(ys), max(xs), max(ys))


def first_free(candidates: Sequence[Box], placed: Sequence[Box]) -> int:
    """Index of the first candidate overlapping nothing placed (else the last)."""
    for index, box in enumerate(candidates):
        if not any(box.overlaps(other) for other in placed):
            return index
    return len(candidates) - 1
