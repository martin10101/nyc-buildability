"""M4-T008 / DF-6 regression pack: an exception condition that reads an UNSUPPLIED
input is INDETERMINATE, never a silent skip.

Defect (WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23, DF-6, High): ``_apply_exceptions``
evaluated exception conditions with the two-valued ``_eval_predicate``. The
predicate ops are deliberately total - ``equals`` / ``in_set`` / ``compare`` answer
``False`` for a value they never saw - so a missing OPTIONAL input silently answered
"this exception does not apply" and the evaluation kept its full ``conditional``
coverage. Because exceptions are exactly the mechanism by which a rule DOWNGRADES
its own coverage (commercial overlay, special district, historic district, large
site), that was a fail-OPEN miss of an escalation derived from a legal input the
engine had never seen.

Implemented semantics (services/api/app/rules/evaluator.py ``_apply_exceptions``):

* ``condition: null``                              -> applies, unchanged.
* condition reads only SUPPLIED inputs             -> evaluated exactly as before.
* condition would SKIP + reads UNSUPPLIED input(s) -> INDETERMINATE: coverage routes
  to ``professional_review_required`` with a note naming the exception id and every
  unsupplied input; the exception is NOT added to ``exceptions_applied``.
* condition APPLIES + reads UNSUPPLIED input(s)    -> the exception is applied (an
  applied exception can only move coverage AWAY from ``verified``, so applying is the
  conservative direction, not a fail-open) and a note makes the unsupported basis
  explicit instead of silent.

"Unsupplied" is the engine-wide test - an absent key OR a present ``None`` - and is
detected BY NAME from the predicate tree before the outcome is trusted.

No AI call anywhere: pure deterministic evaluation. No contract change: only the
existing ``coverage_status`` and ``notes`` fields carry the outcome.

Scenario map (packet M4-T008 AS-1..AS-5 + the standard six categories):
  AS-1 / missing-input : unsupplied input inside an exception condition -> PRR + note
  AS-2 / positive      : all inputs present -> behaviour bit-for-bit unchanged
  AS-3 / negative      : unsupplied input NOT read by any exception -> unchanged
  AS-4 / exception     : required + applicability indeterminate paths unchanged
  AS-5 / contract      : trace still validates; no new keys; strict JSON; determinism
  AS-6 / effective-date: temporal gating still wins over an indeterminate exception
  boundary             : condition:null, empty exceptions, present-None, partial sets,
                         all/any/not combinators, exists, multi-exception severity
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from app.rules import coverage as cov
from app.rules.dsl import build_rule_definition, evaluation_trace_schema
from app.rules.evaluator import evaluate
from app.rules.registry import RuleRegistry
from app.rules.snapshots import SnapshotStore

_PRR = cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
_M4T003 = Path(__file__).resolve().parent / "fixtures" / "m4t003"
_SNAPSHOT_ID = "zr-demo-m4t003"

# Real production rules used as the live defect site.
_R5_HEIGHT = "r5-height"
_R5_FAR = "r5-residential-far"


@pytest.fixture(scope="module")
def snapshots() -> SnapshotStore:
    """The SYNTHETIC M4-T003 snapshot store (one demo snapshot), reused so this
    pack adds no new fixture files and no new rule ids to any registry."""
    return SnapshotStore(_M4T003 / "snapshots").load()


@pytest.fixture
def registry() -> RuleRegistry:
    """The REAL registry (packaged snapshots + committed R5 rulesets)."""
    return RuleRegistry().load()


# --------------------------------------------------------------------------
# Synthetic rule builder - one optional flag, one exception, nothing else.
# --------------------------------------------------------------------------

_BASE_DOC: dict = {
    "rule_id": "df6-demo",
    "rule_version": "0.0.1-draft",
    "family": "df6_demo",
    "title": "SYNTHETIC exception-indeterminacy demo (M4-T008 / DF-6)",
    "jurisdiction": "nyc",
    "status": "extracted_draft",
    "description": (
        "SYNTHETIC fixture (M4-T008): a minimal rule with one REQUIRED district "
        "input, one REQUIRED area input, and OPTIONAL flags read by an exception "
        "condition. Illustrative only; never a legal statement and never a Verified "
        "determination."
    ),
    "citations": [
        {
            "snapshot_id": _SNAPSHOT_ID,
            "section": "00-00-DEMO",
            "quote": (
                "SYNTHETIC (not verbatim from any source): for M4-T003 engine-hardening "
                "demonstrations only - effective-date temporal selection and a compliance "
                "pass/fail determination. Illustrative values; never a legal statement."
            ),
            "last_amended": None,
        }
    ],
    "inputs": [
        {
            "name": "zoning_district",
            "type": "string",
            "required": True,
            "description": "District governing the lot (scope via applicability).",
        },
        {
            "name": "lot_area_sq_ft",
            "type": "number",
            "required": True,
            "unit": "square_feet",
            "exclusive_minimum": 0,
            "description": "Zoning-lot area (must be > 0).",
        },
        {
            "name": "overlay_present",
            "type": "boolean",
            "required": False,
            "description": "OPTIONAL: whether a commercial overlay applies.",
        },
        {
            "name": "special_district_present",
            "type": "boolean",
            "required": False,
            "description": "OPTIONAL: whether a special district applies.",
        },
        {
            "name": "unrelated_flag",
            "type": "boolean",
            "required": False,
            "description": "OPTIONAL and read by NO exception condition (control).",
        },
    ],
    "outputs": [
        {
            "name": "max_floor_area_sq_ft",
            "type": "number",
            "unit": "square_feet",
            "description": "Maximum floor area = lot area x FAR.",
        }
    ],
    "parameters": [
        {
            "name": "far_value",
            "value": 1.5,
            "citation_ref": _SNAPSHOT_ID,
            "note": "SYNTHETIC FAR.",
        }
    ],
    "applicability": {"op": "in_set", "input": "zoning_district", "values": ["DEMO"]},
    "computation": {
        "steps": [
            {"id": "far", "op": "identity", "args": [{"param": "far_value"}], "note": "FAR."},
            {
                "id": "max_fa",
                "op": "multiply",
                "args": [{"input": "lot_area_sq_ft"}, {"step": "far"}],
                "note": "Maximum floor area = lot area x FAR.",
            },
        ],
        "outputs": {"max_floor_area_sq_ft": {"step": "max_fa"}},
    },
    "exceptions": [],
    "limitations": [
        "SYNTHETIC DF-6 demonstration; illustrative value; requires official capture "
        "+ G6 before any use."
    ],
}

_APPLIES = {"zoning_district": "DEMO", "lot_area_sq_ft": 10000}


def _rule(snapshots: SnapshotStore, *exceptions: dict, **overrides):
    doc = copy.deepcopy(_BASE_DOC)
    doc["exceptions"] = list(exceptions)
    doc.update(copy.deepcopy(overrides))
    return build_rule_definition(doc, snapshots)


def _exc(exc_id: str, condition, effect: str = "professional_review_required") -> dict:
    return {
        "id": exc_id,
        "description": f"SYNTHETIC exception {exc_id}.",
        "condition": condition,
        "effect": effect,
        "citation_ref": _SNAPSHOT_ID,
    }


def _indeterminate_notes(result) -> list[str]:
    return [n for n in result.trace.notes if "indeterminate" in n]


def _applied_ids(result) -> set[str]:
    return {e["id"] for e in result.trace.exceptions_applied}


# ==========================================================================
# AS-1 (missing-input) - the defect itself: unsupplied input inside an
# exception condition routes to PRR with a note naming input + exception.
# ==========================================================================

def test_df6_as1_unsupplied_input_in_exception_condition_routes_to_prr(snapshots):
    """THE DF-6 CASE. Before the fix: equals(None, True) -> False -> the
    coverage-downgrading exception was silently skipped and coverage stayed
    ``conditional``. After: indeterminate -> professional_review_required."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, dict(_APPLIES), snapshots)

    assert result.coverage_status == _PRR, "a silent skip would have left 'conditional'"
    # The exception is NOT claimed as applied - the engine does not know either way.
    assert _applied_ids(result) == set()
    # A note names BOTH the exception id and the unsupplied input.
    notes = _indeterminate_notes(result)
    assert len(notes) == 1
    assert "commercial_overlay" in notes[0]
    assert "overlay_present" in notes[0]


