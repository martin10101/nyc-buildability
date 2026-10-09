/**
 * Runtime contract check for the results document the results panel renders
 * (task M5-T140, ruling R9).
 *
 * Contract: packages/contracts/schemas/v1/results.schema.json (version 1.3.0 the three-way
 * layer, and its strict superset 1.4.0 which adds the OPTIONAL first-building-options blocks
 * building_alternatives and coverage_by_portion) and its runtime guard services/api/app/contracts/study_contracts.py
 * (validate_results_document). The server already refuses to ship a body that fails
 * that guard (500 internal_contract_error); this is the CLIENT's independent check, so
 * a 200 body is NEVER trusted until its shape is verified (the study-setup /
 * hidden-issue-flags posture). Kept in its own module so the transport client
 * (results-api.ts) stays thin.
 *
 * NO legal meaning and NO zoning math live here: it verifies the SHAPE of exactly the
 * blocks the reader (apps/web/src/lib/architect/three-answers.ts, the Pick at :35)
 * consumes, and nothing else. It additionally REFUSES a document in which a key is
 * withheld in `value_states` and ALSO present among that answer's shown `values` — so a
 * number can never be shown for a withheld result even if the server erred (R556, R570;
 * ruling R9; scenario S21).
 *
 * BODY-INDEPENDENCE INVARIANT (inherited from scenario-contract-checks): every problem
 * message is a static string literal, so no byte of a rejected body ever reaches the
 * problem list that the failure state renders.
 */

import {
  Problems,
  checkBoolean,
  checkBoundedArray,
  checkEnum,
  checkNonEmptyString,
  isNonEmptyString,
} from "./scenario-contract-checks";
import {
  checkNoFixtureAnnotation,
  checkNullableNonEmptyString,
  checkObject,
  isJsonNumber,
} from "./study/study-checks";
import type { ThreeAnswersResults } from "./architect/three-answers";

/** The three-way value-states layer version (schema enum). Kept as the baseline the reader needs
 * (every accepted document is this version or its strict superset). */
export const RESULTS_CONTRACT_VERSION = "1.3.0";

/** The results-contract versions the reader accepts: the three-way 1.3.0 layer and its strict
 * superset 1.4.0 (the additive first-building-options blocks, M5-T146/M5-T147). 1.4.0 is accepted so
 * the live panel renders the new blocks; because the blocks are OPTIONAL, every valid 1.3.0 document
 * stays valid byte-for-byte. Earlier versions (1.0.0–1.2.0) carry no value_states and are refused by
 * the value_states rules below, as before. */
export const SUPPORTED_RESULTS_CONTRACT_VERSIONS = ["1.3.0", "1.4.0"] as const;

/** The two methods a worked alternative may carry (schema building_alternative.fill_rule). */
export const BUILDING_FILL_RULES = ["widest", "to_min_base"] as const;

/** The two owner labels a preliminary capacity estimate may carry (schema; D-090-R543). */
export const CAPACITY_ESTIMATE_LABELS = ["Preliminary capacity estimate", "Not known"] as const;

/** The two statuses the coverage-by-portion block may carry (schema coverage_by_portion). */
export const COVERAGE_BY_PORTION_STATUSES = ["available", "withheld"] as const;

/** The three answers the reader consumes (results.schema.json `answers`). */
export const RESULTS_ANSWER_KEYS = [
  "floor_area_allowance",
  "permitted_envelope",
  "building_option",
] as const;

/** The three ways a value may appear (schema `value_state.way`). */
export const VALUE_WAYS = ["settled", "conditional", "withheld"] as const;

/** The two kinds of gap a withheld value or not-available answer may carry (schema `gap_kind`). */
export const GAP_KINDS = ["missing_information", "work_owed"] as const;

/** The plain-English units the reader formats (schema `unit`). */
export const RESULTS_UNITS = [
  "square_feet",
  "feet",
  "ratio",
  "percent",
  "stories",
  "dwelling_units",
  "square_feet_per_dwelling_unit",
] as const;

export type ResultsValidation =
  | { ok: true; document: ThreeAnswersResults }
  | { ok: false; problems: string[] };

