"""A-02b (D-090; queue A-02 second slice; RECONCILIATION C-12): R6B lot coverage (ZR 23-362),
the corner rear-yard waiver (ZR 23-344(a)) and dwelling units (ZR 23-52) on the benchmark lot
215-16 Northern Blvd (R6B / C2-2 corner, 10,075 sq ft).

Three independent sources are compared, never one against itself:

* the EXPECTED values come from the benchmark contract fixture (competitor review section A);
* the LEGAL TEXT comes from the committed ZR snapshots (``zr-23-362``, ``zr-23-344``,
  ``zr-23-52``; ``zr-11-25`` for the R6 -> R6B suffix reading);
* the ENGINE values come from evaluating the draft rules through the real registry.

Site facts the rules consume as inputs (lot type, the 100-ft test, the intersection angle, the
special-density-area status) are NOT in the benchmark fixture: they are Lane B facts. Tests that
need them name them as test inputs (``_SITE_FACTS``); the one value not attested anywhere - the
angle of 215 Place and Northern Blvd - is a test input only, never an asserted fact.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from fractions import Fraction
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
_COVERAGE = "r6b-lot-coverage"
_REAR_YARD = "r6b-rear-yard-corner-waiver"
_UNITS = "r6b-dwelling-units"
_STANDARD_FAR = "r6-r12-residential-far"
_RULE_FILES = {
    _COVERAGE: "r6b_lot_coverage.rule.json",
    _REAR_YARD: "r6b_rear_yard_corner_waiver.rule.json",
    _UNITS: "r6b_dwelling_units.rule.json",
}
_SNAPSHOTS = ("zr-23-362", "zr-23-344", "zr-23-52")

#: Lane B site facts the rules consume (not in the benchmark fixture). The lot type is taken
#: from the fixture below; the angle is a TEST INPUT (the real angle is B-01 data).
_SITE_FACTS = {
    "within_100_ft_of_street_line_intersection": True,
    "street_line_intersection_angle_degrees": 90,
    "special_density_area": False,
}


# --------------------------------------------------------------------------
# Loaders.
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def registry() -> RuleRegistry:
    return RuleRegistry(env=_ON).load()


def _expected() -> dict[str, dict]:
    doc = json.loads(_BENCHMARK.read_text("utf-8"))
    return {item["key"]: item for item in doc["expected_values"]}


def _snapshot(snapshot_id: str) -> dict:
    return json.loads((_DOCS_SNAPSHOTS / f"{snapshot_id}.snapshot.json").read_text("utf-8"))


def _provision(snapshot_id: str, paragraph: str) -> dict:
    return next(p for p in _snapshot(snapshot_id)["provisions"] if p["paragraph"] == paragraph)


def _rule_doc(rule_id: str) -> dict:
    return json.loads((_RULESET_DIR / _RULE_FILES[rule_id]).read_text("utf-8"))


def _params(rule_id: str) -> dict:
    return {p["name"]: p["value"] for p in _rule_doc(rule_id)["parameters"]}


def _benchmark_district() -> str:
    return _expected()["zoning_district"]["value"]


def _base_facts() -> dict:
    """The benchmark lot's zoning facts: R6B with a mapped C2-2 overlay, no special district."""
    expected = _expected()
    return {"zoning_district": expected["zoning_district"]["value"],
            "overlay_present": bool(expected["commercial_overlay"]["value"]),
            "special_district_present": False}


def _coverage_inputs(**overrides) -> dict:
    return {**_base_facts(), "lot_type": _expected()["lot_type"]["value"], **overrides}


def _yard_inputs(**overrides) -> dict:
    return {**_base_facts(),
            "within_100_ft_of_street_line_intersection":
                _SITE_FACTS["within_100_ft_of_street_line_intersection"],
            "street_line_intersection_angle_degrees":
                _SITE_FACTS["street_line_intersection_angle_degrees"],
            **overrides}


def _standard_floor_area(registry: RuleRegistry) -> float:
    """The dividend: the residential_far family's own output for the benchmark lot."""
    area = float(_expected()["lot_area"]["value"])
    trace = registry.evaluate(_STANDARD_FAR, {"zoning_district": _benchmark_district(),
                                              "lot_area_sq_ft": area}).export()
    return trace["outputs"]["max_residential_floor_area_sq_ft"]


