"""Survey-document extraction pipeline package (M2-T015; architecture sections 2-8).

The S2-S8 side of the document ingestion pipeline: the routing/gating shell (unit
3i-2) — the CLOSED S3 format-routing matrix (SB-S2), the isolation-gated single
pipeline entry, and the SB-S7 wrong-address ``needs_review`` routing decision — plus
the in-repo strict-subset PDF reader (units 3i-3a..3j), the concrete
:class:`~app.documents.extraction.vector_pdf_decoder.VectorPdfDecoder` for the
digitally-authored PDF routes (unit 3k, SB-S1), and the end-to-end deterministic
:func:`~app.documents.extraction.survey_pipeline.run_survey_extraction` that composes
decode → assemble → check → promote. No unisolated parsing path exists: decoding is
reachable only inside an ``ExtractionJobAuthorized`` from a proven isolation boundary.
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
from app.documents.extraction.survey_pipeline import (
    AssembledFact,
    DecoderUnavailable,
    ExtractionCompleted,
    ExtractionNotStarted,
    SurveyExtractionContext,
    SurveyExtractionOutcome,
    assemble_survey_evidence,
    run_survey_extraction,
)
from app.documents.extraction.vector_pdf_decoder import (
    DecodedPage,
    PdfDecodeRefusal,
    VectorPdfDecoder,
    pdf_decode_refusal,
)

__all__ = [
    "AssembledFact",
    "DecodedPage",
    "DecoderSeam",
    "DecoderUnavailable",
    "ExtractionCompleted",
    "ExtractionEntryOutcome",
    "ExtractionJobAuthorized",
    "ExtractionNotStarted",
    "FormatRoute",
    "IsolationUnavailable",
    "NeedsReviewRouting",
    "PdfDecodeRefusal",
    "RouteDeferred",
    "RouteRejected",
    "RouteSupported",
    "SUPPORTED_FORMATS",
    "SurveyDocumentFormat",
    "SurveyExtractionContext",
    "SurveyExtractionOutcome",
    "VectorPdfDecoder",
    "assemble_survey_evidence",
    "begin_extraction_job",
    "pdf_decode_refusal",
    "route_format",
    "run_survey_extraction",
    "wrong_address_routing",
]
