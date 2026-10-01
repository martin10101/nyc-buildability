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
    // Plan §5a item 3: the supported cap is the headline number alone, with no caution chip.
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent(/^15,000 sq ft$/);
    expect(screen.queryByText(/Conditional/)).not.toBeInTheDocument();
    expect(screen.getByTestId("bbL-bound-map")).toHaveTextContent(props.profile.identity.bbl);
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("withholds BOTH calculated summaries when the condo decision withholds", () => {
    const props = inputs();
    props.condo = { ...props.condo, withholdAllowances: true };
    render(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("Not available — the site needs review first");
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not available — the site needs review first");
    expect(screen.getAllByTestId("dashboard-status-item")[0]).toHaveTextContent("Results withheld");
    // FAR, cap and the three dimensional rows.
    expect(screen.getAllByText("Not available — the site needs review first")).toHaveLength(5);
    expect(screen.queryByText("15,000 sq ft")).not.toBeInTheDocument();
  });

  it("does not promote a mismatched scenario or unsupported source citations", () => {
    const props = inputs();
    props.scenario!.evaluated_input.bbl = "1000019999";
    const view = render(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("Not available — the rule and scenario records do not match");
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not available — the rule and scenario records do not match");
    props.scenario!.evaluated_input.bbl = props.profile.identity.bbl;
    props.evaluation!.evaluations[0].citations = [];
    view.rerender(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("Not available — the rule sources are incomplete");
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not available — the rule sources are incomplete");
  });

  it("keeps a conflicting source FAR visible as a conflict instead of selecting a number", () => {
    const props = inputs();
    const reference = props.profile.provenance.find(record => record.original_field_name === "residfar")!;
    props.profile.provenance.push({ ...reference, provenance_id: `${reference.provenance_id}-duplicate`, normalized_value: 12 });
    render(<DashboardPanels {...props}/>);
    expect(screen.getByTestId("dashboard-reference-far")).toHaveTextContent("Not available — city records disagree");
    fireEvent.click(screen.getByRole("button", { name: /City-listed residential FAR/ }));
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
    render(<DashboardPanels {...props} proposalEditorEnabled/>);
    const actions = within(screen.getByRole("region", { name: "Quick actions" }));
    fireEvent.click(actions.getByRole("button", { name: /Report preview/ }));
    fireEvent.click(actions.getByRole("button", { name: /Draw a proposal/ }));
    fireEvent.click(screen.getByRole("button", { name: /1 missing input \(1 critical\)/ }));
    expect(props.onOpen).toHaveBeenNthCalledWith(1, "report");
    expect(props.onOpen).toHaveBeenNthCalledWith(2, "proposal");
    expect(props.onOpen).toHaveBeenNthCalledWith(3, "issues");
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });

  it("hides the set-aside proposal and envelope entries unless the server flag is on (D-01, plan §7)", () => {
    const props = inputs();
    const view = render(<DashboardPanels {...props}/>);
    expect(screen.queryByRole("button", { name: /Draw a proposal/ })).not.toBeInTheDocument();
    expect(within(screen.getByRole("group", { name: "Development details" })).queryByRole("button", { name: "Envelope" })).not.toBeInTheDocument();
    // The envelope rows still say plainly that they are not available; nothing else changes.
    expect(screen.getByRole("rowheader", { name: "Height" }).closest("tr")).toHaveTextContent("Not available — not calculated yet");
    expect(within(screen.getByRole("group", { name: "Development details" })).getByRole("button", { name: "Units" })).toBeInTheDocument();
    view.rerender(<DashboardPanels {...props} proposalEditorEnabled/>);
    expect(screen.getByRole("button", { name: /Draw a proposal/ })).toBeInTheDocument();
    fireEvent.click(within(screen.getByRole("group", { name: "Development details" })).getByRole("button", { name: "Envelope" }));
    expect(props.onOpen).toHaveBeenCalledTimes(1);
    expect(props.onOpen).toHaveBeenCalledWith("envelope");
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
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not available — the site needs review first");
    expect(screen.getAllByTestId("dashboard-status-item")[2]).toHaveTextContent(`${count} lots on record`);
  });
});

describe("owner directive 2026-10-01: tax-lot-only warning and labels on the dashboard results", () => {
  // Word for word, so any drift in the app's wording fails here.
  const WARNING = "These numbers cover only the tax lot you entered. The full zoning lot may include other lots. The whole-site limit, the room left after existing buildings, and the combined lot's rear yard and coverage are not calculated yet.";
  const ZONING_LOT_ROWS = ["Whole-site capacity", "Remaining development capacity", "Combined zoning lot: coverage", "Combined zoning lot: rear yard"];

  function expectZoningLotRows(summary: HTMLElement) {
    for (const label of ZONING_LOT_ROWS) {
      const cell = within(summary).getByRole("rowheader", { name: label }).closest("tr")!.querySelector<HTMLElement>("td")!;
      expect(cell.textContent).toBe("Not confirmed");
      expect(cell).toBeVisible();
    }
  }

  it("shows the warning on the results before any tap and labels the cap and the zoning-lot rows", () => {
    render(<DashboardPanels {...inputs()}/>);
    const summary = screen.getByRole("region", { name: "Development limits summary" });
    // Nothing is tapped: the strip is closed, and the warning is still on screen with the numbers.
    expect(screen.getByTestId("dashboard-status-strip")).toHaveAttribute("aria-expanded", "false");
    const warning = within(summary).getByTestId("tax-lot-only-warning");
    expect(warning).toBeVisible();
    expect(warning).toHaveAttribute("role", "note");
    expect(warning.textContent).toBe(WARNING);
    expect(screen.getByTestId("dashboard-status-details")).not.toContainElement(warning);
    // The label sits on the value as a plain line under the number: the number itself is unchanged
    // and the label is not an exception chip.
    const cap = screen.getByTestId("dashboard-cap");
    expect(cap).toHaveTextContent(/^15,000 sq ft$/);
    const label = screen.getByTestId("dashboard-cap-scope");
    expect(label.textContent).toBe("Tax-lot-only estimate");
    expect(label).toBeVisible();
    expect(label.closest(".bd-headline")).toContainElement(cap);
    expect(label).not.toHaveClass("bd-exception");
    expectZoningLotRows(summary);
  });

  it("keeps the warning and the 'Not confirmed' rows when the cap is withheld, without a cap label", () => {
    const props = inputs();
    props.condo = { ...props.condo, withholdAllowances: true };
    render(<DashboardPanels {...props}/>);
    const summary = screen.getByRole("region", { name: "Development limits summary" });
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not available — the site needs review first");
    expect(screen.queryByTestId("dashboard-cap-scope")).toBeNull();
    expect(within(summary).getByTestId("tax-lot-only-warning").textContent).toBe(WARNING);
    expectZoningLotRows(summary);
  });

  it("names lots 1 and 70 and says the numbers use lot 70 only for a verified zoning lot", () => {
    // Test fixture only: a verified zoning-lot fact shaped for the 215-16 Northern benchmark.
    const props = inputs();
    props.profile.identity.bbl = "4073340070";
    render(<DashboardPanels {...props} zoningLot={{ taxLotBbls: ["4073340001", "4073340070"], calculatedBbl: "4073340070" }}/>);
    expect(screen.getByTestId("tax-lot-only-warning").textContent).toBe(
      "This zoning lot includes tax lots 1 and 70. These numbers use lot 70 only. The whole-site limit, the room left after existing buildings, and the combined lot's rear yard and coverage are not calculated yet.",
    );
  });
});
