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

from . import drawings_embed, map_caption, readers
from .components import short_line
from .drawings_embed import Embedded
from .html import el, raw

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
    when the one-outline check passed and the drawings drew. ``neighbourhood`` and
    ``block`` are the COMPACT summary-frame thumbnails for the one-page location
    sheet; ``summary_plan`` is the compact site plan beside page 1's answers; and
    ``report_plan`` is the full-size site plan shown once, on the constraints
    sheet. The same full-size drawing is never printed twice."""

    available: bool
    reason: str | None = None
    neighbourhood: Embedded | None = None
    block: Embedded | None = None
    summary_plan: Embedded | None = None
    report_plan: Embedded | None = None


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
    """Decide whether the report may show the surroundings and render the maps when
    it may (ruling Y5). The location sheet and page 1 take COMPACT summary-frame
    drawings; the constraints sheet takes the one full-size plan. A missing map
    document, a failed one-outline check or maps that do not draw all yield
    ``available=False`` with a short limitation line - never a partial or mismatched
    picture (S2, S6)."""
    if not isinstance(map_context, Mapping):
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)
    if not outlines_match(_subject_outline(map_context), readers.results_lot_outline(results)):
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)

    def embed(fn_name, layers, frame):
        return drawings_embed.embed_map(fn_name, map_context, layers=layers, frame=frame, env=env)

    # The neighbourhood map and the block close-up are CO-EQUAL wide strips stacked
    # full width on the location page (each at most 182 by 105 mm, no title inside -
    # the report adds the title); page 1 takes the compact summary plan, the
    # constraints sheet the one full-size plan (corrections T156-C2).
    neighbourhood = embed("render_neighbourhood_map", map_caption.NEIGHBOURHOOD_LAYERS, "wide")
    block = embed("render_block_map", map_caption.BLOCK_LAYERS, "wide")
    summary_plan = embed("render_site_context_plan", map_caption.SITE_LAYERS, "summary")
    report_plan = embed("render_site_context_plan", map_caption.SITE_LAYERS, "report")
    drawn = [m for m in (neighbourhood, block, summary_plan, report_plan) if m.is_drawing]
    if not drawn:
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)
    return Surroundings(True, neighbourhood=neighbourhood, block=block,
                        summary_plan=summary_plan, report_plan=report_plan)


def _wide_figure(title: str, drawing: Embedded | None) -> object | None:
    """One co-equal full-width location map: its title, the drawing, then its
    sources-and-dates caption below it."""
    if drawing is None or not drawing.is_drawing:
        return None
    parts: list[object] = [el("p", title, class_="figure-title"),
                           el("figure", raw(drawing.svg or ""))]
    if drawing.caption:
        parts.append(el("p", drawing.caption, class_="figure-note"))
    return el("div", *parts, class_="location-wide-figure")


def render(surroundings: Surroundings) -> object:
    """The 'Where is the lot?' sheet, filling ONE balanced A4 page (corrections
    T156-C2): the neighbourhood map and the block close-up as two co-equal
    full-width wide strips stacked, each with its title and its sources-and-dates
    caption. One short line when the surroundings are not available. No photo, empty
    frame or photo wording (ruling Y9); the stack can take a third figure later
    without a redesign."""
    children: list[object] = [el("h2", QUESTION)]
    if not surroundings.available:
        children.append(short_line(surroundings.reason or _SURROUNDINGS_UNAVAILABLE))
        return el("div", *children, class_="location-sheet")
    stack = [fig for fig in (_wide_figure("Neighbourhood", surroundings.neighbourhood),
                             _wide_figure("Block close-up", surroundings.block)) if fig is not None]
    children.append(el("div", *stack, class_="location-stack"))
    return el("div", *children, class_="location-sheet")
