"""The lot choice with condo base lots, and its study-contract shapes (queue item B-07).

Plan §3 step 2: "This property has N lots: use all (default), or pick. Each lot is listed
with its approximate size. Lots are tax lots, not condo apartments. For 298 Wallabout they
are lots 32 and 33." Plan §4: condo base lots have no PLUTO record, so they use rank 3
(tax map) unless DOF dimensions are found.

The condo billing lot 3022647515 resolves to base lots 3022640032 and 3022640033 (condo key
301313, number 1313) in the byte-faithful research body of
tests/connectors/test_dtm_condo_soda.py (BILLING_3022647515_BODY). Here the accepted seam
``resolve_condo_billing`` runs with a resolver double returning that result. Outlines are
SYNTHETIC: the recorded Wallabout DTM outlines are EPSG:4326, display only, never measured.
"""

from __future__ import annotations

import pytest

from app.connectors.condo_base_lot import resolve_condo_billing
from app.connectors.dtm_condo_soda import (
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
    CondoBaseLotResult,
    SourceTimeoutError,
)
from app.spatial.multi_lot_site import (
    COMBINATION_NOT_OFFERED,
    COMBINATION_OFFERED,
    ORIGIN_CONDO_BASE_LOT,
    ORIGIN_TAX_LOT,
    SiteLot,
    build_lot_choice,
    derive_multi_lot_site,
    study_lot_selection,
    study_lots,
)
from app.spatial.multi_lot_site.lot_choice import NO_OUTLINE_SUPPLIED
from app.spatial.site_geometry import (
    LABEL_CITY_RECORDS,
    LABEL_TAX_MAP,
    LABEL_UNKNOWN,
    CityRecordLot,
    LotOutline,
)
from tests.spatial._study_contract import assert_valid_study_part as assert_valid

CRS = {"wkid": 102718, "latest_wkid": 2263}
BILLING = "3022647515"
BASE = ("3022640032", "3022640033")
UNIT = "3022642601"
PLAIN = "4073340070"


def resolution(status=STATUS_RESOLVED, base=BASE, error=None):
    def resolver(bbl, *, correlation_id, **_):
        if error is not None:
            raise error
        return CondoBaseLotResult(
            status=status, input_value=bbl, lot_class="billing", correlation_id=correlation_id,
            retrieved_at="2026-10-01T00:00:00Z", resolution_path="billing_bbl",
            base_bbls=list(base) if status == STATUS_RESOLVED else [], condo_number="1313",
            condo_key="301313", provenance=[{"dataset_id": "p8u6-a6it"}])
    return resolve_condo_billing(BILLING, correlation_id="b07-test", resolver=resolver)


def outline_lot(bbl: str, ring, area=None) -> SiteLot:
    records = CityRecordLot(area, None, None, "synthetic DOF") if area else None
    return SiteLot(bbl, LotOutline(tuple(ring), CRS, "synthetic tax-lot"), city_records=records)


def rect(x0, x1):
    return ((x0, 0.0), (x1, 0.0), (x1, 100.0), (x0, 100.0))


# ------------------------------------------------------------------------------ the listing


def test_condo_billing_lot_is_replaced_by_its_base_lots():
    choice = build_lot_choice([BILLING], {}, condo_resolutions={BILLING: resolution()})
    assert choice.bbls == BASE
    assert {entry.origin for entry in choice.entries} == {ORIGIN_CONDO_BASE_LOT}
    condo = choice.entries[0].condo
    assert (condo.billing_bbl, condo.condo_key, condo.condo_number, condo.dataset_ids) == (
        BILLING, "301313", "1313", ("p8u6-a6it",))
    assert choice.not_listed == ()
    assert any("stands for its recorded base lot(s) 3022640032, 3022640033" in note
               for note in choice.notes)
    # No outline supplied: listed, size unknown (never guessed).
    for entry in choice.entries:
        assert entry.lot.outline_refusal == NO_OUTLINE_SUPPLIED
        assert (entry.size.value, entry.size.label) == (None, LABEL_UNKNOWN)


def test_condo_base_lots_without_pluto_use_the_tax_map_area():
    lots = {BASE[0]: outline_lot(BASE[0], rect(0, 50)), BASE[1]: outline_lot(BASE[1], rect(50, 75))}
    choice = build_lot_choice([BILLING], lots, condo_resolutions={BILLING: resolution()})
    sizes = [(e.bbl, e.size.value, e.size.label) for e in choice.entries]
    assert sizes == [(BASE[0], 5000.0, LABEL_TAX_MAP), (BASE[1], 2500.0, LABEL_TAX_MAP)]
    assert any("Condo base lots have no PLUTO record" in note for note in choice.notes)
    # Selecting both base lots: one block, touching, combined like any tax lots.
    site = derive_multi_lot_site(choice, None, None)
    assert site.combination.status == COMBINATION_OFFERED
    assert site.geometry.lot_area.value == 7500.0
    assert site.provenance["condo_base_lots"] == {BASE[0]: BILLING, BASE[1]: BILLING}
    assert site.lot_area_sum.label == LABEL_UNKNOWN


