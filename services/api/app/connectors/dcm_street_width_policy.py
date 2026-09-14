"""Pure policy layer over the accepted DCM Streetwidth classifier
(task M4-T019, owner directive D-052 - ``project-control/directives/
D-052-street-width-draft-classification/source-001.md``). This module never
re-parses the raw DCM text itself - it consumes the accepted, byte-immutable
:mod:`app.connectors.dcm_street_width_classifier` output (the 24 typed
``ambiguity_class`` values) and decides the DRAFT wide/narrow policy question
the classifier deliberately leaves open (OQ-3).

THE POLICY (the owner's own words, D-052 requirements R001-R007):

- R001 ordinary threshold: below 75 ft is narrow; exactly 75 ft or above is
  wide. Applicable zoning exceptions (ZR 12-10 alternate-width / named-street
  provisions et al.) must be checked BEFORE a final classification issues; an
  applicable exception that this module does not implement leaves the
  classification UNRESOLVED - it is never silently thresholded.
- R002 draft source authorization: a clear number or recognized explicit
  bound from a CORRECTLY MATCHED DCM feature may be used for DRAFT purposes,
  subject to documented-source, street-status, and frontage-coverage checks.
  This is recorded as an owner-approved ASSUMPTION about the annotation's
  applicability - never a verified DCP guarantee. A bare nearest-centerline
  match is INSUFFICIENT frontage coverage on its own.
- R003 one-sided-bound rule: classification issues only when every value the
  accepted reading permits falls on the same side of 75 ft. ``<75`` supports
  narrow; ``>75``, ``>=75``, ``75-90`` support wide; ``<=75``, ``60-75``,
  ``70-80`` remain UNRESOLVED (they straddle the threshold).
- R004 forbidden moves: approximations, probabilistic wording, conflicting
  records, unclear coverage, and unrecognized text stay UNKNOWN and route to
  map resolution. This module never invents a tolerance, averages varying
  widths, rounds across the threshold, or silently picks one range endpoint.
- R005 provenance: every decision (including a refusal) preserves the
  original label text, source version, matched geometry reference,
  interpreted bounds, and the classification reason.
- R006 (reaffirms D-051-R002/R003): UNKNOWN is the underlying data state this
  module EMITS. It is never converted into a fallback classification here;
  each consuming rule justifies its own fallback (or stays not-assessed).
- R007: all outputs carry a DRAFT-until-G6 marker (Section 20 hard stop
  unchanged - qualified legal review governs publication).

This module is intentionally narrow: geometry matching (collecting every
touching feature and establishing frontage coverage) is later B3/B4 work.
Here, the caller ATTESTS to having done those checks via
:class:`AttestedPreconditions` - a bare boolean cannot silently satisfy a
precondition; every field is required with no default, and an unrecognized
or missing ``frontage_match_method`` fails closed exactly like the
``nearest_centerline_only`` refusal case.

Deterministic, side-effect-free, network-free code. No AI, no legal
interpretation - this module answers "does the owner's DRAFT policy license a
classification here", never "what should a consuming rule do about it".
"""

from __future__ import annotations

from dataclasses import dataclass

from app.connectors.dcm_street_width_classifier import (
    AMBIGUITY_CLASS_DISPOSITIONS,
    WIDE_THRESHOLD_FT,
    WidthClassification,
)

__all__ = [
    "DECISION_WIDE",
    "DECISION_NARROW",
    "DECISION_UNRESOLVED",
    "DECISION_UNKNOWN",
    "FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY",
    "FRONTAGE_MATCH_COVERAGE_ESTABLISHED",
    "ROUTED_TO_MAP_RESOLUTION",
    "DRAFT_LABEL_NOTICE",
    "OWNER_APPROVED_ASSUMPTION_NOTICE",
    "AttestedPreconditions",
    "InterpretedBounds",
    "PolicyDecision",
    "CLASS_INTERPRETED_BOUNDS",
    "classify_street_width_policy",
]

