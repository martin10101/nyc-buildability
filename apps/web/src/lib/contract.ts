/**
 * Canonical contract vocabulary for the web client (task M2-T002).
 *
 * REPLACES the retired handwritten src/lib/property-profile.ts. The ONLY
 * type vocabulary for the property profile is the GENERATED module
 * packages/contracts/generated/property_profile.ts (M2-T003 output,
 * regenerated deterministically from the canonical JSON schemas; CI job
 * contracts-typegen fails on any drift). This file:
 *
 *   1. Re-exports the generated types (type-only imports — erased at build
 *      time, so the Next.js bundle never compiles files outside apps/web).
 *   2. Declares the runtime enum arrays the client needs for validation.
 *      Each array is LOCKED to the generated union with `satisfies` plus a
 *      two-way exhaustiveness assertion, so any contract change that adds
 *      or removes an enum member fails `tsc` here — the arrays cannot
 *      silently drift from the generated vocabulary. This includes the
 *      contract_version pin: the generated union is
 *      "1.0.0" | "1.1.0" | "1.2.0" | "1.3.0" (the stale handwritten
 *      "1.0.0"|"1.1.0" pin is retired with this file; "1.3.0" added by task
 *      M2-T006 amendment A1 - publishing a contract version is a coordinated
 *      schema + backend + client-vocabulary change while this set is closed).
 *   3. Provides RUNTIME NARROWING helpers for the two open-object shapes
 *      the schema deliberately leaves unconstrained (zoning.mapped_features
 *      items and conflict value entries). These helpers are display-only
 *      passthroughs guarded by typeof checks; they never invent, coerce, or
 *      interpret a value, and they are NOT a competing schema.
 *
 * No legal logic lives here (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 */

import type {
  Bbl,
  Bin,
  BoroughCode,
  BoroughName,
  CoverageStatus,
  DataCompleteness,
  DistrictProvenanceMap,
  FactValue,
  PropertyProfile,
  SourceFact,
} from "../../../../packages/contracts/generated/property_profile";

export type {
  Bbl,
  Bin,
  BoroughCode,
  BoroughName,
  CoverageStatus,
  DataCompleteness,
  DistrictProvenanceMap,
  FactValue,
  PropertyProfile,
  SourceFact,
};

// ---------------------------------------------------------------------------
// Named aliases DERIVED from the generated root type (never hand-declared
// shapes — indexing the generated type keeps them in lockstep with it).
// ---------------------------------------------------------------------------

export type ProfileVersion = PropertyProfile["profile_version"];
export type ContractVersion = ProfileVersion["contract_version"];
export type Identity = PropertyProfile["identity"];
export type IdentityAddress = NonNullable<Identity["address"]>;
export type Zoning = PropertyProfile["zoning"];
export type MappedFeatureObject = NonNullable<Zoning["mapped_features"]>[number];
export type MissingInput = PropertyProfile["missing_inputs"][number];
export type Conflict = PropertyProfile["conflicts"][number];
export type ConflictValue = Conflict["values"][number];
export type UserConfirmation = PropertyProfile["user_confirmations"][number];
export type Reproducibility = NonNullable<PropertyProfile["reproducibility"]>;
export type StatusDimensions = NonNullable<PropertyProfile["status_dimensions"]>;

// ---------------------------------------------------------------------------
// Runtime enum arrays, exhaustively locked to the generated unions.
// `satisfies readonly X[]` proves every member IS in the union; the exported
// `ContractEnumAssertions` type proves the union has NO member missing from
// the array (two-way equality — tsc fails on either direction of drift).
// ---------------------------------------------------------------------------

export const SUPPORTED_CONTRACT_VERSIONS = [
  "1.0.0",
  "1.1.0",
  "1.2.0",
  "1.3.0",
] as const satisfies readonly ContractVersion[];

export const COVERAGE_STATUSES = [
  "verified",
  "conditional",
  "professional_review_required",
  "data_conflict",
  "unsupported",
  "not_applicable",
] as const satisfies readonly CoverageStatus[];

export const DATA_COMPLETENESS_VALUES = [
  "complete",
  "missing_noncritical",
  "missing_critical",
] as const satisfies readonly DataCompleteness[];

export const USER_CONFIRMED_OR_OVERRIDDEN_VALUES = [
  "none",
  "confirmed",
  "overridden",
] as const satisfies readonly SourceFact["user_confirmed_or_overridden"][];

export const CONFLICT_STATUS_VALUES = [
  "none",
  "conflicting",
  "resolved",
] as const satisfies readonly SourceFact["conflict_status"][];

export const CONFLICT_RESOLUTION_VALUES = [
  "unresolved",
  "user_confirmed",
  "user_overridden",
  "source_priority",
] as const satisfies readonly Conflict["resolution"][];

export const CRITICALITY_VALUES = [
  "critical",
  "noncritical",
] as const satisfies readonly MissingInput["criticality"][];

export const USER_CONFIRMATION_ACTIONS = [
  "confirmed",
  "overridden",
] as const satisfies readonly UserConfirmation["action"][];

export const BOROUGH_NAMES = [
  "Manhattan",
  "Bronx",
  "Brooklyn",
  "Queens",
  "Staten Island",
] as const satisfies readonly BoroughName[];

export const BOROUGH_CODES = [1, 2, 3, 4, 5] as const satisfies readonly BoroughCode[];