def _units_inputs(floor_area: float, **overrides) -> dict:
    return {"zoning_district": _benchmark_district(),
            "max_residential_floor_area_sq_ft": floor_area,
            "housing_program": "standard_residence",
            "special_density_area": _SITE_FACTS["special_density_area"],
            "special_district_present": False, **overrides}


def _applied_ids(trace: dict) -> set[str]:
    return {e["id"] for e in trace["exceptions_applied"]}


# --------------------------------------------------------------------------
# Source fidelity: the captured ZR text states every encoded value exactly.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("snapshot_id", _SNAPSHOTS)
def test_snapshot_provenance_is_complete(snapshot_id) -> None:
    snap = _snapshot(snapshot_id)
    source = snap["source"]
    assert source["request_url"] == (
        "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/"
        + snapshot_id.removeprefix("zr-"))
    assert source["http_status"] == 200
    assert len(source["raw_html_sha256"]) == 64
    assert source["section_last_amended"] == "2024-12-05"
    assert source["raw_html_verified"] is False
    cross = snap["cross_check"]
    assert cross["result"] == "match" and cross["channel"] == "print_pdf"
    assert cross["request_url"].endswith(f"/entityprint/pdf/node/{source['portal_node_id']}")
    assert len(cross["raw_pdf_sha256"]) == 64
    assert snap["extraction_status"] == "extracted_draft"
    digest = hashlib.sha256(snap["verbatim_excerpt"].encode("utf-8")).hexdigest()
    assert snap["content_digest_sha256"] == digest
    for provision in snap["provisions"]:
        assert provision["verbatim_source_quote"] in snap["verbatim_excerpt"]


def test_zr_23_362_states_the_benchmark_corner_coverage_and_the_rule_matches() -> None:
    provision = _provision("zr-23-362", "(a)")
    assert "#corner lots# shall be 100 percent" in provision["verbatim_source_quote"]
    assert "#interior lots# or #through lots# shall be 80 percent" in provision[
        "verbatim_source_quote"]
    values = provision["values"]
    expected = _expected()["max_lot_coverage"]
    assert expected["source"]["ref"] == "ZR 23-362" and expected["unit"] == "percent"
    assert Decimal(values["corner_lot_max_residential_lot_coverage_percent"]) == Decimal(
        str(expected["value"]))
    by_type = _params(_COVERAGE)["max_residential_lot_coverage_percent_by_lot_type"]
    assert set(by_type) == set(next(i for i in _rule_doc(_COVERAGE)["inputs"]
                                    if i["name"] == "lot_type")["enum"])
    for lot_type in ("corner", "interior", "through"):
        stated = values[f"{lot_type}_lot_max_residential_lot_coverage_percent"]
        assert Decimal(str(by_type[lot_type])) == Decimal(stated), lot_type


def test_zr_23_344a_states_the_waiver_and_the_rule_encodes_both_conditions() -> None:
    provision = _provision("zr-23-344", "(a)")
    assert "no #rear yard# shall be required within 100 feet" in provision["verbatim_source_quote"]
    values = provision["values"]
    expected = _expected()["rear_yard_within_100_ft_of_corner"]
    assert expected["value"] == "not required" and expected["source"]["ref"] == "ZR 23-344(a)"
    applicability = _rule_doc(_REAR_YARD)["applicability"]["all"]
    angle = next(p for p in applicability if p.get("op") == "compare")
    assert angle["input"] == "street_line_intersection_angle_degrees"
    assert angle["compare"] == "le"  # "135 degrees or less"
    assert "135 degrees or less" in values["angle_condition_text"]
    assert Decimal(str(angle["value"])) == Decimal(values["max_intersection_angle_degrees"])
    within = next(p for p in applicability
                  if p.get("input") == "within_100_ft_of_street_line_intersection")
    assert within == {"op": "equals", "input": "within_100_ft_of_street_line_intersection",
                      "value": True}
    assert values["distance_from_point_of_intersection_ft"] == "100"
    assert _params(_REAR_YARD)["rear_yard_required_when_waived"] == 0


