/**
 * Dependency-based invalidation (task C-06, plan M1-11; plan section 9). Pure,
 * browser-memory-only functions over the shared study store's existing types:
 * no clock, no network, no storage, no React.
 *
 * Plan section 9 "Dependency-based invalidation" has four rules:
 *  1. Changing a site input marks dependent results in EVERY option out of date.
 *  2. Changing an option affects ONLY that option.
 *  3. A new rule version marks every result that used the older version.
 *  4. Late responses never overwrite newer ones (see ./study-revision).
 *
 * Which result FIELDS depend on the site, the option, or a rule version is
 * declared once, explicitly, in RESULT_FIELD_DEPENDENCIES below. The table fails
 * CLOSED: a result field it does not list is treated as dependent on every class
 * (dependenciesOf), so an unmapped field is always marked out of date rather
 * than silently kept. Erring toward "dependent" can only cause a redundant
 * recompute; erring toward "independent" would show a stale number as current,
 * which plan section 9 / 5a forbid.
 *
 * The store itself (study-store.ts) tracks only WHICH options are stale
 * (staleOptionIds); the per-option reason and per-field detail modelled here
 * attach to RESULTS, which the store does not hold yet (results.schema.json;
 * durable results are slice 2 / B-001 / Q7). optionsInvalidatedBy is the bridge
 * the store's mutation path uses for the option-level projection.
 */

import { classifyResponse, type ResponseDecision, type RevisionToken } from "./study-revision";

/** The three things a result field can depend on (plan section 9). */
export type DependencyClass = "site" | "option" | "rule_version";

export const DEPENDENCY_CLASSES: readonly DependencyClass[] = ["site", "option", "rule_version"];

/**
 * The result fields invalidation ranges over, named from results.schema.json
 * (the v1 results contract; READ ONLY here). The twelve substantive answers and
 * figures each depend on the site, the option and the rule versions; the two
 * meta fields are structurally narrower (no legal judgement):
 *  - depends_on_fact_ids is the list of site facts a result used, so it changes
 *    only when the site facts change;
 *  - lot_selection_statement is the pinned statement string (study.schema.json;
 *    plan section 3 step 2), never recomputed, so it depends on nothing.
 */
export type ResultField =
  | "floor_area_allowance"
  | "permitted_envelope"
  | "building_option"
  | "remaining_floor_area"
  | "shortfall"
  | "addon_gains"
  | "best_combination"
  | "unit_estimate"
  | "geometry"
  | "floor_by_floor"
  | "floor_stack"
  | "existing_building"
  | "depends_on_fact_ids"
  | "lot_selection_statement";

/** Every substantive zoning answer depends on the site, the option and the rules. */
const SITE_OPTION_RULE: readonly DependencyClass[] = ["site", "option", "rule_version"];

/**
 * The declared dependency of each result field. Substantive numbers list all
 * three classes (fail-safe: a program such as community facility can move an
 * allowance, and heights can move an envelope, so the option is never assumed
 * irrelevant). The two meta fields are narrower, as documented above.
 */
export const RESULT_FIELD_DEPENDENCIES: { readonly [F in ResultField]: readonly DependencyClass[] } = {
  floor_area_allowance: SITE_OPTION_RULE,
  permitted_envelope: SITE_OPTION_RULE,
  building_option: SITE_OPTION_RULE,
  remaining_floor_area: SITE_OPTION_RULE,
  shortfall: SITE_OPTION_RULE,
  addon_gains: SITE_OPTION_RULE,
  best_combination: SITE_OPTION_RULE,
  unit_estimate: SITE_OPTION_RULE,
  geometry: SITE_OPTION_RULE,
  floor_by_floor: SITE_OPTION_RULE,
  floor_stack: SITE_OPTION_RULE,
  existing_building: SITE_OPTION_RULE,
  depends_on_fact_ids: ["site"],
  lot_selection_statement: [],
};

/** The result fields in declaration order (used to keep staleness lists deterministic). */
export const RESULT_FIELDS: readonly ResultField[] = Object.keys(RESULT_FIELD_DEPENDENCIES) as ResultField[];

