import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Results } from "@/lib/architect/three-answers";
import { loadResultsFixture } from "@/test-support/results-fixtures";
import { ThreeAnswersPanel } from "../ThreeAnswersPanel";

/**
 * The CARDS leg of the one continuous recorded-data journey for 215-16 Northern Boulevard
 * (D-090-R137). It loads EXACTLY the committed journey fixture (the byte-exact engine output the
 * Python journey test asserts) and renders it through the panel, proving the web cards read the
 * recorded-data identity, scope and withheld states straight from the document. No string is copied
 * into this suite — every expected string is read from the loaded document.
 *
 * Part A owns the answers; the building options are Part B. FirstBuildingOptions keeps its props, so
 * this leg checks only that Part B's section is PRESENT, never its inside (M5-T149 part A brief).
 */

afterEach(cleanup);

const JOURNEY_FIXTURE = "recorded_215_16_northern_journey";

function journey(): { doc: Results; scope: NonNullable<Results["scope"]> } {
  const doc = loadResultsFixture(JOURNEY_FIXTURE);
  if (!doc.scope) throw new Error(`fixture changed: ${JOURNEY_FIXTURE} must carry a scope`);
  return { doc, scope: doc.scope };
}

// The panel guard's snake_case regex (three-answers-panel.test.tsx), reused so this leg proves the
// recorded-data scope block reaches the screen in plain words, with no machine code.
const SNAKE_CASE = /\b[a-z0-9]+(?:_[a-z0-9]+)+\b/;

describe("journey cards leg: 215-16 Northern recorded-data (D-090-R137)", () => {
  it("leads with the identity line: the lot, read from the committed journey fixture", () => {
    const { doc, scope } = journey();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.getByTestId("three-answers-identity-lot").textContent).toBe(scope.lot.display);
  });

  it("renders the scope label and lot identity read from the committed journey fixture", () => {
    const { doc, scope } = journey();
    render(<ThreeAnswersPanel results={doc} />);
    const block = screen.getByTestId("three-answers-scope");
    expect(within(block).getByTestId("three-answers-scope-label").textContent).toBe(scope.label);
    expect(within(block).getByTestId("three-answers-scope-lot").textContent).toBe(scope.lot.display);
  });

  it("shows every assumed condition, and the front-lot-line statement read from the document", () => {
    const { doc, scope } = journey();
    render(<ThreeAnswersPanel results={doc} />);
    const block = screen.getByTestId("three-answers-scope");
    const rows = within(block).queryAllByTestId<HTMLElement>("three-answers-scope-assumption");
    expect(rows).toHaveLength(scope.assumptions.length);
    expect(scope.assumptions).toHaveLength(12);
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
    expect(within(block).getByTestId("three-answers-scope-remaining-reason").textContent).toBe(
      scope.remaining_capacity.reason,
    );
  });

  it("puts no machine code on the screen across the recorded-data scope block", () => {
    const { doc } = journey();
    render(<ThreeAnswersPanel results={doc} />);
    expect(screen.getByTestId("three-answers-scope").textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("is a contract 1.4.0 document with the three-way layer (so the states below are real)", () => {
    const { doc } = journey();
    expect(doc.contract_version).toBe("1.4.0");
    expect(doc.building_alternatives?.length ?? 0).toBeGreaterThan(0);
    expect(doc.answers.building_option.status).toBe("not_available");
    const env = doc.answers.permitted_envelope;
    if (env.status !== "available" || !env.value_states) throw new Error("fixture changed");
    expect(env.value_states.max_lot_coverage?.way).toBe("withheld");
    expect(env.value_states.rear_yard?.way).toBe("withheld");
  });

  it("W8: a withheld envelope value shows its reason and never a number (R556)", () => {
    const { doc } = journey();
    const env = doc.answers.permitted_envelope;
    if (env.status !== "available" || !env.value_states) throw new Error("fixture changed");
    const coverage = env.value_states.max_lot_coverage;
    if (!coverage || coverage.way !== "withheld") throw new Error("fixture changed");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const card = screen.getByTestId("answer-permitted_envelope");
    const row = within(card)
      .getAllByTestId("answer-withheld-value")
      .map(entry => entry.textContent ?? "")
      .find(text => text.includes(coverage.reason));
    expect(row).toBeDefined();
    expect(row).toContain("Not known");
    expect(row).not.toMatch(/\d+%/);
  });

  it("S4: the legal dwelling-unit limit shows withheld on the allowance card, with no number", () => {
    const { doc } = journey();
    const allowance = doc.answers.floor_area_allowance;
    if (allowance.status !== "available" || !allowance.value_states) throw new Error("fixture changed");
    const limit = allowance.value_states.legal_unit_limit_standard;
    if (!limit || limit.way !== "withheld") throw new Error("fixture changed");
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const card = screen.getByTestId("answer-floor_area_allowance");
    const row = within(card)
      .getAllByTestId("answer-withheld-value")
      .find(entry => (entry.querySelector("dt")?.textContent ?? "") === limit.label);
    if (!row) throw new Error("the legal-limit withheld row is missing");
    const reason = within(row).getByTestId("answer-withheld-reason");
    expect(reason.textContent).toBe(`Not known — ${limit.reason}`);
    expect(reason.textContent ?? "").not.toMatch(/\d/);
  });

  it("the single building-option card points to the list, never the machine field name", () => {
    const { doc } = journey();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    const card = screen.getByTestId("answer-building_option");
    expect(card.textContent ?? "").toContain("Not available");
    expect(card.textContent ?? "").not.toMatch(SNAKE_CASE);
  });

  it("renders Part B's building-options section (present only — its inside is Part B's own test)", () => {
    const { doc } = journey();
    render(<ThreeAnswersPanel results={doc} showDraftValues />);
    expect(screen.getByTestId("first-building-options")).toBeInTheDocument();
  });
});
