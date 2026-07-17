/**
 * Runtime validation of every HTTP-200 profile body against the GENERATED
 * canonical types (task M2-T002 output A; scenario S3).
 *
 * The generated module packages/contracts/generated/property_profile.ts is
 * the type vocabulary; this validator is its runtime mirror: it checks the
 * presence and primitive type of every DOCUMENTED key, every enum against
 * the contract-locked arrays in src/lib/contract.ts, and the closed
 * published contract_version set. Undocumented extra keys are tolerated
 * (the canonical schemas are open objects) and simply never read.
 *
 * FAILURE IS TOTAL: when any check fails the caller receives only the
 * bounded problem list — never a partially-usable profile — so nothing can
 * be rendered from an invalid payload (S3: validation-failure state,
 * nothing partially rendered).
 *
 * No legal logic: this file checks SHAPE, never meaning, and never rewrites
 * a value (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 */

import {
  ANALYSIS_READINESS_VALUES,
  BOROUGH_CODES,
  BOROUGH_NAMES,
  CONFLICT_RESOLUTION_VALUES,
  CONFLICT_STATUS_VALUES,
  COVERAGE_STATUSES,
  CRITICALITY_VALUES,
  DATA_COMPLETENESS_VALUES,
  FINANCIAL_READINESS_VALUES,
  GEOMETRY_VALIDITY_VALUES,
  RULE_COVERAGE_VALUES,
  SOURCE_RECORD_COMPLETENESS_VALUES,
  SUPPORTED_CONTRACT_VERSIONS,
  USER_CONFIRMATION_ACTIONS,
  USER_CONFIRMED_OR_OVERRIDDEN_VALUES,
  type PropertyProfile,
} from "./contract";

export const MAX_REPORTED_PROBLEMS = 20;

export type ProfileValidationResult =
  | { ok: true; profile: PropertyProfile }
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
  allowed: readonly (string | number)[],
  optional: boolean,
): void {
  if (value === undefined) {
    if (!optional) {
      problems.add(path, "required enum value is missing");
    }
    return;
  }
  if (!(allowed as readonly unknown[]).includes(value)) {
    problems.add(path, `value is not in the documented enum (${allowed.join(", ")})`);
  }
}

function checkString(
  problems: Problems,
  path: string,
  value: unknown,
  optional: boolean,
  nonEmpty = false,
): void {
  if (value === undefined) {
    if (!optional) problems.add(path, "required string is missing");
    return;
  }
  if (typeof value !== "string") {
    problems.add(path, "must be a string");
    return;
  }
  if (nonEmpty && value.length === 0) {
    problems.add(path, "must be a non-empty string");
  }
}

function checkStringArray(
  problems: Problems,
  path: string,
  value: unknown,
  optional: boolean,
  nonEmptyItems = false,
): void {
  if (value === undefined) {
    if (!optional) problems.add(path, "required array is missing");
    return;
  }
  if (!Array.isArray(value)) {
    problems.add(path, "must be an array");
    return;
  }
  value.forEach((item, index) => {
    if (typeof item !== "string" || (nonEmptyItems && item.length === 0)) {
      problems.add(`${path}[${index}]`, "must be a non-empty string");
    }
  });
}

function checkFactMap(problems: Problems, path: string, value: unknown): void {
  if (!isRecord(value)) {
    problems.add(path, "must be an object of fact values");
    return;
  }
  for (const [key, fact] of Object.entries(value)) {
    const factPath = `${path}.${key}`;
    if (!isRecord(fact)) {
      problems.add(factPath, "fact must be an object");
      continue;
    }
    if (!("value" in fact)) {
      problems.add(factPath, "fact is missing the required `value` key");
    }
    if (!isNonEmptyString(fact.provenance_ref)) {
      problems.add(factPath, "fact is missing a non-empty `provenance_ref`");
    }
    if (fact.units !== undefined && fact.units !== null && typeof fact.units !== "string") {
      problems.add(factPath, "`units` must be a string when present");
    }
    checkEnum(problems, `${factPath}.coverage_status`, fact.coverage_status, COVERAGE_STATUSES, true);
  }
}

function checkProvenanceMap(problems: Problems, path: string, value: unknown): void {
  if (value === undefined) return;
  if (!isRecord(value)) {
    problems.add(path, "must be an object mapping values to provenance-ref lists");
    return;
  }
  for (const [key, refs] of Object.entries(value)) {
    checkStringArray(problems, `${path}.${key}`, refs, false, true);
  }
}

function checkProfileVersion(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("profile_version", "required object is missing or not an object");
    return;
  }
  checkEnum(
    problems,
    "profile_version.contract_version",
    value.contract_version,
    SUPPORTED_CONTRACT_VERSIONS,
    false,
  );
  if (typeof value.profile_revision !== "number") {
    problems.add("profile_version.profile_revision", "must be a number");
  }
  checkString(problems, "profile_version.generated_at", value.generated_at, false, true);
}

