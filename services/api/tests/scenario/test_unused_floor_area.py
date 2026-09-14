"""Executable acceptance pack S1..S6 for the C1 unused-draft-zoning-floor-area
section (task M5-T017, directive D-041 R001).

Offline and deterministic. Every numeric assertion is DERIVED from the fixture
(cap read from the canonical trace; existing area from the fixture profile) - no
magic number is retyped. Each test maps to exactly one acceptance scenario.

The section is exercised BOTH through the full ``build_scenario`` document (so the
wire-in, the root professional_review_required widening, and schema validity are
proven end to end) and directly via ``build_unused_floor_area_section`` for the
edge cases.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.scenario import (
    UNUSED_FLOOR_AREA_LABEL,
    build_scenario,
    build_unused_floor_area_section,
    validate_scenario_document,
)
from app.scenario import (
    UnusedFloorAreaNotComputableReason as Reason,
)
from app.scenario import (
    UnusedFloorAreaState as State,
)
from app.scenario import constants as C

from . import _support as S

REPO_ROOT = Path(__file__).resolve().parents[4]
CANONICAL_SCHEMA = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1" / "scenario.schema.json"
BUNDLED_SCHEMA = (
    REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1" / "scenario.schema.json"
)

# The bldgarea fact provenance id + record appended to the profile so the
# section can resolve the existing-area provenance the same way lot area is.
BLDGAREA_PROV_ID = "prov-bldgarea"
BLDGAREA_SOURCE_ID = "nyc-dcp-mappluto-arcgis"


def profile_with_bldgarea(
    value,
    *,
    coverage_status: str = "conditional",
    units: str | None = "square_feet",
    with_fact: bool = True,
    with_provenance: bool = True,
    numbldgs: dict | None = None,
):
    """A profile that (optionally) carries an existing-building bldgarea fact whose
    provenance_ref resolves against the root provenance[] array - the SAME resolution
    pattern lot area uses. bbl matches the canonical rule_evaluation so the scenario
    stays a preliminary (no bbl-mismatch conflict).

    ``numbldgs`` optionally supplies the SIBLING existing_building_facts.numbldgs fact
    (e.g. ``{"value": 0.0, "coverage_status": "conditional"}``) - the D-059-R002/R011
    vacancy basis a zero bldgarea needs to be consumed as a usable zero. Omitted
    entirely (``None``, the default) means numbldgs is ABSENT from the profile.
    """
    prof = S.profile()
    facts: dict = {}
    if with_fact:
        fact = {
            "value": value,
            "provenance_ref": BLDGAREA_PROV_ID,
            "coverage_status": coverage_status,
        }
        if units is not None:
            fact["units"] = units
        facts["bldgarea"] = fact
    if numbldgs is not None:
        facts["numbldgs"] = numbldgs
    if facts:
        prof["existing_building_facts"] = facts
    if with_provenance:
        prof["provenance"].append(
            {
                "provenance_id": BLDGAREA_PROV_ID,
                "source_id": BLDGAREA_SOURCE_ID,
                "dataset_version": "26v1",
                "original_field_name": "bldgarea",
                "effective_date": None,
            }
        )
    return prof


def _vacant_numbldgs(coverage_status: str = "conditional") -> dict:
    """The established-vacancy numbldgs fact (present, usable, == 0)."""
    return {"value": 0.0, "coverage_status": coverage_status}


def _section(document: dict) -> dict:
    return document["unused_draft_zoning_floor_area"]


# ---------------------------------------------------------------------------
# S1 - computed normal remainder.
# ---------------------------------------------------------------------------


def test_s1_computed_normal_remainder():
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)  # fixture-derived cap (15000.0)
    bldgarea = cap - 5000.0  # a usable existing area strictly below the cap
    document = build_scenario(profile_with_bldgarea(bldgarea), rule_evaluation)
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.COMPUTED.value
    # Deterministic unrounded subtraction, in square_feet.
    assert section["unused_draft_zoning_floor_area_sq_ft"] == cap - bldgarea
    assert section["unit"] == "square_feet"
    assert section["not_computable_reason"] is None
    assert section["over_built_statement"] is None

    # Precise-noun label rendered verbatim; DRAFT / FAR-derived wording present.
    assert section["label"] == UNUSED_FLOOR_AREA_LABEL
    assert "unused draft zoning floor area (far-derived)" in section["label"].lower()
    # Scope note states geometry NOT assessed.
    assert section["scope_note"] == C.UNUSED_FLOOR_AREA_SCOPE_NOTE
    scope_lower = section["scope_note"].lower()
    assert "geometry" in scope_lower and "not been assessed" in scope_lower
    for term in ("height", "yards", "layout"):
        assert term in scope_lower

    # Formula records BOTH inputs; each input carries resolvable provenance.
    assert section["formula"] == C.UNUSED_FLOOR_AREA_FORMULA
    cap_input = section["inputs"]["draft_zoning_floor_area_cap"]
    assert cap_input["value_sq_ft"] == cap
    # cap provenance is the scenario cap_provenance echoed verbatim.
    assert cap_input["provenance"] == document["cap_provenance"]
    existing_input = section["inputs"]["existing_building_floor_area"]
    assert existing_input["value_sq_ft"] == bldgarea
    assert existing_input["coverage_status"] == "conditional"
    assert existing_input["provenance_ref"] == BLDGAREA_PROV_ID
    # bldgarea provenance resolved from provenance_ref via the root provenance[] array.
    assert existing_input["provenance"]["source_id"] == BLDGAREA_SOURCE_ID
    assert existing_input["provenance"]["original_field_name"] == "bldgarea"

    # Machine-readable ZR 12-10 assumption record (a field, not display text).
    assert section["assumptions"] == [C.zoning_lot_extent_assumption()]
    assumption = section["assumptions"][0]
    assert assumption["key"] == "zoning_lot_extent"
    assert set(assumption) == {"key", "assumption_type", "value", "unit", "rationale"}
    assert "12-10" in assumption["rationale"]
    assert "zoning lot" in assumption["value"].lower()

    # A computed (positive) remainder does NOT itself trigger professional review.
    assert section["professional_review_required"] is False
    assert document["professional_review_required"] is False


# ---------------------------------------------------------------------------
# S2 - over-built honest negative remainder.
# ---------------------------------------------------------------------------


def test_s2_over_built_honest_negative():
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    bldgarea = cap + 5000.0  # existing area EXCEEDS the draft cap
    document = build_scenario(profile_with_bldgarea(bldgarea), rule_evaluation)
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.OVER_BUILT.value
    # Preserved NEGATIVE - never clamped to zero, nulled, or absolute-valued.
    value = section["unused_draft_zoning_floor_area_sq_ft"]
    assert value == cap - bldgarea
    assert value < 0
    assert value != 0
    assert value != abs(value)

    # An explicit own statement names the over-built condition honestly.
    assert section["over_built_statement"] == C.UNUSED_FLOOR_AREA_OVER_BUILT_STATEMENT
    assert "exceed" in section["over_built_statement"].lower()

    # Routes to professional review at BOTH levels.
    assert section["professional_review_required"] is True
    assert document["professional_review_required"] is True

    # Same provenance + assumption + scope discipline as S1.
    assert section["assumptions"] == [C.zoning_lot_extent_assumption()]
    assert section["formula"] == C.UNUSED_FLOOR_AREA_FORMULA
    assert section["inputs"]["existing_building_floor_area"]["provenance"]["source_id"] == (
        BLDGAREA_SOURCE_ID
    )
    assert section["scope_note"] == C.UNUSED_FLOOR_AREA_SCOPE_NOTE


# ---------------------------------------------------------------------------
# S3 - zero boundary (an honest zero is computed, not over_built, not missing).
# ---------------------------------------------------------------------------


def test_s3_zero_boundary_is_computed_not_over_built():
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    bldgarea = cap  # bldgarea == draft cap exactly
    document = build_scenario(profile_with_bldgarea(bldgarea), rule_evaluation)
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.COMPUTED.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] == 0
    assert section["not_computable_reason"] is None
    assert section["over_built_statement"] is None
    # The zero itself triggers no professional-review routing.
    assert section["professional_review_required"] is False
    assert document["professional_review_required"] is False
    # Label / scope / assumption discipline unchanged.
    assert section["label"] == UNUSED_FLOOR_AREA_LABEL
    assert section["assumptions"] == [C.zoning_lot_extent_assumption()]


def test_s1_established_vacancy_zero_existing_area_is_usable_and_computed():
    """D-059-R002/R011 correction (formerly a MISCAST 'vacant lot' test that
    supplied bldgarea=0 WITHOUT establishing vacancy - the exact defect the
    reviewer flagged). An existing area of exactly 0.0 is a USABLE input
    (_nonnegative_finite_float, deliberately not _positive_...) and yields the
    C1 headline answer - the full draft cap as unused floor area - ONLY when
    the SAME profile's numbldgs fact establishes vacancy (present, usable,
    exactly 0). Kills the one-character mutant that would reclassify an
    established-vacancy lot as existing_building_area_unusable."""
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    document = build_scenario(
        profile_with_bldgarea(0.0, numbldgs=_vacant_numbldgs()), rule_evaluation
    )
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.COMPUTED.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] == cap
    assert section["not_computable_reason"] is None
    assert section["inputs"]["existing_building_floor_area"]["value_sq_ft"] == 0.0
    assert section["professional_review_required"] is False
    assert document["professional_review_required"] is False


# ---------------------------------------------------------------------------
# D-059-R002/R011 - bldgarea == 0 WITHOUT established vacancy fails closed
# (never consumed as a real/vacant zero). Reproduces the reviewer's exact
# unit-level case: one building, recorded bldgarea 0, a positive draft cap -
# the OLD code returned the full cap as unused with no not_computable reason
# and no professional-review flag. RED on that old behavior.
# ---------------------------------------------------------------------------


def test_s1_zero_with_positive_numbldgs_fails_closed_red_on_old():
    """The reviewer's exact reproduction case: one building (numbldgs=1),
    recorded bldgarea 0, a positive draft cap. The OLD code returned
    computed=cap (the full cap as 'unused'), no not_computable_reason, and no
    professional-review flag - exactly what this test forbids."""
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    document = build_scenario(
        profile_with_bldgarea(0.0, numbldgs={"value": 1.0, "coverage_status": "conditional"}),
        rule_evaluation,
    )
    validate_scenario_document(document)

    section = _section(document)
    # RED-ON-OLD: the pre-fix code computed this as `cap` (COMPUTED); the fix
    # must fail closed instead.
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] != cap
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None  # never estimated
    assert section["not_computable_reason"] == Reason.EXISTING_BUILDING_AREA_UNUSABLE.value
    # Escalates to professional review at BOTH levels (unlike the generic
    # unusable-coverage-status case, which does not).
    assert section["professional_review_required"] is True
    assert document["professional_review_required"] is True

    # The original zero and the numbldgs basis (1, a positive count) stay
    # traceable in assumptions (the closed inputs shape has no numbldgs field).
    assert len(section["assumptions"]) == 2
    zero_assumption, numbldgs_assumption = section["assumptions"]
    assert zero_assumption["key"] == "existing_building_area_recorded_zero"
    assert zero_assumption["value"] == 0.0
    assert numbldgs_assumption["key"] == "existing_building_area_numbldgs_basis"
    assert numbldgs_assumption["value"] == 1.0
    assert "1" in numbldgs_assumption["rationale"]
    assert "positive" in numbldgs_assumption["rationale"].lower()


def test_s1_zero_with_absent_numbldgs_fails_closed():
    """numbldgs absent entirely (the shared _support PROFILE shape, and any
    real profile that never received the column) - vacancy is never guessed."""
    rule_evaluation = S.canonical_rule_evaluation()
    document = build_scenario(profile_with_bldgarea(0.0), rule_evaluation)  # no numbldgs
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None
    assert section["not_computable_reason"] == Reason.EXISTING_BUILDING_AREA_UNUSABLE.value
    assert section["professional_review_required"] is True
    assert document["professional_review_required"] is True
    numbldgs_assumption = section["assumptions"][1]
    assert numbldgs_assumption["value"] is None
    assert "not present" in numbldgs_assumption["rationale"]


@pytest.mark.parametrize("bad_numbldgs_coverage", ["data_conflict", "unsupported"])
def test_s1_zero_with_unusable_numbldgs_coverage_fails_closed(bad_numbldgs_coverage):
    """numbldgs is present but its own coverage_status makes it unusable -
    treated the SAME as absent (never guessed)."""
    rule_evaluation = S.canonical_rule_evaluation()
    document = build_scenario(
        profile_with_bldgarea(
            0.0, numbldgs={"value": 0.0, "coverage_status": bad_numbldgs_coverage}
        ),
        rule_evaluation,
    )
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.EXISTING_BUILDING_AREA_UNUSABLE.value
    assert section["professional_review_required"] is True


def test_s1_zero_with_nonnumeric_numbldgs_fails_closed():
    """numbldgs has a usable coverage_status but a malformed (non-numeric)
    value - fails closed, never coerced or guessed."""
    rule_evaluation = S.canonical_rule_evaluation()
    document = build_scenario(
        profile_with_bldgarea(
            0.0, numbldgs={"value": "one", "coverage_status": "conditional"}
        ),
        rule_evaluation,
    )
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.EXISTING_BUILDING_AREA_UNUSABLE.value
    assert section["professional_review_required"] is True


def test_s1_fractional_remainder_is_unrounded():
    """G4 correction C2: a fractional remainder survives verbatim - real caps
    (FAR x lot area) and PLUTO bldgareas are frequently fractional, so a
    round() introduced at the subtraction site must fail this test (the
    integer-only fixtures elsewhere cannot discriminate it)."""
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    bldgarea = cap - 4999.5  # fractional remainder, exactly representable
    document = build_scenario(profile_with_bldgarea(bldgarea), rule_evaluation)
    validate_scenario_document(document)

    section = _section(document)
    assert section["state"] == State.COMPUTED.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] == cap - bldgarea
    assert section["unused_draft_zoning_floor_area_sq_ft"] == 4999.5
    # The discriminator: any rounding yields 5000.0, not 4999.5.
    assert section["unused_draft_zoning_floor_area_sq_ft"] != round(cap - bldgarea)


# ---------------------------------------------------------------------------
# S4 - missing or unusable existing area -> typed not_computable, value null.
# ---------------------------------------------------------------------------


def test_s4a_missing_existing_area_fact_is_not_computable():
    rule_evaluation = S.canonical_rule_evaluation()
    # (a) no bldgarea fact at all.
    doc_no_fact = build_scenario(
        profile_with_bldgarea(None, with_fact=False), rule_evaluation
    )
    validate_scenario_document(doc_no_fact)
    section = _section(doc_no_fact)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.MISSING_EXISTING_BUILDING_AREA.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None  # never estimated
    assert section["unit"] is None
    assert section["professional_review_required"] is False
    # The cap and the rest of the scenario document are unchanged (still a cap).
    assert doc_no_fact["draft_zoning_floor_area_cap_sq_ft"] == S.trace_cap(rule_evaluation)

    # (a') bldgarea fact present but its value is null.
    doc_null = build_scenario(profile_with_bldgarea(None, with_fact=True), rule_evaluation)
    validate_scenario_document(doc_null)
    assert (
        _section(doc_null)["not_computable_reason"]
        == Reason.MISSING_EXISTING_BUILDING_AREA.value
    )
    assert _section(doc_null)["unused_draft_zoning_floor_area_sq_ft"] is None


@pytest.mark.parametrize("bad_status", ["data_conflict", "unsupported"])
def test_s4b_unusable_existing_area_echoes_coverage_status(bad_status):
    rule_evaluation = S.canonical_rule_evaluation()
    document = build_scenario(
        profile_with_bldgarea(9000.0, coverage_status=bad_status), rule_evaluation
    )
    validate_scenario_document(document)
    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert (
        section["not_computable_reason"]
        == Reason.EXISTING_BUILDING_AREA_UNUSABLE.value
    )
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None  # never substituted
    # The fact's coverage_status is echoed VERBATIM.
    assert section["inputs"]["existing_building_floor_area"]["coverage_status"] == bad_status
    assert section["professional_review_required"] is False


def test_s4b_present_but_nonnumeric_value_is_unusable():
    """A present, non-null bldgarea value that is not a usable finite non-negative
    number fails closed to unusable - never coerced, never estimated."""
    rule_evaluation = S.canonical_rule_evaluation()
    for bad_value in ("9000", -1.0, float("nan")):
        document = build_scenario(
            profile_with_bldgarea(bad_value), rule_evaluation
        )
        validate_scenario_document(document)
        section = _section(document)
        assert section["state"] == State.NOT_COMPUTABLE.value
        assert (
            section["not_computable_reason"]
            == Reason.EXISTING_BUILDING_AREA_UNUSABLE.value
        )
        assert section["unused_draft_zoning_floor_area_sq_ft"] is None


# ---------------------------------------------------------------------------
# S5 - every no-cap path carries the section, state not_computable / no_draft_far_cap.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [
        S.unsupported_rule_evaluation,
        S.not_applicable_rule_evaluation,
        S.conflict_rule_evaluation,
        S.professional_review_rule_evaluation,
        S.missing_lot_area_rule_evaluation,
        S.integrity_disagreement_rule_evaluation,
    ],
)
def test_s5_no_cap_paths_are_no_draft_far_cap(rule_evaluation_factory):
    # A bldgarea fact IS present, proving the reason is the ABSENT CAP, not a
    # missing existing area (no subtraction is attempted without a cap).
    document = build_scenario(
        profile_with_bldgarea(9000.0), rule_evaluation_factory()
    )
    validate_scenario_document(document)
    section = _section(document)
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.NO_DRAFT_FAR_CAP.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None
    assert section["formula"] is None
    assert section["assumptions"] == []  # nothing computed -> no assumption asserted
    assert section["professional_review_required"] is False  # section adds no PRR here


def test_s5_section_is_present_on_degenerate_empty_inputs():
    document = build_scenario({}, {})
    validate_scenario_document(document)
    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.NO_DRAFT_FAR_CAP.value


# ---------------------------------------------------------------------------
# Root professional_review_required OR semantics: BOTH triggers pinned.
# ---------------------------------------------------------------------------


def test_root_prr_or_semantics_both_triggers():
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)

    # Trigger 1 - over-built section on an otherwise-clean preliminary path.
    over = build_scenario(profile_with_bldgarea(cap + 1.0), rule_evaluation)
    assert over["professional_review_required"] is True
    assert _section(over)["state"] == State.OVER_BUILT.value

    # Trigger 2 - rule-evaluation fail-safe, section not_computable (adds no PRR),
    # yet root stays True from the rule-evaluation trigger.
    fail_safe = build_scenario(
        profile_with_bldgarea(9000.0), S.professional_review_rule_evaluation()
    )
    assert fail_safe["professional_review_required"] is True
    assert _section(fail_safe)["professional_review_required"] is False

    # Neither trigger - a computed (non-negative) remainder keeps root False.
    clean = build_scenario(profile_with_bldgarea(cap - 1.0), rule_evaluation)
    assert clean["professional_review_required"] is False


# ---------------------------------------------------------------------------
# S6 - contract / renderer-parity JSON safety / precise-noun discipline.
# ---------------------------------------------------------------------------


def _all_states_documents():
    re = S.canonical_rule_evaluation
    cap = S.trace_cap(re())
    return [
        ("computed", build_scenario(profile_with_bldgarea(cap - 100.0), re())),
        ("zero", build_scenario(profile_with_bldgarea(cap), re())),
        ("over_built", build_scenario(profile_with_bldgarea(cap + 100.0), re())),
        ("missing", build_scenario(profile_with_bldgarea(None, with_fact=False), re())),
        (
            "unusable",
            build_scenario(profile_with_bldgarea(1.0, coverage_status="unsupported"), re()),
        ),
        ("no_cap", build_scenario(profile_with_bldgarea(1.0), S.conflict_rule_evaluation())),
    ]


def test_s6_both_schema_copies_are_byte_identical():
    assert BUNDLED_SCHEMA.read_bytes() == CANONICAL_SCHEMA.read_bytes()


def test_s6_new_key_is_required_and_fully_specified_and_closed():
    schema = json.loads(CANONICAL_SCHEMA.read_text(encoding="utf-8"))
    assert "unused_draft_zoning_floor_area" in schema["required"]
    assert schema["properties"]["unused_draft_zoning_floor_area"] == {
        "$ref": "#/$defs/unused_draft_zoning_floor_area"
    }
    section_def = schema["$defs"]["unused_draft_zoning_floor_area"]
    assert section_def["additionalProperties"] is False
    assert section_def["type"] == "object"
    # inputs sub-object is closed too.
    assert schema["$defs"]["unused_floor_area_inputs"]["additionalProperties"] is False


def test_s6_every_state_survives_strict_and_utf8_json():
    for label, document in _all_states_documents():
        validate_scenario_document(document)
        # Renderer-parity rule (M5-T012): both must succeed for every state.
        text = json.dumps(document, allow_nan=False)
        encoded = json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")
        assert text, label
        assert encoded, label


def test_s6_no_forbidden_nouns_and_no_verified_compliant_language():
    forbidden = ("maximum buildable area", "remaining development rights", "remaining capacity")
    strings = [
        C.UNUSED_FLOOR_AREA_LABEL,
        C.UNUSED_FLOOR_AREA_SCOPE_NOTE,
        C.UNUSED_FLOOR_AREA_OVER_BUILT_STATEMENT,
        C.UNUSED_FLOOR_AREA_FORMULA,
        C.zoning_lot_extent_assumption()["rationale"],
        C.zoning_lot_extent_assumption()["value"],
    ]
    for text in strings:
        low = text.lower()
        for phrase in forbidden:
            assert phrase not in low, (phrase, text)
        assert "verified" not in low, text
        assert "compliant" not in low, text


def test_s6_section_present_and_valid_on_every_state():
    for label, document in _all_states_documents():
        section = document["unused_draft_zoning_floor_area"]
        # Every state carries the full closed shape.
        assert set(section) == {
            "state",
            "unused_draft_zoning_floor_area_sq_ft",
            "unit",
            "label",
            "scope_note",
            "formula",
            "professional_review_required",
            "over_built_statement",
            "not_computable_reason",
            "inputs",
            "assumptions",
        }, label
        assert section["label"] == UNUSED_FLOOR_AREA_LABEL


def test_section_is_deterministic():
    re = S.canonical_rule_evaluation
    prof = profile_with_bldgarea(9000.0)
    first = build_scenario(prof, re())
    second = build_scenario(profile_with_bldgarea(9000.0), re())
    assert json.dumps(first) == json.dumps(second)


def test_direct_pure_function_computed_and_verbatim_cap():
    """The pure function is exercised directly (edge coverage). The cap is consumed
    VERBATIM (a separate float subtraction never mutates the echoed cap value)."""
    prof = profile_with_bldgarea(4000.0)
    section = build_unused_floor_area_section(
        property_profile=prof, cap_value=10000.0, cap_provenance={"echoed": "verbatim"}
    )
    assert section["state"] == State.COMPUTED.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] == 6000.0
    # cap provenance echoed verbatim, not reshaped.
    assert section["inputs"]["draft_zoning_floor_area_cap"]["provenance"] == {
        "echoed": "verbatim"
    }


def test_direct_pure_function_zero_cap_is_no_draft_far_cap():
    # A non-positive cap is treated as no cap (build_scenario only surfaces
    # strictly-positive caps); the function fails closed to no_draft_far_cap.
    for bad_cap in (0.0, -5.0, None, float("nan"), "x"):
        section = build_unused_floor_area_section(
            property_profile={}, cap_value=bad_cap, cap_provenance=None
        )
        assert section["state"] == State.NOT_COMPUTABLE.value
        assert section["not_computable_reason"] == Reason.NO_DRAFT_FAR_CAP.value


def test_builder_does_not_mutate_profile_with_bldgarea():
    import copy

    prof = profile_with_bldgarea(9000.0)
    snapshot = copy.deepcopy(prof)
    build_scenario(prof, S.canonical_rule_evaluation())
    assert prof == snapshot
