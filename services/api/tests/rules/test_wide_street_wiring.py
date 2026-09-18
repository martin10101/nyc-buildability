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

import hashlib
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
from app.rules.named_street_override import (
    MatchStatus,
    NamedStreetOverrideMatcher,
    OverrideQuery,
    load_default_matcher,
)
from app.rules.snapshots import load_snapshot_file
from app.rules.wide_street_wiring import (
    COVERAGE_CONDITIONAL,
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
    DETERMINATION_NOT_WITHIN_WIDE,
    DETERMINATION_PROFESSIONAL_REVIEW,
    DETERMINATION_WITHIN_WIDE,
    FAR_ROW_NONE,
    FAR_ROW_STANDARD,
    FAR_ROW_WIDE_STREET,
    MatchedNamedStreetOverride,
    NamedStreetOverrideStatus,
    build_named_street_override_status,
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


# ---------------------------------------------------------------------------
# M5-T040 WIRING: build_named_street_override_status is the FIRST production
# consumer of the accepted ZR 12-10 matcher (app.rules.named_street_override).
# It runs the matcher over the candidate segments and produces the wiring's
# NamedStreetOverrideStatus fail-closed (D-051). The wiring truth table (AS-4):
#   all-NOT_MATCHED (fully-resolved) -> exceptions_checked True (row can fire);
#   any MATCHED_OVERRIDE -> professional review carrying the distinct override
#     provenance, wide FAR never applied numerically;
#   any INDETERMINATE / missing input -> the existing refusal stands unchanged.
# ---------------------------------------------------------------------------

# Real-snapshot queries whose matcher outcomes are pinned by the accepted
# M5-T039 matcher suite (test_named_street_override.py): an ordinary street is
# NOT_MATCHED; the conditional Broadway designation is INDETERMINATE.
_ORDINARY_RESOLVED = OverrideQuery("Manhattan", 7, "Nowhere Road", "A Street", "B Street")
_ORDINARY_NO_BOUNDS = OverrideQuery("Manhattan", 7, "Nowhere Road", None, None)
_CONDITIONAL_BROADWAY = OverrideQuery(
    "Manhattan", 7, "Broadway", "West 94th Street", "West 97th Street"
)


def _real_matcher() -> NamedStreetOverrideMatcher:
    return load_default_matcher()


def _matched_override_matcher(tmp_path) -> tuple[NamedStreetOverrideMatcher, OverrideQuery, dict]:
    """A matcher built from a SYNTHETIC unconditional snapshot whose single row
    reaches MATCHED_OVERRIDE (mirrors test_named_street_override::
    test_matched_override_for_unconditional_row). Returns the matcher, a query
    that matches, and the expected provenance facts."""
    named_quote = (
        "In Community District 1 in the Borough of Testville, the roadways of "
        "Testonly Avenue between First and Second Streets shall each be "
        "considered a wide street."
    )
    alt_quote = "In C5-3 Districts the alternate-width test may be considered."
    excerpt = named_quote + "\n\n" + alt_quote
    digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
    doc = {
        "snapshot_id": "zr-wiring-matched",
        "section_number": "12-10",
        "section_title": "synthetic",
        "source": {"request_url": "u", "retrieved_at": "t", "raw_html_verified": False},
        "verbatim_excerpt": excerpt,
        "content_digest_sha256": digest,
        "extraction_status": "extracted_draft",
        "named_street_overrides": {
            "provision_id": "test-named",
            "section_anchor": "ZR 12-10 test anchor",
            "node_anchor": "/node/0",
            "verbatim_source_quote": named_quote,
            "disposition_when_located": "matched_override",
            "open_legal_questions": [],
            "rows": [
                {
                    "row_id": "testonly",
                    "borough": "Testville",
                    "community_district": 1,
                    "street_name": "Testonly Avenue",
                    "frontage_from": "First Street",
                    "frontage_to": "Second Street",
                }
            ],
        },
        "alternate_width_provisions": {
            "provision_id": "test-alt",
            "section_anchor": "ZR 12-10 test anchor",
            "applicable_districts": ["C5-3"],
            "verbatim_source_quote": alt_quote,
            "disposition_reason": "test",
        },
    }
    path = tmp_path / "zr-wiring-matched.snapshot.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    matcher = NamedStreetOverrideMatcher(load_snapshot_file(path))
    query = OverrideQuery("Testville", 1, "Testonly Avenue", "First Street", "Second Street")
    expected = {
        "provision_id": "test-named",
        "snapshot_sha256": digest,
        "section_anchor": "ZR 12-10 test anchor",
        "matched_row_verbatim": named_quote,
    }
    return matcher, query, expected


def test_build_status_all_not_matched_fully_resolved_is_clear() -> None:
    # Every candidate segment is an ordinary street with fully-resolved inputs ->
    # the matcher returns NOT_MATCHED for all -> the override table was applied and
    # no designation applies (checked AND resolved).
    matcher = _real_matcher()
    assert matcher.match(_ORDINARY_RESOLVED).status is MatchStatus.NOT_MATCHED  # oracle
    status = build_named_street_override_status(matcher, [_ORDINARY_RESOLVED])
    assert status.override_table_implemented is True
    assert status.segment_may_touch_named_override is False
    assert status.matched_override is None


def test_build_status_all_clear_lets_exceptions_checked_become_true() -> None:
    # A wide segment within 100 ft + an all-clear override status -> the elevated
    # exceptions_checked criterion is met and the wide row fires (AS-4).
    matcher = _real_matcher()
    status = build_named_street_override_status(matcher, [_ORDINARY_RESOLVED])
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=status,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_WITHIN_WIDE
    assert result.exceptions_checked is True
    assert result.named_street_override_pending is False
    assert result.named_street_override_match is None


def test_build_status_matched_override_carries_distinct_provenance(tmp_path) -> None:
    matcher, query, expected = _matched_override_matcher(tmp_path)
    assert matcher.match(query).status is MatchStatus.MATCHED_OVERRIDE  # oracle
    status = build_named_street_override_status(matcher, [query])
    assert isinstance(status.matched_override, MatchedNamedStreetOverride)
    m = status.matched_override
    assert m.provision_id == expected["provision_id"]
    assert m.snapshot_sha256 == expected["snapshot_sha256"]
    assert m.section_anchor == expected["section_anchor"]
    assert m.matched_row_verbatim == expected["matched_row_verbatim"]


def test_matched_override_forces_professional_review_with_provenance(tmp_path) -> None:
    # A DEFINITIVE match -> professional review carrying the four override
    # provenance elements, and the wide FAR is never applied numerically, EVEN with
    # a wide policy decision and a within-100ft wide segment supplied.
    matcher, query, expected = _matched_override_matcher(tmp_path)
    status = build_named_street_override_status(matcher, [query])
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=status,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.far_row == FAR_ROW_NONE
    assert result.exceptions_checked is False
    assert result.named_street_override_pending is True
    # No wide FAR bonus is ever granted on a matched override.
    assert select_far_row_value(result, standard_far=2.2, wide_street_far=3.0) is None
    # The distinct override provenance rides on the determination AND in the reason.
    assert result.named_street_override_match is not None
    assert result.named_street_override_match.provision_id == expected["provision_id"]
    assert expected["snapshot_sha256"] in result.reason
    assert expected["provision_id"] in result.reason
    assert expected["section_anchor"] in result.reason


def test_matched_override_preempts_all_narrow_standard_row(tmp_path) -> None:
    # A named-street override designates the street WIDE regardless of numeric
    # width: a match on an otherwise ALL-NARROW lot must NOT fire the standard row -
    # it escalates to professional review (branch 0 preempts the all-narrow branch).
    matcher, query, _ = _matched_override_matcher(tmp_path)
    status = build_named_street_override_status(matcher, [query])
    result = determine_wide_street_far(
        [_narrow_decision()],
        lot=_make_lot(),
        wide_segments=[],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=status,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.far_row == FAR_ROW_NONE


def test_build_status_indeterminate_segment_is_unresolved_refusal() -> None:
    # A located-but-conditional designation (Broadway W94-97) is INDETERMINATE ->
    # the segment could not be cleared -> refusal stands unchanged (may_touch True,
    # not implemented) -> a wide-tending lot fails safe to professional review.
    matcher = _real_matcher()
    assert matcher.match(_CONDITIONAL_BROADWAY).status is MatchStatus.INDETERMINATE  # oracle
    status = build_named_street_override_status(matcher, [_CONDITIONAL_BROADWAY])
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True
    assert status.matched_override is None
    result = determine_wide_street_far(
        [_wide_decision()],
        lot=_make_lot(),
        wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED,
        named_street_override=status,
        correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.exceptions_checked is False
    assert result.named_street_override_pending is True


def test_build_status_not_matched_but_missing_bounds_is_unresolved() -> None:
    # A NOT_MATCHED whose query lacks cross-street bounds is NOT fully-resolved
    # (letter of the binding wiring semantics): it cannot clear the exception, so
    # the status stays unresolved (fail-closed, never a guessed clearance).
    matcher = _real_matcher()
    assert matcher.match(_ORDINARY_NO_BOUNDS).status is MatchStatus.NOT_MATCHED  # oracle
    status = build_named_street_override_status(matcher, [_ORDINARY_NO_BOUNDS])
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True


def test_build_status_mixed_unresolved_segment_blocks_clear() -> None:
    # One fully-resolved NOT_MATCHED + one INDETERMINATE -> the whole lot is
    # unresolved (every segment must clear for exceptions_checked to be possible).
    matcher = _real_matcher()
    status = build_named_street_override_status(
        matcher, [_ORDINARY_RESOLVED, _CONDITIONAL_BROADWAY]
    )
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True


def test_build_status_empty_queries_is_unresolved() -> None:
    # No candidate segment supplied -> nothing was checked -> unresolved (never a
    # vacuous "cleared").
    matcher = _real_matcher()
    status = build_named_street_override_status(matcher, [])
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True


def test_build_status_matched_override_wins_over_indeterminate(tmp_path) -> None:
    # A MATCHED_OVERRIDE is decisive even alongside an INDETERMINATE segment: the
    # richer matched provenance is carried (not merely an unresolved refusal).
    matcher, query, expected = _matched_override_matcher(tmp_path)
    # A second query on the same synthetic matcher that is INDETERMINATE (located
    # street, missing bounds resolves to INDETERMINATE only for a named row; here
    # use a missing community district to force INDETERMINATE).
    indeterminate_q = OverrideQuery(
        "Testville", None, "Testonly Avenue", "First Street", "Second Street"
    )
    assert matcher.match(indeterminate_q).status is MatchStatus.INDETERMINATE
    status = build_named_street_override_status(matcher, [indeterminate_q, query])
    assert status.matched_override is not None
    assert status.matched_override.provision_id == expected["provision_id"]


# ---------------------------------------------------------------------------
# M5-T040 (run 46): the wiring re-establishes TYPED, NORMALIZED candidate inputs
# before an all-NOT_MATCHED result may attest exceptions_checked. The matcher
# SHORT-CIRCUITS to NOT_MATCHED for an ordinary (non-override) street WITHOUT
# inspecting the cross-street bounds and COERCES non-string locators (str() /
# digit-scan) along the way, so a malformed-but-nonblank field must be caught at
# the wiring seam, never trusted through that coerced NOT_MATCHED (D-051).
# ---------------------------------------------------------------------------

def _raw_query(
    borough: object, cd: object, street: object, xfrom: object, xto: object
) -> OverrideQuery:
    """Build an OverrideQuery from deliberately untyped values (malformed-shape
    probes). The frozen dataclass runs no runtime type check - matching a real
    caller that passes non-string values - so the static checker is told to allow
    the invalid shapes here once."""
    return OverrideQuery(borough, cd, street, xfrom, xto)  # type: ignore


# Malformed candidates: an ordinary (non-override) street carrying non-string
# borough / community district / bounds. The matcher COERCES each and reaches
# NOT_MATCHED without inspecting the bounds; the wiring's typed gate refuses them.
_MALFORMED_BOUNDS = _raw_query("Manhattan", 7, "Nowhere Road", 123, 456)
_MALFORMED_BOROUGH = _raw_query(123, 7, "Nowhere Road", "A Street", "B Street")
_MALFORMED_CD_LIST = _raw_query("Manhattan", [7], "Nowhere Road", "A Street", "B Street")


def test_matcher_short_circuits_to_not_matched_without_inspecting_bounds() -> None:
    # Documents the short-circuit the wiring guards against: an ordinary street
    # with GARBAGE, non-string bounds STILL returns NOT_MATCHED - the matcher
    # never inspects the bounds on the non-override path.
    matcher = _real_matcher()
    assert matcher.match(_MALFORMED_BOUNDS).status is MatchStatus.NOT_MATCHED  # oracle
    assert matcher.match(_MALFORMED_BOROUGH).status is MatchStatus.NOT_MATCHED  # coerced
    assert matcher.match(_MALFORMED_CD_LIST).status is MatchStatus.NOT_MATCHED  # coerced


def test_build_status_non_string_bounds_are_unresolved() -> None:
    # Bounds present but non-string (nonblank when coerced) are NOT typed/
    # normalized -> the exception cannot be cleared (fail-closed) even though the
    # matcher short-circuited to NOT_MATCHED.
    matcher = _real_matcher()
    status = build_named_street_override_status(matcher, [_MALFORMED_BOUNDS])
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True
    assert status.matched_override is None


def test_build_status_non_string_borough_is_unresolved() -> None:
    # The matcher coerces a non-string borough to reach NOT_MATCHED; the wiring
    # refuses to attest on an untyped locator.
    matcher = _real_matcher()
    status = build_named_street_override_status(matcher, [_MALFORMED_BOROUGH])
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True


def test_build_status_list_community_district_is_unresolved() -> None:
    # A list community district coerces through the matcher's digit-scan
    # ([7] -> "7" -> 7) to NOT_MATCHED, but a list is not a TYPED community
    # district; the wiring's typed gate refuses it.
    matcher = _real_matcher()
    status = build_named_street_override_status(matcher, [_MALFORMED_CD_LIST])
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True


def test_build_status_mixed_resolved_and_malformed_bounds_blocks_clear() -> None:
    # One fully-resolved NOT_MATCHED + one NOT_MATCHED with malformed bounds ->
    # the whole lot is unresolved (every segment must clear for exceptions_checked
    # to be possible). Order-independent: the malformed segment blocks regardless.
    matcher = _real_matcher()
    forward = build_named_street_override_status(matcher, [_ORDINARY_RESOLVED, _MALFORMED_BOUNDS])
    reverse = build_named_street_override_status(matcher, [_MALFORMED_BOUNDS, _ORDINARY_RESOLVED])
    for status in (forward, reverse):
        assert status.override_table_implemented is False
        assert status.segment_may_touch_named_override is True
        assert status.matched_override is None
