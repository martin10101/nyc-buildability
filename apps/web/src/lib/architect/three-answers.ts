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
  Scope,
  ScopeAssumption,
  StreetWidthCase,
  Unit,
} from "../../../../../packages/contracts/generated/results";
import { NOT_CONFIRMED, REMAINING_CAPACITY_LABEL, REMAINING_CAPACITY_REASON } from "./tax-lot-scope";

// The canonical generated contract types (packages/contracts/generated/results.ts, task C-03),
// re-exported so the panel and its tests import them from one place.
export type { AnswerValue, ExceptionLabel, Results, Scope, ScopeAssumption, Unit };

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
  | "scope"
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

/** Row label for an available value of the allowance left after a kept building (plan §3
 * step 4). Without a verified value the row reads REMAINING_CAPACITY_LABEL (D-090-R038). */
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
  | { kind: "not_available"; label: string; text: string; reason?: string };

/**
 * The allowance left after a kept building (plan §3 step 4). null when no building is kept.
 * Read only while the allowance itself is shown. Without a verified value it reads the owner's
 * settled wording (D-090-R038), which replaces plan §3 step 4's: "Remaining development
 * capacity" → "Not confirmed", then the reason line.
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
      label: REMAINING_CAPACITY_LABEL,
      text: NOT_CONFIRMED,
      reason: REMAINING_CAPACITY_REASON,
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

// ---- Scope beside the numbers (results contract 1.1.0, D-090-R108) ----
// The panel reads every scope string straight from the document (label, lot.display, each
// assumption statement, the whole-site statement and the two settled remaining-capacity strings).
// These maps only turn the machine assumption key and the basis enum into plain words so no
// internal code reaches the screen (plan §5a item 5); they never restate a document string.

const SCOPE_ASSUMPTION_KEY_LABELS: Readonly<Record<string, string>> = {
  lot_type: "Lot type",
  within_100_ft_of_street_line_intersection: "Within 100 ft of a street-line intersection",
  street_line_intersection_angle_degrees: "Street-line intersection angle",
  housing_program: "Housing program",
  floor_to_floor_ft: "Floor-to-floor height",
};

/** A machine assumption key in plain words. An unlisted key is de-underscored and sentence-cased
 * so a key added to the contract later never prints as a raw code. */
export function scopeAssumptionKeyLabel(key: string): string {
  const mapped = SCOPE_ASSUMPTION_KEY_LABELS[key];
  if (mapped) return mapped;
  const words = key.replace(/_/g, " ").trim();
  return words ? words.charAt(0).toUpperCase() + words.slice(1) : key;
}

// The basis enum (schema scope_assumption.basis) in plain words, so the architect sees whether a
// value was assumed, entered, a fixed benchmark, from city records, from a supplied survey, from
// the approximate tax map, or the app's default — never the enum code.
const SCOPE_BASIS_LABELS: Readonly<Record<ScopeAssumption["basis"], string>> = {
  assumed: "Assumed",
  entered: "Entered",
  fixture: "Test fixture",
  city_records: "City records",
  survey_entered: "Survey",
  approximate_tax_map: "Approximate tax map",
  default: "Default",
};

/** Where an assumed value came from, in plain words (never the enum code). */
export function scopeAssumptionBasisLabel(basis: ScopeAssumption["basis"]): string {
  return SCOPE_BASIS_LABELS[basis];
}

/** An assumed value with its unit, in plain words: a flag reads Yes/No, a number is grouped, and
 * a code-like string is de-underscored. The unit comes from the document already in plain words. */
export function scopeAssumptionValueText(
  value: string | number | boolean,
  unit: string | null,
): string {
  let base: string;
  if (typeof value === "boolean") base = value ? "Yes" : "No";
  else if (typeof value === "number") base = PLAIN_NUMBER.format(value);
  else base = value.replace(/_/g, " ");
  return unit ? `${base} ${unit}` : base;
}

export interface ScopeAssumptionView {
  keyLabel: string;
  valueText: string;
  basisLabel: string;
  statement: string;
}

