"""Deterministic proposal-fact derivation (task M5-T051, D-076 phase B1).

From a VALIDATED ``proposed_massing`` block (phase B0, :mod:`app.scenario.proposal`)
plus the lot's recorded EPSG:2263 geometry supplied by the CALLER, this module derives
the proposal's deterministic geometric FACTS - each carrying a full-provenance
:class:`EvidenceRecord`:

* **footprint area** (sf) - shoelace on the base 2263 outline;
* **lot coverage ratio** - footprint / the caller-supplied lot area, the lot-area
  provenance carried through verbatim;
* **per-level areas** (sf) - the level's own outline where present, else the base
  outline; which one was used is recorded EXPLICITLY, never a silent guess;
* **gross floor-area TREATMENT** - the sum of ``plate_area x floor_count`` over the
  levels, tagged with a DECLARED inclusions/exclusions vocabulary so a downstream
  reader sees exactly what the number is and is not;
* **wall setbacks** (ft) - for each named exterior wall, the minimum distance to the
  caller-supplied lot-line segments and, where the caller supplies an attested street
  line for that frontage, to that street line;
* **height per level and cumulative height** (ft) - ``floor_to_floor_ft x floor_count``.

THIRD-INPUT-CLASS honesty (D-076-R002). These are PROVIDED values (what the proposal
offers), NEVER allowances (what a rule permits or a code obliges). This module runs NO
rule evaluation, does NO requirement lookup, and emits NO "permitted / required /
allowed / compliant" vocabulary anywhere in its values, fields, or messages. The literal
``source_class`` on every record is :data:`SOURCE_CLASS` (``'proposed_derivation'``); it
is the FACT boundary the B2 rule engine consumes, never a rule result.

Purity and bounds (AS-7). The module is pure computation on its parameters: it imports
only the standard library (``math`` for geometry, ``hashlib`` + ``json`` for the
deterministic provenance digests) plus this package's own B0 validator; it performs NO
network, connector, or file I/O and fetches nothing. Every input arrives as a parameter -
the lot geometry and the street attestation are CALLER-SUPPLIED (the spatial stack and the
attested wide-street seam are consumed by the caller, never imported here). The bounded
ceilings of the validated block (DB-013) are inherited: the module never iterates beyond
the vertex / level / wall counts the B0 validator has already bounded.

Fail-closed (AS-6). Any geometric degeneracy is refused with a typed
:class:`ProposalDerivationError` naming the exact field, never guessed past; a street
setback with no attestation supplied is a TYPED honest absence (:class:`EvidenceRecord`
with ``value is None``), never a default distance. As defense in depth the block is
re-validated with :func:`app.scenario.proposal.validate_proposed_massing` on entry, so a
caller that skips validation still cannot drive a degenerate geometry into the arithmetic.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum

from .proposal import validate_proposed_massing

__all__ = [
    "SOURCE_CLASS",
    "GrossFloorAreaTreatment",
    "GROSS_FLOOR_AREA_INCLUSIONS",
    "GROSS_FLOOR_AREA_EXCLUSIONS",
    "StreetSetbackResolution",
    "ProposalDerivationError",
    "EvidenceRecord",
    "LotLineSegment",
    "AttestedStreetLine",
    "LotContext",
    "LevelArea",
    "LevelHeight",
    "WallSetback",
    "GrossFloorArea",
    "ProposalDerivation",
    "derive_proposal",
]


#: The literal source class stamped on every derived record: a PROVIDED value (what the
#: proposal offers), NEVER an allowance (what a rule permits). It is the FACT boundary the
#: B2 rule engine consumes; it is never a rule id and never implies a rule result.
SOURCE_CLASS = "proposed_derivation"


_Point = tuple[float, float]


class GrossFloorAreaTreatment(str, Enum):
    """The DECLARED vocabulary describing exactly what the B1 gross floor-area sum
    counts - so B2 and professionals can read precisely what the number is and is not.

    It is deliberately NOT a "zoning floor area": that term implies rule treatment
    (deductions, exemptions, bonuses) which is B2 territory, never derived here.
    """

    #: Sum over levels of (the level's derived plate area) x (its ``floor_count``), with
    #: NO deductions, exemptions, or adjustments of any kind - a pure geometric gross.
    PER_LEVEL_GROSS_NO_DEDUCTIONS = "per_level_gross_plate_area_times_floor_count_no_deductions"


#: What the gross sum INCLUDES (declared, so nothing is implied).
GROSS_FLOOR_AREA_INCLUSIONS: tuple[str, ...] = (
    "each level's derived plate area (its own outline where present, else the base outline)",
    "each level's plate area multiplied by that level's floor_count (identical repeated floors)",
)

#: What the gross sum EXCLUDES (declared disclaimers; this is NOT a zoning floor area).
GROSS_FLOOR_AREA_EXCLUSIONS: tuple[str, ...] = (
    "no zoning-floor-area deductions (mechanical, cellar, or any other) - not a zoning floor area",
    "no exemptions, bonuses, or any rule-derived adjustment (that is B2 rule territory)",
    "no net / rentable / usable / efficiency adjustment - this is a geometric gross only",
)


class StreetSetbackResolution(str, Enum):
    """Whether a wall's street-line setback was derived or is a typed honest absence."""

    #: A caller-supplied attested street line was present; the setback was measured.
    DERIVED = "derived"
    #: No attested street line was supplied for this frontage; the setback is a typed
    #: honest ABSENCE (never a default distance). D-051 fallback discipline: absence,
    #: not a guess.
    ABSENT_NO_ATTESTATION = "absent_no_attestation"


