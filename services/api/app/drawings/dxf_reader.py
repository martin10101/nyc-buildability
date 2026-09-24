"""Strict-subset ASCII DXF reader (D-087 CAD-3; phase C; not wired to any route).

DXF (Drawing Interchange Format) is Autodesk's open, documented, licence-free interchange
for AutoCAD drawings. This module turns the *ASCII* DXF group-code stream into typed,
layer-tagged geometry primitives so architect drawings can be read back into the product
without a native-DWG licence (the DWG path stays an owner decision, D-087-R007). It is a
deliberate STRICT SUBSET and a dependency-free reader (stdlib only, no network): it parses
exactly LINE, LWPOLYLINE, POLYLINE/VERTEX/SEQEND, 3DFACE and TEXT on their named layers,
plus the header's declared drawing units and AutoCAD version. Everything else is either
disclosed (counted) or refused, per the written rule below. Nothing here is wired to a
route, worker, or ``app/main.py``; a later gated packet places it behind the
parser-isolation boundary.

Format authority: every group code and header variable below is cited to the Autodesk DXF
Reference (the "Group Codes" / entity and HEADER-section chapters). Each citation is marked
``[recalled - verify]`` for the G1 data-contract reviewer to confirm against the official
reference / the sibling M5-T084 research notes; nothing about the format is guessed.

Written subset / disclose-or-refuse rule (all-or-nothing per file)
------------------------------------------------------------------
* PARSED into typed primitives (the subset): ``LINE``, ``LWPOLYLINE``,
  ``POLYLINE``/``VERTEX``/``SEQEND``, ``3DFACE``, ``TEXT`` inside the ENTITIES section, each
  tagged with its layer (group 8; DXF default layer ``"0"`` when absent) and exact
  coordinates.
* DISCLOSED, not refused (the read still succeeds): any other ENTITIES-section entity type
  (``INSERT``, ``CIRCLE``, ``ARC``, ``SPLINE``, ``HATCH``, proxy objects, ...) is NOT
  parsed; its type name is counted in :attr:`DxfDocument.disclosed_unknown` so the caller
  sees exactly what was dropped and how much. Whole sections other than HEADER and ENTITIES
  (TABLES, BLOCKS, CLASSES, OBJECTS, THUMBNAILIMAGE, ...) are skipped and recorded in
  :attr:`DxfDocument.skipped_sections`; a block *definition* is therefore skipped while an
  ``INSERT`` reference in ENTITIES is disclosed-as-unknown.
* REFUSED as a typed VALUE (never an exception; all-or-nothing) - the whole file yields a
  :class:`DxfRefusal`, not a partial parse: binary DXF (sentinel), non-ASCII bytes,
  over-limit size / line length / line count / entity count / polyline vertex count, an odd
  group-code/value line count (pair-parity), a non-integer group code, a non-numeric or
  non-finite coordinate, a stray ``VERTEX``/``SEQEND``, an unterminated ``POLYLINE``, a
  ``SECTION`` without its name, a header value that will not parse, or a file with no DXF
  section markers at all.
* CURVES: a non-zero *bulge* (group 42) on an LWPOLYLINE/POLYLINE vertex is REFUSED. Bulge
  encodes a circular arc; flattening it needs a declared arc-tessellation tolerance this
  phase-C reader will not assume, so it fails closed rather than silently straighten a
  curved boundary.

Units honesty (phase C): the drawing units are REPORTED from the header ``$INSUNITS``
variable with the Autodesk unit code; a file that carries no ``$INSUNITS`` is reported
``unitless`` with ``source="absent"`` - feet are NEVER assumed. An explicit ``$INSUNITS=0``
is also ``unitless`` but with ``source="header:$INSUNITS"``, so the caller can tell
"declared unitless" from "no units declared".

Line splitting / input: the stream is split on the three real DXF terminators ONLY (CR, LF,
CRLF); ``str.splitlines`` also breaks on ``\\x0b \\x0c \\x1c-\\x1e`` and would shift pairing,
so such a control char is NEVER used to break a line and cannot shift the (code, value)
pairing (one in a coordinate still fails closed at :func:`_to_float`). It survives inside the
value where it is flanked by non-whitespace; the pre-existing per-value ``.strip()`` still
trims it when it is leading/trailing, so a value made up SOLELY of such characters strips to
``''`` (that strip behaviour is unchanged). ``bytes`` is preferred; a ``str`` gets the SAME
binary-sentinel and non-ASCII checks (no lenient bypass); any other type is a typed refusal,
not a ``TypeError``.

Failure model: no exception ever escapes :func:`read_dxf`. Structural problems raise a
private marker that the public boundary converts to a :class:`DxfRefusal`; a final
defensive guard turns any unexpected error into a refusal value as well. All bounds are
named, reviewed constants (:class:`DxfLimits`), injectable for tests, never tuned silently,
and hard-ceilinged (:data:`_LIMIT_CEILINGS`) so a permissive caller cannot disable a
protection (a bound above its ceiling is clamped down; below 1 is a caller bug that raises).
``max_lines`` / ``max_line_chars`` are enforced WHILE scanning, before the full line list exists.
"""

