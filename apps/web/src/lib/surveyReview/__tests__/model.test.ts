import { describe, expect, it } from "vitest";
import {
  canOfferConfirm,
  coerceToSampleType,
  dominantAction,
  factResolution,
  factsBlockingConfirmation,
  isOpenItem,
  openItemCount,
  orderFactsByUrgency,
} from "@/lib/surveyReview/model";
import { validateReviewView } from "@/lib/surveyReview/validate";
import type { FactView, ReviewDocument } from "@/lib/surveyReview/types";

function fact(overrides: Partial<FactView>): FactView {
  return {
    evidence_id: "e",
    fact_type: "stated_lot_area",
    original_value: "5,000 SF",
    baseline_normalized_value: 5000,
    baseline_units: "square_feet",
    normalized_value: 5000,
    units: "square_feet",
    confirmation_state: "unconfirmed",
    confirmation_note: null,
    correction_history: [],
    correction_count: 0,
    check_pass: 1,
    check_fail: 0,
    check_unresolved: 0,
    location: null,
    page_number: 1,
    extraction_method: "ocr_text",
    is_unconfirmed_evidence: true,
    promotable: true,
    downstream_impact: null,
    display_label: "Stated lot area",
    ai_drafted_label: false,
    accepted_history_fingerprint: "sha256:x",
    ...overrides,
  };
}

function doc(overrides: Partial<ReviewDocument>): ReviewDocument {
  return {
    document_digest: "sha256:abc",
    target_bbl: "1000010010",
    state: "needs_review",
    state_history: [],
    facts: [],
    confirm_precondition_met: false,
    blocking_fact_ids: [],
    original_available: true,
    correlation_id: null,
    title: "t",
    pages: [],
    principal: {
      principal_id: "p",
      role: "qualified_professional",
      display_name: "Pro",
      capabilities: {
        can_view: true,
        can_accept_fact: true,
        can_correct_fact: true,
        can_reject_fact: true,
        can_confirm_document: true,
        can_reject_document: true,
        can_reopen_document: true,
      },
      capabilities_known: true,
    },
    extraction_available: true,
    ...overrides,
  };
}

describe("survey-review model derivations", () => {
  it("classifies fact resolution from check counts and confirmation", () => {
    expect(factResolution(fact({ check_fail: 1 }))).toBe("conflict");
    expect(factResolution(fact({ check_fail: 0, check_unresolved: 1, check_pass: 0 }))).toBe("unresolved");
    expect(factResolution(fact({ confirmation_state: "rejected", check_pass: 0 }))).toBe("rejected");
    expect(factResolution(fact({ confirmation_state: "confirmed" }))).toBe("confirmed");
    expect(factResolution(fact({}))).toBe("unconfirmed");
  });

  it("orders facts conflict → unresolved → unconfirmed → resolved", () => {
    const facts = [
      fact({ evidence_id: "clean" }),
      fact({ evidence_id: "conflict", check_fail: 1, check_pass: 0 }),
      fact({ evidence_id: "unresolved", check_unresolved: 1, check_pass: 0 }),
    ];
    expect(orderFactsByUrgency(facts).map((f) => f.evidence_id)).toEqual([
      "conflict",
      "unresolved",
      "clean",
    ]);
  });

  it("F1: a clean-but-unconfirmed fact is NOT an open item (only its confirmation remains)", () => {
    expect(isOpenItem(fact({ promotable: true, check_fail: 0, check_unresolved: 0 }))).toBe(false);
    expect(isOpenItem(fact({ check_fail: 1 }))).toBe(true);
    expect(isOpenItem(fact({ check_unresolved: 1 }))).toBe(true);
  });

  it("F1: dominant action flips to Confirm once all facts are resolved", () => {
    const openDoc = doc({
      facts: [fact({ evidence_id: "c", check_fail: 1, check_pass: 0 })],
      blocking_fact_ids: ["c"],
      confirm_precondition_met: false,
    });
    expect(openItemCount(openDoc)).toBe(1);
    expect(dominantAction(openDoc)).toMatch(/resolve 1 open item/);

    const readyDoc = doc({
      facts: [fact({ evidence_id: "a" }), fact({ evidence_id: "b" })],
      blocking_fact_ids: [],
      confirm_precondition_met: true,
    });
    expect(openItemCount(readyDoc)).toBe(0);
    expect(canOfferConfirm(readyDoc)).toBe(true);
    expect(dominantAction(readyDoc)).toMatch(/confirm or reject the document/i);
  });

  it("consumes the backend confirm precondition + blocking ids (never computed)", () => {
    const d = doc({
      facts: [fact({ evidence_id: "a" }), fact({ evidence_id: "b", check_fail: 1, check_pass: 0 })],
      blocking_fact_ids: ["b"],
      confirm_precondition_met: false,
    });
    expect(canOfferConfirm(d)).toBe(false);
    expect(factsBlockingConfirmation(d).map((f) => f.evidence_id)).toEqual(["b"]);
  });

  it("never offers confirm to a role without the confirm capability", () => {
    const d = doc({ confirm_precondition_met: true });
    d.principal.capabilities.can_confirm_document = false;
    expect(canOfferConfirm(d)).toBe(false);
  });

  it("F5: coerces a correction input to the fact's numeric type", () => {
    expect(coerceToSampleType("4800", 5000)).toBe(4800);
    expect(coerceToSampleType("not-a-number", 5000)).toBe("not-a-number");
    expect(coerceToSampleType("4800", "5,000 SF")).toBe("4800");
  });
});

describe("survey-review read-model validation", () => {
  it("accepts a well-formed DocumentReviewView", () => {
    const body = {
      document_digest: "sha256:abc",
      target_bbl: "1000010010",
      state: "needs_review",
      state_history: [],
      facts: [
        {
          evidence_id: "e",
          confirmation_state: "unconfirmed",
          promotable: true,
          correction_history: [],
          check_pass: 1,
          check_fail: 0,
          check_unresolved: 0,
        },
      ],
      confirm_precondition_met: true,
      blocking_fact_ids: [],
    };
    expect(validateReviewView(body).ok).toBe(true);
  });

  it("rejects an undocumented document state", () => {
    const result = validateReviewView({
      document_digest: "x",
      state: "verified",
      target_bbl: "b",
      state_history: [],
      facts: [],
      confirm_precondition_met: true,
      blocking_fact_ids: [],
    });
    expect(result.ok).toBe(false);
    expect(result.problems.join(" ")).toMatch(/state/);
  });

  it("rejects a fact with an undocumented confirmation state", () => {
    const result = validateReviewView({
      document_digest: "x",
      state: "needs_review",
      target_bbl: "b",
      state_history: [],
      confirm_precondition_met: true,
      blocking_fact_ids: [],
      facts: [
        { evidence_id: "e", confirmation_state: "verified", promotable: true, correction_history: [], check_pass: 0, check_fail: 0, check_unresolved: 0 },
      ],
    });
    expect(result.ok).toBe(false);
    expect(result.problems.join(" ")).toMatch(/confirmation_state/);
  });
});
