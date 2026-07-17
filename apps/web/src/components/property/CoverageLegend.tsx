import {
  COVERAGE_STATUSES,
  isCoverageStatus,
  mappedFeatureView,
  type CoverageStatus,
  type PropertyProfile,
} from "@/lib/contract";
import { coverageDisplay } from "@/lib/coverage";

/**
 * ALWAYS-VISIBLE coverage-status legend (M2-T001 G3 defect D3 resolution).
 *
 * A sighted keyboard or touch user previously saw only the bare enum badge
 * (the plain-language gloss lived in a hover `title` and screen-reader
 * text). This legend states the gloss visibly — no hover required — for
 * every status ACTUALLY PRESENT on the current profile.
 *
 * The remaining vocabulary (statuses not present on this profile) sits in
 * a keyboard-accessible disclosure below, so the screen never ASSERTS a
 * status wording (e.g. "verified") that no on-screen fact carries — the
 * honesty rule that the app never presents "verified" on an unreviewed
 * profile stays intact (S7).
 */
export function CoverageLegend({ profile }: { profile: PropertyProfile }) {
  const present = new Set<CoverageStatus>();
  for (const facts of [profile.lot_facts, profile.existing_building_facts]) {
    for (const fact of Object.values(facts)) {
      if (fact.coverage_status && isCoverageStatus(fact.coverage_status)) {
        present.add(fact.coverage_status);
      }
    }
  }
  for (const feature of profile.zoning.mapped_features ?? []) {
    const view = mappedFeatureView(feature);
    if (view.coverageStatus) {
      present.add(view.coverageStatus);
    }
  }

  const presentStatuses = COVERAGE_STATUSES.filter((status) => present.has(status));
  const otherStatuses = COVERAGE_STATUSES.filter((status) => !present.has(status));

  return (
    <section className="card coverage-legend" aria-labelledby="coverage-legend-title" data-testid="coverage-legend">
      <h2 className="section-title" id="coverage-legend-title">
        What the coverage labels mean
      </h2>
      {presentStatuses.length === 0 ? (
        <p className="section-note">
          No fact on this profile carries a coverage label.
        </p>
      ) : (
        <ul className="legend-list" aria-label="Coverage statuses used on this profile">
          {presentStatuses.map((status) => {
            const display = coverageDisplay(status);
            return (
              <li key={status}>
                <span className={`status-badge status-${status}`}>
                  <span aria-hidden="true">{display.symbol}</span>
                  {display.value}
                </span>
                <span className="legend-gloss">{display.gloss}</span>
              </li>
            );
          })}
        </ul>
      )}
      <details className="provenance-details">
        <summary>Full coverage vocabulary (statuses not used on this profile)</summary>
        <div className="provenance-body">
          {/* Plain text, deliberately NOT the badge component: no status
              badge may exist in the DOM for a status no on-screen fact
              carries (the S7 honesty journey counts .status-verified
              nodes), and this list only documents vocabulary. */}
          <ul className="legend-list">
            {otherStatuses.map((status) => {
              const display = coverageDisplay(status);
              return (
                <li key={status}>
                  <code>
                    {display.symbol} {display.value}
                  </code>
                  <span className="legend-gloss">{display.gloss}</span>
                </li>
              );
            })}
          </ul>
        </div>
      </details>
    </section>
  );
}
