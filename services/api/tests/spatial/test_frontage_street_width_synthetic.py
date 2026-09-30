"""Street width per frontage on small synthetic lots (queue item B-04; plan M1-13, §4).

Offline and deterministic. Lots and center lines are built as in the B-03 synthetic tests
(EPSG:2263 feet; each center line half its mapped width outside the lot line it fronts), and
the site geometry is derived by the real B-03 code. The DCM segment records the width step
reads are built next to them with the same OBJECTIDs and raw widths.

Invariant checked throughout: a frontage is wide or narrow only when the D-052 policy
issues that class; every other case carries "Needs street width" with BOTH classes
possible - never a silent narrow default.
"""

from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

import pytest

from app.connectors.dcm_street_width_policy import (
    DECISION_UNKNOWN,
    DECISION_UNRESOLVED,
    DRAFT_LABEL_NOTICE,
    ROUTED_TO_MAP_RESOLUTION,
)
from app.rules.snapshots import SnapshotStore
from app.spatial.frontage_street_width import (
    CLASS_NARROW,
    CLASS_NEEDS_STREET_WIDTH,
    CLASS_WIDE,
    EXCEPTION_MAY_APPLY,
    EXCEPTION_NOT_APPLICABLE,
    EXCEPTION_NOT_CHECKED,
    MARKER_NEEDS_STREET_WIDTH,
    STATUS_COMPLETE,
    STATUS_NEEDS_STREET_WIDTH,
    LotZoningContext,
    MappedStreetSegment,
    SegmentSource,
    Zr1210Exceptions,
    default_exceptions,
    derive_frontage_street_widths,
)
from app.spatial.site_geometry import (
    LABEL_CITY_RECORDS,
    LABEL_UNKNOWN,
    LotOutline,
    StreetCenterline,
    StreetData,
    derive_site_geometry,
)
from app.spatial.site_geometry.results import FRONTAGE_CONFIRMED, FRONTAGE_UNCERTAIN

CRS = {"wkid": 102718, "latest_wkid": 2263}
ENVELOPE = (-1000.0, -1000.0, 1000.0, 1000.0)
RECT = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]
SOUTH = ((0.0, 0.0), (25.0, 0.0))
WEST = ((0.0, 100.0), (0.0, 0.0))
R6 = LotZoningContext(("R6",), None, "synthetic zoning record")

SOURCE = SegmentSource(
    source="synthetic DCM street center lines",
    source_id="nyc-dcp-dcm-street-centerline-arcgis",
    dataset="synthetic/DCM_Street_Center_Line",
    dataset_version="2025-12-01T19:39:55Z",
    request_url="https://example.invalid/DCM_Street_Center_Line/query",
    retrieved_at="2026-09-30T06:10:28Z",
    raw_digest="sha256:" + "0" * 64,
)


def _is_number(text) -> bool:
    try:
        float(text)
    except (TypeError, ValueError):
        return False
    return True


def centerline(name, oid, width, edge, *, extra_offset=0.0, extend=300.0, ok=True,
               note=None) -> StreetCenterline:
    """Center line parallel to the counterclockwise lot edge, half the width outside it."""
    (a, b) = edge
    length = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = uy, -ux
    offset = (float(width) / 2.0 if _is_number(width) else 30.0) + extra_offset
    start = (a[0] - ux * extend + nx * offset, a[1] - uy * extend + ny * offset)
    end = (b[0] + ux * extend + nx * offset, b[1] + uy * extend + ny * offset)
    return StreetCenterline(name, name, oid, ((start, end),), width, ok, note)


def segment(oid, name, width, *, borough="Queens", plain=True, note=None,
            source=SOURCE) -> MappedStreetSegment:
    return MappedStreetSegment(oid, name, borough, width, plain, note, source)


def site_with(*lines, points=RECT):
    return derive_site_geometry(
        LotOutline(tuple(points), CRS, "synthetic tax-lot"),
        StreetData(tuple(lines), ENVELOPE, CRS, "synthetic streets"))


