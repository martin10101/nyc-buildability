"""One transit/parking-zone source applied identically to every option (queue item B-10;
plan check C-8).

Offline and deterministic: the recorded 215-16 Northern Blvd pack (queue item B-01) is
replayed through the accepted PLUTO connector and builder; synthetic variants are labeled
as such and derived in the test. No live call is made.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl
from app.profile.builder import build_property_profile
from app.profile.data_versions import (
    STATUS_CURRENT,
    assess_source,
    pin_from_site_fact_source,
    published_from_pins,
)
from app.profile.site_facts import PLUTO_DATASET_NAME
from app.profile.transit_parking import (
    MISSING_PARKING_ZONE_SOURCE,
    STATUS_CHECK_NEEDED,
    STATUS_RECORDED,
    TRANSIT_ZONE_FIELD,
    applied_to_options,
    resolve_transit_parking_status,
)
from tests.spatial._northern_replay import BBL, replay_pluto

_CLOCK = lambda: datetime(2026, 9, 30, 6, 20, tzinfo=UTC)  # noqa: E731
PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
PLUTO_FILE = "pluto_64uk-42ks_bbl_4073340070.json"
RETRIEVED_AT = "2026-09-30T06:20:00Z"


def benchmark_profile() -> dict:
    """The recorded 215-16 Northern Blvd lot, through the real connector and builder."""
    return build_property_profile(replay_pluto(), clock=_CLOCK)


def benchmark_record() -> dict:
    return json.loads((PACK / PLUTO_FILE).read_text("utf-8"))[0]


def profile_from_record(record: dict) -> dict:
    """A profile built from one PLUTO record served offline (SYNTHETIC when the record
    was mutated; never presented as official data)."""
    body = json.dumps([record])

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(200, body)

    result = fetch_by_bbl(
        BBL,
        transport=transport,
        sleep=lambda _s: None,
        clock=_CLOCK,
        correlation_id="b10-test",
        observation_event_id="b10-test",
    )
    return build_property_profile(result, clock=_CLOCK)


# ---------------------------------------------------------------------------
# Recorded benchmark: one sourced value
# ---------------------------------------------------------------------------


def test_benchmark_215_16_northern_records_outer_transit_zone_with_its_source() -> None:
    status = resolve_transit_parking_status(benchmark_profile())
    assert status.lot_bbl == BBL == "4073340070"
    assert status.status == STATUS_RECORDED
    assert status.transit_zone == "Outer Transit Zone"
    assert status.needs_check is False
    assert status.missing_source is None

    source = status.source
    assert source is not None
    assert source["kind"] == "city_dataset"
    assert source["dataset"] == PLUTO_DATASET_NAME == "PLUTO (64uk-42ks)"
    assert source["dataset_version"] == "26v2"
    assert source["retrieved_at"] == RETRIEVED_AT
    assert source["query_ref"].endswith("64uk-42ks.json?bbl=4073340070")
    assert source["provenance_refs"] == ["pluto-64uk-42ks-26v2-4073340070-transitzone"]


def test_recorded_detail_states_the_value_and_the_legal_boundary_not_a_parking_count() -> None:
    status = resolve_transit_parking_status(benchmark_profile())
    detail = status.detail
    assert "Outer Transit Zone" in detail
    assert TRANSIT_ZONE_FIELD in detail
    assert "check C-8" in detail
    # The parking consequence is never decided here (platform principle 1).
    assert "not decided here" in detail
    assert "G6" in detail
    # It never claims a number of spaces or an exemption.
    assert "space" not in detail.lower()
    assert "exempt" not in detail.lower()


def test_status_source_is_pinnable_by_b06_and_current_against_its_own_retrieval() -> None:
    status = resolve_transit_parking_status(benchmark_profile())
    pin = pin_from_site_fact_source(status.source, fact_ids=("transit_parking",))
    assert pin is not None
    assert pin.dataset == "PLUTO (64uk-42ks)"
    assert pin.version == "26v2"
    assert pin.retrieved_at == RETRIEVED_AT
    # A retrieval is an observation of what the dataset published then, so the pin is
    # current against itself (data_versions rule; no newer version is on record).
    assessed = assess_source(pin, published_from_pins([pin]))
    assert assessed.status == STATUS_CURRENT


# ---------------------------------------------------------------------------
# C-8: one source applied identically to every option
# ---------------------------------------------------------------------------


def test_one_source_applied_identically_to_every_option() -> None:
    status = resolve_transit_parking_status(benchmark_profile())
    options = ("as_of_right", "affordable", "senior", "shared_housing", "max_units")
    applied = applied_to_options(status, options)

    assert set(applied) == set(options)
    expected = status.to_dict()
    for option_id in options:
        assert applied[option_id] == expected
    # Every option carries the byte-identical status - it cannot differ (check C-8).
    distinct = {json.dumps(value, sort_keys=True) for value in applied.values()}
    assert len(distinct) == 1


def test_applied_to_options_rejects_blank_and_duplicate_ids() -> None:
    status = resolve_transit_parking_status(benchmark_profile())
    with pytest.raises(ValueError):
        applied_to_options(status, ("option_a", "option_a"))
    with pytest.raises(ValueError):
        applied_to_options(status, ("option_a", "  "))


def test_resolve_is_deterministic() -> None:
    profile = benchmark_profile()
    first = resolve_transit_parking_status(profile).to_dict()
    second = resolve_transit_parking_status(profile).to_dict()
    assert first == second


# ---------------------------------------------------------------------------
# Check needed: missing or untrusted, never a guess
# ---------------------------------------------------------------------------


def test_check_needed_when_pluto_has_no_transit_zone_value() -> None:
    record = benchmark_record()
    assert record.pop(TRANSIT_ZONE_FIELD) == "Outer Transit Zone"  # SYNTHETIC: null omitted
    status = resolve_transit_parking_status(profile_from_record(record))
    assert status.status == STATUS_CHECK_NEEDED
    assert status.transit_zone is None
    assert status.needs_check is True
    assert status.missing_source == MISSING_PARKING_ZONE_SOURCE
    assert "Check needed" in status.detail
    assert "dpnc-b2hd" in status.detail  # names the parking-zone layers to check


def test_untrusted_pluto_value_is_check_needed_never_surfaced() -> None:
    # SYNTHETIC minimal profile: PLUTO returns a transit zone but flags a conflict on it.
    profile = {
        "identity": {"bbl": BBL},
        "provenance": [
            {
                "source_id": "nyc-dcp-pluto-soda",
                "bbl": BBL,
                "original_field_name": "transitzone",
                "normalized_value": "Outer Transit Zone",
                "conflict_status": "conflicting",
                "dataset_version": "26v2",
                "retrieved_at": RETRIEVED_AT,
                "request_url": (
                    "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=" + BBL
                ),
                "provenance_id": "pluto-64uk-42ks-26v2-" + BBL + "-transitzone",
            }
        ],
    }
    status = resolve_transit_parking_status(profile)
    assert status.status == STATUS_CHECK_NEEDED
    assert status.transit_zone is None
    assert "conflict" in status.detail.lower()


def test_missing_identity_bbl_raises() -> None:
    with pytest.raises(ValueError):
        resolve_transit_parking_status({"provenance": []})
