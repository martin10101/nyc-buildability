import { capNotices, collectConditions } from "@/lib/architect/presented-notices";
import type { ThreeAnswersResults } from "@/lib/architect/three-answers";

/**
 * The shared conditions, stated ONCE (presentation contract §1 "State shared context once" and §3
 * "Show at most three … group additional behind a meaningful count"; walkthrough note N3, which
 * found the same two "If …" lines repeating under about ten results). M5-T149 part A.
 *
 * It reads the document through the M5-T148 notices adapter: `collectConditions` lists each distinct
 * condition once, in first-appearance order; `capNotices` shows at most three and counts the rest.
 * No condition text is typed here (ruling V2) — only the "Condition 1 / Condition 2" NAMING is the
 * component's, so a reader never sees an internal id such as "C1" (the adapter's id).
 */
export function SharedConditions({ results }: { results: ThreeAnswersResults }) {
  const { shared } = collectConditions(results);
  if (shared.length === 0) return null;
  const { visible, moreLabel } = capNotices(shared);
  return (
    <section
      className="ta-shared-conditions"
      data-testid="shared-conditions"
      aria-labelledby="ta-shared-conditions-heading"
    >
      <h3 id="ta-shared-conditions-heading" className="ta-shared-conditions-heading">
        Conditions that apply to these results
      </h3>
      <ol className="ta-shared-conditions-list">
        {visible.map((condition, index) => (
          <li className="ta-shared-condition" data-testid="shared-condition" key={condition.id}>
            <span className="ta-shared-condition-label" data-testid="shared-condition-label">
              {`Condition ${index + 1}`}
            </span>
            {`: ${condition.text}`}
          </li>
        ))}
      </ol>
      {moreLabel ? (
        <p className="ta-shared-conditions-more" data-testid="shared-conditions-more">
          {moreLabel}
        </p>
      ) : null}
    </section>
  );
}
