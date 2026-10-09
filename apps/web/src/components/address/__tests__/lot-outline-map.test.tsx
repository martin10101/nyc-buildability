import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  LOT_OUTLINE_MAX_ZOOM,
  LotOutlineMap,
  contextLotOutlineFitBoundsOptions,
  lotOutlineFitBoundsOptions,
  runOnStyleReady,
} from "@/components/address/LotOutlineMap";
import { MAPLIBRE_WORKER_URL } from "@/lib/architect/map-runtime";

/**
 * M5-T023/M5-T025 pack for LotOutlineMap. maplibre-gl is mocked at the MODULE
 * boundary (the component dynamic-imports it) so this runs offline with no
 * WebGL: the mock records exactly what geometry reaches the map source,
 * proving the contract geometry is drawn VERBATIM (every ring, every
 * polygon) and never recomputed. Each typed outcome is asserted to render
 * its honest state.
 *
 * D-056-R002 [ORCH-CORRECTED per M5-T025-G3 F1]: the mock's "load" wiring is
 * driven through `once()` + `isStyleLoaded()` (matching the real MapLike
 * surface the component uses), with a per-test-configurable
 * `styleAlreadyLoaded` flag. These tests are a WIRING GUARD, not a faithful
 * simulation of MapLibre's event timing (G3 A3): they prove the draw step no
 * longer hangs on a single bare `on("load")` contingency — the reachable
 * root cause was "load" (which needs a completed first render) never firing
 * on a degraded-rendering device, with no style.load arm, readiness check,
 * or error surface. The already-loaded rows exercise the `isStyleLoaded()`
 * defense-in-depth path; `runOnStyleReady` is also unit-tested directly
 * against a minimal fake, independent of this mock.
 */

const mocks = vi.hoisted(() => {
  const mapCtor = vi.fn();
  const addSource = vi.fn();
  const addLayer = vi.fn();
  const addControl = vi.fn();
  const fitBounds = vi.fn();
  const remove = vi.fn();
  const resize = vi.fn();
  const attributionCtor = vi.fn();
  const navigationCtor = vi.fn();
  const setWorkerUrl = vi.fn();
  const state = {
    styleAlreadyLoaded: false,
    autoRender: true,
    sourceLoaded: true,
    renderListeners: [] as Array<() => void>,
    errorListeners: [] as Array<(event?: { sourceId?: string }) => void>,
    // Task M5-T066 interaction support: recorded click listeners, the features
    // a drawn-vertex-layer query returns (a hit vs an empty click), and the
    // GeoJSON sources so getSource/setData can be observed.
    clickListeners: [] as Array<(event?: unknown) => void>,
    overlayHit: [] as Array<{ properties?: Record<string, unknown> | null }>,
    sources: {} as Record<string, { setData: ReturnType<typeof vi.fn> }>,
    // M5-T071 (DB-048): every constructed map, each carrying its OWN per-source
    // creation counts. The AS-1 sync spec asserts on these to detect a DUPLICATE
    // source added within a single live map (the real defect) while tolerating a
    // legitimate whole-map rebuild — a fresh instance that adds the source once
    // more. A module-wide addSource tally cannot tell those two apart.
    mapInstances: [] as Array<{ sourceAddCounts: Record<string, number> }>,
  };

  class MockMap {
    sourceAddCounts: Record<string, number> = {};
    constructor(options: unknown) {
      mapCtor(options);
      state.mapInstances.push(this);
    }
    isStyleLoaded() {
      return state.styleAlreadyLoaded;
    }
    once(type: string, cb: () => void) {
      // Mirrors the real MapLibre "one-time listener attached after the
      // style is already loaded is never invoked" semantics: if the style
      // is already loaded, no further "load"/"style.load" event will ever
      // fire again, so this mock (correctly) does NOT invoke cb here — the
      // component must have already run the draw step synchronously via
      // isStyleLoaded() before calling once() at all.
      if (state.styleAlreadyLoaded) return;
      if (type === "load") queueMicrotask(cb);
    }
    on(type: string, cb: (event?: { sourceId?: string }) => void) {
      if (type === "error") state.errorListeners.push(cb);
      if (type === "click") state.clickListeners.push(cb as (event?: unknown) => void);
      if (type === "render") {
        state.renderListeners.push(cb);
        if (state.autoRender) queueMicrotask(cb);
      }
    }
    off(type: string, cb: () => void) {
      if (type === "render") state.renderListeners = state.renderListeners.filter(listener => listener !== cb);
    }
    isSourceLoaded() { return state.sourceLoaded; }
    getLayer(id: string) {
      return addLayer.mock.calls.find(([layer]) => (layer as { id: string }).id === id)?.[0];
    }
    // Supports BOTH the parcel-render observer form `queryRenderedFeatures({ layers })`
    // and the click hit-test form `queryRenderedFeatures(point, { layers })`. A
    // query against the drawn-vertex layer returns the configured overlay hit;
    // any other query returns the lot-outline features the observer needs.
    queryRenderedFeatures(arg1?: unknown, arg2?: unknown) {
      const options = (arg2 ?? arg1) as { layers?: string[] } | undefined;
      const layers = options?.layers ?? [];
      if (layers.includes("proposal-drawn-outline-points")) return state.overlayHit;
      return ["lot-outline-fill", "lot-outline-line"].map(id => ({ source: "lot-outline", layer: { id } }));
    }
    getSource(id: string) {
      return state.sources[id];
    }
    addSource(id: string, source: unknown) {
      this.sourceAddCounts[id] = (this.sourceAddCounts[id] ?? 0) + 1;
      state.sources[id] = { setData: vi.fn() };
      addSource(id, source);
    }
    addLayer(layer: unknown) {
      addLayer(layer);
    }
    addControl(control: unknown, position?: string) {
      addControl(control, position);
    }
    fitBounds(bounds: unknown, options?: unknown) {
      fitBounds(bounds, options);
    }
    remove() {
      remove();
    }
    resize() {
      resize();
    }
  }
  class MockAttributionControl {
    constructor(options: unknown) {
      attributionCtor(options);
    }
  }
  class MockNavigationControl {
    constructor(options: unknown) {
      navigationCtor(options);
    }
  }
  return {
    mapCtor,
    addSource,
    addLayer,
    addControl,
    fitBounds,
    remove,
    resize,
    attributionCtor,
    navigationCtor,
    setWorkerUrl,
    state,
    MockMap,
    MockAttributionControl,
    MockNavigationControl,
    setStyleAlreadyLoaded(value: boolean) {
      state.styleAlreadyLoaded = value;
    },
    fireMapError(sourceId?: string) {
      state.errorListeners.forEach((cb) => cb(sourceId ? { sourceId } : undefined));
    },
    fireMapClick(event?: unknown) {
      state.clickListeners.forEach((cb) => cb(event));
    },
  };
});

