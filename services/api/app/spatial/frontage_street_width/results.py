"""Result records for street width per frontage (queue item B-04, plan §4 "Street widths").

A frontage's street class is ``wide`` or ``narrow`` only when the accepted D-052 policy
issues it. Anything else is ``needs_street_width``: the frontage carries the marker
"Needs street width", the reasons, and both classes as still possible, so a consumer shows
the wide-street and narrow-street results side by side. Unknown is never turned into narrow.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from app.connectors.dcm_street_width_classifier import WidthClassification
from app.connectors.dcm_street_width_policy import PolicyDecision
from app.spatial.site_geometry.labels import SourcedValue

from .exceptions import ExceptionCheck
from .inputs import MappedStreetSegment, SegmentSource

__all__ = [
    "CLASS_NARROW",
    "CLASS_NEEDS_STREET_WIDTH",
    "CLASS_WIDE",
    "MARKER_NEEDS_STREET_WIDTH",
    "STATUS_COMPLETE",
    "STATUS_NEEDS_STREET_WIDTH",
    "FrontageStreetWidth",
    "SegmentWidthReading",
    "SiteStreetWidths",
]

MARKER_NEEDS_STREET_WIDTH = "Needs street width"

CLASS_WIDE = "wide"
CLASS_NARROW = "narrow"
CLASS_NEEDS_STREET_WIDTH = "needs_street_width"

STATUS_COMPLETE = "complete"
STATUS_NEEDS_STREET_WIDTH = "needs_street_width"


@dataclass(frozen=True)
class SegmentWidthReading:
    """One DCM segment along the frontage: the accepted classifier's read of its mapped
    width, the ZR 12-10 named-street check, and the D-052 policy decision (which carries
    the provenance quintuple and the DRAFT label)."""

    segment: MappedStreetSegment
    classification: WidthClassification
    named_street: ExceptionCheck
    decision: PolicyDecision


@dataclass(frozen=True)
class FrontageStreetWidth:
    """The street width facts for one B-03 frontage.

    ``mapped_width`` is the single mapped width in feet (label "City records") when the
    frontage is confirmed and every segment along it states the same plain number;
    otherwise it is unknown with the reason. ``street_class`` / ``marker`` /
    ``possible_classes`` say which street-width results a consumer must show.
    """

    street_key: str
    street_name: str
    frontage_status: str
    street_class: str
    marker: str | None
    possible_classes: tuple[str, ...]
    mapped_width: SourcedValue
    readings: tuple[SegmentWidthReading, ...]
    exceptions: tuple[ExceptionCheck, ...]
    reasons: tuple[str, ...]
    sources: tuple[SegmentSource, ...]
    draft_label: str

    @property
    def needs_street_width(self) -> bool:
        return self.street_class == CLASS_NEEDS_STREET_WIDTH


@dataclass(frozen=True)
class SiteStreetWidths:
    """Every frontage of one lot with its street width. ``status`` is ``complete`` only
    when there is at least one frontage and each has a class; otherwise the lot carries
    ``marker`` "Needs street width" and ``notes`` say why."""

    status: str
    marker: str | None
    frontages: tuple[FrontageStreetWidth, ...]
    notes: tuple[str, ...]
    draft_label: str
    provenance: Mapping[str, object] = field(default_factory=dict)

    def frontage(self, street_key: str) -> FrontageStreetWidth | None:
        for frontage in self.frontages:
            if frontage.street_key == street_key:
                return frontage
        return None
