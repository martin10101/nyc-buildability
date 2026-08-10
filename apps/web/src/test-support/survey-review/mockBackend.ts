/**
 * Stateful in-memory survey-review backend for tests ONLY (task M2-T016).
 *
 * This module uses ONLY type imports from the app (erased at transpile time), so
 * it is safe to import from Playwright e2e specs without a runtime `@/` alias.
 * It mirrors the review-action contract (workflow §12): accept / correct /
 * reject a fact, confirm / reject the document, with append-only correction
 * history, the H5 promotion gate, optimistic concurrency, and downstream
 * recalculation.
 *
 * ONE reducer (`handleRequest`) is shared by component tests (via the mock
 * client in ./mockClient.ts) and Playwright e2e (via a `page.route` handler).
 * Not shipped: application code never imports this module.
 */

import type {
  JsonValue,
  ReviewDocument,
  ReviewFact,
  ValidationResult,
} from "@/lib/surveyReview/types";
import {
  extractionUnavailableDocument,
  inboxEntries,
  reviewDocument,
} from "./fixtures";

export interface MockStore {
  documents: Record<string, ReviewDocument>;
}

export function seedStore(): MockStore {
  return {
    documents: {
      "doc-pro": reviewDocument("professional", "doc-pro"),
      "doc-user": reviewDocument("preparer", "doc-user"),
      "doc-consumer": reviewDocument("consumer", "doc-consumer"),
      "doc-uploaded": extractionUnavailableDocument(),
    },
  };
}

export interface HttpResult {
  status: number;
  body: unknown;
}

