"""Deterministic promotion gate for survey facts (application-level; M2-T015).

The last deterministic hurdle between a fact's submitted evidence and any promoted
material buildability input. :func:`evaluate_promotion` weighs ONLY the typed results
already produced by the deterministic validators —
:func:`app.documents.units.validate_normalized_value` (normalized-value/unit typing),
``geometry_validation.validate_location`` (cross-field geometry/location), and the
correction-history integrity validators — and returns a frozen typed VERDICT:
:class:`PromotionAllowed` only when every validation REQUIRED for the submitted
``fact_type`` (:data:`REQUIRED_VALIDATIONS`, one explicit entry per taxonomy member)
is present, non-empty, resolved, and consistent with that fact type; otherwise the
frozen :class:`PromotionRefused` carrying the verbatim submission and every stated
reason. The verdict is a value, deliberately never an exception, and a refusal
contains nothing downstream code could promote.

STANDALONE by design: this module reads no ingestion state and performs no promotion
itself — it only judges submitted evidence. Wiring the gate into the ingestion state
machine is a separate unit; nothing here imports or touches it.

Zero-weight rule: ``extraction_method`` and ``confidence`` are recorded verbatim into
the verdict for provenance and NOTHING else. There is deliberately no code path in
this module that reads the confidence number or branches on the extraction method: a
fact extracted by AI or OCR (``ai_assisted_classification`` and ``ocr_text``, named
in :data:`ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS`) promotes exactly when its
deterministic validations are complete and resolved — no earlier, no later — and a
confidence of ANY value never substitutes for a missing, empty, failed, unresolved,
or inconsistent validation.

Evidence contract (structural, fail-closed): the gate depends only on the taxonomy
and judges every submitted result by the shared typed-result convention of
:mod:`app.documents.taxonomy` and :mod:`app.documents.units`. A result counts as
RESOLVED only when it affirmatively exposes ``resolved is True``, exposes NO
``reject_code``, and identifies the submitted fact type (the
:class:`~app.documents.taxonomy.SurveyFactType` member itself or its exact wire
string). Every other shape — a typed refusal value, a result without the affirmative
flag, a result for a different fact type, a contradictory result claiming both, an
empty result list (a visible mid-state), an unrecognized validation kind, or any
shape the gate does not understand — fails closed to :class:`PromotionRefused`.
Unknown evidence is never weighed; it is refused visibly.
"""

from __future__ import annotations

import enum
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeGuard

from app.documents.taxonomy import (
    SurveyFactType,
    UnsupportedFactType,
    validate_fact_type,
)

__all__ = [
    "PromotionAllowed",
    "PromotionRefused",
    "PromotionVerdict",
    "REQUIRED_VALIDATIONS",
    "ValidationKind",
    "ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS",
    "evaluate_promotion",
]


@enum.unique
class ValidationKind(enum.Enum):
    """Closed set of deterministic validation families the gate can weigh.

    Each member names the validator family whose typed result it carries:

    - ``normalized_value``: :func:`app.documents.units.validate_normalized_value` —
      normalized-value shape and stated-unit typing.
    - ``location``: ``geometry_validation.validate_location`` — cross-field
      geometry/location validation.
    - ``correction_history``: the correction-history integrity validators.

    The set extends ADDITIVELY only, together with the deterministic validator that
    grounds the new member (mirroring the taxonomy's extension rule). An evidence key
    outside this set is never interpreted or guessed — it fails closed to refusal.
    """

    NORMALIZED_VALUE = "normalized_value"
    LOCATION = "location"
    CORRECTION_HISTORY = "correction_history"


#: Extraction methods the promotion requirement singles out as carrying ZERO
#: deterministic weight. Deliberately NOT consulted by :func:`evaluate_promotion` —
#: no extraction method carries deterministic weight here, because the verdict counts
#: only typed validator results. The constant exists so wiring and UI layers can
#: label AI/OCR-derived evidence without re-deriving the set.
ZERO_DETERMINISTIC_WEIGHT_EXTRACTION_METHODS: frozenset[str] = frozenset(
    {"ai_assisted_classification", "ocr_text"}
)


# ------------------------------------------------------------ required validations