class ProposalDerivationError(ValueError):
    """A proposal could not be derived because an input was geometrically degenerate
    or unusable. Carries the exact ``field`` (a dotted path) so a caller can name it
    verbatim. A subclass of :class:`ValueError`; the failure is always typed."""

    def __init__(self, message: str, *, field: str) -> None:
        super().__init__(message)
        self.field = field


# ---------------------------------------------------------------------------
# Typed derived records (each a PROVIDED fact with full provenance)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceRecord:
    """One derived proposal FACT with full provenance.

    ``value``        the derived number, or ``None`` for a typed honest absence.
    ``unit``         the unit of ``value`` (``'square_feet'`` | ``'ratio'`` |
                     ``'feet'`` | ``'count'``).
    ``method``       the deterministic method that produced it (a stable name).
    ``input_ids``    the exact input identifiers the value was computed from - outline
                     digest(s), wall id(s), lot-line id(s), the lot-area provenance
                     digest, a street-attestation digest - NEVER a rule id.
    ``source_class`` the literal :data:`SOURCE_CLASS`; a PROVIDED value, not an allowance.
    ``detail``       a plain description of exactly what the value is (and, for an honest
                     absence, why it is absent).
    ``provenance``   caller-supplied provenance carried through verbatim where the fact
                     consumes an external datum (the lot area, a street attestation);
                     ``None`` for a purely geometric derivation.
    """

    value: float | None
    unit: str
    method: str
    input_ids: tuple[str, ...]
    detail: str
    source_class: str = SOURCE_CLASS
    provenance: Mapping[str, object] | None = None


@dataclass(frozen=True)
class LevelArea:
    """A single level's derived plate area and which outline produced it."""

    level_index: int
    outline_source: str  # "own_outline" | "base_outline"
    evidence: EvidenceRecord


@dataclass(frozen=True)
class LevelHeight:
    """A single level's derived height (``floor_to_floor_ft x floor_count``)."""

    level_index: int
    evidence: EvidenceRecord


@dataclass(frozen=True)
class WallSetback:
    """A named wall's setbacks: to the nearest lot line and (where attested) the street."""

    wall_id: str
    lot_line_setback: EvidenceRecord
    street_line_setback: EvidenceRecord
    street_setback_resolution: StreetSetbackResolution