vi.mock("maplibre-gl", () => ({
  default: {
    setWorkerUrl: mocks.setWorkerUrl,
    Map: mocks.MockMap,
    AttributionControl: mocks.MockAttributionControl,
    NavigationControl: mocks.MockNavigationControl,
  },
  setWorkerUrl: mocks.setWorkerUrl,
  Map: mocks.MockMap,
  AttributionControl: mocks.MockAttributionControl,
  NavigationControl: mocks.MockNavigationControl,
}));

const FIXTURE_ROOT = resolve(
  process.cwd(),
  "../../packages/contracts/fixtures/valid/lot_geometry",
);
function fixture(name: string): Record<string, unknown> {
  return JSON.parse(readFileSync(resolve(FIXTURE_ROOT, `${name}.json`), "utf8"));
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "X-Correlation-ID": "lot-cid-1",
    },
  });
}
function fetchReturning(response: Response): typeof fetch {
  return vi.fn().mockResolvedValue(response) as unknown as typeof fetch;
}
function fetchRejecting(): typeof fetch {
  return vi.fn().mockRejectedValue(new Error("offline")) as unknown as typeof fetch;
}

function enableWebgl() {
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(
    {} as unknown as never,
  );
}
function disableWebgl() {
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(
    null as unknown as never,
  );
}

/** The layer IDs the map installed, in order. DB-049(h): every check on
 * `addLayer` uses layer-ID PRESENCE (this helper), never an exact cross-render
 * `toHaveBeenCalledTimes` tally — that exact-count form is the DB-048 flake
 * class, red "expected 2, got 4" whenever a legitimate whole-map rebuild re-adds
 * the two lot-outline layers between an effect pass and the assertion. Presence
 * still reddens the real defect (a dropped layer). */
function addedLayerIds(): string[] {
  return mocks.addLayer.mock.calls.map(([layer]) => (layer as { id?: string }).id ?? "");
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
  mocks.setStyleAlreadyLoaded(false);
  mocks.state.errorListeners.length = 0;
  mocks.state.renderListeners.length = 0;
  mocks.state.clickListeners.length = 0;
  mocks.state.overlayHit.length = 0;
  for (const key of Object.keys(mocks.state.sources)) delete mocks.state.sources[key];
  mocks.state.mapInstances.length = 0;
  mocks.state.autoRender = true;
  mocks.state.sourceLoaded = true;
  vi.useRealTimers();
});

