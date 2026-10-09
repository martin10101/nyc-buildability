"""§8a existing-building hidden-issue flags (queue item B-09, first slice; plan L-11).

Offline and deterministic. The flag logic is exercised on a SYNTHETIC existing-floor-area
result (built through the B-05 resolver from a stated assumption / certificate statement for
a synthetic lot), and the recorded 215-16 Northern Blvd benchmark pack is replayed with no
network for the real "Unknown -> Check needed" case.
"""

from __future__ import annotations

import json

import pytest

from app.profile.data_versions import (
    PinnedSource,
    PublishedVersion,
    assess_data_versions,
)
from app.profile.existing_floor_area import (
    CertificateOfOccupancyStatement,
    DobRecordSet,
    ExistingFloorAreaEvidence,
    StatedAssumption,
    resolve_existing_zoning_floor_area,
)
from app.profile.hidden_issue_flags import (
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    STATUS_NOT_FLAGGED,
    AsOfRightAllowance,
    FlagGroup,
    HiddenIssueFlag,
    existing_building_group,
)
from tests.spatial._northern_replay import BBL as BENCHMARK_BBL
from tests.spatial._northern_replay import MANIFEST, PACK

BBL = "1000010100"  # synthetic: Manhattan block 1, lot 100
AT = "2026-09-30T12:00:00Z"
# Plan section 5b, the flag wording the module must use verbatim (plan line 261).
LARGER_VERBATIM = ("The existing building is larger than today's zoning allows; demolition "
                   "would reduce floor area.")
ALLOWANCE_SOURCE = {"kind": "rule_evaluation", "statement": "R6B as-of-right, rule v1"}

EXPECTED_ITEMS = (
    "existing_building.larger_than_today",
    "existing_building.non_conforming_use",
    "existing_building.legal_use_and_occupancy",
    "existing_building.rent_regulated_apartments",
    "existing_building.harassment_certification",
)


def known_efa(value: int = 50000):
    """A known existing floor area, via a stated assumption (B-05 resolver)."""
    evidence = ExistingFloorAreaEvidence(
        assumption=StatedAssumption(value, "architect's stated assumption", AT))
    return resolve_existing_zoning_floor_area(BBL, evidence)


def certificate_efa(value: int = 50000):
    evidence = ExistingFloorAreaEvidence(
        co_statement=CertificateOfOccupancyStatement(value, "4623241-0000001", AT))
    return resolve_existing_zoning_floor_area(BBL, evidence)


def unknown_efa():
    """No evidence supplied -> B-05 resolves to Unknown — enter."""
    return resolve_existing_zoning_floor_area(BBL, ExistingFloorAreaEvidence())


def item(group: FlagGroup, item_id: str) -> HiddenIssueFlag:
    (flag,) = [f for f in group.flags if f.item_id == item_id]
    return flag


# --- group shape -------------------------------------------------------------------------

def test_group_has_the_five_section_8a_existing_building_items_in_order():
    group = existing_building_group(BBL)
    assert group.group_id == "existing_building"
    assert group.lot_bbl == BBL
    assert tuple(f.item_id for f in group.flags) == EXPECTED_ITEMS
    assert all(f.phase == "1" for f in group.flags)


def test_group_and_flag_round_trip_to_dict():
    group = existing_building_group(BBL, existing_floor_area=known_efa(),
                                    as_of_right_allowance=AsOfRightAllowance(1, ALLOWANCE_SOURCE))
    payload = group.to_dict()
    assert payload["group_id"] == "existing_building"
    assert [f["item_id"] for f in payload["flags"]] == list(EXPECTED_ITEMS)
    larger = payload["flags"][0]
    assert larger["status"] == STATUS_FLAG
    assert larger["status_label"] == "Flag"
    assert larger["evidence"][0]["label"].startswith("Existing zoning floor area")


