"""Survey-document extraction pipeline package (M2-T015; architecture sections 2-3).

The S2-S8 side of the document ingestion pipeline. This package currently contains
the routing/gating shell (unit 3i-2): the CLOSED S3 format-routing matrix (SB-S2),
the isolation-gated single pipeline entry, and the SB-S7 wrong-address
``needs_review`` routing decision. Per-format decoders implement
:class:`~app.documents.extraction.routing.DecoderSeam` in later units — no decode
implementation exists in this package yet, and no unisolated parsing path ever will.
"""

from app.documents.extraction.routing import (
    SUPPORTED_FORMATS,
    DecoderSeam,
    ExtractionEntryOutcome,
    ExtractionJobAuthorized,
    FormatRoute,
    IsolationUnavailable,
    NeedsReviewRouting,
    RouteDeferred,
    RouteRejected,
    RouteSupported,
    SurveyDocumentFormat,
    begin_extraction_job,
    route_format,
    wrong_address_routing,
)

__all__ = [
    "DecoderSeam",
    "ExtractionEntryOutcome",
    "ExtractionJobAuthorized",
    "FormatRoute",
    "IsolationUnavailable",
    "NeedsReviewRouting",
    "RouteDeferred",
    "RouteRejected",
    "RouteSupported",
    "SUPPORTED_FORMATS",
    "SurveyDocumentFormat",
    "begin_extraction_job",
    "route_format",
    "wrong_address_routing",
]
