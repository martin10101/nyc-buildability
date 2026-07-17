import { mappedFeatureView, type PropertyProfile } from "@/lib/contract";
import { fieldLabel, formatValue } from "@/lib/format";

interface UnsupportedEntry {
  field: string;
  value: unknown;
}

function collectUnsupported(profile: PropertyProfile): UnsupportedEntry[] {
  const entries: UnsupportedEntry[] = [];
  for (const facts of [profile.lot_facts, profile.existing_building_facts]) {
    for (const [field, fact] of Object.entries(facts)) {
      if (fact.coverage_status === "unsupported") {
        entries.push({ field, value: fact.value });
      }
    }
  }
  for (const feature of profile.zoning.mapped_features ?? []) {
    const view = mappedFeatureView(feature);
    if (view.coverageStatus === "unsupported" && view.feature !== null) {
      entries.push({ field: view.feature, value: view.value });
    }
  }
  return entries;
}

/**
 * Unsupported facts and dataset drift signals (PRD principle 4: conflicts
 * and stale/broken data must be visible). Facts whose coverage_status is
 * `unsupported` plus the connector's drift_signals are listed here in
 * addition to their inline badges.
 */
export function UnsupportedSection({ profile }: { profile: PropertyProfile }) {
  const unsupported = collectUnsupported(profile);
  const driftSignals = profile.reproducibility?.drift_signals ?? [];
  return (
    <section className="card" aria-labelledby="unsupported-title">
      <h2 className="section-title" id="unsupported-title">
        Unsupported values and dataset drift
      </h2>
      {unsupported.length === 0 && driftSignals.length === 0 ? (
        <p className="section-note">
          No unsupported values or dataset drift signals were detected in
          this retrieval.
        </p>
      ) : (
        <>
          {unsupported.length > 0 ? (
            <ul className="missing-list" aria-label="Unsupported facts">
              {unsupported.map((entry) => (
                <li key={entry.field}>
                  <strong>{fieldLabel(entry.field)}</strong> ={" "}
                  {formatValue(entry.value)} — coverage status: unsupported
                </li>
              ))}
            </ul>
          ) : null}
          {driftSignals.length > 0 ? (
            <>
              <p className="section-note">
                The official dataset returned values that no longer match its
                recorded contract (schema drift):
              </p>
              <ul className="missing-list" aria-label="Drift signals">
                {driftSignals.map((signal) => (
                  <li key={signal}>{signal}</li>
                ))}
              </ul>
            </>
          ) : null}
        </>
      )}
    </section>
  );
}
