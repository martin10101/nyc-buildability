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
 * every HTTP-200 rule-evaluation body has each DOCUMENTED key checked for the
 * right shape and contract-locked enum value BEFORE anything renders. This is a
 * POSITIVE-SHAPE check, not a closed-schema one: an unknown or extra top-level
 * key is NOT rejected (there is no client-side additionalProperties
 * enforcement), so the server stays authoritative on the full closed schema.
 * FAILURE IS TOTAL — when a documented key is missing or malformed the caller
 * receives only a bounded problem list, never a partially-usable document — so
 * nothing can be drawn from an invalid payload.
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
  // M5-T058 (contract 1.2.0): a condo billing BBL whose base lot could not be
  // resolved to a single lot (multi-lot / unresolved / typed-error outcome). The
  // honest name for an absent substrate a condo cause produced; a genuinely
  // absent non-condo substrate keeps spatial_intersection_absent.
  "condo_base_lot_unresolved",
] as const satisfies readonly NonNullable<RuleEvaluation["fail_safe_reason"]>[];

export const RULE_LIFECYCLE_STATUSES = [
  "discovered",
  "extracted_draft",
  "needs_review",
  "published",
] as const satisfies readonly (RuleEvaluation["rule_lifecycle_statuses"][number])[];

/** The closed set of published rule_evaluation contract versions. M5-T037: the
 * additive 1.1.0 bump appends the OPTIONAL wide_street block. M5-T058: the
 * additive 1.2.0 bump appends the OPTIONAL substrate_substitution block (the
 * condo billing-BBL -> base-lot substitution stamp). 1.0.0 and 1.1.0 stay valid
 * because both blocks are optional and every earlier version remains admitted. */
export const RULE_EVALUATION_CONTRACT_VERSIONS = [
  "1.0.0",
  "1.1.0",
  "1.2.0",
] as const satisfies readonly RuleEvaluation["contract_version"][];

type WideStreetBlock = NonNullable<RuleEvaluation["wide_street"]>;

/** The typed wide-street determination states (never collapsed). */
export const WIDE_STREET_DETERMINATION_STATES = [
  "within_100ft_of_wide_street",
  "not_within_100ft_of_wide_street",
  "professional_review_required",
] as const satisfies readonly WideStreetBlock["determination_state"][];

/** Which ZR 23-22 conditional-FAR row fired (`none` = no bonus granted). */
export const WIDE_STREET_FAR_ROWS = [
  "wide_street_row",
  "standard_row",
  "none",
] as const satisfies readonly WideStreetBlock["far_row"][];

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

/** Array whose items are strings, or (when ``allowNull``) strings-or-null — the
 * two shapes the D-052 provenance arrays use. */
