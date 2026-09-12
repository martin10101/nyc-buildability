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
 *
 * DEPTH (M5-T004 rework, G4 finding 2 / G5 findings 1 and 3): the validator now
 * checks what it always claimed to.
 *   - `cap_provenance` is type-checked FIELD BY FIELD before the cast, and is
 *     REQUIRED to be non-null whenever a cap is surfaced. Previously a body
 *     carrying `cap_provenance: {"note":"tbd"}` passed and rendered a 15,000 sq
 *     ft maximum with an EMPTY optimized-objective name — violating
 *     .claude/rules/frontend-web.md:13 ("never show 'best' without naming the
 *     optimized objective").
 *   - every schema-declared array is bounded at MAX_DOCUMENT_ARRAY_LENGTH and
 *     REJECTED (never truncated) beyond it.
 *   - unknown keys are rejected at every object level, as
 *     `additionalProperties: false` requires and as this docstring already
 *     claimed.
 *   - `needs_review` is pinned to `true` (schema: "Always true").
 *
 * The generic check primitives live in ./scenario-contract-checks, which owns
 * the body-independence invariant for the problem list.
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
import {
  MAX_DOCUMENT_ARRAY_LENGTH,
  MAX_REPORTED_PROBLEMS,
  Problems,
  checkBoolean,
  checkBoundedArray,
  checkEnum,
  checkNoUnknownKeys,
  checkNonEmptyString,
  checkNullableString,
  checkOptionalBoundedArray,
  checkRequiredScalar,
  checkString,
  checkTokenRepresentable,
  isNonEmptyString,
  isRecord,
} from "./scenario-contract-checks";

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

/** Re-exported so the public import surface of this module is unchanged by the
 * modularity split (CLAUDE.md principle 16: preserve public imports through a
 * compatibility facade). */
export { MAX_DOCUMENT_ARRAY_LENGTH, MAX_REPORTED_PROBLEMS };

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

/** The 4-value rule-status enum `cap_provenance.rule_status` is pinned to. */
export const CAP_RULE_STATUSES = [
  "discovered",
  "extracted_draft",
  "needs_review",
  "published",
] as const satisfies readonly CapProvenance["rule_status"][];

/** The C1 unused-draft-zoning-floor-area section (D-041 / M5-T017). The
 * generated module types the section inline on `Scenario`, so this alias is the
 * one place its shape is named for the mirror validator. */
export type UnusedFloorAreaSection = Scenario["unused_draft_zoning_floor_area"];

/** The 3-value `unused_draft_zoning_floor_area.state` enum. */
export const UNUSED_FLOOR_AREA_STATES = [
  "computed",
  "over_built",
  "not_computable",
] as const satisfies readonly UnusedFloorAreaSection["state"][];

/** The 3 typed `not_computable_reason` values (the non-null branch of the
 * enum-or-null field). */
export const UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS = [
  "missing_existing_building_area",
  "existing_building_area_unusable",
  "no_draft_far_cap",
] as const satisfies readonly NonNullable<
  UnusedFloorAreaSection["not_computable_reason"]
>[];

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
  MutuallyEqual<CapProvenance["rule_status"], (typeof CAP_RULE_STATUSES)[number]>,
  MutuallyEqual<
    UnusedFloorAreaSection["state"],
    (typeof UNUSED_FLOOR_AREA_STATES)[number]
  >,
  MutuallyEqual<
    NonNullable<UnusedFloorAreaSection["not_computable_reason"]>,
    (typeof UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS)[number]
  >,
];

// ---------------------------------------------------------------------------
// Documented key sets — the schema declares `additionalProperties: false` on
// every object, so an undocumented key is a contract violation, not a tolerated
// extension. `_expected_failure` is a declared OPTIONAL top-level property of
// the schema (negative-fixture marker), so it is documented, not unknown.
// ---------------------------------------------------------------------------

const SCENARIO_KEYS = [
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
  "unused_draft_zoning_floor_area",
  "_expected_failure",
] as const;

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

const ASSUMPTION_KEYS = ["key", "assumption_type", "value", "unit", "rationale"] as const;

