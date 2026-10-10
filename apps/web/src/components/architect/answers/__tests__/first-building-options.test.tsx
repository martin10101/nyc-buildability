import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Results } from "@/lib/architect/three-answers";
import {
  APARTMENT_SIZE_BASIS_NOTE,
  feet,
  firstBuildingOptionsView,
  percent,
  sqft,
  twoDp,
  type FirstBuildingOptionsView,
} from "@/lib/architect/first-building-options";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { FirstBuildingOptions } from "../FirstBuildingOptions";

/**
 * M5-T149 PART B: the building-option section of the results SCREEN. The component is rendered
 * DIRECTLY from the view the document builds (FirstBuildingOptions({view})), so this test depends
 * only on part B's files, never on part A's panel. The building option shows FIRST as "Building
 * option: Site fit not verified" with its "Scheduled area" (never "achieved", never "no allowance
 * left unused" — row R895), then what was not checked, its floor schedule and its own preliminary
 * capacity estimate; a withheld coverage carries NO figure (R556/R570); no building at 16 ft shows no
 * scheduled area and each building's reason from the document.
 *
 * Every expected value is READ from the loaded fixture (never retyped), through the SAME formatters
 * the view uses (sqft / feet / percent / twoDp).
 */

afterEach(cleanup);

/** building B worked, coverage withheld (step-p6 real-building-b / real-estimate-b). */
const BENCHMARK = "synthetic_building_alternatives_contract_1_4_0";
/** building A worked, coverage available with a footprint figure. */
const COVERAGE_AVAILABLE = "synthetic_coverage_by_portion_available_contract_1_4_0";
/** A stable older document (1.2.0) that carries none of the 1.4.0 blocks. */
const OLDER_NO_BLOCKS = "synthetic_scope_and_notes_contract_1_2_0";
/** The committed benchmark: building B worked plus building A not worked (and coverage withheld). */
const JOURNEY = "recorded_215_16_northern_journey";

type Alternative = NonNullable<Results["building_alternatives"]>[number];

function firstAlternative(doc: Results): Alternative {
  const alternatives = doc.building_alternatives;
  if (!alternatives || alternatives.length === 0) {
    throw new Error("fixture changed: building_alternatives must carry at least one alternative");
  }
  return alternatives[0];
}

function viewOf(doc: Results, showDraftValues = true): FirstBuildingOptionsView {
  const view = firstBuildingOptionsView(doc, showDraftValues);
  if (!view) throw new Error("fixture changed: expected a first-building-options view");
  return view;
}

function renderDoc(doc: Results, showDraftValues = true) {
  render(<FirstBuildingOptions view={viewOf(doc, showDraftValues)} />);
}

function optionsSection(): HTMLElement {
  return screen.getByTestId("first-building-options");
}

