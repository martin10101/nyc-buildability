import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ConflictsSection } from "@/components/property/ConflictsSection";
import { MissingInputsSection } from "@/components/property/MissingInputsSection";
import { baseProfile } from "@/test-support/fixtures";
import type { Conflict } from "@/lib/property-profile";

afterEach(cleanup);

describe("ConflictsSection (S1/S6)", () => {
  it("shows every conflicting value WITH its source and the unresolved label", () => {
    // SYNTHETIC conflict entry shaped exactly like the accepted M1-T005
    // builder emits for a borocode disagreement (services/api builder
    // _conflicts()); labeled synthetic, no official value invented.
    const conflicts: Conflict[] = [
      {
        field: "borocode",
        values: [
          {
            source_id: "nyc-dcp-pluto-soda",
            value: "1",
            derivation: "derived from the canonical BBL digits",
          },
          {
            source_id: "nyc-dcp-pluto-soda",
            value: "3",
            derivation: "record field 'borocode' verbatim",
          },
        ],
        resolution: "unresolved",
      },
    ];
    render(<ConflictsSection conflicts={conflicts} />);
    expect(screen.getByText(/resolution: unresolved/)).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getAllByText(/nyc-dcp-pluto-soda/).length).toBe(2);
    expect(
      screen.getByText(/Nothing has been resolved automatically/),
    ).toBeInTheDocument();
  });

  it("renders an explicit empty state instead of hiding the section", () => {
    render(<ConflictsSection conflicts={[]} />);
    expect(
      screen.getByText(/No cross-source conflicts were detected/),
    ).toBeInTheDocument();
  });
});

describe("MissingInputsSection (S6 / D3 policy)", () => {
  it("shows the total, surfaces relevant fields, and reveals the grouped rest via the count toggle", () => {
    const entries = baseProfile().missing_inputs;
    render(<MissingInputsSection entries={entries} />);

    // Total always visible in the heading.
    expect(
      screen.getByRole("heading", { name: /Missing official inputs \(24\)/ }),
    ).toBeInTheDocument();

    // Feasibility-relevant entries surfaced immediately.
    expect(screen.getByText("overlay1")).toBeInTheDocument();
    expect(screen.getByText("mih_opt1")).toBeInTheDocument();

    // Administrative entries hidden behind an EXPLICIT count toggle.
    expect(screen.queryByText("basempdate")).toBeNull();
    const toggle = screen.getByRole("button", { name: /more missing fields/ });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(toggle.textContent).toMatch(/\d+ more missing fields/);

    fireEvent.click(toggle);
    expect(screen.getByText("basempdate")).toBeInTheDocument();
    expect(screen.getByText("dcasdate")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Hide \d+ additional missing fields/ }),
    ).toHaveAttribute("aria-expanded", "true");
  });
});
