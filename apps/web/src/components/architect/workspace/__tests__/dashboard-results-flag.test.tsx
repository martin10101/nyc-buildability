import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import { deriveCondoSurface } from "../../CondoRecordsSection";
import { DashboardTools, type DashboardToolsProps } from "../DashboardTools";

/**
 * S20 [WIRING] (task M5-T140, rulings R1/R9): with the website switch off or absent (the default),
 * the dashboard's Results tool — including a `?tool=results` deep link — renders the plain
 * not-available view and makes NO network call. With the switch on, the tool shows the form and
 * still makes no call until the user presses the button (ruling R2). By the pattern of
 * dashboard-proposal-flag.test.tsx.
 */

vi.mock("@/lib/condo-records", async original => ({
  ...(await original<typeof import("@/lib/condo-records")>()),
  useCondoRecords: () => ({ kind: "route_absent", httpStatus: 404 }),
}));
vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));

let fetchSpy: ReturnType<typeof vi.fn>;
beforeEach(() => {
  fetchSpy = vi.fn(async () => new Response("{}", { status: 404 }));
  vi.stubGlobal("fetch", fetchSpy);
});
afterEach(() => vi.unstubAllGlobals());
afterEach(cleanup);

function props(resultsUiEnabled?: boolean): DashboardToolsProps {
  const profile = baseProfile();
  return {
    tool: "results",
    profile,
    scenario: null,
    evaluation: null,
    returnedScenario: null,
    returnedEvaluation: null,
    condo: deriveCondoSurface(profile, { kind: "route_absent", httpStatus: 404 }),
    address: null,
    label: "Test property",
    selection: "calculation",
    onSelectEvidence: vi.fn(),
    onInspect: vi.fn(),
    onOpen: vi.fn(),
    surveyEnabled: false,
    resultsUiEnabled,
  };
}

describe("dashboard results tool is behind a default-off website switch", () => {
  for (const flag of [undefined, false] as const) {
    it(`renders the plain not-available view and makes no call when the switch is ${String(flag)}`, () => {
      render(<DashboardTools {...props(flag)} />);
      expect(
        screen.getByRole("heading", { name: "Results is not available in this version" }),
      ).toBeInTheDocument();
      expect(screen.queryByTestId("results-panel")).not.toBeInTheDocument();
      expect(screen.queryByTestId("results-form")).not.toBeInTheDocument();
      expect(fetchSpy).not.toHaveBeenCalled();
    });
  }

  it("shows the form (and no result, no call) when the switch is on", () => {
    render(<DashboardTools {...props(true)} />);
    expect(screen.getByTestId("results-panel")).toBeInTheDocument();
    expect(screen.getByTestId("results-form")).toBeInTheDocument();
    expect(screen.getByTestId("results-show")).toBeInTheDocument();
    expect(screen.queryByTestId("results-document")).toBeNull();
    // Ruling R2: no request is made on open.
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
