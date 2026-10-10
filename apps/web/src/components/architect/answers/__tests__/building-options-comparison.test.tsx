import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Results } from "@/lib/architect/three-answers";
import {
  buildingOptionsComparisonView,
  feet,
  sqft,
  storeyText,
  twoDp,
  type BuildingOptionsComparisonView,
} from "@/lib/architect/first-building-options";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { twoBuildingsDocument } from "@/test-support/results-two-buildings";
import { BuildingOptionsComparison } from "../BuildingOptionsComparison";

/**
 * M5-T149 PART B: one comparison of the step-P6 method's buildings (scenario S7; row R894). The
 * buildings sit side by side on the SAME rows, order and units; a building that was not worked reads
 * the one not-known wording with its reason, never 0 and never an empty cell; none is preferred
 * (question A2 open). Tested on the committed benchmark (building B worked, building A not worked) and
 * on the synthetic two-building document (both worked). Every expected value is READ from the loaded
 * document through the SAME formatters the view uses.
 */

afterEach(cleanup);

const BENCHMARK = "synthetic_building_alternatives_contract_1_4_0";
const COVERAGE_AVAILABLE = "synthetic_coverage_by_portion_available_contract_1_4_0";
const JOURNEY = "recorded_215_16_northern_journey";

function comparisonOf(doc: Results): BuildingOptionsComparisonView {
  const view = buildingOptionsComparisonView(doc);
  if (!view) throw new Error("expected a comparison view (two or more buildings)");
  return view;
}

function renderComparison(doc: Results) {
  render(<BuildingOptionsComparison view={comparisonOf(doc)} />);
}

/** The cells of one metric row, left to right (column order A, B). */
function rowCells(rowLabel: string): string[] {
  const rows = screen.getAllByTestId("comparison-row");
  const row = rows.find(r => (r.querySelector("th")?.textContent ?? "") === rowLabel);
  if (!row) throw new Error(`comparison row not found: ${rowLabel}`);
  return within(row)
    .getAllByTestId("comparison-cell")
    .map(cell => cell.textContent ?? "");
}

