import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Results } from "@/lib/architect/three-answers";
import { feet, percent, sqft, twoDp } from "@/lib/architect/first-building-options";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * PART C (first half): the results SCREEN shows the additive contract-1.4.0 blocks — the worked
 * first-building alternatives with their floor schedules, conditions, what was not checked and each
 * building's preliminary capacity estimate; the legal dwelling-unit limit kept separate (withheld,
 * no substitute); and coverage by portion (withheld with no figure, or its figures when available).
 *
 * Every expected value is READ from the loaded synthetic fixture (never retyped), through the SAME
 * formatters the panel uses (sqft / feet / percent / twoDp). The fixtures trace to
 * docs/reference-cases/R6B/cases/step-p6-worked.json rows real-building-b / real-estimate-b and the
 * coverage-by-portion rows (M5-T146 part A). The committed benchmark document is NOT read here: those
 * tests follow in the second half when part E regenerates it to 1.4.0.
 */

afterEach(cleanup);

/** building B, coverage withheld (benchmark; step-p6 real-building-b / real-estimate-b). */
const BENCHMARK = "synthetic_building_alternatives_contract_1_4_0";
/** building A, coverage available with a footprint figure. */
const COVERAGE_AVAILABLE = "synthetic_coverage_by_portion_available_contract_1_4_0";
/** A stable older document (1.2.0) that carries none of the 1.4.0 blocks. The only 1.3.0 fixture is
 * the committed benchmark, which part E regenerates to 1.4.0, so the first-half "unchanged screen"
 * proof uses this stable synthetic fixture instead. */
const OLDER_NO_BLOCKS = "synthetic_scope_and_notes_contract_1_2_0";

type Alternative = NonNullable<Results["building_alternatives"]>[number];

function firstAlternative(doc: Results): Alternative {
  const alternatives = doc.building_alternatives;
  if (!alternatives || alternatives.length === 0) {
    throw new Error("fixture changed: building_alternatives must carry at least one alternative");
  }
  return alternatives[0];
}

function optionsSection(): HTMLElement {
  return screen.getByTestId("first-building-options");
}

