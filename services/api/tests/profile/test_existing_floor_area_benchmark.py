"""Existing zoning floor area on the recorded 215-16 Northern Blvd pack (queue item B-05;
plan M2-07 "Existing floor area is never taken from DOF building area").

Replays the byte-faithful official responses of queue item B-01
(services/api/tests/fixtures/benchmark_215_16_northern/, MANIFEST.json) with no network:

- DOB BIS job filings (ic3t-wcy2) for BINs 4623241, 4616079 and 4157401;
- DOB NOW and DOB BIS certificates of occupancy (pkdm-hqz6, bs8b-p36w);
- PLUTO 26v2 (bldgarea 54,488 = DOF building area; numbldgs 1).

Recorded facts (fixture README, disagreement 3): NB job 440608941 (BIN 4623241) states
'Proposed Zoning Sqft' 39,934; its certificate 4623241-0000001 was issued 06/03/26. PLUTO
building area is 54,488. The trap is taking 54,488 as zoning floor area.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from app.connectors import pluto_soda
from app.profile.builder import build_property_profile
from app.profile.existing_floor_area import (
    CertificateOfOccupancyStatement,
    DobRecordSet,
    ExistingFloorAreaEvidence,
    StatedAssumption,
    resolve_existing_zoning_floor_area,
)
from app.profile.site_facts import build_site_facts
from app.resilience.transport import TransportResponse
from tests.profile.site_fact_contract import assert_valid_site_fact
from tests.spatial._northern_replay import BBL, MANIFEST, PACK

LOT_1 = "4073340001"
PLUTO_FILE = "pluto_64uk-42ks_bbl_4073340070.json"
NB_FILE = "dob_bis_jobs_ic3t-wcy2_bin_4623241.json"
DOB_ZONING_FLOOR_AREA = 39934
DOF_BUILDING_AREA = 54488
# Other recorded areas that are not zoning floor area: NB 440608941 total construction
# floor area, and the DOB NOW jobs' total construction floor areas.
NOT_ZONING = (DOF_BUILDING_AREA, 45388, 55179, 45308)
CLOCK = datetime(2026, 9, 30, 6, 20, tzinfo=UTC)


def record_set(name: str) -> DobRecordSet:
    entry = MANIFEST[name]
    rows = json.loads((PACK / name).read_bytes().decode("utf-8"))
    return DobRecordSet(entry["dataset_id"], rows, entry["retrieved_at"], entry["url"])


def recorded(prefixes: tuple[str, ...]) -> tuple[DobRecordSet, ...]:
    return tuple(record_set(name) for name in sorted(MANIFEST) if name.startswith(prefixes))


JOB_SETS = recorded(("dob_bis_jobs_",))
CERTIFICATE_SETS = recorded(("dob_bis_co_", "dob_now_co_"))
EVIDENCE = ExistingFloorAreaEvidence(dob_job_filings=JOB_SETS, certificates=CERTIFICATE_SETS)


def profile(bldgarea: str | None = None) -> dict:
    """The recorded PLUTO row through the real connector and builder; with ``bldgarea``,
    a SYNTHETIC variant whose building area is changed (nothing else)."""
    body = (PACK / PLUTO_FILE).read_bytes().decode("utf-8")
    if bldgarea is not None:
        rows = json.loads(body)
        rows[0]["bldgarea"] = bldgarea
        body = json.dumps(rows)
    result = pluto_soda.fetch_by_bbl(
        BBL, transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda _s: None, clock=lambda: CLOCK,
        correlation_id="b05-benchmark", observation_event_id="b05-benchmark")
    return build_property_profile(result, clock=lambda: CLOCK)


def only(facts, key: str) -> dict:
    (fact,) = [fact for fact in facts if fact["key"] == key]
    return fact


def test_benchmark_existing_zoning_floor_area_is_the_dob_filing() -> None:
    result = resolve_existing_zoning_floor_area(BBL, EVIDENCE, recorded_building_count=1)
    fact = result.fact
    assert_valid_site_fact(fact)
    assert (fact["value"], fact["unit"]) == (DOB_ZONING_FLOOR_AREA, "square_feet")
    assert fact["value"] not in NOT_ZONING
    assert (result.basis, result.basis_label) == ("dob_job_filing", "DOB job filing")
    assert fact["measurement"] == {"rank": "city_records", "label": "City records"}
    assert fact["source"] == {
        "kind": "city_filing",
        "dataset": "DOB Job Application Filings (ic3t-wcy2)",
        "dataset_version": None,
        "retrieved_at": MANIFEST[NB_FILE]["retrieved_at"],
        "query_ref": MANIFEST[NB_FILE]["url"],
        "document_ref": "DOB BIS job 440608941, document 01",
        "statement": None,
    }
    note = fact["note"]
    assert "certificate of occupancy 4623241-0000001 issued 06/03/26" in note
    assert "job type NB, building 4623241" in note
    # BIN 4616079's A1 row names lot 1 in its lot column and lot 70 in its BBL column.
    (entry,) = result.considered
    assert entry["document_ref"] == "DOB BIS job 421240534, document 01"
    assert "name different lots (4073340001, 4073340070)" in entry["reason"]


def test_benchmark_site_facts_use_the_filing_and_show_dof_area_only_as_reference() -> None:
    site = build_site_facts(profile(), existing_floor_area=EVIDENCE)
    existing = only(site.facts, "existing_zoning_floor_area")
    assert_valid_site_fact(existing)
    assert existing["value"] == DOB_ZONING_FLOOR_AREA
    assert site.existing_floor_area.basis == "dob_job_filing"
    # PLUTO NumBldgs (1) was available, so the building-count check ran.
    assert "not available to check" not in existing["note"]

    (reference,) = [ref for ref in site.references if ref["key"] == "recorded_building_area"]
    assert (reference["value"], reference["unit"], reference["use"]) == (
        DOF_BUILDING_AREA, "square_feet", "reference_only")
    assert reference["source"]["dataset"] == "PLUTO (64uk-42ks)"
    # 54,488 appears nowhere in the site facts: only in the reference field.
    facts_text = json.dumps(site.facts)
    assert "54488" not in facts_text and "54,488" not in facts_text
    assert all(fact["value"] != DOF_BUILDING_AREA for fact in site.facts)


def test_benchmark_without_dob_evidence_is_unknown_although_dof_area_is_recorded() -> None:
    site = build_site_facts(profile())
    existing = only(site.facts, "existing_zoning_floor_area")
    assert_valid_site_fact(existing)
    assert (existing["value"], existing["measurement"]["rank"]) == (None, "unknown")
    assert existing["blocks"] == ["remaining_floor_area", "existing_building_paths"]
    assert site.existing_floor_area.reason == (
        "No DOB job-filing rows were supplied. No certificate of occupancy figure or "
        "stated assumption was entered.")
    assert DOF_BUILDING_AREA in [ref["value"] for ref in site.references]


@pytest.mark.parametrize("bldgarea", ["1", "39934", "54488", "999999"])
def test_benchmark_fact_does_not_depend_on_dof_building_area(bldgarea: str) -> None:
    baseline = only(build_site_facts(profile(), existing_floor_area=EVIDENCE).facts,
                    "existing_zoning_floor_area")
    varied = build_site_facts(profile(bldgarea), existing_floor_area=EVIDENCE)
    assert only(varied.facts, "existing_zoning_floor_area") == baseline
    unknown = build_site_facts(profile(bldgarea))
    assert only(unknown.facts, "existing_zoning_floor_area")["value"] is None


def test_benchmark_tax_lot_is_not_taken_as_the_zoning_lot() -> None:
    # DOB job 421803891 (lot 1) says the zoning lot is tax lots 1 and 70. Lot 70's figure
    # is never given to lot 1, and lot 1's filings never feed lot 70.
    lot_1 = resolve_existing_zoning_floor_area(LOT_1, EVIDENCE)
    assert_valid_site_fact(lot_1.fact)
    assert (lot_1.fact["lot_bbl"], lot_1.fact["value"], lot_1.basis) == (LOT_1, None,
                                                                          "unknown")
    assert "building 4157401" in lot_1.reason
    lot_1_figures = {entry["value"] for entry in lot_1.considered}
    assert {14150, 39772} <= lot_1_figures and DOB_ZONING_FLOOR_AREA not in lot_1_figures

    only_lot_1_rows = ExistingFloorAreaEvidence(
        dob_job_filings=(record_set("dob_bis_jobs_ic3t-wcy2_bin_4157401.json"),))
    lot_70 = resolve_existing_zoning_floor_area(BBL, only_lot_1_rows)
    assert lot_70.fact["value"] is None
    assert "No DOB job filing in the supplied rows is for tax lot 4073340070" in lot_70.reason

    result = resolve_existing_zoning_floor_area(BBL, EVIDENCE)
    assert result.scope == "tax_lot"
    assert ("covers tax lot 4073340070 only: the zoning lot may include other tax lots"
            in result.fact["note"])


def test_benchmark_dob_now_job_filings_and_pluto_are_refused_as_sources() -> None:
    for name in ("dob_now_jobs_w9ak-ipjd_bbl_4073340070.json", PLUTO_FILE):
        with pytest.raises(ValueError, match="refused"):
            record_set(name)


def test_benchmark_certificate_rows_alone_give_no_figure() -> None:
    # The recorded certificate rows carry no floor-area column.
    (row,) = record_set("dob_now_co_pkdm-hqz6_bbl_4073340070.json").rows
    assert not [key for key in row if "area" in key or "sq" in key]
    result = resolve_existing_zoning_floor_area(
        BBL, ExistingFloorAreaEvidence(certificates=CERTIFICATE_SETS))
    assert (result.basis, result.fact["value"]) == ("unknown", None)


def test_benchmark_precedence_with_a_certificate_figure_and_an_assumption() -> None:
    at = "2026-09-30T12:00:00Z"
    statement = CertificateOfOccupancyStatement(39934, "4623241-0000001", at)
    assumption = StatedAssumption(41000, "SYNTHETIC test assumption.", at)
    evidence = ExistingFloorAreaEvidence(JOB_SETS, CERTIFICATE_SETS, statement, assumption)
    result = resolve_existing_zoning_floor_area(BBL, evidence, recorded_building_count=1)
    assert_valid_site_fact(result.fact)
    assert (result.basis, result.fact["value"]) == ("certificate_of_occupancy", 39934)
    reasons = {entry["basis"]: entry["reason"] for entry in result.considered}
    assert reasons["dob_job_filing"] == (
        "Not used: Certificate of occupancy comes first and gives the same value.")
    assert reasons["stated_assumption"] == (
        "Not used: Certificate of occupancy comes first and gives a different value.")

    without_certificate = ExistingFloorAreaEvidence(JOB_SETS, CERTIFICATE_SETS,
                                                    assumption=assumption)
    result = resolve_existing_zoning_floor_area(BBL, without_certificate)
    assert (result.basis, result.fact["value"]) == ("dob_job_filing", DOB_ZONING_FLOOR_AREA)
    assert "Stated assumption gives 41,000 sq ft (not used)." in result.fact["note"]
