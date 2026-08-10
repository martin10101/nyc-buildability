import { describe, expect, it } from "vitest";
import { createHttpSurveyReviewClient } from "@/lib/surveyReview/api";
import { createMockSurveyReviewClient, seedStore } from "@/test-support/survey-review/mockClient";

/**
 * Client + reducer contract tests (task M2-T016). Exercises the REAL client
 * decode path against the stateful mock backend, covering the review-action
 * matrix (workflow §12): read, correct (append-only + H5 clearing + stale +
 * no-op), reject, confirm (H5 gate), and the authorization refusals.
 */

const AREA_FACT = "sev:doc:p1:2";
const CLEAN_FACT = "sev:doc:p1:1";

describe("survey-review client — reads", () => {
  it("reads a document by id", async () => {
    const out = await createMockSurveyReviewClient().readDocument("doc-pro");
    expect(out.kind).toBe("document");
  });

  it("returns not_found for an unknown id", async () => {
    const out = await createMockSurveyReviewClient().readDocument("nope");
    expect(out.kind).toBe("not_found");
  });

  it("returns validation_failure for a 200 that fails the read-model contract", async () => {
    const client = createHttpSurveyReviewClient();
    const out = await client.readDocument("x", {
      fetchImpl: async () =>
        new Response(JSON.stringify({ document_id: "x" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    });
    expect(out.kind).toBe("validation_failure");
  });
});

describe("survey-review client — corrections (SC-S1/S2/S5/S6)", () => {
  it("appends a correction, preserves the immutable original, clears the conflict + downstream", async () => {
    const store = seedStore();
    const client = createMockSurveyReviewClient(store);
    const out = await client.correctFact({
      documentId: "doc-pro",
      evidenceId: AREA_FACT,
      corrected_normalized_value: 4800,
      corrected_units: "square_feet",
      reason: "OCR misread the stated area against the boundary calculation.",
      accepted_history_fingerprint: "hist-0",
    });
    expect(out.kind).toBe("updated");
    if (out.kind !== "updated") return;
    const fact = out.document.facts.find((f) => f.fact.evidence_id === AREA_FACT)!;
    expect(fact.fact.correction_history).toHaveLength(1);
    expect(fact.fact.original_value).toBe("5,000 SF"); // immutable
    expect(fact.promotion.allowed).toBe(true);
    expect(out.document.downstream.every((c) => c.status === "cleared")).toBe(true);
  });

  it("refuses a stale correction and returns the current document", async () => {
    const out = await createMockSurveyReviewClient().correctFact({
      documentId: "doc-pro",
      evidenceId: AREA_FACT,
      corrected_normalized_value: 4800,
      corrected_units: "square_feet",
      reason: "fix",
      accepted_history_fingerprint: "hist-STALE",
    });
    expect(out.kind).toBe("error");
    if (out.kind !== "error") return;
    expect(out.reject_code).toBe("stale_history");
    expect(out.currentDocument).toBeDefined();
  });

  it("refuses a no-op correction", async () => {
    const out = await createMockSurveyReviewClient().correctFact({
      documentId: "doc-pro",
      evidenceId: AREA_FACT,
      corrected_normalized_value: 5000,
      corrected_units: "square_feet",
      reason: "unchanged",
      accepted_history_fingerprint: "hist-0",
    });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("correction_no_op");
  });
});

describe("survey-review client — confirmation gate (SC-S4)", () => {
  it("refuses confirmation while a material fact still fails (promotion_gate_unmet)", async () => {
    const out = await createMockSurveyReviewClient().confirmDocument({ documentId: "doc-pro" });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("promotion_gate_unmet");
  });

  it("confirms only after the conflict is resolved, and marks material facts confirmed", async () => {
    const store = seedStore();
    const client = createMockSurveyReviewClient(store);
    await client.correctFact({
      documentId: "doc-pro",
      evidenceId: AREA_FACT,
      corrected_normalized_value: 4800,
      corrected_units: "square_feet",
      reason: "resolve conflict",
      accepted_history_fingerprint: "hist-0",
    });
    const out = await client.confirmDocument({ documentId: "doc-pro" });
    expect(out.kind).toBe("updated");
    if (out.kind !== "updated") return;
    expect(out.document.state).toBe("professionally_confirmed");
    const clean = out.document.facts.find((f) => f.fact.evidence_id === CLEAN_FACT)!;
    expect(clean.fact.professional_confirmation.state).toBe("confirmed");
  });
});

describe("survey-review client — authorization (SC-S3)", () => {
  it("refuses accept for a read-only consumer principal", async () => {
    const out = await createMockSurveyReviewClient().acceptFact({
      documentId: "doc-consumer",
      evidenceId: CLEAN_FACT,
    });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("unauthorized");
  });

  it("refuses document confirmation for a preparer (non-professional) principal", async () => {
    const out = await createMockSurveyReviewClient().confirmDocument({ documentId: "doc-user" });
    expect(out.kind).toBe("error");
    if (out.kind === "error") expect(out.reject_code).toBe("unauthorized_transition_actor");
  });

  it("rejects a fact detection and records the professional confirmation state", async () => {
    const store = seedStore();
    const client = createMockSurveyReviewClient(store);
    const out = await client.rejectFact({
      documentId: "doc-pro",
      evidenceId: "sev:doc:p1:3",
      reason: "AI north-arrow guess is not usable.",
    });
    expect(out.kind).toBe("updated");
    if (out.kind !== "updated") return;
    const fact = out.document.facts.find((f) => f.fact.evidence_id === "sev:doc:p1:3")!;
    expect(fact.fact.professional_confirmation.state).toBe("rejected");
  });
});
