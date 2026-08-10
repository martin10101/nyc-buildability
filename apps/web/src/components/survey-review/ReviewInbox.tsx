"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { StatusBadge } from "./StatusBadge";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { useSurveyReviewClient } from "@/lib/surveyReview/context";
import { documentStateDisplay } from "@/lib/surveyReview/labels";
import type { InboxOutcome } from "@/lib/surveyReview/types";

/**
 * Review inbox (task M2-T016; workflow §3.1). The queue of documents by state.
 * Handles the honest empty state (§10.8): never a blank canvas — it explains
 * the next action. Loading and recoverable failure states are first-class.
 */
export function ReviewInbox() {
  const client = useSurveyReviewClient();
  const [loading, setLoading] = useState(true);
  const [outcome, setOutcome] = useState<InboxOutcome | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [announcement, setAnnouncement] = useState("");
  const seq = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    const current = ++seq.current;
    setLoading(true);
    void client.listInbox(undefined, { signal: controller.signal }).then((result) => {
      if (seq.current !== current || result.kind === "aborted") return;
      setLoading(false);
      setOutcome(result);
      setAnnouncement(
        result.kind === "inbox"
          ? `Review inbox loaded with ${result.entries.length} document${result.entries.length === 1 ? "" : "s"}.`
          : "The review inbox could not be loaded.",
      );
    });
    return () => controller.abort();
  }, [client, attempt]);

  return (
    <div data-testid="review-inbox">
      <OutcomeAnnouncer message={loading ? "" : announcement} />
      <header className="confirm-header">
        <h1 className="section-title" style={{ fontSize: "1.4rem", margin: 0 }}>
          Survey review inbox
        </h1>
        <p className="section-note">
          Documents awaiting review, ordered by state. Every extracted fact is
          unconfirmed evidence until a designated professional confirms it.
        </p>
      </header>

      {loading ? (
        <section className="card" data-testid="inbox-loading" aria-busy="true">
          <p className="section-note">Loading the review queue…</p>
        </section>
      ) : null}

      {!loading && outcome && outcome.kind === "inbox" ? (
        outcome.entries.length === 0 ? (
          <section className="card" data-testid="inbox-empty">
            <h2 className="section-title">No documents to review</h2>
            <p className="section-note">
              There are no survey documents in review right now. Upload a survey
              to begin, or check back when a document routes to review.
            </p>
          </section>
        ) : (
          <ul className="sr-inbox-list">
            {outcome.entries.map((entry) => (
              <li key={entry.document_id} className="card sr-inbox-row" data-testid={`inbox-row-${entry.document_id}`}>
                <div className="sr-inbox-main">
                  <Link className="sr-inbox-link" href={`/survey/review/${encodeURIComponent(entry.document_id)}`}>
                    {entry.title}
                  </Link>
                  <p className="section-note">
                    BBL {entry.target_bbl} · {entry.open_item_count} open item
                    {entry.open_item_count === 1 ? "" : "s"}
                  </p>
                </div>
                <StatusBadge display={documentStateDisplay(entry.state)} />
              </li>
            ))}
          </ul>
        )
      ) : null}

      {!loading && outcome && outcome.kind !== "inbox" ? (
        <section className="card failure-state" data-testid="inbox-failure">
          <h2 className="failure-title" tabIndex={-1} data-outcome-heading>
            The review inbox could not be loaded
          </h2>
          <p>
            {outcome.kind === "unauthorized"
              ? outcome.message
              : "The review service could not be reached or returned an unexpected response. Nothing was changed."}
          </p>
          <button type="button" className="secondary-button" onClick={() => setAttempt((n) => n + 1)}>
            Retry
          </button>
        </section>
      ) : null}
    </div>
  );
}
