"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { ProposalOutlineMap, isDrawnPointFinite, missingOrdinateLabel } from "./ProposalOutlineMap";
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

/** (e)/G3-A3 Delay between clearing the announcer and setting a blocked-press
 * reason, so a repeated press with the SAME reason still changes the region's
 * text on a later task and is announced again (OutcomeAnnouncer's clear-then-set
 * contract). */
const REANNOUNCE_DELAY_MS = 100;

/** (a) The omitted-rows clause shared by the post-convert counts line and the
 * post-convert announcement (a UI row tally, never a zoning number). */
function omittedRowsClause(n: number): string {
  return `${n} row${n === 1 ? "" : "s"} without both coordinates ${n === 1 ? "was" : "were"} not included`;
}

/** (a)/(F7) The single convert hint. `incompleteLabels` holds one
 * missingOrdinateLabel per incomplete row (rows the shared pair predicate
 * rejects); the hint names the missing ordinate exactly when every incomplete
 * row lacks the same one, and stays generic ("coordinates") otherwise. Three
 * honest cases:
 *  • too few finite points AND incomplete rows remain — fill or delete them;
 *  • too few finite points, all typed — add more;
 *  • enough to convert BUT incomplete rows remain — state how many Convert will
 *    LEAVE OUT, at the point of action, so omission is never silent. */
function convertHintCopy(finiteCount: number, incompleteLabels: string[]): string {
  const n = incompleteLabels.length;
  const one = n === 1;
  const shared = n > 0 && incompleteLabels.every((l) => l === incompleteLabels[0]) ? incompleteLabels[0] : "";
  const rows = `${n} row${one ? "" : "s"}`;
  const pronoun = one ? "it" : "them";
  if (finiteCount < MIN_DRAWN_VERTICES) {
    if (n === 0) {
      const more = MIN_DRAWN_VERTICES - finiteCount;
      return `Add ${more} more point${more === 1 ? "" : "s"} to convert — an outline needs at least ${MIN_DRAWN_VERTICES} points (you have ${finiteCount}).`;
    }
    return (
      `Convert needs at least ${MIN_DRAWN_VERTICES} points with both coordinates filled in. ` +
      `${rows} still need${one ? "s" : ""} ${shared ? `a ${shared}` : "coordinates"} — fill ${pronoun} in or ` +
      `delete ${pronoun} (${finiteCount} of ${MIN_DRAWN_VERTICES} ready).`
    );
  }
  if (n === 0) return "";
  return (
    `Convert will include ${finiteCount} point${finiteCount === 1 ? "" : "s"}. ` +
    `${rows} ${one ? "is" : "are"} missing ${shared ? `${one ? "its" : "their"} ${shared}` : "coordinates"} and ` +
    `will be left out — fill ${pronoun} in to include ${pronoun}, or delete ${pronoun}.`
  );
}

function refusalTestId(outcome: OutlineBridgeOutcome): string {
  return `outline-draw-${outcome.kind.replace(/_/g, "-")}`;
}

