"use client";

import Link from "next/link";
import { readFailureCopy } from "@/lib/surveyReview/errorCopy";
import type { ReadDocumentOutcome } from "@/lib/surveyReview/types";

/**
 * First-class failure state for the initial document READ (task M2-T016;
 * workflow §10.8, SC-S7). States what failed and whether retry is safe; never a
 * raw backend error. `aborted` renders nothing (a superseded request owns no UI).
 */
export function ReadFailureState({
  outcome,
  onRetry,
}: {
  outcome: Exclude<ReadDocumentOutcome, { kind: "document" }>;
  onRetry: () => void;
}) {
  if (outcome.kind === "aborted") return null;
  const copy = readFailureCopy(outcome);
  if (!copy) return null;
  return (
    <section className="card failure-state" data-testid={`read-failure-${outcome.kind}`}>
      <h2 className="failure-title" tabIndex={-1} data-outcome-heading>
        {copy.title}
      </h2>
      <p>{copy.body}</p>
      {copy.retrySafe ? (
        <button type="button" className="secondary-button" onClick={onRetry} data-testid="read-retry">
          Retry
        </button>
      ) : null}
      <p className="section-note">
        <Link href="/survey/review">Back to the review inbox</Link>
      </p>
    </section>
  );
}
