"""Neighbours' existing-floor-area capture (queue item B-11 slice 2; plan section 11b).

Lane B captures each neighbour's existing zoning floor area through the B-05 source order
(certificate of occupancy > DOB filing > stated assumption; never DOF/PLUTO building area)
and wires the captured input into the slice-1 unused-floor-area carriage. The parity output
stays the owner-settled "Not confirmed" wording (D-090-R038): never a number, never a
subtraction. Recorded replay only; the one live capture is the pack, recorded once.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from app.profile.existing_floor_area import (
    CertificateOfOccupancyStatement,
    DobRecordSet,
    ExistingFloorAreaEvidence,
    StatedAssumption,
)
from app.profile.parity.neighbor_floor_area import (
    CAPTURE_CAPTURED,
    CAPTURE_NOT_RECORDED,
    NEIGHBOR_SET_METHOD,
    NeighborEvidence,
    NeighborFloorAreaCapture,
    capture_neighbor_floor_area,
    capture_neighbors,
    neighbor_parity_data,
)
from app.profile.parity.unused_floor_area import (
    NOT_CONFIRMED_LABEL,
    NOT_CONFIRMED_REASON,
    ROLE_NEIGHBOR,
    STATUS_NOT_CONFIRMED,
    UnusedFloorAreaData,
)

PACK = (Path(__file__).resolve().parents[1]
        / "fixtures" / "benchmark_block_7334_neighbor_lot_1")
MANIFEST = {entry["file"]: entry
            for entry in json.loads((PACK / "MANIFEST.json").read_text("utf-8"))["files"]}
NEIGHBOR_BBL = "4073340001"           # lot 1, the recorded touching neighbour of lot 70
LOT_1_BLDGAREA, LOT_70_BLDGAREA = "8409", "54488"   # DOF building area: never read
AT = "2026-10-03T12:00:00Z"
_DIGIT = re.compile(r"[0-9]")


def record_set(name: str) -> DobRecordSet:
    entry = MANIFEST[name]
    rows = json.loads((PACK / name).read_bytes().decode("utf-8"))
    return DobRecordSet(entry["dataset_id"], rows, entry["retrieved_at"], entry["url"])


def benchmark_evidence() -> ExistingFloorAreaEvidence:
    return ExistingFloorAreaEvidence(
        dob_job_filings=(record_set("dob_bis_jobs_ic3t-wcy2_bin_4157401.json"),),
        certificates=(record_set("dob_bis_co_bs8b-p36w_bbl_4073340001.json"),
                      record_set("dob_now_co_pkdm-hqz6_bbl_4073340001.json")))


def signed_off_nb_filing(bbl: str, value: int) -> DobRecordSet:
    """A labelled-SYNTHETIC recorded DOB row: one signed-off new building giving ``value``
    sq ft for ``bbl`` (no zoning-lot text), with a real-shaped query provenance."""
    row = {
        "job__": "999000001", "doc__": "01", "bin__": "9990001",
        "borough": "QUEENS", "block": "07334", "lot": bbl[-4:], "bbl": bbl,
        "job_type": "NB", "job_status_descrp": "SIGNED OFF", "signoff_date": "01/01/2024",
        "existing_zoning_sqft": "0", "proposed_zoning_sqft": str(value),
        "job_description": "New building (synthetic test row) on this tax lot only.",
    }
    return DobRecordSet(
        "ic3t-wcy2", (row,), AT,
        "test-fixture-synthetic:https://data.cityofnewyork.us/resource/ic3t-wcy2.json"
        "?bin__=9990001")


# ---------------------------------------------------------------- neighbour-set method


def test_neighbor_set_method_is_documented_and_carried() -> None:
    for token in ("tax block", "shares a lot line", "touching", "4073340001", "99.98"):
        assert token in NEIGHBOR_SET_METHOD, token
    captured = capture_neighbors([])
    assert captured.method == NEIGHBOR_SET_METHOD
    assert captured.captures == ()
    # The set method is overridable but defaults to the documented one.
    assert capture_neighbors([], method="other").method == "other"


# --------------------------------------------------------- the B-05 source order per neighbour


def test_captured_via_certificate_outranks_assumption_with_provenance() -> None:
    evidence = ExistingFloorAreaEvidence(
        co_statement=CertificateOfOccupancyStatement(18_500, "CO-TEST-1", AT),
        assumption=StatedAssumption(20_000, "architect estimate (synthetic).", AT))
    capture = capture_neighbor_floor_area(NeighborEvidence("4073340002", evidence))
    assert (capture.status, capture.basis) == (CAPTURE_CAPTURED, "certificate_of_occupancy")
    assert (capture.value_sq_ft, capture.unit) == (18_500, "square_feet")
    # Provenance is present on the recorded figure.
    assert capture.source is not None
    assert capture.source["kind"] == "city_filing"
    assert capture.source["document_ref"] == "Certificate of occupancy CO-TEST-1"


def test_captured_via_stated_assumption_with_provenance() -> None:
    evidence = ExistingFloorAreaEvidence(
        assumption=StatedAssumption(12_345, "architect stated assumption (synthetic).", AT))
    capture = capture_neighbor_floor_area(NeighborEvidence("4073340002", evidence))
    assert (capture.status, capture.basis, capture.value_sq_ft) == (
        CAPTURE_CAPTURED, "stated_assumption", 12_345)
    assert capture.source is not None and capture.source["kind"] == "assumption"


def test_captured_via_dob_filing_carries_full_provenance() -> None:
    evidence = ExistingFloorAreaEvidence(
        dob_job_filings=(signed_off_nb_filing("4073340002", 11_000),))
    capture = capture_neighbor_floor_area(NeighborEvidence("4073340002", evidence))
    assert (capture.status, capture.basis, capture.value_sq_ft) == (
        CAPTURE_CAPTURED, "dob_job_filing", 11_000)
    source = capture.source
    assert source is not None
    assert source["dataset"] == "DOB Job Application Filings (ic3t-wcy2)"
    assert source["query_ref"].endswith("bin__=9990001")
    assert source["retrieved_at"] == AT


def test_not_recorded_when_sources_are_silent() -> None:
    capture = capture_neighbor_floor_area(
        NeighborEvidence("4073340002", ExistingFloorAreaEvidence()))
    assert (capture.status, capture.value_sq_ft, capture.basis) == (
        CAPTURE_NOT_RECORDED, None, "unknown")
    assert capture.source is None
    assert "Needs existing zoning floor area" in (capture.note or "")


# ---------------------------------------------------- recorded benchmark neighbour (lot 1)


def test_benchmark_neighbor_lot_1_is_not_recorded_from_the_recorded_pack() -> None:
    capture = capture_neighbor_floor_area(
        NeighborEvidence(NEIGHBOR_BBL, benchmark_evidence(), recorded_building_count=1))
    assert capture.bbl == NEIGHBOR_BBL
    assert (capture.status, capture.value_sq_ft, capture.basis) == (
        CAPTURE_NOT_RECORDED, None, "unknown")
    # Both DOB figures are set aside with their reasons; the zoning-lot filing is cited.
    set_aside = sorted(c["value"] for c in capture.considered if c["value"])
    assert set_aside == [14150, 39772]
    assert [m["document_ref"] for m in capture.zoning_lot_mentions] == [
        "DOB BIS job 421803891, document 01"]
    assert "building 4157401" in (capture.result.reason or "")


def test_benchmark_neighbor_never_reads_dof_building_area() -> None:
    capture = capture_neighbor_floor_area(
        NeighborEvidence(NEIGHBOR_BBL, benchmark_evidence(), recorded_building_count=1))
    text = json.dumps(capture.to_dict())
    for number in (LOT_1_BLDGAREA, LOT_70_BLDGAREA, "8,409", "54,488"):
        assert number not in text, number


def test_pluto_building_area_has_no_path_into_neighbour_evidence() -> None:
    # The evidence type refuses PLUTO (64uk-42ks), so DOF building area cannot be supplied.
    with pytest.raises(ValueError, match="refused"):
        DobRecordSet("64uk-42ks", ({"bbl": NEIGHBOR_BBL},), AT,
                     "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=4073340001")


# ------------------------------------------- wiring into the slice-1 unused-floor-area carriage


def test_wiring_keeps_the_settled_wording_and_no_capacity_number() -> None:
    captures = capture_neighbors([
        NeighborEvidence(NEIGHBOR_BBL, benchmark_evidence()),                 # not recorded
        NeighborEvidence("4073340002", ExistingFloorAreaEvidence(
            assumption=StatedAssumption(9_000, "synthetic assumption.", AT))),  # captured
    ])
    parity = neighbor_parity_data(captures)
    assert len(parity) == 2
    assert all(isinstance(entry, UnusedFloorAreaData) for entry in parity)
    assert [entry.lot_bbl for entry in parity] == [NEIGHBOR_BBL, "4073340002"]
    for entry in parity:
        assert entry.role == ROLE_NEIGHBOR
        assert entry.status == STATUS_NOT_CONFIRMED
        assert entry.label == NOT_CONFIRMED_LABEL
        assert entry.reason == NOT_CONFIRMED_REASON
        # The capacity output itself never carries a digit (no number, no subtraction).
        assert not _DIGIT.search(entry.label)
        assert not _DIGIT.search(entry.reason)
        assert not hasattr(entry, "value")
        assert not hasattr(entry, "unused_floor_area_sq_ft")
        assert not hasattr(entry, "remaining_floor_area")
    # The captured neighbour carries its sourced input; the not-recorded one says so.
    first, second = parity
    assert first.existing_floor_area_input["known"] is False
    assert second.existing_floor_area_input["known"] is True
    assert second.existing_floor_area_input["value_sq_ft"] == 9_000
    # The not-recorded neighbour's whole line (including the disclosure) carries no digit.
    assert not _DIGIT.search(first.detail)


def test_empty_neighbor_set_produces_no_parity_rows() -> None:
    assert neighbor_parity_data(capture_neighbors([])) == ()


# ---------------------------------------------------------------- input validation + shape


def test_neighbor_evidence_validates_its_inputs() -> None:
    with pytest.raises(ValueError, match="10-digit BBL"):
        NeighborEvidence("40733400", ExistingFloorAreaEvidence())
    with pytest.raises(ValueError, match="ExistingFloorAreaEvidence"):
        NeighborEvidence(NEIGHBOR_BBL, {"not": "evidence"})  # type: ignore[arg-type]


def test_capture_to_dict_shape_carries_figure_source_and_status() -> None:
    capture = capture_neighbor_floor_area(
        NeighborEvidence("4073340002", ExistingFloorAreaEvidence(
            assumption=StatedAssumption(7_777, "synthetic.", AT))))
    assert isinstance(capture, NeighborFloorAreaCapture)
    document = capture.to_dict()
    assert document["role"] == ROLE_NEIGHBOR
    assert document["status"] == CAPTURE_CAPTURED
    assert document["value_sq_ft"] == 7_777
    assert document["basis"] == "stated_assumption"
    assert document["source"]["kind"] == "assumption"
    # The full B-05 result is the carriage input, not a serialised value.
    assert "result" not in document
