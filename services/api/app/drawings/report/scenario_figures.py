"""Scenario-sheet drawings (page type 4, M5-T173 part B3).

The scenario sheet (``page_scenario_sheet``) shows, per worked building, two
drawings: the two-zone AREA ILLUSTRATION (the drawing kit's
:func:`app.drawings.kit.area_allocation.draw_area_allocation` kernel) and the
floor-stack SECTION (``kit.render_floor_stack``). This module embeds both,
defensively, behind the Lane E flag - mirroring :mod:`.drawings_embed`:

* the kit is a leaf that fails CLOSED, so a disabled kit, a missing block or a
  kernel :class:`Unavailable` becomes ``None`` (nothing drawn) or a one-line
  reason, never an exception and never an error page;
* the section opts in to the permitted-envelope height lines through the
  ``results=`` keyword of ``render_floor_stack`` ONLY when that keyword exists
  (part B2); without it the module calls today's :func:`.drawings_embed.embed_floor_stack`,
  so the two parts land in either order and the default output is unchanged.

Every printed value comes from the results document (the kernel validates and
prints the block's own figures); this module computes no zoning quantity.
"""

from __future__ import annotations

import inspect
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, replace

from . import drawings_embed

__all__ = [
    "ScenarioDrawings",
    "embed_area_illustration",
    "embed_scenario_drawings",
    "embed_section",
    "scenario_drawings_for",
]

_AREA_UNAVAILABLE = "The area illustration is not shown here."
_SECTION_UNAVAILABLE = "The floor-stack section is not available for this report."

# The three STANDARD-case permitted-envelope height keys part B2 draws as lines
# (min base, max base, max building height). The qualifying-affordable/senior keys
# are not drawn for the standard building, so they are not counted here.
_HEIGHT_KEYS = ("min_base_height", "max_base_height", "max_building_height")

# The document's own way vocabulary (contract 1.3.0+). A standard height carried as
# "conditional" in ``permitted_envelope.value_states`` must say so on the section
# caption (owner's standard: conditional stays conditional).
_CONDITIONAL_WAY = "conditional"

# The smallest point size a drawing label may print at (presentation contract, print
# type scale, change of 2026-10-11: "drawing labels at least 8.5 pt at the printed
# size"; the superseded rule was >= 7 pt). The kit draws its section labels at a
# fixed 8.0 pt native size, so the embed enlarges the section just enough that the
# smallest label prints at or above this.
_MIN_LABEL_PT = 8.5

_VIEWBOX_RE = re.compile(r'viewBox="([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)"')
_FONT_SIZE_RE = re.compile(r'font-size="([\d.]+)"')
_SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>")


@dataclass(frozen=True)
class ScenarioDrawings:
    """The two scenario-sheet drawings for one worked building, whether the section
    actually carries the permitted-envelope height lines (part B2), and whether those
    standard height lines are CONDITIONAL in the document (read from
    ``value_states``, never hard-coded). Part W embeds these once and passes them to
    :func:`page_scenario_sheet.render`; the page embeds its own when none are passed."""

    area_illustration: drawings_embed.Embedded | None
    section: drawings_embed.Embedded
    section_has_height_lines: bool
    section_heights_conditional: bool = False


def _finite_nonneg(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) >= 0.0
    )


def _has_results_keyword(fn: object) -> bool:
    try:
        return "results" in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def _permitted_envelope_has_height(results: Mapping) -> bool:
    """True when the document's ``answers.permitted_envelope`` is available and
    carries at least one finite non-negative STANDARD-case height in feet - the
    same facts part B2 draws its lines from. A document read only; no law is
    evaluated here (the lines themselves are B2's, drawn in the kit)."""
    answers = results.get("answers") if isinstance(results, Mapping) else None
    block = answers.get("permitted_envelope") if isinstance(answers, Mapping) else None
    if not isinstance(block, Mapping) or block.get("status") != "available":
        return False
    for value in block.get("values") or []:
        if not isinstance(value, Mapping):
            continue
        if value.get("key") in _HEIGHT_KEYS and value.get("unit") == "feet":
            if _finite_nonneg(value.get("value")):
                return True
    return False


