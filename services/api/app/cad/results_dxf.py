"""DXF written from the results geometry (task E-03; plan section 3 step 7,
section 5c item 3 "DXF is written from the same geometry"; M1-22).

Reads ONE results document. Its geometry block is loaded and validated by the
drawing kit's loader (:func:`app.drawings.kit.adapter.load_drawing_input`, fail
closed) - the same geometry the site plan and massing SVGs draw - and every
layer's name and color come from the drawing style table
(:mod:`app.drawings.kit.styles`). Nothing is typed in: no ring, height, option
name or measurement label comes from anywhere but the results.

Layers, in this order, each present only when something is drawn on it:

* ``lot_line`` (C-PROP-LINE) - the lot outline, exterior and holes, closed
  polylines at grade;
* ``yard`` (A-ZONE-YARD) - each required yard's outline at grade;
* ``setback_line`` (A-ZONE-STBK-LINE-F05, ...) - ONE LAYER PER LEVEL: the
  setback lines of floor 5 on ``-F05``; floor 0, -1, ... (the results' cellar
  levels) on ``-C01``, ``-C02``, ...; drawn in plan at grade as LINE segments
  (a level's elevation is not in the results when it has no floor row);
* ``envelope`` (A-ZONE-ENVL) - each envelope tier as a 3D wireframe: its
  outline at ``bottom_ft`` and at ``top_ft``, and one vertical edge per vertex;
* the building option's floor plates on their use's layer (A-MASS-RESI, ...),
  each outline at its floor's bottom elevation, stacked by the floor-to-floor
  heights of ``floor_by_floor`` exactly as the massing SVG stacks them;
* ``note`` (A-ANNO-NOTE) - the annotation (:mod:`app.cad.results_dxf_notes`):
  option and revision, the measurement-status note when not surveyed, the
  reason of every layer that is not available, coordinates and units.

Units: coordinates are the results' feet, unscaled and untranslated (1 drawing
unit = 1 ft, 1:1). The header is ``dxf_writer``'s: ``$INSUNITS`` 21 (US survey
feet). For ``EPSG:2263`` that is the CRS's unit; ``local_feet`` is defined by
the results contract as the EPSG:2263 grid moved to a lot corner, so its foot
is the same survey foot.

Lot-only export: when the envelope and floor plates are not available the DXF
still carries the lot outline, with notes naming why the rest is missing. The
older caller-ring path (``app.cad.export_service``, which refuses a DXF
without a building footprint) is left as it is.

The low-level writing - validation, the one ASCII sanitizer, section order,
the tables, ``$INSUNITS`` - is ``app.cad.dxf_writer``'s, reused unchanged.
Pure and deterministic: the same results give byte-identical DXF text. Behind
``LANE_E_ENABLED`` (default off); no route calls it yet.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.cad import dxf_writer as dw
from app.cad.results_dxf_notes import DxfNote, annotation_notes
from app.drawings.kit.adapter import load_drawing_input
from app.drawings.kit.errors import DrawingInputError
from app.drawings.kit.flag import DrawingKitDisabled, drawing_kit_enabled
from app.drawings.kit.model import DrawingInput, LayerUnavailable, Polygon, Unavailable
from app.drawings.kit.model import Ring as KitRing
from app.drawings.kit.projection import floor_levels
from app.drawings.kit.styles import style_for

__all__ = [
    "DrawingInputError",
    "DrawingKitDisabled",
    "ResultsDxf",
    "Unavailable",
    "level_layer",
    "render_results_dxf",
]

#: Annotation text height as a share of the lot's larger side, and the line
#: pitch as a multiple of the height (the same proportions as dxf_writer).
_TEXT_SHARE = 1.0 / 50.0
_LINE_PITCH = 1.5


@dataclass(frozen=True)
class ResultsDxf:
    """A finished DXF: the ASCII text (LF line ends), its layer names in LAYER
    table order, and every annotation line with the results values it prints."""

    text: str
    layers: tuple[str, ...]
    notes: tuple[DxfNote, ...]


def level_layer(floor: int) -> str:
    """The setback-line layer of one level: ``-Fnn`` for floor nn >= 1, and
    ``-C01``, ``-C02``, ... for the results' cellar levels 0, -1, ..."""
    base = style_for("setback_line").cad_layer
    return f"{base}-F{floor:02d}" if floor >= 1 else f"{base}-C{1 - floor:02d}"


