"""Benchmark: street width per frontage for 215-16 Northern Blvd, Queens (BBL 4073340070).

Queue item B-04 (plan M1-13 data side, §4 "Street widths") on the recorded B-01 pack,
replayed offline through the real connectors and the B-03 site geometry. Nothing is assumed
about either street: the class is DERIVED from what the recorded DCM data says.

What the recorded data says (fixture README, "Street widths" row; MANIFEST purpose line):
DCM ``Streetwidth`` is "100" for Northern Boulevard (OBJECTID 53832) and "60" for 215 Place
(OBJECTID 11453), both plain mapped streets (Feat_Type Mapped_St, every special flag "N").
Through the accepted classifier and the D-052 policy that gives Northern Boulevard WIDE and
215 Place NARROW - but only because the ZR 12-10 exceptions were checked first against the
lot's recorded zoning (PLUTO 26v2: R6B with a C2-2 overlay). Without that record both
frontages stay "Needs street width".
"""

from __future__ import annotations

import pytest

from app.connectors.dcm_street_centerline_arcgis import DcmTransport, fetch_layer_metadata
from app.connectors.dcm_street_width_policy import (
    DECISION_NARROW,
    DECISION_UNRESOLVED,
    DECISION_WIDE,
    DRAFT_LABEL_NOTICE,
    OWNER_APPROVED_ASSUMPTION_NOTICE,
)
from app.spatial.frontage_street_width import (
    CLASS_NARROW,
    CLASS_NEEDS_STREET_WIDTH,
    CLASS_WIDE,
    EXCEPTION_NOT_APPLICABLE,
    EXCEPTION_NOT_CHECKED,
    MARKER_NEEDS_STREET_WIDTH,
    STATUS_COMPLETE,
    STATUS_NEEDS_STREET_WIDTH,
    street_widths_from_sources,
)
from app.spatial.site_geometry import LABEL_CITY_RECORDS, derive_site_geometry_from_sources

from ._northern_replay import (
    DCM_ENVELOPE,
    DCM_FILE,
    MANIFEST,
    PACK,
    manifest_digest,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

NORTHERN = "Northern Boulevard"
PLACE = "215 Place"
LAYER_FILE = "dcm_layer_metadata.json"


def replay_layer_metadata():
    entry = MANIFEST[LAYER_FILE]
    body = (PACK / LAYER_FILE).read_bytes().decode("utf-8")
    return fetch_layer_metadata(
        fetch=lambda url, _cid: DcmTransport(url=url, status=200, body=body,
                                             retrieved_at=entry["retrieved_at"]),
        correlation_id="b04-benchmark")


@pytest.fixture(scope="module")
def site():
    return derive_site_geometry_from_sources(
        replay_lot_geometry(), [replay_dcm_page()], envelope=DCM_ENVELOPE,
        pluto_result=replay_pluto())


@pytest.fixture(scope="module")
def result(site):
    return street_widths_from_sources(site, [replay_dcm_page()], pluto_result=replay_pluto(),
                                      layer_metadata=replay_layer_metadata())


def test_every_frontage_carries_a_sourced_width(result):
    assert result.status == STATUS_COMPLETE and result.marker is None
    assert [f.street_name for f in result.frontages] == [PLACE, NORTHERN]
    for frontage in result.frontages:
        assert frontage.mapped_width.known
        assert frontage.mapped_width.label == LABEL_CITY_RECORDS
        assert frontage.draft_label == DRAFT_LABEL_NOTICE


@pytest.mark.parametrize(("street", "segment", "raw", "feet", "ambiguity", "decision", "klass"), [
    (NORTHERN, 53832, "100", 100.0, "clean_numeric_ge_75", DECISION_WIDE, CLASS_WIDE),
    (PLACE, 11453, "60", 60.0, "clean_numeric_lt_75", DECISION_NARROW, CLASS_NARROW),
])
def test_class_is_derived_from_the_recorded_dcm_width(
        result, street, segment, raw, feet, ambiguity, decision, klass):
    frontage = result.frontage(street)
    assert frontage.street_class == klass
    assert frontage.marker is None and frontage.possible_classes == (klass,)
    assert frontage.mapped_width.value == feet
    (reading,) = frontage.readings
    assert reading.segment.object_id == segment
    assert reading.segment.mapped_width_raw == raw
    assert reading.segment.borough == "Queens"
    assert reading.segment.plain_mapped_street
    assert reading.classification.ambiguity_class == ambiguity
    assert reading.decision.decision_state == decision
    assert reading.decision.original_label == raw
    assert reading.decision.matched_geometry_ref == f"DCM OBJECTID={segment}"
    assert reading.decision.assumption_notice == OWNER_APPROVED_ASSUMPTION_NOTICE


def test_source_dataset_and_retrieval_are_pinned(result):
    entry = MANIFEST[DCM_FILE]
    for frontage in result.frontages:
        (source,) = frontage.sources
        assert source.source_id == entry["source_id"] == "nyc-dcp-dcm-street-centerline-arcgis"
        assert source.dataset.endswith("/DCM_Street_Center_Line")
        assert source.request_url == entry["url"]
        assert source.retrieved_at == entry["retrieved_at"] == "2026-09-30T06:10:28Z"
        assert source.raw_digest == manifest_digest(DCM_FILE)
        # Layer editingInfo.dataLastEditDate (README: 2025-12-01T19:39:55Z).
        assert source.dataset_version == "2025-12-01T19:39:55Z"
        assert frontage.readings[0].decision.source_version == "2025-12-01T19:39:55Z"
    assert result.provenance["streets"]["raw_digests"] == [manifest_digest(DCM_FILE)]


def test_zr_12_10_exceptions_were_checked_first(result):
    for frontage in result.frontages:
        alternate, named = frontage.exceptions
        assert alternate.status == named.status == EXCEPTION_NOT_APPLICABLE
        assert "zoning districts in PLUTO 26v2 (R6B, C2-2)" in alternate.reason
        assert named.reason == ("ZR 12-10 names Broadway (Manhattan) and Allen Street "
                                f"(Manhattan); {frontage.street_name} is not one of them")
    zoning = result.provenance["zoning"]
    assert zoning["dataset_version"] == "26v2"
    assert zoning["request_url"] == replay_pluto().request_url


def test_without_the_zoning_record_both_frontages_need_street_width(site):
    result = street_widths_from_sources(site, [replay_dcm_page()])
    assert result.status == STATUS_NEEDS_STREET_WIDTH
    assert result.marker == MARKER_NEEDS_STREET_WIDTH
    for frontage in result.frontages:
        assert frontage.street_class == CLASS_NEEDS_STREET_WIDTH
        assert frontage.possible_classes == (CLASS_WIDE, CLASS_NARROW)
        assert frontage.exceptions[0].status == EXCEPTION_NOT_CHECKED
        assert frontage.readings[0].decision.decision_state == DECISION_UNRESOLVED
        # The recorded width is still reported as a sourced fact.
        assert frontage.mapped_width.label == LABEL_CITY_RECORDS
    assert result.frontage(NORTHERN).mapped_width.value == 100.0
    # Without the layer metadata the source version falls back to the retrieval time,
    # labelled so it is never mistaken for a dataset version.
    reading = result.frontage(NORTHERN).readings[0]
    assert reading.segment.source.dataset_version is None
    assert reading.decision.source_version == "retrieved_at:2026-09-30T06:10:28Z"
