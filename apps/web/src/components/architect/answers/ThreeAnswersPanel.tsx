"use client";

import { useId } from "react";
import {
  DRAFT_PREVIEW_TAG,
  answerView,
  buildingOptionNotesView,
  remainingFloorAreaView,
  scopeAssumptionKeyLabel,
  scopeAssumptionValueText,
  scopeView,
  shortfallView,
  type Scope,
  type ThreeAnswersResults,
} from "@/lib/architect/three-answers";
import { firstBuildingOptionsView } from "@/lib/architect/first-building-options";
import { AnswerCard, BuildingOptionNotes, ShortfallBlock, SupplementRow } from "./AnswerCard";
import { FirstBuildingOptions } from "./FirstBuildingOptions";
import { ResultsStatusStrip } from "./ResultsStatusStrip";
import { ScopeSummary } from "./ScopeSummary";
import { SharedConditions } from "./SharedConditions";
import "./three-answers.css";

export interface ThreeAnswersPanelProps {
  /** One `results` contract document (generated type packages/contracts/generated/results.ts). */
  results: ThreeAnswersResults;
  /**
   * Show numbers computed from rules that are not reviewed yet (`results.draft`). Only a surface
   * behind a lane flag may set this; absent or false, every available answer of a draft document
   * reads "Not available — the rules for this answer are not reviewed yet" (D-090-R010).
   */
  showDraftValues?: boolean;
}

// The two scope assumptions the identity line names beside the lot (presentation contract §2
// item 1): the housing program and the floor-to-floor height. Read from the document; never typed.
const IDENTITY_KEYS = ["housing_program", "floor_to_floor_ft"] as const;

/**
 * The architect-facing results slice (presentation contract step 3; M5-T149 part A). In the
 * contract's reading order: the property identity first; then one short context strip; then the
 * shared conditions stated once; then the three answers together, each a short face with its
 * derivation on demand. The building options (Part B) and the detailed scope follow. It renders one
 * `results` document and fetches nothing; Part C wires the live request and the window around it.
 */
export function ThreeAnswersPanel({ results, showDraftValues = false }: ThreeAnswersPanelProps) {
  const headingId = useId();
  const scope = scopeView(results);
  const remaining = remainingFloorAreaView(results);
  const firstOptions = firstBuildingOptionsView(results, showDraftValues);
  return (
    <section className="ta-panel" aria-labelledby={headingId} data-testid="three-answers-panel">
      <h2 id={headingId} className="ta-panel-title">
        Results
        {results.draft && showDraftValues ? (
          <span className="ta-draft-tag" data-testid="three-answers-draft-tag">
            {` — ${DRAFT_PREVIEW_TAG}`}
          </span>
        ) : null}
      </h2>
      {/* Desktop (window content >= 1000 px): a two-column grid — the answers on the left, the
         details and the building options on the right. Below 1000 px the two regions stack in the
         same reading order (M5-T149 orchestrator addition; presentation contract §3). */}
      <div className="ta-layout">
        <div className="ta-left" data-testid="three-answers-left">
          {results.scope ? <IdentityLine scope={results.scope} /> : null}
          <ResultsStatusStrip results={results} />
          <SharedConditions results={results} />
          <div className="ta-answers">
            <AnswerCard
              answerKey="floor_area_allowance"
              view={answerView(results, "floor_area_allowance", showDraftValues)}
            >
              {remaining ? <SupplementRow view={remaining} /> : null}
            </AnswerCard>
            <AnswerCard
              answerKey="permitted_envelope"
              view={answerView(results, "permitted_envelope", showDraftValues)}
            />
            <AnswerCard
              answerKey="building_option"
              view={answerView(results, "building_option", showDraftValues)}
            >
              <ShortfallBlock view={shortfallView(results)} />
              <BuildingOptionNotes notes={buildingOptionNotesView(results)} />
            </AnswerCard>
          </div>
        </div>
        <div className="ta-right" data-testid="three-answers-right">
          {scope ? <ScopeSummary view={scope} /> : null}
          {firstOptions ? <FirstBuildingOptions view={firstOptions} /> : null}
        </div>
      </div>
      <p className="ta-completeness" data-testid="three-answers-completeness">
        {results.completeness_line.text}
      </p>
    </section>
  );
}

/**
 * The identity line (presentation contract §2 item 1): the lot first, then the housing program and
 * the floor height. Every string is read from the document's scope — the lot from `scope.lot`, the
 * program and floor height from the matching assumptions in plain words (never a machine key or
 * code, never a typed value — ruling V2). An absent assumption is simply omitted.
 */
function IdentityLine({ scope }: { scope: Scope }) {
  const facts = IDENTITY_KEYS.flatMap(key => {
    const assumption = scope.assumptions.find(entry => entry.key === key);
    return assumption ? [assumption] : [];
  });
  return (
    <header className="ta-identity" data-testid="three-answers-identity">
      <p className="ta-identity-lot" data-testid="three-answers-identity-lot">
        {scope.lot.display}
      </p>
      {facts.length > 0 ? (
        <div className="ta-identity-facts">
          {facts.map(assumption => (
            <div
              className="ta-identity-fact"
              key={assumption.key}
              data-testid="three-answers-identity-fact"
            >
              <span className="ta-identity-fact-key">{scopeAssumptionKeyLabel(assumption.key)}</span>
              {": "}
              <span
                className="ta-identity-fact-value"
                data-testid="three-answers-identity-fact-value"
              >
                {scopeAssumptionValueText(assumption.value, assumption.unit)}
              </span>
            </div>
          ))}
        </div>
      ) : null}
    </header>
  );
}