_HISTORY = ValidationKind.CORRECTION_HISTORY
_NORMALIZED = ValidationKind.NORMALIZED_VALUE
_LOCATION = ValidationKind.LOCATION

#: The explicit per-fact-type authority on which validations a fact MUST carry as
#: resolved before promotion. Every taxonomy member appears exactly once, none with an
#: empty set (both guarded at import below — a member added without deciding its
#: requirement, or with no requirement at all, must fail at import, never promote on
#: no evidence at validation time).
#:
#: Grounding: every fact type with a normalized-value/unit rule
#: (:data:`app.documents.units.FACT_TYPES_WITH_UNIT_RULE`) requires that rule's
#: resolved result; ``reconstructed_boundary_polygon`` deliberately has NO unit rule —
#: :mod:`app.documents.units` routes its validity to the geometry validation path — so
#: it requires the resolved ``location`` result instead (requiring unit typing for it
#: would make it permanently unpromotable). Every fact type requires the resolved
#: correction-history integrity result: a promoted fact's (possibly empty) correction
#: history must be affirmatively intact, never assumed. The map extends ADDITIVELY
#: only — adding a required kind can only make the gate stricter, never looser.
REQUIRED_VALIDATIONS: Mapping[SurveyFactType, frozenset[ValidationKind]] = MappingProxyType(
    {
        SurveyFactType.BOUNDARY_SEGMENT_DISTANCE: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.BOUNDARY_BEARING: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.STATED_LOT_AREA: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.SCALE_STATEMENT: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.NORTH_ARROW_ORIENTATION: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.ELEVATION_VALUE: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.ADDRESS_TEXT: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.BBL_TEXT: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.COMPUTED_CLOSURE: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.CALCULATED_LOT_AREA: frozenset({_NORMALIZED, _HISTORY}),
        SurveyFactType.RECONSTRUCTED_BOUNDARY_POLYGON: frozenset({_LOCATION, _HISTORY}),
    }
)

# Additive-extension guard: a taxonomy member added without deciding its required
# validations must fail here at import, never fall through silently at gate time.
_UNGOVERNED = frozenset(SurveyFactType) - frozenset(REQUIRED_VALIDATIONS)
if _UNGOVERNED:
    raise RuntimeError(
        "every SurveyFactType member needs an explicit REQUIRED_VALIDATIONS entry; "
        "ungoverned: " + ", ".join(sorted(member.value for member in _UNGOVERNED))
    )

# Fail-closed guard: a fact type requiring NO validation would promote on no evidence.
_UNGUARDED = sorted(
    member.value for member, kinds in REQUIRED_VALIDATIONS.items() if not kinds
)
if _UNGUARDED:
    raise RuntimeError(
        "a fact type with an empty REQUIRED_VALIDATIONS set would promote on no "
        "evidence; every member must require at least one validation: "
        + ", ".join(_UNGUARDED)
    )


# ------------------------------------------------------------------ typed verdicts


@dataclass(frozen=True)
class PromotionAllowed:
    """Typed ALLOWED verdict: every required validation is present and resolved.

    ``grounds`` carries the exact typed validator results the verdict rests on, as
    ``(kind wire string, results tuple)`` pairs in :class:`ValidationKind` definition
    order — the promotion's deterministic provenance. ``submitted_extraction_method``
    and ``submitted_confidence`` are recorded verbatim (``repr`` for non-wire shapes)
    and had ZERO influence on the verdict.
    """

    fact_type: SurveyFactType
    grounds: tuple[tuple[str, tuple[object, ...]], ...]
    submitted_extraction_method: str
    submitted_confidence: str

    allowed = True
    promotable = True


@dataclass(frozen=True)
class PromotionRefused:
    """Typed refusal of promotion — a visible RESULT that contains nothing promotable.

    Deliberately a value, not a ``DocumentIngestionError`` subclass and never raised:
    incomplete, empty, failed, unresolved, inconsistent, or AI-only evidence is a
    routine fail-closed outcome the caller must handle and surface — typed rejection,
    route to review — not a crash. The result carries ONLY the verbatim submission
    (``repr`` for non-wire shapes) and the stated reasons: it has no resolved value
    and no grounds of any kind, so there is nothing downstream code could promote
    into a material buildability input. The payload is metadata only — mirroring the
    ``errors.py`` payload convention — and safe to serialize into an API response or
    audit record.
    """

    submitted_fact_type: str
    submitted_validation_results: str
    submitted_extraction_method: str
    submitted_confidence: str
    reasons: tuple[str, ...]

    allowed = False
    promotable = False
    reject_code = "promotion_refused"

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "reject_code": self.reject_code,
            "submitted_fact_type": self.submitted_fact_type,
            "submitted_validation_results": self.submitted_validation_results,
            "submitted_extraction_method": self.submitted_extraction_method,
            "submitted_confidence": self.submitted_confidence,
            "reasons": list(self.reasons),
        }


