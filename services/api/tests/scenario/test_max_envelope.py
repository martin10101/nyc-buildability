"""M5-T064 (D-082-R002): deterministic maximum-buildable-envelope engine.

Hand-computed, offline, deterministic. Reuses the accepted B2 SYNTHETIC fixture rulesets +
hand-computed rectangle case (one rule per checked family: lot_coverage max 0.5, height 60 ft
attested), and a minimal duck-typed registry double for the multi-rule binding / provenance
cases, so no new fixture ruleset files are added.

- AS-1: binding values equal the tightest applicable rule's declared allowance (registry-derived,
  no hand-copied constant); an unbounded direction is an honest gap, never an invented ceiling.
- AS-2: each resolved dimension names its binding rule id + the out-competed ids; flipping which
  rule is tighter flips the named binding id.
- AS-3: honest gaps in the typed vocabulary; EVERY declared dimension is enumerated (nothing
  silently omitted); the non-commensurable FAR / rear-yard dimensions are always gaps.
- AS-4: check_proposal on the emitted candidate PASSes every computable (commensurable) check at
  the derived values, at-cap-exact (a +epsilon mutation FAILs).
- AS-5: byte-stable output across repeated calls.
- AS-6: no scenario document / contract version is constructed; typed precondition refusals.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from app.rules import proposal_checks as pc
from app.rules.registry import RuleRegistry
from app.rules.snapshots import SnapshotStore
from app.scenario import max_envelope as me
from app.scenario.derivation import LotContext, LotLineSegment
from app.scenario.proposal import validate_proposed_massing

_B2_FIXTURES = Path(__file__).resolve().parents[1] / "rules" / "fixtures" / "proposal_checks"
_RULESETS = _B2_FIXTURES / "rulesets"
_SNAPSHOTS = _B2_FIXTURES / "snapshots"

_ATTESTED = {"zoning_district": "R5", "street_width_class": "wide"}

#: A deterministic interior EPSG:2263 SW corner well inside the accepted NYC bounds, used as the
#: default lot anchor so the fitted candidate is always in-bounds.
_LOT_ANCHOR = (985000.0, 195000.0)


# ---------------------------------------------------------------------------
# Fixtures / helpers.
# ---------------------------------------------------------------------------


@pytest.fixture
def fixture_registry() -> RuleRegistry:
    """The accepted B2 synthetic registry (one rule per checked family)."""
    return RuleRegistry(_RULESETS, snapshots=SnapshotStore(_SNAPSHOTS)).load()


def _rect_segments(
    min_x: float, min_y: float, width: float, depth: float
) -> tuple[LotLineSegment, ...]:
    """The four axis-aligned lot-line segments of the rectangle anchored at ``(min_x, min_y)`` -
    the supported lot geometry class the candidate is fitted to."""
    x1, y1 = min_x + width, min_y + depth
    return (
        LotLineSegment(id="L-S", start=(min_x, min_y), end=(x1, min_y)),
        LotLineSegment(id="L-E", start=(x1, min_y), end=(x1, y1)),
        LotLineSegment(id="L-N", start=(x1, y1), end=(min_x, y1)),
        LotLineSegment(id="L-W", start=(min_x, y1), end=(min_x, min_y)),
    )


def _lot(
    area: float = 8000.0, *, width: float | None = None, depth: float | None = None,
    anchor: tuple[float, float] = _LOT_ANCHOR,
) -> LotContext:
    """A supported axis-aligned rectangular lot with real 2263 geometry. When ``width``/``depth``
    are given the lot takes those proportions (area = width * depth, exactly consistent); otherwise
    an 80 x depth-100 rectangle sized to ``area``. The recorded area is the EXACT bounding-box
    product so the geometry is consistent with the coverage denominator."""
    if width is None and depth is None:
        depth = 100.0
        width = area / depth
    assert width is not None and depth is not None
    min_x, min_y = anchor
    return LotContext(
        area_sq_ft=width * depth,
        area_provenance={"source_id": "synthetic"},
        lot_line_segments=_rect_segments(min_x, min_y, width, depth),
    )


def _by_dim(envelope: me.MaxEnvelope) -> dict[str, me.EnvelopeDimensionResult]:
    return {d.dimension_id: d for d in envelope.dimensions}


def _assert_contained(envelope: me.MaxEnvelope) -> None:
    """Every emitted candidate vertex lies within the lot's bounding rectangle (containment)."""
    rect = envelope.candidate_placement.lot_rectangle
    assert rect is not None
    max_x = rect["anchor_x"] + rect["width_ft"]
    max_y = rect["anchor_y"] + rect["depth_ft"]
    for x, y in envelope.candidate["outline"]["vertices"]:
        assert rect["anchor_x"] <= x <= max_x
        assert rect["anchor_y"] <= y <= max_y


