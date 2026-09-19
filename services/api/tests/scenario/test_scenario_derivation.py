"""Property + hand-computed-fixture acceptance pack for :mod:`app.scenario.derivation`
(task M5-T051, D-076 phase B1).

The module derives a proposal's deterministic geometric FACTS - footprint, lot coverage,
per-level areas, gross floor-area treatment, wall setbacks, and heights - each in a typed
:class:`EvidenceRecord`. These are PROVIDED values, never allowances (D-076-R002): the
tests verify the FACT boundary directly (source_class, method, input identifiers), the
hand-computed arithmetic in ``fixtures/derivation/`` (never self-proven), the invariance
properties (rotation / translation), and the typed fail-closed refusals.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import re
from pathlib import Path

import pytest

from app.scenario.derivation import (
    SOURCE_CLASS,
    AttestedStreetLine,
    EvidenceRecord,
    GrossFloorAreaTreatment,
    LotContext,
    LotLineSegment,
    ProposalDerivation,
    ProposalDerivationError,
    StreetSetbackResolution,
    derive_proposal,
)
from app.scenario.proposal import ProposedMassingError

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "derivation"

# The exact rule-language ("allowance-class") terms that must NEVER appear in any derived
# output, field name, vocabulary entry, or message (AS-4 / D-076-R002). "allowance" itself
# is a disclaimer word (used only as "not an allowance") and is deliberately not on this
# list; these four are the words that would misrepresent a PROVIDED fact as a rule result.
_ALLOWANCE_TERMS = re.compile(
    r"\b(permitted|permits|permit|required|allowed|compliant|obliges|obliged)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Fixture loading (data only - never runs the module to produce expectations)
# ---------------------------------------------------------------------------


def _load_fixture(name: str) -> dict:
    return json.loads((_FIXTURE_DIR / f"{name}.json").read_text(encoding="utf-8"))


def _lot_context(lot: dict) -> LotContext:
    return LotContext(
        area_sq_ft=lot["area_sq_ft"],
        area_provenance=lot["area_provenance"],
        lot_line_segments=tuple(
            LotLineSegment(
                id=seg["id"],
                start=(float(seg["start"][0]), float(seg["start"][1])),
                end=(float(seg["end"][0]), float(seg["end"][1])),
            )
            for seg in lot["lot_line_segments"]
        ),
        street_lines=tuple(
            AttestedStreetLine(
                wall_id=line["wall_id"],
                start=(float(line["start"][0]), float(line["start"][1])),
                end=(float(line["end"][0]), float(line["end"][1])),
                attestation=line["attestation"],
            )
            for line in lot["street_lines"]
        ),
    )


def _derive_fixture(name: str) -> tuple[ProposalDerivation, dict]:
    fixture = _load_fixture(name)
    result = derive_proposal(fixture["proposed_massing"], _lot_context(fixture["lot"]))
    return result, fixture["expected"]


ALL_FIXTURES = ["rectangle_100x80", "l_shape_multilevel", "wall_setback"]


def _setback(result: ProposalDerivation, wall_id: str):
    return next(s for s in result.wall_setbacks if s.wall_id == wall_id)


def _level_area(result: ProposalDerivation, level_index: int):
    return next(a for a in result.per_level_areas if a.level_index == level_index)


def _level_height(result: ProposalDerivation, level_index: int):
    return next(h for h in result.level_heights if h.level_index == level_index)


# ---------------------------------------------------------------------------
# AS-1 / AS-2 / AS-3: hand-computed fixtures match exactly
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_fixture_footprint_and_coverage(name: str) -> None:
    result, expected = _derive_fixture(name)
    assert result.footprint_area.value == expected["footprint_area_sq_ft"]
    assert result.footprint_area.unit == "square_feet"
    assert result.lot_coverage.value == expected["lot_coverage_ratio"]
    assert result.lot_coverage.unit == "ratio"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_fixture_per_level_areas(name: str) -> None:
    result, expected = _derive_fixture(name)
    for level in expected["per_level_areas"]:
        derived = _level_area(result, level["level_index"])
        assert derived.evidence.value == level["area_sq_ft"]
        assert derived.outline_source == level["outline_source"]
        assert derived.evidence.unit == "square_feet"


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_fixture_gross_and_heights(name: str) -> None:
    result, expected = _derive_fixture(name)
    assert result.gross_floor_area.evidence.value == expected["gross_floor_area_sq_ft"]
    assert result.cumulative_height.value == expected["cumulative_height_ft"]
    for level in expected["level_heights_ft"]:
        assert _level_height(result, level["level_index"]).evidence.value == level["height_ft"]


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_fixture_wall_setbacks(name: str) -> None:
    result, expected = _derive_fixture(name)
    for wall in expected["wall_setbacks"]:
        setback = _setback(result, wall["wall_id"])
        assert setback.lot_line_setback.value == wall["lot_line_ft"]
        assert setback.street_line_setback.value == wall["street_line_ft"]
        assert setback.street_setback_resolution.value == wall["street_resolution"]


def test_rectangle_is_the_primary_as1_case() -> None:
    result, _ = _derive_fixture("rectangle_100x80")
    assert result.footprint_area.value == 8000.0
    assert result.lot_coverage.value == 0.5
    # Every value arrives in an EvidenceRecord naming its inputs, method, source_class.
    assert result.footprint_area.method == "shoelace_area_2263"
    assert result.footprint_area.input_ids == (result.outline_digest,)
    assert result.source_class == SOURCE_CLASS


def test_l_shape_concavity_area_exact() -> None:
    result, _ = _derive_fixture("l_shape_multilevel")
    # Shoelace handles concavity: 8000 (full) - 1600 (notch) = 6400.
    assert result.footprint_area.value == 6400.0
    # A smaller upper level with its OWN outline yields its own per-level area.
    upper = _level_area(result, 1)
    assert upper.outline_source == "own_outline"
    assert upper.evidence.value == 1600.0
    # The gross sum matches the declared vocabulary and never claims a zoning floor area.
    treatment = result.gross_floor_area.treatment
    assert treatment is GrossFloorAreaTreatment.PER_LEVEL_GROSS_NO_DEDUCTIONS
    joined = " ".join(result.gross_floor_area.inclusions + result.gross_floor_area.exclusions)
    assert "zoning floor area" in joined.lower()  # only as the explicit "NOT a zoning floor area"
    assert "not a zoning floor area" in joined.lower()


def test_street_setback_derived_carries_attestation_identifiers() -> None:
    result, _ = _derive_fixture("wall_setback")
    front = _setback(result, "front")
    assert front.street_setback_resolution is StreetSetbackResolution.DERIVED
    assert front.street_line_setback.value == 25.0
    # The EvidenceRecord carries the attestation identifiers (provenance + a digest id).
    assert front.street_line_setback.provenance is not None
    assert str(front.street_line_setback.provenance["classification_basis"]).startswith("DCM")
    assert any(
        ref.startswith("street_attestation:") for ref in front.street_line_setback.input_ids
    )


def test_street_setback_absent_is_typed_honest_absence() -> None:
    result, _ = _derive_fixture("wall_setback")
    rear = _setback(result, "rear")
    assert rear.street_setback_resolution is StreetSetbackResolution.ABSENT_NO_ATTESTATION
    assert rear.street_line_setback.value is None  # never a default distance
    assert rear.street_line_setback.provenance is None
    # The lot-line setback is still derived (18/48 hand values).
    assert rear.lot_line_setback.value == 48.0


def test_lot_area_provenance_carried_through() -> None:
    result, _ = _derive_fixture("rectangle_100x80")
    assert result.lot_coverage.provenance is not None
    assert result.lot_coverage.provenance["bbl"] == "1000010001"
    assert any(ref.startswith("lot_area_provenance:") for ref in result.lot_coverage.input_ids)


# ---------------------------------------------------------------------------
# AS-1: every derived value carries a full EvidenceRecord with source_class
# ---------------------------------------------------------------------------


def _all_records(result: ProposalDerivation) -> list[EvidenceRecord]:
    records = [
        result.footprint_area,
        result.lot_coverage,
        result.gross_floor_area.evidence,
        result.cumulative_height,
    ]
    records += [la.evidence for la in result.per_level_areas]
    records += [lh.evidence for lh in result.level_heights]
    for setback in result.wall_setbacks:
        records += [setback.lot_line_setback, setback.street_line_setback]
    return records


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_every_record_is_a_provided_derivation(name: str) -> None:
    result, _ = _derive_fixture(name)
    for record in _all_records(result):
        assert record.source_class == SOURCE_CLASS
        assert record.method  # a stable non-empty method name
        assert record.input_ids  # names the inputs it was computed from
        assert record.unit in {"square_feet", "ratio", "feet", "count"}


# ---------------------------------------------------------------------------
# AS-4: facts, not allowances - no rule-language anywhere in the output
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ALL_FIXTURES)
def test_no_allowance_language_in_output(name: str) -> None:
    # The derivation's OWN vocabulary (method, unit, detail, source_class, input ids,
    # and the gross-treatment vocabulary) must never use rule language; caller-supplied
    # provenance carried through verbatim is not the module's vocabulary and is excluded.
    result, _ = _derive_fixture(name)
    for record in _all_records(result):
        for field_value in (record.method, record.unit, record.detail, record.source_class):
            assert not _ALLOWANCE_TERMS.search(field_value), field_value
        for ref in record.input_ids:
            assert not _ALLOWANCE_TERMS.search(ref), ref
    vocab = " ".join(
        (result.gross_floor_area.treatment.value,)
        + result.gross_floor_area.inclusions
        + result.gross_floor_area.exclusions
    )
    assert not _ALLOWANCE_TERMS.search(vocab), vocab


def test_source_class_literal_is_proposed_derivation() -> None:
    assert SOURCE_CLASS == "proposed_derivation"


# ---------------------------------------------------------------------------
# AS-5: invariance properties (rotation of vertex order; translation)
# ---------------------------------------------------------------------------


def _rotate_ring(vertices: list[list[float]], shift: int) -> list[list[float]]:
    """Cyclically rotate a closed ring's DISTINCT vertices by ``shift`` and re-close it."""
    distinct = vertices[:-1]
    rotated = distinct[shift:] + distinct[:shift]
    return [list(pt) for pt in rotated] + [list(rotated[0])]


