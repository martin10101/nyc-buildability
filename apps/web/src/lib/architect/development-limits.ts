/** Presentation selection only. No zoning rule, FAR arithmetic, or inferred limit. */
import type { PropertyProfile, SourceFact } from "@/lib/contract";
import type { EvaluationTrace, RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import { isRecord } from "@/lib/scenario-contract-checks";

export interface ResidentialReference {
  value: number | null;
  status: "City reference" | "Unknown" | "Conflicting records" | "Source value unavailable";
  records: SourceFact[];
}

export function residentialReference(profile: PropertyProfile): ResidentialReference {
  const records = profile.provenance.filter(record => record.source_id === "nyc-dcp-pluto-soda"
    && record.original_field_name === "residfar" && record.bbl === profile.identity.bbl);
  if (!records.length) return { value: null, status: "Unknown", records };
  const conflict = profile.conflicts.some(item => item.field === "residfar" && item.resolution === "unresolved");
  if (records.length !== 1 || records[0].conflict_status === "conflicting" || conflict
    || profile.provenance.filter(record => record.provenance_id === records[0].provenance_id).length !== 1) {
    return { value: null, status: "Conflicting records", records };
  }
  const value = records[0].normalized_value;
  return isLimit(value)
    ? { value, status: "City reference", records }
    : { value: null, status: value == null ? "Unknown" : "Source value unavailable", records };
}

function isLimit(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0;
}

/** Only the fields the detail views dereference are checked here. This is a
 * presentation guard for open trace payloads, not a replacement API validator. */
function readableTrace(value: unknown): value is EvaluationTrace {
  if (!isRecord(value)) return false;
  const strings = ["rule_id", "rule_version", "rule_status", "family"];
  return strings.every(key => typeof value[key] === "string")
    && typeof value.applicability_outcome === "boolean"
    && isRecord(value.evaluated_inputs) && isRecord(value.outputs)
    && isRecord(value.input_validation) && typeof value.input_validation.valid === "boolean"
    && Array.isArray(value.input_validation.invalid_inputs) && value.input_validation.invalid_inputs.every(input => isRecord(input)
      && typeof input.name === "string" && typeof input.reason === "string")
    && isRecord(value.effective_window) && typeof value.effective_window.in_effect === "boolean"
    && Array.isArray(value.citations) && value.citations.every(readableCitation)
    && Array.isArray(value.computation_steps) && value.computation_steps.every(step => isRecord(step)
      && typeof step.step_id === "string" && typeof step.op === "string" && typeof step.note === "string"
      && typeof step.result === "number" && Number.isFinite(step.result) && Array.isArray(step.resolved_args));
}

function readableCitation(value: unknown): boolean {
  return isRecord(value) && typeof value.snapshot_id === "string" && typeof value.section === "string"
    && typeof value.quote === "string" && isRecord(value.provenance)
    && (value.last_amended == null || typeof value.last_amended === "string");
}

export function evaluationIsInspectable(evaluation: RuleEvaluation | null): boolean {
  return !!evaluation && Array.isArray(evaluation.evaluations) && evaluation.evaluations.every(readableTrace);
}

function fingerprint(value: unknown): value is string {
  return typeof value === "string" && /^sha256:[a-f0-9]{64}$/.test(value);
}

/** A missing or empty association identifier is not evidence of agreement. */
export function analysisRecordsDiffer(evaluation: RuleEvaluation | null, scenario: Scenario | null): boolean {
  if (!evaluation || !scenario) return true;
  const left = evaluation.evaluated_input;
  const right = scenario.evaluated_input;
  return !isRecord(left) || !isRecord(right) || !left.bbl || left.bbl !== right.bbl
    || !fingerprint(left.input_fingerprint) || !fingerprint(right.input_fingerprint)
    || left.input_fingerprint !== right.input_fingerprint
    || !left.profile_contract_version || left.profile_contract_version !== right.profile_contract_version
    || right.rule_evaluation_contract_version !== evaluation.contract_version;
}

function uniqueResidentialTrace(evaluation: RuleEvaluation | null, bbl: string): EvaluationTrace | null {
  if (!evaluation || !evaluationIsInspectable(evaluation) || !isRecord(evaluation.evaluated_input)
    || !bbl || evaluation.evaluated_input.bbl !== bbl || !fingerprint(evaluation.evaluated_input.input_fingerprint)
    || evaluation.fail_safe !== false || evaluation.fail_safe_reason !== null
    || evaluation.rule_conflict?.conflict || evaluation.coverage_source !== "rule_evaluator"
    || evaluation.coverage_status !== "conditional") return null;
  // Count identity/applicability first. A bad or competing value may not be
  // filtered away to leave whichever number agrees with the desired result.
  const candidates = evaluation.evaluations.filter(trace => trace.family === "residential_far" && trace.applicability_outcome);
  if (candidates.length !== 1) return null;
  const trace = candidates[0];
  const identities = evaluation.evaluations.filter(item => item.rule_id === trace.rule_id && item.rule_version === trace.rule_version);
  if (identities.length !== 1 || !trace.rule_id || !trace.rule_version || !trace.input_validation.valid
    || trace.input_validation.invalid_inputs.length > 0
    || !trace.effective_window.in_effect || trace.coverage_status !== "conditional" || !trace.citations.length) return null;
  return trace;
}

export function evaluatedResidentialFar(evaluation: RuleEvaluation | null, bbl: string) {
  const trace = uniqueResidentialTrace(evaluation, bbl);
  const value = trace ? (trace.outputs as Record<string, unknown>).max_residential_far : null;
  return trace && isLimit(value) ? { value, trace } : null;
}

/** A cap is promoted only after its existing canonical residential square-foot
 * output, trace identity and input snapshot agree. No arithmetic is performed. */
export function scenarioCap(scenario: Scenario | null, evaluation: RuleEvaluation | null = null, bbl = ""): number | null {
  if (!scenario || analysisRecordsDiffer(evaluation, scenario) || scenario.evaluated_input.bbl !== bbl
    || scenario.scenario_kind !== "preliminary" || scenario.coverage_status !== "conditional"
    || !isRecord(scenario.integrity_check) || scenario.integrity_check.agreed === false) return null;
  const trace = uniqueResidentialTrace(evaluation, bbl);
  const provenance = scenario.cap_provenance;
  const value = scenario.draft_zoning_floor_area_cap_sq_ft;
  if (!trace || !isRecord(provenance) || provenance.rule_id !== trace.rule_id || provenance.rule_version !== trace.rule_version
    || provenance.rule_status !== trace.rule_status || provenance.output_name !== "max_residential_floor_area_sq_ft"
    || !Array.isArray(provenance.citations) || !provenance.citations.length || !provenance.citations.every(readableCitation)
    || !isLimit(value) || (trace.outputs as Record<string, unknown>).max_residential_floor_area_sq_ft !== value) return null;
  return value;
}

const FAILURE_LABELS: Record<NonNullable<RuleEvaluation["fail_safe_reason"]>, string> = {
  spatial_intersection_absent: "Zoning boundary check unavailable",
  spatial_context_incomplete: "Zoning boundary check incomplete",
  data_conflict: "Conflicting property data",
  geometry_uncertain: "Lot boundary requires review",
  inconsistent_confident_geometry: "Conflicting boundary results",
  rule_conflict: "Conflicting rule results",
};

export function calculationStatus(evaluation: RuleEvaluation | null, scenario: Scenario | null, bbl: string): string {
  if (evaluation && evaluation.evaluated_input?.bbl !== bbl) return "Property identity mismatch";
  if (evaluation?.fail_safe_reason) return FAILURE_LABELS[evaluation.fail_safe_reason];
  if (evaluation?.rule_conflict?.conflict || evaluation?.coverage_status === "data_conflict" || scenario?.coverage_status === "data_conflict") return "Conflicting results";
  if (evaluation && !evaluationIsInspectable(evaluation)) return "Rule details incomplete · inspect captured evidence";
  if (evaluation?.fail_safe) return "Rule result unavailable · inspect evidence";
  if (scenario && analysisRecordsDiffer(evaluation, scenario)) return "Analysis records differ · inspect evidence";
  if (scenario?.integrity_check.agreed === false) return "Scenario integrity check failed · inspect evidence";
  return "Draft assessment · envelope incomplete";
}

export function scenarioBlocksPromotion(scenario: Scenario | null): boolean {
  return !!scenario && (scenario.coverage_status !== "conditional" || scenario.scenario_kind !== "preliminary"
    || scenario.integrity_check.agreed === false);
}

/** Labels map the current canonical scenario keys; unknown families remain in full evidence. */
export const BULK_ROWS = [
  ["height_limit", "Height"],
  ["setbacks_yards", "Setbacks and yards"],
  ["lot_coverage_open_space", "Lot coverage and open space"],
] as const;

/** Current bulk provenance is open-typed. No supported family/output/unit
 * contract establishes a height, yard or coverage limit here. Keep the supplied
 * constraints in evidence; never interpret an arbitrary matching number. */
export function bulkRow(scenario: Scenario | null, key: string, evaluation: RuleEvaluation | null) {
  const empty = { value: null, unit: null };
  if (scenario?.coverage_status === "data_conflict" || evaluation?.coverage_status === "data_conflict"
    || evaluation?.rule_conflict?.conflict) return { ...empty, status: "Conflicting results" };
  const rows = scenario?.constraints.filter(item => item.key === key) ?? [];
  if (rows.length > 1) return { ...empty, status: "Conflicting records" };
  const row = rows[0];
  if (row?.state === "conflicting") return { ...empty, status: "Conflicting results" };
  if (row?.state === "unsupported") return { ...empty, status: "Not supported" };
  if (row?.state === "professional_review_required") return { ...empty, status: "Review required" };
  return { ...empty, status: "Not calculated" };
}
