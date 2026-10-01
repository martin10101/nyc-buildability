"""A-02a regression guard: adding the R6B draft rules changes NO other district's result.

1. GOLDEN: every rule that existed before A-02a, evaluated for every ZR 23-21 / 23-22 district
   under three input sets, exports byte-identical traces - pinned to the digest recorded on the
   pre-change tree (commit 64fff2d1, before any A-02a edit) - with lane A OFF and with it ON.
2. The flag-off registry is exactly the pre-change registry (same rule ids, same families).
3. The property integration (family residential_far) returns a byte-identical document for EVERY
   district, R6B included, with lane A on or off: the qualifying alternative lives in its own
   family, so nothing the integration reads moved.

If you change an existing rule or snapshot ON PURPOSE, the golden digest moves with it: recompute
it with :func:`_golden_digest` on the new tree and update ``_GOLDEN_DIGEST`` in the same change,
saying why in the commit.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.rules import RuleRegistry
from app.rules import integration as ri

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DOCS_SNAPSHOTS = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"

_OFF: dict[str, str] = {}
_ON = {"LANE_A_ENABLED": "1"}

#: Every rule id in the registry before A-02a (the flag-off registry must equal this exactly).
_PRE_EXISTING_RULE_IDS = (
    "r1-r2-bare-pitched-height", "r1-r2-qrs-height", "r1-r2-r3-residential-far",
    "r1-r2-reference-plane-23421g", "r1-r2-suffix-variants-pitched-height",
    "r2x-r4-residential-far", "r3-2-r4-flat-height", "r3-r4-pitched-height", "r4b-height",
    "r5-height", "r5-qrs-height", "r5-residential-far", "r5-setback", "r5a-height",
    "r5b-height", "r5d-height", "r6-r12-residential-far",
    "r6-r7-r8-wide-street-conditional-far",
)

#: sha256 of the canonical JSON of all 2,430 exported traces (18 rules x 45 districts x 3 input
#: sets), computed on the pre-change tree.
_GOLDEN_DIGEST = "e2e8630355560b6998786d7b648edca376d3d29fb2c6a7ad3949e8e8ccf58252"
_GOLDEN_RECORDS = 2430

_INPUT_SETS = (
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
)


def _all_districts() -> list[str]:
    """Every district of the ZR 23-21 and 23-22 tables (45), R6B included."""
    out: set[str] = set()
    for snapshot_id in ("zr-23-21", "zr-23-22"):
        raw = json.loads((_DOCS_SNAPSHOTS / f"{snapshot_id}.snapshot.json").read_text("utf-8"))
        for row in raw["table"]["rows"]:
            out.update(row["districts"])
    return sorted(out)


def _golden_digest(registry: RuleRegistry) -> tuple[str, int]:
    records = []
    for rule_id in _PRE_EXISTING_RULE_IDS:
        for district in _all_districts():
            for index, base in enumerate(_INPUT_SETS):
                trace = registry.evaluate(rule_id, {"zoning_district": district, **base}).export()
                records.append([rule_id, district, index, trace])
    blob = json.dumps(records, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest(), len(records)


def _profile(district: str, area: float = 10075.0) -> dict:
    """A minimal confident single-district profile in the shape evaluate_property reads."""
    return {
        "identity": {"bbl": "4073340070"},
        "spatial_intersection": {
            "lot_overall_class": "single_district_confident",
            "professional_review_required": False,
            "pairs": [{
                "family": "base_zoning", "pair_class": "interior_confident",
                "district_label": district, "lot_area_sq_ft": area,
            }],
            "provenance_refs": ["prov-spatial"],
        },
        "lot_geometry": {"area_sq_ft": area, "provenance_ref": "prov-lotgeom"},
    }


@pytest.mark.parametrize("env", [_OFF, _ON], ids=["lane_a_off", "lane_a_on"])
def test_every_pre_existing_rule_trace_is_byte_identical_to_the_golden(env) -> None:
    digest, count = _golden_digest(RuleRegistry(env=env).load())
    assert count == _GOLDEN_RECORDS
    assert digest == _GOLDEN_DIGEST


def test_golden_is_independent_of_the_snapshot_copy() -> None:
    """Same digest whether citations resolve against the packaged bundle or the docs source."""
    from app.rules.snapshots import SnapshotStore

    docs = RuleRegistry(snapshots=SnapshotStore(_DOCS_SNAPSHOTS), env=_ON).load()
    assert _golden_digest(docs) == (_GOLDEN_DIGEST, _GOLDEN_RECORDS)


def test_flag_off_registry_is_the_pre_change_registry() -> None:
    off = RuleRegistry(env=_OFF).load()
    assert tuple(off.rule_ids()) == _PRE_EXISTING_RULE_IDS
    assert off.families() == [
        "residential_far", "residential_height_setback", "residential_height_setback_r1_r2",
        "residential_height_setback_r3_r4",
    ]


def test_flag_on_adds_only_the_two_r6b_rules() -> None:
    on = RuleRegistry(env=_ON).load()
    added = set(on.rule_ids()) - set(_PRE_EXISTING_RULE_IDS)
    assert added == {"r6b-height", "r6b-qualifying-housing-far"}
    assert set(_PRE_EXISTING_RULE_IDS) <= set(on.rule_ids())


def test_property_integration_is_identical_for_every_district_on_or_off() -> None:
    off = RuleRegistry(env=_OFF).load()
    on = RuleRegistry(env=_ON).load()
    for district in _all_districts():
        profile = _profile(district)
        doc_off = ri.evaluate_property(profile, registry=off).as_dict()
        doc_on = ri.evaluate_property(profile, registry=on).as_dict()
        assert json.dumps(doc_on, sort_keys=True) == json.dumps(doc_off, sort_keys=True), district


def test_integration_for_r6b_still_reports_the_standard_allowance_only() -> None:
    """The residential_far integration (and so the rule-evaluation document and the scenario
    builder) keeps reporting the standard 20,150 sq ft for R6B; the qualifying 24,180 sq ft is
    computed by its own family and never enters that document."""
    doc = ri.evaluate_property(_profile("R6B"), registry=RuleRegistry(env=_ON).load()).as_dict()
    applicable = [t for t in doc["evaluations"] if t["applicability_outcome"]]
    assert [t["rule_id"] for t in applicable] == ["r6-r12-residential-far"]
    assert applicable[0]["outputs"]["max_residential_floor_area_sq_ft"] == 20150.0
    assert "r6b-qualifying-housing-far" not in json.dumps(doc)
