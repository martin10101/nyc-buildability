// Display rules for the first-building-options blocks of a results document (results contract 1.4.0;
// M5-T146 / M5-T147; rulings W1–W7; D-090-R509/R526/R540/R541/R543/R544/R556/R570/R688). Pure
// functions over a `results` document: no fetching, no legal logic, no arithmetic on the numbers —
// every value, ratio, condition, label, reason and fit note is READ from the document and only
// formatted for reading. A withheld result carries NO number and NEVER a substitute (R556/R570); the
// single building-option answer that points to this list is handled in three-answers.ts. Nothing is
// called feasible, complies, confirmed, validated or legally correct, and no human verdict is entered.
//
// Ruling W7: the share range and the apartment size are SHOWN with the values used and called
// preliminary assumptions; they are NOT editable on this screen (work owed, DB-213(a)).
//
// The legal dwelling-unit limit is NOT rendered here: on the benchmark it is a withheld value_state
// of the floor-area-allowance answer (shown by that answer card), and the top-level unit_estimate
// block is now a pointer to this list (M5-T146 parts B/E) — so this section never restates it.

import type {
  BuildingAlternative,
  BuildingNotWorked,
  CoverageByPortion,
  FloorScheduleRow,
  PreliminaryCapacityEstimate,
} from "../../../../../packages/contracts/generated/results";
import {
  NOT_AVAILABLE,
  RULES_NOT_REVIEWED_REASON,
  conditionList,
  displayQuantity,
  gapKindLine,
  quantityText,
  uniqueSections,
  type ThreeAnswersResults,
} from "./three-answers";
import { collectConditions } from "./presented-notices";

/**
 * The measurement-basis words shown beside the preliminary apartment size. They are tied to the
 * contract by a test (ruling V11 (11), DB-215 b): the words must appear in the results schema's
 * description of `apartment_size_sqft`. The schema reads "…apartment size on the HPD measurement
 * basis…", so this phrase is the shared wording, not an invented UI label.
 */
export const APARTMENT_SIZE_BASIS_NOTE = "on the HPD measurement basis";

const TWO_DP = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** A square-foot quantity in plain words, e.g. "6,716.67 sq ft" (never the raw unit code). */
export function sqft(value: number): string {
  return quantityText(displayQuantity(value, "square_feet"));
}

/** A feet quantity in plain words, e.g. "30 ft". */
export function feet(value: number): string {
  return quantityText(displayQuantity(value, "feet"));
}

/** A ratio as a whole-number percent, e.g. 1 -> "100%", 0.8 -> "80%". The coverage ratios of
 * ZR 23-362 read as percentages, never as the raw decimal; rounded so 0.8 x 100 never prints its
 * binary-float tail. */
export function percent(ratio: number): string {
  return `${Math.round(ratio * 100)}%`;
}

/** A number to exactly two decimals, e.g. 17.27 / 0.60 — used for the estimate's quotients and the
 * owner's preliminary share range, which are shown to two decimals and never rounded to a count. */
export function twoDp(value: number): string {
  return TWO_DP.format(value);
}

/** A storey count in plain words, e.g. "3 storeys", "1 storey". A count read from the document. */
export function storeyText(count: number): string {
  return `${count} ${count === 1 ? "storey" : "storeys"}`;
}

/** One storey of a worked building's floor schedule, each field in plain words. */
export interface FloorRowView {
  storey: number;
  floorToFloor: string;
  top: string;
  planArea: string;
  floorArea: string;
  runningTotal: string;
}

/** A worked building's own preliminary capacity estimate: either the two quotients across the
 * owner's preliminary share range (label "Preliminary capacity estimate"), or "Not known" with its
 * reason and NO number. The share and the apartment size are the owner's PRELIMINARY ASSUMPTIONS,
 * shown but not editable on this screen (ruling W7). */
export type CapacityView =
  | {
      kind: "known";
      label: string;
      floorArea: string;
      /** The two quotients to two decimals, never rounded to a count (D-090-R541). */
      low: string;
      high: string;
      /** The whole numbers just below the low quotient and just above the high quotient. */
      wholeBelowLow: number;
      wholeAboveHigh: number;
      /** The owner's preliminary share range and apartment size (preliminary assumptions, shown not
       * editable here — ruling W7). */
      shareLow: string;
      shareHigh: string;
      apartmentSize: string;
    }
  | { kind: "not_known"; label: string; reason: string };

