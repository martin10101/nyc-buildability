/**
 * Runtime validation of a study document against
 * packages/contracts/schemas/v1/study.schema.json (task C-05, plan M1-10), the
 * same hand-written-mirror approach as src/lib/validate-profile.ts and
 * src/lib/scenario-contract.ts (the web client has no JSON-Schema engine).
 *
 * FAILURE IS TOTAL: the caller receives either the typed study or only a
 * bounded problem list, never a partially usable document. Unknown keys are
 * rejected at every level (`additionalProperties: false`), numbers must be
 * finite (strict JSON), and the fixture-only `_expected_failure` key is refused.
 *
 * On top of the schema, the store's cross-field invariants (the schema leaves
 * the first to "the study store"): the selected option is one of the options;
 * option ids are unique (each option is edited independently by its id); site
 * fact ids are unique (a fact id is stable within its study).
 *
 * Shape only; no legal logic; never rewrites a value.
 */

import {
  Problems,
  checkBoolean,
  checkEnum,
  checkNonEmptyString,
  isNonEmptyString,
} from "../scenario-contract-checks";
import { checkMeasurement, checkSiteFact } from "./site-fact-validator";
import {
  checkArray,
  checkBbl,
  checkDateTime,
  checkKeys,
  checkNoFixtureAnnotation,
  checkNullableNonEmptyString,
  checkObject,
  checkPositiveNumber,
  isJsonNumber,
} from "./study-checks";
import {
  COMBINATION_STATUSES,
  EXISTING_BUILDING_PLANS,
  GOAL_KINDS,
  HEIGHT_BASES,
  LOT_SELECTION_MODES,
  LOT_SELECTION_STATEMENT,
  ORIGIN_KINDS,
  PROGRAM_COMPONENTS,
  STUDY_CONTRACT_VERSIONS,
  type Study,
} from "./study-vocabulary";

export type StudyValidationResult =
  | { ok: true; study: Study }
  | { ok: false; problems: string[] };

const STUDY_REQUIRED_KEYS = [
  "contract_version",
  "study_id",
  "property",
  "lots",
  "lot_selection",
  "site",
  "options",
  "selected_option_id",
  "revision",
  "origin",
] as const;

const OPTION_REQUIRED_KEYS = [
  "option_id",
  "name",
  "addon_selection",
  "goal",
  "program",
  "floor_to_floor_heights",
  "assumptions",
  "existing_building_plan",
] as const;

function checkProperty(problems: Problems, value: unknown): void {
  const property = checkObject(problems, "property", value);
  if (!property) return;
  checkKeys(problems, "property", property, ["bbl", "address"]);
  checkBbl(problems, "property.bbl", property.bbl);
  checkNullableNonEmptyString(problems, "property.address", property.address);
}

/** lot oneOf: a positive size with a known rank, or null with rank 'unknown' (never 0). */
function checkLots(problems: Problems, value: unknown): void {
  const lots = checkArray(problems, "lots", value, 1);
  lots?.forEach((item, index) => {
    const path = `lots[${index}]`;
    const lot = checkObject(problems, path, item);
    if (!lot) return;
    checkKeys(problems, path, lot, ["bbl", "approximate_lot_area_sq_ft", "size_measurement", "selected"]);
    checkBbl(problems, `${path}.bbl`, lot.bbl);
    checkBoolean(problems, `${path}.selected`, lot.selected);
    const rank = checkMeasurement(problems, `${path}.size_measurement`, lot.size_measurement);
    const area = lot.approximate_lot_area_sq_ft;
    if (area === null) {
      if (rank !== null && rank !== "unknown") {
        problems.add(`${path}.size_measurement`, "an unknown lot size must carry rank 'unknown'");
      }
    } else if (!(isJsonNumber(area) && area > 0)) {
      problems.add(`${path}.approximate_lot_area_sq_ft`, "must be a number greater than 0, or null when unknown (never 0)");
    } else if (rank === "unknown") {
      problems.add(`${path}.size_measurement`, "a known lot size needs a known rank");
    }
  });
}

/** lot_selection and its combination oneOf (a reason only, and always, when not offered). */
function checkLotSelection(problems: Problems, value: unknown): void {
  const selection = checkObject(problems, "lot_selection", value);
  if (!selection) return;
  checkKeys(problems, "lot_selection", selection, ["mode", "statement", "combination"]);
  checkEnum(problems, "lot_selection.mode", selection.mode, LOT_SELECTION_MODES);
  if (selection.statement !== LOT_SELECTION_STATEMENT) {
    problems.add("lot_selection.statement", "must be the exact lot-selection statement (plan section 3 step 2)");
  }
  const combination = checkObject(problems, "lot_selection.combination", selection.combination);
  if (!combination) return;
  checkKeys(problems, "lot_selection.combination", combination, ["status", "reason"]);
  checkEnum(problems, "lot_selection.combination.status", combination.status, COMBINATION_STATUSES);
  checkNullableNonEmptyString(problems, "lot_selection.combination.reason", combination.reason);
  if (combination.status === "not_offered" && combination.reason === null) {
    problems.add("lot_selection.combination.reason", "a combination that is not offered must state the reason");
  }
  if ((combination.status === "single_lot" || combination.status === "offered") && combination.reason !== null) {
    problems.add("lot_selection.combination.reason", "must be null unless the combination is not offered");
  }
}

