"use client";

import { StatusBadge } from "./StatusBadge";
import { confirmationDisplay } from "@/lib/surveyReview/labels";
import { checkSummaryKind, factResolution, renderValue } from "@/lib/surveyReview/model";
import type { FactView } from "@/lib/surveyReview/types";

/**
 * One fact summary row in the decision list (task M2-T016; workflow §10.1).
 * Shows the label, current normalized value + units, the per-fact confirmation
 * state (layer B), and a deterministic-check summary derived from the backend
 * check counts. Selecting a row focuses the item. The row never asserts
 * "Verified".
 */
export function FactRow({
  fact,
  selected,
  onSelect,
}: {
  fact: FactView;
  selected: boolean;
  onSelect: (evidenceId: string) => void;
}) {
  const confirmation = confirmationDisplay(fact.confirmation_state);
  const resolution = factResolution(fact);
  const summaryKind = checkSummaryKind(fact);

  return (
    <li className="sr-fact-row">
      <button
        type="button"
        className={`sr-fact-button${selected ? " sr-fact-button-selected" : ""}`}
        aria-pressed={selected}
        aria-current={selected ? "true" : undefined}
        onClick={() => onSelect(fact.evidence_id)}
        data-testid={`fact-row-${fact.evidence_id}`}
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
            {renderValue(fact.normalized_value)}
            {fact.units ? <span className="fact-units"> {fact.units}</span> : null}
          </span>
        </span>
        <span className="sr-fact-status">
          <StatusBadge display={confirmation} testId={`fact-confirmation-${fact.evidence_id}`} />
          {fact.check_fail > 0 ? (
            <span className="sr-check-summary sr-tone-conflict" data-testid={`fact-conflict-${fact.evidence_id}`}>
              {fact.check_fail} conflict{fact.check_fail === 1 ? "" : "s"}
            </span>
          ) : null}
          {fact.check_unresolved > 0 ? (
            <span className="sr-check-summary sr-tone-caution">{fact.check_unresolved} unresolved</span>
          ) : null}
          {summaryKind === "passed" ? (
            <span className="sr-check-summary sr-tone-positive">
              {fact.check_pass} check{fact.check_pass === 1 ? "" : "s"} passed
            </span>
          ) : null}
        </span>
      </button>
    </li>
  );
}