/** Coverage by portion (ZR 23-362 / ZR 12-10). "available" carries the ratios, the 100 ft distance,
 * the two portion areas and the footprint figure; "withheld" carries NO number — its reason gives
 * the law by portion without a square-foot result (ruling W1, R556/R570). */
export type CoverageView =
  | {
      kind: "available";
      cornerRatio: string;
      interiorRatio: string;
      cornerDistance: string;
      cornerArea: string;
      interiorArea: string;
      footprint: string;
      zrSections: readonly string[];
      conditions: readonly string[];
    }
  | {
      kind: "withheld";
      label: string;
      reason: string;
      gapKindLine: string | null;
      resolvedBy: string;
      zrSections: readonly string[];
    };

/** One worked first-building alternative, read from the document; NONE is preferred (ruling W3). */
export interface BuildingAlternativeView {
  building: string;
  label: string;
  /** The sentence why the plan fits (contract 1.4.0 optional `fit_note`); null when absent. Shown as
   * plain text beside the building; it checks the plan against coverage only, not placement. */
  fitNote: string | null;
  floorSchedule: readonly FloorRowView[];
  storeyCount: number;
  height: string;
  footprint: string;
  totalFloorArea: string;
  unusedFloorArea: string;
  /** Each "If <assumption>" line of the alternative's `way`; empty when it is settled. Kept for the
   * record; NOT shown under the building option, which refers to the shared conditions by name. */
  conditions: readonly string[];
  /** The shared conditions this building refers to, BY NAME ("Condition 1", "Condition 2") in the
   * notices adapter's first-appearance order (ruling V11 (5)); the full text is stated once in the
   * shared-conditions card, never repeated here. Empty when the building is settled. */
  conditionRefs: readonly string[];
  isConditional: boolean;
  isWithheld: boolean;
  withheldReason: string | null;
  /** What was NOT checked for this alternative, plain words (ruling W5, R526/R548). */
  notChecked: readonly string[];
  capacity: CapacityView;
}

/** One building of the step-P6 method that was NOT worked, read from `buildings_not_worked` (ruling
 * W14/W15, the walkthrough F1): its label, why it was not worked and what would let it be worked, all
 * plain text from the document, plus the gap kind in plain words. NO number is a result here. */
export interface BuildingNotWorkedView {
  building: string;
  label: string;
  reason: string;
  resolvedBy: string;
  /** A short tag for a missing fact about the property ("Needs property information"), or null. There
   * is NO separate kind line for work owed (ruling V11 (3); one wording per situation, row R894). */
  propertyInfoTag: string | null;
}

/** The short tag a missing-property-fact gap carries (ruling V11 (3)); work-owed carries none. */
export const NEEDS_PROPERTY_INFO_TAG = "Needs property information";

/** The one wording for a building whose result is not available in the comparison — never a 0 and
 * never an empty cell (ruling V8; row R894, "one wording per situation"). */
export const COMPARISON_NOT_KNOWN = "Not known";

/**
 * One building shown as a column of the option comparison, side by side with the others on the same
 * metric rows and units. A worked building carries each metric, read from the document (ruling V2); a
 * not-worked building carries its reason and reads "Not known" for every metric (never 0, never an
 * empty cell — row R894). Nothing here is preferred: the owner's question A2 is open (row R894).
 */
export type ComparisonColumn =
  | {
      kind: "worked";
      building: string;
      label: string;
      /** "3 storeys". */
      storeys: string;
      /** "30 ft". */
      height: string;
      /** The scheduled area, never "achieved" (row R895): "20,150 sq ft". */
      scheduledArea: string;
      /** The footprint each storey rests on: "6,716.67 sq ft". */
      planPerStorey: string;
      /** "17.27 to 21.59 apartments", or the one not-known wording when the estimate is withheld. */
      estimate: string;
    }
  | {
      kind: "not_worked";
      building: string;
      label: string;
      /** Why this building was not worked, read from the document. */
      reason: string;
    };

/** The option comparison: the method's buildings side by side, in a stable order by building id. */
export interface BuildingOptionsComparisonView {
  columns: readonly ComparisonColumn[];
}

