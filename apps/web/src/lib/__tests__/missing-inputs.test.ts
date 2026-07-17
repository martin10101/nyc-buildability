import { describe, expect, it } from "vitest";
import { groupMissingInputs } from "@/lib/missing-inputs";
import { baseProfile } from "@/test-support/fixtures";
import type { MissingInput } from "@/lib/property-profile";

/**
 * S6 / M1-T005 G3 D3: the documented missing-inputs display policy.
 * Invariant: surfaced + grouped == total (NOTHING is silently dropped).
 */
describe("groupMissingInputs", () => {
  it("never drops an entry: surfaced + grouped always equals total", () => {
    const entries = baseProfile().missing_inputs;
    const grouped = groupMissingInputs(entries);
    expect(grouped.total).toBe(entries.length);
    expect(grouped.surfaced.length + grouped.grouped.length).toBe(entries.length);
    const fields = new Set([
      ...grouped.surfaced.map((e) => e.field),
      ...grouped.grouped.map((e) => e.field),
    ]);
    for (const entry of entries) {
      expect(fields.has(entry.field)).toBe(true);
    }
  });

  it("surfaces feasibility-relevant fields from the real builder fixture", () => {
    const grouped = groupMissingInputs(baseProfile().missing_inputs);
    const surfacedFields = grouped.surfaced.map((e) => e.field);
    // Zoning/feasibility columns must be immediately visible.
    for (const field of ["overlay1", "overlay2", "spdist2", "zonedist3", "ltdheight", "mih_opt1"]) {
      expect(surfacedFields).toContain(field);
    }
    // Administrative date-stamp columns go behind the count toggle.
    const groupedFields = grouped.grouped.map((e) => e.field);
    for (const field of ["basempdate", "dcasdate", "polidate", "rpaddate"]) {
      expect(groupedFields).toContain(field);
    }
  });

  it("always surfaces critical entries even when not feasibility-listed", () => {
    const entries: MissingInput[] = [
      { field: "some_admin_column", criticality: "critical", reason: "r" },
      { field: "another_admin_column", criticality: "noncritical", reason: "r" },
    ];
    const grouped = groupMissingInputs(entries);
    expect(grouped.surfaced.map((e) => e.field)).toEqual(["some_admin_column"]);
    expect(grouped.grouped.map((e) => e.field)).toEqual(["another_admin_column"]);
  });

  it("handles the empty list", () => {
    expect(groupMissingInputs([])).toEqual({ surfaced: [], grouped: [], total: 0 });
  });
});
