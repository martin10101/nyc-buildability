"use client";

import { useMemo } from "react";
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
 */

export interface DrawnPoint {
  lng: number;
  lat: number;
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

  // A map click MOVES the selected point when one is selected, else PLACES a new
  // point. A click that lands on a drawn vertex SELECTS it (LotOutlineMap
  // routes that to onDrawnVertexClick). Every one of these has a keyboard
  // equivalent in the table (Add / Select / the lng-lat inputs / Delete).
  const handleMapClick = (lngLat: { lng: number; lat: number }) => {
    if (hasSelection) onMoveSelected(lngLat);
    else onPlace(lngLat);
  };

  return (
    <div className="proposal-outline-map" data-testid="proposal-outline-map">
      <p className="section-note" data-testid="proposal-outline-map-instructions">
        {hasSelection
          ? `Point ${selectedIndex} is selected — click the map to move it, or edit it in the table below. Click the point again to deselect.`
          : "Click the lot map to place a proposed outline point, or add points by keyboard in the table below. Click a placed point to select it."}
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
        {points.length === 0
          ? "No points drawn yet."
          : `${points.length} point${points.length === 1 ? "" : "s"} drawn.${
              hasSelection ? ` Point ${selectedIndex} selected.` : ""
            }`}
      </p>
    </div>
  );
}
