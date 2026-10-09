"""The recorded city-record columns as three-state facts (task M5-T130, scenario S2; O14).

Expected OUTCOMES come from the orchestrator's reading O14 (quoted beside each test) and the
work order's sentences (gaps K10, K18, K19), never from the module under test. The property
profiles are hand-built to the shape the shared reader reads, one per column state, so each of
the states O14 names is pinned by a test of its own.

O14, in the orchestrator's words carried in result_way_facts: a column the served PLUTO row
omitted, where a fetch is recorded, is "recorded as absent" (the city's records list none,
never "the lot has none"); no fetch, a failed fetch, no row, or a value that cannot be trusted
is "not read"; a column that was not read is never taken as "none" (work order K10).
"""

from __future__ import annotations

import pytest

from app.profile.site_facts import PLUTO_SOURCE_ID
from app.scenario.three_answers.result_way_facts import (
    DATASET_LABEL,
    gather_recorded_facts,
)
from app.scenario.three_answers.result_way_inputs import Recorded

_BBL = "4073340070"
_RETRIEVED = "2026-09-30T06:20:00Z"
_QUERY = "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=4073340070"


def _profile(columns: dict, *, fetched: bool = True, drift: tuple[str, ...] = ()) -> dict:
    """A built-profile-shaped document (identity + PLUTO provenance + reproducibility). A column
    in ``columns`` is a served value; a column left out is a served-empty column (omitted by the
    SODA null-omission rule). ``fetched=False`` makes the reproducibility name no PLUTO fetch, so
    a served-empty column is "not read", not "recorded as absent". ``drift`` marks a column as a
    connector-drift signal (a served-but-untrusted value)."""
    provenance = [
        {
            "source_id": PLUTO_SOURCE_ID, "bbl": _BBL, "original_field_name": column,
            "normalized_value": value, "dataset_version": "26v2",
            "retrieved_at": _RETRIEVED, "request_url": _QUERY,
            "provenance_id": f"pluto-{column}", "conflict_status": "none",
        }
        for column, value in columns.items()
    ]
    reproducibility = {
        "source_id": PLUTO_SOURCE_ID if fetched else "some-other-source",
        "dataset_version": "26v2", "retrieved_at": _RETRIEVED, "request_url": _QUERY,
        "drift_signals": list(drift),
    }
    return {"identity": {"bbl": _BBL}, "provenance": provenance, "reproducibility": reproducibility}


def _state(profile, name: str) -> Recorded:
    return getattr(gather_recorded_facts(profile), name).state


# --------------------------------------------------------------------------- served empty = absent
def test_every_column_served_empty_after_a_fetch_is_recorded_as_absent():
    """O14: a column the served row omitted, where a fetch is recorded, is 'recorded as absent'
    (work order K10: 'None recorded: stated as "city records list no special purpose district"';
    K18: 'Recorded "not split": stated as a fact')."""
    facts = gather_recorded_facts(_profile({}))
    for fact in facts.facts():
        assert fact.state is Recorded.ABSENT, fact.name
        # the wording is about the city's records, never "the lot has none"
        assert "city records" in fact.statement.lower()
        assert "the lot has no" not in fact.statement.lower()


def test_split_zone_false_is_recorded_as_absent_a_real_not_split():
    """splitzone is served explicitly as true/false, so a served false is a real recorded
    'not split' (work order K18)."""
    assert _state(_profile({"splitzone": False}), "split_by_district_line") is Recorded.ABSENT
    assert _state(_profile({"splitzone": True}), "split_by_district_line") is Recorded.PRESENT


# --------------------------------------------------------------------------- not read != none
def test_no_profile_is_not_read_for_every_column():
    """O14: no fetch record -> 'not read'; a column that was not read is never taken as 'none'
    (work order K10)."""
    facts = gather_recorded_facts(None)
    for fact in facts.facts():
        assert fact.state is Recorded.NOT_READ, fact.name
        assert fact.dataset is None and fact.retrieved_at is None