/** The same table as a Map, so a lookup of an unmapped key is a plain `undefined` (fail closed). */
const DEPENDENCY_TABLE: ReadonlyMap<string, readonly DependencyClass[]> = new Map(
  Object.entries(RESULT_FIELD_DEPENDENCIES),
);

/**
 * The classes a result field depends on. Fail CLOSED: a field the table does not
 * declare is treated as dependent on every class, so it is always invalidated.
 */
export function dependenciesOf(field: ResultField): ReadonlySet<DependencyClass> {
  const declared = DEPENDENCY_TABLE.get(field);
  return new Set(declared ?? DEPENDENCY_CLASSES);
}

export function fieldDependsOn(field: ResultField, cls: DependencyClass): boolean {
  return dependenciesOf(field).has(cls);
}

/** The fields of `candidates` that depend on `cls` (fail closed via dependenciesOf). */
export function fieldsDependingOn(
  cls: DependencyClass,
  candidates: readonly ResultField[] = RESULT_FIELDS,
): ResultField[] {
  return candidates.filter((field) => fieldDependsOn(field, cls));
}

/** Why a result field went out of date (plan section 9: the reason, which input changed). */
export type InvalidationReason =
  | { readonly kind: "site_input_changed"; readonly input: string }
  | { readonly kind: "option_input_changed"; readonly optionId: string }
  | { readonly kind: "rule_version_changed"; readonly ruleId: string; readonly from: string; readonly to: string };

/** One out-of-date result field and the reason it went stale. */
export interface FieldStaleness {
  readonly field: ResultField;
  readonly reason: InvalidationReason;
}

/**
 * The in-memory invalidation state of ONE option's result (results.schema.json
 * holds the result of one option at one revision). `outOfDate` is empty when the
 * result is current; otherwise it carries at most one entry per field, with the
 * most recent reason that field went stale. `ruleVersions` maps rule_id ->
 * version used (results.schema.json rule_versions, rule_id@version).
 */
export interface OptionResultState {
  readonly optionId: string;
  readonly computedForRevision: RevisionToken;
  readonly ruleVersions: Readonly<Record<string, string>>;
  readonly outOfDate: readonly FieldStaleness[];
}

/** A fresh, fully-current result state for an option computed at `revision`. */
export function currentResultState(
  optionId: string,
  revision: RevisionToken,
  ruleVersions: Readonly<Record<string, string>> = {},
): OptionResultState {
  return { optionId, computedForRevision: revision, ruleVersions: { ...ruleVersions }, outOfDate: [] };
}

export function isResultCurrent(result: OptionResultState): boolean {
  return result.outOfDate.length === 0;
}

/** Mark the given fields out of date with `reason`; one entry per field, most recent reason wins. */
function markFields(
  result: OptionResultState,
  fields: readonly ResultField[],
  reason: InvalidationReason,
): OptionResultState {
  if (fields.length === 0) return result;
  const byField = new Map<ResultField, FieldStaleness>();
  for (const staleness of result.outOfDate) byField.set(staleness.field, staleness);
  const affected = new Set(fields);
  for (const field of affected) byField.set(field, { field, reason });
  const ordered = orderStaleness(byField, affected);
  return { ...result, outOfDate: ordered };
}

/** Keep stalenesses in a stable, declaration-driven order; unknown fields trail in input order. */
function orderStaleness(
  byField: ReadonlyMap<ResultField, FieldStaleness>,
  affected: ReadonlySet<ResultField>,
): FieldStaleness[] {
  const seen = new Set<ResultField>();
  const ordered: FieldStaleness[] = [];
  for (const field of RESULT_FIELDS) {
    const staleness = byField.get(field);
    if (staleness) {
      ordered.push(staleness);
      seen.add(field);
    }
  }
  // Unmapped fields (fail-closed probes, e.g. a field not in RESULT_FIELDS) keep their input order.
  for (const field of affected) {
    if (seen.has(field)) continue;
    const staleness = byField.get(field);
    if (staleness) ordered.push(staleness);
  }
  return ordered;
}

/**
 * Rule 1 - a site input changed. Every option's result is marked out of date in
 * the fields that depend on the site; options' INPUTS are never touched (the
 * store proves this separately). `candidates` is the result-field set to
 * consider, defaulting to the full vocabulary; a field outside the vocabulary is
 * still invalidated (fail closed).
 */