/** The C1 section's closed key set (schema $defs/unused_draft_zoning_floor_area,
 * additionalProperties:false). */
const UNUSED_FLOOR_AREA_KEYS = [
  "state",
  "unused_draft_zoning_floor_area_sq_ft",
  "unit",
  "label",
  "scope_note",
  "formula",
  "professional_review_required",
  "over_built_statement",
  "not_computable_reason",
  "inputs",
  "assumptions",
] as const;

/** The C1 `inputs` object closed key set (schema $defs/unused_floor_area_inputs). */
const UNUSED_FLOOR_AREA_INPUTS_KEYS = [
  "draft_zoning_floor_area_cap",
  "existing_building_floor_area",
] as const;

/** `inputs.draft_zoning_floor_area_cap` closed key set. */
const UNUSED_FLOOR_AREA_CAP_INPUT_KEYS = ["value_sq_ft", "unit", "provenance"] as const;

/** `inputs.existing_building_floor_area` closed key set. */
const UNUSED_FLOOR_AREA_EXISTING_INPUT_KEYS = [
  "value_sq_ft",
  "unit",
  "coverage_status",
  "provenance_ref",
  "provenance",
] as const;

const COVERAGE_MATRIX_ROW_KEYS = [
  "constraint_family",
  "governs",
  "rule_status_today",
  "blocks_buildable_envelope",
] as const;

const INTEGRITY_CHECK_KEYS = [
  "performed",
  "agreed",
  "tolerance",
  "method",
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

const CITATION_KEYS = [
  "snapshot_id",
  "section",
  "quote",
  "last_amended",
  "provenance",
] as const;

/** Weakly-typed (`unknown`) constraint-provenance sub-arrays the display layer
 * maps over. The schema leaves `provenance` open, so a non-array here is not a
 * violation — but an over-long array still is, because the renderers walk it. */
const PROVENANCE_ARRAY_KEYS = [
  "base_district_candidates",
  "competing_rules",
  "competing_output_names",
  "provenance_refs",
  "resolved",
  "review_reasons",
] as const;

export type ScenarioValidationResult =
  | { ok: true; document: Scenario }
  | { ok: false; problems: string[] };

// ---------------------------------------------------------------------------
// Per-field checks. Each records problems against the documented path and
// never rewrites, coerces, or defaults a value.
// ---------------------------------------------------------------------------

function checkEvaluatedInput(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("evaluated_input", "required object is missing or not an object");
    return;
  }
  checkNoUnknownKeys(problems, "evaluated_input", value, EVALUATED_INPUT_KEYS);
  if (!(value.bbl === null || isNonEmptyString(value.bbl))) {
    problems.add("evaluated_input.bbl", "must be a non-empty string or null");
  }
  checkNonEmptyString(
    problems,
    "evaluated_input.profile_contract_version",
    value.profile_contract_version,
  );
  checkTokenRepresentable(
    problems,
    "evaluated_input.profile_contract_version",
    value.profile_contract_version,
  );
  checkNonEmptyString(
    problems,
    "evaluated_input.rule_evaluation_contract_version",
    value.rule_evaluation_contract_version,
  );
  checkTokenRepresentable(
    problems,
    "evaluated_input.rule_evaluation_contract_version",
    value.rule_evaluation_contract_version,
  );
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
  const list = checkBoundedArray(problems, "constraints", value);
  if (!list) return;
  list.forEach((constraint, index) => {
    const path = `constraints[${index}]`;
    if (!isRecord(constraint)) {
      problems.add(path, "must be an object");
      return;
    }
    checkNoUnknownKeys(problems, path, constraint, CONSTRAINT_KEYS);
    checkNonEmptyString(problems, `${path}.key`, constraint.key);
    checkTokenRepresentable(problems, `${path}.key`, constraint.key);
    checkEnum(problems, `${path}.state`, constraint.state, CONSTRAINT_STATES);
    // The schema pins `value` to number | string | boolean | null. Before this
    // check it was accepted as "key exists", so an OBJECT reached format.ts and
    // was JSON.stringify'd straight into the DOM (G5 finding 2).
    checkRequiredScalar(problems, `${path}.value`, constraint, "value");
    checkNullableString(problems, `${path}.unit`, constraint.unit);
    checkEnum(
      problems,
      `${path}.data_completeness`,
      constraint.data_completeness,
      DATA_COMPLETENESS_VALUES,
    );
    if (!("provenance" in constraint)) {
      problems.add(`${path}.provenance`, "required key is missing");
    } else {
      checkProvenanceArrays(problems, `${path}.provenance`, constraint.provenance);
    }
    checkString(problems, `${path}.note`, constraint.note);
  });
}

