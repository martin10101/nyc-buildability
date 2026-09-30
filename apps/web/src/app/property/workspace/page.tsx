import type { Metadata } from "next";
import { Suspense } from "react";
import { notFound } from "next/navigation";
import { ruleEvaluationSurfaceEnabled } from "@/lib/rule-evaluation";
import { surveyReviewEnabled } from "@/lib/surveyReview/config";
import { proposalEditorEnabled } from "@/lib/architect/proposal-editor-flag";
import { unusedFloorAreaSectionEnabled } from "@/lib/architect/unused-floor-area-flag";
import { DashboardEntry } from "@/components/architect/workspace/DashboardEntry";

export const metadata: Metadata = { title: "Property workspace — NYC Buildability (internal)" };
/** Uses the existing SERVER gate; a client query cannot enable a disabled backend.
 * D-01: the set-aside proposal editor is read from its own default-off server flag.
 * D-06: so is the set-aside unused-floor-area section (INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED). */
export default async function DashboardPage({ searchParams }: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  if (!ruleEvaluationSurfaceEnabled({ ruleeval: params.ruleeval })) notFound();
  return <Suspense fallback={null}><DashboardEntry surveyEnabled={surveyReviewEnabled()} proposalEditorEnabled={proposalEditorEnabled()} unusedFloorAreaSectionEnabled={unusedFloorAreaSectionEnabled()}/></Suspense>;
}
