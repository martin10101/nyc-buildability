"""B7 wide-street rule wiring (M5-T034): the FIRST production consumer of the
accepted wide-street stack.

It consumes a D-052 street-width policy decision
(:mod:`app.connectors.dcm_street_width_policy`) and the B4 100-ft
buffer/intersection engine (:mod:`app.connectors.wide_street_buffer_engine`),
and produces the typed determination the ZR 23-22 conditional-FAR rule rows
consume: *is the zoning lot (or a portion of it) within 100 feet of a WIDE
street?* Only an affirmative determination lets the higher (wide-street) FAR row
fire; every other outcome keeps the conservative (lower) row or fails safe.

OWN-MODULE RULING (M4-T021 G3). This wiring lands in its OWN module; it does not
modify, split, or add wiring into ``wide_street_buffer_engine`` or
``dcm_street_width_policy``. Both producers are consumed READ-ONLY through their
public interfaces.

DECISION LOGIC (both a street-width classification AND a proximity test are
required, because footnote 1's higher FAR applies only "within 100 feet of a
WIDE street"):

* Any policy decision that is not exactly ``wide`` or ``narrow`` (i.e.
  ``unresolved`` or ``unknown``) -> ``PROFESSIONAL_REVIEW_REQUIRED``. Routing is
  NEVER keyed off :attr:`PolicyDecision.routed_to` (G3 A4 binding): the
  ``decision_state`` governs. ``routed_to`` is provenance only.
* Every relevant decision ``narrow`` -> ``NOT_WITHIN_100FT_OF_WIDE_STREET`` (the
  conservative standard row; there is no wide street to be within 100 ft of).
* At least one ``wide`` decision -> the B4 engine decides proximity:
  ``computed`` + aggregate intersects -> ``WITHIN_100FT_OF_WIDE_STREET`` (wide
  row); ``computed`` + no intersection -> ``NOT_WITHIN_100FT_OF_WIDE_STREET``
  (standard row; the wide street exists but the lot is not within 100 ft);
  any typed engine failure (CRS, invalid geometry, malformed attestation, the
  new input-bounds guard), an unattested EC-5 precondition, or a
  no-wide-segments result that contradicts a ``wide`` policy decision ->
  ``PROFESSIONAL_REVIEW_REQUIRED``. A guessed ``wide`` is never emitted.

D-051 FALLBACK DIRECTION (validated for THESE rows, not asserted universally).
On any uncertainty this module withholds the higher wide-street FAR and lets the
conservative (LOWER) row govern (or fails safe to professional review). For ZR
23-22 the wide-street value is the HIGHER FAR (R6 3.00 vs 2.20; R7-1/R7-2 4.00 vs
3.44; R8 7.20 vs 6.02), so withholding it on uncertainty can never OVERSTATE
buildable floor area - overstating one of these lots is the single worst output
this family can produce (rule note ``wide_street_far_alternative``). Fail-closed
here therefore means fail-closed-to-lower-FAR, which is the conservative
direction FOR THIS RULE. Per D-051 each consuming rule validates its own
direction; this is not a universal "narrow is always safe" claim (cf. the ZR
23-431 street-wall counterexample where narrow is the LARGER value).

exceptions_checked ELEVATED criterion (M4-T021 G3 A1). ``exceptions_checked`` is
reported True ONLY when the applicable zoning exceptions were checked AND every
applicable one is either inapplicable or resolved. The ZR 12-10 2-row
named-street override table (Broadway W94-97 CD7; Allen St Rivington-Delancey
CD3) IS consulted here - :func:`build_named_street_override_status` (extracted to
:mod:`app.rules.named_street_override_status`) runs the accepted matcher over the
candidate segments. A candidate segment the matcher could not resolve (missing
community district or cross-street bounds, or an indeterminate locator) can
therefore never be reported ``exceptions_checked=True``, and such a lot fails safe
to professional review rather than claiming a wide determination on an unresolved
exception (AS-4). A DEFINITIVE match is a qualified-legal determination whose
designated-wide value is never applied numerically (M5-T039 ruling; the
C5-3/C6-4/C6-6 alternate-width value stays in the G6 legal queue) - it too forces
professional review.

DRAFT-until-G6 (D-045-R009). Every determination carries the DRAFT marker and the
D-052 provenance quintuple (original label, source version, matched geometry
reference, interpreted bounds, classification reason) aggregated from the policy
decisions it rests on. Nothing here is published, Verified, or a final legal
determination; the rule stays ``needs_review`` pending G6 qualified-human
approval (Section 20 hard stop unchanged).

Deterministic, side-effect-free, network-free. No AI, no legal interpretation.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.connectors.dcm_street_width_policy import (
    DECISION_NARROW,
    DECISION_WIDE,
    PolicyDecision,
)
from app.connectors.wide_street_buffer_engine import (
    STATUS_COMPUTED,
    STATUS_NO_WIDE_SEGMENTS_PROVIDED,
    STATUS_PRECONDITIONS_NOT_ATTESTED,
    AttestedLotPolygon,
    AttestedWideSegment,
    Ec5AttestedPreconditions,
    WideStreetBufferEngineError,
    WideStreetBufferResult,
    compute_wide_street_buffer_intersection,
)
from app.rules.named_street_override_status import (
    MatchedNamedStreetOverride,
    NamedStreetOverrideStatus,
    build_named_street_override_status,
)

__all__ = [
    "DETERMINATION_NOT_WITHIN_WIDE",
    "DETERMINATION_PROFESSIONAL_REVIEW",
    "DETERMINATION_WITHIN_WIDE",
    "DRAFT_LABEL_NOTICE",
    "FALLBACK_DIRECTION_NOTICE",
    "FAR_ROW_NONE",
    "FAR_ROW_STANDARD",
    "FAR_ROW_WIDE_STREET",
    "ROUTED_TO_NOT_USED_NOTICE",
    "COVERAGE_CONDITIONAL",
    "COVERAGE_PROFESSIONAL_REVIEW_REQUIRED",
    "MatchedNamedStreetOverride",
    "NamedStreetOverrideStatus",
    "WideStreetDetermination",
    "build_named_street_override_status",
    "determine_wide_street_far",
    "select_far_row_value",
]

# ---------------------------------------------------------------------------
# Determination states. WITHIN/NOT_WITHIN are the two confident DRAFT outcomes;
# PROFESSIONAL_REVIEW is the honest fail-safe. Never collapsed into each other.
# ---------------------------------------------------------------------------
DETERMINATION_WITHIN_WIDE = "within_100ft_of_wide_street"
DETERMINATION_NOT_WITHIN_WIDE = "not_within_100ft_of_wide_street"
DETERMINATION_PROFESSIONAL_REVIEW = "professional_review_required"

# Which conditional-FAR row the determination lets fire. FAR_ROW_NONE means no
# row fires and NO FAR bonus is granted (professional review).
FAR_ROW_WIDE_STREET = "wide_street_row"
FAR_ROW_STANDARD = "standard_row"
FAR_ROW_NONE = "none"

# Draft-rule coverage vocabulary this module hands to the integration layer. A
# draft determination tops out at conditional (never verified, D-045-R009);
# uncertainty is professional_review_required. These match the canonical
# coverage strings used by app.rules.coverage without importing it (this module
# never evaluates the rule; it only labels the determination).
COVERAGE_CONDITIONAL = "conditional"
COVERAGE_PROFESSIONAL_REVIEW_REQUIRED = "professional_review_required"

DRAFT_LABEL_NOTICE = (
    "DRAFT - not a Verified determination (D-045-R009). This wide-street "
    "determination feeds a needs_review draft rule and is subject to G6 "
    "qualified-human legal review before any published/production use; the "
    "higher wide-street FAR is never a final result here."
)

ROUTED_TO_NOT_USED_NOTICE = (
    "Routing is keyed off PolicyDecision.decision_state, never off "
    "PolicyDecision.routed_to (M4-T021 G3 A4). routed_to is carried as "
    "provenance only; an unknown/unresolved decision_state fails safe to "
    "professional review regardless of any routed_to value."
)

FALLBACK_DIRECTION_NOTICE = (
    "D-051 fallback direction (validated for the ZR 23-22 conditional-FAR "
    "rows only): on uncertainty the higher wide-street FAR is withheld and the "
    "conservative LOWER-FAR row governs (or the result fails safe to "
    "professional review). Because the wide-street value is the HIGHER FAR for "
    "these districts, withholding it can never overstate buildable floor area. "
    "This is not a universal 'narrow is always conservative' claim - each "
    "consuming rule validates its own direction (D-051)."
)


@dataclass(frozen=True)
class WideStreetDetermination:
    """One lot's typed wide-street determination for the ZR 23-22 conditional-FAR
    rows. ``far_row`` names which row may fire; ``coverage_hint`` is the draft
    coverage the integration layer should honor. The provenance tuples carry the
    D-052 quintuple aggregated from every policy decision this rests on (empty
    tuples only when no decision was supplied). Every buffer field is None unless
    the B4 engine actually ran and returned a computed result."""

    determination_state: str
    far_row: str
    coverage_hint: str
    exceptions_checked: bool
    named_street_override_pending: bool
    reason: str
    # D-052 provenance quintuple, aggregated across the supplied decisions.
    policy_decision_states: tuple[str, ...]
    original_labels: tuple[str | None, ...]
    source_versions: tuple[str | None, ...]
    matched_geometry_refs: tuple[str | None, ...]
    interpreted_bounds_summaries: tuple[str, ...]
    classification_reasons: tuple[str, ...]
    # B4 engine facts (None unless the engine ran and returned a result).
    buffer_status: str | None
    aggregate_intersects: bool | None
    aggregate_area_sq_ft: float | None
    lot_identity: str | None
    draft_label: str
    routed_to_note: str
    fallback_direction_note: str
    # Set (non-None) ONLY on a determination refused because a candidate segment
    # DEFINITIVELY matched a ZR 12-10 named-street override; carries the distinct
    # override provenance (M5-T040). None on every other determination. This is an
    # internal field for reviewers/consumers; it is NOT part of the frozen
    # rule_evaluation contract (integration._wide_street_summary does not read it),
    # so the override provenance also rides in ``reason`` for the wire surface.
    named_street_override_match: MatchedNamedStreetOverride | None = None


def _provenance(decisions: Sequence[PolicyDecision]) -> dict:
    """Aggregate the D-052 provenance quintuple across the supplied decisions,
    preserving order and never deduplicating (each decision's provenance is
    kept individually so a reviewer can trace every segment)."""
    return {
        "policy_decision_states": tuple(d.decision_state for d in decisions),
        "original_labels": tuple(d.original_label for d in decisions),
        "source_versions": tuple(d.source_version for d in decisions),
        "matched_geometry_refs": tuple(d.matched_geometry_ref for d in decisions),
        "interpreted_bounds_summaries": tuple(
            d.interpreted_bounds.interval_description for d in decisions
        ),
        "classification_reasons": tuple(d.classification_reason for d in decisions),
    }


def _elevated_exceptions_checked(
    decisions: Sequence[PolicyDecision],
    named_street_override: NamedStreetOverrideStatus,
) -> bool:
    """The M4-T021 G3 A1 ELEVATED criterion. True only when the named-street
    override / alternate-width exceptions are fully resolved AND every supplied
    decision is a confident wide/narrow classification.

    A ``wide``/``narrow`` decision_state already implies the D-052
    ``exceptions_checked`` attestation held (the policy module returns
    ``unresolved`` otherwise), but the elevated criterion is stricter: a status
    whose override table was not fully applied/resolved
    (``override_table_implemented`` False), a DEFINITIVE named-street override
    match, or an empty decision set all mean the exceptions are not fully resolved
    for a confident determination, so this returns False even when the caller
    attested a check."""
    if named_street_override.matched_override is not None:
        return False
    # DB-028(c): the safe attestation path REQUIRES the matcher to have fully
    # applied and resolved the override table (override_table_implemented=True). A
    # status whose override table was not fully applied can never clear the
    # elevated criterion - this rejects a hand-built may_touch=False/
    # implemented=False status that the old boolean pair let slip through
    # (attestation only tightens, never loosens;
    # build_named_street_override_status never emits that shape).
    if not named_street_override.override_table_implemented:
        return False
    # DB-028(d): with no supplied decisions there is nothing to attest, so the
    # empty case is explicitly False - never the vacuous all(()) -> True that let
    # the no-policy-decisions professional-review branch read exceptions_checked=True.
    return bool(decisions) and all(
        d.decision_state in (DECISION_WIDE, DECISION_NARROW) for d in decisions
    )


def _determination(
    *,
    determination_state: str,
    far_row: str,
    coverage_hint: str,
    exceptions_checked: bool,
    named_street_override_pending: bool,
    reason: str,
    decisions: Sequence[PolicyDecision],
    buffer_result: WideStreetBufferResult | None,
    lot_identity: str | None,
    named_street_override_match: MatchedNamedStreetOverride | None = None,
) -> WideStreetDetermination:
    prov = _provenance(decisions)
    return WideStreetDetermination(
        determination_state=determination_state,
        far_row=far_row,
        coverage_hint=coverage_hint,
        exceptions_checked=exceptions_checked,
        named_street_override_pending=named_street_override_pending,
        reason=reason,
        policy_decision_states=prov["policy_decision_states"],
        original_labels=prov["original_labels"],
        source_versions=prov["source_versions"],
        matched_geometry_refs=prov["matched_geometry_refs"],
        interpreted_bounds_summaries=prov["interpreted_bounds_summaries"],
        classification_reasons=prov["classification_reasons"],
        buffer_status=(buffer_result.status if buffer_result is not None else None),
        aggregate_intersects=(
            buffer_result.aggregate_intersects if buffer_result is not None else None
        ),
        aggregate_area_sq_ft=(
            buffer_result.aggregate_area_sq_ft if buffer_result is not None else None
        ),
        lot_identity=lot_identity,
        draft_label=DRAFT_LABEL_NOTICE,
        routed_to_note=ROUTED_TO_NOT_USED_NOTICE,
        fallback_direction_note=FALLBACK_DIRECTION_NOTICE,
        named_street_override_match=named_street_override_match,
    )


def determine_wide_street_far(
    policy_decisions: Sequence[PolicyDecision],
    *,
    lot: AttestedLotPolygon,
    wide_segments: Sequence[AttestedWideSegment],
    ec5_preconditions: Ec5AttestedPreconditions,
    named_street_override: NamedStreetOverrideStatus,
    correlation_id: str,
) -> WideStreetDetermination:
    """Produce the typed wide-street determination for one lot.

    ``policy_decisions`` are the D-052 width policy decisions for the candidate
    street segments near the lot (BEFORE wide-filtering - so unknown/unresolved
    segments are visible here and force honest professional review).
    ``wide_segments`` are the already-wide-disposed segments the B4 engine
    buffers (the caller filters these from the wide decisions; this module never
    re-classifies width). This function never raises for a bad geometry/CRS/bound
    input: it maps every typed B4 engine failure to a professional-review
    determination."""
    # DB-028(c): the override exception is "pending" (unresolved) whenever the
    # matcher did not fully apply/resolve the table for this determination - the
    # not-pending safe path REQUIRES override_table_implemented=True. A hand-built
    # may_touch=False/implemented=False status therefore no longer reads as cleared
    # (build_named_street_override_status never emits that shape; this only tightens
    # the inconsistent hand-built case, and attestation may only get stricter here).
    named_pending = not named_street_override.override_table_implemented
    exceptions_checked = _elevated_exceptions_checked(policy_decisions, named_street_override)

    # 0. A DEFINITIVE named-street override match is decisive and preempts the
    #    width branches: the designation makes the street WIDE by legal
    #    determination regardless of its numeric width classification, so a matched
    #    override on an otherwise-narrow-classified segment must NOT fire the
    #    standard row. The designated-wide value is a qualified-legal question
    #    (M5-T039 ruling) - never applied numerically here - so the outcome is
    #    professional review carrying the distinct override provenance (AS-4).
    if named_street_override.matched_override is not None:
        return _determination(
            determination_state=DETERMINATION_PROFESSIONAL_REVIEW,
            far_row=FAR_ROW_NONE,
            coverage_hint=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            exceptions_checked=False,
            named_street_override_pending=True,
            reason=named_street_override.matched_override.reason,
            decisions=policy_decisions,
            buffer_result=None,
            lot_identity=lot.lot_identity,
            named_street_override_match=named_street_override.matched_override,
        )

    # 1. Nothing to assess -> professional review (never a silent narrow/wide).
    if not policy_decisions:
        return _determination(
            determination_state=DETERMINATION_PROFESSIONAL_REVIEW,
            far_row=FAR_ROW_NONE,
            coverage_hint=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            exceptions_checked=exceptions_checked,
            named_street_override_pending=named_pending,
            reason=(
                "no street-width policy decisions were supplied for this lot; the "
                "wide-street condition is unknown and the higher FAR is withheld - "
                "professional review required"
            ),
            decisions=policy_decisions,
            buffer_result=None,
            lot_identity=lot.lot_identity,
        )

    # 2. Any non-{wide,narrow} decision_state -> professional review. Keyed off
    #    decision_state, NEVER routed_to (G3 A4).
    unclassified = [
        d.decision_state
        for d in policy_decisions
        if d.decision_state not in (DECISION_WIDE, DECISION_NARROW)
    ]
    if unclassified:
        return _determination(
            determination_state=DETERMINATION_PROFESSIONAL_REVIEW,
            far_row=FAR_ROW_NONE,
            coverage_hint=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            exceptions_checked=exceptions_checked,
            named_street_override_pending=named_pending,
            reason=(
                "street width is not classified for "
                f"{len(unclassified)} of {len(policy_decisions)} candidate "
                f"segment(s) (decision_state(s) {sorted(set(unclassified))}); the "
                "wide-street condition cannot be determined, so the higher FAR is "
                "withheld - professional review required (decision keyed off "
                "decision_state, not routed_to)"
            ),
            decisions=policy_decisions,
            buffer_result=None,
            lot_identity=lot.lot_identity,
        )

    # 3. Every decision narrow -> no wide street near this lot -> standard row.
    if all(d.decision_state == DECISION_NARROW for d in policy_decisions):
        return _determination(
            determination_state=DETERMINATION_NOT_WITHIN_WIDE,
            far_row=FAR_ROW_STANDARD,
            coverage_hint=COVERAGE_CONDITIONAL,
            exceptions_checked=exceptions_checked,
            named_street_override_pending=named_pending,
            reason=(
                "every candidate street segment is classified narrow; there is no "
                "wide street for the lot to be within 100 ft of, so the "
                "conservative standard-row FAR governs (D-051 fallback direction)"
            ),
            decisions=policy_decisions,
            buffer_result=None,
            lot_identity=lot.lot_identity,
        )

    # 4. At least one wide decision. An unresolved named-street override - the
    #    matcher was consulted but could not clear or match the candidate segment -
    #    blocks a confident wide determination (AS-4).
    if named_pending:
        return _determination(
            determination_state=DETERMINATION_PROFESSIONAL_REVIEW,
            far_row=FAR_ROW_NONE,
            coverage_hint=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            exceptions_checked=False,
            named_street_override_pending=True,
            reason=(
                "a candidate segment may fall under the ZR 12-10 named-street "
                "override / C5-3/C6-4/C6-6 alternate-width table (Broadway W94-97 "
                "CD7; Allen St Rivington-Delancey CD3): the named-street override "
                "matcher was consulted but could not resolve the candidate segment "
                "(missing community district or cross-street bounds, or an "
                "indeterminate locator), so the override exception is unresolved; "
                "exceptions_checked cannot be asserted and the wide-street FAR is "
                "withheld - professional review required"
            ),
            decisions=policy_decisions,
            buffer_result=None,
            lot_identity=lot.lot_identity,
        )

    # 4b. Proximity is decided by the B4 engine. Every typed engine failure maps
    #     to professional review; a guessed 'wide' is never emitted.
    try:
        buffer_result = compute_wide_street_buffer_intersection(
            lot, wide_segments, ec5_preconditions=ec5_preconditions, correlation_id=correlation_id
        )
    except WideStreetBufferEngineError as exc:
        return _determination(
            determination_state=DETERMINATION_PROFESSIONAL_REVIEW,
            far_row=FAR_ROW_NONE,
            coverage_hint=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            exceptions_checked=exceptions_checked,
            named_street_override_pending=named_pending,
            reason=(
                "the B4 buffer engine refused the input with a typed failure "
                f"({exc.error_type}: {exc.message}); the wide-street proximity "
                "cannot be computed, so the higher FAR is withheld - professional "
                "review required"
            ),
            decisions=policy_decisions,
            buffer_result=None,
            lot_identity=lot.lot_identity,
        )

    if buffer_result.status == STATUS_COMPUTED:
        if buffer_result.aggregate_intersects:
            return _determination(
                determination_state=DETERMINATION_WITHIN_WIDE,
                far_row=FAR_ROW_WIDE_STREET,
                coverage_hint=COVERAGE_CONDITIONAL,
                exceptions_checked=exceptions_checked,
                named_street_override_pending=named_pending,
                reason=(
                    "at least one street is classified wide and the lot is within "
                    "100 ft of it (B4 aggregate intersects); the wide-street "
                    "conditional-FAR row applies (DRAFT, pending G6)"
                ),
                decisions=policy_decisions,
                buffer_result=buffer_result,
                lot_identity=lot.lot_identity,
            )
        return _determination(
            determination_state=DETERMINATION_NOT_WITHIN_WIDE,
            far_row=FAR_ROW_STANDARD,
            coverage_hint=COVERAGE_CONDITIONAL,
            exceptions_checked=exceptions_checked,
            named_street_override_pending=named_pending,
            reason=(
                "a wide street exists but the lot is NOT within 100 ft of it (B4 "
                "aggregate does not intersect); the conservative standard-row FAR "
                "governs (D-051 fallback direction)"
            ),
            decisions=policy_decisions,
            buffer_result=buffer_result,
            lot_identity=lot.lot_identity,
        )

    # 4c. A wide decision but the engine did not compute a proximity result:
    #     unattested EC-5 preconditions, or a no-wide-segments result that
    #     contradicts the wide policy decision -> professional review.
    if buffer_result.status == STATUS_NO_WIDE_SEGMENTS_PROVIDED:
        detail = (
            "a segment was classified wide by policy but no wide segment reached "
            "the B4 engine (inconsistent input)"
        )
    elif buffer_result.status == STATUS_PRECONDITIONS_NOT_ATTESTED:
        detail = "the B4 EC-5 named-street/alternate-width preconditions are not attested"
    else:
        detail = f"the B4 engine returned a non-computed status {buffer_result.status!r}"
    return _determination(
        determination_state=DETERMINATION_PROFESSIONAL_REVIEW,
        far_row=FAR_ROW_NONE,
        coverage_hint=COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
        exceptions_checked=exceptions_checked,
        named_street_override_pending=named_pending,
        reason=(
            f"{detail}; the wide-street proximity cannot be confidently "
            "determined, so the higher FAR is withheld - professional review "
            "required"
        ),
        decisions=policy_decisions,
        buffer_result=buffer_result,
        lot_identity=lot.lot_identity,
    )


def select_far_row_value(
    determination: WideStreetDetermination,
    *,
    standard_far: float,
    wide_street_far: float,
) -> float | None:
    """Select the FAR the determination lets fire, given the district's two
    candidate values (the caller reads these from the rule's
    ``standard_far_by_district`` / ``wide_street_far_by_district`` params - this
    module never hard-codes a FAR). Returns the wide-street (higher) value ONLY
    for a ``WITHIN_WIDE`` determination; the standard (lower) value for
    ``NOT_WITHIN_WIDE``; and None when no row fires (professional review) so no
    FAR bonus is ever granted on uncertainty."""
    if determination.far_row == FAR_ROW_WIDE_STREET:
        return wide_street_far
    if determination.far_row == FAR_ROW_STANDARD:
        return standard_far
    return None