/** Bound every weakly-typed nested array the display layer maps over. The
 * schema leaves `provenance` open (`unknown | null`), so this bounds rather
 * than types it. */
function checkProvenanceArrays(
  problems: Problems,
  path: string,
  provenance: unknown,
): void {
  if (!isRecord(provenance)) return;
  for (const key of PROVENANCE_ARRAY_KEYS) {
    if (key in provenance) {
      checkOptionalBoundedArray(problems, `${path}.${key}`, provenance[key]);
    }
  }
}

/** Validate an assumptions array. Parametrised on `arrayPath` because the same
 * closed record shape ($defs/assumption) appears both at the scenario root
 * (`assumptions`) and inside the C1 section
 * (`unused_draft_zoning_floor_area.assumptions`). */
function checkAssumptions(problems: Problems, arrayPath: string, value: unknown): void {
  const list = checkBoundedArray(problems, arrayPath, value);
  if (!list) return;
  list.forEach((assumption, index) => {
    const path = `${arrayPath}[${index}]`;
    if (!isRecord(assumption)) {
      problems.add(path, "must be an object");
      return;
    }
    checkNoUnknownKeys(problems, path, assumption, ASSUMPTION_KEYS);
    checkNonEmptyString(problems, `${path}.key`, assumption.key);
    checkTokenRepresentable(problems, `${path}.key`, assumption.key);
    checkString(problems, `${path}.assumption_type`, assumption.assumption_type);
    // Schema-required and previously unchecked (G4 finding 2, "structural").
    checkRequiredScalar(problems, `${path}.value`, assumption, "value");
    checkNullableString(problems, `${path}.unit`, assumption.unit);
    checkString(problems, `${path}.rationale`, assumption.rationale);
  });
}

function checkReasons(problems: Problems, value: unknown): void {
  const list = checkBoundedArray(problems, "reasons", value);
  if (!list) return;
  list.forEach((item, index) => {
    checkString(problems, `reasons[${index}]`, item);
  });
}

function checkCoverageMatrix(problems: Problems, value: unknown): void {
  const list = checkBoundedArray(problems, "coverage_matrix", value);
  if (!list) return;
  list.forEach((row, index) => {
    const path = `coverage_matrix[${index}]`;
    if (!isRecord(row)) {
      problems.add(path, "must be an object");
      return;
    }
    checkNoUnknownKeys(problems, path, row, COVERAGE_MATRIX_ROW_KEYS);
    checkNonEmptyString(problems, `${path}.constraint_family`, row.constraint_family);
    checkTokenRepresentable(problems, `${path}.constraint_family`, row.constraint_family);
    checkString(problems, `${path}.governs`, row.governs);
    checkEnum(
      problems,
      `${path}.rule_status_today`,
      row.rule_status_today,
      COVERAGE_MATRIX_STATUSES,
    );
    checkBoolean(
      problems,
      `${path}.blocks_buildable_envelope`,
      row.blocks_buildable_envelope,
    );
  });
}

function checkIntegrityCheck(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("integrity_check", "required object is missing or not an object");
    return;
  }
  checkNoUnknownKeys(problems, "integrity_check", value, INTEGRITY_CHECK_KEYS);
  checkBoolean(problems, "integrity_check.performed", value.performed);
  if (!(value.agreed === null || typeof value.agreed === "boolean")) {
    problems.add("integrity_check.agreed", "must be a boolean or null");
  }
  if (typeof value.tolerance !== "number") {
    problems.add("integrity_check.tolerance", "must be a number");
  }
  checkString(problems, "integrity_check.method", value.method);
  checkString(problems, "integrity_check.note", value.note);
}

