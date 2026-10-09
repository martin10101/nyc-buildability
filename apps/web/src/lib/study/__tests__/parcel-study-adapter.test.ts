import { describe, expect, it } from "vitest";
import {
  createParcelStudy,
  deriveParcelStudyScope,
  exportParcelStudy,
  type ParcelStudyDraft,
  type ParcelStudyScope,
} from "../../architect/parcel-study";
import {
  applyParcelStudyDraft,
  parcelStudyDraftFromStudyEntry,
  parcelStudyPropertyBbl,
  studyEntryFromParcelStudyDraft,
  type ParcelStudyInit,
} from "../parcel-study-adapter";
import { updateOptionInputs, upsertSiteFact } from "../study-operations";
import { T1, T2, enteredStreetWidth, expectOk, newStudyResult, optionInputs } from "./study-test-data";

// The same recorded condo identities the parcel-study tests use (no network).
const BILLING = "3022647515";
const LOT_32 = "3022640032";
const LOT_33 = "3022640033";

function scope(billingBbl: string | null = BILLING, baseBbls = [LOT_32, LOT_33]): ParcelStudyScope {
  const result = deriveParcelStudyScope({
    enteredBbl: BILLING,
    billingBbl,
    baseLots: baseBbls.map((bbl) => ({ bbl })),
  });
  if (!result.ok) throw new Error(result.message);
  return result.scope;
}

function init(): ParcelStudyInit {
  return {
    studyId: "test-fixture-synthetic-parcel-study",
    address: null,
    // Test value: the adapter never infers whether lots can be combined.
    combination: { status: "not_offered", reason: "Test fixture: contiguity not checked" },
    initialOption: { optionId: "option-a", name: "Option A", inputs: optionInputs() },
    at: "2026-09-30T12:00:00Z",
  };
}

function edited(base: ParcelStudyScope = scope()): ParcelStudyDraft {
  return {
    ...createParcelStudy(base),
    arrangement: "together",
    buildingScheme: "multiple",
    existingBuildings: [
      { bbl: LOT_32, intent: "retain" },
      { bbl: LOT_33, intent: "demolish" },
    ],
  };
}

describe("ParcelStudyDraft <-> shared study (lossless)", () => {
  it.each<[string, ParcelStudyDraft]>([
    ["a new draft", createParcelStudy(scope())],
    ["an edited draft", edited()],
    ["a draft without a billing record", edited(scope(null))],
    ["a separate-sites draft", { ...edited(), arrangement: "separate", existingBuildings: [
      { bbl: LOT_32, intent: "alter" }, { bbl: LOT_33, intent: "undecided" },
    ] }],
  ])("round-trips %s byte for byte", (_name, draft) => {
    const entry = expectOk(studyEntryFromParcelStudyDraft(draft, init()));
    const back = parcelStudyDraftFromStudyEntry(entry);
    expect(back).toEqual({ ok: true, draft });
    if (!back.ok) throw new Error(back.message);
    expect(JSON.stringify(back.draft)).toBe(JSON.stringify(draft));
    expect(exportParcelStudy(back.draft, back.draft.scope)).toEqual(exportParcelStudy(draft, draft.scope));
  });

  it("maps the property and base lots into the study; unknown sizes stay unknown, never 0", () => {
    const entry = expectOk(studyEntryFromParcelStudyDraft(edited(), init()));
    expect(entry.study.property).toEqual({ bbl: BILLING, address: null });
    expect(entry.study.lots).toEqual([LOT_32, LOT_33].map((bbl) => ({
      bbl,
      approximate_lot_area_sq_ft: null,
      size_measurement: { rank: "unknown", label: "Unknown — enter" },
      selected: true,
    })));
    expect(entry.study.lot_selection.combination).toEqual(init().combination);
    expect(entry.study.options).toHaveLength(1);
    expect(parcelStudyPropertyBbl(scope())).toBe(BILLING);
    expect(parcelStudyPropertyBbl(scope(null))).toBe(BILLING);
  });

  it("keeps the draft through option and site edits of the shared study", () => {
    const draft = edited();
    let entry = expectOk(studyEntryFromParcelStudyDraft(draft, init()));
    entry = expectOk(updateOptionInputs(entry, "option-a", { existing_building_plan: "keep" }, T1));
    entry = expectOk(upsertSiteFact(entry, enteredStreetWidth("fact-street-width-a", "Synthetic Street A", 60), T2));
    expect(parcelStudyDraftFromStudyEntry(entry)).toEqual({ ok: true, draft });
  });

  it("applies an edited draft as a site change: a new revision, every option out of date", () => {
    const start = expectOk(studyEntryFromParcelStudyDraft(createParcelStudy(scope()), init()));
    const next = expectOk(applyParcelStudyDraft(start, edited(), T1));
    expect(next.study.revision).toEqual({ number: 2, created_at: T1, parent: 1 });
    expect(next.staleOptionIds).toEqual(["option-a"]);
    expect(next.study.options).toBe(start.study.options);
    expect(parcelStudyDraftFromStudyEntry(next)).toEqual({ ok: true, draft: edited() });
    expect(expectOk(applyParcelStudyDraft(next, edited(), T2))).toBe(next);
  });

  it("refuses a draft for another parcel set, and an invalid draft", () => {
    const start = expectOk(studyEntryFromParcelStudyDraft(createParcelStudy(scope()), init()));
    const other = createParcelStudy(scope(BILLING, [LOT_32, "3022640034"]));
    expect(applyParcelStudyDraft(start, other, T1)).toMatchObject({ ok: false, code: "parcel_scope_changed" });
    const missingLot = { ...edited(), existingBuildings: [{ bbl: LOT_32, intent: "retain" as const }] };
    expect(applyParcelStudyDraft(start, missingLot, T1)).toMatchObject({ ok: false, code: "invalid_parcel_draft" });
    expect(studyEntryFromParcelStudyDraft(missingLot, init())).toMatchObject({
      ok: false,
      code: "invalid_parcel_draft",
    });
  });

  it("a study not started from a parcel study has no draft", () => {
    const entry = expectOk(newStudyResult());
    expect(parcelStudyDraftFromStudyEntry(entry)).toMatchObject({ ok: false, code: "not_a_parcel_study" });
  });
});
