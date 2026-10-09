import { describe, expect, it, vi } from "vitest";
import {
  applyComputedResult,
  currentResultState,
  dependenciesOf,
  fieldsDependingOn,
  invalidateOnOptionChange,
  invalidateOnRuleVersionChange,
  invalidateOnSiteChange,
  isResultCurrent,
  optionsInvalidatedBy,
  type InvalidationReason,
  type OptionResultState,
  type ResultField,
  type StudyChange,
} from "../study-invalidation";

/**
 * Dependency-based invalidation (task C-06, plan M1-11; plan section 9). The
 * store's option-inputs-untouched proof lives in study-operations.test.ts; these
 * tests exercise the pure result-level invalidation model.
 */

/** The twelve substantive answers/figures (each depends on site + option + rule version). */
const SUBSTANTIVE: readonly ResultField[] = [
  "floor_area_allowance",
  "permitted_envelope",
  "building_option",
  "remaining_floor_area",
  "shortfall",
  "addon_gains",
  "best_combination",
  "unit_estimate",
  "geometry",
  "floor_by_floor",
  "floor_stack",
  "existing_building",
];
const SITE_FIELDS: readonly ResultField[] = [...SUBSTANTIVE, "depends_on_fact_ids"];
const OPTION_FIELDS: readonly ResultField[] = SUBSTANTIVE;
const RULE_FIELDS: readonly ResultField[] = SUBSTANTIVE;

function twoCurrentResults(): OptionResultState[] {
  return [
    currentResultState("opt-a", 3, { far: "1.0.0", height: "2.0.0" }),
    currentResultState("opt-b", 3, { far: "1.0.0", height: "2.0.0" }),
  ];
}

function getResult(results: readonly OptionResultState[], optionId: string): OptionResultState {
  const found = results.find((result) => result.optionId === optionId);
  if (!found) throw new Error(`no result for ${optionId}`);
  return found;
}

function markedFields(result: OptionResultState): ResultField[] {
  return result.outOfDate.map((staleness) => staleness.field).sort();
}

function reasonFor(result: OptionResultState, field: ResultField): InvalidationReason | undefined {
  return result.outOfDate.find((staleness) => staleness.field === field)?.reason;
}

interface RuleCase {
  readonly label: string;
  readonly run: (results: OptionResultState[]) => OptionResultState[];
  readonly affectedOptionIds: readonly string[];
  readonly untouchedOptionIds: readonly string[];
  readonly expectedMarked: readonly ResultField[];
  readonly expectedUntouched: readonly ResultField[];
  readonly reason: InvalidationReason;
}

const rules: readonly RuleCase[] = [
  {
    label: "rule 1 - a site change marks every option's site-dependent fields",
    run: (results) => invalidateOnSiteChange(results, "lot_area"),
    affectedOptionIds: ["opt-a", "opt-b"],
    untouchedOptionIds: [],
    expectedMarked: SITE_FIELDS,
    expectedUntouched: ["lot_selection_statement"],
    reason: { kind: "site_input_changed", input: "lot_area" },
  },
  {
    label: "rule 2 - an option change marks only that option's option-dependent fields",
    run: (results) => invalidateOnOptionChange(results, "opt-a"),
    affectedOptionIds: ["opt-a"],
    untouchedOptionIds: ["opt-b"],
    expectedMarked: OPTION_FIELDS,
    expectedUntouched: ["depends_on_fact_ids", "lot_selection_statement"],
    reason: { kind: "option_input_changed", optionId: "opt-a" },
  },
  {
    label: "rule 3 - a new rule version marks every result that used the older version",
    run: (results) => invalidateOnRuleVersionChange(results, "far", "1.1.0"),
    affectedOptionIds: ["opt-a", "opt-b"],
    untouchedOptionIds: [],
    expectedMarked: RULE_FIELDS,
    expectedUntouched: ["depends_on_fact_ids", "lot_selection_statement"],
    reason: { kind: "rule_version_changed", ruleId: "far", from: "1.0.0", to: "1.1.0" },
  },
];