# ---------------------------------------------------------------------------
# Decision states. Four distinct states, never collapsed into each other
# (D-052-R006 / D-051-R002): UNRESOLVED is a policy refusal (a missing
# precondition, or a straddling one-sided-bound test); UNKNOWN is the
# classifier's own data-ambiguity state, unchanged, routed onward.
# ---------------------------------------------------------------------------
DECISION_WIDE = "wide"
DECISION_NARROW = "narrow"
DECISION_UNRESOLVED = "unresolved"
DECISION_UNKNOWN = "unknown"

# Frontage-coverage attestation values (D-052-R002). Only the exact value
# COVERAGE_ESTABLISHED satisfies the precondition; NEAREST_CENTERLINE_ONLY is
# the owner's explicit refusal case, and any other/unrecognized value also
# fails closed (never guessed into satisfied).
FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY = "nearest_centerline_only"
FRONTAGE_MATCH_COVERAGE_ESTABLISHED = "coverage_established"

ROUTED_TO_MAP_RESOLUTION = "map_resolution"

DRAFT_LABEL_NOTICE = (
    "DRAFT - subject to qualified-reviewer G6 legal review before any "
    "published/production use (D-052-R007); this is not a final "
    "determination."
)

OWNER_APPROVED_ASSUMPTION_NOTICE = (
    "Owner-approved DRAFT ASSUMPTION (D-052-R002): a clear number or "
    "recognized explicit bound from the correctly matched DCM feature was "
    "used, subject to documented-source, street-status, and frontage-"
    "coverage attestations. This is an assumption about the annotation's "
    "applicability - never a verified NYC DCP guarantee."
)


@dataclass(frozen=True)
class AttestedPreconditions:
    """Caller attestations required before this module will issue ANY
    classification (D-052-R001/R002). Every field is required with NO
    default - a caller must explicitly assert each check; nothing here can
    silently default to satisfied.

    ``source_documented`` - the DCM data source and its version are on
    record for this call (paired with ``source_version`` below).
    ``street_status_checked`` - the segment's mapped/paper-street status was
    checked (a currently-mapped-street precondition, kept separate from the
    width read itself).
    ``frontage_match_method`` - one of :data:`FRONTAGE_MATCH_COVERAGE_ESTABLISHED`
    (every touching feature was collected and frontage coverage was
    established) or :data:`FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY` (a bare
    nearest-centerline match - INSUFFICIENT per R002). Any other string is
    also treated as insufficient (fail closed on an unrecognized method).
    ``exceptions_checked`` - the applicable zoning exceptions (ZR 12-10
    alternate-width / named-street provisions et al.) were checked for this
    segment (R001); absent or false, the classification stays UNRESOLVED.
    ``source_version`` / ``matched_geometry_ref`` are carried through purely
    as provenance (R005) - they do not themselves gate the decision.
    """

    source_documented: bool
    source_version: str | None
    street_status_checked: bool
    frontage_match_method: str
    matched_geometry_ref: str | None
    exceptions_checked: bool


@dataclass(frozen=True)
class InterpretedBounds:
    """The accepted reading's interval relative to the 75 ft threshold, per
    D-052-R003. ``derivable`` is False when the classifier's ambiguity_class
    carries no coherent interval at all (approximations, labelled
    non-answers, unrecognized text, schema-drift/negative anomalies -
    D-052-R004). ``one_sided`` is only meaningful when ``derivable`` is True:
    True means every value the interval permits sits on one side of 75 ft
    (``side`` names that side); False means the interval straddles 75 ft."""

    derivable: bool
    one_sided: bool | None
    side: str | None
    interval_description: str


@dataclass(frozen=True)
class PolicyDecision:
    """One D-052 policy decision (or refusal). Carries the full provenance
    quintuple (D-052-R005): ``original_label``, ``source_version``,
    ``matched_geometry_ref``, ``interpreted_bounds``, and
    ``classification_reason``. ``assumption_notice`` is populated ONLY when
    ``decision_state`` is wide/narrow (an issued classification) - a refusal
    (UNRESOLVED) or a data-ambiguity state (UNKNOWN) makes no applicability
    assumption to caveat. ``routed_to`` is set to
    :data:`ROUTED_TO_MAP_RESOLUTION` only for UNKNOWN (D-052-R004);
    UNRESOLVED refusals are not routed anywhere - they are a policy gate,
    not a data-ambiguity state. ``draft_label`` is always populated
    (D-052-R007)."""

    decision_state: str
    original_label: str | None
    ambiguity_class: str
    source_version: str | None
    matched_geometry_ref: str | None
    interpreted_bounds: InterpretedBounds
    classification_reason: str
    routed_to: str | None
    assumption_notice: str | None
    draft_label: str


