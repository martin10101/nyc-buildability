import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { InternalBanner } from "@/components/property/InternalBanner";
import { ReviewInbox } from "@/components/survey-review/ReviewInbox";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import { surveyReviewEnabled } from "@/lib/surveyReview/config";
import "./survey-review.css";

export const metadata: Metadata = {
  title: "Survey review inbox — NYC Buildability (internal)",
};

/**
 * Survey review inbox route (task M2-T016, Packet C). INTERNAL ONLY: gated
 * behind the non-public runtime flag INTERNAL_SURVEY_REVIEW_ENABLED (fail-safe
 * off; 404 when disabled). Same B-001 deployment restriction as the other
 * internal screens — the app has no auth yet, so this must never be exposed
 * publicly, and the backend re-enforces every review action independently.
 */
export default function SurveyReviewInboxPage() {
  if (!surveyReviewEnabled()) notFound();
  return (
    <div className="property-shell">
      <InternalBanner />
      <SurveyReviewClientProvider>
        <ReviewInbox />
      </SurveyReviewClientProvider>
    </div>
  );
}