def test_df6_as1_present_none_is_treated_as_unsupplied(snapshots):
    """An explicitly-``None`` value reaches the predicate identically to an absent
    key, so it must route to the same indeterminate escalation (boundary)."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, {**_APPLIES, "overlay_present": None}, snapshots)
    assert result.coverage_status == _PRR
    assert "overlay_present" in _indeterminate_notes(result)[0]


def test_df6_as1_not_wrapped_predicate_cannot_launder_an_unsupplied_input(snapshots):
    """A ``not``-wrapped condition flips the unsupported ``False`` to ``True``, so the
    exception APPLIES. That is the conservative direction (applying can only downgrade
    coverage), so it is not the DF-6 fail-open - but the unsupported basis must be
    stated in the trace rather than presented as a determination."""
    rule = _rule(
        snapshots,
        _exc(
            "qualifying_site",
            {"not": {"op": "equals", "input": "overlay_present", "value": True}},
            effect="conditional_alternative",
        ),
    )
    result = evaluate(rule, dict(_APPLIES), snapshots)
    assert "qualifying_site" in _applied_ids(result)
    disclosure = [
        n for n in result.trace.notes
        if "was applied although its condition reads" in n
    ]
    assert len(disclosure) == 1
    assert "overlay_present" in disclosure[0]


@pytest.mark.parametrize(
    "condition,expect_names",
    [
        # a single leaf
        ({"op": "equals", "input": "overlay_present", "value": True}, ["overlay_present"]),
        # 'all' - the unsupplied name is reached through the combinator
        (
            {
                "all": [
                    {"op": "equals", "input": "overlay_present", "value": True},
                    {"op": "equals", "input": "special_district_present", "value": True},
                ]
            },
            ["overlay_present", "special_district_present"],
        ),
        # 'any' - likewise
        (
            {
                "any": [
                    {"op": "equals", "input": "overlay_present", "value": True},
                    {"op": "equals", "input": "special_district_present", "value": True},
                ]
            },
            ["overlay_present", "special_district_present"],
        ),
        # nested not(all(...))
        (
            {
                "not": {
                    "all": [
                        {"op": "equals", "input": "overlay_present", "value": True},
                        {"op": "equals", "input": "special_district_present", "value": True},
                    ]
                }
            },
            ["overlay_present", "special_district_present"],
        ),
        # the 'exists' presence probe is still an unsupplied read
        ({"op": "exists", "input": "overlay_present"}, ["overlay_present"]),
        # a numeric threshold on an unsupplied value
        (
            {"op": "compare", "input": "overlay_present", "compare": "gt", "value": 0},
            ["overlay_present"],
        ),
        # in_set on an unsupplied value
        ({"op": "in_set", "input": "overlay_present", "values": [True]}, ["overlay_present"]),
    ],
)
def test_df6_as1_every_combinator_and_op_reaches_the_unsupplied_name(
    snapshots, condition, expect_names
):
    """Name detection walks ``all`` / ``any`` / ``not`` and every predicate op, so no
    condition shape can hide an unsupplied read. Each shape here would be SKIPPED
    two-valued (or, for ``not``, would apply) - the ones that would skip must escalate."""
    rule = _rule(snapshots, _exc("exc_under_test", condition))
    result = evaluate(rule, dict(_APPLIES), snapshots)
    notes = _indeterminate_notes(result)
    if notes:
        assert result.coverage_status == _PRR
        for name in expect_names:
            assert name in notes[0]
    else:
        # the shape APPLIED the exception instead of skipping it - the conservative
        # direction - and must then carry the explicit unsupported-basis disclosure.
        assert "exc_under_test" in _applied_ids(result)
        assert any("was applied although its condition reads" in n for n in result.trace.notes)


def test_df6_as1_partially_supplied_condition_still_escalates(snapshots):
    """Boundary: one of the two names IS supplied. The condition still reads an
    unsupplied name, so the outcome is still indeterminate, and ONLY the unsupplied
    name is reported."""
    rule = _rule(
        snapshots,
        _exc(
            "combo",
            {
                "any": [
                    {"op": "equals", "input": "overlay_present", "value": True},
                    {"op": "equals", "input": "special_district_present", "value": True},
                ]
            },
        ),
    )
    result = evaluate(rule, {**_APPLIES, "overlay_present": False}, snapshots)
    assert result.coverage_status == _PRR
    note = _indeterminate_notes(result)[0]
    assert "special_district_present" in note
    assert "overlay_present" not in note


def test_df6_as1_live_defect_site_r5_height_without_modifier_flags(registry):
    """The defect on a REAL committed rule: r5-height declares four OPTIONAL modifier
    flags, each gating a professional_review_required exception. Evaluated without
    them, the pre-fix engine reported a confident 35/45 ft envelope as ``conditional``
    while four escalating exceptions had been silently skipped."""
    result = registry.evaluate(_R5_HEIGHT, {"zoning_district": "R5"})
    assert result.coverage_status == _PRR
    notes = _indeterminate_notes(result)
    named = " ".join(notes)
    for flag in (
        "overlay_present",
        "special_district_present",
        "historic_district",
        "large_site",
    ):
        assert flag in named, f"{flag} must be named as an unsupplied exception input"
    for exc_id in (
        "commercial_overlay_modification",
        "special_district_modification",
        "historic_district_base_height_match",
        "large_site_modification",
    ):
        assert exc_id in named
    # The unconditional documented limitation is unaffected by DF-6.
    assert "no_minimum_base_height" in _applied_ids(result)


# ==========================================================================
# AS-2 (positive) - all-inputs-present behaviour is unchanged.
# ==========================================================================

@pytest.mark.parametrize("flag_value,expect_applied", [(True, True), (False, False)])
def test_df6_as2_supplied_input_evaluates_exactly_as_before(
    snapshots, flag_value, expect_applied
):
    """Both outcomes of a fully-supplied condition are preserved: supplied-True still
    applies the exception (PRR), supplied-False still skips it silently (conditional).
    A supplied ``False`` is knowledge, not a gap - it must NOT escalate."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, {**_APPLIES, "overlay_present": flag_value}, snapshots)
    assert ("commercial_overlay" in _applied_ids(result)) is expect_applied
    assert result.coverage_status == (_PRR if expect_applied else cov.COVERAGE_CONDITIONAL)
    assert _indeterminate_notes(result) == []


