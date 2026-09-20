/**
 * Bounded reflection of server-supplied text (task M2-T002 output A).
 *
 * Everything the API returns is DATA, not markup. React already escapes all
 * interpolated text (the app never uses dangerouslySetInnerHTML — enforced
 * by grep in the producer self-check), so the remaining hardening is:
 *
 *   1. LENGTH caps — a hostile or misbehaving upstream cannot flood the
 *      screen or the accessibility tree with megabytes of "message".
 *   2. CONTROL-CHARACTER stripping — C0/C1 controls (except \n and \t,
 *      which are normalized to spaces) can break copy/paste, logs, and
 *      terminal-adjacent tooling; they never render.
 *   3. TOKEN allowlisting for machine identifiers (correlation ids) so a
 *      reflected id is always a plain, copyable token.
 *
 * Truncation is explicit ("… [truncated]") — never silent (UI rule: no
 * silent defaults).
 */

export const MAX_REFLECTED_TEXT_LENGTH = 600;
export const MAX_TOKEN_LENGTH = 64;
export const MAX_ZONING_DISTRICT_LENGTH = 32;
export const TRUNCATION_MARKER = "… [truncated]";

// C0 controls, DEL, and C1 controls. Built with fromCharCode so no literal
// control characters live in the source file (lint-safe).
const CONTROL_CHARS = new RegExp(
  `[${String.fromCharCode(0)}-${String.fromCharCode(31)}${String.fromCharCode(127)}-${String.fromCharCode(159)}]`,
  "g",
);

// Characters OUTSIDE the recorded-zoning-district charset [A-Za-z0-9/-]. Built
// with new RegExp (a plain string) so the '/' carries no regex-delimiter
// ambiguity and needs no escaping; the trailing '-' is a literal hyphen.
const NON_ZONING_DISTRICT_CHARS = new RegExp("[^A-Za-z0-9/-]", "g");

/**
 * Bound a server-supplied string for display. Non-strings and empty/blank
 * strings yield the caller's fallback copy (never a coerced value).
 */
export function boundedText(
  value: unknown,
  fallback: string,
  max: number = MAX_REFLECTED_TEXT_LENGTH,
): string {
  if (typeof value !== "string") {
    return fallback;
  }
  const cleaned = value.replace(/[\r\n\t]+/g, " ").replace(CONTROL_CHARS, "").trim();
  if (cleaned === "") {
    return fallback;
  }
  if (cleaned.length <= max) {
    return cleaned;
  }
  return `${cleaned.slice(0, max)}${TRUNCATION_MARKER}`;
}

/**
 * Bound a machine token (correlation id, state name) to a safe charset.
 * Characters outside [A-Za-z0-9._-] are dropped; an empty result is null
 * (rendered as an explicit absence, never invented).
 */
export function boundedToken(
  value: unknown,
  max: number = MAX_TOKEN_LENGTH,
): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const cleaned = value.replace(/[^A-Za-z0-9._-]/g, "").slice(0, max);
  return cleaned === "" ? null : cleaned;
}

/**
 * Bound a recorded zoning-district identifier for display. Unlike boundedToken,
 * the charset ADMITS the slash that special mixed-use districts carry (e.g.
 * "M1-5/R7-2") alongside the hyphen of a numbered district ("R7-2") and the
 * suffix letters of a variant ("R10H", "C6-4"). boundedToken's [A-Za-z0-9._-]
 * charset would silently strip the '/' and corrupt the value the moment lot-level
 * zoning lands (the sanitizer-boundary lesson: machine identifiers and zoning
 * districts are different vocabularies, just as ISO timestamps are). Anything
 * outside [A-Za-z0-9/-] is dropped, the result is length-capped, and an empty
 * result is an explicit null — never an invented district.
 *
 * This is the recorded PRECONDITION for emitting any non-null recorded zoning
 * (DB-036(a)): every recorded_zoning value must pass through it before it may
 * render, so a slash district can never be silently mangled downstream.
 */
export function boundedZoningDistrict(
  value: unknown,
  max: number = MAX_ZONING_DISTRICT_LENGTH,
): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const cleaned = value.replace(NON_ZONING_DISTRICT_CHARS, "").slice(0, max);
  return cleaned === "" ? null : cleaned;
}
