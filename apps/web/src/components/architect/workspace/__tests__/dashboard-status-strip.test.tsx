import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import type { Scenario } from "@/lib/scenario-contract";
import { deriveCondoSurface } from "../../CondoRecordsSection";
import { DashboardPanels, type DashboardPanelsProps } from "../DashboardPanels";
import { FLOOR_AREA_REMINDER, STRIP_LIMIT, calculationReason, dashboardStatus } from "../dashboard-status";
import scenarioFixture from "../../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

afterEach(cleanup);

// Plan §5a item 2, copied word for word so any drift in the app's wording fails here.
const PLAN_FLOOR_AREA_REMINDER = "Make sure this floor area is available for use. Confirm with the owner or developer that none of it was sold or merged with another lot.";

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
    map: <div>Map bound to {profile.identity.bbl}</div>,
    onInspect: vi.fn(), onOpen: vi.fn(),
  };
}

describe("plan §5a on the single-page dashboard (D-03)", () => {
  it("shows one strip of at most three items and keeps the standing notices behind it until tapped", () => {
    render(<DashboardPanels {...inputs()}/>);
    expect(screen.getAllByRole("region", { name: "Results status" })).toHaveLength(1);
    expect(screen.getAllByTestId("dashboard-status-item").map(item => item.textContent))
      .toEqual(["Draft zoning maximum", "City-record measurements", "Lot you entered"]);
    const details = screen.getByTestId("dashboard-status-details");
    const strip = screen.getByTestId("dashboard-status-strip");
    expect(details).not.toBeVisible();
    expect(strip).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(strip);
    expect(strip).toHaveAttribute("aria-expanded", "true");
    expect(details).toBeVisible();
    expect(within(screen.getByTestId("dashboard-standing-notices")).getAllByRole("listitem").map(item => item.textContent)).toEqual([
      "This is not a Buildings Department approval.",
      PLAN_FLOOR_AREA_REMINDER,
      "Based on the lot you entered — the app does not verify the zoning lot.",
      "The rules for this zoning district are not complete in the app yet, so some limits are not calculated.",
    ]);
    expect(FLOOR_AREA_REMINDER).toBe(PLAN_FLOOR_AREA_REMINDER);
    // Once, behind the strip; never repeated beside a number.
    expect(screen.getAllByText(PLAN_FLOOR_AREA_REMINDER)).toHaveLength(1);
    expect(screen.getAllByText(/not a Buildings Department approval/)).toHaveLength(1);
    expect(within(details).getByText("These numbers come from draft rules that a qualified reviewer has not approved yet.")).toBeVisible();
    fireEvent.click(strip);
    expect(details).not.toBeVisible();
  });

  it("puts only an exception that changes how to read a value beside it, at most one per row", () => {
    const props = inputs();
    props.profile.lot_facts.lotdepth.coverage_status = "professional_review_required";
    const { container } = render(<DashboardPanels {...props}/>);
    const depth = screen.getByRole("rowheader", { name: "Lot depth" }).closest("tr")!;
    expect(within(depth).getByText("Needs review")).toBeInTheDocument();
    expect(container.querySelectorAll<HTMLElement>(".bd-exception")).toHaveLength(1);
    for (const row of Array.from(container.querySelectorAll<HTMLElement>("tr"))) {
      expect(row.querySelectorAll(".bd-exception").length).toBeLessThanOrEqual(1);
    }
    // The former caution chips and source labels beside numbers are gone.
    for (const label of ["Conditional", "DRAFT", "Draft rule", "Why?", "Source record", "City record", "Not labeled"]) {
      expect(screen.queryByText(label)).not.toBeInTheDocument();
    }
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent(/^15,000 sq ft$/);
  });

  it("replaces a withheld number with 'Not available — <reason>' and shows no digits", () => {
    const props = inputs();
    props.condo = { ...props.condo, withholdAllowances: true };
    render(<DashboardPanels {...props}/>);
    for (const id of ["dashboard-cap", "dashboard-evaluated-far"]) {
      const cell = screen.getByTestId(id);
      expect(cell.textContent).toMatch(/^Not available — \S/);
      expect(cell.textContent).not.toMatch(/\d/);
    }
    for (const title of ["Height", "Setbacks and yards", "Lot coverage and open space"]) {
      expect(screen.getByRole("rowheader", { name: title }).closest("tr")!.querySelector("td")).toHaveTextContent(/^Not available — /);
    }
  });

  it("shows up to three notices on screen and groups more under one Notes (N) item", () => {
    const props = inputs();
    // The fixture's 24 non-critical, feasibility-irrelevant missing inputs are not notices.
    const view = render(<DashboardPanels {...props}/>);
    expect(screen.queryByRole("list", { name: "Needs attention" })).not.toBeInTheDocument();
    props.profile.missing_inputs = [{ field: "lotarea", criticality: "critical" }];
    view.rerender(<DashboardPanels {...props}/>);
    const onScreen = within(screen.getByRole("list", { name: "Needs attention" }));
    expect(onScreen.getAllByRole("listitem")).toHaveLength(1);
    expect(onScreen.getByRole("button", { name: /1 missing input \(1 critical\)/ })).toBeInTheDocument();
    expect(screen.queryByText(/^Notes \(/)).not.toBeInTheDocument();

    props.condo = { ...props.condo, withholdAllowances: true, conflict: true };
    props.profile.reproducibility!.staleness = { served_from_cache: true, stale: true };
    view.rerender(<DashboardPanels {...props}/>);
    const grouped = within(screen.getByRole("list", { name: "Needs attention" }));
    expect(grouped.getAllByRole("listitem")).toHaveLength(1);
    expect(screen.queryByRole("button", { name: /missing input/ })).not.toBeInTheDocument();
    fireEvent.click(grouped.getByRole("button", { name: "Notes (4)" }));
    expect(screen.getByTestId("dashboard-status-details")).toBeVisible();
    for (const text of ["Site definition needs review", "Condo records disagree", "1 missing input (1 critical)", "Property records out of date"]) {
      expect(screen.getByRole("button", { name: new RegExp(text.replace(/[()]/g, "\\$&")) })).toBeVisible();
    }
    fireEvent.click(screen.getByRole("button", { name: /Property records out of date/ }));
    expect(props.onOpen).toHaveBeenCalledWith("evidence");
  });

  it("uses plain English with no internal codes, including behind the strip", () => {
    const { container } = render(<DashboardPanels {...inputs()}/>);
    fireEvent.click(screen.getByTestId("dashboard-status-strip"));
    const text = container.textContent ?? "";
    expect(text).not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
    for (const code of ["Lot type code", "PLUTO", "lottype", "conditional"]) expect(text).not.toContain(code);
    expect(screen.getByText("City-recorded building area (not zoning floor area)")).toBeInTheDocument();
    for (const status of ["Draft assessment · envelope incomplete", "Analysis records differ · inspect evidence",
      "Rule details incomplete · inspect captured evidence", "Zoning boundary check unavailable", "Property identity mismatch"]) {
      expect(calculationReason(status)).not.toMatch(/·|inspect|_|^[A-Z]/);
    }
  });

  it("never builds more than three strip items", () => {
    for (const withheld of [false, true]) for (const calculated of [false, true]) for (const multiLot of [false, true]) {
      expect(dashboardStatus({ withheld, calculated, multiLot, baseLots: 5 }).items.length).toBeLessThanOrEqual(STRIP_LIMIT);
    }
  });
});
