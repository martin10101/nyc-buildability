"""Zero-dependency ASCII DXF writer for proposed site plans (task M5-T081,
D-087 CAD-1).

Purpose: emit an AutoCAD-openable ASCII DXF (the D-087-R004 "working reading /
middleman" path) for a proposed building option - a layered site plan carrying
the tax lot, the building footprint, a 3D massing (3DFACE wall quads per floor
band plus closed outline polylines at each elevation) and a fixed provenance
annotation. AutoCAD opens this DXF natively and can save it as DWG; native DWG
writing stays an owner licensing decision (D-087-R007) and is out of scope.

Determinism and safety commitments:

* STDLIB ONLY - no new dependency, no network, no I/O. The public builder
  returns the DXF as a ``str``; the caller decides where the bytes go. Identical
  inputs give byte-identical output (a golden sha256 is pinned in the tests).
* FORMAT AUTHORITY - every section order, header variable, table field and
  entity group code follows the Autodesk DXF Reference (help.autodesk.com,
  "DXF Reference"). This module was authored WITHOUT network access, so each
  structural citation is marked ``[recalled - verify]`` for the G1
  data-contract-verifier (who has network) to confirm against the live
  reference; the parallel research packet M5-T084 records the official notes.
  Version AC1009 (AutoCAD Release 12) is chosen deliberately: it is the most
  widely openable ASCII DXF and needs no entity handles, no OBJECTS section and
  no CLASSES section (DXF Reference, "AutoCAD Drawing Database Version Number"
  / ``$ACADVER`` values [recalled - verify]).
* ONE SANITIZER - every value that reaches the group-code stream passes through
  a single choke point (``_GroupCodeStream.pair`` -> ``_sanitize_value``). No
  carriage return, line feed, other control character, or non-ASCII byte can
  enter the stream; a violation is a typed refusal, never a scrubbed-and-emitted
  value. Because the whole document is assembled in memory and only returned on
  success, any refusal yields NO partial output.
* FAIL CLOSED - non-finite or over-magnitude coordinates, degenerate or
  duplicate-vertex rings, invalid layer names, over-cap floor counts, and
  over-cap entity counts each raise a typed ``DxfValidationError`` with a
  machine-readable ``code``. The builder refuses an oversized request BEFORE it
  materializes any geometry, and every coordinate that reaches the output passes
  the magnitude bound at the numeric choke point ``_format_real``. There is no
  "best effort" partial drawing.
* HONESTY (D-073-R006 / D-076-R002 / D-083 vocabulary) - the ANNOTATION layer
  always carries "PROPOSED - NOT A CITY RECORD", the CRS/units note (EPSG:2263,
  US survey feet) and the generator identity. Nothing emitted is ever labelled
  permitted, approved, certified, compliant or "maximum allowed building"; this
  module draws geometry and states no legal conclusion.

Coordinates are world coordinates in EPSG:2263 (NAD83 New York Long Island, US
survey feet); the input rings mirror the EPSG:2263 rings served by
``app.connectors.mappluto_geometry_arcgis`` (read-only reference, not imported).
Deterministic code only: no AI, no legal interpretation, no approval.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

# CLAIM_CLASS_WORDS is re-exported as an identity-equal compatibility alias
# (pdf_sheet_writer and the tests import it from this module); the explicit
# ``as`` form marks the intentional re-export.
from app.cad.claim_words import CLAIM_CLASS_WORDS as CLAIM_CLASS_WORDS
from app.cad.claim_words import contains_claim_word

# --------------------------------------------------------------------------- #
# Format constants - Autodesk DXF Reference. Each citation is [recalled - verify]
# (authored offline); the G1 data-contract-verifier confirms against the live
# reference and the M5-T084 research notes.
# --------------------------------------------------------------------------- #

#: $ACADVER value for AutoCAD Release 12 (DXF Reference, HEADER Section Group
#: Codes, "$ACADVER" -> group code 1; AC1009 = R12) [recalled - verify].
DXF_VERSION_R12 = "AC1009"

#: $INSUNITS integer for US SURVEY FEET (DXF Reference, HEADER Section Group
#: Codes, "$INSUNITS" -> group code 70; 21 = US Survey Feet). NYC geometry is
#: EPSG:2263 (US survey feet), so the drawing self-declares survey feet, NOT
#: international feet (code 2). Code 21 exists precisely to distinguish survey
#: from international feet and was ADDED in the AutoCAD 2017 DXF reference
#: (docs/research/dxf-format-reference-2026-09.md sections 0.2/3/7, primary
#: sources [HDR2026]/[HDR2017], verbatim: "a writer that means survey feet
#: should set $INSUNITS 21, not 2 (international feet)"; codes 22-24 = US Survey
#: Inch/Yard/Mile). $INSUNITS itself postdates a strict R12 reader (it entered
#: wide use at R2000) and is written here as an ordinary header variable; the
#: exact CRS is ALSO stated verbatim on the ANNOTATION layer, so no unit fact
#: depends solely on a reader honouring $INSUNITS.
INSUNITS_US_SURVEY_FEET = 21

#: Line ending. LF is chosen for byte-deterministic, cross-platform output;
#: DXF readers split on any newline and the sanitizer forbids CR/LF inside
#: values, so no value can forge a line break (DXF Reference, "ASCII DXF
#: files") [recalled - verify].
_EOL = "\n"

#: Coordinate/real formatting precision. Six decimals round-trip every fixture
#: coordinate and keep output deterministic across platforms.
_COORD_DECIMALS = 6

# --------------------------------------------------------------------------- #
# Layers (DXF Reference, TABLES Section, LAYER table; symbol-name rules:
# uppercase letters/digits/`$`/`_`/`-`, no spaces, <= 31 chars for R12
# [recalled - verify]). Colours are AutoCAD Color Index numbers (group code 62).
# --------------------------------------------------------------------------- #

LAYER_LOT = "LOT"
LAYER_BUILDING_OUTLINE = "BUILDING_OUTLINE"
LAYER_MASSING_3D = "MASSING_3D"
LAYER_ANNOTATION = "ANNOTATION"

#: Ordered (name, ACI colour) layer definitions written to the LAYER table.
LAYER_DEFINITIONS: tuple[tuple[str, int], ...] = (
    (LAYER_LOT, 7),               # 7 = white/black
    (LAYER_BUILDING_OUTLINE, 5),  # 5 = blue
    (LAYER_MASSING_3D, 3),        # 3 = green
    (LAYER_ANNOTATION, 2),        # 2 = yellow
)

# --------------------------------------------------------------------------- #
# Text style (STYLE) and active viewport (VPORT) tables.
#
# STYLE record group codes CHECKED against the LIVE Autodesk DXF Reference
# "STYLE (DXF)" page (help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF,
# GUID-EF68AF7C-13EF-45A1-8175-ED6CE66C8FC9, retrieved 2026-09-24 UTC): 2 = style
# name, 70 = standard flags (1 = shape, 4 = vertical), 40 = fixed text height
# (0 = not fixed), 41 = width factor, 50 = oblique angle, 71 = text-generation
# flags, 42 = last height used, 3 = primary font file, 4 = bigfont file (blank if
# none). The record is stable across releases, so it applies unchanged to R12.
# Every TEXT entity here omits the optional style-name group 7 and therefore
# resolves to the default STANDARD style (DXF Reference, TEXT: "7 = text style
# name (optional, default STANDARD)"); defining STANDARD in a STYLE table makes
# that referenced style PRESENT in the file rather than reconstructed by the
# reader (closes G1 advisory A2 from M5-T081-G1.md / DB-057 b).
# --------------------------------------------------------------------------- #

STYLE_STANDARD_NAME = "STANDARD"

#: STANDARD uses AutoCAD's built-in "txt" SHX font (group 3); the reader resolves
#: "txt" to txt.shx. The bigfont file (group 4) is blank.
STYLE_PRIMARY_FONT = "txt"
STYLE_BIGFONT = ""
STYLE_FIXED_HEIGHT = 0.0      # group 40: 0 -> height taken per-TEXT (its own group 40)
STYLE_WIDTH_FACTOR = 1.0      # group 41
STYLE_OBLIQUE_ANGLE = 0.0     # group 50
STYLE_LAST_HEIGHT = 0.2       # group 42 (last height used); a cosmetic default

# VPORT record group codes are the R12/AC1009 layout [recalled - verify]. The
# LIVE 2024 "VPORT (DXF)" page (GUID-8CE7CC87-27BD-4490-89DA-C21F516415A9,
# retrieved 2026-09-24 UTC) is the R2000+ subclass form: it relocates VIEW HEIGHT
# to group 45 and adds render-mode (281) and UCS groups. In an R12 file AutoCAD
# reads the VPORT with the R12 schema, where VIEW HEIGHT = group 40 and VIEWPORT
# ASPECT RATIO = group 41 (lens length 42, clipping 43/44). This *ACTIVE record
# uses the R12 group codes so a native R12 reader frames the drawing. The codes
# shared with the live modern page (2 = name, 10/20 + 11/21 = viewport corners,
# 12/22 = view centre in DCS, 13-15/23-25 = snap/grid, 16/26/36 = view direction,
# 17/27/37 = view target, 42 = lens length, 50/51 = snap-rotation/twist,
# 71 = view mode, 72 = circle sides, 74 = UCSICON) are CHECKED against that page.

#: The current-viewport configuration record is always named "*ACTIVE" (VPORT
#: page, CHECKED: "The entries corresponding to the active viewport ... all have
#: the name *ACTIVE. The first such entry describes the current viewport.").
VPORT_ACTIVE_NAME = "*ACTIVE"
VPORT_LENS_LENGTH = 50.0      # group 42 (CHECKED: "Lens length")
VPORT_ASPECT_RATIO = 1.0      # group 41 (R12): a square view covers the larger span
VPORT_FRAME_MARGIN = 1.1      # 10% margin so the extents sit inside the framed view
VPORT_CIRCLE_SIDES = 1000     # group 72 (CHECKED: "Circle sides"); display-only

# --------------------------------------------------------------------------- #
# Fixed provenance annotation (honesty; D-073-R006 / D-076-R002 / D-083).
# --------------------------------------------------------------------------- #

GENERATOR_ID = "NYC-BUILDABILITY DXF WRITER"
GENERATOR_VERSION = "1"

PROPOSED_LABEL = "PROPOSED - NOT A CITY RECORD"
CRS_UNITS_NOTE = "COORDINATES: EPSG:2263 NAD83 NY LONG ISLAND - US SURVEY FEET"
GENERATOR_NOTE = f"GENERATED BUILDING OPTION - {GENERATOR_ID} V{GENERATOR_VERSION}"

# Claim-class words forbidden in ANY emitted string are the shared canonical list
# in app.cad.claim_words (D-083; M5-T102). ``CLAIM_CLASS_WORDS`` is imported above
# and re-exported here as an identity-equal compatibility alias (pdf_sheet_writer
# and the tests import it from this module); the separator-collapsing screen is
# app.cad.claim_words.contains_claim_word.

# --------------------------------------------------------------------------- #
# Bounds and caps (fail-closed).
# --------------------------------------------------------------------------- #

#: Total emitted-entity cap. A proposed site plan is small; a request that would
#: exceed this is a typed refusal, not a multi-megabyte drawing.
MAX_ENTITIES = 50_000

#: Per-ring vertex cap.
MAX_RING_VERTICES = 10_000

#: Per-building floor cap. A proposed building's floor stack is bounded; a
#: larger floor count is a typed refusal enforced BEFORE any geometry is
#: materialized (mirrors the massing truth object's total-floor ceiling).
MAX_FLOORS = 2_000

#: Coordinate-magnitude bound (absolute value, US survey feet). A finite but
#: astronomically large coordinate formats to a ~300-digit token that would
#: confuse AutoCAD; anything beyond this bound is a typed refusal at the numeric
#: choke point ``_format_real`` (mirrors the PDF sheet writer's 1e8 bound). NYC
#: EPSG:2263 coordinates are ~1e6, so real geometry is far inside this bound.
MAX_COORD_ABS = 1e8

#: Rings below this absolute planar area (sq ft) are degenerate.
_AREA_EPSILON = 1e-9

#: Allowed value bytes = printable ASCII only (0x20-0x7E). Control characters
#: (incl. CR 0x0D, LF 0x0A, DEL 0x7F) and non-ASCII are rejected.
_ALLOWED_MIN, _ALLOWED_MAX = 0x20, 0x7E

#: Symbol-name (layer/linetype) rule for R12 [recalled - verify].
_SYMBOL_NAME_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$-")
_SYMBOL_NAME_MAX = 31

Coord2D = tuple[float, float]
Coord3D = tuple[float, float, float]


# --------------------------------------------------------------------------- #
# Typed errors - fail closed, no partial output.
# --------------------------------------------------------------------------- #

class DxfWriterError(Exception):
    """Base class for every DXF writer refusal."""


class DxfValidationError(DxfWriterError):
    """Input/model validation refusal. ``code`` is machine-readable."""

    def __init__(self, code: str, message: str, *, field: str | None = None) -> None:
        self.code = code
        self.field = field
        detail = f"{code}: {message}"
        if field is not None:
            detail = f"{detail} (field={field})"
        super().__init__(detail)


class DxfSanitizationError(DxfWriterError):
    """A value carried a forbidden byte (control/CR/LF/non-ASCII). The stream
    is refused so no injected byte can forge a group-code line."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.code = "forbidden_character"
        super().__init__(f"forbidden_character: {message} (field={field})")


