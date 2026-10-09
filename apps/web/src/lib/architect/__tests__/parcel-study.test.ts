import { describe, expect, it } from "vitest";
import {
  MAX_PARCEL_STUDY_JSON_LENGTH,
  createParcelStudy,
  deriveParcelStudyScenarios,
  deriveParcelStudyScope,
  exportParcelStudy,
  importParcelStudy,
  parcelStudyMatchesScope,
  type ParcelStudyDraft,
  type ParcelStudyScope,
} from "../parcel-study";

const INPUT = {
  enteredBbl: "3022647515",
  billingBbl: "3022647515",
  baseLots: [{ bbl: "3022640032" }, { bbl: "3022640033" }],
};

function scope(input: unknown = INPUT): ParcelStudyScope {
  const result = deriveParcelStudyScope(input);
  if (!result.ok) throw new Error(result.message);
  return result.scope;
}

function restore(value: unknown, current = scope()) {
  return importParcelStudy(JSON.stringify(value), current);
}

describe("parcel study scope", () => {
  it("uses exactly the base lots, keeps display order and compares membership independently of ordering", () => {
    const first = scope();
    const reverse = scope({ ...INPUT, baseLots: [...INPUT.baseLots].reverse() });
    expect(first.baseBbls).toEqual(["3022640032", "3022640033"]);
    expect(reverse.baseBbls).toEqual(["3022640033", "3022640032"]);
    expect(first.key).toBe(reverse.key);
    expect(parcelStudyMatchesScope(createParcelStudy(first), reverse)).toBe(true);
  });

  it.each([
    { ...INPUT, baseLots: [] },
    { ...INPUT, baseLots: [INPUT.baseLots[0]] },
    { ...INPUT, baseLots: [...INPUT.baseLots, INPUT.baseLots[0]] },
    { ...INPUT, baseLots: [...INPUT.baseLots, { bbl: INPUT.billingBbl }] },
    { ...INPUT, enteredBbl: "3022641001", baseLots: [...INPUT.baseLots, { bbl: "3022641001" }] },
    { ...INPUT, baseLots: [...INPUT.baseLots, { bbl: "not-a-bbl" }] },
    { ...INPUT, baseLots: [...INPUT.baseLots, { bbl: "3022640000" }] },
    { ...INPUT, baseLots: [...INPUT.baseLots, { bbl: "3000000032" }] },
    { ...INPUT, baseLots: [...INPUT.baseLots, { bbl: "6022640032" }] },
    { ...INPUT, baseLots: [...INPUT.baseLots, { bbl: " 3022640032" }] },
    { ...INPUT, baseLots: [...INPUT.baseLots, null] },
    { ...INPUT, enteredBbl: null },
    { ...INPUT, billingBbl: "invalid" },
  ])("rejects ambiguous or incomplete records without silently dropping a row: %j", (input) => {
    expect(deriveParcelStudyScope(input)).toMatchObject({ ok: false, code: "invalid_records" });
  });

  it("allows an explicitly unknown billing identity and never invents it from a unit input", () => {
    const result = scope({ ...INPUT, enteredBbl: "3022641001", billingBbl: null });
    expect(result.billingBbl).toBeNull();
    expect(result.baseBbls).not.toContain("3022641001");
  });

  it("invalidates a draft when either its input identity or base membership changes", () => {
    const draft = createParcelStudy(scope());
    for (const input of [
      { ...INPUT, enteredBbl: "3022641001" },
      { ...INPUT, billingBbl: null },
      { ...INPUT, baseLots: [{ bbl: "3022640032" }, { bbl: "3022640034" }] },
    ]) {
      expect(parcelStudyMatchesScope(draft, scope(input))).toBe(false);
      expect(restore(draft, scope(input))).toMatchObject({ ok: false, code: "scope_changed" });
      expect(exportParcelStudy(draft, scope(input))).toMatchObject({ ok: false, code: "scope_changed" });
    }
  });
});

