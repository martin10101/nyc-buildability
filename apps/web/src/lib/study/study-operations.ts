/**
 * Pure study operations (task C-05, plan M1-10; plan section 9 "One shared study
 * per property"). Each takes an entry and returns a new one; nothing here reads a
 * clock, the network or storage. The caller passes `at`, the RFC 3339 time of
 * the change, which becomes the new revision's created_at.
 *
 * Rules the operations keep:
 * - The site (lots, lot selection, site facts) is shared by every option: a site
 *   change marks every option's results out of date.
 * - An option change touches that option only: every other option object is
 *   reused by reference, so it stays byte-identical, and only that option is
 *   marked out of date.
 * - Every change to the study is a new revision (number + 1, parent = previous).
 *   An operation that changes nothing returns the same entry (no new revision).
 * - Every result is validated against the study contract before it is returned;
 *   an operation that would produce an invalid document changes nothing.
 * - Caller input is copied as strict JSON: a NaN or Infinity is refused, never
 *   rewritten to null (review correction 2).
 * - A document read from a file never becomes the current study directly: see
 *   ./study-import (plan section 9, nothing imported becomes a current fact).
 * - The store never invents option inputs (floor heights, program, existing
 *   building plan): they come from the caller, stated as defaults or entered.
 */

import {
  copyJson,
  deepFreeze,
  sameJson,
  studyFailure,
  type ParcelChoices,
  type StudyEntry,
  type StudyResult,
} from "./study-entry";
import { validateStudyDocument } from "./study-validator";
import {
  LOT_SELECTION_STATEMENT,
  type Lot,
  type LotSelection,
  type OptionInputs,
  type SiteFact,
  type SourceKind,
  type Study,
  type StudyOption,
  type StudyProperty,
} from "./study-vocabulary";

export interface NewOption {
  /** Defaults to the next free "option-<n>" id. */
  optionId?: string;
  name: string;
  inputs: OptionInputs;
}

export interface CreateStudyInput {
  studyId: string;
  property: StudyProperty;
  lots: Lot[];
  lotSelection: Pick<LotSelection, "mode" | "combination">;
  siteFacts: SiteFact[];
  initialOption: NewOption;
  /** Further options after the initial one. */
  moreOptions?: NewOption[];
  /** The option that drives the report; defaults to the initial option. */
  selectedOptionId?: string;
  /** "Start a new study from this": the export the inputs were copied from. Absent or null = a new study. */
  fromExportId?: string | null;
  at: string;
  parcelChoices?: ParcelChoices | null;
}

/** Which options a committed change marks out of date. */
type StaleMark = "all" | "none" | readonly string[];

/** Source kinds of a city value: an edit is a new fact, never an in-place overwrite (site_fact.schema.json `editable`). */
const CITY_SOURCE_KINDS: readonly SourceKind[] = ["city_dataset", "city_filing", "tax_map_computation"];

function ok(entry: StudyEntry): StudyResult {
  return { ok: true, entry };
}

function invalid(problems: readonly string[]): StudyResult {
  return studyFailure("invalid_document", "The change would make the study invalid; nothing was changed.", problems);
}

function unknownOption(): StudyResult {
  return studyFailure("unknown_option", "This option is not part of the study.");
}

function nonFinite(): StudyResult {
  return studyFailure(
    "invalid_document",
    "A number in the change is not finite (NaN or Infinity); nothing was changed.",
    ["input: a number is not finite (NaN or Infinity); JSON cannot carry it"],
  );
}

/** An option in contract key order (not yet copied: callers copy it with copyJson). */
function optionOf(optionId: string, name: string, inputs: OptionInputs): StudyOption {
  return {
    option_id: optionId,
    name,
    addon_selection: inputs.addon_selection,
    goal: inputs.goal,
    program: inputs.program,
    floor_to_floor_heights: inputs.floor_to_floor_heights,
    assumptions: inputs.assumptions,
    existing_building_plan: inputs.existing_building_plan,
  };
}

/** An option's inputs: everything but its id and name. */
export function optionInputsOf(option: StudyOption): OptionInputs {
  return {
    addon_selection: option.addon_selection,
    goal: option.goal,
    program: option.program,
    floor_to_floor_heights: option.floor_to_floor_heights,
    assumptions: option.assumptions,
    existing_building_plan: option.existing_building_plan,
  };
}