# --------------------------------------------------------------------------- #
# Value formatting and the ONE sanitizer.
# --------------------------------------------------------------------------- #

def _format_real(value: float, *, field: str) -> str:
    """Deterministic fixed-decimal real and the single NUMERIC choke point:
    rejects non-finite and over-magnitude values up front so a bad coordinate
    never reaches the stream (mirrors ``_sanitize_value`` for strings)."""
    if not math.isfinite(value):
        raise DxfValidationError(
            "non_finite_coordinate", f"{value!r} is not finite", field=field
        )
    if abs(value) > MAX_COORD_ABS:
        raise DxfValidationError(
            "coordinate_out_of_range",
            f"|{value!r}| exceeds magnitude bound {MAX_COORD_ABS:.0f}",
            field=field,
        )
    if value == 0.0:  # normalise -0.0 -> 0.0 for stable bytes
        value = 0.0
    return f"{value:.{_COORD_DECIMALS}f}"


def _sanitize_value(value: str, *, field: str) -> str:
    """The single choke point every group-code value passes through.

    Rejects control characters (including CR and LF, which would otherwise
    forge extra group-code lines) and any non-ASCII byte. Returns the value
    unchanged when it is clean; never scrubs-and-continues.
    """
    if not isinstance(value, str):
        raise DxfSanitizationError(field, f"value must be str, got {type(value).__name__}")
    for ch in value:
        code = ord(ch)
        if code < _ALLOWED_MIN or code > _ALLOWED_MAX:
            raise DxfSanitizationError(
                field, f"illegal byte 0x{code:02x} in {value!r}"
            )
    return value


