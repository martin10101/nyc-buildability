"use client";

import { useState } from "react";
import { ReasonForm } from "./ReasonForm";
import { actionFailureCopy } from "@/lib/surveyReview/errorCopy";
import { canOfferConfirm, factsBlockingConfirmation } from "@/lib/surveyReview/model";
import type { ActionOutcome, ReviewDocument } from "@/lib/surveyReview/types";

/**
 * Document decision panel (task M2-T016 rework; workflow §4.3, §5.3, §10.3).
 *
 * The CONFIRM control is present only for a principal with `can_confirm_document`
 * and enabled only when the backend H5 precondition is met
 * (`confirm_precondition_met`, CONSUMED). When disabled it NAMES the exact
 * blocking facts (`blocking_fact_ids`). A `confirmation_rejected` refusal (a
 * professionally-rejected material fact) is surfaced with its `rejected_fact_ids`.
 * A confirmed document offers REOPEN (edge 12). No automatic/AI path anywhere.
 */
export function ConfirmDocumentPanel({
  document,
  onConfirm,
  onRejectDocument,
  onReopenDocument,
  onSelectEvidence,
}: {
  document: ReviewDocument;
  onConfirm: () => Promise<ActionOutcome>;
  onRejectDocument: (reason: string) => Promise<ActionOutcome>;
  onReopenDocument: (reason: string) => Promise<ActionOutcome>;
  onSelectEvidence: (evidenceId: string) => void;
}) {
  const [mode, setMode] = useState<"view" | "reject" | "reopen">("view");
  const [confirmBusy, setConfirmBusy] = useState(false);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [rejectedFactIds, setRejectedFactIds] = useState<string[]>([]);

  const capabilities = document.principal.capabilities;
  const canConfirm = canOfferConfirm(document);
  const blocking = factsBlockingConfirmation(document);
  const labelFor = (id: string) =>
    document.facts.find((f) => f.evidence_id === id)?.display_label ?? id;

  async function handleConfirm() {
    setConfirmError(null);
    setRejectedFactIds([]);
    setConfirmBusy(true);
    const outcome = await onConfirm();
    setConfirmBusy(false);
    if (outcome.kind === "updated" || outcome.kind === "aborted") return;
    const copy = actionFailureCopy(outcome);
    setConfirmError(copy ? `${copy.title}. ${copy.body}` : "The document could not be confirmed.");
    if (outcome.kind === "error" && outcome.rejectedFactIds) {
      setRejectedFactIds(outcome.rejectedFactIds);
    }
  }

  if (document.state === "professionally_confirmed") {
    return (
      <section className="card sr-decision" data-testid="document-decision">
        <h2 className="section-title">Document confirmed</h2>
        <p className="section-note" data-testid="confirmed-note">
          A designated professional confirmed this document after per-fact review.
          Each fact still carries its own confirmation state above.
        </p>
        {capabilities.can_reopen_document ? (
          <>
            <button
              type="button"
              className="sr-danger-button"
              onClick={() => setMode("reopen")}
              data-testid="action-reopen-document"
            >
              Reopen document…
            </button>
            {mode === "reopen" ? (
              <ReasonForm
                heading="Reopen this document (post-confirmation contradiction)"
                submitLabel="Reopen document"
                destructive
                testId="reopen-document"
                onSubmit={onReopenDocument}
                onCancel={() => setMode("view")}
              />
            ) : null}
          </>
        ) : (
          <p className="section-note" data-testid="reopen-capability-note">
            Only a designated professional can reopen a confirmed document.
          </p>
        )}
      </section>
    );
  }

  if (document.state === "rejected") {
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
          decision is reserved for that role. The specific qualifying designation
          is pending an owner decision.
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
            deterministic checks and no material fact is rejected. These facts
            still block confirmation:
          </p>
          {blocking.length > 0 ? (
            <ul className="sr-blocking-list">
              {blocking.map((f) => (
                <li key={f.evidence_id}>
                  <button
                    type="button"
                    className="sr-link-button"
                    onClick={() => onSelectEvidence(f.evidence_id)}
                    data-testid={`blocking-fact-${f.evidence_id}`}
                  >
                    {f.display_label}
                  </button>
                  {f.confirmation_state === "rejected"
                    ? " — professionally rejected (blocks confirmation until replaced)"
                    : f.check_fail > 0
                      ? " — has a data conflict"
                      : f.check_unresolved > 0
                        ? " — has an unresolved check"
                        : ""}
                </li>
              ))}
            </ul>
          ) : (
            <p className="section-note">This document has no material facts to confirm yet.</p>
          )}
        </div>
      ) : null}

      {confirmError ? (
        <p className="inline-error" role="alert" data-testid="confirm-document-error">
          {confirmError}
        </p>
      ) : null}
      {rejectedFactIds.length > 0 ? (
        <ul className="sr-blocking-list" data-testid="confirm-rejected-facts">
          {rejectedFactIds.map((id) => (
            <li key={id}>
              <button
                type="button"
                className="sr-link-button"
                onClick={() => onSelectEvidence(id)}
                data-testid={`rejected-blocking-${id}`}
              >
                {labelFor(id)}
              </button>{" "}
              — reject this document or upload a corrected survey to proceed.
            </li>
          ))}
        </ul>
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
