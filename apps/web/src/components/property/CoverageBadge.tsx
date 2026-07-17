import { coverageDisplay } from "@/lib/coverage";
import type { CoverageStatus } from "@/lib/property-profile";

/**
 * Coverage-status badge. Shows the EXACT PRD section 12 enum value plus a
 * symbol and a screen-reader gloss — status is never communicated by color
 * alone (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md section 8).
 */
export function CoverageBadge({ status }: { status: CoverageStatus }) {
  const display = coverageDisplay(status);
  return (
    <span className={`status-badge status-${status}`} title={display.gloss}>
      <span aria-hidden="true">{display.symbol}</span>
      {display.value}
      <span className="visually-hidden"> — {display.gloss}</span>
    </span>
  );
}