function nowIso(): string {
  return "2026-07-20T13:00:00Z";
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

function hasOpenChecks(fact: ReviewFact): boolean {
  return fact.fact.validation_results.some(
    (r) => r.status === "fail" || r.status === "unresolved",
  );
}

/** Recompute promotion verdicts + downstream statuses from evidence state. */
function refreshDerived(doc: ReviewDocument): void {
  for (const rf of doc.facts) {
    if (!rf.material) {
      rf.promotion = { evidence_id: rf.fact.evidence_id, allowed: true, refusal_reasons: [] };
      continue;
    }
    const open = rf.fact.validation_results.filter(
      (r) => r.status === "fail" || r.status === "unresolved",
    );
    rf.promotion = {
      evidence_id: rf.fact.evidence_id,
      allowed: open.length === 0,
      refusal_reasons: open.map((r) => r.detail ?? `${r.check_id} ${r.status}`),
    };
  }
  for (const conclusion of doc.downstream) {
    const blockers = conclusion.blocking_evidence_ids
      .map((id) => doc.facts.find((f) => f.fact.evidence_id === id))
      .filter((f): f is ReviewFact => f !== undefined);
    const stillOpen = blockers.some(
      (f) => hasOpenChecks(f) || f.fact.professional_confirmation.state === "rejected",
    );
    if (!stillOpen) {
      conclusion.status = "cleared";
      conclusion.explanation =
        "Cleared — the blocking survey item was resolved and this conclusion was recomputed.";
    }
  }
}

function findFact(doc: ReviewDocument, evidenceId: string): ReviewFact | undefined {
  return doc.facts.find((f) => f.fact.evidence_id === evidenceId);
}

function actionError(status: number, reject_code: string, message: string, extra?: object): HttpResult {
  return { status, body: { reject_code, message, ...(extra ?? {}) } };
}

/** The single reducer over the store. Returns an HTTP status + body. */
export function handleRequest(
  store: MockStore,
  method: string,
  url: string,
  body: unknown,
): HttpResult {
  const parsed = new URL(url, "http://mock.local");
  const marker = "/api/v1/documents";
  const idx = parsed.pathname.indexOf(marker);
  const tail = idx >= 0 ? parsed.pathname.slice(idx + marker.length) : parsed.pathname;
  const segments = tail.split("/").filter((s) => s.length > 0).map((s) => decodeURIComponent(s));

  // GET /documents/review-inbox
  if (segments.length === 1 && segments[0] === "review-inbox") {
    return { status: 200, body: { entries: inboxEntries() } };
  }

  const docId = segments[0];
  const doc = docId ? store.documents[docId] : undefined;

  // GET /documents/{id}/review
  if (segments.length === 2 && segments[1] === "review") {
    if (!doc) return { status: 404, body: { message: "No survey document was found for this id." } };
    return { status: 200, body: clone(doc) };
  }

  if (method !== "POST") {
    return { status: 405, body: { message: "Method not allowed." } };
  }
  if (!doc) return actionError(404, "not_found", "The document was not found.");
  const capabilities = doc.principal.capabilities;
  const payload = (body ?? {}) as Record<string, unknown>;

  // POST /documents/{id}/facts/{eid}/{action}
  if (segments.length === 4 && segments[1] === "facts") {
    const evidenceId = segments[2];
    const action = segments[3];
    const rf = findFact(doc, evidenceId);
    if (!rf) return actionError(404, "not_found", "The fact was not found.");

    if (action === "accept") {
      if (!capabilities.can_accept_fact) {
        return actionError(403, "unauthorized", "Your role cannot accept facts.");
      }
      return { status: 200, body: clone(doc) };
    }

    if (action === "correct") {
      if (!capabilities.can_correct_fact) {
        return actionError(403, "unauthorized", "Your role cannot correct facts.");
      }
      const reason = typeof payload.reason === "string" ? payload.reason.trim() : "";
      if (reason === "") {
        return actionError(422, "correction_reason_required", "A correction needs a reason.");
      }
      const fingerprint = payload.accepted_history_fingerprint;
      if (fingerprint !== rf.accepted_history_fingerprint) {
        return actionError(409, "stale_history", "The item's accepted history changed.", {
          current_document: clone(doc),
        });
      }
      const newUnits =
        payload.corrected_units === null || payload.corrected_units === undefined
          ? null
          : String(payload.corrected_units);
      const newValueRaw = payload.corrected_normalized_value;
      const sameValue = String(newValueRaw) === String(rf.fact.normalized_value);
      const sameUnits = newUnits === (rf.fact.units ?? null);
      if (sameValue && sameUnits) {
        return actionError(422, "correction_no_op", "Nothing changed by this correction.");
      }
      rf.fact.correction_history.push({
        corrected_at: nowIso(),
        corrected_by_role: doc.principal.role,
        corrected_by: doc.principal.principal_id ?? undefined,
        previous_normalized_value: rf.fact.normalized_value,
        corrected_normalized_value: newValueRaw as JsonValue,
        previous_units: rf.fact.units,
        corrected_units: newUnits,
        reason,
      });
      rf.fact.normalized_value = newValueRaw as JsonValue;
      rf.fact.units = newUnits;
      rf.fact.validation_results = rf.fact.validation_results.map(
        (r): ValidationResult =>
          r.status === "fail" ? { ...r, status: "pass", detail: null } : r,
      );
      rf.accepted_history_fingerprint = `hist-${rf.fact.correction_history.length}`;
      doc.concurrency_token = `doc-token-${Date.now()}`;
      refreshDerived(doc);
      return { status: 200, body: clone(doc) };
    }

    if (action === "reject") {
      if (!capabilities.can_reject_fact) {
        return actionError(403, "unauthorized", "Your role cannot reject facts.");
      }
      const reason = typeof payload.reason === "string" ? payload.reason.trim() : "";
      if (reason === "") {
        return actionError(422, "validation_error", "A rejection needs a reason.");
      }
      rf.fact.professional_confirmation = {
        state: "rejected",
        confirmed_by: doc.principal.principal_id ?? "reviewer",
        confirmed_at: nowIso(),
        note: reason,
      };
      refreshDerived(doc);
      return { status: 200, body: clone(doc) };
    }

    return { status: 404, body: { message: "Unknown fact action." } };
  }

  // POST /documents/{id}/{action}
  if (segments.length === 2) {
    const action = segments[1];
    if (action === "reject") {
      if (!capabilities.can_reject_document) {
        return actionError(
          403,
          "unauthorized_transition_actor",
          "Only a designated professional can reject a document.",
        );
      }
      const reason = typeof payload.reason === "string" ? payload.reason.trim() : "";
      if (reason === "") {
        return actionError(422, "transition_reason_required", "A reason is required.");
      }
      doc.state_history.push({
        from_state: doc.state,
        to_state: "rejected",
        actor_kind: "qualified_human",
        actor_id: doc.principal.principal_id ?? "reviewer",
        occurred_at: nowIso(),
        reason,
      });
      doc.state = "rejected";
      return { status: 200, body: clone(doc) };
    }

    if (action === "confirm") {
      if (!capabilities.can_confirm_document) {
        return actionError(
          403,
          "unauthorized_transition_actor",
          "Only a designated professional can confirm a document.",
        );
      }
      refreshDerived(doc);
      const blocking = doc.facts.filter((f) => f.material && !f.promotion.allowed);
      if (blocking.length > 0) {
        return actionError(
          409,
          "promotion_gate_unmet",
          "Material facts still block confirmation.",
        );
      }
      for (const rf of doc.facts) {
        if (rf.material && rf.fact.professional_confirmation.state === "unconfirmed") {
          rf.fact.professional_confirmation = {
            state: "confirmed",
            confirmed_by: doc.principal.principal_id ?? "reviewer",
            confirmed_at: nowIso(),
            note: null,
          };
        }
      }
      doc.state_history.push({
        from_state: doc.state,
        to_state: "professionally_confirmed",
        actor_kind: "qualified_human",
        actor_id: doc.principal.principal_id ?? "reviewer",
        occurred_at: nowIso(),
        reason: null,
      });
      doc.state = "professionally_confirmed";
      return { status: 200, body: clone(doc) };
    }

    if (action === "reextract") {
      if (!capabilities.can_request_reextraction) {
        return actionError(403, "unauthorized", "Your role cannot request re-extraction.");
      }
      doc.state_history.push({
        from_state: doc.state,
        to_state: "processing",
        actor_kind: "deterministic_pipeline",
        actor_id: null,
        occurred_at: nowIso(),
        reason: null,
      });
      doc.state = "processing";
      return { status: 200, body: clone(doc) };
    }
  }

  return { status: 404, body: { message: "Unknown route." } };
}

/** A `fetch` implementation backed by a store, for the mock client. */
export function createStoreFetch(store: MockStore): typeof fetch {
  return (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString();
    const method = init?.method ?? "GET";
    let body: unknown = null;
    if (init?.body && typeof init.body === "string") {
      try {
        body = JSON.parse(init.body);
      } catch {
        body = null;
      }
    }
    const result = handleRequest(store, method, url, body);
    return new Response(JSON.stringify(result.body), {
      status: result.status,
      headers: { "Content-Type": "application/json", "X-Correlation-ID": "mock-corr-1" },
    });
  }) as typeof fetch;
}
