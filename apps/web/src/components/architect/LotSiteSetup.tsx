"use client";

/**
 * Lot choice + site facts with source labels (queue D-04, plan M1-13, §3 steps
 * 2-3, §4; §5a). Presentation only, over a contract-shaped Study read from the
 * C-05 shared store. It renders:
 *  - the lots that make up the site, each with its approximate size and source;
 *  - whether the selected lots were combined, and — when they were not — the
 *    reason, taken verbatim from B-07's `lot_selection.combination` (the web
 *    never re-checks geometry or adjacency, lane prompt);
 *  - the owner-pinned statement that the app does not verify the zoning lot;
 *  - each site fact with its source label, its full source behind a tap.
 *
 * No measurement is invented: when the study is not connected yet (B-07/B-02 are
 * not wired to the web — see docs/lanes/requests/D-1.md), the panel shows a plain
 * "not connected" card, never a guessed number (plan §5a item 3).
 *
 * This slice is read-only. Re-picking the lots and editing a fact need the C-05
 * mutation path plus a fresh B-07 combination check per selection, which Lane C
 * has not wired yet; they are the next slice (see the request file).
 */

import { lotChoiceView, siteFactRows } from "@/lib/architect/lot-site-setup";
import type { Study } from "@/lib/study/study-vocabulary";
import { useStudy } from "@/lib/study/use-study";

export function LotSiteSetup({ bbl, study: studyProp }: { bbl: string; study?: Study | null }) {
  const stored = useStudy(bbl);
  const study = studyProp ?? stored?.study ?? null;

  if (!study) {
    return (
      <section className="card architect-empty" data-testid="lot-site-unavailable">
        <p className="architect-eyebrow">Lot &amp; site setup</p>
        <h2>Site setup is not connected yet</h2>
        <p>
          The lots that make up this site and their pre-filled measurements are prepared by the
          site-facts service. That data is not connected to this screen yet, so there is nothing to
          show here. No measurements are guessed.
        </p>
      </section>
    );
  }

  const choice = lotChoiceView(study);
  const facts = siteFactRows(study);

  return (
    <div data-testid="lot-site-setup" className="lot-site-setup">
      <section className="card" aria-label="Lot choice">
        <h2>{choice.heading}</h2>
        <p className="section-note">{choice.pickLine}</p>
        <ul className="lot-site-list">
          {choice.lots.map((lot) => (
            <li key={lot.bbl} data-testid={`lot-row-${lot.bbl}`} className="lot-site-row">
              <span className="lot-site-row__main">
                {lot.lotLabel} · {lot.sizeText}
              </span>
              <span className="lot-site-row__source">{lot.sourceLabel}</span>
              <span className="lot-site-row__pick">{lot.selected ? "In the site" : "Not selected"}</span>
            </li>
          ))}
        </ul>
        <div
          className={`lot-site-combination${choice.combination.refused ? " lot-site-combination--refused" : ""}`}
          role={choice.combination.refused ? "note" : undefined}
          data-testid={choice.combination.refused ? "lot-combination-refusal" : "lot-combination"}
        >
          <p className="lot-site-combination__heading">{choice.combination.heading}</p>
          {choice.combination.detail ? <p>{choice.combination.detail}</p> : null}
        </div>
        <p className="lot-site-statement" role="note" data-testid="lot-site-statement">
          {choice.statement}
        </p>
      </section>

      <section className="card" aria-label="Site facts">
        <h2>Site facts</h2>
        <p className="section-note">
          Each value shows where it came from. Nothing here has to be typed when a city value is on
          file.
        </p>
        <dl className="lot-site-facts">
          {facts.map((fact) => (
            <div key={fact.factId} data-testid={`site-fact-${fact.factId}`} className="lot-site-fact">
              <dt>{fact.label}</dt>
              <dd>
                <span
                  className={`lot-site-fact__value${fact.isUnknown ? " lot-site-fact__value--unknown" : ""}`}
                >
                  {fact.valueText}
                </span>
                <span className="lot-site-fact__source">{fact.sourceLabel}</span>
                {fact.isUnknown && fact.blocks.length ? (
                  <p className="lot-site-fact__blocks">Needed for: {fact.blocks.join(", ")}.</p>
                ) : null}
                <details className="lot-site-fact__detail">
                  <summary>Source</summary>
                  <ul>
                    {fact.sourceLines.map((line, index) => (
                      <li key={index}>{line}</li>
                    ))}
                  </ul>
                </details>
              </dd>
            </div>
          ))}
        </dl>
      </section>
    </div>
  );
}
