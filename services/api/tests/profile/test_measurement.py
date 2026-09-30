"""Measurement ranks, labels and the weakest-input label (queue item B-02; plan M1-07
and section 4 "How labels carry through")."""

from __future__ import annotations

import itertools

import pytest

from app.profile.measurement import (
    MEASUREMENT_LABELS,
    MEASUREMENT_ORDER,
    RANK_APPROXIMATE_TAX_MAP,
    RANK_ASSUMED,
    RANK_CITY_RECORDS,
    RANK_ENTERED,
    RANK_SURVEY_ENTERED,
    RANK_UNKNOWN,
    answer_measurement,
    measurement,
    weakest_measurement,
)
from tests.profile.site_fact_contract import load_schema, schema_errors


def test_vocabulary_is_exactly_the_site_fact_contract_vocabulary() -> None:
    defs = load_schema("site_fact.schema.json")["$defs"]
    contract = {}
    for option in defs["measurement"]["oneOf"]:
        properties = defs[option["$ref"].rsplit("/", 1)[1]]["properties"]
        contract[properties["rank"]["const"]] = properties["label"]["const"]
    assert dict(MEASUREMENT_LABELS) == contract
    assert set(MEASUREMENT_ORDER) == set(contract)
    assert len(MEASUREMENT_ORDER) == 6


def test_plan_section_4_order_is_kept_and_unknown_is_weakest() -> None:
    plan_order = [
        RANK_SURVEY_ENTERED,
        RANK_CITY_RECORDS,
        RANK_APPROXIMATE_TAX_MAP,
        RANK_UNKNOWN,
    ]
    positions = [MEASUREMENT_ORDER.index(rank) for rank in plan_order]
    assert positions == sorted(positions)
    assert MEASUREMENT_ORDER[-1] == RANK_UNKNOWN


def test_assumed_is_the_weakest_known_rank() -> None:
    # results.schema.json: a "Needs street width" case counts the assumed width as an
    # 'assumed' input, so the case reads "Assumed" whatever its other inputs are.
    for rank in MEASUREMENT_ORDER:
        if rank in (RANK_ASSUMED, RANK_UNKNOWN):
            continue
        assert weakest_measurement([rank, RANK_ASSUMED])["rank"] == RANK_ASSUMED
    assert weakest_measurement([RANK_ENTERED, RANK_APPROXIMATE_TAX_MAP])["rank"] == RANK_ENTERED


@pytest.mark.parametrize("pair", list(itertools.combinations(MEASUREMENT_ORDER, 2)))
def test_weakest_of_any_pair_is_the_later_rank_in_either_order(pair) -> None:
    stronger, weaker = pair
    assert weakest_measurement([stronger, weaker]) == measurement(weaker)
    assert weakest_measurement([weaker, stronger]) == measurement(weaker)


def test_weakest_reads_site_facts_measurements_and_rank_strings() -> None:
    fact = {"key": "lot_area", "measurement": measurement(RANK_CITY_RECORDS)}
    tax_map = measurement(RANK_APPROXIMATE_TAX_MAP)
    assert weakest_measurement([fact, tax_map, RANK_SURVEY_ENTERED]) == {
        "rank": "approximate_tax_map",
        "label": "Approximate — tax map",
    }
    assert weakest_measurement(iter([fact])) == {"rank": "city_records", "label": "City records"}


def test_unknown_input_makes_the_answer_not_available() -> None:
    assert weakest_measurement([RANK_CITY_RECORDS, RANK_UNKNOWN]) == {
        "rank": "unknown",
        "label": "Unknown — enter",
    }
    assert answer_measurement([RANK_CITY_RECORDS, RANK_UNKNOWN]) is None


@pytest.mark.parametrize("rank", [r for r in MEASUREMENT_ORDER if r != RANK_UNKNOWN])
def test_answer_label_is_a_valid_results_measurement(rank) -> None:
    label = answer_measurement([RANK_SURVEY_ENTERED, rank])
    assert label == measurement(rank)
    assert not schema_errors(label, "#/$defs/measurement_known")


def test_every_measurement_object_is_valid_for_the_contract() -> None:
    for rank in MEASUREMENT_ORDER:
        assert not schema_errors(measurement(rank), "#/$defs/measurement")
    assert schema_errors(measurement(RANK_UNKNOWN), "#/$defs/measurement_known")


@pytest.mark.parametrize(
    "inputs",
    [
        [],
        ["verified"],
        [{"rank": "city_records", "label": "Survey (entered)"}],
        [{"measurement": {"rank": "survey", "label": "Survey (entered)"}}],
        [{"measurement": "city_records"}],
        [3],
    ],
)
def test_bad_inputs_fail_loudly(inputs) -> None:
    with pytest.raises(ValueError):
        weakest_measurement(inputs)


def test_measurement_rejects_an_unknown_rank() -> None:
    with pytest.raises(ValueError):
        measurement("approximate")