def test_df6_as2_r5_height_all_modifier_flags_known_stays_conditional(registry):
    """The real rule with every modifier flag affirmatively known to be false yields
    the unchanged confident envelope - the M4-T006 accepted behaviour."""
    result = registry.evaluate(
        _R5_HEIGHT,
        {
            "zoning_district": "R5",
            "overlay_present": False,
            "special_district_present": False,
            "historic_district": False,
            "large_site": False,
        },
    )
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.outputs == {"max_base_height": 35.0, "max_building_height": 45.0}
    assert _indeterminate_notes(result) == []


def test_df6_as2_r5_height_known_overlay_still_downgrades(registry):
    """A KNOWN overlay still produces the ordinary applied-exception downgrade, and it
    is reported as applied (not as indeterminate)."""
    result = registry.evaluate(
        _R5_HEIGHT,
        {
            "zoning_district": "R5",
            "overlay_present": True,
            "special_district_present": False,
            "historic_district": False,
            "large_site": False,
        },
    )
    assert result.coverage_status == _PRR
    assert "commercial_overlay_modification" in _applied_ids(result)
    assert _indeterminate_notes(result) == []


def test_df6_as2_r5_far_all_inputs_present_unchanged(registry):
    """The FAR rule with ``site_class`` supplied is untouched by DF-6 in both
    directions (standard lot -> alternative not applied; qualifying -> applied)."""
    standard = registry.evaluate(
        _R5_FAR,
        {"zoning_district": "R5", "lot_area_sq_ft": 5000, "site_class": "standard_zoning_lot"},
    )
    assert standard.coverage_status == cov.COVERAGE_CONDITIONAL
    assert "qualifying_residential_site" not in _applied_ids(standard)
    assert _indeterminate_notes(standard) == []

    qualifying = registry.evaluate(
        _R5_FAR,
        {
            "zoning_district": "R5",
            "lot_area_sq_ft": 5000,
            "site_class": "qualifying_residential_site",
        },
    )
    assert "qualifying_residential_site" in _applied_ids(qualifying)
    assert _indeterminate_notes(qualifying) == []


