"""Existing zoning floor area: sources, precedence, labels and unknowns (queue item B-05;
plan M2-07 "Existing floor area is never taken from DOF building area", section 3 step 4).

Offline and deterministic. Every row here is SYNTHETIC (built in the test on the shape of
the recorded ic3t-wcy2 / pkdm-hqz6 rows) for a synthetic lot, and every source is named
``test-fixture-synthetic``. The recorded benchmark pack is exercised in
``test_existing_floor_area_benchmark.py``.
"""

from __future__ import annotations

import dataclasses
import inspect
import re

import pytest

from app.profile import site_facts
from app.profile.existing_floor_area import (
    BASIS_LABELS,
    BLOCKED_OUTPUTS,
    PRECEDENCE,
    CertificateOfOccupancyStatement,
    DobRecordSet,
    ExistingFloorAreaEvidence,
    StatedAssumption,
    read_dob_filings,
    resolve_existing_zoning_floor_area,
)
from app.profile.existing_floor_area import resolve as resolve_module
from tests.profile.site_fact_contract import assert_valid_site_fact

BBL = "1000010100"  # synthetic: Manhattan block 1, lot 100
AT = "2026-09-30T12:00:00Z"
QUERY = "test-fixture-synthetic://ic3t-wcy2?bbl=1000010100"


def job(job_number: str = "100000001", **overrides) -> dict:
    """A SYNTHETIC ic3t-wcy2 row: a signed-off new building of 12,000 zoning sq ft."""
    row = {
        "job__": job_number, "doc__": "01", "borough": "MANHATTAN", "block": "00001",
        "lot": "00100", "bin__": "1000001", "bbl": BBL, "job_type": "NB",
        "job_status": "X", "job_status_descrp": "SIGNED OFF", "signoff_date": "01/15/2020",
        "existing_zoning_sqft": "0", "proposed_zoning_sqft": "12000",
        "total_construction_floor_area": "15000",
    }
    row.update(overrides)
    return {key: value for key, value in row.items() if value is not None}


def jobs(*rows: dict) -> DobRecordSet:
    return DobRecordSet("ic3t-wcy2", rows, AT, QUERY)


def certificates(*rows: dict) -> DobRecordSet:
    return DobRecordSet("pkdm-hqz6", rows, AT, "test-fixture-synthetic://pkdm-hqz6")


def issued_co(job_number: str = "100000001", **overrides) -> dict:
    row = {"job_filing_name": job_number, "bin": "1000001", "bbl": BBL,
           "c_of_o_status": "CO Issued", "c_of_o_number": "1000001-0000001",
           "c_of_o_issuance_date": "03/01/21  9:00:00 AM", "c_of_o_filing_type": "Final"}
    row.update(overrides)
    return row


CO_STATEMENT = CertificateOfOccupancyStatement(12500, "1000001-0000001", AT)
ASSUMPTION = StatedAssumption(13000, "Architect's take-off from the 2019 plans.", AT)


def resolve(*job_rows: dict, certificate_rows=(), co=None, assumption=None, count=None):
    evidence = ExistingFloorAreaEvidence(
        dob_job_filings=(jobs(*job_rows),) if job_rows else (),
        certificates=(certificates(*certificate_rows),) if certificate_rows else (),
        co_statement=co,
        assumption=assumption,
    )
    result = resolve_existing_zoning_floor_area(BBL, evidence, recorded_building_count=count)
    assert_valid_site_fact(result.fact)
    assert result.fact["lot_bbl"] == BBL
    assert (result.scope, result.zoning_lot_scope) == ("tax_lot_as_stated", "not_established")
    return result


def assert_unknown(result, *reason_parts: str) -> None:
    fact = result.fact
    assert (fact["value"], fact["unit"], fact["source"]) == (None, None, None)
    assert fact["measurement"] == {"rank": "unknown", "label": "Unknown — enter"}
    assert fact["blocks"] == ["remaining_floor_area", "existing_building_paths"]
    assert (result.basis, result.basis_label) == ("unknown", "Unknown — enter")
    assert result.basis_label == fact["measurement"]["label"]
    assert result.reason
    for part in reason_parts:
        assert part in result.reason, (part, result.reason)
        assert part in fact["note"]


