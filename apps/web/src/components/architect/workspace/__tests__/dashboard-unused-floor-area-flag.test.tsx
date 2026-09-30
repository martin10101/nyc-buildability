import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Scenario } from "@/lib/scenario-contract";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import { deriveCondoSurface } from "../../CondoRecordsSection";
import { DashboardTools, type DashboardToolsProps } from "../DashboardTools";
import scenarioFixture from "../../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

/**
 * D-06 (plan §3 step 4, M2-07; set-aside item #6): the dashboard's Scenarios,
 * Evidence and Report tools pass the server-read
 * INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED down. Off (the default): one
 * "Not available — needs existing zoning floor area" line, no section and no
 * remainder record. On: the kept section and remainder record render.
 */

vi.mock("@/lib/condo-records", async original => ({
  ...await original<typeof import("@/lib/condo-records")>(),
  useCondoRecords: () => ({ kind: "route_absent", httpStatus: 404 }),
}));
vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
afterEach(cleanup);

const NOT_AVAILABLE = "Not available — needs existing zoning floor area";
const TOOLS = ["scenarios", "evidence", "report"] as const;

function props(tool: (typeof TOOLS)[number], unusedFloorAreaSectionEnabled?: boolean): DashboardToolsProps {
  const profile = baseProfile();
  const scenario = structuredClone(scenarioFixture) as Scenario;
  const evaluation = draftApplicableDoc();
  scenario.evaluated_input.bbl = profile.identity.bbl;
  evaluation.evaluated_input.bbl = profile.identity.bbl;
  return {
    tool, profile, scenario, evaluation, returnedScenario: scenario, returnedEvaluation: evaluation,
    condo: deriveCondoSurface(profile, { kind: "route_absent", httpStatus: 404 }),
    address: null, label: "Test property", selection: "calculation",
    onSelectEvidence: vi.fn(), onInspect: vi.fn(), onOpen: vi.fn(), surveyEnabled: false,
    unusedFloorAreaSectionEnabled,
  };
}

describe("dashboard unused-floor-area section is set aside behind a default-off server flag", () => {
  for (const tool of TOOLS) {
    for (const flag of [undefined, false] as const) {
      it(`tool=${tool}, flag ${String(flag)}: one not-available line, no section, no remainder record`, () => {
        render(<DashboardTools {...props(tool, flag)}/>);
        expect(screen.getAllByTestId("unused-floor-area-not-available").map(line => line.textContent)).toEqual([NOT_AVAILABLE]);
        expect(screen.queryByTestId("scenario-unused-floor-area")).toBeNull();
        expect(screen.queryByText("Remainder inputs, result and provenance")).toBeNull();
      });
    }

    it(`tool=${tool}, flag on: the kept section and remainder record render`, () => {
      render(<DashboardTools {...props(tool, true)}/>);
      expect(screen.queryByTestId("unused-floor-area-not-available")).toBeNull();
      if (tool === "scenarios") expect(screen.getByTestId("scenario-unused-floor-area")).toBeInTheDocument();
      else expect(screen.getByText("Remainder inputs, result and provenance")).toBeInTheDocument();
    });
  }
});
