"""§8a zoning-lot-history hidden-issue flags (queue item B-09, slice 2; plan L-11, P-2).

Offline and deterministic. The flag logic runs on synthetic recorded documents and on a
synthetic B-05 result; the real 215-16 Northern Blvd pack is replayed with no network for the
recorded DOB zoning-lot mention and the recorded ACRIS index metadata (codes never
interpreted).
"""

from __future__ import annotations

import json

import pytest

from app.profile.existing_floor_area import (
    DobRecordSet,
    ExistingFloorAreaEvidence,
    resolve_existing_zoning_floor_area,
)
from app.profile.hidden_issue_flags import (
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    STATUS_NOT_FLAGGED,
    STATUS_OPPORTUNITY,
    FlagGroup,
    HiddenIssueFlag,
    zoning_lot_history_group,
)
from app.profile.hidden_issue_flags.zoning_lot_history import GROUP_ID
from tests.spatial._northern_replay import BBL as BENCHMARK_BBL
from tests.spatial._northern_replay import MANIFEST, PACK

BBL = "1000010100"  # synthetic: Manhattan block 1, lot 100

EXPECTED_ITEMS = (
    "zoning_lot_history.recorded_descriptions_or_mergers",
    "zoning_lot_history.floor_area_transferred",
    "zoning_lot_history.restrictive_declarations",
    "zoning_lot_history.e_designations",
)
# Items whose source can be records on file (items 1-3); item 4 (E-designations) never is.
RECORDS_BACKED = EXPECTED_ITEMS[:3]


def record(ref: str, *, tax_lots=("1000010100",), text="recorded document (not interpreted)",
           query_ref="q", retrieved_at="2026-09-30T06:14:32Z") -> dict:
    """A recorded zoning-lot document in the RECORD_KEYS shape (ACRIS index metadata etc.)."""
    return {"document_ref": ref, "tax_lots": list(tax_lots), "text": text,
            "query_ref": query_ref, "retrieved_at": retrieved_at}


def mention_efa(*refs: str):
    """A synthetic B-05 result carrying DOB zoning-lot mentions (via a stated assumption)."""
    efa = resolve_existing_zoning_floor_area(
        BBL, ExistingFloorAreaEvidence())  # Unknown — enter; we only use its mentions
    mentions = tuple(
        {"document_ref": r, "tax_lots": ["1000010101"], "text": "ONE ZONING LOT",
         "query_ref": "q", "retrieved_at": "2026-09-30T06:00:00Z"} for r in refs)
    return efa.__class__(efa.fact, efa.basis, efa.basis_label, efa.reason, efa.considered,
                         efa.completion, mentions, efa.scope, efa.zoning_lot_scope)


def item(group: FlagGroup, item_id: str) -> HiddenIssueFlag:
    (flag,) = [f for f in group.flags if f.item_id == item_id]
    return flag


# --- group shape -------------------------------------------------------------------------

def test_group_has_the_four_section_8a_zoning_lot_history_items_in_order():
    group = zoning_lot_history_group(BBL)
    assert group.group_id == GROUP_ID == "zoning_lot_history"
    assert group.title == "Zoning-lot history"
    assert group.lot_bbl == BBL
    assert tuple(f.item_id for f in group.flags) == EXPECTED_ITEMS
    assert all(f.phase == "1" for f in group.flags)


def test_group_round_trips_to_dict():
    group = zoning_lot_history_group(BBL, recorded_documents=[record("ACRIS document 1")])
    payload = group.to_dict()
    assert payload["group_id"] == "zoning_lot_history"
    assert [f["item_id"] for f in payload["flags"]] == list(EXPECTED_ITEMS)
    assert payload["flags"][0]["status"] == STATUS_FLAG


# --- flag-only invariant (plan P-2) ------------------------------------------------------

def test_group_is_flag_only_never_opportunity_or_not_flagged():
    """P-2: this group only ever reminds or asks for a check - it never clears a lot."""
    for group in (
        zoning_lot_history_group(BBL),
        zoning_lot_history_group(BBL, recorded_documents=[record("ACRIS document 1")]),
        zoning_lot_history_group(BBL, existing_floor_area=mention_efa("DOB BIS job 9, doc 01")),
    ):
        for flag in group.flags:
            assert flag.status in (STATUS_FLAG, STATUS_CHECK_NEEDED)
            assert flag.status not in (STATUS_OPPORTUNITY, STATUS_NOT_FLAGGED)


# --- nothing on file: every item is "Check needed" naming the missing source -------------

