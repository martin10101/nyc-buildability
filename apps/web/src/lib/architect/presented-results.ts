// Presentation adapter: each document result tagged with its kind, in the reading order the owner's
// contract sets (M5-T148 part B; presentation contract §4 "label → value and unit, or unavailable
// state → material exception → details action", §8 the PresentedMetric sketch). A THIN layer over
// the generated results contract — not a competing schema. Pure. It decides no law and recalculates
// nothing (ruling V2, D-090-R855): every value, label, unit, exception and condition is READ from
// the document and only formatted or grouped. A withheld value carries NO number (ruling V8).
//
// Result kinds (presentation contract §6 "Allowance and achieved area must have distinct labels"):
//  - allowance  — the floor-area-allowance values AND the withheld unit limits beside them.
//  - envelope   — the permitted-envelope heights and the withheld envelope items beside them.
//  - scheduled  — a listed building option's SCHEDULED area. NEVER "achieved": a floor schedule whose
//                 placement and site fit are not established is the "scheduled area", with
//                 "Site fit not verified" beside it (ruling V5, D-090-R895). There is deliberately no
//                 "achieved" kind. A building's own label is READ from the document verbatim, as the
//                 three-answers panel already does; the kind this adapter assigns is "scheduled".
//  - estimate   — a worked building's preliminary capacity estimate, kept separate as an estimate.

import type { AnswerKey, ThreeAnswersResults } from "./three-answers";
import type {
  BuildingAlternative,
  ExceptionLabel,
  ValueState,
} from "../../../../../packages/contracts/generated/results";
import { twoDp } from "./first-building-options";
import { METRIC_NOT_KNOWN, formatMetric, type FormattedMetric } from "./metric-format";
import { STATUS_NOT_KNOWN, presentStatus, type PresentedStatus } from "./result-status";

export type ResultKind = "allowance" | "envelope" | "scheduled" | "estimate";

/** Shown beside a scheduled option's area — the option is never called "achieved" (ruling V5). */
export const SITE_FIT_NOT_VERIFIED = "Site fit not verified";

/** The report's own suffix for a scheduled option whose placement and site fit are not established
 * (D-090 source-081, ruling X5): "site fit unverified" — lowercase, as it reads inside the one-line
 * phrase. Distinct from SITE_FIT_NOT_VERIFIED, which stands alone as a note elsewhere. */
export const SITE_FIT_UNVERIFIED = "site fit unverified";

/**
 * The ONE-LINE scheduled phrase the report and the website share (ruling X5; scenario S1):
 * "Scheduled floor area: N sq ft; site fit unverified", where the figure is already formatted by
 * the metric adapter (e.g. "20,150 sq ft"). Never "achieved", never "no allowance left unused".
 * The figure is READ from the document; this helper only joins it to the fixed wording (ruling X7).
 */
export function scheduledFloorAreaLine(areaText: string): string {
  return `Scheduled floor area: ${areaText}; ${SITE_FIT_UNVERIFIED}`;
}

/** A result's value for reading: a formatted value (or range), or the not-known state with no digit. */
export type PresentedValue =
  | { kind: "value"; text: string }
  | { kind: "not_known"; text: string };

/**
 * One presented result, its fields in the contract's reading order: `label`, then `display` (a value
 * or the unavailable state), then `exception` (one material exception), then `detailsKey` (the
 * evidence surface to open). `resultKind` tags what the result is; `status` is the owner's status
 * word; `note` is a scheduled option's "Site fit not verified", else null.
 */
export interface PresentedResult {
  /** A stable id matching presented-notices' resultId, e.g. "permitted_envelope.max_building_height". */
  id: string;
  resultKind: ResultKind;
  /** Plain label, read from the document verbatim. */
  label: string;
  display: PresentedValue;
  status: PresentedStatus;
  /** One material exception label from the document (e.g. "With approvals"), or null. */
  exception: ExceptionLabel;
  /** "Site fit not verified" for a scheduled option, else null. */
  note: string | null;
  /** The evidence surface this result opens (same stable key as `id`). */
  detailsKey: string;
}

const NOT_KNOWN_DISPLAY: PresentedValue = { kind: "not_known", text: METRIC_NOT_KNOWN };

