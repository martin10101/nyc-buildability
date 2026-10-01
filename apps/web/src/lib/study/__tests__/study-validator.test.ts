import { describe, expect, it } from "vitest";
import validCopiedFromExport from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_copied_from_export_existing_zfa_unknown.json";
import validCorner from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_corner_lot_two_options.json";
import validStreetWidthUnknown from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_street_width_unknown.json";
import invalidGoalOther from "../../../../../../packages/contracts/fixtures/invalid/study/goal_other_without_text.json";
import invalidRevisionOne from "../../../../../../packages/contracts/fixtures/invalid/study/revision_one_with_parent.json";
import invalidStatement from "../../../../../../packages/contracts/fixtures/invalid/study/selection_statement_reworded.json";
import invalidNestedZero from "../../../../../../packages/contracts/fixtures/invalid/study/site_fact_unknown_encoded_as_zero.json";
import validZfaAssumed from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_existing_zoning_floor_area_assumed.json";
import validLotAreaTaxMap from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_lot_area_approximate_tax_map.json";
import validStreetWidthEntered from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_street_width_entered.json";
import validWallaboutUnknown from "../../../../../../packages/contracts/fixtures/valid/site_fact/wallabout_base_lot_32_lot_area_unknown.json";
import invalidZfaRecorded from "../../../../../../packages/contracts/fixtures/invalid/site_fact/existing_zfa_from_recorded_building_area.json";
import invalidZfaZero from "../../../../../../packages/contracts/fixtures/invalid/site_fact/existing_zfa_zero.json";
import invalidLabel from "../../../../../../packages/contracts/fixtures/invalid/site_fact/label_does_not_match_rank.json";
import invalidFactZero from "../../../../../../packages/contracts/fixtures/invalid/site_fact/unknown_encoded_as_zero.json";
import invalidNoBlocks from "../../../../../../packages/contracts/fixtures/invalid/site_fact/unknown_without_blocks.json";
import { validateStudyDocument } from "../study-validator";
import { cornerStudy } from "./study-test-data";

/**
 * The runtime mirror of study.schema.json (+ site_fact) agrees with the
 * committed contract fixtures: every valid fixture passes, and every invalid
 * fixture fails FOR ITS STATED DEFECT. The fixture-only `_expected_failure`
 * key is removed first, so an invalid fixture cannot pass this test merely by
 * carrying that key (it is refused separately below).
 */

function copy(value: unknown): Record<string, unknown> {
  return JSON.parse(JSON.stringify(value)) as Record<string, unknown>;
}

function withoutAnnotation(value: unknown): Record<string, unknown> {
  const document = copy(value);
  delete document._expected_failure;
  return document;
}

/** The corner study with its site facts replaced by `fact` alone. */
function studyWithFact(fact: unknown): Record<string, unknown> {
  const study = copy(cornerStudy());
  study.site = { facts: [withoutAnnotation(fact)] };
  return study;
}

function problemsOf(document: unknown): string[] {
  const result = validateStudyDocument(document);
  return result.ok ? [] : result.problems;
}

describe("validateStudyDocument: committed study fixtures", () => {
  it.each<[string, unknown]>([
    ["synthetic_corner_lot_two_options", validCorner],
    ["synthetic_copied_from_export_existing_zfa_unknown", validCopiedFromExport],
    ["synthetic_street_width_unknown", validStreetWidthUnknown],
  ])("accepts the valid fixture %s", (_name, fixture) => {
    expect(validateStudyDocument(copy(fixture))).toMatchObject({ ok: true });
  });

  it.each<[string, unknown, string]>([
    ["goal_other_without_text", invalidGoalOther, "options[1].goal.text"],
    ["revision_one_with_parent", invalidRevisionOne, "revision.parent"],
    ["selection_statement_reworded", invalidStatement, "lot_selection.statement"],
    ["site_fact_unknown_encoded_as_zero", invalidNestedZero, "site.facts[3]"],
  ])("rejects the invalid fixture %s at its stated defect", (_name, fixture, path) => {
    const problems = problemsOf(withoutAnnotation(fixture));
    expect(problems.length).toBeGreaterThan(0);
    expect(problems.every((problem) => problem.startsWith(path))).toBe(true);
  });

  it("refuses the fixture-only annotation in a real study", () => {
    const problems = problemsOf({ ...copy(validCorner), _expected_failure: "fixture note" });
    expect(problems.some((problem) => problem.includes("fixture-only key"))).toBe(true);
  });
});