def test_df6_as2_condition_null_exception_is_unaffected(snapshots):
    """Boundary: an unconditional (``condition: null``) documented limitation always
    applies and can never be indeterminate - it reads no input at all."""
    rule = _rule(snapshots, _exc("always_on", None, effect="documented_limitation"))
    result = evaluate(rule, dict(_APPLIES), snapshots)
    assert "always_on" in _applied_ids(result)
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert _indeterminate_notes(result) == []


def test_df6_as2_rule_with_no_exceptions_is_unaffected(snapshots):
    """Boundary: the empty exception list."""
    result = evaluate(_rule(snapshots), dict(_APPLIES), snapshots)
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.trace.exceptions_applied == []
    assert _indeterminate_notes(result) == []


# ==========================================================================
# AS-3 (negative control) - an unsupplied optional input that NO exception
# condition reads keeps its existing missing_noncritical behaviour.
# ==========================================================================

def test_df6_as3_unsupplied_input_not_read_by_any_exception_is_untouched(snapshots):
    """``unrelated_flag`` is optional and unsupplied, but no exception condition reads
    it: coverage stays ``conditional``, completeness stays ``missing_noncritical``, and
    the pre-existing 'optional input(s) not supplied' note is still the only signal."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, {**_APPLIES, "overlay_present": False}, snapshots)

    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.trace.data_completeness == cov.COMPLETENESS_MISSING_NONCRITICAL
    assert _indeterminate_notes(result) == []
    optional_notes = [n for n in result.trace.notes if "optional input(s) not supplied" in n]
    assert len(optional_notes) == 1
    assert "unrelated_flag" in optional_notes[0]


def test_df6_as3_completeness_axis_is_not_repurposed(snapshots):
    """An unsupplied OPTIONAL input stays ``missing_noncritical`` even when it made an
    exception indeterminate. The escalation is carried on the coverage axis (PRR);
    ``data_completeness`` continues to describe input supply only, so the two axes stay
    independent (missing_critical remains reserved for a missing REQUIRED input)."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, dict(_APPLIES), snapshots)
    assert result.coverage_status == _PRR
    assert result.trace.data_completeness == cov.COMPLETENESS_MISSING_NONCRITICAL


