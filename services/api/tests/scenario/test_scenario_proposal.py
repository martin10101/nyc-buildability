"""Unit acceptance pack for :mod:`app.scenario.proposal` (task M5-T048, phase B0).

These tests exercise the SEMANTIC validator ``validate_proposed_massing`` that
owns the semantic invariants - some a JSON Schema cannot express, others it
could but which are enforced here by design (see the split below).

STRUCTURAL vs SEMANTIC validation (documented distinction, AS-3/AS-4):

* The JSON Schema (``scenario.schema.json`` ``proposed_massing`` $def) fixes the
  STRUCTURAL shape - key presence, object/array types, the ``srid`` enum
  ``[2263]``, the ``kind`` enum ``["proposed"]``, and ``additionalProperties:
  false``. A defect the schema can express (wrong srid, kind != 'proposed',
  a missing required key, an extra key) fails schema validation.
* This module owns the SEMANTIC invariants, of two kinds:
  - (B) invariants a JSON Schema CANNOT state, which REQUIRE cross-value /
    geometry validation: ring closure (first == last), non-self-intersection,
    distinct non-closing vertices, level-index contiguity {0..N-1} (a set tied
    to the array length), and wall start/end indices in range of the outline
    vertex count and distinct (a cross-field reference);
  - (A) invariants a JSON Schema COULD express but which this module enforces BY
    DESIGN so each refusal is a typed field-named error and the numeric bounds
    live once as constants: NYC EPSG:2263 per-coordinate bounds (schema
    prefixItems + minimum/maximum), the sane floor-to-floor upper bound (schema
    maximum), and the DB-013 count ceilings (schema maxItems / maximum).
  Strict positivity of ``floor_to_floor_ft`` IS already expressed in the schema
  (``exclusiveMinimum: 0`` on proposed_level.floor_to_floor_ft) and re-checked
  here as defense in depth. Height finiteness is neither: no real JSON document
  can carry NaN/Infinity, so the schema never sees it; this module's finiteness
  check guards in-memory floats. Each failure is a TYPED ``ProposedMassingError``
  naming the exact ``field``. A document carrying a (B) defect is STRUCTURALLY
  schema-valid but SEMANTICALLY refused (see the fixtures + contract tests).

A proposed building is a THIRD input class - never a city record, never a rule
(D-076-R002): nothing here computes or implies an allowance.
"""

from __future__ import annotations

import copy
import math

import pytest

from app.scenario.proposal import (
    MAX_EXTERIOR_WALLS,
    MAX_FLOOR_COUNT,
    MAX_FLOOR_TO_FLOOR_FT,
    MAX_LEVELS,
    MAX_OUTLINE_VERTICES,
    ProposedMassingError,
    validate_proposed_massing,
)

# A base X/Y comfortably inside the NYC EPSG:2263 unit-sanity bounds.
_X0 = 1000000.0
_Y0 = 200000.0


def _valid_block() -> dict:
    """A minimal, fully-valid proposed_massing block (fresh copy each call)."""
    return {
        "outline": {
            "srid": 2263,
            "vertices": [
                [_X0, _Y0],
                [_X0 + 100.0, _Y0],
                [_X0 + 100.0, _Y0 + 80.0],
                [_X0, _Y0 + 80.0],
                [_X0, _Y0],
            ],
        },
        "levels": [
            {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0},
            {"level_index": 1, "floor_count": 3, "floor_to_floor_ft": 10.5},
        ],
        "exterior_walls": [
            {"id": "south", "start_vertex_index": 0, "end_vertex_index": 1},
            {"id": "east", "start_vertex_index": 1, "end_vertex_index": 2},
        ],
        "provenance": {
            "author": "architect@example.com",
            "kind": "proposed",
            "editor_version": "proposal-editor/0.1.0",
            "parent_scenario_id": None,
        },
    }


def _convex_ring(n_distinct: int) -> list[list[float]]:
    """An explicitly-closed convex (hence simple) ring of ``n_distinct`` distinct
    vertices on a small circle inside the NYC bounds, plus the closing vertex."""
    cx, cy, r = _X0, _Y0, 50.0
    pts = [
        [cx + r * math.cos(2.0 * math.pi * k / n_distinct),
         cy + r * math.sin(2.0 * math.pi * k / n_distinct)]
        for k in range(n_distinct)
    ]
    pts.append([pts[0][0], pts[0][1]])
    return pts


