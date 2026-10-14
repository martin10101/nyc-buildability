// Page-1 parity: the legal ceiling beside the apartment estimate (M5-T171; D-094 R041/R057).
//
// Pure functions over one `results` document — no fetching, no legal logic, no arithmetic on the
// numbers. Every figure is READ from the document and only FORMATTED for reading, exactly as
// report page 1 reads it (services/api/app/drawings/report/page_decision_summary.py,
// unit_limit_text.py, readers.py, formatting.py). This module invents no value: where the document
// carries no legal unit limit or no capacity estimate the block shows no figure and says so; the 29
// is never shown as settled. The distinction line is a LITERAL here whose unit test compares it
// character-for-character with docs/design/presentation-tokens.json wording.ceiling_estimate_distinction.

import type {
  AnswerValue,
  BuildingAlternative,
  PreliminaryCapacityEstimate,
  ValueCondition,
  ValueState,
} from "../../../../../packages/contracts/generated/results";

// Re-exported so the component and the block's tests import the contract value-state type from one
// place (three-answers.ts, which is read-only here, does not re-export it).
export type { ValueState } from "../../../../../packages/contracts/generated/results";
import {
  ANSWER_KEYS,
  NOT_AVAILABLE,
  RULES_NOT_REVIEWED_REASON,
  type AnswerKey,
  type ThreeAnswersResults,
} from "./three-answers";

/**
 * The distinction line, a literal held here and byte-identical to report page 1's
 * WORDING["ceiling_estimate_distinction"]. The S1 unit test reads
 * docs/design/presentation-tokens.json from disk and compares it character for character, so a
 * silent drift between the website and the PDF fails closed.
 */
export const CEILING_ESTIMATE_DISTINCTION =
  "The ceiling is a conditional zoning limit; the estimate is an unvalidated apartment-yield " +
  "range; neither is a demonstrated layout.";

/** The plain line shown when the whole block is behind the draft gate (D-090-R010): the numbers
 * are computed from rules that are not reviewed yet, so no figure is shown on an architect surface. */
export const DRAFT_GATED_LINE = `${NOT_AVAILABLE} — ${RULES_NOT_REVIEWED_REASON}`;

/** The plain line shown when the document carries no legal dwelling-unit ceiling at all. */
export const CEILING_NOT_AVAILABLE = "Legal ceiling not available";

/** The plain line shown when the document carries no readable apartment-estimate range. */
export const ESTIMATE_NOT_AVAILABLE = "Apartment estimate not available";

/** The generic lot-area basis line report page 1 falls back to when the recorded area, the FAR or
 * the tax lot is absent from the document (page_decision_summary._floor_area_basis). */
export const LOT_AREA_BASIS_FALLBACK = "Residential FAR on the recorded lot area";

// The six status labels, byte-identical to the report (services/api/app/drawings/report/labels.py).
const PROVISIONAL = "Provisional";
const CONDITIONAL = "Conditional";
const PENDING_VERIFICATION = "Pending verification";
const UNRESOLVED = "Unresolved";

// The document key for the standard-residence legal dwelling-unit limit (the page-1 legal ceiling),
// the same key unit_limit_text._STANDARD_LIMIT_KEY reads.
const STANDARD_LIMIT_KEY = "legal_unit_limit_standard";
const MAX_RESIDENTIAL_FAR_KEY = "max_residential_far";
// A phrase that appears ONLY in the ACRIS zoning-lot-index condition, matching the report's
// zoning_lot_item._ZONING_LOT_CONDITION_MARKER, so the zoning-lot concern is never confused with a
// generic zoning-lot condition or any other condition.
const ZONING_LOT_CONDITION_MARKER = "register of recorded documents";

// ---- Figure formatting, byte-identical to services/api/app/drawings/report/formatting.py ----

function asFiniteNumber(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return value;
}

/** A whole number grouped with commas (29 -> "29", 20150 -> "20,150"); a fractional value keeps two
 * decimals (format_int_commas). */
