/** Official NYC tiled basemap. Sources, tile sizes, bounds and CORS verified by M5-T029 G1. */
export const NYC_MAP_ATTRIBUTION = '<a href="https://maps.nyc.gov/tiles/" target="_blank" rel="noopener noreferrer">© City of New York</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0</a>';
export const NYC_CONTEXT_STYLE = {
    version: 8 as const,
    sources: {
        "nyc-basemap": { type: "raster", tiles: ["https://maps.nyc.gov/xyz/1.0.0/carto/basemap/{z}/{x}/{y}.jpg"], tileSize: 256, minzoom: 8, maxzoom: 21, bounds: [-75.9374, 39.3682, -71.7187, 42.0329], attribution: NYC_MAP_ATTRIBUTION },
        "nyc-labels": { type: "raster", tiles: ["https://maps.nyc.gov/xyz/1.0.0/carto/label/{z}/{x}/{y}.png8"], tileSize: 256, minzoom: 8, maxzoom: 21, bounds: [-74.2727, 40.0341, -71.9101, 41.2919] },
    },
    layers: [
        { id: "lot-outline-background", type: "background", paint: { "background-color": "#f1eee5" } },
        { id: "nyc-basemap", type: "raster", source: "nyc-basemap" },
        { id: "nyc-labels", type: "raster", source: "nyc-labels" },
    ],
};
export function contextLayerName(sourceId: unknown): string | null {
    return sourceId === "nyc-basemap" ? "Street basemap" : sourceId === "nyc-labels" ? "Street labels" : null;
}
