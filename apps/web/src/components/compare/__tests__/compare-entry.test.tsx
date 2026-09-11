import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CompareEntry } from "@/components/compare/CompareScreen";
import { jsonResponse, preliminaryScenarioBody } from "./scenario-fixtures";

/**
 * `CompareEntry` coverage (task M5-T004 rework; G4 finding 5).
 *
 * Every other Compare test renders `CompareScreen` directly with an injected
 * `fetchImpl`, so the entry component — the thing the route actually mounts —
 * had ZERO coverage: neither bad-param branch, neither copy variant, not its
 * `h1`, and critically not the guarantee that NO REQUEST IS ISSUED for an
 * invalid parameter. The Confirm screen has exactly this test
 * (`confirm-entry.test.tsx`, with `expect(fetchSpy).not.toHaveBeenCalled()`);
 * this mirrors it.
 *
 * `useSearchParams` is mocked per test via this module-scoped variable
 * (URLSearchParams implements the `get` CompareEntry uses), matching the
 * ConfirmEntry test's technique exactly.
 */

let search = "";
vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(search),
}));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("CompareEntry — invalid parameter never reaches the network", () => {
  it("renders an h1 and issues NO request when no bbl parameter is provided", () => {
    search = "";
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);

    render(<CompareEntry />);

    expect(screen.getByTestId("compare-bad-param")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 1, name: "No property selected" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("compare-bad-param")).toHaveTextContent(
      "None was provided",
    );
    // Nothing was compared and nothing was requested.
    expect(fetchSpy).not.toHaveBeenCalled();
    expect(screen.queryByTestId("scenario-result")).toBeNull();
  });

  it("renders an h1 and issues NO request when the bbl parameter is format-invalid", () => {
    search = "bbl=12ab";
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);

    render(<CompareEntry />);

    expect(
      screen.getByRole("heading", { level: 1, name: "No property selected" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("compare-bad-param")).toHaveTextContent(
      "not a valid BBL",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("keeps the internal banner and a way out of the bad-param state", () => {
    search = "";
    vi.stubGlobal("fetch", vi.fn());

    render(<CompareEntry />);

    expect(screen.getByTestId("internal-banner")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Go to property lookup" }),
    ).toHaveAttribute("href", "/property");
  });
});

describe("CompareEntry — a valid parameter mounts the screen and requests once", () => {
  it("passes the canonical BBL through to CompareScreen", async () => {
    search = "bbl=1000477501";
    const fetchSpy = vi.fn(async () =>
      jsonResponse(preliminaryScenarioBody(), 200),
    );
    vi.stubGlobal("fetch", fetchSpy);

    render(<CompareEntry />);

    expect(screen.queryByTestId("compare-bad-param")).toBeNull();
    await screen.findByTestId("scenario-result");
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    // The document's own identity heads the result.
    expect(screen.getByTestId("scenario-heading-bbl")).toHaveTextContent("1000477501");
  });
});
