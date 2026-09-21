"use client";

import { useCallback, useState } from "react";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import {
  addLevel,
  addVertex,
  addWall,
  adoptOutlineVertices,
  rectangleSampleDraft,
  removeLevel,
  removeVertex,
  removeWall,
  toProposalCheckRequest,
  updateLevel,
  updateVertex,
  updateWall,
  validateDraft,
  type DraftProblem,
  type DraftVertex,
  type ProposalDraft,
  type ProposalVariation,
} from "@/lib/architect/proposal-draft";
import {
  announcementForProposalCheck,
  fetchProposalCheck,
  type ProposalCheckOutcome,
} from "@/lib/proposal-checks-api";
import { ProposalCheckReport } from "./ProposalCheckReport";
import { ProposalOutlineDraw } from "./ProposalOutlineDraw";
import { ProposalVariations } from "./ProposalVariations";

/**
 * Proposal editor container (task M5-T060, D-076 phase B3 slice 2). A
 * keyboard-first draft editor whose primary input is the NUMERIC EPSG:2263
 * vertex table (the draft authority); levels and exterior walls are numeric
 * forms beside it. A run-check POSTs the draft to /api/v1/proposal-checks and
 * renders the grouped report; saved variations are client-local and ephemeral.
 *
 * The recorded lot-outline map is COMPOSED read-only beside the form for
 * context only (display CRS is display-only; nothing is measured from it). When
 * a BBL is present, the released map-drawing input (task M5-T065, D-082-R001) is
 * offered beside it: the architect sketches a 4326 outline, the server bridges
 * it to authoritative EPSG:2263 by correspondence (no client-side transform),
 * and the converted vertices land in this numeric draft EXACTLY as if typed —
 * the table stays the visible, editable authority (manual remains the option,
 * D-082-R003). Scenario emission stays deferred.
 */

let variationSeq = 0;

function numInputValue(n: number): string {
  return Number.isFinite(n) ? String(n) : "";
}
function parseNum(raw: string): number {
  return raw.trim() === "" ? Number.NaN : Number(raw);
}

