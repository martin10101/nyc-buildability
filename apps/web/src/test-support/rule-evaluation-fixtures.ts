/**
 * Rule-evaluation document fixtures for unit/component tests ONLY (task
 * M4-T005 phase 3). Nothing here is imported by application code.
 *
 * The four base documents are the COMMITTED canonical contract fixtures from
 * packages/contracts/fixtures/valid/rule_evaluation/ (accepted in M4-T005
 * phase 1 — the byte-exact serializer output for each of the four result
 * shapes the endpoint can produce). No document body is hand-written here; the
 * only synthesized case is the rule-conflict document (there is no committed
 * valid conflict fixture because the real single-rule R5 family can never
 * conflict), and it is derived from the committed fail-safe fixture by adding
 * the typed rule_conflict object the serializer emits.
 */

import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import supportedFamilyDraft from "../../../../packages/contracts/fixtures/valid/rule_evaluation/supported_family_draft.json";
import unsupportedNotApplicable from "../../../../packages/contracts/fixtures/valid/rule_evaluation/unsupported_not_applicable.json";
import professionalReviewFailSafe from "../../../../packages/contracts/fixtures/valid/rule_evaluation/professional_review_fail_safe.json";
import splitLotSpatialUncertainty from "../../../../packages/contracts/fixtures/valid/rule_evaluation/split_lot_spatial_uncertainty.json";

function clone(document: unknown): RuleEvaluation {
  return structuredClone(document) as unknown as RuleEvaluation;
}

/** State 1 — applicable draft determination (coverage_status conditional). */
export function draftApplicableDoc(): RuleEvaluation {
  return clone(supportedFamilyDraft);
}

/** State 2 — not applicable / unsupported (coverage_status not_applicable). */
export function unsupportedDoc(): RuleEvaluation {
  return clone(unsupportedNotApplicable);
}

/** State 3 — missing evidence (fail_safe, spatial_intersection_absent). */
export function missingEvidenceDoc(): RuleEvaluation {
  return clone(professionalReviewFailSafe);
}

/** State 5 — spatial uncertainty (split lot; share RANGES preserved). */
export function spatialUncertaintyDoc(): RuleEvaluation {
  return clone(splitLotSpatialUncertainty);
}

/**
 * State 4 — conflicting rules. Derived from the committed fail-safe fixture by
 * attaching the typed rule_conflict object the serializer emits for a detected
 * same-family conflict (fail_safe_reason=rule_conflict, no value produced).
 */
export function ruleConflictDoc(): RuleEvaluation {
  const base = missingEvidenceDoc();
  base.fail_safe_reason = "rule_conflict";
  base.reasons = [
    "same-family rule conflict for district 'R5': rules [res-far-synth-a, res-far-synth-b] " +
      "are simultaneously in effect and independently applicable for overlapping output(s) " +
      "['max_residential_far']; the governing rule is a legal determination - professional " +
      "review required, no value produced",
  ];
  base.rule_conflict = {
    conflict: true,
    family: "residential_far",
    as_of_date: null,
    competing_output_names: ["max_residential_far"],
    competing_rules: [
      {
        rule_id: "res-far-synth-a",
        rule_version: "0.1.0-draft",
        effective_from: "2024-01-01",
        effective_to: null,
        output_names: ["max_residential_far"],
      },
      {
        rule_id: "res-far-synth-b",
        rule_version: "0.1.0-draft",
        effective_from: "2024-06-01",
        effective_to: null,
        output_names: ["max_residential_far"],
      },
    ],
    note: "two draft rules simultaneously in effect for overlapping outputs",
  };
  return base;
}