class _FakeResult:
    def __init__(self, trace: dict) -> None:
        self._trace = trace

    def export(self) -> dict:
        return self._trace


class _FakeRegistry:
    """A minimal duck-typed registry: returns hand-authored evaluator traces for named rule ids
    per family (the same pattern the accepted B2 suite uses). No detect_conflicts, so the engine's
    getattr-guarded advisory path returns None."""

    def __init__(self, family_rule_ids: dict, traces: dict) -> None:
        self._family_rule_ids = family_rule_ids
        self._traces = traces

    def family_coverage(self, family: str) -> dict:
        rule_ids = self._family_rule_ids.get(family)
        return {"rule_ids": list(rule_ids)} if rule_ids else {"family": family}

    def evaluate(self, rule_id: str, _inputs: dict) -> _FakeResult:
        return _FakeResult(self._traces[rule_id])


def _trace(rule_id: str, output_name: str, value: float, *, applicable: bool = True) -> dict:
    return {
        "rule_id": rule_id,
        "rule_version": "1.0.0",
        "rule_status": "needs_review",
        "applicability_outcome": applicable,
        "coverage_status": next(iter(me._USABLE_COVERAGE)),
        "outputs": {output_name: value},
        "citations": (),
    }


# ---------------------------------------------------------------------------
# Drift guard: the usable-coverage set must equal the accepted checker's.
# ---------------------------------------------------------------------------


def test_usable_coverage_matches_accepted_checker():
    assert me._USABLE_COVERAGE == pc._USABLE_COVERAGE


# ---------------------------------------------------------------------------
# AS-1: registry-derived binding values; unbounded -> honest gap.
# ---------------------------------------------------------------------------


def test_as1_binding_values_from_fixture_registry(fixture_registry):
    envelope = me.derive_max_envelope(_lot(), _ATTESTED, registry=fixture_registry)
    dims = _by_dim(envelope)

    coverage = dims["max_lot_coverage_ratio"]
    assert coverage.binding_value == pytest.approx(0.5)  # the fixture rule's declared allowance
    assert coverage.binding_rule_id == "pc-lot-coverage-demo"
    assert coverage.out_competed_rule_ids == ()  # sole applicable rule
    assert coverage.gap_reason is None
    assert coverage.rule_citations  # provenance carried from the rule

    height = dims["max_building_height"]
    assert height.binding_value == pytest.approx(60.0)
    assert height.binding_rule_id == "pc-height-setback-demo"
    assert height.gap_reason is None

    # No hand-copied constant: the binding values are exactly the fixture rules' outputs, and a
    # gap never carries a number.
    for d in envelope.dimensions:
        assert (d.binding_value is None) == (d.gap_reason is not None)


def test_as1_far_and_rear_yard_are_non_commensurable_gaps_even_with_a_rule(fixture_registry):
    """The fixture registry HAS residential-FAR and rear-yard rules, yet both are always honest
    gaps for the rectangle-prism class (semantic gate, registry-independent)."""
    envelope = me.derive_max_envelope(_lot(), _ATTESTED, registry=fixture_registry)
    dims = _by_dim(envelope)
    for dim_id in ("max_residential_floor_area_sq_ft", "min_rear_yard_depth_ft"):
        d = dims[dim_id]
        assert d.binding_value is None
        assert d.gap_reason is me.EnvelopeGapReason.NON_COMMENSURABLE_WITH_MASSING