function checkAnswerValue(problems: Problems, path: string, value: unknown): void {
  const entry = checkObject(problems, path, value);
  if (!entry) return;
  if (typeof entry.key !== "string") problems.add(`${path}.key`, "must be a string");
  checkNonEmptyString(problems, `${path}.label`, entry.label);
  if (!isJsonNumber(entry.value)) problems.add(`${path}.value`, "must be a finite number");
  checkEnum(problems, `${path}.unit`, entry.unit, RESULTS_UNITS);
}

/** One `value_states` entry: a way, plus the fields that way requires (withheld carries the
 * label, reason, gap_kind and resolved_by the panel reads). Returns its `way` for the R9
 * cross-check, or null when the entry is malformed. */
function checkValueState(problems: Problems, path: string, value: unknown): string | null {
  const state = checkObject(problems, path, value);
  if (!state) return null;
  checkEnum(problems, `${path}.way`, state.way, VALUE_WAYS);
  if (state.way === "conditional") {
    const conditions = checkBoundedArray(problems, `${path}.conditions`, state.conditions);
    // A conditional value must NAME at least one condition (schema: conditions minItems 1); an
    // empty list would show a value as conditional-on-nothing, i.e. settled by silence.
    if (Array.isArray(state.conditions) && state.conditions.length === 0) {
      problems.add(`${path}.conditions`, "a conditional value must name at least one condition");
    }
    conditions?.forEach((condition, index) => {
      const item = checkObject(problems, `${path}.conditions[${index}]`, condition);
      if (item) checkNonEmptyString(problems, `${path}.conditions[${index}].assumption`, item.assumption);
    });
  } else if (state.way === "withheld") {
    checkNonEmptyString(problems, `${path}.label`, state.label);
    checkNonEmptyString(problems, `${path}.reason`, state.reason);
    checkEnum(problems, `${path}.gap_kind`, state.gap_kind, GAP_KINDS);
    checkNonEmptyString(problems, `${path}.resolved_by`, state.resolved_by);
  }
  return typeof state.way === "string" ? state.way : null;
}

/** One answer (available | not_available). For an available answer it checks the shown values,
 * the measurement label and the value_states map, AND the R9 refusal: a key withheld in
 * value_states must never also appear among the shown values. */
function checkAnswer(problems: Problems, path: string, value: unknown): void {
  const answer = checkObject(problems, path, value);
  if (!answer) return;
  if (answer.status === "available") {
    const values = checkBoundedArray(problems, `${path}.values`, answer.values);
    values?.forEach((item, index) => checkAnswerValue(problems, `${path}.values[${index}]`, item));
    const measurement = checkObject(problems, `${path}.measurement`, answer.measurement);
    if (measurement) checkNonEmptyString(problems, `${path}.measurement.label`, measurement.label);

    const shownKeys = new Set(
      Array.isArray(answer.values)
        ? answer.values
            .map(item => (item && typeof (item as { key?: unknown }).key === "string"
              ? (item as { key: string }).key
              : null))
            .filter((key): key is string => key !== null)
        : [],
    );
    const states = answer.value_states;
    // No value is settled by silence (three_way_document.py: "one entry for every value"; schema:
    // value_states required on every available 1.3.0 answer). An available answer that SHOWS values
    // must carry a value_states map (rule 1).
    if (
      Array.isArray(answer.values) &&
      answer.values.length > 0 &&
      (states === undefined || states === null)
    ) {
      problems.add(
        `${path}.value_states`,
        "an available answer that shows values must carry a value_states map (no value is settled by silence)",
      );
    }
    if (states !== undefined && states !== null) {
      const map = checkObject(problems, `${path}.value_states`, states);
      if (map) {
        const keys = Object.keys(map);
        // Every shown value must have a value_states entry (rule 2): a value with no state would be
        // read as settled by silence.
        for (const shownKey of shownKeys) {
          if (!(shownKey in map)) {
            problems.add(
              `${path}.value_states[${shownKey}]`,
              "a shown value must carry a value_states entry (settled, conditional or withheld); none is settled by silence",
            );
          }
        }
        if (keys.length > 64) {
          problems.add(`${path}.value_states`, "carries more value states than this screen accepts");
        } else {
          for (const key of keys) {
            const way = checkValueState(problems, `${path}.value_states[${key}]`, map[key]);
            // R9 (R556, R570): a withheld key must not also be a shown value, or a number could be
            // shown for a result the document says is not known.
            if (way === "withheld" && shownKeys.has(key)) {
              problems.add(
                `${path}.value_states[${key}]`,
                "is withheld but also appears among the answer's shown values; a withheld value may never carry a number",
              );
            }
          }
        }
      }
    }
  } else if (answer.status === "not_available") {
    checkNonEmptyString(problems, `${path}.reason`, answer.reason);
    checkNonEmptyString(problems, `${path}.reason_kind`, answer.reason_kind);
    if (answer.gap_kind !== undefined && answer.gap_kind !== null) {
      checkEnum(problems, `${path}.gap_kind`, answer.gap_kind, GAP_KINDS);
    }
  } else {
    problems.add(`${path}.status`, "must be the string \"available\" or \"not_available\"");
  }
}

