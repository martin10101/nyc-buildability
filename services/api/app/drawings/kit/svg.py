"""SVG written as text - deterministic formatting and small element builders.

Same input -> byte-identical output: numbers always carry two decimals
(``-0.00`` normalized), attributes keep the order they are given in, and
text is XML-escaped. No third-party library.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from .model import Point
from .styles import TYPOGRAPHY, ShapeStyle

__all__ = [
    "Attr",
    "attrs",
    "element",
    "escape",
    "num",
    "open_tag",
    "path_data",
    "polyline_data",
    "stroke_attrs",
    "svg_document",
    "text_element",
    "xml_illegal",
]

Attr = tuple[str, str | float | int | None]


def num(value: float) -> str:
    text = f"{value:.2f}"
    return "0.00" if text == "-0.00" else text


# Characters XML 1.0 forbids in a document: C0 controls other than tab, LF and
# CR; lone UTF-16 surrogates; U+FFFE and U+FFFF.
_XML_ILLEGAL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]")


def xml_illegal(text: str) -> bool:
    return _XML_ILLEGAL.search(text) is not None


def escape(text: str) -> str:
    """XML-escape ``text``; refuse characters XML cannot carry at all, so the
    SVG is always well-formed (the adapter refuses them earlier, typed)."""
    if xml_illegal(text):
        raise ValueError("text carries a character XML forbids")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def attrs(pairs: Iterable[Attr]) -> str:
    parts = []
    for name, value in pairs:
        if value is None:
            continue
        if isinstance(value, float):
            rendered = num(value)
        else:
            rendered = escape(str(value))
        parts.append(f' {name}="{rendered}"')
    return "".join(parts)


def element(tag: str, pairs: Iterable[Attr], content: str | None = None) -> str:
    if content is None:
        return f"<{tag}{attrs(pairs)}/>"
    return f"<{tag}{attrs(pairs)}>{content}</{tag}>"


def open_tag(tag: str, pairs: Iterable[Attr]) -> str:
    return f"<{tag}{attrs(pairs)}>"


def path_data(rings: Sequence[Sequence[Point]]) -> str:
    """Closed sub-paths, one per ring (drawing coordinates)."""
    parts = []
    for ring in rings:
        points = list(ring[:-1]) if len(ring) > 1 and ring[0] == ring[-1] else list(ring)
        head, *rest = points
        segs = [f"M{num(head[0])} {num(head[1])}"] + [f"L{num(x)} {num(y)}" for x, y in rest]
        parts.append(" ".join(segs) + " Z")
    return " ".join(parts)


def polyline_data(points: Sequence[Point]) -> str:
    head, *rest = points
    return " ".join([f"M{num(head[0])} {num(head[1])}"] + [f"L{num(x)} {num(y)}" for x, y in rest])


def stroke_attrs(style: ShapeStyle) -> list[Attr]:
    dash = " ".join(num(v) for v in style.dash_pt) if style.dash_pt else None
    return [
        ("stroke", style.outline),
        ("stroke-width", float(style.line_weight_pt)),
        ("stroke-dasharray", dash),
        ("stroke-linejoin", "round"),
    ]


def text_element(
    x: float,
    y: float,
    text: str,
    *,
    size: float,
    source: str | None,
    role: str,
    anchor: str = "start",
    rotate: float = 0.0,
    weight: str | None = None,
    style: str | None = None,
) -> str:
    """One ``<text>``; ``data-source`` names where its value came from."""
    transform = f"rotate({num(rotate)} {num(x)} {num(y)})" if rotate else None
    return element(
        "text",
        [
            ("x", float(x)),
            ("y", float(y)),
            ("font-size", float(size)),
            ("text-anchor", anchor),
            ("font-weight", weight),
            ("font-style", style),
            ("transform", transform),
            ("fill", "#111111"),
            ("data-role", role),
            ("data-source", source),
        ],
        escape(text),
    )


def svg_document(
    *, width: float, height: float, drawing: str, title: str, defs: str, body: Sequence[str]
) -> str:
    head = open_tag(
        "svg",
        [
            ("xmlns", "http://www.w3.org/2000/svg"),
            ("viewBox", f"0 0 {num(width)} {num(height)}"),
            ("width", float(width)),
            ("height", float(height)),
            ("font-family", TYPOGRAPHY.font_family),
            ("data-drawing", drawing),
            ("data-kit-version", "0"),
        ],
    )
    background = element(
        "rect", [("x", 0.0), ("y", 0.0), ("width", float(width)), ("height", float(height)),
                 ("fill", "#FFFFFF")],
    )
    lines = [head, element("title", [], escape(title)), f"<defs>{defs}</defs>", background]
    lines.extend(body)
    lines.append("</svg>")
    return "\n".join(lines) + "\n"
