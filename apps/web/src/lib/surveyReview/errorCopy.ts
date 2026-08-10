/**
 * Plain-language mapping of typed review outcomes (task M2-T016 rework).
 *
 * The client returns machine-readable backend `reject_code`s and transport
 * failures; this module turns each into honest reviewer copy: WHAT failed,
 * whether RETRY is safe, and whether prior state is intact. A raw backend
 * payload is never shown (workflow §10.8). Corrections are append-only, so no
 * failed action can corrupt state.
 */

import type {
  ActionOutcome,
  ReadDocumentOutcome,
  ReviewRejectCode,
} from "./types";

export interface FailureCopy {
  title: string;
  body: string;
  retrySafe: boolean;
  needsInput: boolean;
}

const REJECT_COPY: Record<ReviewRejectCode, FailureCopy> = {
  unauthorized_review_action: {
    title: "You are not authorized for this action",
    body:
      "Your role cannot perform this action. Only a designated qualified professional may confirm, reject, or reopen a document. Nothing was changed.",
    retrySafe: false,
    needsInput: false,
  },
  document_record_not_found: {
    title: "The document was not found",
    body: "This document no longer exists, or the digest is wrong. Return to the review inbox.",
    retrySafe: false,
    needsInput: false,
  },
  fact_not_found: {
    title: "The fact was not found",
    body: "This fact no longer exists on the document. Re-open the current state and try again.",
    retrySafe: true,
    needsInput: false,
  },
  concurrent_review_modification: {
    title: "This item was updated by someone else",
    body:
      "The item's accepted history changed since you opened it, so your change was not applied — nothing was lost or corrupted. The current state has been reloaded; your draft is preserved below — re-apply it.",
    retrySafe: true,
    needsInput: true,
  },
  correction_rejected: {
    title: "The correction was rejected by a deterministic check",
    body:
      "The correction failed a deterministic correction-history check (tamper, chain, append-only, no-op, or missing reason). Nothing was changed — the immutable original is intact. Adjust your input and try again.",
    retrySafe: true,
    needsInput: true,
  },
  confirmation_rejected: {
    title: "Rejected facts block confirmation",
    body:
      "This document cannot be confirmed while material facts are professionally rejected. A rejected detection is unusable and is never overwritten to 'confirmed' — replace it via a re-extraction or a corrected upload first. The blocking facts are listed below.",
    retrySafe: false,
    needsInput: false,
  },
  illegal_transition: {
    title: "That transition is not allowed from the current state",
    body:
      "The document state changed underneath this action, or the H5 precondition is unmet. Resolve the remaining open items and try again. Nothing was changed.",
    retrySafe: false,
    needsInput: false,
  },
  unauthorized_transition_actor: {
    title: "Only a designated professional can do this",
    body:
      "Confirming, rejecting, or reopening a document requires the designated qualified-professional role with an attributed identity. Nothing was changed.",
    retrySafe: false,
    needsInput: false,
  },
  transition_reason_required: {
    title: "A reason is required",
    body: "This action needs a non-empty reason before it can be recorded. Add a reason and try again.",
    retrySafe: true,
    needsInput: true,
  },
  post_confirmation_edit_refused: {
    title: "Reopen the document before editing a confirmed fact",
    body:
      "This document is professionally confirmed, so a fact cannot be corrected or rejected directly — that would silently invalidate a completed review. Reopen the document first (a visible, audited step), then make your change. Nothing was changed.",
    retrySafe: false,
    needsInput: false,
  },
};

export function rejectCodeCopy(code: ReviewRejectCode): FailureCopy {
  return REJECT_COPY[code];
}

export function actionFailureCopy(outcome: ActionOutcome): FailureCopy | null {
  switch (outcome.kind) {
    case "updated":
    case "aborted":
      return null;
    case "error":
      return rejectCodeCopy(outcome.reject_code);
    case "network_error":
      return { title: "Could not reach the review service", body: outcome.message, retrySafe: true, needsInput: false };
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

export function readFailureCopy(outcome: ReadDocumentOutcome): FailureCopy | null {
  switch (outcome.kind) {
    case "document":
    case "aborted":
      return null;
    case "not_found":
      return { title: "No survey document found", body: outcome.message, retrySafe: false, needsInput: false };
    case "unauthorized":
      return {
        title: "You are not authorized to view this document",
        body: outcome.message,
        retrySafe: false,
        needsInput: false,
      };
    case "network_error":
      return { title: "Could not reach the review service", body: outcome.message, retrySafe: true, needsInput: false };
    case "client_timeout":
      return {
        title: "The document took too long to load",
        body: "The review service did not answer in time, so the request was cancelled. Retrying is safe.",
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