describe("proposed study arrangements", () => {
  it("compares one combined group with separate proposed groups without claiming legal membership", () => {
    const draft = createParcelStudy(scope());
    const [combined, separate] = deriveParcelStudyScenarios(draft);
    expect(combined).toEqual({ id: "combined", sites: [{
      id: "combined",
      baseBbls: ["3022640032", "3022640033"],
      buildingScheme: "undecided",
      existingBuildings: draft.existingBuildings,
    }] });
    expect(separate.id).toBe("separate");
    expect(separate.sites.map((site) => site.baseBbls)).toEqual([["3022640032"], ["3022640033"]]);
    expect(separate.sites.every((site) => site.buildingScheme === null)).toBe(true);
    expect(JSON.stringify([combined, separate])).not.toMatch(/confirmed|verified|height|floorArea|allowance/);
  });

  it("keeps retention choices independent of combined building count and arrangement", () => {
    const draft = createParcelStudy(scope());
    draft.existingBuildings[0].intent = "retain";
    draft.existingBuildings[1].intent = "demolish";
    draft.buildingScheme = "multiple";
    draft.arrangement = "together";
    const together = deriveParcelStudyScenarios(draft);
    expect(together.map((scenario) => scenario.id)).toEqual(["combined"]);
    expect(together[0].sites[0].buildingScheme).toBe("multiple");
    expect(together[0].sites[0].existingBuildings.map((entry) => entry.intent)).toEqual(["retain", "demolish"]);
    draft.arrangement = "separate";
    const separate = deriveParcelStudyScenarios(draft);
    expect(separate.map((scenario) => scenario.id)).toEqual(["separate"]);
    expect(separate[0].sites.flatMap((site) => site.existingBuildings).map((entry) => entry.intent)).toEqual(["retain", "demolish"]);
    expect(draft.buildingScheme).toBe("multiple");
  });

  it("does not let a derived scenario mutate form state", () => {
    const current = scope();
    const draft = createParcelStudy(current);
    const scenarios = deriveParcelStudyScenarios(draft);
    scenarios[0].sites[0].baseBbls.pop();
    scenarios[0].sites[0].existingBuildings[0].intent = "demolish";
    expect(draft.scope.baseBbls).toHaveLength(2);
    expect(current.baseBbls).toHaveLength(2);
    expect(draft.existingBuildings[0].intent).toBe("undecided");
  });
});

describe("versioned user-choice exchange", () => {
  it("round-trips only choices and identifiers, restoring current record order", () => {
    const draft = createParcelStudy(scope());
    draft.arrangement = "together";
    draft.buildingScheme = "multiple";
    draft.existingBuildings[0].intent = "alter";
    const download = exportParcelStudy(draft, scope());
    if (!download.ok) throw new Error(download.message);
    const reverse = scope({ ...INPUT, baseLots: [...INPUT.baseLots].reverse() });
    const upload = importParcelStudy(download.json, reverse);
    expect(upload).toEqual({ ok: true, draft: {
      ...draft,
      scope: reverse,
      existingBuildings: [...draft.existingBuildings].reverse(),
    } });
    expect(Object.keys(JSON.parse(download.json))).toEqual([
      "kind", "version", "scope", "arrangement", "buildingScheme", "existingBuildings",
    ]);
  });

  it.each([
    null, [], 0, "parcel_study",
    { version: 1 },
    { ...createParcelStudy(scope()), version: 2 },
    { ...createParcelStudy(scope()), kind: "property_report" },
    { ...createParcelStudy(scope()), arrangement: "merged" },
    { ...createParcelStudy(scope()), buildingScheme: 2 },
    { ...createParcelStudy(scope()), confirmed: true },
    { ...createParcelStudy(scope()), siteDefinition: { status: "verified" } },
    { ...createParcelStudy(scope()), floorArea: 20_000 },
    { ...createParcelStudy(scope()), provenance: { source: "city" } },
    { ...createParcelStudy(scope()), scope: { ...scope(), verified: true } },
    { ...createParcelStudy(scope()), scope: { ...scope(), key: "forged" } },
    { ...createParcelStudy(scope()), scope: { ...scope(), baseBbls: ["3022640032", "3022640032"] } },
    { ...createParcelStudy(scope()), existingBuildings: [] },
    { ...createParcelStudy(scope()), existingBuildings: [{ bbl: "3022640032", intent: "retain" }] },
    { ...createParcelStudy(scope()), existingBuildings: [{ bbl: "3022640032", intent: "retain" }, { bbl: "3022640032", intent: "demolish" }] },
    { ...createParcelStudy(scope()), existingBuildings: [{ bbl: "3022640032", intent: "retain" }, { bbl: "3022640033", intent: "keep" }] },
    { ...createParcelStudy(scope()), existingBuildings: [{ bbl: "3022640032", intent: "retain" }, { bbl: "3022640033", intent: "retain", height: 50 }] },
  ])("rejects malformed choices and injected legal/source/limit fields: %j", (value) => {
    expect(restore(value)).toMatchObject({ ok: false, code: "invalid_draft" });
  });

  it("rejects cross-property data even when an attacker copies the current scope key", () => {
    const draft = createParcelStudy(scope());
    const forged = { ...draft, scope: { ...draft.scope, enteredBbl: "3022657515" } };
    expect(restore(forged)).toMatchObject({ ok: false, code: "invalid_draft" });
  });

  it("refuses forged fields on export as well as import", () => {
    const forged = { ...createParcelStudy(scope()), verified: true } as ParcelStudyDraft;
    expect(exportParcelStudy(forged, scope())).toMatchObject({ ok: false, code: "invalid_draft" });
  });

  it("bounds untrusted input and distinguishes unreadable JSON", () => {
    expect(importParcelStudy("[", scope())).toMatchObject({ ok: false, code: "invalid_json" });
    expect(importParcelStudy(" ".repeat(MAX_PARCEL_STUDY_JSON_LENGTH + 1), scope())).toMatchObject({ ok: false, code: "too_large" });
  });
});
