import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CompareScreen } from "@/components/compare/CompareScreen";
import { ScenarioWorkspace } from "@/components/architect/ScenarioWorkspace";
import { CalculationEvidence } from "@/components/architect/CalculationEvidence";
import { scenarioCap } from "@/lib/architect/development-limits";
import {
  UNUSED_FLOOR_AREA_NOT_AVAILABLE_KEY,
  UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON,
  UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT,
  needsExistingZoningFloorArea,
} from "@/lib/architect/unused-floor-area";
import { validateScenarioDocument, type Scenario } from "@/lib/scenario-contract";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import {
  FIXTURE_BBL,
  computedUnusedFloorAreaBody,
  jsonResponse,
  notAvailableUnusedFloorAreaBody,
  overBuiltUnusedFloorAreaBody,
  preliminaryScenarioBody,
  professionalReviewScenarioBody,
  stubFetch,
} from "./scenario-fixtures";

/**
 * D-06 (plan §3 step 4 "Existing building", M2-07; RECONCILIATION set-aside
 * item #6, C-3). Plan §3 step 4: existing floor area is never taken from
 * city-recorded (DOF) building area; without a verified value, remaining
 * capacity shows the owner's settled wording (D-090-R038, 2026-10-01, which
 * replaces plan §3 step 4's): "Remaining development capacity: Not confirmed",
 * then "Needs verified zoning-lot boundaries and existing zoning floor area."
 * The full-site allowance still shows.
 *
 *   OFF (default) — the unused-floor-area section is set aside: the scenario
 *     views show no unused-floor-area number, only those two lines.
 *   ON  — the kept section renders; when the server's section carries the
 *     `unused_floor_area_not_available` basis record (A-03 default), the line
 *     replaces the misleading "No existing building floor-area record" gloss.
 */

vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
afterEach(cleanup);

// Owner wording (D-090-R038), retyped on purpose so a drift in either constant is caught.
const NOT_AVAILABLE = "Remaining development capacity: Not confirmed";
const NOT_AVAILABLE_REASON = "Needs verified zoning-lot boundaries and existing zoning floor area.";
const MISLEADING_GLOSS = "No existing building floor-area record";

function renderCompare(body: Record<string, unknown>, enabled?: boolean) {
  return render(
    <CompareScreen
      bbl={FIXTURE_BBL}
      fetchImpl={stubFetch(jsonResponse(body, 200))}
      unusedFloorAreaSectionEnabled={enabled}
    />,
  );
}

/** A typed document from a fixture body, proven valid by the mirror validator. */
function asScenario(body: Record<string, unknown>, bbl?: string): Scenario {
  if (bbl !== undefined) (body.evaluated_input as Record<string, unknown>).bbl = bbl;
  const result = validateScenarioDocument(body);
  if (!result.ok) throw new Error(result.problems.join("; "));
  return result.document;
}

function section(body: Record<string, unknown>): Record<string, unknown> {
  return body.unused_draft_zoning_floor_area as Record<string, unknown>;
}

function expectOneNotAvailableLine() {
  const lines = screen.getAllByTestId("unused-floor-area-not-available");
  expect(lines).toHaveLength(1);
  expect(lines[0].textContent).toBe(NOT_AVAILABLE);
  // Line 2, the reason, directly under line 1.
  const reasons = screen.getAllByTestId("unused-floor-area-not-available-reason");
  expect(reasons).toHaveLength(1);
  expect(reasons[0].textContent).toBe(NOT_AVAILABLE_REASON);
  expect(lines[0].nextElementSibling).toBe(reasons[0]);
}

