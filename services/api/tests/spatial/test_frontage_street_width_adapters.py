"""Adapters from connector results to street-width inputs (queue item B-04).

Offline: the recorded 215-16 Northern Blvd DCM page and PLUTO row, replayed through the
real connectors, then altered in memory to reach the fail-closed branches.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from app.spatial.frontage_street_width import (
    CLASS_NARROW,
    CLASS_NEEDS_STREET_WIDTH,
    CLASS_WIDE,
    MARKER_NEEDS_STREET_WIDTH,
    STATUS_NEEDS_STREET_WIDTH,
    mapped_segments_from_pages,
    street_widths_from_sources,
    zoning_context_from_pluto,
)
from app.spatial.site_geometry import derive_site_geometry_from_sources

from ._northern_replay import (
    DCM_ENVELOPE,
    DCM_FILE,
    MANIFEST,
    manifest_digest,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)


def _with_segment_change(page, target, **changes):
    entries = [replace(e, segment=replace(e.segment, **changes))
               if e.segment.object_id == target else e for e in page.entries]
    return replace(page, entries=entries)


def test_every_recorded_segment_is_read_with_its_page_as_source():
    segments = mapped_segments_from_pages([replay_dcm_page()])
    assert [s.object_id for s in segments] == [2821, 3134, 3656, 11453, 16384, 53832]
    by_id = {s.object_id: s for s in segments}
    assert (by_id[53832].street_name, by_id[53832].mapped_width_raw) == ("Northern Boulevard",
                                                                          "100")
    assert (by_id[11453].street_name, by_id[11453].mapped_width_raw) == ("215 Place", "60")
    assert all(s.plain_mapped_street and s.status_note is None for s in segments)
    source = by_id[53832].source
    assert source.documented
    assert source.request_url == MANIFEST[DCM_FILE]["url"]
    assert source.raw_digest == manifest_digest(DCM_FILE)
    assert source.dataset_version is None  # no layer metadata given


@pytest.mark.parametrize(("change", "expected"), [
    ({"paper_street": "Y"}, "paper_street='Y'"),
    ({"record_street": "Y"}, "record_street='Y'"),
    ({"stair_street": None}, "stair_street=None"),
    ({"marginal_wharf": "Y"}, "marginal_wharf='Y'"),
    ({"feat_type": "Former_St"}, "not a mapped street"),
])
def test_special_street_status_is_not_a_plain_mapped_street(change, expected):
    page = _with_segment_change(replay_dcm_page(), 53832, **change)
    by_id = {s.object_id: s for s in mapped_segments_from_pages([page])}
    assert not by_id[53832].plain_mapped_street
    assert expected in by_id[53832].status_note
    assert by_id[11453].plain_mapped_street


def test_segment_without_object_id_is_surfaced_and_fails_closed():
    # Review 265 F1: a DCM feature with no OBJECTID is kept, never dropped, and the frontage
    # it lies along gets "Needs street width" - on the recorded pack, end to end.
    page = _with_segment_change(replay_dcm_page(), 53832, object_id=None)
    segments = mapped_segments_from_pages([page])
    unidentified = [s for s in segments if s.object_id is None]
    assert [(s.street_name, s.mapped_width_raw) for s in unidentified] == [
        ("Northern Boulevard", "100")]
    site = derive_site_geometry_from_sources(
        replay_lot_geometry(), [page], envelope=DCM_ENVELOPE, pluto_result=replay_pluto())
    result = street_widths_from_sources(site, [page], pluto_result=replay_pluto())
    northern = result.frontage("Northern Boulevard")
    assert northern.street_class == CLASS_NEEDS_STREET_WIDTH
    assert northern.marker == MARKER_NEEDS_STREET_WIDTH
    assert northern.possible_classes == (CLASS_WIDE, CLASS_NARROW)
    assert northern.readings == () and northern.mapped_width.value is None
    assert result.frontage("215 Place").street_class == CLASS_NARROW
    assert result.status == STATUS_NEEDS_STREET_WIDTH
    assert "without a segment number" in result.notes[0]


def test_zoning_context_from_the_recorded_pluto_row():
    zoning = zoning_context_from_pluto(replay_pluto())
    assert zoning.zoning_districts == ("R6B", "C2-2")
    assert zoning.community_district is None  # PLUTO cd "411" is never decoded here
    assert zoning.source == "PLUTO 26v2"
    assert zoning.provenance["dataset_version"] == "26v2"


def test_overlay_alone_never_stands_in_for_the_zoning_district():
    pluto = replay_pluto()
    facts = [f for f in pluto.facts if f.get("original_field_name") != "zonedist1"]
    zoning = zoning_context_from_pluto(replace(pluto, facts=facts))
    assert zoning.zoning_districts == ()


def test_no_pluto_match_gives_no_districts():
    zoning = zoning_context_from_pluto(replace(replay_pluto(), status="no_match", facts=[]))
    assert zoning.zoning_districts == ()

