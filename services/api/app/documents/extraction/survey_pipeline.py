"""End-to-end deterministic survey-extraction pipeline (M2-T015 unit 3k).

Wires the already-built stages of the ingestion pipeline into ONE deterministic
flow for the digitally-authored PDF routes (SB-S1):

    begin_extraction_job  (isolation gate + S3 routing, unit 3i)
        -> VectorPdfDecoder.decode  (S4 decode, unit 3k / pdf_* reader)
        -> assemble survey_evidence facts  (this module)
        -> deterministic checks  (app.documents.checks, unit 3d)
        -> per-fact promotion verdicts  (app.documents.promotion, unit 3f)
        -> gated state transition  (promotion_gated_transition, unit 3f-2)

Doctrine (CLAUDE.md principle 1; architecture §§8-10) is enforced STRUCTURALLY, not
by convention:

* **Isolation is fail-closed and unbypassable.** Decoding is reachable ONLY through
  :func:`app.documents.extraction.routing.begin_extraction_job`, which consults
  :func:`app.documents.isolation.require_isolation` first and hands out a decoder only
  inside an ``ExtractionJobAuthorized``. When the boundary is unproven this pipeline
  returns the verbatim :class:`IsolationUnavailable` and NEVER touches a decoder — the
  document rests in ``uploaded`` (the caller keeps the record where it is).
* **Deterministic code calculates; AI does not.** Fact assembly here is pure
  pattern-and-provenance code: it classifies a decoded embedded-text run ONLY by an
  EXACT canonical pattern (a ``1:N`` scale ratio, a 10-digit NYC BBL) — never fuzzy,
  never a model. Distances, bearings, areas, and free-text addresses need richer
  normalization/classification (architecture §§8.2-8.3, §10) and are deliberately NOT
  fabricated here; the advisory ``ai_assisted_classification`` path that proposes them
  remains promotion-gated and is a later unit.
* **Promotion is deterministic and confidence-blind.** Every assembled fact is born
  ``unconfirmed`` and promotes to ``auto_extracted`` only when its normalized-value and
  correction-history validators resolve (:func:`evaluate_promotion`) AND every executed
  deterministic check passes. Any failing/unresolved check, any unproven fact, a
  wrong-address ``address_bbl_match`` (SB-S7), a decode refusal, or an empty extraction
  routes the document to ``needs_review`` — never a silent pass, never a silent drop.

The pipeline is a pure function of its inputs plus the injected isolation verdict: it
mutates no global state and performs no I/O. The gated ``processing -> auto_extracted``
edge is driven through :func:`app.documents.state.promotion_gated_transition`; the
fail-closed ``processing -> needs_review`` edge through the raw authority-checked
:func:`app.documents.state.transition` (a non-gated edge). Raw ``transition`` is never
used for a gated edge.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from app.documents.checks import (
    CheckFailed,
    CheckPassed,
    CheckResult,
    CheckUnevaluable,
    address_bbl_match,
    scale_consistency,
)
from app.documents.correction_history import (
    CorrectionHistoryValidation,
    NormalizationBaseline,
    ValidatedCorrectionHistory,
    validate_correction_history,
)
from app.documents.extraction.routing import (
    ExtractionEntryOutcome,
    ExtractionJobAuthorized,
    NeedsReviewRouting,
    RouteSupported,
    begin_extraction_job,
    wrong_address_routing,
)
from app.documents.extraction.vector_pdf_decoder import (
    DecodedPage,
    PdfDecodeRefusal,
    pdf_decode_refusal,
)
from app.documents.geometry_validation import LocationValidation, validate_location
from app.documents.models import BBL_PATTERN
from app.documents.promotion import (
    REQUIRED_VALIDATIONS,
    PromotionAllowed,
    PromotionVerdict,
    ValidationKind,
    evaluate_promotion,
)
from app.documents.state import (
    DocumentState,
    TransitionActor,
    TransitionRecord,
    promotion_gated_transition,
    transition,
)
from app.documents.taxonomy import SurveyFactType
from app.documents.units import (
    SCALE_RATIO_PATTERN,
    NormalizedValueValidation,
    ValidatedScale,
    ValidatedUnitlessText,
    validate_normalized_value,
)

__all__ = [
    "AssembledFact",
    "DecoderUnavailable",
    "ExtractionCompleted",
    "ExtractionNotStarted",
    "SurveyExtractionContext",
    "SurveyExtractionOutcome",
    "assemble_survey_evidence",
    "run_survey_extraction",
]

#: The extraction path recorded on every fact this deterministic assembler emits: the
#: born-digital PDF embedded text layer (a digitally-authored, non-advisory read).
_EMBEDDED_TEXT = "embedded_text_extraction"

#: Deterministic reads of digitally-authored embedded text carry full detection
#: confidence (schema ``confidence`` doctrine); confidence NEVER promotes a value.
_DETERMINISTIC_CONFIDENCE = 1.0

_PDF_USER_SPACE = "pdf_user_space_points"


# ------------------------------------------------------------------ input context


@dataclass(frozen=True)
class SurveyExtractionContext:
    """Document-level context every assembled fact needs for provenance and matching.

    ``document_digest`` is the immutable-original content identity (``sha256:<64 hex>``)
    every fact carries; ``target_bbl`` is the upload INTENT written to each fact's
    ``bbl`` (never a verified association — the ``address_bbl_match`` check records
    that). ``subject_address``/``subject_bbl`` are the STATED subject-property targets
    the deterministic ``address_bbl_match`` check compares against. ``extraction_run_id``
    groups every fact of this one isolated run; ``extracted_at`` is the RFC 3339
    extraction timestamp. All are supplied by the caller (the S1 record + the analysis
    target) — nothing here is defaulted or guessed.
    """

    document_digest: str
    target_bbl: str
    subject_address: str
    subject_bbl: str
    extraction_run_id: str
    extracted_at: str


# ------------------------------------------------------------------ assembled fact


@dataclass(frozen=True)
class AssembledFact:
    """One deterministically assembled survey fact: its schema-shaped ``survey_evidence``
    record plus the typed validator results the promotion gate consumes.

    ``evidence`` is a JSON-shaped ``dict`` that validates against
    ``packages/contracts/schemas/v1/survey_evidence.schema.json``; its
    ``validation_results`` array is filled in with the deterministic CHECK outcomes
    after assembly. ``normalized_validation``, ``location_validation``, and
    ``history_validation`` are the frozen typed results of the deterministic validators
    (units / geometry / correction-history) for THIS fact — the promotion gate's grounds.
    """

    evidence: dict
    fact_type: SurveyFactType
    normalized_validation: NormalizedValueValidation
    location_validation: LocationValidation
    history_validation: CorrectionHistoryValidation


# ------------------------------------------------------------------ typed outcomes


@dataclass(frozen=True)
class ExtractionNotStarted:
    """The isolation gate or S3 routing refused before any decode: the verbatim
    :class:`IsolationUnavailable` / :class:`RouteDeferred` / :class:`RouteRejected`
    from :func:`begin_extraction_job`. No decoder was touched and no state changed —
    the document stays where it is (``uploaded``)."""

    entry_outcome: ExtractionEntryOutcome

    started = False

    def to_payload(self) -> dict:
        return {
            "outcome": "extraction_not_started",
            "entry_outcome": self.entry_outcome.to_payload(),
        }


@dataclass(frozen=True)
class DecoderUnavailable:
    """An authorized SUPPORTED route whose concrete stage-S4 decoder is a later unit
    (the advisory raster routes). Isolation is proven and the format is supported, but
    no decode is attempted here — the route is carried verbatim for the caller."""

    route: RouteSupported

    started = False

    def to_payload(self) -> dict:
        return {"outcome": "decoder_unavailable", "route": self.route.to_payload()}


@dataclass(frozen=True)
class ExtractionCompleted:
    """A completed decode + assembly + check + promotion pass over one document.

    ``facts`` are the schema-shaped ``survey_evidence`` records (with their check
    ``validation_results`` filled in); ``check_results`` are the executed deterministic
    checks; ``fact_verdicts`` map each fact's ``evidence_id`` to its deterministic
    :class:`PromotionVerdict`. ``target_state`` is the lifecycle state the pipeline
    routed the document to and ``transition_record`` is the authority-checked record of
    that edge (a gated ``processing -> auto_extracted`` or a fail-closed
    ``processing -> needs_review``). ``wrong_address`` carries the SB-S7
    :class:`NeedsReviewRouting` when an ``address_bbl_match`` failure/unevaluable drove
    the review routing; ``decode_refusal`` carries the typed reader refusal when the
    document was routed to review because it could not be decoded within the strict
    subset. Both are ``None`` on the clean auto-extracted path.
    """

    facts: tuple[dict, ...]
    check_results: tuple[CheckResult, ...]
    fact_verdicts: Mapping[str, PromotionVerdict]
    target_state: DocumentState
    transition_record: TransitionRecord
    wrong_address: NeedsReviewRouting | None
    decode_refusal: PdfDecodeRefusal | None

    started = True

    def to_payload(self) -> dict:
        return {
            "outcome": "extraction_completed",
            "target_state": self.target_state.value,
            "fact_count": len(self.facts),
            "check_results": [result.to_payload() for result in self.check_results],
            "fact_verdicts": {
                fact_id: (
                    "promotion_allowed"
                    if isinstance(verdict, PromotionAllowed)
                    else verdict.to_payload()
                )
                for fact_id, verdict in self.fact_verdicts.items()
            },
            "wrong_address": (
                None if self.wrong_address is None else self.wrong_address.to_payload()
            ),
            "decode_refusal": (
                None
                if self.decode_refusal is None
                else {
                    "refusal_type": type(self.decode_refusal).__name__,
                    "detail": str(self.decode_refusal),
                }
            ),
        }


SurveyExtractionOutcome = ExtractionNotStarted | DecoderUnavailable | ExtractionCompleted


# ---------------------------------------------------------- deterministic classify


def _classify_text_run(text: object) -> tuple[SurveyFactType, str] | None:
    """The (fact type, normalized value) an embedded-text run deterministically states,
    or ``None`` when no EXACT canonical pattern matches.

    Only two unambiguous, closed-form patterns are recognized — the whole run must
    match, with NO trimming, case-folding, or interpretation (a silent cleanup would be
    a silent classification): a canonical ``1:N`` drawing-scale ratio, and a 10-digit
    NYC BBL. Everything else is left unclassified rather than guessed; richer
    normalization (distances/bearings/areas) and fuzzy labeling (addresses) belong to
    later deterministic-association and advisory-AI units, never to this exact matcher.
    """
    if not isinstance(text, str):
        return None
    if SCALE_RATIO_PATTERN.fullmatch(text):
        return (SurveyFactType.SCALE_STATEMENT, text)
    if BBL_PATTERN.fullmatch(text):
        return (SurveyFactType.BBL_TEXT, text)
    return None


def _build_fact(
    page: DecodedPage,
    text: str,
    member: SurveyFactType,
    normalized_value: str,
    context: SurveyExtractionContext,
    x: float,
    y: float,
    sequence: int,
) -> AssembledFact:
    """Assemble one provenance-complete ``survey_evidence`` fact + its typed validations.

    The fact records the exact detected run verbatim as ``original_value`` (immutable),
    the deterministically classified ``normalized_value``, an explicit unitless ``units``
    (``None``), the ``embedded_text_extraction`` path, full detection confidence, an
    empty (never-corrected) history, and the born ``unconfirmed`` professional state.
    The locator is a page-space ``bounding_box`` at the run's device-space anchor
    (a zero-extent point box — the schema permits ``x_min == x_max`` and the deterministic
    geometry validator allows the equality); page coordinates are NEVER survey/world
    coordinates. Every validator is run at assembly time so the fact carries its own
    typed grounds.
    """
    page_number = page.index + 1
    digest_hex = context.document_digest.split(":", 1)[1]
    evidence_id = f"sev:{digest_hex[:12]}:p{page_number}:{sequence:03d}"
    location = {
        "kind": "bounding_box",
        "bounding_box": {
            "x_min": x,
            "y_min": y,
            "x_max": x,
            "y_max": y,
            "coordinate_space": _PDF_USER_SPACE,
        },
    }
    evidence: dict = {
        "evidence_id": evidence_id,
        "bbl": context.target_bbl,
        "document_digest": context.document_digest,
        "page_number": page_number,
        "location": location,
        "fact_type": member.value,
        "original_value": text,
        "normalized_value": normalized_value,
        "units": None,
        "extraction_method": _EMBEDDED_TEXT,
        "extraction_run_id": context.extraction_run_id,
        "extracted_at": context.extracted_at,
        "confidence": _DETERMINISTIC_CONFIDENCE,
        "validation_results": [],
        "correction_history": [],
        "professional_confirmation": {
            "state": "unconfirmed",
            "confirmed_by": None,
            "confirmed_at": None,
        },
    }
    normalized_validation = validate_normalized_value(member.value, normalized_value, None)
    location_validation = validate_location(location, _EMBEDDED_TEXT)
    history_validation = validate_correction_history(
        original_value=text,
        normalized_value=normalized_value,
        units=None,
        correction_history=[],
        baseline=NormalizationBaseline(normalized_value=normalized_value, units=None),
    )
    return AssembledFact(
        evidence=evidence,
        fact_type=member,
        normalized_validation=normalized_validation,
        location_validation=location_validation,
        history_validation=history_validation,
    )


def assemble_survey_evidence(
    pages: Sequence[DecodedPage], context: SurveyExtractionContext
) -> tuple[AssembledFact, ...]:
    """Deterministically assemble ``survey_evidence`` facts from decoded pages.

    One fact is emitted per embedded-text run that EXACTLY matches a canonical pattern
    (:func:`_classify_text_run`), in page-then-run order, each with full document/page/
    coordinate provenance. Runs that match no pattern are left unassembled — never
    coerced into a fact. Pure and deterministic: the same pages and context always yield
    byte-identical facts.
    """
    facts: list[AssembledFact] = []
    sequence = 0
    for page in pages:
        for run in page.content.text_runs:
            classified = _classify_text_run(run.text)
            if classified is None:
                continue
            sequence += 1
            member, normalized_value = classified
            facts.append(
                _build_fact(
                    page=page,
                    text=run.text,
                    member=member,
                    normalized_value=normalized_value,
                    context=context,
                    x=float(run.x),
                    y=float(run.y),
                    sequence=sequence,
                )
            )
    return tuple(facts)


# ------------------------------------------------------------- promotion evidence


@dataclass(frozen=True)
class _FactScopedHistory:
    """Adapter binding a RESOLVED correction-history result to its fact type for the
    promotion gate's structural evidence contract (``resolved is True``, no
    ``reject_code``, fact-type identity). The correction-history validator's result is
    fact-agnostic; the wiring layer scopes it to the fact it validated, exactly as the
    promotion module documents the wiring layer must (``test_promotion`` module note)."""

    fact_type: SurveyFactType
    correction_count: int

    resolved = True


def _history_evidence(
    member: SurveyFactType, result: CorrectionHistoryValidation
) -> object:
    """Fact-scope a resolved history result; pass a refusal through unchanged so the
    gate still fails closed on it."""
    if isinstance(result, ValidatedCorrectionHistory):
        return _FactScopedHistory(
            fact_type=member, correction_count=result.correction_count
        )
    return result


def _promote_fact(fact: AssembledFact) -> PromotionVerdict:
    """The deterministic promotion verdict for one assembled fact.

    Builds exactly the ``ValidationKind`` grounds the fact type REQUIRES
    (:data:`REQUIRED_VALIDATIONS`) from the validators run at assembly time, then defers
    entirely to :func:`evaluate_promotion` — the confidence-blind, fail-closed gate. A
    refused validator (unresolved value, tampered history) yields a refusal here too.
    """
    member = fact.fact_type
    required = REQUIRED_VALIDATIONS[member]
    grounds: dict[ValidationKind, tuple[object, ...]] = {}
    if ValidationKind.NORMALIZED_VALUE in required:
        grounds[ValidationKind.NORMALIZED_VALUE] = (fact.normalized_validation,)
    if ValidationKind.LOCATION in required:
        grounds[ValidationKind.LOCATION] = (fact.location_validation,)
    if ValidationKind.CORRECTION_HISTORY in required:
        grounds[ValidationKind.CORRECTION_HISTORY] = (
            _history_evidence(member, fact.history_validation),
        )
    return evaluate_promotion(
        member.value,
        grounds,
        fact.evidence["extraction_method"],
        fact.evidence["confidence"],
    )


# --------------------------------------------------------------- check wiring


def _check_entry(result: CheckResult) -> dict:
    """One ``survey_evidence.validation_results`` array entry from a typed check result.

    ``detail`` is ``None`` only on PASS (schema rule); a FAIL/UNEVALUABLE always states
    why, and the computed comparison basis is recorded so the outcome is reproducible.
    """
    if isinstance(result, CheckPassed):
        return {"check_id": result.check_name, "status": "pass", "detail": None}
    if isinstance(result, CheckFailed):
        return {
            "check_id": result.check_name,
            "status": "fail",
            "detail": (
                f"deterministic check {result.check_name!r} found a contradiction "
                f"within tolerance {result.tolerance!r}"
            ),
            "observed_value": dict(result.computed),
        }
    return {
        "check_id": result.check_name,
        "status": "unresolved",
        "detail": result.reason,
    }


def _run_document_checks(
    facts: Sequence[AssembledFact], context: SurveyExtractionContext
) -> tuple[tuple[CheckResult, ...], NeedsReviewRouting | None]:
    """Run every deterministic check that APPLIES to the assembled facts, recording each
    outcome onto the facts it covers, and derive the SB-S7 wrong-address routing.

    Only applicable checks are run (a check with no facts is simply not run — never a
    fabricated pass): ``scale_consistency`` over every resolved scale statement, and
    ``address_bbl_match`` over the resolved BBL/address facts against the stated subject
    targets. A failed/unevaluable ``address_bbl_match`` is turned into the typed
    :class:`NeedsReviewRouting` (SB-S7) via :func:`wrong_address_routing`.
    """
    results: list[CheckResult] = []
    wrong_address: NeedsReviewRouting | None = None

    scale_facts = [
        fact
        for fact in facts
        if fact.fact_type is SurveyFactType.SCALE_STATEMENT
        and isinstance(fact.normalized_validation, ValidatedScale)
    ]
    if scale_facts:
        scale_result = scale_consistency(
            [fact.normalized_validation for fact in scale_facts]
        )
        results.append(scale_result)
        entry = _check_entry(scale_result)
        for fact in scale_facts:
            fact.evidence["validation_results"].append(dict(entry))

    address_facts = [
        fact
        for fact in facts
        if fact.fact_type is SurveyFactType.ADDRESS_TEXT
        and isinstance(fact.normalized_validation, ValidatedUnitlessText)
    ]
    bbl_facts = [
        fact
        for fact in facts
        if fact.fact_type is SurveyFactType.BBL_TEXT
        and isinstance(fact.normalized_validation, ValidatedUnitlessText)
    ]
    if address_facts or bbl_facts:
        address_fact = address_facts[0] if address_facts else None
        bbl_fact = bbl_facts[0] if bbl_facts else None
        match_result = address_bbl_match(
            address_fact.normalized_validation if address_fact else None,
            bbl_fact.normalized_validation if bbl_fact else None,
            subject_address=context.subject_address,
            subject_bbl=context.subject_bbl,
        )
        results.append(match_result)
        entry = _check_entry(match_result)
        for fact in (*address_facts, *bbl_facts):
            fact.evidence["validation_results"].append(dict(entry))
        if isinstance(match_result, (CheckFailed, CheckUnevaluable)):
            wrong_address = wrong_address_routing(match_result)

    return tuple(results), wrong_address


# ----------------------------------------------------------------- the pipeline


def run_survey_extraction(
    *,
    format_identity: object,
    original_bytes: bytes,
    context: SurveyExtractionContext,
    actor: TransitionActor,
    occurred_at: datetime,
    current_state: DocumentState = DocumentState.PROCESSING,
) -> SurveyExtractionOutcome:
    """Run the full deterministic extraction pipeline for one document.

    ``current_state`` is the document's lifecycle state as the extraction job runs
    (``processing`` after the worker claimed it). Returns:

    - :class:`ExtractionNotStarted` when the isolation gate or S3 routing refused
      (``isolation_unavailable`` / deferred / rejected) — nothing decoded, no
      transition; the document rests where it is.
    - :class:`DecoderUnavailable` when a supported route has no concrete decoder yet
      (advisory raster routes) — again no decode, no transition.
    - :class:`ExtractionCompleted` otherwise, carrying the assembled facts, executed
      checks, per-fact promotion verdicts, and the authority-checked transition record.
      The document is routed to ``auto_extracted`` ONLY when there is at least one fact,
      every executed check passed, and every fact's deterministic promotion verdict is
      :class:`PromotionAllowed`; that edge is driven through the H5 gate
      (:func:`promotion_gated_transition`) with the per-fact verdicts. Any other
      state — a decode refusal, an empty extraction, a failed/unresolved check, a
      wrong-address match (SB-S7), or any unproven fact — routes the document to
      ``needs_review`` through the raw authority-checked ``transition`` (a non-gated
      edge). No AI value, confidence, or model output can move either edge.
    """
    entry = begin_extraction_job(format_identity)
    if not isinstance(entry, ExtractionJobAuthorized):
        return ExtractionNotStarted(entry_outcome=entry)
    if entry.decoder is None:
        return DecoderUnavailable(route=entry.route)

    primitives = entry.decoder.decode(original_bytes)
    refusal = pdf_decode_refusal(primitives)
    if refusal is not None:
        record = transition(
            current_state, DocumentState.NEEDS_REVIEW, actor=actor, occurred_at=occurred_at
        )
        return ExtractionCompleted(
            facts=(),
            check_results=(),
            fact_verdicts={},
            target_state=DocumentState.NEEDS_REVIEW,
            transition_record=record,
            wrong_address=None,
            decode_refusal=refusal,
        )

    pages = tuple(item for item in primitives if isinstance(item, DecodedPage))
    facts = assemble_survey_evidence(pages, context)
    check_results, wrong_address = _run_document_checks(facts, context)
    verdicts: dict[str, PromotionVerdict] = {
        fact.evidence["evidence_id"]: _promote_fact(fact) for fact in facts
    }

    every_check_passed = all(
        isinstance(result, CheckPassed) for result in check_results
    )
    every_fact_promotes = all(
        isinstance(verdict, PromotionAllowed) for verdict in verdicts.values()
    )
    auto_extract = bool(facts) and every_check_passed and every_fact_promotes

    fact_dicts = tuple(fact.evidence for fact in facts)
    if auto_extract:
        record = promotion_gated_transition(
            current_state,
            DocumentState.AUTO_EXTRACTED,
            actor=actor,
            occurred_at=occurred_at,
            material_fact_verdicts=verdicts,
        )
        return ExtractionCompleted(
            facts=fact_dicts,
            check_results=check_results,
            fact_verdicts=verdicts,
            target_state=DocumentState.AUTO_EXTRACTED,
            transition_record=record,
            wrong_address=None,
            decode_refusal=None,
        )

    record = transition(
        current_state, DocumentState.NEEDS_REVIEW, actor=actor, occurred_at=occurred_at
    )
    return ExtractionCompleted(
        facts=fact_dicts,
        check_results=check_results,
        fact_verdicts=verdicts,
        target_state=DocumentState.NEEDS_REVIEW,
        transition_record=record,
        wrong_address=wrong_address,
        decode_refusal=None,
    )
