import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  scopeAssumptionBasisLabel,
  scopeAssumptionKeyLabel,
  scopeAssumptionValueText,
  scopeView,
  type Results,
  type ScopeAssumption,
} from "@/lib/architect/three-answers";
import {
  NOT_CONFIRMED,
  REMAINING_CAPACITY_LABEL,
  REMAINING_CAPACITY_REASON,
  TAX_LOT_ONLY_ESTIMATE,
} from "@/lib/architect/tax-lot-scope";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * Scope beside the numbers (results contract 1.1.0, D-090-R108): when a document carries a
 * non-null `scope`, the panel reads the label, the lot identity, the assumed conditions, the
 * whole-site statement and the two settled remaining-capacity strings STRAIGHT FROM the document.
 * This suite renders the committed Northern scope fixture and reads the expected strings from the
 * loaded document — no scope string is copied into the component or this suite. The two settled
 * constants are pinned once, so the owner wording cannot drift between the contract and the web.
 */

afterEach(cleanup);

const SCOPE_FIXTURE = "synthetic_scope_tax_lot_only_northern";
const NO_SCOPE_FIXTURE = "synthetic_all_answers_available";

/** The Northern fixture and its scope, so a missing scope fails loudly instead of vacuously. */
function northern(): { doc: Results; scope: NonNullable<Results["scope"]> } {
  const doc = loadResultsFixture(SCOPE_FIXTURE);
  if (!doc.scope) throw new Error(`fixture changed: ${SCOPE_FIXTURE} must carry a scope`);
  return { doc, scope: doc.scope };
}

function scopeBlock(): HTMLElement {
  return screen.getByTestId("three-answers-scope");
}