export interface FirstBuildingOptionsView {
  /** The document is a draft and this is an architect surface: the numbers are hidden and the
   * section shows only the one not-reviewed line (the same gate the three answer cards use). */
  draftHidden: boolean;
  draftHiddenText: string;
  alternatives: readonly BuildingAlternativeView[];
  /** The buildings of the method that were NOT worked, each with its reason (ruling W14/W15). When
   * `alternatives` is empty this is how the section says why nothing is shown (never an empty
   * heading, never a lead about worked shapes — the F1 fix). */
  notWorked: readonly BuildingNotWorkedView[];
  /** The method's buildings side by side (row R894), or null when fewer than two buildings exist. */
  comparison: BuildingOptionsComparisonView | null;
  coverage: CoverageView | null;
}

function floorRowView(row: FloorScheduleRow): FloorRowView {
  return {
    storey: row.storey,
    floorToFloor: feet(row.floor_to_floor_ft),
    top: feet(row.top_ft),
    planArea: sqft(row.plan_area_sqft),
    floorArea: sqft(row.floor_area_sqft),
    runningTotal: sqft(row.running_total_sqft),
  };
}

function capacityView(estimate: PreliminaryCapacityEstimate): CapacityView {
  if (estimate.label === "Preliminary capacity estimate") {
    return {
      kind: "known",
      label: estimate.label,
      floorArea: sqft(estimate.floor_area_sqft),
      low: twoDp(estimate.quotient_low),
      high: twoDp(estimate.quotient_high),
      wholeBelowLow: estimate.whole_below_low,
      wholeAboveHigh: estimate.whole_above_high,
      shareLow: twoDp(estimate.share_low),
      shareHigh: twoDp(estimate.share_high),
      apartmentSize: sqft(estimate.apartment_size_sqft),
    };
  }
  return { kind: "not_known", label: estimate.label, reason: estimate.reason };
}

function alternativeView(
  alternative: BuildingAlternative,
  conditionRefs: readonly string[],
): BuildingAlternativeView {
  const way = alternative.way;
  return {
    building: alternative.building,
    label: alternative.label,
    fitNote: alternative.fit_note ?? null,
    floorSchedule: alternative.floor_schedule.map(floorRowView),
    storeyCount: alternative.storey_count,
    height: feet(alternative.height_ft),
    footprint: sqft(alternative.footprint_area_sqft),
    totalFloorArea: sqft(alternative.total_floor_area_sqft),
    unusedFloorArea: sqft(alternative.unused_floor_area_sqft),
    conditions: conditionList(way),
    conditionRefs,
    isConditional: way.way === "conditional",
    isWithheld: way.way === "withheld",
    withheldReason: way.way === "withheld" ? way.reason : null,
    notChecked: alternative.not_checked,
    capacity: capacityView(alternative.capacity_estimate),
  };
}

/**
 * The shared conditions each building refers to, BY NAME ("Condition 1", …), in the notices adapter's
 * first-appearance order — the SAME order and numbering the shared-conditions card uses (ruling V11
 * (5)). The full text lives once in that card; this never repeats it. Returns a function from a
 * building id to its ordered condition names.
 */
function conditionRefsByBuilding(results: ThreeAnswersResults): (building: string) => string[] {
  const { shared, references } = collectConditions(results);
  const nameById = new Map(shared.map((condition, index) => [condition.id, `Condition ${index + 1}`]));
  const refsByResult = new Map(references.map(ref => [ref.resultId, ref.conditionIds]));
  return building => {
    const ids = refsByResult.get(`building_alternative.${building}`) ?? [];
    return ids.map(id => nameById.get(id)).filter((name): name is string => name !== undefined);
  };
}

function coverageView(coverage: CoverageByPortion): CoverageView {
  if (coverage.status === "available") {
    return {
      kind: "available",
      cornerRatio: percent(coverage.corner_ratio),
      interiorRatio: percent(coverage.interior_ratio),
      cornerDistance: feet(coverage.corner_lot_distance_ft),
      cornerArea: sqft(coverage.corner_portion_area_sqft),
      interiorArea: sqft(coverage.interior_portion_area_sqft),
      footprint: sqft(coverage.footprint_sqft),
      zrSections: uniqueSections(coverage.zr_sections),
      conditions: conditionList(coverage.way),
    };
  }
  return {
    kind: "withheld",
    label: coverage.label,
    reason: coverage.reason,
    gapKindLine: gapKindLine(coverage.gap_kind),
    resolvedBy: coverage.resolved_by,
    zrSections: uniqueSections(coverage.zr_sections),
  };
}

