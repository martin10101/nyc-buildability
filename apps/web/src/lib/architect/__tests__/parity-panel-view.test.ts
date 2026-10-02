import { describe, expect, it } from "vitest";
import realDof from "../../../../../../packages/contracts/fixtures/valid/parity_data/real_dof_bayside.json";
import synthetic from "../../../../../../packages/contracts/fixtures/valid/parity_data/synthetic_subject.json";
import {
  NOT_A_VALUATION_NOTICE,
  NOT_CONFIRMED_LABEL,
  NOT_CONFIRMED_REASON,
  type ParityData,
} from "@/lib/parity-api";
import {
  EXCLUDED_REASON_TEXT,
  comparableSalesView,
  formatRecordedPrice,
  parityStripSummary,
  unusedFloorAreaView,
} from "@/lib/architect/parity-panel-view";

/**
 * Pure view-model for the parity panel (queue D-15, plan §11b, B-11). Proves:
 * recorded sale price/date surfaced verbatim (never derived); the disclosed filter
 * and the not-a-valuation notice carried verbatim; the exclusion reason mapped to
 * plain words (no raw token); the unused-floor-area block is the owner-settled
 * wording with NO digit; the one §5a status strip holds at most three items.
 */

// Deep-clone so a test can never mutate the shared fixture module.
function bayside(): ParityData {
  return JSON.parse(JSON.stringify(realDof)) as ParityData;
}
function synth(): ParityData {
  return JSON.parse(JSON.stringify(synthetic)) as ParityData;
}

describe("comparableSalesView — recorded sales surfaced verbatim, nothing derived", () => {
  it("carries each recorded sale's price and date exactly as recorded", () => {
    const view = comparableSalesView(bayside());
    expect(view.selected).toHaveLength(4);
    const first = view.selected[0];
    expect(first.address).toBe("45-30 BELL BOULEVARD");
    expect(first.recordedPrice).toBe("$3,700,000"); // 3700000 comma-grouped, not computed
    expect(first.saleDate).toBe("2025-11-20");
  });

  it("surfaces the disclosed filter and the not-a-valuation notice verbatim", () => {
    const data = bayside();
    const view = comparableSalesView(data);
    expect(view.criteriaText).toBe(data.comparable_sales.criteria_text);
    expect(view.notAValuation).toBe(NOT_A_VALUATION_NOTICE);
  });

  it("maps every exclusion reason to plain words, never the raw token", () => {
    const view = comparableSalesView(synth());
    expect(view.excluded).toHaveLength(2);
    expect(view.excluded[0].reasonText).toBe(EXCLUDED_REASON_TEXT.subject_lot);
    for (const row of view.excluded) {
      expect(row.reasonText).not.toContain("_");
    }
  });

  it("carries the DOF provenance for the Source disclosure", () => {
    const view = comparableSalesView(bayside());
    expect(view.source).not.toBeNull();
    expect(view.source?.dataset).toContain("DOF");
    expect(view.source?.requestUrl).toContain("://");
  });
});

describe("formatRecordedPrice — display formatting of a recorded fact, not a computation", () => {
  it("comma-groups the publisher's recorded integer", () => {
    expect(formatRecordedPrice(3700000)).toBe("$3,700,000");
    expect(formatRecordedPrice(0)).toBe("$0");
  });
  it("returns null when no price is recorded", () => {
    expect(formatRecordedPrice(null)).toBeNull();
  });
});

describe("unusedFloorAreaView — owner-settled wording only, never a number", () => {
  it("is exactly the settled label and reason, with no digit", () => {
    const view = unusedFloorAreaView(bayside());
    expect(view.label).toBe(NOT_CONFIRMED_LABEL);
    expect(view.reason).toBe(NOT_CONFIRMED_REASON);
    expect(/[0-9]/.test(`${view.label} ${view.reason}`)).toBe(false);
  });
});

describe("parityStripSummary — one §5a strip, at most three items", () => {
  it("summarizes recorded-sale and excluded counts plus the capacity status", () => {
    const summary = parityStripSummary(bayside());
    expect(summary.items.length).toBeLessThanOrEqual(3);
    expect(summary.items[0]).toBe("4 recorded sales");
    expect(summary.items).toContain("Remaining capacity: Not confirmed");
    expect(summary.items).toContain("8 not included");
  });

  it("singularizes a single recorded sale", () => {
    expect(parityStripSummary(synth()).items[0]).toBe("1 recorded sale");
  });
});