describe("PART B: the building-option section on the results screen (contract 1.4.0)", () => {
  it("S1: shows building B as a labelled alternative with its floor schedule, from the list", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const alternatives = doc.building_alternatives ?? [];
    const buildingB = firstAlternative(doc);
    renderDoc(doc);
    const blocks = within(optionsSection()).getAllByTestId("building-alternative");
    // the section reads the LIST, so more alternatives would show with no shape change.
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
  });

  it("S6: the building option is SCHEDULED, site fit not verified — never 'achieved', never 'unused'", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const buildingB = firstAlternative(doc);
    renderDoc(doc);
    const block = within(optionsSection()).getAllByTestId("building-alternative")[0];
    // the site-fit distinction FIRST: "Building option: Site fit not verified".
    expect(within(block).getByTestId("building-alternative-site-fit").textContent).toBe(
      "Building option: Site fit not verified",
    );
    // the value is the SCHEDULED area, read from the document ("20,150 sq ft").
    expect(within(block).getByTestId("building-alternative-scheduled").textContent).toBe(
      `Scheduled area: ${sqft(buildingB.total_floor_area_sqft)}`,
    );
    // storeys and height stay in the summary, but NOT any "total floor area" or "unused" figure.
    const summary = within(block).getByTestId("building-alternative-summary").textContent ?? "";
    expect(summary).toContain(`${buildingB.storey_count} storeys`);
    expect(summary).toContain(feet(buildingB.height_ft));
    // what was NOT checked, each item read from the document, in order.
    const items = within(block)
      .getAllByTestId("building-alternative-not-checked-item")
      .map(element => element.textContent);
    expect(items).toEqual(buildingB.not_checked);
    // the shared conditions are referred to BY NAME, never repeated in full (ruling V11 (5)).
    const applies = within(block).getByTestId("option-applies").textContent ?? "";
    expect(applies).toContain("Applies:");
    expect(applies).toMatch(/Condition \d/);
    const way = buildingB.way;
    if (way.way === "conditional") {
      // the full "If …" condition text does NOT appear under the building option (it is in the card).
      expect(block.textContent ?? "").not.toContain(way.conditions[0].assumption);
    }
    // the word "achieved" appears nowhere (row R895); and no "unused" / "no allowance left unused".
    const sectionText = optionsSection().textContent ?? "";
    expect(sectionText.toLowerCase()).not.toContain("achieved");
    expect(sectionText.toLowerCase()).not.toContain("unused");
    expect(sectionText).not.toMatch(/feasible|complies|legally correct|\bvalidated\b/i);
  });

  it("S6: with no building worked (16 ft), no scheduled area shows and each building's reason shows", () => {
    // Built the way the server builds the 16 ft state: building_alternatives emptied, each building of
    // the method listed as not worked with its reason read from the document.
    const base = loadResultsFixture(JOURNEY);
    const benchmarkA = (base.buildings_not_worked ?? [])[0];
    const buildingB = {
      building: "B",
      label: "Building B: the fewest storeys reaching the minimum base height",
      reason:
        "2 storeys, each needing a plan of 10,075.00 sq ft; more than the bound of 8,060 sq ft - 80 percent of the recorded lot area of 10,075 sq ft, the lowest coverage ratio that can apply.",
      gap_kind: "work_owed" as const,
      resolved_by: "A fuller massing (more storeys with a smaller plan) the program has not built yet.",
    };
    const notWorked = benchmarkA ? [benchmarkA, buildingB] : [buildingB];
    const doc = { ...base, building_alternatives: [], buildings_not_worked: notWorked } as Results;
    renderDoc(doc);
    const section = optionsSection();
    // no worked alternative, so no scheduled area and no lead about worked shapes.
    expect(within(section).queryAllByTestId("building-alternative")).toHaveLength(0);
    expect(within(section).queryAllByTestId("building-alternative-scheduled")).toHaveLength(0);
    expect(section.textContent ?? "").not.toContain("Scheduled area:");
    expect(within(section).getByTestId("first-building-options-lead").textContent ?? "").not.toContain(
      "worked from the floor-area allowance",
    );
    // each building's reason from the document, never an empty heading.
    const blocks = within(section).getAllByTestId("building-not-worked");
    expect(blocks).toHaveLength(notWorked.length);
    notWorked.forEach((entry, index) => {
      expect(within(blocks[index]).getByTestId("building-not-worked-label").textContent).toBe(entry.label);
      expect(within(blocks[index]).getByTestId("building-not-worked-reason").textContent).toBe(
        `Not known — ${entry.reason}`,
      );
    });
    // ONE WORDING PER SITUATION (ruling V11 (3)): a missing property fact (building A) carries the
    // short tag; a building the method cannot yet work (building B, work owed) carries NO tag, and no
    // second phrase ("Not built yet", "still owed") reaches the screen.
    expect(benchmarkA?.gap_kind).toBe("missing_information");
    expect(within(blocks[0]).getByTestId("building-not-worked-tag").textContent).toBe(
      "Needs property information",
    );
    expect(within(blocks[1]).queryByTestId("building-not-worked-tag")).toBeNull();
    // no not-worked block carries a second kind phrase (scoped to the blocks: the coverage block
    // below legitimately keeps its own gap line, which is a different result).
    for (const block of blocks) {
      expect(block.textContent ?? "").not.toContain("Not built yet: this part of the program is still owed.");
      expect(block.textContent ?? "").not.toContain("Missing information about this property.");
    }
  });

  it("S5: shows the building's preliminary capacity estimate as preliminary assumptions", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const estimate = firstAlternative(doc).capacity_estimate;
    if (estimate.label !== "Preliminary capacity estimate") {
      throw new Error("fixture changed: the benchmark estimate must be known");
    }
    renderDoc(doc);
    const block = within(optionsSection()).getAllByTestId("building-alternative")[0];
    const estimateBlock = within(block).getByTestId("capacity-estimate");
    // the owner label, byte-exact (D-090-R543).
    expect(within(estimateBlock).getByTestId("capacity-estimate-label").textContent).toBe(estimate.label);
    // the two quotients to two decimals (17.27 to 21.59), read from the document.
    const range = within(estimateBlock).getByTestId("capacity-estimate-range").textContent ?? "";
    expect(range).toContain(twoDp(estimate.quotient_low));
    expect(range).toContain(twoDp(estimate.quotient_high));
    // the share range and apartment size shown as preliminary assumptions.
    const share = within(estimateBlock).getByTestId("capacity-estimate-share").textContent ?? "";
    expect(share).toContain(twoDp(estimate.share_low));
    expect(share).toContain(twoDp(estimate.share_high));
    const size = within(estimateBlock).getByTestId("capacity-estimate-size").textContent ?? "";
    expect(size).toContain(sqft(estimate.apartment_size_sqft));
    // the measurement-basis words are the shared wording tied to the contract (ruling V11 (11)).
    expect(size).toContain(APARTMENT_SIZE_BASIS_NOTE);
    expect(
      within(estimateBlock).getByTestId("capacity-estimate-assumptions").textContent ?? "",
    ).toContain("Preliminary assumptions");
  });

  it("S3: coverage by portion is withheld with its reason and NO square-foot figure", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const coverage = doc.coverage_by_portion;
    if (!coverage || coverage.status !== "withheld") {
      throw new Error("fixture changed: the benchmark coverage must be withheld");
    }
    renderDoc(doc);
    const block = within(optionsSection()).getByTestId("coverage-by-portion");
    expect(within(block).getByTestId("coverage-by-portion-reason").textContent).toBe(
      `Not known — ${coverage.reason}`,
    );
    // NO footprint figure is shown for a withheld result (R556/R570); never the building's footprint.
    expect(within(block).queryByTestId("coverage-footprint")).toBeNull();
    const buildingFootprint = sqft(firstAlternative(doc).footprint_area_sqft);
    expect(block.textContent ?? "").not.toContain(buildingFootprint);
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
    renderDoc(doc);
    const block = within(optionsSection()).getByTestId("coverage-by-portion");
    expect(within(block).getByTestId("coverage-footprint").textContent).toBe(sqft(coverage.footprint_sqft));
    expect(block.textContent ?? "").toContain(percent(coverage.corner_ratio));
    expect(block.textContent ?? "").toContain(feet(coverage.corner_lot_distance_ft));
  });

  it("S4: the legal dwelling-unit limit is NOT restated in this section (it is the allowance card's)", () => {
    const doc = loadResultsFixture(BENCHMARK);
    renderDoc(doc);
    expect(within(optionsSection()).queryByTestId("legal-unit-limit")).toBeNull();
    // the preliminary capacity estimate IS shown here (kept separate from the legal limit, R688).
    expect(within(optionsSection()).getAllByTestId("capacity-estimate").length).toBeGreaterThanOrEqual(1);
  });

  it("an older document with none of the new blocks builds no view (the section is absent)", () => {
    const doc = loadResultsFixture(OLDER_NO_BLOCKS);
    expect(doc.building_alternatives ?? null).toBeNull();
    expect(doc.coverage_by_portion ?? null).toBeNull();
    expect(firstBuildingOptionsView(doc, true)).toBeNull();
  });

  it("on a draft architect surface the options are hidden behind the not-reviewed gate", () => {
    const doc = loadResultsFixture(BENCHMARK);
    expect(doc.draft).toBe(true);
    renderDoc(doc, false);
    const section = optionsSection();
    expect(within(section).getByTestId("first-building-options-draft-hidden").textContent).toBe(
      "Not available — the rules for this answer are not reviewed yet",
    );
    // no numbers reach an architect surface for a draft document.
    expect(within(section).queryByTestId("floor-schedule")).toBeNull();
    expect(within(section).queryByTestId("capacity-estimate")).toBeNull();
    expect(within(section).queryByTestId("building-options-comparison")).toBeNull();
  });

  it("S11: the floor table sits in a keyboard-reachable, named scroll box with the Running total column", () => {
    const doc = loadResultsFixture(BENCHMARK); // building B is worked, so a floor table renders
    renderDoc(doc);
    const scroll = within(optionsSection()).getByTestId("floor-schedule-scroll");
    // the box is a named region, reachable by keyboard (jsdom cannot measure, so assert structure).
    expect(scroll.getAttribute("role")).toBe("region");
    expect(scroll.getAttribute("aria-label")).toBe("Floor schedule");
    expect(scroll.getAttribute("tabindex")).toBe("0");
    const table = within(scroll).getByTestId("floor-schedule");
    expect(scroll.contains(table)).toBe(true);
    expect(within(table).getByText("Running total")).toBeInTheDocument();
  });

  it("the benchmark (building B plus building A not worked) shows one comparison, no developer word", () => {
    const doc = loadResultsFixture(JOURNEY);
    renderDoc(doc);
    const section = optionsSection();
    // two buildings exist (B worked, A not worked), so the comparison renders.
    expect(within(section).getByTestId("building-options-comparison")).toBeInTheDocument();
    // no machine snake_case word reaches the screen.
    expect(section.textContent ?? "").not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
  });
});
