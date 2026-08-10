"use client";

import { StatusBadge } from "./StatusBadge";
import { coverageStatusGloss, downstreamKindDisplay } from "@/lib/surveyReview/labels";
import type { FactView } from "@/lib/surveyReview/types";

/**
 * Downstream-impact strip (task M2-T016 rework; workflow §7, §9.2, SC-S5/S6).
 *
 * The shipped backend expresses downstream honesty PER FACT: each fact carries a
 * `downstream_impact` that is `blocked` (a dependent conclusion cannot rest on
 * it) or `provisional` (usable only provisionally, e.g. unconfirmed evidence),
 * with a plain-language reason and coverage status. This strip aggregates those
 * per-fact impacts — no silent defaults, no fabricated values. The impact is a
 * computed consequence of evidence state: it CANNOT be clicked away; it clears
 * only when the reviewer resolves the item and the backend recalculation
 * (re-read) removes the impact.
 *
 * AWAITING-BACKEND: the backend leaves `analysis_readiness` null (the specific
 * blocked conclusion names are decided by the profile consumer), so named
 * conclusions are not shown here — the honest per-fact impact is.
 */
export function DownstreamImpact({
  facts,
  onSelectEvidence,
}: {
  facts: FactView[];
  onSelectEvidence: (evidenceId: string) => void;
}) {
  const impacted = facts.filter((f) => f.downstream_impact !== null);
  const blockedCount = impacted.filter((f) => f.downstream_impact?.impact_kind === "blocked").length;
  const provisionalCount = impacted.filter((f) => f.downstream_impact?.impact_kind === "provisional").length;

  return (
    <section className="card sr-downstream" aria-label="Downstream buildability impact" data-testid="downstream-impact">
      <h2 className="section-title">Downstream buildability impact</h2>
      {impacted.length === 0 ? (
        <p className="section-note" data-testid="downstream-empty">
          No survey fact currently blocks or provisionally affects a dependent
          buildability conclusion.
        </p>
      ) : (
        <>
          <p className="section-note" data-testid="downstream-summary">
            {blockedCount > 0
              ? `${blockedCount} fact${blockedCount === 1 ? "" : "s"} block dependent conclusions`
              : "No fact blocks a dependent conclusion"}
            {provisionalCount > 0
              ? `; ${provisionalCount} render${provisionalCount === 1 ? "s a" : ""} dependent conclusion${provisionalCount === 1 ? "" : "s"} provisional until confirmation.`
              : "."}
          </p>
          <ul className="sr-downstream-list">
            {impacted.map((fact) => {
              const impact = fact.downstream_impact!;
              const display = downstreamKindDisplay(impact.impact_kind);
              return (
                <li
                  key={fact.evidence_id}
                  className="sr-downstream-item"
                  data-testid={`downstream-${fact.evidence_id}`}
                  data-status={impact.impact_kind}
                >
                  <div className="sr-downstream-head">
                    <button
                      type="button"
                      className="sr-link-button sr-downstream-label"
                      onClick={() => onSelectEvidence(fact.evidence_id)}
                      data-testid={`downstream-link-${fact.evidence_id}`}
                    >
                      {fact.display_label}
                    </button>
                    <StatusBadge display={display} testId={`downstream-status-${fact.evidence_id}`} />
                  </div>
                  <p className="sr-downstream-explanation">{impact.reason}</p>
                  <p className="section-note">
                    Coverage: {impact.coverage_status} — {coverageStatusGloss(impact.coverage_status)}
                  </p>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </section>
  );
}
