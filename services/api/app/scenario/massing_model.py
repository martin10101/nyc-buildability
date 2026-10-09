"""M5-T082 (D-087 3D-1): the deterministic massing truth object - compatibility facade.

The canonical scenario-geometry object of ``docs/3D_MASSING_ENGINE_ARCHITECTURE.md``
(sections 2-4 and 10, subset). It is the SERVER-SIDE truth every 3D view and the CAD
export consume; a renderer draws it and never invents it (section 2). Nothing here is a
rule and nothing is a city record.

M5-T112 (DB-079 a) split this 994-line module along its responsibilities, BEHIND THIS
COMPATIBILITY FACADE - every public name :mod:`app.scenario.scene_assembler` and the tests
import keeps working from here unchanged:

* :mod:`app.scenario.massing_guards` - the fail-closed input boundary: the typed
  :class:`MassingModelError`, bounded caller-input echoes, the finiteness / magnitude
  predicates, the NYC EPSG:2263 range guard, the shapely geometry-engine wrap, and the
  DB-079 (b) overflow-field locator;
* :mod:`app.scenario.massing_triangulation` - ring preparation and the concave-safe
  ear-clipping triangulator with its work budget (its ``triangulate_polygon`` is the ONE
  public reusable API the later GLB export fix, DB-082 a, consumes);
* :mod:`app.scenario.massing_mesh` - prism / plate / mesh construction.

This module keeps the builder orchestration and the truth object: it validates the lot
ring and the B0 ``proposed_massing`` block (read-only through :mod:`app.scenario.proposal`),
expands the floor stack, triangulates each distinct outline once under one shared work
budget, meshes a prism per floor, and assembles the versioned truth object with its
declared EPSG:2263 coordinate frame, per-floor plates, metrics and provenance.

Honesty (D-076-R002 / D-083 vocabulary): a building derived from an architect proposal is
``proposed`` ("Proposed - not a city record"); one derived from the max-envelope generator
is a ``generated_option`` ("Generated building option"). No output is ever labelled a city
record, a rule, or an achievable / legal value, and no legal conclusion is drawn.

The only intended behaviour change in the M5-T112 split is DB-079 (b): the B0
``OverflowError`` arm now names the level outline when the out-of-float-range value sits
there, not the blanket ``proposed_massing.outline``. Every valid-input output is
byte-identical. Deterministic and offline: standard library + the admitted ``shapely`` /
``numpy``; no network, no new dependency, no route, no web. ``content_hash`` pins a golden
sha256.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from shapely.geometry import Polygon

from .massing_guards import MAX_COORD_ABS as MAX_COORD_ABS
from .massing_guards import MAX_ECHO_CHARS as MAX_ECHO_CHARS
from .massing_guards import NYC_2263_X_MAX as NYC_2263_X_MAX
from .massing_guards import NYC_2263_X_MIN as NYC_2263_X_MIN
from .massing_guards import NYC_2263_Y_MAX as NYC_2263_Y_MAX
from .massing_guards import NYC_2263_Y_MIN as NYC_2263_Y_MIN
from .massing_guards import (
    MassingModelError,
    _is_finite_number,
    _locate_overflow_field,
    _Point,
    _preview,
    _wrap_geos_errors,
)
from .massing_mesh import _build_prism, _PrismMesh
from .massing_triangulation import (
    _QUANT_DECIMALS,
    MAX_TRIANGULATION_WORK,
    _min_ear_clip_work,
    _prepare_ring,
    _q,
    _triangulate,
    _WorkBudget,
)
from .massing_triangulation import _cross3 as _cross3
from .massing_triangulation import _point_in_triangle as _point_in_triangle
from .massing_triangulation import _signed_area as _signed_area
from .proposal import MAX_OUTLINE_VERTICES as MAX_OUTLINE_VERTICES
from .proposal import (
    ProposedMassingError,
    validate_proposed_massing,
)

__all__ = [
    "MassingModelError",
    "MassingModel",
    "build_massing_model",
    "build_from_generated_option",
    "GENERATOR_VERSION",
    "GEOMETRY_VERSION",
    "SOURCE_PROPOSED",
    "SOURCE_GENERATED_OPTION",
]

# --- versioning -----------------------------------------------------------
GENERATOR_VERSION = "massing-1.0.0"
GEOMETRY_VERSION = 1

# --- declared coordinate frame (section 3) --------------------------------
CRS_CODE = "EPSG:2263"
CRS_AUTHORITY = "EPSG:2263 (NAD83 / New York Long Island, US survey feet)"
HORIZONTAL_UNIT = "us_survey_foot"
VERTICAL_UNIT = "us_survey_foot"
AXIS_ORDER = "easting_northing"  # x = easting, y = northing
#: The grid a renderer should snap to; emitted coordinates are quantised to it so
#: the golden serialization is stable. Metadata, never a legal precision claim.
PRECISION_GRID_FT = 1e-6

# --- source labels (the ONLY building labels; honesty vocabulary) ---------
SOURCE_PROPOSED = "proposed"
SOURCE_GENERATED_OPTION = "generated_option"
LAYER_PARCEL = "parcel"
_LAYER_FOR_SOURCE = {
    SOURCE_PROPOSED: "proposed_massing",
    SOURCE_GENERATED_OPTION: "generated_option",
}
_DISCLOSURE_FOR_SOURCE = {
    SOURCE_PROPOSED: "Proposed - not a city record",
    SOURCE_GENERATED_OPTION: "Generated building option",
}

# --- fail-closed ceilings (resource bounds, never legal values) ------------
#: Total expanded floors across the stack (a paste / generation error above this).
MAX_TOTAL_FLOORS = 2000
#: A footprint may sit at most this far outside the lot line (survey noise) before
#: it is refused ``footprint_outside_lot``. It is NEVER clipped to fit.
FOOTPRINT_OUTSIDE_LOT_TOL_FT = 1e-6
#: Total emitted mesh vertices (2 x ring size per floor band) - bounds the payload a
#: viewer / exporter receives (~6.5 MB of JSON at the ceiling).
MAX_TOTAL_MESH_VERTICES = 100_000


# ---------------------------------------------------------------------------
# Provenance digests.
# ---------------------------------------------------------------------------


def _digest(payload: Any) -> str:
    """A deterministic sha256 over a canonical JSON encoding of ``payload``."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# The truth object.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MassingModel:
    """The versioned scenario-geometry truth object (section 2). Renderer-agnostic
    JSON; a viewer draws it and never becomes its source."""

    source: str
    disclosure: str
    coordinate_reference_system: dict
    parcel: dict
    building_layer: dict
    meshes: tuple[_PrismMesh, ...]
    plates: tuple[dict, ...]
    metrics: dict
    provenance: dict

    def as_dict(self) -> dict:
        return {
            "generator_version": GENERATOR_VERSION,
            "geometry_version": GEOMETRY_VERSION,
            "source": self.source,
            "disclosure": self.disclosure,
            "coverage_status": "conditional",
            "coordinate_reference_system": self.coordinate_reference_system,
            "layers": [LAYER_PARCEL, self.building_layer["layer"]],
            "parcel": self.parcel,
            "building_layer": self.building_layer,
            "meshes": [m.as_dict() for m in self.meshes],
            "plates": [dict(p) for p in self.plates],
            "metrics": self.metrics,
            "provenance": self.provenance,
        }

    def to_json(self) -> str:
        """Deterministic, strict (no NaN/Infinity) JSON encoding."""
        return json.dumps(
            self.as_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )

    def content_hash(self) -> str:
        """A golden sha256 over :meth:`to_json` - stable for identical inputs."""
        return "sha256:" + hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Floor-stack adapter (B0 levels -> expanded per-floor bands).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Floor:
    floor_index: int
    level_index: int
    height_ft: float
    z_bottom: float
    z_top: float
    ring: tuple[_Point, ...]  # the prepared ring; also its content-dedupe key
    ring_field: str