function checkIdentity(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("identity", "required object is missing or not an object");
    return;
  }
  if (!isNonEmptyString(value.bbl)) {
    problems.add("identity.bbl", "must be a non-empty string");
  }
  checkStringArray(problems, "identity.bins", value.bins, true, true);
  if (value.address !== undefined) {
    if (!isRecord(value.address)) {
      problems.add("identity.address", "must be an object when present");
    } else {
      const address = value.address;
      checkString(problems, "identity.address.house_number", address.house_number, true);
      checkString(problems, "identity.address.street_name", address.street_name, true);
      checkEnum(problems, "identity.address.borough", address.borough, BOROUGH_NAMES, true);
      checkEnum(
        problems,
        "identity.address.borough_code",
        address.borough_code,
        BOROUGH_CODES,
        true,
      );
      checkString(problems, "identity.address.zip_code", address.zip_code, true);
      checkString(
        problems,
        "identity.address.normalized_address",
        address.normalized_address,
        true,
      );
    }
  }
  if (value.geometry !== undefined && !isRecord(value.geometry)) {
    problems.add("identity.geometry", "must be an object when present");
  }
}

function checkZoning(problems: Problems, value: unknown): void {
  if (!isRecord(value)) {
    problems.add("zoning", "required object is missing or not an object");
    return;
  }
  checkStringArray(problems, "zoning.districts", value.districts, true);
  checkStringArray(problems, "zoning.commercial_overlays", value.commercial_overlays, true);
  checkStringArray(problems, "zoning.special_districts", value.special_districts, true);
  if (value.mapped_features !== undefined) {
    if (!Array.isArray(value.mapped_features)) {
      problems.add("zoning.mapped_features", "must be an array when present");
    } else {
      value.mapped_features.forEach((item, index) => {
        if (!isRecord(item)) {
          problems.add(`zoning.mapped_features[${index}]`, "must be an object");
        }
      });
    }
  }
  checkProvenanceMap(problems, "zoning.district_provenance", value.district_provenance);
  checkProvenanceMap(
    problems,
    "zoning.commercial_overlay_provenance",
    value.commercial_overlay_provenance,
  );
  checkProvenanceMap(
    problems,
    "zoning.special_district_provenance",
    value.special_district_provenance,
  );
}

function checkProvenance(problems: Problems, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add("provenance", "required array is missing or not an array");
    return;
  }
  value.forEach((record, index) => {
    const path = `provenance[${index}]`;
    if (!isRecord(record)) {
      problems.add(path, "must be an object");
      return;
    }
    for (const key of [
      "provenance_id",
      "source_id",
      "original_field_name",
      "dataset_version",
      "bbl",
    ] as const) {
      if (!isNonEmptyString(record[key])) {
        problems.add(`${path}.${key}`, "must be a non-empty string");
      }
    }
    if (!("original_value" in record)) {
      problems.add(`${path}.original_value`, "required key is missing");
    }
    if (!("normalized_value" in record)) {
      problems.add(`${path}.normalized_value`, "required key is missing");
    }
    checkString(problems, `${path}.retrieved_at`, record.retrieved_at, false, true);
    if (!("effective_date" in record)) {
      problems.add(`${path}.effective_date`, "required key is missing (string or null)");
    } else if (record.effective_date !== null && typeof record.effective_date !== "string") {
      problems.add(`${path}.effective_date`, "must be a string or null");
    }
    if (
      record.units !== undefined &&
      record.units !== null &&
      typeof record.units !== "string"
    ) {
      problems.add(`${path}.units`, "must be a string or null when present");
    }
    if (typeof record.confidence !== "number") {
      problems.add(`${path}.confidence`, "must be a number");
    }
    checkEnum(
      problems,
      `${path}.user_confirmed_or_overridden`,
      record.user_confirmed_or_overridden,
      USER_CONFIRMED_OR_OVERRIDDEN_VALUES,
      false,
    );
    checkEnum(
      problems,
      `${path}.conflict_status`,
      record.conflict_status,
      CONFLICT_STATUS_VALUES,
      false,
    );
  });
}

function checkMissingInputs(problems: Problems, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add("missing_inputs", "required array is missing or not an array");
    return;
  }
  value.forEach((entry, index) => {
    const path = `missing_inputs[${index}]`;
    if (!isRecord(entry)) {
      problems.add(path, "must be an object");
      return;
    }
    checkString(problems, `${path}.field`, entry.field, false, true);
    checkEnum(problems, `${path}.criticality`, entry.criticality, CRITICALITY_VALUES, false);
    checkString(problems, `${path}.reason`, entry.reason, true);
    if (
      entry.feasibility_relevant !== undefined &&
      typeof entry.feasibility_relevant !== "boolean"
    ) {
      problems.add(`${path}.feasibility_relevant`, "must be a boolean when present");
    }
  });
}