def test_no_sources_every_item_is_check_needed_naming_its_source():
    group = zoning_lot_history_group(BBL)
    for item_id in EXPECTED_ITEMS:
        flag = item(group, item_id)
        assert flag.status == STATUS_CHECK_NEEDED
        assert flag.typical_source  # names what would answer it
        assert not flag.evidence
    # Item 4 names its own, non-ACRIS source and says ACRIS does not establish it.
    e = item(group, "zoning_lot_history.e_designations")
    assert "Appendix C" in e.detail and "ACRIS" in e.detail
    assert "never guessed" in e.detail


# --- DOB zoning-lot mentions back item 1 only --------------------------------------------

def test_dob_mentions_flag_item_1_with_fact_ref_but_not_items_2_and_3():
    efa = mention_efa("DOB BIS job 421803891, document 01")
    group = zoning_lot_history_group(BBL, existing_floor_area=efa)
    one = item(group, "zoning_lot_history.recorded_descriptions_or_mergers")
    assert one.status == STATUS_FLAG
    assert "DOB BIS job 421803891, document 01" in one.detail
    assert "1000010101" in one.detail  # the other tax lot it is filed on
    assert one.fact_refs == (efa.fact["fact_id"],)
    # A DOB zoning-lot mention is not a development-rights transfer or a declaration.
    assert item(group, "zoning_lot_history.floor_area_transferred").status == STATUS_CHECK_NEEDED
    assert item(group, "zoning_lot_history.restrictive_declarations").status == STATUS_CHECK_NEEDED


# --- recorded ACRIS documents back items 1-3 (never item 4) ------------------------------

def test_recorded_documents_flag_items_1_to_3_as_reminders_not_item_4():
    group = zoning_lot_history_group(
        BBL, recorded_documents=[record("ACRIS document A"), record("ACRIS document B")])
    for item_id in RECORDS_BACKED:
        flag = item(group, item_id)
        assert flag.status == STATUS_FLAG
        assert "2 recorded records on file" in flag.detail
        assert "ACRIS document A" in flag.detail and "ACRIS document B" in flag.detail
        assert "does not verify the zoning lot" in flag.detail
        assert len(flag.evidence) == 2
    assert item(group, "zoning_lot_history.e_designations").status == STATUS_CHECK_NEEDED


def test_item_2_is_a_p2_reminder_that_never_concludes_a_transfer():
    flag = item(
        zoning_lot_history_group(BBL, recorded_documents=[record("ACRIS document A")]),
        "zoning_lot_history.floor_area_transferred")
    assert flag.status == STATUS_FLAG
    assert "P-2" in flag.detail
    assert "may have been sold or merged" in flag.detail
    assert "never verified here" in flag.detail
    # Never concludes a number or a transfer (no computation anywhere in this group).
    assert "sq ft" not in flag.detail and "transferred:" not in flag.detail


# --- codes are not interpreted: the output ignores the recorded text ---------------------

def test_recorded_text_and_codes_do_not_change_the_output():
    """"Codes not interpreted": a document typed DECL, MTGE or ZONE yields the same flags."""
    base = zoning_lot_history_group(
        BBL, recorded_documents=[record("ACRIS document A", text="doc_type DECL")])
    other = zoning_lot_history_group(
        BBL, recorded_documents=[record("ACRIS document A", text="doc_type MTGE zoning lot")])
    assert base.to_dict() == other.to_dict()
    # No recorded code leaks into a human category in any detail line.
    for flag in base.flags:
        lowered = flag.detail.lower()
        assert "mortgage" not in lowered and "deed" not in lowered


# --- dedupe and tax-lot union ------------------------------------------------------------

def test_duplicate_document_refs_collapse_and_union_their_tax_lots():
    group = zoning_lot_history_group(BBL, recorded_documents=[
        record("ACRIS document A", tax_lots=["1000010100"]),
        record("ACRIS document A", tax_lots=["1000010101"]),
    ])
    flag = item(group, "zoning_lot_history.restrictive_declarations")
    assert "1 recorded record on file" in flag.detail
    assert flag.evidence[0]["source"]["tax_lots"] == ["1000010100", "1000010101"]


def test_long_lists_are_capped_but_the_count_is_stated_in_full():
    docs = [record(f"ACRIS document {i:02d}") for i in range(9)]
    flag = item(zoning_lot_history_group(BBL, recorded_documents=docs),
                "zoning_lot_history.recorded_descriptions_or_mergers")
    assert "9 recorded records on file" in flag.detail
    assert "and 3 more" in flag.detail  # 9 - the 6-item cap


