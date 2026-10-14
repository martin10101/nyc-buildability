import { describe, expect, it } from "vitest";
import {
  RESULTS_CONTRACT_VERSION,
  validateResultsDocument,
} from "@/lib/results-contract-checks";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import type { Results } from "@/lib/architect/three-answers";

/**
 * [WIRING] The website's own check of a returned results document (task M5-T140, ruling R9).
 * It verifies the SHAPE the reader consumes and REFUSES a document in which a key is withheld
 * in value_states and also present among the answer's shown values (scenario S21; R556, R570).
 * The committed journey fixture is now the regenerated real contract-1.4.0 document (M5-T146 part E),
 * so a check that accepts it and rejects deliberate breakages is never vacuous.
 */

const JOURNEY = "recorded_215_16_northern_journey";

/** A deliberate wrong-shape probe, written `as unknown as Results` (CODING_RULES), never a
 * direct cast — these bodies exist only to be refused. */
function probe(overrides: (doc: Results) => void): unknown {
  const doc = loadResultsFixture(JOURNEY);
  overrides(doc);
  return doc as unknown as Results;
}

describe("validateResultsDocument — shape of the blocks the panel reads [WIRING]", () => {
  it("accepts the committed journey document (regenerated contract-1.4.0, never vacuous)", () => {
    const doc = loadResultsFixture(JOURNEY);
    expect(doc.contract_version).toBe("1.4.0");
    const result = validateResultsDocument(doc);
    expect(result.ok).toBe(true);
  });

  it("refuses a document whose contract version is below the three-way 1.3.0 layer", () => {
    const body = probe(doc => {
      (doc as { contract_version: string }).contract_version = "1.2.0";
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    expect(RESULTS_CONTRACT_VERSION).toBe("1.3.0");
    if (!result.ok) expect(result.problems.some(p => p.startsWith("contract_version"))).toBe(true);
  });

  it("refuses a body that is not an object", () => {
    expect(validateResultsDocument(null).ok).toBe(false);
    expect(validateResultsDocument("nope").ok).toBe(false);
    expect(validateResultsDocument([]).ok).toBe(false);
  });

  it("refuses a withheld value_states entry missing its gap_kind (the panel reads the kind)", () => {
    const body = probe(doc => {
      const envelope = doc.answers.permitted_envelope;
      if (envelope.status !== "available" || !envelope.value_states) {
        throw new Error("fixture changed: envelope must carry value_states");
      }
      delete (envelope.value_states.max_lot_coverage as { gap_kind?: unknown }).gap_kind;
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some(p => p.includes("gap_kind"))).toBe(true);
    }
  });

  it("S21: refuses a document in which a key is withheld AND present among the shown values", () => {
    // The journey floor-area answer withholds `legal_unit_limit_qualifying_affordable` (M5-T157:
    // the standard legal unit limit is now a shown conditional ceiling, so this proof uses the
    // qualifying-affordable limit, still withheld). Add it as a SHOWN value with a number: the
    // server erred, and the website must refuse the whole document so a number is never shown for a
    // withheld result (R556, R570).
    const body = probe(doc => {
      const allowance = doc.answers.floor_area_allowance;
      if (allowance.status !== "available" || !allowance.value_states) {
        throw new Error("fixture changed: allowance must carry value_states");
      }
      expect(allowance.value_states.legal_unit_limit_qualifying_affordable?.way).toBe("withheld");
      allowance.values.push({
        key: "legal_unit_limit_qualifying_affordable",
        label: "Legal dwelling-unit limit, qualifying affordable housing",
        value: 29,
        unit: "dwelling_units",
        zr_sections: ["ZR 23-52"],
        sources: [],
        exception_label: null,
      });
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(
        result.problems.some(
          p => p.includes("legal_unit_limit_qualifying_affordable") && p.includes("withheld"),
        ),
      ).toBe(true);
    }
  });

  it("B1: refuses an available answer that shows values but carries no value_states map", () => {
    const body = probe(doc => {
      const allowance = doc.answers.floor_area_allowance;
      if (allowance.status !== "available") throw new Error("fixture changed");
      delete (allowance as { value_states?: unknown }).value_states;
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.includes("value_states"))).toBe(true);
  });

  it("B2: refuses a shown value that has no value_states entry (never settled by silence)", () => {
    const body = probe(doc => {
      const allowance = doc.answers.floor_area_allowance;
      if (allowance.status !== "available" || !allowance.value_states) throw new Error("fixture changed");
      // max_residential_far is a SHOWN value; drop its state entry.
      expect(allowance.values.some(v => v.key === "max_residential_far")).toBe(true);
      delete (allowance.value_states as Record<string, unknown>).max_residential_far;
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.includes("max_residential_far"))).toBe(true);
  });

  it("B3: refuses a conditional value whose list of conditions is empty", () => {
    const body = probe(doc => {
      const allowance = doc.answers.floor_area_allowance;
      if (allowance.status !== "available" || !allowance.value_states) throw new Error("fixture changed");
      const state = allowance.value_states.max_residential_far;
      if (!state || state.way !== "conditional") throw new Error("fixture changed");
      (state as unknown as { conditions: unknown[] }).conditions = [];
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some(p => p.includes("at least one condition"))).toBe(true);
    }
  });

  it("refuses an answer with a non-numeric value", () => {
    const body = probe(doc => {
      const allowance = doc.answers.floor_area_allowance;
      if (allowance.status !== "available") throw new Error("fixture changed");
      (allowance.values[0] as { value: unknown }).value = "a lot";
    });
    const result = validateResultsDocument(body);
    expect(result.ok).toBe(false);
  });

  it("refuses a status strip item with no text", () => {
    const body = probe(doc => {
      (doc.status_strip[0] as { text: unknown }).text = "";
    });
    expect(validateResultsDocument(body).ok).toBe(false);
  });
});

/**
 * [WIRING] Contract 1.5.0 (task M5-T164): the additive illustrative placement and area allocation,
 * and the cross-key way rules the schema cannot express (fitted only when placed; apartment + other
 * = total within rounding), mirrored from services/api/app/contracts/results_way_rules.py. The
 * value-state way rule of 1.3.0 keeps running on a 1.5.0 document, and an unknown version is still
 * refused.
 */
const REAR_YARD_1_5_0 = "synthetic_rear_yard_constraints_contract_1_5_0";
const PLACED_1_5_0 = "synthetic_placed_building_contract_1_5_0";

/** One worked alternative, loosely typed for the deliberate 1.5.0 mutations below. */
interface MutableAlt {
  building: string;
  placement?: { status: string; label: string; outline?: unknown };
  area_allocation?: {
    label: string;
    share: number;
    fitted: boolean;
    apartment_area_sqft: number;
    other_area_sqft: number;
    total_sqft: number;
  };
}

function altOf(doc: Results): MutableAlt {
  return (doc as unknown as { building_alternatives: MutableAlt[] }).building_alternatives[0];
}

describe("validateResultsDocument — contract 1.5.0 placement and area allocation [WIRING]", () => {
  it("accepts the rear-yard-constraints 1.5.0 fixture (withheld placement, unfitted allocation)", () => {
    const doc = loadResultsFixture(REAR_YARD_1_5_0);
    expect(doc.contract_version).toBe("1.5.0");
    expect(validateResultsDocument(doc).ok).toBe(true);
  });

  it("accepts the placed-building 1.5.0 fixture (placed placement, fitted allocation)", () => {
    const doc = loadResultsFixture(PLACED_1_5_0);
    expect(doc.contract_version).toBe("1.5.0");
    expect(validateResultsDocument(doc).ok).toBe(true);
  });

  it("S11: accepts 1.5.0 but still refuses an unknown contract version", () => {
    const doc = loadResultsFixture(PLACED_1_5_0);
    (doc as unknown as { contract_version: string }).contract_version = "9.9.9";
    const result = validateResultsDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.startsWith("contract_version"))).toBe(true);
  });

  it("S12: refuses an area_allocation that is fitted while the placement is withheld", () => {
    const doc = loadResultsFixture(PLACED_1_5_0);
    const alt = altOf(doc);
    if (!alt.placement || !alt.area_allocation) throw new Error("fixture changed");
    alt.placement.status = "withheld";
    delete alt.placement.outline; // a valid withheld placement; the allocation stays fitted
    const result = validateResultsDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.includes("fitted"))).toBe(true);
  });

  it("S12: refuses an area_allocation whose apartment + other does not equal total", () => {
    const doc = loadResultsFixture(PLACED_1_5_0);
    const alt = altOf(doc);
    if (!alt.area_allocation) throw new Error("fixture changed");
    alt.area_allocation.total_sqft = alt.area_allocation.total_sqft + 1000;
    const result = validateResultsDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.includes("apartment + other"))).toBe(true);
  });

  it("S4: refuses a placement label other than 'Illustrative'", () => {
    const doc = loadResultsFixture(PLACED_1_5_0);
    const alt = altOf(doc);
    if (!alt.placement) throw new Error("fixture changed");
    alt.placement.label = "Illustration";
    const result = validateResultsDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.includes("placement.label"))).toBe(true);
  });

  it("S3: refuses a withheld placement that carries an outline", () => {
    const doc = loadResultsFixture(REAR_YARD_1_5_0);
    const alt = altOf(doc);
    if (!alt.placement) throw new Error("fixture changed");
    alt.placement.outline = [[[0, 0], [1, 0], [1, 1], [0, 0]]];
    const result = validateResultsDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.includes("outline"))).toBe(true);
  });

  it("keeps the 1.3.0 value-state way rule running on a 1.5.0 document", () => {
    const doc = loadResultsFixture(PLACED_1_5_0);
    const allowance = doc.answers.floor_area_allowance;
    if (allowance.status !== "available" || !allowance.value_states) {
      throw new Error("fixture changed: allowance must carry value_states");
    }
    const shownKey = allowance.values[0].key;
    delete (allowance.value_states as Record<string, unknown>)[shownKey];
    const result = validateResultsDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some(p => p.includes(shownKey))).toBe(true);
  });
});
