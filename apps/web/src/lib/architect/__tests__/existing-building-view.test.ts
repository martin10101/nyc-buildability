import { describe, expect, it } from "vitest";
import existingZfaUnknownStudy from "../../../../../../packages/contracts/fixtures/valid/study/synthetic_copied_from_export_existing_zfa_unknown.json";
import assumedExistingZfaFact from "../../../../../../packages/contracts/fixtures/valid/site_fact/synthetic_existing_zoning_floor_area_assumed.json";
import { validateStudyDocument } from "@/lib/study/study-validator";
import {
  EXISTING_BUILDING_PLANS,
  MEASUREMENT_LABELS,
  type SiteFact,
  type Study,
} from "@/lib/study/study-vocabulary";
import { ENTER_POSITIVE_NUMBER, ENTER_VALUE_FIRST } from "../lot-site-setup";
import { UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT } from "../unused-floor-area";
import {
  EXISTING_BUILDING_PLAN_LABELS,
  FACE_TEXT_MAX_CHARS,
  buildExistingFloorAreaFact,
  existingBuildingFaceBudget,
  existingBuildingPlanOptions,
  existingFloorAreaFact,
  existingFloorAreaGroup,
  selectedOptionPlan,
  validateExistingFloorAreaInput,
} from "../existing-building-view";

const unknownStudy = existingZfaUnknownStudy as unknown as Study;
const assumedFact = assumedExistingZfaFact as unknown as SiteFact;
const unknownExistingFact = unknownStudy.site.facts.find(
  (fact) => fact.key === "existing_zoning_floor_area",
) as SiteFact;

/** The unknown-fixture study with its existing-zfa fact replaced, re-proved contract-valid. */
function studyWithExistingFact(fact: SiteFact): Study {
  const study = structuredClone(unknownStudy);
  study.site.facts = study.site.facts.map((existing) =>
    existing.key === "existing_zoning_floor_area" ? structuredClone(fact) : existing,
  );
  return study;
}

describe("existing-building-view — the three-way plan choice (plan §3 step 4)", () => {
  it("maps every closed plan value to plain words, with no raw token", () => {
    for (const value of EXISTING_BUILDING_PLANS) {
      const label = EXISTING_BUILDING_PLAN_LABELS[value];
      expect(label).toBeTruthy();
      expect(label).not.toContain("_");
    }
    expect(EXISTING_BUILDING_PLAN_LABELS.keep).toBe("Keep the existing building");
    expect(EXISTING_BUILDING_PLAN_LABELS.remove).toBe("Remove the existing building");
    expect(EXISTING_BUILDING_PLAN_LABELS.no_existing_building).toBe("No existing building");
  });

  it("offers the three choices in the vocabulary's own order", () => {
    expect(existingBuildingPlanOptions().map((option) => option.value)).toEqual([
      ...EXISTING_BUILDING_PLANS,
    ]);
  });

  it("reads the selected option's plan (the shown value, never a silent keep/remove)", () => {
    expect(selectedOptionPlan(unknownStudy)).toBe("keep");
    const removed = structuredClone(unknownStudy);
    removed.options[0].existing_building_plan = "remove";
    expect(selectedOptionPlan(removed)).toBe("remove");
  });
});

describe("existing-building-view — the existing zoning floor area fact", () => {
  it("finds an unknown fact and shows what it blocks (keep, none established)", () => {
    const group = existingFloorAreaGroup(unknownStudy.site.facts);
    expect(group).not.toBeNull();
    expect(group!.primary.isUnknown).toBe(true);
    expect(group!.primary.valueText).toBe(MEASUREMENT_LABELS.unknown);
    // The blocks come from the fact itself, in plain words (remaining capacity, keep / rebuild).
    expect(group!.primary.blocks).toEqual(["remaining capacity", "keep / rebuild comparison"]);
  });

  it("finds a known fact and shows its value with its source label (keep, established)", () => {
    const group = existingFloorAreaGroup([assumedFact]);
    expect(group!.primary.isUnknown).toBe(false);
    expect(group!.primary.valueText).toBe("6,200 sq ft");
    expect(group!.primary.sourceLabel).toBe(MEASUREMENT_LABELS.assumed);
  });

  it("returns null when the study carries no existing-zfa fact (the server-absent edge)", () => {
    expect(existingFloorAreaGroup([])).toBeNull();
    expect(existingFloorAreaFact([])).toBeNull();
  });
});

