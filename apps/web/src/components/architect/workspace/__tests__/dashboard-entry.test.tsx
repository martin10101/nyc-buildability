import { useState } from "react";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import scenarioFixture from "../../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";
import { DashboardEntry } from "../DashboardEntry";

const state = vi.hoisted(() => ({ params: new URLSearchParams(), profile: null as PropertyProfile | null, scenario: null as Scenario | null, evaluation: null as RuleEvaluation | null, replace: vi.fn() }));
vi.mock("next/navigation", () => ({ useSearchParams: () => state.params, useRouter: () => ({ replace: state.replace }) }));
vi.mock("@/lib/architect/use-property", () => ({ useProperty: () => ({ loading: false, outcome: state.profile ? { kind: "profile", profile: state.profile } : null, retry: vi.fn() }) }));
vi.mock("@/lib/architect/use-analysis", () => ({ useAnalysis: () => ({ scenario: state.scenario ? { kind: "scenario", document: state.scenario } : null, evaluation: state.evaluation ? { kind: "evaluation", document: state.evaluation } : null, retryScenario: vi.fn(), retryEvaluation: vi.fn() }) }));
vi.mock("@/lib/condo-records", async original => ({ ...await original<typeof import("@/lib/condo-records")>(), useCondoRecords: () => ({ kind: "route_absent", httpStatus: 404 }) }));
vi.mock("../DashboardMap", () => ({ DashboardMap: ({ bbl }: { bbl: string }) => <div>Real-map consumer for {bbl}</div> }));
vi.mock("@/components/address/AddressResolutionScreen", () => ({ AddressResolutionScreen: ({ onConfirmLot }: { onConfirmLot: (bbl: string) => void }) => <div><label>Street address<input id="architect-address"/></label><button onClick={() => onConfirmLot("1000010100")}>Confirm another lot</button></div> }));
vi.mock("../DashboardTools", () => ({ DashboardTools: ({ tool }: { tool: string }) => <ToolEditor tool={tool}/> }));
function ToolEditor({ tool }: { tool: string }) {
  const [value, setValue] = useState("");
  return <><label>Draft for {tool}<input value={value} onChange={event => setValue(event.target.value)}/></label><a href={`/property?ruleeval=on&bbl=${state.profile?.identity.bbl}&view=evidence`}>Inspect supporting evidence</a></>;
}
beforeEach(() => {
  vi.clearAllMocks(); sessionStorage.clear();
  state.profile = baseProfile();
  state.params = new URLSearchParams(`bbl=${state.profile.identity.bbl}`);
  state.scenario = structuredClone(scenarioFixture) as Scenario;
  state.evaluation = draftApplicableDoc();
  state.scenario.evaluated_input.bbl = state.profile.identity.bbl;
  state.evaluation.evaluated_input.bbl = state.profile.identity.bbl;
});
afterEach(cleanup);

describe("connected dashboard composition", () => {
  it("keeps search mounted, opens tools without routing, and preserves proposal edits on close", async () => {
    render(<DashboardEntry/>);
    const input = screen.getByLabelText("Street address");
    fireEvent.change(input, { target: { value: "an address being typed" } });
    const action = screen.getByRole("button", { name: /Draw a proposal/ });
    action.focus(); fireEvent.click(action);
    const panel = screen.getByRole("dialog", { name: "Proposal editor" });
    fireEvent.change(within(panel).getByLabelText("Draft for proposal"), { target: { value: "Keep this design" } });
    fireEvent.click(within(panel).getByRole("button", { name: "Close Proposal editor window" }));
    fireEvent.click(action);
    expect(screen.getByLabelText("Draft for proposal")).toHaveValue("Keep this design");
    expect(screen.getByLabelText("Street address")).toBe(input);
    expect(input).toHaveValue("an address being typed");
    expect(state.replace).not.toHaveBeenCalled();
    fireEvent.click(within(panel).getByRole("link", { name: "Inspect supporting evidence" }));
    await waitFor(() => expect(screen.getByRole("dialog", { name: "Evidence & sources" })).toBeVisible());
    expect(state.replace).not.toHaveBeenCalled();
  });
  it("updates only the dashboard URL after explicit confirmation and resets drafts on a different property", () => {
    const view = render(<DashboardEntry/>);
    const input = screen.getByLabelText("Street address");
    fireEvent.click(screen.getByRole("button", { name: /Draw a proposal/ }));
    fireEvent.change(screen.getByLabelText("Draft for proposal"), { target: { value: "Old property draft" } });
    fireEvent.click(screen.getByRole("button", { name: "Confirm another lot" }));
    expect(state.replace).toHaveBeenCalledWith("/property/workspace?ruleeval=on&bbl=1000010100", { scroll: false });
    state.params.set("bbl", "1000010100");
    state.profile = { ...baseProfile(), identity: { ...baseProfile().identity, bbl: "1000010100" } };
    state.scenario = null; state.evaluation = null;
    view.rerender(<DashboardEntry/>);
    expect(screen.getByLabelText("Street address")).toBe(input);
    fireEvent.click(screen.getByRole("button", { name: /Draw a proposal/ }));
    expect(screen.getByLabelText("Draft for proposal")).toHaveValue("");
  });
  it("withholds a wrong-property profile before analysis or map panels mount", () => {
    state.params.set("bbl", "1000010100");
    render(<DashboardEntry/>);
    expect(screen.getByRole("heading", { name: "Property identity mismatch" })).toBeVisible();
    expect(screen.queryByTestId("connected-dashboard")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Street address")).toBeVisible();
  });
  it("withholds both numerical summaries on foreign analysis identity and retains original evidence", () => {
    state.scenario!.evaluated_input.bbl = "1000019999";
    render(<DashboardEntry/>);
    expect(screen.getByTestId("dashboard-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("dashboard-evaluated-far")).toHaveTextContent("Not calculated");
    const record = screen.getByText("Returned scenario record").closest("details")!;
    expect(JSON.parse(record.querySelector("pre")!.textContent!)).toEqual(state.scenario);
  });
  it("opens a supported deep-linked tool while keeping the property dashboard in place", () => {
    state.params.set("tool", "envelope");
    render(<DashboardEntry/>);
    expect(screen.getByRole("dialog", { name: "Proposal editor" })).toBeVisible();
    expect(screen.getByTestId("buildability-dashboard")).toBeVisible();
    expect(screen.getByLabelText("Street address")).toBeVisible();
  });
});
