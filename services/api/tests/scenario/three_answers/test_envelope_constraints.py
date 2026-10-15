"""The envelope-constraint checks from NB-06 (task M5-T170): the street wall, the setback above
the base, and the side yard, with ONE test per input state (RULE 2), the texts guard (RULE 3) and
the no-default-for-a-fact proofs (RULE 1). Expected outcomes come from the R6B reference case
(docs/reference-cases/R6B/cases/overlay-reading.json) and the law (NB-06), never a program run.
"""

from __future__ import annotations

import pytest

from app.connectors.dcm_street_width_classifier import classify_street_width
from app.connectors.dcm_street_width_policy import (
    FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
    AttestedPreconditions,
    classify_street_width_policy,
)
from app.scenario.three_answers.envelope_constraints import (
    BUILDING_MIXED,
    BUILDING_MULTI_FAMILY,
    BUILDING_RESIDENTIAL_ONLY,
    BUILDING_SINGLE_TWO_FAMILY_DETACHED,
    SETBACK_DEPTH_NARROW_FT,
    SETBACK_DEPTH_WIDE_FT,
    STREET_WALL_OFFSET_FT,
    STREET_WALL_OFFSET_NARROW_NO_OVERLAY_FT,
    WIDTH_NARROW,
    WIDTH_UNKNOWN,
    WIDTH_UNRESOLVED,
    WIDTH_WIDE,
    Frontage,
    build_envelope_analysis,
)

WIDE = Frontage("Northern Boulevard", WIDTH_WIDE, 100.0)
NARROW = Frontage("215 Place", WIDTH_NARROW, 60.0)
UNRESOLVED = Frontage("Some Street", WIDTH_UNRESOLVED, None)
UNKNOWN = Frontage("Other Street", WIDTH_UNKNOWN, None)


def _build(**kw):
    base = dict(
        overlay_present=True,
        building_type=BUILDING_RESIDENTIAL_ONLY,
        frontages=(WIDE, NARROW),
        street_wall_height_ft=30.0,
        max_base_height_ft=45.0,
        source_title="NYC Department of City Planning MapPLUTO",
        source_date="2026-09-30",
    )
    base.update(kw)
    return build_envelope_analysis(**base)


def _row(analysis, kind):
    return next(r for r in analysis.envelope_rows if r["kind"] == kind)


def _values(row):
    return {v["name"]: v["value"] for v in row.get("values", [])}


# --------------------------------------------------------------------------- street wall (S3)
def test_street_wall_always_applies_and_is_conditional():
    row = _row(_build(), "street_wall")
    assert row["state"] == "applies"
    # Conditional on the prevailing-frontage test and the operative street line (never settled).
    assumptions = " ".join(c["assumption"] for c in row["conditions"])
    assert "prevailing street wall" in assumptions
    assert "operative street line" in assumptions


@pytest.mark.parametrize("building_type", [BUILDING_RESIDENTIAL_ONLY, BUILDING_MIXED])
def test_street_wall_overlay_is_eight_feet_each_frontage_for_both_building_types(building_type):
    # overlay -> 35-631(b): 8 ft on each frontage, wide or narrow alike (S3).
    row = _row(_build(overlay_present=True, building_type=building_type), "street_wall")
    vals = _values(row)
    assert set(vals.values()) == {STREET_WALL_OFFSET_FT}
    assert len(vals) == 2
    assert "ZR 35-631" in row["zr_sections"]
    expected = "ZR 35-01" if building_type == BUILDING_MIXED else "ZR 34-24"
    assert expected in row["zr_sections"]


def test_street_wall_no_overlay_is_eight_wide_ten_narrow_never_collapsed():
    # no overlay -> 23-431(b): 8 ft wide / 10 ft narrow, the D-051 asymmetry, never collapsed (S3).
    row = _row(_build(overlay_present=False), "street_wall")
    vals = _values(row)
    assert vals["Street wall within this distance of the Northern Boulevard street line"] == \
        STREET_WALL_OFFSET_FT
    assert vals["Street wall within this distance of the 215 Place street line"] == \
        STREET_WALL_OFFSET_NARROW_NO_OVERLAY_FT
    assert STREET_WALL_OFFSET_FT != STREET_WALL_OFFSET_NARROW_NO_OVERLAY_FT
    assert "ZR 23-431" in row["zr_sections"]


