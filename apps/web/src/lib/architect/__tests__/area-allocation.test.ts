import { describe, expect, it } from "vitest";
import {
  AREA_REASON_FITTED_UNKNOWN,
  AREA_REASON_INCOMPLETE,
  AREA_REASON_MISSING,
  AREA_REASON_NOT_PLACED,
  AREA_REASON_SHARE_MISMATCH,
  AREA_REASON_SHARE_NOT_NUMBER,
  AREA_REASON_SHARE_OUT_OF_RANGE,
  AREA_REASON_SPLIT_NOT_NUMBERS,
  AREA_REASON_TOTAL_MISMATCH,
  areaAllocationView,
} from "@/lib/architect/area-allocation";

/**
 * M5-T187 — the area-allocation selector's input-state table. One test per input state (the table is
 * in the producer report). Every block is a small inline literal (no shared fixture folder exists);
 * the values mirror the accepted 1.5.0 fixtures (synthetic_rear_yard: share 0.65, 12025/6475/18500;
 * synthetic_placed_building: share 0.70, 13300/5700/19000, fitted). The reasons are asserted against
 * the exported constants so they stay byte-equal to the PDF kernel's Unavailable text.
 */

const CONVERSION =
  "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked";

/** A sound NOT-fitted block at the given share, with areas that reconcile with the share and total. */
function barBlock(share: number, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  const total = 18500;
  const apartment = Math.round(share * total * 100) / 100;
  return {
    label: "Illustrative",
    share,
    measure: "residential_floor_area",
    conversion_statement: CONVERSION,
    apartment_area_sqft: apartment,
    other_area_sqft: total - apartment,
    total_sqft: total,
    fitted: false,
    ...overrides,
  };
}

/** A sound FITTED block (the placed-building fixture's values). */
function fittedBlock(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    label: "Illustrative",
    share: 0.7,
    measure: "residential_floor_area",
    conversion_statement: CONVERSION,
    apartment_area_sqft: 13300,
    other_area_sqft: 5700,
    total_sqft: 19000,
    fitted: true,
    ...overrides,
  };
}

const PLACED_PLACEMENT = {
  status: "placed",
  outline: [
    [
      [0, 0],
      [82, 0],
      [82, 82],
      [0, 82],
      [0, 0],
    ],
  ],
};

describe("areaAllocationView — the input-state table", () => {
  it("not fitted -> a proportional bar with the block's own percentage and fraction", () => {
    const view = areaAllocationView(barBlock(0.65));
    expect(view).toEqual({
      kind: "bar",
      percent: 65,
      apartmentFraction: 0.65,
      conversionStatement: CONVERSION,
    });
  });

  it("share 0.60 -> bar, percent 60 (the percentage is read from share, never hardcoded)", () => {
    const view = areaAllocationView(barBlock(0.6));
    expect(view.kind).toBe("bar");
    if (view.kind === "bar") {
      expect(view.percent).toBe(60);
      expect(view.apartmentFraction).toBe(0.6);
    }
  });

  it("share 0.65 -> bar, percent 65", () => {
    const view = areaAllocationView(barBlock(0.65));
    expect(view.kind === "bar" && view.percent).toBe(65);
  });

  it("share 0.75 -> bar, percent 75", () => {
    const view = areaAllocationView(barBlock(0.75));
    expect(view.kind === "bar" && view.percent).toBe(75);
  });

  it("share above the range (0.80) -> unavailable, out-of-range reason", () => {
    const view = areaAllocationView(barBlock(0.65, { share: 0.8, apartment_area_sqft: 14800, other_area_sqft: 3700 }));
    expect(view).toEqual({ kind: "unavailable", reason: AREA_REASON_SHARE_OUT_OF_RANGE });
  });

  it("share below the range (0.50) -> unavailable, out-of-range reason", () => {
    const view = areaAllocationView(barBlock(0.65, { share: 0.5, apartment_area_sqft: 9250, other_area_sqft: 9250 }));
    expect(view).toEqual({ kind: "unavailable", reason: AREA_REASON_SHARE_OUT_OF_RANGE });
  });

  it("inconsistent split: apartment + other != total -> unavailable, total-mismatch reason", () => {
    const view = areaAllocationView(barBlock(0.65, { other_area_sqft: 6000 }));
    expect(view).toEqual({ kind: "unavailable", reason: AREA_REASON_TOTAL_MISMATCH });
  });

  it("inconsistent split: apartment / total != share -> unavailable, share-mismatch reason", () => {
    // total and the addends reconcile, but the apartment share is 0.70, not the stated 0.65.
    const view = areaAllocationView(
      barBlock(0.65, { apartment_area_sqft: 12950, other_area_sqft: 5550 }),
    );
    expect(view).toEqual({ kind: "unavailable", reason: AREA_REASON_SHARE_MISMATCH });
  });

  it("a missing block (not an object) -> unavailable, missing reason", () => {
    for (const bad of [undefined, null, 42, "x", []]) {
      expect(areaAllocationView(bad)).toEqual({ kind: "unavailable", reason: AREA_REASON_MISSING });
    }
  });

  it("a garbled block (wrong fixed label / measure / conversion) -> unavailable, incomplete reason", () => {
    expect(areaAllocationView(barBlock(0.65, { label: "Verified" }))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_INCOMPLETE,
    });
    expect(areaAllocationView(barBlock(0.65, { measure: "gross_floor_area" }))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_INCOMPLETE,
    });
    expect(areaAllocationView(barBlock(0.65, { conversion_statement: "something else" }))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_INCOMPLETE,
    });
  });

  it("a non-numeric share -> unavailable, share-not-a-number reason", () => {
    expect(areaAllocationView(barBlock(0.65, { share: "0.65" }))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_SHARE_NOT_NUMBER,
    });
    expect(areaAllocationView(barBlock(0.65, { share: Number.NaN }))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_SHARE_NOT_NUMBER,
    });
  });

  it("a non-numeric area split -> unavailable, split-not-numbers reason", () => {
    expect(areaAllocationView(barBlock(0.65, { apartment_area_sqft: null }))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_SPLIT_NOT_NUMBERS,
    });
  });

  it("an unstated fitted flag -> unavailable, fitted-unknown reason", () => {
    expect(areaAllocationView(barBlock(0.65, { fitted: "true" }))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_FITTED_UNKNOWN,
    });
  });

  it("fitted WITH a placed outline -> fitted_deferred (zones drawn in Part B)", () => {
    expect(areaAllocationView(fittedBlock(), PLACED_PLACEMENT)).toEqual({ kind: "fitted_deferred" });
  });

  it("fitted WITHOUT an outline -> unavailable, not-placed reason (never a bar mislabelled fitted)", () => {
    expect(areaAllocationView(fittedBlock())).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_NOT_PLACED,
    });
    expect(areaAllocationView(fittedBlock(), { status: "withheld" })).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_NOT_PLACED,
    });
  });
});
