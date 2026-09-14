import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, fireEvent } from "@testing-library/react";
import { EvidenceRecord } from "../EvidenceRecord";
import { baseProfile } from "@/test-support/fixtures";
import { propertyHref, readWorkspaceView } from "@/lib/architect/navigation";

describe("architect workspace safety", () => {
  it("retains the canonical BBL through every available view", () => {
    expect(propertyHref("1000010010", "evidence")).toBe("/property?ruleeval=on&bbl=1000010010&view=evidence");
    expect(propertyHref("javascript:alert(1)", "facts")).toBe("/property?ruleeval=on");
    expect(readWorkspaceView("made-up")).toBe("overview");
  });
  it("exposes every captured source value and review metadata without unsafe links", () => {
    const profile = baseProfile();
    const record = { ...profile.provenance[0], original_value: "RAW-CAPTURE", normalized_value: "NORMALIZED-CAPTURE", request_url: "javascript:alert(1)", user_confirmed_or_overridden: "overridden" as const };
    render(<EvidenceRecord record={record} profile={profile} />);
    expect(screen.getByText("RAW-CAPTURE")).toBeInTheDocument();
    expect(screen.getByText("NORMALIZED-CAPTURE")).toBeInTheDocument();
    expect(screen.getByText("overridden")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Full captured source record"));
    expect(screen.getByText(/javascript:alert/)).toBeInTheDocument();
    expect(document.querySelector('a[href^="javascript:"]')).toBeNull();
  });
});

afterEach(cleanup);

it("prints a readable brief by default and includes complete audit records only on request", async () => {
  const { ReportView } = await import("../ReportView");
  const print = vi.spyOn(window, "print").mockImplementation(() => undefined);
  render(<ReportView profile={baseProfile()} scenario={null} evaluation={null} label="Test property" />);
  const audit = screen.getByRole("checkbox", { name: "Include full audit appendix" });
  expect(audit).not.toBeChecked();
  fireEvent.click(screen.getByRole("button", { name: "Print property brief" }));
  expect(print).toHaveBeenCalledOnce();
  expect(Array.from(document.querySelectorAll<HTMLDetailsElement>(".architect-raw")).every(item => !item.open)).toBe(true);
  fireEvent(window, new Event("afterprint"));
  fireEvent.click(audit);
  fireEvent.click(screen.getByRole("button", { name: "Print property brief" }));
  expect(document.querySelector(".architect-report")).toHaveClass("includes-audit");
  expect(Array.from(document.querySelectorAll<HTMLDetailsElement>(".architect-raw")).every(item => item.open)).toBe(true);
  fireEvent(window, new Event("afterprint"));
  print.mockRestore();
});
