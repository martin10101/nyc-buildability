import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ConflictsSection } from "@/components/property/ConflictsSection";
import { MissingInputsSection } from "@/components/property/MissingInputsSection";
import { baseProfile } from "@/test-support/fixtures";
import type { Conflict } from "@/lib/contract";

afterEach(cleanup);

describe("ConflictsSection (S1/S6)", () => {
  it("shows every conflicting value WITH its source and the unresolved label", () => {
    // SYNTHETIC conflict entry shaped exactly like the accepted M1-T005
    // builder emits for a borocode disagreement (services/api builder
    // _conflicts()); labeled synthetic, no official value invented.
    // `derivation` is an OPEN-schema key the builder emits (not documented
    // in the generated conflict-value type) — the cast mirrors how it
    // arrives over the wire; the component reads it via the runtime
    // narrowing helper in src/lib/contract.ts.
    const conflicts = [
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
    ] as unknown as Conflict[];
    render(<ConflictsSection conflicts={conflicts} />);
    expect(screen.getByText(/resolution: unresolved/)).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getAllByText(/nyc-dcp-pluto-soda/).length).toBe(2);
    expect(screen.getByText(/derived from the canonical BBL digits/)).toBeInTheDocument();
    expect(screen.getByText(/record field 'borocode' verbatim/)).toBeInTheDocument();
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

describe("MissingInputsSection (S6 / D3 policy + M2-T002 D1/D4)", () => {
  it("shows the total, surfaces relevant fields WITH human labels, and reveals the grouped rest via the count toggle", () => {
    const entries = baseProfile().missing_inputs;
    render(<MissingInputsSection entries={entries} />);

    // Total always visible in the heading.
    expect(
      screen.getByRole("heading", { name: /Missing official inputs \(24\)/ }),
    ).toBeInTheDocument();

    // Feasibility-relevant entries surfaced immediately, labeled (D1):
    // no raw PLUTO column name reaches the user.
    expect(screen.getByText("Commercial overlay 1")).toBeInTheDocument();
    expect(
      screen.getByText("Mandatory Inclusionary Housing option 1"),
    ).toBeInTheDocument();
    expect(screen.queryByText("overlay1")).toBeNull();
    expect(screen.queryByText("mih_opt1")).toBeNull();

    // Administrative entries hidden behind an EXPLICIT count toggle.
    expect(screen.queryByText("Input data vintage (base map)")).toBeNull();
    const toggle = screen.getByRole("button", { name: /more missing fields/ });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(toggle.textContent).toMatch(/\d+ more missing fields/);

    fireEvent.click(toggle);
    expect(screen.getByText("Input data vintage (base map)")).toBeInTheDocument();
    expect(screen.getByText("Input data vintage (DCAS)")).toBeInTheDocument();
    expect(screen.queryByText("basempdate")).toBeNull();
    expect(
      screen.getByRole("button", { name: /Hide \d+ additional missing fields/ }),
    ).toHaveAttribute("aria-expanded", "true");
  });

  it("D4: states the shared boilerplate reason ONCE and keeps per-field exceptions inline", () => {
    const shared =
      "column absent from the SODA record (null-omission semantics): " +
      "the value is unknown for this tax lot and is never fabricated";
    const entries = baseProfile().missing_inputs.map((entry) => ({ ...entry }));
    // Give one entry a DIFFERENT reason (per-field exception).
    const exception = entries.find((entry) => entry.field === "overlay1");
    if (!exception) throw new Error("fixture is missing overlay1");
    exception.reason = "numfloors_not_available: official dictionary p.28 rule";
    render(<MissingInputsSection entries={entries} />);

    // Shared reason appears exactly once, in the section-level note.
    expect(screen.getByTestId("shared-missing-reason")).toHaveTextContent(
      "null-omission semantics",
    );
    expect(screen.getAllByText(new RegExp("null-omission semantics")).length).toBe(1);

    // The exception's own reason stays visible inline.
    expect(screen.getByText(/official dictionary p\.28 rule/)).toBeInTheDocument();
    expect(entries.filter((entry) => entry.reason === shared).length).toBeGreaterThan(0);
  });
});