def widths_for(width, *, name="Main Street", borough="Queens", zoning=R6, **kwargs):
    site = site_with(centerline(name, 1, width, SOUTH))
    return derive_frontage_street_widths(
        site, [segment(1, name, width, borough=borough)], zoning, **kwargs)


def confirmed_site_with_raw(width):
    """A real B-03 site whose one confirmed frontage records ``width`` as the mapped width.

    B-03 can only confirm a frontage when the mapped width is one plain number (it places
    the street line at half that width), so a confirmed frontage on a range or inequality
    cannot come out of it today. This builds that case directly to test the policy path.
    """
    site = site_with(centerline("Main Street", 1, "60", SOUTH))
    (frontage,) = site.frontages
    assert frontage.status == FRONTAGE_CONFIRMED
    recorded = () if width is None else (width,)  # B-03 lists only non-null widths
    return replace(site, frontages=(replace(frontage, mapped_width_raw=recorded),))


def assert_needs(frontage):
    assert frontage.street_class == CLASS_NEEDS_STREET_WIDTH
    assert frontage.marker == MARKER_NEEDS_STREET_WIDTH
    assert frontage.possible_classes == (CLASS_WIDE, CLASS_NARROW)
    assert frontage.reasons


# --------------------------------------------------------------------------- known widths


@pytest.mark.parametrize(("raw", "expected", "feet"), [
    ("100", CLASS_WIDE, 100.0),
    ("80", CLASS_WIDE, 80.0),
    ("75", CLASS_WIDE, 75.0),  # D-052-R001: exactly 75 ft is WIDE
    ("75.0", CLASS_WIDE, 75.0),
    ("74.99", CLASS_NARROW, 74.99),
    ("60", CLASS_NARROW, 60.0),
])
def test_known_mapped_width_gives_the_class(raw, expected, feet):
    result = widths_for(raw)
    assert result.status == STATUS_COMPLETE and result.marker is None
    (frontage,) = result.frontages
    assert frontage.street_class == expected
    assert frontage.marker is None and frontage.reasons == ()
    assert frontage.possible_classes == (expected,)
    assert frontage.mapped_width.value == feet
    assert frontage.mapped_width.label == LABEL_CITY_RECORDS
    assert "OBJECTID" not in frontage.mapped_width.basis  # plain words, segment numbers
    assert "segment(s) 1" in frontage.mapped_width.basis
    assert SOURCE.retrieved_at in frontage.mapped_width.basis
    (reading,) = frontage.readings
    assert reading.decision.decision_state == expected
    assert reading.decision.matched_geometry_ref == "DCM OBJECTID=1"
    assert reading.decision.source_version == SOURCE.dataset_version
    assert frontage.sources == (SOURCE,)
    assert frontage.draft_label == DRAFT_LABEL_NOTICE == result.draft_label
    assert [e.status for e in frontage.exceptions] == [EXCEPTION_NOT_APPLICABLE] * 2


def test_corner_lot_gets_a_width_per_frontage():
    site = site_with(centerline("Main Street", 1, "60", SOUTH),
                     centerline("First Avenue", 2, "100", WEST))
    assert site.lot_type.kind == "corner"
    result = derive_frontage_street_widths(
        site, [segment(1, "Main Street", "60"), segment(2, "First Avenue", "100")], R6)
    assert result.status == STATUS_COMPLETE
    assert result.frontage("Main Street").street_class == CLASS_NARROW
    assert result.frontage("First Avenue").street_class == CLASS_WIDE
    assert result.frontage("First Avenue").mapped_width.value == 100.0


# --------------------------------------------------------------------------- bounds (D-052-R003)


