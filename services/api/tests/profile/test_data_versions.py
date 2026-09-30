"""Pinned data versions and the "Out of date" rule (queue item B-06; check C-7, data side).

C-7 (competitor review section D): "Data versions shown and current". The rule
(``app.profile.data_versions``): a pinned source is "Out of date" only when a newer
published version of the same dataset is on record (the plan gives no age threshold). An
unknown or unreadable version, or a pin with nothing to compare against, is "Version
unknown" and never current.

Offline. The data is recorded official data:

- the B-01 pack for 215-16 Northern Blvd (``tests/fixtures/benchmark_215_16_northern``):
  PLUTO 26v2, MapPLUTO 26v2, DCM layer ``dataLastEditDate`` 2025-12-01T19:39:55Z and the
  DOB filings, all captured 2026-09-30;
- the M1-T002 PLUTO fixtures (``tests/fixtures/pluto``), captured 2026-07-16 at 26v1: F01 (a
  lot record) and F09 (the ``$select=version`` probe).

Inputs marked SYNTHETIC are hand-made version strings that exercise the rule's edges.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors import pluto_soda
from app.connectors.dcm_street_centerline_arcgis import DcmTransport, fetch_layer_metadata
from app.contracts.study_contracts import validate_results_document
from app.profile.builder import build_property_profile
from app.profile.data_versions import (
    OUT_OF_DATE_EXCEPTION_LABEL,
    STATUS_CURRENT,
    STATUS_OUT_OF_DATE,
    STATUS_VERSION_UNKNOWN,
    PinnedSource,
    PublishedVersion,
    assess_data_versions,
    assess_source,
    pin_from_record,
    pin_from_site_fact_source,
    pins_from_site_facts,
    published_from_pins,
)
from app.profile.existing_floor_area import (
    DobRecordSet,
    ExistingFloorAreaEvidence,
    resolve_existing_zoning_floor_area,
)
from app.profile.site_facts import PLUTO_DATASET_NAME, build_site_facts
from app.resilience.transport import TransportResponse
from app.spatial.frontage_street_width import street_widths_from_sources
from app.spatial.site_geometry import derive_site_geometry_from_sources
from tests.spatial._northern_replay import (
    BBL,
    DCM_ENVELOPE,
    MANIFEST,
    PACK,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
PLUTO_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
RESULTS_FIXTURE = (REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
                   / "synthetic_all_answers_available.json")
RESULTS_SCHEMA = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1" / "results.schema.json"
PLUTO_FILE = "pluto_64uk-42ks_bbl_4073340070.json"
MAPPLUTO_FILE = "mappluto_lot_4073340070_epsg2263.json"
DCM_LAYER_FILE = "dcm_layer_metadata.json"
MAPPLUTO = "MapPLUTO (nyc-dcp-mappluto-arcgis)"


def _pluto_site_facts(body: str, bbl: str, retrieved_at: str):
    """A recorded PLUTO body through the real connector, profile builder and B-02 site
    facts, stamped with the recorded retrieval time."""
    moment = datetime.fromisoformat(retrieved_at)
    result = pluto_soda.fetch_by_bbl(
        bbl, transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda _s: None, clock=lambda: moment,
        correlation_id="b06", observation_event_id="b06")
    return build_site_facts(build_property_profile(result, clock=lambda: moment))


def _pluto_fixture(name: str) -> dict:
    return json.loads((PLUTO_FIXTURES / name).read_text("utf-8"))


@pytest.fixture(scope="module")
def benchmark_pluto_facts():
    entry = MANIFEST[PLUTO_FILE]
    body = (PACK / PLUTO_FILE).read_bytes().decode("utf-8")
    return _pluto_site_facts(body, BBL, entry["retrieved_at"])


@pytest.fixture(scope="module")
def f01_facts():
    fixture = _pluto_fixture("F01_single_lot_normal.json")
    return _pluto_site_facts(fixture["response_body_raw"], "1000010100",
                             fixture["retrieval_timestamp_utc"])


@pytest.fixture(scope="module")
def f09_probe() -> PublishedVersion:
    """The recorded PLUTO version probe: 26v1 on 2026-07-16."""
    fixture = _pluto_fixture("F09_version_select.json")
    (row,) = json.loads(fixture["response_body_raw"])
    return PublishedVersion(PLUTO_DATASET_NAME, row["version"],
                            fixture["retrieval_timestamp_utc"], fixture["request_url"])


@pytest.fixture(scope="module")
def benchmark_spatial():
    site = derive_site_geometry_from_sources(
        replay_lot_geometry(), [replay_dcm_page()], envelope=DCM_ENVELOPE,
        pluto_result=replay_pluto())
    entry = MANIFEST[DCM_LAYER_FILE]
    body = (PACK / DCM_LAYER_FILE).read_bytes().decode("utf-8")
    metadata = fetch_layer_metadata(
        fetch=lambda url, _cid: DcmTransport(url=url, status=200, body=body,
                                             retrieved_at=entry["retrieved_at"]),
        correlation_id="b06-benchmark")
    widths = street_widths_from_sources(site, [replay_dcm_page()], pluto_result=replay_pluto(),
                                        layer_metadata=metadata)
    return site, widths


def _dcm_pins(widths) -> tuple[PinnedSource, ...]:
    """The distinct DCM sources behind the street widths (B-04 records the layer's
    ``dataLastEditDate`` as each segment source's ``dataset_version``)."""
    return tuple(dict.fromkeys(
        pin_from_record(asdict(source), dataset=source.dataset)
        for frontage in widths.frontages for source in frontage.sources))


def _pin(version, dataset=PLUTO_DATASET_NAME) -> PinnedSource:
    return PinnedSource(dataset, version, "2026-01-01T00:00:00Z", "synthetic://pin")


def _seen(version, dataset=PLUTO_DATASET_NAME, seen_at="2026-09-30T00:00:00Z") -> PublishedVersion:
    return PublishedVersion(dataset, version, seen_at, "synthetic://published")


# --- pinned version present -------------------------------------------------------------


def test_every_sourced_site_fact_is_pinned_with_its_version_and_retrieval_time(
        benchmark_pluto_facts) -> None:
    pins = pins_from_site_facts(benchmark_pluto_facts.facts)
    entry = MANIFEST[PLUTO_FILE]
    # One PLUTO retrieval serves every PLUTO-sourced fact; the existing zoning floor area is
    # unknown with no source, so it has no pin.
    (pin,) = pins
    assert (pin.dataset, pin.version, pin.retrieved_at, pin.query_ref) == (
        "PLUTO (64uk-42ks)", "26v2", entry["retrieved_at"], entry["url"])
    sourced = [fact["fact_id"] for fact in benchmark_pluto_facts.facts if fact["source"]]
    assert list(pin.fact_ids) == sourced
    assert f"{BBL}:lot_area" in pin.fact_ids and f"{BBL}:zoning_district:1" in pin.fact_ids
    assert f"{BBL}:existing_zoning_floor_area" not in pin.fact_ids


def test_sources_without_a_dataset_are_not_pinned() -> None:
    # An architect entry or a stated assumption names no dataset: there is no version to check.
    entry = {"kind": "architect_entry", "dataset": None, "dataset_version": None,
             "retrieved_at": "2026-09-30T00:00:00Z", "query_ref": None,
             "document_ref": None, "statement": None}
    assert pin_from_site_fact_source(entry) is None
    assert pin_from_site_fact_source(None) is None


# --- a newer version known -> "Out of date" with the reason -----------------------------


def test_a_newer_published_version_marks_the_source_out_of_date(
        f01_facts, benchmark_pluto_facts, f09_probe) -> None:
    pins = pins_from_site_facts(f01_facts.facts)
    published = published_from_pins(pins_from_site_facts(benchmark_pluto_facts.facts))
    report = assess_data_versions(pins, (*published, f09_probe))

    (source,) = report.sources
    assert (source.status, source.label, source.exception_label) == (
        STATUS_OUT_OF_DATE, "Out of date", "Out of date")
    assert (source.pinned_version, source.version_basis, source.latest_known_version) == (
        "26v1", "release", "26v2")
    assert source.latest_known_seen_at == MANIFEST[PLUTO_FILE]["retrieved_at"]
    assert source.latest_known_query_ref == MANIFEST[PLUTO_FILE]["url"]
    assert source.reason == (
        "PLUTO (64uk-42ks) 26v1 (retrieved 2026-07-16T20:26:46Z) is in use; a newer version, "
        "26v2, is published (seen 2026-09-30T06:10:20Z).")

    assert report.out_of_date is True
    assert report.out_of_date_reason == source.reason
    assert report.fact_exception_labels() == dict.fromkeys(source.fact_ids, "Out of date")
    check = report.c7_data_side()
    assert check.passes is False and check.failures == (f"Out of date: {source.reason}",)


def test_the_out_of_date_output_fits_the_results_contract(f01_facts, benchmark_pluto_facts
                                                         ) -> None:
    report = assess_data_versions(
        pins_from_site_facts(f01_facts.facts),
        published_from_pins(pins_from_site_facts(benchmark_pluto_facts.facts)))
    results = json.loads(RESULTS_FIXTURE.read_text("utf-8"))
    results["out_of_date"] = report.out_of_date
    results["out_of_date_reason"] = report.out_of_date_reason
    validate_results_document(results)  # raises on any contract defect

    schema = json.loads(RESULTS_SCHEMA.read_text("utf-8"))
    labels = schema["$defs"]["exception_label"]["anyOf"][0]["enum"]
    assert OUT_OF_DATE_EXCEPTION_LABEL in labels
    assert set(report.fact_exception_labels().values()) <= set(labels)


def test_the_competitor_reports_pluto_24v4_is_out_of_date(benchmark_pluto_facts) -> None:
    # Competitor review page 88: the report used PLUTO 24v4; the benchmark pack has 26v2.
    competitor = PinnedSource(PLUTO_DATASET_NAME, "24v4", None, None)
    published = published_from_pins(pins_from_site_facts(benchmark_pluto_facts.facts))
    status = assess_source(competitor, published)
    assert status.status == STATUS_OUT_OF_DATE
    assert status.reason == ("PLUTO (64uk-42ks) 24v4 is in use; a newer version, 26v2, is "
                             "published (seen 2026-09-30T06:10:20Z).")


@pytest.mark.parametrize(("pinned", "published", "expected"), [
    # PLUTO releases (research pluto-mappluto section 3.2): majors YYvN, minors YYvN.M.
    ("26v1", "26v1.1", STATUS_OUT_OF_DATE),
    ("26v1.1", "26v2", STATUS_OUT_OF_DATE),
    ("25v4", "26v1", STATUS_OUT_OF_DATE),
    ("26v2", "26v1.1", STATUS_CURRENT),
    ("26v1", "26v1.0", STATUS_CURRENT),
    # Dataset timestamps (for example a layer dataLastEditDate).
    ("2025-12-01T19:39:55Z", "2026-01-05T00:00:00Z", STATUS_OUT_OF_DATE),
    ("2025-12-01T19:39:55Z", "2025-12-01T19:39:55.000Z", STATUS_CURRENT),
    ("2026-04-05T18:46:56Z", "2026-04-05T14:46:56-04:00", STATUS_CURRENT),
])
def test_versions_compare_within_their_kind(pinned, published, expected) -> None:
    # SYNTHETIC version strings.
    assert assess_source(_pin(pinned), [_seen(published)]).status == expected


def test_the_newest_of_several_published_versions_is_used(f09_probe) -> None:
    # SYNTHETIC: 26v1 (F09), 26v2 and 26v1.1 on record -> 26v2 is the latest known.
    status = assess_source(_pin("26v1.1"), [f09_probe, _seen("26v2"), _seen("26v1.1")])
    assert (status.status, status.latest_known_version) == (STATUS_OUT_OF_DATE, "26v2")


def test_behind_means_only_a_newer_version_is_known(f01_facts, f09_probe) -> None:
    # The plan gives no age threshold, so a 26v1 pin with 26v1 as the newest version on record
    # is current. The rule reads no clock.
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), [f09_probe])
    (source,) = report.sources
    assert (source.status, source.label, source.exception_label) == (
        STATUS_CURRENT, "Current", None)
    assert source.reason == ("PLUTO (64uk-42ks) 26v1 (retrieved 2026-07-16T20:26:46Z) is the "
                             "newest published version on record (checked 2026-07-16T20:26:53Z).")
    assert report.out_of_date is False and report.out_of_date_reason is None