def test_as1_unbounded_direction_is_a_gap_not_an_invented_ceiling(fixture_registry, tmp_path):
    """A registry with no lot_coverage rule yields a FAMILY_UNSUPPORTED gap (never a guessed
    ceiling) and, with no footprint cap, no candidate."""
    import shutil

    subset = tmp_path / "rulesets"
    subset.mkdir()
    shutil.copy(_RULESETS / "pc-height-setback-demo.rule.json", subset)
    registry = RuleRegistry(subset, snapshots=SnapshotStore(_SNAPSHOTS)).load()
    envelope = me.derive_max_envelope(_lot(), _ATTESTED, registry=registry)
    coverage = _by_dim(envelope)["max_lot_coverage_ratio"]
    assert coverage.binding_value is None
    assert coverage.gap_reason is me.EnvelopeGapReason.FAMILY_UNSUPPORTED
    assert envelope.candidate is None
    # the candidate gap is the missing saturating BINDING (not the lot geometry, which is fine).
    assert envelope.candidate_placement.status is (
        me.CandidatePlacementStatus.NO_SATURATING_BINDING
    )
    assert any("footprint" in note for note in envelope.candidate_notes)


def test_as1_unattested_input_is_allowance_unresolved_gap(fixture_registry):
    """The height rule requires an attested street_width_class; without it the allowance is
    unresolved (professional_review_required) -> a typed gap, never a fabricated height."""
    envelope = me.derive_max_envelope(_lot(), {"zoning_district": "R5"}, registry=fixture_registry)
    height = _by_dim(envelope)["max_building_height"]
    assert height.binding_value is None
    assert height.gap_reason is me.EnvelopeGapReason.ALLOWANCE_UNRESOLVED
    assert envelope.candidate is None  # no height cap -> no candidate


def test_as1_no_applicable_rule_gap(fixture_registry):
    """Facts to which no rule is applicable (wrong district) yield NO_APPLICABLE_RULE for the
    commensurable dimensions - the honest unbounded case."""
    envelope = me.derive_max_envelope(
        _lot(), {"zoning_district": "R9", "street_width_class": "wide"}, registry=fixture_registry
    )
    coverage = _by_dim(envelope)["max_lot_coverage_ratio"]
    assert coverage.gap_reason is me.EnvelopeGapReason.NO_APPLICABLE_RULE
    assert coverage.binding_value is None


# ---------------------------------------------------------------------------
# AS-2: provenance - binding id + out-competed ids; flipping the tighter rule flips the id.
# ---------------------------------------------------------------------------


def _two_coverage_registry(cov_a: float, cov_b: float, height: float = 50.0) -> _FakeRegistry:
    return _FakeRegistry(
        {"lot_coverage": ["cov-a", "cov-b"], "residential_height_setback": ["h-a"]},
        {
            "cov-a": _trace("cov-a", "max_lot_coverage_ratio", cov_a),
            "cov-b": _trace("cov-b", "max_lot_coverage_ratio", cov_b),
            "h-a": _trace("h-a", "max_building_height", height),
        },
    )


def test_as2_tightest_maximum_binds_and_names_out_competed():
    envelope = me.derive_max_envelope(_lot(), {"zoning_district": "R5"},
                                      registry=_two_coverage_registry(0.5, 0.6))
    coverage = _by_dim(envelope)["max_lot_coverage_ratio"]
    assert coverage.binding_value == pytest.approx(0.5)  # tightest ceiling
    assert coverage.binding_rule_id == "cov-a"
    assert coverage.out_competed_rule_ids == ("cov-b",)