function toDisplay(metric: FormattedMetric): PresentedValue {
  return metric.kind === "value"
    ? { kind: "value", text: metric.text }
    : { kind: "not_known", text: metric.text };
}

function valueStates(answer: ThreeAnswersResults["answers"][AnswerKey]): Record<string, ValueState> {
  if (answer.status !== "available") return {};
  const states = answer.value_states;
  return states ? (states as Record<string, ValueState>) : {};
}

// The shown values of an answer, plus the withheld value_states beside them (each shown as its
// reason, never a number — the same split the three-answers panel makes).
function answerResults(
  results: ThreeAnswersResults,
  key: AnswerKey,
  kind: ResultKind,
): PresentedResult[] {
  const answer = results.answers[key];
  if (answer.status !== "available") return [];
  const states = valueStates(answer);
  const shownKeys = new Set(answer.values.map(value => value.key));
  const out: PresentedResult[] = [];

  for (const value of answer.values) {
    out.push({
      id: `${key}.${value.key}`,
      resultKind: kind,
      label: value.label,
      display: toDisplay(formatMetric(value.value, value.unit)),
      status: presentStatus(states[value.key]),
      exception: value.exception_label,
      note: kind === "scheduled" ? SITE_FIT_NOT_VERIFIED : null,
      detailsKey: `${key}.${value.key}`,
    });
  }

  for (const [stateKey, state] of Object.entries(states)) {
    if (state.way === "withheld" && !shownKeys.has(stateKey)) {
      out.push({
        id: `${key}.${stateKey}`,
        resultKind: kind,
        label: state.label,
        display: NOT_KNOWN_DISPLAY,
        status: presentStatus(state),
        exception: null,
        note: null,
        detailsKey: `${key}.${stateKey}`,
      });
    }
  }
  return out;
}

// A worked alternative's scheduled area, and its own preliminary capacity estimate (kind "estimate").
function alternativeResults(alternative: BuildingAlternative): PresentedResult[] {
  const way = alternative.way;
  const scheduled: PresentedResult = {
    id: `building_alternative.${alternative.building}`,
    resultKind: "scheduled",
    label: alternative.label,
    display:
      way.way === "withheld"
        ? NOT_KNOWN_DISPLAY
        : toDisplay(formatMetric(alternative.total_floor_area_sqft, "square_feet")),
    status: presentStatus(way),
    exception: null,
    note: SITE_FIT_NOT_VERIFIED,
    detailsKey: `building_alternative.${alternative.building}`,
  };

  const estimate = alternative.capacity_estimate;
  const estimateBase = {
    id: `building_alternative.${alternative.building}.capacity`,
    resultKind: "estimate" as const,
    exception: null,
    note: null,
    detailsKey: `building_alternative.${alternative.building}.capacity`,
  };
  const capacity: PresentedResult =
    estimate.label === "Preliminary capacity estimate"
      ? {
          ...estimateBase,
          label: estimate.label,
          display: { kind: "value", text: `${twoDp(estimate.quotient_low)} to ${twoDp(estimate.quotient_high)}` },
          status: { kind: "settled" },
        }
      : {
          ...estimateBase,
          label: estimate.label,
          display: NOT_KNOWN_DISPLAY,
          status: { kind: "not_known", label: STATUS_NOT_KNOWN, reason: estimate.reason },
        };

  return [scheduled, capacity];
}

/**
 * Every result of the document, each tagged with its kind, in the reading order the contract sets.
 * Allowance first, then envelope, then each listed building's scheduled option and its estimate.
 * A withheld value carries no number; a scheduled option is never "achieved". A 1.0.0–1.3.0 document
 * with no building alternatives simply yields no scheduled/estimate rows from that source.
 */
export function presentedResults(results: ThreeAnswersResults): PresentedResult[] {
  return [
    ...answerResults(results, "floor_area_allowance", "allowance"),
    ...answerResults(results, "permitted_envelope", "envelope"),
    ...answerResults(results, "building_option", "scheduled"),
    ...(results.building_alternatives ?? []).flatMap(alternativeResults),
  ];
}
