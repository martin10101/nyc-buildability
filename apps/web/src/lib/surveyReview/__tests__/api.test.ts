import { describe, expect, it } from "vitest";
import { boundedEvidenceId, createHttpSurveyReviewClient } from "@/lib/surveyReview/api";
import {
  createMockSurveyReviewClient,
  seedStore,
  DIGEST_PRO,
  DIGEST_USER,
} from "@/test-support/survey-review/mockClient";
import type { ReviewDocument, SurveyReviewClient } from "@/lib/surveyReview/types";

/**
 * Client + reducer contract tests (task M2-T016 rework). Exercises the REAL
 * client decode path (incl. the re-read-after-mutation pattern) against the
 * stateful mock reconciled to the shipped backend: digest keying, the backend
 * reject-code set, the H5 confirm precondition, optimistic concurrency by
 * history fingerprint, and the new confirmation / post-confirmation semantics.
 */

const CLEAN = "sev:doc:p1:1";
const AREA = "sev:doc:p1:2";
const NORTH = "sev:doc:p1:3";

async function read(client: SurveyReviewClient, digest: string): Promise<ReviewDocument> {
  const out = await client.readDocument(digest);
  if (out.kind !== "document") throw new Error(`expected document, got ${out.kind}`);
  return out.document;
}

function fp(doc: ReviewDocument, evidenceId: string): string {
  return doc.facts.find((f) => f.evidence_id === evidenceId)!.accepted_history_fingerprint;
}

