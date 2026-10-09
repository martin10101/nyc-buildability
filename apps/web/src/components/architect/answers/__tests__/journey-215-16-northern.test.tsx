import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Results } from "@/lib/architect/three-answers";
import { twoDp } from "@/lib/architect/first-building-options";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * The CARDS leg of the one continuous recorded-data journey for 215-16 Northern Boulevard
 * (D-090-R137). It loads EXACTLY the committed journey fixture (the byte-exact engine output
 * the Python journey test asserts) and renders it through the same panel the generic suite
 * uses, proving the web cards read the recorded-data scope beside the numbers.
 *
 * This is the web leg of the journey; vitest runs in CI only (thin client), so this proves
 * the cards render ONLY on the pushed head, never from local reasoning. No scope string is
 * copied into this suite - every expected string is read from the loaded document.
 */

afterEach(cleanup);

const JOURNEY_FIXTURE = "recorded_215_16_northern_journey";

/** The committed journey fixture and its scope, so a missing scope fails loudly, not vacuously. */
function journey(): { doc: Results; scope: NonNullable<Results["scope"]> } {
  const doc = loadResultsFixture(JOURNEY_FIXTURE);
  if (!doc.scope) throw new Error(`fixture changed: ${JOURNEY_FIXTURE} must carry a scope`);
  return { doc, scope: doc.scope };
}

// The panel guard's snake_case regex (three-answers-panel.test.tsx), reused so this leg proves
// the recorded-data scope block reaches the screen in plain words, with no machine code.
const SNAKE_CASE = /\b[a-z0-9]+(?:_[a-z0-9]+)+\b/;

