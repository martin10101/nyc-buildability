"""Unit tests for the pure illustrative-area-allocation computation.

The module under test is app.scenario.three_answers.area_allocation.

Every expected value comes ONLY from the settled worked example
docs/reference-cases/R6B/cases/placement-building-b.json (step P8, row area-allocation), never from
a program run; the agreement of two independent AI readings is not proof. The produced
area_allocation dict is validated against contract 1.5.0 $defs.area_allocation and against the
cross-key rules in results_way_rules.py (the fitted-only-when-placed rule the schema cannot
express).

Scenario map (packet M5-T182): S4 the split; S5 the 8,060 no-conflation guard (G-10); S7 schema
conformance + no apartment-plan keys + fitted-true-with-withheld refused; S8 the fixed measure. Plus
the result-deciding rule: a missing residential floor area holds the allocation back, and fitted
follows the placement status (read by equality, never a truthiness test).
"""

from __future__ import annotations

import json
from importlib import resources

import jsonschema
import pytest
from referencing import Registry, Resource

from app.contracts.results_way_rules import results_way_violations
from app.scenario.three_answers import area_allocation as mod
from app.scenario.three_answers.area_allocation import (
    AREA_MEASURE,
    ILLUSTRATIVE_LABEL,
    PLATE_CONVERSION_STATEMENT,
    STATED_APARTMENT_SHARE,
    build_area_allocation,
    per_storey_area,
)
from app.scenario.three_answers.placement import build_placement

# --- the settled worked example (row area-allocation), as the sole numeric source ---
RESIDENTIAL_FLOOR_AREA_SQFT = 20150.0  # all residential, so = the zoning floor area
STOREYS = 3
EXPECTED_SHARE = 0.60  # the one stated share (share_low)
EXPECTED_APARTMENT_TOTAL = 12090.00  # 20,150 x 0.60
EXPECTED_OTHER_TOTAL = 8060.00  # 20,150 - 12,090
EXPECTED_TOTAL = 20150.00
EXPECTED_APARTMENT_PER_STOREY = 4030.00  # 12,090 / 3
EXPECTED_OTHER_PER_STOREY = 2686.67  # 8,060 / 3
EXPECTED_PLATE = 6716.67  # 4,030.00 + 2,686.67 (the per-storey figures sum to the plate)

# The coverage lower bound (row lot-coverage-max): 0.80 of the recorded lot area. A DIFFERENT
# quantity on a DIFFERENT basis that happens to share the numeral 8,060 with the other-area total.
RECORDED_LOT_AREA_SQFT = 10075.0  # administrative_record (PLUTO)
COVERAGE_LOWER_BOUND_PCT = 0.80

_PLAN_KEYS = ("unit_count", "units", "rooms", "walls", "core", "stair", "elevator")
_SCHEMA_PACKAGE = "app._contract_schemas.v1"


