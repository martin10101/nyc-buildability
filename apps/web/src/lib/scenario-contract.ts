/**
 * Canonical scenario contract vocabulary + runtime validator for the web client
 * (task M5-T002; hardened under D-022).
 *
 * The ONLY type vocabulary for a draft scenario result is the GENERATED module
 * packages/contracts/generated/scenario.ts (M5-T001, regenerated deterministically
 * from packages/contracts/schemas/v1/scenario.schema.json; the contracts-typegen
 * CI job fails on any drift). This file consumes those types the EXACT same way
 * src/lib/rule-evaluation-contract.ts consumes rule_evaluation.ts — a type-only
 * relative import erased at build time, so the Next.js bundle never compiles a
 * file outside apps/web and no schema is ever forked here.
 *
 * It then provides a RUNTIME validator that FAITHFULLY enforces the canonical
 * scenario.schema.json (+ its common.schema.json $refs) before any HTTP-200 body
 * can render. FAILURE IS TOTAL — the caller receives only a bounded problem list,
 * never a partially-usable document — so nothing can be drawn from an invalid
 * payload and malformed nested data can never reach the render layer.
 *
 * The validator enforces, before casting `unknown` to `Scenario` (schema §):
 *   - additionalProperties:false + required presence at EVERY object level
 *     (root, evaluated_input, each constraint, cap_provenance, each citation,
 *     each assumption, each coverage_matrix row, integrity_check);
 *   - the canonical BBL pattern and sha256 fingerprint pattern (common.schema.json);
 *   - the strictly-positive-non-null draft cap (exclusiveMinimum 0);
 *   - every enum (coverage_status narrowed to exclude `verified`; constraint
 *     state; cap_provenance.rule_status; coverage-matrix rule_status_today);
 *   - finite numbers everywhere (no NaN/±Infinity — strict JSON);
 *   - objects are objects, not arrays or null where the schema says object.
 *
 * The DRAFT vocabulary deliberately EXCLUDES `verified`: a scenario is never
 * Verified (PRD sections 10-12). No legal logic lives here
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md): this file checks SHAPE, never
 * meaning, and never rewrites a value (the surfaced cap is displayed verbatim,
 * never recomputed or relabeled).
 */

import type {
  CapProvenance,
  CoverageMatrixRow,
  DataCompleteness,
  DraftCoverageStatus,
  IntegrityCheck,
  Scenario,
  ScenarioAssumption,
  ScenarioConstraint,
  ScenarioEvaluatedInput,
} from "../../../../packages/contracts/generated/scenario";

export type {
  CapProvenance,
  CoverageMatrixRow,
  DataCompleteness,
  DraftCoverageStatus,
  IntegrityCheck,
  Scenario,
  ScenarioAssumption,
  ScenarioConstraint,
  ScenarioEvaluatedInput,
};

// ---------------------------------------------------------------------------
// Runtime enum arrays, exhaustively locked to the generated unions with the
// same two-way `MutuallyEqual` proof rule-evaluation-contract.ts uses: tsc fails
// here on either direction of drift, so the arrays can never silently diverge
// from the generated vocabulary.
// ---------------------------------------------------------------------------

/** The closed set of draft coverage statuses — `verified` is intentionally
 * absent (a scenario is never Verified). */
export const SCENARIO_COVERAGE_STATUSES = [
  "conditional",
  "professional_review_required",
  "data_conflict",
  "unsupported",
  "not_applicable",
] as const satisfies readonly DraftCoverageStatus[];

export const SCENARIO_DATA_COMPLETENESS_VALUES = [
  "complete",
  "missing_noncritical",
  "missing_critical",
] as const satisfies readonly DataCompleteness[];

export const SCENARIO_KINDS = [
  "preliminary",
  "no_scenario",
  "unsupported",
] as const satisfies readonly Scenario["scenario_kind"][];

export const CONSTRAINT_STATES = [
  "known",
  "draft",
  "missing",
  "conflicting",
  "unsupported",
  "professional_review_required",
] as const satisfies readonly ScenarioConstraint["state"][];