/** A supplement block (remaining_floor_area, shortfall): a `status` string, and a non-empty
 * reason when it is not available. The reader reads these fields only. */
function checkStatusBlock(problems: Problems, path: string, value: unknown): void {
  const block = checkObject(problems, path, value);
  if (!block) return;
  if (typeof block.status !== "string") {
    problems.add(`${path}.status`, "must be a string");
    return;
  }
  if (block.status === "not_available") {
    checkNonEmptyString(problems, `${path}.reason`, block.reason);
  }
}

/** The scope-beside-the-numbers block (results contract 1.1.0+); null is accepted. When present
 * every string the ScopeSummary reads is checked so a malformed scope never reaches the card. */
function checkScope(problems: Problems, value: unknown): void {
  if (value === null || value === undefined) return;
  const scope = checkObject(problems, "scope", value);
  if (!scope) return;
  checkNonEmptyString(problems, "scope.label", scope.label);
  const lot = checkObject(problems, "scope.lot", scope.lot);
  if (lot) checkNonEmptyString(problems, "scope.lot.display", lot.display);
  const wholeSite = checkObject(problems, "scope.whole_site", scope.whole_site);
  if (wholeSite) checkNonEmptyString(problems, "scope.whole_site.statement", wholeSite.statement);
  const remaining = checkObject(problems, "scope.remaining_capacity", scope.remaining_capacity);
  if (remaining) {
    checkNonEmptyString(problems, "scope.remaining_capacity.label", remaining.label);
    checkNonEmptyString(problems, "scope.remaining_capacity.reason", remaining.reason);
  }
  const assumptions = checkBoundedArray(problems, "scope.assumptions", scope.assumptions);
  assumptions?.forEach((item, index) => {
    const row = checkObject(problems, `scope.assumptions[${index}]`, item);
    if (!row) return;
    checkNonEmptyString(problems, `scope.assumptions[${index}].key`, row.key);
    checkNonEmptyString(problems, `scope.assumptions[${index}].statement`, row.statement);
    if (
      !(
        typeof row.value === "string" ||
        typeof row.value === "number" ||
        typeof row.value === "boolean"
      )
    ) {
      problems.add(`scope.assumptions[${index}].value`, "must be a string, number or boolean");
    }
  });
}

/** A finite-number field (areas, heights, ratios, quotients). */
function checkNumberField(problems: Problems, path: string, value: unknown): void {
  if (!isJsonNumber(value)) problems.add(path, "must be a finite number");
}

/** One floor-schedule row of a worked alternative (schema floor_schedule_row): six numeric fields. */
function checkFloorScheduleRow(problems: Problems, path: string, value: unknown): void {
  const row = checkObject(problems, path, value);
  if (!row) return;
  for (const field of [
    "storey",
    "floor_to_floor_ft",
    "top_ft",
    "plan_area_sqft",
    "floor_area_sqft",
    "running_total_sqft",
  ]) {
    checkNumberField(problems, `${path}.${field}`, (row as Record<string, unknown>)[field]);
  }
}