export const SOURCE_RECORD_COMPLETENESS_VALUES = [
  "complete",
  "partial",
  "not_computed",
] as const satisfies readonly StatusDimensions["source_record_completeness"][];

export const ANALYSIS_READINESS_VALUES = [
  "ready",
  "blocked_missing_critical",
  "blocked_data_conflict",
  "not_computed",
] as const satisfies readonly StatusDimensions["analysis_readiness"][];

export const RULE_COVERAGE_VALUES = [
  "not_computed",
] as const satisfies readonly StatusDimensions["rule_coverage"][];

export const GEOMETRY_VALIDITY_VALUES = [
  "missing",
  "not_computed",
] as const satisfies readonly StatusDimensions["geometry_validity"][];

export const FINANCIAL_READINESS_VALUES = [
  "not_computed",
] as const satisfies readonly StatusDimensions["financial_readiness"][];

/** Two-way equality proof: `true` only when A and B are the same union. */
type MutuallyEqual<A, B> = [A] extends [B] ? ([B] extends [A] ? true : never) : never;

/**
 * Compile-time exhaustiveness proof (exported so it is never "unused").
 * If ANY enum array above misses a member of its generated union, the
 * corresponding tuple slot becomes `never` and `tsc` fails.
 */
export type ContractEnumAssertions = [
  MutuallyEqual<ContractVersion, (typeof SUPPORTED_CONTRACT_VERSIONS)[number]>,
  MutuallyEqual<CoverageStatus, (typeof COVERAGE_STATUSES)[number]>,
  MutuallyEqual<DataCompleteness, (typeof DATA_COMPLETENESS_VALUES)[number]>,
  MutuallyEqual<
    SourceFact["user_confirmed_or_overridden"],
    (typeof USER_CONFIRMED_OR_OVERRIDDEN_VALUES)[number]
  >,
  MutuallyEqual<SourceFact["conflict_status"], (typeof CONFLICT_STATUS_VALUES)[number]>,
  MutuallyEqual<Conflict["resolution"], (typeof CONFLICT_RESOLUTION_VALUES)[number]>,
  MutuallyEqual<MissingInput["criticality"], (typeof CRITICALITY_VALUES)[number]>,
  MutuallyEqual<UserConfirmation["action"], (typeof USER_CONFIRMATION_ACTIONS)[number]>,
  MutuallyEqual<BoroughName, (typeof BOROUGH_NAMES)[number]>,
  MutuallyEqual<BoroughCode, (typeof BOROUGH_CODES)[number]>,
  MutuallyEqual<
    StatusDimensions["source_record_completeness"],
    (typeof SOURCE_RECORD_COMPLETENESS_VALUES)[number]
  >,
  MutuallyEqual<
    StatusDimensions["analysis_readiness"],
    (typeof ANALYSIS_READINESS_VALUES)[number]
  >,
  MutuallyEqual<StatusDimensions["rule_coverage"], (typeof RULE_COVERAGE_VALUES)[number]>,
  MutuallyEqual<
    StatusDimensions["geometry_validity"],
    (typeof GEOMETRY_VALIDITY_VALUES)[number]
  >,
  MutuallyEqual<
    StatusDimensions["financial_readiness"],
    (typeof FINANCIAL_READINESS_VALUES)[number]
  >,
];

export function isCoverageStatus(value: unknown): value is CoverageStatus {
  return (
    typeof value === "string" &&
    (COVERAGE_STATUSES as readonly string[]).includes(value)
  );
}

// ---------------------------------------------------------------------------
// Runtime narrowing for OPEN contract objects (display-only passthroughs).
//
// zoning.mapped_features items are `{"type": "object"}` in the canonical
// schema (no documented keys); the accepted M1-T005 builder emits
// feature/value/provenance_ref/coverage_status, and the M2-T001 G3 review
// accepted their display. The generated type is therefore `{}` and every
// key read MUST be runtime-guarded here — never asserted.
//
// Conflict value entries document only source_id/value; the builder emits an
// additional `derivation` string whose display the M2-T001 G3 review
// accepted (S6 borocode-conflict journey asserts it). It is read through a
// guard below and its absence is always tolerated. RECOMMENDATION recorded
// in the producer report: document `derivation` (and the mapped-feature
// keys) in the canonical schema in a follow-up contracts task.
// ---------------------------------------------------------------------------

export interface MappedFeatureView {
  /** Builder-emitted feature (source column) name, when present. */
  feature: string | null;
  /** True when the open object carries a `value` key at all. */
  hasValue: boolean;
  value: unknown;
  provenanceRef: string | null;
  coverageStatus: CoverageStatus | null;
}

export function mappedFeatureView(item: MappedFeatureObject): MappedFeatureView {
  const record = item as Record<string, unknown>;
  return {
    feature: typeof record.feature === "string" ? record.feature : null,
    hasValue: "value" in record,
    value: record.value,
    provenanceRef:
      typeof record.provenance_ref === "string" ? record.provenance_ref : null,
    coverageStatus: isCoverageStatus(record.coverage_status)
      ? record.coverage_status
      : null,
  };
}

/** Builder-emitted `derivation` note on a conflict value (open-schema key). */
export function conflictValueDerivation(value: ConflictValue): string | null {
  const record = value as Record<string, unknown>;
  return typeof record.derivation === "string" ? record.derivation : null;
}
