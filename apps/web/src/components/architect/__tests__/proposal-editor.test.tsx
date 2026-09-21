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

  it("adopts map-drawn vertices into the numeric outline table exactly as if typed (M5-T065)", async () => {
    const bridgeBody = {
      document_kind: "outline_bridge",
      bbl: "1000010010",
      srid: 2263,
      vertices: [
        { x: 1000020, y: 200010 },
        { x: 1000080, y: 200010 },
        { x: 1000080, y: 200030 },
      ],
      correspondence: {
        method: "affine_least_squares_2d",
        alignment: "forward+offset0",
        alignment_winding: "forward",
        alignment_offset: 0,
        control_point_count: 4,
        candidates_evaluated: 8,
        rms_residual_ft: 0.0004,
        max_residual_ft: 0.0009,
        residual_bound_ft: 2.0,
        runner_up_rms_residual_ft: 55.2,
        alignment_separation_ft: 55.19,
        alignment_separation_min_ft: 2.0,
        source_display_ring: { crs: "EPSG:4326", source_id: "nyc-dcp-mappluto-lot-outline", representation: "lot_outline_display" },
        source_authoritative_ring: { crs: "EPSG:2263", source_id: "nyc-dcp-mappluto-arcgis", representation: "lot_geometry_authoritative" },
      },
      disclosure: "Approximate PROPOSED input, not a survey and not a city record.",
      correlation_id: "cid",
    };
    const text = JSON.stringify(bridgeBody);
    const bridgeStub = (async () =>
      new Response(text, {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Content-Length": String(new TextEncoder().encode(text).length),
          "X-Correlation-ID": "cid",
        },
      })) as typeof fetch;

    render(<ProposalEditor bbl="1000010010" fetchImpl={bridgeStub} />);
    // The rectangle seed starts with 5 numeric vertices (the authority).
    expect(screen.getAllByLabelText(/^Vertex \d+ X coordinate$/)).toHaveLength(5);

    // Draw three points and convert them through the (stubbed) bridge.
    const addDrawn = screen.getByRole("button", { name: "Add drawn point" });
    fireEvent.click(addDrawn);
    fireEvent.click(addDrawn);
    fireEvent.click(addDrawn);
    fireEvent.click(screen.getByTestId("outline-draw-convert"));
    await screen.findByTestId("outline-draw-bridged");

    // The converted 2263 vertices land in the numeric table exactly as if typed;
    // the table stays the visible, editable authority (manual remains the option).
    const xs = screen.getAllByLabelText(/^Vertex \d+ X coordinate$/) as HTMLInputElement[];
    expect(xs).toHaveLength(3);
    expect(xs[0].value).toBe("1000020");
    expect((screen.getByLabelText("Vertex 2 Y coordinate") as HTMLInputElement).value).toBe("200030");
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