describe("journey cards leg: 215-16 Northern recorded-data scope (D-090-R137)", () => {
  it("renders the scope label and lot identity read from the committed journey fixture", () => {
    const { doc, scope } = journey();
    render(<ThreeAnswersPanel results={doc} />);
    const block = screen.getByTestId("three-answers-scope");
    expect(within(block).getByTestId("three-answers-scope-label").textContent).toBe(scope.label);
    expect(within(block).getByTestId("three-answers-scope-lot").textContent).toBe(
      scope.lot.display,
    );
  });

  it("shows every assumed condition, and the front-lot-line statement read from the document", () => {
    const { doc, scope } = journey();
    render(<ThreeAnswersPanel results={doc} />);
    const block = screen.getByTestId("three-answers-scope");
    const rows = within(block).queryAllByTestId<HTMLElement>("three-answers-scope-assumption");
    expect(rows).toHaveLength(scope.assumptions.length);
    expect(scope.assumptions).toHaveLength(12);

    // The front-lot-line disclosure for the corner lot, its statement byte-exact from the
    // document (the address-street assumption the journey rests on).
    const frontIndex = scope.assumptions.findIndex(assumption => assumption.key === "lot_front_ft");
    expect(frontIndex).toBeGreaterThanOrEqual(0);
    const frontStatement = scope.assumptions[frontIndex].statement;
    expect(frontStatement).toContain("Northern Boulevard");
    const statement = within(rows[frontIndex]).getByTestId(
      "three-answers-scope-assumption-statement",
    );
    expect(statement.textContent).toBe(frontStatement);
    expect(statement).toBeVisible();
  });

  it("keeps whole-site and remaining capacity unconfirmed, read from the document", () => {
    const { doc, scope } = journey();
    render(<ThreeAnswersPanel results={doc} />);
    const block = screen.getByTestId("three-answers-scope");
    expect(within(block).getByTestId("three-answers-scope-whole-site").textContent).toBe(
      scope.whole_site.statement,
    );
    expect(
      within(block).getByTestId("three-answers-scope-remaining-reason").textContent,
    ).toBe(scope.remaining_capacity.reason);
  });

  it("puts no machine code on the screen across the recorded-data scope block", () => {
    const { doc } = journey();
    render(<ThreeAnswersPanel results={doc} />);
    expect(screen.getByTestId("three-answers-scope").textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("renders the regenerated committed journey fixture at contract 1.4.0 with the three-way layer", () => {
    const { doc } = journey();
    expect(doc.contract_version).toBe("1.4.0");
    // the regenerated document carries the worked first-building alternatives (contract 1.4.0).
    expect((doc.building_alternatives?.length ?? 0)).toBeGreaterThan(0);
    // the single building option is a whole not-available answer; coverage and the rear yard withheld.
    expect(doc.answers.building_option.status).toBe("not_available");
    const env = doc.answers.permitted_envelope;
    if (env.status !== "available" || !env.value_states) throw new Error("fixture changed");
    expect(env.value_states.max_lot_coverage?.way).toBe("withheld");
    expect(env.value_states.rear_yard?.way).toBe("withheld");
  });

  it("W8: on a lane-flag surface a withheld value shows its reason and never a number", () => {
    // The journey fixture is a draft; the lane-flag surface shows the numbers. A withheld value
    // (coverage) is rendered as its reason, never a number falling back from another value (R556).
    const { doc } = journey();
    const env = doc.answers.permitted_envelope;
    if (env.status !== "available" || !env.value_states) throw new Error("fixture changed");
    const coverageReason = env.value_states.max_lot_coverage;
    if (!coverageReason || coverageReason.way !== "withheld") throw new Error("fixture changed");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const card = screen.getByTestId("answer-permitted_envelope");
    const withheld = within(card).queryAllByTestId("answer-withheld-value");
    const texts = withheld.map(row => row.textContent ?? "");
    // coverage shows its reason, with "Not known" and no percentage
    const coverageRow = texts.find(text => text.includes(coverageReason.reason));
    expect(coverageRow).toBeDefined();
    expect(coverageRow).toContain("Not known");
    expect(coverageRow).not.toMatch(/\d+%/);
    // no headline number is the coverage figure (it never falls back to a shown value)
    expect(within(card).queryAllByTestId("answer-withheld-value").length).toBeGreaterThanOrEqual(2);
  });
});

describe("M5-T147 PART C: the first building option on the regenerated screen (contract 1.4.0)", () => {
  type Alternative = NonNullable<Results["building_alternatives"]>[number];

  function firstAlternative(doc: Results): Alternative {
    const alternatives = doc.building_alternatives;
    if (!alternatives || alternatives.length === 0) {
      throw new Error("fixture changed: the regenerated journey must carry building_alternatives");
    }
    return alternatives[0];
  }

  it("S1/S2/S6: building B is a labelled alternative with its floor schedule, conditions, what was not checked and its estimate", () => {
    const doc = loadResultsFixture(JOURNEY_FIXTURE);
    const buildingB = firstAlternative(doc);
    const estimate = buildingB.capacity_estimate;
    if (estimate.label !== "Preliminary capacity estimate") throw new Error("fixture changed");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const section = screen.getByTestId("first-building-options");
    const block = within(section).getAllByTestId("building-alternative")[0];
    expect(within(block).getByTestId("building-alternative-label").textContent).toBe(buildingB.label);
    const rows = within(within(block).getByTestId("floor-schedule")).getAllByTestId("floor-schedule-row");
    expect(rows).toHaveLength(buildingB.storey_count);
    // the estimate under the owner label, its quotients read from the document
    expect(within(block).getByTestId("capacity-estimate-label").textContent).toBe("Preliminary capacity estimate");
    const range = within(block).getByTestId("capacity-estimate-range").textContent ?? "";
    expect(range).toContain(twoDp(estimate.quotient_low));
    expect(range).toContain(twoDp(estimate.quotient_high));
    // what was not checked, each item read from the document
    expect(
      within(block)
        .getAllByTestId("building-alternative-not-checked-item")
        .map(element => element.textContent),
    ).toEqual(buildingB.not_checked);
    // conditional, never settled; the marker is a word, not a colour
    expect(within(block).getByTestId("option-conditional-marker").textContent).toBe("Conditional");
    // nothing is called feasible
    expect(section.textContent ?? "").not.toMatch(/feasible|complies|legally correct/i);
  });

  it("shows fit_note beside the building as plain text (read from the document)", () => {
    const doc = loadResultsFixture(JOURNEY_FIXTURE);
    const buildingB = firstAlternative(doc);
    if (!buildingB.fit_note) throw new Error("fixture changed: the regenerated journey must carry fit_note");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = within(screen.getByTestId("first-building-options")).getAllByTestId("building-alternative")[0];
    expect(within(block).getByTestId("building-alternative-fit-note").textContent).toBe(buildingB.fit_note);
  });

  it("S3: coverage by portion is withheld with its reason and NO figure", () => {
    const doc = loadResultsFixture(JOURNEY_FIXTURE);
    const coverage = doc.coverage_by_portion;
    if (!coverage || coverage.status !== "withheld") {
      throw new Error("fixture changed: the regenerated journey coverage must be withheld");
    }
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const block = within(screen.getByTestId("first-building-options")).getByTestId("coverage-by-portion");
    expect(within(block).getByTestId("coverage-by-portion-reason").textContent).toBe(
      `Not known — ${coverage.reason}`,
    );
    expect(within(block).queryByTestId("coverage-footprint")).toBeNull();
  });

  it("S4: the legal dwelling-unit limit shows withheld on the allowance card, with no number", () => {
    const doc = loadResultsFixture(JOURNEY_FIXTURE);
    const allowance = doc.answers.floor_area_allowance;
    if (allowance.status !== "available" || !allowance.value_states) throw new Error("fixture changed");
    const limit = allowance.value_states.legal_unit_limit_standard;
    if (!limit || limit.way !== "withheld") {
      throw new Error("fixture changed: the legal dwelling-unit limit must be withheld");
    }
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const card = screen.getByTestId("answer-floor_area_allowance");
    const row = within(card)
      .getAllByTestId("answer-withheld-value")
      .find(entry => (entry.querySelector("dt")?.textContent ?? "") === limit.label);
    if (!row) throw new Error("the legal-limit withheld row is missing");
    const reason = within(row).getByTestId("answer-withheld-reason");
    expect(reason.textContent).toBe(`Not known — ${limit.reason}`);
    // the withheld legal limit carries no number, no older or substitute value (R556/R570)
    expect(reason.textContent ?? "").not.toMatch(/\d/);
  });

  it("the single building-option card points to the list, never the machine field name", () => {
    const doc = loadResultsFixture(JOURNEY_FIXTURE);
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const card = screen.getByTestId("answer-building_option");
    expect(card.textContent ?? "").toContain("Not available");
    expect(card.textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("S10: building A (not worked) is named after the listed building, with its reason and resolver, and no footprint figure", () => {
    const doc = loadResultsFixture(JOURNEY_FIXTURE);
    const notWorked = doc.buildings_not_worked ?? [];
    const buildingA = notWorked.find(entry => entry.building === "A");
    if (!buildingA) throw new Error("fixture changed: the regenerated journey must list building A as not worked");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const section = screen.getByTestId("first-building-options");
    // the listed building comes first, the not-worked building after it.
    const worked = within(section).getAllByTestId("building-alternative");
    const notWorkedBlocks = within(section).getAllByTestId("building-not-worked");
    expect(worked.length).toBeGreaterThan(0);
    expect(notWorkedBlocks.length).toBe(notWorked.length);
    const aBlock = notWorkedBlocks.find(
      block => (within(block).getByTestId("building-not-worked-label").textContent ?? "") === buildingA.label,
    );
    if (!aBlock) throw new Error("building A's not-worked block is missing");
    expect(within(aBlock).getByTestId("building-not-worked-reason").textContent).toBe(
      `Not known — ${buildingA.reason}`,
    );
    expect(within(aBlock).getByTestId("building-not-worked-resolved").textContent).toContain(
      buildingA.resolved_by,
    );
    // nothing in building A reads as a footprint FIGURE: its block carries no square-foot number (the
    // label's words "the widest footprint" are fine; a withheld footprint never shows a figure).
    expect(aBlock.textContent ?? "").not.toContain(" sq ft");
    // the whole section still carries no machine code.
    expect(section.textContent ?? "").not.toMatch(SNAKE_CASE);
  });
});
