"""SVG ``<pattern>`` definitions built from the style table's hatch specs."""

from __future__ import annotations

from collections.abc import Iterable

from .styles import ShapeStyle, style_for
from .svg import element, num

__all__ = ["hatch_defs", "hatch_fill"]


def hatch_fill(kind: str) -> str | None:
    """``url(#...)`` paint for ``kind``'s hatch overlay, or None when unhatched."""
    return f"url(#hatch-{kind})" if style_for(kind).hatch else None


def _pattern(style: ShapeStyle) -> str:
    hatch = style.hatch
    assert hatch is not None
    s = hatch.spacing_pt
    line_attrs = [("stroke", hatch.color), ("stroke-width", float(hatch.line_weight_pt))]
    lines = [element("line", [("x1", 0.0), ("y1", s / 2), ("x2", s), ("y2", s / 2), *line_attrs])]
    if hatch.crossed:
        lines.append(
            element("line", [("x1", s / 2), ("y1", 0.0), ("x2", s / 2), ("y2", s), *line_attrs])
        )
    # CAD angles run counter-clockwise with y up; SVG y points down, so negate.
    return element(
        "pattern",
        [
            ("id", f"hatch-{style.kind}"),
            ("patternUnits", "userSpaceOnUse"),
            ("width", float(s)),
            ("height", float(s)),
            ("patternTransform", f"rotate({num(-float(hatch.angle_deg))})"),
        ],
        "".join(lines),
    )


def hatch_defs(kinds: Iterable[str]) -> str:
    """Pattern definitions for the hatched kinds among ``kinds`` (deduplicated,
    in first-seen order)."""
    seen: list[str] = []
    for kind in kinds:
        if kind not in seen and style_for(kind).hatch is not None:
            seen.append(kind)
    return "".join(_pattern(style_for(kind)) for kind in seen)
