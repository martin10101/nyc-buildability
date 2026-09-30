"""A-02a (D-090; queue A-02 first slice; RECONCILIATION C-1, C-2, L-1): R6B floor area (ZR 23-22)
and heights (ZR 23-432) on the benchmark lot 215-16 Northern Blvd (R6B / C2-2 corner, 10,075 sq ft).

Three independent sources are compared, never one against itself:

* the EXPECTED values come from the benchmark contract fixture
  (``packages/contracts/fixtures/valid/benchmark_lot/northern_blvd_215_16_queens_4073340070.json``,
  transcribed from the competitor review section A);
* the LEGAL TEXT comes from the committed ZR snapshots (``zr-23-22``, ``zr-23-432``);
* the ENGINE values come from evaluating the draft rules through the real registry.

Every expected number below is loaded from the fixture or the snapshot; none is restated as a
literal (the M5-T004 tautology finding). Both new rules are lane A behavior (``lane_flag: "A"``):
they are indexed only when ``LANE_A_ENABLED`` is on, so each registry here names its environment.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.rules import RuleRegistry
from app.rules import coverage as cov

_REPO_ROOT = Path(__file__).resolve().parents[4]
_RULESET_DIR = Path(__file__).resolve().parents[2] / "app" / "rules" / "rulesets"
_DOCS_SNAPSHOTS = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"
_BENCHMARK = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)

_ON = {"LANE_A_ENABLED": "1"}
_HEIGHT = "r6b-height"
_QUALIFYING_FAR = "r6b-qualifying-housing-far"
_STANDARD_FAR = "r6-r12-residential-far"
_WIDE_STREET_FAR = "r6-r7-r8-wide-street-conditional-far"
_NEW_RULE_FILES = {
    _HEIGHT: "r6b_height.rule.json",
    _QUALIFYING_FAR: "r6b_qualifying_housing_far.rule.json",
}

# Benchmark fixture key -> (rule id, rule output). The mapping is the claim under test.
_FAR_OUTPUTS = {
    "max_residential_far": (_STANDARD_FAR, "max_residential_far"),
    "max_residential_floor_area": (_STANDARD_FAR, "max_residential_floor_area_sq_ft"),
    "max_residential_far_qualifying_affordable_or_senior": (
        _QUALIFYING_FAR, "qualifying_max_residential_far"),
    "max_residential_floor_area_qualifying_affordable_or_senior": (
        _QUALIFYING_FAR, "qualifying_max_residential_floor_area_sq_ft"),
}
_HEIGHT_OUTPUTS = {
    "min_base_height": "min_base_height",
    "max_base_height": "max_base_height",
    "max_building_height": "max_building_height",
    "max_base_height_qualifying_affordable_or_senior": "qualifying_max_base_height",
    "max_building_height_qualifying_affordable_or_senior": "qualifying_max_building_height",
}
# Benchmark height key -> ZR 23-432 snapshot column (R6B row).
_HEIGHT_COLUMNS = {
    "min_base_height": "min_base_height_ft",
    "max_base_height": "standard_max_base_height_ft",
    "max_building_height": "standard_max_building_height_ft",
    "max_base_height_qualifying_affordable_or_senior": "qualifying_max_base_height_ft",
    "max_building_height_qualifying_affordable_or_senior": "qualifying_max_building_height_ft",
}
# Height rule parameter -> ZR 23-432 snapshot column.
_HEIGHT_PARAMS = {
    "min_base_height_ft": "min_base_height_ft",
    "standard_max_base_height_ft": "standard_max_base_height_ft",
    "standard_max_building_height_ft": "standard_max_building_height_ft",
    "qualifying_max_base_height_ft": "qualifying_max_base_height_ft",
    "qualifying_max_building_height_ft": "qualifying_max_building_height_ft",
}


# --------------------------------------------------------------------------
# Loaders.
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def registry() -> RuleRegistry:
    """The production rulesets with lane A on, resolved against the PACKAGED snapshot bundle (the
    installed-wheel path; the bundle is byte-identical to docs/ per test_zr_snapshot_bundle)."""
    return RuleRegistry(env=_ON).load()


def _expected() -> dict[str, dict]:
    doc = json.loads(_BENCHMARK.read_text("utf-8"))
    return {item["key"]: item for item in doc["expected_values"]}


def _snapshot(snapshot_id: str) -> dict:
    return json.loads((_DOCS_SNAPSHOTS / f"{snapshot_id}.snapshot.json").read_text("utf-8"))


def _rows_for(snapshot_id: str, district: str) -> list[dict]:
    return [r for r in _snapshot(snapshot_id)["table"]["rows"] if district in r["districts"]]


def _rule_doc(rule_id: str) -> dict:
    return json.loads((_RULESET_DIR / _NEW_RULE_FILES[rule_id]).read_text("utf-8"))


def _params(rule_id: str) -> dict:
    return {p["name"]: p["value"] for p in _rule_doc(rule_id)["parameters"]}


def _benchmark_district_and_area() -> tuple[str, float]:
    expected = _expected()
    return expected["zoning_district"]["value"], float(expected["lot_area"]["value"])


def _height_inputs(*, overlay: bool = True, special: bool = False) -> dict:
    district, _ = _benchmark_district_and_area()
    return {"zoning_district": district, "overlay_present": overlay,
            "special_district_present": special}


def _applied_ids(trace: dict) -> set[str]:
    return {e["id"] for e in trace["exceptions_applied"]}


# --------------------------------------------------------------------------
# Source fidelity: the captured ZR text states every benchmark value exactly.
# --------------------------------------------------------------------------

def test_benchmark_fixture_is_the_r6b_10075_lot() -> None:
    district, area = _benchmark_district_and_area()
    assert district == "R6B"
    assert area == 10075


def test_zr_23_432_r6b_row_states_every_benchmark_height() -> None:
    """One R6B row, no footnote marker, and each of the five heights equals the benchmark."""
    rows = _rows_for("zr-23-432", "R6B")
    assert len(rows) == 1 and rows[0]["districts"] == ["R6B"]
    assert "district_footnotes" not in rows[0]
    expected = _expected()
    for key, column in _HEIGHT_COLUMNS.items():
        assert Decimal(rows[0][column]) == Decimal(str(expected[key]["value"])), key
        assert expected[key]["source"]["ref"] == "ZR 23-432"


def test_zr_23_22_r6b_row_states_both_benchmark_far_values() -> None:
    rows = _rows_for("zr-23-22", "R6B")
    assert len(rows) == 1 and rows[0]["districts"] == ["R6B"]
    assert not rows[0].get("district_footnotes") and not rows[0].get("value_footnotes")
    expected = _expected()
    assert Decimal(rows[0]["standard_residences"]) == Decimal(
        str(expected["max_residential_far"]["value"]))
    assert Decimal(rows[0]["qualifying_affordable_or_senior_housing"]) == Decimal(
        str(expected["max_residential_far_qualifying_affordable_or_senior"]["value"]))


def test_rule_parameters_are_byte_equal_to_the_snapshot_rows() -> None:
    row_432 = _rows_for("zr-23-432", "R6B")[0]
    height_params = _params(_HEIGHT)
    assert set(height_params) == set(_HEIGHT_PARAMS)
    for name, column in _HEIGHT_PARAMS.items():
        assert Decimal(str(height_params[name])) == Decimal(row_432[column]), name
    row_22 = _rows_for("zr-23-22", "R6B")[0]
    qualifying = _params(_QUALIFYING_FAR)["qualifying_far_by_district"]
    assert set(qualifying) == set(_rule_doc(_QUALIFYING_FAR)["applicability"]["all"][0]["values"])
    assert Decimal(str(qualifying["R6B"])) == Decimal(
        row_22["qualifying_affordable_or_senior_housing"])


def test_citations_quote_the_snapshot_verbatim_and_bind_its_digest() -> None:
    for rule_id in _NEW_RULE_FILES:
        for citation in _rule_doc(rule_id)["citations"]:
            snap = _snapshot(citation["snapshot_id"])
            assert citation["quote"] in snap["verbatim_excerpt"]
            assert citation["content_digest_sha256"] == snap["content_digest_sha256"]
            assert citation["last_amended"] == snap["source"]["section_last_amended"]


def test_zr_23_432_snapshot_provenance_is_complete() -> None:
    snap = _snapshot("zr-23-432")
    source = snap["source"]
    assert source["request_url"].startswith("https://zoningresolution.planning.nyc.gov/")
    assert source["http_status"] == 200
    assert len(source["raw_html_sha256"]) == 64
    assert source["section_last_amended"] == "2024-12-05"
    assert source["raw_html_verified"] is False
    assert snap["cross_check"]["result"] == "match"
    assert len(snap["cross_check"]["raw_pdf_sha256"]) == 64
    assert snap["extraction_status"] == "extracted_draft"
    excerpt_digest = hashlib.sha256(snap["verbatim_excerpt"].encode("utf-8")).hexdigest()
    assert snap["content_digest_sha256"] == excerpt_digest


# --------------------------------------------------------------------------
# C-2: both allowances computed, separately labeled.
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "program", [None, "qualifying_affordable_housing", "qualifying_senior_housing"]
)
def test_c2_benchmark_standard_and_qualifying_allowances(registry, program) -> None:
    """20,150 sq ft (2.00) from the standard rule and 24,180 sq ft (2.40) from the qualifying
    rule, for the benchmark district and lot area."""
    district, area = _benchmark_district_and_area()
    inputs = {"zoning_district": district, "lot_area_sq_ft": area}
    if program is not None:
        inputs["housing_program"] = program
    expected = _expected()
    for key, (rule_id, output) in _FAR_OUTPUTS.items():
        trace = registry.evaluate(rule_id, inputs).export()
        assert trace["applicability_outcome"] is True
        assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
        assert trace["outputs"][output] == float(expected[key]["value"]), key


def test_c2_the_two_allowances_never_share_a_label_or_family(registry) -> None:
    standard = registry.rule(_STANDARD_FAR)
    qualifying = registry.rule(_QUALIFYING_FAR)
    assert not set(standard.output_names()) & set(qualifying.output_names())
    assert standard.family == "residential_far"
    assert qualifying.family == "residential_far_qualifying_housing"
    # The residential_far family (read by the integration, the scenario builder and the checks)
    # is exactly what it was: the qualifying alternative is not in it.
    assert _QUALIFYING_FAR not in registry.family_coverage("residential_far")["rule_ids"]
    district, area = _benchmark_district_and_area()
    trace = registry.evaluate(_QUALIFYING_FAR, {"zoning_district": district,
                                                "lot_area_sq_ft": area}).export()
    applied = {e["id"]: e for e in trace["exceptions_applied"]}
    assert applied["qualifying_housing_eligibility"]["effect"] == "conditional_alternative"


def test_c2_standard_program_makes_the_alternative_not_applicable(registry) -> None:
    district, area = _benchmark_district_and_area()
    trace = registry.evaluate(_QUALIFYING_FAR, {
        "zoning_district": district, "lot_area_sq_ft": area,
        "housing_program": "standard_residence"}).export()
    assert trace["applicability_outcome"] is False
    assert trace["coverage_status"] == cov.COVERAGE_NOT_APPLICABLE
    assert trace["outputs"] == {}


def test_c2_qualifying_rule_is_r6b_only(registry) -> None:
    for district in ("R6", "R6A", "R6D", "R7B", "R5"):
        trace = registry.evaluate(
            _QUALIFYING_FAR, {"zoning_district": district, "lot_area_sq_ft": 10_000}).export()
        assert trace["applicability_outcome"] is False, district
        assert trace["outputs"] == {}


@pytest.mark.parametrize("bad_area", [0, -1, float("nan")])
def test_c2_qualifying_rule_fails_closed_on_bad_lot_area(registry, bad_area) -> None:
    result = registry.evaluate(_QUALIFYING_FAR, {"zoning_district": "R6B",
                                                 "lot_area_sq_ft": bad_area})
    assert result.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert result.export()["outputs"] == {}


# --------------------------------------------------------------------------
# R6B has no wide-street increase (kept explicit).
# --------------------------------------------------------------------------

def test_r6b_has_no_wide_street_increase(registry) -> None:
    wide = registry.rule(_WIDE_STREET_FAR)
    assert "R6B" not in wide.applicability["values"]
    assert "R6B" not in wide.parameters["wide_street_far_by_district"]
    trace = registry.evaluate(_WIDE_STREET_FAR, {"zoning_district": "R6B",
                                                 "lot_area_sq_ft": 10_075}).export()
    assert trace["applicability_outcome"] is False
    assert "wide_street_far_by_district" not in registry.rule(_STANDARD_FAR).parameters
    q_trace = registry.evaluate(_QUALIFYING_FAR, {"zoning_district": "R6B",
                                                  "lot_area_sq_ft": 10_075}).export()
    assert "no_wide_street_increase" in _applied_ids(q_trace)
    expected = _expected()["wide_street_far_increase"]
    assert expected["value"] == "none" and expected["source"]["ref"] == "ZR 23-22"


# --------------------------------------------------------------------------
# C-1: the ONE R6B height lookup.
# --------------------------------------------------------------------------

def test_c1_benchmark_heights_from_the_one_lookup(registry) -> None:
    """The benchmark lot (R6B with a C2-2 overlay, no special district in its record): all five
    heights come from r6b-height, labeled, conditional, with the overlay note attached."""
    trace = registry.evaluate(_HEIGHT, _height_inputs(overlay=True)).export()
    assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
    expected = _expected()
    for key, output in _HEIGHT_OUTPUTS.items():
        assert trace["outputs"][output] == float(expected[key]["value"]), key
    applied = _applied_ids(trace)
    assert {"qualifying_housing_heights", "no_street_width_dependence",
            "setback_per_23_433_not_encoded", "commercial_overlay_not_captured"} <= applied


def test_c1_overlay_note_only_when_an_overlay_is_mapped(registry) -> None:
    trace = registry.evaluate(_HEIGHT, _height_inputs(overlay=False)).export()
    assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert "commercial_overlay_not_captured" not in _applied_ids(trace)


def test_c1_no_other_rule_emits_a_height_for_r6b(registry) -> None:
    """Across the WHOLE registry, the only rule applicable to R6B that emits any output in feet
    is r6b-height - for the benchmark facts and for a broad superset of attested facts."""
    superset = {
        **_height_inputs(), "lot_area_sq_ft": 10_075, "street_width_class": "wide",
        "building_type": "attached", "site_class": "standard_zoning_lot",
        "qualifying_residential_site": True, "historic_district": False, "large_site": False,
        "housing_program": "qualifying_affordable_housing",
    }
    for inputs in (_height_inputs(), superset):
        emitting = set()
        for rule_id in registry.rule_ids():
            rule = registry.rule(rule_id)
            feet = {o.name for o in rule.outputs if o.unit == "feet"}
            trace = registry.evaluate(rule_id, inputs).export()
            if feet and trace["applicability_outcome"]:
                emitting.add(rule_id)
        assert emitting == {_HEIGHT}


def test_c1_special_district_or_unattested_inputs_fail_closed(registry) -> None:
    special = registry.evaluate(_HEIGHT, _height_inputs(special=True))
    assert special.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    unattested = registry.evaluate(_HEIGHT, {"zoning_district": "R6B"})
    assert unattested.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


def test_c1_height_rule_is_r6b_only(registry) -> None:
    for district in ("R6", "R6A", "R6D", "R5", "R7B"):
        inputs = {**_height_inputs(), "zoning_district": district}
        assert registry.evaluate(_HEIGHT, inputs).export()["applicability_outcome"] is False


# --------------------------------------------------------------------------
# Lifecycle, lane flag, determinism.
# --------------------------------------------------------------------------

def test_new_rules_are_draft_needs_review_and_lane_a_gated(registry) -> None:
    for rule_id in _NEW_RULE_FILES:
        doc = _rule_doc(rule_id)
        assert doc["status"] == "needs_review"
        assert doc["release"]["independent_review"] == "pending"
        assert doc["release"]["qualified_human_approval"] == "pending"
        assert doc["lane_flag"] == "A"
        assert doc["effective_from"] == "2024-12-05"
        result = registry.evaluate(rule_id, {**_height_inputs(), "lot_area_sq_ft": 10_075})
        assert result.coverage_status != cov.COVERAGE_VERIFIED


@pytest.mark.parametrize("env", [{}, {"LANE_A_ENABLED": ""}, {"LANE_A_ENABLED": "maybe"},
                                 {"LANE_A_ENABLED": "0"}, {"LANE_B_ENABLED": "1"}])
def test_flag_off_the_new_rules_are_validated_but_not_indexed(env) -> None:
    off = RuleRegistry(env=env).load()
    gated = off.gated_off_rule_ids()
    # A-02b adds more lane A rules; every gated rule is lane A and these two are among them.
    assert set(_NEW_RULE_FILES) <= set(gated) and set(gated.values()) == {"A"}
    for rule_id in _NEW_RULE_FILES:
        assert rule_id not in off.rule_ids()
        with pytest.raises(KeyError):
            off.rule(rule_id)
    assert "residential_far_qualifying_housing" not in off.families()
    assert _HEIGHT not in off.family_coverage("residential_height_setback")["rule_ids"]


def test_a_gated_rule_is_still_validated_with_its_flag_off(tmp_path) -> None:
    """The gate hides nothing broken: an invalid lane-gated rule fails the load even when its
    lane is off, and an unknown lane letter is a schema violation."""
    from app.rules.dsl import DSLError, build_rule_definition
    from app.rules.snapshots import SnapshotError, SnapshotStore

    broken = _rule_doc(_HEIGHT)
    broken["citations"][0]["snapshot_id"] = "zr-does-not-exist"
    (tmp_path / "r6b_height.rule.json").write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(SnapshotError):
        RuleRegistry(tmp_path, env={}).load()

    unknown_lane = {**_rule_doc(_HEIGHT), "lane_flag": "F"}
    with pytest.raises(DSLError, match="lane_flag"):
        build_rule_definition(unknown_lane, SnapshotStore().load())


def test_flag_default_reads_the_process_environment(monkeypatch) -> None:
    monkeypatch.delenv("LANE_A_ENABLED", raising=False)
    assert _HEIGHT not in RuleRegistry().load().rule_ids()
    monkeypatch.setenv("LANE_A_ENABLED", "true")
    assert _HEIGHT in RuleRegistry().load().rule_ids()


def test_flag_on_indexes_both_rules(registry) -> None:
    assert registry.gated_off_rule_ids() == {}
    assert _HEIGHT in registry.family_coverage("residential_height_setback")["rule_ids"]
    assert registry.family_coverage("residential_far_qualifying_housing")["rule_ids"] == [
        _QUALIFYING_FAR]


def test_evaluation_is_byte_deterministic(registry) -> None:
    inputs = {**_height_inputs(), "lot_area_sq_ft": 10_075}
    for rule_id in _NEW_RULE_FILES:
        first = json.dumps(registry.evaluate(rule_id, inputs).export(), sort_keys=True)
        second = json.dumps(registry.evaluate(rule_id, inputs).export(), sort_keys=True)
        assert first == second


def test_before_the_amendment_date_nothing_is_emitted(registry) -> None:
    inputs = {**_height_inputs(), "lot_area_sq_ft": 10_075}
    for rule_id in _NEW_RULE_FILES:
        result = registry.evaluate(rule_id, inputs, as_of_date="2024-12-04")
        assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
        assert result.export()["outputs"] == {}
