"""Offline acceptance pack for :mod:`app.drawings.drawing_alignment` (M5-T124,
D-087 PKT-L2, phase C2 drawing-to-lot alignment).

Every fixture is built by KEYWORD inside this file; nothing is imported from another
test module. Each guarding test is paired with a NAMED in-process mutation
(monkeypatching a module seam) that reddens it - the mutation asserts the FLIPPED
outcome, proving the guard is load-bearing. No harness is committed.

The tests import only :mod:`app.drawings.drawing_alignment` and, transitively,
:mod:`app.scenario.proposal` (the alignment contract) - neither pulls the 3.12-only
``app.documents`` chain, so the file collects and runs on the sandbox's Python 3.11.
CI (3.12) is the authority.
"""

from __future__ import annotations

import math

import pytest
from shapely.geometry import Polygon

from app.drawings import drawing_alignment as da
from app.drawings.drawing_alignment import (
    ControlPair,
    PlaneTransform,
    align_draft_to_lot,
)

# --- fixtures (keyword-constructed) --------------------------------------------------

# A target base well inside the NYC EPSG:2263 bounds (900000..1100000 x, 100000..300000).
BASE = (1_000_000.0, 200_000.0)
PRECISION = "imported drawing - not survey-confirmed"


def _provenance() -> dict:
    return {
        "input_class": "imported_pdf",
        "precision": PRECISION,
        "label": "Proposed - not a city record",
        "frame_note": "outline is in a LOCAL scaled sheet frame",
    }


def _rect_outline() -> list[list[float]]:
    # A closed local-frame rectangle (distinct vertices + repeated closing vertex).
    return [[10.0, 10.0], [40.0, 10.0], [40.0, 30.0], [10.0, 30.0], [10.0, 10.0]]


def _block(vertices: list[list[float]] | None = None, *, levels: list | None = None) -> dict:
    return {
        "outline": {"srid": 2263, "vertices": vertices or _rect_outline()},
        "levels": levels or [{"level_index": 0, "floor_count": 3, "floor_to_floor_ft": 10.0}],
        "exterior_walls": [],
        "provenance": {
            "author": "architect",
            "editor_version": "pdf-sheet-import/1",
            "kind": "proposed",
        },
    }


def _lot(x0: float = 0.0, y0: float = 0.0, w: float = 500.0, h: float = 500.0) -> list:
    return [
        (BASE[0] + x0, BASE[1] + y0),
        (BASE[0] + x0 + w, BASE[1] + y0),
        (BASE[0] + x0 + w, BASE[1] + y0 + h),
        (BASE[0] + x0, BASE[1] + y0 + h),
    ]


def _translation_pairs() -> list[ControlPair]:
    return [
        ControlPair(local=(0.0, 0.0), target=(BASE[0], BASE[1])),
        ControlPair(local=(100.0, 0.0), target=(BASE[0] + 100.0, BASE[1])),
        ControlPair(local=(0.0, 50.0), target=(BASE[0], BASE[1] + 50.0)),
    ]


def _true_rigid(angle_rad: float):
    c, s = math.cos(angle_rad), math.sin(angle_rad)

    def apply(x: float, y: float) -> tuple[float, float]:
        return (c * x - s * y + BASE[0], s * x + c * y + BASE[1])

    return apply


def _rotation_pairs(angle_rad: float) -> list[ControlPair]:
    apply = _true_rigid(angle_rad)
    locals_ = [(0.0, 0.0), (100.0, 0.0), (0.0, 50.0), (60.0, 40.0)]
    return [ControlPair(local=p, target=apply(*p)) for p in locals_]


def _signed_area(ring: list) -> float:
    pts = [(float(x), float(y)) for x, y in ring]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    total = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        total += x0 * y1 - x1 * y0
    return total / 2.0


# ============================ AS-1: the rigid fit ====================================