def _bounds(
    derivable: bool,
    one_sided: bool | None,
    side: str | None,
    interval_description: str,
) -> InterpretedBounds:
    return InterpretedBounds(
        derivable=derivable, one_sided=one_sided, side=side,
        interval_description=interval_description,
    )


_T = WIDE_THRESHOLD_FT  # 75.0 - referenced so the interval text never drifts
_UNDERIVABLE = "no coherent interval can be read from this value"

# Per-class interpreted-bounds table, built from the accepted classifier's
# 24 typed classes (its AMBIGUITY_CLASS_DISPOSITIONS table + docstring) -
# NOT by re-parsing the raw text a second time. Each row documents whether a
# bound is derivable at all and, if so, whether the accepted reading is
# one-sided of the 75 ft threshold (D-052-R003). Exhaustiveness against the
# classifier's own table is asserted below and re-checked by the test suite.
CLASS_INTERPRETED_BOUNDS: dict[str, InterpretedBounds] = {
    # -- Derivable, one-sided (wide side) --------------------------------
    "clean_numeric_ge_75": _bounds(
        True, True, DECISION_WIDE,
        f"single value >= {_T:g} ft (wide side)",
    ),
    "range_both_endpoints_ge_75": _bounds(
        True, True, DECISION_WIDE,
        f"range with both endpoints >= {_T:g} ft (wide side)",
    ),
    "gt_inequality_ge_75": _bounds(
        True, True, DECISION_WIDE,
        f"one-sided lower bound >= {_T:g} ft: [bound, +infinity) with the "
        f"bound itself >= {_T:g} ft (wide side)",
    ),
    # -- Derivable, one-sided (narrow side) -------------------------------
    "clean_numeric_lt_75": _bounds(
        True, True, DECISION_NARROW,
        f"single value < {_T:g} ft (narrow side)",
    ),
    "range_both_endpoints_lt_75": _bounds(
        True, True, DECISION_NARROW,
        f"range with both endpoints < {_T:g} ft (narrow side)",
    ),
    "lt_inequality_at_or_below_75_confident_narrow": _bounds(
        True, True, DECISION_NARROW,
        f"strict upper bound <= {_T:g} ft: (-infinity, bound) entirely below "
        f"{_T:g} ft (narrow side)",
    ),
    "le_inequality_below_75_confident_narrow": _bounds(
        True, True, DECISION_NARROW,
        f"inclusive upper bound < {_T:g} ft: (-infinity, bound] entirely "
        f"below {_T:g} ft (narrow side)",
    ),
    # -- Derivable, straddling (NOT one-sided) ----------------------------
    "range_straddles_cutoff": _bounds(
        True, False, None,
        f"range straddles the {_T:g} ft threshold (lower endpoint below, "
        "upper endpoint at or above)",
    ),
    "gt_inequality_below_75_ambiguous": _bounds(
        True, False, None,
        f"one-sided lower bound < {_T:g} ft: [bound, +infinity) straddles "
        "the threshold",
    ),
    "lt_inequality_above_75_ambiguous": _bounds(
        True, False, None,
        f"strict upper bound > {_T:g} ft: (-infinity, bound) straddles the "
        "threshold",
    ),
    "le_inequality_at_or_above_75_ambiguous": _bounds(
        True, False, None,
        f"inclusive upper bound >= {_T:g} ft: (-infinity, bound] straddles "
        "the threshold",
    ),
    # -- Not derivable (no coherent interval at all) ----------------------
    "range_order_unexpected": _bounds(
        False, None, None,
        f"range endpoints are out of the expected ascending order; {_UNDERIVABLE}",
    ),
    "approximate_or_hedged_value_ambiguous": _bounds(
        False, None, None,
        f"value carries an approximation/hedge marker (not a mathematical "
        f"entailment); {_UNDERIVABLE}",
    ),
    "width_irregular": _bounds(
        False, None, None,
        f"labelled non-answer 'Width Irregular' (no single width); {_UNDERIVABLE}",
    ),
    "varies": _bounds(
        False, None, None,
        f"labelled non-answer 'varies' (no single width); {_UNDERIVABLE}",
    ),
    "not_applicable_n_a": _bounds(
        False, None, None,
        f"labelled non-answer 'n/a' (no width data present); {_UNDERIVABLE}",
    ),
    "unknown_no_qualifier": _bounds(
        False, None, None,
        f"bare 'Unknown' label (no width data present); {_UNDERIVABLE}",
    ),
    "unknown_hedged_below_75": _bounds(
        False, None, None,
        f"hedge 'Unknown but <{_T:g}' (prose, not a mathematical "
        f"entailment); {_UNDERIVABLE}",
    ),
    "unknown_hedged_above_75": _bounds(
        False, None, None,
        f"hedge 'Unknown but >{_T:g}' (prose, not a mathematical "
        f"entailment); {_UNDERIVABLE}",
    ),
    "regular_but_unknown": _bounds(
        False, None, None,
        f"labelled non-answer 'Regular but unknown.' (no width data present); "
        f"{_UNDERIVABLE}",
    ),
    "empty_or_missing": _bounds(
        False, None, None,
        f"value is missing/empty (no width data present); {_UNDERIVABLE}",
    ),
    "unexpected_type": _bounds(
        False, None, None,
        f"value was not a string as documented (schema-drift signal); {_UNDERIVABLE}",
    ),
    "negative_value_unexpected": _bounds(
        False, None, None,
        f"value parses as a physically meaningless negative number (data-"
        f"quality anomaly); {_UNDERIVABLE}",
    ),
    "unrecognized_free_text_ambiguous": _bounds(
        False, None, None,
        f"raw value did not match any known DCM Streetwidth shape "
        f"(unrecognized text); {_UNDERIVABLE}",
    ),
}