export function ProposalOutlineDraw({
  bbl,
  onAdopt,
  fetchImpl,
  adoptionRevision = 0,
}: {
  bbl: string;
  onAdopt: (vertices: DraftVertex[]) => void;
  fetchImpl?: typeof fetch;
  /** A receiving numeric-draft edit supersedes any conversion still in flight. */
  adoptionRevision?: number;
}) {
  const [points, setPoints] = useState<DrawnPoint[]>([]);
  const [converting, setConverting] = useState(false);
  const [outcome, setOutcome] = useState<OutlineBridgeOutcome | null>(null);
  const [announcement, setAnnouncement] = useState("");
  // (a) How many not-yet-typed rows the LAST conversion left out, captured at
  // convert time so the post-convert status can name the omitted count truthfully
  // (never a silent drop). The converted count comes from the server report.
  const [omittedOnConvert, setOmittedOnConvert] = useState(0);
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
  // G3-A4/HJ-5: Convert is described by the hint at the point of action.
  const hintId = useId();
  // (e)/G3-A3 The pending "set" half of a blocked press's clear-then-set. Any
  // conversion start/result, a newer blocked press, or unmount cancels it, so a
  // stale blocked reason can never overwrite a newer announcement.
  const reannounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelReannounce = useCallback(() => {
    if (reannounceTimer.current !== null) {
      clearTimeout(reannounceTimer.current);
      reannounceTimer.current = null;
    }
  }, []);
  const revisionRef = useRef(0);
  const pendingConversion = useRef<{ revision: number; controller: AbortController } | null>(null);
  const mounted = useRef(false);
  const cancelConversion = useCallback(() => {
    revisionRef.current += 1;
    const request = pendingConversion.current;
    pendingConversion.current = null;
    request?.controller.abort();
    cancelReannounce();
  }, [cancelReannounce]);
  const invalidateConversion = useCallback(() => {
    cancelConversion();
    setConverting(false);
    setAnnouncement("");
    // Keep the last completed outcome, including its refusal/provenance.
    // A superseded pending response must never replace that historical result.
  }, [cancelConversion]);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      cancelConversion();
    };
  }, [cancelConversion]);
  useEffect(() => {
    if (pendingConversion.current !== null) invalidateConversion();
  }, [bbl, adoptionRevision, invalidateConversion]);

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
    invalidateConversion();
    setPoints((ps) => [...ps, { lng: Number.NaN, lat: Number.NaN }]);
  }, [invalidateConversion]);

  // Place a point from a map click (finite display 4326 position). Appends into
  // the SAME points state the keyboard path uses (AS-1) — one drawn-outline
  // model. No selection is made, so consecutive clicks keep placing.
  const placePoint = useCallback((lngLat: { lng: number; lat: number }) => {
    invalidateConversion();
    setPoints((ps) => [...ps, { lng: lngLat.lng, lat: lngLat.lat }]);
  }, [invalidateConversion]);

  const updatePoint = useCallback((index: number, patch: Partial<DrawnPoint>) => {
    invalidateConversion();
    setPoints((ps) => ps.map((p, i) => (i === index ? { ...p, ...patch } : p)));
  }, [invalidateConversion]);

  // Move the currently-selected point to a clicked map position (AS-2 adjust via
  // the map). The keyboard equivalent is editing the row's lng/lat inputs.
  const moveSelectedPoint = useCallback(
    (lngLat: { lng: number; lat: number }) => {
      if (selectedIndex === null) return;
      invalidateConversion();
      setPoints((ps) => ps.map((p, i) =>
        i === selectedIndex ? { lng: lngLat.lng, lat: lngLat.lat } : p,
      ));
    },
    [selectedIndex, invalidateConversion],
  );

  // Toggle selection of a point (AS-2 select) — from a map-vertex click or the
  // table's Select control (keyboard equivalent).
  const selectPoint = useCallback((index: number) => {
    setSelectedIndex((sel) => (sel === index ? null : index));
  }, []);

  const deletePoint = useCallback((index: number) => {
    invalidateConversion();
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
  }, [invalidateConversion]);

  const drawnCount = points.length;
  // DB-047(e): Convert gates on the count of FINITE points (both ordinates a
  // finite number), never the raw row count. A freshly added keyboard row is
  // NaN/NaN until typed, so a count-only gate would launch a doomed bridge
  // round-trip on rows the overlay does not even draw. incompleteCount is the
  // number of added-but-not-yet-typed rows, used only to explain the disable.
  const finiteCount = points.filter(isDrawnPointFinite).length;
  const incompleteCount = drawnCount - finiteCount;
  const canConvert = finiteCount >= MIN_DRAWN_VERTICES && !converting;

  // (b)/(F7) One exact missing-ordinate label per incomplete row — the rows the
  // shared pair predicate rejects — so the hint never overstates what is missing.
  const incompleteLabels = points.filter((p) => !isDrawnPointFinite(p)).map(missingOrdinateLabel);
  // The single convert hint, shown INDEPENDENT of Convert enablement whenever a
  // row is incomplete or too few points exist (a).
  const convertHint = convertHintCopy(finiteCount, incompleteLabels);
  const hintVisible = drawnCount > 0 && (finiteCount < MIN_DRAWN_VERTICES || incompleteCount > 0);
  // (e) The reason a not-convertible Convert announces when activated.
  const convertBlockedReason = converting ? "Conversion is already in progress." : convertHint;

  const convert = useCallback(async () => {
    // Send only the finite points — a stray not-yet-typed row is never posted.
    // For an all-finite outline this is byte-identical to the accepted payload.
    const drawn = points
      .filter(isDrawnPointFinite)
      .map((p) => [p.lng, p.lat] as [number, number]);
    // (a) Record how many rows are being left out so the post-convert status can
    // name the omitted count — never a silent drop.
    const omitted = points.length - drawn.length;
    cancelConversion();
    const request = { revision: revisionRef.current, controller: new AbortController() };
    pendingConversion.current = request;
    setConverting(true);
    setAnnouncement("");
    const result = await fetchOutlineBridge({ bbl, drawn_vertices: drawn }, {
      fetchImpl,
      signal: request.controller.signal,
    });
    if (!mounted.current || pendingConversion.current !== request ||
        revisionRef.current !== request.revision || request.controller.signal.aborted) return;
    pendingConversion.current = null;
    cancelReannounce();
    setConverting(false);
    setOmittedOnConvert(omitted);
    setOutcome(result);
    // G3-A4/HJ-5: a successful conversion that left rows out says so in the
    // announcement too (the result card is not reliably spoken when it mounts).
    const announced = announcementForOutlineBridge(result);
    setAnnouncement(
      result.kind === "bridged" && omitted > 0 ? `${announced} ${omittedRowsClause(omitted)}.` : announced,
    );
    if (result.kind === "bridged") {
      onAdopt(result.report.vertices.map((v) => ({ x: v.x, y: v.y })));
    }
  }, [points, bbl, fetchImpl, onAdopt, cancelReannounce, cancelConversion]);

  // (e) Convert is aria-disabled (not `disabled`) while not convertible, so it
  // stays in the tab order (A7). Activating it in that state announces WHY
  // through the announcer ONLY — never the outcome card (G3-F1 / HJ-1) — and
  // makes NO bridge call. Clear, then set on a later task, so a repeated press
  // with the same reason is announced again (G3-A3 / HJ-6).
  const onConvertActivate = useCallback(() => {
    if (!canConvert) {
      cancelReannounce();
      setAnnouncement("");
      reannounceTimer.current = setTimeout(() => {
        reannounceTimer.current = null;
        setAnnouncement(convertBlockedReason);
      }, REANNOUNCE_DELAY_MS);
      return;
    }
    void convert();
  }, [canConvert, convert, convertBlockedReason, cancelReannounce]);

  return (
    <section className="proposal-outline-draw" data-testid="proposal-outline-draw" aria-label="Draw the building outline">
      <OutcomeAnnouncer testId="outline-draw-announcer" message={announcement} />
      <header className="proposal-outline-draw-head">
        <h3>Draw the outline</h3>
        {/* [ORCH-CORRECTED per HJ B1] State-neutral lead: the gesture invitation lives ONLY in
            the wrapper's map-state-gated instructions (DB-047(d)); this section header must never
            invite a map click it cannot promise. */}
        <p className="proposal-honesty" data-testid="outline-draw-honesty">
          Proposed — your sketch, not a city record. Add points and type them by keyboard in the
          table below, then convert them to numeric coordinates. The conversion is approximate
          proposed input with its fit accuracy disclosed — not a survey. The numbers table stays
          editable; typing coordinates is always an option.
        </p>
      </header>

      <div className="proposal-outline-draw-map" data-testid="outline-draw-map-context">
        {/* [ORCH-CORRECTED per HJ B1] No presence claim: on condo/fallback lots there is no map. */}
        <p className="section-note">
          Any reference map shown displays the recorded lot for context only. Nothing is measured
          from it; your drawing is converted to official-grid feet on the server.
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
          {points.map((p, i) => {
            // (b)/(F7) Completeness comes ONLY from the shared pair predicate
            // (G3-F3), so every row Convert omits carries the marker. The
            // per-ordinate booleans answer a different question — WHICH input is
            // missing — and feed only aria-invalid; never color alone, and never
            // claim a filled ordinate is missing.
            const rowComplete = isDrawnPointFinite(p);
            const rowMissing = missingOrdinateLabel(p);
            const lngFinite = Number.isFinite(p.lng);
            const latFinite = Number.isFinite(p.lat);
            return (
            <tr key={i} data-selected={i === selectedIndex} className={i === selectedIndex ? "is-selected" : undefined}>
              <th scope="row">
                {i}
                {!rowComplete ? (
                  <span className="row-incomplete-marker" data-testid={`outline-draw-row-incomplete-${i}`}>
                    {" "}
                    Needs {rowMissing}
                  </span>
                ) : null}
              </th>
              <td>
                <input
                  type="number"
                  aria-label={`Drawn point ${i} longitude`}
                  aria-invalid={lngFinite ? undefined : "true"}
                  value={numInputValue(p.lng)}
                  onChange={(e) => updatePoint(i, { lng: parseNum(e.target.value) })}
                />
              </td>
              <td>
                <input
                  type="number"
                  aria-label={`Drawn point ${i} latitude`}
                  aria-invalid={latFinite ? undefined : "true"}
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
            );
          })}
          {points.length === 0 ? (
            <tr>
              <td colSpan={4} className="section-note" data-testid="outline-draw-empty">
                No points drawn yet. Add at least {MIN_DRAWN_VERTICES} points, then convert.
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
          onClick={onConvertActivate}
          aria-disabled={!canConvert}
          aria-describedby={hintVisible ? hintId : undefined}
        >
          {converting ? "Converting…" : "Convert to numeric outline"}
        </button>
      </div>

      {hintVisible ? (
        // A persistent hint at the point of action. It renders INDEPENDENT of
        // Convert enablement (a): while too few finite points exist it explains
        // the disable (HJ-4 / DB-047(e)); once enough exist BUT incomplete rows
        // remain, it states exactly how many rows Convert will LEAVE OUT — so
        // omission is never silent. `convertHint` carries the exact-ordinate
        // wording (F7); Convert is described by it (G3-A4 / HJ-5).
        <p id={hintId} className="section-note" role="status" data-testid="outline-draw-min-hint">
          {convertHint}
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
              {/* (a) Name the converted count (from the server report) AND the
                  omitted count (rows without both coordinates, captured at convert
                  time) — never a silent omission. */}
              <p data-testid="outline-draw-convert-counts">
                {`${outcome.report.vertices.length} point${outcome.report.vertices.length === 1 ? "" : "s"} converted to numeric coordinates`}
                {omittedOnConvert > 0 ? `; ${omittedRowsClause(omittedOnConvert)}.` : "."}
              </p>
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
              {/* G3-F1 / HJ-1: the card's text comes from the OUTCOME alone. The
                  shared announcer state is also written by a blocked Convert
                  press ("Add 1 more point…", "Conversion is already in
                  progress."), which must never rewrite the server's refusal. */}
              <p>{announcementForOutlineBridge(outcome)}</p>
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