function checkConflicts(problems: Problems, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add("conflicts", "required array is missing or not an array");
    return;
  }
  value.forEach((conflict, index) => {
    const path = `conflicts[${index}]`;
    if (!isRecord(conflict)) {
      problems.add(path, "must be an object");
      return;
    }
    checkString(problems, `${path}.field`, conflict.field, false, true);
    checkEnum(
      problems,
      `${path}.resolution`,
      conflict.resolution,
      CONFLICT_RESOLUTION_VALUES,
      false,
    );
    if (!Array.isArray(conflict.values) || conflict.values.length < 2) {
      problems.add(`${path}.values`, "must be an array of at least 2 entries");
      return;
    }
    conflict.values.forEach((entry, valueIndex) => {
      const valuePath = `${path}.values[${valueIndex}]`;
      if (!isRecord(entry)) {
        problems.add(valuePath, "must be an object");
        return;
      }
      checkString(problems, `${valuePath}.source_id`, entry.source_id, false, true);
      if (!("value" in entry)) {
        problems.add(`${valuePath}.value`, "required key is missing");
      }
    });
  });
}

function checkUserConfirmations(problems: Problems, value: unknown): void {
  if (!Array.isArray(value)) {
    problems.add("user_confirmations", "required array is missing or not an array");
    return;
  }
  value.forEach((entry, index) => {
    const path = `user_confirmations[${index}]`;
    if (!isRecord(entry)) {
      problems.add(path, "must be an object");
      return;
    }
    checkString(problems, `${path}.field`, entry.field, false, true);
    checkEnum(problems, `${path}.action`, entry.action, USER_CONFIRMATION_ACTIONS, false);
    checkString(problems, `${path}.confirmed_at`, entry.confirmed_at, true);
    checkString(problems, `${path}.confirmed_by`, entry.confirmed_by, true);
  });
}

function checkReproducibility(problems: Problems, value: unknown): void {
  if (value === undefined) return;
  if (!isRecord(value)) {
    problems.add("reproducibility", "must be an object when present");
    return;
  }
  for (const key of [
    "correlation_id",
    "source_id",
    "dataset_id",
    "request_url",
    "coverage_policy",
  ] as const) {
    if (!isNonEmptyString(value[key])) {
      problems.add(`reproducibility.${key}`, "must be a non-empty string");
    }
  }
  checkString(problems, "reproducibility.retrieved_at", value.retrieved_at, false, true);
  if (!("dataset_version" in value)) {
    problems.add("reproducibility.dataset_version", "required key is missing (string or null)");
  } else if (value.dataset_version !== null && typeof value.dataset_version !== "string") {
    problems.add("reproducibility.dataset_version", "must be a string or null");
  }
  if (typeof value.record_count !== "number") {
    problems.add("reproducibility.record_count", "must be a number");
  }
  checkStringArray(problems, "reproducibility.drift_signals", value.drift_signals, false, true);
  checkStringArray(
    problems,
    "reproducibility.connector_notes",
    value.connector_notes,
    false,
    true,
  );
}

function checkStatusDimensions(problems: Problems, value: unknown): void {
  if (value === undefined) return;
  if (!isRecord(value)) {
    problems.add("status_dimensions", "must be an object when present");
    return;
  }
  checkEnum(
    problems,
    "status_dimensions.source_record_completeness",
    value.source_record_completeness,
    SOURCE_RECORD_COMPLETENESS_VALUES,
    false,
  );
  checkEnum(
    problems,
    "status_dimensions.analysis_readiness",
    value.analysis_readiness,
    ANALYSIS_READINESS_VALUES,
    false,
  );
  checkEnum(
    problems,
    "status_dimensions.rule_coverage",
    value.rule_coverage,
    RULE_COVERAGE_VALUES,
    false,
  );
  checkEnum(
    problems,
    "status_dimensions.geometry_validity",
    value.geometry_validity,
    GEOMETRY_VALIDITY_VALUES,
    false,
  );
  checkEnum(
    problems,
    "status_dimensions.financial_readiness",
    value.financial_readiness,
    FINANCIAL_READINESS_VALUES,
    false,
  );
  checkString(problems, "status_dimensions.policy", value.policy, false, true);
}

/**
 * Validate an HTTP-200 body against the generated canonical types. Returns
 * the typed profile ONLY when every documented check passes.
 */
export function validateProfileDocument(body: unknown): ProfileValidationResult {
  const problems = new Problems();
  if (!isRecord(body)) {
    return { ok: false, problems: ["profile: response body is not a JSON object"] };
  }

  checkProfileVersion(problems, body.profile_version);
  checkIdentity(problems, body.identity);
  checkFactMap(problems, "lot_facts", body.lot_facts);
  checkFactMap(problems, "existing_building_facts", body.existing_building_facts);
  checkZoning(problems, body.zoning);
  if (!isRecord(body.project_intent)) {
    problems.add("project_intent", "required object is missing or not an object");
  }
  checkProvenance(problems, body.provenance);
  checkMissingInputs(problems, body.missing_inputs);
  checkConflicts(problems, body.conflicts);
  checkUserConfirmations(problems, body.user_confirmations);
  checkEnum(
    problems,
    "data_completeness",
    body.data_completeness,
    DATA_COMPLETENESS_VALUES,
    true,
  );
  checkReproducibility(problems, body.reproducibility);
  checkStatusDimensions(problems, body.status_dimensions);

  if (problems.list.length > 0) {
    return { ok: false, problems: problems.list };
  }
  return { ok: true, profile: body as unknown as PropertyProfile };
}
