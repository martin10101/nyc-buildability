import type { Metadata } from "next";
import { Suspense } from "react";
import { CompareEntry } from "@/components/compare/CompareScreen";

export const metadata: Metadata = {
  title: "Compare scenario — NYC Buildability (internal)",
};

/**
 * PRODUCT_FLOW step 3 route (task M5-T004). INTERNAL/DEV ONLY — same B-001
 * deployment restriction as the Property and Confirm screens. The PRD section
 * 29 disclaimer is rendered by the shared layout footer on every page; the
 * internal banner renders inside CompareEntry.
 *
 * The Suspense boundary is required by Next.js for useSearchParams during
 * prerendering; the fallback is the empty shell (the client resolves the BBL
 * parameter immediately on hydration).
 */
export default function ComparePage() {
  return (
    <Suspense fallback={null}>
      <CompareEntry />
    </Suspense>
  );
}
