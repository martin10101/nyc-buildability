/**
 * INTERNAL/DEV banner (task M2-T001 S7, shared by the Property and Confirm
 * screens in M2-T002). The property-profile API has no authentication yet
 * (B-001); every screen that shows official data must carry this notice.
 */
export function InternalBanner() {
  return (
    <div className="internal-banner" role="note" data-testid="internal-banner">
      <strong>INTERNAL DEVELOPMENT BUILD</strong> — not a public product.
      This screen has no user accounts or access control yet, shows
      unreviewed official-source data, and must not be shared outside the
      engineering team. Nothing here is a legal determination.
    </div>
  );
}
