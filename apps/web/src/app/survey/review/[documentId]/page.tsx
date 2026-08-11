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
  // The digest is `sha256:<64hex>`, so the `:` is percent-encoded in the path.
  // The route param arrives with that encoding intact, and the API client
  // encodes again when it builds the request URL — double-encoding the digest
  // into `sha256%3A...`, which matches no document. Decode once here. A valid
  // digest contains no `%`, so this is a no-op if the param ever arrives
  // already decoded, and a malformed segment fails closed rather than throwing.
  let documentDigest: string;
  try {
    documentDigest = decodeURIComponent(documentId);
  } catch {
    notFound();
  }
  // Enforce the documented digest contract at the boundary (G3 F14). Without it the
  // route forwards an arbitrary decoded string to the client; that is contained today
  // only because every consumer re-encodes with encodeURIComponent, which is a
  // convention, not a guarantee. 404 rather than a typed error keeps this route's
  // information posture identical to the flag-off response (G3 F15).
  if (!/^sha256:[0-9a-f]{64}$/.test(documentDigest)) notFound();
  return (
    <div className="property-shell">
      <InternalBanner />
      <SurveyReviewClientProvider>
        <SurveyReviewScreen documentDigest={documentDigest} />
      </SurveyReviewClientProvider>
    </div>
  );
}