@pytest.mark.parametrize("name", ["rectangle_100x80", "l_shape_multilevel"])
def test_vertex_order_rotation_preserves_area(name: str) -> None:
    fixture = _load_fixture(name)
    base_result = derive_proposal(fixture["proposed_massing"], _lot_context(fixture["lot"]))
    block = copy.deepcopy(fixture["proposed_massing"])
    block["outline"]["vertices"] = _rotate_ring(block["outline"]["vertices"], 2)
    # Rotating the outline re-indexes the walls; drop them so the block stays valid and
    # the property under test (area is order-independent) is isolated.
    block["exterior_walls"] = []
    rotated = derive_proposal(block, _lot_context(fixture["lot"]))
    assert rotated.footprint_area.value == base_result.footprint_area.value


def _translate(value, dx: float, dy: float):
    if isinstance(value, list) and len(value) == 2 and all(
        isinstance(c, (int, float)) for c in value
    ):
        return [value[0] + dx, value[1] + dy]
    if isinstance(value, list):
        return [_translate(v, dx, dy) for v in value]
    if isinstance(value, dict):
        return {k: _translate(v, dx, dy) for k, v in value.items()}
    return value


@pytest.mark.parametrize("name", ["rectangle_100x80", "wall_setback"])
def test_translation_preserves_area_coverage_and_setbacks(name: str) -> None:
    fixture = _load_fixture(name)
    base = derive_proposal(fixture["proposed_massing"], _lot_context(fixture["lot"]))
    dx, dy = 3000.0, -4000.0  # stays inside the NYC 2263 unit-sanity bounds
    moved_block = _translate(copy.deepcopy(fixture["proposed_massing"]), dx, dy)
    moved_lot = copy.deepcopy(fixture["lot"])
    moved_lot["lot_line_segments"] = _translate(moved_lot["lot_line_segments"], dx, dy)
    moved_lot["street_lines"] = [
        {**line, "start": _translate(line["start"], dx, dy), "end": _translate(line["end"], dx, dy)}
        for line in moved_lot["street_lines"]
    ]
    moved = derive_proposal(moved_block, _lot_context(moved_lot))

    assert moved.footprint_area.value == base.footprint_area.value
    assert moved.lot_coverage.value == base.lot_coverage.value
    for setback in base.wall_setbacks:
        moved_setback = _setback(moved, setback.wall_id)
        assert moved_setback.lot_line_setback.value == setback.lot_line_setback.value
        assert moved_setback.street_line_setback.value == setback.street_line_setback.value


