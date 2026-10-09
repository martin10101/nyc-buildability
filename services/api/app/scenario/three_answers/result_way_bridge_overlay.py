"""What an independent reading supports under a recorded commercial overlay (task M5-T130,
reading O16 of the orchestrator).

The merged decision module (:mod:`result_ways`) holds no table of what an overlay reading
supports: its caller states, per result family, whether an independent reading supports showing
that family under a recorded commercial overlay. This module is that caller's table.

READING O16 (the orchestrator's, to be confirmed or corrected by the reviewers). A small table,
held in app code, says per result family whether an independent reading supports showing it
under a C2-2 overlay mapped within R6B, each entry naming the reference row it rests on. App
code never reads the reference files at run time; a TEST reads those rows through the test-only
loader (which refuses a superseded row) and fails if a row is superseded, is not a value row,
or does not say "same as plain R6B". A family is SUPPORTED only where its current row gives the
answer with no standing condition from either reading.

By the merged rows (``cases/step-p4-worked.json``, ``cases/overlay-reading.json`` and
``cases/step-p5-worked.json``): the floor area ratio and the lot-coverage rule are supported; the
base and building heights, the setback and the dwelling-unit rule rest on the overlay rows that
say "same as plain R6B" with no standing condition, so they are supported; the REAR YARD is now
supported too - the step-P5 row ``zr-34-23-page`` reads the ZR 34-23 page as the complete
three-subsection list, none of which speaks of the rear yard, which resolves the step-P4
completeness caveat the rear yard was held on, so the overlay adds no rear-yard rule and the rear
yard follows the plain R6B rules (M5-T144, owner D-090 R646/R647). Being supported means the
overlay no longer blocks the rear yard; the plain R6B corner/reach rules then decide it (and still
withhold it beyond the corner-lot portion, for a missing property fact, in the decision module).
Any other overlay code, or an overlay within another district, supports nothing (the caller
supplies this table only for a C2-2 overlay within R6B). The street-wall-location rule, which the
readings say the overlay changes, is not a result of this module.
"""

from __future__ import annotations

from dataclasses import dataclass

from .result_way_inputs import OverlayResultSupport, ResultFamily

__all__ = [
    "OVERLAY_DISTRICT",
    "OVERLAY_SUPPORT_ROWS",
    "SUPPORTED_OVERLAY_CODE",
    "OverlaySupportRow",
    "overlay_support_for",
]

# The one overlay code and district this table reads. For any other code or district the caller
# states that nothing is supported (so the decision module withholds every residential result).
SUPPORTED_OVERLAY_CODE = "C2-2"
OVERLAY_DISTRICT = "R6B"


@dataclass(frozen=True)
class OverlaySupportRow:
    """One table entry: whether a family is supported and the reference row it rests on.

    ``case_id`` / ``row_id`` name the CURRENT reference-case row the entry rests on; a test reads
    that row through the loader and checks it is a value row that says "same as plain R6B" and
    (for a supported family) carries no standing condition. App code never reads the file.
    """

    family: ResultFamily
    supported: bool
    case_id: str
    row_id: str
    reading_owed: str = ""
    zr_sections: tuple[str, ...] = ()


# The orchestrator's reading O16 as a table. Each row names the current merged reference row it
# rests on (the step-P4 case supersedes the step-P2 overlay-reading rows for floor area ratio and
# lot coverage; the base/building height, setback and dwelling-unit rows stay in the
# overlay-reading case; the rear yard now rests on the step-P5 row zr-34-23-page, which resolves
# the completeness caveat the step-P4 rear-yard row was held on - M5-T144).
OVERLAY_SUPPORT_ROWS: tuple[OverlaySupportRow, ...] = (
    OverlaySupportRow(ResultFamily.FLOOR_AREA, True, "step-p4-worked", "floor-area-ratio"),
    OverlaySupportRow(ResultFamily.COVERAGE, True, "step-p4-worked", "lot-coverage"),
    OverlaySupportRow(ResultFamily.HEIGHTS, True, "overlay-reading", "base-and-building-height"),
    OverlaySupportRow(ResultFamily.SETBACK, True, "overlay-reading", "setback-above-base"),
    OverlaySupportRow(ResultFamily.UNIT_LIMIT, True, "overlay-reading", "dwelling-units"),
    OverlaySupportRow(ResultFamily.REAR_YARD, True, "step-p5-worked", "zr-34-23-page"),
)


def overlay_support_for(
    overlay_code: str | None, district: str | None,
) -> dict[ResultFamily, OverlayResultSupport] | None:
    """The per-family overlay support the decision module consumes for a recorded overlay, or
    None when this table does not speak for it (another overlay code or another district - the
    decision module then withholds every residential result, naming the owed reading).

    The returned statement is exactly reading O16's table; it is not a legal determination and
    is marked as the orchestrator's reading in the module doc and the producer report.
    """
    if overlay_code != SUPPORTED_OVERLAY_CODE or district != OVERLAY_DISTRICT:
        return None
    return {
        row.family: OverlayResultSupport(
            supported=row.supported, reading_owed=row.reading_owed, zr_sections=row.zr_sections,
        )
        for row in OVERLAY_SUPPORT_ROWS
    }
