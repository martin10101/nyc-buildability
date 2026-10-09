"""Plain inputs for street width per frontage (queue item B-04, plan §4 "Street widths").

The pure derivation reads only these records. ``adapters.py`` builds them from the accepted
connectors' results (DCM street center-line geometry pages, PLUTO); tests build them
directly.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

__all__ = ["LotZoningContext", "MappedStreetSegment", "SegmentSource"]


@dataclass(frozen=True)
class SegmentSource:
    """Where one DCM segment's attributes came from.

    ``dataset_version`` is the layer's ``editingInfo.dataLastEditDate`` when the caller read
    the layer metadata, else None (never guessed). ``raw_digest`` is the sha256 of the query
    page body the segment was parsed from.
    """

    source: str
    source_id: str
    dataset: str
    dataset_version: str | None
    request_url: str | None
    retrieved_at: str | None
    raw_digest: str | None

    @property
    def documented(self) -> bool:
        """True when the retrieval is on record: source id, URL, time and body digest."""
        return all(isinstance(value, str) and value.strip() for value in (
            self.source_id, self.request_url, self.retrieved_at, self.raw_digest))


@dataclass(frozen=True)
class MappedStreetSegment:
    """One DCM street center-line segment as the width step needs it.

    ``object_id`` is None when the feature came back without an OBJECTID (schema drift): such
    a segment is kept so the coverage rule can see it, and its width is never read.
    ``mapped_width_raw`` is the DCM ``Streetwidth`` text exactly as served (the mapped width,
    usually property line to property line). ``plain_mapped_street`` is True only for a
    currently mapped street with no special City Map flag; ``status_note`` says why not.
    """

    object_id: int | None
    street_name: str | None
    borough: str | None
    mapped_width_raw: str | None
    plain_mapped_street: bool
    status_note: str | None
    source: SegmentSource


@dataclass(frozen=True)
class LotZoningContext:
    """The lot facts the ZR 12-10 exception check needs.

    ``zoning_districts`` lists every zoning district and commercial overlay recorded for the
    lot (empty = not known). ``community_district`` is the district number within the
    borough (for example 7 for Manhattan Community District 7) when a documented source
    gives it, else None - it is never decoded from an unverified field.
    """

    zoning_districts: tuple[str, ...]
    community_district: int | None
    source: str
    provenance: Mapping[str, object] = field(default_factory=dict)