# ---------------------------------------------------------------------------
# Precedence and source labels
# ---------------------------------------------------------------------------


def test_dob_filing_for_completed_work_is_city_records_from_a_city_filing() -> None:
    result = resolve(job())
    fact = result.fact
    assert (fact["value"], fact["unit"]) == (12000, "square_feet")
    assert fact["measurement"] == {"rank": "city_records", "label": "City records"}
    assert (result.basis, result.basis_label, result.reason) == (
        "dob_job_filing", "DOB job filing", None)
    assert fact["source"] == {
        "kind": "city_filing", "dataset": "DOB Job Application Filings (ic3t-wcy2)",
        "dataset_version": None, "retrieved_at": AT, "query_ref": QUERY,
        "document_ref": "DOB BIS job 100000001, document 01", "statement": None,
    }
    assert fact["blocks"] == [] and fact["editable"] is True
    assert "signed off 01/15/2020" in fact["note"]
    assert ("Scope: stated for tax lot 1000010100; whether the figure covers only this tax "
            "lot or a zoning lot of several tax lots is not established.") in fact["note"]
    assert "only" not in fact["note"].split("Scope:")[1].split(";")[0]
    assert result.completion == {
        "kind": "dob_sign_off", "dataset": "DOB Job Application Filings (ic3t-wcy2)",
        "query_ref": QUERY, "retrieved_at": AT,
        "document_ref": "DOB BIS job 100000001, document 01", "job": "100000001",
        "signed_off": "01/15/2020"}
    # The job's total construction floor area (15,000) is never the value.
    assert "15,000" not in fact["note"]


def test_certificate_statement_is_city_records_with_the_certificate_as_document() -> None:
    result = resolve(co=CO_STATEMENT)
    fact = result.fact
    assert (result.basis, result.basis_label) == ("certificate_of_occupancy",
                                                  "Certificate of occupancy")
    assert fact["value"] == 12500
    assert fact["measurement"] == {"rank": "city_records", "label": "City records"}
    assert fact["source"]["kind"] == "city_filing"
    assert fact["source"]["dataset"] == "DOB certificate of occupancy (document)"
    assert fact["source"]["document_ref"] == "Certificate of occupancy 1000001-0000001"
    assert "transcribed from the document" in fact["note"]


def test_stated_assumption_is_labeled_assumed_with_its_statement() -> None:
    result = resolve(assumption=ASSUMPTION)
    fact = result.fact
    assert (result.basis, result.basis_label) == ("stated_assumption", "Stated assumption")
    assert fact["value"] == 13000
    assert fact["measurement"] == {"rank": "assumed", "label": "Assumed"}
    assert fact["source"]["kind"] == "assumption"
    assert fact["source"]["statement"] == "Architect's take-off from the 2019 plans."
    assert "No DOB job-filing rows" not in fact["note"]


@pytest.mark.parametrize(
    ("with_co", "with_job", "with_assumption", "basis", "value"),
    [
        (True, True, True, "certificate_of_occupancy", 12500),
        (True, False, True, "certificate_of_occupancy", 12500),
        (False, True, True, "dob_job_filing", 12000),
        (False, False, True, "stated_assumption", 13000),
        (False, False, False, "unknown", None),
    ],
)
def test_precedence_certificate_then_filing_then_assumption_then_unknown(
    with_co, with_job, with_assumption, basis, value
) -> None:
    result = resolve(
        *((job(),) if with_job else ()),
        co=CO_STATEMENT if with_co else None,
        assumption=ASSUMPTION if with_assumption else None,
    )
    assert (result.basis, result.fact["value"]) == (basis, value)
    assert PRECEDENCE == ("certificate_of_occupancy", "dob_job_filing", "stated_assumption")
    # Every lower candidate that was given is listed, not dropped, with a differing value
    # named in the note.
    lower = [b for b in PRECEDENCE[PRECEDENCE.index(basis) + 1:] if {
        "dob_job_filing": with_job, "stated_assumption": with_assumption}.get(b)
    ] if basis != "unknown" else []
    assert [entry["basis"] for entry in result.considered] == lower
    for entry in result.considered:
        assert entry["reason"] == (
            f"Not used: {BASIS_LABELS[basis]} comes first and gives a different value.")
        assert f"{BASIS_LABELS[entry['basis']]} gives" in result.fact["note"]


