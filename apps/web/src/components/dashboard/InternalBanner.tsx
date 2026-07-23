/**
 * Dashboard-local INTERNAL banner (M0-T022). Deliberately self-contained — the
 * owner dashboard imports NOTHING from the architect-facing product, so it stays
 * a clean, one-directional boundary that can later be extracted into its own
 * Render service/subdomain from the same repo. Keeps data-testid="internal-banner"
 * (a11y role="note") consistent with the product banner.
 */
export function InternalBanner() {
  return (
    <div className="internal-banner" role="note" data-testid="internal-banner">
      <strong>INTERNAL DEVELOPMENT BUILD</strong> — read-only owner observability over
      the project-control system. Not a public product, no access control yet, and not a
      legal determination. Do not share outside the engineering team.
    </div>
  );
}
