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
export const TRUNCATION_MARKER = "… [truncated]";

// C0 controls, DEL, and C1 controls. Built with fromCharCode so no literal
// control characters live in the source file (lint-safe).
const CONTROL_CHARS = new RegExp(
  `[${String.fromCharCode(0)}-${String.fromCharCode(31)}${String.fromCharCode(127)}-${String.fromCharCode(159)}]`,
  "g",
);

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