/** cap_provenance.rule_status — locked to the generated CapProvenance union;
 * `verified` is intentionally absent (the cap comes from a draft rule). */
export const CAP_RULE_STATUSES = [
  "discovered",
  "extracted_draft",
  "needs_review",
  "published",
] as const satisfies readonly CapProvenance["rule_status"][];

export const COVERAGE_MATRIX_RULE_STATUSES = [
  "draft",
  "missing",
  "out_of_scope",
] as const satisfies readonly CoverageMatrixRow["rule_status_today"][];

/** Two-way equality proof: `true` only when A and B are the same union. */
type MutuallyEqual<A, B> = [A] extends [B] ? ([B] extends [A] ? true : never) : never;

/** Compile-time exhaustiveness proof (exported so it is never "unused"): any
 * array above that misses a member of its generated union makes the
 * corresponding tuple slot `never` and fails tsc. */
export type ScenarioEnumAssertions = [
  MutuallyEqual<DraftCoverageStatus, (typeof SCENARIO_COVERAGE_STATUSES)[number]>,
  MutuallyEqual<DataCompleteness, (typeof SCENARIO_DATA_COMPLETENESS_VALUES)[number]>,
  MutuallyEqual<Scenario["scenario_kind"], (typeof SCENARIO_KINDS)[number]>,
  MutuallyEqual<ScenarioConstraint["state"], (typeof CONSTRAINT_STATES)[number]>,
  MutuallyEqual<CapProvenance["rule_status"], (typeof CAP_RULE_STATUSES)[number]>,
  MutuallyEqual<
    CoverageMatrixRow["rule_status_today"],
    (typeof COVERAGE_MATRIX_RULE_STATUSES)[number]
  >,
];

// ---------------------------------------------------------------------------
// Canonical key sets — the schema's `required` + `additionalProperties:false`
// at every object level. `_expected_failure` is the schema's single OPTIONAL
// top-level key (a fixture-only annotation the schema explicitly permits).
// ---------------------------------------------------------------------------

const TOP_LEVEL_REQUIRED = [
  "contract_version",
  "scenario_kind",
  "coverage_status",
  "data_completeness",
  "needs_review",
  "professional_review_required",
  "not_verified_disclaimer",
  "evaluated_input",
  "constraints",
  "draft_zoning_floor_area_cap_sq_ft",
  "cap_label",
  "cap_provenance",
  "assumptions",
  "reasons",
  "coverage_matrix",
  "integrity_check",
] as const;
const TOP_LEVEL_OPTIONAL = ["_expected_failure"] as const;

const EVALUATED_INPUT_KEYS = [
  "bbl",
  "profile_contract_version",
  "rule_evaluation_contract_version",
  "input_fingerprint",
] as const;
const CONSTRAINT_KEYS = [
  "key",
  "state",
  "value",
  "unit",
  "data_completeness",
  "provenance",
  "note",
] as const;
const CAP_PROVENANCE_KEYS = [
  "rule_id",
  "rule_version",
  "rule_status",
  "output_name",
  "citations",
  "note",
] as const;
const CITATION_REQUIRED = ["snapshot_id", "section", "quote", "provenance"] as const;
const CITATION_OPTIONAL = ["last_amended"] as const;
const ASSUMPTION_KEYS = ["key", "assumption_type", "value", "unit", "rationale"] as const;
const COVERAGE_MATRIX_ROW_KEYS = [
  "constraint_family",
  "governs",
  "rule_status_today",
  "blocks_buildable_envelope",
] as const;
const INTEGRITY_KEYS = ["performed", "agreed", "tolerance", "method", "note"] as const;

const BBL_PATTERN = /^[1-5][0-9]{5}[0-9]{4}$/;
const SHA256_PATTERN = /^sha256:[0-9a-f]{64}$/;

export const MAX_REPORTED_PROBLEMS = 20;

export type ScenarioValidationResult =
  | { ok: true; document: Scenario }
  | { ok: false; problems: string[] };

