"""Carry a lot's recorded facts to the merged decision module (task M5-T130, Part 0 of
docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md; the second of the engine pieces).

This module gathers, as sourced facts with their provenance, everything the merged decision
module (``result_way_inputs.ResultWayInputs``) needs, builds that input for a lot from the
recorded official data, calls :func:`result_ways.decide_result_ways`, and returns the ways
BESIDE the gathered facts. It is NEW and nothing under ``services/api/app`` calls it; it edits no
existing file, the engine still runs as it does, and the emitted results document does not
change. The piece after it switches the emitted document to contract 1.3.0 and wires this entry
function into the real path.

It gathers, each where the module asks for a three-state fact:
  (a) the recorded city-record columns - from :mod:`result_way_facts` (reading O14);
  (b) the lot type, the district and the recorded lot area with its fact id - from the evaluator
      inputs as they are built today;
  (c) the reach - :func:`app.spatial.lot_reach.measure_lot_reach` on the prepared outline and
      the site geometry of the recorded lot, adapted into the module's own reach records; an
      unknown measurement stays unknown;
  (d) the two area figures and whether they agree - reading O15 below;
  (e) the four conditions with no data source - "not checked", always, until a source exists;
  (f) the special density area - "not given" unless the request carries a user's statement; a
      statement is passed on as a statement and appears in NO fact record (owner rule 1; R255);
  (g) what an independent reading supports under a recorded overlay -
      :mod:`result_way_bridge_overlay` (reading O16);
  (h) the large-lot answer of gap K3 - reading O17 below.
The housing kind is the user's choice of option and is passed through.

READING O15 (the orchestrator's). No area tolerance is invented. The two figures AGREE only when
the outline's area, rounded to the whole square foot, equals the recorded figure; otherwise they
DISAGREE; where the outline's area cannot be computed the comparison could not be made. Only one
recorded lot in the repository holds both figures and they differ by 313 sq ft, which the work
order calls a disagreement; no recorded data supports a wider tolerance, so none is invented. The
rule is stated in words with the comparison's result so a later piece can print it. A wider
tolerance needs recorded lots to rest on and is owed work (backlog row DB-173).

READING O17 (the orchestrator's). The large-lot answer is computed from the RECORDED lot area
against the one figure held here from the captured text of ZR 23-362 (held once, with its capture
id and quoted words); no recorded area gives "not stated". Gap K3 is applied as the work order
writes it ("30,000 square feet or more"); the merged reading suggests ZR 23-362(b) may reach only
eligible sites and so may not arise for a plain R6B lot (backlog rows DB-168, DB-172), which the
producer report records - this piece changes no result on it.

A FACT THAT CONTRADICTS ANOTHER IS NOT RESOLVED HERE (reading O18): where the evaluator inputs
refuse today (two sources that disagree at the same rank), this piece never runs - it reads an
evaluator-inputs document the builders already produced, which fails closed on such a conflict.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.spatial import lot_reach as _lot_reach
from app.spatial.site_geometry.outline import PreparedOutline
from app.spatial.site_geometry.results import SiteGeometry

from .result_way_bridge_overlay import overlay_support_for
from .result_way_facts import RecordedConditions, gather_recorded_facts
from .result_way_inputs import (
    AreaAgreement,
    Checked,
    CornerReach,
    DensityKnowledge,
    LegalMeasure,
    LotAreaFigures,
    LotType,
    ReachMeasurements,
    ReachValue,
    Recorded,
    ResultWayInputs,
    ResultWays,
    StreetReach,
)
from .result_ways import decide_result_ways

__all__ = [
    "LARGE_LOT_THRESHOLD",
    "GatheredResult",
    "LargeLotAnswer",
    "SourceFact",
    "adapt_reach",
    "compare_lot_area",
    "gather_result_ways",
    "large_lot_answer",
    "read_site_inputs",
]

# The ONE zoning figure of reading O17, held once with its capture id and quoted words (the
# captured ZR 23-362(b)(1) threshold). It is compared with the recorded lot area; it is never a
# number the module derives. No other module file carries a zoning number.
LARGE_LOT_THRESHOLD = LegalMeasure(
    value=30000.0,
    unit="square feet",
    zr_section="ZR 23-362",
    capture_snapshot_id="zr-23-362",
    capture_content_digest="f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9",
    captured_words=(
        "65 percent on zoning lots with a lot area of 30,000 square feet or more that are not "
        "large sites"
    ),
    comparison="the recorded lot area is 30,000 square feet or more",
)

_LOT_TYPE_BY_NAME = {
    "corner": LotType.CORNER,
    "interior": LotType.INTERIOR,
    "through": LotType.THROUGH,
}


@dataclass(frozen=True)
class SourceFact:
    """One sourced value carried from the evaluator inputs, with its fact id for provenance."""

    name: str
    value: Any
    fact_id: str | None


@dataclass(frozen=True)
class LargeLotAnswer:
    """The gap-K3 large-lot answer (reading O17): True / False / None ("not stated"), the plain
    statement, and the captured measure it was compared against."""

    met: bool | None
    statement: str
    measure: LegalMeasure


@dataclass(frozen=True)
class GatheredResult:
    """The ways beside the gathered facts and their provenance (the entry function's return)."""

    ways: ResultWays
    inputs: ResultWayInputs
    recorded: RecordedConditions
    area_statement: str
    large_lot: LargeLotAnswer
    source_facts: tuple[SourceFact, ...]
    held_back: tuple[str, ...]


# ---------------------------------------------------------------------------
# (b) the lot type, the district and the recorded lot area from the evaluator inputs
# ---------------------------------------------------------------------------
def _input_record(evaluator_inputs: Mapping[str, Any] | None, key: str) -> Mapping | None:
    if not isinstance(evaluator_inputs, Mapping):
        return None
    inputs = evaluator_inputs.get("inputs")
    if not isinstance(inputs, list):
        return None
    for record in inputs:
        if isinstance(record, Mapping) and record.get("key") == key:
            return record
    return None


def read_site_inputs(
    evaluator_inputs: Mapping[str, Any] | None,
) -> tuple[str | None, LotType | None, float | None, tuple[SourceFact, ...], tuple[str, ...]]:
    """Read the district, the lot type and the recorded lot area (with fact ids) from the
    evaluator-inputs document as it is built today. A key that is not present stays None (never a
    default): the dependent results are then withheld by the decision module."""
    held: list[str] = []
    district_rec = _input_record(evaluator_inputs, "zoning_district")
    type_rec = _input_record(evaluator_inputs, "lot_type")
    area_rec = _input_record(evaluator_inputs, "lot_area_sq_ft")

    district = district_rec.get("value") if district_rec else None
    lot_type_name = type_rec.get("value") if type_rec else None
    lot_type = _LOT_TYPE_BY_NAME.get(lot_type_name) if lot_type_name is not None else None
    if lot_type_name is not None and lot_type is None:
        held.append(
            f"The recorded lot type {lot_type_name!r} is not one the program recognises, so the "
            "lot type is carried as not given."
        )
    area_value = area_rec.get("value") if area_rec else None
    recorded_area = float(area_value) if isinstance(area_value, (int, float)) else None

    district_id = district_rec.get("fact_id") if district_rec else None
    type_id = type_rec.get("fact_id") if type_rec else None
    area_id = area_rec.get("fact_id") if area_rec else None
    source_facts = (
        SourceFact("zoning district", district, district_id),
        SourceFact("lot type", lot_type_name, type_id),
        SourceFact("recorded lot area", recorded_area, area_id),
    )
    return district, lot_type, recorded_area, source_facts, tuple(held)


# ---------------------------------------------------------------------------
# (c) the reach, adapted from the spatial measurement into the module's records
# ---------------------------------------------------------------------------
def adapt_reach(measured: _lot_reach.LotReach) -> ReachMeasurements:
    """Adapt the spatial lot-reach measurement into the decision module's own reach records. A
    value stays unknown exactly when the measurement is unknown (None); never a zero."""
    street_lines = tuple(
        StreetReach(line.street_name, ReachValue(line.reach.value))
        for line in measured.street_lines
    )
    corner = CornerReach(
        reach=ReachValue(measured.corner.reach.value),
        angle=ReachValue(measured.corner.angle.value),
    )
    return ReachMeasurements(street_lines, corner)


def _reach_for(
    outline: PreparedOutline | None, geometry: SiteGeometry | None,
) -> ReachMeasurements | None:
    """The reach for the lot, or None when there is no site geometry at all (then the decision
    module records every reach-dependent result as not known)."""
    if geometry is None:
        return None
    return adapt_reach(_lot_reach.measure_lot_reach(outline, geometry))


# ---------------------------------------------------------------------------
# (d) the two area figures and whether they agree (reading O15)
# ---------------------------------------------------------------------------
def _sq_ft(value: float) -> str:
    whole = int(round(value))
    return f"{whole:,} sq ft" if float(whole) == float(value) else f"{value:,.2f} sq ft"


def compare_lot_area(
    recorded_sq_ft: float | None, outline_sq_ft: float | None,
) -> tuple[LotAreaFigures, str]:
    """Compare the recorded lot area with the tax-map outline area (reading O15). Returns the
    figures record the decision module consumes and a plain statement of the rule and its result.

    No tolerance is invented: the figures AGREE only when the outline area, rounded to the whole
    square foot, equals the recorded figure; otherwise they DISAGREE; the outline area is never
    used in a calculation in place of the recorded figure.
    """
    if recorded_sq_ft is None:
        return (
            LotAreaFigures(None, None, outline_sq_ft),
            "No lot area is recorded; the tax-map outline area is never used in its place.",
        )
    if outline_sq_ft is None:
        return (
            LotAreaFigures(recorded_sq_ft, AreaAgreement.COULD_NOT_COMPARE, None),
            f"The recorded lot area is {_sq_ft(recorded_sq_ft)}; the tax-map outline area could "
            "not be computed, so the two could not be compared.",
        )
    if round(outline_sq_ft) == recorded_sq_ft:
        return (
            LotAreaFigures(recorded_sq_ft, AreaAgreement.AGREES, outline_sq_ft),
            f"The tax-map outline area ({_sq_ft(outline_sq_ft)}) matches the recorded lot area "
            f"({_sq_ft(recorded_sq_ft)}) to the whole square foot, so the recorded lot area is "
            "used.",
        )
    return (
        LotAreaFigures(recorded_sq_ft, AreaAgreement.DISAGREES, outline_sq_ft),
        f"The recorded lot area ({_sq_ft(recorded_sq_ft)}) and the tax-map outline area "
        f"({_sq_ft(outline_sq_ft)}) differ, so results that need the area rest on the recorded "
        "figure until a survey or deed settles it. Both figures are shown; neither replaces the "
        "other.",
    )


# ---------------------------------------------------------------------------
# (h) the large-lot answer of gap K3 (reading O17)
# ---------------------------------------------------------------------------
def large_lot_answer(recorded_sq_ft: float | None) -> LargeLotAnswer:
    """Whether the recorded lot area is at or above the lot size at which a different maximum lot
    coverage applies (reading O17). No recorded area gives "not stated" (None)."""
    if recorded_sq_ft is None:
        return LargeLotAnswer(
            None,
            "Whether this lot is at or above the lot size at which a different maximum lot "
            "coverage applies is not stated, because no lot area is recorded.",
            LARGE_LOT_THRESHOLD,
        )
    met = recorded_sq_ft >= LARGE_LOT_THRESHOLD.value
    phrase = "at or above" if met else "below"
    return LargeLotAnswer(
        met,
        f"The recorded lot area ({_sq_ft(recorded_sq_ft)}) is {phrase} the lot size at which a "
        "different maximum lot coverage applies.",
        LARGE_LOT_THRESHOLD,
    )


# ---------------------------------------------------------------------------
# (f) the special density area from a user's statement (never a fact)
# ---------------------------------------------------------------------------
def _density(special_density_statement: bool | None) -> tuple[DensityKnowledge, tuple[str, ...]]:
    """The special-density knowledge from a user's statement. None is "not given"; True is the
    user's statement that the lot is NOT in a special density area (the only statement the work
    order gives a path for); a statement that it IS in one is not decided and is held back."""
    if special_density_statement is None:
        return DensityKnowledge.NOT_GIVEN, ()
    if special_density_statement is True:
        return DensityKnowledge.USER_STATEMENT_NOT_IN_ONE, ()
    return DensityKnowledge.NOT_GIVEN, (
        "A statement that the lot is in a special density area is not yet handled, so the special "
        "density area is carried as not given.",
    )


# ---------------------------------------------------------------------------
# the entry function
# ---------------------------------------------------------------------------
def gather_result_ways(
    *,
    evaluator_inputs: Mapping[str, Any] | None,
    profile: Mapping[str, Any] | None,
    outline: PreparedOutline | None,
    geometry: SiteGeometry | None,
    housing_kind: str | None,
    special_density_statement: bool | None = None,
) -> GatheredResult:
    """Gather a lot's recorded facts, build the decision module's input, decide the ways, and
    return the ways beside the gathered facts and their provenance.

    ``evaluator_inputs`` is the document the builders produce today (the lot type, the district
    and the recorded lot area, each a sourced fact with its id); ``profile`` is the built
    property profile for the recorded map-based columns (reading O14); ``outline`` and
    ``geometry`` are the prepared tax-map outline and the single-lot site geometry for the reach
    (reading O14/O15) and the outline area (reading O15); ``housing_kind`` is the user's choice of
    option, carried through; ``special_density_statement`` is a user's statement, None when none
    was made (it never enters a fact record - owner rule 1).
    """
    held: list[str] = []

    district, lot_type, recorded_area, source_facts, site_held = read_site_inputs(evaluator_inputs)
    held.extend(site_held)

    recorded = gather_recorded_facts(profile)
    reach = _reach_for(outline, geometry)
    outline_area = outline.polygon.area if outline is not None else None
    area, area_statement = compare_lot_area(recorded_area, outline_area)
    large_lot = large_lot_answer(recorded_area)
    density, density_held = _density(special_density_statement)
    held.extend(density_held)

    overlay_support = None
    if recorded.commercial_overlay.state is Recorded.PRESENT:
        overlay_support = overlay_support_for(recorded.commercial_overlay.code, district)

    inputs = ResultWayInputs(
        district=district,
        lot_type=lot_type,
        housing_kind=housing_kind,
        area=area,
        reach=reach,
        special_purpose_district=recorded.special_purpose_district.state,
        split_by_district_line=recorded.split_by_district_line.state,
        commercial_overlay=recorded.commercial_overlay.state,
        commercial_overlay_code=recorded.commercial_overlay.code,
        inclusionary_housing_area=recorded.inclusionary_housing_area.state,
        flood_zone=recorded.flood_zone.state,
        landmark_or_historic=recorded.landmark_or_historic.state,
        # (e) the four conditions with no data source are "not checked", always.
        waterfront=Checked.NOT_CHECKED,
        airport_height=Checked.NOT_CHECKED,
        transit_easement=Checked.NOT_CHECKED,
        near_district_line=Checked.NOT_CHECKED,
        special_density=density,
        large_lot_threshold_met=large_lot.met,
        overlay_support=overlay_support,
    )
    ways = decide_result_ways(inputs)
    return GatheredResult(
        ways=ways,
        inputs=inputs,
        recorded=recorded,
        area_statement=area_statement,
        large_lot=large_lot,
        source_facts=source_facts,
        held_back=tuple(held),
    )
