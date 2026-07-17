/**
 * Client-side BBL format validation (task M2-T001).
 *
 * MIRRORS — never replaces — the server rule in
 * services/api/app/connectors/bbl.py: a canonical BBL is exactly 10 digits
 * with borough digit 1–5 (grounding: packages/contracts README, Geoclient
 * User Guide v2.0.4). The server remains the authority and is still called
 * for every input that passes this check.
 *
 * DELIBERATE GAP (documented): the server additionally rejects all-zero tax
 * block (`invalid_block`) and all-zero tax lot (`invalid_lot`). Those checks
 * are intentionally NOT duplicated here so the server 422 path stays a real,
 * reachable production path (exercised by acceptance scenario S3's
 * server-side case). Client validation exists only to catch obvious format
 * errors BEFORE any network call.
 */

export interface BblValidationOk {
  ok: true;
  /** Canonical 10-digit BBL actually sent to the API. */
  canonical: string;
}

export interface BblValidationError {
  ok: false;
  /** Machine code, aligned with the server's vocabulary where formats match. */
  code: "empty" | "non_numeric" | "wrong_length" | "invalid_borough";
  /** Plain-language message shown next to the input. */
  message: string;
}

export type BblValidationResult = BblValidationOk | BblValidationError;

const DIGITS_ONLY = /^[0-9]+$/;

export function validateBblInput(raw: string): BblValidationResult {
  const text = raw.trim();
  if (text === "") {
    return {
      ok: false,
      code: "empty",
      message: "Enter a 10-digit BBL (borough, block, and lot).",
    };
  }
  if (!DIGITS_ONLY.test(text)) {
    return {
      ok: false,
      code: "non_numeric",
      message:
        "A BBL contains digits only — no dashes, spaces, or letters. " +
        "Example: 1000010010.",
    };
  }
  if (text.length !== 10) {
    return {
      ok: false,
      code: "wrong_length",
      message: `A BBL is exactly 10 digits; you entered ${text.length}.`,
    };
  }
  const borough = Number(text[0]);
  if (borough < 1 || borough > 5) {
    return {
      ok: false,
      code: "invalid_borough",
      message:
        "The first digit is the borough and must be 1–5 " +
        "(1 Manhattan, 2 Bronx, 3 Brooklyn, 4 Queens, 5 Staten Island).",
    };
  }
  return { ok: true, canonical: text };
}