def _check_floor_cap(levels: Sequence[Any]) -> None:
    """Refuse an over-tall stack from the B0 level counts alone, BEFORE any ring is
    prepared, triangulated or meshed (``over_cap_floors``)."""
    total = sum(
        lvl.get("floor_count", 0) for lvl in levels
        if isinstance(lvl, Mapping) and isinstance(lvl.get("floor_count"), int)
    )
    if total > MAX_TOTAL_FLOORS:
        raise MassingModelError(
            f"the floor stack has {total} floors, over the cap of {MAX_TOTAL_FLOORS} "
            "floors", reason="over_cap_floors", field="proposed_massing.levels")


def _expand_floor_stack(
    block: Mapping[str, Any], default_ring: tuple[_Point, ...]
) -> list[_Floor]:
    """Adapter: expand the B0 ``levels`` (each ``floor_count`` identical floors of
    ``floor_to_floor_ft``) into an explicit per-floor band stack, stacking z from 0.

    The B0 contract DOES carry per-floor heights this way, so no separate floor-stack
    input is needed. A level may carry its own ``outline`` (a setback / tower band);
    that footprint is prepared for its floors (identical content shares one ring),
    else the top-level footprint is reused. No triangulation happens here. Fails
    closed on a non-positive height or an empty stack."""
    levels = block.get("levels")
    if not isinstance(levels, list) or not levels:
        raise MassingModelError("proposed_massing.levels must be a non-empty array",
                                reason="invalid_source", field="proposed_massing.levels")

    field_by_ring: dict[tuple[_Point, ...], str] = {
        default_ring: "proposed_massing.outline"}
    floors: list[_Floor] = []
    z = 0.0
    floor_index = 0
    for lvl in sorted(levels, key=lambda item: item.get("level_index", 0)):
        level_index = lvl.get("level_index", 0)
        height = lvl.get("floor_to_floor_ft")
        count = lvl.get("floor_count")
        if not _is_finite_number(height) or height <= 0:
            raise MassingModelError(
                f"level {level_index} floor_to_floor_ft must be finite and > 0; "
                f"got {_preview(height)}",
                reason="non_positive_height",
                field=f"proposed_massing.levels[{level_index}].floor_to_floor_ft")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise MassingModelError(
                f"level {level_index} floor_count must be an integer >= 1; "
                f"got {_preview(count)}",
                reason="invalid_source",
                field=f"proposed_massing.levels[{level_index}].floor_count")

        ring = default_ring
        if lvl.get("outline") is not None:
            ring = tuple(_prepare_ring(
                lvl["outline"].get("vertices", []),
                f"proposed_massing.levels[{level_index}].outline.vertices"))
            field_by_ring.setdefault(
                ring, f"proposed_massing.levels[{level_index}].outline")
        ring_field = field_by_ring[ring]

        for _ in range(count):
            floors.append(_Floor(
                floor_index=floor_index, level_index=level_index,
                height_ft=_q(height), z_bottom=_q(z), z_top=_q(z + height),
                ring=ring, ring_field=ring_field))
            z += height
            floor_index += 1
    return floors