class _GroupCodeStream:
    """Accumulates (group code, value) pairs and renders them as ASCII DXF.

    ``pair`` is the sole serialization primitive; it sanitizes every value, so
    string entity fields and formatted numbers alike flow through one guard.
    """

    __slots__ = ("_lines",)

    def __init__(self) -> None:
        self._lines: list[str] = []

    def pair(self, code: int, value: str) -> None:
        clean = _sanitize_value(value, field=f"group_code_{code}")
        self._lines.append(str(int(code)))
        self._lines.append(clean)

    def real(self, code: int, value: float) -> None:
        self.pair(code, _format_real(value, field=f"group_code_{code}"))

    def render(self) -> str:
        # Trailing EOL: DXF files end with a final newline after 0/EOF.
        return _EOL.join(self._lines) + _EOL


# --------------------------------------------------------------------------- #
# Symbol-name and geometry validation helpers.
# --------------------------------------------------------------------------- #

def _validate_layer_name(name: str) -> None:
    if not name or len(name) > _SYMBOL_NAME_MAX:
        raise DxfValidationError(
            "invalid_layer_name", f"{name!r} length out of range 1..{_SYMBOL_NAME_MAX}",
            field="layer",
        )
    if any(ch not in _SYMBOL_NAME_CHARS for ch in name):
        raise DxfValidationError(
            "invalid_layer_name",
            f"{name!r} has characters outside the R12 symbol-name set",
            field="layer",
        )


