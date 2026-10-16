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
from collections.abc import Mapping
from dataclasses import dataclass

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


@dataclass(frozen=True)
class ScenarioDrawings:
    """The two scenario-sheet drawings for one worked building, plus whether the
    section actually carries the permitted-envelope height lines (part B2). Part W
    embeds these once and passes them to :func:`page_scenario_sheet.render`; the
    page embeds its own when none are passed."""

    area_illustration: drawings_embed.Embedded | None
    section: drawings_embed.Embedded
    section_has_height_lines: bool


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
            return drawings_embed.embed_floor_stack(building, env=env)
        return _embedded_from_drawing(result)
    return drawings_embed.embed_floor_stack(building, env=env)


def _section_has_height_lines(results: Mapping, section: drawings_embed.Embedded) -> bool:
    """Whether the embedded section actually carries the height lines: part B2 is
    present (``render_floor_stack`` has ``results=``), the section is drawn, and the
    document carries at least one standard-case permitted-envelope height."""
    from app.drawings import kit

    fn = getattr(kit, "render_floor_stack", None)
    if fn is None or not _has_results_keyword(fn):
        return False
    return section.is_drawing and _permitted_envelope_has_height(results)


def scenario_drawings_for(building: Mapping, results: Mapping, *, env=None) -> ScenarioDrawings:
    """Both scenario-sheet drawings for one worked building, with the section's
    height-line state."""
    area = embed_area_illustration(building, env=env)
    section = embed_section(building, results, env=env)
    return ScenarioDrawings(area, section, _section_has_height_lines(results, section))


def embed_scenario_drawings(results: Mapping, *, env=None) -> list[ScenarioDrawings]:
    """The scenario-sheet drawings for every worked building, in document order
    (part W embeds once and passes them to the page)."""
    return [
        scenario_drawings_for(building, results, env=env)
        for building in (results.get("building_alternatives") or [])
        if isinstance(building, Mapping)
    ]