# ---------------------------------------------------------------------------
# Valid blocks
# ---------------------------------------------------------------------------


def test_valid_block_returns_none() -> None:
    assert validate_proposed_massing(_valid_block()) is None


def test_valid_block_with_null_parent_scenario_id() -> None:
    block = _valid_block()
    block["provenance"]["parent_scenario_id"] = None
    assert validate_proposed_massing(block) is None


def test_valid_block_with_present_parent_scenario_id() -> None:
    block = _valid_block()
    block["provenance"]["parent_scenario_id"] = "scenario-123"
    assert validate_proposed_massing(block) is None


def test_valid_block_absent_optional_parent_scenario_id() -> None:
    block = _valid_block()
    block["provenance"].pop("parent_scenario_id")
    assert validate_proposed_massing(block) is None


def test_valid_block_with_differing_per_level_outline() -> None:
    block = _valid_block()
    # A smaller, still-valid closed simple square for the upper level.
    block["levels"][1]["outline"] = {
        "srid": 2263,
        "vertices": [
            [_X0 + 10.0, _Y0 + 10.0],
            [_X0 + 60.0, _Y0 + 10.0],
            [_X0 + 60.0, _Y0 + 60.0],
            [_X0 + 10.0, _Y0 + 60.0],
            [_X0 + 10.0, _Y0 + 10.0],
        ],
    }
    assert validate_proposed_massing(block) is None


def test_valid_block_null_per_level_outline_ok() -> None:
    block = _valid_block()
    block["levels"][0]["outline"] = None
    assert validate_proposed_massing(block) is None


def test_valid_minimal_triangle_outline() -> None:
    block = _valid_block()
    block["outline"]["vertices"] = [
        [_X0, _Y0],
        [_X0 + 100.0, _Y0],
        [_X0 + 50.0, _Y0 + 90.0],
        [_X0, _Y0],
    ]
    assert validate_proposed_massing(block) is None


# ---------------------------------------------------------------------------
# Block-level structural refusals
# ---------------------------------------------------------------------------


def test_block_not_a_dict_refused() -> None:
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(["not", "a", "dict"])
    assert exc.value.field == "proposed_massing"


def test_missing_outline_refused() -> None:
    block = _valid_block()
    del block["outline"]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline"


# ---------------------------------------------------------------------------
# Outline / geometry (semantic)
# ---------------------------------------------------------------------------


def test_wrong_srid_refused() -> None:
    block = _valid_block()
    block["outline"]["srid"] = 4326
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline.srid"


def test_open_ring_refused() -> None:
    block = _valid_block()
    block["outline"]["vertices"] = [
        [_X0, _Y0],
        [_X0 + 100.0, _Y0],
        [_X0 + 100.0, _Y0 + 80.0],
        [_X0, _Y0 + 80.0],
    ]  # NOT closed: first != last
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline"
    assert "not closed" in str(exc.value)


def test_self_intersecting_outline_refused() -> None:
    block = _valid_block()
    # A bowtie: edges (0-1) and (2-3) cross.
    block["outline"]["vertices"] = [
        [_X0, _Y0],
        [_X0 + 10.0, _Y0 + 10.0],
        [_X0 + 10.0, _Y0],
        [_X0, _Y0 + 10.0],
        [_X0, _Y0],
    ]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline"
    assert "self-intersecting" in str(exc.value)


def test_too_few_positions_refused() -> None:
    block = _valid_block()
    block["outline"]["vertices"] = [[_X0, _Y0], [_X0 + 10.0, _Y0], [_X0, _Y0]]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline.vertices"


def test_duplicate_non_closing_vertex_refused() -> None:
    block = _valid_block()
    block["outline"]["vertices"] = [
        [_X0, _Y0],
        [_X0 + 100.0, _Y0],
        [_X0 + 100.0, _Y0],  # duplicate of the previous, not the closing vertex
        [_X0, _Y0 + 80.0],
        [_X0, _Y0],
    ]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline"


def test_vertex_not_a_pair_refused() -> None:
    block = _valid_block()
    block["outline"]["vertices"][1] = [_X0 + 100.0, _Y0, 0.0]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline.vertices[1]"


def test_vertex_non_finite_refused() -> None:
    block = _valid_block()
    block["outline"]["vertices"][1] = [float("inf"), _Y0]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline.vertices[1]"