def _signed_area(points: Sequence[Coord2D]) -> float:
    """Shoelace signed area of the ring (implicitly closed)."""
    total = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return total / 2.0


# --------------------------------------------------------------------------- #
# Typed document model.
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Ring:
    """A closed outline. ``points`` are OPEN (no repeated closing vertex); the
    writer emits the closed flag. Rendered as a closed 2D POLYLINE at
    ``elevation`` (DXF Reference, POLYLINE/VERTEX [recalled - verify])."""

    layer: str
    points: tuple[Coord2D, ...]
    elevation: float = 0.0

    def validate(self) -> None:
        _validate_layer_name(self.layer)
        if not math.isfinite(self.elevation):
            raise DxfValidationError(
                "non_finite_coordinate", "ring elevation is not finite", field=self.layer
            )
        pts = self.points
        if len(pts) < 3:
            raise DxfValidationError(
                "degenerate_ring", "a ring needs at least 3 vertices", field=self.layer
            )
        if len(pts) > MAX_RING_VERTICES:
            raise DxfValidationError(
                "ring_cap_exceeded",
                f"{len(pts)} vertices exceed cap {MAX_RING_VERTICES}",
                field=self.layer,
            )
        for x, y in pts:
            if not (math.isfinite(x) and math.isfinite(y)):
                raise DxfValidationError(
                    "non_finite_coordinate", f"({x!r}, {y!r}) is not finite",
                    field=self.layer,
                )
        n = len(pts)
        for i in range(n):
            if pts[i] == pts[(i + 1) % n]:
                raise DxfValidationError(
                    "duplicate_vertices", f"vertex {i} repeats its neighbour",
                    field=self.layer,
                )
        if abs(_signed_area(pts)) < _AREA_EPSILON:
            raise DxfValidationError(
                "degenerate_ring", "ring encloses zero area", field=self.layer
            )


@dataclass(frozen=True)
class Face3D:
    """A planar 3DFACE quad (four corners; DXF Reference, 3DFACE
    [recalled - verify])."""

    layer: str
    corners: tuple[Coord3D, Coord3D, Coord3D, Coord3D]

    def validate(self) -> None:
        _validate_layer_name(self.layer)
        for x, y, z in self.corners:
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                raise DxfValidationError(
                    "non_finite_coordinate", "3DFACE corner is not finite",
                    field=self.layer,
                )


@dataclass(frozen=True)
class LineSegment:
    """A straight LINE (DXF Reference, LINE [recalled - verify])."""

    layer: str
    start: Coord3D
    end: Coord3D

    def validate(self) -> None:
        _validate_layer_name(self.layer)
        for x, y, z in (self.start, self.end):
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                raise DxfValidationError(
                    "non_finite_coordinate", "LINE endpoint is not finite",
                    field=self.layer,
                )
        if self.start == self.end:
            raise DxfValidationError(
                "degenerate_line", "LINE start equals end", field=self.layer
            )


