import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ConfirmScreen } from "@/components/confirm/ConfirmScreen";
import {
  baseProfile,
  cr500NoMatchResponse,
  jsonResponse,
} from "@/test-support/fixtures";

/**
 * Confirm screen (PRODUCT_FLOW step 2) component journeys: compact card
 * sections, honest unknown/persistence labeling, questions limited to what
 * official data cannot answer, and the SAME hardened client boundary as
 * the Property screen (the recorded 500+no_match fixture can never render
 * as a no-match result here either).
 */

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("ConfirmScreen — compact property card (S1)", () => {
  it("renders identity, lot summary, building, zoning, flags, conflicts, legend, and questions", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(baseProfile(), 200)),
    );
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("confirm-card");

    // Identity with canonical address and honest BIN/geometry statements.
    expect(screen.getByTestId("confirm-identity")).toHaveTextContent("BBL 1000010010");
    expect(screen.getByTestId("confirm-identity")).toHaveTextContent("140 CARDER ROAD");
    expect(screen.getByTestId("confirm-bin")).toHaveTextContent("Not yet retrieved");

    // Lot summary with units and labels (no raw column names).
    expect(screen.getByTestId("confirm-lot")).toHaveTextContent("Lot area");
    expect(screen.getByTestId("confirm-lot")).toHaveTextContent("7,577,714");
    expect(screen.getByTestId("confirm-lot")).toHaveTextContent("square feet");

    // Existing building facts.
    expect(screen.getByTestId("confirm-building")).toHaveTextContent("Number of floors");

    // Zoning: both split-zone districts and the special district.
    expect(screen.getAllByText("R3-2").length).toBeGreaterThan(0);
    expect(screen.getAllByText("C4-1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("GI").length).toBeGreaterThan(0);

    // Flags: landmark value present in the F05 capture; pending actions
    // honestly declared unretrievable.
    expect(screen.getByTestId("confirm-flags")).toHaveTextContent("INDIVIDUAL LANDMARK");
    expect(screen.getByTestId("confirm-pending-flag")).toHaveTextContent(
      "no official connector",
    );

    // Conflicts stay visible (explicit empty state) and legend is present.
    expect(screen.getByText(/No cross-source conflicts were detected/)).toBeInTheDocument();
    expect(screen.getByTestId("coverage-legend")).toBeInTheDocument();
  });

  it("asks ONLY questions official data cannot answer, with honest persistence labeling (S7)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(baseProfile(), 200)),
    );
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("confirm-card");

    const questions = screen.getByTestId("confirm-questions");
    // The F05 profile has no critical gap and no conflict: the only
    // question is development intent (not a government fact).
    expect(questions).toHaveTextContent("What do you intend to build or change?");
    expect(screen.getByTestId("questions-empty-note")).toHaveTextContent(
      "no critical gap and no unresolved conflict",
    );

    // NO pretend persistence: the affordance is disabled and says so.
    expect(screen.getByTestId("confirm-disabled-button")).toBeDisabled();
    expect(screen.getByTestId("confirm-persistence-note")).toHaveTextContent(
      "cannot be saved yet",
    );
    expect(screen.getByTestId("confirm-persistence-note")).toHaveTextContent(
      "no fact has been auto-confirmed",
    );

    // Honesty: no "best"/"verified" wording and no verified badge.
    expect(document.querySelector(".status-badge.status-verified")).toBeNull();
    expect(document.body.textContent).not.toMatch(/\bbest\b/i);
  });

  it("surfaces critical gaps and unresolved conflicts as questions when present", async () => {
    const profile = baseProfile();
    profile.missing_inputs.push({
      field: "lotarea",
      criticality: "critical",
      reason: "column absent from the SODA record",
    });
    profile.conflicts.push({
      field: "borocode",
      values: [
        { source_id: "nyc-dcp-pluto-soda", value: "1" },
        { source_id: "nyc-dcp-pluto-soda", value: "3" },
      ],
      resolution: "unresolved",
    });
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(profile, 200)),
    );
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("confirm-card");

    const questions = screen.getByTestId("confirm-questions");
    expect(questions).toHaveTextContent("Can you provide Lot area?");
    expect(questions).toHaveTextContent("Which value of Borough code is correct?");
    expect(screen.queryByTestId("questions-empty-note")).toBeNull();
  });
});

describe("ConfirmScreen — hardened boundary (S2/S3 apply here too)", () => {
  it("renders unexpected_response for the recorded 500+no_match fixture, never no-match", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => cr500NoMatchResponse()),
    );
    render(<ConfirmScreen bbl="5999999999" />);
    await screen.findByTestId("state-unexpected-response");
    expect(screen.queryByTestId("state-no-match")).toBeNull();
    expect(screen.queryByTestId("confirm-card")).toBeNull();
  });

  it("renders the validation-failure state for a malformed 200 (nothing partially rendered)", async () => {
    const broken = baseProfile() as unknown as Record<string, unknown>;
    delete broken.zoning;
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(broken, 200)),
    );
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("state-validation-failure");
    expect(screen.queryByTestId("confirm-card")).toBeNull();
    expect(screen.queryByText("7,577,714")).toBeNull();
  });

  it("renders a recoverable failure state with a way back for a typed 503", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse({ state: "source_unavailable", message: "outage" }, 503)),
    );
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("state-source_unavailable");
    expect(screen.getByRole("button", { name: "Retry lookup" })).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", { name: /Back to property lookup/ }).length,
    ).toBeGreaterThan(0);
  });
});