def test_vertex_boolean_is_not_a_number() -> None:
    block = _valid_block()
    block["outline"]["vertices"][1] = [True, _Y0]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline.vertices[1]"


def test_vertex_out_of_nyc_bounds_refused() -> None:
    block = _valid_block()
    # A 4326-style longitude/latitude pair - the classic wrong-CRS mistake.
    block["outline"]["vertices"][1] = [-73.98, 40.75]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline.vertices[1]"
    assert "NYC" in str(exc.value)


# ---------------------------------------------------------------------------
# Levels: consistency (count matches records) + heights
# ---------------------------------------------------------------------------


def test_empty_levels_refused() -> None:
    block = _valid_block()
    block["levels"] = []
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels"


def test_level_index_gap_refused() -> None:
    block = _valid_block()
    block["levels"][1]["level_index"] = 3  # {0, 3} with 2 records -> not {0, 1}
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels"
    assert "contiguous" in str(exc.value)


def test_level_index_duplicate_refused() -> None:
    block = _valid_block()
    block["levels"][1]["level_index"] = 0  # {0, 0}
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels"


def test_single_level_index_must_be_zero() -> None:
    block = _valid_block()
    block["levels"] = [{"level_index": 1, "floor_count": 1, "floor_to_floor_ft": 12.0}]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels"


def test_level_count_matches_records_when_contiguous() -> None:
    # Three records with indices {0,1,2} is accepted: the count matches the
    # contiguous index range exactly.
    block = _valid_block()
    block["levels"] = [
        {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0},
        {"level_index": 2, "floor_count": 1, "floor_to_floor_ft": 10.0},
        {"level_index": 1, "floor_count": 1, "floor_to_floor_ft": 10.0},
    ]
    assert validate_proposed_massing(block) is None


def test_level_index_non_integer_refused() -> None:
    block = _valid_block()
    block["levels"][0]["level_index"] = 0.0
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].level_index"


def test_floor_count_zero_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_count"] = 0
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_count"


def test_floor_count_non_integer_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_count"] = 2.5
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_count"


def test_negative_height_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_to_floor_ft"] = -10.0
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_to_floor_ft"
    assert "strictly positive" in str(exc.value)


def test_zero_height_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_to_floor_ft"] = 0.0
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_to_floor_ft"


def test_non_finite_height_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_to_floor_ft"] = float("inf")
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_to_floor_ft"
    assert "finite" in str(exc.value)


def test_nan_height_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_to_floor_ft"] = float("nan")
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_to_floor_ft"


def test_height_over_bound_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_to_floor_ft"] = MAX_FLOOR_TO_FLOOR_FT + 1.0
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_to_floor_ft"


def test_height_at_bound_ok() -> None:
    block = _valid_block()
    block["levels"][0]["floor_to_floor_ft"] = MAX_FLOOR_TO_FLOOR_FT
    assert validate_proposed_massing(block) is None


def test_invalid_per_level_outline_refused() -> None:
    block = _valid_block()
    block["levels"][1]["outline"] = {
        "srid": 2263,
        "vertices": [
            [_X0, _Y0],
            [_X0 + 10.0, _Y0],
            [_X0 + 10.0, _Y0 + 10.0],
            [_X0, _Y0 + 10.0],
        ],  # open ring
    }
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[1].outline"


# ---------------------------------------------------------------------------
# Exterior walls
# ---------------------------------------------------------------------------


def test_wall_index_out_of_range_refused() -> None:
    block = _valid_block()
    block["exterior_walls"][0]["end_vertex_index"] = 99
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.exterior_walls[0].end_vertex_index"


def test_wall_start_equals_end_refused() -> None:
    block = _valid_block()
    block["exterior_walls"][0]["end_vertex_index"] = 0
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.exterior_walls[0]"


def test_wall_empty_id_refused() -> None:
    block = _valid_block()
    block["exterior_walls"][0]["id"] = "   "
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.exterior_walls[0].id"


def test_wall_duplicate_id_refused() -> None:
    block = _valid_block()
    block["exterior_walls"][1]["id"] = "south"  # collides with wall 0
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.exterior_walls[1].id"


def test_wall_index_non_integer_refused() -> None:
    block = _valid_block()
    block["exterior_walls"][0]["start_vertex_index"] = "0"
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.exterior_walls[0].start_vertex_index"


