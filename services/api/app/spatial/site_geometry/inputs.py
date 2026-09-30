"""Plain inputs for single-lot site geometry (queue item B-03).

The pure derivation reads only these records. ``adapters.py`` builds them from the
accepted connectors' results; tests build them directly. Every coordinate is EPSG:2263
(NAD83 / New York Long Island, US survey feet) - the measurement geometry. The EPSG:4326
display outline is never measured.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

__all__ = [
    "CityRecordLot",
    "LotOutline",
    "Point2",
    "StreetCenterline",
    "StreetData",
]

Point2 = tuple[float, float]


@dataclass(frozen=True)
class LotOutline:
    """One tax lot's outline: a single exterior ring (open or closed), no holes.

    ``crs`` must be the EPSG:2263 stamp (wkid 102718 / latest wkid 2263); anything else is
    refused before a coordinate is read. ``source`` names the dataset in plain words.
    """

    exterior: tuple[Point2, ...]
    crs: Mapping[str, object]
    source: str
    provenance: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StreetCenterline:
    """One DCM street center-line feature.

    ``street_key`` groups features of the same street (normalized name). ``mapped_width_raw``
    is the DCM ``Streetwidth`` text, passed through; only a plain single number is used here
    to place the street line. ``status_ok`` is False for anything other than a plain mapped
    street (the adapter decides; ``status_note`` says why), which makes a match uncertain.
    """

    street_key: str
    street_name: str | None
    object_id: int | None
    paths: tuple[tuple[Point2, ...], ...]
    mapped_width_raw: str | None
    status_ok: bool
    status_note: str | None = None


@dataclass(frozen=True)
class StreetData:
    """Every street center line inside ``covered_envelope`` (xmin, ymin, xmax, ymax).

    The envelope must cover the lot's bounds plus the search radius, otherwise a street
    could be missing and lot type stays unknown. ``incomplete_reasons`` lists anything that
    makes the set incomplete (a transfer-limited page, a feature with unusable geometry).
    """

    centerlines: tuple[StreetCenterline, ...]
    covered_envelope: tuple[float, float, float, float] | None
    crs: Mapping[str, object]
    source: str
    incomplete_reasons: tuple[str, ...] = ()
    provenance: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CityRecordLot:
    """City-recorded lot dimensions (PLUTO). ``None`` = not recorded (never 0)."""

    lot_area_sq_ft: float | None
    lot_front_ft: float | None
    lot_depth_ft: float | None
    source: str
    provenance: Mapping[str, object] = field(default_factory=dict)