def test_translation_fit_lands_outline_on_asserted_2263_vertices():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    assert res.ok is True
    assert res.proposed_massing["outline"]["vertices"] == [
        [1000010.0, 200010.0],
        [1000040.0, 200010.0],
        [1000040.0, 200030.0],
        [1000010.0, 200030.0],
        [1000010.0, 200010.0],
    ]
    assert res.alignment["translation_ft"] == pytest.approx([BASE[0], BASE[1]])
    assert res.alignment["rotation_deg"] == pytest.approx(0.0, abs=1e-9)
    assert res.alignment["max_residual_ft"] == pytest.approx(0.0, abs=1e-9)


def test_mutation_translation_dropped_reddens_translation_fit(monkeypatch):
    # Mutation: the fit forgets its translation (identity map). The outline then stays
    # in the near-origin local frame, so it fails the NYC-2263 contract - NOT the
    # asserted in-bounds vertices.
    monkeypatch.setattr(
        da, "_rigid_fit", lambda s, t: PlaneTransform(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    )
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    assert res.ok is False and res.reason == "aligned_invalid"


def test_ninety_degree_rotation_fit_exact_vertices():
    pairs = _rotation_pairs(math.pi / 2.0)
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    assert res.ok is True
    apply = _true_rigid(math.pi / 2.0)
    expected = [list(apply(x, y)) for x, y in _rect_outline()]
    got = res.proposed_massing["outline"]["vertices"]
    for g, e in zip(got, expected, strict=True):
        assert g == pytest.approx(e, abs=1e-6)
    assert res.alignment["rotation_deg"] == pytest.approx(90.0, abs=1e-9)


def test_mutation_rotation_sign_flipped_reddens_rotation_fit(monkeypatch):
    # Mutation: negate the rotation sense (a plausible atan2 argument-swap / sign bug).
    real = da._rigid_fit

    def flipped(source, target):
        t = real(source, target)
        return PlaneTransform(t.m00, -t.m01, -t.m10, t.m11, t.tx, t.ty)

    monkeypatch.setattr(da, "_rigid_fit", flipped)
    pairs = _rotation_pairs(math.pi / 2.0)
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    apply = _true_rigid(math.pi / 2.0)
    expected = [list(apply(x, y)) for x, y in _rect_outline()]
    got = res.proposed_massing["outline"]["vertices"]
    assert any(g != pytest.approx(e, abs=1e-6) for g, e in zip(got, expected, strict=True))


def test_arbitrary_rotation_fit_matches_true_transform():
    angle = math.radians(31.7)
    pairs = _rotation_pairs(angle)
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    assert res.ok is True
    apply = _true_rigid(angle)
    expected = [list(apply(x, y)) for x, y in _rect_outline()]
    got = res.proposed_massing["outline"]["vertices"]
    for g, e in zip(got, expected, strict=True):
        assert g == pytest.approx(e, abs=1e-6)
    assert res.alignment["rotation_deg"] == pytest.approx(31.7, abs=1e-6)
    assert res.alignment["confirmed_scale"] == 1.0


def test_mutation_identity_rotation_reddens_arbitrary_rotation(monkeypatch):
    # Mutation: drop the rotation (translation-only fit). The rotated outline no longer
    # matches the true transform.
    def no_rotation(source, target):
        cen_s = da._centroid(source)
        cen_t = da._centroid(target)
        return PlaneTransform(1.0, 0.0, 0.0, 1.0, cen_t[0] - cen_s[0], cen_t[1] - cen_s[1])

    monkeypatch.setattr(da, "_rigid_fit", no_rotation)
    angle = math.radians(31.7)
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _rotation_pairs(angle))
    apply = _true_rigid(angle)
    expected = [list(apply(x, y)) for x, y in _rect_outline()]
    got = res.proposed_massing["outline"]["vertices"]
    assert any(g != pytest.approx(e, abs=1e-6) for g, e in zip(got, expected, strict=True))


def test_applied_transform_is_a_proper_rigid_motion():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _rotation_pairs(math.radians(31.7)))
    # A proper rigid motion preserves orientation: the aligned outline's signed area has
    # the same sign as the local outline's.
    assert res.ok is True
    local_sign = math.copysign(1.0, _signed_area(_rect_outline()))
    aligned_sign = math.copysign(1.0, _signed_area(res.proposed_massing["outline"]["vertices"]))
    assert local_sign == aligned_sign


