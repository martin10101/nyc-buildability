"""Benchmark: multi-lot site math on block 7334, Queens, tax lots 1 and 70 (queue item B-07).

Recorded official data, replayed offline through the real connectors:

- tax lot 70 (215-16 Northern Blvd): the B-01 pack, ``fixtures/benchmark_215_16_northern``;
- tax lot 1 (215-10 Northern Blvd) and the DCM street center lines within 150 ft of both
  lots: ``fixtures/benchmark_block_7334_lots_1_70`` (captured 2026-10-01, MANIFEST.json).

DOB BIS job 421803891 (B-01 pack) is an alteration filed "TO REFLECT ONE (1) ZONING LOT AND
(2) TAX LOTS (LOT #1 & #70)". That is evidence of a filing, not a verified zoning lot: the
zoning-lot status stays "Check needed" whichever lots are selected (owner, 2026-10-01).

Observed on the recorded outlines (EPSG:2263, 0.01 ft): lots 1 and 70 share one 99.98 ft lot
line. Lot 70 alone: corner, 215 Place 99.98 ft and Northern Boulevard 103.88 ft (the B-03
benchmark). Lot 1 alone: corner, 215 Street 99.98 ft and Northern Boulevard 99.25 ft. Both:
one corner site fronting 215 Street, Northern Boulevard (203.13 ft) and 215 Place.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors import dcm_street_centerline_arcgis as dcm
from app.connectors import mappluto_geometry_arcgis, pluto_soda
from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.dcm_street_centerline_geometry import parse_segment_geometry_page
from app.profile.existing_floor_area import (
    DobRecordSet,
    ExistingFloorAreaEvidence,
    resolve_existing_zoning_floor_area,
)
from app.resilience.transport import TransportResponse
from app.spatial.frontage_street_width import CLASS_NARROW, CLASS_WIDE, mapped_segments_from_pages
from app.spatial.multi_lot_site import (
    COMBINATION_OFFERED,
    COMBINATION_SINGLE_LOT,
    EXISTING_ATTACHED,
    ZONING_LOT_CHECK_NEEDED,
    build_lot_choice,
    derive_multi_lot_site,
    site_lot_from_sources,
    study_lot_selection,
    study_lots,
)
from app.spatial.site_geometry import LABEL_CITY_RECORDS, LABEL_TAX_MAP, street_data_from_pages
from app.spatial.site_geometry.results import STATUS_COMPLETE
from tests.profile.site_fact_contract import assert_valid_site_fact
from tests.spatial import _northern_replay as lot70_pack
from tests.spatial._study_contract import assert_valid_study_part as assert_valid

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_block_7334_lots_1_70"
MANIFEST_DOC = json.loads((PACK / "MANIFEST.json").read_text("utf-8"))
MANIFEST = {entry["file"]: entry for entry in MANIFEST_DOC["files"]}
ENVELOPE = tuple(MANIFEST_DOC["dcm_envelope_epsg2263"])
DCM_FILE = "dcm_street_centerline_envelope_lots_1_70.json"
LOT_1, LOT_70 = "4073340001", "4073340070"
NORTHERN, PLACE, STREET = "Northern Boulevard", "215 Place", "215 Street"
ZONING_LOT_JOB = "DOB BIS job 421803891, document 01"
_CLOCK = datetime(2026, 10, 1, 22, 20, tzinfo=UTC)
_FILES = {entry["url"]: PACK / name for name, entry in MANIFEST.items()}
_FILES.update({entry["url"]: lot70_pack.PACK / name for name, entry in lot70_pack.MANIFEST.items()})


def _transport(url: str, headers: dict, timeout: float) -> TransportResponse:
    return TransportResponse(200, _FILES[url].read_bytes().decode("utf-8"))


def _geometry(bbl: str):
    return mappluto_geometry_arcgis.fetch_lot_geometry(
        bbl, transport=_transport, sleep=lambda _s: None, clock=lambda: _CLOCK,
        rng=Random(0), correlation_id="b07-benchmark")


def _pluto(bbl: str):
    return pluto_soda.fetch_by_bbl(
        bbl, transport=_transport, sleep=lambda _s: None, clock=lambda: _CLOCK,
        correlation_id="b07-benchmark", observation_event_id="b07-benchmark")


def _record_set(name: str) -> DobRecordSet:
    entry = lot70_pack.MANIFEST[name]
    rows = json.loads((lot70_pack.PACK / name).read_bytes().decode("utf-8"))
    return DobRecordSet(entry["dataset_id"], rows, entry["retrieved_at"], entry["url"])


def _evidence() -> ExistingFloorAreaEvidence:
    names = sorted(lot70_pack.MANIFEST)
    return ExistingFloorAreaEvidence(
        tuple(_record_set(n) for n in names if n.startswith("dob_bis_jobs_")),
        tuple(_record_set(n) for n in names if n.startswith(("dob_bis_co_", "dob_now_co_"))))


@pytest.fixture(scope="module")
def existing():
    evidence = _evidence()
    return {bbl: resolve_existing_zoning_floor_area(bbl, evidence) for bbl in (LOT_1, LOT_70)}


@pytest.fixture(scope="module")
def inputs(existing):
    entry = MANIFEST[DCM_FILE]
    page = parse_segment_geometry_page(
        DcmTransport(url=entry["url"], status=200, body=(PACK / DCM_FILE).read_text("utf-8"),
                     retrieved_at=entry["retrieved_at"]), correlation_id="b07-benchmark")
    lots = {bbl: site_lot_from_sources(bbl, _geometry(bbl), _pluto(bbl),
                                       existing_floor_area=existing[bbl])
            for bbl in (LOT_1, LOT_70)}
    choice = build_lot_choice([LOT_1, LOT_70], lots)
    return choice, street_data_from_pages([page], envelope=ENVELOPE), mapped_segments_from_pages(
        [page])


def _site(inputs, picked):
    choice, streets, segments = inputs
    return derive_multi_lot_site(choice, picked, streets, street_segments=segments)


def _frontages(site) -> dict[str, float]:
    return {f.street_name: f.length.value for f in site.geometry.frontages}


# --------------------------------------------------------------------- recorded fixtures


def test_fixture_bytes_and_urls_are_as_recorded():
    for name, entry in MANIFEST.items():
        body = (PACK / name).read_bytes()
        assert hashlib.sha256(body).hexdigest() == entry["sha256"], name
        assert (len(body), entry["http_status"]) == (entry["bytes"], 200), name
    assert MANIFEST[f"mappluto_lot_{LOT_1}_epsg2263.json"]["url"] == (
        mappluto_geometry_arcgis.build_lot_query_url(LOT_1))
    assert MANIFEST[f"pluto_64uk-42ks_bbl_{LOT_1}.json"]["url"] == (
        f"{pluto_soda.BASE_URL}?bbl={LOT_1}")
    assert MANIFEST[DCM_FILE]["url"] == dcm.build_segment_query_url(envelope=ENVELOPE)
    assert MANIFEST["dcm_layer_metadata.json"]["url"] == dcm.build_metadata_url()
    assert sorted(p.name for p in PACK.iterdir()) == sorted(
        [*MANIFEST, "MANIFEST.json", "README.md", ".gitattributes"])


# ------------------------------------------------------------ selecting 1, 2 or all lots


def test_lot_choice_lists_both_lots_with_their_recorded_sizes(inputs):
    choice = inputs[0]
    assert [(e.bbl, e.size.value, e.size.label) for e in choice.entries] == [
        (LOT_1, 9925.0, LABEL_CITY_RECORDS), (LOT_70, 10075.0, LABEL_CITY_RECORDS)]


def test_lot_70_alone_is_the_b03_benchmark(inputs):
    site = _site(inputs, [LOT_70])
    assert site.combination.status == COMBINATION_SINGLE_LOT
    assert site.geometry.status == STATUS_COMPLETE
    assert site.geometry.lot_type.kind == "corner"
    assert _frontages(site) == {PLACE: 99.98, NORTHERN: 103.88}
    assert site.geometry.lot_area.value == 10387.99
    assert (site.geometry.area_check.difference_sq_ft,
            site.geometry.area_check.difference_pct) == (312.99, 3.11)


def test_lot_1_alone(inputs):
    site = _site(inputs, [LOT_1])
    assert site.geometry.status == STATUS_COMPLETE
    assert site.geometry.lot_type.kind == "corner"
    assert _frontages(site) == {STREET: 99.98, NORTHERN: 99.25}
    assert site.geometry.lot_area.value == 9922.45
    assert site.lot_area_sum.value == 9925.0
    assert site.geometry.area_check.difference_sq_ft == -2.55


def test_both_lots_make_one_corner_site_with_the_shared_line_removed(inputs):
    site = _site(inputs, None)
    assert site.combination.status == COMBINATION_OFFERED
    (shared,) = site.combination.shared_lines
    assert (shared.first_bbl, shared.second_bbl, shared.length_ft) == (LOT_1, LOT_70, 99.98)
    geometry = site.geometry
    assert geometry.status == STATUS_COMPLETE
    assert geometry.lot_type.kind == "corner"
    assert geometry.lot_type.label == LABEL_TAX_MAP
    assert _frontages(site) == {PLACE: 99.98, STREET: 99.98, NORTHERN: 203.13}
    # The removed line is not a lot line of the combined site: lot 1's east line (lot 70's
    # west line) ran between these two shared corners; no combined edge joins them.
    shared_ends = {(1048788.63, 216408.05), (1048810.23, 216310.44)}
    ring = [(round(x, 2), round(y, 2)) for x, y in site.outline.exterior]
    assert shared_ends <= set(ring)
    assert not any({a, b} == shared_ends for a, b in zip(ring, ring[1:], strict=False))
    assert len(geometry.edges) == 7
    assert geometry.lot_area.value == 20310.44
    assert geometry.lot_area.basis.startswith(
        "Planar area of the combined MapPLUTO 26v2 tax-lot (lots 1 and 70) outline")
    # Combined area = sum of the recorded lot areas, checked against the combined outline.
    assert site.lot_area_sum.value == 20000.0
    assert (geometry.area_check.difference_sq_ft, geometry.area_check.difference_pct) == (
        310.44, 1.55)
    widths = {f.street_name: f.street_class for f in site.street_widths.frontages}
    assert widths == {NORTHERN: CLASS_WIDE, PLACE: CLASS_NARROW, STREET: CLASS_NARROW}
    assert site.street_widths.marker is None


# ------------------------------------------------------ owner constraints (2026-10-01)


@pytest.mark.parametrize(("picked", "not_selected"), [
    ([LOT_70], (LOT_1,)), ([LOT_1], ()), (None, ())])
def test_zoning_lot_stays_check_needed_although_a_filing_names_both_lots(
        inputs, picked, not_selected):
    zoning_lot = _site(inputs, picked).zoning_lot
    assert (zoning_lot.status, zoning_lot.label, zoning_lot.verified) == (
        ZONING_LOT_CHECK_NEEDED, "Check needed", False)
    assert [m["document_ref"] for m in zoning_lot.recorded_mentions] == [ZONING_LOT_JOB]
    assert "ONE (1) ZONING LOT AND (2) TAX LOTS" in zoning_lot.recorded_mentions[0]["text"]
    assert zoning_lot.named_lots_not_selected == not_selected
    assert "The app does not verify the zoning lot" in zoning_lot.reason


def test_existing_buildings_are_attached_per_lot_unchanged_and_not_added(inputs, existing):
    before = {bbl: json.dumps(result.fact, sort_keys=True) for bbl, result in existing.items()}
    site = _site(inputs, None)
    assert [(e.bbl, e.status) for e in site.existing_buildings] == [
        (LOT_1, EXISTING_ATTACHED), (LOT_70, EXISTING_ATTACHED)]
    for entry in site.existing_buildings:
        assert entry.result is existing[entry.bbl]
        assert json.dumps(entry.result.fact, sort_keys=True) == before[entry.bbl]
        assert_valid_site_fact(entry.result.fact)
        # B-05 leaves both Unknown — enter: the DOB figures stay set aside, per lot.
        assert entry.result.fact["value"] is None
    set_aside = {e.bbl: sorted(c["value"] for c in e.result.considered if c["value"])
                 for e in site.existing_buildings}
    assert set_aside == {LOT_1: [14150, 39772], LOT_70: [39934]}
    # No set-aside figure, and no total of them, reaches the combined site's own values.
    combined_text = repr((site.notes, site.lot_area_sum, site.geometry, site.zoning_lot))
    figures = (14150, 39772, 39934, 14150 + 39772, 39772 + 39934, 14150 + 39772 + 39934)
    for figure in figures:
        for text in (str(figure), f"{figure:,}"):
            assert text not in combined_text, text


def test_study_shapes_for_each_selection(inputs):
    for picked in ([LOT_1], [LOT_70], None):
        site = _site(inputs, picked)
        for item in study_lots(inputs[0], site.selected_bbls):
            assert_valid(item, "#/$defs/lot")
        assert_valid(study_lot_selection(site), "#/properties/lot_selection")