def test_street_wall_no_overlay_unknown_width_shows_no_distance_never_narrow():
    # RULE 1 / D-051: an unknown-width frontage without the overlay shows NO distance (never the
    # 10-ft narrow value by default).
    row = _row(_build(overlay_present=False, frontages=(WIDE, UNKNOWN)), "street_wall")
    vals = _values(row)
    assert "Street wall within this distance of the Other Street street line" not in vals
    assert STREET_WALL_OFFSET_NARROW_NO_OVERLAY_FT not in vals.values()


def test_street_wall_overlay_not_read_withholds_the_distance():
    # RULE 1: overlay not read -> the rule (and the distance) depend on whether an overlay is
    # mapped; no distance shown, the dependency named as a condition, never defaulted.
    row = _row(_build(overlay_present=None), "street_wall")
    assert row["state"] == "applies"
    assert "values" not in row
    assert any("commercial overlay is mapped" in c["assumption"] for c in row["conditions"])


def test_street_wall_building_type_not_stated_carries_a_named_condition():
    # RULE 1: a building type not stated is never taken as residential-only; the pathway is a named
    # condition, and both pathways still reach 35-631(b) under the overlay (8 ft).
    row = _row(_build(building_type=None), "street_wall")
    assert set(_values(row).values()) == {STREET_WALL_OFFSET_FT}
    assert any("all-residential" in c["assumption"] for c in row["conditions"])


# --------------------------------------------------------------------------- setback (S1, S2)
@pytest.mark.parametrize(
    "height,triggered",
    [(30.0, False), (44.99, False), (45.00, False), (45.01, True), (50.0, True)],
)
def test_setback_trigger_table_strict_above_the_maximum_base_height(height, triggered):
    # S2: 30 / 44.99 / 45.00 -> not triggered (not strictly above the 45 ft maximum base height);
    # 45.01 / 50 -> triggered. 45.00 is NEVER printed as triggered.
    row = _row(_build(street_wall_height_ft=height), "setback")
    assert row["state"] == ("applies" if triggered else "not_applicable")
    if not triggered:
        assert "no setback" in row["text"].lower()
        assert "triggered" not in row["text"].lower()


def test_setback_depths_are_ten_wide_fifteen_narrow_cited():
    # S1: wide (Northern Boulevard) 10 ft, narrow (215 Place) 15 ft, cited to 23-433; one basis.
    row = _row(_build(street_wall_height_ft=50.0), "setback")
    assert row["state"] == "applies"
    vals = _values(row)
    assert vals["Setback depth above the maximum base height on the Northern Boulevard frontage"] \
        == SETBACK_DEPTH_WIDE_FT
    assert vals["Setback depth above the maximum base height on the 215 Place frontage"] \
        == SETBACK_DEPTH_NARROW_FT
    assert "ZR 23-433" in row["zr_sections"]


def test_setback_not_applicable_carries_the_depths_and_the_above_base_condition():
    # S7: the 30 ft option is not triggered, but carries the 10/15 ft depths as values and a
    # condition naming the above-45-ft trigger.
    row = _row(_build(street_wall_height_ft=30.0), "setback")
    assert row["state"] == "not_applicable"
    assert set(_values(row).values()) == {SETBACK_DEPTH_WIDE_FT, SETBACK_DEPTH_NARROW_FT}
    assert any("above the 45 ft maximum base height" in c["assumption"] for c in row["conditions"])


def test_triggered_setback_notes_the_depths_are_minimums_subject_to_23_433():
    # G1 F3: a triggered setback row says the 10/15 ft depths are the least the setback must be and
    # that ZR 23-433(a) to (d) may reduce or waive them (plain user words). The benchmark triggers
    # no setback, so this condition does not appear on the shipped print.
    row = _row(_build(street_wall_height_ft=50.0), "setback")
    assert row["state"] == "applies"
    blob = " ".join(c["assumption"] for c in row["conditions"]).lower()
    assert "23-433(a) to (d)" in blob
    assert "least" in blob or "minimum" in blob


def test_not_triggered_setback_carries_no_minimums_condition():
    # The minimums-are-subject-to-23-433 note belongs only to a TRIGGERED row; the benchmark
    # (30 ft, not triggered) does not carry it.
    row = _row(_build(street_wall_height_ft=30.0), "setback")
    assert row["state"] == "not_applicable"
    blob = " ".join(c["assumption"] for c in row["conditions"]).lower()
    assert "23-433(a) to (d)" not in blob


def test_setback_height_not_stated_is_conditional_never_not_known():
    # RULE 1 / R061: the law is known (a setback above the maximum base height); whether the
    # building reaches above it is a named condition, never not_known.
    row = _row(_build(street_wall_height_ft=None), "setback")
    assert row["state"] == "applies"
    assert any("rises above" in c["assumption"] for c in row["conditions"])


