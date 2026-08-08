"""Canonical closed taxonomy of survey fact types (application-level; M2-T015).

``fact_type`` is deliberately an OPEN non-empty string in the wire contract
(``packages/contracts/schemas/v1/survey_evidence.schema.json`` 1.0.0 — OPEN-WITH-FLAG,
contract section 4.3): the closed taxonomy belongs to the implementation unit that
grounds it in the deterministic checks. This module is that taxonomy. NOTHING here
changes the wire contract: the schema field stays an open string throughout v1, and
the taxonomy lands there only as a future ADDITIVE enum extension. Until then this
module is the application-level authority on which fact types the deterministic
implementation actually supports.

Fail-closed rule: an unknown, misspelled, or malformed ``fact_type`` is NEVER silently
accepted as a material buildability input. :func:`validate_fact_type` refuses it with
the typed, visible :class:`UnsupportedFactType` RESULT — a value, deliberately not an
exception — so the caller surfaces the refusal (typed rejection, route to review)
instead of crashing or silently passing. Exact match only: no trimming, case-folding,
or spelling correction is ever applied, because a silent cleanup is a silent
acceptance.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

__all__ = [
    "SUPPORTED_FACT_TYPES",
    "FactTypeValidation",
    "SupportedFactType",
    "SurveyFactType",
    "UnsupportedFactType",
    "validate_fact_type",
]


@enum.unique
class SurveyFactType(enum.Enum):
    """CANONICAL closed set of survey fact types the deterministic implementation supports.

    Member values are the exact wire strings written into ``survey_evidence.fact_type``.
    Grounding (contract = docs/SURVEY_EVIDENCE_CONTRACT.md + the 1.0.0 schema;
    architecture = docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md):

    DETECTED facts — extracted from document content by the approved per-format paths
    (contract section 4.4):

    - ``boundary_segment_distance``: "a boundary dimension" (contract section 1); named
      fact_type example (section 4.3); consumed by the ``boundary_closure``,
      ``segment_sum``, and ``contradictory_dimensions`` checks (section 4.5).
    - ``boundary_bearing``: named fact_type example (schema, section 4.3); stated
      bearings drive traverse assembly (architecture section 8.3) and the
      ``north_orientation`` cross-check against the detected north arrow (section 9).
    - ``stated_lot_area``: "a stated area" (contract section 1); named example
      (section 4.3); the EXPECTED side of ``area_vs_stated``.
    - ``scale_statement``: "a scale statement" (contract section 1); named example
      (section 4.3); validated by ``scale_consistency``.
    - ``north_arrow_orientation``: "a north-arrow orientation" (contract section 1);
      named example (section 4.3); validated by ``north_orientation``.
    - ``elevation_value``: "an elevation" (contract section 1); named example
      (section 4.3); validated by ``elevation_consistency``.
    - ``address_text``: "an address block" (contract section 1); named example
      (section 4.3); input to ``address_bbl_match`` (SB-S7).
    - ``bbl_text``: the document's detected BBL / section-block-lot text — the
      ``address_bbl_match`` check matches "the document's detected address/BBL text"
      against the target property (architecture section 9).

    DERIVED facts — emitted by deterministic geometry reconstruction with
    ``extraction_method: deterministic_geometry_reconstruction`` (architecture
    section 8.4: "computed closure, calculated area, assembled polygon" are each
    emitted as evidence records):

    - ``computed_closure``: the computed traverse closure; ``boundary_closure``
      records the gap as ``observed_value``.
    - ``calculated_lot_area``: the "calculated polygon area" (contract section 4.5
      ``observed_value`` example); the OBSERVED side of ``area_vs_stated``.
    - ``reconstructed_boundary_polygon``: the assembled polygon ("e.g. a reconstructed
      boundary polygon" — schema ``extraction_method`` description); validated by
      ``geometry_validity`` and compared read-only by ``tax_lot_geometry_comparison``
      (SB-S4).

    The set extends ADDITIVELY only, together with the deterministic code that grounds
    the new member — mirroring the ``check_id`` extension rule (contract section 4.5).
    """

    BOUNDARY_SEGMENT_DISTANCE = "boundary_segment_distance"
    BOUNDARY_BEARING = "boundary_bearing"
    STATED_LOT_AREA = "stated_lot_area"
    SCALE_STATEMENT = "scale_statement"
    NORTH_ARROW_ORIENTATION = "north_arrow_orientation"
    ELEVATION_VALUE = "elevation_value"
    ADDRESS_TEXT = "address_text"
    BBL_TEXT = "bbl_text"
    COMPUTED_CLOSURE = "computed_closure"
    CALCULATED_LOT_AREA = "calculated_lot_area"
    RECONSTRUCTED_BOUNDARY_POLYGON = "reconstructed_boundary_polygon"


#: Exact wire strings of the canonical taxonomy, for set-membership use.
SUPPORTED_FACT_TYPES: frozenset[str] = frozenset(member.value for member in SurveyFactType)


@dataclass(frozen=True)
class SupportedFactType:
    """Typed SUPPORTED outcome of :func:`validate_fact_type`.

    Carries the resolved :class:`SurveyFactType` member for the submitted wire string.
    """

    fact_type: SurveyFactType

    supported = True


@dataclass(frozen=True)
class UnsupportedFactType:
    """Typed refusal of a fact type outside the canonical taxonomy — a visible RESULT.

    Deliberately a value, not a ``DocumentIngestionError`` subclass and never raised:
    an unknown ``fact_type`` is a routine fail-closed outcome the caller must handle
    and surface, not a crash. ``submitted_fact_type`` preserves the submission
    verbatim (its ``repr`` for a non-string) and ``reason`` states why it was refused;
    the payload is metadata only — mirroring the ``errors.py`` payload convention —
    and safe to serialize into an API response or audit record.
    """

    submitted_fact_type: str
    reason: str

    supported = False
    reject_code = "unsupported_fact_type"

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "reject_code": self.reject_code,
            "submitted_fact_type": self.submitted_fact_type,
            "reason": self.reason,
        }


FactTypeValidation = SupportedFactType | UnsupportedFactType


def validate_fact_type(fact_type: str) -> FactTypeValidation:
    """Validate one wire ``fact_type`` string against the canonical taxonomy.

    Returns :class:`SupportedFactType` when ``fact_type`` is EXACTLY a canonical wire
    string, else :class:`UnsupportedFactType`. Never raises — every malformed input
    (wrong type, empty, unknown, misspelled, case- or whitespace-varying) becomes the
    typed refusal, so no unknown fact type can crash ingestion or slip through as a
    material buildability input.
    """
    if not isinstance(fact_type, str):
        return UnsupportedFactType(
            submitted_fact_type=repr(fact_type),
            reason=(
                "fact_type must be a string (the survey_evidence wire type), got "
                f"{type(fact_type).__name__}"
            ),
        )
    if not fact_type.strip():
        return UnsupportedFactType(
            submitted_fact_type=fact_type,
            reason="fact_type must be a non-empty string (contract section 4.3)",
        )
    try:
        member = SurveyFactType(fact_type)
    except ValueError:
        return UnsupportedFactType(
            submitted_fact_type=fact_type,
            reason=(
                "not a canonical supported survey fact type (exact match required; "
                "no trimming, case-folding, or spelling correction is applied)"
            ),
        )
    return SupportedFactType(fact_type=member)