from __future__ import annotations

import enum
import math
import re
from collections.abc import Iterator
from dataclasses import dataclass, field

__all__ = [
    "DEFAULT_LIMITS",
    "DxfDocument",
    "DxfLimits",
    "DxfReadResult",
    "DxfRefusal",
    "DxfRefusalReason",
    "DxfUnits",
    "FacePrimitive",
    "LinePrimitive",
    "PolylinePrimitive",
    "TextPrimitive",
    "read_dxf",
]

# --------------------------------------------------------------------------- group codes
# Autodesk DXF Reference, "Group Code Value Types" and the entity/HEADER chapters.
# [recalled - verify]: the G1 data-contract reviewer confirms each constant against the
# official reference (and the M5-T084 research notes). Nothing here is guessed.
GC_ENTITY_TYPE = 0  # entity type / structural marker (SECTION, ENDSEC, EOF, LINE, ...)
GC_TEXT_VALUE = 1  # primary text string (TEXT); string value of a HEADER variable
GC_NAME = 2  # section / table / block name
GC_HEADER_VAR = 9  # HEADER variable name (e.g. $INSUNITS, $ACADVER)
GC_LAYER = 8  # layer name
GC_X1, GC_Y1, GC_Z1 = 10, 20, 30  # primary point (LINE start, vertex, TEXT insertion)
GC_X2, GC_Y2, GC_Z2 = 11, 21, 31  # second point (LINE end, 3DFACE corner 2)
GC_X3, GC_Y3, GC_Z3 = 12, 22, 32  # third point (3DFACE corner 3)
GC_X4, GC_Y4, GC_Z4 = 13, 23, 33  # fourth point (3DFACE corner 4)
GC_TEXT_HEIGHT = 40  # text height (TEXT)
GC_BULGE = 42  # LWPOLYLINE / VERTEX bulge (non-zero = circular arc segment)
GC_FLAGS = 70  # entity flags; bit 1 = closed for LWPOLYLINE and POLYLINE

# HEADER variable names ([recalled - verify], Autodesk DXF Reference HEADER section).
HDR_INSUNITS = "$INSUNITS"  # drawing units code (its value carried on a group-70 pair)
HDR_ACADVER = "$ACADVER"  # AutoCAD version string (value carried on a group-1 pair)

# Entity flag bit: closed polyline (LWPOLYLINE 70 & 1, POLYLINE 70 & 1) [recalled - verify].
_CLOSED_FLAG_BIT = 1

# Recognized DXF sections; only these two carry data this reader consumes.
_SECTION_HEADER = "HEADER"
_SECTION_ENTITIES = "ENTITIES"

# Binary DXF files begin with this 18-byte label ("AutoCAD Binary DXF" followed by
# \r\n\x1a\x00) [recalled - verify]. Detected on the raw bytes, before ASCII decode, so the
# refusal is specific (BINARY_DXF) rather than a generic non-ASCII decode failure.
_BINARY_SENTINEL = b"AutoCAD Binary DXF"
# ASCII text form of the same sentinel, for the ``str`` input path (which never went through
# the raw-bytes check). Derived from the bytes constant so the two can never drift apart.
_BINARY_SENTINEL_STR = _BINARY_SENTINEL.decode("ascii")