describe("LotOutlineMap — single_lot with WebGL", () => {
  beforeEach(() => enableWebgl());

  it("frames compact and large context maps from their real size, resizes before fitting, and preserves a ready camera", async () => {
    let width = 400, height = 160;
    vi.spyOn(Element.prototype, "clientWidth", "get").mockImplementation(() => width);
    vi.spyOn(Element.prototype, "clientHeight", "get").mockImplementation(() => height);
    let resized: ResizeObserverCallback | null = null;
    vi.stubGlobal("ResizeObserver", class {
      constructor(callback: ResizeObserverCallback) { resized = callback; }
      observe() {}
      disconnect() {}
    });
    mocks.state.autoRender = false;
    render(<LotOutlineMap bbl="1008350041" context fetchImpl={fetchReturning(jsonResponse(fixture("single_lot_polygon")))} />);
    await waitFor(() => expect(mocks.fitBounds).toHaveBeenCalled());
    expect(mocks.fitBounds).toHaveBeenLastCalledWith(expect.any(Array), { padding: 32, duration: 0, maxZoom: 18.5 });

    mocks.fitBounds.mockClear();
    mocks.resize.mockClear();
    width = 900; height = 600;
    act(() => resized?.([], {} as ResizeObserver));
    expect(mocks.fitBounds).toHaveBeenLastCalledWith(expect.any(Array), { padding: 72, duration: 0, maxZoom: 18.5 });
    expect(mocks.resize.mock.invocationCallOrder[0]).toBeLessThan(mocks.fitBounds.mock.invocationCallOrder[0]);

    act(() => { [...mocks.state.renderListeners].forEach(listener => listener()); });
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered");
    mocks.fitBounds.mockClear();
    height = 160;
    act(() => resized?.([], {} as ResizeObserver));
    expect(mocks.fitBounds).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Recenter lot" }));
    expect(mocks.fitBounds).toHaveBeenLastCalledWith(expect.any(Array), { padding: 32, duration: 0, maxZoom: 18.5 });
  });

  it("withholds an otherwise drawable response for a different or absent BBL", async () => {
    const fx = fixture("single_lot_polygon");
    fx.bbl = "3022640032";
    const { rerender } = render(<LotOutlineMap bbl="1008350041" fetchImpl={fetchReturning(jsonResponse(fx))} />);
    expect(await screen.findByTestId("lot-outline-unavailable")).toHaveTextContent("does not match");
    expect(mocks.mapCtor).not.toHaveBeenCalled();
    delete fx.bbl;
    rerender(<LotOutlineMap bbl="1008350041" fetchImpl={fetchReturning(jsonResponse(fx))} />);
    expect(await screen.findByTestId("lot-outline-unavailable")).toHaveTextContent("does not match");
    expect(mocks.mapCtor).not.toHaveBeenCalled();
  });

  it("keeps an initializing map pending while its floating panel is hidden and resizes the same map on reveal", async () => {
    vi.useFakeTimers();
    mocks.state.autoRender = false;
    const fetchImpl = fetchReturning(jsonResponse(fixture("single_lot_polygon")));
    const { container, rerender } = render(<div hidden><LotOutlineMap bbl="1008350041" fetchImpl={fetchImpl} /></div>);
    await act(async () => { await vi.advanceTimersByTimeAsync(1); await vi.dynamicImportSettled(); });
    const mapCount = mocks.mapCtor.mock.calls.length;
    expect(mapCount).toBeGreaterThan(0);
    act(() => { [...mocks.state.renderListeners].forEach(listener => listener()); });
    expect(container.querySelector('[data-testid="lot-outline"]')).toHaveAttribute("data-parcel-state", "loading");
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000); });
    expect(mocks.remove).not.toHaveBeenCalled();
    rerender(<div><LotOutlineMap bbl="1008350041" fetchImpl={fetchImpl} /></div>);
    await act(async () => { await Promise.resolve(); });
    expect(mocks.resize).toHaveBeenCalled();
    act(() => { [...mocks.state.renderListeners].forEach(listener => listener()); });
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered");
    expect(mocks.mapCtor).toHaveBeenCalledTimes(mapCount);
    expect(fetchImpl).toHaveBeenCalledOnce();
  });

  it("S1: draws the fixture geometry VERBATIM as a GeoJSON source, fits bounds, and puts NYC DCP attribution on the map", async () => {
    const fx = fixture("single_lot_polygon");
    render(
      <LotOutlineMap bbl="1008350041" fetchImpl={fetchReturning(jsonResponse(fx))} />,
    );

    expect(await screen.findByTestId("lot-outline-map")).toBeInTheDocument();
    await waitFor(() => expect(mocks.addSource).toHaveBeenCalled());
    expect(mocks.setWorkerUrl).toHaveBeenCalledWith(MAPLIBRE_WORKER_URL);
    expect(mocks.setWorkerUrl.mock.invocationCallOrder[0]).toBeLessThan(mocks.mapCtor.mock.invocationCallOrder[0]);
    await waitFor(() => expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered"));

    const [, source] = mocks.addSource.mock.calls[0] as [string, { data: { geometry: unknown } }];
    // The geometry handed to MapLibre EQUALS the fixture geometry — untouched.
    expect(source.data.geometry).toEqual(fx.geometry);
    // A fill + a line layer are installed (presence, not an exact tally — DB-049 h),
    // camera framed, attribution control added.
    const s1LayerIds = addedLayerIds();
    expect(s1LayerIds).toContain("lot-outline-fill");
    expect(s1LayerIds).toContain("lot-outline-line");
    expect(mocks.fitBounds).toHaveBeenCalled();
    // D-056-R002 framing fix: the raised maxZoom cap is what actually reaches
    // fitBounds (not just "called with something").
    expect(mocks.fitBounds).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ maxZoom: LOT_OUTLINE_MAX_ZOOM }),
    );
    expect(mocks.attributionCtor).toHaveBeenCalledWith(
      expect.objectContaining({
        customAttribution: expect.stringContaining("City Planning"),
      }),
    );
    // D-056-R003: a visible, keyboard-accessible zoom control (compass off —
    // a flat top-down display-only outline has no rotation affordance).
    expect(mocks.navigationCtor).toHaveBeenCalledWith(
      expect.objectContaining({ showCompass: false }),
    );
    expect(mocks.addControl).toHaveBeenCalledWith(
      expect.anything(),
      "top-right",
    );
    // Visible +/-20 ft copy + attribution text (present with or without WebGL).
    expect(screen.getByTestId("lot-outline-accuracy").textContent).toContain(
      "20 ft",
    );
    expect(screen.getByTestId("lot-outline-attribution").textContent).toContain(
      "City Planning",
    );
    // Accessible: labeled region + a screen-reader outcome summary.
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("role", "region");
    expect(screen.getByTestId("lot-outline-summary").textContent).toContain(
      "approximate lot outline",
    );
  });

  it("S2: a MultiPolygon reaches the source with EVERY polygon preserved (no first-pick, no dropped ring)", async () => {
    const fx = fixture("single_lot_multipolygon");
    render(
      <LotOutlineMap bbl="4142600001" fetchImpl={fetchReturning(jsonResponse(fx))} />,
    );
    await screen.findByTestId("lot-outline-map");
    await waitFor(() => expect(mocks.addSource).toHaveBeenCalled());
    const [, source] = mocks.addSource.mock.calls[0] as [string, { data: { geometry: { type: string; coordinates: unknown[] } } }];
    expect(source.data.geometry).toEqual(fx.geometry);
    expect(source.data.geometry.type).toBe("MultiPolygon");
    expect(source.data.geometry.coordinates).toHaveLength(
      (fx.geometry as { coordinates: unknown[] }).coordinates.length,
    );
  });

  it("G5 F-1: a HOSTILE reflected attribution NEVER reaches the MapLibre AttributionControl (a client constant does); the React text shows it inert", async () => {
    const hostile = '<img src=x onerror="window.__pwned=1">NYC DCP';
    const fx = fixture("single_lot_polygon");
    fx.attribution = hostile;
    const { container } = render(
      <LotOutlineMap bbl="1008350041" fetchImpl={fetchReturning(jsonResponse(fx))} />,
    );
    await screen.findByTestId("lot-outline-map");
    await waitFor(() => expect(mocks.attributionCtor).toHaveBeenCalled());
    // The control receives the client CONSTANT, never the reflected string.
    const opts = mocks.attributionCtor.mock.calls[0][0] as { customAttribution: string };
    expect(opts.customAttribution).toBe("NYC Department of City Planning (DCP), MapPLUTO");
    expect(opts.customAttribution).not.toContain("onerror");
    // The reflected value still shows as INERT React-escaped text (no element).
    expect(screen.getByTestId("lot-outline-attribution").textContent).toContain(
      "onerror",
    );
    expect(container.querySelectorAll("img")).toHaveLength(0);
    expect(
      (window as unknown as Record<string, unknown>).__pwned,
    ).toBeUndefined();
  });

  it("S2: a Polygon WITH an interior hole passes every ring to the source (no hole filled)", async () => {
    // Synthetic structural input (a hole case is not among the committed
    // contract fixtures): proves the pass-through never drops an interior ring.
    const fx = fixture("single_lot_polygon");
    const exterior = (fx.geometry as { coordinates: number[][][] }).coordinates[0];
    const hole = [
      [-73.9855, 40.7486],
      [-73.9853, 40.7486],
      [-73.9853, 40.7488],
      [-73.9855, 40.7488],
      [-73.9855, 40.7486],
    ];
    (fx.geometry as { coordinates: number[][][] }).coordinates = [exterior, hole];
    render(
      <LotOutlineMap bbl="1008350041" fetchImpl={fetchReturning(jsonResponse(fx))} />,
    );
    await screen.findByTestId("lot-outline-map");
    await waitFor(() => expect(mocks.addSource).toHaveBeenCalled());
    const [, source] = mocks.addSource.mock.calls[0] as [string, { data: { geometry: { coordinates: unknown[] } } }];
    expect(source.data.geometry.coordinates).toHaveLength(2);
    expect(source.data.geometry).toEqual(fx.geometry);
  });
});

