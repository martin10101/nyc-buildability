import { describe, expect, it } from "vitest";
import {
  SITE_FIT_NOT_VERIFIED,
  presentedResults,
  type PresentedResult,
  type ResultKind,
} from "@/lib/architect/presented-results";
import { twoDp } from "@/lib/architect/first-building-options";
import { loadResultsFixture, loadResultsFixtures } from "@/test-support/results-fixtures";

/**
 * M5-T148 part B scenario S6: each result tagged with its kind. The floor-area allowance and the
 * unit limits are allowance; the heights are envelope; a listed building is a scheduled option,
 * never "achieved"; the capacity estimate is an estimate. Plus the cross-cutting rules: run on
 * EVERY committed fixture, no withheld value ever gains a digit, nothing is called verified or
 * achieved by this adapter.
 */

const BENCHMARK = "recorded_215_16_northern_journey";
const KINDS: readonly ResultKind[] = ["allowance", "envelope", "scheduled", "estimate"];

function byId(results: readonly PresentedResult[], id: string): PresentedResult {
  const found = results.find(result => result.id === id);
  if (!found) throw new Error(`no presented result with id ${id}`);
  return found;
}

describe("presentedResults kinds on the benchmark (scenario S6)", () => {
  const doc = loadResultsFixture(BENCHMARK);
  const results = presentedResults(doc);

  it("tags the floor-area allowance values as allowance", () => {
    expect(byId(results, "floor_area_allowance.max_residential_floor_area").resultKind).toBe("allowance");
    expect(byId(results, "floor_area_allowance.max_residential_far").resultKind).toBe("allowance");
  });

  it("tags the withheld legal unit limits as allowance, shown not-known with no digit", () => {
    const limit = byId(results, "floor_area_allowance.legal_unit_limit_standard");
    expect(limit.resultKind).toBe("allowance");
    expect(limit.display.kind).toBe("not_known");
    expect(limit.status.kind).toBe("not_known");
  });

  it("tags the heights as envelope", () => {
    expect(byId(results, "permitted_envelope.max_building_height").resultKind).toBe("envelope");
    expect(byId(results, "permitted_envelope.min_base_height").resultKind).toBe("envelope");
    // a withheld envelope item (lot coverage) is envelope too, not-known.
    const coverage = byId(results, "permitted_envelope.max_lot_coverage");
    expect(coverage.resultKind).toBe("envelope");
    expect(coverage.display.kind).toBe("not_known");
  });

  it("tags building B as a scheduled option, never 'achieved', with site fit not verified", () => {
    const scheduled = byId(results, "building_alternative.B");
    expect(scheduled.resultKind).toBe("scheduled");
    expect(scheduled.note).toBe(SITE_FIT_NOT_VERIFIED);
    expect(scheduled.display.kind).toBe("value");
    if (scheduled.display.kind !== "value") throw new Error("value expected");
    const alt = doc.building_alternatives?.[0];
    if (!alt) throw new Error("fixture changed: no alternative");
    expect(scheduled.display.text).toBe("20,150 sq ft");
    // the adapter's own tag is "scheduled"; "achieved" is never a kind it produces.
    expect(scheduled.resultKind).not.toBe("achieved" as unknown as ResultKind);
  });

  it("tags the capacity estimate as an estimate, the document's range to two decimals", () => {
    const estimate = byId(results, "building_alternative.B.capacity");
    expect(estimate.resultKind).toBe("estimate");
    const capacity = doc.building_alternatives?.[0].capacity_estimate;
    if (!capacity || capacity.label !== "Preliminary capacity estimate") throw new Error("fixture changed");
    expect(estimate.display.kind).toBe("value");
    if (estimate.display.kind !== "value") throw new Error("value expected");
    expect(estimate.display.text).toBe(`${twoDp(capacity.quotient_low)} to ${twoDp(capacity.quotient_high)}`);
    expect(estimate.display.text).toBe("17.27 to 21.59"); // ruling V9
  });
});

describe("presentedResults over every committed fixture", () => {
  // Mutation proof partner: if a withheld value is ever given a formatted number, a result with a
  // not-known status would carry a value display — this invariant fails, catching it.
  it("never gives a withheld value a digit, and only uses the four known kinds", () => {
    for (const { name, doc } of loadResultsFixtures()) {
      const results = presentedResults(doc);
      for (const result of results) {
        expect(KINDS, `${name}/${result.id}`).toContain(result.resultKind);
        if (result.status.kind === "not_known") {
          expect(result.display.kind, `${name}/${result.id}`).toBe("not_known");
        }
      }
    }
  });

  it("never calls a result verified or achieved in the adapter's own wording", () => {
    for (const { name, doc } of loadResultsFixtures()) {
      for (const result of presentedResults(doc)) {
        const where = `${name}/${result.id}`;
        expect(result.resultKind, where).not.toBe("achieved");
        // status words and the scheduled note are the adapter's own text; none says verified/achieved.
        expect(JSON.stringify(result.status), where).not.toContain("Verified");
        if (result.note) expect(result.note.toLowerCase(), where).not.toContain("achieved");
        if (result.resultKind === "scheduled") expect(result.note, where).toBe(SITE_FIT_NOT_VERIFIED);
      }
    }
  });
});
