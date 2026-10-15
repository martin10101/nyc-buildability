"""Unit tests for the pure illustrative-placement computation.

The module under test is app.scenario.three_answers.placement.

Every expected value comes ONLY from the settled worked example
docs/reference-cases/R6B/cases/placement-building-b.json (step P8), never from a program run; the
agreement of two independent AI readings is not proof. The produced building_placement dict is
validated against contract 1.5.0 $defs.building_placement (the bundled schema the engine uses).

Scenario map (packet M5-T182): S1 plate + footprint; S2 placed outline (every vertex derived,
reconciled); S3 withheld (no outline); S6 the tax-map / city-map offset conflict; S7 schema
conformance + no apartment-plan keys; S8 the fixed measure. Plus the result-deciding rule: a missing
fact holds the placement back, and no optional fact is read with a truthiness test.
"""

from __future__ import annotations

import json
from importlib import resources

import jsonschema
import pytest
from referencing import Registry, Resource

from app.scenario.three_answers.placement import (
    AREA_MEASURE,
    ILLUSTRATIVE_LABEL,
    PLATE_CONVERSION_STATEMENT,
    PRINTED_TAX_MAP_BASIS,
    RECONCILE_TOLERANCE_SQFT,
    build_placement,
    compute_placement_geometry,
    plate_area_sqft,
)

# --- the settled worked example (placement-building-b.json), as the sole numeric source ---
ZFA_SQFT = 20150.0
STOREYS = 3
TAX_FRONTAGE_FT = 100.76  # printed_tax_map (= PLUTO lotfront)
TAX_DEPTH_FT = 100.0  # printed_tax_map (= PLUTO lotdepth)
GIS_FRONTAGE_FT = 103.88  # gis (conflict check only)
GIS_DEPTH_FT = 99.97  # gis (conflict check only)

EXPECTED_PLATE = 6716.67  # 20,150 / 3 (row plate)
EXPECTED_PLAN_DEPTH = 66.66  # 6,716.6667 / 100.76 (row footprint-tax-map)
EXPECTED_FOOTPRINT = 6716.66  # 66.66 x 100.76 (row footprint-tax-map)
EXPECTED_TAX_BACK_CLEARANCE = 33.34  # 100 - 66.66 (row placement-tax-map)
EXPECTED_GIS_PLAN_DEPTH = 64.66  # 6,716.6667 / 103.88 (row gis-conflict-check)
EXPECTED_GIS_BACK_CLEARANCE = 35.31  # 99.97 - 64.66 (row gis-conflict-check, NOT 33.32)
EXPECTED_FRONTAGE_CONFLICT = 3.12  # 103.88 - 100.76 (row gis-conflict-check)
EXPECTED_TAX_RECTANGLE = 10076.0  # 100.76 x 100 (row gis-conflict-check)
EXPECTED_FOOTPRINT_SHARE = 66.66  # 6,716.66 / 10,076 x 100 (row lot-coverage-whole-lot)

_PLAN_KEYS = ("unit_count", "units", "rooms", "walls", "core", "stair", "elevator")


# --- a validator for one schema $def fragment, from the same bundled schema the engine uses ---
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
    schema = {"$ref": f"{results['$id']}#/$defs/{defname}"}
    return jsonschema.Draft202012Validator(schema, registry=registry)


def _schema_const(defname: str) -> str:
    return _load("results.schema.json")["$defs"][defname]["const"]


def _placed() -> dict:
    return build_placement(
        placed=True,
        zoning_floor_area_sqft=ZFA_SQFT,
        storeys=STOREYS,
        frontage_ft=TAX_FRONTAGE_FT,
        lot_depth_ft=TAX_DEPTH_FT,
        gis_frontage_ft=GIS_FRONTAGE_FT,
        gis_depth_ft=GIS_DEPTH_FT,
    )


def _geom():
    return compute_placement_geometry(
        zoning_floor_area_sqft=ZFA_SQFT,
        storeys=STOREYS,
        frontage_ft=TAX_FRONTAGE_FT,
        lot_depth_ft=TAX_DEPTH_FT,
        gis_frontage_ft=GIS_FRONTAGE_FT,
        gis_depth_ft=GIS_DEPTH_FT,
    )