describe("LotOutlineMap — honest states without a drawn map", () => {
  beforeEach(() => enableWebgl());

  it("condo unit lot: honest-empty state names the reason; no map is constructed", async () => {
    render(
      <LotOutlineMap
        bbl="1000151001"
        fetchImpl={fetchReturning(jsonResponse(fixture("no_outline_condo_unit")))}
      />,
    );
    const empty = await screen.findByTestId("lot-outline-empty");
    expect(empty.textContent).toContain("condominium unit lot");
    expect(screen.queryByTestId("lot-outline-map")).toBeNull();
    expect(mocks.mapCtor).not.toHaveBeenCalled();
  });

  it("no_feature: honest-empty state, no map", async () => {
    render(
      <LotOutlineMap
        bbl="5999999999"
        fetchImpl={fetchReturning(jsonResponse(fixture("no_outline_no_feature")))}
      />,
    );
    expect(await screen.findByTestId("lot-outline-empty")).toBeInTheDocument();
    expect(mocks.mapCtor).not.toHaveBeenCalled();
  });

  it("multiple_features: review posture, never a first-pick outline", async () => {
    render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={fetchReturning(jsonResponse(fixture("multiple_features_review")))}
      />,
    );
    const review = await screen.findByTestId("lot-outline-review");
    expect(review.textContent).toContain("more than one parcel");
    expect(mocks.mapCtor).not.toHaveBeenCalled();
  });

  it("invalid_geometry: honest note, no shape drawn", async () => {
    render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={fetchReturning(jsonResponse(fixture("invalid_geometry")))}
      />,
    );
    expect(await screen.findByTestId("lot-outline-invalid")).toBeInTheDocument();
    expect(mocks.mapCtor).not.toHaveBeenCalled();
  });

  it("route_absent (flag-off 404): typed unavailable fallback, never a blank container", async () => {
    render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={fetchReturning(
          new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 }),
        )}
      />,
    );
    expect(await screen.findByTestId("lot-outline-unavailable")).toBeInTheDocument();
  });

  it("network failure: typed unavailable fallback (address details unaffected)", async () => {
    render(<LotOutlineMap bbl="1008350041" fetchImpl={fetchRejecting()} />);
    const fallback = await screen.findByTestId("lot-outline-unavailable");
    expect(fallback.textContent).toContain("could not be loaded");
  });
});

describe("LotOutlineMap — WebGL unavailable", () => {
  beforeEach(() => disableWebgl());

  it("single_lot without WebGL: honest fallback, +/-20 ft copy kept, maplibre-gl NEVER imported/constructed", async () => {
    render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={fetchReturning(jsonResponse(fixture("single_lot_polygon")))}
      />,
    );
    expect(
      await screen.findByTestId("lot-outline-webgl-unavailable"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("lot-outline-accuracy").textContent).toContain(
      "20 ft",
    );
    expect(screen.queryByTestId("lot-outline-map")).toBeNull();
    expect(mocks.mapCtor).not.toHaveBeenCalled();
    // G3 ADVISORY-1: the screen-reader summary must MATCH the visible fallback,
    // not falsely announce that a map is shown.
    const summary = screen.getByTestId("lot-outline-summary").textContent ?? "";
    expect(summary).toContain("could not open an interactive map");
    expect(summary).not.toContain("An approximate lot outline is shown");
  });
});

