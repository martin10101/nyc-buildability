"""Property-profile values -> site_fact v1 records (queue item B-02; plan M1-07 "Every
input shows its status and source", section 4 source labels, section 9 "Unknowns stay
unknown ... name what they block").

Offline and deterministic. The official PLUTO captures of task M1-T002 (fixtures F01,
F05, F10) are replayed through the accepted connector and builder. Synthetic variants
are labeled as such and derived in the test. The recorded 215-16 Northern Blvd pack
(PR #254) is not on this branch's base, so it is not used here.
"""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors.pluto_soda import FIELD_UNITS, TransportResponse, fetch_by_bbl
from app.profile.builder import build_property_profile
from app.profile.contract import validate_profile
from app.profile.measurement import answer_measurement, weakest_measurement
from app.profile.site_facts import BLOCKS, PLUTO_DATASET_NAME, build_site_facts
from tests.profile.site_fact_contract import assert_valid_site_fact, load_schema, schema_errors

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
RETRIEVED_AT = "2026-07-16T12:00:00Z"
DIMENSION_KEYS = ("lot_area", "lot_depth", "lot_frontage")
# Street names passed as frontage_streets are test inputs ("TEST STREET A"), never a
# claim about which streets a fixture lot fronts.


def fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def profile_from_body(body: str, bbl: str, **builder_kwargs) -> dict:
    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(200, body)

    result = fetch_by_bbl(
        bbl,
        transport=transport,
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id="b02-test",
        observation_event_id="b02-event",
    )
    return build_property_profile(result, clock=FIXED_CLOCK, **builder_kwargs)


def official_profile(name: str, bbl: str, **builder_kwargs) -> dict:
    return profile_from_body(fixture(name)["response_body_raw"], bbl, **builder_kwargs)


def synthetic_profile(mutate, **builder_kwargs) -> dict:
    """SYNTHETIC variant of the official F01 capture (exercises this module only;
    never presented as official data)."""
    record = json.loads(fixture("F01_single_lot_normal.json")["response_body_raw"])[0]
    mutate(record)
    return profile_from_body(json.dumps([record]), "1000010100", **builder_kwargs)


def only(facts, key: str) -> dict:
    matches = [fact for fact in facts if fact["key"] == key]
    assert len(matches) == 1, (key, matches)
    return matches[0]


def assert_all_valid(site) -> None:
    for fact in site.facts:
        assert_valid_site_fact(fact)
        if fact["measurement"]["rank"] == "unknown":
            assert fact["value"] is None and fact["unit"] is None
            assert fact["blocks"] == list(BLOCKS[fact["key"]])
        else:
            assert fact["blocks"] == []
            assert fact["source"] is not None
        if fact["key"] in DIMENSION_KEYS and fact["value"] is not None:
            assert fact["value"] > 0


def pluto_record(profile: dict, provenance_id: str) -> dict:
    matches = [r for r in profile["provenance"] if r["provenance_id"] == provenance_id]
    assert len(matches) == 1
    return matches[0]


# ---------------------------------------------------------------------------
# Official captures
# ---------------------------------------------------------------------------


def test_f01_known_values_carry_city_records_label_and_their_pluto_source() -> None:
    profile = official_profile("F01_single_lot_normal.json", "1000010100")
    site = build_site_facts(profile)
    assert_all_valid(site)
    assert [fact["key"] for fact in site.facts] == [
        "lot_area",
        "lot_depth",
        "lot_type",
        "zoning_district",
        "existing_zoning_floor_area",
    ]

    for key, column, value, unit in (
        ("lot_area", "lotarea", 23121, "square_feet"),
        ("lot_depth", "lotdepth", 67.01, "feet"),
        ("zoning_district", "zonedist1", "R3-2", None),
    ):
        fact = only(site.facts, key)
        assert (fact["value"], fact["unit"]) == (value, unit)
        assert fact["measurement"] == {"rank": "city_records", "label": "City records"}
        assert fact["lot_bbl"] == "1000010100"
        source = fact["source"]
        assert source["kind"] == "city_dataset"
        assert source["dataset"] == PLUTO_DATASET_NAME == "PLUTO (64uk-42ks)"
        assert source["dataset_version"] == "26v1"
        assert source["retrieved_at"] == RETRIEVED_AT
        assert source["query_ref"] == (
            "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000010100"
        )
        # The source points at the very provenance record the builder emitted, and
        # that record names the PLUTO field and holds the same value.
        (ref,) = source["provenance_refs"]
        record = pluto_record(profile, ref)
        assert record["original_field_name"] == column
        assert record["normalized_value"] == value
        assert column in fact["note"]


