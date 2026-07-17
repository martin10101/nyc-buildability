"use client";

import { useState } from "react";
import { fieldLabel } from "@/lib/format";
import { groupMissingInputs } from "@/lib/missing-inputs";
import type { MissingInput } from "@/lib/property-profile";

/**
 * Missing official inputs, rendered under the DOCUMENTED filter policy in
 * src/lib/missing-inputs.ts (M1-T005 G3 defect D3): critical and
 * feasibility-relevant gaps are surfaced immediately; the remaining entries
 * are grouped behind an explicit count toggle. The TOTAL count is always
 * visible and nothing is ever dropped.
 */
export function MissingInputsSection({ entries }: { entries: MissingInput[] }) {
  const [showGrouped, setShowGrouped] = useState(false);
  const { surfaced, grouped, total } = groupMissingInputs(entries);

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
          {surfaced.length > 0 ? (
            <ul className="missing-list" aria-label="Feasibility-relevant missing fields">
              {surfaced.map((entry) => (
                <li key={entry.field}>
                  <strong>{fieldLabel(entry.field)}</strong>{" "}
                  <span className="criticality-tag">{entry.criticality}</span>
                  {entry.reason ? (
                    <span className="section-note"> — {entry.reason}</span>
                  ) : null}
                </li>
              ))}
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
                  {grouped.map((entry) => (
                    <li key={entry.field}>
                      <strong>{fieldLabel(entry.field)}</strong>{" "}
                      <span className="criticality-tag">{entry.criticality}</span>
                      {entry.reason ? (
                        <span className="section-note"> — {entry.reason}</span>
                      ) : null}
                    </li>
                  ))}
                </ul>
              ) : null}
            </>
          ) : null}
        </>
      )}
    </section>
  );
}
