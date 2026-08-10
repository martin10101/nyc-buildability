"use client";

import { useState, type FormEvent } from "react";
import { actionFailureCopy } from "@/lib/surveyReview/errorCopy";
import type { ActionOutcome } from "@/lib/surveyReview/types";

/**
 * Reusable reason-required action form (task M2-T016). Used for rejecting a
 * fact detection and for rejecting a document (workflow §10.4, edge 11). The
 * reason is mandatory (§6.2 / reason discipline). On failure the reviewer's
 * unsaved reason is preserved for retry (§10.8).
 */
export function ReasonForm({
  heading,
  submitLabel,
  destructive,
  onSubmit,
  onCancel,
  testId,
}: {
  heading: string;
  submitLabel: string;
  destructive?: boolean;
  onSubmit: (reason: string) => Promise<ActionOutcome>;
  onCancel: () => void;
  testId: string;
}) {
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clientError, setClientError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setClientError(null);
    if (reason.trim() === "") {
      setClientError("A reason is required.");
      return;
    }
    setBusy(true);
    const outcome = await onSubmit(reason.trim());
    setBusy(false);
    if (outcome.kind === "updated" || outcome.kind === "aborted") return;
    const copy = actionFailureCopy(outcome);
    setError(copy ? `${copy.title}. ${copy.body}` : "The action could not be completed.");
  }

  return (
    <form className="sr-editor" onSubmit={handleSubmit} data-testid={testId}>
      <h4 className="sr-subhead">{heading}</h4>
      <div className="sr-field">
        <label className="field-label" htmlFor={`${testId}-reason`}>
          Reason (required)
        </label>
        <textarea
          id={`${testId}-reason`}
          className="text-input sr-textarea"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          disabled={busy}
          required
          data-testid={`${testId}-reason`}
        />
      </div>
      {clientError ? (
        <p className="inline-error" role="alert" data-testid={`${testId}-client-error`}>
          {clientError}
        </p>
      ) : null}
      {error ? (
        <p className="inline-error" role="alert" data-testid={`${testId}-error`}>
          {error}
        </p>
      ) : null}
      <div className="sr-editor-actions">
        <button
          type="submit"
          className={destructive ? "sr-danger-button" : "primary-button"}
          disabled={busy}
          data-testid={`${testId}-submit`}
        >
          {busy ? "Working…" : submitLabel}
        </button>
        <button type="button" className="secondary-button" onClick={onCancel} disabled={busy}>
          Cancel
        </button>
      </div>
    </form>
  );
}
