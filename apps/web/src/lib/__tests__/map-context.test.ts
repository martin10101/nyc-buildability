import { describe, expect, it } from "vitest";
import { NYC_CONTEXT_STYLE, contextLayerName } from "../map-context";
import { parseZoningContext, zoningContextRequest, fetchZoningContext } from "../architect/zoning-context";
import { officialZoningTextUrl } from "../architect/source-links";

const polygon = { type: "Feature", properties: { OBJECTID: 1, ZONEDIST: "R5" }, geometry: { type: "Polygon", coordinates: [[[-74,40],[-73.99,40],[-73.99,40.01],[-74,40]]] } };
const collection = { type: "FeatureCollection", features: [polygon] };
describe("source-backed map context", () => {
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
