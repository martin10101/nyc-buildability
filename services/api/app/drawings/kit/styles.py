"""The drawing style table (plan section 5c item 5) - ONE table, read as data.

Every kind of shape the drawings show maps to its look here: fill color,
outline color and dash, line weight, hatch pattern and CAD layer name. The
site plan, the massing, the legend (generated from what is actually drawn),
and later the PDF and the DXF all read this table, so a shape looks the same
everywhere. ``style_table_as_dict()`` is the serialized form for other
consumers (screen, DXF writer).

Palette: the use colors are the Okabe & Ito "Color Universal Design" (2008)
colorblind-safe set (yellow #F0E442, vermillion #D55E00, blue #0072B2,
reddish purple #CC79A7, bluish green #009E73, sky blue #56B4E9, orange
#E69F00) plus a neutral grey for cellars. The five use fills are checked by
tests for separation under simulated protanopia and deuteranopia (Machado,
Oliveira & Fernandes 2009). Black-and-white print: every area kind also has a
unique hatch (angle, spacing, crossed), so no kind depends on color alone.

Hatches are line families (angle, spacing, optionally crossed at +90 degrees),
which an SVG ``<pattern>`` and a DXF user-defined HATCH can both express.
Line weights and hatch spacing are in points (1/72 in), the SVG user unit.

CAD layer names are PLATFORM-DEFINED (discipline-major-minor, in the style of
the US National CAD Standard; not a certified NCS mapping) - uppercase, no
spaces, at most 31 characters. ``cad_color`` is the layer's AutoCAD Color
Index (DXF group code 62), the nearest of the nine standard indexes (1 red,
2 yellow, 3 green, 4 cyan, 5 blue, 6 magenta, 7 white/black, 8 dark grey,
9 light grey) to the kind's screen color: an R12 DXF has no true color, so
this is the DXF's reading of the same palette. The ``note`` kind (text only,
never in the legend) names the DXF annotation layer (task E-03).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

__all__ = [
    "AREA",
    "LINE",
    "STYLE_TABLE",
    "TEXT",
    "TYPOGRAPHY",
    "Hatch",
    "ShapeStyle",
    "Typography",
    "style_for",
    "style_table_as_dict",
]

AREA = "area"
LINE = "line"
TEXT = "text"


@dataclass(frozen=True)
class Hatch:
    angle_deg: int  # 0 horizontal, 45 / 135 diagonal, 90 vertical
    spacing_pt: float
    crossed: bool  # adds a second family of lines at angle + 90
    color: str
    line_weight_pt: float


@dataclass(frozen=True)
class ShapeStyle:
    kind: str
    label: str  # legend text
    geometry: str  # AREA, LINE or TEXT
    fill: str | None
    outline: str
    line_weight_pt: float
    dash_pt: tuple[float, ...]  # () = solid
    hatch: Hatch | None
    cad_layer: str
    in_legend: bool
    cad_color: int  # AutoCAD Color Index, DXF group code 62


@dataclass(frozen=True)
class Typography:
    font_family: str
    title_pt: float
    label_pt: float
    dimension_pt: float
    note_pt: float
    char_width_em: float  # conservative average glyph width, for label collision boxes


# Open-source family first (plan section 5c item 5), then common fallbacks.
TYPOGRAPHY = Typography(
    font_family="Inter, 'Helvetica Neue', Arial, sans-serif",
    title_pt=11.0,
    label_pt=8.0,
    dimension_pt=8.0,
    note_pt=7.5,
    char_width_em=0.6,
)

_USE_OUTLINE = "#222222"


def _use(
    kind: str, label: str, fill: str, hatch: Hatch | None, layer: str, aci: int
) -> ShapeStyle:
    return ShapeStyle(kind, label, AREA, fill, _USE_OUTLINE, 0.5, (), hatch, layer, True, aci)


def _hatch(angle: int, spacing: float, crossed: bool, color: str) -> Hatch:
    return Hatch(angle, spacing, crossed, color, 0.4)


# Legend order = table order.
STYLE_TABLE: tuple[ShapeStyle, ...] = (
    # Uses - the floor_use vocabulary of results.schema.json.
    _use("residential", "Residential", "#F0E442", None, "A-MASS-RESI", 2),
    _use("commercial", "Commercial", "#D55E00", _hatch(0, 6.0, False, "#222222"),
         "A-MASS-COMM", 1),
    _use(
        "community_facility", "Community facility", "#0072B2",
        _hatch(90, 6.0, False, "#222222"), "A-MASS-CFAC", 5,
    ),
    _use("cellar", "Cellar", "#BDBDBD", _hatch(0, 6.0, True, "#222222"), "A-MASS-CELR", 9),
    _use(
        "bulkhead_or_mechanical", "Bulkhead or mechanical", "#CC79A7",
        _hatch(45, 6.0, True, "#222222"), "A-MASS-MECH", 6,
    ),
    # Zones on the lot - a pale wash identified by its hatch.
    ShapeStyle("yard", "Yard", AREA, "#D9F0EA", "#009E73", 0.75, (),
               _hatch(45, 6.0, False, "#009E73"), "A-ZONE-YARD", True, 3),
    ShapeStyle("court", "Court", AREA, "#E6F4FC", "#0072B2", 0.75, (),
               _hatch(135, 6.0, False, "#0072B2"), "A-ZONE-CORT", True, 4),
    ShapeStyle("setback_zone", "Setback zone", AREA, "#FBF1D9", "#E69F00", 0.75, (),
               _hatch(45, 3.0, False, "#E69F00"), "A-ZONE-STBK", True, 2),
    # Lines.
    ShapeStyle("setback_line", "Setback line", LINE, None, "#D55E00", 1.0, (6.0, 3.0),
               None, "A-ZONE-STBK-LINE", True, 1),
    ShapeStyle("envelope", "Envelope", LINE, None, "#0072B2", 1.0, (2.0, 2.0),
               None, "A-ZONE-ENVL", True, 5),
    ShapeStyle("lot_line", "Lot line", LINE, None, "#000000", 1.5, (),
               None, "C-PROP-LINE", True, 7),
    ShapeStyle("dimension", "Dimension", LINE, None, "#333333", 0.5, (),
               None, "A-ANNO-DIMS", False, 8),
    # Location and zoning maps (task E-07, plan section 5c item 2) - context drawn
    # from city open data. Neutral washes so no map kind implies a use color, and
    # each carries a unique hatch so the map reads in black-and-white print. The
    # subject lot is emphasised (bold outline, cross-hatch) so it stands out on
    # both maps; the zoning district fill is a single neutral wash (the exact
    # district symbol is the label, never a color-coded classification). cad_color
    # (required since E-03) is the nearest standard AutoCAD index to each screen color.
    ShapeStyle("subject_lot", "Subject lot", AREA, "#FDE9D0", "#C8500A", 1.5, (),
               _hatch(0, 3.0, True, "#C8500A"), "A-PROP-SUBJ", True, 1),
    ShapeStyle("zoning_district", "Zoning district", AREA, "#EAF0F6", "#4A6572", 0.75, (),
               _hatch(135, 3.0, False, "#4A6572"), "A-ZONE-DIST", True, 8),
    ShapeStyle("building_footprint", "Building footprint", AREA, "#E0E0E0", "#9E9E9E", 0.4, (),
               _hatch(90, 3.0, False, "#9E9E9E"), "A-BLDG-FTPR", True, 9),
    # Text - drawing notes (the DXF annotation layer).
    ShapeStyle("note", "Note", TEXT, None, "#111111", 0.25, (),
               None, "A-ANNO-NOTE", False, 7),
)

_BY_KIND = {style.kind: style for style in STYLE_TABLE}


def style_for(kind: str) -> ShapeStyle:
    """The look of one kind of shape; an unknown kind fails loudly."""
    try:
        return _BY_KIND[kind]
    except KeyError:
        raise ValueError(f"no drawing style for kind {kind!r}") from None


def style_table_as_dict() -> dict:
    """JSON-ready form of the table (and typography), in table order."""
    return {
        "typography": asdict(TYPOGRAPHY),
        "styles": [
            {**asdict(style), "dash_pt": list(style.dash_pt)} for style in STYLE_TABLE
        ],
    }