describe("scope beside the numbers (D-090-R108)", () => {
  it("shows the label and lot identity read from the document", () => {
    const { doc, scope } = northern();
    render(<ThreeAnswersPanel results={doc} />);
    expect(within(scopeBlock()).getByTestId("three-answers-scope-label").textContent).toBe(
      scope.label,
    );
    expect(within(scopeBlock()).getByTestId("three-answers-scope-lot").textContent).toBe(
      scope.lot.display,
    );
  });

  it("discloses every assumed condition in order, in plain words, with its basis", () => {
    const { doc, scope } = northern();
    render(<ThreeAnswersPanel results={doc} />);
    const rows = within(scopeBlock()).getAllByTestId("three-answers-scope-assumption");
    expect(rows).toHaveLength(scope.assumptions.length);
    scope.assumptions.forEach((assumption, index) => {
      const row = rows[index];
      // Key in plain words (no raw machine key reaches the screen).
      expect(row).toHaveTextContent(scopeAssumptionKeyLabel(assumption.key));
      expect(within(row).getByTestId("three-answers-scope-assumption-value").textContent).toBe(
        scopeAssumptionValueText(assumption.value, assumption.unit),
      );
      // The basis word — assumed / entered / test fixture / default — in plain words.
      expect(within(row).getByTestId("three-answers-scope-assumption-basis").textContent).toBe(
        scopeAssumptionBasisLabel(assumption.basis),
      );
      // The statement text, byte-exact from the document, is the detail.
      expect(
        within(row).getByTestId("three-answers-scope-assumption-statement").textContent,
      ).toBe(assumption.statement);
    });
    // The settled lot line read directly (the prompt's named lot for 215-16 Northern).
    expect(within(scopeBlock()).getByTestId("three-answers-scope-lot").textContent).toBe(
      "Queens block 7334, lot 70",
    );
  });

  it("keeps whole-site and remaining capacity unconfirmed, read from the document", () => {
    const { doc, scope } = northern();
    render(<ThreeAnswersPanel results={doc} />);
    expect(within(scopeBlock()).getByTestId("three-answers-scope-whole-site").textContent).toBe(
      scope.whole_site.statement,
    );
    const remaining = within(scopeBlock()).getByTestId("three-answers-scope-remaining");
    expect(remaining.querySelector<HTMLElement>(".ta-scope-remaining-label")?.textContent).toBe(
      scope.remaining_capacity.label,
    );
    expect(
      within(remaining).getByTestId("three-answers-scope-remaining-reason").textContent,
    ).toBe(scope.remaining_capacity.reason);
  });

  it("pins the settled wording so it cannot drift between the contract and the web", () => {
    const { scope } = northern();
    expect(scope.label).toBe(TAX_LOT_ONLY_ESTIMATE);
    expect(scope.remaining_capacity.label).toBe(`${REMAINING_CAPACITY_LABEL}: ${NOT_CONFIRMED}`);
    expect(scope.remaining_capacity.reason).toBe(REMAINING_CAPACITY_REASON);
  });

  it("shows the assumptions open by default under a plain heading, nothing hidden (D-090-R119)", () => {
    const { doc, scope } = northern();
    render(<ThreeAnswersPanel results={doc} />);
    const assumptions = within(scopeBlock()).getByTestId("three-answers-scope-assumptions");
    // No disclosure wrapper: the list is not collapsed behind a toggle (the owner's reviewer
    // audit — a closed <details> hid the assumptions). The heading is a plain heading, not a
    // keyboard-operable summary, so reading the assumptions needs no interaction.
    expect(assumptions.tagName).not.toBe("DETAILS");
    expect(assumptions.querySelector("summary")).toBeNull();
    const heading = within(assumptions).getByRole("heading", { name: "Assumed conditions" });
    expect(heading).toBeVisible();
    // The real list and every row are visible straight away. toBeVisible() reports false for a
    // descendant of a closed <details>, so it would fail against the old collapsed markup.
    const list = assumptions.querySelector<HTMLUListElement>("ul.ta-scope-assumption-list");
    expect(list).not.toBeNull();
    expect(list).toBeVisible();
    const rows = within(assumptions).getAllByTestId("three-answers-scope-assumption");
    expect(rows).toHaveLength(scope.assumptions.length);
    rows.forEach(row => expect(row).toBeVisible());
  });

  it("shows the scope label beside the headline numbers on a lane-flag surface", () => {
    const { doc } = northern();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    // The allowance number shows (draft preview) and the scope label sits with it.
    expect(
      within(screen.getByTestId("answer-floor_area_allowance")).getByTestId("answer-headline"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("three-answers-scope-label").textContent).toBe(
      TAX_LOT_ONLY_ESTIMATE,
    );
  });

  it("renders unchanged when a document carries no scope (a 1.0.0 document)", () => {
    const doc = loadResultsFixture(NO_SCOPE_FIXTURE);
    expect(scopeView(doc)).toBeNull();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.queryByTestId("three-answers-scope")).toBeNull();
  });

  it("renders no scope block when a 1.1.0 document carries scope null", () => {
    const doc: Results = { ...loadResultsFixture(SCOPE_FIXTURE), scope: null };
    expect(scopeView(doc)).toBeNull();
    render(<ThreeAnswersPanel results={doc} />);
    expect(screen.queryByTestId("three-answers-scope")).toBeNull();
  });
});

/**
 * Lane D follow-up (D-090-R119/R131): the results scope grows from 5 assumed-input rows to 12 (new
 * keys zoning_district, overlay_present, special_district_present, special_density_area,
 * lot_front_ft, lot_depth_ft, site_measurement_rank). Each new key needs a plain-word label and
 * each code-like value a plain-word rendering, matching the drawings' scope vocabulary
 * (services/api/app/drawings/kit/scope.py, Lane E), so the cards read well and no snake_case or
 * enum code reaches the screen. The committed fixture at this head still carries 5 rows (Lane C
 * swaps the 12-row fixture in its own task/ PR); this suite builds the 12-row scope in the test.
 */

