import { describe, expect, it } from "vitest";
import { METRIC_NOT_KNOWN, formatMetric } from "@/lib/architect/metric-format";
import type { Unit } from "@/lib/architect/three-answers";

/**
 * M5-T148 part B scenario S4: a document value and unit formatted for reading. Zero is "0 sq ft",
 * never "Not known"; null/undefined give the not-known state and never a number; an unknown unit
 * gives the bare number; the data is never changed.
 */

describe("formatMetric (scenario S4)", () => {
  it("groups a whole square-foot value with its unit", () => {
    const metric = formatMetric(20150, "square_feet");
    expect(metric.kind).toBe("value");
    expect(metric.text).toBe("20,150 sq ft");
  });

  // Mutation proof target: turning `value == null` into a truthiness test (`!value`) makes 0 read
  // "Not known"; this test fails when that happens, so 0 can never become not-known.
  it("formats exactly 0 as '0 sq ft', never 'Not known'", () => {
    const metric = formatMetric(0, "square_feet");
    expect(metric.kind).toBe("value");
    expect(metric.text).toBe("0 sq ft");
    if (metric.kind !== "value") throw new Error("0 must be a value");
    expect(metric.text).not.toContain(METRIC_NOT_KNOWN);
  });

  it("shows at most two decimals on a long value, without changing the data", () => {
    const value = 1234567.891;
    expect(formatMetric(value, "square_feet").text).toBe("1,234,567.89 sq ft");
    // The value itself is untouched: a second format of the SAME number is identical, and the
    // number still carries its full precision (display rounding never wrote back).
    expect(value).toBe(1234567.891);
    expect(formatMetric(value, "square_feet").text).toBe("1,234,567.89 sq ft");
  });

  it("gives the not-known state for null and for undefined, never a number", () => {
    for (const absent of [null, undefined]) {
      const metric = formatMetric(absent, "square_feet");
      expect(metric.kind).toBe("not_known");
      expect(metric.text).toBe(METRIC_NOT_KNOWN);
      expect(metric).not.toHaveProperty("number");
    }
  });

  it("gives the not-known state for a non-finite number (NaN, Infinity), never 'NaN'", () => {
    expect(formatMetric(Number.NaN, "square_feet").kind).toBe("not_known");
    expect(formatMetric(Number.POSITIVE_INFINITY, "square_feet").kind).toBe("not_known");
  });

  it("shows the bare number for a unit the contract does not know, never a raw code", () => {
    const metric = formatMetric(42, "parsecs" as unknown as Unit);
    expect(metric.kind).toBe("value");
    if (metric.kind !== "value") throw new Error("value expected");
    expect(metric.text).toBe("42");
    expect(metric.unit).toBe("");
  });

  it("reads each known unit for reading, never the enum code", () => {
    expect(formatMetric(55, "feet").text).toBe("55 ft");
    expect(formatMetric(2, "ratio").text).toBe("2.0");
    expect(formatMetric(100, "percent").text).toBe("100%");
    expect(formatMetric(1, "stories").text).toBe("1 floor");
    expect(formatMetric(3, "stories").text).toBe("3 floors");
    expect(formatMetric(1, "dwelling_units").text).toBe("1 unit");
  });
});