# Autodesk $INSUNITS unit codes -> reported name [recalled - verify]. A code outside this
# map is reported verbatim as ``unknown_insunits_<code>`` - never coerced to a known unit.
# Codes 0-21 were confirmed against the live official reference in M5-T081-G1.md
# (INSUNITS values 0-24, cloudhelp/2025 GUID-A58A87BB-482B-4042-A00A-EEF55A2B4FD8).
# Codes 22/23/24 (US Survey Inch/Yard/Mile) are ADDED here from that same reference range,
# marked ``[recalled - verify]`` because this producer could not re-open the live page; the
# G1 report already verified the 0-24 range exists. Reported names follow the existing
# lowercase-plural convention (21 = ``us_survey_feet``), so 22/23/24 mirror it.
_INSUNITS_NAMES: dict[int, str] = {
    0: "unitless",
    1: "inches",
    2: "feet",
    3: "miles",
    4: "millimeters",
    5: "centimeters",
    6: "meters",
    7: "kilometers",
    8: "microinches",
    9: "mils",
    10: "yards",
    11: "angstroms",
    12: "nanometers",
    13: "microns",
    14: "decimeters",
    15: "dekameters",
    16: "hectometers",
    17: "gigameters",
    18: "astronomical_units",
    19: "light_years",
    20: "parsecs",
    21: "us_survey_feet",
    22: "us_survey_inches",  # [recalled - verify] Autodesk INSUNITS 22 = US Survey Inch
    23: "us_survey_yards",  # [recalled - verify] Autodesk INSUNITS 23 = US Survey Yard
    24: "us_survey_miles",  # [recalled - verify] Autodesk INSUNITS 24 = US Survey Mile
}


class DxfRefusalReason(enum.Enum):
    """Closed vocabulary of typed refusal reasons (each a VALUE, never an exception)."""

    BINARY_DXF = "binary_dxf"
    NON_ASCII = "non_ascii"
    FILE_TOO_LARGE = "file_too_large"
    TOO_MANY_LINES = "too_many_lines"
    LINE_TOO_LONG = "line_too_long"
    ODD_PAIR_COUNT = "odd_pair_count"
    BAD_GROUP_CODE = "bad_group_code"
    BAD_COORDINATE = "bad_coordinate"
    TOO_MANY_ENTITIES = "too_many_entities"
    TOO_MANY_VERTICES = "too_many_vertices"
    UNSUPPORTED_BULGE = "unsupported_bulge"
    MALFORMED_STRUCTURE = "malformed_structure"


# Hard fail-safe ceilings on every bound (G5-A1: DxfLimits is a public keyword param, so a
# caller could otherwise pass a permissive instance and effectively DISABLE the size/line/
# entity/vertex protections). A field ABOVE its ceiling is CLAMPED DOWN to the ceiling in
# __post_init__ (a fail-safe reduction of capability, never a raise), so the protections can
# never be turned off no matter what a caller passes. Ceilings sit well above the reviewed
# production DEFAULT_LIMITS, so any legitimate limit passes through unchanged; only an attempt
# to disable a bound is clamped. A field BELOW 1 is a caller bug and still raises (unchanged).
# These are reviewed safety constants, pinned by test like DEFAULT_LIMITS; change by review only.
_LIMIT_CEILINGS: dict[str, int] = {
    "max_bytes": 64 * 1024 * 1024, "max_lines": 8_000_000, "max_line_chars": 65_536,
    "max_entities": 2_000_000, "max_vertices": 1_000_000,
}


@dataclass(frozen=True)
class DxfLimits:
    """Named, reviewed initial bounds on untrusted DXF input; injectable for tests.

    Production callers use :data:`DEFAULT_LIMITS`. Tests construct small instances to prove
    each bound at its exact edge without allocating huge fixtures; doing so never changes
    the reviewed production defaults, which the suite asserts verbatim. Bounds change only
    through review, never silently and never set by AI. A field below 1 is a caller bug and
    raises; a field above its hard ceiling in :data:`_LIMIT_CEILINGS` is clamped down
    (fail-safe, never a raise) so a permissive caller can never disable a protection.
    """

    max_bytes: int = 8 * 1024 * 1024
    max_lines: int = 2_000_000
    max_line_chars: int = 4096
    max_entities: int = 200_000
    max_vertices: int = 100_000

    def __post_init__(self) -> None:
        for name, ceiling in _LIMIT_CEILINGS.items():
            value = getattr(self, name)
            if value < 1:
                raise ValueError(f"{name} must be >= 1")
            if value > ceiling:
                # frozen dataclass -> clamp via object.__setattr__ (fail-safe reduction).
                object.__setattr__(self, name, ceiling)


