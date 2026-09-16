import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fieldLabel } from "@/lib/format";
import { baseProfile } from "@/test-support/fixtures";
import { draftApplicableDoc, spatialUncertaintyDoc, unsupportedDoc } from "@/test-support/rule-evaluation-fixtures";
import { ArchitectEntry } from "../ArchitectEntry";
import type { PropertyProfile } from "@/lib/contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import type { Scenario } from "@/lib/scenario-contract";
import scenarioFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

const state = vi.hoisted(() => ({ params: new URLSearchParams(), profile: null as PropertyProfile | null, evaluation: null as RuleEvaluation | null, scenario: null as Scenario | null, push: vi.fn() }));
vi.mock("next/navigation", () => ({ useSearchParams: () => state.params, useRouter: () => ({ push: state.push }) }));
vi.mock("@/lib/architect/use-property", () => ({ useProperty: () => ({ loading: false, outcome: state.profile ? { kind: "profile", profile: state.profile } : null, retry: vi.fn() }) }));
vi.mock("@/lib/architect/use-analysis", () => ({ useAnalysis: () => ({ scenario: state.scenario ? { kind: "scenario", document: state.scenario } : null, evaluation: state.evaluation ? { kind: "evaluation", document: state.evaluation } : null, retryScenario: vi.fn(), retryEvaluation: vi.fn() }) }));
vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
beforeEach(() => { state.profile = baseProfile(); state.evaluation = null; state.scenario = null; state.params = new URLSearchParams(`bbl=${state.profile.identity.bbl}&view=facts`); sessionStorage.clear(); vi.clearAllMocks(); });

describe("V3 connected report audit", () => {
  it.each(["malformed evaluation", "evaluation mismatch", "evaluation missing BBL", "scenario mismatch", "scenario missing BBL", "both mismatched", "malformed mismatched evaluation"])("prints and restores original evidence for %s", kind => {
    state.params.set("view", "report");
    state.evaluation = draftApplicableDoc();
    state.scenario = structuredClone(scenarioFixture) as Scenario;
    state.evaluation.evaluated_input.bbl = state.profile!.identity.bbl;
    state.scenario.evaluated_input.bbl = state.profile!.identity.bbl;
    if (kind.includes("malformed")) delete (state.evaluation.evaluations[0] as unknown as Record<string, unknown>).outputs;
    if (kind === "evaluation missing BBL") state.evaluation.evaluated_input.bbl = null;
    if (kind === "scenario missing BBL") state.scenario.evaluated_input.bbl = null;
    if (["evaluation mismatch", "both mismatched", "malformed mismatched evaluation"].includes(kind)) state.evaluation.evaluated_input.bbl = "5000010001";
    if (["scenario mismatch", "both mismatched"].includes(kind)) state.scenario.evaluated_input.bbl = "5000010001";
    const expected = [
      ...(kind === "malformed evaluation" ? [{ label: "Captured unusable rule-evaluation record", value: state.evaluation }] : []),
      ...(state.evaluation.evaluated_input.bbl !== state.profile!.identity.bbl ? [{ label: "Returned rule evaluation record", value: state.evaluation }] : []),
      ...(state.scenario.evaluated_input.bbl !== state.profile!.identity.bbl ? [{ label: "Returned scenario record", value: state.scenario }] : []),
    ];
    render(<ArchitectEntry/>);
    const report = document.querySelector<HTMLElement>(".architect-report")!;
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    const records = expected.map(({ label, value }) => {
      expect(screen.getAllByText(label, { exact: true })).toHaveLength(1);
      const record = screen.getByText(label, { exact: true }).closest("details")!;
      expect(record.closest(".architect-report")).toBe(report);
      expect(record.open).toBe(false);
      expect(JSON.parse(record.querySelector("pre")!.textContent!)).toEqual(value);
      if (label.startsWith("Returned")) expect(record.closest("[role='alert']")).toHaveTextContent("Results are withheld from this property");
      return record;
    });
    // Include both initially open and initially closed disclosures in the
    // actual route's print lifecycle, rather than only mounting ReportView.
    const facts = report.querySelector<HTMLDetailsElement>("#brief-facts")!;
    facts.open = true;
    const before = Array.from(report.querySelectorAll("details")).map(item => ({ item, open: item.open }));
    fireEvent.click(screen.getByRole("checkbox", { name: "Include full audit appendix" }));
    const print = vi.spyOn(window, "print").mockImplementation(() => {
      expect(report).toHaveClass("includes-audit");
      records.forEach(record => expect(record.open).toBe(true));
      expect(report.querySelector<HTMLDetailsElement>("#brief-calculations")!.open).toBe(true);
    });
    try {
      fireEvent.click(screen.getByRole("button", { name: "Print property brief" }));
      expect(print).toHaveBeenCalledOnce();
      fireEvent(window, new Event("beforeprint"));
      fireEvent(window, new Event("afterprint"));
      before.forEach(({ item, open }) => expect(item.open).toBe(open));
      records.forEach((record, i) => expect(JSON.parse(record.querySelector("pre")!.textContent!)).toEqual(expected[i].value));
    } finally { print.mockRestore(); }
  });
});