describe("the §9 invalidation rules (parameterized: case, change, marked set, untouched set, reason)", () => {
  it.each(rules)("$label", (rule) => {
    const before = twoCurrentResults();
    const after = rule.run(before);

    // Untouched options are returned by reference, byte-identical.
    for (const optionId of rule.untouchedOptionIds) {
      const index = before.findIndex((result) => result.optionId === optionId);
      expect(after[index]).toBe(before[index]);
    }

    // Affected options carry exactly the expected marked set, each with the reason;
    // the expected-untouched fields stay current.
    for (const optionId of rule.affectedOptionIds) {
      const result = getResult(after, optionId);
      expect(markedFields(result)).toEqual([...rule.expectedMarked].sort());
      for (const field of rule.expectedMarked) {
        expect(reasonFor(result, field)).toEqual(rule.reason);
      }
      for (const field of rule.expectedUntouched) {
        expect(reasonFor(result, field)).toBeUndefined();
      }
    }
  });
});

describe("rule 2 - options are independent (plan section 9)", () => {
  it("never touches another option's result", () => {
    const before = twoCurrentResults();
    const after = invalidateOnOptionChange(before, "opt-a");
    expect(getResult(after, "opt-b")).toBe(before[1]);
    expect(isResultCurrent(getResult(after, "opt-b"))).toBe(true);
    expect(isResultCurrent(getResult(after, "opt-a"))).toBe(false);
  });
});

describe("rule 3 - a new rule version", () => {
  it("leaves results already on the new version, or not using the rule, untouched; never claims the new result", () => {
    const results = [
      currentResultState("opt-a", 3, { far: "1.0.0" }), // old far -> marked
      currentResultState("opt-b", 3, { far: "1.1.0" }), // already new -> untouched
      currentResultState("opt-c", 3, { height: "2.0.0" }), // does not use far -> untouched
    ];
    const after = invalidateOnRuleVersionChange(results, "far", "1.1.0");
    expect(isResultCurrent(after[0])).toBe(false);
    expect(after[1]).toBe(results[1]);
    expect(after[2]).toBe(results[2]);
    // The reported version is never advanced here (a recompute, slice 2, may do that).
    expect(after[0].ruleVersions).toEqual({ far: "1.0.0" });
  });
});

describe("the dependency table", () => {
  it("declares the two meta fields narrowly and every substantive field on all three classes", () => {
    expect([...dependenciesOf("lot_selection_statement")]).toEqual([]);
    expect([...dependenciesOf("depends_on_fact_ids")]).toEqual(["site"]);
    for (const field of SUBSTANTIVE) {
      expect(dependenciesOf(field)).toEqual(new Set<string>(["site", "option", "rule_version"]));
    }
  });

  it("fieldsDependingOn selects fields by class", () => {
    expect(fieldsDependingOn("site")).toContain("depends_on_fact_ids");
    expect(fieldsDependingOn("site")).not.toContain("lot_selection_statement");
    expect(fieldsDependingOn("option")).not.toContain("depends_on_fact_ids");
    expect(fieldsDependingOn("rule_version")).not.toContain("depends_on_fact_ids");
    expect(fieldsDependingOn("option")).toEqual([...OPTION_FIELDS]);
  });

  it("keeps one entry per field, most recent reason wins", () => {
    const afterSite = invalidateOnSiteChange([currentResultState("opt-a", 1, { far: "1.0.0" })], "lot_area");
    const afterBoth = invalidateOnRuleVersionChange(afterSite, "far", "1.1.0");
    const geometry = afterBoth[0].outOfDate.filter((staleness) => staleness.field === "geometry");
    expect(geometry).toHaveLength(1);
    expect(geometry[0].reason).toEqual({ kind: "rule_version_changed", ruleId: "far", from: "1.0.0", to: "1.1.0" });
  });
});

