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
import { ApartmentFigures } from "./ApartmentFigures";
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
  /**
   * The property's street address — the SAME address the report receives (the typed label, else the
   * recorded address, resolved upstream; M5-T153 rework 3). When present it leads the identity as the
   * heading, with the borough/block/lot beneath; absent, the identity keeps today's lot heading.
   */
  address?: string;
}

// The two scope assumptions the identity line names beside the lot (presentation contract §2
// item 1): the housing program and the floor-to-floor height. Read from the document; never typed.
const IDENTITY_KEYS = ["housing_program", "floor_to_floor_ft"] as const;

/**
 * The architect-facing results slice (presentation contract step 3; M5-T149 part A, rulings V11/V12;
 * D-094 R151 / M5-T181). The RESULTS lead the first screen, as on report page 1: a full-width LEAD
 * band carries, in page-1 order, the identity, the one short context strip, the Floor-area allowance
 * and — directly below it — the legal ceiling beside the apartment estimate (the ApartmentFigures
 * block). Below the band sits the existing 44:56 detail grid: its left column keeps the permitted
 * envelope, the building option, the building options/comparison and what needs resolving with the
 * shared conditions stated once (the answers refer to them by name); its right column keeps the
 * detailed scope and the assumed conditions, open by default (R119) — now beneath the results band
 * rather than filling the first screen's right half. The lead and the grid share the Results window's
 * size container, so a narrow screen stacks them in the same reading order. It renders one `results`
 * document and fetches nothing; Part C wires the live request.
 */
export function ThreeAnswersPanel({ results, showDraftValues = false, address }: ThreeAnswersPanelProps) {
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
      {/* The results lead the first screen (D-094 R151; presentation contract principle 1 and the
          page-1 order): a full-width band holding the identity, the one status strip, the Floor-area
          allowance and, directly below it, the legal ceiling beside the apartment estimate — ABOVE the
          detail grid, so the architect sees the result before the assumed conditions. The band shares
          the Results window's size container with the grid below, so a narrow screen stacks it in the
          same reading order. */}
      <div className="ta-lead" data-testid="three-answers-lead">
        {results.scope ? <IdentityLine scope={results.scope} address={address} /> : null}
        <ResultsStatusStrip results={results} />
        <AnswerCard
          answerKey="floor_area_allowance"
          view={answerView(results, "floor_area_allowance", showDraftValues)}
          conditionNames={conditionNames}
        >
          {remaining ? <SupplementRow view={remaining} /> : null}
        </AnswerCard>
        {/* Page-1 parity (M5-T171): the legal ceiling beside the apartment estimate, the same
            additive block report page 1 shows after the results summary — distinct from, and not a
            change to, the allowance card above. M5-T181 moves this JSX into the lead band only; its
            props and test ids are unchanged. */}
        <ApartmentFigures results={results} showDraftValues={showDraftValues} />
      </div>
      <div className="ta-layout">
        <div className="ta-left" data-testid="three-answers-left">
          <div className="ta-answers">
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
 * The identity line (presentation contract §2 item 1; M5-T153 rework 3, E1): the SAME identity the
 * report titles the property with. When an address is known (the typed label or the recorded
 * address, resolved upstream and passed in), the address leads as the heading and the borough/block/
 * lot sits beneath it — so the screen and the report name the property the same way. With no address
 * the lot label stays the heading (today's behaviour). Then the housing program and the floor height.
 * Every string is read from the document's scope (or the resolved address) in plain words, never a
 * machine key or a typed-into-the-form value (ruling V2). An absent assumption is simply omitted.
 */
function IdentityLine({ scope, address }: { scope: Scope; address?: string }) {
  const facts = IDENTITY_KEYS.flatMap(key => {
    const assumption = scope.assumptions.find(entry => entry.key === key);
    return assumption ? [assumption] : [];
  });
  const hasAddress = typeof address === "string" && address.trim() !== "";
  return (
    <header className="ta-identity" data-testid="three-answers-identity">
      {hasAddress ? (
        <>
          <p className="ta-identity-lot" data-testid="three-answers-identity-address">
            {address}
          </p>
          <p className="ta-identity-sublot" data-testid="three-answers-identity-lot">
            {scope.lot.display}
          </p>
        </>
      ) : (
        <p className="ta-identity-lot" data-testid="three-answers-identity-lot">
          {scope.lot.display}
        </p>
      )}
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
