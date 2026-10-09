"use client";

import type { FormEvent, RefObject } from "react";

/**
 * Address entry inputs (task M5-T015, design spec section 5). Purely
 * presentational and controlled by AddressResolutionScreen — this form
 * validates NOTHING: the Geoclient connector is the sole validation
 * authority (an empty or insufficient submit returns the connector's own
 * 422 invalid_input, rendered as its error card). The ONLY client guard is
 * the submit button staying inert while both house number and street are
 * blank — a UX nicety, never a validation authority, and it never
 * suppresses a 422 the server would have returned.
 *
 * The borough is a native <select> of the five borough names so this field
 * needs no reflected text; ZIP is the alternative the connector accepts
 * (borough-or-zip is the connector's requirement, not ours).
 */

export interface AddressFormValues {
  houseNumber: string;
  street: string;
  /** "" means not chosen; otherwise one of the five borough names. */
  borough: string;
  zip: string;
}

export const EMPTY_ADDRESS_FORM: AddressFormValues = {
  houseNumber: "",
  street: "",
  borough: "",
  zip: "",
};

const BOROUGHS = [
  "Manhattan",
  "Bronx",
  "Brooklyn",
  "Queens",
  "Staten Island",
] as const;

export function AddressForm({
  values,
  onChange,
  onSubmit,
  streetInputRef,
}: {
  values: AddressFormValues;
  onChange: (values: AddressFormValues) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  /** Lets the screen's "Edit the address" recovery affordance move focus
   * back to the street input (never to <body>). */
  streetInputRef?: RefObject<HTMLInputElement | null>;
}) {
  // The ONLY inert condition. Deliberately NOT disabled while a request is
  // in flight: a new submit supersedes the old one (abort + monotonic seq),
  // exactly like the PropertyLookup machine this screen clones.
  const submitInert = values.houseNumber.trim() === "" && values.street.trim() === "";
  return (
    <form
      className="bbl-form"
      onSubmit={onSubmit}
      noValidate
      data-testid="address-form"
    >
      <div className="field-group">
        <label className="field-label" htmlFor="address-house-number">
          House number
        </label>
        <input
          id="address-house-number"
          name="house_number"
          className="text-input"
          autoComplete="off"
          placeholder="e.g. 120"
          value={values.houseNumber}
          onChange={(event) =>
            onChange({ ...values, houseNumber: event.target.value })
          }
          aria-describedby="address-house-number-hint"
        />
        <span className="field-hint" id="address-house-number-hint">
          As it appears in the postal address.
        </span>
      </div>
      <div className="field-group">
        <label className="field-label" htmlFor="address-street">
          Street
        </label>
        <input
          id="address-street"
          name="street"
          className="text-input"
          autoComplete="off"
          placeholder="e.g. Broadway"
          value={values.street}
          onChange={(event) => onChange({ ...values, street: event.target.value })}
          aria-describedby="address-street-hint"
          ref={streetInputRef}
        />
        <span className="field-hint" id="address-street-hint">
          Street name only — the city&apos;s service normalizes spelling.
        </span>
      </div>
      <div className="field-group">
        <label className="field-label" htmlFor="address-borough">
          Borough
        </label>
        <select
          id="address-borough"
          name="borough"
          className="text-input"
          value={values.borough}
          onChange={(event) => onChange({ ...values, borough: event.target.value })}
          aria-describedby="address-borough-hint"
        >
          <option value="">Choose a borough…</option>
          {BOROUGHS.map((borough) => (
            <option key={borough} value={borough}>
              {borough}
            </option>
          ))}
        </select>
        <span className="field-hint" id="address-borough-hint">
          The city&apos;s service needs a borough or a ZIP code.
        </span>
      </div>
      <div className="field-group">
        <label className="field-label" htmlFor="address-zip">
          ZIP code (alternative to borough)
        </label>
        <input
          id="address-zip"
          name="zip"
          className="text-input"
          inputMode="numeric"
          autoComplete="off"
          placeholder="e.g. 10007"
          value={values.zip}
          onChange={(event) => onChange({ ...values, zip: event.target.value })}
          aria-describedby="address-zip-hint"
        />
        <span className="field-hint" id="address-zip-hint">
          Optional when a borough is chosen.
        </span>
      </div>
      <button
        type="submit"
        className="primary-button"
        disabled={submitInert}
        data-testid="address-submit"
      >
        Resolve address
      </button>
    </form>
  );
}
