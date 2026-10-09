"use client";

import type { ResultsRequestBody } from "@/lib/results-api";

/**
 * The results form (task M5-T140, rulings R3, R4). Three inputs and one button, no fetch of its
 * own — the parent (ResultsPanel) owns the request and asks the server ONLY when the button is
 * pressed (ruling R2). Presentation only; it holds no copy of a server value.
 *
 *  - Housing program: the three the server accepts, shown in the words the server's own returned
 *    line uses (read from services/api/.../three_way_document.py `_HOUSING_PROGRAM_DISPLAY`).
 *    Standard residence is the visible starting choice.
 *  - Floor-to-floor height: an editable field, EMPTY at the start, with its helper line. The
 *    website keeps NO starting number of its own; an empty field sends no height and the returned
 *    document calls the height used the default.
 *  - Special-density statement: an OPTIONAL statement the user may make, never pre-filled and
 *    never shown as a fact; sent only when made.
 */

/** The three housing programs and the words the server's own returned line prints for each
 * (R3). The form's label of the chosen program is proven equal to the returned line in the
 * flag-on journey. */
export const HOUSING_PROGRAM_OPTIONS: ReadonlyArray<{
  value: ResultsRequestBody["housing_program"];
  label: string;
}> = [
  { value: "standard_residence", label: "Standard residence" },
  { value: "qualifying_affordable_housing", label: "Qualifying affordable housing" },
  { value: "qualifying_senior_housing", label: "Qualifying senior housing" },
];

export const HEIGHT_HELPER =
  "Leave empty to use the program's starting height. The height used is shown with the results.";

/** R4: the form refuses a non-positive or non-numeric height with this exact message; it invents
 * no upper limit. */
export const HEIGHT_REFUSED_MESSAGE = "Enter a height in feet greater than zero.";

export const DENSITY_STATEMENT_LABEL = "I state that this lot is not in a special density area.";
export const DENSITY_STATEMENT_HELPER =
  "This is your statement about the lot, not a recorded fact. It is sent only when you make it, and any result it produces is shown as conditional on your statement.";

export const SHOW_RESULTS_LABEL = "Show results";

export interface ResultsFormValues {
  program: ResultsRequestBody["housing_program"];
  /** The raw field text, empty at the start (ruling R3). Parsed by the parent; never coerced. */
  heightText: string;
  /** Whether the user has made the special-density statement. Unchecked at the start. */
  densityStatement: boolean;
}

export interface ResultsFormProps {
  values: ResultsFormValues;
  onChange: (next: ResultsFormValues) => void;
  onSubmit: () => void;
  /** Whether a request is in flight: the button stays pressable (a newer press supersedes the
   * older request, ruling R2) but announces the busy state to assistive tech. */
  busy: boolean;
  /** The form's own message for a refused height (ruling R4), or null when the field is fine. */
  heightError: string | null;
}

export function ResultsForm({ values, onChange, onSubmit, busy, heightError }: ResultsFormProps) {
  return (
    <form
      className="results-form card"
      data-testid="results-form"
      aria-label="Results inputs"
      onSubmit={event => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <p className="architect-eyebrow">Development results</p>

      <div className="results-field">
        <label htmlFor="results-housing-program">Housing program</label>
        <select
          id="results-housing-program"
          data-testid="results-housing-program"
          value={values.program}
          onChange={event =>
            onChange({ ...values, program: event.target.value as ResultsFormValues["program"] })
          }
        >
          {HOUSING_PROGRAM_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="results-field">
        <label htmlFor="results-floor-to-floor">Floor-to-floor height (feet)</label>
        <input
          id="results-floor-to-floor"
          data-testid="results-floor-to-floor"
          type="text"
          inputMode="decimal"
          autoComplete="off"
          value={values.heightText}
          aria-describedby="results-floor-to-floor-help"
          aria-invalid={heightError !== null}
          onChange={event => onChange({ ...values, heightText: event.target.value })}
        />
        <p id="results-floor-to-floor-help" className="section-note" data-testid="results-floor-to-floor-help">
          {HEIGHT_HELPER}
        </p>
        {heightError !== null ? (
          <p className="results-field-error" role="alert" data-testid="results-floor-to-floor-error">
            {heightError}
          </p>
        ) : null}
      </div>

      <div className="results-field results-density">
        <label>
          <input
            type="checkbox"
            data-testid="results-density-statement"
            checked={values.densityStatement}
            onChange={event => onChange({ ...values, densityStatement: event.target.checked })}
          />{" "}
          {DENSITY_STATEMENT_LABEL}
        </label>
        <p className="section-note" data-testid="results-density-help">
          {DENSITY_STATEMENT_HELPER}
        </p>
      </div>

      <button type="submit" className="primary-button" data-testid="results-show" aria-busy={busy}>
        {SHOW_RESULTS_LABEL}
      </button>
    </form>
  );
}