def test_equal_lower_value_is_listed_as_same_value() -> None:
    result = resolve(job(), assumption=StatedAssumption(12000, "Same as the filing.", AT))
    assert result.basis == "dob_job_filing"
    assert result.considered[0]["reason"] == (
        "Not used: DOB job filing comes first and gives the same value.")


# ---------------------------------------------------------------------------
# Unknown with a reason
# ---------------------------------------------------------------------------


def test_nothing_supplied_is_an_explicit_unknown_with_the_reason() -> None:
    result = resolve()
    assert_unknown(result, "No DOB job-filing rows were supplied.",
                   "No certificate of occupancy figure or stated assumption was entered.")
    assert result.fact["note"].startswith("Needs existing zoning floor area")
    assert result.considered == ()


def test_filing_not_completed_is_set_aside_and_the_value_is_unknown() -> None:
    pending = job(job_status="R", job_status_descrp="PERMIT ISSUED - ENTIRE JOB/WORK",
                  signoff_date=None)
    result = resolve(pending)
    assert_unknown(result, "No completed DOB filing states a zoning floor area for "
                           "building 1000001.")
    (entry,) = result.considered
    assert entry["value"] == 12000 and entry["bin"] == "1000001"
    assert "not shown as completed" in entry["reason"]


def test_certificate_row_naming_the_job_shows_the_work_completed() -> None:
    pending = job(job_status="R", job_status_descrp="PERMIT ISSUED - ENTIRE JOB/WORK",
                  signoff_date=None)
    result = resolve(pending, certificate_rows=(issued_co(),))
    assert (result.basis, result.fact["value"]) == ("dob_job_filing", 12000)
    assert "certificate of occupancy 1000001-0000001 issued" in result.fact["note"]
    assert result.completion == {
        "kind": "certificate_of_occupancy",
        "dataset": "DOB NOW: Certificate of Occupancy (pkdm-hqz6)",
        "query_ref": "test-fixture-synthetic://pkdm-hqz6", "retrieved_at": AT,
        "document_ref": "1000001-0000001", "job": "100000001",
        "issued": "03/01/21  9:00:00 AM", "filing_type": "Final"}


@pytest.mark.parametrize("co_row", [
    issued_co(bbl="1000010101", bin="1000009"),        # another lot and building
    issued_co(c_of_o_status="Withdrawn"),               # not issued
    issued_co(job_filing_name="100000999"),             # another job
])
def test_certificate_row_that_does_not_name_this_job_and_lot_completes_nothing(co_row) -> None:
    pending = job(job_status="R", job_status_descrp="PERMIT ISSUED - ENTIRE JOB/WORK",
                  signoff_date=None)
    assert resolve(pending, certificate_rows=(co_row,)).basis == "unknown"


def test_rows_for_other_lots_are_not_used() -> None:
    other = job(bbl="1000010101", lot="00101")
    assert_unknown(resolve(other), "No DOB job filing in the supplied rows is for tax lot "
                                   "1000010100 (1 rows for other or unidentified lots")


def test_row_whose_bbl_and_lot_disagree_is_set_aside() -> None:
    result = resolve(job(lot="00001"))
    assert result.basis == "unknown"
    (entry,) = result.considered
    assert "name different lots (1000010001, 1000010100)" in entry["reason"]


def test_bin_in_the_bbl_column_falls_back_to_borough_block_lot() -> None:
    # docs/research/dob-legacy-sources.md section 3.1: ic3t-wcy2 'bbl' can hold the BIN.
    result = resolve(job(bbl="1000001"))
    assert (result.basis, result.fact["value"]) == ("dob_job_filing", 12000)


def test_demolished_building_drops_out_and_the_new_building_counts() -> None:
    old = job("100000010", bin__="1000002", job_type="A1", proposed_zoning_sqft="3000")
    demolition = job("100000011", bin__="1000002", job_type="DM", proposed_zoning_sqft="0")
    result = resolve(old, demolition, job())
    assert (result.basis, result.fact["value"]) == ("dob_job_filing", 12000)
    (entry,) = result.considered
    assert entry["value"] == 3000
    assert "demolished (demolition job 100000011 signed off 01/15/2020)" in entry["reason"]