def test_base_lot_dimensions_from_dof_rank_as_city_records():
    lots = {BASE[0]: outline_lot(BASE[0], rect(0, 50), area=4990.0)}
    choice = build_lot_choice([BILLING], lots, condo_resolutions={BILLING: resolution()})
    assert (choice.entries[0].size.value, choice.entries[0].size.label) == (
        4990.0, LABEL_CITY_RECORDS)


@pytest.mark.parametrize(("given", "expected"), [
    (None, "its base lots were not looked up"),
    (lambda: resolution(STATUS_UNRESOLVED), "it was not resolved to its base lots (unresolved)"),
    (lambda: resolution(error=SourceTimeoutError("slow", correlation_id="t")),
     "it was not resolved to its base lots (error, " + SourceTimeoutError.error_type + ")"),
])
def test_unresolved_condo_billing_lot_is_not_listed(given, expected):
    resolutions = {} if given is None else {BILLING: given()}
    choice = build_lot_choice([BILLING, PLAIN], {}, condo_resolutions=resolutions)
    assert choice.bbls == (PLAIN,)
    (missing,) = choice.not_listed
    assert missing.bbl == BILLING
    assert expected in missing.reason and missing.reason.endswith("Check needed.")


def test_condo_unit_and_malformed_entries_are_not_tax_lots():
    choice = build_lot_choice([UNIT, "12345", PLAIN, PLAIN], {})
    assert choice.bbls == (PLAIN,)
    assert choice.entries[0].origin == ORIGIN_TAX_LOT
    reasons = {item.bbl: item.reason for item in choice.not_listed}
    assert "is a condo unit (an apartment), not a tax lot of land" in reasons[UNIT]
    assert reasons["12345"] == "Not a valid 10-digit BBL."


def test_size_prefers_city_records_then_tax_map_then_unknown():
    recorded = outline_lot("1001000010", rect(0, 100), area=9990.0)
    mapped = outline_lot("1001000011", rect(100, 200))
    broken = SiteLot("1001000012", LotOutline(((0, 0), (1, 1), (2, 2)), CRS, "synthetic"))
    choice = build_lot_choice([lot.bbl for lot in (recorded, mapped, broken)],
                              {lot.bbl: lot for lot in (recorded, mapped, broken)})
    sizes = [(e.size.value, e.size.label) for e in choice.entries]
    assert sizes == [(9990.0, LABEL_CITY_RECORDS), (10000.0, LABEL_TAX_MAP),
                     (None, LABEL_UNKNOWN)]
    assert choice.entries[2].size.reason.startswith("No recorded lot area and no usable")


def test_mismatched_inputs_are_refused():
    with pytest.raises(ValueError, match="holds tax lot"):
        build_lot_choice([PLAIN], {"4073340001": SiteLot(PLAIN, None, "none")})
    with pytest.raises(ValueError, match="give an outline or the reason"):
        SiteLot(PLAIN, None)
    with pytest.raises(ValueError, match="not a valid tax lot BBL"):
        SiteLot("4-7334-70", None, "none")
    with pytest.raises(ValueError, match="canonical 10-digit string"):
        SiteLot(4073340070, None, "none")


# ------------------------------------------------------------------- study contract shapes


@pytest.mark.parametrize("picked", [None, [BASE[0]]])
def test_lot_choice_and_selection_validate_against_the_study_contract(picked):
    lots = {BASE[0]: outline_lot(BASE[0], rect(0, 50)), BASE[1]: outline_lot(BASE[1], rect(50, 75))}
    choice = build_lot_choice([BILLING], lots, condo_resolutions={BILLING: resolution()})
    site = derive_multi_lot_site(choice, picked, None)
    items = study_lots(choice, site.selected_bbls)
    for item in items:
        assert_valid(item, "#/$defs/lot")
    assert [item["selected"] for item in items] == ([True, True] if picked is None
                                                    else [True, False])
    selection = study_lot_selection(site)
    assert_valid(selection, "#/properties/lot_selection")
    assert selection["statement"] == (
        "Based on the lots you selected — the app does not verify the zoning lot")


def test_not_offered_selection_validates_with_its_reason():
    lots = {BASE[0]: outline_lot(BASE[0], rect(0, 50)),
            BASE[1]: outline_lot(BASE[1], rect(80, 100))}
    choice = build_lot_choice([BILLING], lots, condo_resolutions={BILLING: resolution()})
    site = derive_multi_lot_site(choice, None, None)
    selection = study_lot_selection(site)
    assert selection["combination"]["status"] == COMBINATION_NOT_OFFERED
    assert "30.00 ft apart" in selection["combination"]["reason"]
    assert_valid(selection, "#/properties/lot_selection")
    assert_valid(selection["combination"], "#/$defs/combination")
