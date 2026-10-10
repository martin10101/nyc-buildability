"""The 'Where is the lot?' sheet that opens page type 2, and the one-outline
check that decides whether the report may show the lot among its surroundings
(rulings Y5, Y9, Y10; D-090 R936 to R940).

WHY: the owner looked at the report and said the site drawing was 'a rectangle on
an angle' with 'no reference to where he is'. The location sheet answers that with
the neighbourhood map and the block close-up from the map document (M5-T154 /
M5-T155), each captioned with its sources and their dates in plain words. There is
NO street photo, empty frame or photo wording (ruling Y9); the figure grid can
take a third figure later without a redesign.

The surroundings are shown ONLY when the map document's subject outline, shifted
by its own minimum x and y, equals the results document's lot outline within
0.01 ft at every vertex (ruling Y5). Otherwise the surroundings are dropped, the
report keeps today's lot-only plan, and one short limitation line is printed. Two
outlines are never drawn together.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from . import drawings_embed, readers
from .components import figure, short_line
from .drawings_embed import Embedded
from .html import el

__all__ = ["QUESTION", "Surroundings", "outlines_match", "render", "resolve"]

QUESTION = "Where is the lot?"

# The map document's subject outline is the measurement-grade MapPLUTO outline
# (EPSG:2263); the results document's outline is the same lot in local feet,
# already anchored at its own minimum. They describe one polygon, so the match
# allows any starting vertex and either winding (ruling Y5).
_OUTLINE_TOLERANCE_FT = 0.01

_SURROUNDINGS_UNAVAILABLE = (
    "The surroundings are not shown for this property: map data that matches this "
    "lot is not available."
)


@dataclass(frozen=True)
class Surroundings:
    """The resolved site-context maps for one report. ``available`` is true only
    when the one-outline check passed and at least one map drew; the three maps
    are the report-frame drawings (``neighbourhood`` and ``block`` for the location
    sheet, ``site_plan`` for the decision summary and the constraints sheet)."""

    available: bool
    reason: str | None = None
    neighbourhood: Embedded | None = None
    block: Embedded | None = None
    site_plan: Embedded | None = None


def _ring(rings: object) -> list[tuple[float, float]] | None:
    """The first ring as (x, y) tuples with any closing duplicate dropped."""
    if not isinstance(rings, list) or not rings:
        return None
    ring = rings[0]
    if not isinstance(ring, list) or len(ring) < 3:
        return None
    try:
        points = [(float(p[0]), float(p[1])) for p in ring]
    except (TypeError, ValueError, IndexError):
        return None
    if (abs(points[0][0] - points[-1][0]) <= 1e-9
            and abs(points[0][1] - points[-1][1]) <= 1e-9):
        points = points[:-1]
    return points or None


def _shift_to_min(ring: list[tuple[float, float]]) -> list[tuple[float, float]]:
    min_x = min(p[0] for p in ring)
    min_y = min(p[1] for p in ring)
    return [(p[0] - min_x, p[1] - min_y) for p in ring]


def _aligns(a: list[tuple[float, float]], b: list[tuple[float, float]], tol: float) -> bool:
    """True when some rotation of ``a`` matches ``b`` vertex-for-vertex within tol."""
    n = len(a)
    for shift in range(n):
        if all(abs(a[(i + shift) % n][0] - b[i][0]) <= tol
               and abs(a[(i + shift) % n][1] - b[i][1]) <= tol for i in range(n)):
            return True
    return False


def outlines_match(
    map_outline: object, results_outline: object, *, tol: float = _OUTLINE_TOLERANCE_FT
) -> bool:
    """The one-outline check (ruling Y5): the map document's subject outline,
    shifted by its own minimum x and y, equals the results document's lot outline
    within ``tol`` ft at every vertex. Any starting vertex and either winding is
    accepted (the two describe one polygon)."""
    a = _ring(map_outline)
    b = _ring(results_outline)
    if a is None or b is None or len(a) != len(b):
        return False
    a = _shift_to_min(a)
    b = _shift_to_min(b)
    return _aligns(a, b, tol) or _aligns(list(reversed(a)), b, tol)


def _subject_outline(map_context: Mapping) -> object:
    mc = map_context.get("map_context")
    subject = mc.get("subject_lot") if isinstance(mc, Mapping) else None
    return subject.get("outline") if isinstance(subject, Mapping) else None


def resolve(map_context: object, results: Mapping, *, env=None) -> Surroundings:
    """Decide whether the report may show the surroundings and render the three
    report-frame maps when it may (ruling Y5). A missing map document, a failed
    one-outline check or maps that do not draw all yield ``available=False`` with a
    short limitation line - never a partial or mismatched picture (S2, S6)."""
    if not isinstance(map_context, Mapping):
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)
    if not outlines_match(_subject_outline(map_context), readers.results_lot_outline(results)):
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)
    neighbourhood = drawings_embed.embed_map("render_neighbourhood_map", map_context, env=env)
    block = drawings_embed.embed_map("render_block_map", map_context, env=env)
    site_plan = drawings_embed.embed_map("render_site_context_plan", map_context, env=env)
    drawn = [m for m in (neighbourhood, block, site_plan) if m.is_drawing]
    if not drawn:
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)
    return Surroundings(True, neighbourhood=neighbourhood, block=block, site_plan=site_plan)


def render(surroundings: Surroundings) -> object:
    """The 'Where is the lot?' sheet: the neighbourhood map and the block close-up,
    each captioned, or one short line when the surroundings are not available. No
    photo, empty frame or photo wording (ruling Y9); the grid can take a third
    figure later."""
    children: list[object] = [el("h2", QUESTION)]
    if not surroundings.available:
        children.append(short_line(surroundings.reason or _SURROUNDINGS_UNAVAILABLE))
        return el("div", *children, class_="location-sheet")
    grid: list[object] = []
    for drawing, fallback in (
        (surroundings.neighbourhood, "The neighbourhood map is not shown here."),
        (surroundings.block, "The block close-up is not shown here."),
    ):
        if drawing is not None:
            grid.append(figure(drawing, drawing.caption or "", line_when_absent=fallback))
    children.append(el("div", *grid, class_="location-figures"))
    return el("div", *children, class_="location-sheet")
