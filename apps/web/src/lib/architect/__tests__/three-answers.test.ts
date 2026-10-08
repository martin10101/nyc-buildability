import { describe, expect, it } from "vitest";
import {
  NOT_AVAILABLE,
  RULES_NOT_REVIEWED_REASON,
  STRIP_MAX_ITEMS,
  answerView,
  displayQuantity,
  notAvailableText,
  quantityText,
  remainingFloorAreaView,
  shortfallView,
  statusStripItems,
  streetWidthCaseLines,
  uniqueSections,
  type AnswerValue,
  type Results,
  type Unit,
} from "@/lib/architect/three-answers";
import { loadResultsFixture } from "@/test-support/results-fixtures";

/**
 * Queue D-05 (plan §5, §5a): the display rules behind the three-answers panel, with literal
 * expected strings so the component tests can rely on them.
 */

describe("notAvailableText — exactly 'Not available — <reason>' (plan §5, §5a item 3)", () => {
  it("drops a lead that only repeats the card's own subject (the plan's own example)", () => {
    expect(
      notAvailableText(
        "Envelope not available — height rules for this district are not built yet.",
        "permitted_envelope",
      ),
    ).toBe("Not available — height rules for this district are not built yet.");
    expect(
      notAvailableText(
        "Building option not available — it needs the permitted envelope.",
        "building_option",
      ),
    ).toBe("Not available — it needs the permitted envelope.");
  });

  it("drops a lead that only names the remaining floor area", () => {
    expect(
      notAvailableText("Remaining floor area not available — the survey is missing", "remaining_floor_area"),
    ).toBe("Not available — the survey is missing");
  });

  it("prefixes a bare reason", () => {
    expect(notAvailableText("height rules for this district are not built yet")).toBe(
      "Not available — height rules for this district are not built yet",
    );
  });

  it("keeps a reason whole when its lead names something other than this card", () => {
    expect(notAvailableText("Envelope not available — x", "building_option")).toBe(
      "Not available — Envelope not available — x",
    );
    expect(
      notAvailableText("The survey is not available — enter it", "permitted_envelope"),
    ).toBe("Not available — The survey is not available — enter it");
  });

  it("never returns an empty reason tail", () => {
    expect(notAvailableText("Not available")).toBe(NOT_AVAILABLE);
    expect(notAvailableText("Envelope not available.", "permitted_envelope")).toBe(NOT_AVAILABLE);
    expect(notAvailableText("   ")).toBe(NOT_AVAILABLE);
  });
});

describe("displayQuantity / quantityText — plain units, never the unit code", () => {
  const cases: [number, Unit, string][] = [
    [10000, "square_feet", "10,000 sq ft"],
    [55, "feet", "55 ft"],
    [2, "ratio", "2.0"],
    [0.75, "ratio", "0.75"],
    [100, "percent", "100%"],
    [4, "stories", "4 floors"],
    [1, "stories", "1 floor"],
    [29, "dwelling_units", "29 units"],
    [680, "square_feet_per_dwelling_unit", "680 sq ft per unit"],
    [12.5, "feet", "12.5 ft"],
    [1234.5, "square_feet", "1,234.5 sq ft"],
  ];
  for (const [value, unit, expected] of cases) {
    it(`${value} ${unit} reads "${expected}"`, () => {
      expect(quantityText(displayQuantity(value, unit))).toBe(expected);
    });
  }

  it("shows the bare number for a unit this build does not know", () => {
    const unknownUnit = "acres" as unknown as Unit;
    expect(quantityText(displayQuantity(3, unknownUnit))).toBe("3");
  });
});