# ---------------------------------------------------------------------------
# AS-6 / AS-7: fail-closed on degeneracy; purity of inputs
# ---------------------------------------------------------------------------


def _valid_block() -> dict:
    return copy.deepcopy(_load_fixture("rectangle_100x80")["proposed_massing"])


def _valid_lot() -> LotContext:
    return _lot_context(_load_fixture("rectangle_100x80")["lot"])


def test_non_positive_lot_area_refused_typed() -> None:
    lot = dataclasses.replace(_valid_lot(), area_sq_ft=0.0)
    with pytest.raises(ProposalDerivationError) as exc:
        derive_proposal(_valid_block(), lot)
    assert exc.value.field == "lot.area_sq_ft"


def test_non_finite_lot_area_refused_typed() -> None:
    lot = dataclasses.replace(_valid_lot(), area_sq_ft=float("inf"))
    with pytest.raises(ProposalDerivationError) as exc:
        derive_proposal(_valid_block(), lot)
    assert exc.value.field == "lot.area_sq_ft"


def test_collapsed_outline_refused_via_validation() -> None:
    block = _valid_block()
    # A bowtie self-intersection: the B0 validator refuses it before any derivation.
    block["outline"]["vertices"] = [
        [1000000.0, 200000.0],
        [1000010.0, 200010.0],
        [1000010.0, 200000.0],
        [1000000.0, 200010.0],
        [1000000.0, 200000.0],
    ]
    with pytest.raises(ProposedMassingError) as exc:
        derive_proposal(block, _valid_lot())
    assert exc.value.field == "proposed_massing.outline"


