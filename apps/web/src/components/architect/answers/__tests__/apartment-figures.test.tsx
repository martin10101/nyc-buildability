import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  CEILING_ESTIMATE_DISTINCTION,
  CEILING_NOT_AVAILABLE,
  DRAFT_GATED_LINE,
  ESTIMATE_NOT_AVAILABLE,
  LOT_AREA_BASIS_FALLBACK,
  apartmentEstimateRange,
  legalCeiling,
  lotAreaBasisLine,
  type ValueState,
} from "@/lib/architect/apartment-figures";
import type { Results } from "@/lib/architect/three-answers";
import { loadResultsFixture, loadResultsFixtures } from "@/test-support/results-fixtures";
import { ApartmentFigures } from "../ApartmentFigures";

/**
 * M5-T171 — the page-1 parity block: the legal ceiling beside the apartment estimate, the identical
 * distinction line, the R055 lot-area line and the zoning-lot concern. Every expected value is read
 * from the loaded document (or the presentation-token file) — no figure is copied into the component
 * or this suite. Each input state has exactly one test; the state / outcome / test table is in the
 * producer report.
 */

afterEach(cleanup);

const BENCHMARK = "recorded_215_16_northern_journey";
const ALL_AVAILABLE = "synthetic_all_answers_available"; // a 1.0.0 document: no ceiling, no estimate
const NO_LOT_AREA = "synthetic_building_alternatives_contract_1_4_0"; // estimate present, no FAR / lot
const ZONING_LOT_MARKER = "register of recorded documents";

/** The presentation tokens, read from disk (repo root, two levels above the vitest cwd apps/web). */
function presentationTokens(): { wording: Record<string, string> } {
  return JSON.parse(
    readFileSync(resolve(process.cwd(), "../../docs/design/presentation-tokens.json"), "utf8"),
  );
}

function clone(doc: Results): Results {
  return JSON.parse(JSON.stringify(doc)) as Results;
}

/** The floor-area allowance's value-states map (the benchmark keeps the ceiling here). */
function allowanceStates(doc: Results): Record<string, ValueState> {
  const fa = doc.answers.floor_area_allowance;
  if (fa.status !== "available" || !fa.value_states) throw new Error("fixture changed");
  return fa.value_states as Record<string, ValueState>;
}

// ---- S1: the distinction line equals the token, character for character ----

describe("S1 — the distinction line is byte-identical to the presentation token", () => {
  it("the literal equals wording.ceiling_estimate_distinction read from disk", () => {
    const tokens = presentationTokens();
    expect(CEILING_ESTIMATE_DISTINCTION).toBe(tokens.wording.ceiling_estimate_distinction);
  });

  it("the rendered distinction line is exactly that token", () => {
    const tokens = presentationTokens();
    render(<ApartmentFigures results={loadResultsFixture(BENCHMARK)} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-distinction").textContent).toBe(
      tokens.wording.ceiling_estimate_distinction,
    );
  });
});

// ---- S6: the lot-area line is composed exactly as report page 1 ----

describe("S6 — the R055 lot-area line, byte-equal to report page 1", () => {
  it("reads '10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone' (× is U+00D7)", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const expected = "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone";
    expect(lotAreaBasisLine(doc)).toBe(expected);
    render(<ApartmentFigures results={doc} showDraftValues />);
    const line = screen.getByTestId("apartment-figures-lot-area").textContent ?? "";
    expect(line).toBe(expected);
    expect(line).toContain("×"); // the multiplication sign, never the letter x
    expect(line).not.toContain(" x ");
  });
});

// ---- S4: the 29 is Conditional, never settled; a withheld limit shows its reason ----

