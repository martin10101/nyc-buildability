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

/** Count the points the overlay actually draws: both ordinates finite. A fresh
 * keyboard row (NaN/NaN, not yet typed) is not drawn and must not be announced. */
export function finitePointCount(points: DrawnPoint[]): number {
  return points.filter((p) => Number.isFinite(p.lng) && Number.isFinite(p.lat)).length;
}

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
    .filter(({ p }) => Number.isFinite(p.lng) && Number.isFinite(p.lat));
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
  // The count the overlay renders (finite points only) — what the status must
  // announce, never the raw row count (DB-047(e)).
  const drawnCount = useMemo(() => finitePointCount(points), [points]);

  // DB-047(d): true only while the leaf's interactive map surface is actually
  // present in our subtree. We cannot edit the accepted LotOutlineMap or read a
  // readiness callback from it, so we observe its rendered output (the semantic
  // aria-label of its map container) and let the copy follow what really exists.
  const rootRef = useRef<HTMLDivElement | null>(null);
  const [mapRendered, setMapRendered] = useState(false);
  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const sync = () => {
      const present = root.querySelector(`[aria-label="${INTERACTIVE_MAP_LABEL}"]`) !== null;
      setMapRendered((prev) => (prev === present ? prev : present));
    };
    sync();
    // The leaf transitions asynchronously (loading -> drawable, or -> a typed
    // fallback / render error) without re-rendering this wrapper, so observe the
    // subtree and re-evaluate whenever its rendered content changes.
    const observer = new MutationObserver(sync);
    observer.observe(root, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [bbl]);

  // A map click MOVES the selected point when one is selected, else PLACES a new
  // point. A click that lands on a drawn vertex SELECTS it (LotOutlineMap
  // routes that to onDrawnVertexClick). Every one of these has a keyboard
  // equivalent in the table (Add / Select / the lng-lat inputs / Delete).
  const handleMapClick = (lngLat: { lng: number; lat: number }) => {
    if (hasSelection) onMoveSelected(lngLat);
    else onPlace(lngLat);
  };

  return (
    <div className="proposal-outline-map" data-testid="proposal-outline-map" ref={rootRef}>
      <p className="section-note" data-testid="proposal-outline-map-instructions">
        {mapRendered
          ? hasSelection
            ? `Point ${selectedIndex} is selected — click the map to move it, or edit it in the table below. Click the point again to deselect.`
            : "Click the lot map to place a proposed outline point, or add points by keyboard in the table below. Click a placed point to select it."
          : "Add proposed outline points by keyboard in the table below — enter each point's longitude and latitude. The reference map on this lot has no interactive drawing surface."}
      </p>
      <LotOutlineMap
        bbl={bbl}
        context
        fetchImpl={fetchImpl}
        onOutlineMapClick={handleMapClick}
        onDrawnVertexClick={onSelect}
        drawnOverlay={overlay}
      />
      <p className="visually-hidden" role="status" data-testid="proposal-outline-map-status">
        {drawnCount === 0
          ? "No points drawn yet."
          : `${drawnCount} point${drawnCount === 1 ? "" : "s"} drawn.${
              hasSelection ? ` Point ${selectedIndex} selected.` : ""
            }`}
      </p>
    </div>
  );
}