describe("vocabulary", () => {
  it("uses the owner's exact words and the server's basis-record key", () => {
    expect(UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT).toBe(NOT_AVAILABLE);
    expect(UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON).toBe(NOT_AVAILABLE_REASON);
    expect(UNUSED_FLOOR_AREA_NOT_AVAILABLE_KEY).toBe("unused_floor_area_not_available");
  });

  it("keys the not-available state on the basis record, never on the typed reason", () => {
    const notAvailable = asScenario(notAvailableUnusedFloorAreaBody());
    const legacyMissing = asScenario(preliminaryScenarioBody());
    // Same typed reason on both; only the server's basis record differs.
    expect(notAvailable.unused_draft_zoning_floor_area.not_computable_reason).toBe("missing_existing_building_area");
    expect(legacyMissing.unused_draft_zoning_floor_area.not_computable_reason).toBe("missing_existing_building_area");
    expect(needsExistingZoningFloorArea(notAvailable.unused_draft_zoning_floor_area)).toBe(true);
    expect(needsExistingZoningFloorArea(legacyMissing.unused_draft_zoning_floor_area)).toBe(false);
    expect(needsExistingZoningFloorArea(asScenario(computedUnusedFloorAreaBody()).unused_draft_zoning_floor_area)).toBe(false);
  });
});

describe("Compare screen — flag OFF (default): the section is set aside", () => {
  const CASES: Array<[string, () => Record<string, unknown>]> = [
    ["A-03 default (not available, recorded area on file)", () => notAvailableUnusedFloorAreaBody()],
    ["legacy computed remainder", () => computedUnusedFloorAreaBody()],
    ["legacy over-built remainder", () => overBuiltUnusedFloorAreaBody()],
    ["legacy missing record (shared preliminary fixture)", preliminaryScenarioBody],
    ["no_scenario (shared professional-review fixture)", professionalReviewScenarioBody],
  ];

  for (const [name, build] of CASES) {
    it(`shows only the owner's two lines and no unused-floor-area number: ${name}`, async () => {
      renderCompare(build());
      await screen.findByTestId("scenario-result");

      expect(screen.queryByTestId("scenario-unused-floor-area")).toBeNull();
      expect(screen.queryByRole("heading", { name: "Floor-area record comparison" })).toBeNull();
      expect(screen.queryByTestId("scenario-unused-floor-area-value")).toBeNull();
      expect(screen.queryByTestId("scenario-unused-floor-area-over-built")).toBeNull();
      expect(screen.queryByTestId("scenario-unused-floor-area-review")).toBeNull();
      expect(screen.queryByText(new RegExp(MISLEADING_GLOSS))).toBeNull();

      const card = screen.getByTestId("scenario-unused-floor-area-set-aside");
      // The two lines carry their own row label; no other label names the same quantity.
      expect(within(card).queryByRole("heading")).toBeNull();
      expect(card.textContent).toBe(`${NOT_AVAILABLE}${NOT_AVAILABLE_REASON}`);
      expectOneNotAvailableLine();
      expect(card).toContainElement(screen.getByTestId("unused-floor-area-not-available"));
      expect(card).toContainElement(screen.getByTestId("unused-floor-area-not-available-reason"));
    });
  }

  it("hides a legacy computed remainder and keeps the full-site allowance", async () => {
    const body = computedUnusedFloorAreaBody(); // cap 15,000 − recorded 10,000
    expect(section(body).unused_draft_zoning_floor_area_sq_ft).toBe(5000);
    renderCompare(body, false);
    await screen.findByTestId("scenario-result");
    expect(screen.queryByText("5,000")).toBeNull();
    expect(screen.queryByText("Draft cap minus recorded building area:")).toBeNull();
    // The allowance still shows (plan §3 step 4).
    expect(screen.getByTestId("scenario-cap-value").textContent).toBe("15,000");
  });

  it("hides a legacy over-built remainder and its statement", async () => {
    const body = overBuiltUnusedFloorAreaBody(); // cap 15,000 − recorded 20,000
    renderCompare(body);
    await screen.findByTestId("scenario-result");
    expect(screen.queryByText("-5,000")).toBeNull();
    expect(screen.queryByText(section(body).over_built_statement as string)).toBeNull();
    expect(screen.getByTestId("scenario-cap-value").textContent).toBe("15,000");
  });
});

