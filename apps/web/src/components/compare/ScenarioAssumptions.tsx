import { formatValue } from "@/lib/format";
import type { Scenario } from "@/lib/scenario-contract";

/**
 * Declared typed assumptions (task M5-T004 rework; G1 finding 1).
 *
 * The contract is explicit that this array is the ONLY place a preliminary
 * scenario may vary: "Preliminary scenarios vary ONLY via explicit typed
 * assumptions (no hidden utilization/optimization defaults)" and "Any variation
 * exists ONLY as an explicit entry here" (scenario.schema.json). Before the
 * rework nothing in the compare tree referenced `assumptions` at all, so two
 * preliminary scenarios differing ONLY by a declared `utilization_factor` or
 * `efficiency_ratio` rendered byte-identically — the one honesty field that
 * distinguishes them was invisible.
 *
 * All five leaves render (`key`, `assumption_type`, `value`, `unit`,
 * `rationale`), and the EMPTY case is stated in full, because "no assumption
 * was applied" is the single most important thing this section can say about
 * today's documents: every committed fixture carries zero assumptions, and a
 * reader must be able to tell that from a section that simply was not rendered.
 */
export function ScenarioAssumptions({ document }: { document: Scenario }) {
  return (
    <section className="card" data-testid="scenario-assumptions-section">
      <h2 className="section-title">Declared assumptions</h2>
      <p className="section-note">
        A preliminary scenario may differ from the raw draft cap ONLY through an
        assumption declared here. The platform applies no hidden utilization,
        efficiency, or optimization default, so an empty list below means the
        number above carries no assumption at all.
      </p>
      {document.assumptions.length === 0 ? (
        <p data-testid="scenario-assumptions-empty">
          <span className="status-label">
            No assumptions are declared on this scenario.
          </span>{" "}
          Nothing has been assumed, factored, or discounted — what is shown is
          the draft rule output as the engine recorded it.
        </p>
      ) : (
        <ul className="missing-list" data-testid="scenario-assumptions">
          {document.assumptions.map((assumption, index) => (
            <li
              key={`assumption-${index}`}
              data-testid={`scenario-assumption-${assumption.key}`}
            >
              <strong>{assumption.key}</strong>
              {": "}
              <span className="fact-value">{formatValue(assumption.value)}</span>
              {assumption.unit !== null ? (
                <span className="fact-units"> {assumption.unit}</span>
              ) : null}{" "}
              <span className="section-note">
                (type: <code>{assumption.assumption_type}</code>
                {assumption.unit === null ? "; no unit recorded" : ""})
              </span>
              <p className="section-note" style={{ margin: 0 }}>
                {assumption.rationale === ""
                  ? "No rationale was recorded for this assumption."
                  : assumption.rationale}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