describe("survey-review client — reads", () => {
  it("reads a document by digest and maps the backend view", async () => {
    const doc = await read(createMockSurveyReviewClient(), DIGEST_PRO);
    expect(doc.facts).toHaveLength(3);
    expect(doc.facts.find((f) => f.evidence_id === CLEAN)!.promotable).toBe(true);
    expect(doc.facts.find((f) => f.evidence_id === AREA)!.promotable).toBe(false);
    expect(doc.blocking_fact_ids.sort()).toEqual([AREA, NORTH]);
    expect(doc.confirm_precondition_met).toBe(false);
    // capability surface provided by the mock is marked known.
    expect(doc.principal.capabilities_known).toBe(true);
  });

  it("returns not_found for an unknown digest", async () => {
    const out = await createMockSurveyReviewClient().readDocument("sha256:deadbeef");
    expect(out.kind).toBe("not_found");
  });

  it("returns validation_failure for a 200 that fails the read contract", async () => {
    const client = createHttpSurveyReviewClient();
    const out = await client.readDocument("sha256:x", {
      fetchImpl: async () =>
        new Response(JSON.stringify({ document_digest: "sha256:x" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    });
    expect(out.kind).toBe("validation_failure");
  });
});

describe("survey-review client — corrections (SC-S1/S2/S6)", () => {
  it("re-reads after a correction: appends history, preserves original, clears the conflict", async () => {
    const client = createMockSurveyReviewClient(seedStore());
    const before = await read(client, DIGEST_PRO);
    const out = await client.correctFact({
      documentDigest: DIGEST_PRO,
      evidenceId: AREA,
      corrected_normalized_value: 4800,
      corrected_units: "square_feet",
      reason: "OCR misread the stated area against the boundary calculation.",
      accepted_history_fingerprint: fp(before, AREA),
    });
    expect(out.kind).toBe("updated");
    if (out.kind !== "updated") return;
    const fact = out.document.facts.find((f) => f.evidence_id === AREA)!;
    expect(fact.correction_history).toHaveLength(1);
    expect(fact.original_value).toBe("5,000 SF"); // immutable
    expect(fact.normalized_value).toBe(4800); // F5: numeric preserved
    expect(fact.promotable).toBe(true);
    expect(out.document.blocking_fact_ids).not.toContain(AREA);
  });

  it("refuses a stale correction with concurrent_review_modification + a fresh document", async () => {
    const out = await createMockSurveyReviewClient().correctFact({
      documentDigest: DIGEST_PRO,
      evidenceId: AREA,
      corrected_normalized_value: 4800,
      corrected_units: "square_feet",
      reason: "fix",
      accepted_history_fingerprint: "sha256:STALE",
    });
    expect(out.kind).toBe("error");
    if (out.kind !== "error") return;
    expect(out.reject_code).toBe("concurrent_review_modification");
    expect(out.currentDocument).toBeDefined();
  });

  it("refuses a no-op correction (correction_rejected)", async () => {
    const client = createMockSurveyReviewClient();
    const before = await read(client, DIGEST_PRO);
    const out = await client.correctFact({
      documentDigest: DIGEST_PRO,
      evidenceId: AREA,
      corrected_normalized_value: 5000,
      corrected_units: "square_feet",
      reason: "unchanged",
      accepted_history_fingerprint: fp(before, AREA),
    });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("correction_rejected");
  });
});

describe("survey-review client — confirmation semantics (SC-S4)", () => {
  it("refuses confirmation while facts are unproven (illegal_transition / H5)", async () => {
    const out = await createMockSurveyReviewClient().confirmDocument({ documentDigest: DIGEST_PRO });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("illegal_transition");
  });

  it("confirms only after every material fact is resolved", async () => {
    const client = createMockSurveyReviewClient(seedStore());
    for (const eid of [AREA, NORTH]) {
      const doc = await read(client, DIGEST_PRO);
      await client.correctFact({
        documentDigest: DIGEST_PRO,
        evidenceId: eid,
        corrected_normalized_value: 4800,
        corrected_units: "square_feet",
        reason: "resolve",
        accepted_history_fingerprint: fp(doc, eid),
      });
    }
    const out = await client.confirmDocument({ documentDigest: DIGEST_PRO });
    expect(out.kind).toBe("updated");
    if (out.kind !== "updated") return;
    expect(out.document.state).toBe("professionally_confirmed");
    expect(out.document.facts.find((f) => f.evidence_id === CLEAN)!.confirmation_state).toBe("confirmed");
  });

  it("blocks confirmation with confirmation_rejected + rejected_fact_ids when a fact is rejected", async () => {
    const client = createMockSurveyReviewClient(seedStore());
    // resolve the conflict, then reject the unresolved detection.
    const doc = await read(client, DIGEST_PRO);
    await client.correctFact({
      documentDigest: DIGEST_PRO,
      evidenceId: AREA,
      corrected_normalized_value: 4800,
      corrected_units: "square_feet",
      reason: "resolve",
      accepted_history_fingerprint: fp(doc, AREA),
    });
    await client.rejectFact({ documentDigest: DIGEST_PRO, evidenceId: NORTH, reason: "AI guess unusable" });
    const out = await client.confirmDocument({ documentDigest: DIGEST_PRO });
    expect(out.kind).toBe("error");
    if (out.kind !== "error") return;
    expect(out.reject_code).toBe("confirmation_rejected");
    expect(out.rejectedFactIds).toContain(NORTH);
  });

  it("refuses a fact edit on a confirmed document (post_confirmation_edit_refused), and reopen recovers it", async () => {
    const client = createMockSurveyReviewClient(seedStore());
    for (const eid of [AREA, NORTH]) {
      const doc = await read(client, DIGEST_PRO);
      await client.correctFact({
        documentDigest: DIGEST_PRO,
        evidenceId: eid,
        corrected_normalized_value: 4800,
        corrected_units: "square_feet",
        reason: "resolve",
        accepted_history_fingerprint: fp(doc, eid),
      });
    }
    await client.confirmDocument({ documentDigest: DIGEST_PRO });
    const confirmed = await read(client, DIGEST_PRO);
    const refused = await client.correctFact({
      documentDigest: DIGEST_PRO,
      evidenceId: CLEAN,
      corrected_normalized_value: 130,
      corrected_units: "feet",
      reason: "late edit",
      accepted_history_fingerprint: fp(confirmed, CLEAN),
    });
    expect(refused.kind).toBe("error");
    if (refused.kind === "error") expect(refused.reject_code).toBe("post_confirmation_edit_refused");

    const reopened = await client.reopenDocument({ documentDigest: DIGEST_PRO, reason: "boundary contradiction found" });
    expect(reopened.kind).toBe("updated");
    if (reopened.kind === "updated") expect(reopened.document.state).toBe("needs_review");
  });
});

describe("survey-review client — authorization (SC-S3)", () => {
  it("refuses reject_fact for a preparer (professional-only in the shipped slice)", async () => {
    const out = await createMockSurveyReviewClient().rejectFact({
      documentDigest: DIGEST_USER,
      evidenceId: NORTH,
      reason: "not usable",
    });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("unauthorized_review_action");
  });

  it("refuses document confirmation for a preparer (unauthorized_transition_actor)", async () => {
    const out = await createMockSurveyReviewClient().confirmDocument({ documentDigest: DIGEST_USER });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("unauthorized_transition_actor");
  });
});

describe("boundedEvidenceId — rejected_fact_ids must survive sanitization", () => {
  // Regression: `boundedToken` strips `:`, so a colon-delimited evidence id came
  // back as `sevdocp13` and no longer matched any `fact.evidence_id` — the UI
  // could not point the reviewer at the facts that blocked confirmation.
  const SANITIZER_CASES: ReadonlyArray<[string, unknown, string | null]> = [
    ["keeps a colon-delimited evidence id intact", "sev:doc:p1:3", "sev:doc:p1:3"],
    ["keeps the dot/underscore/hyphen charset", "sev:doc-a.b_c:9", "sev:doc-a.b_c:9"],
    ["strips markup rather than passing it through", "sev:doc<script>:1", "sev:docscript:1"],
    ["strips whitespace", "sev :doc\tp1", "sev:docp1"],
    ["returns null for a value that sanitizes to empty", "<<<>>>", null],
    ["returns null for an empty string", "", null],
    ["returns null for a non-string", 42, null],
    ["returns null for null", null, null],
  ];

  it.each(SANITIZER_CASES)("%s", (_label, input, expected) => {
    expect(boundedEvidenceId(input)).toBe(expected);
  });

  it("bounds the length", () => {
    expect(boundedEvidenceId("a".repeat(500))?.length).toBe(128);
  });

  it("drops unsanitizable entries from rejectedFactIds instead of emitting them raw", async () => {
    const client = createMockSurveyReviewClient(seedStore());
    const doc = await read(client, DIGEST_PRO);
    await client.correctFact({
      documentDigest: DIGEST_PRO,
      evidenceId: AREA,
      corrected_normalized_value: 4800,
      corrected_units: "square_feet",
      reason: "resolve",
      accepted_history_fingerprint: fp(doc, AREA),
    });
    await client.rejectFact({ documentDigest: DIGEST_PRO, evidenceId: NORTH, reason: "AI guess unusable" });
    const out = await client.confirmDocument({ documentDigest: DIGEST_PRO });
    expect(out.kind).toBe("error");
    if (out.kind !== "error") return;
    // The real id round-trips, and every emitted entry is a sanitized string.
    expect(out.rejectedFactIds).toContain(NORTH);
    for (const id of out.rejectedFactIds ?? []) {
      expect(boundedEvidenceId(id)).toBe(id);
    }
  });
});
