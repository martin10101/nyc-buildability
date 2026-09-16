import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import { PropertyOverview } from "../PropertyOverview";
import { ZoningView } from "../ProfileViews";
import { ReportView } from "../ReportView";
import { DevelopmentLimits } from "../DevelopmentLimits";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { draftApplicableDoc, missingEvidenceDoc } from "@/test-support/rule-evaluation-fixtures";
import scenarioFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
afterEach(cleanup);

/** Display-only fixtures. District permutations do not assert legal applicability. */
function inputs() {
  const profile = baseProfile();
  const evaluation = draftApplicableDoc();
  const scenario = structuredClone(scenarioFixture) as Scenario;
  evaluation.evaluated_input.bbl = profile.identity.bbl;
  scenario.evaluated_input.bbl = profile.identity.bbl;
  Object.assign(profile.provenance.find(record => record.original_field_name === "residfar")!, { normalized_value: 3, original_value: "3.00" });
  Object.assign(profile.provenance.find(record => record.original_field_name === "builtfar")!, { normalized_value: 2.61, original_value: "2.61" });
  profile.existing_building_facts.builtfar!.value = 2.61;
  return { profile, evaluation, scenario };
}
function reference(profile: PropertyProfile) {
  return profile.provenance.find(record => record.original_field_name === "residfar")!;
}
function show(profile: PropertyProfile, evaluation: RuleEvaluation | null = null, scenario: Scenario | null = null) {
  return render(<DevelopmentLimits profile={profile} evaluation={evaluation} scenario={scenario}/>);
}

