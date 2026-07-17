"use client";

import { useState } from "react";
import { fieldLabel } from "@/lib/format";
import { extractSharedReason, groupMissingInputs } from "@/lib/missing-inputs";
import type { MissingInput } from "@/lib/contract";

/**
 * Missing official inputs, rendered under the DOCUMENTED filter policy in
 * src/lib/missing-inputs.ts (M1-T005 G3 defect D3): critical and
 * feasibility-relevant gaps are surfaced immediately; the remaining entries
 * are grouped behind an explicit count toggle. The TOTAL count is always
 * visible and nothing is ever dropped.
 *
 * D4 (M2-T001 G3): the shared boilerplate reason is stated ONCE above the
 * lists; only entries whose reason DIFFERS from it show their reason
 * inline (per-field exceptions stay visible, nothing is altered).
 *
 * Entries the API marks `feasibility_relevant` (contract 1.2.0, the
 * builder's documented completeness basis) carry an explicit tag so the
 * user can tell which gaps drive the completeness statuses.
 */
export function MissingInputsSection({ entries }: { entries: MissingInput[] }) {
  const [showGrouped, setShowGrouped] = useState(false);
  const { surfaced, grouped, total } = groupMissingInputs(entries);
  const sharedReason = extractSharedReason(entries);

  const renderEntry = (entry: MissingInput) => (
    <li key={entry.field}>
      <strong>{fieldLabel(entry.field)}</strong>{" "}
      <span className="criticality-tag">{entry.criticality}</span>
      {entry.feasibility_relevant ? (
        <span className="criticality-tag"> · completeness basis</span>
      ) : null}
      {entry.reason && entry.reason !== sharedReason ? (
        <span className="section-note"> — {entry.reason}</span>
      ) : null}
    </li>
  );

  return (
    <section className="card" aria-labelledby="missing-title">
      <h2 className="section-title" id="missing-title">
        Missing official inputs ({total})
      </h2>
      {total === 0 ? (
        <p className="section-note">
          No expected official input is missing for this property.
        </p>
      ) : (
        <>
          <p className="section-note">
            The official record does not include these fields. Missing values
            are never guessed or filled in. Feasibility-relevant gaps are
            listed first; the rest are grouped below — every entry remains
            accessible.
          </p>
          {sharedReason ? (
            <p className="section-note" data-testid="shared-missing-reason">
              Shared reason (stated once — applies to every field below unless
              a different reason is shown next to it): {sharedReason}
            </p>
          ) : null}
          {surfaced.length > 0 ? (
            <ul className="missing-list" aria-label="Feasibility-relevant missing fields">
              {surfaced.map(renderEntry)}
            </ul>
          ) : (
            <p className="section-note">
              None of the missing fields is classified critical or
              feasibility-relevant under the documented display policy.
            </p>
          )}
          {grouped.length > 0 ? (
            <>
              <button
                type="button"
                className="grouped-toggle"
                aria-expanded={showGrouped}
                onClick={() => setShowGrouped((current) => !current)}
              >
                {showGrouped
                  ? `Hide ${grouped.length} additional missing fields`
                  : `Show ${grouped.length} more missing fields (administrative or non-feasibility columns)`}
              </button>
              {showGrouped ? (
                <ul className="missing-list" aria-label="Additional missing fields">
                  {grouped.map(renderEntry)}
                </ul>
              ) : null}
            </>
          ) : null}
        </>
      )}
    </section>
  );
}