def test_f01_lot_type_stays_unknown_with_the_checked_pluto_record() -> None:
    site = build_site_facts(official_profile("F01_single_lot_normal.json", "1000010100"))
    lot_type = only(site.facts, "lot_type")
    assert lot_type["value"] is None
    assert lot_type["measurement"]["label"] == "Unknown — enter"
    assert lot_type["blocks"] == ["permitted_envelope", "building_option"]
    assert lot_type["source"]["provenance_refs"] == ["pluto-64uk-42ks-26v1-1000010100-lottype"]
    assert "LotType code 0" in lot_type["note"]


def test_existing_zoning_floor_area_is_never_taken_from_pluto_building_area() -> None:
    site = build_site_facts(official_profile("F01_single_lot_normal.json", "1000010100"))
    existing = only(site.facts, "existing_zoning_floor_area")
    assert existing["value"] is None
    assert existing["source"] is None
    assert existing["blocks"] == ["remaining_floor_area", "existing_building_paths"]
    assert "certificate of occupancy" in existing["note"]

    # PLUTO BldgArea (10,000 sq ft in F01) is only a reference value, never a site fact.
    reference = {ref["key"]: ref for ref in site.references}["recorded_building_area"]
    assert (reference["value"], reference["unit"]) == (10000, "square_feet")
    assert reference["use"] == "reference_only"
    assert reference["source"]["provenance_refs"] == [
        "pluto-64uk-42ks-26v1-1000010100-bldgarea"
    ]
    assert all(fact["value"] != 10000 for fact in site.facts)


def test_f01_frontage_is_a_reference_and_unknown_per_named_street() -> None:
    profile = official_profile("F01_single_lot_normal.json", "1000010100")
    assert build_site_facts(profile).of_key("lot_frontage") == ()

    site = build_site_facts(profile, frontage_streets=("TEST STREET A",))
    assert_all_valid(site)
    frontage = only(site.facts, "lot_frontage")
    assert frontage["street"] == "TEST STREET A"
    assert frontage["value"] is None
    assert frontage["blocks"] == ["permitted_envelope", "building_option", "geometry"]
    assert "297.49 ft" in frontage["note"]
    reference = {ref["key"]: ref for ref in site.references}["recorded_lot_frontage"]
    assert (reference["value"], reference["unit"]) == (297.49, "feet")


def test_f05_zero_dimensions_are_unknown_never_zero() -> None:
    # Official capture: PLUTO records lotfront "0.0000000" and lotdepth "0.0000000".
    profile = official_profile("F05_split_zone_lot.json", "1000010010")
    site = build_site_facts(profile, frontage_streets=("TEST STREET A",))
    assert_all_valid(site)
    depth = only(site.facts, "lot_depth")
    assert depth["value"] is None and depth["unit"] is None
    assert depth["measurement"]["rank"] == "unknown"
    assert depth["blocks"] == ["permitted_envelope", "building_option", "geometry"]
    assert "never 0" in depth["note"]
    # The checked PLUTO record stays named even though its value is unusable.
    assert depth["source"]["provenance_refs"] == ["pluto-64uk-42ks-26v1-1000010010-lotdepth"]
    assert "recorded_lot_frontage" not in {ref["key"] for ref in site.references}
    assert "No usable city-recorded frontage" in only(site.facts, "lot_frontage")["note"]
    assert all(fact["value"] != 0 for fact in site.facts)


def test_f05_and_f10_split_lots_carry_one_fact_per_district() -> None:
    f05 = build_site_facts(official_profile("F05_split_zone_lot.json", "1000010010"))
    assert [f["value"] for f in f05.of_key("zoning_district")] == ["R3-2", "C4-1"]
    f10 = build_site_facts(official_profile("F10_marble_hill.json", "1022150001"))
    assert_all_valid(f10)
    districts = f10.of_key("zoning_district")
    assert [f["value"] for f in districts] == ["M1-1", "R6", "R7-1"]
    assert [f["fact_id"] for f in districts] == [
        "1022150001:zoning_district:1",
        "1022150001:zoning_district:2",
        "1022150001:zoning_district:3",
    ]
    assert f10.of_key("commercial_overlay") == ()
    # F10 records bldgarea "0": no reference value is shown for it.
    assert "recorded_building_area" not in {ref["key"] for ref in f10.references}


