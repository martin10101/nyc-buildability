"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { LotOutlineMap, type DrawnOverlayData } from "@/components/address/LotOutlineMap";

/**
 * Map-CLICK interaction wrapper (task M5-T066, D-082-R001). Composes the
 * accepted read-only lot map (LotOutlineMap) with its additive interaction
 * props so the architect can PLACE, SELECT, and ADJUST drawn outline points by
 * clicking the map — feeding the SAME single drawn-outline state the numeric
 * table already owns (ProposalOutlineDraw). One draft model, one bridge, one
 * adoption path; click is an ADDITION to the keyboard table, never a
 * replacement.
 *
 * HONESTY (D-076-R002): the drawn shape is PROPOSED input, never a city record,
 * and nothing is measured from the map. Clicked positions are display EPSG:4326
 * until the accepted server bridge converts them (no client-side CRS math here —
 * the no-reprojection doctrine).
 *
 * This wrapper holds NO map instance and no coordinate math beyond assembling
 * the display overlay; the map lifecycle, WebGL fallback, and click plumbing all
 * live in LotOutlineMap. Keyboard operability is complete in the composing
 * table (add/select/adjust/delete), so this surface adds pointer convenience
 * without removing any keyboard path (the accepted a11y bar).
 *
 * COPY HONESTY (DB-047(d)): the instruction lead must describe only interactions
 * that EXIST. The leaf LotOutlineMap renders an interactive, clickable map
 * surface ONLY on the drawable path (a single_lot outline with usable geometry
 * AND WebGL, not render-failed); in every typed-fallback state (condo unit lot,
 * multiple_features, invalid_geometry, no-WebGL, post-construction render error)
 * it renders a keyboard-only fallback with NO clickable map. LotOutlineMap is an
 * accepted, forbidden-to-edit surface that exposes no readiness callback, so we
 * OBSERVE whether its interactive map surface is present in our subtree (by its
 * semantic aria-label) and only then invite a map gesture. This adds NO fetch —
 * every finite-value flow is byte-identical to the accepted behavior.
 *
 * POINT COUNT HONESTY (DB-047(e)): the screen-reader status reports the FINITE
 * point count — exactly what the overlay renders — never a raw row count that
 * would announce not-yet-typed keyboard rows the map does not draw.
 */

/** Mirrors the aria-label LotOutlineMap puts on its interactive map container
 * (the accepted, forbidden-to-edit display surface). Its presence in our subtree
 * is the single honest signal that a clickable map actually rendered. */
const INTERACTIVE_MAP_LABEL = "Interactive approximate lot outline map";

export interface DrawnPoint {
  lng: number;
  lat: number;
}

/** The ONE finiteness predicate for a drawn point: BOTH ordinates a finite
 * number (M5-T071 G3 F6). A fresh keyboard row (NaN/NaN, not yet typed) is not
 * finite, so the overlay does not draw it, the status does not count it, and
 * Convert does not send it. Exported so every site shares this single definition
 * — the overlay builder and finitePointCount below, and ProposalOutlineDraw's
 * finite gate + convert filter — with no duplicated `Number.isFinite` pair-check
 * anywhere else (AS-5 grep-provable). */
export function isDrawnPointFinite(p: DrawnPoint): boolean {
  return Number.isFinite(p.lng) && Number.isFinite(p.lat);
}

/** Count the points the overlay actually draws: both ordinates finite. A fresh
 * keyboard row (NaN/NaN, not yet typed) is not drawn and must not be announced. */
export function finitePointCount(points: DrawnPoint[]): number {
  return points.filter(isDrawnPointFinite).length;
}

/** Name the ordinate(s) a drawn point still lacks: "longitude", "latitude",
 * "longitude and latitude", or "" when both are present (M5-T071 G3 F7, HJ-7).
 * This answers WHICH ordinate is absent — a different question from the pair
 * predicate `isDrawnPointFinite`, which alone decides whether a row is complete
 * (drawn, counted, sent). Shared by the row markers, the convert hint and the
 * selection copy so a half-typed row is described exactly everywhere. */
export function missingOrdinateLabel(p: DrawnPoint): string {
  return [Number.isFinite(p.lng) ? "" : "longitude", Number.isFinite(p.lat) ? "" : "latitude"]
    .filter((part) => part !== "")
    .join(" and ");
}

type MapSurface = "unknown" | "present" | "absent";

/** (c) Map-readiness announcement lifecycle for the ONE status region: armed
 * ("pending") on each transition of the observed surface, "showing" from the
 * first status at which a click would PLACE a new point, "done" at the next
 * status change — so readiness is spoken once, never re-appended to every update. */
interface ReadyAnnouncement {
  surface: MapSurface;
  phase: "pending" | "showing" | "done";
  base: string;
}

