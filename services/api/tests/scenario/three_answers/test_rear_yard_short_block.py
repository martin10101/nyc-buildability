"""Scenario tests for the ZR 23-344 rear-yard checks (task M5-T167, steps 3-4).

These pin the result-deciding behaviour of
:mod:`app.scenario.three_answers.rear_yard_checks` against the R6B reference case
(docs/reference-cases/R6B), never against a program run. They implement the THREE RULES the
packet requires:

RULE 1 - no default stands for a fact: for every input the "not given"/"not known" state holds the
dependent result back (not known), never read as "no". There is no truthiness test on an optional
fact that would read an unknown as "no" (an empty district is not known, not "outside R6-R12").

RULE 2 - one test per input state, with a table: the (b) short-dimension test, the (a) corner
waiver and the (c)(3) adjoining-side-line test each carry a state table below.

RULE 3 - returned texts are user texts: a guard over the whole battery of emitted texts forbids
internal names (gap/reading numbers, "reference case", "milestone", task ids, "the caller"), any
claim that law text is "captured" or "built", and any unconditional "no rear yard"; it also checks
the corner waiver (a) is never the only exception named ((b) and (c)(3) are named too).
"""
from __future__ import annotations

import json

import pytest

from app.scenario.three_answers.rear_yard_checks import (
    SHORT_DIMENSION_MAX_230,
    CapturedMeasure,
    RearYardAnalysis,
    build_rear_yard_analysis,
    classify_short_dimension,
)
from app.spatial.site_geometry.block_frontage import BlockFrontageMeasure

# The benchmark real-lot facts (docs/reference-cases/R6B/cases/real-lot.json): corner angle about
# 89.7 degrees, the lot reaches about 144.60 ft from the corner, recorded lot area 10,075 sq ft,
# the MapPLUTO outline area 10,387.99 sq ft. The measurement basis for the short dimension is
# unresolved law, so basis_fixed_by_law stays False on every real-lot path.
_SOURCE_TITLE = "NYC Department of City Planning MapPLUTO"
_SOURCE_DATE = "2026-10-10"


def _bf(basis: str | None = None, sep: float | None = None) -> BlockFrontageMeasure:
    if basis is None or sep is None:
        return BlockFrontageMeasure()
    return BlockFrontageMeasure(separations={basis: sep})


def _analysis(**over) -> RearYardAnalysis:
    kwargs = dict(
        corner_reach_ft=144.60,
        corner_angle_deg=89.7,
        district="R6B",
        block_frontage=_bf("gis", 203.13),
        recorded_area_sqft=10075.0,
        outline_area_sqft=10387.99,
        source_title=_SOURCE_TITLE,
        source_date=_SOURCE_DATE,
        basis_fixed_by_law=False,
    )
    kwargs.update(over)
    return build_rear_yard_analysis(**kwargs)


def _check(analysis: RearYardAnalysis, provision: str) -> dict:
    return next(c for c in analysis.rear_yard["checks"] if c["provision"] == provision)


# --------------------------------------------------------------------------
# RULE 2 - (b) the short dimension of a block: the strict "< 230 feet" table
# --------------------------------------------------------------------------
# input (separation_ft, basis_fixed_by_law) -> outcome; the test that pins it is this row.
SHORT_DIMENSION_TABLE = [
    (229.99, True, "applies"),          # M1: 229.99 < 230, strict
    (230.00, True, "not_applicable"),   # M2: exactly 230 is NOT short (strict)
    (230.01, True, "not_applicable"),   # M3: above 230
    (100.0, True, "applies"),           # a short block well under 230
    (260.0, False, "not_known"),        # real lot: basis unresolved law (>=230 on one basis)
    (203.13, False, "not_known"),       # real lot: a value < 230 on one basis still not known
    (None, True, "not_known"),          # not measured
    (None, False, "not_known"),         # not measured, real lot
]


@pytest.mark.parametrize("sep,fixed,state", SHORT_DIMENSION_TABLE)
def test_short_dimension_state_table(sep, fixed, state):
    basis = "printed_tax_map" if sep is not None else None
    got, reason = classify_short_dimension(sep, basis, basis_fixed_by_law=fixed)
    assert got == state
    assert reason  # every state carries a plain reason


