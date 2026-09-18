// M5-T037 (D-073-R003): the wide-street conditional FAR must reach BOTH the
// screen and the printed property brief from the SAME validated document, so
// the two surfaces can never disagree. ReportView embeds the SAME
// DevelopmentLimits (the FAR row) and CalculationEvidence (the D-052
// provenance) components the screen uses, so parity is structural — there is no
// second data path. These tests prove it at the surface.
import { cleanup, render, screen } from "@testing-library/react";
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
