"""Deterministic, dependency-free PDF 1.4 site-plan sheet writer (M5-T085, D-087 BLUEPRINT-1).

Draws ONE landscape US-Letter page from canonical EPSG:2263 rings (US survey
feet): the lot outline, an optional proposed-building footprint, per-edge
dimension strings in feet, a chosen plot scale that fits the sheet with declared
margins, a scale bar, a grid-north arrow, and a title block. Every drawn value is
computed server-side from the 2263 inputs; nothing is drawn that the inputs do not
contain, and no legal conclusion is asserted (the sheet is stamped
``PROPOSED - NOT A CITY RECORD``).

Output subset (so the in-repo strict survey reader round-trips the bytes)
-----------------------------------------------------------------------
The content stream emits ONLY constructs the strict reader
(:mod:`app.documents.extraction.pdf_content`) interprets: straight lines
(``m``/``l``/``h``), axis-aligned rectangles (``re``), and horizontal text
(``BT``/``Tf``/``Td``/``Tj``/``ET``) under a translation-only CTM. No curves,
rotated/sheared transforms, images, or XObjects appear. Object, cross-reference,
and trailer structure follow ISO 32000-1 §7.5 (classic ``xref`` table, exact
byte offsets, ``startxref``/``%%EOF``); literal-string escaping of ``(`` ``)``
``\\`` runs through the single :func:`_escape_pdf_text` escaper per ISO 32000-1
§7.3.4.2 and all text is ASCII-sanitised.

Purity and determinism
----------------------
:func:`render_site_plan_pdf` is a pure function of its :class:`SitePlanInput`:
no clock, randomness, network, or I/O. ``generated_at`` and ``generator_version``
are inputs, never read from the environment, so identical inputs yield
byte-identical output (a golden sha256). The PUBLIC entry never raises on caller
data: a problem found before rendering is a RETURNED :class:`SitePlanRefusal`,
while a non-finite number found mid-render is RAISED by :func:`_num` as the
private :class:`_RenderRefused` carrier and converted back into a returned
:class:`SitePlanRefusal` at the one public boundary :func:`_finish` - so the
``_num`` docstring and this never-raise promise agree (DB-053 b). Only
IEEE-deterministic float operations (``+ - * /`` and ``math.sqrt``) feed the
emitted numbers, and every number is rounded before formatting, so the golden
bytes are stable across platforms.

Input hardening (M5-T091, DB-053 a-c)
-------------------------------------
Rings and vertices must be sequences (never ``str``/bytes, sets, or mappings);
each vertex is exactly two real numbers (``bool`` and numeric strings are
refused - parsing text to floats is the wiring layer's job). Every caller text
field must be a ``str`` and is screened, before anything is drawn, for the shared
claim-class words (:data:`app.cad.claim_words.CLAIM_CLASS_WORDS`) through the one
separator-collapsing screen :func:`app.cad.claim_words.contains_claim_word`, which
all three writers use (M5-T102). Both the given value and the ASCII-sanitised form
the sheet would print are screened, so a word hidden behind a non-ASCII separator
that prints as ``?`` is still caught. The number formatter :func:`_num` refuses a
non-finite value, so ``nan``/``inf`` can never reach the content stream as a token.

Wiring hardening (M5-T105, DB-059 a, d; DB-053 b)
------------------------------------------------
Every caller text field is additionally bounded at :data:`_MAX_TEXT_CHARS`
characters and refused - typed, naming the field, before anything is drawn - when
longer, so unbounded caller text cannot inflate the sheet once an export route
feeds it (DB-059 a). The per-vertex finiteness check covers x AND y (DB-059 d),
and the non-finite raise/return contract above is documented honestly (DB-053 b).
Valid output is byte-identical to the M5-T091 golden.

Export-seam hardening (M5-T109, DB-075 (a))
-------------------------------------------
:func:`_coerce_vertex` previously caught only ``OverflowError`` around ``float()``; a
``numbers.Real`` subclass whose ``__float__`` raises ``ValueError``/``TypeError`` passed the
``isinstance`` guard yet escaped the never-raise contract. The catch is broadened to a typed
``non_numeric_coordinate`` refusal (unreachable from JSON, but the public boundary must never
raise on caller data). Valid output stays byte-identical to the golden.
"""