# ============ AS-2: discrepancies shown, never reconciled ============================


def test_residuals_reported_per_pair_and_max_against_tolerance():
    # Noisy target picks: every residual is reported, and the max drives the disclosure.
    apply = _true_rigid(0.0)
    locals_ = [(0.0, 0.0), (100.0, 0.0), (0.0, 50.0), (80.0, 60.0)]
    noise = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (3.0, 0.0)]
    pairs = [
        ControlPair(local=p, target=(apply(*p)[0] + n[0], apply(*p)[1] + n[1]))
        for p, n in zip(locals_, noise, strict=True)
    ]
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs, tolerance_ft=1.0)
    assert res.ok is True
    assert len(res.alignment["residuals_ft"]) == len(pairs)
    assert res.alignment["max_residual_ft"] == pytest.approx(max(res.alignment["residuals_ft"]))
    assert res.alignment["max_residual_ft"] > 1.0
    types = {d["type"] for d in res.discrepancies}
    assert "residual_exceeds_tolerance" in types


def test_mutation_drop_residual_reddens_residual_report(monkeypatch):
    real = da._residuals
    monkeypatch.setattr(da, "_residuals", lambda tr, s, t: real(tr, s, t)[:-1])
    apply = _true_rigid(0.0)
    locals_ = [(0.0, 0.0), (100.0, 0.0), (0.0, 50.0), (80.0, 60.0)]
    pairs = [ControlPair(local=p, target=apply(*p)) for p in locals_]
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    # With a residual dropped the report no longer has one per pair.
    assert len(res.alignment["residuals_ft"]) != len(pairs)


def test_two_pair_fit_disclosed_as_unchecked():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs()[:2])
    assert res.ok is True
    assert {d["type"] for d in res.discrepancies} == {"two_pairs_unchecked"}


def test_mutation_two_pair_disclosure_suppressed(monkeypatch):
    monkeypatch.setattr(da, "_is_unchecked_two_pair", lambda n: False)
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs()[:2])
    assert "two_pairs_unchecked" not in {d["type"] for d in res.discrepancies}


def _scale_mismatch_pairs() -> list[ControlPair]:
    # Target = 2 x source + BASE: the pairs IMPLY a scale of 2, the rigid fit applies 1.
    return [
        ControlPair(local=(0.0, 0.0), target=(BASE[0], BASE[1])),
        ControlPair(local=(100.0, 0.0), target=(BASE[0] + 200.0, BASE[1])),
        ControlPair(local=(0.0, 50.0), target=(BASE[0], BASE[1] + 100.0)),
        ControlPair(local=(60.0, 40.0), target=(BASE[0] + 120.0, BASE[1] + 80.0)),
    ]


def _edge_len(vertices: list) -> float:
    (x0, y0), (x1, y1) = vertices[0], vertices[1]
    return math.hypot(x1 - x0, y1 - y0)


def test_implied_scale_disclosed_never_applied():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _scale_mismatch_pairs())
    assert res.ok is True
    assert res.alignment["implied_scale"] == pytest.approx(2.0, rel=1e-6)
    assert res.alignment["confirmed_scale"] == 1.0
    assert "scale_mismatch" in {d["type"] for d in res.discrepancies}
    # NOT applied: the aligned outline preserves the local edge length (rigid).
    local_edge = _edge_len(_rect_outline())
    aligned_edge = _edge_len(res.proposed_massing["outline"]["vertices"])
    assert aligned_edge == pytest.approx(local_edge, rel=1e-9)


def test_mutation_apply_implied_scale_reddens_scale_disclosure(monkeypatch):
    # Mutation: the applied transform uses the IMPLIED scale (2) instead of 1. The
    # aligned outline is then rescaled - the local edge length is no longer preserved.
    monkeypatch.setattr(da, "_applied_scale", lambda: 2.0)
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _scale_mismatch_pairs())
    local_edge = _edge_len(_rect_outline())
    aligned_edge = _edge_len(res.proposed_massing["outline"]["vertices"])
    assert aligned_edge == pytest.approx(2.0 * local_edge, rel=1e-6)