# --------------------------------------------------------------------------- width -> depth (S5)
def _classify(raw):
    """The D-052 wide/narrow decision for one mapped-width string, through the ACCEPTED classifier
    and policy with every precondition attested (the reuse S5 requires)."""
    pre = AttestedPreconditions(
        source_documented=True, source_version="v1", street_status_checked=True,
        frontage_match_method=FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
        matched_geometry_ref="seg-1", exceptions_checked=True,
    )
    return classify_street_width_policy(classify_street_width(raw), pre).decision_state


@pytest.mark.parametrize(
    "raw,expected_class,expected_depth",
    [
        ("100", WIDTH_WIDE, SETBACK_DEPTH_WIDE_FT),
        ("75.00", WIDTH_WIDE, SETBACK_DEPTH_WIDE_FT),
        ("60", WIDTH_NARROW, SETBACK_DEPTH_NARROW_FT),
        ("74.99", WIDTH_NARROW, SETBACK_DEPTH_NARROW_FT),
        ("60-75", WIDTH_UNRESOLVED, None),
        ("<=75", WIDTH_UNRESOLVED, None),
        (None, WIDTH_UNKNOWN, None),
        ("garbled nonsense", WIDTH_UNKNOWN, None),
    ],
)
def test_per_frontage_width_class_drives_the_setback_depth(raw, expected_class, expected_depth):
    # S5 via the reused D-052 classifier: wide 10 ft, narrow 15 ft; one-sided-straddle UNRESOLVED
    # and missing/garbled UNKNOWN both withhold the depth; never narrow by default (D-051).
    assert _classify(raw) == expected_class
    f = Frontage("Test Street", expected_class, None)
    row = _row(_build(street_wall_height_ft=50.0, frontages=(f,)), "setback")
    depth = _values(row).get("Setback depth above the maximum base height on the Test Street "
                             "frontage")
    assert depth == expected_depth
    if expected_depth is None:
        assert depth != SETBACK_DEPTH_NARROW_FT  # never narrow by default


# --------------------------------------------------------------------------- side yard (S4)
def test_side_yard_multi_family_none_required():
    row = _row(_build(building_type=BUILDING_MULTI_FAMILY, overlay_present=False), "side_yard")
    assert row["state"] == "not_applicable"
    assert "ZR 23-335" in row["zr_sections"]


def test_side_yard_mixed_none_required():
    row = _row(_build(building_type=BUILDING_MIXED), "side_yard")
    assert row["state"] == "not_applicable"


def test_side_yard_mixed_leads_with_23_335b_not_34_232():
    # G1 F2: a mixed building reaches "no side yard required" through the Chapter 5 bulk (ZR 35-01
    # -> 23-335(b)); 34-232 by its words governs a residential building only, and 35-24 is not
    # captured. The citation (not only the state) is asserted. The shipped benchmark is
    # residential-only, so the printed report is unaffected.
    row = _row(_build(building_type=BUILDING_MIXED, overlay_present=True), "side_yard")
    assert row["state"] == "not_applicable"
    assert "23-335(b)" in row["text"]
    assert "ZR 23-335" in row["zr_sections"]
    assert "ZR 35-01" in row["zr_sections"]
    assert "ZR 34-232" not in row["zr_sections"]  # 34-232 reaches a residential building only
    assert "ZR 35-24" not in row["zr_sections"]   # 35-24 is not captured, never cited


def test_side_yard_residential_in_overlay_keeps_34_232():
    # A residential (not mixed) building in the overlay keeps the 34-232 citation.
    row = _row(_build(building_type=BUILDING_RESIDENTIAL_ONLY, overlay_present=True), "side_yard")
    assert row["state"] == "not_applicable"
    assert "ZR 34-232" in row["zr_sections"]


def test_side_yard_detached_in_overlay_none_required():
    row = _row(_build(building_type=BUILDING_SINGLE_TWO_FAMILY_DETACHED, overlay_present=True),
               "side_yard")
    assert row["state"] == "not_applicable"
    assert "ZR 34-232" in row["zr_sections"]


def test_side_yard_detached_without_overlay_two_five_foot_yards():
    row = _row(_build(building_type=BUILDING_SINGLE_TWO_FAMILY_DETACHED, overlay_present=False),
               "side_yard")
    assert row["state"] == "applies"
    assert row["values"][0]["value"] == 5.0
    assert "ZR 23-335" in row["zr_sections"]


