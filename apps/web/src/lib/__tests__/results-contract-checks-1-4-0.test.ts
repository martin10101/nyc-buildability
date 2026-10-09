import { describe, expect, it } from "vitest";
import {
  SUPPORTED_RESULTS_CONTRACT_VERSIONS,
  validateResultsDocument,
} from "@/lib/results-contract-checks";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import type { Results } from "@/lib/architect/three-answers";

/**
 * [WIRING] The website's own check of a returned results document at contract 1.4.0 (M5-T147). It
 * accepts the additive first-building-options blocks and REFUSES a document in which a withheld
 * coverage result carries a number or a worked alternative has a wrong estimate label (R556/R570;
 * D-090-R543). The two 1.4.0 synthetic fixtures are real contract documents, so a check that accepts
 * them and rejects deliberate breakages is never vacuous. The committed benchmark (which part E
 * regenerates to 1.4.0) is NOT read here.
 */

const BENCHMARK = "synthetic_building_alternatives_contract_1_4_0";
const COVERAGE_AVAILABLE = "synthetic_coverage_by_portion_available_contract_1_4_0";
/** The regenerated committed benchmark carries buildings_not_worked (building A); the synthetic
 * fixtures above (part A, before ruling W14) do not. */
const JOURNEY = "recorded_215_16_northern_journey";

/** A deliberate wrong-shape probe, written `as unknown as Results` (CODING_RULES), never a direct
 * cast — these bodies exist only to be refused. */
function probe(name: string, overrides: (doc: Results) => void): unknown {
  const doc = loadResultsFixture(name);
  overrides(doc);
  return doc as unknown as Results;
}

describe("validateResultsDocument — the additive 1.4.0 blocks [WIRING]", () => {
  it("accepts the two 1.4.0 synthetic fixtures (never vacuous)", () => {
    expect(validateResultsDocument(loadResultsFixture(BENCHMARK)).ok).toBe(true);
    expect(validateResultsDocument(loadResultsFixture(COVERAGE_AVAILABLE)).ok).toBe(true);
  });

  it("accepts contract 1.4.0 and keeps 1.3.0, refusing an earlier version", () => {
    expect(SUPPORTED_RESULTS_CONTRACT_VERSIONS).toContain("1.3.0");
    expect(SUPPORTED_RESULTS_CONTRACT_VERSIONS).toContain("1.4.0");
    const body = probe(BENCHMARK, doc => {
      (doc as { contract_version: string }).contract_version = "1.2.0";
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.startsWith("contract_version"))).toBe(true);
  });

  it("R556/R570: refuses a withheld coverage result that carries a footprint figure", () => {
    const body = probe(BENCHMARK, doc => {
      const coverage = doc.coverage_by_portion;
      if (!coverage || coverage.status !== "withheld") throw new Error("fixture changed");
      (coverage as unknown as { footprint_sqft: number }).footprint_sqft = 8060;
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(
        result.problems.some(
          p => p.includes("coverage_by_portion.footprint_sqft") && p.includes("never carry a number"),
        ),
      ).toBe(true);
    }
  });

  it("D-090-R543: refuses a worked alternative whose estimate label is not an owner label", () => {
    const body = probe(BENCHMARK, doc => {
      const alternative = doc.building_alternatives?.[0];
      if (!alternative) throw new Error("fixture changed");
      (alternative.capacity_estimate as { label: string }).label = "Apartments";
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some(p => p.includes("capacity_estimate.label"))).toBe(true);
    }
  });

  it("refuses a floor-schedule row with a non-numeric plan area", () => {
    const body = probe(BENCHMARK, doc => {
      const alternative = doc.building_alternatives?.[0];
      if (!alternative) throw new Error("fixture changed");
      (alternative.floor_schedule[0] as { plan_area_sqft: unknown }).plan_area_sqft = "wide";
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some(p => p.includes("plan_area_sqft"))).toBe(true);
    }
  });

  it("refuses a worked alternative whose list of unchecked items is empty (ruling W5)", () => {
    const body = probe(BENCHMARK, doc => {
      const alternative = doc.building_alternatives?.[0];
      if (!alternative) throw new Error("fixture changed");
      (alternative as unknown as { not_checked: unknown[] }).not_checked = [];
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some(p => p.includes("not_checked"))).toBe(true);
    }
  });

  it("W14/W15: accepts the benchmark's buildings_not_worked list (building A carries no number)", () => {
    const doc = loadResultsFixture(JOURNEY);
    expect((doc.buildings_not_worked?.length ?? 0)).toBeGreaterThan(0);
    expect(validateResultsDocument(doc).ok).toBe(true);
  });

  it("W14/W15: refuses a not-worked entry missing its reason, and one missing its gap_kind", () => {
    const missingReason = probe(JOURNEY, doc => {
      const entry = doc.buildings_not_worked?.[0];
      if (!entry) throw new Error("fixture changed");
      delete (entry as { reason?: unknown }).reason;
    });
    const r1 = validateResultsDocument(missingReason);
    expect(r1.ok).toBe(false);
    if (!r1.ok) expect(r1.problems.some(p => p.includes("buildings_not_worked[0].reason"))).toBe(true);

    const badKind = probe(JOURNEY, doc => {
      const entry = doc.buildings_not_worked?.[0];
      if (!entry) throw new Error("fixture changed");
      (entry as { gap_kind: string }).gap_kind = "not_a_kind";
    });
    const r2 = validateResultsDocument(badKind);
    expect(r2.ok).toBe(false);
    if (!r2.ok) expect(r2.problems.some(p => p.includes("buildings_not_worked[0].gap_kind"))).toBe(true);
  });
});