const READY_SENTENCE = " The lot map is ready to draw on — click it to place points.";

/**
 * Build the map overlay for the drawn points (pure — unit-tested without WebGL).
 * Each rendered Point feature keeps its ORIGINAL point index (so a click hit
 * maps back to the caller's state) and a `selected` flag (drives the highlight
 * paint). A point whose coordinates are not yet finite (a freshly added,
 * not-yet-typed keyboard row) is intentionally not drawn, and the connecting
 * LineString spans only the finite points in order.
 */
export function drawnOverlayData(points: DrawnPoint[], selectedIndex: number | null): DrawnOverlayData {
  const finite = points
    .map((p, index) => ({ p, index }))
    .filter(({ p }) => isDrawnPointFinite(p));
  const features: DrawnOverlayData["features"] = finite.map(({ p, index }) => ({
    type: "Feature",
    properties: { index, selected: index === selectedIndex },
    geometry: { type: "Point", coordinates: [p.lng, p.lat] as [number, number] },
  }));
  if (finite.length >= 2) {
    features.unshift({
      type: "Feature",
      properties: {},
      geometry: {
        type: "LineString",
        coordinates: finite.map(({ p }) => [p.lng, p.lat] as [number, number]),
      },
    });
  }
  return { type: "FeatureCollection", features };
}