def test_as2_mutation_flips_the_binding_rule_id():
    """Making cov-b the tighter rule flips the named binding id and the out-competed list."""
    envelope = me.derive_max_envelope(_lot(), {"zoning_district": "R5"},
                                      registry=_two_coverage_registry(0.5, 0.4))
    coverage = _by_dim(envelope)["max_lot_coverage_ratio"]
    assert coverage.binding_value == pytest.approx(0.4)
    assert coverage.binding_rule_id == "cov-b"
    assert coverage.out_competed_rule_ids == ("cov-a",)


def test_as2_minimum_direction_takes_the_largest_floor():
    """A MINIMUM-direction dimension binds to the LARGEST requirement across usable rules."""
    binding, reason, _ = me._select_binding(
        [
            _trace("y-a", "min_rear_yard_depth_ft", 20.0),
            _trace("y-b", "min_rear_yard_depth_ft", 30.0),
        ],
        "min_rear_yard_depth_ft",
        me.EnvelopeDirection.MINIMUM,
    )
    assert reason is None
    assert binding is not None
    assert binding.value == pytest.approx(30.0)
    assert binding.rule_id == "y-b"
    assert binding.out_competed == ("y-a",)


# ---------------------------------------------------------------------------
# AS-3: every dimension enumerated; honest gaps typed; nothing silently omitted.
# ---------------------------------------------------------------------------


def test_as3_all_declared_dimensions_are_enumerated(fixture_registry):
    envelope = me.derive_max_envelope(_lot(), {"zoning_district": "R5"}, registry=fixture_registry)
    emitted = {d.dimension_id for d in envelope.dimensions}
    declared = {spec.dimension_id for spec in me.ENVELOPE_DIMENSIONS}
    assert emitted == declared
    # Each dimension is either a binding value XOR a typed gap - never both, never neither.
    for d in envelope.dimensions:
        assert (d.binding_value is not None) != (d.gap_reason is not None)


def test_as3_gaps_survive_serialization(fixture_registry):
    envelope = me.derive_max_envelope(_lot(), {"zoning_district": "R5"}, registry=fixture_registry)
    doc = envelope.as_dict()
    gap_ids = {d["dimension_id"] for d in doc["dimensions"] if d["gap_reason"] is not None}
    assert "max_residential_floor_area_sq_ft" in gap_ids
    assert "min_rear_yard_depth_ft" in gap_ids
    assert doc["summary"]["total"] == len(me.ENVELOPE_DIMENSIONS)


# ---------------------------------------------------------------------------
# AS-4: generator-checker consistency.
# ---------------------------------------------------------------------------


def test_as4_candidate_passes_the_checker_at_cap(fixture_registry):
    lot = _lot(8000.0)
    envelope = me.derive_max_envelope(lot, _ATTESTED, registry=fixture_registry)
    assert envelope.candidate is not None
    validate_proposed_massing(envelope.candidate)  # a valid B0 block

    # The candidate is FITTED to the actual lot geometry and PROVEN contained.
    assert envelope.candidate_placement.status is me.CandidatePlacementStatus.FITTED
    assert envelope.candidate_placement.contained is True
    _assert_contained(envelope)

    # The engine's own consistency proof recorded both saturating checks as PASS.
    assert envelope.candidate_consistency is not None
    saturating = envelope.candidate_consistency["saturating_checks"]
    assert saturating["lot_coverage_ratio"] == "pass"
    assert saturating["building_height"] == "pass"

    # Re-run the accepted checker independently over the SAME lot: coverage at cap, height at cap.
    report = pc.check_proposal(
        envelope.candidate, lot, _ATTESTED,
        scenario_label="verify", registry=fixture_registry,
    )
    results = {r.check_id: r for r in report.results}
    assert results["lot_coverage_ratio"].outcome is pc.CheckOutcome.PASS
    assert results["lot_coverage_ratio"].provided_value == pytest.approx(0.5)
    assert results["lot_coverage_ratio"].required_value == pytest.approx(0.5)
    assert results["building_height"].outcome is pc.CheckOutcome.PASS
    assert results["building_height"].provided_value == pytest.approx(60.0)


