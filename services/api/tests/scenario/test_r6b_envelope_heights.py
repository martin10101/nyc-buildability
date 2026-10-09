"""A-02a C-1 at the consumers: the maximum envelope and the proposal checks read the R6B height from
the ONE ZR 23-432 lookup (rule ``r6b-height`` in family ``residential_height_setback``), and every
other district's envelope / check report is byte-identical with lane A on or off.

Expected heights are loaded from the benchmark contract fixture (215-16 Northern Blvd), never
restated. The qualifying-housing 65 ft is an alternative output the consumers never read: a 60 ft
proposal FAILS against the standard 55 ft.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from app.rules import proposal_checks as pc
from app.rules.registry import RuleRegistry
from app.scenario import max_envelope as me
from app.scenario.derivation import LotContext, LotLineSegment

_REPO_ROOT = Path(__file__).resolve().parents[4]
_BENCHMARK = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)
_CASE = (
    Path(__file__).resolve().parents[1] / "rules" / "fixtures" / "proposal_checks"
    / "rectangle_case.json"
)
_ON = {"LANE_A_ENABLED": "1"}
_OFF: dict[str, str] = {}
_R6B_FACTS = {"zoning_district": "R6B", "overlay_present": True, "special_district_present": False}


def _expected(key: str) -> float:
    doc = json.loads(_BENCHMARK.read_text("utf-8"))
    return float(next(v["value"] for v in doc["expected_values"] if v["key"] == key))


def _benchmark_lot() -> LotContext:
    return LotContext(area_sq_ft=_expected("lot_area"), area_provenance={"source": "benchmark"})


def _case() -> dict:
    return json.loads(_CASE.read_text("utf-8"))


def _case_lot(case: dict) -> LotContext:
    lot = case["lot"]
    return LotContext(
        area_sq_ft=lot["area_sq_ft"],
        area_provenance=lot["area_provenance"],
        lot_line_segments=tuple(
            LotLineSegment(id=s["id"], start=tuple(s["start"]), end=tuple(s["end"]))
            for s in lot["lot_line_segments"]
        ),
    )


def _height_dim(envelope: me.MaxEnvelope) -> me.EnvelopeDimensionResult:
    return next(d for d in envelope.dimensions if d.dimension_id == "max_building_height")


def _height_check(block: dict, facts: dict, registry: RuleRegistry) -> pc.CheckResult:
    case = _case()
    report = pc.check_proposal(block, _case_lot(case), facts, scenario_label="a02a",
                               registry=registry)
    return next(r for r in report.results if r.check_id == "building_height")


def test_envelope_binds_the_benchmark_height_from_r6b_height() -> None:
    envelope = me.derive_max_envelope(_benchmark_lot(), _R6B_FACTS,
                                      registry=RuleRegistry(env=_ON).load())
    height = _height_dim(envelope)
    assert height.binding_value == _expected("max_building_height")
    assert height.binding_rule_id == "r6b-height"
    assert height.out_competed_rule_ids == ()
    assert height.conflict_advisory is None
    assert {c["snapshot_id"] for c in height.rule_citations} == {"zr-23-432"}


def test_envelope_flag_off_keeps_the_pre_change_gap() -> None:
    envelope = me.derive_max_envelope(_benchmark_lot(), _R6B_FACTS,
                                      registry=RuleRegistry(env=_OFF).load())
    height = _height_dim(envelope)
    assert height.binding_value is None
    assert height.gap_reason is me.EnvelopeGapReason.NO_APPLICABLE_RULE


def test_envelope_special_district_leaves_the_height_unresolved() -> None:
    facts = {**_R6B_FACTS, "special_district_present": True}
    envelope = me.derive_max_envelope(_benchmark_lot(), facts,
                                      registry=RuleRegistry(env=_ON).load())
    assert _height_dim(envelope).gap_reason is me.EnvelopeGapReason.ALLOWANCE_UNRESOLVED


def test_checker_reads_the_standard_55_ft_never_the_qualifying_65_ft() -> None:
    registry = RuleRegistry(env=_ON).load()
    standard = _expected("max_building_height")
    qualifying = _expected("max_building_height_qualifying_affordable_or_senior")
    block = _case()["block"]  # 3 floors x 10 ft = 30 ft
    passing = _height_check(block, _R6B_FACTS, registry)
    assert passing.outcome is pc.CheckOutcome.PASS
    assert passing.required_value == standard
    assert passing.rule_id == "r6b-height"

    taller = copy.deepcopy(block)
    taller["levels"][0]["floor_count"] = 6  # 60 ft: above 55, below 65
    assert standard < 60.0 < qualifying
    failing = _height_check(taller, _R6B_FACTS, registry)
    assert failing.outcome is pc.CheckOutcome.FAIL
    assert failing.required_value == standard
    assert failing.shortfall == pytest.approx(60.0 - standard)


_OTHER_DISTRICT_FACTS = (
    {"zoning_district": "R5", "overlay_present": False, "special_district_present": False,
     "historic_district": False, "large_site": False},
    {"zoning_district": "R5D", "overlay_present": False, "special_district_present": False,
     "historic_district": False, "large_site": False},
    {"zoning_district": "R4B", "overlay_present": False, "special_district_present": False,
     "historic_district": False, "large_site": False},
    {"zoning_district": "R6A", "overlay_present": True, "special_district_present": False},
    {"zoning_district": "R6", "street_width_class": "wide"},
)


@pytest.mark.parametrize("facts", _OTHER_DISTRICT_FACTS, ids=lambda f: f["zoning_district"])
def test_other_districts_envelope_and_checks_identical_on_or_off(facts) -> None:
    off = RuleRegistry(env=_OFF).load()
    on = RuleRegistry(env=_ON).load()
    env_off = me.derive_max_envelope(_benchmark_lot(), facts, registry=off).as_dict()
    env_on = me.derive_max_envelope(_benchmark_lot(), facts, registry=on).as_dict()
    assert json.dumps(env_on, sort_keys=True) == json.dumps(env_off, sort_keys=True)
    case = _case()
    report_off = pc.check_proposal(case["block"], _case_lot(case), facts,
                                   scenario_label="a02a", registry=off).as_dict()
    report_on = pc.check_proposal(case["block"], _case_lot(case), facts,
                                  scenario_label="a02a", registry=on).as_dict()
    assert json.dumps(report_on, sort_keys=True) == json.dumps(report_off, sort_keys=True)
