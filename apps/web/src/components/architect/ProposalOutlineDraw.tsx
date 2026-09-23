"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { ProposalOutlineMap } from "./ProposalOutlineMap";
import type { DraftVertex } from "@/lib/architect/proposal-draft";
import {
  announcementForOutlineBridge,
  fetchOutlineBridge,
  type OutlineBridgeOutcome,
} from "@/lib/outline-bridge-api";

/**
 * Map-drawing input component (task M5-T065, D-082-R001). The architect sketches
 * a building-outline guess as an ordered list of DISPLAY EPSG:4326 points over
 * the recorded lot map, then converts them to the authoritative EPSG:2263
 * numeric model through the flag-gated outline-bridge route. Adoption is
 * ADDITIVE: the converted vertices land in the accepted draft exactly as if
 * typed, and the numeric table stays the visible, editable authority (manual
 * remains the option, D-082-R003).
 *
 * HONESTY (D-076-R002): the drawn shape is PROPOSED input, never a city record,
 * and the converted coordinates are the bridge's output with its residual
 * disclosed — never presented as survey-grade measurement. The recorded
 * LotOutlineMap is COMPOSED read-only for context; nothing is measured from it
 * and no client-side 4326->2263 transform lives here (the no-reprojection
 * doctrine — the conversion is server-side by correspondence).
 *
 * ACCESSIBILITY: every action is keyboard-operable — each drawn point has
 * labeled lng/lat number inputs and a Delete button, and Add/Convert are plain
 * buttons. Focus is MANAGED on delete (the DB-043(a) remedy applied from the
 * start): rather than focus a ref synchronously in the delete handler (whose
 * state change remounts the row), a nonce records the intended target and a
 * useEffect moves focus after the re-render (CODING_RULES).
 */

/** Mirror of BRIDGE_MIN_DRAWN_VERTICES (outline_bridge.py): an outline is at
 * least a triangle. The route remains the authority; this only gates the button
 * so an obviously-too-small POST is spared. */
export const MIN_DRAWN_VERTICES = 3;

interface DrawnPoint {
  lng: number;
  lat: number;
}

function parseNum(raw: string): number {
  return raw.trim() === "" ? Number.NaN : Number(raw);
}
function numInputValue(n: number): string {
  return Number.isFinite(n) ? String(n) : "";
}

function refusalTestId(outcome: OutlineBridgeOutcome): string {
  return `outline-draw-${outcome.kind.replace(/_/g, "-")}`;
}