@dataclass(frozen=True)
class TextLabel:
    """Single-line TEXT (DXF Reference, TEXT [recalled - verify]). The string is
    NOT sanitized here on purpose; the emit-time stream sanitizer is the single
    guard, proven by the injection test."""

    layer: str
    position: Coord3D
    height: float
    text: str

    def validate(self) -> None:
        _validate_layer_name(self.layer)
        x, y, z = self.position
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise DxfValidationError(
                "non_finite_coordinate", "TEXT position is not finite", field=self.layer
            )
        if not math.isfinite(self.height) or self.height <= 0.0:
            raise DxfValidationError(
                "invalid_text_height", f"height {self.height!r} must be finite and > 0",
                field=self.layer,
            )


@dataclass
class DxfDocument:
    """A validated, serializable DXF drawing."""

    layers: tuple[tuple[str, int], ...]
    rings: list[Ring] = field(default_factory=list)
    faces: list[Face3D] = field(default_factory=list)
    lines: list[LineSegment] = field(default_factory=list)
    texts: list[TextLabel] = field(default_factory=list)
    extents_min: Coord3D = (0.0, 0.0, 0.0)
    extents_max: Coord3D = (0.0, 0.0, 0.0)

    def entity_count(self) -> int:
        return len(self.rings) + len(self.faces) + len(self.lines) + len(self.texts)

    def validate(self) -> None:
        for name, _color in self.layers:
            _validate_layer_name(name)
        count = self.entity_count()
        if count > MAX_ENTITIES:
            raise DxfValidationError(
                "entity_cap_exceeded", f"{count} entities exceed cap {MAX_ENTITIES}"
            )
        for coord in (self.extents_min, self.extents_max):
            for v in coord:
                if not math.isfinite(v):
                    raise DxfValidationError(
                        "non_finite_coordinate", "drawing extent is not finite",
                        field="$EXTMIN/$EXTMAX",
                    )
        for ring in self.rings:
            ring.validate()
        for face in self.faces:
            face.validate()
        for line in self.lines:
            line.validate()
        for text in self.texts:
            text.validate()


# --------------------------------------------------------------------------- #
# Serialization - section order per DXF Reference [recalled - verify]:
# HEADER, TABLES, ENTITIES, then 0/EOF.
# --------------------------------------------------------------------------- #

def _write_header(s: _GroupCodeStream, doc: DxfDocument) -> None:
    # DXF Reference, HEADER Section: 0/SECTION, 2/HEADER, 9/<var>... , 0/ENDSEC.
    s.pair(0, "SECTION")
    s.pair(2, "HEADER")
    s.pair(9, "$ACADVER")
    s.pair(1, DXF_VERSION_R12)            # group 1 = version string
    s.pair(9, "$INSUNITS")
    s.pair(70, str(INSUNITS_US_SURVEY_FEET))  # group 70 = integer units (21 = US Survey Feet)
    s.pair(9, "$EXTMIN")                  # extents min (group 10/20/30)
    s.real(10, doc.extents_min[0])
    s.real(20, doc.extents_min[1])
    s.real(30, doc.extents_min[2])
    s.pair(9, "$EXTMAX")                  # extents max (group 10/20/30)
    s.real(10, doc.extents_max[0])
    s.real(20, doc.extents_max[1])
    s.real(30, doc.extents_max[2])
    s.pair(0, "ENDSEC")


def _vport_frame(doc: DxfDocument) -> tuple[float, float, float]:
    """Return ``(view_center_x, view_center_y, view_height)`` for the *ACTIVE
    viewport so it FRAMES the drawing extents (with :data:`VPORT_FRAME_MARGIN`).

    The centre is the extents midpoint; the height covers the larger of the
    extents height and width/aspect, so with :data:`VPORT_ASPECT_RATIO` the whole
    drawing is in view. A degenerate span floors at 1.0 to keep the height > 0.
    """
    min_x, min_y = doc.extents_min[0], doc.extents_min[1]
    max_x, max_y = doc.extents_max[0], doc.extents_max[1]
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    width = max_x - min_x
    height = max_y - min_y
    span = max(width / VPORT_ASPECT_RATIO, height, 1.0)
    return center_x, center_y, span * VPORT_FRAME_MARGIN