@dataclass(frozen=True)
class GrossFloorArea:
    """The gross floor-area sum plus its DECLARED inclusions/exclusions vocabulary."""

    treatment: GrossFloorAreaTreatment
    inclusions: tuple[str, ...]
    exclusions: tuple[str, ...]
    evidence: EvidenceRecord


@dataclass(frozen=True)
class ProposalDerivation:
    """The full set of derived proposal FACTS, each carrying an :class:`EvidenceRecord`."""

    source_class: str
    outline_digest: str
    footprint_area: EvidenceRecord
    lot_coverage: EvidenceRecord
    per_level_areas: tuple[LevelArea, ...]
    gross_floor_area: GrossFloorArea
    wall_setbacks: tuple[WallSetback, ...]
    level_heights: tuple[LevelHeight, ...]
    cumulative_height: EvidenceRecord


# ---------------------------------------------------------------------------
# Caller-supplied lot context (parameters; nothing is fetched)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LotLineSegment:
    """One caller-supplied lot-line segment in EPSG:2263 (US survey feet)."""

    id: str
    start: _Point
    end: _Point


@dataclass(frozen=True)
class AttestedStreetLine:
    """A caller-supplied attested street frontage line, in EPSG:2263.

    Mirrors the accepted wide-street attestation OUTPUT read-only: the caller has
    already established the street identity via the accepted DCM / wide-street seam;
    this module NEVER re-derives street width and NEVER re-classifies disposition. It
    measures the geometric distance from the frontage wall to ``start``-``end`` and
    carries ``attestation`` (the provenance identifiers) through verbatim.

    ``wall_id``     the exterior-wall id this frontage attaches to.
    ``attestation`` provenance identifiers carried through verbatim (e.g.
                    ``classification_basis`` / ``source_retrieved_at`` /
                    ``source_raw_digest`` / a street name / object id).
    """

    wall_id: str
    start: _Point
    end: _Point
    attestation: Mapping[str, object]


