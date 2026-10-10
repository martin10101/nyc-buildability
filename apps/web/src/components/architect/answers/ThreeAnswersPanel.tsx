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
import { collectConditions } from "@/lib/architect/presented-notices";
import {
  firstBuildingOptionsView,
  type FirstBuildingOptionsView,
} from "@/lib/architect/first-building-options";
import {
  AnswerCard,
  BuildingOptionCard,
  BuildingOptionNotes,
  ShortfallBlock,
  SupplementRow,
  type BuildingOptionCardView,
  type ConditionNames,
} from "./AnswerCard";
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
 * The architect-facing results slice (presentation contract step 3; M5-T149 part A, rulings V11/V12).
 * The left column follows the contract's reading order (§2): identity, one short context strip, the
 * three answers, the building options and the comparison, then what needs resolving and the shared
 * conditions stated once (the answers refer to them by name) — so the answers lead the first screen.
 * The right column holds the detailed scope and the assumed conditions, open by default (R119). It
 * renders one `results` document and fetches nothing; Part C wires the live request.
 */
export function ThreeAnswersPanel({ results, showDraftValues = false }: ThreeAnswersPanelProps) {
  const headingId = useId();
  const scope = scopeView(results);
  const remaining = remainingFloorAreaView(results);
  const firstOptions = firstBuildingOptionsView(results, showDraftValues);
  const conditionNames = makeConditionNames(results);
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
      <div className="ta-layout">
        <div className="ta-left" data-testid="three-answers-left">
          {results.scope ? <IdentityLine scope={results.scope} /> : null}
          <ResultsStatusStrip results={results} />
          <div className="ta-answers">
            <AnswerCard
              answerKey="floor_area_allowance"
              view={answerView(results, "floor_area_allowance", showDraftValues)}
              conditionNames={conditionNames}
            >
              {remaining ? <SupplementRow view={remaining} /> : null}
            </AnswerCard>
            <AnswerCard
              answerKey="permitted_envelope"
              view={answerView(results, "permitted_envelope", showDraftValues)}
              conditionNames={conditionNames}
            />
            {firstOptions ? (
              <BuildingOptionCard view={buildingOptionCardView(firstOptions, conditionNames)} />
            ) : (
              <AnswerCard
                answerKey="building_option"
                view={answerView(results, "building_option", showDraftValues)}
                conditionNames={conditionNames}
              >
                <ShortfallBlock view={shortfallView(results)} />
                <BuildingOptionNotes notes={buildingOptionNotesView(results)} />
              </AnswerCard>
            )}
          </div>
          {firstOptions ? <FirstBuildingOptions view={firstOptions} /> : null}
          <SharedConditions results={results} />
        </div>
        <div className="ta-right" data-testid="three-answers-right">
          {scope ? <ScopeSummary view={scope} /> : null}
        </div>
      </div>
      <p className="ta-completeness" data-testid="three-answers-completeness">
        {results.completeness_line.text}
      </p>
    </section>
  );
}

/**
 * A lookup from a result id to the shared conditions it refers to, by name ("Condition 1") — read
 * through the M5-T148 notices adapter, so the numbering matches the shared-conditions block exactly
 * (ruling V11 (5)). An id the document ties to no condition returns an empty list.
 */
function makeConditionNames(results: ThreeAnswersResults): ConditionNames {
  const { shared, references } = collectConditions(results);
  const positionById = new Map(shared.map((condition, index) => [condition.id, index + 1]));
  return (resultId: string) => {
    const ref = references.find(entry => entry.resultId === resultId);
    if (!ref) return [];
    return ref.conditionIds.map(id => `Condition ${positionById.get(id) ?? id.slice(1)}`);
  };
}

/**
 * The building-option card's view (ruling V11 (2)), built from Part B's view model: a worked
 * building gives the scheduled area and the conditions it rests on; no worked building gives "Not
 * known" with the document's reason and what would settle it; a draft architect surface hides the
 * number behind the same not-reviewed line as the other cards.
 */
function buildingOptionCardView(
  firstOptions: FirstBuildingOptionsView,
  conditionNames: ConditionNames,
): BuildingOptionCardView {
  if (firstOptions.draftHidden) {
    return { kind: "not_reviewed", text: firstOptions.draftHiddenText };
  }
  const worked = firstOptions.alternatives[0];
  if (worked) {
    return {
      kind: "scheduled",
      scheduledArea: worked.totalFloorArea,
      conditionNames: conditionNames(`building_alternative.${worked.building}`),
    };
  }
  const notWorked = firstOptions.notWorked[0];
  return {
    kind: "not_known",
    reason: notWorked ? notWorked.reason : "",
    gapTag: notWorked ? notWorked.propertyInfoTag : null,
    resolvedBy: notWorked ? notWorked.resolvedBy : null,
  };
}

/**
 * The identity line (presentation contract §2 item 1): the lot first, then the housing program and
 * the floor height. Every string is read from the document's scope in plain words (never a machine
 * key or code, never a typed value — ruling V2). An absent assumption is simply omitted.
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