describe("PART C: the first-building-options section on the results screen (contract 1.4.0)", () => {
  it("S1: shows building B as a labelled alternative with its floor schedule, from the list", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const alternatives = doc.building_alternatives ?? [];
    const buildingB = firstAlternative(doc);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const blocks = within(optionsSection()).getAllByTestId("building-alternative");
    // the panel reads the LIST, so more alternatives would show with no shape change.
    expect(blocks).toHaveLength(alternatives.length);
    const block = blocks[0];
    // a labelled alternative, read from the document; none is preferred or default.
    expect(within(block).getByTestId("building-alternative-label").textContent).toBe(buildingB.label);
    // the floor schedule is a real table: one body row per worked storey.
    const table = within(block).getByTestId("floor-schedule");
    expect(table.tagName).toBe("TABLE");
    const rows = within(table).getAllByTestId("floor-schedule-row");
    expect(rows).toHaveLength(buildingB.storey_count);
    buildingB.floor_schedule.forEach((row, index) => {
      expect(rows[index].textContent).toContain(sqft(row.plan_area_sqft));
      expect(rows[index].textContent).toContain(sqft(row.running_total_sqft));
    });
    // the summary shows the storeys (3), height (30 ft) and total (20,150 sq ft), read from the doc.
    const summary = within(block).getByTestId("building-alternative-summary").textContent ?? "";
    expect(summary).toContain(`${buildingB.storey_count} storeys`);
    expect(summary).toContain(feet(buildingB.height_ft));
    expect(summary).toContain(sqft(buildingB.total_floor_area_sqft));
    // nothing is called feasible.
    expect(optionsSection().textContent ?? "").not.toMatch(/feasible|complies|legally correct/i);
  });

  it("S2: shows the building's preliminary capacity estimate as editable preliminary assumptions", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const estimate = firstAlternative(doc).capacity_estimate;
    if (estimate.label !== "Preliminary capacity estimate") {
      throw new Error("fixture changed: the benchmark estimate must be known");
    }
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = within(optionsSection()).getAllByTestId("building-alternative")[0];
    const estimateBlock = within(block).getByTestId("capacity-estimate");
    // the owner label, byte-exact (D-090-R543).
    expect(within(estimateBlock).getByTestId("capacity-estimate-label").textContent).toBe(estimate.label);
    // the two quotients to two decimals (17.27 to 21.59), read from the document.
    const range = within(estimateBlock).getByTestId("capacity-estimate-range").textContent ?? "";
    expect(range).toContain(twoDp(estimate.quotient_low));
    expect(range).toContain(twoDp(estimate.quotient_high));
    // the share range and apartment size shown as editable preliminary assumptions.
    const share = within(estimateBlock).getByTestId("capacity-estimate-share").textContent ?? "";
    expect(share).toContain(twoDp(estimate.share_low));
    expect(share).toContain(twoDp(estimate.share_high));
    const size = within(estimateBlock).getByTestId("capacity-estimate-size").textContent ?? "";
    expect(size).toContain(sqft(estimate.apartment_size_sqft));
    expect(
      within(estimateBlock).getByTestId("capacity-estimate-assumptions").textContent ?? "",
    ).toContain("Preliminary assumptions");
  });

  it("S3: shows coverage by portion withheld with its reason and NO square-foot figure", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const coverage = doc.coverage_by_portion;
    if (!coverage || coverage.status !== "withheld") {
      throw new Error("fixture changed: the benchmark coverage must be withheld");
    }
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = within(optionsSection()).getByTestId("coverage-by-portion");
    // the law by portion is carried in the reason, read from the document (100 percent / 80 percent).
    expect(within(block).getByTestId("coverage-by-portion-reason").textContent).toBe(
      `Not known — ${coverage.reason}`,
    );
    expect(block.textContent ?? "").toContain(coverage.reason);
    // NO footprint figure is shown for a withheld result (R556/R570).
    expect(within(block).queryByTestId("coverage-footprint")).toBeNull();
    // what would settle it, read from the document.
    expect(within(block).getByTestId("coverage-by-portion-resolved").textContent).toContain(
      coverage.resolved_by,
    );
  });

  it("S3b: when the document carries an available coverage, shows its figures", () => {
    const doc = loadResultsFixture(COVERAGE_AVAILABLE);
    const coverage = doc.coverage_by_portion;
    if (!coverage || coverage.status !== "available") {
      throw new Error("fixture changed: this fixture must carry an available coverage");
    }
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = within(optionsSection()).getByTestId("coverage-by-portion");
    expect(within(block).getByTestId("coverage-footprint").textContent).toBe(sqft(coverage.footprint_sqft));
    expect(block.textContent ?? "").toContain(percent(coverage.corner_ratio));
    expect(block.textContent ?? "").toContain(percent(coverage.interior_ratio));
    expect(block.textContent ?? "").toContain(feet(coverage.corner_lot_distance_ft));
  });

  it("S4: the legal dwelling-unit limit is NOT restated in this section (it is the allowance card's)", () => {
    // On the regenerated benchmark the legal dwelling-unit limit is a withheld value_state of the
    // floor-area-allowance answer (shown by that card; see journey-215-16-northern.test.tsx S4), and
    // the top-level unit_estimate is a pointer to this list — so this section must NOT restate it (no
    // contradiction with the shown estimate, coordinator point 3; R688).
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(within(optionsSection()).queryByTestId("legal-unit-limit")).toBeNull();
    // the preliminary capacity estimate IS shown here (kept separate from the legal limit, R688).
    expect(within(optionsSection()).getAllByTestId("capacity-estimate").length).toBeGreaterThanOrEqual(1);
  });

  it("S5: a withheld coverage result never falls back to a substitute value (R570)", () => {
    // The benchmark withholds coverage but carries building B's footprint (6,716.67 sq ft). The
    // withheld coverage block must show no figure, and never the building's footprint in its place.
    const doc = loadResultsFixture(BENCHMARK);
    const coverage = doc.coverage_by_portion;
    if (!coverage || coverage.status !== "withheld") throw new Error("fixture changed");
    const buildingFootprint = sqft(firstAlternative(doc).footprint_area_sqft);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = within(optionsSection()).getByTestId("coverage-by-portion");
    expect(within(block).queryByTestId("coverage-footprint")).toBeNull();
    expect(block.textContent ?? "").not.toContain(buildingFootprint);
  });

  it("S6: shows what has not been checked and never calls an option feasible", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const alternative = firstAlternative(doc);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = within(optionsSection()).getAllByTestId("building-alternative")[0];
    // the option is conditional, not settled: the marker is a WORD, not a colour.
    expect(within(block).getByTestId("option-conditional-marker").textContent).toBe("Conditional");
    // what was not checked, each item read from the document, in order.
    const items = within(block)
      .getAllByTestId("building-alternative-not-checked-item")
      .map(element => element.textContent);
    expect(items).toEqual(alternative.not_checked);
    expect(optionsSection().textContent ?? "").not.toMatch(/feasible|complies|legally correct|\bvalidated\b/i);
  });

  it("S7: the overall results label stays 'Preliminary zoning results' on a 1.4.0 document", () => {
    const doc = loadResultsFixture(BENCHMARK);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const strip = screen.getByTestId("three-answers-status-strip");
    const items = within(strip)
      .getAllByTestId("three-answers-status-item")
      .map(element => element.textContent);
    expect(items).toContain("Preliminary zoning results");
    // the label is read from the document, not typed into the panel.
    expect(doc.status_strip.map(item => item.text)).toContain("Preliminary zoning results");
  });

  it("an older document with none of the new blocks shows no first-building-options section", () => {
    const doc = loadResultsFixture(OLDER_NO_BLOCKS);
    expect(doc.building_alternatives ?? null).toBeNull();
    expect(doc.coverage_by_portion ?? null).toBeNull();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.queryByTestId("first-building-options")).toBeNull();
  });

  it("on a draft architect surface the options are hidden behind the not-reviewed gate", () => {
    const doc = loadResultsFixture(BENCHMARK);
    expect(doc.draft).toBe(true);
    render(<ThreeAnswersPanel results={doc} />);
    const section = screen.getByTestId("first-building-options");
    expect(within(section).getByTestId("first-building-options-draft-hidden").textContent).toBe(
      "Not available — the rules for this answer are not reviewed yet",
    );
    // no numbers reach an architect surface for a draft document.
    expect(within(section).queryByTestId("floor-schedule")).toBeNull();
    expect(within(section).queryByTestId("capacity-estimate")).toBeNull();
  });
});

