"""§8a map-based-rules hidden-issue flags (queue item B-09, slice 3; plan L-11).

Offline and deterministic: the recorded 215-16 Northern Blvd pack (queue item B-01) is
replayed through the accepted PLUTO connector and builder; synthetic variants (a mutated
PLUTO row or a minimal synthetic profile) are labeled as such and derived in the test. No
live call is made. Every claim in the module docstrings and docs/lanes/status/B.md is
checked here.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors.pluto_soda import SOURCE_ID as PLUTO_SOURCE_ID
from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl
from app.profile.builder import build_property_profile
from app.profile.hidden_issue_flags import (
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    STATUS_NOT_FLAGGED,
    FlagGroup,
    HiddenIssueFlag,
    map_based_rules_group,
)
from app.profile.hidden_issue_flags.map_based_rules import GROUP_ID, GROUP_TITLE
from app.profile.transit_parking import resolve_transit_parking_status
from tests.spatial._northern_replay import BBL, replay_pluto

_CLOCK = lambda: datetime(2026, 9, 30, 6, 20, tzinfo=UTC)  # noqa: E731
PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
PLUTO_FILE = "pluto_64uk-42ks_bbl_4073340070.json"

# The nine §8a map-based items, in plan order.
EXPECTED_ITEMS = (
    "map_based_rules.special_districts_and_overlays",
    "map_based_rules.inclusionary_housing",
    "map_based_rules.split_by_district_line",
    "map_based_rules.near_district_line",
    "map_based_rules.flood",
    "map_based_rules.waterfront_coastal",
    "map_based_rules.transit_easements",
    "map_based_rules.airport_height",
    "map_based_rules.landmarks_historic",
)


def benchmark_profile() -> dict:
    """The recorded 215-16 Northern Blvd lot, through the real connector and builder."""
    return build_property_profile(replay_pluto(), clock=_CLOCK)


def benchmark_record() -> dict:
    return json.loads((PACK / PLUTO_FILE).read_text("utf-8"))[0]


def profile_from_record(record: dict) -> dict:
    """A profile from one PLUTO record served offline (SYNTHETIC when the record was
    mutated; never presented as official data), through the real connector and builder."""
    body = json.dumps([record])

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(200, body)

    result = fetch_by_bbl(
        BBL, transport=transport, sleep=lambda _s: None, clock=_CLOCK,
        correlation_id="b09s3-test", observation_event_id="b09s3-test",
    )
    return build_property_profile(result, clock=_CLOCK)


def by_id(group: FlagGroup) -> dict[str, HiddenIssueFlag]:
    return {flag.item_id: flag for flag in group.flags}


# ---------------------------------------------------------------------------
# Shape and order
# ---------------------------------------------------------------------------


def test_group_identity_and_nine_items_in_plan_order() -> None:
    group = map_based_rules_group(BBL, profile=benchmark_profile())
    assert isinstance(group, FlagGroup)
    assert group.group_id == GROUP_ID == "map_based_rules"
    assert group.title == GROUP_TITLE == "Map-based rules"
    assert group.lot_bbl == BBL == "4073340070"
    assert tuple(f.item_id for f in group.flags) == EXPECTED_ITEMS
    assert all(f.group == GROUP_ID for f in group.flags)
    assert all(f.phase == "1" for f in group.flags)
    # Every item is one of the three §8a kinds (opportunity never applies to this group).
    assert {f.status for f in group.flags} <= {
        STATUS_FLAG, STATUS_CHECK_NEEDED, STATUS_NOT_FLAGGED}


def test_to_dict_round_trips_and_is_deterministic() -> None:
    first = map_based_rules_group(BBL, profile=benchmark_profile()).to_dict()
    second = map_based_rules_group(BBL, profile=benchmark_profile()).to_dict()
    assert first == second
    assert [f["item_id"] for f in first["flags"]] == list(EXPECTED_ITEMS)


# ---------------------------------------------------------------------------
# Recorded benchmark 215-16 Northern Blvd lot 70
# ---------------------------------------------------------------------------


def test_benchmark_statuses_match_the_recorded_pluto_row() -> None:
    flags = by_id(map_based_rules_group(BBL, profile=benchmark_profile()))
    # overlay1 C2-2 is recorded -> flag; splitzone recorded false -> No flag; everything
    # else has no recorded value / no connected source -> Check needed.
    assert flags["map_based_rules.special_districts_and_overlays"].status == STATUS_FLAG
    assert flags["map_based_rules.split_by_district_line"].status == STATUS_NOT_FLAGGED
    for item in (
        "inclusionary_housing", "near_district_line", "flood", "waterfront_coastal",
        "transit_easements", "airport_height", "landmarks_historic",
    ):
        assert flags[f"map_based_rules.{item}"].status == STATUS_CHECK_NEEDED, item


def test_benchmark_overlay_flag_names_the_overlay_and_carries_its_pluto_source() -> None:
    flag = by_id(map_based_rules_group(BBL, profile=benchmark_profile()))[
        "map_based_rules.special_districts_and_overlays"]
    assert flag.status == STATUS_FLAG
    assert "C2-2" in flag.detail
    assert "overlay1" in flag.detail
    # Names that a rule check is needed and never decides what the overlay requires.
    assert "rule check" in flag.detail
    assert flag.status_label == "Flag"
    # The evidence carries the PLUTO source so B-06 can pin it ("Out of date" / version).
    assert len(flag.evidence) == 1
    source = flag.evidence[0]["source"]
    assert source["kind"] == "city_dataset"
    assert source["dataset_version"] == "26v2"
    assert source["provenance_refs"] == [
        "pluto-64uk-42ks-26v2-4073340070-overlay1"]


def test_benchmark_split_zone_is_a_recorded_no_flag_distinct_from_near_boundary() -> None:
    flags = by_id(map_based_rules_group(BBL, profile=benchmark_profile()))
    split = flags["map_based_rules.split_by_district_line"]
    assert split.status == STATUS_NOT_FLAGGED
    assert split.status_label == "No flag"
    assert "splitzone false" in split.detail
    assert len(split.evidence) == 1  # the recorded splitzone value, with its source
    # splitzone false does NOT clear "within 20 ft of a district line": that stays a check
    # (the benchmark lot is near-boundary-uncertain per the B-01 substrate, README).
    near = flags["map_based_rules.near_district_line"]
    assert near.status == STATUS_CHECK_NEEDED
    assert "not lot-precise" in near.detail


def test_benchmark_check_needed_items_name_their_missing_source() -> None:
    flags = by_id(map_based_rules_group(BBL, profile=benchmark_profile()))
    assert "Inclusionary Housing" in flags["map_based_rules.inclusionary_housing"].detail
    assert "FEMA" in flags["map_based_rules.flood"].detail
    assert "Coastal" in flags["map_based_rules.waterfront_coastal"].detail
    assert "transit easement" in flags["map_based_rules.transit_easements"].detail.lower()
    assert "FAA" in flags["map_based_rules.airport_height"].detail
    assert "LPC" in flags["map_based_rules.landmarks_historic"].detail
    # Absent categorical columns are "none OR unknown", never a silent clear (D-051).
    assert "none OR unknown" in flags["map_based_rules.landmarks_historic"].detail
    for flag in flags.values():
        if flag.status == STATUS_CHECK_NEEDED:
            assert flag.needs_check is True
            assert flag.status_label == "Check needed"


# ---------------------------------------------------------------------------
# A present recorded PLUTO value flags (synthetic mutated rows, labeled)
# ---------------------------------------------------------------------------


def test_present_special_district_flags_and_names_it() -> None:
    record = benchmark_record()
    record["spdist1"] = "EC-5"  # SYNTHETIC: a special district recorded on the row
    flag = by_id(map_based_rules_group(BBL, profile=profile_from_record(record)))[
        "map_based_rules.special_districts_and_overlays"]
    assert flag.status == STATUS_FLAG
    assert "EC-5" in flag.detail
    assert "spdist1" in flag.detail


def test_present_mih_option_flag_flags_inclusionary_housing() -> None:
    record = benchmark_record()
    record["mih_opt1"] = True  # SYNTHETIC: a Mandatory Inclusionary Housing option flag
    flag = by_id(map_based_rules_group(BBL, profile=profile_from_record(record)))[
        "map_based_rules.inclusionary_housing"]
    assert flag.status == STATUS_FLAG
    assert "mih_opt1" in flag.detail
    assert "rule check" in flag.detail  # never decides what MIH requires
    assert len(flag.evidence) == 1


def test_split_zone_true_flags() -> None:
    record = benchmark_record()
    record["splitzone"] = True  # SYNTHETIC: a split lot
    flag = by_id(map_based_rules_group(BBL, profile=profile_from_record(record)))[
        "map_based_rules.split_by_district_line"]
    assert flag.status == STATUS_FLAG
    assert "splitzone true" in flag.detail


def test_present_flood_flag_flags_but_defers_the_zone_letter_and_rule() -> None:
    record = benchmark_record()
    record["pfirm15_flag"] = 1  # SYNTHETIC: lot in the Preliminary FIRM floodplain
    flag = by_id(map_based_rules_group(BBL, profile=profile_from_record(record)))[
        "map_based_rules.flood"]
    assert flag.status == STATUS_FLAG
    assert "pfirm15_flag" in flag.detail
    assert "FEMA" in flag.detail  # the zone letter still comes from FEMA
    assert "Appendix G" in flag.detail  # the resilience rule is a rule check, not decided


def test_present_landmark_and_historic_district_flag_without_deciding_lpc() -> None:
    record = benchmark_record()
    record["landmark"] = "Individual Landmark"  # SYNTHETIC
    record["histdist"] = "Douglaston Historic District"  # SYNTHETIC
    flag = by_id(map_based_rules_group(BBL, profile=profile_from_record(record)))[
        "map_based_rules.landmarks_historic"]
    assert flag.status == STATUS_FLAG
    assert "Individual Landmark" in flag.detail
    assert "Douglaston Historic District" in flag.detail
    assert "rule check" in flag.detail
    assert len(flag.evidence) == 2


# ---------------------------------------------------------------------------
# Untrusted recorded value: never surfaced (same trust rules as the site facts)
# ---------------------------------------------------------------------------


def test_untrusted_overlay_value_is_check_needed_never_surfaced() -> None:
    # SYNTHETIC minimal profile: PLUTO returns an overlay but flags a conflict on it.
    profile = {
        "identity": {"bbl": BBL},
        "provenance": [
            {
                "source_id": PLUTO_SOURCE_ID,
                "bbl": BBL,
                "original_field_name": "overlay1",
                "normalized_value": "C2-2",
                "conflict_status": "conflicting",
                "dataset_version": "26v2",
                "retrieved_at": "2026-09-30T06:20:00Z",
                "request_url": (
                    "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=" + BBL),
                "provenance_id": "pluto-64uk-42ks-26v2-" + BBL + "-overlay1",
            }
        ],
    }
    flag = by_id(map_based_rules_group(BBL, profile=profile))[
        "map_based_rules.special_districts_and_overlays"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "C2-2" not in flag.detail  # the conflicting value is never surfaced as a fact
    assert "conflict" in flag.detail.lower()


# ---------------------------------------------------------------------------
# No profile: the PLUTO-backed items cannot be read
# ---------------------------------------------------------------------------


def test_without_a_profile_every_item_is_check_needed() -> None:
    group = map_based_rules_group(BBL)
    assert tuple(f.item_id for f in group.flags) == EXPECTED_ITEMS
    assert all(f.status == STATUS_CHECK_NEEDED for f in group.flags)
    assert "No property profile" in by_id(group)[
        "map_based_rules.split_by_district_line"].detail


# ---------------------------------------------------------------------------
# Opt-in B-10 transit/parking zone (pending owner question b): off by default
# ---------------------------------------------------------------------------


def test_transit_parking_zone_is_absent_by_default() -> None:
    group = map_based_rules_group(BBL, profile=benchmark_profile())
    assert "map_based_rules.transit_parking_zone" not in by_id(group)
    assert len(group.flags) == 9


def test_transit_parking_zone_is_an_opt_in_tenth_flag_when_supplied() -> None:
    profile = benchmark_profile()
    status = resolve_transit_parking_status(profile)
    group = map_based_rules_group(BBL, profile=profile, transit_parking=status)
    assert len(group.flags) == 10
    extra = group.flags[-1]
    assert extra.item_id == "map_based_rules.transit_parking_zone"
    assert extra.status == STATUS_FLAG
    assert "Outer Transit Zone" in extra.detail
    assert "check C-8" in extra.detail
    assert "space" not in extra.detail.lower()  # never a parking count
    assert "transit easements near stations" not in extra.detail.lower()  # a different layer


def test_transit_parking_zone_check_needed_carries_through_from_b10() -> None:
    record = benchmark_record()
    record.pop("transitzone")  # SYNTHETIC: null omitted by SODA
    profile = profile_from_record(record)
    status = resolve_transit_parking_status(profile)
    group = map_based_rules_group(BBL, profile=profile, transit_parking=status)
    extra = by_id(group)["map_based_rules.transit_parking_zone"]
    assert extra.status == STATUS_CHECK_NEEDED
    assert "6ztr-wgff" in extra.detail  # B-10's missing source


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_invalid_bbl_raises() -> None:
    with pytest.raises(ValueError):
        map_based_rules_group("not-a-bbl")
    with pytest.raises(ValueError):
        map_based_rules_group("0073340070")  # borough 0 is invalid


def test_profile_for_a_different_lot_raises() -> None:
    with pytest.raises(ValueError):
        map_based_rules_group("4073340071", profile=benchmark_profile())


def test_wrong_transit_parking_type_raises() -> None:
    with pytest.raises(ValueError):
        map_based_rules_group(BBL, transit_parking={"status": "recorded"})  # type: ignore[arg-type]
