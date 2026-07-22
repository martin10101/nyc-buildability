/**
 * Canonical rule-evaluation contract vocabulary + runtime validator for the
 * web client (task M4-T005 phase 3).
 *
 * The ONLY type vocabulary for a draft rule-evaluation result is the GENERATED
 * module packages/contracts/generated/rule_evaluation.ts (M4-T005 phase 1,
 * regenerated deterministically from packages/contracts/schemas/v1/
 * rule_evaluation.schema.json; the contracts-typegen CI job fails on any
 * drift). This file consumes those types the EXACT same way src/lib/contract.ts
 * consumes property_profile.ts — a type-only relative import that is erased at
 * build time, so the Next.js bundle never compiles a file outside apps/web and
 * no schema is ever forked here.
 *
 * It then provides a RUNTIME validator that mirrors src/lib/validate-profile.ts:
 * every HTTP-200 rule-evaluation body is checked against the documented key set
 * and the contract-locked enums BEFORE anything renders. FAILURE IS TOTAL — the
 * caller receives only a bounded problem list, never a partially-usable
 * document — so nothing can be drawn from an invalid payload.
 *
 * The DRAFT vocabulary deliberately EXCLUDES `verified`: a draft rule result is
 * never Verified (PRD sections 10-12). A body whose top-level coverage_status is
 * `verified` fails validation here and can never reach the screen.
 *
 * No legal logic lives here (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md): this file
 * checks SHAPE, never meaning, and never rewrites a value.
 */

import type {
  BaseDistrictCandidate,
  CoverageStatus,
  DataCompleteness,
  DraftCoverageStatus,
  EvaluatedInput,
  EvaluationTrace,
  FamilyCoverage,
  RuleConflict,
  RuleEvaluation,
  SpatialContext,
  SpatialUncertainty,
} from "../../../../packages/contracts/generated/rule_evaluation";

export type {
  BaseDistrictCandidate,
  CoverageStatus,
  DataCompleteness,
  DraftCoverageStatus,
  EvaluatedInput,
  EvaluationTrace,
  FamilyCoverage,
  RuleConflict,
  RuleEvaluation,
  SpatialContext,
  SpatialUncertainty,
};

// ---------------------------------------------------------------------------
// Runtime enum arrays, exhaustively locked to the generated unions with the
// same two-way `MutuallyEqual` proof src/lib/contract.ts uses: tsc fails here
// on either direction of drift, so the arrays can never silently diverge from
// the generated vocabulary.
// ---------------------------------------------------------------------------

/** The closed set of draft coverage statuses — `verified` is intentionally
 * absent (a draft result is never Verified). */
export const DRAFT_COVERAGE_STATUSES = [
  "conditional",
  "professional_review_required",
  "data_conflict",
  "unsupported",
  "not_applicable",
] as const satisfies readonly DraftCoverageStatus[];

export const DATA_COMPLETENESS_VALUES = [
  "complete",
  "missing_noncritical",
  "missing_critical",
] as const satisfies readonly DataCompleteness[];

export const COVERAGE_SOURCES = [
  "rule_evaluator",
  "integration_fail_safe",
] as const satisfies readonly RuleEvaluation["coverage_source"][];

export const FAIL_SAFE_REASONS = [
  "spatial_intersection_absent",
  "spatial_context_incomplete",
  "data_conflict",
  "geometry_uncertain",
  "inconsistent_confident_geometry",
  "rule_conflict",
] as const satisfies readonly NonNullable<RuleEvaluation["fail_safe_reason"]>[];

export const RULE_LIFECYCLE_STATUSES = [
  "discovered",
  "extracted_draft",
  "needs_review",
  "published",
] as const satisfies readonly (RuleEvaluation["rule_lifecycle_statuses"][number])[];

/** Two-way equality proof: `true` only when A and B are the same union. */
type MutuallyEqual<A, B> = [A] extends [B] ? ([B] extends [A] ? true : never) : never;

/** Compile-time exhaustiveness proof (exported so it is never "unused"): any
 * array above that misses a member of its generated union makes the
 * corresponding tuple slot `never` and fails tsc. */
export type RuleEvalEnumAssertions = [
  MutuallyEqual<DraftCoverageStatus, (typeof DRAFT_COVERAGE_STATUSES)[number]>,
  MutuallyEqual<DataCompleteness, (typeof DATA_COMPLETENESS_VALUES)[number]>,
  MutuallyEqual<RuleEvaluation["coverage_source"], (typeof COVERAGE_SOURCES)[number]>,
  MutuallyEqual<
    NonNullable<RuleEvaluation["fail_safe_reason"]>,
    (typeof FAIL_SAFE_REASONS)[number]
  >,
  MutuallyEqual<
    RuleEvaluation["rule_lifecycle_statuses"][number],
    (typeof RULE_LIFECYCLE_STATUSES)[number]
  >,
];

export const MAX_REPORTED_PROBLEMS = 20;

export type RuleEvaluationValidationResult =
  | { ok: true; document: RuleEvaluation }
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
    problems.add(
      "evaluated_input.profile_contract_version",
      "must be a non-empty string",
    );
  }
  if (
    typeof value.input_fingerprint !== "string" ||
    !/^sha256:[0-9a-f]{64}$/.test(value.input_fingerprint)
  ) {
    problems.add(
      "evaluated_input.input_fingerprint",
      "must match ^sha256:[0-9a-f]{64}$",
    );
  }
  const provenance = value.input_provenance;
  if (!isRecord(provenance)) {
    problems.add("evaluated_input.input_provenance", "must be an object");
  } else {
    checkStringArray(
      problems,
      "evaluated_input.input_provenance.zoning_district",
      provenance.zoning_district,
    );
    checkStringArray(
      problems,
      "evaluated_input.input_provenance.lot_area_sq_ft",
      provenance.lot_area_sq_ft,
    );
  }
}

