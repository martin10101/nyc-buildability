/** MapLibre 6's GeoJSON worker must be explicitly hosted with its shared module
 * under Next. These are exact assets from the lock-admitted package, checked by
 * the map-context parity test. No source URL or user input selects executable code. */
export const MAPLIBRE_WORKER_URL = "/maplibre/6.7.0/maplibre-gl-worker.mjs";

export interface ParcelRenderMap {
  on(type: string, callback: () => void): void;
  off(type: string, callback: () => void): void;
  isSourceLoaded(id: string): boolean;
  getLayer(id: string): unknown;
  queryRenderedFeatures(options: { layers: string[] }): Array<{ source?: string; layer?: { id?: string } }>;
}

/** Observe actual rendered parcel features, not successful addLayer calls or
 * raster readiness. The owning map lifecycle supplies the bounded deadline and
 * failure state, and always disposes this listener on success/error/unmount. */
export function observeParcelRender(map: ParcelRenderMap, onRendered: () => void): () => void {
  let active = true;
  const layers = ["lot-outline-fill", "lot-outline-line"];
  const dispose = () => { active = false; map.off("render", check); };
  function check() {
    if (!active || !layers.every(id => map.getLayer(id)) || !map.isSourceLoaded("lot-outline")) return;
    const features = map.queryRenderedFeatures({ layers });
    if (!layers.every(id => features.some(feature => feature.source === "lot-outline" && feature.layer?.id === id))) return;
    dispose();
    onRendered();
  }
  map.on("render", check);
  return dispose;
}
