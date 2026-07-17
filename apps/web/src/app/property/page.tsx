import type { Metadata } from "next";
import { InternalBanner } from "@/components/property/InternalBanner";
import { PropertyLookup } from "@/components/property/PropertyLookup";

export const metadata: Metadata = {
  title: "Property lookup — NYC Buildability (internal)",
};

/**
 * First browser Property screen (task M2-T001; hardened in M2-T002).
 * INTERNAL/DEV ONLY: the property-profile API has no authentication yet
 * (B-001) and this screen must not be deployed publicly. The PRD section 29
 * disclaimer is rendered by the shared layout footer on every page.
 */
export default function PropertyPage() {
  return (
    <div className="property-shell">
      <InternalBanner />
      <PropertyLookup />
    </div>
  );
}