describe("Compare screen — flag ON: the server's not-available state", () => {
  it("replaces the misleading gloss with the owner's two lines, keeps the document's own label and scope note", async () => {
    const body = notAvailableUnusedFloorAreaBody();
    renderCompare(body, true);
    await screen.findByTestId("scenario-result");

    const block = screen.getByTestId("scenario-unused-floor-area");
    expect(block).toHaveAttribute("data-state", "not_computable");
    expectOneNotAvailableLine();
    expect(block).toContainElement(screen.getByTestId("unused-floor-area-not-available"));
    expect(block).toContainElement(screen.getByTestId("unused-floor-area-not-available-reason"));

    // The gloss for missing_existing_building_area would be false here: a
    // recorded building area exists (carried for reference only).
    expect(screen.queryByTestId("scenario-unused-floor-area-reason")).toBeNull();
    expect(screen.queryByTestId("scenario-unused-floor-area-no-estimate")).toBeNull();
    expect(screen.queryByText(new RegExp(MISLEADING_GLOSS))).toBeNull();

    // No number: nothing subtracted, and the recorded area is not shown as one.
    expect(screen.queryByTestId("scenario-unused-floor-area-value")).toBeNull();
    expect(block).not.toHaveTextContent("12,000");

    // The document's own words, verbatim.
    expect(screen.getByTestId("scenario-unused-floor-area-label").textContent).toBe(section(body).label);
    expect(screen.getByTestId("scenario-unused-floor-area-scope-note").textContent).toBe(section(body).scope_note);
    expect(screen.getByTestId("scenario-cap-value").textContent).toBe("15,000");
  });

  it("shows the same line when no recorded building area is on file", async () => {
    renderCompare(notAvailableUnusedFloorAreaBody(null), true);
    await screen.findByTestId("scenario-result");
    expectOneNotAvailableLine();
    expect(screen.queryByText(new RegExp(MISLEADING_GLOSS))).toBeNull();
  });

  it("contrast: without the basis record the legacy typed-reason gloss still renders", async () => {
    const body = notAvailableUnusedFloorAreaBody();
    const unused = section(body);
    unused.assumptions = (unused.assumptions as Array<Record<string, unknown>>).filter(
      (assumption) => assumption.key !== UNUSED_FLOOR_AREA_NOT_AVAILABLE_KEY,
    );
    renderCompare(body, true);
    await screen.findByTestId("scenario-result");
    expect(screen.queryByTestId("unused-floor-area-not-available")).toBeNull();
    expect(screen.queryByTestId("unused-floor-area-not-available-reason")).toBeNull();
    expect(screen.getByTestId("scenario-unused-floor-area-reason")).toHaveTextContent(MISLEADING_GLOSS);
  });

  it("the basis record wins over a contradictory computed state: no number is shown beside it", async () => {
    const body = computedUnusedFloorAreaBody();
    const unused = section(body);
    const basis = (section(notAvailableUnusedFloorAreaBody()).assumptions as unknown[])[0];
    unused.assumptions = [...(unused.assumptions as unknown[]), basis];
    renderCompare(body, true);
    await screen.findByTestId("scenario-result");
    expect(screen.queryByTestId("scenario-unused-floor-area-value")).toBeNull();
    expect(screen.queryByText("5,000")).toBeNull();
    expectOneNotAvailableLine();
  });
});

/** The development-limits suite's pairing: the fixture scenario and the draft
 * evaluation for the same BBL support the 15,000 cap. */
function workspaceInputs(body: Record<string, unknown>) {
  const bbl = baseProfile().identity.bbl;
  const evaluation = draftApplicableDoc();
  evaluation.evaluated_input.bbl = bbl;
  return { bbl, evaluation, scenario: asScenario(body, bbl) };
}