# --- S1: the plate and the footprint, each on its own recompute, reconciled not forced ---
def test_s1_plate_is_zoning_floor_area_per_storey() -> None:
    assert plate_area_sqft(ZFA_SQFT, STOREYS) == EXPECTED_PLATE


def test_s1_plan_depth_and_footprint() -> None:
    geom = _geom()
    assert geom.plate_sqft == EXPECTED_PLATE
    assert geom.plan_depth_ft == EXPECTED_PLAN_DEPTH
    assert geom.footprint_sqft == EXPECTED_FOOTPRINT


def test_s1_footprint_reconciles_with_plate_but_is_not_forced_equal() -> None:
    geom = _geom()
    # separate quantities, 0.01 apart, reconciled within the readers' half a square foot
    assert geom.footprint_sqft != geom.plate_sqft
    assert abs(geom.footprint_sqft - geom.plate_sqft) == pytest.approx(0.01, abs=1e-9)
    assert abs(geom.footprint_sqft - geom.plate_sqft) <= RECONCILE_TOLERANCE_SQFT


# --- S2: the placed footprint outline, every vertex derived, measured area reconciled ---
def test_s2_placed_carries_outline_and_the_fixed_fields() -> None:
    placed = _placed()
    assert placed["status"] == "placed"
    assert placed["label"] == ILLUSTRATIVE_LABEL
    assert placed["basis"] == PRINTED_TAX_MAP_BASIS
    assert placed["measure"] == AREA_MEASURE
    assert placed["conversion_statement"] == PLATE_CONVERSION_STATEMENT
    assert "outline" in placed


def test_s2_outline_vertices_are_derived_from_frontage_and_depth() -> None:
    geom = _geom()
    ring = geom.outline[0]
    # a closed rectangle: origin at the street-line corner, x along the frontage, y back from it
    assert ring == [
        [0.0, 0.0],
        [TAX_FRONTAGE_FT, 0.0],
        [TAX_FRONTAGE_FT, EXPECTED_PLAN_DEPTH],
        [0.0, EXPECTED_PLAN_DEPTH],
        [0.0, 0.0],
    ]
    assert ring[0] == ring[-1]  # closed


def test_s2_outline_area_reconciles_with_the_plate() -> None:
    geom = _geom()
    # the outline area is measured from the vertices (shoelace), not copied from the footprint
    assert geom.outline_area_sqft == EXPECTED_FOOTPRINT
    assert abs(geom.outline_area_sqft - geom.plate_sqft) <= RECONCILE_TOLERANCE_SQFT


def test_s2_placed_validates_against_the_contract() -> None:
    errors = list(_fragment_validator("building_placement").iter_errors(_placed()))
    assert errors == []


# --- S3: the unplaced (withheld) state carries no outline ---
def test_s3_withheld_has_no_outline_and_validates() -> None:
    withheld = build_placement(placed=False)
    assert withheld["status"] == "withheld"
    assert "outline" not in withheld
    assert withheld["label"] == ILLUSTRATIVE_LABEL
    assert withheld["basis"] == PRINTED_TAX_MAP_BASIS
    assert withheld["measure"] == AREA_MEASURE
    assert withheld["conversion_statement"] == PLATE_CONVERSION_STATEMENT
    assert list(_fragment_validator("building_placement").iter_errors(withheld)) == []


def test_s3_withheld_with_an_outline_is_rejected_by_the_schema() -> None:
    bad = build_placement(placed=False)
    bad["outline"] = _placed()["outline"]  # the withheld branch forbids an outline key
    assert list(_fragment_validator("building_placement").iter_errors(bad)) != []


