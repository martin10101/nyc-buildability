"""Offline tests for the D-052 street-width classification-POLICY layer
(task M4-T019). Builds on the accepted, unmodified M4-T015 classifier
(:mod:`app.connectors.dcm_street_width_classifier`) purely through its
public API - no network, no fixtures needed."""

from __future__ import annotations

import pytest

from app.connectors.dcm_street_width_classifier import (
    AMBIGUITY_CLASS_DISPOSITIONS,
    DISPOSITION_NARROW_FAIL_CLOSED,
    WidthClassification,
    classify_street_width,
)
from app.connectors.dcm_street_width_policy import (
    CLASS_INTERPRETED_BOUNDS,
    DECISION_NARROW,
    DECISION_UNKNOWN,
    DECISION_UNRESOLVED,
    DECISION_WIDE,
    FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
    FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY,
    ROUTED_TO_MAP_RESOLUTION,
    AttestedPreconditions,
    classify_street_width_policy,
)


def _ok_preconditions(
    *,
    source_documented: bool = True,
    source_version: str | None = "dcm-street-cl-v2026.1",
    street_status_checked: bool = True,
    frontage_match_method: str = FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
    matched_geometry_ref: str | None = "objectid:12345",
    exceptions_checked: bool = True,
) -> AttestedPreconditions:
    """Every attestation satisfied - the baseline used by tests that are not
    themselves testing precondition refusal."""
    return AttestedPreconditions(
        source_documented=source_documented,
        source_version=source_version,
        street_status_checked=street_status_checked,
        frontage_match_method=frontage_match_method,
        matched_geometry_ref=matched_geometry_ref,
        exceptions_checked=exceptions_checked,
    )


def _decide(raw: str, preconditions: AttestedPreconditions | None = None):
    classification = classify_street_width(raw)
    return classify_street_width_policy(classification, preconditions or _ok_preconditions())


# ---------------------------------------------------------------------------
# S1 / R001 - threshold boundaries (74.99 / 75.0 / 75.01)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_state",
    [
        ("74.99", DECISION_NARROW),
        ("75", DECISION_WIDE),
        ("75.0", DECISION_WIDE),
        ("75.01", DECISION_WIDE),
    ],
)
def test_threshold_boundaries(raw: str, expected_state: str) -> None:
    decision = _decide(raw)
    assert decision.decision_state == expected_state


# ---------------------------------------------------------------------------
# S1 / R003 - the owner's worked examples, verbatim, as literal test cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_state",
    [
        ("<75", DECISION_NARROW),
        (">75", DECISION_WIDE),
        (">=75", DECISION_WIDE),
        ("75-90", DECISION_WIDE),
        ("<=75", DECISION_UNRESOLVED),
        ("60-75", DECISION_UNRESOLVED),
        ("70-80", DECISION_UNRESOLVED),
    ],
)
def test_r003_owner_examples_verbatim(raw: str, expected_state: str) -> None:
    decision = _decide(raw)
    assert decision.decision_state == expected_state


def test_one_sided_bound_property_holds_over_all_derivable_classes() -> None:
    """Property from D-052-R003: classify (wide/narrow) iff the accepted
    reading's interval is a subset of (-inf, 75) or [75, +inf) - i.e. iff
    ``one_sided`` is True. This is asserted structurally over the table
    itself (not just the worked examples above)."""
    for ambiguity_class, bounds in CLASS_INTERPRETED_BOUNDS.items():
        if bounds.derivable and bounds.one_sided:
            assert bounds.side in (DECISION_WIDE, DECISION_NARROW), ambiguity_class
        elif bounds.derivable and not bounds.one_sided:
            assert bounds.side is None, ambiguity_class
        else:
            assert bounds.one_sided is None and bounds.side is None, ambiguity_class


# ---------------------------------------------------------------------------
# Range handling generally (beyond the owner's literal examples)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_state",
    [
        ("50-60", DECISION_NARROW),
        ("80-90", DECISION_WIDE),
        ("166-192", DECISION_WIDE),
        ("74-75.3", DECISION_UNRESOLVED),
        ("60-90", DECISION_UNRESOLVED),  # straddles; NOT resolved to wide via averaging (avg=75)
    ],
)
def test_range_handling_generally(raw: str, expected_state: str) -> None:
    decision = _decide(raw)
    assert decision.decision_state == expected_state


def test_range_order_unexpected_is_unknown_not_resolved() -> None:
    decision = _decide("100-90")
    assert decision.decision_state == DECISION_UNKNOWN
    assert decision.routed_to == ROUTED_TO_MAP_RESOLUTION


# ---------------------------------------------------------------------------
# S2 / R001 / R002 - preconditions fail closed; no default-true anywhere
# ---------------------------------------------------------------------------


def test_missing_source_documented_refuses_even_a_clean_wide_value() -> None:
    decision = _decide("80", _ok_preconditions(source_documented=False))
    assert decision.decision_state == DECISION_UNRESOLVED
    assert "source not documented" in decision.classification_reason
    assert decision.assumption_notice is None