from __future__ import annotations

import math
import numbers
from collections.abc import Sequence
from dataclasses import dataclass

from app.cad.claim_words import CLAIM_CLASS_WORDS, contains_claim_word

__all__ = [
    "CLAIM_CLASS_WORDS",
    "SCALE_CANDIDATES_FT_PER_IN",
    "SitePlanInput",
    "SitePlanRefusal",
    "choose_scale",
    "render_site_plan_pdf",
]

# -- sheet geometry (PDF points; 72 pt = 1 inch), US Letter landscape -----------
_POINTS_PER_INCH = 72.0
_SHEET_W = 792.0
_SHEET_H = 612.0
_MARGIN = 54.0
_TITLE_BLOCK_H = 108.0
_ANNOT_STRIP_W = 90.0

_DRAW_LEFT = _MARGIN
_DRAW_RIGHT = _SHEET_W - _MARGIN - _ANNOT_STRIP_W
_DRAW_BOTTOM = _MARGIN + _TITLE_BLOCK_H
_DRAW_TOP = _SHEET_H - _MARGIN
_DRAWABLE_W = _DRAW_RIGHT - _DRAW_LEFT
_DRAWABLE_H = _DRAW_TOP - _DRAW_BOTTOM

# Standard engineering plot scales (feet represented by one drawn inch), ascending
# so the first that fits yields the largest legible drawing.
SCALE_CANDIDATES_FT_PER_IN: tuple[float, ...] = (
    10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0,
    120.0, 160.0, 200.0, 240.0, 300.0, 400.0, 500.0,
)

# -- input bounds ---------------------------------------------------------------
_MAX_RING_VERTICES = 1024
# EPSG:2263 (NY Long Island ft) spans ~900k-1.07M easting, ~120k-280k northing;
# 1e8 is far outside any real NYC parcel yet bounds absurd inputs.
_MAX_COORD_ABS = 1.0e8
# Every caller text field is bounded so unbounded caller text cannot inflate the
# sheet once an export route feeds it (DB-059 a; a 200k-char address renders a
# ~201 kB PDF today). 120 chars comfortably holds a real address / bbl / provenance
# line on one title-block row (9 pt Helvetica, landscape US Letter) yet refuses abuse.
_MAX_TEXT_CHARS = 120

# -- drawing element counts (exported so round-trip tests assert exact totals) --
_SCALE_BAR_DIVISIONS = 4
_SCALE_BAR_SEGMENTS = 1 + (_SCALE_BAR_DIVISIONS + 1)  # baseline + tick per division edge
_NORTH_ARROW_SEGMENTS = 3  # shaft + two arrowhead strokes
_SCALE_BAR_LABELS = 2  # "0" and the far-end distance
_NORTH_ARROW_LABELS = 1  # the grid-north caption
_TITLE_BLOCK_LINES = 8
_SHEET_RECTS = 2  # sheet border + title-block border

# -- text / rendering constants -------------------------------------------------
_DIM_DECIMALS = 2  # dimension strings are printed to 2 decimal places (feet)
_DIM_FONT_PT = 7.0
_LABEL_FONT_PT = 8.0
_TITLE_FONT_PT = 9.0
_FONT_RESOURCE = "F1"


@dataclass(frozen=True)
class SitePlanInput:
    """Canonical inputs for one site-plan sheet; all geometry is EPSG:2263 feet.

    ``lot_ring`` and ``building_ring`` are open rings (the closing edge back to
    the first vertex is implied). ``generated_at`` and ``generator_version`` are
    provenance strings supplied by the caller (never a clock) so output stays
    deterministic.
    """

    lot_ring: tuple[tuple[float, float], ...]
    building_ring: tuple[tuple[float, float], ...] | None
    address: str
    bbl: str
    generated_at: str
    generator_version: str


@dataclass(frozen=True)
class SitePlanRefusal:
    """A typed, fail-closed refusal; ``reject_code`` names the class of problem."""

    reject_code: str
    detail: str

    def to_payload(self) -> dict[str, str]:
        return {"reject_code": self.reject_code, "detail": self.detail}


class _RenderRefused(Exception):
    """Internal carrier for a refusal found mid-render; never escapes the public API."""

    def __init__(self, refusal: SitePlanRefusal) -> None:
        super().__init__(refusal.reject_code)
        self.refusal = refusal


