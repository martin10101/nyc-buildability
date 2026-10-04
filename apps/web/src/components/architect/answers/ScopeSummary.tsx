import type { ScopeView } from "@/lib/architect/three-answers";

/**
 * The scope beside the numbers (results contract 1.1.0, D-090-R108): the panel states the estimate
 * is a "Tax-lot-only estimate", names the lot, discloses the assumed corner conditions, and keeps
 * whole-site development and remaining capacity unconfirmed. Every string is read from the `results`
 * document (via `scopeView`); nothing is typed here. The label is a plain-text line, never a
 * coloured chip, and no status is encoded by colour alone (owner directive; plan §5a).
 *
 * The assumed conditions are shown OPEN by default (D-090-R119, per the owner's reviewer audit): a
 * plain heading over a real list, with nothing hidden behind a disclosure, so an architect never
 * has to click to see which corner conditions the estimate assumed. One line per assumption (key,
 * value and basis), its statement on the line underneath, so a longer list still reads cleanly.
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
      <div className="ta-scope-assumptions" data-testid="three-answers-scope-assumptions">
        <h3 className="ta-scope-assumptions-heading">Assumed conditions</h3>
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
      </div>
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
