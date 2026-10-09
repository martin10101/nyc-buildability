"""Multi-lot site math on a small synthetic block (queue item B-07; plan M2-05, §3 step 2, §4).

Offline and deterministic. EPSG:2263-stamped rings in feet. Block 100 (borough 1):

      North Street (60 ft, center line y = 130)
    +---------+---------+---------+
    | lot 10  | lot 11  | lot 12  |  East Avenue (80 ft, center line x = 340)
    +---------+---------+---------+
    | lot 20  | lot 21  |                lot 40 is on block 101, east of East Avenue
    +---------+---------+
      South Street (60 ft, center line y = -180)

Lots are 100 ft wide; lots 10-12 are 100 ft deep and lots 20-21 150 ft. Lot 21 meets lot 10
only at the point (100, 0). Plan M2-05 done-when: selecting 1, 2 or all lots updates the
outline, frontage, lot type and area correctly.
"""

from __future__ import annotations

from dataclasses import fields

import pytest

from app.profile.existing_floor_area import (
    ExistingFloorAreaEvidence,
    StatedAssumption,
    resolve_existing_zoning_floor_area,
)
from app.spatial.multi_lot_site import (
    COMBINATION_NOT_OFFERED,
    COMBINATION_OFFERED,
    COMBINATION_SINGLE_LOT,
    EXISTING_ATTACHED,
    EXISTING_NOT_SUPPLIED,
    SELECTION_ALL,
    SELECTION_STATEMENT,
    SELECTION_SUBSET,
    ZONING_LOT_CHECK_NEEDED,
    LotSelectionError,
    MultiLotSite,
    SiteLot,
    build_lot_choice,
    derive_multi_lot_site,
    derive_multi_lot_site_if_enabled,
    multi_lot_site_enabled,
    study_lot_selection,
)
from app.spatial.multi_lot_site.zoning_lot import MENTION_KEYS, TEXT_NOT_READ
from app.spatial.site_geometry import (
    LABEL_CITY_RECORDS,
    LABEL_TAX_MAP,
    LABEL_UNKNOWN,
    CityRecordLot,
    LotOutline,
    StreetCenterline,
    StreetData,
    derive_site_geometry,
)
from app.spatial.site_geometry.results import STATUS_COMPLETE, STATUS_REFUSED

CRS = {"wkid": 102718, "latest_wkid": 2263}


def bbl(lot: int, block: int = 100) -> str:
    return f"1{block:05d}{lot:04d}"


