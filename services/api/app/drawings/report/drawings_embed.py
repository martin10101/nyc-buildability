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
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from xml.sax.saxutils import escape as _xml_escape

from app.drawings.kit.presentation_tokens import COLOR

__all__ = [
    "Embedded",
    "allowance_bar_chart_svg",
    "embed_floor_stack",
    "embed_kit_drawing",
    "embed_map",
    "embed_summary_site_plan",
    "size_svg_to_points",
    "summary_frame_available",
]

_VIEWBOX = re.compile(r'viewBox="([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)"')


def size_svg_to_points(svg: str) -> str:
    """Set the embedded SVG's displayed ``width``/``height`` in POINTS equal to
    its viewBox size, so a browser prints it at its designed size (ruling D1).

    The kit's SVGs carry UNITLESS ``width``/``height`` whose numbers are points,
    but a browser reads a unitless length as CSS px (1px = 0.75pt), so the drawing
    would print at 0.75 of its size and its labels would fall below 7 pt. Stamping
    ``width="<w>pt" height="<h>pt"`` (the viewBox width/height) fixes the scale and
    is never shrunk by the report's CSS."""
    match = _VIEWBOX.search(svg)
    if not match:
        return svg
    width, height = match.group(3), match.group(4)

    def rewrite(open_tag: re.Match) -> str:
        tag = open_tag.group(0)
        tag = re.sub(r'\swidth="[^"]*"', "", tag)
        tag = re.sub(r'\sheight="[^"]*"', "", tag)
        return tag[:-1] + f' width="{width}pt" height="{height}pt">'

    return re.sub(r"<svg\b[^>]*>", rewrite, svg, count=1)


@dataclass(frozen=True)
class Embedded:
    """A drawing ready to place, or a short line to print in its place."""

    svg: str | None = None
    caption: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)
    attribution: str | None = None
    short_line: str | None = None
    # The style kinds the drawing actually drew (the kit ``Drawing.kinds_drawn``,
    # read verbatim). Empty for a short line or a drawing that reports none. It is
    # NOT rendered - the drawn-content manifest reads it so a page can decide a
    # "drawn"/"shown" claim from rendered content, never a hard-coded constant
    # (M5-T173 part B4; :mod:`.manifest`).
    kinds_drawn: tuple[str, ...] = field(default_factory=tuple)

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
        svg = getattr(result, "svg", None)
        return Embedded(
            svg=size_svg_to_points(svg) if svg else svg,
            caption=getattr(result, "caption", None),
            notes=tuple(getattr(result, "notes", ()) or ()),
            attribution=getattr(result, "attribution", None),
            kinds_drawn=tuple(getattr(result, "kinds_drawn", ()) or ()),
        )
    reason = getattr(result, "reason", None)
    return Embedded(short_line=str(reason) if reason else "This drawing is not shown here.")


def _call(module, fn_name: str, arg, env, missing_line: str, *, frame: str = "report") -> Embedded:
    fn = getattr(module, fn_name, None)
    if fn is None or not _frame_supported(fn):
        return Embedded(short_line=missing_line)
    try:
        result = fn(arg, frame=frame, env=env)
    except Exception:  # noqa: BLE001 - any kit failure means no drawing, never an error page
        return Embedded(short_line=missing_line)
    return _from_result(result)


_SITE_PLAN_UNAVAILABLE = "The site plan is not available for this report."
_FLOOR_STACK_UNAVAILABLE = "The floor-stack section is not available for this report."


def embed_kit_drawing(
    fn_name: str, results: Mapping, *, env=None, not_available_line: str | None = None
) -> Embedded:
    """A drawing-kit drawing (site plan, massing) at the report frame. When it is
    unavailable the short line names the drawing (A9)."""
    from app.drawings import kit

    return _call(kit, fn_name, results, env,
                 not_available_line or "This drawing is not available for this report.")


def summary_frame_available(results: Mapping, *, env=None) -> bool:
    """True once M5-T152's compact ``frame="summary"`` site plan is distinct from
    the full ``frame="sheet"`` output. Until then the two are identical, so the
    decision summary falls back to no drawing (F3)."""
    from app.drawings import kit

    fn = getattr(kit, "render_site_plan", None)
    if fn is None or not _frame_supported(fn):
        return False
    try:
        summary = fn(results, frame="summary", env=env)
        sheet = fn(results, frame="sheet", env=env)
    except Exception:  # noqa: BLE001
        return False
    return getattr(summary, "svg", None) not in (None, getattr(sheet, "svg", None))