def _check_output_size(floors: Sequence[_Floor]) -> None:
    """Refuse an over-large mesh from ring sizes alone, BEFORE any triangulation or
    prism is built (``over_cap_output_vertices``).

    This total INTENTIONALLY does not content-dedupe (DB-061 f / G3-A3): every floor
    emits its OWN prism, so two floors sharing an identical outline still produce two
    prisms and thus ``2 * (2 * ring)`` output vertices. :func:`_triangulate_distinct`
    dedupes the triangulation WORK (a distinct ring is triangulated once), but the
    emitted vertex COUNT is per floor. Never 'optimize' this sum into a
    per-distinct-ring figure: it would under-count the real payload a viewer/exporter
    receives and let the ceiling be bypassed."""
    total = sum(2 * len(floor.ring) for floor in floors)
    if total > MAX_TOTAL_MESH_VERTICES:
        raise MassingModelError(
            f"the massing would emit {total} mesh vertices, over the cap of "
            f"{MAX_TOTAL_MESH_VERTICES}", reason="over_cap_output_vertices",
            field="proposed_massing.levels")


def _triangulate_distinct(
    floors: Sequence[_Floor],
) -> dict[tuple[_Point, ...], list[tuple[int, int, int]]]:
    """Triangulate each DISTINCT ring once under ONE shared per-request budget.
    Refuses up front when the least possible work (:func:`_min_ear_clip_work`) of the
    distinct rings already exceeds :data:`MAX_TRIANGULATION_WORK`."""
    distinct: dict[tuple[_Point, ...], str] = {}
    for floor in floors:
        distinct.setdefault(floor.ring, floor.ring_field)
    least = sum(_min_ear_clip_work(len(ring)) for ring in distinct)
    if least > MAX_TRIANGULATION_WORK:
        raise MassingModelError(
            f"triangulating {len(distinct)} distinct outline(s) needs at least {least} "
            f"work units, over the budget of {MAX_TRIANGULATION_WORK}",
            reason="triangulation_budget_exceeded", field="proposed_massing.levels")
    budget = _WorkBudget(MAX_TRIANGULATION_WORK)
    return {ring: _triangulate(ring, field, budget) for ring, field in distinct.items()}


