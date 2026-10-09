/** Official DCP NYZD boundaries for display only; no client-side lot zoning determination. */
export const ZONING_CONTEXT_URL = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer/0/query";
export type ContextBounds = [
    [
        number,
        number
    ],
    [
        number,
        number
    ]
];
export interface ZoningContextFeature {
    type: "Feature";
    properties: {
        OBJECTID: number;
        ZONEDIST: string | null;
    };
    geometry: {
        type: "Polygon" | "MultiPolygon";
        coordinates: number[][][] | number[][][][];
    };
}
export interface ZoningContextCollection {
    type: "FeatureCollection";
    features: ZoningContextFeature[];
}
export type ZoningContextOutcome = {
    kind: "context";
    data: ZoningContextCollection;
} | {
    kind: "unavailable";
} | {
    kind: "aborted";
};
export function zoningContextRequest(bounds: ContextBounds): string | null {
    const [west, south] = bounds[0], [east, north] = bounds[1];
    if (![west, south, east, north].every(Number.isFinite) || west < -180 || east > 180 || south < -90 || north > 90 || west >= east || south >= north || east - west > .2 || north - south > .2)
        return null;
    const params = new URLSearchParams({ f: "geojson", where: "1=1", geometry: `${west},${south},${east},${north}`, geometryType: "esriGeometryEnvelope", inSR: "4326", spatialRel: "esriSpatialRelIntersects", outFields: "OBJECTID,ZONEDIST", outSR: "4326", returnGeometry: "true", orderByFields: "OBJECTID ASC", resultRecordCount: "100" });
    return `${ZONING_CONTEXT_URL}?${params}`;
}
export function parseZoningContext(body: unknown): ZoningContextCollection | null {
    if (!body || typeof body !== "object")
        return null;
    const value = body as Record<string, unknown>;
    const meta = value.properties as Record<string, unknown> | undefined;
    if (value.type !== "FeatureCollection" || value.error || meta?.exceededTransferLimit || !Array.isArray(value.features) || value.features.length > 100)
        return null;
    let pointCount = 0;
    for (const feature of value.features) {
        if (!feature || feature.type !== "Feature" || !feature.geometry || !feature.properties)
            return null;
        if (!Number.isInteger(feature.properties.OBJECTID) || !(feature.properties.ZONEDIST === null || (typeof feature.properties.ZONEDIST === "string" && /^[A-Z0-9 /-]{1,15}$/.test(feature.properties.ZONEDIST))))
            return null;
        const geometry = feature.geometry;
        if (!["Polygon", "MultiPolygon"].includes(geometry.type) || !Array.isArray(geometry.coordinates))
            return null;
        const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates;
        if (!polygons.length)
            return null;
        for (const polygon of polygons) {
            if (!Array.isArray(polygon) || !polygon.length)
                return null;
            for (const ring of polygon) {
                if (!Array.isArray(ring) || ring.length < 4)
                    return null;
                for (const position of ring) {
                    if (++pointCount > 30000 || !Array.isArray(position) || position.length !== 2 || !position.every((n: unknown) => typeof n === "number" && Number.isFinite(n)) || Math.abs(position[0]) > 180 || Math.abs(position[1]) > 90)
                        return null;
                }
                if (ring[0][0] !== ring[ring.length - 1][0] || ring[0][1] !== ring[ring.length - 1][1])
                    return null;
            }
        }
    }
    return { type: "FeatureCollection", features: value.features as ZoningContextFeature[] };
}
export async function fetchZoningContext(bounds: ContextBounds, signal: AbortSignal, fetchImpl: typeof fetch = fetch): Promise<ZoningContextOutcome> {
    const url = zoningContextRequest(bounds);
    if (!url)
        return { kind: "unavailable" };
    const controller = new AbortController();
    let finish: () => void = () => undefined;
    const stopped = new Promise<ZoningContextOutcome>(resolve => { finish = () => { controller.abort(); resolve(signal.aborted ? { kind: "aborted" } : { kind: "unavailable" }); }; });
    if (signal.aborted)
        return { kind: "aborted" };
    signal.addEventListener("abort", finish, { once: true });
    const timeout = setTimeout(finish, 8000);
    const request = (async (): Promise<ZoningContextOutcome> => {
        try {
            const response = await fetchImpl(url, { signal: controller.signal, credentials: "omit", referrerPolicy: "no-referrer", headers: { Accept: "application/geo+json, application/json" } });
            if (!response.ok || !response.headers.get("content-type")?.includes("json") || !response.body)
                return { kind: "unavailable" };
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let text = "", bytes = 0;
            try {
                for (;;) {
                    const result = await reader.read();
                    if (result.done)
                        break;
                    bytes += result.value.byteLength;
                    if (bytes > 1500000)
                        return { kind: "unavailable" };
                    text += decoder.decode(result.value, { stream: true });
                }
            }
            finally {
                await reader.cancel().catch(() => undefined);
            }
            const data = parseZoningContext(JSON.parse(text + decoder.decode()));
            return data ? { kind: "context", data } : { kind: "unavailable" };
        }
        catch {
            return signal.aborted ? { kind: "aborted" } : { kind: "unavailable" };
        }
    })();
    try {
        return await Promise.race([request, stopped]);
    }
    finally {
        clearTimeout(timeout);
        signal.removeEventListener("abort", finish);
    }
}