describe("development-first entry points", () => {
  it.each(["overview", "zoning", "report"])("puts a distinct city FAR reference and calculation status in %s", view => {
    const profile = baseProfile();
    const reference = profile.provenance.find(record => record.original_field_name === "residfar")!;
    reference.normalized_value = 3;
    const building = profile.existing_building_facts.builtfar!;
    building.value = 2.61;
    const props = { profile, scenario: null, evaluation: null, onInspect: vi.fn() };
    render(view === "overview" ? <PropertyOverview {...props}/> : view === "zoning" ? <ZoningView {...props}/> : <ReportView {...props} label="Test property"/>);
    const summary = screen.getByRole("region", { name: "Development limits" });
    expect(within(summary).getByText("Residential FAR · city record")).toBeInTheDocument();
    expect(within(summary).getByTestId("development-reference-far")).toHaveTextContent("3.00");
    expect(within(summary).getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(summary).not.toHaveTextContent("2.61");
    expect(within(summary).getByText("Height")).toBeInTheDocument();
    expect(within(summary).getByText("Setbacks and yards")).toBeInTheDocument();
    expect(within(summary).getByText("Lot coverage and open space")).toBeInTheDocument();
  });

  it("keeps every existing building fact behind one reversible disclosure", () => {
    const { profile } = inputs();
    render(<PropertyOverview profile={profile} scenario={null} onInspect={vi.fn()}/>);
    const disclosure = screen.getByText("Existing building information").closest("details")!;
    expect(disclosure.open).toBe(false);
    fireEvent.click(screen.getByText("Existing building information"));
    expect(disclosure.open).toBe(true);
    expect(within(disclosure).getByRole("rowheader", { name: "Built FAR" }).closest("tr")).toHaveTextContent("2.61");
    expect(within(disclosure).getAllByRole("rowheader")).toHaveLength(Object.keys(profile.existing_building_facts).length);
    fireEvent.click(screen.getByText("Existing building information"));
    expect(disclosure.open).toBe(false);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("3.00");
  });
});

describe("source and calculation boundaries", () => {
  it("shows the captured 1279 37 Street values without manufacturing a 7,200 sq ft cap", () => {
    const { profile } = inputs();
    // The two observed numeric fields are the real-parcel regression; the
    // surrounding cloned fixture is synthetic, not a captured full profile.
    profile.identity.bbl = "3052960043";
    profile.provenance.forEach(record => { record.bbl = profile.identity.bbl; });
    profile.identity.address!.normalized_address = "3622 13 AVENUE";
    profile.zoning.districts = ["M1-2/R6A"];
    profile.zoning.special_districts = ["MX-12"];
    profile.lot_facts.lotarea!.value = 2400;
    const evaluation = missingEvidenceDoc();
    evaluation.evaluated_input.bbl = profile.identity.bbl;
    show(profile, evaluation);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("3.00");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByText("Zoning boundary check unavailable")).toBeInTheDocument();
    expect(screen.queryByText(/7,200|2\.61/)).not.toBeInTheDocument();
  });

  it("renders canonical evaluated FAR and cap separately from the city reference", () => {
    const { profile, evaluation, scenario } = inputs();
    show(profile, evaluation, scenario);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("3.00");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("1.50");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("15,000 sq ft");
    expect(screen.getByRole("link", { name: "Rules and calculation →" })).toHaveAttribute("href", `/property?ruleeval=on&bbl=${profile.identity.bbl}&view=evidence`);
  });

  it("preserves genuine zero values for source FAR, evaluated FAR and the cap", () => {
    const { profile, evaluation, scenario } = inputs();
    reference(profile).normalized_value = 0;
    evaluation.evaluations[0].outputs = { max_residential_far: 0 };
    scenario.draft_zoning_floor_area_cap_sq_ft = 0;
    show(profile, evaluation, scenario);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("0.00");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("0.00");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("0 sq ft");
  });

  it.each([null, "3", "", false, -1, Infinity, NaN, { unexpected: 3 }])("does not coerce a malformed or missing source FAR: %j", value => {
    const { profile } = inputs();
    reference(profile).normalized_value = value;
    show(profile);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent(value == null ? "Unknown" : "Source value unavailable");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
  });

  it.each(["different values", "identical values", "duplicate provenance ID", "record conflict", "profile conflict"])("exposes ambiguous source evidence: %s", kind => {
    const { profile } = inputs();
    const record = reference(profile);
    if (kind === "profile conflict") profile.conflicts.push({ field: "residfar", resolution: "unresolved", values: [{ source_id: record.source_id, value: 3 }, { source_id: "another-source", value: 4 }] });
    else if (kind === "record conflict") record.conflict_status = "conflicting";
    else if (kind === "duplicate provenance ID") profile.provenance[0].provenance_id = record.provenance_id;
    else profile.provenance.push({ ...record, provenance_id: `${record.provenance_id}-second`, normalized_value: kind === "different values" ? 4 : 3 });
    show(profile);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("Conflicting records");
    expect(screen.getByRole("link", { name: "View source records →" })).toBeInTheDocument();
  });

  it("does not borrow a source reference from another property or another source field", () => {
    const { profile } = inputs();
    reference(profile).bbl = "5000010001";
    show(profile);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("Unknown");
  });

  it("opens the exact residential FAR record without turning an unsafe supplied URL into a link", () => {
    const { profile } = inputs();
    const record = reference(profile);
    record.request_url = "javascript:alert(1)";
    const inspect = vi.fn();
    render(<DevelopmentLimits profile={profile} scenario={null} evaluation={null} onInspect={inspect}/>);
    fireEvent.click(screen.getByRole("button", { name: "Source for residential FAR" }));
    expect(inspect).toHaveBeenCalledWith(record.provenance_id);
    expect(document.querySelector('a[href^="javascript:"]')).toBeNull();
  });

  it.each(["BBL mismatch", "fail safe", "rule conflict", "duplicate output", "inapplicable", "invalid input", "out of effect", "missing citation", "malformed output"])("withholds an unreliable evaluated FAR: %s", kind => {
    const { profile, evaluation } = inputs();
    const trace = evaluation.evaluations[0];
    if (kind === "BBL mismatch") evaluation.evaluated_input.bbl = "5000010001";
    if (kind === "fail safe") evaluation.fail_safe = true;
    if (kind === "rule conflict") evaluation.coverage_status = "data_conflict";
    if (kind === "duplicate output") evaluation.evaluations.push(structuredClone(trace));
    if (kind === "inapplicable") trace.applicability_outcome = false;
    if (kind === "invalid input") trace.input_validation.valid = false;
    if (kind === "out of effect") trace.effective_window.in_effect = false;
    if (kind === "missing citation") trace.citations = [];
    if (kind === "malformed output") trace.outputs = { max_residential_far: "1.5" };
    show(profile, evaluation);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("3.00");
  });

  it.each(["BBL mismatch", "conflict", "unsupported", "failed integrity", "missing provenance", "nonfinite"])("withholds an unreliable cap: %s", kind => {
    const { profile, scenario } = inputs();
    if (kind === "BBL mismatch") scenario.evaluated_input.bbl = "5000010001";
    if (kind === "conflict") scenario.coverage_status = "data_conflict";
    if (kind === "unsupported") scenario.scenario_kind = "unsupported";
    if (kind === "failed integrity") scenario.integrity_check.agreed = false;
    if (kind === "missing provenance") scenario.cap_provenance = null;
    if (kind === "nonfinite") scenario.draft_zoning_floor_area_cap_sq_ft = Infinity;
    show(profile, null, scenario);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
  });

  it("does not combine analysis documents made from different input snapshots", () => {
    const { profile, evaluation, scenario } = inputs();
    scenario.evaluated_input.input_fingerprint = `sha256:${"a".repeat(64)}`;
    show(profile, evaluation, scenario);
    expect(screen.getByText("Analysis records differ · inspect evidence")).toBeInTheDocument();
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it.each(["R1-1", "R2A", "R3-1", "R4B", "R5D", "R6", "R6A", "R7-1", "R7D", "R8B", "R9X", "R10", "R11", "R12", "R3-2/R4", "M1-2/R6A", "unknown"])("uses no district-specific lookup for %s", district => {
    const { profile } = inputs();
    profile.zoning.districts = [district];
    reference(profile).normalized_value = 4.125;
    show(profile);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("4.125");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
  });

  it.each(["1000010010", "2000010001", "3000010001", "4000010001", "5000010001"])("keeps the same source and unknown semantics for borough BBL %s", bbl => {
    const { profile } = inputs();
    profile.identity.bbl = bbl;
    profile.provenance.forEach(record => { record.bbl = bbl; });
    show(profile);
    expect(screen.getByTestId("development-reference-far")).toHaveTextContent("3.00");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByRole("link", { name: "View source records →" })).toHaveAttribute("href", `/property?ruleeval=on&bbl=${bbl}&view=evidence`);
  });

  it("renders supplied bulk constraints, including zero, without converting units or estimating gaps", () => {
    const { profile, scenario, evaluation } = inputs();
    const height = scenario.constraints.find(row => row.key === "height_limit")!;
    const trace = structuredClone(evaluation.evaluations[0]);
    Object.assign(trace, { rule_id: "synthetic-bulk-output", family: "height", outputs: { synthetic_height: 0 } });
    evaluation.evaluations.push(trace);
    Object.assign(height, { state: "draft", value: 0, unit: "feet", provenance: { rule_id: trace.rule_id, rule_version: trace.rule_version, output_name: "synthetic_height" } });
    show(profile, evaluation, scenario);
    expect(screen.getByText("Height", { selector: "dt" }).closest("div")).toHaveTextContent("0 feetDraft");
    expect(screen.getByRole("link", { name: "Evidence for Height" })).toBeInTheDocument();
    expect(screen.getByText("Setbacks and yards", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
    expect(screen.getByText("Lot coverage and open space", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
  });

  it.each([null, {}, [], "claimed provenance", { rule_id: "unlinked-rule" }])("does not promote a bulk value without traceable provenance: %j", provenance => {
    const { profile, scenario, evaluation } = inputs();
    const height = scenario.constraints.find(row => row.key === "height_limit")!;
    Object.assign(height, { state: "draft", value: 55, unit: "feet", provenance });
    show(profile, evaluation, scenario);
    expect(screen.getByText("Height", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
    expect(screen.queryByRole("link", { name: "Evidence for Height" })).not.toBeInTheDocument();
  });
});