@dataclass(frozen=True)
class LotContext:
    """Everything the derivation consumes about the lot - all CALLER-SUPPLIED.

    ``area_sq_ft``        the lot's recorded 2263 area (the coverage denominator).
    ``area_provenance``   the lot-area provenance, carried through verbatim.
    ``lot_line_segments`` the lot-line segments walls are measured against.
    ``street_lines``      attested street frontage lines (optional, per wall).
    """

    area_sq_ft: float
    area_provenance: Mapping[str, object]
    lot_line_segments: tuple[LotLineSegment, ...] = ()
    street_lines: tuple[AttestedStreetLine, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Provenance digests (deterministic; hashlib + json, standard library only)
# ---------------------------------------------------------------------------


def _points_digest(points: Sequence[_Point]) -> str:
    """A short deterministic digest of a coordinate sequence (an outline identifier).

    Byte-identical for identical coordinates regardless of Python object identity, so a
    record's ``input_ids`` reproducibly names the exact geometry it was computed from.
    """
    canonical = json.dumps(
        [[float(x), float(y)] for x, y in points], separators=(",", ":")
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _mapping_digest(mapping: Mapping[str, object]) -> str:
    """A short deterministic digest of a provenance mapping (a provenance identifier).

    ``sort_keys`` + ``default=str`` make it order-insensitive and total, so any
    caller-supplied provenance yields a stable identifier without constraining its shape.
    """
    canonical = json.dumps(dict(mapping), separators=(",", ":"), sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Geometry primitives (deterministic, dependency-free)
# ---------------------------------------------------------------------------


def _shoelace_area(closed_ring: Sequence[_Point]) -> float:
    """Unsigned polygon area (sf) by the shoelace formula on a CLOSED ring (the last
    vertex duplicates the first). Sign-independent, so it is invariant to the ring's
    winding direction and to a rotation of the vertex order."""
    total = 0.0
    for i in range(len(closed_ring) - 1):
        x1, y1 = closed_ring[i]
        x2, y2 = closed_ring[i + 1]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def _orientation(a: _Point, b: _Point, c: _Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a: _Point, b: _Point, p: _Point) -> bool:
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(
        a[1], b[1]
    )


def _segments_intersect(a: _Point, b: _Point, c: _Point, d: _Point) -> bool:
    """True when segment ``a``-``b`` and segment ``c``-``d`` share ANY point (standard
    four-orientation test, endpoints included)."""
    d1 = _orientation(c, d, a)
    d2 = _orientation(c, d, b)
    d3 = _orientation(a, b, c)
    d4 = _orientation(a, b, d)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    ):
        return True
    if d1 == 0 and _on_segment(c, d, a):
        return True
    if d2 == 0 and _on_segment(c, d, b):
        return True
    if d3 == 0 and _on_segment(a, b, c):
        return True
    if d4 == 0 and _on_segment(a, b, d):
        return True
    return False


def _point_segment_distance(p: _Point, a: _Point, b: _Point) -> float:
    """Shortest distance from point ``p`` to segment ``a``-``b``."""
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0.0:  # a degenerate (point) segment
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _segment_segment_distance(a: _Point, b: _Point, c: _Point, d: _Point) -> float:
    """Shortest distance between segment ``a``-``b`` and segment ``c``-``d`` (0 when
    they touch or cross)."""
    if _segments_intersect(a, b, c, d):
        return 0.0
    return min(
        _point_segment_distance(a, c, d),
        _point_segment_distance(b, c, d),
        _point_segment_distance(c, a, b),
        _point_segment_distance(d, a, b),
    )


# ---------------------------------------------------------------------------
# Outline extraction from the (already-validated) block
# ---------------------------------------------------------------------------


def _closed_ring(outline: object, field_path: str) -> list[_Point]:
    """The parsed closed ring (including the closing duplicate) of a validated outline.

    The block is validated on entry, so shape defects cannot reach here; the typed
    guards are defense in depth (a caller that skipped validation still fails closed,
    naming the exact field, rather than raising a raw ``TypeError`` mid-arithmetic)."""
    if not isinstance(outline, dict):
        raise ProposalDerivationError(f"{field_path} must be an object", field=field_path)
    vertices = outline.get("vertices")
    if not isinstance(vertices, list) or len(vertices) < 4:
        raise ProposalDerivationError(
            f"{field_path}.vertices must be a closed ring", field=f"{field_path}.vertices"
        )
    ring: list[_Point] = []
    for idx, vertex in enumerate(vertices):
        if not isinstance(vertex, (list, tuple)) or len(vertex) != 2:
            raise ProposalDerivationError(
                f"{field_path}.vertices[{idx}] must be an [x, y] pair",
                field=f"{field_path}.vertices[{idx}]",
            )
        ring.append((float(vertex[0]), float(vertex[1])))
    return ring


def _area_or_refuse(closed_ring: Sequence[_Point], field_path: str) -> float:
    """The polygon area, refused typed if it is not strictly positive (a collapsed or
    zero-area outline is a degeneracy the validated block should never carry; this is
    defense in depth for a caller that bypassed validation)."""
    area = _shoelace_area(closed_ring)
    if not math.isfinite(area) or area <= 0.0:
        raise ProposalDerivationError(
            f"{field_path} encloses no positive area ({area}); a collapsed or degenerate "
            "outline cannot be derived",
            field=field_path,
        )
    return area


# ---------------------------------------------------------------------------
# Per-derivation builders
# ---------------------------------------------------------------------------


def _derive_footprint(base_ring: Sequence[_Point], outline_digest: str) -> EvidenceRecord:
    area = _area_or_refuse(base_ring, "proposed_massing.outline")
    return EvidenceRecord(
        value=area,
        unit="square_feet",
        method="shoelace_area_2263",
        input_ids=(outline_digest,),
        detail=(
            "Footprint (ground-plate) area of the base outline, by the shoelace formula "
            "in EPSG:2263 US survey feet. A PROVIDED value; not an allowance."
        ),
    )


def _derive_coverage(
    footprint_area: float, lot: LotContext, outline_digest: str
) -> EvidenceRecord:
    if not isinstance(lot.area_sq_ft, (int, float)) or isinstance(lot.area_sq_ft, bool):
        raise ProposalDerivationError(
            "lot.area_sq_ft must be a number", field="lot.area_sq_ft"
        )
    lot_area = float(lot.area_sq_ft)
    if not math.isfinite(lot_area) or lot_area <= 0.0:
        raise ProposalDerivationError(
            f"lot.area_sq_ft must be a finite positive number; got {lot.area_sq_ft!r}",
            field="lot.area_sq_ft",
        )
    provenance_digest = _mapping_digest(lot.area_provenance)
    return EvidenceRecord(
        value=footprint_area / lot_area,
        unit="ratio",
        method="footprint_over_lot_area",
        input_ids=(outline_digest, f"lot_area_provenance:{provenance_digest}"),
        detail=(
            "Lot coverage ratio: the derived footprint area divided by the "
            "caller-supplied lot area. A PROVIDED value; not an allowance or a maximum."
        ),
        provenance=dict(lot.area_provenance),
    )


def _derive_level_areas(
    levels: Sequence[dict], base_ring: Sequence[_Point], base_digest: str
) -> tuple[tuple[LevelArea, ...], dict[int, float], dict[int, int]]:
    """Per-level plate areas plus, for the gross sum, the plate area and floor_count per
    level index. A level's OWN outline is used where present, else the base outline; the
    choice is recorded EXPLICITLY on each record."""
    level_areas: list[LevelArea] = []
    plate_by_index: dict[int, float] = {}
    floors_by_index: dict[int, int] = {}
    for pos, level in enumerate(levels):
        level_index = int(level["level_index"])
        own_outline = level.get("outline")
        if own_outline is not None:
            ring = _closed_ring(own_outline, f"proposed_massing.levels[{pos}].outline")
            area = _area_or_refuse(ring, f"proposed_massing.levels[{pos}].outline")
            outline_source = "own_outline"
            digest = _points_digest(ring)
        else:
            area = _area_or_refuse(base_ring, "proposed_massing.outline")
            outline_source = "base_outline"
            digest = base_digest
        plate_by_index[level_index] = area
        floors_by_index[level_index] = int(level["floor_count"])
        level_areas.append(
            LevelArea(
                level_index=level_index,
                outline_source=outline_source,
                evidence=EvidenceRecord(
                    value=area,
                    unit="square_feet",
                    method="shoelace_area_2263",
                    input_ids=(digest,),
                    detail=(
                        f"Plate area of level {level_index}, from its {outline_source} "
                        "(the base outline is used explicitly when a level has no own "
                        "outline). A PROVIDED value; not an allowance."
                    ),
                ),
            )
        )
    level_areas.sort(key=lambda la: la.level_index)
    return tuple(level_areas), plate_by_index, floors_by_index


def _derive_gross(
    plate_by_index: Mapping[int, float],
    floors_by_index: Mapping[int, int],
    base_digest: str,
) -> GrossFloorArea:
    gross = 0.0
    for level_index, plate in plate_by_index.items():
        gross += plate * floors_by_index[level_index]
    return GrossFloorArea(
        treatment=GrossFloorAreaTreatment.PER_LEVEL_GROSS_NO_DEDUCTIONS,
        inclusions=GROSS_FLOOR_AREA_INCLUSIONS,
        exclusions=GROSS_FLOOR_AREA_EXCLUSIONS,
        evidence=EvidenceRecord(
            value=gross,
            unit="square_feet",
            method="sum_plate_area_times_floor_count",
            input_ids=(base_digest,),
            detail=(
                "Gross floor area = sum over levels of plate_area x floor_count, with the "
                "declared inclusions/exclusions vocabulary. NOT a zoning floor area (no "
                "deductions, exemptions, or bonuses); a PROVIDED value, not an allowance."
            ),
        ),
    )


def _derive_heights(levels: Sequence[dict]) -> tuple[tuple[LevelHeight, ...], EvidenceRecord]:
    heights: list[LevelHeight] = []
    cumulative = 0.0
    for level in levels:
        level_index = int(level["level_index"])
        height = float(level["floor_to_floor_ft"]) * int(level["floor_count"])
        cumulative += height
        heights.append(
            LevelHeight(
                level_index=level_index,
                evidence=EvidenceRecord(
                    value=height,
                    unit="feet",
                    method="floor_to_floor_ft_times_floor_count",
                    input_ids=(f"level:{level_index}",),
                    detail=(
                        f"Height of level {level_index} = floor_to_floor_ft x floor_count. "
                        "A PROVIDED value; not an allowance or a maximum."
                    ),
                ),
            )
        )
    heights.sort(key=lambda lh: lh.level_index)
    cumulative_record = EvidenceRecord(
        value=cumulative,
        unit="feet",
        method="sum_level_heights",
        input_ids=tuple(f"level:{lh.level_index}" for lh in heights),
        detail=(
            "Cumulative building height = sum of the per-level heights. A PROVIDED value; "
            "not an allowance or a maximum."
        ),
    )
    return tuple(heights), cumulative_record


def _wall_segment(wall: dict, base_ring: Sequence[_Point]) -> tuple[_Point, _Point]:
    start_index = int(wall["start_vertex_index"])
    end_index = int(wall["end_vertex_index"])
    start = base_ring[start_index]
    end = base_ring[end_index]
    if start == end:  # defense in depth: DB-034(c) refuses this at validation
        raise ProposalDerivationError(
            f"exterior wall {wall.get('id')!r} is a degenerate zero-length segment",
            field=f"proposed_massing.exterior_walls[{wall.get('id')!r}]",
        )
    return start, end


def _lot_line_setback(
    wall_id: str, segment: tuple[_Point, _Point], lot: LotContext
) -> EvidenceRecord:
    if not lot.lot_line_segments:
        return EvidenceRecord(
            value=None,
            unit="feet",
            method="lot_line_setback_absent",
            input_ids=(f"wall:{wall_id}",),
            detail=(
                "No lot-line segment was supplied; the lot-line setback is a typed honest "
                "absence, never a default distance."
            ),
        )
    best_distance: float | None = None
    nearest_id = ""
    for lot_line in lot.lot_line_segments:
        distance = _segment_segment_distance(
            segment[0], segment[1], lot_line.start, lot_line.end
        )
        if best_distance is None or distance < best_distance:
            best_distance = distance
            nearest_id = lot_line.id
    return EvidenceRecord(
        value=best_distance,
        unit="feet",
        method="min_segment_distance_2263",
        input_ids=(f"wall:{wall_id}", f"lot_line:{nearest_id}"),
        detail=(
            f"Minimum distance from wall {wall_id!r} to the {len(lot.lot_line_segments)} "
            f"supplied lot-line segment(s); nearest = {nearest_id!r}. A PROVIDED value; "
            "not an allowance or a maximum."
        ),
    )


def _street_line_setback(
    wall_id: str, segment: tuple[_Point, _Point], lot: LotContext
) -> tuple[EvidenceRecord, StreetSetbackResolution]:
    attested = next(
        (line for line in lot.street_lines if line.wall_id == wall_id), None
    )
    if attested is None:
        return (
            EvidenceRecord(
                value=None,
                unit="feet",
                method="street_line_setback_absent",
                input_ids=(f"wall:{wall_id}",),
                detail=(
                    "No attested street line was supplied for this frontage; the "
                    "street-line setback is a typed honest absence, never a default "
                    "distance (D-051 fallback discipline: absence, not a guess)."
                ),
            ),
            StreetSetbackResolution.ABSENT_NO_ATTESTATION,
        )
    distance = _segment_segment_distance(
        segment[0], segment[1], attested.start, attested.end
    )
    return (
        EvidenceRecord(
            value=distance,
            unit="feet",
            method="min_segment_distance_2263",
            input_ids=(
                f"wall:{wall_id}",
                f"street_attestation:{_mapping_digest(attested.attestation)}",
            ),
            detail=(
                f"Minimum distance from wall {wall_id!r} to the caller-attested street "
                "line. The street width is NOT re-derived here; the attestation "
                "provenance is carried through. A PROVIDED value; not an allowance."
            ),
            provenance=dict(attested.attestation),
        ),
        StreetSetbackResolution.DERIVED,
    )


def _derive_wall_setbacks(
    walls: Sequence[dict], base_ring: Sequence[_Point], lot: LotContext
) -> tuple[WallSetback, ...]:
    setbacks: list[WallSetback] = []
    for wall in walls:
        wall_id = str(wall["id"])
        segment = _wall_segment(wall, base_ring)
        street_record, resolution = _street_line_setback(wall_id, segment, lot)
        setbacks.append(
            WallSetback(
                wall_id=wall_id,
                lot_line_setback=_lot_line_setback(wall_id, segment, lot),
                street_line_setback=street_record,
                street_setback_resolution=resolution,
            )
        )
    return tuple(setbacks)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def derive_proposal(block: object, lot: LotContext) -> ProposalDerivation:
    """Derive the deterministic FACTS of a proposed building.

    ``block`` a ``proposed_massing`` block (it is re-validated with
    :func:`app.scenario.proposal.validate_proposed_massing` as defense in depth; a
    :class:`app.scenario.proposal.ProposedMassingError` propagates on any structural or
    geometric defect). ``lot`` the CALLER-SUPPLIED lot context (area + provenance, lot-line
    segments, and optional attested street lines).

    Returns a :class:`ProposalDerivation` whose every value is an :class:`EvidenceRecord`
    carrying its inputs, method, and the literal ``source_class`` :data:`SOURCE_CLASS`.
    Raises :class:`ProposalDerivationError` (typed, exact field) on any geometric
    degeneracy the caller drove past validation. Performs NO rule evaluation and computes
    NO allowance (D-076-R002).
    """
    if not isinstance(lot, LotContext):
        raise ProposalDerivationError(
            "lot must be a LotContext instance", field="lot"
        )
    validate_proposed_massing(block)  # defense in depth; typed ProposedMassingError
    if not isinstance(block, dict):  # pragma: no cover - the validator guarantees a dict
        raise ProposalDerivationError(
            "proposed_massing must be an object", field="proposed_massing"
        )

    base_ring = _closed_ring(block["outline"], "proposed_massing.outline")
    base_digest = _points_digest(base_ring)
    levels = block["levels"]
    walls = block["exterior_walls"]

    footprint = _derive_footprint(base_ring, base_digest)
    coverage = _derive_coverage(footprint.value, lot, base_digest)  # type: ignore[arg-type]
    level_areas, plate_by_index, floors_by_index = _derive_level_areas(
        levels, base_ring, base_digest
    )
    gross = _derive_gross(plate_by_index, floors_by_index, base_digest)
    heights, cumulative = _derive_heights(levels)
    wall_setbacks = _derive_wall_setbacks(walls, base_ring, lot)

    return ProposalDerivation(
        source_class=SOURCE_CLASS,
        outline_digest=base_digest,
        footprint_area=footprint,
        lot_coverage=coverage,
        per_level_areas=level_areas,
        gross_floor_area=gross,
        wall_setbacks=wall_setbacks,
        level_heights=heights,
        cumulative_height=cumulative,
    )
