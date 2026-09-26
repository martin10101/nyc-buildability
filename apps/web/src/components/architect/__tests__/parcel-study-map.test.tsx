import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { LotOutlineOutcome, ValidatedGeometry } from "@/lib/lot-geometry-api";
import { ParcelStudyMap, type ParcelStudyOutline } from "../ParcelStudyMap";

interface TestSource {
  data: { features: Array<{ properties: { bbl: string; color: string; contextOnly: boolean }; geometry: ValidatedGeometry }> };
}
interface TestMap {
  sources: Map<string, TestSource>;
  emit: (event: string, payload?: { sourceId?: string }) => void;
  remove: ReturnType<typeof vi.fn>;
  resize: ReturnType<typeof vi.fn>;
  fitBounds: ReturnType<typeof vi.fn>;
}
const runtime = vi.hoisted(() => ({
  maps: [] as TestMap[],
  markers: [] as HTMLElement[],
  renderAvailable: true,
  styleReady: true,
  observerDisconnect: vi.fn(),
  observerCallback: null as ResizeObserverCallback | null,
}));

vi.mock("maplibre-gl", () => {
  class MapMock {
    sources = new Map<string, TestSource>();
    layers = new Set<string>();
    events = new Map<string, Set<(payload?: { sourceId?: string }) => void>>();
    remove = vi.fn();
    resize = vi.fn();
    fitBounds = vi.fn();
    constructor() { runtime.maps.push(this); }
    on(event: string, callback: (payload?: { sourceId?: string }) => void) {
      if (!this.events.has(event)) this.events.set(event, new Set());
      this.events.get(event)!.add(callback);
    }
    off(event: string, callback: (payload?: { sourceId?: string }) => void) { this.events.get(event)?.delete(callback); }
    emit(event: string, payload?: { sourceId?: string }) { this.events.get(event)?.forEach(callback => callback(payload)); }
    isStyleLoaded() { return runtime.styleReady; }
    isSourceLoaded(id: string) { return this.sources.has(id); }
    getLayer(id: string) { return this.layers.has(id); }
    addSource(id: string, source: TestSource) { this.sources.set(id, source); }
    addLayer(layer: { id: string }) { this.layers.add(layer.id); }
    addControl() {}
    queryRenderedFeatures({ layers }: { layers: string[] }) {
      if (!runtime.renderAvailable) return [];
      return [...this.sources].flatMap(([source, data]) => data.data.features.flatMap(feature =>
        layers.map(id => ({ source, layer: { id }, properties: feature.properties }))));
    }
  }
  class MarkerMock {
    constructor({ element }: { element: HTMLElement }) { runtime.markers.push(element); }
    setLngLat() { return this; }
    addTo() { return this; }
    remove() {}
  }
  class ControlMock {}
  return { default: { Map: MapMock, Marker: MarkerMock,
    AttributionControl: ControlMock, NavigationControl: ControlMock, setWorkerUrl: vi.fn() } };
});

const LOT_A = "3022640032";
const LOT_B = "3022640033";
const BILLING = "3022647515";
const polygon: ValidatedGeometry = { type: "Polygon", coordinates: [
  [[-73.958, 40.700], [-73.957, 40.700], [-73.957, 40.701], [-73.958, 40.701], [-73.958, 40.700]],
  [[-73.9578, 40.7002], [-73.9572, 40.7002], [-73.9572, 40.7008], [-73.9578, 40.7008], [-73.9578, 40.7002]],
] };
const multipolygon: ValidatedGeometry = { type: "MultiPolygon", coordinates: [
  polygon.coordinates,
  [[[-73.956, 40.700], [-73.955, 40.700], [-73.955, 40.701], [-73.956, 40.700]]],
] };

