"use client";

import { useState, type FormEvent } from "react";
import { actionFailureCopy } from "@/lib/surveyReview/errorCopy";
import { renderValue } from "@/lib/surveyReview/model";
import type { ActionOutcome, CorrectFactRequest, ReviewFact } from "@/lib/surveyReview/types";

/**
 * Focused correction editor (task M2-T016; workflow §10.4, SC-S1/S6).
 *
 * Shows the IMMUTABLE `original_value` read-only, the current normalized
 * value/units, an input for the corrected value + units, and a REQUIRED reason.
 * Unit changes are explicit (both sides visible) so a decimal/unit-ambiguity
 * fix is always shown. On failure the reviewer's unsaved input is preserved and
 * re-presented for retry (§10.8) — a failed correction can never corrupt state
 * because corrections are append-only server-side.
 */
export function CorrectionForm({
  fact,
  onSubmit,
  onCancel,
}: {
  fact: ReviewFact;
  onSubmit: (req: CorrectFactRequest) => Promise<ActionOutcome>;
  onCancel: () => void;
}) {
  const initialValue = renderValue(fact.fact.normalized_value);
  const [value, setValue] = useState(initialValue);
  const [units, setUnits] = useState(fact.fact.units ?? "");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clientError, setClientError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setClientError(null);
    if (reason.trim() === "") {
      setClientError("A reason is required for every correction.");
      return;
    }
    const unchangedValue = value === initialValue;
    const unchangedUnits = (units || null) === (fact.fact.units ?? null);
    if (unchangedValue && unchangedUnits) {
      setClientError(
        "Nothing changed. A correction must change the value or units — use Accept to affirm an unchanged value.",
      );
      return;
    }
    setBusy(true);
    const outcome = await onSubmit({
      documentId: "", // filled by the parent handler (kept out of the form)
      evidenceId: fact.fact.evidence_id,
      corrected_normalized_value: value,
      corrected_units: units.trim() === "" ? null : units.trim(),
      reason: reason.trim(),
      accepted_history_fingerprint: fact.accepted_history_fingerprint,
    });
    setBusy(false);
    if (outcome.kind === "updated" || outcome.kind === "aborted") {
      return; // parent closes the editor and re-renders the settled document
    }
    const copy = actionFailureCopy(outcome);
    setError(copy ? `${copy.title}. ${copy.body}` : "The correction could not be applied.");
    // Input is intentionally preserved for retry.
  }

  return (
    <form className="sr-editor" onSubmit={handleSubmit} data-testid="correction-form">
      <h4 className="sr-subhead">Correct this fact</h4>
      <div className="sr-field">
        <span className="field-label">Original detected value (immutable)</span>
        <output className="sr-readonly" data-testid="correction-original">
          {renderValue(fact.fact.original_value)}
        </output>
      </div>
      <div className="sr-field">
        <label className="field-label" htmlFor="correction-value">
          Corrected normalized value
        </label>
        <input
          id="correction-value"
          className="text-input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={busy}
          data-testid="correction-value"
        />
      </div>
      <div className="sr-field">
        <label className="field-label" htmlFor="correction-units">
          Units (leave blank if unitless)
        </label>
        <input
          id="correction-units"
          className="text-input"
          value={units}
          onChange={(e) => setUnits(e.target.value)}
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
          value={reason}
          onChange={(e) => setReason(e.target.value)}
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
