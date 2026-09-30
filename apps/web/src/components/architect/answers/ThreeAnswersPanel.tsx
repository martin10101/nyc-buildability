"use client";

import { useId } from "react";
import type { ThreeAnswersResults } from "@/lib/architect/results-document";
import {
  DRAFT_PREVIEW_TAG,
  answerView,
  remainingFloorAreaView,
  shortfallView,
} from "@/lib/architect/three-answers";
import { AnswerCard, ShortfallBlock, SupplementRow } from "./AnswerCard";
import { ResultsStatusStrip } from "./ResultsStatusStrip";
import "./three-answers.css";

export interface ThreeAnswersPanelProps {
  /** One `results` contract document (packages/contracts/schemas/v1/results.schema.json). */
  results: ThreeAnswersResults;
  /**
   * Show numbers computed from rules that are not reviewed yet (`results.draft`). Only a surface
   * behind a lane flag may set this; absent or false, every available answer of a draft
   * document reads "Not available — the rules for this answer are not reviewed yet"
   * (schema `draft`; D-090-R010). Fail safe: the default hides draft numbers.
   */
  showDraftValues?: boolean;
}

/**
 * The three answers (queue D-05; plan §5 "Three separate answers", §5a "Label on the box").
 *
 * Presentational only: it renders one `results` document and fetches nothing. Lane C wires live
 * data later (M1-12); until then it is not mounted on any route. Order on screen: the one status
 * strip, the floor-area allowance, the permitted envelope, the building option, then the
 * completeness line. Each answer shows its numbers only when available; otherwise exactly
 * "Not available — <reason>" in place of the number (plan §5 "Calculation behavior").
 */
export function ThreeAnswersPanel({ results, showDraftValues = false }: ThreeAnswersPanelProps) {
  const headingId = useId();
  const remaining = remainingFloorAreaView(results);
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
      <ResultsStatusStrip results={results} />
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
        </AnswerCard>
      </div>
      <p className="ta-completeness" data-testid="three-answers-completeness">
        {results.completeness_line.text}
      </p>
    </section>
  );
}