def test_only_demolished_buildings_give_unknown() -> None:
    demolition = job("100000011", job_type="DM", proposed_zoning_sqft="0")
    assert_unknown(resolve(job(), demolition), "name no standing building")


def test_figures_for_two_standing_buildings_are_never_added() -> None:
    second = job("100000002", bin__="1000002", proposed_zoning_sqft="5000")
    assert_unknown(resolve(job(), second), "more than one standing building "
                                           "(1000001, 1000002)")


def test_standing_building_without_a_figure_leaves_the_lot_total_unknown() -> None:
    second = job("100000002", bin__="1000002", job_type="A2", proposed_zoning_sqft="0")
    assert_unknown(resolve(job(), second), "for building 1000002.")


def test_completed_filings_that_disagree_give_unknown() -> None:
    later = job("100000003", job_type="A1", existing_zoning_sqft="12000",
                proposed_zoning_sqft="14000", enlargement_sq_footage="2000")
    assert_unknown(resolve(job(), later), "Completed DOB filings for building 1000001 "
                                          "disagree")


def test_signed_off_enlargement_alone_gives_its_figure() -> None:
    enlarged = job("100000003", job_type="A1", existing_zoning_sqft="12000",
                   proposed_zoning_sqft="14000", enlargement_sq_footage="2000")
    assert resolve(enlarged).fact["value"] == 14000


# ---------------------------------------------------------------------------
# A figure must be shown to describe one building (zoning-lot figures fail closed)
# ---------------------------------------------------------------------------

# The shape of recorded DOB BIS job 421803891 (tax lot 4073340001), signed off here.
ZONING_LOT_TEXT = ("ALTERATION -1 APPLICATION TO BE FILED UNDER TAX LOT #1 TO REFLECT ONE (1) "
                   "ZONING LOT AND (2) TAX LOTS (LOT #1 &amp; #70). NO WORK TO BE DONE UNDER "
                   "THIS APPLICATION.")


@pytest.mark.parametrize(("overrides", "why"), [
    ({"job_description": ZONING_LOT_TEXT}, "Its text mentions a zoning lot"),
    ({"job_description": "NO WORK UNDER THIS APPLICATION."}, "It states no work"),
    ({}, "states no enlargement but changes the zoning figure from 9,100 to 39,772"),
])
def test_filing_not_shown_to_describe_one_building_fails_closed(overrides, why) -> None:
    alteration = job("100000004", job_type="A1", existing_zoning_sqft="9100",
                     proposed_zoning_sqft="39772", **overrides)
    for rows in ((alteration,), (job(), alteration)):  # alone, and beside the NB's 12,000
        result = resolve(*rows)
        assert_unknown(result, "DOB BIS job 100000004, document 01 for building 1000001 is "
                               "not shown to describe this building alone", why)
        assert 39772 in [entry["value"] for entry in result.considered]


def test_new_building_without_zoning_lot_text_is_used() -> None:
    # An NB changes the figure from 0 by definition; with no zoning-lot text it is used,
    # but its zoning-lot scope is still stated as not established.
    result = resolve(job(existing_zoning_sqft=None))
    assert result.fact["value"] == 12000 and result.zoning_lot_mentions == ()


def test_same_block_rows_mentioning_a_zoning_lot_are_cited_not_used() -> None:
    other_lot = job("100000005", lot="00001", bbl="1000010001", bin__="1000009",
                    job_type="A1", job_status_descrp="PLAN EXAM - DISAPPROVED",
                    existing_zoning_sqft="9100", proposed_zoning_sqft="39772",
                    job_description=ZONING_LOT_TEXT)
    other_block = job("100000006", block="00002", bbl="1000020001", lot="00001",
                      job_description=ZONING_LOT_TEXT)
    result = resolve(job(), other_lot, other_block)
    assert result.fact["value"] == 12000
    (mention,) = result.zoning_lot_mentions
    assert mention == {"document_ref": "DOB BIS job 100000005, document 01",
                       "tax_lots": ["1000010001"], "text": ZONING_LOT_TEXT,
                       "query_ref": QUERY, "retrieved_at": AT}
    assert ("DOB BIS job 100000005, document 01 (tax lot 1000010001) mentions a zoning lot"
            in result.fact["note"])


