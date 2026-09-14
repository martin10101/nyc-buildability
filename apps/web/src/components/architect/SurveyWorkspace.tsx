"use client";
import { useState } from "react";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import { ReviewInbox } from "@/components/survey-review/ReviewInbox";
import { SurveyReviewScreen } from "@/components/survey-review/SurveyReviewScreen";
import { ArchitectShell } from "./ArchitectShell";
export function SurveyWorkspace({ documentDigest }: {
    documentDigest?: string;
}) {
    const [bbl, setBbl] = useState<string | null>(null);
    return <ArchitectShell bbl={bbl} active="survey" surveyEnabled>
    <SurveyReviewClientProvider>
      {documentDigest ? <SurveyReviewScreen documentDigest={documentDigest} onPropertyChange={setBbl}/> : <ReviewInbox />}
    </SurveyReviewClientProvider>
  </ArchitectShell>;
}
