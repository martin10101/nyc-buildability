"use client";

import { useEffect, useRef, useState } from "react";
import {
  fetchLotGeometry,
  type LotOutlineOutcome,
  type LotOutlineView,
  type ValidatedGeometry,
} from "@/lib/lot-geometry-api";

/**
 * LotOutlineMap (task M5-T023, D-040-R001) — the focused module that owns ALL
 * lot-outline map behavior on the address confirm card. It replaces the
 * "no outline drawn yet" placeholder with honest, typed outcomes:
 *
 *   - single_lot          -> a MapLibre GL JS map drawing the display-only
 *                            EPSG:4326 outline (Polygon or MultiPolygon, with
 *                            every interior ring preserved exactly); the
 *                            +/-20 ft approximate-outline copy and NYC DCP
 *                            attribution are shown.
 *   - no_outline          -> a typed honest-empty state naming the reason
 *                            (condo unit lot carries no polygon / no lot for
 *                            this BBL) — no map is fabricated.
 *   - multiple_features   -> a review-required posture — geometry is withheld,
 *                            never a silent first-pick.
 *   - invalid_geometry    -> a typed honest note — no shape is drawn.
 *   - transport failures  -> a typed fallback that states the outline is
 *     (404/network/timeout/  unavailable; NEVER a crash, NEVER a blank div,
 *      malformed/unexpected) NEVER a retry storm (one bounded fetch per BBL).
 *   - WebGL unavailable    -> the same honest fallback (Playwright CI Chromium
 *                            may lack WebGL); maplibre-gl is only imported when
 *                            WebGL is present.
 *
 * DISPLAY-ONLY: this component DRAWS what the contract delivered and computes
 * NO area/dimension/measurement from the coordinates. The only coordinate math
 * is a bounding box used purely to frame the camera (fitBounds) — no value is
 * derived or shown. The ZoLa link and its BBL-absent branch live on the parent
 * card and are always kept as the escape hatch.
 *
 * maplibre-gl is browser-only and is DYNAMICALLY imported inside a client-only
 * effect (never at module top), so `next build` (SSR) never touches it and the
 * bundle cost stays scoped to this confirm surface.
 */

// Minimal structural typing of the maplibre-gl surface this module uses, so the
// dynamic import stays self-contained and does not couple the type-check to the
// full maplibre type surface.
interface MapLike {
  on(type: string, listener: () => void): void;
  once(type: string, listener: () => void): void;
  isStyleLoaded(): boolean;
  addSource(id: string, source: unknown): void;
  addLayer(layer: unknown): void;
  addControl(control: unknown, position?: string): void;
  fitBounds(bounds: [[number, number], [number, number]], options?: unknown): void;
  remove(): void;
}
interface MapConstructor {
  new (options: unknown): MapLike;
}
interface AttributionControlConstructor {
  new (options: unknown): unknown;
}
interface NavigationControlConstructor {
  new (options: unknown): unknown;
}
interface MapLibreModule {
  Map: MapConstructor;
  AttributionControl: AttributionControlConstructor;
  NavigationControl: NavigationControlConstructor;
}

/**
 * Run `draw` exactly once, as soon as the map's style is ready — regardless
 * of whether readiness is reached BEFORE or AFTER this function is called
 * (task M5-T025, D-056-R002 root-cause fix).
 *
 * ROOT CAUSE [ORCH-CORRECTED per M5-T025-G3 F1]: the prior code gated the
 * ENTIRE draw step (addSource/addLayer/fitBounds) behind exactly one
 * one-time `map.on("load", draw)` listener. MapLibre's "load" fires once,
 * only after the initial style loads AND the map completes its first
 * visually-complete render — an event that can simply NEVER FIRE on a
 * device whose GL rendering is degraded (the reporting device also failed
 * to boot ZoLa, another GL map app; the D-056-R004 record names hardware
 * acceleration). With no "style.load" arm, no readiness check, and no
 * "error" handler, there was then nothing left to invoke the callback: the
 * EMPTY_STYLE background layer paints as soon as the style is applied
 * (independent of "load") and AttributionControl is construction-time DOM,
 * so the result is EXACTLY the reported symptom — gray canvas +
 * attribution, no outline, permanently, with nothing to find by zooming.
 * NOTE: the "listener attached after 'load' already fired" race is NOT
 * reachable at this call site (the listener was attached synchronously in
 * the same task as construction, and an event requiring a completed render
 * cannot fire inside the constructor); the `isStyleLoaded()` fast path
 * below is therefore defense-in-depth for other call orders, not the
 * operative fix here. The operative fix is the "style.load" arm — it fires
 * when the style loads, independent of the render pipeline — plus the
 * "error" surface added at the call site. The precise device-side trigger
 * is confirmed by the owner's redeploy retest (D-056-R006).
 *
 * This function closes the race unconditionally: if the style is ALREADY
 * loaded by the time it is called, `draw` runs immediately and
 * synchronously, with no event wait at all. Otherwise it arms BOTH "load"
 * and "style.load" with an idempotency guard, so `draw` still runs exactly
 * once even if both end up firing.
 */