def choose_scale(width_ft: float, height_ft: float) -> float | None:
    """Return the feet-per-inch of the tightest standard scale that fits the sheet.

    Picks the smallest candidate (largest drawing) whose scaled extent fits the
    drawable region within the declared margins; ``None`` when even the coarsest
    candidate overflows the sheet.
    """
    for feet_per_inch in SCALE_CANDIDATES_FT_PER_IN:
        pt_per_ft = _POINTS_PER_INCH / feet_per_inch
        if width_ft * pt_per_ft <= _DRAWABLE_W and height_ft * pt_per_ft <= _DRAWABLE_H:
            return feet_per_inch
    return None


def render_site_plan_pdf(spec: SitePlanInput) -> bytes | SitePlanRefusal:
    """Render ``spec`` to deterministic PDF 1.4 bytes, or return a typed refusal."""
    if not isinstance(spec, SitePlanInput):
        return SitePlanRefusal("invalid_input", "spec must be a SitePlanInput")
    text_refusal = _screen_caller_text(spec)
    if text_refusal is not None:
        return text_refusal
    lot = _validate_ring(spec.lot_ring, "lot")
    if isinstance(lot, SitePlanRefusal):
        return lot
    building: tuple[tuple[float, float], ...] | None = None
    if spec.building_ring is not None:
        checked = _validate_ring(spec.building_ring, "building")
        if isinstance(checked, SitePlanRefusal):
            return checked
        building = checked

    rings = [lot] + ([building] if building is not None else [])
    min_x = min(x for ring in rings for x, _ in ring)
    min_y = min(y for ring in rings for _, y in ring)
    max_x = max(x for ring in rings for x, _ in ring)
    max_y = max(y for ring in rings for _, y in ring)
    width_ft = max_x - min_x
    height_ft = max_y - min_y
    if width_ft <= 0.0 or height_ft <= 0.0:
        return SitePlanRefusal(
            "invalid_ring", "the combined geometry has zero width or height extent"
        )

    feet_per_inch = choose_scale(width_ft, height_ft)
    if feet_per_inch is None:
        return SitePlanRefusal(
            "oversize_input",
            f"geometry extent {width_ft:.1f} x {height_ft:.1f} ft exceeds the sheet"
            f" at every standard scale (coarsest {SCALE_CANDIDATES_FT_PER_IN[-1]:.0f}"
            " ft/in)",
        )

    pt_per_ft = _POINTS_PER_INCH / feet_per_inch
    content_w = width_ft * pt_per_ft
    content_h = height_ft * pt_per_ft
    origin_x = _DRAW_LEFT + (_DRAWABLE_W - content_w) / 2.0
    origin_y = _DRAW_BOTTOM + (_DRAWABLE_H - content_h) / 2.0

    def to_device(x: float, y: float) -> tuple[float, float]:
        # EPSG:2263 +Y (grid north) maps to +device-Y (up on the page): no flip.
        return (origin_x + (x - min_x) * pt_per_ft, origin_y + (y - min_y) * pt_per_ft)

    return _finish(spec, lot, building, feet_per_inch, to_device)


def _finish(
    spec: SitePlanInput,
    lot: tuple[tuple[float, float], ...],
    building: tuple[tuple[float, float], ...] | None,
    feet_per_inch: float,
    to_device,
) -> bytes | SitePlanRefusal:
    """The one public boundary: build + assemble, converting a mid-render
    :class:`_RenderRefused` into a RETURNED :class:`SitePlanRefusal`.

    :func:`_num` RAISES the private :class:`_RenderRefused` carrier when a computed
    drawing number is non-finite; this is the SOLE place that carrier is caught and
    turned back into a returned refusal, so :func:`render_site_plan_pdf` never
    raises on caller data (the honest DB-053 b contract). No partial output: either
    a complete :func:`_assemble_pdf` byte string or a refusal is returned.
    """
    try:
        content = _build_content(spec, lot, building, feet_per_inch, to_device)
        return _assemble_pdf(content)
    except _RenderRefused as refused:
        return refused.refusal


# -- validation -----------------------------------------------------------------

# Sequences that are text/bytes, never a ring or an (x, y) pair.
_TEXT_LIKE = (str, bytes, bytearray, memoryview)


