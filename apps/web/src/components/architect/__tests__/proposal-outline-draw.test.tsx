import { afterEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ProposalOutlineDraw } from "../ProposalOutlineDraw";

/**
 * Task M5-T065 (D-082-R001), map-drawing component (AS-1). Every action is
 * keyboard-operable, the drawn shape is labeled PROPOSED input (not a city
 * record), focus is MANAGED on delete (DB-043(a) from the start), and a
 * successful convert adopts the bridged EPSG:2263 vertices into the numeric
 * draft while a typed refusal produces NO coordinates and is announced
 * distinctly. The read-only LotOutlineMap is mocked (no WebGL in jsdom).
 *
 * Task M5-T066 (D-082-R001) adds PARENT INTEGRATION coverage: the real
 * ProposalOutlineMap wrapper renders here (only the leaf LotOutlineMap is
 * mocked), so the pointer callbacks the map runtime would fire — place / select
 * / move — are captured and driven directly, proving the map and the keyboard
 * table share ONE drawn-outline state (select/move/delete + deletion focus + the
 * persistent 1–2-point hint). Real MapLibre pointer geometry proves in the
 * Playwright e2e; this is the jsdom wiring/state guard.
 */

// Capture the props ProposalOutlineMap passes down to the (mocked) LotOutlineMap,
// so a test can invoke the map's click callbacks exactly as the runtime would.
interface CapturedLotMapProps {
  bbl: string;
  onOutlineMapClick?: (lngLat: { lng: number; lat: number }) => void;
  onDrawnVertexClick?: (index: number) => void;
  drawnOverlay?: { features: Array<{ properties: Record<string, unknown>; geometry: { type: string } }> };
}
let lastLotMapProps: CapturedLotMapProps | null = null;

vi.mock("@/components/address/LotOutlineMap", () => ({
  LotOutlineMap: (props: CapturedLotMapProps) => {
    lastLotMapProps = props;
    return <div data-testid="mock-lot-map">map {props.bbl}</div>;
  },
}));

/** Place a point by simulating a map click (nothing selected → place; a
 * selection → move) exactly as ProposalOutlineMap routes the runtime event. */
function mapClick(lngLat: { lng: number; lat: number }): void {
  act(() => lastLotMapProps!.onOutlineMapClick!(lngLat));
}
/** Click a drawn vertex on the map (select/deselect toggle). */
function mapVertexClick(index: number): void {
  act(() => lastLotMapProps!.onDrawnVertexClick!(index));
}
function pointFeatureCount(): number {
  return (lastLotMapProps?.drawnOverlay?.features ?? []).filter((f) => f.geometry.type === "Point").length;
}

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

/** Type finite coordinates into an existing drawn-point row. */
function fillPoint(i: number, lng: number, lat: number): void {
  fireEvent.change(screen.getByLabelText(`Drawn point ${i} longitude`), { target: { value: String(lng) } });
  fireEvent.change(screen.getByLabelText(`Drawn point ${i} latitude`), { target: { value: String(lat) } });
}

/** Add n rows AND fill each with distinct finite coordinates, so Convert is
 * genuinely enabled (DB-047(e) requires >= 3 FINITE points, not row count). */
function addFinitePoints(n: number): void {
  addPoints(n);
  for (let i = 0; i < n; i += 1) fillPoint(i, -73.999 + i * 0.0003, 40.7 + i * 0.0002);
}

afterEach(() => {
  cleanup();
  lastLotMapProps = null;
});