export function formatIntCommas(value: unknown): string | null {
  const number = asFiniteNumber(value);
  if (number === null) return null;
  if (number === Math.trunc(number)) return Math.trunc(number).toLocaleString("en-US");
  return number.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** A floor-area ratio with at least one decimal (2.0 -> "2.0", 2.4 -> "2.4"; format_ratio). */
export function formatRatio(value: unknown): string | null {
  const number = asFiniteNumber(value);
  if (number === null) return null;
  let text = number.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
  if (!text.includes(".")) text += ".0";
  return text;
}

/** One answer value formatted by its document unit, matching report formatting.format_measure: a
 * known unit uses its formatter, any other unit (dwelling_units included) is a grouped number with
 * no unit — exactly how the report shows the legal ceiling ("29"). */
export function formatMeasure(value: unknown, unit: string): string | null {
  if (unit === "square_feet") {
    const grouped = formatIntCommas(value);
    return grouped === null ? null : `${grouped} sq ft`;
  }
  if (unit === "ratio") return formatRatio(value);
  if (unit === "feet") {
    const grouped = formatIntCommas(value);
    return grouped === null ? null : `${grouped} ft`;
  }
  if (unit === "degrees") {
    const grouped = formatIntCommas(value);
    return grouped === null ? null : `${grouped} degrees`;
  }
  return formatIntCommas(value);
}

// ---- Reading the document (the three answers, then the building alternatives) ----

function availableAnswer(
  results: ThreeAnswersResults,
  key: AnswerKey,
): { values: AnswerValue[]; states: Record<string, ValueState> } | null {
  const answer = results.answers[key];
  if (answer.status !== "available") return null;
  const states = answer.value_states ? (answer.value_states as Record<string, ValueState>) : {};
  return { values: answer.values, states };
}

/** The conditions a shown value rests on, or an empty list (a settled or stateless value has none).
 * Mirrors the report's present_values: a value whose state way is "withheld" is never a shown value. */
function shownValueConditions(state: ValueState | undefined): ValueCondition[] {
  if (state && state.way === "conditional") return state.conditions;
  return [];
}

/** A status label for a value's `way`, byte-identical to labels._from_way_token (a settled value is
 * Provisional; a conditional value is Conditional; an absent state is Provisional, as the report's
 * present_values defaults). A withheld state is handled by {@link labelForWithheld}. */
function labelForWay(state: ValueState | undefined): string {
  if (!state) return PROVISIONAL;
  if (state.way === "settled") return PROVISIONAL;
  if (state.way === "conditional") return CONDITIONAL;
  return PENDING_VERIFICATION;
}

/** A status label for a withheld value, byte-identical to labels.label_for_value_state: a missing
 * fact is Unresolved; anything else (work owed) is Pending verification. */
function labelForWithheld(state: Extract<ValueState, { way: "withheld" }>): string {
  return state.gap_kind === "missing_information" ? UNRESOLVED : PENDING_VERIFICATION;
}

export type LegalCeiling =
  | { kind: "value"; figure: string; label: string }
  | { kind: "withheld"; reason: string; label: string }
  | { kind: "none" };

/**
 * The standard-residence legal dwelling-unit ceiling for the page-1 block, read only from the
 * document (unit_limit_text.legal_ceiling). A shown ceiling is its formatted figure with its own
 * state label (a conditional ceiling is Conditional, never settled); a withheld ceiling is its
 * document reason with its label and no figure; an absent ceiling is {kind:"none"} — no invented value.
 */
export function legalCeiling(results: ThreeAnswersResults): LegalCeiling {
  for (const key of ANSWER_KEYS) {
    const answer = availableAnswer(results, key);
    if (!answer) continue;
    for (const value of answer.values) {
      if (value.key !== STANDARD_LIMIT_KEY) continue;
      const state = answer.states[value.key];
      if (state && state.way === "withheld") continue; // not a shown value
      const figure = formatMeasure(value.value, value.unit);
      if (figure === null) continue;
      return { kind: "value", figure, label: labelForWay(state) };
    }
  }
  for (const key of ANSWER_KEYS) {
    const answer = availableAnswer(results, key);
    if (!answer) continue;
    const shownKeys = new Set(answer.values.map(value => value.key));
    const state = answer.states[STANDARD_LIMIT_KEY];
    if (state && state.way === "withheld" && !shownKeys.has(STANDARD_LIMIT_KEY)) {
      return { kind: "withheld", reason: state.reason, label: labelForWithheld(state) };
    }
  }
  return { kind: "none" };
}

function firstCapacityEstimate(results: ThreeAnswersResults): PreliminaryCapacityEstimate | null {
  const alternatives = results.building_alternatives as BuildingAlternative[] | null | undefined;
  const first = Array.isArray(alternatives) ? alternatives[0] : undefined;
  return first ? first.capacity_estimate : null;
}

/**
 * The first building alternative's preliminary apartment-estimate range as "low-high" (e.g. "17-22"),
 * read from the document (readers.apartment_estimate_range): both bounds come from the document and
 * none is retyped. `null` when there is no alternative, no ranged estimate, or a bound is absent.
 */
export function apartmentEstimateRange(results: ThreeAnswersResults): string | null {
  const estimate = firstCapacityEstimate(results);
  if (!estimate || !("whole_below_low" in estimate)) return null;
  const low = formatIntCommas(estimate.whole_below_low);
  const high = formatIntCommas(estimate.whole_above_high);
  if (low === null || high === null) return null;
  return `${low}-${high}`;
}

/** The (assumption) text of the ACRIS zoning-lot-index condition carried on a shown figure (or a
 * building alternative's way), or `null` when no figure carries it. Detected by the marker phrase so
 * it is never confused with another condition (zoning_lot_item.zoning_lot_basis). `null` means the
 * figures are not conditional on the recorded-document index, so the lot is not flagged unconfirmed. */
export function zoningLotConcern(results: ThreeAnswersResults): string | null {
  const match = (conditions: ValueCondition[]): string | null => {
    for (const condition of conditions) {
      if (
        condition.kind === "unchecked_condition" &&
        condition.assumption.includes(ZONING_LOT_CONDITION_MARKER)
      ) {
        return condition.assumption;
      }
    }
    return null;
  };
  for (const key of ANSWER_KEYS) {
    const answer = availableAnswer(results, key);
    if (!answer) continue;
    for (const value of answer.values) {
      const state = answer.states[value.key];
      if (state && state.way === "withheld") continue;
      const hit = match(shownValueConditions(state));
      if (hit !== null) return hit;
    }
  }
  for (const alternative of (results.building_alternatives as BuildingAlternative[] | null) ?? []) {
    const hit = match(shownValueConditions(alternative.way));
    if (hit !== null) return hit;
  }
  return null;
}

/** The recorded lot-area figure, read from the first `contradicted_record` condition's own sentence
 * (readers.lot_area_basis + recorded_lot_area_text) — never retyped. `null` when no figure carries
 * that condition or the sentence does not name a recorded area. */
export function recordedLotAreaText(results: ThreeAnswersResults): string | null {
  const firstContradictedRecord = (): string | null => {
    for (const key of ANSWER_KEYS) {
      const answer = availableAnswer(results, key);
      if (!answer) continue;
      for (const value of answer.values) {
        const state = answer.states[value.key];
        if (state && state.way === "withheld") continue;
        for (const condition of shownValueConditions(state)) {
          if (condition.kind === "contradicted_record") return condition.assumption;
        }
      }
    }
    for (const alternative of (results.building_alternatives as BuildingAlternative[] | null) ?? []) {
      for (const condition of shownValueConditions(alternative.way)) {
        if (condition.kind === "contradicted_record") return condition.assumption;
      }
    }
    return null;
  };
  const basis = firstContradictedRecord();
  if (basis === null) return null;
  const match = /recorded lot area of ([\d,]+) sq ft/.exec(basis);
  return match ? `${match[1]} sq ft` : null;
}

/** The shown (non-withheld) maximum residential FAR figure from the floor-area allowance, formatted
 * as the report formats it (format_ratio via named_value). `null` when it is absent or withheld. */
function shownResidentialFar(results: ThreeAnswersResults): string | null {
  const answer = availableAnswer(results, "floor_area_allowance");
  if (!answer) return null;
  for (const value of answer.values) {
    if (value.key !== MAX_RESIDENTIAL_FAR_KEY) continue;
    const state = answer.states[value.key];
    if (state && state.way === "withheld") continue;
    return formatMeasure(value.value, value.unit);
  }
  return null;
}

/**
 * The R055 lot-area assumption line, composed exactly as report page 1 composes it
 * (page_decision_summary._floor_area_basis): "<recorded> recorded lot area × FAR <far>, tax lot
 * <lot>[ alone]" — the × is U+00D7 and "alone" is added only while the zoning lot is unconfirmed.
 * Every value is read from the document; when the recorded area, the FAR or the tax lot is absent the
 * report's generic basis line is used, byte-identical to page 1.
 */
export function lotAreaBasisLine(results: ThreeAnswersResults): string {
  const recorded = recordedLotAreaText(results);
  const far = shownResidentialFar(results);
  const lot = results.scope?.lot.lot;
  if (!recorded || !far || !lot) return LOT_AREA_BASIS_FALLBACK;
  const unconfirmed = zoningLotConcern(results) !== null;
  const taxClause = unconfirmed ? `tax lot ${lot} alone` : `tax lot ${lot}`;
  return `${recorded} recorded lot area × FAR ${far}, ${taxClause}`;
}

export type ApartmentEstimateView =
  | { kind: "value"; figure: string; label: string }
  | { kind: "none" };

export interface ApartmentFiguresView {
  /** True when the block is behind the draft gate (D-090-R010): the figures are hidden on an
   * architect surface, and only {@link DRAFT_GATED_LINE} is shown. */
  draftGated: boolean;
  ceiling: LegalCeiling;
  estimate: ApartmentEstimateView;
  distinction: string;
  lotArea: string;
  /** The document's own zoning-lot concern sentence, shown only while the lot is unconfirmed; `null`
   * otherwise. Never invented — read straight from the document's condition. */
  zoningLotConcern: string | null;
}

/**
 * The page-1 parity block's view model, assembled from the document. `showDraftValues` carries the
 * panel's draft gate: a draft document on an architect surface (the flag off) hides every figure,
 * exactly as the answer cards do, so an unreviewed number never reaches an architect (D-090-R010).
 */
export function apartmentFiguresView(
  results: ThreeAnswersResults,
  showDraftValues: boolean,
): ApartmentFiguresView {
  const draftGated = results.draft === true && !showDraftValues;
  const estimateRange = apartmentEstimateRange(results);
  const estimate: ApartmentEstimateView =
    estimateRange === null
      ? { kind: "none" }
      : { kind: "value", figure: `Estimate ${estimateRange}`, label: PROVISIONAL };
  return {
    draftGated,
    ceiling: legalCeiling(results),
    estimate,
    distinction: CEILING_ESTIMATE_DISTINCTION,
    lotArea: lotAreaBasisLine(results),
    zoningLotConcern: zoningLotConcern(results),
  };
}
