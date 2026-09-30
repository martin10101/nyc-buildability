/**
 * Runtime mirror of packages/contracts/schemas/v1/site_fact.schema.json for the
 * web study store (task C-05, plan M1-10). One site value is either KNOWN (a
 * value with its unit, one of five measurement ranks and a source whose kind can
 * produce that rank) or UNKNOWN (value and unit null, rank 'unknown', and a
 * non-empty list of what it blocks). An unknown is never 0: dimensions are
 * strictly positive (plan section 9 "Unknowns stay unknown").
 *
 * Every rule below cites the schema clause it mirrors; this module checks SHAPE,
 * never meaning, and never rewrites a value.
 */

import {
  Problems,
  checkBoolean,
  checkEnum,
  checkNonEmptyString,
  isNonEmptyString,
} from "../scenario-contract-checks";
import {
  checkArray,
  checkDateTime,
  checkKeys,
  checkNoFixtureAnnotation,
  checkNullableBbl,
  checkNullableNonEmptyString,
  checkObject,
  isJsonNumber,
  isOneOf,
} from "./study-checks";
import {
  BLOCKED_OUTPUTS,
  LOT_TYPE_VALUES,
  MEASUREMENT_LABELS,
  MEASUREMENT_RANKS,
  SITE_FACT_CONTRACT_VERSIONS,
  SITE_FACT_KEYS,
  SITE_FACT_UNITS,
  SOURCE_KINDS,
  type MeasurementRank,
  type SourceKind,
} from "./study-vocabulary";

const SITE_FACT_REQUIRED_KEYS = [
  "contract_version",
  "fact_id",
  "key",
  "lot_bbl",
  "street",
  "value",
  "unit",
  "measurement",
  "source",
  "blocks",
  "editable",
] as const;

const SOURCE_REQUIRED_KEYS = [
  "kind",
  "dataset",
  "dataset_version",
  "retrieved_at",
  "query_ref",
  "document_ref",
  "statement",
] as const;

type SourceTextField = "dataset" | "query_ref" | "document_ref" | "statement";

/** source oneOf: the fields each kind must carry as non-empty text. */
const SOURCE_KIND_REQUIRED_FIELDS: { readonly [K in SourceKind]: readonly SourceTextField[] } = {
  city_dataset: ["dataset", "query_ref"],
  tax_map_computation: ["dataset", "query_ref"],
  city_filing: ["dataset", "document_ref"],
  survey: ["document_ref"],
  architect_entry: [],
  assumption: ["statement"],
};

/** Rank rules (allOf[0]): the source kinds that can produce each known rank. */
const RANK_SOURCE_KINDS: { readonly [R in Exclude<MeasurementRank, "unknown">]: readonly SourceKind[] } = {
  survey_entered: ["survey"],
  city_records: ["city_dataset", "city_filing"],
  approximate_tax_map: ["tax_map_computation"],
  entered: ["architect_entry"],
  assumed: ["assumption"],
};

/** Key rules (allOf[1]): existing zoning floor area never comes from a city dataset. */
const EXISTING_ZFA_SOURCE_KINDS: readonly SourceKind[] = ["city_filing", "architect_entry", "assumption"];

/** measurement oneOf: a rank with exactly its tied label. Returns the rank, or null when invalid. */
export function checkMeasurement(
  problems: Problems,
  path: string,
  value: unknown,
): MeasurementRank | null {
  const measurement = checkObject(problems, path, value);
  if (!measurement) return null;
  checkKeys(problems, path, measurement, ["rank", "label"]);
  if (!isOneOf(MEASUREMENT_RANKS, measurement.rank)) {
    checkEnum(problems, `${path}.rank`, measurement.rank, MEASUREMENT_RANKS);
    return null;
  }
  const rank = measurement.rank as MeasurementRank;
  if (measurement.label !== MEASUREMENT_LABELS[rank]) {
    problems.add(`${path}.label`, "must be the display label tied to its rank (plan section 4 table)");
  }
  return rank;
}

/**
 * source: an object or null. Returns the kind, null for an explicit null
 * source, or undefined when the source is invalid (already reported).
 */
function checkNullableSource(
  problems: Problems,
  path: string,
  value: unknown,
): SourceKind | null | undefined {
  if (value === null) return null;
  const source = checkObject(problems, path, value);
  if (!source) return undefined;
  checkKeys(problems, path, source, SOURCE_REQUIRED_KEYS, ["provenance_refs"]);
  for (const field of ["dataset", "dataset_version", "query_ref", "document_ref", "statement"]) {
    checkNullableNonEmptyString(problems, `${path}.${field}`, source[field]);
  }
  checkDateTime(problems, `${path}.retrieved_at`, source.retrieved_at);
  if (source.provenance_refs !== undefined) {
    const refs = checkArray(problems, `${path}.provenance_refs`, source.provenance_refs);
    refs?.forEach((ref, index) => {
      checkNonEmptyString(problems, `${path}.provenance_refs[${index}]`, ref);
    });
  }
  if (!isOneOf(SOURCE_KINDS, source.kind)) {
    checkEnum(problems, `${path}.kind`, source.kind, SOURCE_KINDS);
    return undefined;
  }
  const kind = source.kind as SourceKind;
  for (const field of SOURCE_KIND_REQUIRED_FIELDS[kind]) {
    if (!isNonEmptyString(source[field])) {
      problems.add(`${path}.${field}`, "is required for this source kind");
    }
  }
  return kind;
}

