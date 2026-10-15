"""Dimension lines for the constraints close frame (M5-T166, D-094 R014/R015).

Each dimension is anchored to ONE edge of the subject lot's outline: two witness
lines rise from the edge's own endpoints to an offset dimension line, and the
label shows only the figure, e.g. ``"99.98 ft"``. The drawing states the shared
measurement basis ONCE in a note directly under it
(``"All dimensions: city map outline, not surveyed."``; owner question K1,
D-094 R116, 2026-10-12) rather than repeating it on every label. A label carries
a short basis tag again ONLY when one drawing MIXES bases (no close frame does
today - all four edges are one gis outline).

The outline the close frame draws is the MapPLUTO (``gis``) outline, so the only
basis the 1.4.0 document carries is the city map outline (short form on drawings
"map outline"; D-094 contract change 2026-10-11, amended 2026-10-12). No tax-map
figure is drawn - none is in the 1.4.0 document, and a tax-map value is never
merged with a GIS outline (NB-04). An edge too short to carry a legible dimension
is left undimensioned (never a bare half-number). If a label cannot be placed at
the minimum size without a collision the frame FAILS rather than shrinking the
label or dropping the dimension silently (presentation contract section 6).

Witness-line endpoints lie on the edge's own projected vertices (``fr.px`` of the
ring vertex), so a dimension always measures the edge it is drawn against.
Coordinates are screen points.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.drawings.kit import geometry as geo
from app.drawings.kit.labels import Box, format_feet, format_number
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import style_for
from app.drawings.kit.svg import element, num

from .context_scene import ViewFrame, place, readable_angle, screen_dir
from .model import Point, Polygon

__all__ = [
    "DIMENSION_MIN_PT",
    "GIS_BASIS",
    "GIS_BASIS_NOTE",
    "GIS_BASIS_TAG",
    "MIN_LABELLED_EDGE_FT",
    "OTHER_BASIS_WORDS",
    "DimensionPlacementError",
    "DrawnDimension",
    "DrawnFact",
    "dimension_line_segments",
    "draw_edge_dimensions",
    "draw_other_basis_dimensions",
    "other_basis_label",
]

_Box = tuple[float, float, float, float]

# The plain-words basis for the city-map outline the close frame draws (the gis
# short form "map outline" from the design contract, plus the standing honesty
# qualifier). Every dimension on the close frame shares it; nothing is merged
# across bases.
GIS_BASIS = "map outline, not surveyed"
# Stated ONCE in a note directly under the drawing when every dimension shares one
# basis (owner question K1, D-094 R116, 2026-10-12); each label then shows only the
# figure ("103.88 ft"). This is the drawing's single-basis note.
GIS_BASIS_NOTE = "All dimensions: city map outline, not surveyed."
# The short basis tag a label carries ONLY when one drawing MIXES bases. No close
# frame mixes bases today (a single gis outline), so no label carries it; the code
# path and its test exist so a future mixed-basis drawing stays unambiguous.
GIS_BASIS_TAG = "map outline"

MIN_LABELLED_EDGE_FT = 6.0     # a shorter edge is left undimensioned (never a bare number)
DIMENSION_MIN_PT = 8.5         # dimension labels print at least 8.5 pt (contract section 6)
_WITNESS_OFFSET_PT = 12.0      # the dimension line sits this far outside the edge
_LABEL_STEP_PT = 2.0           # extra outward clearance tried per candidate
_LANE_STEPS = 10               # candidate positions outward (a wider lane clears a near line)
_ALONG_STEPS = 6               # candidate shifts along the edge, each way, when the lane is blocked


class DimensionPlacementError(RuntimeError):
    """A dimension label could not be placed at the minimum size without a
    collision. The close frame FAILS rather than shrinking the label below the
    minimum or dropping a dimension silently (presentation contract section 6)."""


@dataclass(frozen=True)
class DrawnDimension:
    """One drawn edge dimension. ``a_px``/``b_px`` are the edge's two projected
    vertices - the witness lines are anchored there, so the dimension measures the
    edge it is drawn against (S1). ``dim_a``/``dim_b`` are the dimension line's
    endpoints (``a_px``/``b_px`` offset outward); the witness lines run ``a_px->dim_a``
    and ``b_px->dim_b``. ``label_box`` is the placed label's bounds, so a caller can
    prove the label is crossed by no drawn line, its own dimension/witness lines
    included (rework 3)."""

    edge_index: int
    length_ft: float
    text: str
    basis: str
    a_px: Point
    b_px: Point
    label_box: Box
    dim_a: Point
    dim_b: Point


def _dimension_line(a: Point, b: Point, edge_index: int, kind: str) -> str:
    style = style_for("dimension")  # the annotation look (never added to the legend)
    return element("path", [
        ("d", f"M{num(a[0])} {num(a[1])} L{num(b[0])} {num(b[1])}"),
        ("fill", "none"), ("stroke", style.outline),
        ("stroke-width", style.line_weight_pt),
        ("data-role", "dimension-line"), ("data-kind", kind), ("data-edge", edge_index)])


def draw_edge_dimensions(
    sheet: Sheet, outline: Polygon, fr: ViewFrame, rect: _Box, *,
    basis: str = GIS_BASIS, basis_tag: str = GIS_BASIS_TAG, edge_bases=None,
    size: float = DIMENSION_MIN_PT,
    min_edge_ft: float = MIN_LABELLED_EDGE_FT, avoid_lines=None,
) -> list[DrawnDimension]:
    """Draw a dimension against every edge of ``outline`` at least ``min_edge_ft``
    long: two witness lines from the edge's own projected vertices to an offset
    dimension line, and a FIGURE-ONLY label ``"<length> ft"`` placed just outside
    the edge on a white background. The shared basis is stated once in a note under
    the drawing by the caller (K1); a label carries a short basis tag ONLY when the
    drawing mixes bases.

    ``edge_bases`` optionally maps an edge index to ``(basis, basis_tag)`` for a
    drawing whose edges have DIFFERENT bases. When it names more than one distinct
    basis the frame MIXES bases, so each label carries its own short tag
    (``"<length> ft, <tag>"``) to stay unambiguous; otherwise every label is
    figure-only. Each :class:`DrawnDimension` records its own basis.

    Returns the drawn dimensions. Raises :class:`DimensionPlacementError` when a
    label cannot be placed at ``size`` without a collision (S2)."""
    if size < DIMENSION_MIN_PT:
        raise DimensionPlacementError(
            f"dimension label size {size} pt is below the {DIMENSION_MIN_PT} pt minimum")
    ring = outline.exterior
    area = geo.signed_area(ring)
    # Pass 1: the geometry of every dimensioned edge, and its witness + dimension
    # lines, DRAWN now so each label - its own and the others' - is placed BESIDE all
    # of them with a clear gap (rework 3: a dimension line never strikes through its
    # own label, as the left-edge twin already did).
    specs = []
    dim_lines: list = []
    for i, (a, b) in enumerate(geo.edges(ring)):
        length = geo.edge_length(a, b)
        if length < min_edge_ft:
            continue
        e_basis, e_tag = basis, basis_tag
        if edge_bases is not None and i in edge_bases:
            e_basis, e_tag = edge_bases[i]
        pa, pb = fr.px(a), fr.px(b)
        nx, ny = geo.outward_normal(a, b, area)
        mid_world = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        n = screen_dir(mid_world[0], mid_world[1], (nx, ny), fr)
        dim_a = (pa[0] + n[0] * _WITNESS_OFFSET_PT, pa[1] + n[1] * _WITNESS_OFFSET_PT)
        dim_b = (pb[0] + n[0] * _WITNESS_OFFSET_PT, pb[1] + n[1] * _WITNESS_OFFSET_PT)
        # the witness lines are anchored ON the edge's own vertices (S1).
        sheet.parts.append(_dimension_line(pa, dim_a, i, "witness"))
        sheet.parts.append(_dimension_line(pb, dim_b, i, "witness"))
        sheet.parts.append(_dimension_line(dim_a, dim_b, i, "dimension"))
        dim_lines += [("dimension", [pa, dim_a]), ("dimension", [pb, dim_b]),
                      ("dimension", [dim_a, dim_b])]
        ang = readable_angle(math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])))
        mx, my = (dim_a[0] + dim_b[0]) / 2.0, (dim_a[1] + dim_b[1]) / 2.0
        specs.append((i, length, pa, pb, dim_a, dim_b, n, ang, mx, my, e_basis, e_tag))
    # A label shows only the figure unless the drawing MIXES bases, when each carries
    # its own short tag (owner K1, 2026-10-12).
    mixed = len({spec[-2] for spec in specs}) > 1
    # Pass 2: place each label BESIDE the dimension lines with a clear gap, on a white
    # background (``halo``). A label avoids the drawn lot boundaries (``avoid_lines``)
    # AND every witness/dimension line, its own included (``cross_max_len=0.0`` -> any
    # touch rejects). Candidates move outward and along the edge, least displacement
    # first; it fails rather than shrinks if no clear spot exists (contract section 6).
    base_avoid = list(avoid_lines or []) + dim_lines
    drawn: list[DrawnDimension] = []
    for i, length, pa, pb, dim_a, dim_b, n, ang, mx, my, e_basis, e_tag in specs:
        text = f"{format_feet(length)}, {e_tag}" if mixed else format_feet(length)
        elen = math.hypot(pb[0] - pa[0], pb[1] - pa[1]) or 1.0
        ux, uy = (pb[0] - pa[0]) / elen, (pb[1] - pa[1]) / elen
        step = size + _LABEL_STEP_PT
        grid = [(3.0 + j * step, al * step)
                for j in range(_LANE_STEPS) for al in range(-_ALONG_STEPS, _ALONG_STEPS + 1)]
        grid.sort(key=lambda oa: (oa[0] - 3.0) + abs(oa[1]))
        cands = [(mx + n[0] * out + ux * al, my + n[1] * out + uy * al, ang)
                 for out, al in grid]
        box = place(sheet, cands, text, size=size, source=f"edge:{outline.source}/0#{i}",
                    role="dimension", anchor="middle", rect=rect, pad=2.0,
                    avoid_lines=base_avoid, own=None, cross_max_len=0.0, halo=True)
        if box is None:
            raise DimensionPlacementError(
                f"edge {i} dimension {text!r} does not fit at {size} pt without a collision")
        drawn.append(DrawnDimension(i, length, text, e_basis, pa, pb, box, dim_a, dim_b))
    return drawn


def dimension_line_segments(dims: list[DrawnDimension]):
    """The witness and dimension line segments of every drawn dimension, as
    ('dimension', polyline). The scene's lot, street and width labels avoid these
    too, so no dimension line passes along a label (rework 3, defect 2)."""
    out = []
    for d in dims:
        out += [("dimension", [d.a_px, d.dim_a]), ("dimension", [d.b_px, d.dim_b]),
                ("dimension", [d.dim_a, d.dim_b])]
    return out


# --------------------------------------------------------------------------- #
# The input_facts' other-basis lot dimensions, drawn BESIDE the map-outline ones
# (D-094 R015; NB-04). The close frame draws the gis (city map outline) edges;
# when the document carries input_facts on OTHER bases (a printed-tax-map frontage,
# a recorded area, a GIS outline area), each is drawn with its OWN basis named, so
# a reader sees the bases apart. Two bases are NEVER merged into one figure
# (NB-04 'double_count_risk'); a GIS value reads "map outline", never "tax map".
# --------------------------------------------------------------------------- #
# The SHORT plain-word basis each label carries on a drawing (design contract
# wording, 2026-10-11). gis is "map outline" on a drawing (never "tax map"), a
# recorded value a "city record", a printed tax-map figure a "printed tax map".
OTHER_BASIS_WORDS = {
    "law": "zoning law",
    "deed": "deed",
    "survey": "survey",
    "printed_tax_map": "printed tax map",
    "approved_plan": "approved plan",
    "filing_attribute": "building filing",
    "administrative_record": "city record",
    "gis": "map outline",
    "derived": "worked from other values",
}
_AREA_UNITS = {"sq_ft", "sq ft", "square_feet", "sqft"}


@dataclass(frozen=True)
class DrawnFact:
    """One drawn other-basis lot dimension: the input fact's key, numeric value,
    unit and quantity basis, the plain-word ``basis_label`` on the drawing, the
    placed ``text`` ("<figure>, <basis>") and its ``label_box``. One fact, one
    basis - two bases are never merged into one label (S5)."""

    key: str
    value: float
    unit: str
    basis: str
    basis_label: str
    text: str
    label_box: Box


def _fact_figure(value: object, unit: object) -> str:
    if str(unit) in _AREA_UNITS:
        return f"{format_number(value)} sq ft"
    return format_feet(value)


def other_basis_label(fact: dict) -> str:
    """One input fact as a FIGURE plus its OWN basis, e.g. "100.5 ft, printed tax
    map" or "9,800 sq ft, city record". Each label names exactly one basis; two
    bases are never merged into one figure (D-094 R015; NB-04)."""
    basis = str(fact.get("basis"))
    word = OTHER_BASIS_WORDS.get(basis, basis)
    return f"{_fact_figure(fact.get('value'), fact.get('unit'))}, {word}"


def draw_other_basis_dimensions(
    sheet: Sheet, facts, rect: _Box, *, x: float | None = None, y: float | None = None,
    size: float = DIMENSION_MIN_PT, avoid_lines=None,
) -> list[DrawnFact]:
    """Draw the ``input_facts``' OTHER-basis lot dimensions BESIDE the map-outline
    dimensions (D-094 R015): ONE label per fact, each naming its own basis, stacked
    in a clear band so each basis reads distinctly. Nothing is averaged or merged
    (NB-04); a GIS value reads "map outline", never "tax map". Each label prints at
    at least ``size`` pt on a white background; it FAILS rather than shrinks or
    merges (presentation contract section 6). Returns the drawn facts."""
    x0 = x if x is not None else rect[0] + 6.0
    top = y if y is not None else rect[1] + 6.0
    drawn: list[DrawnFact] = []
    # Street mapped widths (``mapped_street_width:*``, basis gis since M5-T170) are NOT
    # lot dimensions: each fronting street already carries its "<n> ft mapped width"
    # label on its frontage (site_context_plan), so drawing it here too would duplicate
    # the figure with the lot outline's generic basis word "map outline" (DB-275; S10).
    # They are excluded from the other-basis LOT-dimension band; a lot's own gis fact
    # (a different key) still reads "map outline" here (S10).
    lot_facts = [f for f in (facts or [])
                 if not str(f.get("key")).startswith("mapped_street_width:")]
    for i, fact in enumerate(lot_facts):
        text = other_basis_label(fact)
        cy = top + i * (size + 4.0)
        # The stacked position first, then nudges down/right so a label finds a
        # clear spot (it fails rather than shrinks, never merges; S5).
        cands = [(x0, cy, 0.0)]
        cands += [(x0, cy + j * (size + 4.0), 0.0)
                  for j in range(len(lot_facts), len(lot_facts) + 8)]
        cands += [(x0 + 90.0, cy + j * (size + 4.0), 0.0) for j in range(0, 8)]
        box = place(sheet, cands, text, size=size,
                    source=f"input_fact:{fact.get('key')}", role="other-basis-dimension",
                    anchor="start", rect=rect, pad=1.0, avoid_lines=avoid_lines, own=None,
                    cross_max_len=2.0 * size, halo=True)
        if box is None:
            raise DimensionPlacementError(
                f"other-basis dimension {text!r} does not fit at {size} pt without a collision")
        basis = str(fact.get("basis"))
        drawn.append(DrawnFact(str(fact.get("key")), fact.get("value"), str(fact.get("unit")),
                               basis, OTHER_BASIS_WORDS.get(basis, basis), text, box))
    return drawn