class _Drawing:
    """Entities by kind, with each layer registered on first use."""

    def __init__(self) -> None:
        self.layers: dict[str, int] = {}
        self.rings: list[dw.Ring] = []
        self.lines: list[dw.LineSegment] = []
        self.texts: list[dw.TextLabel] = []

    def layer(self, kind: str, name: str | None = None) -> str:
        style = style_for(kind)
        name = name or style.cad_layer
        self.layers.setdefault(name, style.cad_color)
        return name

    def polygon(self, layer: str, polygon: Polygon, z: float) -> None:
        for ring in polygon.rings:
            self.rings.append(dw.Ring(layer, _open(ring), z))


def _open(ring: KitRing) -> tuple[tuple[float, float], ...]:
    return ring[:-1]  # the kit's rings are closed (first == last); dxf_writer closes them


def _draw_setback_lines(d: _Drawing, data: DrawingInput) -> None:
    if isinstance(data.setback_lines, LayerUnavailable):
        return
    for entry in data.setback_lines:
        layer = d.layer("setback_line", level_layer(entry.floor))
        for points in entry.lines:
            for a, b in zip(points, points[1:], strict=False):
                if a != b:  # a repeated point draws nothing
                    d.lines.append(dw.LineSegment(layer, (*a, 0.0), (*b, 0.0)))


def _draw_envelope(d: _Drawing, data: DrawingInput) -> None:
    if isinstance(data.envelope, LayerUnavailable):
        return
    layer = d.layer("envelope")
    for tier in data.envelope:
        d.polygon(layer, tier.outline, tier.bottom_ft)
        d.polygon(layer, tier.outline, tier.top_ft)
        for ring in tier.outline.rings:
            for x, y in _open(ring):
                d.lines.append(dw.LineSegment(layer, (x, y, tier.bottom_ft),
                                              (x, y, tier.top_ft)))


def _draw_floor_plates(d: _Drawing, data: DrawingInput) -> None:
    if isinstance(data.floor_plates, LayerUnavailable):
        return
    levels = floor_levels(data.floor_rows)  # the loader checked every plate has its row
    for plate in data.floor_plates:
        d.polygon(d.layer(plate.use), plate.outline, levels[plate.floor][0])


def _draw_notes(d: _Drawing, data: DrawingInput, notes: Iterable[DxfNote]) -> None:
    xs = [x for x, _ in data.lot.exterior]
    ys = [y for _, y in data.lot.exterior]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    height = round(span * _TEXT_SHARE, 6)
    layer = d.layer("note")
    top = min(ys) - 2.0 * height
    for i, note in enumerate(notes):
        d.texts.append(dw.TextLabel(layer, (min(xs), top - i * _LINE_PITCH * height, 0.0),
                                    height, note.text))


def _extents(d: _Drawing) -> tuple[dw.Coord3D, dw.Coord3D]:
    points = [(x, y, r.elevation) for r in d.rings for x, y in r.points]
    points += [p for line in d.lines for p in (line.start, line.end)]
    points += [t.position for t in d.texts]
    xs, ys, zs = zip(*points, strict=True)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _build(results: Mapping, data: DrawingInput) -> ResultsDxf:
    notes = annotation_notes(results, data)
    d = _Drawing()
    d.polygon(d.layer("lot_line"), data.lot, 0.0)
    if not isinstance(data.yards, LayerUnavailable):
        for yard in data.yards:
            d.polygon(d.layer("yard"), yard.outline, 0.0)
    _draw_setback_lines(d, data)
    _draw_envelope(d, data)
    _draw_floor_plates(d, data)
    _draw_notes(d, data, notes)
    doc = dw.DxfDocument(layers=tuple(d.layers.items()), rings=d.rings, lines=d.lines,
                         texts=d.texts)
    doc.extents_min, doc.extents_max = _extents(d)
    try:
        text = dw.serialize_document(doc)
    except dw.DxfWriterError as exc:  # caps, magnitudes, the sanitizer: one refusal type
        raise DrawingInputError(getattr(exc, "code", "dxf_refused"), str(exc)) from exc
    return ResultsDxf(text=text, layers=tuple(d.layers), notes=tuple(notes))


def render_results_dxf(
    results: Mapping, *, env: Mapping[str, str] | None = None
) -> ResultsDxf | Unavailable:
    """The DXF of one results document, or :class:`Unavailable` (with the
    results' reason) when the results carry no geometry at all. Invalid
    results raise :class:`DrawingInputError`; nothing partial is returned."""
    if not drawing_kit_enabled(env):
        raise DrawingKitDisabled("the results DXF is off (LANE_E_ENABLED is not set)")
    data = load_drawing_input(results)
    if isinstance(data, Unavailable):
        return Unavailable("dxf", data.reason, data.reason_kind, f"{data.source}/reason")
    return _build(results, data)