def _screen_caller_text(spec: SitePlanInput) -> SitePlanRefusal | None:
    """Refuse non-string, over-long, or claim-bearing caller text BEFORE drawing.

    Every caller-supplied string printed on the sheet is screened, in order, for:
    (1) type (must be ``str``); (2) length (at most :data:`_MAX_TEXT_CHARS`, so
    unbounded caller text cannot inflate the sheet - DB-059 a; bounding first also
    keeps the separator-collapsing screen off a huge string); (3) the shared
    claim-class words through the one separator-collapsing screen
    (:func:`app.cad.claim_words.contains_claim_word`), both as given and in the
    ASCII-sanitised form the sheet would print. Every refusal names the field and,
    for a claim word, the barred word - never the caller's text.
    """
    fields = (
        ("address", spec.address),
        ("bbl", spec.bbl),
        ("generated_at", spec.generated_at),
        ("generator_version", spec.generator_version),
    )
    for name, value in fields:
        if not isinstance(value, str):
            return SitePlanRefusal("invalid_text", f"{name} must be a string")
        if len(value) > _MAX_TEXT_CHARS:
            return SitePlanRefusal(
                "text_too_long",
                f"{name} exceeds the {_MAX_TEXT_CHARS}-character limit",
            )
        barred = contains_claim_word(value, _ascii_sanitise(value))
        if barred is not None:
            return SitePlanRefusal(
                "claim_class_word",
                f"{name} contains the barred claim-class word {barred!r}",
            )
    return None


def _is_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, _TEXT_LIKE)


def _validate_ring(
    ring: object, label: str
) -> tuple[tuple[float, float], ...] | SitePlanRefusal:
    """Coerce, bound, and de-close one ring; refuse anything non-drawable (never raises)."""
    if not _is_sequence(ring):
        return SitePlanRefusal(
            "invalid_ring", f"{label} ring is not a sequence of (x, y) pairs"
        )
    if len(ring) > _MAX_RING_VERTICES:
        return SitePlanRefusal(
            "oversize_input",
            f"{label} ring has {len(ring)} vertices, above the"
            f" {_MAX_RING_VERTICES} bound",
        )
    cleaned: list[tuple[float, float]] = []
    for vertex in ring:
        point = _coerce_vertex(vertex, label)
        if isinstance(point, SitePlanRefusal):
            return point
        cleaned.append(point)
    # Drop an explicit closing duplicate of the first vertex; the writer closes rings.
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1]:
        cleaned = cleaned[:-1]
    if len(cleaned) < 3:
        return SitePlanRefusal(
            "invalid_ring",
            f"{label} ring needs at least 3 distinct vertices, found {len(cleaned)}",
        )
    return tuple(cleaned)


def _coerce_vertex(vertex: object, label: str) -> tuple[float, float] | SitePlanRefusal:
    """One vertex -> a finite, bounded (x, y) float pair, or a typed refusal."""
    if not _is_sequence(vertex) or len(vertex) != 2:
        return SitePlanRefusal("invalid_ring", f"{label} ring vertex is not a pair")
    for value in vertex:
        if isinstance(value, bool) or not isinstance(value, numbers.Real):
            return SitePlanRefusal(
                "non_numeric_coordinate", f"{label} ring has a non-numeric coordinate"
            )
    try:
        x, y = float(vertex[0]), float(vertex[1])
    except OverflowError:  # an integer (or fraction) beyond the float range
        return SitePlanRefusal(
            "oversize_input", f"{label} ring coordinate exceeds +/-{_MAX_COORD_ABS:.0f} ft"
        )
    except (ValueError, TypeError):
        # DB-075 (a): a numbers.Real subclass whose __float__ raises ValueError/TypeError
        # passed the isinstance(numbers.Real) check above but cannot yield a float; broaden
        # the catch so the never-raise contract holds (not reachable from JSON, but the
        # public boundary must never raise on caller data).
        return SitePlanRefusal(
            "non_numeric_coordinate", f"{label} ring has a non-numeric coordinate"
        )
    if not (math.isfinite(x) and math.isfinite(y)):
        return SitePlanRefusal(
            "non_finite_coordinate", f"{label} ring has a non-finite coordinate"
        )
    if abs(x) > _MAX_COORD_ABS or abs(y) > _MAX_COORD_ABS:
        return SitePlanRefusal(
            "oversize_input",
            f"{label} ring coordinate exceeds +/-{_MAX_COORD_ABS:.0f} ft",
        )
    return (x, y)


