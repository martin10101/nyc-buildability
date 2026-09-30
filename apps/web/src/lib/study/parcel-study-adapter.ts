/**
 * Lossless adapter between the parcel-study form (src/lib/architect/parcel-study.ts,
 * ParcelStudyDraft) and the shared study (task C-05, plan M1-10).
 *
 * What goes where:
 * - The property and its recorded base lots become the study's `property` and
 *   `lots` (every base lot selected; its size stays unknown until site setup
 *   fills it, never 0 - plan section 9).
 * - The form choices the v1 study contract has no field for (arrangement,
 *   building scheme, per-lot existing-building intent, and the entered and
 *   billing identities) travel beside the document as `parcelChoices`.
 * Rebuilding the draft from an entry gives back exactly the draft that
 * parcel-study.ts writes (its canonical form), so nothing is lost either way.
 *
 * Never inferred here: whether the lots can be combined (plan section 3 step 2:
 * one block and touching - site setup decides, M1-13) and the option inputs
 * (floor heights, program, existing-building plan). The caller supplies both.
 */

import {
  PARCEL_STUDY_VERSION,
  deriveParcelStudyScope,
  importParcelStudy,
  type ParcelStudyDraft,
  type ParcelStudyScope,
} from "../architect/parcel-study";
import {
  sameJson,
  studyFailure,
  type ParcelChoices,
  type StudyEntry,
  type StudyErrorCode,
  type StudyResult,
} from "./study-entry";
import { commitStudyChange, createStudyEntry, type NewOption } from "./study-operations";
import { MEASUREMENT_LABELS, type Combination, type SiteFact } from "./study-vocabulary";

export interface ParcelStudyInit {
  studyId: string;
  /** Confirmed address as displayed; null when found by BBL only. */
  address: string | null;
  /** Whether the lots can be combined, decided by site setup - never inferred here. */
  combination: Combination;
  siteFacts?: SiteFact[];
  initialOption: NewOption;
  at: string;
}

export type ParcelDraftResult =
  | { ok: true; draft: ParcelStudyDraft }
  | { ok: false; code: StudyErrorCode; message: string };

/**
 * The BBL a parcel study's shared study is stored under: the condo billing BBL
 * when the records name one (study.schema.json property: "For a condominium this
 * is the billing BBL"), otherwise the entered BBL.
 */
export function parcelStudyPropertyBbl(scope: ParcelStudyScope): string {
  return scope.billingBbl ?? scope.enteredBbl;
}

/** The draft in parcel-study.ts canonical form, validated against `scope`. */
function canonicalDraft(draft: ParcelStudyDraft, scope: ParcelStudyScope): ParcelDraftResult {
  const result = importParcelStudy(JSON.stringify(draft), scope);
  if (result.ok) return { ok: true, draft: result.draft };
  const code: StudyErrorCode = result.code === "scope_changed" ? "parcel_scope_changed" : "invalid_parcel_draft";
  return { ok: false, code, message: result.message };
}

function choicesOf(draft: ParcelStudyDraft): ParcelChoices {
  return {
    enteredBbl: draft.scope.enteredBbl,
    billingBbl: draft.scope.billingBbl,
    arrangement: draft.arrangement,
    buildingScheme: draft.buildingScheme,
    existingBuildings: draft.existingBuildings.map((entry) => ({ bbl: entry.bbl, intent: entry.intent })),
  };
}

/** A new shared study (revision 1) for the property and base lots of a parcel-study draft. */
export function studyEntryFromParcelStudyDraft(draft: ParcelStudyDraft, init: ParcelStudyInit): StudyResult {
  const checked = canonicalDraft(draft, draft.scope);
  if (!checked.ok) return studyFailure(checked.code, checked.message);
  const canonical = checked.draft;
  return createStudyEntry({
    studyId: init.studyId,
    property: { bbl: parcelStudyPropertyBbl(canonical.scope), address: init.address },
    lots: canonical.scope.baseBbls.map((bbl) => ({
      bbl,
      approximate_lot_area_sq_ft: null,
      size_measurement: { rank: "unknown", label: MEASUREMENT_LABELS.unknown },
      selected: true,
    })),
    lotSelection: { mode: "all", combination: init.combination },
    siteFacts: init.siteFacts ?? [],
    initialOption: init.initialOption,
    at: init.at,
    parcelChoices: choicesOf(canonical),
  });
}

/** Rebuild the parcel-study draft from a shared study entry. */
export function parcelStudyDraftFromStudyEntry(entry: StudyEntry): ParcelDraftResult {
  const choices = entry.parcelChoices;
  if (!choices) {
    return { ok: false, code: "not_a_parcel_study", message: "This study was not started from a parcel study." };
  }
  const scope = deriveParcelStudyScope({
    enteredBbl: choices.enteredBbl,
    billingBbl: choices.billingBbl,
    baseLots: entry.study.lots.map((lot) => ({ bbl: lot.bbl })),
  });
  if (!scope.ok) return { ok: false, code: "invalid_parcel_draft", message: scope.message };
  const draft: ParcelStudyDraft = {
    kind: "parcel_study",
    version: PARCEL_STUDY_VERSION,
    scope: scope.scope,
    arrangement: choices.arrangement,
    buildingScheme: choices.buildingScheme,
    existingBuildings: choices.existingBuildings.map((item) => ({ bbl: item.bbl, intent: item.intent })),
  };
  return canonicalDraft(draft, scope.scope);
}

/**
 * Apply an edited or restored parcel-study draft to the shared study. The draft
 * must belong to the same property and base lots. These choices are site-level,
 * so every option is marked out of date.
 */
export function applyParcelStudyDraft(entry: StudyEntry, draft: ParcelStudyDraft, at: string): StudyResult {
  const current = parcelStudyDraftFromStudyEntry(entry);
  if (!current.ok) return studyFailure(current.code, current.message);
  const next = canonicalDraft(draft, current.draft.scope);
  if (!next.ok) return studyFailure(next.code, next.message);
  const choices = choicesOf(next.draft);
  if (sameJson(choices, entry.parcelChoices)) return { ok: true, entry };
  return commitStudyChange(entry, entry.study, at, "all", choices);
}
