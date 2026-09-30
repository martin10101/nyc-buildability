// Display rules for the three-answers panel (queue D-05; plan §5 "Three separate answers" and
// "Calculation behavior", §5a "Label on the box"). Pure functions over a `results` document:
// no fetching, no legal logic, no arithmetic on the numbers — values, units, rule sections and
// reasons are read from the document and only formatted for reading.
//
// Plan §5: each answer is shown only when its rules are implemented and reviewed, eligibility is
// resolved and the site geometry is supported; otherwise it shows "Not available" with the
// reason, and a caution label never turns an unsupported number into a result.
//
// Draft rules (schema `draft`, D-090-R010): while ANY rule version used is not published, a
// surface shown to an architect renders every available answer as not available ("rules not
// reviewed"). Only a surface behind a lane flag may pass `showDraftValues` to see the numbers.

import type {
  AnswerValue,
  ExceptionLabel,
  Results,
  StreetWidthCase,
  Unit,
} from "../../../../../packages/contracts/generated/results";

// The canonical generated contract types (packages/contracts/generated/results.ts, task C-03),
// re-exported so the panel and its tests import them from one place.
export type { AnswerValue, ExceptionLabel, Results, Unit };

/**
 * The part of a `results` document the panel reads, derived from the generated `Results` type
 * so the compiler keeps it in step with the contract. A full `Results` document is accepted.
 */
export type ThreeAnswersResults = Pick<
  Results,
  | "out_of_date"
  | "out_of_date_reason"
  | "lot_selection_statement"
  | "with_approvals_label"
  | "answers"
  | "remaining_floor_area"
  | "shortfall"
  | "completeness_line"
  | "status_strip"
  | "notices_count"
  | "draft"
  | "street_width_case"
>;

export type AnswerKey = keyof ThreeAnswersResults["answers"];

/** The three answers, in the plan's order (§3 step 5, §5). */
export const ANSWER_KEYS: readonly AnswerKey[] = [
  "floor_area_allowance",
  "permitted_envelope",
  "building_option",
];

export const ANSWER_TITLES: Readonly<Record<AnswerKey, string>> = {
  floor_area_allowance: "Floor-area allowance",
  permitted_envelope: "Permitted envelope",
  building_option: "Building option",
};

export const NOT_AVAILABLE = "Not available";

/** Reason shown for an available answer computed from rules that are not reviewed yet. */
export const RULES_NOT_REVIEWED_REASON = "the rules for this answer are not reviewed yet";

/** Heading tag on a lane-flag surface that shows draft numbers (never an architect surface). */
export const DRAFT_PREVIEW_TAG = "internal preview, rules not reviewed";

/** Reason shown if an available answer arrives without any value (the contract forbids it). */
export const NO_VALUE_REASON = "no value was returned for this answer";

/** Row label for the allowance left after a kept building (plan §3 step 4). */
export const REMAINING_LABEL = "Remaining after the existing building";

/** Row label for a building option's gap to the allowance (plan §5 answer 3). */
export const SHORTFALL_LABEL = "Gap to the allowance";

export const REACHES_ALLOWANCE_TEXT = "Reaches the full floor-area allowance.";

/** Plan §5a item 1: the status strip shows at most three short items. */
export const STRIP_MAX_ITEMS = 3;

// Leading words of a reason that only repeat the title the card already shows, e.g. the plan's
// own example "Envelope not available — height rules for this district are not built yet" under
// the "Permitted envelope" heading. Only these exact leads are dropped; any other reason is kept
// word for word after "Not available — ".
type ReasonSubject = AnswerKey | "remaining_floor_area" | "shortfall";
const REASON_SUBJECTS: Readonly<Record<ReasonSubject, readonly string[]>> = {
  floor_area_allowance: ["floor-area allowance", "floor area allowance", "allowance"],
  permitted_envelope: ["permitted envelope", "envelope"],
  building_option: ["building option", "option"],
  remaining_floor_area: ["remaining floor area", "remaining capacity"],
  shortfall: ["shortfall", "gap to the allowance"],
};

const SEPARATOR = /^\s*[—–-]\s*/;

/**
 * "Not available — <reason>" (plan §5, §5a item 3). A lead of "Not available —" or
 * "<this answer's subject> not available —" already in the reason is not repeated.
 */
export function notAvailableText(reason: string, subject?: ReasonSubject): string {
  const trimmed = reason.trim();
  const lower = trimmed.toLowerCase();
  const subjects: readonly string[] = subject ? REASON_SUBJECTS[subject] : [];
  const leads = [...subjects.map(s => `${s} not available`), "not available"].sort(
    (a, b) => b.length - a.length,
  );
  for (const lead of leads) {
    if (!lower.startsWith(lead)) continue;
    const after = trimmed.slice(lead.length);
    if (/^\s*[.:]?\s*$/.test(after)) return NOT_AVAILABLE;
    const separator = SEPARATOR.exec(after);
    if (separator) return `${NOT_AVAILABLE} — ${after.slice(separator[0].length)}`;
  }
  return trimmed === "" ? NOT_AVAILABLE : `${NOT_AVAILABLE} — ${trimmed}`;
}

/** A number and its plain-English unit, kept apart so a headline can size them differently. */
export interface DisplayQuantity {
  number: string;
  unit: string;
}

const PLAIN_NUMBER = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });
const RATIO_NUMBER = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 3,
});