@pytest.mark.parametrize(("raw", "expected"), [
    ("<75", CLASS_NARROW),
    (">75", CLASS_WIDE),
    (">=75", CLASS_WIDE),
    ("75-90", CLASS_WIDE),
])
def test_bound_on_one_side_of_75_issues_a_class(raw, expected):
    result = derive_frontage_street_widths(
        confirmed_site_with_raw(raw), [segment(1, "Main Street", raw)], R6)
    (frontage,) = result.frontages
    assert frontage.street_class == expected
    # Not one number, so no single width is stated even though the class is known.
    assert frontage.mapped_width.value is None
    assert frontage.mapped_width.label == LABEL_UNKNOWN


@pytest.mark.parametrize("raw", ["<=75", "60-75", "70-80", ">70"])
def test_bound_straddling_75_needs_street_width(raw):
    result = derive_frontage_street_widths(
        confirmed_site_with_raw(raw), [segment(1, "Main Street", raw)], R6)
    assert result.status == STATUS_NEEDS_STREET_WIDTH
    assert result.marker == MARKER_NEEDS_STREET_WIDTH
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert frontage.readings[0].decision.decision_state == DECISION_UNRESOLVED
    assert any("both sides of 75 ft" in r for r in frontage.reasons)
    assert "Main Street" in result.notes[-1] and "narrow-street" in result.notes[-1]


def test_range_width_through_site_geometry_needs_street_width():
    # B-03 cannot place a street line for "60-75", so the frontage stays unconfirmed.
    result = widths_for("60-75")
    (frontage,) = result.frontages
    assert frontage.frontage_status == FRONTAGE_UNCERTAIN
    assert_needs(frontage)
    assert any("not confirmed" in r for r in frontage.reasons)
    assert any("both sides of 75 ft" in r for r in frontage.reasons)
    assert frontage.mapped_width.value is None


@pytest.mark.parametrize("raw", ["Unknown", "Width Irregular", "varies", "~80",
                                 "Unknown but >75", None, ""])