describe("PART B: the option comparison (scenario S7)", () => {
  it("S7: the synthetic two-building document shows both worked buildings side by side on the same rows and units", () => {
    const doc = twoBuildingsDocument();
    const alternatives = doc.building_alternatives ?? [];
    expect(alternatives).toHaveLength(2);
    const byId = Object.fromEntries(alternatives.map(a => [a.building, a]));
    const a = byId.A;
    const b = byId.B;
    renderComparison(doc);

    // one column header per building, in a stable order (A then B), read from the document.
    const heads = screen.getAllByTestId("comparison-column-head").map(h => h.textContent);
    expect(heads).toEqual([a.label, b.label]);

    // the same five rows, each with one unit, for both buildings — read through the view's formatters.
    expect(rowCells("Storeys")).toEqual([storeyText(a.storey_count), storeyText(b.storey_count)]);
    expect(rowCells("Height")).toEqual([feet(a.height_ft), feet(b.height_ft)]);
    expect(rowCells("Scheduled area")).toEqual([
      sqft(a.total_floor_area_sqft),
      sqft(b.total_floor_area_sqft),
    ]);
    expect(rowCells("Plan per storey")).toEqual([
      sqft(a.footprint_area_sqft),
      sqft(b.footprint_area_sqft),
    ]);
    if (a.capacity_estimate.label !== "Preliminary capacity estimate") throw new Error("fixture changed");
    if (b.capacity_estimate.label !== "Preliminary capacity estimate") throw new Error("fixture changed");
    expect(rowCells("Estimate")).toEqual([
      `${twoDp(a.capacity_estimate.quotient_low)} to ${twoDp(a.capacity_estimate.quotient_high)} apartments`,
      `${twoDp(b.capacity_estimate.quotient_low)} to ${twoDp(b.capacity_estimate.quotient_high)} apartments`,
    ]);
    // none is ranked ahead of the others (question A2 open); the forbidden word "preferred" is
    // never used on the website (ruling X5, scenario S1).
    const lead = screen.getByTestId("building-options-comparison-lead").textContent ?? "";
    expect(lead).toContain("None is ranked ahead of the others");
    expect(lead.toLowerCase()).not.toContain("preferred");

    // W1 (one wording per situation): each worked summary leads with the one-line scheduled phrase,
    // not a separate "Site fit not verified" note beside a duplicate "Scheduled area" row.
    const summaryFit = screen.getAllByTestId("comparison-summary-site-fit");
    expect(summaryFit.length).toBe(2); // both buildings are worked
    for (const el of summaryFit) {
      const text = el.textContent ?? "";
      expect(text).toContain("Scheduled floor area:");
      expect(text).toContain("site fit unverified");
      expect(text).not.toContain("Site fit not verified");
    }
  });

  it("S7: a building not worked reads 'Not known' with its reason, never 0, never an empty cell", () => {
    const doc = loadResultsFixture(JOURNEY);
    const notWorkedA = (doc.buildings_not_worked ?? []).find(e => e.building === "A");
    if (!notWorkedA) throw new Error("fixture changed: building A must be not worked on the benchmark");
    renderComparison(doc);

    // columns are A (not worked) then B (worked).
    const heads = screen.getAllByTestId("comparison-column-head").map(h => h.textContent);
    expect(heads[0]).toBe(notWorkedA.label);

    // every metric cell of the not-worked column A reads the one not-known wording — never 0, never
    // empty (row R894). (Column index 0 across every metric row.)
    for (const label of ["Storeys", "Height", "Scheduled area", "Plan per storey", "Estimate"]) {
      const cellA = rowCells(label)[0];
      expect(cellA, label).toBe("Not known");
      expect(cellA, label).not.toBe("");
      expect(cellA, label).not.toBe("0");
    }
    // the not-worked reason is shown once, with the one wording, in its summary.
    const summaries = screen.getAllByTestId("comparison-summary");
    const notKnown = summaries
      .map(s => within(s).queryByTestId("comparison-summary-not-known"))
      .find(Boolean);
    expect(notKnown?.textContent).toBe(`Not known — ${notWorkedA.reason}`);
  });

  it("the comparison table is a labelled, keyboard-reachable scroll region with real table semantics", () => {
    renderComparison(loadResultsFixture(JOURNEY));
    const scroll = screen.getByTestId("comparison-table-scroll");
    expect(scroll.getAttribute("role")).toBe("region");
    expect(scroll.getAttribute("aria-label")).toBe("Building options compared, in a table");
    expect(scroll.getAttribute("tabindex")).toBe("0");
    const table = within(scroll).getByTestId("comparison-table");
    expect(table.tagName).toBe("TABLE");
    // real table semantics: a caption, column headers and a row header per metric.
    expect(within(table).getByText("The method's buildings compared on the same measures")).toBeInTheDocument();
    expect(within(table).getAllByRole("columnheader").length).toBeGreaterThanOrEqual(3); // Measure + A + B
    expect(within(table).getAllByRole("rowheader")).toHaveLength(5); // the five metrics
    // the stacked summaries are present too (side by side wide, stacked narrow).
    expect(screen.getAllByTestId("comparison-summary")).toHaveLength(2);
  });

  it("keeps the row labels in view when the table scrolls sideways (ruling V11 (8): a sticky column)", () => {
    renderComparison(loadResultsFixture(JOURNEY));
    // every metric row header, and the corner cell, carry the sticky-first-column class.
    const rowHeads = screen.getAllByTestId("comparison-row-head");
    expect(rowHeads).toHaveLength(5);
    for (const head of rowHeads) expect(head.className).toContain("bo-compare-rowhead");
    const corner = within(screen.getByTestId("comparison-table")).getByText("Measure");
    expect(corner.className).toContain("bo-compare-rowhead");
    // the CSS makes that column sticky, with its background from a shared token (not a literal).
    const css = readFileSync(
      resolve(process.cwd(), "src/components/architect/answers", "building-options.css"),
      "utf8",
    );
    const stickyRule = css.slice(css.indexOf(".bo-compare-rowhead"));
    expect(stickyRule).toMatch(/position:\s*sticky/);
    expect(stickyRule).toMatch(/left:\s*0/);
    expect(stickyRule).toMatch(/background:\s*var\(--pt-color-/);
  });

  it("builds no comparison for a single building (a comparison of one is no comparison)", () => {
    // the committed benchmark fixture carries only building B and no not-worked building.
    const single = loadResultsFixture(BENCHMARK);
    expect(single.building_alternatives ?? []).toHaveLength(1);
    expect(single.buildings_not_worked ?? []).toHaveLength(0);
    expect(buildingOptionsComparisonView(single)).toBeNull();
    // the coverage-available fixture carries only building A.
    expect(buildingOptionsComparisonView(loadResultsFixture(COVERAGE_AVAILABLE))).toBeNull();
  });

  it("types no developer word and no colour literal", () => {
    renderComparison(loadResultsFixture(JOURNEY));
    const section = screen.getByTestId("building-options-comparison");
    expect(section.textContent ?? "").not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);

    // the building-option CSS files carry no colour literal — every colour is a shared token.
    for (const file of ["building-options.css"]) {
      const css = readFileSync(
        resolve(process.cwd(), "src/components/architect/answers", file),
        "utf8",
      );
      expect(css, file).not.toMatch(/#[0-9a-fA-F]{3,8}\b/);
      expect(css, file).not.toMatch(/\brgba?\s*\(/);
      expect(css, file).not.toMatch(/\bhsla?\s*\(/);
    }
  });
});
