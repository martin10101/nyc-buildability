import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import type { Scenario } from "@/lib/scenario-contract";
import type { CondoSurfaceDecision } from "../../CondoRecordsSection";
import { deriveCondoSurface } from "../../CondoRecordsSection";
import { DashboardPanels, type DashboardPanelsProps } from "../DashboardPanels";
import scenarioFixture from "../../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

afterEach(cleanup);

function inputs(): DashboardPanelsProps {
  const profile = baseProfile();
  const evaluation = draftApplicableDoc();
  const scenario = structuredClone(scenarioFixture) as Scenario;
  evaluation.evaluated_input.bbl = profile.identity.bbl;
  scenario.evaluated_input.bbl = profile.identity.bbl;
  return {
    profile, evaluation, scenario,
    condo: deriveCondoSurface(profile, { kind: "route_absent", httpStatus: 404 }),
    label: "Test property",
    map: <div data-testid="bbL-bound-map">Map bound to {profile.identity.bbl}</div>,
    onInspect: vi.fn(), onOpen: vi.fn(),
  };
}

describe("real-data dashboard summaries", () => {
  it("keeps source FAR distinct from guarded rule outputs and cap scope", () => {
    const props = inputs();
    props.profile.provenance.find(record => record.original_field_name === "residfar")!.normalized_value = 3.44;
    render(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-reference-far")).toHaveTextContent("3.44");
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("1.50");
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("15,000 sq ft");
    expect(screen.getByText("FAR only · Buildable envelope not assessed")).toBeInTheDocument();
    expect(within(screen.getByTestId("dashboard-cap").closest("tr")!).getByRole("button", { name: /Conditional/ })).toBeInTheDocument();
    expect(screen.getByTestId("bbL-bound-map")).toHaveTextContent(props.profile.identity.bbl);
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("withholds BOTH calculated summaries when the condo decision withholds", () => {
    const props = inputs();
    props.condo = { ...props.condo, withholdAllowances: true };
    render(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByText("Site definition requires review · allowances withheld")).toBeInTheDocument();
    expect(screen.getAllByText(/Withheld · site review/)).toHaveLength(3);
    expect(screen.queryByText("15,000 sq ft")).not.toBeInTheDocument();
  });

  it("does not promote a mismatched scenario or unsupported source citations", () => {
    const props = inputs();
    props.scenario!.evaluated_input.bbl = "1000019999";
    const view = render(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not calculated");
    props.scenario!.evaluated_input.bbl = props.profile.identity.bbl;
    props.evaluation!.evaluations[0].citations = [];
    view.rerender(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not calculated");
  });

  it("keeps a conflicting source FAR visible as a conflict instead of selecting a number", () => {
    const props = inputs();
    const reference = props.profile.provenance.find(record => record.original_field_name === "residfar")!;
    props.profile.provenance.push({ ...reference, provenance_id: `${reference.provenance_id}-duplicate`, normalized_value: 12 });
    render(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-reference-far")).toHaveTextContent("Conflicting records");
    fireEvent.click(screen.getByRole("button", { name: /City record/ }));
    expect(props.onOpen).toHaveBeenCalledWith("evidence");
    expect(props.onInspect).not.toHaveBeenCalled();
  });

  it("shows an absent frontage as unknown and preserves supplied zero values and source links", () => {
    const props = inputs();
    delete props.profile.lot_facts.lotfront;
    const lot = props.profile.lot_facts.lotarea;
    lot.value = 0;
    render(<DashboardPanels {...props}/>);
    const table = within(screen.getByRole("region", { name: "Recorded lot details" }));
    const areaRow = table.getByRole("rowheader", { name: "Lot area" }).closest("tr")!;
    expect(areaRow).toHaveTextContent("0");
    expect(table.getByRole("rowheader", { name: "Lot frontage" }).closest("tr")).toHaveTextContent("Unknown");
    fireEvent.click(within(areaRow).getByRole("button"));
    expect(props.onInspect).toHaveBeenCalledWith(lot.provenance_ref);
  });

  it("opens tools and issues in the caller's floating workspace", () => {
    const props = inputs();
    props.profile.missing_inputs = [{ field: "lotarea", criticality: "critical" }];
    render(<DashboardPanels {...props}/>);
    const actions = within(screen.getByRole("region", { name: "Quick actions" }));
    fireEvent.click(actions.getByRole("button", { name: /Report preview/ }));
    fireEvent.click(actions.getByRole("button", { name: /Draw a proposal/ }));
    fireEvent.click(screen.getByRole("button", { name: /1 missing input · 1 critical/ }));
    expect(props.onOpen).toHaveBeenNthCalledWith(1, "report");
    expect(props.onOpen).toHaveBeenNthCalledWith(2, "proposal");
    expect(props.onOpen).toHaveBeenNthCalledWith(3, "issues");
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });

  it.each([3, 4, 5])("shows all %i recorded base parcels without assuming exactly two", count => {
    const props = inputs();
    // Only baseLots.length/outcome are read by this summary. This seam deliberately
    // does not assert that these synthetic records can authorize a calculation.
    props.condo = {
      ...props.condo, withholdAllowances: true,
      recordsView: { outcome: "multi_lot_set", baseLots: Array.from({ length: count }, (_, index) => ({ bbl: `100001000${index}` })) },
    } as CondoSurfaceDecision;
    render(<DashboardPanels {...props}/>);
    expect(screen.getByRole("button", { name: new RegExp(`${count} base parcel records.*Review parcels`) })).toBeInTheDocument();
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not calculated");
  });
});
