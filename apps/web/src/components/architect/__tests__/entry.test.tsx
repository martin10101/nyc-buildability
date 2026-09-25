import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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

// DB-050(h): the Preliminary-development-limits panel mounts on the proposal view and
// fetches the UNMOUNTED max-envelope route from the lot context. A DEFAULT stub is
// installed so no test makes an unstubbed max-envelope network call (which added ~5s of
// suite-time creep and a floating state update); the additive-panel block below overrides
// it per test. The default returns the real production shape for the unmounted route: a
// generic 404 → the panel degrades to its typed feature-unavailable card.
let maxEnvelopeFetch: ReturnType<typeof vi.fn>;
function featureUnavailableResponse(): Response {
  // The generic 404 the UNMOUNTED route serves; an explicit numeric Content-Length so
  // the client's size-bound-before-parse branch runs deterministically (matching the
  // panel/api suites' own fixtures) and the outcome classifies as feature_unavailable.
  const text = JSON.stringify({ detail: "Not Found" });
  return new Response(text, { status: 404, headers: { "Content-Type": "application/json", "Content-Length": String(new TextEncoder().encode(text).length) } });
}
beforeEach(() => { state.profile = baseProfile(); state.evaluation = null; state.scenario = null; state.params = new URLSearchParams(`bbl=${state.profile.identity.bbl}&view=facts`); sessionStorage.clear(); vi.clearAllMocks(); maxEnvelopeFetch = vi.fn(async () => featureUnavailableResponse()); vi.stubGlobal("fetch", maxEnvelopeFetch); });

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
  it("renders the additive proposal-editor view inside the gated architect tree", async () => {
    state.params.set("view", "proposal");
    render(<ArchitectEntry />);
    expect(screen.getByTestId("proposal-editor")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Proposal editor" })).toBeInTheDocument();
    expect(screen.getByTestId("editor-honesty")).toHaveTextContent("not a city record");
    // The max-envelope panel mounts here; let its STUBBED fetch settle to the typed
    // feature-unavailable card so there is no floating unstubbed network call (DB-050(h)).
    await screen.findByTestId("envelope-failure");
  });

  it("mounts the max-envelope panel through the STUBBED fetch — never an unstubbed network call (DB-050(h))", async () => {
    state.params.set("view", "proposal");
    render(<ArchitectEntry />);
    expect(screen.getByTestId("proposal-editor")).toBeInTheDocument();
    // The panel's fetch went to the injected stub (not real network), targeting the
    // max-envelope route; settle the outcome to avoid a floating state update.
    await waitFor(() => expect(maxEnvelopeFetch).toHaveBeenCalled());
    expect(String(maxEnvelopeFetch.mock.calls[0][0])).toContain("/api/v1/max-envelope");
    await screen.findByTestId("envelope-failure");
  });
});

/* ================================================================ *
 * D-086 P2 (M5-T115) — the search surface: ONE search/recovery area with the
 * environment badge + professional-review line kept at every width (DB-083 f),
 * the address search, and the BBL alternative whose four distinct lib/bbl.ts
 * validation messages render verbatim (spec §5.1). Rendered with NO bbl param
 * so ArchitectEntry mounts PropertySearch.
 * ================================================================ */
