"""Geometry primitives for the architect drawing-sheet reader profile (M5-T083, D-087
PDF-1): the frozen output value types AND the pure 2-D affine / Bezier algebra over them.

Page-scoped vector primitives are expressed in PDF **user space** — the page's default
user space (1 unit = 1/72 inch, scaled by ``/UserUnit``), with the origin at the
``/MediaBox`` coordinate system after every ``cm`` concatenation has been applied. These
coordinates are deliberately NOT world coordinates: unit/scale confirmation (feet per
drawing unit, the drawing's stated scale) is a separate, human-confirmed C2 packet. Every
page therefore also carries its ``media_box`` (the page box) and ``user_unit`` so a later
stage can convert without re-reading the PDF.

No I/O, no PDF parsing, no clock, no randomness: the value types are immutable frozen
dataclasses and the algebra is a set of pure functions. Interpretation of PDF content
lives in :mod:`app.drawings.sheet_reader`, which composes this module.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

#: Cubic-Bezier subdivision depth cap (2**24 segments) — a bounded-work safety net; the
#: reader's total-point budget is the hard limit.
MAX_FLATTEN_DEPTH = 24

#: A 2-D affine transform ``(a, b, c, d, e, f)`` in the PDF matrix convention
#: (ISO 32000-1 §8.3.3 [recalled - verify]): a row-vector point ``[x y 1]`` maps to
#: ``(a*x + c*y + e, b*x + d*y + f)``. Full affine — rotation and shear included.
Matrix = tuple[float, float, float, float, float, float]

#: A 2-D point in user space.
Point = tuple[float, float]


def concat_matrix(m: Matrix, ctm: Matrix) -> Matrix:
    """Concatenate ``m`` onto ``ctm`` (``m`` applied first): ISO 32000-1 §8.3.4 ``cm``
    semantics [recalled - verify]. Returns the 3x3 product ``M * CTM`` in (a..f) form."""
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = ctm
    return (
        a1 * a2 + b1 * c2,
        a1 * b2 + b1 * d2,
        c1 * a2 + d1 * c2,
        c1 * b2 + d1 * d2,
        e1 * a2 + f1 * c2 + e2,
        e1 * b2 + f1 * d2 + f2,
    )


def apply_matrix(m: Matrix, x: float, y: float) -> Point:
    """Map user point ``(x, y)`` through ``m`` (row-vector convention, §8.3.4)."""
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def _mid(p: Point, q: Point) -> Point:
    return ((p[0] + q[0]) * 0.5, (p[1] + q[1]) * 0.5)


def point_line_distance(p: Point, a: Point, b: Point) -> float:
    """Perpendicular distance from ``p`` to the line through ``a`` and ``b`` (or to ``a``
    when the chord is degenerate)."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)
    if length == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    return abs(dx * (a[1] - p[1]) - dy * (a[0] - p[0])) / length


def cubic_flat(p0: Point, p1: Point, p2: Point, p3: Point, tol: float) -> bool:
    """A cubic segment is flat when BOTH control points lie within ``tol`` of the chord.

    The bound is on the curve's PERPENDICULAR / cross-track deviation from the chord line
    (§8.5.2.2 [recalled - verify]): projecting the error onto the chord normal, the control
    points' along-chord offsets cancel, so ``max(dist(p1), dist(p2)) <= tol`` bounds the
    perpendicular error. It is NOT a guaranteed bound on distance-to-SEGMENT when a control
    point projects outside the chord endpoints (along-chord overshoot on S-curves/cusps);
    midpoint de Casteljau subdivision is exact, and the ``and`` (both control points) — not
    ``or`` — is what makes the guarantee hold on ASYMMETRIC curves.
    """
    return (
        point_line_distance(p1, p0, p3) <= tol
        and point_line_distance(p2, p0, p3) <= tol
    )


def is_finite_point(p: Point) -> bool:
    """True when both components of ``p`` are finite (no ``inf`` / ``nan``)."""
    return math.isfinite(p[0]) and math.isfinite(p[1])


def flatten_cubic(
    p0: Point,
    p1: Point,
    p2: Point,
    p3: Point,
    tol: float,
    out: list[Point],
    depth: int,
    budget: int,
) -> bool:
    """Adaptive de Casteljau flattening under a HARD point ``budget``.

    Subdivide until flat within ``tol`` (or the depth cap), appending every point AFTER
    ``p0`` up to and including ``p3`` to ``out`` — but NEVER letting ``out`` grow beyond
    ``budget`` points. Returns ``True`` when the whole curve was flattened within budget,
    and ``False`` the moment the budget would be exceeded (the caller must then refuse).

    Threading the caller's remaining page-point budget bounds a SINGLE curve's transient
    allocation to ``budget`` points, so a valid-but-degenerate curve (huge control
    coordinates that never satisfy ``cubic_flat``) cannot first materialize the full
    ``2**MAX_FLATTEN_DEPTH`` leaf list before the reader charges its page-wide point budget.
    """
    if len(out) >= budget:
        return False
    if depth >= MAX_FLATTEN_DEPTH or cubic_flat(p0, p1, p2, p3, tol):
        out.append(p3)
        return True
    p01 = _mid(p0, p1)
    p12 = _mid(p1, p2)
    p23 = _mid(p2, p3)
    p012 = _mid(p01, p12)
    p123 = _mid(p12, p23)
    pm = _mid(p012, p123)
    if not flatten_cubic(p0, p01, p012, pm, tol, out, depth + 1, budget):
        return False
    return flatten_cubic(pm, p123, p23, p3, tol, out, depth + 1, budget)


