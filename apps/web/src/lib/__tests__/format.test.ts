import { describe, expect, it } from "vitest";
import { FIELD_LABELS, fieldLabel, formatValue } from "@/lib/format";
import { FEASIBILITY_RELEVANT_FIELDS } from "@/lib/missing-inputs";
import { baseProfile } from "@/test-support/fixtures";

/**
 * D1 (M2-T001 G3): every surfaced raw PLUTO key must have a reviewed human
 * label — no raw column name reaches the user (scenario S5). The mapping
 * is asserted against (a) the exact ~20 keys the G3 review named, (b) every
 * fact/missing-input key in the committed real-builder fixture, and (c)
 * the full documented display policy list.
 */

/** The keys the M2-T001 G3 review (defect D1) listed as missing, VERBATIM. */
const D1_KEYS = [
  "residfar",
  "commfar",
  "facilfar",
  "affresfar",
  "mnffar",
  "zonedist1",
  "zonedist2",
  "zonedist3",
  "zonedist4",
  "overlay1",
  "overlay2",
  "spdist1",
  "spdist2",
  "spdist3",
  "ltdheight",
  "mih_opt1",
  "mih_opt2",
  "mih_opt3",
  "mih_opt4",
  "edesignum",
  "appbbl",
  "appdate",
  "condono",
];

/** Grouped administrative keys visible in the G3 D1 screenshot. */
const D1_ADMIN_KEYS = [
  "basempdate",
  "dcasdate",
  "edesigdate",
  "landmkdate",
  "masdate",
  "polidate",
  "rpaddate",
  "zoningdate",
];

describe("FIELD_LABELS coverage (D1/S5)", () => {
  it("labels every key the G3 review named in defect D1", () => {
    for (const key of [...D1_KEYS, ...D1_ADMIN_KEYS]) {
      expect(FIELD_LABELS[key], `label for ${key}`).toBeTruthy();
      expect(FIELD_LABELS[key]).not.toBe(key);
    }
  });

  it("labels every fact key and missing-input field in the real-builder fixture", () => {
    const profile = baseProfile();
    const keys = [
      ...Object.keys(profile.lot_facts),
      ...Object.keys(profile.existing_building_facts),
      ...profile.missing_inputs.map((entry) => entry.field),
    ];
    for (const key of keys) {
      expect(FIELD_LABELS[key], `label for ${key}`).toBeTruthy();
    }
  });

  it("labels every field in the documented feasibility display policy", () => {
    for (const key of FEASIBILITY_RELEVANT_FIELDS) {
      expect(FIELD_LABELS[key], `label for ${key}`).toBeTruthy();
    }
  });

  it("covers the full 108-column PLUTO inventory", () => {
    expect(Object.keys(FIELD_LABELS).length).toBeGreaterThanOrEqual(108);
  });

  it("falls back HONESTLY for an unreviewed future column (explicit marker, never silently raw)", () => {
    expect(fieldLabel("brand_new_column")).toBe(
      "brand_new_column (source column — label pending review)",
    );
  });
});

describe("formatValue (unchanged M2-T001 behavior)", () => {
  it("renders numbers with digit grouping and full precision", () => {
    expect(formatValue(7577714)).toBe("7,577,714");
    expect(formatValue(0)).toBe("0");
  });

  it("renders null/undefined as an explicit dash", () => {
    expect(formatValue(null)).toBe("—");
    expect(formatValue(undefined)).toBe("—");
  });

  it("renders booleans as Yes/No", () => {
    expect(formatValue(true)).toBe("Yes");
    expect(formatValue(false)).toBe("No");
  });
});