describe("Architect Scenarios view (ScenarioWorkspace)", () => {
  it("flag off, supported cap: the owner's two lines, no section, the audit record stays complete", () => {
    const { bbl, evaluation, scenario } = workspaceInputs(computedUnusedFloorAreaBody());
    expect(scenarioCap(scenario, evaluation, bbl)).toBe(15000);
    render(<ScenarioWorkspace document={scenario} evaluation={evaluation} bbl={bbl}/>);
    expect(screen.queryByTestId("scenario-unused-floor-area")).toBeNull();
    expect(screen.queryByText("5,000")).toBeNull();
    expectOneNotAvailableLine();
    const raw = screen.getByText("Complete scenario record").closest("details")!.querySelector("pre")!;
    expect(JSON.parse(raw.textContent!)).toEqual(scenario);
  });

  it("flag off, unconfirmed association: the lines sit with the returned figures", () => {
    const { bbl, scenario } = workspaceInputs(notAvailableUnusedFloorAreaBody());
    render(<ScenarioWorkspace document={scenario} evaluation={null} bbl={bbl} unusedFloorAreaSectionEnabled={false}/>);
    const disclosure = screen.getByText("Returned scenario figures · association not confirmed").closest("details")!;
    expect(disclosure).toContainElement(screen.getByTestId("unused-floor-area-not-available"));
    expect(disclosure).toContainElement(screen.getByTestId("unused-floor-area-not-available-reason"));
    expect(screen.queryByTestId("scenario-unused-floor-area")).toBeNull();
    expectOneNotAvailableLine();
  });

  it("flag on: the kept section renders with the owner's two lines for the A-03 state", () => {
    const { bbl, evaluation, scenario } = workspaceInputs(notAvailableUnusedFloorAreaBody());
    render(<ScenarioWorkspace document={scenario} evaluation={evaluation} bbl={bbl} unusedFloorAreaSectionEnabled/>);
    const block = screen.getByTestId("scenario-unused-floor-area");
    expect(block).toContainElement(screen.getByTestId("unused-floor-area-not-available"));
    expect(screen.queryByTestId("scenario-unused-floor-area-set-aside")).toBeNull();
    expect(screen.queryByText(new RegExp(MISLEADING_GLOSS))).toBeNull();
  });
});

describe("Calculation evidence (evidence view and report)", () => {
  it("flag off: no remainder scope note, formula or section record; the owner's two lines; assumptions and the complete record stay", () => {
    const body = computedUnusedFloorAreaBody();
    const scenario = asScenario(body);
    render(<CalculationEvidence evaluation={null} scenario={scenario}/>);
    expect(screen.getByRole("heading", { name: "Scenario assumptions" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Scenario assumptions and area remainder" })).toBeNull();
    // The two lines carry their own row label; the old "Unused floor area on the lot" heading is gone.
    expect(screen.queryByRole("heading", { name: "Unused floor area on the lot" })).toBeNull();
    expectOneNotAvailableLine();
    expect(screen.queryByText(section(body).formula as string)).toBeNull();
    expect(screen.queryByText(section(body).scope_note as string)).toBeNull();
    expect(screen.queryByText("Remainder inputs, result and provenance")).toBeNull();
    expect(screen.getByText("All scenario assumptions")).toBeInTheDocument();
    const raw = screen.getByText("Complete scenario record").closest("details")!.querySelector("pre")!;
    expect(JSON.parse(raw.textContent!)).toEqual(scenario);
  });

  it("flag on, A-03 state: the formula slot shows the owner's two lines, the section record stays inspectable", () => {
    const body = notAvailableUnusedFloorAreaBody();
    render(<CalculationEvidence evaluation={null} scenario={asScenario(body)} unusedFloorAreaSectionEnabled/>);
    expect(screen.getByRole("heading", { name: "Scenario assumptions and area remainder" })).toBeInTheDocument();
    expect(screen.getByText(section(body).scope_note as string)).toBeInTheDocument();
    // The two lines stand in the formula's place; no formula paragraph is drawn.
    expect(document.querySelector<HTMLElement>(".architect-formula")).toBeNull();
    expectOneNotAvailableLine();
    expect(screen.queryByText("No supported remainder formula")).toBeNull();
    expect(screen.getByText("Remainder inputs, result and provenance")).toBeInTheDocument();
  });

  it("flag on, legacy missing record: unchanged wording", () => {
    render(<CalculationEvidence evaluation={null} scenario={asScenario(preliminaryScenarioBody())} unusedFloorAreaSectionEnabled/>);
    expect(document.querySelector<HTMLElement>(".architect-formula")!.textContent).toBe("No supported remainder formula");
    expect(screen.queryByTestId("unused-floor-area-not-available")).toBeNull();
    expect(screen.queryByTestId("unused-floor-area-not-available-reason")).toBeNull();
  });
});
