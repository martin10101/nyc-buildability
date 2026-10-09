"""A-02b at the consumers: the three new R6B rules (lot coverage, rear-yard corner waiver, dwelling
units) live in their OWN families, so the maximum envelope and the proposal checks - which read
the families ``lot_coverage`` and ``rear_yard`` - are byte-identical to the pre-change tree for
R6B and for every other district, with lane A on.

GOLDEN: the canonical JSON of the envelope and the check report for the benchmark R6B facts and
five other districts, lane A on, hashes to the digest recorded on the pre-change tree (commit
04afba9d, A-02a, before any A-02b edit). Wiring coverage / units into the envelope or the
three-answer generator is later work (A-04).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.rules import proposal_checks as pc
from app.rules.registry import RuleRegistry
from app.scenario import max_envelope as me
from app.scenario.derivation import LotContext, LotLineSegment

_CASE = (
    Path(__file__).resolve().parents[1] / "rules" / "fixtures" / "proposal_checks"
    / "rectangle_case.json"
)
_ON = {"LANE_A_ENABLED": "1"}

#: The benchmark R6B facts plus the A-02b site facts (which the consumers must ignore: they are
#: not caller-mappable rule inputs), and five other districts.
FACTS = (
    {"zoning_district": "R6B", "overlay_present": True, "special_district_present": False},
    {"zoning_district": "R6B", "overlay_present": True, "special_district_present": False,
     "lot_type": "corner", "within_100_ft_of_street_line_intersection": True,
     "street_line_intersection_angle_degrees": 90, "special_density_area": False},
    {"zoning_district": "R5", "overlay_present": False, "special_district_present": False,
     "historic_district": False, "large_site": False},
    {"zoning_district": "R5D", "overlay_present": False, "special_district_present": False,
     "historic_district": False, "large_site": False},
    {"zoning_district": "R4B", "overlay_present": False, "special_district_present": False,
     "historic_district": False, "large_site": False},
    {"zoning_district": "R6A", "overlay_present": True, "special_district_present": False},
    {"zoning_district": "R6", "street_width_class": "wide"},
)

#: sha256 of the canonical JSON of every (envelope, check report) pair above, lane A on, computed
#: on the pre-change tree (04afba9d).
_GOLDEN_DIGEST = "a66b1b6ceba6f2ae683cb2ba9c8b08e72e9f8e0af79c73ea353f154a8c699866"


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


def consumer_digest(registry: RuleRegistry) -> str:
    case = _case()
    lot = _case_lot(case)
    records = []
    for facts in FACTS:
        envelope = me.derive_max_envelope(lot, facts, registry=registry).as_dict()
        report = pc.check_proposal(case["block"], lot, facts, scenario_label="a02b",
                                   registry=registry).as_dict()
        records.append([facts, envelope, report])
    blob = json.dumps(records, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def test_envelope_and_checks_are_byte_identical_to_the_pre_change_tree() -> None:
    assert consumer_digest(RuleRegistry(env=_ON).load()) == _GOLDEN_DIGEST


def test_the_consumed_families_still_have_no_rule_with_lane_a_on() -> None:
    """The envelope's and checker's lot-coverage and rear-yard families are untouched: still
    unsupported (an honest gap), never silently fed by the new R6B rules."""
    registry = RuleRegistry(env=_ON).load()
    for family in ("lot_coverage", "rear_yard"):
        assert registry.family_coverage(family)["coverage_status"] == "unsupported"
    envelope = me.derive_max_envelope(_case_lot(_case()), FACTS[1], registry=registry)
    by_id = {d.dimension_id: d for d in envelope.dimensions}
    assert by_id["max_lot_coverage_ratio"].gap_reason is me.EnvelopeGapReason.FAMILY_UNSUPPORTED
    assert (by_id["min_rear_yard_depth_ft"].gap_reason
            is me.EnvelopeGapReason.NON_COMMENSURABLE_WITH_MASSING)
