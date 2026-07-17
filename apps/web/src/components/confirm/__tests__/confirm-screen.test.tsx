import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
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

/**
 * M2-T005 D1 (scenarios S1/S2) on the Confirm screen: outcome arrivals
 * are announced exactly once by the persistent announcer and focus lands
 * on the outcome heading — never body. The announcement/focus mechanism is
 * shared with the Property screen (OutcomeAnnouncer + FailureTitle +
 * data-outcome-heading), where every failure state is exercised
 * parametrically; here representative states prove the Confirm wiring.
 */

function liveRegionsContaining(text: string): Element[] {
  return Array.from(
    document.querySelectorAll('[aria-live], [role="alert"], [role="status"]'),
  ).filter((el) => (el.textContent ?? "").includes(text));
}

describe("ConfirmScreen — a11y announcement + focus (M2-T005 S1/S2)", () => {
  it("announces a failure arrival exactly once and focuses the failure heading", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse({ state: "no_match", bbl: "5999999999", message: "none" }, 404)),
    );
    render(<ConfirmScreen bbl="5999999999" />);
    await screen.findByTestId("state-no-match");

    const announcement =
      "Lookup complete: no property record found in the official dataset.";
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(announcement);
    expect(liveRegionsContaining(announcement)).toHaveLength(1);
    const card = screen.getByTestId("state-no-match");
    expect(card).not.toHaveAttribute("role", "alert");
    expect(card).not.toHaveAttribute("aria-live");

    const headingEl = screen.getByRole("heading", { name: "No property record found" });
    expect(headingEl).toHaveAttribute("data-outcome-heading");
    await waitFor(() => expect(document.activeElement).toBe(headingEl));
    expect(document.activeElement).not.toBe(document.body);
  });

  it("announces the validation-failure arrival exactly once (hardened boundary states announce too)", async () => {
    const broken = baseProfile() as unknown as Record<string, unknown>;
    delete broken.zoning;
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(broken, 200)));
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("state-validation-failure");

    const announcement =
      "Lookup failed: the response did not match the published data contract.";
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(announcement);
    expect(liveRegionsContaining(announcement)).toHaveLength(1);
    await waitFor(() =>
      expect(document.activeElement).toBe(
        screen.getByRole("heading", {
          name: "The response did not match the published data contract",
        }),
      ),
    );
  });

  it("announces success arrival exactly once and focuses the identity heading", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(baseProfile(), 200)));
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("confirm-card");

    const announcement =
      "Lookup complete: official property profile loaded for BBL 1000010010.";
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(announcement);
    expect(liveRegionsContaining("profile loaded for BBL 1000010010")).toHaveLength(1);

    const headingEl = screen.getByRole("heading", { name: "BBL 1000010010" });
    expect(headingEl).toHaveAttribute("data-outcome-heading");
    await waitFor(() => expect(document.activeElement).toBe(headingEl));
  });

  it("retry: focuses the loading card (never body), clears the announcement, then focuses the new outcome heading", async () => {
    let resolveSecond: ((response: Response) => void) | undefined;
    const fetchStub = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ state: "source_unavailable", message: "outage" }, 503),
      )
      .mockImplementationOnce(
        () => new Promise<Response>((resolve) => (resolveSecond = resolve)),
      );
    vi.stubGlobal("fetch", fetchStub);
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("state-source_unavailable");

    fireEvent.click(screen.getByRole("button", { name: "Retry lookup" }));
    const loading = await screen.findByTestId("loading-stages");
    await waitFor(() => expect(document.activeElement).toBe(loading));
    expect(document.activeElement).not.toBe(document.body);
    expect(screen.getByTestId("outcome-announcer").textContent).toBe("");

    resolveSecond?.(jsonResponse(baseProfile(), 200));
    await screen.findByTestId("confirm-card");
    expect(screen.getByTestId("outcome-announcer")).toHaveTextContent(
      "profile loaded for BBL 1000010010",
    );
    await waitFor(() =>
      expect(document.activeElement).toBe(
        screen.getByRole("heading", { name: "BBL 1000010010" }),
      ),
    );
  });
});

describe("ConfirmScreen — D4: landmark/flood flags render exactly once (M2-T005 S3)", () => {
  it("keeps flag values in the dedicated flags section and filters them from the zoning table", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(baseProfile(), 200)));
    render(<ConfirmScreen bbl="1000010010" />);
    await screen.findByTestId("confirm-card");

    // The flags section keeps the official values (with honest unknowns).
    const flags = screen.getByTestId("confirm-flags");
    expect(flags).toHaveTextContent("INDIVIDUAL LANDMARK");
    expect(flags).toHaveTextContent("Governors Island Historic District");

    // The zoning mapped-features table no longer repeats them, states
    // where they live, and keeps its non-flag features.
    const zoning = screen.getByTestId("zoning-section");
    expect(zoning).not.toHaveTextContent("INDIVIDUAL LANDMARK");
    expect(zoning).not.toHaveTextContent("2007 FIRM flood flag");
    expect(zoning).toHaveTextContent("Mapped features");
    expect(zoning).toHaveTextContent("each official value is shown once");
    expect(zoning).toHaveTextContent("Zoning map");

    // Each flag label appears exactly once as a row label on the screen.
    expect(screen.getAllByText("Landmark", { exact: true })).toHaveLength(1);
    expect(screen.getAllByText("Historic district", { exact: true })).toHaveLength(1);
    expect(screen.getAllByText("2007 FIRM flood flag", { exact: true })).toHaveLength(1);
    expect(
      screen.getAllByText("2015 preliminary FIRM flood flag", { exact: true }),
    ).toHaveLength(1);
  });
});
