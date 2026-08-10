/**
 * Stateful in-memory survey-review backend for tests ONLY (task M2-T016 rework).
 *
 * Reconciled to the shipped slice `services/api/app/documents/review_actions.py`:
 * digest-keyed endpoints, `ReviewActionResult` mutation responses (the client
 * re-reads), the backend reject-code set (incl. `confirmation_rejected` with
 * `detail.rejected_fact_ids` and `post_confirmation_edit_refused`), the H5
 * confirm precondition, optimistic concurrency by history fingerprint, and the
 * per-fact `downstream_impact` honesty derivation.
 *
 * Uses ONLY type imports from the app plus a RELATIVE value import of the
 * fingerprint util (no `@/` runtime alias), so Playwright e2e can import it.
 * ONE reducer (`handleRequest`) is shared by component tests (via ./mockClient)
 * and e2e (via a `page.route` handler). Not shipped.
 */

import { historyFingerprint } from "../../lib/surveyReview/fingerprint";
import type { DownstreamImpact, JsonValue } from "@/lib/surveyReview/types";
import {
  DIGEST_PRO,
  DIGEST_UPLOADED,
  DIGEST_USER,
  reviewDoc,
  uploadedDoc,
  type MockDoc,
  type MockFact,
} from "./fixtures";

export interface MockStore {
  documents: Record<string, MockDoc>;
}

export function seedStore(): MockStore {
  return {
    documents: {
      [DIGEST_PRO]: reviewDoc("professional", DIGEST_PRO),
      [DIGEST_USER]: reviewDoc("preparer", DIGEST_USER),
      [DIGEST_UPLOADED]: uploadedDoc(),
    },
  };
}

export { DIGEST_PRO, DIGEST_USER, DIGEST_UPLOADED } from "./fixtures";

export interface HttpResult {
  status: number;
  body: unknown;
}

const NOW = "2026-07-20T13:00:00Z";

function deriveImpact(fact: MockFact, digest: string): DownstreamImpact | null {
  const ids = [fact.evidence_id];
  if (fact.confirmation_state === "rejected") {
    return {
      impact_kind: "blocked",
      coverage_status: "data_conflict",
      reason:
        "survey detection was professionally rejected as unusable; a dependent conclusion cannot rest on it",
      provenance_digest: digest,
      provenance_evidence_ids: ids,
      analysis_readiness: null,
    };
  }
  if (!fact.promotable) {
    return {
      impact_kind: "blocked",
      coverage_status: "professional_review_required",
      reason:
        "survey fact is unresolved: its deterministic checks are incomplete, failed, or in conflict; needs review before a dependent conclusion",
      provenance_digest: digest,
      provenance_evidence_ids: ids,
      analysis_readiness: null,
    };
  }
  if (fact.confirmation_state === "confirmed") return null;
  return {
    impact_kind: "provisional",
    coverage_status: "professional_review_required",
    reason:
      "survey evidence is complete but not professionally confirmed (Unconfirmed evidence); a dependent conclusion is provisional until confirmation",
    provenance_digest: digest,
    provenance_evidence_ids: ids,
    analysis_readiness: null,
  };
}

/** Recompute promotable / downstream / blocking / precondition (matches backend). */
function refreshDerived(doc: MockDoc): void {
  for (const fact of doc.facts) {
    fact.promotable = fact.check_fail === 0 && fact.check_unresolved === 0;
    fact.is_unconfirmed_evidence = fact.confirmation_state !== "confirmed";
    fact.downstream_impact = deriveImpact(fact, doc.document_digest);
  }
  const blocking = doc.facts
    .filter((f) => !f.promotable || f.confirmation_state === "rejected")
    .map((f) => f.evidence_id);
  doc.blocking_fact_ids = blocking;
  doc.confirm_precondition_met = doc.facts.length > 0 && blocking.length === 0;
}