describe("S4 — the ceiling's state", () => {
  it("state A: a shown conditional ceiling reads 'Legal ceiling 29' with the chip 'Conditional'", () => {
    render(<ApartmentFigures results={loadResultsFixture(BENCHMARK)} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-ceiling-value").textContent).toBe("Legal ceiling 29");
    expect(screen.getByTestId("apartment-figures-ceiling-chip").textContent).toBe("Conditional");
  });

  it("state J: a shown settled ceiling reads the chip 'Provisional', never 'Conditional'", () => {
    const doc = clone(loadResultsFixture(BENCHMARK));
    allowanceStates(doc).legal_unit_limit_standard = { way: "settled" };
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-ceiling-value").textContent).toBe("Legal ceiling 29");
    expect(screen.getByTestId("apartment-figures-ceiling-chip").textContent).toBe("Provisional");
  });

  it("state B: a withheld ceiling (work owed) shows the document's reason and 'Pending verification', no number", () => {
    const doc = clone(loadResultsFixture(BENCHMARK));
    const fa = doc.answers.floor_area_allowance;
    if (fa.status !== "available") throw new Error("fixture changed");
    fa.values = fa.values.filter(value => value.key !== "legal_unit_limit_standard");
    const reason = "The dwelling-unit factor for this program is not built yet.";
    allowanceStates(doc).legal_unit_limit_standard = {
      way: "withheld",
      label: "Legal dwelling-unit limit, standard residences",
      reason,
      gap_kind: "work_owed",
      resolved_by: "Building the rule and checking it against a worked example",
    };
    expect(legalCeiling(doc)).toEqual({ kind: "withheld", reason, label: "Pending verification" });
    render(<ApartmentFigures results={doc} showDraftValues />);
    const value = screen.getByTestId("apartment-figures-ceiling-value").textContent ?? "";
    expect(value).toBe(`Legal ceiling: ${reason}`);
    expect(value).not.toMatch(/\d/);
    expect(screen.getByTestId("apartment-figures-ceiling-chip").textContent).toBe("Pending verification");
  });

  it("state B2: a withheld ceiling whose gap is a missing fact reads 'Unresolved'", () => {
    const doc = clone(loadResultsFixture(BENCHMARK));
    const fa = doc.answers.floor_area_allowance;
    if (fa.status !== "available") throw new Error("fixture changed");
    fa.values = fa.values.filter(value => value.key !== "legal_unit_limit_standard");
    allowanceStates(doc).legal_unit_limit_standard = {
      way: "withheld",
      label: "Legal dwelling-unit limit, standard residences",
      reason: "The recorded lot area is not confirmed.",
      gap_kind: "missing_information",
      resolved_by: "A survey or deed confirming the lot area",
    };
    expect(legalCeiling(doc).kind).toBe("withheld");
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-ceiling-chip").textContent).toBe("Unresolved");
  });

  it("state C: a document with no legal ceiling shows 'Legal ceiling not available', no chip", () => {
    const doc = loadResultsFixture(ALL_AVAILABLE);
    expect(legalCeiling(doc)).toEqual({ kind: "none" });
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-ceiling-value").textContent).toBe(CEILING_NOT_AVAILABLE);
    expect(screen.queryByTestId("apartment-figures-ceiling-chip")).toBeNull();
  });
});

// ---- The estimate's state ----

describe("the apartment estimate's state", () => {
  it("state D: a ranged estimate reads 'Estimate 17-22' with the chip 'Provisional'", () => {
    const doc = loadResultsFixture(BENCHMARK);
    expect(apartmentEstimateRange(doc)).toBe("17-22");
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-estimate-value").textContent).toBe("Estimate 17-22");
    expect(screen.getByTestId("apartment-figures-estimate-chip").textContent).toBe("Provisional");
  });

  it("state E: a 'Not known' capacity estimate shows 'Apartment estimate not available', no figure", () => {
    const doc = clone(loadResultsFixture(BENCHMARK));
    const alternatives = doc.building_alternatives;
    if (!alternatives || alternatives.length === 0) throw new Error("fixture changed");
    alternatives[0].capacity_estimate = { label: "Not known", reason: "The floor area is withheld." };
    expect(apartmentEstimateRange(doc)).toBeNull();
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-estimate-value").textContent).toBe(ESTIMATE_NOT_AVAILABLE);
    expect(screen.queryByTestId("apartment-figures-estimate-chip")).toBeNull();
  });

  it("state F: a document with no building alternatives shows 'Apartment estimate not available'", () => {
    const doc = clone(loadResultsFixture(BENCHMARK));
    doc.building_alternatives = [];
    expect(apartmentEstimateRange(doc)).toBeNull();
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-estimate-value").textContent).toBe(ESTIMATE_NOT_AVAILABLE);
  });
});

// ---- The zoning-lot concern and the lot-area fallback ----

describe("the zoning-lot concern and the lot-area fallback", () => {
  it("state G: while the lot is unconfirmed the concern is the document's own sentence and the line ends 'alone'", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ApartmentFigures results={doc} showDraftValues />);
    const concern = screen.getByTestId("apartment-figures-zoning-lot").textContent ?? "";
    expect(concern).toContain(ZONING_LOT_MARKER); // read from the document, not invented
    expect(screen.getByTestId("apartment-figures-lot-area").textContent).toContain("tax lot 70 alone");
  });

  it("state H: with no recorded-document index condition there is no concern and no 'alone'", () => {
    const doc = clone(loadResultsFixture(BENCHMARK));
    // Drop the ACRIS zoning-lot condition from every shown figure and building way; keep the rest.
    const strip = (states: Record<string, ValueState> | null | undefined): void => {
      for (const state of Object.values(states ?? {})) {
        if (state.way === "conditional") {
          state.conditions = state.conditions.filter(
            condition => !condition.assumption.includes(ZONING_LOT_MARKER),
          );
        }
      }
    };
    for (const key of ["floor_area_allowance", "permitted_envelope", "building_option"] as const) {
      const answer = doc.answers[key];
      if (answer.status === "available") strip(answer.value_states as Record<string, ValueState>);
    }
    for (const alternative of doc.building_alternatives ?? []) {
      if (alternative.way.way === "conditional") {
        alternative.way.conditions = alternative.way.conditions.filter(
          condition => !condition.assumption.includes(ZONING_LOT_MARKER),
        );
      }
    }
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.queryByTestId("apartment-figures-zoning-lot")).toBeNull();
    const line = screen.getByTestId("apartment-figures-lot-area").textContent ?? "";
    expect(line).toContain("tax lot 70");
    expect(line).not.toContain("alone");
  });

  it("state I: with no recorded area / FAR / tax lot the line is the report's generic basis line", () => {
    const doc = loadResultsFixture(NO_LOT_AREA);
    expect(lotAreaBasisLine(doc)).toBe(LOT_AREA_BASIS_FALLBACK);
    render(<ApartmentFigures results={doc} showDraftValues />);
    expect(screen.getByTestId("apartment-figures-lot-area").textContent).toBe(LOT_AREA_BASIS_FALLBACK);
  });
});