def test_missing_street_status_checked_refuses() -> None:
    decision = _decide("80", _ok_preconditions(street_status_checked=False))
    assert decision.decision_state == DECISION_UNRESOLVED
    assert "street status not checked" in decision.classification_reason


def test_bare_nearest_centerline_match_is_refused() -> None:
    """R002: 'A nearest-centerline match alone is insufficient.' Modeled as
    an explicit refusal case on the frontage_match_method attestation."""
    decision = _decide(
        "80", _ok_preconditions(frontage_match_method=FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY)
    )
    assert decision.decision_state == DECISION_UNRESOLVED
    assert "nearest-centerline" in decision.classification_reason


def test_unrecognized_frontage_match_method_also_fails_closed() -> None:
    decision = _decide("80", _ok_preconditions(frontage_match_method="something_else"))
    assert decision.decision_state == DECISION_UNRESOLVED
    assert "frontage coverage not established" in decision.classification_reason


def test_missing_exceptions_checked_refuses_never_silently_thresholded() -> None:
    """R001: an applicable exception that is not implemented must remain
    UNRESOLVED - even for a value that would otherwise unambiguously
    classify wide."""
    decision = _decide("100", _ok_preconditions(exceptions_checked=False))
    assert decision.decision_state == DECISION_UNRESOLVED
    assert "zoning exceptions" in decision.classification_reason
    assert decision.assumption_notice is None


def test_all_preconditions_false_lists_every_failure() -> None:
    decision = _decide(
        "80",
        AttestedPreconditions(
            source_documented=False,
            source_version=None,
            street_status_checked=False,
            frontage_match_method=FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY,
            matched_geometry_ref=None,
            exceptions_checked=False,
        ),
    )
    assert decision.decision_state == DECISION_UNRESOLVED
    reason = decision.classification_reason
    assert "source not documented" in reason
    assert "street status not checked" in reason
    assert "nearest-centerline" in reason
    assert "zoning exceptions" in reason


def test_preconditions_dataclass_has_no_defaults() -> None:
    """Every attestation is required at construction - nothing can silently
    default to satisfied (risk: 'precondition theater')."""
    with pytest.raises(TypeError):
        AttestedPreconditions()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# S3 / R004 - forbidden moves: negative tests proving each does NOT happen
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    ["~75", "~80", "~60", "Around 100", "Probably between 80 - 90", "approx 80"],
)
def test_approximation_never_gets_an_invented_tolerance(raw: str) -> None:
    """An approximation/hedge is NEVER granted wide or narrow, no matter how
    close the stated number is to (or past) the threshold - proves no
    tolerance is invented around 75."""
    decision = _decide(raw)
    assert decision.decision_state == DECISION_UNKNOWN
    assert decision.routed_to == ROUTED_TO_MAP_RESOLUTION
    assert decision.decision_state not in (DECISION_WIDE, DECISION_NARROW)


@pytest.mark.parametrize("raw", ["60-75", "70-80", "74-75.3", "60-90"])
def test_straddling_range_is_never_endpoint_picked(raw: str) -> None:
    """No averaging path exists and no endpoint is silently selected: a
    straddling range always stays UNRESOLVED, never narrow (low endpoint)
    nor wide (high endpoint)."""
    decision = _decide(raw)
    assert decision.decision_state == DECISION_UNRESOLVED
    assert decision.decision_state not in (DECISION_WIDE, DECISION_NARROW, DECISION_UNKNOWN)


def test_no_rounding_across_the_threshold() -> None:
    """74.99 must never round up to 75 and become wide."""
    decision = _decide("74.99")
    assert decision.decision_state == DECISION_NARROW


@pytest.mark.parametrize(
    "raw",
    ["Width Irregular", "varies", "n/a", "Unknown", "gibberish free text", "100-90"],
)
def test_unclear_or_unrecognized_or_conflicting_stays_unknown(raw: str) -> None:
    decision = _decide(raw)
    assert decision.decision_state == DECISION_UNKNOWN
    assert decision.routed_to == ROUTED_TO_MAP_RESOLUTION


# ---------------------------------------------------------------------------
# S4 / R005 / R006 / R007 - provenance quintuple, assumption + DRAFT labels,
# UNKNOWN as a first-class state distinct from narrow
# ---------------------------------------------------------------------------


def test_provenance_quintuple_present_on_a_wide_decision() -> None:
    decision = _decide("80")
    assert decision.original_label == "80"
    assert decision.source_version == "dcm-street-cl-v2026.1"
    assert decision.matched_geometry_ref == "objectid:12345"
    assert decision.interpreted_bounds.derivable is True
    assert decision.classification_reason
    assert decision.assumption_notice is not None
    assert "never a verified" in decision.assumption_notice.lower()
    assert decision.draft_label