describe("D-086 P2 search surface (no bbl → PropertySearch)", () => {
  beforeEach(() => { state.params = new URLSearchParams(); });

  it("AS-5/DB-083(f): the environment badge + professional-review line render on the search surface (no breakpoint hides them) and carry the internal-build meaning WITHOUT retyping the §29 disclaimer", () => {
    render(<ArchitectEntry />);
    const env = screen.getByTestId("search-environment");
    expect(env).toHaveAttribute("role", "note");
    expect(env).toHaveTextContent("Internal build");
    // LS-P01/A01 meaning: no access control, do-not-share, not a legal determination.
    expect(env).toHaveTextContent("No sign-in or access control yet");
    expect(env).toHaveTextContent("do not share outside the engineering team");
    expect(env).toHaveTextContent("nothing here is a legal determination");
    // A03: the professional-review line is present and visible on the surface.
    expect(screen.getByTestId("search-review")).toHaveTextContent(
      "Preliminary analysis — professional review required before any reliance.",
    );
    // The env note is the environment disclosure, NOT the PRD §29 disclaimer (that
    // one stays verbatim in the global footer via REQUIRED_DISCLAIMER, DB-083 b).
    expect(env).not.toHaveTextContent(
      "This platform provides preliminary development and zoning feasibility",
    );
  });

  it("AS-1: ONE search/recovery area — the address search and the BBL alternative are both on the search surface (the BBL is a native details labelled as an alternative, not a separate step)", () => {
    render(<ArchitectEntry />);
    // The address search (architect autocomplete + manual resolver) is present.
    expect(screen.getByTestId("address-resolution-screen")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1, name: "Find a property" })).toBeInTheDocument();
    // The BBL alternative is a native <details> naming itself an alternative.
    expect(screen.getByText("Search by tax lot (BBL)")).toBeInTheDocument();
    expect(screen.getByText(/alternative to the address search above, not a separate step/)).toBeInTheDocument();
    expect(screen.getByLabelText("BBL")).toBeInTheDocument();
  });

  it("AS-1: an invalid BBL renders each of the four DISTINCT lib/bbl.ts messages verbatim — never one generic red icon", () => {
    render(<ArchitectEntry />);
    const input = screen.getByLabelText("BBL");
    const open = () => fireEvent.click(screen.getByRole("button", { name: "Open property" }));
    const errorBox = () => screen.getByTestId("architect-bbl-error");

    // empty
    fireEvent.change(input, { target: { value: "   " } });
    open();
    expect(errorBox()).toHaveTextContent("Enter a 10-digit BBL (borough, block, and lot).");

    // non_numeric
    fireEvent.change(input, { target: { value: "12ab567890" } });
    open();
    expect(errorBox()).toHaveTextContent("A BBL contains digits only");

    // wrong_length
    fireEvent.change(input, { target: { value: "12345" } });
    open();
    expect(errorBox()).toHaveTextContent("A BBL is exactly 10 digits; you entered 5.");

    // invalid_borough (first digit 0)
    fireEvent.change(input, { target: { value: "0234567890" } });
    open();
    expect(errorBox()).toHaveTextContent("The first digit is the borough and must be 1–5");

    // A valid BBL clears the error and routes (no message rendered).
    fireEvent.change(input, { target: { value: "1000010010" } });
    open();
    expect(state.push).toHaveBeenCalled();
    expect(errorBox()).toBeEmptyDOMElement();
    // aria-invalid is set only while an error is shown (removed on the valid input).
    expect(input).not.toHaveAttribute("aria-invalid");
  });
});

/**
 * Task M5-T070 (D-082-R003 + D-083 / AS-6): the Preliminary-development-limits
 * panel composes ADDITIVELY above the accepted proposal editor on the architect
 * surface. It fetches the UNMOUNTED max-envelope route from the lot context alone
 * (baseProfile carries a recorded lot area), so these tests drive the panel via a
 * scoped global-fetch stub. The essential AS-6 guarantee is display-surface
 * safety: whether the panel loads limits or fails, the accepted editor below it
 * renders and stays fully usable — never a dead surface, never a fabricated limit.
 */
