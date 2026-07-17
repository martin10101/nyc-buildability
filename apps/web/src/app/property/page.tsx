import type { Metadata } from "next";
import { PropertyLookup } from "@/components/property/PropertyLookup";

export const metadata: Metadata = {
  title: "Property lookup — NYC Buildability (internal)",
};

/**
 * First browser Property screen (task M2-T001). INTERNAL/DEV ONLY: the
 * property-profile API has no authentication yet (B-001) and this screen
 * must not be deployed publicly. The PRD section 29 disclaimer is rendered
 * by the shared layout footer on every page.
 */
export default function PropertyPage() {
  return (
    <div className="property-shell">
      <div className="internal-banner" role="note" data-testid="internal-banner">
        <strong>INTERNAL DEVELOPMENT BUILD</strong> — not a public product.
        This screen has no user accounts or access control yet, shows
        unreviewed official-source data, and must not be shared outside the
        engineering team. Nothing here is a legal determination.
      </div>
      <PropertyLookup />
    </div>
  );
}