/** Serialise a MockDoc to the backend DocumentReviewView shape (+ principal/title). */
function toReviewView(doc: MockDoc): unknown {
  refreshDerived(doc);
  return {
    document_digest: doc.document_digest,
    target_bbl: doc.target_bbl,
    title: doc.title,
    state: doc.state,
    state_history: doc.state_history,
    facts: doc.facts.map((f) => ({
      evidence_id: f.evidence_id,
      fact_type: f.fact_type,
      original_value: f.original_value,
      baseline_normalized_value: f.baseline_normalized_value,
      baseline_units: f.baseline_units,
      normalized_value: f.normalized_value,
      units: f.units,
      confirmation_state: f.confirmation_state,
      confirmation_note: f.confirmation_note,
      correction_history: f.correction_history,
      correction_count: f.correction_count,
      check_pass: f.check_pass,
      check_fail: f.check_fail,
      check_unresolved: f.check_unresolved,
      location: f.location,
      page_number: f.page_number,
      extraction_method: f.extraction_method,
      is_unconfirmed_evidence: f.is_unconfirmed_evidence,
      promotable: f.promotable,
      downstream_impact: f.downstream_impact,
    })),
    confirm_precondition_met: doc.confirm_precondition_met,
    blocking_fact_ids: doc.blocking_fact_ids,
    original_available: doc.original_available,
    principal: doc.principal,
    correlation_id: "mock-corr-1",
  };
}

function findFact(doc: MockDoc, evidenceId: string): MockFact | undefined {
  return doc.facts.find((f) => f.evidence_id === evidenceId);
}

