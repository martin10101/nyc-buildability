"""World-to-drawing frame for the location and zoning maps.

Maps show a neighbourhood, so - unlike the site plan's standard architectural
scale - the frame simply fits the drawn features (the subject lot plus the map's
city-data layer) into the plan region at the largest scale that fits, centred.
``y`` is flipped (world grid north is up; SVG y points down). The scale is
reported graphically by the scale bar, never as a ratio label.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.drawings.kit import geometry as geo

from .errors import MapInputError
from .model import Point, Polygon

__all__ = ["MapFrame", "fit"]


@dataclass(frozen=True)
class MapFrame:
    k: float  # drawing points per foot
    ox: float
    oy: float
    minx: float
    maxy: float

    def px(self, p: Point) -> Point:
        return self.ox + (p[0] - self.minx) * self.k, self.oy + (self.maxy - p[1]) * self.k


def fit(
    polygons: Iterable[Polygon], region: tuple[float, float, float, float], margin: float
) -> MapFrame:
    """Frame that fits every ring of ``polygons`` into ``region`` (x0,y0,x1,y1)
    with ``margin`` points of breathing room, at the largest uniform scale."""
    points = [p for polygon in polygons for ring in polygon.rings for p in ring]
    if not points:
        raise MapInputError("empty_extent", "no geometry to map", location="/map_context")
    minx, miny, maxx, maxy = geo.bbox(points)
    width, height = maxx - minx, maxy - miny
    if width <= 0.0 or height <= 0.0:
        raise MapInputError("empty_extent", "mapped geometry has no extent",
                            location="/map_context")
    x0, y0, x1, y1 = region
    k = min(((x1 - x0) - 2 * margin) / width, ((y1 - y0) - 2 * margin) / height)
    ox = x0 + ((x1 - x0) - width * k) / 2.0
    oy = y0 + ((y1 - y0) - height * k) / 2.0
    return MapFrame(k, ox, oy, minx, maxy)