def test_short_dimension_threshold_is_the_captured_230_strict():
    assert isinstance(SHORT_DIMENSION_MAX_230, CapturedMeasure)
    assert SHORT_DIMENSION_MAX_230.value == 230.0
    assert SHORT_DIMENSION_MAX_230.zr_section == "ZR 12-10"
    # strict: just under applies, exactly-230 and just over do not.
    assert classify_short_dimension(229.9999, "survey", basis_fixed_by_law=True)[0] == "applies"
    assert classify_short_dimension(230.0, "survey", basis_fixed_by_law=True)[0] == "not_applicable"


def test_229_996_is_never_printed_as_230():
    """S1: a separation below 230 is never printed as '230.00' - the printed value must not
    contradict the strict '< 230 feet' conclusion."""
    state, reason = classify_short_dimension(229.996, "survey", basis_fixed_by_law=True)
    assert state == "applies"
    assert "229.996" in reason
    assert "is 230 feet" not in reason and "is 230.00 feet" not in reason


def test_real_lot_short_dimension_is_not_known_whatever_the_measure():
    """S2/S9: for a real lot the measurement basis is unresolved law, so (b) is not known whatever
    the block-frontage measure found - a value at or above 230 ft on one basis cannot settle it."""
    for sep in (203.13, 229.99, 260.0):
        state, _ = classify_short_dimension(sep, "gis", basis_fixed_by_law=False)
        assert state == "not_known"


def test_check_b_not_applicable_text_omits_the_waiver_consequence():
    # DB-265 (5): a not_applicable (b) reading no longer appends the (b) waiver consequence
    # ("within 100 feet of that street line no rear yard would be required"), which only follows
    # where (b) actually applies. Reachable only with a stated basis (basis_fixed_by_law=True).
    not_applicable = _analysis(basis_fixed_by_law=True, block_frontage=_bf("survey", 260.0))
    b = _check(not_applicable, "23-344(b)")
    assert b["state"] == "not_applicable"
    assert "no rear yard would be required" not in b["text"]
    assert "not less than 230 feet" in b["text"]  # the not-applicable reason itself stays


def test_check_b_applies_text_keeps_the_waiver_consequence():
    # Where (b) applies, the waiver consequence is still stated (qualified by "within 100 feet").
    applies = _analysis(basis_fixed_by_law=True, block_frontage=_bf("survey", 229.99))
    b = _check(applies, "23-344(b)")
    assert b["state"] == "applies"
    assert "within 100 feet of that street line no rear yard would be required" in b["text"]


# --------------------------------------------------------------------------
# RULE 2 - (a) the corner-area waiver: the state table
# --------------------------------------------------------------------------
# input (corner_reach_ft, corner_angle_deg) -> (a) state; the test that pins it is this row.
CORNER_WAIVER_TABLE = [
    (None, 89.7, "not_known"),       # reach not measured
    (144.6, None, "not_known"),      # angle not measured
    (144.6, 150.0, "not_applicable"),  # angle above 135
    (144.6, 135.0, "applies"),       # exactly 135 qualifies
    (144.6, 89.7, "applies"),        # benchmark: a corner within 135, lot reaches beyond 100 ft
    (50.0, 89.7, "applies"),         # whole lot within 100 ft of the corner
]


@pytest.mark.parametrize("reach,angle,state", CORNER_WAIVER_TABLE)
def test_corner_waiver_state_table(reach, angle, state):
    check = _check(_analysis(corner_reach_ft=reach, corner_angle_deg=angle), "23-344(a)")
    assert check["state"] == state


def test_corner_waiver_reach_describes_coverage_but_is_not_the_only_exception():
    beyond = _check(_analysis(corner_reach_ft=144.6, corner_angle_deg=89.7), "23-344(a)")
    assert "within 100 feet" in beyond["text"]
    within = _check(_analysis(corner_reach_ft=50.0, corner_angle_deg=89.7), "23-344(a)")
    assert "within 100 feet" in within["text"]