def test_as4_footprint_saturates_the_cap_and_is_contained(fixture_registry):
    """The fitted footprint saturates the coverage cap (coverage the CHECKER computes on it is at
    the inclusive cap, never over) AND is contained within the lot rectangle. Exact float byte-
    equality is no longer claimed - at the lot's real anchor the shoelace is not byte-exact, so the
    honest, safety-critical guarantee is coverage <= cap while saturating it."""
    lot = _lot(8000.0)
    envelope = me.derive_max_envelope(lot, _ATTESTED, registry=fixture_registry)
    assert envelope.candidate is not None

    # Coverage the checker will compute (its own shoelace / the recorded lot area) is at/under cap.
    coverage = me._rect_coverage(
        *_footprint_box(envelope), lot.area_sq_ft
    )
    assert coverage <= 0.5  # never over the inclusive cap (the safety-critical direction)
    assert coverage == pytest.approx(0.5, rel=1e-6)  # and saturates it

    _assert_contained(envelope)


def _footprint_box(envelope: me.MaxEnvelope) -> tuple[float, float, float, float]:
    """(min_x, min_y, width, depth) of the emitted candidate footprint, from its vertices."""
    verts = envelope.candidate["outline"]["vertices"]
    min_x, min_y = verts[0]
    width = verts[1][0] - verts[0][0]
    depth = verts[2][1] - verts[1][1]
    return min_x, min_y, width, depth


@pytest.mark.parametrize("mutate", ["height", "coverage"])
def test_as4_epsilon_mutation_fails_the_checker(fixture_registry, mutate):
    """A +epsilon mutation of the at-cap candidate FAILs the corresponding computable check -
    proving the candidate sits at the inclusive boundary, not comfortably under it."""
    envelope = me.derive_max_envelope(_lot(8000.0), _ATTESTED, registry=fixture_registry)
    block = copy.deepcopy(envelope.candidate)
    if mutate == "height":
        block["levels"][0]["floor_to_floor_ft"] += 1e-6
        check_id = "building_height"
    else:
        for idx in (1, 2):  # push the east edge out -> footprint area over the coverage cap
            block["outline"]["vertices"][idx][0] += 1.0
        check_id = "lot_coverage_ratio"
    report = pc.check_proposal(
        block, _lot(8000.0), _ATTESTED, scenario_label="verify", registry=fixture_registry
    )
    result = {r.check_id: r for r in report.results}[check_id]
    assert result.outcome is pc.CheckOutcome.FAIL


def test_as4_tolerates_ambiguous_checker_outcome_for_multi_rule_family():
    """When a family has >1 usable rule the envelope conservatively binds the tightest, but the
    checker refuses to pick (AMBIGUOUS -> could_not_check). That is tolerated - the candidate is
    still emitted (it satisfies the tightest rule) and the consistency proof records no FAIL."""
    envelope = me.derive_max_envelope(
        _lot(8000.0), {"zoning_district": "R5"}, registry=_two_coverage_registry(0.5, 0.6)
    )
    assert envelope.candidate is not None
    assert envelope.candidate_consistency["saturating_checks"]["lot_coverage_ratio"] == (
        "could_not_check"
    )
    assert envelope.candidate_consistency["saturating_checks"]["building_height"] == "pass"


def test_multi_floor_height_saturation_stays_within_bound():
    """A binding height above the single-floor-to-floor bound is split into the fewest equal
    floors, each within the accepted bound, and the cumulative height never exceeds the cap."""
    from app.scenario.proposal import MAX_FLOOR_TO_FLOOR_FT

    levels = me._height_levels(250.0)
    assert len(levels) == 1
    total = levels[0]["floor_to_floor_ft"] * levels[0]["floor_count"]
    assert total <= 250.0
    assert levels[0]["floor_to_floor_ft"] <= MAX_FLOOR_TO_FLOOR_FT


# ---------------------------------------------------------------------------
# AS-4 (fixed-anchor deviation resolved): the candidate is FITTED to the lot's actual 2263
# geometry - anchored at the real lot, contained, and correct across translated and differently
# proportioned lots - and unsupported geometry is an EXPLICIT typed gap, never a schematic.
# ---------------------------------------------------------------------------


