"""Tests for the C-09 compare backend (plan M1-18 'Compare options side by side';
directive D-090; feeds Lane D's D-10).

Two options are built from the SAME 215-16 Northern Blvd benchmark inputs the A-04
golden tests use (BBL 4073340070). The input values are copied here (the benchmark test
file is not edited); real results-v1 documents are generated through
``app.scenario.three_answers.generate_results`` with ``LANE_A_ENABLED`` on, exactly as the
benchmark test does, so the comparison is exercised over real generator output, not a
hand-built stub.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.contracts.compare_rows import ROW_CATALOGUE, CompareRowsError, build_compare_rows
from app.contracts.study_contracts import (
    STUDY_CONTRACT_STEMS,
    validate_compare_rows_document,
)
from app.scenario.three_answers import (
    BuildingDefaults,
    ThreeAnswerInputs,
    generate_results,
)

_REPO_ROOT = Path(__file__).resolve().parents[4]
_BENCHMARK = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)
_FIXTURES = _REPO_ROOT / "packages" / "contracts" / "fixtures"
_ON = {"LANE_A_ENABLED": "1"}
_OFF: dict[str, str] = {}

_CATALOGUE_KEYS = [key for key, _label, _builder in ROW_CATALOGUE]


def _expected(key: str):
    doc = json.loads(_BENCHMARK.read_text("utf-8"))
    return next(v["value"] for v in doc["expected_values"] if v["key"] == key)


def _inputs(*, option_id: str, results_id: str, study_id="study-1", revision=1, ftf=10.0):
    return ThreeAnswerInputs(
        results_id=results_id,
        study_id=study_id,
        option_id=option_id,
        revision=revision,
        computed_at="2026-10-03T00:00:00Z",
        zoning_district=_expected("zoning_district"),
        lot_area_sq_ft=float(_expected("lot_area")),
        lot_type=_expected("lot_type"),
        housing_program="standard_residence",
        overlay_present=True,
        special_district_present=False,
        within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0,
        special_density_area=False,
        lot_front_ft=float(_expected("lot_dimension_1")),
        lot_depth_ft=float(_expected("lot_dimension_2")),
        depends_on_fact_ids=("pluto:4073340070:lotarea",),
        lot_area_fact_id="pluto:4073340070:lotarea",
        building_defaults=BuildingDefaults(floor_to_floor_ft=ftf),
    )


def _results(*, option_id, results_id, study_id="study-1", revision=1, ftf=10.0, env=None):
    inputs = _inputs(
        option_id=option_id, results_id=results_id, study_id=study_id, revision=revision, ftf=ftf
    )
    return generate_results(inputs, env=_ON if env is None else env).document


def _row(doc: dict, key: str) -> dict:
    return next(r for r in doc["rows"] if r["key"] == key)


def _lot_extent(geometry: dict) -> tuple[float, float]:
    xs = [p[0] for ring in geometry["lot_outline"] for p in ring]
    ys = [p[1] for ring in geometry["lot_outline"] for p in ring]
    return (max(xs) - min(xs), max(ys) - min(ys))


# ---------------------------------------------------------------------------
# Identical row set for every option (plan M1-18 'Identical rows').
# ---------------------------------------------------------------------------


def test_same_ordered_row_set_for_every_option() -> None:
    a = _results(option_id="opt-a", results_id="res-a")
    b = _results(option_id="opt-b", results_id="res-b")
    doc = build_compare_rows([a, b], study_id="study-1", revision=1)

    # The full catalogue, in a fixed order, and exactly one cell per option on every row.
    assert [r["key"] for r in doc["rows"]] == _CATALOGUE_KEYS
    assert [r["catalogue_order"] for r in doc["rows"]] == list(range(len(_CATALOGUE_KEYS)))
    for row in doc["rows"]:
        assert len(row["cells"]) == 2
        for cell in row["cells"]:
            assert cell["status"] in ("available", "not_available")  # never missing/blank
    # The identity columns follow the caller's order.
    assert [o["option_id"] for o in doc["options"]] == ["opt-a", "opt-b"]
    # Reaching here means build validated the output; it is also independently valid.
    validate_compare_rows_document(doc)
    assert doc["contract_version"] == "1.0.0"


def test_identical_options_render_byte_identical_cells() -> None:
    # Two options with identical inputs (only the identity differs) produce identical cells.
    a = _results(option_id="opt-a", results_id="res-a")
    b = _results(option_id="opt-b", results_id="res-b")
    doc = build_compare_rows([a, b], study_id="study-1", revision=1)
    for row in doc["rows"]:
        assert row["cells"][0] == row["cells"][1], row["key"]


def test_floor_to_floor_difference_shows_in_the_rows() -> None:
    a = _results(option_id="opt-a", results_id="res-a", ftf=10.0)
    b = _results(option_id="opt-b", results_id="res-b", ftf=12.0)
    doc = build_compare_rows([a, b], study_id="study-1", revision=1)

    ftf_row = _row(doc, "floor_to_floor_ft")
    assert ftf_row["cells"][0]["value"] == 10.0
    assert ftf_row["cells"][1]["value"] == 12.0
    assert ftf_row["cells"][0]["unit"] == "feet"
    # The taller floor-to-floor fits fewer floors under the 55 ft limit, which also shows.
    floors_row = _row(doc, "floors_fit")
    assert floors_row["cells"][0]["value"] == 5
    assert floors_row["cells"][1]["value"] == 4


def test_allowance_value_is_copied_with_its_provenance() -> None:
    a = _results(option_id="opt-a", results_id="res-a")
    b = _results(option_id="opt-b", results_id="res-b")
    doc = build_compare_rows([a, b], study_id="study-1", revision=1)
    cell = _row(doc, "floor_area_allowance")["cells"][0]
    assert cell["status"] == "available"
    assert cell["value"] == _expected("max_residential_floor_area")  # 20150, a straight copy
    assert cell["unit"] == "square_feet"
    assert "ZR 23-22" in cell["zr_sections"]  # provenance carried, never stripped
    assert cell["sources"]


# ---------------------------------------------------------------------------
# A not_available option still has every row, with the results' own reason.
# ---------------------------------------------------------------------------


def test_not_available_option_still_has_every_row_with_reason_carried() -> None:
    on = _results(option_id="opt-on", results_id="res-on", env=_ON)
    off = _results(option_id="opt-off", results_id="res-off", env=_OFF)  # lane gated off
    doc = build_compare_rows([on, off], study_id="study-1", revision=1)

    # Every metric row is still present for both options.
    assert [r["key"] for r in doc["rows"]] == _CATALOGUE_KEYS
    assert all(len(r["cells"]) == 2 for r in doc["rows"])

    # The gated option's answer cell is not_available with the generator's OWN reason/kind.
    off_cell = _row(doc, "floor_area_allowance")["cells"][1]
    assert off_cell["status"] == "not_available"
    assert off_cell["reason_kind"] == "rule_not_reviewed"
    assert off_cell["reason"]  # a real sentence, copied from the results document
    source_reason = off["answers"]["floor_area_allowance"]["reason"]
    assert off_cell["reason"] == source_reason  # verbatim, never reworded


# ---------------------------------------------------------------------------
# Fail closed on an incoherent comparison.
# ---------------------------------------------------------------------------


def test_mixed_study_ids_raise() -> None:
    a = _results(option_id="opt-a", results_id="res-a", study_id="study-1")
    b = _results(option_id="opt-b", results_id="res-b", study_id="study-2")
    with pytest.raises(CompareRowsError, match="study"):
        build_compare_rows([a, b], study_id="study-1", revision=1)


def test_mixed_revisions_raise() -> None:
    a = _results(option_id="opt-a", results_id="res-a", revision=1)
    b = _results(option_id="opt-b", results_id="res-b", revision=2)
    with pytest.raises(CompareRowsError, match="revision"):
        build_compare_rows([a, b], study_id="study-1", revision=1)


def test_fewer_than_two_options_raise() -> None:
    a = _results(option_id="opt-a", results_id="res-a")
    with pytest.raises(CompareRowsError, match="at least two"):
        build_compare_rows([a], study_id="study-1", revision=1)


def test_repeated_option_id_raises() -> None:
    a = _results(option_id="opt-a", results_id="res-a")
    b = _results(option_id="opt-a", results_id="res-b")  # same option_id twice
    with pytest.raises(CompareRowsError, match="more than once"):
        build_compare_rows([a, b], study_id="study-1", revision=1)


# ---------------------------------------------------------------------------
# A-05 duplicate record carried through (opaque, caller-produced).
# ---------------------------------------------------------------------------


def test_duplicate_record_appears_for_identical_options() -> None:
    a = _results(option_id="opt-a", results_id="res-a")
    b = _results(option_id="opt-b", results_id="res-b")  # identical inputs
    record = {
        "option_ids": ["opt-a", "opt-b"],
        "disposition": "merge",
        "reason": "Both options resolve to the same inputs and the same results.",
    }
    doc = build_compare_rows(
        [a, b], study_id="study-1", revision=1, duplicate_records=[record]
    )
    # Carried through verbatim (opaque: the comparison never recomputed A-05's identity).
    assert doc["duplicates"] == [record]


def test_no_duplicate_records_by_default() -> None:
    a = _results(option_id="opt-a", results_id="res-a")
    b = _results(option_id="opt-b", results_id="res-b")
    doc = build_compare_rows([a, b], study_id="study-1", revision=1)
    assert doc["duplicates"] == []


def test_duplicate_record_naming_an_absent_option_raises() -> None:
    a = _results(option_id="opt-a", results_id="res-a")
    b = _results(option_id="opt-b", results_id="res-b")
    record = {"option_ids": ["opt-a", "opt-ghost"], "disposition": "merge"}
    with pytest.raises(CompareRowsError, match="not in this"):
        build_compare_rows([a, b], study_id="study-1", revision=1, duplicate_records=[record])


# ---------------------------------------------------------------------------
# common_scale fits both geometries (the only numbers the comparison computes).
# ---------------------------------------------------------------------------


def test_common_scale_fits_both_geometries() -> None:
    a = _results(option_id="opt-a", results_id="res-a", ftf=10.0)
    b = _results(option_id="opt-b", results_id="res-b", ftf=12.0)
    doc = build_compare_rows([a, b], study_id="study-1", revision=1)

    scale = doc["common_scale"]
    assert scale["status"] == "available"
    assert scale["units"] == "feet"
    # Both options share the same lot, so each option's extent equals the lot extent.
    width_a, height_a = _lot_extent(a["geometry"])
    width_b, height_b = _lot_extent(b["geometry"])
    per = {entry["option_id"]: entry for entry in scale["per_option"]}
    assert per["opt-a"]["width_ft"] == width_a and per["opt-a"]["height_ft"] == height_a
    assert per["opt-b"]["width_ft"] == width_b and per["opt-b"]["height_ft"] == height_b
    # fits_extent is the per-dimension maximum, so both plans fit inside it.
    assert scale["fits_extent"]["width_ft"] == max(width_a, width_b)
    assert scale["fits_extent"]["height_ft"] == max(height_a, height_b)
    assert per["opt-a"]["crs"] == "local_feet"


def test_common_scale_not_available_when_an_option_has_no_geometry() -> None:
    on = _results(option_id="opt-on", results_id="res-on", env=_ON)
    off = _results(option_id="opt-off", results_id="res-off", env=_OFF)  # geometry not_available
    doc = build_compare_rows([on, off], study_id="study-1", revision=1)
    scale = doc["common_scale"]
    assert scale["status"] == "not_available"
    assert "opt-off" in scale["reason"]
    assert scale["reason_kind"] == off["geometry"]["reason_kind"]


# ---------------------------------------------------------------------------
# Contract registration and fixtures.
# ---------------------------------------------------------------------------


def test_compare_rows_is_registered_as_a_study_contract() -> None:
    assert "compare_rows" in STUDY_CONTRACT_STEMS


def test_bundled_schema_is_byte_identical_to_canonical() -> None:
    canonical = (
        _REPO_ROOT / "packages" / "contracts" / "schemas" / "v1" / "compare_rows.schema.json"
    ).read_bytes()
    bundled = (
        _REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1"
        / "compare_rows.schema.json"
    ).read_bytes()
    assert canonical == bundled


@pytest.mark.parametrize(
    "name",
    ["two_options_with_duplicate.json", "one_option_without_geometry.json"],
)
def test_valid_fixtures_validate(name: str) -> None:
    doc = json.loads((_FIXTURES / "valid" / "compare_rows" / name).read_text("utf-8"))
    validate_compare_rows_document(doc)  # raises on any defect


@pytest.mark.parametrize(
    "name",
    [
        "single_option.json",
        "blank_cell.json",
        "cell_unknown_status.json",
        "row_missing_a_cell.json",
        "missing_duplicates.json",
        "duplicate_record_without_option_ids.json",
    ],
)
def test_invalid_fixtures_fail(name: str) -> None:
    from app.contracts.study_contracts import StudyContractError

    doc = json.loads((_FIXTURES / "invalid" / "compare_rows" / name).read_text("utf-8"))
    # Drop the fixture-only annotation so the failure proven here is the STATED structural
    # defect, not merely the presence of _expected_failure (which the validator also rejects).
    doc.pop("_expected_failure", None)
    with pytest.raises(StudyContractError):
        validate_compare_rows_document(doc)
