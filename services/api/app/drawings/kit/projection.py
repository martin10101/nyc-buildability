"""Isometric projection and painter's ordering for the axonometric massing.

The viewer looks from the south-west and above (plan x = grid east, y = grid
north, z up). Each floor plate becomes a prism from the floor's bottom to its
top elevation, taken from the floor-by-floor heights. Painter's order:

* floors bottom to top - floors occupy separate height bands, so a higher
  floor is always nearer the viewer along any shared line of sight;
* within a floor, the side faces that face the viewer (back faces culled),
  farthest first, then the top faces (a top is above every side of its band).

Faces are shaded by direction: tops lightest, sides darker by how far they
turn from the light.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from . import geometry as geo
from .model import FloorPlate, FloorRow

__all__ = [
    "SIDE",
    "TOP",
    "Face",
    "floor_faces",
    "floor_levels",
    "project",
    "side_darkening",
]

SIDE, TOP = "side", "top"
_COS30 = math.sqrt(3.0) / 2.0
_TOWARD_VIEWER = (-math.sqrt(0.5), -math.sqrt(0.5))
_LIGHT = (-0.8, -0.6)  # plan direction the light comes from (unit vector)
TOP_LIGHTENING = 0.45


@dataclass(frozen=True)
class Face:
    floor: int
    plate: FloorPlate
    face: str  # SIDE or TOP
    rings: tuple[tuple[tuple[float, float, float], ...], ...]  # 3-D points, feet
    darkening: float  # SIDE: amount mixed toward black; TOP: 0 (lightened instead)


def project(x: float, y: float, z: float) -> tuple[float, float]:
    """Isometric screen coordinates (X right, Y up), in feet."""
    return (x - y) * _COS30, (x + y) * 0.5 + z


def floor_levels(rows: Sequence[FloorRow]) -> dict[int, tuple[float, float]]:
    """(bottom, top) elevation of each floor: floors 1.. stack up from grade 0,
    floors 0, -1, ... stack down from it."""
    heights = {row.floor: row.height_ft for row in rows}
    levels: dict[int, tuple[float, float]] = {}
    z = 0.0
    for floor in sorted(f for f in heights if f >= 1):
        levels[floor] = (z, z + heights[floor])
        z += heights[floor]
    z = 0.0
    for floor in sorted((f for f in heights if f <= 0), reverse=True):
        levels[floor] = (z - heights[floor], z)
        z -= heights[floor]
    return levels


def side_darkening(normal: tuple[float, float]) -> float:
    lit = max(0.0, normal[0] * _LIGHT[0] + normal[1] * _LIGHT[1])
    return round(0.40 - 0.28 * lit, 4)


def _solid_normal(a, b, ring_area: float, is_hole: bool) -> tuple[float, float]:
    nx, ny = geo.outward_normal(a, b, ring_area)
    return (-nx, -ny) if is_hole else (nx, ny)


def floor_faces(
    floor: int,
    plates: Sequence[tuple[int, FloorPlate]],
    level: tuple[float, float],
    origin: tuple[float, float],
) -> list[Face]:
    """Visible faces of one floor's plates, in painter's order.

    ``plates`` pairs each plate with its index in the results (tie-breaker);
    ``origin`` is subtracted from plan coordinates.
    """
    z0, z1 = level
    ox, oy = origin
    sides: list[tuple[tuple, Face]] = []
    tops: list[Face] = []
    for index, plate in plates:
        local = [tuple((x - ox, y - oy) for x, y in ring) for ring in plate.outline.rings]
        for r, ring in enumerate(local):
            ring_area = geo.signed_area(ring)
            for e, (a, b) in enumerate(geo.edges(ring)):
                n = _solid_normal(a, b, ring_area, is_hole=r > 0)
                if n[0] * _TOWARD_VIEWER[0] + n[1] * _TOWARD_VIEWER[1] <= 1e-9:
                    continue  # faces away from the viewer, or edge-on
                quad = ((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1))
                depth = -((a[0] + b[0]) / 2.0 + (a[1] + b[1]) / 2.0)  # farther = more negative
                key = (round(depth, 9), index, r, e)
                sides.append((key, Face(floor, plate, SIDE, (quad,), side_darkening(n))))
        top_rings = tuple(tuple((x, y, z1) for x, y in ring) for ring in local)
        tops.append(Face(floor, plate, TOP, top_rings, 0.0))
    return [face for _, face in sorted(sides, key=lambda item: item[0])] + tops