def test_degenerate_closing_vertex_wall_refused_via_validation() -> None:
    block = _valid_block()
    # DB-034(c): index 4 is the repeated closing vertex (== index 0); a wall 0->4 is a
    # zero-length wall the B0 validator refuses before derivation runs.
    block["exterior_walls"] = [
        {"id": "degenerate", "start_vertex_index": 0, "end_vertex_index": 4}
    ]
    with pytest.raises(ProposedMassingError) as exc:
        derive_proposal(block, _valid_lot())
    assert exc.value.field == "proposed_massing.exterior_walls[0]"


def test_lot_must_be_a_lot_context() -> None:
    with pytest.raises(ProposalDerivationError) as exc:
        derive_proposal(_valid_block(), {"area_sq_ft": 16000.0})  # type: ignore[arg-type]
    assert exc.value.field == "lot"


def test_missing_per_level_outline_falls_back_to_base_explicitly() -> None:
    # A level with no own outline is NOT an error: it falls back to the base outline and
    # records the choice EXPLICITLY (never a silent guess).
    result, _ = _derive_fixture("rectangle_100x80")
    for level in result.per_level_areas:
        assert level.outline_source == "base_outline"
        assert level.evidence.value == result.footprint_area.value


def test_empty_lot_lines_gives_typed_absence_not_a_guess() -> None:
    lot = dataclasses.replace(_valid_lot(), lot_line_segments=())
    result = derive_proposal(_valid_block(), lot)
    for setback in result.wall_setbacks:
        assert setback.lot_line_setback.value is None
        assert setback.lot_line_setback.method == "lot_line_setback_absent"


def test_input_block_is_not_mutated() -> None:
    block = _valid_block()
    snapshot = copy.deepcopy(block)
    derive_proposal(block, _valid_lot())
    assert block == snapshot


def test_result_is_frozen() -> None:
    result, _ = _derive_fixture("rectangle_100x80")
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.footprint_area = None  # type: ignore[misc]