describe("connected architect entry", () => {
  it.each(["overview", "zoning", "scenarios", "evidence", "report"].flatMap(view => ["input_validation", "effective_window", "outputs", "citations"].map(field => ({ view, field }))))("preserves a malformed $field record without crashing the $view route", ({ view, field }) => {
    state.params.set("view", view);
    state.evaluation = draftApplicableDoc();
    state.evaluation.evaluated_input.bbl = state.profile!.identity.bbl;
    delete (state.evaluation.evaluations[0] as unknown as Record<string, unknown>)[field];
    state.scenario = structuredClone(scenarioFixture) as Scenario;
    state.scenario.evaluated_input.bbl = state.profile!.identity.bbl;
    expect(() => render(<ArchitectEntry/>)).not.toThrow();
    expect(screen.getByRole("heading", { name: "Rule details incomplete" })).toBeInTheDocument();
    expect(screen.getByTestId("rule-eval-announcer")).toHaveTextContent("Numerical summaries are unavailable");
    const raw = screen.getByText("Captured unusable rule-evaluation record").closest("details")!.querySelector("pre")!;
    expect(JSON.parse(raw.textContent!)).toEqual(state.evaluation);
    if (view !== "evidence") expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });
  it("shows all facts and opens source evidence immediately with Escape returning focus", () => {
    render(<ArchitectEntry />);
    const source = screen.getByRole("button", { name: "Source for Lot area" });
    source.focus(); fireEvent.click(source);
    const inspector = screen.getByRole("complementary", { name: "Contextual evidence inspector" });
    expect(inspector).toHaveFocus();
    expect(within(inspector).getByText("Original value")).toBeInTheDocument();
    expect(inspector).toHaveClass("has-selection");
    fireEvent.keyDown(inspector, { key: "Escape" });
    expect(source).toHaveFocus();
    for (const field of Object.keys(state.profile!.lot_facts)) expect(screen.getByRole("rowheader", { name: fieldLabel(field) })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Building" }));
    expect(screen.getByRole("heading", { name: "Existing building facts" })).toBeInTheDocument();
    for (const field of Object.keys(state.profile!.existing_building_facts)) expect(screen.getByRole("rowheader", { name: fieldLabel(field) })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Identity" }));
    expect(screen.getByRole("heading", { name: "Identity & source coverage" })).toBeInTheDocument();
  });
  it("filters the selected fact category without losing source access or the complete records", () => {
    render(<ArchitectEntry/>);
    fireEvent.change(screen.getByLabelText("Filter facts"), { target: { value: "lot area" } });
    expect(screen.getAllByRole("rowheader")).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Source for Lot area" })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Filter facts"), { target: { value: "no matching fact" } });
    expect(screen.getByText("No facts match this filter.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Clear filter" }));
    expect(screen.getAllByRole("rowheader")).toHaveLength(Object.keys(state.profile!.lot_facts).length);
  });
  it("explains an absent selected source and keeps the inspector close control usable", () => {
    state.params.set("view", "overview");
    state.profile!.lot_facts.lotarea!.provenance_ref = "missing-lot-area-source";
    render(<ArchitectEntry />);
    const source = within(screen.getByRole("region", { name: "Development limits" })).getByRole("button", { name: "Source for Lot area" });
    source.focus();
    fireEvent.click(source);
    const inspector = screen.getByRole("complementary", { name: "Contextual evidence inspector" });
    expect(inspector).toHaveFocus();
    expect(within(inspector).getByRole("heading", { name: "Source record unavailable" })).toBeInTheDocument();
    expect(inspector).toHaveTextContent("missing-lot-area-source");
    expect(inspector).toHaveTextContent("was not supplied");
    fireEvent.click(within(inspector).getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("complementary", { name: "Contextual evidence inspector" })).not.toBeInTheDocument();
    expect(source).toHaveFocus();
  });
  it("retains the searched label and distinguishes the PLUTO representative address", () => {
    const bbl = state.profile!.identity.bbl;
    sessionStorage.setItem(`nyc-buildability:confirmed-address:${bbl}`, JSON.stringify({ bbl, label: "CONFIRMED SEARCHED ADDRESS", confirmedAt: "2026-09-14T00:00:00Z", sourceRecord: {} }));
    render(<ArchitectEntry />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("CONFIRMED SEARCHED ADDRESS");
    expect(screen.getByTestId("representative-address")).toHaveTextContent(state.profile!.identity.address!.normalized_address!);
  });
  it("withholds an analysis returned for another BBL and preserves its returned evidence", () => {
    state.params.set("view", "evidence"); state.evaluation = draftApplicableDoc(); state.evaluation.evaluated_input.bbl = "5000010001";
    render(<ArchitectEntry />);
    expect(screen.getByRole("alert")).toHaveTextContent("Rule evaluation identity mismatch");
    expect(screen.getByRole("alert")).toHaveTextContent("5000010001");
    expect(screen.queryByText("max_residential_far")).not.toBeInTheDocument();
    expect(screen.getByText("Returned rule evaluation record")).toBeInTheDocument();
  });
  it.each([
    { returnedBbl: "5000010001", document: unsupportedDoc, identityState: "mismatch" },
    { returnedBbl: null, document: spatialUncertaintyDoc, identityState: "missing" },
  ])("announces identity $identityState instead of a withheld analysis classification", ({ returnedBbl, document, identityState }) => {
    state.params.set("view", "evidence");
    const { rerender } = render(<ArchitectEntry />);
    state.evaluation = document();
    state.evaluation.evaluated_input.bbl = returnedBbl;
    rerender(<ArchitectEntry />);
    const announcer = screen.getByTestId("rule-eval-announcer");
    expect(announcer).toHaveTextContent(`Rule evaluation identity ${identityState}`);
    expect(announcer).toHaveTextContent(`Requested BBL ${state.profile!.identity.bbl}`);
    expect(announcer).toHaveTextContent(`returned BBL ${returnedBbl ?? "not stated"}`);
    expect(announcer).toHaveTextContent("Results are withheld from this property");
    expect(announcer).not.toHaveTextContent(/no draft rule applies|lot spans districts|Draft rule evaluation loaded/);
  });
  it("announces a loaded evaluation only when its BBL matches the selected property", () => {
    state.evaluation = draftApplicableDoc();
    state.evaluation.evaluated_input.bbl = state.profile!.identity.bbl;
    render(<ArchitectEntry />);
    expect(screen.getByTestId("rule-eval-announcer")).toHaveTextContent("Draft rule evaluation loaded: an unreviewed draft determination");
  });
  it("rejects a mismatched property record before mounting its analysis", () => {
    state.profile!.identity.bbl = "5000010001";
    render(<ArchitectEntry />);
    expect(screen.getByRole("heading", { name: "Property identity mismatch" })).toBeInTheDocument();
    expect(screen.queryByTestId("profile-view")).not.toBeInTheDocument();
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent("Property identity mismatch");
    expect(screen.getByTestId("outcome-announcer")).not.toHaveTextContent("profile loaded");
  });
  it("preserves explicit absent flags and planned capability states", () => {
    state.params.set("view", "zoning"); state.profile!.zoning.mapped_features = [];
    const { rerender } = render(<ArchitectEntry />);
    expect(screen.getByText("Pending land-use actions")).toBeInTheDocument();
    expect(screen.getByText("Unknown — source not connected")).toBeInTheDocument();
    for (const label of ["Landmark", "Historic district", "2007 FIRM flood flag", "2015 preliminary FIRM flood flag"]) expect(screen.getByText(label, { exact: true })).toBeInTheDocument();
    state.params.set("view", "units"); rerender(<ArchitectEntry />);
    expect(screen.getByRole("heading", { name: "Units is not available in this version" })).toBeInTheDocument();
    expect(screen.queryByTestId("architect-cap")).not.toBeInTheDocument();
  });
});

afterEach(cleanup);