# ==========================================================================
# AS-4 (exception / prior indeterminate paths) - unchanged.
# ==========================================================================

def test_df6_as4_missing_required_input_path_unchanged(snapshots):
    """A missing REQUIRED input still stops before computation with
    missing_critical - it never reaches the exception stage at all."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, {"zoning_district": "DEMO"}, snapshots)
    assert result.coverage_status == _PRR
    assert result.outputs == {}
    assert result.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL
    assert _indeterminate_notes(result) == []


def test_df6_as4_applicability_indeterminate_path_unchanged(snapshots):
    """The applicability three-valued path still owns its own reason string."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, {"lot_area_sq_ft": 10000}, snapshots)
    assert result.coverage_status == _PRR
    assert result.trace.applicability_trace[0].get("indeterminate") is True


def test_df6_as4_not_applicable_never_reaches_exceptions(snapshots):
    """A rule that does not apply short-circuits before exceptions, so an unsupplied
    exception input can never turn a not_applicable into an escalation."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, {**_APPLIES, "zoning_district": "OTHER"}, snapshots)
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert _indeterminate_notes(result) == []


def test_df6_as4_invalid_supplied_input_still_fails_closed_first(snapshots):
    """A supplied-but-INVALID optional input is rejected by the existing fail-closed
    validation before the exception stage; it is not re-labelled as indeterminate."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, {**_APPLIES, "overlay_present": "yes-please"}, snapshots)
    assert result.coverage_status == _PRR
    assert result.trace.input_validation["valid"] is False
    assert _indeterminate_notes(result) == []


