/**
 * Survey-review presentation derivations (task M2-T016).
 *
 * PURE, deterministic view helpers over the read-model. These order and label
 * items for display; they NEVER compute a promotion verdict, a coverage status,
 * or any legal/zoning value (CLAUDE.md principle 1). Where a decision depends on
 * the H5 gate, this module only READS the backend-supplied `promotion.allowed`
 * verdict — it never derives it.
 */

import type {
  DocumentState,
  JsonValue,
  ReviewDocument,
  ReviewFact,
  ValidationResult,
} from "./types";

/** Presentation-only resolution status for one fact row (not a wire enum). */
export type FactResolution =
  | "conflict" // has a failing deterministic check
  | "unresolved" // has an unresolved deterministic check
  | "rejected" // professional rejected the detection
  | "confirmed" // professional confirmed the fact
  | "unconfirmed"; // clean/unconfirmed evidence, no open check

export function failingChecks(fact: ReviewFact): ValidationResult[] {
  return fact.fact.validation_results.filter((r) => r.status === "fail");
}

export function unresolvedChecks(fact: ReviewFact): ValidationResult[] {
  return fact.fact.validation_results.filter((r) => r.status === "unresolved");
}

/** Derive the display resolution of a fact (decision urgency order below). */
export function factResolution(fact: ReviewFact): FactResolution {
  const confirmation = fact.fact.professional_confirmation.state;
  if (failingChecks(fact).length > 0) return "conflict";
  if (unresolvedChecks(fact).length > 0) return "unresolved";
  if (confirmation === "rejected") return "rejected";
  if (confirmation === "confirmed") return "confirmed";
  return "unconfirmed";
}

const RESOLUTION_ORDER: Record<FactResolution, number> = {
  conflict: 0,
  unresolved: 1,
  unconfirmed: 2,
  rejected: 3,
  confirmed: 4,
};

/**
 * Order facts by DECISION URGENCY (workflow §3.1 step 2): conflicts and
 * unresolved items first, then unconfirmed evidence, then resolved. Stable on
 * `evidence_id` so ordering is deterministic for tests and screen readers.
 */
export function orderFactsByUrgency(facts: ReviewFact[]): ReviewFact[] {
  return [...facts].sort((a, b) => {
    const byResolution = RESOLUTION_ORDER[factResolution(a)] - RESOLUTION_ORDER[factResolution(b)];
    if (byResolution !== 0) return byResolution;
    return a.fact.evidence_id.localeCompare(b.fact.evidence_id);
  });
}

/** Whether a fact still needs a reviewer decision (open item). */
export function isOpenItem(fact: ReviewFact): boolean {
  const resolution = factResolution(fact);
  return resolution === "conflict" || resolution === "unresolved" || resolution === "unconfirmed";
}

export function openItemCount(document: ReviewDocument): number {
  return document.facts.filter((f) => f.material && isOpenItem(f)).length;
}

const CONFIRMABLE_SOURCE_STATES: ReadonlySet<DocumentState> = new Set<DocumentState>([
  "auto_extracted",
  "needs_review",
]);

/**
 * Material facts still BLOCKING document confirmation — those whose backend
 * `promotion` verdict is not allowed. The UI names these when the confirm
 * action is disabled (workflow §4.3). This READS verdicts; it does not compute
 * them.
 */
export function factsBlockingConfirmation(document: ReviewDocument): ReviewFact[] {
  return document.facts.filter((f) => f.material && !f.promotion.allowed);
}

/**
 * Whether the UI may OFFER the confirm-document action. Requires: the confirm
 * capability (server-derived, encodes the pending owner-decided professional
 * role — §5.5), a source state from which edges 9/10 are legal, and every
 * material fact carrying an ALLOWED promotion verdict (H5 precondition mirror).
 * The backend re-enforces all of this regardless of what the UI offers.
 */
export function canOfferConfirm(document: ReviewDocument): boolean {
  return (
    document.principal.capabilities.can_confirm_document &&
    CONFIRMABLE_SOURCE_STATES.has(document.state) &&
    factsBlockingConfirmation(document).length === 0 &&
    document.facts.some((f) => f.material)
  );
}

/** Downstream conclusions currently blocked or provisional (honesty surface). */
export function blockedOrProvisional(document: ReviewDocument) {
  return document.downstream.filter(
    (c) => c.status === "blocked" || c.status === "provisional",
  );
}

/** Compact human rendering of an open JSON value for display. */
export function renderValue(value: JsonValue): string {
  if (value === null) return "—";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}
