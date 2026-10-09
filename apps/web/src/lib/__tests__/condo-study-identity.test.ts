import { describe, expect, it } from "vitest";
import { fetchCondoRecords, type CondoRecordsView } from "../condo-records";
import { deriveParcelStudyScope } from "../architect/parcel-study";

const GOOD_ROWS = [{ bbl: "3022640032" }, { bbl: "3022640033" }];
const DOCUMENT = {
  document_kind: "condo_records",
  outcome: "multi_lot_set",
  entered_bbl: "3022647515",
  billing_bbl: "3022647515",
  base_lots: GOOD_ROWS,
};

async function view(overrides: Record<string, unknown> = {}): Promise<CondoRecordsView> {
  const body = { ...DOCUMENT, ...overrides };
  const result = await fetchCondoRecords("3022647515", {
    fetchImpl: (async () => ({
      status: 200,
      headers: { get: () => null },
      json: async () => body,
    })) as unknown as typeof fetch,
  });
  if (result.kind !== "document") throw new Error(`Expected document, received ${result.kind}`);
  return result.view;
}

describe("condo parcel-study raw identity integrity", () => {
  it("admits exact canonical identities without making a legal confirmation", async () => {
    const records = await view();
    expect(records.studyIdentityIntegrity).toBe(true);
    expect(deriveParcelStudyScope(records).ok).toBe(true);
    expect(records.siteDefinition).toBeNull();
  });

  it.each([null, undefined])("permits unknown billing identity (%j) without filling it from the entered lot", async (billing_bbl) => {
    const records = await view({ billing_bbl, entered_bbl: "3022641001" });
    expect(records.studyIdentityIntegrity).toBe(true);
    expect(records.billingBbl).toBeNull();
    expect(records.enteredBbl).toBe("3022641001");
  });

  it.each([
    null,
    undefined,
    [],
    "3022640034",
    {},
    { bbl: null },
    { bbl: 3022640034 },
    { bbl: "30226400\u000034" },
    { bbl: " 3022640034" },
    { bbl: "3022640034 " },
    { bbl: "3022640034more" },
    { bbl: "6022640034" },
    { bbl: "3000000034" },
    { bbl: "3022640000" },
  ])("refuses the entire study set when an original row is invalid: %j", async (badRow) => {
    const records = await view({ base_lots: [...GOOD_ROWS, badRow] });
    expect(records.studyIdentityIntegrity).toBe(false);
    // The records display still retains the two good identities. Its sanitized
    // output alone must never become the planner's complete source membership.
    expect(records.baseLots.slice(0, 2).map((lot) => lot.bbl)).toEqual(["3022640032", "3022640033"]);
  });

  it.each([null, undefined, {}, "3022640032"])("refuses a missing or non-array source membership: %j", async (base_lots) => {
    expect((await view({ base_lots })).studyIdentityIntegrity).toBe(false);
  });

  it.each([null, undefined, "", " 3022647515", "30226475\u000015", 3022647515])("requires the raw entered identity, without trimming or fallback: %j", async (entered_bbl) => {
    const records = await view({ entered_bbl, bbl: "3022647515" });
    expect(records.studyIdentityIntegrity).toBe(false);
  });

  it.each(["", "30226475\u000015", " 3022647515", 3022647515, {}, "6022647515"])("refuses a present invalid billing identity: %j", async (billing_bbl) => {
    expect((await view({ billing_bbl })).studyIdentityIntegrity).toBe(false);
  });

  it("never trusts an API-supplied integrity flag", async () => {
    const records = await view({ base_lots: [...GOOD_ROWS, null], studyIdentityIntegrity: true });
    expect(records.studyIdentityIntegrity).toBe(false);
  });

  it("leaves valid-shaped duplicates and umbrella overlap for the domain gate to refuse", async () => {
    for (const extra of [{ bbl: "3022640032" }, { bbl: "3022647515" }]) {
      const records = await view({ base_lots: [...GOOD_ROWS, extra] });
      expect(records.studyIdentityIntegrity).toBe(true);
      expect(deriveParcelStudyScope(records)).toMatchObject({ ok: false, code: "invalid_records" });
    }
  });
});