/** Rank rules (allOf[0]). */
function checkRankRule(
  problems: Problems,
  path: string,
  fact: Record<string, unknown>,
  rank: MeasurementRank,
  sourceKind: SourceKind | null | undefined,
): void {
  const blocks = Array.isArray(fact.blocks) ? fact.blocks : null;
  if (rank === "unknown") {
    if (fact.value !== null) problems.add(`${path}.value`, "must be null while the value is unknown");
    if (fact.unit !== null) problems.add(`${path}.unit`, "must be null while the value is unknown");
    if (blocks !== null && blocks.length === 0) {
      problems.add(`${path}.blocks`, "an unknown value must name what it blocks (plan section 9)");
    }
    return;
  }
  if (fact.value === null) {
    problems.add(`${path}.value`, "a known value is never null; use rank 'unknown' (plan section 9)");
  }
  if (sourceKind !== undefined && (sourceKind === null || !RANK_SOURCE_KINDS[rank].includes(sourceKind))) {
    problems.add(`${path}.source`, "a known value needs a source whose kind can produce its rank");
  }
  if (blocks !== null && blocks.length > 0) {
    problems.add(`${path}.blocks`, "must be empty for a known value");
  }
}

/** A dimension: a positive number in its unit, or null with a null unit (never 0). */
function checkDimension(
  problems: Problems,
  path: string,
  fact: Record<string, unknown>,
  unit: "square_feet" | "feet",
): void {
  const known = isJsonNumber(fact.value) && fact.value > 0 && fact.unit === unit;
  const unknown = fact.value === null && fact.unit === null;
  if (!known && !unknown) {
    problems.add(
      `${path}.value`,
      `must be a number greater than 0 in ${unit}, or null with a null unit (never 0)`,
    );
  }
}

function checkNullStreet(problems: Problems, path: string, fact: Record<string, unknown>): void {
  if (fact.street !== null) problems.add(`${path}.street`, "must be null for this key");
}

function checkNullUnit(problems: Problems, path: string, fact: Record<string, unknown>): void {
  if (fact.unit !== null) problems.add(`${path}.unit`, "must be null for this key");
}

/** Key rules (allOf[1]). */
function checkKeyRule(
  problems: Problems,
  path: string,
  fact: Record<string, unknown>,
  sourceKind: SourceKind | null | undefined,
): void {
  switch (fact.key) {
    case "lot_area":
      checkNullStreet(problems, path, fact);
      checkDimension(problems, path, fact, "square_feet");
      return;
    case "lot_frontage":
    case "street_width":
      if (!isNonEmptyString(fact.street)) {
        problems.add(`${path}.street`, "is required for a per-street value");
      }
      checkDimension(problems, path, fact, "feet");
      return;
    case "lot_depth":
      checkNullStreet(problems, path, fact);
      checkDimension(problems, path, fact, "feet");
      return;
    case "lot_type":
      checkNullStreet(problems, path, fact);
      checkNullUnit(problems, path, fact);
      if (!(fact.value === null || isOneOf(LOT_TYPE_VALUES, fact.value))) {
        problems.add(`${path}.value`, `must be one of ${LOT_TYPE_VALUES.join(", ")}, or null`);
      }
      return;
    case "zoning_district":
    case "commercial_overlay":
      checkNullStreet(problems, path, fact);
      checkNullUnit(problems, path, fact);
      if (!(fact.value === null || isNonEmptyString(fact.value))) {
        problems.add(`${path}.value`, "must be a non-empty string or null");
      }
      return;
    case "existing_zoning_floor_area":
      checkNullStreet(problems, path, fact);
      if (sourceKind !== undefined && sourceKind !== null && !EXISTING_ZFA_SOURCE_KINDS.includes(sourceKind)) {
        problems.add(
          `${path}.source`,
          "existing zoning floor area comes only from a filing, an architect entry or a stated assumption",
        );
      }
      checkDimension(problems, path, fact, "square_feet");
      return;
    default:
      return; // an unknown key is already reported by the enum check
  }
}

/** Validate one site fact (site_fact.schema.json) at `path`. */
export function checkSiteFact(problems: Problems, path: string, value: unknown): void {
  const fact = checkObject(problems, path, value);
  if (!fact) return;
  checkNoFixtureAnnotation(problems, path, fact);
  checkKeys(problems, path, fact, SITE_FACT_REQUIRED_KEYS, ["note"]);
  checkEnum(problems, `${path}.contract_version`, fact.contract_version, SITE_FACT_CONTRACT_VERSIONS);
  checkNonEmptyString(problems, `${path}.fact_id`, fact.fact_id);
  checkEnum(problems, `${path}.key`, fact.key, SITE_FACT_KEYS);
  checkNullableBbl(problems, `${path}.lot_bbl`, fact.lot_bbl);
  checkNullableNonEmptyString(problems, `${path}.street`, fact.street);
  if (!(fact.value === null || typeof fact.value === "string" || isJsonNumber(fact.value))) {
    problems.add(`${path}.value`, "must be a finite number, a string, or null");
  }
  if (!(fact.unit === null || isOneOf(SITE_FACT_UNITS, fact.unit))) {
    problems.add(`${path}.unit`, `must be one of ${SITE_FACT_UNITS.join(", ")}, or null`);
  }
  const rank = checkMeasurement(problems, `${path}.measurement`, fact.measurement);
  const sourceKind = checkNullableSource(problems, `${path}.source`, fact.source);
  const blocks = checkArray(problems, `${path}.blocks`, fact.blocks);
  blocks?.forEach((entry, index) => {
    checkEnum(problems, `${path}.blocks[${index}]`, entry, BLOCKED_OUTPUTS);
  });
  checkBoolean(problems, `${path}.editable`, fact.editable);
  if (fact.note !== undefined && !(fact.note === null || typeof fact.note === "string")) {
    problems.add(`${path}.note`, "must be a string or null");
  }
  if (rank !== null) checkRankRule(problems, path, fact, rank, sourceKind);
  checkKeyRule(problems, path, fact, sourceKind);
}