def test_zr_23_52_states_the_factor_and_the_three_quarters_rule() -> None:
    provision = _provision("zr-23-52", "(b)")
    quote = provision["verbatim_source_quote"]
    assert "factor shall be 680" in quote
    assert "Fractions equal to or greater than three-quarters" in quote
    values = provision["values"]
    expected = _expected()
    assert expected["dwelling_unit_factor"]["source"]["ref"] == "ZR 23-52"
    params = _params(_UNITS)
    assert params["dwelling_unit_factor"] == int(values["dwelling_unit_factor"]) == expected[
        "dwelling_unit_factor"]["value"]
    assert values["fraction_counted_as_one_dwelling_unit_text"] == "three-quarters"
    assert Fraction(str(params["fraction_counted_as_one_dwelling_unit"])) == Fraction(3, 4)
    assert Fraction(values["fraction_counted_as_one_dwelling_unit"]) == Fraction(3, 4)
    assert expected["dwelling_unit_rounding_rule"]["value"] == "rounds up only at .75 or more"


@pytest.mark.parametrize("rule_id", sorted(_RULE_FILES))
def test_citations_quote_the_snapshot_verbatim_and_bind_its_digest(rule_id) -> None:
    for citation in _rule_doc(rule_id)["citations"]:
        snap = _snapshot(citation["snapshot_id"])
        assert citation["quote"] in snap["verbatim_excerpt"]
        assert citation["content_digest_sha256"] == snap["content_digest_sha256"]
        assert citation["last_amended"] == snap["source"]["section_last_amended"]


@pytest.mark.parametrize("snapshot_id", _SNAPSHOTS)
def test_r6b_is_reached_through_zr_11_25_and_every_rule_says_so(snapshot_id) -> None:
    """None of the three sections names R6B; each lists R6 and no separate suffixed-district
    provision, so the reading rests on ZR 11-25's text - flagged on every result."""
    district_line = _snapshot(snapshot_id)["verbatim_excerpt"].split("\n\n")[1]
    districts = district_line.split()
    assert "R6" in districts and "R6B" not in districts
    suffix_rule = _snapshot("zr-11-25")["verbatim_excerpt"]
    assert "If a section lists an R4 District, therefore, the provisions of that section shall " \
           "also apply to R4-1, R4A and R4B Districts" in suffix_rule
    for rule_id in _RULE_FILES:
        exc = next(e for e in _rule_doc(rule_id)["exceptions"]
                   if e["id"] == "suffix_inheritance_zr_11_25")
        assert exc["condition"] is None and exc["citation_ref"] == "zr-11-25"


# --------------------------------------------------------------------------
# Lot coverage (ZR 23-362(a)).
# --------------------------------------------------------------------------

def test_benchmark_corner_lot_coverage_is_100_percent(registry) -> None:
    assert _expected()["lot_type"]["value"] == "corner"
    trace = registry.evaluate(_COVERAGE, _coverage_inputs()).export()
    assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert trace["data_completeness"] == cov.COMPLETENESS_COMPLETE
    assert trace["outputs"] == {
        "max_residential_lot_coverage_percent": float(_expected()["max_lot_coverage"]["value"])}
    assert {"suffix_inheritance_zr_11_25", "standard_lots_only",
            "commercial_overlay_not_captured"} <= _applied_ids(trace)
    assert "interior_or_through_special_rules_not_captured" not in _applied_ids(trace)
    assert {c["snapshot_id"] for c in trace["citations"]} == {"zr-23-362", "zr-11-25"}


@pytest.mark.parametrize("lot_type", ["interior", "through"])
def test_interior_and_through_lots_are_80_percent_with_the_23_363_note(registry, lot_type) -> None:
    trace = registry.evaluate(_COVERAGE, _coverage_inputs(lot_type=lot_type)).export()
    assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert trace["outputs"]["max_residential_lot_coverage_percent"] == 80.0
    assert "interior_or_through_special_rules_not_captured" in _applied_ids(trace)