# --- unknown version -> never "current" -------------------------------------------------


@pytest.mark.parametrize(("pinned", "published"), [
    (None, [_seen("26v2")]),                              # no pinned version
    ("", [_seen("26v2")]),
    ("latest", [_seen("26v2")]),                          # not a release or a date
    ("retrieved_at:2026-09-30T06:10:20Z", [_seen("2026-09-30T06:10:20Z")]),
    ("2026-09-30T06:10:20", [_seen("2026-09-30T06:10:20Z")]),  # no time zone
    ("26v2", []),                                         # nothing to compare with
    ("26v2", [_seen("26v2", dataset="PLUTO (other)")]),    # another dataset only
    ("26v2", [_seen("2026-09-30T06:10:20Z")]),             # another kind of version
    ("26v2", [_seen("26v2"), _seen(None)]),               # a published version is unreadable
    ("26v2", [_seen("26v2"), _seen("26v3-beta")]),
])
def test_an_unknown_version_is_never_current(pinned, published) -> None:
    # SYNTHETIC version strings.
    status = assess_source(_pin(pinned), published)
    assert status.status == STATUS_VERSION_UNKNOWN
    assert (status.label, status.exception_label) == ("Version unknown", None)
    assert status.reason.endswith("so it cannot be shown as current.")
    report = assess_data_versions([_pin(pinned)], published)
    assert report.c7_data_side().passes is False
    assert report.out_of_date is False