def embed_summary_site_plan(results: Mapping, *, env=None) -> Embedded:
    """A compact (<= 85 mm) site plan for the decision summary, only when the
    summary frame exists; otherwise a short line pointing to the site page (F3)."""
    if not summary_frame_available(results, env=env):
        return Embedded(short_line=_SITE_PLAN_UNAVAILABLE)
    from app.drawings import kit

    return _call(kit, "render_site_plan", results, env, _SITE_PLAN_UNAVAILABLE, frame="summary")


def embed_floor_stack(alternative: Mapping, *, env=None) -> Embedded:
    """The floor-stack section for one worked building (``render_floor_stack``)."""
    from app.drawings import kit

    return _call(kit, "render_floor_stack", alternative, env, _FLOOR_STACK_UNAVAILABLE)


_MAP_UNAVAILABLE = "This map is not shown here."
# When the 1.5.0 constraint overlay cannot be drawn (a label that cannot be placed
# at 8.5 pt raises by design, or a malformed established geometry), the site map is
# kept WITHOUT the overlay and carries this short note rather than dropping the whole
# map (M5-T175 S15; code-review advisories 1 and 2). Any OTHER map failure keeps the
# old behaviour (one short line).
_OVERLAY_DROPPED_NOTE = "A zoning line could not be drawn on this map; page 3 lists it."
# When the placed building footprint (M5-T173 part B) cannot be drawn on the close
# frame, the map is kept WITHOUT the footprint and carries this short note naming
# what was not drawn, rather than dropping the whole map (S6).
_FOOTPRINT_DROPPED_NOTE = "The building footprint could not be drawn on this map."


def embed_map(
    fn_name: str, map_context: Mapping, *, layers: tuple[str, ...], frame: str = "report", env=None,
    constraint_lines=None, input_facts=None, placed_footprint=None,
) -> Embedded:
    """A site-context, block or neighbourhood map, captioned in plain words with a
    short "Sources: ..." line (the layers it shows, each with its edit date once)
    and the drawing's own notes (:mod:`.map_caption`, rulings Y7/X6). ``frame`` is
    ``"report"`` (the full-size plan) or ``"summary"`` (the compact page-1 /
    location-sheet thumbnail). ``constraint_lines`` / ``input_facts`` (results
    contract 1.5.0) are forwarded ONLY to the site-context map, which draws the
    established overlay on its close frames (M5-T175). ``placed_footprint``
    (M5-T173 part B) is the placed building footprint drawn on the close frame;
    like the overlay it is forwarded ONLY when given. Each of these extras is
    omitted from the call otherwise, so the neighbourhood/block maps and every
    render without them are byte-identical (S1, S6). If the render fails with an
    extra, the map is kept by re-rendering WITHOUT both the overlay and the
    footprint, carrying one note naming what was not drawn (the zoning-line note
    for the overlay; a footprint note for the footprint). An Unavailable, missing
    keyword or genuine map failure prints one short line, never an error (S6)."""
    from app.drawings import maps

    from . import map_caption

    fn = getattr(maps, fn_name, None)
    if fn is None or not _frame_supported(fn):
        return Embedded(short_line=_MAP_UNAVAILABLE)
    overlay = {}
    if constraint_lines is not None:
        overlay["constraint_lines"] = constraint_lines
    if input_facts is not None:
        overlay["input_facts"] = input_facts
    if placed_footprint is not None:
        overlay["placed_footprint"] = placed_footprint
    note: tuple[str, ...] = ()
    try:
        result = fn(map_context, frame=frame, env=env, **overlay)
    except Exception:  # noqa: BLE001 - any kit failure means no map, never an error page
        if not overlay:
            return Embedded(short_line=_MAP_UNAVAILABLE)
        # The failure may be an extra's (an overlay label that cannot be placed, a
        # malformed established geometry, or a footprint that cannot be drawn): keep
        # the map by drawing it WITHOUT the extras and carry a short note naming what
        # was not drawn. If it fails without them too, it is a genuine map failure -
        # today's one short line (S15, S6).
        try:
            result = fn(map_context, frame=frame, env=env)
        except Exception:  # noqa: BLE001
            return Embedded(short_line=_MAP_UNAVAILABLE)
        dropped: list[str] = []
        if "constraint_lines" in overlay or "input_facts" in overlay:
            dropped.append(_OVERLAY_DROPPED_NOTE)
        if "placed_footprint" in overlay:
            dropped.append(_FOOTPRINT_DROPPED_NOTE)
        note = tuple(dropped)
    svg = getattr(result, "svg", None)
    if svg is None:
        reason = getattr(result, "reason", None)
        return Embedded(short_line=str(reason) if reason else _MAP_UNAVAILABLE)
    caption = map_caption.figure_caption(result, map_context, layers)
    return Embedded(svg=size_svg_to_points(svg), caption=caption, notes=note,
                    kinds_drawn=tuple(getattr(result, "kinds_drawn", ()) or ()))


