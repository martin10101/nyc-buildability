/**
 * "Start a new study from this" (plan section 9 "Historical exports"; task C-05,
 * review correction 1). A study read from a file is never installed as the
 * current study: "Nothing imported becomes a current fact or result." Only the
 * architect's INPUTS are copied into a new study:
 * - the options (add-on selections, goal, program, floor-to-floor heights,
 *   assumptions, existing-building plan) and which option is selected;
 * - the lots, which of them are selected, and the lot-selection mode;
 * - site values the architect supplied: ranks 'survey_entered', 'entered' and
 *   'assumed' (the labeled input channel, plan task M1-08).
 * Everything else is a FACT and is re-fetched by site setup, never copied:
 * city-sourced values ('City records', 'Approximate — tax map'), 'Unknown'
 * placeholders, lot sizes the architect did not supply, and whether the lots
 * can be combined (the caller passes the combination site setup re-derived).
 *
 * The new study has a new id, starts at revision 1, names the export it was
 * copied from when there is one (origin 'copied_from_export'), and every option
 * is out of date: no result is imported.
 */

import { studyFailure, type StudyResult } from "./study-entry";
import { createStudyEntry, optionInputsOf } from "./study-operations";
import { validateStudyDocument } from "./study-validator";
import {
  MEASUREMENT_LABELS,
  type Combination,
  type Lot,
  type MeasurementRank,
  type SiteFact,
  type Study,
} from "./study-vocabulary";

/** Ranks of values the architect supplies; every other rank is a fact that is re-fetched. */
export const ARCHITECT_INPUT_RANKS: readonly MeasurementRank[] = ["survey_entered", "entered", "assumed"];

export interface StartFromImportInput {
  /** Id of the NEW study (a copy is a new study, never the file's study). */
  studyId: string;
  at: string;
  /** The export the file came from, or null for a plain study file (origin 'new'). */
  exportId: string | null;
  /** Whether the lots can be combined, re-derived by site setup - never taken from the file. */
  combination: Combination;
}

export function isArchitectInput(rank: MeasurementRank): boolean {
  return ARCHITECT_INPUT_RANKS.includes(rank);
}

/** The site facts of an imported study that are NOT copied: site setup re-fetches them. */
export function factsToRefetch(document: Study): SiteFact[] {
  return document.site.facts.filter((fact) => !isArchitectInput(fact.measurement.rank));
}

/** A lot's selection is an input; its size is kept only when the architect supplied it. */
function lotInput(lot: Lot): Lot {
  if (isArchitectInput(lot.size_measurement.rank)) return lot;
  return {
    bbl: lot.bbl,
    approximate_lot_area_sq_ft: null,
    size_measurement: { rank: "unknown", label: MEASUREMENT_LABELS.unknown },
    selected: lot.selected,
  };
}

/** A new study holding only the inputs of `document` (a validated file). */
export function startStudyFromImport(document: Study, input: StartFromImportInput): StudyResult {
  const checked = validateStudyDocument(document);
  if (!checked.ok) {
    return studyFailure("invalid_document", "The file is not a valid study; nothing was started.", checked.problems);
  }
  const [first, ...rest] = document.options.map((option) => ({
    optionId: option.option_id,
    name: option.name,
    inputs: optionInputsOf(option),
  }));
  return createStudyEntry({
    studyId: input.studyId,
    property: document.property,
    lots: document.lots.map(lotInput),
    lotSelection: { mode: document.lot_selection.mode, combination: input.combination },
    siteFacts: document.site.facts.filter((fact) => isArchitectInput(fact.measurement.rank)),
    initialOption: first,
    moreOptions: rest,
    selectedOptionId: document.selected_option_id,
    fromExportId: input.exportId,
    at: input.at,
  });
}
