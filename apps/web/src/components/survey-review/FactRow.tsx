"use client";

import { StatusBadge } from "./StatusBadge";
import { confirmationDisplay } from "@/lib/surveyReview/labels";
import { factResolution, failingChecks, renderValue, unresolvedChecks } from "@/lib/surveyReview/model";
import type { ReviewFact } from "@/lib/surveyReview/types";

/**
 * One fact summary row in the decision list (task M2-T016; workflow §10.1).
 * Shows the label, current normalized value + units, the per-fact confirmation
 * state (layer B), and a deterministic-check summary. Selecting a row focuses
 * the item (bi-directional with the overlay). The row never asserts "Verified".
 */
export function FactRow({
  fact,
  selected,
  onSelect,
}: {
  fact: ReviewFact;
  selected: boolean;
  onSelect: (evidenceId: string) => void;
}) {
  const confirmation = confirmationDisplay(fact.fact.professional_confirmation.state);
  const resolution = factResolution(fact);
  const failCount = failingChecks(fact).length;
  const unresolvedCount = unresolvedChecks(fact).length;
  const passCount = fact.fact.validation_results.filter((r) => r.status === "pass").length;

  return (
    <li className="sr-fact-row">
      <button
        type="button"
        className={`sr-fact-button${selected ? " sr-fact-button-selected" : ""}`}
        aria-pressed={selected}
        aria-current={selected ? "true" : undefined}
        onClick={() => onSelect(fact.fact.evidence_id)}
        data-testid={`fact-row-${fact.fact.evidence_id}`}
        data-resolution={resolution}
      >
        <span className="sr-fact-headline">
          <span className="sr-fact-label">
            {fact.display_label}
            {fact.ai_drafted_label ? (
              <span className="sr-ai-tag" title="This label was drafted by AI and is not authoritative.">
                {" "}
                AI-drafted label
              </span>
            ) : null}
          </span>
          <span className="sr-fact-value">
            {renderValue(fact.fact.normalized_value)}
            {fact.fact.units ? <span className="fact-units"> {fact.fact.units}</span> : null}
          </span>
        </span>
        <span className="sr-fact-status">
          <StatusBadge display={confirmation} testId={`fact-confirmation-${fact.fact.evidence_id}`} />
          {failCount > 0 ? (
            <span className="sr-check-summary sr-tone-conflict" data-testid={`fact-conflict-${fact.fact.evidence_id}`}>
              {failCount} conflict{failCount === 1 ? "" : "s"}
            </span>
          ) : null}
          {unresolvedCount > 0 ? (
            <span className="sr-check-summary sr-tone-caution">
              {unresolvedCount} unresolved
            </span>
          ) : null}
          {passCount > 0 && failCount === 0 && unresolvedCount === 0 ? (
            <span className="sr-check-summary sr-tone-positive">{passCount} check{passCount === 1 ? "" : "s"} passed</span>
          ) : null}
        </span>
      </button>
    </li>
  );
}