DEFAULT_LIMITS = DxfLimits()


@dataclass(frozen=True)
class DxfUnits:
    """Reported drawing units - never assumed. ``code`` is the Autodesk $INSUNITS code (or
    ``None`` when no units header exists); ``source`` is ``"header:$INSUNITS"`` or
    ``"absent"``."""

    code: int | None
    name: str
    source: str


@dataclass(frozen=True)
class LinePrimitive:
    """A DXF ``LINE``: two 3D endpoints on a named layer."""

    entity_type: str
    layer: str
    start: tuple[float, float, float]
    end: tuple[float, float, float]


@dataclass(frozen=True)
class PolylinePrimitive:
    """A closed-or-open polyline (``LWPOLYLINE`` or old-style ``POLYLINE``/``VERTEX``).

    ``vertices`` are (x, y) pairs in file order. ``entity_type`` records which DXF form the
    geometry came from so provenance is not flattened away.
    """

    entity_type: str
    layer: str
    closed: bool
    vertices: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class FacePrimitive:
    """A DXF ``3DFACE``: three or four 3D corners on a named layer."""

    entity_type: str
    layer: str
    corners: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class TextPrimitive:
    """A DXF ``TEXT`` label: insertion point, string, and optional height."""

    entity_type: str
    layer: str
    position: tuple[float, float, float]
    text: str
    height: float | None


@dataclass(frozen=True)
class DxfDocument:
    """Successful strict-subset read result (``ok = True``).

    ``primitives`` are the parsed subset entities in file order; ``disclosed_unknown`` is a
    sorted tuple of ``(entity_type, count)`` for ENTITIES types outside the subset;
    ``skipped_sections`` is a sorted tuple of whole sections skipped; ``entity_count`` is the
    total ENTITIES-section entities seen (parsed + disclosed).
    """

    ok: bool
    units: DxfUnits
    acad_version: str | None
    primitives: tuple[
        LinePrimitive | PolylinePrimitive | FacePrimitive | TextPrimitive, ...
    ]
    disclosed_unknown: tuple[tuple[str, int], ...]
    skipped_sections: tuple[str, ...]
    entity_count: int


@dataclass(frozen=True)
class DxfRefusal:
    """Typed all-or-nothing refusal (``ok = False``): a VALUE the caller inspects, never a
    raised exception. ``reason`` is a :class:`DxfRefusalReason`; ``detail`` is a short human
    string with the offending context."""

    ok: bool
    reason: DxfRefusalReason
    detail: str


DxfReadResult = DxfDocument | DxfRefusal


# ------------------------------------------------------------------- internal parse layer


@dataclass
class _Refuse(Exception):
    """Private control-flow marker - raised inside the parser, converted to a
    :class:`DxfRefusal` value at the public boundary so no exception ever escapes."""

    reason: DxfRefusalReason
    detail: str