def test_provenance_quintuple_present_on_a_refusal() -> None:
    decision = _decide("80", _ok_preconditions(exceptions_checked=False))
    assert decision.original_label == "80"
    assert decision.source_version == "dcm-street-cl-v2026.1"
    assert decision.matched_geometry_ref == "objectid:12345"
    assert decision.interpreted_bounds.derivable is True
    assert decision.classification_reason
    assert decision.assumption_notice is None  # no classification was issued
    assert decision.draft_label


def test_assumption_notice_only_on_issued_classifications() -> None:
    wide = _decide("80")
    narrow = _decide("60")
    unresolved = _decide("60-75")
    unknown = _decide("~80")
    assert wide.assumption_notice is not None
    assert narrow.assumption_notice is not None
    assert unresolved.assumption_notice is None
    assert unknown.assumption_notice is None


def test_draft_label_present_on_every_decision_state() -> None:
    for raw in ("80", "60", "60-75", "~80"):
        decision = _decide(raw)
        assert decision.draft_label == (
            decision.draft_label
        )  # populated (non-empty checked below)
        assert decision.draft_label != ""
        assert "DRAFT" in decision.draft_label
        assert "G6" in decision.draft_label


def test_unknown_is_routed_only_for_unknown_state() -> None:
    assert _decide("~80").routed_to == ROUTED_TO_MAP_RESOLUTION
    assert _decide("80").routed_to is None
    assert _decide("60").routed_to is None
    assert _decide("60-75").routed_to is None


def test_unknown_is_a_first_class_state_distinct_from_narrow() -> None:
    """D-052-R006 / D-051-R002: UNKNOWN is the underlying data state this
    module emits - it must never be silently folded into narrow, even
    though the accepted classifier's OWN disposition field for these
    classes is literally 'narrow_fail_closed' (that field belongs to the
    classifier's separate fail-closed convention, not to this policy)."""
    classification = classify_street_width("Unknown")
    assert classification.disposition == DISPOSITION_NARROW_FAIL_CLOSED
    decision = classify_street_width_policy(classification, _ok_preconditions())
    assert decision.decision_state == DECISION_UNKNOWN
    assert decision.decision_state != DECISION_NARROW
    assert decision.routed_to == ROUTED_TO_MAP_RESOLUTION


# ---------------------------------------------------------------------------
# Exhaustiveness: the interpreted-bounds table stays in lockstep with the
# accepted classifier's 24 typed classes.
# ---------------------------------------------------------------------------


def test_class_interpreted_bounds_is_exhaustive_over_the_classifier_table() -> None:
    classifier_classes = {row[0] for row in AMBIGUITY_CLASS_DISPOSITIONS}
    assert set(CLASS_INTERPRETED_BOUNDS) == classifier_classes
    assert len(CLASS_INTERPRETED_BOUNDS) == 24


def test_class_interpreted_bounds_internally_consistent() -> None:
    for ambiguity_class, bounds in CLASS_INTERPRETED_BOUNDS.items():
        if not bounds.derivable:
            assert bounds.one_sided is None, ambiguity_class
            assert bounds.side is None, ambiguity_class
        elif bounds.one_sided:
            assert bounds.side in (DECISION_WIDE, DECISION_NARROW), ambiguity_class
        else:
            assert bounds.side is None, ambiguity_class


# ---------------------------------------------------------------------------
# Defensive robustness: an unrecognized ambiguity_class (schema drift from a
# hypothetical future classifier change) never raises and never guesses.
# ---------------------------------------------------------------------------


def test_unrecognized_ambiguity_class_fails_closed_to_unknown_without_raising() -> None:
    bogus = WidthClassification(
        raw_text="oddball value",
        ambiguity_class="not_a_real_class_from_a_future_classifier",
        disposition=DISPOSITION_NARROW_FAIL_CLOSED,
        review_required=True,
        basis="test-only fabricated classification",
    )
    decision = classify_street_width_policy(bogus, _ok_preconditions())
    assert decision.decision_state == DECISION_UNKNOWN
    assert decision.routed_to == ROUTED_TO_MAP_RESOLUTION
    assert "schema" in decision.classification_reason


# ---------------------------------------------------------------------------
# Never raises, over a broad mixed sample of raw inputs and precondition
# combinations.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "75", "74.99", "80", "-10", "n/a", "Width Irregular", "varies",
        "Unknown but <75", "Unknown but >75", "Regular but unknown.",
        ">-5", "100-90", "gibberish free text", "",
    ],
)
@pytest.mark.parametrize(
    "preconditions",
    [
        _ok_preconditions(),
        _ok_preconditions(exceptions_checked=False),
        _ok_preconditions(frontage_match_method=FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY),
    ],
)
def test_policy_never_raises(raw: str, preconditions: AttestedPreconditions) -> None:
    classification = classify_street_width(raw)
    decision = classify_street_width_policy(classification, preconditions)
    assert decision.decision_state in (
        DECISION_WIDE, DECISION_NARROW, DECISION_UNRESOLVED, DECISION_UNKNOWN,
    )