# -- content-stream construction ------------------------------------------------


def _build_content(
    spec: SitePlanInput,
    lot: tuple[tuple[float, float], ...],
    building: tuple[tuple[float, float], ...] | None,
    feet_per_inch: float,
    to_device,
) -> bytes:
    """Assemble the page content stream (device space; PDF operator subset only)."""
    ops: list[str] = ["1 w", "0 0 0 RG"]
    _draw_rect(ops, _MARGIN, _MARGIN, _SHEET_W - 2 * _MARGIN, _SHEET_H - 2 * _MARGIN)
    _draw_rect(ops, _MARGIN, _MARGIN, _SHEET_W - 2 * _MARGIN, _TITLE_BLOCK_H)

    _draw_ring(ops, lot, to_device)
    _label_edges(ops, lot, to_device)
    if building is not None:
        _draw_ring(ops, building, to_device)
        _label_edges(ops, building, to_device)

    _draw_north_arrow(ops)
    _draw_scale_bar(ops, feet_per_inch)
    _draw_title_block(ops, spec, feet_per_inch)
    return ("\n".join(ops) + "\n").encode("latin-1")


def _draw_ring(ops: list[str], ring: tuple[tuple[float, float], ...], to_device) -> None:
    first = to_device(*ring[0])
    ops.append(f"{_num(first[0])} {_num(first[1])} m")
    for vertex in ring[1:]:
        px, py = to_device(*vertex)
        ops.append(f"{_num(px)} {_num(py)} l")
    ops.append("h S")


def _label_edges(
    ops: list[str], ring: tuple[tuple[float, float], ...], to_device
) -> None:
    n = len(ring)
    for i in range(n):
        ax, ay = ring[i]
        bx, by = ring[(i + 1) % n]
        length = math.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay))
        text = f"{round(length, _DIM_DECIMALS):.{_DIM_DECIMALS}f}"
        mid = to_device((ax + bx) / 2.0, (ay + by) / 2.0)
        _draw_text(ops, mid[0] + 2.0, mid[1] + 2.0, _DIM_FONT_PT, text)


def _draw_north_arrow(ops: list[str]) -> None:
    ax = _DRAW_RIGHT + _ANNOT_STRIP_W / 2.0
    base_y = _DRAW_TOP - 60.0
    tip_y = _DRAW_TOP - 18.0
    head = 6.0
    ops.append(f"{_num(ax)} {_num(base_y)} m {_num(ax)} {_num(tip_y)} l S")
    ops.append(f"{_num(ax)} {_num(tip_y)} m {_num(ax - head)} {_num(tip_y - head)} l S")
    ops.append(f"{_num(ax)} {_num(tip_y)} m {_num(ax + head)} {_num(tip_y - head)} l S")
    _draw_text(ops, ax - 34.0, base_y - 12.0, _LABEL_FONT_PT, "GRID N (EPSG:2263)")


def _draw_scale_bar(ops: list[str], feet_per_inch: float) -> None:
    x0 = _DRAW_RIGHT + 10.0
    y0 = _DRAW_TOP - 110.0
    length_pt = _POINTS_PER_INCH  # one inch of paper == feet_per_inch feet
    step = length_pt / _SCALE_BAR_DIVISIONS
    ops.append(f"{_num(x0)} {_num(y0)} m {_num(x0 + length_pt)} {_num(y0)} l S")
    for i in range(_SCALE_BAR_DIVISIONS + 1):
        tx = x0 + i * step
        ops.append(f"{_num(tx)} {_num(y0)} m {_num(tx)} {_num(y0 + 6.0)} l S")
    _draw_text(ops, x0 - 2.0, y0 - 10.0, _DIM_FONT_PT, "0")
    _draw_text(
        ops, x0 + length_pt - 8.0, y0 - 10.0, _DIM_FONT_PT, f"{feet_per_inch:.0f} ft"
    )