def test_served_empty_without_a_recorded_fetch_is_not_read():
    """O14: the same omitted column, but with NO PLUTO fetch recorded, is 'not read', not
    'recorded as absent' - the distinction is the connector's own record of the fetch."""
    assert _state(_profile({}, fetched=False), "special_purpose_district") is Recorded.NOT_READ


def test_a_served_but_untrusted_value_is_not_read_never_guessed():
    """A value that cannot be trusted (a connector drift signal) is never guessed at, so the
    condition is 'not read', not 'recorded as absent' and not 'present'."""
    profile = _profile({"splitzone": "maybe"}, drift=("unexpected_checkbox_value:splitzone",))
    fact = gather_recorded_facts(profile).split_by_district_line
    assert fact.state is Recorded.NOT_READ
    assert fact.unusable_reason  # the plain reason the value could not be used is carried


# --------------------------------------------------------------------------- present + code
def test_recorded_values_are_present_and_the_overlay_code_is_carried():
    facts = gather_recorded_facts(_profile({
        "spdist1": "MX-1", "overlay1": "C2-2", "splitzone": True,
        "mih_opt1": True, "firm07_flag": 1, "landmark": "An Individual Landmark",
    }))
    assert facts.special_purpose_district.state is Recorded.PRESENT
    assert facts.commercial_overlay.state is Recorded.PRESENT
    assert facts.commercial_overlay.code == "C2-2"  # the overlay's code is carried
    assert facts.split_by_district_line.state is Recorded.PRESENT
    assert facts.inclusionary_housing_area.state is Recorded.PRESENT
    assert facts.flood_zone.state is Recorded.PRESENT
    assert facts.landmark_or_historic.state is Recorded.PRESENT


def test_a_falsy_flag_is_absent_not_present():
    """A checkbox false (mih_opt) or a numeric zero (firm flag) is not the condition being
    present; it is a recorded absence."""
    facts = gather_recorded_facts(_profile({
        "mih_opt1": False, "mih_opt2": False, "mih_opt3": False, "mih_opt4": False,
        "firm07_flag": 0, "pfirm15_flag": 0,
    }))
    assert facts.inclusionary_housing_area.state is Recorded.ABSENT
    assert facts.flood_zone.state is Recorded.ABSENT


def test_present_in_one_column_wins_over_absent_in_the_others():
    """Any one special-district column with a value makes the condition present."""
    facts = gather_recorded_facts(_profile({"spdist3": "EC-5"}))
    assert facts.special_purpose_district.state is Recorded.PRESENT


def test_one_untrusted_column_with_no_present_column_is_not_read():
    """If a special-district column is served but untrusted and none is present, the condition
    cannot be established, so it is 'not read' (never guessed)."""
    profile = _profile({"spdist1": "MX-1"}, drift=("connector_drift:spdist1",))
    # spdist1 is drift-flagged (unusable); spdist2/spdist3 served empty.
    assert gather_recorded_facts(profile).special_purpose_district.state is Recorded.NOT_READ


# --------------------------------------------------------------------------- provenance
def test_each_fact_carries_its_dataset_columns_lot_id_and_fetch_record():
    facts = gather_recorded_facts(_profile({}))
    sp = facts.special_purpose_district
    assert sp.columns == ("spdist1", "spdist2", "spdist3")
    assert sp.bbl == _BBL
    assert sp.dataset == DATASET_LABEL and sp.dataset_id == "64uk-42ks"
    assert sp.retrieved_at == _RETRIEVED and sp.query_ref == _QUERY
    assert facts.commercial_overlay.columns == ("overlay1", "overlay2")
    assert facts.flood_zone.columns == ("firm07_flag", "pfirm15_flag")


@pytest.mark.parametrize("state_profile,expected", [
    ({}, Recorded.ABSENT),
    ({"overlay1": "C2-2"}, Recorded.PRESENT),
])
def test_overlay_state_table(state_profile, expected):
    assert _state(_profile(state_profile), "commercial_overlay") is expected
