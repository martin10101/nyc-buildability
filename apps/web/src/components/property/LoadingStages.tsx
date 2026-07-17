/**
 * Staged loading indicator (task M2-T001; design system section 12: show
 * the actual pipeline). Stages reflect what genuinely happens — client
 * format validation (already completed when this renders), then one request
 * to the platform API which retrieves the official record and builds the
 * canonical profile. No fake progress percentages, no invented stages.
 */
export function LoadingStages({ bbl }: { bbl: string }) {
  return (
    <section className="card" aria-live="polite" data-testid="loading-stages">
      <h2 className="section-title">Looking up BBL {bbl}</h2>
      <ol className="loading-stages">
        <li className="stage-done">
          <span aria-hidden="true">✓</span> BBL format checked
        </li>
        <li className="stage-active">
          <span aria-hidden="true">…</span> Retrieving the official property
          record and building the canonical profile
        </li>
        <li className="stage-pending">Rendering official facts</li>
      </ol>
    </section>
  );
}