function checkArrayOf(
  problems: Problems,
  path: string,
  value: unknown,
  allowNull: boolean,
): void {
  if (!Array.isArray(value)) {
    problems.add(path, "must be an array");
    return;
  }
  value.forEach((item, index) => {
    if (!(typeof item === "string" || (allowNull && item === null))) {
      problems.add(
        `${path}[${index}]`,
        allowNull ? "must be a string or null" : "must be a string",
      );
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
 * Validate the OPTIONAL wide_street block (contract 1.1.0). ABSENT is valid (a
 * 1.0.0-shaped body omits it); when PRESENT every documented key of the DRAFT
 * D-052 provenance summary is shape-checked, so a malformed block fails TOTAL
 * validation and never renders. No legal meaning is judged here — shape only.
 */
function checkWideStreet(problems: Problems, value: unknown): void {
  if (value === undefined) return;
  if (!isRecord(value)) {
    problems.add("wide_street", "must be an object when present");
    return;
  }
  checkEnum(
    problems,
    "wide_street.determination_state",
    value.determination_state,
    WIDE_STREET_DETERMINATION_STATES,
  );
  checkEnum(problems, "wide_street.far_row", value.far_row, WIDE_STREET_FAR_ROWS);
  if (
    !(
      value.governing_max_residential_far === null ||
      typeof value.governing_max_residential_far === "number"
    )
  ) {
    problems.add(
      "wide_street.governing_max_residential_far",
      "must be a number or null",
    );
  }
  for (const key of [
    "coverage_hint",
    "draft_label",
    "fallback_direction_note",
    "reason",
  ] as const) {
    if (!isNonEmptyString(value[key])) {
      problems.add(`wide_street.${key}`, "must be a non-empty string");
    }
  }
  for (const key of ["exceptions_checked", "named_street_override_pending"] as const) {
    if (typeof value[key] !== "boolean") {
      problems.add(`wide_street.${key}`, "must be a boolean");
    }
  }
  for (const key of [
    "policy_decision_states",
    "interpreted_bounds_summaries",
    "classification_reasons",
  ] as const) {
    checkArrayOf(problems, `wide_street.${key}`, value[key], false);
  }
  for (const key of ["original_labels", "source_versions", "matched_geometry_refs"] as const) {
    checkArrayOf(problems, `wide_street.${key}`, value[key], true);
  }
}

/**
 * Validate the OPTIONAL substrate_substitution block (contract 1.2.0, M5-T058).
 * ABSENT is valid (a 1.0.0/1.1.0-shaped body omits it); when PRESENT every
 * documented key of the condo billing-BBL -> base-lot substitution stamp is
 * shape-checked, so a malformed block fails TOTAL validation and never renders.
 * A RECORD of a documented resolution, never a computed allowance — no legal or
 * substitution meaning is judged here, only shape. Positive-shape only: the
 * server owns the closed schema (additionalProperties:false).
 */
function checkSubstrateSubstitution(problems: Problems, value: unknown): void {
  if (value === undefined) return;
  if (!isRecord(value)) {
    problems.add("substrate_substitution", "must be an object when present");
    return;
  }
  for (const key of ["entered_bbl", "analyzed_bbl", "note"] as const) {
    if (!isNonEmptyString(value[key])) {
      problems.add(`substrate_substitution.${key}`, "must be a non-empty string");
    }
  }
  for (const key of ["condo_key", "resolution_path", "retrieved_at"] as const) {
    if (!(value[key] === null || typeof value[key] === "string")) {
      problems.add(`substrate_substitution.${key}`, "must be a string or null");
    }
  }
  if (!(value.source_id === null || isNonEmptyString(value.source_id))) {
    problems.add("substrate_substitution.source_id", "must be a non-empty string or null");
  }
  checkStringArray(problems, "substrate_substitution.dataset_ids", value.dataset_ids);
  const mixed = value.mixed_substrate;
  if (!isRecord(mixed)) {
    problems.add("substrate_substitution.mixed_substrate", "must be an object");
    return;
  }
  for (const key of ["lot_facts_substrate", "identity_facts_substrate", "note"] as const) {
    if (!isNonEmptyString(mixed[key])) {
      problems.add(`substrate_substitution.mixed_substrate.${key}`, "must be a non-empty string");
    }
  }
}

/**
 * Validate an HTTP-200 body against the generated rule_evaluation types.
 * Returns the typed document ONLY when every documented key passes its shape
 * and enum check. Unknown/extra top-level keys are not rejected (positive-shape
 * check; the server owns the closed schema). A `verified` top-level
 * coverage_status is rejected (draft is never Verified).
 */
export function validateRuleEvaluationDocument(
  body: unknown,
): RuleEvaluationValidationResult {
  const problems = new Problems();
  if (!isRecord(body)) {
    return { ok: false, problems: ["rule_evaluation: response body is not a JSON object"] };
  }

  checkEnum(
    problems,
    "contract_version",
    body.contract_version,
    RULE_EVALUATION_CONTRACT_VERSIONS,
  );
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
  checkWideStreet(problems, body.wide_street);
  checkSubstrateSubstitution(problems, body.substrate_substitution);

  if (problems.list.length > 0) {
    return { ok: false, problems: problems.list };
  }
  return { ok: true, document: body as unknown as RuleEvaluation };
}