/** The `key` of each array entry (null when absent or invalid), aligned with the entry index. */
function idsOf(entries: readonly unknown[] | null, key: string): (string | null)[] {
  return (entries ?? []).map((entry) => {
    const id = typeof entry === "object" && entry !== null ? (entry as Record<string, unknown>)[key] : null;
    return isNonEmptyString(id) ? id : null;
  });
}

/** site.facts; returns the fact ids for the uniqueness check. */
function checkSite(problems: Problems, value: unknown): (string | null)[] {
  const site = checkObject(problems, "site", value);
  if (!site) return [];
  checkKeys(problems, "site", site, ["facts"]);
  const facts = checkArray(problems, "site.facts", site.facts);
  facts?.forEach((fact, index) => {
    checkSiteFact(problems, `site.facts[${index}]`, fact);
  });
  return idsOf(facts, "fact_id");
}

function checkGoal(problems: Problems, path: string, value: unknown): void {
  const goal = checkObject(problems, path, value);
  if (!goal) return;
  checkKeys(problems, path, goal, ["kind", "text"]);
  checkEnum(problems, `${path}.kind`, goal.kind, GOAL_KINDS);
  checkNullableNonEmptyString(problems, `${path}.text`, goal.text);
  if (goal.kind === "other" && goal.text === null) {
    problems.add(`${path}.text`, "a goal of 'other' must state the goal in words (plan section 5)");
  }
  if (goal.kind !== "other" && goal.text !== null) {
    problems.add(`${path}.text`, "must be null unless the goal is 'other'");
  }
}

function checkHeightSetting(problems: Problems, path: string, value: unknown): void {
  const setting = checkObject(problems, path, value);
  if (!setting) return;
  checkKeys(problems, path, setting, ["height_ft", "basis", "statement"]);
  checkPositiveNumber(problems, `${path}.height_ft`, setting.height_ft);
  checkEnum(problems, `${path}.basis`, setting.basis, HEIGHT_BASES);
  checkNonEmptyString(problems, `${path}.statement`, setting.statement);
}

function checkFloorHeights(problems: Problems, path: string, value: unknown): void {
  const heights = checkObject(problems, path, value);
  if (!heights) return;
  checkKeys(problems, path, heights, ["ground_floor", "typical_floor", "per_floor_overrides"]);
  checkHeightSetting(problems, `${path}.ground_floor`, heights.ground_floor);
  checkHeightSetting(problems, `${path}.typical_floor`, heights.typical_floor);
  const overrides = checkArray(problems, `${path}.per_floor_overrides`, heights.per_floor_overrides);
  overrides?.forEach((item, index) => {
    const overridePath = `${path}.per_floor_overrides[${index}]`;
    const entry = checkObject(problems, overridePath, item);
    if (!entry) return;
    checkKeys(problems, overridePath, entry, ["floor", "height_ft"]);
    if (!(Number.isInteger(entry.floor) && (entry.floor as number) >= 1)) {
      problems.add(`${overridePath}.floor`, "must be an integer of at least 1 (1 = ground floor)");
    }
    checkPositiveNumber(problems, `${overridePath}.height_ft`, entry.height_ft);
  });
}

function checkAssumptions(problems: Problems, path: string, value: unknown): void {
  const assumptions = checkArray(problems, path, value);
  assumptions?.forEach((item, index) => {
    const entryPath = `${path}[${index}]`;
    const entry = checkObject(problems, entryPath, item);
    if (!entry) return;
    checkKeys(problems, entryPath, entry, ["assumption_id", "statement", "value", "unit"]);
    checkNonEmptyString(problems, `${entryPath}.assumption_id`, entry.assumption_id);
    checkNonEmptyString(problems, `${entryPath}.statement`, entry.statement);
    const scalar = entry.value;
    if (!(scalar === null || typeof scalar === "string" || typeof scalar === "boolean" || isJsonNumber(scalar))) {
      problems.add(`${entryPath}.value`, "must be a finite number, string, boolean, or null");
    }
    if (!(entry.unit === null || typeof entry.unit === "string")) {
      problems.add(`${entryPath}.unit`, "must be a string or null");
    }
  });
}

