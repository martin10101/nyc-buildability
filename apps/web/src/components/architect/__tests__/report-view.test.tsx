// M5-T037 (D-073-R003): the wide-street conditional FAR must reach BOTH the
// screen and the printed property brief from the SAME validated document, so
// the two surfaces can never disagree. ReportView embeds the SAME
// DevelopmentLimits (the FAR row) and CalculationEvidence (the D-052
// provenance) components the screen uses, so parity is structural — there is no
// second data path. These tests prove it at the surface.
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import { ReportView } from "../ReportView";
import { DevelopmentLimits } from "../DevelopmentLimits";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import { validateRuleEvaluationDocument } from "@/lib/rule-evaluation-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";

vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
afterEach(cleanup);

const WIDE_STREET_BLOCK = {
  determination_state: "within_100ft_of_wide_street",
  far_row: "wide_street_row",
  governing_max_residential_far: 3.44,
  coverage_hint: "conditional",
  exceptions_checked: true,
  named_street_override_pending: false,
  policy_decision_states: ["wide"],
  original_labels: ["80"],
  source_versions: ["2026-03-26"],
  matched_geometry_refs: ["OBJECTID=12345"],
  interpreted_bounds_summaries: ["mapped width 80 ft (>= 75 ft, wide)"],
  classification_reasons: ["DCM effective_disposition=wide; ambiguity_class=none"],
  draft_label: "DRAFT — not a verified legal determination",
  fallback_direction_note:
    "On uncertainty the higher wide-street FAR is withheld; the conservative row governs (validated for these rows only).",
  reason: "Wide-street row governs: within 100 ft of a wide street; DRAFT pending G6.",
} satisfies NonNullable<RuleEvaluation["wide_street"]>;

function wideStreetDoc(bbl: string): RuleEvaluation {
  const doc = draftApplicableDoc();
  doc.contract_version = "1.1.0";
  doc.evaluated_input.bbl = bbl;
  doc.wide_street = structuredClone(WIDE_STREET_BLOCK);
  return doc;
}