/** A JSON number-or-null that must be FINITE. The schema types every C1 value as
 * `number | null` and states "Never NaN/Infinity (strict JSON)"; JSON.parse can
 * never produce a non-finite number, but the validator takes `unknown`, so a
 * caller-constructed NaN/Infinity is rejected here rather than reaching a
 * `formatValue` that would render "NaN"/"Infinity" beside a legal figure. */
function checkNullableFiniteNumber(
  problems: Problems,
  path: string,
  value: unknown,
): void {
  if (!(value === null || (typeof value === "number" && Number.isFinite(value)))) {
    problems.add(path, "must be a finite number or null");
  }
}

/** A schema `type: ["object", "null"]` field. Arrays are excluded (`isRecord`
 * matches JSON-schema `object`, not `array`). */
function checkNullableObject(problems: Problems, path: string, value: unknown): void {
  if (!(value === null || isRecord(value))) {
    problems.add(path, "must be an object or null");
  }
}

/** The closed `unused_draft_zoning_floor_area.inputs` object
 * (schema $defs/unused_floor_area_inputs): the draft cap consumed verbatim and
 * the existing built floor area, each with its per-input provenance. Recorded on
 * every state, so a consumer always sees what was and was not available. */
function checkUnusedFloorAreaInputs(
  problems: Problems,
  path: string,
  value: unknown,
): void {
  if (!isRecord(value)) {
    problems.add(path, "required object is missing or not an object");
    return;
  }
  checkNoUnknownKeys(problems, path, value, UNUSED_FLOOR_AREA_INPUTS_KEYS);

  const capPath = `${path}.draft_zoning_floor_area_cap`;
  const capInput = value.draft_zoning_floor_area_cap;
  if (!isRecord(capInput)) {
    problems.add(capPath, "required object is missing or not an object");
  } else {
    checkNoUnknownKeys(problems, capPath, capInput, UNUSED_FLOOR_AREA_CAP_INPUT_KEYS);
    checkNullableFiniteNumber(problems, `${capPath}.value_sq_ft`, capInput.value_sq_ft);
    checkNullableString(problems, `${capPath}.unit`, capInput.unit);
    checkNullableObject(problems, `${capPath}.provenance`, capInput.provenance);
  }

  const existingPath = `${path}.existing_building_floor_area`;
  const existing = value.existing_building_floor_area;
  if (!isRecord(existing)) {
    problems.add(existingPath, "required object is missing or not an object");
  } else {
    checkNoUnknownKeys(
      problems,
      existingPath,
      existing,
      UNUSED_FLOOR_AREA_EXISTING_INPUT_KEYS,
    );
    checkNullableFiniteNumber(
      problems,
      `${existingPath}.value_sq_ft`,
      existing.value_sq_ft,
    );
    checkNullableString(problems, `${existingPath}.unit`, existing.unit);
    checkNullableString(
      problems,
      `${existingPath}.coverage_status`,
      existing.coverage_status,
    );
    checkNullableString(
      problems,
      `${existingPath}.provenance_ref`,
      existing.provenance_ref,
    );
    checkNullableObject(problems, `${existingPath}.provenance`, existing.provenance);
  }
}

/**
 * The C1 unused-draft-zoning-floor-area section (D-041), REQUIRED on every
 * scenario document (schema $defs/unused_draft_zoning_floor_area,
 * additionalProperties:false). Mirror-faithful to the closed inner shape: an
 * unknown key anywhere fails, the state and typed-reason enums are pinned, the
 * remainder value is a finite number or null (an over-built NEGATIVE is a legal
 * value the validator must accept — it is never clamped here), and the closed
 * `inputs` object and `assumptions` array are structurally checked. The section
 * carries no cross-field state coupling beyond the schema (JSON Schema declares
 * `value` as number-or-null on every state); the honest state coupling is the
 * server's, surfaced verbatim.
 */
