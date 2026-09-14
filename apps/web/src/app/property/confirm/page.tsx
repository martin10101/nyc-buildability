import type { Metadata } from "next";
import { ArchitectEntry } from "@/components/architect/ArchitectEntry";
import { ruleEvaluationSurfaceEnabled } from "@/lib/rule-evaluation";
import { surveyReviewEnabled } from "@/lib/surveyReview/config";
import { Suspense } from "react";
import { ConfirmEntry } from "@/components/confirm/ConfirmScreen";

export const metadata: Metadata = {
  title: "Confirm property — NYC Buildability (internal)",
};

/**
 * PRODUCT_FLOW step 2 route (task M2-T002). INTERNAL/DEV ONLY — same
 * B-001 deployment restriction as the Property screen. The PRD section 29
 * disclaimer is rendered by the shared layout footer on every page; the
 * internal banner renders inside ConfirmEntry.
 *
 * The Suspense boundary is required by Next.js for useSearchParams during
 * prerendering; the fallback is the empty shell (the client resolves the
 * BBL parameter immediately on hydration).
 */
export default async function ConfirmPage({ searchParams }: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const params = await searchParams;
  if (ruleEvaluationSurfaceEnabled({ ruleeval: params.ruleeval })) return <Suspense fallback={null}><ArchitectEntry defaultView="overview" requireBbl surveyEnabled={surveyReviewEnabled()} /></Suspense>;
  return (
    <Suspense fallback={null}>
      <ConfirmEntry />
    </Suspense>
  );
}