describe("M5-T037 — screen/report wide-street parity (D-073-R003)", () => {
  it("renders the identical wide-street conditional FAR on the report and the screen", () => {
    const profile = baseProfile();
    const doc = wideStreetDoc(profile.identity.bbl);
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);

    // Screen surface: DevelopmentLimits rendered directly.
    render(<DevelopmentLimits profile={profile} scenario={null} evaluation={doc} />);
    const screenValue = screen.getByTestId("wide-street-result").textContent;
    cleanup();

    // Report surface: ReportView embeds the SAME DevelopmentLimits + CalculationEvidence.
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    const reportValue = screen.getByTestId("wide-street-result").textContent;

    expect(reportValue).toBe(screenValue);
    expect(reportValue).toContain("3.44");
    // The same document also feeds the D-052 provenance surface on the report.
    expect(screen.getByTestId("wide-street-provenance")).toHaveTextContent("OBJECTID=12345");
  });

  it("shows the honest professional-review escalation on the report, never a fabricated FAR", () => {
    const profile = baseProfile();
    const doc = wideStreetDoc(profile.identity.bbl);
    doc.wide_street!.determination_state = "professional_review_required";
    doc.wide_street!.far_row = "none";
    doc.wide_street!.governing_max_residential_far = null;
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    expect(screen.getByTestId("wide-street-result")).toHaveTextContent("Professional review required");
    expect(screen.queryByText(/3\.44/)).toBeNull();
  });

  it("adds no wide-street surface for a 1.0.0 document (no invented block)", () => {
    const profile = baseProfile();
    const doc = draftApplicableDoc();
    doc.evaluated_input.bbl = profile.identity.bbl;
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    expect(screen.queryByTestId("development-wide-street")).toBeNull();
    expect(screen.queryByTestId("wide-street-provenance")).toBeNull();
  });

  // [ORCH-CORRECTED per M5-T037 HJ F1] A validator-valid but NON-INSPECTABLE
  // document that still carries a wide_street block must be withheld on the
  // report exactly as every screen surface withholds it (the report feeds
  // DevelopmentLimits the same inspectability-gated evaluation) — screen and
  // report can never quietly disagree (D-073-R003).
  it("withholds the wide-street panel on the report for a non-inspectable document, matching the screen", () => {
    const profile = baseProfile();
    const doc = wideStreetDoc(profile.identity.bbl);
    doc.evaluations[0].rule_id = 123 as unknown as string;
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    expect(screen.queryByTestId("development-wide-street")).toBeNull();
    expect(screen.queryByTestId("wide-street-result")).toBeNull();
    cleanup();
    // The screen equivalent: the gate passes null to DevelopmentLimits.
    render(<DevelopmentLimits profile={profile} scenario={null} evaluation={null} />);
    expect(screen.queryByTestId("development-wide-street")).toBeNull();
  });

  // [ORCH-CORRECTED per M5-T037 HJ F2] The REAL server strings (verbatim from
  // wide_street_wiring.py DRAFT_LABEL_NOTICE / FALLBACK_DIRECTION_NOTICE and a
  // real fold reason) carry internal identifiers. The calm answer-first panel
  // must never surface them; they belong behind the evidence disclosure. This
  // fixture uses the actual constants so the jargon cannot silently return.
  it("keeps real server jargon strings off the calm wide-street panel", () => {
    const profile = baseProfile();
    const doc = wideStreetDoc(profile.identity.bbl);
    doc.wide_street!.draft_label =
      "DRAFT - not a Verified determination (D-045-R009). This wide-street " +
      "determination feeds a needs_review draft rule and is subject to G6 " +
      "qualified-human legal review before any published/production use; the " +
      "higher wide-street FAR is never a final result here.";
    doc.wide_street!.fallback_direction_note =
      "D-051 fallback direction (validated for the ZR 23-22 conditional-FAR " +
      "rows only): on uncertainty the higher wide-street FAR is withheld and the " +
      "conservative LOWER-FAR row governs (or the result fails safe to " +
      "professional review). Because the wide-street value is the HIGHER FAR for " +
      "these districts, withholding it can never overstate buildable floor area. " +
      "This is not a universal 'narrow is always conservative' claim - each " +
      "consuming rule validates its own direction (D-051).";
    doc.wide_street!.reason =
      "wide-street determination within_100ft_of_wide_street: the wide-street " +
      "(higher) conditional-FAR row governs (max_residential_far 3.44); DRAFT pending G6.";
    render(<DevelopmentLimits profile={profile} scenario={null} evaluation={doc} />);
    const panel = screen.getByTestId("development-wide-street");
    const text = panel.textContent ?? "";
    for (const token of ["D-045-R009", "D-051", "needs_review", "within_100ft_of_wide_street", "ZR 23-22"]) {
      expect(text).not.toContain(token);
    }
    expect(screen.getByTestId("wide-street-draft")).toHaveTextContent(
      "Draft — pending qualified legal review (not verified).",
    );
    expect(screen.getByTestId("wide-street-result")).toHaveTextContent("3.44");
  });
});

describe("M5-T040 — DB-025(a) calculation-evidence review label gates on determination_state", () => {
  it("does not mislabel a confident within-wide determination as professional review in the evidence", () => {
    const profile = baseProfile();
    render(
      <ReportView profile={profile} scenario={null} evaluation={wideStreetDoc(profile.identity.bbl)} label="Test property" />,
    );
    // The wide-street provenance section carries the confident within value and
    // never the "Professional review required" status line (that phrase belongs
    // to the review determination only). Scope to the section so the panel-level
    // draft banner is not read.
    const provenance = screen.getByTestId("wide-street-provenance");
    expect(provenance).not.toHaveTextContent("Professional review required");
    expect(provenance).toHaveTextContent("3.44");
  });

  it("labels a professional-review wide-street determination as such in the evidence", () => {
    const profile = baseProfile();
    const doc = wideStreetDoc(profile.identity.bbl);
    doc.wide_street!.determination_state = "professional_review_required";
    doc.wide_street!.far_row = "none";
    doc.wide_street!.governing_max_residential_far = null;
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    const provenance = screen.getByTestId("wide-street-provenance");
    expect(provenance).toHaveTextContent("Professional review required");
    expect(provenance).toHaveTextContent("withheld — professional review required");
  });
});

