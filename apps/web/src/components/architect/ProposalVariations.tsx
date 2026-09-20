"use client";

import { useState } from "react";
import type { ProposalVariation } from "@/lib/architect/proposal-draft";

/**
 * Client-local proposed-variations list (task M5-T060). The list is EPHEMERAL
 * client state: this browser session only, never saved, never a scenario
 * document, never a city record (D-076-R002; the platform is stateless and
 * scenario emission is a deliberately deferred packet). Save / select /
 * compare-two are all in-memory — no network write happens here.
 */

function summaryText(v: ProposalVariation): string {
  if (!v.report) return "not checked yet";
  const s = v.report.summary;
  return `${s.fail} fail · ${s.couldNotCheck} could not check · ${s.pass} pass`;
}

function VariationColumn({ v }: { v: ProposalVariation }) {
  return (
    <div className="proposal-compare-column" data-testid={`compare-column-${v.id}`}>
      <h5>{v.label}</h5>
      <p className="proposal-honesty">Proposed — not a city record.</p>
      <p className="proposal-variation-summary">{summaryText(v)}</p>
      {v.report ? (
        <ul>
          {v.report.results.map((r) => (
            <li key={r.checkId}>
              {r.label}: {r.outcome === "could_not_check" ? "could not check" : r.outcome}
            </li>
          ))}
        </ul>
      ) : (
        <p className="section-note">Run a check on this variation to compare its results.</p>
      )}
    </div>
  );
}

export function ProposalVariations({
  variations,
  activeId,
  canSave,
  onSave,
  onSelect,
}: {
  variations: ProposalVariation[];
  activeId: string | null;
  canSave: boolean;
  onSave: () => void;
  onSelect: (id: string) => void;
}) {
  const [leftId, setLeftId] = useState("");
  const [rightId, setRightId] = useState("");
  const left = variations.find((v) => v.id === leftId) ?? null;
  const right = variations.find((v) => v.id === rightId) ?? null;

  return (
    <section className="card proposal-variations" aria-label="Proposed variations">
      <h3>Proposed variations</h3>
      <p className="proposal-honesty" data-testid="variations-honesty">
        Proposed — your input, not a city record.
      </p>
      <p className="section-note" data-testid="variations-ephemeral">
        Kept in this browser session only — not saved.
      </p>
      <button
        type="button"
        className="secondary-button"
        onClick={onSave}
        disabled={!canSave}
        data-testid="save-variation"
      >
        Save current proposal as a variation
      </button>
      {variations.length === 0 ? (
        <p className="section-note">No variations saved yet.</p>
      ) : (
        <ul className="proposal-variation-list">
          {variations.map((v) => (
            <li key={v.id} className={v.id === activeId ? "is-active" : ""}>
              <button
                type="button"
                className="proposal-variation-select"
                aria-current={v.id === activeId ? "true" : undefined}
                onClick={() => onSelect(v.id)}
              >
                {v.label}
              </button>
              <span className="proposal-variation-summary">{summaryText(v)}</span>
            </li>
          ))}
        </ul>
      )}
      {variations.length >= 2 ? (
        <div className="proposal-compare" data-testid="variation-compare">
          <h4>Compare two variations</h4>
          <div className="proposal-compare-controls">
            <label>
              First variation
              <select value={leftId} onChange={(e) => setLeftId(e.target.value)}>
                <option value="">Choose…</option>
                {variations.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Second variation
              <select value={rightId} onChange={(e) => setRightId(e.target.value)}>
                <option value="">Choose…</option>
                {variations.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          {left && right ? (
            <div className="proposal-compare-grid">
              <VariationColumn v={left} />
              <VariationColumn v={right} />
            </div>
          ) : (
            <p className="section-note">Choose two saved variations to compare their results side by side.</p>
          )}
        </div>
      ) : null}
    </section>
  );
}
