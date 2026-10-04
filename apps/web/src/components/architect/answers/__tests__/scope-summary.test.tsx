import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  scopeAssumptionBasisLabel,
  scopeAssumptionKeyLabel,
  scopeAssumptionValueText,
  scopeView,
  type Results,
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

  it("puts the assumptions in a real list behind a keyboard-reachable disclosure heading", () => {
    const { doc, scope } = northern();
    render(<ThreeAnswersPanel results={doc} />);
    const disclosure = within(scopeBlock()).getByTestId("three-answers-scope-assumptions");
    expect(disclosure.tagName).toBe("DETAILS");
    expect(disclosure).not.toHaveAttribute("open");
    // The summary is the list heading and is natively keyboard-operable (same pattern as the
    // "Rule sections" and status-strip disclosures in this panel).
    const summary = disclosure.querySelector<HTMLElement>("summary");
    expect(summary?.textContent).toBe("Assumed conditions");
    const list = disclosure.querySelector<HTMLUListElement>("ul.ta-scope-assumption-list");
    expect(list).not.toBeNull();
    expect(list?.querySelectorAll<HTMLLIElement>("li")).toHaveLength(scope.assumptions.length);
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
