/**
 * Canonical scenario contract vocabulary + runtime validator for the web
 * client (task M5-T004).
 *
 * The ONLY type vocabulary for a scenario document is the GENERATED module
 * packages/contracts/generated/scenario.ts (M5-T001, regenerated
 * deterministically from packages/contracts/schemas/v1/scenario.schema.json;
 * the contracts-typegen CI job fails on any drift). This file consumes those
 * types the EXACT same way src/lib/rule-evaluation-contract.ts consumes
 * rule_evaluation.ts — a type-only relative import erased at build time, so the
 * Next.js bundle never compiles a file outside apps/web and no schema is forked
 * here.
 *
 * It then provides a RUNTIME validator mirroring src/lib/validate-profile.ts
 * and src/lib/rule-evaluation-contract.ts: every HTTP-200 scenario body is
 * checked against the documented key set and the contract-locked enums BEFORE
 * anything renders. FAILURE IS TOTAL — the caller receives only a bounded
 * problem list, never a partially-usable document — so nothing can be drawn
 * from an invalid payload.
 *
 * The DRAFT vocabulary deliberately EXCLUDES `verified`: a scenario is never
 * Verified (PRD sections 10-12). A body whose coverage_status is `verified`
 * fails validation here and can never reach the screen.
 *
 * No legal logic lives here (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md): this file
 * checks SHAPE, never meaning, and never rewrites a value.
 */

import type {
  CapProvenance,
  CoverageMatrixRow,
  DataCompleteness,
  DraftCoverageStatus,
  IntegrityCheck,
  Scenario,
  ScenarioAssumption,
  ScenarioCitation,
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
  ScenarioCitation,
  ScenarioConstraint,
  ScenarioEvaluatedInput,
};

// ---------------------------------------------------------------------------
// Runtime enum arrays, exhaustively locked to the generated unions with the
// same two-way `MutuallyEqual` proof src/lib/rule-evaluation-contract.ts uses:
// tsc fails here on either direction of drift, so the arrays can never silently
// diverge from the generated vocabulary.
// ---------------------------------------------------------------------------

/** The closed set of scenario coverage statuses — `verified` is intentionally
 * absent (a scenario is never Verified). */
export const SCENARIO_COVERAGE_STATUSES = [
  "conditional",
  "professional_review_required",
  "data_conflict",
  "unsupported",
  "not_applicable",
] as const satisfies readonly DraftCoverageStatus[];

export const SCENARIO_KINDS = [
  "preliminary",
  "no_scenario",
  "unsupported",
] as const satisfies readonly Scenario["scenario_kind"][];

export const DATA_COMPLETENESS_VALUES = [
  "complete",
  "missing_noncritical",
  "missing_critical",
] as const satisfies readonly DataCompleteness[];

export const CONSTRAINT_STATES = [
  "known",
  "draft",
  "missing",
  "conflicting",
  "unsupported",
  "professional_review_required",
] as const satisfies readonly ScenarioConstraint["state"][];

export const COVERAGE_MATRIX_STATUSES = [
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
  MutuallyEqual<Scenario["scenario_kind"], (typeof SCENARIO_KINDS)[number]>,
  MutuallyEqual<DataCompleteness, (typeof DATA_COMPLETENESS_VALUES)[number]>,
  MutuallyEqual<ScenarioConstraint["state"], (typeof CONSTRAINT_STATES)[number]>,
  MutuallyEqual<
    CoverageMatrixRow["rule_status_today"],
    (typeof COVERAGE_MATRIX_STATUSES)[number]
  >,
];

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
  if (!(value.bbl === null || isNonEmptyString(value.bbl))) {
    problems.add("evaluated_input.bbl", "must be a non-empty string or null");
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
        /^sha256:[0-9a-f]{64}$/.test(value.input_fingerprint))
    )
  ) {
    problems.add(
      "evaluated_input.input_fingerprint",
      "must be null or match ^sha256:[0-9a-f]{64}$",
    );
  }
}