def test_side_yard_open_area_minimum_is_five_feet():
    row = _row(_build(building_type=BUILDING_MULTI_FAMILY), "side_yard")
    assert any("at least 5 feet" in c["assumption"] for c in row["conditions"])


def test_side_yard_building_type_not_stated_without_overlay_names_the_detached_case():
    # RULE 1: not stated is never taken as residential-only; the detached case is a named condition.
    row = _row(_build(building_type=None, overlay_present=False), "side_yard")
    assert row["state"] == "not_applicable"
    assert any("detached" in c["assumption"] for c in row["conditions"])


# --------------------------------------------------------------------------- constraint lines (S6)
def test_constraint_lines_not_established_without_an_operative_street_line():
    # S6 / D-094-R017: the benchmark (no operative street line) -> street_wall_band and setback_line
    # both not_established, carrying basis + zr_sections and NO geometry.
    lines = {c["kind"]: c for c in _build().constraint_lines}
    for kind in ("street_wall_band", "setback_line"):
        assert lines[kind]["state"] == "not_established"
        assert "geometry" not in lines[kind]
        assert lines[kind]["basis"] == "derived"
        assert lines[kind]["zr_sections"]


def test_street_wall_band_established_when_a_geometry_is_supplied():
    # S6: a constructed case with the band computed from an operative street line -> established,
    # carrying its geometry.
    band = [[0.0, 0.0], [8.0, 0.0], [8.0, 20.0], [0.0, 20.0]]
    lines = {c["kind"]: c for c in _build(street_wall_band_geometry=band).constraint_lines}
    assert lines["street_wall_band"]["state"] == "established"
    assert lines["street_wall_band"]["geometry"] == band


# --------------------------------------------------------------------------- input facts (S14)
def test_input_facts_are_gis_mapped_widths_one_per_frontage_with_provenance():
    facts = _build().input_facts
    assert [f["key"] for f in facts] == [
        "mapped_street_width:Northern Boulevard", "mapped_street_width:215 Place",
    ]
    for f in facts:
        assert f["basis"] == "gis"  # a DCM mapped width is a GIS value, never recorded/tax-map
        assert f["unit"] == "ft"
        assert f["source_title"] and f["source_date"]


def test_no_input_fact_without_provenance():
    # D-093: no source title or date -> no fact invented.
    assert _build(source_title="", source_date="").input_facts == []


def test_no_input_fact_for_a_frontage_without_a_mapped_width():
    facts = _build(frontages=(WIDE, UNKNOWN)).input_facts  # UNKNOWN has no mapped width
    assert [f["key"] for f in facts] == ["mapped_street_width:Northern Boulevard"]


# --------------------------------------------------------------------------- R061 / S8
def test_no_envelope_row_is_ever_not_known():
    # S8: none of the three rows is state not_known; the genuine unknowns are named conditions.
    analysis = _build(overlay_present=None, building_type=None, street_wall_height_ft=None,
                      frontages=(UNKNOWN,))
    assert all(r["state"] != "not_known" for r in analysis.envelope_rows)


# --------------------------------------------------------------------------- RULE 3 texts guard
_FORBIDDEN = (
    "captur", "reference case", "milestone", "m5-t", "the caller", "is built", "db-",
    "fixture", "step-p", "nb-0", "professional review", "gap (",
)


def test_emitted_texts_are_plain_user_texts():
    # RULE 3: every emitted text and condition is plain user language - no record id, no internal
    # name, no claim about which law text is captured or built.
    cases = [
        _build(),
        _build(overlay_present=False),
        _build(overlay_present=None, building_type=None),
        _build(street_wall_height_ft=50.0),
        _build(building_type=BUILDING_SINGLE_TWO_FAMILY_DETACHED, overlay_present=False),
        _build(frontages=(UNRESOLVED, UNKNOWN)),
    ]
    for analysis in cases:
        texts = []
        for row in analysis.envelope_rows:
            texts.append(row["text"].lower())
            for c in row.get("conditions", []):
                texts.append(c["assumption"].lower())
                texts.append(c["settled_by"].lower())
        blob = " ".join(texts)
        for bad in _FORBIDDEN:
            assert bad not in blob, f"forbidden {bad!r} in an emitted text"
        # every row text is a short, labelled draft reading (page-3 summary, like the rear-yard
        # combined row): it names its law section and reads as a draft/conditional reading.
        for row in analysis.envelope_rows:
            assert "reading" in row["text"].lower()
            assert row["zr_sections"]