# ---------------------------------------------------------------------------
# Lot ring + coordinate frame.
# ---------------------------------------------------------------------------


def _lot_polygon(lot_ring: Sequence[Sequence[float]]) -> tuple[Polygon, list[_Point]]:
    """Validate the canonical lot ring and return its shapely polygon + prepared ring.
    Refuses a self-intersecting or self-touching lot, and a lot outside the NYC
    EPSG:2263 range (a wrong-unit / wrong-CRS mistake, ``lot_ring_out_of_nyc_bounds``).

    The lot is the ONE ring B0 never validates, so :func:`_prepare_ring` is called with
    ``nyc_range_check=True``: it range-checks the RAW vertices in its parse loop, BEFORE
    the collinear collapse (DB-069 a), reusing the very :data:`NYC_2263_X_MIN` ..
    constants B0 applies to the proposal footprint (single source of truth) and naming
    ``lot_ring`` so the refusal points at the real culprit. These are generous
    fail-closed unit guards, never a precise city boundary. One ring cannot carry a
    hole: a keyhole ring that pinches one off by revisiting a vertex is refused
    ``self_intersection`` in :func:`_prepare_ring`."""
    ring = _prepare_ring(lot_ring, "lot_ring", nyc_range_check=True)
    poly = Polygon([(x, y) for x, y in ring])
    if poly.interiors:  # defensive: unreachable from one ring (DB-054 f)
        raise MassingModelError("lot_ring encloses a hole; a massing lot must be a "
                                "single simple ring", reason="lot_has_holes",
                                field="lot_ring")
    if not poly.is_valid:
        raise MassingModelError("lot_ring is not a valid simple polygon",
                                reason="self_intersection", field="lot_ring")
    return poly, ring


def _local_origin(lot_ring: Sequence[_Point]) -> _Point:
    """A stable local origin near the parcel centroid (section 3, step 1)."""
    centroid = Polygon([(x, y) for x, y in lot_ring]).centroid
    return (_q(centroid.x), _q(centroid.y))


def _crs_frame(origin: _Point) -> dict:
    """The declared coordinate frame with the exact world->local transform (section 3)."""
    ox, oy = origin
    return {
        "crs": CRS_CODE,
        "authority": CRS_AUTHORITY,
        "horizontal_unit": HORIZONTAL_UNIT,
        "vertical_unit": VERTICAL_UNIT,
        "axis_order": AXIS_ORDER,
        "storage": "authoritative_world_2263",
        "local_origin": [ox, oy, 0.0],
        "world_to_local": {
            "operation": "subtract_local_origin",
            "offset": [-ox, -oy, 0.0],
        },
        "precision_grid_ft": PRECISION_GRID_FT,
    }


# ---------------------------------------------------------------------------
# Builders.
# ---------------------------------------------------------------------------