function checkSpatialUncertainty(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("spatial_uncertainty", "required object is missing or not an object");
    return;
  }
  if (typeof value.professional_review_required !== "boolean") {
    problems.add(
      "spatial_uncertainty.professional_review_required",
      "must be a boolean",
    );
  }
  checkStringArray(problems, "spatial_uncertainty.review_reasons", value.review_reasons);
  checkStringArray(problems, "spatial_uncertainty.notes", value.notes);
  if (!Array.isArray(value.base_district_candidates)) {
    problems.add(
      "spatial_uncertainty.base_district_candidates",
      "must be an array",
    );
    return;
  }
  value.base_district_candidates.forEach((candidate, index) => {
    const path = `spatial_uncertainty.base_district_candidates[${index}]`;
    if (!isRecord(candidate)) {
      problems.add(path, "must be an object");
      return;
    }
    for (const key of ["share_min", "share_point", "share_max"] as const) {
      const share = candidate[key];
      if (!(share === null || typeof share === "number")) {
        problems.add(`${path}.${key}`, "must be a number or null");
      }
    }
  });
}

function checkFamilyCoverage(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("family_coverage", "required object is missing or not an object");
    return;
  }
  if (!isNonEmptyString(value.family)) {
    problems.add("family_coverage.family", "must be a non-empty string");
  }
  checkEnum(
    problems,
    "family_coverage.coverage_status",
    value.coverage_status,
    DRAFT_COVERAGE_STATUSES,
  );
  if (typeof value.note !== "string") {
    problems.add("family_coverage.note", "must be a string");
  }
}

function checkRuleConflict(problems: Problems, value: unknown): void {
  if (value === null) return;
  if (!isRecord(value)) {
    problems.add("rule_conflict", "must be an object or null");
    return;
  }
  if (typeof value.conflict !== "boolean") {
    problems.add("rule_conflict.conflict", "must be a boolean");
  }
  if (!isNonEmptyString(value.family)) {
    problems.add("rule_conflict.family", "must be a non-empty string");
  }
  checkStringArray(
    problems,
    "rule_conflict.competing_output_names",
    value.competing_output_names,
  );
  if (!Array.isArray(value.competing_rules)) {
    problems.add("rule_conflict.competing_rules", "must be an array");
  }
}

/**
 * Validate an HTTP-200 body against the generated rule_evaluation types.
 * Returns the typed document ONLY when every documented check passes. A
 * `verified` top-level coverage_status is rejected (draft is never Verified).
 */
export function validateRuleEvaluationDocument(
  body: unknown,
): RuleEvaluationValidationResult {
  const problems = new Problems();
  if (!isRecord(body)) {
    return { ok: false, problems: ["rule_evaluation: response body is not a JSON object"] };
  }

  if (body.contract_version !== "1.0.0") {
    problems.add("contract_version", 'must be the string "1.0.0"');
  }
  checkEvaluatedInput(problems, body.evaluated_input);
  checkEnum(problems, "coverage_status", body.coverage_status, DRAFT_COVERAGE_STATUSES);
  checkEnum(problems, "coverage_source", body.coverage_source, COVERAGE_SOURCES);
  if (
    !(
      body.data_completeness === null ||
      (typeof body.data_completeness === "string" &&
        (DATA_COMPLETENESS_VALUES as readonly string[]).includes(body.data_completeness))
    )
  ) {
    problems.add("data_completeness", "must be a data-completeness enum value or null");
  }
  for (const key of [
    "needs_review",
    "professional_review_required",
    "fail_safe",
  ] as const) {
    if (typeof body[key] !== "boolean") {
      problems.add(key, "must be a boolean");
    }
  }
  if (
    !(
      body.fail_safe_reason === null ||
      (typeof body.fail_safe_reason === "string" &&
        (FAIL_SAFE_REASONS as readonly string[]).includes(body.fail_safe_reason))
    )
  ) {
    problems.add("fail_safe_reason", "must be a documented fail-safe reason or null");
  }
  checkStringArray(problems, "rule_lifecycle_statuses", body.rule_lifecycle_statuses);
  if (!isNonEmptyString(body.not_verified_disclaimer)) {
    problems.add("not_verified_disclaimer", "must be a non-empty string");
  }
  if (!(body.zoning_district === null || isNonEmptyString(body.zoning_district))) {
    problems.add("zoning_district", "must be a non-empty string or null");
  }
  if (!(body.lot_area_sq_ft === null || typeof body.lot_area_sq_ft === "number")) {
    problems.add("lot_area_sq_ft", "must be a number or null");
  }
  if (!(body.lot_area_source === null || isNonEmptyString(body.lot_area_source))) {
    problems.add("lot_area_source", "must be a non-empty string or null");
  }
  if (!(body.spatial_context === null || isRecord(body.spatial_context))) {
    problems.add("spatial_context", "must be an object or null");
  }
  checkSpatialUncertainty(problems, body.spatial_uncertainty);
  if (!Array.isArray(body.evaluations)) {
    problems.add("evaluations", "must be an array");
  }
  checkFamilyCoverage(problems, body.family_coverage);
  checkStringArray(problems, "reasons", body.reasons);
  checkRuleConflict(problems, body.rule_conflict);

  if (problems.list.length > 0) {
    return { ok: false, problems: problems.list };
  }
  return { ok: true, document: body as unknown as RuleEvaluation };
}