describe("max-envelope panel composes additively on the proposal surface (M5-T070, AS-6)", () => {
  // The EXACT ENVELOPE_DISCLOSURE text from the authoritative serialization
  // (services/api/app/scenario/max_envelope.py :100-108), so the stubbed response
  // body is faithful to MaxEnvelope.as_dict() and the panel's verbatim render is
  // asserted char-for-char (a paraphrase or truncation fails).
  const ENVELOPE_DISCLOSURE =
    "This maximum-buildable envelope is a DETERMINISTIC, rules-derived ESTIMATE for the " +
    "rectangle-prism massing class - NOT a city record, a permit, an approval, or a legal " +
    "determination. Each dimension is the tightest applicable draft rule's allowance for this " +
    "lot (the looser rules are automatically satisfied and recorded as out-competed); where " +
    "more than one rule bounds a dimension, which rule governs is a legal determination " +
    "requiring professional review, surfaced here as an advisory rather than resolved. " +
    "Non-commensurable dimensions (residential FAR, rear yard) are disclosed as honest gaps. " +
    "Qualified professional review is required before any reliance.";

  /** The Generated building option outline the stub returns — DELIBERATELY DISTINCT
   * from the editor's rectangle seed (5 vertices, vertex 0 X 1000000) so adoption
   * VISIBLY reseeds the numeric authority (4 vertices, vertex 0 X 1000200). */
  const OPTION_2263: Array<[number, number]> = [
    [1000200, 200500],
    [1000260, 200500],
    [1000260, 200540],
    [1000200, 200540],
  ];

  /**
   * A faithful MaxEnvelope.as_dict() body: one binding + one gap dimension (gap > 0,
   * so the aggregate stays visibly incomplete, D-083-R004) and a FITTED, contained
   * candidate carrying the full CandidatePlacement shape — all five fields, including
   * the lot_rectangle + footprint {anchor_x, anchor_y, width_ft, depth_ft, area_sq_ft}
   * records (max_envelope.py :340-347/:617-621/:891-895) — so one-action adoption is
   * offered. An explicit numeric Content-Length runs the client's
   * size-bound-before-parse branch deterministically in jsdom.
   */
  function envelopeResponse(): Response {
    const body = {
      massing_class: "rectangle_prism",
      label: "BBL preliminary development limits",
      disclosure: ENVELOPE_DISCLOSURE,
      dimensions: [
        {
          dimension_id: "max_far_floor_area",
          family: "floor_area",
          required_output: "max_floor_area_sq_ft",
          direction: "max",
          unit: "sq_ft",
          label: "Maximum floor area",
          saturating: false,
          binding_value: 20000,
          binding_rule_id: "zr-far-r6",
          binding_rule_version: "2024.1",
          coverage_status: "covered",
          out_competed_rule_ids: ["zr-far-r6-alt"],
          rule_citations: [{ section: "23-142" }],
          gap_reason: null,
          conflict_advisory: null,
          detail: "The floor-area ratio ceiling for the underlying district.",
        },
        {
          dimension_id: "max_height_ft",
          family: "height",
          required_output: "max_height_ft",
          direction: "max",
          unit: "ft",
          label: "Maximum height",
          saturating: false,
          binding_value: null,
          binding_rule_id: null,
          binding_rule_version: null,
          coverage_status: "uncovered",
          out_competed_rule_ids: [],
          rule_citations: [],
          // [ORCH-CORRECTED per G3-F3/G4-F3] a REAL EnvelopeGapReason token, never prose.
          gap_reason: "allowance_unresolved",
          conflict_advisory: null,
          detail: "The height ceiling depends on a street width this lot has not resolved.",
        },
      ],
      candidate: {
        outline: { srid: 2263, vertices: OPTION_2263 },
        levels: [{ level_index: 0, floor_count: 4, floor_to_floor_ft: 10 }],
        exterior_walls: [
          { id: "W-S", start_vertex_index: 0, end_vertex_index: 1 },
          { id: "W-E", start_vertex_index: 1, end_vertex_index: 2 },
        ],
      },
      candidate_notes: ["Fitted to the recorded lot area; edit every value after adoption."],
      candidate_placement: {
        status: "fitted",
        detail: "The generated option was fitted inside the lot rectangle and proved contained.",
        lot_rectangle: { anchor_x: 1000200, anchor_y: 200500, width_ft: 300, depth_ft: 200, area_sq_ft: 60000 },
        footprint: { anchor_x: 1000200, anchor_y: 200500, width_ft: 60, depth_ft: 40, area_sq_ft: 2400 },
        contained: true,
      },
      candidate_consistency: { consistent: true },
      summary: { binding: 1, gap: 1, saturating_binding: 0, total: 2 },
      rule_input_bindings: {},
      unmapped_lot_facts: [],
      correlation_id: "cid",
    };
    const text = JSON.stringify(body);
    return new Response(text, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Content-Length": String(new TextEncoder().encode(text).length),
        "X-Correlation-ID": "cid",
      },
    });
  }

  const vertexXInputs = () => screen.getAllByLabelText(/^Vertex \d+ X coordinate$/) as HTMLInputElement[];
  const vertexX0 = () => screen.getByLabelText("Vertex 0 X coordinate") as HTMLInputElement;

  it("renders the limits panel BEFORE the accepted editor in document order (answer-first, additive)", async () => {
    state.params.set("view", "proposal");
    vi.stubGlobal("fetch", vi.fn(async () => envelopeResponse()));
    render(<ArchitectEntry />);
    // The panel leads with the server disclosure rendered VERBATIM...
    expect(await screen.findByTestId("envelope-disclosure")).toHaveTextContent(ENVELOPE_DISCLOSURE);
    expect(screen.getByRole("heading", { name: "Preliminary development limits" })).toBeInTheDocument();
    // ...and the accepted editor still renders, fully available.
    const panel = screen.getByTestId("max-envelope-panel");
    const editor = screen.getByTestId("proposal-editor");
    expect(screen.getByTestId("editor-honesty")).toHaveTextContent("not a city record");
    expect(screen.getByRole("button", { name: "Add vertex" })).toBeInTheDocument();
    // Explicit ORDERING (not merely both present): the panel PRECEDES the editor in
    // the DOM — the computed limits lead the surface, the editor follows.
    expect(panel.compareDocumentPosition(editor) & Node.DOCUMENT_POSITION_FOLLOWING).not.toBe(0);
  });

  it("adopts the Generated building option through the panel; manual editing AFTER adoption still mutates the draft", async () => {
    state.params.set("view", "proposal");
    vi.stubGlobal("fetch", vi.fn(async () => envelopeResponse()));
    render(<ArchitectEntry />);
    await screen.findByTestId("envelope-disclosure");
    // The editor starts on the MANUAL rectangle seed (5 vertices, vertex 0 X 1000000).
    expect(vertexXInputs()).toHaveLength(5);
    expect(vertexX0().value).toBe("1000000");

    // ONE action adopts the option: the numeric AUTHORITY is reseeded from the
    // candidate (4 vertices, vertex 0 X 1000200) and announced as PROPOSED.
    fireEvent.click(screen.getByTestId("adopt-candidate"));
    expect(vertexXInputs()).toHaveLength(4);
    expect(vertexX0().value).toBe("1000200");
    expect(screen.getByTestId("proposal-check-announcer")).toHaveTextContent("Adopted the Generated building option");

    // Manual editing AFTER adoption still changes draft state (never a dead or
    // read-only surface): retype a coordinate, then add a vertex.
    fireEvent.change(vertexX0(), { target: { value: "1000999" } });
    expect(vertexX0().value).toBe("1000999");
    fireEvent.click(screen.getByRole("button", { name: "Add vertex" }));
    expect(vertexXInputs()).toHaveLength(5);
  });

  it("degrades the panel to a typed failure card; manual editing AFTER the fetch failure still mutates the draft", async () => {
    state.params.set("view", "proposal");
    vi.stubGlobal("fetch", vi.fn(async () => { throw new Error("network down"); }));
    render(<ArchitectEntry />);
    // A typed failure card (never a dead surface, never a fabricated limit)...
    const failure = await screen.findByTestId("envelope-failure");
    expect(failure).toHaveTextContent("could not be reached");
    expect(screen.queryByTestId("envelope-disclosure")).not.toBeInTheDocument();
    // ...and the accepted editor below stays fully usable: manual editing changes state.
    expect(screen.getByTestId("proposal-editor")).toBeInTheDocument();
    expect(vertexXInputs()).toHaveLength(5);
    fireEvent.change(vertexX0(), { target: { value: "1000123" } });
    expect(vertexX0().value).toBe("1000123");
    fireEvent.click(screen.getByRole("button", { name: "Add vertex" }));
    expect(vertexXInputs()).toHaveLength(6);
  });
});

afterEach(() => vi.unstubAllGlobals());
afterEach(cleanup);
