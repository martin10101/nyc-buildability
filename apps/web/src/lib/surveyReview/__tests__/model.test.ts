import { describe, expect, it } from "vitest";
import {
  blockedOrProvisional,
  canOfferConfirm,
  factResolution,
  factsBlockingConfirmation,
  isOpenItem,
  openItemCount,
  orderFactsByUrgency,
} from "@/lib/surveyReview/model";
import { validateReviewDocument } from "@/lib/surveyReview/validate";
import { reviewDocument } from "@/test-support/survey-review/fixtures";

describe("survey-review model derivations", () => {
  it("orders facts by decision urgency (conflict first, resolved last)", () => {
    const doc = reviewDocument();
    const ordered = orderFactsByUrgency(doc.facts);
    expect(ordered[0].fact.evidence_id).toBe("sev:doc:p1:2"); // the area conflict
  });

  it("classifies fact resolution from checks and confirmation state", () => {
    const doc = reviewDocument();
    const byId = Object.fromEntries(doc.facts.map((f) => [f.fact.evidence_id, f]));
    expect(factResolution(byId["sev:doc:p1:2"])).toBe("conflict");
    expect(factResolution(byId["sev:doc:p1:3"])).toBe("unresolved");
    expect(factResolution(byId["sev:doc:p1:1"])).toBe("unconfirmed");
  });

  it("counts only material open items", () => {
    // fact1 (unconfirmed, material) + fact2 (conflict, material); fact3 is non-material
    expect(openItemCount(reviewDocument())).toBe(2);
  });

  it("does NOT offer confirm while a material fact is in conflict (H5 mirror)", () => {
    const doc = reviewDocument("professional");
    expect(canOfferConfirm(doc)).toBe(false);
    expect(factsBlockingConfirmation(doc).map((f) => f.fact.evidence_id)).toContain(
      "sev:doc:p1:2",
    );
  });

  it("never offers confirm to a role without the confirm capability", () => {
    const doc = reviewDocument("preparer");
    doc.facts.forEach((f) => (f.promotion = { evidence_id: f.fact.evidence_id, allowed: true, refusal_reasons: [] }));
    // Even with all promotion verdicts allowed, the preparer cannot confirm.
    expect(canOfferConfirm(doc)).toBe(false);
  });

  it("surfaces the blocked and provisional downstream conclusions", () => {
    const open = blockedOrProvisional(reviewDocument());
    expect(open.map((c) => c.conclusion_id).sort()).toEqual(["far_max", "lot_coverage"]);
  });

  it("marks unconfirmed/conflict/unresolved facts as open items", () => {
    const doc = reviewDocument();
    const byId = Object.fromEntries(doc.facts.map((f) => [f.fact.evidence_id, f]));
    expect(isOpenItem(byId["sev:doc:p1:1"])).toBe(true);
    expect(isOpenItem(byId["sev:doc:p1:2"])).toBe(true);
  });
});

describe("survey-review read-model validation", () => {
  it("accepts a well-formed document", () => {
    expect(validateReviewDocument(reviewDocument()).ok).toBe(true);
  });

  it("rejects an undocumented document state (nothing renders from it)", () => {
    const bad = reviewDocument() as unknown as Record<string, unknown>;
    bad.state = "verified";
    const result = validateReviewDocument(bad);
    expect(result.ok).toBe(false);
    expect(result.problems.join(" ")).toMatch(/state/);
  });

  it("rejects a fact missing its professional_confirmation state", () => {
    const bad = reviewDocument();
    delete (bad.facts[0].fact as unknown as Record<string, unknown>).professional_confirmation;
    const result = validateReviewDocument(bad);
    expect(result.ok).toBe(false);
    expect(result.problems.join(" ")).toMatch(/professional_confirmation/);
  });

  it("rejects a non-object body", () => {
    expect(validateReviewDocument(null).ok).toBe(false);
    expect(validateReviewDocument("nope").ok).toBe(false);
  });
});
