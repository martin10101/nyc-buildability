"""Lot depth from a street frontage (queue item B-03, plan M1-13 "depth").

Depth from street S is measured straight back into the lot, perpendicular to S's frontage
(the length-weighted mean direction of its frontage edges), from evenly spaced points on
those edges to the first lot line behind them - counted only when that line is a rear lot
line (within ``REAR_LINE_MAX_ANGLE_DEG`` of the frontage). The shortest, average and longest
are reported; for a rectangle they are equal. Depth stays unknown when the frontage bends
(``SINGLE_STREET_MAX_BEND_DEG``) or too few points reach a rear lot line.
"""

from __future__ import annotations

from .labels import tax_map_value, unknown_value
from .outline import OutlineEdge, PreparedOutline
from .parameters import (
    DEPTH_MIN_SAMPLE_SHARE,
    REAR_LINE_MAX_ANGLE_DEG,
    SINGLE_STREET_MAX_BEND_DEG,
)
from .rays import line_angle_deg, ray_segment_distance, sample_points, unit, vector_angle_deg
from .results import DepthProfile

__all__ = ["frontage_bend_deg", "mean_outward_normal", "measure_depth"]

_REACH_FT = 1_000_000.0  # beyond any lot; the ray stops at the first lot line anyway


def mean_outward_normal(edges: list[OutlineEdge]):
    sx = sum(edge.outward_normal[0] * edge.length_ft for edge in edges)
    sy = sum(edge.outward_normal[1] * edge.length_ft for edge in edges)
    return unit((sx, sy))


def frontage_bend_deg(edges: list[OutlineEdge]) -> float:
    """Largest angle between the outward directions of any two frontage edges on one street
    (0 for one edge; 180 when the same street name faces opposite sides of the lot)."""
    worst = 0.0
    for i, first in enumerate(edges):
        for second in edges[i + 1:]:
            worst = max(worst, vector_angle_deg(first.outward_normal, second.outward_normal))
    return worst


def _first_line_behind(origin, inward, source: OutlineEdge, outline: PreparedOutline):
    best_t, best_edge = None, None
    for other in outline.edges:
        if other.index == source.index:
            continue
        t = ray_segment_distance(origin, inward, other.start, other.end, _REACH_FT)
        if t is not None and (best_t is None or t < best_t):
            best_t, best_edge = t, other
    return best_t, best_edge


def _unknown_profile(street_key: str, reason: str, basis: str) -> DepthProfile:
    missing = unknown_value("ft", reason, basis)
    return DepthProfile(street_key, missing, missing, missing)


def measure_depth(
    street_key: str, street_name: str, edges: list[OutlineEdge], outline: PreparedOutline,
    source: str,
) -> DepthProfile:
    """Depth profile from one street's confirmed frontage edges."""
    basis = (
        f"Measured on the {source} outline straight back from the {street_name} frontage "
        "to the rear lot line"
    )
    bend = frontage_bend_deg(edges)
    normal = mean_outward_normal(edges)
    if bend > SINGLE_STREET_MAX_BEND_DEG or normal is None:
        return _unknown_profile(street_key, (
            f"The frontage on {street_name} is not straight (its lot lines turn by "
            f"{bend:.0f} degrees), so there is no single direction to measure depth in."),
            basis)
    inward = (-normal[0], -normal[1])
    frontage_direction = (-normal[1], normal[0])
    depths: list[tuple[float, float]] = []
    total_weight = 0.0
    for edge in edges:
        for point, weight in sample_points(edge):
            total_weight += weight
            depth, line = _first_line_behind(point, inward, edge, outline)
            if depth is None or line is None:
                continue
            if line_angle_deg(line.direction, frontage_direction) <= REAR_LINE_MAX_ANGLE_DEG:
                depths.append((depth, weight))
    counted = sum(weight for _, weight in depths)
    if not depths or counted < DEPTH_MIN_SAMPLE_SHARE * total_weight:
        return _unknown_profile(street_key, (
            f"Straight back from the {street_name} frontage there is no clear rear lot line."),
            basis)
    mean = sum(depth * weight for depth, weight in depths) / counted
    values = [depth for depth, _ in depths]
    return DepthProfile(
        street_key,
        tax_map_value(min(values), "ft", basis + " (shortest)"),
        tax_map_value(mean, "ft", basis + " (average)"),
        tax_map_value(max(values), "ft", basis + " (longest)"),
    )
