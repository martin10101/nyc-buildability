import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  type AreaPoint,
  AREA_REASON_FITTED_UNKNOWN,
  AREA_REASON_INCOMPLETE,
  AREA_REASON_MISSING,
  AREA_REASON_NOT_PLACED,
  AREA_REASON_OUTLINE_NO_AREA,
  AREA_REASON_OUTLINE_NOT_POINTS,
  AREA_REASON_OUTLINE_OUT_OF_RANGE,
  AREA_REASON_OUTLINE_TOO_MANY_POINTS,
  AREA_REASON_SHARE_MISMATCH,
  AREA_REASON_SHARE_NOT_NUMBER,
  AREA_REASON_SHARE_OUT_OF_RANGE,
  AREA_REASON_SPLIT_NOT_NUMBERS,
  AREA_REASON_TOTAL_MISMATCH,
  areaAllocationView,
  polyArea,
} from "@/lib/architect/area-allocation";

/**
 * M5-T187 + M5-T202 part B2a — the area-allocation selector's input-state table and the
 * fitted two-zone geometry. One test per input state. Every block is a small inline literal
 * (values mirror the accepted 1.5.0 fixtures) except S1, which reads the benchmark fixture
 * and the kit-authored golden from disk so the TypeScript split is pinned to the PDF kernel's.
 * The reasons are asserted against the exported constants so they stay byte-equal to the
 * kernel's Unavailable text.
 */

const CONVERSION =
  "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked";

/** Repo root is two levels above the vitest cwd (apps/web). */
function repoFile(relative: string): string {
  return readFileSync(resolve(process.cwd(), "../..", relative), "utf8");
}

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

/** A placement placed with the given exterior ring. */
function placed(ring: unknown): Record<string, unknown> {
  return { status: "placed", outline: [ring] };
}

const SQUARE_82 = [
  [0, 0],
  [82, 0],
  [82, 82],
  [0, 82],
  [0, 0],
];

describe("areaAllocationView — the input-state table (unfitted / garbled)", () => {
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
});

// ---- S1: the fitted split equals the PDF kernel's (golden from the kit code) ----

describe("S1 — the fitted two-zone split equals the kernel's (golden from kit/area_allocation.py)", () => {
  it("the benchmark (0.6; 100.76 x 66.66) splits at the kernel's division x and fraction, within 1e-6", () => {
    const golden = JSON.parse(repoFile("apps/web/src/test-support/report-parity-area-zones.json"));
    const doc = JSON.parse(
      repoFile("packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json"),
    );
    const alt = doc.building_alternatives[0];
    const view = areaAllocationView(alt.area_allocation, alt.placement);

    expect(view.kind).toBe("fitted_zones");
    if (view.kind !== "fitted_zones") return;

    // one division; apartment/footprint area 0.6 within 1e-6; division x and fraction equal the kernel's.
    expect(Math.abs(view.apartmentFraction - golden.benchmark.apartment_fraction)).toBeLessThanOrEqual(1e-6);
    expect(Math.abs(view.apartmentFraction - 0.6)).toBeLessThanOrEqual(1e-6);
    expect(Math.abs(view.divisionX - golden.benchmark.division_x)).toBeLessThanOrEqual(1e-6);
    expect(Math.abs(polyArea(view.ring) - golden.benchmark.footprint_area)).toBeLessThanOrEqual(1e-6);
    expect(view.percent).toBe(60);
  });

  it("an 82 x 82 placed square at share 0.70 cuts at 0.70 of the width and 0.70 of the area", () => {
    const view = areaAllocationView(fittedBlock(), placed(SQUARE_82));
    expect(view.kind).toBe("fitted_zones");
    if (view.kind !== "fitted_zones") return;
    expect(Math.abs(view.divisionX - 0.7 * 82)).toBeLessThanOrEqual(1e-6);
    expect(Math.abs(view.apartmentFraction - 0.7)).toBeLessThanOrEqual(1e-6);
    // the apartment and other polygons reconstitute the whole footprint.
    const whole = polyArea(view.ring);
    const parts = polyArea(view.apartmentPolygon) + polyArea(view.otherPolygon);
    expect(Math.abs(parts - whole)).toBeLessThanOrEqual(1e-6);
  });
});

// ---- S2: a fitted block with no (or an un-drawable) outline fails closed, one test per state ----

describe("S2 — fitted with no / un-drawable outline fails closed to the kernel's reason", () => {
  it("fitted WITHOUT any placed outline -> not-placed reason (never a bar mislabelled fitted)", () => {
    expect(areaAllocationView(fittedBlock())).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_NOT_PLACED,
    });
  });

  it("fitted with a withheld placement -> not-placed reason", () => {
    expect(areaAllocationView(fittedBlock(), { status: "withheld" })).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_NOT_PLACED,
    });
  });

  it("fitted with fewer than three distinct vertices -> not-placed reason", () => {
    expect(
      areaAllocationView(fittedBlock(), placed([[0, 0], [82, 0], [0, 0]])),
    ).toEqual({ kind: "unavailable", reason: AREA_REASON_NOT_PLACED });
  });

  it("a footprint above the 1000-vertex cap -> too-many-points reason", () => {
    const ring: number[][] = [];
    for (let i = 0; i < 1001; i += 1) {
      const a = (2 * Math.PI * i) / 1001;
      ring.push([50 + 40 * Math.cos(a), 50 + 40 * Math.sin(a)]);
    }
    expect(areaAllocationView(fittedBlock(), placed(ring))).toEqual({
      kind: "unavailable",
      reason: AREA_REASON_OUTLINE_TOO_MANY_POINTS,
    });
  });

  it("a vertex that is not a two-number point -> not-given-as-points reason", () => {
    expect(
      areaAllocationView(fittedBlock(), placed([[0, 0], [82, 0], [82], [0, 82]])),
    ).toEqual({ kind: "unavailable", reason: AREA_REASON_OUTLINE_NOT_POINTS });
  });

  it("a NaN / infinite / over-large coordinate -> out-of-range reason (one test per bad value)", () => {
    for (const bad of [Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY, 1e308]) {
      expect(
        areaAllocationView(fittedBlock(), placed([[0, 0], [82, 0], [82, bad], [0, 82], [0, 0]])),
      ).toEqual({ kind: "unavailable", reason: AREA_REASON_OUTLINE_OUT_OF_RANGE });
    }
  });

  it("a zero-area collinear ring -> no-area reason (no division by zero)", () => {
    expect(
      areaAllocationView(fittedBlock(), placed([[0, 0], [40, 0], [80, 0], [0, 0]])),
    ).toEqual({ kind: "unavailable", reason: AREA_REASON_OUTLINE_NO_AREA });
  });

  it("a zero-width vertical spike -> no-area reason", () => {
    expect(
      areaAllocationView(fittedBlock(), placed([[10, 0], [10, 40], [10, 80], [10, 0]])),
    ).toEqual({ kind: "unavailable", reason: AREA_REASON_OUTLINE_NO_AREA });
  });
});

// ---- the geometry port is self-consistent (supports S1) ----

describe("the ported geometry", () => {
  it("polyArea is the shoelace area of a rectangle", () => {
    const rect: AreaPoint[] = [
      [0, 0],
      [100.76, 0],
      [100.76, 66.66],
      [0, 66.66],
    ];
    expect(Math.abs(polyArea(rect) - 100.76 * 66.66)).toBeLessThanOrEqual(1e-6);
  });
});