@_wrap_geos_errors
def build_massing_model(
    *,
    lot_ring: Sequence[Sequence[float]],
    proposed_massing: Mapping[str, Any],
    source: str = SOURCE_PROPOSED,
    scenario_id: str | None = None,
    property_geometry_version_id: str | None = None,
    rule_release_id: str | None = None,
) -> MassingModel:
    """Build the massing truth object from a canonical 2263 lot ring and a B0
    ``proposed_massing`` block (validated read-only through :mod:`app.scenario.proposal`).

    ``source`` selects the honest building label (``proposed`` or ``generated_option``);
    the optional ids are carried through provenance verbatim. Every failure is a typed
    :class:`MassingModelError`; nothing is clipped or repaired."""
    if source not in _LAYER_FOR_SOURCE:
        raise MassingModelError(
            f"source must be one of {sorted(_LAYER_FOR_SOURCE)}; got {_preview(source)}",
            reason="invalid_source", field="source")

    # Fail-closed B0 validation of the proposed building (translated to a typed refusal).
    try:
        validate_proposed_massing(proposed_massing)
    except ProposedMassingError as exc:
        raise MassingModelError(
            f"proposed_massing failed B0 contract validation: {_preview(exc)}",
            reason="invalid_source", field=exc.field) from exc
    except OverflowError as exc:
        # A footprint or per-level outline coordinate beyond the finite float range (a
        # JSON integer literal such as 10**400) overflows B0's own finiteness check
        # (math.isfinite on a huge int raises OverflowError, NOT a ProposedMassingError).
        # Type it as the same non_finite refusal the lot path raises, so no untyped
        # OverflowError escapes the builder (DB-069 g / G5 MED-1), and name the REAL
        # outline the overflow sits in (DB-079 b): _locate_overflow_field walks B0's
        # order and returns proposed_massing.outline (footprint, unchanged) or
        # proposed_massing.levels[<pos>].outline (a level outline), never the blanket
        # footprint label for a level-outline overflow.
        raise MassingModelError(
            "proposed_massing carries a coordinate beyond the finite float range "
            "(a non-finite magnitude); it is refused, never truncated",
            reason="non_finite", field=_locate_overflow_field(proposed_massing)) from exc

    # Cheap bounds first: nothing below runs for an over-tall stack.
    _check_floor_cap(proposed_massing["levels"])
    lot_poly, lot_prepared = _lot_polygon(lot_ring)
    origin = _local_origin(lot_prepared)

    footprint_ring = tuple(_prepare_ring(
        proposed_massing["outline"].get("vertices", []),
        "proposed_massing.outline.vertices"))
    floors = _expand_floor_stack(proposed_massing, footprint_ring)
    _check_output_size(floors)

    # Fail-closed containment: every floor footprint within the lot (never clipped).
    lot_guard = lot_poly.buffer(FOOTPRINT_OUTSIDE_LOT_TOL_FT)
    checked: set[tuple[_Point, ...]] = set()
    for floor in floors:
        if floor.ring in checked:
            continue
        checked.add(floor.ring)
        floor_poly = Polygon([(x, y) for x, y in floor.ring])
        if not lot_guard.contains(floor_poly):
            raise MassingModelError(
                f"level {floor.level_index} footprint lies outside the lot beyond "
                f"{FOOTPRINT_OUTSIDE_LOT_TOL_FT} ft; it is refused, never clipped",
                reason="footprint_outside_lot",
                field=f"proposed_massing.levels[{floor.level_index}].outline")

    caps = _triangulate_distinct(floors)
    meshes = tuple(
        _build_prism(floor.ring, caps[floor.ring], floor.z_bottom, floor.z_top,
                     floor.floor_index, floor.level_index, origin)
        for floor in floors
    )

    plates = tuple({
        "floor_index": m.floor_index,
        "level_index": m.level_index,
        "elevation_ft": m.z_bottom_ft,
        "height_ft": round(m.z_top_ft - m.z_bottom_ft, _QUANT_DECIMALS),
        "area_sq_ft": m.plate_area_sq_ft,
    } for m in meshes)

    gross_floor_area = round(sum(p["area_sq_ft"] for p in plates), _QUANT_DECIMALS)
    total_height = round(sum(p["height_ft"] for p in plates), _QUANT_DECIMALS)

    parcel = {
        "layer": LAYER_PARCEL,
        "ring": [[x, y] for x, y in lot_prepared],
        "area_sq_ft": round(float(lot_poly.area), _QUANT_DECIMALS),
        "elevation_ft": 0.0,
    }
    building_layer = {
        "layer": _LAYER_FOR_SOURCE[source],
        "disclosure": _DISCLOSURE_FOR_SOURCE[source],
        "floor_count": len(floors),
    }

    provenance = {
        "generator_version": GENERATOR_VERSION,
        "source": source,
        "scenario_id": scenario_id,
        "property_geometry_version_id": property_geometry_version_id,
        "rule_release_id": rule_release_id,
        "input_digests": {
            "lot_ring": _digest([[x, y] for x, y in lot_prepared]),
            "proposed_massing": _digest(_canonical_block(proposed_massing)),
            "local_origin": _digest(list(origin)),
        },
        "proposal_provenance": _passthrough_provenance(proposed_massing),
    }

    return MassingModel(
        source=source,
        disclosure=_DISCLOSURE_FOR_SOURCE[source],
        coordinate_reference_system=_crs_frame(origin),
        parcel=parcel,
        building_layer=building_layer,
        meshes=meshes,
        plates=plates,
        metrics={
            "gross_floor_area_sq_ft": gross_floor_area,
            "total_height_ft": total_height,
            "floor_count": len(floors),
            "lot_area_sq_ft": parcel["area_sq_ft"],
        },
        provenance=provenance,
    )