def _embedded_from_drawing(result: object) -> drawings_embed.Embedded:
    """Wrap a kit ``Drawing`` (or ``Unavailable``) into an :class:`.drawings_embed.Embedded`,
    sizing the SVG to points like :mod:`.drawings_embed` does."""
    svg = getattr(result, "svg", None)
    if svg:
        return drawings_embed.Embedded(svg=drawings_embed.size_svg_to_points(svg))
    reason = getattr(result, "reason", None)
    return drawings_embed.Embedded(short_line=str(reason) if reason else _SECTION_UNAVAILABLE)


def _enlarge_to_min_label_pt(svg: str, min_pt: float = _MIN_LABEL_PT) -> str:
    """Enlarge a point-sized SVG so its SMALLEST text label prints at or above
    ``min_pt``, without ever breaking the embed invariant that the stamped point
    width/height equal the viewBox (so the drawing prints at its designed point
    size, checks D1/D2).

    :func:`.drawings_embed.size_svg_to_points` stamps ``width``/``height`` equal to
    the viewBox, so a label of font-size ``s`` (viewBox units) prints at ``s`` pt.
    The kit's section labels are a fixed 8.0 pt, below the contract's 8.5 pt. We
    cannot change the kit (forbidden) or the ``width==viewBox`` invariant, so we
    grow the viewBox AND the stamped point size by one factor and scale the whole
    body by the same factor: the stamped size still equals the viewBox, and every
    label now occupies ``s * factor`` viewBox units, so it prints at ``s * factor``
    pt. The factor is the smallest that lifts the smallest label to ``min_pt``; a
    drawing already at or above it, or with no measurable label, is returned
    unchanged."""
    open_match = _SVG_OPEN_RE.search(svg)
    viewbox = _VIEWBOX_RE.search(svg)
    close = svg.rfind("</svg>")
    if open_match is None or viewbox is None or close < open_match.end():
        return svg
    fonts = [float(size) for size in _FONT_SIZE_RE.findall(svg)]
    smallest = min(fonts, default=0.0)
    if smallest <= 0.0 or smallest >= min_pt:
        return svg
    factor = min_pt / smallest
    new_w = float(viewbox.group(3)) * factor
    new_h = float(viewbox.group(4)) * factor
    open_tag = _VIEWBOX_RE.sub(
        f'viewBox="{viewbox.group(1)} {viewbox.group(2)} {new_w:.2f} {new_h:.2f}"',
        open_match.group(0), count=1,
    )
    open_tag = re.sub(r'\swidth="[^"]*"', f' width="{new_w:.2f}pt"', open_tag, count=1)
    open_tag = re.sub(r'\sheight="[^"]*"', f' height="{new_h:.2f}pt"', open_tag, count=1)
    body = svg[open_match.end():close]
    tail = svg[close:]  # "</svg>" and any trailing whitespace the kit emits
    return f'{open_tag}<g transform="scale({factor:.6f})">{body}</g>{tail}'


def _with_min_label_pt(embedded: drawings_embed.Embedded) -> drawings_embed.Embedded:
    """Return the embedded section with its labels enlarged to at least the contract
    minimum point size; a short line (no drawing) is returned unchanged."""
    if not embedded.is_drawing or not embedded.svg:
        return embedded
    enlarged = _enlarge_to_min_label_pt(embedded.svg)
    if enlarged == embedded.svg:
        return embedded
    return replace(embedded, svg=enlarged)


def embed_area_illustration(building: Mapping, *, env=None) -> drawings_embed.Embedded | None:
    """The two-zone area illustration for one worked building, behind the Lane E
    flag. ``None`` when the kit is off or the building carries no ``area_allocation``
    block (so a 1.4.0 sheet shows no illustration and no new claim); an
    :class:`.drawings_embed.Embedded` carrying the drawing when drawn, or the
    kernel's own ``Unavailable`` reason verbatim when it refuses (a degenerate
    block). The report prints the one caption beneath it, so ``caption=False``."""
    from app.drawings.kit import area_allocation
    from app.drawings.kit.flag import drawing_kit_enabled

    if not drawing_kit_enabled(env):
        return None
    block = building.get("area_allocation") if isinstance(building, Mapping) else None
    if not isinstance(block, Mapping):
        return None
    placement = building.get("placement") if isinstance(building, Mapping) else None
    placement = placement if isinstance(placement, Mapping) else None
    try:
        result = area_allocation.draw_area_allocation(block, placement=placement, caption=False)
    except Exception:  # noqa: BLE001 - any kernel failure means no drawing, never an error page
        return drawings_embed.Embedded(short_line=_AREA_UNAVAILABLE)
    svg = getattr(result, "svg", None)
    if svg:
        return drawings_embed.Embedded(svg=drawings_embed.size_svg_to_points(svg))
    reason = getattr(result, "reason", None)
    return drawings_embed.Embedded(short_line=str(reason) if reason else _AREA_UNAVAILABLE)


