/**
 * Survey-review presentation derivations (task M2-T016 rework).
 *
 * PURE, deterministic view helpers over the backend read-model. They order and
 * label items for display; they NEVER compute a promotion verdict, a coverage
 * status, or any legal value (CLAUDE.md #1). The H5 confirm precondition is
 * CONSUMED from the backend (`confirm_precondition_met` + `blocking_fact_ids`),
 * never derived here.
 */

import type { CheckSummaryKind } from "./labels";
import type { DocumentState, FactView, JsonValue, ReviewDocument } from "./types";

/** Presentation-only resolution status for one fact row (not a wire enum). */
export type FactResolution =
  | "conflict"
  | "unresolved"
  | "rejected"
  | "confirmed"
  | "unconfirmed";

export function factResolution(fact: FactView): FactResolution {
  if (fact.check_fail > 0) return "conflict";
  if (fact.check_unresolved > 0) return "unresolved";
  if (fact.confirmation_state === "rejected") return "rejected";
  if (fact.confirmation_state === "confirmed") return "confirmed";
  return "unconfirmed";
}

/** The dominant check-summary badge kind for a fact (or null when nothing to flag). */
export function checkSummaryKind(fact: FactView): CheckSummaryKind | null {
  if (fact.check_fail > 0) return "conflict";
  if (fact.check_unresolved > 0) return "unresolved";
  if (fact.check_pass > 0) return "passed";
  return null;
}

const RESOLUTION_ORDER: Record<FactResolution, number> = {
  conflict: 0,
  unresolved: 1,
  unconfirmed: 2,
  rejected: 3,
  confirmed: 4,
};

export function orderFactsByUrgency(facts: FactView[]): FactView[] {
  return [...facts].sort((a, b) => {
    const byResolution = RESOLUTION_ORDER[factResolution(a)] - RESOLUTION_ORDER[factResolution(b)];
    if (byResolution !== 0) return byResolution;
    return a.evidence_id.localeCompare(b.evidence_id);
  });
}

/**
 * Whether a fact still needs a PER-FACT decision (F1). A clean fact that is
 * merely `unconfirmed` (promotable, no failing/unresolved checks) is NOT counted
 * as open — its only remaining step is DOCUMENT confirmation, so counting it as
 * an "open item" would wrongly keep the dominant action on "resolve items" while
 * Confirm is already available (spec §10.3).
 */
export function isOpenItem(fact: FactView): boolean {
  return fact.check_fail > 0 || fact.check_unresolved > 0;
}

export function openItemCount(document: ReviewDocument): number {
  return document.facts.filter(isOpenItem).length;
}

const CONFIRMABLE_SOURCE_STATES: ReadonlySet<DocumentState> = new Set<DocumentState>([
  "auto_extracted",
  "needs_review",
]);

/** Material facts still blocking confirmation — CONSUMED from `blocking_fact_ids`. */
export function factsBlockingConfirmation(document: ReviewDocument): FactView[] {
  const blocking = new Set(document.blocking_fact_ids);
  return document.facts.filter((f) => blocking.has(f.evidence_id));
}

/**
 * Whether the UI may OFFER the confirm-document action. Requires the confirm
 * capability (server-derived; encodes the pending owner-decided professional
 * role — §5.5), a source state from which edges 9/10 are legal, and the backend
 * H5 precondition (`confirm_precondition_met`). The backend re-enforces all of
 * it. When capabilities are AWAITING-BACKEND, `can_confirm_document` defaults
 * true and the server refusal is surfaced honestly.
 */
export function canOfferConfirm(document: ReviewDocument): boolean {
  return (
    document.principal.capabilities.can_confirm_document &&
    CONFIRMABLE_SOURCE_STATES.has(document.state) &&
    document.confirm_precondition_met
  );
}

/** Facts carrying a blocked/provisional downstream impact (honesty surface). */
export function factsWithDownstreamImpact(document: ReviewDocument): FactView[] {
  return document.facts.filter((f) => f.downstream_impact !== null);
}

/** Compact human rendering of an open JSON value for display. */
export function renderValue(value: JsonValue): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}

/**
 * Type-aware coercion of a correction input string back to the fact's original
 * JSON type (F5), so a numeric measurement is not silently re-typed to a string.
 * Falls back to the raw string when the sample is a string or the input does not
 * parse cleanly (never a silent wrong-type coercion).
 */
export function coerceToSampleType(input: string, sample: JsonValue): JsonValue {
  if (typeof sample === "number") {
    const trimmed = input.trim();
    if (trimmed !== "" && Number.isFinite(Number(trimmed))) return Number(trimmed);
    return input;
  }
  if (typeof sample === "boolean") {
    const lowered = input.trim().toLowerCase();
    if (lowered === "true") return true;
    if (lowered === "false") return false;
    return input;
  }
  return input;
}

/** The dominant next action copy (F1): confirm when all facts are resolved. */
export function dominantAction(document: ReviewDocument): string {
  const open = openItemCount(document);
  if (canOfferConfirm(document)) {
    return "Next: confirm or reject the document below.";
  }
  if (open > 0) {
    return `Next: resolve ${open} open item${open === 1 ? "" : "s"} (highest priority first).`;
  }
  if (document.blocking_fact_ids.length > 0) {
    return "Rejected facts block confirmation — reopen the document or upload a corrected survey.";
  }
  if (!document.principal.capabilities.can_confirm_document && document.principal.capabilities_known) {
    return "All facts are resolved. A designated professional must confirm the document.";
  }
  return "All material facts are resolved.";
}