export interface ScopeView {
  /** The scope label, byte-exact from the document (e.g. "Tax-lot-only estimate"). */
  label: string;
  /** The human lot label, read from the document (e.g. "Queens block 7334, lot 70"). */
  lotDisplay: string;
  /** Each assumed condition in the order the document gives; statement read from the document. */
  assumptions: readonly ScopeAssumptionView[];
  /** The whole-site statement, byte-exact from the document. */
  wholeSiteStatement: string;
  /** The remaining-capacity line ("<label>: <status word>"), byte-exact from the document. */
  remainingLabel: string;
  /** The reason under the remaining-capacity line, byte-exact from the document. */
  remainingReason: string;
}

/**
 * The scope-beside-the-numbers block (results contract 1.1.0, D-090-R108), or null when the
 * document carries no scope — a 1.0.0 document, or a 1.1.0 document with scope null — so the panel
 * renders unchanged from before for those (requirement b). Every string is read from the document;
 * the key and basis are turned into plain words only, never restated.
 */
export function scopeView(results: ThreeAnswersResults): ScopeView | null {
  const scope = results.scope;
  if (!scope) return null;
  return {
    label: scope.label,
    lotDisplay: scope.lot.display,
    assumptions: scope.assumptions.map(assumption => ({
      keyLabel: scopeAssumptionKeyLabel(assumption.key),
      valueText: scopeAssumptionValueText(assumption.value, assumption.unit),
      basisLabel: scopeAssumptionBasisLabel(assumption.basis),
      statement: assumption.statement,
    })),
    wholeSiteStatement: scope.whole_site.statement,
    remainingLabel: scope.remaining_capacity.label,
    remainingReason: scope.remaining_capacity.reason,
  };
}

// ---- Building-option draft notes (results contract 1.2.0, D-090-R132) ----
// A note is a DRAFT reading of the captured zoning text for the building option — never a
// compliance statement. The panel reads the text, ZR sections and snapshot ids straight from the
// document; the kind becomes plain words and the heading is a fixed UI label. Nothing is retyped.

/**
 * Heading over every building-option draft note. A fixed label (never read from the document): it
 * marks the note as a draft reading a qualified reviewer has NOT signed off, so a reading is never
 * shown as a finding (D-090-R132).
 */
export const BUILDING_OPTION_NOTE_HEADING = "Draft reading — pending qualified review";

// The note kind enum (schema building_option_note.kind) in plain words, so the architect sees what
// the reading is about, never the enum code (plan §5a item 5). An unlisted kind is de-underscored
// and sentence-cased so a kind added to the contract later never prints as a raw code.
const BUILDING_OPTION_NOTE_KIND_LABELS: Readonly<Record<string, string>> = {
  minimum_base_height: "Minimum base height",
};

/** A note kind in plain words (never the enum code). */
export function buildingOptionNoteKindLabel(kind: string): string {
  const mapped = BUILDING_OPTION_NOTE_KIND_LABELS[kind];
  if (mapped) return mapped;
  const words = kind.replace(/_/g, " ").trim();
  return words ? words.charAt(0).toUpperCase() + words.slice(1) : kind;
}

export interface BuildingOptionNoteView {
  /** The draft heading over the note (the fixed UI label above, never from the document). */
  draftLabel: string;
  /** What the reading is about, in plain words (e.g. "Minimum base height"). */
  kindLabel: string;
  /** The note text, byte-exact from the document. */
  text: string;
  /** The ZR sections the reading is based on, read from the document (e.g. "ZR 23-431"). */
  zrSections: readonly string[];
  /** The captured snapshot ids behind the reading, read from the document (e.g. "zr-23-431"). */
  snapshotIds: readonly string[];
}

/**
 * The building option's draft notes (results contract 1.2.0, D-090-R132). Reads only the
 * document. Fail safe: a note whose `draft` flag is not exactly true is dropped, so a reading
 * never reaches the screen as a finding; a building option that is not available, or one with no
 * notes, yields an empty list so the card is unchanged (requirement c). The rendering gate — show
 * a note only while the heights it interprets are shown — is the card itself: the panel passes
 * this list to the building-option card, which renders its children only when available.
 */
export function buildingOptionNotesView(results: ThreeAnswersResults): BuildingOptionNoteView[] {
  const option = results.answers.building_option;
  if (option.status !== "available" || !option.notes) return [];
  return option.notes
    .filter(note => note.draft === true)
    .map(note => ({
      draftLabel: BUILDING_OPTION_NOTE_HEADING,
      kindLabel: buildingOptionNoteKindLabel(note.kind),
      text: note.text,
      zrSections: note.zr_sections,
      snapshotIds: note.snapshot_ids,
    }));
}
