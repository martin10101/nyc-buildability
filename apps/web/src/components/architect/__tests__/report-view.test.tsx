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
});
