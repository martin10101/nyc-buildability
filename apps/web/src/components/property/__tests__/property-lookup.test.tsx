import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PropertyLookup } from "@/components/property/PropertyLookup";
import { baseProfile, jsonResponse, partialProfile } from "@/test-support/fixtures";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function submitBbl(value: string) {
  fireEvent.change(screen.getByLabelText("BBL"), { target: { value } });
  fireEvent.click(screen.getByRole("button", { name: "Look up property" }));
}

describe("PropertyLookup — client validation before network (S3)", () => {
  it("shows a validation message for '1-00001-0100' and never calls fetch", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<PropertyLookup />);
    submitBbl("1-00001-0100");
    expect(await screen.findByTestId("client-validation-error")).toHaveTextContent(
      "digits only",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("shows a length message for '123' and never calls fetch", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<PropertyLookup />);
    submitBbl("123");
    expect(await screen.findByTestId("client-validation-error")).toHaveTextContent(
      "exactly 10 digits",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});

describe("PropertyLookup — profile rendering (S1/S2)", () => {
  it("renders the split-zone profile: districts, units, coverage wording, counts", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(baseProfile(), 200)),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");

    // Identity and both split-zone districts visible. (getAllByText:
    // district codes also appear inside their provenance drill-downs.)
    expect(screen.getByText("BBL 1000010010")).toBeInTheDocument();
    expect(screen.getAllByText("R3-2").length).toBeGreaterThan(0);
    expect(screen.getAllByText("C4-1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("GI").length).toBeGreaterThan(0);

    // Fact value with units (lotarea 7,577,714 square feet).
    expect(screen.getAllByText("7,577,714").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/square feet/).length).toBeGreaterThan(0);

    // Coverage labels use the exact PRD section 12 enum wording.
    expect(screen.getAllByText("conditional").length).toBeGreaterThan(0);

    // data_completeness banner shows the exact enum value. M2-T004 corrected
    // the completeness basis (documented 19-column feasibility set replaces the
    // 108-column denominator), so the F05 ground-truth fixture now reads
    // "complete" (G1/G3 correction C1/D1, orchestrator-authorized).
    expect(screen.getByTestId("completeness-banner")).toHaveTextContent(
      "complete",
    );

    // Missing inputs: total count always visible (fixture has 24 entries).
    expect(
      screen.getByRole("heading", { name: /Missing official inputs \(24\)/ }),
    ).toBeInTheDocument();

    // No conflicts in this profile -> explicit empty state, never hidden.
    expect(
      screen.getByText(/No cross-source conflicts were detected/),
    ).toBeInTheDocument();

    // Honesty: no status badge claims "verified" and "best" appears nowhere.
    expect(document.body.textContent).not.toMatch(/\bbest\b/i);
    expect(document.querySelector(".status-verified")).toBeNull();
  });

  it("tolerates absent identity.address and geometry (S6 partial data)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse(partialProfile(), 200)),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("profile-view");
    expect(
      screen.getByText(/No address could be stated for this lot/),
    ).toBeInTheDocument();
  });
});

describe("PropertyLookup — failure states and retry (S5)", () => {
  it("renders a typed 503 state and recovers via Retry", async () => {
    const fetchStub = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ state: "source_unavailable", message: "outage" }, 503),
      )
      .mockResolvedValueOnce(jsonResponse(baseProfile(), 200));
    vi.stubGlobal("fetch", fetchStub);
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-source_unavailable");
    expect(screen.getByText(/Retrying is safe/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Retry lookup" }));
    await screen.findByTestId("profile-view");
    expect(fetchStub).toHaveBeenCalledTimes(2);
  });

  it("renders the generic 500 state with its correlation id", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(
          { state: "internal_error", message: "generic" },
          500,
          "corr-internal-1",
        ),
      ),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-internal-error");
    expect(screen.getByTestId("correlation-id")).toHaveTextContent("corr-internal-1");
  });

  it("renders the recoverable network-failure state when fetch throws", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("fetch failed");
      }),
    );
    render(<PropertyLookup />);
    submitBbl("1000010010");
    await screen.findByTestId("state-network-error");
    expect(screen.getByRole("button", { name: "Retry lookup" })).toBeInTheDocument();
  });

  it("renders 422 detail.code when the server rejects a BBL the client allowed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(
          {
            state: "validation_error",
            message: "BBL tax block must be 1-99999; got '00000'",
            detail: { code: "invalid_block", raw_value: "'1000000000'" },
          },
          422,
        ),
      ),
    );
    render(<PropertyLookup />);
    submitBbl("1000000000"); // passes the client mirror (documented gap)
    await screen.findByTestId("state-validation-error");
    expect(screen.getByTestId("validation-code")).toHaveTextContent("invalid_block");
    expect(screen.getByTestId("validation-message")).toHaveTextContent("tax block");
  });
});

describe("PropertyLookup — honesty affordances (S7)", () => {
  it("shows the disabled address entry with honest copy", () => {
    vi.stubGlobal("fetch", vi.fn());
    render(<PropertyLookup />);
    const addressInput = screen.getByLabelText(/Address \(not yet available\)/);
    expect(addressInput).toBeDisabled();
    expect(screen.getByTestId("address-disabled-copy")).toHaveTextContent(
      "credentials are still pending",
    );
  });
});