def test_df6_as4_geometric_uncertainty_still_composes(snapshots):
    """Severity composition is unchanged: an indeterminate exception and a
    data_conflict geometry still resolve to the MOST severe status."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(
        rule,
        dict(_APPLIES),
        snapshots,
        spatial_context={
            "lot_overall_class": "data_conflict",
            "professional_review_required": True,
            "coverage_note": "conflicting district assignments",
        },
    )
    assert result.coverage_status == cov.COVERAGE_DATA_CONFLICT
    assert _indeterminate_notes(result) != []


def test_df6_as4_multiple_exceptions_each_reported(snapshots):
    """Every indeterminate exception is named separately; an applied one alongside
    them is still reported as applied."""
    rule = _rule(
        snapshots,
        _exc("overlay_exc", {"op": "equals", "input": "overlay_present", "value": True}),
        _exc("special_exc", {"op": "equals", "input": "special_district_present", "value": True}),
        _exc("always_on", None, effect="documented_limitation"),
    )
    result = evaluate(rule, dict(_APPLIES), snapshots)
    notes = _indeterminate_notes(result)
    assert len(notes) == 2
    assert {"overlay_exc", "special_exc"} <= {n.split()[1] for n in notes}
    assert _applied_ids(result) == {"always_on"}
    assert result.coverage_status == _PRR


# ==========================================================================
# AS-5 (contract) - trace still validates; no new keys; strict JSON; determinism.
# ==========================================================================

def test_df6_as5_indeterminate_trace_validates_against_engine_schema(snapshots):
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    exported = evaluate(rule, dict(_APPLIES), snapshots).export()
    jsonschema.Draft202012Validator(evaluation_trace_schema()).validate(exported)


@pytest.mark.parametrize(
    "schema_path",
    [
        Path(__file__).resolve().parents[2] / "app" / "rules" / "schemas" / "v1"
        / "evaluation_trace.schema.json",
        Path(__file__).resolve().parents[2] / "app" / "_contract_schemas" / "v1"
        / "rule_evaluation.schema.json",
    ],
    ids=["engine_trace_schema", "canonical_rule_evaluation_contract"],
)
def test_df6_as5_escalated_trace_introduces_no_new_contract_key(registry, schema_path):
    """Both the engine trace schema and the canonical rule_evaluation contract declare
    the trace with ``additionalProperties: false`` and a fixed ``required`` list. A DF-6
    escalated trace must carry EXACTLY the declared key set - no key added, none dropped
    - which is what proves the fix took the contract-safe (notes-only) route.

    The key sets are compared directly rather than by running the validator, because the
    canonical contract's trace ``$ref``s sibling schema FILES (coverage_status, common)
    that a standalone sub-schema validator cannot resolve; the key set is precisely the
    part ``additionalProperties: false`` governs. Full end-to-end validation of the whole
    contract document is covered by tests/api/test_rule_evaluation_api.py."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    # The engine schema IS the trace; the canonical contract nests it under $defs.
    trace_schema = (
        schema["$defs"]["evaluation_trace"]
        if schema_path.name == "rule_evaluation.schema.json"
        else schema
    )
    assert trace_schema["additionalProperties"] is False

    exported = registry.evaluate(_R5_HEIGHT, {"zoning_district": "R5"}).export()
    assert exported["coverage_status"] == _PRR  # the DF-6 escalation is present
    assert set(exported) == set(trace_schema["properties"])
    assert set(trace_schema["required"]) <= set(exported)


