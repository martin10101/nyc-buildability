import { describe, expect, it } from "vitest";
import { LOT_SITE_SETUP_FLAG, lotSiteSetupEnabled } from "../lot-site-setup-flag";
import {
  combinationView,
  lotChoiceView,
  lotRows,
  siteFactLabel,
  siteFactRows,
  siteFactValueText,
  sourceLines,
} from "../lot-site-setup";
import { LOT_SELECTION_STATEMENT, MEASUREMENT_LABELS, type SiteFact, type Source, type Study } from "@/lib/study/study-vocabulary";
import { CROSS_BLOCK_REASON, twoLotCrossBlockStudy } from "@/components/architect/__tests__/lot-site-fixtures";

const factById = (id: string): SiteFact =>
  twoLotCrossBlockStudy.site.facts.find((fact) => fact.fact_id === id)!;

function withCombination(status: Study["lot_selection"]["combination"]["status"], reason: string | null): Study {
  return {
    ...twoLotCrossBlockStudy,
    lot_selection: { ...twoLotCrossBlockStudy.lot_selection, combination: { status, reason } },
  };
}

describe("INTERNAL_LOT_SITE_SETUP_ENABLED flag (default off)", () => {
  it("is off when absent, empty or an unknown token", () => {
    expect(lotSiteSetupEnabled({})).toBe(false);
    expect(lotSiteSetupEnabled({ [LOT_SITE_SETUP_FLAG]: "" })).toBe(false);
    expect(lotSiteSetupEnabled({ [LOT_SITE_SETUP_FLAG]: "maybe" })).toBe(false);
    expect(lotSiteSetupEnabled({ [LOT_SITE_SETUP_FLAG]: "0" })).toBe(false);
    expect(lotSiteSetupEnabled({ [LOT_SITE_SETUP_FLAG]: "false" })).toBe(false);
  });

  it("is on only for an explicit true token (trimmed, case-insensitive)", () => {
    for (const token of ["1", "true", "yes", "on", " On ", "TRUE"]) {
      expect(lotSiteSetupEnabled({ [LOT_SITE_SETUP_FLAG]: token })).toBe(true);
    }
  });
});

describe("lotChoiceView (plan §3 step 2)", () => {
  it("counts the lots and offers use-all-or-pick for more than one", () => {
    const view = lotChoiceView(twoLotCrossBlockStudy);
    expect(view.count).toBe(2);
    expect(view.heading).toBe("This property has 2 lots.");
    expect(view.pickLine).toBe("Use all (default), or pick the lots that make up the site.");
    expect(view.statement).toBe(LOT_SELECTION_STATEMENT);
  });

  it("names a single lot without a pick choice", () => {
    const single: Study = { ...twoLotCrossBlockStudy, lots: [twoLotCrossBlockStudy.lots[0]] };
    const view = lotChoiceView(single);
    expect(view.heading).toBe("This property has 1 lot.");
    expect(view.pickLine).toBe("The site is this one lot.");
  });
});

describe("lotRows", () => {
  it("shows each lot's number, size and source label", () => {
    const rows = lotRows(twoLotCrossBlockStudy);
    expect(rows).toEqual([
      { bbl: "3001230001", lotLabel: "Lot 1", sizeText: "4,000 sq ft", sourceLabel: MEASUREMENT_LABELS.approximate_tax_map, selected: true },
      { bbl: "3004560070", lotLabel: "Lot 70", sizeText: "3,200 sq ft", sourceLabel: MEASUREMENT_LABELS.city_records, selected: true },
    ]);
  });

  it("says when a lot's size is unknown", () => {
    const unknownSize: Study = {
      ...twoLotCrossBlockStudy,
      lots: [{ bbl: "3001230001", approximate_lot_area_sq_ft: null, size_measurement: { rank: "unknown", label: MEASUREMENT_LABELS.unknown }, selected: true }],
    };
    expect(lotRows(unknownSize)[0].sizeText).toBe("Size unknown");
  });
});

