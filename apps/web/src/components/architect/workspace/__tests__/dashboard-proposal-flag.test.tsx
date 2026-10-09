import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { baseProfile } from "@/test-support/fixtures";
import { deriveCondoSurface } from "../../CondoRecordsSection";
import { DashboardTools, type DashboardToolsProps } from "../DashboardTools";

/**
 * D-01 (plan §7 "not a design tool", RECONCILIATION set-aside #1/#8): with the
 * server flag INTERNAL_PROPOSAL_EDITOR_ENABLED off (the default), the dashboard's
 * proposal and envelope tools — including a `?tool=proposal|envelope` deep link —
 * render the plain not-available view. No editor, no coordinate drawing and no
 * max-envelope request is mounted. The code itself is set aside, not deleted.
 */

vi.mock("@/lib/condo-records", async original => ({
  ...await original<typeof import("@/lib/condo-records")>(),
  useCondoRecords: () => ({ kind: "route_absent", httpStatus: 404 }),
}));
vi.mock("@/components/address/LotOutlineMap", () => ({ LotOutlineMap: () => <div>Map presentation seam</div> }));

/** The generic 404 an unmounted route serves (explicit Content-Length, matching the
 * entry suite's fixture, so the client classifies it as feature_unavailable). */
function notFoundResponse(): Response {
  const text = JSON.stringify({ detail: "Not Found" });
  return new Response(text, { status: 404, headers: { "Content-Type": "application/json", "Content-Length": String(new TextEncoder().encode(text).length) } });
}

let fetchSpy: ReturnType<typeof vi.fn>;
beforeEach(() => {
  fetchSpy = vi.fn(async () => notFoundResponse());
  vi.stubGlobal("fetch", fetchSpy);
});
afterEach(() => vi.unstubAllGlobals());
afterEach(cleanup);

function props(tool: "proposal" | "envelope", proposalEditorEnabled?: boolean): DashboardToolsProps {
  const profile = baseProfile();
  return {
    tool, profile, scenario: null, evaluation: null, returnedScenario: null, returnedEvaluation: null,
    condo: deriveCondoSurface(profile, { kind: "route_absent", httpStatus: 404 }),
    address: null, label: "Test property", selection: "calculation",
    onSelectEvidence: vi.fn(), onInspect: vi.fn(), onOpen: vi.fn(), surveyEnabled: false,
    proposalEditorEnabled,
  };
}

describe("dashboard proposal tool is set aside behind a default-off server flag", () => {
  for (const tool of ["proposal", "envelope"] as const) {
    for (const flag of [undefined, false] as const) {
      it(`renders the not-available view for tool=${tool} when the flag is ${String(flag)}`, () => {
        render(<DashboardTools {...props(tool, flag)}/>);
        expect(screen.getByRole("heading", { name: "Proposal editor is not available in this version" })).toBeInTheDocument();
        expect(screen.queryByTestId("proposal-editor")).not.toBeInTheDocument();
        expect(screen.queryByTestId("max-envelope-panel")).not.toBeInTheDocument();
        expect(screen.queryByLabelText(/^Vertex \d+ X coordinate$/)).not.toBeInTheDocument();
        expect(fetchSpy).not.toHaveBeenCalled();
      });
    }
  }

  it("mounts the editor from the EMPTY draft when the flag is on (never the example rectangle)", async () => {
    render(<DashboardTools {...props("proposal", true)}/>);
    expect(screen.getByTestId("proposal-editor")).toBeInTheDocument();
    expect(screen.queryAllByLabelText(/^Vertex \d+ X coordinate$/)).toHaveLength(0);
    expect(screen.getByLabelText("Proposal label")).toHaveValue("New proposal");
    // Let the stubbed max-envelope request settle (no floating state update).
    await screen.findByTestId("envelope-failure");
  });
});