def test_bad_bbl_and_wrong_input_types_raise():
    with pytest.raises(ValueError, match="10-digit BBL"):
        existing_building_group("123")
    with pytest.raises(ValueError, match="ExistingFloorAreaResult"):
        existing_building_group(BBL, existing_floor_area=object())
    with pytest.raises(ValueError, match="AsOfRightAllowance"):
        existing_building_group(BBL, as_of_right_allowance=50000)
    with pytest.raises(ValueError, match="DataVersionReport"):
        existing_building_group(BBL, data_versions=object())


# --- item 1: larger than today's rules ---------------------------------------------------

def test_larger_check_needed_when_no_floor_area_result_supplied():
    flag = item(existing_building_group(BBL), "existing_building.larger_than_today")
    assert flag.status == STATUS_CHECK_NEEDED
    assert "DOF/PLUTO building area" in flag.detail
    assert flag.exception_label is None


def test_larger_check_needed_when_floor_area_unknown_carries_the_b05_reason():
    efa = unknown_efa()
    flag = item(existing_building_group(BBL, existing_floor_area=efa),
                "existing_building.larger_than_today")
    assert flag.status == STATUS_CHECK_NEEDED
    # The B-05 reason (why it is unknown) is carried through, not re-invented.
    assert efa.reason is not None and efa.reason in flag.detail
    assert flag.fact_refs == (efa.fact["fact_id"],)


def test_larger_check_needed_when_known_but_no_allowance_supplied():
    flag = item(existing_building_group(BBL, existing_floor_area=known_efa(50000)),
                "existing_building.larger_than_today")
    assert flag.status == STATUS_CHECK_NEEDED
    assert "50,000 sq ft" in flag.detail
    assert "allowance is the engine's" in flag.detail
    assert flag.exception_label is None


def test_larger_flags_when_existing_exceeds_the_as_of_right_allowance():
    group = existing_building_group(
        BBL, existing_floor_area=known_efa(50000),
        as_of_right_allowance=AsOfRightAllowance(40000, ALLOWANCE_SOURCE))
    flag = item(group, "existing_building.larger_than_today")
    assert flag.status == STATUS_FLAG
    assert LARGER_VERBATIM in flag.detail
    assert "50,000 sq ft" in flag.detail and "40,000 sq ft" in flag.detail
    labels = [e["label"] for e in flag.evidence]
    assert "Today's as-of-right allowance" in labels
    assert flag.evidence[-1]["source"] == ALLOWANCE_SOURCE


def test_not_flagged_when_existing_within_allowance_including_equal():
    for allowed in (60000, 50000):
        flag = item(
            existing_building_group(
                BBL, existing_floor_area=known_efa(50000),
                as_of_right_allowance=AsOfRightAllowance(allowed, ALLOWANCE_SOURCE)),
            "existing_building.larger_than_today")
        assert flag.status == STATUS_NOT_FLAGGED
        assert LARGER_VERBATIM not in flag.detail
        assert "within today's as-of-right allowance" in flag.detail


def test_larger_flag_carries_out_of_date_from_b06_data_versions():
    efa = known_efa(50000)
    fact_id = efa.fact["fact_id"]
    pin = PinnedSource(dataset="DOB Job Application Filings (ic3t-wcy2)", version="26v1",
                       retrieved_at=None, query_ref=None, fact_ids=(fact_id,))
    report = assess_data_versions(
        [pin], [PublishedVersion(pin.dataset, "26v2", None, None)])
    assert report.out_of_date and report.fact_exception_labels()[fact_id] == "Out of date"
    flag = item(
        existing_building_group(
            BBL, existing_floor_area=efa,
            as_of_right_allowance=AsOfRightAllowance(40000, ALLOWANCE_SOURCE),
            data_versions=report),
        "existing_building.larger_than_today")
    assert flag.status == STATUS_FLAG
    assert flag.exception_label == "Out of date"


def test_larger_no_exception_when_source_current():
    efa = known_efa(50000)
    fact_id = efa.fact["fact_id"]
    pin = PinnedSource(dataset="d", version="26v2", retrieved_at=None, query_ref=None,
                       fact_ids=(fact_id,))
    report = assess_data_versions([pin], [PublishedVersion("d", "26v2", None, None)])
    flag = item(
        existing_building_group(
            BBL, existing_floor_area=efa,
            as_of_right_allowance=AsOfRightAllowance(40000, ALLOWANCE_SOURCE),
            data_versions=report),
        "existing_building.larger_than_today")
    assert flag.exception_label is None


