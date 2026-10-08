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
 * The committed journey fixture is a real contract-1.3.0 document, so a check that accepts it
 * and rejects deliberate breakages is never vacuous.
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
  it("accepts the committed journey document (real contract-1.3.0, never vacuous)", () => {
    const result = validateResultsDocument(loadResultsFixture(JOURNEY));
    expect(result.ok).toBe(true);
  });

  it("refuses a document whose contract version is not the three-way 1.3.0 layer", () => {
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
    // The journey floor-area answer withholds `legal_unit_limit_standard`. Add it as a SHOWN
    // value with a number: the server erred, and the website must refuse the whole document so a
    // number is never shown for a withheld result (R556, R570).
    const body = probe(doc => {
      const allowance = doc.answers.floor_area_allowance;
      if (allowance.status !== "available" || !allowance.value_states) {
        throw new Error("fixture changed: allowance must carry value_states");
      }
      expect(allowance.value_states.legal_unit_limit_standard?.way).toBe("withheld");
      allowance.values.push({
        key: "legal_unit_limit_standard",
        label: "Legal dwelling-unit limit, standard residences",
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
        result.problems.some(p => p.includes("legal_unit_limit_standard") && p.includes("withheld")),
      ).toBe(true);
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
