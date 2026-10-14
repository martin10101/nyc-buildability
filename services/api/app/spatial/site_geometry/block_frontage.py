"""Block-frontage measure between the two streets bounding a block (ZR 12-10 "short
dimension of a block"; the geometry input to the ZR 23-344(b) rear-yard check, task M5-T167).

Pure geometry over the single-lot DCM street window. Given the frontage street, the street
window around the lot and the lot's own location, it finds the two streets that bound the
block along that frontage - the cross-streets at the two ends of the frontage block face -
and measures the separation between them along the frontage direction, on the measurement
bases the geometry supports (the DCM centrelines give a ``derived`` separation). It INVENTS
no geometry: a window that fails, does not reach two bounding cross-streets on opposite
sides, or is ambiguous gives a not-known separation (D-051 honest absence; S15), never a
guessed one.

This module stays geometry-only and holds NO zoning number. It does NOT apply the 230-ft
threshold or decide whether ZR 23-344(b) applies; that is the scenario layer
(:mod:`app.scenario.three_answers.rear_yard_checks`), which also carries the UNRESOLVED
measurement-basis law (R6B reference case row ``b-measurement-basis``: the captured ZR 12-10
text does not fix whether the dimension is measured between street lines, centrelines or lot
lines). Every coordinate is EPSG:2263 (US survey feet)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from .inputs import Point2, StreetCenterline, StreetData

__all__ = [
    "BlockFrontageMeasure",
    "BoundingStreet",
    "measure_block_frontage",
    "street_mapped_width_ft",
]

# A cross-street bounds the block only when its centreline runs roughly across the frontage
# street - at least this many degrees off the frontage direction. 45 degrees mirrors the ZR
# 12-10 through-/rear-lot-line "within 45 degrees of being parallel" boundary.
_PERPENDICULAR_MIN_DEG = 45.0

# The basis of a separation measured from DCM mapped centrelines. One of the nine
# QUANTITY_BASES (results schema $defs.quantity_basis / tools/research_record_check.py).
BASIS_CENTRELINE = "derived"


@dataclass(frozen=True)
class BoundingStreet:
    """One of the two streets bounding the block along the frontage: its key, its display
    name and its single mapped width in feet (None when the DCM width is a range, 'Unknown'
    or absent - never guessed)."""

    street_key: str
    street_name: str
    width_ft: float | None
    width_raw: str | None


@dataclass(frozen=True)
class BlockFrontageMeasure:
    """The block-frontage separation between the two bounding cross-streets, per basis.

    ``separations`` maps a measurement basis (the nine QUANTITY_BASES) to the separation in
    feet on that basis; it is EMPTY when no basis could be measured (then the dimension is
    not known). ``bounding_streets`` names the two streets found (empty when two were not
    found). ``reason`` says, in plain words, what was measured or why it is not known. No
    basis value is ever a guess; a basis is present only when it was actually measured."""

    separations: dict[str, float] = field(default_factory=dict)
    bounding_streets: tuple[BoundingStreet, ...] = ()
    reason: str = ""

    @property
    def known(self) -> bool:
        return bool(self.separations) and len(self.bounding_streets) == 2


def street_mapped_width_ft(raw: str | None) -> float | None:
    """The DCM ``Streetwidth`` text as a single width in feet, or None when it is a range
    ('60-80'), 'Unknown', empty or not a plain number. A range or unknown width is never
    collapsed to one value (DB-260: no mapped street width adopted as settled)."""
    if raw is None:
        return None
    text = raw.strip()
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) and value > 0 else None


def _paths_vertices(paths: Sequence[Sequence[Point2]]) -> list[Point2]:
    return [(float(x), float(y)) for path in paths for (x, y) in path]


def _principal_direction(paths: Sequence[Sequence[Point2]]) -> tuple[float, float] | None:
    """The dominant direction of a street's centreline polylines as a unit vector: the
    vector between its two farthest vertices. None when it is degenerate."""
    verts = _paths_vertices(paths)
    if len(verts) < 2:
        return None
    best = 0.0
    vec = None
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            dx = verts[j][0] - verts[i][0]
            dy = verts[j][1] - verts[i][1]
            d2 = dx * dx + dy * dy
            if d2 > best:
                best = d2
                vec = (dx, dy)
    if vec is None or best <= 0:
        return None
    length = math.sqrt(best)
    return (vec[0] / length, vec[1] / length)


def _angle_between_deg(a: tuple[float, float], b: tuple[float, float]) -> float:
    """The unsigned angle (0-90 degrees) between two undirected lines."""
    dot = max(-1.0, min(1.0, abs(a[0] * b[0] + a[1] * b[1])))
    return math.degrees(math.acos(dot))


def _nearest_vertex_distance(paths: Sequence[Sequence[Point2]], pt: Point2) -> float | None:
    verts = _paths_vertices(paths)
    if not verts:
        return None
    return min(math.hypot(v[0] - pt[0], v[1] - pt[1]) for v in verts)


def _projection(paths: Sequence[Sequence[Point2]], pt: Point2,
                direction: tuple[float, float]) -> float | None:
    """The signed distance, along ``direction`` from ``pt``, to the street's nearest vertex:
    positive on one side of the lot, negative on the other."""
    verts = _paths_vertices(paths)
    if not verts:
        return None
    nearest = min(verts, key=lambda v: math.hypot(v[0] - pt[0], v[1] - pt[1]))
    return (nearest[0] - pt[0]) * direction[0] + (nearest[1] - pt[1]) * direction[1]


def measure_block_frontage(
    frontage_street_key: str,
    street_data: StreetData | None,
    *,
    lot_point: Point2 | None,
) -> BlockFrontageMeasure:
    """Measure the separation between the two streets bounding the block along the frontage
    street ``frontage_street_key``. Fail-closed: a missing window, a missing lot location, a
    frontage street with no usable centreline, or fewer than two bounding cross-streets on
    opposite sides gives a not-known measure (empty ``separations``), never a guess."""
    if street_data is None or lot_point is None:
        return BlockFrontageMeasure(reason="No street window or lot location was available.")
    frontage_paths = [
        c.paths for c in street_data.centerlines
        if c.street_key == frontage_street_key and c.paths
    ]
    frontage_direction = next(
        (d for paths in frontage_paths if (d := _principal_direction(paths)) is not None), None
    )
    if frontage_direction is None:
        return BlockFrontageMeasure(
            reason="The frontage street's centreline is not in the window, so the block's "
            "bounding cross-streets cannot be measured."
        )
    # Cross-streets: usable centrelines running roughly across the frontage (>= 45 degrees off
    # it), grouped by which side of the lot their nearest point falls on (signed projection).
    negative: list[tuple[float, StreetCenterline]] = []
    positive: list[tuple[float, StreetCenterline]] = []
    for c in street_data.centerlines:
        if c.street_key == frontage_street_key or not c.status_ok or not c.paths:
            continue
        direction = _principal_direction(c.paths)
        if direction is None or _angle_between_deg(direction, frontage_direction) < (
            _PERPENDICULAR_MIN_DEG
        ):
            continue
        projection = _projection(c.paths, lot_point, frontage_direction)
        if projection is None or projection == 0:
            continue
        (positive if projection > 0 else negative).append((projection, c))
    if not negative or not positive:
        return BlockFrontageMeasure(
            reason="The window does not reach a bounding cross-street on both sides of the "
            "lot along the frontage, so the block dimension is not known."
        )
    near_neg = min(negative, key=lambda item: abs(item[0]))
    near_pos = min(positive, key=lambda item: abs(item[0]))
    separation = abs(near_pos[0]) + abs(near_neg[0])
    streets = tuple(
        BoundingStreet(
            street_key=c.street_key,
            street_name=c.street_name or c.street_key,
            width_ft=street_mapped_width_ft(c.mapped_width_raw),
            width_raw=c.mapped_width_raw,
        )
        for _, c in (near_neg, near_pos)
    )
    return BlockFrontageMeasure(
        separations={BASIS_CENTRELINE: separation},
        bounding_streets=streets,
        reason=(
            f"Measured {separation:.2f} ft between the {streets[0].street_name} and "
            f"{streets[1].street_name} centrelines along the {frontage_street_key} frontage."
        ),
    )
