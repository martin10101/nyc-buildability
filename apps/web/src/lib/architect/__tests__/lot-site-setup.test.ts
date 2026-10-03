import { describe, expect, it } from "vitest";
import cornerLotStudy from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_corner_lot_two_options.json";
import { LOT_SITE_SETUP_FLAG, lotSiteSetupEnabled } from "../lot-site-setup-flag";
import {
  FACE_TEXT_MAX_CHARS,
  SITE_FACTS_INTRO,
  SITE_SETUP_NOT_CONNECTED,
  applyEnteredFactToSource,
  combinationView,
  combinationViewOf,
  groupSiteFactRows,
  lotChoiceView,
  lotChoiceViewOf,
  lotRows,
  lotSiteSetupFaceBudget,
  siteFactLabel,
  siteFactRows,
  siteFactRowsOf,
  siteFactValueText,
  sourceFromSetup,
  sourceFromStudy,
  sourceLines,
  validateFactInput,
  type LotSiteSource,
} from "../lot-site-setup";
import { enterSiteFactValue } from "@/lib/study/study-operations";
import { LOT_SELECTION_STATEMENT, MEASUREMENT_LABELS, type SiteFact, type Source, type Study } from "@/lib/study/study-vocabulary";
import type { StudySetup } from "@/lib/study/study-setup-api";
import { CROSS_BLOCK_REASON, twoLotCrossBlockStudy, twoLotOfferedStudy } from "@/components/architect/__tests__/lot-site-fixtures";

