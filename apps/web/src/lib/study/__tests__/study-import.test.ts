import { describe, expect, it } from "vitest";
import copiedFromExport from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_copied_from_export_existing_zfa_unknown.json";
import { factsToRefetch, startStudyFromImport, type StartFromImportInput } from "../study-import";
import { exportStudyJson, importStudyJson } from "../study-json";
import { createStudyStore } from "../study-store";
import type { Combination, Study } from "../study-vocabulary";
import { SYNTHETIC_BBL, T1, cornerStudy, expectOk } from "./study-test-data";

/**
 * Review correction 1 (plan section 9 "Historical exports"): nothing imported
 * becomes a current fact or result. A study read from a file starts a NEW study
 * holding only the architect's inputs; every fact is left to be re-fetched.
 */

const SINGLE_LOT: Combination = { status: "single_lot", reason: null };

function start(exportId: string | null = null): StartFromImportInput {
  return { studyId: "test-fixture-synthetic-study-copy", at: T1, exportId, combination: SINGLE_LOT };
}

/** The corner fixture as it arrives from a file (export -> import). */
function fileStudy(document: Study = cornerStudy()): Study {
  const exported = exportStudyJson(document);
  if (!exported.ok) throw new Error(exported.problems.join("; "));
  const imported = importStudyJson(exported.json, document.property.bbl);
  if (!imported.ok) throw new Error(imported.problems.join("; "));
  return imported.study;
}

describe("starting a study from an imported file copies inputs only", () => {
  it("keeps the architect's entered values and drops every city fact and unknown placeholder", () => {
    const file = fileStudy();
    const entry = expectOk(startStudyFromImport(file, start()));
    // The corner file carries 6 city-sourced facts and 2 entered street widths.
    expect(entry.study.site.facts.map((fact) => fact.fact_id)).toEqual(["fact-street-width-a", "fact-street-width-b"]);
    expect(entry.study.site.facts.every((fact) => fact.measurement.rank === "entered")).toBe(true);
    expect(factsToRefetch(file).map((fact) => fact.fact_id)).toEqual([
      "fact-lot-area",
      "fact-frontage-a",
      "fact-frontage-b",
      "fact-lot-depth",
      "fact-lot-type",
      "fact-zoning-district",
    ]);
  });

  it("resets a lot size that came from city data to unknown, keeping the lot choice", () => {
    const entry = expectOk(startStudyFromImport(fileStudy(), start()));
    expect(entry.study.lots).toEqual([
      {
        bbl: SYNTHETIC_BBL,
        approximate_lot_area_sq_ft: null,
        size_measurement: { rank: "unknown", label: "Unknown — enter" },
        selected: true,
      },
    ]);
  });

  it("keeps a lot size the architect entered", () => {
    const document = cornerStudy();
    document.lots[0].size_measurement = { rank: "entered", label: "Entered" };
    const entry = expectOk(startStudyFromImport(fileStudy(document), start()));
    expect(entry.study.lots[0].approximate_lot_area_sq_ft).toBe(5000);
  });

  it("never makes a hand-edited 'City records' value current", () => {
    const document = cornerStudy();
    const lotArea = document.site.facts[0];
    lotArea.value = 99999;
    lotArea.measurement = { rank: "city_records", label: "City records" };
    lotArea.source = {
      kind: "city_dataset",
      dataset: "test-fixture-synthetic PLUTO-shaped record",
      dataset_version: null,
      retrieved_at: "2026-09-30T12:00:00Z",
      query_ref: "test-fixture-synthetic://pluto/5999999999",
      document_ref: null,
      statement: null,
    };
    const entry = expectOk(startStudyFromImport(fileStudy(document), start()));
    expect(entry.study.site.facts.some((fact) => fact.fact_id === "fact-lot-area")).toBe(false);
    expect(entry.study.site.facts.some((fact) => fact.value === 99999)).toBe(false);
    expect(entry.study.lots[0].approximate_lot_area_sq_ft).toBeNull();
  });

  it("copies the options and the selected option; no result is imported", () => {
    const document = cornerStudy();
    document.selected_option_id = "opt-b";
    const file = fileStudy(document);
    const entry = expectOk(startStudyFromImport(file, start()));
    expect(entry.study.options).toEqual(file.options);
    expect(entry.study.selected_option_id).toBe("opt-b");
    expect(entry.staleOptionIds).toEqual(["opt-a", "opt-b"]);
  });

  it("is a new study at revision 1, whatever revision and origin the file claims", () => {
    const document = cornerStudy();
    document.revision = { number: 7, created_at: "2026-09-30T12:05:00Z", parent: 6 };
    const entry = expectOk(startStudyFromImport(fileStudy(document), start()));
    expect(entry.study.study_id).toBe("test-fixture-synthetic-study-copy");
    expect(entry.study.revision).toEqual({ number: 1, created_at: T1, parent: null });
    expect(entry.study.origin).toEqual({ kind: "new", export_id: null });
  });

  it("names the export it was copied from", () => {
    const entry = expectOk(startStudyFromImport(fileStudy(), start("test-fixture-synthetic-export-001")));
    expect(entry.study.origin).toEqual({ kind: "copied_from_export", export_id: "test-fixture-synthetic-export-001" });
  });

  it("takes the combination from site setup, never from the file", () => {
    const document = JSON.parse(JSON.stringify(copiedFromExport)) as Study;
    const notOffered: Combination = { status: "not_offered", reason: "Test fixture: lots do not touch" };
    const entry = expectOk(startStudyFromImport(document, { ...start(), combination: notOffered }));
    expect(entry.study.lot_selection.combination).toEqual(notOffered);
    // The copied-from-export fixture has only city and unknown facts: nothing is copied.
    expect(entry.study.site.facts).toEqual([]);
  });

  it("refuses an invalid document", () => {
    const document = cornerStudy();
    document.options[0].program = [];
    expect(startStudyFromImport(document, start())).toMatchObject({ ok: false, code: "invalid_document" });
  });

  it("the store holds only the started study, never the file", () => {
    const store = createStudyStore();
    const file = fileStudy();
    expectOk(store.replace(startStudyFromImport(file, start())));
    expect(store.get(SYNTHETIC_BBL)?.study.site.facts).toHaveLength(2);
    expect(store.get(SYNTHETIC_BBL)?.study.study_id).not.toBe(file.study_id);
  });
});
