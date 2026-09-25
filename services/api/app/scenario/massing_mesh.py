"""Massing prism mesh construction (M5-T112 split of :mod:`app.scenario.massing_model`).

One responsibility: turn a prepared CCW ring plus its cap triangulation into a single
closed, outward-oriented triangulated prism between two elevations - a bottom cap, a top
cap and one outward-wound side quad per ring edge - with a per-floor plate area (from the
authoritative 2263 ring via shapely) and a well-conditioned signed volume (reduced in
LOCAL coordinates so it stays accurate at NYC magnitudes). Consistent winding gives a
positive signed volume and every directed edge appears exactly once (section 4 / the
section-10 mesh gate).

Imported by the :mod:`app.scenario.massing_model` facade; it imports the coordinate
quantiser from :mod:`app.scenario.massing_triangulation`, the shared point type from
:mod:`app.scenario.massing_guards`, and the already-admitted ``numpy`` / ``shapely``. No
route, no web, no new dependency.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from shapely.geometry import Polygon

from .massing_guards import _Point
from .massing_triangulation import _QUANT_DECIMALS, _q

__all__ = ["_PrismMesh", "_build_prism"]


@dataclass(frozen=True)
class _PrismMesh:
    floor_index: int
    level_index: int
    z_bottom_ft: float
    z_top_ft: float
    vertices: tuple[tuple[float, float, float], ...]
    triangles: tuple[tuple[int, int, int], ...]
    plate_area_sq_ft: float
    signed_volume_cu_ft: float

    def as_dict(self) -> dict:
        return {
            "floor_index": self.floor_index,
            "level_index": self.level_index,
            "z_bottom_ft": self.z_bottom_ft,
            "z_top_ft": self.z_top_ft,
            "vertices": [list(v) for v in self.vertices],
            "triangles": [list(t) for t in self.triangles],
            "plate_area_sq_ft": self.plate_area_sq_ft,
            "signed_volume_cu_ft": self.signed_volume_cu_ft,
        }


def _build_prism(
    ring: Sequence[_Point],
    cap: Sequence[tuple[int, int, int]],
    z_bottom: float,
    z_top: float,
    floor_index: int,
    level_index: int,
    local_origin: _Point,
) -> _PrismMesh:
    """A single closed, outward-oriented prism over ``ring`` between two elevations.

    Bottom + top caps (top from the CCW ``cap`` triangulation, bottom reversed) and
    one outward-wound side quad per ring edge. Vertices are stored in authoritative
    world 2263 coordinates; the signed volume is reduced in LOCAL coordinates (origin
    subtracted) so the closed-mesh volume is well conditioned at NYC magnitudes."""
    n = len(ring)
    zb, zt = _q(z_bottom), _q(z_top)
    verts: list[tuple[float, float, float]] = [(x, y, zb) for x, y in ring]  # 0..n-1
    verts += [(x, y, zt) for x, y in ring]  # n..2n-1
    tris: list[tuple[int, int, int]] = []
    # Top cap: CCW from above -> +z outward normal.
    for a, b, c in cap:
        tris.append((a + n, b + n, c + n))
    # Bottom cap: reversed -> -z outward normal.
    for a, b, c in cap:
        tris.append((a, c, b))
    # Side walls: for CCW ring edge i->j, outward-wound quad (bi,bj,tj)+(bi,tj,ti).
    for i in range(n):
        j = (i + 1) % n
        bi, bj = i, j
        ti, tj = i + n, j + n
        tris.append((bi, bj, tj))
        tris.append((bi, tj, ti))

    ox, oy = local_origin
    local = np.array(
        [[vx - ox, vy - oy, vz] for vx, vy, vz in verts], dtype=np.float64
    )
    idx = np.array(tris, dtype=np.int64)
    v0 = local[idx[:, 0]]
    v1 = local[idx[:, 1]]
    v2 = local[idx[:, 2]]
    signed_volume = float(np.sum(np.einsum("ij,ij->i", v0, np.cross(v1, v2))) / 6.0)

    plate_area = float(Polygon([(x, y) for x, y in ring]).area)
    return _PrismMesh(
        floor_index=floor_index,
        level_index=level_index,
        z_bottom_ft=zb,
        z_top_ft=zt,
        vertices=tuple(verts),
        triangles=tuple(tris),
        plate_area_sq_ft=round(plate_area, _QUANT_DECIMALS),
        signed_volume_cu_ft=round(signed_volume, _QUANT_DECIMALS),
    )