def _write_vport_table(s: _GroupCodeStream, doc: DxfDocument) -> None:
    # DXF Reference, VPORT table (R12 layout; see the VPORT constants block). One
    # *ACTIVE record framing the drawing extents in a plan view.
    center_x, center_y, view_height = _vport_frame(doc)
    s.pair(0, "TABLE")
    s.pair(2, "VPORT")
    s.pair(70, "1")                       # max entries
    s.pair(0, "VPORT")
    s.pair(2, VPORT_ACTIVE_NAME)          # group 2 = viewport name (*ACTIVE)
    s.pair(70, "0")                       # standard flags
    s.real(10, 0.0)                       # lower-left corner of viewport (screen)
    s.real(20, 0.0)
    s.real(11, 1.0)                       # upper-right corner of viewport (screen)
    s.real(21, 1.0)
    s.real(12, center_x)                  # view centre point (DCS) = extents midpoint
    s.real(22, center_y)
    s.real(13, 0.0)                       # snap base point
    s.real(23, 0.0)
    s.real(14, 1.0)                       # snap spacing X/Y
    s.real(24, 1.0)
    s.real(15, 10.0)                      # grid spacing X/Y
    s.real(25, 10.0)
    s.real(16, 0.0)                       # view direction from target (WCS): plan (+Z)
    s.real(26, 0.0)
    s.real(36, 1.0)
    s.real(17, 0.0)                       # view target point (WCS)
    s.real(27, 0.0)
    s.real(37, 0.0)
    s.real(40, view_height)               # group 40 (R12) = view height (frames extents)
    s.real(41, VPORT_ASPECT_RATIO)        # group 41 (R12) = viewport aspect ratio
    s.real(42, VPORT_LENS_LENGTH)         # group 42 = lens length
    s.real(43, 0.0)                       # front clipping plane offset
    s.real(44, 0.0)                       # back clipping plane offset
    s.real(50, 0.0)                       # snap rotation angle
    s.real(51, 0.0)                       # view twist angle
    s.pair(71, "0")                       # view mode
    s.pair(72, str(int(VPORT_CIRCLE_SIDES)))  # circle sides (display-only)
    s.pair(73, "1")                       # fast zoom setting
    s.pair(74, "3")                       # UCSICON setting
    s.pair(75, "0")                       # snap on/off
    s.pair(76, "0")                       # grid on/off
    s.pair(77, "0")                       # snap style
    s.pair(78, "0")                       # snap isopair
    s.pair(0, "ENDTAB")


def _write_ltype_table(s: _GroupCodeStream) -> None:
    # LTYPE table with the single CONTINUOUS linetype (DXF Reference, LTYPE).
    s.pair(0, "TABLE")
    s.pair(2, "LTYPE")
    s.pair(70, "1")                       # max entries
    s.pair(0, "LTYPE")
    s.pair(2, "CONTINUOUS")               # group 2 = linetype name
    s.pair(70, "0")                       # standard flags
    s.pair(3, "Solid line")               # group 3 = descriptive text
    s.pair(72, "65")                      # group 72 = alignment code 'A'
    s.pair(73, "0")                       # group 73 = dash count (0 = solid)
    s.real(40, 0.0)                       # group 40 = total pattern length
    s.pair(0, "ENDTAB")


def _write_layer_table(s: _GroupCodeStream, doc: DxfDocument) -> None:
    # LAYER table (DXF Reference, LAYER).
    s.pair(0, "TABLE")
    s.pair(2, "LAYER")
    s.pair(70, str(len(doc.layers)))      # max entries
    for name, color in doc.layers:
        s.pair(0, "LAYER")
        s.pair(2, name)                   # group 2 = layer name
        s.pair(70, "0")                   # standard flags
        s.pair(62, str(int(color)))       # group 62 = ACI colour
        s.pair(6, "CONTINUOUS")           # group 6 = linetype name
    s.pair(0, "ENDTAB")


def _write_style_table(s: _GroupCodeStream) -> None:
    # STYLE table (DXF Reference; see the STYLE constants block). One STANDARD
    # text style so every default-styled TEXT resolves to a defined style.
    s.pair(0, "TABLE")
    s.pair(2, "STYLE")
    s.pair(70, "1")                       # max entries
    s.pair(0, "STYLE")
    s.pair(2, STYLE_STANDARD_NAME)        # group 2 = style name
    s.pair(70, "0")                       # standard flags (0 = ordinary text style)
    s.real(40, STYLE_FIXED_HEIGHT)        # group 40 = fixed text height (0 = not fixed)
    s.real(41, STYLE_WIDTH_FACTOR)        # group 41 = width factor
    s.real(50, STYLE_OBLIQUE_ANGLE)       # group 50 = oblique angle
    s.pair(71, "0")                       # group 71 = text-generation flags
    s.real(42, STYLE_LAST_HEIGHT)         # group 42 = last height used
    s.pair(3, STYLE_PRIMARY_FONT)         # group 3 = primary font file
    s.pair(4, STYLE_BIGFONT)              # group 4 = bigfont file (blank)
    s.pair(0, "ENDTAB")


def _write_tables(s: _GroupCodeStream, doc: DxfDocument) -> None:
    # DXF Reference, TABLES Section. Canonical R12 write order is VPORT, LTYPE,
    # LAYER, STYLE [recalled - verify]; LTYPE precedes LAYER because a layer's
    # group 6 references the CONTINUOUS linetype, and the STANDARD text style the
    # TEXT entities use is defined last.
    s.pair(0, "SECTION")
    s.pair(2, "TABLES")
    _write_vport_table(s, doc)
    _write_ltype_table(s)
    _write_layer_table(s, doc)
    _write_style_table(s)
    s.pair(0, "ENDSEC")