export function ProposalOutlineDraw({
  bbl,
  onAdopt,
  fetchImpl,
}: {
  bbl: string;
  onAdopt: (vertices: DraftVertex[]) => void;
  fetchImpl?: typeof fetch;
}) {
  const [points, setPoints] = useState<DrawnPoint[]>([]);
  const [converting, setConverting] = useState(false);
  const [outcome, setOutcome] = useState<OutlineBridgeOutcome | null>(null);
  const [announcement, setAnnouncement] = useState("");
  // The point selected on the map (or via the table's Select control). A
  // selected point is what a map click MOVES; selecting also drives the map
  // highlight and the selected-row styling. null = nothing selected (a map
  // click PLACES a new point).
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  // Focus-on-delete: the delete handler records the intended focus target
  // (a row index, or -1 for the Add button) and a useEffect applies it AFTER
  // the remove re-render, never synchronously against a remounting node.
  const [pendingFocus, setPendingFocus] = useState<number | null>(null);
  const listRef = useRef<HTMLTableSectionElement | null>(null);
  const addRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (pendingFocus === null) return;
    if (pendingFocus < 0) {
      addRef.current?.focus();
    } else {
      const target = listRef.current?.querySelector<HTMLButtonElement>(
        `[data-point-delete="${pendingFocus}"]`,
      );
      (target ?? addRef.current)?.focus();
    }
    setPendingFocus(null);
  }, [pendingFocus]);

  const addPoint = useCallback(() => {
    setPoints((ps) => [...ps, { lng: Number.NaN, lat: Number.NaN }]);
  }, []);

  // Place a point from a map click (finite display 4326 position). Appends into
  // the SAME points state the keyboard path uses (AS-1) — one drawn-outline
  // model. No selection is made, so consecutive clicks keep placing.
  const placePoint = useCallback((lngLat: { lng: number; lat: number }) => {
    setPoints((ps) => [...ps, { lng: lngLat.lng, lat: lngLat.lat }]);
  }, []);

  const updatePoint = useCallback((index: number, patch: Partial<DrawnPoint>) => {
    setPoints((ps) => ps.map((p, i) => (i === index ? { ...p, ...patch } : p)));
  }, []);

  // Move the currently-selected point to a clicked map position (AS-2 adjust via
  // the map). The keyboard equivalent is editing the row's lng/lat inputs.
  const moveSelectedPoint = useCallback(
    (lngLat: { lng: number; lat: number }) => {
      setSelectedIndex((sel) => {
        if (sel !== null) {
          setPoints((ps) => ps.map((p, i) => (i === sel ? { lng: lngLat.lng, lat: lngLat.lat } : p)));
        }
        return sel;
      });
    },
    [],
  );

  // Toggle selection of a point (AS-2 select) — from a map-vertex click or the
  // table's Select control (keyboard equivalent).
  const selectPoint = useCallback((index: number) => {
    setSelectedIndex((sel) => (sel === index ? null : index));
  }, []);

  const deletePoint = useCallback((index: number) => {
    setPoints((ps) => {
      const next = ps.filter((_, i) => i !== index);
      // Keep focus on a delete control: the row that slid up into this index,
      // else the previous row, else the Add button when the list is now empty.
      setPendingFocus(next.length === 0 ? -1 : Math.min(index, next.length - 1));
      return next;
    });
    // Reconcile the selection so it never dangles past the removed row.
    setSelectedIndex((sel) => {
      if (sel === null) return null;
      if (sel === index) return null;
      return sel > index ? sel - 1 : sel;
    });
  }, []);

  const drawnCount = points.length;
  // DB-047(e): Convert gates on the count of FINITE points (both ordinates a
  // finite number), never the raw row count. A freshly added keyboard row is
  // NaN/NaN until typed, so a count-only gate would launch a doomed bridge
  // round-trip on rows the overlay does not even draw. incompleteCount is the
  // number of added-but-not-yet-typed rows, used only to explain the disable.
  const finiteCount = points.filter(
    (p) => Number.isFinite(p.lng) && Number.isFinite(p.lat),
  ).length;
  const incompleteCount = drawnCount - finiteCount;
  const canConvert = finiteCount >= MIN_DRAWN_VERTICES && !converting;

  const convert = useCallback(async () => {
    // Send only the finite points — a stray not-yet-typed row is never posted.
    // For an all-finite outline this is byte-identical to the accepted payload.
    const drawn = points
      .filter((p) => Number.isFinite(p.lng) && Number.isFinite(p.lat))
      .map((p) => [p.lng, p.lat] as [number, number]);
    setConverting(true);
    setAnnouncement("");
    const result = await fetchOutlineBridge({ bbl, drawn_vertices: drawn }, { fetchImpl });
    setConverting(false);
    setOutcome(result);
    setAnnouncement(announcementForOutlineBridge(result));
    if (result.kind === "bridged") {
      onAdopt(result.report.vertices.map((v) => ({ x: v.x, y: v.y })));
    }
  }, [points, bbl, fetchImpl, onAdopt]);

  return (
    <section className="proposal-outline-draw" data-testid="proposal-outline-draw" aria-label="Draw the building outline">
      <OutcomeAnnouncer testId="outline-draw-announcer" message={announcement} />
      <header className="proposal-outline-draw-head">
        <h3>Draw the outline</h3>
        <p className="proposal-honesty" data-testid="outline-draw-honesty">
          Proposed — your sketch, not a city record. Click the lot map to place points (or add and type
          them by keyboard below), then convert them to numeric coordinates. The conversion is approximate
          proposed input with its fit accuracy disclosed — not a survey. The numbers table stays editable;
          typing coordinates is always an option.
        </p>
      </header>

      <div className="proposal-outline-draw-map" data-testid="outline-draw-map-context">
        <p className="section-note">
          The map shows the recorded lot for reference. Nothing is measured from it; your drawing is
          converted to official-grid feet on the server.
        </p>
        <ProposalOutlineMap
          bbl={bbl}
          points={points}
          selectedIndex={selectedIndex}
          onPlace={placePoint}
          onSelect={selectPoint}
          onMoveSelected={moveSelectedPoint}
          fetchImpl={fetchImpl}
        />
      </div>

      <table className="proposal-outline-draw-table">
        <caption>Drawn points (display longitude / latitude) — a proposed sketch, converted server-side</caption>
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col">Longitude</th>
            <th scope="col">Latitude</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody ref={listRef}>
          {points.map((p, i) => (
            <tr key={i} data-selected={i === selectedIndex} className={i === selectedIndex ? "is-selected" : undefined}>
              <th scope="row">{i}</th>
              <td>
                <input
                  type="number"
                  aria-label={`Drawn point ${i} longitude`}
                  value={numInputValue(p.lng)}
                  onChange={(e) => updatePoint(i, { lng: parseNum(e.target.value) })}
                />
              </td>
              <td>
                <input
                  type="number"
                  aria-label={`Drawn point ${i} latitude`}
                  value={numInputValue(p.lat)}
                  onChange={(e) => updatePoint(i, { lat: parseNum(e.target.value) })}
                />
              </td>
              <td>
                <button
                  type="button"
                  data-point-select={i}
                  aria-pressed={i === selectedIndex}
                  aria-label={`${i === selectedIndex ? "Deselect" : "Select"} drawn point ${i}`}
                  onClick={() => selectPoint(i)}
                >
                  {i === selectedIndex ? "Deselect" : "Select"}
                </button>
                <button
                  type="button"
                  data-point-delete={i}
                  aria-label={`Delete drawn point ${i}`}
                  onClick={() => deletePoint(i)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
          {points.length === 0 ? (
            <tr>
              <td colSpan={4} className="section-note" data-testid="outline-draw-empty">
                No points drawn yet. Add at least {MIN_DRAWN_VERTICES} points over the lot, then convert.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>

      <div className="proposal-outline-draw-actions">
        <button ref={addRef} type="button" className="secondary-button" onClick={addPoint}>
          Add drawn point
        </button>
        <button
          type="button"
          className="primary-button"
          data-testid="outline-draw-convert"
          onClick={convert}
          disabled={!canConvert}
        >
          {converting ? "Converting…" : "Convert to numeric outline"}
        </button>
      </div>

      {drawnCount > 0 && finiteCount < MIN_DRAWN_VERTICES ? (
        // A persistent hint explaining why Convert is disabled. Two reasons can
        // apply: not enough points yet (HJ-4, DB-045(g)), or rows added but not
        // yet typed (DB-047(e)). The finite count is what actually counts toward
        // conversion, so the hint speaks to it, never the raw row count.
        <p className="section-note" role="status" data-testid="outline-draw-min-hint">
          {incompleteCount > 0
            ? `Convert needs at least ${MIN_DRAWN_VERTICES} points with both coordinates filled in. ` +
              `${incompleteCount} row${incompleteCount === 1 ? "" : "s"} still ` +
              `need${incompleteCount === 1 ? "s" : ""} a longitude and latitude — fill ` +
              `${incompleteCount === 1 ? "it" : "them"} in or delete ` +
              `${incompleteCount === 1 ? "it" : "them"} (${finiteCount} of ${MIN_DRAWN_VERTICES} ready).`
            : `Add ${MIN_DRAWN_VERTICES - finiteCount} more point${MIN_DRAWN_VERTICES - finiteCount === 1 ? "" : "s"} to convert — an outline needs at least ${MIN_DRAWN_VERTICES} points (you have ${finiteCount}).`}
        </p>
      ) : null}

      {outcome !== null && outcome.kind !== "aborted" ? (
        <section
          className={outcome.kind === "bridged" ? "card" : "card failure-state"}
          data-testid="outline-draw-status"
          data-outcome-kind={outcome.kind}
          role={outcome.kind === "bridged" ? "status" : "alert"}
        >
          {outcome.kind === "bridged" ? (
            <div data-testid={refusalTestId(outcome)}>
              <strong>Outline converted to numeric coordinates</strong>
              <p>{outcome.report.disclosure}</p>
              <dl className="outline-draw-provenance">
                <dt>Fit residual (RMS)</dt>
                <dd data-testid="outline-draw-residual">
                  {outcome.report.correspondence.rmsResidualFt === null
                    ? "disclosed by the server"
                    : `${outcome.report.correspondence.rmsResidualFt} ft`}
                </dd>
                <dt>Correspondence method</dt>
                <dd>{outcome.report.correspondence.method}</dd>
                <dt>Alignment</dt>
                <dd>{outcome.report.correspondence.alignment}</dd>
                <dt>Source rings</dt>
                <dd>
                  {outcome.report.correspondence.sourceDisplayRing.sourceId ?? "display"} (
                  {outcome.report.correspondence.sourceDisplayRing.crs ?? "4326"}) ·{" "}
                  {outcome.report.correspondence.sourceAuthoritativeRing.sourceId ?? "authoritative"} (
                  {outcome.report.correspondence.sourceAuthoritativeRing.crs ?? "2263"})
                </dd>
              </dl>
            </div>
          ) : (
            <div data-testid={refusalTestId(outcome)}>
              <strong>Outline not converted</strong>
              <p>{announcement}</p>
              {outcome.kind === "residual_too_high" ? (
                <p className="failure-meta" data-testid="outline-draw-residual-detail">
                  Fit residual{" "}
                  {outcome.rmsResidualFt === null ? "was over" : `${outcome.rmsResidualFt} ft exceeds`} the
                  bound{outcome.residualBoundFt === null ? "" : ` of ${outcome.residualBoundFt} ft`}. No
                  coordinates were produced.
                </p>
              ) : null}
              {"reason" in outcome && outcome.reason ? (
                <p className="failure-meta" data-testid="outline-draw-reason">
                  Reason: {outcome.reason}
                </p>
              ) : null}
            </div>
          )}
        </section>
      ) : null}
    </section>
  );
}