function notWorkedView(entry: BuildingNotWorked): BuildingNotWorkedView {
  return {
    building: entry.building,
    label: entry.label,
    reason: entry.reason,
    resolvedBy: entry.resolved_by,
    // Only a missing-property-fact carries a short tag; work-owed carries none — one wording per
    // situation, no second phrase such as "Not built yet" / "still owed" (ruling V11 (3)).
    propertyInfoTag: entry.gap_kind === "missing_information" ? NEEDS_PROPERTY_INFO_TAG : null,
  };
}

/** A worked building's estimate for the comparison: the two quotients across the owner's share range,
 * or the one not-known wording — read from the document, never recalculated (ruling V2). */
function comparisonEstimate(estimate: PreliminaryCapacityEstimate): string {
  if (estimate.label === "Preliminary capacity estimate") {
    return `${twoDp(estimate.quotient_low)} to ${twoDp(estimate.quotient_high)} apartments`;
  }
  return COMPARISON_NOT_KNOWN;
}

function workedColumn(alternative: BuildingAlternative): ComparisonColumn {
  return {
    kind: "worked",
    building: alternative.building,
    label: alternative.label,
    storeys: storeyText(alternative.storey_count),
    height: feet(alternative.height_ft),
    scheduledArea: sqft(alternative.total_floor_area_sqft),
    planPerStorey: sqft(alternative.footprint_area_sqft),
    estimate: comparisonEstimate(alternative.capacity_estimate),
  };
}

function notWorkedColumn(entry: BuildingNotWorked): ComparisonColumn {
  return { kind: "not_worked", building: entry.building, label: entry.label, reason: entry.reason };
}

/**
 * The option comparison for a results document: every building of the method (worked and not worked)
 * as one column, in a stable order by building id. Null unless at least one building is worked AND at
 * least two buildings exist in total — a comparison of one building is no comparison, and a set of
 * only not-worked buildings is already told by the not-worked blocks. Every value is read from the
 * document; a building that was not worked shows its reason and reads "Not known" for each metric —
 * never 0, never an empty cell (row R894). Question A2 is open: every building is shown, none is
 * preferred.
 */
export function buildingOptionsComparisonView(
  results: ThreeAnswersResults,
): BuildingOptionsComparisonView | null {
  const alternatives = Array.isArray(results.building_alternatives)
    ? results.building_alternatives
    : [];
  const notWorked = Array.isArray(results.buildings_not_worked) ? results.buildings_not_worked : [];
  const columns: ComparisonColumn[] = [
    ...alternatives.map(workedColumn),
    ...notWorked.map(notWorkedColumn),
  ].sort((a, b) => a.building.localeCompare(b.building));
  if (alternatives.length === 0 || columns.length < 2) return null;
  return { columns };
}

/**
 * The first-building-options section of a results document (results contract 1.4.0), or null when
 * the document carries no `building_alternatives` list, no `coverage_by_portion` block AND no
 * `buildings_not_worked` list — so every 1.0.0–1.3.0 document renders exactly as before (the panel
 * adds nothing). Every value is read from the document; a withheld result carries no number and no
 * substitute. When `alternatives` is empty but `notWorked` is not, the section still renders (it says
 * why each building was not worked — the F1 fix), never an empty heading.
 */
export function firstBuildingOptionsView(
  results: ThreeAnswersResults,
  showDraftValues: boolean,
): FirstBuildingOptionsView | null {
  const alternatives = Array.isArray(results.building_alternatives)
    ? results.building_alternatives
    : [];
  const notWorked = Array.isArray(results.buildings_not_worked)
    ? results.buildings_not_worked
    : [];
  const coverage = results.coverage_by_portion ?? null;
  if (alternatives.length === 0 && coverage === null && notWorked.length === 0) return null;

  const refsFor = conditionRefsByBuilding(results);
  return {
    draftHidden: results.draft && !showDraftValues,
    draftHiddenText: `${NOT_AVAILABLE} — ${RULES_NOT_REVIEWED_REASON}`,
    alternatives: alternatives.map(alternative => alternativeView(alternative, refsFor(alternative.building))),
    notWorked: notWorked.map(notWorkedView),
    comparison: buildingOptionsComparisonView(results),
    coverage: coverage ? coverageView(coverage) : null,
  };
}