# Exhaustiveness guard at import time: the classifier ships exactly the
# classes named in AMBIGUITY_CLASS_DISPOSITIONS; if it ever changes, this
# policy module must be updated in lockstep rather than silently defaulting
# an unmapped class to "derivable" or dropping it.
_CLASSIFIER_CLASSES = {row[0] for row in AMBIGUITY_CLASS_DISPOSITIONS}
assert set(CLASS_INTERPRETED_BOUNDS) == _CLASSIFIER_CLASSES, (
    "dcm_street_width_policy.CLASS_INTERPRETED_BOUNDS has drifted from the "
    "accepted classifier's AMBIGUITY_CLASS_DISPOSITIONS table - update both "
    "in lockstep"
)


def _precondition_failures(preconditions: AttestedPreconditions) -> tuple[str, ...]:
    """Return the human-readable reasons a classification must be refused,
    or an empty tuple when every precondition is satisfied. No precondition
    is ever treated as satisfied by omission (every field is required on
    :class:`AttestedPreconditions`, and this function re-checks each one
    explicitly rather than trusting a truthy default)."""
    failures: list[str] = []
    if not preconditions.source_documented:
        failures.append("source not documented (D-052-R002)")
    if not preconditions.street_status_checked:
        failures.append("street status not checked (D-052-R002)")
    if preconditions.frontage_match_method == FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY:
        failures.append(
            "frontage coverage not established - a bare nearest-centerline "
            "match alone is insufficient (D-052-R002)"
        )
    elif preconditions.frontage_match_method != FRONTAGE_MATCH_COVERAGE_ESTABLISHED:
        failures.append(
            "frontage coverage not established - unrecognized "
            f"frontage_match_method {preconditions.frontage_match_method!r} "
            "(D-052-R002)"
        )
    if not preconditions.exceptions_checked:
        failures.append(
            "applicable zoning exceptions (ZR 12-10 alternate-width / "
            "named-street provisions et al.) not checked (D-052-R001)"
        )
    return tuple(failures)