def test_fact_ids_are_unique_and_stable_across_builds() -> None:
    first = build_site_facts(official_profile("F10_marble_hill.json", "1022150001"))
    second = build_site_facts(official_profile("F10_marble_hill.json", "1022150001"))
    ids = [fact["fact_id"] for fact in first.facts]
    assert len(ids) == len(set(ids))
    assert first == second


# ---------------------------------------------------------------------------
# A lot whose values are missing
# ---------------------------------------------------------------------------


def _drop_site_values(record: dict) -> None:
    for column in ("lotarea", "lotfront", "lotdepth", "lottype", "zonedist1", "bldgarea"):
        record.pop(column)


def test_missing_values_stay_unknown_and_say_what_they_block() -> None:
    profile = synthetic_profile(_drop_site_values)
    site = build_site_facts(profile, frontage_streets=("TEST STREET A",))
    assert_all_valid(site)
    assert site.references == ()
    assert {fact["key"] for fact in site.unknown_facts()} == {
        "lot_area",
        "lot_frontage",
        "lot_depth",
        "lot_type",
        "zoning_district",
        "existing_zoning_floor_area",
    }
    for fact in site.facts:
        assert fact["value"] is None and fact["unit"] is None
        assert fact["measurement"] == {"rank": "unknown", "label": "Unknown — enter"}
        assert fact["blocks"] == list(BLOCKS[fact["key"]])

    area = only(site.facts, "lot_area")
    assert area["blocks"] == [
        "floor_area_allowance",
        "remaining_floor_area",
        "permitted_envelope",
        "building_option",
        "unit_estimate",
    ]
    assert area["note"] == "PLUTO has no lotarea value for this lot."
    # The source names the PLUTO request that was checked; no record backs a value.
    assert area["source"]["query_ref"].endswith("?bbl=1000010100")
    assert "provenance_refs" not in area["source"]
    district = only(site.facts, "zoning_district")
    assert "floor_area_allowance" in district["blocks"]
    assert district["fact_id"] == "1000010100:zoning_district:1"

    # A result built on any of these inputs carries no known label.
    assert weakest_measurement(site.facts)["rank"] == "unknown"
    assert answer_measurement([only(site.facts, "lot_area")]) is None


def test_missing_optional_districts_and_overlays_emit_no_fact() -> None:
    site = build_site_facts(official_profile("F01_single_lot_normal.json", "1000010100"))
    assert len(site.of_key("zoning_district")) == 1
    assert site.of_key("commercial_overlay") == ()


# ---------------------------------------------------------------------------
# Unusable values: drift, conflicts, identity
# ---------------------------------------------------------------------------


def test_drift_flagged_value_is_unknown() -> None:
    profile = synthetic_profile(lambda record: record.update(lotarea="NaN"))
    assert "non_finite_number_value:lotarea" in profile["reproducibility"]["drift_signals"]
    area = only(build_site_facts(profile).facts, "lot_area")
    assert_valid_site_fact(area)
    assert area["value"] is None
    assert "drift" in area["note"]


def test_conflicting_district_is_unknown_and_the_conflict_stays_visible() -> None:
    conflict = {  # SYNTHETIC cross-source conflict in the builder's conflict shape
        "field": "zonedist1",
        "values": [
            {"source_id": "nyc-dcp-pluto-soda", "value": "R3-2", "derivation": "PLUTO"},
            {"source_id": "test-synthetic-ztldb", "value": "R4", "derivation": "ZTLDB"},
        ],
        "resolution": "unresolved",
        "reason": "synthetic",
    }
    profile = synthetic_profile(lambda record: None, additional_conflicts=[conflict])
    district = only(build_site_facts(profile).facts, "zoning_district")
    assert_valid_site_fact(district)
    assert district["value"] is None
    assert "'R3-2'" in district["note"] and "'R4'" in district["note"]
    assert "unresolved" in district["note"]
    assert district["blocks"] == list(BLOCKS["zoning_district"])


