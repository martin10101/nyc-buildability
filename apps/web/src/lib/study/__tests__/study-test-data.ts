/**
 * Shared test data for the study store tests (task C-05). Synthetic only: the
 * option inputs and facts below are test values ("test-fixture-synthetic"),
 * never defaults the store applies - the store takes option inputs from its
 * caller. The contract fixtures are read from packages/contracts/fixtures.
 */

import corner from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_corner_lot_two_options.json";
import type { StudyEntry, StudyResult } from "../study-entry";
import { createStudyEntry } from "../study-operations";
import type { OptionInputs, SiteFact, Study } from "../study-vocabulary";

export const SYNTHETIC_BBL = "5999999999";
export const T1 = "2026-09-30T12:10:00Z";
export const T2 = "2026-09-30T12:20:00Z";
export const T3 = "2026-09-30T12:30:00Z";

/** The committed two-option fixture (revision 3; options opt-a and opt-b) as a fresh copy. */
export function cornerStudy(): Study {
  return JSON.parse(JSON.stringify(corner)) as Study;
}

export function optionInputs(): OptionInputs {
  return {
    addon_selection: [{ addon_id: "test-fixture-synthetic-addon", on: false }],
    goal: { kind: "most_residential_floor_area", text: null },
    program: ["market_rate_residential"],
    floor_to_floor_heights: {
      ground_floor: {
        height_ft: 12,
        basis: "stated_default",
        statement: "Test fixture ground-floor height 12 ft (test-fixture-synthetic)",
      },
      typical_floor: {
        height_ft: 10,
        basis: "stated_default",
        statement: "Test fixture typical floor height 10 ft (test-fixture-synthetic)",
      },
      per_floor_overrides: [],
    },
    assumptions: [],
    existing_building_plan: "no_existing_building",
  };
}

/** An architect-entered street width (source kind architect_entry). */
export function enteredStreetWidth(factId: string, street: string, feet: number, at = T1): SiteFact {
  return {
    contract_version: "1.0.0",
    fact_id: factId,
    key: "street_width",
    lot_bbl: null,
    street,
    value: feet,
    unit: "feet",
    measurement: { rank: "entered", label: "Entered" },
    source: {
      kind: "architect_entry",
      dataset: null,
      dataset_version: null,
      retrieved_at: at,
      query_ref: null,
      document_ref: null,
      statement: null,
    },
    blocks: [],
    editable: true,
  };
}

export function expectOk(result: StudyResult): StudyEntry {
  if (!result.ok) throw new Error(`${result.code}: ${result.message} ${result.problems.join("; ")}`);
  return result.entry;
}

/** A one-option study for the synthetic property (revision 1). */
export function newStudyResult(bbl = SYNTHETIC_BBL): StudyResult {
  return createStudyEntry({
    studyId: `test-fixture-synthetic-study-${bbl}`,
    property: { bbl, address: null },
    lots: [
      {
        bbl,
        approximate_lot_area_sq_ft: null,
        size_measurement: { rank: "unknown", label: "Unknown — enter" },
        selected: true,
      },
    ],
    lotSelection: { mode: "all", combination: { status: "single_lot", reason: null } },
    siteFacts: [],
    initialOption: { optionId: "option-a", name: "Option A", inputs: optionInputs() },
    at: "2026-09-30T12:00:00Z",
  });
}
