import { fieldLabel, formatValue } from "@/lib/format";
import type { Conflict } from "@/lib/property-profile";

/**
 * Cross-source conflicts (PRD principles 2/4; task M2-T001 output 1).
 * Every conflicting value is shown WITH its source; unresolved conflicts
 * stay visible — the UI never picks a winner and never hides an entry.
 */
export function ConflictsSection({ conflicts }: { conflicts: Conflict[] }) {
  return (
    <section className="card" aria-labelledby="conflicts-title">
      <h2 className="section-title" id="conflicts-title">
        Data conflicts
      </h2>
      {conflicts.length === 0 ? (
        <p className="section-note">
          No cross-source conflicts were detected for this property in the
          current official data.
        </p>
      ) : (
        <>
          <p className="section-note">
            Official records disagree on the values below. All values are
            shown with their source. Nothing has been resolved automatically.
          </p>
          {conflicts.map((conflict) => (
            <div key={conflict.field}>
              <h3 style={{ fontSize: "0.95rem", margin: "0.75rem 0 0" }}>
                {fieldLabel(conflict.field)}{" "}
                <span className="criticality-tag">
                  resolution: {conflict.resolution}
                </span>
              </h3>
              <ul className="conflict-values">
                {conflict.values.map((entry, index) => (
                  <li key={`${conflict.field}-${index}`}>
                    <strong>{formatValue(entry.value)}</strong>
                    {" — source: "}
                    {entry.source_id}
                    {entry.derivation ? ` (${entry.derivation})` : null}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </>
      )}
    </section>
  );
}
