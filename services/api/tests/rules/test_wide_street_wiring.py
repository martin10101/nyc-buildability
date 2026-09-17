"""B7 wide-street wiring acceptance suite (M5-T034). Fully offline and
deterministic. The policy module (app.connectors.dcm_street_width_policy) is used
as the D-052 ORACLE for the wide/narrow/unresolved/unknown decision; the buffer
engine (app.connectors.wide_street_buffer_engine) is exercised through its real
parse surfaces for the proximity test. No network access occurs anywhere.

Coverage:
  AS-3  wide -> wide row; narrow -> standard row; any non-{wide,narrow} ->
        professional review (no FAR bonus); routing keyed off decision_state,
        never routed_to.
  AS-2  the new engine input-bound surfaces through this wiring as an honest
        professional-review determination (never a crash/guess).
  AS-4  exceptions_checked ELEVATED criterion; a lot possibly touching the two
        named-street override segments never claims exceptions_checked=True and
        fails safe rather than claiming wide.
  AS-5  T019 leftovers with the policy module as oracle (one-sided bounds stay
        UNRESOLVED), a genuine conflicting/unknown-records case, and the D-051
        fallback-direction assertions for THESE rows.
  AS-6  provenance quintuple present on every determination; DRAFT marker; no
        published/verified language.
"""

from __future__ import annotations

import json

from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_LATEST_WKID as DCM_WKID_LATEST,
)
from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_WKID as DCM_WKID,
)
from app.connectors.dcm_street_centerline_geometry import (
    parse_segment_geometry_page,
)
from app.connectors.dcm_street_width_classifier import WidthClassification
from app.connectors.dcm_street_width_policy import (
    DECISION_NARROW,
    DECISION_UNKNOWN,
    DECISION_UNRESOLVED,
    DECISION_WIDE,
    FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
    AttestedPreconditions,
    InterpretedBounds,
    PolicyDecision,
    classify_street_width_policy,
)
from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP as MAPPLUTO_CRS_STAMP,
)
from app.connectors.mappluto_geometry_arcgis import (
    EXPECTED_LATEST_WKID as MAPPLUTO_WKID_LATEST,
)
from app.connectors.mappluto_geometry_arcgis import (
    EXPECTED_WKID as MAPPLUTO_WKID,
)
from app.connectors.mappluto_geometry_arcgis import (
    analyze_lot_geometry,
)
from app.connectors.wide_street_buffer_engine import (
    MAX_WIDE_SEGMENTS,
    AttestedLotPolygon,
    AttestedWideSegment,
    Ec5AttestedPreconditions,
)
from app.rules.wide_street_wiring import (
    COVERAGE_CONDITIONAL,
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
    DETERMINATION_NOT_WITHIN_WIDE,
    DETERMINATION_PROFESSIONAL_REVIEW,
    DETERMINATION_WITHIN_WIDE,
    FAR_ROW_NONE,
    FAR_ROW_STANDARD,
    FAR_ROW_WIDE_STREET,
    NamedStreetOverrideStatus,
    determine_wide_street_far,
    select_far_row_value,
)

CID = "m5t034-wiring-test"

SQUARE_LOT_RINGS = [[[0, 0], [0, 200], [200, 200], [200, 0], [0, 0]]]

EC5_CHECKED = Ec5AttestedPreconditions(
    named_street_override_checked=True,
    alternate_width_clause_checked=True,
    attestation_note="both checks performed for this synthetic fixture",
)

# Named-street override table is a follow-up: not implemented, and (unless a
# test says otherwise) no candidate segment is flagged as touching it.
OVERRIDE_CLEAR = NamedStreetOverrideStatus(
    override_table_implemented=False,
    segment_may_touch_named_override=False,
    note="no candidate segment flagged as touching a named-street override",
)
OVERRIDE_MAY_TOUCH = NamedStreetOverrideStatus(
    override_table_implemented=False,
    segment_may_touch_named_override=True,
    note="a candidate segment may fall under Broadway W94-97 / Allen St override",
)


