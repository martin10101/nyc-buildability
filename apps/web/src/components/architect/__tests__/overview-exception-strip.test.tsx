import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import type { PropertyProfile } from "@/lib/contract";
import { fieldLabel } from "@/lib/format";
import { propertyHref } from "@/lib/architect/navigation";
import { draftApplicableDoc } from "@/test-support/rule-evaluation-fixtures";
import { OverviewExceptionStrip } from "../OverviewExceptionStrip";
import { PropertyOverview } from "../PropertyOverview";
import { AnalysisIdentityNotice } from "../AnalysisIdentityNotice";
import { IncompleteEvaluationNotice } from "../DevelopmentLimits";

// The map is a presentation seam here; PropertyOverview renders it inside the canvas.
vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));
afterEach(cleanup);

/** Push one unresolved conflict onto a mutable profile (mirrors the shape the
 * accepted development-limits.test.tsx uses). Returns the conflicting field. */
function withConflict(profile: PropertyProfile, field = "lotarea"): string {
  profile.conflicts.push({
    field,
    resolution: "unresolved",
    values: [{ source_id: "nyc-dcp-pluto-soda", value: 3 }, { source_id: "another-source", value: 4 }],
  });
  return field;
}
/** Promote an existing (validly-shaped) missing input to critical. */
function withCriticalMissing(profile: PropertyProfile): string {
  const entry = profile.missing_inputs[0];
  entry.criticality = "critical";
  return entry.field;
}
/** Flag the property source stale (only .staleness.stale is read). */
function withStale(profile: PropertyProfile): void {
  profile.reproducibility = {
    ...(profile.reproducibility ?? {}),
    staleness: { stale: true },
  } as unknown as PropertyProfile["reproducibility"];
}

describe("OverviewExceptionStrip — AS-1: one strip, only ACTIVE issues", () => {
  it("renders NOTHING and no status region when no issue is active (no empty strip)", () => {
    // baseProfile has no unresolved conflict, no critical missing input, not stale.
    render(<OverviewExceptionStrip profile={baseProfile()} />);
    expect(screen.queryByTestId("overview-exception-strip")).toBeNull();
    // Absent-state of the aria region: no role=status "Active issues" exists.
    expect(screen.queryByRole("status", { name: "Active issues" })).toBeNull();
  });

  it("surfaces an unresolved conflict with its fields, the blocked effect and the preserved link", () => {
    const profile = baseProfile();
    const field = withConflict(profile);
    render(<OverviewExceptionStrip profile={profile} />);
    const strip = screen.getByTestId("overview-exception-strip");
    // Present-state of the aria region: exactly this role=status carries the name.
    expect(screen.getByRole("status", { name: "Active issues" })).toBe(strip);
    const row = within(strip).getByTestId("exception-issue-conflict");
    expect(row).toHaveTextContent("Unresolved data conflicts");
    expect(row).toHaveTextContent(fieldLabel(field));
    expect(row).toHaveTextContent("a reliable value is withheld until the conflict is reviewed");
    const link = within(row).getByRole("link", { name: "Review conflicting source values →" });
    expect(link).toHaveAttribute("href", propertyHref(profile.identity.bbl, "issues"));
  });

  it("surfaces a critical missing input with its field, the blocked effect and the preserved link", () => {
    const profile = baseProfile();
    const field = withCriticalMissing(profile);
    render(<OverviewExceptionStrip profile={profile} />);
    const row = screen.getByTestId("exception-issue-missing");
    expect(row).toHaveTextContent("Critical inputs missing");
    expect(row).toHaveTextContent(fieldLabel(field));
    expect(row).toHaveTextContent("cannot be relied on until they are supplied");
    expect(within(row).getByRole("link", { name: "Review missing inputs →" })).toHaveAttribute(
      "href",
      propertyHref(profile.identity.bbl, "issues"),
    );
  });

  it("surfaces a stale source keeping the exact stale sentence plus a review clause, no link", () => {
    const profile = baseProfile();
    withStale(profile);
    render(<OverviewExceptionStrip profile={profile} />);
    const row = screen.getByTestId("exception-issue-stale");
    // The exact wording that already prints in the brief is preserved verbatim.
    expect(row).toHaveTextContent(
      "The property source is stale. Captured dates and retrieval status are available in Evidence.",
    );
    expect(row).toHaveTextContent("Review the retrieval dates before relying on these figures.");
    expect(within(row).queryByRole("link")).toBeNull();
  });

  it("folds all three active issues into ONE role=status region (one strip, not three)", () => {
    const profile = baseProfile();
    withConflict(profile);
    withCriticalMissing(profile);
    withStale(profile);
    render(<OverviewExceptionStrip profile={profile} />);
    expect(screen.getAllByTestId("overview-exception-strip")).toHaveLength(1);
    // Exactly one status region for the event (A04: one strip = one status region).
    expect(screen.getAllByRole("status", { name: "Active issues" })).toHaveLength(1);
    const strip = screen.getByTestId("overview-exception-strip");
    expect(within(strip).getByTestId("exception-issue-conflict")).toBeInTheDocument();
    expect(within(strip).getByTestId("exception-issue-missing")).toBeInTheDocument();
    expect(within(strip).getByTestId("exception-issue-stale")).toBeInTheDocument();
  });

  it("shows only the active rows and omits the inactive ones", () => {
    const profile = baseProfile();
    withCriticalMissing(profile); // only critical missing is active
    render(<OverviewExceptionStrip profile={profile} />);
    expect(screen.getByTestId("exception-issue-missing")).toBeInTheDocument();
    expect(screen.queryByTestId("exception-issue-conflict")).toBeNull();
    expect(screen.queryByTestId("exception-issue-stale")).toBeNull();
  });
});