PromotionVerdict = PromotionAllowed | PromotionRefused


# ---------------------------------------------------------------------- helpers


def _refused(
    fact_type: object,
    validation_results: object,
    extraction_method: object,
    confidence: object,
    reasons: Sequence[str],
) -> PromotionRefused:
    return PromotionRefused(
        submitted_fact_type=(
            fact_type if isinstance(fact_type, str) else repr(fact_type)
        ),
        submitted_validation_results=repr(validation_results),
        submitted_extraction_method=(
            extraction_method
            if isinstance(extraction_method, str)
            else repr(extraction_method)
        ),
        submitted_confidence=repr(confidence),
        reasons=tuple(reasons),
    )


def _canonical_kind(key: object) -> ValidationKind | None:
    """The exactly identified :class:`ValidationKind`, else ``None``.

    Accepts the member itself or its exact wire string — both exactly name one
    canonical member; nothing else is trimmed, case-folded, or interpreted.
    """
    if isinstance(key, ValidationKind):
        return key
    if isinstance(key, str):
        try:
            return ValidationKind(key)
        except ValueError:
            return None
    return None


def _result_refusal(
    kind: ValidationKind, position: int, member: SurveyFactType, result: object
) -> str | None:
    """``None`` when the result is resolved and consistent, else the stated reason.

    Structural, fail-closed judgment per the module's evidence contract: only a
    result that affirmatively exposes ``resolved is True``, carries no
    ``reject_code``, and identifies the submitted fact type counts.
    """
    carries_reject_code = hasattr(result, "reject_code")
    affirms_resolved = getattr(result, "resolved", None) is True
    if carries_reject_code and affirms_resolved:
        return (
            f"result at index {position} of validation kind {kind.value!r} is "
            "internally contradictory: it claims to be resolved yet carries "
            f"reject_code {getattr(result, 'reject_code')!r}; contradictory evidence "
            "is treated as tampered and fails closed"
        )
    if carries_reject_code:
        stated = getattr(result, "reason", None)
        detail = f": {stated}" if isinstance(stated, str) else ""
        return (
            f"result at index {position} of validation kind {kind.value!r} is a typed "
            f"refusal value (reject_code={getattr(result, 'reject_code')!r}){detail}; "
            "a fact with any refused validation is never promotable"
        )
    if not affirms_resolved:
        return (
            f"result at index {position} of validation kind {kind.value!r} does not "
            "affirmatively declare itself resolved (resolved is True); unresolved or "
            "unrecognized evidence fails closed"
        )
    identified = getattr(result, "fact_type", None)
    if not (
        identified is member
        or (isinstance(identified, str) and identified == member.value)
    ):
        return (
            f"result at index {position} of validation kind {kind.value!r} identifies "
            f"fact type {identified!r}, not the submitted {member.value!r}; "
            "inconsistent evidence is treated as tampered and fails closed"
        )
    return None


def _is_results_sequence(results: object) -> TypeGuard[Sequence[object]]:
    """True when ``results`` is a real sequence of results (not text/bytes)."""
    return isinstance(results, Sequence) and not isinstance(
        results, (str, bytes, bytearray)
    )


def _results_refusals(
    kind: ValidationKind, member: SurveyFactType, results: object
) -> list[str]:
    """Every stated reason the submitted results for one kind cannot count."""
    if not _is_results_sequence(results):
        return [
            f"results for validation kind {kind.value!r} must be a list/tuple of "
            f"typed validator results, got {type(results).__name__}; unreadable "
            "evidence fails closed"
        ]
    if len(results) == 0:
        return [
            f"validation kind {kind.value!r} was submitted with an empty result list "
            "— an empty validation set is a visible mid-state and is never "
            "promotable; extraction confidence of any value never substitutes for "
            "the missing results"
        ]
    reasons: list[str] = []
    for position, result in enumerate(results):
        reason = _result_refusal(kind, position, member, result)
        if reason is not None:
            reasons.append(reason)
    return reasons