function checkConstraints(problems: Problems, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add("constraints", "must be an array");
    return;
  }
  value.forEach((constraint, index) => {
    const path = `constraints[${index}]`;
    if (!isRecord(constraint)) {
      problems.add(path, "must be an object");
      return;
    }
    if (!isNonEmptyString(constraint.key)) {
      problems.add(`${path}.key`, "must be a non-empty string");
    }
    checkEnum(problems, `${path}.state`, constraint.state, CONSTRAINT_STATES);
    if (!("value" in constraint)) {
      problems.add(`${path}.value`, "required key is missing");
    }
    if (!(constraint.unit === null || typeof constraint.unit === "string")) {
      problems.add(`${path}.unit`, "must be a string or null");
    }
    checkEnum(
      problems,
      `${path}.data_completeness`,
      constraint.data_completeness,
      DATA_COMPLETENESS_VALUES,
    );
    if (!("provenance" in constraint)) {
      problems.add(`${path}.provenance`, "required key is missing");
    }
    if (typeof constraint.note !== "string") {
      problems.add(`${path}.note`, "must be a string");
    }
  });
}

function checkAssumptions(problems: Problems, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add("assumptions", "must be an array");
    return;
  }
  value.forEach((assumption, index) => {
    const path = `assumptions[${index}]`;
    if (!isRecord(assumption)) {
      problems.add(path, "must be an object");
      return;
    }
    if (!isNonEmptyString(assumption.key)) {
      problems.add(`${path}.key`, "must be a non-empty string");
    }
    if (typeof assumption.assumption_type !== "string") {
      problems.add(`${path}.assumption_type`, "must be a string");
    }
    if (typeof assumption.rationale !== "string") {
      problems.add(`${path}.rationale`, "must be a string");
    }
  });
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
    if (!isNonEmptyString(row.constraint_family)) {
      problems.add(`${path}.constraint_family`, "must be a non-empty string");
    }
    if (typeof row.governs !== "string") {
      problems.add(`${path}.governs`, "must be a string");
    }
    checkEnum(problems, `${path}.rule_status_today`, row.rule_status_today, COVERAGE_MATRIX_STATUSES);
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
  if (typeof value.performed !== "boolean") {
    problems.add("integrity_check.performed", "must be a boolean");
  }
  if (!(value.agreed === null || typeof value.agreed === "boolean")) {
    problems.add("integrity_check.agreed", "must be a boolean or null");
  }
  if (typeof value.tolerance !== "number") {
    problems.add("integrity_check.tolerance", "must be a number");
  }
  if (typeof value.method !== "string") {
    problems.add("integrity_check.method", "must be a string");
  }
  if (typeof value.note !== "string") {
    problems.add("integrity_check.note", "must be a string");
  }
}

/**
 * Validate an HTTP-200 body against the generated scenario types. Returns the
 * typed document ONLY when every documented check passes. A `verified`
 * coverage_status is rejected (a scenario is never Verified).
 */
export function validateScenarioDocument(body: unknown): ScenarioValidationResult {
  const problems = new Problems();
  if (!isRecord(body)) {
    return { ok: false, problems: ["scenario: response body is not a JSON object"] };
  }

  if (body.contract_version !== "1.0.0") {
    problems.add("contract_version", 'must be the string "1.0.0"');
  }
  checkEnum(problems, "scenario_kind", body.scenario_kind, SCENARIO_KINDS);
  checkEnum(problems, "coverage_status", body.coverage_status, SCENARIO_COVERAGE_STATUSES);
  checkEnum(problems, "data_completeness", body.data_completeness, DATA_COMPLETENESS_VALUES);
  for (const key of ["needs_review", "professional_review_required"] as const) {
    if (typeof body[key] !== "boolean") {
      problems.add(key, "must be a boolean");
    }
  }
  if (!isNonEmptyString(body.not_verified_disclaimer)) {
    problems.add("not_verified_disclaimer", "must be a non-empty string");
  }
  checkEvaluatedInput(problems, body.evaluated_input);
  checkConstraints(problems, body.constraints);
  if (
    !(
      body.draft_zoning_floor_area_cap_sq_ft === null ||
      typeof body.draft_zoning_floor_area_cap_sq_ft === "number"
    )
  ) {
    problems.add("draft_zoning_floor_area_cap_sq_ft", "must be a number or null");
  }
  if (!(body.cap_label === null || isNonEmptyString(body.cap_label))) {
    problems.add("cap_label", "must be a non-empty string or null");
  }
  if (!(body.cap_provenance === null || isRecord(body.cap_provenance))) {
    problems.add("cap_provenance", "must be an object or null");
  }
  checkAssumptions(problems, body.assumptions);
  checkStringArray(problems, "reasons", body.reasons);
  checkCoverageMatrix(problems, body.coverage_matrix);
  checkIntegrityCheck(problems, body.integrity_check);

  if (problems.list.length > 0) {
    return { ok: false, problems: problems.list };
  }
  return { ok: true, document: body as unknown as Scenario };
}