# --- S6: the tax-map / city-map offset conflict, both bases carried, never resolved ---
def test_s6_offsets_derived_on_each_basis() -> None:
    geom = _geom()
    assert geom.tax_back_clearance_ft == EXPECTED_TAX_BACK_CLEARANCE
    assert geom.gis_plan_depth_ft == EXPECTED_GIS_PLAN_DEPTH
    assert geom.gis_back_clearance_ft == EXPECTED_GIS_BACK_CLEARANCE
    assert geom.frontage_conflict_ft == EXPECTED_FRONTAGE_CONFLICT
    assert geom.footprint_share_pct == EXPECTED_FOOTPRINT_SHARE
    assert geom.tax_rectangle_sqft == EXPECTED_TAX_RECTANGLE


def test_s6_conflict_condition_names_both_bases_and_resolves_neither() -> None:
    placed = _placed()
    conflicts = [
        c for c in placed["conditions"] if c["kind"] == "contradicted_record"
    ]
    assert len(conflicts) == 1
    text = conflicts[0]["assumption"]
    assert "33.34" in text  # the tax-map back clearance
    assert "35.31" in text  # the city-map (GIS) back clearance
    assert "3.12" in text  # the frontage conflict
    # a conflict carried, not silently resolved: a survey/deed would settle it
    assert "survey" in conflicts[0]["settled_by"].lower()


def test_s6_without_gis_inputs_no_conflict_is_invented() -> None:
    geom = compute_placement_geometry(
        zoning_floor_area_sqft=ZFA_SQFT,
        storeys=STOREYS,
        frontage_ft=TAX_FRONTAGE_FT,
        lot_depth_ft=TAX_DEPTH_FT,
    )
    assert geom.gis_back_clearance_ft is None
    assert geom.frontage_conflict_ft is None


# --- S7: schema conformance; no apartment-plan keys; the fixed consts ---
def test_s7_consts_match_the_schema_byte_for_byte() -> None:
    assert ILLUSTRATIVE_LABEL == _schema_const("illustrative_label")
    assert AREA_MEASURE == _schema_const("area_measure")
    assert PLATE_CONVERSION_STATEMENT == _schema_const("plate_conversion_statement")


@pytest.mark.parametrize("plan_key", _PLAN_KEYS)
def test_s7_an_apartment_plan_key_is_rejected(plan_key: str) -> None:
    bad = _placed()
    bad[plan_key] = 1
    assert list(_fragment_validator("building_placement").iter_errors(bad)) != []


# --- S8: the fixed measure (G-14); the physical floor plate is not checked ---
def test_s8_physical_floor_plate_is_listed_not_checked() -> None:
    for placement in (_placed(), build_placement(placed=False)):
        assert placement["conversion_statement"] == PLATE_CONVERSION_STATEMENT
        assert any(
            "physical floor plate (gross-up, exclusions, wall thickness)" in entry
            for entry in placement["not_checked"]
        )


# --- the result-deciding rule: a missing fact holds the placement back (no default/truthiness) ---
@pytest.mark.parametrize(
    "overrides",
    [
        {"zoning_floor_area_sqft": None},
        {"storeys": None},
        {"frontage_ft": None},
        {"lot_depth_ft": None},
    ],
)
def test_a_missing_fact_withholds_the_placement(overrides: dict) -> None:
    kwargs = {
        "placed": True,
        "zoning_floor_area_sqft": ZFA_SQFT,
        "storeys": STOREYS,
        "frontage_ft": TAX_FRONTAGE_FT,
        "lot_depth_ft": TAX_DEPTH_FT,
    }
    kwargs.update(overrides)
    placement = build_placement(**kwargs)
    assert placement["status"] == "withheld"
    assert "outline" not in placement


def test_plate_is_none_when_a_fact_is_missing() -> None:
    assert plate_area_sqft(None, STOREYS) is None
    assert plate_area_sqft(ZFA_SQFT, None) is None


def test_a_real_zero_frontage_is_a_value_not_a_missing_fact() -> None:
    # a truthiness test on the frontage would read 0.0 as missing and silently withhold; the
    # module reads it as a value, so a zero frontage fails closed (it is a bad dimension)
    with pytest.raises(ValueError):
        build_placement(
            placed=True,
            zoning_floor_area_sqft=ZFA_SQFT,
            storeys=STOREYS,
            frontage_ft=0.0,
            lot_depth_ft=TAX_DEPTH_FT,
        )