def _draw_title_block(
    ops: list[str], spec: SitePlanInput, feet_per_inch: float
) -> None:
    lines = [
        f"SITE: {spec.address}",
        f"BBL: {spec.bbl}",
        f"Generated: {spec.generated_at}",
        f"Generator: {spec.generator_version}",
        "Units: US survey feet   CRS: EPSG:2263",
        f"Scale: 1 in = {feet_per_inch:.0f} ft   Orientation: EPSG:2263 grid north",
        "PROPOSED - NOT A CITY RECORD",
        "Not for construction - professional review required",
    ]
    x = _MARGIN + 8.0
    y = _MARGIN + _TITLE_BLOCK_H - 16.0
    for line in lines:
        _draw_text(ops, x, y, _TITLE_FONT_PT, line)
        y -= 12.0


def _draw_rect(ops: list[str], x: float, y: float, w: float, h: float) -> None:
    ops.append(f"{_num(x)} {_num(y)} {_num(w)} {_num(h)} re S")


def _draw_text(ops: list[str], x: float, y: float, size: float, text: str) -> None:
    ops.append(
        f"BT /{_FONT_RESOURCE} {_num(size)} Tf {_num(x)} {_num(y)} Td"
        f" ({_escape_pdf_text(text)}) Tj ET"
    )


def _escape_pdf_text(text: str) -> str:
    """The one escaper: ASCII-sanitise, then escape ``(`` ``)`` ``\\`` for a literal string.

    Any byte outside printable ASCII (0x20-0x7E) becomes ``?`` so the emitted
    string never carries bytes the strict reader would mishandle; the three
    literal-string metacharacters are backslash-escaped so parentheses in an
    address cannot unbalance the stream. Per ISO 32000-1 §7.3.4.2 a literal string
    only REQUIRES escaping unbalanced ``(`` / ``)`` and every ``\\`` [recalled -
    verify against the standard's exact wording]; escaping ALL three unconditionally
    is the conservative superset and always leaves every literal string balanced and
    well-formed. This is the SOLE path text takes into the content stream.
    """
    out: list[str] = []
    for safe in _ascii_sanitise(text):
        if safe in ("(", ")", "\\"):
            out.append("\\" + safe)
        else:
            out.append(safe)
    return "".join(out)


def _ascii_sanitise(text: str) -> str:
    """Map every character outside printable ASCII (0x20-0x7E) to ``?``."""
    return "".join(ch if 0x20 <= ord(ch) <= 0x7E else "?" for ch in text)


def _num(value: float) -> str:
    """Format a coordinate/size deterministically: round to 3 dp, trim, no ``-0``.

    A non-finite value RAISES the private :class:`_RenderRefused` carrier (this
    function is NOT total on non-finite input, by design) so a ``nan``/``inf``
    token can never reach the content stream. The carrier never escapes the public
    API: the single boundary :func:`_finish` catches it and returns a typed
    :class:`SitePlanRefusal` instead (DB-053 b honest contract).
    """
    if not math.isfinite(value):
        raise _RenderRefused(
            SitePlanRefusal("non_finite_value", "a computed drawing number is not finite")
        )
    rounded = round(value, 3)
    if rounded == 0.0:
        rounded = 0.0  # collapse -0.0
    text = f"{rounded:.3f}".rstrip("0").rstrip(".")
    return text or "0"


# -- PDF object / xref assembly (ISO 32000-1 §7.5) ------------------------------


def _assemble_pdf(content: bytes) -> bytes:
    """Wrap the content stream in a 5-object PDF 1.4 file with an exact xref table."""
    bodies = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "
            + f"{_num(_SHEET_W)} {_num(_SHEET_H)}".encode("latin-1")
            + b"] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        (
            b"<< /Length "
            + str(len(content)).encode("latin-1")
            + b" >>\nstream\n"
            + content
            + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, body in enumerate(bodies, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode("latin-1")
        out += body
        out += b"\nendobj\n"

    xref_offset = len(out)
    count = len(bodies) + 1  # object 0 plus the in-use objects
    out += b"xref\n"
    out += f"0 {count}\n".encode("latin-1")
    out += b"0000000000 65535 f\r\n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n\r\n".encode("latin-1")
    out += b"trailer\n"
    out += f"<< /Size {count} /Root 1 0 R >>\n".encode("latin-1")
    out += b"startxref\n"
    out += f"{xref_offset}\n".encode("latin-1")
    out += b"%%EOF"
    return bytes(out)