def _load(name: str) -> dict:
    return json.loads(resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8"))


def _fragment_validator(defname: str) -> jsonschema.Draft202012Validator:
    results = _load("results.schema.json")
    common = _load("common.schema.json")
    registry = Registry().with_resources(
        [
            (results["$id"], Resource.from_contents(results)),
            (common["$id"], Resource.from_contents(common)),
        ]
    )
    return jsonschema.Draft202012Validator(
        {"$ref": f"{results['$id']}#/$defs/{defname}"}, registry=registry
    )


def _schema_const(defname: str) -> str:
    return _load("results.schema.json")["$defs"][defname]["const"]


def _alloc(placement_status: str | None = "placed") -> dict:
    return build_area_allocation(
        residential_floor_area_sqft=RESIDENTIAL_FLOOR_AREA_SQFT,
        placement_status=placement_status,
    )


def _document(placement: dict, allocation: dict) -> dict:
    """A minimal 1.5.0 document fragment carrying one building alternative, for the cross-key rule.
    results_way_violations reads building_alternatives[].placement and [].area_allocation, but
    returns early unless the document also carries an ``answers`` mapping, so one is included."""
    return {
        "contract_version": "1.5.0",
        "answers": {},
        "building_alternatives": [
            {"building": "B", "placement": placement, "area_allocation": allocation}
        ],
    }


# --- S4: the split at the one stated 60 percent share ---
def test_s4_split_totals() -> None:
    alloc = _alloc()
    assert alloc["share"] == EXPECTED_SHARE
    assert alloc["apartment_area_sqft"] == EXPECTED_APARTMENT_TOTAL
    assert alloc["other_area_sqft"] == EXPECTED_OTHER_TOTAL
    assert alloc["total_sqft"] == EXPECTED_TOTAL


def test_s4_apartment_plus_other_equals_total() -> None:
    alloc = _alloc()
    assert alloc["apartment_area_sqft"] + alloc["other_area_sqft"] == alloc["total_sqft"]


def test_s4_per_storey_figures_sum_to_the_plate() -> None:
    apartment = per_storey_area(EXPECTED_APARTMENT_TOTAL, STOREYS)
    other = per_storey_area(EXPECTED_OTHER_TOTAL, STOREYS)
    assert apartment == EXPECTED_APARTMENT_PER_STOREY
    assert other == EXPECTED_OTHER_PER_STOREY
    assert apartment + other == EXPECTED_PLATE


def test_s4_the_default_share_is_the_stated_low_end() -> None:
    assert STATED_APARTMENT_SHARE == EXPECTED_SHARE


# --- S5: the 8,060 coincidence is never summed, equated or carried as one figure (G-10) ---
def test_s5_two_8060_figures_are_equal_numerals_on_different_bases() -> None:
    # the allocation other-area total (0.40 x 20,150, derived)
    other_total = _alloc()["other_area_sqft"]
    # the coverage lower bound (0.80 x 10,075, administrative_record) - computed HERE, never by the
    # allocation module
    coverage_lower_bound = round(COVERAGE_LOWER_BOUND_PCT * RECORDED_LOT_AREA_SQFT, 2)
    assert other_total == EXPECTED_OTHER_TOTAL
    assert coverage_lower_bound == EXPECTED_OTHER_TOTAL  # the same numeral
    assert other_total == coverage_lower_bound


def test_s5_the_allocation_never_carries_a_coverage_figure() -> None:
    alloc = _alloc()
    # only the eight allocation keys; no coverage / lot-area key mixing the two bases
    assert set(alloc) <= {
        "label",
        "share",
        "measure",
        "conversion_statement",
        "apartment_area_sqft",
        "other_area_sqft",
        "total_sqft",
        "fitted",
        "conditions",
    }
    joined = " ".join(k.lower() for k in alloc)
    assert "coverage" not in joined
    assert "lot_area" not in joined


def test_s5_the_module_computes_no_coverage() -> None:
    # the allocation emits no lot-coverage symbol; that figure belongs to the coverage reading
    public = {name.lower() for name in mod.__all__}
    assert not any("coverage" in name for name in public)


# --- S6-equivalent: fitted follows the placement status (equality, not truthiness) ---
@pytest.mark.parametrize(
    "status, expected",
    [("placed", True), ("withheld", False), (None, False), ("anything_else", False)],
)
def test_fitted_follows_the_placement_status(status, expected: bool) -> None:
    assert build_area_allocation(
        residential_floor_area_sqft=RESIDENTIAL_FLOOR_AREA_SQFT, placement_status=status
    )["fitted"] is expected


# --- S7: schema conformance; fitted-true-with-withheld refused; no apartment-plan keys ---
def test_s7_placed_allocation_validates() -> None:
    assert list(_fragment_validator("area_allocation").iter_errors(_alloc("placed"))) == []


def test_s7_unplaced_allocation_validates_and_is_emitted() -> None:
    alloc = _alloc("withheld")
    assert alloc is not None  # emitted for every alternative with a floor area, placed or not
    assert alloc["fitted"] is False
    assert list(_fragment_validator("area_allocation").iter_errors(alloc)) == []


def test_s7_consts_match_the_schema_byte_for_byte() -> None:
    assert ILLUSTRATIVE_LABEL == _schema_const("illustrative_label")
    assert AREA_MEASURE == _schema_const("area_measure")
    assert PLATE_CONVERSION_STATEMENT == _schema_const("plate_conversion_statement")


@pytest.mark.parametrize("plan_key", _PLAN_KEYS)
def test_s7_an_apartment_plan_key_is_rejected(plan_key: str) -> None:
    bad = _alloc()
    bad[plan_key] = 1
    assert list(_fragment_validator("area_allocation").iter_errors(bad)) != []


def test_s7_fitted_true_with_a_withheld_placement_is_refused_by_the_cross_key_rule() -> None:
    # force the broken combination the module never builds, and prove the way-layer catches it
    placement = build_placement(placed=False)
    allocation = dict(_alloc("withheld"))
    allocation["fitted"] = True
    violations = results_way_violations(_document(placement, allocation))
    assert any(v.rule == "allocation_fitted_without_placement" for v in violations)


def test_s7_the_modules_own_output_passes_the_cross_key_rule() -> None:
    placed_doc = _document(build_placement(placed=True, zoning_floor_area_sqft=20150.0,
                                           storeys=3, frontage_ft=100.76, lot_depth_ft=100.0),
                           _alloc("placed"))
    withheld_doc = _document(build_placement(placed=False), _alloc("withheld"))
    assert results_way_violations(placed_doc) == []
    assert results_way_violations(withheld_doc) == []


# --- S8: the fixed measure (G-14) ---
def test_s8_carries_the_measure_and_conversion_statement() -> None:
    alloc = _alloc()
    assert alloc["measure"] == AREA_MEASURE == "residential_floor_area"
    assert alloc["conversion_statement"] == PLATE_CONVERSION_STATEMENT
    assert "no gross-up, exclusions or wall-thickness conversion worked" in (
        alloc["conversion_statement"]
    )


# --- the result-deciding rule: a missing floor area holds the allocation back ---
def test_a_missing_floor_area_holds_the_allocation_back() -> None:
    assert build_area_allocation(residential_floor_area_sqft=None) is None


def test_per_storey_is_none_when_a_fact_is_missing() -> None:
    assert per_storey_area(None, STOREYS) is None
    assert per_storey_area(EXPECTED_APARTMENT_TOTAL, None) is None


def test_a_share_outside_the_contract_bound_fails_closed() -> None:
    with pytest.raises(ValueError):
        build_area_allocation(residential_floor_area_sqft=RESIDENTIAL_FLOOR_AREA_SQFT, share=0.50)
    with pytest.raises(ValueError):
        build_area_allocation(residential_floor_area_sqft=RESIDENTIAL_FLOOR_AREA_SQFT, share=0.80)