def test_identity_conflict_makes_every_value_unknown() -> None:
    # SYNTHETIC: the record's borocode disagrees with its BBL.
    profile = synthetic_profile(lambda record: record.update(borocode="2"))
    assert profile["status_dimensions"]["analysis_readiness"] == "blocked_data_conflict"
    site = build_site_facts(profile)
    assert_all_valid(site)
    assert site.unknown_facts() == site.facts
    assert site.references == ()
    assert "identity" in only(site.facts, "lot_area")["note"]


def test_present_overlay_is_a_city_records_fact() -> None:
    profile = synthetic_profile(lambda record: record.update(overlay1="C2-2"))
    overlay = only(build_site_facts(profile).facts, "commercial_overlay")
    assert_valid_site_fact(overlay)
    assert (overlay["value"], overlay["unit"]) == ("C2-2", None)
    assert overlay["measurement"]["rank"] == "city_records"
    assert overlay["fact_id"] == "1000010100:commercial_overlay:1"


def test_undocumented_unit_is_not_used() -> None:
    profile = official_profile("F01_single_lot_normal.json", "1000010100")
    for record in profile["provenance"]:
        if record["original_field_name"] == "lotarea":
            record["units"] = "acres"  # SYNTHETIC defect
    area = only(build_site_facts(profile).facts, "lot_area")
    assert area["value"] is None
    assert "not the documented unit" in area["note"]


# ---------------------------------------------------------------------------
# Weakest label over real facts; no change to the profile
# ---------------------------------------------------------------------------


def test_result_over_city_records_inputs_carries_city_records() -> None:
    site = build_site_facts(official_profile("F01_single_lot_normal.json", "1000010100"))
    inputs = [only(site.facts, "lot_area"), only(site.facts, "zoning_district")]
    assert answer_measurement(inputs) == {"rank": "city_records", "label": "City records"}
    assert answer_measurement([*inputs, only(site.facts, "lot_type")]) is None


def test_profile_is_read_only_and_still_valid() -> None:
    profile = official_profile("F10_marble_hill.json", "1022150001")
    before = copy.deepcopy(profile)
    site = build_site_facts(profile, frontage_streets=("TEST STREET A", "TEST STREET B"))
    assert profile == before
    validate_profile(profile)
    # Facts are independent copies: changing one never reaches the profile.
    site.facts[0]["source"]["provenance_refs"].append("x")
    assert profile == before


def test_contract_check_is_not_vacuous() -> None:
    site = build_site_facts(synthetic_profile(_drop_site_values))
    unknown_area = only(site.facts, "lot_area")
    assert not schema_errors(unknown_area)
    # An unknown disguised as 0, or an unknown that names nothing it blocks, fails.
    assert schema_errors({**unknown_area, "value": 0, "unit": "square_feet"})
    assert schema_errors({**unknown_area, "blocks": []})
    known = only(
        build_site_facts(official_profile("F01_single_lot_normal.json", "1000010100")).facts,
        "lot_area",
    )
    assert schema_errors({**known, "source": None})


def test_units_match_the_connector_units() -> None:
    assert FIELD_UNITS["lotarea"] == FIELD_UNITS["bldgarea"] == "square feet"
    assert FIELD_UNITS["lotfront"] == FIELD_UNITS["lotdepth"] == "feet"


def test_blocks_use_only_the_contract_vocabulary() -> None:
    schema = load_schema("site_fact.schema.json")
    vocabulary = set(schema["$defs"]["blocked_output"]["enum"])
    keys = set(schema["properties"]["key"]["enum"])
    for key, blocked in BLOCKS.items():
        assert key in keys
        assert blocked and set(blocked) <= vocabulary
        assert len(set(blocked)) == len(blocked)


@pytest.mark.parametrize(
    "profile, streets",
    [
        ({}, ()),
        ({"identity": {}}, ()),
        ("not a profile", ()),
        ({"identity": {"bbl": "1000010100"}}, ("",)),
        ({"identity": {"bbl": "1000010100"}}, ("A ST", "A ST")),
        ({"identity": {"bbl": "1000010100"}}, "A ST"),
    ],
)
def test_bad_arguments_fail_loudly(profile, streets) -> None:
    with pytest.raises(ValueError):
        build_site_facts(profile, frontage_streets=streets)