// The panel guard's snake_case regex (three-answers-panel.test.tsx), reused here so this suite
// proves the same "no machine code on the screen" invariant over the grown scope block.
const SNAKE_CASE = /\b[a-z0-9]+(?:_[a-z0-9]+)+\b/;

// The 7 new assumption keys with the plain-word label each must read as (requirement a).
const NEW_KEY_LABELS: ReadonlyArray<readonly [string, string]> = [
  ["zoning_district", "Zoning district"],
  ["overlay_present", "Commercial overlay present"],
  ["special_district_present", "Special purpose district"],
  ["special_density_area", "Special density area"],
  ["lot_front_ft", "Lot frontage"],
  ["lot_depth_ft", "Lot depth"],
  ["site_measurement_rank", "Site measurement basis"],
];

// Code-like string values with the plain words each must read as (requirement b): measurement-rank
// values and the housing-program code the scope carries, consistent with the drawings.
const VALUE_WORDS: ReadonlyArray<readonly [string, string]> = [
  ["city_records", "city records"],
  ["survey_entered", "survey (entered)"],
  ["approximate_tax_map", "approximate tax map"],
  ["entered", "entered"],
  ["assumed", "assumed"],
  ["standard_residence", "standard residence"],
];

// The 12 assumption rows the results scope carries on origin/task/R108-scope-all-assumed-inputs
// (the pending fixture, packages/contracts/fixtures/valid/results/synthetic_scope_tax_lot_only_
// northern.json). Copied verbatim here as a typed literal — the committed fixture at this head
// still has 5 rows (Lane C swaps it in its task/ PR). This proves the panel reads the 12-row scope
// cleanly before that swap lands under the panel guard.
const PENDING_TWELVE_ROW_ASSUMPTIONS: readonly ScopeAssumption[] = [
  { key: "zoning_district", value: "R6B", unit: null, basis: "fixture",
    statement: "Zoning district R6B is taken from the test fixture, not from a city source, in this benchmark run." },
  { key: "overlay_present", value: true, unit: null, basis: "fixture",
    statement: "A commercial overlay is assumed present (C2-2 in the benchmark), taken from the test fixture rather than a city source in this benchmark run." },
  { key: "special_district_present", value: false, unit: null, basis: "fixture",
    statement: "No special purpose district is assumed to apply; the benchmark run hard-codes this and does not read the special-district layer." },
  { key: "special_density_area", value: false, unit: null, basis: "fixture",
    statement: "The lot is assumed not to lie in a special density area; the benchmark run hard-codes this and does not read the special-density layer." },
  { key: "lot_type", value: "corner", unit: null, basis: "fixture",
    statement: "Corner lot assumed; the live data does not record the lot type." },
  { key: "lot_front_ft", value: 100.8, unit: "feet", basis: "fixture",
    statement: "The lot frontage of 100.8 feet is taken from the test fixture, not from a survey or city source, in this benchmark run." },
  { key: "lot_depth_ft", value: 100, unit: "feet", basis: "fixture",
    statement: "The lot depth of 100 feet is taken from the test fixture, not from a survey or city source, in this benchmark run." },
  { key: "site_measurement_rank", value: "city_records", unit: null, basis: "default",
    statement: "The site measurements are labelled 'City records' by default; no survey or entered measurement was supplied in this benchmark run." },
  { key: "within_100_ft_of_street_line_intersection", value: true, unit: null, basis: "assumed",
    statement: "The lot is assumed to lie within 100 feet of a street-line intersection." },
  { key: "street_line_intersection_angle_degrees", value: 90, unit: "degrees", basis: "assumed",
    statement: "The street lines are assumed to meet at a 90-degree angle." },
  { key: "housing_program", value: "standard_residence", unit: null, basis: "default",
    statement: "Standard residence is used as the default housing program." },
  { key: "floor_to_floor_ft", value: 10, unit: "feet", basis: "default",
    statement: "A 10-foot floor-to-floor height is used as the default." },
];

