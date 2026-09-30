/**
 * The study's JSON boundary (task C-05, plan M1-10): export and import of the
 * contract document, each validated against study.schema.json (the runtime
 * mirror in ./study-validator). An invalid document is never written and never
 * accepted; the caller receives only the bounded problem list.
 *
 * Only the contract document crosses this boundary. The store's out-of-date
 * flags and parcel-study choices are not part of the contract and are not
 * exported. An imported document is a shape-checked study, nothing more: it
 * carries no results, and restoring a HISTORICAL export (copy inputs, re-fetch
 * facts, recalculate - plan section 9) is the export-record path, not this one.
 */

import { validateStudyDocument } from "./study-validator";
import type { Study } from "./study-vocabulary";

/** Upper bound on a study file; a longer text is rejected before parsing. */
export const MAX_STUDY_JSON_LENGTH = 1_048_576;

export type StudyExportResult =
  | { ok: true; json: string }
  | { ok: false; code: "invalid_document" | "too_large"; problems: readonly string[] };

export type StudyImportResult =
  | { ok: true; study: Study }
  | {
      ok: false;
      code: "too_large" | "invalid_json" | "invalid_document" | "wrong_property";
      problems: readonly string[];
    };

export function exportStudyJson(study: Study): StudyExportResult {
  const checked = validateStudyDocument(study);
  if (!checked.ok) return { ok: false, code: "invalid_document", problems: checked.problems };
  const json = JSON.stringify(study, null, 2);
  if (json.length > MAX_STUDY_JSON_LENGTH) {
    return { ok: false, code: "too_large", problems: ["study: the document exceeds the supported file size"] };
  }
  return { ok: true, json };
}

/**
 * Parse and validate a study file. When `expectedBbl` is given, a study for
 * another property is refused (a study belongs to one property, plan section 9).
 */
export function importStudyJson(json: string, expectedBbl?: string): StudyImportResult {
  if (json.length > MAX_STUDY_JSON_LENGTH) {
    return { ok: false, code: "too_large", problems: ["study: the file exceeds the supported file size"] };
  }
  let value: unknown;
  try {
    value = JSON.parse(json);
  } catch {
    return { ok: false, code: "invalid_json", problems: ["study: the file is not valid JSON"] };
  }
  const checked = validateStudyDocument(value);
  if (!checked.ok) return { ok: false, code: "invalid_document", problems: checked.problems };
  if (expectedBbl !== undefined && checked.study.property.bbl !== expectedBbl) {
    return { ok: false, code: "wrong_property", problems: ["property.bbl: the study belongs to another property"] };
  }
  return { ok: true, study: checked.study };
}