/** Validate, keep the stale flags in option order, and freeze. */
function finish(study: Study, stale: ReadonlySet<string>, parcelChoices: ParcelChoices | null): StudyResult {
  const checked = validateStudyDocument(study);
  if (!checked.ok) return invalid(checked.problems);
  const staleOptionIds = study.options.map((option) => option.option_id).filter((id) => stale.has(id));
  return ok(deepFreeze({ study, staleOptionIds, parcelChoices }));
}

/**
 * The one commit path: a new revision on top of `entry`, the stale flags
 * updated, the document validated. `nextStudy` carries the change; its revision
 * is replaced here. Module-private: every caller passes copied or frozen parts.
 */
function commitStudyChange(
  entry: StudyEntry,
  nextStudy: Study,
  at: string,
  markStale: StaleMark,
  parcelChoices: ParcelChoices | null = entry.parcelChoices,
): StudyResult {
  const previous = entry.study.revision.number;
  const study: Study = { ...nextStudy, revision: { number: previous + 1, created_at: at, parent: previous } };
  const stale = new Set(entry.staleOptionIds);
  if (markStale === "all") study.options.forEach((option) => stale.add(option.option_id));
  else if (markStale !== "none") markStale.forEach((id) => stale.add(id));
  return finish(study, stale, parcelChoices);
}

function freeOptionId(used: ReadonlySet<string>, start: number): string {
  let n = start;
  while (used.has(`option-${n}`)) n += 1;
  return `option-${n}`;
}

/** The next free "option-<n>" id. */
export function nextOptionId(study: Study): string {
  return freeOptionId(new Set(study.options.map((option) => option.option_id)), study.options.length + 1);
}

/** A new study (revision 1). Every option starts out of date: it has no results yet. */
export function createStudyEntry(input: CreateStudyInput): StudyResult {
  const options: StudyOption[] = [];
  const used = new Set<string>();
  for (const option of [input.initialOption, ...(input.moreOptions ?? [])]) {
    const optionId = option.optionId ?? freeOptionId(used, options.length + 1);
    used.add(optionId);
    options.push(optionOf(optionId, option.name, option.inputs));
  }
  const exportId = input.fromExportId;
  const study = copyJson<Study>({
    contract_version: "1.0.0",
    study_id: input.studyId,
    property: input.property,
    lots: input.lots,
    lot_selection: {
      mode: input.lotSelection.mode,
      statement: LOT_SELECTION_STATEMENT,
      combination: input.lotSelection.combination,
    },
    site: { facts: input.siteFacts },
    options,
    selected_option_id: input.selectedOptionId ?? options[0].option_id,
    revision: { number: 1, created_at: input.at, parent: null },
    origin:
      exportId === undefined || exportId === null
        ? { kind: "new", export_id: null }
        : { kind: "copied_from_export", export_id: exportId },
  });
  const parcelChoices = input.parcelChoices ? copyJson(input.parcelChoices) : null;
  if (study === null || (input.parcelChoices && parcelChoices === null)) return nonFinite();
  return finish(study, new Set(study.options.map((option) => option.option_id)), parcelChoices);
}

export function addOption(entry: StudyEntry, option: NewOption, at: string): StudyResult {
  const optionId = option.optionId ?? nextOptionId(entry.study);
  if (entry.study.options.some((existing) => existing.option_id === optionId)) {
    return studyFailure("duplicate_option_id", "Another option already uses this id.");
  }
  const added = copyJson(optionOf(optionId, option.name, option.inputs));
  if (added === null) return nonFinite();
  return commitStudyChange(entry, { ...entry.study, options: [...entry.study.options, added] }, at, [optionId]);
}

/** A copy of one option's inputs under a new id and name; the source option is untouched. */
export function duplicateOption(
  entry: StudyEntry,
  sourceOptionId: string,
  copy: { optionId?: string; name: string },
  at: string,
): StudyResult {
  const source = entry.study.options.find((option) => option.option_id === sourceOptionId);
  if (!source) return unknownOption();
  return addOption(entry, { optionId: copy.optionId, name: copy.name, inputs: optionInputsOf(source) }, at);
}

function replaceOption(
  entry: StudyEntry,
  optionId: string,
  change: (option: StudyOption) => StudyOption,
  at: string,
  markStale: StaleMark,
): StudyResult {
  const index = entry.study.options.findIndex((option) => option.option_id === optionId);
  if (index < 0) return unknownOption();
  const current = entry.study.options[index];
  const next = copyJson(change(current));
  if (next === null) return nonFinite();
  if (sameJson(next, current)) return ok(entry);
  const options = entry.study.options.map((option, position) => (position === index ? next : option));
  return commitStudyChange(entry, { ...entry.study, options }, at, markStale);
}

