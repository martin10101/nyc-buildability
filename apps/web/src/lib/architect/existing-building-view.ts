/**
 * Presentation model for step 4 "Existing building" of the lot & site setup window
 * (queue D-06 slice 2; plan docs/PRODUCT_PLAN_CURRENT_2026-09-28.md §3 step 4, §4). It turns the
 * closed option field `existing_building_plan` and the `existing_zoning_floor_area` site fact into
 * plain display rows and builds the contract-shaped fact for an entered value.
 *
 * Boundaries this module keeps (same discipline as ./lot-site-setup):
 * - It computes NO legal logic and NO remaining capacity. Remaining capacity is "Not confirmed"
 *   elsewhere (./tax-lot-scope) and is never derived on screen (plan §3 step 4; owner D-090-R038).
 * - It never writes a CITY source for an entered existing zoning floor area: the architect picks
 *   "architect entry" or "stated assumption" explicitly (plan §3 step 4: a DOB filing / certificate
 *   is a city value the server supplies; a typed value is the architect's entry or a stated
 *   assumption — never a city dataset such as PLUTO/DOF building area).
 * - Plan tokens never reach the face: each enum value maps to plain words here (one map, tested per
 *   value), and nothing is pre-selected — an unchosen plan shows the study's honest default.
 */

import {
  EXISTING_BUILDING_PLANS,
  MEASUREMENT_LABELS,
  type SiteFact,
  type Source,
  type Study,
} from "@/lib/study/study-vocabulary";
import {
  ENTER_POSITIVE_NUMBER,
  ENTER_VALUE_FIRST,
  FACE_TEXT_MAX_CHARS,
  groupSiteFactRows,
  siteFactRowsOf,
  type FactInputResult,
  type FaceTextBudget,
  type SiteFactGroup,
} from "./lot-site-setup";

export type ExistingBuildingPlan = (typeof EXISTING_BUILDING_PLANS)[number];

/** The step heading and the radio-group label (plan §3 step 4). */
export const EXISTING_BUILDING_STEP_HEADING = "Existing building";
export const EXISTING_BUILDING_GROUP_LABEL = "What happens to the existing building?";

/** Honest unchosen state: nothing is assumed, and neither keep nor remove is pre-selected. */
export const EXISTING_BUILDING_UNCHOSEN_NOTE = "No choice made yet. Pick one — nothing is assumed.";

/**
 * Plain words for each closed `existing_building_plan` value (study.schema.json; vocabulary exports
 * no labels, so the map lives here and a test covers every value). Never a raw enum token on the face.
 */
export const EXISTING_BUILDING_PLAN_LABELS: Record<ExistingBuildingPlan, string> = {
  no_existing_building: "No existing building",
  keep: "Keep the existing building",
  remove: "Remove the existing building",
};

export interface ExistingBuildingPlanOption {
  value: ExistingBuildingPlan;
  label: string;
}

/** The three choices in the vocabulary's own order, each in plain words, for the radio group. */
export function existingBuildingPlanOptions(): ExistingBuildingPlanOption[] {
  return EXISTING_BUILDING_PLANS.map((value) => ({ value, label: EXISTING_BUILDING_PLAN_LABELS[value] }));
}

/** The plan of the study's selected option (the shown value; never a silent keep/remove). */
export function selectedOptionPlan(study: Study): ExistingBuildingPlan {
  const option =
    study.options.find((candidate) => candidate.option_id === study.selected_option_id) ?? study.options[0];
  return option.existing_building_plan;
}

export const EXISTING_FLOOR_AREA_KEY = "existing_zoning_floor_area" as const;

/** The step-4 entry labels (plain words; §5a readable copy). */
export const EXISTING_FLOOR_AREA_INPUT_LABEL = "Existing zoning floor area (sq ft)";
export const EXISTING_FLOOR_AREA_SOURCE_LEGEND = "How is this value sourced?";
export const CHOOSE_SOURCE_REASON = "Choose how this value is sourced.";

/** The only two source kinds an architect may enter for this fact (never a city source). */
export type ExistingFloorAreaSourceKind = "architect_entry" | "assumption";

export interface ExistingFloorAreaSourceChoice {
  kind: ExistingFloorAreaSourceKind;
  label: string;
}

export const EXISTING_FLOOR_AREA_SOURCE_CHOICES: ExistingFloorAreaSourceChoice[] = [
  { kind: "architect_entry", label: "Architect entry" },
  { kind: "assumption", label: "Stated assumption" },
];

/**
 * The existing-zoning-floor-area fact group (the primary value and, when a CITY filing is kept and
 * the architect has entered one, the "Entered"/"Assumed" value beside it). Reuses the tested
 * ./lot-site-setup row + grouping logic so a `<fact_id>-entered` value stays beside its base. Null
 * when the study carries no existing-zfa fact at all (the server always supplies one — unknown when
 * no DOB figure exists — so this is an edge).
 */