def rect(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


RINGS = {
    10: rect(0, 0, 100, 100), 11: rect(100, 0, 200, 100), 12: rect(200, 0, 300, 100),
    20: rect(0, -150, 100, 0), 21: rect(100, -150, 200, 0),
}
NORTH, EAST, SOUTH = "North Street", "East Avenue", "South Street"
STREETS = StreetData((
    StreetCenterline(NORTH, NORTH, 1, (((-400.0, 130.0), (700.0, 130.0)),), "60", True),
    StreetCenterline(EAST, EAST, 2, (((340.0, -500.0), (340.0, 500.0)),), "80", True),
    StreetCenterline(SOUTH, SOUTH, 3, (((-400.0, -180.0), (700.0, -180.0)),), "60", True),
), (-1000.0, -1000.0, 1000.0, 1000.0), CRS, "synthetic streets")


def site_lot(lot: int, ring=None, *, block: int = 100, area: float | None = None,
             existing=None) -> SiteLot:
    ring = RINGS[lot] if ring is None else ring
    records = CityRecordLot(area, None, None, "synthetic PLUTO") if area else None
    return SiteLot(bbl(lot, block), LotOutline(tuple(ring), CRS, "synthetic tax-lot"),
                   city_records=records, existing_floor_area=existing)


def choice(*lots: SiteLot):
    return build_lot_choice([lot.bbl for lot in lots], {lot.bbl: lot for lot in lots})


def frontages(site: MultiLotSite) -> dict[str, float]:
    return {f.street_name: f.length.value for f in site.geometry.frontages}


ROW = choice(site_lot(10, area=9990.0), site_lot(11, area=10010.0), site_lot(12, area=10000.0))


# ------------------------------------------------------------ selecting 1, 2 or all lots


def test_one_lot_is_exactly_the_single_lot_geometry():
    lot = ROW.entries[0].lot
    site = derive_multi_lot_site(ROW, [lot.bbl], STREETS)
    assert site.geometry == derive_site_geometry(lot.outline, STREETS, lot.city_records)
    assert (site.selection_mode, site.combination.status) == (
        SELECTION_SUBSET, COMBINATION_SINGLE_LOT)
    assert site.combination.reason is None
    assert site.geometry.lot_type.kind == "interior"
    assert frontages(site) == {NORTH: 100.0}
    assert site.lot_area_sum.value == 9990.0
    assert site.outline.exterior == RINGS[10]
    assert site.outline.shared_lines == ()


def test_two_lots_join_with_the_shared_line_removed():
    site = derive_multi_lot_site(ROW, [bbl(10), bbl(11)], STREETS)
    assert site.combination.status == COMBINATION_OFFERED
    assert (site.combination.same_block, site.combination.touching) == (True, True)
    (shared,) = site.combination.shared_lines
    assert (shared.first_bbl, shared.second_bbl, shared.length_ft) == (bbl(10), bbl(11), 100.0)
    geometry = site.geometry
    assert geometry.status == STATUS_COMPLETE
    assert geometry.lot_type.kind == "interior"
    assert frontages(site) == {NORTH: 200.0}
    assert geometry.lot_area.value == 20000.0
    assert geometry.lot_area.label == LABEL_TAX_MAP
    assert geometry.lot_depth.value == 100.0
    # No combined outline edge lies on the removed lot line x = 100.
    ring = site.outline.exterior
    assert not any(a[0] == b[0] == 100.0 for a, b in zip(ring, ring[1:], strict=False))
    assert "removes the lot line(s) they share (100.00 ft)" in site.outline.statement


def test_all_lots_make_a_corner_lot_with_two_outside_frontages():
    site = derive_multi_lot_site(ROW, None, STREETS)
    assert site.selection_mode == SELECTION_ALL
    assert site.selected_bbls == (bbl(10), bbl(11), bbl(12))
    assert site.geometry.lot_type.kind == "corner"
    assert frontages(site) == {EAST: 100.0, NORTH: 300.0}
    assert site.geometry.lot_area.value == 30000.0
    assert [s.length_ft for s in site.combination.shared_lines] == [100.0, 100.0]


def test_selection_changes_lot_type_frontage_and_area():
    readings = {}
    for picked in ([bbl(12)], [bbl(11), bbl(12)], [bbl(10), bbl(11)], None):
        site = derive_multi_lot_site(ROW, picked, STREETS)
        readings[tuple(picked or ("all",))] = (
            site.geometry.lot_type.kind, frontages(site), site.geometry.lot_area.value,
            site.lot_area_sum.value)
    assert readings == {
        (bbl(12),): ("corner", {EAST: 100.0, NORTH: 100.0}, 10000.0, 10000.0),
        (bbl(11), bbl(12)): ("corner", {EAST: 100.0, NORTH: 200.0}, 20000.0, 20010.0),
        (bbl(10), bbl(11)): ("interior", {NORTH: 200.0}, 20000.0, 20000.0),
        ("all",): ("corner", {EAST: 100.0, NORTH: 300.0}, 30000.0, 30000.0),
    }


def test_front_and_back_lots_make_a_through_lot():
    site = derive_multi_lot_site(choice(site_lot(10), site_lot(20)), None, STREETS)
    assert site.geometry.lot_type.kind == "through"
    assert frontages(site) == {NORTH: 100.0, SOUTH: 100.0}
    assert site.geometry.lot_depth.value == 250.0
    assert site.geometry.lot_area.value == 25000.0


def test_combined_area_is_the_sum_of_recorded_areas_checked_against_the_outline():
    site = derive_multi_lot_site(ROW, None, STREETS)
    assert site.lot_area_sum.value == 30000.0
    assert site.lot_area_sum.label == LABEL_CITY_RECORDS
    assert site.lot_area_sum.basis.startswith("Sum of the recorded lot areas: lot 10 9,990.00")
    check = site.geometry.area_check
    assert (check.outline_sq_ft, check.city_records_sq_ft, check.difference_sq_ft) == (
        30000.0, 30000.0, 0.0)
    assert site.geometry.city_records.lot_area == site.lot_area_sum
    assert site.geometry.city_records.lot_front.label == LABEL_UNKNOWN
    assert "one frontage per tax lot" in site.geometry.city_records.lot_front.reason


def test_recorded_sum_is_unknown_when_a_lot_has_no_recorded_area():
    site = derive_multi_lot_site(choice(site_lot(10, area=9990.0), site_lot(11)), None, STREETS)
    assert site.lot_area_sum.value is None
    assert site.lot_area_sum.reason.startswith("The city records have no lot area for lot 11")
    assert site.geometry.area_check is None
    assert site.geometry.lot_area.value == 20000.0  # the outline still measures


# ------------------------------------------------------------- not offered, with the reason


@pytest.mark.parametrize(("lots", "picked", "reason"), [
    ((10, 11, 12), (10, 12),
     "Lots can be combined only if they touch. Lot 12 does not touch lot 10 (lots 10 and 12 are "
     "100.00 ft apart)."),
    ((10, 21), (10, 21),
     "Lots can be combined only if they touch. Lot 21 does not touch lot 10 (lots 10 and 21 meet "
     "only at a point (shared lot line 0.00 ft, under the 1.00 ft minimum))."),
])
def test_lots_that_do_not_touch_are_not_combined(lots, picked, reason):
    site = derive_multi_lot_site(choice(*(site_lot(n) for n in lots)),
                                 [bbl(n) for n in picked], STREETS)
    assert site.combination.status == COMBINATION_NOT_OFFERED
    assert (site.combination.same_block, site.combination.touching) == (True, False)
    assert site.combination.reason == reason
    assert (site.geometry, site.outline) == (None, None)
    assert reason in site.notes


def test_lots_on_two_blocks_are_not_combined():
    other = site_lot(40, rect(380, 0, 480, 100), block=101)
    site = derive_multi_lot_site(choice(site_lot(12), other), None, STREETS)
    assert site.combination.status == COMBINATION_NOT_OFFERED
    assert site.combination.same_block is False
    assert site.combination.reason == ("Lots can be combined only if they are on one block. "
                                       "The selection is on block 100 (lot 12) and block 101 "
                                       "(lot 40).")


def test_a_lot_without_an_outline_cannot_be_checked_for_touching():
    missing = SiteLot(bbl(11), None, "MapPLUTO has no usable outline for this lot.")
    site = derive_multi_lot_site(choice(site_lot(10), missing), None, STREETS)
    assert site.combination.status == COMBINATION_NOT_OFFERED
    assert site.combination.touching is None
    assert site.combination.reason.endswith(
        "lot 11: MapPLUTO has no usable outline for this lot.")


def test_a_single_lot_without_an_outline_is_refused_not_guessed():
    missing = SiteLot(bbl(11), None, "MapPLUTO has no usable outline for this lot.")
    site = derive_multi_lot_site(choice(missing), None, STREETS)
    assert site.combination.status == COMBINATION_SINGLE_LOT
    assert site.geometry.status == STATUS_REFUSED
    assert site.geometry.lot_area.value is None
    assert site.outline is None


@pytest.mark.parametrize("order", [(10, 20, 21), (10, 21, 20), (21, 10, 20)])
def test_three_lots_where_one_only_touches_through_another_are_combined(order):
    site = derive_multi_lot_site(choice(*(site_lot(n) for n in order)), None, STREETS)
    assert site.combination.status == COMBINATION_OFFERED
    assert {frozenset((s.first_bbl, s.second_bbl)) for s in site.combination.shared_lines} == {
        frozenset((bbl(10), bbl(20))), frozenset((bbl(20), bbl(21)))}
    assert site.geometry.lot_type.kind == "through"
    assert frontages(site) == {NORTH: 100.0, SOUTH: 200.0}
    assert site.geometry.lot_area.value == 40000.0


# ------------------------------------------------------- outline conflicts: nothing measured


def _not_offered_without_geometry(site, reason_start: str) -> None:
    """Touching lots whose outlines cannot be joined: not offered, with the reason, and no
    outline, geometry or combined area (review #281 N1/N2)."""
    assert site.combination.status == COMBINATION_NOT_OFFERED
    assert (site.combination.same_block, site.combination.touching) == (True, True)
    assert site.combination.reason.startswith(reason_start)
    assert (site.outline, site.geometry) == (None, None)
    assert site.combination.reason in site.notes
    assert site.lot_area_sum.value is None
    assert site.lot_area_sum.reason.endswith(site.combination.reason)
    assert study_lot_selection(site)["combination"] == {
        "status": COMBINATION_NOT_OFFERED, "reason": site.combination.reason}


def test_overlapping_outlines_are_not_joined():
    overlapping = site_lot(11, rect(90, 0, 200, 100), area=11000.0)
    site = derive_multi_lot_site(choice(site_lot(10, area=9990.0), overlapping), None, STREETS)
    _not_offered_without_geometry(
        site,
        "The tax-map outlines of the selected lots overlap (lots 10 and 11 by 1,000.00 sq ft)")


def test_lots_around_an_unselected_lot_are_not_measured_with_a_hole():
    ring = [site_lot(n, rect(x, y, x + 100, y + 100)) for n, (x, y) in enumerate(
        [(0, 0), (100, 0), (200, 0), (0, 100), (200, 100), (0, 200), (100, 200), (200, 200)],
        start=1)]
    site = derive_multi_lot_site(choice(*ring), None, None)
    _not_offered_without_geometry(
        site, "The selected lots enclose 10,000.00 sq ft of land that is not selected.")


@pytest.mark.parametrize("picked", [(10, 12), (10, 21)])
def test_a_selection_that_is_not_offered_has_no_combined_area(picked):
    lots = [site_lot(n, area=10000.0) for n in (10, 11, 12, 21)]
    site = derive_multi_lot_site(choice(*lots), [bbl(n) for n in picked], STREETS)
    assert site.combination.status == COMBINATION_NOT_OFFERED
    assert site.lot_area_sum.value is None
    assert site.lot_area_sum.label == LABEL_UNKNOWN
    assert site.lot_area_sum.reason == ("The lots are not combined, so no combined area is "
                                        "given. " + site.combination.reason)


def test_lines_within_the_tolerance_are_joined_at_their_true_length():
    near = site_lot(11, rect(100.004, 0, 200, 100))
    site = derive_multi_lot_site(choice(site_lot(10), near), None, STREETS)
    assert site.combination.status == COMBINATION_OFFERED
    assert site.combination.shared_lines[0].length_ft == 100.0
    assert site.geometry.lot_type.kind == "interior"
    assert frontages(site) == {NORTH: 200.0}


@pytest.mark.parametrize(("offset", "shown"), [(0.05, "0.050"), (0.011, "0.011")])
def test_a_gap_wider_than_the_tolerance_is_not_closed(offset, shown):
    gap = site_lot(11, rect(100 + offset, 0, 200, 100))
    site = derive_multi_lot_site(choice(site_lot(10), gap), None, STREETS)
    assert site.combination.status == COMBINATION_NOT_OFFERED
    assert f"lots 10 and 11 are {shown} ft apart" in site.combination.reason


# ------------------------------------------- existing buildings and the zoning lot (owner)


def _assumed(lot: int, value: int):
    evidence = ExistingFloorAreaEvidence(assumption=StatedAssumption(
        value, "synthetic stated assumption", "2026-10-01T00:00:00Z"))
    return resolve_existing_zoning_floor_area(bbl(lot), evidence)


def test_existing_buildings_stay_per_lot_and_are_never_added_up():
    first, second = _assumed(10, 4000), _assumed(11, 6000)
    site = derive_multi_lot_site(
        choice(site_lot(10, existing=first), site_lot(11, existing=second), site_lot(12)),
        None, STREETS)
    a, b, c = site.existing_buildings
    assert (a.bbl, a.status, b.bbl, b.status) == (bbl(10), EXISTING_ATTACHED,
                                                  bbl(11), EXISTING_ATTACHED)
    assert a.result is first and b.result is second
    assert (a.result.fact["value"], b.result.fact["value"]) == (4000, 6000)
    assert (c.bbl, c.status, c.result) == (bbl(12), EXISTING_NOT_SUPPLIED, None)
    assert "Check needed" in c.note
    assert "not added up across lots" in " ".join(site.notes)
    # No field of the combined result carries a summed or subtracted floor area.
    assert {f.name for f in fields(MultiLotSite)} == {
        "selection_mode", "selected_bbls", "statement", "lots", "combination", "outline",
        "geometry", "lot_area_sum", "street_widths", "existing_buildings", "zoning_lot",
        "notes", "parameters", "provenance"}


def test_an_existing_building_fact_cannot_move_to_another_lot():
    with pytest.raises(ValueError, match="never moved to another lot"):
        site_lot(11, existing=_assumed(10, 4000))


def test_zoning_lot_is_check_needed_even_when_a_record_names_exactly_the_selection():
    record = {"document_ref": "synthetic zoning lot document", "tax_lots": [bbl(10), bbl(11)],
              "text": "ZONING LOT OF LOTS 10 AND 11", "query_ref": "test-fixture-synthetic",
              "retrieved_at": "2026-10-01T00:00:00Z"}
    both = derive_multi_lot_site(ROW, [bbl(10), bbl(11)], STREETS,
                                 recorded_zoning_lot_documents=[record])
    assert (both.zoning_lot.status, both.zoning_lot.label, both.zoning_lot.verified) == (
        ZONING_LOT_CHECK_NEEDED, "Check needed", False)
    assert both.zoning_lot.statement == SELECTION_STATEMENT == both.statement
    assert both.zoning_lot.named_lots_not_selected == ()
    one = derive_multi_lot_site(ROW, [bbl(10)], STREETS, recorded_zoning_lot_documents=[record])
    assert one.zoning_lot.status == ZONING_LOT_CHECK_NEEDED
    assert one.zoning_lot.named_lots_not_selected == (bbl(11),)
    assert (f"They are filed on tax lot {bbl(11)}, which you did not select."
            in one.zoning_lot.reason)
    with pytest.raises(ValueError, match="zoning-lot record needs"):
        derive_multi_lot_site(ROW, None, STREETS, recorded_zoning_lot_documents=[{"text": "x"}])


JOB_421803891_TEXT = (
    "ALTERATION -1 APPLICATION TO BE FILED UNDER TAX LOT #1 TO REFLECT ONE (1) ZONING LOT AND "
    "(2) TAX LOTS (LOT #1 &amp; #70). NO WORK TO BE DONE UNDER THIS APPLICATION. NB "
    "APPLICATION #440608941 HAS BEEN FILED UNDER TAX LOT #70.")


@pytest.mark.parametrize("text", [
    JOB_421803891_TEXT,                                                    # recorded phrasing
    "ZONING LOT #2 CONSISTS OF TAX LOTS 5 AND 6",                          # review #281 r2
    "ZONING LOT COMPRISED OF LOT #1; ACCESSORY PARKING LOT #3 ON SITE",    # review #281 r2
    "ZONING LOT INCLUDES LOT #1. ADJACENT LOT #5 OF BLOCK 7335 NOT PART OF ZONING LOT",
    "ZONING LOT: BLOCK 7334 LOTS #1-#5",
    "ZONING LOT MERGER WITH LOTS #12, 13 AND #14",
])
def test_record_text_is_shown_but_never_read_for_lot_numbers(text):
    # A record filed on lot 10 whose text names other lots, rightly or wrongly: only the
    # lot it is filed on can be flagged; the text is carried and the architect checks it.
    record = {"document_ref": "synthetic filing", "tax_lots": [bbl(10)], "text": text,
              "query_ref": "test-fixture-synthetic", "retrieved_at": "2026-10-01T00:00:00Z"}
    for picked, flagged in (([bbl(11)], (bbl(10),)), ([bbl(10)], ())):
        site = derive_multi_lot_site(ROW, picked, STREETS, recorded_zoning_lot_documents=[record])
        zoning_lot = site.zoning_lot
        assert zoning_lot.named_lots_not_selected == flagged
        assert zoning_lot.recorded_mentions[0]["text"] == text
        assert set(zoning_lot.recorded_mentions[0]) == set(MENTION_KEYS)
        assert zoning_lot.reason.endswith(TEXT_NOT_READ)
        assert (zoning_lot.status, zoning_lot.verified) == (ZONING_LOT_CHECK_NEEDED, False)
        for wrong in ("0002", "0003", "0005", "0012", "0014", "0070"):
            assert f"100100{wrong}" not in zoning_lot.reason


# ------------------------------------------------------------------ selection and the flag


@pytest.mark.parametrize("picked", [[], [bbl(10), bbl(10)], [bbl(13)]])
def test_bad_selections_are_refused(picked):
    with pytest.raises(LotSelectionError):
        derive_multi_lot_site(ROW, picked, STREETS)


def test_an_oversized_selection_is_refused_not_run_unbounded():
    many = choice(*(site_lot(n, rect(n * 10, 0, n * 10 + 10, 100)) for n in range(1, 102)))
    with pytest.raises(LotSelectionError, match="101 lots selected; at most 100"):
        derive_multi_lot_site(many, None, None)


def test_selection_follows_the_lot_choice_order():
    site = derive_multi_lot_site(ROW, [bbl(12), bbl(10), bbl(11)], STREETS)
    assert site.selected_bbls == (bbl(10), bbl(11), bbl(12))
    assert site.selection_mode == SELECTION_ALL


@pytest.mark.parametrize("env", [{}, {"LANE_B_ENABLED": ""}, {"LANE_B_ENABLED": "0"},
                                 {"LANE_B_ENABLED": "false"}, {"LANE_A_ENABLED": "true"}])
def test_the_lane_b_flag_is_off_unless_explicitly_on(env):
    assert multi_lot_site_enabled(env) is False
    assert derive_multi_lot_site_if_enabled(ROW, None, STREETS, env=env) is None


def test_the_lane_b_flag_is_off_in_an_environment_without_it(monkeypatch):
    monkeypatch.delenv("LANE_B_ENABLED", raising=False)
    assert multi_lot_site_enabled() is False
    assert derive_multi_lot_site_if_enabled(ROW, None, STREETS) is None


def test_the_gated_entry_runs_when_the_lane_b_flag_is_on():
    site = derive_multi_lot_site_if_enabled(ROW, None, STREETS, env={"LANE_B_ENABLED": "true"})
    assert site == derive_multi_lot_site(ROW, None, STREETS)
