import { Fragment } from "react";
import {
  statusStripItems,
  streetWidthCaseLines,
  type ThreeAnswersResults,
} from "@/lib/architect/three-answers";

/**
 * The one status strip at the top of the results (queue D-05; plan §5a items 1, 2 and 6): a
 * single line of at most three short items. Tapping it opens the details behind it — the
 * lot-selection statement the results carry (plan §3 step 2), why they are out of date, the
 * approvals label, the street-width case, any strip item beyond the third, and the standing
 * notices grouped as one "Notes (N)" item. Nothing here is repeated beside the numbers.
 */
export function ResultsStatusStrip({ results }: { results: ThreeAnswersResults }) {
  const { visible, overflow } = statusStripItems(results);
  const caseLines = streetWidthCaseLines(results);
  return (
    <details className="ta-strip" data-testid="three-answers-status-strip">
      <summary className="ta-strip-line">
        <span className="ta-strip-items">
          {visible.map((text, index) => (
            <Fragment key={`${index}-${text}`}>
              {index > 0 ? (
                <span className="ta-strip-dot" aria-hidden="true">
                  {" · "}
                </span>
              ) : null}
              <span className="ta-strip-item" data-testid="three-answers-status-item">
                {text}
              </span>
            </Fragment>
          ))}
        </span>{" "}
        <span className="ta-strip-hint">Details</span>
      </summary>
      <div className="ta-strip-details" data-testid="three-answers-status-details">
        <ul className="ta-strip-list">
          {results.out_of_date ? (
            <li data-testid="three-answers-out-of-date">
              {results.out_of_date_reason
                ? `Out of date — ${results.out_of_date_reason}`
                : "Out of date"}
            </li>
          ) : null}
          {results.with_approvals_label ? <li>{results.with_approvals_label}</li> : null}
          {caseLines.map(line => (
            <li key={line}>{line}</li>
          ))}
          <li>{results.lot_selection_statement}</li>
          {overflow.map((text, index) => (
            <li key={`overflow-${index}-${text}`} data-testid="three-answers-status-overflow">
              {text}
            </li>
          ))}
        </ul>
        {results.notices_count > 0 ? (
          <p className="ta-notes" data-testid="three-answers-notes">
            Notes ({results.notices_count})
          </p>
        ) : null}
      </div>
    </details>
  );
}
