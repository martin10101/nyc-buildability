import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { InternalBanner } from "@/components/property/InternalBanner";
import { SurveyReviewScreen } from "@/components/survey-review/SurveyReviewScreen";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import { surveyReviewEnabled } from "@/lib/surveyReview/config";
import "../survey-review.css";

export const metadata: Metadata = {
  title: "Survey review — NYC Buildability (internal)",
};

// Required for the runtime flag to mean anything (same as /dashboard). Without
// it Next evaluates `surveyReviewEnabled()` during the BUILD, where the flag is
// unset, and bakes the 404 into a static page — so setting the variable at
// runtime would never open the route.
export const dynamic = "force-dynamic";

/**
 * Survey review screen route (task M2-T016, Packet C). INTERNAL ONLY: gated
 * behind INTERNAL_SURVEY_REVIEW_ENABLED (fail-safe off; 404 when disabled).
 * The path segment is the document DIGEST (`sha256:<64hex>`, URL-encoded); the
 * client screen loads the review read-model through the injected
 * SurveyReviewClient and performs no writes of its own — every decision is a
 * server-authorized action.
 */
export default async function SurveyReviewPage({
  params,
}: {
  params: Promise<{ documentId: string }>;
}) {
  if (!surveyReviewEnabled()) notFound();
  const { documentId } = await params;
  return (
    <div className="property-shell">
      <InternalBanner />
      <SurveyReviewClientProvider>
        <SurveyReviewScreen documentDigest={documentId} />
      </SurveyReviewClientProvider>
    </div>
  );
}
