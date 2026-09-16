/** Presentation selection only. No zoning rule, FAR arithmetic, or inferred limit. */
import type { PropertyProfile, SourceFact } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
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

/** The cap is a separate canonical square-foot output, never FAR × tax-lot area. */
export function presentableScenario(scenario: Scenario | null, bbl: string): Scenario | null {
  return scenario?.evaluated_input.bbl === bbl ? scenario : null;
}

export function evaluatedResidentialFar(evaluation: RuleEvaluation | null, bbl: string) {
  if (!evaluation || evaluation.evaluated_input.bbl !== bbl || evaluation.fail_safe
    || evaluation.rule_conflict?.conflict || evaluation.coverage_status !== "conditional") return null;
  const candidates = evaluation.evaluations.filter(trace => trace.family === "residential_far"
    && trace.applicability_outcome && trace.input_validation.valid && trace.effective_window.in_effect
    && trace.coverage_status === "conditional" && "max_residential_far" in trace.outputs);
  if (candidates.length !== 1 || !candidates[0].citations.length) return null;
  const value = (candidates[0].outputs as Record<string, unknown>).max_residential_far;
  return isLimit(value) ? { value, trace: candidates[0] } : null;
}

export function scenarioCap(scenario: Scenario | null): number | null {
  const value = scenario?.draft_zoning_floor_area_cap_sq_ft;
  return scenario?.scenario_kind === "preliminary" && scenario.coverage_status === "conditional"
    && scenario.integrity_check.agreed !== false && !!scenario.cap_provenance?.citations.length
    && isLimit(value) ? value : null;
}

/** A shared BBL alone cannot join results produced from different input snapshots. */
export function analysisRecordsDiffer(evaluation: RuleEvaluation | null, scenario: Scenario | null): boolean {
  return !!(evaluation && scenario && scenario.evaluated_input.input_fingerprint
    && evaluation.evaluated_input.input_fingerprint !== scenario.evaluated_input.input_fingerprint);
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
  if (evaluation && evaluation.evaluated_input.bbl !== bbl) return "Property identity mismatch";
  if (analysisRecordsDiffer(evaluation, scenario)) return "Analysis records differ · inspect evidence";
  if (evaluation?.fail_safe_reason) return FAILURE_LABELS[evaluation.fail_safe_reason];
  if (evaluation?.rule_conflict?.conflict || scenario?.coverage_status === "data_conflict") return "Conflicting results";
  return "Draft assessment · envelope incomplete";
}

/** Labels map the current canonical scenario keys; unknown families remain in full evidence. */
export const BULK_ROWS = [
  ["height_limit", "Height"],
  ["setbacks_yards", "Setbacks and yards"],
  ["lot_coverage_open_space", "Lot coverage and open space"],
] as const;

function hasMatchingTrace(row: Scenario["constraints"][number], evaluation: RuleEvaluation | null) {
  const provenance = row.provenance;
  if (!isRecord(provenance) || typeof provenance.output_name !== "string"
    || typeof provenance.rule_id !== "string" || typeof provenance.rule_version !== "string"
    || !evaluation || evaluation.fail_safe || evaluation.rule_conflict?.conflict
    || evaluation.coverage_status !== "conditional") return false;
  const candidates = evaluation.evaluations.filter(trace => trace.rule_id === provenance.rule_id
    && trace.rule_version === provenance.rule_version && trace.applicability_outcome
    && trace.input_validation.valid && trace.effective_window.in_effect && trace.coverage_status === "conditional"
    && trace.citations.length > 0
    && (trace.outputs as Record<string, unknown>)[provenance.output_name as string] === row.value);
  return candidates.length === 1;
}

export function bulkRow(scenario: Scenario | null, key: string, evaluation: RuleEvaluation | null) {
  if (scenario?.coverage_status === "data_conflict") return { value: null, unit: null, status: "Conflicting results" };
  const rows = scenario?.constraints.filter(item => item.key === key) ?? [];
  if (rows.length > 1) return { value: null, unit: null, status: "Conflicting records" };
  const row = rows[0];
  if (!row || row.state === "missing") return { value: null, unit: null, status: "Not calculated" };
  if (row.state === "conflicting") return { value: null, unit: null, status: "Conflicting results" };
  if (row.state === "unsupported") return { value: null, unit: null, status: "Not supported" };
  if (row.state === "professional_review_required") return { value: null, unit: null, status: "Review required" };
  if (scenario?.coverage_status !== "conditional") return { value: null, unit: null, status: "Not calculated" };
  if (row.unit == null || !isLimit(row.value) || !hasMatchingTrace(row, evaluation)) return { value: null, unit: null, status: "Not calculated" };
  return { value: row.value, unit: row.unit, status: row.state === "draft" ? "Draft" : "Recorded result" };
}
