"""M4-T009 acceptance-scenario pack for the R1-R12 residential FAR draft rule
family - core scenarios AS-1, AS-2, AS-3, AS-4, AS-7, AS-8, AS-9.

AS-5 (source-digest binding: matching AND mismatched content) and AS-6 (each
district's qualifying alternative surfaced through the evaluation output) live in
the sibling module ``test_r1_r12_residential_far_provenance.py``; the pack was
split so neither module crosses the modularity warn threshold (AS-8 keeps the
authored test files warning-free). Together the two modules are the complete
acceptance evidence for AS-1 .. AS-9.

The family transcribes the maximum residential floor-area ratio for every
R1-R12 district from two committed, byte-verified source snapshots:

  * ``docs/research/zr-snapshots/v1/zr-23-21.snapshot.json`` - R1 through R5;
  * ``docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`` - R6 through R12.

Every assertion here LOADS the snapshot and compares against it; no expected FAR
value is restated as a literal in this file (AS-1: a test that hardcodes the same
number the rule hardcodes proves nothing - the M5-T004 G1/DCV tautology finding).

The registry under test is built against the CANONICAL ``docs`` snapshot source
(a superset of the packaged bundle) via the engine's supported explicit-directory
override, so the family is proven on its own merits. This is NOT a way around the
packaged-bundle guard tests: the packaged bundle (``app/_zr_snapshots/v1``) is
missing ``zr-23-22`` and carries a stale ``zr-23-21`` (digest ``4b6dd1f5...`` - the
superseded pre-recapture capture), so the DEFAULT (packaged) snapshot store cannot
load the R6-R12 rules that cite ``zr-23-22``. That drift is out of this task's file
scope (remediated only by ``services/api/scripts/sync_zr_snapshots.py`` writing under
``app/_zr_snapshots/``); it is routed to the orchestrator for corroboration and
separately authorized remediation and is deliberately left to FAIL the dedicated
default-store guards (``test_zr_snapshot_bundle.py``) rather than being masked here.
See ``project-control/reports/M4-T009-producer-report.md``.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.rules import RuleRegistry
from app.rules import coverage as cov
from app.rules.operations import COMPUTE_OPS
from app.rules.snapshots import SnapshotStore

# test file: <root>/services/api/tests/rules/test_r1_r12_residential_far.py
_ENGINE_DIR = Path(__file__).resolve().parents[2] / "app" / "rules"
_REPO_ROOT = Path(__file__).resolve().parents[4]
_RULESET_DIR = _ENGINE_DIR / "rulesets"
_DOCS_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"

_EFFECTIVE_FROM = "2024-12-05"
_FOOTNOTE_1_CAP_EXCEPTION_ID = "single_dwelling_unit_equivalent_far_cap"

# rule_id -> ruleset filename. Each rule cites exactly one snapshot (see AS-5).
_FLAT_RULES = {
    "r1-r2-r3-residential-far": "r1_r2_r3_residential_far.rule.json",
    "r2x-r4-residential-far": "r2x_r4_residential_far.rule.json",
    "r5-residential-far": "r5_residential_far.rule.json",
    "r6-r12-residential-far": "r6_r12_residential_far.rule.json",
}
_CONDITIONAL_RULE = "r6-r7-r8-wide-street-conditional-far"
_CONDITIONAL_FILE = "r6_r7_r8_wide_street_conditional_far.rule.json"
_ALL_FAR_RULES = {**_FLAT_RULES, _CONDITIONAL_RULE: _CONDITIONAL_FILE}

# The four ZR 23-22 districts footnote 1 conditions on wide-street proximity.
_CONDITIONAL_DISTRICTS = ("R6", "R7-1", "R7-2", "R8")

# AS-2: every district in the two snapshots is covered by an authored rule.
# No district is intentionally excluded; an empty exclusion list is asserted so a
# future silent drop is visible rather than tolerated.
_DOCUMENTED_EXCLUSIONS: dict[str, str] = {}


# --------------------------------------------------------------------------
# Fixtures / snapshot helpers - everything is loaded from the committed source.
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def registry() -> RuleRegistry:
    """Registry over the production rulesets, resolving citations against the
    CANONICAL docs snapshot source (a superset of the packaged bundle)."""
    return RuleRegistry(_RULESET_DIR, snapshots=SnapshotStore(_DOCS_SNAPSHOT_DIR)).load()


def _rule_doc(rule_id: str) -> dict:
    return json.loads((_RULESET_DIR / _ALL_FAR_RULES[rule_id]).read_text("utf-8"))


def _snapshot_raw(snapshot_id: str) -> dict:
    return json.loads((_DOCS_SNAPSHOT_DIR / f"{snapshot_id}.snapshot.json").read_text("utf-8"))


def _row_values(row: dict) -> tuple[str, str]:
    """(standard, qualifying) value STRINGS for a table row, tolerating the two
    column-naming schemes (23-21 vs 23-22)."""
    if "standard_zoning_lots" in row:
        return row["standard_zoning_lots"], row["qualifying_residential_sites"]
    return row["standard_residences"], row["qualifying_affordable_or_senior_housing"]


def _district_rows(snapshot_id: str) -> dict[str, list[dict]]:
    """Map each district -> the list of table rows it appears in. A flat district
    appears in exactly one row; a wide-street-conditional district appears twice."""
    out: dict[str, list[dict]] = {}
    for row in _snapshot_raw(snapshot_id)["table"]["rows"]:
        std, qual = _row_values(row)
        for district in row["districts"]:
            out.setdefault(district, []).append(
                {
                    "standard": std,
                    "qualifying": qual,
                    "value_footnotes": row.get("value_footnotes", {}),
                    "district_footnotes": row.get("district_footnotes", {}),
                }
            )
    return out


def _all_snapshot_districts(snapshot_id: str) -> set[str]:
    return set(_district_rows(snapshot_id))


def _rule_snapshot_id(rule_id: str) -> str:
    """Every rule in this family cites exactly one snapshot; return its id."""
    citations = _rule_doc(rule_id)["citations"]
    ids = {c["snapshot_id"] for c in citations}
    assert len(ids) == 1, f"{rule_id} cites more than one snapshot: {ids}"
    return ids.pop()


def _params(rule_id: str, name: str) -> dict:
    for param in _rule_doc(rule_id)["parameters"]:
        if param["name"] == name:
            return param["value"]
    return {}


# --------------------------------------------------------------------------
# AS-1 - SOURCE FIDELITY: every authored FAR value equals the snapshot value.
# --------------------------------------------------------------------------

def test_as1_flat_rule_values_match_snapshot() -> None:
    """Every FAR value in every flat rule is byte-identical to its snapshot, AND the
    parameter maps cover EXACTLY the applicable district set - no applicable district
    without a value, no value for a non-applicable district. A missing or extra key
    is a failure, not a silently-uncompared entry, and BOTH columns (standard and the
    qualifying material alternative) are compared for every district."""
    for rule_id in _FLAT_RULES:
        snapshot_id = _rule_snapshot_id(rule_id)
        rows = _district_rows(snapshot_id)
        applicability = set(_rule_doc(rule_id)["applicability"]["values"])
        standard = _params(rule_id, "standard_far_by_district")
        qualifying = _params(rule_id, "qualifying_far_by_district")
        assert standard, f"{rule_id} has no standard_far_by_district parameter"
        # COMPLETE parameter/applicability key coverage (standard column).
        assert set(standard) == applicability, (
            f"{rule_id}: standard_far_by_district keys {sorted(standard)} != "
            f"applicability {sorted(applicability)}"
        )
        # Every flat rule in this family surfaces its qualifying (second-column)
        # material alternative as a provenance-linked parameter keyed by the same set.
        assert qualifying, f"{rule_id} has no qualifying_far_by_district parameter"
        assert set(qualifying) == applicability, (
            f"{rule_id}: qualifying_far_by_district keys {sorted(qualifying)} != "
            f"applicability {sorted(applicability)}"
        )
        # Compare EVERY key against the snapshot (both columns, every district).
        for district in applicability:
            district_rows = rows.get(district)
            assert district_rows, f"{district} ({rule_id}) not found in {snapshot_id}"
            assert len(district_rows) == 1, (
                f"{district} is not a flat lookup in {snapshot_id}: {district_rows}"
            )
            assert Decimal(str(standard[district])) == Decimal(district_rows[0]["standard"]), (
                f"{rule_id}:{district} standard FAR {standard[district]} != snapshot "
                f"{district_rows[0]['standard']}"
            )
            assert Decimal(str(qualifying[district])) == Decimal(district_rows[0]["qualifying"]), (
                f"{rule_id}:{district} qualifying FAR {qualifying[district]} != snapshot "
                f"{district_rows[0]['qualifying']}"
            )


def test_as1_conditional_rule_values_match_snapshot() -> None:
    """The conditional rule's three per-district maps (conservative, wide-street,
    qualifying) each cover EXACTLY the applicable set and are byte-identical to the
    snapshot; and the R8 footnote-2 value (8.64) - the single material alternative
    that only the wide-street row carries - is byte-checked against the snapshot,
    anchored to the row whose qualifying value actually carries footnote 2."""
    rows = _district_rows(_rule_snapshot_id(_CONDITIONAL_RULE))
    applicability = set(_rule_doc(_CONDITIONAL_RULE)["applicability"]["values"])
    conservative = _params(_CONDITIONAL_RULE, "standard_far_by_district")
    wide_street = _params(_CONDITIONAL_RULE, "wide_street_far_by_district")
    qualifying = _params(_CONDITIONAL_RULE, "qualifying_far_by_district")
    ws_qualifying = _params(_CONDITIONAL_RULE, "wide_street_qualifying_far_by_district")
    # COMPLETE key coverage: the three primary maps cover exactly the applicable set.
    for name, param in (
        ("standard_far_by_district", conservative),
        ("wide_street_far_by_district", wide_street),
        ("qualifying_far_by_district", qualifying),
    ):
        assert set(param) == applicability, (
            f"{_CONDITIONAL_RULE}: {name} keys {sorted(param)} != applicability "
            f"{sorted(applicability)}"
        )
    for district in _CONDITIONAL_DISTRICTS:
        district_rows = rows.get(district)
        assert district_rows and len(district_rows) == 2, (
            f"{district} must appear in exactly two snapshot rows, got {district_rows}"
        )
        standards = sorted(Decimal(r["standard"]) for r in district_rows)
        low, high = standards[0], standards[-1]
        assert low != high, f"{district} rows have identical standard values"
        # Conservative (returned) value is the LOWER; wide-street value is the HIGHER.
        assert Decimal(str(conservative[district])) == low
        assert Decimal(str(wide_street[district])) == high
        # The qualifying value surfaced is the one from the LOWER (non-wide-street) row.
        low_row = min(district_rows, key=lambda r: Decimal(r["standard"]))
        assert Decimal(str(qualifying[district])) == Decimal(low_row["qualifying"])
    # R8 footnote-2 value: byte-checked against the qualifying value of the HIGHER
    # (wide-street) row - the row whose qualifying column carries footnote 2 in the
    # snapshot markup - so the 8.64 alternative is anchored to the source, not restated.
    assert ws_qualifying, "wide_street_qualifying_far_by_district must not be empty"
    for district, value in ws_qualifying.items():
        assert district in applicability, f"{district} not applicable to {_CONDITIONAL_RULE}"
        high_row = max(rows[district], key=lambda r: Decimal(r["standard"]))
        assert high_row["value_footnotes"].get("qualifying_affordable_or_senior_housing") == "2", (
            f"{district}: the byte-checked footnote-2 value must come from the row whose "
            "qualifying value carries footnote 2 in the snapshot"
        )
        assert Decimal(str(value)) == Decimal(high_row["qualifying"]), (
            f"{district} footnote-2 qualifying {value} != snapshot {high_row['qualifying']}"
        )


# --------------------------------------------------------------------------
# AS-2 - COMPLETE COVERAGE, COMPUTED NOT ASSERTED.
# --------------------------------------------------------------------------

def _covered_districts() -> dict[str, str]:
    """district -> rule_id for every district any authored rule declares
    applicable. Asserts the applicability sets are pairwise disjoint."""
    covered: dict[str, str] = {}
    for rule_id in _ALL_FAR_RULES:
        for district in _rule_doc(rule_id)["applicability"]["values"]:
            assert district not in covered, (
                f"district {district} is claimed by both {covered.get(district)} "
                f"and {rule_id}"
            )
            covered[district] = rule_id
    return covered


def test_as2_every_snapshot_district_is_covered_or_excluded() -> None:
    snapshot_districts = _all_snapshot_districts("zr-23-21") | _all_snapshot_districts(
        "zr-23-22"
    )
    covered = set(_covered_districts())
    silently_absent = snapshot_districts - covered - set(_DOCUMENTED_EXCLUSIONS)
    assert not silently_absent, f"districts silently absent from every rule: {silently_absent}"
    # No rule may claim a district that does not exist in either snapshot.
    invented = covered - snapshot_districts
    assert not invented, f"rules claim districts absent from the snapshots: {invented}"


def test_as2_district_counts_are_asserted() -> None:
    assert len(_all_snapshot_districts("zr-23-21")) == 18
    assert len(_all_snapshot_districts("zr-23-22")) == 27
    covered = _covered_districts()
    # 18 + 27 distinct districts, minus any documented exclusion, are all covered.
    assert len(covered) == 45 - len(_DOCUMENTED_EXCLUSIONS)


# --------------------------------------------------------------------------
# AS-3 - CONSERVATIVE ON CONDITIONALS: never return the higher value.
# --------------------------------------------------------------------------

def test_as3_conditional_districts_return_conservative_value(registry) -> None:
    rows = _district_rows(_rule_snapshot_id(_CONDITIONAL_RULE))
    for district in _CONDITIONAL_DISTRICTS:
        standards = sorted(Decimal(r["standard"]) for r in rows[district])
        low, high = float(standards[0]), float(standards[-1])
        result = registry.evaluate(
            _CONDITIONAL_RULE,
            {
                "zoning_district": district,
                "lot_area_sq_ft": 10_000,
                "housing_program": "standard_residence",
            },
        )
        trace = result.export()
        assert trace["outputs"]["max_residential_far"] == low, (
            f"{district} must return the conservative {low}"
        )
        # The higher wide-street value is NEVER the returned result.
        assert trace["outputs"]["max_residential_far"] != high
        # The higher value is surfaced as an explicit conditional alternative.
        applied = {e["id"]: e for e in trace["exceptions_applied"]}
        assert "wide_street_far_alternative" in applied
        assert applied["wide_street_far_alternative"]["effect"] == "conditional_alternative"
        assert result.coverage_status == cov.COVERAGE_CONDITIONAL


def test_as3_higher_value_is_the_wide_street_footnote_row() -> None:
    """The higher of the two rows is the one carrying ZR 23-22 footnote 1 - proven
    from the snapshot markup, so 'conservative' is anchored to the source, not to
    an arbitrary min()."""
    rows = _district_rows(_rule_snapshot_id(_CONDITIONAL_RULE))
    for district in _CONDITIONAL_DISTRICTS:
        high_row = max(rows[district], key=lambda r: Decimal(r["standard"]))
        marked = (
            high_row["district_footnotes"].get(district) == "1"
            or high_row["value_footnotes"].get("standard_residences") == "1"
        )
        assert marked, f"{district}: higher row does not carry footnote 1 in snapshot"


# --------------------------------------------------------------------------
# AS-4 - FOOTNOTE SCOPE: 0.60 cap only on the first ZR 23-21 row.
# --------------------------------------------------------------------------

def test_as4_footnote_1_cap_only_on_first_row_rule() -> None:
    # Present on the R1/R2/R3 rule (the first ZR 23-21 table row).
    first_row_exceptions = {e["id"] for e in _rule_doc("r1-r2-r3-residential-far")["exceptions"]}
    assert _FOOTNOTE_1_CAP_EXCEPTION_ID in first_row_exceptions
    # Absent from every other ZR 23-21 rule (R2X, R4*, R5*).
    for rule_id in ("r2x-r4-residential-far", "r5-residential-far"):
        exceptions = {e["id"] for e in _rule_doc(rule_id)["exceptions"]}
        assert _FOOTNOTE_1_CAP_EXCEPTION_ID not in exceptions, (
            f"{rule_id} wrongly carries the footnote-1 0.60 cap"
        )


def test_as4_snapshot_marks_footnote_1_on_first_row_only() -> None:
    """Read the source: only the first ZR 23-21 row's standard value carries the
    footnote-1 superscript; no other row carries any value footnote."""
    rows = _snapshot_raw("zr-23-21")["table"]["rows"]
    assert rows[0].get("value_footnotes", {}).get("standard_zoning_lots") == "1"
    for row in rows[1:]:
        assert not row.get("value_footnotes"), (
            f"unexpected value footnote on a non-first ZR 23-21 row: {row['districts']}"
        )


# --------------------------------------------------------------------------
# AS-5 (source-digest binding, matching + mismatched) and AS-6 (each district's
# qualifying alternative surfaced) live in test_r1_r12_residential_far_provenance.py.
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# AS-7 - STATUS AND HONESTY LABELS.
# --------------------------------------------------------------------------

def test_as7_all_rules_are_draft_and_unapproved() -> None:
    for rule_id in _ALL_FAR_RULES:
        doc = _rule_doc(rule_id)
        assert doc["status"] == "needs_review"
        assert doc["status"] not in {"published", "verified", "approved"}
        assert doc["release"]["independent_review"] == "pending"
        assert doc["release"]["qualified_human_approval"] == "pending"
        assert doc["effective_from"] == _EFFECTIVE_FROM


def test_as7_no_family_result_is_ever_verified(registry) -> None:
    samples = [
        ("r1-r2-r3-residential-far", {"zoning_district": "R2", "lot_area_sq_ft": 5_000}),
        ("r6-r12-residential-far", {"zoning_district": "R12", "lot_area_sq_ft": 5_000}),
        (_CONDITIONAL_RULE, {"zoning_district": "R8", "lot_area_sq_ft": 5_000}),
    ]
    for rule_id, inputs in samples:
        result = registry.evaluate(rule_id, inputs)
        assert result.coverage_status != cov.COVERAGE_VERIFIED


def test_as7_before_effective_from_is_not_effective(registry) -> None:
    result = registry.evaluate(
        "r6-r12-residential-far",
        {
            "zoning_district": "R10",
            "lot_area_sq_ft": 5_000,
            "housing_program": "standard_residence",
        },
        as_of_date="2020-01-01",
    )
    trace = result.export()
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert trace["applicability_outcome"] is False
    assert "max_residential_far" not in trace["outputs"]


# --------------------------------------------------------------------------
# AS-8 - NO ENGINE CHANGE, NO NEW PRIMITIVE.
# --------------------------------------------------------------------------

def test_as8_family_uses_only_existing_primitives() -> None:
    known_effects = {
        "conditional_alternative", "documented_limitation", "professional_review_required"
    }
    for rule_id in _ALL_FAR_RULES:
        doc = _rule_doc(rule_id)
        assert doc["applicability"]["op"] == "in_set"
        for step in doc["computation"]["steps"]:
            assert step["op"] in COMPUTE_OPS, (
                f"{rule_id} step uses op {step['op']!r} unknown to the engine"
            )
        for exc in doc["exceptions"]:
            assert exc["effect"] in known_effects


def test_as8_registry_loads_whole_family(registry) -> None:
    ids = set(registry.rule_ids())
    assert set(_ALL_FAR_RULES).issubset(ids)


# --------------------------------------------------------------------------
# AS-9 - CORRECT THE EXISTING R5 PILOT IN THE SAME FAMILY.
# --------------------------------------------------------------------------

def test_as9_r5_no_longer_carries_footnote_cap_r1r2r3_does(registry) -> None:
    r5_exceptions = {e["id"] for e in _rule_doc("r5-residential-far")["exceptions"]}
    assert _FOOTNOTE_1_CAP_EXCEPTION_ID not in r5_exceptions
    r1_exceptions = {e["id"] for e in _rule_doc("r1-r2-r3-residential-far")["exceptions"]}
    assert _FOOTNOTE_1_CAP_EXCEPTION_ID in r1_exceptions

    # R5 evaluation output no longer carries the cap ...
    r5 = registry.evaluate(
        "r5-residential-far",
        {"zoning_district": "R5", "lot_area_sq_ft": 10_000, "site_class": "standard_zoning_lot"},
    ).export()
    assert _FOOTNOTE_1_CAP_EXCEPTION_ID not in {e["id"] for e in r5["exceptions_applied"]}
    # ... but the R1/R2/R3 output does (unconditional documented limitation).
    r1 = registry.evaluate(
        "r1-r2-r3-residential-far",
        {"zoning_district": "R1-2A", "lot_area_sq_ft": 10_000, "site_class": "standard_zoning_lot"},
    ).export()
    assert _FOOTNOTE_1_CAP_EXCEPTION_ID in {e["id"] for e in r1["exceptions_applied"]}


def test_as9_r5_far_values_unchanged_and_match_snapshot(registry) -> None:
    rows = _district_rows("zr-23-21")
    for district in ("R5", "R5A", "R5B", "R5D"):
        expected = float(Decimal(rows[district][0]["standard"]))
        result = registry.evaluate(
            "r5-residential-far",
            {
                "zoning_district": district,
                "lot_area_sq_ft": 1_000,
                "site_class": "standard_zoning_lot",
            },
        ).export()
        assert result["outputs"]["max_residential_far"] == expected