def test_candidate_is_anchored_to_the_actual_lot_and_translates_with_it(fixture_registry):
    """The footprint is anchored at the LOT's real SW corner, so the same lot at two different
    2263 locations yields two differently-placed candidates (the fixed-anchor bug placed both at
    the same hardcoded interior point)."""
    a_anchor, b_anchor = (985000.0, 195000.0), (1010000.0, 250000.0)
    env_a = me.derive_max_envelope(
        _lot(8000.0, anchor=a_anchor), _ATTESTED, registry=fixture_registry
    )
    env_b = me.derive_max_envelope(
        _lot(8000.0, anchor=b_anchor), _ATTESTED, registry=fixture_registry
    )
    for env, anchor in ((env_a, a_anchor), (env_b, b_anchor)):
        placement = env.candidate_placement
        assert placement.status is me.CandidatePlacementStatus.FITTED
        assert placement.contained is True
        assert placement.footprint["anchor_x"] == anchor[0]
        assert placement.footprint["anchor_y"] == anchor[1]
        assert env.candidate["outline"]["vertices"][0] == [anchor[0], anchor[1]]
        _assert_contained(env)
    # The two candidates are placed at DIFFERENT coordinates (the deviation would collapse them).
    assert env_a.candidate["outline"]["vertices"] != env_b.candidate["outline"]["vertices"]


@pytest.mark.parametrize(
    "width,depth", [(40.0, 200.0), (200.0, 40.0), (80.0, 100.0), (50.0, 160.0)]
)
def test_candidate_fits_differently_proportioned_lots(fixture_registry, width, depth):
    """A footprint is scaled to the LOT's own proportions and stays contained per dimension, so a
    long-narrow lot and a wide-shallow lot of the same area get differently-shaped candidates - not
    one fixed schematic rectangle."""
    lot = _lot(width=width, depth=depth)
    envelope = me.derive_max_envelope(lot, _ATTESTED, registry=fixture_registry)
    placement = envelope.candidate_placement
    assert placement.status is me.CandidatePlacementStatus.FITTED
    fw, fd = placement.footprint["width_ft"], placement.footprint["depth_ft"]
    assert 0.0 < fw <= width       # contained in the lot's width
    assert 0.0 < fd <= depth       # contained in the lot's depth
    # the footprint keeps the lot's aspect ratio (a scaled copy; depth shrinks only by rounding).
    assert (fw / fd) == pytest.approx(width / depth, rel=1e-6)
    _assert_contained(envelope)
    # coverage the checker computes is still at/under the cap regardless of proportion.
    coverage = me._rect_coverage(*_footprint_box(envelope), lot.area_sq_ft)
    assert coverage <= 0.5


def test_absent_lot_geometry_is_an_explicit_gap_not_a_schematic(fixture_registry):
    """No lot-line geometry -> an explicit typed placement gap and NO candidate (never the old
    fixed-anchor schematic). The binding values still stand."""
    lot = LotContext(area_sq_ft=8000.0, area_provenance={"source_id": "synthetic"})
    envelope = me.derive_max_envelope(lot, _ATTESTED, registry=fixture_registry)
    assert envelope.candidate is None
    assert envelope.candidate_consistency is None
    placement = envelope.candidate_placement
    assert placement.status is me.CandidatePlacementStatus.LOT_GEOMETRY_UNSUPPORTED
    assert "no lot-line geometry" in placement.detail
    # the dimensions are unaffected: coverage + height still bind.
    assert _by_dim(envelope)["max_lot_coverage_ratio"].binding_value == pytest.approx(0.5)
    assert _by_dim(envelope)["max_building_height"].binding_value == pytest.approx(60.0)


