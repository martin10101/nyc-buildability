"use client";

import { useState, type FormEvent } from "react";
import { actionFailureCopy } from "@/lib/surveyReview/errorCopy";
import { coerceToSampleType, renderValue } from "@/lib/surveyReview/model";
import type { ActionOutcome, CorrectFactRequest, FactView } from "@/lib/surveyReview/types";

/** The reviewer's in-progress correction draft — held by the PARENT (F3). */
export interface CorrectionDraft {
  value: string;
  units: string;
  reason: string;
}

export function initialDraft(fact: FactView): CorrectionDraft {
  return { value: renderValue(fact.normalized_value), units: fact.units ?? "", reason: "" };
}

/**
 * Focused correction editor (task M2-T016; workflow §10.4, SC-S1/S6/S7).
 *
 * CONTROLLED by a parent-held `draft` so it SURVIVES a stale-history reload:
 * when the fact remounts (its correction history changed underneath), the parent
 * re-injects the same draft and re-opens the editor — the reviewer's unsaved
 * value/units/reason are re-presented, never lost (F3, §10.8).
 *
 * The immutable `original_value` is read-only; unit changes are explicit (both
 * sides visible). The corrected value is coerced back to the fact's ORIGINAL
 * JSON type (F5) so a numeric measurement is not silently re-typed to a string.
 */
export function CorrectionForm({
  fact,
  draft,
  onDraftChange,
  onSubmit,
  onCancel,
  staleNotice,
}: {
  fact: FactView;
  draft: CorrectionDraft;
  onDraftChange: (draft: CorrectionDraft) => void;
  onSubmit: (req: CorrectFactRequest) => Promise<ActionOutcome>;
  onCancel: () => void;
  staleNotice: string | null;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clientError, setClientError] = useState<string | null>(null);

  const baseValue = renderValue(fact.normalized_value);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setClientError(null);
    if (draft.reason.trim() === "") {
      setClientError("A reason is required for every correction.");
      return;
    }
    const coerced = coerceToSampleType(draft.value, fact.normalized_value);
    const newUnits = draft.units.trim() === "" ? null : draft.units.trim();
    const unchangedValue = JSON.stringify(coerced) === JSON.stringify(fact.normalized_value);
    const unchangedUnits = newUnits === (fact.units ?? null);
    if (unchangedValue && unchangedUnits) {
      setClientError(
        "Nothing changed. A correction must change the value or units — use Accept to affirm an unchanged value.",
      );
      return;
    }
    setBusy(true);
    const outcome = await onSubmit({
      documentDigest: "", // injected by the parent handler
      evidenceId: fact.evidence_id,
      corrected_normalized_value: coerced,
      corrected_units: newUnits,
      reason: draft.reason.trim(),
      accepted_history_fingerprint: fact.accepted_history_fingerprint,
    });
    setBusy(false);
    if (outcome.kind === "updated" || outcome.kind === "aborted") return;
    const copy = actionFailureCopy(outcome);
    setError(copy ? `${copy.title}. ${copy.body}` : "The correction could not be applied.");
    // Input is preserved by the parent-held draft for retry.
  }

  return (
    <form className="sr-editor" onSubmit={handleSubmit} data-testid="correction-form">
      <h4 className="sr-subhead">Correct this fact</h4>
      {staleNotice ? (
        <p className="inline-error" role="alert" data-testid="stale-notice">
          {staleNotice}
        </p>
      ) : null}
      <div className="sr-field">
        <span className="field-label">Original detected value (immutable)</span>
        <output className="sr-readonly" data-testid="correction-original">
          {renderValue(fact.original_value)}
        </output>
      </div>
      <div className="sr-field">
        <label className="field-label" htmlFor="correction-value">
          Corrected normalized value{" "}
          {typeof fact.normalized_value === "number" ? (
            <span className="section-note">(numeric)</span>
          ) : null}
        </label>
        <input
          id="correction-value"
          className="text-input"
          value={draft.value}
          onChange={(e) => onDraftChange({ ...draft, value: e.target.value })}
          disabled={busy}
          data-testid="correction-value"
          inputMode={typeof fact.normalized_value === "number" ? "decimal" : undefined}
        />
        <span className="field-hint">Current: {baseValue}</span>
      </div>
      <div className="sr-field">
        <label className="field-label" htmlFor="correction-units">
          Units (leave blank if unitless)
        </label>
        <input
          id="correction-units"
          className="text-input"
          value={draft.units}
          onChange={(e) => onDraftChange({ ...draft, units: e.target.value })}
          disabled={busy}
          data-testid="correction-units"
        />
      </div>
      <div className="sr-field">
        <label className="field-label" htmlFor="correction-reason">
          Reason (required)
        </label>
        <textarea
          id="correction-reason"
          className="text-input sr-textarea"
          value={draft.reason}
          onChange={(e) => onDraftChange({ ...draft, reason: e.target.value })}
          disabled={busy}
          required
          data-testid="correction-reason"
        />
      </div>
      {clientError ? (
        <p className="inline-error" role="alert" data-testid="correction-client-error">
          {clientError}
        </p>
      ) : null}
      {error ? (
        <p className="inline-error" role="alert" data-testid="correction-error">
          {error}
        </p>
      ) : null}
      <div className="sr-editor-actions">
        <button type="submit" className="primary-button" disabled={busy} data-testid="correction-submit">
          {busy ? "Applying…" : "Apply correction"}
        </button>
        <button type="button" className="secondary-button" onClick={onCancel} disabled={busy}>
          Cancel
        </button>
      </div>
    </form>
  );
}
