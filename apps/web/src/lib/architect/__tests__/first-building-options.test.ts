import { describe, expect, it } from "vitest";
import type { Results } from "@/lib/architect/three-answers";
import {
  feet,
  firstBuildingOptionsView,
  percent,
  sqft,
  twoDp,
} from "@/lib/architect/first-building-options";
import { loadResultsFixture, loadResultsFixtures } from "@/test-support/results-fixtures";

/**
 * The view model for the first-building-options blocks (results contract 1.4.0). Pure functions over
 * a loaded document: every value is read from the document; a withheld result carries no number and
 * no substitute (R556/R570). No number is retyped — expectations are read from the loaded fixture
 * through the module's own formatters.
 */

const BENCHMARK = "synthetic_building_alternatives_contract_1_4_0";
const COVERAGE_AVAILABLE = "synthetic_coverage_by_portion_available_contract_1_4_0";
/** The regenerated committed benchmark carries buildings_not_worked (building A); the synthetic
 * fixtures above (part A, before ruling W14) do not. */
const JOURNEY = "recorded_215_16_northern_journey";

type Alternative = NonNullable<Results["building_alternatives"]>[number];

function firstAlternative(doc: Results): Alternative {
  const alternatives = doc.building_alternatives;
  if (!alternatives || alternatives.length === 0) throw new Error("fixture changed: no alternatives");
  return alternatives[0];
}