const corner = cornerLotStudy as unknown as Study;
const EDIT_AT = "2026-10-02T09:00:00Z";
/** A deep-cloned source so no test shares a mutable fixture. */
const cornerSource = (): LotSiteSource =>
  sourceFromStudy(structuredClone(corner) as unknown as Study);

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

  it("states the offered selection as a neutral fact, with no adjacency or verification claim", () => {
    const view = combinationView(twoLotOfferedStudy);
    expect(view.refused).toBe(false);
    expect(view.heading).toBe("Lots shown together");
    expect(view.detail).toBe("These are the lots you selected.");
    // B-07 gives no reason for an offered combination, so the app must not author an
    // adjacency ("touch", "one block") or verification conclusion in its own voice.
    const text = `${view.heading} ${view.detail}`.toLowerCase();
    expect(text).not.toContain("touch");
    expect(text).not.toContain("one block");
    expect(text).not.toContain("verif");
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

describe("LotSiteSource — a study and a server setup reduce to the same display source", () => {
  it("re-keys a study into lots, selection and site facts", () => {
    const source = sourceFromStudy(twoLotCrossBlockStudy);
    expect(source.lots).toBe(twoLotCrossBlockStudy.lots);
    expect(source.lotSelection.combination).toEqual({ status: "not_offered", reason: CROSS_BLOCK_REASON });
    expect(source.siteFacts).toBe(twoLotCrossBlockStudy.site.facts);
  });

  it("re-keys a setup, and the source-based views match the study-based views", () => {
    const setup: StudySetup = {
      property: twoLotCrossBlockStudy.property,
      lots: twoLotCrossBlockStudy.lots,
      lotSelection: twoLotCrossBlockStudy.lot_selection,
      siteFacts: twoLotCrossBlockStudy.site.facts,
    };
    const source = sourceFromSetup(setup);
    expect(lotChoiceViewOf(source)).toEqual(lotChoiceView(twoLotCrossBlockStudy));
    expect(combinationViewOf(source.lotSelection)).toEqual(combinationView(twoLotCrossBlockStudy));
    expect(siteFactRowsOf(source.siteFacts)).toEqual(siteFactRows(twoLotCrossBlockStudy));
  });
});

describe("validateFactInput (plain words, no computation)", () => {
  const area = corner.site.facts.find((fact) => fact.key === "lot_area")!;
  const lotType = corner.site.facts.find((fact) => fact.key === "lot_type")!;
  const district = corner.site.facts.find((fact) => fact.key === "zoning_district")!;

  it("accepts a positive measured number and rejects zero, negatives and non-numbers", () => {
    expect(validateFactInput(area, "10500")).toEqual({ ok: true, value: 10500 });
    expect(validateFactInput(area, " 4200.5 ")).toEqual({ ok: true, value: 4200.5 });
    expect(validateFactInput(area, "0")).toEqual({ ok: false, reason: "Enter a number greater than zero." });
    expect(validateFactInput(area, "-5")).toEqual({ ok: false, reason: "Enter a number greater than zero." });
    expect(validateFactInput(area, "wide")).toEqual({ ok: false, reason: "Enter a number greater than zero." });
    expect(validateFactInput(area, "   ")).toEqual({ ok: false, reason: "Enter a value first." });
  });

  it("holds lot type to the three plain words and keeps other text non-empty", () => {
    expect(validateFactInput(lotType, "Interior")).toEqual({ ok: true, value: "interior" });
    expect(validateFactInput(lotType, "cul-de-sac")).toEqual({
      ok: false,
      reason: "Enter one of: corner, interior or through.",
    });
    expect(validateFactInput(district, "R7A")).toEqual({ ok: true, value: "R7A" });
  });
});

describe("applyEnteredFactToSource — the setup-only mirror of enterSiteFactValue", () => {
  it("keeps a city value and adds the entered value beside it under <id>-entered", () => {
    const source = cornerSource();
    const result = applyEnteredFactToSource(source, "fact-lot-area", 10500, EDIT_AT);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    // The original city fact is untouched…
    const original = result.source.siteFacts.find((fact) => fact.fact_id === "fact-lot-area")!;
    expect(original.value).toBe(5000);
    expect(original.source?.kind).toBe("tax_map_computation");
    // …and the entered fact sits beside it.
    const entered = result.source.siteFacts.find((fact) => fact.fact_id === "fact-lot-area-entered")!;
    expect(entered.value).toBe(10500);
    expect(entered.unit).toBe("square_feet");
    expect(entered.measurement).toEqual({ rank: "entered", label: MEASUREMENT_LABELS.entered });
    expect(entered.source?.kind).toBe("architect_entry");
  });

  it("produces the SAME entered fact the C-05 store's enterSiteFactValue produces (anti-drift)", () => {
    const entry = { study: structuredClone(corner) as unknown as Study, staleOptionIds: [], parcelChoices: null };
    const stored = enterSiteFactValue(entry, { factId: "fact-lot-area", value: 10500 }, EDIT_AT);
    expect(stored.ok).toBe(true);
    if (!stored.ok) return;
    const storeEntered = stored.entry.study.site.facts.find((fact) => fact.fact_id === "fact-lot-area-entered")!;

    const local = applyEnteredFactToSource(cornerSource(), "fact-lot-area", 10500, EDIT_AT);
    expect(local.ok).toBe(true);
    if (!local.ok) return;
    const localEntered = local.source.siteFacts.find((fact) => fact.fact_id === "fact-lot-area-entered")!;

    expect(localEntered).toEqual(storeEntered);
  });

  it("replaces a non-city value in place rather than adding a sibling", () => {
    // The corner study's street-width facts are architect entries (non-city).
    const source = cornerSource();
    const before = source.siteFacts.length;
    const result = applyEnteredFactToSource(source, "fact-street-width-a", 80, EDIT_AT);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.source.siteFacts.length).toBe(before); // replaced, not added
    const edited = result.source.siteFacts.find((fact) => fact.fact_id === "fact-street-width-a")!;
    expect(edited.value).toBe(80);
    expect(edited.measurement.rank).toBe("entered");
  });

  it("refuses an unknown fact id without changing anything", () => {
    expect(applyEnteredFactToSource(cornerSource(), "fact-missing", 1, EDIT_AT)).toEqual({
      ok: false,
      reason: "That value is not part of this site.",
    });
  });
});

describe("groupSiteFactRows — the entered value groups with its city fact", () => {
  it("pairs <id> and <id>-entered into one group and leaves others standalone", () => {
    const edited = applyEnteredFactToSource(cornerSource(), "fact-lot-area", 10500, EDIT_AT);
    expect(edited.ok).toBe(true);
    if (!edited.ok) return;
    const groups = groupSiteFactRows(siteFactRowsOf(edited.source.siteFacts));
    const lotArea = groups.find((group) => group.primary.factId === "fact-lot-area")!;
    expect(lotArea.primary.valueText).toBe("5,000 sq ft");
    expect(lotArea.entered?.factId).toBe("fact-lot-area-entered");
    expect(lotArea.entered?.valueText).toBe("10,500 sq ft");
    expect(lotArea.entered?.sourceLabel).toBe(MEASUREMENT_LABELS.entered);
    // No "-entered" row is rendered as its own group.
    expect(groups.some((group) => group.primary.factId === "fact-lot-area-entered")).toBe(false);
    // An un-edited fact has no entered sibling.
    const district = groups.find((group) => group.primary.key === "zoning_district")!;
    expect(district.entered).toBeNull();
  });
});

describe("lotSiteSetupFaceBudget — §5a face-text budget (D-090-R082)", () => {
  it("keeps the trimmed section copy within budget and names the dropped restatement", () => {
    expect(SITE_FACTS_INTRO.length).toBeLessThanOrEqual(FACE_TEXT_MAX_CHARS);
    expect(SITE_SETUP_NOT_CONNECTED.length).toBeLessThanOrEqual(FACE_TEXT_MAX_CHARS);
    // R082: the earlier restatement ("Nothing here has to be typed…") is gone; the
    // intro still names the one fact the architect needs (source + override).
    expect(SITE_FACTS_INTRO).toContain("Each value shows its source");
    expect(SITE_FACTS_INTRO).not.toContain("Nothing here has to be typed");
    // The empty-state line reads as a fact, not a caution.
    expect(SITE_SETUP_NOT_CONNECTED).toContain("No measurement is guessed");
    expect(SITE_SETUP_NOT_CONNECTED.toLowerCase()).not.toContain("prepared by");
  });

  it("exempts the pinned statement and B-07's refusal, budgets the app leads, ≤3 notices (refused)", () => {
    const budget = lotSiteSetupFaceBudget(sourceFromStudy(twoLotCrossBlockStudy));
    expect(budget.noticeCount).toBeLessThanOrEqual(3);
    // Pinned (verbatim, exempt): the owner statement and B-07's refusal reason.
    expect(budget.pinned).toContain(LOT_SELECTION_STATEMENT);
    expect(budget.pinned).toContain(CROSS_BLOCK_REASON);
    // App-authored leads are length-budgeted and carry the trimmed intro.
    expect(budget.appStrings).toContain(SITE_FACTS_INTRO);
    expect(budget.appStrings).toContain("This property has 2 lots.");
    expect(budget.appStrings).toContain("These lots were not combined");
    for (const line of budget.appStrings) {
      expect(line.length).toBeLessThanOrEqual(FACE_TEXT_MAX_CHARS);
    }
    // B-07's reason stays out of the length budget (it may be long, by design).
    expect(budget.appStrings).not.toContain(CROSS_BLOCK_REASON);
  });

  it("budgets the app's own offered line (no B-07 reason to pin)", () => {
    const budget = lotSiteSetupFaceBudget(sourceFromStudy(twoLotOfferedStudy));
    expect(budget.pinned).toEqual([LOT_SELECTION_STATEMENT]);
    expect(budget.appStrings).toContain("These are the lots you selected.");
  });
});
