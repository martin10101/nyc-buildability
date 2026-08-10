/**
 * Structural validation of the backend `DocumentReviewView` BEFORE render
 * (task M2-T016 rework). Mirrors the property screen's discipline
 * (src/lib/validate-profile.ts): a malformed payload becomes a distinct
 * `validation_failure` outcome carrying only a bounded problem list — nothing
 * from an invalid response is ever partially rendered.
 *
 * SHAPE guard only — it checks that the fields the review UI reads exist and
 * carry documented enum values, so the client mapper + components can trust the
 * payload. It never computes zoning values, promotes evidence, or upgrades a
 * status.
 */

import type { ConfirmationState, DocumentState } from "./types";

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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export interface ReviewValidation {
  ok: boolean;
  problems: string[];
}

function validateFact(raw: unknown, index: number, problems: string[]): void {
  if (!isRecord(raw)) {
    problems.push(`facts[${index}] is not an object`);
    return;
  }
  if (typeof raw.evidence_id !== "string" || raw.evidence_id === "") {
    problems.push(`facts[${index}].evidence_id is missing`);
  }
  if (!CONFIRMATION_STATES.has(String(raw.confirmation_state))) {
    problems.push(`facts[${index}].confirmation_state is missing or not a documented state`);
  }
  if (typeof raw.promotable !== "boolean") {
    problems.push(`facts[${index}].promotable is missing or not a boolean`);
  }
  if (!Array.isArray(raw.correction_history)) {
    problems.push(`facts[${index}].correction_history is not an array`);
  }
  for (const key of ["check_pass", "check_fail", "check_unresolved"]) {
    if (typeof raw[key] !== "number") {
      problems.push(`facts[${index}].${key} is missing or not a number`);
    }
  }
}

/**
 * Validate a decoded `DocumentReviewView` body. Returns `ok:false` with a
 * bounded problem list when the payload cannot be trusted; the caller renders
 * the validation-failure state and shows NOTHING from the body.
 */
export function validateReviewView(body: unknown): ReviewValidation {
  const problems: string[] = [];
  if (!isRecord(body)) {
    return { ok: false, problems: ["response body is not an object"] };
  }
  if (typeof body.document_digest !== "string" || body.document_digest === "") {
    problems.push("document_digest is missing");
  }
  if (!DOCUMENT_STATES.has(String(body.state))) {
    problems.push("state is missing or not a documented DocumentState");
  }
  if (typeof body.target_bbl !== "string") {
    problems.push("target_bbl is missing");
  }
  if (typeof body.confirm_precondition_met !== "boolean") {
    problems.push("confirm_precondition_met is missing or not a boolean");
  }
  if (!Array.isArray(body.blocking_fact_ids)) {
    problems.push("blocking_fact_ids is not an array");
  }
  if (!Array.isArray(body.state_history)) {
    problems.push("state_history is not an array");
  }
  if (!Array.isArray(body.facts)) {
    problems.push("facts is not an array");
  } else {
    (body.facts as unknown[]).forEach((fact, index) => validateFact(fact, index, problems));
  }
  return { ok: problems.length === 0, problems };
}