function result(bbl: string, geometry: ValidatedGeometry = polygon): LotOutlineOutcome {
  return { kind: "document", correlationId: null, view: {
    bbl, outcome: "single_lot", outcomeToken: "single_lot", geometry,
    geometryUnusable: false, featureCount: 1, reviewRequired: false, noOutlineReason: null,
    condoClassification: { classification: "base_lot", note: null },
    accuracyNote: "Approximate, plus or minus 20 feet.", attribution: "NYC DCP MapPLUTO",
    disclaimer: "Not a legal boundary survey.", notes: ["A recorded source note."],
    source: { sourceId: "nyc-dcp-mappluto", datasetVersion: "26v2", retrievedAt: "2026-09-25T18:00:00Z" },
  } };
}
function outline(bbl: string, outcome = result(bbl)): ParcelStudyOutline {
  return { bbl, outcome, loading: false };
}
function missing(bbl: string): ParcelStudyOutline {
  const outcome = result(bbl);
  if (outcome.kind === "document") Object.assign(outcome.view, {
    outcome: "no_outline", geometry: null, featureCount: 0, noOutlineReason: "no_feature_for_bbl",
  });
  return outline(bbl, outcome);
}
function condoContext(): ParcelStudyOutline {
  const outcome = result(BILLING, multipolygon);
  if (outcome.kind === "document") outcome.view.condoClassification = {
    classification: "condo_billing_lot", note: "Condominium billing lot: merged complex outline.",
  };
  return outline(BILLING, outcome);
}
function features(index = runtime.maps.length - 1) {
  return runtime.maps[index].sources.get("parcel-study-outlines")!.data.features;
}

beforeEach(() => {
  runtime.maps.length = 0;
  runtime.markers.length = 0;
  runtime.renderAvailable = true;
  runtime.styleReady = true;
  runtime.observerDisconnect.mockReset();
  runtime.observerCallback = null;
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue({} as WebGLRenderingContext);
  vi.stubGlobal("ResizeObserver", class {
    constructor(callback: ResizeObserverCallback) { runtime.observerCallback = callback; }
    observe() {}
    disconnect() { runtime.observerDisconnect(); }
  });
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); vi.useRealTimers(); });