// ---- The draft gate (D-090-R010) ----

describe("the draft gate", () => {
  it("a draft document on an architect surface (the flag off) shows only the not-reviewed line", () => {
    render(<ApartmentFigures results={loadResultsFixture(BENCHMARK)} />);
    expect(screen.getByTestId("apartment-figures-draft-gated").textContent).toBe(DRAFT_GATED_LINE);
    expect(screen.queryByTestId("apartment-figures-ceiling-value")).toBeNull();
    expect(screen.queryByTestId("apartment-figures-estimate-value")).toBeNull();
    expect(screen.queryByTestId("apartment-figures-distinction")).toBeNull();
    expect(screen.queryByTestId("apartment-figures-lot-area")).toBeNull();
  });
});

// ---- S2: no forbidden word anywhere in the block, on every committed fixture ----

describe("S2 — the block never overstates a result", () => {
  const FORBIDDEN = [
    "buildable",
    "achievable",
    "can be built",
    "feasible",
    "compliant",
    "optimal",
    "preferred",
    "verified",
    "achieved",
    "recommended",
  ];
  for (const { name, doc } of loadResultsFixtures()) {
    it(`${name}: holds none of the forbidden words`, () => {
      render(<ApartmentFigures results={doc} showDraftValues />);
      const text = (screen.getByTestId("apartment-figures").textContent ?? "").toLowerCase();
      for (const word of FORBIDDEN) expect(text).not.toContain(word);
    });
  }
});

// ---- S7: every committed fixture renders the block; it reads figures or degrades, never throws ----

describe("S7 — every committed valid results document renders the block", () => {
  const FIXTURES = loadResultsFixtures();

  it("loads the committed fixtures (never a vacuous run), including the 1.5.0 examples", () => {
    const names = FIXTURES.map(fixture => fixture.name);
    expect(names.length).toBeGreaterThanOrEqual(4);
    expect(names).toContain(BENCHMARK);
    expect(names.some(name => name.includes("1_5_0"))).toBe(true);
  });

  for (const { name, doc } of FIXTURES) {
    it(`${name}: reads the ceiling and the estimate from the document, degrading to no figure`, () => {
      render(<ApartmentFigures results={doc} showDraftValues />);
      expect(screen.getByTestId("apartment-figures")).toBeInTheDocument();
      const ceiling = legalCeiling(doc);
      const ceilingValue = screen.getByTestId("apartment-figures-ceiling-value").textContent;
      if (ceiling.kind === "value") expect(ceilingValue).toBe(`Legal ceiling ${ceiling.figure}`);
      else if (ceiling.kind === "none") expect(ceilingValue).toBe(CEILING_NOT_AVAILABLE);
      else expect(ceilingValue).toBe(`Legal ceiling: ${ceiling.reason}`);
      const range = apartmentEstimateRange(doc);
      const estimateValue = screen.getByTestId("apartment-figures-estimate-value").textContent;
      if (range === null) expect(estimateValue).toBe(ESTIMATE_NOT_AVAILABLE);
      else expect(estimateValue).toBe(`Estimate ${range}`);
    });
  }
});

// ---- The block uses its OWN test ids ----

describe("the block uses its own test ids, never the whole-panel ones", () => {
  it("renders no answer-conditional-marker / answer-value / answer-headline-number inside the block", () => {
    render(<ApartmentFigures results={loadResultsFixture(BENCHMARK)} showDraftValues />);
    const block = screen.getByTestId("apartment-figures");
    expect(within(block).queryAllByTestId("answer-conditional-marker")).toHaveLength(0);
    expect(within(block).queryAllByTestId("answer-value")).toHaveLength(0);
    expect(within(block).queryAllByTestId("answer-headline-number")).toHaveLength(0);
  });
});
