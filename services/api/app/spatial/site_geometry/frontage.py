"""Frontage per street along the outline's outside edges (queue item B-03, plan §4).

A street's frontage is the total length of the outline edges that front it. It is stated
only when it is certain: no edge that might face that street is uncertain, the street data
is complete, and the street does not run through the lot. Otherwise the length is unknown
and the reason says how much is already confirmed.
"""

from __future__ import annotations

from .depth import measure_depth
from .inputs import StreetCenterline
from .labels import tax_map_value, unknown_value
from .outline import PreparedOutline
from .results import (
    EDGE_UNCERTAIN,
    FRONTAGE_CONFIRMED,
    FRONTAGE_UNCERTAIN,
    EdgeFinding,
    StreetFrontage,
)

__all__ = ["build_frontages"]


def _doubt(key, findings, incomplete, crossing_keys) -> str | None:
    if key in crossing_keys:
        return "this street's center line runs through the lot"
    lines = [str(f.index + 1) for f in findings
             if f.verdict == EDGE_UNCERTAIN and key in f.candidate_streets]
    if lines:
        return "lot line(s) " + ", ".join(lines) + " may also face it"
    if incomplete:
        return "the street data is incomplete (" + " ".join(incomplete) + ")"
    return None


def build_frontages(
    findings: tuple[EdgeFinding, ...],
    outline: PreparedOutline,
    centerlines: tuple[StreetCenterline, ...],
    incomplete: tuple[str, ...],
    crossing_keys: tuple[str, ...],
    source: str,
) -> tuple[StreetFrontage, ...]:
    keys = {f.street_key for f in findings if f.street_key is not None}
    keys |= {k for f in findings if f.verdict == EDGE_UNCERTAIN for k in f.candidate_streets}
    keys |= set(crossing_keys)
    frontages = []
    for key in sorted(keys):
        same_street = [c for c in centerlines if c.street_key == key]
        name = next((c.street_name for c in same_street if c.street_name), key)
        edges = [f for f in findings if f.street_key == key]
        ids = sorted({i for f in edges for i in f.segment_object_ids})
        if not ids:
            ids = sorted({c.object_id for c in same_street if c.object_id is not None})
        widths = tuple(sorted({c.mapped_width_raw for c in same_street
                               if c.object_id in ids and c.mapped_width_raw is not None}))
        gaps = [f.max_street_line_gap_ft for f in edges if f.max_street_line_gap_ft is not None]
        confirmed = sum(outline.edges[f.index].length_ft for f in edges)
        basis = (f"Sum of the {source} outline edges that lie on the {name} street line "
                 "(City Map center line and mapped width)")
        doubt = _doubt(key, findings, incomplete, crossing_keys)
        if doubt is None and edges:
            length = tax_map_value(confirmed, "ft", basis)
            depth = measure_depth(key, name, [outline.edges[f.index] for f in edges],
                                  outline, source)
            status = FRONTAGE_CONFIRMED
        else:
            known = f"{confirmed:.2f} ft is confirmed, but " if edges else "Possible frontage: "
            length = unknown_value("ft", known + (doubt or "no edge fronts it") + ".", basis)
            depth, status = None, FRONTAGE_UNCERTAIN
        frontages.append(StreetFrontage(
            key, name, status, length, tuple(f.index for f in edges), tuple(ids), widths,
            max(gaps) if gaps else None, depth))
    return tuple(frontages)