describe("M5-T040 — DB-025(c) conservative-FAR labelling parity, screen and report (D-073-R006)", () => {
  // A shared-document regression: the SAME validated wide_street document must
  // caption the not-within value as the CONSERVATIVE governing ratio — never
  // "Wide-street conditional FAR" — identically on the screen (DevelopmentLimits)
  // and in the printed brief (ReportView → DevelopmentLimits calm panel +
  // CalculationEvidence D-052 provenance). The within and professional-review
  // cases are retained here as controls so the distinction can never regress.
  function docFor(bbl: string, overrides: Partial<NonNullable<RuleEvaluation["wide_street"]>>): RuleEvaluation {
    const doc = wideStreetDoc(bbl);
    Object.assign(doc.wide_street!, overrides);
    return doc;
  }

  const notWithin = {
    determination_state: "not_within_100ft_of_wide_street",
    far_row: "standard_row",
    governing_max_residential_far: 2.2,
    policy_decision_states: ["narrow"],
    original_labels: ["40"],
    matched_geometry_refs: ["OBJECTID=999"],
    interpreted_bounds_summaries: ["mapped width 40 ft (< 75 ft, narrow)"],
    classification_reasons: ["DCM effective_disposition=narrow; ambiguity_class=none"],
    reason: "Not within 100 ft of a wide street; the conservative standard-row FAR governs; DRAFT pending G6.",
  } satisfies Partial<NonNullable<RuleEvaluation["wide_street"]>>;

  it("captions the conservative not-within FAR as the governing ratio on both screen and report (DB-025c)", () => {
    const profile = baseProfile();
    const doc = docFor(profile.identity.bbl, notWithin);
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);

    // Screen surface: DevelopmentLimits rendered directly.
    render(<DevelopmentLimits profile={profile} scenario={null} evaluation={doc} />);
    const screenPanel = screen.getByTestId("development-wide-street");
    const screenValue = screen.getByTestId("wide-street-result").textContent;
    expect(screenPanel).toHaveTextContent("Governing floor-area ratio");
    expect(screenPanel).not.toHaveTextContent("Wide-street conditional FAR");
    expect(screenPanel).toHaveTextContent("the conservative floor-area ratio governs");
    // The accessible section label follows the not-within distinction too.
    expect(screen.getByRole("region", { name: "Governing floor-area ratio" })).toBe(screenPanel);
    expect(screen.queryByRole("region", { name: "Wide-street conditional FAR" })).toBeNull();
    cleanup();

    // Report surface: ReportView embeds the SAME DevelopmentLimits + CalculationEvidence.
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    const reportValue = screen.getByTestId("wide-street-result").textContent;
    const reportPanel = screen.getByTestId("development-wide-street");
    expect(reportPanel).toHaveTextContent("Governing floor-area ratio");
    expect(reportPanel).not.toHaveTextContent("Wide-street conditional FAR");
    // The D-052 provenance heading follows suit — no conditional-FAR heading over
    // the conservative value in the evidence surface either. The report nests the
    // evidence inside a closed <details>, so its heading is outside the a11y tree;
    // hidden:true asserts the heading regardless of the collapsed state. The value
    // caption is read via textContent, which the closed <details> does not affect.
    const provenance = screen.getByTestId("wide-street-provenance");
    expect(within(provenance).getByRole("heading", { name: "Governing floor-area ratio · D-052 provenance", hidden: true })).toBeInTheDocument();
    expect(within(provenance).queryByRole("heading", { name: "Wide-street conditional FAR · D-052 provenance", hidden: true })).toBeNull();
    expect(provenance).toHaveTextContent("Governing floor-area ratio (dimensionless ratio)");
    expect(provenance).not.toHaveTextContent("Wide-street conditional FAR (dimensionless ratio)");

    // Screen and report agree, and both show the conservative value.
    expect(reportValue).toBe(screenValue);
    expect(reportValue).toContain("2.20");
  });

  it("retains the within control: the conditional-FAR caption on both surfaces", () => {
    const profile = baseProfile();
    const doc = wideStreetDoc(profile.identity.bbl); // within_100ft_of_wide_street, 3.44
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    expect(screen.getByTestId("development-wide-street")).toHaveTextContent("Wide-street conditional FAR");
    const provenance = screen.getByTestId("wide-street-provenance");
    expect(within(provenance).getByRole("heading", { name: "Wide-street conditional FAR · D-052 provenance", hidden: true })).toBeInTheDocument();
    expect(provenance).toHaveTextContent("Wide-street conditional FAR (dimensionless ratio)");
    expect(screen.getByTestId("wide-street-result")).toHaveTextContent("3.44");
  });

  it("retains the professional-review control: the withheld value stays the wide-street conditional FAR", () => {
    const profile = baseProfile();
    const doc = docFor(profile.identity.bbl, {
      determination_state: "professional_review_required",
      far_row: "none",
      governing_max_residential_far: null,
    });
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    expect(screen.getByTestId("wide-street-result")).toHaveTextContent("Professional review required");
    expect(within(screen.getByTestId("wide-street-provenance")).getByRole("heading", { name: "Wide-street conditional FAR · D-052 provenance", hidden: true })).toBeInTheDocument();
    expect(screen.queryByText(/3\.44/)).toBeNull();
  });
});