def test_empty_wall_list_ok() -> None:
    block = _valid_block()
    block["exterior_walls"] = []
    assert validate_proposed_massing(block) is None


# ---------------------------------------------------------------------------
# Provenance (third-input-class honesty, D-076-R002)
# ---------------------------------------------------------------------------


def test_provenance_kind_must_be_proposed() -> None:
    block = _valid_block()
    block["provenance"]["kind"] = "record"
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.provenance.kind"
    assert "proposed" in str(exc.value)


def test_provenance_missing_author_refused() -> None:
    block = _valid_block()
    block["provenance"]["author"] = ""
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.provenance.author"


def test_provenance_parent_scenario_id_wrong_type_refused() -> None:
    block = _valid_block()
    block["provenance"]["parent_scenario_id"] = 42
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.provenance.parent_scenario_id"


# ---------------------------------------------------------------------------
# DB-013 bounded ceilings: tests at the ceiling and one past it (AS-5)
# ---------------------------------------------------------------------------


def test_outline_vertices_at_ceiling_ok() -> None:
    block = _valid_block()
    block["outline"]["vertices"] = _convex_ring(MAX_OUTLINE_VERTICES - 1)
    assert len(block["outline"]["vertices"]) == MAX_OUTLINE_VERTICES
    # Walls reference only the low indices, which stay in range.
    assert validate_proposed_massing(block) is None


def test_outline_vertices_over_ceiling_refused() -> None:
    block = _valid_block()
    block["outline"]["vertices"] = [[_X0, _Y0] for _ in range(MAX_OUTLINE_VERTICES + 1)]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.outline.vertices"
    assert "MAX_OUTLINE_VERTICES" in str(exc.value)


def test_levels_at_ceiling_ok() -> None:
    block = _valid_block()
    block["levels"] = [
        {"level_index": i, "floor_count": 1, "floor_to_floor_ft": 10.0}
        for i in range(MAX_LEVELS)
    ]
    assert validate_proposed_massing(block) is None


def test_levels_over_ceiling_refused() -> None:
    block = _valid_block()
    block["levels"] = [
        {"level_index": i, "floor_count": 1, "floor_to_floor_ft": 10.0}
        for i in range(MAX_LEVELS + 1)
    ]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels"
    assert "MAX_LEVELS" in str(exc.value)


def test_floor_count_at_ceiling_ok() -> None:
    block = _valid_block()
    block["levels"][0]["floor_count"] = MAX_FLOOR_COUNT
    assert validate_proposed_massing(block) is None


def test_floor_count_over_ceiling_refused() -> None:
    block = _valid_block()
    block["levels"][0]["floor_count"] = MAX_FLOOR_COUNT + 1
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.levels[0].floor_count"
    assert "MAX_FLOOR_COUNT" in str(exc.value)


def test_exterior_walls_at_ceiling_ok() -> None:
    block = _valid_block()
    block["exterior_walls"] = [
        {"id": f"w{i}", "start_vertex_index": 0, "end_vertex_index": 1}
        for i in range(MAX_EXTERIOR_WALLS)
    ]
    assert validate_proposed_massing(block) is None


def test_exterior_walls_over_ceiling_refused() -> None:
    block = _valid_block()
    block["exterior_walls"] = [
        {"id": f"w{i}", "start_vertex_index": 0, "end_vertex_index": 1}
        for i in range(MAX_EXTERIOR_WALLS + 1)
    ]
    with pytest.raises(ProposedMassingError) as exc:
        validate_proposed_massing(block)
    assert exc.value.field == "proposed_massing.exterior_walls"
    assert "MAX_EXTERIOR_WALLS" in str(exc.value)


# ---------------------------------------------------------------------------
# Third-input-class honesty (D-076-R002): the module derives nothing
# ---------------------------------------------------------------------------


def test_validator_returns_none_never_a_value() -> None:
    """The validator only accepts or refuses; it never returns a derived
    allowance, area, coverage, or FAR (that is phase B1/B2)."""
    block = _valid_block()
    result = validate_proposed_massing(block)
    assert result is None


def test_input_block_is_not_mutated() -> None:
    block = _valid_block()
    snapshot = copy.deepcopy(block)
    validate_proposed_massing(block)
    assert block == snapshot