export function ProposalOutlineMap({
  bbl,
  points,
  selectedIndex,
  onPlace,
  onSelect,
  onMoveSelected,
  fetchImpl,
}: {
  bbl: string;
  points: DrawnPoint[];
  selectedIndex: number | null;
  onPlace: (lngLat: { lng: number; lat: number }) => void;
  onSelect: (index: number) => void;
  onMoveSelected: (lngLat: { lng: number; lat: number }) => void;
  fetchImpl?: typeof fetch;
}) {
  const overlay = useMemo(() => drawnOverlayData(points, selectedIndex), [points, selectedIndex]);
  const hasSelection = selectedIndex !== null;
  // (d) Is the SELECTED row actually drawn on the map? An untyped selected row
  // (NaN/NaN) is not on the map, so a click PLACES it, not MOVES it — the copy
  // and status must say so. Uses the ONE shared finiteness predicate (F6).
  const selectedPoint = selectedIndex !== null ? points[selectedIndex] : undefined;
  const selectedIsFinite = selectedPoint !== undefined && isDrawnPointFinite(selectedPoint);
  // The count the overlay renders (finite points only) — what the status must
  // announce, never the raw row count (DB-047(e)).
  const drawnCount = useMemo(() => finitePointCount(points), [points]);

  // DB-047(d): the copy follows what actually exists in the leaf's subtree. We
  // cannot edit the accepted LotOutlineMap or read a readiness callback from it,
  // so we observe its rendered output. [ORCH-CORRECTED per HJ B2] Tri-state, not
  // boolean: while the leaf is still LOADING we must claim nothing about the lot
  // (the old boolean asserted "no interactive drawing surface" — a false definite
  // negative — for the whole load window on every drawable lot). "present" keys
  // on the interactive container's semantic aria-label; "unknown" on the leaf's
  // loading node (lot-outline-loading); anything else is a typed fallback state,
  // where the definite keyboard-only copy is the honest one.
  const rootRef = useRef<HTMLDivElement | null>(null);
  const [mapSurface, setMapSurface] = useState<MapSurface>("unknown");
  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const sync = () => {
      const present = root.querySelector(`[aria-label="${INTERACTIVE_MAP_LABEL}"]`) !== null;
      const loading = root.querySelector('[data-testid="lot-outline-loading"]') !== null;
      const next = present ? "present" : loading ? "unknown" : "absent";
      setMapSurface((prev) => (prev === next ? prev : next));
    };
    sync();
    // The leaf transitions asynchronously (loading -> drawable, or -> a typed
    // fallback / render error) without re-rendering this wrapper, so observe the
    // subtree and re-evaluate whenever its rendered content changes.
    const observer = new MutationObserver(sync);
    observer.observe(root, { childList: true, subtree: true });
    return () => observer.disconnect();
    // [bbl] is a RESET KEY, not a value read in this effect body (M5-T071 G3
    // F8). A new lot mounts a fresh leaf subtree, so the observer and its
    // initial sync must be torn down and rebuilt when bbl changes. Do NOT let an
    // exhaustive-deps autofix "simplify" this to [] — that silently freezes the
    // observer against the first lot and breaks the loading->drawable re-sync
    // (both the MutationObserver-transition and the loading-copy specs rest on
    // this key). Keep [bbl].
  }, [bbl]);

  // A map click MOVES the selected point when one is selected, else PLACES a new
  // point. A click that lands on a drawn vertex SELECTS it (LotOutlineMap
  // routes that to onDrawnVertexClick). Every one of these has a keyboard
  // equivalent in the table (Add / Select / the lng-lat inputs / Delete).
  const handleMapClick = (lngLat: { lng: number; lat: number }) => {
    if (hasSelection) onMoveSelected(lngLat);
    else onPlace(lngLat);
  };

  // (d)/HJ-7 What a selected, not-yet-drawn row lacks — exact for a half-typed
  // row ("no latitude yet"), "coordinates" only when both ordinates are missing.
  const selectedMissing = (selectedPoint ? missingOrdinateLabel(selectedPoint) : "") || "longitude and latitude";
  const selectedMissingNoun = selectedMissing === "longitude and latitude" ? "coordinates" : selectedMissing;

  // Every clause below is gated on the SAME mapSurface x selection x
  // selectedIsFinite state (G3-F2 / DB-047(d)): a map gesture is described only
  // when a clickable map is present, and only the gesture a click would perform.
  const instructions =
    mapSurface === "present"
      ? hasSelection
        ? selectedIsFinite
          ? `Point ${selectedIndex} is selected — click the map to move it, or edit it in the table below. Click the point again to deselect.`
          : // (d) An untyped selected row is not on the map, so a click PLACES it
            // (never moves a point that isn't drawn), and there is no drawn point
            // to click again — deselecting happens in the table only.
            `Point ${selectedIndex} is selected but has no ${selectedMissingNoun} yet — click the map to place it, or type its ${selectedMissing} in the table below. Use its Deselect button in the table to clear the selection.`
        : "Click the lot map to place a proposed outline point, or add points by keyboard in the table below. Click a placed point to select it."
      : mapSurface === "unknown"
        ? "Preparing the reference map — you can start adding points by keyboard in the table below; enter each point's longitude and latitude."
        : "Add proposed outline points by keyboard in the table below — enter each point's longitude and latitude. The reference map on this lot has no interactive drawing surface.";

  const countSentence =
    drawnCount === 0 ? "No points drawn yet." : `${drawnCount} point${drawnCount === 1 ? "" : "s"} drawn.`;
  const selectionSentence = !hasSelection
    ? ""
    : selectedIsFinite
      ? ` Point ${selectedIndex} selected.`
      : mapSurface === "present"
        ? ` Point ${selectedIndex} selected — it has no ${selectedMissingNoun} yet, so a map click will place it.`
        : ` Point ${selectedIndex} selected — it has no ${selectedMissingNoun} yet; type its ${selectedMissing} in the table.`;
  const statusBase = `${countSentence}${selectionSentence}`;

  // (c) Readiness is announced ONCE per transition to "present" (G3-A7 /
  // HJ-3(c)), and only where a click would PLACE a new point — never while a
  // selected point would be MOVED (G3-F2(ii)). State is adjusted during render
  // (React's "store information from previous renders" pattern); each branch
  // lands in a state the others do not re-enter, so this converges at once.
  const readyApplicable = mapSurface === "present" && !hasSelection;
  const [ready, setReady] = useState<ReadyAnnouncement>({ surface: "unknown", phase: "pending", base: "" });
  if (ready.surface !== mapSurface) {
    setReady({ surface: mapSurface, phase: "pending", base: "" });
  } else if (ready.phase === "pending" && readyApplicable) {
    setReady({ surface: mapSurface, phase: "showing", base: statusBase });
  } else if (ready.phase === "showing" && ready.base !== statusBase) {
    setReady({ surface: mapSurface, phase: "done", base: "" });
  }
  const showReady =
    readyApplicable && ready.surface === mapSurface && ready.phase === "showing" && ready.base === statusBase;

  return (
    <div className="proposal-outline-map" data-testid="proposal-outline-map" ref={rootRef}>
      <p className="section-note" data-testid="proposal-outline-map-instructions">
        {instructions}
      </p>
      <LotOutlineMap
        bbl={bbl}
        context
        fetchImpl={fetchImpl}
        onOutlineMapClick={handleMapClick}
        onDrawnVertexClick={onSelect}
        drawnOverlay={overlay}
      />
      {/* (c) The map-ready change is announced through THIS one existing status
          region — never a new live region (adding aria-live/role=status/role=alert
          is forbidden). When the leaf's interactive surface appears (mapSurface
          flips to "present") this text changes once and the single region speaks.
          (d) The selection is named even at zero finite points (an untyped
          selected row used to drop the selection clause entirely). */}
      <p className="visually-hidden" role="status" data-testid="proposal-outline-map-status">
        {`${statusBase}${showReady ? READY_SENTENCE : ""}`}
      </p>
    </div>
  );
}