def _mirror_pairs() -> list[ControlPair]:
    # Target = reflect-about-x(source) + BASE: a reflection fits better than a rotation.
    locals_ = [(0.0, 0.0), (100.0, 0.0), (0.0, 50.0), (60.0, 40.0)]
    return [ControlPair(local=p, target=(p[0] + BASE[0], -p[1] + BASE[1])) for p in locals_]


def test_better_mirror_fit_disclosed_never_flipped():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _mirror_pairs())
    assert res.ok is True
    assert "better_mirror_fit" in {d["type"] for d in res.discrepancies}
    assert res.alignment["mirror_rms_residual_ft"] < res.alignment["rms_residual_ft"]
    # NOT flipped: the applied outline keeps the local orientation (proper motion).
    local_sign = math.copysign(1.0, _signed_area(_rect_outline()))
    aligned_sign = math.copysign(1.0, _signed_area(res.proposed_massing["outline"]["vertices"]))
    assert local_sign == aligned_sign


def test_mutation_allow_reflection_reddens_mirror_disclosure(monkeypatch):
    # Mutation: apply the mirror fit when it is better ("allow reflection"). The aligned
    # outline is then flipped - its orientation is reversed.
    monkeypatch.setattr(
        da,
        "_choose_transform",
        lambda rigid, mirror, rr, mr: mirror if mr < rr else rigid,
    )
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _mirror_pairs())
    local_sign = math.copysign(1.0, _signed_area(_rect_outline()))
    aligned_sign = math.copysign(1.0, _signed_area(res.proposed_massing["outline"]["vertices"]))
    assert local_sign != aligned_sign


def _outside_lot_setup():
    # Translate the outline to 2263; the lot's right edge cuts through it so part lies
    # outside. Outline -> x in [1000010, 1000040], y in [200010, 200030]. Lot right edge
    # at x = 1000025 -> outside strip is 15 ft x 20 ft = 300 sq ft.
    lot = [
        (BASE[0], BASE[1]),
        (BASE[0] + 25.0, BASE[1]),
        (BASE[0] + 25.0, BASE[1] + 500.0),
        (BASE[0], BASE[1] + 500.0),
    ]
    return _translation_pairs(), lot


def test_outside_lot_area_disclosed_never_clipped():
    pairs, lot = _outside_lot_setup()
    res = align_draft_to_lot(_block(), _provenance(), lot, pairs)
    assert res.ok is True
    assert res.alignment["outline_area_outside_lot_sq_ft"] == pytest.approx(300.0, rel=1e-6)
    assert "outline_outside_lot" in {d["type"] for d in res.discrepancies}
    # NOT clipped: the aligned outline is the full transformed rectangle (5 positions),
    # not the intersection with the lot.
    assert res.proposed_massing["outline"]["vertices"] == [
        [1000010.0, 200010.0],
        [1000040.0, 200010.0],
        [1000040.0, 200030.0],
        [1000010.0, 200030.0],
        [1000010.0, 200010.0],
    ]


def test_mutation_clip_to_lot_reddens_outside_lot_disclosure(monkeypatch):
    def clip(vertices, lot_ring):
        inter = Polygon([(x, y) for x, y in vertices]).intersection(
            Polygon([(x, y) for x, y in lot_ring])
        )
        coords = [[x, y] for x, y in inter.exterior.coords]
        return coords

    monkeypatch.setattr(da, "_final_outline_vertices", clip)
    pairs, lot = _outside_lot_setup()
    res = align_draft_to_lot(_block(), _provenance(), lot, pairs)
    # Clipped: the outline no longer reaches the full transformed extent (x=1000040).
    xs = [v[0] for v in res.proposed_massing["outline"]["vertices"]]
    assert max(xs) < 1000040.0