export interface StyleReadyMap {
  isStyleLoaded(): boolean;
  once(type: string, listener: () => void): void;
}
export function runOnStyleReady(map: StyleReadyMap, draw: () => void): void {
  let done = false;
  const runOnce = () => {
    if (done) return;
    done = true;
    draw();
  };
  if (map.isStyleLoaded()) {
    runOnce();
    return;
  }
  map.once("load", runOnce);
  map.once("style.load", runOnce);
}

/**
 * Camera-framing options for `fitBounds` (D-056-R002 framing fix). The prior
 * `maxZoom: 18` rendered a canonical NYC rowhouse lot (~25 x 100 ft) at
 * roughly 17 x 67 px inside the 320px panel: at NYC's latitude (~40.71 N,
 * cos ~0.758) the Web Mercator ground resolution at zoom 18 is
 * ~156543.034 * 0.758 / 2^18 ~= 0.45 m/px, and 25ft x 100ft = 7.62m x
 * 30.48m, so 7.62/0.45 ~= 17px by 30.48/0.45 ~= 67px — effectively invisible
 * even when the outline IS drawn (see the producer report). 19.5 roughly
 * HALVES the ground resolution to ~0.16 m/px, rendering the same lot at
 * roughly 48 x 190 px, clearly visible inside the panel. No raster basemap
 * tiles are wired (M5-T023 — the outline draws on a flat background layer),
 * so there is no tile-pixelation ceiling that would argue for keeping the
 * cap lower.
 */
export const LOT_OUTLINE_MAX_ZOOM = 19.5;
export function lotOutlineFitBoundsOptions(): {
  padding: number;
  duration: number;
  maxZoom: number;
} {
  return { padding: 24, duration: 0, maxZoom: LOT_OUTLINE_MAX_ZOOM };
}

/** Detect a usable WebGL context WITHOUT importing maplibre-gl. Any failure
 * (no document, no context, a throwing getContext) is treated as unavailable so
 * the honest fallback renders instead of a crash. */
export function isWebglAvailable(): boolean {
  if (typeof document === "undefined") return false;
  try {
    const canvas = document.createElement("canvas");
    const gl =
      canvas.getContext("webgl2") ||
      canvas.getContext("webgl") ||
      canvas.getContext("experimental-webgl");
    return gl !== null && gl !== undefined;
  } catch {
    return false;
  }
}

/** Bounding box across every position of the geometry — camera framing ONLY
 * (fitBounds). This is NOT a measurement: no distance, area, or dimension is
 * derived or surfaced; the map only needs a viewport. Returns null for empty
 * input. */
function geometryBounds(
  geometry: ValidatedGeometry,
): [[number, number], [number, number]] | null {
  let minLng = Infinity;
  let minLat = Infinity;
  let maxLng = -Infinity;
  let maxLat = -Infinity;
  const rings: number[][][] =
    geometry.type === "Polygon"
      ? geometry.coordinates
      : geometry.coordinates.flat();
  for (const ring of rings) {
    for (const [lng, lat] of ring) {
      if (lng < minLng) minLng = lng;
      if (lat < minLat) minLat = lat;
      if (lng > maxLng) maxLng = lng;
      if (lat > maxLat) maxLat = lat;
    }
  }
  if (!Number.isFinite(minLng) || !Number.isFinite(minLat)) return null;
  return [
    [minLng, minLat],
    [maxLng, maxLat],
  ];
}