export function existingFloorAreaGroup(facts: SiteFact[]): SiteFactGroup | null {
  const rows = siteFactRowsOf(facts.filter((fact) => fact.key === EXISTING_FLOOR_AREA_KEY));
  return groupSiteFactRows(rows)[0] ?? null;
}

/** The primary existing-zfa fact (not a `-entered` mirror), or null when the study carries none. */
export function existingFloorAreaFact(facts: SiteFact[]): SiteFact | null {
  return (
    facts.find((fact) => fact.key === EXISTING_FLOOR_AREA_KEY && !fact.fact_id.endsWith("-entered")) ??
    facts.find((fact) => fact.key === EXISTING_FLOOR_AREA_KEY) ??
    null
  );
}

/**
 * Validate a typed existing zoning floor area: a number greater than zero (square feet). Shares the
 * exact per-fact-edit messages (./lot-site-setup), so the step rejects a bad value with the same
 * plain words. No value is computed; the contract (and the store, when a study exists) is the final
 * guard. The schema forbids a zero/negative existing_zoning_floor_area outright.
 */
export function validateExistingFloorAreaInput(raw: string): FactInputResult {
  const trimmed = raw.trim();
  if (trimmed === "") return { ok: false, reason: ENTER_VALUE_FIRST };
  const value = Number(trimmed);
  if (!Number.isFinite(value) || value <= 0) return { ok: false, reason: ENTER_POSITIVE_NUMBER };
  return { ok: true, value };
}

/** Whether the existing fact is a kept CITY value (a DOB filing / certificate). Such a value is
 * never overwritten in place: an entry is a new fact beside it (site_fact `editable`). */
function isKeptCityExistingFact(existing: SiteFact | null): boolean {
  return existing?.source?.kind === "city_filing";
}

/**
 * Build the contract-shaped existing-zoning-floor-area fact for a value the architect entered. The
 * source is the architect's chosen kind — "architect entry" (rank "Entered") or "stated assumption"
 * (rank "Assumed", with the assumption stated) — and NEVER a city source. A kept city filing is
 * preserved: the entry takes a `<fact_id>-entered` id so the city value stays beside it; an unknown
 * placeholder or an earlier entry is replaced in place under its own id. The key, lot and unit are
 * fixed by the schema (existing_zoning_floor_area, square_feet); nothing is computed.
 */
export function buildExistingFloorAreaFact(
  existing: SiteFact | null,
  bbl: string,
  value: number,
  sourceKind: ExistingFloorAreaSourceKind,
  at: string,
): SiteFact {
  const baseId = existing?.fact_id ?? "existing-zoning-floor-area";
  const source: Source =
    sourceKind === "assumption"
      ? {
          kind: "assumption",
          dataset: null,
          dataset_version: null,
          retrieved_at: at,
          query_ref: null,
          document_ref: null,
          statement: `Architect's stated assumption: existing zoning floor area ${value.toLocaleString(
            "en-US",
          )} sq ft.`,
        }
      : {
          kind: "architect_entry",
          dataset: null,
          dataset_version: null,
          retrieved_at: at,
          query_ref: null,
          document_ref: null,
          statement: null,
        };
  return {
    contract_version: existing?.contract_version ?? "1.0.0",
    fact_id: isKeptCityExistingFact(existing) ? `${baseId}-entered` : baseId,
    key: EXISTING_FLOOR_AREA_KEY,
    lot_bbl: existing ? existing.lot_bbl : bbl,
    street: null,
    value,
    unit: "square_feet",
    measurement:
      sourceKind === "assumption"
        ? { rank: "assumed", label: MEASUREMENT_LABELS.assumed }
        : { rank: "entered", label: MEASUREMENT_LABELS.entered },
    source,
    blocks: [],
    editable: true,
  };
}

/**
 * The step's §5a face-text budget (mirrors ./lot-site-setup lotSiteSetupFaceBudget). Every
 * app-authored string shown on the step face must be <= FACE_TEXT_MAX_CHARS; the step adds no
 * standing notice block (the plan radio group is a control, and the fact's "Unknown — enter"/blocks
 * line is fact-level behind the "keep" choice), so noticeCount is 0.
 */
export function existingBuildingFaceBudget(): FaceTextBudget {
  return {
    appStrings: [
      EXISTING_BUILDING_STEP_HEADING,
      EXISTING_BUILDING_GROUP_LABEL,
      EXISTING_BUILDING_UNCHOSEN_NOTE,
      EXISTING_FLOOR_AREA_INPUT_LABEL,
      EXISTING_FLOOR_AREA_SOURCE_LEGEND,
      CHOOSE_SOURCE_REASON,
      ...existingBuildingPlanOptions().map((option) => option.label),
      ...EXISTING_FLOOR_AREA_SOURCE_CHOICES.map((choice) => choice.label),
    ],
    pinned: [],
    noticeCount: 0,
  };
}

/** Re-exported so the step and its tests share the one budget ceiling. */
export { FACE_TEXT_MAX_CHARS };
