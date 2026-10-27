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

__all__ = ["QUESTION", "Surroundings", "outlines_match", "placed_footprint", "render",
           "resolve"]

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
    ``block`` are the wide-frame thumbnails built for the location sheet (only the
    neighbourhood locator is printed now); ``summary_plan`` is the COMPACT CLOSE
    frame (the close composition at the 88 mm column) beside page 1's answers; and
    ``report_plan`` is the large close frame shown once, on the constraints sheet.
    The same drawing is never printed twice (M5-T166)."""

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


def _overlay_data(results: Mapping) -> tuple[list | None, list | None]:
    """The results contract 1.5.0 overlay inputs the site frame draws (M5-T175):
    ``geometry.constraint_lines`` and ``input_facts``, read defensively. ``None``
    for a 1.4.0 (and earlier) document, so the site frame draws nothing and is
    byte-identical (S1)."""
    geometry = results.get("geometry") if isinstance(results, Mapping) else None
    lines = geometry.get("constraint_lines") if isinstance(geometry, Mapping) else None
    facts = results.get("input_facts") if isinstance(results, Mapping) else None
    return (lines if isinstance(lines, list) and lines else None,
            facts if isinstance(facts, list) and facts else None)


def placed_footprint(results: Mapping) -> list | None:
    """The engine's results-local floor-1 plate ring (``geometry.floor_plates``, the
    entry whose ``floor`` is 1), passed to the CLOSE frame as the illustrative footprint
    (M5-T173 part B). The block must be ``available`` (a building is placed) and the
    floor-1 entry must carry a non-empty outline ring; otherwise ``None`` - a 1.4.0
    document (no block), a not-``available`` block, or a malformed entry - so the close
    frame keeps the 'No building placed' legend and draws no footprint (S1). A ring that
    is present but geometrically degenerate is still returned: the close frame then drops
    'No building placed' but draws nothing, which part B1's renderer decides (S4)."""
    geometry = results.get("geometry") if isinstance(results, Mapping) else None
    plates = geometry.get("floor_plates") if isinstance(geometry, Mapping) else None
    if not isinstance(plates, Mapping) or plates.get("status") != "available":
        return None
    entries = plates.get("entries")
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if not isinstance(entry, Mapping) or entry.get("floor") != 1:
            continue
        outline = entry.get("outline")
        if isinstance(outline, list) and outline and isinstance(outline[0], list) and outline[0]:
            return outline[0]
        return None
    return None


def resolve(map_context: object, results: Mapping, *, env=None) -> Surroundings:
    """Decide whether the report may show the surroundings and render the maps when
    it may (ruling Y5). The location sheet takes the wide locator; page 1 takes the
    COMPACT CLOSE frame; the constraints sheet takes the large close frame. A missing map
    document, a failed one-outline check or maps that do not draw all yield
    ``available=False`` with a short limitation line - never a partial or mismatched
    picture (S2, S6)."""
    if not isinstance(map_context, Mapping):
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)
    if not outlines_match(_subject_outline(map_context), readers.results_lot_outline(results)):
        return Surroundings(False, reason=_SURROUNDINGS_UNAVAILABLE)

    def embed(fn_name, layers, frame, **overlay):
        return drawings_embed.embed_map(fn_name, map_context, layers=layers, frame=frame, env=env,
                                        **overlay)

    # Page 2 is the neighbourhood locator only (D-094 R014/R074); the block close-up
    # is still built here (restorable) but not printed (render shows the locator). Page 1
    # takes the COMPACT close frame (the close composition at the 88 mm column; M5-T166
    # rework 1, G3/G4 F1); the constraints sheet takes the large close frame - the
    # subject and its edge-sharing neighbours dominate, dimensioned on page 3 (M5-T166).
    # Only the two site-context frames carry the 1.5.0 overlay (the established
    # constraint lines + the other-basis dimensions); passing None leaves them, and the
    # neighbourhood/block locators, byte-identical (M5-T175 rework 1; S1/S12).
    constraint_lines, input_facts = _overlay_data(results)
    overlay = {"constraint_lines": constraint_lines, "input_facts": input_facts}
    neighbourhood = embed("render_neighbourhood_map", map_caption.NEIGHBOURHOOD_LAYERS, "wide")
    block = embed("render_block_map", map_caption.BLOCK_LAYERS, "wide")
    summary_plan = embed("render_site_context_plan", map_caption.SITE_LAYERS, "summary_close",
                         **overlay)
    # The illustrative building footprint is drawn ONLY on the large close frame (part B1),
    # so the floor-1 plate ring is passed to this embed alone; the summary close frame and
    # the wide locators never receive it and stay byte-identical (S1/S6).
    report_plan = embed("render_site_context_plan", map_caption.SITE_LAYERS, "close",
                        placed_footprint=placed_footprint(results), **overlay)
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
    """The 'Where is the lot?' sheet: ONE neighbourhood locator (D-094 R014/R074).
    The block close-up is no longer printed here - the dimensioned constraints close
    frame on the next sheet does that job - but the stack can still take a second
    figure later without a redesign. One short line when the surroundings are not
    available. No photo, empty frame or photo wording (ruling Y9)."""
    children: list[object] = [el("h2", QUESTION)]
    if not surroundings.available:
        children.append(short_line(surroundings.reason or _SURROUNDINGS_UNAVAILABLE))
        return el("div", *children, class_="location-sheet")
    stack = [fig for fig in (_wide_figure("Neighbourhood", surroundings.neighbourhood),)
             if fig is not None]
    children.append(el("div", *stack, class_="location-stack"))
    return el("div", *children, class_="location-sheet")
