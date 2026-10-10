"""The drawing interface (ruling X9).

The report asks the drawing kit and the maps for report-frame drawings through
``frame="report"``. M5-T152 adds that keyword and ``render_floor_stack`` in
parallel, so this module calls the interface defensively: if the keyword or the
function is missing, or the kit is disabled, the page prints one short line
instead of a drawing. A kit :class:`Unavailable` becomes its own one-line reason.
The allowance bar chart is the report's OWN presentation SVG (a simple bar is
presentation, not law); every figure on it is read from the document.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping
from dataclasses import dataclass, field
from xml.sax.saxutils import escape as _xml_escape

__all__ = [
    "Embedded",
    "allowance_bar_chart_svg",
    "embed_floor_stack",
    "embed_kit_drawing",
    "embed_map",
]


@dataclass(frozen=True)
class Embedded:
    """A drawing ready to place, or a short line to print in its place."""

    svg: str | None = None
    caption: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)
    attribution: str | None = None
    short_line: str | None = None

    @property
    def is_drawing(self) -> bool:
        return self.svg is not None


def _frame_supported(fn: object) -> bool:
    try:
        return "frame" in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def _from_result(result: object) -> Embedded:
    if hasattr(result, "svg"):
        return Embedded(
            svg=getattr(result, "svg", None),
            caption=getattr(result, "caption", None),
            notes=tuple(getattr(result, "notes", ()) or ()),
            attribution=getattr(result, "attribution", None),
        )
    reason = getattr(result, "reason", None)
    return Embedded(short_line=str(reason) if reason else "This drawing is not shown here.")


def _call(module, fn_name: str, arg, env, missing_line: str) -> Embedded:
    fn = getattr(module, fn_name, None)
    if fn is None or not _frame_supported(fn):
        return Embedded(short_line=missing_line)
    try:
        result = fn(arg, frame="report", env=env)
    except Exception:  # noqa: BLE001 - any kit failure means no drawing, never an error page
        return Embedded(short_line=missing_line)
    return _from_result(result)


def embed_kit_drawing(fn_name: str, results: Mapping, *, env=None) -> Embedded:
    """A drawing-kit drawing (site plan, massing) at the report frame."""
    from app.drawings import kit

    return _call(kit, fn_name, results, env, "This drawing is not shown here.")


def embed_floor_stack(alternative: Mapping, *, env=None) -> Embedded:
    """The floor-stack section for one worked building (``render_floor_stack``)."""
    from app.drawings import kit

    return _call(
        kit, "render_floor_stack", alternative, env,
        "The floor-stack section is not shown here.",
    )


def embed_map(fn_name: str, map_context: Mapping, *, env=None) -> Embedded:
    """A location or zoning map at the report frame."""
    from app.drawings import maps

    return _call(maps, fn_name, map_context, env, "This map is not shown here.")


def allowance_bar_chart_svg(
    allowance_display: str | None,
    allowance_value: float | None,
    buildings: list[dict],
) -> str | None:
    """A compact horizontal bar chart: the floor-area allowance against each
    worked building's scheduled area, on one scale. Returns ``None`` when there is
    nothing to draw. Every printed number is a document figure passed in."""
    bars = [b for b in buildings if isinstance(b.get("scheduled_value"), (int, float))]
    if not bars or not isinstance(allowance_value, (int, float)) or allowance_value <= 0:
        return None
    scale = max([allowance_value, *[b["scheduled_value"] for b in bars]])
    if scale <= 0:
        return None
    track = 300.0
    rows = []
    y = 6
    # The allowance reference line, full scale.
    allowance_text = f"{allowance_display} sq ft" if allowance_display else ""
    rows.append(_bar(y, track, "Floor-area allowance", allowance_text, allowance_value, scale))
    y += 22
    for b in bars:
        name = f"Building {b.get('building')}" if b.get("building") else "Worked building"
        label = b.get("scheduled_display")
        text = f"{label} sq ft" if label else ""
        rows.append(_bar(y, track, name, text, b["scheduled_value"], scale))
        y += 22
    height = y + 4
    body = "".join(rows)
    return (
        f'<svg class="bar-chart" viewBox="0 0 460 {height}" '
        f'role="img" width="460" height="{height}">{body}</svg>'
    )


def _bar(y: int, track: float, name: str, value_text: str, value: float, scale: float) -> str:
    width = max(1.0, track * (value / scale))
    name_s = _xml_escape(name)
    value_s = _xml_escape(value_text)
    return (
        f'<text x="0" y="{y + 9}">{name_s}</text>'
        f'<rect x="140" y="{y}" width="{width:.1f}" height="12" fill="#18577A"></rect>'
        f'<text x="{140 + width + 4:.1f}" y="{y + 9}">{value_s}</text>'
    )
