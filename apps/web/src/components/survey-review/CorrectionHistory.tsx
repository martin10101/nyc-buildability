"use client";

import { extractionMethodDisplay } from "@/lib/surveyReview/labels";
import { renderValue } from "@/lib/surveyReview/model";
import type { FactView } from "@/lib/surveyReview/types";

/**
 * Immutability side-by-side (task M2-T016; workflow §6.4, SC-S2).
 *
 * Shows the IMMUTABLE original detection (`original_value` + the pre-correction
 * baseline the backend returns as `baseline_normalized_value`/`baseline_units`)
 * next to the current corrected value and the full append-only correction chain.
 * Corrections NEVER visually overwrite the original.
 */
export function CorrectionHistory({
  fact,
  documentDigest,
  originalAvailable,
}: {
  fact: FactView;
  documentDigest: string;
  originalAvailable: boolean;
}) {
  const history = fact.correction_history;
  const method = extractionMethodDisplay(fact.extraction_method);

  return (
    <div className="sr-history" data-testid="correction-history">
      <div className="sr-sidebyside">
        <section className="sr-original" data-testid="fact-original">
          <h4 className="sr-subhead">Original extraction (immutable)</h4>
          <dl className="sr-kv">
            <div>
              <dt>Original detected value</dt>
              <dd className="fact-value" data-testid="original-value">
                {renderValue(fact.original_value)}
              </dd>
            </div>
            <div>
              <dt>Original normalized value</dt>
              <dd>
                {renderValue(fact.baseline_normalized_value)}
                {fact.baseline_units ? ` ${fact.baseline_units}` : ""}
              </dd>
            </div>
            <div>
              <dt>Extraction method</dt>
              <dd>
                {method.label}
                {method.advisory ? (
                  <span className="section-note"> — advisory, never authoritative</span>
                ) : null}
              </dd>
            </div>
            <div>
              <dt>Original document</dt>
              <dd className="section-note">
                {fact.page_number ? `Page ${fact.page_number} of the ` : "The "}
                immutable original (digest <code>{documentDigest.slice(0, 19)}…</code>).{" "}
                {originalAvailable
                  ? "The original bytes and this value are unchanged after any correction."
                  : "The original bytes are not retrievable in this environment (B-001), but the digest and this value are unchanged."}
              </dd>
            </div>
          </dl>
        </section>

        <section className="sr-current" data-testid="fact-current">
          <h4 className="sr-subhead">Current value</h4>
          <p className="fact-value" data-testid="current-value">
            {renderValue(fact.normalized_value)}
            {fact.units ? <span className="fact-units"> {fact.units}</span> : null}
          </p>
          {history.length === 0 ? (
            <p className="section-note">Never corrected.</p>
          ) : (
            <p className="section-note">
              {history.length} correction{history.length === 1 ? "" : "s"} applied
              (see the chain below). The original above is preserved.
            </p>
          )}
        </section>
      </div>

      {history.length > 0 ? (
        <table className="facts-table sr-history-table" data-testid="correction-chain">
          <caption>Append-only correction history (oldest first)</caption>
          <thead>
            <tr>
              <th scope="col">When</th>
              <th scope="col">By (role)</th>
              <th scope="col">From</th>
              <th scope="col">To</th>
              <th scope="col">Reason</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry, index) => (
              <tr key={`${entry.corrected_at}-${index}`}>
                <td>{entry.corrected_at}</td>
                <td>
                  {entry.corrected_by_role}
                  {entry.corrected_by ? ` (${entry.corrected_by})` : ""}
                </td>
                <td>
                  {renderValue(entry.previous_normalized_value)}
                  {entry.previous_units ? ` ${entry.previous_units}` : ""}
                </td>
                <td>
                  {renderValue(entry.corrected_normalized_value)}
                  {entry.corrected_units ? ` ${entry.corrected_units}` : ""}
                </td>
                <td>{entry.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </div>
  );
}
