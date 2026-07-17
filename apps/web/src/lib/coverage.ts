/**
 * Coverage-status display vocabulary (task M2-T001).
 *
 * The canonical enum value (PRD section 12 wording, verbatim from
 * coverage_status.schema.json) is ALWAYS shown; the plain-language gloss
 * only explains it (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md: plain language
 * first, exact vocabulary preserved; never legal certainty by color alone).
 * The UI never invents a status and never upgrades one.
 */

import type { CoverageStatus, DataCompleteness } from "./contract";

export interface CoverageDisplay {
  /** Exact PRD section 12 enum value, displayed verbatim. */
  value: CoverageStatus;
  /** Plain-language explanation. */
  gloss: string;
  /** Non-color symbol so status is never communicated by color alone. */
  symbol: string;
}

const COVERAGE_DISPLAY: Record<CoverageStatus, Omit<CoverageDisplay, "value">> = {
  verified: {
    gloss: "Confirmed under a published, professionally reviewed rule.",
    symbol: "✓",
  },
  conditional: {
    gloss: "Official source fact, not yet professionally reviewed.",
    symbol: "◐",
  },
  professional_review_required: {
    gloss: "A qualified professional must review this before reliance.",
    symbol: "!",
  },
  data_conflict: {
    gloss: "Official sources disagree; both values are shown, nothing was resolved.",
    symbol: "≠",
  },
  unsupported: {
    gloss: "The platform detected a data problem and cannot support this value.",
    symbol: "∅",
  },
  not_applicable: {
    gloss: "Does not apply to this property.",
    symbol: "—",
  },
};

export function coverageDisplay(status: CoverageStatus): CoverageDisplay {
  return { value: status, ...COVERAGE_DISPLAY[status] };
}

export interface CompletenessDisplay {
  /** Exact PRD section 12 enum value, displayed verbatim. */
  value: DataCompleteness;
  headline: string;
  gloss: string;
}

const COMPLETENESS_DISPLAY: Record<DataCompleteness, Omit<CompletenessDisplay, "value">> = {
  complete: {
    headline: "All expected official inputs were retrieved",
    gloss: "No expected source field is missing for this property.",
  },
  missing_noncritical: {
    headline: "Some non-critical official inputs are missing",
    gloss:
      "The official record omits some fields. None is classified critical, " +
      "but every gap is listed below — nothing is hidden.",
  },
  missing_critical: {
    headline: "Critical official inputs are missing",
    gloss:
      "At least one field classified critical is missing from the official " +
      "record. Feasibility conclusions cannot be complete without it.",
  },
};

export function completenessDisplay(value: DataCompleteness): CompletenessDisplay {
  return { value, ...COMPLETENESS_DISPLAY[value] };
}
