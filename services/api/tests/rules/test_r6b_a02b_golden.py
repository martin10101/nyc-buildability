"""A-02b regression guard: adding the R6B lot-coverage, rear-yard and dwelling-unit draft rules (and
the additive ``round_threshold`` op) changes NO other rule's result - A-02a's R6B rules included.

GOLDEN: every rule the registry indexed before A-02b with lane A ON - the 18 pre-D-090 rules plus
A-02a's ``r6b-height`` and ``r6b-qualifying-housing-far`` - evaluated for every ZR 23-21 / 23-22
district under four input sets exports traces whose canonical JSON hashes to the digest recorded on
the pre-change tree (commit 04afba9d, A-02a, before any A-02b edit). The fourth input set carries
every input the A-02b rules read, so the new inputs are proven not to move any other rule.

With lane A OFF, A-02a's own golden (``test_r6b_other_districts_unchanged``) still pins the 18
pre-D-090 rules, and the three A-02b rules are validated but not indexed.

If you change an existing rule or snapshot ON PURPOSE, recompute ``_GOLDEN_DIGEST`` with
:func:`golden_digest` on the new tree and say why in the commit.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.rules import RuleRegistry

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DOCS_SNAPSHOTS = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"

_OFF: dict[str, str] = {}
_ON = {"LANE_A_ENABLED": "1"}

#: The three rules A-02b adds (all lane A).
A02B_RULE_IDS = ("r6b-dwelling-units", "r6b-lot-coverage", "r6b-rear-yard-corner-waiver")

#: Every rule id indexed with lane A on before A-02b (18 pre-D-090 rules + A-02a's two).
PRE_A02B_RULE_IDS_LANE_A_ON = (
    "r1-r2-bare-pitched-height", "r1-r2-qrs-height", "r1-r2-r3-residential-far",
    "r1-r2-reference-plane-23421g", "r1-r2-suffix-variants-pitched-height",
    "r2x-r4-residential-far", "r3-2-r4-flat-height", "r3-r4-pitched-height", "r4b-height",
    "r5-height", "r5-qrs-height", "r5-residential-far", "r5-setback", "r5a-height",
    "r5b-height", "r5d-height", "r6-r12-residential-far",
    "r6-r7-r8-wide-street-conditional-far", "r6b-height", "r6b-qualifying-housing-far",
)

#: sha256 of the canonical JSON of all 3,600 traces (20 rules x 45 districts x 4 input sets) with
#: lane A on, computed on the pre-change tree (04afba9d).
_GOLDEN_DIGEST = "75e74db54fd2a628eec15e89d0cf814a98475dc2d1947ad837a45fb82e7d69e6"
_GOLDEN_RECORDS = 3600

INPUT_SETS = (
    {"lot_area_sq_ft": 10075},
    {
        "lot_area_sq_ft": 10075, "lot_area_sqft": 10075, "lot_width_ft": 100.8,
        "rear_wall_slope_percent": 50, "building_type": "detached", "overlay_present": False,
        "special_district_present": False, "historic_district": False, "large_site": False,
        "transportation_infrastructure_adjacent": False, "qualifying_residential_site": False,
        "site_class": "standard_zoning_lot", "street_width_class": "narrow",
        "housing_program": "qualifying_affordable_housing",
    },
    {
        "lot_area_sq_ft": 10075, "lot_area_sqft": 10075, "lot_width_ft": 100.8,
        "rear_wall_slope_percent": 50, "building_type": "attached", "overlay_present": True,
        "special_district_present": False, "historic_district": False, "large_site": False,
        "transportation_infrastructure_adjacent": False, "qualifying_residential_site": True,
        "site_class": "qualifying_residential_site", "street_width_class": "wide",
        "housing_program": "standard_residence",
    },
    {
        # Every input an A-02b rule reads, on the benchmark facts.
        "lot_area_sq_ft": 10075, "overlay_present": True, "special_district_present": False,
        "housing_program": "standard_residence", "lot_type": "corner",
        "within_100_ft_of_street_line_intersection": True,
        "street_line_intersection_angle_degrees": 90, "max_residential_floor_area_sq_ft": 20150,
        "special_density_area": False,
    },
)


def all_districts() -> list[str]:
    """Every district of the ZR 23-21 and 23-22 tables (45), R6B included."""
    out: set[str] = set()
    for snapshot_id in ("zr-23-21", "zr-23-22"):
        raw = json.loads((_DOCS_SNAPSHOTS / f"{snapshot_id}.snapshot.json").read_text("utf-8"))
        for row in raw["table"]["rows"]:
            out.update(row["districts"])
    return sorted(out)


def golden_digest(registry: RuleRegistry) -> tuple[str, int]:
    records = []
    for rule_id in PRE_A02B_RULE_IDS_LANE_A_ON:
        for district in all_districts():
            for index, base in enumerate(INPUT_SETS):
                trace = registry.evaluate(rule_id, {"zoning_district": district, **base}).export()
                records.append([rule_id, district, index, trace])
    blob = json.dumps(records, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest(), len(records)


def test_every_pre_a02b_rule_trace_is_byte_identical_to_the_golden() -> None:
    assert golden_digest(RuleRegistry(env=_ON).load()) == (_GOLDEN_DIGEST, _GOLDEN_RECORDS)


def test_golden_is_independent_of_the_snapshot_copy() -> None:
    from app.rules.snapshots import SnapshotStore

    docs = RuleRegistry(snapshots=SnapshotStore(_DOCS_SNAPSHOTS), env=_ON).load()
    assert golden_digest(docs) == (_GOLDEN_DIGEST, _GOLDEN_RECORDS)


def test_flag_on_adds_exactly_the_a02b_rules_to_the_pre_a02b_registry() -> None:
    on = RuleRegistry(env=_ON).load()
    assert set(on.rule_ids()) - set(PRE_A02B_RULE_IDS_LANE_A_ON) == set(A02B_RULE_IDS)
    assert set(PRE_A02B_RULE_IDS_LANE_A_ON) <= set(on.rule_ids())


@pytest.mark.parametrize("env", [_OFF, {"LANE_A_ENABLED": "0"}, {"LANE_B_ENABLED": "1"}])
def test_flag_off_the_a02b_rules_are_validated_but_not_indexed(env) -> None:
    off = RuleRegistry(env=env).load()
    gated = off.gated_off_rule_ids()
    assert set(A02B_RULE_IDS) <= set(gated)
    assert all(gated[rule_id] == "A" for rule_id in A02B_RULE_IDS)
    for rule_id in A02B_RULE_IDS:
        assert rule_id not in off.rule_ids()
        with pytest.raises(KeyError):
            off.rule(rule_id)
    for family in ("residential_lot_coverage", "residential_rear_yard_corner_waiver",
                   "residential_dwelling_units"):
        assert family not in off.families()