describe("ProposalOutlineDraw", () => {
  it("labels the drawn shape as proposed input and gates convert on 3 FINITE points, not row count (DB-047(e))", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    expect(screen.getByTestId("outline-draw-honesty")).toHaveTextContent("not a city record");
    const convert = screen.getByTestId("outline-draw-convert");
    // (e) Convert is aria-disabled (never the `disabled` attribute) so it stays
    // in the tab order while not convertible.
    expect(convert).toHaveAttribute("aria-disabled", "true");

    // Three rows ADDED but not yet typed (NaN/NaN). A count-only gate would
    // enable Convert here and launch a doomed bridge round-trip; the finiteness
    // gate keeps it not-convertible and explains why. Reverting the gate reddens this.
    addPoints(3);
    expect(convert).toHaveAttribute("aria-disabled", "true");
    expect(screen.getByTestId("outline-draw-min-hint")).toHaveTextContent("coordinates filled in");
    // The overlay/status draw nothing yet — no finite points to render.
    expect(pointFeatureCount()).toBe(0);

    // Type finite coordinates; Convert enables only when 3 finite points exist.
    fillPoint(0, -73.9998, 40.7001);
    fillPoint(1, -73.9992, 40.7001);
    expect(convert).toHaveAttribute("aria-disabled", "true"); // only 2 finite so far
    fillPoint(2, -73.9992, 40.7003);
    expect(convert).toHaveAttribute("aria-disabled", "false");
    expect(screen.queryByTestId("outline-draw-min-hint")).toBeNull();
    // The overlay now draws exactly the 3 finite points (status matches).
    expect(pointFeatureCount()).toBe(3);
  });

  it("the composed section never invites a map gesture when no interactive map exists (HJ B1)", () => {
    // [ORCH-CORRECTED per HJ B1] This suite's leaf mock renders NO interactive
    // aria-label and no loading node, so the wrapper classifies the surface
    // absent — the composed section a human reads top to bottom (header honesty
    // paragraph, map-context note, wrapper instructions) must not contain a
    // click invitation ANYWHERE, and neither leading paragraph may claim a map
    // is present. Restoring the old ungated lead copy reddens this spec.
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    const section = screen.getByTestId("proposal-outline-draw");
    expect(section.textContent).not.toContain("Click the lot map");
    expect(screen.getByTestId("outline-draw-honesty")).toHaveTextContent(
      "Add points and type them by keyboard",
    );
    expect(screen.getByTestId("outline-draw-map-context")).toHaveTextContent(
      "Any reference map shown displays the recorded lot for context only",
    );
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
    addFinitePoints(3);
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
    addFinitePoints(3);
    fireEvent.click(screen.getByTestId("outline-draw-convert"));
    await waitFor(() => expect(screen.getByTestId("outline-draw-status")).toBeInTheDocument());
    expect(screen.getByTestId("outline-draw-status")).toHaveAttribute("data-outcome-kind", "out_of_neighborhood");
    expect(onAdopt).not.toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// Task M5-T066 — PARENT INTEGRATION: pointer (map) and keyboard share ONE
// drawn-outline state. The real ProposalOutlineMap wrapper renders (only the
// leaf LotOutlineMap is mocked), so the place/select/move callbacks are driven
// exactly as the map runtime would. Real pointer geometry proves in the e2e.
// ---------------------------------------------------------------------------
describe("ProposalOutlineDraw — shared pointer/keyboard state (M5-T066)", () => {
  it("AS-1: map clicks and keyboard entry append into the SAME table and the overlay stays in sync", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    // No points yet: the empty-state row and an overlay with no point features.
    expect(screen.getByTestId("outline-draw-empty")).toBeInTheDocument();
    expect(pointFeatureCount()).toBe(0);

    // Place two points by MAP CLICK (pointer path), nothing selected.
    mapClick({ lng: -73.9998, lat: 40.7001 });
    mapClick({ lng: -73.9992, lat: 40.7001 });
    // Add the third by the KEYBOARD path (Add drawn point + typed coordinates).
    addPoints(1);
    fireEvent.change(screen.getByLabelText("Drawn point 2 longitude"), { target: { value: "-73.9992" } });
    fireEvent.change(screen.getByLabelText("Drawn point 2 latitude"), { target: { value: "40.7003" } });

    // All three landed in ONE table (one draft model): clicked rows carry the
    // clicked coordinates, the keyboard row carries the typed ones.
    expect((screen.getByLabelText("Drawn point 0 longitude") as HTMLInputElement).value).toBe("-73.9998");
    expect((screen.getByLabelText("Drawn point 1 longitude") as HTMLInputElement).value).toBe("-73.9992");
    expect((screen.getByLabelText("Drawn point 2 latitude") as HTMLInputElement).value).toBe("40.7003");
    // Convert enables at 3 points; the map overlay renders all three points.
    expect(screen.getByTestId("outline-draw-convert")).toHaveAttribute("aria-disabled", "false");
    expect(pointFeatureCount()).toBe(3);
  });

  it("AS-2: a placed point is selected then MOVED by a map click, with the keyboard-equivalent Select/Deselect toggle", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    mapClick({ lng: -73.9998, lat: 40.7001 });
    mapClick({ lng: -73.9992, lat: 40.7001 });

    // Select point 0 via a map-vertex click; the row shows the keyboard-equivalent
    // Deselect control pressed, and the overlay marks that point selected.
    mapVertexClick(0);
    expect(screen.getByRole("button", { name: "Deselect drawn point 0" })).toHaveAttribute("aria-pressed", "true");
    const selected = lastLotMapProps!.drawnOverlay!.features.find(
      (f) => f.geometry.type === "Point" && f.properties.index === 0,
    );
    expect(selected!.properties.selected).toBe(true);

    // With a selection, a map click MOVES that point (not a place — count stays 2).
    mapClick({ lng: -73.999, lat: 40.7005 });
    expect(screen.getAllByRole("button", { name: /^Delete drawn point/ })).toHaveLength(2);
    expect((screen.getByLabelText("Drawn point 0 longitude") as HTMLInputElement).value).toBe("-73.999");
    expect((screen.getByLabelText("Drawn point 0 latitude") as HTMLInputElement).value).toBe("40.7005");

    // Deselect via the map (click the same vertex again) → back to a placing map.
    mapVertexClick(0);
    expect(screen.getByRole("button", { name: "Select drawn point 0" })).toHaveAttribute("aria-pressed", "false");
    // A subsequent click now PLACES (count grows to 3), proving deselection stuck.
    mapClick({ lng: -73.9992, lat: 40.7003 });
    expect(screen.getAllByRole("button", { name: /^Delete drawn point/ })).toHaveLength(3);
  });

  it("AS-2: deleting a SELECTED drawn point via the table clears the selection and keeps focus on a delete control (DB-043(a))", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    mapClick({ lng: -73.9998, lat: 40.7001 });
    mapClick({ lng: -73.9992, lat: 40.7001 });
    mapClick({ lng: -73.9992, lat: 40.7003 });

    mapVertexClick(1);
    expect(screen.getByRole("button", { name: "Deselect drawn point 1" })).toHaveAttribute("aria-pressed", "true");

    fireEvent.click(screen.getByLabelText("Delete drawn point 1"));
    // Focus is never lost: it lands on the delete control that slid into index 1.
    expect(document.activeElement).toBe(screen.getByLabelText("Delete drawn point 1"));
    expect(screen.getAllByRole("button", { name: /^Delete drawn point/ })).toHaveLength(2);
    // The removed row's selection was reconciled away — no row is left selected.
    expect(screen.queryByRole("button", { name: /^Deselect drawn point/ })).toBeNull();
  });

  it("HJ-4: a persistent 'need at least 3 points' hint shows only while 1–2 points exist", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    expect(screen.queryByTestId("outline-draw-min-hint")).toBeNull(); // 0 points

    mapClick({ lng: -73.9998, lat: 40.7001 }); // 1 point
    expect(screen.getByTestId("outline-draw-min-hint")).toHaveTextContent("Add 2 more points");

    mapClick({ lng: -73.9992, lat: 40.7001 }); // 2 points (singular copy)
    expect(screen.getByTestId("outline-draw-min-hint")).toHaveTextContent("Add 1 more point");
    expect(screen.getByTestId("outline-draw-min-hint")).not.toHaveTextContent("Add 1 more points");

    mapClick({ lng: -73.9992, lat: 40.7003 }); // 3 points → hint gone, convert enabled
    expect(screen.queryByTestId("outline-draw-min-hint")).toBeNull();
    expect(screen.getByTestId("outline-draw-convert")).toHaveAttribute("aria-disabled", "false");
  });
});