/** A worked building's preliminary capacity estimate (schema preliminary_capacity_estimate): the
 * owner label plus either the quotients (available) or a reason and NO number ("Not known"). */
function checkCapacityEstimate(problems: Problems, path: string, value: unknown): void {
  const estimate = checkObject(problems, path, value);
  if (!estimate) return;
  checkEnum(problems, `${path}.label`, estimate.label, CAPACITY_ESTIMATE_LABELS);
  if (estimate.label === "Preliminary capacity estimate") {
    for (const field of [
      "floor_area_sqft",
      "share_low",
      "share_high",
      "apartment_size_sqft",
      "quotient_low",
      "quotient_high",
      "quotient_low_unrounded",
      "quotient_high_unrounded",
      "whole_below_low",
      "whole_above_low",
      "whole_below_high",
      "whole_above_high",
    ]) {
      checkNumberField(problems, `${path}.${field}`, (estimate as Record<string, unknown>)[field]);
    }
  } else if (estimate.label === "Not known") {
    checkNonEmptyString(problems, `${path}.reason`, estimate.reason);
    // R556/R570: a not-known estimate carries no number (never a substitute figure).
    for (const field of ["floor_area_sqft", "quotient_low", "quotient_high"]) {
      if (isJsonNumber((estimate as Record<string, unknown>)[field])) {
        problems.add(`${path}.${field}`, "a not-known estimate may never carry a number");
      }
    }
  }
}

/** The building_alternatives list (schema, contract 1.4.0). Absent or null is accepted (additive);
 * when present each entry's shape is checked so a malformed alternative never reaches the panel. */
function checkBuildingAlternatives(problems: Problems, value: unknown): void {
  if (value === null || value === undefined) return;
  const list = checkBoundedArray(problems, "building_alternatives", value);
  if (!list) return;
  list.forEach((item, index) => {
    const path = `building_alternatives[${index}]`;
    const alternative = checkObject(problems, path, item);
    if (!alternative) return;
    checkNonEmptyString(problems, `${path}.building`, alternative.building);
    checkNonEmptyString(problems, `${path}.label`, alternative.label);
    checkEnum(problems, `${path}.fill_rule`, alternative.fill_rule, BUILDING_FILL_RULES);
    const schedule = checkBoundedArray(problems, `${path}.floor_schedule`, alternative.floor_schedule);
    schedule?.forEach((row, rowIndex) =>
      checkFloorScheduleRow(problems, `${path}.floor_schedule[${rowIndex}]`, row),
    );
    for (const field of [
      "storey_count",
      "height_ft",
      "footprint_area_sqft",
      "floor_area_allowance_sqft",
      "total_floor_area_sqft",
      "unused_floor_area_sqft",
    ]) {
      checkNumberField(problems, `${path}.${field}`, (alternative as Record<string, unknown>)[field]);
    }
    checkBoolean(problems, `${path}.below_min_base`, alternative.below_min_base);
    checkValueState(problems, `${path}.way`, alternative.way);
    const notChecked = checkBoundedArray(problems, `${path}.not_checked`, alternative.not_checked);
    if (Array.isArray(alternative.not_checked) && alternative.not_checked.length === 0) {
      problems.add(`${path}.not_checked`, "a worked alternative must name at least one unchecked item");
    }
    notChecked?.forEach((entry, entryIndex) =>
      checkNonEmptyString(problems, `${path}.not_checked[${entryIndex}]`, entry),
    );
    checkCapacityEstimate(problems, `${path}.capacity_estimate`, alternative.capacity_estimate);
  });
}

/** The coverage_by_portion block (schema, contract 1.4.0). Absent or null is accepted (additive).
 * A WITHHELD result carries NO number (R556/R570) — any portion area, ratio or footprint figure on
 * the withheld branch is refused, so the panel can never show a number for a withheld coverage. */
