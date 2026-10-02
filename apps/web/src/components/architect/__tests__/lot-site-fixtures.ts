/**
 * Contract-shaped study fixtures for the D-04 lot-choice + site-facts tests
 * (queue D-04, plan M1-13). NOT a test file (no *.test.*), so vitest never
 * collects it; the tests import it and prove each study is contract-valid with
 * the real validateStudyDocument.
 *
 * The single-lot "offered" path uses the committed contract fixture
 * packages/contracts/fixtures/valid/study/synthetic_corner_lot_two_options.json
 * directly (imported in the test). This file adds the one shape that has no
 * committed fixture: two lots on different blocks whose combination B-07 refuses.
 * The refusal reason is COPIED VERBATIM from B-07's own output
 * (services/api/app/spatial/multi_lot_site/combination.py `_blocks_reason`) for
 * these two BBLs — the web never computes it.
 *
 * BBLs are synthetic (borough 3, two different blocks) so the study is clearly
 * not a real property; measurement labels and statement come from the locked
 * study vocabulary to stay byte-exact.
 */

import { LOT_SELECTION_STATEMENT, MEASUREMENT_LABELS, type Study } from "@/lib/study/study-vocabulary";

export const LOT_A = "3001230001"; // borough 3, block 123, lot 1
export const LOT_B = "3004560070"; // borough 3, block 456, lot 70

/** B-07 cross-block refusal, verbatim from combination.py `_blocks_reason` for LOT_A + LOT_B. */
export const CROSS_BLOCK_REASON =
  "Lots can be combined only if they are on one block. The selection is on block 123 (lot 1) and block 456 (lot 70).";

const TAX_MAP = { rank: "approximate_tax_map", label: MEASUREMENT_LABELS.approximate_tax_map } as const;
const CITY = { rank: "city_records", label: MEASUREMENT_LABELS.city_records } as const;
const UNKNOWN = { rank: "unknown", label: MEASUREMENT_LABELS.unknown } as const;

/** Two tax lots on different blocks: the app lists both, refuses the combination, shows why. */
export const twoLotCrossBlockStudy: Study = {
  contract_version: "1.0.0",
  study_id: "test-fixture-synthetic-study-d04-cross-block",
  property: { bbl: LOT_A, address: "1 Synthetic Test Street (test-fixture-synthetic)" },
  lots: [
    { bbl: LOT_A, approximate_lot_area_sq_ft: 4000, size_measurement: TAX_MAP, selected: true },
    { bbl: LOT_B, approximate_lot_area_sq_ft: 3200, size_measurement: CITY, selected: true },
  ],
  lot_selection: {
    mode: "all",
    statement: LOT_SELECTION_STATEMENT,
    combination: { status: "not_offered", reason: CROSS_BLOCK_REASON },
  },
  site: {
    facts: [
      {
        contract_version: "1.0.0",
        fact_id: "fact-lot-area-a",
        key: "lot_area",
        lot_bbl: LOT_A,
        street: null,
        value: 4000,
        unit: "square_feet",
        measurement: TAX_MAP,
        source: {
          kind: "tax_map_computation",
          dataset: "test-fixture-synthetic DOF Digital Tax Map outline",
          dataset_version: null,
          retrieved_at: "2026-09-30T12:00:00Z",
          query_ref: "test-fixture-synthetic://dtm/3001230001",
          document_ref: null,
          statement: null,
        },
        blocks: [],
        editable: true,
      },
      {
        contract_version: "1.0.0",
        fact_id: "fact-lot-type",
        key: "lot_type",
        lot_bbl: LOT_A,
        street: null,
        value: "corner",
        unit: null,
        measurement: CITY,
        source: {
          kind: "city_dataset",
          dataset: "test-fixture-synthetic PLUTO-shaped record",
          dataset_version: "test-fixture-synthetic",
          retrieved_at: "2026-09-30T12:00:00Z",
          query_ref: "test-fixture-synthetic://pluto/3001230001",
          document_ref: null,
          statement: null,
        },
        blocks: [],
        editable: true,
      },
      {
        contract_version: "1.0.0",
        fact_id: "fact-zoning-district",
        key: "zoning_district",
        lot_bbl: LOT_A,
        street: null,
        value: "R6B",
        unit: null,
        measurement: CITY,
        source: {
          kind: "city_dataset",
          dataset: "test-fixture-synthetic PLUTO-shaped record",
          dataset_version: "test-fixture-synthetic",
          retrieved_at: "2026-09-30T12:00:00Z",
          query_ref: "test-fixture-synthetic://pluto/3001230001",
          document_ref: null,
          statement: null,
        },
        blocks: [],
        editable: true,
      },
      {
        contract_version: "1.0.0",
        fact_id: "fact-street-width-unknown",
        key: "street_width",
        lot_bbl: null,
        street: "Example Avenue",
        value: null,
        unit: null,
        measurement: UNKNOWN,
        source: null,
        blocks: ["permitted_envelope", "building_option"],
        editable: true,
      },
    ],
  },
  options: [
    {
      option_id: "opt-a",
      name: "Option A",
      addon_selection: [],
      goal: { kind: "most_residential_floor_area", text: null },
      program: ["market_rate_residential"],
      floor_to_floor_heights: {
        ground_floor: { height_ft: 12, basis: "stated_default", statement: "Default ground-floor height: 12 ft (editable)" },
        typical_floor: { height_ft: 10, basis: "stated_default", statement: "Default typical floor height: 10 ft (editable)" },
        per_floor_overrides: [],
      },
      assumptions: [],
      existing_building_plan: "no_existing_building",
    },
  ],
  selected_option_id: "opt-a",
  revision: { number: 1, created_at: "2026-09-30T12:00:00Z", parent: null },
  origin: { kind: "new", export_id: null },
};