/** Client-side CONSTANT attribution for the MapLibre AttributionControl. G5 F-1:
 * MapLibre renders customAttribution as HTML (innerHTML), so it must NEVER carry
 * a reflected server string (boundedText does not neutralize HTML
 * metacharacters). The reflected `view.attribution` is shown ONLY as
 * React-escaped text in AttributionAndAccuracy, which is safe. */
const DCP_ATTRIBUTION = "NYC Department of City Planning (DCP), MapPLUTO";

const EMPTY_STYLE = {
  version: 8 as const,
  sources: {},
  layers: [
    {
      id: "lot-outline-background",
      type: "background",
      paint: { "background-color": "#eef1f4" },
    },
  ],
};

/** A one-line screen-reader summary of the current state, derived
 * deterministically from the typed outcome (no legal semantics, no invented
 * values). */
function outcomeSummary(
  outcome: LotOutlineOutcome | null,
  drawable: boolean,
  mapRenderFailed: boolean,
): string {
  if (outcome === null) return "Loading the approximate lot outline…";
  switch (outcome.kind) {
    case "document":
      switch (outcome.view.outcome) {
        case "single_lot":
          if (outcome.view.geometryUnusable)
            return "The lot outline could not be drawn: the official geometry was not usable. Use the ZoLa map link above for the authoritative outline.";
          if (drawable && mapRenderFailed)
            // Geometry and WebGL are both present but the map itself
            // reported an error after construction (D-056-R002 hardening) —
            // distinct from the no-WebGL fallback below.
            return "An approximate outline is available for this lot, but the interactive map could not be rendered. Use the ZoLa map link above for the authoritative outline.";
          if (!drawable)
            // Geometry exists but no interactive map could be opened (e.g. no
            // WebGL). The summary must match the visible fallback, not claim a
            // map is shown.
            return "An approximate outline is available for this lot, but this browser could not open an interactive map. Use the ZoLa map link above for the authoritative outline.";
          return "An approximate lot outline is shown, drawn from the official NYC City Planning MapPLUTO parcel geometry (plus or minus 20 feet).";
        case "no_outline":
          return outcome.view.noOutlineReason === "condo_unit_lot_no_polygon"
            ? "No outline is drawn: this is a condominium unit lot, which has no parcel polygon of its own. Use the ZoLa map link."
            : "No outline is drawn: the official source returned no parcel for this lot. Use the ZoLa map link.";
        case "multiple_features":
          return "No outline is drawn: the official source returned more than one parcel for this lot, so it needs review before an outline can be trusted. Use the ZoLa map link.";
        case "invalid_geometry":
          return "No outline is drawn: the official parcel geometry for this lot was not a usable shape. Use the ZoLa map link.";
      }
      return "The lot outline is unavailable. Use the ZoLa map link.";
    case "route_absent":
      return "The lot outline is not available in this environment. Use the ZoLa map link for the authoritative outline.";
    case "network_error":
    case "client_timeout":
    case "error":
    case "unexpected_response":
      return "The lot outline could not be loaded. The address details above are unaffected. Use the ZoLa map link for the authoritative outline.";
    case "aborted":
      return "";
  }
}

function AttributionAndAccuracy({ view }: { view: LotOutlineView }) {
  return (
    <>
      <p className="section-note" data-testid="lot-outline-accuracy">
        {view.accuracyNote}
      </p>
      <p className="failure-meta" data-testid="lot-outline-attribution">
        {view.attribution}
      </p>
    </>
  );
}