def _write_polyline(s: _GroupCodeStream, ring: Ring) -> None:
    # DXF Reference, POLYLINE/VERTEX/SEQEND [recalled - verify].
    s.pair(0, "POLYLINE")
    s.pair(8, ring.layer)                 # group 8 = layer
    s.pair(66, "1")                       # group 66 = vertices follow
    s.pair(70, "1")                       # group 70 bit 1 = closed
    s.real(10, 0.0)                       # dummy base point x
    s.real(20, 0.0)                       # dummy base point y
    s.real(30, ring.elevation)            # group 30 = polyline elevation
    for x, y in ring.points:
        s.pair(0, "VERTEX")
        s.pair(8, ring.layer)
        s.real(10, x)
        s.real(20, y)
        s.real(30, ring.elevation)
    s.pair(0, "SEQEND")
    s.pair(8, ring.layer)


def _write_face(s: _GroupCodeStream, face: Face3D) -> None:
    s.pair(0, "3DFACE")
    s.pair(8, face.layer)
    for idx, (x, y, z) in enumerate(face.corners):
        s.real(10 + idx, x)               # 10,11,12,13
        s.real(20 + idx, y)               # 20,21,22,23
        s.real(30 + idx, z)               # 30,31,32,33


def _write_line(s: _GroupCodeStream, line: LineSegment) -> None:
    s.pair(0, "LINE")
    s.pair(8, line.layer)
    s.real(10, line.start[0])
    s.real(20, line.start[1])
    s.real(30, line.start[2])
    s.real(11, line.end[0])
    s.real(21, line.end[1])
    s.real(31, line.end[2])


def _write_text(s: _GroupCodeStream, text: TextLabel) -> None:
    s.pair(0, "TEXT")
    s.pair(8, text.layer)
    s.real(10, text.position[0])
    s.real(20, text.position[1])
    s.real(30, text.position[2])
    s.real(40, text.height)               # group 40 = text height
    s.pair(1, text.text)                  # group 1 = text string


def _write_entities(s: _GroupCodeStream, doc: DxfDocument) -> None:
    s.pair(0, "SECTION")
    s.pair(2, "ENTITIES")
    for ring in doc.rings:
        _write_polyline(s, ring)
    for face in doc.faces:
        _write_face(s, face)
    for line in doc.lines:
        _write_line(s, line)
    for text in doc.texts:
        _write_text(s, text)
    s.pair(0, "ENDSEC")


def serialize_document(doc: DxfDocument) -> str:
    """Validate then render ``doc`` to an ASCII DXF string. Any refusal raises
    before the string is returned, so no partial output escapes."""
    doc.validate()
    s = _GroupCodeStream()
    _write_header(s, doc)
    _write_tables(s, doc)
    _write_entities(s, doc)
    s.pair(0, "EOF")                      # DXF Reference: file terminates 0/EOF
    return s.render()


# --------------------------------------------------------------------------- #
# Site-plan builder.
# --------------------------------------------------------------------------- #

def _normalize_ring(raw: Sequence[Sequence[float]], *, field: str) -> tuple[Coord2D, ...]:
    """Coerce an (x, y) sequence to a tuple of float pairs, dropping a repeated
    closing vertex if present. Shape errors are typed refusals."""
    try:
        pts = [(float(p[0]), float(p[1])) for p in raw]
    except (TypeError, ValueError, IndexError) as exc:
        raise DxfValidationError(
            "invalid_ring_shape", f"{field} must be a sequence of (x, y) pairs: {exc}",
            field=field,
        ) from None
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]  # accept a pre-closed ring by dropping the duplicate
    return tuple(pts)


def _assert_no_claim_words(text: str) -> None:
    # Separator-insensitive shared screen (app.cad.claim_words): "As_of_right" /
    # "MAXIMUM  ALLOWED" are caught here just as the PDF/GLB writers catch them.
    barred = contains_claim_word(text)
    if barred is not None:
        raise DxfValidationError(
            "claim_class_word", f"{text!r} contains barred word {barred!r}",
            field=LAYER_ANNOTATION,
        )


def _build_annotation(
    lot: tuple[Coord2D, ...], base_elevation: float
) -> list[TextLabel]:
    xs = [x for x, _ in lot]
    ys = [y for _, y in lot]
    min_x, min_y = min(xs), min(ys)
    span = max(max(xs) - min_x, max(ys) - min_y, 1.0)
    height = round(span / 50.0, _COORD_DECIMALS)
    gap = height * 1.5
    top_y = min_y - height * 2.0
    labels: list[TextLabel] = []
    for i, message in enumerate((PROPOSED_LABEL, CRS_UNITS_NOTE, GENERATOR_NOTE)):
        _assert_no_claim_words(message)
        labels.append(
            TextLabel(
                layer=LAYER_ANNOTATION,
                position=(min_x, top_y - i * gap, base_elevation),
                height=height,
                text=message,
            )
        )
    return labels


