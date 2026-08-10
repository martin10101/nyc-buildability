"use client";

import { useState } from "react";
import { ReasonForm } from "./ReasonForm";
import { actionFailureCopy } from "@/lib/surveyReview/errorCopy";
import { canOfferConfirm, factsBlockingConfirmation } from "@/lib/surveyReview/model";
import type { ActionOutcome, ReviewDocument } from "@/lib/surveyReview/types";

/**
 * Document decision panel (task M2-T016; workflow §4.3, §5.3, §10.3, SC-S3/S4).
 *
 * The CONFIRM control:
 *   - is present ONLY for a principal with `can_confirm_document`
 *     (server-derived; encodes the pending owner-decided qualified-professional
 *     role — never a hardcoded role string; §5.5);
 *   - is enabled ONLY when the H5 precondition is met (every material fact
 *     carries an ALLOWED promotion verdict — a value CONSUMED from the backend);
 *   - when disabled, NAMES the exact facts still blocking confirmation and why,
 *     never silently hidden.
 *
 * There is NO automatic or AI path to confirmation. Confirming records
 * attribution + timestamp server-side. Rejecting the document (edge 11) needs a
 * reason and the same designated role.
 */
export function ConfirmDocumentPanel({
  document,
  onConfirm,
  onRejectDocument,
  onSelectEvidence,
}: {
  document: ReviewDocument;
  onConfirm: () => Promise<ActionOutcome>;
  onRejectDocument: (reason: string) => Promise<ActionOutcome>;
  onSelectEvidence: (evidenceId: string) => void;
}) {
  const [mode, setMode] = useState<"view" | "reject">("view");
  const [confirmBusy, setConfirmBusy] = useState(false);
  const [confirmError, setConfirmError] = useState<string | null>(null);

  const capabilities = document.principal.capabilities;
  const canConfirm = canOfferConfirm(document);
  const blocking = factsBlockingConfirmation(document);
  const isConfirmed = document.state === "professionally_confirmed";
  const isRejected = document.state === "rejected";

  async function handleConfirm() {
    setConfirmError(null);
    setConfirmBusy(true);
    const outcome = await onConfirm();
    setConfirmBusy(false);
    if (outcome.kind === "updated" || outcome.kind === "aborted") return;
    const copy = actionFailureCopy(outcome);
    setConfirmError(copy ? `${copy.title}. ${copy.body}` : "The document could not be confirmed.");
  }

  if (isConfirmed) {
    return (
      <section className="card sr-decision" data-testid="document-decision">
        <h2 className="section-title">Document confirmed</h2>
        <p className="section-note" data-testid="confirmed-note">
          A designated professional confirmed this document after per-fact
          review. Each fact still carries its own confirmation state above.
        </p>
      </section>
    );
  }

  if (isRejected) {
    return (
      <section className="card sr-decision" data-testid="document-decision">
        <h2 className="section-title">Document rejected</h2>
        <p className="section-note" data-testid="rejected-note">
          This document was professionally rejected and is terminal. A corrected
          upload is a new document with its own digest.
        </p>
      </section>
    );
  }

  return (
    <section className="card sr-decision" aria-label="Document decision" data-testid="document-decision">
      <h2 className="section-title">Document decision</h2>

      {!capabilities.can_confirm_document ? (
        <p className="section-note" data-testid="confirm-capability-note">
          Only a designated qualified professional can confirm or reject this
          document. Your role can review and correct facts, but the document
          decision is reserved for that role. The specific qualifying
          designation is pending an owner decision.
        </p>
      ) : null}

      {capabilities.can_confirm_document ? (
        <div className="sr-decision-actions">
          <button
            type="button"
            className="primary-button"
            onClick={handleConfirm}
            disabled={!canConfirm || confirmBusy}
            data-testid="action-confirm-document"
          >
            {confirmBusy ? "Confirming…" : "Confirm document"}
          </button>
          {capabilities.can_reject_document ? (
            <button
              type="button"
              className="sr-danger-button"
              onClick={() => setMode("reject")}
              data-testid="action-reject-document"
            >
              Reject document…
            </button>
          ) : null}
        </div>
      ) : null}

      {capabilities.can_confirm_document && !canConfirm ? (
        <div className="sr-blocking" data-testid="confirm-blocked-explanation">
          <p className="section-note">
            Confirmation is unavailable until every material fact passes its
            deterministic checks. These facts still block confirmation:
          </p>
          {blocking.length > 0 ? (
            <ul className="sr-blocking-list">
              {blocking.map((f) => (
                <li key={f.fact.evidence_id}>
                  <button
                    type="button"
                    className="sr-link-button"
                    onClick={() => onSelectEvidence(f.fact.evidence_id)}
                    data-testid={`blocking-fact-${f.fact.evidence_id}`}
                  >
                    {f.display_label}
                  </button>
                  {f.promotion.refusal_reasons.length > 0
                    ? ` — ${f.promotion.refusal_reasons.join("; ")}`
                    : ""}
                </li>
              ))}
            </ul>
          ) : (
            <p className="section-note">
              This document has no material facts to confirm yet.
            </p>
          )}
        </div>
      ) : null}

      {confirmError ? (
        <p className="inline-error" role="alert" data-testid="confirm-document-error">
          {confirmError}
        </p>
      ) : null}

      {mode === "reject" ? (
        <ReasonForm
          heading="Reject this document"
          submitLabel="Reject document"
          destructive
          testId="reject-document"
          onSubmit={onRejectDocument}
          onCancel={() => setMode("view")}
        />
      ) : null}
    </section>
  );
}