def test_an_unknown_pin_stays_unknown_even_when_a_newer_version_is_known() -> None:
    # SYNTHETIC: without a pinned version there is nothing to call behind or current.
    status = assess_source(_pin(None), [_seen("26v2")])
    assert status.status == STATUS_VERSION_UNKNOWN
    assert status.reason == ("PLUTO (64uk-42ks) has no recorded version, so it cannot be "
                             "shown as current.")


def test_no_pinned_source_does_not_pass_c7() -> None:
    check = assess_data_versions([], []).c7_data_side()
    assert check.passes is False
    assert check.failures == ("No data source is pinned, so no version can be shown.",)


def test_benchmark_dob_filing_source_records_no_version_so_it_is_version_unknown() -> None:
    # B-05 records DOB SODA sources with dataset_version null. Replayed on the benchmark pack,
    # the set-aside NB 440608941 figure's source is therefore "Version unknown", never current.
    def recorded(name: str) -> DobRecordSet:
        entry = MANIFEST[name]
        rows = json.loads((PACK / name).read_bytes().decode("utf-8"))
        return DobRecordSet(entry["dataset_id"], rows, entry["retrieved_at"], entry["url"])

    def recorded_sets(*prefixes: str) -> tuple[DobRecordSet, ...]:
        return tuple(recorded(n) for n in sorted(MANIFEST) if n.startswith(prefixes))

    evidence = ExistingFloorAreaEvidence(
        dob_job_filings=recorded_sets("dob_bis_jobs_"),
        certificates=recorded_sets("dob_bis_co_", "dob_now_co_"))
    result = resolve_existing_zoning_floor_area(BBL, evidence, recorded_building_count=1)
    (entry,) = [e for e in result.considered
                if e["document_ref"] == "DOB BIS job 440608941, document 01"]
    pin = pin_from_site_fact_source(entry["source"])
    status = assess_source(pin, published_from_pins([pin]))
    assert (pin.dataset, pin.version) == ("DOB Job Application Filings (ic3t-wcy2)", None)
    assert status.status == STATUS_VERSION_UNKNOWN


