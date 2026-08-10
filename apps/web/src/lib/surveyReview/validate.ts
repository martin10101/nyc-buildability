/**
 * Structural validation of the survey-review read-model BEFORE render
 * (task M2-T016). Mirrors the property screen's discipline
 * (src/lib/validate-profile.ts): a malformed payload becomes a distinct
 * `validation_failure` outcome carrying only a bounded problem list — nothing
 * from an invalid response is ever partially rendered.
 *
 * This is a SHAPE guard, not legal validation: it checks that the fields the
 * review UI reads exist and carry documented enum values, so the components can
 * trust the model. It never computes zoning values, promotes evidence, or
 * upgrades a status.
 */

import type {
  ConfirmationState,
  DocumentState,
  ReviewDocument,
  ReviewFact,
} from "./types";

const DOCUMENT_STATES: ReadonlySet<string> = new Set<DocumentState>([
  "uploaded",
  "processing",
  "auto_extracted",
  "needs_review",
  "rejected",
  "professionally_confirmed",
]);

const CONFIRMATION_STATES: ReadonlySet<string> = new Set<ConfirmationState>([
  "unconfirmed",
  "confirmed",
  "rejected",
]);

const DOWNSTREAM_STATUSES: ReadonlySet<string> = new Set([
  "blocked",
  "provisional",
  "recalculating",
  "cleared",
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export interface ReviewValidation {
  ok: boolean;
  document: ReviewDocument;
  problems: string[];
}

function validateFact(raw: unknown, index: number, problems: string[]): void {
  if (!isRecord(raw)) {
    problems.push(`facts[${index}] is not an object`);
    return;
  }
  const fact = raw.fact;
  if (!isRecord(fact)) {
    problems.push(`facts[${index}].fact is missing or not an object`);
    return;
  }
  if (typeof fact.evidence_id !== "string" || fact.evidence_id === "") {
    problems.push(`facts[${index}].fact.evidence_id is missing`);
  }
  const confirmation = fact.professional_confirmation;
  if (!isRecord(confirmation) || !CONFIRMATION_STATES.has(String(confirmation.state))) {
    problems.push(
      `facts[${index}].fact.professional_confirmation.state is missing or not a documented state`,
    );
  }
  if (!Array.isArray(fact.validation_results)) {
    problems.push(`facts[${index}].fact.validation_results is not an array`);
  }
  if (!Array.isArray(fact.correction_history)) {
    problems.push(`facts[${index}].fact.correction_history is not an array`);
  }
  const promotion = raw.promotion;
  if (!isRecord(promotion) || typeof promotion.allowed !== "boolean") {
    problems.push(`facts[${index}].promotion.allowed is missing or not a boolean`);
  }
  if (typeof raw.accepted_history_fingerprint !== "string") {
    problems.push(`facts[${index}].accepted_history_fingerprint is missing`);
  }
}

/**
 * Validate a decoded review-document body. Returns `ok:false` with a bounded
 * problem list when the payload cannot be trusted; the caller renders the
 * validation-failure state and shows NOTHING from the body.
 */
export function validateReviewDocument(body: unknown): ReviewValidation {
  const problems: string[] = [];
  if (!isRecord(body)) {
    return { ok: false, document: {} as ReviewDocument, problems: ["response body is not an object"] };
  }

  if (typeof body.document_id !== "string" || body.document_id === "") {
    problems.push("document_id is missing");
  }
  if (!DOCUMENT_STATES.has(String(body.state))) {
    problems.push("state is missing or not a documented DocumentState");
  }
  if (typeof body.target_bbl !== "string") {
    problems.push("target_bbl is missing");
  }
  if (!Array.isArray(body.state_history)) {
    problems.push("state_history is not an array");
  }
  if (!Array.isArray(body.facts)) {
    problems.push("facts is not an array");
  } else {
    (body.facts as unknown[]).forEach((fact, index) => validateFact(fact, index, problems));
  }
  if (!Array.isArray(body.downstream)) {
    problems.push("downstream is not an array");
  } else {
    (body.downstream as unknown[]).forEach((conclusion, index) => {
      if (!isRecord(conclusion) || !DOWNSTREAM_STATUSES.has(String(conclusion.status))) {
        problems.push(`downstream[${index}].status is missing or not a documented status`);
      }
    });
  }
  const principal = body.principal;
  if (!isRecord(principal) || !isRecord(principal.capabilities)) {
    problems.push("principal.capabilities is missing");
  }
  if (typeof body.extraction_available !== "boolean") {
    problems.push("extraction_available is missing or not a boolean");
  }

  return {
    ok: problems.length === 0,
    document: body as unknown as ReviewDocument,
    problems,
  };
}

/** Narrowed accessor used by tests. */
export type { ReviewFact };