# ---------------------------------------------------------------------------
# Offline fixture builders (real accepted parse surfaces, never network).
# ---------------------------------------------------------------------------


def _dcm_attributes(object_id: int, streetwidth: str) -> dict:
    return {
        "OBJECTID": object_id,
        "Borough": "Manhattan",
        "Feat_Type": "Mapped_St",
        "Feat_status": "City_St",
        "Street_NM": "Test Wide Street",
        "HonoraryNM": "None",
        "Old_ST_NM": "None",
        "Streetwidth": streetwidth,
        "Route_Type": "Gen_use",
        "RoadwayType": "Surface_ST",
        "Build_Status": "Improved",
        "Record_ST": "N",
        "Paper_ST": "N",
        "Stair_ST": "N",
        "CCO_ST": "N",
        "Marg_Wharf": "N",
        "Edit_Date": None,
    }


def _dcm_page_body(object_id: int, paths: list, streetwidth: str) -> str:
    doc = {
        "objectIdFieldName": "OBJECTID",
        "geometryType": "esriGeometryPolyline",
        "geometryProperties": {"shapeLengthFieldName": "Shape__Length", "units": "esriFeet"},
        "spatialReference": {"wkid": DCM_WKID, "latestWkid": DCM_WKID_LATEST},
        "features": [
            {"attributes": _dcm_attributes(object_id, streetwidth), "geometry": {"paths": paths}}
        ],
    }
    return json.dumps(doc)


def _make_segment(object_id: int, paths: list, streetwidth: str = "80") -> AttestedWideSegment:
    transport = DcmTransport(
        url="https://example.invalid/dcm-page",
        status=200,
        body=_dcm_page_body(object_id, paths, streetwidth),
        retrieved_at="2026-09-17T00:00:00Z",
    )
    page = parse_segment_geometry_page(transport, correlation_id=CID)
    entry = page.entries[0]
    return AttestedWideSegment(
        polyline=entry,
        wkid=DCM_WKID,
        latest_wkid=DCM_WKID_LATEST,
        classification_basis=f"effective_disposition={entry.segment.effective_disposition}",
        source_retrieved_at=page.retrieved_at,
        source_raw_digest=page.raw_digest,
    )


def _make_lot(
    rings: list = SQUARE_LOT_RINGS, lot_identity: str = "1-00100-0001"
) -> AttestedLotPolygon:
    assessment = analyze_lot_geometry({"rings": rings}, crs=MAPPLUTO_CRS_STAMP, correlation_id=CID)
    return AttestedLotPolygon(
        assessment=assessment,
        wkid=MAPPLUTO_WKID,
        latest_wkid=MAPPLUTO_WKID_LATEST,
        lot_identity=lot_identity,
        source_retrieved_at="2026-09-17T00:00:00Z",
        source_raw_digest="sha256:cafef00d",
    )


def _satisfied_preconditions() -> AttestedPreconditions:
    """Every D-052 precondition satisfied, so the policy's decision comes from the
    ambiguity_class (the class table under test), not a precondition refusal."""
    return AttestedPreconditions(
        source_documented=True,
        source_version="dcm-2026-09",
        street_status_checked=True,
        frontage_match_method=FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
        matched_geometry_ref="seg-ref-1",
        exceptions_checked=True,
    )


def _policy(ambiguity_class: str, raw_text: str) -> PolicyDecision:
    """Run the REAL D-052 policy module (the oracle) on a constructed classifier
    read with a known ambiguity_class and satisfied preconditions."""
    classification = WidthClassification(
        raw_text=raw_text,
        ambiguity_class=ambiguity_class,
        disposition="narrow_fail_closed",
        review_required=True,
        basis="test-constructed classifier read",
    )
    return classify_street_width_policy(classification, _satisfied_preconditions())


# A clean wide (>=75) and clean narrow (<75) decision from the real policy.
def _wide_decision() -> PolicyDecision:
    return _policy("clean_numeric_ge_75", "80")