describe("ParcelStudyMap display-only identity and geometry", () => {
  it("shows the recorded condo outline without inventing a third land parcel when Wallabout base outlines are absent", async () => {
    render(<ParcelStudyMap compact arrangement="compare" outlines={[missing(LOT_A), missing(LOT_B)]} contextOutline={condoContext()} />);
    await screen.findByText("Condo tax-map outline shown for context; individual parcel boundaries unavailable.");
    expect(screen.getByTestId("parcel-study-context-outline")).toHaveAttribute("data-context-state", "rendered");
    expect(features()).toEqual([{ type: "Feature", properties: { bbl: BILLING, color: "#24699a", contextOnly: true }, geometry: multipolygon }]);
    expect(runtime.markers.map(marker => marker.textContent)).toEqual(["Condo context"]);
    expect(screen.getAllByText("No outline in the source record.")).toHaveLength(2);
    expect(screen.getByLabelText("Parcel outline availability").children).toHaveLength(2);
    expect(screen.getByText("Condo tax-map outline · context only")).toBeVisible();
    expect(screen.getByText(`Billing BBL ${BILLING} · Not an additional parcel or a confirmed development site. The condo tax-map outline does not establish individual parcel boundaries.`)).toBeInTheDocument();
    expect(screen.getByText("Condominium billing lot: merged complex outline.")).toBeInTheDocument();
    expect(screen.queryByText(/1 of 2 approximate parcel outlines shown/)).not.toBeInTheDocument();
  });

  it.each(["wrong BBL", "review", "malformed", "nonbilling", "multiple", "no outline", "duplicate base"])("withholds unsafe condo context: %s", async (reason) => {
    const context = condoContext();
    if (context.outcome?.kind !== "document") throw new Error("Fixture must be a document");
    if (reason === "wrong BBL") context.outcome.view.bbl = "3022647516";
    if (reason === "review") context.outcome.view.reviewRequired = true;
    if (reason === "malformed") context.outcome.view.geometry = { type: "Polygon", coordinates: [] };
    if (reason === "nonbilling") context.outcome.view.condoClassification.classification = "base_lot";
    if (reason === "multiple") context.outcome.view.featureCount = 2;
    if (reason === "no outline") { context.outcome.view.outcome = "no_outline"; context.outcome.view.geometry = null; }
    if (reason === "duplicate base") { context.bbl = LOT_A; context.outcome.view.bbl = LOT_A; }
    render(<ParcelStudyMap arrangement="compare" outlines={[missing(LOT_A), missing(LOT_B)]} contextOutline={context} />);
    expect(screen.getByTestId("parcel-study-context-outline")).toHaveAttribute("data-context-state", "unavailable");
    expect(runtime.maps).toHaveLength(0);
    expect(screen.queryByTestId("parcel-study-map-canvas")).not.toBeInTheDocument();
    expect(screen.getAllByText("No outline in the source record.").length).toBeGreaterThanOrEqual(2);
  });

  it("keeps a usable base outline when another is missing instead of replacing it with condo context", async () => {
    render(<ParcelStudyMap arrangement="compare" outlines={[outline(LOT_A), missing(LOT_B)]} contextOutline={condoContext()} />);
    await screen.findByText("1 of 2 approximate parcel outlines shown.");
    expect(features().map(feature => feature.properties)).toEqual([{ bbl: LOT_A, color: "#a4680c", contextOnly: false }]);
    expect(runtime.markers.map(marker => marker.textContent)).toEqual(["1 · Lot 32"]);
    expect(screen.queryByTestId("parcel-study-context-outline")).not.toBeInTheDocument();
    expect(screen.getByText("No outline in the source record.")).toBeInTheDocument();
  });

  it("distinguishes missing records from failed outline requests and keeps retry guidance visible with context", async () => {
    const { rerender } = render(<ParcelStudyMap arrangement="compare" outlines={[missing(LOT_A), missing(LOT_B)]} />);
    expect(screen.getByText("Individual parcel boundaries unavailable in the source records.")).toBeVisible();
    rerender(<ParcelStudyMap arrangement="compare" outlines={[outline(LOT_A, { kind: "client_timeout", timeoutMs: 12000 }), missing(LOT_B)]} contextOutline={condoContext()} />);
    await screen.findByText("Condo tax-map outline shown for context; individual parcel requests failed. Retry to check availability.");
    expect(screen.getByText("Outline request timed out.")).toBeInTheDocument();
  });

  it("uses compact camera padding, resizes before a pending fit, and preserves camera after readiness", async () => {
    let width = 400, height = 160;
    vi.spyOn(Element.prototype, "clientWidth", "get").mockImplementation(() => width);
    vi.spyOn(Element.prototype, "clientHeight", "get").mockImplementation(() => height);
    runtime.renderAvailable = false;
    render(<ParcelStudyMap arrangement="together" outlines={[outline(LOT_A)]} />);
    await waitFor(() => expect(runtime.maps).toHaveLength(1));
    const map = runtime.maps[0];
    expect(map.fitBounds).toHaveBeenLastCalledWith(expect.any(Array), { padding: 32, duration: 0, maxZoom: 19.5 });
    map.fitBounds.mockClear();
    map.resize.mockClear();
    width = 900; height = 600;
    act(() => runtime.observerCallback?.([], {} as ResizeObserver));
    expect(map.fitBounds).toHaveBeenLastCalledWith(expect.any(Array), { padding: 72, duration: 0, maxZoom: 19.5 });
    expect(map.resize.mock.invocationCallOrder[0]).toBeLessThan(map.fitBounds.mock.invocationCallOrder[0]);
    runtime.renderAvailable = true;
    act(() => map.emit("render"));
    expect(screen.getByText("1 of 1 approximate parcel outlines shown.")).toBeInTheDocument();
    map.fitBounds.mockClear();
    height = 160;
    act(() => runtime.observerCallback?.([], {} as ResizeObserver));
    expect(map.fitBounds).not.toHaveBeenCalled();
    expect(features()[0].geometry).toEqual(polygon);
  });

  it("keeps a hidden initializing map pending past the deadline, then resizes and verifies real features on reveal", async () => {
    vi.useFakeTimers();
    const outlines = [outline(LOT_A)];
    const { container, rerender } = render(<div hidden><ParcelStudyMap arrangement="together" outlines={outlines} /></div>);
    await act(async () => { await vi.dynamicImportSettled(); });
    expect(runtime.maps).toHaveLength(1);
    act(() => runtime.maps[0].emit("render"));
    expect(container).toHaveTextContent("Loading interactive parcel map…");
    expect(container).not.toHaveTextContent("1 of 1 approximate parcel outlines shown.");
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000); });
    expect(runtime.maps[0].remove).not.toHaveBeenCalled();
    runtime.renderAvailable = false;
    rerender(<div><ParcelStudyMap arrangement="together" outlines={outlines} /></div>);
    await act(async () => { await Promise.resolve(); });
    expect(runtime.maps[0].resize).toHaveBeenCalledOnce();
    expect(screen.getByText("Loading interactive parcel map…")).toBeInTheDocument();
    runtime.renderAvailable = true;
    act(() => runtime.maps[0].emit("render"));
    expect(screen.getByText("1 of 1 approximate parcel outlines shown.")).toBeInTheDocument();
    expect(runtime.maps).toHaveLength(1);
  });

  it("draws all polygons and holes verbatim, with numbered lot and BBL labels", async () => {
    render(<ParcelStudyMap arrangement="separate" outlines={[outline(LOT_A), outline(LOT_B, result(LOT_B, multipolygon))]} />);
    await screen.findByText("2 of 2 approximate parcel outlines shown.");
    expect(features()).toHaveLength(2);
    expect(features()[0].geometry).toEqual(polygon);
    expect(features()[1].geometry).toEqual(multipolygon);
    expect(features()[0].geometry.coordinates).toHaveLength(2);
    expect(features()[1].geometry.coordinates).toHaveLength(2);
    expect(features()[0].properties.color).not.toBe(features()[1].properties.color);
    expect(runtime.markers.map(marker => marker.textContent)).toEqual(["1 · Lot 32", "2 · Lot 33"]);
    expect(runtime.markers[1]).toHaveAttribute("aria-label", `Parcel 2, Lot 33, BBL ${LOT_B}`);
    expect(screen.getByRole("link", { name: "View Lot 33 in ZoLa" })).toHaveAttribute("href", `https://zola.planning.nyc.gov/bbl/${LOT_B}`);
    expect(screen.getAllByText("A recorded source note.")).toHaveLength(2);
  });

  it("withholds a wrong-BBL response while preserving the valid other parcel", async () => {
    render(<ParcelStudyMap arrangement="together" outlines={[outline(LOT_A), outline(LOT_B, result("3022647515"))]} />);
    await screen.findByText("1 of 2 approximate parcel outlines shown.");
    expect(features().map(feature => feature.properties.bbl)).toEqual([LOT_A]);
    expect(screen.getByText("Returned parcel does not match; outline withheld.")).toBeInTheDocument();
    expect(runtime.markers).toHaveLength(1);
  });

  it("does not pick from ambiguous, duplicate, unusable, or missing outlines", async () => {
    const ambiguous = result(LOT_A);
    if (ambiguous.kind === "document") ambiguous.view.outcome = "multiple_features";
    const { rerender } = render(<ParcelStudyMap arrangement="compare" outlines={[outline(LOT_A, ambiguous)]} />);
    expect(screen.getByText("Parcel geometry needs review; outline withheld.")).toBeInTheDocument();
    expect(runtime.maps).toHaveLength(0);
    rerender(<ParcelStudyMap arrangement="together" outlines={[outline(LOT_A), outline(LOT_A)]} />);
    expect(screen.getAllByText("Duplicate parcel records; outline withheld for review.")).toHaveLength(2);
    expect(runtime.maps).toHaveLength(0);
    const unusable = result(LOT_B);
    if (unusable.kind === "document") unusable.view.geometryUnusable = true;
    rerender(<ParcelStudyMap arrangement="separate" outlines={[outline(LOT_B, unusable)]} />);
    expect(screen.getByText("Source geometry is unusable; outline withheld.")).toBeInTheDocument();
    rerender(<ParcelStudyMap arrangement="separate" outlines={[outline(LOT_A, { kind: "route_absent", httpStatus: 404 })]} />);
    expect(screen.getByText("Outline service unavailable here.")).toBeInTheDocument();
    expect(runtime.maps).toHaveLength(0);
  });

  it("keeps data and ZoLa links when WebGL is unavailable without a fabricated map", async () => {
    vi.mocked(HTMLCanvasElement.prototype.getContext).mockReturnValue(null);
    render(<ParcelStudyMap arrangement="together" outlines={[outline(LOT_A), outline(LOT_B)]} />);
    await screen.findByText(/Interactive map unavailable in this browser/);
    expect(runtime.maps).toHaveLength(0);
    expect(screen.queryByTestId("parcel-study-map-canvas")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View Lot 32 in ZoLa" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View Lot 33 in ZoLa" })).toBeInTheDocument();
    expect(screen.getAllByText("Approximate outline available.")).toHaveLength(2);
  });

  it("changes grouping without merging geometry and disposes the old map and resize observer", async () => {
    const outlines = [outline(LOT_A), outline(LOT_B)];
    const { rerender, unmount } = render(<ParcelStudyMap arrangement="together" outlines={outlines} />);
    await screen.findByText("2 of 2 approximate parcel outlines shown.");
    expect(features()[0].properties.color).toBe(features()[1].properties.color);
    const old = runtime.maps[0];
    rerender(<ParcelStudyMap arrangement="together" outlines={outlines.map(entry => ({ ...entry }))} />);
    expect(runtime.maps).toHaveLength(1);
    expect(old.remove).not.toHaveBeenCalled();
    rerender(<ParcelStudyMap arrangement="compare" outlines={outlines} />);
    await waitFor(() => expect(runtime.maps).toHaveLength(2));
    expect(old.remove).toHaveBeenCalledOnce();
    expect(runtime.observerDisconnect).toHaveBeenCalledOnce();
    expect(features()).toHaveLength(2);
    expect(features()[0].properties.color).not.toBe(features()[1].properties.color);
    const latest = runtime.maps[1];
    act(() => runtime.observerCallback?.([], {} as ResizeObserver));
    expect(latest.resize).toHaveBeenCalledOnce();
    act(() => old.emit("error"));
    expect(screen.queryByText(/Interactive map could not render/)).toBeNull();
    unmount();
    expect(latest.remove).toHaveBeenCalledOnce();
    expect(runtime.observerDisconnect).toHaveBeenCalledTimes(2);
  });

  it("cancels the async map import on unmount before it can create a map", async () => {
    const { unmount } = render(<ParcelStudyMap arrangement="together" outlines={[outline(LOT_A)]} />);
    unmount();
    await act(async () => { await vi.dynamicImportSettled(); });
    expect(runtime.maps).toHaveLength(0);
  });

  it("waits for rendered parcel features and exposes render failure without losing records", async () => {
    runtime.renderAvailable = false;
    render(<ParcelStudyMap arrangement="separate" outlines={[outline(LOT_A)]} />);
    await waitFor(() => expect(runtime.maps).toHaveLength(1));
    expect(screen.getByText("Loading interactive parcel map…")).toBeInTheDocument();
    expect(screen.queryByText(/1 of 1 approximate parcel outlines shown/)).toBeNull();
    act(() => runtime.maps[0].emit("error"));
    expect(screen.getByText(/Interactive map could not render/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View Lot 32 in ZoLa" })).toBeInTheDocument();
    expect(runtime.maps[0].remove).toHaveBeenCalledOnce();
  });

  it("uses style readiness once and isolates failed street tiles from parcel data", async () => {
    runtime.styleReady = false;
    render(<ParcelStudyMap arrangement="separate" outlines={[outline(LOT_A)]} />);
    await waitFor(() => expect(runtime.maps).toHaveLength(1));
    expect(runtime.maps[0].sources.size).toBe(0);
    act(() => { runtime.maps[0].emit("style.load"); runtime.maps[0].emit("load"); });
    expect(features()).toHaveLength(1);
    expect(runtime.markers).toHaveLength(1);
    act(() => runtime.maps[0].emit("error", { sourceId: "nyc-basemap" }));
    expect(screen.getByText(/Some street context could not load/)).toBeInTheDocument();
    expect(screen.getByText("1 of 1 approximate parcel outlines shown.")).toBeInTheDocument();
    expect(runtime.maps[0].remove).not.toHaveBeenCalled();
  });
});