# ============ AS-3: the contract (re-validation) =====================================


def test_aligned_draft_passes_validate_and_keeps_kind_proposed():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    assert res.ok is True
    assert res.proposed_massing["provenance"]["kind"] == "proposed"
    # The aligned block is contract-valid (re-validation did not raise).
    da.validate_proposed_massing(res.proposed_massing)


def test_still_out_of_bounds_result_is_a_typed_refusal():
    # An identity fit (target == source, near origin) leaves the outline in the local
    # frame, which fails the NYC-2263 bounds check -> typed aligned_invalid.
    pairs = [
        ControlPair(local=(0.0, 0.0), target=(0.0, 0.0)),
        ControlPair(local=(100.0, 0.0), target=(100.0, 0.0)),
        ControlPair(local=(0.0, 50.0), target=(0.0, 50.0)),
    ]
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    assert res.ok is False
    assert res.reason == "aligned_invalid"
    assert res.field.startswith("proposed_massing.outline")


def test_mutation_skip_revalidation_reddens_out_of_bounds_refusal(monkeypatch):
    monkeypatch.setattr(da, "validate_proposed_massing", lambda block: None)
    pairs = [
        ControlPair(local=(0.0, 0.0), target=(0.0, 0.0)),
        ControlPair(local=(100.0, 0.0), target=(100.0, 0.0)),
        ControlPair(local=(0.0, 50.0), target=(0.0, 50.0)),
    ]
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    # With the contract skipped, the out-of-bounds outline is NOT refused.
    assert res.ok is True


def test_alignment_block_is_complete():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    block = res.alignment
    for key in (
        "method", "formula", "pair_count", "rotation_rad", "rotation_deg",
        "translation_ft", "residuals_ft", "max_residual_ft", "rms_residual_ft",
        "tolerance_ft", "confirmed_scale", "implied_scale", "mirror_rms_residual_ft",
        "outline_area_sq_ft", "outline_area_outside_lot_sq_ft", "input_precision",
        "precision_note", "discrepancies",
    ):
        assert key in block
    assert block["method"] == da.ALIGNMENT_METHOD
    assert block["pair_count"] == 3


def test_per_level_outline_is_also_transformed_into_2263():
    per_level = {"level_index": 0, "floor_count": 2, "floor_to_floor_ft": 10.0,
                 "outline": {"srid": 2263, "vertices": _rect_outline()}}
    res = align_draft_to_lot(
        _block(levels=[per_level]), _provenance(), _lot(), _translation_pairs()
    )
    assert res.ok is True
    lvl_vertices = res.proposed_massing["levels"][0]["outline"]["vertices"]
    assert lvl_vertices[0] == [1000010.0, 200010.0]


# ============ AS-4: honesty + safety =================================================


def test_precision_label_kept_exactly_and_never_upgraded():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    assert res.provenance["precision"] == PRECISION
    assert res.alignment["input_precision"] == PRECISION


def test_mutation_precision_upgraded_reddens_honesty(monkeypatch):
    monkeypatch.setattr(da, "_input_precision", lambda prov: "survey-confirmed - authoritative")
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    # The mutation upgrades the precision the alignment block reports.
    assert res.alignment["input_precision"] != PRECISION


def test_no_permit_or_approved_or_maximum_allowed_wording():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _mirror_pairs())
    import json

    blob = json.dumps(
        {"alignment": res.alignment, "provenance": res.provenance,
         "proposed_massing": res.proposed_massing}
    ).lower()
    for forbidden in ("permit", "approved", "maximum allowed", "maximum-allowed"):
        assert forbidden not in blob


def test_every_output_number_is_finite():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _scale_mismatch_pairs())
    scalars = [
        res.alignment["rotation_rad"], res.alignment["rotation_deg"],
        res.alignment["max_residual_ft"], res.alignment["rms_residual_ft"],
        res.alignment["implied_scale"], *res.alignment["translation_ft"],
        *res.alignment["residuals_ft"],
    ]
    assert all(math.isfinite(v) for v in scalars)


