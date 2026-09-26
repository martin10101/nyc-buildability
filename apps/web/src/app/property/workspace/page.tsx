import type { Metadata } from "next";
import { Suspense } from "react";
import { notFound } from "next/navigation";
import { ruleEvaluationSurfaceEnabled } from "@/lib/rule-evaluation";
import { surveyReviewEnabled } from "@/lib/surveyReview/config";
import { DashboardEntry } from "@/components/architect/workspace/DashboardEntry";

export const metadata: Metadata = { title: "Property workspace — NYC Buildability (internal)" };
/** Uses the existing SERVER gate; a client query cannot enable a disabled backend. */
export default async function DashboardPage({ searchParams }: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  if (!ruleEvaluationSurfaceEnabled({ ruleeval: params.ruleeval })) notFound();
  return <Suspense fallback={null}><DashboardEntry surveyEnabled={surveyReviewEnabled()}/></Suspense>;
}
