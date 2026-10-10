/**
 * A SYNTHETIC two-building results document, for tests ONLY (M5-T149 part B). Nothing here is
 * imported by application code.
 *
 * It is COPIED from the committed 1.4.0 fixtures and marked synthetic: building A from
 * `synthetic_coverage_by_portion_available_contract_1_4_0` and building B from
 * `synthetic_building_alternatives_contract_1_4_0`, placed together in one document so the option
 * comparison has TWO worked buildings to show side by side (the committed fixtures each carry only
 * one worked building, and the committed benchmark carries one worked plus one not-worked). No number
 * is retyped: every value is read from the committed fixtures through `loadResultsFixture`; only the
 * identity fields are relabelled, to mark the document synthetic and never a real result.
 */
import type { Results } from "@/lib/architect/three-answers";
import { loadResultsFixture } from "./results-fixtures";

/** A results document with building A and building B BOTH worked, for the option-comparison tests. */
export function twoBuildingsDocument(): Results {
  const base = loadResultsFixture("recorded_215_16_northern_journey");
  const buildingA = (loadResultsFixture("synthetic_coverage_by_portion_available_contract_1_4_0")
    .building_alternatives ?? [])[0];
  const buildingB = (loadResultsFixture("synthetic_building_alternatives_contract_1_4_0")
    .building_alternatives ?? [])[0];
  if (!buildingA || !buildingB) {
    throw new Error("fixtures changed: both committed 1.4.0 fixtures must carry a building alternative");
  }
  return {
    ...base,
    results_id: "synthetic_two_worked_buildings",
    study_id: "synthetic_two_worked_buildings",
    building_alternatives: [buildingA, buildingB],
    buildings_not_worked: [],
  };
}
