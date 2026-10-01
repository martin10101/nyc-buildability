import { describe, expect, it } from "vitest";
import {
  NOT_CONFIRMED,
  TAX_LOT_ONLY_ESTIMATE,
  TAX_LOT_ONLY_WARNING,
  ZONING_LOT_ROWS,
  taxLotScopeWarning,
  verifiedZoningLotNumbers,
  type VerifiedZoningLot,
} from "../tax-lot-scope";

// Owner directive 2026-10-01, copied word for word so any drift in the app's wording fails here.
const GENERIC = "These numbers cover only the tax lot you entered. The full zoning lot may include other lots. The whole-site limit, the room left after existing buildings, and the combined lot's rear yard and coverage are not calculated yet.";
const VERIFIED_1_70 = "This zoning lot includes tax lots 1 and 70. These numbers use lot 70 only. The whole-site limit, the room left after existing buildings, and the combined lot's rear yard and coverage are not calculated yet.";

// Test fixture only: the shape of a verified zoning-lot fact for the 215-16 Northern benchmark
// (block 07334, tax lots 1 and 70). No such verified fact is served to the web yet.
const LOT_70 = "4073340070";
const VERIFIED: VerifiedZoningLot = { taxLotBbls: ["4073340001", LOT_70], calculatedBbl: LOT_70 };

describe("tax-lot-only wording (owner directive 2026-10-01)", () => {
  it("keeps the exact labels and the generic warning", () => {
    expect(TAX_LOT_ONLY_ESTIMATE).toBe("Tax-lot-only estimate");
    expect(NOT_CONFIRMED).toBe("Not confirmed");
    expect(TAX_LOT_ONLY_WARNING).toBe(GENERIC);
    expect(ZONING_LOT_ROWS.map(([, label]) => label)).toEqual([
      "Whole-site capacity",
      "Remaining development capacity",
      "Combined zoning lot: coverage",
      "Combined zoning lot: rear yard",
    ]);
    // Plain words: no internal codes in any shown text.
    for (const text of [GENERIC, VERIFIED_1_70, ...ZONING_LOT_ROWS.map(([, label]) => label)]) {
      expect(text).not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
    }
  });

  it("reads the generic warning when no verified zoning lot is supplied", () => {
    expect(taxLotScopeWarning(LOT_70)).toBe(GENERIC);
    expect(taxLotScopeWarning(LOT_70, null)).toBe(GENERIC);
    expect(taxLotScopeWarning("")).toBe(GENERIC);
  });

  it("names lots 1 and 70 and says the numbers use lot 70 only for the verified variant", () => {
    expect(taxLotScopeWarning(LOT_70, VERIFIED)).toBe(VERIFIED_1_70);
    expect(verifiedZoningLotNumbers(VERIFIED, LOT_70)).toEqual({ lots: [1, 70], calculated: 70 });
    // Listed in any order, the lots read in lot-number order.
    expect(taxLotScopeWarning(LOT_70, { ...VERIFIED, taxLotBbls: [LOT_70, "4073340001"] })).toBe(VERIFIED_1_70);
  });

  it("lists three or more lots in plain English", () => {
    const three: VerifiedZoningLot = { taxLotBbls: ["4073340070", "4073340001", "4073340005"], calculatedBbl: "4073340005" };
    expect(taxLotScopeWarning("4073340005", three)).toMatch(/^This zoning lot includes tax lots 1, 5, and 70\. These numbers use lot 5 only\. /);
  });

  it.each([
    ["the fact belongs to another property", { ...VERIFIED, calculatedBbl: "4073340001" }],
    ["the calculated lot is not on the zoning lot", { taxLotBbls: ["4073340001", "4073340002"], calculatedBbl: LOT_70 }],
    ["only one tax lot is listed", { taxLotBbls: [LOT_70], calculatedBbl: LOT_70 }],
    ["a lot is on another block", { taxLotBbls: ["4073350001", LOT_70], calculatedBbl: LOT_70 }],
    ["a lot is listed twice", { taxLotBbls: [LOT_70, LOT_70], calculatedBbl: LOT_70 }],
    ["a lot is not a canonical BBL", { taxLotBbls: ["1", LOT_70], calculatedBbl: LOT_70 }],
    ["a lot number is zero", { taxLotBbls: ["4073340000", LOT_70], calculatedBbl: LOT_70 }],
    ["the list is malformed", { taxLotBbls: "4073340001,4073340070", calculatedBbl: LOT_70 } as unknown as VerifiedZoningLot],
  ])("falls back to the generic warning when %s", (_case, zoningLot) => {
    expect(verifiedZoningLotNumbers(zoningLot, LOT_70)).toBeNull();
    expect(taxLotScopeWarning(LOT_70, zoningLot)).toBe(GENERIC);
  });
});
