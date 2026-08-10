"use client";

import { StatusBadge } from "./StatusBadge";
import { downstreamDisplay } from "@/lib/surveyReview/labels";
import type { DownstreamConclusion, ReviewFact } from "@/lib/surveyReview/types";

/**
 * Downstream-impact strip (task M2-T016; workflow §7, §9.2, SC-S5/S6).
 *
 * Names exactly which buildability conclusions are blocked or provisional
 * because survey evidence is unresolved — no silent defaults, no fabricated
 * values. A blocked conclusion shows no value; a provisional one shows a clearly
 * labeled provisional value with its stated assumption. The flag is a computed
 * consequence of evidence state: it CANNOT be clicked away — it clears only when
 * the reviewer resolves the item and the backend recalculation reruns.
 */
export function DownstreamImpact({
  downstream,
  facts,
  onSelectEvidence,
}: {
  downstream: DownstreamConclusion[];
  facts: ReviewFact[];
  onSelectEvidence: (evidenceId: string) => void;
}) {
  const labelForEvidence = (evidenceId: string): string =>
    facts.find((f) => f.fact.evidence_id === evidenceId)?.display_label ?? evidenceId;

  const openCount = downstream.filter(
    (c) => c.status === "blocked" || c.status === "provisional",
  ).length;

  return (
    <section className="card sr-downstream" aria-label="Downstream buildability impact" data-testid="downstream-impact">
      <h2 className="section-title">Downstream buildability impact</h2>
      {downstream.length === 0 ? (
        <p className="section-note" data-testid="downstream-empty">
          No buildability conclusion depends on an unresolved survey item.
        </p>
      ) : (
        <>
          <p className="section-note" data-testid="downstream-summary">
            {openCount === 0
              ? "No conclusion is currently blocked or provisional on these survey items."
              : `${openCount} conclusion${openCount === 1 ? " is" : "s are"} blocked or provisional until these survey items are resolved.`}
          </p>
          <ul className="sr-downstream-list">
            {downstream.map((conclusion) => {
              const display = downstreamDisplay(conclusion.status);
              return (
                <li
                  key={conclusion.conclusion_id}
                  className="sr-downstream-item"
                  data-testid={`downstream-${conclusion.conclusion_id}`}
                  data-status={conclusion.status}
                >
                  <div className="sr-downstream-head">
                    <span className="sr-downstream-label">{conclusion.label}</span>
                    <StatusBadge display={display} testId={`downstream-status-${conclusion.conclusion_id}`} />
                  </div>
                  <p className="sr-downstream-explanation">{conclusion.explanation}</p>
                  {conclusion.status === "provisional" && conclusion.provisional_value ? (
                    <p className="sr-downstream-provisional" data-testid={`downstream-provisional-${conclusion.conclusion_id}`}>
                      Provisional value (not final): <strong>{conclusion.provisional_value}</strong>
                    </p>
                  ) : null}
                  {conclusion.blocking_evidence_ids.length > 0 ? (
                    <p className="section-note">
                      Depends on:{" "}
                      {conclusion.blocking_evidence_ids.map((id, index) => (
                        <span key={id}>
                          {index > 0 ? ", " : ""}
                          <button
                            type="button"
                            className="sr-link-button"
                            onClick={() => onSelectEvidence(id)}
                            data-testid={`downstream-link-${id}`}
                          >
                            {labelForEvidence(id)}
                          </button>
                        </span>
                      ))}
                    </p>
                  ) : null}
                </li>
              );
            })}
          </ul>
        </>
      )}
    </section>
  );
}