describe("answerView — the draft gate and the headline", () => {
  it("a draft document hides every available answer unless a lane-flag surface asks", () => {
    const doc = loadResultsFixture("synthetic_all_answers_available");
    expect(doc.draft).toBe(true);
    expect(answerView(doc, "floor_area_allowance", false)).toEqual({
      kind: "not_available",
      text: `Not available — ${RULES_NOT_REVIEWED_REASON}`,
    });
    const shown = answerView(doc, "floor_area_allowance", true);
    expect(shown.kind).toBe("available");
  });

  it("a natively not-available answer keeps its own reason under the draft gate", () => {
    const doc = loadResultsFixture("synthetic_envelope_not_available_existing_building");
    expect(answerView(doc, "permitted_envelope", false)).toEqual({
      kind: "not_available",
      text: "Not available — height rules for this district are not built yet.",
    });
  });

  it("picks the contract's headline key, else the first value, and keeps every value", () => {
    const doc = loadResultsFixture("synthetic_all_answers_available");
    const answer = doc.answers.floor_area_allowance;
    if (answer.status !== "available") throw new Error("fixture changed: allowance not available");
    const view = answerView(doc, "floor_area_allowance", true);
    if (view.kind !== "available") throw new Error("expected an available view");
    if (view.headline.kind !== "value") throw new Error("expected a value headline");
    expect(view.headline.shown.value.key).toBe("max_residential_floor_area");
    expect(1 + view.rows.length).toBe(answer.values.length);
    expect(view.withheld).toEqual([]);

    const withoutKey: AnswerValue[] = answer.values.filter(
      value => value.key !== "max_residential_floor_area",
    );
    const probe: Results = {
      ...doc,
      answers: { ...doc.answers, floor_area_allowance: { ...answer, values: withoutKey } },
    };
    const fallback = answerView(probe, "floor_area_allowance", true);
    if (fallback.kind !== "available") throw new Error("expected an available view");
    if (fallback.headline.kind !== "value") throw new Error("expected a value headline");
    // No value_states on this 1.0.0 fixture: an absent headline key falls back to the first value.
    expect(fallback.headline.shown.value).toBe(withoutKey[0]);
  });

  it("S14: a conditional value shows 'If <assumption>' and a withheld value shows its reason", () => {
    // A 1.3.0 probe built from the all-available fixture: mark the floor-area headline conditional
    // and add a withheld value_states entry for a key not shown in values[].
    const doc = loadResultsFixture("synthetic_all_answers_available");
    const answer = doc.answers.floor_area_allowance;
    if (answer.status !== "available") throw new Error("fixture changed: allowance not available");
    const probe: Results = {
      ...doc,
      contract_version: "1.3.0",
      answers: {
        ...doc.answers,
        floor_area_allowance: {
          ...answer,
          value_states: {
            max_residential_floor_area: {
              way: "conditional",
              conditions: [
                {
                  kind: "unchecked_condition",
                  assumption: "If the recorded lot area is confirmed",
                  settled_by: "A survey or deed dimensions",
                },
              ],
            },
            legal_unit_limit_standard: {
              way: "withheld",
              label: "Legal dwelling-unit limit",
              reason: "There is no evidence of a special density area, so it is not known.",
              gap_kind: "work_owed",
              resolved_by: "Sourced evidence of the special density area",
            },
          },
        },
      },
    };
    const view = answerView(probe, "floor_area_allowance", true);
    if (view.kind !== "available") throw new Error("expected an available view");
    if (view.headline.kind !== "value") throw new Error("expected a value headline");
    expect(view.headline.shown.condition).toBe("If the recorded lot area is confirmed");
    expect(view.withheld).toEqual([
      {
        key: "legal_unit_limit_standard",
        label: "Legal dwelling-unit limit",
        reason: "There is no evidence of a special density area, so it is not known.",
      },
    ]);
    // The withheld key never appears among the shown values (R570).
    expect(view.rows.every(row => row.value.key !== "legal_unit_limit_standard")).toBe(true);
  });

  it("S14 RED PROOF: a withheld HEADLINE key is shown as its reason, never the first value (R556)", () => {
    // Build a permitted_envelope whose designated headline key (max_building_height) is WITHHELD
    // and removed from values[], with other heights shown. Today's reader returned values[0] (a
    // different value) as the headline; the fixed reader shows the withheld reason instead.
    const doc = loadResultsFixture("synthetic_all_answers_available");
    const envelope = doc.answers.permitted_envelope;
    if (envelope.status !== "available") throw new Error("fixture changed: envelope not available");
    const without = envelope.values.filter(value => value.key !== "max_building_height");
    expect(without.length).toBeGreaterThan(0);
    const probe: Results = {
      ...doc,
      contract_version: "1.3.0",
      answers: {
        ...doc.answers,
        permitted_envelope: {
          ...envelope,
          values: without,
          value_states: {
            max_building_height: {
              way: "withheld",
              label: "Maximum building height",
              reason: "The height depends on a rule the program has not built yet.",
              gap_kind: "work_owed",
              resolved_by: "Building the rule and checking it against a worked example",
            },
          },
        },
      },
    };
    const view = answerView(probe, "permitted_envelope", true);
    if (view.kind !== "available") throw new Error("expected an available view");
    // The fixed reader: the headline is the withheld reason, NOT the first shown value.
    expect(view.headline.kind).toBe("withheld");
    if (view.headline.kind !== "withheld") throw new Error("expected a withheld headline");
    expect(view.headline.withheld.key).toBe("max_building_height");
    expect(view.headline.withheld.reason).toContain("not built yet");
    // Every originally shown value is kept as a row (none is promoted into the headline slot).
    expect(view.rows.map(row => row.value.key).sort()).toEqual(
      without.map(value => value.key).sort(),
    );
  });

  it("an available answer with no value is not available, never a blank number", () => {
    const doc = loadResultsFixture("synthetic_all_answers_available");
    const answer = doc.answers.building_option;
    if (answer.status !== "available") throw new Error("fixture changed: option not available");
    const probe: Results = {
      ...doc,
      answers: { ...doc.answers, building_option: { ...answer, values: [] } },
    };
    const view = answerView(probe, "building_option", true);
    expect(view.kind).toBe("not_available");
    if (view.kind === "not_available") expect(view.text.startsWith("Not available — ")).toBe(true);
  });
});