/** A new display name. Results do not depend on the name, so nothing goes out of date. */
export function renameOption(entry: StudyEntry, optionId: string, name: string, at: string): StudyResult {
  return replaceOption(entry, optionId, (option) => optionOf(option.option_id, name, optionInputsOf(option)), at, "none");
}

/**
 * Change one option's inputs. Only this option changes and only this option is
 * marked out of date (plan section 9: "Changing an option affects only that option").
 */
export function updateOptionInputs(
  entry: StudyEntry,
  optionId: string,
  patch: Partial<OptionInputs>,
  at: string,
): StudyResult {
  return replaceOption(
    entry,
    optionId,
    (option) => optionOf(option.option_id, option.name, { ...optionInputsOf(option), ...patch }),
    at,
    [optionId],
  );
}

/** Choose the option that drives the report (plan section 9). */
export function selectOption(entry: StudyEntry, optionId: string, at: string): StudyResult {
  if (!entry.study.options.some((option) => option.option_id === optionId)) return unknownOption();
  if (entry.study.selected_option_id === optionId) return ok(entry);
  return commitStudyChange(entry, { ...entry.study, selected_option_id: optionId }, at, "none");
}

function fromCity(fact: SiteFact): boolean {
  return fact.source !== null && CITY_SOURCE_KINDS.includes(fact.source.kind);
}

/**
 * Add a site fact, or replace the fact with the same fact_id. The site is shared,
 * so every option is marked out of date (plan section 9). A city value is never
 * overwritten in place by a non-city value: an architect's edit is a new fact
 * with its own id (site_fact.schema.json `editable`).
 */
export function upsertSiteFact(entry: StudyEntry, fact: SiteFact, at: string): StudyResult {
  const facts = entry.study.site.facts;
  const index = facts.findIndex((existing) => existing.fact_id === fact.fact_id);
  const next = copyJson(fact);
  if (next === null) return nonFinite();
  if (index >= 0) {
    if (sameJson(facts[index], next)) return ok(entry);
    if (fromCity(facts[index]) && !fromCity(next)) {
      return studyFailure(
        "city_fact_overwrite",
        "A city value is never overwritten in place. Record the edit as a new fact with its own id.",
      );
    }
  }
  const nextFacts = index >= 0 ? facts.map((existing, position) => (position === index ? next : existing)) : [...facts, next];
  return commitStudyChange(entry, { ...entry.study, site: { ...entry.study.site, facts: nextFacts } }, at, "all");
}

/** Remove a site fact; every option is marked out of date. */
export function removeSiteFact(entry: StudyEntry, factId: string, at: string): StudyResult {
  const facts = entry.study.site.facts;
  if (!facts.some((fact) => fact.fact_id === factId)) {
    return studyFailure("unknown_fact", "This site fact is not part of the study.");
  }
  const nextFacts = facts.filter((fact) => fact.fact_id !== factId);
  return commitStudyChange(entry, { ...entry.study, site: { ...entry.study.site, facts: nextFacts } }, at, "all");
}

/**
 * Replace the parcel-study form choices (the commit path of
 * ./parcel-study-adapter applyParcelStudyDraft, which validates the draft first).
 * They are site-level, so every option is marked out of date.
 */
export function setParcelChoices(entry: StudyEntry, choices: ParcelChoices, at: string): StudyResult {
  const next = copyJson(choices);
  if (next === null) return nonFinite();
  if (sameJson(next, entry.parcelChoices)) return ok(entry);
  return commitStudyChange(entry, entry.study, at, "all", next);
}

/**
 * Clear an option's out-of-date flag once its results were computed. Results
 * computed for an earlier revision never clear it (plan section 9: late
 * responses never overwrite newer ones). Not a new revision: the study itself
 * does not change.
 */
export function markOptionResultsCurrent(
  entry: StudyEntry,
  optionId: string,
  computedForRevision: number,
): StudyResult {
  if (!entry.study.options.some((option) => option.option_id === optionId)) return unknownOption();
  if (computedForRevision !== entry.study.revision.number) {
    return studyFailure(
      "stale_revision",
      "These results were computed for another revision; the option stays out of date.",
    );
  }
  if (!entry.staleOptionIds.includes(optionId)) return ok(entry);
  return ok(
    deepFreeze({
      study: entry.study,
      staleOptionIds: entry.staleOptionIds.filter((id) => id !== optionId),
      parcelChoices: entry.parcelChoices,
    }),
  );
}
