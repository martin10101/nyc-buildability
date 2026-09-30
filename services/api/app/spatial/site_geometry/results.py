"""Result records for single-lot site geometry (queue item B-03).

Every measurement is a :class:`~.labels.SourcedValue` carrying its plan §4 label. Unknown
stays unknown: ``value`` is None and ``reason`` says why.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .labels import SourcedValue

__all__ = [
    "EDGE_FRONTS",
    "EDGE_NO_STREET",
    "EDGE_UNCERTAIN",
    "FRONTAGE_CONFIRMED",
    "FRONTAGE_UNCERTAIN",
    "LOT_TYPE_CORNER",
    "LOT_TYPE_INTERIOR",
    "LOT_TYPE_THROUGH",
    "LOT_TYPE_UNKNOWN",
    "RELATION_CORNER",
    "RELATION_THROUGH",
    "RELATION_UNCLEAR",
    "STATUS_COMPLETE",
    "STATUS_PARTIAL",
    "STATUS_REFUSED",
    "AreaCheck",
    "CityRecordValues",
    "DepthProfile",
    "EdgeFinding",
    "LotType",
    "SiteGeometry",
    "StreetFrontage",
    "StreetRelation",
]

EDGE_FRONTS = "fronts"
EDGE_NO_STREET = "no_street"
EDGE_UNCERTAIN = "uncertain"

FRONTAGE_CONFIRMED = "confirmed"
FRONTAGE_UNCERTAIN = "uncertain"

LOT_TYPE_CORNER = "corner"
LOT_TYPE_INTERIOR = "interior"
LOT_TYPE_THROUGH = "through"
LOT_TYPE_UNKNOWN = "unknown"

RELATION_CORNER = "corner"
RELATION_THROUGH = "through"
RELATION_UNCLEAR = "unclear"

STATUS_COMPLETE = "complete"
STATUS_PARTIAL = "partial"
STATUS_REFUSED = "refused"


@dataclass(frozen=True)
class EdgeFinding:
    """What lies straight outside one outline edge.

    ``fronts``: every sample looks onto the same street's street line. ``no_street``: no
    street line lies outside it. ``uncertain``: anything else; ``reasons`` says what.
    """

    index: int
    length_ft: float
    verdict: str
    street_key: str | None
    candidate_streets: tuple[str, ...]
    reasons: tuple[str, ...]
    matched_share: float
    max_street_line_gap_ft: float | None
    segment_object_ids: tuple[int, ...] = ()
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class DepthProfile:
    """Lot depth measured straight back from one street's frontage."""

    street_key: str
    minimum: SourcedValue
    mean: SourcedValue
    maximum: SourcedValue


@dataclass(frozen=True)
class StreetFrontage:
    street_key: str
    street_name: str
    status: str
    length: SourcedValue
    edge_indices: tuple[int, ...]
    segment_object_ids: tuple[int, ...]
    mapped_width_raw: tuple[str, ...]
    max_street_line_gap_ft: float | None
    depth: DepthProfile | None = None


@dataclass(frozen=True)
class StreetRelation:
    first: str
    second: str
    relation: str
    angle_deg: float | None
    reason: str


@dataclass(frozen=True)
class LotType:
    """Geometric lot type from the outline: corner / interior / through / unknown.

    This is a stated geometric test (see ``lot_type.py``), not a Zoning Resolution
    determination; ``basis`` records the test. For an unknown, ``reason`` explains it in plain
    words and ``reason_code`` names it (``lot_type.REASON_*``). ``unconfirmed_lot_lines``
    lists uncertain lot lines (0-based edge indices) that did not change a known type.
    """

    kind: str
    label: str
    basis: str
    reason: str | None
    streets: tuple[str, ...]
    relations: tuple[StreetRelation, ...] = ()
    reason_code: str | None = None
    unconfirmed_lot_lines: tuple[int, ...] = ()


@dataclass(frozen=True)
class AreaCheck:
    """Outline area against the recorded lot area. Reported, never reconciled."""

    outline_sq_ft: float
    city_records_sq_ft: float
    difference_sq_ft: float
    difference_pct: float
    statement: str


@dataclass(frozen=True)
class CityRecordValues:
    lot_area: SourcedValue
    lot_front: SourcedValue
    lot_depth: SourcedValue


@dataclass(frozen=True)
class SiteGeometry:
    status: str
    refusal_reason: str | None
    lot_area: SourcedValue
    city_records: CityRecordValues
    area_check: AreaCheck | None
    frontages: tuple[StreetFrontage, ...]
    lot_type: LotType
    lot_depth: SourcedValue
    edges: tuple[EdgeFinding, ...]
    street_crossings: tuple[str, ...]
    notes: tuple[str, ...]
    parameters: Mapping[str, object] = field(default_factory=dict)
    provenance: Mapping[str, object] = field(default_factory=dict)

    def frontage(self, street_key: str) -> StreetFrontage | None:
        for frontage in self.frontages:
            if frontage.street_key == street_key:
                return frontage
        return None
