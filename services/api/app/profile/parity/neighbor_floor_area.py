"""Capture each neighbour's existing zoning floor area (queue item B-11 slice 2, plan
section 11b "neighbours' unused floor area"; Lane B).

Lane B provides DATA, never a capacity. B-11 slice 1 built the carriage in
``app.profile.parity.unused_floor_area`` (the subject's and each neighbour's sourced
existing-floor-area INPUT, with the unused-floor-area output always "Not confirmed"). This
module is slice 2: it CAPTURES each neighbour's existing zoning floor area through the B-05
source order and feeds the captured inputs into that carriage.

What this module does, and does not do:

- **Neighbour set (documented method, never computed here).** A neighbour is a lot on the
  subject's tax block whose recorded MapPLUTO EPSG:2263 outline shares a lot line with the
  subject's outline - a touching lot. That geometry test lives in B-07
  (``app.spatial.multi_lot_site``) and is proven on the benchmark in
  ``tests/spatial/test_multi_lot_site_benchmark_block_7334.py`` (lots 1 and 70 share one
  99.98 ft lot line). This module does not recompute geometry: the caller supplies the
  neighbour set (the recorded touching lots), and :data:`NEIGHBOR_SET_METHOD` records how
  it is defined. The method, and the benchmark neighbour, are recorded in
  ``docs/research/neighbor-floor-area-2026-10-03.md``.
- **Capture (the B-05 source order, reused verbatim).** Each neighbour's existing zoning
  floor area is resolved with ``app.profile.existing_floor_area`` exactly as the subject's
  is: a certificate-of-occupancy figure, else a DOB job-filing figure, else a stated
  assumption, else "not recorded" (value unknown). DOF/PLUTO building area has no path in
  (``ExistingFloorAreaEvidence`` admits no building-area input). This module adds no new
  source order and reads no new field; it only applies B-05 per neighbour and labels the
  outcome ``captured`` / ``not_recorded``.
- **Wiring (into the slice-1 carriage, unchanged).** :func:`neighbor_parity_data` hands the
  captured :class:`~app.profile.existing_floor_area.ExistingFloorAreaResult` of each
  neighbour to ``neighbors_unused_floor_area_data`` (slice 1). The parity output stays the
  owner-settled "Remaining development capacity: Not confirmed" wording (D-090-R038) - never
  a number, never a subtraction. The allowance and the subtraction are the rule engine's
  (Lane A), which is off.

Pure, deterministic code: no I/O, no legal logic, no calculation. Inputs are never changed.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from app.profile.existing_floor_area import (
    ExistingFloorAreaEvidence,
    ExistingFloorAreaResult,
    resolve_existing_zoning_floor_area,
)
from app.profile.parity.unused_floor_area import (
    ROLE_NEIGHBOR,
    UnusedFloorAreaData,
    neighbors_unused_floor_area_data,
)

__all__ = [
    "CAPTURE_CAPTURED",
    "CAPTURE_NOT_RECORDED",
    "NEIGHBOR_SET_METHOD",
    "NeighborEvidence",
    "NeighborFloorAreaCapture",
    "NeighborFloorAreaCaptureSet",
    "capture_neighbor_floor_area",
    "capture_neighbors",
    "neighbor_parity_data",
]

# captured = the B-05 source order produced a figure (value is on file); not_recorded = it
# did not (value unknown). This layer never produces a remaining capacity either way.
CAPTURE_CAPTURED = "captured"
CAPTURE_NOT_RECORDED = "not_recorded"

# How the neighbour set is defined (documented method, surfaced verbatim; the geometry test
# is B-07's, not recomputed here). Recorded in docs/research/neighbor-floor-area-2026-10-03.md.
NEIGHBOR_SET_METHOD = (
    "Neighbours are the lots on the subject's tax block whose recorded MapPLUTO EPSG:2263 "
    "outline shares a lot line with the subject's outline (a touching lot), per the recorded "
    "geometry (B-07, app.spatial.multi_lot_site). For the benchmark subject 215-16 Northern "
    "Boulevard (BBL 4073340070) the recorded fixtures establish tax lot 1 (BBL 4073340001, "
    "215-10 Northern Boulevard) as a touching neighbour: lots 1 and 70 share one 99.98 ft lot "
    "line. Only recorded, touching lots are included; a block-wide neighbour set is a future "
    "capture (an open B-11 owner question)."
)

_BBL = re.compile(r"^[1-5][0-9]{9}$")


@dataclass(frozen=True)
class NeighborEvidence:
    """One neighbour's recorded existing-floor-area evidence, ready for the B-05 source order.

    Attributes:
        bbl: the neighbour tax lot (10-digit BBL).
        evidence: the admitted B-05 inputs for this neighbour - recorded DOB job filings,
            certificate-of-occupancy rows (completion evidence), a figure read from a
            certificate of occupancy, and/or a stated assumption. No building-area input
            exists in this type, so DOF/PLUTO building area has no path in.
        recorded_building_count: the city-recorded number of buildings on the neighbour's
            tax lot (a completeness check on DOB filings only; never an area), or None.
    """

    bbl: str
    evidence: ExistingFloorAreaEvidence
    recorded_building_count: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.bbl, str) or not _BBL.match(self.bbl):
            raise ValueError(f"neighbour bbl must be a 10-digit BBL, got {self.bbl!r}")
        if not isinstance(self.evidence, ExistingFloorAreaEvidence):
            raise ValueError("evidence must be an ExistingFloorAreaEvidence")


@dataclass(frozen=True)
class NeighborFloorAreaCapture:
    """One neighbour's captured existing zoning floor area, with its provenance.

    The output of the B-05 source order for one neighbour, labelled ``captured`` or
    ``not_recorded``. It carries the sourced figure (or null) and every figure it set aside
    with the reason, so a "not recorded" outcome is auditable. It never carries a remaining
    development capacity.

    Attributes:
        bbl: the neighbour tax lot (10-digit BBL).
        status: :data:`CAPTURE_CAPTURED` when a figure is on file, else
            :data:`CAPTURE_NOT_RECORDED`.
        value_sq_ft: the sourced existing zoning floor area in square feet, or None.
        unit: ``square_feet`` when known, else None.
        basis: which B-05 source was used (``certificate_of_occupancy`` / ``dob_job_filing``
            / ``stated_assumption``) or ``unknown``.
        basis_label: its plain label.
        source: the input's provenance (a site_fact source), or None when not recorded.
        note: the plain-English note (why there is no figure / what was set aside).
        considered: every figure seen but not used, each with its reason (and source where
            the figure came from a DOB filing).
        zoning_lot_mentions: recorded DOB rows whose text mentions a zoning lot (a reminder
            only; never read for lot numbers).
        result: the full B-05 ``ExistingFloorAreaResult`` (for the slice-1 carriage).
    """

    bbl: str
    status: str
    value_sq_ft: int | float | None
    unit: str | None
    basis: str
    basis_label: str
    source: dict | None
    note: str | None
    considered: tuple[dict, ...]
    zoning_lot_mentions: tuple[dict, ...]
    result: ExistingFloorAreaResult

    def to_dict(self) -> dict:
        """The capture as a plain dict (the ``result`` is omitted - it is the carriage
        input, not a serialised value)."""
        return {
            "lot_bbl": self.bbl,
            "role": ROLE_NEIGHBOR,
            "status": self.status,
            "value_sq_ft": self.value_sq_ft,
            "unit": self.unit,
            "basis": self.basis,
            "basis_label": self.basis_label,
            "source": self.source,
            "note": self.note,
            "considered": list(self.considered),
            "zoning_lot_mentions": list(self.zoning_lot_mentions),
        }


@dataclass(frozen=True)
class NeighborFloorAreaCaptureSet:
    """The captured existing floor area of every neighbour, with the neighbour-set method.

    Attributes:
        method: how the neighbour set was defined (:data:`NEIGHBOR_SET_METHOD`), surfaced
            verbatim so the architect sees exactly which lots are treated as neighbours.
        captures: one :class:`NeighborFloorAreaCapture` per neighbour, in the order supplied.
    """

    method: str
    captures: tuple[NeighborFloorAreaCapture, ...]

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "captures": [capture.to_dict() for capture in self.captures],
        }


def capture_neighbor_floor_area(neighbor: NeighborEvidence) -> NeighborFloorAreaCapture:
    """Capture one neighbour's existing zoning floor area through the B-05 source order.

    The resolution is ``app.profile.existing_floor_area.resolve_existing_zoning_floor_area``
    - the same code and the same precedence the subject uses. DOF/PLUTO building area is
    never read (the evidence type admits no such input). The outcome is labelled
    ``captured`` when a figure is on file, else ``not_recorded``.
    """
    result = resolve_existing_zoning_floor_area(
        neighbor.bbl, neighbor.evidence,
        recorded_building_count=neighbor.recorded_building_count,
    )
    fact = result.fact
    value = fact.get("value")
    status = CAPTURE_CAPTURED if value is not None else CAPTURE_NOT_RECORDED
    return NeighborFloorAreaCapture(
        bbl=neighbor.bbl,
        status=status,
        value_sq_ft=value,
        unit=fact.get("unit"),
        basis=result.basis,
        basis_label=result.basis_label,
        source=fact.get("source"),
        note=fact.get("note"),
        considered=result.considered,
        zoning_lot_mentions=result.zoning_lot_mentions,
        result=result,
    )


def capture_neighbors(
    neighbors: Sequence[NeighborEvidence],
    *,
    method: str = NEIGHBOR_SET_METHOD,
) -> NeighborFloorAreaCaptureSet:
    """Capture every neighbour's existing zoning floor area, one entry per neighbour, in
    order. ``method`` records how the neighbour set was defined (default
    :data:`NEIGHBOR_SET_METHOD`)."""
    captures = tuple(capture_neighbor_floor_area(neighbor) for neighbor in neighbors)
    return NeighborFloorAreaCaptureSet(method=method, captures=captures)


def neighbor_parity_data(
    capture_set: NeighborFloorAreaCaptureSet,
) -> tuple[UnusedFloorAreaData, ...]:
    """Wire the captured neighbour inputs into the slice-1 unused-floor-area carriage.

    Each neighbour's captured :class:`~app.profile.existing_floor_area.ExistingFloorAreaResult`
    is passed to ``neighbors_unused_floor_area_data`` (slice 1), which reports the owner-settled
    "Remaining development capacity: Not confirmed" for every neighbour and carries the sourced
    existing-floor-area input - never a number, never a subtraction.
    """
    return neighbors_unused_floor_area_data(
        [capture.result for capture in capture_set.captures]
    )