class Problems {
  list: string[] = [];

  add(path: string, message: string): void {
    if (this.list.length < MAX_REPORTED_PROBLEMS) {
      this.list.push(`${path}: ${message}`);
    } else if (this.list.length === MAX_REPORTED_PROBLEMS) {
      this.list.push("… further problems omitted (bounded report)");
    }
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

/** A number the schema will accept: finite (never NaN/±Infinity — strict JSON). */
function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

/** A constraint/assumption `value`: number|string|boolean|null, numbers FINITE. */
function isScalarValue(value: unknown): boolean {
  return (
    value === null ||
    typeof value === "string" ||
    typeof value === "boolean" ||
    isFiniteNumber(value)
  );
}

/** Enforce additionalProperties:false + required-presence for one object level. */
function checkExactKeys(
  problems: Problems,
  path: string,
  obj: Record<string, unknown>,
  required: readonly string[],
  optional: readonly string[] = [],
): void {
  const prefix = path ? `${path}.` : "";
  const allowed = new Set<string>([...required, ...optional]);
  for (const key of Object.keys(obj)) {
    if (!allowed.has(key)) {
      problems.add(`${prefix}${key}`, "unexpected property (additionalProperties: false)");
    }
  }
  for (const key of required) {
    if (!(key in obj)) {
      problems.add(`${prefix}${key}`, "required property is missing");
    }
  }
}

function checkEnum(
  problems: Problems,
  path: string,
  value: unknown,
  allowed: readonly string[],
): void {
  if (!(typeof value === "string" && allowed.includes(value))) {
    problems.add(path, `value is not in the documented enum (${allowed.join(", ")})`);
  }
}

function checkStringArray(problems: Problems, path: string, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add(path, "must be an array");
    return;
  }
  value.forEach((item, index) => {
    if (typeof item !== "string") {
      problems.add(`${path}[${index}]`, "must be a string");
    }
  });
}

function checkEvaluatedInput(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("evaluated_input", "required object is missing or not an object");
    return;
  }
  checkExactKeys(problems, "evaluated_input", value, EVALUATED_INPUT_KEYS);
  if (!(value.bbl === null || (typeof value.bbl === "string" && BBL_PATTERN.test(value.bbl)))) {
    problems.add(
      "evaluated_input.bbl",
      "must be null or a canonical 10-digit BBL (^[1-5][0-9]{5}[0-9]{4}$)",
    );
  }
  if (!isNonEmptyString(value.profile_contract_version)) {
    problems.add("evaluated_input.profile_contract_version", "must be a non-empty string");
  }
  if (!isNonEmptyString(value.rule_evaluation_contract_version)) {
    problems.add(
      "evaluated_input.rule_evaluation_contract_version",
      "must be a non-empty string",
    );
  }
  if (
    !(
      value.input_fingerprint === null ||
      (typeof value.input_fingerprint === "string" &&
        SHA256_PATTERN.test(value.input_fingerprint))
    )
  ) {
    problems.add(
      "evaluated_input.input_fingerprint",
      "must be null or match ^sha256:[0-9a-f]{64}$",
    );
  }
}

function checkConstraint(problems: Problems, path: string, value: unknown): void {
  if (!isRecord(value)) {
    problems.add(path, "must be an object");
    return;
  }
  checkExactKeys(problems, path, value, CONSTRAINT_KEYS);
  if (!isNonEmptyString(value.key)) {
    problems.add(`${path}.key`, "must be a non-empty string");
  }
  checkEnum(problems, `${path}.state`, value.state, CONSTRAINT_STATES);
  if (!isScalarValue(value.value)) {
    problems.add(`${path}.value`, "must be a finite number, string, boolean, or null");
  }
  if (!(value.unit === null || typeof value.unit === "string")) {
    problems.add(`${path}.unit`, "must be a string or null");
  }
  checkEnum(
    problems,
    `${path}.data_completeness`,
    value.data_completeness,
    SCENARIO_DATA_COMPLETENESS_VALUES,
  );
  // Schema: provenance is type ["object","null"] — an ARRAY must not pass.
  if (!(value.provenance === null || isRecord(value.provenance))) {
    problems.add(`${path}.provenance`, "must be an object (not an array) or null");
  }
  if (typeof value.note !== "string") {
    problems.add(`${path}.note`, "must be a string");
  }
}