function checkUnusedFloorArea(problems: Problems, value: unknown): void {
  const base = "unused_draft_zoning_floor_area";
  if (!isRecord(value)) {
    problems.add(base, "required object is missing or not an object");
    return;
  }
  checkNoUnknownKeys(problems, base, value, UNUSED_FLOOR_AREA_KEYS);
  checkEnum(problems, `${base}.state`, value.state, UNUSED_FLOOR_AREA_STATES);
  checkNullableFiniteNumber(
    problems,
    `${base}.unused_draft_zoning_floor_area_sq_ft`,
    value.unused_draft_zoning_floor_area_sq_ft,
  );
  checkNullableString(problems, `${base}.unit`, value.unit);
  checkNonEmptyString(problems, `${base}.label`, value.label);
  checkNonEmptyString(problems, `${base}.scope_note`, value.scope_note);
  checkNullableString(problems, `${base}.formula`, value.formula);
  checkBoolean(
    problems,
    `${base}.professional_review_required`,
    value.professional_review_required,
  );
  checkNullableString(
    problems,
    `${base}.over_built_statement`,
    value.over_built_statement,
  );
  // not_computable_reason: one of the three typed reasons, or null.
  const reason = value.not_computable_reason;
  const reasonOk =
    reason === null ||
    (typeof reason === "string" &&
      (UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS as readonly string[]).includes(reason));
  if (!reasonOk) {
    problems.add(
      `${base}.not_computable_reason`,
      `must be null or one of the documented reasons (${UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS.join(
        ", ",
      )})`,
    );
  }
  checkUnusedFloorAreaInputs(problems, `${base}.inputs`, value.inputs);
  checkAssumptions(problems, `${base}.assumptions`, value.assumptions);
}

function checkCitations(problems: Problems, path: string, value: unknown): void {
  const list = checkBoundedArray(problems, path, value);
  if (!list) return;
  list.forEach((citation, index) => {
    const itemPath = `${path}[${index}]`;
    if (!isRecord(citation)) {
      problems.add(itemPath, "must be an object");
      return;
    }
    checkNoUnknownKeys(problems, itemPath, citation, CITATION_KEYS);
    checkString(problems, `${itemPath}.snapshot_id`, citation.snapshot_id);
    checkTokenRepresentable(problems, `${itemPath}.snapshot_id`, citation.snapshot_id);
    checkString(problems, `${itemPath}.section`, citation.section);
    checkString(problems, `${itemPath}.quote`, citation.quote);
    if (!isRecord(citation.provenance)) {
      problems.add(
        `${itemPath}.provenance`,
        "required object is missing or not an object",
      );
    }
    if (
      !(
        citation.last_amended === undefined ||
        citation.last_amended === null ||
        typeof citation.last_amended === "string"
      )
    ) {
      problems.add(`${itemPath}.last_amended`, "must be a string or null when present");
    }
  });
}

/**
 * FIELD-BY-FIELD `cap_provenance` validation (G4 finding 2).
 *
 * `capIsPresent` binds the two together: a material value may never be
 * surfaced without its provenance (scenario.schema.json `citation` def, PRD
 * section 19), so a non-null cap with a null provenance is a contract
 * violation, not a tolerated shape.
 *
 * STRICTNESS IS SPLIT BY PROVENANCE OF THE FIELD, on G1's trace of the
 * producer side:
 *
 *   - `output_name` and `note` are CONSTANT-SOURCED in the builder, so an empty
 *     one is unreachable without a code change and rejecting it costs nothing.
 *     `output_name` in particular is the field
 *     .claude/rules/frontend-web.md:13 exists for — never show a maximum
 *     without naming the optimized objective — so it stays non-empty.
 *   - `rule_id` and `rule_version` are PROPAGATED from the rule_evaluation
 *     trace (services/api/app/scenario/builder.py:171-172), and both schemas
 *     type them as bare strings with no `minLength`, so the server's own
 *     jsonschema gate would ship an empty one. Requiring them non-empty here
 *     turned a defective rule record into a TOTAL OUTAGE — a validation-failure
 *     card instead of a cap with valid citations — which is strictly worse for
 *     the reader than a cap whose rule id is visibly blank. They are
 *     `checkString` (first reported as a divergence in this file's earlier
 *     revision; G1 traced it and the relaxation is the resolution).
 *
 * All four are additionally checked for DISPLAY REPRESENTABILITY, which is a
 * different question from emptiness: an empty identifier bounds to empty and so
 * is unaltered, while `zr:23-21` would be quietly rewritten and is rejected.
 */