function checkOption(problems: Problems, path: string, value: unknown): void {
  const option = checkObject(problems, path, value);
  if (!option) return;
  checkKeys(problems, path, option, OPTION_REQUIRED_KEYS);
  checkNonEmptyString(problems, `${path}.option_id`, option.option_id);
  checkNonEmptyString(problems, `${path}.name`, option.name);
  const switches = checkArray(problems, `${path}.addon_selection`, option.addon_selection);
  switches?.forEach((item, index) => {
    const switchPath = `${path}.addon_selection[${index}]`;
    const entry = checkObject(problems, switchPath, item);
    if (!entry) return;
    checkKeys(problems, switchPath, entry, ["addon_id", "on"]);
    checkNonEmptyString(problems, `${switchPath}.addon_id`, entry.addon_id);
    checkBoolean(problems, `${switchPath}.on`, entry.on);
  });
  checkGoal(problems, `${path}.goal`, option.goal);
  const program = checkArray(problems, `${path}.program`, option.program, 1);
  program?.forEach((entry, index) => {
    checkEnum(problems, `${path}.program[${index}]`, entry, PROGRAM_COMPONENTS);
  });
  checkFloorHeights(problems, `${path}.floor_to_floor_heights`, option.floor_to_floor_heights);
  checkAssumptions(problems, `${path}.assumptions`, option.assumptions);
  checkEnum(problems, `${path}.existing_building_plan`, option.existing_building_plan, EXISTING_BUILDING_PLANS);
}

/** options; returns the option ids for the cross-field checks. */
function checkOptions(problems: Problems, value: unknown): (string | null)[] {
  const options = checkArray(problems, "options", value, 1);
  options?.forEach((option, index) => {
    checkOption(problems, `options[${index}]`, option);
  });
  return idsOf(options, "option_id");
}

/** revision oneOf: revision 1 has no parent; every later revision names one. */
function checkRevision(problems: Problems, value: unknown): void {
  const revision = checkObject(problems, "revision", value);
  if (!revision) return;
  checkKeys(problems, "revision", revision, ["number", "created_at", "parent"]);
  checkDateTime(problems, "revision.created_at", revision.created_at);
  const revisionNumber = revision.number;
  const parent = revision.parent;
  if (!(Number.isInteger(revisionNumber) && (revisionNumber as number) >= 1)) {
    problems.add("revision.number", "must be an integer of at least 1");
    return;
  }
  if (revisionNumber === 1 && parent !== null) {
    problems.add("revision.parent", "revision 1 has no parent");
  }
  if (revisionNumber !== 1 && !(Number.isInteger(parent) && (parent as number) >= 1)) {
    problems.add("revision.parent", "a revision after the first must name its parent revision");
  }
}

/** origin oneOf: a new study has no export id; a copied one names its export. */
function checkOrigin(problems: Problems, value: unknown): void {
  const origin = checkObject(problems, "origin", value);
  if (!origin) return;
  checkKeys(problems, "origin", origin, ["kind", "export_id"]);
  checkEnum(problems, "origin.kind", origin.kind, ORIGIN_KINDS);
  checkNullableNonEmptyString(problems, "origin.export_id", origin.export_id);
  if (origin.kind === "new" && origin.export_id !== null) {
    problems.add("origin.export_id", "must be null for a new study");
  }
  if (origin.kind === "copied_from_export" && origin.export_id === null) {
    problems.add("origin.export_id", "a study copied from an export must name the export");
  }
}

function checkUnique(
  problems: Problems,
  path: string,
  ids: readonly (string | null)[],
  message: string,
): void {
  const seen = new Set<string>();
  ids.forEach((id, index) => {
    if (id === null) return;
    if (seen.has(id)) problems.add(`${path}[${index}]`, message);
    seen.add(id);
  });
}

/** Validate a study document. Returns the typed study ONLY when every check passes. */
export function validateStudyDocument(body: unknown): StudyValidationResult {
  const problems = new Problems();
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return { ok: false, problems: ["study: document is not a JSON object"] };
  }
  const study = body as Record<string, unknown>;
  checkNoFixtureAnnotation(problems, "study", study);
  checkKeys(problems, "study", study, STUDY_REQUIRED_KEYS);
  checkEnum(problems, "contract_version", study.contract_version, STUDY_CONTRACT_VERSIONS);
  checkNonEmptyString(problems, "study_id", study.study_id);
  checkProperty(problems, study.property);
  checkLots(problems, study.lots);
  checkLotSelection(problems, study.lot_selection);
  const factIds = checkSite(problems, study.site);
  const optionIds = checkOptions(problems, study.options);
  checkNonEmptyString(problems, "selected_option_id", study.selected_option_id);
  checkRevision(problems, study.revision);
  checkOrigin(problems, study.origin);

  if (isNonEmptyString(study.selected_option_id) && !optionIds.includes(study.selected_option_id)) {
    problems.add("selected_option_id", "must name one of the study's options (plan section 9)");
  }
  checkUnique(problems, "options", optionIds, "option_id repeats another option's id");
  checkUnique(problems, "site.facts", factIds, "fact_id repeats another fact's id");

  if (problems.list.length > 0) return { ok: false, problems: problems.list };
  return { ok: true, study: body as unknown as Study };
}
