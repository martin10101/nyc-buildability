"""Area-illustration drawing kernel (task M5-T183; D-094 R087-R098, R024/R092, G-14).

Draws the two-zone area illustration from ONE 1.5.0 ``area_allocation`` block:

* NOT fitted (``fitted`` is false) -> a proportional horizontal bar split by the
  apartment share, sitting beside the building diagram, with no zone inside any
  outline;
* FITTED (``fitted`` is true, the building's ``placement`` is ``placed`` and
  carries an outline) -> two zones inside that footprint, split by a single
  vertical division at the share ratio, with no bar.

The two zone labels and the one caption are the presentation-token strings
verbatim; exactly one stated percentage is printed, ``round(share * 100)`` read
from the block (never hardcoded). The two zones share one fill and are told
apart by their hatch, not by colour. No room, unit wall, apartment count, stair
or elevator is ever drawn, and no line sits inside a zone other than the single
proportional division.

Fail CLOSED (mirroring :mod:`.section`'s ``Unavailable`` pattern): a missing or
garbled block, a non-finite share, a share outside 0.60-0.75, an apartment/other
split that does not reconcile with the total or with the share, or a fitted block
with no placed outline returns :class:`Unavailable` - never a drawn guess. A
fitted block without an outline draws nothing labelled fitted (never a bar
mislabelled).

Leaf kit module: it imports only the kit's own ``model``, ``presentation_tokens``
and ``svg`` helpers - nothing from ``drawings/report`` or ``drawings/maps``
(layering). The hatch patterns are built locally (the shared style table carries
no apartment/other kind and is not this task's to edit), mirroring the structure
of :mod:`.hatches`.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from .model import Drawing, Label, Point, Unavailable
from .presentation_tokens import COLOR, TYPE, WORDING
from .svg import element, num, path_data, polyline_data, svg_document, text_element

__all__ = ["draw_area_allocation"]

# The block's fixed contract values (results.schema.json $defs area_measure /
# plate_conversion_statement / illustrative_label). The kernel prints the block's
# OWN values; it compares them with these to refuse a garbled block (it does not
# substitute them - no default stands for a fact).
_MEASURE = "residential_floor_area"
_MEASURE_WORDS = "Residential floor area"
_CONVERSION = (
    "plate = zoning floor area per storey; no gross-up, exclusions or "
    "wall-thickness conversion worked"
)
_LABEL = "Illustrative"

# The one share the block may carry (schema: 0.60 to 0.75).
_SHARE_MIN = 0.60
_SHARE_MAX = 0.75
# apartment + other must equal total within the two-decimal display rounding (the
# results_way_rules.py tolerance, mirrored).
_AREA_TOL = 0.01 + 1e-9
# The drawn proportion equals the share within 0.5 percent (R091); the same
# tolerance guards the defensive apartment/total == share consistency check.
# NOTE: the apartment/total == share WAY RULE (DB-248) stays owned by M5-T172;
# here it is only a defensive refusal so the kernel never draws an inconsistent
# split.
_SHARE_TOL = 0.005 + 1e-9

# A placed footprint the kernel can draw truthfully carries a handful of vertices
# and finite coordinates of a plausible magnitude. A ring larger than this cap
# (F3), a coordinate that is not a finite number (F1: NaN / +/-inf), or a
# coordinate whose magnitude would overflow the shoelace and scaling arithmetic to
# inf/nan (F1) is NOT a drawable footprint and fails CLOSED to Unavailable - never
# a malformed drawing or an exception. The coordinates are in feet; even an
# absolute projected coordinate (EPSG:2263 NY state-plane, about 1.1e6 ft for New
# York City) sits far below the magnitude bound, while a value at or above it
# overflows the shoelace products.
_MAX_OUTLINE_VERTICES = 1000
_COORD_MAX = 1.0e9

# Readability floor (R098, DB-246): the drawing-label PREFERRED print size (9.5 pt);
# never TYPOGRAPHY.label_pt (8.0) nor the 7.5 scale-bar size. Every label is at
# least 8.5 pt at the printed size.
_LABEL_PT = float(TYPE["drawing-label"]["print_pt_preferred"])

# Both zones carry ONE neutral fill, so colour alone cannot tell them apart; the
# hatch does (R098). The hatch lines and outlines are the shared ink.
_ZONE_FILL = COLOR["selected"]
_OUTLINE = COLOR["supporting"]
_HATCH_INK = COLOR["ink"]

# Two distinct hatch families (angle only differs), built locally.
_HATCH_APARTMENT = "aa-hatch-apartment"
_HATCH_OTHER = "aa-hatch-other"
_HATCH_SPACING = 5.0
_HATCH_WEIGHT = 0.5

# Layout (user units = points; 1 pt = 1/72 in). A4 report drawing stays well under
# 182 mm x 150 mm.
# Wide enough that the full conversion statement reads on one line at 9.5 pt and
# stays within the A4 report drawing width (182 mm = 515.9 pt).
_MARGIN = 24.0
_CANVAS_W = 468.0
_PCT_Y = 30.0
_ART_TOP = 44.0
_BAR_W = 292.0
_BAR_H = 44.0
_FP_SPAN = 196.0  # the footprint's longer side fills this many points
_ROW_H = 20.0
_SWATCH = 12.0
_GAP = 16.0


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _plausible_coord(value: object) -> bool:
    """True when ``value`` is a finite number whose magnitude cannot overflow the
    geometry arithmetic (F1: rejects NaN, +/-inf, a non-number, and an over-large
    magnitude such as 1e308)."""
    return _finite_number(value) and abs(float(value)) <= _COORD_MAX


def _hatch_pattern(pattern_id: str, angle_deg: float) -> str:
    """One ``<pattern>`` of parallel lines at ``angle_deg`` (local; mirrors
    :func:`app.drawings.kit.hatches._pattern`). SVG y points down, so the CAD
    angle is negated."""
    spacing = _HATCH_SPACING
    line = element(
        "line",
        [
            ("x1", 0.0),
            ("y1", spacing / 2.0),
            ("x2", float(spacing)),
            ("y2", spacing / 2.0),
            ("stroke", _HATCH_INK),
            ("stroke-width", float(_HATCH_WEIGHT)),
        ],
    )
    return element(
        "pattern",
        [
            ("id", pattern_id),
            ("patternUnits", "userSpaceOnUse"),
            ("width", float(spacing)),
            ("height", float(spacing)),
            ("patternTransform", f"rotate({num(-float(angle_deg))})"),
        ],
        line,
    )


def _defs() -> str:
    return _hatch_pattern(_HATCH_APARTMENT, 45.0) + _hatch_pattern(_HATCH_OTHER, 135.0)


def _rect(x: float, y: float, w: float, h: float, *, fill: str, role: str) -> str:
    return element(
        "rect",
        [
            ("x", float(x)),
            ("y", float(y)),
            ("width", float(w)),
            ("height", float(h)),
            ("fill", fill),
            ("stroke", _OUTLINE),
            ("stroke-width", 0.75),
            ("data-role", role),
        ],
    )


def _hatched_rect(x: float, y: float, w: float, h: float, *, pattern: str, role: str) -> list[str]:
    """A neutral-filled rectangle with its hatch overlaid (two paths, like the
    kit's :meth:`Sheet.area`)."""
    return [
        _rect(x, y, w, h, fill=_ZONE_FILL, role=role),
        element(
            "rect",
            [
                ("x", float(x)),
                ("y", float(y)),
                ("width", float(w)),
                ("height", float(h)),
                ("fill", f"url(#{pattern})"),
                ("stroke", "none"),
            ],
        ),
    ]


def _zone(points: Sequence[Point], *, pattern: str, role: str) -> list[str]:
    """A polygon zone: a neutral fill with its hatch overlaid."""
    d = path_data([list(points)])
    return [
        element(
            "path",
            [
                ("d", d),
                ("fill", _ZONE_FILL),
                ("fill-rule", "evenodd"),
                ("stroke", _OUTLINE),
                ("stroke-width", 0.75),
                ("data-role", role),
            ],
        ),
        element(
            "path",
            [("d", d), ("fill", f"url(#{pattern})"), ("fill-rule", "evenodd"), ("stroke", "none")],
        ),
    ]


# -- geometry (polygon split by a single vertical division at the share ratio) --


def _poly_area(pts: Sequence[Point]) -> float:
    area = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def _clip_x(pts: Sequence[Point], c: float, keep_left: bool) -> list[Point]:
    """Sutherland-Hodgman clip of ``pts`` against the vertical line x = c, keeping
    the x <= c side (``keep_left``) or the x >= c side."""
    out: list[Point] = []
    n = len(pts)
    for i in range(n):
        cur = pts[i]
        nxt = pts[(i + 1) % n]
        cur_in = cur[0] <= c if keep_left else cur[0] >= c
        nxt_in = nxt[0] <= c if keep_left else nxt[0] >= c
        if cur_in:
            out.append(cur)
        if cur_in != nxt_in:
            t = (c - cur[0]) / (nxt[0] - cur[0])
            out.append((c, cur[1] + t * (nxt[1] - cur[1])))
    return out


def _division_x(pts: Sequence[Point], share: float) -> float:
    """The x at which a vertical line splits ``pts`` so the area to its left is
    ``share`` of the whole. Deterministic bisection (area is monotonic in x)."""
    total = _poly_area(pts)
    target = share * total
    lo = min(p[0] for p in pts)
    hi = max(p[0] for p in pts)
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if _poly_area(_clip_x(pts, mid, keep_left=True)) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# -- the shared footer (percentage, legend, measure, conversion, caption) --


def _text(parts: list[str], labels: list[Label], x: float, y: float, text: str, role: str,
          *, size: float = _LABEL_PT) -> None:
    parts.append(text_element(x, y, text, size=size, source=None, role=role))
    labels.append(Label(text, "", role))


def _footer(parts: list[str], labels: list[Label], top: float, *, caption: bool) -> float:
    """Legend (two hatch swatches with the token labels), the measure basis tag,
    the byte-exact conversion statement and the one caption. Returns the bottom y."""
    y = top
    for pattern, role, swatch_role, text in (
        (_HATCH_APARTMENT, "area_label_apartment", "area_swatch_apartment",
         WORDING["area_zone_apartment"]),
        (_HATCH_OTHER, "area_label_other", "area_swatch_other", WORDING["area_zone_other"]),
    ):
        parts.append(_rect(_MARGIN, y, _SWATCH, _SWATCH, fill=_ZONE_FILL, role=swatch_role))
        parts.append(
            element(
                "rect",
                [
                    ("x", float(_MARGIN)),
                    ("y", float(y)),
                    ("width", float(_SWATCH)),
                    ("height", float(_SWATCH)),
                    ("fill", f"url(#{pattern})"),
                    ("stroke", "none"),
                ],
            )
        )
        _text(parts, labels, _MARGIN + _SWATCH + 6.0, y + _SWATCH - 2.0, text, role)
        y += _ROW_H
    y += 6.0
    _text(parts, labels, _MARGIN, y, _MEASURE_WORDS, "area_measure")
    y += _ROW_H
    _text(parts, labels, _MARGIN, y, _CONVERSION, "area_conversion")
    y += _ROW_H
    if caption:
        _text(parts, labels, _MARGIN, y, WORDING["area_illustration_caption"], "caption")
        y += _ROW_H
    return y


def _finish(parts: list[str], labels: list[Label], fraction: float, bottom: float) -> Drawing:
    body = [
        element(
            "g",
            [
                ("data-drawing-part", "area_allocation"),
                ("data-apartment-fraction", float(fraction)),
            ],
            "".join(parts),
        )
    ]
    height = bottom + 14.0
    svg = svg_document(
        width=_CANVAS_W, height=height, drawing="area_allocation",
        title="Area allocation illustration", defs=_defs(), body=body,
    )
    kinds = ("apartment_area", "other_building_area")
    return Drawing("area_allocation", svg, tuple(labels), kinds)


# -- validation (fail closed) --


def _validate(allocation: object) -> Unavailable | tuple[float, bool]:
    """Return ``(share, fitted)`` for a sound block, or ``Unavailable``. Every
    optional fact is tested explicitly - no truthiness test stands in for a value,
    and no default stands for a missing fact."""
    if not isinstance(allocation, Mapping):
        return Unavailable("area_allocation", "There is no area allocation to draw.",
                           "missing_input", "/area_allocation")
    if allocation.get("label") != _LABEL or allocation.get("measure") != _MEASURE \
            or allocation.get("conversion_statement") != _CONVERSION:
        return Unavailable("area_allocation", "The area allocation is incomplete.",
                           "schema_invalid", "/area_allocation")
    share = allocation.get("share")
    if not _finite_number(share):
        return Unavailable("area_allocation", "The apartment share is not a number.",
                           "schema_invalid", "/area_allocation/share")
    share = float(share)
    if share < _SHARE_MIN or share > _SHARE_MAX:
        return Unavailable("area_allocation", "The apartment share is outside the range shown.",
                           "schema_invalid", "/area_allocation/share")
    apartment = allocation.get("apartment_area_sqft")
    other = allocation.get("other_area_sqft")
    total = allocation.get("total_sqft")
    if not (_finite_number(apartment) and _finite_number(other) and _finite_number(total)):
        return Unavailable("area_allocation", "The area split is not given in numbers.",
                           "schema_invalid", "/area_allocation")
    apartment, other, total = float(apartment), float(other), float(total)
    if total <= 0.0 or abs((apartment + other) - total) > _AREA_TOL:
        return Unavailable("area_allocation",
                           "The apartment and other areas do not add up to the total.",
                           "inconsistent", "/area_allocation/total_sqft")
    if abs((apartment / total) - share) > _SHARE_TOL:
        return Unavailable("area_allocation",
                           "The apartment area does not match the share shown.",
                           "inconsistent", "/area_allocation/share")
    fitted = allocation.get("fitted")
    if fitted is not True and fitted is not False:
        return Unavailable("area_allocation", "It is not stated whether the footprint is fitted.",
                           "schema_invalid", "/area_allocation/fitted")
    return share, fitted


def _outline_unavailable(reason: str) -> Unavailable:
    """A placed footprint the kernel cannot draw truthfully (F1/F2/F3). The reason
    is plain words only - no field or record names."""
    return Unavailable("area_allocation", reason, "outline_invalid", "/placement/outline")


def _placed_ring(placement: object) -> list[Point] | Unavailable | None:
    """The placed footprint's exterior ring; ``None`` when no outline is placed;
    ``Unavailable`` when an outline IS placed but cannot be drawn truthfully.

    Fails CLOSED on a footprint with too many points (F3), a point that is not a
    finite number of plausible magnitude (F1: NaN, +/-inf, a non-number or an
    over-large magnitude that would overflow to inf/nan), or no area to divide
    (F2: a zero-area collinear or zero-width ring) - never a malformed drawing and
    never an unhandled ``ZeroDivisionError``/``ValueError`` downstream.
    """
    if not isinstance(placement, Mapping) or placement.get("status") != "placed":
        return None
    outline = placement.get("outline")
    if not isinstance(outline, Sequence) or isinstance(outline, (str, bytes)) or not outline:
        return None
    ring = outline[0]
    if not isinstance(ring, Sequence) or isinstance(ring, (str, bytes)):
        return None
    if len(ring) > _MAX_OUTLINE_VERTICES:  # F3: a footprint carries a handful of vertices
        return _outline_unavailable("The footprint has too many points to draw.")
    pts: list[Point] = []
    for vertex in ring:  # F1: every coordinate a finite number of plausible magnitude
        if not isinstance(vertex, Sequence) or isinstance(vertex, (str, bytes)) or len(vertex) < 2:
            return _outline_unavailable("The footprint shape is not given as points.")
        if not (_plausible_coord(vertex[0]) and _plausible_coord(vertex[1])):
            return _outline_unavailable("The footprint shape has a point that is out of range.")
        pts.append((float(vertex[0]), float(vertex[1])))
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        return None
    if _poly_area(pts) <= 0.0:  # F2: a zero-area footprint cannot be split into two zones
        return _outline_unavailable("The footprint has no area to show as two zones.")
    return pts


# -- the two drawn states --


def _draw_bar(share: float, *, caption: bool) -> Drawing:
    parts: list[str] = []
    labels: list[Label] = []
    pct = round(share * 100)
    _text(parts, labels, _MARGIN, _PCT_Y, f"{pct}% apartment area", "area_percentage")
    apartment_w = _BAR_W * share
    parts += _hatched_rect(_MARGIN, _ART_TOP, apartment_w, _BAR_H,
                           pattern=_HATCH_APARTMENT, role="area_bar_apartment")
    parts += _hatched_rect(_MARGIN + apartment_w, _ART_TOP, _BAR_W - apartment_w, _BAR_H,
                           pattern=_HATCH_OTHER, role="area_bar_other")
    fraction = apartment_w / _BAR_W
    bottom = _footer(parts, labels, _ART_TOP + _BAR_H + _GAP, caption=caption)
    return _finish(parts, labels, fraction, bottom)


def _draw_zones(share: float, ring: list[Point], *, caption: bool) -> Drawing:
    parts: list[str] = []
    labels: list[Label] = []
    pct = round(share * 100)
    _text(parts, labels, _MARGIN, _PCT_Y, f"{pct}% apartment area", "area_percentage")

    total = _poly_area(ring)
    c = _division_x(ring, share)
    apartment_poly = _clip_x(ring, c, keep_left=True)
    other_poly = _clip_x(ring, c, keep_left=False)
    fraction = _poly_area(apartment_poly) / total

    minx = min(p[0] for p in ring)
    maxx = max(p[0] for p in ring)
    miny = min(p[1] for p in ring)
    maxy = max(p[1] for p in ring)
    span = max(maxx - minx, maxy - miny)
    k = _FP_SPAN / span if span > 0 else 1.0

    def place(point: Point) -> Point:
        x, y = point
        return (_MARGIN + (x - minx) * k, _ART_TOP + (maxy - y) * k)

    parts += _zone([place(p) for p in apartment_poly], pattern=_HATCH_APARTMENT,
                   role="area_zone_apartment")
    parts += _zone([place(p) for p in other_poly], pattern=_HATCH_OTHER,
                   role="area_zone_other")
    # The footprint outline, over the zones (one clean edge, no detail inside).
    parts.append(
        element(
            "path",
            [
                ("d", path_data([[place(p) for p in ring]])),
                ("fill", "none"),
                ("stroke", _HATCH_INK),
                ("stroke-width", 1.0),
                ("data-role", "area_footprint"),
            ],
        )
    )
    # The single proportional division (the only line inside the footprint).
    on_division = [p for p in apartment_poly if abs(p[0] - c) <= 1e-6]
    if len(on_division) >= 2:
        y_lo = min(p[1] for p in on_division)
        y_hi = max(p[1] for p in on_division)
    else:  # defensive: fall back to the footprint's vertical extent at the cut
        y_lo, y_hi = miny, maxy
    parts.append(
        element(
            "path",
            [
                ("d", polyline_data([place((c, y_lo)), place((c, y_hi))])),
                ("fill", "none"),
                ("stroke", _HATCH_INK),
                ("stroke-width", 1.0),
                ("data-role", "area_division"),
            ],
        )
    )
    fp_h = (maxy - miny) * k
    bottom = _footer(parts, labels, _ART_TOP + fp_h + _GAP, caption=caption)
    return _finish(parts, labels, fraction, bottom)


def draw_area_allocation(
    allocation: Mapping, *, placement: Mapping | None = None, caption: bool = True
) -> Drawing | Unavailable:
    """The two-zone area illustration for one worked building, or ``Unavailable``.

    ``allocation`` is a 1.5.0 ``area_allocation`` block; ``placement`` is that
    building's optional ``placement`` block. When ``allocation.fitted`` is false a
    proportional bar is drawn; when it is true and ``placement`` is ``placed`` with
    an outline, two zones are drawn inside that footprint. A fitted block with no
    placed outline returns ``Unavailable`` - nothing is drawn, and never a bar
    mislabelled fitted. ``caption=False`` omits the drawing's own caption (the
    report prints one beneath it); the default keeps it.
    """
    checked = _validate(allocation)
    if isinstance(checked, Unavailable):
        return checked
    share, fitted = checked
    if not fitted:
        return _draw_bar(share, caption=caption)
    ring = _placed_ring(placement)
    if isinstance(ring, Unavailable):
        return ring
    if ring is None:
        return Unavailable(
            "area_allocation",
            "The footprint has not been placed on the lot, so the zones cannot be drawn yet.",
            "not_placed", "/placement/outline",
        )
    return _draw_zones(share, ring, caption=caption)
