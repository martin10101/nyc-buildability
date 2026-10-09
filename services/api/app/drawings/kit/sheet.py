"""Accumulator shared by the drawings: SVG parts, sourced labels, the boxes
already taken by labels (for collision-free placement), and the style kinds
drawn (which become the legend)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from .hatches import hatch_fill
from .labels import Box, first_free, text_box
from .model import Label
from .styles import style_for
from .svg import Attr, element, stroke_attrs, text_element

__all__ = ["Sheet"]


@dataclass
class Sheet:
    parts: list[str] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    boxes: list[Box] = field(default_factory=list)
    kinds: list[str] = field(default_factory=list)

    def use_kind(self, kind: str) -> None:
        style_for(kind)  # unknown kinds fail loudly
        if kind not in self.kinds:
            self.kinds.append(kind)

    def area(self, d: str, kind: str, extra: Iterable[Attr] = (), fill: str | None = None) -> None:
        """A filled outline in ``kind``'s style, with its hatch overlaid."""
        style = style_for(kind)
        self.use_kind(kind)
        extra = list(extra)
        self.parts.append(
            element("path", [("d", d), ("fill", fill or style.fill), ("fill-rule", "evenodd"),
                             *stroke_attrs(style), *extra])
        )
        paint = hatch_fill(kind)
        if paint:
            self.parts.append(
                element("path", [("d", d), ("fill", paint), ("fill-rule", "evenodd"),
                                 ("stroke", "none"), *extra])
            )

    def line(self, d: str, kind: str, extra: Iterable[Attr] = ()) -> None:
        self.use_kind(kind)
        self.parts.append(
            element("path", [("d", d), ("fill", "none"), *stroke_attrs(style_for(kind)), *extra])
        )

    def reserve(self, box: Box) -> None:
        self.boxes.append(box)

    def label(
        self,
        candidates: Sequence[tuple[float, float, float]],
        text: str,
        *,
        size: float,
        source: str,
        role: str,
        anchor: str = "start",
        style: str | None = None,
    ) -> Box:
        """Print ``text`` at the first candidate (x, y, rotation) whose box is
        free; record the label and its source."""
        boxes = [text_box(x, y, text, size, anchor, rot) for x, y, rot in candidates]
        index = first_free(boxes, self.boxes)
        x, y, rot = candidates[index]
        self.parts.append(
            text_element(x, y, text, size=size, source=source, role=role, anchor=anchor,
                         rotate=rot, style=style)
        )
        self.boxes.append(boxes[index])
        self.labels.append(Label(text, source, role))
        return boxes[index]