describe("combinationView — the refusal comes from B-07, never recomputed here", () => {
  it("passes through the not-offered reason verbatim", () => {
    const view = combinationView(twoLotCrossBlockStudy);
    expect(view.refused).toBe(true);
    expect(view.heading).toBe("These lots were not combined");
    expect(view.detail).toBe(CROSS_BLOCK_REASON);
  });

  it("states a combined site without claiming verification", () => {
    const view = combinationView(withCombination("offered", null));
    expect(view.refused).toBe(false);
    expect(view.heading).toBe("Shown as one site");
    expect(view.detail).toContain("on one block and touch");
  });

  it("names one lot with no combination", () => {
    const view = combinationView(withCombination("single_lot", null));
    expect(view.refused).toBe(false);
    expect(view.heading).toBe("One lot");
    expect(view.detail).toBeNull();
  });
});

describe("site facts with source labels (plan §3 step 3, §4)", () => {
  it("formats numbers with units, words plainly, and keeps an unknown unknown", () => {
    expect(siteFactValueText(factById("fact-lot-area-a"))).toBe("4,000 sq ft");
    expect(siteFactValueText(factById("fact-lot-type"))).toBe("Corner");
    expect(siteFactValueText(factById("fact-zoning-district"))).toBe("R6B");
    expect(siteFactValueText(factById("fact-street-width-unknown"))).toBe(MEASUREMENT_LABELS.unknown);
  });

  it("labels a fact, naming the street for a per-street value", () => {
    expect(siteFactLabel(factById("fact-lot-area-a"))).toBe("Lot area");
    const streetLabel = siteFactLabel(factById("fact-street-width-unknown"));
    expect(streetLabel).toContain("Street width");
    expect(streetLabel).toContain("Example Avenue");
  });

  it("names what an unknown value blocks, in plain English", () => {
    const rows = siteFactRows(twoLotCrossBlockStudy);
    const unknown = rows.find((row) => row.factId === "fact-street-width-unknown")!;
    expect(unknown.isUnknown).toBe(true);
    expect(unknown.blocks).toEqual(["permitted envelope", "building option"]);
    const known = rows.find((row) => row.factId === "fact-lot-area-a")!;
    expect(known.isUnknown).toBe(false);
    expect(known.blocks).toEqual([]);
    expect(known.sourceLabel).toBe(MEASUREMENT_LABELS.approximate_tax_map);
  });
});

describe("sourceLines (plain English, internal query URL never surfaced)", () => {
  const base: Omit<Source, "kind"> = {
    dataset: null,
    dataset_version: null,
    retrieved_at: "2026-09-30T12:02:00Z",
    query_ref: "internal://never-shown",
    document_ref: null,
    statement: null,
  };

  it("summarises a dataset with its version and date", () => {
    const lines = sourceLines(factById("fact-lot-type").source);
    expect(lines).toContain("test-fixture-synthetic PLUTO-shaped record (test-fixture-synthetic)");
    expect(lines).toContain("Recorded 2026-09-30.");
    expect(lines.join(" ")).not.toContain("internal://");
    expect(lines.join(" ")).not.toContain("pluto/");
  });

  it("explains an entered, assumed, survey, filing and absent source", () => {
    expect(sourceLines({ ...base, kind: "architect_entry" })).toContain("Entered by you.");
    expect(sourceLines({ ...base, kind: "assumption", statement: "Assumed 60 ft from the adjacent street." }))
      .toContain("Assumed 60 ft from the adjacent street.");
    expect(sourceLines({ ...base, kind: "survey", document_ref: "Survey 2026-14" })).toContain("Survey: Survey 2026-14");
    expect(sourceLines({ ...base, kind: "city_filing", dataset: "DOB NOW", document_ref: "Job 123" })).toContain("Filing: Job 123");
    expect(sourceLines(null)).toEqual(["No source recorded — this value was not found and must be entered."]);
  });
});
