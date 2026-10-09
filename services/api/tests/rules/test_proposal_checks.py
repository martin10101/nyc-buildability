"""M5-T054 (D-076 phase B2): proposal-conditioned rule checks.

Hand-computed, offline, deterministic. The fixture rules under
``fixtures/proposal_checks/rulesets`` are SYNTHETIC representability rules
evaluated through the EXISTING evaluator; the numeric expectations are computed by
hand in ``rectangle_case.json`` and here, never by running the module (no
self-proving fixture).

Two checks are COMMENSURABLE and resolve to PASS/FAIL: ``lot_coverage_ratio`` (a
ratio) and ``building_height`` (feet, attestation-gated). Two are structurally
NON-commensurable and are always COULD_NOT_CHECK (provided_fact_not_commensurate):
``rear_yard_depth`` (a generic minimum wall-to-lot-line setback is not a rear-yard
depth) and ``residential_far_floor_area`` (a geometric gross floor area is not a
residential zoning floor area) - matching units are not equivalence, and the module
never introduces the legal interpretation that would be needed to compare them. One
suite also runs against the REAL production registry to prove existing-registry
compatibility for both attested and unattested height/setback behavior.
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import pytest

from app.rules import proposal_checks as pc
from app.rules.registry import RuleRegistry
from app.rules.snapshots import SnapshotStore
from app.scenario.derivation import AttestedStreetLine, LotContext, LotLineSegment

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "proposal_checks"
_RULESETS = _FIXTURES / "rulesets"
_SNAPSHOTS = _FIXTURES / "snapshots"
_CASE_PATH = _FIXTURES / "rectangle_case.json"

# Real R5 lot facts that let the accepted r5-height rule resolve (every optional
# legal input attested, so no exception is indeterminate); still no street width.
_REAL_R5_COMPLETE = {
    "zoning_district": "R5",
    "overlay_present": False,
    "special_district_present": False,
    "historic_district": False,
    "large_site": False,
}


# ---------------------------------------------------------------------------
# Fixtures / helpers.
# ---------------------------------------------------------------------------


@pytest.fixture
def fixture_registry() -> RuleRegistry:
    """A registry over the four SYNTHETIC B2 fixture rules + shared synthetic
    snapshot (one rule per checked family)."""
    return RuleRegistry(_RULESETS, snapshots=SnapshotStore(_SNAPSHOTS)).load()


@pytest.fixture
def case() -> dict:
    return json.loads(_CASE_PATH.read_text(encoding="utf-8"))


def _lot_from(case: dict) -> LotContext:
    lot = case["lot"]
    return LotContext(
        area_sq_ft=lot["area_sq_ft"],
        area_provenance=lot["area_provenance"],
        lot_line_segments=tuple(
            LotLineSegment(id=s["id"], start=tuple(s["start"]), end=tuple(s["end"]))
            for s in lot["lot_line_segments"]
        ),
        street_lines=tuple(
            AttestedStreetLine(
                wall_id=s["wall_id"],
                start=tuple(s["start"]),
                end=tuple(s["end"]),
                attestation=s.get("attestation", {}),
            )
            for s in lot.get("street_lines", [])
        ),
    )


def _by_id(report: pc.ProposalCheckReport) -> dict[str, pc.CheckResult]:
    return {r.check_id: r for r in report.results}


# ---------------------------------------------------------------------------
# AS-1: rectangle proposal -> one commensurable PASS + one commensurable FAIL.
#
# CONTRACT CONFLICT (recorded for orchestrator resolution in the producer report):
# AS-1 as written names "one yard-class PASS". The only yard-family check
# (rear_yard_depth) is structurally NON-commensurable - the derived minimum
# wall-to-lot-line setback is not a rear-yard depth, and designating the rear lot
# line is a legal interpretation this module must not make (see
# test_rear_yard_not_commensurate_even_with_a_rule_present). A supported yard-class
# PASS therefore cannot be produced from the existing facts and rules without a
# legal interpretation. Rather than silently substituting height for the yard PASS
# or weakening the refusal, we EXPLICITLY demonstrate the commensurable PASS path
# via building_height (feet vs feet) and the FAIL path via lot_coverage_ratio, and
# leave the yard check COULD_NOT_CHECK. The conflict is escalated in
# project-control/reports/M5-T054-producer-report.md for orchestrator resolution.
# ---------------------------------------------------------------------------


def test_as1_rectangle_coverage_fail_height_pass(fixture_registry, case):
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        case["lot_rule_facts_attested"],
        scenario_label=case["scenario_label"],
        proposal_id=case["proposal_id"],
        registry=fixture_registry,
    )
    results = _by_id(report)

    # Coverage (commensurable ratio): PROVIDED 0.625 > MAXIMUM 0.500 -> FAIL 0.125.
    cov = results["lot_coverage_ratio"]
    assert cov.outcome is pc.CheckOutcome.FAIL
    assert cov.provided_value == pytest.approx(0.625)
    assert cov.required_value == pytest.approx(0.5)
    assert cov.shortfall == pytest.approx(0.125)
    assert cov.direction is pc.CheckDirection.MAXIMUM

    # Building height (commensurable feet): PROVIDED 30 <= MAXIMUM 60 -> PASS.
    height = results["building_height"]
    assert height.outcome is pc.CheckOutcome.PASS
    assert height.provided_value == pytest.approx(30.0)
    assert height.required_value == pytest.approx(60.0)
    assert height.shortfall is None

    # Rear yard + residential FAR: NON-commensurable -> COULD_NOT_CHECK, no allowance.
    for check_id in ("rear_yard_depth", "residential_far_floor_area"):
        res = results[check_id]
        assert res.outcome is pc.CheckOutcome.COULD_NOT_CHECK
        assert res.could_not_check_reason is (
            pc.CouldNotCheckReason.PROVIDED_FACT_NOT_COMMENSURATE
        )
        assert res.required_value is None  # no allowance presented for comparison
        assert res.shortfall is None

    # Every result carries the scenario label, proposal id, and PROVIDED source_class.
    for res in report.results:
        assert res.scenario_label == "scenario-A-baseline"
        assert res.proposal_id == "prop-0001"
        assert res.source_class == pc.SOURCE_CLASS == "proposed_derivation"
    # The resolved/valued checks carry the derivation record ids they consumed.
    for check_id in ("lot_coverage_ratio", "building_height", "residential_far_floor_area"):
        assert results[check_id].provided_input_ids


def test_as1_matches_fixture_expectations(fixture_registry, case):
    """Outcomes match the hand-computed expectations recorded in the fixture, for
    both the unattested and the attested street-width variants."""
    variants = (
        (case["lot_rule_facts"], case["expected_unattested"]),
        (case["lot_rule_facts_attested"], case["expected_attested"]),
    )
    for facts, expected in variants:
        report = pc.check_proposal(
            case["block"], _lot_from(case), facts,
            scenario_label=case["scenario_label"], registry=fixture_registry,
        )
        results = _by_id(report)
        for check_id in ("lot_coverage_ratio", "building_height",
                         "rear_yard_depth", "residential_far_floor_area"):
            exp = expected[check_id]
            res = results[check_id]
            assert res.outcome.value == exp["outcome"], (facts, check_id)
            if exp.get("shortfall") is not None:
                assert res.shortfall == pytest.approx(exp["shortfall"]), check_id
            if exp.get("reason") is not None:
                assert res.could_not_check_reason is not None
                assert res.could_not_check_reason.value == exp["reason"], check_id
        summary = report.as_dict()["summary"]
        assert summary == expected["summary"], facts


# ---------------------------------------------------------------------------
# AS-2: attestation gates the height check (first-class COULD_NOT_CHECK).
# ---------------------------------------------------------------------------


def test_as2_unattested_street_width_could_not_check(fixture_registry, case):
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        {"zoning_district": "R5"},  # NO street_width_class supplied
        scenario_label="scenario-A-baseline",
        registry=fixture_registry,
    )
    height = _by_id(report)["building_height"]
    assert height.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert height.could_not_check_reason is pc.CouldNotCheckReason.ALLOWANCE_UNRESOLVED
    # Never a default width, never a silent pass/fail, never a computed allowance.
    assert height.required_value is None
    assert height.provided_value == pytest.approx(30.0)  # the PROVIDED fact recorded
    assert height.coverage_status == "professional_review_required"


def test_as2_attested_street_width_runs_the_check(fixture_registry, case):
    """With an attested wide street the height check runs: 30 ft <= 60 ft -> PASS."""
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        {"zoning_district": "R5", "street_width_class": "wide"},
        scenario_label="scenario-A-baseline",
        registry=fixture_registry,
    )
    height = _by_id(report)["building_height"]
    assert height.outcome is pc.CheckOutcome.PASS
    assert height.provided_value == pytest.approx(30.0)
    assert height.required_value == pytest.approx(60.0)


# ---------------------------------------------------------------------------
# Semantic mismatch (rework core): matching units are not equivalence.
# ---------------------------------------------------------------------------


def test_rear_yard_not_commensurate_even_with_a_rule_present(fixture_registry, case):
    """The fixture registry HAS a rear-yard rule that computes 5 ft, yet the module
    still refuses to treat the minimum wall-to-lot-line setback as a rear-yard depth:
    COULD_NOT_CHECK (provided_fact_not_commensurate), no allowance, no comparison."""
    report = pc.check_proposal(
        case["block"], _lot_from(case), case["lot_rule_facts_attested"],
        scenario_label="s", registry=fixture_registry,
    )
    yard = _by_id(report)["rear_yard_depth"]
    assert yard.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert yard.could_not_check_reason is (
        pc.CouldNotCheckReason.PROVIDED_FACT_NOT_COMMENSURATE
    )
    assert yard.required_value is None  # the 5 ft allowance is never presented
    assert yard.shortfall is None
    assert yard.provided_value == pytest.approx(10.0)  # the PROVIDED fact still shown
    assert "rear-yard depth" in yard.detail  # names the missing meaning


def test_residential_far_not_commensurate_even_with_a_rule_present(fixture_registry, case):
    """The fixture registry HAS a residential-FAR rule that computes 12000 sq ft, yet
    the module refuses to compare a geometric gross floor area against it: matching
    square-foot units are not equivalence."""
    report = pc.check_proposal(
        case["block"], _lot_from(case), case["lot_rule_facts_attested"],
        scenario_label="s", registry=fixture_registry,
    )
    far = _by_id(report)["residential_far_floor_area"]
    assert far.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert far.could_not_check_reason is (
        pc.CouldNotCheckReason.PROVIDED_FACT_NOT_COMMENSURATE
    )
    assert far.required_value is None  # the 12000 allowance is never presented
    assert far.provided_value == pytest.approx(15000.0)  # the PROVIDED gross still shown
    assert "residential zoning floor area" in far.detail


def test_provided_fact_absent_path_for_a_commensurable_check(case):
    """A commensurable check whose derived fact is a typed honest absence surfaces
    PROVIDED_FACT_ABSENT (not commensurate, not a silent pass). Exercised directly on
    a commensurable min-setback check against a derivation with no lot line."""
    from app.scenario.derivation import derive_proposal

    lot = LotContext(area_sq_ft=8000.0, area_provenance={}, lot_line_segments=())
    derivation = derive_proposal(case["block"], lot)
    probe = pc.ProposalCheck(
        check_id="min_setback_probe",
        family="lot_coverage",
        required_output="max_lot_coverage_ratio",
        provided_fact="min_lot_line_setback",
        direction=pc.CheckDirection.MINIMUM,
        unit="feet",
        label="probe setback",
    )
    result = pc._run_check(
        probe, derivation, RuleRegistry(_RULESETS, snapshots=SnapshotStore(_SNAPSHOTS)).load(),
        {"lot_area_sq_ft": 8000.0, "zoning_district": "R5"},
        scenario_label="s", proposal_id=None,
    )
    assert result.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert result.could_not_check_reason is pc.CouldNotCheckReason.PROVIDED_FACT_ABSENT
    assert result.provided_value is None


# ---------------------------------------------------------------------------
# AS-3: wiring preconditions (T051-G5 + DB-034(b)) - refuse BEFORE derivation.
# ---------------------------------------------------------------------------


def test_as3_oversized_lot_line_list_refused(case):
    over = pc.MAX_LOT_LINE_SEGMENTS + 1
    seg = LotLineSegment(id="x", start=(999990.0, 199990.0), end=(999990.0, 200060.0))
    lot = LotContext(
        area_sq_ft=8000.0,
        area_provenance={},
        lot_line_segments=tuple(seg for _ in range(over)),
    )
    with pytest.raises(pc.ProposalCheckError) as exc:
        pc.check_proposal(case["block"], lot, {}, scenario_label="s")
    assert exc.value.field == "lot.lot_line_segments"
    assert str(over) in str(exc.value)  # the offending count is named


def test_as3_oversized_street_line_list_refused(case):
    over = pc.MAX_STREET_LINES + 1
    line = AttestedStreetLine(
        wall_id="W-S", start=(0.0, 0.0), end=(1.0, 0.0), attestation={}
    )
    lot = LotContext(
        area_sq_ft=8000.0,
        area_provenance={},
        street_lines=tuple(line for _ in range(over)),
    )
    with pytest.raises(pc.ProposalCheckError) as exc:
        pc.check_proposal(case["block"], lot, {}, scenario_label="s")
    assert exc.value.field == "lot.street_lines"
    assert str(over) in str(exc.value)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_as3_nonfinite_coordinate_refused_before_derivation(case, bad):
    lot = LotContext(
        area_sq_ft=8000.0,
        area_provenance={},
        lot_line_segments=(
            LotLineSegment(id="LL", start=(999990.0, bad), end=(999990.0, 200060.0)),
        ),
    )
    # A ProposalCheckError (precondition) - NOT a ProposalDerivationError - proves
    # the refusal happens BEFORE derive_proposal, so no EvidenceRecord can carry it.
    with pytest.raises(pc.ProposalCheckError) as exc:
        pc.check_proposal(case["block"], lot, {}, scenario_label="s")
    assert exc.value.field == "lot.lot_line_segments['LL'].start"


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_as3_nonfinite_area_refused(case, bad):
    lot = LotContext(area_sq_ft=bad, area_provenance={})
    with pytest.raises(pc.ProposalCheckError) as exc:
        pc.check_proposal(case["block"], lot, {}, scenario_label="s")
    assert exc.value.field == "lot.area_sq_ft"


def test_as3_db034b_offending_value_is_length_capped(case):
    """DB-034(b): a refusal embeds the offending value only through a length-capped
    repr, so an oversized value can never bloat the message."""
    huge = list(range(5000))  # a non-[x,y] 'point' with a very long repr
    lot = LotContext(
        area_sq_ft=8000.0,
        area_provenance={},
        lot_line_segments=(
            LotLineSegment(id="LL", start=huge, end=(1.0, 2.0)),  # type: ignore[arg-type]
        ),
    )
    with pytest.raises(pc.ProposalCheckError) as exc:
        pc.check_proposal(case["block"], lot, {}, scenario_label="s")
    message = str(exc.value)
    assert "repr truncated" in message
    # the embedded repr is capped; the full 5000-element repr would be far longer.
    assert len(message) < pc.MAX_REFUSAL_REPR_LEN + 200


def test_empty_scenario_label_refused(case):
    with pytest.raises(pc.ProposalCheckError) as exc:
        pc.check_proposal(case["block"], _lot_from(case), {}, scenario_label="   ")
    assert exc.value.field == "scenario_label"


# ---------------------------------------------------------------------------
# AS-4: the grouped summary always carries the COULD_NOT_CHECK count.
# ---------------------------------------------------------------------------


def test_as4_summary_carries_could_not_check_count(fixture_registry, case):
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        case["lot_rule_facts_attested"],
        scenario_label="scenario-A-baseline",
        registry=fixture_registry,
    )
    assert report.pass_count == 1
    assert report.fail_count == 1
    assert report.could_not_check_count == 2
    summary = report.as_dict()["summary"]
    assert summary == {"pass": 1, "fail": 1, "could_not_check": 2, "total": 4}
    # A passing subset can never be read as whole-building approval.
    assert summary["could_not_check"] >= 1


# ---------------------------------------------------------------------------
# AS-5: explicit, auditable fact mapping; no rule input fed by an unmapped value.
# ---------------------------------------------------------------------------


def test_as5_declared_mapping_and_unmapped_facts(fixture_registry, case):
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        {"zoning_district": "R5", "boobytrap_input": 999, "lot_area_sq_ft": 1.0},
        scenario_label="scenario-A-baseline",
        registry=fixture_registry,
    )
    bindings = report.rule_input_bindings
    # lot area is sourced ONLY from the LotContext (single source of truth); a
    # same-named caller fact is treated as unmapped and never fed.
    assert bindings["lot_area_sq_ft"] == "lot_context.area_sq_ft"
    assert bindings["zoning_district"] == "caller_lot_fact:zoning_district"
    assert "boobytrap_input" in report.unmapped_lot_facts
    assert "lot_area_sq_ft" in report.unmapped_lot_facts  # the redundant caller copy
    assert "boobytrap_input" not in bindings
    # the declared fact-mapping is echoed for audit, including the semantic_gap that
    # marks the non-commensurable checks (so the refusal-to-compare is auditable data).
    mapping = {m["check_id"]: m for m in report.as_dict()["fact_mapping"]}
    assert mapping["lot_coverage_ratio"]["provided_fact"] == "lot_coverage"
    assert mapping["lot_coverage_ratio"]["semantic_gap"] is None
    far_map = mapping["residential_far_floor_area"]
    assert far_map["required_output"] == "max_residential_floor_area_sq_ft"
    assert far_map["semantic_gap"] is not None
    assert mapping["rear_yard_depth"]["semantic_gap"] is not None


def test_as5_unsupported_family_is_could_not_check(case, tmp_path):
    """A COMMENSURABLE family with no implemented rule surfaces COULD_NOT_CHECK
    (FAMILY_UNSUPPORTED), never a silent PASS. The non-commensurable checks stay
    PROVIDED_FACT_NOT_COMMENSURATE regardless of the registry (the semantic gate is
    registry-independent). Built from a subset registry holding only the coverage
    rule (no height/setback family)."""
    subset = tmp_path / "rulesets"
    subset.mkdir()
    shutil.copy(_RULESETS / "pc-lot-coverage-demo.rule.json", subset)
    registry = RuleRegistry(subset, snapshots=SnapshotStore(_SNAPSHOTS)).load()
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        {"zoning_district": "R5", "street_width_class": "wide"},
        scenario_label="s",
        registry=registry,
    )
    results = _by_id(report)
    assert results["lot_coverage_ratio"].outcome is pc.CheckOutcome.FAIL  # implemented
    # commensurable but no family implemented -> FAMILY_UNSUPPORTED
    height = results["building_height"]
    assert height.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert height.could_not_check_reason is pc.CouldNotCheckReason.FAMILY_UNSUPPORTED
    # non-commensurable -> semantic gate wins over the registry state
    for missing in ("rear_yard_depth", "residential_far_floor_area"):
        res = results[missing]
        assert res.outcome is pc.CheckOutcome.COULD_NOT_CHECK
        assert res.could_not_check_reason is (
            pc.CouldNotCheckReason.PROVIDED_FACT_NOT_COMMENSURATE
        )


# ---------------------------------------------------------------------------
# AS-6: the module constructs no scenario document and emits no contract version.
# ---------------------------------------------------------------------------


def test_as6_no_scenario_document_or_contract_version_emitted(fixture_registry, case):
    source = Path(pc.__file__).read_text(encoding="utf-8")
    forbidden = (
        "build_scenario",
        "validate_scenario_document",
        "assert_scenario_not_verified",
        "SCENARIO_CONTRACT_VERSION",
        "from app.scenario.builder",
        "from app.scenario.contract",
        "import app.scenario.builder",
        "import app.scenario.contract",
    )
    for token in forbidden:
        assert token not in source, f"module must not reference {token!r}"
    # the ONLY app.scenario import is the derivation module.
    assert "from app.scenario.derivation import" in source

    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        case["lot_rule_facts"],
        scenario_label="s",
        registry=fixture_registry,
    )
    document = report.as_dict()
    # a ProposalCheckReport is NOT a scenario document: none of the emitting keys.
    for scenario_key in ("contract_version", "kind", "scenario_id", "constraint_completeness"):
        assert scenario_key not in document


# ---------------------------------------------------------------------------
# AS-7: purity + determinism (same inputs -> byte-identical result).
# ---------------------------------------------------------------------------


def test_as7_deterministic(fixture_registry, case):
    def run() -> dict:
        return pc.check_proposal(
            case["block"],
            _lot_from(case),
            case["lot_rule_facts_attested"],
            scenario_label="scenario-A-baseline",
            proposal_id="prop-0001",
            registry=fixture_registry,
        ).as_dict()

    assert json.dumps(run(), sort_keys=True) == json.dumps(run(), sort_keys=True)


# ---------------------------------------------------------------------------
# Existing-registry compatibility: attested and unattested height/setback behavior.
# ---------------------------------------------------------------------------


def test_real_registry_height_resolves_when_legal_inputs_attested(case):
    """Against the REAL accepted families with every optional legal input attested,
    the r5-height rule (section 23-422) resolves and the proposal's cumulative height
    PASSes (30 ft <= 45 ft), carrying the real rule id and provenance. The
    lot_coverage / rear_yard families are not implemented; residential FAR and rear
    yard stay non-commensurable."""
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        _REAL_R5_COMPLETE,
        scenario_label="scenario-A-baseline",
        registry=RuleRegistry().load(),
    )
    results = _by_id(report)

    height = results["building_height"]
    assert height.outcome is pc.CheckOutcome.PASS
    assert height.required_value == pytest.approx(45.0)  # real R5 max_building_height
    assert height.provided_value == pytest.approx(30.0)
    assert height.rule_id == "r5-height"
    assert height.rule_citations  # provenance carried from the real rule

    assert results["lot_coverage_ratio"].could_not_check_reason is (
        pc.CouldNotCheckReason.FAMILY_UNSUPPORTED
    )
    for check_id in ("rear_yard_depth", "residential_far_floor_area"):
        assert results[check_id].could_not_check_reason is (
            pc.CouldNotCheckReason.PROVIDED_FACT_NOT_COMMENSURATE
        )


def test_real_registry_height_could_not_check_when_inputs_unattested(case):
    """Against the REAL registry with the optional legal inputs NOT attested, the R5
    height rules fail closed (professional_review_required from the indeterminate
    overlay/historic/large-site exceptions), so the height check is COULD_NOT_CHECK -
    family supported, never FAMILY_UNSUPPORTED, never a fabricated pass/fail."""
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        {"zoning_district": "R5"},
        scenario_label="scenario-A-baseline",
        registry=RuleRegistry().load(),
    )
    height = _by_id(report)["building_height"]
    assert height.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert height.could_not_check_reason is not pc.CouldNotCheckReason.FAMILY_UNSUPPORTED
    assert height.required_value is None


def test_real_registry_residential_far_is_not_commensurate(case):
    """Existing-registry proof of the residential-FAR boundary: the REAL
    r5-residential-far rule DOES compute max_residential_floor_area_sq_ft (8000*1.5),
    yet the module refuses to compare the geometric gross floor area against it."""
    report = pc.check_proposal(
        case["block"],
        _lot_from(case),
        _REAL_R5_COMPLETE,
        scenario_label="scenario-A-baseline",
        registry=RuleRegistry().load(),
    )
    far = _by_id(report)["residential_far_floor_area"]
    assert far.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert far.could_not_check_reason is (
        pc.CouldNotCheckReason.PROVIDED_FACT_NOT_COMMENSURATE
    )
    assert far.required_value is None


def test_no_finite_value_reaches_math_isfinite_helper():
    """Guard the finiteness helper directly (unit-level clarity for AS-3)."""
    assert pc._is_finite_number(3.0) is True
    assert pc._is_finite_number(3) is True
    assert pc._is_finite_number(True) is False
    assert pc._is_finite_number(float("nan")) is False
    assert pc._is_finite_number(float("inf")) is False
    assert pc._is_finite_number(10**400) is False
    assert math.isfinite(3.0)  # sanity


# ---------------------------------------------------------------------------
# M5-T057 SCOPE 3 - G4 fold-in tests (M5-T054 G4-1..G4-4). These BIND existing,
# correct, fail-closed behaviour of the ACCEPTED B2 module; app/rules/proposal_checks.py is
# byte-unchanged. G4-1/G4-2 need two/zero applicable rules in one family - impossible with the
# committed one-rule-per-family fixtures - so they drive check_proposal with a minimal registry
# double returning hand-authored traces (no new fixture ruleset files, which are out of scope).
# ---------------------------------------------------------------------------

#: A coverage status the module treats as a usable allowance (read from the module itself so the
#: test can never drift from the accepted _USABLE_COVERAGE set).
_USABLE_COVERAGE_STATUS = next(iter(pc._USABLE_COVERAGE))


class _FakeResult:
    def __init__(self, trace: dict) -> None:
        self._trace = trace

    def export(self) -> dict:
        return self._trace


class _FakeRegistry:
    """A minimal RuleRegistry double: it returns hand-authored evaluator traces for named rule
    ids in a family, so _select_allowance's multi-usable (AMBIGUOUS) and zero-applicable
    (NO_APPLICABLE) branches are bound without adding fixture ruleset files."""

    def __init__(self, family_rule_ids: dict, traces: dict) -> None:
        self._family_rule_ids = family_rule_ids
        self._traces = traces

    def family_coverage(self, family: str) -> dict:
        rule_ids = self._family_rule_ids.get(family)
        return {"rule_ids": list(rule_ids)} if rule_ids else {"family": family}

    def evaluate(self, rule_id: str, _inputs: dict) -> _FakeResult:
        return _FakeResult(self._traces[rule_id])


def _coverage_trace(rule_id: str, *, applicable: bool, output: float = 0.5) -> dict:
    return {
        "rule_id": rule_id,
        "rule_version": "1.0.0",
        "rule_status": "published",
        "applicability_outcome": applicable,
        "coverage_status": _USABLE_COVERAGE_STATUS,
        "outputs": {"max_lot_coverage_ratio": output},
        "citations": (),
    }


def _minimum_trace(rule_id: str, *, required: float) -> dict:
    """A usable, applicable trace whose single output is a MINIMUM-direction allowance the
    injected min-setback check compares against."""
    return {
        "rule_id": rule_id,
        "rule_version": "1.0.0",
        "rule_status": "published",
        "applicability_outcome": True,
        "coverage_status": _USABLE_COVERAGE_STATUS,
        "outputs": {"min_required_setback_ft": required},
        "citations": (),
    }


def test_g4_1_ambiguous_rule_never_picks_a_winner(case):
    """G4-1: two usable same-family rules independently produce the allowance output -> the check
    is COULD_NOT_CHECK/ambiguous_rule with required_value None (which governs is a legal
    determination the module never makes). The PROVIDED fact is still recorded."""
    registry = _FakeRegistry(
        {"lot_coverage": ["cov-a", "cov-b"]},
        {
            "cov-a": _coverage_trace("cov-a", applicable=True),
            "cov-b": _coverage_trace("cov-b", applicable=True),
        },
    )
    report = pc.check_proposal(
        case["block"], _lot_from(case), {"zoning_district": "R5"},
        scenario_label="scenario-A-baseline", registry=registry,
    )
    res = _by_id(report)["lot_coverage_ratio"]
    assert res.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert res.could_not_check_reason is pc.CouldNotCheckReason.AMBIGUOUS_RULE
    assert res.required_value is None
    assert res.provided_value == pytest.approx(0.625)


def test_g4_2_no_applicable_rule_is_visible_not_a_silent_pass(case):
    """G4-2: a rule applicable ELSEWHERE (applicability_outcome False for these facts) yields
    COULD_NOT_CHECK/no_applicable_rule - a visible not-applicable, never a silent PASS."""
    registry = _FakeRegistry(
        {"lot_coverage": ["cov-elsewhere"]},
        {"cov-elsewhere": _coverage_trace("cov-elsewhere", applicable=False)},
    )
    report = pc.check_proposal(
        case["block"], _lot_from(case), {"zoning_district": "R5"},
        scenario_label="scenario-A-baseline", registry=registry,
    )
    res = _by_id(report)["lot_coverage_ratio"]
    assert res.outcome is pc.CheckOutcome.COULD_NOT_CHECK
    assert res.could_not_check_reason is pc.CouldNotCheckReason.NO_APPLICABLE_RULE
    assert res.required_value is None


def test_g4_3_minimum_branch_end_to_end(case, monkeypatch):
    """G4-3: the commensurable MINIMUM branch exercised END-TO-END through check_proposal, not
    only via a direct _compare call. The sole PROPOSAL_CHECKS MINIMUM entry (rear_yard_depth) is
    semantic-gapped -> COULD_NOT_CHECK before any comparison, so we monkeypatch in ONE
    commensurable MINIMUM check over the real derived ``min_lot_line_setback`` (10.0 ft for the
    fixture rectangle: west wall x=1000000 minus lot line x=999990) and drive the whole pipeline
    - preconditions, single derivation, allowance selection, comparison, grouping/counts - with a
    registry double supplying the allowance. Hand-computed against the derived provided value 10.0
    ft: PASS when provided >= required (inclusive at equality); FAIL with shortfall = required -
    provided."""
    min_check = pc.ProposalCheck(
        check_id="min_setback_probe",
        family="min_setback_family",
        required_output="min_required_setback_ft",
        provided_fact="min_lot_line_setback",
        direction=pc.CheckDirection.MINIMUM,
        unit="feet",
        label="probe minimum setback",
    )
    monkeypatch.setattr(pc, "PROPOSAL_CHECKS", (min_check,))

    def run(required: float) -> tuple[pc.CheckResult, pc.ProposalCheckReport]:
        registry = _FakeRegistry(
            {"min_setback_family": ["min-a"]},
            {"min-a": _minimum_trace("min-a", required=required)},
        )
        report = pc.check_proposal(
            case["block"], _lot_from(case), {"zoning_district": "R5"},
            scenario_label="scenario-A-baseline", registry=registry,
        )
        # exactly one grouped result, so the summary counts reflect this branch alone.
        assert report.pass_count + report.fail_count + report.could_not_check_count == 1
        return _by_id(report)["min_setback_probe"], report

    # PASS: derived provided 10.0 ft >= required 5.0 ft -> PASS, no shortfall.
    passed, passed_report = run(5.0)
    assert passed.outcome is pc.CheckOutcome.PASS
    assert passed.provided_value == pytest.approx(10.0)
    assert passed.required_value == pytest.approx(5.0)
    assert passed.shortfall is None
    assert passed_report.pass_count == 1

    # Equality boundary: provided 10.0 ft >= required 10.0 ft -> PASS (inclusive floor).
    boundary, _ = run(10.0)
    assert boundary.outcome is pc.CheckOutcome.PASS
    assert boundary.shortfall is None

    # FAIL: provided 10.0 ft < required 15.0 ft -> FAIL, shortfall = 15 - 10 = 5.0 ft.
    failed, failed_report = run(15.0)
    assert failed.outcome is pc.CheckOutcome.FAIL
    assert failed.provided_value == pytest.approx(10.0)
    assert failed.required_value == pytest.approx(15.0)
    assert failed.shortfall == pytest.approx(5.0)
    assert failed_report.fail_count == 1

    # Direct _compare micro-check of the same operator (kept for operator-level clarity).
    assert pc._compare(pc.CheckDirection.MINIMUM, 10.0, 10.0) == (pc.CheckOutcome.PASS, None)


def test_g4_4_non_lotcontext_and_street_line_finiteness_guards(case):
    """G4-4: two defensive wiring guards. (i) a lot that is not a LotContext is refused typed
    (field 'lot'); (ii) a non-finite STREET-line coordinate is refused before derivation (the
    finiteness loop previously bound only for lot lines)."""
    with pytest.raises(pc.ProposalCheckError) as exc_type:
        pc.check_proposal(case["block"], {"area_sq_ft": 8000.0}, scenario_label="s")
    assert exc_type.value.field == "lot"

    lot = LotContext(
        area_sq_ft=8000.0,
        area_provenance={},
        lot_line_segments=(),
        street_lines=(
            AttestedStreetLine(
                wall_id="W-S",
                start=(math.nan, 200000.0),
                end=(1000100.0, 200000.0),
                attestation={},
            ),
        ),
    )
    with pytest.raises(pc.ProposalCheckError) as exc_fin:
        pc.check_proposal(case["block"], lot, scenario_label="s")
    assert exc_fin.value.field == "lot.street_lines['W-S'].start"