# --- items 2, 4, 5: no Lane B source yet -> always Check needed, never a guess ------------

@pytest.mark.parametrize("item_id, phrase, typical", [
    ("existing_building.non_conforming_use", "never guessed", "zoning use rules (engine)"),
    ("existing_building.rent_regulated_apartments", "never guessed", "DHCR and HPD data"),
    ("existing_building.harassment_certification", "Certification of No Harassment",
     "HPD Certification of No Harassment"),
])
def test_unsourced_items_are_check_needed_with_an_honest_reason(item_id, phrase, typical):
    flag = item(existing_building_group(BBL, existing_floor_area=known_efa()), item_id)
    assert flag.status == STATUS_CHECK_NEEDED
    assert phrase in flag.detail
    assert typical in flag.typical_source
    assert not flag.evidence and not flag.fact_refs


# --- item 3: legal use and occupancy on the CO -------------------------------------------

def test_legal_use_check_needed_and_plain_when_no_certificate_referenced():
    flag = item(existing_building_group(BBL, existing_floor_area=known_efa()),
                "existing_building.legal_use_and_occupancy")
    assert flag.status == STATUS_CHECK_NEEDED
    assert "read from the certificate" in flag.detail
    assert "already referenced" not in flag.detail


def test_legal_use_references_a_certificate_the_floor_area_already_used():
    efa = certificate_efa(50000)
    flag = item(existing_building_group(BBL, existing_floor_area=efa),
                "existing_building.legal_use_and_occupancy")
    assert flag.status == STATUS_CHECK_NEEDED
    assert "already referenced" in flag.detail
    assert "4623241-0000001" in flag.detail


# --- allowance value object --------------------------------------------------------------

def test_allowance_rejects_negatives_and_empty_source_but_accepts_zero():
    assert AsOfRightAllowance(0, ALLOWANCE_SOURCE).value_sq_ft == 0
    with pytest.raises(ValueError, match="non-negative"):
        AsOfRightAllowance(-1, ALLOWANCE_SOURCE)
    with pytest.raises(ValueError, match="provenance mapping"):
        AsOfRightAllowance(1000, {})


def test_flag_rejects_an_unknown_status():
    with pytest.raises(ValueError, match="unknown flag status"):
        HiddenIssueFlag("x.y", "x", "Y", "maybe", "d", "s")


# --- recorded benchmark: 215-16 Northern Blvd lot 70 (no network) ------------------------

def _record_set(name: str) -> DobRecordSet:
    entry = MANIFEST[name]
    rows = json.loads((PACK / name).read_bytes().decode("utf-8"))
    return DobRecordSet(entry["dataset_id"], rows, entry["retrieved_at"], entry["url"])


def _recorded(prefixes: tuple[str, ...]) -> tuple[DobRecordSet, ...]:
    return tuple(_record_set(n) for n in sorted(MANIFEST) if n.startswith(prefixes))


def test_benchmark_lot_is_unknown_so_larger_than_today_is_check_needed():
    evidence = ExistingFloorAreaEvidence(
        dob_job_filings=_recorded(("dob_bis_jobs_",)),
        certificates=_recorded(("dob_bis_co_", "dob_now_co_")))
    efa = resolve_existing_zoning_floor_area(BENCHMARK_BBL, evidence)
    # B-05: lot 70 is "Unknown — enter" (39,934 set aside; zoning-lot mention cited).
    assert efa.fact["value"] is None
    flag = item(
        existing_building_group(BENCHMARK_BBL, existing_floor_area=efa,
                                as_of_right_allowance=AsOfRightAllowance(40000, ALLOWANCE_SOURCE)),
        "existing_building.larger_than_today")
    assert flag.status == STATUS_CHECK_NEEDED
    # The DOF building area (54,488) is never used as a floor area here.
    assert "54,488" not in flag.detail
