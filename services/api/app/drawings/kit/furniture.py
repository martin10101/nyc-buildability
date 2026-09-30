"""Drawing furniture: north arrow, scale bar, legend and notes.

The legend is generated from the kinds actually drawn (plan section 5c item
5), in style-table order. Notes print text read from the results (each note
carries its ``data-source``), wrapped to the panel width.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .hatches import hatch_fill
from .labels import format_number
from .model import Label, StreetWidthCase
from .styles import AREA, STYLE_TABLE, TYPOGRAPHY, style_for
from .svg import attrs, element, escape, num, open_tag, stroke_attrs, text_element

__all__ = [
    "SCALE_BAR_LENGTHS_FT",
    "Note",
    "case_notes",
    "legend",
    "north_arrow",
    "notes_block",
    "scale_bar",
]

# Candidate scale-bar lengths (feet); the longest that fits is used.
SCALE_BAR_LENGTHS_FT = (2, 4, 5, 10, 20, 40, 50, 100, 200, 400, 500, 1000, 2000, 4000, 5000)

_LEGEND_ROW = 16.0
_NOTE_LINE = 10.0


def north_arrow(cx: float, top: float) -> list[str]:
    """Arrow to grid north (+y of the results' CRS, which the schema defines as
    EPSG:2263 grid north for both ``local_feet`` and ``EPSG:2263``)."""
    tip, base = top + 10.0, top + 46.0
    arrow = element(
        "path",
        [
            ("d", f"M{num(cx)} {num(tip)} L{num(cx + 7)} {num(base)} "
                  f"L{num(cx)} {num(base - 9)} L{num(cx - 7)} {num(base)} Z"),
            ("fill", "#000000"),
            ("stroke", "#000000"),
            ("stroke-width", 0.5),
        ],
    )
    size = TYPOGRAPHY.label_pt
    return [
        '<g data-role="north-arrow">',
        arrow,
        text_element(cx, top + 6.0, "N", size=size + 2, source=None, role="furniture",
                     anchor="middle", weight="bold"),
        text_element(cx + 14.0, base - 4.0, "Grid north", size=size, source=None,
                     role="furniture"),
        "</g>",
    ]


def scale_bar(
    x0: float, top: float, px_per_ft: float, max_px: float
) -> tuple[list[str], list[Label]]:
    """Two-segment bar of the longest candidate length that fits ``max_px``."""
    length = SCALE_BAR_LENGTHS_FT[0]
    for candidate in SCALE_BAR_LENGTHS_FT:
        if candidate * px_per_ft <= max_px:
            length = candidate
    half = length / 2.0
    seg = half * px_per_ft
    size = TYPOGRAPHY.note_pt
    parts = [
        open_tag("g", [("data-role", "scale-bar"), ("data-x0", float(x0)),
                       ("data-px-per-ft", f"{px_per_ft:.6f}")]),
        element("rect", [("x", float(x0)), ("y", float(top)), ("width", seg), ("height", 5.0),
                         ("fill", "#000000"), ("stroke", "#000000"), ("stroke-width", 0.5)]),
        element("rect", [("x", x0 + seg), ("y", float(top)), ("width", seg), ("height", 5.0),
                         ("fill", "#FFFFFF"), ("stroke", "#000000"), ("stroke-width", 0.5)]),
    ]
    labels: list[Label] = []
    for value, text in ((0.0, "0"), (half, format_number(half)),
                        (float(length), f"{format_number(length)} ft")):
        parts.append(text_element(x0 + value * px_per_ft, top + 15.0, text, size=size,
                                  source="scale", role="scale", anchor="middle"))
        labels.append(Label(text, "scale", "scale"))
    parts.append("</g>")
    return parts, labels


def _swatch(kind: str, x: float, y: float) -> list[str]:
    style = style_for(kind)
    if style.geometry == AREA:
        rect = [("x", x), ("y", y), ("width", 18.0), ("height", 10.0)]
        out = [element("rect", [*rect, ("fill", style.fill), *stroke_attrs(style)])]
        paint = hatch_fill(kind)
        if paint:
            out.append(element("rect", [*rect, ("fill", paint), ("stroke", "none")]))
        return out
    return [element("line", [("x1", x), ("y1", y + 5.0), ("x2", x + 18.0), ("y2", y + 5.0),
                             *stroke_attrs(style)])]


def legend(kinds_drawn: Sequence[str], x: float, top: float) -> tuple[list[str], float]:
    """Legend rows for the drawn kinds (table order); returns parts and bottom y."""
    shown = [s for s in STYLE_TABLE if s.in_legend and s.kind in kinds_drawn]
    parts = ['<g data-role="legend">',
             text_element(x, top + 8.0, "Legend", size=TYPOGRAPHY.label_pt, source=None,
                          role="furniture", weight="bold")]
    y = top + 14.0
    for style in shown:
        parts.extend(_swatch(style.kind, x, y))
        parts.append(text_element(x + 24.0, y + 8.5, style.label, size=TYPOGRAPHY.label_pt,
                                  source=None, role="legend"))
        y += _LEGEND_ROW
    parts.append("</g>")
    return parts, y


@dataclass(frozen=True)
class Note:
    """One note line made of parts: ``(text, source)`` read from the results, or
    ``(text, None)`` literal words, which never carry a number."""

    parts: tuple[tuple[str, str | None], ...]

    def __post_init__(self) -> None:
        for text, source in self.parts:
            if source is None and any(ch.isdigit() for ch in text):
                raise ValueError("a literal note part must not carry numbers")


def _runs(words: list[tuple[str, str | None]]) -> list[tuple[str, str | None]]:
    """Consecutive words of the same part, joined."""
    runs: list[tuple[str, str | None]] = []
    for word, source in words:
        if runs and runs[-1][1] == source:
            runs[-1] = (runs[-1][0] + " " + word, source)
        else:
            runs.append((word, source))
    return runs


def _wrap(note: Note, chars: int) -> list[list[tuple[str, str | None]]]:
    """Greedy word wrap that remembers which part each word came from."""
    lines: list[list[tuple[str, str | None]]] = [[]]
    length = 0
    for text, source in note.parts:
        for word in text.split():
            extra = len(word) + (1 if lines[-1] else 0)
            if lines[-1] and length + extra > chars:
                lines.append([])
                length, extra = 0, len(word)
            lines[-1].append((word, source))
            length += extra
    return [_runs(line) for line in lines if line]


def _tspan(text: str, source: str | None, x: float | None, dy: float | None) -> str:
    pairs = [("x", x), ("dy", dy), ("data-source", source)]
    return f"<tspan{attrs(pairs)}>{escape(text)}</tspan>"


def notes_block(
    notes: Sequence[Note], x: float, top: float, width: float
) -> tuple[list[str], list[Label], float]:
    """Wrapped notes: one ``<text>`` per note, one ``<tspan>`` per run of a part
    on a line; every sourced run names its source."""
    if not notes:
        return [], [], top
    size = TYPOGRAPHY.note_pt
    chars = max(12, int(width / (size * TYPOGRAPHY.char_width_em)))
    parts = ['<g data-role="notes">',
             text_element(x, top + 8.0, "Notes", size=TYPOGRAPHY.label_pt, source=None,
                          role="furniture", weight="bold")]
    labels: list[Label] = []
    y = top + 20.0
    for note in notes:
        lines = _wrap(note, chars)
        spans = []
        for i, runs in enumerate(lines):
            for j, (text, source) in enumerate(runs):
                last = j == len(runs) - 1
                spans.append(_tspan(text if last else text + " ", source,
                                    float(x) if j == 0 else None,
                                    (0.0 if i == 0 else _NOTE_LINE) if j == 0 else None))
        parts.append(f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}" '
                     f'fill="#111111" data-role="note">{"".join(spans)}</text>')
        labels.extend(Label(" ".join(text.split()), source, "note")
                      for text, source in note.parts if source is not None)
        y += _NOTE_LINE * len(lines) + 4.0
    parts.append("</g>")
    return parts, labels, y


def case_notes(case: StreetWidthCase | None) -> list[Note]:
    """For one case of a "Needs street width" set: the marker, then each
    street's assumed width class (plan section 4), read from the results."""
    if case is None:
        return []
    notes = [Note(((case.marker, f"{case.source}/marker"),))]
    for assumption in case.assumptions:
        notes.append(Note(((assumption.street, f"{assumption.source}/street"),
                           ("width assumed", None),
                           (assumption.assumed, f"{assumption.source}/assumed"))))
    return notes
