import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ConfirmEntry } from "@/components/confirm/ConfirmScreen";

/**
 * M2-T005 D3 (scenario S3): the confirm-bad-param state must render an h1
 * — in that state the "Step 2" header never mounts, so without one the
 * page's heading hierarchy started at level 2 (visual-quality Minor D3).
 *
 * `useSearchParams` is mocked per test via this module-scoped variable
 * (URLSearchParams implements the `get` used by ConfirmEntry).
 */

let search = "";
vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(search),
}));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("ConfirmEntry — bad-param state heading hierarchy (D3)", () => {
  it("renders an h1 when no bbl parameter is provided", () => {
    search = "";
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy); // must never be called in this state
    render(<ConfirmEntry />);
    expect(screen.getByTestId("confirm-bad-param")).toBeInTheDocument();
    const h1 = screen.getByRole("heading", { level: 1, name: "No property selected" });
    expect(h1).toBeInTheDocument();
    expect(screen.getByTestId("confirm-bad-param")).toHaveTextContent(
      "None was provided",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("renders an h1 when the bbl parameter is format-invalid", () => {
    search = "bbl=12ab";
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<ConfirmEntry />);
    expect(
      screen.getByRole("heading", { level: 1, name: "No property selected" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("confirm-bad-param")).toHaveTextContent(
      "not a valid BBL",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