def test_df6_as5_exceptions_applied_entries_keep_exactly_three_keys(snapshots):
    """No key was added to an ``exceptions_applied`` entry: the indeterminate outcome
    is carried entirely by coverage_status + notes (contract-safe route)."""
    rule = _rule(
        snapshots,
        _exc("overlay_exc", {"op": "equals", "input": "overlay_present", "value": True}),
        _exc("always_on", None, effect="documented_limitation"),
    )
    result = evaluate(rule, dict(_APPLIES), snapshots)
    for entry in result.trace.exceptions_applied:
        assert set(entry) == {"id", "effect", "description"}


def test_df6_as5_indeterminate_trace_is_strict_json_and_deterministic(snapshots):
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    a = json.dumps(evaluate(rule, dict(_APPLIES), snapshots).export(), sort_keys=True,
                   allow_nan=False)
    b = json.dumps(evaluate(rule, dict(_APPLIES), snapshots).export(), sort_keys=True,
                   allow_nan=False)
    assert a == b


def test_df6_as5_notes_are_plain_strings(snapshots):
    """``notes`` is contractually ``array of string``; the new notes must not smuggle
    a structured object into it."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, dict(_APPLIES), snapshots)
    assert all(isinstance(note, str) for note in result.trace.notes)


def test_df6_as5_escalation_never_upgrades_coverage(snapshots):
    """The escalation can only move coverage AWAY from verified: a draft rule cannot
    be lifted to verified by any exception path."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
    )
    result = evaluate(rule, dict(_APPLIES), snapshots)
    assert result.coverage_status != cov.COVERAGE_VERIFIED
    assert result.trace.rule_release["verified_eligible"] is False


# ==========================================================================
# AS-6 (effective-date) - temporal gating is evaluated BEFORE exceptions and
# is unchanged by DF-6.
# ==========================================================================

def test_df6_as6_not_yet_effective_wins_over_indeterminate_exception(snapshots):
    """A rule that is not in effect yields not_applicable with no computation, even
    though an exception condition reads an unsupplied input. Temporal gating (step 0)
    must not be overridden by the exception escalation (step 5)."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
        effective_from="2024-12-05",
    )
    result = evaluate(rule, dict(_APPLIES), snapshots, as_of_date="2024-12-04")
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert result.outputs == {}
    assert result.trace.effective_window["in_effect"] is False
    assert _indeterminate_notes(result) == []


def test_df6_as6_on_and_after_effective_date_the_escalation_applies(snapshots):
    """Boundary: on the first effective day (inclusive) the rule is in effect and the
    DF-6 escalation is produced."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
        effective_from="2024-12-05",
    )
    for as_of in ("2024-12-05", "2025-06-01"):
        result = evaluate(rule, dict(_APPLIES), snapshots, as_of_date=as_of)
        assert result.trace.effective_window["in_effect"] is True
        assert result.coverage_status == _PRR
        assert _indeterminate_notes(result) != []


def test_df6_as6_invalid_as_of_date_still_fails_closed_first(snapshots):
    """An unusable as_of date fails closed at step 0a with its own reason; the
    exception stage is never reached."""
    rule = _rule(
        snapshots,
        _exc("commercial_overlay", {"op": "equals", "input": "overlay_present", "value": True}),
        effective_from="2024-12-05",
    )
    result = evaluate(rule, dict(_APPLIES), snapshots, as_of_date="2024-02-30")
    assert result.coverage_status == _PRR
    assert result.trace.applicability_trace[0].get("invalid_as_of_date") is True
    assert _indeterminate_notes(result) == []
