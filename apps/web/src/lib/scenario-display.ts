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
 *
 * `constraints[].provenance` is typed `unknown` by the contract, so it is the
 * one region a renderer cannot address field by field. The rework's answer is
 * `provenanceLeaves`: a GENERIC walk that surfaces EVERY leaf of whatever the
 * server attached, rather than a hand-listed subset that silently drops the
 * rest (the defect that dropped `review_reasons`, `coverage_note`,
 * `lot_overall_class` and `pair_class` on the professional-review fixture, and
 * every `source_id` / `dataset_version` on the profile-sourced constraints).
 * Both its width and its strings are bounded, and every bound it applies is
 * DISCLOSED to the caller rather than applied silently.
 */

import { MAX_REFLECTED_TEXT_LENGTH, MAX_TOKEN_LENGTH, boundedText } from "./bounded";
import { formatValue } from "./format";
import type {
  CoverageMatrixRow,
  Scenario,
  ScenarioConstraint,
} from "./scenario-contract";

/** scenario_kind → plain-language label. The exact contract value is always
 * rendered alongside (DCV finding 14: a mapped label alone drops the word the
 * contract actually used). */
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

function asStringOrNull(value: unknown): string | null {
  return typeof value === "string" ? boundedText(value, "") : null;
}

export interface BaseDistrictCandidateView {
  districtLabel: string | null;
  shareMin: number | null;
  sharePoint: number | null;
  shareMax: number | null;
  /** `null` when the source did not state it. NEVER defaulted to `false`: an
   * unknown rendered as a negative assertion is a silent default (DCV-15). */
  minorPortion: boolean | null;
  /** The recorded pair classification (e.g. `boundary_uncertain`) — the WHY of
   * an uncertain share, dropped entirely before the rework (G3 finding 15). */
  pairClass: string | null;
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
      districtLabel: asStringOrNull(record?.district_label),
      shareMin: asNumberOrNull(record?.share_min),
      sharePoint: asNumberOrNull(record?.share_point),
      shareMax: asNumberOrNull(record?.share_max),
      minorPortion:
        typeof record?.minor_portion === "boolean" ? record.minor_portion : null,
      pairClass: asStringOrNull(record?.pair_class),
    };
  });
}

export interface CompetingRuleView {
  ruleId: string | null;
  ruleVersion: string | null;
  effectiveFrom: string | null;
  effectiveTo: string | null;
  outputNames: string[];
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
      ? outputs
          .filter((name): name is string => typeof name === "string")
          .map((name) => boundedText(name, ""))
      : [],
    competingRules: Array.isArray(rules)
      ? rules.map((entry) => {
          const record = asRecord(entry);
          const outputNames = record?.output_names;
          return {
            ruleId: asStringOrNull(record?.rule_id),
            ruleVersion: asStringOrNull(record?.rule_version),
            effectiveFrom: asStringOrNull(record?.effective_from),
            effectiveTo: asStringOrNull(record?.effective_to),
            outputNames: Array.isArray(outputNames)
              ? outputNames
                  .filter((name): name is string => typeof name === "string")
                  .map((name) => boundedText(name, ""))
              : [],
          };
        })
      : [],
  };
}

export interface ConstraintConflictView {
  constraintKey: string;
  conflict: RuleConflictView;
}

/**
 * EVERY constraint that records a same-family rule conflict, paired with its
 * key. The coverage gloss for `data_conflict` promises "both values are shown,
 * nothing was resolved"; before the rework `ruleConflict` had zero consumers
 * repo-wide, so the screen asserted a display its own render path contradicted
 * (G1-6 / G3-7 / G4-3 / DCV-6). Scanning all constraints rather than only
 * `residential_far_cap` means a conflict recorded on any other family surfaces
 * too, instead of becoming the next silent drop.
 */
export function ruleConflicts(document: Scenario): ConstraintConflictView[] {
  const views: ConstraintConflictView[] = [];
  for (const constraint of document.constraints) {
    const conflict = ruleConflict(constraint);
    if (
      conflict &&
      (conflict.competingOutputNames.length > 0 || conflict.competingRules.length > 0)
    ) {
      views.push({ constraintKey: constraint.key, conflict });
    }
  }
  return views;
}

// ---------------------------------------------------------------------------
// Generic provenance leaf walk.
// ---------------------------------------------------------------------------

/** Widest provenance blob rendered for one constraint. Beyond this the reader
 * reports `truncated: true` and the renderer states the omission explicitly —
 * the bound is disclosed, never silent. */
export const MAX_PROVENANCE_LEAVES = 200;

/** Deepest nesting walked before the reader stops and says so. */
export const MAX_PROVENANCE_DEPTH = 12;

export interface ProvenanceLeaf {
  /** Dotted path within the provenance blob, e.g. `resolved[0].source_id`. */
  path: string;
  /** The leaf value, formatted for display only (never recomputed). */
  value: string;
}

export interface ProvenanceView {
  leaves: ProvenanceLeaf[];
  /** True when the walk hit MAX_PROVENANCE_LEAVES or MAX_PROVENANCE_DEPTH and
   * some leaves are therefore NOT shown. The caller MUST say so on screen. */
  truncated: boolean;
}

/**
 * Flatten a weakly-typed provenance blob to its leaves so every recorded fact
 * reaches the screen. Objects and arrays recurse; primitives and `null` are
 * formatted by the shared display formatter (no rounding — see format.ts).
 *
 * An EMPTY object or array is itself reported as a leaf ("(empty)") rather than
 * vanishing: an empty `review_reasons` is a different statement from an absent
 * one, and only one of them is silence.
 */
export function provenanceLeaves(value: unknown): ProvenanceView {
  const leaves: ProvenanceLeaf[] = [];
  let truncated = false;

  const push = (path: string, display: string): void => {
    if (leaves.length >= MAX_PROVENANCE_LEAVES) {
      truncated = true;
      return;
    }
    leaves.push({
      path: boundedText(path, "(unnamed field)", MAX_TOKEN_LENGTH * 4),
      value: boundedText(display, "", MAX_REFLECTED_TEXT_LENGTH),
    });
  };

  const walk = (node: unknown, path: string, depth: number): void => {
    if (leaves.length >= MAX_PROVENANCE_LEAVES) {
      truncated = true;
      return;
    }
    if (depth > MAX_PROVENANCE_DEPTH) {
      truncated = true;
      push(path, "(nested deeper than this view shows)");
      return;
    }
    if (Array.isArray(node)) {
      if (node.length === 0) {
        push(path, "(empty list)");
        return;
      }
      node.forEach((item, index) => walk(item, `${path}[${index}]`, depth + 1));
      return;
    }
    const record = asRecord(node);
    if (record) {
      const keys = Object.keys(record);
      if (keys.length === 0) {
        push(path, "(empty object)");
        return;
      }
      for (const key of keys) {
        walk(record[key], path === "" ? key : `${path}.${key}`, depth + 1);
      }
      return;
    }
    push(path, formatValue(node));
  };

  if (value === null || value === undefined) {
    return { leaves, truncated };
  }
  walk(value, "", 0);
  return { leaves, truncated };
}
