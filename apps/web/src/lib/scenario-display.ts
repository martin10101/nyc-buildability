/**
 * Display-only vocabulary + safe field extraction for the Compare (Step 3)
 * scenario screen (task M5-T004).
 *
 * Everything here is PRESENTATION support: it maps the contract-locked enum
 * values to plain-language labels and safely reads optional, weakly-typed
 * `provenance` sub-objects the backend attaches to a constraint. It performs NO
 * legal or numeric computation and never invents, ranks, or merges a value
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md). Enum labels only explain the exact
 * value; the exact value is always shown alongside so meaning is never encoded
 * by color or by a friendly word alone.
 */

import type {
  CoverageMatrixRow,
  Scenario,
  ScenarioConstraint,
} from "./scenario-contract";

/** scenario_kind → plain-language label (the exact value is shown too). */
export const SCENARIO_KIND_LABELS: Record<Scenario["scenario_kind"], string> = {
  preliminary: "Preliminary draft scenario",
  no_scenario: "No preliminary scenario",
  unsupported: "Not supported yet",
};

/** constraint.state → plain-language label. */
export const CONSTRAINT_STATE_LABELS: Record<ScenarioConstraint["state"], string> = {
  known: "known (from the official record)",
  draft: "draft (unreviewed rule output)",
  missing: "missing (no rule family provides it)",
  conflicting: "conflicting (rules or sources disagree)",
  unsupported: "unsupported (no implemented rule family)",
  professional_review_required: "professional review required",
};

/** coverage_matrix.rule_status_today → plain-language label. */
export const COVERAGE_MATRIX_STATUS_LABELS: Record<
  CoverageMatrixRow["rule_status_today"],
  string
> = {
  draft: "draft rule available (unreviewed)",
  missing: "missing — no rule family provides it",
  out_of_scope: "out of scope for this property",
};

/** Find the first constraint with a given key (constraints are keyed). */
export function findConstraint(
  document: Scenario,
  key: string,
): ScenarioConstraint | undefined {
  return document.constraints.find((constraint) => constraint.key === key);
}

/** Every coverage-matrix family that is MISSING today — the visible gaps. */
export function missingCoverageGaps(document: Scenario): CoverageMatrixRow[] {
  return document.coverage_matrix.filter((row) => row.rule_status_today === "missing");
}

// ---------------------------------------------------------------------------
// Safe readers for the weakly-typed (`unknown | null`) constraint.provenance
// sub-objects the backend attaches. Each returns a narrow, display-ready view
// or an empty result — never throws, never coerces a missing value into a
// present one.
// ---------------------------------------------------------------------------

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function asNumberOrNull(value: unknown): number | null {
  return typeof value === "number" ? value : null;
}

export interface BaseDistrictCandidateView {
  districtLabel: string | null;
  shareMin: number | null;
  sharePoint: number | null;
  shareMax: number | null;
  minorPortion: boolean;
}

/**
 * The preserved base-district share candidates recorded on a constraint's
 * provenance (professional-review / split-lot scenarios). Ranges are surfaced
 * exactly as recorded and NEVER collapsed to a single value.
 */
export function baseDistrictCandidates(
  constraint: ScenarioConstraint | undefined,
): BaseDistrictCandidateView[] {
  const provenance = asRecord(constraint?.provenance);
  const raw = provenance?.base_district_candidates;
  if (!Array.isArray(raw)) return [];
  return raw.map((entry) => {
    const record = asRecord(entry);
    return {
      districtLabel:
        typeof record?.district_label === "string" ? record.district_label : null,
      shareMin: asNumberOrNull(record?.share_min),
      sharePoint: asNumberOrNull(record?.share_point),
      shareMax: asNumberOrNull(record?.share_max),
      minorPortion: record?.minor_portion === true,
    };
  });
}

export interface CompetingRuleView {
  ruleId: string | null;
  ruleVersion: string | null;
  effectiveFrom: string | null;
  effectiveTo: string | null;
}

export interface RuleConflictView {
  competingOutputNames: string[];
  competingRules: CompetingRuleView[];
}

/**
 * The typed same-family rule conflict recorded on a constraint's provenance
 * (data-conflict scenarios). Competing rules are surfaced verbatim; the
 * platform never selects a winner.
 */
export function ruleConflict(
  constraint: ScenarioConstraint | undefined,
): RuleConflictView | null {
  const provenance = asRecord(constraint?.provenance);
  if (!provenance) return null;
  const outputs = provenance.competing_output_names;
  const rules = provenance.competing_rules;
  if (!Array.isArray(outputs) && !Array.isArray(rules)) return null;
  return {
    competingOutputNames: Array.isArray(outputs)
      ? outputs.filter((name): name is string => typeof name === "string")
      : [],
    competingRules: Array.isArray(rules)
      ? rules.map((entry) => {
          const record = asRecord(entry);
          return {
            ruleId: typeof record?.rule_id === "string" ? record.rule_id : null,
            ruleVersion:
              typeof record?.rule_version === "string" ? record.rule_version : null,
            effectiveFrom:
              typeof record?.effective_from === "string" ? record.effective_from : null,
            effectiveTo:
              typeof record?.effective_to === "string" ? record.effective_to : null,
          };
        })
      : [],
  };
}