/** Formats a contract value for reading. Never shows the raw unit code (plan §5a item 5). */
export function displayQuantity(value: number, unit: Unit): DisplayQuantity {
  const number = PLAIN_NUMBER.format(value);
  switch (unit) {
    case "square_feet":
      return { number, unit: "sq ft" };
    case "feet":
      return { number, unit: "ft" };
    case "ratio":
      return { number: RATIO_NUMBER.format(value), unit: "" };
    case "percent":
      return { number, unit: "%" };
    case "stories":
      return { number, unit: value === 1 ? "floor" : "floors" };
    case "dwelling_units":
      return { number, unit: value === 1 ? "unit" : "units" };
    case "square_feet_per_dwelling_unit":
      return { number, unit: "sq ft per unit" };
    default:
      // A unit added to the contract later shows the bare number, never its code.
      return { number, unit: "" };
  }
}

/** One-line text of a quantity, e.g. "10,000 sq ft", "100%", "2.0". */
export function quantityText(quantity: DisplayQuantity): string {
  if (quantity.unit === "") return quantity.number;
  if (quantity.unit === "%") return `${quantity.number}%`;
  return `${quantity.number} ${quantity.unit}`;
}

// The contract's stable value keys (schema answer_value.key: "e.g. max_residential_floor_area,
// max_building_height, achieved_zoning_floor_area") picked as each answer's large number. When
// the key is absent the answer's first value is the headline. Every value is still shown.
const HEADLINE_KEYS: Readonly<Record<AnswerKey, string>> = {
  floor_area_allowance: "max_residential_floor_area",
  permitted_envelope: "max_building_height",
  building_option: "achieved_zoning_floor_area",
};

export type AnswerView =
  | {
      kind: "available";
      headline: AnswerValue;
      rows: readonly AnswerValue[];
      measurementLabel: string;
    }
  | { kind: "not_available"; text: string };

export function answerView(
  results: ThreeAnswersResults,
  key: AnswerKey,
  showDraftValues: boolean,
): AnswerView {
  const answer = results.answers[key];
  if (answer.status !== "available") {
    return { kind: "not_available", text: notAvailableText(answer.reason, key) };
  }
  if (results.draft && !showDraftValues) {
    return { kind: "not_available", text: `${NOT_AVAILABLE} — ${RULES_NOT_REVIEWED_REASON}` };
  }
  const values = answer.values;
  if (values.length === 0) {
    return { kind: "not_available", text: `${NOT_AVAILABLE} — ${NO_VALUE_REASON}` };
  }
  const headline = values.find(value => value.key === HEADLINE_KEYS[key]) ?? values[0];
  return {
    kind: "available",
    headline,
    rows: values.filter(value => value !== headline),
    measurementLabel: answer.measurement.label,
  };
}

/** Rule sections of one value, each once, in document order. */
export function uniqueSections(sections: readonly string[]): string[] {
  return sections.filter((section, index) => sections.indexOf(section) === index);
}

export type SupplementView =
  | { kind: "value"; label: string; quantity: DisplayQuantity }
  | { kind: "not_available"; label: string; text: string };

/**
 * The allowance left after a kept building (plan §3 step 4). null when no building is kept.
 * Read only while the allowance itself is shown.
 */
export function remainingFloorAreaView(results: ThreeAnswersResults): SupplementView | null {
  const remaining = results.remaining_floor_area;
  if (remaining.status === "available") {
    return {
      kind: "value",
      label: REMAINING_LABEL,
      quantity: displayQuantity(remaining.value_sf, "square_feet"),
    };
  }
  if (remaining.status === "not_available") {
    return {
      kind: "not_available",
      label: REMAINING_LABEL,
      text: notAvailableText(remaining.reason, "remaining_floor_area"),
    };
  }
  return null;
}

export type ShortfallView =
  | { kind: "reaches_allowance" }
  | { kind: "shortfall"; amount: DisplayQuantity; reasons: readonly string[] }
  | { kind: "not_available"; label: string; text: string };

/**
 * How much of the allowance the building option reaches, and why not all of it (plan §5
 * answer 3). Read only while the building option itself is shown.
 */
export function shortfallView(results: ThreeAnswersResults): ShortfallView {
  const shortfall = results.shortfall;
  if (shortfall.status === "none") return { kind: "reaches_allowance" };
  if (shortfall.status === "shortfall") {
    return {
      kind: "shortfall",
      amount: displayQuantity(shortfall.sq_ft, "square_feet"),
      reasons: shortfall.reasons.map(reason => reason.text),
    };
  }
  return {
    kind: "not_available",
    label: SHORTFALL_LABEL,
    text: notAvailableText(shortfall.reason, "shortfall"),
  };
}

/** The strip's items: at most three on the line; anything more goes behind it (plan §5a 1, 6). */
export function statusStripItems(results: ThreeAnswersResults): {
  visible: readonly string[];
  overflow: readonly string[];
} {
  const texts = results.status_strip.map(item => item.text);
  return { visible: texts.slice(0, STRIP_MAX_ITEMS), overflow: texts.slice(STRIP_MAX_ITEMS) };
}

const ASSUMED_WIDTH: Readonly<Record<string, string>> = {
  wide: "a wide street",
  narrow: "a narrow street",
};

/** Plain-English lines for a "Needs street width" case document (plan §4). */
export function streetWidthCaseLines(results: ThreeAnswersResults): string[] {
  const assumptions: StreetWidthCase["assumptions"] = results.street_width_case?.assumptions ?? [];
  return assumptions.flatMap(assumption => {
    const width = ASSUMED_WIDTH[assumption.assumed];
    return width
      ? [`This case assumes ${assumption.street} is ${width}; its width is not known.`]
      : [];
  });
}