def test_non_axis_aligned_lot_geometry_is_unsupported(fixture_registry):
    """A diagonal lot-line segment (not the supported axis-aligned rectangle class) is an explicit
    gap - the engine never coerces it into a schematic placement."""
    segs = (
        LotLineSegment(id="S", start=(985000.0, 195000.0), end=(985100.0, 195000.0)),
        LotLineSegment(id="D", start=(985100.0, 195000.0), end=(985000.0, 195100.0)),  # diagonal
        LotLineSegment(id="W", start=(985000.0, 195100.0), end=(985000.0, 195000.0)),
    )
    lot = LotContext(
        area_sq_ft=5000.0, area_provenance={"source_id": "synthetic"}, lot_line_segments=segs
    )
    envelope = me.derive_max_envelope(lot, _ATTESTED, registry=fixture_registry)
    assert envelope.candidate is None
    assert envelope.candidate_placement.status is (
        me.CandidatePlacementStatus.LOT_GEOMETRY_UNSUPPORTED
    )


def test_interior_vertex_lot_geometry_is_unsupported(fixture_registry):
    """An L-shaped lot has a vertex inside its bounding box, so a rectangle in the box is NOT
    guaranteed inside the lot; the engine refuses to claim containment and emits an explicit gap."""
    x0, y0 = 985000.0, 195000.0
    # L-shape ring: (0,0)-(100,0)-(100,60)-(40,60)-(40,100)-(0,100) offset by (x0, y0).
    pts = [(0, 0), (100, 0), (100, 60), (40, 60), (40, 100), (0, 100)]
    abs_pts = [(x0 + px, y0 + py) for px, py in pts]
    segs = tuple(
        LotLineSegment(id=f"L{i}", start=abs_pts[i], end=abs_pts[(i + 1) % len(abs_pts)])
        for i in range(len(abs_pts))
    )
    lot = LotContext(
        area_sq_ft=8800.0, area_provenance={"source_id": "synthetic"}, lot_line_segments=segs
    )
    envelope = me.derive_max_envelope(lot, _ATTESTED, registry=fixture_registry)
    assert envelope.candidate is None
    assert envelope.candidate_placement.status is (
        me.CandidatePlacementStatus.LOT_GEOMETRY_UNSUPPORTED
    )


def test_lot_geometry_inconsistent_with_recorded_area_is_unsupported(fixture_registry):
    """When the lot-line bounding box disagrees with the recorded lot area (the coverage
    denominator), the engine will not present a lot-fitted candidate - it emits an explicit gap."""
    segs = _rect_segments(985000.0, 195000.0, 80.0, 100.0)  # bbox area 8000
    lot = LotContext(
        area_sq_ft=9000.0,  # disagrees with the 8000 bounding box
        area_provenance={"source_id": "synthetic"}, lot_line_segments=segs,
    )
    envelope = me.derive_max_envelope(lot, _ATTESTED, registry=fixture_registry)
    assert envelope.candidate is None
    assert envelope.candidate_placement.status is (
        me.CandidatePlacementStatus.LOT_GEOMETRY_UNSUPPORTED
    )
    assert "not consistent with the recorded lot area" in envelope.candidate_placement.detail


def test_footprint_exceeding_the_lot_is_an_explicit_gap(fixture_registry):
    """When the rules-derived coverage would need a footprint larger than the lot geometry can
    hold (coverage ratio > 1), the binding values still stand but no contained candidate is
    emitted - an explicit FOOTPRINT_EXCEEDS_LOT gap, never an over-lot rectangle."""
    registry = _FakeRegistry(
        {"lot_coverage": ["cov"], "residential_height_setback": ["h"]},
        {
            "cov": _trace("cov", "max_lot_coverage_ratio", 1.5),  # more than the lot can hold
            "h": _trace("h", "max_building_height", 50.0),
        },
    )
    envelope = me.derive_max_envelope(_lot(8000.0), {"zoning_district": "R5"}, registry=registry)
    assert _by_dim(envelope)["max_lot_coverage_ratio"].binding_value == pytest.approx(1.5)
    assert envelope.candidate is None
    assert envelope.candidate_placement.status is (
        me.CandidatePlacementStatus.FOOTPRINT_EXCEEDS_LOT
    )