// ---------------------------------------------------------------------------
// Task M5-T078 (DB-049) — drawing-surface disclosure + a11y cluster:
// (a) omission never silent, (b)/(F7) row-level incomplete markers naming the
// exact missing ordinate, (e) keyboard-reachable aria-disabled Convert that
// announces the reason and makes NO bridge call.
// ---------------------------------------------------------------------------
describe("ProposalOutlineDraw — DB-049 omission disclosure + row markers + keyboard Convert (M5-T078)", () => {
  it("AS-1 (a): 4 rows / 3 finite — Convert is ready, the hint at the point of action names the 1 omitted row, and the post-convert status names converted AND omitted counts", async () => {
    const onAdopt = vi.fn();
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={onAdopt} fetchImpl={stub(bridged200())} />);
    addFinitePoints(3); // rows 0-2 finite
    addPoints(1); // row 3 added, never typed (NaN/NaN)

    // Convert is READY (3 finite points) yet the omission hint STILL renders —
    // independent of enablement — and states how many rows Convert will omit.
    // MUTATION: re-gating the hint on `finiteCount < MIN` (the old condition)
    // suppresses it here (finiteCount is 3), throwing on getByTestId → red.
    const convert = screen.getByTestId("outline-draw-convert");
    expect(convert).toHaveAttribute("aria-disabled", "false");
    const hint = screen.getByTestId("outline-draw-min-hint");
    expect(hint).toHaveTextContent("Convert will include 3 points");
    expect(hint).toHaveTextContent("1 row");
    expect(hint).toHaveTextContent("will not be included");

    fireEvent.click(convert);
    await screen.findByTestId("outline-draw-bridged");
    // Post-convert status NAMES both counts — the omission is never silent.
    const counts = screen.getByTestId("outline-draw-convert-counts");
    expect(counts).toHaveTextContent("3 points converted");
    expect(counts).toHaveTextContent("1 row");
    expect(counts).toHaveTextContent("not included");
    // Only the 3 finite points were adopted (the untyped row was never sent).
    expect(onAdopt).toHaveBeenCalledTimes(1);
    expect(onAdopt.mock.calls[0][0]).toHaveLength(3);
  });

  it("AS-2 (b/F7): each incomplete row carries aria-invalid + a visible marker naming the EXACT missing ordinate; a complete row carries neither", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    addPoints(3);
    fillPoint(0, -73.9998, 40.7001); // row 0 complete
    // Row 1 gets ONLY a longitude (latitude still missing); row 2 stays NaN/NaN.
    fireEvent.change(screen.getByLabelText("Drawn point 1 longitude"), { target: { value: "-73.9992" } });

    // Complete row: no marker, no aria-invalid on either input.
    expect(screen.queryByTestId("outline-draw-row-incomplete-0")).toBeNull();
    expect(screen.getByLabelText("Drawn point 0 longitude")).not.toHaveAttribute("aria-invalid");
    expect(screen.getByLabelText("Drawn point 0 latitude")).not.toHaveAttribute("aria-invalid");

    // Row 1 missing ONLY latitude: marker says "latitude" (never the blanket
    // "longitude and latitude" — F7), and only the latitude input is aria-invalid.
    const row1 = screen.getByTestId("outline-draw-row-incomplete-1");
    expect(row1).toHaveTextContent("Needs latitude");
    expect(row1).not.toHaveTextContent("longitude and latitude");
    expect(screen.getByLabelText("Drawn point 1 longitude")).not.toHaveAttribute("aria-invalid");
    // MUTATION: dropping aria-invalid on the missing ordinate reddens here.
    expect(screen.getByLabelText("Drawn point 1 latitude")).toHaveAttribute("aria-invalid", "true");

    // Row 2 missing BOTH: marker names both, both inputs aria-invalid.
    expect(screen.getByTestId("outline-draw-row-incomplete-2")).toHaveTextContent("Needs longitude and latitude");
    expect(screen.getByLabelText("Drawn point 2 longitude")).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByLabelText("Drawn point 2 latitude")).toHaveAttribute("aria-invalid", "true");
  });

  it("F7: the omission hint names the exact missing ordinate for a single half-typed row (not a blanket 'longitude and latitude')", () => {
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={stub(bridged200())} />);
    addFinitePoints(3);
    addPoints(1); // row 3
    // Row 3: longitude only → latitude missing, one incomplete row.
    fireEvent.change(screen.getByLabelText("Drawn point 3 longitude"), { target: { value: "-73.9990" } });
    const hint = screen.getByTestId("outline-draw-min-hint");
    expect(hint).toHaveTextContent("without a latitude");
    expect(hint).not.toHaveTextContent("longitude and latitude");
    expect(screen.getByTestId("outline-draw-row-incomplete-3")).toHaveTextContent("Needs latitude");
  });

  it("AS-4 (e): a not-convertible Convert is aria-disabled and keyboard-reachable; activating it announces the reason and makes NO bridge call", () => {
    const fetchSpy = vi.fn(async () => bridged200()) as unknown as typeof fetch;
    render(<ProposalOutlineDraw bbl={BBL} onAdopt={vi.fn()} fetchImpl={fetchSpy} />);
    addFinitePoints(2); // only 2 finite → not convertible

    const convert = screen.getByTestId("outline-draw-convert");
    expect(convert).toHaveAttribute("aria-disabled", "true");
    // NOT the `disabled` attribute → it stays in the tab order (A7 remedy).
    expect(convert).not.toBeDisabled();

    fireEvent.click(convert);
    // No conversion/bridge call was made …
    expect(fetchSpy).not.toHaveBeenCalled();
    // … and the reason is announced through the EXISTING announcer region.
    expect(screen.getByTestId("outline-draw-announcer")).toHaveTextContent("Add 1 more point to convert");
  });
});
