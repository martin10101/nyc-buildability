/**
 * Plain-language mapping of typed review outcomes (task M2-T016).
 *
 * The client returns machine-readable `reject_code`s and transport-failure
 * kinds; this module turns each into honest reviewer copy: WHAT failed, whether
 * RETRY is safe, and whether prior state is intact. A raw backend payload is
 * never shown (workflow §10.8). Corrections are append-only, so no failed
 * action can corrupt state — every mappable failure is safe to retry.
 */

import type {
  ActionOutcome,
  ReadDocumentOutcome,
  ReviewRejectCode,
} from "./types";

export interface FailureCopy {
  title: string;
  body: string;
  /** Whether the same action is safe to re-attempt without side effects. */
  retrySafe: boolean;
  /** Whether the reviewer must change their input before retrying. */
  needsInput: boolean;
}

const REJECT_COPY: Record<ReviewRejectCode, FailureCopy> = {
  unauthorized: {
    title: "You are not authorized for this action",
    body:
      "Your role cannot perform this action. Only a designated qualified professional may confirm or reject a document. Nothing was changed.",
    retrySafe: false,
    needsInput: false,
  },
  illegal_transition: {
    title: "That transition is not allowed from the current state",
    body:
      "The document state changed underneath this action, or the action is not legal from where the document is now. Re-open the current state and try again. Nothing was changed.",
    retrySafe: true,
    needsInput: false,
  },
  unauthorized_transition_actor: {
    title: "Only a designated professional can do this",
    body:
      "Confirming or rejecting a document requires the designated qualified-professional role with an attributed identity. Nothing was changed.",
    retrySafe: false,
    needsInput: false,
  },
  transition_reason_required: {
    title: "A reason is required",
    body: "This action needs a non-empty reason before it can be recorded. Add a reason and try again.",
    retrySafe: true,
    needsInput: true,
  },
  promotion_gate_unmet: {
    title: "Some material facts still block confirmation",
    body:
      "The document cannot be confirmed until every material fact has a passing deterministic verdict. Resolve the remaining open items first. Nothing was changed.",
    retrySafe: false,
    needsInput: false,
  },
  correction_tampered: {
    title: "The correction did not match the immutable original",
    body:
      "The submitted correction failed the tamper check against the immutable original value. Nothing was changed — the original is intact. Re-open the current state and try again.",
    retrySafe: true,
    needsInput: true,
  },
  correction_chain_mismatch: {
    title: "The correction history changed since you opened it",
    body:
      "Another correction was appended while you were editing. Nothing was changed. Re-open the current state to see the latest history, then re-apply your change.",
    retrySafe: true,
    needsInput: true,
  },
  correction_no_op: {
    title: "Nothing was changed by this correction",
    body:
      "A correction must change the value or units. Affirming an unchanged value is professional confirmation, not a correction. Change a value, or use Accept instead.",
    retrySafe: true,
    needsInput: true,
  },
  correction_reason_required: {
    title: "A correction needs a reason",
    body: "Every correction must state a non-empty reason so it is reviewable. Add a reason and try again.",
    retrySafe: true,
    needsInput: true,
  },
  stale_history: {
    title: "This item was updated by someone else",
    body:
      "The item's accepted history changed since you opened it, so your change was not applied — nothing was lost or corrupted. The current state has been re-loaded below; re-apply your change on it.",
    retrySafe: true,
    needsInput: true,
  },
  not_found: {
    title: "The document or item was not found",
    body: "This document or fact no longer exists, or the id is wrong. Return to the review inbox.",
    retrySafe: false,
    needsInput: false,
  },
  validation_error: {
    title: "The action input was rejected",
    body: "The review service rejected the submitted input. Check the value and reason, then try again.",
    retrySafe: true,
    needsInput: true,
  },
};

export function rejectCodeCopy(code: ReviewRejectCode): FailureCopy {
  return REJECT_COPY[code];
}

/** Copy for a non-success ACTION outcome (excludes success + aborted). */
export function actionFailureCopy(outcome: ActionOutcome): FailureCopy | null {
  switch (outcome.kind) {
    case "updated":
    case "aborted":
      return null;
    case "error":
      return rejectCodeCopy(outcome.reject_code);
    case "network_error":
      return {
        title: "Could not reach the review service",
        body: outcome.message,
        retrySafe: true,
        needsInput: false,
      };
    case "client_timeout":
      return {
        title: "The action took too long",
        body:
          "The review service did not answer in time, so the request was cancelled. Nothing was changed and no partial write occurred. Retrying is safe.",
        retrySafe: true,
        needsInput: false,
      };
    case "unexpected_response":
      return {
        title: "Unexpected response from the review service",
        body: `The service returned HTTP ${outcome.httpStatus}, which is not a documented response. Nothing was trusted or applied.`,
        retrySafe: true,
        needsInput: false,
      };
    case "validation_failure":
      return {
        title: "The response did not match the review contract",
        body:
          "The service returned data that failed this screen's contract validation. Nothing from that response was applied. This needs platform attention.",
        retrySafe: true,
        needsInput: false,
      };
  }
}

/** Copy for a non-success READ outcome (excludes success + aborted). */
export function readFailureCopy(outcome: ReadDocumentOutcome): FailureCopy | null {
  switch (outcome.kind) {
    case "document":
    case "aborted":
      return null;
    case "not_found":
      return {
        title: "No survey document found",
        body: outcome.message,
        retrySafe: false,
        needsInput: false,
      };
    case "unauthorized":
      return {
        title: "You are not authorized to view this document",
        body: outcome.message,
        retrySafe: false,
        needsInput: false,
      };
    case "network_error":
      return {
        title: "Could not reach the review service",
        body: outcome.message,
        retrySafe: true,
        needsInput: false,
      };
    case "client_timeout":
      return {
        title: "The document took too long to load",
        body:
          "The review service did not answer in time, so the request was cancelled. Retrying is safe.",
        retrySafe: true,
        needsInput: false,
      };
    case "unexpected_response":
      return {
        title: "Unexpected response from the review service",
        body: `The service returned HTTP ${outcome.httpStatus}, which is not a documented response. The body was not trusted or rendered.`,
        retrySafe: true,
        needsInput: false,
      };
    case "validation_failure":
      return {
        title: "The response did not match the review contract",
        body:
          "The service returned a document that failed this screen's contract validation. Nothing from that response is shown.",
        retrySafe: true,
        needsInput: false,
      };
  }
}