def test_unknown_lot_type_gives_no_coverage_and_names_the_input(registry) -> None:
    inputs = _coverage_inputs()
    del inputs["lot_type"]
    trace = registry.evaluate(_COVERAGE, inputs).export()
    assert trace["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert trace["data_completeness"] == cov.COMPLETENESS_MISSING_CRITICAL
    assert trace["outputs"] == {}
    assert any("lot_type" in note for note in trace["notes"])


def test_an_unlisted_lot_type_is_rejected_not_guessed(registry) -> None:
    trace = registry.evaluate(_COVERAGE, _coverage_inputs(lot_type="mixed")).export()
    assert trace["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert trace["outputs"] == {}
    assert trace["input_validation"]["valid"] is False


# --------------------------------------------------------------------------
# Rear-yard corner waiver (ZR 23-344(a)).
# --------------------------------------------------------------------------

def test_benchmark_rear_yard_is_not_required_within_100_ft_of_the_corner(registry) -> None:
    trace = registry.evaluate(_REAR_YARD, _yard_inputs()).export()
    assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert trace["applicability_outcome"] is True
    # 0 = "not required", the benchmark's expected value.
    assert _expected()["rear_yard_within_100_ft_of_corner"]["value"] == "not required"
    assert trace["outputs"] == {"rear_yard_required_within_100_ft_of_corner": 0.0}
    assert {"suffix_inheritance_zr_11_25", "only_within_100_ft_of_the_intersection",
            "commercial_overlay_not_captured"} <= _applied_ids(trace)


@pytest.mark.parametrize(
    ("angle", "waived"),
    [(135, True), (134.9999, True), (90, True), (45, True), (135.0001, False), (150, False)],
)
def test_angle_boundary_is_135_degrees_or_less(registry, angle, waived) -> None:
    trace = registry.evaluate(
        _REAR_YARD, _yard_inputs(street_line_intersection_angle_degrees=angle)).export()
    assert trace["applicability_outcome"] is waived
    if waived:
        assert trace["outputs"] == {"rear_yard_required_within_100_ft_of_corner": 0.0}
    else:
        assert trace["coverage_status"] == cov.COVERAGE_NOT_APPLICABLE
        assert trace["outputs"] == {}


def test_beyond_100_ft_the_waiver_does_not_apply_and_nothing_is_emitted(registry) -> None:
    trace = registry.evaluate(
        _REAR_YARD, _yard_inputs(within_100_ft_of_street_line_intersection=False)).export()
    assert trace["coverage_status"] == cov.COVERAGE_NOT_APPLICABLE
    assert trace["outputs"] == {}


@pytest.mark.parametrize(
    "missing",
    [("within_100_ft_of_street_line_intersection",), ("street_line_intersection_angle_degrees",),
     ("within_100_ft_of_street_line_intersection", "street_line_intersection_angle_degrees")],
)
def test_unknown_geometry_means_no_rear_yard_result_with_the_reason(registry, missing) -> None:
    inputs = _yard_inputs()
    for name in missing:
        del inputs[name]
    trace = registry.evaluate(_REAR_YARD, inputs).export()
    assert trace["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert trace["data_completeness"] == cov.COMPLETENESS_MISSING_CRITICAL
    assert trace["outputs"] == {}
    note = next(n for n in trace["notes"] if n.startswith("missing required input(s)"))
    for name in missing:
        assert name in note


@pytest.mark.parametrize("angle", [0, -10, 180, 400, float("nan")])
def test_an_impossible_angle_fails_closed(registry, angle) -> None:
    trace = registry.evaluate(
        _REAR_YARD, _yard_inputs(street_line_intersection_angle_degrees=angle)).export()
    assert trace["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert trace["outputs"] == {}


# --------------------------------------------------------------------------
# Dwelling units (ZR 23-52) - C-12: the estimate with its formula.
# --------------------------------------------------------------------------

def test_c12_benchmark_units_29_with_the_formula(registry) -> None:
    expected = _expected()
    floor_area = _standard_floor_area(registry)
    assert floor_area == float(expected["max_residential_floor_area"]["value"])  # 20,150
    trace = registry.evaluate(_UNITS, _units_inputs(floor_area)).export()
    assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert trace["data_completeness"] == cov.COMPLETENESS_COMPLETE
    outputs = trace["outputs"]
    assert outputs["max_dwelling_units"] == float(expected["dwelling_units_standard"]["value"])
    assert round(outputs["dwelling_units_before_rounding"], 2) == expected[
        "dwelling_units_standard_unrounded"]["value"]
    # The formula travels with the estimate: divide by 680, then the .75 fraction rule.
    divide, threshold = trace["computation_steps"]
    assert (divide["op"], divide["resolved_args"]) == (
        "divide", [floor_area, expected["dwelling_unit_factor"]["value"]])
    assert divide["result"] == outputs["dwelling_units_before_rounding"]
    assert "23-52" in divide["note"]
    assert (threshold["op"], threshold["resolved_args"]) == (
        "round_threshold", [divide["result"], 0.75])
    assert threshold["result"] == outputs["max_dwelling_units"]
    assert "three-quarters" in threshold["note"]
    assert {c["snapshot_id"] for c in trace["citations"]} == {"zr-23-52", "zr-11-25"}


@pytest.mark.parametrize(
    ("floor_area", "units"),
    [
        (20150, 29),        # 29.632 -> 29 (benchmark)
        (19720, 29),        # 29.000 -> 29
        (20223.2, 29),      # 29.74  -> 29
        (20229, 29),        # 29.7485 -> 29
        (20229.99, 29),     # 29.74998... -> 29
        (20230, 30),        # 29.75 exactly -> 30 (equal counts as one)
        (20230.01, 30),     # just above -> 30
        (20399, 30),        # 29.998 -> 30
        (20400, 30),        # 30.000 -> 30
        (510, 1),           # 0.75 -> 1
        (509.99, 0),        # below three-quarters of one unit -> 0
    ],
)
def test_units_round_up_only_at_three_quarters(registry, floor_area, units) -> None:
    trace = registry.evaluate(_UNITS, _units_inputs(floor_area)).export()
    assert trace["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert trace["outputs"]["max_dwelling_units"] == units
    # Independent check of the boundary side from the exact quotient (never from the trace).
    whole, fraction = divmod(Fraction(str(floor_area)) / 680, 1)
    assert units == whole + (1 if fraction >= Fraction(3, 4) else 0)


def test_units_are_one_place_across_the_registry(registry) -> None:
    """C-12: for R6B, only r6b-dwelling-units emits a dwelling-unit output."""
    floor_area = _standard_floor_area(registry)
    superset = {**_coverage_inputs(), **_yard_inputs(), **_units_inputs(floor_area),
                "lot_area_sq_ft": 10_075, "street_width_class": "narrow"}
    emitting = set()
    for rule_id in registry.rule_ids():
        rule = registry.rule(rule_id)
        unit_outputs = {o.name for o in rule.outputs if o.unit in ("dwelling_units", "units")}
        trace = registry.evaluate(rule_id, superset).export()
        if unit_outputs and trace["applicability_outcome"]:
            emitting.add(rule_id)
    assert emitting == {_UNITS}


def test_qualifying_senior_housing_has_no_factor(registry) -> None:
    trace = registry.evaluate(_UNITS, _units_inputs(
        20150, housing_program="qualifying_senior_housing")).export()
    assert trace["coverage_status"] == cov.COVERAGE_NOT_APPLICABLE
    assert trace["outputs"] == {}


def test_special_density_area_has_no_factor(registry) -> None:
    trace = registry.evaluate(_UNITS, _units_inputs(20150, special_density_area=True)).export()
    assert trace["coverage_status"] == cov.COVERAGE_NOT_APPLICABLE
    assert trace["outputs"] == {}


def test_qualifying_affordable_is_computed_but_sent_to_review(registry) -> None:
    trace = registry.evaluate(_UNITS, _units_inputs(
        24180, housing_program="qualifying_affordable_housing")).export()
    assert trace["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert "qualifying_affordable_dividend_to_verify" in _applied_ids(trace)


@pytest.mark.parametrize("missing", ["housing_program", "special_density_area",
                                     "max_residential_floor_area_sq_ft"])
def test_unknown_program_area_or_floor_area_gives_no_estimate(registry, missing) -> None:
    inputs = _units_inputs(20150)
    del inputs[missing]
    trace = registry.evaluate(_UNITS, inputs).export()
    assert trace["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert trace["data_completeness"] == cov.COMPLETENESS_MISSING_CRITICAL
    assert trace["outputs"] == {}
    assert any(missing in note for note in trace["notes"])


@pytest.mark.parametrize("bad", [0, -680, float("nan"), float("inf")])
def test_units_fail_closed_on_a_bad_floor_area(registry, bad) -> None:
    trace = registry.evaluate(_UNITS, _units_inputs(bad)).export()
    assert trace["coverage_status"] == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert trace["outputs"] == {}


# --------------------------------------------------------------------------
# Shared: fail-closed attestations, scope, lifecycle, determinism.
# --------------------------------------------------------------------------

def _inputs_for(rule_id: str, registry: RuleRegistry) -> dict:
    if rule_id == _COVERAGE:
        return _coverage_inputs()
    if rule_id == _REAR_YARD:
        return _yard_inputs()
    return _units_inputs(_standard_floor_area(registry))


@pytest.mark.parametrize("rule_id", sorted(_RULE_FILES))
def test_special_district_or_unattested_special_district_fails_closed(registry, rule_id) -> None:
    inputs = _inputs_for(rule_id, registry)
    special = registry.evaluate(rule_id, {**inputs, "special_district_present": True})
    assert special.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    unattested = {k: v for k, v in inputs.items() if k != "special_district_present"}
    result = registry.evaluate(rule_id, unattested)
    assert result.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


@pytest.mark.parametrize("rule_id", [_COVERAGE, _REAR_YARD])
def test_unattested_overlay_fails_closed(registry, rule_id) -> None:
    inputs = {k: v for k, v in _inputs_for(rule_id, registry).items() if k != "overlay_present"}
    assert registry.evaluate(rule_id, inputs).coverage_status == (
        cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED)


@pytest.mark.parametrize("rule_id", sorted(_RULE_FILES))
@pytest.mark.parametrize("district", ["R6", "R6A", "R6D", "R7B", "R5", "R6-1"])
def test_rules_are_r6b_only(registry, rule_id, district) -> None:
    inputs = {**_inputs_for(rule_id, registry), "zoning_district": district}
    trace = registry.evaluate(rule_id, inputs).export()
    assert trace["applicability_outcome"] is False
    assert trace["outputs"] == {}


@pytest.mark.parametrize("rule_id", sorted(_RULE_FILES))
def test_rules_are_draft_needs_review_and_lane_a_gated(registry, rule_id) -> None:
    doc = _rule_doc(rule_id)
    assert doc["status"] == "needs_review"
    assert doc["release"]["independent_review"] == "pending"
    assert doc["release"]["qualified_human_approval"] == "pending"
    assert doc["lane_flag"] == "A"
    assert doc["effective_from"] == "2024-12-05"
    result = registry.evaluate(rule_id, _inputs_for(rule_id, registry))
    assert result.coverage_status != cov.COVERAGE_VERIFIED
    assert registry.rule(rule_id).family not in ("lot_coverage", "rear_yard")


@pytest.mark.parametrize("rule_id", sorted(_RULE_FILES))
def test_evaluation_is_byte_deterministic(registry, rule_id) -> None:
    inputs = _inputs_for(rule_id, registry)
    first = json.dumps(registry.evaluate(rule_id, inputs).export(), sort_keys=True)
    second = json.dumps(registry.evaluate(rule_id, inputs).export(), sort_keys=True)
    assert first == second


@pytest.mark.parametrize("rule_id", sorted(_RULE_FILES))
def test_before_the_amendment_date_nothing_is_emitted(registry, rule_id) -> None:
    result = registry.evaluate(rule_id, _inputs_for(rule_id, registry), as_of_date="2024-12-04")
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert result.export()["outputs"] == {}