def allowance_bar_chart_svg(
    allowance_display: str | None,
    allowance_value: float | None,
    buildings: list[dict],
    *,
    placed_on_site: bool = False,
    footprint_drawn: bool | None = None,
) -> str | None:
    """A compact horizontal bar chart distinguishing THREE things on ONE zero-based
    scale (R018/R020): the floor-area allowance, each worked building's scheduled
    area, and whether a building is placed on site. The placed-on-site row is a status,
    never a bar, with three honest states: "Not demonstrated" when nothing is placed
    (not a zero-height bar); "Worked out; not drawn" when the engine placed the building
    but the site plan does not draw the footprint; and "Shown on the site plan" only when
    the footprint is actually drawn in the report - so page 5 never claims a placement the
    site plan contradicts and the chart never prints two equal bars. ``footprint_drawn``
    carries that drawn state from the drawn-content manifest (M5-T173 part B): ``True``
    only when the site plan actually drew the footprint; ``False`` or ``None`` (an unwired
    caller) is not drawn, so page 5 never claims a drawing page 4 lacks. Returns ``None``
    when there is no allowance to chart. Every printed number is a document figure passed in."""
    if not isinstance(allowance_value, (int, float)) or allowance_value <= 0:
        return None
    bars = [b for b in buildings if isinstance(b.get("scheduled_value"), (int, float))]
    scale = max([allowance_value, *[b["scheduled_value"] for b in bars]])
    if scale <= 0:
        return None
    # Give the value labels room so they are never cut (A6): a short track with a
    # wide right margin for the figure. The viewBox width (500) stays inside the
    # A4 content box when printed at its designed point size (500 pt = 176 mm).
    track = 220.0
    width_total = 500
    rows = []
    y = 6
    allowance_text = f"{allowance_display} sq ft" if allowance_display else ""
    rows.append(_bar(y, track, "Floor-area allowance", allowance_text, allowance_value, scale))
    y += 22
    for b in bars:
        name = f"Building {b.get('building')}" if b.get("building") else "Worked building"
        label = b.get("scheduled_display")
        text = f"{label} sq ft" if label else ""
        rows.append(_bar(y, track, f"{name} scheduled", text, b["scheduled_value"], scale))
        y += 22
    # placed-on-site: a status, never a bar (an unknown is never a zero-height bar, R020).
    # Three honest states (S14): not placed -> "Not demonstrated"; placed but the site plan
    # does not draw the footprint -> "Worked out; not drawn"; placed AND drawn -> "Shown on
    # the site plan". The drawn state is the manifest's ``footprint_drawn``: True only when
    # the site plan actually drew the footprint; False or None (an unwired caller) is not
    # drawn, so the chart never claims a drawing page 4 lacks.
    drawn = footprint_drawn is True
    if not placed_on_site:
        placed_text = "Not demonstrated"
    elif drawn:
        placed_text = "Shown on the site plan"
    else:
        placed_text = "Worked out; not drawn"
    rows.append(_status_row(y, "Placed on site", placed_text))
    y += 22
    height = y + 4
    body = "".join(rows)
    # viewBox units are points; stamped width/height in pt print it at true size (D1).
    return (
        f'<svg class="bar-chart" viewBox="0 0 {width_total} {height}" '
        f'role="img" width="{width_total}pt" height="{height}pt">{body}</svg>'
    )


def _status_row(y: int, name: str, status_text: str) -> str:
    """A label and a status word with NO rectangle (the placed-on-site distinction):
    the status is never drawn as a bar, so an unknown cannot read as a zero-length
    bar (R020). font-size in viewBox units (points): at least 7 (D2)."""
    name_s = _xml_escape(name)
    status_s = _xml_escape(status_text)
    return (
        f'<text x="0" y="{y + 9}" font-size="8">{name_s}</text>'
        f'<text x="155" y="{y + 9}" font-size="8" font-style="italic">{status_s}</text>'
    )


def _bar(y: int, track: float, name: str, value_text: str, value: float, scale: float) -> str:
    width = max(1.0, track * (value / scale))
    name_s = _xml_escape(name)
    value_s = _xml_escape(value_text)
    # font-size in viewBox units (points): at least 7 so it prints legibly (D2).
    fill = COLOR["action"]
    return (
        f'<text x="0" y="{y + 9}" font-size="8">{name_s}</text>'
        f'<rect x="150" y="{y}" width="{width:.1f}" height="12" fill="{fill}"></rect>'
        f'<text x="{150 + width + 5:.1f}" y="{y + 9}" font-size="8">{value_s}</text>'
    )
