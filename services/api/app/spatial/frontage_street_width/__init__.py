"""Street width per frontage (queue item B-04; plan M1-13 data side and §4 "Street widths").

For each frontage the single-lot site geometry (B-03, :mod:`app.spatial.site_geometry`)
found, attach the adjacent street's MAPPED width from the DCP Digital City Map and its
wide / narrow class through the accepted DCM width classifier and D-052 policy, with the
source, dataset and retrieval time. A width that is unknown, unresolved or not yet checked
against the ZR 12-10 exceptions is marked "Needs street width" with both classes possible -
never a silent narrow default.

Modules: ``inputs`` (plain inputs) · ``exceptions`` (ZR 12-10 exception checks through the
accepted matcher) · ``derive`` (pure entry point) · ``results`` · ``adapters`` (from
connector results). Nothing calls this package yet; a later Lane A/C task wires it and does
any result doubling. Everything here is DRAFT until qualified review (D-052-R007).
"""

from __future__ import annotations

from .adapters import (
    mapped_segments_from_pages,
    street_widths_from_sources,
    zoning_context_from_pluto,
)
from .derive import FRONTAGE_NOT_CONFIRMED, METHOD_VERSION, derive_frontage_street_widths
from .exceptions import (
    EXCEPTION_MAY_APPLY,
    EXCEPTION_NOT_APPLICABLE,
    EXCEPTION_NOT_CHECKED,
    ExceptionCheck,
    Zr1210Exceptions,
    default_exceptions,
)
from .inputs import LotZoningContext, MappedStreetSegment, SegmentSource
from .results import (
    CLASS_NARROW,
    CLASS_NEEDS_STREET_WIDTH,
    CLASS_WIDE,
    MARKER_NEEDS_STREET_WIDTH,
    STATUS_COMPLETE,
    STATUS_NEEDS_STREET_WIDTH,
    FrontageStreetWidth,
    SegmentWidthReading,
    SiteStreetWidths,
)

__all__ = [
    "CLASS_NARROW",
    "CLASS_NEEDS_STREET_WIDTH",
    "CLASS_WIDE",
    "EXCEPTION_MAY_APPLY",
    "EXCEPTION_NOT_APPLICABLE",
    "EXCEPTION_NOT_CHECKED",
    "FRONTAGE_NOT_CONFIRMED",
    "MARKER_NEEDS_STREET_WIDTH",
    "METHOD_VERSION",
    "STATUS_COMPLETE",
    "STATUS_NEEDS_STREET_WIDTH",
    "ExceptionCheck",
    "FrontageStreetWidth",
    "LotZoningContext",
    "MappedStreetSegment",
    "SegmentSource",
    "SegmentWidthReading",
    "SiteStreetWidths",
    "Zr1210Exceptions",
    "default_exceptions",
    "derive_frontage_street_widths",
    "mapped_segments_from_pages",
    "street_widths_from_sources",
    "zoning_context_from_pluto",
]