describe("fail closed - an unknown result field is treated as dependent on everything", () => {
  const UNKNOWN = "mystery_result_field" as unknown as ResultField;

  it("dependenciesOf returns every class for an unmapped field", () => {
    expect(dependenciesOf(UNKNOWN)).toEqual(new Set<string>(["site", "option", "rule_version"]));
  });

  it("every change type marks an unmapped field out of date", () => {
    const base = [currentResultState("opt-a", 1, { far: "1.0.0" })];
    const candidates: readonly ResultField[] = [UNKNOWN];
    expect(markedFields(invalidateOnSiteChange(base, "x", candidates)[0])).toContain(UNKNOWN);
    expect(markedFields(invalidateOnOptionChange(base, "opt-a", candidates)[0])).toContain(UNKNOWN);
    expect(markedFields(invalidateOnRuleVersionChange(base, "far", "9.9.9", candidates)[0])).toContain(UNKNOWN);
  });
});

describe("rule 4 - late responses never overwrite newer ones", () => {
  it("applies a response whose token is the current revision and clears the out-of-date fields", () => {
    const stale = invalidateOnSiteChange([currentResultState("opt-a", 1, { far: "1.0.0" })], "lot_area")[0];
    const { result, decision } = applyComputedResult(
      stale,
      { optionId: "opt-a", computedForRevision: 2, ruleVersions: { far: "1.1.0" } },
      2,
    );
    expect(decision).toEqual({ apply: true });
    expect(isResultCurrent(result)).toBe(true);
    expect(result.computedForRevision).toBe(2);
    expect(result.ruleVersions).toEqual({ far: "1.1.0" });
  });

  it("drops a late response (older token), records it as ignored, and never applies it", () => {
    const stale = invalidateOnSiteChange([currentResultState("opt-a", 1, { far: "1.0.0" })], "lot_area")[0];
    const { result, decision } = applyComputedResult(
      stale,
      { optionId: "opt-a", computedForRevision: 1, ruleVersions: { far: "1.0.0" } },
      2,
    );
    expect(decision).toMatchObject({ apply: false, ignored: "stale_response" });
    expect(result).toBe(stale); // unchanged: never applied
    expect(isResultCurrent(result)).toBe(false);
  });
});

describe("optionsInvalidatedBy (the store's option-level projection)", () => {
  const ids = ["opt-a", "opt-b", "opt-c"];
  const cases: ReadonlyArray<{ change: StudyChange; expected: readonly string[] }> = [
    { change: { kind: "none" }, expected: [] },
    { change: { kind: "option", optionId: "opt-b" }, expected: ["opt-b"] },
    { change: { kind: "site", input: "lot_area" }, expected: ids },
    { change: { kind: "rule_version", ruleId: "far", from: "1.0.0", to: "1.1.0" }, expected: ids },
  ];

  it.each(cases)("marks the right options for $change.kind", ({ change, expected }) => {
    expect(optionsInvalidatedBy(ids, change)).toEqual([...expected]);
  });
});

describe("purity - no persisted/storage or network API is used", () => {
  it("exercises every exported function without touching fetch or localStorage", () => {
    const fetchSpy = vi.fn();
    const originalFetch = (globalThis as { fetch?: unknown }).fetch;
    (globalThis as { fetch?: unknown }).fetch = fetchSpy;
    const setItem = vi.spyOn(Storage.prototype, "setItem");
    const getItem = vi.spyOn(Storage.prototype, "getItem");
    try {
      const base = [currentResultState("opt-a", 1, { far: "1.0.0" })];
      invalidateOnSiteChange(base, "lot_area");
      invalidateOnOptionChange(base, "opt-a");
      invalidateOnRuleVersionChange(base, "far", "1.1.0");
      applyComputedResult(base[0], { optionId: "opt-a", computedForRevision: 1, ruleVersions: { far: "1.0.0" } }, 1);
      optionsInvalidatedBy(["opt-a"], { kind: "site", input: "lot_area" });
      dependenciesOf("geometry");
    } finally {
      (globalThis as { fetch?: unknown }).fetch = originalFetch;
      setItem.mockRestore();
      getItem.mockRestore();
    }
    expect(fetchSpy).not.toHaveBeenCalled();
    expect(setItem).not.toHaveBeenCalled();
    expect(getItem).not.toHaveBeenCalled();
  });
});
