import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";
import { NYC_CONTEXT_STYLE, contextLayerName } from "../map-context";
import { parseZoningContext, zoningContextRequest, fetchZoningContext } from "../architect/zoning-context";
import { officialZoningTextUrl } from "../architect/source-links";
import { MAPLIBRE_WORKER_URL, observeParcelRender } from "../architect/map-runtime";

const polygon = { type: "Feature", properties: { OBJECTID: 1, ZONEDIST: "R5" }, geometry: { type: "Polygon", coordinates: [[[-74,40],[-73.99,40],[-73.99,40.01],[-74,40]]] } };
const collection = { type: "FeatureCollection", features: [polygon] };
describe("source-backed map context", () => {
  it("ships the exact admitted MapLibre worker, sibling module and license on the fixed same-origin path", () => {
    const installed = resolve(process.cwd(), "node_modules/maplibre-gl");
    const packageVersion = JSON.parse(readFileSync(resolve(installed, "package.json"), "utf8")).version;
    expect(packageVersion).toBe("6.7.0");
    expect(MAPLIBRE_WORKER_URL).toBe(`/maplibre/${packageVersion}/maplibre-gl-worker.mjs`);
    for (const file of ["maplibre-gl-worker.mjs", "maplibre-gl-shared.mjs", "LICENSE.txt"]) {
      const original = readFileSync(resolve(installed, file === "LICENSE.txt" ? file : `dist/${file}`));
      const hosted = readFileSync(resolve(process.cwd(), `public/maplibre/${packageVersion}/${file}`));
      expect(hosted.equals(original), `${file} must remain byte-identical to the lock-admitted distribution`).toBe(true);
    }
  });

  it("requires the parcel source and both visible parcel layers, then stops observing", () => {
    let render = () => {};
    const map = {
      on: (_event: string, listener: () => void) => { render = listener; }, off: vi.fn(),
      getLayer: vi.fn().mockReturnValue({}), isSourceLoaded: vi.fn().mockReturnValue(false),
      queryRenderedFeatures: vi.fn().mockReturnValue([]),
    };
    const shown = vi.fn();
    observeParcelRender(map, shown);
    render();
    expect(map.queryRenderedFeatures).not.toHaveBeenCalled();
    map.isSourceLoaded.mockReturnValue(true);
    render();
    expect(shown).not.toHaveBeenCalled();
    map.queryRenderedFeatures.mockReturnValue([{ source: "lot-outline", layer: { id: "lot-outline-fill" } }]);
    render();
    expect(shown).not.toHaveBeenCalled();
    map.queryRenderedFeatures.mockReturnValue(["lot-outline-fill", "lot-outline-line"].map(id => ({ source: "nyc-basemap", layer: { id } })));
    render();
    expect(shown).not.toHaveBeenCalled();
    map.queryRenderedFeatures.mockReturnValue(["lot-outline-fill", "lot-outline-line"].map(id => ({ source: "lot-outline", layer: { id } })));
    render(); render();
    expect(map.isSourceLoaded).toHaveBeenCalledWith("lot-outline");
    expect(map.queryRenderedFeatures).toHaveBeenCalledWith({ layers: ["lot-outline-fill", "lot-outline-line"] });
    expect(shown).toHaveBeenCalledTimes(1);
    expect(map.off).toHaveBeenCalledWith("render", render);
  });

  it("uses only fixed official raster templates with source attribution", () => {
    expect(NYC_CONTEXT_STYLE.sources["nyc-basemap"].tiles).toEqual(["https://maps.nyc.gov/xyz/1.0.0/carto/basemap/{z}/{x}/{y}.jpg"]);
    expect(NYC_CONTEXT_STYLE.sources["nyc-labels"].tileSize).toBe(256);
    expect(NYC_CONTEXT_STYLE.sources["nyc-basemap"].attribution).toContain("City of New York");
    expect(contextLayerName("lot-outline")).toBeNull();
  });
  it("bounds zoning requests and retains returned polygon coordinates verbatim", () => {
    const url = new URL(zoningContextRequest([[-74.014,40.705],[-74.007,40.712]])!);
    expect(url.searchParams.get("resultRecordCount")).toBe("100");
    expect(url.searchParams.get("inSR")).toBe("4326");
    expect(zoningContextRequest([[-75,40],[-73,42]])).toBeNull();
    expect(zoningContextRequest([[NaN,40],[-73,42]])).toBeNull();
    expect(parseZoningContext(collection)?.features[0].geometry.coordinates).toBe(polygon.geometry.coordinates);
  });
  it.each([
    [10, "M1-2/R6"],
    [114, "M1-4/R6A"],
    [132, "M1-2/R6B"],
  ])("retains official NYZD mixed-district label for OBJECTID %i", (OBJECTID, ZONEDIST) => {
    // Label/ID pairs verified against NYZD; the polygon is the local geometry fixture.
    const feature = { ...polygon, properties: { OBJECTID, ZONEDIST } };
    const result = parseZoningContext({ ...collection, features: [feature] });
    expect(result?.features[0].properties).toEqual({ OBJECTID, ZONEDIST });
    expect(result?.features[0].geometry.coordinates).toBe(polygon.geometry.coordinates);
  });
  it("keeps mixed-district metadata bounded and rejects unrelated characters", () => {
    for (const ZONEDIST of [42, "", "M1-2/R6".repeat(3), "M1-2\\R6", "<R6>"]) {
      expect(parseZoningContext({ ...collection, features: [{ ...polygon, properties: { OBJECTID: 10, ZONEDIST } }] })).toBeNull();
    }
  });
  it("withholds partial, malformed, open-ring and oversized boundary data", () => {
    expect(parseZoningContext({ ...collection, properties: { exceededTransferLimit: true } })).toBeNull();
    expect(parseZoningContext({ error: { message: "unavailable" } })).toBeNull();
    const bad = structuredClone(collection); bad.features[0].geometry.coordinates[0][3] = [-73,41];
    expect(parseZoningContext(bad)).toBeNull();
    expect(parseZoningContext({ ...collection, features: Array(101).fill(polygon) })).toBeNull();
  });
  it("handles source failure and cancellation without returning geometry", async () => {
    expect(await fetchZoningContext([[-74.014,40.705],[-74.007,40.712]], new AbortController().signal, async () => new Response('{"error":{}}', { headers: { "content-type": "application/json" } }))).toEqual({ kind: "unavailable" });
    const controller = new AbortController(); controller.abort();
    expect(await fetchZoningContext([[-74.014,40.705],[-74.007,40.712]], controller.signal)).toEqual({ kind: "aborted" });
  });
  it("allows exact official zoning text forms and rejects reflected arbitrary URLs", () => {
    expect(officialZoningTextUrl("https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21")).toBe("https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21");
    expect(officialZoningTextUrl("https://zoningresolution.planning.nyc.gov/article-iii/chapter-3#33-121")).not.toBeNull();
    for (const url of ["javascript:alert(1)", "https://evil.example/article-ii/chapter-3", "https://user@zoningresolution.planning.nyc.gov/article-ii/chapter-3", "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3?redirect=evil", "https://zoningresolution.planning.nyc.gov/unknown", "https://zoningresolution.planning.nyc.gov.evil.example/article-ii/chapter-3"]) expect(officialZoningTextUrl(url)).toBeNull();
  });
});