def test_width_text_without_a_usable_width_needs_street_width(raw):
    result = derive_frontage_street_widths(
        confirmed_site_with_raw(raw), [segment(1, "Main Street", raw)], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    decision = frontage.readings[0].decision
    assert decision.decision_state == DECISION_UNKNOWN
    assert decision.routed_to == ROUTED_TO_MAP_RESOLUTION
    assert decision.original_label == raw
    assert any("gives no usable width" in r for r in frontage.reasons)


# --------------------------------------------------------------------------- no match


def test_no_street_center_line_near_the_lot_needs_street_width():
    site = site_with()  # complete street data, but no street anywhere near the lot
    result = derive_frontage_street_widths(site, [], R6)
    assert result.frontages == ()
    assert result.status == STATUS_NEEDS_STREET_WIDTH
    assert result.marker == MARKER_NEEDS_STREET_WIDTH
    assert "No street frontage" in result.notes[0]


def test_matched_segment_missing_from_the_street_data_needs_street_width():
    site = site_with(centerline("Main Street", 1, "100", SOUTH))
    result = derive_frontage_street_widths(site, [segment(99, "Other Street", "100")], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert frontage.readings == ()
    assert "not in the street data given" in frontage.reasons[0]
    assert frontage.mapped_width.value is None


def test_frontage_without_segment_numbers_needs_street_width():
    site = site_with(centerline("Main Street", None, "100", SOUTH))
    result = derive_frontage_street_widths(site, [], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert frontage.reasons[0] == "No City Map street center line was matched to this frontage."


def test_refused_site_geometry_needs_street_width():
    site = derive_site_geometry(LotOutline(tuple(RECT), {"wkid": 4326}, "degrees"), None)
    result = derive_frontage_street_widths(site, [], R6)
    assert result.status == STATUS_NEEDS_STREET_WIDTH
    assert result.notes[0].startswith("No frontage could be measured")


def test_street_data_differing_from_the_frontage_data_needs_street_width():
    site = site_with(centerline("Main Street", 1, "100", SOUTH))
    result = derive_frontage_street_widths(site, [segment(1, "Main Street", "60")], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert any("differs from the data" in r for r in frontage.reasons)


def test_conflicting_records_for_one_segment_need_street_width():
    site = site_with(centerline("Main Street", 1, "100", SOUTH))
    result = derive_frontage_street_widths(
        site, [segment(1, "Main Street", "100"), segment(1, "Main Street", "60")], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert any("conflicting records" in r for r in frontage.reasons)


def test_same_segment_read_twice_with_the_same_facts_is_not_a_conflict():
    site = site_with(centerline("Main Street", 1, "100", SOUTH))
    second_page = replace(SOURCE, request_url="https://example.invalid/page-2",
                          raw_digest="sha256:" + "1" * 64)
    result = derive_frontage_street_widths(
        site, [segment(1, "Main Street", "100"),
               segment(1, "Main Street", "100", source=second_page)], R6)
    assert result.frontages[0].street_class == CLASS_WIDE
    assert result.frontages[0].sources == (SOURCE,)  # the first reading is kept


# --------------------------------------------------------------------------- coverage, status


def test_unconfirmed_frontage_never_takes_a_class():
    # The lot line sits 8 ft off the street line: B-03 leaves the frontage uncertain.
    site = site_with(centerline("Main Street", 1, "100", SOUTH, extra_offset=8.0))
    result = derive_frontage_street_widths(site, [segment(1, "Main Street", "100")], R6)
    (frontage,) = result.frontages
    assert frontage.frontage_status == FRONTAGE_UNCERTAIN
    assert_needs(frontage)
    assert frontage.readings[0].decision.decision_state == DECISION_UNRESOLVED
    assert "frontage coverage not established" in (
        frontage.readings[0].decision.classification_reason)


def test_width_changing_along_one_frontage_needs_street_width():
    # One street, two City Map segments: 60 ft wide west of x = 50, 100 ft wide east of it.
    # Each center line sits half its own width south of the lot line, so B-03 confirms the
    # frontage on both segments.
    long_lot = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    west_part = StreetCenterline("Main Street", "Main Street", 1,
                                 (((-300.0, -30.0), (50.0, -30.0)),), "60", True)
    east_part = StreetCenterline("Main Street", "Main Street", 2,
                                 (((50.0, -50.0), (400.0, -50.0)),), "100", True)
    site = site_with(west_part, east_part, points=long_lot)
    (street,) = site.frontages
    assert street.status == FRONTAGE_CONFIRMED and street.segment_object_ids == (1, 2)
    result = derive_frontage_street_widths(
        site, [segment(1, "Main Street", "60"), segment(2, "Main Street", "100")], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert any("part is wide and part is narrow" in r for r in frontage.reasons)
    assert "changes along this frontage" in frontage.mapped_width.reason


def test_special_city_map_status_needs_street_width():
    result = derive_frontage_street_widths(
        confirmed_site_with_raw("100"),
        [segment(1, "Main Street", "100", plain=False,
                 note="the City Map flags it (paper_street='Y'); needs review")], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert any("paper_street='Y'" in r for r in frontage.reasons)


def test_undocumented_source_needs_street_width():
    undocumented = replace(SOURCE, raw_digest=None)
    site = site_with(centerline("Main Street", 1, "100", SOUTH))
    result = derive_frontage_street_widths(
        site, [segment(1, "Main Street", "100", source=undocumented)], R6)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert any("not on record" in r for r in frontage.reasons)


# --------------------------------------------------------------------------- ZR 12-10 exceptions


def test_exceptions_not_checked_without_zoning_needs_street_width():
    result = widths_for("100", zoning=None)
    (frontage,) = result.frontages
    assert_needs(frontage)
    alternate = frontage.exceptions[0]
    assert alternate.status == EXCEPTION_NOT_CHECKED
    assert "zoning districts are not known" in alternate.reason
    # The mapped width itself is still a sourced fact.
    assert frontage.mapped_width.value == 100.0
    assert frontage.mapped_width.label == LABEL_CITY_RECORDS


@pytest.mark.parametrize("district", ["C6-4", "C5-3", "C6-6"])
def test_alternate_width_district_needs_street_width(district):
    zoning = LotZoningContext((district,), None, "synthetic zoning record")
    result = widths_for("60", zoning=zoning)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert frontage.exceptions[0].status == EXCEPTION_MAY_APPLY
    assert frontage.exceptions[0].provision_id == "zr-12-10-c-district-alternate-width"


def test_named_street_in_manhattan_needs_street_width_until_resolved():
    result = widths_for("100", name="Broadway", borough="Manhattan")
    (frontage,) = result.frontages
    assert_needs(frontage)
    named = frontage.readings[0].named_street
    assert named.status == EXCEPTION_MAY_APPLY
    assert "community district" in named.reason


def test_named_street_in_another_community_district_is_cleared():
    zoning = LotZoningContext(("C4-6",), 9, "synthetic zoning record")
    result = widths_for("100", name="Broadway", borough="Manhattan", zoning=zoning)
    (frontage,) = result.frontages
    assert frontage.street_class == CLASS_WIDE
    assert frontage.readings[0].named_street.status == EXCEPTION_NOT_APPLICABLE


def test_named_street_in_its_community_district_needs_street_width():
    zoning = LotZoningContext(("C4-6",), 7, "synthetic zoning record")
    result = widths_for("100", name="Broadway", borough="Manhattan", zoning=zoning)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert frontage.readings[0].named_street.provision_id == "zr-12-10-named-street-wide"


def test_same_street_name_in_another_borough_is_not_a_named_street():
    result = widths_for("100", name="Broadway", borough="Queens")
    assert result.frontages[0].street_class == CLASS_WIDE
    assert "Broadway in Queens is not one of them" in result.frontages[0].exceptions[1].reason


def test_named_street_with_an_unrecognized_borough_goes_to_the_matcher():
    result = widths_for("100", name="Broadway", borough="CW")  # DCM domain value, not a borough
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert frontage.readings[0].named_street.status == EXCEPTION_MAY_APPLY


def test_unloadable_zr_snapshot_leaves_exceptions_unchecked(tmp_path: Path):
    broken = Zr1210Exceptions.load(SnapshotStore(tmp_path / "missing"))
    result = widths_for("100", exceptions=broken)
    (frontage,) = result.frontages
    assert_needs(frontage)
    assert {e.status for e in frontage.exceptions} == {EXCEPTION_NOT_CHECKED}
    assert "could not be loaded" in frontage.exceptions[0].reason
    assert result.provenance["zr_12_10_snapshot"]["content_digest_sha256"] is None


def test_never_a_silent_narrow_default():
    cases = [
        widths_for("Unknown"), widths_for("60-75"), widths_for("100", zoning=None),
        derive_frontage_street_widths(confirmed_site_with_raw("<=75"),
                                      [segment(1, "Main Street", "<=75")], R6),
    ]
    for result in cases:
        for frontage in result.frontages:
            assert frontage.street_class != CLASS_NARROW
            assert CLASS_WIDE in frontage.possible_classes


def test_default_exceptions_fail_safe_when_the_snapshot_cannot_load(monkeypatch):
    from app.spatial.frontage_street_width import exceptions as module

    def broken():
        raise RuntimeError("snapshot store unavailable")

    monkeypatch.setattr(module, "_packaged", broken)
    checks = module.default_exceptions()
    assert checks.snapshot_sha256 is None
    assert "RuntimeError" in checks.unavailable_reason
    result = widths_for("100")  # derive falls back to default_exceptions()
    assert_needs(result.frontages[0])


def test_default_exceptions_use_the_packaged_zr_12_10_snapshot():
    checks = default_exceptions()
    assert checks.snapshot_sha256 == SnapshotStore().get("zr-12-10").content_digest_sha256
    result = widths_for("100")
    assert result.provenance["zr_12_10_snapshot"] == {
        "snapshot_id": "zr-12-10", "content_digest_sha256": checks.snapshot_sha256}