# --------------------------------------------------------------------------
# RULE 2 - (c)(3) the adjoining zoning lot's side lot line: the district table
# --------------------------------------------------------------------------
# input district -> (c)(3) state; the test that pins it is this row (S10).
C3_DISTRICT_TABLE = [
    (None, "not_known"),      # RULE 1: not given is not known, never read as "no"
    ("", "not_known"),        # RULE 1: an empty district is not known, not "outside R6-R12"
    ("R6B", "not_known"),     # within R6-R12 (letter suffix); neighbours not captured
    ("R12", "not_known"),     # within range
    ("R7-1", "not_known"),    # within range
    ("R4B", "not_applicable"),  # plainly outside R6-R12
    ("R5", "not_applicable"),
    ("R3-2", "not_applicable"),
]


@pytest.mark.parametrize("district,state", C3_DISTRICT_TABLE)
def test_c3_district_state_table(district, state):
    check = _check(_analysis(district=district), "23-344(c)(3)")
    assert check["state"] == state


def test_c3_and_combined_texts_name_the_c1_alternative_besides_c3():
    # DB-265 (1): the (c)(3) check text and the combined row's conditions name the ZR 23-344(c)(1)
    # alternative - a rear yard IS required where the deemed rear lot line meets a neighbour's
    # rear lot line - besides the (c)(3) side-lot-line branch. State unchanged (not_known).
    analysis = _analysis(district="R6B")
    c3 = _check(analysis, "23-344(c)(3)")
    assert c3["state"] == "not_known"
    assert "23-344(c)(1)" in c3["text"] and "23-344(c)(3)" in c3["text"]
    assert "rear lot line" in c3["text"]
    conds = " ".join(c["assumption"] for c in analysis.rear_yard["combined"]["conditions"])
    assert "23-344(c)(1)" in conds and "23-344(c)(3)" in conds


# --------------------------------------------------------------------------
# RULE 1 - a not_known check carries NO number (schema oneOf); the combined row
# --------------------------------------------------------------------------
def test_not_known_checks_carry_no_number():
    analysis = _analysis()  # real lot: (b) and (c)(3) are not known
    for provision in ("23-344(b)", "23-344(c)(3)"):
        check = _check(analysis, provision)
        assert check["state"] == "not_known"
        assert "inputs" not in check  # no number for a not_known check


def test_combined_row_is_conditional_never_unconditional_no_rear_yard():
    """S13: the benchmark combined row is not known and shown as a conditional reading, never an
    unconditional 'no rear yard'; ZR 23-344(b) is linked and (c)(3) named besides the corner (a)."""
    analysis = _analysis()
    combined = analysis.rear_yard["combined"]
    assert combined["state"] == "not_known"
    assert combined["way"] == "conditional"
    assert combined["conditions"]  # the conditions that would settle it are named
    assert "ZR 23-344" in combined["zr_sections"]
    provisions = {c["provision"] for c in analysis.rear_yard["checks"]}
    assert provisions == {"23-344(a)", "23-344(b)", "23-344(c)(3)"}


# --------------------------------------------------------------------------
# RULE 1 - input_facts: no invented provenance; each value the calc value (S19/S24)
# --------------------------------------------------------------------------
def test_input_facts_equal_the_calculation_values_one_per_basis():
    analysis = _analysis(recorded_area_sqft=10075.0, outline_area_sqft=10387.99)
    facts = {f["key"]: f for f in analysis.input_facts}
    assert facts["recorded_lot_area"]["value"] == 10075.0
    assert facts["recorded_lot_area"]["basis"] == "administrative_record"
    assert facts["lot_outline_area"]["value"] == 10387.99
    assert facts["lot_outline_area"]["basis"] == "gis"
    # no second figure for one basis.
    bases = [f["basis"] for f in analysis.input_facts]
    assert len(bases) == len(set(bases))
    for fact in analysis.input_facts:
        assert fact["source_title"] and fact["source_date"]  # real provenance


def test_no_provenance_means_no_input_fact_invented():
    """RULE 1: with no source title or date, no input fact is invented."""
    assert _analysis(source_date="").input_facts == []
    assert _analysis(source_title="").input_facts == []