def test_candidate_placement_is_serialized(fixture_registry):
    """The placement is machine-readable on the serialized envelope (status + detail always;
    lot_rectangle + footprint + contained on a FITTED candidate)."""
    doc = me.derive_max_envelope(_lot(8000.0), _ATTESTED, registry=fixture_registry).as_dict()
    placement = doc["candidate_placement"]
    assert placement["status"] == "fitted"
    assert placement["contained"] is True
    assert placement["lot_rectangle"]["anchor_x"] == 985000.0
    assert placement["footprint"]["width_ft"] > 0.0


# ---------------------------------------------------------------------------
# AS-5: determinism (same inputs -> byte-identical result).
# ---------------------------------------------------------------------------


def test_as5_deterministic(fixture_registry):
    def run() -> str:
        env = me.derive_max_envelope(_lot(8000.0), _ATTESTED, registry=fixture_registry,
                                     label="env-A")
        return json.dumps(env.as_dict(), sort_keys=True)

    assert run() == run()


# ---------------------------------------------------------------------------
# AS-6: no scenario document / contract version; typed precondition refusals.
# ---------------------------------------------------------------------------


def test_as6_no_scenario_document_or_contract_version(fixture_registry):
    source = Path(me.__file__).read_text(encoding="utf-8")
    for token in (
        "build_scenario", "validate_scenario_document", "SCENARIO_CONTRACT_VERSION",
        "from app.scenario.builder", "from app.scenario.contract",
    ):
        assert token not in source, f"module must not reference {token!r}"

    envelope = me.derive_max_envelope(_lot(), _ATTESTED, registry=fixture_registry)
    doc = envelope.as_dict()
    for scenario_key in ("contract_version", "scenario_id", "constraint_completeness"):
        assert scenario_key not in doc
    # The candidate is a proposed_massing block (kind 'proposed'), never a scenario document.
    assert doc["candidate"]["provenance"]["kind"] == "proposed"


def test_as6_non_lotcontext_refused():
    with pytest.raises(me.MaxEnvelopeError) as exc:
        me.derive_max_envelope({"area_sq_ft": 8000.0}, registry=_two_coverage_registry(0.5, 0.6))
    assert exc.value.field == "lot"


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
def test_as6_bad_area_refused(bad):
    lot = LotContext(area_sq_ft=bad, area_provenance={})
    with pytest.raises(me.MaxEnvelopeError) as exc:
        me.derive_max_envelope(lot, registry=_two_coverage_registry(0.5, 0.6))
    assert exc.value.field == "lot.area_sq_ft"


def test_unmapped_lot_facts_are_surfaced_never_fed(fixture_registry):
    envelope = me.derive_max_envelope(
        _lot(), {"zoning_district": "R5", "boobytrap": 1, "lot_area_sq_ft": 1.0},
        registry=fixture_registry,
    )
    assert "boobytrap" in envelope.unmapped_lot_facts
    assert "lot_area_sq_ft" in envelope.unmapped_lot_facts  # the redundant caller copy
    assert envelope.rule_input_bindings["lot_area_sq_ft"] == "lot_context.area_sq_ft"


def test_real_registry_compatibility():
    """Against the REAL accepted registry: lot_coverage is unsupported (honest gap, no candidate),
    residential FAR + rear yard stay non-commensurable, and no value is fabricated."""
    lot = LotContext(area_sq_ft=8000.0, area_provenance={})
    facts = {
        "zoning_district": "R5", "overlay_present": False, "special_district_present": False,
        "historic_district": False, "large_site": False,
    }
    envelope = me.derive_max_envelope(lot, facts, registry=RuleRegistry().load())
    dims = _by_dim(envelope)
    assert dims["max_lot_coverage_ratio"].gap_reason is me.EnvelopeGapReason.FAMILY_UNSUPPORTED
    assert dims["max_residential_floor_area_sq_ft"].gap_reason is (
        me.EnvelopeGapReason.NON_COMMENSURABLE_WITH_MASSING
    )
    assert envelope.candidate is None  # no coverage cap -> no footprint