def test_repeated_rows_that_disagree_are_set_aside() -> None:
    result = resolve(job(), job(proposed_zoning_sqft="12500"))
    assert result.basis == "unknown"
    assert "Repeated rows for this filing disagree" in result.considered[0]["reason"]


def test_identical_repeated_rows_collapse() -> None:
    assert resolve(job(), job()).fact["value"] == 12000


def test_building_count_that_does_not_match_gives_unknown() -> None:
    assert_unknown(resolve(job(), count=2), "City records count 2 building(s)")
    assert resolve(job(), count=1).fact["value"] == 12000
    note = resolve(job()).fact["note"]
    assert "building count for the lot was not available to check" in note


def test_unreadable_zoning_figure_is_set_aside() -> None:
    result = resolve(job(proposed_zoning_sqft="12,000"))
    assert result.basis == "unknown"
    assert "is not a number" in result.considered[0]["reason"]


# ---------------------------------------------------------------------------
# DOF / PLUTO building area can never become existing zoning floor area
# ---------------------------------------------------------------------------


def test_no_input_can_carry_a_building_area() -> None:
    evidence_fields = {f.name for f in dataclasses.fields(ExistingFloorAreaEvidence)}
    assert evidence_fields == {"dob_job_filings", "certificates", "co_statement", "assumption"}
    parameters = inspect.signature(resolve_existing_zoning_floor_area).parameters
    assert list(parameters) == ["bbl", "evidence", "recorded_building_count"]
    site_parameters = inspect.signature(site_facts.build_site_facts).parameters
    assert list(site_parameters) == ["profile", "frontage_streets", "existing_floor_area"]


@pytest.mark.parametrize(("dataset_id", "why"), [
    ("64uk-42ks", "PLUTO building area (BldgArea) is DOF building area"),
    ("w9ak-ipjd", "DOB NOW job filings carry no zoning floor-area column"),
    ("abcd-1234", "is not a DOB job-filing or certificate dataset"),
])
def test_building_area_datasets_are_refused(dataset_id: str, why: str) -> None:
    with pytest.raises(ValueError, match=re.escape(why)):
        DobRecordSet(dataset_id, ({"bldgarea": "54488"},), AT, QUERY)


def test_record_sets_go_only_where_they_belong() -> None:
    with pytest.raises(ValueError, match="dob_job_filings must come from ic3t-wcy2"):
        ExistingFloorAreaEvidence(dob_job_filings=(certificates(issued_co()),))
    with pytest.raises(ValueError, match="certificates must come from"):
        ExistingFloorAreaEvidence(certificates=(jobs(job()),))


def test_total_construction_floor_area_is_never_read() -> None:
    row = job(proposed_zoning_sqft="0", total_construction_floor_area="54488")
    result = resolve(row)
    assert result.basis == "unknown" and "54,488" not in result.fact["note"]
    assert read_dob_filings(BBL, (jobs(row),)).value is None


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), True, "12000"])
def test_entered_values_must_be_positive_numbers(value) -> None:
    with pytest.raises(ValueError, match="positive number of square feet"):
        StatedAssumption(value, "statement", AT)
    with pytest.raises(ValueError, match="positive number of square feet"):
        CertificateOfOccupancyStatement(value, "1000001-0000001", AT)


def test_entries_need_a_statement_a_certificate_number_and_a_time() -> None:
    with pytest.raises(ValueError, match="statement"):
        StatedAssumption(1000, "  ", AT)
    with pytest.raises(ValueError, match="co_number"):
        CertificateOfOccupancyStatement(1000, "", AT)
    with pytest.raises(ValueError, match="entered_at"):
        StatedAssumption(1000, "statement", "2026-09-30")
    with pytest.raises(ValueError, match="bbl"):
        resolve_existing_zoning_floor_area("4157401")
    with pytest.raises(ValueError, match="recorded_building_count"):
        resolve_existing_zoning_floor_area(BBL, recorded_building_count=-1)


def test_blocks_and_contract_version_match_site_facts() -> None:
    assert site_facts.BLOCKS["existing_zoning_floor_area"] == BLOCKED_OUTPUTS
    assert resolve_module.SITE_FACT_CONTRACT_VERSION == site_facts.SITE_FACT_CONTRACT_VERSION
