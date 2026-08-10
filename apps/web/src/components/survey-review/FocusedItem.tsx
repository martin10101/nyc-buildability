"use client";

import { useEffect, useRef, useState } from "react";
import { ChecksPanel } from "./ChecksPanel";
import { CorrectionForm } from "./CorrectionForm";
import { CorrectionHistory } from "./CorrectionHistory";
import { ReasonForm } from "./ReasonForm";
import { StatusBadge } from "./StatusBadge";
import { actionFailureCopy } from "@/lib/surveyReview/errorCopy";
import { confirmationDisplay, extractionMethodDisplay } from "@/lib/surveyReview/labels";
import { factResolution } from "@/lib/surveyReview/model";
import type {
  ActionOutcome,
  CorrectFactRequest,
  PrincipalCapabilities,
  ReviewFact,
} from "@/lib/surveyReview/types";

type Mode = "view" | "correct" | "reject";

/**
 * The single FOCUSED item — one at a time (task M2-T016; workflow §10.1, §10.4).
 *
 * Composes: the per-fact confirmation state (layer B), the deterministic-check
 * panel (conflicts unresolvable-by-click, SC-S6), the immutable original ↔
 * current side-by-side with the correction chain (SC-S2), and the action set
 * (Accept / Correct / Reject). Actions the principal is not authorized for are
 * DISABLED with a plain-language reason (§5.2), never silently absent; the
 * server re-enforces authorization independently.
 */
export function FocusedItem({
  fact,
  capabilities,
  onAccept,
  onCorrect,
  onReject,
}: {
  fact: ReviewFact;
  capabilities: PrincipalCapabilities;
  onAccept: () => Promise<ActionOutcome>;
  onCorrect: (req: CorrectFactRequest) => Promise<ActionOutcome>;
  onReject: (reason: string) => Promise<ActionOutcome>;
}) {
  const [mode, setMode] = useState<Mode>("view");
  const [acceptBusy, setAcceptBusy] = useState(false);
  const [acceptError, setAcceptError] = useState<string | null>(null);
  const headingRef = useRef<HTMLHeadingElement | null>(null);

  // Reset to view mode + move focus to the heading whenever the focused fact
  // changes (keyboard/screen-reader users land on the newly focused item).
  useEffect(() => {
    setMode("view");
    setAcceptError(null);
    headingRef.current?.focus();
  }, [fact.fact.evidence_id]);

  const confirmation = confirmationDisplay(fact.fact.professional_confirmation.state);
  const method = extractionMethodDisplay(fact.fact.extraction_method);
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
          {method.advisory ? " · advisory extraction, never authoritative" : ""} ·
          detection confidence {Math.round(fact.fact.confidence * 100)}% (confidence never
          promotes a value)
        </span>
      </div>

      <CorrectionHistory fact={fact.fact} />

      <h4 className="sr-subhead">Deterministic checks</h4>
      <ChecksPanel fact={fact.fact} />

      {mode === "view" ? (
        <div className="sr-action-set" data-testid="focused-actions">
          <div className="sr-action-row">
            <button
              type="button"
              className="secondary-button"
              onClick={handleAccept}
              disabled={!capabilities.can_accept_fact || acceptBusy}
              data-testid="action-accept"
            >
              {acceptBusy ? "Accepting…" : "Accept value"}
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => setMode("correct")}
              disabled={!capabilities.can_correct_fact}
              data-testid="action-correct"
            >
              Correct…
            </button>
            <button
              type="button"
              className="sr-danger-button"
              onClick={() => setMode("reject")}
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
              Some actions are disabled for your role. Only an authorized
              reviewer can accept or correct facts, and only a designated
              professional can reject a detection. The server enforces this
              regardless of what is shown here.
            </p>
          ) : null}
          <p className="section-note">
            Accept affirms the current value. It is not professional
            confirmation — a fact becomes confirmed only when a designated
            professional confirms the whole document.
          </p>
          {resolution === "rejected" ? (
            <p className="section-note" data-testid="rejected-note">
              This detection was rejected. A corrected upload or re-extraction is
              needed to supply a usable value.
            </p>
          ) : null}
          {acceptError ? (
            <p className="inline-error" role="alert" data-testid="accept-error">
              {acceptError}
            </p>
          ) : null}
        </div>
      ) : null}

      {mode === "correct" ? (
        <CorrectionForm
          fact={fact}
          onSubmit={onCorrect}
          onCancel={() => setMode("view")}
        />
      ) : null}

      {mode === "reject" ? (
        <ReasonForm
          heading="Reject this detection"
          submitLabel="Reject detection"
          destructive
          testId="reject-fact"
          onSubmit={onReject}
          onCancel={() => setMode("view")}
        />
      ) : null}
    </section>
  );
}
