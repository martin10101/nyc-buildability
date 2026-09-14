"use client";
import { useEffect, useState } from "react";
import type { ContextBounds } from "@/lib/architect/zoning-context";
import { useZoningContext } from "@/lib/architect/use-zoning-context";

export interface ZoningContextMap {
  on(type: string, listener: (event?: { sourceId?: string }) => void): void;
  off?(type: string, listener: (event?: { sourceId?: string }) => void): void;
  addSource(id: string, source: unknown): void;
  addLayer(layer: unknown, beforeId?: string): void;
  getLayer(id: string): unknown;
  removeLayer(id: string): void;
  getSource(id: string): unknown;
  removeSource(id: string): void;
}

/** Map layer lifecycle; the bounded network operation lives in useZoningContext. */
export function ZoningContextControl({ map, bounds }: { map: ZoningContextMap; bounds: ContextBounds }) {
  const [enabled, setEnabled] = useState(false);
  const [drawStatus, setDrawStatus] = useState("");
  const result = useZoningContext(bounds, enabled);
  useEffect(() => {
    if (result?.kind !== "context") return;
    let current = true;
    const onError = (event?: { sourceId?: string }) => {
      if (current && event?.sourceId === "nyc-zoning-context") setDrawStatus("unavailable");
    };
    map.on("error", onError);
    try {
      map.addSource("nyc-zoning-context", { type: "geojson", data: result.data });
      map.addLayer({ id: "nyc-zoning-boundaries", type: "line", source: "nyc-zoning-context", paint: { "line-color": "#60758b", "line-width": 2, "line-dasharray": [4, 3] } }, "lot-outline-fill");
      const districts = [...new Set(result.data.features.map(feature => feature.properties.ZONEDIST).filter(Boolean))];
      setDrawStatus(result.data.features.length === 0 ? "no nearby boundaries returned" : districts.length ? `loaded: ${districts.join(", ")}` : "loaded; district labels not supplied");
    } catch { setDrawStatus("unavailable"); }
    return () => {
      current = false;
      map.off?.("error", onError);
      try {
        if (map.getLayer("nyc-zoning-boundaries")) map.removeLayer("nyc-zoning-boundaries");
        if (map.getSource("nyc-zoning-context")) map.removeSource("nyc-zoning-context");
      } catch { /* Parent map may already have been removed. */ }
    };
  }, [map, result]);
  const status = !result ? "loading" : result.kind === "context" ? drawStatus : "unavailable";
  return <div className="architect-zoning-context">
    <label><input type="checkbox" checked={enabled} onChange={event => setEnabled(event.target.checked)} /> Zoning boundaries</label>
    {enabled ? <p className="section-note" role="status">Boundary context {status}. Not a lot zoning determination. <a href="https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf" target="_blank" rel="noopener noreferrer">NYC DCP source / ±20 ft accuracy ↗</a></p> : null}
  </div>;
}