// The label and value words every row of the 12-row scope must render, in the pending order.
const EXPECTED_TWELVE_ROWS: ReadonlyArray<{ label: string; value: string }> = [
  { label: "Zoning district", value: "R6B" },
  { label: "Commercial overlay present", value: "Yes" },
  { label: "Special purpose district", value: "No" },
  { label: "Special density area", value: "No" },
  { label: "Lot type", value: "corner" },
  { label: "Lot frontage", value: "100.8 feet" },
  { label: "Lot depth", value: "100 feet" },
  { label: "Site measurement basis", value: "city records" },
  { label: "Within 100 ft of a street-line intersection", value: "Yes" },
  { label: "Street-line intersection angle", value: "90 degrees" },
  { label: "Housing program", value: "standard residence" },
  { label: "Floor-to-floor height", value: "10 feet" },
];

describe("new scope assumption keys and value words (D-090-R119/R131)", () => {
  for (const [key, label] of NEW_KEY_LABELS) {
    it(`labels the ${key} key as "${label}"`, () => {
      expect(scopeAssumptionKeyLabel(key)).toBe(label);
    });
  }

  it("keeps the original 5 key labels and the de-underscore fallback for a truly unknown key", () => {
    expect(scopeAssumptionKeyLabel("lot_type")).toBe("Lot type");
    expect(scopeAssumptionKeyLabel("within_100_ft_of_street_line_intersection")).toBe(
      "Within 100 ft of a street-line intersection",
    );
    expect(scopeAssumptionKeyLabel("street_line_intersection_angle_degrees")).toBe(
      "Street-line intersection angle",
    );
    expect(scopeAssumptionKeyLabel("housing_program")).toBe("Housing program");
    expect(scopeAssumptionKeyLabel("floor_to_floor_ft")).toBe("Floor-to-floor height");
    // A key the contract adds later still never prints as a raw code.
    expect(scopeAssumptionKeyLabel("some_future_key")).toBe("Some future key");
  });

  for (const [code, words] of VALUE_WORDS) {
    it(`renders the ${code} value as "${words}"`, () => {
      expect(scopeAssumptionValueText(code, null)).toBe(words);
    });
  }

  it("keeps a plain code, booleans, numbers-with-units, and the de-underscore fallback", () => {
    expect(scopeAssumptionValueText("R6B", null)).toBe("R6B");
    expect(scopeAssumptionValueText(true, null)).toBe("Yes");
    expect(scopeAssumptionValueText(false, null)).toBe("No");
    expect(scopeAssumptionValueText(100.8, "feet")).toBe("100.8 feet");
    // An unmapped code-like string still de-underscores, so the panel guard sees no snake_case.
    expect(scopeAssumptionValueText("qualifying_affordable_housing", null)).toBe(
      "qualifying affordable housing",
    );
  });

  it("reads the 12-row scope cleanly: every label, every value word, and no snake_case", () => {
    const { doc, scope } = northern();
    const twelve: Results = {
      ...doc,
      scope: { ...scope, assumptions: [...PENDING_TWELVE_ROW_ASSUMPTIONS] },
    };
    render(<ThreeAnswersPanel results={twelve} />);
    const rows = within(scopeBlock()).getAllByTestId("three-answers-scope-assumption");
    expect(rows).toHaveLength(EXPECTED_TWELVE_ROWS.length);
    EXPECTED_TWELVE_ROWS.forEach((expected, index) => {
      const row = rows[index];
      expect(row).toHaveTextContent(expected.label);
      expect(
        within(row).getByTestId("three-answers-scope-assumption-value").textContent,
      ).toBe(expected.value);
    });
    // No machine code reaches the screen across the whole grown block (panel guard invariant).
    expect(scopeBlock().textContent ?? "").not.toMatch(SNAKE_CASE);
  });
});
