"""Check C-4 on the drawn geometry: what the SVG DRAWS must match the numbers it
PRINTS (plate areas, yard depths), measured back from the SVG itself.

Independent of the kit's own code: shapes are re-read from the SVG path data
and converted back to feet with the drawing's scale (the scale bar for the site
plan; the vertical extrusion of each side face for the massing).
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

from .kit_support import SVG_NS, numbers_in, parse, resolve

_POINT = re.compile(r"[ML](-?[\d.]+) (-?[\d.]+)")
COS30 = math.sqrt(3.0) / 2.0


def subpaths(d: str) -> list[list[tuple[float, float]]]:
    return [[(float(x), float(y)) for x, y in _POINT.findall(part)]
            for part in d.split("Z") if _POINT.search(part)]


def _area(points) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(points, points[1:] + points[:1], strict=True))) / 2.0


def path_area(d: str) -> float:
    """Exterior minus holes (first sub-path is the exterior)."""
    rings = subpaths(d)
    return _area(rings[0]) - sum(_area(r) for r in rings[1:])


def _perimeter(d: str) -> float:
    return sum(math.dist(a, b) for r in subpaths(d) for a, b in zip(r, r[1:] + r[:1], strict=True))


def _base_paths(root: ET.Element) -> list[ET.Element]:
    return [p for p in root.iter(f"{SVG_NS}path") if not p.get("fill", "").startswith("url(")]


def _scale(root: ET.Element) -> float:
    bar = next(g for g in root.iter(f"{SVG_NS}g") if g.get("data-role") == "scale-bar")
    return float(bar.get("data-px-per-ft"))


def site_plan_problems(svg: str, doc: dict) -> list[str]:
    """Footprint areas equal the plates' gross_sf; each printed yard depth equals
    how far the drawn yard reaches from a drawn lot line it runs along."""
    root = parse(svg)
    k = _scale(root)
    problems = []
    paths = _base_paths(root)
    for path in (p for p in paths if p.get("data-floor")):
        gross = resolve(doc, path.get("data-source"))["gross_sf"]
        drawn = path_area(path.get("d")) / k ** 2
        tol = max(1.0, 0.001 * gross) + _perimeter(path.get("d")) * 0.01 / k ** 2
        if abs(drawn - gross) > tol:
            problems.append(f"footprint {path.get('data-source')}: drawn {drawn:.2f} vs {gross}")
    lot = next(p for p in paths if p.get("data-source") == "/geometry/lot_outline")
    lot_ring = subpaths(lot.get("d"))[0]
    depth_texts = {el.get("data-source"): el.text for el in root.iter(f"{SVG_NS}text")
                   if el.get("data-role") == "yard_depth"}
    for path in (p for p in paths if (p.get("data-source") or "").startswith("/geometry/yards")):
        printed = numbers_in(depth_texts[path.get("data-source") + "/depth_ft"])[0]
        yard = subpaths(path.get("d"))[0]
        reaches = [max(_line_distance(p, a, b) for p in yard) / k
                   for a, b in zip(lot_ring, lot_ring[1:] + lot_ring[:1], strict=True)
                   if _runs_along(yard, a, b)]
        if not any(abs(reach - printed) <= 0.02 / k + 0.01 for reach in reaches):
            problems.append(f"yard {path.get('data-source')}: prints {printed}, reaches {reaches}")
    return problems


def _line_distance(p, a, b) -> float:
    return abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / math.dist(a, b)


def _runs_along(ring, a, b, tol: float = 0.05) -> bool:
    """Some edge of ``ring`` lies on segment ab's line and overlaps it (px)."""
    length = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    for c, d in zip(ring, ring[1:] + ring[:1], strict=True):
        if max(_line_distance(c, a, b), _line_distance(d, a, b)) > tol:
            continue
        tc = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
        td = (d[0] - a[0]) * ux + (d[1] - a[1]) * uy
        if min(max(tc, td), length) - max(min(tc, td), 0.0) > tol:
            return True
    return False


def massing_problems(svg: str, doc: dict) -> list[str]:
    """Each printed floor area equals the drawn top faces of that floor and use,
    read back through the isometric area factor (cos 30 x scale squared), the
    scale taken from the side faces' vertical extrusion."""
    root = parse(svg)
    faces = [p for p in _base_paths(root) if p.get("data-face")]
    heights = {row["floor"]: row["height_ft"] for row in doc["floor_by_floor"]}
    k = None
    for face in (f for f in faces if f.get("data-face") == "side"):
        pts = subpaths(face.get("d"))[0]
        k = math.dist(pts[1], pts[2]) / heights[resolve(doc, face.get("data-plate"))["floor"]]
        break
    assert k is not None, "no side face to read the scale from"
    drawn: dict[tuple[int, str], float] = {}
    perimeter: dict[tuple[int, str], float] = {}
    for face in (f for f in faces if f.get("data-face") == "top"):
        plate = resolve(doc, face.get("data-plate"))
        key = (plate["floor"], plate["use"])
        drawn[key] = drawn.get(key, 0.0) + path_area(face.get("d")) / (COS30 * k ** 2)
        perimeter[key] = perimeter.get(key, 0.0) + _perimeter(face.get("d"))
    printed: dict[tuple[int, str], float] = {}
    for el in root.iter(f"{SVG_NS}text"):
        if el.get("data-role") == "floor_area":
            row = resolve(doc, el.get("data-source").rsplit("/", 1)[0])
            key = (row["floor"], row["use"])
            printed[key] = printed.get(key, 0.0) + numbers_in(el.text)[0]
    problems = []
    for key, value in printed.items():
        tol = max(1.0, 0.001 * value) + perimeter.get(key, 0.0) * 0.02 / (COS30 * k ** 2)
        if key not in drawn or abs(drawn[key] - value) > tol:
            problems.append(f"floor {key}: prints {value} sf, draws {drawn.get(key)}")
    return problems