def classify_street_width_policy(
    classification: WidthClassification,
    preconditions: AttestedPreconditions,
) -> PolicyDecision:
    """Apply the D-052 DRAFT policy to one accepted-classifier read. Never
    raises: every classifier output and every attestation combination always
    yields a typed :class:`PolicyDecision`. This function never modifies
    ``classification`` or re-parses ``classification.raw_text`` - it only
    consumes the classifier's public ``ambiguity_class`` and ``raw_text``."""
    bounds = CLASS_INTERPRETED_BOUNDS.get(classification.ambiguity_class)
    if bounds is None:
        bounds = _bounds(
            False, None, None,
            "unrecognized ambiguity_class from the classifier (schema "
            f"drift); {_UNDERIVABLE}",
        )

    failures = _precondition_failures(preconditions)
    if failures:
        reason = (
            "classification refused - missing precondition(s): "
            + "; ".join(failures)
            + ". Never silently thresholded (D-052-R001/R002)."
        )
        return PolicyDecision(
            decision_state=DECISION_UNRESOLVED,
            original_label=classification.raw_text,
            ambiguity_class=classification.ambiguity_class,
            source_version=preconditions.source_version,
            matched_geometry_ref=preconditions.matched_geometry_ref,
            interpreted_bounds=bounds,
            classification_reason=reason,
            routed_to=None,
            assumption_notice=None,
            draft_label=DRAFT_LABEL_NOTICE,
        )

    if not bounds.derivable:
        reason = (
            f"{bounds.interval_description}; per D-052-R004 this value "
            "remains UNKNOWN and is routed to map resolution (no tolerance "
            "invented, no averaging, no rounding across the threshold, no "
            "endpoint selection)."
        )
        return PolicyDecision(
            decision_state=DECISION_UNKNOWN,
            original_label=classification.raw_text,
            ambiguity_class=classification.ambiguity_class,
            source_version=preconditions.source_version,
            matched_geometry_ref=preconditions.matched_geometry_ref,
            interpreted_bounds=bounds,
            classification_reason=reason,
            routed_to=ROUTED_TO_MAP_RESOLUTION,
            assumption_notice=None,
            draft_label=DRAFT_LABEL_NOTICE,
        )

    if not bounds.one_sided:
        reason = (
            f"{bounds.interval_description}; per D-052-R003 the one-sided-"
            "bound rule is not satisfied (the accepted reading permits "
            "values on both sides of the threshold), so the classification "
            "remains UNRESOLVED - no endpoint of the range/inequality is "
            "selected."
        )
        return PolicyDecision(
            decision_state=DECISION_UNRESOLVED,
            original_label=classification.raw_text,
            ambiguity_class=classification.ambiguity_class,
            source_version=preconditions.source_version,
            matched_geometry_ref=preconditions.matched_geometry_ref,
            interpreted_bounds=bounds,
            classification_reason=reason,
            routed_to=None,
            assumption_notice=None,
            draft_label=DRAFT_LABEL_NOTICE,
        )

    state = bounds.side if bounds.side in (DECISION_WIDE, DECISION_NARROW) else DECISION_UNRESOLVED
    reason = (
        f"{bounds.interval_description}; per D-052-R001/R003 the accepted "
        f"reading's entire permitted interval lies on the {state} side of "
        f"the {_T:g} ft threshold, subject to the documented-source, "
        "street-status, frontage-coverage, and zoning-exceptions "
        "attestations already checked."
    )
    return PolicyDecision(
        decision_state=state,
        original_label=classification.raw_text,
        ambiguity_class=classification.ambiguity_class,
        source_version=preconditions.source_version,
        matched_geometry_ref=preconditions.matched_geometry_ref,
        interpreted_bounds=bounds,
        classification_reason=reason,
        routed_to=None,
        assumption_notice=OWNER_APPROVED_ASSUMPTION_NOTICE,
        draft_label=DRAFT_LABEL_NOTICE,
    )