# --------------------------------------------------------------------- the gate


def evaluate_promotion(
    fact_type: str,
    validation_results: object,
    extraction_method: object,
    confidence: object,
) -> PromotionVerdict:
    """Judge one fact's submitted evidence against the deterministic promotion gate.

    ``validation_results`` is a mapping from validation kind (:class:`ValidationKind`
    member or its exact wire string) to the sequence of typed results the
    deterministic validators already produced for THIS fact. Returns
    :class:`PromotionAllowed` only when every kind in
    ``REQUIRED_VALIDATIONS[fact_type]`` is present as a non-empty sequence of
    resolved, fact-type-consistent results and every supplied result — required or
    not — is resolved and consistent; otherwise the typed
    :class:`PromotionRefused` carrying the verbatim submission and every stated
    reason. Never raises — every malformed, incomplete, empty, failed, unresolved,
    inconsistent, unknown, or AI-only submission becomes the typed refusal.

    ``extraction_method`` and ``confidence`` are recorded verbatim into the verdict
    and are read for NOTHING else: no branch in this function or its helpers
    consults either, so a confidence of any value — and any extraction method,
    including ``ai_assisted_classification`` and ``ocr_text`` — carries zero
    deterministic weight and can never substitute for a missing or failed
    validation.
    """
    fact_type_result = validate_fact_type(fact_type)
    if isinstance(fact_type_result, UnsupportedFactType):
        return _refused(
            fact_type,
            validation_results,
            extraction_method,
            confidence,
            [
                "fact_type refused by the canonical taxonomy: "
                + fact_type_result.reason
            ],
        )
    member = fact_type_result.fact_type
    required = REQUIRED_VALIDATIONS[member]

    if not isinstance(validation_results, Mapping):
        return _refused(
            fact_type,
            validation_results,
            extraction_method,
            confidence,
            [
                "validation_results must be a mapping from validation kind to the "
                "list of typed validator results, got "
                f"{type(validation_results).__name__}; the gate cannot weigh "
                "evidence it cannot read and fails closed"
            ],
        )

    reasons: list[str] = []
    supplied: dict[ValidationKind, object] = {}
    for key, value in validation_results.items():
        kind = _canonical_kind(key)
        if kind is None:
            reasons.append(
                f"unrecognized validation kind {key!r}; the gate weighs only "
                "grounded deterministic validations ("
                + ", ".join(sorted(k.value for k in ValidationKind))
                + ") and unknown evidence fails closed"
            )
            continue
        if kind in supplied:
            reasons.append(
                f"validation kind {kind.value!r} was submitted more than once "
                "(e.g. as both the enum member and the wire string); ambiguous "
                "evidence fails closed"
            )
            continue
        supplied[kind] = value

    for kind in ValidationKind:
        if kind in supplied:
            reasons.extend(_results_refusals(kind, member, supplied[kind]))
        elif kind in required:
            reasons.append(
                f"required validation {kind.value!r} for fact type {member.value!r} "
                "is absent from the submitted evidence; a fact promotes only on "
                "complete deterministic validation — extraction confidence of any "
                "value never substitutes for a missing validation"
            )

    if reasons:
        return _refused(
            fact_type, validation_results, extraction_method, confidence, reasons
        )

    grounds: list[tuple[str, tuple[object, ...]]] = []
    for kind in ValidationKind:
        if kind not in supplied:
            continue
        results = supplied[kind]
        # Always true here — every supplied kind passed the shape check above; the
        # guard narrows the type for the frozen grounds tuple.
        if _is_results_sequence(results):
            grounds.append((kind.value, tuple(results)))

    return PromotionAllowed(
        fact_type=member,
        grounds=tuple(grounds),
        submitted_extraction_method=(
            extraction_method
            if isinstance(extraction_method, str)
            else repr(extraction_method)
        ),
        submitted_confidence=repr(confidence),
    )