export function ProposalEditor({ bbl, fetchImpl }: { bbl?: string | null; fetchImpl?: typeof fetch }) {
  const [draft, setDraft] = useState<ProposalDraft>(() => rectangleSampleDraft());
  const [outcome, setOutcome] = useState<ProposalCheckOutcome | null>(null);
  const [checking, setChecking] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const [draftProblems, setDraftProblems] = useState<DraftProblem[]>([]);
  const [variations, setVariations] = useState<ProposalVariation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  const runCheck = useCallback(async () => {
    const problems = validateDraft(draft);
    setDraftProblems(problems);
    if (problems.length > 0) {
      // Mirror validation blocked the draft client-side (each problem names its
      // route constant). The server refusal remains the truth; this only spares
      // an obviously-doomed POST.
      setOutcome(null);
      setAnnouncement("Proposal not sent: the draft has input problems, listed below.");
      return;
    }
    setChecking(true);
    setAnnouncement("");
    const result = await fetchProposalCheck(toProposalCheckRequest(draft), { fetchImpl });
    setChecking(false);
    setOutcome(result);
    setAnnouncement(announcementForProposalCheck(result));
    if (result.kind === "report" && activeId) {
      setVariations((vs) => vs.map((v) => (v.id === activeId ? { ...v, report: result.report } : v)));
    }
  }, [draft, fetchImpl, activeId]);

  const saveVariation = useCallback(() => {
    variationSeq += 1;
    const id = `variation-${variationSeq}`;
    const report = outcome && outcome.kind === "report" ? outcome.report : null;
    setVariations((vs) => [
      ...vs,
      { id, label: draft.scenario_label.trim() || `Variation ${vs.length + 1}`, draft, report },
    ]);
    setActiveId(id);
    setAnnouncement("Saved the current proposal as a variation (this browser session only).");
  }, [draft, outcome]);

  // Adopt map-drawn vertices into the numeric draft EXACTLY as if typed (task
  // M5-T065, D-082-R001/R003): the converted EPSG:2263 vertices from the
  // outline-bridge replace the draft outline, the numeric table stays the
  // visible/editable authority, and a fresh check must be run on the adopted
  // shape (the old outcome no longer describes the current draft).
  const adoptDrawnOutline = useCallback((vertices: DraftVertex[]) => {
    setDraft((d) => adoptOutlineVertices(d, vertices));
    setDraftProblems([]);
    setOutcome(null);
    setAnnouncement(
      `Adopted ${vertices.length} drawn points into the numeric outline — proposed input you can edit; run the check when ready.`,
    );
  }, []);

  const selectVariation = useCallback(
    (id: string) => {
      const found = variations.find((v) => v.id === id);
      if (!found) return;
      setActiveId(id);
      setDraft(found.draft);
      setDraftProblems([]);
      setOutcome(
        found.report
          ? { kind: "report", report: found.report, correlationId: found.report.correlationId }
          : null,
      );
      setAnnouncement(`Loaded variation ${found.label}.`);
    },
    [variations],
  );

  return (
    <div className="proposal-editor" data-testid="proposal-editor">
      <OutcomeAnnouncer testId="proposal-check-announcer" message={announcement} />
      <header className="proposal-editor-head">
        <h2>Proposal editor</h2>
        <p className="proposal-honesty" data-testid="editor-honesty">
          Proposed — your input, not a city record. You enter the numbers; the check compares them
          against the rules and returns a preliminary result that requires professional review.
        </p>
      </header>

      <div className="proposal-editor-grid">
        <form className="proposal-editor-form" onSubmit={(e) => e.preventDefault()}>
          <div className="field-group">
            <label className="field-label" htmlFor="proposal-scenario-label">
              Proposal label
            </label>
            <input
              id="proposal-scenario-label"
              className="text-input"
              value={draft.scenario_label}
              onChange={(e) => setDraft((d) => ({ ...d, scenario_label: e.target.value }))}
            />
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="proposal-id">
              Proposal id (optional)
            </label>
            <input
              id="proposal-id"
              className="text-input"
              value={draft.proposal_id}
              onChange={(e) => setDraft((d) => ({ ...d, proposal_id: e.target.value }))}
            />
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="proposal-zoning-district">
              Zoning district (caller-attested)
            </label>
            <input
              id="proposal-zoning-district"
              className="text-input"
              value={draft.zoning_district}
              onChange={(e) => setDraft((d) => ({ ...d, zoning_district: e.target.value }))}
            />
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="proposal-street-width">
              Street width class (caller-attested)
            </label>
            <select
              id="proposal-street-width"
              className="text-input"
              value={draft.street_width_class}
              onChange={(e) =>
                setDraft((d) => ({ ...d, street_width_class: e.target.value as ProposalDraft["street_width_class"] }))
              }
            >
              <option value="">Not attested</option>
              <option value="wide">Wide</option>
              <option value="narrow">Narrow</option>
            </select>
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="proposal-lot-area">
              Lot area (sq ft, caller-attested)
            </label>
            <input
              id="proposal-lot-area"
              type="number"
              className="text-input"
              value={draft.lot_area_sq_ft === null ? "" : numInputValue(draft.lot_area_sq_ft)}
              onChange={(e) =>
                setDraft((d) => ({ ...d, lot_area_sq_ft: e.target.value.trim() === "" ? null : parseNum(e.target.value) }))
              }
            />
          </div>

          <table className="proposal-vertex-table">
            <caption>Outline vertices (EPSG:2263 feet) — the numeric authority for this proposal</caption>
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">X (ft)</th>
                <th scope="col">Y (ft)</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {draft.vertices.map((v, i) => (
                <tr key={i}>
                  <th scope="row">{i}</th>
                  <td>
                    <input
                      type="number"
                      aria-label={`Vertex ${i} X coordinate`}
                      value={numInputValue(v.x)}
                      onChange={(e) => setDraft((d) => updateVertex(d, i, { x: parseNum(e.target.value) }))}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      aria-label={`Vertex ${i} Y coordinate`}
                      value={numInputValue(v.y)}
                      onChange={(e) => setDraft((d) => updateVertex(d, i, { y: parseNum(e.target.value) }))}
                    />
                  </td>
                  <td>
                    <button type="button" onClick={() => setDraft((d) => removeVertex(d, i))} aria-label={`Delete vertex ${i}`}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button type="button" className="secondary-button" onClick={() => setDraft((d) => addVertex(d, { x: 0, y: 0 }))}>
            Add vertex
          </button>

          <table className="proposal-level-table">
            <caption>Levels</caption>
            <thead>
              <tr>
                <th scope="col">Level</th>
                <th scope="col">Floor count</th>
                <th scope="col">Floor-to-floor (ft)</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {draft.levels.map((l, i) => (
                <tr key={i}>
                  <td>
                    <input
                      type="number"
                      aria-label={`Level ${i} index`}
                      value={numInputValue(l.level_index)}
                      onChange={(e) => setDraft((d) => updateLevel(d, i, { level_index: parseNum(e.target.value) }))}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      aria-label={`Level ${i} floor count`}
                      value={numInputValue(l.floor_count)}
                      onChange={(e) => setDraft((d) => updateLevel(d, i, { floor_count: parseNum(e.target.value) }))}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      aria-label={`Level ${i} floor to floor height`}
                      value={numInputValue(l.floor_to_floor_ft)}
                      onChange={(e) => setDraft((d) => updateLevel(d, i, { floor_to_floor_ft: parseNum(e.target.value) }))}
                    />
                  </td>
                  <td>
                    <button type="button" onClick={() => setDraft((d) => removeLevel(d, i))} aria-label={`Delete level ${i}`}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button
            type="button"
            className="secondary-button"
            onClick={() => setDraft((d) => addLevel(d, { level_index: d.levels.length, floor_count: 1, floor_to_floor_ft: 10 }))}
          >
            Add level
          </button>

          <table className="proposal-wall-table">
            <caption>Exterior walls</caption>
            <thead>
              <tr>
                <th scope="col">Id</th>
                <th scope="col">Start vertex</th>
                <th scope="col">End vertex</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {draft.exterior_walls.map((w, i) => (
                <tr key={i}>
                  <td>
                    <input
                      aria-label={`Wall ${i} id`}
                      value={w.id}
                      onChange={(e) => setDraft((d) => updateWall(d, i, { id: e.target.value }))}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      aria-label={`Wall ${i} start vertex index`}
                      value={numInputValue(w.start_vertex_index)}
                      onChange={(e) => setDraft((d) => updateWall(d, i, { start_vertex_index: parseNum(e.target.value) }))}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      aria-label={`Wall ${i} end vertex index`}
                      value={numInputValue(w.end_vertex_index)}
                      onChange={(e) => setDraft((d) => updateWall(d, i, { end_vertex_index: parseNum(e.target.value) }))}
                    />
                  </td>
                  <td>
                    <button type="button" onClick={() => setDraft((d) => removeWall(d, i))} aria-label={`Delete wall ${i}`}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button
            type="button"
            className="secondary-button"
            onClick={() => setDraft((d) => addWall(d, { id: `W-${d.exterior_walls.length}`, start_vertex_index: 0, end_vertex_index: 0 }))}
          >
            Add wall
          </button>

          <div className="proposal-run">
            <button type="button" className="primary-button" onClick={runCheck} disabled={checking} data-testid="run-check">
              {checking ? "Checking…" : "Run check"}
            </button>
          </div>

          {draftProblems.length ? (
            <section className="card failure-state proposal-draft-problems" role="alert" data-testid="draft-problems">
              <strong>Proposal not sent</strong>
              <p>The draft was blocked before sending. Fix these to match what the checking service will accept:</p>
              <ul>
                {draftProblems.map((p, i) => (
                  <li key={i}>
                    {p.message} <span className="proposal-route-constant">(route: {p.routeConstant})</span>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </form>

        <aside className="proposal-editor-aside">
          {bbl ? (
            <div className="proposal-map-context" data-testid="proposal-map-context">
              <ProposalOutlineDraw bbl={bbl} onAdopt={adoptDrawnOutline} fetchImpl={fetchImpl} />
            </div>
          ) : null}
          <ProposalCheckReport outcome={outcome} checking={checking} />
          <ProposalVariations
            variations={variations}
            activeId={activeId}
            canSave={draft.vertices.length > 0}
            onSave={saveVariation}
            onSelect={selectVariation}
          />
        </aside>
      </div>
    </div>
  );
}
