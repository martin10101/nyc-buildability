import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Scenario } from "@/lib/scenario-contract";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import { deriveCondoSurface } from "../../CondoRecordsSection";
import { DashboardTools, type DashboardToolsProps } from "../DashboardTools";
import scenarioFixture from "../../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

vi.mock("@/lib/condo-records", async original => ({
  ...await original<typeof import("@/lib/condo-records")>(),
  useCondoRecords: () => ({ kind: "route_absent", httpStatus: 404 }),
}));

afterEach(cleanup);

function inputs(tool: "evidence" | "report"): DashboardToolsProps {
  const profile = baseProfile();
  const returnedScenario = structuredClone(scenarioFixture) as Scenario;
  const returnedEvaluation = draftApplicableDoc();
  returnedScenario.evaluated_input.bbl = profile.identity.bbl;
  returnedEvaluation.evaluated_input.bbl = profile.identity.bbl;
  return {
    tool, profile, returnedScenario, returnedEvaluation,
    // These are the adapter's withheld calculation inputs. Originals must stay
    // inspectable even when neither document reaches a calculated result view.
    scenario: null, evaluation: null,
    condo: deriveCondoSurface(profile, { kind: "route_absent", httpStatus: 404 }),
    address: null, label: "Test property", selection: "calculation",
    onSelectEvidence: vi.fn(), onInspect: vi.fn(), onOpen: vi.fn(), surveyEnabled: false,
  };
}

function inspectBothOriginals(props: DashboardToolsProps) {
  const section = screen.getByRole("region", { name: "Withheld analysis records" });
  expect(section).toHaveTextContent("These figures are not development allowances for this property.");
  const originals = [
    ["Original rule-evaluation record · allowances withheld", props.returnedEvaluation],
    ["Original scenario record · allowances withheld", props.returnedScenario],
  ] as const;
  for (const [label, original] of originals) {
    const summary = within(section).getByText(label, { exact: true });
    const disclosure = summary.closest("details")!;
    expect(disclosure).not.toBeNull();
    expect(disclosure).not.toHaveAttribute("open");
    fireEvent.click(summary);
    expect(disclosure).toHaveAttribute("open");
    expect(JSON.parse(disclosure.querySelector("pre")!.textContent!)).toEqual(original);
  }
  if (props.tool === "report") {
    expect(section.closest(".architect-report")).not.toBeNull();
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  }
  return section;
}

for (const tool of ["evidence", "report"] as const) {
  describe(`${tool}: withheld originals remain reachable`, () => {
    for (const kind of ["scenario", "evaluation"] as const) {
      it.each([["foreign", "1000019999"], ["missing", null]] as const)(
        `preserves BOTH originals when the ${kind} has a %s BBL`, (_label, invalidBbl) => {
          const props = inputs(tool);
          const document = kind === "scenario" ? props.returnedScenario! : props.returnedEvaluation!;
          Object.assign(document.evaluated_input, { bbl: invalidBbl });
          render(<DashboardTools {...props}/>);
          const section = inspectBothOriginals(props);
          expect(section).toHaveTextContent("At least one analysis record does not identify the selected property.");
          expect(section).not.toHaveTextContent("The legal analysis site is unresolved.");
        },
      );
    }

    it("preserves BOTH matching originals when the condo decision withholds allowances", () => {
      const props = inputs(tool);
      props.condo = { ...props.condo, withholdAllowances: true };
      render(<DashboardTools {...props}/>);
      const section = inspectBothOriginals(props);
      expect(section).toHaveTextContent("The legal analysis site is unresolved.");
      expect(section).not.toHaveTextContent("At least one analysis record does not identify the selected property.");
    });

    it("does not label matching, unwithheld originals as withheld", () => {
      const props = inputs(tool);
      render(<DashboardTools {...props}/>);
      expect(screen.queryByRole("region", { name: "Withheld analysis records" })).toBeNull();
    });
  });
}
