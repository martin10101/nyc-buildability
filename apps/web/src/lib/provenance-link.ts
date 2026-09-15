import type { Identity, Reproducibility, SourceFact } from "@/lib/contract";

/** Safe official links use constant prefixes and exact tokens, never request_url. */

/** The one allowlisted, constant host+path prefix for a dataset landing page. */
export const DATASET_LANDING_PREFIX = "https://data.cityofnewyork.us/d/";

const SOCRATA_DATASET_ID_PATTERN = /^[a-z0-9]{4}-[a-z0-9]{4}$/;
const PLUTO_SOURCE_ID = "nyc-dcp-pluto-soda";
const PLUTO_DATASET_ID = "64uk-42ks";
const PLUTO_RECORD_PREFIX = "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=";
const BBL_PATTERN = /^[1-5][0-9]{9}$/;

/** True only for a string matching the exact Socrata 4-4 dataset-id shape. */
export function isValidDatasetId(value: unknown): value is string {
  return typeof value === "string" && value.length === 9 && SOCRATA_DATASET_ID_PATTERN.test(value);
}

/**
 * Build the official dataset landing page URL from a validated dataset id.
 * Returns null (never a guessed or partial link) for anything that is not a
 * string in the exact validated shape — including an absent id, the common
 * case for provenance records that carry no `dataset_id` at all (e.g.
 * Zoning Resolution legal-text citations, which are not a Socrata dataset
 * and have no landing page this constant prefix could ever point at).
 */
export function datasetLandingUrl(datasetId: unknown): string | null {
  return isValidDatasetId(datasetId) ? `${DATASET_LANDING_PREFIX}${datasetId}` : null;
}

/** Current public PLUTO data, not an immutable copy of the captured source. */
export function plutoRecordUrl(sourceId: unknown, datasetId: unknown, bbl: unknown): string | null {
  return sourceId === PLUTO_SOURCE_ID && datasetId === PLUTO_DATASET_ID
    && typeof bbl === "string" && bbl.length === 10 && BBL_PATTERN.test(bbl)
    ? `${PLUTO_RECORD_PREFIX}${bbl}` : null;
}

/** Resolve only this fact's metadata; never borrow a different source's dataset. */
export function sourceFactLinks(
  record: Pick<SourceFact, "source_id" | "dataset_id" | "bbl">,
  reproducibility?: Pick<Reproducibility, "source_id" | "dataset_id">,
  identity?: Pick<Identity, "bbl">,
) {
  const sameSource = record.source_id === reproducibility?.source_id;
  const datasetId = record.dataset_id !== undefined
    ? record.dataset_id : sameSource ? reproducibility?.dataset_id : undefined;
  const datasetConflict = sameSource && record.dataset_id !== undefined
    && record.dataset_id !== reproducibility?.dataset_id;
  const identityMatches = identity === undefined || record.bbl === identity.bbl;
  return {
    datasetId,
    datasetUrl: datasetLandingUrl(datasetId),
    currentRecordUrl: identityMatches && !datasetConflict
      ? plutoRecordUrl(record.source_id, datasetId, record.bbl) : null,
  };
}
