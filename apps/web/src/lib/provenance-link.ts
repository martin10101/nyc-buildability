/**
 * Safe outbound source links for provenance surfaces (task M5-T025, D-056-R001).
 *
 * The ONLY safe way to build a link to the official dataset landing page is a
 * client-side CONSTANT prefix plus a dataset id that has been through STRICT
 * token validation — mirroring the ZoLa constant-prefix + validated-token
 * pattern in AddressConfirmCard.tsx (G5 F-1 discipline: "the client
 * validation is the only guard", link built ONLY from a module constant plus
 * the re-validated value) and src/lib/bounded.ts's "drop the whole value
 * rather than half-sanitize" posture. The href is NEVER built from
 * `request_url` or any other server-echoed string — this module's only input
 * is a dataset id, so there is no code path by which a reflected string can
 * reach an href through it. An id that fails validation, or is absent,
 * renders an honest absence (the caller keeps its existing text), never a
 * guessed or partially-sanitized link.
 *
 * Socrata (NYC Open Data, data.cityofnewyork.us) dataset ids are exactly
 * four lowercase alphanumeric characters, a hyphen, then four more lowercase
 * alphanumeric characters (e.g. the PLUTO dataset id "64uk-42ks" —
 * services/api/app/connectors/pluto_soda.py DATASET_ID). The regex below
 * requires that EXACT shape, anchored at both ends — nothing else is
 * accepted, so a hostile or malformed value (including one that merely
 * CONTAINS a valid-looking id as a substring) can never reach the prefix.
 */

/** The one allowlisted, constant host+path prefix for a dataset landing page. */
export const DATASET_LANDING_PREFIX = "https://data.cityofnewyork.us/d/";

const SOCRATA_DATASET_ID_PATTERN = /^[a-z0-9]{4}-[a-z0-9]{4}$/;

/** True only for a string matching the exact Socrata 4-4 dataset-id shape. */
export function isValidDatasetId(value: unknown): value is string {
  return typeof value === "string" && SOCRATA_DATASET_ID_PATTERN.test(value);
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
