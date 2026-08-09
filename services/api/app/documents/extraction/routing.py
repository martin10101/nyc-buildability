"""S3 format routing, isolation-gated pipeline entry, and wrong-address routing (M2-T015).

The routing/gating SHELL between the S1 upload gate and the per-format decoders
(``docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md`` sections 2-3). Three things live
here, all of them frozen typed values, none of them parsers:

- :func:`route_format` — the CLOSED per-format decision matrix of architecture
  section 3 (pipeline stage S3; SB-S2). Each SUPPORTED matrix row routes to its
  verbatim permitted ``extraction_method`` values; DXF and native DWG defer with the
  policy's stated vector-PDF-export alternative; anything else is a typed rejection
  naming the supported formats. Never improvised parsing.
- :func:`begin_extraction_job` — the SINGLE pipeline entry. It consults
  :func:`app.documents.isolation.require_isolation` FIRST; on
  :class:`~app.documents.isolation.ParsingDisabled` it returns the frozen
  :class:`IsolationUnavailable` outcome: the document rests in ``uploaded``, stages
  S2-S8 never run, and no unisolated fallback path exists structurally — there is no
  parameter, flag, or ambient state through which this function can skip the gate.
  Only on ParsingPermitted plus a supported route does it return
  :class:`ExtractionJobAuthorized`, carrying the route, the :class:`DecoderSeam`
  protocol reference, and — for the digitally-authored PDF routes — the CONCRETE
  :class:`~app.documents.extraction.vector_pdf_decoder.VectorPdfDecoder` (unit 3k).
  The decode implementation itself lives in that module and in the ``pdf_*`` reader;
  this module only SELECTS and hands out the decoder inside a proven-boundary
  authorization — it still runs no bytes of its own.
- :func:`wrong_address_routing` — SB-S7: a FAILED or UNEVALUABLE
  ``address_bbl_match`` check routes the document to ``needs_review`` (flagged,
  never ingested as usable). The decision is a value; performing the transition —
  and later leaving ``needs_review`` only over the promotion-gated
  professional-confirmation edge — belongs to
  :func:`app.documents.state.promotion_gated_transition`, never to this module.

Routing consumes the upload gate's ALREADY-SNIFFED format identity as a typed input
(:class:`SurveyDocumentFormat`); no byte is ever inspected or re-sniffed here. The S1
gate's canonical raster ids (``tiff``/``png``/``jpeg``, :mod:`app.documents.gate`) are
these members' values verbatim; the coarse sniffed ``pdf`` id must be refined into one
of the three PDF matrix rows by the isolated S2 structural screen before S3 routing —
an unrefined identity therefore routes to a fail-closed rejection, never to a guess.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from app.documents.checks import CheckFailed, CheckUnevaluable
from app.documents.extraction.vector_pdf_decoder import VectorPdfDecoder
from app.documents.isolation import ParsingDisabled, require_isolation
from app.documents.state import PROMOTION_GATED_TRANSITIONS, DocumentState

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


# ------------------------------------------------------- closed format identities


class SurveyDocumentFormat(str, Enum):
    """CLOSED enum of the architecture section-3 format-policy matrix rows.

    Exactly the eight policy rows exist; a new member is added additively only after
    the format policy approves a new path (section 3). ``TIFF``/``PNG``/``JPEG``
    values are the S1 gate's canonical sniffed ids verbatim; the three PDF members
    are the S2 structural refinement of the gate's coarse ``pdf`` id. ``DXF`` and
    ``DWG`` exist so the router can answer policy rows 6-7 with their typed
    deferrals (S1 already refuses those uploads by extension upstream; the router
    stays total over the policy matrix regardless).
    """

    BORN_DIGITAL_PDF = "born_digital_pdf"
    VECTOR_PDF = "vector_pdf"
    SCANNED_PDF = "scanned_pdf"
    TIFF = "tiff"
    PNG = "png"
    JPEG = "jpeg"
    DXF = "dxf"
    DWG = "dwg"


#: The six SUPPORTED matrix rows (section 3 rows 1-5), in matrix order.
SUPPORTED_FORMATS: tuple[SurveyDocumentFormat, ...] = (
    SurveyDocumentFormat.BORN_DIGITAL_PDF,
    SurveyDocumentFormat.VECTOR_PDF,
    SurveyDocumentFormat.SCANNED_PDF,
    SurveyDocumentFormat.TIFF,
    SurveyDocumentFormat.PNG,
    SurveyDocumentFormat.JPEG,
)

#: Section-3 row 3 permitted methods, verbatim; rows 4-5 are "as row 3".
_ROW_3_RASTER_METHODS: tuple[str, ...] = (
    "ocr_text",
    "line_symbol_detection",
    "ai_assisted_classification",
    "deterministic_geometry_reconstruction",
)

#: Permitted ``extraction_method`` values per SUPPORTED row, VERBATIM from the
#: section-3 matrix (the closed enum of the survey_evidence contract; no other path
#: exists). Row order inside each tuple follows the matrix cell exactly.
_EXTRACTION_METHODS: Mapping[SurveyDocumentFormat, tuple[str, ...]] = {
    SurveyDocumentFormat.BORN_DIGITAL_PDF: (
        "embedded_text_extraction",
        "vector_object_extraction",
        "ai_assisted_classification",
        "deterministic_geometry_reconstruction",
    ),
    SurveyDocumentFormat.VECTOR_PDF: (
        "vector_object_extraction",
        "embedded_text_extraction",
        "ai_assisted_classification",
        "deterministic_geometry_reconstruction",
    ),
    SurveyDocumentFormat.SCANNED_PDF: _ROW_3_RASTER_METHODS,
    SurveyDocumentFormat.TIFF: _ROW_3_RASTER_METHODS,
    SurveyDocumentFormat.PNG: _ROW_3_RASTER_METHODS,
    SurveyDocumentFormat.JPEG: _ROW_3_RASTER_METHODS,
}

#: Rows flagged ``raster_only=true`` (row 3; rows 4-5 are "as row 3"). Their
#: detections are ADVISORY: the section-3 advisory-lineage rule always routes a
#: material fact with advisory-only lineage to ``needs_review`` downstream (S7/S8).
_RASTER_ONLY_FORMATS: frozenset[SurveyDocumentFormat] = frozenset(
    {
        SurveyDocumentFormat.SCANNED_PDF,
        SurveyDocumentFormat.TIFF,
        SurveyDocumentFormat.PNG,
        SurveyDocumentFormat.JPEG,
    }
)

_DXF_GUIDANCE = (
    "DXF is not parsed: no validated conversion stage exists yet, so this upload is "
    "refused. Export the drawing as a vector PDF (format policy row 2, the primary "
    "CAD interchange target) and upload that instead. A future DXF-to-vector-PDF "
    "conversion stage must pass its own G1 review before any DXF is accepted."
)

_DWG_GUIDANCE = (
    "Native DWG is not parsed and nothing is derived from it. The format policy "
    "permits store-only acceptance at most; because B-001 defers durable private "
    "storage, store-only DWG acceptance is also deferred. Export the drawing as a "
    "vector PDF and upload that instead. Adopting any DWG-parsing library is a "
    "licensing/payment STOP condition reserved to the owner."
)


# ------------------------------------------------------------ typed route results


@dataclass(frozen=True)
class RouteSupported:
    """Typed SUPPORTED route: one of the six supported matrix rows, carrying its
    permitted ``extraction_method`` values verbatim from the section-3 matrix cell.

    ``raster_only`` restates the matrix flag for rows 3-5: their OCR and line/symbol
    detections are advisory, and the advisory-lineage rule (section 3) keeps any
    material fact with advisory-only lineage on the ``needs_review`` path downstream.
    The payload is metadata only and safe to serialize.
    """

    format: SurveyDocumentFormat
    extraction_methods: tuple[str, ...]
    raster_only: bool

    supported = True

    def to_payload(self) -> dict:
        """Structured route payload (metadata only, JSON-serializable)."""
        return {
            "route": "supported",
            "format": self.format.value,
            "extraction_methods": list(self.extraction_methods),
            "raster_only": self.raster_only,
        }


@dataclass(frozen=True)
class RouteDeferred:
    """Typed DEFERRAL of a policy row the pipeline recognizes but must not parse
    (section-3 rows 6-7: DXF and native DWG), carrying the policy's stated
    alternative verbatim as ``guidance``. Deliberately a value, never an exception."""

    format: SurveyDocumentFormat
    guidance: str

    supported = False
    reject_code = "format_deferred"

    def to_payload(self) -> dict:
        """Structured deferral payload (metadata only, JSON-serializable)."""
        return {
            "route": "deferred",
            "reject_code": self.reject_code,
            "format": self.format.value,
            "guidance": self.guidance,
        }


@dataclass(frozen=True)
class RouteRejected:
    """Typed rejection of anything outside the closed matrix, naming the supported
    formats (section-3 final row). Improvised parsing of an unmatrixed format never
    exists (SB-S2). ``presented`` is the repr of the offered identity — metadata
    only, never document bytes."""

    presented: str
    supported_formats: tuple[str, ...]

    supported = False
    reject_code = "unsupported_format"

    def to_payload(self) -> dict:
        """Structured rejection payload (metadata only, JSON-serializable)."""
        return {
            "route": "rejected",
            "reject_code": self.reject_code,
            "presented": self.presented,
            "supported_formats": list(self.supported_formats),
        }


FormatRoute = RouteSupported | RouteDeferred | RouteRejected


def route_format(format_identity: object) -> FormatRoute:
    """Route the upload gate's already-sniffed (and S2-refined) format identity
    through the CLOSED section-3 matrix. Pure value-to-value: no byte is inspected.

    Accepts a :class:`SurveyDocumentFormat` member or its exact serialized value
    string (job payloads carry strings); every other input — including the coarse
    unrefined ``'pdf'`` sniff id — is a fail-closed :class:`RouteRejected` naming
    the supported formats, never a guess.
    """
    if isinstance(format_identity, SurveyDocumentFormat):
        fmt = format_identity
    else:
        try:
            fmt = SurveyDocumentFormat(format_identity)
        except (ValueError, TypeError):
            return RouteRejected(
                presented=repr(format_identity),
                supported_formats=tuple(f.value for f in SUPPORTED_FORMATS),
            )
    if fmt is SurveyDocumentFormat.DXF:
        return RouteDeferred(format=fmt, guidance=_DXF_GUIDANCE)
    if fmt is SurveyDocumentFormat.DWG:
        return RouteDeferred(format=fmt, guidance=_DWG_GUIDANCE)
    return RouteSupported(
        format=fmt,
        extraction_methods=_EXTRACTION_METHODS[fmt],
        raster_only=fmt in _RASTER_ONLY_FORMATS,
    )


# ------------------------------------------------------------------- decoder seam


@runtime_checkable
class DecoderSeam(Protocol):
    """Typed seam for the per-format decoders of pipeline stage S4.

    A conforming decoder decodes the immutable original's exact bytes into
    structured extraction primitives inside the section-5 parser isolation boundary.
    The first concrete implementation is
    :class:`~app.documents.extraction.vector_pdf_decoder.VectorPdfDecoder` (unit 3k,
    the digitally-authored PDF routes); a Protocol class itself cannot be
    instantiated, so the bare seam is never a runnable decode path — only a concrete
    conforming decoder is.
    """

    def decode(self, original_bytes: bytes) -> Sequence[object]:
        """Decode untrusted original bytes into structured detection primitives."""
        ...


# ------------------------------------------------------- gated pipeline entry


@dataclass(frozen=True)
class IsolationUnavailable:
    """Typed refusal of the whole extraction job: the parser isolation boundary is
    not affirmatively proven, so stages S2-S8 never run (architecture section 2).

    The document rests in ``uploaded`` (``resting_state``); nothing silently
    degrades, and no unisolated fallback exists anywhere. Carries the frozen
    :class:`~app.documents.isolation.ParsingDisabled` verdict verbatim as the
    stated reason. Deliberately a value, never an exception.
    """

    verdict: ParsingDisabled

    authorized = False
    reject_code = "isolation_unavailable"
    resting_state = DocumentState.UPLOADED

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "outcome": "isolation_unavailable",
            "reject_code": self.reject_code,
            "resting_state": self.resting_state.value,
            "verdict": self.verdict.to_payload(),
        }


@dataclass(frozen=True)
class ExtractionJobAuthorized:
    """Typed authorization of one extraction job: isolation affirmatively proven AND
    the format routed to a supported matrix row.

    Carries the :class:`RouteSupported` route, the :class:`DecoderSeam` protocol
    reference the per-format decoder must satisfy, and — for a route whose concrete
    stage-S4 decoder exists — the CONCRETE :class:`DecoderSeam` implementation itself
    (``decoder``). The digitally-authored PDF routes (born-digital and vector PDF,
    format-policy rows 1-2, SB-S1) carry a concrete
    :class:`~app.documents.extraction.vector_pdf_decoder.VectorPdfDecoder`; the
    advisory raster routes (rows 3-5) still carry ``decoder=None`` because their
    concrete decoder is a later unit — an authorization for them routes but does not
    yet decode. Authorization is capability plus routing plus decoder selection only —
    RUNNING the decoder inside the applied, self-verified isolation boundary remains
    the isolated parser path's duty (section 5); a decoder is handed out ONLY inside
    this value, which :func:`begin_extraction_job` returns exclusively on a proven
    boundary, so no decoder is ever reachable without one.
    """

    route: RouteSupported
    decoder_protocol: type
    decoder: DecoderSeam | None = None

    authorized = True

    def to_payload(self) -> dict:
        """Structured authorization payload (metadata only, JSON-serializable)."""
        return {
            "outcome": "extraction_job_authorized",
            "route": self.route.to_payload(),
            "decoder_protocol": self.decoder_protocol.__name__,
            "decoder": None if self.decoder is None else type(self.decoder).__name__,
        }


ExtractionEntryOutcome = (
    IsolationUnavailable | ExtractionJobAuthorized | RouteDeferred | RouteRejected
)


#: The one shared, stateless concrete decoder for the digitally-authored PDF routes
#: (born-digital + vector PDF, format-policy rows 1-2, SB-S1). Both rows are decoded by
#: the same in-repo strict-subset reader — it extracts BOTH vector objects and the
#: embedded text layer — so one instance serves both. The advisory raster rows (3-5)
#: are deliberately ABSENT: their concrete decoder is a later unit, so a supported
#: raster route authorizes with ``decoder=None`` and does not yet decode. A shared
#: instance is safe because ``VectorPdfDecoder.decode`` is a pure function of its bytes.
_CONCRETE_DECODERS: Mapping[SurveyDocumentFormat, DecoderSeam] = {
    SurveyDocumentFormat.VECTOR_PDF: VectorPdfDecoder(),
    SurveyDocumentFormat.BORN_DIGITAL_PDF: VectorPdfDecoder(),
}


def begin_extraction_job(format_identity: object) -> ExtractionEntryOutcome:
    """The SINGLE entry point of the extraction pipeline (stages S2-S8).

    FIRST consults :func:`app.documents.isolation.require_isolation`; a
    :class:`~app.documents.isolation.ParsingDisabled` verdict returns
    :class:`IsolationUnavailable` before any routing — the document rests in
    ``uploaded`` and S2-S8 never run. Only under ParsingPermitted is the format
    routed: a supported route returns :class:`ExtractionJobAuthorized`; a deferred
    or rejected route is returned verbatim as the job outcome.

    Structurally bypass-free ON PURPOSE: the sole parameter is the format identity,
    and the isolation gate is consulted unconditionally inside — there is NO
    parameter, flag, environment variable, or ambient state through which a caller
    can reach routing (let alone a decoder) without a proven boundary. Widening this
    signature with any gate-skipping affordance is a doctrine violation
    (architecture sections 2 and 5).
    """
    capability = require_isolation()
    if isinstance(capability.verdict, ParsingDisabled):
        return IsolationUnavailable(verdict=capability.verdict)
    route = route_format(format_identity)
    if isinstance(route, RouteSupported):
        return ExtractionJobAuthorized(
            route=route,
            decoder_protocol=DecoderSeam,
            decoder=_CONCRETE_DECODERS.get(route.format),
        )
    return route


# ---------------------------------------------------- wrong-address routing (SB-S7)

_ADDRESS_BBL_MATCH = "address_bbl_match"

#: The only exit from ``needs_review`` toward usable evidence. Guarded at import so
#: wrong-address routing can never exist without the promotion gate on that edge.
_PROFESSIONAL_CONFIRMATION_EDGE = (
    DocumentState.NEEDS_REVIEW,
    DocumentState.PROFESSIONALLY_CONFIRMED,
)

if _PROFESSIONAL_CONFIRMATION_EDGE not in PROMOTION_GATED_TRANSITIONS:
    raise RuntimeError(
        "structural invariant broken: the needs_review -> professionally_confirmed "
        "edge is no longer promotion-gated (app.documents.state); wrong-address "
        "routing (SB-S7) must not exist without that gate"
    )


@dataclass(frozen=True)
class NeedsReviewRouting:
    """Typed ``needs_review`` routing decision for a wrong-address document (SB-S7).

    A FAILED or UNEVALUABLE ``address_bbl_match`` check flags the document: it is
    never ingested as usable evidence (``usable`` is structurally False), and the
    only way its facts ever become usable is a qualified human driving the
    promotion-gated professional-confirmation edge via
    :func:`app.documents.state.promotion_gated_transition`. This object is a VALUE:
    it performs no transition, and nothing here mutates document state. Carries the
    consumed check's payload verbatim as provenance.
    """

    check_name: str
    cause: str
    check_payload: Mapping[str, object]

    routing = "needs_review"
    target_state = DocumentState.NEEDS_REVIEW
    flagged = True
    usable = False

    def to_payload(self) -> dict:
        """Structured routing payload (metadata only, JSON-serializable)."""
        return {
            "routing": self.routing,
            "target_state": self.target_state.value,
            "flagged": self.flagged,
            "usable": self.usable,
            "check_name": self.check_name,
            "cause": self.cause,
            "check": dict(self.check_payload),
        }


def wrong_address_routing(address_check: object) -> NeedsReviewRouting:
    """Route a wrong-address document to ``needs_review`` (SB-S7).

    Consumes the typed ``address_bbl_match`` result: a :class:`CheckFailed` (the
    document's address/BBL facts contradict the upload-intent BBL) and a
    :class:`CheckUnevaluable` (the match could not be evaluated) BOTH flag the
    document — an unevaluable identity check never passes silently. Anything else
    is caller misuse and raises: a passed check needs no wrong-address routing, and
    a routing decision is never fabricated from one.
    """
    if not isinstance(address_check, (CheckFailed, CheckUnevaluable)):
        raise TypeError(
            "wrong_address_routing consumes a CheckFailed or CheckUnevaluable "
            f"address_bbl_match result; got {type(address_check).__name__} — a "
            "needs_review routing is never fabricated from a pass or a non-check"
        )
    if address_check.check_name != _ADDRESS_BBL_MATCH:
        raise ValueError(
            "wrong_address_routing consumes only the address_bbl_match check; got "
            f"check_name {address_check.check_name!r}"
        )
    cause = "failed" if isinstance(address_check, CheckFailed) else "unevaluable"
    return NeedsReviewRouting(
        check_name=address_check.check_name,
        cause=cause,
        check_payload=address_check.to_payload(),
    )
