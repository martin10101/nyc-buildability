import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ProposalOutlineDraw } from "../ProposalOutlineDraw";

/**
 * Task M5-T065 (D-082-R001), map-drawing component (AS-1). Every action is
 * keyboard-operable, the drawn shape is labeled PROPOSED input (not a city
 * record), focus is MANAGED on delete (DB-043(a) from the start), and a
 * successful convert adopts the bridged EPSG:2263 vertices into the numeric
 * draft while a typed refusal produces NO coordinates and is announced
 * distinctly. The read-only LotOutlineMap is mocked (no WebGL in jsdom).
 */

vi.mock("@/components/address/LotOutlineMap", () => ({
  LotOutlineMap: ({ bbl }: { bbl: string }) => <div data-testid="mock-lot-map">map {bbl}</div>,
}));

const BBL = "1000010010";

function bridgeResponse(body: unknown, status: number): Response {
  const text = JSON.stringify(body);
  return new Response(text, {
    status,
    headers: {
      "Content-Type": "application/json",
      "Content-Length": String(new TextEncoder().encode(text).length),
      "X-Correlation-ID": "cid",
    },
  });
}
function stub(response: Response): typeof fetch {
  return (async () => response) as typeof fetch;
}

function bridged200(): Response {
  return bridgeResponse(
    {
      document_kind: "outline_bridge",
      bbl: BBL,
      srid: 2263,
      vertices: [
        { x: 1_000_020, y: 200_010 },
        { x: 1_000_080, y: 200_010 },
        { x: 1_000_080, y: 200_030 },
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
      disclosure: "Approximate PROPOSED input for editing, not a survey and not a city record.",
      correlation_id: "cid",
    },
    200,
  );
}

function addPoints(n: number): void {
  const addBtn = screen.getByRole("button", { name: "Add drawn point" });
  for (let i = 0; i < n; i += 1) fireEvent.click(addBtn);
}

afterEach(cleanup);

describe("ProposalOutlineDraw", () => {
  it("labels the drawn shape as proposed input and gates convert until 3 points exist", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    expect(screen.getByTestId("outline-draw-honesty")).toHaveTextContent("not a city record");
    const convert = screen.getByTestId("outline-draw-convert");
    expect(convert).toBeDisabled();
    addPoints(2);
    expect(convert).toBeDisabled();
    addPoints(1);
    expect(convert).toBeEnabled();
  });

  it("places and edits drawn points by keyboard-operable inputs, then adopts bridged 2263 vertices", async () => {
    const onAdopt = vi.fn();
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={onAdopt} fetchImpl={stub(bridged200())} />);
    addPoints(3);
    const coords: Array<[number, number]> = [
      [-73.9998, 40.7001],
      [-73.9992, 40.7001],
      [-73.9992, 40.7003],
    ];
    coords.forEach(([lng, lat], i) => {
      fireEvent.change(screen.getByLabelText(`Drawn point ${i} longitude`), { target: { value: String(lng) } });
      fireEvent.change(screen.getByLabelText(`Drawn point ${i} latitude`), { target: { value: String(lat) } });
    });
    expect((screen.getByLabelText("Drawn point 0 longitude") as HTMLInputElement).value).toBe("-73.9998");

    fireEvent.click(screen.getByTestId("outline-draw-convert"));
    await screen.findByTestId("outline-draw-bridged");

    // Adopted EXACTLY the server's 2263 vertices (as if typed).
    expect(onAdopt).toHaveBeenCalledTimes(1);
    expect(onAdopt).toHaveBeenCalledWith([
      { x: 1_000_020, y: 200_010 },
      { x: 1_000_080, y: 200_010 },
      { x: 1_000_080, y: 200_030 },
    ]);
    // The disclosed residual and the proposed-not-a-record framing are shown.
    expect(screen.getByTestId("outline-draw-residual")).toHaveTextContent("0.0004 ft");
    expect(screen.getByTestId("outline-draw-status")).toHaveTextContent("not a city record");
    expect(screen.getByTestId("outline-draw-announcer")).toHaveTextContent("proposed values");
  });

  it("manages focus on delete: focus lands on a delete control, and the Add button when the list empties", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    addPoints(3);
    // Delete the middle row: focus should land on the row that slid up into index 1.
    fireEvent.click(screen.getByLabelText("Delete drawn point 1"));
    expect(document.activeElement).toBe(screen.getByLabelText("Delete drawn point 1"));
    expect(screen.getAllByRole("button", { name: /^Delete drawn point/ })).toHaveLength(2);

    // Empty the list entirely: focus falls back to the Add button.
    fireEvent.click(screen.getByLabelText("Delete drawn point 1"));
    fireEvent.click(screen.getByLabelText("Delete drawn point 0"));
    expect(document.activeElement).toBe(screen.getByRole("button", { name: "Add drawn point" }));
    expect(screen.getByTestId("outline-draw-empty")).toBeInTheDocument();
  });

  it("refuses a residual-too-high fit distinctly and adopts NO coordinates", async () => {
    const onAdopt = vi.fn();
    const response = bridgeResponse(
      { state: "residual_too_high", rms_residual_ft: 9.5, residual_bound_ft: 2.0, message: "did not align" },
      422,
    );
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={onAdopt} fetchImpl={stub(response)} />);
    addPoints(3);
    fireEvent.click(screen.getByTestId("outline-draw-convert"));
    await screen.findByTestId("outline-draw-residual-too-high");
    expect(onAdopt).not.toHaveBeenCalled();
    expect(screen.getByTestId("outline-draw-status")).toHaveAttribute("data-outcome-kind", "residual_too_high");
    expect(screen.getByTestId("outline-draw-residual-detail")).toHaveTextContent("9.5 ft");
  });

  it("refuses an out-of-neighborhood draw distinctly from a residual refusal", async () => {
    const onAdopt = vi.fn();
    const response = bridgeResponse({ state: "out_of_neighborhood", message: "outside the lot" }, 422);
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={onAdopt} fetchImpl={stub(response)} />);
    addPoints(3);
    fireEvent.click(screen.getByTestId("outline-draw-convert"));
    await waitFor(() => expect(screen.getByTestId("outline-draw-status")).toBeInTheDocument());
    expect(screen.getByTestId("outline-draw-status")).toHaveAttribute("data-outcome-kind", "out_of_neighborhood");
    expect(onAdopt).not.toHaveBeenCalled();
  });
});