def _compute_extents(doc_parts: DxfDocument) -> tuple[Coord3D, Coord3D]:
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for ring in doc_parts.rings:
        for x, y in ring.points:
            xs.append(x)
            ys.append(y)
            zs.append(ring.elevation)
    for face in doc_parts.faces:
        for x, y, z in face.corners:
            xs.append(x)
            ys.append(y)
            zs.append(z)
    for line in doc_parts.lines:
        for x, y, z in (line.start, line.end):
            xs.append(x)
            ys.append(y)
            zs.append(z)
    for text in doc_parts.texts:
        x, y, z = text.position
        xs.append(x)
        ys.append(y)
        zs.append(z)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def build_site_plan_document(
    lot: Sequence[Sequence[float]],
    building: Sequence[Sequence[float]],
    floor_heights: Sequence[float],
    *,
    base_elevation: float = 0.0,
) -> DxfDocument:
    """Build a validated :class:`DxfDocument` for a proposed site plan.

    ``lot`` and ``building`` are open EPSG:2263 (x, y) rings; ``floor_heights``
    is one positive height (US survey feet) per floor. Layers produced: LOT
    (footprint of the tax lot), BUILDING_OUTLINE (building footprint),
    MASSING_3D (3DFACE wall quads = building_edges x floors, closed outline
    polylines at every band elevation = floors + 1, and one vertical LINE per
    building corner), ANNOTATION (fixed provenance labels).
    """
    lot_ring = _normalize_ring(lot, field="lot")
    building_ring = _normalize_ring(building, field="building")

    # Resource bounds enforced BEFORE materializing any ring/face/line (G5 F1):
    # a typed refusal on an oversized request, never a multi-gigabyte allocation
    # first. len(floor_heights) is read before the heights tuple is built, so a
    # 10-million-floor request refuses in O(1) with no allocation.
    n_floors = len(floor_heights)
    if n_floors > MAX_FLOORS:
        raise DxfValidationError(
            "floor_cap_exceeded", f"{n_floors} floors exceed cap {MAX_FLOORS}"
        )
    edge_count = len(building_ring)
    if edge_count > MAX_RING_VERTICES:
        raise DxfValidationError(
            "ring_cap_exceeded",
            f"{edge_count} building vertices exceed cap {MAX_RING_VERTICES}",
            field="building",
        )
    if edge_count * n_floors > MAX_ENTITIES:
        raise DxfValidationError(
            "entity_cap_exceeded",
            f"{edge_count}x{n_floors} wall faces would exceed entity cap {MAX_ENTITIES}",
        )

    heights = tuple(float(h) for h in floor_heights)
    if not heights:
        raise DxfValidationError("no_floors", "at least one floor height is required")
    for h in heights:
        if not math.isfinite(h) or h <= 0.0:
            raise DxfValidationError(
                "invalid_floor_height", f"floor height {h!r} must be finite and > 0"
            )
    base = float(base_elevation)
    if not math.isfinite(base):
        raise DxfValidationError(
            "non_finite_coordinate", "base_elevation is not finite", field="base_elevation"
        )

    # Band elevations: base, base+h0, base+h0+h1, ... (floors + 1 boundaries).
    elevations = [base]
    for h in heights:
        elevations.append(elevations[-1] + h)
    roof = elevations[-1]

    rings: list[Ring] = [
        Ring(LAYER_LOT, lot_ring, base),
        Ring(LAYER_BUILDING_OUTLINE, building_ring, base),
    ]
    # MASSING_3D closed outline polyline at every band elevation (self-contained
    # wireframe independent of the footprint layer).
    for elev in elevations:
        rings.append(Ring(LAYER_MASSING_3D, building_ring, elev))

    # 3DFACE wall quads: one per building edge per floor band. ``edge_count`` is
    # the pre-check value above (len(building_ring)).
    faces: list[Face3D] = []
    for band in range(len(heights)):
        z_bottom, z_top = elevations[band], elevations[band + 1]
        for i in range(edge_count):
            x1, y1 = building_ring[i]
            x2, y2 = building_ring[(i + 1) % edge_count]
            faces.append(
                Face3D(
                    LAYER_MASSING_3D,
                    (
                        (x1, y1, z_bottom),
                        (x2, y2, z_bottom),
                        (x2, y2, z_top),
                        (x1, y1, z_top),
                    ),
                )
            )

    # Vertical corner LINE from base to roof at each building vertex.
    lines: list[LineSegment] = [
        LineSegment(LAYER_MASSING_3D, (x, y, base), (x, y, roof))
        for x, y in building_ring
    ]

    texts = _build_annotation(lot_ring, base)

    doc = DxfDocument(
        layers=LAYER_DEFINITIONS,
        rings=rings,
        faces=faces,
        lines=lines,
        texts=texts,
    )
    doc.extents_min, doc.extents_max = _compute_extents(doc)
    doc.validate()
    return doc


def render_site_plan_dxf(
    lot: Sequence[Sequence[float]],
    building: Sequence[Sequence[float]],
    floor_heights: Sequence[float],
    *,
    base_elevation: float = 0.0,
) -> str:
    """Convenience wrapper: build and serialize a proposed site plan in one call.
    Returns the ASCII DXF text (identical inputs -> byte-identical output)."""
    doc = build_site_plan_document(
        lot, building, floor_heights, base_elevation=base_elevation
    )
    return serialize_document(doc)