describe("PART C walkthrough correction: no building listed (F1/S9) and the narrow table (N4/S11)", () => {
  type NotWorked = NonNullable<Results["buildings_not_worked"]>[number];

  /** A 16 ft document, BUILT FROM THE REGENERATED COMMITTED BENCHMARK the way the server does at
   * 16 ft (M5-T146 part B "Walkthrough correction", state S25): building_alternatives emptied, and
   * buildings_not_worked = the benchmark's real building A entry plus a constructed building B entry.
   * The screen assertions read every shown string from this document object, never a typed value. */
  function noBuildingListed(): { doc: Results; notWorked: NotWorked[] } {
    const base = loadResultsFixture("recorded_215_16_northern_journey");
    const benchmarkA = (base.buildings_not_worked ?? [])[0];
    const buildingB: NotWorked = {
      building: "B",
      label: "Building B: the fewest storeys reaching the minimum base height",
      reason:
        "2 storeys, each needing a plan of 10,075.00 sq ft; more than the bound of 8,060 sq ft - 80 percent of the recorded lot area of 10,075 sq ft, the lowest coverage ratio that can apply.",
      gap_kind: "work_owed",
      resolved_by: "A fuller massing (more storeys with a smaller plan) the program has not built yet.",
    };
    const notWorked: NotWorked[] = benchmarkA ? [benchmarkA, buildingB] : [buildingB];
    const doc: Results = { ...base, building_alternatives: [], buildings_not_worked: notWorked };
    return { doc, notWorked };
  }

  it("S9: with no building listed, the section names each not-worked building, its reason and resolver, and no worked-shapes lead", () => {
    const { doc, notWorked } = noBuildingListed();
    expect(notWorked.length).toBeGreaterThanOrEqual(2); // A and B
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const section = optionsSection();
    // no building is shown as a worked alternative, and no lead speaks of worked shapes.
    expect(within(section).queryAllByTestId("building-alternative")).toHaveLength(0);
    expect(within(section).getByTestId("first-building-options-lead").textContent ?? "").not.toContain(
      "worked from the floor-area allowance",
    );
    // the heading is never empty: each not-worked building shows its label, reason and resolver.
    const blocks = within(section).getAllByTestId("building-not-worked");
    expect(blocks).toHaveLength(notWorked.length);
    notWorked.forEach((entry, index) => {
      const block = blocks[index];
      expect(within(block).getByTestId("building-not-worked-label").textContent).toBe(entry.label);
      expect(within(block).getByTestId("building-not-worked-reason").textContent).toBe(
        `Not known — ${entry.reason}`,
      );
      expect(within(block).getByTestId("building-not-worked-resolved").textContent).toContain(
        entry.resolved_by,
      );
    });
    // the single Building option card points to the section, never the document's machine reason.
    const optionCard = screen.getByTestId("answer-building_option");
    expect(optionCard.textContent ?? "").toContain("Not available");
    expect(optionCard.textContent ?? "").not.toContain("building_alternatives");
    expect(optionCard.textContent ?? "").not.toContain("buildings_not_worked");
    // no machine code or false reason anywhere in the section.
    expect(section.textContent ?? "").not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
    expect(section.textContent ?? "").not.toContain("below the minimum base height");
  });

  it("S11: the floor table sits in a keyboard-reachable, named scroll box with the Running total column", () => {
    const doc = loadResultsFixture(BENCHMARK); // building B is worked, so a floor table renders
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const scroll = within(optionsSection()).getByTestId("floor-schedule-scroll");
    // the box is a named region, reachable by keyboard (jsdom cannot measure, so assert structure).
    expect(scroll.getAttribute("role")).toBe("region");
    expect(scroll.getAttribute("aria-label")).toBe("Floor schedule");
    expect(scroll.getAttribute("tabindex")).toBe("0");
    expect(scroll.className).toContain("ta-floor-schedule-scroll");
    // the table is inside the box, and the Running total column header is reachable within it.
    const table = within(scroll).getByTestId("floor-schedule");
    expect(scroll.contains(table)).toBe(true);
    expect(within(table).getByText("Running total")).toBeInTheDocument();
  });
});
