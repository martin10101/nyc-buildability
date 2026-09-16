import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  LOT_OUTLINE_MAX_ZOOM,
  LotOutlineMap,
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
  const attributionCtor = vi.fn();
  const navigationCtor = vi.fn();
  const setWorkerUrl = vi.fn();
  const state = {
    styleAlreadyLoaded: false,
    autoRender: true,
    sourceLoaded: true,
    renderListeners: [] as Array<() => void>,
    errorListeners: [] as Array<(event?: { sourceId?: string }) => void>,
  };

  class MockMap {
    constructor(options: unknown) {
      mapCtor(options);
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
    queryRenderedFeatures() {
      return ["lot-outline-fill", "lot-outline-line"].map(id => ({ source: "lot-outline", layer: { id } }));
    }
    addSource(id: string, source: unknown) {
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

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.clearAllMocks();
  mocks.setStyleAlreadyLoaded(false);
  mocks.state.errorListeners.length = 0;
  mocks.state.renderListeners.length = 0;
  mocks.state.autoRender = true;
  mocks.state.sourceLoaded = true;
  vi.useRealTimers();
});

describe("LotOutlineMap — single_lot with WebGL", () => {
  beforeEach(() => enableWebgl());

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
    // A fill + a line layer, camera framed, attribution control added.
    expect(mocks.addLayer).toHaveBeenCalledTimes(2);
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
        bbl="1008350096"
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
  it("raises maxZoom above the prior fingernail-size cap of 18", () => {
    const options = lotOutlineFitBoundsOptions();
    expect(options.maxZoom).toBe(LOT_OUTLINE_MAX_ZOOM);
    expect(options.maxZoom).toBeGreaterThan(18);
    expect(options.padding).toBe(24);
    expect(options.duration).toBe(0);
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
    expect(mocks.addLayer).toHaveBeenCalledTimes(2);
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
    await waitFor(() => expect(mocks.addLayer).toHaveBeenCalledTimes(2));
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
    fireEvent.click(screen.getByRole("button", { name: "Recenter lot" }));
    expect(mocks.fitBounds).toHaveBeenLastCalledWith(expect.any(Array), { padding: 72, duration: 0, maxZoom: 18.5 });
  });
});
