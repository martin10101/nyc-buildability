"use client";

import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import type { LotOutlineOutcome, ValidatedGeometry } from "@/lib/lot-geometry-api";
import { MAPLIBRE_WORKER_URL } from "@/lib/architect/map-runtime";
import { isMapContainerVisible, observeMapContainer } from "@/lib/architect/map-container";
import { NYC_CONTEXT_STYLE, contextLayerName } from "@/lib/map-context";
import { zolaLotUrl } from "@/lib/provenance-link";

export interface ParcelStudyOutline {
  bbl: string;
  outcome: LotOutlineOutcome | null;
  loading: boolean;
}

export interface ParcelStudyMapProps {
  outlines: ParcelStudyOutline[];
  arrangement: "together" | "separate" | "compare";
  compact?: boolean;
}

interface StudyFeature {
  type: "Feature";
  properties: { bbl: string; color: string };
  geometry: ValidatedGeometry;
}

interface StudyMap {
  on(type: string, callback: (event?: { sourceId?: string }) => void): void;
  off(type: string, callback: (event?: { sourceId?: string }) => void): void;
  isStyleLoaded(): boolean;
  isSourceLoaded(id: string): boolean;
  getLayer(id: string): unknown;
  queryRenderedFeatures(options: { layers: string[] }): Array<{
    source?: string; layer?: { id?: string }; properties?: { bbl?: string };
  }>;
  addSource(id: string, source: unknown): void;
  addLayer(layer: unknown): void;
  addControl(control: unknown, position: string): void;
  fitBounds(bounds: [[number, number], [number, number]], options: unknown): void;
  resize?(): void;
  remove(): void;
}

interface StudyMarker {
  setLngLat(point: [number, number]): StudyMarker;
  addTo(map: StudyMap): StudyMarker;
  remove(): void;
}

interface StudyMapLibrary {
  setWorkerUrl(url: string): void;
  Map: new (options: unknown) => StudyMap;
  Marker: new (options: { element: HTMLElement }) => StudyMarker;
  AttributionControl: new (options: unknown) => unknown;
  NavigationControl: new (options: unknown) => unknown;
}

const SOURCE = "parcel-study-outlines";
const LAYERS = ["parcel-study-fill", "parcel-study-line"];
const COLORS = ["#a4680c", "#24699a", "#4f6d49", "#82549a"];
const DCP_ATTRIBUTION = "NYC Department of City Planning (DCP), MapPLUTO";

function outlineState(entry: ParcelStudyOutline, duplicate: boolean): {
  geometry: ValidatedGeometry | null; message: string;
} {
  const unavailable = (message: string) => ({ geometry: null, message });
  if (!zolaLotUrl(entry.bbl)) return unavailable("Invalid parcel identifier; outline withheld.");
  if (duplicate) return unavailable("Duplicate parcel records; outline withheld for review.");
  if (entry.loading) return unavailable("Loading outline…");
  const result = entry.outcome;
  if (result === null) return unavailable("Outline not loaded.");
  if (result.kind !== "document") {
    return unavailable(result.kind === "client_timeout" ? "Outline request timed out."
      : result.kind === "route_absent" ? "Outline service unavailable here."
      : result.kind === "aborted" ? "Outline request cancelled."
      : "Outline could not be loaded.");
  }
  const view = result.view;
  if (view.bbl !== entry.bbl) return unavailable("Returned parcel does not match; outline withheld.");
  if (view.outcome === "no_outline") return unavailable(view.noOutlineReason === "condo_unit_lot_no_polygon"
    ? "No parcel outline for this condo record." : "No outline in the source record.");
  if (view.outcome === "multiple_features" || view.reviewRequired) {
    return unavailable("Parcel geometry needs review; outline withheld.");
  }
  if (view.outcome !== "single_lot" || view.geometryUnusable || !view.geometry) {
    return unavailable("Source geometry is unusable; outline withheld.");
  }
  return { geometry: view.geometry, message: "Approximate outline available." };
}