function err(status: number, reject_code: string, message: string, extra?: object): HttpResult {
  return { status, body: { reject_code, message, ...(extra ?? {}) } };
}

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

  if (segments.length === 1 && segments[0] === "review-inbox") {
    // AWAITING-BACKEND endpoint — the mock returns an honest (empty) queue.
    return { status: 200, body: { entries: [] } };
  }

  const digest = segments[0];
  const doc = digest ? store.documents[digest] : undefined;

  if (segments.length === 2 && segments[1] === "review") {
    if (!doc) return { status: 404, body: { message: "No survey document was found for this digest." } };
    return { status: 200, body: toReviewView(doc) };
  }

  if (method !== "POST") return { status: 405, body: { message: "Method not allowed." } };
  if (!doc) return err(404, "document_record_not_found", "The document was not found.");
  const caps = doc.principal.capabilities;
  const payload = (body ?? {}) as Record<string, unknown>;

  // POST /documents/{digest}/facts/{eid}/{action}
  if (segments.length === 4 && segments[1] === "facts") {
    const fact = findFact(doc, segments[2]);
    const action = segments[3];
    if (!fact) return err(404, "fact_not_found", "The fact was not found.");

    if (action === "accept") {
      if (!caps.can_accept_fact) return err(403, "unauthorized_review_action", "Your role cannot accept facts.");
      // Affirmation: no structural change (audit lives server-side).
      return { status: 200, body: { event_type: "fact_accepted", document_digest: digest } };
    }

    if (action === "correct" || action === "reject") {
      if (doc.state === "professionally_confirmed") {
        return err(
          409,
          "post_confirmation_edit_refused",
          "cannot edit a fact on a professionally_confirmed document; reopen it first",
        );
      }
    }

    if (action === "correct") {
      if (!caps.can_correct_fact) return err(403, "unauthorized_review_action", "Your role cannot correct facts.");
      const reason = typeof payload.reason === "string" ? payload.reason.trim() : "";
      if (reason === "") return err(422, "correction_rejected", "a non-empty reason is required");
      const expected = historyFingerprint(fact.correction_history as unknown as JsonValue[]);
      if (payload.accepted_history_fingerprint !== expected) {
        return err(409, "concurrent_review_modification", "the fact's correction history changed since it was opened");
      }
      const newUnits =
        payload.corrected_units === null || payload.corrected_units === undefined
          ? null
          : String(payload.corrected_units);
      const newValue = payload.corrected_normalized_value;
      const sameValue = JSON.stringify(newValue) === JSON.stringify(fact.normalized_value);
      const sameUnits = newUnits === (fact.units ?? null);
      if (sameValue && sameUnits) return err(422, "correction_rejected", "a correction must change the value or units");
      fact.correction_history.push({
        corrected_at: NOW,
        corrected_by_role: doc.principal.role,
        corrected_by: doc.principal.principal_id ?? undefined,
        previous_normalized_value: fact.normalized_value as JsonValue,
        corrected_normalized_value: newValue as JsonValue,
        previous_units: fact.units,
        corrected_units: newUnits,
        reason,
      });
      fact.normalized_value = newValue;
      fact.units = newUnits;
      fact.correction_count = fact.correction_history.length;
      // The corrected value passes re-validation deterministically.
      fact.check_pass += fact.check_fail + fact.check_unresolved;
      fact.check_fail = 0;
      fact.check_unresolved = 0;
      refreshDerived(doc);
      return { status: 200, body: { event_type: "fact_corrected", document_digest: digest } };
    }

    if (action === "reject") {
      // reject_fact is PROFESSIONAL-ONLY in the shipped slice.
      if (!caps.can_reject_fact) return err(403, "unauthorized_review_action", "Only a professional can reject a fact.");
      const reason = typeof payload.reason === "string" ? payload.reason.trim() : "";
      if (reason === "") return err(422, "confirmation_rejected", "a non-empty reason is required");
      fact.confirmation_state = "rejected";
      fact.confirmation_note = reason;
      refreshDerived(doc);
      return { status: 200, body: { event_type: "fact_rejected", document_digest: digest } };
    }

    return { status: 404, body: { message: "Unknown fact action." } };
  }

  // POST /documents/{digest}/{action}
  if (segments.length === 2) {
    const action = segments[1];

    if (action === "confirm") {
      if (!caps.can_confirm_document) {
        return err(403, "unauthorized_transition_actor", "Only a professional can confirm a document.");
      }
      refreshDerived(doc);
      const rejected = doc.facts.filter((f) => f._material && f.confirmation_state === "rejected").map((f) => f.evidence_id);
      if (rejected.length > 0) {
        return err(422, "confirmation_rejected", "cannot confirm while material facts are professionally rejected", {
          detail: { rejected_fact_ids: rejected },
        });
      }
      if (!doc.confirm_precondition_met) {
        return err(409, "illegal_transition", "material facts are unproven; the H5 precondition is unmet");
      }
      for (const fact of doc.facts) {
        if (fact._material && fact.confirmation_state === "unconfirmed") {
          fact.confirmation_state = "confirmed";
          fact.confirmation_note = null;
        }
      }
      doc.state_history.push({
        from_state: doc.state,
        to_state: "professionally_confirmed",
        actor_kind: "qualified_human",
        actor_id: doc.principal.principal_id ?? "reviewer",
        occurred_at: NOW,
        reason: null,
      });
      doc.state = "professionally_confirmed";
      return { status: 200, body: { event_type: "document_confirmed", document_digest: digest } };
    }

    if (action === "reject") {
      if (!caps.can_reject_document) {
        return err(403, "unauthorized_transition_actor", "Only a professional can reject a document.");
      }
      const reason = typeof payload.reason === "string" ? payload.reason.trim() : "";
      if (reason === "") return err(422, "transition_reason_required", "a reason is required");
      if (doc.state !== "needs_review") return err(409, "illegal_transition", "a document can be rejected only from needs_review");
      doc.state_history.push({
        from_state: doc.state,
        to_state: "rejected",
        actor_kind: "qualified_human",
        actor_id: doc.principal.principal_id ?? "reviewer",
        occurred_at: NOW,
        reason,
      });
      doc.state = "rejected";
      return { status: 200, body: { event_type: "document_rejected", document_digest: digest } };
    }

    if (action === "reopen") {
      if (!caps.can_reopen_document) {
        return err(403, "unauthorized_transition_actor", "Only a professional can reopen a document.");
      }
      const reason = typeof payload.reason === "string" ? payload.reason.trim() : "";
      if (reason === "") return err(422, "transition_reason_required", "a reason is required");
      if (doc.state !== "professionally_confirmed") {
        return err(409, "illegal_transition", "only a confirmed document can be reopened");
      }
      doc.state_history.push({
        from_state: doc.state,
        to_state: "needs_review",
        actor_kind: "qualified_human",
        actor_id: doc.principal.principal_id ?? "reviewer",
        occurred_at: NOW,
        reason,
      });
      doc.state = "needs_review";
      return { status: 200, body: { event_type: "document_reopened", document_digest: digest } };
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
