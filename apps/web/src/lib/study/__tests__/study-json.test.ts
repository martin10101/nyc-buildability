import { describe, expect, it } from "vitest";
import invalidGoalOther from "../../../../../../packages/contracts/fixtures/invalid/study/goal_other_without_text.json";
import invalidNestedZero from "../../../../../../packages/contracts/fixtures/invalid/study/site_fact_unknown_encoded_as_zero.json";
import { MAX_STUDY_JSON_LENGTH, exportStudyJson, importStudyJson } from "../study-json";
import { studyEntryFromDocument } from "../study-operations";
import type { Study } from "../study-vocabulary";
import { SYNTHETIC_BBL, cornerStudy, expectOk } from "./study-test-data";

function withoutAnnotation(value: unknown): Record<string, unknown> {
  const document = JSON.parse(JSON.stringify(value)) as Record<string, unknown>;
  delete document._expected_failure;
  return document;
}

describe("study JSON boundary", () => {
  it("exports a valid study and imports it back unchanged", () => {
    const exported = exportStudyJson(cornerStudy());
    if (!exported.ok) throw new Error(exported.problems.join("; "));
    const imported = importStudyJson(exported.json, SYNTHETIC_BBL);
    expect(imported).toEqual({ ok: true, study: cornerStudy() });
  });

  it("exports the store's document, not its out-of-date flags", () => {
    const entry = expectOk(studyEntryFromDocument(cornerStudy()));
    const exported = exportStudyJson(entry.study);
    if (!exported.ok) throw new Error(exported.problems.join("; "));
    expect(JSON.parse(exported.json)).toEqual(cornerStudy());
    expect(exported.json).not.toContain("staleOptionIds");
  });

  it.each<[string, unknown, string]>([
    ["goal_other_without_text", invalidGoalOther, "options[1].goal.text"],
    ["site_fact_unknown_encoded_as_zero", invalidNestedZero, "site.facts[3]"],
  ])("rejects the invalid fixture %s on import", (_name, fixture, path) => {
    const result = importStudyJson(JSON.stringify(withoutAnnotation(fixture)));
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
    if (result.ok) return;
    expect(result.problems.some((problem) => problem.startsWith(path))).toBe(true);
  });

  it("rejects a fixture file as committed (it carries the fixture-only annotation)", () => {
    const result = importStudyJson(JSON.stringify(invalidGoalOther));
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
    if (result.ok) return;
    expect(result.problems.some((problem) => problem.includes("fixture-only key"))).toBe(true);
  });

  it("rejects text that is not JSON, an oversized file, and a study for another property", () => {
    expect(importStudyJson("{not json")).toMatchObject({ ok: false, code: "invalid_json" });
    expect(importStudyJson(" ".repeat(MAX_STUDY_JSON_LENGTH + 1))).toMatchObject({ ok: false, code: "too_large" });
    const exported = exportStudyJson(cornerStudy());
    if (!exported.ok) throw new Error(exported.problems.join("; "));
    expect(importStudyJson(exported.json, "5999999998")).toMatchObject({ ok: false, code: "wrong_property" });
  });

  it("never writes an invalid document", () => {
    const study = cornerStudy();
    study.options[0].floor_to_floor_heights.ground_floor.height_ft = Number.NaN;
    expect(exportStudyJson(study)).toMatchObject({ ok: false, code: "invalid_document" });
    const reworded = { ...cornerStudy(), lot_selection: { ...cornerStudy().lot_selection, statement: "Zoning lot verified" } };
    expect(exportStudyJson(reworded as unknown as Study)).toMatchObject({ ok: false, code: "invalid_document" });
  });
});