describe("firstBuildingOptionsView (contract 1.4.0)", () => {
  it("returns null for every document with none of the new blocks, and a view when any is present", () => {
    for (const { name, doc } of loadResultsFixtures()) {
      const hasBlocks =
        (doc.building_alternatives?.length ?? 0) > 0 ||
        doc.coverage_by_portion != null ||
        (doc.buildings_not_worked?.length ?? 0) > 0;
      const view = firstBuildingOptionsView(doc, true);
      if (hasBlocks) expect(view, name).not.toBeNull();
      else expect(view, name).toBeNull();
    }
  });

  it("maps buildings_not_worked from the document (building A on the benchmark), no number a result", () => {
    const doc = loadResultsFixture(JOURNEY);
    const notWorked = doc.buildings_not_worked ?? [];
    expect(notWorked.length).toBeGreaterThan(0); // building A on the regenerated benchmark
    const view = firstBuildingOptionsView(doc, true);
    if (!view) throw new Error("view missing");
    expect(view.notWorked).toHaveLength(notWorked.length);
    view.notWorked.forEach((mapped, index) => {
      expect(mapped.building).toBe(notWorked[index].building);
      expect(mapped.label).toBe(notWorked[index].label);
      expect(mapped.reason).toBe(notWorked[index].reason);
      expect(mapped.resolvedBy).toBe(notWorked[index].resolved_by);
    });
    // the mapped entries carry no numeric field of their own (reason/resolver are text).
    expect(Object.keys(view.notWorked[0])).toEqual([
      "building",
      "label",
      "reason",
      "resolvedBy",
      "gapKindLine",
    ]);
  });

  it("returns a view when only buildings_not_worked is present (no alternative, no coverage)", () => {
    const base = loadResultsFixture(JOURNEY);
    expect((base.buildings_not_worked?.length ?? 0)).toBeGreaterThan(0);
    const probe = {
      ...base,
      building_alternatives: [],
      coverage_by_portion: null,
    } as unknown as typeof base;
    const view = firstBuildingOptionsView(probe, true);
    expect(view).not.toBeNull();
    expect(view?.alternatives).toHaveLength(0);
    expect((view?.notWorked.length ?? 0)).toBeGreaterThan(0);
  });

  it("maps building B's floor schedule, totals and estimate, read from the document", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const alternative = firstAlternative(doc);
    const view = firstBuildingOptionsView(doc, true);
    if (!view) throw new Error("view missing");
    expect(view.alternatives).toHaveLength(doc.building_alternatives?.length ?? 0);
    const mapped = view.alternatives[0];
    expect(mapped.label).toBe(alternative.label);
    expect(mapped.storeyCount).toBe(alternative.storey_count);
    expect(mapped.height).toBe(feet(alternative.height_ft));
    expect(mapped.totalFloorArea).toBe(sqft(alternative.total_floor_area_sqft));
    expect(mapped.floorSchedule).toHaveLength(alternative.floor_schedule.length);
    expect(mapped.floorSchedule[0].planArea).toBe(sqft(alternative.floor_schedule[0].plan_area_sqft));
    // the alternative is conditional, never settled by silence (ruling W2).
    expect(mapped.isConditional).toBe(true);
    expect(mapped.conditions.length).toBeGreaterThan(0);
    expect(mapped.notChecked).toEqual(alternative.not_checked);
  });

  it("maps the preliminary capacity estimate to two decimals, from the document", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const estimate = firstAlternative(doc).capacity_estimate;
    if (estimate.label !== "Preliminary capacity estimate") throw new Error("fixture changed");
    const view = firstBuildingOptionsView(doc, true);
    const capacity = view?.alternatives[0].capacity;
    if (!capacity || capacity.kind !== "known") throw new Error("estimate should be known");
    expect(capacity.label).toBe("Preliminary capacity estimate");
    expect(capacity.low).toBe(twoDp(estimate.quotient_low));
    expect(capacity.high).toBe(twoDp(estimate.quotient_high));
    expect(capacity.shareLow).toBe(twoDp(estimate.share_low));
    expect(capacity.shareHigh).toBe(twoDp(estimate.share_high));
    expect(capacity.apartmentSize).toBe(sqft(estimate.apartment_size_sqft));
  });

  it("maps a withheld coverage with NO number and no substitute (R556/R570)", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const view = firstBuildingOptionsView(doc, true);
    const coverage = view?.coverage;
    if (!coverage || coverage.kind !== "withheld") throw new Error("coverage should be withheld");
    // the withheld view carries the law reason and what would settle it — but NO numeric figure.
    expect("footprint" in coverage).toBe(false);
    expect("cornerArea" in coverage).toBe(false);
    expect(coverage.reason.length).toBeGreaterThan(0);
    expect(coverage.resolvedBy.length).toBeGreaterThan(0);
  });

  it("maps fit_note when the document carries it (the regenerated benchmark), else null", () => {
    // The regenerated committed document carries the optional fit_note on building B; the synthetic
    // benchmark fixture (which predates the field) carries none — the view reads whichever the
    // document holds, never a typed value.
    const regenerated = loadResultsFixture("recorded_215_16_northern_journey");
    const alternative = firstAlternative(regenerated);
    const view = firstBuildingOptionsView(regenerated, true);
    expect(view?.alternatives[0].fitNote).toBe(alternative.fit_note ?? null);
    expect(view?.alternatives[0].fitNote).not.toBeNull();

    const synthetic = loadResultsFixture(BENCHMARK);
    expect(firstBuildingOptionsView(synthetic, true)?.alternatives[0].fitNote).toBe(
      firstAlternative(synthetic).fit_note ?? null,
    );
  });

  it("maps an available coverage with its ratios and footprint, from the document", () => {
    const doc = loadResultsFixture(COVERAGE_AVAILABLE);
    const coverage = doc.coverage_by_portion;
    if (!coverage || coverage.status !== "available") throw new Error("fixture changed");
    const view = firstBuildingOptionsView(doc, true);
    const mapped = view?.coverage;
    if (!mapped || mapped.kind !== "available") throw new Error("coverage should be available");
    expect(mapped.footprint).toBe(sqft(coverage.footprint_sqft));
    expect(mapped.cornerRatio).toBe(percent(coverage.corner_ratio));
    expect(mapped.interiorRatio).toBe(percent(coverage.interior_ratio));
  });

  it("hides the numbers on a draft architect surface and shows them behind the lane flag", () => {
    const doc = loadResultsFixture(BENCHMARK);
    expect(doc.draft).toBe(true);
    expect(firstBuildingOptionsView(doc, false)?.draftHidden).toBe(true);
    expect(firstBuildingOptionsView(doc, true)?.draftHidden).toBe(false);
  });
});
