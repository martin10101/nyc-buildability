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
export function ReviewInbox({ bbl, embedded = false }: { bbl?: string; embedded?: boolean } = {}) {
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

  const entries = outcome?.kind === "inbox" ? outcome.entries.filter(entry => !bbl || entry.target_bbl === bbl) : [];
  return (
    <div data-testid="review-inbox">
      <OutcomeAnnouncer message={loading ? "" : announcement} />
      <header className="confirm-header">
        {embedded ? <h2 className="section-title">Survey documents for this property</h2> : <h1 className="section-title" style={{ fontSize: "1.4rem", margin: 0 }}>Survey review inbox</h1>}
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
        entries.length === 0 ? (
          <section className="card" data-testid="inbox-empty">
            <h2 className="section-title">No documents to review</h2>
            <p className="section-note">
              {bbl ? "No survey documents for this BBL were returned in the review queue." : "There are no survey documents in review right now."} Upload is not available in this version; existing routed documents appear here.
            </p>
          </section>
        ) : (
          <ul className="sr-inbox-list">
            {entries.map((entry) => (
              <li key={entry.document_digest} className="card sr-inbox-row" data-testid={`inbox-row-${entry.document_digest}`}>
                <div className="sr-inbox-main">
                  <Link className="sr-inbox-link" href={`/survey/review/${encodeURIComponent(entry.document_digest)}`}>
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
