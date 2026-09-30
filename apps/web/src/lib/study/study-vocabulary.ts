/**
 * Study contract vocabulary for the web client (task C-05, plan M1-10).
 *
 * The ONLY type vocabulary for a study is the GENERATED module
 * packages/contracts/generated/study.ts (task C-03, regenerated from
 * packages/contracts/schemas/v1/study.schema.json + site_fact + common; the
 * contracts-typegen CI job fails on drift). It is consumed the same way
 * src/lib/contract.ts consumes property_profile.ts: a type-only relative import,
 * erased at build time, so no schema is forked here.
 *
 * The runtime enum arrays below are LOCKED to the generated unions with
 * `satisfies` plus the two-way `StudyEnumAssertions` proof, so a contract change
 * that adds or removes an enum member fails `tsc` here instead of drifting.
 *
 * No legal logic lives here: these are the contract's words, not rules.
 */

import type {
  AddonSwitch,
  Assumption,
  BlockedOutput,
  Combination,
  FloorToFloorHeights,
  Goal,
  HeightSetting,
  Lot,
  Measurement,
  Option as StudyOption,
  Origin,
  Revision,
  SiteFact,
  Source,
  Study,
} from "../../../../../packages/contracts/generated/study";

export type {
  AddonSwitch,
  Assumption,
  BlockedOutput,
  Combination,
  FloorToFloorHeights,
  Goal,
  HeightSetting,
  Lot,
  Measurement,
  Origin,
  Revision,
  SiteFact,
  Source,
  Study,
  StudyOption,
};

/** An option's inputs: everything except its identity and display name (plan section 9). */
export type OptionInputs = Omit<StudyOption, "option_id" | "name">;
export type StudyProperty = Study["property"];
export type LotSelection = Study["lot_selection"];
export type MeasurementRank = Measurement["rank"];
export type SourceKind = Source["kind"];
type StudyContractVersion = Study["contract_version"];
type SiteFactContractVersion = SiteFact["contract_version"];
type SiteFactKey = SiteFact["key"];
type SiteFactUnit = NonNullable<SiteFact["unit"]>;
type LotSelectionMode = LotSelection["mode"];
type CombinationStatus = Combination["status"];
type GoalKind = Goal["kind"];
type ProgramComponent = StudyOption["program"][number];
type HeightBasis = HeightSetting["basis"];
type ExistingBuildingPlan = StudyOption["existing_building_plan"];
type OriginKind = Origin["kind"];

export const STUDY_CONTRACT_VERSIONS = ["1.0.0"] as const satisfies readonly StudyContractVersion[];
export const SITE_FACT_CONTRACT_VERSIONS = [
  "1.0.0",
] as const satisfies readonly SiteFactContractVersion[];

/** The exact label every result carries (study.schema.json lot_selection.statement; plan section 3 step 2). */
export const LOT_SELECTION_STATEMENT: LotSelection["statement"] =
  "Based on the lots you selected — the app does not verify the zoning lot";

/** Display label tied one-to-one to its measurement rank (site_fact.schema.json; plan section 4 table). */
export const MEASUREMENT_LABELS = {
  survey_entered: "Survey (entered)",
  city_records: "City records",
  approximate_tax_map: "Approximate — tax map",
  entered: "Entered",
  assumed: "Assumed",
  unknown: "Unknown — enter",
} as const satisfies { readonly [R in MeasurementRank]: Extract<Measurement, { rank: R }>["label"] };

export const MEASUREMENT_RANKS = [
  "survey_entered",
  "city_records",
  "approximate_tax_map",
  "entered",
  "assumed",
  "unknown",
] as const satisfies readonly MeasurementRank[];

export const SITE_FACT_KEYS = [
  "lot_area",
  "lot_frontage",
  "lot_depth",
  "lot_type",
  "zoning_district",
  "commercial_overlay",
  "street_width",
  "existing_zoning_floor_area",
] as const satisfies readonly SiteFactKey[];

export const SITE_FACT_UNITS = ["square_feet", "feet"] as const satisfies readonly SiteFactUnit[];

/** site_fact.schema.json key rule for lot_type (the generated type widens the value to string). */
export const LOT_TYPE_VALUES = ["corner", "interior", "through"] as const;

export const SOURCE_KINDS = [
  "survey",
  "city_dataset",
  "city_filing",
  "tax_map_computation",
  "architect_entry",
  "assumption",
] as const satisfies readonly SourceKind[];

export const BLOCKED_OUTPUTS = [
  "floor_area_allowance",
  "remaining_floor_area",
  "permitted_envelope",
  "building_option",
  "existing_building_paths",
  "unit_estimate",
  "geometry",
] as const satisfies readonly BlockedOutput[];

export const LOT_SELECTION_MODES = ["all", "subset"] as const satisfies readonly LotSelectionMode[];

export const COMBINATION_STATUSES = [
  "single_lot",
  "offered",
  "not_offered",
] as const satisfies readonly CombinationStatus[];

export const GOAL_KINDS = [
  "most_residential_floor_area",
  "most_total_floor_area",
  "other",
] as const satisfies readonly GoalKind[];

export const PROGRAM_COMPONENTS = [
  "market_rate_residential",
  "affordable_residential",
  "senior_residential",
  "community_facility",
  "commercial",
] as const satisfies readonly ProgramComponent[];

export const HEIGHT_BASES = ["stated_default", "entered"] as const satisfies readonly HeightBasis[];

export const EXISTING_BUILDING_PLANS = [
  "no_existing_building",
  "keep",
  "remove",
] as const satisfies readonly ExistingBuildingPlan[];

export const ORIGIN_KINDS = ["new", "copied_from_export"] as const satisfies readonly OriginKind[];

/** Two-way equality proof: `true` only when A and B are the same union. */
type MutuallyEqual<A, B> = [A] extends [B] ? ([B] extends [A] ? true : never) : never;

/**
 * Compile-time exhaustiveness proof (exported so it is never "unused"). If an
 * array above misses a member of its generated union, its slot becomes `never`
 * and `tsc` fails.
 */
export type StudyEnumAssertions = [
  MutuallyEqual<StudyContractVersion, (typeof STUDY_CONTRACT_VERSIONS)[number]>,
  MutuallyEqual<SiteFactContractVersion, (typeof SITE_FACT_CONTRACT_VERSIONS)[number]>,
  MutuallyEqual<MeasurementRank, (typeof MEASUREMENT_RANKS)[number]>,
  MutuallyEqual<SiteFactKey, (typeof SITE_FACT_KEYS)[number]>,
  MutuallyEqual<SiteFactUnit, (typeof SITE_FACT_UNITS)[number]>,
  MutuallyEqual<SourceKind, (typeof SOURCE_KINDS)[number]>,
  MutuallyEqual<BlockedOutput, (typeof BLOCKED_OUTPUTS)[number]>,
  MutuallyEqual<LotSelectionMode, (typeof LOT_SELECTION_MODES)[number]>,
  MutuallyEqual<CombinationStatus, (typeof COMBINATION_STATUSES)[number]>,
  MutuallyEqual<GoalKind, (typeof GOAL_KINDS)[number]>,
  MutuallyEqual<ProgramComponent, (typeof PROGRAM_COMPONENTS)[number]>,
  MutuallyEqual<HeightBasis, (typeof HEIGHT_BASES)[number]>,
  MutuallyEqual<ExistingBuildingPlan, (typeof EXISTING_BUILDING_PLANS)[number]>,
  MutuallyEqual<OriginKind, (typeof ORIGIN_KINDS)[number]>,
];
