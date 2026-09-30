"""Which DCM segments a frontage's width may be read from (queue item B-04; review 265 F1).

THE RULE (stated). A frontage's mapped width is read from its segments, and D-052 frontage
coverage (R002: a correctly matched feature, every touching feature collected) is attested,
only when all three hold:

1. Identified - the frontage lists at least one segment (OBJECTID), and that list is exactly
   the set of segments its fronting lot lines matched sample by sample (the B-03
   ``EdgeFinding.segment_object_ids`` of ``frontage.edge_indices``). A list B-03 filled from
   segments of the same street NAME (its fallback when no matched sample had an OBJECTID) is
   a name-only match: no segment is read.
2. Covered - B-03 confirmed the frontage: every sample point along every fronting lot line
   lies on the street line of a center line of this street, and no other lot line may face it.
3. Nothing unidentified - no center line of this street in the street data lacks an
   OBJECTID, so every center line those samples matched is one of the listed segments.

Together: every sampled point of the frontage lies on the street line of a listed, identified
segment. If 2 or 3 fails the listed segments are still read for the record, but coverage is
not attested, so the D-052 policy issues no class and the frontage needs a street width.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.spatial.site_geometry.results import FRONTAGE_CONFIRMED, EdgeFinding, StreetFrontage

from .inputs import MappedStreetSegment

__all__ = ["FrontageSegments", "frontage_segments"]


@dataclass(frozen=True)
class FrontageSegments:
    """``read_ids``: the segments whose width is read (empty when rule 1 fails).
    ``coverage``: rules 1-3 all hold. ``problems``: plain reasons for each rule that fails."""

    read_ids: tuple[int, ...]
    coverage: bool
    problems: tuple[str, ...]


def _name(text: str | None) -> str:
    return " ".join((text or "").split())


def _same_street(segment: MappedStreetSegment, frontage: StreetFrontage) -> bool:
    """An unidentified segment counts against a frontage when it has this street's name, or
    no name at all (it could be any street)."""
    name = _name(segment.street_name)
    return not name or name in (_name(frontage.street_key), _name(frontage.street_name))


def _ids(ids: Iterable[int]) -> str:
    return ", ".join(str(i) for i in ids)


def frontage_segments(frontage: StreetFrontage, edges: Iterable[EdgeFinding],
                      unidentified: Iterable[MappedStreetSegment]) -> FrontageSegments:
    by_index = {edge.index: edge for edge in edges}
    listed = tuple(frontage.segment_object_ids)
    matched = {i for index in frontage.edge_indices
               for i in (by_index[index].segment_object_ids if index in by_index else ())}
    problems: list[str] = []
    if not listed:
        problems.append("No City Map street center line with a segment number (OBJECTID) was "
                        "matched to this frontage.")
    elif not matched or matched != set(listed):
        problems.append(f"City Map segment(s) {_ids(listed)} were matched to this frontage by "
                        "street name only, not along its lot lines, so their width is not "
                        "read.")
    identified = not problems
    if frontage.status != FRONTAGE_CONFIRMED:
        problems.append(f"The frontage on {frontage.street_name} is not confirmed: "
                        f"{frontage.length.reason or 'see the site geometry'}")
    same = [s for s in unidentified if _same_street(s, frontage)]
    if same:
        problems.append(f"The street data has {len(same)} City Map segment(s) of "
                        f"{frontage.street_name} (or unnamed) without a segment number "
                        "(OBJECTID), so the segments along this frontage cannot all be "
                        "identified.")
    return FrontageSegments(listed if identified else (), not problems, tuple(problems))