describe("OverviewExceptionStrip — AS-1 boundary: identity/incomplete are NOT folded", () => {
  it("identity mismatch stays a role=alert AnalysisIdentityNotice and never enters the role=status strip", () => {
    // The dedicated identity surface keeps role=alert (ledger A15 / KEY RULE).
    render(
      <AnalysisIdentityNotice
        label="Rule evaluation"
        requestedBbl="1000010010"
        document={{ evaluated_input: { bbl: "5000010001" } }}
      />,
    );
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Results are withheld from this property.");
    expect(alert).toHaveTextContent("Requested BBL 1000010010; returned BBL 5000010001.");
    // The status strip does not name identity mismatch (a clean profile → no strip),
    // so folding never downgrades the alert to a status region.
    render(<OverviewExceptionStrip profile={baseProfile()} />);
    expect(screen.queryByTestId("overview-exception-strip")).toBeNull();
  });

  it("incomplete assessment stays a role=status IncompleteEvaluationNotice, not a strip row", () => {
    const evaluation = draftApplicableDoc();
    // Make it non-inspectable (A05 branch): a trace missing its outputs.
    delete (evaluation.evaluations[0] as unknown as Record<string, unknown>).outputs;
    render(<IncompleteEvaluationNotice evaluation={evaluation} />);
    const status = screen.getByRole("status");
    expect(status).toHaveTextContent("Rule details incomplete");
    expect(status).toHaveTextContent("Numerical summaries are unavailable. The returned record is preserved below.");
    // The exception strip has no incomplete-assessment row (a clean profile → none).
    render(<OverviewExceptionStrip profile={baseProfile()} />);
    expect(screen.queryByTestId("exception-issue-incomplete")).toBeNull();
  });
});

describe("OverviewExceptionStrip — AS-1 integration on the overview surface", () => {
  it("PropertyOverview shows the ONE strip and NO legacy separate alert blocks when issues are active", () => {
    const profile = baseProfile();
    withConflict(profile);
    withCriticalMissing(profile);
    render(<PropertyOverview profile={profile} scenario={null} evaluation={null} onInspect={vi.fn()} />);
    const strip = screen.getByTestId("overview-exception-strip");
    expect(within(strip).getByTestId("exception-issue-conflict")).toBeInTheDocument();
    expect(within(strip).getByTestId("exception-issue-missing")).toBeInTheDocument();
    // The former two separate `.architect-alert` role=status blocks (PropertyIssuesSummary)
    // are folded away on the overview — none remain.
    expect(document.querySelectorAll<HTMLElement>(".architect-alert")).toHaveLength(0);
    // The conflict heading appears exactly once (in the strip), never duplicated.
    expect(screen.getAllByText("Unresolved data conflicts")).toHaveLength(1);
  });

  it("PropertyOverview renders no strip for a clean profile", () => {
    render(<PropertyOverview profile={baseProfile()} scenario={null} evaluation={null} onInspect={vi.fn()} />);
    expect(screen.queryByTestId("overview-exception-strip")).toBeNull();
  });
});