function checkCapProvenance(
  problems: Problems,
  value: unknown,
  capIsPresent: boolean,
): void {
  if (value === null) {
    if (capIsPresent) {
      problems.add(
        "cap_provenance",
        "must be present whenever draft_zoning_floor_area_cap_sq_ft is non-null (a material value may never be surfaced without its provenance)",
      );
    }
    return;
  }
  if (!isRecord(value)) {
    problems.add("cap_provenance", "must be an object or null");
    return;
  }
  checkNoUnknownKeys(problems, "cap_provenance", value, CAP_PROVENANCE_KEYS);
  checkString(problems, "cap_provenance.rule_id", value.rule_id);
  checkString(problems, "cap_provenance.rule_version", value.rule_version);
  checkNonEmptyString(problems, "cap_provenance.output_name", value.output_name);
  checkNonEmptyString(problems, "cap_provenance.note", value.note);
  checkTokenRepresentable(problems, "cap_provenance.rule_id", value.rule_id);
  checkTokenRepresentable(problems, "cap_provenance.rule_version", value.rule_version);
  checkTokenRepresentable(problems, "cap_provenance.output_name", value.output_name);
  checkEnum(problems, "cap_provenance.rule_status", value.rule_status, CAP_RULE_STATUSES);
  checkCitations(problems, "cap_provenance.citations", value.citations);
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

  checkNoUnknownKeys(problems, "scenario", body, SCENARIO_KEYS);

  if (body.contract_version !== "1.0.0") {
    problems.add("contract_version", 'must be the string "1.0.0"');
  }
  checkEnum(problems, "scenario_kind", body.scenario_kind, SCENARIO_KINDS);
  checkEnum(problems, "coverage_status", body.coverage_status, SCENARIO_COVERAGE_STATUSES);
  checkEnum(problems, "data_completeness", body.data_completeness, DATA_COMPLETENESS_VALUES);
  // The schema documents needs_review as "Always true" but types it as a bare
  // boolean with no `const`, so only the validator can hold the line (G1
  // finding 9). A scenario is never Verified; `false` here would be the server
  // claiming otherwise.
  if (body.needs_review !== true) {
    problems.add(
      "needs_review",
      'must be exactly true (the schema pins it: a scenario is always "needs_review")',
    );
  }
  checkBoolean(
    problems,
    "professional_review_required",
    body.professional_review_required,
  );
  checkNonEmptyString(
    problems,
    "not_verified_disclaimer",
    body.not_verified_disclaimer,
  );
  checkEvaluatedInput(problems, body.evaluated_input);
  checkConstraints(problems, body.constraints);

  const cap = body.draft_zoning_floor_area_cap_sq_ft;
  if (!(cap === null || typeof cap === "number")) {
    problems.add("draft_zoning_floor_area_cap_sq_ft", "must be a number or null");
  }
  if (!(body.cap_label === null || isNonEmptyString(body.cap_label))) {
    problems.add("cap_label", "must be a non-empty string or null");
  }
  checkCapProvenance(problems, body.cap_provenance, typeof cap === "number");

  checkAssumptions(problems, "assumptions", body.assumptions);
  checkReasons(problems, body.reasons);
  checkCoverageMatrix(problems, body.coverage_matrix);
  checkIntegrityCheck(problems, body.integrity_check);
  checkUnusedFloorArea(problems, body.unused_draft_zoning_floor_area);

  if (problems.list.length > 0) {
    return { ok: false, problems: problems.list };
  }
  return { ok: true, document: body as unknown as Scenario };
}
