/**
 * What the study store holds per property (task C-05, plan M1-10): the
 * contract-shaped study document plus two things the v1 contract does not carry.
 *
 * - `staleOptionIds`: options whose results are missing or out of date. C-05
 *   keeps this as a plain flag per option (a site change marks every option, an
 *   option change marks that option only; plan section 9). Dependency-based
 *   invalidation (which result depends on which fact) is C-06 (plan M1-11).
 * - `parcelChoices`: the parcel-study form choices (arrangement, building scheme,
 *   per-lot existing-building intent) that study.schema.json has no field for.
 *   They sit beside the document so the ParcelStudyDraft adapter is lossless;
 *   they are never exported as part of the contract document.
 *
 * Entries are immutable: every operation returns a new entry that reuses the
 * unchanged parts by reference and is deep-frozen, so a consumer cannot edit
 * the shared study in place.
 */

import type {
  ParcelStudyArrangement,
  ParcelStudyBuildingScheme,
  ParcelStudyExistingBuildingIntent,
} from "../architect/parcel-study";
import type { Study } from "./study-vocabulary";

export interface ParcelChoices {
  readonly enteredBbl: string;
  readonly billingBbl: string | null;
  readonly arrangement: ParcelStudyArrangement;
  readonly buildingScheme: ParcelStudyBuildingScheme;
  readonly existingBuildings: readonly {
    readonly bbl: string;
    readonly intent: ParcelStudyExistingBuildingIntent;
  }[];
}

export interface StudyEntry {
  readonly study: Study;
  /** option_ids whose results are missing or out of date, in option order. */
  readonly staleOptionIds: readonly string[];
  /** Parcel-study form choices outside the contract; null when not created from a parcel study. */
  readonly parcelChoices: ParcelChoices | null;
}

export type StudyErrorCode =
  | "invalid_document"
  | "unknown_option"
  | "duplicate_option_id"
  | "unknown_fact"
  | "city_fact_overwrite"
  | "stale_revision"
  | "not_a_parcel_study"
  | "invalid_parcel_draft"
  | "parcel_scope_changed"
  | "no_study"
  | "wrong_property";

export type StudyFailure = {
  ok: false;
  code: StudyErrorCode;
  message: string;
  problems: readonly string[];
};

export type StudyResult = { ok: true; entry: StudyEntry } | StudyFailure;

export function studyFailure(
  code: StudyErrorCode,
  message: string,
  problems: readonly string[] = [],
): StudyFailure {
  return { ok: false, code, message, problems };
}

export function isOptionStale(entry: StudyEntry, optionId: string): boolean {
  return entry.staleOptionIds.includes(optionId);
}

export function selectedOption(entry: StudyEntry): Study["options"][number] | null {
  return entry.study.options.find((option) => option.option_id === entry.study.selected_option_id) ?? null;
}

/**
 * Copy JSON-shaped data so the store never shares an object with its caller.
 * Returns null when the data holds a number JSON cannot carry (NaN, Infinity):
 * JSON.stringify would silently write it as null, turning an invalid number
 * into a valid "no value", so it is refused instead (strict JSON, as the
 * server-side validator requires).
 */
export function copyJson<T>(value: T): T | null {
  let finite = true;
  const text = JSON.stringify(value, (_key: string, item: unknown) => {
    if (typeof item === "number" && !Number.isFinite(item)) finite = false;
    return item;
  });
  return finite && typeof text === "string" ? (JSON.parse(text) as T) : null;
}

export function sameJson(left: unknown, right: unknown): boolean {
  return JSON.stringify(left) === JSON.stringify(right);
}

/** Freeze every not-yet-frozen object reachable from `value` (frozen subtrees are already whole). */
export function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const key of Object.keys(value)) {
      deepFreeze((value as Record<string, unknown>)[key]);
    }
  }
  return value;
}
