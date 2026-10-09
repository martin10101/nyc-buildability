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
  /** Each "If <assumption>" line of the alternative's `way`; empty when it is settled. */
  conditions: readonly string[];
  isConditional: boolean;
  isWithheld: boolean;
  withheldReason: string | null;
  /** What was NOT checked for this alternative, plain words (ruling W5, R526/R548). */
  notChecked: readonly string[];
  capacity: CapacityView;
}

export interface FirstBuildingOptionsView {
  /** The document is a draft and this is an architect surface: the numbers are hidden and the
   * section shows only the one not-reviewed line (the same gate the three answer cards use). */
  draftHidden: boolean;
  draftHiddenText: string;
  alternatives: readonly BuildingAlternativeView[];
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

function alternativeView(alternative: BuildingAlternative): BuildingAlternativeView {
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
    isConditional: way.way === "conditional",
    isWithheld: way.way === "withheld",
    withheldReason: way.way === "withheld" ? way.reason : null,
    notChecked: alternative.not_checked,
    capacity: capacityView(alternative.capacity_estimate),
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

/**
 * The first-building-options section of a results document (results contract 1.4.0), or null when
 * the document carries neither a `building_alternatives` list nor a `coverage_by_portion` block — so
 * every 1.0.0–1.3.0 document renders exactly as before (the panel adds nothing). Every value is read
 * from the document; a withheld result carries no number and no substitute.
 */
export function firstBuildingOptionsView(
  results: ThreeAnswersResults,
  showDraftValues: boolean,
): FirstBuildingOptionsView | null {
  const alternatives = Array.isArray(results.building_alternatives)
    ? results.building_alternatives
    : [];
  const coverage = results.coverage_by_portion ?? null;
  if (alternatives.length === 0 && coverage === null) return null;

  return {
    draftHidden: results.draft && !showDraftValues,
    draftHiddenText: `${NOT_AVAILABLE} — ${RULES_NOT_REVIEWED_REASON}`,
    alternatives: alternatives.map(alternativeView),
    coverage: coverage ? coverageView(coverage) : null,
  };
}
