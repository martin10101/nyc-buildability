/**
 * User-authored parcel study choices only. No geometry, zoning calculation,
 * site confirmation, source facts, network calls, or persistent storage.
 * The versioned exchange format is this form's state, not a property report.
 */
export const PARCEL_STUDY_VERSION = 1;
export const MAX_PARCEL_STUDY_JSON_LENGTH = 65_536;

export type ParcelStudyArrangement = "together" | "separate" | "compare";
export type ParcelStudyBuildingScheme = "undecided" | "one" | "multiple";
export type ParcelStudyExistingBuildingIntent = "undecided" | "retain" | "alter" | "demolish";

export interface ParcelStudyScope {
  key: string;
  enteredBbl: string;
  billingBbl: string | null;
  /** Display order follows the current records; membership comparison is sorted. */
  baseBbls: string[];
}

export interface ParcelStudyExistingBuilding {
  bbl: string;
  intent: ParcelStudyExistingBuildingIntent;
}

export interface ParcelStudyDraft {
  kind: "parcel_study";
  version: typeof PARCEL_STUDY_VERSION;
  scope: ParcelStudyScope;
  arrangement: ParcelStudyArrangement;
  /** Applies only to the combined study; never establishes an existing count. */
  buildingScheme: ParcelStudyBuildingScheme;
  existingBuildings: ParcelStudyExistingBuilding[];
}

export interface ParcelStudySite {
  id: string;
  baseBbls: string[];
  buildingScheme: ParcelStudyBuildingScheme | null;
  existingBuildings: ParcelStudyExistingBuilding[];
}

export interface ParcelStudyScenario {
  id: "combined" | "separate";
  sites: ParcelStudySite[];
}

export interface ParcelStudyError {
  ok: false;
  code: "invalid_records" | "invalid_draft" | "scope_changed" | "invalid_json" | "too_large";
  message: string;
}

export const PARCEL_STUDY_BOUNDARIES = {
  legalSite: "A study choice does not establish or divide a legal zoning lot. Existing zoning-lot arrangements need review.",
  envelope: "Height, footprint, yards and floor-area results need supported rules and site inputs. These choices do not supply missing calculations.",
} as const;

function record(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null;
}

function exactKeys(value: Record<string, unknown>, keys: string[]): boolean {
  return Object.keys(value).length === keys.length
    && keys.every((key) => Object.prototype.hasOwnProperty.call(value, key));
}

function canonicalBbl(value: unknown): value is string {
  return typeof value === "string" && /^[1-5][0-9]{9}$/.test(value)
    && value.slice(1, 6) !== "00000" && value.slice(6) !== "0000";
}

function scopeKey(enteredBbl: string, billingBbl: string | null, baseBbls: string[]): string {
  return [enteredBbl, billingBbl ?? "unknown", [...baseBbls].sort().join(",")].join("|");
}

function fail(code: ParcelStudyError["code"], message: string): ParcelStudyError {
  return { ok: false, code, message };
}

/** Reject the complete ambiguous set; never silently remove a bad or repeated row. */
export function deriveParcelStudyScope(input: unknown): { ok: true; scope: ParcelStudyScope } | ParcelStudyError {
  const source = record(input);
  if (!source || !canonicalBbl(source.enteredBbl)
    || (source.billingBbl !== null && !canonicalBbl(source.billingBbl))
    || !Array.isArray(source.baseLots) || source.baseLots.length < 2) {
    return fail("invalid_records", "A parcel study needs the entered property identity and at least two valid recorded base lots.");
  }
  const baseBbls: string[] = [];
  const seen = new Set<string>();
  for (const lot of source.baseLots) {
    const bbl = record(lot)?.bbl;
    if (!canonicalBbl(bbl)) {
      return fail("invalid_records", "A recorded base-lot identity is missing or invalid. The parcel set needs review.");
    }
    if (bbl === source.enteredBbl || bbl === source.billingBbl) {
      return fail("invalid_records", "The entered condo or billing identity also appears as a base lot. The parcel set needs review.");
    }
    if (seen.has(bbl)) {
      return fail("invalid_records", "A base lot is repeated in the city records. The parcel set needs review.");
    }
    seen.add(bbl);
    baseBbls.push(bbl);
  }
  const enteredBbl = source.enteredBbl;
  const billingBbl = source.billingBbl as string | null;
  return { ok: true, scope: { enteredBbl, billingBbl, baseBbls, key: scopeKey(enteredBbl, billingBbl, baseBbls) } };
}

export function createParcelStudy(scope: ParcelStudyScope): ParcelStudyDraft {
  return {
    kind: "parcel_study",
    version: PARCEL_STUDY_VERSION,
    scope: { ...scope, baseBbls: [...scope.baseBbls] },
    arrangement: "compare",
    buildingScheme: "undecided",
    existingBuildings: scope.baseBbls.map((bbl) => ({ bbl, intent: "undecided" })),
  };
}