describe("validateStudyDocument: committed site-fact fixtures nested in a study", () => {
  it.each<[string, unknown]>([
    ["synthetic_existing_zoning_floor_area_assumed", validZfaAssumed],
    ["synthetic_lot_area_approximate_tax_map", validLotAreaTaxMap],
    ["synthetic_street_width_entered", validStreetWidthEntered],
    ["wallabout_base_lot_32_lot_area_unknown", validWallaboutUnknown],
  ])("accepts the valid site fact %s", (_name, fact) => {
    expect(problemsOf(studyWithFact(fact))).toEqual([]);
  });

  it.each<[string, unknown, string]>([
    ["existing_zfa_from_recorded_building_area", invalidZfaRecorded, "site.facts[0].source"],
    ["existing_zfa_zero", invalidZfaZero, "site.facts[0].value"],
    ["label_does_not_match_rank", invalidLabel, "site.facts[0].measurement.label"],
    ["unknown_encoded_as_zero", invalidFactZero, "site.facts[0]"],
    ["unknown_without_blocks", invalidNoBlocks, "site.facts[0].blocks"],
  ])("rejects the invalid site fact %s at its stated defect", (_name, fact, path) => {
    const problems = problemsOf(studyWithFact(fact));
    expect(problems.length).toBeGreaterThan(0);
    expect(problems.every((problem) => problem.startsWith(path))).toBe(true);
  });
});

describe("validateStudyDocument: store invariants and strictness", () => {
  it("requires the selected option to be one of the options", () => {
    const study = cornerStudy();
    study.selected_option_id = "opt-z";
    expect(problemsOf(study)).toEqual([expect.stringMatching(/^selected_option_id: /)]);
  });

  it("rejects two options with the same id, so an edit can never hit both", () => {
    const study = cornerStudy();
    study.options[1].option_id = "opt-a";
    expect(problemsOf(study)).toEqual([expect.stringMatching(/^options\[1\]: /)]);
  });

  it("rejects two site facts with the same id", () => {
    const study = cornerStudy();
    study.site.facts[1].fact_id = "fact-lot-area";
    expect(problemsOf(study)).toEqual([expect.stringMatching(/^site\.facts\[1\]: /)]);
  });

  it("rejects a non-finite height that JSON could not carry", () => {
    const study = cornerStudy();
    study.options[0].floor_to_floor_heights.typical_floor.height_ft = Number.POSITIVE_INFINITY;
    expect(problemsOf(study)).toEqual([
      expect.stringMatching(/^options\[0\]\.floor_to_floor_heights\.typical_floor\.height_ft: /),
    ]);
  });

  it("rejects a lot size of 0: an unknown size is null with rank 'unknown'", () => {
    const study = cornerStudy();
    study.lots[0].approximate_lot_area_sq_ft = 0;
    expect(problemsOf(study)).toEqual([expect.stringMatching(/^lots\[0\]\.approximate_lot_area_sq_ft: /)]);
  });

  it("rejects an undocumented key and never echoes the document's own text", () => {
    const study = { ...copy(cornerStudy()), "SECRET-BODY-KEY": "SECRET-BODY-VALUE" };
    const problems = problemsOf(study);
    expect(problems.length).toBeGreaterThan(0);
    expect(problems.join("\n")).not.toContain("SECRET");
  });

  it("rejects a non-object body with a single bounded problem", () => {
    expect(validateStudyDocument([])).toEqual({ ok: false, problems: ["study: document is not a JSON object"] });
  });
});