def embed_section(building: Mapping, results: Mapping, *, env=None) -> drawings_embed.Embedded:
    """The floor-stack section for one worked building. When ``render_floor_stack``
    carries the ``results=`` keyword (part B2) the section is drawn with the
    permitted-envelope height lines; otherwise today's :func:`.drawings_embed.embed_floor_stack`
    output is kept byte-identical. Any kit failure falls back to that same call, so
    the two parts land in either order with no error (S7)."""
    from app.drawings import kit

    fn = getattr(kit, "render_floor_stack", None)
    if fn is not None and _has_results_keyword(fn):
        try:
            result = fn(building, results=results, env=env)
        except Exception:  # noqa: BLE001 - fall back to today's call, never an error page
            embedded = drawings_embed.embed_floor_stack(building, env=env)
        else:
            embedded = _embedded_from_drawing(result)
    else:
        embedded = drawings_embed.embed_floor_stack(building, env=env)
    # The kit draws the section labels at a fixed 8.0 pt; enlarge the whole section
    # so the smallest label prints at or above the contract's 8.5 pt (part B2's and
    # the visual reviewer's open item), keeping the drawing's point-size invariant.
    return _with_min_label_pt(embedded)


def _section_has_height_lines(results: Mapping, section: drawings_embed.Embedded) -> bool:
    """Whether the embedded section actually carries the height lines: part B2 is
    present (``render_floor_stack`` has ``results=``), the section is drawn, and the
    document carries at least one standard-case permitted-envelope height."""
    from app.drawings import kit

    fn = getattr(kit, "render_floor_stack", None)
    if fn is None or not _has_results_keyword(fn):
        return False
    return section.is_drawing and _permitted_envelope_has_height(results)


def _standard_heights_conditional(results: Mapping) -> bool:
    """Whether the STANDARD-case permitted-envelope heights the section draws are
    CONDITIONAL in the document. A document read only: it reads the
    ``value_states`` way (contract 1.3.0+) of the standard height keys that actually
    carry a drawable value, and returns True when any of them is ``conditional``.
    No law is evaluated and nothing is hard-coded - a document whose heights are
    settled returns False, so the section caption never calls a settled height
    conditional or a conditional height settled."""
    answers = results.get("answers") if isinstance(results, Mapping) else None
    block = answers.get("permitted_envelope") if isinstance(answers, Mapping) else None
    if not isinstance(block, Mapping):
        return False
    states = block.get("value_states")
    if not isinstance(states, Mapping):
        return False
    drawn: set[str] = set()
    for value in block.get("values") or []:
        if not isinstance(value, Mapping):
            continue
        if value.get("key") in _HEIGHT_KEYS and value.get("unit") == "feet":
            if _finite_nonneg(value.get("value")):
                drawn.add(value.get("key"))
    for key in drawn:
        entry = states.get(key)
        if isinstance(entry, Mapping) and entry.get("way") == _CONDITIONAL_WAY:
            return True
    return False


def scenario_drawings_for(building: Mapping, results: Mapping, *, env=None) -> ScenarioDrawings:
    """Both scenario-sheet drawings for one worked building, with the section's
    height-line state and whether those height lines are conditional in the
    document (only meaningful, and only read, when the lines are drawn)."""
    area = embed_area_illustration(building, env=env)
    section = embed_section(building, results, env=env)
    has_lines = _section_has_height_lines(results, section)
    conditional = has_lines and _standard_heights_conditional(results)
    return ScenarioDrawings(area, section, has_lines, conditional)


def embed_scenario_drawings(results: Mapping, *, env=None) -> list[ScenarioDrawings]:
    """The scenario-sheet drawings for every worked building, in document order
    (part W embeds once and passes them to the page)."""
    return [
        scenario_drawings_for(building, results, env=env)
        for building in (results.get("building_alternatives") or [])
        if isinstance(building, Mapping)
    ]