describe("supplements, strip and street-width lines", () => {
  it("remaining floor area: not applicable → nothing; not available → the owner's wording (D-090-R038)", () => {
    expect(remainingFloorAreaView(loadResultsFixture("synthetic_all_answers_available"))).toBeNull();
    // Owner wording, settled 2026-10-01, word for word: "Remaining development capacity" →
    // "Not confirmed", then the reason line.
    expect(
      remainingFloorAreaView(
        loadResultsFixture("synthetic_envelope_not_available_existing_building"),
      ),
    ).toEqual({
      kind: "not_available",
      label: "Remaining development capacity",
      text: "Not confirmed",
      reason: "Needs verified zoning-lot boundaries and existing zoning floor area.",
    });
  });

  it("shortfall: none reads as reaching the allowance; a shortfall keeps its reasons", () => {
    const doc = loadResultsFixture("synthetic_all_answers_available");
    expect(shortfallView(doc)).toEqual({ kind: "reaches_allowance" });
    const probe: Results = {
      ...doc,
      shortfall: {
        status: "shortfall",
        sq_ft: 1250,
        reasons: [
          {
            text: "Probe reason.",
            computed_from: ["probe-constraint"],
            values: [{ name: "probe height", value: 1, unit: "feet" }],
          },
        ],
      },
    };
    expect(shortfallView(probe)).toEqual({
      kind: "shortfall",
      amount: { number: "1,250", unit: "sq ft" },
      reasons: ["Probe reason."],
    });
  });

  it("the strip keeps at most three items and moves the rest behind it", () => {
    const doc = loadResultsFixture("synthetic_all_answers_available");
    const probe: Results = {
      ...doc,
      status_strip: ["One", "Two", "Three", "Four", "Five"].map(text => ({ text })),
    };
    const { visible, overflow } = statusStripItems(probe);
    expect(STRIP_MAX_ITEMS).toBe(3);
    expect(visible).toEqual(["One", "Two", "Three"]);
    expect(overflow).toEqual(["Four", "Five"]);
  });

  it("a street-width case names its assumed width in plain English", () => {
    const narrow = loadResultsFixture("synthetic_needs_street_width_narrow_case");
    expect(streetWidthCaseLines(narrow)).toEqual([
      "This case assumes Synthetic Street B is a narrow street; its width is not known.",
    ]);
    expect(streetWidthCaseLines(loadResultsFixture("synthetic_all_answers_available"))).toEqual([]);
  });

  it("uniqueSections lists each rule section once, in order", () => {
    expect(uniqueSections(["ZR 23-432", "ZR 23-433", "ZR 23-432"])).toEqual([
      "ZR 23-432",
      "ZR 23-433",
    ]);
  });
});
