import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { ProposalEditor } from "../ProposalEditor";
import { attestedReportBody, checkResponse, stubFetch } from "@/test-support/proposal-check-fixtures";

/**
 * Task M5-T060, editor container: the keyboard-first numeric draft flow (add /
 * edit / delete vertex + level + wall), the run-check that renders the AS-1
 * arithmetic, client-side mirror validation that blocks a bad draft NAMING the
 * route constant without sending, client-local variations + compare, and the
 * grep proof that the packet carries no dangerouslySetInnerHTML and no scenario
 * contract_version token (D-076-R002 / AS-4).
 */

vi.mock("@/components/address/LotOutlineMap", () => ({
  LotOutlineMap: () => <div>Map presentation seam</div>,
}));

const stub = () => stubFetch(checkResponse(attestedReportBody(), 200));

describe("ProposalEditor", () => {
  it("edits the numeric draft, runs a check, renders the AS-1 arithmetic, and saves an ephemeral variation", async () => {
    render(<ProposalEditor bbl="1000010010" fetchImpl={stub()} />);
    expect(screen.getByTestId("editor-honesty")).toHaveTextContent("not a city record");

    fireEvent.click(screen.getByRole("button", { name: "Add vertex" }));
    fireEvent.change(screen.getByLabelText("Vertex 0 X coordinate"), { target: { value: "1000000" } });
    fireEvent.click(screen.getByRole("button", { name: "Add level" }));
    fireEvent.click(screen.getByRole("button", { name: "Add wall" }));

    fireEvent.click(screen.getByTestId("run-check"));
    expect(await screen.findByTestId("proposal-check-summary")).toHaveTextContent("1 did not meet an allowance");
    expect(screen.getByTestId("shortfall-lot_coverage_ratio")).toHaveTextContent(
      "0.625 ratio provided; 0.5 ratio required; 0.125 ratio short",
    );
    expect(screen.getByTestId("proposal-check-announcer")).toHaveTextContent("proposed values you entered");

    fireEvent.click(screen.getByTestId("save-variation"));
    expect(screen.getByRole("button", { name: "scenario-A-baseline" })).toBeInTheDocument();
    expect(screen.getByTestId("variations-ephemeral")).toHaveTextContent("this browser session only");
  });

  it("adds, edits, and deletes vertices, levels, and walls through the editor UI (add/edit/delete coverage)", () => {
    render(<ProposalEditor bbl={null} fetchImpl={stub()} />);
    const vertexXs = () => screen.getAllByLabelText(/^Vertex \d+ X coordinate$/);
    const levelIndices = () => screen.getAllByLabelText(/^Level \d+ index$/);
    const wallIds = () => screen.getAllByLabelText(/^Wall \d+ id$/);

    // The rectangle seed: 5 vertices, 1 level, 4 walls.
    expect(vertexXs()).toHaveLength(5);
    expect(levelIndices()).toHaveLength(1);
    expect(wallIds()).toHaveLength(4);

    // ADD one of each.
    fireEvent.click(screen.getByRole("button", { name: "Add vertex" }));
    fireEvent.click(screen.getByRole("button", { name: "Add level" }));
    fireEvent.click(screen.getByRole("button", { name: "Add wall" }));
    expect(vertexXs()).toHaveLength(6);
    expect(levelIndices()).toHaveLength(2);
    expect(wallIds()).toHaveLength(5);

    // EDIT a field in each table.
    fireEvent.change(screen.getByLabelText("Vertex 0 X coordinate"), { target: { value: "1000005" } });
    expect((screen.getByLabelText("Vertex 0 X coordinate") as HTMLInputElement).value).toBe("1000005");
    fireEvent.change(screen.getByLabelText("Level 0 floor count"), { target: { value: "7" } });
    expect((screen.getByLabelText("Level 0 floor count") as HTMLInputElement).value).toBe("7");
    fireEvent.change(screen.getByLabelText("Wall 0 id"), { target: { value: "W-EDIT" } });
    expect((screen.getByLabelText("Wall 0 id") as HTMLInputElement).value).toBe("W-EDIT");

    // DELETE the appended rows by index; the edited rows remain.
    fireEvent.click(screen.getByRole("button", { name: "Delete vertex 5" }));
    fireEvent.click(screen.getByRole("button", { name: "Delete level 1" }));
    fireEvent.click(screen.getByRole("button", { name: "Delete wall 4" }));
    expect(vertexXs()).toHaveLength(5);
    expect(levelIndices()).toHaveLength(1);
    expect(wallIds()).toHaveLength(4);
    expect((screen.getByLabelText("Vertex 0 X coordinate") as HTMLInputElement).value).toBe("1000005");
    expect((screen.getByLabelText("Wall 0 id") as HTMLInputElement).value).toBe("W-EDIT");
  });

  it("blocks a bad-charset draft client-side, naming the route constant, without sending", () => {
    render(<ProposalEditor bbl={null} fetchImpl={stub()} />);
    fireEvent.change(screen.getByLabelText("Proposal label"), { target: { value: "bad<script>" } });
    fireEvent.click(screen.getByTestId("run-check"));
    expect(screen.getByTestId("draft-problems")).toHaveTextContent("_LABEL_CHARSET");
    expect(screen.queryByTestId("proposal-check-summary")).toBeNull();
  });

  it("compares two client-local variations side by side", async () => {
    render(<ProposalEditor bbl={null} fetchImpl={stub()} />);
    fireEvent.click(screen.getByTestId("run-check"));
    await screen.findByTestId("proposal-check-summary");
    fireEvent.click(screen.getByTestId("save-variation"));
    fireEvent.click(screen.getByTestId("save-variation"));
    const compare = screen.getByTestId("variation-compare");
    const selects = compare.querySelectorAll<HTMLSelectElement>("select");
    expect(selects).toHaveLength(2);
    fireEvent.change(selects[0], { target: { value: selects[0].options[1].value } });
    fireEvent.change(selects[1], { target: { value: selects[1].options[2].value } });
    expect(compare.querySelectorAll(".proposal-compare-column")).toHaveLength(2);
  });

  it("carries no dangerouslySetInnerHTML and no scenario contract_version token in the packet source", () => {
    const files = [
      "../ProposalEditor.tsx",
      "../ProposalCheckReport.tsx",
      "../ProposalVariations.tsx",
      "../../../lib/proposal-checks-api.ts",
      "../../../lib/architect/proposal-draft.ts",
      "../../../test-support/proposal-check-fixtures.ts",
    ];
    for (const rel of files) {
      const source = readFileSync(new URL(rel, import.meta.url), "utf8");
      expect(source, rel).not.toContain("dangerouslySetInnerHTML");
      expect(source, rel).not.toContain("contract_version");
    }
  });
});

afterEach(cleanup);
