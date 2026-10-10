import { capNotices } from "@/lib/architect/presented-notices";
import {
  openItemsView,
  sharedConditionsView,
  type ThreeAnswersResults,
} from "@/lib/architect/three-answers";

/**
 * The shared conditions, stated ONCE, and the short "What needs resolving" list (presentation
 * contract §1/§2 item 6/§3; walkthrough notes N3/N6; rulings V11 (5)/(6)). M5-T149 part A.
 *
 * Only conditions shared by TWO OR MORE results are listed here — each named "Condition N" and
 * stated once (`sharedConditionsView`). A condition that applies to a single result is a local
 * exception and is shown in full WITH that result (AnswerCard), never here (the contract's
 * local-exception rule). `capNotices` shows at most three and counts the rest.
 *
 * Open items: read through `openItemsView` (the document's own reasons and resolvers), capped the
 * same way; each names what it affects and what would settle it. No text is typed here (ruling V2).
 */
export function SharedConditions({ results }: { results: ThreeAnswersResults }) {
  const shared = sharedConditionsView(results);
  const openItems = openItemsView(results);
  if (shared.length === 0 && openItems.length === 0) return null;
  const conditions = capNotices(shared);
  const items = capNotices(openItems);
  return (
    <section
      className="ta-shared-conditions"
      data-testid="shared-conditions"
      aria-label="Conditions and open items"
    >
      {shared.length > 0 ? (
        <div className="ta-shared-conditions-group">
          <h3 className="ta-shared-conditions-heading">Conditions that apply to several results</h3>
          <ol className="ta-shared-conditions-list">
            {conditions.visible.map(condition => (
              <li className="ta-shared-condition" data-testid="shared-condition" key={condition.name}>
                <span className="ta-shared-condition-label" data-testid="shared-condition-label">
                  {condition.name}
                </span>
                {`: ${condition.text}`}
              </li>
            ))}
          </ol>
          {conditions.moreLabel ? (
            <p className="ta-shared-conditions-more" data-testid="shared-conditions-more">
              {conditions.moreLabel}
            </p>
          ) : null}
        </div>
      ) : null}
      {openItems.length > 0 ? (
        <div className="ta-open-items-group">
          <h3 className="ta-open-items-heading">What needs resolving</h3>
          <ul className="ta-open-items-list">
            {items.visible.map((item, index) => (
              <li className="ta-open-item" data-testid="open-item" key={`${item.affects}-${index}`}>
                <span className="ta-open-item-affects" data-testid="open-item-affects">
                  {item.affects}
                </span>
                <span className="ta-open-item-settle" data-testid="open-item-settle">
                  What would settle it: {item.settledBy}
                </span>
              </li>
            ))}
          </ul>
          {items.moreLabel ? (
            <p className="ta-open-items-more" data-testid="open-items-more">
              {items.moreLabel}
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