export function invalidateOnSiteChange(
  results: readonly OptionResultState[],
  input: string,
  candidates: readonly ResultField[] = RESULT_FIELDS,
): OptionResultState[] {
  const affected = fieldsDependingOn("site", candidates);
  const reason: InvalidationReason = { kind: "site_input_changed", input };
  return results.map((result) => markFields(result, affected, reason));
}

/**
 * Rule 2 - one option's inputs changed. ONLY that option's result is marked out
 * of date; every other option's result is returned by reference, untouched.
 */
export function invalidateOnOptionChange(
  results: readonly OptionResultState[],
  optionId: string,
  candidates: readonly ResultField[] = RESULT_FIELDS,
): OptionResultState[] {
  const affected = fieldsDependingOn("option", candidates);
  const reason: InvalidationReason = { kind: "option_input_changed", optionId };
  return results.map((result) => (result.optionId === optionId ? markFields(result, affected, reason) : result));
}

/**
 * Rule 3 - a new rule version. Every result computed under an OLDER version of
 * `ruleId` is marked out of date in its rule-version-dependent fields. A result
 * that did not use the rule, or already used `newVersion`, is untouched. The
 * result is NEVER silently recomputed and its reported version is NEVER advanced
 * here (ruleVersions is left as-is), so it never claims the new result; only the
 * recompute step (slice 2) may do that.
 */
export function invalidateOnRuleVersionChange(
  results: readonly OptionResultState[],
  ruleId: string,
  newVersion: string,
  candidates: readonly ResultField[] = RESULT_FIELDS,
): OptionResultState[] {
  const affected = fieldsDependingOn("rule_version", candidates);
  return results.map((result) => {
    const used = Object.prototype.hasOwnProperty.call(result.ruleVersions, ruleId)
      ? result.ruleVersions[ruleId]
      : undefined;
    if (used === undefined || used === newVersion) return result;
    const reason: InvalidationReason = { kind: "rule_version_changed", ruleId, from: used, to: newVersion };
    return markFields(result, affected, reason);
  });
}

/** A freshly computed result arriving from the engine, carrying the revision it was computed for. */
export interface ComputedResult {
  readonly optionId: string;
  readonly computedForRevision: RevisionToken;
  readonly ruleVersions: Readonly<Record<string, string>>;
}

export interface ApplyOutcome {
  readonly result: OptionResultState;
  readonly decision: ResponseDecision;
}

/**
 * Rule 4 - apply a computed result only when its token is the current revision.
 * A late response (an older token) is DROPPED: the existing state is returned
 * unchanged and the decision records why it was ignored, never applied (plan
 * section 9, via ./study-revision classifyResponse).
 */
export function applyComputedResult(
  current: OptionResultState,
  computed: ComputedResult,
  currentRevision: RevisionToken,
): ApplyOutcome {
  const decision = classifyResponse(computed.computedForRevision, currentRevision);
  if (!decision.apply) return { result: current, decision };
  return {
    result: {
      optionId: current.optionId,
      computedForRevision: computed.computedForRevision,
      ruleVersions: { ...computed.ruleVersions },
      outOfDate: [],
    },
    decision,
  };
}

/** A study change, named for the store's mutation path (study-operations.ts). */
export type StudyChange =
  | { readonly kind: "site"; readonly input: string }
  | { readonly kind: "option"; readonly optionId: string }
  | { readonly kind: "rule_version"; readonly ruleId: string; readonly from: string; readonly to: string }
  | { readonly kind: "none" };

/**
 * The option-level projection the store keeps (staleOptionIds): which option ids
 * a change marks out of date. A site or rule-version change touches shared
 * inputs, so every option is marked; an option change marks only that option; a
 * name or selection change ("none") marks nothing. This is the §9 rule stated
 * once so the store's mutation path and this module cannot drift.
 */
export function optionsInvalidatedBy(optionIds: readonly string[], change: StudyChange): string[] {
  switch (change.kind) {
    case "none":
      return [];
    case "option":
      return [change.optionId];
    case "site":
    case "rule_version":
      return [...optionIds];
  }
}