function checkCoverageByPortion(problems: Problems, value: unknown): void {
  if (value === null || value === undefined) return;
  const coverage = checkObject(problems, "coverage_by_portion", value);
  if (!coverage) return;
  if (coverage.status === "available") {
    for (const field of [
      "corner_ratio",
      "interior_ratio",
      "corner_lot_distance_ft",
      "corner_portion_area_sqft",
      "interior_portion_area_sqft",
      "footprint_sqft",
    ]) {
      checkNumberField(problems, `coverage_by_portion.${field}`, (coverage as Record<string, unknown>)[field]);
    }
    checkBoundedArray(problems, "coverage_by_portion.zr_sections", coverage.zr_sections);
    checkValueState(problems, "coverage_by_portion.way", coverage.way);
  } else if (coverage.status === "withheld") {
    checkNonEmptyString(problems, "coverage_by_portion.label", coverage.label);
    checkNonEmptyString(problems, "coverage_by_portion.reason", coverage.reason);
    checkEnum(problems, "coverage_by_portion.gap_kind", coverage.gap_kind, GAP_KINDS);
    checkNonEmptyString(problems, "coverage_by_portion.resolved_by", coverage.resolved_by);
    checkBoundedArray(problems, "coverage_by_portion.zr_sections", coverage.zr_sections);
    for (const field of [
      "footprint_sqft",
      "corner_portion_area_sqft",
      "interior_portion_area_sqft",
      "corner_ratio",
      "interior_ratio",
    ]) {
      if (isJsonNumber((coverage as Record<string, unknown>)[field])) {
        problems.add(
          `coverage_by_portion.${field}`,
          "a withheld coverage result may never carry a number",
        );
      }
    }
  } else {
    problems.add("coverage_by_portion.status", 'must be the string "available" or "withheld"');
  }
}

/**
 * Validate a results document against the shape the panel reads. On success returns the typed
 * document (the reader's Pick); otherwise a bounded list of problems. SHAPE only — no legal
 * meaning is read.
 */
export function validateResultsDocument(body: unknown): ResultsValidation {
  const problems = new Problems();
  const doc = checkObject(problems, "results", body);
  if (!doc) return { ok: false, problems: problems.list };
  checkNoFixtureAnnotation(problems, "results", doc);

  checkEnum(problems, "contract_version", doc.contract_version, SUPPORTED_RESULTS_CONTRACT_VERSIONS);

  checkBoolean(problems, "out_of_date", doc.out_of_date);
  checkNullableNonEmptyString(problems, "out_of_date_reason", doc.out_of_date_reason);
  checkNonEmptyString(problems, "lot_selection_statement", doc.lot_selection_statement);
  // with_approvals_label is a fixed string or null (schema); the reader shows it when non-null.
  if (!(doc.with_approvals_label === null || isNonEmptyString(doc.with_approvals_label))) {
    problems.add("with_approvals_label", "must be a non-empty string or null");
  }

  const answers = checkObject(problems, "answers", doc.answers);
  if (answers) {
    for (const key of RESULTS_ANSWER_KEYS) {
      checkAnswer(problems, `answers.${key}`, answers[key]);
    }
  }

  checkStatusBlock(problems, "remaining_floor_area", doc.remaining_floor_area);
  checkStatusBlock(problems, "shortfall", doc.shortfall);

  const completeness = checkObject(problems, "completeness_line", doc.completeness_line);
  if (completeness) checkNonEmptyString(problems, "completeness_line.text", completeness.text);

  const strip = checkBoundedArray(problems, "status_strip", doc.status_strip);
  strip?.forEach((item, index) => {
    const entry = checkObject(problems, `status_strip[${index}]`, item);
    if (entry) checkNonEmptyString(problems, `status_strip[${index}].text`, entry.text);
  });

  if (!isJsonNumber(doc.notices_count)) problems.add("notices_count", "must be a finite number");
  checkBoolean(problems, "draft", doc.draft);
  checkScope(problems, doc.scope);

  // The additive contract-1.4.0 blocks (first building options; absent/null on a 1.3.0 document).
  checkBuildingAlternatives(problems, doc.building_alternatives);
  checkCoverageByPortion(problems, doc.coverage_by_portion);

  if (problems.list.length > 0) return { ok: false, problems: problems.list };
  return { ok: true, document: doc as unknown as ThreeAnswersResults };
}