def build_from_generated_option(
    *,
    lot_ring: Sequence[Sequence[float]],
    max_envelope: Mapping[str, Any],
    scenario_id: str | None = None,
    property_geometry_version_id: str | None = None,
    rule_release_id: str | None = None,
) -> MassingModel:
    """Build the truth object from a generated building option in the max-envelope
    engine's exact ``as_dict`` shape. The candidate is the engine's ``candidate`` field
    (a B0 ``proposed_massing`` draft); when it is ``None`` the engine emitted an explicit
    typed placement gap and no massing can be built - a typed refusal, never a fabricated
    building. The result is labelled ``generated_option`` ("Generated building option")."""
    if not isinstance(max_envelope, Mapping) or "candidate" not in max_envelope:
        raise MassingModelError(
            "max_envelope must be the engine's as_dict shape carrying a 'candidate' key",
            reason="invalid_source", field="max_envelope")
    candidate = max_envelope.get("candidate")
    if candidate is None:
        placement = max_envelope.get("candidate_placement") or {}
        detail = placement.get("detail") if isinstance(placement, Mapping) else None
        # The engine-sourced ``detail`` is length-bounded through _preview (DB-069 d
        # extension / G3 ADVISORY-1 A = G4 ADVISORY-2): a huge detail string cannot
        # amplify this refusal message.
        detail_preview = _preview(detail) if detail else ""
        raise MassingModelError(
            "max_envelope emitted no candidate footprint (an explicit typed placement "
            f"gap); no generated option can be built. {detail_preview}".strip(),
            reason="no_generated_candidate", field="max_envelope.candidate")
    return build_massing_model(
        lot_ring=lot_ring,
        proposed_massing=candidate,
        source=SOURCE_GENERATED_OPTION,
        scenario_id=scenario_id,
        property_geometry_version_id=property_geometry_version_id,
        rule_release_id=rule_release_id,
    )


def _canonical_block(block: Mapping[str, Any]) -> dict:
    """The digest-relevant subset of a proposed_massing block (outline + levels)."""
    return {
        "outline": block.get("outline"),
        "levels": block.get("levels"),
        "exterior_walls": block.get("exterior_walls"),
    }


def _passthrough_provenance(block: Mapping[str, Any]) -> dict:
    """Carry the proposal's own provenance through verbatim (author / editor_version /
    kind), so the truth object records where its footprint came from."""
    prov = block.get("provenance")
    if not isinstance(prov, Mapping):
        return {}
    return {
        "author": prov.get("author"),
        "editor_version": prov.get("editor_version"),
        "kind": prov.get("kind"),
        "parent_scenario_id": prov.get("parent_scenario_id"),
    }
