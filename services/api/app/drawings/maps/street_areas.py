"""Street areas: the open space between the tax lots, named by the street
centre line that runs through it (M5-T155, rulings Y2 c / Y6).

The drawings compute NO law (ruling Y6): a street area is simply the part of
the window that is NOT covered by a tax lot (the subject lot included), i.e. the
gaps in the tax map. Each gap is then labelled with the name of the street
centre line that runs through it, and with its mapped width only where the data
gives a plain number. A gap no centre line runs through is drawn unnamed. This
is drawn from the city tax map and the Digital City Map centre lines; nothing is
surveyed, and the caption says so.

Pure geometry (EPSG:2263 US survey feet) built on ``shapely`` (already pinned):
the window minus the union of the tax lots, slivers under a stated minimum area
dropped, each remaining piece carrying the street runs that cross it. Output is
sorted deterministically so the same input gives byte-identical drawings (S8).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from shapely import make_valid
from shapely.geometry import LineString, MultiLineString, box
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from .model import Line, Point, Polygon, StreetLine

__all__ = [
    "MIN_RUN_LENGTH_FT",
    "MIN_STREET_AREA_SQFT",
    "StreetArea",
    "StreetRun",
    "clip_polygon_to_rect",
    "clip_polyline_to_rect",
    "clip_street",
    "gaps_in_rect",
    "street_areas",
]

# A gap smaller than this (square feet) is a sliver of the tax map - a rounding
# gap between two abutting lots, not a street - and is dropped (S1).
MIN_STREET_AREA_SQFT = 40.0
# A centre line must run at least this far through a gap to name it, so a line
# that merely clips a corner of a gap does not label the whole area (S1).
MIN_RUN_LENGTH_FT = 10.0


@dataclass(frozen=True)
class StreetRun:
    """One street centre line clipped to a single street area - what names it.

    ``path`` is the longest clipped piece of the centre line inside the area
    (for placing the name along the street); ``length_ft`` is the total clipped
    length. Every printed value (name, mapped width) keeps its document source.
    """

    name: str
    name_source: str
    width_text: str | None
    width_source: str | None
    mapped_width_ft: float | None
    mapped_width_source: str | None
    path: Line
    length_ft: float
    source: str


@dataclass(frozen=True)
class StreetArea:
    """One gap between the tax lots inside the window - a street area.

    ``runs`` are the street centre lines that run through it (sorted by name);
    an area no centre line runs through has an empty ``runs`` and is drawn
    unnamed. ``outline`` is the gap polygon (exterior ring first, then holes),
    EPSG:2263 US survey feet. ``source`` traces the gap to the tax-lot layer it
    was carved from (the gaps are DERIVED, never a printed value)."""

    outline: Polygon
    runs: tuple[StreetRun, ...]
    source: str


def _shapely_polygon(polygon: Polygon) -> ShapelyPolygon:
    exterior = list(polygon.exterior)
    holes = [list(ring) for ring in polygon.holes]
    return ShapelyPolygon(exterior, holes)


def _model_polygon(geom: ShapelyPolygon, source: str) -> Polygon:
    rings: list[tuple[Point, ...]] = [tuple((float(x), float(y)) for x, y in geom.exterior.coords)]
    rings += [tuple((float(x), float(y)) for x, y in ring.coords) for ring in geom.interiors]
    return Polygon(rings=tuple(rings), source=source)


def _polygon_pieces(geom: BaseGeometry) -> list[ShapelyPolygon]:
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    if geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        return [g for g in geom.geoms if g.geom_type == "Polygon" and not g.is_empty]
    return []


def _line_strings(street: StreetLine) -> list[LineString]:
    return [LineString([tuple(p) for p in path]) for path in street.paths if len(path) >= 2]


def _longest_line_coords(geom: BaseGeometry) -> tuple[Line, float]:
    """The longest LineString piece of ``geom`` (its coords and the TOTAL length
    of every line piece) - the total is used to decide whether a street runs far
    enough through a gap to name it, the longest piece to place the label."""
    parts: list[LineString] = []
    if geom.is_empty:
        return (), 0.0
    if geom.geom_type == "LineString":
        parts = [geom]
    elif geom.geom_type in ("MultiLineString", "GeometryCollection"):
        parts = [g for g in geom.geoms if g.geom_type == "LineString" and not g.is_empty]
    if not parts:
        return (), 0.0
    total = float(sum(p.length for p in parts))
    longest = max(parts, key=lambda p: p.length)
    coords: Line = tuple((float(x), float(y)) for x, y in longest.coords)
    return coords, total


def _runs_through(
    piece: ShapelyPolygon, streets: Iterable[StreetLine], min_run_ft: float
) -> tuple[StreetRun, ...]:
    runs: list[StreetRun] = []
    for street in streets:
        lines = _line_strings(street)
        if not lines:
            continue
        clipped = MultiLineString(lines).intersection(piece)
        coords, length = _longest_line_coords(clipped)
        if length < min_run_ft or len(coords) < 2:
            continue
        runs.append(
            StreetRun(
                name=street.name,
                name_source=street.name_source,
                width_text=street.width_text,
                width_source=street.width_source,
                mapped_width_ft=street.mapped_width_ft,
                mapped_width_source=street.mapped_width_source,
                path=coords,
                length_ft=length,
                source=street.source,
            )
        )
    # Deterministic order: by street name, then by the longer run first.
    runs.sort(key=lambda r: (r.name, -round(r.length_ft, 3)))
    return tuple(runs)


def street_areas(
    window: tuple[float, float, float, float],
    lots: Iterable[Polygon],
    streets: Iterable[StreetLine],
    *,
    min_area_sqft: float = MIN_STREET_AREA_SQFT,
    min_run_ft: float = MIN_RUN_LENGTH_FT,
    source: str = "/map_context/tax_lots",
) -> tuple[StreetArea, ...]:
    """The street areas inside ``window`` (xmin, ymin, xmax, ymax).

    The window minus the union of every tax lot (the subject lot included), with
    slivers under ``min_area_sqft`` dropped; each remaining gap carries the
    street runs that cross it for at least ``min_run_ft``. Every lot is clipped
    to the window first, so a lot that only reaches into the window still carves
    its part out (the mutation test proves a gap never overlaps a lot).
    """
    win = box(*window)
    lot_geoms = []
    for lot in lots:
        geom = make_valid(_shapely_polygon(lot))
        clipped = geom.intersection(win)
        if not clipped.is_empty:
            lot_geoms.append(clipped)
    covered = unary_union(lot_geoms) if lot_geoms else None
    gap = win.difference(covered) if covered is not None else win
    streets = list(streets)
    areas: list[StreetArea] = []
    for i, piece in enumerate(_polygon_pieces(gap)):
        if piece.area < min_area_sqft:
            continue
        areas.append(
            StreetArea(
                outline=_model_polygon(piece, f"{source}#gap-{i}"),
                runs=_runs_through(piece, streets, min_run_ft),
                source=source,
            )
        )
    # Deterministic order: by the piece's lower-left corner, then larger first.
    areas.sort(key=lambda a: _sort_key(a.outline))
    return tuple(areas)


def clip_street(
    street: StreetLine, window: tuple[float, float, float, float]
) -> list[Line]:
    """The street's centre-line polylines clipped to ``window`` (for the block
    and neighbourhood maps, which draw the street NETWORK rather than the areas).
    Returns the in-window pieces, ordered deterministically."""
    win = box(*window)
    out: list[Line] = []
    for path in street.paths:
        if len(path) < 2:
            continue
        clipped = LineString([tuple(p) for p in path]).intersection(win)
        if clipped.is_empty:
            continue
        if clipped.geom_type == "LineString":
            geoms = [clipped]
        elif clipped.geom_type in ("MultiLineString", "GeometryCollection"):
            geoms = [g for g in clipped.geoms if g.geom_type == "LineString"]
        else:
            geoms = []
        for g in geoms:
            if not g.is_empty and g.length > 0.0:
                out.append(tuple((float(x), float(y)) for x, y in g.coords))
    out.sort(key=lambda c: (round(c[0][0], 3), round(c[0][1], 3)))
    return out


Rings = list[tuple[Point, ...]]
Rect = tuple[float, float, float, float]


def _rings_of(geom: ShapelyPolygon) -> Rings:
    rings: Rings = [tuple((float(x), float(y)) for x, y in geom.exterior.coords)]
    rings += [tuple((float(x), float(y)) for x, y in r.coords) for r in geom.interiors]
    return rings


def clip_polygon_to_rect(rings: Rings, rect: Rect) -> list[Rings]:
    """Clip a polygon (exterior ring first, then holes) to the axis-aligned
    ``rect`` (x0, y0, x1, y1). Returns a list of polygons (each a list of rings),
    EMPTY if nothing is inside - so lots and buildings are cut at the drawing
    frame, never floating past it. Coordinate-agnostic (world OR screen)."""
    poly = make_valid(ShapelyPolygon(rings[0], list(rings[1:])))
    clipped = poly.intersection(box(*rect))
    return [_rings_of(p) for p in _polygon_pieces(clipped)]


def gaps_in_rect(rect: Rect, lot_rings: Iterable[Rings], min_area: float) -> list[Rings]:
    """The street space inside ``rect``: the rectangle minus the union of the lot
    polygons (each clipped to the rect), pieces under ``min_area`` (in the
    coordinate units squared) dropped. Even coverage over the WHOLE viewport, so
    the street hatching is continuous. Deterministically ordered."""
    frame = box(*rect)
    covered = []
    for rings in lot_rings:
        piece = make_valid(ShapelyPolygon(rings[0], list(rings[1:]))).intersection(frame)
        if not piece.is_empty:
            covered.append(piece)
    union = unary_union(covered) if covered else None
    gap = frame.difference(union) if union is not None else frame
    out = [_rings_of(p) for p in _polygon_pieces(gap) if p.area >= min_area]
    out.sort(key=lambda rings: (round(min(p[0] for p in rings[0]), 3),
                                round(min(p[1] for p in rings[0]), 3)))
    return out


def clip_polyline_to_rect(polyline: Iterable[Point], rect: Rect) -> list[Line]:
    """Clip a polyline to ``rect``; returns the in-rect pieces, ordered."""
    line = LineString([tuple(p) for p in polyline])
    clipped = line.intersection(box(*rect))
    if clipped.is_empty:
        return []
    if clipped.geom_type == "LineString":
        geoms = [clipped]
    elif clipped.geom_type in ("MultiLineString", "GeometryCollection"):
        geoms = [g for g in clipped.geoms if g.geom_type == "LineString"]
    else:
        geoms = []
    out = [tuple((float(x), float(y)) for x, y in g.coords) for g in geoms if g.length > 0.0]
    out.sort(key=lambda c: (round(c[0][0], 3), round(c[0][1], 3)))
    return out


def _sort_key(polygon: Polygon) -> tuple[float, float, float]:
    xs = [p[0] for ring in polygon.rings for p in ring]
    ys = [p[1] for ring in polygon.rings for p in ring]
    span_x = max(xs) - min(xs)
    span_y = max(ys) - min(ys)
    return (round(min(xs), 3), round(min(ys), 3), -round(span_x * span_y, 3))