describe("existing-building-view — validate the typed value (same words as a per-fact edit)", () => {
  it("accepts a number greater than zero", () => {
    expect(validateExistingFloorAreaInput("6200")).toEqual({ ok: true, value: 6200 });
  });
  it("rejects zero, a negative, a non-number and empty with the validator's message", () => {
    expect(validateExistingFloorAreaInput("0")).toEqual({ ok: false, reason: ENTER_POSITIVE_NUMBER });
    expect(validateExistingFloorAreaInput("-5")).toEqual({ ok: false, reason: ENTER_POSITIVE_NUMBER });
    expect(validateExistingFloorAreaInput("abc")).toEqual({ ok: false, reason: ENTER_POSITIVE_NUMBER });
    expect(validateExistingFloorAreaInput("   ")).toEqual({ ok: false, reason: ENTER_VALUE_FIRST });
  });
});

describe("existing-building-view — build the entered fact with the chosen allowed source", () => {
  it("builds an architect-entry fact (rank Entered), never a city source, and it is contract-valid", () => {
    const fact = buildExistingFloorAreaFact(unknownExistingFact, "5999999998", 6200, "architect_entry", "2026-10-03T09:00:00Z");
    expect(fact.source?.kind).toBe("architect_entry");
    expect(fact.measurement).toEqual({ rank: "entered", label: MEASUREMENT_LABELS.entered });
    expect(fact.unit).toBe("square_feet");
    expect(fact.value).toBe(6200);
    expect(validateStudyDocument(studyWithExistingFact(fact)).ok).toBe(true);
  });

  it("builds a stated-assumption fact (rank Assumed) with the assumption stated, and it is contract-valid", () => {
    const fact = buildExistingFloorAreaFact(unknownExistingFact, "5999999998", 6200, "assumption", "2026-10-03T09:00:00Z");
    expect(fact.source?.kind).toBe("assumption");
    expect(fact.measurement).toEqual({ rank: "assumed", label: MEASUREMENT_LABELS.assumed });
    expect(fact.source?.statement).toContain("6,200");
    expect(validateStudyDocument(studyWithExistingFact(fact)).ok).toBe(true);
  });

  it("never writes a city source kind for either choice", () => {
    for (const kind of ["architect_entry", "assumption"] as const) {
      const fact = buildExistingFloorAreaFact(unknownExistingFact, "5999999998", 100, kind, "2026-10-03T09:00:00Z");
      expect(["city_dataset", "city_filing", "tax_map_computation"]).not.toContain(fact.source?.kind);
    }
  });

  it("keeps a kept CITY filing beside the entered value (a city value is never overwritten in place)", () => {
    const cityFiling: SiteFact = {
      ...unknownExistingFact,
      fact_id: "fact-existing-zfa",
      value: 8000,
      unit: "square_feet",
      measurement: { rank: "city_records", label: MEASUREMENT_LABELS.city_records },
      source: {
        kind: "city_filing",
        dataset: "test-fixture-synthetic DOB filings",
        dataset_version: null,
        retrieved_at: "2026-09-30T12:00:00Z",
        query_ref: null,
        document_ref: "test-fixture-synthetic-job-1",
        statement: null,
      },
      blocks: [],
    };
    const entered = buildExistingFloorAreaFact(cityFiling, "5999999998", 6200, "architect_entry", "2026-10-03T09:00:00Z");
    expect(entered.fact_id).toBe("fact-existing-zfa-entered");
  });
});

describe("existing-building-view — §5a face budget and settled wording", () => {
  it("keeps every app-authored face string within the budget and adds no notice block", () => {
    const budget = existingBuildingFaceBudget();
    for (const text of budget.appStrings) expect(text.length).toBeLessThanOrEqual(FACE_TEXT_MAX_CHARS);
    expect(budget.noticeCount).toBe(0);
  });

  it("does not touch the owner-settled remaining-capacity wording", () => {
    // The step computes no remaining capacity; the settled wording stays byte-identical elsewhere.
    expect(UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT).toBe("Remaining development capacity: Not confirmed");
  });
});
