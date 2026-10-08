/**
 * Runtime contract check for the results document the results panel renders
 * (task M5-T140, ruling R9).
 *
 * Contract: packages/contracts/schemas/v1/results.schema.json (version 1.3.0, the
 * three-way layer) and its runtime guard services/api/app/contracts/study_contracts.py
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

/** The one results-contract version the panel's three-way layer reads (schema enum). */
export const RESULTS_CONTRACT_VERSION = "1.3.0";

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
    if (states !== undefined && states !== null) {
      const map = checkObject(problems, `${path}.value_states`, states);
      if (map) {
        const keys = Object.keys(map);
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

  checkEnum(problems, "contract_version", doc.contract_version, [RESULTS_CONTRACT_VERSION]);

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

  if (problems.list.length > 0) return { ok: false, problems: problems.list };
  return { ok: true, document: doc as unknown as ThreeAnswersResults };
}
