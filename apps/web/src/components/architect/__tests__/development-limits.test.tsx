import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import { PropertyOverview } from "../PropertyOverview";
import { ZoningView } from "../ProfileViews";
import { ReportView } from "../ReportView";
import { DevelopmentLimits, DraftHeadline } from "../DevelopmentLimits";
import { ScenarioWorkspace } from "../ScenarioWorkspace";
import type { PropertyProfile } from "@/lib/contract";
import type { Scenario } from "@/lib/scenario-contract";
import { validateScenarioDocument } from "@/lib/scenario-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import { validateRuleEvaluationDocument } from "@/lib/rule-evaluation-contract";
import { draftApplicableDoc, missingEvidenceDoc, ruleConflictDoc } from "@/test-support/rule-evaluation-fixtures";
import { bulkRow, evaluatedResidentialFar, evaluationIsInspectable, scenarioCap } from "@/lib/architect/development-limits";
import scenarioFixture from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";
import r5Snapshot from "../../../../../../services/api/app/_zr_snapshots/v1/zr-23-21.snapshot.json";
import r6Snapshot from "../../../../../../services/api/app/_zr_snapshots/v1/zr-23-22.snapshot.json";

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

describe("V3 citation support", () => {
  it.each(["overview", "zoning", "report"])("withholds empty but validator-accepted source support in %s", view => {
    const { profile, evaluation, scenario } = inputs();
    const empty = { snapshot_id: "", section: "", quote: "", provenance: {} };
    evaluation.evaluations[0].citations = [empty];
    scenario.cap_provenance!.citations = [structuredClone(empty)];
    expect(validateRuleEvaluationDocument(evaluation).ok).toBe(true);
    expect(validateScenarioDocument(scenario).ok).toBe(true);
    expect(evaluationIsInspectable(evaluation)).toBe(true);
    const props = { profile, evaluation, scenario, onInspect: vi.fn() };
    render(view === "overview" ? <PropertyOverview {...props}/> : view === "zoning" ? <ZoningView {...props}/> : <ReportView {...props} label="Test property"/>);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByText("Rule source support incomplete · inspect evidence")).toBeInTheDocument();
    if (view === "report") {
      const raw = screen.getByText("Full rule-evaluation document").closest("details")!.querySelector("pre")!;
      expect(JSON.parse(raw.textContent!)).toEqual(evaluation);
    }
  });

  it.each(["snapshot_id", "section", "quote"])("does not treat whitespace-only %s as supporting evidence", field => {
    const { profile, evaluation } = inputs();
    (evaluation.evaluations[0].citations[0] as unknown as Record<string, unknown>)[field] = " \t\n ";
    expect(validateRuleEvaluationDocument(evaluation).ok).toBe(true);
    expect(evaluationIsInspectable(evaluation)).toBe(true);
    expect(evaluatedResidentialFar(evaluation, profile.identity.bbl)).toBeNull();
  });

  const sourceFields = ["snapshot_id", "section_number", "source_id", "official_channel", "request_url", "retrieved_at", "content_digest_sha256"];
  it.each(sourceFields.flatMap(field => [undefined, "", " \t "].map(value => ({ field, value }))))("requires meaningful provenance $field = $value", ({ field, value }) => {
    const { profile, evaluation, scenario } = inputs();
    const citation = evaluation.evaluations[0].citations[0];
    const metadata = citation.provenance as Record<string, unknown>;
    if (value === undefined) delete metadata[field]; else metadata[field] = value;
    scenario.cap_provenance!.citations = structuredClone(evaluation.evaluations[0].citations);
    expect(evaluatedResidentialFar(evaluation, profile.identity.bbl)).toBeNull();
    expect(scenarioCap(scenario, evaluation, profile.identity.bbl)).toBeNull();
  });

  it.each([undefined, null, {}, [], "source"])("withholds a missing or unusable provenance object %j", provenance => {
    const { profile, evaluation, scenario } = inputs();
    (evaluation.evaluations[0].citations[0] as unknown as Record<string, unknown>).provenance = provenance;
    (scenario.cap_provenance!.citations[0] as unknown as Record<string, unknown>).provenance = provenance;
    expect(evaluatedResidentialFar(evaluation, profile.identity.bbl)).toBeNull();
    expect(scenarioCap(scenario, evaluation, profile.identity.bbl)).toBeNull();
  });

  it.each([
    ["snapshot_id", "other-snapshot"], ["section_number", "23-22"], ["source_id", "unrelated-source"],
    ["official_channel", "unrecorded"], ["retrieved_at", "yesterday"], ["content_digest_sha256", "not-a-digest"],
    ["request_url", "https://example.com/article-ii/chapter-3/23-21"],
    ["request_url", "javascript:alert(1)"],
    ["request_url", "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22"],
  ])("rejects unbound source metadata %s = %s", (field, value) => {
    const { profile, evaluation, scenario } = inputs();
    (evaluation.evaluations[0].citations[0].provenance as Record<string, unknown>)[field] = value;
    scenario.cap_provenance!.citations = structuredClone(evaluation.evaluations[0].citations);
    expect(evaluatedResidentialFar(evaluation, profile.identity.bbl)).toBeNull();
    expect(scenarioCap(scenario, evaluation, profile.identity.bbl)).toBeNull();
  });

  it.each(["empty cap citation", "different snapshot", "different digest", "different quote", "different capture", "extra cap citation", "duplicate trace citation"])("withholds cap support with %s", kind => {
    const { profile, evaluation, scenario } = inputs();
    const citation = scenario.cap_provenance!.citations[0];
    const metadata = citation.provenance as Record<string, unknown>;
    if (kind === "empty cap citation") scenario.cap_provenance!.citations = [{ snapshot_id: "", section: "", quote: "", provenance: {} }];
    if (kind === "different snapshot") { citation.snapshot_id = "another-capture"; metadata.snapshot_id = "another-capture"; }
    if (kind === "different digest") metadata.content_digest_sha256 = "a".repeat(64);
    if (kind === "different quote") citation.quote = "A different supplied excerpt.";
    if (kind === "different capture") metadata.retrieved_at = "2026-08-01T00:00:00Z";
    if (kind === "extra cap citation") scenario.cap_provenance!.citations.push(structuredClone(citation));
    if (kind === "duplicate trace citation") evaluation.evaluations[0].citations.push(structuredClone(evaluation.evaluations[0].citations[0]));
    render(<DraftHeadline scenario={scenario} evaluation={evaluation} bbl={profile.identity.bbl}/>);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it.each([r5Snapshot, r6Snapshot])("accepts meaningful metadata from committed draft snapshot $snapshot_id", snapshot => {
    const { profile, evaluation, scenario } = inputs();
    // A presentation-only metadata substitution, not a district applicability
    // or legal-approval assertion. Values remain the supplied fixture outputs.
    const citation = {
      snapshot_id: snapshot.snapshot_id, section: snapshot.section_number, quote: snapshot.verbatim_excerpt,
      last_amended: snapshot.source.section_last_amended,
      provenance: {
        snapshot_id: snapshot.snapshot_id, section_number: snapshot.section_number,
        source_id: snapshot.source.source_id, official_channel: snapshot.source.official_channel,
        request_url: snapshot.source.request_url, retrieved_at: snapshot.source.retrieved_at,
        content_digest_sha256: snapshot.content_digest_sha256, raw_html_verified: false, extraction_status: "extracted_draft",
      },
    };
    evaluation.evaluations[0].citations = [citation];
    scenario.cap_provenance!.citations = [structuredClone(citation)];
    expect(evaluatedResidentialFar(evaluation, profile.identity.bbl)?.value).toBe(1.5);
    expect(scenarioCap(scenario, evaluation, profile.identity.bbl)).toBe(15000);
    expect(citation.provenance.raw_html_verified).toBe(false);
  });
});

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

describe("review cluster — five independently reproduced associations", () => {
  it.each(["input_validation", "effective_window", "outputs", "citations"])("R1 does not crash on validator-accepted missing trace %s", field => {
    const { profile, evaluation, scenario } = inputs();
    delete (evaluation.evaluations[0] as unknown as Record<string, unknown>)[field];
    expect(validateRuleEvaluationDocument(evaluation).ok).toBe(true);
    expect(() => show(profile, evaluation, scenario)).not.toThrow();
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it("R2 does not promote a cap while the associated evaluation reports a rule conflict", () => {
    const { profile, scenario } = inputs();
    const evaluation = ruleConflictDoc();
    evaluation.evaluated_input.bbl = profile.identity.bbl;
    evaluation.evaluated_input.input_fingerprint = scenario.evaluated_input.input_fingerprint!;
    show(profile, evaluation, scenario);
    expect(screen.getByText("Conflicting rule results")).toBeInTheDocument();
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it("R3 does not treat a null scenario fingerprint as association evidence", () => {
    const { profile, evaluation, scenario } = inputs();
    scenario.evaluated_input.input_fingerprint = null;
    show(profile, evaluation, scenario);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
  });

  it("R4 cannot relabel a residential FAR output as height in feet", () => {
    const { profile, evaluation, scenario } = inputs();
    const trace = evaluation.evaluations[0];
    Object.assign(scenario.constraints.find(row => row.key === "height_limit")!, {
      state: "draft", value: 1.5, unit: "feet",
      provenance: { rule_id: trace.rule_id, rule_version: trace.rule_version, output_name: "max_residential_far" },
    });
    show(profile, evaluation, scenario);
    expect(screen.getByText("Height", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
  });

  it("R5 never chooses one competing trace by filtering on the desired value", () => {
    const { evaluation, scenario } = inputs();
    const trace = evaluation.evaluations[0];
    evaluation.evaluations.push({ ...structuredClone(trace), outputs: { max_residential_far: 2.5 } });
    Object.assign(scenario.constraints.find(row => row.key === "height_limit")!, {
      state: "draft", value: 1.5, unit: "feet",
      provenance: { rule_id: trace.rule_id, rule_version: trace.rule_version, output_name: "max_residential_far" },
    });
    expect(bulkRow(scenario, "height_limit", evaluation).value).toBeNull();
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
    evaluation.evaluations[0].outputs = { max_residential_far: 0, max_residential_floor_area_sq_ft: 0 };
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

  it("preserves untyped bulk constraints, including zero, in evidence without interpreting their meaning", () => {
    const { profile, scenario, evaluation } = inputs();
    const height = scenario.constraints.find(row => row.key === "height_limit")!;
    const trace = structuredClone(evaluation.evaluations[0]);
    Object.assign(trace, { rule_id: "synthetic-bulk-output", family: "height", outputs: { synthetic_height: 0 } });
    evaluation.evaluations.push(trace);
    Object.assign(height, { state: "draft", value: 0, unit: "feet", provenance: { rule_id: trace.rule_id, rule_version: trace.rule_version, output_name: "synthetic_height" } });
    render(<ReportView profile={profile} evaluation={evaluation} scenario={scenario} label="Test property"/>);
    expect(screen.getByText("Height", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
    expect(screen.getByRole("link", { name: "Evidence for Height" })).toBeInTheDocument();
    expect(screen.getByText("Setbacks and yards", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
    expect(screen.getByText("Lot coverage and open space", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
    const captured = screen.getByText("Complete scenario record").closest("details")!.querySelector("pre")!;
    const retained = JSON.parse(captured.textContent!).constraints.find((row: { key: string }) => row.key === "height_limit");
    expect(retained).toEqual(height);
  });

  it.each([null, {}, [], "claimed provenance", { rule_id: "unlinked-rule" }])("does not promote a bulk value without traceable provenance: %j", provenance => {
    const { profile, scenario, evaluation } = inputs();
    const height = scenario.constraints.find(row => row.key === "height_limit")!;
    Object.assign(height, { state: "draft", value: 55, unit: "feet", provenance });
    show(profile, evaluation, scenario);
    expect(screen.getByText("Height", { selector: "dt" }).closest("div")).toHaveTextContent("Not calculated");
    expect(screen.getByRole("link", { name: "Evidence for Height" })).toHaveAttribute("href", `/property?ruleeval=on&bbl=${profile.identity.bbl}&view=evidence`);
  });
});

describe("review cluster neighboring states", () => {
  it("shows readable review status and preserves its exact enum in source wording", () => {
    const { profile, evaluation, scenario } = inputs();
    scenario.coverage_status = "professional_review_required";
    show(profile, evaluation, scenario);
    const cap = screen.getByTestId("architect-cap");
    expect(within(cap).getByText("Professional review required", { exact: true })).toBeInTheDocument();
    const wording = within(cap).getByText("Result scope and source wording").closest("details")!;
    expect(wording).toHaveTextContent("professional_review_required");
  });
  it.each(["conflicting scenario", "failed integrity", "unsupported scenario", "contradictory validation", "malformed invalid-input list"])("withholds promoted results for %s", kind => {
    const { profile, evaluation, scenario } = inputs();
    if (kind === "conflicting scenario") scenario.coverage_status = "data_conflict";
    if (kind === "failed integrity") scenario.integrity_check.agreed = false;
    if (kind === "unsupported scenario") scenario.scenario_kind = "unsupported";
    if (kind === "contradictory validation") evaluation.evaluations[0].input_validation.invalid_inputs = [{ name: "lot_area", reason: "not usable" }];
    if (kind === "malformed invalid-input list") (evaluation.evaluations[0].input_validation as unknown as Record<string, unknown>).invalid_inputs = null;
    show(profile, evaluation, scenario);
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });
  it.each([null, "", "   ", "sha256:", `sha256:${"G".repeat(64)}`])("withholds an unproven scenario fingerprint %j", inputFingerprint => {
    const { profile, evaluation, scenario } = inputs();
    scenario.evaluated_input.input_fingerprint = inputFingerprint;
    show(profile, evaluation, scenario);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
  });

  it.each(["overview", "zoning", "report"])("withholds cap promotion across %s when the evaluation is fail-safe", view => {
    const { profile, evaluation, scenario } = inputs();
    evaluation.fail_safe = true;
    evaluation.fail_safe_reason = "spatial_intersection_absent";
    const props = { profile, evaluation, scenario, onInspect: vi.fn() };
    render(view === "overview" ? <PropertyOverview {...props}/> : view === "zoning" ? <ZoningView {...props}/> : <ReportView {...props} label="Test property"/>);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByText("Zoning boundary check unavailable")).toBeInTheDocument();
  });

  it.each(["zoning", "report"])("preserves a malformed evaluation as captured evidence in %s", view => {
    const { profile, evaluation, scenario } = inputs();
    delete (evaluation.evaluations[0] as unknown as Record<string, unknown>).outputs;
    const props = { profile, evaluation, scenario, onInspect: vi.fn() };
    expect(() => render(view === "zoning" ? <ZoningView {...props}/> : <ReportView {...props} label="Test property"/>)).not.toThrow();
    expect(screen.getByRole("heading", { name: "Rule details incomplete" })).toBeInTheDocument();
    const raw = screen.getByText("Captured unusable rule-evaluation record").closest("details")!.querySelector("pre")!;
    expect(JSON.parse(raw.textContent!)).toEqual(evaluation);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  const malformed = [undefined, null, false, 42, "malformed", [], {}];
  it.each(["input_validation", "effective_window", "outputs", "citations"].flatMap(field => malformed.map(value => ({ field, value }))))("guards malformed $field = $value at the reader", ({ field, value }) => {
    const { profile, evaluation, scenario } = inputs();
    (evaluation.evaluations[0] as unknown as Record<string, unknown>)[field] = value;
    expect(() => show(profile, evaluation, scenario)).not.toThrow();
    expect(screen.getByTestId("development-evaluated-far")).toHaveTextContent("Not calculated");
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it.each([null, false, 42, "bad trace", [], {}])("guards a malformed trace entry %j", trace => {
    const { profile, evaluation, scenario } = inputs();
    (evaluation.evaluations as unknown[])[0] = trace;
    expect(() => show(profile, evaluation, scenario)).not.toThrow();
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it.each([null, {}, [], { snapshot_id: "s", section: "23-21", quote: "q", provenance: null }])("guards malformed citation entries %j", citation => {
    const { profile, evaluation, scenario } = inputs();
    (evaluation.evaluations[0].citations as unknown[])[0] = citation;
    expect(() => show(profile, evaluation, scenario)).not.toThrow();
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it.each(["same number", "different number", "invalid twin", "inapplicable twin"])("checks duplicate trace identity before output filtering: %s", kind => {
    const { profile, evaluation, scenario } = inputs();
    const twin = structuredClone(evaluation.evaluations[0]);
    if (kind === "different number") twin.outputs = { max_residential_far: 2.5, max_residential_floor_area_sq_ft: 25000 };
    if (kind === "invalid twin") twin.input_validation.valid = false;
    if (kind === "inapplicable twin") twin.applicability_outcome = false;
    evaluation.evaluations.push(twin);
    expect(evaluatedResidentialFar(evaluation, profile.identity.bbl)).toBeNull();
    expect(scenarioCap(scenario, evaluation, profile.identity.bbl)).toBeNull();
  });

  it.each(["missing evaluation", "different rule", "different version", "wrong output meaning", "different cap value"])("does not promote a cap with %s", kind => {
    const { profile, evaluation, scenario } = inputs();
    if (kind === "different rule") scenario.cap_provenance!.rule_id = "different-rule";
    if (kind === "different version") scenario.cap_provenance!.rule_version = "different-version";
    if (kind === "wrong output meaning") scenario.cap_provenance!.output_name = "max_residential_far";
    if (kind === "different cap value") scenario.draft_zoning_floor_area_cap_sq_ft = 15001;
    render(<DraftHeadline scenario={scenario} evaluation={kind === "missing evaluation" ? null : evaluation} bbl={profile.identity.bbl}/>);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
  });

  it("withholds the Scenarios headline and keeps an unassociated return inside explicit evidence", () => {
    const { profile, scenario } = inputs();
    const evaluation = ruleConflictDoc();
    evaluation.evaluated_input.bbl = profile.identity.bbl;
    evaluation.evaluated_input.input_fingerprint = scenario.evaluated_input.input_fingerprint!;
    render(<ScenarioWorkspace document={scenario} evaluation={evaluation} bbl={profile.identity.bbl}/>);
    expect(screen.getByTestId("architect-cap")).toHaveTextContent("Not calculated");
    const disclosure = screen.getByText("Returned scenario figures · association not confirmed").closest("details")!;
    expect(disclosure.open).toBe(false);
    expect(disclosure).toHaveTextContent("15,000");
    const raw = screen.getByText("Complete scenario record").closest("details")!.querySelector("pre")!;
    expect(JSON.parse(raw.textContent!)).toEqual(scenario);
  });
});
