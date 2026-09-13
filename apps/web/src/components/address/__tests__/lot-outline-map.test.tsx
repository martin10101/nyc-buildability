import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LotOutlineMap } from "@/components/address/LotOutlineMap";

/**
 * M5-T023 pack for LotOutlineMap. maplibre-gl is mocked at the MODULE boundary
 * (the component dynamic-imports it) so this runs offline with no WebGL: the
 * mock records exactly what geometry reaches the map source, proving the
 * contract geometry is drawn VERBATIM (every ring, every polygon) and never
 * recomputed. Each typed outcome is asserted to render its honest state.
 */

const mocks = vi.hoisted(() => {
  const mapCtor = vi.fn();
  const addSource = vi.fn();
  const addLayer = vi.fn();
  const addControl = vi.fn();
  const fitBounds = vi.fn();
  const remove = vi.fn();
  const attributionCtor = vi.fn();

  class MockMap {
    constructor(options: unknown) {
      mapCtor(options);
    }
    on(type: string, cb: () => void) {
      if (type === "load") queueMicrotask(cb);
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
  return {
    mapCtor,
    addSource,
    addLayer,
    addControl,
    fitBounds,
    remove,
    attributionCtor,
    MockMap,
    MockAttributionControl,
  };
});

vi.mock("maplibre-gl", () => ({
  default: { Map: mocks.MockMap, AttributionControl: mocks.MockAttributionControl },
  Map: mocks.MockMap,
  AttributionControl: mocks.MockAttributionControl,
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

    const [, source] = mocks.addSource.mock.calls[0] as [string, { data: { geometry: unknown } }];
    // The geometry handed to MapLibre EQUALS the fixture geometry — untouched.
    expect(source.data.geometry).toEqual(fx.geometry);
    // A fill + a line layer, camera framed, attribution control added.
    expect(mocks.addLayer).toHaveBeenCalledTimes(2);
    expect(mocks.fitBounds).toHaveBeenCalled();
    expect(mocks.attributionCtor).toHaveBeenCalledWith(
      expect.objectContaining({
        customAttribution: expect.stringContaining("City Planning"),
      }),
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
  });
});
