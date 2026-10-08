import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Results } from "@/lib/architect/three-answers";
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

  it("renders the committed journey fixture at contract 1.3.0 with the three-way layer", () => {
    const { doc } = journey();
    expect(doc.contract_version).toBe("1.3.0");
    // the building option is a whole not-available answer; coverage and the rear yard are withheld.
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
