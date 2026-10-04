"""Typed, validated view of the results ``geometry`` block the kit draws from.

Built only by :func:`app.drawings.kit.adapter.load_drawing_input`. Every value
keeps ``source`` - the JSON pointer (RFC 6901) of where it came from in the
results document - so each printed label can be traced back to the results
(checks C-4 and C-5). All coordinates are in feet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scope import ScopeView

__all__ = [
    "CaseAssumption",
    "Drawing",
    "DrawingInput",
    "EnvelopeTier",
    "FloorPlate",
    "FloorRow",
    "Label",
    "LayerUnavailable",
    "Point",
    "Polygon",
    "Ring",
    "SetbackLine",
    "Street",
    "StreetWidthCase",
    "Unavailable",
    "Yard",
    "YardNotRequired",
]

Point = tuple[float, float]
Ring = tuple[Point, ...]


@dataclass(frozen=True)
class Polygon:
    """Exterior ring first, then any holes; every ring closed (first == last)."""

    rings: tuple[Ring, ...]
    source: str

    @property
    def exterior(self) -> Ring:
        return self.rings[0]

    @property
    def holes(self) -> tuple[Ring, ...]:
        return self.rings[1:]


@dataclass(frozen=True)
class Street:
    name: str
    frontage: tuple[Point, ...]
    source: str


@dataclass(frozen=True)
class Yard:
    kind: str  # front | side | rear
    depth_ft: float
    outline: Polygon
    source: str


@dataclass(frozen=True)
class YardNotRequired:
    kind: str
    reason: str
    source: str


@dataclass(frozen=True)
class LayerUnavailable:
    """A rule-dependent layer the results mark not_available, with its reason."""

    layer: str
    reason: str
    reason_kind: str
    source: str


@dataclass(frozen=True)
class SetbackLine:
    floor: int
    lines: tuple[tuple[Point, ...], ...]
    source: str


@dataclass(frozen=True)
class EnvelopeTier:
    """One tier of the permitted envelope: ``outline`` extruded from
    ``bottom_ft`` to ``top_ft`` above grade (results geometry.envelope)."""

    bottom_ft: float
    top_ft: float
    outline: Polygon
    source: str


@dataclass(frozen=True)
class FloorPlate:
    floor: int
    use: str
    gross_sf: float
    outline: Polygon
    source: str


@dataclass(frozen=True)
class FloorRow:
    floor: int
    label: str
    gross_sf: float
    height_ft: float
    use: str
    source: str


@dataclass(frozen=True)
class CaseAssumption:
    street: str
    assumed: str  # wide | narrow
    source: str


@dataclass(frozen=True)
class StreetWidthCase:
    """These results are ONE case of the plan section 4 "Needs street width"
    side-by-side set; every drawing of them says so."""

    marker: str
    assumptions: tuple[CaseAssumption, ...]
    source: str


@dataclass(frozen=True)
class DrawingInput:
    """Everything the site plan, massing and DXF need, validated and fail-closed."""

    crs: str
    measurement_label: str
    lot: Polygon
    streets: tuple[Street, ...]
    yards: tuple[Yard, ...] | LayerUnavailable
    yards_not_required: tuple[YardNotRequired, ...]
    setback_lines: tuple[SetbackLine, ...] | LayerUnavailable
    envelope: tuple[EnvelopeTier, ...] | LayerUnavailable
    floor_plates: tuple[FloorPlate, ...] | LayerUnavailable
    floor_rows: tuple[FloorRow, ...]
    street_width_case: StreetWidthCase | None
    scope: ScopeView | None = None


@dataclass(frozen=True)
class Unavailable:
    """A drawing that cannot be made, with the one line that names what is missing
    (plan M1-16). ``reason`` is the results' own reason wherever the results
    give one (``source`` points to it)."""

    drawing: str
    reason: str
    reason_kind: str
    source: str


@dataclass(frozen=True)
class Label:
    """One printed text and where its value came from.

    ``source`` grammar: ``/json/pointer`` (the value at that pointer of the
    results document), ``edge:/pointer/to/ring#i`` (length of edge i of that
    ring - dimensions are computed from the geometry, never typed), or
    ``scale`` (scale-bar furniture).
    """

    text: str
    source: str
    role: str


@dataclass(frozen=True)
class Drawing:
    """A finished vector drawing: the SVG text, every sourced label printed on
    it, and the style kinds actually drawn (the legend's content)."""

    drawing: str
    svg: str
    labels: tuple[Label, ...]
    kinds_drawn: tuple[str, ...]