function parsedScope(value: unknown): ParcelStudyScope | null {
  const input = record(value);
  if (!input || !exactKeys(input, ["key", "enteredBbl", "billingBbl", "baseBbls"])
    || !Array.isArray(input.baseBbls)) return null;
  const result = deriveParcelStudyScope({
    enteredBbl: input.enteredBbl,
    billingBbl: input.billingBbl,
    baseLots: input.baseBbls.map((bbl: unknown) => ({ bbl })),
  });
  return result.ok && input.key === result.scope.key ? result.scope : null;
}

export function parcelStudyMatchesScope(draft: ParcelStudyDraft, scope: ParcelStudyScope): boolean {
  const previous = parsedScope(draft.scope);
  const current = parsedScope(scope);
  return previous !== null && current !== null && previous.key === current.key;
}

/** Every group is proposed, never a determination of legal site membership. */
export function deriveParcelStudyScenarios(draft: ParcelStudyDraft): ParcelStudyScenario[] {
  const sites: ParcelStudyScenario[] = [];
  if (draft.arrangement !== "separate") {
    sites.push({ id: "combined", sites: [{
      id: "combined",
      baseBbls: [...draft.scope.baseBbls],
      buildingScheme: draft.buildingScheme,
      existingBuildings: draft.existingBuildings.map((entry) => ({ ...entry })),
    }] });
  }
  if (draft.arrangement !== "together") {
    sites.push({ id: "separate", sites: draft.scope.baseBbls.map((bbl) => ({
      id: bbl,
      baseBbls: [bbl],
      buildingScheme: null,
      existingBuildings: draft.existingBuildings.filter((entry) => entry.bbl === bbl).map((entry) => ({ ...entry })),
    })) });
  }
  return sites;
}

function validateDraft(value: unknown, scope: ParcelStudyScope): { ok: true; draft: ParcelStudyDraft } | ParcelStudyError {
  const input = record(value);
  if (!input || !exactKeys(input, ["kind", "version", "scope", "arrangement", "buildingScheme", "existingBuildings"])
    || input.kind !== "parcel_study" || input.version !== PARCEL_STUDY_VERSION
    || !["together", "separate", "compare"].includes(input.arrangement as string)
    || !["undecided", "one", "multiple"].includes(input.buildingScheme as string)
    || !Array.isArray(input.existingBuildings)) {
    return fail("invalid_draft", "This file is not a supported parcel study. Only study choices can be restored.");
  }
  const importedScope = parsedScope(input.scope);
  const currentScope = parsedScope(scope);
  if (!importedScope || !currentScope) {
    return fail("invalid_draft", "The study contains an invalid or ambiguous parcel identity.");
  }
  if (importedScope.key !== currentScope.key) {
    return fail("scope_changed", "This study belongs to a different property or parcel set. Start a new study using the current records.");
  }
  const intents = new Map<string, ParcelStudyExistingBuildingIntent>();
  for (const value of input.existingBuildings) {
    const entry = record(value);
    if (!entry || !exactKeys(entry, ["bbl", "intent"]) || !canonicalBbl(entry.bbl)
      || !currentScope.baseBbls.includes(entry.bbl) || intents.has(entry.bbl)
      || !["undecided", "retain", "alter", "demolish"].includes(entry.intent as string)) {
      return fail("invalid_draft", "Existing-building choices must list each recorded base lot once, with a supported choice.");
    }
    intents.set(entry.bbl, entry.intent as ParcelStudyExistingBuildingIntent);
  }
  if (intents.size !== currentScope.baseBbls.length) {
    return fail("invalid_draft", "An existing-building choice is missing for a recorded base lot.");
  }
  return { ok: true, draft: {
    kind: "parcel_study",
    version: PARCEL_STUDY_VERSION,
    scope: currentScope,
    arrangement: input.arrangement as ParcelStudyArrangement,
    buildingScheme: input.buildingScheme as ParcelStudyBuildingScheme,
    existingBuildings: currentScope.baseBbls.map((bbl) => ({ bbl, intent: intents.get(bbl)! })),
  } };
}

export function exportParcelStudy(draft: ParcelStudyDraft, scope: ParcelStudyScope): { ok: true; json: string } | ParcelStudyError {
  const result = validateDraft(draft, scope);
  if (!result.ok) return result;
  const json = JSON.stringify(result.draft, null, 2);
  return json.length <= MAX_PARCEL_STUDY_JSON_LENGTH
    ? { ok: true, json }
    : fail("too_large", "This parcel study is too large to download in the supported format.");
}

export function importParcelStudy(json: string, scope: ParcelStudyScope): { ok: true; draft: ParcelStudyDraft } | ParcelStudyError {
  if (json.length > MAX_PARCEL_STUDY_JSON_LENGTH) {
    return fail("too_large", "This file is too large to be a supported parcel study.");
  }
  let value: unknown;
  try {
    value = JSON.parse(json);
  } catch {
    return fail("invalid_json", "This file is not valid JSON. Choose a downloaded parcel study file.");
  }
  return validateDraft(value, scope);
}