def _to_float(value: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise _Refuse(
            DxfRefusalReason.BAD_COORDINATE, f"non-numeric coordinate {value!r}"
        ) from None
    if not math.isfinite(parsed):
        raise _Refuse(
            DxfRefusalReason.BAD_COORDINATE, f"non-finite coordinate {value!r}"
        ) from None
    return parsed


def _first(body: list[tuple[int, str]], code: int) -> str | None:
    """First value in ``body`` carrying group ``code`` (or ``None``)."""
    for pair_code, pair_value in body:
        if pair_code == code:
            return pair_value
    return None


def _require_point(
    body: list[tuple[int, str]], cx: int, cy: int, cz: int
) -> tuple[float, float, float]:
    xs = _first(body, cx)
    ys = _first(body, cy)
    if xs is None or ys is None:
        raise _Refuse(
            DxfRefusalReason.MALFORMED_STRUCTURE, f"missing coordinate group codes {cx}/{cy}"
        )
    zs = _first(body, cz)
    return (_to_float(xs), _to_float(ys), _to_float(zs) if zs is not None else 0.0)


def _closed_from_flags(body: list[tuple[int, str]]) -> bool:
    flags = _first(body, GC_FLAGS)
    if flags is None:
        return False
    try:
        return bool(int(flags) & _CLOSED_FLAG_BIT)
    except ValueError:
        raise _Refuse(
            DxfRefusalReason.MALFORMED_STRUCTURE, f"non-integer flags {flags!r}"
        ) from None


def _parse_line(body: list[tuple[int, str]], layer: str) -> LinePrimitive:
    return LinePrimitive(
        entity_type="LINE",
        layer=layer,
        start=_require_point(body, GC_X1, GC_Y1, GC_Z1),
        end=_require_point(body, GC_X2, GC_Y2, GC_Z2),
    )


def _parse_lwpolyline(
    body: list[tuple[int, str]], layer: str, limits: DxfLimits
) -> PolylinePrimitive:
    closed = _closed_from_flags(body)
    vertices: list[tuple[float, float]] = []
    pending_x: float | None = None
    for code, value in body:
        if code == GC_X1:
            pending_x = _to_float(value)
        elif code == GC_Y1:
            if pending_x is None:
                raise _Refuse(
                    DxfRefusalReason.MALFORMED_STRUCTURE, "LWPOLYLINE Y (20) without X (10)"
                )
            vertices.append((pending_x, _to_float(value)))
            pending_x = None
            if len(vertices) > limits.max_vertices:
                raise _Refuse(
                    DxfRefusalReason.TOO_MANY_VERTICES,
                    f"LWPOLYLINE over {limits.max_vertices} vertices",
                )
        elif code == GC_BULGE and _to_float(value) != 0.0:
            raise _Refuse(DxfRefusalReason.UNSUPPORTED_BULGE, "non-zero bulge (curved segment)")
    if pending_x is not None:
        raise _Refuse(
            DxfRefusalReason.MALFORMED_STRUCTURE, "LWPOLYLINE dangling X (10) without Y (20)"
        )
    return PolylinePrimitive("LWPOLYLINE", layer, closed, tuple(vertices))


def _parse_face(body: list[tuple[int, str]], layer: str) -> FacePrimitive:
    corner_codes = (
        (GC_X1, GC_Y1, GC_Z1),
        (GC_X2, GC_Y2, GC_Z2),
        (GC_X3, GC_Y3, GC_Z3),
        (GC_X4, GC_Y4, GC_Z4),
    )
    corners: list[tuple[float, float, float]] = []
    for cx, cy, cz in corner_codes:
        xs = _first(body, cx)
        ys = _first(body, cy)
        zs = _first(body, cz)
        if xs is None and ys is None and zs is None:
            continue
        if xs is None or ys is None:
            raise _Refuse(
                DxfRefusalReason.MALFORMED_STRUCTURE, f"3DFACE corner missing X/Y ({cx}/{cy})"
            )
        corners.append((_to_float(xs), _to_float(ys), _to_float(zs) if zs is not None else 0.0))
    if len(corners) < 3:
        raise _Refuse(DxfRefusalReason.MALFORMED_STRUCTURE, "3DFACE has fewer than 3 corners")
    return FacePrimitive("3DFACE", layer, tuple(corners))


def _parse_text(body: list[tuple[int, str]], layer: str) -> TextPrimitive:
    position = _require_point(body, GC_X1, GC_Y1, GC_Z1)
    text = _first(body, GC_TEXT_VALUE)
    if text is None:
        raise _Refuse(DxfRefusalReason.MALFORMED_STRUCTURE, "TEXT missing string value (group 1)")
    height_raw = _first(body, GC_TEXT_HEIGHT)
    height = _to_float(height_raw) if height_raw is not None else None
    return TextPrimitive("TEXT", layer, position, text, height)


def _parse_polyline(
    pairs: list[tuple[int, str]],
    header_body: list[tuple[int, str]],
    start: int,
    n: int,
    limits: DxfLimits,
) -> tuple[PolylinePrimitive, int]:
    """Old-style POLYLINE: header entity followed by 0/VERTEX* then 0/SEQEND.

    ``header_body`` is the POLYLINE's own attribute pairs; ``start`` indexes the first pair
    after them. Returns the primitive and the index just past SEQEND.
    """
    layer = _first(header_body, GC_LAYER) or "0"
    closed = _closed_from_flags(header_body)
    vertices: list[tuple[float, float]] = []
    k = start
    while k < n:
        code, value = pairs[k]
        if code != GC_ENTITY_TYPE:
            raise _Refuse(
                DxfRefusalReason.MALFORMED_STRUCTURE, f"expected VERTEX/SEQEND, got group {code}"
            )
        if value == "VERTEX":
            m = k + 1
            vertex_body: list[tuple[int, str]] = []
            while m < n and pairs[m][0] != GC_ENTITY_TYPE:
                vertex_body.append(pairs[m])
                m += 1
            xs = _first(vertex_body, GC_X1)
            ys = _first(vertex_body, GC_Y1)
            if xs is None or ys is None:
                raise _Refuse(DxfRefusalReason.MALFORMED_STRUCTURE, "VERTEX missing X/Y (10/20)")
            bulge = _first(vertex_body, GC_BULGE)
            if bulge is not None and _to_float(bulge) != 0.0:
                raise _Refuse(DxfRefusalReason.UNSUPPORTED_BULGE, "non-zero bulge (curved segment)")
            vertices.append((_to_float(xs), _to_float(ys)))
            if len(vertices) > limits.max_vertices:
                raise _Refuse(
                    DxfRefusalReason.TOO_MANY_VERTICES,
                    f"POLYLINE over {limits.max_vertices} vertices",
                )
            k = m
        elif value == "SEQEND":
            m = k + 1
            while m < n and pairs[m][0] != GC_ENTITY_TYPE:
                m += 1  # skip SEQEND's own body pairs (e.g. layer)
            return PolylinePrimitive("POLYLINE", layer, closed, tuple(vertices)), m
        else:
            raise _Refuse(
                DxfRefusalReason.MALFORMED_STRUCTURE, f"expected VERTEX/SEQEND, got {value!r}"
            )
    raise _Refuse(DxfRefusalReason.MALFORMED_STRUCTURE, "unterminated POLYLINE (no SEQEND)")


def _decode(data: bytes | str, limits: DxfLimits) -> str:
    if isinstance(data, bytes):
        if data[: len(_BINARY_SENTINEL)] == _BINARY_SENTINEL:
            raise _Refuse(DxfRefusalReason.BINARY_DXF, "binary DXF sentinel present")
        if len(data) > limits.max_bytes:
            raise _Refuse(DxfRefusalReason.FILE_TOO_LARGE, f"over {limits.max_bytes} bytes")
        try:
            return data.decode("ascii")
        except UnicodeDecodeError:
            raise _Refuse(
                DxfRefusalReason.NON_ASCII, "non-ASCII byte; this reader is ASCII-DXF only"
            ) from None
    if isinstance(data, str):
        # STR path (test convenience and any str caller). It re-applies the SAME
        # binary-sentinel and ASCII checks as the bytes path (closing G5-A3, where the
        # str branch skipped both); a str is otherwise treated as already-decoded ASCII.
        if data[: len(_BINARY_SENTINEL_STR)] == _BINARY_SENTINEL_STR:
            raise _Refuse(DxfRefusalReason.BINARY_DXF, "binary DXF sentinel present")
        if len(data) > limits.max_bytes:
            raise _Refuse(DxfRefusalReason.FILE_TOO_LARGE, f"over {limits.max_bytes} chars")
        if not data.isascii():
            raise _Refuse(
                DxfRefusalReason.NON_ASCII, "non-ASCII char; this reader is ASCII-DXF only"
            )
        return data
    # Neither bytes nor str -> a typed refusal VALUE, never a raised TypeError.
    raise _Refuse(
        DxfRefusalReason.MALFORMED_STRUCTURE,
        f"unsupported input type {type(data).__name__}; expected bytes or str",
    )


# The three real DXF line terminators, and ONLY those: CRLF first so a CR immediately
# followed by an LF is one break, not two (CR then an empty line). ``str.splitlines()`` also
# breaks on ``\x0b \x0c \x1c \x1d \x1e`` (all ASCII); a value literally containing one of
# those would be cut in two and SHIFT the (code, value) pairing (G3-F1 / G5-A2), so those
# characters are deliberately absent from this pattern.
_LINE_TERMINATOR = re.compile(r"\r\n|\r|\n")


def _iter_dxf_lines(text: str, limits: DxfLimits) -> Iterator[str]:
    """Yield DXF lines splitting on CR, LF or CRLF ONLY, one line at a time.

    A control character ``str.splitlines()`` would split on (``\\x0b \\x0c \\x1c \\x1d \\x1e``)
    is NOT a terminator here, so it never breaks a line and never shifts the (code, value)
    pairing. It survives inside the value where it is flanked by non-whitespace; the per-value
    ``.strip()`` in :func:`_to_pairs` still trims it if it is leading/trailing, so a value made
    up SOLELY of such characters strips to ``''`` (that strip behaviour is unchanged, G3-A1). A
    control char that lands in a coordinate is still caught downstream by :func:`_to_float`
    (BAD_COORDINATE).

    It is a GENERATOR: ``max_lines`` and ``max_line_chars`` are enforced WHILE scanning, as
    each line is produced, so an over-``max_lines`` file refuses without the full line list
    ever being materialised (G5-A4).

    Complexity is O(n): a SINGLE precompiled ``_LINE_TERMINATOR.search(text, pos)`` finds the
    next terminator of ANY of the three kinds in one C-level pass and never rescans for an
    absent terminator. (The prior implementation called both ``find("\\n")`` AND ``find("\\r")``
    every line; when a file used only one terminator the other ``find`` rescanned to EOF each
    line, making pure-LF - our own writer's output - and pure-CR input O(n^2): G3-B1 / G5-F1.)
    A trailing terminator does NOT yield an extra empty final line (matching ``splitlines``);
    a blank line between two terminators does.
    """
    n = len(text)
    pos = 0
    count = 0
    search = _LINE_TERMINATOR.search
    while pos < n:
        match = search(text, pos)
        if match is None:  # last line: no trailing terminator
            end = nxt = n
        else:
            end = match.start()
            nxt = match.end()  # already absorbs a full CRLF as one break
        line = text[pos:end]
        count += 1
        if count > limits.max_lines:
            raise _Refuse(DxfRefusalReason.TOO_MANY_LINES, f"over {limits.max_lines} lines")
        if len(line) > limits.max_line_chars:
            raise _Refuse(
                DxfRefusalReason.LINE_TOO_LONG, f"line over {limits.max_line_chars} chars"
            )
        yield line
        pos = nxt


def _to_pairs(text: str, limits: DxfLimits) -> list[tuple[int, str]]:
    pairs: list[tuple[int, str]] = []
    code_line: str | None = None
    total = 0
    for line in _iter_dxf_lines(text, limits):
        total += 1
        if code_line is None:
            code_line = line
            continue
        code_text = code_line.strip()
        try:
            code = int(code_text)
        except ValueError:
            raise _Refuse(
                DxfRefusalReason.BAD_GROUP_CODE, f"non-integer group code {code_text!r}"
            ) from None
        pairs.append((code, line.strip()))
        code_line = None
    # PAIR-PARITY: every group code line must be followed by a value line -> even line count.
    # A leftover unpaired code line means an odd total line count.
    if code_line is not None:
        raise _Refuse(
            DxfRefusalReason.ODD_PAIR_COUNT, f"odd group-code/value line count {total}"
        )
    return pairs


@dataclass
class _WalkState:
    """Mutable accumulator threaded through the pair walk."""

    insunits_code: int | None = None
    acad_version: str | None = None
    pending_var: str | None = None
    saw_section: bool = False
    entity_count: int = 0
    primitives: list[LinePrimitive | PolylinePrimitive | FacePrimitive | TextPrimitive] = field(
        default_factory=list
    )
    unknown: dict[str, int] = field(default_factory=dict)
    skipped: set[str] = field(default_factory=set)


def _handle_header(pairs: list[tuple[int, str]], i: int, state: _WalkState) -> None:
    code, value = pairs[i]
    if code == GC_HEADER_VAR:
        state.pending_var = value
    elif state.pending_var == HDR_INSUNITS and code == GC_FLAGS:
        try:
            state.insunits_code = int(value)
        except ValueError:
            raise _Refuse(
                DxfRefusalReason.MALFORMED_STRUCTURE, f"non-integer $INSUNITS {value!r}"
            ) from None
    elif state.pending_var == HDR_ACADVER and code == GC_TEXT_VALUE:
        state.acad_version = value


def _handle_entity(
    pairs: list[tuple[int, str]], i: int, n: int, state: _WalkState, limits: DxfLimits
) -> int:
    code, etype = pairs[i]
    if code != GC_ENTITY_TYPE:
        raise _Refuse(
            DxfRefusalReason.MALFORMED_STRUCTURE, f"stray group {code} outside an entity"
        )
    j = i + 1
    body: list[tuple[int, str]] = []
    while j < n and pairs[j][0] != GC_ENTITY_TYPE:
        body.append(pairs[j])
        j += 1
    layer = _first(body, GC_LAYER) or "0"
    if etype == "LINE":
        state.primitives.append(_parse_line(body, layer))
    elif etype == "LWPOLYLINE":
        state.primitives.append(_parse_lwpolyline(body, layer, limits))
    elif etype == "3DFACE":
        state.primitives.append(_parse_face(body, layer))
    elif etype == "TEXT":
        state.primitives.append(_parse_text(body, layer))
    elif etype == "POLYLINE":
        primitive, j = _parse_polyline(pairs, body, j, n, limits)
        state.primitives.append(primitive)
    elif etype in ("VERTEX", "SEQEND"):
        raise _Refuse(DxfRefusalReason.MALFORMED_STRUCTURE, f"{etype} outside a POLYLINE")
    else:
        state.unknown[etype] = state.unknown.get(etype, 0) + 1
    state.entity_count += 1
    # ENTITY-COUNT BOUND: total ENTITIES-section entities (parsed + disclosed).
    if state.entity_count > limits.max_entities:
        raise _Refuse(
            DxfRefusalReason.TOO_MANY_ENTITIES, f"over {limits.max_entities} entities"
        )
    return j


def _walk(pairs: list[tuple[int, str]], limits: DxfLimits) -> DxfDocument:
    state = _WalkState()
    section: str | None = None
    i = 0
    n = len(pairs)
    while i < n:
        code, value = pairs[i]
        if code == GC_ENTITY_TYPE and value == "SECTION":
            if i + 1 >= n or pairs[i + 1][0] != GC_NAME:
                raise _Refuse(
                    DxfRefusalReason.MALFORMED_STRUCTURE, "SECTION without a name (group 2)"
                )
            section = pairs[i + 1][1]
            state.saw_section = True
            state.pending_var = None
            if section not in (_SECTION_HEADER, _SECTION_ENTITIES):
                state.skipped.add(section)
            i += 2
            continue
        if code == GC_ENTITY_TYPE and value == "ENDSEC":
            section = None
            i += 1
            continue
        if code == GC_ENTITY_TYPE and value == "EOF":
            break
        if section == _SECTION_HEADER:
            _handle_header(pairs, i, state)
            i += 1
        elif section == _SECTION_ENTITIES:
            i = _handle_entity(pairs, i, n, state, limits)
        else:
            i += 1
    if not state.saw_section:
        raise _Refuse(DxfRefusalReason.MALFORMED_STRUCTURE, "no DXF section markers found")
    return DxfDocument(
        ok=True,
        units=_resolve_units(state.insunits_code),
        acad_version=state.acad_version,
        primitives=tuple(state.primitives),
        disclosed_unknown=tuple(sorted(state.unknown.items())),
        skipped_sections=tuple(sorted(state.skipped)),
        entity_count=state.entity_count,
    )


def _resolve_units(code: int | None) -> DxfUnits:
    if code is None:
        return DxfUnits(code=None, name="unitless", source="absent")
    name = _INSUNITS_NAMES.get(code, f"unknown_insunits_{code}")
    return DxfUnits(code=code, name=name, source="header:$INSUNITS")


def read_dxf(data: bytes | str, *, limits: DxfLimits = DEFAULT_LIMITS) -> DxfReadResult:
    """Read a strict-subset ASCII DXF into typed primitives, or a typed refusal VALUE.

    ``data`` is the raw DXF file (bytes preferred so the binary-DXF sentinel and byte size
    can be checked; a ``str`` is accepted for in-test convenience). Never raises: every
    failure - malformed structure, an over-limit input, an unsupported feature, or even an
    unexpected internal error - is returned as a :class:`DxfRefusal`.
    """
    try:
        text = _decode(data, limits)
        pairs = _to_pairs(text, limits)
        return _walk(pairs, limits)
    except _Refuse as refusal:
        return DxfRefusal(ok=False, reason=refusal.reason, detail=refusal.detail)
    except Exception as exc:  # defensive: no exception ever escapes read_dxf
        return DxfRefusal(
            ok=False,
            reason=DxfRefusalReason.MALFORMED_STRUCTURE,
            detail=f"unexpected {type(exc).__name__}: {exc}",
        )