function checkCitation(problems: Problems, path: string, value: unknown): void {
  if (!isRecord(value)) {
    problems.add(path, "must be an object");
    return;
  }
  checkExactKeys(problems, path, value, CITATION_REQUIRED, CITATION_OPTIONAL);
  for (const key of ["snapshot_id", "section", "quote"] as const) {
    if (typeof value[key] !== "string") {
      problems.add(`${path}.${key}`, "must be a string");
    }
  }
  if ("last_amended" in value && !(value.last_amended === null || typeof value.last_amended === "string")) {
    problems.add(`${path}.last_amended`, "must be a string or null");
  }
  // Schema: citation.provenance is type "object" (never null, never an array).
  if (!isRecord(value.provenance)) {
    problems.add(`${path}.provenance`, "must be an object");
  }
}

function checkCapProvenance(problems: Problems, value: unknown): void {
  if (value === null) return;
  if (!isRecord(value)) {
    problems.add("cap_provenance", "must be an object or null");
    return;
  }
  checkExactKeys(problems, "cap_provenance", value, CAP_PROVENANCE_KEYS);
  for (const key of ["rule_id", "rule_version", "output_name", "note"] as const) {
    if (typeof value[key] !== "string") {
      problems.add(`cap_provenance.${key}`, "must be a string");
    }
  }
  checkEnum(problems, "cap_provenance.rule_status", value.rule_status, CAP_RULE_STATUSES);
  if (!Array.isArray(value.citations)) {
    problems.add("cap_provenance.citations", "must be an array");
  } else {
    value.citations.forEach((citation, index) =>
      checkCitation(problems, `cap_provenance.citations[${index}]`, citation),
    );
  }
}

function checkAssumption(problems: Problems, path: string, value: unknown): void {
  if (!isRecord(value)) {
    problems.add(path, "must be an object");
    return;
  }
  checkExactKeys(problems, path, value, ASSUMPTION_KEYS);
  if (!isNonEmptyString(value.key)) {
    problems.add(`${path}.key`, "must be a non-empty string");
  }
  if (typeof value.assumption_type !== "string") {
    problems.add(`${path}.assumption_type`, "must be a string");
  }
  if (!isScalarValue(value.value)) {
    problems.add(`${path}.value`, "must be a finite number, string, boolean, or null");
  }
  if (!(value.unit === null || typeof value.unit === "string")) {
    problems.add(`${path}.unit`, "must be a string or null");
  }
  if (typeof value.rationale !== "string") {
    problems.add(`${path}.rationale`, "must be a string");
  }
}

function checkCoverageMatrix(problems: Problems, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add("coverage_matrix", "must be an array");
    return;
  }
  value.forEach((row, index) => {
    const path = `coverage_matrix[${index}]`;
    if (!isRecord(row)) {
      problems.add(path, "must be an object");
      return;
    }
    checkExactKeys(problems, path, row, COVERAGE_MATRIX_ROW_KEYS);
    if (typeof row.constraint_family !== "string") {
      problems.add(`${path}.constraint_family`, "must be a string");
    }
    if (typeof row.governs !== "string") {
      problems.add(`${path}.governs`, "must be a string");
    }
    checkEnum(problems, `${path}.rule_status_today`, row.rule_status_today, COVERAGE_MATRIX_RULE_STATUSES);
    if (typeof row.blocks_buildable_envelope !== "boolean") {
      problems.add(`${path}.blocks_buildable_envelope`, "must be a boolean");
    }
  });
}

