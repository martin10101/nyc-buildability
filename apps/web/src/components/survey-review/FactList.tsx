"use client";

import { FactRow } from "./FactRow";
import { orderFactsByUrgency } from "@/lib/surveyReview/model";
import type { FactView } from "@/lib/surveyReview/types";

/**
 * The fact list ordered by DECISION URGENCY (task M2-T016; workflow §3.1, §10.1):
 * conflicts and unresolved items first, then unconfirmed evidence, then resolved.
 */
export function FactList({
  facts,
  selectedEvidenceId,
  onSelect,
}: {
  facts: FactView[];
  selectedEvidenceId: string | null;
  onSelect: (evidenceId: string) => void;
}) {
  const ordered = orderFactsByUrgency(facts);
  return (
    <section className="card" aria-label="Extracted facts to review" data-testid="fact-list">
      <h2 className="section-title">Extracted facts</h2>
      <p className="section-note">
        Ordered by decision urgency. Each fact is unconfirmed evidence until a
        designated professional confirms it — nothing here is verified by
        extraction alone.
      </p>
      {ordered.length === 0 ? (
        <p className="section-note" data-testid="fact-list-empty">
          This document has no extracted facts yet.
        </p>
      ) : (
        <ul className="sr-fact-list">
          {ordered.map((fact) => (
            <FactRow
              key={fact.evidence_id}
              fact={fact}
              selected={fact.evidence_id === selectedEvidenceId}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </section>
  );
}
