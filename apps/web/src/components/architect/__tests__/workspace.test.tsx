import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, fireEvent, within } from "@testing-library/react";
import { ArchitectShell } from "../ArchitectShell";
import { EvidenceRecord } from "../EvidenceRecord";
import { baseProfile } from "@/test-support/fixtures";
import { propertyHref, readWorkspaceView } from "@/lib/architect/navigation";
import { draftApplicableDoc, unsupportedDoc } from "@/test-support/rule-evaluation-fixtures";
import { CalculationEvidence } from "../CalculationEvidence";

describe("architect workspace safety", () => {
  it("retains the canonical BBL through every available view", () => {
    expect(propertyHref("1000010010", "evidence")).toBe("/property?ruleeval=on&bbl=1000010010&view=evidence");
    expect(propertyHref("javascript:alert(1)", "facts")).toBe("/property?ruleeval=on");
    expect(readWorkspaceView("made-up")).toBe("overview");
  });
  it("routes the additive proposal view without disturbing the existing views", () => {
    expect(readWorkspaceView("proposal")).toBe("proposal");
    expect(propertyHref("1000010010", "proposal")).toBe("/property?ruleeval=on&bbl=1000010010&view=proposal");
    expect(readWorkspaceView("made-up")).toBe("overview");
  });
  it("exposes every captured source value and review metadata without unsafe links", () => {
    const profile = baseProfile();
    const record = { ...profile.provenance[0], original_value: "RAW-CAPTURE", normalized_value: "NORMALIZED-CAPTURE", request_url: "javascript:alert(1)", user_confirmed_or_overridden: "overridden" as const, conflict_status: "conflicting" as const };
    profile.user_confirmations = [{ field: record.original_field_name, action: "overridden", override_value: "REVIEWED-CAPTURE", confirmed_by: "Synthetic reviewer", confirmed_at: "2026-09-15T01:00:00Z" }];
    render(<EvidenceRecord record={record} profile={profile} />);
    expect(screen.getByText("RAW-CAPTURE")).toBeInTheDocument();
    expect(screen.getByText("NORMALIZED-CAPTURE")).toBeInTheDocument();
    expect(screen.getByText("overridden")).toBeInTheDocument();
    expect(screen.getByText("conflicting")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Review history"));
    const history = screen.getByText("Recorded confirmations and overrides").closest("details")!.querySelector("pre")!;
    expect(JSON.parse(history.textContent!)).toEqual(profile.user_confirmations);
    fireEvent.click(screen.getByText("Full captured source record"));
    expect(screen.getByText(/javascript:alert/)).toBeInTheDocument();
    expect(document.querySelector('a[href^="javascript:"]')).toBeNull();
  });
  it("shows the applicable determination first and keeps other determinations expandable", () => {
    const evaluation = draftApplicableDoc();
    const other = unsupportedDoc().evaluations[0];
    other.rule_id = "other-recorded-determination";
    evaluation.evaluations.unshift(other);
    render(<CalculationEvidence evaluation={evaluation} scenario={null}/>);
    const determinations = document.querySelectorAll<HTMLDetailsElement>(".architect-determination");
    expect(determinations).toHaveLength(2);
    expect(determinations[0].open).toBe(true);
    expect(determinations[0].querySelector("summary")).toHaveTextContent("Applicable determination · r5-residential-far");
    expect(determinations[1].open).toBe(false);
    fireEvent.click(determinations[1].querySelector("summary")!);
    expect(determinations[1].open).toBe(true);
    expect(determinations[1]).toHaveTextContent("Full evaluation trace");
    expect(evaluation.evaluations[0].rule_id).toBe("other-recorded-determination");
  });
});

afterEach(cleanup);

it("prints a readable brief by default and includes complete audit records only on request", async () => {
  const { ReportView } = await import("../ReportView");
  const print = vi.spyOn(window, "print").mockImplementation(() => undefined);
  const profile = baseProfile();
  profile.zoning.mapped_features = [];
  render(<ReportView profile={profile} scenario={null} evaluation={null} label="Test property" />);
  const audit = screen.getByRole("checkbox", { name: "Include full audit appendix" });
  expect(audit).not.toBeChecked();
  const facts = document.getElementById("brief-facts") as HTMLDetailsElement;
  const sources = document.getElementById("brief-sources") as HTMLDetailsElement;
  expect(facts.open).toBe(false);
  expect(sources.open).toBe(false);
  fireEvent.click(screen.getByRole("button", { name: "Print property brief" }));
  expect(print).toHaveBeenCalledOnce();
  expect(facts.open).toBe(true);
  expect(sources.open).toBe(true);
  const zoning = document.getElementById("brief-zoning")!;
  for (const label of ["Landmark", "Historic district", "2007 FIRM flood flag", "2015 preliminary FIRM flood flag", "Pending land-use actions"]) expect(zoning).toHaveTextContent(label);
  expect(zoning).toHaveTextContent("Unknown — not supplied");
  expect(Array.from(document.querySelectorAll<HTMLDetailsElement>(".architect-raw")).every(item => !item.open)).toBe(true);
  fireEvent(window, new Event("afterprint"));
  expect(facts.open).toBe(false);
  expect(sources.open).toBe(false);
  fireEvent(window, new Event("beforeprint"));
  expect(facts.open).toBe(true);
  fireEvent(window, new Event("afterprint"));
  fireEvent.click(audit);
  fireEvent.click(screen.getByRole("button", { name: "Print property brief" }));
  expect(document.querySelector(".architect-report")).toHaveClass("includes-audit");
  expect(Array.from(document.querySelectorAll<HTMLDetailsElement>(".architect-raw")).every(item => item.open)).toBe(true);
  fireEvent(window, new Event("afterprint"));
  print.mockRestore();
});

/* M5-T119 (D-086 P3a, DB-087 g / DISC-P2-1, ledger A01/A03): the shell carries a
 * phone-width environment + professional-review strip on LOADED surfaces (its CSS
 * visibility is proven at 360px by the responsive-a11y e2e; jsdom applies no media
 * queries, so these assert DOM presence + search-surface gating). */
describe("M5-T119 — shell phone-width environment + review strip", () => {
  afterEach(cleanup);
  it("renders the environment restriction note and the review line on a loaded surface", () => {
    render(<ArchitectShell bbl="1000010010" active="overview"><p>Workspace child</p></ArchitectShell>);
    const strip = screen.getByTestId("shell-environment");
    // role=note carries the restriction meaning as text, never colour alone.
    expect(strip).toHaveAttribute("role", "note");
    expect(within(strip).getByText("Internal build")).toBeInTheDocument();
    expect(strip).toHaveTextContent("No sign-in or access control yet");
    expect(strip).toHaveTextContent("nothing here is a legal determination");
    expect(strip).toHaveTextContent("do not share outside the engineering team");
    const review = within(strip).getByTestId("shell-review");
    expect(review).toHaveTextContent("professional review required");
    // The strip reuses the accepted M5-T115 paraphrase and does NOT add a second
    // internal-banner region (the topbar keeps the only one).
    expect(within(strip).queryByTestId("internal-banner")).toBeNull();
  });

  it("does NOT render the shell environment strip on the search surface (no double with the search strip)", () => {
    render(<ArchitectShell active="search"><p>Search child</p></ArchitectShell>);
    expect(screen.queryByTestId("shell-environment")).toBeNull();
    expect(screen.queryByTestId("shell-review")).toBeNull();
  });

  it("keeps the desktop topbar environment disclosure untouched on a loaded surface", () => {
    render(<ArchitectShell bbl="1000010010" active="overview"><p>Workspace child</p></ArchitectShell>);
    // The topbar `.architect-environment` details still exists (desktop carrier).
    expect(document.querySelector(".architect-environment")).not.toBeNull();
  });
});