function hasWebgl(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return !!(canvas.getContext("webgl2") || canvas.getContext("webgl") || canvas.getContext("experimental-webgl"));
  } catch { return false; }
}

/** Camera framing only. No union, area, distance, or buildable shape is derived. */
function cameraBounds(features: StudyFeature[]): [[number, number], [number, number]] {
  let west = Infinity, south = Infinity, east = -Infinity, north = -Infinity;
  for (const { geometry } of features) {
    const rings = geometry.type === "Polygon" ? geometry.coordinates : geometry.coordinates.flat();
    for (const ring of rings) for (const [lng, lat] of ring) {
      west = Math.min(west, lng); south = Math.min(south, lat);
      east = Math.max(east, lng); north = Math.max(north, lat);
    }
  }
  return [[west, south], [east, north]];
}

/** The parent owns requests. This component draws only the matching display
 * geometry, preserving every polygon and hole exactly as returned. The study
 * grouping changes colors and labels only; it never creates a legal site. */
function MapRecordList({ compact, children }: { compact: boolean; children: ReactNode }) {
  return compact ? <details className="provenance-details"><summary>Parcel identities, availability &amp; ZoLa links</summary>{children}</details> : <>{children}</>;
}

export function ParcelStudyMap({ outlines, arrangement, compact = false }: ParcelStudyMapProps) {
  const titleId = useId();
  const statusId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [webgl, setWebgl] = useState<boolean | null>(null);
  const [mapStatus, setMapStatus] = useState<"loading" | "ready" | "failed">("loading");
  const [contextMissing, setContextMissing] = useState(false);
  useEffect(() => { setWebgl(hasWebgl()); }, []);

  // Parents may recreate the array while editing unrelated study fields. A
  // JSON snapshot of the typed, bounded transport data gives identical data a
  // stable identity without refetching or restarting WebGL. Coordinates remain
  // structurally unchanged; this performs no spatial operation.
  const outlineKey = JSON.stringify(outlines);
  const snapshot = useMemo(() => JSON.parse(outlineKey) as ParcelStudyOutline[], [outlineKey]);
  const parcels = useMemo(() => {
    const counts = new Map<string, number>();
    for (const entry of snapshot) counts.set(entry.bbl, (counts.get(entry.bbl) ?? 0) + 1);
    return snapshot.map((entry, index) => ({ ...entry,
      ...outlineState(entry, counts.get(entry.bbl)! > 1),
      number: index + 1,
      lot: zolaLotUrl(entry.bbl) ? Number(entry.bbl.slice(6)) : null,
      color: arrangement === "together" ? COLORS[0] : COLORS[index % COLORS.length],
    }));
  }, [snapshot, arrangement]);
  const features = useMemo<StudyFeature[]>(() => parcels.flatMap(entry => entry.geometry ? [{
    type: "Feature" as const,
    properties: { bbl: entry.bbl, color: entry.color },
    geometry: entry.geometry,
  }] : []), [parcels]);

  useEffect(() => {
    if (!webgl || features.length === 0 || !containerRef.current) return;
    const container = containerRef.current;
    // Camera margins are screen pixels, never parcel measurements.
    const fitOptions = () => {
      const shortestSide = Math.min(container.clientWidth, container.clientHeight);
      return { padding: shortestSide > 0 ? Math.min(72, shortestSide * 0.2) : 24, duration: 0, maxZoom: 19.5 };
    };
    let cancelled = false, failed = false, ready = false, drawn = false;
    let map: StudyMap | null = null;
    let containerWatch: ReturnType<typeof observeMapContainer> | null = null;
    const markers: StudyMarker[] = [];
    let stopRenderWatch = () => {};
    setMapStatus("loading");
    setContextMissing(false);
    const dispose = () => {
      stopRenderWatch();
      containerWatch?.dispose();
      markers.forEach(marker => marker.remove());
      markers.length = 0;
      map?.remove();
      map = null;
    };
    const fail = () => {
      if (cancelled || failed) return;
      failed = true;
      setMapStatus("failed");
      dispose();
    };
    let resizeMap = () => {};
    containerWatch = observeMapContainer(container, {
      onResize: () => resizeMap(), onTimeout: () => { if (!ready) fail(); },
    });
    void (async () => {
      const imported = await import("maplibre-gl") as unknown as { default?: StudyMapLibrary } & StudyMapLibrary;
      if (cancelled || failed) return;
      const gl = imported.default ?? imported;
      gl.setWorkerUrl(MAPLIBRE_WORKER_URL);
      const bounds = cameraBounds(features);
      const current = new gl.Map({ container, style: NYC_CONTEXT_STYLE,
        center: [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2],
        zoom: 16, attributionControl: false, interactive: true });
      map = current;
      resizeMap = () => {
        if (cancelled || failed) return;
        try { current.resize?.(); } catch { fail(); }
      };
      current.addControl(new gl.AttributionControl({ customAttribution: DCP_ATTRIBUTION }), "bottom-right");
      current.addControl(new gl.NavigationControl({ showCompass: false }), "top-right");
      current.on("error", event => {
        if (cancelled || failed) return;
        if (contextLayerName(event?.sourceId)) setContextMissing(true);
        else fail();
      });
      const draw = () => {
        if (cancelled || failed || drawn) return;
        drawn = true;
        try {
          current.addSource(SOURCE, { type: "geojson", data: { type: "FeatureCollection", features } });
          current.addLayer({ id: LAYERS[0], type: "fill", source: SOURCE,
            paint: { "fill-color": ["get", "color"], "fill-opacity": 0.24 } });
          current.addLayer({ id: LAYERS[1], type: "line", source: SOURCE,
            paint: { "line-color": ["get", "color"], "line-width": 3 } });
          current.fitBounds(bounds, fitOptions());
          for (const parcel of parcels) if (parcel.geometry) {
            const label = document.createElement("span");
            label.className = "parcel-study-map__marker";
            label.textContent = `${parcel.number} · Lot ${parcel.lot}`;
            label.setAttribute("aria-label", `Parcel ${parcel.number}, Lot ${parcel.lot}, BBL ${parcel.bbl}`);
            // Anchor to a returned exterior vertex, never a guessed centroid.
            const first = parcel.geometry.type === "Polygon"
              ? parcel.geometry.coordinates[0][0] : parcel.geometry.coordinates[0][0][0];
            markers.push(new gl.Marker({ element: label }).setLngLat([first[0], first[1]]).addTo(current));
          }
          const checkRender = () => {
            if (cancelled || failed || ready || !isMapContainerVisible(container)) return;
            try {
              if (!LAYERS.every(id => current.getLayer(id)) || !current.isSourceLoaded(SOURCE)) return;
              const rendered = current.queryRenderedFeatures({ layers: LAYERS });
              if (!features.every(feature => LAYERS.every(id => rendered.some(item =>
                item.source === SOURCE && item.layer?.id === id && item.properties?.bbl === feature.properties.bbl)))) return;
              ready = true;
              containerWatch?.markReady();
              stopRenderWatch();
              setMapStatus("ready");
            } catch { fail(); }
          };
          stopRenderWatch = () => current.off("render", checkRender);
          current.on("render", checkRender);
          resizeMap = () => {
            if (cancelled || failed) return;
            try {
              current.resize?.();
              if (!ready) current.fitBounds(bounds, fitOptions());
              checkRender();
            } catch { fail(); }
          };
          checkRender();
        } catch { fail(); }
      };
      current.on("load", draw);
      current.on("style.load", draw);
      if (current.isStyleLoaded()) draw();
    })().catch(fail);
    return () => { cancelled = true; dispose(); };
  }, [features, parcels, webgl]);

  const loading = outlines.some(entry => entry.loading);
  const mapMessage = features.length === 0
    ? loading ? "Loading parcel outlines…" : "No parcel outlines available to draw."
    : webgl === false ? "Interactive map unavailable in this browser. Parcel records and ZoLa links remain available below."
    : mapStatus === "failed" ? "Interactive map could not render. Parcel records and ZoLa links remain available below."
    : mapStatus === "ready" ? `${features.length} of ${parcels.length} approximate parcel outlines shown.`
    : "Loading interactive parcel map…";

  return <section className="parcel-study-map" aria-labelledby={titleId}>
    <h3 id={titleId}>Parcel study map</h3>
    <p className="section-note">{arrangement === "together" ? "Together: parcels share one study color."
      : arrangement === "compare" ? "Compare: numbered parcels distinguish the study options."
      : "Separately: each numbered parcel is a study option."} Study grouping only.</p>
    {features.length > 0 && webgl !== false ? <div ref={containerRef}
      className="parcel-study-map__canvas" data-testid="parcel-study-map-canvas"
      role="region" aria-label="Interactive approximate parcel outlines" aria-describedby={statusId}
      hidden={mapStatus === "failed"} /> : null}
    <p id={statusId} className="parcel-study-map__status" role="status">{mapMessage}</p>
    {contextMissing ? <p className="section-note">Some street context could not load; parcel outlines are separate source data.</p> : null}
    <MapRecordList compact={compact}><ol className="parcel-study-map__legend" aria-label="Parcel outline availability">
      {parcels.map((entry, index) => <li className="parcel-study-map__parcel" key={`${entry.bbl}-${index}`}>
        <span className="parcel-study-map__swatch" style={{ backgroundColor: entry.color }} aria-hidden="true">{entry.number}</span>
        <div><strong>Parcel {entry.number}{entry.lot !== null ? ` · Lot ${entry.lot}` : ""}</strong>
          <span> BBL {entry.bbl}</span><p className="section-note">{entry.message}</p>
          {zolaLotUrl(entry.bbl) ? <a href={zolaLotUrl(entry.bbl)!} target="_blank" rel="noopener noreferrer">
            View Lot {entry.lot} in ZoLa</a> : null}
        </div>
      </li>)}
    </ol></MapRecordList>
    <p className="section-note">Approximate MapPLUTO outlines · Display only, not a boundary survey or buildable envelope.</p>
    <details className="provenance-details">
      <summary>Map sources and limitations</summary>
      <p className="section-note">Grouping does not merge tax lots, establish a zoning lot, or change zoning. No area, width, depth, height, or development allowance is calculated from this map.</p>
      {outlines.map((entry, index) => entry.outcome?.kind === "document" ? <div key={`${entry.bbl}-${index}`}>
        <strong>Requested BBL {entry.bbl}</strong>
        <p className="section-note">Returned BBL: {entry.outcome.view.bbl ?? "Unknown"}. {entry.outcome.view.attribution}</p>
        <p className="section-note">{entry.outcome.view.accuracyNote} {entry.outcome.view.disclaimer}</p>
        <p className="section-note">Source: {entry.outcome.view.source.sourceId ?? "Unknown"} · Version: {entry.outcome.view.source.datasetVersion ?? "Unknown"} · Retrieved: {entry.outcome.view.source.retrievedAt ?? "Unknown"}</p>
        {entry.outcome.view.condoClassification.note ? <p className="section-note">{entry.outcome.view.condoClassification.note}</p> : null}
        {entry.outcome.view.notes.map((note, n) => <p className="section-note" key={n}>{note}</p>)}
      </div> : null)}
      <p className="section-note">Street basemap and labels: <a href="https://maps.nyc.gov/tiles/" target="_blank" rel="noopener noreferrer">City of New York, CC BY 4.0</a>. Tile capture dates are not supplied here; street context is not current survey evidence.</p>
    </details>
  </section>;
}