export function LotOutlineMap({
  bbl,
  fetchImpl,
}: {
  bbl: string;
  fetchImpl?: typeof fetch;
}) {
  const [outcome, setOutcome] = useState<LotOutlineOutcome | null>(null);
  const [webglAvailable, setWebglAvailable] = useState(false);
  // D-056-R002 hardening: a "error" event from a constructed map (WebGL
  // context loss, a style/source/layer failure) now routes to a typed
  // fallback instead of leaving a silently blank/gray map — distinct from
  // the (unchanged) no-WebGL fallback below, which never constructs a map.
  const [mapRenderFailed, setMapRenderFailed] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLike | null>(null);

  // Detect WebGL once on mount (client-only, so SSR and the first client render
  // agree on the loading skeleton and no hydration mismatch occurs).
  useEffect(() => {
    setWebglAvailable(isWebglAvailable());
  }, []);

  // ONE bounded fetch per BBL view. A superseded/unmounted request is aborted;
  // there is no retry loop.
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setOutcome(null);
    void fetchLotGeometry(bbl, { fetchImpl, signal: controller.signal }).then(
      (result) => {
        if (active && result.kind !== "aborted") setOutcome(result);
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, [bbl, fetchImpl]);

  // Initialize the MapLibre map only for a single_lot outline with usable
  // geometry AND a WebGL context. Dynamic import keeps maplibre-gl out of SSR
  // and out of the no-WebGL path entirely.
  const view = outcome?.kind === "document" ? outcome.view : null;
  const drawable =
    view !== null &&
    view.outcome === "single_lot" &&
    view.geometry !== null &&
    webglAvailable;
  const geometry = drawable ? (view.geometry as ValidatedGeometry) : null;

  useEffect(() => {
    if (!geometry) return;
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;
    setMapRenderFailed(false);

    void (async () => {
      const mod = (await import("maplibre-gl")) as unknown as {
        default?: MapLibreModule;
      } & Partial<MapLibreModule>;
      if (cancelled) return;
      const gl: MapLibreModule = mod.default ?? (mod as MapLibreModule);
      const bounds = geometryBounds(geometry);
      const map = new gl.Map({
        container,
        style: EMPTY_STYLE,
        // No basemap tile source is wired (none is admitted in the source
        // registry); the outline draws on a neutral background. attributionControl
        // is added explicitly below so the NYC DCP attribution is on the map.
        attributionControl: false,
        interactive: true,
        center: bounds ? [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2] : [-73.98, 40.75],
        zoom: 15,
      });
      mapRef.current = map;
      // G5 F-1: pass the CONSTANT (MapLibre renders this as HTML). The
      // reflected view.attribution is shown only as React-escaped text.
      map.addControl(
        new gl.AttributionControl({ customAttribution: DCP_ATTRIBUTION }),
        "bottom-right",
      );
      // D-056-R003: visible, keyboard-accessible zoom in/out buttons.
      // showCompass is off — this is a flat, display-only top-down outline
      // with no rotation-relevant affordance elsewhere, so a bearing
      // indicator would add clutter without conveying anything useful.
      map.addControl(new gl.NavigationControl({ showCompass: false }), "top-right");
      // D-056-R002 hardening: a map "error" (e.g. WebGL context loss, a
      // style/source/layer failure) was previously UNHANDLED — silently
      // logged by MapLibre and otherwise invisible. Route it to a typed
      // fallback instead of leaving a permanently blank/gray map.
      map.on("error", () => {
        if (cancelled) return;
        setMapRenderFailed(true);
      });
      // D-056-R002 root-cause fix: run the draw step exactly once, as soon
      // as the style is ready, regardless of whether readiness was reached
      // before or after this listener attaches (see runOnStyleReady's own
      // documentation above for the root-cause analysis).
      runOnStyleReady(map, () => {
        if (cancelled) return;
        map.addSource("lot-outline", {
          type: "geojson",
          data: {
            type: "Feature",
            properties: {},
            // Coordinates VERBATIM from the contract — every ring preserved.
            geometry,
          },
        });
        map.addLayer({
          id: "lot-outline-fill",
          type: "fill",
          source: "lot-outline",
          paint: { "fill-color": "#2f6fb0", "fill-opacity": 0.18 },
        });
        map.addLayer({
          id: "lot-outline-line",
          type: "line",
          source: "lot-outline",
          paint: { "line-color": "#1d4e79", "line-width": 2 },
        });
        if (bounds) {
          map.fitBounds(bounds, lotOutlineFitBoundsOptions());
        }
      });
    })();

    return () => {
      cancelled = true;
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [geometry]);

  return (
    <section
      className="lot-outline"
      role="region"
      aria-label="Approximate tax lot outline"
      data-testid="lot-outline"
    >
      <p className="visually-hidden" data-testid="lot-outline-summary" role="status">
        {outcomeSummary(outcome, drawable, mapRenderFailed)}
      </p>

      {outcome === null ? (
        <p className="section-note" data-testid="lot-outline-loading" aria-hidden="true">
          Loading the approximate lot outline…
        </p>
      ) : null}

      {view !== null ? (
        <>
          {view.outcome === "single_lot" && !view.geometryUnusable ? (
            drawable && !mapRenderFailed ? (
              <>
                <div
                  ref={containerRef}
                  className="lot-outline-map"
                  data-testid="lot-outline-map"
                  aria-label="Interactive approximate lot outline map"
                />
                <AttributionAndAccuracy view={view} />
              </>
            ) : drawable && mapRenderFailed ? (
              // D-056-R002 hardening: geometry and WebGL are both present,
              // but the map itself reported an "error" after construction —
              // an honest fallback instead of a permanently blank/gray map.
              <>
                <p
                  className="section-note"
                  data-testid="lot-outline-render-error"
                >
                  An approximate outline is available for this lot, but the
                  interactive map could not be rendered. Open the city&apos;s
                  ZoLa map above for the authoritative outline.
                </p>
                <AttributionAndAccuracy view={view} />
              </>
            ) : (
              // Geometry is present but WebGL is unavailable: an honest fallback
              // that never leaves a blank container. The +/-20 ft copy and
              // attribution still show; the ZoLa link (parent card) is the map.
              <>
                <p
                  className="section-note"
                  data-testid="lot-outline-webgl-unavailable"
                >
                  An approximate outline is available for this lot, but this
                  browser could not open an interactive map (no WebGL). Open the
                  city&apos;s ZoLa map above for the authoritative outline.
                </p>
                <AttributionAndAccuracy view={view} />
              </>
            )
          ) : null}

          {view.outcome === "single_lot" && view.geometryUnusable ? (
            <>
              <p className="section-note" data-testid="lot-outline-unavailable">
                The official geometry for this lot was not a usable shape, so no
                outline is drawn here. Open the city&apos;s ZoLa map above for
                the authoritative outline.
              </p>
              <AttributionAndAccuracy view={view} />
            </>
          ) : null}

          {view.outcome === "no_outline" ? (
            <>
              <p className="section-note" data-testid="lot-outline-empty">
                {view.noOutlineReason === "condo_unit_lot_no_polygon"
                  ? "No parcel outline is drawn: this is a condominium unit lot, which carries no polygon of its own in the official MapPLUTO data — the billing lot holds the merged complex outline. Open the city's ZoLa map above."
                  : "No parcel outline is drawn: the official source returned no lot for this BBL. Open the city's ZoLa map above."}
              </p>
              <AttributionAndAccuracy view={view} />
            </>
          ) : null}

          {view.outcome === "multiple_features" ? (
            <>
              <p className="section-note" data-testid="lot-outline-review">
                No outline is drawn: the official source returned more than one
                parcel for this lot. This needs review before an outline can be
                trusted — the platform never silently picks one. Open the
                city&apos;s ZoLa map above.
              </p>
              <AttributionAndAccuracy view={view} />
            </>
          ) : null}

          {view.outcome === "invalid_geometry" ? (
            <>
              <p className="section-note" data-testid="lot-outline-invalid">
                No outline is drawn: the official parcel geometry for this lot
                was not a usable shape. Open the city&apos;s ZoLa map above.
              </p>
              <AttributionAndAccuracy view={view} />
            </>
          ) : null}
        </>
      ) : null}

      {outcome !== null && outcome.kind !== "document" ? (
        <p className="section-note" data-testid="lot-outline-unavailable">
          {outcome.kind === "route_absent"
            ? "The lot outline is not available in this environment. Open the city's ZoLa map above for the authoritative outline."
            : "The lot outline could not be loaded (the address details above are unaffected). Open the city's ZoLa map above for the authoritative outline."}
        </p>
      ) : null}
    </section>
  );
}