# --- benchmark 215-16 Northern: pinned versions shown -----------------------------------


def test_benchmark_sources_show_their_pinned_versions_and_are_current(
        benchmark_pluto_facts, benchmark_spatial, f09_probe) -> None:
    site, widths = benchmark_spatial
    pluto_pins = pins_from_site_facts(benchmark_pluto_facts.facts)
    mappluto_pin = pin_from_record(site.provenance["lot_outline"], dataset=MAPPLUTO)
    dcm_pins = _dcm_pins(widths)
    pins = (*pluto_pins, mappluto_pin, *dcm_pins)

    # The pinned versions are the ones the recorded bodies carry.
    pluto_row = json.loads((PACK / PLUTO_FILE).read_bytes())[0]
    mappluto_feature = json.loads((PACK / MAPPLUTO_FILE).read_bytes())["features"][0]
    dcm_layer = json.loads((PACK / DCM_LAYER_FILE).read_bytes())
    dcm_edit = datetime.fromtimestamp(dcm_layer["editingInfo"]["dataLastEditDate"] / 1000, UTC)
    assert [pin.version for pin in pluto_pins] == [pluto_row["version"]] == ["26v2"]
    assert mappluto_pin.version == mappluto_feature["attributes"]["Version"] == "26v2"
    assert [pin.version for pin in dcm_pins] == [
        dcm_edit.strftime("%Y-%m-%dT%H:%M:%SZ")] == ["2025-12-01T19:39:55Z"]
    assert sorted(frontage.street_key for frontage in widths.frontages
                  if frontage.sources) == ["215 Place", "Northern Boulevard"]
    for pin in pins:
        assert pin.retrieved_at and pin.query_ref

    # The capture is the newest observation on record; F09's older 26v1 changes nothing.
    report = assess_data_versions(pins, (*published_from_pins(pins), f09_probe))
    shown = {(source.dataset, source.pinned_version, source.status)
             for source in report.sources}
    assert shown == {
        ("PLUTO (64uk-42ks)", "26v2", STATUS_CURRENT),
        (MAPPLUTO, "26v2", STATUS_CURRENT),
        ("https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/"
         "DCM_Street_Center_Line", "2025-12-01T19:39:55Z", STATUS_CURRENT),
    }
    assert report.c7_data_side().passes is True
    assert report.out_of_date is False and report.fact_exception_labels() == {}


def test_the_report_does_not_depend_on_input_order(benchmark_pluto_facts, f01_facts,
                                                   f09_probe) -> None:
    pins = [*pins_from_site_facts(f01_facts.facts), _pin("26v1.1"), _pin(None)]
    published = [*published_from_pins(pins_from_site_facts(benchmark_pluto_facts.facts)),
                 f09_probe, _seen("26v1.1")]
    expected = assess_data_versions(pins, published).to_dict()
    shuffler = random.Random(6)
    for _ in range(5):
        shuffler.shuffle(pins)
        shuffler.shuffle(published)
        assert assess_data_versions(pins, published).to_dict() == expected
    json.dumps(expected, allow_nan=False)