function checkIntegrityCheck(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("integrity_check", "required object is missing or not an object");
    return;
  }
  checkExactKeys(problems, "integrity_check", value, INTEGRITY_KEYS);
  if (typeof value.performed !== "boolean") {
    problems.add("integrity_check.performed", "must be a boolean");
  }
  if (!(value.agreed === null || typeof value.agreed === "boolean")) {
    problems.add("integrity_check.agreed", "must be a boolean or null");
  }
  if (!isFiniteNumber(value.tolerance)) {
    problems.add("integrity_check.tolerance", "must be a finite number");
  }
  for (const key of ["method", "note"] as const) {
    if (typeof value[key] !== "string") {
      problems.add(`integrity_check.${key}`, "must be a string");
    }
  }
}

/**
 * Validate an HTTP-200 body against the canonical scenario schema. Returns the
 * typed document ONLY when EVERY documented check passes; otherwise a bounded
 * problem list. A `verified` coverage_status/rule_status, a non-positive/null-less
 * cap, an out-of-shape nested object, or any unexpected property is rejected, so
 * an invalid payload can never reach the render layer.
 */
export function validateScenarioDocument(body: unknown): ScenarioValidationResult {
  const problems = new Problems();
  if (!isRecord(body)) {
    return { ok: false, problems: ["scenario: response body is not a JSON object"] };
  }

  // Root additionalProperties:false + all 16 required keys present.
  checkExactKeys(problems, "", body, TOP_LEVEL_REQUIRED, TOP_LEVEL_OPTIONAL);
  if ("_expected_failure" in body && typeof body._expected_failure !== "string") {
    problems.add("_expected_failure", "must be a string when present");
  }

  if (body.contract_version !== "1.0.0") {
    problems.add("contract_version", 'must be the string "1.0.0"');
  }
  checkEnum(problems, "scenario_kind", body.scenario_kind, SCENARIO_KINDS);
  checkEnum(problems, "coverage_status", body.coverage_status, SCENARIO_COVERAGE_STATUSES);
  checkEnum(problems, "data_completeness", body.data_completeness, SCENARIO_DATA_COMPLETENESS_VALUES);
  for (const key of ["needs_review", "professional_review_required"] as const) {
    if (typeof body[key] !== "boolean") {
      problems.add(key, "must be a boolean");
    }
  }
  if (!isNonEmptyString(body.not_verified_disclaimer)) {
    problems.add("not_verified_disclaimer", "must be a non-empty string");
  }
  checkEvaluatedInput(problems, body.evaluated_input);

  if (!Array.isArray(body.constraints)) {
    problems.add("constraints", "must be an array");
  } else {
    body.constraints.forEach((constraint, index) =>
      checkConstraint(problems, `constraints[${index}]`, constraint),
    );
  }

  // Schema: null OR a finite number strictly > 0 (exclusiveMinimum 0). Reject
  // -1, 0, NaN, ±Infinity.
  if (
    !(
      body.draft_zoning_floor_area_cap_sq_ft === null ||
      (isFiniteNumber(body.draft_zoning_floor_area_cap_sq_ft) &&
        body.draft_zoning_floor_area_cap_sq_ft > 0)
    )
  ) {
    problems.add(
      "draft_zoning_floor_area_cap_sq_ft",
      "must be null or a finite number strictly greater than 0",
    );
  }
  if (!(body.cap_label === null || isNonEmptyString(body.cap_label))) {
    problems.add("cap_label", "must be a non-empty string or null");
  }
  checkCapProvenance(problems, body.cap_provenance);

  if (!Array.isArray(body.assumptions)) {
    problems.add("assumptions", "must be an array");
  } else {
    body.assumptions.forEach((assumption, index) =>
      checkAssumption(problems, `assumptions[${index}]`, assumption),
    );
  }
  checkStringArray(problems, "reasons", body.reasons);
  checkCoverageMatrix(problems, body.coverage_matrix);
  checkIntegrityCheck(problems, body.integrity_check);

  if (problems.list.length > 0) {
    return { ok: false, problems: problems.list };
  }
  return { ok: true, document: body as unknown as Scenario };
}