// ---------------------------------------------------------------------------
// D-056-R002 root-cause fix: `runOnStyleReady` closes the missed-"load"-event
// race directly and is unit-tested here against a minimal FAKE (no WebGL, no
// maplibre-gl mock, no React) — the strongest possible red-on-old/green-on-new
// proof this jsdom environment can express, since it exercises the exact
// function that replaced the old `map.on("load", draw)` call.
// ---------------------------------------------------------------------------
describe("runOnStyleReady — pure unit tests (D-056-R002 root-cause fix)", () => {
  it("style ALREADY loaded: draw() runs immediately and synchronously, with no event wait at all", () => {
    // [ORCH-CORRECTED per M5-T025-G3 F1] This path is DEFENSE-IN-DEPTH, not
    // the operative production fix: at the component's call site the
    // listener was always attached synchronously with construction, so
    // "already loaded before attach" is not reachable there. The reachable
    // root cause was the one-time "load" event (which requires a completed
    // first render) never firing on a degraded-rendering device, with no
    // style.load arm and no readiness check — closed by the style.load arm
    // tested below. This row pins the fast path for any OTHER call order.
    const once = vi.fn();
    const fakeMap = { isStyleLoaded: () => true, once };
    const draw = vi.fn();
    runOnStyleReady(fakeMap, draw);
    expect(draw).toHaveBeenCalledTimes(1);
    // No listener was even armed — the immediate path is truly synchronous,
    // not "attach and hope the event still fires".
    expect(once).not.toHaveBeenCalled();
  });

  it("style NOT YET loaded: arms both 'load' and 'style.load'; draw() runs exactly once even if both fire", () => {
    const listeners: Record<string, () => void> = {};
    const fakeMap = {
      isStyleLoaded: () => false,
      once: (type: string, cb: () => void) => {
        listeners[type] = cb;
      },
    };
    const draw = vi.fn();
    runOnStyleReady(fakeMap, draw);
    expect(draw).not.toHaveBeenCalled();
    expect(Object.keys(listeners).sort()).toEqual(["load", "style.load"]);
    // Both events fire (a real, if unusual, possibility) — draw still runs
    // exactly once (idempotency guard).
    listeners.load();
    listeners["style.load"]();
    expect(draw).toHaveBeenCalledTimes(1);
  });

  it("style not yet loaded, only 'style.load' fires (not 'load'): draw() still runs", () => {
    // MapLibre's own guidance treats "style.load" as the reliable hook —
    // this proves the fix does not silently depend on "load" alone.
    const listeners: Record<string, () => void> = {};
    const fakeMap = {
      isStyleLoaded: () => false,
      once: (type: string, cb: () => void) => {
        listeners[type] = cb;
      },
    };
    const draw = vi.fn();
    runOnStyleReady(fakeMap, draw);
    listeners["style.load"]();
    expect(draw).toHaveBeenCalledTimes(1);
  });
});

