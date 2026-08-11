"use client";

import { useEffect, useRef, useState } from "react";
import { ChecksPanel } from "./ChecksPanel";
import { CorrectionForm, type CorrectionDraft } from "./CorrectionForm";
import { CorrectionHistory } from "./CorrectionHistory";
import { ReasonForm } from "./ReasonForm";
import { StatusBadge } from "./StatusBadge";
import { actionFailureCopy } from "@/lib/surveyReview/errorCopy";
import { confirmationDisplay, extractionMethodDisplay } from "@/lib/surveyReview/labels";
import { factResolution } from "@/lib/surveyReview/model";
import type {
  ActionOutcome,
  CorrectFactRequest,
  FactView,
  PrincipalCapabilities,
} from "@/lib/surveyReview/types";

/**
 * The single FOCUSED item — one at a time (task M2-T016; workflow §10.1, §10.4).
 *
 * Composes: the per-fact confirmation state (layer B), the deterministic-check
 * summary (conflicts unresolvable-by-click, SC-S6), the immutable original ↔
 * current side-by-side with the correction chain (SC-S2), and the action set.
 * Actions the principal is not authorized for are DISABLED with a plain-language
 * reason (§5.2), never silently absent; the server re-enforces independently.
 *
 * The correction editor is PARENT-CONTROLLED (`correcting` + `draft`) so the
 * reviewer's unsaved input survives a stale-history reload (F3). Accept shows a
 * session affirmation marker with accurate copy (F2).
 */
export function FocusedItem({
  fact,
  capabilities,
  documentDigest,
  originalAvailable,
  affirmedAt,
  correcting,
  correctionDraft,
  staleNotice,
  onStartCorrect,
  onCancelCorrect,
  onDraftChange,
  onAccept,
  onCorrect,
  onReject,
}: {
  fact: FactView;
  capabilities: PrincipalCapabilities;
  documentDigest: string;
  originalAvailable: boolean;
  affirmedAt: string | null;
  correcting: boolean;
  correctionDraft: CorrectionDraft;
  staleNotice: string | null;
  onStartCorrect: () => void;
  onCancelCorrect: () => void;
  onDraftChange: (draft: CorrectionDraft) => void;
  onAccept: () => Promise<ActionOutcome>;
  onCorrect: (req: CorrectFactRequest) => Promise<ActionOutcome>;
  onReject: (reason: string) => Promise<ActionOutcome>;
}) {
  const [rejecting, setRejecting] = useState(false);
  const [acceptBusy, setAcceptBusy] = useState(false);
  const [acceptError, setAcceptError] = useState<string | null>(null);
  const headingRef = useRef<HTMLHeadingElement | null>(null);

  useEffect(() => {
    setRejecting(false);
    setAcceptError(null);
    headingRef.current?.focus();
  }, [fact.evidence_id]);

  const confirmation = confirmationDisplay(fact.confirmation_state);
  const method = extractionMethodDisplay(fact.extraction_method);
  const resolution = factResolution(fact);

  async function handleAccept() {
    setAcceptError(null);
    setAcceptBusy(true);
    const outcome = await onAccept();
    setAcceptBusy(false);
    if (outcome.kind === "updated" || outcome.kind === "aborted") return;
    const copy = actionFailureCopy(outcome);
    setAcceptError(copy ? `${copy.title}. ${copy.body}` : "The action could not be completed.");
  }

  return (
    <section className="card sr-focused" aria-label="Focused item" data-testid="focused-item">
      <h3 className="section-title" tabIndex={-1} ref={headingRef} data-testid="focused-heading">
        {fact.display_label}
      </h3>
      <div className="sr-focused-meta">
        <StatusBadge display={confirmation} testId="focused-confirmation" />
        <span className="section-note">
          {method.label}
          {method.advisory ? " · advisory extraction, never authoritative" : ""}
        </span>
      </div>

      <CorrectionHistory fact={fact} documentDigest={documentDigest} originalAvailable={originalAvailable} />

      <h4 className="sr-subhead">Deterministic checks</h4>
      <ChecksPanel fact={fact} />

      {!correcting && !rejecting ? (
        <div className="sr-action-set" data-testid="focused-actions">
          <div className="sr-action-row">
            <button
              type="button"
              className="secondary-button"
              onClick={handleAccept}
              disabled={!capabilities.can_accept_fact || acceptBusy}
              data-testid="action-accept"
            >
              {acceptBusy ? "Affirming…" : "Accept value"}
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={onStartCorrect}
              disabled={!capabilities.can_correct_fact}
              data-testid="action-correct"
            >
              Correct…
            </button>
            <button
              type="button"
              className="sr-danger-button"
              onClick={() => setRejecting(true)}
              disabled={!capabilities.can_reject_fact}
              data-testid="action-reject"
            >
              Reject…
            </button>
          </div>
          {!capabilities.can_accept_fact ||
          !capabilities.can_correct_fact ||
          !capabilities.can_reject_fact ? (
            <p className="section-note" data-testid="action-disabled-reason">
              Some actions are disabled for your role. Rejecting a detection is
              reserved for a designated professional. The server enforces this
              regardless of what is shown here.
            </p>
          ) : null}
          {affirmedAt ? (
            <p className="section-note" data-testid="accept-affirmed">
              You affirmed this value this session at {affirmedAt}. A recalculation of
              dependent conclusions was requested. (Affirmation is recorded in the
              server audit trail; this marker is a session reminder.)
            </p>
          ) : (
            <p className="section-note">
              Accept affirms the current value and requests a dependent recalculation.
              It is not professional confirmation — a fact becomes confirmed only when a
              designated professional confirms the whole document.
            </p>
          )}
          {resolution === "rejected" ? (
            <p className="section-note" data-testid="rejected-note">
              This detection was rejected. A corrected upload or re-extraction is needed
              to supply a usable value; it blocks document confirmation until then.
            </p>
          ) : null}
          {acceptError ? (
            <p className="inline-error" role="alert" data-testid="accept-error">
              {acceptError}
            </p>
          ) : null}
        </div>
      ) : null}

      {correcting ? (
        <CorrectionForm
          fact={fact}
          draft={correctionDraft}
          onDraftChange={onDraftChange}
          onSubmit={onCorrect}
          onCancel={onCancelCorrect}
          staleNotice={staleNotice}
        />
      ) : null}

      {rejecting ? (
        <ReasonForm
          heading="Reject this detection"
          submitLabel="Reject detection"
          destructive
          testId="reject-fact"
          onSubmit={onReject}
          onCancel={() => setRejecting(false)}
        />
      ) : null}
    </section>
  );
}
