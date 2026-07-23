'use client';

// Route-level error boundary for /dashboard (M0-T022). Next.js App Router renders
// each route segment independently, so any unexpected error while rendering the
// dashboard is CONTAINED to /dashboard and shown here — it can never impair the
// architect-facing property-analysis product (which shares no code path with the
// dashboard and is rendered on its own routes). We surface only the opaque
// error.digest (never error.message) so no internal detail leaks.
import './dashboard.css';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="dash-shell" role="alert">
      <div className="internal-banner" role="note" data-testid="internal-banner">
        <strong>INTERNAL DEVELOPMENT BUILD</strong> — owner dashboard.
      </div>
      <div className="dash-card">
        <h1 className="dash-card-title">Dashboard temporarily unavailable</h1>
        <p className="dash-muted">
          The owner dashboard hit an unexpected error and was contained here. This is
          internal, read-only observability tooling — the property-analysis product is
          unaffected. No project state was changed.
        </p>
        {error.digest ? (
          <p className="dash-muted dash-small">Reference: {error.digest}</p>
        ) : null}
        <button type="button" className="secondary-button" onClick={() => reset()}>
          Try again
        </button>
      </div>
    </div>
  );
}