@dataclass(frozen=True)
class SheetPolyline:
    """One painted subpath, flattened to a user-space polyline.

    Bezier curves are flattened to straight segments (see the reader's declared
    ``flatten_tolerance``). ``closed`` records an explicit ``h`` close (the last point
    connects back to the first without duplicating it). ``stroked`` / ``filled`` record
    how the containing path was painted; a path ended by ``n`` (clip-only / no paint)
    has both ``False`` and is still surfaced so a consumer sees the geometry.
    """

    points: tuple[Point, ...]
    closed: bool
    stroked: bool
    filled: bool


@dataclass(frozen=True)
class SheetTextRun:
    """One shown text run, anchored at its user-space origin.

    Full text + CTM composition is applied, so rotated/sheared text is placed correctly
    (the survey profile refuses rotated text; this profile keeps it). ``matrix`` is the
    composed text-rendering matrix (text space -> user space) so a consumer can recover
    the run's angle and scale; ``font_size`` is the nominal ``Tf`` size (glyph metrics
    and text advance are not modelled — a documented simplification). Because advance is
    not modelled, ``x`` / ``y`` are EXACT only for the FIRST show after each positioning
    operator (``Td`` / ``TD`` / ``Tm`` / ``T*`` / ``'`` / ``"``); a second ``Tj`` / ``TJ``
    on the same line without an intervening positioning op is reported at the un-advanced
    origin. Individually positioned drawing-sheet labels (the common case) are exact.
    """

    text: str
    x: float
    y: float
    font_size: float
    matrix: Matrix


@dataclass(frozen=True)
class SheetImage:
    """One image XObject placement: COUNTED and disclosed, NEVER decoded.

    ``matrix`` maps the image's unit square ``[0,1] x [0,1]`` to user space (its placement
    rectangle, per ISO 32000-1 §8.9.5 [recalled - verify]). ``width`` / ``height`` /
    ``bits_per_component`` / ``color_space`` are read from the image dictionary keys, never
    from the (undecoded) sample bytes; any that is absent or non-trivial is ``None``.
    """

    name: str
    matrix: Matrix
    width: int | None
    height: int | None
    bits_per_component: int | None
    color_space: str | None


@dataclass(frozen=True)
class SheetPage:
    """One interpreted page: its box, user unit, declared flattening tolerance, and the
    flat vector/text/image primitives in execution order.

    ``shading_skips`` / ``inline_image_skips`` are the DISCLOSED counts of two non-geometry
    constructs the reader deliberately skips rather than refusing (M5-T118, D-087 P3): the
    ``sh`` shading operator (ISO 32000-1 §8.7.4.2, a colour fill, not linework) and inline
    images (``BI``/``ID``/``EI``, §8.9.7, raster samples, never decoded). They paint nothing
    into ``polylines`` / ``images``, so the page surfaces the count for honest disclosure. Both
    default to 0, so a page with neither is byte-identical to the pre-P3 output type."""

    index: int
    media_box: tuple[float, float, float, float]
    user_unit: float
    flatten_tolerance: float
    polylines: tuple[SheetPolyline, ...]
    text_runs: tuple[SheetTextRun, ...]
    images: tuple[SheetImage, ...]
    shading_skips: int = 0
    inline_image_skips: int = 0

    @property
    def image_count(self) -> int:
        """Number of image XObject placements counted on this page (never decoded)."""
        return len(self.images)


@dataclass(frozen=True)
class SheetDocument:
    """Every interpreted page, plus the flattening tolerance declared for the read."""

    flatten_tolerance: float
    pages: tuple[SheetPage, ...]

    @property
    def shading_skips(self) -> int:
        """Total ``sh`` shading operators skipped across all pages (M5-T118; §8.7.4.2)."""
        return sum(page.shading_skips for page in self.pages)

    @property
    def inline_image_skips(self) -> int:
        """Total inline images (``BI``/``ID``/``EI``) skipped across all pages (M5-T118; §8.9.7)."""
        return sum(page.inline_image_skips for page in self.pages)


@dataclass(frozen=True)
class SheetRefusal:
    """Typed refusal VALUE — the reader profile never raises on any input.

    ``origin`` is ``"strict_reader"`` when the refusal is a wrapped
    :class:`~app.documents.extraction.pdf_lexer.PdfSyntaxError` /
    :class:`~app.documents.extraction.pdf_xref.UnsupportedPdfFeature` from the reused
    strict reader (malformed bytes, encryption, cross-reference streams, ...), or
    ``"sheet_profile"`` when it is one of this profile's own bounds (an over-limit stream,
    an XObject cycle, a too-deep recursion, an unsupported content operator, ...).
    """

    reject_code: str
    feature: str
    detail: str
    origin: str

    STRICT_READER: ClassVar[str] = "strict_reader"
    SHEET_PROFILE: ClassVar[str] = "sheet_profile"

    def to_payload(self) -> dict[str, object]:
        return {
            "reject_code": self.reject_code,
            "feature": self.feature,
            "detail": self.detail,
            "origin": self.origin,
        }