describe("lotOutlineFitBoundsOptions — D-056-R002 framing fix", () => {
  it.each([
    [400, 160, 32],
    [160, 500, 32],
    [640, 480, 72],
    [0, 0, 24],
  ])("context framing at %i × %i pixels uses %i pixels of padding without changing its zoom cap", (clientWidth, clientHeight, padding) => {
    expect(contextLotOutlineFitBoundsOptions({ clientWidth, clientHeight })).toEqual({ padding, duration: 0, maxZoom: 18.5 });
  });

  it("raises maxZoom above the prior fingernail-size cap of 18", () => {
    const options = lotOutlineFitBoundsOptions();
    expect(options.maxZoom).toBe(LOT_OUTLINE_MAX_ZOOM);
    expect(options.maxZoom).toBeGreaterThan(18);
    expect(options.padding).toBe(24);
    expect(options.duration).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// Task M5-T066 — additive map-CLICK interaction. Real pointer geometry only
// proves in the Playwright e2e (jsdom has no MapLibre pointer/WebGL); these are
// the WIRING/state guards: byte-equivalent display when the props are absent,
// and the click/overlay contract when present.
// ---------------------------------------------------------------------------
describe("LotOutlineMap — additive map-CLICK interaction (M5-T066)", () => {
  beforeEach(() => enableWebgl());

  const emptyOverlay = { type: "FeatureCollection" as const, features: [] };
  const singleLot = () => fetchReturning(jsonResponse(fixture("single_lot_polygon")));

  it("AS-3 byte-equivalence: with no interaction props, NO click listener attaches and only the 2 lot-outline layers are added", async () => {
    render(<LotOutlineMap bbl="1008350041" fetchImpl={singleLot()} />);
    await screen.findByTestId("lot-outline-map");
    await waitFor(() => expect(mocks.addSource).toHaveBeenCalled());
    // Byte-equivalence: the two lot-outline layers install and NO drawn-overlay
    // layer is added when no interaction props are passed. DB-049(h): asserted by
    // layer-ID SET equality (and presence-negative), never an exact cross-render
    // tally. [M5-T078 rework G4-A5] The set keeps the title's "only": a stray
    // extra layer of any id reddens, while a legitimate whole-map rebuild (which
    // re-adds the same two ids) still passes.
    const ids = addedLayerIds();
    expect(new Set(ids)).toEqual(new Set(["lot-outline-fill", "lot-outline-line"]));
    expect(ids).not.toContain("proposal-drawn-outline-line");
    expect(ids).not.toContain("proposal-drawn-outline-points");
    expect(mocks.state.clickListeners).toHaveLength(0);
  });

  it("AS-1: registers a click listener and reports the display 4326 position on an empty-area click", async () => {
    const onOutlineMapClick = vi.fn();
    render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={singleLot()}
        onOutlineMapClick={onOutlineMapClick}
        onDrawnVertexClick={vi.fn()}
        drawnOverlay={emptyOverlay}
      />,
    );
    await screen.findByTestId("lot-outline-map");
    await waitFor(() => expect(mocks.state.clickListeners.length).toBeGreaterThan(0));
    act(() => mocks.fireMapClick({ point: { x: 10, y: 10 }, lngLat: { lng: -73.98, lat: 40.75 } }));
    expect(onOutlineMapClick).toHaveBeenCalledWith({ lng: -73.98, lat: 40.75 });
  });

  it("AS-2: a click that lands on a drawn vertex routes to onDrawnVertexClick, never a place", async () => {
    const onOutlineMapClick = vi.fn();
    const onDrawnVertexClick = vi.fn();
    mocks.state.overlayHit.push({ properties: { index: 2 } });
    render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={singleLot()}
        onOutlineMapClick={onOutlineMapClick}
        onDrawnVertexClick={onDrawnVertexClick}
        drawnOverlay={emptyOverlay}
      />,
    );
    await screen.findByTestId("lot-outline-map");
    // The drawn-vertex hit test is guarded on the overlay layer's existence, so
    // wait until the overlay's drawn-points layer is installed before firing the
    // click. [ORCH-CORRECTED per G3 F1 / HJ A8 / G4 finding 3] Presence, never
    // an exact call tally across effects (the DB-048 flake class).
    await waitFor(() =>
      expect(
        mocks.addLayer.mock.calls.some(
          ([layer]) => (layer as { id?: string }).id === "proposal-drawn-outline-points",
        ),
      ).toBe(true),
    );
    act(() => mocks.fireMapClick({ point: { x: 5, y: 5 }, lngLat: { lng: -73.98, lat: 40.75 } }));
    expect(onDrawnVertexClick).toHaveBeenCalledWith(2);
    expect(onOutlineMapClick).not.toHaveBeenCalled();
  });

  it("pins the wrapper-observed signals: the interactive container's aria-label and the loading node's testid (DB-047(d) drift guard)", async () => {
    // [ORCH-CORRECTED per G4 advisory 4 + HJ B2] ProposalOutlineMap classifies
    // this leaf's surface by querying these two rendered signals verbatim
    // (the interactive aria-label, and lot-outline-loading during the load
    // window). A rename here would silently degrade the wrapper's copy —
    // fail-safe but unannounced, with every unit suite still green — so pin
    // both against the REAL leaf.
    render(<LotOutlineMap bbl="1008350041" fetchImpl={singleLot()} drawnOverlay={emptyOverlay} />);
    expect(screen.getByTestId("lot-outline-loading")).toBeInTheDocument();
    await screen.findByTestId("lot-outline-map");
    expect(screen.getByLabelText("Interactive approximate lot outline map")).toBeInTheDocument();
  });

  it("AS-2 early-click guard: a click BEFORE the overlay layer is installed places a point and never queries the missing drawn-vertex layer", async () => {
    // Map never reaches 'rendered' (no parcel render), so the overlay effect
    // never installs its source/layers — reproducing the real window between the
    // click listener attaching (at construction) and overlay readiness.
    mocks.state.autoRender = false;
    // A hit WOULD be returned if the (absent) drawn-vertex layer were queried.
    mocks.state.overlayHit.push({ properties: { index: 3 } });
    const onOutlineMapClick = vi.fn();
    const onDrawnVertexClick = vi.fn();
    render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={singleLot()}
        onOutlineMapClick={onOutlineMapClick}
        onDrawnVertexClick={onDrawnVertexClick}
        drawnOverlay={emptyOverlay}
      />,
    );
    await screen.findByTestId("lot-outline-map");
    await waitFor(() => expect(mocks.state.clickListeners.length).toBeGreaterThan(0));
    // The drawn-vertex layer is NOT installed (map not ready).
    expect(
      mocks.addLayer.mock.calls.some(
        ([layer]) => (layer as { id?: string }).id === "proposal-drawn-outline-points",
      ),
    ).toBe(false);
    act(() => mocks.fireMapClick({ point: { x: 5, y: 5 }, lngLat: { lng: -73.98, lat: 40.75 } }));
    // Guarded: with no drawn-vertex layer to hit, the click PLACES a point and
    // the configured overlayHit is NEVER consulted. Reverting the getLayer guard
    // turns this red (the unguarded query returns the hit and routes to select).
    expect(onOutlineMapClick).toHaveBeenCalledWith({ lng: -73.98, lat: 40.75 });
    expect(onDrawnVertexClick).not.toHaveBeenCalled();
  });

  it("AS-1 sync: renders the drawn overlay as its own source + 2 layers, then updates it in place via setData (never a second source)", async () => {
    // DB-048 hardening: this spec previously asserted the EXACT cross-render
    // addLayer tally (`toHaveBeenCalledTimes(4)`), which flaked "expected 4, got
    // 6" — a fresh fetchImpl on each render changed the fetched geometry
    // identity and rebuilt the map, re-adding the two lot-outline layers between
    // the overlay install and the assertion. The teeth that matter are now pinned
    // by two defect-specific assertions that stay deterministic under extra effect
    // passes AND under a legitimate whole-map rebuild:
    //   • DUPLICATE-SOURCE defect (dropping the component's `getSource(id) ?
    //     setData : addSource` guard so an update re-adds the source on the SAME
    //     live map): the offending map instance's own overlay-source creation
    //     count climbs past 1 → the per-instance `every(n <= 1)` assertion reds.
    //     Checked PER INSTANCE (not a module-wide tally), so a fresh rebuilt map
    //     legitimately creating the source once more does NOT false-fail.
    //   • STALE-FINAL-PAYLOAD defect (the in-place update calls setData with an
    //     outdated collection — e.g. a captured/previous value — so the map's
    //     last drawn state is stale): `toHaveBeenLastCalledWith(overlay2)` reds.
    //     A plain `toHaveBeenCalledWith(overlay2)` would NOT — overlay2 still sits
    //     somewhere earlier in the call history — which is why we assert the FINAL
    //     payload, not mere presence in history.
    // A STABLE fetchImpl (fresh Response per call, one identity) also removes the
    // rebuild churn at the root, so the happy path builds exactly one instance.
    const overlay2 = {
      type: "FeatureCollection" as const,
      features: [
        {
          type: "Feature" as const,
          properties: { index: 0, selected: false },
          geometry: { type: "Point" as const, coordinates: [-73.98, 40.75] as [number, number] },
        },
      ],
    };
    const stableFetch = vi.fn(() =>
      Promise.resolve(jsonResponse(fixture("single_lot_polygon"))),
    ) as unknown as typeof fetch;
    const { rerender } = render(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={stableFetch}
        onOutlineMapClick={vi.fn()}
        onDrawnVertexClick={vi.fn()}
        drawnOverlay={emptyOverlay}
      />,
    );
    await screen.findByTestId("lot-outline-map");
    // Final state: the overlay source exists with BOTH its layers installed
    // (presence, not an exact cross-render total).
    await waitFor(() => expect(mocks.state.sources["proposal-drawn-outline"]).toBeDefined());
    const overlayLayerIds = mocks.addLayer.mock.calls
      .map(([layer]) => (layer as { id: string }).id)
      .filter((id) => id === "proposal-drawn-outline-line" || id === "proposal-drawn-outline-points");
    expect(overlayLayerIds).toContain("proposal-drawn-outline-line");
    expect(overlayLayerIds).toContain("proposal-drawn-outline-points");
    expect(mocks.addSource).toHaveBeenCalledWith("proposal-drawn-outline", expect.anything());

    rerender(
      <LotOutlineMap
        bbl="1008350041"
        fetchImpl={stableFetch}
        onOutlineMapClick={vi.fn()}
        onDrawnVertexClick={vi.fn()}
        drawnOverlay={overlay2}
      />,
    );
    // FINAL setData payload (not merely "overlay2 appeared in the call history").
    // The overlay updates IN PLACE, so the LIVE source's LAST setData call must
    // carry the fresh collection. Read the source fresh at assert time so the
    // assertion follows the live map even if any rebuild replaced the object.
    await waitFor(() =>
      expect(
        mocks.state.sources["proposal-drawn-outline"].setData,
      ).toHaveBeenLastCalledWith(overlay2),
    );
    // NEVER a duplicate source WITHIN a live map instance: the overlay source is
    // created once per map and every later change goes through setData. Asserted
    // on PER-INSTANCE creation counts, not a module-wide addSource tally: a
    // legitimate setup pass (a whole-map rebuild) spins up a fresh instance that
    // adds the source once more, which a module-wide tally would wrongly read as a
    // duplicate. A real duplicate-source defect drives one instance's count past 1.
    const overlayAddsPerInstance = mocks.state.mapInstances.map(
      (m) => m.sourceAddCounts["proposal-drawn-outline"] ?? 0,
    );
    // The overlay source WAS created (the interactive overlay really installed) …
    expect(overlayAddsPerInstance.some((n) => n === 1)).toBe(true);
    // … and NO single map instance created it more than once.
    expect(overlayAddsPerInstance.every((n) => n <= 1)).toBe(true);
    // (g)/(G4 finding 2) With a STABLE fetchImpl the happy path builds EXACTLY
    // ONE map instance — so this spec now also proves the overlay updated IN
    // PLACE, WITHOUT a whole-map rebuild (the dimension the removed cross-render
    // addLayer tally used to cover). A rebuild would push a second instance and
    // red this.
    expect(mocks.state.mapInstances).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// [ORCH-CORRECTED per M5-T025-G3 F1] Component-level WIRING GUARD that the
// fix is actually wired in: with the mock configured to "style already
// loaded before the wiring attaches", the map still draws. This scenario is
// the mock's proxy for "the draw step must not hang on a single bare
// on('load') contingency" — the reachable production failure was "load"
// never firing on a degraded-rendering device (see the module ROOT CAUSE
// comment), which the style.load arm closes. A component still built on
// bare `on("load", ...)` leaves the map undrawn here (red-on-old), because
// this mock's `once()` mirrors one-time-event semantics while the old
// mock's `on("load", cb)` unconditionally queueMicrotask'd cb and could
// never have caught any missed-draw bug.
// ---------------------------------------------------------------------------
describe("LotOutlineMap — root-cause regression: style already loaded before wiring attaches", () => {
  beforeEach(() => enableWebgl());

  it("draws the outline even when the style is ALREADY loaded by the time draw-wiring attaches", async () => {
    mocks.setStyleAlreadyLoaded(true);
    const fx = fixture("single_lot_polygon");
    render(
      <LotOutlineMap bbl="1008350041" fetchImpl={fetchReturning(jsonResponse(fx))} />,
    );
    expect(await screen.findByTestId("lot-outline-map")).toBeInTheDocument();
    await waitFor(() => expect(mocks.addSource).toHaveBeenCalled());
    // The draw step ran: both lot-outline layers installed (DB-049 h: presence,
    // not an exact tally).
    const ids = addedLayerIds();
    expect(ids).toContain("lot-outline-fill");
    expect(ids).toContain("lot-outline-line");
    expect(mocks.fitBounds).toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// D-056-R002 hardening: a map "error" event (WebGL context loss, a
// style/source/layer failure) was previously UNHANDLED. It now routes to a
// typed fallback instead of leaving a permanently blank/gray map.
// ---------------------------------------------------------------------------
describe("LotOutlineMap — map 'error' event routes to a typed fallback (D-056-R002 hardening)", () => {
  beforeEach(() => enableWebgl());

  it("an 'error' event after construction replaces the map with an honest fallback, never a silent blank map", async () => {
    const fx = fixture("single_lot_polygon");
    render(
      <LotOutlineMap bbl="1008350041" fetchImpl={fetchReturning(jsonResponse(fx))} />,
    );
    expect(await screen.findByTestId("lot-outline-map")).toBeInTheDocument();
    // The container mounts before the dynamic MapLibre import attaches events.
    // Exercise the documented post-construction error, not an unobserved event.
    await waitFor(() => expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered"));
    act(() => mocks.fireMapError());
    expect(
      await screen.findByTestId("lot-outline-render-error"),
    ).toBeInTheDocument();
    expect(screen.queryByTestId("lot-outline-map")).toBeNull();
    // The +/-20 ft copy and attribution stay visible (same honest-fallback
    // shape as the other typed states) and the summary matches what's shown.
    expect(screen.getByTestId("lot-outline-accuracy").textContent).toContain(
      "20 ft",
    );
    const summary = screen.getByTestId("lot-outline-summary").textContent ?? "";
    expect(summary).toContain("could not be rendered");
  });
});


describe("M5-T029 source-backed street context", () => {
  it("does not announce an outline from layer installation alone; waits for loaded and rendered parcel features", async () => {
    enableWebgl();
    mocks.state.autoRender = false;
    mocks.state.sourceLoaded = false;
    render(<LotOutlineMap bbl="1008350041" context fetchImpl={fetchReturning(jsonResponse(fixture("single_lot_polygon")))} />);
    // Wait until both lot-outline layers are installed (DB-049 h: presence, not an
    // exact cross-render tally) — then prove the outline is NOT yet announced.
    await waitFor(() => {
      const ids = addedLayerIds();
      expect(ids).toContain("lot-outline-fill");
      expect(ids).toContain("lot-outline-line");
    });
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "loading");
    expect(screen.getByTestId("lot-outline-summary")).toHaveTextContent("Loading the selected parcel outline");
    act(() => mocks.state.renderListeners.forEach(listener => listener()));
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "loading");
    mocks.state.sourceLoaded = true;
    act(() => mocks.state.renderListeners.forEach(listener => listener()));
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered");
    expect(screen.getByTestId("lot-outline-summary")).toHaveTextContent("An approximate lot outline is shown");
    expect(mocks.state.renderListeners).toHaveLength(0);
  });

  it("bounds a stalled GeoJSON worker with an honest fallback and disposes the map without accepting late renders", async () => {
    enableWebgl();
    vi.useFakeTimers();
    mocks.state.autoRender = false;
    render(<LotOutlineMap bbl="1008350041" context fetchImpl={fetchReturning(jsonResponse(fixture("single_lot_polygon")))} />);
    await act(async () => { await vi.advanceTimersByTimeAsync(1); });
    await act(async () => { await vi.dynamicImportSettled(); });
    expect(mocks.state.renderListeners).toHaveLength(1);
    const lateRender = mocks.state.renderListeners[0];
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "unavailable");
    expect(screen.getByTestId("lot-outline-render-error")).toHaveTextContent("interactive map could not be rendered");
    expect(screen.queryByTestId("lot-outline-map")).not.toBeInTheDocument();
    expect(screen.getByTestId("lot-outline-accuracy")).toHaveTextContent("±20 ft");
    expect(mocks.remove).toHaveBeenCalledTimes(1);
    expect(mocks.state.renderListeners).toHaveLength(0);
    act(lateRender);
    expect(screen.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "unavailable");
  });

  it("disposes an outstanding parcel render observation when the view unmounts", async () => {
    enableWebgl();
    mocks.state.autoRender = false;
    const { unmount } = render(<LotOutlineMap bbl="1008350041" context fetchImpl={fetchReturning(jsonResponse(fixture("single_lot_polygon")))} />);
    await waitFor(() => expect(mocks.state.renderListeners).toHaveLength(1));
    unmount();
    expect(mocks.state.renderListeners).toHaveLength(0);
    expect(mocks.remove).toHaveBeenCalledTimes(1);
  });

  it("keeps the parcel available when an individual street layer fails", async () => {
    enableWebgl();
    render(<LotOutlineMap bbl="1008350041" context fetchImpl={fetchReturning(jsonResponse(fixture("single_lot_polygon")))} />);
    await waitFor(() => expect(mocks.addSource).toHaveBeenCalled());
    expect(screen.getByRole("button", { name: "Recenter lot" })).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: "Zoning boundaries" })).not.toBeChecked();
    expect(screen.getByTestId("lot-outline-accuracy")).toHaveTextContent("Approximate outline · ±20 ft · NYC Department of City Planning / MapPLUTO");
    expect(screen.getByTestId("lot-outline-accuracy")).not.toHaveTextContent("EPSG");
    expect(screen.getByTestId("lot-outline-technical-accuracy")).not.toBeVisible();
    fireEvent.click(screen.getByText("Map sources and limitations", { exact: true }));
    expect(screen.getByTestId("lot-outline-technical-accuracy")).toBeVisible();
    expect(screen.getByTestId("lot-outline-technical-accuracy")).toHaveTextContent("EPSG:4326");
    act(() => mocks.fireMapError("nyc-basemap"));
    expect(screen.getByText(/Street basemap: unavailable/)).toBeInTheDocument();
    expect(screen.getByTestId("lot-outline-map")).toBeInTheDocument();
    expect(screen.queryByTestId("lot-outline-render-error")).not.toBeInTheDocument();
    Object.defineProperties(screen.getByTestId("lot-outline-map"), {
      clientWidth: { value: 640 }, clientHeight: { value: 480 },
    });
    fireEvent.click(screen.getByRole("button", { name: "Recenter lot" }));
    expect(mocks.fitBounds).toHaveBeenLastCalledWith(expect.any(Array), { padding: 72, duration: 0, maxZoom: 18.5 });
  });
});