def _narrow_decision() -> PolicyDecision:
    return _policy("clean_numeric_lt_75", "40")


# Vertical segment at x=-50: buffer reaches x in [-150, 50] -> intersects lot.
def _within_segment() -> AttestedWideSegment:
    return _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])


# Vertical segment at x=-300: buffer reaches only x in [-400, -200] -> no touch.
def _beyond_segment() -> AttestedWideSegment:
    return _make_segment(2, [[[-300.0, -1000.0], [-300.0, 1000.0]]])


# ---------------------------------------------------------------------------
# AS-3: rule behavior (row firing) + routing keyed off decision_state.
# ---------------------------------------------------------------------------


def test_wide_and_within_100ft_fires_the_wide_street_row() -> None:
    d = _wide_decision()
    assert d.decision_state == DECISION_WIDE  # oracle
    result = determine_wide_street_far(
        [d],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_WITHIN_WIDE
    assert result.far_row == FAR_ROW_WIDE_STREET
    assert result.coverage_hint == COVERAGE_CONDITIONAL
    assert result.aggregate_intersects is True
    # The wide row selects the HIGHER FAR; the standard value is never returned.
    assert select_far_row_value(result, standard_far=2.2, wide_street_far=3.0) == 3.0


def test_all_narrow_fires_the_standard_row() -> None:
    d = _narrow_decision()
    assert d.decision_state == DECISION_NARROW  # oracle
    result = determine_wide_street_far(
        [d],
        lot=_make_lot(),
        wide_segments=[],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_NOT_WITHIN_WIDE
    assert result.far_row == FAR_ROW_STANDARD
    assert result.coverage_hint == COVERAGE_CONDITIONAL
    # The standard row selects the LOWER (conservative) FAR.
    assert select_far_row_value(result, standard_far=2.2, wide_street_far=3.0) == 2.2


def test_wide_but_beyond_100ft_fires_the_standard_row() -> None:
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[_beyond_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_NOT_WITHIN_WIDE
    assert result.far_row == FAR_ROW_STANDARD
    assert result.aggregate_intersects is False
    assert select_far_row_value(result, standard_far=2.2, wide_street_far=3.0) == 2.2


def test_unresolved_is_professional_review_with_no_bonus() -> None:
    d = _policy("lt_inequality_above_75_ambiguous", "<80")
    assert d.decision_state == DECISION_UNRESOLVED  # oracle
    result = determine_wide_street_far(
        [d],
        lot=_make_lot(),
        wide_segments=[],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.far_row == FAR_ROW_NONE
    assert result.coverage_hint == COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    # No FAR bonus is ever granted on uncertainty.
    assert select_far_row_value(result, standard_far=2.2, wide_street_far=3.0) is None


def test_routing_is_keyed_off_decision_state_not_routed_to() -> None:
    # A synthetic PolicyDecision whose decision_state is wide but whose routed_to
    # is (inconsistently) set: the wiring must fire the wide row on the STATE and
    # ignore routed_to entirely (G3 A4).
    inconsistent = PolicyDecision(
        decision_state=DECISION_WIDE,
        original_label="80",
        ambiguity_class="clean_numeric_ge_75",
        source_version="dcm-2026-09",
        matched_geometry_ref="seg-ref-1",
        interpreted_bounds=InterpretedBounds(
            derivable=True, one_sided=True, side=DECISION_WIDE,
            interval_description="single value >= 75 ft (wide side)",
        ),
        classification_reason="test",
        routed_to="map_resolution",  # deliberately inconsistent with a wide state
        assumption_notice=None,
        draft_label="DRAFT",
    )
    result = determine_wide_street_far(
        [inconsistent],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_WITHIN_WIDE
    assert result.far_row == FAR_ROW_WIDE_STREET

    # And an UNKNOWN decision (which DOES carry routed_to=map_resolution) is a
    # professional-review outcome - not "routed" into any wide/narrow path.
    unknown = _policy("unrecognized_free_text_ambiguous", "garbled")
    assert unknown.decision_state == DECISION_UNKNOWN
    assert unknown.routed_to == "map_resolution"
    unknown_result = determine_wide_street_far(
        [unknown],
        lot=_make_lot(),
        wide_segments=[],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert unknown_result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW


def test_no_policy_decisions_is_professional_review() -> None:
    result = determine_wide_street_far(
        [],
        lot=_make_lot(),
        wide_segments=[],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.far_row == FAR_ROW_NONE


def test_corner_lot_one_wide_one_narrow_fires_wide_when_within_100ft() -> None:
    # A genuine corner lot: one wide frontage + one narrow frontage is NOT a
    # conflict - the wide-street row applies when within 100 ft of the wide one.
    result = determine_wide_street_far(
        [_wide_decision(), _narrow_decision()],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_WITHIN_WIDE
    assert result.far_row == FAR_ROW_WIDE_STREET


# ---------------------------------------------------------------------------
# AS-2 through the wiring: the engine input-bound surfaces as professional review.
# ---------------------------------------------------------------------------


def test_engine_input_bound_surfaces_as_professional_review() -> None:
    over_count = [_within_segment()] * (MAX_WIDE_SEGMENTS + 1)
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=over_count,
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.far_row == FAR_ROW_NONE
    assert "input_bounds_exceeded" in result.reason


def test_unattested_ec5_preconditions_surface_as_professional_review() -> None:
    unchecked = Ec5AttestedPreconditions(
        named_street_override_checked=False,
        alternate_width_clause_checked=False,
        attestation_note="neither check performed yet",
    )
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=unchecked,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.buffer_status == "preconditions_not_attested"


def test_wide_policy_but_no_wide_segments_is_inconsistent_professional_review() -> None:
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.buffer_status == "no_wide_segments_provided"
    assert "inconsistent" in result.reason


# ---------------------------------------------------------------------------
# AS-4: exceptions_checked elevated criterion + named-street override honesty.
# ---------------------------------------------------------------------------


def test_named_street_override_candidate_never_claims_exceptions_checked() -> None:
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_MAY_TOUCH,
        correlation_id=CID,
    )
    # A lot possibly touching a named-street override never claims wide and never
    # claims exceptions_checked=True (the override table is not implemented).
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.exceptions_checked is False
    assert result.named_street_override_pending is True
    assert "named-street override" in result.reason


def test_exceptions_checked_true_only_when_fully_resolved() -> None:
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.exceptions_checked is True
    assert result.named_street_override_pending is False


def test_unresolved_decision_never_claims_exceptions_checked() -> None:
    d = _policy("gt_inequality_below_75_ambiguous", ">60")
    assert d.decision_state == DECISION_UNRESOLVED
    result = determine_wide_street_far(
        [d],
        lot=_make_lot(),
        wide_segments=[],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR,
        correlation_id=CID,
    )
    assert result.exceptions_checked is False


# ---------------------------------------------------------------------------
# AS-5: T019 leftovers (policy module as oracle) + conflicting records +
# fallback-direction assertions.
# ---------------------------------------------------------------------------


def test_t019_le_74_is_narrow_per_policy_and_fires_standard_row() -> None:
    # '<=74' -> inclusive upper bound 74 < 75 -> policy NARROW (oracle). The task
    # warned a naive '<=74 -> narrow' could be wrong; here the D-052 policy module
    # itself decides narrow, and one-sided-bound straddlers stay UNRESOLVED below.
    d = _policy("le_inequality_below_75_confident_narrow", "<=74")
    assert d.decision_state == DECISION_NARROW
    result = determine_wide_street_far(
        [d], lot=_make_lot(), wide_segments=[], ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_NOT_WITHIN_WIDE
    assert result.far_row == FAR_ROW_STANDARD


def test_t019_lt_80_one_sided_bound_stays_unresolved_per_policy() -> None:
    d = _policy("lt_inequality_above_75_ambiguous", "<80")
    assert d.decision_state == DECISION_UNRESOLVED  # one-sided bound straddles 75
    result = determine_wide_street_far(
        [d], lot=_make_lot(), wide_segments=[], ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW


def test_t019_gt_60_one_sided_bound_stays_unresolved_per_policy() -> None:
    d = _policy("gt_inequality_below_75_ambiguous", ">60")
    assert d.decision_state == DECISION_UNRESOLVED
    result = determine_wide_street_far(
        [d], lot=_make_lot(), wide_segments=[], ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW


def test_conflicting_or_unrecognized_records_stay_unknown_and_route_to_review() -> None:
    # Per D-052-R004 conflicting/unrecognized records stay UNKNOWN (routed to map
    # resolution). The policy module decides UNKNOWN (oracle); the wiring never
    # silently picks a side - it surfaces professional review.
    d = _policy("unrecognized_free_text_ambiguous", "conflicting DCM records: 60 and 90")
    assert d.decision_state == DECISION_UNKNOWN
    result = determine_wide_street_far(
        [d], lot=_make_lot(), wide_segments=[], ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.far_row == FAR_ROW_NONE


def test_fallback_direction_lower_far_is_conservative_for_these_rows() -> None:
    # D-051 (validated for THESE rows): the standard row is the LOWER FAR, and it
    # is what governs on any uncertainty/no-wide-street outcome; the higher
    # wide-street FAR is only ever selected by an affirmative WITHIN_WIDE result.
    standard, wide = 2.2, 3.0
    assert standard < wide
    not_within = determine_wide_street_far(
        [_narrow_decision()], lot=_make_lot(), wide_segments=[],
        ec5_preconditions=EC5_CHECKED, named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    assert select_far_row_value(not_within, standard_far=standard, wide_street_far=wide) == standard
    review = determine_wide_street_far(
        [_policy("lt_inequality_above_75_ambiguous", "<80")], lot=_make_lot(),
        wide_segments=[], ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    # Uncertainty grants no bonus at all (even more conservative than the lower row).
    assert select_far_row_value(review, standard_far=standard, wide_street_far=wide) is None
    assert "conservative" in review.fallback_direction_note
    assert "D-051" in review.fallback_direction_note


# ---------------------------------------------------------------------------
# AS-6: provenance quintuple + DRAFT marker + no verified/published language.
# ---------------------------------------------------------------------------


def test_provenance_quintuple_present_on_every_determination() -> None:
    d = _wide_decision()
    result = determine_wide_street_far(
        [d], lot=_make_lot(), wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED, named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    # All five provenance channels are populated, aggregated from the decision.
    assert result.policy_decision_states == (DECISION_WIDE,)
    assert result.original_labels == (d.original_label,)
    assert result.source_versions == (d.source_version,)
    assert result.matched_geometry_refs == (d.matched_geometry_ref,)
    assert result.interpreted_bounds_summaries == (d.interpreted_bounds.interval_description,)
    assert result.classification_reasons == (d.classification_reason,)
    assert result.lot_identity == "1-00100-0001"


def test_draft_marker_present_and_never_claims_verified_or_published() -> None:
    result = determine_wide_street_far(
        [_wide_decision()], lot=_make_lot(), wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED, named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    # The DRAFT marker names G6 review (its prose legitimately contains the word
    # "Verified" as a NEGATION - "not a Verified determination" - exactly like the
    # accepted integration NOT_VERIFIED_DISCLAIMER; the honest check is that the
    # determination never CLAIMS a verified/published STATUS).
    assert "DRAFT" in result.draft_label
    assert "G6" in result.draft_label
    assert result.coverage_hint in (COVERAGE_CONDITIONAL, COVERAGE_PROFESSIONAL_REVIEW_REQUIRED)
    assert result.coverage_hint != "verified"
    assert result.determination_state != "published"