# ============ AS-4/AS-5: bounded inputs refused typed ================================


def test_too_few_pairs_refused_typed():
    res = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs()[:1])
    assert res.ok is False and res.reason == "too_few_pairs"


def test_too_many_pairs_refused_typed():
    pair = ControlPair(local=(0.0, 0.0), target=(BASE[0], BASE[1]))
    res = align_draft_to_lot(
        _block(), _provenance(), _lot(), [pair] * (da.MAX_CONTROL_PAIRS + 1)
    )
    assert res.ok is False and res.reason == "too_many_pairs"


def test_non_finite_control_coordinate_refused_typed():
    pairs = _translation_pairs() + [
        ControlPair(local=(float("inf"), 0.0), target=(BASE[0] + 5.0, BASE[1]))
    ]
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    assert res.ok is False and res.reason == "non_finite_input"


def test_coincident_source_points_refused_typed():
    pairs = [
        ControlPair(local=(5.0, 5.0), target=(BASE[0], BASE[1])),
        ControlPair(local=(5.0, 5.0), target=(BASE[0] + 100.0, BASE[1])),
        ControlPair(local=(5.0, 5.0), target=(BASE[0], BASE[1] + 100.0)),
    ]
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    assert res.ok is False and res.reason == "coincident_source"


def test_indeterminate_rotation_refused_typed():
    # Distinct sources but all targets coincident: no rotation angle is determined.
    pairs = [
        ControlPair(local=(0.0, 0.0), target=(BASE[0], BASE[1])),
        ControlPair(local=(100.0, 0.0), target=(BASE[0], BASE[1])),
        ControlPair(local=(0.0, 50.0), target=(BASE[0], BASE[1])),
    ]
    res = align_draft_to_lot(_block(), _provenance(), _lot(), pairs)
    assert res.ok is False and res.reason == "indeterminate_rotation"


def test_bad_control_pair_shape_refused_typed():
    res = align_draft_to_lot(
        _block(), _provenance(), _lot(), [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]
    )
    assert res.ok is False and res.reason == "bad_control_pair"


def test_bad_draft_block_refused_typed():
    res = align_draft_to_lot({"outline": None}, _provenance(), _lot(), _translation_pairs())
    assert res.ok is False and res.reason == "bad_draft_block"


def test_bad_lot_ring_refused_typed():
    res = align_draft_to_lot(_block(), _provenance(), [(1.0, 2.0)], _translation_pairs())
    assert res.ok is False and res.reason == "bad_lot_ring"


def test_lot_ring_over_cap_refused_typed():
    big = [(BASE[0] + i, BASE[1]) for i in range(da.MAX_LOT_RING_VERTICES + 1)]
    res = align_draft_to_lot(_block(), _provenance(), big, _translation_pairs())
    assert res.ok is False and res.reason == "bad_lot_ring"


def test_non_finite_lot_coordinate_refused_typed():
    lot = [(BASE[0], BASE[1]), (float("nan"), BASE[1]), (BASE[0], BASE[1] + 10.0)]
    res = align_draft_to_lot(_block(), _provenance(), lot, _translation_pairs())
    assert res.ok is False and res.reason == "non_finite_input"


# ============ AS-5: scope / purity ==================================================


def test_two_identical_calls_are_equal_no_persistence():
    a = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    b = align_draft_to_lot(_block(), _provenance(), _lot(), _translation_pairs())
    assert a.proposed_massing == b.proposed_massing
    assert a.alignment == b.alignment
    assert a.discrepancies == b.discrepancies


def test_input_block_is_not_mutated():
    block = _block()
    before = block["outline"]["vertices"][0][:]
    align_draft_to_lot(block, _provenance(), _lot(), _translation_pairs())
    assert block["outline"]["vertices"][0] == before  # deep-copied, not mutated in place


def test_module_imports_no_io_or_network():
    import inspect

    source = inspect.getsource(da)
    for banned in ("import os", "import socket", "import urllib", "open(", "requests"):
        assert banned not in source
