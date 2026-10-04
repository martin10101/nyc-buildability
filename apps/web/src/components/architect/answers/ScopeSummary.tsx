import type { ScopeView } from "@/lib/architect/three-answers";

/**
 * The scope beside the numbers (results contract 1.1.0, D-090-R108): the panel states the estimate
 * is a "Tax-lot-only estimate", names the lot, discloses the assumed corner conditions, and keeps
 * whole-site development and remaining capacity unconfirmed. Every string is read from the `results`
 * document (via `scopeView`); nothing is typed here. The label is a plain-text line, never a
 * coloured chip, and no status is encoded by colour alone (owner directive; plan §5a).
 */
export function ScopeSummary({ view }: { view: ScopeView }) {
  return (
    <section className="ta-scope" data-testid="three-answers-scope" aria-label="Estimate scope">
      <p className="ta-scope-label" data-testid="three-answers-scope-label">
        {view.label}
      </p>
      <p className="ta-scope-lot" data-testid="three-answers-scope-lot">
        {view.lotDisplay}
      </p>
      <details className="ta-scope-assumptions" data-testid="three-answers-scope-assumptions">
        <summary>Assumed conditions</summary>
        <ul className="ta-scope-assumption-list">
          {view.assumptions.map((assumption, index) => (
            <li
              className="ta-scope-assumption"
              key={`${assumption.keyLabel}-${index}`}
              data-testid="three-answers-scope-assumption"
            >
              <span className="ta-scope-assumption-head">
                <span className="ta-scope-assumption-key">{assumption.keyLabel}</span>
                {": "}
                <span
                  className="ta-scope-assumption-value"
                  data-testid="three-answers-scope-assumption-value"
                >
                  {assumption.valueText}
                </span>
                <span className="ta-scope-assumption-dot" aria-hidden="true">
                  {" · "}
                </span>
                <span
                  className="ta-scope-assumption-basis"
                  data-testid="three-answers-scope-assumption-basis"
                >
                  {assumption.basisLabel}
                </span>
              </span>
              <span
                className="ta-scope-assumption-statement"
                data-testid="three-answers-scope-assumption-statement"
              >
                {assumption.statement}
              </span>
            </li>
          ))}
        </ul>
      </details>
      <p className="ta-scope-whole-site" data-testid="three-answers-scope-whole-site">
        {view.wholeSiteStatement}
      </p>
      <p className="ta-scope-remaining" data-testid="three-answers-scope-remaining">
        <span className="ta-scope-remaining-label">{view.remainingLabel}</span>
        <span
          className="ta-scope-remaining-reason"
          data-testid="three-answers-scope-remaining-reason"
        >
          {view.remainingReason}
        </span>
      </p>
    </section>
  );
}