# --- validation --------------------------------------------------------------------------

def test_bad_bbl_and_wrong_efa_type_raise():
    with pytest.raises(ValueError, match="10-digit BBL"):
        zoning_lot_history_group("123")
    with pytest.raises(ValueError, match="ExistingFloorAreaResult"):
        zoning_lot_history_group(BBL, existing_floor_area=object())


def test_malformed_recorded_documents_raise():
    with pytest.raises(ValueError, match="needs"):
        zoning_lot_history_group(BBL, recorded_documents=[{"document_ref": "x"}])
    with pytest.raises(ValueError, match="tax_lots must be a list"):
        zoning_lot_history_group(BBL, recorded_documents=[
            {"document_ref": "x", "tax_lots": "nope", "text": "t",
             "query_ref": "q", "retrieved_at": "r"}])


# --- recorded benchmark: 215-16 Northern Blvd lot 70 (no network) ------------------------

def _record_set(name: str) -> DobRecordSet:
    entry = MANIFEST[name]
    rows = json.loads((PACK / name).read_bytes().decode("utf-8"))
    return DobRecordSet(entry["dataset_id"], rows, entry["retrieved_at"], entry["url"])


def _recorded(prefixes: tuple[str, ...]) -> tuple[DobRecordSet, ...]:
    return tuple(_record_set(n) for n in sorted(MANIFEST) if n.startswith(prefixes))


def _benchmark_acris_documents() -> list[dict]:
    """Recorded ACRIS index metadata for lot 70, built from the fixtures WITHOUT reading the
    documents or interpreting any doc_type code (the module never sees the codes)."""
    legals = json.loads(
        (PACK / "acris_legals_8h5j-fqxa_bbl_4-7334-70.json").read_bytes().decode("utf-8"))
    entry = MANIFEST["acris_legals_8h5j-fqxa_bbl_4-7334-70.json"]
    docs: dict[str, dict] = {}
    for row in legals:
        bbl = f"{row['borough']}{int(row['block']):05d}{int(row['lot']):04d}"
        ref = f"ACRIS document {row['document_id']}"
        docs.setdefault(ref, record(
            ref, tax_lots=[bbl], text="ACRIS legals index metadata (recorded, not interpreted)",
            query_ref=entry["url"], retrieved_at=entry["retrieved_at"]))
    return list(docs.values())


def test_benchmark_lot_70_reminds_from_the_recorded_dob_mention_and_acris_metadata():
    evidence = ExistingFloorAreaEvidence(
        dob_job_filings=_recorded(("dob_bis_jobs_",)),
        certificates=_recorded(("dob_bis_co_", "dob_now_co_")))
    efa = resolve_existing_zoning_floor_area(BENCHMARK_BBL, evidence)
    assert efa.fact["value"] is None  # B-05: Unknown — enter (figure set aside, mention cited)
    group = zoning_lot_history_group(
        BENCHMARK_BBL, existing_floor_area=efa,
        recorded_documents=_benchmark_acris_documents())

    one = item(group, "zoning_lot_history.recorded_descriptions_or_mergers")
    assert one.status == STATUS_FLAG
    # The recorded DOB zoning-lot mention + the 7 ACRIS documents are all carried as evidence
    # (the one-line detail caps the listing at 6, but every record is in the evidence).
    labels = [e["label"] for e in one.evidence]
    assert "DOB BIS job 421803891, document 01" in labels
    dob = next(e for e in one.evidence if e["label"] == "DOB BIS job 421803891, document 01")
    assert dob["source"]["tax_lots"] == ["4073340001"]  # filed on a tax lot not selected
    assert len(one.evidence) == 8
    assert one.fact_refs == (efa.fact["fact_id"],)

    # Recorded ACRIS index metadata backs items 2 and 3 as reminders.
    assert item(group, "zoning_lot_history.floor_area_transferred").status == STATUS_FLAG
    assert item(group, "zoning_lot_history.restrictive_declarations").status == STATUS_FLAG
    # Item 4 (E-designations) has no connected source, ACRIS or otherwise.
    assert item(group, "zoning_lot_history.e_designations").status == STATUS_CHECK_NEEDED

    # Nothing concludes the zoning lot, verifies a merger, or computes an area.
    for flag in group.flags:
        assert "sq ft" not in flag.detail
        if flag.status == STATUS_FLAG:
            assert "does not verify the zoning lot" in flag.detail