def test_a_missing_area_holds_its_fact_back():
    """RULE 1: a missing recorded or outline area is simply not emitted, never a default."""
    analysis = _analysis(recorded_area_sqft=None)
    keys = {f["key"] for f in analysis.input_facts}
    assert "recorded_lot_area" not in keys
    assert "lot_outline_area" in keys


def test_recorded_area_fact_moves_when_the_input_moves():
    """S24 (red/green): the emitted recorded_lot_area is the value passed in, not a constant; a
    different input moves the emitted value."""
    a1 = _analysis(recorded_area_sqft=10075.0)
    a2 = _analysis(recorded_area_sqft=9800.0)
    v1 = next(f for f in a1.input_facts if f["key"] == "recorded_lot_area")["value"]
    v2 = next(f for f in a2.input_facts if f["key"] == "recorded_lot_area")["value"]
    assert v1 == 10075.0 and v2 == 9800.0 and v1 != v2


# --------------------------------------------------------------------------
# S24 - every emitted constraint line lies within the lot (so not_known carries no geometry)
# --------------------------------------------------------------------------
def test_constraint_lines_carry_no_geometry_when_not_established():
    analysis = _analysis()
    assert analysis.constraint_lines  # the rear-yard lines are emitted as rows
    for line in analysis.constraint_lines:
        assert line["state"] == "not_known"
        assert "geometry" not in line  # a not_known line carries no geometry (within-lot invariant)


# --------------------------------------------------------------------------
# RULE 3 - returned texts are user texts
# --------------------------------------------------------------------------
_FORBIDDEN_TOKENS = [
    "gap (", "gap(", "reading 1", "reading 2", "reference case", "milestone", "m5-t",
    "the caller", "captur", "is built", "step-p", "db-", "schema", "fixture",
]


def _all_texts(analysis: RearYardAnalysis) -> list[str]:
    texts: list[str] = []
    for check in analysis.rear_yard["checks"]:
        texts.append(check["text"])
    combined = analysis.rear_yard["combined"]
    texts.append(combined["text"])
    for cond in combined.get("conditions", []):
        texts.append(cond.get("assumption", ""))
        texts.append(cond.get("settled_by", ""))
    for fact in analysis.input_facts:
        texts.append(fact["source_title"])
    return [t for t in texts if t]


@pytest.mark.parametrize(
    "analysis",
    [
        _analysis(),  # the real benchmark (not known / Conditional)
        _analysis(corner_angle_deg=150.0),  # (a) not applicable
        _analysis(corner_reach_ft=None, corner_angle_deg=None),  # (a) not known
        _analysis(district="R4B"),  # (c)(3) not applicable
        _analysis(basis_fixed_by_law=True, block_frontage=_bf("survey", 229.99)),  # (b) applies
    ],
)
def test_texts_are_plain_user_texts(analysis):
    for text in _all_texts(analysis):
        low = text.lower()
        for token in _FORBIDDEN_TOKENS:
            assert token not in low, f"internal token {token!r} leaked into a user text: {text!r}"


def test_no_unconditional_no_rear_yard_anywhere():
    """RULE 3 / S13: wherever 'no rear yard' appears it is qualified by 'within 100 feet' - never an
    unconditional 'no rear yard'."""
    for analysis in (_analysis(), _analysis(corner_reach_ft=50.0, corner_angle_deg=89.7)):
        blob = " ".join(_all_texts(analysis)).lower()
        start = 0
        while True:
            idx = blob.find("no rear yard", start)
            if idx == -1:
                break
            window = blob[idx:idx + 60]
            assert "within 100 feet" in window, f"unconditional 'no rear yard': ...{window}..."
            start = idx + 1


def test_checks_name_b_and_c3_besides_the_corner_waiver():
    """S11: the result names (b) and (c)(3) too, so the corner waiver (a) is never the only
    exception."""
    blob = json.dumps(_analysis().rear_yard)
    assert "23-344(a)" in blob
    assert "23-344(b)" in blob
    assert "23-344(c)(3)" in blob


def test_every_text_carries_the_not_a_dob_determination_disclaimer():
    analysis = _analysis()
    for check in analysis.rear_yard["checks"]:
        assert "Not a determination by the Department of Buildings." in check["text"]
